---
id: 2026-11-02-google-elephant-goldfish-model-software-design-review
title: "Google 官方開源 Elephant-Goldfish Model (EGM) 架構解構：大象長記憶規劃、金魚零上下文對抗審查與軟體設計工業化"
source_url: "https://www.threads.com/@whaleagent/post/DfMDAdOk5BD"
source_platform: "Threads (@whaleagent)"
author: "WhaleAgent (@whaleagent) / Google (Dave Rensin 等)"
analyzed_at: 2026-11-02
analyzed_by: "Antigravity"
status: pending
cluster: 1
cluster_role: "Google大象金魚模型與零記憶審查"
short_title: "Google大象金魚模型EGM軟體設計審查"
tags:
  - google
  - elephant-goldfish-model
  - egm
  - design-first
  - zero-context-review
  - fresh-subagents
  - multi-agent
  - claude-code
  - antigravity
  - codex
---

# Google 官方開源 Elephant-Goldfish Model (EGM) 架構解構：大象長記憶規劃、金魚零上下文對抗審查與軟體設計工業化

- **來源連結**：[Threads 原文分享 (@whaleagent)](https://www.threads.com/@whaleagent/post/DfMDAdOk5BD) ｜ [短網址](https://www.threads.com/share/BATMHSMqgj/)
- **核心作者**：WhaleAgent（@whaleagent）
- **發明者與原創文獻**：Dave Rensin（Google 傑出工程師，《Elephants & Goldfish》設計論綱）
- **官方開源專案**：[google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model)（官方網站 [egm.dev](https://egm.dev)，Star: 8,600+）
- **分析主題**：解構 Google 正式開源之軟體工程 AI 協同外掛「**Elephant-Goldfish Model（EGM，大象-金魚模型）**」。剖析每日支撐數千名 Google 工程師的「設計先行（Design-first）」核心範式——由具備深厚歷史記憶的「**大象（Elephant）**」負責梳理需求、記錄決策並草擬系統規格，再派發多個**完全不帶對話歷史、純粹依據文件與源碼進行挑剔的「金魚（Goldfish）」零記憶子代理**進行對抗式盲審，嚴禁跳過設計直接寫代碼。深入解析其跨 Antigravity（`agy`）、Claude Code 與 Codex 的 7 大專用工作流技能（Brainstorm、Draft、Review、Resolve、Bootstrap、Review-loop、Drift-report），推導企業級 AI 研發架構的工程落地標準。
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（Claude Code 四級模型分工架構解構）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（四角色動態調用原則：架構師、實現者、審查員與除錯專家）
  - [`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)（Thorsten Ball 15 條 Agent 實戰哲學）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（Going Li 四 Agent 派工與五路工具流）

---

## 1. 來源摘要與背景脈絡

### 1.1 傳統 AI 輔助開發的「跳躍實作病」
在當前大模型輔助開發中，最嚴重的通病是「**未經審慎架構設計，直接敲代碼**」：
- 使用者提出一個大型功能需求，Agent 在幾秒鐘內直接開工修改 10 幾個檔案。
- **會話偏誤（Context Anchoring）**：在同一個長會話中，模型受先前聊天脈絡與妥協方案干擾，無法以客觀視角審視自己提出的方案是否有安全漏洞或架構缺陷。
- **代碼越界與無效修補**：一旦架構方向錯誤，後續測試紅燈便會引發「補丁疊補丁（whack-a-mole）」的崩潰循環。

### 1.2 Google 內部工程實踐：EGM 三方制衡體系
Google 傑出工程師 Dave Rensin 與研發團隊將 Google 內部成熟的「設計審查（Design Review）」體系轉化為 AI 開源外掛 `google/elephant-goldfish-model`：
- **核心哲學**：**「Design with an elephant. Review with a goldfish.（與大象一同設計，用金魚進行審查）」**。
- 將架構設計階段與代碼實作階段嚴格物理切分，並透過子代理的「記憶隔離」達成真正客觀的架構壓力測試。

---

## 2. 架構核心解構與技術深度

```text
                                  ┌───────────────────────────┐
                                  │      人類工程師 (You)      │
                                  │  (裁決權衡、最終批准設計)  │
                                  └─────────────┬─────────────┘
                                                │
                           1. 需求探索與架構討論 (egm-brainstorm)
                                                ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                   大象代理人 (The Elephant)                 │
       │  - 具備深厚專案背景 (Deep Context)                           │
       │  - 記住過往所有討論、取捨歷程與環境約束                     │
       │  - 負責起草：concepts_brief.md 與 design_draft.md           │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         2. 產出規格草稿，發起五階段盲審
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                  金魚審查員 (The Goldfish)                  │
       │  - 嚴格物理隔離！零對話歷史 (Zero Earlier Context)           │
       │  - 只閱讀：設計草稿文件 + 關聯原始碼                        │
       │  - 職責：找出「未明言假設」、規格模糊處、破壞性邊界案例     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         3. 彙整反饋與修正 (egm-resolve)
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                  正式核准規格 (Approved Spec)               │
       │  - 歸檔於 docs/designs/                                      │
       │  - 此時才允許調用 Coding Agent 進行代碼實作                  │
       └─────────────────────────────────────────────────────────────┘
```

### 2.1 三大主體角色與職責邊界（The Triad）
1. **大象（Elephant）**：
   - **上下文範圍**：完整的專案脈絡、前置需求分析、架構決策與對話歷史。
   - **責任**：與工程師深入探討功能邊界，進行概念發散與收斂，並撰寫結構化設計規範文檔。
2. **金魚（Goldfish）**：
   - **上下文範圍**：**僅限草稿文檔與被引用的原始碼檔案，嚴禁傳入前段聊天紀錄**！
   - **責任**：如同第一次看這個 PR 的資深審查員（Fresh-eyes Reviewer）。因為完全沒有看過先前的妥協討論，能夠一眼看穿設計文檔中自相矛盾、隱藏假設（Unstated Assumptions）與邏輯斷層。
3. **人類工程師（You）**：
   - **責任**：軟體架構最終負責人。在審查意見衝突時做出決策（Trade-offs），批准後才交付編碼。

### 2.2 跨三大主流平台的全覆蓋安裝體系
EGM 外掛支援目前三大主流 Agent 平台：
- **Antigravity CLI / App**：
  ```bash
  agy plugin install https://github.com/google/elephant-goldfish-model
  # 呼叫指令：/egm:egm-brainstorm、/egm:egm-draft、/egm:egm-review
  ```
- **Claude Code**：
  ```bash
  claude plugin marketplace add google/elephant-goldfish-model
  claude plugin install egm@egm
  ```
- **Codex**：
  ```bash
  codex plugin marketplace add google/elephant-goldfish-model
  codex plugin add egm@egm
  ```

### 2.3 七大工作流技能矩陣（EGM 7-Skill Matrix）

| 技能名稱 | 指令別名 | 核心職責與產出物 | 執行約束與子代理調用 |
| :--- | :--- | :--- | :--- |
| **Brainstorm** | `egm-brainstorm` | 概念碰撞與可行性探索，產出 `concepts_brief.md` | 大象主筆，引入 Fresh Reviewer 挑戰提議 |
| **Draft** | `egm-draft` | 將 Brief 擴展為正式規格書 `design_draft.md` | 每寫完一個章節主動暫停，在對話中向使用者確認 |
| **Review** | `egm-review` | 啟動金魚子代理進行五階段標準化審查 | **強制調用 Fresh Subagents**；若平台不支援則終止 |
| **Resolve** | `egm-resolve` | 逐條審視金魚審查員的缺陷發現並決定修改方式 | 大象與人類共同對話收斂 |
| **Bootstrap** | `egm-bootstrap` | 為既有代碼庫快速逆向梳理架構與補齊規範文件 | 快速建立系統 Baseline 文檔 |
| **Review-loop** | `egm-review-loop` | 針對特定任務（如資安、效能、API）執行專項審查組 | 可配置化審查員小組 |
| **Drift-report** | `egm-drift-report` | 比對已簽入的設計文檔與目前最新原始碼的偏離程度 | 檢驗文檔是否失真過期（Code-Doc Drift） |

### 2.4 五階段金魚審查矩陣（Five-Stage Goldfish Review）
在 `egm-review` 中，零記憶金魚審查員依序檢驗五大面向：
1. **完整性（Completeness）**：關鍵使用者歷程（CUJ）是否有未覆蓋的情境？
2. **清晰度（Clarity）**：是否存在模糊用語、未說明的術語或含糊的時序定義？
3. **現狀適配度（Codebase Fit）**：與既有系統設計模式、命名空間與資料結構是否衝突？
4. **實作可行性（Implementation Plan）**：拆解的步驟是否可驗證？是否存在不可逆之高風險變更？
5. **假設審查（Assumption Audit）**：文檔是否把「期望行為」當成了「保證前提」？

---

## 3. 對現有系統的啟發與落差分析

| 評估維度 | Google EGM 範式特徵 | 本知識庫與現有 Agent 體系現狀 | 落地借鑑與改進方向 |
| :--- | :--- | :--- | :--- |
| **審查記憶隔離** | 物理級隔離對話歷史，審查員僅讀規格與源碼 | 目前常見的 Subagent 派工常直接繼承或傳遞完整上下文，帶有先入為主的偏誤 | 實施「金魚零上下文審查協定（Zero-Context Review Protocol）」，杜絕會話記憶污染 |
| **設計先行硬約束** | 未通過 `egm-review` 並核准前，嚴禁產生任何功能代碼 | Agent 接獲任務容易急於改代碼，做錯難以逆向回收 | 確立大型非平凡功能「Spec 審查綠燈後方可編碼」的工程硬閘門 |
| **規格文檔防腐** | `egm-drift-report` 週期性比對代碼與設計文檔之偏離 | 既有文檔撰寫後往往閒置，難以及時感知代碼重構後的架構漂移 | 引入代碼與文檔漂移檢驗工具（Drift Detector） |
| **平台中立性** | 一套架構原生適配 Antigravity、Claude Code 與 Codex | 很多規範僅限於特定 CLI 或環境指令 | 規範標準化的 EGM Prompt 範本與技能接口，相容全平台 |

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將 Google 官方開源之 Elephant-Goldfish Model 軟體設計審查體系納入工程落地，規劃以下 3 項任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261102-04`**｜**[優先級：高]** 撰寫「大象-金魚架構（EGM）規格手冊：長上下文架構大腦、零記憶子代理審查與 CUJ 驅動設計流程」收錄於 `docs/elephant-goldfish-model-spec.md`
  - **目標範圍**：`docs/elephant-goldfish-model-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳述 Google EGM 三方角色（Elephant、Goldfish、Human）的職責邊界、上下文可見性矩陣與權責分離協議。
    2. 制定五階段金魚盲審流程（完整性、清晰度、代碼適配、實作可行性、假設審查）之具體驗核清單（Checklist）。
    3. 規範從 `concepts_brief.md` → `design_draft.md` → `docs/designs/` 簽入的標準工程流轉標準。
  - **驗收標準（DoD）**：產出 `docs/elephant-goldfish-model-spec.md`，具備標準 Markdown 結構與繁體中文規範；以 `Test-Path docs/elephant-goldfish-model-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261102-05`**｜**[優先級：中]** 實作「零記憶金魚審查員（Goldfish Reviewer）隔離上下文模擬與五階段審查驗證腳本」於 `tools/verify_egm_goldfish_review.py` 與單元測試
  - **目標範圍**：`tools/verify_egm_goldfish_review.py`、`tests/test_verify_egm_goldfish_review.py`
  - **具體做法**：
    1. 實作純 Python 版本的金魚審查檢驗工具 `tools/verify_egm_goldfish_review.py`，支援讀取設計文檔草稿與原始碼路徑。
    2. 實作上下文隔離校驗機制：確保傳遞給審查邏輯的資料封包中**完全不包含先前的 prompt 歷史與未經核准的聊天記錄**。
    3. 實作五階段結構化驗證規則引擎（檢查是否定義 CUJ、是否具備回滾機制、是否有未解之假設標註），輸出 PASS/FAIL 結構化報告。
    4. 撰寫單元測試套件 `tests/test_verify_egm_goldfish_review.py`，覆蓋有效設計草稿、缺失 CUJ 草稿、上下文洩漏攔截等邊界情境。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_egm_goldfish_review.py` 綠燈通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261102-06`**｜**[優先級：低]** 產出標準化「EGM 七大工作流技能（Brainstorm/Draft/Review/Resolve）Prompt 模板庫」收錄於 `templates/egm-workflow-prompts.md`
  - **目標範圍**：`templates/egm-workflow-prompts.md`
  - **具體做法**：
    1. 產出適用於 Antigravity、Claude Code 與 Codex 的 EGM 核心 Prompt 範本庫。
    2. 包含大象起草指令（`egm-brainstorm` / `egm-draft`）、金魚零記憶審查員系統提示詞（嚴禁角色偏誤、強制以挑剔視角找茬）、以及意見收斂協議（`egm-resolve`）。
    3. 提供代碼-文檔漂移檢驗（`egm-drift-report`）的對比檢查 Prompt。
  - **驗收標準（DoD）**：產出 `templates/egm-workflow-prompts.md`，結構清晰且包含變數替換標記；以 `Test-Path templates/egm-workflow-prompts.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
