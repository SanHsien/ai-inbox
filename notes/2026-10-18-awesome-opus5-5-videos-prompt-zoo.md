---
id: 2026-10-18-awesome-opus5-5-videos-prompt-zoo
title: "Awesome Opus 5.5 Videos 提示詞動物園解構：700+ 代碼驅動視覺動畫、3D 場景、技術解說與互動遊戲開源基準庫"
source_url: "https://github.com/yihui-dev/awesome-opus5-5-videos/tree/main"
source_platform: "GitHub"
author: "yihui-dev & Skillry Community"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: in-progress
cluster: 2
cluster_role: "提示動物園"
short_title: "Awesome Opus 5.5 Videos"
tags:
  - awesome-opus5-5
  - prompt-zoo
  - creative-coding
  - threejs-webgl
  - canvas-animation
  - gsap-svg
  - explainer-graphics
  - web-audio
---

# Awesome Opus 5.5 Videos 提示詞動物園解構：700+ 代碼驅動視覺動畫、3D 場景、技術解說與互動遊戲開源基準庫

- **來源連結**：[yihui-dev/awesome-opus5-5-videos (GitHub)](https://github.com/yihui-dev/awesome-opus5-5-videos/tree/main)
- **展示與重製對照站**：[Skillry (skillry.dev/ai-videos/opus-5-5)](https://skillry.dev/ai-videos/opus-5-5)
- **分析日期**：`2026-10-18`
- **當前狀態**：`🟢 已做 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-prompt-motion-claude-video-showcase.md`](./2026-10-18-prompt-motion-claude-video-showcase.md)（Prompt Motion 策展庫解構）
  - [`notes/2026-10-17-motion-prompt-animation-dictionary.md`](./2026-10-17-motion-prompt-animation-dictionary.md)（微觀動態字典）
  - [`notes/2026-10-17-cinematic-shot-ui-film-director.md`](./2026-10-17-cinematic-shot-ui-film-director.md)（宏觀運鏡分鏡）

---

## 1. 核心內容摘要與技術深挖

### 1.1 什麼是 Awesome Opus 5.5 Videos？
`yihui-dev/awesome-opus5-5-videos` 是一個在 GitHub 上獲得超過 5,700 顆星與近 600 次 Fork 的頂級開源專案。它全面收錄了全球創作者使用 **Claude Opus 5.5** 透過純文字 Prompt 生成的「**代碼驅動動態視覺作品（Code-driven Visual Creations）**」：
- **龐大資料規模**：包含 **703 組完整提示詞（存於 `prompts/*.md` 與 `data/videos.json`）**。
- **即時重製與雙欄對照（Live Remakes）**：其中 418 部作品在 Skillry 平台完成重新編譯渲染，提供原始推文影片與即時代碼重製（Live Remake）的並排對照。
- **四大核心技術領域**：
  1. **動態圖形（Motion Graphics, 58+ 核心案例）**：字體排版、品牌發表、UI 流轉、SVG Path Morphing、GSAP 物理緩動。
  2. **技術與概念解說動畫（Explainers, 16+ 核心案例）**：分散式架構演進、排序演算法動態圖解、量子力學模型、資料流管道可視化。
  3. **3D 場景與著色器（3D Scenes, 14+ 核心案例）**：Three.js 程序化生成幾何體、GLSL Raymarching、頂點著色器光影流動、粒子星系。
  4. **互動遊戲與合成器（Games & Interactive, 12+ 核心案例）**：Canvas 物理引擎彈珠台、網頁合成器（Web Audio API + 互動式波形）、粒子沙盒。

```text
┌────────────────────────────────────────────────────────────────────────┐
│        Awesome Opus 5.5 Videos 程式碼視覺生成（Creative Coding）體系    │
└────────────────────────────────────────────────────────────────────────┘

 [ 創作者 Prompt / 概念描述 (prompts/*.md) ]
                     │
                     ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ Claude Opus 5.5 程式碼生成引擎                                        │
 │ ├─ 數學與物理模型建模 (貝茲曲線, 向量場, 粒子引力, 矩陣變換)          │
 │ ├─ 現代前端視覺渲染技術棧切換：                                       │
 │ │   • Canvas 2D Context (高性能粒子、數學分形)                        │
 │ │   • SVG + GSAP (精確向量幾何、字體排版、路徑變形)                   │
 │ │   • Three.js + WebGL (3D 空間網格、攝像機軌道、PBR 材質)            │
 │ │   • GLSL Fragment Shaders (GPU 像素級光線步進 Raymarching)         │
 │ │   • Web Audio API (程式化震盪器 Oscillator、即時音效合成)          │
 │ └─ 零依賴單檔架構 (Single-File Self-Contained HTML)                   │
 └───────────────────┬───────────────────────────────────────────────────┘
                     │ 輸出 index.html
                     ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 即時執行與多場景交付                                                  │
 │ ├─ 1. 瀏覽器直接互動 (60 FPS, 支援滑鼠懸停、點擊反饋、鍵盤控制)       │
 │ ├─ 2. Generative UI Widget (直接內嵌於對話面板作為動態概念解釋)       │
 │ └─ 3. 視訊錄製流水線 (Headless Chrome + FFmpeg 匯出無損 4K 影片)       │
 └───────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 技術深度：為什麼「單檔代碼生成」優於傳統影片？
相較於 Sora / Runway / Kling 等基於 Diffusion 的影片模型，Claude 生成前端代碼驅動的動態具有顛覆性的技術優勢：

1. **無限解析度與確定性（Infinite Scalability & Zero Artifacts）**：
   - 影片完全由向量與著色器計算生成，在 1080p、4K 乃至 8K 螢幕上皆為點對點原生銳利渲染，徹底消除神經網路生成視訊常見的邊緣模糊、偽影與畫面漂移。
2. **文字排版與邏輯零幻覺（Zero Text & Diagram Hallucination）**：
   - 在技術解說動畫（Explainers）中，代碼中的架構名稱、API 呼叫時序與資料欄位完全由 DOM/Canvas 向量繪製，絕對不發生字母亂碼或拼寫崩壞。
3. **即時互動性（True Interactivity）**：
   - 作品不僅僅是「被動觀看的影片」，更是支援滑鼠視角旋轉、點擊互動、音效合成的動態軟體程式，能直接轉換為產品 Landing Page 或 Demo Widget。
4. **機器可讀的結構化 Prompt 資料集（Machine-Readable Dataset）**：
   - 專案附帶 `data/videos.json` 與標準命名之 `prompts/<creator>-<id>.md`，每份檔案包含作者原始推文、提示詞全文、使用的技術標籤（如 `Three.js · GLSL · Canvas`），具備極高的 Agent 檢索與 Few-shot 學習價值。

---

## 2. 對現有系統的啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與 Note 18（Prompt Motion）的互補關係**：
    - `Prompt Motion`（筆記 18）：偏向產品宣傳片、文字排版與 Remotion 視訊管道。
    - `Awesome Opus 5.5 Videos`（本篇）：則是**橫跨 2D 動態、3D WebGL、GLSL 著色器與 Web Audio 的綜合性 Creative Coding 基準庫**，資料量（700+）與多樣性大幅超越前者。
  - **結合 Antigravity 內建技能**：
    - 可直接與 `generative_ui` 技能聯動，讓 Agent 在回答演算法或架構原理時，調用本庫的 Prompt 結構生成「可操作的動態圖解」。
  - **結合現有的微觀/宏觀視聽體系**：
    - `cinematic-shot`（運鏡）+ `motion-prompt`（動態字典）+ `awesome-opus-5.5`（端到端單檔代碼 Prompt），構建出完整的 AI 視覺生成閉環。

- **落差與採納判斷**：
  - **高度價值採納點**：
    1. 將 `data/videos.json` 與精選 Prompt 轉化為本地 Agent 可快速檢索的視覺生成基準庫。
    2. 提煉其「單檔自包含 HTML（Single-file HTML）」的 Prompt 模式，作為 Coding Agent 生成互動式視覺演示的標準能力。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261018-07`**｜**[優先級：低]** 建立「Claude Opus 5.5 程式碼視覺化生成提示詞庫（Awesome Opus 5.5 Prompts Benchmark）」解析腳本與分類檢索工具
  - **目標範圍**：`SanHsien/ai-inbox` 與前端視覺動效工具庫
  - **狀態**：⚪ 不做（提示詞庫解析腳本價值低，視覺化生成需求由 T-20261018-08 單檔技能涵蓋）
  - **具體實作步驟**：
    1. 分析 `yihui-dev/awesome-opus5-5-videos` 的 `data/videos.json` 結構與 703 個 Prompt Markdown 格式。
    2. 實作輕量提取與索引腳本，依技術棧（Canvas, SVG, GSAP, Three.js, GLSL, Web Audio）與場景（動態圖形、技術解說、3D 場景、互動遊戲）進行標籤化索引。
    3. 篩選出 Top 20 具備高工業可用性的「軟體架構解說動畫（Explainers）」與「3D 產品展示（3D Scenes）」標準範本。
  - **驗收標準（DoD）**：產出結構化索引資料或檢索腳本，能一鍵檢索對應技術棧的最佳 Prompt 範本。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [x] **`T-20261018-08`**｜**[優先級：中]** 封裝「單檔 HTML/Canvas/Three.js 互動視覺化生成 Agent 技能（Single-File Creative Coding Skill）」
  - **目標範圍**：本地 Agent Skills 庫（如 `creative-coding` / `visual-explainer`）
  - **具體實作步驟**：
    1. 提煉 `awesome-opus5-5-videos` 中高品質代碼生成的 Prompt 工程規範（包含防跑版、單檔內嵌 CDN 依賴、自適應響應式 Canvas、Web Audio 安全解鎖）。
    2. 建立通用 Agent 提示詞樣板，讓 Claude Code / Antigravity 在面對「技術架構解說」或「互動視覺演練」時，能直接生成零依賴、可在瀏覽器直接執行的單檔 HTML。
    3. 結合 `generative_ui` 技能，支援在對話中或本地直接開啟預覽。
  - **驗收標準（DoD）**：產出結構化 Agent 技能規範或樣板 Markdown，驗證能由純文字需求生成高幀率（60fps）、支援滑鼠互動的單檔 3D / 動畫頁面。
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。產出標準技能規範 `templates/single-file-creative-coding-skill.md` 與單檔 Three.js (r128 CDN) 螺旋星系粒子視覺化範例 `assets/creative-coding-demo/threejs-particle-galaxy.html`。

---
