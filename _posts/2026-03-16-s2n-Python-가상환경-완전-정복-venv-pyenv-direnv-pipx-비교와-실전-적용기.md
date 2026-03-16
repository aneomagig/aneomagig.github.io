---
layout: post
title: "[s2n] Python 가상환경 완전 정복: venv, pyenv, direnv, pipx 비교와 실전 적용기"
date: 2026-03-16 07:06:30 +0900
categories: velog
series: "s2n"
---


## 들어가며
심화프로젝트가 끝나고 실무통합 프로젝트를 진행하면서는, 단순 코딩 작업보다는 다른 팀과 소통하고 문서화해야 하는 태스크가 더 많아서 블로그를 작성할 기회가 별로 많지 않았다. 그래서 오랜만에 작은 티켓이지만 이거라도 작성해 보고자 한다.

파이썬 개발을 하다 보면 가상환경 세팅이 항상 골칫거리다. 특히 팀 프로젝트에서는 "내 컴퓨터에서는 되는데요?"라는 말이 나오지 않으려면 개발 환경을 통일하는 게 중요하다. 오늘은 파이썬 가상환경 도구들을 정리하고, 실제로 `pipx`를 도입하려다가 `direnv`로 귀결된 과정을 기록한다.

---

## 1. 파이썬 가상환경이란?

파이썬은 패키지를 시스템 전역에 설치하는 구조라, 프로젝트마다 의존성 버전이 달라지면 충돌이 발생한다.

```
프로젝트 A: requests==2.28.0
프로젝트 B: requests==2.31.0
```

이 문제를 해결하기 위해 **프로젝트별로 격리된 파이썬 환경**을 만드는 것이 가상환경이다.

---

## 2. 도구별 역할 정리

### venv (파이썬 내장)

가장 기본적인 가상환경 도구. 파이썬 3.3부터 내장되어 있다.

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

- 장점: 별도 설치 불필요, 심플
- 단점: 매번 수동으로 activate 해야 함, 파이썬 버전 관리 불가

---

### pyenv

파이썬 버전 자체를 관리하는 도구. 프로젝트마다 다른 파이썬 버전을 쓸 수 있다.

```bash
pyenv install 3.11.9
pyenv local 3.11.9   # 해당 폴더에서 사용할 버전 지정 → .python-version 파일 생성
```

`.python-version` 파일이 생성되어 폴더별로 파이썬 버전이 고정된다.

---

### direnv

디렉토리에 진입할 때 자동으로 환경변수를 로드해주는 도구. `.envrc` 파일에 설정을 적어두면, 해당 폴더에 `cd`하는 순간 자동 실행된다.

```bash
# .envrc
export PYENV_VERSION=$(cat .envs/python/.python-version)
source .envs/python/.venv/bin/activate
```

```bash
direnv allow   # 최초 1회만 실행
```

이후부터는 폴더에 진입하는 것만으로 venv가 자동 활성화된다.

- 장점: 자동화, 팀원 모두 동일한 환경 진입 가능
- 단점: direnv 자체를 별도 설치해야 함

---

### pipx

CLI 도구를 격리된 환경에 설치하는 도구. `npm install -g`와 비슷하지만, 각 도구가 독립된 가상환경을 가진다.

```bash
pipx install s2n           # PyPI에서 설치
pipx install --editable .  # 로컬 코드를 editable 모드로 설치
```

- 장점: CLI 도구 전역 설치, 프로젝트 간 격리
- 단점: 개발용 의존성(pytest 등) 포함이 번거로움

---

## 3. pipx를 도입하려다가 포기한 이유

오픈소스 CLI 도구인 `s2n`을 개발하면서, 매번 `source .envs/python/.venv/bin/activate`를 치는 게 귀찮아서 pipx로 개발 환경을 통일할 수 있지 않을까 생각했다.

### 처음 생각한 그림

```
pipx install --editable .
→ s2n CLI 전역 사용 가능
→ 코드 수정 즉시 반영
→ 팀원 모두 동일한 환경
```

### 문제: pytest를 어떻게?

pipx는 기본적으로 `pyproject.toml`의 production 의존성만 설치한다. `pytest`, `responses` 같은 dev 의존성은 포함되지 않는다.

`pipx inject`로 추가하는 방법이 있긴 하다:

```bash
pipx install --editable .
pipx inject s2n pytest responses pytest-cov
```

그런데 pytest를 실행하려면:

```bash
~/.local/share/pipx/venvs/s2n/bin/pytest  # 이 경로를 직접 써야 함
```

이게 venv 활성화보다 더 번거롭다.

### 결론: 도구 선택 기준

| 상황 | 적합한 도구 |
|---|---|
| 최종 사용자가 CLI 설치 | `pipx install s2n` |
| 개발 중 (pytest 포함) | `venv` + `direnv` |
| 파이썬 버전 관리 | `pyenv` |

**pipx는 최종 사용자용, venv+direnv는 개발자용**이 맞다.

---

## 4. 실제로 고친 것: direnv 버그 수정

`direnv`를 세팅해뒀는데 실제로 동작하지 않는 문제가 있었다.

### 원인

`.envrc`에 `$VENV_DIR`라는 환경변수를 사용하고 있었는데, 이 변수가 어디에도 정의되어 있지 않았다.

```bash
# 기존 (버그)
export PYENV_VERSION=$(cat .envs/python/.python-version)
source $VENV_DIR/bin/activate   # $VENV_DIR이 빈 문자열 → 동작 안 함
```

### 수정

```bash
# 수정 후
export PYENV_VERSION=$(cat .envs/python/.python-version)
source .envs/python/.venv/bin/activate
```

이후 `direnv allow` 한 번만 실행하면, 프로젝트 폴더에 진입할 때마다 자동으로 venv가 활성화된다.

---

## 5. 최종 개발 환경 구성

```
s2n/
├── .envs/
│   └── python/
│       ├── .python-version   ← pyenv로 파이썬 버전 고정
│       └── .venv/            ← venv 가상환경
├── .envrc                    ← direnv 설정 (자동 venv 활성화)
├── pyproject.toml            ← 패키지 의존성
└── requirements-dev.txt      ← 개발 의존성 (pytest 등)
```

**사용 흐름:**
1. 최초 1회: `direnv allow`
2. 이후: 폴더 진입하면 자동으로 venv 활성화
3. 개발: `pytest` 바로 실행 가능
4. 배포된 CLI 테스트: `pipx install .`

---

## 마치며

처음에는 pipx로 모든 걸 해결하려 했지만, 도구마다 설계 목적이 다르다는 걸 다시 확인했다. **pipx는 사용자를 위한 도구, direnv+venv는 개발자를 위한 도구**. 목적에 맞는 도구를 쓰는 게 결국 가장 심플한 해결책이었다.
