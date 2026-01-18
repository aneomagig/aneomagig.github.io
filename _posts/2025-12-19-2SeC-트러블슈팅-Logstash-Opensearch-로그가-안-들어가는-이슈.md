---
layout: post
title: "[2SeC] 트러블슈팅: Logstash -> Opensearch 로그가 안 들어가는 이슈..."
date: 2025-12-19 03:23:56 +0900
categories: velog
series: "2SeC"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/558e42ca-3177-4c24-bbac-25f1cba3f23b/image.png"
---

<h2 id="ecs-환경과-로컬-docker-테스트의-결정적인-차이">ECS 환경과 로컬 Docker 테스트의 결정적인 차이</h2>
<h2 id="0-문제-상황-요약">0. 문제 상황 요약</h2>
<p>2SeC-SIEM 프로젝트에서<br/><strong>Kinesis → Logstash(ECS Fargate) → OpenSearch</strong> 파이프라인을 구축하던 중,<br/>Logstash 컨테이너는 정상적으로 실행되는데 <strong>OpenSearch에 로그가 전혀 적재되지 않는 문제</strong>가 발생했다.</p>
<p>겉으로 보기에는 단순 연결 문제처럼 보였지만, 실제로는 다음 요소들이 복합적으로 얽혀 있었다.</p>
<ul>
<li>Logstash 베이스 이미지 선택 문제</li>
<li>OpenSearch output 플러그인 미설치</li>
<li>패턴 파일 권한 문제</li>
<li>환경 변수 미주입</li>
<li>IAM 인증 방식에 대한 오해</li>
<li>ECS 환경과 로컬 Docker 환경의 근본적인 차이</li>
</ul>
<p>이 글에서는 <strong>하루 동안 이 문제를 어떻게 좁혀갔고, 최종적으로 무엇을 확인했는지</strong>를 정리한다.</p>
<hr/>
<h2 id="1-최초-증상-logstash는-도는데-opensearch에-로그가-없다">1. 최초 증상: “Logstash는 도는데 OpenSearch에 로그가 없다”</h2>
<p>ECS에서 Logstash 태스크는 다음 상태였다.</p>
<ul>
<li>컨테이너 상태: RUNNING</li>
<li>Logstash 기동 로그: 정상</li>
<li>pipeline 로딩 로그: 정상</li>
</ul>
<p>하지만 OpenSearch Dashboard에서는</p>
<ul>
<li>인덱스가 생성되지 않음</li>
<li><code>_cat/indices</code> 결과 없음</li>
</ul>
<p>즉, <strong>Logstash → OpenSearch output 단계에서 문제가 발생</strong>하고 있었다.</p>
<hr/>
<h2 id="2-첫-번째-원인-logstash-기본-이미지에는-opensearch-output이-없다">2. 첫 번째 원인: Logstash 기본 이미지에는 OpenSearch output이 없다</h2>
<p>처음 사용하던 이미지는 다음이었다.</p>
<pre><code class="language-bash">docker.elastic.co/logstash/logstash:8.11.0</code></pre>
<p>이 이미지는 ElasticSearch 기준 이미지이며,
opensearch {} output 플러그인이 기본 포함되어 있지 않다.</p>
<p>로컬 테스트 시 바로 다음 에러가 발생했다.</p>
<pre><code>Couldn't find any output plugin named 'opensearch'</code></pre><h3 id="해결-방법">해결 방법</h3>
<p>OpenSearch 공식 Logstash 이미지를 사용하도록 변경했다.<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/558e42ca-3177-4c24-bbac-25f1cba3f23b/image.png"/>이 이미지에는 다음이 포함되어 있다.
    •    logstash-output-opensearch
    •    OpenSearch OSS 호환 설정</p>
<p>👉 이 단계에서 output 플러그인 미설치 문제는 해결</p>
<hr/>
<h2 id="3-두-번째-원인-패턴-파일은-있는데-permission-denied">3. 두 번째 원인: 패턴 파일은 있는데 Permission denied</h2>
<p>이미지를 빌드한 뒤 컨테이너 내부를 확인했을 때, 이상한 상태를 발견했다.</p>
<pre><code>ls -l /usr/share/logstash/patterns

