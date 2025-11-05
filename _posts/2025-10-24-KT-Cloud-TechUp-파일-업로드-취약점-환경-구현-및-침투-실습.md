---
layout: post
title: "[KT Cloud TechUp] 파일 업로드 취약점 환경 구현 및 침투 실습"
date: 2025-10-24 08:52:10 +0900
categories: velog
series: "kt cloud techup"
---

<h2 id="part-1-python으로-웹서버에-파일-업로드하기">Part 1: Python으로 웹서버에 파일 업로드하기</h2>
<p>파일 업로드 취약점의 심각성 - 다른 취약점 10개를 합친 것보다 웹셸 취약점 1개가 더 치명적이다!
이유 - 즉시 시스템 명령어 실행 가능, 파일 시스템 완전 접근, 데이터베이스 직접 조작, 추가 악성코드 설치 가능, 네트워크 스캔 및 내부 확산</p>
<h3 id="🎯-실습-목표">🎯 실습 목표</h3>
<ul>
<li>Python으로 HTTP POST 요청을 통한 파일 업로드</li>
<li>XAMPP + PHP로 파일 업로드 서버 구축</li>
<li>다중 파일 업로드 자동화</li>
</ul>
<h3 id="🛠️-준비물">🛠️ 준비물</h3>
<ul>
<li>XAMPP (Apache + PHP)</li>
<li>Python 3.x</li>
<li>requests 라이브러리</li>
<li>테스트용 이미지 파일 (1.jpg)</li>
</ul>
<h3 id="📂-폴더-구조">📂 폴더 구조</h3>
<p>bash
코드 복사
바탕화면/kt cloud techup/코드/1027_python_file_upload/
├── 1.jpg                    # 업로드할 이미지 파일
└── file_upload.py           # Python 스크립트</p>
<p>C:\xampp\htdocs\file_upload<br/>├── upload_handler.php       # PHP 업로드 핸들러
└── uploads/                 # 업로드된 파일이 저장될 폴더 (자동생성)</p>
<h3 id="필요한-사전-지식">필요한 사전 지식</h3>
<ol>
<li>아파치란? = 웹서버 프로그램
인터넷 브라우저 ←→ 아파치 웹서버 ←→ PHP/HTML 파일들
 (요청)         (중간다리)        (실제 처리)</li>
