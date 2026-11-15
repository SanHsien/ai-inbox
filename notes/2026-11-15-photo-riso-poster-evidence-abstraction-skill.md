---
id: "2026-11-15-photo-riso-poster-evidence-abstraction-skill"
title: "luckdvr/photo-riso-poster：證據導向抽象與 2–3 色 Riso 印刷風海報 Skill 查證評估"
source_url: "https://github.com/luckdvr/photo-riso-poster"
source_platform: "GitHub / Social"
author: "luckdvr"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 2
cluster_role: "證據導向視覺Skill"
short_title: "PhotoRisoPoster海報Skill"
tags:
  - skill
  - risograph
  - visual-abstraction
  - prompt-engineering
  - image-generation
  - codex
---

# luckdvr/photo-riso-poster：證據導向抽象與 2–3 色 Riso 印刷風海報 Skill 查證評估

- **來源連結**：[luckdvr/photo-riso-poster](https://github.com/luckdvr/photo-riso-poster)
- **發布平台 / 作者**：`GitHub` / `luckdvr`（MIT License，60 Stars / 2 Forks，建立於 `2026-08-03`）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

> **安全審查與實查結果**：
> 已唯讀檢視 GitHub repo 檔案樹、[README.md](https://raw.githubusercontent.com/luckdvr/photo-riso-poster/main/README.md) 與 [SKILL.md](https://raw.githubusercontent.com/luckdvr/photo-riso-poster/main/SKILL.md)（共 73 行）。本專案為**純 Markdown 單檔規則（零腳本、零 Hook、零 MCP、零外部執行依賴）**，無遠端命令執行或越權風險，已通過靜態安全檢視。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：GitHub 開發者 `luckdvr`，靈感取自 `LiamGvchi/gc-minimal-zine-poster`（極簡 Zine 排版語法）與 `Evianis/travel-photo-abstraction`（證據優先的照片抽象方法），未夾帶兩者原始碼或圖檔。
- **What（核心產出 / 做了什麼）**：
  - 提供單一 `SKILL.md` 提示詞規格，將「照片」或「純文字主題」轉換為 2–3 色套印、帶紙張纖維與錯位油墨感（Misregistration）的 Risograph 孔版印刷檔案海報。
- **Why（為解決什麼問題 / 痛點）**：
  - 直接把照片交給生圖模型做「Riso 風格化（img2img）」，往往只是套上一層廉價數位濾鏡，保留過多雜亂背景、失去版畫節奏與留白呼吸感。
- **How（核心架構與關鍵機制）**：
  1. **Text-Only 嚴格隔離生圖（不附原圖）**：`SKILL.md` 強制規定**絕不把原照片或參考圖附給生圖工具**；必須先由主模型視覺讀取照片，記錄「主體／次要物件數量、正規化位置、比例、遮擋、方向、主軸、大面積色溫、2–3 個主色角色」與可選 EXIF 日期，再透過純文字 4 段式 Prompt（畫布紙色／油墨層與群聚／排印系統／氛圍與禁用清單）送交生圖工具。
  2. **三檔抽象度與自然語言局部微調**：支援 `faithful`（具象版畫細節）、`standard`（預設簡化剪影，人物與動物匿名化去五官）與 `minimal`（純幾何點／線／色塊，只保留數量與節奏），並允許用口語要求局部高辨識度（如「狗要像本狗」）。
  3. **紙色冷暖跟隨與 65–85% 留白幾何**：冷色照片配青灰瓷白／冷雪白紙，暖色照片配淺米白紙；強制 `65–85%` 空紙留白、單一偏心視覺群聚佔 `10–25%`（禁止滿版風景與網格對齊）。
  4. **排印文字即證據**：禁止純裝飾文字，標記直接承載觀察結果（如數量 `x 007` / `x 024 TRUNKS`、固定詞彙 `ARCHIVE NNN` / `NO. NNN`、氣候／季節短行、2–4 行英文短詩）。
- **When & Where（適用時機與場景）**：個人作品集、展覽／活動海報、攝影紀實視覺檔案，以及任何具備「讀圖＋生圖」能力的代理或對話介面（Codex、ChatGPT、Gemini、Antigravity `image-generator`）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/agent-assets`（跨平台共用 Skill 庫）、Antigravity 內建 `image-generator` subagent，以及 `C:\GitHub\ai-inbox` 視覺／設計類範本群組（Cluster 2）。
- **值得採納的核心設計方法（可跨 Skill 複用）**：
  - **「先視覺解構為結構化事實，再純文字重建」的兩階段管線**：刻意切斷 `img2img` 像素依賴，強迫模型把構圖不變量（數量、遮擋、不對稱間距、色溫角色）顯式寫進文字再生成，是防止 AI 視覺產出淪為「廉價濾鏡」的高性價比技巧。
  - **負向約束與自我複檢閉環**：明確列出 `Avoid` 清單（禁止滿版地面／天空、UI 純白、電影打光、3D、霓虹），並要求輸出後檢查「群聚是否過大、字詞是否拼錯、油墨是否過淡」，不達標則強化失敗規則重生成一次。
- **平台適配限制與注意事項**：
  - 原 repo 針對 Codex 內建生圖工具與 `$photo-riso-poster` 語法撰寫，且範例依賴多模態視覺讀圖與高品質文字渲染生圖模型；在 Antigravity 執行時需將「內建生圖工具」對應至 `image-generator` subagent，在無 EXIF 讀取工具（如純網頁端或未開 PIL/exiftool）時依規則自動略過日期行，不可偽造日期。
  - 若納入本機共用 Skill，僅取已審核之純文字 `SKILL.md`（無須下載 `examples/` 內約 17MB 圖檔）。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-14`**｜**[優先級：低]** 視需求將 `photo-riso-poster`（精簡純 `SKILL.md`）收錄至 `SanHsien/agent-assets` 並以 Antigravity `image-generator` 實測 1 組照片／文字主題海報
  - **目標範圍**：`C:\GitHub\agent-assets\skills\`（或個人本地 `~/.gemini/config/skills/`）
  - **具體做法**：
    1. 僅引入已通過審查的 `SKILL.md`（不拉取 17MB `examples/` 圖庫），補充 Antigravity 環境註記（對應 `image-generator` subagent 與 EXIF 可選規則）。
    2. 實測 1 組純文字主題與 1 組照片輸入（`standard` 與 `minimal` 各測一次），確認 `65–85%` 留白與英文短詞拼字穩定度。
  - **驗收標準（DoD）**：成功於本機透過 `image-generator` 產出符合 2–3 色 Riso 留白與證據排印規則的海報樣張，並確認無額外安全風險或上下文過載。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
