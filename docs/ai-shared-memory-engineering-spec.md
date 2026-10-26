# 多 Agent 團隊共用記憶系統工程規範

> 對應任務：`T-20261026-23`｜來源筆記：[`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](../notes/2026-10-26-ai-shared-memory-template-team-collaboration.md)
> 原始來源：[`Leoceeport/ai-memory-template`](https://github.com/Leoceeport/ai-memory-template) @ `ad84653`（最後推送 2026-09-17；GitHub 顯示 1 star，**授權欄位為空**，README 只寫「自用與團隊內部使用皆可，改成自己的版本不需回報」）。查證日期 2026-10-26。
> 因授權欄位為空，本文用自己的話整理規格，不轉貼範本內容；範本的檔案逐一讀過（README、`MEMORY.md`、`.claude/CLAUDE.md`、`domains/` 各索引、`_meta_kind.md`、`rules_summary.md`、`lessons/README.md`、`scripts/*.sh`、`hooks/*`、`docs/monthly_consolidation.md`），**沒有執行任何腳本**。
> 維護者既有做法只引用「結構與數字」，不引用私人記憶內容；私有 repo 一律用別名（`[Private Repo: 跨Agent資產庫]`）。

---

## 0. 先釐清：筆記與範本實際內容的差異

| 筆記的說法 | 範本實際 | 出處 |
|---|---|---|
| 糾正佇列審核後「合入 `lessons.md`」 | 範本沒有 `lessons.md`。流程是：`correction-queue.jsonl` →（管理員逐條 y／n／edit）→ 通過者搬到 `corrections.jsonl`，並合併進**規則主表** `domains/rules/rules_summary.md` → 清空佇列 | `domains/lessons/README.md`、`domains/lessons/_index.md`、`docs/monthly_consolidation.md` 第 4 點 |
| `check_index.sh` 回傳非 0「即擋下 CI」 | 範本**沒有 CI 設定**；非 0 只對「手動／收工流程呼叫腳本的人」有意義，要擋 CI 得自己接 | 倉庫檔案清單（無 `.github/`） |
| 具體檔 frontmatter 有 `kind / date / status` | 範本定義的是 `name / description / type / kind / date`，**沒有 `status`**；`kind` 有 7 種值 | `domains/rules/_meta_kind.md` |
| 單人與團隊都必須走佇列 | 範本明寫「一人使用可跳過佇列、直接改主表」 | `README.md` 讀寫規則第 3 條、`domains/lessons/_index.md` |
| 防線是「Git 原子同步」 | `memory_commit.sh` 是「commit → `pull --rebase` → push」，**衝突時只中止 rebase、本機 commit 保留**，並不是交易式原子；失敗用不同結束碼區分 | `scripts/memory_commit.sh` |
| 腳本可直接在 Windows 11 原生用 | 腳本是 POSIX `sh`，用到 `/tmp`、`whoami`、`grep`、`sed`；Windows 要靠 Git Bash，或照 `T-20261026-24` 改寫成 Python | `scripts/*.sh`、`hooks/*.sh` |

---

## 1. 三跳查詢協議與 Context 預算控制

### 1.1 拓撲

```text
        開工時 hook 自動注入（只注入第 1 跳）
                       │
                       ▼ 跳 1
   ┌──────────────────────────────────────────┐
   │ MEMORY.md  入口索引：一行一條「指針」，    │   ← 永遠只放指針，不放內容，不超過一頁
   │ 指向：組織側寫｜規則主表｜寫入規範｜        │
   │       主題總索引｜糾正佇列                  │
   └───────────────┬──────────────────────────┘
                   ▼ 跳 2（按需，依任務挑一個主題）
   ┌──────────────────────────────────────────┐
   │ domains/<主題>/_index.md  主題索引         │   ← 單一索引條目 > 60 → 拆子資料夾或歸檔
   │ 一行一檔：[標題](檔) — 一句話說明          │
   └───────────────┬──────────────────────────┘
                   ▼ 跳 3（只讀真正需要的幾個檔）
   ┌──────────────────────────────────────────┐
   │ domains/<主題>/<YYYY-MM-DD-事件>.md        │   ← frontmatter: name/description/type/kind/date
   └──────────────────────────────────────────┘
規則：最多三次查詢；禁止整包讀取
```

### 1.2 為什麼這能控制 Context（可驗證的算式）

每次工作的記憶載入量：

```text
B = B_entry + B_topic + Σ B_file(i)         i = 1..k，k 為跳 3 讀的檔數
約束：B_entry 為固定成本（每次開工都付），B_topic 與 B_file 為變動成本（按需付）
目標：把「每次都付」的部分壓到最小，其餘用索引指針換取
```

實測數字（2026-10-26，字元／位元組數，**未用 tokenizer 換算**，token 數依模型而異）：

| 對象 | 每次開工固定載入 | 全部內容 |
|---|---|---|
| 範本（空白狀態） | `MEMORY.md` 540 bytes ＋ `domains/_index.md` 345 bytes（`session_start.sh` 只注入這兩個） | —（空範本） |
| 維護者現有的 Claude 記憶庫 | `MEMORY.md` 189 行、26,889 字元（39,111 bytes）；索引條目 163 條 | 另有 169 個記憶檔，合計 793,091 bytes，平均約 4.7 KB |

讀法：只讀入口索引約 39 KB，若改成整包載入約 832 KB，兩者相差約 21 倍。**這是同一份記憶庫的規模對比，不是效能實驗**；它說明「索引化」的價值，也說明維護者現有的 `MEMORY.md` 本身已偏大（見 1.3）。

### 1.3 與「滾動視窗」流派的取捨

筆記所述的「Hook 載入最新 10 份 Summary」是固定成本隨摘要大小線性成長、且沒有層級可以跳過；三跳法的固定成本只取決於入口索引，變動成本取決於任務。三跳法的代價是**索引必須被維護**，否則指針失效或漏編，查詢就退化成猜檔名——這正是第 5 節索引健檢要解決的問題。

維護者現況需注意：入口 `MEMORY.md` 有 163 條指針、遠超 60；範本的 60 條門檻是套在「單一索引」上，入口索引的要求是「只放指針、不超過一頁」。維護者的入口索引已用章節分群（User／Feedback／Project／Reference／Insight），並搭配 QMD 搜尋輔助載入。套用本規範時應把「入口索引條目數」也列入監控（建議警告線與主題索引同為 60，超過就把某一類整體下沉到主題索引），但這是**本文的建議**，範本並未對入口索引設數字門檻。

---

## 2. 目錄結構範例

範本的結構（以 GitHub tree API 讀到的檔案清單為準）：

```text
<memory-repo>/                      # 團隊自建的「私人」倉庫，範本本身不直接拿來寫
├── MEMORY.md                       # 入口索引
├── _org.md                         # 組織側寫（是誰、做什麼、對外禁忌、語言語氣）
├── domains/
│   ├── _index.md                   # 主題總索引
│   ├── rules/    _index.md  rules_summary.md  _meta_kind.md
│   ├── people/   _index.md         # 客戶、夥伴、別名表
│   ├── projects/ _index.md         # 一案一檔或一案一資料夾
│   ├── lessons/  _index.md  README.md  correction-queue.jsonl  corrections.jsonl
│   └── tools/    _index.md         # 工具、金鑰「放在哪」（不是金鑰本身）、排程
├── scripts/  memory_commit.sh  check_index.sh  scan_secrets.sh  install_hooks.sh
├── hooks/    pre-commit  session_start.sh  stop_reminder.sh
├── docs/     monthly_consolidation.md
└── .claude/  CLAUDE.md  settings.snippet.json     # 貼進每人的 ~/.claude/
```

歸檔慣例：各主題資料夾下 `_archive/YYYYMM/`，原檔搬過去，索引改指向濃縮摘要（`docs/monthly_consolidation.md` 末段）。

與維護者既有結構的對照（只比較結構）：

| 面向 | 範本 | 維護者的 Claude 記憶庫 | 共用 SSOT 倉庫 `[Private Repo: 跨Agent資產庫]` |
|---|---|---|---|
| 一檔一事實 | 是（帶日期檔名） | 是：170 個 .md 檔，依前綴分 `feedback-`／`project-`／`reference-`／`insight-`／`daily-`／`user-` | `knowledge/` 為「有來源與日期的精煉知識」，3 個主題檔 |
| 索引 | `MEMORY.md` → `_index.md` | `MEMORY.md` 單層、章節分群 | `knowledge/README.md` 為索引 |
| 規則單一來源 | `rules_summary.md` | 全域指令檔 | `rules/AGENTS.md`、`rules/GLOBAL_RULES.md` |
| 變更審核 | correction-queue | 直接寫（單人） | 經審查的提交；改 knowledge 後要更新雜湊，狀態回到待審 |

---

## 3. 動詞寫入契約

### 3.1 規則

1. **開頭用動詞**：`implemented / fixed / decided / discovered / flagged / reversed / deferred`（`_meta_kind.md`）。目的：讓一行標題就能判斷「發生了什麼」，索引不用另寫摘要。
2. **帶日期**：日期檔名或日期段落；**禁用相對時間詞**（昨天、剛才、上週），寫絕對日期。
3. **同一天同一件事不重寫**：先 grep 有沒有。
4. **不確定標「待驗」**，不寫成事實。
5. **不值得寫就不寫**：沒有持久參考價值的不入庫。
6. 寫完同時更新該資料夾 `_index.md`（沒更新索引 = 沒寫，第 5 節的健檢會抓）。

### 3.2 `kind` 與 frontmatter

```text
---
name: 短-slug
description: 一行說明（用來判斷相關性，會被索引引用）
type: user | feedback | project | reference
kind: decision | discovery | gotcha | correction | progress | decision_reversal | open_question
date: YYYY-MM-DD
---
```

| kind | 用途 | 生命週期處理（月整理） |
|---|---|---|
| decision | 拍板 | 被推翻時，舊的標「已被 X 推翻」 |
| discovery | 查到的事實 | 動態資料需標查證日期 |
| gotcha | 踩過的坑 | 長期保留 |
| correction | 對 AI 行為的糾正 | 經佇列審核後才進規則 |
| progress | 進度、待辦 | 案子結案 → 濃縮成三行結論並歸檔 |
| decision_reversal | 推翻決定 | 與被推翻者互相指向 |
| open_question | 待決 | 有答案 → 改成 decision 並補日期 |

---

## 4. 糾正審核佇列與單一權威

### 4.1 為什麼需要

多人或多 Agent 都能「糾正 AI」，若每人直接改規則主表，主表會互相打架、無人負責。規定：**規則主表只有一個寫入者（管理員／主 Session）；其他人只能往佇列追加。**

### 4.2 資料綱要（來自 `lessons/README.md`，欄位意義為本文補充）

每行一個 JSON 物件（JSONL）：

| 欄位 | 型別 | 說明 |
|---|---|---|
| `id` | string | `corr-<時間戳>`；全佇列唯一 |
| `timestamp` | string | ISO 8601 含時區 |
| `by` | string | 誰提出（人或 Agent 名稱） |
| `scene` | string | 發生了什麼 |
| `wrong` | string | 錯在哪 |
| `correct` | string | 該怎麼做 |
| `category` | enum | `verification｜approval｜language｜persona｜tone｜factcheck` |
| `priority` | enum | `core｜rule｜nit` |
| `pinned` | boolean | 是否釘選 |

範本的佇列與已通過檔（`correction-queue.jsonl`、`corrections.jsonl`）在 `ad84653` 都是空檔，**沒有範例資料列可參考**；欄位以 README 描述為準。

### 4.3 狀態與流程

```text
 任何人／Agent 發現被糾正
        │ 追加一行（append-only，不改既有行）
        ▼
 ┌────────────────────────┐     審核者逐條：  y
 │ correction-queue.jsonl │ ───────────────────────▶ 搬到 corrections.jsonl（主檔）
 │       （待審）          │                          並合併進 rules_summary.md（註明日期與來源）
 └────────────────────────┘     n  ───────────────▶ 丟棄（建議在月整理紀錄留一行原因）
                                edit ──────────────▶ 改寫後再當 y 處理
 全部處理完 → 佇列清空
```

### 4.4 單一權威的落地要求

- **誰是權威**：管理員（團隊）或「主 Session」（單人多 Agent）。權威寫入規則主表前，必須逐條看過 `scene/wrong/correct`，不批次盲目接受。
- **子 Agent 與非權威 Session**：只准追加佇列，不得改 `rules_summary.md`。
- **單人例外**：範本明寫一人使用可跳過佇列。多 Agent 同時寫的單人環境，是否跳過取決於「是否真的有多個寫入者」，見 `docs/correction-queue-evaluation.md`。
- **併發追加的 Git 風險（本文推論，未實測）**：兩個人各自在同一檔尾追加一行，Git 會判衝突。可行緩解：對佇列檔設 `.gitattributes` 的 `*.jsonl merge=union`（Git 內建 union 合併驅動，會保留雙方新增行），或一個糾正一個檔。任一方案落地前要先實測合併行為。
- **審計**：`pinned` 與 `priority: core` 的項目建議在審核時額外要求第二人確認（本文建議，範本無此規定）。

---

## 5. 索引防腐蝕門檻

### 5.1 範本的四類檢查（`scripts/check_index.sh`）

| # | 檢查 | 判定方式（讀碼） | 輸出 |
|---|---|---|---|
| 1 | 未編索引 | 對每個索引所在資料夾的同層 `.md`（排除 `_index.md`、`README.md`），檢查檔名字串是否出現在索引中 | `未編索引 <檔>` |
| 2 | 索引壞連結 | 擷取索引中 `](…)` 的相對連結（排除 `http` 開頭），檢查檔是否存在 | `壞連結 <索引> → <路徑>` |
| 3 | 入口壞指針 | 擷取 `MEMORY.md` 中反引號包起來、含 `/` 與 `.md` 的路徑，檢查存在 | `入口壞連結 …` |
| 4 | 索引過長 | 以 `^- ` 開頭的行數 > 60 | `過長 <索引> 有 N 條，該歸檔或拆分` |

任一項有輸出則結束碼為 1，否則印「索引正常」。

### 5.2 讀碼發現的弱點（建議在 Python 版修正；未實測）

1. 「未編索引」用**子字串比對**（`grep -q "$b" "$idx"`）：`a.md` 會被索引裡的 `data.md` 誤判為已編入。Python 版應改為解析連結目標後做集合比對。
2. 「過長」只數 `^- ` 開頭行，巢狀縮排或編號清單不被計入。
3. 暫存結果寫固定路徑 `/tmp/check_index_out`，兩個人同時跑會互相覆蓋；Windows 原生也沒有 `/tmp`。
4. 只檢查「同層」`.md`，子資料夾（含 `_archive/`）內的檔不檢查；這是合理的，但規範要明講。
5. 入口索引（第 3 項）只抓有反引號的路徑，用 `[文字](連結)` 寫法的指針會漏檢。

### 5.3 門檻規範

| 項目 | 規範值 | 超標時動作 |
|---|---|---|
| 主題索引條目數 | ≤ 60（範本值） | 拆子資料夾或歸檔到 `_archive/YYYYMM/` |
| 入口索引 | 只放指針、不超過一頁 | 範本無數字；本文建議同樣以 60 條為警告線 |
| 壞連結／漏編／入口壞指針 | 0 | 修正後才可 commit（建議以 pre-commit 或收工流程串 `&&`） |
| 月整理 | 每月一次、約 30 分鐘 | 依 `docs/monthly_consolidation.md` 六步：健檢 → 合併重複／濃縮已結案 progress／open_question 轉 decision／標記被推翻 → 拆分肥大索引 → 清佇列 → 掃金鑰 → 提交並留一行紀錄 |

---

## 6. Git 防線

### 6.1 收工同步 `memory_commit.sh` 的行為（讀碼）

```text
git add -A
├─ 無變更 → 印「沒有變更」
└─ 有變更 → commit（訊息含時間與使用者）；失敗 → 結束碼 1
沒有 origin → 只留本機版本，結束碼 0
git pull --rebase origin <當前分支>
├─ 失敗 → git rebase --abort（退回合併前狀態；本機 commit 保留、未推送），印原因前 3 行，結束碼 2
└─ 成功 → git push
          ├─ 成功 → 「已推送」
          └─ 失敗 → 本機 commit 保留，印錯誤前 3 行，結束碼 3
```

規範要點：

1. **工作區永遠不留在「合併進行中」或帶衝突標記的狀態**——失敗一律先 `rebase --abort`。
2. **三種失敗用不同結束碼**（1 commit、2 合併衝突、3 推送），呼叫端（hook 或 Agent）可據此決定下一步，並且**明講錯誤，不吞**。
3. 它保證的是「不留半成品」，**不保證「不丟 commit」以外的原子性**：本機 commit 在失敗後仍存在，需人工 `pull --rebase`、解衝突、再 push。
4. 範本的 `git add -A` 會把工作區所有變更一起提交；在多 Agent 共用的工作區，這會連別人未完成的檔案一起提交。共用倉庫應改為只加自己負責的路徑（本文建議）。

### 6.2 開工與收尾 Hook

- `session_start.sh`（SessionStart）：`git pull --rebase`（錯誤被丟棄）後，把 `MEMORY.md` 與 `domains/_index.md` 印到 stdout，讓內容進入對話。注意：**拉取失敗不會告知使用者**（stderr 導向 `/dev/null`），可能用舊記憶工作；規範建議失敗時至少印一行警告。
- `stop_reminder.sh`（Stop）：記憶倉庫有未提交變更時，**每天第一次**擋一次收尾（回傳 `decision: block`），提醒寫回、更新索引、跑健檢與提交；以 `/tmp/memory_stop_nudge_<日期>` 當當日標記，並檢查 `stop_hook_active` 避免無限迴圈。

### 6.3 金鑰掃描

`scan_secrets.sh` 用單一正規式擋：AWS 存取金鑰（`AKIA…`）、GitHub PAT（`ghp_…`、`github_pat_…`）、`sk-` 開頭金鑰、Slack token（`xox…`）、Google API key（`AIza…`）、Telegram bot token 格式、私鑰標頭，以及 `password/secret/token/api_key` 後接 12 字以上值的賦值式。`pre-commit` hook 對**暫存區**內容掃描（`git show :<file>`，不是工作區），`--all` 掃全倉。擋下時要求「把該行改寫成『金鑰在某處』」，不要繞過。

弱點（讀碼）：這是黑名單式特徵比對，擋不了沒有已知前綴的金鑰與個資（姓名、電話、財務）；`--all` 用 `grep -r` 會讀所有檔含二進位。規範仍應補一條人工規則：敏感資料不進共用倉、不進對話（範本 `rules_summary.md` 第 11 條）。

### 6.4 Windows 原生落地對照

| 範本依賴 | Windows 11 原生替代 |
|---|---|
| `sh`／`grep`／`sed`／`/tmp`／`whoami` | Git Bash，或以 Python 3.11+ 標準庫改寫（`T-20261026-24` 的方向） |
| `.git/hooks/pre-commit`（`cp` ＋ `chmod`） | Windows 可直接複製檔案；Git for Windows 以 sh 執行 hook |
| `settings.snippet.json` 的 `sh $HOME/...` | 改為 `python <路徑>` 或 `bash` 明確指令；`$HOME` 在不同 shell 展開不同 |
| 當日標記用 `/tmp/…` | 改用 `%TEMP%` 或倉庫外的狀態檔 |

---

## 7. 採用順序（範本建議 + 本文補充）

1. 範本原建議：兩個人試兩週（一管理員、一使用者）→ 只開 `people / projects / rules` 三個主題 → 兩週後看索引有沒有被維護再加人。
2. 本文補充：先實作並通過健檢工具（`T-20261026-24`）再推行；佇列併發追加方案（第 4.4 節）要先在拋棄式 clone 上實測合併行為。
3. 不建議：直接把範本當成自己的寫入倉庫（範本 README 自己也這樣要求）。

---

## 8. 查證來源與未查證項目

已查證（2026-10-26，以 `gh api` 讀取檔案文字，未 clone）：

- <https://github.com/Leoceeport/ai-memory-template> @ `ad84653`：上述所有檔案；`stargazers_count = 1`、`license = null`、`pushed_at = 2026-09-17`
- 本機維護者記憶庫的結構與數量（`ls`、行數、位元組數統計；未引用內容）
- 維護者共用 SSOT 倉庫的 `AGENTS.md`、`docs/SSOT_CONTRACT.md`、`docs/RUNBOOK.md`（私有，僅引用結構）

未查證／未實測：

- 範本腳本在任何環境的實際執行結果（只讀碼）；
- Facebook 社團討論串（<https://www.facebook.com/groups/1224997379198346/permalink/1423729639325118>）需登入，**未讀取**，筆記中 Going Li／顏志吉／Max DDuan 的說法均為轉述，未驗證；
- `merge=union` 對 JSONL 的實際合併效果；
- token 數（只給字元與位元組數）。
