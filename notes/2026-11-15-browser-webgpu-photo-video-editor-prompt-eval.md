---
id: "2026-11-15-browser-webgpu-photo-video-editor-prompt-eval"
title: "純瀏覽器 WebGPU AI 修圖與影片工具 Prompt 評估：參考專案查證與一次全包空殼風險分析"
source_url: "https://github.com/xiaowu89/skill-matting"
source_platform: "Social / GitHub"
author: "匿名社群分享（參考專案：xiaowu89/skill-matting、lxulxu/WatermarkRemover）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 2
cluster_role: "前端WebGPU修圖"
short_title: "WebGPU修圖Prompt評估"
source_reviewed_at: 2026-11-18
source_review: partial
source_review_note: "原貼文搜尋不到（試過：Threads 站內搜尋「skill-matting」、Facebook 貼文搜尋「skill-matting WatermarkRemover WebGPU」「WebGPU 美圖秀秀 去水印 去背 Opus 5.5 Prompt」「純瀏覽器 WebGPU 修圖 去水印 Prompt」；都沒有結果）；替代來源兩個參考 repo 的 README、2 張示範圖與 5 則 issue 已讀完"
source_images: 2
source_replies: 5
tags:
  - webgpu
  - onnx-runtime-web
  - webcodecs
  - image-editing
  - video-matting
  - watermark-removal
---

# 純瀏覽器 WebGPU AI 修圖與影片工具 Prompt 評估：參考專案查證與一次全包空殼風險分析

