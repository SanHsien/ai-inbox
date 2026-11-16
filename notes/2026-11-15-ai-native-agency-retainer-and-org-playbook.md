---
id: "2026-11-15-ai-native-agency-retainer-and-org-playbook"
title: "AI-Native 一人接案公司：從賣工時轉向「建置＋月費維運」與多角色可重複服務系統"
source_url: "N/A"
source_platform: "Social / Forum"
author: "匿名社群分享"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 1
cluster_role: "一人接案Agency系統"
short_title: "AI一人接案Agency"
source_review: unavailable
source_reviewed_at: 2026-11-17
source_review_note: "建檔時維護者只提供轉貼的文字（兩篇文章與兩則留言），沒有原始貼文連結、作者與平台，無法開啟原貼查看圖片與完整留言"
tags:
  - ai-agency
  - freelance
  - retainer-model
  - multi-agent-org
  - sop-assetization
  - recurring-revenue
---

# AI-Native 一人接案公司：從賣工時轉向「建置＋月費維運」與多角色可重複服務系統

- **來源連結**：`N/A`（社群兩篇連續文章：〈AI 接案商業模式〉與〈AI-Native Agency 組織架構〉）
- **發布平台 / 作者**：`社群平台` / `匿名作者`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 已封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md`](./2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md)（需求解壓縮、價值報價法與外部裁判 DoD）
  - [`notes/2026-10-17-hansun-fullstack-agent-deployment-manual.md`](./2026-10-17-hansun-fullstack-agent-deployment-manual.md)（全端建站規格與上線 QA 稽核）
  - [`notes/2026-10-24-feedback-desk-client-ticket-ai-handoff.md`](./2026-10-24-feedback-desk-client-ticket-ai-handoff.md)（客戶工單流轉與 AI 維運交接）

---

## 0. 原始資料盤點

> 2026-11-17 重審。本篇 `source_url` 為 N/A：建檔時拿到的是轉貼的文字（兩篇連續文章〈AI 接案商業模式〉〈AI-Native Agency 組織架構〉與兩則網友留言），沒有原始貼文連結、作者帳號或平台。依 AGENTS.md 第 3 節，不人肉搜尋轉貼來源。

- **作者圖片**：看不到。不知道原貼文有沒有附圖（例如組織架構圖、報價表）；本文的 ASCII 流程圖是建檔時依文字重畫的，不是原圖。
- **作者留言補充**：看不到。
- **網友留言重點**：只有建檔時一併轉貼進來的兩則（通用提示詞問法、國外 B2B Lead Gen 工具鏈），已在 2.1 節評估；原貼文底下其餘留言無從查看，也無法確認這兩則是否被作者回應或被其他人反駁。
- **對分析的影響**：沒有新資料，內容不改。本篇結論建立在轉貼文字上，文中的金額試算（原文算錯之處已在 5W1H 註明）與工具鏈都無法回到原貼核對；若日後取得原始連結，應補看圖片與留言再把 `source_review` 改掉。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（適用對象）**：具備工程與工具鏈整合能力的獨立開發者／一人接案團隊（Solopreneur / AI-Native Agency）。
- **What（核心主張）**：
  1. **不賣「我會用 AI」，只賣「確定結果」**：客戶關心的是「原本要找 3 個人做的事，你能不能幫我完整交卷」。
  2. **商業模式升級（從單次買斷到 Recurring Revenue）**：從「做完收 8 萬結案」轉為「**一次性導入費（如 12 萬）＋ 每月服務費（如 2.5–3 萬做 SEO/GEO、內容、數據分析、網站維運）＋ 成效型收入**」，累積 10 家客戶即可形成穩定的月度經常性收入。
  3. **多角色 Agent 組織架構與經驗沉澱**：

```text
客戶 ─▶ AI 業務/診斷 ─▶ AI PM ─▶ Research / Strategy Agent
                                        │
        ┌───────────────────────────────┘
        ▼
  執行層 (Developer / Writer / Designer / SEO) ─▶ Reviewer (退回修改) ─▶ QA ─▶ 人類最終批准 ─▶ 交付與月費維運
        │
        └─▶ 結案後沉澱資產：Skill / SOP / Template / Agent / Dataset (人力參與從 50% 逐次遞減)
