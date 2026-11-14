---
id: "2026-11-15-multi-ai-20-dollar-role-routing-anti-fake-green"
title: "多模型分權省額與防假綠實戰評估：「$20×3 打敗 $200」PM／實作／QA 路由對照"
source_url: "N/A"
source_platform: "Social / Forum"
author: "匿名一線開發者（ERP／電商／遊戲化實戰經驗）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 1
cluster_role: "多模型省額角色路由"
short_title: "多AI分權省額路由"
tags:
  - model-routing
  - cost-optimization
  - multi-agent
  - anti-fake-green
  - hooks
  - context-management
---

# 多模型分權省額與防假綠實戰評估：「$20×3 打敗 $200」PM／實作／QA 路由對照

- **來源連結**：`N/A`（社群貼文：多帳號實戰後總結之「用 20 美方案打敗 200 美的省錢開發方法」）
- **發布平台 / 作者**：`社群平台` / `匿名一線開發者`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 實踐脈絡）**：實戰開發 ERP、電商與遊戲化系統的工程師；自述一個月內同時實測 5 個高階訂閱（Claude $200×2、Codex Astra $200×2、Grok $300×1）後改採分權省額架構。
- **What（核心產出 / 做了什麼）**：提出「**高階模型做規劃與 QA、低成本模型做一線實作**」的多模型分工，以及「**任務樹 + Hook 防漂移 + 三層防假綠**」的無人值守控管模式。
- **Why（為解決什麼問題 / 痛點）**：
  - 實際開發中，寫程式碼本身只消耗約 **10–20%** 的 Token，其餘 **80–90%** 全燒在「上下文膨脹、測試紅燈反覆修、單一 AI 自我驗證與合版前轉紅／假綠」。
  - 單一高價模型包辦全流程極易被高耗額機制（如 Astra）快速榨乾配額，且容易在長上下文後「丟西瓜撿芝麻」。
- **How（核心架構與關鍵機制）**：
  1. **雙軌省額路由**：
     - **同廠省法**（自稱省 20–30% Token）：Claude Opus 當 PM 討論 $\rightarrow$ 輕量模型（貼文稱 Fable）做 QA $\rightarrow$ 總結後交 Sonnet 開發。
     - **跨廠 `$20×3` 打敗 `$200` 組合**（自稱省 60–70%）：Claude Opus（PM／總綱設計） $\rightarrow$ Codex Astra high（QA／高強度審查） $\rightarrow$ DeepSeek / Kimi（低價一線實作）。
  2. **防漂移結構**：每個專案建立「總綱 $\rightarrow$ 大項目 $\rightarrow$ 子項目 $\rightarrow$ 細分 Task」任務包；每次開新對話（開席記憶）框住最外層目標；以 Context % 觸發自我總結並回頭對齊總綱。
  3. **Hook 機械護欄 ＋ 三層防假綠**：
     - 第一層：明確定義什麼是「假綠」與「真紅」（禁止騙過測試）。
     - 第二層：所有程式設追蹤／回測機制。
     - 第三層：多主機隔離驗證。
- **When & Where（適用時機與場景）**：需求邊界可被切分為細粒度 Task（如 ERP 表單、電商 CRUD、模組化開發）且具備可自動化驗證測試的專案。
- **Key Metrics / Numbers（宣稱數據，未經獨立基準驗證）**：
  - 寫碼佔總 Token 約 10–20%、上下文／測試／驗證佔 80–90%；同廠分工自稱省 20–30%、跨廠三角色分工自稱省 60–70%；三層防假綠自稱解決 80–90% 問題。（皆屬單一作者體感經驗值，無控制變因實驗記錄。）

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（已實證 Astra 相對 Sol 耗額達 5x–12x，與本文「Astra 燒極快、不宜包辦一線寫碼」完全互印）。
  - `SanHsien/agent-advisor`（已內建 `pro` / `flash` 雙層實作＋獨立 `pro-reviewer`）。
  - `SanHsien/harness-guard`（已實作防假綠、禁止註解測試／回傳假資料／未驗證宣稱結案的 Hook 閘門）。
  - `SanHsien/agent-relay`（已實作跨機派工、`accept` 本地複驗、`ask`/`answer` 決策流與 worktree 隔離）。
- **落差與採納判斷**：
  - **值得採納**：
    1. **「PM（高階推理）／一線實作（高配額低成本）／QA（獨立高強度審查）」三權分立模型**：這與維護者現有的 `Opus/Sol/Pro (規劃與審查)` ＋ `Terra/Flash/DeepSeek (一線實作)` 完全吻合，可直接沉澱進模型路由速查表作為角色分工範本。
    2. **Context 臨界點強制「總結並回對總綱」再換新 Session**：配合維護者既有的 `cc-session-reader` 與 `agent-handoff`，把換 Session 前回頭核對總綱（Roadmap / DoD）固化成標準動作，可避免多輪壓縮後偏離主軸。
  - **需保留警覺（勿盲信宣稱比例）**：
    1. 文中「省 60–70%」僅在「規格切得極細、一線低價模型不會寫出大量隱性 Bug」時成立；若核心架構複雜或重構牽涉跨檔不變量，低階模型產出的返工成本（Reviewer Tax）反而可能超過直接用中階主力模型（如 GPT-6.1 Terra / Sonnet）一次寫對的成本。
    2. 多數結構化護欄（Hook、三層隔離、開席記憶、跨機派工）維護者生態系已經實作完成，無須重造一套工具，僅需補齊路由矩陣文件對照即可。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-06`**｜**[優先級：低]** 於 `docs/model-burn-rate-routing-matrix.md` 增補「PM／一線實作／QA 三角分權路由樣板」與 Reviewer Tax 評估註記
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（可與 `T-20261114-03` 實測時一併更新）
  - **具體做法**：
    1. 在速查表新增一節對照「三角色分權路由」（高階模型負責 PM 拆解與最終 QA、高配額模型負責依規格一線實作），並標明來源可信度為【社群經驗，未經獨立基準驗證】。
    2. 補入「Context 臨界點回對總綱再換新對話」與「返工稅（Reviewer Tax）風險邊界」檢核提醒。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 完成增補且通過 `python tools/verify_inbox.py`。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
