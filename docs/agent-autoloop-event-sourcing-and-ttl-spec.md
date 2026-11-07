# Agent Autoloop 事件溯源內核、掛起零消耗與四層安全防線規格

> 對應任務：`T-20261108-02`｜來源筆記：[`notes/2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md`](../notes/2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md)
> 參考開源專案：[`KKKKhazix/agent-autoloop`](https://github.com/KKKKhazix/agent-autoloop)（MIT License）
> 機械檢驗腳本：[`tools/verify_autoloop_dispatch_guard.py`](../tools/verify_autoloop_dispatch_guard.py)｜單元測試：[`tests/test_verify_autoloop_dispatch_guard.py`](../tests/test_verify_autoloop_dispatch_guard.py)

---

## 1. 核心架構：為什麼背景常駐 Agent 需要「無狀態行程 + 事件溯源內核」

傳統命令列 Agent（Claude Code、Codex、Hermes）在執行長程或需人類確認的任務時，若維持互動式終端常駐等待，會同時產生三種風險：
1. **閒置資源與重複燒額**：程序常駐等待人類回覆，或因輪詢（Polling）反覆喚醒模型消耗 Context Token。
2. **中斷失憶**：視窗關閉、網路閃斷或行程崩潰後，缺乏交易式狀態日誌，重跑時被迫整輪重做或遺失已確認步驟。
3. **外部事件注入與無限迴圈**：接上 GitHub Issue / Webhook 後，外部不可信文字若直接拼入 Prompt，或 Agent 產生的事件再次觸發下游 Agent，極易引發權限劫持與 Token 燒乾迴圈。

`KKKKhazix/agent-autoloop` 將調度中台拆解為「**1,850 行零依賴純函式內核（`kernel/`）** + **I/O 外殼（`host/`）** + **四大插件面（Source / Agent / Channel / Delivery）**」：

```text
[外部事件 Source] (GitHub Issue / Cron / Webhook)
       │ 1. 僅傳遞標準事件 (禁止攜帶 cwd / agent / access)
       ▼
[事件溯源內核 Kernel] (純函式：不讀時鐘、不用隨機數、SQLite WAL+FULL 單一交易落盤)
       │ 2. 依本機 rules.json 匹配 Agent 與目錄；外部正文寫入獨立 context.json
       ▼
[接單程序 Worker] ──啟動──▶ [CLI Agent (Claude / Codex / ACP)]
       │                        │ 3. 輸出最後一條回覆 + ```agent-autoloop 回執區塊
       │ 4. 行程立即退出 (0 RSS / 0 Token)
       ▼
[內核解析回執]
  ├─ 完成 (無待決項) ────────────────────▶ 寫入完成事實，結案
  ├─ 預約複查 (later) / 新事件 (events) ─▶ 累加 hop 計數 (TTL <= 8，不可清零)
  └─ 拿不準請示 (ask) ──────────────────▶ 推送拍板卡片 (飛書 / Slack / 桌面通知)
                                                │
                                                ▼ 5. 人類點擊卡片或執行 answer
                                          以 --resume 接回原會話 ID 繼續完成
```

---

## 2. 四大安全與防呆契約（由 `verify_autoloop_dispatch_guard.py` 機械校驗）

### 2.1 契約一：路由與權限欄位隔離（Route Override Guard — `AUTOLOOP-001`）
- **規則**：外部傳入的事件（Event Payload）只能描述「發生了什麼事」，**嚴禁包含任何可影響派工目標或執行環境的控制欄位**：
  - 禁止欄位：`cwd`、`agent`、`to`、`access`、`program`、`command`、`skill`、`parallel`。
- **理由**：用哪個 Agent、在哪個工作目錄、開什麼沙盒權限，必須 100% 由本機受保護的 `rules.json` 決定；若允許事件覆寫這些欄位，攻擊者發一個特製 Issue 或 Webhook 即可指定 `cwd: "/"` 與 `access: "full"`。

### 2.2 契約二：指令與外部資料分離（Prompt Parameterization Guard — `AUTOLOOP-002`）
- **規則**：`rules.json` 中的 `prompt` 與 `command` 模板，**禁止直接內插未受信任的外部自由文本欄位**（如 `{body}`、`{title}`、`{issue_body}`、`{comment}`、`{description}`、`{payload}`）。
- **允許的參數化佔位符**：僅允許經嚴格字元白名單（`^[A-Za-z0-9._:/-]+$`）校驗的識別元：
  - `{type}`、`{id}`、`{link}`、`{context_file}`。
- **理由**：比照 SQL 參數化查詢（Parameterized Query），外部 Issue 標題與內文一律寫入獨立資料檔（如 `context.json`），不在組裝階段直接拼入指令或系統提示詞。

### 2.3 契約三：跳數熔斷與單調遞增（TTL Hop Limit Guard — `AUTOLOOP-003`）
- **規則**：
  1. 派工事件鏈的跳數 `hop` 必須隨每次派生事件單調遞增（`child.hop == parent.hop + 1`）。
  2. **經過人工提問（`ask`）或定時複查（`later`）時，`hop` 嚴禁歸零或倒退**，且 Agent 回執不得自行修改 `hop`。
  3. 當 `hop > max_hops`（預設 `max_hops = 8`）時，內核必須拒絕再次派活（`action == "drop_and_alert"`），僅寫入日誌並發送熔斷告警卡片。
- **理由**：防止兩個 Agent 互相拋出事件，或 Agent 利用 `later` 定時喚醒自己造成無限迴圈燒光 API 配額。

### 2.4 契約四：反自問自答與 Windows 沙盒 ACL 隔離（Anti-Self-Approval & ACL Guard — `AUTOLOOP-004`）
- **規則**：
  1. **禁止 Worker 掛載審批工具**：接單 Worker 所啟動的 CLI Agent，其可用工具／MCP 清單不得包含卡片拍板或權限核准操作（如 `autoloop_answer`、`answer_card`、`approve_delivery`、`mcp__autoloop__answer`），否則 Agent 可在單輪內自己發卡、自己回答拍板。
  2. **禁止 PR 檢出執行**：交付流水線（`delivery`）審查外部 PR 時，`checkout_pr_code` 必須為 `false`，且對 Octopus merge（多父節點章魚合併）必須拒絕自動放行。
  3. **Windows 資料目錄 ACL 收斂**：在 Windows 環境下（特別是與 Codex 沙盒並存時），中台資料目錄（含 `hub.db`、`master.key`、`secrets.env`）的允許存取主體僅限當前使用者帳號與 `SYSTEM`，不得殘留沙盒群組或 `Everyone` / `Users` 讀取權限。

---

## 3. 驗證指令

```powershell
# 執行預設自檢（涵蓋四大契約的正反例驗證）
python tools/verify_autoloop_dispatch_guard.py

# 驗證外部派工設定與事件鏈 JSON 檔案
python tools/verify_autoloop_dispatch_guard.py --config path/to/autoloop_bundle.json --json
```
