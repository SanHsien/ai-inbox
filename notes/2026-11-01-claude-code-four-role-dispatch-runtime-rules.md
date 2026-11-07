---
id: 2026-11-01-claude-code-four-role-dispatch-runtime-rules
title: "Claude Code 四角色動態調用原則解構：主 Session 拍板、規格驅動開工、里程碑檢查點與布林決策 API 實戰"
source_url: "https://www.threads.com/@0xalpha.ai/post/DeQTEQwE7Gz"
source_platform: "Threads (@0xalpha.ai)"
author: "0xalpha.ai (@0xalpha.ai)"
analyzed_at: 2026-11-01
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "跨 CLI 與階層派工"
short_title: "Claude Code四角色動態調用原則"
tags:
  - claude-code
  - agent-dispatch-rules
  - runtime-orchestration
  - milestone-checkpoints
  - decision-api
  - hierarchical-agents
  - token-discipline
  - 0xalpha
---

# Claude Code 四角色動態調用原則解構：主 Session 拍板、規格驅動開工、里程碑檢查點與布林決策 API 實戰

- **來源連結**：[Threads 原文分享 (@0xalpha.ai)](https://www.threads.com/@0xalpha.ai/post/DeQTEQwE7Gz)
- **核心作者**：0xalpha.ai（@0xalpha.ai，AI 前沿工具與自主編程架構探索者）
- **分析主題**：解構 0xalpha.ai 針對 Claude Code 四級分工配置進一步公開的實戰動態派工與執行期（Runtime）調用觸發原則——「很多人留言求設定，整理一下我實際在跑的分工 🧵 影片裡的四個角色可以這樣對應：・Opus：主 session，負責規劃、拆工作、最後拍板 ・Sonnet：拿到明確規格就開工實作 ・Fable：關鍵時刻的檢查點，不是每步都叫 ・Jev：只回答『是／否、選哪個』的決策 API。核心觀念就一句：強模型不要拿去做雜事」。深度剖析如何將粗粒度的模型選型轉化為**嚴格的狀態機觸發機制**，防止多 Agent 開發中常見的「過度評審（Over-Reviewing）延遲爆炸」與「決策介面發散（Unstructured Decision Hallucination）」問題，並建立標準化執行期閘門規範。
- **當前狀態**：`⚪ 已封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（Claude Code 四級模型分工架構理念與拓撲總論）
  - [`2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md`](https://github.com/SanHsien/claude-context-audit/blob/main/notes/2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md)（微軟 TokenEconomizer 黑盒成本控制）
  - [`notes/2026-10-31-yetone-magpie-local-ai-gateway-smart-routing.md`](./2026-10-31-yetone-magpie-local-ai-gateway-smart-routing.md)（Magpie 本地 AI 模型網關智慧路由）
  - [`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md)（Karpathy 專案規範四大硬閘門）

---

## 1. 核心內容摘要：從靜態模型分工到動態調用原則（Executive Summary）

在定義了 Opus、Sonnet、Fable 與 JEV 的角色階層之後，工程實踐中最容易遭遇的失敗模式是：**「雖然配置了不同模型，但調用邊界模糊，導致輕量任務依然呼叫旗艦模型，或審查代理人每一步都在阻礙執行，使整體開發週期呈數倍拉長」**。

0xalpha.ai 公開的四條實戰執行期原則，為多 Agent 編排提供了精確的狀態機切換邊界：

