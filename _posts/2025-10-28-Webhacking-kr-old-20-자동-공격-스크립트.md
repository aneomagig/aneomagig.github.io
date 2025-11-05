---
layout: post
title: "[Webhacking.kr] old-20 자동 공격 스크립트"
date: 2025-10-28 01:22:31 +0900
categories: velog
series: "wargame"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/708ba2e0-7a93-4324-88b5-0e10e595173f/image.png"
---

문제 자체는 굉장히 단순하다.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/708ba2e0-7a93-4324-88b5-0e10e595173f/image.png)닉네임에 무작위, 코멘트에 무작위 값을 넣고, 캡챠 값만 html에서 따와서 복붙해서 이 모든 걸 2초 안에 제출하면 된다.
```
<form name="lv5frm" method="post">
  <input type="text" name="id" size="10" maxlength="10">
  <input type="text" name="cmt" size="50" maxlength="50">
  <input type="text" name="captcha">
  <input type="button" name="captcha_" value="8FwrScVKar" style="border:0;background:lightgreen;">
  <input type="button" value="Submit" onclick="ck()">
  <input type="reset" value="reset">
</form>
```
구조는 이와 같다.

### 1단계: JS 콘솔 접근
사실 처음에 혼자서 문제를 풀 때는 그냥 JS 스크립트를 작성해서, 페이지가 로드되자마자 개발자도구 콘솔에 2초 안에 복붙하는 피지컬(?)을 활용했다.
```
function autoSubmitWithCaptcha() {
    console.log("자동 제출 시작...");
    
    try {
        // 1. 캡챠값 읽기 (name="captcha_"인 버튼의 value)
        const captchaButton = document.querySelector('input[name="captcha_"]');
        
        if (!captchaButton) {
            console.error("캡챠 버튼을 찾을 수 없습니다!");
            return false;
        }
        
        const captchaValue = captchaButton.value;
        console.log("캡챠 값:", captchaValue);
        
        // 2. 폼 필드들에 값 입력
        const idInput = document.querySelector('input[name="id"]');
        const cmtInput = document.querySelector('input[name="cmt"]');
        const captchaInput = document.querySelector('input[name="captcha"]');
        
        if (idInput && cmtInput && captchaInput) {
            idInput.value = 'webhacking';
            cmtInput.value = 'hahahahahahaha';
            captchaInput.value = captchaValue;
            
            console.log("모든 필드 입력 완료");
            console.log(`- ID: ${idInput.value}`);
            console.log(`- Comment: ${cmtInput.value}`);
            console.log(`- Captcha: ${captchaInput.value}`);
        } else {
            console.error("일부 입력 필드를 찾을 수 없습니다!");
            return false;
        }
        
        // 3. Submit 버튼 클릭 (onclick="ck()" 함수 실행)
        const submitBtn = document.querySelector('input[value="Submit"][onclick="ck()"]');
        
        if (submitBtn) {
            console.log("Submit 버튼 클릭!");
            submitBtn.click();
            return true;
        } else {
            console.error("Submit 버튼을 찾을 수 없습니다!");
            
            // ck() 함수 직접 호출 시도
            if (typeof ck === 'function') {
                console.log("ck() 함수 직접 호출");
                ck();
                return true;
            }
            
            return false;
        }
        
    } catch (error) {
        console.error("오류 발생:", error);
        return false;
    }
}

// 실행
autoSubmitWithCaptcha();
```
이 코드를 페이지가 켜진 2초 안에 붙여넣기하면 해결이 된다.
하지만 이렇게 저능한(?) 방법으로 푸는 게 맞나 싶어서 파이썬 셀레니움으로 풀어 보았다.

### 2단계: Python Selenium 도입

