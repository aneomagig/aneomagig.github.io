---
layout: post
title: "[On-Race] Troubleshooting - Spring Boot 멀티 모듈 + SonarQube 테스트 커버리지 0% 및 빌드 에러 해결기"
date: 2026-04-02 07:26:19 +0900
categories: velog
series: "On-Race"
---

개발을 진행하다 보면 새로운 코드 작성만큼이나 시간과 에너지를 쏟게 되는 것이 바로 파이프라인(CI/CD)과 코드 품질 측정 도구를 연동하는 작업이다. 이번 프로젝트에서는 Spring Boot 멀티 모듈 프로젝트에 GitHub Actions와 SonarQube(SonarCloud)를 연동하는 과정에서 여러 겹의 환장할(...!) 에러들을 만났고, 이를 연쇄적으로 해결해 나가는 과정을 겪었다.

나와 같은 에러로 고통받고 있을 누군가를 위해, 꼬리에 꼬리를 무는 에러들을 어떻게 분석하고 해결했는지 상세히 기록해 본다.

## 💥 현상 (Problem)
시작은 매우 단순했다.

"분명 테스트 코드를 짰는데, PR을 올리고 나면 SonarQube 커버리지가 무조건 0%로 나와요!"

테스트가 없는 것도 아니고 분명히 존재하는데, 소나큐브 화면에서는 야속하게 0%를 가리키고 있었다. 왜 이런 일이 발생했을까?

## 🕵️‍♂️ 1차 원인: 테스트 코드 컴파일 에러와 continue-on-error의 함정
가장 먼저 의심한 것은 JaCoCo(자바 코드 커버리지 라이브러리) 리포트의 생성 여부였다. 소나큐브는 직접 테스트를 돌리는 게 아니라, JaCoCo가 만들어준 xml 포맷의 리포트를 읽어들여 렌더링할 뿐이다.

GitHub Actions 로그를 까보니... 테스트가 돌아가기는커녕 컴파일 단계에서 깨지고 있었다!


원인이 되었던 테스트 코드의 Mockito 사용 부분
```
then(ipCounter).should(never()).expire(any());
```
Mockito의 any()를 썼는데, Redisson 라이브러리의 expire() 메서드 오버로딩(Instant vs Duration) 때문에 컴파일러가 "어떤 걸 써야 할지 모르겠다"며 ambiguous method call 컴파일 에러를 뱉어낸 것이다.

그런데 왜 컴파일 에러가 났는데 Github Action은 실패하지 않고 통과(초록불)되었을까?

바로 파이프라인의 .github/workflows/sonarcloud.yml 설정 때문이었다.
```
- name: Run backend tests with coverage
        working-directory: ./backend
        run: ./gradlew :auth:test :auth:jacocoTestReport :main:test :main:jacocoTestReport --no-daemon
        continue-on-error: true # <--- 바로 이 녀석!!!
```
continue-on-error: true 옵션이 켜져 있어서, 테스트나 컴파일이 실패해도 파이프라인은 쿨하게 다음 단계인 소나큐브 스캔 스텝으로 넘어가 버린 것이다. 결론적으로, 컴파일 실패 -> 테스트 미실행 -> JaCoCo XML 리포트 미생성 -> 소나큐브: "읽을 파일이 없네? 커버리지 0%!" 로 이어진 것이었다.

### ✅ 해결 방안: 테스트 코드의 모호한 Mockito any() 호출을 any(Duration.class) 와 같이 명확한 타입으로 픽스하여 테스트 컴파일을 정상화했다.

## 🕵️‍♂️ 2차 원인: sonar.java.binaries – 소나큐브의 길 잃음 (멀티 모듈 문제)
"휴, 이제 XML 파일은 잘 생성되니 커버리지가 나오겠지?" 아니었다. 테스트가 정상 동작하고 리포트가 생성되어도 커버리지가 누락될 수 있다는 사실을 알게 되었다. 원인은 sonar-project.properties 파일에 있었다.

```
# 기존 설정
sonar.java.binaries=.
sonar.coverage.jacoco.xmlReportPaths=backend/auth/build/reports/jacoco/test/jacocoTestReport.xml, ...
```
JaCoCo 커버리지 리포트는 '소스 코드(.java)' 기준이 아니라 '컴파일된 바이트코드(.class)' 기준으로 작성된다. 소나큐브가 이를 해석하려면 우리가 등록한 소스 코드와 컴파일된 .class 파일들을 적절히 매핑(Mapping)해야 한다. 그런데 멀티 모듈 구조에서 sonar.java.binaries=. 처럼 현재 디렉토리 뭉뚱그려 지정해 버리니, 소나큐브가 바이트코드를 제대로 찾지 못해 커버리지 결과를 소스코드에 매칭하지 못했던 것이다.