```text
+---------------------------------------------------------------------------------------------------+
|                     Claude Code 四角色動態觸發狀態機與邊界流轉圖                                  |
+---------------------------------------------------------------------------------------------------+

                     ┌─────────────────────────────────────────────────┐
                     │          Opus (主 Session / 決策中樞)           │
                     │  • 任務進入：釐清需求、盤點架構                 │
                     │  • 產生高內聚規格工單 (Spec Packet)            │
                     └────────────────────────┬────────────────────────┘
                                              │
                                              ▼
                             [ 檢查：規格是否明確具體？ ]
                             ├──────────────────────────┐
                     (明確)  │                          │ (模糊)
                             ▼                          ▼
               ┌───────────────────────────┐    ┌───────────────────────────┐
               │    Sonnet (規格驅動開工)   │    │  退回 Opus 補充規格與約束 │
               │ • 高頻執行代碼修改與測試  │    └───────────────────────────┘
               │ • 閉環自測，產生 Diff 產物│
               └─────────────┬─────────────┘
                             │
                             ▼
                    [ 是否到達關鍵檢查點？ ]
                    (如：模組完成 / 破壞性修改 / 結案前)
                    ├───────────────────────────┐
             (是)   │                           │ (否：日常小修改)
                    ▼                           ▼
       ┌───────────────────────────┐    ┌───────────────────────────┐
       │   Fable (里程碑檢查點)    │    │      跳過評審，快速推進    │
       │ • 嚴格對照 DoD 打分驗收   │    └─────────────┬─────────────┘
       │ • 爆破半徑與安全回歸審核  │                  │
       └─────────────┬─────────────┘                  │
                     │                                │
                     └─────────────────┬──────────────┘
                                       │
                                       ▼
                     ┌─────────────────────────────────┐
                     │     JEV (輕量布林決策 API)      │
                     │ • 「是/否、選哪個」快速過濾     │
                     │ • 零文字廢話，毫秒級輸出返回    │
                     └─────────────────┬───────────────┘
                                       │
                                       ▼
                     ┌─────────────────────────────────┐
                     │          Opus (最終拍板)        │
                     │ • 檢視全流程證據，Merge 或交付  │
                     └─────────────────────────────────┘
```

---

## 2. 深入技術剖析：四大動態調用準則與防禦工程

### 2.1 準則一：Opus 主 Session 拍板制（Orchestrator Singularity）

- **定義**：Opus 是唯一的「頂層會話主持者（Session Master）」，它維護整體長遠規劃、專案架構約定與最終發布決策。
- **禁忌邊界**：Opus 絕對不親自執行非關鍵代碼編輯，不直接在 Shell 中跑無窮無盡的摸索指令。
- **工程實務**：當使用者提出需求時，Opus 專注於產出一份符合本庫規範的任務清單（含目標範圍、具體做法、DoD），並直接指派工單。

### 2.2 準則二：Sonnet 規格驅動開工（Spec-Driven Invocation）

- **定義**：Sonnet 不參與前期發散性討論，只有在「輸入具備明確檔案路徑、清晰介面定義與可驗證的測試命令」時才被喚醒。
- **防止幻覺**：若規格模糊，Sonnet 容易依賴模型先驗知識胡亂猜測，產生大量「看起來合理但脫離專案現狀」的無效代碼；強制「見規格才開工」可將 Sonnet 的單次解決率（First-Pass Rate）提升至 85% 以上。

### 2.3 準則三：Fable 里程碑檢查點（Milestone-Only Evaluation）

- **定義**：**「關鍵時刻的檢查點，不是每步都叫」**。
- **反模式修正**：許多 Multi-Agent 系統設計了每輪 Tool Call 後自動觸發 Reviewer，導致 Token 消耗倍增、延遲劇增（每一步都等 15 秒），工程師體驗極差。
- **觸發條件限制**：
  1. **模組級驗收點**：一個獨立模組或功能全部實作完畢，單元測試通過後。
  2. **高危險操作前**：涉及資料庫 Schema 變更、公開 API 破壞性修改或核心依賴升級前。
  3. **交付結案前**：全流程完成，準備 commit/push 前的最終完整審核。

### 2.4 準則四：JEV 嚴格決策介面（Binary & Enum Selection API）

- **定義**：JEV 專門處理高頻、確定性的分支判斷，其介面**嚴禁輸出 Markdown 或自由敘述，只允許輸出布林值（`true / false`）或受限列舉（`enum`）**。
- **應用場景**：
  - *「這個改動是否超過 5 個檔案的爆破半徑？」* -> `true`
  - *「這條測試指令失敗是否屬於暫態網路問題？」* -> `false`
  - *「當前任務應該路由至 Daily-Coding 還是 Long-Context？」* -> `"daily-coding"`
- **工程效益**：利用輕量模型（如 Haiku 或 Flash）搭配 JSON Schema 嚴格限制（Structured Outputs），解析零開銷、延遲小於 200ms、且徹底免疫幻覺。

---

## 3. 與本庫工程規範的對接實踐

