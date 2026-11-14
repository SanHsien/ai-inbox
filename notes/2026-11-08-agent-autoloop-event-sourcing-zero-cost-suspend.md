---
id: 2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend
title: "Agent Autoloop 架構深挖：約 2,000 行零依賴事件溯源內核、掛起零消耗、指令資料分離與 8 跳 TTL 熔斷防線"
source_url: "https://www.threads.com/share/BBhKdG9xii"
source_platform: "Threads (@leeunhn) / GitHub (KKKKhazix/agent-autoloop)"
author: "李昀翰 (@leeunhn) / Khazix (@KKKKhazix)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: pending
cluster: "1"
cluster_role: "A2A 通訊與協同工作區"
short_title: "Agent-Autoloop事件溯源與掛起零消耗"
tags:
  - agent-autoloop
  - event-sourcing
  - zero-cost-suspend
  - prompt-injection-defense
  - ttl-circuit-breaker
  - multi-agent-orchestration
  - acp
---

# Agent Autoloop 架構深挖：kernel/ 約 2,000 行（11 檔實數 2,057）零依賴事件溯源內核、掛起零消耗、指令資料分離與 8 跳 TTL 熔斷防線

- **來源連結**：[Threads 原文分享](https://www.threads.com/share/BBhKdG9xii) ｜ [貼文永久網址 (@leeunhn)](https://www.threads.com/@leeunhn/post/DfUMk5hlLLV) ｜ [GitHub (KKKKhazix/agent-autoloop)](https://github.com/KKKKhazix/agent-autoloop) ｜ [安全邊界文件 (SECURITY.md)](https://github.com/KKKKhazix/agent-autoloop/blob/main/SECURITY.md)
- **核心作者**：李昀翰（`@leeunhn` 推薦）／ Khazix（`@KKKKhazix`，專案作者）
- **分析主題**：解構在 GitHub 迅速斬獲 3,929 Stars、713 Forks 的命令列 Agent 背景自動化中台 **`KKKKhazix/agent-autoloop`**（TypeScript，Node 24+，零外部執行期依賴）。剖析其「掛起零消耗（提问後行程立即退出，0 RSS / 0 Token 等待人類拍板）」、「kernel/ 約 2,000 行（11 檔實數 2,057）的純函式事件溯源內核（SQLite WAL+FULL 單一交易落盤）」、「SQL 參數化式指令資料分離」與「8 跳 TTL 強制熔斷」四大機制，以及 `SECURITY.md` 揭露的反自問自答、PR 零檢出審查與 Windows Codex 沙盒 ACL 收斂防線。
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-21-agent-relay-pipeline-phase4.md`](./2026-10-21-agent-relay-pipeline-phase4.md)（`SanHsien/agent-relay` 跨機器派工、並發／花費上限與驗收合併）
  - [`notes/2026-10-26-codync-open-source-agent-relay-fallback.md`](./2026-10-26-codync-open-source-agent-relay-fallback.md)（Codync 開源 Agent 中繼與 ACP 橋接、E2EE 遠端審批）
  - [`notes/2026-10-31-openbot-local-first-multi-agent-desktop-workspace.md`](./2026-10-31-openbot-local-first-multi-agent-desktop-workspace.md)（OpenBot 本地優先多 Agent 工作台）

---

## 1. 核心內容摘要：5W1H 初篩與內核拓撲（Executive Summary）

| 維度 | 核心內容 |
| :--- | :--- |
| **Who（主體）** | 開源專案 **`KKKKhazix/agent-autoloop`**（MIT License，3,929 Stars），以及社群衍生的 Windows 移植版 `yangfan27/agent-autoloop-win`。 |
| **What（核心定位）** | 專為命令列 Coding Agent（Claude Code、Codex、ACP 協定代理、DeepSeek Harness、Hermes、Gemini CLI 等）設計的本機背景事件調度中台。 |
| **Why（解決痛點）** | 1. 傳統 CLI Agent 需人工盯著終端機等待下一步，視窗關閉或斷線即中斷。<br>2. 常駐等待人類確認時佔用行程與記憶體，若靠輪詢還會白燒 Token。<br>3. 接上外部事件（如 GitHub Issue / Webhook）後，面臨 Prompt Injection、無限派工迴圈與 Agent 自行核准高風險操作的失控風險。 |
| **Where（部署環境）** | Windows / macOS / Linux 本機（Node 24+，無須公網伺服器，透過飛書、釘釘、企微、Slack、Discord 或桌面通知推送拍板卡片）。 |
| **When（觸發場景）** | 每日定時早報、GitHub Issue 自動跟進、線上告警排查、使用者回饋修復、網站巡檢與 `deliver` 標籤驅動的 PR 自動審查合併流水線。 |
| **How（運作契約）** | Agent 不需接入 SDK 或修改原始碼，只需在最後一條回覆末尾附帶 ```` ```agent-autoloop {"ask": [...]} ``` ```` JSON 回執區塊，行程隨即退出；人類拍板後中台自動以 `--resume` 接續原會話 ID 完成剩餘工作。 |

---

## 2. 深入技術拆解：內核四大機制與確定性驗證（Deep Dive）

### 2.1 內核四大機制對照

1. **掛起零消耗（Zero-Cost Suspension）**：
   - 當 Agent 遇到刪資料、重啟服務、發貨方式等需人類拍板事項時，輸出 `ask` JSON 回執後**行程直接結束退出**。
   - 等待狀態持久化於本機 SQLite（`hub.db`）；即使人類 3 天後才回覆，期間 **0 個 Agent 行程在跑、0 Token 消耗**，僅中台（約 60 MB RSS：README 效能表「空闲内存 59.94 MB RSS」，作者在 Apple M5 Pro 上自述的實測，本筆記未重現）在背景待命；一旦執行 `agent-autoloop answer <id> <選項>` 或點擊飛書卡片，中台立即喚醒原會話繼續執行。
   - 若 Agent 輸出的回執 JSON 格式有誤，中台只讓它在原會話重寫最後一段回覆，**不會把已做完的業務重做一遍**。
2. **純函式事件溯源（Deterministic Event-Sourcing Kernel）**：
   - `kernel/` 約 2,000 行程式碼（11 檔實數 2,057，2026-11-14 以 GitHub API 計）、**0 外部依賴、不讀系統時鐘、不用隨機數、不發網路請求**。
   - 所有狀態皆由單一 append-only 事實日誌推導，決策、事實追加與狀態投影（`evolve`）在同一個 SQLite `WAL + FULL` 交易中寫入磁碟才回應。
   - 內建確定性模擬測試：
     - `node sim/random.ts 24301 200000`：單一隨機種子重現 20 萬步斷網、丟包、崩潰與重複提交；
     - `node sim/crash.ts 1000 12648430`：真實 SQLite 行程強制 `SIGKILL` 1,000 次，驗證已確認紀錄零遺失；
     - `agent-autoloop why <輪次>`：一鍵回溯任意輪次的觸發事件、規則版本與回執因果鏈。
3. **指令資料分離（SQL 參數化式防注入）**：
   - 外部事件（如 GitHub Issue 標題與正文）**一律視為不可信資料寫入獨立檔案（`context.json`），絕不直接拼接進 Prompt**。
   - Prompt 內僅允許帶入經字元白名單校驗的 `type`、`id`、`link`。
   - **路由與權限隔離**：派給哪個 Agent、在哪個 `cwd` 目錄、給予什麼 `access` 權限，100% 由本機 `rules.json` 決定；外部事件若夾帶 `cwd`、`agent`、`access` 欄位會被內核直接拒收。
4. **跳數熔斷（TTL Hop Limit = 8）**：
   - 針對 Threads 留言區提問「*會不會自動做一大堆不相干的事情然後浪費 token？*」：Agent 回執產生的派生事件若再次觸發 Agent，跳數（hop count）會一路累加。
   - **不可清零鐵律**：即使中間經過人工 `ask` 提問或 `later` 預約複查，跳數也**絕不清零**，且 Agent 無法自行修改；一旦超過 **8 層**，內核只記錄不再派活，並發送告警卡片通知人類。

### 2.2 `SECURITY.md` 揭露的三大實戰資安防線

| 防線名稱 | 潛在攻擊／失效場景 | `agent-autoloop` 的工程防禦設計 |
| :--- | :--- | :--- |
| **反自問自答（Anti-Self-Approval）** | 中台提供 MCP 工具供查詢與回答卡片；若將該 MCP 配進 Worker 啟動的 CLI 使用者級設定，Agent 跑一輪時能自己呼叫 MCP 回答自己發出的拍板卡片。 | 嚴禁在接單 Worker 的 CLI 環境掛載具 `answer` 權限的 MCP，確保人工拍板硬閘門不被 Agent 內部短路。 |
| **PR 零檢出審查（Zero-Checkout PR Delivery）** | 外部 PR 若含惡意測試、設定檔或 `.git/hooks`，一旦在審查機上 `git checkout` 或執行測試即遭 RCE。 | `delivery` 插件只從 `main` 讀取審查設定，對 PR **只下載 Git objects 產生純文字 diff**，絕不檢出或執行 PR 程式碼；且遇到隱藏差異的**章魚合併（Octopus merge）直接拒絕放行**。 |
| **Windows Codex 沙盒 ACL 收斂** | Codex 在 Windows 建立沙盒時，會對使用者目錄下的資料夾加上沙盒帳號的讀取權限，導致沙盒內命令可偷讀中台 `master.key` 與 `secrets.env`。 | 中台安裝器與每次啟動時強制重設資料目錄 ACL（macOS/Linux `0700`，Windows 僅保留當前使用者與 `SYSTEM`），收回沙盒帳號對主密鑰的讀取權。 |

---

## 3. 與本庫 `SanHsien/agent-relay` 及同類方案對照

| 比較維度 | `KKKKhazix/agent-autoloop` | `SanHsien/agent-relay` | `Codync` (`2026-10-26` 筆記) |
| :--- | :--- | :--- | :--- |
| **核心定位** | 本機事件溯源調度中台 + 拍板卡片閉環 | 跨機器 Git/A2A 派工佇列 + 驗收閘門合併 | 行動端 E2EE 遠端審批 + 多 Agent 容錯降級 |
| **人類拍板期間資源佔用** | **0 行程 / 0 Token**（輸出 `ask` 後立即退出，拍板後 `--resume`） | Worktree 無頭 CLI 單輪執行完畢後退出 | 透過 ACP 橋接常駐會話 |
| **防無限迴圈與配額保護** | **8 跳 TTL 強制熔斷**（經 `ask`/`later` 不清零） | `max_concurrency` + `max_cost_usd` + 冪等防重跑 | 上游端點 Fallback 與速率限制退避 |
| **外部事件防注入** | 事件禁帶 `cwd`/`agent`/`access`，正文隔離於 `context.json` | SSH `allowed_signers` 寄件者簽章驗證 + Worktree 隔離 | E2EE 通道金鑰驗證 |

---

## 4. 拆解待辦事項（Action Items）

- [ ] **`T-20261108-02`**｜**[優先級：高]** 撰寫 Agent Autoloop 事件溯源與四層安全防線規格，並實作 `tools/verify_autoloop_dispatch_guard.py` 派工安全檢驗器
  - **目標範圍**：`docs/agent-autoloop-event-sourcing-and-ttl-spec.md`、`tools/verify_autoloop_dispatch_guard.py`、`tests/test_verify_autoloop_dispatch_guard.py`
  - **具體實作步驟**：
    1. 撰寫 `docs/agent-autoloop-event-sourcing-and-ttl-spec.md`，整理「無狀態行程 + 事件溯源內核」拓撲與四大機械契約（`AUTOLOOP-001` 路由與權限欄位隔離、`AUTOLOOP-002` 指令與外部資料分離、`AUTOLOOP-003` 8 跳 TTL 單調遞增與熔斷、`AUTOLOOP-004` 反自問自答／PR 零檢出／Windows 沙盒 ACL 收斂）。
    2. 實作 `tools/verify_autoloop_dispatch_guard.py`，支援檢驗派工規則與事件鏈 JSON 套件（`--config`、`--json`），攔截事件夾帶 `cwd`/`agent`/`access`、Prompt 內插 `{body}`/`{title}`、跳數被重置或超限未熔斷、以及 Worker 掛載拍板工具等違規。
    3. 撰寫 `tests/test_verify_autoloop_dispatch_guard.py` 涵蓋四大規則之正反例測試。
  - **驗收標準（DoD）**：
    - 產出 `docs/agent-autoloop-event-sourcing-and-ttl-spec.md`、`tools/verify_autoloop_dispatch_guard.py` 與 `tests/test_verify_autoloop_dispatch_guard.py`。
    - `python tools/verify_autoloop_dispatch_guard.py` 回傳 `[PASS]`（exit 0）。
    - `python -m unittest tests/test_verify_autoloop_dispatch_guard.py -v` 全數通過。
  - **實作紀錄 / 證據**：已完成 `docs/agent-autoloop-event-sourcing-and-ttl-spec.md`、`tools/verify_autoloop_dispatch_guard.py` 與 `tests/test_verify_autoloop_dispatch_guard.py`；執行 `python tools/verify_autoloop_dispatch_guard.py` 輸出 `[PASS] Agent Autoloop 四層派工安全防線檢驗通過。`，執行單元測試 `Ran 6 tests — OK`。 **退回（2026-11-14，獨立審查）**：`tools/verify_autoloop_dispatch_guard.py:99` 只檢查 prompt，漏掉 command 欄位（規格 :48 要求）；:189 空 JSON `{}` 回 PASS；:134 跳數 1→7 放行（規格要求 parent+1）；:177 放行 Administrators（規格只允許本人與 SYSTEM）。
