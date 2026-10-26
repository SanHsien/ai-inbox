---
id: 2026-10-18-multi-agent-factory-magpie-herdr-routing
title: "多 Agent 生產力工廠實戰架構：Magpie 統一網關、Herdr 終端復用、Obsidian 接棒交接與額度感知動態路由解構"
source_url: "https://github.com/yetone/magpie"
source_platform: "Threads / GitHub"
author: "Threads 社群實戰者 / yetone & herdrdev"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: in-progress # pending | in-progress | done | archived
cluster: 1
cluster_role: "終端派工"
short_title: "Herdr 終端復用 + Magpie 統一網關"
tags:
  - multi-agent-factory
  - magpie
  - herdr
  - model-routing
  - quota-watcher
  - agent-handoff
---

# 多 Agent 生產力工廠實戰架構：Magpie 統一網關、Herdr 終端復用、Obsidian 接棒交接與額度感知動態路由解構

- **來源連結**：[yetone/magpie (GitHub)](https://github.com/yetone/magpie) ｜ [herdrdev/herdr (GitHub)](https://github.com/herdrdev/herdr) ｜ [OrcaRouter](https://github.com/orcarouter)
- **發布平台 / 作者**：`Threads 對話節錄` / `yetone & herdrdev 社群實戰者`
- **分析日期**：`2026-10-18`
- **當前狀態**：`🟡 進行中 (In Progress)`

---

## 1. 核心內容摘要

### 1.1 核心主張：從「單兵 Agent」進化為「工業級多代理協同工廠」

過去開發者使用 AI Coding Agent（如 Claude Code, Codex, OpenCode, Antigravity）往往採用單兵作戰模式，面臨四大痛點：
1. **設定與訂閱破碎**：每個 CLI 各自為政，各有各的 config 格式、API Key 與 Base URL，切換模型極度痛苦。
2. **多終端監控盲區**：同時開 5~10 個 Agent 平行跑任務時，一般 `tmux` 或終端標籤無法感知 Agent 的執行生命週期（誰在施工、誰卡在等確認、誰已經跑完）。
3. **知識漂移與修改衝突**：多個 Agent 隨意改動專案程式碼與技能庫，缺乏簽入/簽出（打卡）與接力交接制度。
4. **Token 焦慮與額度踩雷**：沒有全局額度感知，把簡單批次丟給貴模型（Opus）燒乾配額，或在大任務中途觸發 Rate Limit 導致整個任務爛尾。

本則 Threads 節錄精準揭示了目前一線資深實戰者運作的**「多 Agent 生產力工廠（Multi-Agent Factory）四大支柱」**，並點名整合了 **Magpie**、**Herdr**、**ORCA** 與 **LibreChat** 等核心神器：

```
┌────────────────────────────────────────────────────────────────────────┐
│                   多 Agent 生產力工廠實戰協同架構 (Factory Matrix)        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 集中資料中心與打卡機制 (Central Knowledge Hub & Check-in Audit)      │
│    └─ 雲端集中管理專案與 Skills，Agent 讀取與修改強制記錄 Log，避免漂移  │
│                                                                        │
│ 2. Obsidian 結構化接棒交接單 (Handoff Boards & Shift Logs)              │
│    └─ 以 Markdown + Frontmatter 記錄前車之鑑與任務狀態，實現無縫接力交接   │
│                                                                        │
│ 3. Herdr Agent-Native 終端復用器 (Multiplexer & PTY Supervisor)         │
│    └─ 即時感知各 Pane 狀態 (Working / Idle / Done / Blocked)，支援互派任務 │
│                                                                        │
│ 4. Magpie 統一本地網關與配額容錯 (Unified Gateway & Failover)            │
│    └─ 統一 API 轉發、跨模型混搭 (Codex 跑 DeepSeek)、RateLimit 自動轉移  │
│                                                                        │
│ 5. 複雜度與額度感知前置分派 Hook (Complexity- & Quota-Aware Routing)   │
│    └─ 指揮官分派前：先查各家額度與重置倒數 ──> 評估工單規模 ──> 推薦施工模型 │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 關鍵開源工具矩陣深度剖析

```
[多 Agent 協同工廠工具分工]

                ┌───────────────────────────────────────┐
                │          指揮官 Agent / 派工 Hook      │
                │ (評估工單複雜度 / 查詢各家額度與重置倒數) │
                └───────────────────┬───────────────────┘
                                    │ 動態派工
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
┌──────────────────┐                               ┌──────────────────┐
│  Herdr (Rust)    │ (狀態感知終端復用)              │  Magpie (Go)     │ (統一 API 網關)
│ ├─ Tab 1: Opus   │ [Working / 規劃審查]            │ ├─ 轉發 API Key  │
│ ├─ Tab 2: Codex  │ [Working / 本地實作]            │ ├─ 跨模型混搭    │ (Codex 跑 DeepSeek)
│ └─ Tab 3: Grok   │ [Done / 測試驗證]               │ └─ 自動容錯切換  │ (RateLimit Failover)
└─────────┬────────┘                               └─────────┬────────┘
          │                                                   │
          ▼                                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 集中資料中心 (Google Drive / Git) ＋ Obsidian 交接單 (Handoff Cards) │
└─────────────────────────────────────────────────────────────────────┘
```

1. **`yetone/magpie` (Go 打造的統一 Coding Agent 本地網關)**：
   - 官方站點：`usemagpie.ai`。
   - **痛點解決**：各家 Coding Agent（Claude Code, Codex, Aider, OpenCode）原本各自綁定特定設定。Magpie 在本地提供統一的 OpenAI/Anthropic 相容 Gateway。
   - **混搭突破**：支援將 **Codex 指向 DeepSeek-V3/R1**、或將 **Claude Code 指向 Kimi / GLM**，大幅降低日常施工成本。
   - **自動容錯（Failover）**：內建 Quota 監控，當某家模型遇到 429 Rate Limit 或額度耗盡時，自動秒級容錯切換至備援 Key 或模型。
2. **`herdrdev/herdr` (Rust 打造的 Agent-Native 終端復用器)**：
   - 官方站點：`herdr.dev`。
   - **非傳統 tmux**：傳統 tmux 只能分屏文字；Herdr 原生解析 PTY 的輸出狀態，直接在 UI/Statusline 標示各 Agent 是處於「Thinking/Working」、「Waiting User Input」、「Completed」還是「Errored」。
   - **Agent 互派工（Agent-to-Agent Socket API）**：Agent 可以透過 Herdr 提供的 Socket API 主動在相鄰 Pane 召喚另一個 Agent 執行子任務，並監聽其完成訊號。
3. **`ORCA` / `OrcaRouter` (智慧動態模型路由與多 Agent 開發環境)**：
   - **OrcaRouter**：動態分析 Prompt 語意複雜度，自動選擇性價比最高之模型（大腦 vs. 施工）。
   - **Orca ADE**：利用 Git Worktrees 為平行執行的多個 Coding Agent 提供完全隔離的工作目錄，避免代碼覆寫衝突。
4. **`LibreChat`**：
   - 作為人工介入、視覺化 Prompt 測試、知識庫調用與各模型對話的統一多模型 UI 前端。

---

## 2. 對現有系統的啟發與落差分析

### 2.1 對應現有系統與專案

| 現有專案 / 規範 / 技能 | 關聯性與啟發重點 |
| :--- | :--- |
| **`token-optimizer` / `orchestration`** | 現有的 `token-optimizer` 與 `orchestration` 著重於「規則面」的模型路由（Default Solo vs. Targeted Delegation）。對話中的做法更進一步升級為**「工程面自動化」**：在分派任務前透過 Hook 自動檢查各模型額度與工單複雜度。 |
| **`agent-handoff` / `dropoff` / `pickup`** | 現有的交接技能使用 Markdown 卡片，對話中的實踐將 Obsidian 作為共享看板，透過 WikiLink 與狀態標籤使交接與 log 更具視覺化與持久性。 |
| **`cross-cli-subagent`** (Note 14) | Note 14 探討過「Opus 規劃顧問 ＋ 外包 OpenCode / AGY / Space Bunny」；Magpie 與 Herdr 提供了底層基礎設施（網關與多終端狀態看板），能完美落地該編排流程。 |
| **`RULE[user_global]`** | 「回報前要真執行過」、「工具靜靜失效比大聲報錯危險得多」。Herdr 的狀態感知與 Magpie 的 Failover 機制，徹底避免了「某個背景 Agent 卡住或死掉卻無人知曉」的致命盲區。 |

### 2.2 落差與採納判斷

- **值得採納的部分**：
  1. **導入 Magpie 解決多 CLI 的模型配置與 Rate Limit 容錯**：評估在 Windows 11 本地以 Magpie 作為統一 Local Gateway，方便 Claude Code / Codex / OpenCode 無痛共用模型與代理。
  2. **實作「複雜度與配額感知前置分派 Hook（Pre-Dispatch Hook）」**：撰寫腳本在任務開工前，自動評估工單規模並檢查額度，直接輸出推薦模型與分派命令。
  3. **規範化集中技能庫的「打卡簽出/簽入日誌」**：在共享 Skills 或共同維護文件夾時，規範 Agent 異動時自動追加 ChangeLog。
- **不適用 / 需調整的部分**：
  1. **避免過度依賴雲端 Google Drive 同步**：跨 Agent 代碼寫入若放在雲端同步資料夾易產生檔案鎖定（File Lock）與同步延遲衝突，代碼與 Git 專案仍應維持本地原生目錄（`C:\GitHub\<repo>`），雲端資料中心僅適合存放唯讀知識庫與共用 Prompt。

### 2.3 實務心得增補：Grok Bot + Herdr + Coding CLI 前哨派工與 AGENTS.md 規範驅動起步

- **Grok Bot 派工前哨站**：
  在 Grok 環境中安裝 Herdr 終端復用器與各 Coding CLI，將 Grok 作為高階任務理解與派工指揮官。Grok 負責拆解需求，再透過 Herdr 自動呼叫適配的 Coding CLI（Claude Code / Codex / Antigravity）在各專案目錄執行具體工程代碼。
- **統一進入點與 `AGENTS.md` 規範驅動（AGENTS.md-driven Bootstrap）**：
  在多 Bot / 多 CLI 協作時，最忌諱每換一個 Agent 就重新灌一次背景。實戰的最佳解是：**「統一所有 Grok Bot 對專案工作目錄（Workspace Entrypoint）的感知，專案的起步與施工規範全部交給各專案根目錄的 `AGENTS.md` 控制」**。任何 Coding Agent 被叫起時，第一步強制讀取當前專案的 `AGENTS.md`，自動獲取禁區、架構契約、依賴路徑與驗收標準（DoD），實現「零重複交待、即起即幹」的標準化派工閉環。

---

## 3. 拆解待辦事項（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261026-28`**｜**[優先級：中]** 撰寫「Grok Bot + Herdr 統一工作目錄進入點與 AGENTS.md 起步驅動規範」收錄於 `docs/grok-herdr-agents-bootstrap.md`
  - **狀態**：🟡 進行中
  - **目標範圍**：`docs/grok-herdr-agents-bootstrap.md`
  - **具體做法**：
    1. 定義 Grok Bot 環境整合 Herdr 與 Coding CLI 的派工拓撲。
    2. 規範專案根目錄進入點標準，制定 Coding CLI 啟動時自動掛載 `AGENTS.md` 的前置起步協議。
    3. 實作進入點驗證腳本或檢查清單，確保任何 Agent 被啟動時均能自動解析當前專案之 SSOT 規範。
  - **驗收標準（DoD）**：產出 `docs/grok-herdr-agents-bootstrap.md`，內含派工架構圖、AGENTS.md 起步協議與驗證範例；以 `Test-Path docs/grok-herdr-agents-bootstrap.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
- [x] **`T-20261018-15`**｜**[優先級：高]** 調研並測試 `yetone/magpie`（統一 Agent 網關）與 `herdrdev/herdr`（Agent-Native 終端復用器）在 Windows 11 下的整合
  - **目標範圍**：`SanHsien/agent-cortex` ＋ `SanHsien/opencodex` ＋ `SanHsien/claude-code-projects-workflow`（**現有可用 Repo**：直接復用 `agent-cortex` 原生 Windows 控制平面、`opencodex` 通用代理網關，與 `claude-code-projects-workflow` Worktree 派工範圍檢查，免去 Linux 專用 tmux/Herdr 摩擦）
  - **具體做法**：
    1. 調研 `yetone/magpie`（Go）與 `herdrdev/herdr`（Rust），在 Windows 11 本地測試其安裝與運作機制。
    2. 驗證 Magpie 統一轉發 Claude Code / Codex API 與 Failover 容錯轉移；對照評估 `SanHsien/agent-cortex` 原生 Windows 控制平面的 Worktree/分支隔離與 Session 派工能力，以及 `SanHsien/opencodex` 作為本機代理中樞之表現。
    3. 評估與現有 `SanHsien/agent-advisor` 與 Antigravity CLI 的相容性，產出工具鏈整合指南。
  - **驗收標準（DoD）**：在 Windows 11 輸出 CLI 狀態與代理轉發測試記錄，整理相容性報告。
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：相容性報告 [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) `docs/reports/2026-10-20-windows-session-control.md`（`8d489b0`、`9a6ebed`）：herdr 0.9.1 Windows 原生 server／pane run／pane read 實測通過；magpie v0.1.1294 Windows binary `version`／`--help` 通過（SHA256 與官方一致，gateway 未啟用）；opencodex 2.88.0 `/healthz`、`/v1/models` 200，真實轉發一次 8 token 請求 HTTP 200、上游回 `relay-ok`；agent-cortex 0.1.8 CLI 可跑但 `doctor` 3 項 FAIL（環境變數／服務路徑未設）；worktree_tasks.py 各子指令 help 通過。結論：開新 Session 改用 agent-relay `dispatch`（Windows Terminal 新分頁＋git worktree，指令沿用 agent-cortex launcher，`3da4baf`→`8c9a532`，64 項單元測試，經三輪獨立審查判定 ship）；代理網關用 opencodex，magpie 當備案。實測紀錄 `docs/evidence/2026-10-20-phase2.md`：task 信 → 收件端開 WT 分頁、worktree 內 claude（haiku，`acceptEdits`）施工 → relay 代 commit → 自動回信 → 指揮者常駐排程收信。

- [x] **`T-20261018-16`**｜**[優先級：中]** 實作「複雜度與配額感知任務分派 Hook 原型（Complexity- & Quota-Aware Dispatch Hook）」
  - **目標範圍**：`SanHsien/codex-reset-checker` ＋ `SanHsien/codex-auto-retry` ＋ `SanHsien/Antigravity-Manager` ＋ `SanHsien/agent-advisor`（**現有可用 Repo**：整合額度查詢、斷線限流原地續跑、帳號切換與 5 大 Runtime 路由）
  - **具體做法**：
    1. 實作輕量化前置檢查腳本 `tools/dispatch_advisor.py`，串接 `SanHsien/codex-reset-checker` 讀取各模型當前額度狀態與重置週期，結合工單規模（檔案數、預估 Token、演算法複雜度）。
    2. 結合 `SanHsien/codex-auto-retry` 守護行程，當遇限流或逾時中斷時原地自動續跑；結合 `Antigravity-Manager` 進行無縫多帳號輪轉。
    3. 自動輸出最佳模型路由建議（例如：高難度選 Opus、機械批次外包 DeepSeek/Flash），並產生標準 Obsidian / Markdown 交接單模板。
  - **驗收標準（DoD）**：執行腳本能根據不同工單情境給出正確的路由決策與交接單結構，並通過 `python tools/verify_inbox.py` 與單元測試。
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：做在 [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay)（不是本 repo 的 `tools/dispatch_advisor.py`）：`agent_relay/advisor.py`＋`relay advise`／`--card`，派工信 `--run auto`（SPEC 第 10 節，`7860df5`→`1bc117d`）。複雜度（詞邊界關鍵字、範圍、長度）× 本機額度（Claude 讀 agentdeck statusline 檔、Codex 跑 `codex-reset-checker --json`）→ runtime／模型／effort、備案或 deferred；失敗時斷線原地重跑、限流改派下一個 runtime（沿用 codex-auto-retry 的做法）；交接卡含 frontmatter 與派給誰／範圍／要做什麼／DoD／備案／額度。實測（`docs/evidence/2026-10-20-t16-advisor.md`）：真實額度 codex 5h 91% 被跳過，困難工單→claude/opus、註解工單→claude/haiku，`--run auto` 實際派工 log 為 `claude-haiku-5-5` 並 commit。單元測試 191 項通過（含 23 項路由情境與審查回歸），本 repo `verify_inbox.py` PASS；三輪獨立審查判定 ship。未涵蓋：Antigravity-Manager 帳號切換（帳號設定變更不自動做）、agy 額度無本機來源。

---

## 4. 關聯筆記、會話溯源與相關任務（Related Notes & Sessions）

- **歷史會話溯源與推進脈絡**：
  - 前序創世 Session（內部紀錄，未公開） ｜ 跨 Agent 中立資產與工廠化終端管理演進起點
  - 本規劃落地 Session（內部紀錄，未公開） ｜ 終端復用（Phase 2）與 Windows 原生控制平面（agent-cortex）對齊
- **共同大腦與架構整合**：
  - [AI 共同大腦工業級架構規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [Crossroad A2A 跨機器寄信協議](./2026-10-19-crossroad-a2a-agent-mail-relay.md) ｜ 關聯任務：`T-20261019-01`、`T-20261019-02`
- **跨 CLI 調度與模型分工**：
  - [跨 CLI 多代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`
  - [SpaceX 首席工程師 pstack 方法論](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-17`、`T-20261018-18`

