---
id: "2026-11-24-lichangzhang-4-ai-employees-workflow-patterns"
title: "李廠長來了 YouTube 實作評析：《我給自己招了4個AI員工，每週省下8小時！》——單代理四角色工作流、漸進授權階梯與「幫我找 vs 幫我讀」二元契約"
source_url: "https://youtu.be/0X5CVapfqPQ"
source_platform: "youtube"
author: "李厂长来了 (@lichangzhanglaile)"
analyzed_at: "2026-11-24"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 83
source_reviewed_at: "2026-11-24"
source_review_note: "已完整解析影片資訊欄（含 4 組指令詞與 7 段章節）、全片 15:29 音訊 Whisper 逐字稿（607 段）及全部 83 則 YouTube 留言；未擷取影片畫面截圖。"
status: pending
cluster: 1
cluster_role: "單代理四角色工作流"
short_title: "李廠長4個AI員工工作流評析"
tags:
  - ai-agent
  - claude-cowork
  - chatgpt-work
  - prompt-engineering
  - hitl
  - progressive-autonomy
  - contract-review
  - voice-mode
---

# 李廠長來了 YouTube 實作評析：《我給自己招了4個AI員工，每週省下8小時！》——單代理四角色工作流、漸進授權階梯與「幫我找 vs 幫我讀」二元契約

