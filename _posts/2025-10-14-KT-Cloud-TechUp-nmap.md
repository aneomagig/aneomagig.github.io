---
layout: post
title: "[KT Cloud TechUp] nmap"
date: 2025-10-14 05:00:55 +0900
categories: velog
---

<h2 id="nmap이란">nmap이란?</h2>
<ul>
<li>네트워크 보안 진단/관리를 위해 사용되는 도구</li>
<li>네트워크에 연결된 호스트/서비스 탐색 + 보안 취약점 사전 점검</li>
<li>live host의 list 제공</li>
<li>열려있는 포트 탐색</li>
<li>OS scanning</li>
</ul>
<h3 id="실습">실습</h3>
<p>kali에서 nmap -sn 192.168.26.129/24 실행
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/7c18eb80-baae-4733-993b-007af6178e2b/image.png"/></p>
<ul>
<li>서브넷 192.168.26.129/24 네트워크를 대상으로 Host discovery 수행 -&gt; 어떤 IP들이 살아있는지 (응답하는 장치가 있는지) 확인함. (포트 스캔은 하지 않음)</li>
<li>로컬 (같은 L2 세그먼트): nmap은 기본적으로 ARP 요청 (ARP probe)를 사용해서 누가 연결되어 있는지 확인함. ARP는 같은 서브넷에서 가장 빠르고 확실한 방법임. (ex: Who has 192.168.26.45? -&gt; 응답하면 MAC 주소와 함께 호스트가 보임)</li>
<li>원격 네트워크 (라우터 건너거나 L3만 접근 가능): ARP를 못 쓰므로 ICMP Echo (ping), TCP SYN같은 다른 기법을 시도함</li>
<li>일반 단말뿐 아니라 네트워크 인프라 장비도 뜸 </li>
<li>x.x.x.1: 많은 네트워크에서 .1은 기본 게이트웨이(라우터/공유기)의 IP로 설정됨. 스캔 결과에 .1이 살아있다면 보통 라우터/공유기일 가능성이 높음</li>
<li>x.x.x.2: .2는 경우에 따라 추가 인프라 장비로 자주 사용됨 (관리용 스위치 IP, 모뎀, 프록시 등)</li>
<li>x.x.x.254: 게이트웨이나 핵심 장비 IP로 자주 쓰임</li>
</ul>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/6e370e30-e1e3-4727-bee9-3a41573f92e2/image.png"/>
게이트웨이의 ip 주소 확인
default: 기본 경로 - 즉 내 컴퓨터가 목적지를 모를 때 (다른 네트워크로 나갈 때) 통신을 보낼 기본 통로
via 192.168.<strong>.</strong>: Gateway IP, 패킷이 외부로 나갈때 이 주소로 먼저 전송됨
dev eth0: 사용하는 네트워크 인터페이스 이름 (eth0: 유선 LAN, wlan0: 무선 LAN)
proto dhcp: DHCP를 통해 ip를 자동으로 받았다는 뜻 (수동 설정 아님)
src 192.168.<strong>.</strong>: 내 컴퓨터(칼리리눅스)의 IP 주소
metric 100: 라우팅 우선순위</p>
<p>nmap –sS 192.168.26.129 –O 명령어 실행
-sS: TCP SYN scan ("half-open", stealth 스캔); TCP SYN 패킷만 보내 응답(SYN/ACK, RST 등)으로 포트 상태를 판별함. 완전한 3-way handshake를 완료하지 않음. 비교적 빠르고 일부 단순한 로깅에서는 덜 눈에 띌 수 있음
-O: OS detection, 네트워크 장비나 방화벽, 패킷 필터링, 응답 방해 때문에 부정확
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/7f918bbd-e33b-4ff7-92d1-9e79a88b5155/image.png"/>
실행 결과 포트 21번 (FTP)가 열려 있고 서비스가 동작하고 있음. </p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/846ccf62-fced-4af2-8b2d-7b0c27b128b4/image.png"/>
Apache를 켰다. 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/f94ebbf1-4a5d-4ba2-89bb-5e7f41c6129b/image.png"/>
다시 명령어를 실행해 보니 http 포트가 잘 스캔되는 모습.</p>
<h3 id="reference">REFERENCE</h3>
<ul>
<li>L2 (Data Link layer): 같은 네트워크 안에서 MAC 주소 기반으로 통신 (스위치, 브릿지, LAN)</li>
<li>L3 (Network Layer): 서로 다른 네트워크 간에 IP 주소 기반으로 통신 (라우터, 게이트웨이)
<a href="https://m.blog.naver.com/dme1004/222785567330">https://m.blog.naver.com/dme1004/222785567330</a></li>
</ul>
