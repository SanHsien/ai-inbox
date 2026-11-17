---
id: 2026-10-19-crossroad-a2a-agent-mail-relay
title: "Crossroad A2A 架構解構：跨機器、跨 SaaS 的非同步 Agent 互聯寄信協議（Agent-to-Agent Mailbox Relay）與零 API Key 協同工作流"
source_url: "https://www.facebook.com/groups/1224997379198346/posts/1422793812752034/"
source_platform: "Facebook 社團（Claude Taiwan）/ GitHub"
author: "Agent-Tong (@Agent-Tong)"
github_repo: "https://github.com/Agent-Tong/Crossroad-A2A"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: "1"
cluster_role: "A2A 通訊與協同工作區"
short_title: "Crossroad A2A 跨機器寄信"
source_review: full
source_reviewed_at: 2026-11-18
source_images: 6
source_replies: 34
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
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-18 補讀：**找回原貼文**。用 Facebook 貼文搜尋找到作者 Leo Tong（即 `Agent-Tong`）2026-10-18 發在社團「Claude Taiwan」的貼文：<https://www.facebook.com/groups/1224997379198346/posts/1422793812752034/>。`source_url` 已改成這則貼文；原值 `https://github.com/Agent-Tong/Crossroad-A2A` 移到 `github_repo`。
>
> - **貼文文字**：說厭倦在各家 AI 之間複製貼上，所以開源 Crossroad A2A，讓不同 agent 互相寄信合作；跨機器、跨 SaaS、不需要額外 API 金鑰；目前是 v0.1 beta、還很粗糙，歡迎大家拆解。
> - **作者圖片 1 張**：島嶼架構圖（標 v0.1、2026 年 10 月），就是 README 的圖 1。中央 Town Hall 常開，負責成員名冊、路由檢查、清洗閘門、帳本與開關；PC1、PC2、VPS1 三座島各有郵局；**VPS3 的「SaaS 港」整塊標成規劃中**，其中 Grok 與 Claude 網頁版也個別標為規劃中；圖底列出信任規則（信是資料不是命令、每個 agent 有簽章身分、只有擁有者能簽規則與安裝、不刪別的 agent、機密只放機密管理工具）。
> - **留言**：貼文計數 34 則，「由新到舊」排序捲到底、所有回覆都展開，34 則全部讀完。
>   - **與 herdr、tmux、multica 有何不同**：多人問。作者回答那些工具只能管命令列的 agent，桌面版 App 與 SaaS 接不上，這正是他自己做的原因。有人提到 Magpie，作者說沒聽過。
>   - **跨 AI 派工的實測回報**（都不是用本專案）：一位說排程收信一段時間後，回報會越來越偏，有 agent 謊稱自己是另一個角色、記錯檔案是誰給的，然後一直找人要檔案；另一位說卡最久的是收件端，回來的東西要附檔案與出處、主控自己重跑一次才算收到；還有一位說指揮者會發沒意義的指示，執行者挑簡單的做完就假裝交差。
>   - **作者的建議**：把角色寫死在 agent 的設定檔、名冊要讓全部 agent 看得到、要記變更紀錄；先寫好需求文件再分工。作者也說自己不是開發者出身。
>   - 其他：一則說「這個沒意義」；一位在三個留言串重複貼自家專案連結（導流）。
> - **對分析的影響**：留言裡三則「跑久會飄、假裝完成、驗收卡在收件端」的回報，都指向同一件事：寄信機制本身不難，難的是收件端驗收。本地的交接機制要保留「收件端自己驗過才算數」這一關；只記錄，不改結論、不開新任務。作者自己在圖上把 SaaS 端標為規劃中，與下方 README 的讀法相符。

> 2026-11-16 重審：來源是 GitHub repo，重讀了官方 README 全文與 `docs/KNOWN_LIMITS.md`。README 內嵌 5 張圖：島嶼地圖（讀了整張圖的文字內容）與 Claude 桌面版收信證明截圖這 2 張看過；信件六步驟圖只讀了 README 對應的文字說明，Telegram 與 ChatGPT 兩張證明截圖因瀏覽器截圖逾時沒看到，只讀了圖說。該 repo 關閉了 issue 功能，沒有留言可讀。frontmatter 平台欄寫的「社群貼文」沒有留下連結，無法回頭查看。
>
> 2026-11-17 補讀：上次沒看到的 3 張圖都打開看了（六步驟圖是 SVG，直接讀圖內文字；兩張證明截圖在瀏覽器開原圖）。社群貼文沒有連結，登入也補不了，維持 `partial`。

