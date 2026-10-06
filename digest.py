#!/usr/bin/env python3
"""Fetch AI/IT headlines from a few RSS feeds and write today's digest."""
import json
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import telegram_send
import translate

FEEDS = {
    "OpenAI 블로그": "https://openai.com/news/rss.xml",
    # ponytail: Anthropic은 공식 RSS가 없어서 Google 뉴스로 anthropic.com/news를 검색해 대체(글 자체는 진짜 Anthropic 발행분)
    "Anthropic 블로그": "https://news.google.com/rss/search?q=site:anthropic.com/news&hl=en-US&gl=US&ceid=US:en",
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
    "GeekNews": "https://news.hada.io/rss/news",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "Google 뉴스(AI, 국내)": "https://news.google.com/rss/search?q=AI%20when:1d&hl=ko&gl=KR&ceid=KR:ko",
}
PER_FEED = 5
OUT_DIR = Path(__file__).parent / "digests"


def _local(tag):
    return tag.split("}")[-1]


def fetch_items(url, limit):
    """Parses both RSS 2.0 (<item>) and Atom (<entry>) feeds."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        root = ET.fromstring(resp.read())
    items = []
    for entry in root.iter():
        if _local(entry.tag) not in ("item", "entry"):
            continue
        title, link, fallback_link = "", "", ""
        for child in entry:
            local = _local(child.tag)
            if local == "title":
                title = (child.text or "").strip()
            elif local == "link":
                href = (child.get("href") or child.text or "").strip()
                if child.get("rel", "alternate") == "alternate":
                    link = href
                else:
                    fallback_link = href
        link = link or fallback_link
        if title:
            items.append((title, link))
        if len(items) >= limit:
            break
    return items


def build_digest():
    lines = [f"# {date.today().isoformat()} AI/IT 뉴스"]
    sections = []
    total = 0
    for name, url in FEEDS.items():
        lines.append(f"\n## {name}")
        items, err = None, None
        for attempt in range(2):  # ponytail: 구글 뉴스 등 간헐적 실패 완화용 1회 재시도
            try:
                items = fetch_items(url, PER_FEED)
                break
            except Exception as e:
                err = e
                time.sleep(1)
        if items is None:
            lines.append(f"(가져오기 실패: {err})")
            continue
        for title, link in items:
            lines.append(f"- [{title}]({link})")
            total += 1
        sections.append({"feed": name, "items": [{"title": t, "link": l} for t, l in items]})
    return "\n".join(lines), sections, total


def build_telegram_message(sections, total):
    today = date.today()
    # ponytail: 뉴스 한 건(제목+링크)을 문단 단위로 유지 — 텔레그램이 길면 문단 경계에서만 쪼개서 중간에 안 끊기게 함
    paragraphs = [f"{today.year}년 {today.month}월 {today.day}일 AI/IT 최신뉴스\n({total}건)"]
    for sec in sections:
        paragraphs.append(f"[{sec['feed']}]")
        for it in sec["items"]:
            paragraphs.append(f"- {translate.to_korean(it['title'])}\n  {it['link']}")
            time.sleep(0.5)
    return "\n\n".join(paragraphs)


def open_news_terminal():
    # ponytail: terminal-notifier는 이 macOS 버전에서 ad-hoc 서명 앱이라 알림 권한이 막혀서 사용 불가.
    # 클릭을 거치지 않고 다이제스트 생성 직후 바로 터미널을 열어 '뉴스'를 띄움.
    script = str(Path(__file__).parent / "open_terminal_news.sh")
    subprocess.run(["bash", script], check=False)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    text, sections, total = build_digest()
    today = date.today().isoformat()
    (OUT_DIR / f"{today}.md").write_text(text, encoding="utf-8")
    (OUT_DIR / f"{today}.json").write_text(
        json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{total}건 저장: {OUT_DIR / f'{today}.md'}")
    open_news_terminal()
    telegram_send.send_text(build_telegram_message(sections, total))


if __name__ == "__main__":
    main()
