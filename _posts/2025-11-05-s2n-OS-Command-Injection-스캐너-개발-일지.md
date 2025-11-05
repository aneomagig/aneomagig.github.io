---
layout: post
title: "[s2n] OS Command Injection 스캐너 개발 일지"
date: 2025-11-05 05:25:41 +0900
categories: velog
series: "s2n"
---

<p>s2n 스캐너에 들어갈 OS Command Injection 스캐너 기능을 개발했습니다. 이 플러그인은 base URL에서 시작해 내부 링크를 재귀 크롤링하고 (HTML 파싱 기반), 발견한 페이지의 파라미터를 자동 추출해 OS Command Injection 취약점을 검사합니다. 인증이 필요하면 DVWAAdapter으로 로그인(선택적)하여 같은 세션을 재사용하도록 설계했습니다.</p>
<h3 id="1-배경--목표">1. 배경 &amp; 목표</h3>
<ul>
<li>비전문가도 사용할 수 있게 base URL만 넣으면 자동으로 내부 링크를 찾아서 스캔하도록</li>
<li>DVWA같은 연습용 웹앱은 인증이 필요한 경우가 많으므로 인증 흐름을 모듈화해서 세션 재사용</li>
</ul>
<h3 id="2-아키텍처-요약">2. 아키텍처 요약</h3>
<p>프로젝트 구조(요약):</p>
<ul>
<li>core/s2nscanner/http/client.py</li>
<li>HttpClient : requests.Session 래퍼. 재시도/타임아웃 일괄 처리.</li>
<li>core/s2nscanner/auth/dvwa_adapter.py</li>
<li>DVWAAdapter : DVWA 전용 로그인/세션관리/cookie save&amp;load. 인증 전용 모듈.</li>
<li>core/s2nscanner/plugins/oscommand.py</li>
<li>자동 크롤링 → 파라미터 추출 → 페이로드 주입으로 OS Command Injection 탐지.</li>
<li>DVWAAdapter는 선택적으로 사용 (import 후 인증 흐름 호출 가능).</li>
</ul>
<p>설계 원칙: 책임 분리. oscommand는 스캐너(크롤러+테스트)에만 집중하고, 인증/세션 관리는 DVWAAdapter가 담당.</p>
<h3 id="3-구현-핵심">3. 구현 핵심</h3>
<ul>
<li><p>크롤러</p>
<ul>
<li>base URL에서 BFS/DFS 형식으로 내부 링크 수집 (depth 기본값 = 2)</li>
<li>수집 대상 <code>&lt;a href&gt;, &lt;form action&gt;, &lt;script src&gt;, &lt;iframe src&gt;, &lt;link href&gt; 등</code></li>
<li>내부 링크만 추적</li>
</ul>
</li>
<li><p>파라미터 추출</p>
<ul>
<li>url 쿼리 파라미터 추출</li>
<li>```HTML <input name="..."/>, <select>, <textarea name="...">`` 등에서 이름 수집&lt;/li&gt;
&lt;li&gt;파라미터가 전혀 없으면 COMMON PARAMS로 대체&lt;/li&gt;
&lt;/ul&gt;
&lt;/li&gt;
&lt;li&gt;&lt;p&gt;테스트 루틴&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;미리 정의한 페이로드 목록을 파라미터 값에 주입&lt;/li&gt;
&lt;li&gt;GET 기본 (POST 확장 가능)&lt;/li&gt;
&lt;li&gt;응답 본문에서 정규표현식으로 uid=, root:..., vulnerable 등 탐지&lt;/li&gt;
&lt;li&gt;매칭 시 바로 취약판정 후 요약에 추가&lt;/li&gt;
&lt;/ul&gt;
&lt;/li&gt;
&lt;/ul&gt;
&lt;h3 id="4-dvwa-adapter-연동-방식"&gt;4. DVWA Adapter 연동 방식&lt;/h3&gt;
&lt;ul&gt;
&lt;li&gt;DVWA Adapter는 Httpclient를 사용해 내부에서 생성/외부에서 전달 가능하게 만듦&lt;/li&gt;
&lt;li&gt;adapter = DVWAAdapter(base_url="&lt;a href="http://localhost/dvwa""&gt;http://localhost/dvwa"&lt;/a&gt;)&lt;/li&gt;
&lt;li&gt;adapter.authenticate([(user, pass)]) -&gt; 인증 성공 시 adapter.get_clinet()로 세션 획득&lt;/li&gt;
&lt;li&gt;oscommand 내부에서도 선택적으로 adapter.authenticate를 호출하도록 구현함 (대화형에서 인증 여부 물어봄)&lt;/li&gt;
&lt;li&gt;두 모듈을 독립적으로 구성함!&lt;/li&gt;
&lt;/ul&gt;
&lt;p&gt;&lt;img alt="" src="https://velog.velcdn.com/images/hosooinmymind/post/d776c857-0531-4c6f-b480-fe83e5f56920/image.png" /&gt;&lt;/p&gt;
&lt;p&gt;&lt;img alt="" src="https://velog.velcdn.com/images/hosooinmymind/post/ec806538-e8f0-4614-994a-394bb0519054/image.png" /&gt;결과에 색깔도 넣어봤다. ㅋㅋ&lt;/p&gt;</textarea></select></li></ul></li></ul>