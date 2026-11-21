# 新筆記獨立審查管線：規劃

> 2026-11-21 起。目標：每篇新筆記都由**沒寫過它的 agent** 審過，審查紀錄能被 `tools/verify_inbox.py` 機器檢查；審查本身出錯時有覆核機制。
> 審查標準的唯一來源是 [`docs/source-review-sop.md`](source-review-sop.md)；本文件只講管線怎麼運作，不另寫規則。

## 1. 要解決的問題

2026-11-16～11-21 的重審一再抓到同類錯誤（自動回覆當證據、作者／工具認錯、二手數字冒充官方、推算寫成事實、留言沒讀完標 `full`、用引用貼文湊差額），而且已完成任務的產出檔建立在錯誤前提上。共同原因：寫的人自己標 `source_review: full`，沒有第二個人看過；Sonnet 的審查也會把推算寫成事實，所以審查本身也要被抽查。

## 2. 設計總覽

```text
作者寫筆記（frontmatter 填 written_by）
   │  verify_inbox：新筆記可以先提交，狀態是「待審」
   │  （README 標 ⏳、task_cli 不准 claim／complete 它的任務、寬限 7 天）
   ▼
review_pipeline.py queue ── 依來源平台分派 ──┬─ codex 道：官方文件、repo、數字、Reddit（codex --search exec，唯讀）
   │                                          └─ chrome 道：Threads／FB／X／IG 留言與圖片（Claude in Chrome 工作階段）
   ▼
審查者交回報告（固定 JSON 區塊）── ingest ──▶ reviews/<slug>.json 加一筆紀錄＋reviews/reports/ 存報告
   │                                          （記下派工當下的內容雜湊）
   ├─ pass，且不需覆核 ─▶ 筆記變「已審」
   ├─ changes_requested ─▶ 作者／整合者修正（written_by 加上自己、填 revised_at）─▶ 再審（確認修正）
   └─ 需要覆核（下修 full、更正 ≥2 處、審查者非強模型、雜湊抽中 1/5）─▶ 強模型 audit ─▶ 已審
```

### 2.1 審查紀錄（機器可檢查）

- 筆記 frontmatter 新增 `written_by`：寫過內容的 agent，格式 `<runtime>/<model>@<session>`，多人以 `; ` 分隔；之後修改內容的人要把自己加上，並填 `revised_at`。
- `reviews/<slug>.json`：該篇的審查紀錄（只追加），每筆含審查者身分、角色（`review`／`audit`）、範圍、`content_sha256`、結論、審查者判定的 `source_review`、更正數、報告路徑。
- 內容雜湊算的是「分析內容」：去掉任務狀態（勾選框、`狀態`、`完成日期`、`實作紀錄 / 證據` 欄位、frontmatter `status`、正文「當前狀態」行），所以 `task_cli` 認領／結案不會讓審查失效；其他任何改動都會。
- 報告存 `reviews/reports/<slug>/`，內文必須含雜湊與審查者身分（防止拿別篇的報告冒用）。

### 2.2 驗證器規則（只加不減）

| 檢查 | 失敗條件 |
| --- | --- |
| 作者 | 受管筆記缺 `written_by` 或格式錯 |
| 日期 | `analyzed_at`／`revised_at` 晚於今天，或 `revised_at` 早於 `analyzed_at` |
| 審查者獨立 | 審查者的 session 出現在 `written_by`；audit 的 session 與同輪審查者相同 |
| 紀錄完整 | 欄位缺漏、值不合法、報告不存在、報告不含雜湊或身分、日期倒退、紀錄指向不存在的筆記 |
| 結論一致 | `pass` 卻有更正；`pass` 的 `source_review` 與筆記現值不同 |
| 覆核 | 觸發條件成立卻沒有強模型 audit 通過現行雜湊 |
| 寬限 | 待審超過 7 天（從 `analyzed_at` 與 `revised_at` 較晚者起算） |
| 基準凍結 | `reviews/legacy-baseline.json` 的雜湊與程式內常數不符 |

「已審」＝現行雜湊上有 `pass` 紀錄，涵蓋 `source`、`facts`、`evidence`、`task_impact` 四個範圍，且覆核條件都滿足。

### 2.3 舊筆記過渡

