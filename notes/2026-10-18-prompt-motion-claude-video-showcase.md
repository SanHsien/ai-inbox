---
id: 2026-10-18-prompt-motion-claude-video-showcase
title: "Prompt Motion 策展庫解構：Claude 驅動的代碼動效視頻（Code-driven Motion Graphics）原理與可複製 Prompts/Skills 實戰解析"
source_url: "https://prompt-motion.com"
source_platform: "Web Showcase"
author: "@p4nthera_ & Global Claude Creators"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: archived
cluster: 2
cluster_role: "視頻策展"
short_title: "Prompt Motion 視頻展示庫"
tags:
  - prompt-motion
  - code-driven-video
  - claude-motion
  - remotion
  - kinetic-typography
  - ui-showcase
---

# Prompt Motion 策展庫解構：Claude 驅動的代碼動效視頻（Code-driven Motion Graphics）原理與可複製 Prompts/Skills 實戰解析

- **來源連結**：[Prompt Motion 官方網站](https://prompt-motion.com)
- **策展發起者**：`@p4nthera_` & 全球 Claude 創作者社群
- **分析日期**：`2026-10-18`
- **當前狀態**：`⚪ 已封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-17-motion-prompt-animation-dictionary.md`](./2026-10-17-motion-prompt-animation-dictionary.md)（微觀動效字典）
  - [`notes/2026-10-17-cinematic-shot-ui-film-director.md`](./2026-10-17-cinematic-shot-ui-film-director.md)（宏觀運鏡分鏡）

---

## 1. 核心內容摘要與技術深挖

### 1.1 什麼是 Prompt Motion？
`Prompt Motion` (`prompt-motion.com`) 是一個專為 **Claude（特別是 Claude Opus 5.5 / 3.7 系列）動態設計（Motion Graphics）** 所建立的開放式作品策展與 Prompt 開源庫：
- **收錄規模**：收錄全球頂尖創作者製作的 200 多個高品質 Motion 影片。
- **透明可複製性（Open Recipes）**：每個影片直接附帶**完整的提示詞（Prompt）**、**所調用的 Agent Skill 規範**、以及底層的技術堆疊（如 Remotion, Canvas, GSAP, CSS Keyframes）。
- **涵蓋領域**：
  1. **產品 UI 演示（Product UI Demos）**：擬真軟體互動、按鈕反饋、卡片流轉。
  2. **動態排版與字幕（Kinetic Typography）**：科技發表會級別的文字放大、翻轉與彈出。
  3. **科技講解動畫（Explainer Graphics）**：資料流圖解、架構演進動畫。

---

### 1.2 Claude 做影片的底層原理：代碼驅動動態圖形（Code-Driven Motion Graphics）
許多人誤以為這是 Sora、Runway 或 Kling 那種基於 Diffusion 的像素神經網路影片。事實上，這是截然不同的**確定性工程渲染（Deterministic Engineering Rendering）**：

```text
┌────────────────────────────────────────────────────────────────────────┐
│             Claude 代碼驅動動態影片 (Code-Driven Video) 生成架構        │
└────────────────────────────────────────────────────────────────────────┘

 [使用者創意需求 / 產品發布文案]
         │
         ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ Claude (Opus 5.5 / 3.7) 程式碼生成大腦                                │
 │ ├─ 1. 時間軸設計：分解為精確幀數 (Frames / FPS)                      │
 │ ├─ 2. 緩動函數計算：貝茲曲線 (Cubic-Bezier Easing / Spring Physics)  │
 │ └─ 3. 生成可執行代碼：                                               │
 │       • Remotion (React + TypeScript 視訊框架)                        │
 │       • HTML5 Canvas / SVG + GSAP (綠襪動態庫)                        │
 │       • WebGL / Three.js 3D 著色器                                    │
 └──────────────────────────────────┬────────────────────────────────────┘
                                    │ 生成程式碼
                                    ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 本地 Headless 瀏覽器環境 (Puppeteer / Playwright / Remotion CLI)       │
 │ ├─ 1. 在虛擬畫布逐幀執行 JavaScript 動態運算                          │
 │ ├─ 2. 無損向量光柵化 (Zero Loss Vector Rasterization)                 │
 │ └─ 3. 完美文字排版 (100% 杜絕 Diffusion 視頻的文字亂碼問題)          │
 └──────────────────────────────────┬────────────────────────────────────┘
                                    │ 輸出無損影格序列 (Image Sequence / Stream)
                                    ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ FFmpeg 視訊編碼器 (H.264 / ProRes / WebM)                             │
 │ └─ 快速合成為高幀率 (60 FPS)、高解析度 (4K) 的 MP4 產品展示片         │
 └───────────────────────────────────────────────────────────────────────┘
```

