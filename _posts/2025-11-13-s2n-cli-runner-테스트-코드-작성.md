---
layout: post
title: "[s2n] cli - runner 테스트 코드 작성"
date: 2025-11-13 05:36:49 +0900
categories: velog
series: "s2n"
---

이제 슬슬 규모가 커진다...
runner에서 모든 플러그인을 모아서 실행하고 output까지 보여줘야 하는데, 현재 plugin들에서 어마어마하게 많은 에러가 발생한다. 이 부분은 코어팀이 해결해야 할 일이라 이 부분을 제외하고, 러너 자체가 잘 돌아가는지를 테스트하는 코드를 작성해보고자 한다.
일단 이 부분만 테스트를 하기 위한 컴퓨팅 사고 정리부터.

## 1. 컴퓨팅 사고
### (1) 분해
케이스를 나눠서 테스트
- 인증 없는 기본 플로우
- DVWA 인증 있는 플로우
- Output_report에서 예외가 터진 플로우

### (2) 추상화
runner 입장에서는 함수들이 잘 호출되었는지, 어떤 인자로 호출되었는지만 관심이 있기 때문에 내부 로직까지는 필요없다. 그래서 FakeScanner, FakeDVWAAdapter, fake_output_report를 만들어서 모양만 맞는 가짜 버전으로 테스트하기로 결정함.

runner에서 하는 일의 패턴을 정리하자면:
CLI 옵션 -> CLIArguments 변환
cliargs_to_scanrequest 호출
build_scan_config 호출
인증 분기 (DVWAAdapter)
ScanContext 구성
Scanner.scan() 호출
output_report 호출

여기서 호출이 잘 되는지, 어떤 인자를 보내는지만 테스트.
즉, runner는 "오케스트레이터"이기 때문에 단위 테스트에서는 DVWA 없이, Fake로 runner의 흐름만 검증한다.


## 2. 코드 설계
전체적인 구조:
runner.scan 함수가
1. CLI 옵션을 제대로 받는가?
2. DVWA 인증 분기를 타는가?
3. Scanner와 output_report를 제대로 호출하는가?
를 차례대로 검증.

