---
id: 2026-10-18-awesome-opus5-5-videos-prompt-zoo
title: "Awesome Opus 5.5 Videos 提示詞動物園解構：700+ 代碼驅動視覺動畫、3D 場景、技術解說與互動遊戲開源基準庫"
source_url: "https://github.com/yihui-dev/awesome-opus5-5-videos/tree/main"
source_platform: "GitHub"
author: "yihui-dev & Skillry Community"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: done
cluster: "2"
cluster_role: "開源剪輯與動效提示庫"
short_title: "Awesome Opus 5.5 Videos"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "README 共 132 張圖只看了 27 張（2 張主圖＋前 25 張縮圖），其餘 105 張只讀標題與技術標籤；issue 留言讀到 4 則（總數未知）"
source_images: 27
source_replies: 4
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
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`code-as-video-studio/notes/2026-10-18-prompt-motion-claude-video-showcase.md`](https://github.com/SanHsien/code-as-video-studio/blob/main/notes/2026-10-18-prompt-motion-claude-video-showcase.md)（Prompt Motion 策展庫解構）
  - [`code-as-video-studio/notes/2026-10-17-motion-prompt-animation-dictionary.md`](https://github.com/SanHsien/code-as-video-studio/blob/main/notes/2026-10-17-motion-prompt-animation-dictionary.md)（微觀動態字典）
  - [`code-as-video-studio/notes/2026-10-17-cinematic-shot-ui-film-director.md`](https://github.com/SanHsien/code-as-video-studio/blob/main/notes/2026-10-17-cinematic-shot-ui-film-director.md)（宏觀運鏡分鏡）

---

## 0. 原始資料盤點

> 2026-11-16 重審：來源是 GitHub repo，看了 README 全文、提交紀錄與 issue。README 共 132 張圖：2 張主圖逐張看過，其餘 130 張是各作品的動態預覽縮圖，實際看了前 25 張（動態圖形區），其餘只讀了標題與技術標籤，沒有逐張打開。本篇沒有對應的社群貼文。

- **作者圖片**：
  - 圖 1（主圖）：約 150 格作品縮圖拼成的牆，內容橫跨文字動畫、3D 場景、粒子、像素遊戲、圖表動畫。
  - 圖 2（主圖）：Skillry 的 Opus 5.5 影片頁截圖，每筆作品左右並排「原始影片」與「即時重製」，上方有分類與排序篩選。
  - 縮圖 1–25（動態圖形區）：多數是大字級文字動畫、數字跳動計數、UI 操作示意、波形與粒子；也有直式短影音格式（卡通角色加字幕）。每格下方標技術棧，其中數格標的是 **`Canvas · AI image`**，代表畫面用了 AI 生成的圖片當素材，不是純程式碼畫出來的。
- **作者留言補充**（維護者在 issue 的回覆）：
  - #1、#3：維護者說明**收錄標準已收緊**：只收「貼給 Opus 5.5 就能重現」的純文字提示詞；靠專用影片 skill 或流程做的、要外部 MCP 或原始素材的、沒公開提示詞的，一律不收。
  - 提交紀錄佐證：2026-10-12 一度加到 853 筆，10-13 刪掉 150 筆「不是純 Opus 5.5 提示詞做的」才變成 703 筆；先前批次的說明寫著包含 Remotion／HyperFrames 流程的作品。
  - README 自己註明：部分作者只公開了一部分提示詞，或只在貼文描述成果，該檔會標示。
- **網友留言重點**：
  - issue #11（@pnaque，未獲回覆）：點名 5 個提示詞檔**直接貼進有工具權限的 agent 會有風險**：要 agent 去 clone 短網址背後的 repo 並把裡面的規則當成「覆蓋預設」、叫 agent 不要停下來問；安裝並執行第三方起始專案；從短網址載入 Three.js；提示詞裡寫著原作者的資料夾、付費 API 金鑰與「把額度用完」；還有一則其實是要 agent 改自己的設定檔與全域指令檔。建議 README 加警語：在沙盒跑、不給金鑰、不跟短網址、不讓 agent 改自己的設定。
  - 其餘 issue 多是無內容或離題的發文，沒有實測回報。
- **對分析的影響**：
  - 修正 1.1 的星數：分析當時寫 5,700 星、近 600 fork；2026-11-16 實看是 15.5k 星、1.6k fork，已在正文加註日期。
  - 修正 1.1「703 組完整提示詞」：不是每一筆都完整，README 明說有些只有部分提示詞或只有原貼文描述，已改寫。
  - 修正 1.2 第 4 點：這批提示詞「具 Few-shot 學習價值」的說法要加上前提，**不可原樣貼給有 shell／檔案／金鑰權限的 agent**，依據是 issue #11。已在正文加註。
  - 「純程式碼、零幻覺」的說法要打折：部分作品用了 AI 生成圖片當素材（縮圖標籤可見），不是全部都由向量與著色器算出來。
  - 已關閉的 `T-20261018-07`（不做解析腳本）結論不變；issue #11 反而多一個不做的理由（整批索引給 agent 檢索前得先過濾危險提示詞）。

---

## 1. 核心內容摘要與技術深挖

### 1.1 什麼是 Awesome Opus 5.5 Videos？
`yihui-dev/awesome-opus5-5-videos` 是一個在 GitHub 上獲得超過 5,700 顆星與近 600 次 Fork 的開源專案（分析當時的數字；2026-11-16 重看是 15.5k 星、1.6k fork）。它全面收錄了全球創作者使用 **Claude Opus 5.5** 透過純文字 Prompt 生成的「**代碼驅動動態視覺作品（Code-driven Visual Creations）**」：
- **龐大資料規模**：包含 **703 筆提示詞檔（存於 `prompts/*.md` 與 `data/videos.json`）**。不是每筆都完整：README 註明部分作者只公開一部分提示詞，或只有原貼文的成果描述。維護者 2026-10-13 刪掉 150 筆不是純提示詞做出來的作品後才是 703 筆。
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
   - 專案附帶 `data/videos.json` 與標準命名之 `prompts/<creator>-<id>.md`，每份檔案包含作者原始推文、提示詞全文、使用的技術標籤（如 `Three.js · GLSL · Canvas`），具備 Agent 檢索與 Few-shot 學習價值。**使用前提**：有人在 issue #11 指出其中數筆提示詞含短網址 clone、覆蓋預設規則、原作者金鑰與額度指示、要求改 agent 自身設定等內容，不可原樣貼給有工具權限的 agent，要先人工讀過並在沙盒執行。

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

- [x] **`T-20261025-04`**｜**[優先級：高]** 實作 `assets/` 全庫 6 個單檔 HTML Generative UI 互動展示之「外部裁判（External Judge）」結構與安全驗證器
  - **目標範圍**：`tools/verify_generative_ui_assets.py` 與 `tests/test_verify_generative_ui_assets.py`
  - **具體做法**：
    1. 實作 `tools/verify_generative_ui_assets.py`（純 Python stdlib），機械化驗證 `assets/` 下全部 6 個 HTML 展示檔（`anti-slop-demo/index.html`、`target-story-editor/index.html`、`health-bank-dashboard/index.html`、`open-meteo-weather-chart/index.html`、`creative-coding-demo/threejs-particle-galaxy.html`、`openlibrary_demo/video_seek_canvas.html`）：(a) 具備合法 HTML5 `<!DOCTYPE html>`、UTF-8 charset 與非空 `<title>`；(b) 所有外部 CDN `<script src>` / `<link href>` 一律使用 `https://`（嚴禁 `http://` 明文或本機路徑 `file://` / `C:\`）；(c) `openlibrary_demo/video_seek_canvas.html` 實作 `seek` 時間函式契約；(d) `health-bank-dashboard/index.html` 不含未遮蔽真實台灣身分證字號且包含免責聲明。
    2. 撰寫 `tests/test_verify_generative_ui_assets.py`，涵蓋真實 6 個 HTML 資產全數通過，以及缺少 DOCTYPE、非安全 `http://` CDN、缺少 `seek(t)`、未遮蔽身分證之反例攔截測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_generative_ui_assets.py` 回傳 exit 0，且 `python -m pytest tests/test_verify_generative_ui_assets.py -q` 全數通過（至少 6 項測試）。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：已完成純 Python stdlib 外部裁判驗證器 `tools/verify_generative_ui_assets.py`，提供對 assets/ 下全數 6 個單檔 HTML 展示之 HTML5 Baseline、外部資源 HTTPS 安全性、`video_seek_canvas.html` 之 `seek` 函式契約、`health-bank-dashboard/index.html` 之身分證脫敏與免責聲明檢驗；並建立 `tests/test_verify_generative_ui_assets.py`（8 項測試，涵蓋真實資產全數通過與各項缺陷反例攔截），執行 `python tools/verify_generative_ui_assets.py`（exit 0）與 `pytest` 8 passed 全數綠燈通過。**搬移註記（2026-10-25）**：健康存摺儀表板與 OpenLibrary `seek(t)` 範例已分別移至 [`SanHsien/health-bank-toolkit`](https://github.com/SanHsien/health-bank-toolkit) 與 [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)，本驗證器改為只檢查留在本 repo 的 4 個 HTML。

---
