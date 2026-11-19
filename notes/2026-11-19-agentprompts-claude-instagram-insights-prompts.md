---
id: "2026-11-19-agentprompts-claude-instagram-insights-prompts"
title: "Threads 情報評估：@agentprompts.ai 的 Claude 分析 Instagram Insights 七組 Prompt 與 Gumroad 導流模式"
source_url: "https://www.threads.com/@agentprompts.ai/post/DfwBU1TFrJz"
source_platform: "Threads"
author: "@agentprompts.ai"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 1
source_replies: 13
source_reviewed_at: "2026-11-19"
status: archived
cluster: 1
cluster_role: "IG數據分析Prompt"
short_title: "Claude分析IG數據Prompt"
tags:
  - claude
  - instagram-insights
  - prompt-engineering
  - marketing-analytics
  - gumroad
  - threads
---

# Threads 情報評估：@agentprompts.ai 的 Claude 分析 Instagram Insights 七組 Prompt 與 Gumroad 導流模式

- **來源貼文**：[Threads 原貼文（`@agentprompts.ai`）](https://www.threads.com/@agentprompts.ai/post/DfwBU1TFrJz)（原分享連結 `https://www.threads.com/share/_3-jUujC6`）
- **發布平台 / 作者**：`Threads` / `@agentprompts.ai`（`2026-11-15`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-18-claude-ai-council-prompt-fact-check.md`](./2026-11-18-claude-ai-council-prompt-fact-check.md)（同類 Threads 模板化提示詞與標題黨事實查核）

---

## 1. 原始資料盤點（主文、1 張配圖、8 則續樓與 5 則網友留言）

- **主貼文核心**：以誇飾標題宣稱 `BREAKING: Claude can now read your INSTAGRAM INSIGHTS like a $160/hour growth strategist. For free.`，並提供 7 組社群數據分析提示詞。
- **作者上傳圖片（共 1 張）**：
  - 深黑背景，中間金線分隔，左側為 Claude 放射星標與文字 `Claude`，右側為 Instagram 圖示與文字 `Instagram`。無真實系統截圖或後台報表數據。
- **作者續樓內容（共 8 則串文）**：
  - **續樓 1（成長體系總綱）**：分析貼文觸及、儲存/分享、增粉與在線時間，產出三支柱、每週節奏與單週測試項。
  - **續樓 2（最佳貼文拆解）**：分析前 5 大爆款的 Hook、首幀、文案長度與發布時機，歸納複用模板。
  - **續樓 3（商業導流）**：插入 Gumroad 付費/名單獲取連結（`gum.co/u/m10hetif`，`250+ AI Prompt Vault`）。
  - **續樓 4（Reels 完播率優化）**：診斷跳出點、前 3 秒鉤子與節奏。
  - **續樓 5（粉絲畫像審計）**：比對現有受眾與目標受眾落差，重寫個人檔案簡介。
  - **續樓 6（限時動態互動計畫）**：分析觀看衰減與互動貼圖排程。
  - **續樓 7（標籤與非粉絲觸及測試）**：單變量實驗設計與追蹤表。
  - **續樓 8（月度指標覆盤）**：月度對比與關鍵單一指標（North Star Metric）監控。
- **網友回應與留言檢驗（共 13 則，含作者 8 則續樓與 5 則網友/AI 留言，已完整讀取無缺漏）**：
  - `@leenakapgate` 詢問是否可用於 Claude coding；
  - 印尼語用戶 `@btnwbmtr` 召喚 `@meta.ai`，`@meta.ai` 回覆直接點破本質：**「這是 @agentprompts.ai 的行銷貼文，透過 7 組用 Claude 讀 Instagram 數據的 prompt，最後導流到包含 250+ prompt 的付費/收集名單 vault」**。
- **原始資料對分析的影響**：主貼文聲稱的「BREAKING / Claude can now read...」並非 Claude 具備任何新的 API 串接或自動讀取 IG 後台功能，純粹是**使用者手動複製貼上 Instagram Insights 數據文字後，讓 Claude 扮演分析師的角色扮演 Prompt 範本**，為標準的社群導流模板貼文。

---

## 2. 對現有系統的啟發與落差評估

- **技術架構實質**：
  - 無任何開源工具、無 MCP Server、無 API 自動化整合，本質為行銷導流與提示詞模板。
  - 提示詞結構（指定角色 + 給定輸入指標 + 限制輸出結構 + 提出具體單一測試項）具備基礎的 Prompt Engineering 規範，但無工程或系統改動價值。
- **本機現有工作流比對**：
  - 本機已建立嚴謹的工程化任務與調研管線（`agent-reach`、`ai-inbox`、`verify_inbox.py` 等），不需要收錄外部黑盒商業 prompt vault。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬社群行銷提示詞與 Gumroad 導流內容，非工程技術創新或工具更新，且無系統缺口；以 `status: archived` 歸檔（標記 `source_review: full`、`source_images: 1`、`source_replies: 13`），保留事實查核與模板結構紀錄即可。
