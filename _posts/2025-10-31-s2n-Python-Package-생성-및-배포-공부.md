---
layout: post
title: "[s2n] Python Package 생성 및 배포 공부"
date: 2025-10-31 08:53:15 +0900
categories: velog
series: "s2n"
---

Python을 이용하면서 pip install 명령어를 통해서 패키지를 등록하는 게 국룰.
그럼 이 패키지는 어떻게 만드는 걸까? 그리고 Pip install을 이용해서 파이썬 패키지를 설치하는 것은 어떻게 만들까?

### 진행과정
1. PyPI에 접근해 계정 등록을 한다.
2. 프로젝트 구조 생성하기
3. 모듈 작성하기
4. 패키지 파일 작성하기
	(1) pyproject.toml 파일 생성
    (2) metadata 작성하기
    (3) README.md 파일 작성
    (4) LICENSE 파일 작성하기
5. 빌드하기 (빌드모듈 설치 -> 빌드)
6. 패키지 업로드하기 (패키지 업로드 모듈 설치하기 -> 패키지 업로드)
7. 패키지 설치
8. 테스트 프로그램 수행하기

### 프로젝트 빌드를 위한 기본 구조
- scdev_kit
  - src
    - scdev_pd_column
      - __init__.py
      - example.py
  - LICENSE.txt
  - pyproject.toml
  - README.md
  - setup.py
  
scdev_pd_column: 소스내부에 패키지 이름이 된다.
init.py: 패키지 디렉토리 내부에 파일들이 모듈임을 알려준다.
example.py: 모듈이 작성된 파일이다.
LICENSE.txt: 패키지의 라이선스를 정의한 파일이다.
pyproject.toml: 프로젝트에 필요한 라이브러리에 대한 내역을 기술해준다.
README.md: 프로젝트 라이브러리 사용 설명서를 기술한다.
setup.py: 빌드를 위한 빌드 정보를 기술하는 파일이다.


### 패키지 파일 작성하기
#### pyproject.toml 파일 생성
pyproject.toml 파일은 빌드 툴에게 (pip or build) 프로젝트 빌드를 위해서 필요한 의존성을 알려준다.
여기서는 setuptools과 wheel을 이용할 것이다.
```
[build-system]
requires = [
    "setuptools>=42",
    "wheel"
]
build-backend = "setuptools.build_meta"
```
- build-sstem.requires:
	
    - 패키지의 목록을 나열한다.
    - 패키지 빌드를 위해서 필요한 항목을 지정한다.
    - 여기에 항목을 나열하면 설치 후가 아니라 빌드 중에만 사용하게 된다.
- build-system.build-backend:
		
	- 빌드를 수행할 때 파이썬 객체의 이름이다.
    - 다른 빌드 시스템을 이용한다면 여기에 기술해야 한다.
    
#### metadata vkdlf wkrtjdgkrl
setup.cfg와 setup.py를 생성할 수 있다.
https://packaging.python.org/en/latest/tutorials/packaging-projects/
에서 Configuring metadat를 참조하면 된다.
- setup.cfg: 매번 동일한 빌드를 수행할 수 있도록 하는 정적 메타 데이터이다. 단순하고, 읽기 쉽고, 많은 공통적인 에러를 피할 수 있다.
- setup.py: 고정되지 않은 동적 빌드를 위해 사용된다. 모든 아이템은 동적 혹은 설치시 결정되는 모듈을 작성한다.

setup.py의 예시
```
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-scdev-pd-columns",
    version="0.0.1",
    author="Schooldevops",
    author_email="schooldevops@gmail.com",
    description="schooldevops sample lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/schooldevops/python-tutorials",
    project_urls={
        "Bug Tracker": "https://github.com/schooldevops/python-tutorials/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
```
- projects_urls: PyPI에서 보여줄 추가적인 링크를 나타냄. 보통 깃헙 같은 소스 리포지토리가 들어감.
- classifiers: 패키지를 위한 몇가지 추가적인 메타데이터 나열. 파이썬 패키지, 라이선스, 운영체제 등 나열
- package_dir: 패키지 이름들과 디렉토리 기술


### 빌드하기
빌드를 수행하여 패키지 파일을 생성한다.

#### 빌드 모듈 설치
build를 설치한다고 가정하면
```
% python -m pip install --upgrade build
```

#### 빌드 수행하기
프로젝트 디렉토리에 이동해서
```
cd scdev_kit
python -m build
```
빌드 수행. 하고 나면 다음 파일이 생성된다.
```
- scdev_kit
  - example_pkg_sdcev_pd_columns-0.0.1-py3-none-any.whl
  - example-pkg-sdcev-pd-columns-0.0.1.tar.gz
```
- tar.gz는 소스 아카이브이다.
- whl 파일은 빌드된 배포본이다.

### 패키지 업로드
twine 패키지를 이용해 업로드해야 한다.
python -m pip install --upgrade twine
으로 설치한다.
python -m twine upload dist/*
으로 업로드하면 된다.


https://devocean.sk.com/blog/techBoardDetail.do?ID=163566