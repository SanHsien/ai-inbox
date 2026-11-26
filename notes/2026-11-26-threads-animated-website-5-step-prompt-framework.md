---
id: "2026-11-26-threads-animated-website-5-step-prompt-framework"
title: "Threads 社群教學評析：《動畫互動網站五步 Prompt 框架》——視覺鏡頭口語化拆解、先列素材與 Awwwards 罐頭風險"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "使用者直接提供全文（Threads 貼文，無原始 URL）"
author: "未具名 Threads 創作者"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: unavailable
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
source_review_note: "使用者於對話直接提供貼文全文（無原始 Threads URL，無法於網頁重開核對作者帳號、範例成品、配圖與留言區）。"
status: archived
cluster: 2
cluster_role: "動畫網站提示框架"
short_title: "Threads動畫網站五步法"
tags:
  - frontend
  - animation
  - prompt-engineering
  - creative-coding
  - anti-ai-slop
---

# Threads 社群教學評析：《動畫互動網站五步 Prompt 框架》——視覺鏡頭口語化拆解、先列素材與 Awwwards 罐頭風險

- **來源**：使用者直接提供 Threads 貼文全文（無原始 URL，脈絡針對「Threads 199 元做網站」爭議之免費教學拆解）
- **分析日期**：`2026-11-26`
- **當前狀態**：`⚪ 歸檔參考 (Archived — 不另開工單)`
- **相關交叉參照**：
  - [`docs/anti-ai-slop-frontend.md`](../docs/anti-ai-slop-frontend.md)（反 AI 罐頭前端工程規範）
  - [`templates/subject-inventory-argument-writing-prompt.md`](../templates/subject-inventory-argument-writing-prompt.md)（主體資產盤點與論證寫作前置 Prompt）
  - [`docs/zero-build-shader-hero-sections-spec.md`](../docs/zero-build-shader-hero-sections-spec.md)（零建置動態 Hero 規格）
  - [`notes/2026-11-08-darkthread-kittenjam-motion-library-frontend-animation-prompts.md`](./2026-11-08-darkthread-kittenjam-motion-library-frontend-animation-prompts.md)（前端動效函式庫與提示詞對照）

---

## 0. 原始內容拆解

貼文提出一套面向非技術背景使用者的動畫互動網站 Prompt 順序：

1. **第 0 步（角色與嚴格執行約束）**：設定為得獎級創意總監 / UI/UX（Awwwards / FWA 標準）/ 首席前端架構師（以 *Aventis Yacht Charters* 奢華遊艇為例），要求零遺漏遵守視覺約束、動態曲線、渲染公式與響應式規則。
2. **第 1 步（畫面與參考素材）**：上傳目標動畫與圖片給 AI 學習，定義網站主題、視覺主角與首屏第一眼焦點。
3. **第 2 步（鏡頭與運鏡節奏）**：不需懂 CSS/GSAP/Three.js 術語，直接用口語描述鏡頭（遠景拉近、隨捲動繞產品旋轉、定格等文字出現再往下走）。
4. **第 3 步（色彩與字體）**：定義深淺模式、主色與點綴色、標題粗細與留白比例，並附上參考網站。
5. **第 4 步（互動與手機端適配）**：明確定義 hover、click、scroll 各自觸發的狀態變化與行動端呈現方式。
6. **第 5 步（先列素材清單，再產可操作首頁原型）**：先讓 AI 盤點所需圖片／影片素材，先出單一可操作首頁再逐輪微調（太快、太小、太花直接口頭修正）。

---

## 1. 評估結論與不另開工單理由

- **可取之處**：
  - 「**鏡頭（Camera/Scroll Choreography）與互動（Hover/Click/Scroll）獨立分層描述**」以及「**先列素材清單再動手產首頁**」降低了純口頭描述動畫網站時的遺漏率，與本庫 [`templates/subject-inventory-argument-writing-prompt.md`](../templates/subject-inventory-argument-writing-prompt.md) 的主體盤點精神一致。
- **明顯工程缺口（與本庫既有規範對照）**：
  1. **浮誇人設易誘發 AI 罐頭（Slop）**：英文 Role 採用 `"hyper-luxurious"`、`"award-winning"` 等空泛形容詞而未附具體設計 Token 時，模型常堆疊過度發光、漸層與模糊特效（違反 [`docs/anti-ai-slop-frontend.md`](../docs/anti-ai-slop-frontend.md)）。
  2. **缺少效能與無障礙退場契約**：未要求 `prefers-reduced-motion`、行動端降級或幀率預算，也沒有實際瀏覽器截圖驗收閉環（如本庫的 `inspect.mjs` / CDP 檢驗）。
  3. **無原始成品驗證**：未附貼文網址或實際產出成品連結，無法驗證 *Aventis Yacht Charters* 範例實際生成品質。
- **不另開工單理由**：本庫既有 [`docs/anti-ai-slop-frontend.md`](../docs/anti-ai-slop-frontend.md)、[`templates/subject-inventory-argument-writing-prompt.md`](../templates/subject-inventory-argument-writing-prompt.md) 與 [`docs/zero-build-shader-hero-sections-spec.md`](../docs/zero-build-shader-hero-sections-spec.md) 已覆蓋更嚴謹的前端設計與驗證閘門，本貼文無新增工程項目，故採 `archived` 歸檔參考。
