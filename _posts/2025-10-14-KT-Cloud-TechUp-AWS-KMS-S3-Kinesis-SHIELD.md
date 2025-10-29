---
layout: post
title: "[KT Cloud TechUp] AWS KMS / S3 / Kinesis / SHIELD"
date: 2025-10-14 02:42:21 +0900
categories: velog
---

<h2 id="kms">KMS</h2>
<ul>
<li>Key Management Service</li>
<li>개발을 하다 보면 환경변수/설정 파일에 비밀번호, API 키, DB 비밀번호 등 중요한 데이터를 넣어야 하는 경우가 있음</li>
<li>여러 명과 협업하거나 배포 실수하여 보안 관련 문제 발생하는 경우가 많음</li>
<li>대칭/비대칭키 관리</li>
<li>권한 제어</li>
<li>통합 보안: S3/RDS/Lambda와 같이 연계해서 활용</li>
<li>감사 로그: AWS CloudTrail과 통합해 키 사용 내역 추적 가능</li>
<li>키 개수별로 월 $1, 암복호화 요청 $0.03/1000건, AWS 서비스 내 통합 사용</li>
<li>AWS Managed Key: AWS 서비스들이 KMS를 통해 Key를 서비스받는 것으로 내부적으로 자동으로 일어나며 사용자의 직접적인 제어 불가</li>
<li>CMK (Customer Managed Key): 사용자가 직접 키 생성/관리</li>
<li>Custom Key Stores: CloudHSM을 활용한 키 관리<ul>
<li>CloudHSM: AWS의 하드웨어 암호화 장비를 통한 하드웨어 방식 암호화. 암호화 키 관리를 클라이언트가 해야 함</li>
</ul>
</li>
</ul>
<h2 id="s3">S3</h2>
<ul>
<li>Amazon Simple Storage Service</li>
<li>객체 스토리지 서비스</li>
<li>인터넷을 통해 데이터를 저장하고 검색할 수 있으며, 확장성/내구성/보안성이 높은 구조를 갖고 있어 웹 호스팅, 백업, 로그 저장, 빅데이터 분석 등 다양한 용도로 활용</li>
<li>간단한 html 홈페이지로도 운영 가능</li>
<li>구성 요소<ul>
<li>Bucket: 데이터를 저장하는 기본 컨테이너 (모든 리전에서 고유값 이름 필요)<ul>
<li>범용 버킷: 단순 객체 저장용. TREE 없이 단일 flat 구조. 스크립트/자동화 처리 구현이 편리하지만 flat하기 떄문에 직관적으로 보기 어렵고, 객체가 많이 쌓이면 Key 관리가 복잡해짐</li>
<li>디렉터리 버킷: 객체 key에 /를 사용해 폴더처럼 계층화. 사람 눈으로 보기 편함 (S3 콘솔에서도 폴더가 표시됨) 디렉토리 단위로 권한/정책이 부여 가능함. 하지만 객체 이동/삭제 시 전체 Key 이름 수정이 필요</li>
</ul>
</li>
<li>Object: S3에 저장되는 데이터 단위 (파일 + 메타데이터)</li>
<li>Key: 버킷 내 객체를 식별하는 고유 경로 또는 이름</li>
<li>Region: 버킷이 위치한 AWS 지역</li>
<li>Versioning: 객체의 버전을 관리하는 기능 (삭제/덮어쓰기 방지)</li>
<li>Storage Class: 데이터 접근 빈도 및 내구성에 따른 저장 클래스 (Standard/IA/Glacier)</li>
</ul>
</li>
<li>보안 기능: IAM 정책</li>
<li>서버 측 암호화 (저장 상태 암호화): SSE-S3, SSE-KMS(권장), SSE-C<ul>
<li>SSE-S3: Amazon S3 관리형 키 (무료)</li>
<li>SSE-KMS: AWS KMS를 이용한 서버 측 암호화 (유료)</li>
<li>DDSE-KMS: AWS KMS 키를 사용한 이중 계층 서버 측 암호화</li>
</ul>
</li>
<li>ACLs (Access Control Lists): 비권장, 버킷 및 객체에 대한 읽기/쓰기 접근 권한 부여 (세밀한 제어는 버킷 정책/IAM 사용 권장)</li>
<li>MFA Delete: 버전 삭제시 MFA 인증 요구</li>
</ul>
<h2 id="kinesis">Kinesis</h2>
<ul>
<li><p>스트리밍 데이터를 다루는 서비스</p>
</li>
<li><p>대량의 데이터 소스로 인해 실시간으로 연속적으로 생성되는 데이터 (로그, IoT 데이터)</p>
</li>
<li><p>Kinesis Data Streams</p>
</li>
<li><p>Kinesis Data Firehose (Amazon Data Firehose)</p>
<ul>
<li>SIEM에서 S3로 보낼때 사용</li>
<li>수집한 데이터를 저장소/분석 툴로 전송하는 서비스</li>
<li>복잡한 설정 없이 데이터 전송 가능, Serverles 서비스라서 용량 설정도 필요없음 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/2d02ae67-a455-4d2c-9f93-cd48d04e9fe9/image.png"/></li>
<li>전송된 데이터 양에 따라 요금 발생, 데이터를 다른 형태로 변환하는 경우에 요금 발생 (ex: Lambda 함수를 이용한 변환)</li>
<li>구조
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ee3a83b9-e121-40f6-a932-03f7cc6e8ced/image.png"/><ul>
<li>Input &gt; Logs</li>
<li>Transform (Lambda)
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/b6d97225-23f5-4763-9ed4-e115d739efd3/image.png"/></li>
</ul>
</li>
</ul>
</li>
<li><p>Kinesis Data Analytics (Amazon Managed Service for Apache Flink)</p>
</li>
<li><p>Kinesis Video Streams</p>
</li>
</ul>
<h2 id="shield">Shield</h2>
<ul>
<li>Shield Advanced는 월 $3000</li>
<li>Shield Standard<ul>
<li>CloudFront, ELB (Elastic Load Balancing), Route 53, Global Accelerator</li>
<li>네트워크/전송 계층(DDoS) 자동 방어, 추가 요금 없이 기본적 자동 보호 적용</li>
<li>애플리케이션 계층 (HTTP flood 등) 보호 일부 제한적
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/0b9e600d-26f2-487d-86db-40b5bf990a81/image.png"/></li>
</ul>
</li>
</ul>
