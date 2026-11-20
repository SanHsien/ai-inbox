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

登入補讀時另外要注意（2026-11-17 補，都是補讀時實際遇到的）：

- **瀏覽器面板隱藏時，Threads 只載入前十則**。開始讀之前先用 `tabs_select` 把自己的分頁叫到前面，再捲動。
- **Threads 的「最新」排序與 Facebook 的留言框，要用 `computer` 的 `scroll` 送真的滾輪事件**。用 JavaScript 改捲動位置會卡住，不會載入後面的留言。
- Threads 可以直接在貼文網址後面加 `?sort_order=recent&filter_type=all` 切到最新排序、顯示全部回覆，不必點選單。
- Threads 的留言列表是**虛擬捲動**：捲過去的項目會從頁面上移除。要**邊捲邊收**，每捲一段就把目前畫面上的留言記下來（以作者加開頭文字去重複），不要等捲到底才一次讀 `innerText`，那樣只拿得到最後一屏。

找回原貼文、Facebook／Instagram 留言與影片截圖（2026-11-18 補，都是補讀時實際遇到的）：

- **原貼文沒留連結時，先查 Facebook 再查 Threads**。這批沒留連結的筆記，原文多半在 Facebook 社團或粉絲專頁。先開 `https://www.facebook.com/search/posts?q=<關鍵字>`（關鍵字用 repo 名、工具名或貼文裡的特殊用語），找不到再到 Threads 站內搜尋。
- **Facebook 搜尋結果的永久連結要點時間戳才拿得到**。時間戳的連結在頁面文字裡讀不到網址，要先用 `find` 找到時間戳取得 `ref`，再用 `computer` 點那個 `ref`，進到貼文頁後抄網址列。
- **Facebook 留言的順序：重新載入 → 切排序 → 先截圖 → 真滾輪**。先展開回覆再捲動會卡住、後面的留言載不出來；所以進頁面先重新載入，把排序切到「所有留言」或「由新到舊」，截一張圖確認留言框有出現，再用 `computer` 的 `scroll` 送滾輪事件捲到底，最後才逐一展開「查看回覆」。
- **Instagram 輪播與 Reel 的留言開 `/p/<id>/` 直接頁**，不要在動態牆的彈出視窗裡讀。面板沒有顯示時 Instagram 不會續載留言，開始前先 `tabs_select`。
- **GitHub README 的影片可以跳秒截圖**：開 `https://github.com/user-attachments/assets/<id>#t=<秒>`（`<id>` 從 README 原始檔取得），每個要看的秒數各開一次、各截一張，不必下載影片。
- **面板停止繪製時，每次截圖前先 `tabs_select`，一次只截一張**。截到全黑或舊畫面多半是分頁被切到背景；把 `tabs_select` 與截圖放在同一批呼叫裡，不要連續截好幾張。

原貼文搜尋不到時，找轉引與存檔（2026-11-18 補，都是實際查過的）：

- **清單型貼文用最冷門的項目名兩兩組合搜 Threads**。搜熱門專案名只會撈到大量單獨介紹；這次是「typesafe skills」「Hermes Jev」命中原貼文。
- **X 站內搜尋不要用帶斜線的 repo 名**（`android/skills` 會被拆字），改用加引號的產品名，配 `since:`／`until:` 日期區間與 `lang:zh`。
- **Wayback 先拿一個一定有存檔的網址當對照**。CDX 介面有時對任何網址都回空白，不等於沒存檔；availability API（`https://archive.org/wayback/available?url=`）與 archive.ph 的 `/newest/<網址>` 比較可靠。X 貼文要查 `twitter.com/...` 網址，`x.com/...` 常查不到。
- **GitHub repo 404 時先查 ecosyste.ms**：`https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/<owner>%2F<repo>`（描述、建立日、標籤、相依清單）與 `https://timeline.ecosyste.ms/api/v1/events/<owner>/<repo>`；再查 Software Heritage 與同名 fork。
- **原稿對不上現行 README 時，取分析當天的版本比對**：`gh api "repos/<owner>/<repo>/commits?path=README.md&until=<分析日>T23:59:59Z"` 取 commit，再讀那一版的 README。Strata 的原稿內容就是出自當天的 README。
- **GitHub 程式碼搜尋同時含兩個參考 repo 名**，能找到照同一份 Prompt 做出的成品，用來判斷 Prompt 流傳時間。
- **Reddit 派 Codex 查**：Claude 的內建瀏覽器與 Claude in Chrome 都禁止開 reddit.com，登入也沒用。改派 Codex：`codex --search exec --skip-git-repo-check -s read-only -C <工作目錄> -o report.md "<prompt>" < /dev/null`，它的網頁搜尋可以限定 reddit.com 並讀貼文 JSON。`-o` 只存最後一則訊息，完整結果要從執行紀錄（stdout）撈。Antigravity 的瀏覽器要先在 Hub 視窗開啟對話才能用。
- 只找到轉引、衍生成品或存檔時，讀完補進第 0 段，仍維持 `partial`；不能只憑主題相同就認定是原貼文，要有數字、比喻、範例或清單組合對得上。

### 什麼時候可以標 `full`

