---
id: "2026-11-15-runway-mcp-collage-motion-graphics-prompt"
title: "Runway MCP ＋ 程式化動態圖形（報紙剪貼拼貼 60 秒短片）工作流與分權 Prompt 評估"
source_url: "https://mcp.runwayml.com/mcp"
source_platform: "Social / MCP"
author: "匿名社群分享（Runway MCP 官方生態）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 2
cluster_role: "MCP圖資與程式化動畫"
short_title: "RunwayMCP拼貼動畫Prompt"
tags:
  - runway-mcp
  - motion-graphics
  - remotion
  - collage-animation
  - prompt-engineering
  - ai-video
---

# Runway MCP ＋ 程式化動態圖形（報紙剪貼拼貼 60 秒短片）工作流與分權 Prompt 評估

- **來源連結**：[Runway Hosted MCP Server](https://mcp.runwayml.com/mcp) ｜ [runwayml/runway-api-mcp-server](https://github.com/runwayml/runway-api-mcp-server)
- **發布平台 / 作者**：`社群平台` / `匿名分享（搭配 Runway 官方 MCP）`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`](./2026-10-18-awesome-opus5-5-videos-prompt-zoo.md)（Remotion 程式化影片與 Prompt 庫）
  - [`notes/2026-11-15-audio-first-greenscreen-ai-commercial-pipeline.md`](./2026-11-15-audio-first-greenscreen-ai-commercial-pipeline.md)（Audio-First 音軌對齊與合成管線）

> **MCP 實查結果**：
> Runway 官方確實提供完整的 MCP 生態系：雲端託管端點 `https://mcp.runwayml.com/mcp`（支援 Claude / Cursor 等客戶端 OAuth 連線直接生成圖影資產）、開發者端點 `https://dev.runwayml.com/mcp`，以及開源倉庫 `runwayml/runway-api-mcp-server`。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：示範使用 Claude Opus 5.5（推理強度設為中間值 `medium`）串接 Runway MCP，產出一部 60 秒「報紙剪貼／混合媒體風格」科普短片（《衛生棉的 138 年簡史》），具備剪報圖層、紅色印章、撕紙轉場、定格抖動（Stop-motion Jitter）、旁白與配樂。
- **Why（為解決什麼問題）**：
  - 直接用 AI 影片模型生成「含大量歷史文字、剪報排版、多段時間軸敘事的 60 秒長片」，極易出現字幕亂碼、畫面閃爍與節奏失控。
- **How（核心分權架構與 Prompt 模板）**：
  - **工具分權**：AI 視覺端（Runway MCP）**只產出靜態剪報／混合媒體美術圖資**；所有動態圖形元素、時間軸編排、撕紙遮罩轉場、定格抖動與文字／印章動畫，全由程式碼模型（Remotion / Canvas / SVG）完成。
  - **原貼文核心 Prompt 模板**：
    > 「製作一個 `[60 秒]` 的動態圖形嚮導影片，內容是 `[你的主題]`。所有視覺圖像應使用 Runway 處理，所有動態圖形元素和動畫應由你完成。藝術風格為 `[報紙剪裁／混合媒體風格]`，並具有高度精細度。這是你作品集的一部分，請確保製作得非常出色。」
  - **推理參數建議**：推理強度設為**中間值（Medium）**，避免過低漏掉時間軸對齊、或過高造成動畫代碼過度抽象與耗時。
- **When & Where**：歷史科普、品牌故事、資訊圖表解說等需要高排版精準度與特定美術材質（拼貼、紙張、版畫）的 30–60 秒知識型短影音。

---

## 2. 啟發與適用性評估

- **值得採納的核心模式**：
  1. **「MCP 生靜態資產＋程式碼跑動態圖形」的職責分離**：比起全靠端到端生影模型賭抽卡，讓生圖工具只生成去背或高解析靜態貼圖（Paper Cutouts / Textures / Stamps），再交給 Remotion / CSS / Canvas 用確定性關鍵幀（如 4–6 fps stepped jitter 模擬定格動畫、SVG `feTurbulence` + `clipPath` 模擬撕紙邊緣）組合，成品可控性與文字正確率高出數個量級。
  2. **無須綁死 Runway 付費額度**：靜態拼貼圖資這一段可無痛替換為本機其他生圖介面（如 Antigravity 內建 `image-generator` 或現有生圖 MCP），僅保留該「視覺與動態分權 Prompt 骨架」即可複用。
- **實務補強提醒（原 Prompt 未涵蓋之處）**：
  - 原 Prompt 未指定旁白來源與時長鎖定，若未先生成 TTS 音檔並量測秒數（Audio-First），60 秒動畫仍可能與實際唸白速度脫節；實作時應先出旁白音檔、取時間戳後再驅動動態圖形腳本。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不新增獨立工程任務**（維持 `status: archived`）。
  - **理由**：本篇價值在於提供一套簡潔可複用的「靜態圖資生成＋程式化 Motion Graphics 分權 Prompt 模板」與 `Runway MCP` 實查紀錄；相關程式化影片合成與 Audio-First 時間軸整合已歸口於 `T-20261115-11`（`SanHsien/video-autopilot-kit`）與 `notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`，不另拆重複任務。
