---
layout: post
title: "[2SeC] AWS OpenSearch 대시보드 접속 트러블슈팅"
date: 2025-12-17 03:06:27 +0900
categories: velog
series: "2SeC"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/00bf0720-5e01-4a23-9951-f2205e78440d/image.png"
---

## 개요
aws-es-proxy는 왜 내 자격증명을 못 찾았을까?
오늘 오픈서치 대시보드에 접속하려다가 모르는 개념을 마주하게 되어서 이렇게 블로그를 작성한다.
export AWS_SDK_LOAD_CONFIG=1 이라는 명령어가 핵심이었는데, 이 안에 AWS 인증 구조의 핵심 개념이 다 들어 있기 때문에 정리하고자 한다.

## 1. 내가 하려고 했던 것
목표는 "로컬 맥북에서 AWS OpenSearch Dashboards에 접속하기"였다.
구성은 다음과 같음:
- OpenSearch는 AWS Managed OpenSearch Service
- 도메인 접근 정책은 IAM Role 기반
- 로컬에서는 aws-es-proxy를 사용해 요청을 SigV4 서명해서 OpenSearch로 전달

즉 구조는:
```
브라우저
 -> localhost:9200 (aws-es-proxy)
 -> SigV4 서명
 -> 오픈서치 도메인
```

## 2. 먼저 확인한 것: AWS CLI
![](/assets/images/hosooinmymind/images/hosooinmymind/post/00bf0720-5e01-4a23-9951-f2205e78440d/image.png)
- AWS 계정 확인됨
- IAM User (admin-02) 정상
![](/assets/images/hosooinmymind/images/hosooinmymind/post/acc6a3b6-e00f-43cf-9dee-503705a03d04/image.png)
- 2SeC-dev-opensearch-admin-role로 정상 assume
- 즉 로컬 AWS 인증 자체는 문제 없음

## 3. 문제 발생
![](/assets/images/hosooinmymind/images/hosooinmymind/post/28c7595c-3b0b-4bf5-9253-9b00e28d1cd7/image.png)이 메시지를 보고 처음에 들었던 생각은 "AWS_PROFILE도 잘 설정됐고, CLI도 잘 되는데 왜 자격증명이 없다고 하지?" 였다.
여기서 핵심은 CLI와 aws-es-proxy가 AWS 인증을 읽는 방식이 다르다는 점이었다.

## 4. AWS 자격증명
AWS는 자격증명을 한 파일에 다 넣지 않는다.

~/.aws/credentials
```
[default]
aws_access_key_id=...
aws_secret_access_key=...
```
- 실제 키 값만 저장한다.
- "누구인지"만 정의함.
- 오래된 도구, 단순 SDK는 이 파일만 읽음.


~/.aws/config
```
[profile opensearch-admin]
role_arn = ...
source_profile = ...
region = ap-northeast-2
```
- assume role
- region
- SSO 설정
- 출력 포맷 등

-> role_arn 정보는 config에만 있음!!

## 5. AWS CLI는 됐는데 aws-es-proxy는 안 된 이유?
AWS CLI v2는 기본적으로 두 파일을 다 읽도록 만들어져 있다. 
하지만 aws-es-proxy의 기본 동작은 아래와 같다.
- Go 언어 AWS SDK를 사용함
- SDK의 기본 정책은 훨씬 보수적임:
	
    - 환경 변수 (AWS_ACCESS_KEY_ID 등)
    - ~/.aws/credentials
    - EC2 메타데이터
- 즉 aws-es-proxy 입장에서는
	
    - opensearch-admin 프로파일을 찾으려 했는데
    - credentials 파일에는 그런 프로파일이 없고
    - config 파일은 안 읽으니까
    - 자격증명 없음 이라고 판단
    -> NoCredentialProviders 에러 발생
    
    
## 6. 해결의 핵심
AWS_SDK_LOAD_CONFIG = 1
이 환경변수는 AWS SDK에게 보내는 명령이다. SDK에게 credentials 파일만 보지 말고 config도 같이 읽으라는 명령. 이 한 줄로 SDK의 흐름이 바뀐다.
- ~/.aws/config에서 opensearch-admin 확인
- role_arn 발견
- source_profile = default 확인
- STS AssumeRole 실행
- 임시 자격증명 발급
- 요청에 SigV4 서명
- OpenSearch로 전달


