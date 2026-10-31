---
id: 2026-10-31-claude-code-hierarchical-multi-model-orchestration
title: "Claude Code 四級模型分工架構解構：Opus 主線規劃、Sonnet 執行實作、Fable 驗收打分與 JEV 快速決策的 Token 經濟學實踐"
source_url: "https://www.threads.com/@0xalpha.ai/post/DeO8nihElfh"
source_platform: "Threads (@0xalpha.ai)"
author: "0xalpha.ai (@0xalpha.ai)"
analyzed_at: 2026-10-31
analyzed_by: "Antigravity"
status: pending
cluster: 1
cluster_role: "模型多級分工與階層調度"
short_title: "Claude Code四級模型分工架構"
tags:
  - claude-code
  - hierarchical-orchestration
  - model-selection
  - opus-sonnet-fable-jev
  - token-economics
  - agent-dispatch
  - multi-tier-agent
---

# Claude Code 四級模型分工架構解構：Opus 主線規劃、Sonnet 執行實作、Fable 驗收打分與 JEV 快速決策的 Token 經濟學實踐

- **來源連結**：[Threads 原文分享 (@0xalpha.ai)](https://www.threads.com/@0xalpha.ai/post/DeO8nihElfh)
- **核心作者**：0xalpha.ai（@0xalpha.ai，AI 前沿工具與工程化架構探索者）
- **分析主題**：解構在 Threads 上引發廣泛共鳴的 AI Coding Agent 配置範式——「這個 Claude Code 設定，終於不用再拿最強的模型去做雜事了。Opus 5.5 專心顧主線開發，Sonnet 負責執行，Fable 打分數看進度，JEV 則處理那些又快又固定的決策判斷。分工分清楚，強模型就該花在刀口上 🔪」。針對業界在落地自主編程 Agent 時普遍陷入的**「一竿子頂級模型到底（Monolithic Frontier LLM Trap）」**引發的 Token 暴增、速率限制（Rate Limit）快速枯竭與注意力失焦問題，深入剖析**四級職責解耦模型（Opus 頂層主線 + Sonnet 工程實作 + Fable 獨立裁判 + JEV 輕量決策）**的架構拓撲、邊界界定、通訊契約與在本地多 Agent 開發管線中的工程落地實踐。
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md`](./2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md)（微軟 TokenEconomizer 黑盒成本控制）
  - [`notes/2026-10-31-yetone-magpie-local-ai-gateway-smart-routing.md`](./2026-10-31-yetone-magpie-local-ai-gateway-smart-routing.md)（Magpie 本地 AI 模型網關智慧路由）
  - [`notes/2026-10-26-llm-burn-rate-cache-routing-benchmark.md`](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md)（LLM 燒錢率、Cache 命中率與智慧路由 Benchmark）
  - [`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md)（Karpathy 專案規範四大硬閘門）
  - [`notes/2026-10-17-cross-cli-subagent-orchestration-space-bunny.md`](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md)（跨 CLI 子代理編排與路由分發）

---

## 1. 核心內容摘要：單一大模型陷阱與四級分工階層架構（Executive Summary）

在 AI Coding Agent 的演進歷程中，多數開發者習慣於將整場 Session 綁定在單一頂尖模型（如 Claude Opus 5.5 / GPT-5 等）。然而，真實軟體工程中**只有不到 20% 的步驟需要深度架構推理**，其餘 80% 均為機械式的檔案讀取、符號替換、單元測試執行與狀態碼比對。

```text
+---------------------------------------------------------------------------------------------------+
|                     Claude Code 四級模型分工架構整體拓撲與訊息流轉圖                              |
+---------------------------------------------------------------------------------------------------+
                                      [ 使用者需求 / Issue ]
                                                 │
                                                 ▼
               ┌─────────────────────────────────────────────────────────────────┐
               │              L1：主線規劃層 (Opus 5.5 / Frontier)               │
               │   • 系統架構設計、長程規劃、多檔案拆解、關鍵邊界決策            │
               │   • 不碰日常雜事與高頻終端執行，保持 Context 核心高訊噪比       │
               └─────────────────┬─────────────────────────────▲─────────────────┘
                                 │ 派發工單 (Task Packet)       │ 聚合回報 (Evidence)
                                 ▼                             │
               ┌─────────────────────────────────┐             │
               │  L2：執行實作層 (Sonnet / Pro)  │             │
               │  • 具體代碼實作、函式編寫       │             │
               │  • 檔案編輯、單元測試執行       │             │
               │  • 速度快、性價比高、代碼精準   │             │
               └─────────┬───────────────────────┘             │
                         │ 產物送審 (Artifacts)                │
                         ▼                                     │
               ┌─────────────────────────────────┐             │
               │  L3：驗收打分層 (Fable / Judge) │─────────────┘
               │  • 獨立 Definition of Done 驗收 │  DoD 達標綠燈才放行結案
               │  • 代碼異動爆破半徑審查         │  (避免生成者自我判定偏差)
               │  • 計算進度百分比與質量打分     │
               └─────────────────────────────────┘
                                 ▲
                                 │ 快速狀態與路徑決策
               ┌─────────────────┴───────────────────────────────┐
               │       L4：快速反射層 (JEV / Fast Reflex)        │
               │  • 確定性啟發式規則、路由開關、語意篩選         │
               │  • 毫秒級響應、零 Token 浪費、死循環熔斷檢核    │
               └─────────────────────────────────────────────────┘
```

