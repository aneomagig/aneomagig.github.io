---
layout: post
title: "[KT Cloud TechUp] 보안뉴스 크롤링 - requests 사용"
date: 2025-10-23 03:03:48 +0900
categories: velog
series: "kt cloud techup"
thumbnail: "/assets/images/hosooinmymind/images/hosooinmymind/post/e6cef61c-d412-4773-ab4c-7e781b8620ca/image.png"
---

지금까지는 selenium을 사용해서 크롤링을 진행했는데, 셀레니움보다 좀 더 빠른 방식인 requests를 사용하는 크롤링 실습을 진행한다.

```
def extract_title_from_html(html_content, idx):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        meta_title = soup.find('meta', attrs={'name': 'title'})
        if meta_title and meta_title.get('content'):
            title = meta_title.get('content').strip()
            title = title.replace("'", "").replace('"', '')
            if title: 
                return title
        
        if soup.title:
            title = soup.title.get_text().strip()
            if " | " in title:
                title = title.split(" | ")[0]
            elif " - " in title:
                title = title.split(" - ")[0]
            return title
        
        return f"제목 없음 - idx {idx}"
    
    except Exception as e:
        return f"제목 추출 오류 - idx {idx}: {e}"
```
제목을 추출해준다.

```
def initialize_csv_file(filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['idx', 'title'])

def save_to_csv(filename, idx, title):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([idx, title])
```
csv 초기화 및 저장 함수.

```
def crawl_boannews_articles():
    base_url = "https://www.boannews.com/media/view.asp"
    csv_filename = "boannews_articles.csv"

    initialize_csv_file(csv_filename)

    success_count = 0
    fail_count = 0

    start_idx = 139800
    end_idx = 139839
    
    print(f"크롤링을 시작합니다: idx {start_idx} 부터 idx {end_idx} 까지")
    print("-" * 50)

    for i in range(start_idx, end_idx + 1):
        try:
            params = {'idx': i, 'page': 1, 'kind': 3}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            response = requests.get(base_url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                success_count += 1
                title = extract_title_from_html(response.text, i)
                print(f"idx {i}: 성공 - {title}")
                save_to_csv(csv_filename, i, title)

            else:
                fail_count += 1
                print(f"idx {i}: 실패 - 상태 코드 {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"idx {i}: 타임아웃 발생")
            fail_count += 1

        except ConnectionError:
            print(f"idx {i}: 연결 오류 발생")
            fail_count += 1

        except requests.exceptions.RequestException as e:
            print(f"idx {i}: 요청 예외 발생 - {e}")
            fail_count += 1

        except Exception as e:
            fail_count += 1
            print(f"idx {i}: 예상치 못한 오류 - {e}")
            
        time.sleep(0.5)

        if (i - start_idx + 1) % 10 == 0:
            processed = i - start_idx + 1
            total = end_idx - start_idx + 1
            progress = (processed / total) * 100
            print(f"\n📊 진행상황: {processed}/{total} ({progress:.1f}%) - 성공: {success_count}, 실패: {fail_count}\n")
    
    print("-" * 50)
    print(f"크롤링 완료!")
    print(f"총 요청 수: {end_idx - start_idx + 1}")
    print(f"성공: {success_count}")
    print(f"실패: {fail_count}")
    if (success_count + fail_count) > 0:
        print(f"성공률: {(success_count / (success_count + fail_count)) * 100:.1f}%")
    print(f"📁 최종 결과가 '{csv_filename}'에 저장되었습니다.")
```
이렇게 제목, idx 번호를 추출해서 csv 파일에 저장하는 코드를 작성했다.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/e6cef61c-d412-4773-ab4c-7e781b8620ca/image.png)
잘 저장되는 것을 확인.
![](/assets/images/hosooinmymind/images/hosooinmymind/post/7f540dce-996b-42a3-9947-52267c6e42cc/image.png)
소요시간은 39초이다.

멀티스레딩(동시 처리)를 위해 threading을 도입할려고 한다.
```
with ThreadPoolExecutor(max_workers=5) as executor:
        # 모든 작업을 큐에 제출
        future_to_idx = {
            executor.submit(crawl_single_article, idx, csv_filename): idx 
            for idx in idx_list #40개 작업을 큐에 넣음
        }
```
작업 큐: [139800, 139801, 139802, ..., 139839] (40개)

스레드1: 139800 처리 → 완료 → 139805 가져가서 처리 → ...
스레드2: 139801 처리 → 완료 → 139806 가져가서 처리 → ...  
스레드3: 139802 처리 → 완료 → 139807 가져가서 처리 → ...
스레드4: 139803 처리 → 완료 → 139808 가져가서 처리 → ...
스레드5: 139804 처리 → 완료 → 139809 가져가서 처리 → ...
이런 식으로 작동하는 Work Stealing / Producer-Consumer 동적 할당 패턴이다.

단일 스레드 (기존 코드)
for i in range(40):
    requests.get(...)  # 40번의 순차적 I/O 대기
    // CPU 사용률: 5%, 대부분 BLOCKED

멀티 스레드 (현재 코드)  
ThreadPoolExecutor(max_workers=5):
    5개 스레드가 동시에 requests.get()
    // CPU 사용률: 20-30%, 컨텍스트 스위칭 증가
    // 스케줄러 부하: 증가하지만 전체 성능 향상

![](/assets/images/hosooinmymind/images/hosooinmymind/post/6c8f8f06-a1e0-47cf-8f54-8459f17ea4ec/image.png)
스레딩을 도입하자 소요시간이 6.5초로 엄청나게 줄어들었다.

여기까지는 수업에서 진행한 내용이다. 하지만 기사를 스크랩하는데 제목만으로 파악할 수 있는 내용에는 한계가 있다고 생각되어서, 크롤링 하는 김에 내용까지 긁어서 llm에 집어넣은 뒤 요약해서 csv에 같이 붙여주면 좋겠다는 생각이 들었다. 이걸 매일 업데이트되는 뉴스를 모아서 팀원들에게 디스코드로 보내주면 좋겠다는 생각이 들었지만, 현실적으로 openai api 비용을 감당하기 힘들 것 같아서 일단 테스트용으로만 만들어 보기로 했다.