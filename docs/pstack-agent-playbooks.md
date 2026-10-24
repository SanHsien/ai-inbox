# pstack 技能庫與 Playbooks 跨 Agent CLI 移植規格書

> **文件定位**：深度拆解前 SpaceX 首席工程師、Cursor 技術成員 Lauren Tan（`@poteto`）主導之 `pstack` 體系，定義核心路由器 `/poteto-mode`、5 大執行專題指導手冊（Playbooks）與專業輔助技能在三大主力 Agent CLI（Claude Code、Codex CLI、Antigravity）之跨平台移植規範與提示詞標準。

---

## 1. 來源依據與查證狀態表

依據任務嚴謹原則，所有引述與原始架構均建立在已查證之公開資料基礎上；涉及私有實作或未公開之內部細節明確標註「未查證」，嚴禁杜撰。

| 項目 | 來源名稱 / 連結 | 查證狀態 | 說明 |
| :--- | :--- | :--- | :--- |
| **原創者與背景** | Lauren Tan (`@poteto`) [YouTube 訪談解說](https://www.youtube.com/watch?v=b7-2w2T2Lqs) | `[已查證]` | 前 SpaceX 首席工程師、前 React Core Team、現 Cursor 工程師，曾於一個月內透過 AI Agent 協同交付數千 PR |
| **社群分享引述** | MengShyue Tsai [Threads 原文](https://www.threads.com/@mengshyue.tsai/post/DenWauFklqQ) | `[已查證]` | 介紹 pstack 核心哲學：以嚴格工程紀律（TDD、終端證據、對抗審查）防範 Vibe Coding 帶來的代碼膨脹 |
| **Cursor 官方插件** | [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) | `[已查證]` | 官方目錄結構含 `skills/poteto-mode/playbooks/`，內建 20+ 個場景手冊與專屬技能庫 |
| **社群開源移植** | [ericlitman/open-pstack](https://github.com/ericlitman/open-pstack) | `[已查證]` | 將 Cursor 專屬依賴解耦，提供通用 Agent CLI Runner 與跨模型 Provider 介面 |
| **內部實時 Telemetry** | SpaceX 內部遙測與閉源測試資料鏈 | `[未查證]` | 商業機密與受限內部架構，公開開源版本僅保留公開通用的工程防線原則 |
| **部分邊緣 Playbooks** | `babysit.md`, `eval.md` 等特殊微調內部參數 | `[未查證]` | 開源版本僅開放框架與介面定義，部分內部模型評測權重與 prompt 涉及內部策略未完全開源 |

---

## 2. 核心架構全景與 ASCII 概念可視化

`pstack` 的核心哲學是 **「證據先行軟體工程（Evidence-First Software Engineering）」**：
AI Agent 不應被當作盲目產出程式碼的打字機，而是必須在嚴密契約與測試防線下運作的初中級工程師夥伴。

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                      pstack 證據先行跨 Agent 協同生命週期                      │
├───────────────────────────────────────────────────────────────────────────────┤
│ 1. 意圖接收 (Intent Ingestion)                                                │
│    └─ 使用者指令：/poteto-mode <具體需求描述>                                 │
│                                                                               │
│ 2. 總控路由器 (Dispatcher: /poteto-mode)                                      │
│    ├─ 語意分類 ──▶ 鎖定對應 Playbook (Bug-fix / Feature / Refactor ...)        │
│    └─ 注入約束 ──▶ 建立強制任務清單 (Todo Checklist) 與專屬 Guardrails        │
│                                                                               │
│ 3. 模組化專業技能協同 (Specialized Modular Skills)                            │
│    ├─ /architect  ──▶ 跨模組架構設計、型別定義、資料流約束                     │
│    ├─ /arena      ──▶ 多方案平行競技、對抗性比較選優                           │
│    ├─ /swarm      ──▶ 大規模批次任務並行拆解委派                               │
│    ├─ /how & /why ──▶ 呼叫鏈溯源、既有設計意圖守護                             │
│    └─ /interrogate──▶ 跨模型對抗審查、邊界壓力測試                             │
│                                                                               │
│ 4. 嚴格執行期驗證閉環 (Runtime Verification Gate)                              │
│    ├─ 嚴禁未經執行的假設 ──▶ 必須回貼真實終端日誌輸出作為證據                  │
│    ├─ 嚴禁空殼函式 / TODO ──▶ 攔截 stub 函式與返回固定假資料                  │
│    └─ 紅燈證明 ──▶ 綠燈通過 ──▶ 零回歸保證 ──▶ 交付 Commit                     │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 總控動態路由器：`/poteto-mode` 規範

### 3.1 職責與前置防線
- **禁止直接編輯代碼**：接收到使用者指令後，第一步永遠是分析意圖、匹配 Playbook、展開任務清單。
- **動態意圖分類**：
  - 修復問題 / 異常報錯 ➔ `Bug-fix Playbook`
  - 新增功能 / 模組擴展 ➔ `Feature Playbook`
  - 代碼重組 / 效能無涉的簡化 ➔ `Refactoring Playbook`
  - 疑難排查 / 系統提問 ➔ `Investigation Playbook`
  - 延遲過高 / 記憶體洩漏 ➔ `Performance Playbook`

### 3.2 跨 CLI 參數與提示詞規格

#### A. Claude Code
- **呼叫方式**：`/poteto-mode <task>`（透過 `.claude/skills/poteto-mode/SKILL.md` 或全域 Prompt 注入）
- **Prompt 範本**：
```markdown
# /poteto-mode: System Dispatcher Prompt (Claude Code)
You are acting as the Chief Architect and Task Dispatcher in "poteto-mode".
Upon receiving the task: "{task_description}"
1. DO NOT make any code modifications immediately.
2. Analyze the user intent and select exactly ONE primary playbook:
   [bug-fix | feature | refactoring | investigation | perf-issue].
3. Output the selected Playbook along with a step-by-step numbered checklist.
4. Enforce the Evidence-First rule: Every claim of completion must include actual bash command execution output.
```

#### B. Codex CLI
- **呼叫方式**：`codex run poteto-mode "{task}"` 或在 `AGENTS.md` / `codex-prompt` 配置自訂指令
- **Prompt 範本**：
```markdown
# poteto-mode Workflow Hook (Codex CLI)
Task: {task_description}
Phase: ROUTE_AND_PLAN
Rules:
- Read codebase context first using read_file / grep.
- Choose Playbook: bug-fix | feature | refactoring | investigation | perf-issue.
- Write a plan to PLAN.md. Block tool execution for file writing until plan is accepted.
```

#### C. Antigravity
- **呼叫方式**：`~/.gemini/config/skills/poteto-mode/SKILL.md` 搭配 `/poteto-mode`
- **Prompt 範本**：
```markdown
# Antigravity Skill Definition: poteto-mode
description: SpaceX Evidence-First orchestration router.
metadata:
  guardrails: ["zero-dummy", "no-reproduction-no-fix", "evidence-required"]
system_prompt: |
  Analyze the request. Route to the matching Playbook.
  Before invoking any file-editing tools, generate the execution checklist.
  Never claim completion without pasting raw terminal output logs.
```

---

## 4. 五大核心 Playbooks 規格拆解

### 4.1 Bug-Fix Playbook（`bug-fix.md`）

- **核心箴言**：**「No Reproduction, No Fix」**（無重現測試，不准動手修正）。
- **流程階段**：
  1. **Phase 1: 重現錯誤（Red Phase）**
     - 撰寫一支獨立測試案例（Unit / E2E / CLI Script），執行該測試並**必須回傳失敗（Exit Code != 0）**。
     - 貼出終端機紅燈報錯輸出，證明 Bug 確實存在且重現方式可靠。
  2. **Phase 2: 根因診斷（Root Cause Analysis）**
     - 追蹤堆疊軌跡與調用鏈，定位根本原因，禁止在表面貼補丁（Monkey Patch）。
  3. **Phase 3: 最小改動修復（Green Phase）**
     - 針對根因做最小範圍的精確修正，禁止無關的重構或格式洗牌。
     - 重新執行重現測試，**必須轉為綠燈（Exit Code == 0）**。
  4. **Phase 4: 全局回歸驗證（Regression Protection）**
     - 執行整個測試套件，確保既有功能無任何回歸破壞。
- **終端驗證門禁**：
  - 提交前必須附帶兩段終端日誌：① 重現測試失敗日誌；② 重現測試通過與全量測試通過日誌。

### 4.2 Feature Playbook（`feature.md`）

- **核心箴言**：**「Design Boundaries First, Code Second」**（邊界先行，架構落實）。
- **流程階段**：
  1. **Phase 1: 架構探索與邊界約定（/architect）**
     - 明確模組的輸入、輸出、資料型別與異常處理策略。
     - 列出對外 API 介面定義（Interface / TypeScript Type / Python Dataclass）。
  2. **Phase 2: 建立合約測試（Contract & Spec Tests）**
     - 先行撰寫驗收測試（Gherkin / Unit Test），覆蓋正常情境與極端邊界（邊界值、空值、超時）。
  3. **Phase 3: 模組化實作**
     - 依據約定介面撰寫業務邏輯，嚴禁留空殼函式（`return true` 或 `pass`）。
  4. **Phase 4: 端到端整合驗收**
     - 執行真實呼叫驗證，產出端到端驗收成果。

### 4.3 Refactoring Playbook（`refactoring.md`）

- **核心箴言**：**「Behavior Preservation & Subtraction First」**（行為嚴格保持，減法優先）。
- **流程階段**：
  1. **Phase 1: 行為測試鎖定（Pinning Tests）**
     - 在動工前確認現有測試覆蓋率；若現有測試不足，先補足字元級或行為級特徵測試（Characterization Tests），確認為全綠。
  2. **Phase 2: 先刪後改（Subtract First）**
     - 優先清理廢棄代碼、死分支（Dead Code）與無用依賴。
  3. **Phase 3: 小步微調與連續測試**
     - 單次改動限制在單一函式或檔案，每次改動後即刻重跑測試，確保測試隨時處於綠燈。
  4. **Phase 4: 對外介面不變性檢驗**
     - 比對公開 API 導出符號與簽名，確認對外部調用者零破壞。

### 4.4 Investigation Playbook（`investigation.md`）

- **核心箴言**：**「Read-Only Exploration, Zero Speculative Edits」**（純讀探查，禁止猜測性修改）。
- **流程階段**：
  1. **Phase 1: 建立問題假設**
     - 針對使用者提出的疑問或效能瓶頸，列出 2~3 個可被證偽的具體假說。
  2. **Phase 2: 呼叫鏈與資料流追蹤（/how & /why）**
     - 透過靜態分析（AST / grep）與動態探針日誌，繪製關鍵函式調用鏈。
  3. **Phase 3: 驗證假說與收集證據**
     - 讀取程式碼、設定檔或日誌，逐一標註證據（檔案路徑、行號、程式碼片段）。
  4. **Phase 4: 輸出調查報告**
     - 產出結構化排查報告，包含根因結論、架構決策脈絡與推薦修復路徑，不直接發起 Commit。

### 4.5 Performance Playbook（`perf-issue.md`）

- **核心箴言**：**「Measure Before You Optimize」**（無基準測量，不談最佳化）。
- **流程階段**：
  1. **Phase 1: 採集基線數據（Baseline Benchmark）**
     - 使用客觀效能度量腳本，記錄當前 CPU 時間、記憶體消耗、延遲（P50/P95/P99）或吞吐量。
  2. **Phase 2: 瓶頸定位（Profiling）**
     - 透過 Profile 工具識別熱點函式（Hot Path），避免在只佔 1% 時間的冷代碼上過度最佳化。
  3. **Phase 3: 針對性最佳化**
     - 實施算法改進、快取、批次合併或非同步化處理。
  4. **Phase 4: 對比驗收（Comparison Evidence）**
     - 在相同硬體與環境條件下重跑基準測試，出具對比表格（改動前 vs 改動後），提升必須具備統計顯著性。

---

## 5. 五大專業輔助技能（Modular Skills）

| 技能指令 | 核心職責 | 執行時機 | 跨 CLI 映射 |
| :--- | :--- | :--- | :--- |
| **`/architect`** | 跨模組資料流與邊界藍圖設計 | 改動跨越 2 個以上檔案或變更公開介面時 | `plan` / `task-orchestrator` / `first-principles` |
| **`/arena`** | 平行嘗試多種解法並對抗性選優 | 遇到架構分歧、效能與簡潔度權衡時 | `subagent` 平行分支派發 ＋ 基準跑分比較 |
| **`/swarm`** | 大規模批次任務並行委派 | 測試矩陣補全、多平台適配、大批重複改動 | `invoke_subagent` 批次併發 ＋ 結果彙整 |
| **`/interrogate`** | 跨模型對抗性代碼審查與極端邊界攻擊 | 準備發起 PR 前，挑剔尋找空指針、競爭危害 | `ai-review` / `blind-review` / 二審子代理 |
| **`/how` & `/why`** | 呼叫鏈追蹤與架構決策溯源 | 接手陌生代碼庫或修改核心底層邏輯時 | 靜態呼叫圖檢索 ＋ Git blame / PR 討論串回溯 |

---

## 6. 三大多 CLI 實例對照（End-to-End Walkthroughs）

### 實例 1：Bug-fix 實例（購物車過期未釋放庫存）

- **情境描述**：使用者回報「購物車訂單超時取消後，未退還已被預扣的庫存量」。
- **三平台對照表**：

| 維度 | Claude Code | Codex CLI | Antigravity |
| :--- | :--- | :--- | :--- |
| **輸入指令** | `/poteto-mode 修復訂單過期未退還庫存的 bug` | `codex run poteto-mode "fix order timeout inventory bug"` | `/poteto-mode 修復訂單過期未退還庫存 bug` |
| **Playbook 匹配** | 自動載入 `playbooks/bug-fix.md` | 鎖定 `bug-fix` 流程並凍結寫入權限 | 啟動 `verification-protocol` ＋ `bug-fix` |
| **Phase 1: 重現** | 撰寫 `test_inventory_release_on_timeout.py`，終端執行 `pytest` 輸出 `FAILED: Expected 10, got 0` | 建立重現腳本，終端驗證 Exit Code 1，貼入紀錄 | 撰寫失敗單元測試，執行確認紅燈，截圖/終端日誌落地 |
| **Phase 2: 修復** | 在 `OrderService.cancel_expired()` 補齊 `InventoryClient.release()` | 精確編輯業務邏輯，禁止無關檔案異動 | 精確編輯業務邏輯，維持程式碼 SOLID 職責分明 |
| **Phase 3: 驗證** | 重跑測試：`PASSED`，全庫測試：`120 passed` | 重跑測試：Exit Code 0，Diff 審查無多餘改動 | 重跑單元測試與端到端測試，全綠通過 |
| **交付輸出** | 附帶紅燈與綠燈之終端輸出日誌，提交 commit | 終端日誌 SHA 校驗通過，自動建立 PR | 依據全域規範執行 `verify_inbox.py` 與測試後 commit & push |

### 實例 2：Feature 實例（新增公共 API 離線 LRU 快取層）

- **情境描述**：為公共數據抓取模組新增具備 TTL 與磁碟持久化能力的 LRU 快取模組。
- **三平台對照表**：

| 維度 | Claude Code | Codex CLI | Antigravity |
| :--- | :--- | :--- | :--- |
| **輸入指令** | `/poteto-mode 為 public-apis 模組增加磁碟持久化 LRU 快取` | `codex run poteto-mode "add persistent LRU cache for public apis"` | `/poteto-mode 實作 public-apis 離線快取模組` |
| **Playbook 匹配** | 載入 `playbooks/feature.md` ＋ 呼叫 `/architect` | 載入 `feature` 規格，輸出 `CACHE_SPEC.md` | 載入 `feature`，定義快取合約介面 |
| **架構約束** | 定義 `CacheInterface`（`get`, `set`, `invalidate`），TTL 預設 3600s | 明確型別簽名與例外處理，禁止使用全局黑魔法 | 設計無第三方依賴純標準庫實作，保證多執行緒安全 |
| **測試先行** | 先寫 `test_cache_lru.py`（測試容量淘汰、過期剔除、持久化讀寫） | 撰寫單元測試覆蓋邊界值，未實作前執行為紅燈 | 撰寫規格測試，覆蓋磁碟異常與並發衝突 |
| **實作與審查** | 撰寫快取實作代碼，呼叫 `/interrogate` 攻擊並發讀寫危害 | 實作代碼，執行靜態檢查與型別檢查 | 實作代碼，調用 `blind-review` 審查記憶體洩漏風險 |
| **交付證據** | 貼出測試覆蓋率（100%）與多執行緒並發測試日誌 | 貼出 CLI 執行日誌與基準讀寫測試數據 | 執行完整測試套件全綠，提交並推送至個人倉庫 |

### 實例 3：Refactoring 實例（簡化資料庫查詢構建器）

- **情境描述**：重構遺留的 SQL 查詢拼裝模組，消除深層巢狀 `if-else`，改為鏈式調用（Fluent Builder）。
- **三平台對照表**：

| 維度 | Claude Code | Codex CLI | Antigravity |
| :--- | :--- | :--- | :--- |
| **輸入指令** | `/poteto-mode 重構 QueryBuilder，簡化巢狀條件判斷` | `codex run poteto-mode "refactor QueryBuilder nested conditions"` | `/poteto-mode 重構 QueryBuilder 巢狀結構` |
| **Playbook 匹配** | 載入 `playbooks/refactoring.md` | 鎖定 `refactoring` 流程，宣告「行為嚴格保持」 | 載入 `refactoring` 流程，設定行為保護閘門 |
| **Phase 1: 鎖定** | 檢查現有測試，補齊 20 組邊界查詢語法測試（Pinning Tests）全綠 | 執行目前全部測試，確認基準狀態為 0 錯誤 | 確認已有單元測試全數通過，保存基準輸出 |
| **Phase 2: 減法** | 刪除 3 個無人使用的內部輔助函式，重跑測試確認仍綠 | 標記廢棄符號，進行小步代碼剔除 | 移除冗餘分支，保持精簡 |
| **Phase 3: 重構** | 引進鏈式方法替換巢狀結構，每改動一個方法即刻單元驗證 | 小步代碼替換，確保 AST 導出簽名一致 | 逐一替換查詢節點，每步執行 focused 測試 |
| **交付證據** | Git Diff 證明未改動對外 API，全量測試綠燈日誌 | 貼出重構前後對比與測試輸出，確認無行為回歸 | 通過 `damage-report` 與本機契約測試，提交完成 |

---

## 7. 與本機環境現有能力之映射與整合指南

本專案與維護者本地現有之規範及工具庫具備極高的契合度，可直接以等價機制實現 `pstack` 核心標準：

```text
┌────────────────────────┬────────────────────────────────────────────────────────┐
│ pstack 核心機制        │ 本地對應資產 / 技能庫實現                              │
├────────────────────────┼────────────────────────────────────────────────────────┤
│ No Reproduction No Fix │ ai-quality-gates ＋ RULE[user_global] 嚴格紅綠燈驗證   │
│ /poteto-mode           │ new-mission ＋ task-orchestrator 意圖識別與派工        │
│ /architect             │ first-principles ＋ templates/article-analysis.md      │
│ /arena                 │ invoke_subagent 平行分支派工評比                       │
│ /interrogate           │ ai-review ＋ blind-review 跨模型對抗攻擊審查          │
│ 零空殼函式 / 零假資料 │ RULE[user_global] 嚴格禁令（禁止空殼函式與假資料）     │
│ 執行期真實終端證據     │ verification-protocol ＋ damage-report 終端日誌落盤    │
└────────────────────────┴────────────────────────────────────────────────────────┘
```

本規格書可直接作為 Agent 在跨 CLI 環境下開發、重構與修復程式碼時的標準作業指導規範。
