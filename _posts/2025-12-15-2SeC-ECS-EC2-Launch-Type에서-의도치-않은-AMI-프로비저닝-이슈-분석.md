---
layout: post
title: "[2SeC] ECS EC2 Launch Type에서 의도치 않은 AMI 프로비저닝 이슈 분석"
date: 2025-12-15 01:20:12 +0900
categories: velog
series: "2SeC"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/86f2343e-dede-4db9-b79d-bde6c596f858/image.png"
---

## 1. 사건 개요
CloudTrail 이벤트를 확인한 결과, admin-02 사용자에 의해 RunInstances 이벤트가 반복적으로 발생했고, 그 과정에서 아래 AMI가 지속적으로 EC2 인스턴스로 생성되었다.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/86f2343e-dede-4db9-b79d-bde6c596f858/image.png)![](/assets/images/hosooinmymind/images/hosooinmymind/post/47dae07a-e2c8-4ccf-aff7-63c9367c8fbe/image.png)
- AMI ID: ami-0d136904eaba14b45
- AMI 이름:
al2023-ami-ecs-neuron-hvm-2023.0.20251209-kernel-6.1-x86_64
- 특징: ECS Agent가 포함된 ECS Optimized Amazon Linux 2023 AMI
이 EC2 인스턴스들은 정상적으로 애플리케이션을 수행하지 못하고, ECS 관점에서는 "정상적인 컨테이너 인스턴스가 아닌 상태"로 판단되어 ECS가 다시 인스턴스를 띄우려는 시도를 무한 반복하게 되었다. 

## 2. 핵심 원인
Terraform 설정의 핵심 포인트
```
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
```
most_recent=true, owners=["amazon"], al2023-ami-*-x86_64 패턴을 모두 만족하는 "가장 최근에 릴리즈된 이미지"가 선택됨. 그 결과 일반 AL2023이 아니라 ECS Agent가 내장된 ECS Optimized AL2023 AMI가 선택됨. 

위 코드를 보면 겉보기에는 "최신 Amazon Linux 2023 AMI"를 가져오는 것처럼 보이지만 실제로는 ECS Optimized AMI까지 포함하는 매우 넓은 조건이다.

즉 결론적으로 ECS용 AMI를 의도하지 않았지만 테라폼은 가장 최신 ECS AMI를 골라버린 것.

## 3. 문제 발생
### ECS EC2 Launch Type의 기본 동작
ECS에서 EC2 Launch Type을 사용하면:
- ECS Cluster는 컨테이너 인스턴스(EC2)를 필요로 함
- 컨테이너 인스턴스는 ECS Agent 실행, ECS Cluster에 정상 등록, 올바른 IAM Role 필요

이번 상황에서는
- EC2는 ECS Agent를 이미 포함한 AMI로 생성됨
- 동시에 ECS Cluster / Capacity Provider / Auto Scailing 쪽에서 컨테이너 인스턴스가 부족하다고 판단함

=> ECS가 계속해서 인스턴스 생성 시도 -> 실패 -> 다시 생성을 시도함

## 4. IAM의 동작
문제의 ECS에는 2sec-dev-ec2-role이 붙어 있었다. 이 role의 권하는 CloudWatch, SSM이고 ECS 관련 권한이 없어서 ECS Cluster에 정상 등록이 불가했다.
그래서 ECS로 쓰기엔 권한이 부족해서 결국 차단되었고, ECS는 계속 인스턴스가 부족하다고 판단했다.

## 5. 구조적인 문제
- 문제 요약: EC2용 AMI를 동적으로 조회하면서, ECS Launch Type / 역할 분리를 고려하지 않은 상태에서 Most_recent 조건을 사용한 것이 근본 원인
- 잘못된 설계 포인트
	
    - AMI 선택 기준이 너무 광범위함
    - ECS/일반 EC2 용도를 구분하지 않음
    - EC2 Launch Type과 Fargate가 혼재된 구조에서 AMI 책임 경계가 불분명
    - ECS Capacity Provider가 "자동 복구" 로직을 수행하면서 증상이 증폭됨
    
---
### 참고
- AMI: EC2 인스턴스를 찍어내는 '설치 완료된 컴퓨터 이미지'
- AMI의 종류: 일반 Amazon Linux AMI, ECS Optimized AMI, GPU AMI, 커스텀 AMI


- ECS: 컨테이너(Docker)를 실행/관리해주는 AWS 서비스. 컨테이너들을 어디서 띄울지, 몇 개 띄울지, 죽으면 다시 살릴지를 자동으로 관리함
- ECS가 일하는 두 가지 방식
	
    - Fargate 방식: 서버 신경 안 써도 됨. EC2를 직접 안 만듦 + AMI 필요 없음 -> ECS가 알아서 서버 관리
    - EC2 Launch Type: ECS가 EC2 서버를 직접 써서 그 위에 컨테이너를 올림. ECS 전용 EC2 서버가 필요함.

    