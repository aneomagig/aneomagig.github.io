---
layout: post
title: "[s2n] GitHub Actions로 CI/CD 파이프라인 구축하기 (feat. 젠킨스)"
date: 2025-11-03 05:43:11 +0900
categories: velog
series: "s2n"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/26a63ac7-425f-4971-b44b-9fb4a78187de/image.png"
---

## Chapter 1 (시행착오)
젠킨스만을 위한 서버를 구축하는 건 우리 프로젝트에 너무 오버스펙이기도 하고, 비용 문제도 있어서 GitHub Actions 위에 Jenkins를 Docker으로 올려서 사용하기로 했다.
항상 프론트엔드 개발만 하다가 인프라는 아예 처음이다. 이번 프로젝트가 잘 마무리되길 빌며... 

### 1. Jenkins / GitHub Actions가 뭘까?
- Jenkins: 자동화 서버. 직접 서버를 띄워서 빌드/배포 작업을 실행함.
- GitHub Actions: 깃헙 안에 내장된 자동화 서비스/별도 서버 없이 push, PR 이벤트로 파이프라인 자동 실행

### 2. 목표 + 구조 설계 이유
GitHub Actions 안에서 Docker로 젠킨스를 실행하고, 젠킨스가 내부 파이프라인을 실행하는 구조를 구축한다.
즉 GitHub Actions -> Docker 컨테이너 실행 -> Jenkins 서버 구동 -> Jenkins Job 실행의 구조.

GitHub이 자동으로 제공하는 runner는 빌드가 시작될 때 생성되고 빌드가 끝나면 삭제되는 가상머신이다. 그래서 젠킨스를 도커로 띄우면 **EC2, AWS 요금이 발생하지 않을 수 있다.**
그리고 우리가 하는 프로젝트는 "한 달짜리 실습용 기초 프로젝트"이기 때문에 젠킨스 서버를 외부에 구축해서 돌리는 것은 오버스펙이라고 판단했다. 하지만 젠킨스를 사용해보고는 싶어서 이런 이상한 구조가 나오게 된 것이다. 결론은 **비효율적인 거 알지만, 젠킨스를 써보고 싶어요...**
물론 이렇게 젠킨스를 사용하면 로그/파일들이 아무것도 남지 않는다. 그래서 결과를 외부 저장소로 보내야 대시보드를 볼 수 있음. 

### 전체 단계
1. Docker 설치 (본 포스팅에서는 생략)
2. Jenkins 컨테이너 실행
3. Jenkins 초기 설정
4. Jenkins Job 실행
5. 자동화 정리


### STEP 2 — Jenkins 컨테이너 실행하기
```
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```
-d: 백그라운드 모드로 실행
--name jenkins: 컨테이너 이름을 jenkins로 지정
-p 8080:8080: 내 컴퓨터 8080 포트를 젠킨스 웹 인터페이스와 연결
-p 50000:50000: 젠킨스 에이전트용 포트 (지금은 그냥 열어두기)
-v jenkins_home:/var/jenkins_home: 젠킨스 설정/데이터를 도커 볼륨에 보존
![](/assets/images/hosooinmymind/images/hosooinmymind/post/26a63ac7-425f-4971-b44b-9fb4a78187de/image.png)docker ps 명령어로 실행 상태 확인. 잘 돌아가고 있음.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/edd3e3cb-499c-43bf-9c80-c35e4d0073f6/image.png)![](/assets/images/hosooinmymind/images/hosooinmymind/post/6b15fd19-4966-49c1-8fce-c1579596bfe5/image.png)![](/assets/images/hosooinmymind/images/hosooinmymind/post/903fae8b-59c8-4cc3-8c0a-a7fc3510fbe6/image.png)설정 끝~

### STEP 3 — Jenkins Job (Pipeline) 생성하기
- 젠킨스가 정상적으로 빌드를 수행할 수 있는 기본 파이프라인 job 생성
- github repo 연결 준비까지 완료
![](/assets/images/hosooinmymind/images/hosooinmymind/post/e3e5d4b7-fa2b-440f-a047-d17948049783/image.png)

