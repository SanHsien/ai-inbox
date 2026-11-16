# 筆記原始資料重審 SOP

> 2026-11-16 起的常態流程。規則本身在 [`AGENTS.md`](../AGENTS.md) 第 3 節「原始資料要全部納入分析」；本文件講怎麼批次執行、怎麼收尾。

## 1. 為什麼要重審

分析不能只看貼文文字。作者上傳的圖、作者在留言區的補充、網友留言，常常會推翻或修正貼文本身。2026-11-16 首輪重審 132 篇（之後新進 3 篇已照新規則寫），抓到的錯誤類型如下：

| 錯誤類型 | 實例（筆記） | 資料出處 |
| --- | --- | --- |
| 工具認錯 | 雙語論文閱讀器其實是 PaperRead，不是 Moonlight | 作者留言給的連結 |
| 作者／出處寫錯 | Karpathy CLAUDE.md 不是 Karpathy 本人寫的；agent-desktop 作者是 Lahfir | 網友留言、作者圖卡 |
| 實測對象寫錯 | GitHub Trending 四包技能實測的是 gbrain／grill-me／gstack／awesome-agent-skills | 作者留言 |
| 定義寫錯 | 學術閱讀 CQR／KSU 的作者原版定義 | 作者圖 5、圖 7 |
| 功能狀態寫錯 | OpenCut 的 MCP／Headless 仍是規劃中 | 上游 README |
| 無出處數字 | agent-desktop「省 90% token」、「10～50ms」 | 對照實測留言 |

連帶有 8 份已完成任務的產出檔建立在錯誤前提上，已一併改正（見第 4 節）。

## 2. 狀態欄位

| `source_review` | 意思 | 其他必填 |
| --- | --- | --- |
| `full` | 文字、作者每張圖（放大看清楚）、全部留言都看過 | `source_reviewed_at`、`source_images`、`source_replies` |
| `partial` | 有留言要登入才看得到、有圖或影片沒看清楚、或原始貼文找不到而改看替代來源 | 同上，另加 `source_review_note`（讀到 N／共 M 則、哪些圖沒看） |
| `unavailable` | 來源刪除、無連結、限特定受眾 | `source_reviewed_at`、`source_review_note` |

`tools/verify_inbox.py` 會擋缺漏。正文要有「## 0. 原始資料盤點」段（格式見 `templates/article-analysis.md`）。

## 3. 每輪怎麼跑

```text
新筆記進來 / 有 partial 待補
   │
   ▼
1. python tools/verify_inbox.py → 缺 source_review 的就是待重審
   grep -l '^source_review: partial' notes/*.md → 待補讀
   │
   ▼
2. 分批派子 agent（約 12 篇一批，每人自開瀏覽器分頁）
   改 frontmatter、補第 0 段、改正事實、需要時新增任務
   已完成任務只回報、不改狀態
   │
   ▼
3. 整合者檢討回報：
   ├─ 產出檔（docs/、templates/、驗證器）被證明錯或太淺 → 直接修正
   ├─ 新增任務 → 照常派工落地
   └─ 驗證器只能改成檢查正確內容，不可放寬
   │
   ▼
4. build_index → verify_inbox → unittest 全過才提交推送；ROADMAP 同步
```

### 瀏覽器實務

- 內建瀏覽器**未登入**就讀得到 Threads、Facebook 公開貼文的文字、圖片與部分留言；用 `javascript_tool` 讀 `document.body.innerText` 與 `img` 清單。
- Threads 留言要**逐段捲動**才會載入，一次捲到底會漏讀。頁尾「相關串文」不是留言。
- 圖片導到圖片網址或用 zoom 放大看，不下載進 repo；只寫重點，不轉錄整段原文。
- X 回覆、Threads 長串留言要登入才看得全 → 標 `partial`。
- YouTube 留言在內建瀏覽器常載不出來，可用 `python -m yt_dlp --skip-download --write-comments`。
- 多個 agent 同時用瀏覽器時，每人先 `tabs_create` 開自己的分頁，不要呼叫 `resize_window`、不要用第三方鏡像站。

## 4. 首輪（2026-11-16～17）結果

- 135 篇全部完成：`full` 25、`partial` 94、`unavailable` 16。
- 新增任務：`T-20261017-35`、`T-20261018-19`、`T-20261026-35`、`T-20261026-36`、`T-20261107-06`、`T-20261108-07`、`T-20261113-01`。
- 修正的已完成任務產出：學術閱讀範本與提示詞（CQR／KSU 原版定義）、雙語論文閱讀指南（改以 PaperRead 為主角）、pstack 規格與驗證器、技能評選矩陣、agent-desktop 規格、Android 技能清單（37 個）與驗證器、TOML 規格、freelance 規格等。

## 5. partial 補讀

`partial` 不是終點。請維護者在內建瀏覽器登入 Threads／X／Facebook 一次後（帳密由維護者自己輸入），逐篇補讀留言、放大看圖，讀全了改 `full` 並更新數字與第 0 段；補讀到的新資訊照第 3 節檢討任務與產出檔。
