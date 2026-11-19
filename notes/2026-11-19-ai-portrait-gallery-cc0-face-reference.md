---
id: "2026-11-19-ai-portrait-gallery-cc0-face-reference"
title: "Threads 資源評估：ai-portrait-gallery.pages.dev 日系 AI 模型人臉與造型 CC0 參考庫"
source_url: "https://www.threads.com/@herb.hou/post/Df1JwFlE489"
source_platform: "Threads"
author: "@herb.hou (侯俊耀) / あぎ (Agi)"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: partial
source_images: 1
source_replies: 1
source_reviewed_at: "2026-11-19"
source_review_note: "主貼文與1張網站首頁截圖完整讀取；貼文顯示3則留言，未登入僅讀到1則（@cola_bb_official），其餘2則未顯示"
status: archived
cluster: 2
cluster_role: "CC0人臉參考庫"
short_title: "CC0日系AI人臉庫"
tags:
  - ai-portrait
  - cc0
  - character-consistency
  - image-generation
  - reference-library
  - threads
---

# Threads 資源評估：ai-portrait-gallery.pages.dev 日系 AI 模型人臉與造型 CC0 參考庫

- **來源貼文**：[Threads 原貼文（`@herb.hou` 侯俊耀）](https://www.threads.com/@herb.hou/post/Df1JwFlE489)（原分享連結 `https://www.threads.com/share/BBh1ue-myj`）
- **資源網站**：[`https://ai-portrait-gallery.pages.dev/`](https://ai-portrait-gallery.pages.dev/)（日本創作者 `あぎ / Agi` 營運，CC0 授權）
- **發布平台 / 作者**：`Threads` / `@herb.hou`（`2026-11-17`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-15-keyframe-grid-sheet-dance-video-prompt.md`](./2026-11-15-keyframe-grid-sheet-dance-video-prompt.md)（角色一致性參考圖與舞步表管線）
  - [`notes/2026-11-19-ann-cheng-muse-ai-short-video-skill.md`](./2026-11-19-ann-cheng-muse-ai-short-video-skill.md)（人物照片作起始幀生片流程）

---

## 1. 原始資料盤點（主文、1 張截圖、留言與外部查證）

- **主貼文核心**：推薦由 `Agi` 提供的免費 AI 模型人臉參考庫 `ai-portrait-gallery.pages.dev`，採 CC0 授權，主打日系高顏值風格，免訓練 LoRA 即可用單張臉做角色一致性參考，內含近 900 張正面臉部圖與 600+ 張造型圖。
- **作者上傳截圖（共 1 張，網站首頁繁體翻譯畫面）**：
  - **實測數據**：截圖顯示 `臉 893`、`造型 606`、`執照 CC0`，右側展示「短的 / 中等的 / 中長髮」3 張日系女性人像。
  - **導流設計細節**：截圖左上與按鈕區明確標示「`● 加入LINE公開聊天`」，並註記「如何使用此圖像以及圖像生成提示的範例僅對 Agino 的 LINE Open Chat 用戶可見」——顯示該站以免費 CC0 圖庫為主體，並將進階 Prompt 教學導流至 LINE Open Chat 社群。
- **網友回應（3 則中讀到 1 則）**：僅見 `@cola_bb_official` 戲稱「影到我 pls del」，無技術補充或反駁；其餘 2 則未登入未顯示。
- **外部搜尋補充核實**：經查證該作者（日本創作者 `あぎ`）另有同系列衍生參考庫 **`ai-pose-gallery.pages.dev`**（姿勢參考）與 **`ai-costume-gallery.pages.dev`**（服裝參考），主要搭配 ControlNet、IP-Adapter 或各類生圖/生片模型的 Character Reference / 起始幀鎖臉功能使用。

---

## 2. 對現有系統的啟發與落差評估

- **適用情境**：當需要在圖片或短影片測試流程中快速挑選「日系人物角色參考圖」（鎖定角色臉型、髮型與穿搭，取代自己從零抽卡或侵犯真人肖像權）時，該 CC0 圖庫是直接可用的線上素材來源。
- **風險與限制提醒**：
  - 雖標註 CC0（可免費商用、免標示出處），仍建議在正式商業專案使用前自行核對特定圖像是否與真實人物高度相似。
  - 屬於純線上靜態素材網站，無 API、無 MCP 亦無須本地部署。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：為現成免費 CC0 線上人臉／造型參考素材網站（及同系列姿勢／服裝庫），有視覺測試或首幀鎖臉需求時直接前往取用即可，無系統整合或開發缺口。
