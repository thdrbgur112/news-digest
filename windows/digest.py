#!/usr/bin/env python3
"""Fetch AI/IT headlines from a few RSS feeds and write today's digest. (Windows 포팅판)"""
import json
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

FEEDS = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "전자신문 IT": "http://rss.etnews.com/Section901.xml",
    "Google 뉴스(AI, 국내)": "https://news.google.com/rss/search?q=AI%20when:1d&hl=ko&gl=KR&ceid=KR:ko",
    "GeekNews": "https://news.hada.io/rss/news",
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
        try:
            items = fetch_items(url, PER_FEED)
        except Exception as e:
            lines.append(f"(가져오기 실패: {e})")
            continue
        for title, link in items:
            lines.append(f"- [{title}]({link})")
            total += 1
        sections.append({"feed": name, "items": [{"title": t, "link": l} for t, l in items]})
    return "\n".join(lines), sections, total


def _ps_escape(s):
    return s.replace("`", "``").replace('"', '`"').replace("$", "`$")


def notify(title, message):
    # ponytail: WinRT 토스트는 AUMID 미등록 앱이면 "Windows PowerShell" 이름으로 뜨는 게 한계.
    # 안 뜨는 환경이면 balloon tip으로 자동 대체(fallback)됨.
    script = f'''
try {{
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $text = $template.GetElementsByTagName("text")
    $text.Item(0).AppendChild($template.CreateTextNode("{_ps_escape(title)}")) > $null
    $text.Item(1).AppendChild($template.CreateTextNode("{_ps_escape(message)}")) > $null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("News Digest").Show($toast)
}} catch {{
    Add-Type -AssemblyName System.Windows.Forms
    $ni = New-Object System.Windows.Forms.NotifyIcon
    $ni.Icon = [System.Drawing.SystemIcons]::Information
    $ni.Visible = $true
    $ni.ShowBalloonTip(5000, "{_ps_escape(title)}", "{_ps_escape(message)}", [System.Windows.Forms.ToolTipIcon]::Info)
    Start-Sleep -Seconds 6
    $ni.Dispose()
}}
'''
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=False)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    text, sections, total = build_digest()
    today = date.today().isoformat()
    (OUT_DIR / f"{today}.md").write_text(text, encoding="utf-8")
    (OUT_DIR / f"{today}.json").write_text(
        json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{total}건 저장: {OUT_DIR / f'{today}.md'}")
    notify("오늘의 AI/IT 뉴스", f"{total}건 준비됨 — 터미널에 '뉴스' 입력")


if __name__ == "__main__":
    main()
