---
layout: post
title: "[kt cloud techup] 레지스트리 vs 이미지 / 컨테이너 / 테라폼 vs 클폼"
date: 2026-01-12 08:49:41 +0900
categories: velog
series: "kt cloud techup"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/de4a0ab5-511f-4f4e-9702-9184ac4cbfcf/image.png"
---

## 1. 이미지란?
- 컨테이너를 실행하기 위한 설계도 (패키지)
- 애플리케이션 코드
- 실행 환경(OS 레이어, 라이브러리)
- 설정값, 실행 명령어(CMD/ENTRYPOINT)
- 이 모든 것이 불변 형태로 묶여 있음
- 직접 실행되지 않음
- 이미지를 기반으로 컨테이너가 생성됨

[예시]
- nginx:1.25
- python:3.11-slim
- myapp:latest

## 2. 레지스트리란?
- 이미지를 저장/배포/관리하는 서버
- 이미지 전용 저장소
- 주요 역할:
	
    - 이미지 업로드 (push)
    - 이미지 다운로드 (pull)
    - 버전 관리
    - 접근 제어
- 대표적인 레지스트리:
	
    - Docker Hub
    - Amazon ECR
    - GitHub Container Registry
    - Private Registry
    
## 3. 구조 흐름
1. 로컬에서 이미지 빌드
```
docker build -t myapp:1.0 .
```

2. 레지스트리에 이미지 저장
```
docker push myrepo/myapp:1.0
```

3. 다른 서버에서 이미지 가져오기
```
docker pull myrepo/myapp:1.o
```

## 4. 컨테이너란?
- 이미지 + 실행 상태(Runtime State)
- 이미지 = 설계도, 컨테이너 = 그 설계도를 실제로 실행 중인 인스턴스
![](/assets/images/hosooinmymind/images/hosooinmymind/post/de4a0ab5-511f-4f4e-9702-9184ac4cbfcf/image.png)
### 컨테이너 내부 구조 

#### 1. 이미지에서 온 파일 시스템 (읽기 전용 레이어)
- OS 기본 파일 (/bin, /lib, /usr 등)
- 애플리케이션 코드 (/app, /srv, /var/www 등)
- 라이브러리, 런타임 (Python, Node, Java, nginx 등)
- 기본 설정 파일

#### 2. 컨테이너 고유의 쓰기 레이어 (Read-write)
- 이 레이어는 컨테이너가 삭제되면 함께 사라짐
- 컨테이너가 실행되면서 새로 생기는 변경사항:
	
    - 로그 파일
    - 임시 파일
    - 애플리케이션이 생성한 데이터
    - 설정 변경 결과
    
#### 3. 실행 중인 프로세스
- 컨테이너 안에서는 프로세스가 돌고 있음
- 예시
	
    - nginx 컨테이너 -> nginx 프로세스
    - python 컨테이너 -> python app.py
    - logstash 컨테이너 -> java -jar logstash.jar
- 컨테이너는 보통 하나의 메인 프로세스(PID 1) 중심
- 그 프로세스가 죽으면 컨테이너도 종료

#### 4. 네트워크 정보 (가상)
- 컨테이너는 자기만의 네트워크 공간을 가짐
- 가상 IP, 포트, 네트워크 인터페이스
- 그래서 컨테이너 A의 localhost와 B의 localhost는 같지 않음
- 포트 노출은 -p 8080:80같은 매핑으로 처리

#### 5. 환경변수 & 런타임 설정
- 실행 시 주입되는 값들: 환경변수, 볼륨 마운트 정보, CPU/메모리 제한, 보안 설정
- 예: docker run -e ENV=prod -m 512m myapp


## 5. 테라폼 vs 클폼
- 테라폼: 여러 클라우드를 하나의 언어로 인프라를 정의하는 도구
- 클폼: AWS 전용 인프라 자동 생성 도구
- 둘 다 IaC이다.

### 테라폼이란?
- HashiCorp에서 만든 멀티 클라우드 인프라 관리 도구
- AWS, GCP, Azure, GitHub, Datadog 등 수백 개의 provider 지원
- HCL (HashiCorp Configuration Language) 사용
- 상태(state) 파일 기반으로 인프라 추적
- 클라우드 벤더에 종속되지 않음
- 예시: AWS EC2 생성
```
resource "aws_instance" "web" {
  ami           = "ami-0abc1234"
  instance_type = "t3.micro"
}
```
![](/assets/images/hosooinmymind/images/hosooinmymind/post/b36cb0e8-2311-4948-b1e6-8a254b9da8ae/image.png)

### 클폼이란?
- AWS에서 제공하는 AWS 전용 인프라 자동화 서비스
- AWS 서비스와 100% 네이티브 연동
- YAML/JSON 기반 템플
- Stack 단위로 리소스 관리
- AWS 콘솔/IAM/권한 관리와 밀접
- 예시
```
Resources:
  MyEC2:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: ami-0abc1234
```
![](/assets/images/hosooinmymind/images/hosooinmymind/post/a15ade7e-609b-4225-9121-34a8da6fbca4/image.png)
