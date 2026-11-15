---
id: "2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh"
title: "ChatGPT Apps（MCP 主動推薦）流量分發評估與「粗暴上架 5 個外掛」現實檢核"
source_url: "N/A"
source_platform: "Social / Forum"
author: "匿名社群分享"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 4
cluster_role: "ChatGPT分發紅利"
short_title: "ChatGPT MCP分發紅利"
tags:
  - openai-apps-sdk
  - mcp
  - distribution-channel
  - chatgpt-app-store
  - deepseek-harness
  - micro-saas
---

# ChatGPT Apps（MCP 主動推薦）流量分發評估與「粗暴上架 5 個外掛」現實檢核

- **來源連結**：`N/A`（社群貼文：主張開發「ChatGPT Plugins」吃每週 12 億活躍用戶主動推薦紅利，並與 DeepSeek Harness 對比）
- **發布平台 / 作者**：`社群平台` / `匿名作者`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要與事實查證（5W1H + CQR）

- **Who / What（貼文主張 vs. 2026 年 11 月技術實況）**：
  1. **「ChatGPT 每週 12 億活躍用戶＋對話主動推薦」— 用戶數未查證**：1.2B WAU 沒有找到支持這個精確數字與時點的官方來源，不要拿它估推薦流量。平台面：貼文說的是從 2023 Plugins 演進到 **OpenAI Apps SDK**（底層基於 **MCP**）；但現行官方文件的 Apps SDK 驗證頁已轉到 Plugins 文件，[提交頁](https://developers.openai.com/plugins/deploy/submission)有 plugin ZIP、developer identity、驗證與審查等具體要求。歷史稱呼不能代替現行操作契約，動手前要以查證當日的官方文件為準。
  2. **「這就是 DeepSeek Harness 要做的事」— 概念混淆澄清**：依[官方 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.md)，**DeepSeek Harness（DSH）** 是 MIT 開源的本機開發者代理執行期（基於 Cordis「一切皆外掛」架構），標明為 developer preview、可能有相容性破壞。這裡只是釐清定位，不代表建議維護者採用（中國服務）。它主打本機檔案、終端、沙盒與自託管可控工作台；而 OpenAI Apps SDK 是面向消費級與企業級雲端用戶的分發市場，兩者定位截然不同（一為本地開發環境外骨骼，一為雲端入口分發）。
- **Why（核心商業誘因）**：
  - 傳統 App Store / SEO 需要使用者主動搜尋；對話內主動推薦則是**高意圖觸發分發（Intent Routing）**——使用者在對話裡提出具體需求時直接被端到工具面前，理論上是最貼近轉換底層（Bottom-of-Funnel）的入口。
- **How（實際上架與技術門檻，並非貼文所說零門檻）**：
  - 需提供 **MCP Server**；tools、resources、prompts 與互動 Widget 哪些必要、哪些可選，要按候選工具對照官方要求逐項列，不能全部當成強制門檻（逐項未查證）。
  - 驗證方式：原稿寫「全面強制 OAuth 2.1 / OpenID Connect」是錯的。官方[提交頁](https://developers.openai.com/plugins/deploy/submission)支援無驗證、OAuth 與混合三種；需要使用者帳號的工具才用 OAuth。原稿提到的 `connector_platform_oauth_redirect` 與「持續自動化端點審查」細節未查證。
- **Key Metrics / Numbers**：貼文宣稱 ChatGPT 週活躍用戶超過 12 億（未查證）；遠端 MCP Server 的算力、頻寬與資料庫託管成本**全由開發者自行負擔**（OpenAI 只是分發與調用入口）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與今日評估的 **AI-Native 一人接案系統**（[`notes/2026-11-15-ai-native-agency-retainer-and-org-playbook.md`](./2026-11-15-ai-native-agency-retainer-and-org-playbook.md)）與維護者既有的 **Cloudflare Workers Serverless 技術棧**（[`notes/2026-11-08-ccckmit-cloudflare-wrangler-deploy-serverless-stack.md`](./2026-11-08-ccckmit-cloudflare-wrangler-deploy-serverless-stack.md)）直接相連。
- **落差與採納判斷**：
  - **比「粗暴生 5 個免洗外掛」有價值的是 MCP 的可移植性，但不是一次建置處處可用**：
    - 既然底層是標準 **MCP**，同一套後端服務既可以給維護者自己的 Claude Code / Codex / Antigravity 使用，也能對外上架到 ChatGPT App Directory 當作獲客入口。各宿主在身份驗證、UI 與工具契約上有差異，每上一個平台都要另外適配與驗收。
  - **必須避開的坑**：
    1. **免洗通用工具無護城河且倒賠伺服器費用**：PDF 轉 Excel、發票產生器這類工具在標準模型內建 Code Interpreter／檔案處理面前毫無競爭力，且免費用戶越多、你的遠端 MCP 託管帳單越高。
    2. **意圖路由不是關鍵字堆疊（Keyword Stuffing）**：OpenAI 審查與意圖路由重視乾淨的工具契約與真實完成任務的能力，粗製濫造的描述只會被自動審查下架或無曝光。
    3. **進場條件**：只選「需要連結外部資料／垂直領域規則／能承接付費訂閱或 B2B 接案引流」的單一工具試水溫，絕不盲目洗 5 個無商業閉環的殼。託管不是零成本：Cloudflare Workers 免費方案有[請求數與 CPU 時間等額度](https://developers.cloudflare.com/workers/platform/limits/)，後端資料與模型成本另計，也不能保證永遠合規。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-10`**｜**[優先級：低]** 依 OpenAI 一手文件修正上架、驗證與託管成本假設，交付單份可行性檢核表
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/openai-plugin-submission-feasibility.md` 與對應 ChatGPT Apps 筆記。
  - **具體做法**：按查證日核對 Apps SDK／Plugins 現行術語、必要包裝、developer identity、MCP、可選 UI、無驗證／OAuth、隱私／審查與對外導流規範。未取得的一手用戶規模數字移為未查證。只比較一個不用中國服務、沒有付費模型依賴的既有需求候選；若無明確需求直接不建議立項，不為湊產出發明 SaaS。
  - **驗收標準（DoD）**：上述檢核表逐項附官方 URL、查證日期、必要／可選／未查證與決策；託管成本列用量假設、免費額度、超額處置及未知費用，不能承諾永遠零成本。明確結論為暫不開發或具條件再提案。同步修正原筆記並通過文件檢查；本任務不登入開發者帳號、不部署、不提交上架、不建立 repo。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
