# Harness² 雙層遞迴與 8 大模組演進及防弊規範

> **對應任務**：`T-20261108-03`
> **來源筆記**：[notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md](../notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md)
> **參考專案**：[`google-research/harness2`](https://github.com/google-research/harness2)（[arXiv:2610.14224](https://arxiv.org/pdf/2610.14224)）

---

## 1. 規範目的

Google Research 的 **Harness²（Harness Squared）** 證明了在固定模型權重（Frozen Weights）且無標準答案（Without Ground-Truth Feedback）的開放世界任務中，透過雙層遞迴精煉外部 8 大 Harness 模組，可在 WorkBuddy-Bench 帶來最高 `+11.5` 分、LAB 法律基準帶來 `+11.8%` 的提升。

本規範將 Harness² 的核心機制轉化為本庫與本地多 Agent 協作環境的可執行工程標準，同時修補原專案「預設關閉 Codex 沙盒且未限制網路存取導致 Benchmark 答案洩漏」之安全漏洞。

---

## 2. 八大可編輯 Harness 模組映射表

在對任何 Agent 工作流進行自我優化時，所有修改提案（Proposals）必須明確標註其所屬的執行期角色與模組分類，禁止跨模組混雜修改卻不留紀錄：

| 執行期角色 (Runtime Role) | Harness² 模組 | 本地 Agent 協作架構對應位置 | 變更驗證閘門 (Verification Gate) |
| :--- | :--- | :--- | :--- |
| **1. Context Construction** | `system prompt` | `AGENTS.md`、`GEMINI.md` | 變更後須檢查是否與既有硬閘門衝突，禁止注入削弱安全停頓之指令 |
| **1. Context Construction** | `guardrails` | `tools/verify_*.py`、Pre-tool Hooks | 必須附帶正向放行與負向攔截（含引號/編碼繞過）之單元測試 |
| **1. Context Construction** | `memory` | `notes/*.md`、`docs/*.md`、SSOT `knowledge/` | 寫入前須執行 `build_index.py` 與 `verify_inbox.py` 確保雙向連結與分類合規 |
| **1. Context Construction** | `skills` | `.gemini/config/skills/<name>/SKILL.md` | 觸發條件（Triggers）與非適用邊界（NOT for）必須明確分離 |
| **2. Tool Interface** | `tool guidance` | 工具 Schema 描述、Skill 內 CLI 路由表 | 參數型別、工作目錄與錯誤退避規則必須具決定性（Deterministic） |
| **2. Tool Interface** | `scripts` | `tools/*.py`、Skill `scripts/*` | 必須在目標平台（Windows 11 原生）實測通過並具備 `tests/test_*.py` |
| **3. Delegation** | `subagents` | `define_subagent`、`invoke_subagent` 派工配置 | 遵循 `token-optimizer` 與單一職責，明確定義輸入契約與回報格式 |
| **4. Middleware** | `plugins` | MCP Servers、Anti-Doom-Loop Hook、Session Loggers | 失效時必須顯式報錯或留存日誌，嚴禁靜默吞掉例外（`except Exception: pass`） |

---

## 3. 第一層遞迴：Task-Level `Propose–Probe–Compose` 對比精煉流程

當面對沒有現成 Ground-Truth 分數的開放式工程或研究任務，且初始執行（Initial Run）出現品質瓶頸時，採行三階段對比精煉：

```
[Initial Trajectory T0]
         │
         ▼
1. Propose (雙軌提案)
   ├─ Candidate G (General / Invariant): 跨領域通用的護欄、重試或格式約束
   └─ Candidate D (Domain-Specific): 針對當前 repo / 語言 / 業務領域的專用腳本或 Skill
         │
         ▼
2. Probe (同任務受控試跑)
   ├─ 執行 Candidate G ──► 產出軌跡 TG 與驗證證據 EG
   └─ 執行 Candidate D ──► 產出軌跡 TD 與驗證證據 ED
         │
         ▼
3. Compose (行為對照合成)
   └─ 對比 (T0, TG, TD) 的失敗點、Token 消耗與確定性測試結果，合成最終 Harness H*
```

### 執行準則
1. **區分 General 與 Domain 修改**：避免把單一專案的特例（Domain-specific）直接寫進全域 `GEMINI.md`（General），全域規則僅收錄跨專案皆成立的不變量（Invariants）。
2. **選用適當擴展模式**：
   - **Parallel Mode（廣度優先）**：當死因不明確時，平行提出 2 個不同模組的最小修改（例如一個改 `tool guidance`、一個加 `scripts` 預檢），對比兩者執行軌跡。
   - **Sequential Mode（深度優先）**：當方向明確但邊界案例多時，在同一模組上根據前一輪測試輸出迭代精煉。

---

## 4. 第二層遞迴：Harnessing-Level `Experience Reflector` 經驗蒸餾門檻

任務結束後，執行器狀態歸零，但經驗不能只留在對話歷史中。要將單次任務的修改升格為持久化規則（寫入 `Improvement Harness`：即本庫 `docs/`、`tools/verify_*.py` 或全域規則），必須通過以下**三項證據門檻**：

1. **軌跡對照證據（Behavioral Contrast Evidence）**：
   - 必須能指出「修改前軌跡 $T_0$ 在哪一步失敗/耗費過多 Token」以及「修改後軌跡 $T^*$ 如何消除該問題」，附上具體實例日期與錯誤現象。
2. **機械防線優先原則（Mechanical Guardrail First）**：
   - 若該教訓能寫成 `tools/verify_*.py` 靜態檢查、單元測試或 Pre-tool Hook（對應 `guardrails` / `scripts` / `plugins`），優先實作為程式碼，文件僅作補充。
3. **零退化驗證（Zero-Regression Check）**：
   - 寫入規則或腳本後，必須通過既有測試套件，確認未破壞既有工作流。

---

## 5. 沙盒與基準防弊安全契約（Sandbox & Anti-Contamination Contract）

針對 `google-research/harness2` 官方 README 揭露之風險（預設執行器無網路限制且關閉 Codex 沙盒，可能上網抓取公開 Benchmark Rubrics 與答案），本地執行任何 Harness 自動優化或基準測試時，強制實施以下安全契約：

| 風險維度 | Harness² 預設危險行為 | 本地強制防弊與安全契約 |
| :--- | :--- | :--- |
| **宿主機執行隔離** | `--substrate cx` 預設關閉 Codex 沙盒（sandbox disabled），動態生成的 `scripts` 可任意讀寫宿主機 | **預設開啟沙盒（Standard Sandbox Mode）**：所有 `Probe` 階段測試的動態腳本與指令預設在沙盒內運行；嚴禁在未驗證的候選 Harness 中自動賦予全域免沙盒權限，亦不得讀寫專案目錄外的機敏路徑。 |
| **基準汙染防範 (Benchmark Contamination)** | 執行器擁有無限制外網存取權，Probe 階段可搜尋公開題庫、Rubrics 或原 repo Issue 答案 | **評測期網路白名單與 Rubric 阻斷**：在執行能力基準評測（Evaluation / Benchmarking）時，必須關閉執行器的公開網頁搜尋能力，或於代理層封鎖基準題庫與評分標準所在之網域，確保 `Behavioral Contrasts` 反映真實推理與工具調用能力，而非檢索作弊能力。 |
| **持久化污染防護 (Improvement Harness Poisoning)** | 若作弊軌跡拿高分，`Experience Reflector` 會將「上網找答案」作為成功經驗寫入持久化資料庫 | **Reflector 審計閘門**：任何寫入持久化規則庫、Skill 或 `verify_*.py` 的修改，必須經過 Git diff 審查與確定性測試，禁止自動將含外網硬編碼 URL 或繞過驗證之腳本合入主幹。 |
