---
id: "2026-11-15-rikyu-geometric-vector-logo-mcp"
title: "Rikyū（rikyu.ai）：構造幾何向量 Logo 生成與 MCP 設計工作流查證評估"
source_url: "https://rikyu.ai/design/logo"
source_platform: "Web / Social"
author: "Kaisei Suzuki (@kaiseisuzuk)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 2
cluster_role: "向量幾何Logo與MCP"
short_title: "Rikyū幾何Logo與MCP"
tags:
  - vector-design
  - svg
  - geometric-logo
  - mcp
  - generative-ui
  - ai-design
---

# Rikyū（rikyu.ai）：構造幾何向量 Logo 生成與 MCP 設計工作流查證評估

- **來源連結**：[Rikyū Logo（舊路徑 404）](https://rikyu.ai/design/logo) ｜ [Rikyū 首頁](https://rikyu.ai/)
- **發布平台 / 作者**：`Web` / `Kaisei Suzuki (@kaiseisuzuk)`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

> **實查澄清**：
> 1. 原貼文連結 `https://rikyu.ai/design/logo` 目前對外回傳 **HTTP 404**，該產品已改版整合為 **Rikyū Studio**（`https://rikyu.ai/`），涵蓋 Vector、Graphics、Websites、Mobile apps、Print、3D 與 Videos。
> 2. **關於「可以接 MCP，不消耗額度」的說法與現行官網事實不符**：實測 `https://rikyu.ai/mcp` 確實為有效的 Streamable HTTP MCP 端點（`Allow: POST`、`Content-Type: application/json`），但官網定價卡片明確將 `MCP integration` 與 `Commercial use included` 列於付費方案（Basic［已停售］1,200 credits/月、Pro 16,000 credits/月、Max 48,000 credits/月）；**Free（$0/月）僅贈送一次性 2,000 credits 且標註 `Personal use only`，未包含 MCP integration**。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：日本獨立開發者 Kaisei Suzuki（`@kaiseisuzuk`）開發與營運的商業 AI 設計平台 Rikyū。
- **What（核心產出 / 做了什麼）**：
  - 早期以「用幾何圖形（圓、線條、輔助格線）構造向量 Logo」在社群爆紅，現已擴展為透過對話與 MCP 驅動多媒介設計產出（Logo/Vector、海報、網站、App 畫面、印刷品、3D、短影片）的 Rikyū Studio。
- **Why（為解決什麼問題 / 痛點）**：
  - 傳統 AI 生圖（Midjourney / GPT Image）輸出的是點陣像素圖，缺乏可編輯的幾何結構、比例格線與乾淨的 SVG 路徑，轉用於實務品牌或前端介面時往往還需人工重描（Auto-trace 雜訊多）。
- **How（核心架構與關鍵機制）**：
  - **Constructive Geometry（構造幾何）**：強調以基礎幾何圖元（圓、弧線、比例格線）組裝標誌，並可呈現類似設計藍圖（Blueprint）的構成脈絡，最終輸出可直接部署的 SVG 向量格式。
  - **MCP（Model Context Protocol）串接**：透過 `https://rikyu.ai/mcp` 提供遠端 MCP 服務，讓 Claude、Codex、Cursor 等開發端 Agent 直接在專案脈絡內呼叫設計與資產生成能力。
- **When & Where（適用時機與場景）**：獨立開發者或無專職設計師團隊需要快速產出向量級品牌圖標、印刷品與行銷視覺素材時。
- **Key Metrics / Numbers（關鍵指標與量化數據）**：
  - 現行官網方案額度：Free（`$0` / 一次性 `2,000 credits` / 僅個人使用）、Basic（已停售 / `1,200 credits/月` / 含 MCP 與商用）、Pro（`16,000 credits/月`）、Max（`48,000 credits/月`，標註為 Pro 的 3 倍）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/ai-inbox` 既有前端／視覺規範（`docs/anti-ai-slop-frontend.md`、`templates/single-file-creative-coding-skill.md`）以及未來需快速產出網站 Favicon、Logo、SVG 插圖的前端建站任務。
- **落差與採納判斷**：
  - **值得採納的核心洞察**：
    - 「AI 設計工具真正的分水嶺不是生圖速度，而是理解**比例、幾何構造、網格與可編輯向量（SVG）**」這個判斷完全成立。在前端與開發工作流中，讓模型先規劃幾何圖元（`circle` / `rect` / `path` / viewBox 格線系統）再做 SVGO 清理與多尺寸匯出，遠比生成 PNG 後再轉向量可靠。
  - **不適用 / 需避坑的部分**：
    - **閉源 Credit 制與條款變化風險**：Rikyū 為閉源商業 SaaS，不僅舊路徑 `/design/logo` 已 404，早期宣傳的免費／免額度體驗也已收斂為「Free 僅 2,000 一次性點數＋限個人、MCP 綁定付費訂閱」。不建議把個人核心自動化管線強綁在未開源的付費 MCP 端點上。
    - **真正「本地零額度消耗」的替代路線**：若目標是在 Claude Code / Codex / Antigravity 中零成本產出幾何向量 Logo 與全套 Brand Kit，可評估本地開源 MCP（如 `mcpware/logoloom`）或直接將「構造幾何 SVG 設計規則 + SVGO 清理」封裝為本地 Skill。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-03`**｜**[優先級：低]** 安全審查並評估本地零額度幾何向量 Logo 方案（`mcpware/logoloom` 或自建構造幾何 SVG + SVGO Skill）
  - **目標範圍**：`C:\GitHub\_sandbox\`（唯讀／沙盒審查）與 `C:\GitHub\ai-inbox\templates\`
  - **具體做法**：
    1. 針對開源 MCP `mcpware/logoloom`（或同類純本地 SVG 品牌套件生成工具）執行安全審查（檢視原始碼、依賴與無外部回傳），確認無違反零信任規範。
    2. 若無需額外 MCP 即可達成，評估在本地蒸餾一份「構造幾何 SVG Logo 設計 Skill」（規範 viewBox、黃金比例／網格約束、基礎圖元組合、SVGO 優化與多尺寸輸出），實現真正零外部額度消耗。
  - **驗收標準（DoD）**：產出審查／實測紀錄，或交付一份可通過 `verify_inbox.py` 的本地幾何 SVG Logo 生成範本，並實測產出至少 1 組乾淨可用於前端專案的 SVG Logo。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
