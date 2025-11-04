---
layout: post
title: "[s2n] DVWA Adapter & Selenium 자동 로그인 CLI 구축기"
date: 2025-11-04 07:10:57 +0900
categories: velog
---

<blockquote>
<p>플러그인 기반 웹 취약점 스캐너(PyPI 배포 목표) 프로젝트 s2n의
인증/세션 관리 구조를 통합하기 위한 DVWAAdapter 개발기</p>
</blockquote>
<h3 id="🎯-배경">🎯 배경</h3>
<p>우리 팀(503+1)은 “웹 취약점 스캐너 파이썬 라이브러리”를 개발 중이다.
각 플러그인은 특정 취약점(XSS, SQLi, OS Command 등)을 담당하고,
공통된 HttpClient를 통해 요청을 보냄.</p>
<p>그런데 문제는…</p>
<ul>
<li>각 플러그인이 DVWA 로그인 로직을 따로 구현 중이었고</li>
<li>환경마다 DVWA URL, 포트, 계정이 다 달라서</li>
<li>로그인 유지나 세션 공유가 엉망으로 꼬일 위험이 높아 보였음</li>
<li>추후 DVWA 환경이 아닌 일반 웹 스캐너로도 확장하고자 하기 때문에 모듈을 분리하는 것이 합리적이라고 생각됨</li>
</ul>
<p>그래서 이번에 인증 로직을 공용 어댑터로 분리하고,
Selenium으로 자동 로그인 세션을 브라우저까지 띄워주는 구조로 통합.</p>
<h3 id="🧱-구조-설계">🧱 구조 설계</h3>
<pre><code>s2n/
├── core/
│   ├── s2nscanner/
│   │   ├── http/
│   │   │   └── client.py               # 공용 HTTP 세션 (requests.Session 래퍼)
│   │   ├── auth/
│   │   │   └── dvwa_adapter.py         # DVWA 로그인 어댑터
│   │   └── utils/
│   │       └── url.py                  # URL 정규화 유틸
│   └── ...
└── cli_test_dvwa_selenium.py           # Selenium 자동 로그인 CLI</code></pre><h3 id="핵심-구성-요소">핵심 구성 요소</h3>
<ol>
<li>HttpClient (공용 세션 관리자): 모든 플러그인은 HttpClient를 통해 요청을 보냄. 세션 유지, 쿠키 공유, 재시도 로직이 통일됨.</li>
<li>DVWA Adapter (로그인 + 세션 유지): CSRF 토큰 자동 추출, 성공 시 HttpClient 세션에 쿠키 저장, Logout 문구 감지로 성공 판별</li>
<li>URL 유틸리티: 각자 다른 DVWA 포트/경로에서도 일관된 URL 사용 가능.</li>
<li>Selenium CLI (자동 로그인 브라우저 실행): 로그인 후 크롬 자동 실행, HttpClient 세션 쿠키를 브라우저에 주입, 로그인된 세션 그대로 유지</li>
</ol>
<h3 id="실행-방법">실행 방법</h3>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/7d98bb4c-cee8-4903-95c5-b099f67afd55/image.png"/></p>
<p>더 자세한 사항은 &gt;&gt; <a href="https://github.com/504s2n/s2n/pull/8">https://github.com/504s2n/s2n/pull/8</a> &lt;&lt;</p>
