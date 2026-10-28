# AI Inbox — 跨 Agent 任務總管規範 (AGENTS.md)

本倉庫 (`SanHsien/ai-inbox`，本地路徑 `C:\GitHub\ai-inbox`) 是維護者的 **個人 AI 情報分析與任務總管 Repo**，資料收集源自維護者的日常技術閱讀，並在此公開供社群自由參考。所有 Agent（Claude Code、Codex、Antigravity、Hermes 等）在收到文章分析請求、查詢待辦事項、或回寫任務完成狀態時，必須遵守本檔案定義的協定。

---

## 1. 目錄結構

```text
C:\GitHub\ai-inbox\
├── README.md                        # 總表（任務表、索引與知識圖譜由腳本產生）
├── AGENTS.md                        # 本規範：給各 Agent 的標準讀寫與狀態更新協定
├── templates/
│   └── article-analysis.md          # 單篇文章分析與待辦拆解的標準範本
├── notes/
│   └── YYYY-MM-DD-<slug>.md         # 每一篇 AI 文章的分析任務結果（一檔一篇）★唯一資料來源
├── tools/
│   ├── task_cli.py                  # 任務佇列查詢 (next/show)、認領 (claim)、結案 (complete，DoD 要求的檔案須存在)、關閉 (close)
│   ├── build_index.py               # 從 notes/ 重產 README 的任務表與索引
│   ├── verify_inbox.py              # 契約驗證（CI 同款）
│   ├── verify_*.py（其餘 10 支）     # 外部裁判：檢查 docs/、templates/、assets/ 的規定結構（見 docs/external-judge-audit.md）
│   ├── _judge_common.py             # 外部裁判共用：剝註解、結構下限、報告輸出
│   ├── video_transcript.py          # 影片音訊下載 + faster-whisper (CUDA/CPU) 逐字稿轉寫（見 docs/video-transcript-howto.md）
│   ├── screen_privacy.py            # 截圖／OCR 隱私檢查（規範 docs/multimodal-screen-privacy-spec.md 的參考實作）
│   └── 其他功能型工具               # audit_fullstack_security、cli_to_skill、public_apis_indexer（各有對應 tests/test_*.py）
├── docs/                            # 技術規格、實測報告與 SOP 手冊（跨 Agent 派工指令見 docs/agent-dispatch.md）
├── assets/                          # 單檔 HTML / Generative UI / Canvas 互動成品
└── tests/                           # tools/ 的單元測試
```

