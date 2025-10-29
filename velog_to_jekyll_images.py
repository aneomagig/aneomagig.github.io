import feedparser, os, re, requests
from datetime import datetime
from bs4 import BeautifulSoup

USERNAME = "hosooinmymind"
RSS_URL = f"https://v2.velog.io/rss/@{USERNAME}"
POSTS_DIR = "_posts"
IMG_DIR = f"assets/images/{USERNAME}"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://velog.io/",
    "Origin": "https://velog.io"
}

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

feed = feedparser.parse(RSS_URL)

for entry in feed.entries:
    title = entry.title.strip()
    slug = re.sub(r'[^a-zA-Z0-9가-힣]+', '-', title).strip('-')
    date_parsed = datetime(*entry.published_parsed[:6])
    date_str = date_parsed.strftime("%Y-%m-%d %H:%M:%S +0900")
    date_filename = date_parsed.strftime("%Y-%m-%d")
    filename = f"{POSTS_DIR}/{date_filename}-{slug}.md"

    soup = BeautifulSoup(entry.description, "html.parser")

    for img in soup.find_all("img"):
        img_url = img.get("src")
        if not img_url or not img_url.startswith("http"):
            continue

        # 🔥 전체 경로 구조 보존
        rel_path = img_url.split("https://velog.velcdn.com/")[-1]
        local_path = os.path.join(IMG_DIR, rel_path)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if not os.path.exists(local_path):
            r = requests.get(img_url, headers=HEADERS)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(r.content)
                print(f"📸 Saved {rel_path}")
            else:
                print(f"⚠️ Failed ({r.status_code}): {img_url}")

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
        f.write(markdown)

print("✅ 모든 이미지 경로 구조 보존 완료!")
