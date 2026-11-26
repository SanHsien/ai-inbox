---
id: "2026-11-26-un-system-data-commons-google-mcp"
title: "UN System Data Commons（`data.un.org`）評析：Google Data Commons 驅動之 26 機構 AI-Ready 知識圖譜與 MCP 接入"
source_url: "https://blog.google/innovation-and-ai/technology/ai/google-un-data-commons-platform/"
source_platform: "Google Blog / UN System Data Commons (data.un.org)"
author: "Prem Ramaswami (Head of Data Commons, Google) / UN Statistics Division"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 1
source_replies: 0
source_reviewed_at: "2026-11-26"
source_review_note: "已透過內建瀏覽器完整閱讀 blog.google 公告全文（含主視覺圖與 2 支嵌入影片）及 data.un.org（首頁、Explore 12 主題、Partners 26 實體、Build/Connect 與 MCP/REST 入口），並以 gh api 查證 datacommonsorg/agent-toolkit 與 MafiAtUN/un-data-commons-field-guide。"
status: pending
cluster: 3
cluster_role: "UN統計MCP知識圖譜"
short_title: "UN數據圖譜與MCP評析"
tags:
  - data-commons
  - un-data
  - knowledge-graph
  - mcp
  - public-apis
  - open-data
---

# UN System Data Commons（`data.un.org`）評析：Google Data Commons 驅動之 26 機構 AI-Ready 知識圖譜與 MCP 接入

- **官方平台**：[`data.un.org`](https://data.un.org/)（UN System Data Commons，支援英文，舊版保留於 `data.un.org/legacy`）
- **官方公告**：[`blog.google/innovation-and-ai/technology/ai/google-un-data-commons-platform/`](https://blog.google/innovation-and-ai/technology/ai/google-un-data-commons-platform/)（`2026-09-17`，作者 Prem Ramaswami）
- **MCP / REST 官方文件**：[`undatacommons-mcp`](https://projects.officialstatistics.org/undata2/undatacommons-mcp/) ｜ [`inspecting-the-graph-with-rest`](https://projects.officialstatistics.org/undata2/undatacommons-mcp/inspecting-the-graph-with-rest/)
- **相關開源工具**：[`datacommonsorg/agent-toolkit`](https://github.com/datacommonsorg/agent-toolkit)（`Apache-2.0`，`149` stars）｜ [`MafiAtUN/un-data-commons-field-guide`](https://github.com/MafiAtUN/un-data-commons-field-guide)
- **分析日期**：`2026-11-26`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/free-public-apis.md`](../docs/free-public-apis.md)（本庫免費公開 API 資源總表目標文件）
  - [`notes/2026-10-20-public-apis-free-open-resources.md`](./2026-10-20-public-apis-free-open-resources.md)（開源免費 API 盤點與實作基準）

---

## 0. 原始資料盤點（平台規模、架構與 MCP / REST 接入）

- **核心目標與資料規模**：
  - 由聯合國系統與 Google（開源 Data Commons 技術）及 Google.org（資助聯合國基金會）合作推出，將分散於各聯合國機構的統計資料整合為單一 **AI-ready 知識圖譜**，統一指標定義、時間軸與地理邊界。
  - **26 個聯合國系統實體已納入**：涵蓋 WHO、UNICEF、UNDP、UNEP、UNESCO、UNHCR、WFP、ILO、ITU、UNCTAD、UN Women、UN DESA、UNAIDS 等；站內 Explore 分 12 大主題（Health `752`、Economic Development `496`、Children & Youth `278`、Climate `262` 等，合計列出 `2,796` 筆主題指標項目），另設 **SDGs**（17 項永續目標）與 **ABAS**（小島嶼發展中國家 7 領域）專區；目標於 **2027 年涵蓋 80% 聯合國系統統計資料集**。
- **人類與 AI 雙重介面**：
  1. **Web 自然語言與視覺化**：`data.un.org` 提供日常語言提問（如南亞孕產婦死亡率、潔淨水覆蓋率）、互動式圖表／地圖、**一鍵匯出 CSV**，以及**每筆數字皆可追溯回原始官方來源（Trace every number）**。
  2. **MCP 與 REST API（Agent 直連）**：透過開放標準 **Model Context Protocol (MCP)** 與 REST 端點，Agent 可執行 `search_indicators`（語意對應標準統計變數）、擷取時間序列與地理觀測值（observations）及中繼資料（metadata）；官方亦提醒**引用關鍵數字前仍應複核原始來源**。

---

## 1. 與本專案現有架構的對照與啟發

- 本庫 [`docs/free-public-apis.md`](../docs/free-public-apis.md) 已收錄各類免費公開 API，但缺少具備**官方統計背書＋知識圖譜對齊＋原生 MCP 工具介面**的宏觀數據來源。
- **UN System Data Commons + `datacommonsorg/agent-toolkit`** 可直接作為本機研究型 Agent 查詢全球衛生、經濟、人口、氣候與 SDG 指標的一手資料來源，避免 Agent 透過一般搜尋引擎抓到過時或二次轉述的統計數字。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261126-06`**｜**[優先級：低]** 將 UN System Data Commons（`data.un.org`）、官方 MCP／REST 文件入口與 `datacommonsorg/agent-toolkit` 補入 `docs/free-public-apis.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\free-public-apis.md`（收錄於集群 3）
  - **執行步驟**：
    1. 在 `docs/free-public-apis.md` 的開放資料／統計分類新增 **UN System Data Commons (`data.un.org`)** 條目，註明涵蓋 26 個 UN 實體、12 大主題、支援 CSV 匯出與出處溯源。
    2. 附上官方 MCP 文件（`projects.officialstatistics.org/undata2/undatacommons-mcp/`）、REST 檢視文件與 [`datacommonsorg/agent-toolkit`](https://github.com/datacommonsorg/agent-toolkit)（`Apache-2.0`）連結，以及「引用前複核原始來源」提醒。
  - **驗收標準（DoD）**：`docs/free-public-apis.md` 完成條目補充，且 `python tools/verify_inbox.py` 驗證通過。