```
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def fast_submit():
    driver = webdriver.Chrome()
    
    try:
        driver.get('https://webhacking.kr/challenge/code-4/')
        
        # 캡챠값 읽기
        captcha_button = driver.find_element(By.CSS_SELECTOR, 'input[name="captcha_"][type="button"]')
        captcha_value = captcha_button.get_attribute('value')
        
        # 폼 입력
        driver.find_element(By.NAME, 'id').send_keys('webhacking')
        driver.find_element(By.NAME, 'cmt').send_keys('hahahahahahaha')
        driver.find_element(By.NAME, 'captcha').send_keys(captcha_value)
        
        # 제출
        driver.find_element(By.CSS_SELECTOR, 'input[value="Submit"]').click()
        
    except Exception as e:
        print(f"에러: {e}")
    finally:
        driver.quit()
```
이렇게 실행하자 webhacking.kr에 로그인이 필요하다는 알림이 뜨는 것을 확인할 수 있었다. 

### 3단계: 로그인 문제 해결
사실 여기에서 가장 오래 걸림...
```
def login_and_solve():
    driver = webdriver.Chrome()
    
    try:
        # 로그인 페이지로 이동
        driver.get('https://webhacking.kr/login.php')
        
        username = input("아이디: ")
        password = input("비밀번호: ")
        
        driver.find_element(By.NAME, 'id').send_keys(username)
        driver.find_element(By.NAME, 'pw').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        
        # 문제 페이지로 이동
        driver.get('https://webhacking.kr/challenge/code-4/')
        # ... 문제 해결 코드
```
처음에 이렇게 vscode 터미널에서 id, pw를 입력하는 방식을 사용할려고 했는데 
```
NoSuchElementException: Unable to locate element: {"method":"css selector","selector":"[name="id"]"}
```
요런 오류가 뜨면서 입력이 되지 않았다. 페이지가 로딩되기 전에 요소를 찾으려고 해서 발생하는 오류라고 한다. 그래서 WebDriverWait을 추가했다.
```
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 요소가 나타날 때까지 대기
id_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "id"))
)
```
근데 또 TensorFlow 뭐라뭐라 하면서 콘솔 입력이 제대로 안 됨...
그래서 그냥 id/pw를 하드코딩으로 박아버렸다...;;
이번엔 진짜 될 줄 알았는데, 로그인이 /login.php가 아니라 Bootstrap 모달에서 진행되고 있었다. 내가 이렇게 기초적인 걸 확인을 안 했다니... 여기서 진짜 깊은 빡침...
```
<a class="btn btn-danger" href="#" data-bs-toggle="modal" data-bs-target="#loginModal">Login</a>

<div class="modal-dialog">
    <div class="modal-content">
        <form onsubmit="loginChk(); return false;" action="/login.php?login" method="POST">
            <!-- 로그인 폼 -->
        </form>
    </div>
</div>
```
이런 구조로 되어 있어서
```
def bootstrap_modal_login():
    driver = webdriver.Chrome()
    
    try:
        # 메인 페이지 접속
        driver.get('https://webhacking.kr/')
        
        # 로그인 버튼 클릭 (모달 열기)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-bs-target="#loginModal"]'))
        )
        login_button.click()
        
        # 모달 내 폼 입력
        id_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#loginModal input[name="id"]'))
        )
        
        id_field.send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, '#loginModal input[name="pw"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, '#loginModal input[type="submit"]').click()
```
요렇게 구조를 바꿨다.
드디어 로그인은 성공...

### 4단계: 캡챠 값 변경 문제
여기서 또 문제 발생.
캡챠값을 읽는 순간 값이 바뀌었다.

로그인 성공! 문제 해결 시작...
Captcha: 0bay4ye45A  # 이 값을 읽는 순간
제출 완료! 결과 확인 중...
실패  # 페이지의 캡챠가 이미 바뀐 상태

