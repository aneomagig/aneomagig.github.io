---
layout: post
title: "[KT Cloud TechUp] NESSUS, Web Shell, Reverse Telnet, OWASP ZAP"
date: 2025-10-15 02:50:39 +0900
categories: velog
series: "kt cloud techup"
---

<h2 id="nesus">NESUS</h2>
<ul>
<li>시스템/네트워크/웹서버/클라우드 환경까지 보안 취약점을 자동으로 점검하고 리포팅해주는 취약점 스캐너
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/9ee94988-7b9f-4077-aed0-11452236a25f/image.png"/></li>
<li>Terrascan by tenable: 정적 코드 분석기. IAC (Infrastructure as Code)의 보안 정책 준수 여부를 점검하는 도구</li>
<li>자동화된 파이프라인에서 동작 (보안 위반 사항을 탐지하여 안전하지 않은 인프라가 배포되기 전에 문제 해결)</li>
<li>취약점 스캔 전에 최대한 많은 탐색을 하는 것이 중요함</li>
<li>예시: Cookies.txt의 잘못된 예시 (cookies.txt는 netscape 형태로 추출해야 함)<pre><code>let cookies = document.cookie.split(";").map(c =&gt; c.trim());
let content = cookies.join("\n");
console.log(content);</code></pre><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/860a74a8-eabb-4da3-8416-88897a6c5b14/image.png"/>
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/5f627d74-cb22-4202-ad67-bdc03808b9f9/image.png"/>- 취약점을 발견하고 나면 발견된 취약점 CVE 번호를 대상으로 조사해보면 좋음<ul>
<li>exploit-db와 같은 사이트에서 exploit을 다운받아서 공격</li>
<li>metasploit에 payload 등 세팅된 exploit 검색해보고 공격</li>
</ul>
</li>
</ul>
<h2 id="web-shell">Web Shell</h2>
<ul>
<li>웹 페이지에서 해당 웹 서버에서 다양한 명령을 실행시킬 수 있는 스크립트 파일</li>
<li>보통 공격자가 웹 서버의 취약점을 이용해 업로드하고 웹 서버에 제어권을 획득하기 위해 사용됨</li>
<li>일반적인 사용자들과 동일한 웹 서비스 포트를 통해 웹 쉘 업로드 및 공격이 이루어지기 때문에 탐지 및 차단이 까다로움</li>
<li>웹 서버에서 웹 쉘을 실행시켜야 하기 때문에 서버 사이드 스크립트 (asp, jsp, php 등)으로 제작되고 사용되는 경우가 많음.</li>
</ul>
<h2 id="reverse-telnet">Reverse Telnet</h2>
<h3 id="telnet이란">Telnet이란?</h3>
<ul>
<li>인터넷이나 로컬 영역 네트워크 연결에 쓰이는 네트워크 프로토콜</li>
</ul>
<h3 id="reverse-telnet이란">Reverse Telnet이란?</h3>
<ul>
<li>보통 네트워크를 통해 공격을 하기 위해서는 방화벽 등을 통과해야 하는데 inbound 패킷에 대한 정책이 걸려있는 시스템을 뚫기는 쉽지 않다. (대부분 웹에서 사용하는 80번 포트 외에는 대부분 막아둠) 하지만 outbound 패킷에 대해서는 보통 특별한 정책을 설정해주지 않는다는 점을 이용한다.</li>
<li>즉 방화벽 내에 존재하는 대상자에서 방화벽 외부의 공격자 컴퓨터로 텔넷을 이용해 접속하는 기술이다.</li>
<li>netcat(nc)를 이용하는데, netcat이란 tcp/udp를 사용해 네트워크 연결을 읽고 쓰는 데 사용되는 컴퓨터 네트워킹 유틸리티이다. -l은 listen mode, -p는 열어놓을 포트 지정이다.</li>
</ul>
<h3 id="간단-실습">간단 실습</h3>
<ul>
<li>victim, attacker: kali linux 환경으로 진행</li>
<li>공격자 ip: 172.30.1.77</li>
<li>victim ip: 172.30.1.88</li>
</ul>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/458b453d-bac3-4897-b32e-0995ac702db3/image.png"/>attacker pc에서 nc -lvnp 8888으로 8888번 포트를 열었다.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/6ff6c1da-1ae5-4ae3-aaf8-25ac5bf439a7/image.png"/>victim pc에서 nc -vz 172.~~ 8888으로 원격 접속.
그 후 attacker pc에서 ifconfig를 하면 victim pc의 ip가 뜬다. (위 사진 참고)</p>
<h2 id="owasp-zap">OWASP ZAP</h2>
<ul>
<li>OWASP: 국제 웹 보안 프로젝트</li>
<li>ZAP(Zed Attack Proxy)<ul>
<li>웹 애플리케이션의 보안 취약점을 자동으로 검사해주는 오픈소스 도구</li>
<li>보안 검사를 수동으로 하면 잊어버리거나, 배포 이후 따로 해야 하므로 일관성을 유지하기 어려움</li>
<li>Github Actions를 활용하면 코드를 배포할 때마다 자동으로 취약점 점검을 수행하고, 리포트를 생성해 확인할 수 있어 실무에서 매우 유용함</li>
<li>다운로드 링크: <a href="https://www.zaproxy.org/download/">https://www.zaproxy.org/download/</a> (java.exe 파일 필요)
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/1b21e3e2-0617-4ed8-8660-0941c31fe0d2/image.png"/>
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/02df57ab-1fc2-4a34-9af0-d6b75a5c2150/image.png"/>
웹해킹 워게임 사티으를 스캔해보았다.</li>
</ul>
</li>
</ul>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/2de309d4-22e4-45ab-ab88-c576bc6add8e/image.png"/>
dvwa 환경에서는 이런 식의 실습도 가능함</p>
<hr/>
<ul>
<li><p>Reference
<a href="https://docs.tenable.com/nessus/Content/WebAuthentication.htm">https://docs.tenable.com/nessus/Content/WebAuthentication.htm</a>
<a href="https://maker5587.tistory.com/42">https://maker5587.tistory.com/42</a>
<a href="https://sdosj.tistory.com/entry/%EB%A6%AC%EB%B2%84%EC%8A%A4-%ED%85%94%EB%84%B7Reverse-telnet">https://sdosj.tistory.com/entry/%EB%A6%AC%EB%B2%84%EC%8A%A4-%ED%85%94%EB%84%B7Reverse-telnet</a></p>
</li>
<li><p>앞으로 할 일
DVWA 환경 구성 완료하기</p>
</li>
</ul>