</ol>
<ul>
<li>손님이 "짜장면 주세요" (<a href="http://localhost/file_upload/upload_handler.php">http://localhost/file_upload/upload_handler.php</a> 요청)
웨이터(아파치)가 주방으로 전달</li>
<li>주방(PHP)에서 짜장면을 만듦 (파일 업로드 처리)</li>
<li>웨이터가 손님에게 서빙 (결과 응답)</li>
</ul>
<ol start="2">
<li>htdocs 폴더란? = 웹서버의 공개 폴더
C:\xampp\htdocs\ &lt;- 이 폴더가 웹에서 접근 가능한 "루트" 폴더이다.</li>
</ol>
<p>htdocs\index.html     → <a href="http://localhost/index.html">http://localhost/index.html</a>
htdocs\test\abc.php   → <a href="http://localhost/test/abc.php">http://localhost/test/abc.php</a>
htdocs\file_upload\upload_handler.php → <a href="http://localhost/file_upload/upload_handler.php">http://localhost/file_upload/upload_handler.php</a></p>
<ul>
<li>htdocs = 상점의 진열장</li>
<li>진열장에 있는 것만 손님이 볼 수 있음</li>
<li>창고(다른 폴더)에 있는 건 손님이 못 봄</li>
</ul>
<ol start="3">
<li>실습의 흐름 정리
 (1) 웹 서버(아파치) 켜기: XAMPP -&gt; Apache Start =&gt; 나 이제 웹서버 역할 한다!라고 컴퓨터가 선언
 (2) 웹서버용 프로그램 (php) 만들기: htdocs/file_upload/upload_handler.php 생성 =&gt; 파일 받으면 저장해줄게! 라는 프로그램 작성
 (3) 클라이언트 프로그램 만들기: file_upload.py 생성 =&gt; 파일을 웹서버로 보낼게! 라는 프로그램 작성</li>
</ol>
<ul>
<li><p>Python 프로그램:
"POST <a href="http://localhost/file_upload/upload_handler.php">http://localhost/file_upload/upload_handler.php</a>
Content-Type: multipart/form-data
[파일 데이터...]"</p>
</li>
<li><p>아파치 서버:
"아, POST 요청이 왔네? 
/file_upload/upload_handler.php 파일을 실행해야겠다"</p>
</li>
<li><p>PHP 프로그램:
"POST 데이터 받았다! 파일을 저장하자!"
→ uploads 폴더에 파일 저장</p>
</li>
<li><p>아파치 서버:
"HTTP/1.1 200 OK
파일 업로드 성공: 1.jpg"</p>
</li>
<li><p>Python 프로그램:
"오케이, 성공했구나!"</p>
</li>
</ul>
<ol start="4">
<li>왜 이렇게 실습하는지?: 실제 인터넷과 똑같은 환경을 만들기 위해</li>
</ol>
<ul>
<li>실제 웹사이트 환경: 클라이언트 -&gt; 인터넷 -&gt; 네이버 서버(아파치+php) -&gt; 파일 업로드</li>
<li>실습 환경: 클라이언트(python) -&gt; 로컬네트워크 -&gt; 클라이언트(아파치+php) -&gt; 파일 업로드</li>
</ul>
<h3 id="1️⃣-xampp-설정">1️⃣ XAMPP 설정</h3>
<p>XAMPP 실행
XAMPP Control Panel 실행
Apache 서비스 시작 (Start 버튼 클릭)
상태가 초록색 "Running"으로 변경되는지 확인
기본 연결 테스트
브라우저에서 <a href="http://localhost">http://localhost</a> 접속하여 XAMPP 메인 페이지가 나오는지 확인</p>
<h3 id="2️⃣-php-업로드-핸들러-작성">2️⃣ PHP 업로드 핸들러 작성</h3>
<p>C:\xampp\htdocs\file_upload\upload_handler.php 파일 생성:</p>
<pre><code>&lt;?php
// upload_handler.php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $upload_dir = './uploads/';

    // uploads 디렉토리가 없으면 생성
    if (!file_exists($upload_dir)) {
        mkdir($upload_dir, 0777, true);
    }

    if (isset($_FILES['myfile'])) {
        $file = $_FILES['myfile'];
        $filename = $file['name'];
        $temp_path = $file['tmp_name'];
        $destination = $upload_dir . $filename;

        if (move_uploaded_file($temp_path, $destination)) {
            echo "파일 업로드 성공: " . $filename;
            echo "\n사용자: " . $_POST['user'];
            echo "\n메모: " . $_POST['note'];
        } else {
            echo "파일 업로드 실패";
        }
    } else {
        echo "파일이 전송되지 않았습니다.";
    }
} else {
    echo "POST 요청만 허용됩니다.";
}
?&gt;</code></pre><p>🔍 PHP 코드 설명
POST 요청 체크: GET 요청은 거부하고 POST만 허용
디렉토리 자동 생성: uploads 폴더가 없으면 자동으로 생성
파일 업로드 처리: 임시 파일을 최종 목적지로 이동
추가 데이터 처리: 폼에서 전송된 user, note 데이터도 함께 처리</p>
<h3 id="3️⃣-python-클라이언트-작성">3️⃣ Python 클라이언트 작성</h3>
<pre><code>import requests
# 업로드 엔드포인트 URL
url = "http://localhost/file_upload/upload_handler.php"
file_path = "./1.jpg"  # 업로드할 파일 경로

# 1.jpg 파일을 1.jpg, 2.jpg, 3.jpg... 99.jpg로 99번 업로드
for i in range(1, 100):
    with open(file_path, "rb") as f:
        # 파일 데이터 설정
        files = {"myfile": (f"{i}.jpg", f, "image/jpeg")}

        # 추가 폼 데이터
        data = {"user": "alice", "note": "test upload"}

        # POST 요청으로 파일 업로드
        resp = requests.post(url, files=files, data=data, timeout=30)
        resp.raise_for_status()  # HTTP 에러 발생시 예외 처리

        print("서버 응답:", resp.status_code, resp.text)</code></pre><p>🔍 Python 코드 설명
