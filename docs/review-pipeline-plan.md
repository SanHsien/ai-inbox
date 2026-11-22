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
   └─ 需要覆核（下修 full、更正 ≥2 處、審查者非強模型、slug 與第一筆審查者抽中 1/5）─▶ 強模型 audit ─▶ 已審
```

### 2.1 審查紀錄（機器可檢查）

- 筆記 frontmatter 新增 `written_by`：寫過內容的 agent，格式 `<runtime>/<model>@<session>`，多人以 `; ` 分隔；之後修改內容的人要把自己加上，並填 `revised_at`。**session 格式依 runtime 收緊**：`claude`、`codex` 必須是完整 UUID（不可縮寫，且 UUID、model、runtime 一律**小寫**，大寫報格式錯；`ingest` 會先 `strip()` reviewer，寫進紀錄與報告 header 的是正規化後的字串；抽查雜湊也用小寫）；`antigravity`、`hermes` 至少 8 字元；`human` 只接受 `human/maintainer@<YYYY-MM-DD>`；`legacy` 只接受 `legacy/unknown@pre-review`。這是**作者**的規則；**審查紀錄的 reviewer** 只接受 `claude` 與 `codex`（管線只有這兩道），`human`、`hermes`、`antigravity`、`legacy` 當 reviewer 一律報錯。維護者本人審查不走這套紀錄：直接改筆記，再由管線審。
- `reviews/<slug>.json`：該篇的審查紀錄（只追加），每筆含審查者身分、角色（`review`／`audit`）、範圍、`content_sha256`、結論、審查者判定的 `source_review`、作者聲明 `author_claim`、更正數、報告路徑。`author_claim` 不由審查者給：`ingest` 從筆記 frontmatter 的 `source_review` 讀，驗證器要求現行雜湊上的紀錄與筆記現值相同。
- 內容雜湊算的是「分析內容」，目標是：`task_cli` 的 claim／complete／close 不改變雜湊，其他任何手寫文字都算進去。**不算進雜湊**的只有：
  - 任務勾選框（`[x]` 視同 `[ ]`）；
  - frontmatter 第一個 `status:` 行的值（行尾註解照算）；正文第一個「當前狀態」行，且值是 `task_cli` 的標準標記（其他文字照算；`task_cli` 也只改寫標準標記的行，找行時跳過程式碼圍欄）；
  - 任務區塊內、**剛好兩格縮排**、格式嚴格為 `  - **<鍵>**：<值>`（鍵名前後無空白、全形冒號）的欄位行，**每個任務每個鍵只略過第一次出現**：`狀態` 的值完全是 `🟡 進行中` 或 `⚪ 不做（…）`；`完成日期`、`實作紀錄 / 證據` 在任務已勾選時略過（完成日期另須是 `YYYY-MM-DD`），未勾選時只有值為空，或完全等於範本固定佔位字串（白名單 `PLACEHOLDER_VALUES`）才略過。
  其餘一律算進雜湊：重複的欄位行、不同縮排、鍵名變形、半形冒號、續行、非標準的值、頂層圍欄之後的同名欄位。repo 裡有一個任務因為非標準寫法（`⚪ 不做（…）。` 句尾多一個句點）而對 `task_cli` 操作敏感，列在 `tests/test_review_ledger.py` 的 `KNOWN_NONSTANDARD`，不為它放寬規則。
- **雜湊算法定版**：`review_ledger.HASH_VERSION`，新紀錄寫入 `hash_version`，驗證器要求它存在且等於現行版本。`tests/test_review_ledger.py` 有 golden 測試（固定範例筆記對固定雜湊）：改 `analysis_text` 會讓 main 上所有審查紀錄與 legacy 基準失效，要改必須寫遷移（重算基準、把仍對應現行內容的紀錄重新派審）並遞增版本，不可只更新期望值。
- 報告存 `reviews/reports/<slug>/`。**紀錄與報告必須一致**：驗證器解析報告最後一個 ```` ```json ```` 區塊（與 `ingest` 共用同一個解析函式），要求 `verdict`、`corrections`（且等於 findings 筆數）、`scope`（集合相等）與紀錄相同；報告 header 的 `- reviewer:`、`- content_sha256:`、`- role:` 逐行與紀錄相同（不是「字串出現在內文任何地方」）。只改紀錄檔的 verdict 就想翻成 pass 會被擋。
- **只追加**：git 可用時，對每個比對基準——`HEAD`（工作樹未提交的改動）、環境變數 `AI_INBOX_REVIEW_BASE` 指的 commit（CI 設成 push 前的 main 或 PR 的 base，workflow 用 `fetch-depth: 0`）、`git merge-base HEAD origin/main`（本機分支上已提交但還沒進 main 的改動）——基準上的 `reviews/<slug>.json` 必須是現行陣列的前綴（已提交的紀錄不可改、不可刪、不可重排），基準上已存在的 `reviews/reports/**` 不可被改或刪（只看修改與刪除，新檔、已 `git add` 的新檔不算）。基準 commit 不存在（全零 SHA、shallow 抓不到）就略過該基準。只比 `HEAD` 的話，提交之後（＝CI 的 checkout）檢查就是 no-op，所以 CI 一定要給 `AI_INBOX_REVIEW_BASE`。

