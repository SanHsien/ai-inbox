---
id: 2026-10-19-ai-shared-brain-multi-agent-architecture
title: "「AI 共同大腦（AI Shared Brain）」工業級架構全景規劃：集中知識中樞、打卡審計、結構化交接記憶與額度感知動態調度的工程實踐"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "內部規劃 / 實戰協作論壇"
author: "AI 協同開發實戰者 / Antigravity"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 1
cluster_role: "總綱中樞"
short_title: "AI 共同大腦全景規劃"
tags:
  - ai-shared-brain
  - multi-agent-architecture
  - central-knowledge-hub
  - audit-checkin
  - agent-handoff
  - quota-router
---

# 「AI 共同大腦（AI Shared Brain）」工業級架構全景規劃：集中知識中樞、打卡審計、結構化交接記憶與額度感知動態調度的工程實踐

- **來源連結**：[SanHsien/ai-inbox (GitHub)](https://github.com/SanHsien/ai-inbox) ｜ 實戰社群「多 Agent 工廠」交流節錄
- **發布平台 / 提案者**：`內部架構規劃 / 實戰協作論壇` / `AI 協同開發實戰者 ＆ Antigravity`
- **分析日期**：`2026-10-19`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要

### 1.1 核心主張：超越「單兵作戰」，為多模型與異構 Agent 打造統一的認知與調度中樞

在日常開發中，同時調用 **Claude Code、Codex CLI、Antigravity、Cursor、Gemini 與本機開源模型** 已成為常態。然而，傳統的多代理使用方式往往陷入嚴重的混亂：
1. **認知碎片化與記憶斷裂**：每個 Agent 各自封閉在獨立的 Context Window 中，換個終端、重開 Session 或切換模型，前一個 Agent 踩過的坑與累積的上下文立刻遺失；
2. **無序讀寫與知識漂移**：多個 Agent 隨意修改專案程式碼與技能庫（Skills），缺乏簽入/簽出（Check-in/Check-out）審計，造成代碼互相覆蓋與架構規則被默默竄改；
3. **額度盲踩與資源浪費**：缺乏全局配額感知，常常用昂貴的旗艦模型（如 Opus）執行簡單的文字批次，或在龐大任務進行到一半時觸發 Rate Limit 導致卡死中斷；
4. **人肉轉發的低效搬運**：開發者在不同終端間手動複製 Prompt 與程式碼，淪為「人肉訊息路由器」。

**「AI 共同大腦（AI Shared Brain）」** 的核心理念是：**它不是單一的超大模型，而是一個跨模型、跨 Agent、跨機器的「外部化認知與協同作業系統」**。
它將「共用知識庫」、「審計打卡」、「交接單記憶」、「額度感知調度」與「非同步信箱」五大支柱緊密咬合，讓所有 Agent 在一個統一的規約下井然有序地協同施工。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   「AI 共同大腦（AI Shared Brain）」架構全景              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 集中資料中心與打卡審計 (Central Knowledge Hub & Check-in Audit)      │
│    ├─ Git / 雲端集中管理所有專案代碼、Skills 庫與全域協作規範 (Global Rules) │
│    └─ 嚴格簽入/簽出審計: Agent 進去拿資料、改東西都要打卡，杜絕知識漂移    │
│                                                                        │
│ 2. 結構化接棒與教訓記憶層 (Structured Handoff & Lessons Memory Layer)    │
│    ├─ 以 Obsidian / Markdown 檔案維護結構化交接單 (Handoff Cards)        │
│    └─ 前車之鑑自動召回 (Lessons Learned): 錯誤發生時立刻沉澱，下個 Agent 秒懂 │
│                                                                        │
│ 3. 額度感知與複雜度動態路由 (Quota-Aware & Complexity Dispatcher)       │
│    ├─ 即時監控各家模型配額、速率限制 (Rate Limit) 與重置倒數時間        │
│    └─ 指揮官 Agent 前置評估工單規模 ──> 動態指派性價比最高之模型施工     │
│                                                                        │
│ 4. 異構 Agent 終端復用與信箱中繼 (Multiplexer & Mailbox Relay)          │
│    ├─ Herdr: 狀態感知終端復用 (Working / Waiting Input / Done / Error)  │
│    └─ Crossroad A2A: 跨機器、跨 SaaS 非同步寄信與 Telegram 門鈴通知     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 關鍵技術支柱深度剖析

```
[AI 共同大腦協同作業生命週期]

  +-----------------------+
  | 人類工程師 / 派工需求 |
  +-----------+-----------+
              |
              v
  +-------------------------------------------------------------+
  |              AI 共同大腦指揮官 (Brain Commander)             |
  |  1. 查閱 Obsidian 專案現況與交接單 (Handoff Cards)           |
  |  2. 查詢各家模型剩餘額度與重置倒數 (Quota Watcher)           |
  |  3. 評估任務複雜度 (架構規劃 vs. 機械批量實作 vs. 對抗性審查)  |
  +-----------------------------+-------------------------------+
                                |
             +------------------+------------------+
             | 分派給最適模型                      |
             v                                     v
  +-----------------------+             +-----------------------+
  | Agent 1 (如: Claude)  |             | Agent 2 (如: Codex)   |
  | 擔任: 架構規劃 / 審查 |             | 擔任: 本地代碼實現    |
  +-----------+-----------+             +-----------+-----------+
              |                                     |
              | 簽出打卡 (Check-out)                | 簽出打卡 (Check-out)
              v                                     v
  ===============================================================
  |             集中資料中心 (Central Knowledge Hub)            |
  |  - 專案程式碼庫 (Git Worktrees 隔離)                        |
  |  - 共用 Skills & 全域規則庫 (防改動鎖)                      |
  |  - 打卡日誌與審計軌跡 (Check-in / Change Audit Logs)         |
  ===============================================================
              ^                                     ^
              | 簽入驗證 (Check-in & Proof)         | 簽入驗證 (Check-in & Proof)
              +------------------+------------------+
                                 |
                                 v
  +-------------------------------------------------------------+
  |                 沉澱與交接 (Memory & Handoff)               |
  |  1. 產出本次施工驗證證據 (真實終端輸出)                     |
  |  2. 踩坑記錄自動追加至 Obsidian 前車之鑑 (Lessons Learned)  |
  |  3. 透過 Crossroad A2A 寄發完成信 / Telegram 通知人類驗收   |
  +-------------------------------------------------------------+
```

1. **集中資料中心與打卡審計（Central Knowledge Hub & Check-in Audit）**：
   - 所有的專案、技能庫與規範統一集中管理（如 `C:\GitHub\<repo>` 或私有雲端同步目錄）。
   - **打卡契約**：Agent 進入專案時，必須在審計日誌中註明 `[CHECK-OUT] agent_id, timestamp, task_id, target_files`；改動完成且跑過測試綠燈後，執行 `[CHECK-IN] commit_hash, proof_output, lesson_learned`。任何人與 Agent 均可回溯改動脈絡。
2. **Obsidian 接棒交接單（Handoff Boards & Shift Logs）**：
   - 解決跨 Session「接球」問題：每個階段結束時，由當前 Agent 產出一份標準化 Markdown 交接單（包含當前目標、已驗證的事實、未完成的清單、潛在風險），下一個 Session 的 Agent 只要讀取交接卡即可無縫接力，杜絕「開場問安、不知所措」的上下文浪費。
3. **額度感知與複雜度動態調度（Quota-Aware Intelligent Routing）**：
   - 透過輕量守護進程定期監控 Anthropic、OpenAI、Google 等服務的 Token 消耗與重置時間。
   - 指揮官依據工單特性動態派工：高推理架構規劃派給 Claude 3.7 / Opus；大規模機械重構或測試編寫派給 Codex / DeepSeek-V3；跨平台多模態查核派給 Gemini；完成後自動互派審查。
4. **多終端監控與非同步信箱（Herdr Multiplexer + Crossroad A2A）**：
   - 使用 Herdr 等狀態感知終端復用器，即時監控各 Pane 的進度狀態（Working、Waiting User Input、Done）；
   - 超過 15 分鐘的長運行任務（如大型編譯或爬蟲），透過 Crossroad A2A 寄信給背景 Worker，完成後透過 Telegram 通知開發者，完全釋放本地終端。

---

### 1.3 GitHub 全量倉庫實測盤點對應（15+ 現成輪子庫，免重複造輪子）

經過透過 GitHub API 對 `SanHsien` 遠端所有倉庫（[SanHsien Repositories](https://github.com/SanHsien?tab=repositories)）進行全量探勘，已有 15+ 個核心資產可直接銜接本規劃之三階段（Phase 1 ~ Phase 3）工程：

| 階段 | 關鍵作用 | 本地與遠端現有可用 Repo（直接復用） | 核心落地能力與職責邊界 |
| :---: | :--- | :--- | :--- |
| **Phase 1: Message Relay** | 非同步訊息通道 | `SanHsien/agentdeck` ＋ `SanHsien/xiaoke-claude-memory`（私有） | 復用 `agentdeck` 的定時輪詢中樞與 `SanHsien/xiaoke-claude-memory`（私有） 的郵箱結構，實作輕量 CLI Mailbox Client，使 Agent 能讀寫 JSON Envelope 信件 |
| **Phase 1: Message Relay** | 即時喚醒門鈴 | `SanHsien/agent-session-restore` ＋ `SanHsien/line-desktop-mcp` ＋ `SanHsien/xiaoke-claude-memory`（私有） | 復用 `asr` 會話喚醒機制與 `line-desktop-mcp` / `SanHsien/xiaoke-claude-memory`（私有） 門鈴，發信時觸發跨 Agent/跨機器/跨裝置（LINE）通知接力 |
| **Phase 2: Dispatch** | 跨終端開新 Session 與代理網關 | `SanHsien/agent-cortex` ＋ `SanHsien/opencodex` ＋ `SanHsien/claude-code-projects-workflow` | **直接復用原生 Windows 控制平面**（`agent-cortex`）與原生通用供應商代理（`opencodex`），結合 `claude-code-projects-workflow` 之 Worktree 派工，徹底平替 Linux 專用 tmux/Magpie |
| **Phase 2: Dispatch** | 跨 CLI 子代理派工契約 | `SanHsien/agent-advisor` ＋ `SanHsien/agy-staff` | **直接復用 `agy-staff`**（將 Antigravity CLI 作為執行端 Worker 委派給 Claude Code / Codex）與 `agent-advisor` 派工合約，定義標準輸入工單與 headless 參數 |
| **Phase 2: Dispatch** | 額度感知動態分派與斷線續跑 | `SanHsien/codex-reset-checker` ＋ `SanHsien/codex-auto-retry` ＋ `SanHsien/Antigravity-Manager` ＋ `SanHsien/agent-advisor` | 復用 `codex-reset-checker` 查額度、`Antigravity-Manager` 帳號切換與 `codex-auto-retry`（限流逾時自動原地續跑守護行程），實現智能路由分派 |
| **Phase 2: Dispatch** | 跨 Session 記憶無損繼承 | `SanHsien/claude-obsidian` ＋ `SanHsien/cc-session-reader` ＋ `SanHsien/personal-ai-os`（私有） | 復用 `claude-obsidian` 筆記同步、`cc-session-reader` 對話過濾與 `SanHsien/personal-ai-os`（私有） 指揮中心，新開 Session 自動注入 Obsidian 交接單與精簡上下文 |
| **Phase 2: Dispatch** | 集中庫打卡與簽出鎖 | `SanHsien/claude-code-projects-workflow` ＋ `SanHsien/codebase-memory-mcp` ＋ `SanHsien/harness-guard` ＋ `SanHsien/agent-environment-audits`（私有） | **直接復用 `claude-code-projects-workflow`**（平行任務 Worktree 派工前範圍檢查與合併衝突預測），結合記憶中樞與環境審計，檔案讀寫強制打卡記錄防衝突 |
| **Phase 3: Verification** | 硬性驗收防線 | `SanHsien/ai-quality-gates` ＋ `SanHsien/harness-guard` ＋ `SanHsien/agent-governance-toolkit` ＋ `SanHsien/SkillSpector` | 復用 `ai-quality-gates`（Gherkin 規格/覆蓋率）、`harness-guard`（5 個阻止 hook）、`agent-governance-toolkit`（運行期政策強制與沙箱審計）與 `SkillSpector` 技能供應鏈掃描，強制終端真實日誌 |
| **Phase 3: Verification** | 雙軌回流升級除錯 | `SanHsien/agent-advisor` (`advisor-pro-reviewer`) | 復用獨立審查員軌道，Worker 報錯時格式化提煉上下文，回送指揮官進行根因診斷與再派工 |

---

### 1.4 多 Agent 通訊、派工與驗收端到端閉環流水線（架構運作圖）

```
  【指揮官 (Brain Commander)】
            │
            ├─ 1. 查詢額度與重置時間 ──▶ [SanHsien/codex-reset-checker]
            ├─ 2. 決定派工路由與合約 ──▶ [SanHsien/agent-advisor]
            │
            ▼
  【Phase 1 & 2: 喚醒、傳遞與開新 Session】
            │
            ├─ 透過 Mailbox 協議寄送信件 ──▶ [agentdeck + SanHsien/xiaoke-claude-memory（私有）]
            ├─ 觸發即時門鈴與會話恢復 ────▶ [agent-session-restore + dropoff/pickup]
            └─ Windows 原生終端開新 Session ──▶ [SanHsien/agent-cortex] (Worktree 隔離)
                                                  │
                                                  ▼
                                      【執行工人 (Worker Agent)】
                                                  │
                                                  ├─ 讀取集中記憶與 Obsidian 交接 ──▶ [claude-obsidian + cc-session-reader]
                                                  ├─ 檔案簽出/簽入打卡防衝突 ──────▶ [codebase-memory-mcp + harness-guard]
                                                  └─ 施工並執行 TDD 驗證
                                                                │
                                                                ▼
                                      【Phase 3: 驗收、審查與閉環】
                                                  │
                                                  ├─ [測試綠燈] ──▶ 執行期硬門禁驗收 ──▶ [ai-quality-gates + harness-guard]
                                                  └─ [遇錯卡關] ──▶ 提煉報錯升級回流 ──▶ [agent-advisor: pro-reviewer]
```

---

## 2. 對現有工作流與專案之啟發

1. **與本地全域規範（`RULE[user_global]`）的本質統一**：
   - 本地全域規範中的「不要在專案目錄外讀寫或刪改」、「回報完成前要真的執行過檢查並貼出輸出」、「被糾正後把教訓寫進檔案」，這三條硬規則本質上就是「AI 共同大腦」打卡與審計機制的靈魂！
2. **與現有技能庫的全面串聯**：
   - `dropoff` / `pickup`：構成了交接單的標準讀寫原語；
   - `orchestration` / `token-optimizer`：構成了複雜度與額度感知調度的核心邏輯；
   - `verification-protocol` / `quality-loop`：構成了簽入打卡前的確定性門禁。
3. **進一步落地為可執行的工程協議**：
   - 將散落在對話中的「打卡拿資料」、「Obsidian 交接單」與「額度監控」沉澱為專門的 CLI 工具與通訊腳本，使不同終端中的 Agent 能自發遵守共同大腦的協調規則。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261019-07`**｜**[優先級：高]** 設計「AI 共同大腦集中知識庫打卡與簽出審計協議（Shared Brain Check-in & Audit Protocol）」，定義 Agent 讀取與修改共用專案/技能時的日誌契約與防衝突鎖
  - **目標範圍**：`SanHsien/claude-code-projects-workflow` ＋ `SanHsien/codebase-memory-mcp` ＋ `SanHsien/harness-guard` ＋ `SanHsien/agent-environment-audits`（私有）
  - **驗收標準（DoD）**：派工前做 Worktree 範圍檢查與合併衝突預測，檔案讀寫有打卡紀錄，實測兩個 Agent 同改一檔會被擋下
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：[SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) `locks.py`（`931e35e`→`2ded579`，SPEC 第 9 節）：store 內 `claims/`（簽出鎖，經 git 跨機器共用，本機 O_EXCL）與 `audit/`（checkout／checkin／blocked 每事件一檔）；範圍重疊沿用 claude-code-projects-workflow 的 `may_overlap`。派工信 `dispatch.paths` 先簽出、重疊即 refused；施工後範圍外變更不 commit、回信附合併衝突預測。`SanHsien/harness-guard` 新增 `checkout-guard`（`4ccde8e`、`5970e74`）：互動 session 改別人簽出的檔即擋下，判斷記入 touch-log。agent-relay 133 項、checkout-guard 15 項測試通過，兩輪獨立審查判定 ship。實測（`docs/evidence/2026-10-20-t07-checkout.md`）：兩封派工同時改 `calc.py`，A 完成（`8463cbe`）、B 回信「relay:…448db8 持有 calc.py」被擋；掛 checkout-guard 的 Claude session 改被簽出的 calc.py 被擋、簽入後放行。限制：codebase-memory-mcp 與 `SanHsien/agent-environment-audits`（私有） 未接入；跨機器同一輪同時簽出靠衝突預測發現；同機兩個互動 session 身分相同不互擋。
- [x] **`T-20261019-08`**｜**[優先級：中]** 實作「跨 Agent 結構化記憶檢索與交接單自動同步工具原型（Shared Brain Memory Sync）」，打通本地 Obsidian 知識庫與各 Coding Agent（Claude/Codex/AGY）之 Session 上下文
  - **目標範圍**：`SanHsien/claude-obsidian` ＋ `SanHsien/cc-session-reader` ＋ `SanHsien/personal-ai-os`（私有）
  - **驗收標準（DoD）**：新開 Session 自動注入 Obsidian 交接單與精簡上下文，實測一次接手不需人工貼上下文
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：[SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) `relay context`（`352edb7`→`0468bca`，SPEC 第 8 節）：把 HANDOFF.md、claude-obsidian vault 的 `handoffs/<repo>.md`、待接手交接卡、cc-session-reader 讀出的上一個 session、git 狀態整理成有時間與字數上限、遮罩過、以 nonce 區塊標示為資料的交接包；經 `relay dispatch` 工人 prompt 與 Claude Code SessionStart hook（`hooks/session_start.py`）自動注入。88 項單元測試通過，兩輪獨立審查判定 ship。實測（`docs/evidence/2026-10-20-t08-handover.md`）：三個來源各放一個只有它知道的事實，派工信只寫「依接手資料完成下一步。」，工人寫出 `power()`、負指數 `raise ValueError`、`test_power`／`test_power_negative`，relay commit `afe08cd`、unittest OK；掛 hook 的新 session 不讀檔即答對三項，不掛 hook 的對照組回答「沒有接手資料」。限制：Codex／agy 無 SessionStart hook，只經派工注入；`SanHsien/personal-ai-os`（私有） 的接手資料模板已寫好，待該 repo 無關的 codeql-action 版本檢查處理後提交。

---

## 4. 關聯筆記、會話溯源與相關任務（Related Notes & Sessions）

- **歷史會話溯源與推進脈絡**：
  - 前序創世 Session（內部紀錄，未公開） ｜ 2026-10-18 最初確立跨 Agent SSOT 中立資產層、Antigravity/Claude/Codex/Cursor 共用 Skills 與 KB 之奠基對話
  - 本規劃落地 Session（內部紀錄，未公開） ｜ 2026-10-19 深入調研多 Agent 自動互傳、開新 Session 派工與驗收閉環流水線，完成 10 大既有倉庫盤點對照
- **通訊傳輸與終端復用**：
  - [Crossroad A2A 跨機器寄信協議](./2026-10-19-crossroad-a2a-agent-mail-relay.md) ｜ 關聯任務：`T-20261019-01`、`T-20261019-02`
  - [多 Agent 工廠：Magpie 網關與 Herdr 終端復用](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261018-16`
- **跨 CLI 調度與模型分工**：
  - [跨 CLI 子代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`
- **工程驗證與記憶中樞**：
  - [SpaceX 首席工程師 pstack 方法論](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-17`、`T-20261018-18`
  - [Claude-Mem 跨 Session 記憶中樞與 Autocompact](./2026-10-17-claude-mem-autocompact-context.md) ｜ 關聯任務：`T-20261017-25`、`T-20261017-26`
  - [XERJ Corpus Hub 領域語料庫釘選](./2026-10-17-xerj-corpus-hub.md) ｜ 關聯任務：`T-20261017-01`、`T-20261017-02`