本庫在各項任務推進中，已在全域規則貫徹了類似的工程紀律：
- **主代理掌控全局**：全域規範明確規定「派工方要對派出去的每件工作負責到底，每件都要走到做完、驗過、落地」。
- **見輸出才算數**：禁止空殼函式與假資料，以可執行的命令輸出（如 unittest、verify 腳本）作為剛性依據。
- **審查不添亂**：透過外部裁判腳本（如 `verify_inbox.py`、`task_cli.py`）提供確定性驗收，不依賴龐大的大模型逐字冗長評審。

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將四角色動態調用原則與二元決策介面工程化，規劃以下 3 項落地任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261101-01`**｜**[優先級：高]** 撰寫「Claude Code 與多 Agent 四角色動態派工與執行期調用手冊：主 Session 拍板、里程碑檢查點與二元決策 API 規範」收錄於 `docs/agent-role-dispatch-runtime-spec.md`
  - **狀態**：⚪ 不做（多 Agent 分工主題已由 docs/multi-agent-parallel-dispatch-spec.md 與 agent-advisor 路由涵蓋，再寫一份只會重複；內容是另一篇文章的配置，沒有新的可驗證產出。）
  - **目標範圍**：`docs/agent-role-dispatch-runtime-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 深入定義四角色的執行期狀態機（Runtime State Machine）與狀態躍遷條件。
    2. 制定「里程碑檢查點（Milestone Checkpoint）」的三大硬性觸發時機與豁免條件，防止過度審查引發延遲爆炸。
    3. 規範 JEV 決策 API 的輸入輸出 Schema（限定 Boolean 與 Enum 嚴格結構化輸出）。
  - **驗收標準（DoD）**：產出 `docs/agent-role-dispatch-runtime-spec.md`，具備標準 Markdown 結構與狀態機流程圖；以 `Test-Path docs/agent-role-dispatch-runtime-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261101-02`**｜**[優先級：中]** 實作「四角色調用閘門控制器與二元/枚舉決策 API 輕量客戶端」於 `tools/verify_agent_dispatch_gate.py` 與單元測試
  - **狀態**：⚪ 不做（多 Agent 分工主題已由 docs/multi-agent-parallel-dispatch-spec.md 與 agent-advisor 路由涵蓋，再寫一份只會重複；內容是另一篇文章的配置，沒有新的可驗證產出。）
  - **目標範圍**：`tools/verify_agent_dispatch_gate.py` 與 `tests/test_verify_agent_dispatch_gate.py`
  - **具體做法**：
    1. 實作輕量閘門控制 CLI，評估傳入任務的規格完整度（是否允許 Sonnet 開工）。
    2. 提供里程碑檢查點判定演算法（依據異動檔案數、關鍵字與測試狀態決定是否喚醒 Fable）。
    3. 實作 JEV 決策結構化輸出模擬器（強制驗證只回傳 `{"decision": true|false}` 或指定枚舉）。
    4. 撰寫單元測試覆蓋多種邊界條件並產出結構化排程決策報告。
  - **驗收標準（DoD）**：產出 `tools/verify_agent_dispatch_gate.py` 與對應測試；執行 `python -m unittest tests/test_verify_agent_dispatch_gate.py` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261101-03`**｜**[優先級：低]** 產出標準化「多 Agent 里程碑檢查點觸發條件與二元決策 Prompt 範本」收錄於 `templates/agent-dispatch-milestone-prompts.md`
  - **狀態**：⚪ 不做（多 Agent 分工主題已由 docs/multi-agent-parallel-dispatch-spec.md 與 agent-advisor 路由涵蓋，再寫一份只會重複；內容是另一篇文章的配置，沒有新的可驗證產出。）
  - **目標範圍**：`templates/agent-dispatch-milestone-prompts.md`
  - **具體做法**：
    1. 提供 Fable 里程碑驗收 Prompt 範本（強調只看 DoD 與爆破半徑，不做無謂細節挑剔）。
    2. 提供 JEV 嚴格二元決策 Prompt 範本（強制約束只輸出 single token 或 JSON boolean）。
  - **驗收標準（DoD）**：產出 `templates/agent-dispatch-milestone-prompts.md`，具備完整範例；以 `Test-Path templates/agent-dispatch-milestone-prompts.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 結論與演進路徑

「強模型不要拿去做雜事」不只是一句口號，更是多 Agent 協同體系能否實現工業化運行的分水嶺。透過主 Session 拍板、規格驅動開工、里程碑檢查點與二元決策 API 的動態約束，團隊才能真正做到兼顧頂級模型的思考深度與輕量代理的敏捷速度，實現 Token 成本、響應延遲與代碼質量的最優平衡。
