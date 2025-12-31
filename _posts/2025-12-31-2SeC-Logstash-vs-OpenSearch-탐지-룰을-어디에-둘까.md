---
layout: post
title: "[2SeC] Logstash vs OpenSearch - 탐지 룰을 어디에 둘까?"
date: 2025-12-31 01:08:37 +0900
categories: velog
series: "2SeC"
---

## 1. 현재 우리 파이프라인 구조
```
[ Cloud / App Logs ]
        ↓
   CloudWatch Logs
        ↓
      Kinesis
        ↓
     Logstash
        ↓
   OpenSearch
        ↓
   Dashboard / Search
```
- Kinesis: 로그 스트리밍 버퍼
- Logstash: 로그 파싱, 정규화, 1차 필터링
- OpenSearch: 저장, 검색, 시각화, 분석

## 2. 탐지 룰에 대한 의견들
- 어차피 OpenSearch는 로그 받는 데 돈이 안 듦. Splunk처럼 ingestion 과금이 있는 것도 아니니 logstash에서 굳이 거르지 말고 통째로 던지고 OpenSearch에서 탐지 룰을 적용하면 되지 않나?
- Logstash에서 한 번 거르고 OpenSearch에서는 좀 더 고레벨의 행위기반탐지를 하는 게 맞지 않나? 통째로 던지기에는 용량적으로도 그렇고 탐지하기도 빡셀 것 같다.

## 3. 핵심 포인트들
(1) OpenSearch는 로그 받아도 돈 안 든다?
- Splunk는 로그 수집량 기준 과금. 그래서 사전에 최대한 줄여야 함 -> Logstash / Forwarder에서 필터링 필수
- OpenSearch는 클러스터 인스턴스 시간 기반 과금. 로그가 얼마나 되든 노드가 떠 있으면 비용은 동일함.

(2) LogStash / OpenSearch 역할 차이
- Logstash의 본질적 역할: 로그 정규화, 구조화, 스트림 단계에서의 판단, lightweight rule / pattern matching => 로그가 시스템에 들어오기 전에 성격을 정리하는 곳
- OpenSearch의 본질적 역할: 로그 저장소, 검색/집계/상관분석, 대시보드, 사후분석, 행위 기반 분석 => 이미 쌓인 로그를 기반으로 관계를 보는 곳

## 4. SIEM에서 쓰이는 구조는?
보통 2단계로 나눔.
(1) Ingest-time Detection: Logstash 담당
- 명백한 공격 패턴
- 룰 기반
- 빠르고 가벼움
- 예: SQLi, XSS, Path Traversal, Scanner User-Agent, 비정상 HTTP Method

(2) Post-index Detection: OpenSearch 담당
- 시간/행위 기반
- 집계 필요
- 상태 변화 추적
- 예: 5분 내 로그인 실패 20회, 특정 IP의 URL 다양성 급증, 평소 없던 API 호출 패턴 등

## 5. Logstash에서 로그를 통채로 던지면 안 되는 이유?
(1) 로그 품질 문제: 파싱 실패 로그도 그대로 저장, 필드 불균일, 탐지 룰 작성 난이도 급상승
(2) OpenSearch 쿼리 비용 증가: 불필요한 로그까지 인덱싱, 쿼리 복잡도 상승, 대시보드 성능 저하
(3) SIEM 사고 흐름이 깨짐: “이 이벤트는 왜 들어왔는지” 설명 불가, 탐지 책임 위치가 모호해짐