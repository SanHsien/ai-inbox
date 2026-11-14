---
id: 2026-11-08-google-research-harness2-recursive-agent-harnessing
title: "Google Research 開源 Harness²（Harness Squared）：無標準答案開放世界的雙層遞迴 Agent Harness 自我優化框架"
source_url: "https://www.threads.com/share/_toE5mWj3"
source_platform: "Threads (@wayturn_) / GitHub (google-research/harness2)"
author: "偉騰 (@wayturn_) / Google Research (Ruiyao Xu, Tomas Pfister et al.)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "工程紀律與設計審查"
short_title: "Google Harness²雙層遞迴優化"
tags:
  - google-research
  - harness2
  - agent-harness
  - recursive-optimization
  - context-engineering
  - benchmark-contamination
---

# Google Research 開源 Harness²（Harness Squared）：無標準答案開放世界的雙層遞迴 Agent Harness 自我優化框架

- **來源連結**：[Threads 原文分享](https://www.threads.com/share/_toE5mWj3) ｜ [貼文永久網址 (@wayturn_)](https://www.threads.com/@wayturn_/post/DfR0PG7mTz6) ｜ [GitHub (google-research/harness2)](https://github.com/google-research/harness2) ｜ [官方論文 (arXiv:2610.14224)](https://arxiv.org/pdf/2610.14224)
- **核心作者**：偉騰（`@wayturn_`）／ Google Research（Ruiyao Xu, Yanfei Chen, Zhongying CuiZhu, Bhavana Dalvi Mishra, Yifei Ming, Han Yu, Rujun Han, Chen-Yu Lee, Tomas Pfister）
- **分析主題**：剖析 Google Research 開源的 **Harness²（Harness Squared：Recursive Agent Harnessing for an Open World）**（23,026 Stars、2,301 Forks、Apache-2.0 License），在固定語言模型權重且無須標準答案（without ground-truth feedback）的開放世界任務中，透過雙層遞迴（Task-level `Propose–Probe–Compose` 與 Harnessing-level `Experience Reflector`）自動精煉 8 大外部 Harness 模組；並檢視其官方 README 揭露之「關閉沙盒與無網路限制導致公開 Benchmark 答案洩漏」防弊邊界。
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md`](./2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md)（Agent Autoloop 事件溯源與 8 跳 TTL 熔斷防線）
  - [`docs/external-judge-audit.md`](../docs/external-judge-audit.md)（外部裁判防弊與驗證器設計規範）

---

## 1. 資訊初篩（5W1H）

- **Who**：Google Research 團隊（Ruiyao Xu, Tomas Pfister 等）開源，由偉騰（`@wayturn_`）於 Threads 整理分享。
- **What**：開源 **Harness²（Harness Squared）**（[`google-research/harness2`](https://github.com/google-research/harness2)），一套在不修改底層語言模型權重（Frozen Weights）、且**無須依賴標準答案（without ground-truth feedback）**的開放世界環境中，透過雙層遞迴自動精煉 Agent 外部控制架構（Harness）的系統。
- **Where**：
  - Threads 原文：`https://www.threads.com/@wayturn_/post/DfR0PG7mTz6`（短網址：`https://www.threads.com/share/_toE5mWj3`）
  - 官方 GitHub：`https://github.com/google-research/harness2`
  - 官方論文：[arXiv:2610.14224](https://arxiv.org/pdf/2610.14224)（*Harness²: Recursive Agent Harnessing for an Open World*）
  - 專案首頁：`https://harness2.github.io`
  - 社群延伸導讀（未查證）：`https://medium.com/@simon3458/ai-agent-harness-squared-intro-bdb182241a04`
- **When**：2026 年 10 月發表論文並開源，2026 年 11 月納入知識庫分析。
- **Why**：真實世界的複雜長程任務（辦公室文件處理、網頁操作、跨檔案軟體工程、法律審查）缺乏可即時計算 Reward 的 Ground Truth。傳統 Prompt Optimizer 需要驗證集標準答案打分；Harness² 改用「同任務多候選執行軌跡的行為對照（Behavioral Contrasts）」來驅動外部 8 大 Harness 模組演化。
- **How**：在單一任務內執行 **Task-level recursion（`Propose–Probe–Compose` 對比精煉）**，並在任務結束後透過 **Harnessing-level recursion（`Experience Reflector` 經驗蒸餾）** 將經過實證的修改規則寫入持久化的 *Improvement Harness* 資料庫。

---

## 2. 核心架構與 8 大可編輯 Harness 模組

Harness² 將包覆在基礎模型外部的執行環境拆解為 **4 大執行期角色、8 個可編輯模組**：

```
+-------------------------------------------------------------------+
|                     Agent Harness (8 Modules)                     |
+---------------------------------+---------------------------------+
| 1. Context Construction         | 2. Tool Interface               |
|   - system prompt (系統提示詞)  |   - tool guidance (工具使用指南)|
|   - guardrails (安全與格式護欄) |   - scripts (輔助執行腳本)      |
|   - memory (長短期記憶狀態)     |                                 |
|   - skills (領域知識與工作流)   | 4. Middleware                   |
| 3. Delegation                   |   - plugins (執行期攔截與日誌)  |
|   - subagents (子代理角色配置)  |                                 |
+---------------------------------+---------------------------------+
```

### 雙層遞迴機制（Two Levels of Recursion）

```
[Level 1: Task-Level Recursion (單一任務內無標準答案對比精煉)]
  初始執行 (Initial Run)
       │
       ▼
  Harness Editor (Propose) ──► 產生兩類修改方案：
       ├─ General / Invariant (通用型優化)
       └─ Domain-Specific (領域專用優化)
       │
       ▼
  Candidate Probes (Probe) ──► 在同一任務上平行/序列試跑 K 個候選 Harness
       │
       ▼
  Harness Composer (Compose) ─► 對比各軌跡行為差異 (Behavioral Contrasts)，合成最佳 Harness

[Level 2: Harnessing-Level Recursion (跨任務經驗累積)]
  任務結束後執行器重置 (Executor Reset)
       │
       ▼
  Experience Reflector ──────► 萃取有證據支撐的教訓 (Evidence-supported lessons)
                               寫入持久化 Improvement Harness，指導未來新任務的 Editor
```

1. **平行與序列擴展模式（Scaling Modes）**：
   - `--mode parallel --k K`：廣度探索（Breadth），同時探測 $K$ 個通用型與 $K$ 個領域型候選配置後一次合成。
   - `--mode sequential --k K`：深度精煉（Depth），將合成後的 Harness 與累積軌跡證據連續迭代 $K$ 輪。
2. **雙執行基底支援（Substrates）**：
   - 支援預設的 `OpenCode` 以及 `Codex`（`--substrate cx`）。

---

## 3. CQR 品質檢驗與基準測試剖析

### 論文基準數據核驗

> 下表基準值來自論文，未逐一核對。

| 基準測試 (Benchmark) | 涵蓋領域 | 基礎配置表現 | Harness² 優化後表現 | 淨提升幅度 |
| :--- | :--- | :--- | :--- | :--- |
| **WorkBuddy-Bench** | `office` / `web` / `code` | Gemini 3.5 Flash (`72.4`) / GLM-5 (`64.2`) | Gemini 3.5 Flash (`80.8`) / GLM-5 (`75.7`) | **+8.4 分** / **+11.5 分**（單步 `K=1`） |
| **JobBench** | 專業知識工作任務 | 基準 Harness | 雙層遞迴精煉 Harness | 最高 **+4.5 分** |
| **LAB (Legal Agent Benchmark)** | 複雜法律條文與合約推理 | 基準 Harness | 雙層遞迴精煉 Harness | Partial pass rate 最高 **+11.8%** |

### 工程與安全邊界批判（Critical Audit）

檢視 [`google-research/harness2` 官方 README](https://github.com/google-research/harness2) 的 `Web access` 節，官方明確揭露了一項重大評估與安全風險：

> *"Executor network access is unrestricted, and Codex runs with its sandbox disabled. Public benchmark rubrics may be accessible online. Before evaluation, configure network restrictions to prevent access to benchmark answers and grading criteria."*

1. **基準汙染與作弊風險（Benchmark Contamination / Reward Hacking）**：
   - 在 `--substrate cx`（Codex）或 `OpenCode` 預設配置下，執行器關閉了沙盒且擁有無限制的對外網路存取權。
   - 當 Agent 在 `Candidate Probes` 階段遇到公開基準（如 WorkBuddy-Bench 或公開 GitHub 上的題庫）時，自主編寫的 `scripts` 或 `tool guidance` 可能直接透過網路搜尋抓回公開的評分標準（Rubrics）甚至標準答案，導致「行為對照（Behavioral Contrasts）」挑選出會上網偷看答案的 Harness。
2. **無沙盒自動生成腳本的宿主機風險**：
   - Harness² 允許 `Harness Editor` 動態生成並修改 `scripts` 與 `plugins`，若在無沙盒（sandbox disabled）環境下連續執行 $K$ 個候選 Probe，一旦生成具破壞性的 Shell/Python 指令，將直接危及宿主機檔案系統與憑證。

---

## 4. 與本庫架構之對映與吸收價值

| Harness² 模組 | 本庫對應實作 | 差距與優化空間 |
| :--- | :--- | :--- |
| `system prompt` / `guardrails` | `AGENTS.md`、`GEMINI.md`、`tools/verify_*.py` | 已具備硬閘門，可引入「通用 vs 領域」雙軌變更分類。 |
| `memory` / `Experience Reflector` | `notes/`、`docs/`、`checkpoint` / `neat-freak` | 可定義標準化的「軌跡對照證據（Behavioral Contrast Evidence）」欄位。 |
| `skills` / `tool guidance` / `scripts` | `.gemini/config/skills/`、`tools/*.py` | 當腳本或規則在 Probe 失敗時，應強制檢查是否違反沙盒與網路隔離契約。 |
| `subagents` / `plugins` | `invoke_subagent`、Pre/Post-tool Hooks | 需防範子代理在評估模式下繞過沙盒或觸發無限制外網抓取。 |

---

## 5. 拆解待辦事項（Action Items）

- [x] **`T-20261108-03`**｜**[優先級：高]** 撰寫《Harness² 雙層遞迴與 8 大模組演進及防弊規範》（`docs/harness2-recursive-agent-harnessing-spec.md`）
  - **目標範圍**：`docs/harness2-recursive-agent-harnessing-spec.md`
  - **具體實作步驟**：
    1. 定義 8 大可編輯 Harness 模組（`system prompt`, `guardrails`, `memory`, `skills`, `tool guidance`, `scripts`, `subagents`, `plugins`）至本庫與本地多 Agent 架構的映射表及驗證閘門。
    2. 規範無標準答案任務的第一層遞迴（Task-Level `Propose–Probe–Compose` 對比精煉流程）與第二層遞迴（Harnessing-Level `Experience Reflector` 經驗蒸餾三項證據門檻）。
    3. 針對 `google-research/harness2` 預設關閉 Codex 沙盒且未限制網路存取的問題，制定「沙盒強制開啟與基準 Rubric 網域隔離」防弊安全契約。
  - **驗收標準（DoD）**：
    - 產出 `docs/harness2-recursive-agent-harnessing-spec.md` 並通過 `python tools/build_index.py` 與 `python tools/verify_inbox.py` 契約及 100% 目錄覆蓋率校驗。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正（2026-11-14）：+11.8 改為「個百分點」並標明是作者報告的 LAB partial pass rate；答案洩漏改寫為官方 Web access 章節揭露的風險，註明本庫沒有已發生洩漏的證據。
