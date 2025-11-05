---
layout: post
title: "[KT Cloud TechUp] Metasploit 실습 ⭐⭐"
date: 2025-10-14 07:40:50 +0900
categories: velog
series: "kt cloud techup"
---

<blockquote>
<p>이 글은 Kali Linux 환경에서 Metasploit과 nmap을 이용해 네트워크 탐지 → 서비스 확인 → MySQL 관련 열거 및 브루트포스 과정을 실습하는 과정을 기록합니다. 학습 목적의 가상환경에서만 실행했으며, 각 단계별 명령·출력·해석을 통해 원리와 방어 관점을 함께 살펴봅니다.</p>
</blockquote>
<ul>
<li>보안 테스팅 / 취약점 분석 &amp; 진단 툴</li>
<li>Exploit: 시스템, 웹, 애플리케이션, 서버 등의 취약점을 악용하는 공격 (BOF, ROP, SQL Injection)</li>
<li>Payload: 피해자의 시스템에서 실행하고 싶은 코드/명령어 (악성코드)
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/d9764081-6f75-4318-be56-c68416d5bbb8/image.png"/></li>
</ul>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/016d5799-856c-4ee0-a5cf-8925314297f6/image.png"/>
msfconsole 명령어로 메타스플로잇 실행</p>
<p>search portscan 명령어
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ddf69282-6c98-4534-80e4-88b1606571d1/image.png"/>
nmap과 유사한 기능이다. metasploit은 스캔을 할 때마다 탐색 이력을 자체 db에 저장해주어서 관리가 용이하다.
정확히는 msfconsole에서 portscan이라는 키워드가 포함된 모듈을 검색하는 명령어이다. 보통 port scanning 기능을 제공하는 auxiliary/scanner/portscan/... 계열 모듈들이 검색됨.</p>
<p>use 5, info 5 명령어
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/249003b4-5547-4909-90ae-1bca40279f65/image.png"/>
metasploit은 여러 개의 모듈로 구성되어 있음 (exploit, payload, auxiliary, post, encoder, nop 등)
그 중 auxiliary/scanner/portscan/tcp 모듈의 info를 출력해줌.</p>
<blockquote>
<p>목적: 내부 네트워크에서 원격 DB가 외부 바인딩(0.0.0.0)으로 열려 있을 때 발생할 수 있는 정보 유출·무차별대입 공격 위험을 재현해 보고, 운영자 관점의 탐지·대응 방안을 제시한다.</p>
</blockquote>
<h2 id="실습">실습</h2>
<p>Kali Linux 환경에서 Metasploit을 사용해 네트워크 탐지부터 서비스 확인, MySQL 관련 보조 모듈을 활용한 정보 수집까지 진행한다. </p>
<ol>
<li>Victim: DB 서비스 상태 확인 및 원격 허용 준비</li>
<li>Attacker: 네트워크 감지(nmap) -&gt; 포트,서비스 확인</li>
<li>Attacker: Metasploit으로 포트 스캔 -&gt; MySQL으로 brute force 시도</li>
<li>Victim: 로그 확인</li>
</ol>
<h3 id="실습-전-세팅">실습 전 세팅</h3>
<p>맥에 적응도 할 겸 윈도우와 맥에 각각 칼리 리눅스를 설치해 실습을 진행함. 맥에 설정을 마치고 한글까지 설치하는 데 시간이 꽤 걸렸다. 한글 설정까지 끝내고 네트워크 설정으로 넘어감. 
네트워크 설정을 Bridge로 바꿔서 두 pc의 vm이 같은 서브넷 대역폭에 들어오도록 한 뒤, ping을 쏴서 간단히 테스트를 진행했다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/9e8bb847-ae73-4b58-8077-f5de8f9b8640/image.png"/>잘 도착!</p>
<ol>
<li><p>Victim: DB 서비스 상태 확인 및 원격 허용 준비<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/cd83fdfd-a0b8-45ea-97a3-21e845b4e672/image.png"/>mariaDB를 재시작해 db를 켜고, sudo ss -ltnp | grep 3306 결과에서 0.0.0.0:3306를 확인해 MariaDB가 모든 인터페이스에서 3306 포트를 열고 외부 접속을 받도록 바인딩함. 즉 이제 Attacker에서 DB에 접속할 수 있다.
원격 접속용 테스트 계정 tester를 만들었고, SHOW DATABASES 같은 기본 권한을 줬음. 비밀번호는 TestPass123!</p>
</li>
<li><p>Attacker: 네트워크 감지(nmap) -&gt; 포트,서비스 확인
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/4acc93da-6eed-4a8c-b8ad-35216f655645/image.png"/><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/aeb7c0f8-5835-4bae-91b1-0427312fc7a7/image.png"/>원격 접속 성공.</p>
</li>
<li><p>Attacker: Metasploit으로 포트 스캔 -&gt; MySQL으로 brute force 시도
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/6f7c0f13-4816-4924-9f6d-b77fe30aa330/image.png"/>브루트포스가 실행된다. (겁나 신기;)</p>
</li>
</ol>
<p>코드를 뜯어보면
use auxiliary/admin/mysql/mysql_enum
// 브루트포스용 보조 모듈을 선택함. auxiliary 모듈: 스캔/열거/브루트포스같은 기능을 수행하는 모듈 그룹
set RHOSTS 172.30.<em>.*</em>
set USERNAME tester
set PASSWORD TestPass123!   # 또는 creds에서 본 비밀번호
set PASS_FILE /tmp/~~
// 브루트포스에 사용할 비밀번호 목록 파일을 지정. 이 파일의 각 줄을 모듈이 하나씩 시도함.
run</p>
<ol start="4">
<li>Victim: 로그 확인
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/16f53384-58d4-4378-884b-cf58bdce6214/image.png"/>
로그에 브루트포스 흔적이 찍힌걸 확인할 수 있다. tester 계정으로 비밀번호를 써서 접속을 시도했으나 차단됨.</li>
</ol>
<p>탐지/대응</p>
<ol>
<li>외부 바인딩(bind-address)이 필요없는 서비스는 127.0.0.1로 바인딩할 것.</li>
<li>원격 접속이 필요한 경우 IP 기반 허용 목록(whitelist) 또는 VPN을 통해서만 연결하게 구성.</li>
<li>fail2ban 또는 iptables 정책으로 짧은 시간 내 반복 로그인 시도를 자동 차단.</li>
<li>DB 접속 로그를 중앙 로그시스템(ELK, Graylog 등)으로 모으고 의심 패턴(짧은 시간에 동일 계정 로그인 실패) 경보 설정.</li>
</ol>