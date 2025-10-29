---
layout: post
title: "[KT Cloud TechUp] xampp mysql 실습 (작성중)"
date: 2025-10-16 08:14:23 +0900
categories: velog
---

<p>xampp를 다운로드하고 설정하면 이런 컨트롤 패널이 뜬다. </p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/5d153280-0d53-4870-86b2-57b6cc3d47d3/image.png"/>
여기서 mysql을 start하고 오른쪽의 shell을 눌러 쉘으로 진입한다.</p>
<p>mysql -u root -p를 통해 mysql에 접속한다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/e1f056c0-c2bf-4c16-8f06-5be64507b347/image.png"/></p>
<p>데이터베이스를 생성하고 선택한다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/34b4fd18-73bb-4ce8-a6a6-254f3b304960/image.png"/></p>
<p>student 테이블을 생성했다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/a277e5d0-d978-4dae-a170-1dc8bd2da65d/image.png"/></p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/c6b3e6e2-4c0b-4d32-b418-b0091a3c9d80/image.png"/>
dept = '컴퓨터'인 튜플을 조회하려고 했는데 한글이 깨져 진행되지 않는다.
이는 HEIDISQL을 사용해 해결할 수 있다. (추후 실습 예정)</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/4c0547a3-2a62-4502-bb49-4a1b58aef04d/image.png"/>
player 테이블을 만들고 값을 넣어 보았다. 또 본능적으로 한글로 입력해서 UPDATE를 사용해 영어로 수정했다.</p>
