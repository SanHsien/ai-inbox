---
id: "2026-11-26-aiarttw-birdchord-v1-suno-workflow"
title: "鳥和弦 v1 簡化版旋律生成 App 與 Suno 結構化提示詞工作流評估"
source_url: "https://c.aiarttw.com/"
source_platform: "Web App / Suno"
author: "aiarttw (@elitebandpassfilters458 / Jonas’s)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
status: archived
cluster: 3
cluster_role: "和弦旋律與Suno範本"
short_title: "鳥和弦v1與Suno工作流"
tags:
  - suno
  - music-generation
  - chord-progression
  - midi
  - prompt-engineering
  - web-audio
---

# 鳥和弦 v1 簡化版旋律生成 App 與 Suno 結構化提示詞工作流評估

- **線上工具**：[鳥和弦v1 · 樂段創作](https://c.aiarttw.com/)（頁面內標示關聯站 `https://sd.aiarttw.com/site/`；Synth Studio 標註 `MP4 元件授權 Aurora © 2026 pixbvr · MIT`）
- **Suno 成品範例**：[借來的潮.莎莎（`@elitebandpassfilters458` / Jonas’s）](https://suno.com/s/IwDCoYl8OQOfU0ET)（轉址至 `https://suno.com/song/20c7eb5b-ecf1-44df-85d7-a33e20f0352f?sh=IwDCoYl8OQOfU0ET`）

---

## 核心結論

這組分享表面是免費 Web 旋律產生器，真正值得參考的技術模式是 **「前置確定性和弦／旋律草稿（Audio/MIDI）+ 結構化 Suno 智能體提示詞」**：先在瀏覽器端透過本地樂理引擎產生 8～32 小節的 WAV / MIDI 草稿，再將音檔上傳 Suno 並搭配指定 BPM、調性、人聲音域與四階段 `STYLE FLOW` 的提示詞，藉此解決純文字生成音樂常發生的旋律漂移與結構鬆散問題。因屬純參考性質的外部創作工具，歸檔備查，不另開實作任務。

---

## 一、鳥和弦 v1（`c.aiarttw.com`）實測機能

全站採 10 個步驟分頁與 20 個直達選單（支援 14 種 UI 主題切換，無須 API Key 即可靠本地樂理演算法運作，亦提供選配 OpenAI / OpenRouter API 設定）：

1. **主題與樂理生成（`01 主題核心` / `02 和弦組`）**：內建 20 大類共 2,040 種題材與 120 種曲風，可設定調性（C–B）、音階（大調／小調／五聲音階）、拍號與小節數，單次生成 10 組 8 小節和弦與旋律變化（如故事敘事、副歌爆發、Hook 記憶、極簡留白等），並可在 Piano Roll 進行量化（`1/16`、`1/8`、`1/4`、三連音）與延伸至 32 小節。
2. **合成編曲與多輸入模態（`03 合成編曲`、`06`–`09`）**：
   - `03 合成編曲`：內建 Aurora 合成器（100 種 Synth 預設、4-operator FM 合成、19 種取樣樂器如 Splendid Grand Piano / CP80 / Wurlitzer EP200 / VCSL 弦管樂 / Smolken 低音提琴）與最多 8 軌多軌編輯，作品存於瀏覽器本地儲存。
   - `06 名曲和弦`（2,500 筆和聲進行）、`07 潮旋律`（故事轉旋律）、`08 畫畫樂`（畫布筆刷轉旋律）、`09 哼哼哈兮`（麥克風錄音或音檔上傳 30 秒內轉 MIDI／和弦）。
3. **Suno 提示詞與藍圖輸出（`04 歌曲藍圖` / `05 Suno智能體`）**：
   - `05 Suno智能體`（文中提及的「推薦樂風」對應此分頁；頁面未見 `v6` 字樣，標籤為 `Suno智能體`）整合 400 種曲風與 2,000 筆音樂人風格參考，支援 12 種曲式結構預設、可拖曳 Meta-tags 總綱（如 `[Intro][Pre-Chorus][Chorus][Final Chorus Variations: +semitone][Outro]`）、以及四階段動態行進 `STYLE FLOW`（`Start with...` → `Transition to...` → `Switch the beat to...` → `Finally into...`）。
4. **匯出格式**：支援下載 `.wav`、`.mp4`、`.mid`（MIDI）、`.txt`（和弦譜）、`.json`（作品備份），以及一鍵複製結構化文字提示詞（顯示字元計數，如 `2,082 / 3,000 字元`）。

---

## 二、Suno 範例曲（`借來的潮.莎莎`）提示詞結構解析

- **基本資訊**：長度 `2:31`，模式為 `CUSTOM`（2026-09-16 建立，頁面未顯示模型版本標籤；瀏覽時顯示 40 次播放、3 個讚）。
- **關鍵 Style Prompt 拆解**：
  > `Afropop dark alt-pop love song, intimate smoky late-night warmth, 128 BPM, 4/4, E-flat major, muted electric guitar with long sea-like reverb, acoustic guitar, hand percussion, syncopated upright bass, warm Rhodes electric piano, bright restrained synthesizer, subtle vinyl crackle, cinematic scene progression from summer beach memory to betrayal and clarity, verses rhythmically conversational in G3–B4, pre-chorus strips to vinyl noise and breath, chorus has a distinctly wider ascending melody reaching D5 with stacked harmonies and a final lifted reprise, keep the attached lead melody recognizable while replacing the chiptune texture with organic instruments`
- **技術重點**：
  1. **明確約束樂理座標**：直接鎖定 `128 BPM, 4/4, E-flat major`，並為 Verse（`G3–B4`）與 Chorus（上行至 `D5` + 和聲堆疊）設定具體音域與張力差。
  2. **動態配器減法**：明確指定 Pre-Chorus 抽離樂器至黑膠底噪與呼吸聲（`strips to vinyl noise and breath`），製造副歌爆發對比。
  3. **音訊草稿覆蓋指令**：結尾句 `keep the attached lead melody recognizable while replacing the chiptune texture with organic instruments` 是「上傳 MIDI/合成器 WAV 草稿讓 Suno 重新編曲成真實樂器」的標準寫法。

---

## 三、評估與歸檔結論

- **與既有筆記關聯**：與 [ACE-Step 1.5 本地免費生成 AI 音樂](2026-11-19-eason13419-codex-ace-step-1-5-local-music.md) 同屬 AI 音樂生成流程（`cluster: 3`），一個偏本地開源模型與 Codex 自動化管線，本篇偏瀏覽器端零門檻樂理草稿 + Suno 長提示詞工程。
- **任務評估**：外部創作輔助工具，無須為本機開發環境新增任務；保留關鍵 Prompt 寫法與匯出規格供日後音訊實驗參考，狀態設為 `archived`。