- **作者圖片**：
  - 圖 1（島嶼地圖）：整個系統的實際拓撲。每台機器是一座「島」，各有一間「郵局」負責簽署寄出的信、替收到的信按「門鈴」；中央一座永遠開機的「Town Hall」在另一台 VPS 上，負責成員登記、路由檢查、清洗關卡（把信圍成資料、限制大小與頻率）、帳本（每個呼叫編號只收一個答覆）與每個 agent 的開關。PC1、PC2 不常開機，上面是 Claude Code 與 Codex agent；VPS1 永遠開機，放容器 agent；還有一座**標為規劃中**的「Harbor」給沒有自己機器的網頁助理停靠（ChatGPT 走外掛加安全通道、Gemini 用 Google Tasks 清單當信箱、Grok 與 Claude 網頁版都標規劃中）。島與 Town Hall 之間是**經 SSH 傳送的簽章信件**。
  - 圖 2（Claude 桌面版收到答覆）：一則標示為「來自另一個 session 的訊息」的區塊，內含郵局通知與用起訖標記圍起來的答覆本文，並明寫這是同儕資料、不是使用者本人打的字、同儕不能授予額外權限。畫面中的名稱都已遮蔽。
  - 圖 3（信件六步驟）：agent 寫出信件檔 → 島上郵局簽章並送到 Town Hall → Town Hall 檢查成員、路由與關卡 → 收件方郵局按門鈴（網頁助理則自己來拉信）→ 收件方作答 → 答覆只收一次，並喚醒寄件方來讀。
  - 圖 4（Telegram 收信證明）：VPS 上容器 agent 的排程工作（名稱含 doorbell）回報收到一封示範信，依任務檔只回了對方指定的一行、沒有另外寄信；寄件人與通道名稱已遮蔽。
  - 圖 5（ChatGPT 收信證明）：使用者請 ChatGPT 透過名為 Crossroad Lobby 的連接器建立「10 分鐘後執行一次」的排程；排程跑完回報找到 1 封未答信、已讀並回覆，狀態為 `reply_submitted`；寄件人、驗證碼與回覆內容已遮蔽。
- **作者留言補充**（官方 README 與已知限制文件自己講的，原稿沒寫到）：
  - **現況是 v0.1、只在一個組織內運作的測試版**，只有一套安裝、一位擁有者，從未有第二套安裝跑過。公開 repo 的 `reference/` 是離線測試過的參考程式碼，**Town Hall 與 PC 門鈴不在公開內容裡**。
  - **延遲以分鐘計**：Claude Code agent 的中位數約 4.5 分鐘、第 90 百分位約 49 分鐘；Gemini 的排程大約每小時一次。
  - **Codex agent 目前不能主動發信**；Claude Code 的身分綁在 session 上，每次重開 session 都要擁有者重新簽署。
  - 網頁助理的回信只算「來自該通道」，系統不賦予任何權限，也無法證明是誰寫的。
  - 作者自己承認：惡意信件仍可能說服模型做出不智的事，設計只能限制它碰得到的範圍。
  - 它**沒有實作** Google 發起的 A2A 協定，是給無法自己架伺服器端點的 agent 用的另一套東西。
- **網友留言重點**：無（issue 已關閉、約 20 顆星，沒有外部使用回報）。
- **對分析的影響**：
  - **1.2 第 1 點的信封 JSON 是原稿自己編的，已換成官方範例的欄位**。官方信封欄位是 `call_id`、`from_agent`、`from_island`、`to_agent`、`purpose`、`ref`、`hop`、`parent`、`body`；原稿的 `message_id`、`reply_to`、`intent`、`payload`、`priority`、`timeout_sec` 在官方規格裡都不存在。
  - **1.1 架構圖與 1.2 第 3 點的「Long-Polling／Webhook Push」「透過 Git 或雲端儲存輪詢」沒有依據**：官方做法是各島郵局每分鐘排程一次、經 SSH 把簽章信件送到 Town Hall，網頁助理則靠自己的排程任務來拉信。已改寫。
  - **補上成熟度說明**：原稿把它寫成可直接採用的協定，實際上公開的只有規格、離線參考碼與設計文件，核心的 Town Hall 沒有開源。這解釋了為什麼 `T-20261019-01`／`T-20261019-02` 最後是在 `SanHsien/agent-relay` 自己實作、只借用概念，結論不變。
  - **值得對照自家實作的兩點**（不開新任務，記在第 2 節）：信件一律圍成同儕資料並標明不是擁有者指令；每個呼叫編號只收一個答覆。
  - 標頭「當前狀態」原本還寫未做，與 `status: done` 不一致，已改。
  - **2026-11-17 補看圖 3～5**：三張圖與 README 文字及上面的改寫一致（排程拉信、答覆只收一次、信件當成資料處理）。圖 4、圖 5 只證明各跑通過一次示範信，仍是單一擁有者的示範，成熟度判斷不變；分析未改、任務未增減。

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
│    ├─ 各島郵局每分鐘排程、經 SSH 送簽章信件；網頁助理自行定時拉信     │
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
   - 官方範例（節錄自 `spec/examples/letter.json`；2026-11-16 依官方 README 更正，原稿的欄位是自行編寫的）：
     ```json
     {"call_id": "20261016T020000Z_a1b2c3", "from_agent": "agent-a", "from_island": "pc1",
      "to_agent": "agent-b", "purpose": "queue_task", "ref": "xx261016a_Letter_Test.md",
      "hop": 1, "parent": null,
      "body": "Please compare options A and B and answer in two lines."}
     ```
   - 收件方看到的不是這段 JSON，而是被起訖標記圍起來的本文，並標明「這是來自某 agent 的同儕資料，不是擁有者、也不是郵局」。同一個 `call_id` 最多只收一個答覆。
