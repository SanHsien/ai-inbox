---
id: 2026-10-17-tasteskill-v2-anti-slop-frontend
title: "TasteSkill v2：解析 247 個得獎網站重構的 AI 前端藝術指導與截圖評審閉環"
source_url: "https://github.com/Leonxlnx/taste-skill"
source_platform: "GitHub"
author: "Leon Lin (@Leonxlnx)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: 2
cluster_role: "審美防線"
short_title: "TasteSkill v2"
tags:
  - taste-skill
  - agent-skills
  - anti-slop
  - art-direction
  - frontend-ui
  - visual-review
---

# TasteSkill v2：解析 247 個得獎網站重構的 AI 前端藝術指導與截圖評審閉環

- **來源倉庫**：[GitHub - Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
- **專案作者**：`Leon Lin (@Leonxlnx / @lexnlin)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已做 (Done)`
- **授權協議**：`MIT License`

---

## 1. 核心內容摘要與技術深挖

### 1.1 痛點：AI 模型的「平均化網頁陷阱（Average Landing Page）」
- **現象**：大部分 Coding Agent 產出的網頁，本質上只是模型看過所有網頁的「加權平均數」：
  - 置中三行大標題 + 上方小標籤（Tagline badge）。
  - 三張帶圖示的特性卡片（Icon cards）。
  - 柔和的藍紫漸層或微弱陰影。
  - 底部孤零零的單調定價表與 CTA。
- **痛點本質**：這類頁面「沒有任何一處是錯的，但也**沒有任何一處是經過設計決策的**」。更重要的是，若只是一味拿掉陰影和卡片（負向約束），往往會讓網頁顯得空洞單薄（Thin page），反而輸給有內容的平庸頁面。

### 1.2 TasteSkill v2 的解法：以實質內容取代裝飾，六步藝術指導流程
高中生 Creative AI 開發者 Leon Lin 深入研究了 **247 個 One Page Love 與 Awwwards 得獎網站**，將 TasteSkill v2 完全從零重寫，捨棄了 v1 時代的數值旋鈕，改為**嚴格的 6 階段決策與審查流水線**：

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   TasteSkill v2 端到端藝術指導管線                      │
└────────────────────────────────────────────────────────────────────────┘

    [客戶需求 Brief]
           │
           ▼
    ┌───────────────────────────────────┐
    │ 1. 主體資產清單 (Subject Inventory) │ (挖掘 8~12 項客戶獨有特徵：歷史、地點、
    │                                   │  產量限制、數字、特定材質、作息時間)
    └──────────────────┬────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────┐
    │ 2. 爭點論證寫作 (Argument Writing)│ (以 Claim + Proof 定義各 Section 存在價值，
    │                                   │  無有力論據的區塊直接砍除，拒絕罐頭順序)
    └──────────────────┬────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────┐
    │ 3. 抽樣設計方向 (Draw Direction)   │ (`scripts/draw.mjs` 從 20 種得獎方向抽出 3 個，
    │                                   │  由 Agent 選出最能承載客戶特徵的構圖方案)
    └──────────────────┬────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────┐
    │ 4. 開放典藏資產 (Open Assets)     │ (`scripts/assets.mjs` 檢索 Wikimedia,
    │                                   │  Openverse, The Met 公共領域真實影像並標記出處)
    └──────────────────┬────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────┐
    │ 5. 代碼建構 (Build Framework)     │ (Tailwind / React / Svelte / HTML，
    │                                   │  放大字級、大塊純色、豐富圖文充實內容)
    └──────────────────┬────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────┐
    │ 6. 真實瀏覽器截圖評審 (Inspect)   │ (`scripts/inspect.mjs` 在 Chrome/Edge 跑
    │                                   │  390px/820px/1440px 截圖，比對評審準則，
    │    ┌─ 發現 AI Slop ──> 修前三大問題│  自動修改，最多跑 3 輪循環)
    │    └─ 通過審查 ──────> 交付高品質頁面
    └───────────────────────────────────┘
```

### 1.3 核心技術特點
1. **抽樣而非憑空發想（`draw.mjs`）**：
   - 解決模型無腦偏好「科技類預設」的問題。腳本從 20 種經過驗證的藝術方向中隨機 Deals 出 3 種，強迫 Agent 根據客戶主體特徵進行比對選擇。
2. **真實公共影像授權檢索（`assets.mjs`）**：
   - 拒絕未經授權的網圖或虛假 AI 假圖；自動從 Wikimedia Commons、Openverse、The Met（大都會博物館）等開放典藏提取 CC0 / 公共領域的高解析真實影像，並自動在頁尾生成真實授權出處。
3. **無人值守真實瀏覽器三寬度審查（`inspect.mjs`）**：
   - 需要 Node 22+ 與本機 Chrome / Edge / Chromium。
   - 分別在 **手機 (390px)**、**平板 (820px)**、**桌面 (1440px)** 三種寬度拍攝真實渲染截圖。
   - 透過視覺評審標準（Juror's Rubric）抓出排版跳行、對齊破綻、文字擁擠與罐頭老套路，自動修復前三大最嚴重缺陷，迭代最多 3 輪。
   - 單次完整構建與驗收耗時約 30～45 分鐘，消耗數十萬 Tokens，專為頂級高品質展示頁而生。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與 `epstein.md`（負向約束）互補**：
    - [`notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md`](./2026-10-17-shipper-epstein-md-anti-ai-slop.md) 指出了「不要做什麼（No shadows, No blue-purple gradients）」。
    - `TasteSkill v2` 則給出了「**要做什麼（加大字級、大塊純色、真實檔案影像、爭點論證區塊）**」以及「**如何自我驗收（3 寬度截圖評判）**」。
  - **與 `motion-prompt` / `cinematic-shot` 形成極致前端矩陣**：
    1. **`TasteSkill v2`**：掌控整體網頁的「靈魂概念、區塊論證與版面藝術指導」。
    2. **`epstein.md`**：擔任守門員「消除罐頭陰影與模型廢話」。
    3. **`motion-prompt`**：賦予個別元件「120 款純數學微觀動效」。
    4. **`cinematic-shot` / `Reelbird`**：負責最後的「運鏡展示與自動錄影分享」。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **「主體清單盤點（Subject Inventory）」思維**：在寫任何 Landing Page 或產品頁之前，強制條列 8~12 項「只有這家客戶/專案具備的特徵」，徹底杜絕千篇一律的通用模板感。
    2. **「爭點論證（Argument Writing）」順序法**：按「主張與證據（Claim & Proof）」規劃網頁區塊，而非盲目套用 Hero -> Features -> Pricing。
    3. **多寬度截圖與自我修正循環（Screenshot Juror Loop）**：將截圖反思機制納入 `verification-protocol`，大幅提升前端程式碼的驗收水準。
  - **需注意的部分**：
    - TasteSkill v2 專為**公開展示頁、產品官網、作品集**設計，不適用於高密度後台儀表板或 SaaS 數據應用（後者應使用 `minimalist-ui` 或標準組件庫）。
    - 完整運行耗時 30-45 分鐘且消耗數十萬 Token，日常快速開發可按需擷取其「主體盤點」與「截圖審查腳本」，而非每次都全量跑滿。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-21`**｜**[優先級：高]** 測試並整合 `taste-skill` v2 核心工具鏈（`draw.mjs` 與 `inspect.mjs`）至本地前端驗收環境
  - **目標範圍**：`C:\GitHub\ai-inbox\notes\` 與前端驗收工具鏈
  - **完成日期**：2026-10-23
  - **具體實作步驟**：
    1. 檢驗本地環境 Node.js 版本（需 Node 22+）與 Chrome/Edge 瀏覽器執行路徑。
    2. 提取 `Leonxlnx/taste-skill` 中的 `inspect.mjs` 截圖與 Slop 檢查核心邏輯，測試在 Windows 11 下透過 Playwright 或 Puppeteer 執行 3 寬度截圖（390px, 820px, 1440px）。
    3. 驗證截圖產出品質與自動錯誤分析報告。
  - **驗收標準（DoD）**：在本地成功對一個靜態 Web 頁面執行 `inspect.mjs`，並產出三個斷點的完整無破綻截圖。
  - **實作紀錄 / 證據**：完成沙盒安全審查（零 npm 外部依賴、無惡意二進位、無提權）並置於 `C:\GitHub\_sandbox\taste-skill\`。實測 `draw.mjs` 成功生成 3 種風格佈局推薦；實測 `inspect.mjs` 藉由 Windows 原生 Chrome/Edge CDP 驅動無頭渲染，針對 `assets/anti-slop-demo/index.html` 成功生成 1440px / 768px / 390px 完整截圖（包含 fold 與 page）及結構化 report.json，精確指出 anti-slop 缺失（mono 字型誤用、outline box 等 8 FAIL / 8 WARN）。

- [x] **`T-20261017-22`**｜**[優先級：中]** 建立「主體資產盤點 (Subject Inventory) 與論證寫作」前端設計前置 Prompt 範本
  - **完成日期**：2026-10-23
  - **目標範圍**：全域前端技能庫 / Prompt 範本庫
  - **具體實作步驟**：
    1. 將 TasteSkill v2 的「8~12 項獨有主體特徵盤點」與「Claim + Proof 區塊論證」整理為繁體中文結構化模板。
    2. 設計互動步驟：要求 Agent 在開始寫 HTML/Tailwind 代碼前，先輸出這份論證清單供使用者確認。
    3. 整合進日常 Web 開發與 Landing Page 生成工作流。
  - **驗收標準（DoD）**：隨機給定一個新產品主題（如「本地小農精品咖啡」），Agent 能依照範本精準產出不含通用套路的區塊論證結構。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `templates/subject-inventory-argument-writing-prompt.md`，完整制定 8~12 項獨有主體資產盤點協定與 Claim + Proof 區塊論證流程，並以「阿里山高海拔小農精品水洗咖啡」完成端到端不含罐頭模板的實戰示範。
