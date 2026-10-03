"""將 ヰ世界情緒 1209Carat. 各分類列表頁轉成 RSS feed。"""
import datetime as dt
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
        if it["image"]:
            desc += f'<br/><img src="{escape(it["image"])}"/>'
        out.append("<item>")
        out.append(f"<title>{escape(it['title'])}</title>")
        out.append(f"<link>{escape(it['link'])}</link>")
        out.append(f'<guid isPermaLink="true">{escape(it["link"])}</guid>')
        out.append(f"<category>{escape(it['category'])}</category>")
        if it["date"]:
            out.append(f"<pubDate>{format_datetime(it['date'])}</pubDate>")
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
    seen, uniq = set(), []
    for it in items:
        if it["link"] not in seen:
            seen.add(it["link"]); uniq.append(it)
    epoch = dt.datetime(1970, 1, 1, tzinfo=JST)
    uniq.sort(key=lambda x: x["date"] or epoch, reverse=True)
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(build_rss(uniq))


if __name__ == "__main__":
    main()