```text
熱門排序捲到底 ─┐
               ├─▶ 有子回覆的留言逐則點開 ─▶ 讀到的則數 vs 貼文計數
最新排序捲到底 ─┘                                   │
                                    ┌───────────────┴───────────────┐
                                  相等                          讀到的較少
                                    │                               │
                                  full            兩種排序都到底、子回覆都點開了？
                                                        │                 │
                                                       是                否
                                                        │                 │
                                          full，第 0 段寫差額        partial，繼續補讀
```

- 兩種排序（熱門、最新）都要捲到底，有子回覆的留言都要點開。只做一種排序、或只捲到載不動為止，不算。
- 做完之後讀到的則數仍少於貼文計數，差的那幾則是**平台不顯示**（登入後也看不到），算 `full`。
- 這種情形要在第 0 段寫明差額：「貼文計數 N 則，平台顯示 M 則已全部讀完，差 N−M 則登入後也不顯示」。`source_replies` 填實際讀到的 M。
- 留言框只有一種排序的平台（例如 Facebook 選「所有留言」），以該排序捲到底、所有「查看回覆」都展開、畫面上已沒有可展開的按鈕為準。
- **留言極多時可抽樣（2026-11-17 維護者指示：「除非留言太多，你覺得不重要」）**：留言數千則以上，且抽樣幾乎都是「存」「+1」、邀請碼、導流等沒有資訊的內容，可以不讀完。至少讀完熱門排序前 300 則、最新排序前 100 則，確認沒有新的實測、反駁或更正，就標 `full`，第 0 段寫「共 M 則，讀 N 則抽樣，其餘判斷不重要：<理由>」。這個判準只用在留言；作者上傳的每張圖仍要看完。留言幾乎全是「留關鍵字換私訊」的導流貼文（例如留「協作」索取資料、作者固定自動回覆），留言區本身沒有分析價值，讀完第一頁確認是這種型態即可，不受 300／100 則下限限制。
- **引用貼文不拿來補差額（2026-11-20）**：Threads 頁面的「引用內容」是別人轉引這篇的貼文，**不能確定有沒有算進貼文的留言計數**（實例：串內 6 則加引用 2 則是 8，計數卻是 7）。引用要點開讀完、寫進第 0 段，但差額一律寫「貼文計數 N 則，平台顯示 M 則（只算串內留言與作者續樓）已全部讀完，差 N−M 則登入後也不顯示」，不要用引用數把差額湊成 0。同一則作者留言不要同時算成續樓與引用；「兩種排序是同一批」要實際比對過才寫。
- 原始社群貼文沒留連結的筆記，先用作者帳號、關鍵字、引用的 repo 名在 Threads／Facebook 站內搜尋與網頁搜尋找回原文；找到就照本節讀完，找不到才維持 `partial`，`source_review_note` 寫明試過哪些搜尋。

## 4. 首輪（2026-11-16～17）結果

- 135 篇全部完成：`full` 25、`partial` 94、`unavailable` 16。
- 2026-11-17 維護者登入 Threads／X／Facebook 後補讀 95 篇：`full` 95、`partial` 24（其中 17 篇原始貼文沒留連結，無法補）、`unavailable` 16。補讀又改正多處事實（作者回覆其實存在、留言證實招生導流、收入結構、聲音名稱等），並補強 11 份產出文件。
- 2026-11-18 收尾：用 Facebook 貼文搜尋找回 10 篇原貼文（多在 FB 社團與粉專），可補讀的 7 篇讀完或依抽樣判準完成；剩 8 篇 `partial` 都是原貼文搜尋不到或連結已失效，替代來源已讀完。
- 2026-11-18 再查轉引與存檔：找回 GitHub 開源神器矩陣的原貼文（Threads，原文有 7 個專案，筆記漏了 OpenBot，已補），改 `full`；剩 7 篇 `partial`。其餘幾篇找到的轉引與存檔改正了事實：Strata 原稿出自分析當天的 README（「合計 32GB 即可開始」只夠跑小尺寸）；K-harness 下架前的相依清單顯示它是 Electron 桌面程式，沒有用 pi；Android 官方技能「30 個」在 v1.0.15 時正確；WebGPU 修圖 Prompt 最晚 10-04 已流傳，照做的成品自己標出多項功能未完成。
- 新增任務：`T-20261017-35`、`T-20261018-19`、`T-20261026-35`、`T-20261026-36`、`T-20261107-06`、`T-20261108-07`、`T-20261113-01`。
- 修正的已完成任務產出：學術閱讀範本與提示詞（CQR／KSU 原版定義）、雙語論文閱讀指南（改以 PaperRead 為主角）、pstack 規格與驗證器、技能評選矩陣、agent-desktop 規格、Android 技能清單（37 個）與驗證器、TOML 規格、freelance 規格等。

## 5. partial 補讀

`partial` 不是終點。請維護者在內建瀏覽器登入 Threads／X／Facebook 一次後（帳密由維護者自己輸入），逐篇補讀留言、放大看圖，讀全了改 `full` 並更新數字與第 0 段；補讀到的新資訊照第 3 節檢討任務與產出檔。