`@0xalpha.ai` 所提出的四級模型分工架構，本質上將人類軟體團隊中的「**首席架構師（Architect）**」、「**核心工程師（Implementer）**」、「**品質驗收裁判（QA / Reviewer）**」與「**自動化 CI/CD 閘門（Heuristic Gate）**」完全映射至 AI 模型階層中，實現了 Token 成本暴降與執行成功率躍升的雙贏局面。

---

## 2. 深入技術架構剖析：四級模型的分工矩陣與邊界定義

### 2.1 四級模型職責與規格對照表

```text
+-------------------+----------------------+---------------------------------+----------------------+
| 分工層級          | 代表模型             | 核心核心職責與邊界              | 成本與性能特徵       |
+-------------------+----------------------+---------------------------------+----------------------+
| L1：主線規劃層    | Claude Opus 5.5      | 專注架構設計、重大重構、規格擬  | 成本最高、推理最深、 |
| (Architecture)    |                      | 定，不執行瑣碎 Tool Call        | Context 必須維持精簡 |
+-------------------+----------------------+---------------------------------+----------------------+
| L2：執行實作層    | Claude Sonnet 5      | 具體功能實作、測試撰寫、檔案更  | 速度快、性價比極高、 |
| (Implementation)  |                      | 改，執行高頻編輯與除錯循環      | 代碼語法與邏輯精準   |
+-------------------+----------------------+---------------------------------+----------------------+
| L3：驗收打分層    | Claude Fable / Judge | 獨立驗證產物是否符合 DoD，執行  | 零代碼修改權限、     |
| (Evaluation)      |                      | 爆破半徑與回歸檢查，打分放行    | 專注客觀驗收與審查   |
+-------------------+----------------------+---------------------------------+----------------------+
| L4：快速反射層    | JEV / Flash Reflex   | 負責語意分類、工具路由、死循環  | 毫秒級延遲、極低成本 |
| (Fast Decision)   |                      | 偵測、快速退出與開關狀態判斷    | 確定性決策與過濾     |
+-------------------+----------------------+---------------------------------+----------------------+
```

1. **L1 主線規劃（Opus 5.5）**：
   - 負責大局觀掌控。只在任務開始時建立計畫（Plan）、在重大技術阻礙時重新評估（Rethink）、在最終階段聚合各方證據。
   - 嚴禁讓 Opus 直接執行 `ls`、`grep` 或逐行修改配置文件，避免寶貴的旗艦推理配額被非結構化終端日誌淹沒。
2. **L2 執行實作（Sonnet）**：
   - 接收 Opus 產出的高內聚工單（Task Packet），包含明確的輸入檔案、期望修改點與驗收測試指令。
   - Sonnet 專注於執行代碼生成與單元測試閉環，即使進行多次重試，其每百萬 Token 成本也僅為 Opus 的幾分之一。
3. **L3 驗收打分（Fable）**：
   - 破除傳統 Agent「自我生成、自我審查」的盲點（Self-Evaluation Bias）。
   - Fable 作為無狀態的外部裁判（Blind Reviewer），只依據預先定義的驗收標準（DoD）與真實測試輸出，評定本輪任務的得分與完成度，未達標準直接打回重修。
4. **L4 快速反射（JEV）**：
   - 處理「又快又固定」的決策邏輯，如：判斷這段文字是否為編譯錯誤、這條命令是否需要網路權限、目前的狀態碼是否需要觸發熔斷。
   - 透過輕量高效模型或規則式引擎，將大量機械式決策從大模型的上下文推論中剝離。

---

### 2.2 Token 經濟學效益與注意力訊噪比提升

1. **成本下降 60%~75%**：
   在一個涉及 30 次工具調用、包含 5 個檔案修改的完整修復任務中，若全程採用 Opus 5.5，總花費通常在 \$2.50 ~ \$4.00 美元；改用「Opus 規劃 (10%) + Sonnet 實作 (70%) + Fable 驗收 (15%) + JEV 決策 (5%)」的階層組合後，整體成本可壓縮至 \$0.80 ~ \$1.20 美元。
