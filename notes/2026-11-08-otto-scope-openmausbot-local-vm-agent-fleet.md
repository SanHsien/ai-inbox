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
source_review: partial
source_reviewed_at: 2026-11-17
source_review_note: "Threads 留言讀到 12 則／共 15 則，其餘要登入；README 7 張截圖只看 3 張。"
source_images: 4
source_replies: 20
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

- **來源貼文**：[Threads 貼文 `@otto.scope`（初次分析時 7K 觀看、62 讚；2026-11-16 重看為 104 讚、15 則回覆）](https://www.threads.com/share/_p8KCq3Fp)（短網址 `_p8KCq3Fp`，真實 URL `https://www.threads.com/@otto.scope/post/DfeO74yIJFT`）
- **官方開源 GitHub 倉庫（主動深挖查證）**：
  - [`milind-soni/OpenMausBot`](https://github.com/milind-soni/OpenMausBot)（前身為 `OpenGrokBot` / 簡稱 `MausBot`，17,737 Stars，2,478 Forks（2026-11-16 複查：23,982 Stars、3,327 Forks），Apache-2.0 授權，由 Milind Soni 主導維護）
  - 社群衍生：[`milind-soni/openmausbot-teams`](https://github.com/milind-soni/openmausbot-teams)（團隊模板與 Skill Playbooks）
- **分析日期**：`2026-11-08`
- **分析者**：`Antigravity`
- **當前狀態**：`📁 歸檔備查 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md`](./2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md)（事件溯源與無感凍結）
  - [`notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md`](./2026-11-08-google-research-harness2-recursive-agent-harnessing.md)（Google Research Harness² 評測沙盒）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看 Threads 貼文：貼文文字、作者圖片 1 張（開原圖看過）。Threads 留言 12 則（含作者 1 則；貼文標示 15 則回覆；留言是捲到才載入，逐段捲動收集）。另看 GitHub README 的 3 張產品截圖（共 7 張，另 4 張是模型選單、應用市集、右鍵選單、設定頁，未看），並以 GitHub API 讀留言數最多的 8 則 issue／PR 的標題與摘要。

- **作者圖片**：
  - 圖 1（貼文附圖）：一張「GitHub Trending 今日精選」樣式的資訊卡，列出 repo 名稱、17,297 Stars、今日 +1,955、TypeScript、Apache-2.0，以及三個賣點（自訂 Agent 團隊、內建虛擬機、本地優先架構）。卡片底部標示來源是一個自動整理 GitHub Trending 的網站。**貼文的三個賣點與這張卡片逐字對應**，可見貼文是照 Trending 卡片的摘要寫的，不是作者自己的使用心得。
  - 圖 2（README 主畫面截圖）：Telegram 式介面，左欄是四個各有名字的 bot，右邊是對話，右上角可選模型。
  - 圖 3（README 電腦面板截圖）：右側面板顯示 bot 的桌面即時預覽，「Runs on」有三個選項：**Cloud box、This Mac、Off**，截圖中選的是 Cloud box。
  - 圖 4（README 詢問卡截圖）：bot 的提問以卡片形式出現在對話裡，使用者點選項回答。
- **作者留言補充**：只有一則，貼出 repo 連結（附 GitHub 預覽卡，卡片文字是 repo 的一句話簡介）。
- **網友留言重點**：
  - **唯一的實際使用回報是負面的**：`141319mns` 說用過了，能力跟 Grok Bot 還是差很多。另有兩則只說「好棒」「超好用」，沒有細節。
  - 有人點名 `meta.ai`（Meta 的 AI 帳號，非一手資料）問它與 Hermes、與 Grok Bot 的差別。回覆的重點是：差別在架構而不是模型強度，它吃使用者本機已登入的 CLI，每個 bot 的電腦是雲端桌面、Local VM、本機三選一。這與 README 的說法一致，也再次說明「Local VM」只是選項之一。
  - GitHub 上留言最多的 8 則全是功能 PR（連接器 OAuth、群組討論流程、同主機 Docker socket、即時語音、決策模型挑選等），沒有針對沙盒隔離失效的回報；未關閉的 issue／PR 共 1,115 則，專案變動很快。
- **對分析的影響**：
  1. **「資料不用擔心傳到外面」說得太滿**：README 寫的是 harness 伺服器跑在 `127.0.0.1`、對話紀錄與金鑰存在本機。但圖 3 顯示 bot 的電腦可以是雲端 Linux 桌面（Cloud box），README 也寫可經 Composio 連 500 多個外部服務，而模型本身是呼叫 Claude、Grok 等雲端供應商。所以「本地優先」指的是控制面與資料存放，不是整條資料路徑都不出機器。已在第 1 節引文下方加註。
  2. **「Local VM」只是三種執行位置之一**：README 原文是每個 bot 可用雲端 Linux 桌面、隔離的 Local VM，或在平台安全邊界已認證時用使用者自己的電腦；直接操作宿主機目前只開放 macOS 與 Ubuntu Xorg，且要明確開啟。Windows 不在宿主機控制的支援清單內。已補進 2.2 節開頭與第 4 節處置。
  3. **補一則使用者負評**：留言有人用過後認為能力與 Grok Bot 差很多。原筆記第 4 節稱它「生產級」，那是依 README 與原始碼結構下的判斷，沒有使用實證；已在第 4 節加註。
  4. 貼文沒有任何實測內容（圖 1 是自動產生的 Trending 卡片），本筆記的技術細節全部來自 README 與原筆記的原始碼調研，與貼文無關。
  5. 維持歸檔、不開任務。

---

## 1. 核心內容摘要與貼文主張（Executive Summary）

Threads 作者 `@otto.scope` 介紹：
> 「這專案一天狂漲快兩千顆星，它是一個開源的 Grok Bot 替代方案，可以讓你用現有的 Claude 或 Grok 帳號，在自己的環境跑出一群 AI 機器人團隊。🚀 可以串接你現有的訂閱帳號，不用為了用 Agent 又去訂新服務。🛡️ 最強的是它內建了 Local VM，讓 AI 可以直接在隔離的虛擬機裡跑指令。🏠 採用本地優先架構，所有程序都跑在 127.0.0.1，資料不用擔心傳到外面。最聰明的地方在於那個虛擬機設計，讓 AI 能在受控環境幫你寫程式、跑測試。」

> 註（2026-11-16）：貼文的三個賣點照抄自附圖的 GitHub Trending 資訊卡。其中「資料不用擔心傳到外面」過度簡化：README 的「本地優先」是指 harness 伺服器與對話紀錄、金鑰在本機；bot 的電腦可選雲端桌面，也可經 Composio 連外部服務，模型呼叫本來就會送到雲端供應商。

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

依 README，每個 bot 的執行位置有三種：雲端 Linux 桌面、隔離的 Local VM、或使用者自己的電腦（僅 macOS 與 Ubuntu Xorg，需明確開啟；Ubuntu Wayland 暫時停用；Windows 不在清單內）。貼文強調的「Local VM / 虛擬機受控環境」，在 Linux / 容器環境下係透過 **`bubblewrap`（bwrap）** 實現的輕量進程級沙盒（稱為 **Bot Box**）：

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
   - OpenMausBot 展示了一套設計完整的多 Agent 本地編排架構（依 README 與原始碼結構判斷，未實際使用；Threads 留言有一位使用者回報實際能力與 Grok Bot 差很多），其「Egress Gate 阻絕 SSRF」與「私有工作空間與核心 DB 物理隔離」的設計極具參考價值。
2. **處置決策**：
   - 該專案為完整的獨立 Electron 產品，目前我們已有成型的四大 Agent 原生調度體系與 `harness-guard` 攔截層，因此不裝；並非不能裝：官方 release（v0.1.155，2026-11-14 查證）有 Windows 安裝檔 `OpenMausBot-0.1.155-setup.exe`。但依 README，直接操作宿主機的功能目前只認證 macOS 與 Ubuntu Xorg，Windows 上裝了也只能用雲端桌面或 Local VM 這兩種執行位置（Windows 上 Local VM 的實作方式本筆記未查）。
   - 將其架構與沙盒設計精華納入本庫知識庫，標記為 **`status: archived` 歸檔備查**，不衍生額外代碼任務。