### 2.2 驗證器規則（只加不減）

| 檢查 | 失敗條件 |
| --- | --- |
| 作者 | 受管筆記缺 `written_by` 或格式錯 |
| 日期 | `analyzed_at`／`revised_at` 晚於今天，或 `revised_at` 早於 `analyzed_at` |
| 審查者獨立 | 審查者的 session 出現在 `written_by`；audit 的 session 與同輪審查者相同（session 比對：小寫後相等，或一方是另一方的前綴，防縮寫） |
| 紀錄完整 | 欄位缺漏、值不合法、身分格式不符 runtime 規定、報告不存在、日期倒退、紀錄指向不存在的筆記；缺 `hash_version` 或不等於現行版本 |
| 審查者身分來源 | reviewer 的 runtime 不是 `claude` 或 `codex`（human、hermes、antigravity、legacy 都不行）；audit 的模型不是強模型（強模型綁 runtime） |
| 紀錄與報告一致 | 報告 header 的身分／雜湊／角色與紀錄不同；結果區塊的 verdict、corrections、scope 與紀錄不同；解析不到結果區塊 |
| 只追加 | 對每個比對基準（`HEAD`、`AI_INBOX_REVIEW_BASE`、`merge-base HEAD origin/main`，見 2.1）：已提交的紀錄被改、刪、重排；已提交的報告被改或刪；`reviews/removed.json` 被改或刪。`AI_INBOX_REVIEW_BASE` 有設卻抓不到或不是 `HEAD` 的祖先也報錯（可能是 force-push）。已登記移出且筆記已不在的 slug 例外（見 2.6） |
| 移出清單 | `reviews/removed.json` 格式錯、日期不合法或晚於今天；已登記移出的 slug 又有同名筆記 |
| 結論一致 | `pass` 卻有更正；`pass` 的 `source_review` 與筆記現值不同；現行雜湊的 `author_claim` 與筆記現在的 `source_review` 不同 |
| audit 範圍 | `audit` 的 `scope` 沒有涵蓋四個範圍（讀不到來源時 audit 要改派能讀的那一道） |
| 覆核 | 觸發條件成立卻沒有強模型 audit 通過現行雜湊 |
| 待審期間的任務 | 筆記待審時，有任務已勾選且完成日期不早於待審起算日；新筆記待審時有任務「進行中」 |
| 寬限 | 待審超過 7 天（從 `analyzed_at` 與 `revised_at` 較晚者起算；補審被要求修改的舊筆記從該筆 `reviewed_at` 起算） |
| 基準凍結 | `reviews/legacy-baseline.json` 的雜湊與程式內常數不符 |

「已審」＝現行雜湊上有 `pass` 紀錄，涵蓋 `source`、`facts`、`evidence`、`task_impact` 四個範圍，且覆核條件都滿足。

### 2.3 舊筆記過渡

