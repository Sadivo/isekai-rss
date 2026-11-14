"""MEE6 診斷用測試 feed：每小時自動新增一筆，用來快速確認 MEE6 會不會推送。

產生兩個 feed（測完後把 workflow 裡的這一步刪掉即可停用）：
  test-a.xml  最單純的格式：英文標題、連結指向自己的 GitHub Pages
  test-b.xml  與正式 feed 相同的寫法：日文標題、連結指向 isekaijoucho、含圖片
"""
import datetime as dt
import json
import os
from email.utils import format_datetime
from xml.sax.saxutils import escape

PAGES = "https://sadivo.github.io/isekai-rss"
SITE = "https://isekaijoucho.kamitsubaki.jp"
STATE = "test_state.json"
KEEP = 10
IMG = SITE + "/assets/isekaijoucho/app/ogp.jpg"


def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    return []


def feed_a(items, now):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', "<channel>",
           "<title>MEE6 test feed A</title>",
           f"<link>{PAGES}/test.html</link>",
           "<description>Hourly test items (plain format)</description>",
           f"<pubDate>{items[0]['rfc']}</pubDate>",
           f"<lastBuildDate>{now}</lastBuildDate>",
           f'<atom:link href="{PAGES}/test-a.xml" rel="self" type="application/rss+xml" />']
    for it in items:
        link = f"{PAGES}/test.html?t={it['id']}"
        out += ["<item>",
                f"<title>Test A {it['id']}</title>",
                f"<link>{link}</link>",
                f'<guid isPermaLink="true">{link}</guid>',
                f"<pubDate>{it['rfc']}</pubDate>",
                f"<description>Test item created at {it['rfc']}</description>",
                "</item>"]
    return "\n".join(out + ["</channel></rss>"])


def feed_b(items, now):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" '
           'xmlns:atom="http://www.w3.org/2005/Atom" '
           'xmlns:dc="http://purl.org/dc/elements/1.1/">', "<channel>",
           "<title>ヰ世界情緒 1209Carat. テスト B</title>",
           "<description>非官方：測試用（與正式 feed 相同格式）</description>",
           f"<pubDate>{items[0]['rfc']}</pubDate>",
           f"<lastBuildDate>{now}</lastBuildDate>",
           f"<link>{SITE}/</link>",
           f'<atom:link href="{PAGES}/test-b.xml" rel="self" type="application/rss+xml" />']
    for it in items:
        link = f"{SITE}/contents/news?t={it['id']}"
        out += ["<item>",
                f'<guid isPermaLink="false">{link}</guid>',
                f"<title>[Movie] ヰ世界テスト {it['id']}</title>",
                f"<link>{link}</link>",
                f'<description><![CDATA[Movie（テスト {it["id"]}）<br><img src="{IMG}" />]]></description>',
                "<dc:creator>ヰ世界情緒</dc:creator>",
                "<category>Movie</category>",
                f"<pubDate>{it['rfc']}</pubDate>",
                f'<media:content url="{IMG}" medium="image" />',
                "</item>"]
    return "\n".join(out + ["</channel></rss>"])


def main():
    now_dt = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    hour_id = now_dt.strftime("%Y%m%d%H")
    state = load_state()
    if not any(s["id"] == hour_id for s in state):
        state.insert(0, {"id": hour_id, "rfc": format_datetime(now_dt)})
    state = state[:KEEP]
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1)
    now = format_datetime(now_dt)
    for name, fn in (("test-a.xml", feed_a), ("test-b.xml", feed_b)):
        with open(name, "w", encoding="utf-8") as f:
            f.write(fn(state, now))
    with open("test.html", "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset='utf-8'><title>MEE6 test feed</title>"
                "<p>MEE6 RSS test page. Latest item: " + escape(state[0]["id"]) + "</p>")
    print(f"test feeds: {len(state)} items, newest {state[0]['id']}")


if __name__ == "__main__":
    main()
