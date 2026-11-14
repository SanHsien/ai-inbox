---
id: 2026-11-08-otto-scope-openmausbot-local-vm-agent-fleet
title: "評析 Threads 推薦「OpenMausBot」：開源 Grok Bot 替代方案、雙行程 Harness 架構與 Local VM / Bot Box 沙盒安全邊界深挖"
source_url: "https://www.threads.com/share/_p8KCq3Fp"
source_platform: "Threads (@otto.scope) / GitHub (milind-soni/OpenMausBot)"
author: "Otto Scope (@otto.scope) / Milind Soni (@milind-soni)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "Agent安全與沙盒隔離"
short_title: "OpenMausBot沙盒與架構深挖"
tags:
  - openmausbot
  - grok-bot-alternative
  - agent-sandbox
  - bubblewrap
  - local-vm
  - multi-agent
  - egress-gate
  - security-boundary
---

# 評析 Threads 推薦「OpenMausBot」：開源 Grok Bot 替代方案、雙行程 Harness 架構與 Local VM / Bot Box 沙盒安全邊界深挖

- **來源貼文**：[Threads 貼文 `@otto.scope`（7K 觀看，62 讚）](https://www.threads.com/share/_p8KCq3Fp)（短網址 `_p8KCq3Fp`，真實 URL `https://www.threads.com/@otto.scope/post/DfeO74yIJFT`）
- **官方開源 GitHub 倉庫（主動深挖查證）**：
  - [`milind-soni/OpenMausBot`](https://github.com/milind-soni/OpenMausBot)（前身為 `OpenGrokBot` / 簡稱 `MausBot`，17,737 Stars，2,478 Forks，Apache-2.0 授權，由 Milind Soni 主導維護）
  - 社群衍生：[`milind-soni/openmausbot-teams`](https://github.com/milind-soni/openmausbot-teams)（團隊模板與 Skill Playbooks）
- **分析日期**：`2026-11-08`
- **分析者**：`Antigravity`
- **當前狀態**：`📁 歸檔備查 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md`](./2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md)（事件溯源與無感凍結）
  - [`notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md`](./2026-11-08-google-research-harness2-recursive-agent-harnessing.md)（Google Research Harness² 評測沙盒）

---

## 1. 核心內容摘要與貼文主張（Executive Summary）

Threads 作者 `@otto.scope` 介紹：
> 「這專案一天狂漲快兩千顆星，它是一個開源的 Grok Bot 替代方案，可以讓你用現有的 Claude 或 Grok 帳號，在自己的環境跑出一群 AI 機器人團隊。🚀 可以串接你現有的訂閱帳號，不用為了用 Agent 又去訂新服務。🛡️ 最強的是它內建了 Local VM，讓 AI 可以直接在隔離的虛擬機裡跑指令。🏠 採用本地優先架構，所有程序都跑在 127.0.0.1，資料不用擔心傳到外面。最聰明的地方在於那個虛擬機設計，讓 AI 能在受控環境幫你寫程式、跑測試。」

經調研官方原始碼，該專案正是社群高度關注的 **OpenMausBot（MausBot）**，定位為 **Grok Bot、Meta Muse、OpenAI dots、Cue by Manus 的開源本地化替代品**。它採用 Telegram 式的通訊軟體介面，側邊欄中的每個機器人都是一個具備自身記憶、模型與電腦環境的獨立 Agent。

---

## 2. 底層技術架構深挖（Technical Deep Dive）

### 2.1 雙行程解耦架構（Two-Process Architecture）

OpenMausBot 徹底分離了「使用者介面」與「Agent 執行載體」：

```
+-----------------------------------------------------------------------------------+
|                        OpenMausBot 雙行程執行架構                                 |
+-----------------------------------------------------------------------------------+
|  [App 前端] React 19 + Tailwind + Electron (127.0.0.1:5199)                       |
|    - 聊天介面、模型選擇器、電腦操作畫面檢視器 (WebContentsView CDP 驅動)         |
|    - 零本機傳輸層 (Zero client-side transports)，僅接收單一 SSE 事件流摺疊為 State|
|                                       │                                           |
|              HTTP Commands            │  Single Canonical SSE Event Stream        |
|                                       ▼                                           |
|  [Harness Server 後端] Node.js 服務 (127.0.0.1:8799)                              |
|    - Driver Registry: 驅動本地 claude / codex / grok 等 CLI (stream-JSON / ACP)   |
|    - Permission Broker: 攔截權限請求，管理審批模式 (Full / Ask / Approve for me)  |
|    - Event Bus: 將各 Provider 的原生事件正規化為規範化 NDJSON 稽核日誌            |
|                                       │                                           |
|             +-------------------------+-------------------------+                 |
|             ▼                                                   ▼                 |
|  [Local VM / Bot Box]                                 [外部整合]                  |
|    - bubblewrap 容器隔離                               - Boat API (雲端 Linux)   |
|    - 唯讀系統目錄 / 私有 PID 與網路 Namespace           - Composio (500+ SaaS 連接)|
|    - Egress Gate 阻絕 Localhost/Metadata SSRF                                     |
+-----------------------------------------------------------------------------------+
```

### 2.2 Local VM 與 Bot Box 沙盒隔離細節（`server/bot-box/`）

貼文強調的「Local VM / 虛擬機受控環境」，在 Linux / 容器環境下係透過 **`bubblewrap`（bwrap）** 實現的輕量進程級沙盒（稱為 **Bot Box**）：

1. **檔案系統邊界**：
   - `/usr`、`/etc`、`/opt` 以及伺服器自身的程式碼目錄皆以**唯讀（Read-Only）**方式掛載。
   - 核心資料庫 `~/.openmausbot`（存放 `messages.db`、`runtime.db`、API Token、伺服器 Unix Socket）在沙盒內部被重置為**全新的私有空白目錄**，沙盒內的 Agent 完全無法嗅探宿主機與其他 Bot 的記憶或金鑰。
   - 僅將該 Turn 真正需要的專案工作目錄（`workspaces/<bot>`）以讀寫權限掛載。
2. **行程與命名空間隔離**：
   - 啟用獨立的 PID Namespace，沙盒內部的 Agent 無法看見或干擾宿主機與其他 Agent 的運作行程。
   - 獨立的私有 `/tmp`、`/var/tmp`、`/run`、`/dev`、`/proc`。
3. **兩大防線閘門（The Two Gates）**（埠號 `3128`、驅動名稱 `cua-driver` 等細節出自 README／貼文描述，未讀原始碼，未查證）：
   - **出站代理閘門（Egress Gate）**：沙盒內部網路僅有 loopback，出網必須強制走 `127.0.0.1:3128` 上的專屬 HTTP CONNECT 代理。該代理會在伺服器端自行解析 DNS，**嚴格拒絕連線至 127.0.0.1、內網私有 IP（RFC 1918）、Link-Local（169.254.169.254 雲端元數據）與 Fly 私有網路**，徹底杜絕 Agent 透過 SSRF 竊取本機憑證或雲端 IAM 權限。
   - **權限仲裁者（Permission Broker）**：僅對「純文字、無管道（Pipe）、無重新導向、路徑完全在 Bot 私有資料夾內」的純讀取指令（`cat`, `head`, `grep`, `ls` 等）放行；任何具備副作用的寫入、刪除或外部路徑讀取均強制阻斷並要求使用者審批。

### 2.3 電腦使用（Computer Use）整合方案

> 本節驅動名稱與依賴說明未讀原始碼，僅依 README／貼文描述。

在桌面端操作上，OpenMausBot 採取了嚴格的收斂策略：
- **拒絕脆弱方案**：完全摒棄 `cliclick`、`robotjs`、`nut.js` 或 Python 臨時腳本。
- **唯一驅動**：本機桌面控制僅採用編譯自 Rust 的官方 **`cua-driver`**（macOS Mach-O / Linux Xorg 受限二進位檔）。
- **瀏覽器操作**：直接利用 Electron 內建的 Chromium，透過 `WebContentsView` 搭配 `webContents.debugger`（CDP 協議）驅動，免安裝外部 Chrome 或 280MB 的 Playwright 套件。

---

## 3. 與本機資安架構之對照與借鏡價值

OpenMausBot 的設計與我們在四大 Agent（Antigravity / Claude / Codex / Hermes）推進的資安標準高度共鳴：

| 評估維度 | OpenMausBot 的設計 | 本機資安防線（`harness-guard` / `GLOBAL_RULES`）對照 |
| :--- | :--- | :--- |
| **金鑰與資料夾保護** | Bot Box 隱藏 `~/.openmausbot`，僅保留空白目錄。 | 硬閘門：嚴禁在專案目錄外讀寫或刪改，防止 Agent 存取家目錄的金鑰、憑證與瀏覽器 Cookie。 |
| **網路出站與 SSRF 防禦** | Egress Gate 強制攔截 Link-Local（169.254.169.254）與本機端口。 | 外部來源零信任：嚴禁讀取本地未授權服務、攔截危險下載命令。 |
| **指令審批防弊** | 依指令語法結構拆解，有管道/重新導向即視為複合命令阻斷。 | `danger-zone-guard`：全域攔截 `curl|bash`、`iwr|iex` 與 `--dangerously-bypass-approvals-and-sandbox`。 |
| **MCP 控制面隔離** | 匯出的 MCP Server 僅開放任務下發與查詢，**嚴格關閉審批授予與金鑰導出**。 | 第三方 MCP 零信任防線：唯讀審核，嚴防惡意指令外溢。 |

---

## 4. 評估結論與處置

1. **專案價值判定**：
   - OpenMausBot 展示了一套生產級的多 Agent 本地編排架構，其「Egress Gate 阻絕 SSRF」與「私有工作空間與核心 DB 物理隔離」的設計極具參考價值。
2. **處置決策**：
   - 該專案為完整的獨立 Electron 產品，目前我們已有成型的四大 Agent 原生調度體系與 `harness-guard` 攔截層，因此不裝；並非不能裝：官方 release（v0.1.155，2026-11-14 查證）有 Windows 安裝檔 `OpenMausBot-0.1.155-setup.exe`。
   - 將其架構與沙盒設計精華納入本庫知識庫，標記為 **`status: archived` 歸檔備查**，不衍生額外代碼任務。
