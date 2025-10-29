---
layout: post
title: "[Webhacking.kr] old-12 Javascript challenge"
date: 2025-10-28 03:23:07 +0900
categories: velog
---

<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ce23b44b-78cf-49e9-bca8-9f4e2044e5de/image.png"/>
script 생긴 걸 보아하니 원래 코드를 이모트콘으로 대체한 것 같은데... javascript 암호화로 서치해보니까 <a href="https://cat-in-136.github.io/2010/12/aadecode-decode-encoded-as-aaencode.html">https://cat-in-136.github.io/2010/12/aadecode-decode-encoded-as-aaencode.html</a> 요런 사이트를 찾을 수 있었다. 바로 복호화 ㄱㄱ.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ae152424-6a5b-4167-9245-72a6fb159fbd/image.png"/>
코드를 좀 잘 살펴보자면... </p>
<pre><code>var enco='';
var enco2=126;
var enco3=33;</code></pre><p>126은 ascii로 ~이고, 33은 ascii로 !이다.</p>
<pre><code>var ck=document.URL.substr(document.URL.indexOf('='));
for(i=1;i&lt;122;i++){
  enco=enco+String.fromCharCode(i,0);
}</code></pre><p>ck: URL에서 = 이후의 부분을 추출
enco: ascii코드 1에서 121까지 문자 + \x00들을 연결한 문자열 생성
즉 \x01\x00\x02\x00 이런식으로 생성될 것임</p>
<pre><code>function enco_(x){
  return enco.charCodeAt(x);
}</code></pre><p>enco 문자열의 x번째 위치 문자의 ascii 코드를 반환</p>
<pre><code>if(ck=="="+String.fromCharCode(enco_(240))+String.fromCharCode(enco_(220))+String.fromCharCode(enco_(232))+String.fromCharCode(enco_(192))+String.fromCharCode(enco_(226))+String.fromCharCode(enco_(200))+String.fromCharCode(enco_(204))+String.fromCharCode(enco_(222-2))+String.fromCharCode(enco_(198))+"~~~~~~"+String.fromCharCode(enco2)+String.fromCharCode(enco3)){
  location.href="./"+ck.replace("=","")+".php";
}</code></pre><p>이걸 콘솔에서 실행해 보자.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/0da30c31-f4bc-4f61-b21d-7b8fb9b8b8a6/image.png"/>
이렇게 함수 정의를 그대로 갖고와서 해주고
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/704b4751-76e6-4e9d-af7e-ea256932a729/image.png"/>
요렇게 하면 무슨 문자열인지 확인 가능.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/7e80b204-bfe5-46be-8a2a-565f899b8274/image.png"/>
야호</p>