- **來源影片**：[`youtu.be/0X5CVapfqPQ`](https://youtu.be/0X5CVapfqPQ)（頻道：`李厂长来了`，發布於 `2026-09-26`，片長 `15:29`，`268,023` 次觀看、`3,108` 讚、`83` 則留言）
- **分析日期**：`2026-11-24`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-11-24-cubelv-handoff-cards-progressive-autonomy.md`](./2026-11-24-cubelv-handoff-cards-progressive-autonomy.md)（三級漸進式放手與人類核准邊界）
  - [`notes/2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md`](./2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md)（`ChatGPT Work` / Connectors 與 Skills 實戰對照）
  - [`docs/agent-memory-and-prompting-best-practices.md`](../docs/agent-memory-and-prompting-best-practices.md)（Agent 提示詞與工作流最佳實踐目標文件）

---

## 0. 原始資料盤點（資訊欄、15:29 音訊逐字稿與 83 則留言）

- **影片章節（7 段）**：`00:00` 4個AI員工 → `01:07` 助手一（管家）→ `04:44` 助手二（製作人）→ `07:15` 助手三（翻譯）→ `10:24` 助手四（陪練）→ `13:03` 人類的價值 → `14:41` 行動清單。
- **核心架構澄清（留言 #20–21 關鍵問答）**：
  - 觀眾 `@wwang2806` 質疑：四個助手都在 `Claude Cowork` 內運行，為何稱為「四個員工／團隊」而非多個獨立協調的 Sub-agents？
  - 作者 `@lichangzhanglaile` 於留言 #21 明確承認：**這並非真正的多 Agent 平行協作系統（Multi-Agent System），而是將單一 AI Agent（`Claude Cowork` / `ChatGPT Work` / `Gemini Spark`）的四種職責場景比喻為四個職位**，藉此降低非技術背景觀眾的心智門檻。
- **其餘留言重點**：
  - **AI 董事會實作方式（留言 #5–6）**：作者澄清「AI 董事會」是人工把 Claude 結論貼給 ChatGPT／Gemini 交叉檢查的方法論，非 Claude 內建功能或 MCP 連線。
  - **Outlook / M365 權限分層（留言 #75–79）**：使用 Claude Microsoft 365 Connector 時，公司信箱通常需 IT 管理員核准，且「讀取」與「草擬／自動發送」為獨立權限，建議初期僅開整理與草擬、不開自動發送。
  - **工具橫評（留言 #44–45、#66–67、#71–72）**：均需約每月 20 美元付費方案；作者排序以 `ChatGPT Work` 與 `Claude Cowork` 為首選，`Gemini Spark` 勝在 Google Workspace 雲端長駐與低門檻，`Grok Bot` 偏開發與 X 深度整合，`Meta Muse` 則因近期出現隱私與權限問題建議謹慎。

---

## 1. 四個角色工作流與可復用工程模式拆解

### 1.1 助手一：AI 管家（Gmail + Google Calendar 漸進授權階梯）
- **五要素指令結構**：`任務 + 工具 + 分類 + 輸出 + 邊界`。
  - 範例邊界：「緊急那類按我的語氣起草回覆並放進草稿箱；**沒有我明確說發送，一封郵件都不許發出去**」。
- **四階漸進授權階梯**（對應《先可見 → 再高效 → 再自動化 → 最後交出執行權》）：
  1. **唯讀分類＋草稿**：只接 Gmail，對過去 24 小時未讀信分三類（緊急／一般／忽略）並進草稿箱。
  2. **跨工具對照**：加入 Google Calendar 唯讀權限，對照緊急郵件輸出三件事（衝突點／會前必備準備／可延後事項）。
  3. **定時排程**：跑順十幾次後，改設每天早上自動執行。
  4. **有限寫入**：最後才授權行事曆寫入（例如本周找兩個不同天的 30 分鐘空檔排入「跑步」）。

### 1.2 助手二：AI 製作人（零散筆記 → 成品檔案）
- **四項強制輸出規格**：`給誰看、多長（頁數/時長）、什麼格式、什麼語氣`，缺一即產出平庸內容。
- **開工前一次性追問閘門（Ask-Before-Guessing）**：
  - 指令明確要求：「開始之前凡是筆記裡交代不清楚的地方，先一次性把問題問我，**別自己猜**」——在寫作或產檔前先收斂規格歧義，大幅降低返工。
- **Skill 化交付**：透過 `Cowork` / `Work` 內建的 PPTX/DOCX/XLSX/PDF Skills 生成可直接編輯的實體檔案，人類退居「導演」角色做頁級微調；進階可將個人品牌範本封裝為專屬 Skill 統一版型。

### 1.3 助手三：AI 翻譯（「幫我找」vs「幫我讀」二元契約＋AI 董事會）
- **嚴格區分「幫我找（外部蒐證）」與「幫我讀（單檔深讀）」**：
  - **「幫我找」**（跨網頁搜尋＋已連線的 Gmail 時間線整合）：每條結論強制附出處連結、不確定直接標 `"待確認"`、禁止推測，並搭配 7 字校對口訣：**「請核實」「簡潔一點」**。
  - **「幫我讀」**（合約、保單、租約等單檔條款審查）：**明確禁止摘要（`不要給我摘要`）**，因為風險全藏在細節；強制逐條讀完並輸出 **5 欄表格**：
    `條款原文 | 大白話解釋 | 為什麼這條重要 | 風險等級 | 我該回去問對方的問題`
- **AI 董事會交叉驗證**：將 Claude 產出交給 ChatGPT 與 Gemini 複核——**三個模型互相打架（分歧）的地方，往往就是真正的風險點**。
- **隱私邊界**：初期先用公開條款／報告演練，熟練後再評估敏感財務或證件文件是否適合上傳。

### 1.4 助手四：AI 陪練（語音模式四步模擬迴圈）
- **流程**：(1) 餵飽背景（公司、JD、履歷、求職信、想強調重點）→ (2) 角色扮演帶懷疑精神的招募經理（一次一問，答得空洞即追問反駁）→ (3) **手機語音模式開口實練**（不打字）→ (4) 脫離角色切換為「教練」，指出說服力不足／卡殼／囉嗦處、針對最差 3 題給 60 秒內參考回覆，並收斂成 **1 頁考前 5 分鐘速記卡**。

---

## 2. 評估與對現有系統的啟發

- **可採納的高價值模式**：
  1. **「幫我讀」禁摘要＋5 欄風險稽核表契約**：極適合收錄為本庫規格文件與文件審查提示詞標準——審查合約、安全條款或長規格時，要求 Agent 禁止摘要、改以結構化逐條風險表輸出。
  2. **「開始前先一次性問清楚，別自己猜」前置追問閘門**：與本庫既有的規格釐清原則高度互補，可作為多步驟產出任務的通用前置句式。
  3. **跨模型對帳（「分歧點即風險點」）**：以結構化方式呼應多模型交叉審查邏輯。
- **需標註限制與不採納處**：
  - **「四個員工」僅為單代理角色隱喻**：不應誤當成多 Agent 平行編排架構（Multi-Agent Orchestration）。
  - **片中引用之第三方統計數據**（如微軟 *Breaking Down the Infinite Workday* 日均 117 封信／被打斷 275 次、JDP 調查 93% 面試焦慮／70% 出聲練習、Pew 2025 調查 64% vs 39%）為影片轉述之二手數字，本筆記僅記錄出處宣稱，未獨立查證原始報告。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261124-03`**｜**[優先級：低]** 補充單代理五要素結構、開工前追問閘門與「幫我找 vs 幫我讀（禁摘要 5 欄表）」提示詞模式至 `docs/agent-memory-and-prompting-best-practices.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\agent-memory-and-prompting-best-practices.md`（收錄於集群 1）
  - **執行步驟**：
    1. 將「五要素指令結構（任務／工具／分類／輸出／邊界）與漸進授權階梯」整理為簡潔的提示詞設計檢核段。
    2. 補入「開工前一次性追問（別自己猜）」前置防返工句式。
    3. 補入「『幫我找（強制出處＋待確認）』vs『幫我讀（禁止摘要、強制輸出 5 欄逐條風險表）』」二元契約與「AI 董事會跨模型分歧點稽核」模式，並明確標註影片中的「四個員工」實為單代理角色分工而非平行 Multi-Agent。
  - **驗收標準（DoD）**：`docs/agent-memory-and-prompting-best-practices.md` 新增上述 3 項實戰提示詞模式與邊界說明，若引用影片轉述統計須標註未獨立查證，且 `python tools/verify_inbox.py` 驗證通過。
