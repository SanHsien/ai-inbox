---
id: "2026-11-28-aiposthub-claude-four-animation-frameworks-eval"
title: "Threads「Claude 搭配四種動畫框架（Python／Motion Canvas／Three.js／Blender）」視覺對比評估"
source_url: "https://www.threads.com/@aiposthub/post/DgO5eA6kYHm"
source_platform: "Threads (@aiposthub)"
author: "aiposthub (@aiposthub)"
analyzed_at: "2026-11-28"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_reviewed_at: "2026-11-28"
source_images: 2
source_replies: 10
source_review_note: "已完整讀取原貼文正文、4 欄對比影片畫面、作者 2 則回覆串（含釘選課程預覽卡）與未登入頁面可見之 8 則網友回覆；貼文計數 12 則回覆中尚有 2 則未於未登入畫面顯示，亦未另行開啟 academy.aiposthub.com 課程頁。"
tags:
  - claude
  - code-as-video
  - motion-canvas
  - threejs
  - blender
  - python
  - threads
status: archived
cluster: 2
cluster_role: "四框架動畫對比"
short_title: "Claude四框架動畫對比"
---

# Threads「Claude 搭配四種動畫框架（Python／Motion Canvas／Three.js／Blender）」視覺對比評估

- **來源連結**：[aiposthub (@aiposthub) Threads 貼文](https://www.threads.com/@aiposthub/post/DgO5eA6kYHm)（原分享網址 `https://www.threads.com/share/BATDZIWEDz`，`2026-11-27` 下午 1:11 發布；8.0 萬次瀏覽、1,234 讚、12 回覆、131 轉發、848 分享）
- **分析日期**：`2026-11-28`
- **當前狀態**：`⚪ 歸檔備查 (Archived)`（未附原始程式碼／Prompt 與原始作者出處，且釘選導流至付費課程；本庫已有 `SanHsien/code-as-video-studio` 與對應規格，不另開待辦）

---

## 0. 原始資料盤點

- **主貼文與示範影片**：貼文轉述「有網友用同一個場景（綠丘、小徑、風車、藍天雲朵與飛行的方塊／紙飛機），展示了 4 種動畫製作方案」，但未標註原作者出處亦未附 GitHub 倉庫。
  1. **`Python`**：手繪筆觸與紙質貼圖風格（作者歸類為手繪藝術、數學動畫與資料視覺化）。
  2. **`Motion Canvas`**：銳利 2D 向量動態設計，畫面呈現 `easeOutElastic` 緩動曲線圖、`WHOOSH!`／`ZOOM!` 漫畫擬聲字與虛線軌跡（適合知識型影片與產品展示）。
  3. **`Three.js`**：WebGL 3D 場景，加入強日光暈（bloom/flare）與發光粒子軌跡（適合互動網頁）；留言區 `@doingimc` 實看指出「Three.js 看起來有點散光了」（過度光暈）。
  4. **`Blender`**：3D 體積雲感雲層、白色螺旋氣流軌跡、3D 樹木與立體光影渲染（適合電影感動畫）。
- **作者釘選導流回覆（`DgRSiMKAebS`）**：
  - 貼出 `https://academy.aiposthub.com/p/flash-lesson-09-claude-opus-animation`（AIPost Academy《Flash Lesson：Claude Opus 5.5 動畫設計實戰》），預覽圖主打免 AE、單一 HTML 檔與 SVG `<animate>` 動畫（Logo 進場、Loading、動態長條圖、手寫字等）。
- **網友留言重點（可見 8 則）**：
  - 多數觀眾認同「選對渲染框架與光影材質比單純改 Prompt 影響更大」（`@lanling.ai`、`@techtip_s.scarlett_`、`@raya.bc`、`@builds.twin`）；
  - `@doingimc` 點出 Three.js 範例光暈過曝問題；`@readwithfun` 與 `@larmo_wonderful` 詢問如何實際在 Prompt 搭配不同工具（作者未回覆）。

---

## 1. 評估結論與歸檔理由

- **對應現有系統 / 專案**：
  - 本庫已將程式碼驅動影片與分鏡工程獨立至 [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)，並於 [`docs/code-as-video-creative-patterns.md`](../docs/code-as-video-creative-patterns.md) 與 [`docs/3d-gui-agent-control-bridge.md`](../docs/3d-gui-agent-control-bridge.md) 涵蓋 `HTML5 Canvas + SVG HUD`、`Three.js`、`Remotion` 與 `Blender` 選型。
- **歸檔判斷**：
  - 本貼文無可複用程式碼、Prompt 原文或基準測試數據，本質為「框架選型直覺對比短片＋課程導流」；四框架的視覺定位差異已記錄於本筆記供集群 2 檢索，無須新增實作任務，狀態設為 `archived`。

---

## 2. 拆解待辦事項（Action Items）

> 無新增工程待辦。
