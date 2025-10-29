---
layout: post
title: "[KT Cloud TechUp] heartbleed 실습"
date: 2025-10-15 07:21:08 +0900
categories: velog
---

<h2 id="heartbleed">Heartbleed</h2>
<ul>
<li>2014년 4월에 발생한 OpenSSL 버그 CVE-2014-0160</li>
<li>OpenSSL 1.0.1 버전에서 발견된 매우 위험한 취약점. TLS/DTLS의 HeartBeat 확장규격에서 발견된 취약점으로, OpenSSL은 어디서든 다 사용하기 때문에 매우 위험때문에 매우 위험</li>
</ul>
<h3 id="ssl이란">SSL이란?</h3>
<ul>
<li>Secure Socket Layer의 약자로, 웹사이트와 브라우저 간의 데이터를 암호화해 인터넷 연결을 보호하는 보안 기술임. 현재는 TLS(Transport Layer Security)로 대체되어 사용 중</li>
<li>SSL/TLS 인증서가 있는 웹사이트는 HTTPS로 표시된다.</li>
<li>그렇다면 OpenSSL은 암호화와 보안 프로토콜을 구현하는 오픈소스 라이브러리로 SSL/TLS 프로토콜을 지원해 안전한 데이터 통신을 제공한다.</li>
</ul>
<h3 id="heartbeat란">HeartBeat란?</h3>
<ul>
<li>클라이언트와 서버 간의 연결 상태를 체크하기 위한 OpenSSL 확장 모듈</li>
<li>TLS/DTLS 프로토콜에서 매번 연결을 재협상하지 않아도 통신연결을 유지하게 해줌</li>
<li>클라이언트가 하트비트를 요청하며 payload와 해당 payload의 길이를 보내면 서버 측에서는 하트비트 응답에 내용을 그대로 복사해서 돌려주며 연결을 확인함</li>
<li>여기에서 클라이언트 요청메시지를 처리할 때 데이터 길이 검증을 수행하지 않아 시스템 메모리에 저장된 64kb 크기의 데이터를 외부에서 아무런 제한 없이 탈취할 수 있는 취약점이 heartbleed
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/991ed22a-0fe3-4295-9f24-c5ed8f7d14a1/image.png"/>
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/01a0bf09-606b-4d7a-bf9f-9a2de44153cf/image.png"/></li>
<li>위 그림은 payload 길이가 조작된 하트비트 메시지 교환이다. </li>
</ul>
<h2 id="실습">실습</h2>
<ul>
<li>실습 환경<ul>
<li>공격자 PC (Kali Linux): 취약점 스캐닝 및 익스플로잇 수행</li>
<li>피해자 PC (Kali Linux): 취약한 웹 서버 구성</li>
<li>네트워크: 가상 환경</li>
</ul>
</li>
</ul>
<h3 id="1-취약한-서버-구성-피해자-pc">1. 취약한 서버 구성 (피해자 PC)</h3>
<ul>
<li>IP: 172.30.1.88
(1) Docker으로 취약한 Ubuntu 14.04 환경 구성
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/462f1023-a822-475d-9ed7-8443bd7decbc/image.png"/> Docker 서비스 시작
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/fe1b721b-3957-4aa9-9747-ef798fa3e903/image.png"/> Ubuntu 14.04 컨테이너 실행 (취약한 OpenSSL 1.0.1 포함)</li>
</ul>
<p>(2) 컨테이너 내부에서 취약한 웹 서버 설정</p>
<pre><code># 패키지 저장소 업데이트
apt-get update

# 필요한 패키지 설치
apt-get install -y openssl apache2 ssl-cert

# Apache SSL 모듈 활성화
a2enmod ssl

# 기본 SSL 사이트 활성화  
a2ensite default-ssl

# Apache 웹서버 시작
service apache2 start</code></pre><p>(3) 서버 상태 확인
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/93102e08-d4e3-46d8-8010-26ec0b55f08d/image.png"/>
잘 설정된 것 확인 완료</p>
<p>(4) 컨테이너를 백그라운드로 실행 (ctrl+p, ctrl+q)</p>
<h3 id="2-취약점-스캐닝-공격자-pc">2. 취약점 스캐닝 (공격자 PC)</h3>
<p>을 할려고 했는데 칼리 하드디스크 용량 부족으로 뻑나서... 수습할려다가 그냥 삭제했다가 다시 깔았다. 와중에 한글 설정이 또 꼬여서 거의 한시간을 날림;</p>
<p>(1) 타겟 정보 수집
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/9eb345be-863f-473c-9023-464b3cf15266/image.png"/></p>
<p>(2) Heartbleed 취약점 스캔
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/5c31496b-7c69-474a-aa88-80b9c124fab2/image.png"/>
스캔이 안 됨... 찾아보니 Ubuntu 14.04에서 OpenSSl 1.0.1f는 취약한 버전이 맞지만 heartbeat 확장 기능이 컴파일 시에 비활성화 되어 있을 수도 있어서 직접 취약한 openSSL을 컴파일해서 사용하는 게 가장 직빵이라고 한다. 
하지만 오늘은 컨디션 난조 + 할 일 쌓여있음으로 일단 pass..... 언젠가 다시 도전해볼것....</p>
<p><a href="https://sudo-minz.tistory.com/8">https://sudo-minz.tistory.com/8</a></p>