- 合併當下 `main` 上的每篇筆記，把「分析內容雜湊」寫進 `reviews/legacy-baseline.json`，檔案雜湊釘在 `tools/review_ledger.py`。內容沒變的舊筆記免審；**一改內容就變成受管筆記**，要填 `written_by`、`revised_at` 並在寬限內送審。
- 不用日期切分：檔名日期是作者自己填的，用日期切分等於可以把新筆記寫成舊日期繞過。
- 舊筆記之後用 Codex 額度逐步補審（`queue --legacy N`、`run --legacy N`），補審通過的就有紀錄，不再依賴基準。
- **補審的結論不可被忽略**：內容與基準相同的舊筆記，下列三種情況視為待審——`pending` 為 True（README 標 ⏳、`task_cli` 鎖認領與結案、進預設 `queue` 的 `fix` 道），寬限從相關那筆 `reviewed_at` 起算（紀錄檔壞到讀不出日期時用最早的可讀日期），超過 7 天 `verify_inbox` 失敗；內容還沒被改，所以不要求 `written_by`：
  1. 該筆記的紀錄檔有任何錯誤（格式錯、壞資料）——不可因為免審就把錯誤當沒事；
  2. 現行雜湊上的 `pass` 紀錄，`source_review` 與筆記現值不同（例如審查者把 `full` 下修成 `partial`）——報錯，筆記要照審查結論改；
  3. 現行雜湊上有未被後續 audit pass 推翻的 `changes_requested`。
  只是「還沒審完」（缺範圍、需要 audit 但還沒做）**不算待審**，維持免審，只在 `queue --legacy` 出現。照報告改完內容後，筆記就變成一般的受管筆記（要填 `written_by`、`revised_at`，再送審）。
- 舊筆記不知道作者 session：補審與修改時作者寫佔位身分 `legacy/unknown@pre-review`，驗證器只准基準裡的筆記使用它（新筆記寫它會失敗，防止冒充「作者不明」來自審）。

### 2.4 派審

- 狀態與執行紀錄放 `~/codex-work/ai-inbox-review/`（不放 `AppData\Local`：Codex 的 `-o` 拒絕寫入含 reparse point 的路徑，2026-11-21 實測）。
- `tools/review_pipeline.py`：`queue`（列待審與該走哪一道）、`prompt`（從 SOP 標記區段產生審查指示）、`run`（codex 道：`codex --search exec -s read-only`，stdin 關閉、逾時、先查 bridge）、`ingest`（驗證報告格式與雜湊未變，寫紀錄）。
- `ingest`（CLI）的身分限制：Codex 的審查只能由 `run` 從事件取得 thread id 入帳，`ingest` 一律拒絕 `codex` 身分；`claude` 身分的 session 必須等於環境變數 `CLAUDE_CODE_SESSION_ID`（沒設或不同就拒絕）。`audit` 少範圍也拒絕。
- **提交只在專用工作樹**：每一道各有一個（codex 道 `STATE_DIR/repo`、chrome 道 `STATE_DIR/repo-chrome`），互不清理對方的。`--commit`（`ingest`、`run`）只准在這兩個工作樹執行，且 HEAD 為 detached、動手前已追蹤檔沒有未提交改動（`git status --porcelain --untracked-files=no`；未追蹤檔不擋）；否則報錯並指向 `cron`。`ingest` 的 `--reviewer` 只接受 `claude/<model>@<CLAUDE_CODE_SESSION_ID>`，`ingest()` 函式本身也拒絕 claude／codex 以外的 runtime。`git add` 只加這次入帳寫入的檔案（紀錄檔與新報告）與 `README.md`。提交前驗證是「沒有引入新錯誤」（入帳前先記下 `verify_inbox` 的錯誤行，入帳後只有新出現的才算失敗）；失敗時還原這次寫入的檔案。push 被拒就 rebase 後重驗再推，最後失敗則 reset 回入帳前。
- Codex 道由 Windows 工作排程器每天跑一次 `cron --lane codex`（在專用工作樹同步 `origin/main` 後執行 `run --lane codex --commit`），提交「這次的審查紀錄、報告與 `README.md`」。專用工作樹有上次殘留的改動時，`cron` 先 `reset --hard`＋`clean -fd`（動手前確認路徑確實是 `STATE_DIR/repo` 且在 `git worktree list` 裡；那是管線自己的工作樹，不是任何人的工作目錄）再同步，不會永久卡住。Windows 三問：排程器與被審的 repo／agent 不同生共死；既有的 agent-relay codex 工人關閉網路、做不了網頁查證，所以不重用它；Windows 原生可跑。
- Chrome 道：只有登入的 Claude in Chrome 讀得到留言。用 Claude Desktop 的排程工作（既有機制）每天跑一次 `cron --lane chrome`：它同步專用工作樹並印出工作樹路徑與待審清單，Claude in Chrome 工作階段把報告草稿存到 `STATE_DIR/drafts/`（工作樹外，cron 建立並印出路徑；cron 的 reset／clean 只動專用工作樹，不會刪它），再 `cd` 進專用工作樹執行 `prompt`／`ingest --commit`。Pro 額度小，只做 Chrome 才能做的「原始資料讀完度」範圍，事實查核留給 Codex。
- Codex 對話自動出現在派工儀表板（127.0.0.1:8765 讀 Codex 的 state 資料庫），不另做儀表板。

