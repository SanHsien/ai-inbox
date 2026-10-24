---
id: 2026-10-17-motion-prompt-animation-dictionary
title: "Motion Prompt：讓 AI 聽懂動態語言的開源視覺動效字典（120 種動畫、動態畫布與 Agent Skill 整合）"
source_url: "https://github.com/showheyohtaki/motion-prompt"
source_platform: "GitHub"
author: "Shohei Ohtaki (@showheyohtaki)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: in-progress
cluster: 2
cluster_role: "動效字典"
short_title: "Motion Prompt 120 種動畫"
tags:
  - motion-prompt
  - animation-dictionary
  - agent-skills
  - frontend-ui
  - video-gen
---

# Motion Prompt：讓 AI 聽懂動態語言的開源視覺動效字典（120 種動畫、動態畫布與 Agent Skill 整合）

- **來源倉庫**：[GitHub - showheyohtaki/motion-prompt](https://github.com/showheyohtaki/motion-prompt)
- **展示圖庫**：[Motion Prompt Live Gallery](https://showheyohtaki.github.io/motion-prompt/)
- **專案作者**：`Shohei Ohtaki (大滝 昇平 / @showheyohtaki)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🔴 未做 (Pending)`
- **授權協議**：`MIT License`

---

## 1. 核心內容摘要與技術深挖

### 1.1 痛點與核心主張
- **痛點（人機動態溝通鴻溝）**：
  - 開發者在向 AI（如 Claude Code, Codex, Cursor）或影片生成模型（如 Veo, Sora, Runaway）描述動畫時，往往受限於「不知道該動作叫什麼名稱」，只能用籠統的模糊形容（例如「那個字慢慢跳出來」、「鏡頭帥氣地轉過去」），導致 AI 產出千奇百怪、難以對齊預期。
  - 創作者並非缺乏想像力，而是缺乏動效領域的**標準共同語言（Common Language）**。
- **解法（視覺動效辭典 + Agent Skill 雙向閉環）**：
  - **五大類別 120 款標準動效規格**：
    1. `motion`（#001–#024）：動態圖形（Motion Graphics，如蒙版展開、文字打字、彈性擺動）。
    2. `camera`（#025–#048）：攝影機運鏡與轉場（如 Dolly in/out、Pan、Tilt、Zoom Transition）。
    3. `ui`（#049–#072）：UI 元件互動（如 Dropdown 展開、Accordion 收合、Modal 彈出、FAB 展開）。
    4. `lp`（#073–#096）：著陸頁與網頁演出（如 Parallax 視差、Scroll Snap、卡片懸停翻轉）。
    5. `photo`（#097–#120）：攝影風格、布光與畫面質感（如 Rim Light、Rembrandt Lighting、Lens Flare）。
  - **純數學時間驅動（Deterministic Canvas 2D）**：每個動態都是純 JavaScript 函式 `cells[i](ctx, w, h, u)`，僅依據正規化時間 $u \in [0, 1]$ 計算，無任何外部程式庫、不呼叫隨機數，確保即時預覽與逐幀渲染完全一致。
  - **圖庫點選直送 AI（Pick & Send to AI Loop）**：
    - Skill 內建本地輕量監聽服務，使用者在 Claude Code 中輸入 `Open the motion-prompt library`，瀏覽器自動打開互動圖庫。
    - 使用者在圖庫挑選喜歡的動效後點擊「Send to AI」，挑選的編號與筆記直接回傳終端 Agent，Agent 自動取得規格參數與參考代碼轉譯至使用者專案（支援 CSS/Tailwind, Canvas, Remotion, 或視訊生成提示詞）。

### 1.2 人機動效協作架構可視化（Pick & Implement Loop）

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Motion Prompt 人機動效閉環協作架構                         │
└────────────────────────────────────────────────────────────────────────┘

    [使用者] ───────────────────────────┐
       │ 1. "Open the motion-prompt"    │ 3. 瀏覽圖庫、點選心儀動效 (#012, #045)
       ▼                                │    點擊「Send to AI」
 ┌──────────────┐                       │
 │ Coding Agent │                       ▼
 │ (Claude Code │ ── 2. 啟動本地監聽 ──> ┌───────────────────────────┐
 │  或 Codex)   │    並打開瀏覽器        │ Motion Prompt Web Gallery │
 └──────┬───────┘                       │ (120 款真實動態 Canvas 卡片)│
        │                               └─────────────┬─────────────┘
        │ 4. 接收已選編號、規格與註記                   │
        │    (如 #012: Mask Reveal, #045: Push Zoom)   │ 透過 127.0.0.1 本地通訊
        ▼                                              ▼
 ┌───────────────────────────────────────────────────────────────────┐
 │ 5. 動效代碼轉譯引擎 (Porting Engine)                             │
 │    ├─ CSS / Tailwind / Framer Motion (網頁元件)                   │
 │    ├─ Remotion / React (程式化影片生成)                           │
 │    ├─ Canvas 2D / WebGL (互動視覺)                                │
 │    └─ Veo / Sora 英文運鏡 Prompt (視訊生成模型)                   │
 └──────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
                         [落地至使用者專案或成果]
```

### 1.3 核心規格與套裝分類

| 套裝代號 | 領域範圍 | 代表動效名稱範例 | 視覺基調 |
| :--- | :--- | :--- | :--- |
| **`motion`** | 動態圖形視覺 | Mask Reveal, Stagger Fade, Kinetic Typography, Path Draw | 深海軍藍底色 + 4 色高對比點綴 |
| **`camera`** | 攝影機運鏡與轉場 | Dolly In, Pan Left, Whip Pan, Crash Zoom, Tracking Shot | 淺灰底色 + 藍色視角導引箭頭 |
| **`ui`** | 現代 UI 元件動態 | Floating Action Button, Bottom Sheet, Skeleton Shimmer | 暖白底色 + 黑色幾何與擬真滑鼠軌跡 |
| **`lp`** | 著陸頁網頁演出 | Hero Parallax, Sticky Scroll, Reveal on View, Glass Blur | 簡約桌面瀏覽器視窗 + 朱紅強調色 |
| **`photo`** | 燈光與質感風格 | Softbox Diffused, Hard Shadow, Bokeh Blur, Golden Hour | 個別場景獨立光影渲染對比 |

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與 `cinematic-shot` 協同**：先前收錄了 [`notes/2026-10-17-cinematic-shot-ui-film-director.md`](./2026-10-17-cinematic-shot-ui-film-director.md)（電影級 UI 鏡頭運鏡）。`cinematic-shot` 偏向整體場景調度與運鏡腳本，而 `motion-prompt` 正好補足了微觀動態元件（120 種精準命名與貝茲曲線參數），兩者結合能形成頂級的 UI 動態產品影片生成管線。
  - **與 `Reelbird` 協同**：搭配 [`notes/2026-10-17-reelbird-open-source-screen-recorder.md`](./2026-10-17-reelbird-open-source-screen-recorder.md)，Agent 生成具備 `motion-prompt` 頂級動效的前端頁面後，直接以 Reelbird 錄製成果並生成分享短網址。
  - **前端樣式預設偏好**：符合全域規則中的「流暢的過場與 hover 回饋」，徹底解決工程師只會寫 `transition: all 0.3s ease` 的僵硬感。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **「動態編號索引化」溝通模式**：在 Prompt 中直接引用動效代號（如 `#005 Mask Reveal`、`#032 Tracking Shot`），精準消除人機歧義。
    2. **獨立無依賴 Canvas 實作哲學**：其 `cells[i](ctx, w, h, u)` 時間驅動無依賴架構，非常適合移植到各種輕量前端小工具或 Generative UI 之中。
  - **需優化與客製化之處**：
    - 目前官方只有英文與日文版名稱清單，中文使用者需要一份精準的**繁體中文對照索引**，方便在中文對話中順暢引用。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-17`**｜**[優先級：高]** 整理 `motion-prompt` 120 款動效的繁體中文名稱與參數對照表，納入前端動效手冊
  - **完成日期**：2026-10-23
  - **目標範圍**：`C:\GitHub\ai-inbox\notes\` 與前端動效指南
  - **具體實作步驟**：
    1. 爬取或解析 `packs/` 下 5 大模組（motion, camera, ui, lp, photo）共 120 項動效的英文定義與規格。
    2. 翻譯並校訂為精準的繁體中文術語（如「遮罩展開」、「交錯漸入」、「軌道跟隨」）。
    3. 整理出方便 Agent 與人類快速查閱的 Markdown 索引速查表（包含 ID、英文名、中文名、一句話語法與適用場景）。
  - **驗收標準（DoD）**：產出完整的 120 款繁中對照速查表，且能讓 Agent 透過關鍵字精準檢索到對應編號。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `docs/motion-prompt-cheatsheet.md`，從原始 repo 完整整理 6 大套件共 144 款動效（原筆記預估 120 款，官方 repo 實際擴充 motion2 套件後總計 144 款，已如實完整收錄並註明差異）之繁中名稱、英文名稱、效果說明、對 AI 說法範例與動態物理參數。

- [ ] **`T-20261017-18`**｜**[優先級：低]** 串接 `motion-prompt`（微觀動態字典）與 `cinematic-shot`（宏觀運鏡），產出產品發表展示 Prompts 範本
  - **目標範圍**：多媒體影視與展示工作流
  - **狀態**：⚪ 不做（與 T-20261018-02 重複，兩者皆併入 T-20261021-15 Code-as-Video Studio 規範）
  - **具體實作步驟**：
    1. 抽取 `cinematic-shot` 的鏡頭語法（Hero Close-up, Feature Pan, Isometric Orbit）。
    2. 結合 `motion-prompt` 的 UI 動態（#049-#072）與網頁演出（#073-#096）。
    3. 撰寫一套「軟體產品動態發表宣傳片」的標準化提示詞範本庫，包含 Tailwind/Framer Motion 代碼範例與 Veo/Sora 視訊生成語法。
  - **驗收標準（DoD）**：提供至少 3 組端到端範本（如「SaaS 產品首頁揭幕」、「行動 App 互動功能展示」），代碼可直接在瀏覽器流暢播放。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
