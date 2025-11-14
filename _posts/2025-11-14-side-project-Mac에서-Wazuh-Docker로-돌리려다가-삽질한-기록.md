---
layout: post
title: "[side project] 🧨 Mac에서 Wazuh Docker로 돌리려다가 삽질한 기록"
date: 2025-11-14 06:34:34 +0900
categories: velog
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/07e7fab0-eeae-4f30-a1ca-e9b22a314243/image.png"
---

### 1단계. 프로젝트 디렉터리 만들기
- 이번 프로젝트에서는 mini-soc-lab 폴더 아래에 wazuh/, dvwa/, notes/ 구조로 폴더를 구성했다.
- wazuh/에는 SIEM 환경 구성을 위한 docker-compose 파일들, dvwa/ 에는 취약한 웹 애플리케이션 관련 설정을 모았다.

### 2단계. Wazuh (SIEM) 단일 노드 올리기
Docker로 Wazuh managet + indexer + dashboard 한 번에 띄우기.

(1) docker-compose.yml 파일 작성![](/assets/images/hosooinmymind/images/hosooinmymind/post/07e7fab0-eeae-4f30-a1ca-e9b22a314243/image.png)(2) docker compose 실행 ![](/assets/images/hosooinmymind/images/hosooinmymind/post/fef0bf78-5e50-4457-ae1a-1a468e739323/image.png) (3) 대시보드 접속 테스트
http://localhost:5601에 접속해도 아무것도 뜨지 않았다. 로그들을 살펴보니 Wazuh 이미지(AMD64)와 내 맥(ARM64)의 아키텍쳐가 달랐다. (어쩐지 엄청 오래 걸림...) 와저 컨테이너가 잘 뜨긴 했지만 dashboard는 ARM에서 에뮬레이션 성능 문제로 초기 부팅이 매우 오래 걸리거나 나처럼 먹통이 되는 경우가 많다고 한다. 그래서 yaml 파일 내에 platform: linux/amd64로 타입을 지정했다.

### 삽질 시작...
분명 Wazuh 공식 문서에 나온 docker-compose를 그대로 사용했음에도 불구하고 이미지 pulll 단계에서부터 말도 안 되게 오래 걸렸다. 그냥 이미지가 커서 그렇겠지 생각했는데...

#### 컨테이너가 켜졌는데 Dashboard는 안 켜지는 현상 발생
wazuh.manager Started
wazuh.indexer Started
wazuh.dashboard Started

하지만 Dashboard(5601)은 접속이 안 되고, 로그를 보니 dashboard가 indexer에 연결을 못 하고 있었다.
docker logs -f wazuh-wazuh.dashboard-1 
[ConnectionError]: connect ECONNREFUSED 172.18.0.2:9200
결과가 계속 이럼. 대시보드가 Indexer(OpenSearch)와 아예 통신이 안 되면서 아예 준비가 안 됨.

docker logs --tail 50 wazuh-wazuh.indexer-1
ERROR: no such index [.opendistro_security]
ERROR: Not yet initialized (you may need to run securityadmin)
ERROR: Failure retrieving configuration
여기서 조졌다는 걸 깨달았다. 
OpenSearch가 ARM Mac에서 제대로 안 돌아간다는 것을...
Wazuh Indexer은 x86 기반 이미지를 제공한다는 것을...
좀 더 찾아보고 프로젝트를 진행했어야 했는데 너무 성급했다. 
M1/M2에서 돌리려면 도커가 자동적으로 qemu 에뮬레이션으로 x86이미지를 돌리게 되는데, 이건 느리고 불안정하고 난리가 난다.


그래도 마지막 희망으로 메모리 제한 추가, 포트 매핑 추가, ulimits를 추가했다. 
```
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    ulimits:
      memlock:
        soft: -1
        hard: -1
```
이렇게 돌리자 compose까지 에러 나고 엉망진창.

### 결론
AWS/Linux 서버에서 실행하거나
로컬에서 UTM에 Ubuntu VM 띄우고 그 안에서 도커 실행하거나
방법을 사용해야 한다.

### 배운 점
공식 문서의 사양을 잘 읽어보자... ㅠㅠ
