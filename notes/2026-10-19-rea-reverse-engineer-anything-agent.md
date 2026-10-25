---
id: 2026-10-19-rea-reverse-engineer-anything-agent
title: "REA（Reverse Engineer Anything）：讓 AI Coding Agent 透過 MCP 驅動本地逆向工程工具鏈，無原始碼即可分析、理解與重造任意應用程式功能"
source_url: "https://www.threads.com/@wayturn_/post/DeTK8xZGfkX"
source_platform: "Threads"
author: "偉騰 (@wayturn_)"
github_repo: "https://github.com/morluto/rea"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: in-progress # pending | in-progress | done | archived
cluster: 3
cluster_role: "逆向分析"
short_title: "REA 逆向工程 MCP Server"
tags:
  - reverse-engineering
  - mcp
  - agent-tools
  - binary-analysis
---

# REA（Reverse Engineer Anything）：讓 AI Coding Agent 透過 MCP 驅動本地逆向工程工具鏈，無原始碼即可分析、理解與重造任意應用程式功能

- **來源連結**：[偉騰 @wayturn_ Threads 貼文](https://www.threads.com/@wayturn_/post/DeTK8xZGfkX) ｜ [morluto/rea (GitHub)](https://github.com/morluto/rea)
- **發布平台 / 原作者**：`Threads` / `偉騰 (@wayturn_)`
- **分析日期**：`2026-10-19`
- **當前狀態**：`🟡 進行中 (In Progress)`

---

## 1. 核心內容摘要

### 1.1 核心主張：SaaS 的逆向拆解時代——不需要原始碼也能理解與重造功能

原貼文核心敘述：

> 「昨天看到馬上玩了一天，SaaS 的惡夢還是來了，1 天就在 GitHub 登上 #1🔥。基本上讓你用 Agent 可以分析任何應用程式中的功能（即使沒有 source），看你想要優化或是重造都可以。」

**REA（Reverse Engineer Anything）** 是由 `morluto` 開源的命令列工具暨 **Model Context Protocol (MCP) 伺服器**，專門為 AI Coding Agent（Claude Code、Codex、Cursor、Gemini CLI、Antigravity 等）提供結構化逆向工程能力。其核心價值在於：

1. **不取代經典工具，而是在上面架一層 Agent 橋接器**：REA 不重造 Ghidra / Hopper / IDA，而是作為一個統一抽象層，讓 AI Agent 能透過 MCP 協議原生驅動這些底層反編譯器與分析器；
2. **全本地執行、證據驅動**：所有分析在本機進行，產出結構化的證據日誌與侷限性說明，而非黑箱猜測；
3. **多平台目標覆蓋**：原生二進位檔（x86/ARM/ELF/Mach-O/PE）、.NET 組件（PE/CLI + CIL 檢視）、Electron/JavaScript 應用（ASAR 解包 + 靜態 JS/TS 分析）、Android APK（透過 JADX 反編譯）、韌體、以及瀏覽器/網路流量（Chrome DevTools Protocol 觀測）。

### 1.2 技術架構與工作原理

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REA 架構全景（三層橋接設計）                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: AI Coding Agent（使用者介面層）                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Claude Code / Codex / Cursor / Gemini CLI / Antigravity     │   │
│  │  ↕ 透過 MCP（Model Context Protocol）雙向通訊                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                            ↕ MCP                                    │
│  Layer 2: REA MCP Server（統一抽象與路由層）                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ・接收 Agent 意圖（「分析這個 App 的登入功能」）              │   │
│  │  ・路由至對應分析引擎（依目標類型自動選擇）                    │   │
│  │  ・產出結構化證據（步驟日誌、侷限性標注、交叉引用）            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                            ↕                                        │
│  Layer 3: 底層逆向工程引擎（本地工具鏈）                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐   │
│  │  Ghidra  │ │  Hopper  │ │  IDA Pro │ │   JADX   │ │  CDP   │   │
│  │ (Native) │ │ (Native) │ │ (Native) │ │(Android) │ │(Browser│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘   │
│                                                                     │
│  Layer 3 (續): 靜態分析引擎                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐    │
│  │  ASAR 解包器 │ │ .NET CIL 檢視│ │ 韌體結構解析（Firmware） │    │
│  │  JS/TS 靜態  │ │  PE/CLI 元資料│ │                          │    │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 關鍵機制

1. **MCP 協議原生整合**：
   - REA 以 MCP Server 身份運行，任何支援 MCP 的 Agent 都能直接調用其工具函式（如 `analyze_binary`、`inspect_network`、`decompile_apk`），無需額外適配；
   - 安裝方式極簡：`npx rea-agents setup` 即可自動向本地 Agent 註冊。

2. **證據驅動分析（Evidence-Based Analysis）**：
   - 每次分析產出結構化的步驟日誌（step log）、發現摘要與侷限性聲明，而非黑箱結論；
   - Agent 可根據這些證據進一步推理、提問或深入特定模組。

3. **多目標自動路由**：
   - 輸入一個檔案或程序，REA 自動辨識其類型（ELF/PE/Mach-O/ASAR/.NET/APK）並路由至對應引擎；
   - 瀏覽器觀測模式透過 Chrome DevTools Protocol（CDP）即時攔截網路請求、DOM 事件與 API 呼叫。

4. **「分析→理解→重造」三階段工作流**：
   ```
   目標應用程式（無原始碼）
         │
         ▼
   [Stage 1: 行為觀測]
   ・網路流量攔截（CDP）     ・UI 事件追蹤
   ・API 端點列舉            ・資料流追蹤
         │
         ▼
   [Stage 2: 結構逆向]
   ・二進位反編譯（Ghidra）   ・符號提取與交叉引用
   ・IL/CIL 反組譯（.NET）   ・JADX 反編譯（Android）
   ・ASAR 解包 + JS 靜態分析 ・函式簽名與呼叫圖
         │
         ▼
   [Stage 3: 規格重構與重造]
   ・Agent 整合所有證據       ・產出功能規格書（Spec）
   ・產出等效實作或優化版本   ・附帶完整溯源證據
   ```

---

## 2. 對現有工作流與專案之啟發

### 2.1 與已有資產的對應

1. **已 Fork 的 `SanHsien/rea`**：
   - GitHub 遠端已存在 [`SanHsien/rea`](https://github.com/SanHsien/rea)（fork 自 `morluto/rea`），可直接作為本地調研與二次開發的基礎。
   - 描述：「透過 Agent 逆向工程一切，從應用程式行為到原生二進位檔案 ｜ Reverse engineer anything with agents, from app behavior down to native binaries.」

2. **與 CLI-Anything（Note 22）的互補關係**：
   - [CLI-Anything](./2026-10-18-cli-anything-agent-native-computer-use.md) 將「任意 GUI 軟體」封裝為 Agent-Native CLI，解決的是「操控」層面；
   - REA 解決的是「理解」層面——即使完全沒有原始碼，也能讓 Agent 分析目標軟體的內部結構與行為邏輯；
   - 兩者結合：CLI-Anything 讓 Agent 操控目標軟體 → REA 讓 Agent 理解其運作原理 → Agent 據此自動重造或優化。

3. **與 desktop-sense（Note 21）的協同**：
   - [desktop-sense](./2026-10-18-desktop-sense-local-screen-context.md) 提供本機螢幕即時視覺感知；
   - REA 的 CDP 瀏覽器觀測模式與 desktop-sense 的截圖分析互補：前者深入網路層與 DOM 事件，後者捕捉視覺呈現。

4. **MCP 生態直接銜接**：
   - 本地環境已配置多個 MCP Server（如 `biomolecular-structure-viewer`），REA 作為另一個 MCP Server 可無縫納入現有工具鏈；
   - 透過 Antigravity 的 `call_mcp_tool` 可直接調用 REA 提供的工具函式。

### 2.2 落差與採納判斷

- **值得採納的部分**：
  - MCP 原生整合、多目標自動路由、證據驅動分析流程三項核心設計，可直接用於競品分析、功能逆向、安全審計等場景；
  - `npx rea-agents setup` 一鍵安裝的開發者體驗極為流暢。
- **需評估的部分**：
  - Windows 11 本地環境下 Ghidra / JADX 等底層工具的安裝與路徑配置需實測驗證；
  - CDP 觀測模式對 Chrome/Edge 版本的相容性需確認；
  - 逆向分析涉及法律合規風險（著作權、DMCA），使用時需確保僅用於合法用途（自有軟體審計、開源專案分析、學術研究）。

### 2.3 實務心得增補：Clean Room 合規 Prompt 與「雲端 GPT + 本地未審查模型」雙軌實操管線

- **合規 Prompt 工程防線**：
  在對雲端模型（GPT-4o / Claude 3.7 Sonnet）發起二進位或逆向提示時，若直接詢問敏感操作易被安全對齊過濾器攔截。實務證明，**「先交代清楚目的為靜態分析、Assembly、Call Graph 並重建功能與資料格式，完全不使用原版程式代碼，亦不進行商用或非法用途」**，能在嚴格遵守 Clean Room 逆向工程原則的前提下，穩定引導模型輸出完整 Assembly、函式調用位址與資料結構映射。
- **雲地雙軌實操管線（Hybrid Cloud-Local Decompilation & Patching）**：
  - **雲端大模型（GPT-4o / Claude）**：利用其強大的上下文理解與反編譯推理能力，產出完整 Assembly 代碼結構、呼叫位址、`TfmRegKey` 與精確 Patch 資訊。
  - **本地未審查模型（Local Uncensored LLM）或二進位工具**：雲端輸出的精確修補規格直接交由地端本地模型實操執行，進行真正的位元級修補（Hex/Assembly Patching）與實機動態除錯，兼顧雲端的高階架構智商與地端的零審查合規實操。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [ ] **`T-20261026-26`**｜**[優先級：高]** 擴充 `docs/reverse-engineering-pipeline-spec.md`：收錄 Clean Room 合規宣告 Prompt 範本與「GPT 靜態分析 + 本地未審查模型實操」雙軌逆向管線
  - **目標範圍**：`docs/reverse-engineering-pipeline-spec.md`
  - **具體做法**：
    1. 在流水線規格書增補「合規防線與審查避障規範」，提供宣告靜態分析、Call Graph、重建資料格式之標準 Clean Room Prompt 範本。
    2. 制定雲端 GPT（靜態分析/輸出 Assembly/呼叫位址/TfmRegKey/Patch 偏移量）與本地未審查模型（實機位元修補與動態除錯）的資料介接契約。
  - **驗收標準（DoD）**：`docs/reverse-engineering-pipeline-spec.md` 包含合規 Prompt 範本與雲地雙軌管線架構圖，執行既有外部裁判驗證通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
- [x] **`T-20261019-09`**｜**[優先級：高]** 在 Windows 11 本地環境測試 `SanHsien/rea` Fork 的安裝流程（`npx rea-agents setup`），驗證 MCP Server 註冊、Ghidra/JADX 底層工具鏈整合，以及對 Electron 應用（ASAR 解包）與瀏覽器 CDP 觀測模式的基礎功能
  - **狀態**：🟢 已完成（沙盒環境驗證通過）
  - **目標範圍**：`SanHsien/rea`（本地路徑 `C:\GitHub\rea`）、沙盒環境（`C:\GitHub\_sandbox\rea\`）
  - **完成日期**：2026-10-23
  - **具體做法**：依維護者安全決策，在沙盒環境（`C:\GitHub\_sandbox\rea\`）下載可攜版 Adoptium JDK 21 與 NSA Ghidra 12.2（官方 SHA-256 嚴格逐字節比對 MATCH）；以隔離行程手動啟動 REA MCP Server（v6.7.0，成功註冊 207 個 MCP 工具），完成 `binary_session` 診斷調用；選定本機 Antigravity Electron 應用進行 `app.asar` 安全解包（1,221 節點、1,251 occurrences）與 778 個 JS 模組之靜態語意分析；啟動無頭 Chrome 以 CDP 模式成功攔截公開網站 6 個 API 請求（嚴格遵守零憑證原則，僅記路徑與狀態碼）。
  - **驗收標準（DoD）**：MCP Server 成功手動啟動並調用、Electron 應用成功解包與 JS 靜態分析並產出結構化日誌（原始碼零入庫）、CDP 模式成功攔截 $\ge 5$ 個 API 請求。
  - **實作紀錄 / 證據**：以 ai-inbox 實測報告交付於 `docs/rea-sandbox-evaluation-evidence.md`，沙盒隔離目錄佔用空間 2,192 MB，系統 PATH 與正式 Agent 配置保持零污染。
- [x] **`T-20261019-10`**｜**[優先級：中]** 設計「REA + CLI-Anything + desktop-sense 三合一逆向分析流水線規格（Reverse Engineering Pipeline Spec）」，定義從「觀測行為→理解結構→重造功能」的端到端 Agent 自動化工作流
  - **目標範圍**：`SanHsien/rea` ＋ `CLI-Anything` ＋ `desktop-sense`
  - **具體做法**：撰寫整合規格文件，定義三個工具的責任邊界與資料交換契約（CLI-Anything 產出操作日誌 → REA 產出逆向證據 → desktop-sense 產出視覺快照），設計 Agent 調用這三個 MCP 的標準 Prompt 模板
  - **驗收標準（DoD）**：規格文件完成、包含至少一個端到端範例（選定一個開源應用，從操控→逆向→重造完整走通），經人工審閱確認各工具責任劃分無重疊無遺漏
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。撰寫三階段逆向分析流水線規格手冊 `docs/reverse-engineering-pipeline-spec.md`，定義 CLI-Anything（行為觀測探針）、REA（結構逆向與解包核心）與 Cleanroom 重造標準；因桌面截圖隱私外洩與 Token 開銷過高，明確將 desktop-sense 標註為「選用、未採用」並附端到端 Electron 逆向實戰範例。
- [x] **`T-20261025-07`**｜**[優先級：高]** 實作逆向工程流水線（REA + CLI-Anything）與 Android 官方 33 Skills 防幻覺規範之「外部裁判」結構驗證器
  - **狀態**：🟢 已完成（外部裁判與單元測試全數通過）
  - **目標範圍**：`tools/verify_re_and_android_specs.py` 與 `tests/test_verify_re_and_android_specs.py`
  - **完成日期**：2026-10-25
  - **具體做法**：
    1. 實作 `tools/verify_re_and_android_specs.py`（純 Python stdlib），機械化解析並驗證：(a) `docs/reverse-engineering-pipeline-spec.md` 涵蓋「觀測行為 → 理解結構 → 重造功能」三階段架構、Cleanroom 重造規範，且明確標註 `desktop-sense` 為「選用、未採用」；(b) `docs/rea-sandbox-evaluation-evidence.md` 涵蓋 SHA-256 校驗、ASAR 解包與系統 PATH 零污染結論；(c) `docs/android-official-skills-anti-hallucination.md` 涵蓋 33 個官方 Skills 清單、XML 轉 Compose 與 Play Billing 合規防線；(d) `docs/android-cli-plugin-windows-validation.md` 記錄修改 Windows Registry PATH 與超過 1 GB 下載硬閘門之安全攔截結論。函式支援多行長字串且先判斷型別，嚴格杜絕 Linux CI ENAMETOOLONG。
    2. 撰寫 `tests/test_verify_re_and_android_specs.py`（繼承 `unittest.TestCase` 以同時相容 `unittest discover` 與 `pytest`），包含 12 項測試，完整涵蓋真實 4 份文件全數通過、關鍵契約反例精準攔截及超長字串防護。
  - **驗收標準（DoD）**：執行 `python tools/verify_re_and_android_specs.py` 回傳 exit 0，且 `python -m unittest discover -s tests -p "test_verify_re_and_android_specs.py"` 與 `pytest` 全數通過（至少 6 項測試）。
  - **實作紀錄 / 證據**：以純 Python stdlib 實作外部裁判驗證器 `tools/verify_re_and_android_specs.py` 與單元測試 `tests/test_verify_re_and_android_specs.py`，驗證 4 份關鍵架構與安全評估文件契約無訛，12 項測試在 `unittest` 與 `pytest` 下全數綠燈通過。

---

## 4. 關聯筆記與相關任務（Related Notes & Sessions）

- **逆向工程與軟體分析工具鏈**：
  - [CLI-Anything：將任意軟體升級為 Agent-Native CLI](./2026-10-18-cli-anything-agent-native-computer-use.md) ｜ 關聯任務：`T-20261018-11`、`T-20261018-12`
  - [desktop-sense：本機螢幕即時視覺感知](./2026-10-18-desktop-sense-local-screen-context.md) ｜ 關聯任務：`T-20261018-05`、`T-20261018-06`
- **MCP 生態與 Agent 工具鏈**：
  - [Claude Code 官方插件目錄](./2026-10-17-claude-plugins-official-directory.md) ｜ 關聯任務：`T-20261017-07`、`T-20261017-08`
  - [Claude Code Mods 自體改造機制](./2026-10-18-claude-code-mods-self-extending-runtime.md) ｜ 關聯任務：`T-20261018-09`、`T-20261018-10`
- **多 Agent 協同與派工**：
  - [AI 共同大腦全景規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [Crossroad A2A 跨機器寄信協議](./2026-10-19-crossroad-a2a-agent-mail-relay.md) ｜ 關聯任務：`T-20261019-01`、`T-20261019-02`
