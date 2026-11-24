---
id: "2026-11-24-cultiwise-gemini-notebook-shorts-video-eval"
title: "享知 Cultiwise YouTube 實測評析：《Gemini Notebook 短影音製作教學》——中文知識型 Shorts 生成能力、自訂風格提示詞與低動態簡報上限"
source_url: "https://youtu.be/pw18hhi-nqE"
source_platform: "youtube"
author: "享知Cultiwise (@cultiwise)"
analyzed_at: "2026-11-24"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 4
source_reviewed_at: "2026-11-24"
source_review_note: "已完整解析影片資訊欄、全片 08:46 繁中官方字幕（622 行 VTT）及全部 4 則 YouTube 留言；未擷取影片畫面截圖。"
status: archived
cluster: 3
cluster_role: "筆記短影音評析"
short_title: "GeminiNotebook短影音實測"
tags:
  - gemini-notebook
  - notebooklm
  - shorts
  - ai-video
  - google
---

# 享知 Cultiwise YouTube 實測評析：《Gemini Notebook 短影音製作教學》——中文知識型 Shorts 生成能力、自訂風格提示詞與低動態簡報上限

- **來源影片**：[`youtu.be/pw18hhi-nqE`](https://youtu.be/pw18hhi-nqE)（頻道：`享知Cultiwise`，發布於 `2026-09-24`，片長 `08:46`，`19,177` 次觀看、`175` 讚、`4` 則留言）
- **分析日期**：`2026-11-24`
- **當前狀態**：`⚪ 歸檔參考 (Archived — 不另開工單)`
- **相關交叉參照**：
  - [`notes/2026-11-07-gemini-notebook-official-api-mcp-preview.md`](./2026-11-07-gemini-notebook-official-api-mcp-preview.md)（Gemini Notebook 官方 API / MCP 預覽版評估：僅支援寫入來源，未開放音視訊摘要端點）
  - [`docs/code-as-video-creative-patterns.md`](../docs/code-as-video-creative-patterns.md)（本庫程式化影片／動態簡報生成模式）

---

## 0. 原始資料盤點（資訊欄、08:46 繁中字幕與 4 則留言）

- **產品更名與功能定位**：原 NotebookLM 已更名為 **Gemini Notebook**（`notebook.google.com`），在「影片摘要」工作室內除了既有的「說明影片」外，新增支援中文直式短影音的 **「精簡」** 模式，可將既有筆記本來源轉為約 1 分多鐘的解說型 Shorts 並下載 MP4。
- **操作細節（字幕 `01:08–05:45`）**：
  - 來源支援網站連結、公開 YouTube 連結（非公開／私人影片無法讀取）與文件／書籍，生成前可勾選或取消特定來源以控制引用範圍。
  - 支援在下方「自訂主題」輸入框指定切入主題（示範：「簡單的咖啡烘焙指南」「常見的沖煮方式」）。
  - 「精簡」模式目前尚未提供「說明影片」的預設視覺風格選擇器，但可在自訂主題提示詞中直接指定風格（作者於留言 #2 補充：於約 `04:20` 處輸入 `"collage style"` 等字樣可切換為拼貼風）。
- **片尾兩支實測成品（`05:51–08:23`）**：分別展示「咖啡豆單向透氣閥」與「手沖／義式／法壓／冰滴四種沖煮方式比較」兩段中文旁白知識短片。
- **全部 4 則留言**：`@CarlosGuadamuz-c8w` 詢問寫實風與拼貼風如何下提示詞，作者回覆於 `04:20` 處在下方提示詞區指定風格（如 `"collage style"`）；其餘為觀眾感謝與頻道導流置頂留言。

---

## 1. 優缺點與對現有系統的評估

- **實測優勢**：
  - 繁體中文腳本撰寫與語音辨識／旁白自然度已有可用水準，無需先產英文再人工翻譯。
  - 可直接限定單本筆記本內的部分來源產出解說短片，適合無程式碼門檻的快速知識拆條。
- **明確限制**：
  1. **低動態感**：作者實測指出「動態相對較少，比較像用 PPT 方式做直式呈現」，畫面表現力明顯弱於程式化動態圖表或專業剪輯。
  2. **功能與 API 落差**：純 Web UI 功能（`notebook.google.com`）；對照 [`notes/2026-11-07-gemini-notebook-official-api-mcp-preview.md`](./2026-11-07-gemini-notebook-official-api-mcp-preview.md) 已知官方 MCP / API 目前僅開放筆記本建立與來源寫入，未提供影片摘要生成端點，無法納入自動化管線。
  3. **穩定度差異**：作者指出英文生成穩定性仍略高於剛上線的中文版，且新功能介面尚缺獨立風格選單。
- **不開工單理由**：屬於消費級 Web UI 功能更新展示，無新增可自動化的 API／MCP／CLI 能力，且其低動態簡報形態已有本庫 [`docs/code-as-video-creative-patterns.md`](../docs/code-as-video-creative-patterns.md) 覆蓋，故採純歸檔參考。
