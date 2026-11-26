---
id: "2026-11-26-vvsvs-cinematique-prompt-library"
title: "Cinematique（VVSVS）150 種免費 AI 電影攝影提示詞資料庫與電腦王阿達報導評估"
source_url: "https://vvsvs.pro/cinematique"
source_platform: "Web / 電腦王阿達"
author: "Ivan Flugelman (VVSVS™) / Rocky (電腦王阿達)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
status: archived
cluster: 2
cluster_role: "電影攝影Prompt詞庫"
short_title: "Cinematique電影提示詞庫"
tags:
  - ai-video
  - image-generation
  - cinematography
  - prompt-engineering
  - grok
  - kocpc
---

# Cinematique（VVSVS）150 種免費 AI 電影攝影提示詞資料庫與電腦王阿達報導評估

- **工具主站**：[Cinematique by VVSVS](https://vvsvs.pro/cinematique)（作者：Ivan Flugelman — VVSVS™）
- **來源報導**：[電腦王阿達：Cinematique 免費 AI 電影提示詞資料庫，150+ 種鏡頭、燈光與構圖 Prompt 直接複製使用](https://www.kocpc.com.tw/archives/668865)（作者：Rocky，2026-09-14，頁內無讀者留言）

---

## 核心結論

`Cinematique` 是定位明確的 **AI 影像／影片攝影語言字典**，精確收錄 **150 項** 電影拍攝技巧（7 大分類、3 級難度、8 種情緒標籤），每筆皆含 `.webp` 圖示或循環 `.mp4` 動圖對照、使用時機、AI 導向建議、常見錯誤與預留 `[Subject]` 的英文 Prompt 範本。實機查證發現網站原圖／影片皆由 `Grok Imagine` 生成，基底改編自 Tetsuo Corp 的 `grokfilm.app`；雖然頁內宣稱 Open Source，但未公開 GitHub Repo、API 或 JSON 匯出（離線版為付費 `$29` Ebook）。適合當作 AI 視覺創作的 Prompt 詞庫參考，無須為此開啟本機開發任務，歸檔備查。

---

## 一、結構與資料盤點（實機檢視 `vvsvs.pro/cinematique`）

1. **總量與分類統計（共 150 項）**：
   - `Camera Work`（41）、`Lighting`（30）、`Composition`（21）、`Genres & Styles`（21）、`Editing`（17）、`Storytelling`（12）、`Visual Effects & Promptable FX`（8）。
   - **篩選維度**：關鍵字搜尋、3 級難度（`Basic` / `Intermediate` / `Advanced`）、8 種情緒（`Cinematic`、`Dramatic`、`Artistic`、`Horror`、`Action`、`Romantic`、`Documentary`、`Nostalgic`）。
2. **單筆條目內容結構**（以實測 `Aerial Shot`、`Close-Up`、`Three-Point Lighting` 為例）：
   - 條目視窗提供 `When to Use`、`Best Practices`（3 點）、`Prompt Template`（一鍵複製，統一預留 `[Subject]` 佔位符），獨立全頁指南（`/cinematique/<slug>`）另附 `Directing the AI`、`Common mistakes`（01–03）與 StudioBinder 參考連結。
   - **Prompt 寫法特徵**：結合「景別／機位＋時間與光比＋具體攝影機與鏡頭型號＋底片色調科學」，例如：
     - *Aerial Shot*：`...ARRI Alexa 65 with Hasselblad glass, 8K resolution, Kodak Vision3 250D color science, subtle atmospheric haze...`
     - *Close-Up*：`...shallow depth of field with background dissolving into creamy bokeh, warm sidelight from a single source, shot on Cooke S4 75mm at T2, Kodak Vision3 500T color science`
     - *Three-Point Lighting*：`...key light at 45 degrees... soft fill light... warm-toned backlight rimming the edges... shot on medium format with an 80mm portrait lens at f/2.8, Kodak Portra color science...`

---

## 二、報導漏載事實與使用邊界

- **源頭與商業模式（報導未提及）**：頁面頂部明確標註 `All images and videos generated with Grok Imagine — Built on grokfilm.app by Tetsuo Corp — remixed & expanded by VVSVS`；站內同時穿插 `$29` `Cinematique Ebook`（387 頁 PDF + 41 支參考短片）、`$250` `World Building Academy` 與 `Flora` 推廣連結。
- **可程式化取得性**：頁面雖在 FAQ 提及「Cinematique is open source」並允許商業專案免費使用其 Prompt 範本，但站上未見任何開源授權條款識別碼（如 MIT/CC）、GitHub 倉庫、REST API 或 JSON 批次匯出介面，所有條目資料皆打包於前端。

---

## 三、評估與歸檔結論

- **參考價值**：在調校 Midjourney、Runway、Veo、Kling 或 Grok Imagine 時，可直接取用其 **攝影機型號 + 鏡頭光圈 + 底片色調（Kodak Vision3 / Portra）+ 具體光位角度** 的組合詞彙，減少模糊形容詞造成的畫面不穩定。
- **任務評估**：純外部靜態瀏覽型參考詞庫，無須於 `ai-inbox` 建立實作任務，狀態設為 `archived`。
