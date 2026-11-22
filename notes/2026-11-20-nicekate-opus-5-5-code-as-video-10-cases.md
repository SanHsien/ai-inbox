---
id: "2026-11-20-nicekate-opus-5-5-code-as-video-10-cases"
title: "YouTube 影音評估：NiceKate AI《迷上 Opus 5.5 做視頻：10個案例》與 Code-as-Video 創意分鏡解構"
source_url: "https://youtu.be/qTYxVlEOY04"
source_platform: "youtube"
author: "NiceKate AI (kate人不错)"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-20"
status: done
cluster: 2
cluster_role: "代碼影片創意分鏡"
short_title: "Opus5.5影片十案例"
tags:
  - claude-opus-5-5
  - code-as-video
  - creative-coding
  - p5js-threejs-remotion
  - anti-ai-slop
  - prompt-engineering
---

# YouTube 影音評估：NiceKate AI《迷上 Opus 5.5 做視頻：10個案例》與 Code-as-Video 創意分鏡解構

- **來源影片**：[迷上 Opus 5.5 做视频：震惊，瘫坐，爆炸！10个案例 (YouTube)](https://youtu.be/qTYxVlEOY04)
- **發布頻道 / 作者**：`NiceKate AI`（微信公眾號：`kate人不错`、X/Twitter：`@nicekate8888`、發布於 `2026-09-25`）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`](./2026-10-18-awesome-opus5-5-videos-prompt-zoo.md)（Awesome Opus 5.5 Videos 700+ 代碼驅動基準庫）
  - [`notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md`](./2026-10-17-shipper-epstein-md-anti-ai-slop.md)（反 AI 罐頭設計與審美防線）
  - [`notes/2026-10-17-tasteskill-v2-anti-slop-frontend.md`](./2026-10-17-tasteskill-v2-anti-slop-frontend.md)（TasteSkill v2 前端設計審美規範）
  - [`notes/2026-11-19-ann-cheng-muse-ai-short-video-skill.md`](./2026-11-19-ann-cheng-muse-ai-short-video-skill.md)（AI 短影音管線）

---

## 1. 原始資料盤點（影片章節、10 個案例與技術解析）

- **影片核心論點**：
  - 本片探討的「用 Claude Opus 5.5 做影片」，非傳統像素擴散生成（Diffusion/Sora/Runway 等直接生成 pixel 的黑箱模型），而是**「Code-as-Video / Creative Coding（代碼驅動動態視覺）」**流派。
  - Opus 5.5 同時扮演「導演、編劇兼軟體工程師」，由 LLM 直寫操控畫面、動畫與時間軸的程式碼（HTML5 Canvas、SVG、p5.js、Three.js、CSS Keyframes 或 Remotion），結合瀏覽器渲染與本地錄製管線自主驗收與重構。
- **10 個核心案例拆解（依時間戳記錄）**：
  1. `00:00` **刺繡版《錦鯉活了》**：傳統東方刺繡風格，以細密程序化紋理與針線色澤模擬魚身擺動，展現非寫實質感的數位工藝。
  2. `01:33` **三蹦子 ULTRA MAX 廣告大片**：將農用三輪車套入旗艦科技發表會的高反差敘事，搭配 3D 鏡頭環繞、金屬倒影、暗調光影與反諷文字標籤。
  3. `02:45` **兵馬俑街舞**：古代陶俑的骨骼關節程序化綁定，將定格剛硬質地與現代街舞的重拍節奏產生跨時空戲劇張力。
  4. `03:26` **碟中蛋（買雞蛋拍成諜戰片）**：將微小生活情境（超市買雞蛋）提升為電影級分鏡，運用特寫、呼吸感晃動與高反差光影建立懸疑感。
  5. `04:39` **沒有骨頭，章魚怎麼把手臂伸得這麼靈活？**：精準生物力學科普，展示肌肉流體靜力學（muscular hydrostats）的柔性形變與無骨伸展動態。
  6. `05:51` **突突突 · Tractor GP（拖拉機大獎賽）**：賽車模擬遊戲風格 UI、動態粒子塵土特效與拖拉機物理震動反饋。
  7. `06:57` **剛 3D 列印出來的龍為什麼就能動**：一體成型鉸鏈（Print-in-Place）工程結構科普，透過幾何剖面與活動間隙視覺化展示機械原理。
  8. `08:12` **搓澡 × 精密工業紀錄片**：將浴室搓澡動作以微米級工業加工視角呈現，極致嚴肅的旁白與市井題材形成幽默解構。
  9. `09:25` **棉花糖如何形成**：高溫離心、糖絲結晶與相變過程的熱流體動力學動態圖解。
  10. `10:38` **蝴蝶的顏色，可能不只是「塗上去」的**：奈米級幾何鱗片結構、光波干涉與結構色（Structural Coloration）光學原理剖析。
- **互動與社群反饋**：
  - 留言區互動積極，觀眾討論集中於「如何將 LLM 輸出的單檔代碼快速轉為 Remotion 或錄影輸出」、以及「科普解說中結構色與鉸鏈的可解釋性遠超一般 AI 影片」。

---

## 2. 對現有系統的啟發與架構映射

- **徹底消除 AI 視覺生成幻覺（Anti-Slop）**：傳統文生影片常見「手指多一根、齒輪胡亂旋轉、文字形變」等致命缺陷；而 Code-as-Video 透過確定性數學與物理公式計算運動軌跡，**在工程結構、科普圖解與 UI 動效領域具備 100% 幾何正確性**。
- **「高反差敘事（High-Contrast Framing）」編劇模板**：案例 2（三蹦子發表會）、案例 4（買蛋諜戰片）、案例 8（搓澡工業紀錄片）揭示了極具傳播力的 Prompt 編劇法：**將最接地氣的日常微小事物，以頂級電影／旗艦發布會／精密製造的敘事語法與鏡頭語言進行降維包裝**。
- **與本機工具鏈結合可能**：庫內已有 `Generative UI` 與 `Generative HTML` 能力，可進一步萃取此類「科普動畫與高反差短片」的標準化分鏡 Prompt，為未來多代理影片生成管線提供範本。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261120-07`**｜**[優先級：低]** 萃取「Code-as-Video」10 款創意反差與科普動畫之結構化分鏡模板，納入 `docs/code-as-video-creative-patterns.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\code-as-video-creative-patterns.md`（收錄於集群 2）
  - **執行步驟**：
    1. 梳理影片中「高反差電影敘事（三蹦子/碟中蛋/搓澡）」與「精密科普動態（結構色/一體列印鉸鏈/肌肉流體）」兩大類 Prompt 結構。
    2. 定義 Code-as-Video 的五步分鏡規格（場景定義、核心反差公式、物理/數學運動規則、鏡頭運動、渲染引擎標記）。
  - **驗收標準（DoD）**：產出 `docs/code-as-video-creative-patterns.md`，包含具體可執行的分鏡模板，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-22
  - **實作紀錄 / 證據**：已產出 docs/code-as-video-creative-patterns.md，完整解構 NiceKate AI 10 款案例之「高反差電影敘事」與「精密科普動態」雙流派結構，制定五步分鏡規格（Timeline FSM、反差/科學公式、確定性物理規則、程式化運鏡與 HUD、渲染引擎約束）及兩套可直接執行的分鏡 Prompt 模板；通過 python tools/verify_inbox.py 驗證。