### ✅ 해결 방안: 각 서브 모듈들의 정확한 빌드 아웃풋 경로들을 콤마(,)로 나열하여 명시해주었다.

```
# 변경된 설정
sonar.java.binaries=backend/auth/build/classes/java/main,backend/main/build/classes/java/main,backend/common/build/classes/java/main,backend/gateway/build/classes/java/main,backend/queue/build/classes/java/main
````

## 🕵️‍♂️ 3차 원인: Exit Code 3 - 컴파일되지 않은 서브 모듈의 반란
이제 완벽할 줄 알았다. 그런데 다시 코드를 Push 하고 Github Actions를 돌려보니, 아예 SonarScanner가 Exit Code 3을 뱉으며 뻗어버렸다!! 💣

```
java.lang.IllegalStateException: No files nor directories matching 'backend/gateway/build/classes/java/main'
...
Error: Action failed: The process '.../sonar-scanner' failed with exit code 3
```
분명 로컬 개발환경에서 Gradle 빌드를 했을 때는 gateway의 classes 폴더가 예쁘게 만들어졌는데, 왜 깃허브 액션 러너에서는 폴더가 없다고 화를 내는 걸까?

이유는 CI 파이프라인의 Task 명령어에 맹점이 있었기 때문이다.

```
# 기존 실행 명령어
run: ./gradlew :auth:test :main:test ...
```
기존 스크립트는 정확히 auth와 main 모듈의 테스트만 실행하도록 타겟팅 되어 있었다. Gradle은 정말 스마트하고 게을러서(?) 요청받은 Task와 그 의존성만 처리한다. 즉 auth, main과 상관없는 독립적인 애플리케이션 진입점인 gateway나 데이터 라우터인 queue 모듈 등은 CI 환경 내에서 자바 컴파일 자체가 아예 수행되지 않은 채로 스킵되었던 것이다.

자바 컴파일이 돌지 않았으니 build/classes/java/main 폴더는 영원히 생성되지 않았고, 아까 2번째 스텝에서 sonar.java.binaries에 우리가 "이 폴더 무조건 있으니까 참조해!"라고 굳게 약속해놨던 소나큐브는 "폴더가 물리적으로 없는데 어떻게 검사해!" 라며 스캔 스텝 자체를 드랍시켜버린 것이다.

### ✅ 최초 & 임시 원인
아까 로컬 개발환경은 문제 없었으면서, 왜 갑자기 스캐너에 잡혔을까? 이유를 파헤쳐보니, 원천 브랜치(develop)에서 변경된 Entity 이름(예: eventPackageId -> eventItemId)이 의존 모듈인 OrderHistoryService 에 반영되지 않아 컴파일이 거부(Compile Error) 당했던 이슈가 있었다. 컴파일 오류로 인해 class가 생성되지 못한 탓도 복합적으로 작용했다.

### ✅ 최종 해결 방안
파이프라인이 소나큐브에게 멱살 잡히지 않도록, 컴파일 에러를 수정한 뒤 테스트를 실행하기 전에 무조건 전체 프로젝트 모듈들의 classes 태스크를 명시적으로 돌려주는 명령어 한 단어를 파이프라인 워크플로우에 추가했다.

```
# 파이프라인 (Actions) 수정
- name: Run backend tests with coverage
  working-directory: ./backend
- run: ./gradlew :auth:test :auth:jacocoTestReport ...
+ run: ./gradlew classes :auth:test :auth:jacocoTestReport ...
```
단어 하나(classes)를 추가해 줌으로써 전체 백엔드 서브 모듈의 .class 폴더 구조가 예쁘게 생겨났고, SonarQube는 이제 모든 경로를 온전히 읽어들여 마주하던 모든 오류가 사라지고 영롱한 커버리지 초록색 뱃지를 보여주게 되었다! 🟢

## 🎉 마무리 및 회고
단순히 "커버리지가 안 잡히네?" 라는 물음표 하나에서 시작했지만, 원인은 파이프라인, 의존성 컴파일, 라이브러리 간 매칭 원리까지 거미줄처럼 얽혀 있었다.

CI 환경에서 continue-on-error를 쓸 땐 정말 주의하자. 테스트나 빌드가 에러 로그에 묻힐 수 있다.
타겟을 향해 컴파일러(Gradle)가 어떤 작업들을 연쇄적으로 수행하는지 정확히 이해하고 스크립트를 작성해야 한다.
SonarQube가 코드의 품질과 커버리지를 해석하기 위해서는 .java뿐만 아니라 최신화된 .class 바이트코드 절대경로가 정확하게 매핑되어야 한다는 사실을 깨달았다.
어렵고 답답했던 트러블슈팅이었지만 문제의 정확한 원인을 파고드는 기쁨을 느낀 삽질이었다. 끝!