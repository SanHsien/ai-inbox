---
id: 2026-10-20-public-apis-free-open-resources
title: "Public APIs 開源清單解構：47 萬 Star 免費 API 大補帖、AI Agent 零金鑰資料獲取與 Generative UI 即時數據串接實踐"
source_url: "https://www.kocpc.com.tw/archives/667830"
source_platform: "電腦王阿達 / GitHub"
author: "電腦王阿達 (Rocky) / public-apis 社群"
github_repo: "https://github.com/public-apis/public-apis"
analyzed_at: 2026-10-20
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 3
cluster_role: "公開資料"
short_title: "Public APIs 免費 API 資源庫"
tags:
  - public-apis
  - free-apis
  - agent-tools
  - generative-ui
  - api-directory
---

# Public APIs 開源清單解構：47 萬 Star 免費 API 大補帖、AI Agent 零金鑰資料獲取與 Generative UI 即時數據串接實踐

- **來源連結**：[電腦王阿達專文介紹](https://www.kocpc.com.tw/archives/667830) ｜ [public-apis/public-apis (GitHub)](https://github.com/public-apis/public-apis)
- **發布平台 / 原作者**：`電腦王阿達 / GitHub` / `電腦王阿達 (Rocky) / public-apis 社群`
- **分析日期**：`2026-10-20`
- **當前狀態**：`🟢 已做 (Done)`

---

## 1. 核心內容摘要

### 1.1 核心主張：解決 AI Agent「有邏輯無資料」的痛點，建立公開 API 探索入口

在現代 AI 輔助軟體開發（AI-Driven Development）中，開發者常透過 Agent（如 Claude Code, Codex, Antigravity, Cursor）快速產出前端介面、小工具或資料儀表板。然而，常見的卡關點在於：**工具架構做出來了，但缺乏真實即時數據來源（Live Data Source）**，只能被迫使用靜態假資料（Mock Data）。

**Public APIs**（GitHub 累積超過 47 萬 Star，集體維護）將散落在網路上的各類公開 API 集中分類整理，涵蓋數十種領域：
1. **多維度分類覆蓋**：天氣、金融、遊戲、新聞、地圖、音樂、AI、書籍、加密貨幣、匯率、開發工具、食物、政府公開資料、機器學習、科學、交通等；
2. **標準化元資料標注**：
   - **功能說明（Description）**：簡述資料內容與使用情境；
   - **驗證方式（Auth）**：`No`（完全免 Key/免 OAuth，直接存取）、`apiKey`、`OAuth`；
   - **HTTPS 支援**：明確標注是否具備傳輸層加密；
   - **CORS 支援**：標注 `Yes` / `No` / `Unknown`，直接決定瀏覽器端（前端 / Generative UI）能否跨域直連；
3. **高頻推薦核心 API**：
   - **Open-Meteo**：高品質全球天氣預報資料，完全免 Key 且免商業授權阻礙；
   - **PokéAPI**：完整寶可夢圖鑑、屬性與數值，適合原型展示；
   - **Dog CEO**：隨機犬類圖片與品種目錄，適合影像測試；
   - **Open Library**：全球書籍檢索與元資料；
   - **Free Dictionary API**：英文詞彙釋義、發音音訊與詞性分析；
   - **JSONPlaceholder**：RESTful 增刪改查（CRUD）虛擬端點，適合 API 流程調試。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Public APIs 架構與 Agent 資料獲取流程                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 需求識別 (Intent Matching)                                          │
│    └─ 使用者：「做一個天氣看板 / 查詢書籍的小工具」                   │
│                                                                        │
│ 2. 條件篩選 (Constraint Filtering)                                     │
│    ┌────────────────┬──────────────┬──────────────┬──────────────────┐ │
│    │ API 名稱       │ 驗證 (Auth)  │ HTTPS        │ 跨域 (CORS)      │ │
│    ├────────────────┼──────────────┼──────────────┼──────────────────┤ │
│    │ Open-Meteo     │ No (免金鑰)  │ Yes (加密)   │ Yes (支援前端直連)│ │
│    │ Open Library   │ No (免金鑰)  │ Yes (加密)   │ Yes (支援前端直連)│ │
│    │ JSONPlaceholder│ No (免金鑰)  │ Yes (加密)   │ Yes (支援前端直連)│ │
│    └────────────────┴──────────────┴──────────────┴──────────────────┘ │
│                                                                        │
│ 3. 落地執行 (Agent Code Generation & Live Data Binding)                │
│    └─ 直接注入 fetch/axios 呼叫，無需使用者申請 API Key 或處理代理伺服器 │
│    └─ 生成 Generative UI / HTML Artifact 即時可視化互動圖表            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 對現有工作流與專案之啟發

### 2.1 與已有資產的對應與查證

1. **GitHub Fork 資產對應（`SanHsien/public-apis`）**：
   - 個人 GitHub 遠端已具備完整 Fork 儲存庫：[`SanHsien/public-apis`](https://github.com/SanHsien/public-apis)（fork 自 `public-apis/public-apis`）。
   - 所有索引抽取、結構化快取、或專案客製化分類標籤，可直接基於已有 Fork `SanHsien/public-apis` 進行維護與落地，確保資產版本可控且無對外依賴風險。

2. **與 Generative UI / HTML Artifacts 的無縫結合**：
   - 本地環境具備 `generative_ui` 技能（`~/.gemini/antigravity/builtin/skills/generative_ui`），能生成單檔 HTML/Canvas/React 互動元件；
   - 傳統 Generative UI 常受限於靜態寫死的資料陣列；若能結合 Public APIs 中 `Auth: No` + `CORS: Yes` 的即時端點（如 Open-Meteo 氣溫風速、Free Dictionary 單字釋義），即可在聊天視窗內瞬間產出具備即時網路數據連線功能的微型應用（Live Generative Widgets）。

3. **與 Agent 原生工具鏈的互補**：
   - [CLI-Anything](./2026-10-18-cli-anything-agent-native-computer-use.md) 與 [REA 逆向工程](./2026-10-19-rea-reverse-engineer-anything-agent.md) 專注於軟體控制與結構分析；
   - `public-apis` 則提供了「公開世界數據層（Public World Data Layer）」，為 Agent 提供免申請、零金鑰的外掛數據能力。

### 2.2 落差與採納判斷

- **值得採納的部分**：
  - 精選「免金鑰（Auth: No）」且「支援前端跨域（CORS: Yes）」的公開 API 形成本地專題清單，作為 Agent 撰寫 Demo / Prototype 時的標準數據來源；
  - 避免傳統開發時頻繁在申請 API Key、處理信用驗證與跨域代理上耗費時間。
- **注意事項與限制**：
  - 「免費不等於無限量」：多數免費 API 設有 Rate Limit（如每小時 100~500 次請求）或隨時有服務終止（Deprecation）風險；
  - 生產環境（Production）仍應使用具 SLA 保障之官方付費服務，Public APIs 應嚴格定位於「原型驗證、AI 概念展示、測試資料與教學練習」。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261020-01`**｜**[優先級：高]** 建立「Public APIs 本地離線索引與免金鑰 API 篩選腳本（`tools/public_apis_indexer.py`）」，抽取無須 Key（Auth: No）且支援 CORS 的端點清單，產出 Agent 快速查閱手冊
  - **目標範圍**：`SanHsien/public-apis`、`tools/public_apis_indexer.py`
  - **具體做法**：撰寫 Python 腳本解析已有 Fork `SanHsien/public-apis` 倉庫之 README 或 raw markdown，過濾出 `Auth: No` 且 `CORS: Yes` 的高品質免費 API，輸出分類 Markdown 手冊，供 Agent 開發時一鍵按類別（天氣、書籍、金融、百科、測試資料等）精準引用
  - **驗收標準（DoD）**：腳本能成功解析並生成結構化索引，涵蓋至少 10 大常用類別，且實測至少 3 個端點（如 Open-Meteo、PokéAPI、Open Library）可直接 `curl` 回傳有效 JSON
  - **完成日期**：2026-10-22
  - **實作紀錄 / 證據**：實作 tools/public_apis_indexer.py（單純 Python 標準庫）與 tests/test_public_apis_indexer.py（單元測試通過）；解析 SanHsien/public-apis README 產出 docs/free-public-apis.md，抽取 462 筆 Auth: No 且 CORS: Yes 之 API，涵蓋 42 個類別；實測 curl Open-Meteo、PokéAPI 與 Open Library 端點均成功回傳有效 JSON。
- [x] **`T-20261020-02`**｜**[優先級：中]** 封裝「Public APIs 動態檢索 Skill / MCP 伺服器規格」，讓 Agent 能依專案需求自動查詢合適的公開 API 並生成 Generative UI 串接代碼
  - **目標範圍**：`~/.gemini/config/skills/` 或本地 MCP 外掛規格
  - **具體做法**：設計 `public-apis-search` 技能規格與 Prompt 範本，定義 Agent 在接收到使用者「做一個天氣/圖書/字典小工具」指令時，自動比對 `public-apis` 推薦清單、確認 CORS/Auth 限制，並直接生成具備 Live Data 抓取能力的前端或腳本
  - **驗收標準（DoD）**：產出完整的 Skill 規格草案與 1 個端到端測試範例（以 Open-Meteo 氣象資料在單檔 HTML 中即時渲染氣溫圖表）
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。撰寫 Public APIs 動態檢索 Skill 規格 `templates/public-apis-search-skill.md`（定義 Auth: No、CORS: Yes 與 HTTPS 三道門檻及 MCP 工具），並實作端到端單檔 HTML 氣溫圖表 `assets/open-meteo-weather-chart/index.html`（直連 Open-Meteo 免金鑰 API 即時繪製 48 小時氣候趨勢、Chart.js 4.4.1、多城市切換與容錯降級）。

---

## 4. 關聯筆記與相關任務（Related Notes & Sessions）

- **Agent 原生工具鏈與數據感知**：
  - [REA 逆向工程 MCP Server](./2026-10-19-rea-reverse-engineer-anything-agent.md) ｜ 關聯任務：`T-20261019-09`、`T-20261019-10`
  - [CLI-Anything：將任意軟體升級為 Agent-Native CLI](./2026-10-18-cli-anything-agent-native-computer-use.md) ｜ 關聯任務：`T-20261018-11`、`T-20261018-12`
  - [desktop-sense：本機螢幕即時視覺感知](./2026-10-18-desktop-sense-local-screen-context.md) ｜ 關聯任務：`T-20261018-05`、`T-20261018-06`
  - [Agent-Reach：跨平台社媒熱點與情報獲取工具包](./2026-10-17-agent-reach-social-intelligence.md) ｜ 關聯任務：`T-20261017-05`、`T-20261017-06`
- **Generative UI 與前端互動**：
  - [靶心人故事編輯器 Generative UI](./2026-10-18-target-story-generative-ui-editor.md) ｜ 關聯任務：`T-20261018-03`、`T-20261018-04`
  - [健保快易通 HTML 轉化 Claude Artifact Dashboard](./2026-10-18-health-bank-html-claude-artifact-dashboard.md) ｜ 關聯任務：`T-20261018-13`、`T-20261018-14`
