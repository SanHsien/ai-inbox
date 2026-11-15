---
id: "2026-11-15-rikyu-geometric-vector-logo-mcp"
title: "Rikyū（rikyu.ai）：構造幾何向量 Logo 生成與 MCP 設計工作流查證評估"
source_url: "https://rikyu.ai/design/logo"
source_platform: "Web / Social"
author: "Kaisei Suzuki (@kaiseisuzuk)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
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
- **當前狀態**：`🟢 已完成 (Done)`

> **實查澄清**：
> 1. 原貼文連結 `https://rikyu.ai/design/logo` 目前對外回傳 **HTTP 404**，該產品已改版整合為 **Rikyū Studio**（`https://rikyu.ai/`），涵蓋 Vector、Graphics、Websites、Mobile apps、Print、3D 與 Videos。
> 2. **關於「可以接 MCP，不消耗額度」的說法與現行官網事實不符**：`https://rikyu.ai/mcp` 只觀察到 HTTP 回應標頭（`Allow: POST`、`Content-Type: application/json`），這不能單獨證明它是可用的 MCP 端點；協定初始化、工具列舉與授權條件都**未實測**。[官網](https://rikyu.ai/)定價卡片明確將 `MCP integration` 與 `Commercial use included` 列於付費方案（Basic［已停售］1,200 credits/月、Pro 16,000 credits/月、Max 48,000 credits/月；Pro／Max 繼承 Basic 的 MCP 與商用）；**Free（$0/月）僅贈送一次性 2,000 credits 且標註 `Personal use only`，未包含 MCP integration**。

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
    - 「AI 設計工具真正的分水嶺不是生圖速度，而是理解**比例、幾何構造、網格與可編輯向量（SVG）**」這是合理的工程偏好，不是比較實驗的結論。對幾何標誌來說，讓模型先規劃幾何圖元（`circle` / `rect` / `path` / viewBox 格線系統）再做 SVGO 清理與多尺寸匯出，通常比生成 PNG 後再轉向量好控制；不能推廣成所有影像或品牌素材的品質結論。
  - **不適用 / 需避坑的部分**：
    - **閉源 Credit 制與條款變化風險**：Rikyū 為閉源商業 SaaS，不僅舊路徑 `/design/logo` 已 404，早期宣傳的免費／免額度體驗也已收斂為「Free 僅 2,000 一次性點數＋限個人、MCP 綁定付費訂閱」。不建議把個人核心自動化管線強綁在未開源的付費 MCP 端點上。
    - **不綁付費端點的替代路線（不是零成本）**：可評估本地開源 MCP [`mcpware/logoloom`](https://github.com/mcpware/logoloom/blob/main/README.md)，或把「構造幾何 SVG 設計規則 + SVGO 清理」封裝為本地 Skill。LogoLoom 的 README 說明 SVG 是先由 Claude 設計，它只做轉字型路徑、優化與匯出的本機後處理；後處理不另收 API 費，但設計那一步仍消耗 agent 的訂閱額度或 token。「純本地、無外部回傳」目前只是作者宣稱：[`package.json`](https://github.com/mcpware/logoloom/blob/main/package.json) 依賴 MCP SDK、sharp、SVGO、opentype.js，依賴與安裝期的網路行為**未審查**。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-03`**｜**[優先級：低]** 唯讀比較 LogoLoom 與現有 SVG 產出方式，釐清額度、依賴與安全邊界
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/local-svg-logo-options-review.md`。
  - **具體做法**：固定 LogoLoom commit，靜態檢查 MCP 入口、檔案寫入路徑、SVG／字型處理、子程序、網路呼叫、package 與鎖檔是否齊全；標示未能檢查的間接依賴。對照「由既有 agent 直接產 SVG」是否已足夠，分清設計模型成本與本機後處理成本；不執行 npx、npm、安裝或 MCP 工具。
  - **驗收標準（DoD）**：上述報告含資料流 ASCII 圖、來源 commit／URL、已查與未查風險、模型額度說明、Windows 相依性及明確採納結論。若沒有新增價值，可據此不採納；不得以「沒有 API key」宣稱全程零成本或已證實無外連。文件檢查結果附證據；不新增關鍵字裁判或全域 Skill。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/local-svg-logo-options-review.md，固定 mcpware/logoloom 9e5de3e。原始碼有未固定版本的 npx -y vtracer-cli 自動備援，以及用字串拼接的 shell 指令；設計仍耗上游 agent 額度；結論暫不安裝。唯讀評估，Codex 撰寫，整合者重產索引並補驗證段；Fable 獨立複審抽查來源事實全部吻合；未執行任何第三方程式。
