---
id: 2026-10-17-meta-sam-3-1-video-segmentation
title: "Meta SAM 3.1 視覺分割模型解析：從點選框選到文字提示、32 FPS 串流追蹤與 Agent 雙階段打碼流水線"
source_url: "https://github.com/facebookresearch/sam3"
source_platform: "Web & Meta AI Research"
author: "Meta AI / 凱文大叔 (SubTutor)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: archived
cluster: "4"
cluster_role: "學術論文閱讀與視覺分割"
short_title: "Meta SAM 3.1 視訊分割"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "「凱文大叔（SubTutor）」的社群內容沒留連結、找不到，那邊的圖與留言沒看到（總數未知）；改看 repo README 4 張圖與 7 則 issue"
source_images: 4
source_replies: 7
tags:
  - computer-vision
  - meta-sam
  - video-segmentation
  - specialized-models
  - privacy-blur
  - multimodal-agent
---

# Meta SAM 3.1 視覺分割模型解析：從點選框選到文字提示、32 FPS 串流追蹤與 Agent 雙階段打碼流水線

- **來源連結**：[Meta Segment Anything (GitHub)](https://github.com/facebookresearch/sam3) / [Meta AI Demos](https://aidemos.meta.com/segment-anything/)
- **發表作者**：`Meta AI` / `凱文大叔 (SubTutor 整合案例)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`⚪ 已封存 (Archived)`

---

## 0. 原始資料盤點

> 2026-11-16 重審：看了 `facebookresearch/sam3` 的 README、SAM 3.1 發布說明、README 的 4 張圖，以及留言最多的 7 則 issue。筆記提到的「凱文大叔（SubTutor）」那則社群內容沒有留下連結，找不到原文，那邊的圖與留言沒看到。

- **作者圖片**（README）：
  - 圖 1 架構圖：文字提示（例「a penguin」）走 Text Encoder、影格走 Image Encoder，一起送進 **Detector**（SAM 3 新增）找出當前影格的遮罩；**Tracker**（沿用 SAM 2）把上一格的遮罩傳下來，也接受遮罩／點／框提示與範例框（exemplar）；兩邊結果合併後輸出並寫回 Memory Bank。兩個編碼器來自 PE（Perception Encoder）。
  - 圖 2 動畫：草地上幾隻狗奔跑的影片分割示範。
  - 圖 3 動畫：足球員的影片追蹤示範。
  - 圖 4 SA-Co 資料集拼圖：街景、水果攤、貓、車等畫面配上名詞片語標註（例「白色車牌」「藍色籃子」）；紅字是畫面裡**不存在**的片語（負樣本），用來訓練模型判斷「沒有這東西」。
- **作者留言補充**（README 與發布說明）：
  - 模型參數量是 **848M**；偵測器與追蹤器共用一個視覺編碼器。
  - SAM 3.1 於 2026-03-27 發布，重點是 Object Multiplex（共用記憶的多物件聯合追蹤）；發布說明寫「128 個物件時在單張 H100 上約 7 倍加速」。
  - 環境要求 Python 3.12 以上；授權是 Meta 自訂的 **SAM License**，不是 MIT／Apache。
  - SAM 3 Agent 有官方範例 notebook（`examples/sam3_agent.ipynb`）。
- **網友留言重點**（issue）：
  - #224（35 則留言，未結）：要求官方提供 ONNX 匯出與 TensorRT 轉換腳本——目前**沒有官方 ONNX 版**。
  - #408（未結）：問有沒有串流版；可見即時串流不是現成功能。
  - #163、#330：自訂資料集微調的格式與分割微調支援，問的人多、仍未結。
  - #317（71 則留言）：想把一張圖的框選概念轉到另一張圖做少樣本分割。
  - #507、#289：推論時 dtype 不一致、訓練時數值錯誤等執行問題。
- **對分析的影響**：
  - 參數量改成 848M（原寫 850M 是約數）。
  - 「16 FPS 翻倍到 32 FPS」在 repo 的 README 與 3.1 發布說明裡都找不到，那裡只寫 7 倍加速；32 FPS 可能出自 Meta 部落格或轉述者，已在 1.2 節標明未在 repo 查到。
  - 第 2 節「可考慮量化版 ONNX 模型」與現況不符（#224），已改寫。
  - 補上授權是 SAM License、要 Python 3.12。兩個任務本來就是「不做」，這些限制讓理由更充分，狀態不變。

---

## 1. 核心內容摘要與技術深挖

### 1.1 專用模型（Specialized Model）的崛起：不聊天，專精像素分割
隨著業界對「對話式通用大模型（LLM）」邊界的認識加深，像 TypeSafe Jev、Meta SAM 這類「不具備通用聊天功能，但在單一垂直領域極致精準、快速」的**專用神經網路模型**正迎來爆發：
- **SAM 的本質**：848M 參數（README 數字）的端到端視覺分割模型（Vision Segmentation Model），其目標不是生成文字或繪製插圖，而是對輸入之圖片或連續視訊影格，依照指定目標**逐像素輸出高精度的二值遮罩（Binary Pixel Mask）**。
- **應用場景**：影片後製中的綠幕去背（Rotoscoping）、敏感資訊自動遮蔽（人臉、車牌打馬賽克）、物體顏色替換與局部光影重構。

### 1.2 SAM 世代演進與 3.1 突破
Meta 團隊在視覺分割領域持續迭代，演進路徑清晰：

1. **SAM 1 (2023)**：開創點選（Point）與框選（Bounding Box）的互動式分割（Promptable Segmentation），僅限單張靜態影像，一次僅能處理一個物件。
2. **SAM 2 (2024)**：引入串流記憶注意力機制（Streaming Memory Attention），具備跨影格追蹤（Video Tracking）能力，但仍高度依賴首幀的手動框選提示。
3. **SAM 3 (2025 年 11 月)**：突破性原生支援**文字提示（Open-vocabulary Text Prompting）**。輸入短語（如 `"car license plate"`、`"red umbrella"`），即可一次自動找出畫面中所有相符物件，並自動沿時間軸追蹤。
4. **SAM 3.1 (2026 年 3 月 27 日)**：核心優化**多物件複用批次追蹤（Object Multiplexing & Shared Memory）**。官方發布說明寫的是：128 個物件時，在單張 NVIDIA H100 上比 2025 年 11 月版約快 **7 倍**。「16 FPS 翻倍至 32 FPS」這組數字在 repo 的 README 與發布說明裡查不到，出處未查證。

### 1.3 語意邊界與「SAM 3 Agent」雙階段流水線
SAM 3.1 本身不是具備多跳邏輯推理能力的 LLM，其自然語言理解存在明確邊界：
- **語言限制**：只接受**簡短的英文名詞片語（Short English Noun Phrases）**（如 `"human face"`、`"yellow handbag"`）。實測若輸入中文（如「人臉」），檢測結果為 0，而英文 `"human face"` 能精準抓取 226 個面孔。
- **邏輯推理限制**：無法理解長句或否定條件句（如「坐著、手上沒拿禮物的人」）。
- **官方解法（SAM 3 Agent）**：透過前置一個輕量多模態大模型（MLLM，如 Claude 3.5 Sonnet / GPT-4o / Qwen-VL）進行視覺理解與指令編排，將複雜需求拆解並翻譯成標準英文名詞，再委派給 SAM 3 進行像素級生成。

```text
┌────────────────────────────────────────────────────────────────────────┐
│             SAM 3.1 Agent 雙階段視覺隱私打碼流水線                     │
└────────────────────────────────────────────────────────────────────────┘

 [使用者自然語言指令] (例如：「把畫面裡坐著講電話的人、車牌都打馬賽克」)
         │
         ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 階段一：MLLM 意圖推理與名詞編排器 (Claude / GPT-4o / Qwen-VL)         │
 │ ├─ 1. 理解場景並進行因果推理 (識別講電話者、識別車輛牌照)             │
 │ ├─ 2. 跨語言翻譯與片語標準化：                                        │
 │ │    • 「坐著講電話的人」 ──▶ "person holding phone"                  │
 │ │    • 「車牌」          ──▶ "license plate"                         │
 │ └─ 3. 輸出結構化標籤清單                                              │
 └──────────────────────────────────┬────────────────────────────────────┘
                                    │ 標準英文片語
                                    ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 階段二：Meta SAM 3.1 視覺分割引擎 (850M Specialized Vision Model)     │
 │ ├─ 1. 影像特徵編碼 (Image/Video Encoder)                              │
 │ ├─ 2. 物件多路複用 (Object Multiplexing: 32 FPS 即時串流)             │
 │ ├─ 3. 逐影格遮罩記憶傳遞 (Memory Bank Tracking)                       │
 │ └─ 4. 輸出精準二值遮罩 (Binary Pixel Masks)                           │
 └──────────────────────────────────┬────────────────────────────────────┘
                                    │ Pixel Mask
                                    ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 階段三：視訊後製處理 (FFmpeg / OpenCV / SubTutor)                     │
 │ └─ 依據 Mask 自動套用高斯模糊 (Gaussian Blur) / 像素馬賽克 (Mosaic)    │
 └───────────────────────────────────────────────────────────────────────┘
```

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **串聯 `reelbird`（開源螢幕錄影）**：前篇調研的 Reelbird 主打自動錄影與 Agent 展示生成。結合 SAM 3.1，可為展示影片提供「全自動隱私去識別化（Auto PII Redaction）」，自動將錄製過程中出現的 API Keys、個人頭像、桌面隱私檔案名稱打上遮罩。
  - **串聯 `cinematic-shot` 與 `motion-prompt`**：SAM 3.1 提供精確輪廓 Mask 後，可配合 `motion-prompt` 的動態轉場特效（例如局部物件發光、流動外框），讓 Coding Agent 能自動產出具備好萊塢水準的宣傳短片。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **「專用小模型 + 通用大模型」的分層架構**：通用 LLM 負責聽懂人話、專用模型（SAM 3.1）負責幹重活（32 FPS 像素追蹤），此分工模式效率與性價比最高。
    2. **影片自動後製工具鏈**：凱文大叔的 SubTutor 證明了獨立開發者可透過整合 SAM 打造自動化影視工具。
  - **適用性界線**：
    - SAM 3.1 依賴 NVIDIA GPU（CUDA）進行高吞吐推論，環境要 Python 3.12 以上。沒有獨立顯卡時只能考慮雲端 API；官方目前沒有 ONNX／TensorRT 匯出（issue #224 未結），也沒有現成的串流版（issue #408）。
    - 授權是 Meta 自訂的 SAM License，不是 MIT／Apache，商用或再散布前要先讀條款。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261017-29`**｜**[優先級：低]** 調研 SAM 3 / 3.1 在 Windows 11 本地環境（NVIDIA CUDA）的推論與 CLI / Python API 封裝
  - **目標範圍**：`SanHsien/ai-inbox` 與視覺多媒體工具鏈
  - **狀態**：⚪ 不做（需要大量 GPU 與模型下載，與目前工作流（程式、文件、社群內容）無關）
  - **具體實作步驟**：
    1. 查閱 `facebookresearch/sam3` 官方權重、依賴需求（PyTorch, TorchVision, CUDA Toolkit）與開源授權條款。
    2. 評估在 Windows 11 本地環境下的載入方式（是否支援 ONNX Runtime / TensorRT 輕量部署）。
    3. 實測英文文字提示（如 `"human face"`, `"license plate"`）於單張靜態照片與 MP4 短影音的 Mask 生成品質與推論延遲。
  - **驗收標準（DoD）**：產出 Windows 11 本地部署指南與實測推論報告（含 FPS 與顯存佔用數據）。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261017-30`**｜**[優先級：低]** 設計「MLLM 語意拆解 + SAM 3.1 像素遮罩」多模態影片隱私自動打碼流水線（Auto-Blur Pipeline）
  - **目標範圍**：多媒體後製與隱私自動化工作流
  - **狀態**：⚪ 不做（同 T-20261017-29，依賴 SAM 本地推論，無實際影片打碼需求）
  - **具體實作步驟**：
    1. 設計前置 Prompt 範本：將使用者中文自然語言指令（含否定與複合條件）轉化為 SAM 3 支援之標準英文名詞片語陣列。
    2. 串接 OpenCV / FFmpeg：接收 SAM 3.1 輸出的逐影格 Mask，對目標區域自動套用高斯模糊或像素馬賽克。
    3. 評估與 `reelbird` 的整合點，探討錄影匯出後自動觸發隱私遮蔽腳本的可行性。
  - **驗收標準（DoD）**：產出端到端打碼概念驗證腳本與技術架構規格文檔。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---