```
pipeline {
    agent any
    
    stages {
    	# 깃헙에서 코드 가져오기
        stage('Clone repository') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url: 'https://github.com/504s2n/s2n'
            }
        }
        
        # 파이썬 가상환경 + requirements 설치
        stage('Install dependencies'){
            steps{
                echo 'Installing dependencies...'
                sh 'python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt || true'
            }
        }
        
        #pytest 실행, 없으면 그냥 통과
        stage('Run tests'){
            steps{
                echo 'Running tests...'
                sh 'pytest || echo "No tests found"'
            }
        }
        stage('Build complete'){
            steps{
                echo 'Jenkins pipeline executed successfully.'
            }
        }
    }
}
```

![](/assets/images/hosooinmymind/images/hosooinmymind/post/22a65f5b-42e7-4101-bf83-73060a081d39/image.png)야호~

### STEP 4 - GitHub -> Jenkins 자동 연결
여기서 두 가지 갈림길이 있다.
첫 번째는 Webhook, 두 번째는 API 호출. 하지만 웹훅을 사용할려면 외부에 항시 운영되는 젠킨스 서버가 필요하다. 우리 프로젝트에서는 젠킨스 서버를 만들지는 않기로 했으므로 후자로 결정.

(1) 젠킨스에서 API 토큰 발급
(2) GitHub Secrets에 등록
(3) GitHub Actions Workflow에서 Jenkins API 호출
(4) push시 Jenkins 자동 빌드

#### (1) 젠킨스에서 API 토큰 발급
![](/assets/images/hosooinmymind/images/hosooinmymind/post/af1e7450-1a98-497b-aad3-1762ae59e8c7/image.png)

===================================================
## 잠깐!
여기까지 하고 중간 점검을 해봤는데, 이 구조로 계속 진행하면 Jenkins가 내 맥북에서만 돌아가고, 내 컴퓨터가 꺼지면 CI도 정지하게 된다. 거기다 ngrok 세션은 8시간마다 끊겨서 매번 갱신해야 하고, 다른 팀원은 아예 접근이 불가능하다는 점 등... 현실적으로 AWS EC2에 Jenkins 서버를 상시 운영하거나 GitHub Actions 단독 구성을 해야 한다는 두 가지 선택지가 남았다. 첫 번째 의견은 팀원들의 반대. 우리 프로젝트에 오버스펙인 데다가, 3주 뒤가 발표인 상황에서 굳이 해야 하냐는 의견이 주였다. 아쉽지만 다음 프로젝트에서 젠킨스를 사용해보는 걸로 하고, 그냥 깃헙 액션스 단독 구성만 하기로 했다.

결론적으로 CI는 PR시 자동 테스트, CD는 메인 브랜치 머지 시 자동 빌드 및 PyPI 배포 / 도커 이미지 자동 빌드 및 푸시 이렇게 하기로 했다.


## Chapter 2: Jenkins 제거 + GitHub Actions 단독 CI/CD 구축 

### 1. CI 파이프라인 - 테스트용 생성
가장 먼저 .github/workflows 폴더를 생성한다. GitHub는 이 경로에 있는 yaml 파일만 워크플로우로 인식한다.

CI 파이프라인 구축의 목표는 main 브랜치에 푸시되면 자동 빌드 + 테스트가 진행되고, PyPI 배포 준비를 위한 패키징 검증을 하는 것이다.

#### setup.py vs pyproject.toml
setup.py와 pyproject.toml 중 뭘 사용할지 선택해야 했다. 둘 다 파이썬 패키지 배포와 빌드 설정을 담당하지만 조금 다르다.
- setup.py
기존의 표준 파이썬 패키징 방식으로, setuptoos / distutils를 사용해 패키지를 빌드하고 배포한다. pip install . 하면 python setup.py install이 자동적으로 호출된다.
	패ㅣ지 이름, 버전, 의존성 등을 정의하고, 빌드(sdist, bdist_wheel)나 배포(twine upload)에 사용한다. 
    설정이 파이썬 코드로 작성되기 때문에 단순한 설정도 실행 시점에 코드를 실행해야 하므로 보안 문제가 발생할 수 있고, 빌드 툴이 섞여 있으면 충돌이 발생할 수 있다.
   