### 2.5 審查被驗收

覆核（`audit`）觸發條件，任一成立就要強模型在現行雜湊上 `pass`：

1. 審查者把作者的 `full` 下修成 `partial`／`unavailable`。
2. 一次審查提出 ≥2 處更正。
3. 審查者模型不是強模型（`tools/review_ledger.py` 的 `STRONG_MODEL`，**模型綁 runtime**：`claude/opus-<數字>(.<數字>)?`、`codex/gpt-6(.<數字>)?-(sol|astra)`；其餘一律不是——`opus-anything`、`hermes/opus-5`、`codex/opus-5.5`、`claude/gpt-6.1-sol` 都不算；`human/maintainer` 不再是強模型，也不能當審查者；Sonnet、Haiku、Fable、Gemini 等都要覆核）。
4. 抽查：`sha256(slug + "\n" + 第一筆紀錄的 reviewer)` 前 8 碼轉整數 mod 5 = 0（約 1/5）；沒有任何紀錄時不算抽中。不看內容雜湊（改一個字就能換到不被抽中的雜湊），也不只看 slug（作者自己挑 slug 就能躲）；第一筆審查者的 session 不是作者能選的。

audit 的 session 不能是作者，也不能是同輪審查者；audit 的範圍必須是四個範圍全部。上一次 audit 通過之後的審查才計入觸發。

### 2.6 筆記移出 repo（不支援改名）

有審查紀錄的筆記**不要改檔名**：紀錄綁 slug，改名會讓舊紀錄變孤兒、新 slug 變待審，已完成的任務還會被判「審查通過前結案」。要把筆記移出 repo（例如搬到別的 repo），在 `reviews/removed.json` 登記：`{"removed": [{"slug": "...", "removed_at": "YYYY-MM-DD", "reason": "..."}]}`（只追加；檔案不存在視為空；每筆三個欄位都要有，日期合法且不晚於今天）。

- slug 在清單裡且 `notes/<slug>.md` 不存在：該 slug 的紀錄檔與報告被刪除不算違反只追加，紀錄檔留著也不算孤兒。
- slug 在清單裡卻又有 `notes/<slug>.md`：報錯。同名筆記不可復活，否則刪掉紀錄再把筆記放回，舊筆記就能回到免審並丟掉 `changes_requested`。
- 清單本身只追加（對各基準比對前綴）。不在清單的刪除照舊報錯，訊息提示去登記。

## 3. 階段、驗收與回復

| 階段 | 內容 | 驗收 | 回復方式 |
| --- | --- | --- | --- |
| 1 紀錄與驗證器 | `tools/review_ledger.py`、`verify_inbox` 新檢查、legacy 基準、`task_cli` 鎖、README ⏳、範本 `written_by` | 單元測試涵蓋每條失敗條件的反例；全庫 `verify_inbox` PASS；舊檢查全部保留 | 還原這幾個 commit；基準檔是新增檔，刪除即回到舊行為 |
| 2 派審 | `tools/review_pipeline.py`、SOP 審查清單標記區段、排程註冊腳本 | 對 2 篇真實新筆記跑完整流程（codex 道實跑、報告入帳、驗證器認得）；`prompt` 內容來自 SOP | 停用排程工作；`reviews/` 紀錄留著不影響舊流程 |
| 3 覆核 | 強模型清單、覆核觸發規則與驗證器 | 測試：下修 full、更正 2 處、弱模型、抽中，四種都要求 audit；audit 同 session 被擋 | 同階段 1 |
| 4 文件與覆核 | AGENTS.md、SOP、ROADMAP、REVIEW.md 設計決策 | 未參與的強模型以攻擊者角度試著讓未審筆記通過，找到的洞修完再審 | — |

每階段 `python tools/verify_inbox.py && python -m unittest discover -s tests` 通過才提交；合併前 rebase 到最新 `main`、重產 legacy 基準再跑一次。

## 4. 威脅模型與已知極限