> 健康存摺解析器與 Code-as-Video 影片工具已於 2026-10-25 獨立成 [`SanHsien/health-bank-toolkit`](https://github.com/SanHsien/health-bank-toolkit) 與 [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)，相關筆記與任務一併移出；要改那些工具請到對應 repo。

**資料流（單一資料來源）**：任務的優先級、範圍、狀態、證據**只寫在筆記裡**；README 的
`<!-- BEGIN GENERATED -->` 區塊一律由腳本產生，禁止手改。

```text
notes/*.md ──build_index.py──▶ README.md（任務表 / 索引）
     └──────verify_inbox.py──▶ 格式、狀態一致性、ID 唯一、連結、機密、README 是否過期
```

---

## 2. 標準作業流程 (SOP)

### 流程 A：收到網路 / 社群 AI 文章，執行分析與拆解

當使用者提供網址、貼文內容或截圖要求分析時：

1. **建立單篇分析檔**：
   - 讀取 `templates/article-analysis.md` 範本。
   - 在 `notes/` 目錄下建立 `YYYY-MM-DD-<slug>.md`（`<slug>` 用英文小寫與連字號，簡明表達主題，例如 `2026-10-17-agent-memory-pruning.md`）。
   - 填寫 YAML frontmatter、核心觀點摘要、對現有環境（Skills / Hooks / 各專案）的價值評估，並拆解出**具體可驗證的待辦事項（Action Items）**。分析內容依 5W1H 結構初篩；若為包含明確實驗數據或論文發表的 AI 文章，主動填寫 CQR（Claim - Evidence - Reasoning）論證檢驗區塊。
   - 每個待辦事項編號格式為：`T-YYYYMMDD-XX`（例如 `T-20261017-01`）。若同一天有多篇文章，序號接續往後編，確保整個 Repo 內任務 ID 唯一。

   - 任務行必須完全照範本格式：``- [ ] **`T-YYYYMMDD-XX`**｜**[優先級：高/中/低]** 標題``，底下至少有 `目標範圍` 與 `驗收標準（DoD）`。格式不符的任務總表讀不到，驗證會失敗。

2. **重產總表並驗證**：
   - `python tools/build_index.py`（更新 README 任務表與索引）
   - `python tools/verify_inbox.py`（必須 `[PASS]`）
   - 知識圖譜由 frontmatter 的 `cluster`、`cluster_role`、`short_title` 自動產生，不需手動編輯 README；漏填時 `verify_inbox.py` 會失敗。

3. **提交與推送**（驗證通過才提交）：
   - `python tools/verify_inbox.py && git add -A && git commit -m "docs(inbox): add analysis and tasks for <slug>" && git push`

---

### 流程 B：各 Agent 認領、實作與回寫狀態

當任何 Agent 被指派執行某項任務（或巡檢本總表挑任務實作）時，**優先使用 `tools/task_cli.py`** 以避免手動編輯行號或漏改 frontmatter `status`：

1. **查詢與認領任務**：
   - 先 `git pull --rebase --autostash` 確保拿到最新總表。
   - 查詢待辦佇列（按「🟡 進行中 → 高 → 中 → 低」排序）：
     ```bash
     python tools/task_cli.py next
     python tools/task_cli.py show T-YYYYMMDD-XX
     ```
   - 認領任務（自動在對應筆記插入 `- **狀態**：🟡 進行中`、同步筆記 `status: in-progress` 並更新 `README.md`）：
     ```bash
     python tools/task_cli.py claim T-YYYYMMDD-XX
     ```
2. **完成與驗收閉環**：
   - 任務在目標專案或全域設定實作完畢，且**實際執行測試或驗證通過**後，才可標記為完成（嚴禁未驗證即標記完成）。
   - 執行結案指令（自動將 `[ ]` 改為 `[x]`、移除 `狀態` 行、填寫 `完成日期` 與 `實作紀錄 / 證據`、自動計算並更新筆記 frontmatter `status`，並重產 `README.md`）：
     ```bash
     python tools/task_cli.py complete T-YYYYMMDD-XX --evidence "<Commit SHA / 產出路徑 / 驗證輸出摘要>"
     ```
   - 若評估後決定不做／關閉：
     ```bash
     python tools/task_cli.py close T-YYYYMMDD-XX --reason "<關閉理由>"
     ```
3. **提交與推送**（驗證通過才提交）：
   - `python tools/verify_inbox.py && python -m unittest discover -s tests && git add -A && git commit -m "chore(tasks): mark T-YYYYMMDD-XX as done" && git push`
4. **開新 Session 派工與完工回報**：Antigravity、Claude、Codex、Hermes 四套桌面端開新對話、派工與回報的指令，見 [`docs/agent-dispatch.md`](docs/agent-dispatch.md)。

---

## 3. 寫作與分析鐵律

- **主動深挖並補齊官方 GitHub／原始碼**：文章若提及任何工具、框架、專案、論文或模型，**必須主動檢索其開源 GitHub 倉庫、文件站或 arXiv，將 Repository URL、架構特點與安裝指引直接補充至分析檔**，不用等維護者提醒。
  - *社群轉貼者說明*：若使用者提供的是純文字截圖或轉貼內容且未附原 PO，**不需要花時間去人肉搜尋轉貼者是誰**，author 直接填 `社群分享` 或專案作者即可，精力完全聚焦在技術本身、官方 Repo 與任務拆解。
  - *影片來源必取逐字稿*：若來源是 YouTube 等影片，**不可只看標題與說明欄就交差**。先用 `python -m yt_dlp` 抓字幕；若遇到 `HTTP 429` 或無字幕，直接執行 `python tools/video_transcript.py <網址> --out <暫存目錄>`（本機已配妥 RTX 3060 CUDA 加速與 `faster-whisper`），完整步驟與踩坑紀錄見 [`docs/video-transcript-howto.md`](docs/video-transcript-howto.md)。
- **規劃必須詳盡具體（拒絕空泛）**：分析時重點永遠是「這篇文章的哪個設計／技巧，能解決什麼痛點，或改進哪個具體專案／Skill？」。拆解任務必須包含目標範圍、具體實作步驟與嚴格的 DoD 驗收標準，不留空泛概念。
- **待辦事項必須可驗收**：不要寫「研究如何優化 prompt」這種無邊界任務；要寫「在 `~/.gemini/config/skills/xxx/SKILL.md` 加入 YYY 檢查步驟，並用 ZZZ 案例實測通過」。
- **DoD 要寫出產出檔路徑，未達成就不算完成**：DoD 若要求產出本 repo 的檔案，用反引號標出路徑（如 `docs/x.md`），`task_cli.py complete` 與 `verify_inbox.py` 會檢查它存在。DoD 裡的任何一項沒做到（例如「實測」只做了評估），就不可結案；證據裡的「限制」若落在 DoD 範圍內，等於未完成。
- **不再新增關鍵字型外部裁判驗證器**：理由與替代做法見 [`docs/external-judge-audit.md`](docs/external-judge-audit.md) 第 5 節。
- **查證個人 Fork 與遠端倉庫嚴禁依賴搜尋引擎斷言（必須直連真實 URL / API 驗證）**：
  - *教訓實例（2026-10-20）*：使用者詢問是否已 Fork `public-apis`，Agent 僅憑 `search_web` 搜尋 `site:github.com/SanHsien "public-apis"` 的空結果便妄下斷言稱「尚未 Fork」，實際上 `https://github.com/SanHsien/public-apis` 早已存在。第三方搜尋引擎爬蟲存在嚴重延遲與索引死角，**查證個人資產、遠端 Repo 或 Fork 狀態時，必須直接對目標 URL（如 `https://github.com/SanHsien/<repo>`）發起真實 HTTP 請求（如 read_url_content 或 curl）或調用 GitHub API 驗證，未經驗證真實網址前嚴禁聲稱不存在**。
- **若文章經評估無須落地**：如實記錄分析結論，YAML frontmatter 的 `status` 設為 `archived`，不強湊無意義的待辦事項。

---

## 4. 公開倉庫安全與隱私防堵鐵律（公開防護線）

本 Repo 為**公開倉庫（Public Repository）**，為防範個人隱私、專利與內部專案資訊外洩，所有 Agent 必須嚴格執行以下防護：

1. **私有 repo 寫真名並標「（私有）」，內容不外流**：
   - 寫法：`` `SanHsien/agent-assets`（私有） ``。讀者一看就知道連結打不開，Agent 也不用查對照表。
     （2026-10-26 起取代舊的 `[Private Repo: 別名]` 寫法；名稱外洩頂多讓人猜到用途，進不去也看不到內容。）
   - 私有 repo 的內部程式碼、未公開的商業邏輯不貼進來，只寫抽象的驗證結論（例如：`單元測試 15/15 通過`）。
   - **本機家目錄路徑不寫真實帳號**：`C:\Users\<帳號>\...`、`/Users/<帳號>/...`、`/home/<帳號>/...` 改寫成
     `%USERPROFILE%\...` 或 `~/...`；指令輸出裡的也要改。`verify_inbox.py` 會擋。
     範例用的佔位帳號（`<Username>`、`username`、`admin`、`test`、`me`、`x`）不擋。
2. **絕對零機密（Zero Secrets）**：
   - 任何 API Key、Token、私鑰、內部帳號密碼、主機 IP 或私人憑證，**絕對不可寫入**任何 `.md` 檔案、Commit 訊息或代碼範例中。
3. **版權與隱私過濾**：
   - 若來源為付費內容、內部研討截圖或私人對話，**不可直接摘錄完整原文**，僅可提煉抽象的架構概念與實作邏輯。
   - 所有公開分析必須保持出處連結（Attribution）與作者標記。
4. **本機截圖、錄影與 OCR**：擷取本機畫面給 AI 看、或把截圖／錄影放進 repo 當證據之前，遵循 [`docs/multimodal-screen-privacy-spec.md`](docs/multimodal-screen-privacy-spec.md)（敏感視窗不截、洩鑰即丟、48 小時內清除）。
   - 截圖前用 `python tools/screen_privacy.py --title "<視窗標題>" --app <程式名>` 判斷：`blocked`／`nocap` 不可截圖。
   - 截圖後先 OCR，再用 `python tools/screen_privacy.py --ocr-file <OCR 文字檔>` 檢查：結果是 `drop_image`（含金鑰、身分證、卡號，或敏感關鍵字達門檻）就刪掉這張圖，不可送出、不可提交。
   - 規則以 `tools/screen_privacy.py` 為準；要改規則先在 `tests/test_screen_privacy.py` 補反例。

## 路線圖

- `ROADMAP.md` 是本 repo 後續工作的單一真相源。完成或新增工作時，在同一個 commit 更新它：做完的列刪掉、新工作加進去。不要在其他文件另列待辦。
