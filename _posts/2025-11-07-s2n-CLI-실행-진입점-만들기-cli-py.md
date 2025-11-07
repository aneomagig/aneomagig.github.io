---
layout: post
title: "[s2n] CLI 실행 진입점 만들기 (cli.py)"
date: 2025-11-07 06:36:32 +0900
categories: velog
series: "s2n"
---

### 1. 문제 분해
CLI 기능을 보면 4가지 명령어로 나눠진다.
(1) scan - 실제 취약점 스캔 실행
URL 입력, 플러그인 지정, 인증 옵션, 결과 출력

(2) crawl - 사이트 링크 탐색
URL 입력, 깊이 설정, 엔드포인트 수집

(3) list-plugins - 사용 가능한 플러그인 목록 보기
등록된 모든 플러그인 이름과 설명

(4) config-show -  현재 설정 보기
config 파일 로딩 후 JSON 출력

정리하자면
cli.py ─▶ 명령어 등록 및 실행
 ├── commands.py ─▶ 실제 각 명령어 함수 정의
 ├── context.py ─▶ 공통 옵션/객체 저장 (config, logger 등)
 └── utils.py ─▶ 입력값 검증, 출력 포맷 등 보조 함수
 
 ### 2. 추상화
 CLI 프로그램을 설계할 때는 명령어 기반 인터페이스를 지원하는 라이브러리를 써야 한다.
 보통 두 가지 후보가 있는데:
 - argparse:  표준 라이브러리, 가볍고 안정적
 - click: 함수 데코레이터 기반, 코드가 깔끔하고 플러그인 구조에 어울림
 
=> s2n은 플러그인 기반 확장 구조이기 때문에 click을 사용하기로 결정.

### 3. 로직 설계

#### (1) init_cli(): CLI 프로그램의 루트 엔트리 (명령어 그룹 등록)
입력: 없음
출력: click CLI 그룹 실행 (s2n 명령 실행 시 진입)
역할: CLI 그룹 생성, 하위 명령어(scan, crawl, list-plugins, config-show) 등록
```
@click.group()
@click.option("-c", "--config", type=click.Path(), help="설정 파일 경로")
@click.option("-v", "--verbose", is_flag=True, help="상세 출력 모드")
@click.option("--log-file", type=click.Path(), help="로그 파일 경로")
@click.pass_context
def cli(ctx, config, verbose, log_file):
    """s2n Web Vulnerability Scanner CLI"""
    ctx.obj = Context(config=config, verbose=verbose, log_file=log_file)
```

#### (2) scan_command(): 스캔 실행 명령어 (핵심 기능)
입력: url, plugin, auth, username, password, output, depth
출력: Log, --output 파일 (Json or txt), 취약점 발견 시 exit code == 1
처리
- 입력값 검증
- Auth Adapter 초기화
- Scanner 실행
- 결과 저장 및 출력

#### (3) crawl_command(): 단순 링크 수집 및 엔드포인트 출력
입력: url, depth, output
출력: 표준 출력 및 파일 저장
처리: Crawler.run(url, depth) -> 링크 리스트 반환

#### (4) list_plugins_command(): 등록된 플러그인 목록 보기
입력: 없음
출력: 콘솔에 플러그인 이름 + 설명

#### (5) config_show_command(): 현재 로딩된 설정 파일 내용을 JSON으로 출력
입력: 없음
출력: json.dumps(config, indent = 2)
처리: Context의 config 객체 불러오기

