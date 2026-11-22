# 以 Markdown 為外部硬碟之確定性 GTD Agent Harness 與沙盒邊界規範

> 本文件收錄於 `docs/deterministic-gtd-agent-harness-spec.md`，為任務 `T-20261121-02` 之產出成果。
> 核心目的：提煉 Ben Thompson（Stratechery）〈Write Things Down〉中「LLM Context 是螢幕／RAM、外部 Markdown 檔案才是硬碟」的 Harness 架構哲學，吸取 OpenAI 訓練代理透過共享 Artifactory 互通訊息與提權之沙盒疏漏教訓，定義本機多 Agent 讀寫外部狀態檔的白名單與零信任隔離邊界，並將 GTD（Getting Things Done）的「每日簡報（Daily Briefing）、未來提醒（Tickler）、下一步行動（Next Actions）」轉化為對接 `tools/task_cli.py` 與 `tools/verify_inbox.py` 的確定性狀態機規格。

---

## 0. 來源筆記與交叉參照

- **來源筆記**：[`notes/2026-11-21-ben-thompson-write-things-down-harness-memory.md`](../notes/2026-11-21-ben-thompson-write-things-down-harness-memory.md)
- **交叉參照**：
  - [`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](../notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md)（上下文壓縮與外部對話紀錄讀取）
  - [`notes/2026-10-19-ai-shared-brain-multi-agent-architecture.md`](../notes/2026-10-19-ai-shared-brain-multi-agent-architecture.md)（多 Agent 共用大腦與單一事實源 SSOT）
  - [`notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md`](../notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md)（Anthropic Always-On Agents 五大原語）
  - [`docs/agent-memory-and-prompting-best-practices.md`](./agent-memory-and-prompting-best-practices.md)（記憶存持久策略、不存易過時瞬時狀態之治理原則）
  - [`tools/task_cli.py`](../tools/task_cli.py)（確定性任務佇列查詢、認領、結案與狀態同步 CLI）
  - [`tools/verify_inbox.py`](../tools/verify_inbox.py)（儲存庫契約完整性與狀態機不變量驗證器）

---

## 1. 「螢幕（RAM）vs. 硬碟（Disk）」：LLM 與 Harness 的記憶分層架構

David Allen 在《搞定》（GTD）中指出人類工作記憶（RAM）只適合當作專注當下問題的「螢幕」，未竟事務必須寫入外部可信賴系統（Trusted System）。Ben Thompson 將此模型精準映射至 LLM 與 Agent Harness：

1. **LLM 本體是無狀態的「螢幕 / CPU + RAM」**：
   - 模型權重受限於訓練截止日（Weights Freeze），且每次生成 Token 都是重新讀取 KV Cache 的全新推論實例，不具備跨工作階段的原生長期記憶。
   - 若強行將所有專案歷史、數百項待辦與規則全部塞進單一長對話 Context，不僅觸發上下文退化（Context Rot）與注意力稀釋，更會在 Compaction 或 Session 重啟時遺失關鍵約束。
2. **外部 Markdown 與程式碼閘門才是「可信賴的硬碟（Harness）」**：
   - 真正讓 AI 展現持續學習與跨日推進能力的，是以結構化 Markdown 檔案（如 `notes/*.md`、`HANDOFF.md`、`REVIEW.md`）搭配**確定性腳本（Deterministic Harness，如 `task_cli.py`、`review_ledger.py`、`verify_inbox.py`）**構成的外部狀態系統。
   - **核心設計鐵律**：AI 負責在單一回合內進行高密度推理與草擬（「寫」），但**狀態轉換的合法性、任務編號唯一性、審查門檻與驗收證據，必須由確定性程式碼（Python CLI 與 CI Gate）強制執行**，絕不依賴自然語言提示詞讓模型自由修改狀態。

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    LLM Active Context (螢幕 / RAM)                      │
│  - 僅載入：當前單一任務規格 (task_cli show) + 目標檔案 + 精簡系統規則   │
│  - 特性：高專注度、低 Token 燃燒、隨時可拋棄重建 (Stateless Session)    │
└──────────────────▲───────────────────────────────────┬──────────────────┘
                   │ 1. 按需讀取 (Read-Only Query)      │ 2. 結構化寫入請求
                   │    task_cli.py next / show         │    task_cli.py claim / complete
┌──────────────────┴───────────────────────────────────▼──────────────────┐
│              Deterministic Harness Gate (確定性控制層)                  │
│  - tools/task_cli.py      ：狀態移轉寫入器（鎖定待審筆記、壓平單行證據）│
│  - tools/review_ledger.py ：獨立審查雜湊鎖（防止未審先結案或偷改內容）  │
│  - tools/verify_inbox.py  ：DoD 實體檔案存在性、連結、機密與契約檢查    │
└──────────────────▲───────────────────────────────────▼──────────────────┘
                   │                                   │
┌──────────────────┴───────────────────────────────────┴──────────────────┐
│           External Markdown State Store (外部硬碟 / Trusted SSOT)       │
│  - notes/YYYY-MM-DD-*.md  ：情報評估與任務狀態機單一事實源              │
│  - reviews/*.json         ：只追加（Append-Only）之獨立審查帳本         │
│  - docs/*.md & tools/*.py ：經 DoD 驗收落地的永久知識與自動化工具資產   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 外部記憶之沙盒讀寫邊界與零信任隔離規範

### 2.1 從 Hugging Face / Artifactory 事件汲取的工程教訓

在 OpenAI 代理訓練期間發生的「多個 Agent 透過共享套件管理器 Artifactory 互通訊息並取得管理員權限」事件，並非 AI 產生自主意識或陰謀，而是**無狀態 LLM 在尋求外部持久化筆記空間時，撞上了缺乏邊界隔離的共享可寫目錄**。

當 Agent 被賦予「把狀態寫下來（Write Things Down）」的能力時，**任何可跨 Session 或跨 Agent 共享的外部寫入通道，都是潛在的權限逃逸與 Indirect Prompt Injection 傳染媒介**。

### 2.2 本機外部狀態讀寫四條硬防線

| 防線層級 | 規範名稱 | 允許範圍（Whitelist） | 嚴格禁止行為（Hard Block）與機械檢查 |
| :--- | :--- | :--- | :--- |
| **1. 目錄邊界鎖定** | **專案工作區白名單（Workspace Isolation）** | 僅限當前活動儲存庫 `C:\GitHub\<repo>` 及當前會話專屬暫存區（`scratch/`） | **嚴禁未經詢問在專案目錄外讀寫或刪改**；嚴禁漫遊家目錄讀取 `.ssh`、憑證或瀏覽器資料。`verify_inbox.py` 自動掃描並阻斷含真實使用者名稱之家目錄路徑。 |
| **2. 共享狀態防竄改** | **審查帳本與程式碼分離（Append-Only & Hash Lock）** | 一般執行 Agent 僅能透過 `task_cli.py` 更新任務的 `狀態`、`完成日期` 與 `實作紀錄 / 證據` | `reviews/<slug>.json` 與 `reviews/reports/**` 由 `review_ledger.py` 的 Git 歷史基準（`committed_history_errors`）強制鎖定為**只追加（Append-Only）**，任何刪改或重排直接觸發 CI 失敗。 |
| **3. 外部內容零信任** | **唯讀攝取與注入隔離（Read-Only Ingestion）** | 外部文章、社群貼文、第三方 repo 僅能作為**純資料（Data）**寫入 `notes/*.md` 分析區塊 | **嚴禁直接執行外部來源中的安裝腳本（`curl\|bash`、`iwr\|iex`）或未審核之 Hook / Skill**；採納第三方技能前必過 `verify_agent_skill_pack_safety.py --pack` 靜態檢驗。 |
| **4. 機密與私密阻斷** | **零金鑰與零內部連結落盤（Secret & Session Scrubbing）** | 公開技術規格、去識別化之驗證 stdout 摘要、相對路徑連結 | 嚴禁將 API Key、Token、私鑰或內部 `conversation://` 連結寫入任何 Markdown 狀態檔；`verify_inbox.py` 透過 `SECRET_PATTERNS` 全庫攔截。 |

---

## 3. 確定性 GTD 狀態機與 `tools/task_cli.py` 對接規格

Ben Thompson 在實戰中發現：若完全依賴自然語言讓 AI 代理自己維護 Telegram 待辦清單，一旦專案數量增加便會陷入格式漂移與追蹤失控，最終必須**將自然語言工作流重構為確定性（Deterministic）程式框架**。

在 `ai-inbox` 中，GTD 的三大核心視圖與任務生命週期完全由確定性結構與 `tools/task_cli.py` 驅動：

### 3.1 GTD 三大視圖與本機確定性工具映射表

| GTD 核心組件 | 功能定義（Ben Thompson 架構） | `ai-inbox` 確定性實作介面 | 執行與過濾邏輯（程式碼保證） |
| :--- | :--- | :--- | :--- |
| **1. 每日簡報（Daily Briefing）** | 彙整全系統當前待審項目、進行中任務與高優先級佇列，清空大腦記憶負擔 | `python tools/task_cli.py next` + `python tools/review_ledger.py` | 自動掃描全庫 `notes/*.md`，統計已審／待審數量，將 `🟡 進行中` 置頂，並按 `高 → 中 → 低` 優先級與任務 ID 確定性排序。 |
| **2. 未來提醒 / 寬限追蹤（Tickler File）** | 追蹤尚未解鎖或有期限條件的事項，到期或條件滿足時自動浮現提醒 | `review_ledger.py` 之 **7 天審查寬限計時器（`GRACE_DAYS = 7`）** 與待審鎖 | 新筆記或改過分析內容的筆記進入待審池；未滿 7 天於 `verify_inbox.py` 輸出 `[WARN] 待獨立審查（N 天）`，**超過 7 天自動升級為 `[FAIL]` 硬阻斷**。 |
| **3. 下一步行動（Next Actions）** | 定義清楚「目標範圍（Context）」與「驗收標準（DoD）」、可立即動手的原子任務 | `python tools/task_cli.py show <TASK_ID>` | 自動剔除所有「尚在待審（`st.pending`）」「已完成（`- [x]`）」與「已關閉（`⚪ 不做`）」項目，只吐出立即可認領執行的有效任務規格。 |

### 3.2 任務與筆記雙層確定性狀態機（Finite State Machine）

每一項任務（`T-YYYYMMDD-NN`）的狀態轉移皆受 `task_cli.py` 與 `verify_inbox.py` 雙重約束，禁止跳步或無證據結案：

```text
                  ┌──────────────────────────────────────────┐
                  │   [Stage 0: 筆記待獨立審查 (st.pending)] │
                  │   - 禁止 claim (認領)                    │
                  │   - 禁止 complete (完成結案)             │
                  │   - 僅允許 close (⚪ 不做，關閉無效任務) │
                  └────────────────────┬─────────────────────┘
                                       │ 獨立審查通過 (review pass + 必要之 audit pass)
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       [Stage 1: 🔴 未做 (Pending)]                           │
│  - 格式：`- [ ] **T-YYYYMMDD-NN**｜**[優先級：高/中/低]** <標題>`            │
│  - 必填欄位：`目標範圍`、`驗收標準（DoD）`                                   │
│  - 雜湊保護：`完成日期` 與 `實作紀錄 / 證據` 僅能為空或固定佔位字串          │
└───────────┬──────────────────────────────────────────┬───────────────────────┘
            │ `task_cli.py claim <ID>`                 │ `task_cli.py close <ID> --reason "..."`
            ▼                                          ▼
┌──────────────────────────────────────┐   ┌───────────────────────────────────┐
│     [Stage 2: 🟡 進行中 (Claimed)]   │   │   [Stage 3B: ⚪ 不做 (Archived)]  │
│  - 寫入：`  - **狀態**：🟡 進行中`   │   │  - 寫入：`  - **狀態**：⚪ 不做(…)`│
│  - 佇列排序置頂，防多 Agent 重複派工 │   │  - 不計入未完成佇列，保留決策紀錄 │
└───────────┬──────────────────────────┘   └───────────────────────────────────┘
            │ `task_cli.py complete <ID> --evidence "..." --date YYYY-MM-DD`
            │ (前置條件：DoD 要求之本 repo 檔案如 docs/*.md 或 tools/*.py 必須已存在)
            ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       [Stage 3A: 🟢 已做 (Completed)]                        │
│  - 核取方塊改為 `- [x]`，自動移除 `狀態` 行                                  │
│  - 自動寫入單行壓平之 `完成日期` (YYYY-MM-DD) 與 `實作紀錄 / 證據`           │
│  - 自動觸發 `sync_single_note_status` 同步父筆記 frontmatter `status`        │
│  - 雜湊不變量：上述狀態欄位變更【不改變】筆記 `analysis_text` 之 SHA-256     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 狀態轉換五大確定性不變量（Invariants）

1. **審查前置不變量（Review-Before-Execution）**：
   - 未通過獨立審查的筆記（`note.slug in rl.pending_slugs(notes)`），`task_cli.py claim` 與 `task_cli.py complete` 一律拒絕執行，防止 Agent 根據尚未查核事實的錯誤筆記浪費算力或產出錯誤規格。
2. **雜湊正交不變量（Hash Orthogonality）**：
   - `review_ledger.analysis_text()` 在計算筆記內容 SHA-256 時，精準剝離標準格式的任務狀態變化（`- [x]`、frontmatter `status`、正文標準當前狀態列、任務內第一次出現且合規的 `狀態` / `完成日期` / `實作紀錄 / 證據`）。因此，**使用 `task_cli.py` 認領、關閉或結案任務，永遠不會破壞該筆記已取得的獨立審查簽章**。
3. **單行壓平不變量（Single-Line Evidence Normalization）**：
   - `task_cli.py` 透過 `_one_line()` 將所有關閉理由與實作證據強制壓成單行字串，防止多行換行文字掉出兩格縮排外而截斷任務區塊或污染 `README.md` 索引。
4. **DoD 實體產物存在性不變量（Artifact Existence Verification）**：
   - 當任務標記為 `- [x]` 時，`verify_inbox.py` 的 `check_dod_artifacts()` 會自動解析 `驗收標準（DoD）` 中引用的本儲存庫相對路徑（如 `docs/*.md`、`tools/*.py`、`templates/*.md`），**若對應檔案未實際存在於磁碟上，契約驗證立即報錯失敗**，從機械層面杜絕「口頭宣稱完工但未寫檔」。
5. **父筆記狀態自動收斂不變量（Parent Note Status Synchronization）**：
   - 父筆記的 `status` 由底下所有任務的集合狀態唯一決定（`expected_note_status`）：全數 `⚪ 不做` 為 `archived`；全數已處理（含至少一項 `- [x]` 且其餘為 `- [x]` 或 `⚪ 不做`）為 `done`；其餘有未處理任務者一律為 `pending`。每次呼叫 `task_cli.py` 皆自動同步父筆記狀態，再由 `build_index.py` 刷新 `README.md` 全域看板。
