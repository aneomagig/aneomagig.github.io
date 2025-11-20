---
layout: post
title: "[side project] Sprint 0: EDR/APT 탐지 우회 시뮬레이션 프로젝트"
date: 2025-11-20 02:22:06 +0900
categories: velog
series: "Side Project"
---

## 개요
실무 역량을 좀 더 강화하고자 사이드 프로젝트를 진행하기로 결심했다.
첫 번째 주제로 정한 것은 EDR을 활용한 APT 공격 그룹의 TTP 모방 및 탐지 우회 시뮬레이션이다.
이 프로젝트를 통해 EDR 솔루션의 작동 원리를 제대로 이해하고, 실제 공격자의 관점에서 보안 시스템을 테스트하며 탐지 엔지니어링 (Detection Engineering) 역량을 강화하고자 한다.

-----
## 💡 프로젝트 추진 배경

최근 보한 위협은 단순한 악성코드 유포를 넘어, 특정 공격 그룹 (APT)이 장기간에 걸쳐 목표 시스템에 은밀하게 침투하고, 영구적으로 머무르는 지능적인 공격(TTP) 형태로 진화하고 있다.
EDR은 이런 공격을 엔드포인트에서 행위 기반으로 탐지하는 핵심 솔루션이지만, 공격자들은 EDR의 탐지 로직을 우회하는 방법을 계속해서 개발 중이다.
본 프로젝트는 다음과 같은 목표를 가지고 진행된다.

### 1. EDR 이해 심화
EDR이 어떤 방식으로 프로세스 행위, 파일 시스템, 레지스트리 변화를 모니터링하는지 핵심 원리를 파악한다.

### 2. 공격자 관점 확보
실제 APT 그룹의 TTP를 재현하며, 보안 시스템의 탐지 사각지대를 찾아낸다.

### 3. 대응 능력 강화
탐지 뿐만 아니라 탐지를 우회하는 공격에 대응할 수 있도록 커스텀 탐지 규칙을 설계-최적화하는 엔지니어링 역량을 확보한다.

-----
## 📚 사전 학습
### EDR/OS 내부
- EDR Hooking (User-Mode/Kernel-Mode)
- Sysmon Event ID 분석
- Process Injection/Hollowing

-> EDR이 운영체제와 상호작용하며 데이터를 수집하고 악성 행위를 탐지하는 기술적 메커니즘을 이해

### 위협 모델링
- MITRE ATT&CK TTP 분석
- APT 그룹별 TTP (Lazarus, FIN7 등)
- Attack Kill Chain

### 방어 우회 기술
- PowerShell Obfuscation 
- Fileless Malware Techniques
- Registry Run Keys Persistence

### 실습 환경
- Osquery EDR 설정
- Caldera Attack Framework 튜토리얼

---
## 🏃‍♀️ 스프린트
### Sprint 1 사전 학습 및 환경 구축
- 핵심 키워드 학습
- Windows VM 및 EDR (또는 Osquery) + 공격 도구(Caldera/Metasploit) 설치 및 기본 설정

### Sprint 2 공격 시나리오 분석 및 1차 탐지
- 특정 APT 그룹의 TTP 3~4가지 선정 및 분석
- 공격 시나리오 실행
- EDR 로그를 분석하여 탐지 여부 및 탐지 로직 파악

### Sprint 3 탐지 우회 및 규칙 개선
- 1차에서 탐지된 행위에 대해 난독화, 프로세스 조작 등 우회 기술을 적용하여 공격 재실행
- EDR 로그를 비교하여 새로운 Custom Rule을 설계하고 적용