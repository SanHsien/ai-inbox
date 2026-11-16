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
source_review: unavailable
source_reviewed_at: 2026-11-16
source_review_note: "source_url 是 MCP 端點不是貼文；原社群貼文與示範短片沒有留下連結或截圖，圖片、影片與留言無從查看"
tags:
  - runway-mcp
  - motion-graphics
  - remotion
  - collage-animation
  - prompt-engineering
  - ai-video
---

# Runway MCP ＋ 程式化動態圖形（報紙剪貼拼貼 60 秒短片）工作流與分權 Prompt 評估

- **來源連結**：[Runway Hosted MCP Server](https://mcp.runwayml.com/mcp) ｜ [runwayml/runway-api-mcp-server](https://github.com/runwayml/runway-api-mcp-server)（已於 2026-09-30 封存，僅供歷史參考）
- **發布平台 / 作者**：`社群平台` / `匿名分享（搭配 Runway 官方 MCP）`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`](./2026-10-18-awesome-opus5-5-videos-prompt-zoo.md)（Remotion 程式化影片與 Prompt 庫）
  - [`notes/2026-11-15-audio-first-greenscreen-ai-commercial-pipeline.md`](./2026-11-15-audio-first-greenscreen-ai-commercial-pipeline.md)（Audio-First 音軌對齊與合成管線）

> **MCP 實查結果**：
> Runway 官方有兩個入口，用途不同：一般使用者的圖影生成 MCP 見 [runway.com/mcp](https://runway.com/mcp)；開發者端見 [dev.runwayml.com/mcp](https://dev.runwayml.com/mcp)（有客戶端連線設定）與 [dev.runwayml.com/agents](https://dev.runwayml.com/agents)，不可混為同一介面。託管端點 `https://mcp.runwayml.com/mcp` 查證時回應 401，只證實需要驗證；OAuth 連線與工具清單未查證。開源倉庫 [`runwayml/runway-api-mcp-server`](https://github.com/runwayml/runway-api-mcp-server) 已於 2026-09-30 封存，README 引導改用上述入口，舊實作僅供歷史參考。
> 本篇 `source_url` 是 MCP 端點，不是社群貼文；原貼文、影片與逐字稿都沒有可回溯來源，以下示範內容與提示詞皆為社群轉述，未查證。

---

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**：看不到。本篇 `source_url` 是 Runway 的 MCP 端點（需驗證，回 401），不是社群貼文；原貼文與那支 60 秒示範短片都沒有留下連結或截圖。
- **作者留言補充**：看不到（同上）。
- **網友留言重點**：看不到（同上）。
- **對分析的影響**：沒有新資料。第 1 節的示範內容、Prompt 模板與「推理強度設中間值」仍全部是未查證的社群轉述，沒有成品畫面可以判斷剪報風格、文字是否亂碼或節奏好壞；結論不變。日後找到原貼文再補看影片與留言。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What（社群轉述，未查證）**：示範使用 Claude Opus 5.5（推理強度設為中間值 `medium`）串接 Runway MCP，產出一部 60 秒「報紙剪貼／混合媒體風格」科普短片（《衛生棉的 138 年簡史》），具備剪報圖層、紅色印章、撕紙轉場、定格抖動（Stop-motion Jitter）、旁白與配樂。
- **Why（為解決什麼問題）**：
  - 直接用 AI 影片模型生成「含大量歷史文字、剪報排版、多段時間軸敘事的 60 秒長片」，極易出現字幕亂碼、畫面閃爍與節奏失控。
- **How（核心分權架構與 Prompt 模板）**：
  - **工具分權**：AI 視覺端（Runway MCP）**只產出靜態剪報／混合媒體美術圖資**；所有動態圖形元素、時間軸編排、撕紙遮罩轉場、定格抖動與文字／印章動畫，全由程式碼模型（Remotion / Canvas / SVG）完成。
  - **轉述的核心 Prompt 模板（無法回溯原貼文，未查證）**：
    > 「製作一個 `[60 秒]` 的動態圖形嚮導影片，內容是 `[你的主題]`。所有視覺圖像應使用 Runway 處理，所有動態圖形元素和動畫應由你完成。藝術風格為 `[報紙剪裁／混合媒體風格]`，並具有高度精細度。這是你作品集的一部分，請確保製作得非常出色。」
  - **推理參數（分享者宣稱，不是官方建議）**：推理強度設為**中間值（Medium）**，理由是避免過低漏掉時間軸對齊、或過高造成動畫代碼過度抽象與耗時。沒有三種強度的對照實測，屬未驗證假設。
- **When & Where**：歷史科普、品牌故事、資訊圖表解說等需要高排版精準度與特定美術材質（拼貼、紙張、版畫）的 30–60 秒知識型短影音。

---

## 2. 啟發與適用性評估

- **值得採納的核心模式**：
  1. **「MCP 生靜態資產＋程式碼跑動態圖形」的職責分離**：比起全靠端到端生影模型賭抽卡，讓生圖工具只生成去背或高解析靜態貼圖（Paper Cutouts / Textures / Stamps），再交給 Remotion / CSS / Canvas 用確定性關鍵幀（如 4–6 fps stepped jitter 模擬定格動畫、SVG `feTurbulence` + `clipPath` 模擬撕紙邊緣）組合；程式化的文字與時間軸提供可測的控制點（規格可參考 [Remotion 官方文件](https://www.remotion.dev/docs/)）。實際成品差異未實測，沒有基準可比。
  2. **不必綁定 Runway（架構方向，未驗證）**：靜態拼貼圖資這一段可考慮換成其他生圖介面（如 Antigravity 內建 `image-generator` 或現有生圖 MCP），保留「視覺與動態分權 Prompt 骨架」；替換的介面、授權與配額都未驗證，本機介面也不等於沒有雲端成本。[舊 repo README](https://github.com/runwayml/runway-api-mcp-server) 列出 Developer Billing 與 API key 前置，示例預設還可能路由到 Seedance，與本機「不額外付費、不用中國服務」的限制衝突，不能照抄預設生成路徑。
- **實務補強提醒（原 Prompt 未涵蓋之處）**：
  - 原 Prompt 未指定旁白來源與時長鎖定，若未先生成 TTS 音檔並量測秒數（Audio-First），60 秒動畫仍可能與實際唸白速度脫節；實作時應先出旁白音檔、取時間戳後再驅動動態圖形腳本。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不新增獨立工程任務**（維持 `status: archived`）。
  - **理由**：本篇價值在於提供一套簡潔可複用的「靜態圖資生成＋程式化 Motion Graphics 分權 Prompt 模板」與 `Runway MCP` 實查紀錄；與 `T-20261115-11`（`SanHsien/video-autopilot-kit`）只有部分重疊：該任務是 Audio-First 綠幕合成、去溢色與 BGM ducking，不含剪報美術、撕紙轉場與拼貼動畫，所以整套 60 秒拼貼並未由它實作。程式化影片另可參考 `notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`。目前無具體需求，且不加付費安裝任務，故不另拆。
