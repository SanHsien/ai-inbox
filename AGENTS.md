# AI Inbox — 跨 Agent 任務總管規範 (AGENTS.md)

本倉庫 (`SanHsien/ai-inbox`，本地路徑 `C:\GitHub\ai-inbox`) 是維護者的 **個人 AI 情報分析與任務總管 Repo**，資料收集源自維護者的日常技術閱讀，並在此公開供社群自由參考。所有 Agent（Claude Code、Codex、Antigravity、Hermes 等）在收到文章分析請求、查詢待辦事項、或回寫任務完成狀態時，必須遵守本檔案定義的協定。

---

## 1. 目錄結構

```text
C:\GitHub\ai-inbox\
├── README.md                        # 總表（任務表、索引與知識圖譜由腳本產生）
├── private-aliases.json             # 私有 repo 公開別名表（真名在本機 private-aliases.local.json）
├── AGENTS.md                        # 本規範：給各 Agent 的標準讀寫與狀態更新協定
├── templates/
│   └── article-analysis.md          # 單篇文章分析與待辦拆解的標準範本
├── notes/
│   └── YYYY-MM-DD-<slug>.md         # 每一篇 AI 文章的分析任務結果（一檔一篇）★唯一資料來源
├── tools/
│   ├── build_index.py               # 從 notes/ 重產 README 的任務表與索引
│   └── verify_inbox.py              # 契約驗證（CI 同款）
└── tests/                           # tools/ 的單元測試
```

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

當任何 Agent 被指派執行某項任務（或巡檢本總表挑任務實作）時：

1. **開始實作**：
   - 先 `git pull --rebase` 確保拿到最新總表。
   - 在筆記中該任務底下加一行 `  - **狀態**：🟡 進行中`，重跑 `build_index.py`。
2. **完成與驗收閉環**：
   - 任務在目標專案或全域設定實作完畢，且**實際執行測試或驗證通過**後，才可標記為完成（嚴禁未驗證即標記完成）。
   - 只改對應的 `notes/YYYY-MM-DD-<slug>.md`：
     - 將該項任務的 `[ ]` 改為 `[x]`，移除 `狀態` 行，補上 `  - **完成日期**：YYYY-MM-DD` 與 `  - **實作紀錄 / 證據**：<Commit SHA / PR / 路徑>`。
     - 調整 frontmatter `status`：全部完成 `done`、部分完成或有進行中 `in-progress`（驗證器會檢查一致性）。
   - 執行 `python tools/build_index.py`，任務會自動從「🔴 未做」移到「🟢 已做」，索引計數同步更新。
3. **提交與推送**（驗證通過才提交）：
   - `python tools/verify_inbox.py && git add -A && git commit -m "chore(tasks): mark T-YYYYMMDD-XX as done" && git push`

---

## 3. 寫作與分析鐵律

- **主動深挖並補齊官方 GitHub／原始碼**：文章若提及任何工具、框架、專案、論文或模型，**必須主動檢索其開源 GitHub 倉庫、文件站或 arXiv，將 Repository URL、架構特點與安裝指引直接補充至分析檔**，不用等維護者提醒。
  - *社群轉貼者說明*：若使用者提供的是純文字截圖或轉貼內容且未附原 PO，**不需要花時間去人肉搜尋轉貼者是誰**，author 直接填 `社群分享` 或專案作者即可，精力完全聚焦在技術本身、官方 Repo 與任務拆解。
- **規劃必須詳盡具體（拒絕空泛）**：分析時重點永遠是「這篇文章的哪個設計／技巧，能解決什麼痛點，或改進哪個具體專案／Skill？」。拆解任務必須包含目標範圍、具體實作步驟與嚴格的 DoD 驗收標準，不留空泛概念。
- **待辦事項必須可驗收**：不要寫「研究如何優化 prompt」這種無邊界任務；要寫「在 `~/.gemini/config/skills/xxx/SKILL.md` 加入 YYY 檢查步驟，並用 ZZZ 案例實測通過」。
- **查證個人 Fork 與遠端倉庫嚴禁依賴搜尋引擎斷言（必須直連真實 URL / API 驗證）**：
  - *教訓實例（2026-10-20）*：使用者詢問是否已 Fork `public-apis`，Agent 僅憑 `search_web` 搜尋 `site:github.com/SanHsien "public-apis"` 的空結果便妄下斷言稱「尚未 Fork」，實際上 `https://github.com/SanHsien/public-apis` 早已存在。第三方搜尋引擎爬蟲存在嚴重延遲與索引死角，**查證個人資產、遠端 Repo 或 Fork 狀態時，必須直接對目標 URL（如 `https://github.com/SanHsien/<repo>`）發起真實 HTTP 請求（如 read_url_content 或 curl）或調用 GitHub API 驗證，未經驗證真實網址前嚴禁聲稱不存在**。
- **若文章經評估無須落地**：如實記錄分析結論，YAML frontmatter 的 `status` 設為 `archived`，不強湊無意義的待辦事項。

---

## 4. 公開倉庫安全與隱私防堵鐵律（公開防護線）

本 Repo 為**公開倉庫（Public Repository）**，為防範個人隱私、專利與內部專案資訊外洩，所有 Agent 必須嚴格執行以下防護：

1. **嚴禁私有專案細節外流**：
   - 當實作完成回寫 `README.md` 的「🟢 已做」或 `notes/` 內的驗收證據時，若修改的是維護者的**私人 Repo** 或**未公開專案**：
     - **禁止**貼出私有 Repo 的 GitHub URL、內部專案名稱或敏感路徑。
     - **統一寫法**：標註為 `[Private Repo: <別名>] 通過驗證` 或 `[Local Config] 已整合`，僅附上抽象的驗證結論（例如：`單元測試 15/15 通過`），不附內部代碼與敏感路徑。
   - **私有 repo 別名對照（各 Agent 必讀）**：
     - 公開別名表：`private-aliases.json`（別名 → 用途，會提交）。
     - 真名對照表：`private-aliases.local.json`（別名 → `owner/repo`，已 gitignore，只存在維護者本機 `C:\GitHub\ai-inbox\`）。
     - **讀**：看到 `[Private Repo: 個人記憶庫]` 這類標記，查本機對照表取得真實 repo 再動工；本機檔不存在就詢問維護者，不要猜。
     - **寫**：提到私有 repo 一律寫 `[Private Repo: <別名>]`。新的私有 repo 先在兩個檔各加一筆（公開檔只寫別名與用途），再使用。
     - `verify_inbox.py` 會擋未登記的別名；本機有對照表時，真名出現在任何會提交的檔案也會擋下。
2. **絕對零機密（Zero Secrets）**：
   - 任何 API Key、Token、私鑰、內部帳號密碼、主機 IP 或私人憑證，**絕對不可寫入**任何 `.md` 檔案、Commit 訊息或代碼範例中。
3. **版權與隱私過濾**：
   - 若來源為付費內容、內部研討截圖或私人對話，**不可直接摘錄完整原文**，僅可提煉抽象的架構概念與實作邏輯。
   - 所有公開分析必須保持出處連結（Attribution）與作者標記。
