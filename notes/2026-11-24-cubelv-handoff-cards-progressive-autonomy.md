---
id: "2026-11-24-cubelv-handoff-cards-progressive-autonomy"
title: "CubeLV 官方教學評析：《交件卡：一步一步，讓你的公司自己跑》——三級漸進式放手、條件式自動核准與多 Agent 人機協作介面設計"
source_url: "https://cubelv.com"
source_platform: "email (CubeLV 官方使用教學 PDF)"
author: "邱冠倫 (CubeLV 創辦人)"
analyzed_at: "2026-11-24"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 6
source_replies: 0
source_reviewed_at: "2026-11-24"
status: pending
cluster: 1
cluster_role: "交件卡漸進放手"
short_title: "CubeLV交件卡漸進放手"
tags:
  - cubelv
  - hitl
  - handoff-cards
  - progressive-autonomy
  - agent-orchestration
  - conditional-approval
  - ui-ux
---

# CubeLV 官方教學評析：《交件卡：一步一步，讓你的公司自己跑》——三級漸進式放手、條件式自動核准與多 Agent 人機協作介面設計

- **來源文件**：CubeLV 官方使用教學信件（標題：《交件卡：一步一步，讓你的公司自己跑》，`2026-10-27 09:53`，5 頁 PDF 全文＋6 張系統截圖）
- **產品官網 / 作者**：[`cubelv.com`](https://cubelv.com) / 邱冠倫（CubeLV 創辦人）
- **分析日期**：`2026-11-24`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md`](./2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md)（`feedback-desk` 雙層工單與 AI 分類轉人工交接）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（主 Session 拍板與子代理里程碑檢查點）
  - [`docs/system-one-decision-model-landscape.md`](../docs/system-one-decision-model-landscape.md)（確定性規則＋置信度灰區轉人工審批架構）
  - [`docs/deterministic-gtd-agent-harness-spec.md`](../docs/deterministic-gtd-agent-harness-spec.md)（確定性待辦狀態機與交接契約）

---

## 0. 原始資料盤點（5 頁教學 PDF 正文與 6 張系統截圖）

- **正文核心架構**：
  1. **待批閱（Review Inbox）雙層分類**：AI 員工執行至需要人類決定的節點時，產出「交件卡」送入待批閱區；頂層依「部門」分頁（截圖顯示：研發部 `55`、客服部 `36`、功能優化部 `5`、指標實驗部 `1`），次層依「卡種」過濾（客服部含：評論回覆 `12`、來信回覆 `1`、聊天室求助 `23`）。
  2. **極簡單卡決策動作**：每張卡只要求人類做一個決定；人類拍板後，若流程圖下游還有接手的 AI 員工，平台自動喚醒下一步執行。
  3. **三級漸進式放手（「交件設定」）**：所有卡種可獨立切換三種授權模式——「交給我核准」「看條件」「直接做」，無需一開始就全自動放行。
- **6 張截圖逐張盤點**：
  - **圖 1（待批閱與 Google Play 評論回覆卡）**：展示部門／卡種篩選列、右上角「交件設定」齒輪，以及 `Google Play` 評論卡片（星等、日期、原文評論在上，可編輯的 AI 擬稿回覆在下，底部按鈕為「刪除」「核准送出」）。
  - **圖 2（App Store 評論回覆卡）**：展示五星評論與對應擬稿回覆之即時修改與送出介面。
  - **圖 3（研發部工程開工卡）**：標示 `新功能`、`1 筆回報`、`開卡 10/13(12天前)`、`回報 10/13(12天前)`，標題為「讓插件能輸出 Word (.docx) 檔，支援以既有範本填值」，下方列出背景原因、影響與可折疊 `> 細節`，底部為四個明確狀態按鈕：**「不做」「已處理」「附指示」「同意開工」**。
  - **圖 4（待批閱設定 / 交件設定面板）**：依部門分組列出各卡種（如研發部的「工程開工」註明「和客服部共用這個設定」；客服部的「評論回覆」設為「看條件」），每列固定三段式切換器：`交給我核准` ｜ `看條件` ｜ `直接做`。
  - **圖 5（工作流架構圖中的放手節點）**：節點流程為 `海巡目標收集員` →（`交出提案`）→ `海巡提案 [直接做]` → `海巡回覆員`，說明切成「直接做」後，上游收集員產出提案即直接喚醒下游回覆員接手。
  - **圖 6（「看條件」規則編輯器與存量追認）**：評論回覆設為「看條件」後，顯示規則列 `星等` `≥` `4`（`欄位` + `比法` + `值`）與 `+ 加條件` 按鈕，下方提示「達成上述條件時直接做不經過核准」，並即時計算存量符合數（「`待批閱裡有 11 張符合`」＋「`現在核准`」一鍵批次送出按鈕）。
- **留言／互動**：`0` 則（本件為官方教學電子郵件，無公開留言區）。

---

## 1. 核心機制與工程設計亮點拆解

```text
[AI 員工執行至關鍵決策點] ──► 產生「交件卡」並觸發 [交件設定] 路由器
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       ▼                           ▼                           ▼
 [1. 交給我核准]            [2. 看條件 (Hybrid Gate)]    [3. 直接做 (Auto)]
  全部進待批閱佇列           欄位 + 比法 + 值 (如 星等 ≥ 4)   自動核准並立即喚醒
  (冷啟動觀察期)              ├─ 符合條件 ──► 直接送出       下游接手 Agent
                              └─ 不符條件 ──► 進待批閱       (如 收集員→回覆員)
```

1. **解決「全人工太累 vs. 全自動太危險」的冷啟動困境**：
   傳統 Agent 工具常迫使使用者在「每次都要按確認」與「開啟全自動（YOLO/Turbo）盲跑」之間二選一。CubeLV 將授權顆粒度切分到**「單一業務卡種（Card Type）」**，讓維護者可以先把無風險或高重複度的節點（如海巡提案）切為「直接做」，高客訴風險的節點（三星以下負評）留在待批閱，實現可逆的**漸進式放手（Progressive Autonomy）**。
2. **「確定性欄位條件」結合「CEO 自然語言補欄位」**：
   規則判斷本身採純確定性結構（`欄位 + 比法 + 值`），零推論延遲且完全可預測；唯有當卡片還缺少所需欄位時，才由使用者按「請 CEO 加條件」用自然語言描述分流標準（如「金額超過一萬元的交給我，其他直接做」），由高層編排器為該卡種補上結構化欄位，兼顧了配置彈性與執行期確定性。
3. **跨部門共用卡種設定與「存量追認（`現在核准`）」**：
   同一種卡（如「工程開工」）在不同部門共用同一套批閱政策，避免規則分叉；當規則放寬時，介面主動掃描既有的待批閱佇列並顯示「待批閱裡有 N 張符合」提供一鍵批次放行，消除規則變更後的積壓清理成本。

---

## 2. 與本專案現有架構的對照與啟發

- **與 `ai-inbox` / `agent-relay` 的互補點**：
  1. 本專案的 [`tools/task_cli.py`](../tools/task_cli.py) 與 `agent-relay` 已具備「待辦開卡、認領、結案（`不做` / `已做`）與門鈴喚醒」骨架，對應 CubeLV 開工卡的四個按鈕（「不做」「已處理」「同意開工」）；但目前缺少 **「附指示（Approve with Guidance）」**（在放行時順手補一行指令直接寫入下游上下文）以及 **「依任務／卡種分級的條件式自動放行規則」**。
  2. 在 [`docs/system-one-decision-model-landscape.md`](../docs/system-one-decision-model-landscape.md) 中，已設計「確定性規則 + System One 灰區轉人工審批」模型；CubeLV 的三段式政策切換器（`交給我核准` / `看條件` / `直接做`）與存量掃描追認 UX，正可作為日後設計本地 Agent 審批儀表板或 `agent-relay` 派工閘門政策的標準參考模型。
- **證據邊界提醒**：
  - 本筆記內容出自 CubeLV 創辦人自身的產品教學信件與帳號截圖（一手介面展示），未揭露「請 CEO 加條件」背後的底層解析實作、失敗率或大型團隊權限控管細節，僅作為人機協作（HITL）介面設計與漸進授權狀態機之架構參考。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261124-02`**｜**[優先級：低]** 萃取 CubeLV「交件卡三級漸進放手（交給我核准／看條件／直接做）」與存量追認模式，整理為多 Agent 人機協作審批閘門設計參考並補入 `docs/system-one-decision-model-landscape.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\system-one-decision-model-landscape.md`（收錄於集群 3，新增人機協作漸進放手設計模式節）
  - **執行步驟**：
    1. 在 `docs/system-one-decision-model-landscape.md` 補充 CubeLV 的「部門 × 卡種」批閱收件匣、三段式授權切換器（全人工／確定性欄位條件／自動直通）以及「附指示」放行原語。
    2. 對照說明如何將「確定性欄位條件（`欄位 + 比法 + 值`）」作為 System One 閘門的前置零成本過濾層，並註明來源為創辦人教學信件截圖（不含底層實作或故障率數據）。
  - **驗收標準（DoD）**：`docs/system-one-decision-model-landscape.md` 納入三級漸進放手與條件式自動核准設計模式，且 `python tools/verify_inbox.py` 驗證通過。