- 防的是**疏忽與自我放行**（自己標 full、沒人看、改完不重審），不是惡意偽造：能推 main 的 agent 都能改驗證器或寫假報告。偽造要同時寫出一致的報告與紀錄，會在 diff 裡留下痕跡；REVIEW.md 記錄這個邊界。
- **偽造的難度照實寫**：`ingest` 會代寫報告格式，所以「會用 CLI」不構成防線；現在靠這幾道提高門檻——session 依 runtime 規定格式（claude／codex 要完整 UUID，不能縮寫來躲比對）、`claude` 身分要等於 `CLAUDE_CODE_SESSION_ID`、Codex 審查只能由 `run` 從事件取 thread id 入帳、紀錄與報告逐項一致、已提交的紀錄與報告只追加。仍然**不防蓄意偽造**：能直接改檔的 agent 可以同時寫出一致的假報告與假紀錄、或設環境變數，只是會在 diff 與 git 歷史裡留下痕跡。
- 身分是自報的 session id；Codex 道由 `run` 從 Codex 的 JSON 事件取得 thread id，不靠審查者自報。
- **審查者身分的來源只剩兩種**：`claude`（`ingest` 要求 session 等於 `CLAUDE_CODE_SESSION_ID`）與 `codex`（只能由 `run` 從事件取 thread id 入帳）。human、hermes、antigravity 不能當審查者：早先它們沒有任何身分檢查，兩行指令就能自寫報告、自審放行。**已知極限**：Claude 的模型名是自報的（Sonnet 工作階段可以自稱 opus，驗證器分辨不出來），也能自設環境變數；強模型清單防的是疏忽，不是蓄意。維護者本人審查不走這套紀錄：直接改筆記，再由管線審。
- **雜湊算法定版**：見 2.1。雜湊算法改版曾讓唯一一筆真實審查紀錄（5 處更正）靜默失效，因為紀錄綁在舊算法的雜湊上。現在 `HASH_VERSION` 加 golden 測試擋住悄悄改動；真的要改，必須同時遷移基準與紀錄。
- 雜湊不含的任務欄位只剩 `task_cli` 會寫的樣子（見 2.1）。**實際剩下的窗口**只有兩處：任務的**關閉理由**（`⚪ 不做（…）` 括號裡的文字）與**已完成任務的單行證據**（`實作紀錄 / 證據` 與 `完成日期` 的值）；這兩處的文字不受審查保護，那是任務證據，不是分析內容。要分析內容受保護就別寫進這裡。未完成任務的 `完成日期`／`實作紀錄 / 證據` 只有空值或固定的範本佔位字串（`review_ledger.PLACEHOLDER_VALUES` 白名單，來源是範本與現有筆記實際用過的寫法）才略過，其他 `*（` 開頭的任意文字算進雜湊；重複的欄位行、不同縮排、續行、非標準值也都算進雜湊。
- **force-push 與 CI 基準**：只追加檢查在 CI 靠 `AI_INBOX_REVIEW_BASE`（push 前的 main 或 PR 的 base）。force-push 改寫 main 之後那個 commit 不存在，若默默略過，整個檢查就失效；所以基準有設卻抓不到或不是 `HEAD` 的祖先，驗證器報錯而不是放行。**main 目前沒有分支保護**，force-push 會讓 CI 報錯而不是放行，但改寫已經發生；要不要開分支保護（禁止 force-push）由維護者決定。
- **兩道並行入帳同一篇**（社群筆記會同時派 chrome 與 codex）：後推的一道 push 被拒、rebase 時 `reviews/<slug>.json` 會兩邊都追加而衝突。`commit_and_push` 的 `redo`：`rebase --abort`、`reset --hard origin/main`，用同一份報告文字在最新 main 上重新入帳（紀錄重新追加、報告序號重編），重跑「沒有引入新錯誤」檢查後再推，最多重做 2 次；重做也失敗（例如筆記內容已變、雜湊不符）才放棄並還原。
- 自動 reset／clean 與 `--commit` 只對 linked worktree（`git rev-parse --git-dir` 與 `--git-common-dir` 不同）：主 checkout 或一般 clone 被放在專用路徑也拒絕。
- 待審期間任務結案的檢查看「完成日期 ≥ 待審起算日」：把完成日期倒填成更早的日期可以躲過，那在 diff 與 git 歷史裡是可見的竄改，不另防。
- **`revised_at` 重置寬限（已知極限，不修）**：作者每次改內容都可以把 `revised_at` 往後填，讓 7 天寬限重新起算。待審期間任務鎖住、README 標 ⏳、佇列持續派審，所以拖延不會讓筆記變成「已審」，只是延後 `verify_inbox` 的逾期錯誤。
- 未知的 `當前狀態` 變體（例如帶說明的「封存（理由…）」）算進雜湊，`task_cli` 因此不改寫它們：筆記的任務狀態以 frontmatter `status` 與任務欄位為準，正文標記只是顯示用。
