---
layout: post
title: "[s2n] 라이브러리를 CLI + import가 가능하게 구조화하기"
date: 2025-11-06 06:20:35 +0900
categories: velog
series: "s2n"
---




### 1. 문제 정의
- s2n 스캐너를 터미널에서도, 파이썬 코드에서도 실행할 수 있게 할 것
- 즉, 하나의 엔진 (Scanner)을 CLI, import 두 경로로 모두 접근 가능하게 해야 함.

### 2. 요구사항 도출
(1) 공통 엔진이 필요함. -> CLI/import가 같은 로직을 써야 하기 때문.
(2) CLI 명령어로 실행 가능해야 함 -> PyPI 배포 후 사용자가 쉽게 s2n scan ... 형태로 실행해야 함
(3) python -m s2n으로도 실행 가능해야 함
(4) from s2n import Scanner로 사용 가능해야 함 -> 코드 내 자동화/테스트/다른 프로그램과 통합 가능해야 함
(5) 구조가 명확히 분리되어야 함

### 3. 구조 설계
- 파이썬은 import 경로를 인식할 때 패키지 이름을 디렉토리 이름으로 인식하기 때문에, from s2n import Scanner과 같이 쓰면 실제로는 /s2n/__init.py를 찾는다. s2n CLI는 pyproject.toml의 [project.scripts] s2n = "S2n.cli:cli"에서 s2n 패키지를 기준으로 탐색한다.
그런데 지금은 core/, s2nscanner/ 안에 main.py가 있는데 이 둘은 패키지 루트가 아니기 때문에 import s2n과 같이는 사용할 수 없다. 그래서 파일 디렉토리부터 수정.
- 하나의 엔진을 중심으로 CLI, import, test 진입점을 분리한다.
```
s2n/
├── cli.py         # 사용자 명령을 받아 core를 실행 (CLI 담당)
├── __main__.py    # python -m s2n 실행 시 cli()로 연결
├── __init__.py    # import 시 core Scanner를 노출
└── core/
    ├── scanner.py     # Scanner 엔진 (플러그인 관리 + 실행)
    ├── interfaces.py  # 데이터 구조 (Finding, Report)
    └── plugins/...    # 각 취약점 검사 플러그인
```

### 4. 모듈 단위 역할 분리
- CLI 계층: cli.py (명령어 정의, 사용자 입력 처리, Scanner 실행) -> cli(), scan(), list_plugins() 필요
- 실행 계층: __main__.py (python -m s2n 실행 시 호출) -> if __name__ = "__main__" cli()
- 라이브러리 계층: __init__.py (외부 import 시 scanner 노출) -> from s2n.core.scanner import Scanner
- 코어 엔진: scanner.py (공통 스캔 로직) -> Scanner.run(), Scanner.run_to_json()
- 데이터 계층: Interfaces.py (데이터 구조 형식 통일) -> Finding, ScanReport, PluginSpec
- 플러그인 계층: /plugins/*.py

### 5. 함수 설계

#### 1️⃣ cli.py 내부
- 터미널에서 받은 옵션들을 어떻게 core Scanner으로 전달할까?
- 입력값 (url, plugin 등)을 인자로 받아서 Scanner으로 넘기면 됨.
```
#함수 초안
@cli.command()
def scan(url, plugin, output, verbose):
	scanner = Scanner(plugins=selected_plugins)
    results = scanner.run(url)
```
- 역할 분리: 입력 파싱(click), 스캐너 생성, 결과 출력 (json or stdout) 

#### 2️⃣ scanner.py 내부
- 여러 플러그인을 공통 인터페이스로 실행하려면?
- Scanner 클래스 안에서 플러그인 리스트를 순회하면서 실행해야 함.
```
# 함수 초안
class Scanner:
	def run(self, target_url):
    	for plugin in self.plugins:
        	plugin_results = plugin.scan(target_url)
```
- 결과를 Dict로 모아 CLI, import 둘 다 활용 가능하게 설계해야 함.

#### 3️⃣ interfaces.py
- 플러그인 결과들이 제각각이면 처리하기 힘듦.
- Finding, ScanReport같은 공통 데이터 구조 생성 필요.
```
# 클래스 초안
@dataclass
class Findng:
	id: str
    plugin: str
    severity: str
    title: str
    description: str
```


#### 4️⃣ __ init__.py
- 외부에서 from s2n import Scanner 했을 때 어디를 노출해야 하나?
- core/scanner.py의 Scanner만 필요함.
```
from s2n.core.scanner import Scanner
__ all__ = ["Scanner"]
```

#### 5️⃣ __main__.py
- python -m s2n 했을 때 CLI가 실행되어야 함.
```
from s2n.cli import cli
if __name__ = "__main__"
	cli()
```

### 6. 구현
bottom-up으로 구성 예정.
(1) core 레벨 먼저 작성 (scanner.py, interfaces.py)
(2) CLI 추가 (cli.py에서 click으로 명령어 래핑)
(3) 실행 진입점 설정 (__main __.py -> CLI 실행 연결)
(4) import 진입점 설정 (__init__.py)
(5) PyPI 설정 (pyproject.toml 설정)