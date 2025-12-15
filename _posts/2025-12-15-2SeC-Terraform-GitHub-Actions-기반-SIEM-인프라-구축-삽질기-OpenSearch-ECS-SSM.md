---
layout: post
title: "[2SeC] Terraform + GitHub Actions 기반 SIEM 인프라 구축 삽질기 (OpenSearch, ECS, SSM)"
date: 2025-12-15 06:25:38 +0900
categories: velog
series: "2SeC"
---

Terraform으로 SIEM 실습 인프라를 구축하면서 실제로 겪은 문제들과 해결 과정을 정리해보고자 한다.
은근 삽질을 많이 해서 왜 막혔고, 어떻게 풀었는지를 위주로 작성해볼려고 한다.

#### 1. 목표: "로깅 가능한 SIEM 베이스라인" 만들기
- Terraform으로 IaC 기반 인프라 구성
- DVWA 취약 웹 서버 배포
- CloudWatch Logs -> Kinesis -> Logstash(ECS) -> OpenSearch 파이프라인
- OpenSearch Dashboards 접속까지 확인

아래 두 가지 태스크만 내가 담당했다.

#### 2. Terraform 구조 설계
- network: VPC / Public & Private Subnet / NAT Gateway
- ec2: DVWA 웹 서버 (SSM 기반 접속)
- cloudwatch: EC2 로그 수집
- Kinesis: 로그 스트림
- ECS: fargate 기반 logstash
- opensearch: VPC 전용 OpenSearch + Advanced Security

infra/dev를 루트 모듈로 두고, 모든 리소스는 modules/* 에서 조합하는 방식이다.

#### 3. 첫 번째 난관: terraform apply 에러 퍼레이드
(1) 처음에 프로젝트 루트에서 terraform apply를 했더니 Error: No configuration files가 떴다. Terraform은 .tf 파일이 있는 디렉토리에서만 실행된다는 것을 알게 되었다.

(2) AWS 인증 에러
로컬에 AWS CLI 인증이 안 되어 있어서 이 문제도 금방 해결

(3) tfvars 파일 없음
이게 없어서 테라폼이 계속 똑같은 값들을 물어봤다. tfvars를 만들고 gitignore에 넣기까지 완료.

#### 4. OpenSearch에서 막혔던 지점
(1) master user password 규칙
자꾸 apply 하다가 막혀서 뜯어보니 패스워드에 특수문자 하나가 없어서였다... 하...

(2) Dashboards 접속 안 됨 -> 네트워크 문제
OpenSearch endpoint를 보니 vpc-xxxx.ap-northeast-2.es.amazonaws.com...이었다. vpc-가 붙어 있다면 외부 인터넷 접근 불가가 정상이다. 즉 브라우저에서 바로 접속은 안 되고, VPC 내부에서만 접속 가능.

#### 5. SSM + 포트포워딩
(1) AWS-StartPortForwardingSession
했는데 이 문서는 EC2 자기 자신 (localhost) 으로만 포워딩한다.
하지만 OpenSearch는 EC2 외부의 VPC 리소스다.
정답은 이 문서: AWS-StartPortForwardingSessionToRemoteHost 였다. 
```
aws ssm start-session \
  --target i-xxxxxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{
    "host":["vpc-xxxx.es.amazonaws.com"],
    "portNumber":["443"],
    "localPortNumber":["9201"]
  }'
```
실행하고 브라우저에서 Https://localhost:9201/_dashboards 접속 및 로그인 완료.

#### 6. OpenSearch Access Policy에서 또 한 번 막힘
EC2에서 curl 테스트: curl -u admin:password https://vpc-xxxx.es.amazonaws.com 했는데 User:anonymous is not authroized가 뜸.
IAM Principal 기반 Access Policy가 적용되고 있는데 요청은 Basic Auth로 가고 있었다. IAM 서명이 아니어서 전부 anonymous가 된 것.
일단 실습/개발용으로 정책을 완화해뒀다.
