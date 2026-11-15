---
id: "2026-11-15-pound0423-single-html-glitch-vfx-eval"
title: "POUND0423 單檔影片／圖片故障特效（Glitch VFX）工具查證與技術評估"
source_url: "https://www.threads.com/@pound0423/post/Dd6eXh4iaCk"
source_platform: "Threads / GitHub"
author: "@pound0423 (POUND0423)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 2
cluster_role: "前端Glitch視覺特效"
short_title: "POUND0423故障特效評估"
tags:
  - glitch-effect
  - webgl
  - canvas
  - video-vfx
  - single-file-html
  - creative-coding
---

# POUND0423 單檔影片／圖片故障特效（Glitch VFX）工具查證與技術評估

- **來源連結**：[Threads 原貼文 (@pound0423)](https://www.threads.com/@pound0423/post/Dd6eXh4iaCk) ｜ [GitHub (@POUND0423)](https://github.com/POUND0423)
- **發布平台 / 作者**：`Threads` / `@pound0423`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`

> **GitHub 實查結果**：
> 曾查 [POUND0423 GitHub 公開倉庫列表](https://github.com/POUND0423?tab=repositories)（當時所見截至 `2026-11-04`，含 `AI-drama-pound`、`GAT-Taiwan-Pound`、`VFX-to-pound01` 等），**本次未取得可對應本篇貼文的原始碼**。未取得完整分頁的 repo 清單，[Threads 原貼文](https://www.threads.com/@pound0423/post/Dd6eXh4iaCk)也讀取失敗，因此是否已開源屬未查證，不能當成「不存在」。貼文內容（展示影片效果、預告晚點開源）為轉述，未查證。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景；來源轉述，未查證）**：台灣創作者 `@pound0423`（GitHub：`POUND0423`），長期以 Claude 輔助開發單檔前端視覺互動工具、Three.js 漫遊專案與 AI 短劇／廣告提示詞工作流。
- **What（核心產出；作者宣稱，未實測）**：使用 Claude Opus 5.5 製作的「影片／圖片一鍵故障特效（Glitch）工具」，支援上傳圖片或影片後快速套用多種動態故障藝術特效並輸出。
- **Why（訴求痛點）**：讓影片創作者無須開啟 Premiere / After Effects 調繁瑣參數，即可在瀏覽器快速為素材加上賽博龐克／VHS／信號干擾等風格化轉場與視覺衝擊。
- **How（技術實作機制推測與分析）**：
  - 以下為推測：此類單檔前端特效可以不靠大型 AI 模型推論，用 **HTML5 Canvas 2D / WebGL Fragment Shader** 的即時像素處理管線做出來。沒看到原始碼，不代表作者實際採用 Three.js、WebGL 或特定編碼器：
    - 常見故障特效原語：RGB 色差分離（Chromatic Aberration / `rgbashift`）、水平掃描線（Scanlines）、切片錯位（Slice Displacement）、噪點／VHS 抖動（Noise / Jitter）與色塊量化。
    - 影片匯出路線：即時繪製於 `<canvas>` 後以 `canvas.captureStream()` 搭配 `MediaRecorder` 錄製 WebM/MP4（各瀏覽器支援的容器與編碼不同，須先用 [`MediaRecorder.isTypeSupported()`](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/isTypeSupported_static) 檢查，不保證每個 Windows 瀏覽器都能輸出 MP4；實務需額外處理原音軌混流與幀率同步，或改由 WebCodecs / FFmpeg.wasm 編碼）。
- **When & Where（適用時機與場景）**：短影音片頭吸睛轉場、MV／Cyberpunk 風格視覺素材、單張海報快速後製。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `C:\GitHub\ai-inbox\templates\single-file-creative-coding-skill.md`（單檔創意編碼工具規範）
  - `C:\GitHub\ai-inbox\notes\2026-11-15-browser-webgpu-photo-video-editor-prompt-eval.md`（純瀏覽器媒體處理垂直切片策略）
  - `SanHsien/video-autopilot-kit`（未來若需自動化套用轉場／故障濾鏡的短影音管線）
- **落差與採納判斷**：
  1. **本次未取得可審查的原始碼**：無法直接評估其音軌保留、瀏覽器匯出畫質與跨格式相容性。純 `MediaRecorder` 在長片或非固定幀率影片的音畫同步，是需要驗證的相容性風險；沒有原片與實測，不能說該作品有此缺陷。
  2. **技術門檻低、可按需現做**：WebGL Glitch Shader 與 FFmpeg [`rgbashift`](https://ffmpeg.org/ffmpeg-filters.html#rgbashift) / `tblend` 濾鏡皆是現成可參考的技術（不是作者使用它們的證據）；若未來在 `video-autopilot-kit` 或前端專案需要故障轉場，直接按實際規格實作一個垂直切片或掛入 FFmpeg filter 即可，無須提前為了拿不到原始碼的示範專案另建獨立前端工具。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：目前沒有具體後製需求，也缺可審查的來源；且瀏覽器 Glitch 特效屬於低門檻、可隨時按需補齊的單點濾鏡能力；保留本篇技術拆解（WebGL Shader 原語與 `MediaRecorder` 音軌同步注意事項）作為日後若有短影音後製需求時的參考即可。
