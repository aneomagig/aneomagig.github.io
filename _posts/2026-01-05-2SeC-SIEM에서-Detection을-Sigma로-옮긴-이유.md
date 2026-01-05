---
layout: post
title: "[2SeC] SIEM에서 Detection을 Sigma로 옮긴 이유"
date: 2026-01-05 08:03:16 +0900
categories: velog
series: "2SeC"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/84ba494e-7961-40b2-a446-15f5af34ec65/image.png"
---

## — Sigma Rule과 OpenSearch Security Analytics 완전 기초 정리

### 1. 이 글의 목적
SIEM을 만들거나 운영하다 보면 “탐지(detection)를 어디서, 어떻게 할 것인가?”라는 질문을 피할 수 없습니다. 이 글은 다음과 같은 상태의 독자를 대상으로 합니다.
- Sigma 룰이 무엇인지 전혀 모른다
- OpenSearch Dashboards의 Security Analytics가 어떤 역할을 하는지 모르겠다
- 기존 ingest / Logstash / Alerting 기반 탐지가 왜 불편한지 감이 없다
- “detection을 sigma로 옮긴다”는 말이 왜 중요한 결정인지 이해하고 싶다
- 최종적으로는 왜 탐지를 Sigma + Security Analytics로 분리하는 것이 구조적으로 옳은지를 이해하는 것이 목표입니다.

### 2. SIEM에서 말하는 “Detection”이란?
- SIEM에서 Detection은 아주 단순하게 말하면 다음 질문에 답하는 과정입니다: “지금 이 로그가 공격인가?”
- 예를 들어:
   - SQL Injection 패턴이 포함된 요청인가?
   - 로그인 URL로 비정상적인 접근이 반복되고 있는가?
   - 스캐너(User-Agent)로 의심되는 요청인가?

즉, 로그를 보고 ‘의미’를 부여하는 단계가 Detection입니다.

### 3. 전통적인 Detection 방식의 문제점
많은 SIEM 초안 구현에서는 Detection을 다음 위치 중 하나에서 처리합니다.

#### 3.1 Logstash / Ingest Pipeline에서 Detection
- 로그가 들어오는 순간 조건문(if/else)으로 탐지
- attack 필드 추가, tag 부여
- 문제점
	
    - 룰이 늘어날수록 파이프라인이 비대해짐
    - 룰 수정 = 파이프라인 수정 + 재배포
    - 정규화와 탐지가 섞여 책임이 모호해짐 

#### 3.2 Alerting(Query 기반)에서 Detection
- 특정 쿼리를 주기적으로 실행
- count, threshold로 탐지
- 문제점
	
    - 이벤트 단위 탐지에는 부적합
   - 룰을 “공유”하거나 “이식”하기 어려움
  - 탐지 로직이 특정 스택에 종속됨

### 4. 그래서 등장한 개념: Sigma Rule
#### 4.1 Sigma Rule이란?
- Sigma는 “로그 탐지를 위한 표준 룰 포맷”입니다.
- 핵심 개념은 다음 한 문장으로 요약됩니다: “탐지 로직을 특정 제품이 아닌, 공통 언어(YAML)로 정의하자”
- Sigma 룰은 보통 다음과 같은 구조를 가집니다.
	
    - 어떤 로그인가? (logsource)
    - 어떤 필드를 볼 것인가?
    - 어떤 조건이 만족되면 탐지인가?
    - 심각도(level)는 어느 정도인가?

#### 4.2 Sigma의 가장 중요한 장점
- 벤더 중립성: 특정 SIEM, 특정 쿼리에 종속되지 않음
- 가독성: YAML 기반으로 사람이 읽고 리뷰 가능
- 재사용성: 룰을 파일 단위로 관리, 공유, 버전 관리 가능
- 탐지와 파이프라인의 분리: “로그 처리”와 “공격 판단”을 명확히 분리

### 5. OpenSearch Security Analytics란?
#### 5.1 Security Analytics의 역할
OpenSearch Dashboards의 Security Analytics는 다음 역할을 담당합니다.
- Sigma Rule을 Import
- 로그와 Sigma Rule을 매칭
- 탐지 이벤트(Alert)를 생성
- Detector 단위로 룰을 묶어 운영
즉,Security Analytics = Sigma Rule 실행 엔진이라고 이해하면 됩니다.

#### 5.2 Security Analytics의 구조
Security Analytics는 크게 다음 개념들로 구성됩니다.
- Rule (Sigma Rule): “이런 로그면 공격이다”라는 정의
- Detector: 여러 룰을 묶어 실행하는 단위
- Alert: 룰이 실제 로그에 매칭된 결과

중요한 점은,
👉 로그는 이미 인덱스에 들어와 있어야 하며,
👉 Security Analytics는 “판단”만 수행한다는 점입니다.

### 6. 왜 Detection을 Sigma로 옮겼는가?
#### 6.1 역할 분리 (Single Responsibility)
- Ingest / Logstash: 정규화, 필드 정리
- Security Analytics: 공격 탐지
- Alerting	임계치/행동: 기반 탐지
이렇게 나누면 각 컴포넌트가 명확해집니다.

#### 6.2 운영 관점의 이점
- 탐지 룰 수정 시 파이프라인 재배포 불필요
- 룰 단위로 리뷰/버전 관리 가능
- 탐지 정책을 문서화하기 쉬움
- SIEM 구조가 “교육 가능한 구조”가 됨

### 7. Event-based 탐지 vs Behavior-based 탐지
#### 7.1 Sigma는 무엇을 잘하나?
- Sigma는 기본적으로 event-based 탐지에 강합니다.
- 예: 이 요청 하나가 SQLi 패턴을 포함하는가?, 이 로그의 User-Agent가 scanner인가?

#### 7.2 그럼 반복 공격은?
- 반복 로그인 실패
- 일정 시간 내 404 다수 발생

이런 behavior-based 탐지는: Security Analytics Detector 또는 OpenSearch Alerting Monitor에서 처리하는 것이 구조적으로 적절합니다.

👉 Sigma는 “판별”, Detector/Alerting은 “행동 분석”

### 8. 정리
이번 구조 변경의 핵심은 단순합니다.
### “탐지는 코드가 아니라 룰로 관리하자”

Ingest는 깨끗하게, 
Detection은 Sigma로,
Behavior는 Detector/Alerting으로

이렇게 나누는 순간, SIEM은
실험 가능한 구조, 확장 가능한 구조, 설명 가능한 구조가 됩니다.

![](/assets/images/hosooinmymind/images/hosooinmymind/post/84ba494e-7961-40b2-a446-15f5af34ec65/image.png)
