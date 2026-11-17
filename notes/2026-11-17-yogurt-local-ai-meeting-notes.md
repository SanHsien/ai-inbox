---
id: "2026-11-17-yogurt-local-ai-meeting-notes"
title: "Threads 情報評估：Yogurt（FrigadeHQ/yogurt）跨平台本地隱私 AI 會議筆記開源替代品"
source_url: "https://www.threads.com/@leeunhn/post/DfuX9KWmSN8"
source_platform: "Threads / GitHub"
author: "@leeunhn (李昀翰) / FrigadeHQ"
github_repo: "https://github.com/FrigadeHQ/yogurt"
analyzed_at: "2026-11-17"
analyzed_by: "antigravity"
source_review: full
source_images: 1
source_replies: 0
source_reviewed_at: "2026-11-17"
status: archived
cluster: 3
cluster_role: "本地會議筆記工具"
short_title: "Yogurt本地會議筆記"
tags:
  - yogurt
  - meeting-notes
  - whisper-cpp
  - llama-cpp
  - local-first
  - threads
---

# Threads 情報評估：Yogurt（FrigadeHQ/yogurt）跨平台本地隱私 AI 會議筆記開源替代品

- **來源貼文**：[Threads 原貼文（`@leeunhn` 李昀翰）](https://www.threads.com/@leeunhn/post/DfuX9KWmSN8)（原分享連結 `https://www.threads.com/share/_pFIgUjjc`）
- **官方 GitHub**：[`FrigadeHQ/yogurt`](https://github.com/FrigadeHQ/yogurt)（MIT License）
- **發布平台 / 作者**：`Threads` / `@leeunhn`（`2026-11-14`）
- **分析日期**：`2026-11-17`
- **當前狀態**：`⚪ 封存 (Archived)`

---

## 1. 原始資料盤點（主文、圖片與留言）

- **主貼文核心**：介紹 GitHub 開源專案 `FrigadeHQ/yogurt`（當時約 1,370 stars），定位為商業會議筆記工具 `Granola` 的免費開源替代品，主打會議錄音與重點整理全程留在本機完成、不上傳他人伺服器，並支援 Mac、Windows 與 Linux。
- **作者上傳圖片（共 1 張，GitHub 連結預覽 OG 卡片截圖）**：
  - 呈現深色桌面介面（`Launch planning`），左側欄包含 `Search`、`Meetings`、`Ask` 與資料夾分類；右側包含 `Transcript`、`My notes`、`Summary` 三分頁，以及 `Resume recording` 與 `Copy` 操作鈕，展現完整的會議逐字稿＋人工筆記＋AI 摘要工作區。
- **網友回應與作者回覆（共 0 則）**：貼文底下目前無任何留言或作者續樓補充（頁面下方僅為 Threads 推薦的「相關串文」）。
- **原始資料對分析的影響**：因貼文與留言未提供技術棧細節，經由主動查詢官方倉庫資訊補齊底層架構與 Windows 支援規格。

---

## 2. 官方技術架構核實與對現有系統評估

- **官方架構核實（`FrigadeHQ/yogurt`，MIT License）**：
  - **跨平台桌面殼**：基於 Electron 建置，支援 **Windows 10 (2004+) / Windows 11 x64**、macOS Apple Silicon 與 Linux AppImage。
  - **100% 本地轉錄**：Windows 與 Linux 透過 **`whisper.cpp`** 在本地執行語音轉文字（macOS 另支援 Apple 原生 SpeechAnalyzer）。
  - **100% 本地摘要與問答**：透過 **`llama.cpp`** 執行本地開源權重模型，產出會議摘要（`Summary`）、行動項與會議內容問答（`Ask`）。
- **對現有系統的評估**：
  - 本機 `ai-inbox` 已具備 `tools/video_transcript.py`（CUDA Whisper 音訊轉錄管線）處理媒體內容，且目前日常工作流並無即時線上會議錄音與整理工具的急迫缺口。
  - 若未來有離線會議記錄需求（且不希望音訊上傳雲端），`FrigadeHQ/yogurt` 採用 MIT 授權與標準 `whisper.cpp` + `llama.cpp` 方案，無需自建輪子，可直接取用或作為 Electron 本地 AI 音訊架構參考。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬現成開源桌面應用，目前無整合進本機多 Agent 開發工作流之必要；留存完整技術盤點與授權資訊作為日後本地會議筆記需求之備選方案即可。
