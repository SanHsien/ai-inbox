---
id: "2026-11-15-multi-ai-20-dollar-role-routing-anti-fake-green"
title: "多模型分權省額與防假綠實戰評估：「$20×3 打敗 $200」PM／實作／QA 路由對照"
source_url: "N/A"
source_platform: "Social / Forum"
author: "匿名一線開發者（ERP／電商／遊戲化實戰經驗）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
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
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 實踐脈絡）**：實戰開發 ERP、電商與遊戲化系統的工程師；自述一個月內同時實測 5 個高階訂閱（Claude $200×2、Codex Astra $200×2、Grok $300×1）後改採分權省額架構。
- **What（核心產出 / 做了什麼）**：提出「**高階模型做規劃與 QA、低成本模型做一線實作**」的多模型分工，以及「**任務樹 + Hook 防漂移 + 三層防假綠**」的無人值守控管模式。
- **Why（為解決什麼問題 / 痛點）**：
  - 【社群宣稱】作者自述（未獨立驗證）：實際開發中，寫程式碼本身只消耗約 **10–20%** 的 Token，其餘 **80–90%** 燒在「上下文膨脹、測試紅燈反覆修、單一 AI 自我驗證與合版前轉紅／假綠」。
  - 【社群宣稱】作者認為單一高價模型包辦全流程容易被高耗額機制（如 Astra）快速用完配額，且容易在長上下文後「丟西瓜撿芝麻」。
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
  - 可信度標記沿用 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 第 0 節；本筆記所有比例都是【社群宣稱】，第 1 節各處的「自稱」「作者認為」皆同此級。
  - 寫碼佔總 Token 約 10–20%、上下文／測試／驗證佔 80–90%；同廠分工自稱省 20–30%、跨廠三角色分工自稱省 60–70%；三層防假綠自稱解決 80–90% 問題。（皆屬單一作者體感經驗值，無控制變因實驗記錄。）

---

## 1.1 CQR 論證檢驗

- **Claim（核心主張）**：三個 20 美元方案分工，可比單一 200 美元方案省 60–70% 額度。
- **Evidence（證據）**：只有作者一個月的多帳號使用體感；沒有同任務對照、沒有 token 紀錄，也沒有返工次數。
- **Reasoning（推論與局限）**：證據不足以支撐固定比例。省多少取決於規格切得多細、低價模型返工多少；本筆記所有比例都只當作者宣稱，不當實證。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（該文件第 0～3、8 節說明：官方 API 單價 Astra 約為 Sol 的 5 倍；12 倍是另一位作者在不同任務下（兩者同為 $100 帳號）的週額度消耗速度比，未獨立重現，兩者不是同一種量測。所以只能說本文「Astra 燒得快」的體感與它方向一致，不是已實證的固定倍率；四種數字的分級對照見該文件第 10.2 節）。
  - `SanHsien/agent-advisor`（已查到的兩個版本都是「implementer＋獨立 reviewer」：Claude Code 版為 Sonnet／Haiku implementer＋Opus reviewer，Antigravity 版為 `pro`／`flash` implementer＋`pro-reviewer`；其餘 runtime 版本未查證。Claude Code 版的路由是 solo／delegate／audit／full 四選一，預設 solo）。
  - `SanHsien/harness-guard`（已實作防假綠、禁止註解測試／回傳假資料／未驗證宣稱結案的 Hook 閘門）。
  - `SanHsien/agent-relay`（已實作跨機派工、`accept` 本地複驗、`ask`/`answer` 決策流與 worktree 隔離）。
- **落差與採納判斷**：
  - **值得採納**：
    1. **「PM（高階推理）／一線實作（高配額低成本）／QA（獨立高強度審查）」角色分工**：可當參考樣板，但不能直接套用。維護者現行做法是依風險在 solo／delegate／audit／full 四種路由擇一，預設 solo，不是每個任務都固定跑三個角色；模型與 effort 要用當下已驗證的完整配對，不能把文中的 Astra high 直接換成本機主力模型。原文用 DeepSeek／Kimi 做一線實作是作者的經驗，這兩個是中國服務，不列入維護者的建議路由。四種路由的書面案例（小型 solo、規格完整 delegate、有風險 audit）與 full 的例外條件見 `docs/model-burn-rate-routing-matrix.md` 第 10.3、10.4 節；那些是文件案例，沒有重跑 benchmark。
    2. **Context 臨界點強制「總結並回對總綱」再換新 Session**：配合維護者既有的 `cc-session-reader` 與 `agent-handoff`，把換 Session 前回頭核對總綱（Roadmap / DoD）寫成短清單（同文件第 10.6 節）。「可避免多輪壓縮後偏離主軸」是貼文的說法【社群宣稱】，效果未量測。
  - **需保留警覺（勿盲信宣稱比例）**：
    1. 文中「省 60–70%」是【社群宣稱】，沒有嘗試次數與返工紀錄，在任何條件下都未經驗證；規格切得再細也不能當成會成立的比例。依現行 cost-policy，每件合格交付成本要把失敗、審查與重做全部算進去：若核心架構複雜或重構牽涉跨檔不變量，低價模型的返工成本可能超過由主代理一次做完的成本（同文件第 10.5 節）。這是推論，同樣沒有實測。
    2. 多數結構化護欄（Hook、三層隔離、開席記憶、跨機派工）維護者生態系已經實作完成，無須重造一套工具，僅需補齊路由矩陣文件對照即可。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-06`**｜**[優先級：低]** 修正模型路由文件的證據分級，補上符合現行 solo／delegate／audit／full 的成本示例
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/model-burn-rate-routing-matrix.md` 與對應 2026-11-15 多模型筆記。
  - **具體做法**：區分 API 單價、不同任務的訂閱耗額比與社群估算，移除把 5x～12x 或省 60～70% 當固定實證的敘述；增補四路由對照與返工成本限制。只引用當前已驗證完整模型／effort 配對，不把三角色流程當每任務固定支出；不建議中國服務、不新增付費訂閱。加入換 session 前核對 ROADMAP／DoD 的短清單。
  - **驗收標準（DoD）**：文件與筆記的可信度標記一致；至少列出小型 solo、規格完整 delegate、風險需要 audit 的三個書面案例，另說明 full 的例外條件。標明這是文件案例、沒有重跑模型 benchmark。核對不違反現行 user policy，並通過 repo 規定文件檢查；不以格式檢查聲稱省額比例成立。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15，commit 87d0d1a、442d073）：docs/model-burn-rate-routing-matrix.md 第 0 節證據分五級，新增第 10 節（10.2 把 5 倍、3.5 倍、12 倍、省 60–70% 拆成不同性質的數字；10.3 路由與配對照抄已安裝 orchestration SKILL.md；10.4 solo／delegate／audit 三個書面案例加 full 例外；10.5 成本公式；10.6 換 session 前核對清單），筆記同步改標社群宣稱。未重跑 benchmark，第 9 節沒動。Fable 獨立複審後修 2 處必修。
