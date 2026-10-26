---
id: 2026-10-19-crossroad-a2a-agent-mail-relay
title: "Crossroad A2A 架構解構：跨機器、跨 SaaS 的非同步 Agent 互聯寄信協議（Agent-to-Agent Mailbox Relay）與零 API Key 協同工作流"
source_url: "https://github.com/Agent-Tong/Crossroad-A2A"
source_platform: "GitHub / 社群貼文"
author: "Agent-Tong (@Agent-Tong)"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 1
cluster_role: "訊息傳輸"
short_title: "Crossroad A2A 跨機器寄信"
tags:
  - a2a
  - crossroad-a2a
  - multi-agent
  - agent-mailbox
  - inter-agent-communication
  - async-relay
---

# Crossroad A2A 架構解構：跨機器、跨 SaaS 的非同步 Agent 互聯寄信協議（Agent-to-Agent Mailbox Relay）與零 API Key 協同工作流

- **來源連結**：[Agent-Tong/Crossroad-A2A (GitHub)](https://github.com/Agent-Tong/Crossroad-A2A)
- **發布平台 / 原作者**：`GitHub / 社群貼文` / `Agent-Tong (@Agent-Tong)`
- **分析日期**：`2026-10-19`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要

### 1.1 核心主張：終結「人肉搬運工」，以非同步「寄信（Mailbox）」機制打通異構 Agent 孤島

在當前多模型共存的開發日常中，許多工程師都面臨嚴重的「AI 孤島」與「人肉 Router」痛點：
- 在 **Claude Code** 規劃好架構後，手動複製 Prompt 貼到 **Gemini 網頁版** 查 YouTube 與多模態資料；
- 等待 **ChatGPT** 跑長週期排程或深度研究時，必須守在螢幕前手動將產出貼回本地終端；
- 部署在雲端 VPS 伺服器上的自動化 Agent 出現異常時，無法跨網路直接把錯誤通知推給本機或手機。

傳統的解決方案通常要求建立中心化的 API 代理伺服器，但這會帶來三大障礙：
1. **高昂且重複的成本**：需要為每個服務重新購買官方 API Key，無法復用既有網頁端/CLI 訂閱（Pro/Max 配額）；
2. **網路拓撲壁壘**：個人開發機通常位於 NAT/家用網路內，缺乏公網固定 IP，難以接收外部 Webhook；
3. **即時長連接負擔**：WebSocket 或 P2P 保持長連接極易因休眠、斷網或 SaaS 速率限制而中斷。

**Crossroad A2A（Agent-to-Agent）** 提出了回歸網際網路最穩定基石的設計哲學——**「非同步信箱中繼（Mailbox Relay / 寄信機制）」**：
> 讓不同 AI Agent 擁有自己的「電子信箱（Mailbox）」，彼此透過標準信封（Envelope）互相寄信。Claude 可以主動發信請 Gemini 查資料、ChatGPT 凌晨排程跑完自動回信、伺服器 Agent 透過信箱觸發 Telegram 通知，實現完全非同步、跨機器、跨 SaaS、零額外 API Key 的自治協同。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Crossroad A2A 非同步信箱中繼架構全景                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 跨 SaaS / 跨環境異構 Agent 節點 (Heterogeneous Agent Nodes)        │
│    ├─ 本地 CLI 節點: Claude Code / Codex CLI / Antigravity             │
│    ├─ 雲端 SaaS 節點: ChatGPT Plus (Scheduled Tasks) / Gemini Advanced │
│    └─ 背景服務節點: VPS Linux Worker / CI Runner / Telegram Bot       │
│                                                                        │
│ 2. 標準化 Agent 任務信封 (A2A Message Envelope Specification)          │
│    └─ 包含: from, to, reply_to, task_id, intent, payload, callback    │
│                                                                        │
│ 3. 非同步信箱中繼站 (Crossroad Mailbox Relay Hub)                       │
│    ├─ 虛擬信箱路由 (Inboxes & Outboxes): 每個 Agent 獨立隊列          │
│    ├─ NAT 穿透與非同步輪詢 (Long-Polling / Webhook Push)              │
│    └─ 零額外 API Key 原則: 僅傳遞任務描述，執行依然消耗各 Agent 原生環境 │
│                                                                        │
│ 4. 閉環協同場景 (Collaborative Use Cases)                             │
│    ├─ 場景 A: 本地 Claude 發信委託 Gemini 查 YouTube 影音數據並收信    │
│    ├─ 場景 B: ChatGPT 排程任務凌晨離線執行完畢，回信通知本地接手       │
│    └─ 場景 C: 伺服器巡檢 Agent 發現錯誤，寄信轉發手機 Telegram 即時告警 │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 核心技術機制深度剖析

```
[Crossroad A2A 非同步寄信工作流]

  +-----------------------+                         +-----------------------+
  |    Local Agent A      |                         |    Remote Agent B     |
  |  (例如: Claude Code)  |                         |  (例如: Gemini / VPS) |
  +-----------+-----------+                         +-----------+-----------+
              |                                                 ^
              | 1. 發送任務信 (Send Mail)                       |
              |    To: gemini-research                          |
              |    Intent: "query_youtube"                      | 4. 輪詢/Webhook
              v                                                 |    領取信件
    ===================================================================
    |                Crossroad A2A Mailbox Relay                      |
    |                                                                 |
    |  [Inbox: claude-local]             [Inbox: gemini-research]     |
    |    (等待回信中)                      +-----------------------+  |
    |                                      | Message: ID-1002      |  |
    |                                      | From: claude-local    |  |
    |                                      +-----------------------+  |
    ===================================================================
                                                                |
                                                                v
                                                    +-----------------------+
                                                    | Agent B 本地獨立執行  |
                                                    | (使用自己的帳號/工具) |
                                                    +-----------+-----------+
                                                                |
              ^                                                 | 5. 回寄成果信
              |                                                 |    To: claude-local
              | 6. 輪詢/通知收取回信                            v
    ===================================================================
    |  [Inbox: claude-local]             [Inbox: gemini-research]     |
    |    +-----------------------+                                    |
    |    | Result: ID-1002       |                                    |
    |    | From: gemini-research |                                    |
    |    +-----------------------+                                    |
    ===================================================================
              |
              v
  +-----------------------+
  |    Local Agent A      |
  |  無縫消化資料繼續推進  |
  +-----------------------+
```

1. **標準任務信封（Message Envelope Specification）**：
   - 規定了最簡且具備自解釋性的 JSON 格式：
     ```json
     {
       "message_id": "msg_20261019_9981",
       "from": "claude-code@mac-mini",
       "to": "gemini-research@cloud",
       "reply_to": "claude-code@mac-mini/inbox",
       "intent": "youtube_deep_research",
       "context": "正在調研視頻動效程式庫...",
       "payload": {
         "query": "Remotion vs Motion Canvas 2026 performance",
         "required_fields": ["video_url", "summary", "benchmark_metrics"]
       },
       "priority": "normal",
       "created_at": 1776558157,
       "timeout_sec": 3600
     }
     ```
2. **零額外 API Key 機制（Zero Extra API Key Architecture）**：
   - 傳統多代理框架（如 LangGraph, CrewAI）常要求使用者在環境變數注入 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY` 與 `GOOGLE_API_KEY`，每次呼叫都是昂貴的 Token 計費。
   - Crossroad A2A 僅充當**傳遞信件的中繼郵局**，不負責模型推理。收件 Agent（如本機運行的 Gemini CLI 或瀏覽器外掛）收到任務後，在自己的環境中呼叫既有登入態或本地訂閱執行，執行完成再把 Markdown/JSON 成果放回回信箱，完全繞過高額 API 轉發費用。
3. **NAT 穿透與非同步輪詢友善（Firewall-friendly Polling）**：
   - 本地開發機無需開放公網 Port，各 Agent 端只需安裝一個輕量級的 CLI Daemon 或透過 Git/雲端儲存進行定時 Polling（例如每分鐘檢查一次收件匣，或在 Agent 即將進入下一個推理循環前檢查有無新信）。
4. **與主流協調協議之對照**：
   - **vs. Anthropic MCP（Model Context Protocol）**：MCP 是 **Agent-to-Tool**（解決 Agent 怎麼讀本地檔案、查資料庫）；Crossroad A2A 是 **Agent-to-Agent**（解決兩個不同模型/環境的 Agent 怎麼交棒）。
   - **vs. Google A2A Protocol**：Google A2A 偏向企業級 RPC 與 Service Discovery；Crossroad A2A 偏向個人開發者的輕量級非同步信箱，強調零配置與跨 SaaS 適用性。
   - **vs. 本地 `dropoff`/`pickup`**：本地 `dropoff`/`pickup` 透過專案目錄下的 `.claude/handoffs/*.md` 實現同機跨專案交接；Crossroad A2A 則進一步將此機制擴展至跨機器、跨雲端服務的廣域網絡。

---

## 2. 對現有工作流與專案之啟發

1. **與本地 `agent-handoff` 及 `dropoff`/`pickup` 技能的無縫對接**：
   - 本地既有的交接規範已具備 Markdown 交接卡與 Frontmatter 元數據。可將 Crossroad A2A 當作傳輸層，當本地執行 `/dropoff` 時，除了寫入本地檔案，亦可選擇將交接信寄給遠端伺服器上的 Agent 繼續施工。
2. **解決長週期任務阻礙開發流（Unblocking Long-running Tasks）**：
   - 對於超過 15 分鐘的大規模單元測試、程式碼變更 Mutation 測試或深入輿情爬蟲，本機 Agent 不必原地阻塞等待，只需將工單「寄出」，由雲端背景 Worker 接手，本機 Agent 可以立刻切換至下一個任務。
3. **安全性與審查防線（Safety Audit Gate）**：
   - 外部 Agent 寄來的信件在被本地 Agent 執行前，必須經過格式驗證與安全性掃描，禁止外部信件直接注入危險的 Shell 執行指令（Command Injection 防範），信件內容一律視為未經驗證之輸入（Untrusted Input）。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261019-01`**｜**[優先級：高]** 深入評估 Crossroad A2A 寄信協議規格（信件 Envelope 結構、非同步收件匣 Polling 與 Webhook 中繼），設計適配本地 Claude Code / Codex / Antigravity 的 CLI 信箱適配器（Mailbox Client Adapter）
  - **目標範圍**：`SanHsien/agentdeck` ＋ `SanHsien/xiaoke-claude-memory`（私有）
  - **驗收標準（DoD）**：復用 `agentdeck` 輪詢機制實作輕量 CLI Mailbox Client，Agent 能讀寫 JSON Envelope 信件並有實際收發紀錄
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：協定與 CLI 在 [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay)（`99f3dc8`，Envelope v1 規格見 SPEC.md，34 項單元測試通過，含雙 clone 經 git 遠端收發）；store 為 `SanHsien/xiaoke-claude-memory`（私有） 的 `mailbox` 分支；輪詢沿用 agentdeck 排程做法（`StartWhenAvailable`），agentdeck 托盤新信通知 `b49486f`、`514e349`。實測一封派工信 `…165506382Z-9ba7aa` commander→codex，工人回信 `…165619565Z-9bc015`，雙方 ack，store 留 6 筆 git 紀錄。紀錄：agent-relay `docs/evidence/2026-10-20-phase1.md`。限制：兩台機器以同一主機的兩份 clone 模擬；工人由 Claude 子 agent 扮演（Codex 沙箱外網路權限被自動模式擋下）。
- [x] **`T-20261019-02`**｜**[優先級：中]** 整合本地現有 `dropoff` / `pickup` 與 Crossroad A2A 中繼架構，實作免公網 IP 與免額外 API Key 的跨機器 Agent 門鈴通知與任務接力原型
  - **目標範圍**：`SanHsien/agent-session-restore` ＋ `SanHsien/line-desktop-mcp` ＋ `SanHsien/xiaoke-claude-memory`（私有）
  - **驗收標準（DoD）**：發信時觸發跨 Agent / 機器 / 手機端門鈴通知，實測一次完整接力
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：[SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) 的 `watch --once` 門鈴（toast／command／handoff）＋ Windows 排程輪詢；`--project asr:<會話名>` 從 agent-session-restore 登記檔查專案路徑；handoff 門鈴產生 dropoff/pickup 交接卡。實測：commander 寄 `…165758924Z-a805c6` → 第二台機器桌面通知 ok、Telegram 手機通知 ok、交接卡 ok → 新 session 接手（pending→picked→done）並回信 `…165845229Z-19470f` → commander 端排程工作 `agent-relay-watch-commander` 拉信並通知（00:59:20）。全程免公網 IP、免新增 API key（git push/pull＋既有 Telegram 腳本）。限制：line-desktop-mcp 每次傳送須人確認，未接成自動門鈴；同上為單主機雙 clone 模擬。

---

## 4. 關聯筆記、會話溯源與相關任務（Related Notes & Sessions）

- **歷史會話溯源與推進脈絡**：
  - 前序創世 Session（內部紀錄，未公開） ｜ 跨 Agent 中立資產與非同步協同演進起點
  - 本規劃落地 Session（內部紀錄，未公開） ｜ 訊息中繼（Phase 1）與跨 Agent 門鈴派工架構落實
- **共同大腦與架構整合**：
  - [AI 共同大腦工業級架構規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [多 Agent 工廠：Magpie 統一網關與 Herdr 終端復用](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261018-16`
- **跨 CLI 調度與派工協議**：
  - [跨 CLI 多代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`