```

- **Why（為解決什麼問題 / 痛點）**：單人用單一對話框接案只會變成「打字比較快的 Freelancer」，仍被自己的時間天花板鎖死；唯有把每次接案拆成標準角色流水線並將經驗沉澱為可複用資產，才能用一套系統承接多個客戶與月費維運。
- **How（核心運作機制）**：把專案從「幫我做個網站」拆解成研究、策略、文案、UI/UX、程式、SEO、獨立 Review、QA 與人類最終把關；每完成一案就把可重複步驟固化成 Skill / SOP / Template。
- **When & Where（適用時機與場景）**：網站建置、SEO/GEO、AI 自動化、企業知識庫、程式開發、市場與競爭者研究等具備高重複性的 B2B 服務。
- **Key Metrics / Numbers（舉例數字，非實證基準）**：文中「12 萬建置＋每月 2.5 萬、10 個客戶＝每月 30 萬」為商業模式舉例計算，而且算錯：2.5 萬 × 10 是每月 25 萬，要每客戶 3 萬才是 30 萬；實際成效視獲客能力、客戶留存率與月費交付邊界控管而定。

---

## 2. 啟發與與現有系統對齊分析

- **維護者目前已經具備的零件（無須重造）**：
  - **診斷與 PM 拆解**：[`templates/client-requirement-decomposition-prompt.md`](../templates/client-requirement-decomposition-prompt.md)
  - **全端 Developer 規格**：[`templates/fullstack-website-builder-skill.md`](../templates/fullstack-website-builder-skill.md)
  - **獨立 Reviewer & QA 閘門**：[`docs/production-smoke-security-checklist.md`](../docs/production-smoke-security-checklist.md) ＋ `SanHsien/agent-advisor`（`advisor-pro-reviewer`）＋ `SanHsien/harness-guard`
  - **多角色派工與跨機協作**：`SanHsien/agent-relay` ＋ [`templates/team-dispatch-skill-template.md`](../templates/team-dispatch-skill-template.md)
  - **交付後客戶開單維運**：[`templates/feedback-desk-agent-prompt.md`](../templates/feedback-desk-agent-prompt.md)
- **若日後要經營接案才需要補的三塊**（目前沒有維護者要經營接案公司的需求證據，所以不是待辦；`T-20261115-08`、`T-20261115-09` 已關閉）：
  1. **缺一條龍「接案營運總綱（Playbook）」**：上述四份範本目前各自獨立，缺一份明確對映「接案 7 階段 $\rightarrow$ 調用哪支現有範本／哪個 Agent $\rightarrow$ 產出什麼交付物 $\rightarrow$ 何時人類批准」的總控文件。
  2. **缺「月費維運（Retainer）邊界與報價範本」**：若月費方案沒有白紙黑字切開「例行維運（安全更新、數據月報、SEO/GEO 微調、小修）」與「新功能變更單（CR）」，月費很容易變成「每月 2.5 萬包山包海無限加班」。
  3. **缺「結案資產沉澱檢查點」**：每次專案結案時，沒有強制觸發「把這次踩過的坑與重複流程蒸餾回 `ai-inbox/templates/` 或 `workflow-skill-creator`」的收尾清單。

### 2.1 補充查證：網友留言評估（入門提示詞 vs. 國外 B2B Lead Gen 工具鏈）

1. **留言 1（通用提示詞詢問 AI 接案架構）**：這類問題只適合當作初始概念掃盲；通用模型給出的是抽象教科書架構，沒有真實行業名單、驗證管道、合規或定價邊界，無法直接作為接案業務引擎。
2. **留言 2（國外流行的 AI Lead Gen 關鍵詞與 API 工具鏈）— 工具名稱為留言所列，現行價格、條款與是否主流都未查證；另有合規紅線**：
   - 這些服務多數要另外付費。本 repo 不增加付費，不把這條工具鏈當預設實作。
   - **留言所列的 B2B Outbound 技術棧**：**Discovery**（Google Places API / Apify 按區域與行業找名單）$\rightarrow$ **Enrichment**（Apollo.io + **Clay** Waterfall 多源驗證企業信箱，並由 Claygent 讀目標官網自動產出診斷切入點）$\rightarrow$ **Outreach**（Instantly.ai / Smartlead 多信箱輪替預熱、壓低退信率）。
   - **合規與實務風險（不可直接盲目照搬）**：
     - 美國受 **CAN-SPAM** 規範（須實體地址、誠實主旨、[10 個工作天內](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)處理退訂）。英國依 [ICO 的 B2B 行銷指引](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing/)，寄給公司（corporate subscriber）的信箱不一律需要 PECR 同意，寄給個人或獨資業者才需要；只要處理到個資，仍另受 UK GDPR 約束。歐盟各國規定不同，不能壓成一條規則，各國細節未查證。台灣進行 B2B 開發須遵守《個人資料保護法》與公開來源合法性，切勿購買黑名單或對社群／LINE 進行未授權批量私訊。
     - 不可使用主網域直接發冷開發信，避免聲譽受損影響正常客戶溝通；API 串接須遵守各平台速率與 ToS（避免無頭硬爬導致封號）。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-08`**｜**[優先級：高]** 建立《AI-Native 一人接案營運總綱》（`docs/ai-agency-delivery-playbook.md`），串聯現有診斷、建站、審查與維運範本成端到端流水線
  - **狀態**：⚪ 不做（2026-11-15 獨立審查：沒有維護者經營接案業務、客戶、預算或月費交付責任的需求證據，候選獲客服務多須額外付費。日後明確要做，先定案型、客戶與交付範圍再寫商業文件）
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\ai-agency-delivery-playbook.md`（參考並連結現有 `templates/client-requirement-decomposition-prompt.md`、`templates/fullstack-website-builder-skill.md`、`docs/production-smoke-security-checklist.md`、`templates/feedback-desk-agent-prompt.md`）
  - **具體做法**：
    1. 繪製 7 階段接案流水線對照表（獲客診斷 $\rightarrow$ 報價簽約 $\rightarrow$ Research/Strategy $\rightarrow$ Developer/Writer $\rightarrow$ 獨立 Reviewer/QA $\rightarrow$ 人類終審交付 $\rightarrow$ 月費維運），每階段明確綁定維護者現有的範本／工具／`agent-relay` 角色，並於第 1 階段納入合規 B2B Lead Gen 關鍵詞與官網診斷切入流程（註明 GDPR / CAN-SPAM / 個資法與網域隔離紅線）。
    2. 訂定「人類必須親自把關的 4 個閘門」（需求確認、對外承諾／報價、上線前安全驗收、例外升級），其餘交給 Agent 流水線。
    3. 加入「結案資產沉澱清單（Post-Project Asset Extraction）」，強制在每個專案收尾時檢核是否產出新的 Skill、SOP 或範本更新。
  - **驗收標準（DoD）**：產出 `docs/ai-agency-delivery-playbook.md`，所有引用之內部範本路徑皆存在有效，且通過 `python tools/verify_inbox.py`。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*

- [ ] **`T-20261115-09`**｜**[優先級：中]** 建立「建置導入＋月費維運（Retainer）提案與邊界範本」（`templates/agency-retainer-proposal-template.md`）
  - **狀態**：⚪ 不做（2026-11-15 獨立審查：同 T-20261115-08，沒有接案需求證據；SLA 與商業條款須有真實服務邊界，不能由 AI 假設客戶與報價）
  - **目標範圍**：`C:\GitHub\ai-inbox\templates\agency-retainer-proposal-template.md`
  - **具體做法**：
    1. 設計可套用於網站／AI 自動化／SEO-GEO 案型的標準提案結構：第一階段一次性導入（含 DoD 驗收標準）、第二階段月費維運（SLA、每月固定交付物如數據月報／備份／安全修補／固定額度微調）。
    2. 明訂「包含範圍 vs. 變更單（CR）計價邊界」與「月費成效指標（Leading vs. Lagging Indicators）」防呆條款，避免接案後陷入無止盡免費改稿。
  - **驗收標準（DoD）**：產出 `templates/agency-retainer-proposal-template.md`，含可直接套用的表格與條款清單，且通過 `python tools/verify_inbox.py`。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