- **來源連結**：
  - [xiaowu89/skill-matting](https://github.com/xiaowu89/skill-matting)（MIT、16 stars、PowerShell、最後更新 2026-08-13）
  - [lxulxu/WatermarkRemover](https://github.com/lxulxu/WatermarkRemover)（**GPL-3.0**、838 stars、Python、最後更新 2026-11-08）
- **發布平台 / 作者**：`社群平台` / `匿名分享（Prompt 示範）`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 已封存 (Archived)`

---

## 0. 原始資料盤點

> 2026-11-18 再找原貼文：原貼文搜尋不到（試過：Threads 站內搜尋「skill-matting」、Facebook 貼文搜尋「skill-matting WatermarkRemover WebGPU」「WebGPU 美圖秀秀 去水印 去背 Opus 5.5 Prompt」「純瀏覽器 WebGPU 修圖 去水印 Prompt」；都沒有結果）；替代來源兩個參考 repo 的 README、2 張示範圖與 5 則 issue 已讀完。維持 `partial`。

> 2026-11-17 用瀏覽器重看。原社群貼文沒有留下連結（作者匿名），貼文本身的圖片與留言**沒看到**；以下只涵蓋兩個參考 repo。

- **作者圖片**：
  - 社群貼文：看不到（沒有連結）。
  - `xiaowu89/skill-matting` README：只有 3 個徽章，沒有示範圖。
  - `lxulxu/WatermarkRemover` README 圖 1（原始畫格）：舞台表演畫面，右上角有影音平台的半透明水印。圖 2（去除後）：同一畫格，右上角水印消失，背景紋理補得自然；這是作者挑的單一示範，不是品質基準。另有一張 star 歷史圖，與分析無關。
- **作者留言補充**：無（兩個 repo 的 issue 裡作者都沒有實質回覆）。
- **網友留言重點**（GitHub issue）：
  - skill-matting #1：有人照 README 的影片去背指令執行就報「Path 參數為空字串」；錯誤輸出裡帶有廠商的聯絡帳號提示，可見這個 skill 是商業公司的導流工具。未關閉。
  - WatermarkRemover #14：去除效果好，但大螢幕或亮色背景下仍看得出水印輪廓，希望加區域模糊。
  - WatermarkRemover #12、#15、#11：相依套件版本衝突（`huggingface_hub` 拿掉 `cached_download`）、wheel 建置失敗、GPU 沒被用到；都是安裝環境問題。
- **對分析的影響**：
  - 補上 README 寫明的事實：skill-matting **首次使用要連網從魔搭（ModelScope，中國服務）下載模型與執行檔**，Lite 模型約 88.6 MB、Full 約 440 MB。原筆記只寫了遙測，沒寫模型下載來源；這讓「目前不安裝」的結論更站得住。已改第 1 節 How。
  - WatermarkRemover 是包 LaMa 模型（`lama_cleaner`）的腳本，需 Python 3.10、手動框選水印區域，且同批影片尺寸與水印位置必須一致；已補進第 1 節 How。
  - 封存結論與 `T-20261115-07` 不做的判斷不變。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（參考來源與對象）**：社群分享以 Claude Opus 5.5 建置「純前端離線版美圖秀秀＋影片去水印／去背／放大」的完整規格 Prompt，並引用兩個開源桌面專案作為演算法參考。
- **What（規格主張）**：
  - **純瀏覽器運算、不上傳伺服器**：上方工具列、左側 8 項工具（新增、調整、文字、消除圖 MI-GAN、摳圖 U²-Net、變清晰 Real-ESRGAN / Upscayl、調色、影片摳圖）＋「影片工具」分頁（MP4/WebM 保留音軌、固定位置去水印、影片去背、2x/4x 放大至 4K）。
  - **互動體驗**：游標中心滾輪縮放、空白鍵拖曳、前後對比線、進度顯示與取消回滾、PNG/JPG/WebP/透明 WebM 匯出。
- **Why（訴求痛點）**：免安裝桌面軟體、保護隱私（檔案不離機）、不消耗雲端推論伺服器費用。
- **How（參考專案實況查證）**：
  - `xiaowu89/skill-matting`（MIT）：並非純 JS，實為封裝成 Agent Skill 的 `scripts/matting.ps1`，透過 `vision.cpp` + `ggml` + `BiRefNet` 在本機執行圖片／影片去背。**腳本內含遙測**：[`scripts/matting.ps1` 第 73～115 行](https://github.com/xiaowu89/skill-matting/blob/master/scripts/matting.ps1#L73)會建立或重用裝置識別碼（來源含主機名稱與網卡資訊的雜湊），向一個以 base64 保存的追蹤網址發 POST；第 1025～1026 行在圖片／影片命令開始時呼叫。這是靜態讀原始碼的結果，沒有實際執行抓包；沒有證據顯示它上傳圖片本體，但「本機推論」不等於全程不連網。README 另寫明首次使用要連網從魔搭（ModelScope，中國服務）下載模型與執行檔（Lite 約 88.6 MB、Full 約 440 MB）（2026-11-17 查 README）。目前不安裝這個 skill。
  - `lxulxu/WatermarkRemover`（**GPL-3.0**）：單檔 Python 腳本 `watermark_remover.py`，包 LaMa 模型（`lama_cleaner`）對影片固定區域逐格修補去水印。README 寫明需 Python 3.10、執行時手動框選水印區域，同一批影片的尺寸與水印位置必須一致，不支援會移動的水印（2026-11-17 查 README）。
- **When & Where（適用邊界）**：純前端 WebGPU/ONNX 適合單張靜態圖片即時編輯；若硬要單靠單頁瀏覽器一次承載多組大型超解析＋影片逐格推理＋音軌重新封裝，極易受限於瀏覽器記憶體與 WebGPU 限制。
- **Key Metrics / Numbers（實務技術規模）**：包含 3 種超解析模型＋MI-GAN＋U²-Net，ONNX 權重總和通常達數百 MB；影片 4K 逐格推理與編碼屬高度耗時／高顯存負載。

---

## 2. 啟發與技術風險評估（為什麼不該照單全收「一次做出第一版」）

- **值得採納的規格設計**：
  1. **四區塊專業修圖版面＋操作細節**：上方工具列、左側工具欄、中間參數面板、右側畫布，加上游標中心縮放、空白鍵平移、可拖曳前後對比線、取消後還原原樣，是一份品質極佳的**前端互動設計驗收清單**。
  2. **資料不離機（Client-Side）與 ONNX/WebGPU 分層**：針對敏感圖片，純瀏覽器推理可以不經自家伺服器，省下推論伺服器成本。但用 WebGPU 不會自動禁止連網：前端程式、權重下載與遙測都要查，是否「不外洩」要靠離線測試與網路觀察驗證，不能靠架構名稱保證。
- **必須避開的四個實作陷阱**：
  1. **「一次做完 8 大工具＋影片三合一」極易誘發假實作（空殼充數）**：讓單一模型一回合生成這麼多複雜 AI 管線時，模型常會把真實 ONNX 推論簡化成 Canvas 模糊／色階濾鏡假裝「已消除／已放大」；若真要動工，必須嚴格拆成**垂直切片（Vertical Slice）**，每次只接通一個真實模型並驗證張量輸出。
  2. **多模型體積與 WebGPU OOM**：MI-GAN、U²-Net、Real-ESRGAN 與影片去背同時常駐顯存可能放不下（取決於模型版本、硬體與顯存，本筆記沒有實測數據），建議採「Web Worker 隔離執行 ＋ 按需懶載入 ＋ IndexedDB / OPFS 模型快取 ＋ 主動釋放 `InferenceSession`」。
  3. **瀏覽器影片處理＋保留音軌複雜度高**：MP4/WebM 解碼、逐格推論、Alpha 透明通道 WebM 編碼及音軌混流（需 `WebCodecs` + `mp4box.js` / `mediabunny` 或 `ffmpeg.wasm`），工程量遠大於單張修圖；在 **Windows 11 本機環境下**，長影片去水印與超解析交給本機 Python / GPU CLI 執行，預期比瀏覽器分頁穩定；速度差多少沒有 benchmark，未查證。
  4. **開源授權注意**：`lxulxu/WatermarkRemover` 採用 **GPL-3.0**。GPL [允許商業使用](https://www.gnu.org/licenses/gpl-faq.html)，限制在於重用或散布衍生程式碼時必須遵守 GPL（含公開原始碼）；所以不能把它的程式碼改寫後改掛 MIT 或放進閉源專案，參考流程思路則沒問題。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-07`**｜**[優先級：低]** 若未來需建置純前端隱私修圖工具，僅採「垂直切片」驗證單一 WebGPU ONNX 模型（如 U²-Net 去背）＋ Canvas 縮放／前後對比線最小可用原型（不照原文一口氣全包）
  - **狀態**：⚪ 不做（2026-11-15 獨立審查：原文自承未立項，目標 repo 存在性未查證，不是既有工具缺陷；保留知識與 skill-matting 遙測發現即可，目前不安裝該 skill，不以「未來若要」占用待辦）
  - **目標範圍**：未來若立項時新建 `C:\GitHub\browser-image-studio`（目前暫不建立空 repo）
  - **具體做法**：
    1. 先搭好「上方工具列＋左側欄＋右側 Canvas（游標中心縮放、空白鍵平移、拖曳對比線、Undo/Redo）」純前端骨架。
    2. 僅接通單一真實 ONNX 模型（例如透過 `onnxruntime-web` WebGPU/WASM 執行去背或超解析），實作 Web Worker 推論進度回報、取消中斷與 OPFS 快取，**嚴禁以 Canvas 濾鏡假冒 AI 推論**。
    3. 影片去背／去水印在 Windows 11 優先評估以本機 CLI／`ffmpeg` + `BiRefNet` 處理，不強塞進單頁瀏覽器。
  - **驗收標準（DoD）**：真實載入至少 1 支 `.onnx` 模型並輸出真實張量遮罩／放大畫素（非假濾鏡），完成前後對比線與透明 PNG 匯出測試。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待未來立項後填寫）*
