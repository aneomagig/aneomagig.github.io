---
layout: post
title: "[s2n] 스캐너 메인 엔진 scanner.py 구현하기"
date: 2025-11-06 07:40:33 +0900
categories: velog
series: "s2n"
---

### 1. 설계 개요 
목표: CLI나 라이브러리로 Scanner를 호출하면
- (선택) DVWA Adapter로 로그인/인증 수행
- (선택) httpClient를 공유 세션으로 만들어서 플러그인에 전달
- 플러그인들을 순차로 실행해 Finding들을 모아 ScanReport를 변환

이런 기능을 가진 core 엔진을 만드는 것.

### 2. 함수 설계
#### (1) `__init__(...)` - 초기화
목적: 스캐너 인스턴스 초기화, 외부 자원 (Plugin, auth_adapter, http_client, config 등) 주입
- Plugins: 선택적으로 플러그인을 직접 전달
- auth_adapter: DVWA Adapter
- http_client
- config, timeout, logger, on_finding 콜백 (! 결정 필요)

출력: 없음 (객체 상태 초기화용)
핵심 로직: 인자 저장, 내부 플러그인 리스트 초기화, 로거 준비

#### (2) discover_plugins() - 플러그인 찾기 / 로드
목적: 전달된 plugins가 있으면 그걸 쓰고, 없으면 s2n.core.s2nscanner.plugins 패키지 아래의 모듈들을 동적으로 찾아 로드해서 플러그인 인스턴스 목록을 구성함

입력: 없음 (객체 상태 사용)
출력: List[PluginSpec] (로드된 플러그인 인스턴스들)
알고리즘:
- 만약 생성자에서 plugins가 주어졌으면 그것을 인스턴스화/정규화해서 반환
- 아니면 pkgutil.iter_modules로 s2n.core.s2nscanner.plugins 내부 모듈명들을 열거.
- 각 모듈을 importlib.import_module로 import -> 모듈 안의 플러그인을 찾아 인스턴스화하거나 모듈 자체를 플러그인으로 사용
- 예외는 로거에 남기고 계속되어야 함

#### (3) _authenticate() - 인증/로그인 관리
목적: auth_adapter가 제공되면 타겟으로 로그인/토큰 획득 등을 수행해 http_client에 인증 정보가 적용되도록 함

입력: target_url
출력: 성공 여부 bool
알고리즘:
- run_target() 호출 시:
	
    - auth_adapter 있으면 auth_adapter.login() 시도
    	- 실패 시 로그 남기고 skip
    	- 성공 시 http_clinet = auth_adapter.http
    - 없으면 내부 httpclient 기본 생성
- 발견된 http_client를 플러그인에 전달
- 각 플러그인에 대해
	
    - plugin.initialize(config, http_client)
    - plugin.scan(target, http_client)
    plugin.teardown() 
    
    
#### (4) run_target(target) - 한 타겟 전체 스캔
목적: 인증된 세션을 사용해 한 타겟을 모든 플러그인으로 스캔하고 결과 수집

입력: target (스캔할 URL)
출력: List[Finding]  각 플러그인이 발견한 취약점 결과들의 리스트

알고리즘:

1. _authenicate() 호출 -> 인증 시도
	
   - 실패: 로그 남기고 스캔 중단 (return 빈 리스트)
   
   
2. 인증 성공 | 불필요 -> 유효한 http_client 확보
3. 각 플러그인 순회하며 다음 단계 수행:
	- plugin.initialize(config, http_client) 호출 -> 플러그인 내부 설정 및 세션 연결 준비
    - plugin.scan(target, http_client) 호출 -> 타겟 URL에 대한 검사 실행
    - 반환된 Finding 객체들을 findings 리스트에 추가
    - (선택) on_finding 콜백 있으면 각 Finding을 실시간 전달
    - plugin.teardown()으로 자원 정리
    
4. 모든 프러그인 실행 후 findings 반환

#### (5) run(targets) - 전체 스캔 조율
목적: 여러 타겟 리스트를 받아 run_target()을 반복 실행하고, 전체 결과를 하나의 ScanReport로 통합

입력: targets: 문자열 리스트 (사이트나 경로)
출력: ScanReport 스캔 전체 요약 

알고리즘:

1. ScanReport 객체 초기화
2. discover_plugins() 호출 -> 사용할 플러그인 목록 확보
3. targets 리스트 순회:
	- 각 타겟에 대해 run_target(target) 실행
    - 반환된 findings를 report.findings에 누적
4. 모든 타겟 실행 후 finished_at = 현재 시각 기록
5. 최종 레포트 반환
    