---
id: 2026-10-17-xerj-corpus-hub
title: "XERJ Corpus Hub：為 Agent 釘選整門領域知識的預索引語料庫"
source_url: "https://www.threads.net/@krumjahn/post/DejmOD1G6t4"
source_platform: "Threads"
author: "Keith Rumjahn (@krumjahn)"
github_repo: "https://github.com/xerj-org/xerj"
official_hub: "https://hub.xerj.org"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: archived
cluster: 3
cluster_role: "語料預索引"
short_title: "XERJ Corpus Hub"
tags:
  - agent-memory
  - retrieval-augmented-generation
  - corpus-hub
  - token-optimization
  - code-search
  - rust
---

# XERJ Corpus Hub：為 Agent 釘選整門領域知識的預索引語料庫

- **原始貼文**：[Threads @krumjahn 貼文](https://www.threads.net/@krumjahn/post/DejmOD1G6t4)
- **官方 GitHub**：[`xerj-org/xerj`](https://github.com/xerj-org/xerj)（Corpus Hub 位於 `corpus-hub` 分支）
- **官方網站 / 註冊表**：[hub.xerj.org](https://hub.xerj.org)
- **發布平台 / 作者**：`Threads` / `Keith Rumjahn (@krumjahn)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`⚪ 封存不做 (Archived)`

---

## 1. 核心內容與開源專案全貌

### 1.1 核心主張與技術痛點
- **痛點**：傳統 Coding Agent 在查閱領域知識、大型代碼庫或歷史標準時，通常依賴兩種不可靠途徑：
  1. **靠 LLM 訓練記憶猜測**：容易出現幻覺（Hallucination），特別是冷門函式庫、演算法或快速迭代的 API。
  2. **靠 grep / sed / view_file 盲搜大量檔案**：一次撈出數萬至上百萬 Token 塞爆 context window，稀釋上下文注意力並極度消耗 API 配額。
- **XERJ 的解法**：用 Rust 自研（非 Java/Lucene）的零相依本地搜尋引擎，兼具 Elasticsearch 相容 API 與 MCP（Model Context Protocol）支援。
- **Corpus Hub 的機制**：將經過精挑細選的代碼庫與領域文檔，透過自動索引預先「釘選」打包成 Agent 可直接查詢的結構化語料。

### 1.2 關鍵規模與技術規格
- **規模數據**：收錄 **515 個活 corpus**、跨 **11 個領域**、總量約 **78.6 GB**。
- **七道授權與檢索關卡**：
  1. **Pinned Source**：所有專案與依賴均鎖死在精確 Commit SHA，確保版本重現性，不受上游 force-push 或刪庫影響。
  2. **Human-Reviewed License**：人工審核授權協議（不單靠機器掃描），避免 Agent 引用有法律爭議的程式碼。
  3. **Ed25519 簽名與 Checksum**：每份語料包封裝結構化記錄包，驗證防竄改。
  4. **嚴格檢索基準分（Measured Retrieval Scores）**：實測檢索召回率與 Token 節省度。
- **Agent 檢索指令工作流**：
  ```bash
  # 1. 依需自 Hub 拉取指定 corpus manifest
  xerj corpus add --from https://raw.githubusercontent.com/xerj-org/xerj/corpus-hub/tools/xerj-code/hub/lz4.json
  # 2. 建立本地索引
  xerj corpus index lz4
  # 3. Agent 進行結構化代碼或語義檢索（直接給出精確行號與上下文代碼塊）
  xerj code lz4 "maximum input size"
  ```

```text
[傳統模式]
Agent ──(grep / 讀取整包檔案)──> 吞入數十萬 Token ──> 上下文被稀釋且高成本

[XERJ Corpus Hub 模式]
領域知識 / 開源庫 ──(人工授權審核 + SHA 釘選 + Ed25519 簽名)──> 預製 Corpus Pack (78.6GB / 515 corpora)
                                                                       │
Agent ──(xerj corpus add / xerj code 精準檢索)────────────────────────┴──> 僅抽取關鍵代碼片段 (省達 40x Token)
```

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **全域 Token 節流機制**：與 `token-optimizer`（多代理與 Context 節流）、`quality-loop` 與 `verification-protocol` 高度契合。
  - **本地知識庫（KB）分層架構**：目前專案參考資料多放在 `references/` 目錄直接讀取，若未來遇到數萬行等級的第三方 SDK 或上游 Repo，應採取「索引 + 精準命中」而非整包 view_file。
  - **Windows 11 原生相容性**：XERJ 是 Rust 單一 binary，理論上具備極佳跨平台潛力，需在原生 Windows 實測 CLI 與路徑表現。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **SHA 釘選與授權檢查制度**：Agent 抓取外部知識或開源代碼時，必須學習其「釘選 Commit SHA」與「明確授權檢查」的防護思維。
    2. **XERJ 混合檢索能力**：XERJ 支援 Autoindex（自動為代碼、PDF、SQLite、CSV 建模）與 MCP，可評估作為本地 Coding 工具的一環。
  - **不適用 / 需調整的部分**：
    1. **儲存策略**：78.6 GB 語料不可全拉，必須維持按需拉取單一語料包（On-demand）。
    2. **路徑相容性**：注意 Windows 反斜線 `\` 與 Git Bash / PowerShell 的路徑相容問題。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261017-01`**｜**[優先級：低]** 調研 XERJ CLI 與 Corpus Hub 在 Windows 11 下的可用性與安裝方式
  - **目標範圍**：`環境工具鏈 / XERJ 原生調研`
  - **狀態**：⚪ 不做（知識檢索已全面採用本地 Markdown 與 Obsidian 知識庫，不另引入重型 XERJ 語料庫工具鏈）
  - **官方來源**：GitHub [`xerj-org/xerj`](https://github.com/xerj-org/xerj)
  - **具體實作步驟**：
    1. 檢視 `xerj-org/xerj` release 頁面是否有預編譯的 Windows 原生 binary（`xerj-x86_64-pc-windows-msvc.zip`）或需透過 `cargo install xerj`。
    2. 在 Windows 11 終端環境測試 `xerj --version` 與本地目錄初始化。
    3. 執行單一語料新增測試：`xerj corpus add --from https://raw.githubusercontent.com/xerj-org/xerj/corpus-hub/tools/xerj-code/hub/lz4.json`。
    4. 測試 `xerj corpus index lz4` 與查詢語法 `xerj code lz4 "maximum input size"`。
  - **驗收標準（DoD）**：在本地終端跑通 minimal example，確認無 Windows 路徑報錯，並在工作筆記中記錄安裝指令與執行輸出。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261017-02`**｜**[優先級：低]** 評估將 XERJ 整合為 Antigravity / Claude Code 本地 MCP 工具或 Skill
  - **目標範圍**：`~\.gemini\config\skills\` 或 `mcp` 外掛
  - **狀態**：⚪ 不做（同 T-20261017-01，不引入 XERJ 工具鏈）
  - **官方來源**：GitHub [`xerj-org/xerj`](https://github.com/xerj-org/xerj) 的 MCP 模組與文件
  - **具體實作步驟**：
    1. 調研 XERJ 內建的 MCP Server 配置方式（查看其 stdio 協定支援）。
    2. 評估編寫一支 `xerj-search` Skill 或在 `token-optimizer` 中加入規則：「當單一目錄檔案數超過 50 或總 Token 估計大於 100K 時，優先調用 xerj 結構化檢索，禁止直接 view_file 吞檔」。
    3. 對比基準測試：拿一個中型開源庫（例如 5,000 行代碼），分別記錄傳統全部載入 Token 消耗 vs XERJ 檢索 Token 消耗。
  - **驗收標準（DoD）**：產出對比數據報告與 Skill/MCP 整合建議書，確認能省下至少 10x 以上 Token。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
