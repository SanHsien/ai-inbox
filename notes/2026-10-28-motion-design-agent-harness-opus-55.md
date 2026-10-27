---
id: 2026-10-28-motion-design-agent-harness-opus-55
title: "代碼驅動 Motion Design Agent 架構：以 Harness 取代 Prompt、seek(t) 時間函式與分鏡自審循環"
source_url: "https://www.threads.com/share/LYKSz64yr/"
source_platform: "Threads (@0xalpha.ai)"
author: "0xalpha.ai"
analyzed_at: 2026-10-28
analyzed_by: "Antigravity"
status: pending
cluster: 1
cluster_role: "開發流程"
short_title: "0xalpha 動態設計 Agent Harness 架構"
tags:
  - motion-design
  - agent-harness
  - claude-code
  - opus-55
  - playwright-ffmpeg
  - anti-slop
  - seek-time-function
  - contact-sheet-scoring
---

# 代碼驅動 Motion Design Agent 架構：以 Harness 取代 Prompt、seek(t) 時間函式與分鏡自審循環

- **來源連結**：[Threads 原文分享 (@0xalpha.ai)](https://www.threads.com/share/LYKSz64yr/) ｜ [貼文永久網址 (Threads @0xalpha.ai)](https://www.threads.net/@0xalpha.ai/post/DeMLz-KD1EE)
- **核心作者**：0xalpha.ai（AI 生成動效與 Agent Harness 工程實踐者）
- **分析主題**：Opus 5.5 / Claude Code 在動態設計（Motion Design）領域的工程躍遷、以確定性 Harness 取代虛浮 Prompt、將影片視為純時間函式 $\text{Frame} = f(t)$ 與 `seek(t)` 任意時點快照、工作室 CLAUDE.md 禁用老套罐頭（Anti-Slop）、渲染前縮圖總覽（Contact Sheet）自審打分循環、以及 Effort 等級分層策略
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（Going Li 五路工具流：ROAD 01 影片工廠與多比例輸出）
  - [`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)（Thorsten Ball 15 條 Agent 實戰哲學：為 Agent 打造試錯工具與無可辯駁證據）
  - [`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md)（Karpathy 四大黃金原則工程加固：精確定位與防盲目嘗試）
  - [`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](./2026-10-26-ai-shared-memory-template-team-collaboration.md)（AI 共用記憶系統三跳索引與動詞寫入契約）

---

## 1. 核心內容摘要：Harness 架構與動態設計工作室（Executive Summary）

在 AI 視覺與影片生成領域，傳統生成式影片模型（如文字生影片 Video Gen）面臨致命的痛點：**隨機性過高、關鍵幀無法精確控制、品牌標誌與產品截圖失真、文字難以清晰排版**。

0xalpha.ai 在 Threads 上展示了透過程式碼驅動（Code-driven Motion Design）的高品質影片工作流，獲得社群高度矚目（50K+ 瀏覽、700+ 讚），並一語道破工程本質：
> **「同一個 Opus 5.5，有沒有接上 motion design 的流程，表現差超多。裸用是一個樣，放進設計好的 harness 裡又是另一個樣。重點是 harness，不是 prompt。」**

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     0xalpha.ai 代碼驅動 Motion Design Agent Harness 全貌                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  [ 人類輸入 ] ──(丟入產品網址 / 品牌規範)                                                       │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ Claude Code (Opus 5.5) ]                                                                     │
│  ├─ 工作室規範 (CLAUDE.md) ──► 禁用視覺老套罐頭 (漸層+置中、全淡入、角落標籤)                   │
│  ├─ 品牌素材自動獲取 ───────► 真實截圖、SVG Logo、官方配色 Hex                                  │
│  └─ 代碼化動效定義 ─────────► 影片即時間函式：Frame = f(t)，支援任意 seek(t) 精確渲染            │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 本地執行環境 (Harness Tooling) ]                                                             │
│  ├─ Node.js (Web/Canvas/SVG/GSAP 動效腳本)                                                      │
│  ├─ Playwright (無頭瀏覽器精確渲染與時間跳轉截圖)                                               │
│  └─ ffmpeg (最終視訊合流、高畫質轉碼與音畫同步)                                                 │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 渲染前自審打分循環 (Pre-render Self-Critique Loop) ]                                         │
│  ├─ 輸出縮圖總覽 (Contact Sheet / Storyboard) 涵蓋各關鍵時點                                    │
│  ├─ Agent 自我打分 (1–10 分)，挑出最差的 3 個分鏡                                               │
│  └─ 針對性修改並重新驗收，直到所有分鏡皆達 8 分以上                                             │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 最終高畫質導出 (ffmpeg Export) ] ──► 封裝成可複用 Skill，下一支影片一句話搞定                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 深入技術拆解：五大核心實戰原則（Deep Dive）

### 2.1 原則一：以「確定性 Harness」取代「機率性 Prompt」
- **裸用模型 vs 工具線束（Harness）**：
  - 單純透過 Prompt 向模型索求「幫我做一段炫酷的動效」，模型只能在文字層面給予抽象建議或寫出未經實測的片段代碼。
  - 建立專屬 Harness：在本機環境安裝 **Node.js、ffmpeg、Playwright**。Agent 不僅負責構思分鏡，更能直接運行腳本、操作 Playwright 截圖並調用 ffmpeg 編碼，形成**「撰寫代碼 $\rightarrow$ 本機渲染 $\rightarrow$ 截圖審查 $\rightarrow$ 迭代優化」**的閉環。

### 2.2 原則二：影片是時間的純函式：$\text{Frame} = f(t)$ 與 `seek(t)`
- **動畫架構數學模型化**：
  - 將整支影片嚴格定義為時間參數 $t$（毫秒或幀數）的純函式：
    $$\text{Canvas / DOM State} = f(t)$$
  - 核心介面契約：`seek(t)`。
    任何外部工具或 Agent 只要給定時間 $t$，動效腳本必須立即、無副作用地繪製出該時刻的確切畫面。
- **巨大的工程優勢**：
  - 無需從頭到尾播放視訊即可在數毫秒內抽取任一時間點的畫面。
  - 為 Playwright 自動化測試與視覺迴歸審查提供了確定性的物理基礎。

### 2.3 原則三：CLAUDE.md 作為「工作室規範」：明文禁止老套視覺罐頭（Anti-Slop）
- **根除 AI 視覺罐頭特徵**：
  - 許多 AI 生成的網頁與影片呈現強烈的「模型塑料感（AI Slop）」。0xalpha.ai 在專案的 `CLAUDE.md` 中白紙黑字寫入視覺黑名單：
    1. ❌ 漸層背景＋置中粗體標題；
    2. ❌ 全部元素同一時間淡入（Fade In）；
    3. ❌ 角落呆板小標籤與生硬邊框。
- **導入專業動效語法**：
  - 強制要求使用物理彈簧動畫（Spring Physics / Stiffness & Damping）、錯落進場（Staggered Timings）、視差層次（Parallax）、真實產品高解析截圖與精確品牌色。

### 2.4 原則四：縮圖總覽自審評分循環（Storyboard Contact Sheet Scoring）
- **避免無效的全片渲染**：
  - 完整視訊的高解析度編碼極為耗時且浪費資源。
  - 在調用 ffmpeg 正式導出前，Agent 必須先透過 Playwright 的 `seek(t)`，抽取整支影片等間隔（或關鍵轉場點）的畫面，拼接成一張**縮圖總覽（Contact Sheet）**。
- **機械自審協議**：
  - Agent 讀取該縮圖，對各分鏡進行 1–10 分的客觀評分；
  - 自動標記並剔除評分最低的 3 個鏡頭，針對性修訂動效代碼；
  - **門檻標準**：全部分鏡評分達 8 分以上，方可啟動 ffmpeg 終端渲染。

### 2.5 原則五：Effort 思考等級分層與 Skill 封裝
- **算力與推理成本分級（Effort Routing）**：
  - 小修與局部調整：`medium`
  - 全新影片創作：`xhigh`
  - 發表會或旗艦開場大片：`max`
- **成果封裝**：
  - 將這套包含 Playwright、seek(t) 介面、CLAUDE.md 規範與自審打分的整套流程打包成專屬 Agent Skill（`motion-design`），使後續創作達到「一句話派工」的工業級標準。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`ai-inbox` / `agent-assets` / `generative_ui`）的整合機會**：
  1. **Generative UI 與動態資產規範升級**：
     - 現有 `assets/anti-slop-demo/` 已具備靜態 Anti-Slop 規範；引進 0xalpha 的 `seek(t)` 概念，可將動效展示擴展至時間維度。
  2. **自動化分鏡審查工具**：
     - 開發基於 Playwright 的縮圖總覽產生與靜態審查腳本，為視覺類任務建立客觀的外部裁判。
  3. **標準化 Motion Design Skill 範本**：
     - 產出專屬的 `motion-design-studio-skill.md` 模板，收錄進 `templates/`。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261028-16`**｜**[優先級：高]** 撰寫「代碼驅動 Motion Design Agent 工作室規範指南」收錄於 `docs/code-driven-motion-design-studio-spec.md`
  - **目標範圍**：`docs/code-driven-motion-design-studio-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 定義 Node + Playwright + ffmpeg 三位一體 Harness 執行環境標準。
    2. 詳細定義時間函式契約 $\text{Frame} = f(t)$ 與 `seek(t)` API 規範。
    3. 列出視覺設計 Anti-Slop 黑名單（禁用漸層置中、齊頭淡入等）與專業動效標準（彈簧物理、錯落時序）。
    4. 制定渲染前 Contact Sheet 評分協議與 Effort 分層路由指南。
  - **驗收標準（DoD）**：產出 `docs/code-driven-motion-design-studio-spec.md`，內含 Harness 架構圖、seek 介面規格、Anti-Slop 檢查表與分鏡自審流程；以 `Test-Path docs/code-driven-motion-design-studio-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261028-17`**｜**[優先級：中]** 實作「Playwright + seek(t) 動畫縮圖總覽與自審打分工具」於 `tools/audit_motion_storyboard.py`
  - **目標範圍**：`tools/audit_motion_storyboard.py` 與 `tests/test_audit_motion_storyboard.py`
  - **具體做法**：
    1. 實作命令列工具，透過 Playwright 載入 HTML/Canvas 動效檔，調用 `seek(t)` 抽取關鍵影格。
    2. 生成 Contact Sheet 縮圖總覽並進行基礎對比度、排版重疊度與 Anti-Slop 特徵機械檢測。
    3. 撰寫單元測試驗證 seek(t) 調用與縮圖生成合規性。
  - **驗收標準（DoD）**：產出 `tools/audit_motion_storyboard.py` 與單元測試，執行 `python -m unittest discover -s tests` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261028-18`**｜**[優先級：低]** 產出標準化「Motion Design Studio CLAUDE.md / Skill 範本」收錄於 `templates/motion-design-studio-skill.md`
  - **目標範圍**：`templates/motion-design-studio-skill.md`
  - **具體做法**：
    1. 產出可直接供專案引入的動態設計專案 CLAUDE.md 與 Skill 定義。
    2. 內含工作室執行規則、品牌色注入流程、ffmpeg 壓縮參數與 8 分門檻自檢指令。
  - **驗收標準（DoD）**：產出 `templates/motion-design-studio-skill.md`，具備完整中文說明與程式碼範本；以 `Test-Path templates/motion-design-studio-skill.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 協同與產出路徑**：
  - [Going Li 四 Agent 派工協定與五路工具流](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md) ｜ 關聯任務：`T-20261028-10`、`T-20261028-11`
  - [Thorsten Ball 15 條 Agent 實戰哲學](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md) ｜ 關聯任務：`T-20261028-04`、`T-20261028-05`
- **規範工程與防罐頭**：
  - [Karpathy 版 CLAUDE.md 四大黃金原則工程加固](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md) ｜ 關聯任務：`T-20261028-01`、`T-20261028-02`
- **共用記憶與跨端沉澱**：
  - [AI 共用記憶系統全景分析](./2026-10-26-ai-shared-memory-template-team-collaboration.md) ｜ 關聯任務：`T-20261026-23`、`T-20261026-24`
