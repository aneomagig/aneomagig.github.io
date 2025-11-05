---
layout: post
title: "[s2n] PyPI 배포용 Python 패키지 + Jenkins 기반 CI/CD 구조 이해하기"
date: 2025-10-31 07:31:04 +0900
categories: velog
series: "s2n"
---

<h3 id="1-용어-정리">1. 용어 정리</h3>
<ul>
<li><p>venv</p>
<ul>
<li>로컬 (혹은 CI)에서 프로젝트 전용 파이썬 가상환경을 만드는 것. 시스템 파이썬과 격리해서 패키지를 설치/관리함.</li>
<li>왜 필요? -&gt; 서로 다른 프로젝트가 서로 다른 버전의 패키지를 요구할 때 충돌을 막기 위해</li>
</ul>
<ul>
<li><p>requirements.txt</p>
<ul>
<li>pip로 설치할 때 읽는 의존성 목록 ex: requests==2.31.0</li>
<li>주로 CI (또는 도커 이미지 빌드)에서 빠르게 pip install -r requirements.txt로 환경 만들 때 사용</li>
</ul>
</li>
</ul>
</li>
<li><p>pyproject.toml</p>
<ul>
<li>현대적인 파이썬 패키지 메타데이터/빌드 설정 파일. 패키지 이름, 버전, 빌드 백엔드 등을 정의 (Poetry/PDM/Setuptools 모두 여기 사용)</li>
<li>패키지(배포)의 소스 표준 -&gt; core 패키지 안에 두는 게 좋음</li>
</ul>
</li>
<li><p>poetry.lock / pdm.lock / pipfile.lock</p>
<ul>
<li>의존성 정확한 버전 고정(lock) 파일. CI나 다른 개발자가 똑같은 의존성으로 재현하도록 도움.</li>
</ul>
</li>
<li><p>dev-dependencies vs dependencies</p>
</li>
</ul>
<pre><code>- dev는 개발 테스트용 (ex: pytest, black)
- dependencies는 런타임에 필요한 것 (ex: requests)</code></pre><ul>
<li><p>wheel, sdist (dist/*)</p>
<ul>
<li>빌드 산출물. PyPI에 올리는 파일들 (Python -m build으로 생성). Jenkins가 생성해서 twine으로 올림.</li>
</ul>
</li>
<li><p>twine    </p>
<ul>
<li>PyPI 업로드 도구. 토큰 인증으로 업로드.</li>
</ul>
</li>
</ul>
<h3 id="2-권장-구조">2. 권장 구조</h3>
<pre><code>s2n/                       # repo root (monorepo)
├── core/                  # &lt;--- 패키지(각각의 파이썬 패키지들)
│   ├── s2nscanner/
│   │   └── __init__.py
│   ├── tests/
│   ├── pyproject.toml     # 패키지 메타데이터 (필수)
│   ├── poetry.lock OR pdm.lock OR pipfile.lock  # lockfile (있으면 포함)
│   ├── requirements.txt   # CI / Docker 빌드용 (권장)
│   └── README.md
│
├── infra/
│   ├── Dockerfile
│   ├── Jenkinsfile        # (또는 루트에 둘 수도 있음)
│   └── scripts/
│       └── deploy_pypi.sh
│
├── scripts/               # 루트 수준 유틸(버전버UMP, release helper 등)
├── docs/
├── .gitignore
└── README.md</code></pre><ul>
<li><p>pyproject.toml: core/ 안에 반드시 있어야 함. 패키지 단위 메타데이터는 패키지 폴더에 가까운 곳에 있어야 함</p>
</li>
<li><p>requirements.txt: core/requirements.txt (CI/Docker이 사용하기 편하게)</p>
<ul>
<li>내용 예시: 런타임 의존성 (-r requirements.txt) 또는 pip install build twine 등 빌드 도구 포함</li>
</ul>
</li>
<li><p>lockfile: core/ 에 둬서 버전 동결 (CI는 Lockfile 기준으로 재현)</p>
</li>
<li><p>.venv/ : 로컬 개발자는 로컬에만 만들거나 각자 홈폴더에 생성 -&gt; 절대 리포지토리에 커밋 X, .gitignore에 추가</p>
</li>
<li><p>infra/Jenkinsfile 또는 루트 Jenkinsfile: Jenkins 파이프라인 정의 (프로젝트가 커지면 루트에 두고 core 빌드 파라미터로 설정)</p>
</li>
<li><p>infra/Dockerfile: 빌드/테스트 컨테이너 이미지. Jenkins 에이전트로 활용</p>
</li>
</ul>
<h3 id="3-로컬-개발자-규칙">3. 로컬 개발자 규칙</h3>
<ol>
<li>core로 들어가서 가상환경 생성<pre><code>cd core
python -m venv .venv
source .venv/bin/activate (Mac)
.venv\Scripts\activate (Windows)
pip isntall -r requirements.txt</code></pre></li>
<li>개발 시 의존성 추가하면 requirements-dev.txt 또는 pyproject.toml에 추가 -&gt; lock 업데이트</li>
<li>.venv는 커밋 X</li>
</ol>
<h3 id="4-monorepo에서-venvrequirements-관리-전략">4. Monorepo에서 venv/requirements 관리 전략</h3>
<ul>
<li>각 패키지 (core/)가 독립성 의존성 가짐</li>
<li>core/pyproject.toml (주 설정)</li>
<li>core/requirements.txt (CI/Docker용 빠른 설치 표준)</li>
<li>core/poetry.lock 또는 core/pdm.lock (버전 재현성)</li>
<li>루트에는 dev-helper 의존성 (ex: pre-commit, realese tooling)만 두고 scripts/로 관리</li>
<li>이유: 모노레포지만 패키지 단위로 빌드/배포 가능 -&gt; 각 패키지의 독립성이 높음</li>
</ul>
<h3 id="5-jenkisn-파이프라인-설계">5. Jenkisn 파이프라인 설계</h3>
<p>젠킨스는 보통 다음 스테이지로 구성.
    1.    Checkout — Git에서 코드 가져오기 (모노레포라서 변경된 패키지만 빌드하게 설정 가능)
    2.    Setup Environment — Docker 에이전트 혹은 venv 생성
    3.    Install deps — pip install -r core/requirements.txt
    4.    Run tests — pytest core/tests
    5.    Build — cd core &amp;&amp; python -m build → dist/<em>.whl, *.tar.gz 생성
    6.    Publish — main 브랜치일 경우 twine upload dist/</em> (Jenkins credentials 사용)
    7.    Archive artifacts / Notify — 빌드 결과 보관 및 알림</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/986ba3d4-4a9e-4de9-9a3f-32727534df03/image.png"/>
이렇게 설계 완료</p>
<p>pyproject.toml            패키지 정보 및 빌드 설정
requirements.txt        의존성 목록 (CI 설치용)
Dockerfile                Jenkins 빌드 환경 정의
Jenkinsfile                테스트 → 빌드 → 배포 자동화 파이프라인
deploy_pypi.sh            PyPI 배포 자동 실행 스크립트
detect_core_change.sh    변경된 디렉터리 감지(빌드 스킵용)
dev.yml, prod.yml        환경별 변수 및 구성 파일</p>
<ol>
<li>CI/CD 파이프라인</li>
</ol>
<ul>
<li>Jenkinsfile에서 core 변경 감지 후 테스트/빌드/배포 단계 자동 실행.</li>
<li>PyPI 토큰은 Jenkins Credentials로 관리.</li>
</ul>
<ol start="2">
<li>도커 환경 통일</li>
</ol>
<ul>
<li>Dockerfile 기반으로 Jenkins 빌드 시 동일 환경 보장.</li>
</ul>
<ol start="3">
<li>브랜치 정책</li>
</ol>
<ul>
<li>dev 브랜치: 테스트용 빌드</li>
<li>main 브랜치: PyPI 배포 트리거</li>
<li>필요 시 detect_core_change.sh로 변경 여부 판단 후 자동화 최적화.</li>
</ul>
<ol start="4">
<li>배포 구성</li>
</ol>
<ul>
<li>deploy/ 내 dev/prod YAML 파일을 기반으로 AWS 등 외부 환경에 IaC 연동.</li>
</ul>