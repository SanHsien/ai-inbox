---
id: 2026-10-26-block-buzz-nostr-agent-workspace
title: "Block Buzz 深度解析：基於 Nostr 協議的去中心化人機協同工作區與 ACP/MCP 代理人架構"
source_url: "https://github.com/block/buzz"
source_platform: "GitHub (Block, Inc.)"
author: "Block, Inc."
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: in-progress
cluster: 1
cluster_role: "Nostr人機協同工作區"
short_title: "Block Buzz 協同工作區"
tags:
  - nostr-protocol
  - multi-agent-collaboration
  - acp-protocol
  - mcp-tools
  - rust-architecture
  - audit-trail
---

# Block Buzz 深度解析：基於 Nostr 協議的去中心化人機協同工作區與 ACP/MCP 代理人架構

- **官方開源倉庫**：[`block/buzz`](https://github.com/block/buzz) ｜ Apache-2.0
- **個人維護 Fork**：[`SanHsien/buzz`](https://github.com/SanHsien/buzz)
- **本地專案路徑**：`C:\GitHub\buzz`
- **分析主題**：Nostr 協議中繼（Relay）、人機同室協同（Human-Agent Collaboration）、ACP/MCP 雙協議解耦、Windows Job Object 進程防線與不可篡改審計日誌
- **分析日期**：`2026-10-26`
- **當前狀態**：`🟡 進行中 (In Progress)`
- **相關交叉參照**：
  - [`notes/2026-10-19-ai-shared-brain-multi-agent-architecture.md`](./2026-10-19-ai-shared-brain-multi-agent-architecture.md)（多 Agent 共同大腦與跨環境同步）
  - [`notes/2026-10-19-crossroad-a2a-agent-mail-relay.md`](./2026-10-19-crossroad-a2a-agent-mail-relay.md)（Agent-to-Agent 通訊與郵件中繼架構）
  - [`notes/2026-10-26-answer-me-with-html-visual-agent-artifacts.md`](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md)（工件輸出與互動反饋迴圈）

---

## 1. 核心內容摘要與專案背景（Key Insights）

由 Jack Dorsey 創立的金融科技巨頭 Block, Inc.（前身為 Square / Cash App）正式開源了旗艦級協同平台 **Buzz（`block/buzz`）**。

其核心願景為：**「一個人類與 AI 代理人共同構建的自主工作區，運行於自己掌控的中繼伺服器（A workspace where humans and agents build together, on a relay you own）。」**

### 1.1 Buzz 直擊的現代協作痛點（The Core Bet）
當代工程團隊在引入 AI Coding Agent 時，協作狀態嚴重碎裂在至少 7 個分頁：
- 團隊聊天（Slack / Discord）
- 程式碼託管與審查（GitHub / GitLab）
- 自動化機器人（CI/CD Bots）
- 工作流管理（Jira / Linear）
- 畫布與白板（Miro / Notion）
- 監控與審查日誌（Datadog / Audit logs）

Buzz 提出的根本解決方案是：**一個社群（Community）、一個身分模型（Identity Model）、一條不可篡改的事件日誌（Event Log）**。在 Buzz 中，AI 代理人不是受限的定時任務或機器人（Bots），而是具備同等權利與審計軌跡的「頻道成員（Channel Members）」。

---

## 2. 深入技術拆解與架構原理（Deep Dive）

Buzz 採用 Rust 打造高併發、模組化的工作區架構，底層建基於開放標準 **Nostr 協議（NIP-01、NIP-42 認證、NIP-98 HTTP 簽名、Blossom 媒體儲存）**。

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                       Block Buzz 系統拓撲架構                           │
└─────────────────────────────────────────────────────────────────────────┘

   [ 人類工程師 ]         [ AI 代理人 (Claude/Codex/Goose) ]      [ CI / Git 系統 ]
 (Desktop / Web App)       (buzz-agent + buzz-dev-mcp)      (git-sign-nostr)
          │                            │                             │
          │ WebSocket                  │ WS + REST (JSON)            │ WS + REST
          ▼                            ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              buzz-relay                                 │
│  單一真實資料來源 (Single Source of Truth) · Axum WS + REST · 權限驗證  │
│  NIP-01 廣播 · NIP-42/98 認證 · 頻道管理 · 工作流引擎 · Hash-Chain 審計 │
└───────┬──────────────────────────────┬──────────────────────────┬───────┘
        │                              │                          │
        ▼                              ▼                          ▼
 ┌──────────────┐               ┌──────────────┐           ┌──────────────┐
 │   Postgres   │               │    Redis     │           │   S3/MinIO   │
 │ 事件分區儲存 │               │  Pub/Sub 廣播 │           │   Blossom    │
 │ 全文檢索 FTS │               │  Presence 狀態│           │   多媒體儲存 │
 └──────────────┘               └──────────────┘           └──────────────┘
```

### 2.1 核心架構四大亮點

#### A. 單一真實資料來源：Nostr 中繼站（Single Relay SSOT）
- **無 P2P Gossip 複雜度**：Buzz 捨棄了不可預測的 P2P Gossip 廣播，採用直連單一 Relay 的星狀架構。客戶端透過 WebSocket 連線，所有讀寫、狀態變更、審查核准（Approvals）均為經 Schnorr 簽名的 Nostr Event。
- **型別化 Kind 系統**：新增功能只需定義新的 `kind` 整數，舊客戶端自動忽略未知 kind，永不破壞既有相容性。
- **Postgres + Redis + S3**：Postgres 負責按月分區的事件持久化與 `to_tsvector` 全文檢索；Redis 負責高頻毫秒級的頻道廣播、輸入中（Typing）與在線狀態（Presence）；S3 負責大型檔案與影片。

#### B. 雙協議解耦代理人（ACP + MCP Architecture）
Buzz 在代理人層面實現了極為乾淨的解耦設計：
```text
[ 編輯器 / ACP 客戶端 ]
  (Zed / JetBrains / buzz-acp)
          │ stdio ACP (Agent Client Protocol - JSON-RPC 2.0)
          ▼
    [ buzz-agent ] ───────► 呼叫 LLM (多 Session 獨立管理、自動摘要 Hand-off)
          │ stdio MCP (Model Context Protocol - JSON-RPC 2.0)
          ▼
   [ buzz-dev-mcp ]
          │ 執行工具調用 (Shell, File Edits, Directory Walk)
          ▼
[ 實體操作系統 / Windows Job Object ]
```
1. **`buzz-agent`（ACP 代理核心）**：
   - 僅透過標準 stdio ACP 協議接收任務，支援多達 8 個並行 Session。
   - 每個 Session 具備獨立的 MCP 連線、上下文與對話歷史。
   - Context 即將耗盡時，自動對歷史進行總結並發起自我交接（Self-handoff）。
2. **`buzz-dev-mcp`（加固型 MCP 伺服器）**：
   - 專為 Headless 自主程式開發設計，提供命令列執行、字串替換與目錄搜尋工具。
   - 代理人只專注於 Tool Calls，思考文字作為 Stream 呈現，所有實質改動均在工具邊界完成。

#### C. Windows 原生 Job Object 進程防線（Process-Tree Hardening）
在自動化 Coding Agent 中，最危險的隱患是命令執行超時後殘留「殭屍進程」或「MSYS/Bash 子進程樹洩漏」。
- **Unix 端**：使用 `killpg` 殺除整個進程群組。
- **Windows 端**：`buzz-dev-mcp` 直接呼叫 Windows 原生 Win32 API：
  - `CreateJobObjectW` 建立 Windows Job Object。
  - 將子行程加入 Job Object，並設定 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`。
  - 當超時中斷觸發時，Windows 核心層級強制連帶終止所有 MSYS、cmd.exe 與編譯器子子行程，提供最頂級的沙盒回收保證。

#### D. Nostr-Signed Git 與雜湊鏈審計日誌（Signed Audit Trail）
- **`git-sign-nostr`**：Git 提交紀錄不再依賴外部 GPG 金鑰伺服器或平台帳號，而是由 Agent 或工程師的 Nostr 金鑰對直接簽章。
- **Hash-Chain Audit Log**：工作區內的每一次指令執行、PR 審批與代碼合併，均寫入防篡改的鏈式審計日誌，具備可驗證憑據（Receipts），可隨時溯源六個月內的所有決策。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **採納與落地行動**：
  1. **建立遠端 Fork 與本地鏡像**：
     - 已成功將 `block/buzz` fork 至個人倉庫 [`SanHsien/buzz`](https://github.com/SanHsien/buzz)。
     - 本地 clone 至統一專案目錄 `C:\GitHub\buzz`，並設置 `gh repo set-default SanHsien/buzz`。
  2. **架構借鏡至 `agent-relay` 與多 Agent 調度體系**：
     - **ACP/MCP 雙管線解耦**：借鏡 `buzz-agent` 與 `buzz-dev-mcp` 的 stdio JSON-RPC 分離架構，使 `agent-relay` 的派工器能更乾淨地掛載不同工具後端。
     - **Windows Job Object 防線實踐**：吸收其 Windows 原生進程樹終止實作，補強本機 Agent 在執行長程建置與測試時的超時防護。
  3. **追蹤 Nostr 協議在去中心化 A2A（Agent-to-Agent）通訊之演進**：
     - 現行 `agent-relay` 採用本機 Mailbox 與 SQLite，未來若需拓展跨機器、跨網路的 Agent 通訊，Buzz 基於 Nostr Signed Event 的中繼架構為首選參考標竿。

- **不採納／暫緩評估**：
  - 目前不急於在本地生產環境部署整套 Postgres+Redis+MinIO 的完整 Buzz Relay 叢集；現階段聚焦於研究與複用其 `buzz-dev-mcp`、`buzz-agent` 以及 Nostr 簽名工作流。

### 3.1 實務心得增補：類 Slack 聊天室私有化常駐、多頻道派工分流與「已讀不回」額度警報

- **地端與 NAS 長程常駐中樞**：
  Buzz 提供的類 Slack 聊天室介面，打破了傳統 CLI 只能在當前終端視窗互動的限制。它不僅能在個人電腦地端啟動，還能直接部署在私有 NAS 或家用伺服器，將地端（Local LLM / 本地 CLI 工具鏈）與雲端（Claude / OpenAI / Grok）的多個 Agent 透過同一個私有聊天室串聯起來，實現真正的 24/7 私有化 Agent 協同中樞。
- **多聊天室任務分配與頻道隔離（Channel-based Agent Routing）**：
  利用不同聊天室頻道對應不同專案或任務目標，並分配指定 Agent 參加特定群組。這樣能以自然頻道邊界物理隔離專案上下文，避免跨專案 Prompt 污染與注意力稀釋。
- **「已讀不回」額度枯竭警報（Quota Exhaustion Silent Drop）與心跳機制**：
  在實務多 Agent 聊天協同中，最棘手的問題是「Agent 額度耗盡時不會丟出明確例外，而是直接已讀不回」。這揭示了在私有化聊天室協同架構下，必須補齊**「心跳偵測（Heartbeat Probe）與額度枯竭主動廣播退場」**機制，避免指揮官與使用者在頻道中陷入無效等待。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261026-27`**｜**[優先級：中]** 評估 Buzz 類 Slack 聊天室在 NAS 私有化常駐部署架構與「已讀不回」額度心跳防線設計
  - **目標範圍**：`docs/buzz-nas-deployment-and-heartbeat-spec.md`
  - **具體做法**：
    1. 規劃 Buzz Nostr Relay 與前端 Web/Desktop 客戶端在 NAS（Docker/Compose）私有化部署指引。
    2. 設計多頻道任務切片與 Agent 分配策略，明確各群組進駐之 Agent 權限與上下文邊界。
    3. 制定「額度感知心跳協定（Quota Heartbeat Protocol）」，當 Agent 偵測到 429 或配額歸零時主動在聊天室廣播退場狀態，消除已讀不回盲區。
  - **驗收標準（DoD）**：產出 `docs/buzz-nas-deployment-and-heartbeat-spec.md`，內含 NAS 部署拓撲、多頻道配置範例與心跳協議定義；以 `Test-Path docs/buzz-nas-deployment-and-heartbeat-spec.md` 驗證存在。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：docs/buzz-nas-deployment-and-heartbeat-spec.md（255 行）：NAS compose 部署拓撲、[[rules]] 多頻道配置範例（依 buzz-acp config.rs 解析器，指出 README 寫的 [channel.UUID] 不被解析）、QHP v0 心跳協議（狀態機、訊息格式、watchdog）。未實際部署、協議未實作，文件第 5 節已列。獨立驗收（fresh-context 審查員，2026-10-26）通過：config.rs 行號與 presence TTL 180 秒核對相符。
- [x] **`T-20261026-08`**｜**[優先級：高]** 撰寫「Block Buzz 架構解析與 Nostr+ACP/MCP 代理人協同設計指引」收錄於 `docs/buzz-nostr-agent-architecture.md`
  - **目標範圍**：`docs/buzz-nostr-agent-architecture.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳解 Buzz 的 Nostr Relay 設計哲學、Kind 系統與 Postgres FTS 全文檢索結構。
    2. 拆解 ACP（Agent Client Protocol）與 MCP（Model Context Protocol）在 `buzz-agent` 中的雙協議解耦管線。
    3. 解析 Windows Job Object 在防止子進程洩漏上的 Win32 API 實作細節。
    4. 探討 Nostr 簽名在 Agent 身分識別與不可篡改審計鏈（Hash-Chain Log）的工程落地方法。
  - **驗收標準（DoD）**：產出 `docs/buzz-nostr-agent-architecture.md`，內含系統拓撲圖、協議序列圖、Windows Job Object API 實作解析與本地調度啟發；以 `Test-Path docs/buzz-nostr-agent-architecture.md` 驗證存在。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：docs/buzz-nostr-agent-architecture.md（264 行）：系統拓撲圖、Nostr＋ACP 協議序列圖、buzz-dev-mcp 的 Windows Job Object 實作解析（附原始碼行號，buzz commit 9e8c9fc）、本地調度啟發。獨立驗收（fresh-context 審查員，2026-10-26）通過：抽查 10 處行號，git-sign-nostr 行號已由 :9 更正為 :6。

- [ ] **`T-20261026-09`**｜**[優先級：中]** 在 `SanHsien/buzz`（`C:\GitHub\buzz`）驗證 Windows 11 下 `buzz-dev-mcp` 與 `buzz-agent` 之獨立編譯與 Job Object 殺進程機制
  - **狀態**：🟡 進行中（卡關：本機 Visual Studio Build Tools 沒裝 C++ 工作負載，cargo check 找不到 link.exe，exit 101；裝好後重跑，紀錄見 docs/evidence/2026-10-26-buzz-windows-build.md）
  - **目標範圍**：`C:\GitHub\buzz\crates\buzz-dev-mcp` 與 `buzz-agent`
  - **具體做法**：
    1. 在 Windows 11 原生環境檢查 Rust 工具鏈（`cargo check -p buzz-dev-mcp -p buzz-agent`）。
    2. 深入測試其 Windows Job Object 進程綁定與超時中斷行為，確認 MSYS/cmd 子行程能否乾淨銷毀。
    3. 整理 Windows 原生編譯注意事項與相依套件需求至文檔。
  - **驗收標準（DoD）**：在 `SanHsien/buzz` 內完成 `buzz-dev-mcp` 與 `buzz-agent` 的編譯檢查，記錄執行日誌與 Job Object 驗證結果。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [x] **`T-20261026-10`**｜**[優先級：低]** 評估將 `agent-relay` 訊息中繼抽象對接 Nostr NIP-01 簽名事件格式之概念驗證
  - **目標範圍**：`C:\GitHub\agent-relay` 訊息格式設計與擴充文檔
  - **具體做法**：
    1. 分析現行 `agent-relay` Mailbox 事件結構與 Nostr NIP-01 事件（id, pubkey, created_at, kind, tags, content, sig）的對照映射。
    2. 撰寫輕量適配器概念驗證原型，評估無中心依賴的 Nostr Relay 在本地與區域網多 Agent 協同的可行性。
  - **驗收標準（DoD）**：產出 Nostr 事件映射對照表與原型評估紀錄於 `agent-relay` 相關文檔。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：SanHsien/agent-relay docs/nostr-nip01-evaluation.md（中英同步）：欄位映射表、ed25519 對 BIP-340 Schnorr 簽章差異、結論（核心不整合，只留單向橋接）。原型 tools/nostr_adapter_poc.py（commit 34bd57e，只用標準庫）把信件轉成 NIP-01 未簽章事件並無損還原，id 依 NIP-01 規則計算（範例信件 a77af769…e3b0）；15 項新測試全過、在刻意做壞的實作上 5 項轉紅，竄改 content 會被 verify 判 MISMATCH。全 repo 366 tests OK，CI 與 CodeQL success（34bd57e）。限制：標準庫沒有 secp256k1 所以事件不含 sig；沒有 WebSocket 所以未實連 relay；kind 9001～9004 是否撞號未查證。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 共同大腦與跨環境同步**：
  - [AI 共同大腦跨環境實踐](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
- **A2A 通訊與訊息中繼**：
  - [Crossroad A2A 通訊與中繼設計](./2026-10-19-crossroad-a2a-agent-mail-relay.md) ｜ 關聯任務：`T-20261019-01`、`T-20261019-02`
- **工件輸出與互動反饋迴圈**：
  - [answer-me-with-html 視覺工件](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md) ｜ 關聯任務：`T-20261026-06`
