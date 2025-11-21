---
layout: post
title: "[s2n] EC2 + Docker + GitHub Actions로 Flask 배포하기"
date: 2025-11-21 06:00:48 +0900
categories: velog
series: "s2n"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/c146f213-d7ed-4259-818d-154ee4364152/image.png"
---

## 1단계: 기초 세팅
### 1. Flask 웹앱 실행 구조 점검
![](/assets/images/hosooinmymind/images/hosooinmymind/post/c146f213-d7ed-4259-818d-154ee4364152/image.png)
현재 파일 구조는 위와 같다.
일단 백엔드 Flask만 실행되면 되기 때문에 Flask 서버를 backend/app.py에서 실행한다. 현재는 테스트가 가능한 상황이 아니기 때문에 패스.

### 2. Dockerfile (dev) 작성하기
Dockerfile 작성하는 방법까지 겸사겸사 공부.
Dockerfile은 일반적으로 아래와 같은 순서/핵심 명령어로 구성된다.

**FROM** (기반 이미지 설정: 빌드할 이미지의 시작점이 되는 기본 이미지 지정) - 필수
**WORKDIR** (작업 디렉토리 설정: 컨테이너 내부에서 이후 명령어들이 실행될 기본 작업 디렉토리 설정)
**COPY** (또는 ADD)(파일 복사: 호스트 시스템의 파일/디렉토리를 컨테이너 내부로 복사)
**RUN** (명령 실행: 이미지 빌드 과정에서 필요한 명령어-패키지 설치, 컴파일 등-를 실행)
**EXPOSE** (포트 노출: 컨테이너가 리스닝할 네트워크 포트를 선언. 실제 포트 매핑은 아님)
**ENV** (환경 변수 설정: 컨테이너 내에서 사용할 환경 변수 설정)
**CMD** (또는 ENTRYPOINT) (실행 명령어: 컨테이너가 시작될 때 가장 먼저 실행될 명령어 지정 - 하나만 사용 가능)

```
# 1. python:3.11-slim 이미지를 기반으로 builder라는 첫 번째 빌드 스테이지 시작
FROM python:3.11-slim AS builder

# 2. 컨테이너 내부의 작업 디렉토리를 /src로 설정 - 이후의 모든 명령은 이 디렉토리 내에서 실행됨
WORKDIR /src

# 3. 빌드 도구 설치 (eventlet, mysql connector 컴파일 필요): 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libssl-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. 종속성 파일만 먼저 복사 (캐싱 최적화)
COPY requirements.txt .

# 5. pip install (requirements 변경 없으면 캐시 재사용)
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# 6. 소스 전체 복사 (requirements 변경 없을 때 빌드 빠름)
COPY backend /src/backend

# ------------------------------
# Runtime Stage - 최종적으로 컨테이너를 실행할 환경 생성
# ------------------------------
# 7. 새로운 최종 스테이지 시작 (이전 스테이지에서 설치했던 컴파일 도구들은 포함되지 않음)
FROM python:3.11-slim

# 8. 최종 실행 환경의 작업 디렉토리를 /app으로 설정
WORKDIR /app

# 9. 이전 builder 스테이지에서 컴파일 및 설치된 모든 파이썬 패키지가 위치한 디렉토리를 현재 스테이지로 복사
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

# 10. builder 스테이지의 /src에 복사되어 있던 애플리케이션 소스 코드를 현재 /app 디렉토리로 복사
COPY --from=builder /src /app

# 11. 컨테이너가 5000번 포트로 통신할 것임을 선언
EXPOSE 5000

# 12. 컨테이너가 시작될 때 실제 애플리케이션을 실행하는 명령어
CMD ["python", "backend/app.py"]

```

### 3. docker build 로컬 빌드 테스트
![](/assets/images/hosooinmymind/images/hosooinmymind/post/69bf7013-7691-4c35-9057-4a1f0cad2171/image.png)
DB가 켜져 있지 않은 상태라서 일단 도커파일 자체가 정상적으로 빌드되는지만 확인했다.

### 4. GitHub Actions (dev.yml) 연동
yml 파일을 쓸 차례.
참고로 yaml은 데이터 직렬화 형식 중 하나로, 사람이 읽기 쉽도록 설계된 파일 포맷으로, 주로 config 파일/데이터 교환/도커 컴포즈/쿠버네티스 같은 자동화 도구에서 많이 사용된다. 들여쓰기가 핵심이다.

----

yaml은 데이터를 크게 세 가지 기본 형식으로 표현한다.
(1) Scalars: 단일 값
```
key: value
name: John Doe
age: 30
```

(2) Mapping: 키-값 쌍
```
user:
  name: Alice
  role: Developer
  settings:
    theme: dark
    font_size: 12
```
이처럼 상위 레벨의 user 아래에 name, role이 종속된다.

(3) Sequence: 목록
```
fruits:
  - Apple
  - Banana
  - Cherry
```

dev.yml은 다음과 같이 작성했다.
```
name: Dev CI/CD - Build & Push Docker Image

# 트리거 조건: 코드가 dev 브랜치가 push되었을 때만 이 워크플로우가 실행됨
on:
  push:
    branches: ["dev"]

permissions:
  contents: read
  # *중요* ghcr.io에 빌드된 이미지를 푸시하기 위해 필수적인 권한
  packages: write

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
        # 1) Checkout Code - 저장소의 최신 코드를 워크플로우가 실행되는 환경으로 가져옴
        - name: Checkout Code
          uses: actions/checkout@v4

        # 2) Set up Docker Buildx - 도커의 빌드 도구인 buildx 설정
        - name: Set up Docker Buildx
          uses: docker/setup-buildx-action@v3

        # 3) Login to GitHub Container Registry
        - name: Login to GitHub Container Registry
          uses: docker//login-action@v3
          with:
            registry: ghcr.io
            username: ${{ github.actor }}
            password: ${{ secrets.DEV_PKG_TOKEN}}

        # 4) Build & Push Docker Image (dev 태그 + sha 태그)
        - name: Build and push Docker Image
          uses: docker/build-push-action@v5
          with:
          	# 도커 빌드 컨텍스트를 현재 워크스페이스 루트로 지정
            context: .
            file: docker/dev/Dockerfile
            push: true
            tags: |
              ghcr.io/${{ github.repository_owner }}/aws-web-app:dev
              ghcr.io/${{ github.repository_owner }}/aws-web-app:${{ github.sha }}

        # 5) Print Builded Image Info
        - name: Image pushed summary
          run: |
            echo "Image: ghcr.io/${{ github.repository_owner }}/aws-web-app:dev"
            echo "Image: ghcr.io/${{ github.repository_owner }}/aws-web-app:${{ github.sha }}"
```

- GHCR에 push할려면 PAT(fine-grained or classic)이 필요함. 일반 GH_TOKEN / GITHUB_TOKEN은 private packages write 권한이 없다.

![](/assets/images/hosooinmymind/images/hosooinmymind/post/ed564476-8162-4da5-90bc-e98e7cd5dac8/image.png)빌드+push까지 성공한 것 확인