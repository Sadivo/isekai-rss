# ヰ世界情緒 1209Carat. RSS

GitHub Actions 每 30 分鐘抓取 News / Movie / Wallpaper / Gallery / Schedule 列表頁，產生 `feed.xml`。

## 設定步驟
1. 在 GitHub 建立新的 **Public** repo（例如 `isekai-rss`），上傳本資料夾所有檔案（含 `.github/workflows/feed.yml`）。
2. repo → Settings → Actions → General → Workflow permissions 選 **Read and write permissions**。
3. Actions 頁 → `Update RSS feed` → **Run workflow** 手動跑一次，確認產生 `feed.xml`。
4. 把以下網址加入 Discord RSS 機器人：
   `https://raw.githubusercontent.com/<你的帳號>/isekai-rss/main/feed.xml`

## 注意
- 只會偵測「列表上的新項目」，內容本身仍需登入會員觀看。
- 若網站改版導致抓不到資料，Actions 會失敗並寄信通知你，舊 feed 不會被覆蓋。
- 公開 repo 若 60 天沒有任何 commit，GitHub 會暫停排程；有新內容就會 commit，通常不會發生，若被暫停到 Actions 頁按 Enable 即可。
