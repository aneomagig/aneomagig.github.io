---
layout: post
title: "[기타] Splunk SIEM"
date: 2025-10-14 00:30:36 +0900
categories: velog
---

<p>SIEM을 구성하는 대표적인 방법은 AWS이다. 하지만 클라우드 내부 서비스가 아닌 외부 SIEM으로 Splunk, Datadog도 존재한다. </p>
<p>Splunk는 machine data를 수집/저장/검색/시각화해서 운영 상태를 분석하고 보안 위협을 감지할 수 있는 로그 분석 플랫폼이다.
Forwarder -&gt; Indexer -&gt; Search Head의 3계층 구조로 이루어져 있다. 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/cced6544-5ac7-4eea-9964-eb81f31dc068/image.png"/>
14일동안 무료로 사용할 수 있다. 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/d980460e-a920-4327-ad4e-753ce0a965ac/image.png"/>
설치하면 이런 메인 화면.</p>
<p>Audit Trail Dashboard
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/8660469b-b900-4075-a95d-66444d87b5c4/image.png"/></p>
<p>모바일 어플리케이션도 존재한다. 전반적으로 ux가 굉장히 잘 되어있는 느낌.</p>
<p>*참고: 인덱스 수명 관리
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/1424473d-3223-4cb8-958d-2d2fccf9fd66/image.png"/></p>