files 파라미터: ("필드명", (파일명, 파일객체, MIME타입)) 형식
data 파라미터: 추가 폼 데이터 (사용자 정보, 메모 등)
raise_for_status(): 4xx, 5xx 에러 발생시 예외 발생
반복 업로드: 같은 파일을 다른 이름으로 99번 업로드</p>
<h3 id="4️⃣-실습-과정에서-발생한-문제들">4️⃣ 실습 과정에서 발생한 문제들</h3>
<h4 id="문제-1-404-not-found-에러">문제 1: 404 Not Found 에러</h4>
<p>requests.exceptions.HTTPError: 404 Client Error: Not Found
원인: 파일명 오타
실제 파일: upload_hanlder.php (n이 빠짐)
코드: upload_handler.php
해결: 파일명을 올바르게 수정</p>
<h4 id="문제-2-서버-연결-확인-방법">문제 2: 서버 연결 확인 방법</h4>
<p>브라우저에서 직접 PHP 파일에 접속하면 다음 메시지가 나타남:
POST 요청만 허용됩니다.
이는 정상적인 동작입니다. (브라우저 = GET 요청, 서버 = POST만 허용)</p>
<h3 id="5️⃣-실행-및-결과-확인">5️⃣ 실행 및 결과 확인</h3>
<p>cd "C:\Users\사용자명\Desktop\kt cloud techup\코드\1027_python_file_upload"
python file_upload.py
예상 출력 결과
makefile
코드 복사
서버 응답: 200 파일 업로드 성공: 1.jpg
사용자: alice
메모: test upload
서버 응답: 200 파일 업로드 성공: 2.jpg
사용자: alice
메모: test upload
...
업로드된 파일 확인
C:\xampp\htdocs\file_upload\uploads\ 폴더에 1.jpg부터 99.jpg까지 파일이 생성됨</p>
<h3 id="6️⃣-추가-개선사항">6️⃣ 추가 개선사항</h3>
<p>에러 처리가 강화된 버전</p>
<pre><code>import requests
import os

url = "http://localhost/file_upload/upload_handler.php"
file_path = "./1.jpg"

# 파일 존재 확인
if not os.path.exists(file_path):
    print(f"에러: {file_path} 파일을 찾을 수 없습니다.")
    exit()

print(f"파일 크기: {os.path.getsize(file_path)} bytes")
print("업로드 시작...")

success_count = 0
for i in range(1, 100):
    try:
        with open(file_path, "rb") as f:
            files = {"myfile": (f"{i}.jpg", f, "image/jpeg")}
            data = {"user": "alice", "note": "test upload"}

            resp = requests.post(url, files=files, data=data, timeout=30)
            resp.raise_for_status()

            success_count += 1
            print(f"✓ {i}.jpg 업로드 성공")

    except Exception as e:
        print(f"✗ {i}.jpg 업로드 실패: {e}")

