---
id: "2026-11-19-eason13419-codex-ace-step-1-5-local-music"
title: "Threads 案例與留言評估：用 Codex 驅動開源 ACE-Step 1.5 + ffmpeg 本地免費生成 AI 音樂"
source_url: "https://www.threads.com/@eason13419/post/Dft5nWUoBML"
source_platform: "Threads / YouTube / GitHub"
author: "@eason13419 (伊森說) / ACE-Step"
github_repo: "https://github.com/ace-step/ACE-Step-1.5"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 8
source_replies: 24
source_reviewed_at: "2026-11-20"
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

## 1. 原始資料盤點（主文、8 張教學圖卡、續樓、教學影片逐字稿與 24 則留言）

- **主貼文與 8 張輪播圖卡（共 8 張，已逐張檢視）**：
  - 核心做法為「**Codex 當施工員＋ACE-Step 1.5 當音樂引擎**」：請 ChatGPT Codex（或 Claude）在專案目錄自動檢查環境、安裝 `ACE-Step 1.5` 與 `ffmpeg`，再用自然語言給定歌詞（或標註「純音樂」）、曲風、男/女聲音色、氣氛、BPM 與長度（最長 10 分鐘，MP3/WAV），由 Codex 呼叫本地腳本產出音檔。
  - 圖卡 03 明確釐清費用邊界：`ACE-Step 1.5` 程式與模型皆為 **MIT 授權免費本地執行**，但驅動它的 Coding Agent（ChatGPT / Claude）仍可能需要訂閱。
- **作者續樓（1 則）**：附上 YouTube 操作示範影片 `https://youtu.be/tB4ZzrDFJ1M`。
- **教學影片逐字稿（2026-11-20 補讀，片長 524 秒，YouTube 自動字幕）**：
  - 流程只有三步：ChatGPT 桌面版切到 Codex 模式並建立專案資料夾 → 請 Codex 安裝 ACE-Step 1.5 與 ffmpeg（作者還加一句「相關套件也一併安裝」）→ 把歌詞與需求交給 Codex 產生音檔。
  - 全片沒有提顯示卡、顯存需求、模型下載大小與生成耗時，也沒有展示安裝過程的畫面；示範的是一首約 2 分鐘的華語歌。
  - 「像真人在唱歌」是作者自己聽完的主觀評語，沒有對照組；與留言的實測評價相反（見下）。
- **網友回應與實測回饋（2026-11-20 登入後補讀；貼文計數 55 則，平台顯示 24 則已全部讀完，差 31 則登入後也不顯示）**：
  - 熱門、最新兩種排序都捲到底，內容相同：1 則作者續樓、21 則頂層留言、2 則子回覆。多則留言旁的回覆計數（1～4）點進單則頁面顯示「尚無回覆」，是平台不顯示的回覆，不是沒讀到。
  - **`@matzumatzu520` 釐清角色**：指出 ChatGPT 只是協助操作與下指令，實際生成音樂的是本地 `ACE-Step`。
  - **`@cheapfly`、`@llllllllllviiiiiiiiii` 實測品質反駁**：前者用過後認為有些發音不夠好，強項只在免費，花小錢用 `Suno` 就夠玩；後者是**自己訓練過之後**仍覺得 `Suno` 好用很多，但後來補一句「畢竟免費，參數給得夠或許還有用武之地」。`@ceris20` 回覆說看了這個實測就不試了。
  - **`@laputacapron`**：認為 Gemini 早就能做音樂，這個做法不算新。
  - 其餘 17 則是「留／存」書籤、按讚與道謝，沒有技術資訊；沒有人回報安裝成功或失敗的細節。貼文另有 9 則引用，側欄顯示的 3 則都是感想，無新資訊。
- **官方 GitHub 核實（`ace-step/ACE-Step-1.5`，2026-11-20 重讀 README）**：
  - 採混合架構（Language Model planner + Diffusion Transformer），內建 Gradio Web UI（`uv run acestep` / `start_gradio_ui.bat`）、REST API、CLI 與 LoRA 訓練；長度支援 10 秒到 10 分鐘；另有 C++ / [`acestep.vst3`](https://github.com/ace-step/acestep.vst3)（DAW 外掛）與 [`ACE-Step-ComfyUI`](https://github.com/ace-step/ACE-Step-ComfyUI)。
  - **顯存分級（README 表格，2026-11-20 改正，原稿寫得不準）**：`≤6 GB` 只跑 DiT、不開 LM（INT8 量化＋完全 CPU offload）；`6–8 GB` 用 `0.6B` LM；`8–16 GB` 中 8–12 GB 用 `0.6B`、12–16 GB 才用 `1.7B`；`16–20 GB` 用 `1.7B`，XL 模型需 offload；`20–24 GB` XL 可全駐顯存；`≥24 GB` 用 XL 加 `4B` LM。XL（4B DiT，2026-04 釋出）至少要 12 GB。
  - **README 自己列了版權風險**：授權是 MIT，但免責段明講可能因風格相似而非故意侵權，請使用者自行確認原創性並揭露 AI 參與。原稿寫「100% 本地無版權風險」不成立，已改正（見第 2 節）。
- **原始資料對分析的影響**：登入後確認沒有被隱藏的實測或反駁，結論不變；改正了顯存分級與「無版權風險」兩處事實，並補上影片沒有交代硬體門檻這一點。

---

## 2. 對現有系統的啟發與落差評估

- **可借鏡的非工程化操作範式**：
  - 「用 Coding Agent（Codex / Claude）代勞本地複雜開源工具安裝、依賴排錯與 CLI 包裝」是極佳的免手寫指令模式（實務上執行安裝前仍應先檢閱倉庫與依賴清單，遵守零信任原則）。
- **本機定位評估**：
  - 結合留言實測與官方規格，`ACE-Step 1.5` 最具價值的場景是**「純音樂／教學影片 BGM／Podcast 開場配樂」**（避開人聲咬字瑕疵；程式與模型是 MIT 授權、可本地執行，但 README 免責段提醒生成結果仍可能因風格相似而侵權，商用前要自行確認）；人聲歌曲則仍以雲端 `Suno` 品質較高。
  - 本機目前無立即性的影片自動化配樂生產任務，且下載數 GB Hugging Face 音樂模型權重非當前所需；待未來影音管線需生成無版權 BGM 時，可直接依官方 `uv` 流程於沙盒啟用測試。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬現成 MIT 開源本地音樂模型工具與入門操作教學，目前本機工作流無即時音樂生成缺口；歸檔留存官方倉庫、Windows VRAM 分級與網友實測優缺點（純音樂 BGM 佳、人聲不如 Suno）備查即可。
