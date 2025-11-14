---
layout: post
title: "[기타] Wazuh 완전정복: 오픈소스 SIEM + XDR 플랫폼이란?"
date: 2025-11-14 03:41:15 +0900
categories: velog
---

Wazuh는 보안 로그를 수집하고, 탐지 규칙을 적용하고, 실시간으로 알림을 받으며, 엔드포인트까지 통합적으로 관리할 수 있는 오픈소스 플랫폼이다.
EDR/XDR, SIEM 실습을 하고 싶지만 상용 솔루션은 너무 비싸 현실적으로 와주를 택하게 되었다.

## Wazuh란?
Wazuh는 오픈소스 기반 보안 관제 플랫폼으로, 두 가지 역할을 수행한다.
1. SIEM: 로그를 수집/정규화/분석하고 이상 행동을 탐지해주는 기능
2. XDR: 엔드포인트에서 실시간 보안 데이터를 수집하고, 위협 탐지/행동 기반 분석/파일 무결성 검사/취약점 점검 등을 수행하는 기능

즉 와주는 ELK 기반 SIEM + EDR 기능을 동시에 제공한다.
상용 제품 (Corelight, Splunk, Palo Alto Cortex XDR 등)의 핵심 기능을 무료로, 오픈 소스로 체험할 수 있는 매력적인 도구이다.

## Wazuh의 아키텍처
### 1) Wazuh Agent: 엔드포인트에 설치되는 경량 에이전트
- 시스템 로그 수집
- 파일 무결성 (FIM)
- 루트킷 탐지
- 취약점 스캐닝 (CVE 기반)
- 명령어 실행 모니터링 (Auditd 기반)
- 정책 위반 탐지 (OSSEC 규칙 기반)

### 2) Wazuh Manager: 중앙 분석 서버
- 에이전트로부터 전달된 로그 수집
- 규칙 기반 탐지
- Decoders를 활용해 로그 정규화
- CVE 기반 취약점 점검
- 알림 생성
- TI 연동 가능 (VirusTotal, AlienVault OTX 등)

=> 모든 분석 동작이 여기서 이뤄짐.

### 3) Wazuh Dashboard (Kibana 기반): 보안 데이터를 시각화하는 웹 인터페이스
- 실시간 경보 모니터링
- 대시보드 (host inventory, pci-dss, mitre att&ck 등)
- 엔드포인트 상세 분석
- 정책 준수 상태 확인
- 의심 활동 트렌드 확인

## Wazuh의 핵심 기능
1. SIEM
2. EDR: 엔드포인트 행동 기반 탐지
3. Vulnerability Detection
4. FIM
5. TI 연동 (OTX, VirusTotal, AbuselPDB같은 외부 위협 정보와 연동해 악성 IP/도메인 실시간 탐지)
6. 클라우드 보안 (AWS, GCP, Azure): CloudTrail로 모니터링, IAM 이벤트 분석

### 사용 시나리오
내가 DVWA 공격/nmap으로 스캔/의심스러운 명령어를 실행하면...
-> Agent가 감지
-> Manager에 로그 전송
-> 규칙과 매칭
-> Event 생성
-> 대시보드에서 실시간 확인 가능