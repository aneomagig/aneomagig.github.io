---
layout: post
title: "[2SeC] 트러블슈팅: Logstash -> Opensearch 로그가 안 들어가는 이슈..."
date: 2025-12-19 03:23:56 +0900
categories: velog
series: "2SeC"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/558e42ca-3177-4c24-bbac-25f1cba3f23b/image.png"
---


## ECS 환경과 로컬 Docker 테스트의 결정적인 차이

## 0. 문제 상황 요약

2SeC-SIEM 프로젝트에서  
**Kinesis → Logstash(ECS Fargate) → OpenSearch** 파이프라인을 구축하던 중,  
Logstash 컨테이너는 정상적으로 실행되는데 **OpenSearch에 로그가 전혀 적재되지 않는 문제**가 발생했다.

겉으로 보기에는 단순 연결 문제처럼 보였지만, 실제로는 다음 요소들이 복합적으로 얽혀 있었다.

- Logstash 베이스 이미지 선택 문제
- OpenSearch output 플러그인 미설치
- 패턴 파일 권한 문제
- 환경 변수 미주입
- IAM 인증 방식에 대한 오해
- ECS 환경과 로컬 Docker 환경의 근본적인 차이

이 글에서는 **하루 동안 이 문제를 어떻게 좁혀갔고, 최종적으로 무엇을 확인했는지**를 정리한다.

---

## 1. 최초 증상: “Logstash는 도는데 OpenSearch에 로그가 없다”

ECS에서 Logstash 태스크는 다음 상태였다.

- 컨테이너 상태: RUNNING
- Logstash 기동 로그: 정상
- pipeline 로딩 로그: 정상

하지만 OpenSearch Dashboard에서는

- 인덱스가 생성되지 않음
- `_cat/indices` 결과 없음

즉, **Logstash → OpenSearch output 단계에서 문제가 발생**하고 있었다.

---

## 2. 첫 번째 원인: Logstash 기본 이미지에는 OpenSearch output이 없다

처음 사용하던 이미지는 다음이었다.

```bash
docker.elastic.co/logstash/logstash:8.11.0
```
이 이미지는 ElasticSearch 기준 이미지이며,
opensearch {} output 플러그인이 기본 포함되어 있지 않다.

로컬 테스트 시 바로 다음 에러가 발생했다.
```
Couldn't find any output plugin named 'opensearch'
```
### 해결 방법
OpenSearch 공식 Logstash 이미지를 사용하도록 변경했다.![](/assets/images/hosooinmymind/images/hosooinmymind/post/558e42ca-3177-4c24-bbac-25f1cba3f23b/image.png)이 이미지에는 다음이 포함되어 있다.
	•	logstash-output-opensearch
	•	OpenSearch OSS 호환 설정

👉 이 단계에서 output 플러그인 미설치 문제는 해결

---
## 3. 두 번째 원인: 패턴 파일은 있는데 Permission denied

이미지를 빌드한 뒤 컨테이너 내부를 확인했을 때, 이상한 상태를 발견했다.
```
ls -l /usr/share/logstash/patterns

-????????? attack_patterns.yml
-????????? patterns_matcher.rb
-????????? severity_mapping.yml
```
파일은 존재하지만 권한을 읽을 수 없는 상태였다. 원인은 명확했다.
- COPY는 되었지만
- logstash 유저가 읽을 수 없는 권한

### 해결 방법

Dockerfile에서 명시적으로 권한과 소유자를 지정했다.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/61354a35-e121-4ea5-88c5-92821c9ba396/image.png)확인 결과
```
-rw-r--r-- 1 logstash logstash attack_patterns.yml
-rw-r--r-- 1 logstash logstash patterns_matcher.rb
-rw-r--r-- 1 logstash logstash severity_mapping.yml
```

---
## 4. 세 번째 원인: 로컬에서 opensearch output이 계속 죽는 이유

stdin → stdout 구조로 단순화해도 다음 에러가 반복 발생했다.
```
undefined method `credentials' for nil:NilClass
```
이 에러는 logstash-output-opensearch 내부에서
AWS SigV4 인증용 credentials 객체가 없을 때 발생한다.

즉, Logstash는 다음을 기대하고 있었다.
- ECS Task Role
- 또는 EC2 Instance Profile
- 또는 IRSA / Metadata 기반 IAM 자격증명
하지만 로컬 Docker 컨테이너에는 그 어떤 IAM 컨텍스트도 존재하지 않았다.

---

## 5. 결정적인 차이: ECS에서는 되지만 로컬에서는 안 되는 이유

ECS 환경에서는
- Task Role이 자동 주입됨
- AWS SDK가 metadata endpoint에서 credentials 획득
- auth_type => aws_iam 정상 동작

로컬 Docker 환경에서는
- IAM Role 없음
- Metadata endpoint 없음
- AWS SDK가 credentials를 얻지 못함
- 결과적으로 nil.credentials 에러 발생

👉 즉, 로컬에서 실패한 것은 설정 오류가 아니라, 실행 환경의 한계였다.

---

## 6. terraform.tfvars에서의 실수도 있었지만, 본질은 아니었다

중간에 terraform.tfvars에 다음과 같은 값이 남아 있었던 것도 발견했다.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/ad6831db-83dd-4655-9eab-e943b6bed0e1/image.png)이는 분명 ECS 배포 시 문제가 될 수 있는 설정이지만,
로컬 테스트에서 발생한 IAM 에러의 직접 원인은 아니었다.

---

## 7. 그래서 지금 상태는?

정리하면 현재 상태는 다음과 같다.
- Logstash 이미지
	
    - OpenSearch output 포함
	
    - Kinesis input 포함
	
    - 패턴 파일 정상 로딩
    
- Logstash pipeline
	
    - 문법 오류 없음
	
    - 필터 단계 정상

- ECS 환경 기준
	
    - IAM Role 기반 OpenSearch 접근 가능
	
    - 구조적으로 로그 유입 가능

즉, 로컬 Docker에서는 IAM 인증 때문에 실패하지만, ECS 환경에서는 정상 동작할 가능성이 매우 높다.

--- 

## 8. 오늘의 교훈

1.	Logstash 로컬 테스트는 IAM 기반 output을 완전히 검증할 수 없다
2.	ECS + Task Role 환경을 기준으로 판단해야 한다
3.	OpenSearch를 쓸 경우 Elastic 공식 이미지가 아닌 OpenSearch OSS 이미지를 써야 한다
4.	Dockerfile에서 파일 권한은 항상 의심하자
5.	에러 메시지보다 실행 환경 차이를 먼저 보자

---

### 9. 다음 액션
	
- PR 병합
- ECS에서 이미지 재배포
- OpenSearch Dashboard에서 인덱스 생성 여부 확인
- 필요 시 CloudWatch Logs로 Logstash output 확인

오늘은 “왜 안 되는지”를 이해한 날이고,
이해한 만큼 다음 단계는 훨씬 빠를 것이다.