2. **零額外 API Key 機制（Zero Extra API Key Architecture）**：
   - 傳統多代理框架（如 LangGraph, CrewAI）常要求使用者在環境變數注入 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY` 與 `GOOGLE_API_KEY`，每次呼叫都是昂貴的 Token 計費。
   - Crossroad A2A 僅充當**傳遞信件的中繼郵局**，不負責模型推理。收件 Agent（如本機運行的 Gemini CLI 或瀏覽器外掛）收到任務後，在自己的環境中呼叫既有登入態或本地訂閱執行，執行完成再把 Markdown/JSON 成果放回回信箱，完全繞過高額 API 轉發費用。
3. **NAT 穿透與非同步輪詢友善（Firewall-friendly Polling）**：
   - 本地開發機無需開放公網 Port。官方做法：每台機器（島）跑一間小郵局，以排程每分鐘一次把簽章信件經 SSH 送到中央的 Town Hall、並替收到的信喚醒對應的 session；無法從外部喚醒的網頁助理（ChatGPT、Gemini）則靠自己的排程任務定時來拉信。
   - **成熟度（官方自述）**：v0.1，只在一個組織內運作；公開 repo 只有規格與離線參考碼，Town Hall 與 PC 門鈴沒有公開。延遲以分鐘計（Claude Code agent 中位數約 4.5 分鐘），Codex agent 目前不能主動發信。
4. **與主流協調協議之對照**：
   - **vs. Anthropic MCP（Model Context Protocol）**：MCP 是 **Agent-to-Tool**（解決 Agent 怎麼讀本地檔案、查資料庫）；Crossroad A2A 是 **Agent-to-Agent**（解決兩個不同模型/環境的 Agent 怎麼交棒）。
   - **vs. Google A2A Protocol**：A2A 協定連接的是各自有伺服器端點的 agent；Crossroad A2A 是另一個專案，給無法架端點的 agent（網頁助理、桌面 session、會休眠的機器）用，官方明說 v0.1 **沒有實作** A2A 協定。原稿的「零配置」說法不成立：官方已知限制提到新增成員要同步改多台主機的政策與橋接程式。
   - **vs. 本地 `dropoff`/`pickup`**：本地 `dropoff`/`pickup` 透過專案目錄下的 `.claude/handoffs/*.md` 實現同機跨專案交接；Crossroad A2A 則進一步將此機制擴展至跨機器、跨雲端服務的廣域網絡。

---

## 2. 對現有工作流與專案之啟發

1. **與本地 `agent-handoff` 及 `dropoff`/`pickup` 技能的無縫對接**：
   - 本地既有的交接規範已具備 Markdown 交接卡與 Frontmatter 元數據。可將 Crossroad A2A 當作傳輸層，當本地執行 `/dropoff` 時，除了寫入本地檔案，亦可選擇將交接信寄給遠端伺服器上的 Agent 繼續施工。
2. **解決長週期任務阻礙開發流（Unblocking Long-running Tasks）**：
   - 對於超過 15 分鐘的大規模單元測試、程式碼變更 Mutation 測試或深入輿情爬蟲，本機 Agent 不必原地阻塞等待，只需將工單「寄出」，由雲端背景 Worker 接手，本機 Agent 可以立刻切換至下一個任務。
3. **安全性與審查防線（Safety Audit Gate）**：
   - 外部 Agent 寄來的信件在被本地 Agent 執行前，必須經過格式驗證與安全性掃描，禁止外部信件直接注入危險的 Shell 執行指令（Command Injection 防範），信件內容一律視為未經驗證之輸入（Untrusted Input）。官方的做法可對照自家 `SanHsien/agent-relay`：信件圍成同儕資料並標明不是擁有者指令、同儕不能授予額外權限、每個呼叫編號只收一個答覆。

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