여기서 캡챠 버튼에 접근하는 순간 JS 이벤트가 발생해서 새로운 값이 생성되었다.
그래서 또 이 부분은 JS로 바로 복사하도록 수정했다.
```
def copy_captcha_directly():
    # JavaScript로 캡챠값을 바로 복사해서 입력
    result = driver.execute_script("""
        // 캡챠값 읽고 바로 복사
        var captchaButton = document.querySelector('input[name="captcha_"][type="button"]');
        var captchaInput = document.querySelector('input[name="captcha"]');
        var captchaValue = captchaButton.value;
        
        // 모든 필드 한번에 입력
        document.getElementsByName('id')[0].value = 'webhacking';
        document.getElementsByName('cmt')[0].value = 'hahahahahahaha';
        captchaInput.value = captchaValue;
        
        return captchaValue;
    """)
    
    # 즉시 제출
    driver.find_element(By.CSS_SELECTOR, 'input[value="Submit"]').click()
```

### 5단계. 최종 완성 코드
```
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def webhacking_old20_solver():
    """WebHacking.kr old-20 자동 해결"""
    
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    driver = webdriver.Chrome()
    
    try:
        print("=== WebHacking.kr old-20 자동 공격 ===")
        
        # 1. 로그인
        driver.get('https://webhacking.kr/')
        time.sleep(2)
        
        # Bootstrap 모달 열기
        driver.find_element(By.CSS_SELECTOR, 'a[data-bs-target="#loginModal"]').click()
        time.sleep(1)
        
        # 로그인 정보 입력
        driver.find_element(By.CSS_SELECTOR, '#loginModal input[name="id"]').send_keys(USERNAME)
        driver.find_element(By.CSS_SELECTOR, '#loginModal input[name="pw"]').send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, '#loginModal input[type="submit"]').click()
        time.sleep(3)
        
        # 2. 문제 페이지로 이동
        driver.get('https://webhacking.kr/challenge/code-4/')
        time.sleep(2)
        
        # 3. JavaScript로 초고속 처리
        driver.execute_script("""
            // 캡챠값 즉시 복사 및 모든 필드 입력
            var captchaValue = document.querySelector('input[name="captcha_"][type="button"]').value;
            document.getElementsByName('id')[0].value = 'webhacking';
            document.getElementsByName('cmt')[0].value = 'hahahahahahaha';
            document.getElementsByName('captcha')[0].value = captchaValue;
            
            // 즉시 제출
            document.querySelector('input[value="Submit"]').click();
        """)
        
        print("제출 완료! 결과 확인 중...")
        
        # 4. 결과 확인
        try:
            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
            result = alert.text
            print(f"결과: {result}")
            
            if "pwned" in result.lower():
                print("성공!")
                return True
            
            alert.accept()
            
        except:
            print("결과 팝업 확인 실패")
            return False
        
    except Exception as e:
        print(f"오류: {e}")
        return False
    finally:
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    success = webhacking_old20_solver()
    print(f"최종 결과: {'SUCCESS! ' if success else 'FAILED '}")
```

## 배운 점들
1. 동적 웹 요소 처리의 복잡성
- 단순해 보이는 폼이라도 JS 이벤트 등 복잡한 로직이 숨어있을 수 있다는 점
- 요소에 접근하는 것만으로도 값이 변경될 수 있다는 점

2. Selenium의 장단점
- 장점: 실제 브라우저 동작 완벽 묘사, js 실행 가능
- 단점: 속도 이슈, 리소스 사용량, 디버깅의 어려움

3. 문제 해결 순서의 중요성
- 로그인 -> 페이지 로딩 대기 -> 요소 접근 -> 값 처리 -> 제출 -> 결과 확인 각 단계마다 예상치 못한 문제들이 발생할 수 있다.
- 각 단계가 완료될 때마다 디버깅을 하면서 단계적으로 문제를 해결해야 한다.

4. JS + Selenium 조합의 강력함
- Python의 제어 흐름 + JS의 DOM 직접 조작으로 웹 인터랙션을 우회할 수 있다.