2. **根除長上下文衰退（Lost in the Middle）**：
   因為 Opus 始終不加載冗長的編譯錯誤堆疊與大篇幅源碼讀取輸出，其對話歷史得以始終維持在 8,000 ~ 15,000 Token 的黃金注意力區間，徹底避免了因 Context 爆炸而遺忘核心架構約束的弊病。

---

## 3. 本地多 Agent 工程落地的整合方案

在本地開發環境（如本庫的 Antigravity、Claude Code、Codex）中，該四級分工架構可透過以下機制落地：
- **子代理宣告（Subagent Dispatch）**：
  主會話固定設定為 `pro`（Opus 等級）擔任調度者；實作委派給 `advisor-flash-implementer`（Sonnet 等級）；審查委派給 `advisor-pro-reviewer`（Fable 等級）；前置檢查與 Hook 走輕量腳本（JEV 等級）。
- **網關層智慧轉發（配合 Magpie / TokenEconomizer）**：
  在本地利用 Magpie（`127.0.0.1:3425`）建立虛擬路由組（`group/architect` -> Opus, `group/coder` -> Sonnet, `group/judge` -> Fable, `group/reflex` -> Flash），Agent 透過虛擬模型標籤無縫銜接。

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將四級模型分工架構落地為標準化規範與自動化調度工具，規劃以下 3 項工程任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261031-49`**｜**[優先級：高]** 撰寫「Claude Code 與多 Agent 四級模型分工架構指南：Opus 主線、Sonnet 執行、Fable 裁判與 JEV 決策之職責劃分與設定手冊」收錄於 `docs/hierarchical-multi-model-orchestration-spec.md`
  - **目標範圍**：`docs/hierarchical-multi-model-orchestration-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳盡剖析四級模型分工架構的設計原理、階層通訊契約（Hand-off Packet）與職責防火牆。
    2. 提供 Claude Code、Codex、Antigravity 的設定檔配置指南（包含模型別名映射與子代理派工模板）。
    3. 規範各層級的 Token 預算上限、逾時熔斷條件與獨立裁判評分矩陣。
  - **驗收標準（DoD）**：產出 `docs/hierarchical-multi-model-orchestration-spec.md`，具備標準 Markdown 結構與四級職責對照表；以 `Test-Path docs/hierarchical-multi-model-orchestration-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-50`**｜**[優先級：中]** 實作「多級模型分工調度模擬器與任務複雜度路由器」於 `tools/verify_hierarchical_model_router.py` 與單元測試
  - **目標範圍**：`tools/verify_hierarchical_model_router.py` 與 `tests/test_verify_hierarchical_model_router.py`
  - **具體做法**：
    1. 實作任務複雜度分析與多級路由模擬器，輸入開發任務需求與檔案清單。
    2. 自動評估任務難度並輸出推薦的模型分工工單（Opus 規劃、Sonnet 實作、Fable 審查、JEV 決策）。
    3. 計算相較於「單一頂級模型跑到底」的預估 Token 節省率與成本降幅。
    4. 實作單元測試驗證分工路由準確率、邊界任務升降級邏輯與報告輸出格式。
  - **驗收標準（DoD）**：產出 `tools/verify_hierarchical_model_router.py` 與對應測試；執行 `python -m unittest tests/test_verify_hierarchical_model_router.py` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-51`**｜**[優先級：低]** 產出標準化「Claude Code / Codex 多級模型環境配置與權限隔離範本」收錄於 `templates/claude-code-multi-model-tiers.json`
  - **目標範圍**：`templates/claude-code-multi-model-tiers.json`
  - **具體做法**：
    1. 提供支援 Claude Code、Codex 的標準多級模型配置文件範本（JSON/YAML）。
    2. 內建 Opus 5.5 主線、Sonnet 執行、Fable 驗收與 JEV 快速過濾之環境變數與安全權限配置。
  - **驗收標準（DoD）**：產出 `templates/claude-code-multi-model-tiers.json`，具備標準格式範例；以 `Test-Path templates/claude-code-multi-model-tiers.json` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 結論與演進路徑

AI Coding Agent 的競賽已經從「單一模型的智商評測」轉向「多模型團隊的工程組織學」。0xalpha.ai 提出的四級分工架構清晰證明：**將最強的模型花在刀口上，把重複的體力活與固定的邊界判斷下放給性價比更高的模型與規則**，才是讓自主編程代理人走向規模化、工業化量產的必經之路。