print(f"\n업로드 완료! 성공: {success_count}/99")</code></pre><h3 id="🎉-정리">🎉 정리</h3>
<p>이번 실습을 통해 배운 점:</p>
<p>Python requests로 멀티파트 파일 업로드
PHP로 파일 업로드 서버 구축
XAMPP 환경에서의 웹 개발 테스트
HTTP 상태 코드와 에러 처리
파일 경로와 네이밍 중요성</p>
<h2 id="part-2-서버에서-파일-업로드-차단하기">Part 2: 서버에서 파일 업로드 차단하기</h2>
<p>웹 서버에 파일 업로드 기능이 있다면 다음과 같은 위험이 있다:</p>
<p>🦠 악성 파일 업로드: 실행 파일, 스크립트 파일 등
💣 서버 공격: PHP, JavaScript 등을 통한 코드 실행
💾 용량 공격: 대용량 파일로 서버 용량 고갈
👤 무차별 업로드: 특정 사용자의 과도한 업로드</p>
<h3 id="📂-확장된-파일-구조">📂 확장된 파일 구조</h3>
<p>바탕화면/kt cloud techup/코드/1027_python_file_upload/
├── 1.jpg                    # 테스트용 이미지
├── file_upload.py           # 기본 업로드 클라이언트
└── test_blocking.py         # 차단 테스트 클라이언트</p>
<p>C:\xampp\htdocs\file_upload<br/>├── upload_handler.php       # 기본 업로드 서버 (차단 없음)
├── upload_handler_blocked.php  # 차단 기능이 있는 서버
└── uploads/                 # 업로드된 파일 저장소</p>
<h3 id="🚫-다층-보안-차단-시스템-구축">🚫 다층 보안 차단 시스템 구축</h3>
<p>차단 기능이 포함된 PHP 서버 작성
C:\xampp\htdocs\file_upload\upload_handler_blocked.php:</p>
<pre><code>&lt;?php
// upload_handler_blocked.php - 보안 강화 버전
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $upload_dir = './uploads/';

    if (!file_exists($upload_dir)) {
        mkdir($upload_dir, 0777, true);
    }

    if (isset($_FILES['myfile'])) {
        $file = $_FILES['myfile'];
        $filename = $file['name'];
        $user = $_POST['user'] ?? '';
        $note = $_POST['note'] ?? '';

        // ===========================================
        // 🛡️ 다층 보안 검사 시작
        // ===========================================

        // 1️⃣ 차단된 사용자 검사
        $blocked_users = ['hacker', 'malicious', 'baduser'];
        if (in_array(strtolower($user), $blocked_users)) {
            http_response_code(403);
            echo "차단된 사용자입니다: " . $user;
            exit;
        }

        // 2️⃣ 파일 확장자 검사 (화이트리스트 방식)
        $file_extension = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
        $blocked_extensions = ['exe', 'php', 'js', 'html', 'bat', 'cmd', 'sh'];

        if (in_array($file_extension, $blocked_extensions)) {
            http_response_code(403);
            echo "차단된 파일 형식입니다: ." . $file_extension;
            exit;
        }

        // 3️⃣ 파일 크기 검사 (5MB 제한)
        $max_file_size = 5 * 1024 * 1024; // 5MB
        if ($file['size'] &gt; $max_file_size) {
            http_response_code(413);
            echo "파일이 너무 큽니다: " . $file['size'] . " bytes (최대: " . $max_file_size . " bytes)";
            exit;
        }

        // 4️⃣ 파일명 특수문자 검사 (정규표현식)
        if (!preg_match('/^[a-zA-Z0-9._-]+$/', $filename)) {
            http_response_code(400);
            echo "파일명에 허용되지 않은 문자가 포함되어 있습니다: " . $filename;
            exit;
        }

        // 5️⃣ 시간대 제한 (업무시간만 허용: 9시-18시)
        $current_hour = date('H');
        if ($current_hour &lt; 9 || $current_hour &gt;= 18) {
            http_response_code(403);
            echo "업무시간 외에는 파일 업로드가 제한됩니다. (현재: " . date('H:i') . ")";
            exit;
        }

        // 6️⃣ 특정 파일명 차단 (블랙리스트)
        $blocked_filenames = ['virus.jpg', 'malware.png', 'hack.gif'];
        if (in_array(strtolower($filename), $blocked_filenames)) {
            http_response_code(403);
            echo "차단된 파일명입니다: " . $filename;
            exit;
        }

        // ===========================================
        // ✅ 모든 보안 검사 통과 - 업로드 진행
        // ===========================================

        $temp_path = $file['tmp_name'];
        $destination = $upload_dir . $filename;

        if (move_uploaded_file($temp_path, $destination)) {
            echo "파일 업로드 성공: " . $filename;
            echo "\n사용자: " . $user;
            echo "\n메모: " . $note;
            echo "\n파일 크기: " . $file['size'] . " bytes";
        } else {
            echo "파일 업로드 실패";
        }
    } else {
        echo "파일이 전송되지 않았습니다.";
    }
} else {
    echo "POST 요청만 허용됩니다.";
}
?&gt;</code></pre><h3 id="🧪-차단-기능-테스트-클라이언트">🧪 차단 기능 테스트 클라이언트</h3>
<p>악의적인 업로드 시도를 시뮬레이션하는 테스트 코드를 작성해보겠습니다:</p>
<p>test_blocking.py:</p>
<pre><code>import requests

# 차단 기능이 있는 서버 URL
url = "http://localhost/file_upload/upload_handler_blocked.php"
file_path = "./1.jpg"

