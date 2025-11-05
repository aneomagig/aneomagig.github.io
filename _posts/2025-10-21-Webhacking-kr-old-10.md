---
layout: post
title: "[Webhacking.kr] old-10"
date: 2025-10-21 02:41:09 +0900
categories: velog
series: "wargame"
---

<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/b06e62da-8543-44ff-ac4e-8e6b60d7a159/image.png"/>O를 goal에 넣으면 될 것 같은 느낌이 드는 문제이다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/d9d1e861-27aa-4e9d-88f7-763e566f512a/image.png"/>O에 mouseover/mouseout 속성이 있어 마우스를 올려봤더니 커서를 올려놓으면 O가 yOu로 바뀌는 것을 볼 수 있었다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/31fcaf22-ab00-4618-80a8-8174e3f709f7/image.png"/> 그리고 클릭할 때마다 오른쪽으로 조금씩 이동한다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/719069fa-5ed8-44b1-8489-8d8e01037a72/image.png"/>
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/07a91f96-7b29-4a06-9034-068a6fa19996/image.png"/> ? 아무일도 일어나지 않음........ </p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/358090d7-30a8-4173-8b7c-a1104a4c52c7/image.png"/>근데 이 부분을 자세히 읽어보니까 
if (this.style.left=='1600px') this.href='?go='+this.style.left 부분이 눈에 띈다. 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/368edf7f-c5b7-48f5-bd8c-4c99a41f3a38/image.png"/>?go=1600을 넣자 no hack이 뜬다.</p>
<p>O가 1600에 갔을 때 무슨 일이 일어나야 하는 건 맞는데, 콘솔에서 위치를 1600으로 박았을 때는 아무 일도 일어나지 않았어서 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/3cc80311-ede3-4c58-be11-2e748a743e41/image.png"/>
이렇게 스타일 코드를 바꾼 다음 한번 클릭해 줬더니
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/5c158596-9080-40bb-8802-74d5c0860b05/image.png"/>
풀렸다 !</p>