#### 與 Diffusion 影片模型的本質優勢對比：
1. **文字 100% 精準（Zero Hallucination Text）**：完全由 DOM/Canvas 繪製向量字體，排版精緻、無文字變形或假字。
2. **完全可編程與回滾（Full Determinism & Version Control）**：隨時調整一個 hex 色碼、動畫持續時間（0.3s -> 0.4s）或文字大小即可重新編譯，不需要靠抽卡碰運氣。
3. **超高性價比**：只消耗 LLM 生成幾百行 Code 的 Token，本地即可透過 FFmpeg 跑完渲染，不需要昂貴的 GPU 影片生成算力租金。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **串聯視聽全鏈條矩陣**：
    - `cinematic-shot`（筆記 05）：提供宏觀運鏡思維（分鏡、景別、推拉移）。
    - `motion-prompt`（筆記 09）：提供 120 種微觀動效名詞與參數。
    - `Prompt Motion`（本篇）：提供**真實可跑的端到端 Code 樣板與完整的 Prompt 咒語**。
    - `reelbird`（筆記 08）：提供螢幕錄影展示與即時分享連結。
  - **適用於 Windows 11 本地開發環境**：
    - Remotion 與 Headless Chrome 可直接在 Windows 11 Node.js 22 環境下離線運行，完全相容於原生環境。

- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **直接提取 Prompt Motion 的 Top 級 Prompt 結構**：將其轉化為本地可用之「產品發布宣傳片生成 Agent Skill」。
    2. **沉澱 Remotion 渲染腳本**：建立最輕量的本機渲染流水線，讓 Agent 能依據文字描述直接產出 MP4。
  - **適用性界線**：
    - 代碼驅動適合 UI 介面、文字排版、圖表數據動效；不適合真實人物肢體或大自然風景（該類場景仍需仰賴 Sora / Kling）。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261018-01`**｜**[優先級：低]** 建立「Claude 代碼動效視頻渲染標準工作流（Remotion / HTML Canvas Video Pipeline）」
  - **目標範圍**：多媒體生成技能庫與 Node.js 工具鏈
  - **狀態**：⚪ 不做（Remotion 渲染流程併入 T-20261021-15（規範）與 T-20261019-04（幀同步原型））
  - **具體實作步驟**：
    1. 研讀 `prompt-motion.com` 最受歡迎案例之底層代碼（Remotion 與 HTML5 Canvas + GSAP 結構）。
    2. 在本地 Windows 11 環境配置輕量渲染驗證腳本（透過 `remotion render` 或 Puppeteer + FFmpeg）。
    3. 編寫 Agent Skill 規範：定義如何讓 Claude 生成符合幀率（60fps）、色彩、彈性緩動（Spring）的標準化動效代碼。
  - **驗收標準（DoD）**：在本地成功跑通一組自動由文字 Prompt 產生 Remotion 代碼並渲染出 5 秒 MP4 產品演示片的端到端測試。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261018-02`**｜**[優先級：低]** 彙整 Prompt Motion 精選「產品 UI 展示與動效字幕」Prompt 範本庫，串聯 `motion-prompt` 與 `cinematic-shot`
  - **目標範圍**：`SanHsien/ai-inbox` 與視覺動效手冊
  - **狀態**：⚪ 不做（併入 T-20261021-15 Code-as-Video Studio 規範，不另建 Prompt 範本庫）
  - **具體實作步驟**：
    1. 從 Prompt Motion 200+ 案例中，篩選出 10 款最適合開源專案與商業軟體發布的展示範本（含 Kinetic Type、SaaS Dashboard Demo、Feature Reveal）。
    2. 將先前整理之 `motion-prompt`（120 款動效字典）與 `cinematic-shot`（運鏡分鏡）注入範本中。
    3. 產出繁體中文說明的「開源專案發表短影音 Prompts 寶典」。
  - **驗收標準（DoD）**：產出結構化 Prompt 範本 Markdown 手冊，可供各 Agent 在專案發表時直接調用。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---
