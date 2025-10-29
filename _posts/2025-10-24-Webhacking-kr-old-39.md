---
layout: post
title: "[Webhacking.kr] old-39"
date: 2025-10-24 02:31:19 +0900
categories: velog
---

<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/4b538dee-b594-4f91-854f-0aac21dc72b5/image.png"/></p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/999bee34-6b01-403b-892d-72907ac4dfe9/image.png"/></p>
<p>$_POST['id'] = str_replace("\","",$_POST['id']);
$_POST['id'] = str_replace("'","''",$_POST['id']);
$_POST['id'] = substr($_POST['id'],0,15);
이 부분을 살펴보면, 백슬래시를 없애고 '를 '', 즉 작은 따옴표가 있으면 두 개로 바꿔준 뒤 15글자로 잘라낸다는 것을 알 수 있다.</p>
<p>그리고 주어진 SQL문
select 1 from member where length(id)&lt;14 and id='{$_POST['id']} 
잘 살펴보면 id=' 여기 마지막에 작은 따옴표가 빠져있다.
그럼 '로 시작하는 SQL문을 입력해 SQL Injection을 할 수 있을 것이다.</p>
<p>그리고 성공 조건인 $result[0] == 1이 될려면 DB에 length(id)&lt;14인 레코드가 존재해야 하고, 그 레코드의 id와 입력값이 일치해야 한다.
admin을 입력해 보는 게 국룰인데, 조건을 만족하면서 입력해야 한다. 
문제를 풀기 위해 필요한 사전지식은 mysql에서는 문자열 비교를 할 때 끝에 공백이 추가로 붙어도 같은 문자로 인식한다는 것이다.
그럼 admin_________' (<em>는 공백을 나타냄) 이렇게 입력하면 따옴표가 변환되어 admin________</em>'' 이렇게 입력이 될 것이다.
그럼 전체 SQL문은 
select 1 from member where length(id)&lt;14 and id='admin         '''
MYSQL은 id='admin''', 'admin ' + '' 이라고 해석하게 된다. </p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/8cbe2ffa-3cd6-4c5f-98ea-84bb0524977b/image.png"/>
꽤 어려웠음.</p>