- 合併當下 `main` 上的每篇筆記，把「分析內容雜湊」寫進 `reviews/legacy-baseline.json`，檔案雜湊釘在 `tools/review_ledger.py`。內容沒變的舊筆記免審；**一改內容就變成受管筆記**，要填 `written_by`、`revised_at` 並在寬限內送審。
- 不用日期切分：檔名日期是作者自己填的，用日期切分等於可以把新筆記寫成舊日期繞過。
- 舊筆記之後用 Codex 額度逐步補審（`queue --legacy N`、`run --legacy N`），補審通過的就有紀錄，不再依賴基準。
- 舊筆記不知道作者 session：補審與修改時作者寫佔位身分 `legacy/unknown@pre-review`，驗證器只准基準裡的筆記使用它（新筆記寫它會失敗，防止冒充「作者不明」來自審）。

### 2.4 派審

- 狀態與執行紀錄放 `~/codex-work/ai-inbox-review/`（不放 `AppData\Local`：Codex 的 `-o` 拒絕寫入含 reparse point 的路徑，2026-11-21 實測）。
- `tools/review_pipeline.py`：`queue`（列待審與該走哪一道）、`prompt`（從 SOP 標記區段產生審查指示）、`run`（codex 道：`codex --search exec -s read-only`，stdin 關閉、逾時、先查 bridge）、`ingest`（驗證報告格式與雜湊未變，寫紀錄）。
- Codex 道由 Windows 工作排程器每天跑一次 `run --lane codex`，只提交 `reviews/` 下的新檔。Windows 三問：排程器與被審的 repo／agent 不同生共死；既有的 agent-relay codex 工人關閉網路、做不了網頁查證，所以不重用它；Windows 原生可跑。
- Chrome 道：只有登入的 Claude in Chrome 讀得到留言。用 Claude Desktop 的排程工作（既有機制）每天跑一次，照 `queue --lane chrome` 審，`ingest` 寫紀錄。Pro 額度小，只做 Chrome 才能做的「原始資料讀完度」範圍，事實查核留給 Codex。
- Codex 對話自動出現在派工儀表板（127.0.0.1:8765 讀 Codex 的 state 資料庫），不另做儀表板。

### 2.5 審查被驗收

覆核（`audit`）觸發條件，任一成立就要強模型在現行雜湊上 `pass`：

1. 審查者把作者的 `full` 下修成 `partial`／`unavailable`。
2. 一次審查提出 ≥2 處更正。
3. 審查者模型不是強模型（`tools/review_ledger.py` 的 `STRONG_MODEL`：Opus、GPT-6.x Sol／Astra、維護者本人；Sonnet、Haiku、Fable、Gemini 等都要覆核）。
4. 抽查：現行雜湊前 8 碼轉整數 mod 5 = 0（約 1/5）。

audit 的 session 不能是作者，也不能是同輪審查者。上一次 audit 通過之後的審查才計入觸發。

## 3. 階段、驗收與回復

| 階段 | 內容 | 驗收 | 回復方式 |
| --- | --- | --- | --- |
| 1 紀錄與驗證器 | `tools/review_ledger.py`、`verify_inbox` 新檢查、legacy 基準、`task_cli` 鎖、README ⏳、範本 `written_by` | 單元測試涵蓋每條失敗條件的反例；全庫 `verify_inbox` PASS；舊檢查全部保留 | 還原這幾個 commit；基準檔是新增檔，刪除即回到舊行為 |
| 2 派審 | `tools/review_pipeline.py`、SOP 審查清單標記區段、排程註冊腳本 | 對 2 篇真實新筆記跑完整流程（codex 道實跑、報告入帳、驗證器認得）；`prompt` 內容來自 SOP | 停用排程工作；`reviews/` 紀錄留著不影響舊流程 |
| 3 覆核 | 強模型清單、覆核觸發規則與驗證器 | 測試：下修 full、更正 2 處、弱模型、抽中，四種都要求 audit；audit 同 session 被擋 | 同階段 1 |
| 4 文件與覆核 | AGENTS.md、SOP、ROADMAP、REVIEW.md 設計決策 | 未參與的強模型以攻擊者角度試著讓未審筆記通過，找到的洞修完再審 | — |

每階段 `python tools/verify_inbox.py && python -m unittest discover -s tests` 通過才提交；合併前 rebase 到最新 `main`、重產 legacy 基準再跑一次。

## 4. 威脅模型與已知極限

- 防的是**疏忽與自我放行**（自己標 full、沒人看、改完不重審），不是惡意偽造：能推 main 的 agent 都能改驗證器或寫假報告。偽造要同時寫出含正確雜湊的報告與紀錄，會在 diff 裡留下痕跡；REVIEW.md 記錄這個邊界。
- 身分是自報的 session id；Codex 道由 `run` 從 Codex 的 JSON 事件取得 thread id，不靠審查者自報。
- 雜湊不含任務狀態欄位，所以「實作紀錄 / 證據」裡的文字不受審查保護；那是任務證據，不是分析內容。
