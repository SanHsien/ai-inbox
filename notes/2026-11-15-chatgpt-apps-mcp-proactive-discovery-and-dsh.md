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
  1. **「ChatGPT 每週 12 億活躍用戶＋對話主動推薦」— 查證屬實**：OpenAI 活躍用戶規模已突破 1.2B WAU，現行開放平台已從早期 2023 Plugins 演進為 **OpenAI Apps SDK + ChatGPT App Directory**（底層基於 **MCP, Model Context Protocol**），具備對話意圖偵測並主動在對話串內推薦 App 與渲染互動式 Widget 的能力。
  2. **「這就是 DeepSeek Harness 要做的事」— 概念混淆澄清**：經查 **DeepSeek Harness（DSH）** 是 MIT 開源的本機開發者代理執行期（基於 Cordis「一切皆外掛」架構），主打本機檔案、終端、沙盒與自託管可控工作台；而 OpenAI Apps SDK 是面向消費級與企業級雲端用戶的分發市場，兩者定位截然不同（一為本地開發環境外骨骼，一為雲端入口分發）。
- **Why（核心商業誘因）**：
  - 傳統 App Store / SEO 需要使用者主動搜尋；對話內主動推薦則是**高意圖觸發分發（Intent Routing）**——使用者在對話裡提出具體需求時直接被端到工具面前，理論上是最貼近轉換底層（Bottom-of-Funnel）的入口。
- **How（實際上架與技術門檻，並非貼文所說零門檻）**：
  - 需提供標準 **遠端 MCP Server**（tools / resources / prompts）與合規互動 Widget。
  - 強制要求 **OAuth 2.1 / OpenID Connect**（含 `connector_platform_oauth_redirect` 等標準驗證流程）以及 **OpenAI 持續自動化端點審查**（定期掃描工具契約與 PII 外洩風險）。
- **Key Metrics / Numbers**：ChatGPT 週活躍用戶超過 12 億；但遠端 MCP Server 的算力、頻寬與資料庫託管成本**全由開發者自行負擔**（OpenAI 目前僅作為分發與調用入口，不會替免洗工具買單伺服器費用）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與今日評估的 **AI-Native 一人接案系統**（[`notes/2026-11-15-ai-native-agency-retainer-and-org-playbook.md`](./2026-11-15-ai-native-agency-retainer-and-org-playbook.md)）與維護者既有的 **Cloudflare Workers Serverless 技術棧**（[`notes/2026-11-08-ccckmit-cloudflare-wrangler-deploy-serverless-stack.md`](./2026-11-08-ccckmit-cloudflare-wrangler-deploy-serverless-stack.md)）直接相連。
- **落差與採納判斷**：
  - **真正有價值的不是「粗暴生 5 個免洗外掛」，而是「MCP 可移植性紅利（Build Once, Distribute Everywhere）」**：
    - 既然底層是標準 **MCP**，同一套後端服務既可以給維護者自己的 Claude Code / Codex / Antigravity 使用，也能對外上架到 ChatGPT App Directory 當作免費獲客漏斗（Top-of-Funnel）導流回付費微 SaaS 或接案諮詢。
  - **必須避開的坑**：
    1. **免洗通用工具無護城河且倒賠伺服器費用**：PDF 轉 Excel、發票產生器這類工具在標準模型內建 Code Interpreter／檔案處理面前毫無競爭力，且免費用戶越多、你的遠端 MCP 託管帳單越高。
    2. **意圖路由不是關鍵字堆疊（Keyword Stuffing）**：OpenAI 審查與意圖路由重視乾淨的工具契約與真實完成任務的能力，粗製濫造的描述只會被自動審查下架或無曝光。
    3. **進場條件**：只選「需要連結外部資料／垂直領域規則／能承接付費訂閱或 B2B 接案引流」且可跑在零成本邊緣託管（如 Cloudflare Workers Free Tier）的單一工具試水溫，絕不盲目洗 5 個無商業閉環的殼。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-10`**｜**[優先級：低]** 查驗 OpenAI Apps SDK 上架與 OAuth 2.1 契約規範，評估以 Cloudflare Workers 零成本託管 1 個具引流價值的垂直 MCP 微工具可行性
  - **目標範圍**：研究評估筆記／規格備忘（`C:\GitHub\ai-inbox\docs\` 或對應微工具專案，先不立新 repo）
  - **具體做法**：
    1. 查閱 OpenAI Apps SDK 官方文件，確認最新上架門檻（遙測／隱私政策、OAuth 2.1 最低要求、自動化審查項目、商業變現／外部導流政策）。
    2. 評估結合 Cloudflare Workers 免費方案＋遠端 Streamable HTTP MCP，挑選 1 個與維護者既有強項相關（如技術規格檢查、在地化商業計算／合規檢核或接案診斷小工具）作為候選切入點，避免紅海通用轉檔工具。
  - **驗收標準（DoD）**：產出一份簡潔的《OpenAI Apps SDK 上架與變現可行性檢核表》，確認邊際成本為零／可控且無違規風險後再決定是否開發。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
