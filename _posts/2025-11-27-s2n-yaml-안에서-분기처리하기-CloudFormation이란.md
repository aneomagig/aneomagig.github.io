---
layout: post
title: "[s2n] yaml 안에서 분기처리하기 +CloudFormation이란?"
date: 2025-11-27 03:54:24 +0900
categories: velog
series: "s2n"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/30b1730a-1b1c-4250-8f07-36bcf6670e78/image.png"
---

1. dev.yml 파일은 "백엔드 Docker 이미지 빌드 후 GHCR에 push"까지만 처리하고 있음.
2. 분기처리 (yaml 안에서), 변경된 파일이 특정 디렉토리일 때만 빌드/배포를 할 것.

------
## CloudFormation
- AWS에서 제공하는 IaC 기반의 서비스
- VPC, EC2, Lambda 등과 같은 리소스를 수동 생성할 필요 없이 템플릿(코드)로 구성하고 Stack을 생성해 인프라를 구성할 수 있음.
- 장점: 인프라 관리 간소화, 신속하게 인프라 복제, 인프라 변경 사항을 쉽게 제어 및 추적
- 구성:
	
    - 템플릿: AWS 리소스를 프로비저닝하고 구성하기 위해 필요한 파일로, JSON or YAML 형식을 사용함.
    - 스택: 하나의 단위로 관리할 수 있는 AWS 리소스 모음. 스택을 통해 템플릿을 읽고, 실제 리소스를 생성하고 인프라를 관리함. 스택의 모든 리소스는 템플릿을 통해 정의함. 스택을 삭제하면 스택이 관리하는 모든 리소스가 삭제된다.
    
- 작동 방식
(1) 스택 생성
![](/assets/images/hosooinmymind/images/hosooinmymind/post/30b1730a-1b1c-4250-8f07-36bcf6670e78/image.png)
- 구성하고자 하는 인프라에 대한 리소스를 json/yaml 형식의 템플릿으로 작성 
- 작성한 템플릿을 S3 혹은 로컬에 저장
- 템플릿 파일의 위치를 지정해 스택을 생성하고 리소스를 구성함

(2) 스택 업데이트
![](/assets/images/hosooinmymind/images/hosooinmymind/post/963b9f0c-2326-42bb-8903-151353282fed/image.png)
- 템플릿을 수정
- 수정한 템플릿을 S3 혹은 로컬에 저장
- CloudFormation은 수정된 템플릿 혹은 파라미터를 기반으로 Change Set을 생성함
- 변경 세트를 통해 변경 사항을 확인 후 변경 세트를 실행
- 실행된 변경 세트는 스택을 업데이트함

---------

## 전체 흐름 구조
(1) 변경 감지
- backend/** 변경 -> 백엔드 Docker 이미지 빌드 + Stack Update
- cloudformation/** 변경 -> Stack update만
- lambda/** 변경 -> lambda 전용 Stack update 

(2) Docker build & push (백엔드 변경 시만)

(3) CloudFomation UpdateStack 실행
- AWS CLI 사용
- credentials: GitHub Secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)