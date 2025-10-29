---
layout: post
title: "[Side Project] 🪄 Velog 글을 자동으로 GitHub Pages 블로그로 동기화하기 (with Jekyll + GitHub Actions) + Discord 알림까지 전송하기!"
date: 2025-10-29 08:15:14 +0900
categories: velog
---

<p>내가 지금까지 작성한 개발 블로그 + 포트폴리오 + 기타 내 소개를 한 곳에서 보여주고 싶어서 Jekyll 블로그를 만들어야겠다는 생각이 들었다.
그리고 Velog에 올린 글이 자동으로 내 개인 블로그(GitHub Pages)에 반영된다면 어떨까?
이번 글에서는 Velog → Jekyll → GitHub Pages 자동 배포 시스템을 만들어본 과정을 정리했다.
한 번 설정하면 이후엔 Velog에 글을 올리는 것만으로 블로그가 자동 갱신된다.</p>
<p>📌 목표 구조
Velog → (RSS 파싱)
      ↳ Python 변환 스크립트 (이미지 포함)
           ↳ GitHub Push
                ↳ GitHub Actions → Jekyll 빌드 &amp; 배포</p>
<h3 id="⚙️-1-jekyll-블로그-초기-세팅">⚙️ 1. Jekyll 블로그 초기 세팅</h3>
<p>먼저 GitHub Pages용 Jekyll 블로그를 생성했다.</p>
<pre><code>gem install jekyll bundler
jekyll new myblog
cd myblog
bundle exec jekyll serve</code></pre><p>로컬 서버(<a href="http://127.0.0.1:4000/)%EC%97%90%EC%84%9C">http://127.0.0.1:4000/)에서</a> 테마와 구성을 확인한 뒤,
aneomagig.github.io라는 GitHub 저장소를 만들어 연결했다.</p>
<pre><code>git init
git remote add origin https://github.com/aneomagig/aneomagig.github.io
git branch -M main
git push -u origin main</code></pre><h3 id="🧩-2-velog-글을-자동으로-변환하는-python-스크립트-작성">🧩 2. Velog 글을 자동으로 변환하는 Python 스크립트 작성</h3>
<p>Velog는 RSS 피드를 제공하므로,
이를 기반으로 포스트를 Markdown으로 변환하는 스크립트를 작성했다.</p>
<pre><code>import feedparser, os, re, requests
from bs4 import BeautifulSoup
from datetime import datetime

USERNAME = "hosooinmymind"
RSS_URL = f"https://v2.velog.io/rss/@{USERNAME}"
POSTS_DIR = "\_posts"
IMG_DIR = f"assets/images/{USERNAME}"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://velog.io/"}

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

feed = feedparser.parse(RSS_URL)

for entry in feed.entries:
title = entry.title.strip()
slug = re.sub(r'[^a-zA-Z0-9가-힣]+', '-', title).strip('-')
date_parsed = datetime(\*entry.published_parsed[:6])
date_filename = date_parsed.strftime("%Y-%m-%d")
date_str = date_parsed.strftime("%Y-%m-%d %H:%M:%S +0900")

    filename = f"{POSTS_DIR}/{date_filename}-{slug}.md"
    soup = BeautifulSoup(entry.description, "html.parser")

    # 이미지 로컬 저장
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if not img_url or not img_url.startswith("http"):
            continue
        rel_path = img_url.split("https://velog.velcdn.com/")[-1]
        local_path = os.path.join(IMG_DIR, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if not os.path.exists(local_path):
            r = requests.get(img_url, headers=HEADERS)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(r.content)
        img["src"] = f"/{local_path.replace(os.sep, '/')}"

    markdown = f"""---

layout: post
title: "{title}"
date: {date_str}
categories: velog

---

{str(soup)}
"""
with open(filename, "w", encoding="utf-8") as f:
f.write(markdown)</code></pre><p>이 스크립트는</p>

<ul>
<li>RSS에서 포스트 내용을 파싱</li>
<li>Velog 이미지(velcdn.com)를 로컬로 다운로드</li>
<li>Jekyll용 _posts/YYYY-MM-DD-title.md 파일로 저장
까지 자동 수행한다.</li>
</ul>
<h3 id="⚙️-3-github-actions로-완전-자동화">⚙️ 3. GitHub Actions로 완전 자동화</h3>
<p>매일 새벽에 이 스크립트가 실행되도록 GitHub Actions를 설정했다.
아래 파일을 생성한다.</p>
<p>📁 .github/workflows/velog-sync.yml</p>
<pre><code>name: 🪄 Velog → Jekyll Auto Sync

on:
schedule: - cron: '0 9 \* \* \*' # 매일 한국시간 오후 6시 실행
workflow_dispatch: # 수동 실행도 가능

jobs:
sync:
runs-on: ubuntu-latest

    steps:
      - name: 📦 Checkout repository
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: ⚙️ Install dependencies
        run: pip install feedparser requests beautifulsoup4

      - name: 🔄 Run Velog sync script
        run: python velog_to_jekyll_images_fixed.py

      - name: 🧾 Commit &amp; Push changes
        run: |
          git config user.name "Velog Sync Bot"
          git config user.email "actions@github.com"
          git add .
          git diff --quiet &amp;&amp; git diff --staged --quiet || git commit -m "🪄 Auto-sync Velog posts"
          git push

</code></pre><p>이제 매일 지정된 시간마다</p>

<ul>
<li>RSS → 포스트 변환</li>
<li>자동 커밋 &amp; push</li>
<li>GitHub Pages 자동 빌드
가 전부 클라우드에서 돌아간다.</li>
</ul>
<h3 id="🧩-이미지-깨짐-문제와-해결-과정">🧩 이미지 깨짐 문제와 해결 과정</h3>
<p>처음엔 Velog에서 가져온 글들이 Jekyll 블로그에 잘 표시되었지만, 본문에 포함된 이미지들이 전부 깨져 있었다. 브라우저 콘솔을 열어보니 경로가 이렇게 되어 있었다.
/assets/images/hosooinmymind/image.png  → 404 (Not Found)</p>
<p>이유를 분석해보니 Velog RSS에서 제공하는 <img/> 경로가 절대주소(<a href="https://velog.velcdn.com/...)%EC%9D%B8%EB%8D%B0">https://velog.velcdn.com/...)인데</a>, RSS 변환 후 단순히 Markdown만 저장하면 Jekyll이 빌드 시 이 외부 이미지를 그대로 복사하지 못하는 게 원인이었다.</p>
<h4 id="❌-잘못된-방식">❌ 잘못된 방식</h4>
<p>처음엔 단순히 <img src="/assets/images/hosooinmymind/https://v2.velog.io/rss/src"/>를 유지했지만, GitHub Pages는 velog.velcdn.com 도메인에서 이미지를 불러올 때 CORS 정책이나 HTTPS→HTTP 혼합 콘텐츠 차단으로 인해 이미지를 렌더링하지 못했다.</p>
<h4 id="✅-해결-방법-이미지-다운로드--경로-변환">✅ 해결 방법: 이미지 다운로드 &amp; 경로 변환</h4>
<p>결국 Python 스크립트에서 이미지 파일을 로컬로 다운로드한 뒤, 모든 <img/>의 src를 블로그 내부 경로로 바꾸는 방식으로 해결했다.</p>
<p>변경된 핵심 부분은 아래와 같다 👇</p>
<pre><code>for img in soup.find_all("img"):
    img_url = img.get("src")
    if not img_url or not img_url.startswith("http"):
        continue

    # Velog 이미지 도메인 기준으로 파일 경로 재구성
    rel_path = img_url.split("https://velog.velcdn.com/")[-1]
    local_path = os.path.join(IMG_DIR, rel_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # 이미지 파일 저장
    if not os.path.exists(local_path):
        r = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)

    # HTML 경로 수정
    img["src"] = f"/{local_path.replace(os.sep, '/')}"</code></pre><p>이 코드는 다음을 수행한다:

① RSS의 <img/> 태그에서 원본 src 추출 <a href="https://velog.velcdn.com/">https://velog.velcdn.com/</a>...
② 이미지 파일을 assets/images/USERNAME/ 아래에 저장 로컬 정적 파일로 변환
③ HTML 내 src 경로를 /assets/... 로 교체 Jekyll에서 로드 가능하게 변경</p>

<p>결과적으로 GitHub Pages에서도 모든 이미지가 깨지지 않고 표시되었다.
특히 requests.get()에 User-Agent 헤더를 추가한 것이 중요했다.
Velog의 CDN이 기본 요청(헤더 없는 요청)을 차단하기 때문이다.</p>
<h4 id="🧠-배운-점">🧠 배운 점</h4>
<p>단순한 RSS 크롤링만으로는 완전한 블로그 백업이 되지 않는다.
이미지 리소스를 함께 관리해야 “오프라인에서도 독립적인 블로그”가 가능하다.
Jekyll과 같은 정적 블로그는 모든 리소스가 /assets 경로에 포함되어야 함을 기억하자.</p>
<h3 id="💡-4-완성된-자동화-흐름">💡 4. 완성된 자동화 흐름</h3>
<p>🕓 매일 1회 GitHub Actions 트리거
🪄 Python 스크립트 실행 -&gt; Velog RSS 파싱 &amp; 이미지 로컬 저장
💾 _posts/ 갱신 -&gt; 새 글 자동 추가
🚀 GitHub Pages 빌드 -&gt; Jekyll 사이트 재배포 완료</p>
<h3 id="🎉-결과">🎉 결과</h3>
<p>이제 Velog에 새 글을 올리면 다음 날 자동으로 내 Jekyll 블로그에도 올라온다.
이미지도 깨지지 않고, 원문 구조 그대로 유지된다.
Velog와 GitHub Pages를 함께 운영하니 개발 기록과 개인 블로그를 하나의 생태계처럼 다룰 수 있게 되었다.</p>
<h2 id="part-2-discord-알림-설정">Part 2. Discord 알림 설정</h2>
<p>대 자동화 시대에 매일 내가 벨로그를 동기화하는 건 말이 안 된다고 생각
자동으로 하루에 한 번씩 동기화하고 디스코드 알림까지 오도록 설정했다.</p>
<h3 id="1️⃣-목표">1️⃣ 목표</h3>
<ul>
<li>Velog RSS 피드를 이용해 자동으로 포스트를 생성</li>
<li>각 글의 이미지도 함께 다운로드하여 _posts 폴더에 저장</li>
<li>GitHub Actions로 매일 자동 실행</li>
<li>마지막으로 디스코드 웹훅 알림을 보내도록 설정</li>
</ul>
<h3 id="2️⃣-velog-rss-크롤링-스크립트">2️⃣ Velog RSS 크롤링 스크립트</h3>
<p>RSS 주소 예시 👉 <a href="https://v2.velog.io/rss/hosooinmymind">https://v2.velog.io/rss/hosooinmymind</a>
이 피드를 읽어와 Jekyll용 마크다운 포스트로 변환한다.</p>
<pre><code>velog_to_jekyll_images.py
import feedparser, os, re, requests
from datetime import datetime
from bs4 import BeautifulSoup

VELG_FEED_URL = "https://v2.velog.io/rss/hosooinmymind"
SAVE_DIR = "\_posts"
IMAGE_DIR = "assets/images/hosooinmymind"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

feed = feedparser.parse(VELG_FEED_URL)
for entry in feed.entries:
title = re.sub(r'[\\/*?:"&lt;&gt;|]', '', entry.title.strip())
date = datetime(\*entry.published_parsed[:6])
filename = f"{SAVE_DIR}/{date.strftime('%Y-%m-%d')}-{title.replace(' ', '-')}.md"

    soup = BeautifulSoup(entry.description, "html.parser")
    for img in soup.find_all("img"):
        src = img["src"]
        if src.startswith("https://velog.velcdn.com"):
            img_name = src.split("/")[-2] + ".png"
            save_path = f"{IMAGE_DIR}/{img_name}"
            if not os.path.exists(save_path):
                with open(save_path, "wb") as f:
                    f.write(requests.get(src).content)
            img["src"] = f"/{save_path}"

    post = f"""---

layout: post
title: "{entry.title}"
date: {date.strftime('%Y-%m-%d %H:%M:%S')} +0900
categories: velog

---

{soup}
"""
with open(filename, "w", encoding="utf-8") as f:
f.write(post)</code></pre><h3 id="3️⃣-github-actions-자동-실행-세팅">3️⃣ GitHub Actions 자동 실행 세팅</h3>

<p>.github/workflows/velog-sync.yml
자동으로 위 스크립트를 실행하는 워크플로 파일이다.</p>
<pre><code>name: Sync Velog posts

permissions:
contents: write # ✅ 저장소에 푸시할 권한 부여

on:
workflow_dispatch:
schedule: - cron: "0 15 \* \* \*" # 매일 00시 KST 실행

jobs:
sync:
runs-on: ubuntu-latest
steps: - name: 📦 Checkout repository
uses: actions/checkout@v3

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: ⚙️ Install dependencies
        run: |
          pip install feedparser requests beautifulsoup4

      - name: 🔄 Run Velog sync script
        run: python velog_to_jekyll_images.py

      - name: 🪄 Commit &amp; Push changes
        run: |
          git config user.name "Velog Sync Bot"
          git config user.email "actions@github.com"
          git add .
          git commit -m "🪄 Auto-sync Velog posts" || echo "No changes to commit"
          git push

      - name: 🔔 Send Discord notification
        if: success()
        run: |
          curl -H "Content-Type: application/json" \
            -d '{"content": "✅ Velog 동기화 완료! 새로운 포스트가 블로그에 반영되었습니다."}' \
            ${{ secrets.DISCORD_WEBHOOK_URL }}</code></pre><h3 id="5️⃣-discord-webhook-설정">5️⃣ Discord Webhook 설정</h3>

<p>디스코드 서버에서 → 서버 설정 → 통합 → Webhook → 새 웹훅 만들기
복사한 URL을 GitHub Secrets에 추가
🔹 GitHub → Settings → Secrets → Actions → New repository secret</p>
<h3 id="6️⃣-테스트-실행">6️⃣ 테스트 실행</h3>
<p>Actions → Velog Sync → Run workflow 클릭 
모든 단계가 초록색 ✅ 이면 성공.
디스코드에는 이런 알림이 도착한다:
<img alt="" src="/assets/images/hosooinmymind/images/hosooinmymind/post/c51c6155-3418-4ed1-a67a-708c544d589d/image.png"/></p>
<h2 id="✨-마무리">✨ 마무리</h2>
<p>이제 Velog에 글을 올리면
GitHub Pages에 자동 반영되고,
매일 자정엔 새 글이 자동으로 업데이트된다.</p>
