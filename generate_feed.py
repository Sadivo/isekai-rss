"""將 ヰ世界情緒 1209Carat. 各分類列表頁轉成 RSS feed。"""
import datetime as dt
import json
import os
import sys
from email.utils import format_datetime
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup

BASE = "https://isekaijoucho.kamitsubaki.jp"
SECTIONS = {  # 路徑: 分類名稱
    "/contents/news": "News",
    "/movies/categories/movie": "Movie",
    "/group/wallpaper": "Wallpaper",
    "/group/gallery": "Gallery",
    "/contents/schedule": "Schedule",
}
JST = dt.timezone(dt.timedelta(hours=9))
STATE_FILE = "seen.json"
UA = "Mozilla/5.0 (personal RSS feed; checks every 30 min)"


def scrape(path, label, html=None):
    if html is None:
        r = requests.get(BASE + path, headers={"User-Agent": UA}, timeout=30)
        r.raise_for_status()
        html = r.text
    soup = BeautifulSoup(html, "lxml")
    items = []
    for li in soup.select("li.thumb-list-item, li.contents-list-item"):
        a = li.find("a", href=True)
        t = li.find("time")
        title_el = li.select_one("h3")
        if not (a and title_el):
            continue
        link = BASE + a["href"].split("?")[0]
        date = None
        if t and t.get("datetime"):
            try:
                date = dt.datetime.fromisoformat(t["datetime"][:10]).replace(tzinfo=JST)
            except ValueError:
                pass
        tags = [s.get_text(strip=True) for s in li.select(".tag")]
        img = li.select_one("[data-bg]")
        items.append({
            "title": f"[{label}] " + title_el.get_text(" ", strip=True),
            "link": link,
            "date": date,
            "category": label,
            "tags": tags,
            "image": img["data-bg"] if img else None,
        })
    return items


def build_rss(items):
    now = format_datetime(dt.datetime.now(dt.timezone.utc))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0"><channel>',
           "<title>ヰ世界情緒 1209Carat. 更新</title>",
           f"<link>{BASE}/</link>",
           "<description>非官方：由列表頁自動產生的更新通知</description>",
           f"<lastBuildDate>{now}</lastBuildDate>"]
    for it in items:
        desc = "、".join([it["category"]] + it["tags"])
        if it["date"]:
            desc += f"（頁面日期 {it['date']:%Y-%m-%d}）"
        if it["image"]:
            desc += f'<br/><img src="{escape(it["image"])}"/>'
        out.append("<item>")
        out.append(f"<title>{escape(it['title'])}</title>")
        out.append(f"<link>{escape(it['link'])}</link>")
        out.append(f'<guid isPermaLink="true">{escape(it["link"])}</guid>')
        out.append(f"<category>{escape(it['category'])}</category>")
        out.append(f"<pubDate>{format_datetime(it['seen'])}</pubDate>")
        if it["image"]:
            out.append(f'<enclosure url="{escape(it["image"])}" type="image/jpeg" length="0"/>')
        out.append(f"<description>{escape(desc)}</description>")
        out.append("</item>")
    out.append("</channel></rss>")
    return "\n".join(out)


def main():
    items, errors = [], 0
    for path, label in SECTIONS.items():
        try:
            got = scrape(path, label)
            print(f"{label}: {len(got)} items")
            items += got
        except Exception as e:  # 單一分類失敗不影響其他分類
            errors += 1
            print(f"{label}: ERROR {e}", file=sys.stderr)
    if not items:
        sys.exit("沒有抓到任何項目，保留舊的 feed.xml")
    # pubDate 用「首次偵測到的時間」，避免 Schedule 的未來活動日期讓 RSS 機器人誤判
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    first_run = not state
    uniq, links = [], set()
    for it in items:
        if it["link"] in links:
            continue
        links.add(it["link"])
        if it["link"] not in state:
            first = now
            if first_run and it["date"]:  # 首次執行：沿用頁面日期（不超過現在）
                first = min(it["date"], now)
            state[it["link"]] = first.isoformat()
        it["seen"] = dt.datetime.fromisoformat(state[it["link"]])
        uniq.append(it)
    uniq.sort(key=lambda x: x["seen"], reverse=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(build_rss(uniq))


if __name__ == "__main__":
    main()
