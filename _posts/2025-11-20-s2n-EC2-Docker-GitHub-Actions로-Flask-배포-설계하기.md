---
layout: post
title: "[s2n] EC2 + Docker + GitHub Actions로 Flask 배포 설계하기"
date: 2025-11-20 06:24:38 +0900
categories: velog
series: "s2n"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/42e9ae8c-8609-4273-bfd9-193c36105b64/image.png"
---

s2n 스캐너의 MVP 개발은 얼추 끝났고, 이 스캐너를 테스트하기 위해 간단한 Flask 기반 익명 채팅 웹앱을 AWS에 배포하는 작업을 진행할려고 한다. 
s2n 스캐너 자체는 이미 dev/main 브랜치 기준으로 GHCR에 도커 이미지를 올려두는 CI/CD가 구축되어 있는데, 이 구조를 참고하여 웹앱 전용 배포 파이프라인을 구축해보고자 한다.

----------

## 1. 배포 전략 Overview
1. dev 브랜치에 push -> GitHub Actions 자동 실행
2. Dockerfile 기반으로 도커 이미지 빌드
3. 빌드된 이미지를 GHCR에 push
4. EC2가 docker pull -> 컨테이너 재시작
5. 실제 서비스는 EC2에서 실행

즉 GitHub -> GHCR -> EC2로 이어지는 Pull-based CD 흐름이다.
여기서 핵심은,
- CI/CD로 매번 정확한 버전의 Docker 이미지를 자동 생성한다.
- EC2는 해당 이미지만 끌어다 실행하면 된다.

## 2. 워크플로우 Trigger 및 권한 설정
dev 브랜치에서 push 이벤트가 발생하면 자동으로 workflow가 실행된다.
```
on:
  push:
    branches: [ dev ]

permissions:
  contents: read
  packages: write
```
여기서 packages: write를 꼭 해 줘야 GHCR에 도커 이미지를 push할 수 있다.

## 3. 전체 CI/CD 파이프라인 flow
아키텍처 흐름을 정리하자면
![](/assets/images/hosooinmymind/images/hosooinmymind/post/42e9ae8c-8609-4273-bfd9-193c36105b64/image.png)위와 같다.
핵심 포인트들은:
- 소스 체크아웃
- 파이썬 빌드 툴 설치 (옵션)
- Wheel(whl) 패키징 (옵션)
- GHCR 로그인
- 도커 이미지 빌드 & push
- dev 전용 태그(:dev) + 커밋 SHA 태그 2종류 동시 생성

## 4. GitHub Actions Workflow 상세
대략 구상해 보자면
```
jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: 3.11

      - name: Install build deps
        run: python -m pip install --upgrade build

      - name: Build Python package (optional)
        run: python -m build || echo "Build skipped"

      - name: Log in to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.DEV_PKG_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./docker/dev/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/chatapp:dev
            ghcr.io/${{ github.repository_owner }}/chatapp:${{ github.sha }}
```
이런 식이 될 것 같다.
이미지 두 개를 푸시하는 이유는 아래와 같다.
- `:dev` -> 항상 최신 dev 배포 버전
- `:<git-sha>` -> 롤백할 때 특정 버전 지정 가능 (EC2에서 docker pull ...:abc123 형태로 재배포)

## 5. dev 브랜치 전용 Dockerfile 설계
s2n 스캐너의 dev Dockerfile을 참고해서, stage 1 build + stage 2 runtime 구조로 설계했다.

docker/dev/Dockerfile
```
# ------- Builder stage -------
FROM python:3.11-slim AS builder
WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml setup.cfg /src/
COPY . /src

RUN python -m pip install --upgrade pip build setuptools wheel && \
    python -m build --wheel --outdir /dist


# ------- Runtime stage -------
FROM python:3.11-slim
WORKDIR /app

COPY --from=builder /dist /dist
RUN pip install --no-cache-dir /dist/*.whl

COPY . .

CMD ["python", "main.py"]
```
고려한 점
- runtime 이미지에는 빌드 도구 제거
- EC2에는 오직 python 패키지가 들어 있는 휠 파일만 설치
- 빌드 캐시 활용을 위해 메타 파일(pyproject.toml)이 먼저 COPY

## 6. .dockerignore 최적화
```
.git
.gitignore
__pycache__
dist
build
.env
node_modules
*.md
```
컨텍스트가 커지면 빌드 시간이 늘어나므로 위 파일들은 dockerignore에 포함할 예정이다.

## 7. EC2에서 어떻게 사용할까?
CI/CD가 GHCR까지는 자동으로 완료되므로, EC2에서는 명령어 한 줄만 실행하면 배포가 끝난다.
```
docker pull ghcr.io/OWNER/chatapp:dev
docker compose up -d
```
개별 run 방식이라면
```
docker pull ghcr.io/OWNER/chatapp:dev
docker stop chatapp || true
docker run -d -p 5000:5000 --env-file .env --name chatapp ghcr.io/OWNER/chatapp:dev
```
즉 EC2는 오직 pull + run만 책임진다.
코드가 변경되면:
1. dev 브랜치에 merge
2. GitHub Actions가 자동 빌드
3. GHCR 이미지 업데이트
4. EC2는 최신 태그 pull

## 8. 배포 플로우 총정리
1. 개발자가 dev에 push
2. GitHub Actions
	- checkout
    - python build
    - dockerfile build
    - GHCR push
3. EC2
	- docker pull
    - docker compose up -d
4. 실제 서비스에 반영 완료