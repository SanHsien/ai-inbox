---
id: "2026-11-15-pound0423-single-html-glitch-vfx-eval"
title: "POUND0423 單檔 Blobtrace（斑點追蹤＋故障特效）網頁工具查證與技術評估"
source_url: "https://www.threads.com/@pound0423/post/Dd6eXh4iaCk"
source_platform: "Threads / GitHub"
author: "@pound0423 (POUND0423)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 2
cluster_role: "前端Glitch視覺特效"
short_title: "POUND0423故障特效評估"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 8
source_replies: 38
tags:
  - glitch-effect
  - webgl
  - canvas
  - video-vfx
  - single-file-html
  - creative-coding
---

# POUND0423 單檔 Blobtrace（斑點追蹤＋故障特效）網頁工具查證與技術評估

- **來源連結**：[Threads 原貼文 (@pound0423)](https://www.threads.com/@pound0423/post/Dd6eXh4iaCk) ｜ [GitHub (@POUND0423)](https://github.com/POUND0423)
- **發布平台 / 作者**：`Threads` / `@pound0423`（貼文日期 2026-09-30）
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`

> **GitHub 實查結果**：
> 曾查 [POUND0423 GitHub 公開倉庫列表](https://github.com/POUND0423?tab=repositories)（當時所見截至 `2026-11-04`，含 `AI-drama-pound`、`GAT-Taiwan-Pound`、`VFX-to-pound01` 等），**本次未取得可對應本篇貼文的原始碼**。2026-11-16 重查：用 GitHub API 列出該帳號全部 11 個公開 repo，沒有對應本篇的專案；[Threads 原貼文](https://www.threads.com/@pound0423/post/Dd6eXh4iaCk)這次讀得到，作者預告「晚點開源」，但也說「不分享連結，只給指令」，並把完整生成指令貼在留言（見第 0 節）。所以現況是：沒有公開原始碼，有完整規格。

---

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**：貼文附一支約 23 秒的示範影片（抽 8 格看，2026-11-16）。畫面左邊是影片預覽、右邊是深色控制面板；開頭是內建示範動畫與選檔視窗，載入一段古裝武打片後，人物身上疊了追蹤框、Windows 2000 風格視窗外框、瞄準鏡圓環、資料標籤與連線，框內套網點、馬賽克、色偏等濾鏡，後段把效果一路加滿。影片看得出這是「斑點追蹤＋特效疊加」工具，不只是整個畫面套故障濾鏡。
- **作者留言補充**：作者在第一則留言貼出完整的生成指令（很長，以下只列重點）：
  - 工具名稱是 **Blobtrace**，風格參考 TouchDesigner 的 blob tracking。
  - 單一 HTML 檔、不用框架、用 Canvas 2D 繪圖，全部在本機運算、不上傳檔案；字型從 Google Fonts 載入。
  - 偵測：畫面縮成 160 格寬再算，追蹤依據有亮部、暗部、動態三種，用連通區域分析找斑點，跨影格依中心點距離配對並給固定編號。
  - 效果：15 種框線類基本效果、4 種連線樣式、14 種框內濾鏡（Glitch 只是其中一種）、全畫面色調／點陣／撕裂／色偏／掃描線，另有 Web Audio 合成音效。
  - 錄製：`canvas.captureStream(30)` 搭配 `MediaRecorder`，優先輸出 WebM，不支援才改 MP4。上傳的影片是靜音循環播放。
  - 貼文本文說「晚點開源放 GitHub」，同時說「不分享連結，只給指令」。
- **網友留言重點**（2026-11-17 登入後補讀：貼文顯示 43 則，熱門、最新兩種排序都捲到底、子回覆都點開，合計讀到 38 則，其餘 5 則平台不顯示；作者回覆 12 則多為道謝）：
  - `@inca1399` 說用 Gemini 照同一份指令做出一樣的版本並附分享連結。這次打開了：是 Gemini Canvas 的分享頁，標題「斑點追蹤網頁工具 Blobtrace 開發」，進入前先跳出「這個應用程式是由他人打造、可能並不安全」的警告。本次沒有按繼續去執行別人的應用程式，所以只能確認連結有效、標題相符，不能確認成品與作者的一樣。
  - `@songjaylu` 問指令能不能直接貼進 App 用，作者答可以（沒有說是哪個 App、也沒有示範）。
  - 作者另外釘選了一則留言，邀人加入他的 Discord 群。
  - 其餘是稱讚、道謝與留言卡位，沒有人回報錯誤、瀏覽器相容問題或錄影畫質。
- **GitHub 現況**：2026-11-16 用 API 列出 `POUND0423` 全部 11 個公開 repo，沒有 Blobtrace 或對應這則貼文的專案；2026-11-17 再查仍是 11 個、仍然沒有，發文至今一個半月未見開源。
- **對分析的影響**：原筆記寫 Threads 貼文讀取失敗、作法全是推測。這次讀到了，改動如下：
  1. 標題與第 1 節 What：工具其實是 Blobtrace，核心是斑點追蹤加疊圖，故障特效只是其中一類濾鏡。
  2. 第 1 節 How：原本推測「Canvas 2D 或 WebGL Fragment Shader」，依作者指令改為確定是 Canvas 2D、沒有用 WebGL；錄製方式確定是 `captureStream` 加 `MediaRecorder`、WebM 優先。
  3. 第 2 節：原本擔心「原音軌混流與音畫同步」。作者的設計是影片靜音播放，錄下來的聲音只有合成音效，等於沒有保留原片聲音，這是功能限制而不是待驗證的風險。
  4. 「缺可審查來源」改為：沒有原始碼，但有完整規格，要用時可照指令重新生成。
  5. 結論仍是封存、不開任務：目前沒有需求；指令本身就是可重現的規格。
  6. 2026-11-17 補讀的 16 則留言沒有推翻任何一點。「有人用 Gemini 照做成功」仍是未驗證的網友自述（分享頁要先同意執行他人應用程式才看得到），第 2 節的寫法不用改。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景；來源轉述，未查證）**：台灣創作者 `@pound0423`（GitHub：`POUND0423`），長期以 Claude 輔助開發單檔前端視覺互動工具、Three.js 漫遊專案與 AI 短劇／廣告提示詞工作流。
- **What（核心產出；作者宣稱，未實測）**：使用 Claude Opus 5.5 製作的單檔網頁工具 **Blobtrace**。貼文本文稱它是「一鍵添加故障特效」，但依作者貼在留言的指令與示範影片，核心是對影片做斑點追蹤（blob tracking），在追蹤到的區塊上疊追蹤框、連線、標籤與框內濾鏡，故障效果（Glitch）只是 14 種濾鏡之一；可即時預覽並錄成影片。
- **Why（訴求痛點）**：讓影片創作者無須開啟 Premiere / After Effects 調繁瑣參數，即可在瀏覽器快速為素材加上賽博龐克／VHS／信號干擾等風格化轉場與視覺衝擊。
- **How（技術實作機制推測與分析）**：
  - 依作者指令（2026-11-16 讀到，不是原始碼）：單一 HTML、不用框架、**Canvas 2D** 繪圖，全部在本機運算；沒有用 WebGL 或 Three.js。偵測先把畫面縮成 160 格寬，依亮部／暗部／動態三種方式取遮罩，再做連通區域分析與跨影格配對。以下兩點原為推測，保留作技術背景，並標出與作者做法的異同：
    - 常見故障特效原語（作者的 Glitch 濾鏡寫的是「RGB 錯位加橫向切片」，另有全畫面撕裂、色偏、掃描線）：RGB 色差分離（Chromatic Aberration / `rgbashift`）、水平掃描線（Scanlines）、切片錯位（Slice Displacement）、噪點／VHS 抖動（Noise / Jitter）與色塊量化。
    - 影片匯出路線（與作者指令相符：`canvas.captureStream(30)`，WebM 優先、不支援才 MP4）：即時繪製於 `<canvas>` 後以 `canvas.captureStream()` 搭配 `MediaRecorder` 錄製 WebM/MP4（各瀏覽器支援的容器與編碼不同，須先用 [`MediaRecorder.isTypeSupported()`](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/isTypeSupported_static) 檢查，不保證每個 Windows 瀏覽器都能輸出 MP4；實務需額外處理原音軌混流與幀率同步，或改由 WebCodecs / FFmpeg.wasm 編碼）。
- **When & Where（適用時機與場景）**：短影音片頭吸睛轉場、MV／Cyberpunk 風格視覺素材、單張海報快速後製。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `C:\GitHub\ai-inbox\templates\single-file-creative-coding-skill.md`（單檔創意編碼工具規範）
  - `C:\GitHub\ai-inbox\notes\2026-11-15-browser-webgpu-photo-video-editor-prompt-eval.md`（純瀏覽器媒體處理垂直切片策略）
  - `SanHsien/video-autopilot-kit`（未來若需自動化套用轉場／故障濾鏡的短影音管線）
- **落差與採納判斷**：
  1. **沒有原始碼，但有完整規格**：作者貼出的指令足以重新生成同類工具（留言有人稱用 Gemini 照做成功，未驗證）。依指令，上傳的影片是靜音循環播放，錄下來的聲音只有工具自己合成的音效，所以**不保留原片聲音**；要拿來後製有聲影片，得另外把原音軌合回去。瀏覽器匯出畫質與長片穩定度仍未實測。
  2. **技術門檻低、可按需現做**：WebGL Glitch Shader 與 FFmpeg [`rgbashift`](https://ffmpeg.org/ffmpeg-filters.html#rgbashift) / `tblend` 濾鏡皆是現成可參考的技術（不是作者使用它們的證據）；若未來在 `video-autopilot-kit` 或前端專案需要故障轉場，直接按實際規格實作一個垂直切片或掛入 FFmpeg filter 即可，無須提前為了拿不到原始碼的示範專案另建獨立前端工具。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：目前沒有具體後製需求；作者的指令已是可重現的規格，需要時照指令生成即可，不必先建工具；且瀏覽器 Glitch 特效屬於低門檻、可隨時按需補齊的單點濾鏡能力；保留本篇技術拆解（WebGL Shader 原語與 `MediaRecorder` 音軌同步注意事項）作為日後若有短影音後製需求時的參考即可。
