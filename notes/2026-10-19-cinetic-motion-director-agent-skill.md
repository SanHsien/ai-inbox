---
id: 2026-10-19-cinetic-motion-director-agent-skill
title: "Cinetic 動態導演 Agent Skill 解構：讓 Claude 掌握 273 種動畫技法、Remotion/GSAP 雙引擎與音畫同步節拍網格（Beat Grid）的 Code-as-Video 實踐"
source_url: "https://www.threads.com/@ethansavemoneydairy/post/DeoDwjXgGYy"
source_platform: "Threads / GitHub"
author: "Leon Lin (@Leonxlnx) / 轉載分享：pizza的存錢日記＆＆自我成長 (@ethansavemoneydairy)"
github_repo: "https://github.com/Leonxlnx/cinetic"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 2
cluster_role: "動態導演"
short_title: "Cinetic 273 種技法 + Beat Grid"
tags:
  - cinetic
  - motion-director
  - remotion
  - gsap
  - code-as-video
  - beat-grid
  - agent-skills
---

# Cinetic 動態導演 Agent Skill 解構：讓 Claude 掌握 273 種動畫技法、Remotion/GSAP 雙引擎與音畫同步節拍網格（Beat Grid）的 Code-as-Video 實踐

- **來源連結**：[Threads 原貼文 (pizza的存錢日記＆＆自我成長)](https://www.threads.com/@ethansavemoneydairy/post/DeoDwjXgGYy)（短網址：[threads.com/share/BAW0aDxKf8](https://www.threads.com/share/BAW0aDxKf8/)）｜ [官方 GitHub (Leonxlnx/cinetic)](https://github.com/Leonxlnx/cinetic)
- **發布平台 / 原作者**：`Threads / GitHub` / 原創者：`Leon Lin (@Leonxlnx)`、社群分享：`pizza的存錢日記＆＆自我成長 (@ethansavemoneydairy)`
- **分析日期**：`2026-10-19`
- **當前狀態**：`🟢 已做 (Done)`

---

## 1. 核心內容摘要

### 1.1 核心主張：讓 Coding Agent 從「寫 CSS」進化為掌控視聽節奏的「Motion Director」

過去使用 AI 輔助製作網頁動效或產品展示影片時，開發者常遇到三大障礙：
1. **AI Slop 罐頭感**：缺乏系統化的動效語彙，AI 產出的動畫往往只是單調的淡入淡出（Fade In/Out）或生硬的縮放，缺乏鏡頭感與電影質感；
2. **音畫節奏脫節（Audio-Visual Drift）**：視覺元素的動作時間點與背景音樂、音效（SFX）各自獨立，影片播到後面轉場與鼓點完全錯位；
3. **軟體工具斷層**：傳統製作產品發表短片依賴 After Effects / Premiere 等重型 GUI 軟體，無法被 Coding Agent 以程式碼自動化批次生產。

由 **Leon Lin（@Leonxlnx）** 開源的 **`Cinetic`** 專案，是一個專為 Coding Agent（如 Claude Code、Antigravity、Cursor）設計的 **Motion Director（動態導演）Agent Skill**。

它讓 AI 能夠以純程式碼（Code-as-Video）的方式，編排並渲染出高質感的產品發表片（Product Launch Films）、品牌動效與社群短影音，實現了從腳本、分鏡、技法選擇、節拍吸附到高畫質渲染的完整自動化閉環。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Cinetic「代碼動效導演」架構全景                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 創意概念先行 (Concept & Idea First)                                  │
│    └─ 3 重剪輯視角探索 ──> 確立核心視覺意象與故事節奏 (Story Device)     │
│                                                                        │
│ 2. 273 種動態技法字典 (The 273 Techniques Library)                     │
│    └─ 14 大專業類別: 文字特效、運鏡、轉場、3D 景深、UI 響應、故障 Glitch   │
│       └─ 內建 60 FPS 時間曲線 (Easing) 與構建配方 (Build Recipes)        │
│                                                                        │
│ 3. 統一節拍網格音畫同步引擎 (Unified Beat Grid Engine)                 │
│    └─ 依據音樂 BPM 與 60 FPS 計算數學網格，所有轉場與音效自動吸附 (Snap) │
│                                                                        │
│ 4. 雙渲染引擎自適應 (Dual Rendering Engines)                           │
│    ├─ Remotion (React-based): 函數式組件化渲染、生態整合度高            │
│    └─ HyperFrames (HTML/GSAP): 極致輕量效能、精準操控 GSAP Timeline      │
│                                                                        │
│ 5. 多階段視覺評審閉環 (Iterative Review Loops)                         │
│    └─ 風格定格幀 (Style Stills) ──> 分鏡聯絡印相表 ──> 最終 Master 導出  │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 關鍵技術機制深度剖析

```
[Cinetic 視聽動效生成流水線]

  +-----------------------+
  |  產品意圖 / README 輸入 | (例如: 軟體發布短片、新功能展示)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |   Concept & Script    | ===> 產出 3 組候選分鏡腳本與故事母題
  +-----------+-----------+
              |
              v
  +-----------------------+
  |  計算統一節拍網格     | ===> 解析音樂 BPM (如 128 BPM)，計算每拍幀數
  |  (Unified Beat Grid)  |      Grid Frame = (Beat * 60 * FPS) / BPM
  +-----------+-----------+
              |
              v
  +-----------------------+
  |  抽樣 273 種技法字典  | ===> 隨機/依情緒選取文字、運鏡、3D、UI 動效配方
  |  (14 Categories)      |
  +-----------+-----------+
              |
              v
  +-----------------------+
  | 雙引擎代碼生成與合成  |
  | ├─ Remotion (React)   | ===> 幀綁定 (useCurrentFrame)
  | └─ GSAP (HTML Timeline)| ===> 暫停 Timeline 並隨幀 Seek
  +-----------+-----------+
              |
              v
  +-----------------------+
  |  多階段視覺品質審核   |
  |  ├─ Style Stills 檢查 | ===> 截圖審查調色與排版
  |  └─ Contact Sheet 審核| ===> 全局節奏與轉場連貫性檢查
  +-----------+-----------+
              | (通過 QA)
              v
  +-----------------------+
  | Master Render (MP4)   | ===> 啟用動態模糊 (Motion Blur)，導出高畫質母帶
  +-----------------------+
```

1. **273 種動態技法字典（The 273 Techniques Dictionary）**：
   - 涵蓋 14 大分類：動態排版（Kinetic Typography）、鏡頭運動（Camera Moves）、畫面轉場（Transitions）、3D 景深（Depth of Field）、UI 微互動（Micro-interactions）、幾何分割、粒子流體、色調分離、噪點故障（Glitch）等。
   - 每項技法均附帶嚴格的 60 FPS 幀數區間、貝茲曲線（Cubic-bezier Easing）與圖層構建配方，杜絕 AI 臨場自由發揮導致的視覺失真。
2. **統一節拍網格（Unified Beat Grid - 音畫同步機制）**：
   - 傳統代碼影片常出現音訊歸音訊、畫面歸畫面，播放至後半段時畫面轉場比鼓點慢半秒。
   - Cinetic 以音樂的 **BPM（每分鐘拍數）** 與 **幀率（60 FPS）** 為基準，將整支影片的時間軸劃分為微秒級的「音樂節拍網格」。所有轉場、相機推拉、文字彈出與音效（SFX），均被強制約束在網格的拍點（Beat）或半拍（Off-beat）上，保證節奏卡點極度精準。
3. **Remotion 與 GSAP 雙渲染引擎適配**：
   - **Remotion**：利用 React 的宣告式組件與 `useCurrentFrame()`，將網頁組件直接轉化為每一幀的畫面，極度適合呈現 Web/SaaS 產品介面。
   - **HyperFrames / GSAP**：針對需要複雜時間軸補間的動畫，透過將 GSAP 的 Timeline 設為 `paused: true`，在渲染迴圈中根據 Remotion 幀數精確 `timeline.seek(frame / fps)`，兼具 GSAP 的強大補間能力與 Remotion 的幀確定性。
4. **多階段視覺 QA 閉環（Review Loops）**：
   - 在直接執行昂貴的整片渲染前，Cinetic 設計了「定格風格幀（Style Stills）」與「分鏡聯絡印相表（Contact Sheet）」，讓 Agent 先自我審查畫面的排版密度、顏色對比與轉場平滑度，避免渲染完成後才發現基本版型錯誤。

---

## 2. 對現有工作流與專案之啟發

1. **與已收錄視覺動效專案的技術演進串聯**：
   - 本倉庫先前已收錄 **Note 5 (`cinematic-shot`)**、**Note 9 (`motion-prompt`)**、**Note 18 (`prompt-motion`)** 與 **Note 21 (`awesome-opus5-5`)**。
   - `Cinetic` 的出現標誌著**「Code-as-Video」從 Prompt 庫邁向完整「Agent Skill 工程框架」**。它不僅包含動效字典，更給出了解決音畫同步（Beat Grid）與雙引擎渲染（Remotion/GSAP）的具體架構。
2. **為開源專案賦能「自動化發表片導演」**：
   - 未來維護者的 GitHub 專案（如 `ai-inbox` 或各類 Agent 工具）可直接導入 `Cinetic` 技能，由 Agent 讀取專案 README 與核心功能，自動生成 15~30 秒具備專業卡點與鏡頭感的產品發表預告片（Teaser Video）。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261019-03`**｜**[優先級：高]** 深度調研並拆解 `Leonxlnx/cinetic` 核心技能庫架構（273 種動態技法字典、14 大分類與 60 FPS 時間配方），整理出本地 Agent Skill 規範手冊
  - **目標範圍**：`Leonxlnx/cinetic`、本地 Agent Skills 體系
  - **完成日期**：2026-10-23
  - **驗收標準（DoD）**：產出 `docs/cinetic-motion-dictionary.md`，完整整理 14 大分類、273 種動態技法之參數結構與 60 FPS 貝茲時間配方對照表，手冊檔案存在且通過連結與結構驗證。
  - **實作紀錄 / 證據**：調研 `Leonxlnx/cinetic` 實體 repo 產出 `docs/cinetic-motion-dictionary.md`，完整涵蓋 14 大分類共 273 種技法參數、60 FPS 貝茲 (Easing) 與彈簧 (Springs) 配方、雙引擎架構指引，`python tools/verify_inbox.py` 通過。
- [x] **`T-20261019-04`**｜**[優先級：中]** 實作「音畫同步節拍網格（BPM & Beat Grid Engine）與 Remotion/GSAP 幀同步渲染流水線原型」，驗證代碼驅動短片無縫吸附節奏
  - **目標範圍**：`remotion`、`gsap`、代碼驅動視覺流水線
  - **驗收標準（DoD）**：產出 `tests/test_beat_grid.py` 與範例 Remotion/GSAP 幀同步代碼，輸入特定 BPM 自動計算拍點影格並生成吸附動畫序列，執行 `pytest tests/test_beat_grid.py` 全數通過。
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。實作節拍網格計算引擎 `tools/beat_grid.py`，撰寫 Remotion/GSAP 幀同步範例代碼 `templates/beat-grid-motion-example.ts`，並新增單元測試 `tests/test_beat_grid.py`（6 項測試全數通過，支援拍點影格、小節強拍、前奏偏移、Snap-to-Grid 吸附與卡點轉場生成）。

---

## 4. 關聯筆記與相關任務（Related Notes & Tasks）

- **Code-as-Video 動態視覺家族演進**：
  - [Prompt Motion 代碼動效視頻策展庫](./2026-10-18-prompt-motion-claude-video-showcase.md) ｜ 關聯任務：`T-20261018-01`、`T-20261018-02`
  - [Awesome Opus 5.5 Videos 提示詞動物園](./2026-10-18-awesome-opus5-5-videos-prompt-zoo.md) ｜ 關聯任務：`T-20261018-07`、`T-20261018-08`
  - [cinematic-shot UI 發表片導演技能](./2026-10-17-cinematic-shot-ui-film-director.md) ｜ 關聯任務：`T-20261017-09`、`T-20261017-10`
  - [Motion Prompt 視覺動效字典](./2026-10-17-motion-prompt-animation-dictionary.md) ｜ 關聯任務：`T-20261017-17`、`T-20261017-18`
- **前端審美與反 AI 罐頭設計**：
  - [Shipper 92 萬字元 epstein.md 反 AI 罐頭設計](./2026-10-17-shipper-epstein-md-anti-ai-slop.md) ｜ 關聯任務：`T-20261017-19`、`T-20261017-20`
  - [TasteSkill v2 得獎網站重構藝術指導](./2026-10-17-tasteskill-v2-anti-slop-frontend.md) ｜ 關聯任務：`T-20261017-21`、`T-20261017-22`