-????????? attack_patterns.yml
-????????? patterns_matcher.rb
-????????? severity_mapping.yml</code></pre><p>파일은 존재하지만 권한을 읽을 수 없는 상태였다. 원인은 명확했다.</p>
<ul>
<li>COPY는 되었지만</li>
<li>logstash 유저가 읽을 수 없는 권한</li>
</ul>
<h3 id="해결-방법-1">해결 방법</h3>
<p>Dockerfile에서 명시적으로 권한과 소유자를 지정했다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/61354a35-e121-4ea5-88c5-92821c9ba396/image.png"/>확인 결과</p>
<pre><code>-rw-r--r-- 1 logstash logstash attack_patterns.yml
-rw-r--r-- 1 logstash logstash patterns_matcher.rb
-rw-r--r-- 1 logstash logstash severity_mapping.yml</code></pre><hr/>
<h2 id="4-세-번째-원인-로컬에서-opensearch-output이-계속-죽는-이유">4. 세 번째 원인: 로컬에서 opensearch output이 계속 죽는 이유</h2>
<p>stdin → stdout 구조로 단순화해도 다음 에러가 반복 발생했다.</p>
<pre><code>undefined method `credentials' for nil:NilClass</code></pre><p>이 에러는 logstash-output-opensearch 내부에서
AWS SigV4 인증용 credentials 객체가 없을 때 발생한다.</p>
<p>즉, Logstash는 다음을 기대하고 있었다.</p>
<ul>
<li>ECS Task Role</li>
<li>또는 EC2 Instance Profile</li>
<li>또는 IRSA / Metadata 기반 IAM 자격증명
하지만 로컬 Docker 컨테이너에는 그 어떤 IAM 컨텍스트도 존재하지 않았다.</li>
</ul>
<hr/>
<h2 id="5-결정적인-차이-ecs에서는-되지만-로컬에서는-안-되는-이유">5. 결정적인 차이: ECS에서는 되지만 로컬에서는 안 되는 이유</h2>
<p>ECS 환경에서는</p>
<ul>
<li>Task Role이 자동 주입됨</li>
<li>AWS SDK가 metadata endpoint에서 credentials 획득</li>
<li>auth_type =&gt; aws_iam 정상 동작</li>
</ul>
<p>로컬 Docker 환경에서는</p>
<ul>
<li>IAM Role 없음</li>
<li>Metadata endpoint 없음</li>
<li>AWS SDK가 credentials를 얻지 못함</li>
<li>결과적으로 nil.credentials 에러 발생</li>
</ul>
<p>👉 즉, 로컬에서 실패한 것은 설정 오류가 아니라, 실행 환경의 한계였다.</p>
<hr/>
<h2 id="6-terraformtfvars에서의-실수도-있었지만-본질은-아니었다">6. terraform.tfvars에서의 실수도 있었지만, 본질은 아니었다</h2>
<p>중간에 terraform.tfvars에 다음과 같은 값이 남아 있었던 것도 발견했다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ad6831db-83dd-4655-9eab-e943b6bed0e1/image.png"/>이는 분명 ECS 배포 시 문제가 될 수 있는 설정이지만,
로컬 테스트에서 발생한 IAM 에러의 직접 원인은 아니었다.</p>
<hr/>
<h2 id="7-그래서-지금-상태는">7. 그래서 지금 상태는?</h2>
<p>정리하면 현재 상태는 다음과 같다.</p>
<ul>
<li><p>Logstash 이미지</p>
<ul>
<li><p>OpenSearch output 포함</p>
</li>
<li><p>Kinesis input 포함</p>
</li>
<li><p>패턴 파일 정상 로딩</p>
</li>
</ul>
</li>
<li><p>Logstash pipeline</p>
<ul>
<li><p>문법 오류 없음</p>
</li>
<li><p>필터 단계 정상</p>
</li>
</ul>
</li>
<li><p>ECS 환경 기준</p>
<ul>
<li><p>IAM Role 기반 OpenSearch 접근 가능</p>
</li>
<li><p>구조적으로 로그 유입 가능</p>
</li>
</ul>
</li>
</ul>
<p>즉, 로컬 Docker에서는 IAM 인증 때문에 실패하지만, ECS 환경에서는 정상 동작할 가능성이 매우 높다.</p>
<hr/>
<h2 id="8-오늘의-교훈">8. 오늘의 교훈</h2>
<ol>
<li>Logstash 로컬 테스트는 IAM 기반 output을 완전히 검증할 수 없다</li>
<li>ECS + Task Role 환경을 기준으로 판단해야 한다</li>
<li>OpenSearch를 쓸 경우 Elastic 공식 이미지가 아닌 OpenSearch OSS 이미지를 써야 한다</li>
<li>Dockerfile에서 파일 권한은 항상 의심하자</li>
<li>에러 메시지보다 실행 환경 차이를 먼저 보자</li>
</ol>
<hr/>
<h3 id="9-다음-액션">9. 다음 액션</h3>
<ul>
<li>PR 병합</li>
<li>ECS에서 이미지 재배포</li>
<li>OpenSearch Dashboard에서 인덱스 생성 여부 확인</li>
<li>필요 시 CloudWatch Logs로 Logstash output 확인</li>
</ul>
<p>오늘은 “왜 안 되는지”를 이해한 날이고,
이해한 만큼 다음 단계는 훨씬 빠를 것이다.</p>