# 🎭 다양한 공격 시나리오 테스트
test_cases = [
    {"filename": "normal.jpg", "user": "alice", "note": "정상 케이스"},
    {"filename": "virus.exe", "user": "alice", "note": "실행파일 업로드 시도"},
    {"filename": "backdoor.php", "user": "alice", "note": "PHP 백도어 업로드 시도"},
    {"filename": "normal.jpg", "user": "hacker", "note": "차단된 사용자의 업로드 시도"},
    {"filename": "virus.jpg", "user": "alice", "note": "의심스러운 파일명"},
    {"filename": "file@#$.jpg", "user": "alice", "note": "특수문자 파일명 공격"},
]

print("=== 🛡️ 보안 차단 시스템 테스트 ===\n")

for i, case in enumerate(test_cases, 1):
    print(f"테스트 {i}: {case['note']}")
    print(f"📁 파일명: {case['filename']}, 👤 사용자: {case['user']}")

    try:
        with open(file_path, "rb") as f:
            files = {"myfile": (case["filename"], f, "image/jpeg")}
            data = {"user": case["user"], "note": case["note"]}

            resp = requests.post(url, files=files, data=data, timeout=30)

            # 상태 코드에 따른 결과 표시
            if resp.status_code == 200:
                print("🟢 상태: 업로드 성공")
            elif resp.status_code == 403:
                print("🔴 상태: 접근 금지 (차단됨)")
            elif resp.status_code == 400:
                print("🟡 상태: 잘못된 요청")
            elif resp.status_code == 413:
                print("🟠 상태: 파일 크기 초과")

            print(f"📝 서버 응답: {resp.text}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

    print("-" * 60)</code></pre><h3 id="실제-실행-결과">실제 실행 결과</h3>
<pre><code>=== 파일 업로드 차단 테스트 ===

테스트 1: 정상 케이스
파일명: normal.jpg, 사용자: alice
상태 코드: 403
서버 응답: 업무시간 외에는 파일 업로드가 제한됩니다. (현재: 03:04)
--------------------------------------------------
테스트 2: 실행파일 차단 테스트
파일명: virus.exe, 사용자: alice
상태 코드: 403
서버 응답: 차단된 파일 형식입니다: .exe
--------------------------------------------------
테스트 3: PHP파일 차단 테스트
파일명: script.php, 사용자: alice
상태 코드: 403
서버 응답: 차단된 파일 형식입니다: .php
--------------------------------------------------
테스트 4: 차단된 사용자 테스트
파일명: normal.jpg, 사용자: hacker
상태 코드: 403
서버 응답: 차단된 사용자입니다: hacker
--------------------------------------------------
테스트 5: 차단된 파일명 테스트
파일명: virus.jpg, 사용자: alice
상태 코드: 403
서버 응답: 업무시간 외에는 파일 업로드가 제한됩니다. (현재: 03:04)
--------------------------------------------------
테스트 6: 특수문자 파일명 테스트
파일명: file@#$.jpg, 사용자: alice
상태 코드: 400
서버 응답: 파일명에 허용되지 않은 문자가 포함되어 있습니다: file@#$.jpg
--------------------------------------------------</code></pre><h3 id="차단-우선순위-분석">차단 우선순위 분석</h3>
<ol>
<li>최우선: 시간 제한<ul>
<li>테스트 1, 5에서 파일 확장자나 파일명 체크 전에 시간 조건이 먼저 적용됨</li>
</ul>
</li>
<li>사용자 차단: 테스트 4에서 hacker 사용자는 시간과 관계없이 차단됨</li>
<li>파일 확장자 차단: 테스트 2, 3에서 .exe, .php 파일은 무조건 차단</li>
<li>파일명 검증: 테스트 6에서 특수문자가 포함된 파일명은 400 에러로 처리</li>
</ol>
<h3 id="보안-수준별-비교">보안 수준별 비교</h3>
<p>테스트 항목              기본 서버       보안 서버
normal.jpg + alice    ✅ 성공    ⏰ 시간제한
virus.exe + alice    ✅ 성공    🚫 확장자 차단
script.php + alice    ✅ 성공    🚫 확장자 차단
normal.jpg + hacker    ✅ 성공    🚫 사용자 차단
virus.jpg + alice    ✅ 성공    ⏰ 시간제한
file@#$.jpg + alice    ✅ 성공    🚫 파일명 검증</p>