---
layout: post
title: "[s2n] devlog - CLI 입력 데이터 구조 리팩토링 (CLIArguments -> ScanRequest)"
date: 2025-11-10 03:27:34 +0900
categories: velog
series: "s2n"
---

### 1. 개요
cli.py에서 개별적으로 처리되고 있는 CLI 옵션들을 공통 인터페이스 계층의 타입 구조를 활용해 통합된 입력 데이터 플로우로 정리한다.
- 기존: click -> dict -> Scanner
- 변경: click -> CLIArguments -> ScanRequest -> ScanConfig -> Scanner

이를 통해 CLI, python import, rest api 호출이 모두 동일한 입력 타입 체계를 사용하게 된다.

### 2. 배경 및 문제점
현재 cli.py는 Click의 옵션 인자를 바로 함수 내부에서 처리하고 있다.
이 구조는 직관적이지만, CLI 실행 외의 환경(Python SDK, REST API, 테스트 코드 등)에서는 재사용이 어렵다.

### 3. 개선 방향
```
click options
    ↓
CLIArguments
    ↓ (검증/변환)
ScanRequest
    ↓ (구성 단계)
ScanConfig
    ↓
Scanner 실행
```

- CLIArguments: CLI에서 입력받은 인자를 구조화
- ScanRequest: 인자를 표준 스캔 요청으로 변환
- ScanConfig: 실제 Scanner 엔진 실행 설정
- Scanner: 스캔 실행, 플러그인 호출

### 4. 변환 로직 설계
#### (1) CLIArguments -> ScanRequest 변환
 core/s2nscanner/cli/mapper.py 생성
 
 #### (2) ScanRequest -> ScanConfig 변환
 core/s2nscanner/cli/config_builder.py 생성

#### (3) CLI 통합 예시
cli.py의 scan 명령은 아래와 같이 단순화될 것이다.
```
@cli.command("scan")
@click.option("-u", "--url", required=True)
@click.option("-p", "--plugin", multiple=True)
@click.option("-a", "--auth")
@click.option("--username")
@click.option("--password")
@click.option("-o", "--output")
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def scan(ctx, url, plugin, auth, username, password, output, verbose):
    from s2n.s2nscanner.cli.mapper import cliargs_to_scanrequest
    from s2n.s2nscanner.cli.config_builder import build_scan_config

    # 1️⃣ CLIArguments 생성
    args = CLIArguments(
        url=url,
        plugin=list(plugin),
        auth=auth,
        username=username,
        password=password,
        output=output,
        verbose=verbose
    )

    # 2️⃣ ScanRequest 변환
    request = cliargs_to_scanrequest(args)

    # 3️⃣ ScanConfig 생성
    config = build_scan_config(request)

    # 4️⃣ 스캐너 실행
    scanner = Scanner(config=config, logger=ctx.obj["logger"])
    report = scanner.scan()

    # 5️⃣ 결과 출력
    print(f"총 발견된 취약점: {len(report.summary.severity_counts)}개")
 ```