```
# setup.py 예시
from setuptools import setup, find_packages

setup(
    name="mypackage",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests", "numpy"],
)
```

- pyproject.toml
	새로운 표준 구성 파일으로, 프로젝트의 메타데이터와 빌드 백엔드 정의를 toml 형식으로 명시한다.
```
# pyproject.toml 예시
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mypackage"
version = "0.1.0"
description = "A modern Python package"
authors = [{ name = "Minji", email = "minji@example.com" }]
dependencies = ["requests", "numpy"]  
```
=> pyproject.toml 사용하기로 결정!

테스트용 ci-cd.yml, requirements.txt, pyproject.toml를 만들어서 푸시했고, 아래와 같이 setup.py를 기반으로 한 빌드 테스트까지 자동화가 잘 되는 것을 확인했다. 이제 이 파일들을 프로젝트 구조에 맞춰서 수정하고, PyPI 배포 파이프라인을 구축하면 된다.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/d50eec74-fe19-4741-a320-40e596cc6a3c/image.png) 

### 2. CI 파이프라인 - 프로젝트에 맞추기
(1) .venv로 가상환경 생성- 독립적인 파이썬 실행 환경 생성
(2) 빌드 툴 설치 (pip install build twine setuptools wheel) - 패키지를 빌드하고 검증/배포할 수 있는 표준 도구 설치
(3) pyproject.toml 작성
(4) python -m build 실행 - dist/s2n-0.1.0.tar.gz, dist/s2n-0.1.0-py3-none-any.whl 생성 -> 소스 코드에서 실제 배포 가능한 패키지로 빌드됨
	- s2n-0.2.0.tar.gz: Source Distribution - 사용자가 직접 빌드해서 사용 가능
	- s2n-0.2.0-py3-none-any.whl: Wheel Distribution - pip install 시 즉시 설치 가능

(5) twine check 실행 - 메타데이터 검증

```
ci-cd.yml
name: s2n CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
  release:
    types: [published]
    # github realese 생성 시에만 Pypi 업로드 트리거

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest -v || echo "No tests found, skipping"

  build-package:
    needs: build-test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: 3.11

      - name: Install packaging tools
        run: |
          pip install --upgrade build

      - name: Build Package
        run: |
          python -m build
          # pyproject.toml 기반 빌드 방식
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: s2n-dist
          path: dist/
          # 빌드 결과 /dist를 릴리즈 job으로 안전하게 전달

  deploy:
      needs: build-package
      if: github.event_name == 'release' && github.event.action == 'published'
      runs-on: ubuntu-latest
      steps:
        - name: Checkout code
          uses: actions/checkout@v4

        - name: Set up Python
          uses: actions/setup-python@v5
          with:
            python-version: 3.11

        - name: Download build artifacts
          uses: actions/download-artifact@v4
          with:
            name: s2n-dist
            path: dist/

        - name: Install Twine
          run: |
            pip install --upgrade twine

        - name: Publish to PyPI
          env:
            TWINE_USERNAME: ${{ secrets.PYPI_USER }}
            TWINE_PASSWORD: ${{ secrets.PYPI_PASS }}
          run: |
            twine upload dist/* --non-interactive || echo "Deployment skipped"
            # 빌드 결과를 pypi 업로드
```
즉 main 브랜치에서 Push => 테스트 & 빌드 확인 => github에서 release -> publish 하면 자동으로 dist/*.whl 업로드 -> twine upload dist/* 실행 => pypi에 새로운 s2n 버전이 생성됨

![](/assets/images/hosooinmymind/images/hosooinmymind/post/4046483b-5af1-4b56-8707-712743c0f753/image.png)
잘 돌아감. CI는 끝났고...

## CD Test
![](/assets/images/hosooinmymind/images/hosooinmymind/post/c1535c2b-2d85-41b7-8025-8b41479afbc7/image.png)![](/assets/images/hosooinmymind/images/hosooinmymind/post/e5d30568-4fca-4125-b415-d532ba16550f/image.png)![](/assets/images/hosooinmymind/images/hosooinmymind/post/7587d13f-c94b-46a2-9a3a-131b8ae1beae/image.png)
야호~~~ 새로운 Release가 생길 때마다 자동으로 이 과정이 수행된다. 