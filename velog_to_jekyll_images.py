import feedparser, json, os, re, requests
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

USERNAME = "hosooinmymind"
RSS_URL = f"https://v2.velog.io/rss/@{USERNAME}"
POSTS_DIR = "_posts"
IMG_DIR = f"assets/images/{USERNAME}"
SITE_BASE_URL = "https://aneomagig.github.io"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://velog.io/",
    "Origin": "https://velog.io"
}

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

feed = feedparser.parse(RSS_URL)
entries = sorted(feed.entries, key=lambda e: datetime(*e.published_parsed[:6]), reverse=True)

updated_posts = []

for entry in entries:
    title = entry.title.strip()
    slug = re.sub(r'[^a-zA-Z0-9가-힣]+', '-', title).strip('-')
    date_parsed = datetime(*entry.published_parsed[:6])
    date_str = date_parsed.strftime("%Y-%m-%d %H:%M:%S +0900")
    date_filename = date_parsed.strftime("%Y-%m-%d")
    filename = f"{POSTS_DIR}/{date_filename}-{slug}.md"
    file_path = Path(filename)

    # RSS 본문 (썸네일 + 내용 일부)
    soup = BeautifulSoup(entry.description, "html.parser")

    # 🎯 1️⃣ HTML 페이지 요청 (시리즈, 태그 가져오기)
    html_url = entry.link
    html_res = requests.get(html_url, headers=HEADERS)
    html_soup = BeautifulSoup(html_res.text, "html.parser")

    # 🔹 시리즈명 추출
    series_tag = html_soup.find("a", href=lambda x: x and "/series/" in x)
    series_name = series_tag.text.strip() if series_tag else None

    # 🔹 태그 추출
    tag_elements = html_soup.select("a.tag-item") or []
    tags = [t.text.strip().replace("#", "") for t in tag_elements]

    # 🔹 본문 내용 (RSS 요약 대신 전체 HTML)
    content_div = html_soup.select_one("div.velog__post-content")
    if content_div:
        soup = content_div

    # 🎯 2️⃣ 이미지 로컬 저장 (경로 구조 유지)
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
                print(f"📸 Saved {rel_path}")
            else:
                print(f"⚠️ Failed ({r.status_code}): {img_url}")

        img["src"] = f"/{local_path.replace(os.sep, '/')}"

    # 🎯 3️⃣ Markdown 파일 생성 (시리즈 + 태그 포함)
    front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: velog
"""

    if series_name:
        front_matter += f'series: "{series_name}"\n'

    if tags:
        front_matter += "tags:\n"
        for t in tags:
            front_matter += f"  - {t}\n"

    front_matter += "---\n\n"

    markdown = front_matter + str(soup)

    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as existing_file:
            if existing_file.read() == markdown:
                print(f"⏭️ Skipped unchanged post: {filename}")
                continue

    with file_path.open("w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Saved post: {filename} ({series_name or 'No series'})")

    post_info = {
        "title": title,
        "slug": slug,
        "date": date_parsed.isoformat(),
        "filename": str(file_path),
        "velog_url": entry.link,
        "site_url": f"{SITE_BASE_URL}/velog/{date_parsed.strftime('%Y/%m/%d')}/{slug}.html"
    }
    updated_posts.append(post_info)

latest_info_path = Path("latest_post.json")
if updated_posts:
    updated_posts.sort(key=lambda p: p["date"], reverse=True)
    with latest_info_path.open("w", encoding="utf-8") as f:
        json.dump(updated_posts[0], f, ensure_ascii=False, indent=2)
    print(f"🆕 Latest synced post: {updated_posts[0]['title']}")
elif latest_info_path.exists():
    latest_info_path.unlink()

print("🎉 모든 포스트 RSS + HTML 병행 크롤링 완료!")
