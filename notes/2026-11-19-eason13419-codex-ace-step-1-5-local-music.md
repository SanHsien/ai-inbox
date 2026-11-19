---
id: "2026-11-19-eason13419-codex-ace-step-1-5-local-music"
title: "Threads 案例與留言評估：用 Codex 驅動開源 ACE-Step 1.5 + ffmpeg 本地免費生成 AI 音樂"
source_url: "https://www.threads.com/@eason13419/post/Dft5nWUoBML"
source_platform: "Threads / YouTube / GitHub"
author: "@eason13419 (伊森說) / ACE-Step"
github_repo: "https://github.com/ace-step/ACE-Step-1.5"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: partial
source_images: 8
source_replies: 24
source_reviewed_at: "2026-11-19"
source_review_note: "主貼文、8張輪播教學圖與作者1則續樓完整讀取；55則留言於未登入狀態讀到24則（含1則作者續樓、21則頂層留言與2則子回覆），其餘受Threads登入牆阻擋"
status: archived
cluster: 3
cluster_role: "本地AI音樂工具"
short_title: "ACE-Step1.5本地音樂"
tags:
  - ace-step
  - music-generation
  - codex
  - ffmpeg
  - local-ai
  - threads
---

# Threads 案例與留言評估：用 Codex 驅動開源 ACE-Step 1.5 + ffmpeg 本地免費生成 AI 音樂

- **來源貼文**：[Threads 原貼文（`@eason13419` 伊森說）](https://www.threads.com/@eason13419/post/Dft5nWUoBML)（原分享連結 `https://www.threads.com/share/BAkxqNtcP_`）
- **作者延伸教學**：[YouTube 教學影片](https://youtu.be/tB4ZzrDFJ1M)
- **官方 GitHub**：[`ace-step/ACE-Step-1.5`](https://github.com/ace-step/ACE-Step-1.5)（MIT License）
- **發布平台 / 作者**：`Threads` / `@eason13419`（`2026-11-14`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-31-voicestudio-local-ai-voice-cloning-skill-pipeline.md`](./2026-10-31-voicestudio-local-ai-voice-cloning-skill-pipeline.md)（本地開源音訊與語音克隆管線）

---

## 1. 原始資料盤點（主文、8 張教學圖卡、續樓與 24 則可見留言）

- **主貼文與 8 張輪播圖卡（共 8 張，已逐張檢視）**：
  - 核心做法為「**Codex 當施工員＋ACE-Step 1.5 當音樂引擎**」：請 ChatGPT Codex（或 Claude）在專案目錄自動檢查環境、安裝 `ACE-Step 1.5` 與 `ffmpeg`，再用自然語言給定歌詞（或標註「純音樂」）、曲風、男/女聲音色、氣氛、BPM 與長度（最長 10 分鐘，MP3/WAV），由 Codex 呼叫本地腳本產出音檔。
  - 圖卡 03 明確釐清費用邊界：`ACE-Step 1.5` 程式與模型皆為 **MIT 授權免費本地執行**，但驅動它的 Coding Agent（ChatGPT / Claude）仍可能需要訂閱。
- **作者續樓（1 則）**：附上 YouTube 操作示範影片 `https://youtu.be/tB4ZzrDFJ1M`。
- **網友回應與實測回饋（55 則中讀到 24 則，其餘受登入牆阻擋）**：
  - **`@matzumatzu520` 釐清角色**：指出 ChatGPT 只是協助操作與下指令，實際生成音樂的是本地 `ACE-Step`。
  - **`@cheapfly` & `@llllllllllviiiiiiiiii` 實測品質反駁**：實測指出 `ACE-Step` 強在免費開源，但**部分人聲發音仍不夠自然**；若論人聲歌曲品質與易用性，付費雲端 `Suno` 仍明顯較佳。
  - 其餘留言多為「留／存」書籤與垃圾廣告投票（`lingwen833` 留 LINE ID），另有部分子回覆被登入牆隱藏。
- **官方 GitHub 核實（`ace-step/ACE-Step-1.5`）**：
  - 採混合架構（Language Model planner + Diffusion Transformer），內建 Gradio Web UI（`uv run acestep` / `start_gradio_ui.bat`）、REST API、CLI 與 LoRA 訓練腳本；另有 C++ / `acestep.vst3`（DAW 外掛）與 `ACE-Step-ComfyUI`。
  - **Windows 顯存分級支援**：`<4–6 GB VRAM` 可跑純 DiT（CPU offload + INT8）；`6–8 GB` 跑 `0.6B LM`；`8–16 GB` 跑預設 `1.7B LM`；`24+ GB` 全駐顯存。

---

## 2. 對現有系統的啟發與落差評估

- **可借鏡的非工程化操作範式**：
  - 「用 Coding Agent（Codex / Claude）代勞本地複雜開源工具安裝、依賴排錯與 CLI 包裝」是極佳的免手寫指令模式（實務上執行安裝前仍應先檢閱倉庫與依賴清單，遵守零信任原則）。
- **本機定位評估**：
  - 結合留言實測與官方規格，`ACE-Step 1.5` 最具價值的場景是**「純音樂／教學影片 BGM／Podcast 開場配樂」**（避開人聲咬字瑕疵，同時取得 MIT 免費商用與 100% 本地無版權風險優勢）；人聲歌曲則仍以雲端 `Suno` 品質較高。
  - 本機目前無立即性的影片自動化配樂生產任務，且下載數 GB Hugging Face 音樂模型權重非當前所需；待未來影音管線需生成無版權 BGM 時，可直接依官方 `uv` 流程於沙盒啟用測試。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬現成 MIT 開源本地音樂模型工具與入門操作教學，目前本機工作流無即時音樂生成缺口；歸檔留存官方倉庫、Windows VRAM 分級與網友實測優缺點（純音樂 BGM 佳、人聲不如 Suno）備查即可。
