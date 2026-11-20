---
id: "2026-11-20-antigravity-gemini4-neon-12-prompts-eval"
title: "Woshipm 長文評估：Gemini 4 Neon 實測基準、Antigravity 12 項配置與第三方插件零信任審查"
source_url: "https://www.woshipm.com/ai/6497136.html"
source_platform: "woshipm (人人都是產品經理)"
author: "饼干哥哥"
github_repo: "https://github.com/DeusData/codebase-memory-mcp"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 22
source_replies: 0
source_reviewed_at: "2026-11-20"
status: pending
cluster: 3
cluster_role: "AGY與Neon實戰配置"
short_title: "AGY十二配置與Neon"
tags:
  - antigravity
  - gemini-4-neon
  - gemini-4-hydrogen
  - codebase-memory-mcp
  - agy-fast-io
  - model-routing
---

# Woshipm 長文評估：Gemini 4 Neon 實測基準、Antigravity 12 項配置與第三方插件零信任審查

- **來源文章**：[美国大豆包翻身了！12个提示词用满血Antigravity吊打Claude（人人都是產品經理）](https://www.woshipm.com/ai/6497136.html)
- **文中相關開源專案（經外部搜尋核實）**：
  - [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp)（Tree-sitter AST + LSP 本地程式碼知識圖譜 MCP）
  - [`oil-oil/agy-fast-io`](https://github.com/oil-oil/agy-fast-io)（非官方 Antigravity 批量讀取規則插件）
- **發布平台 / 作者**：`woshipm` / `饼干哥哥`（`2026-11-20`）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-11-18-gemini-4-carbon-argon-swarm-evals.md`](./2026-11-18-gemini-4-carbon-argon-swarm-evals.md)（Gemini 4 Carbon / Argon 與 `/swarm`）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](./2026-11-20-gemini-decision-1-decisions-api-eval.md)（Gemini Decision 1 路由與校準）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型速查表）

---

## 1. 原始資料盤點（正文、22 張圖片與評論區）

- **Gemini 4 全系列與 Neon 官方數據（圖 2、圖 3、圖 4、圖 6、圖 18）**：
  - **四款分工**：`Carbon`（$4/$20，11/30 前 $2/$10，長週期研究）、**`Neon`（$3/$15，Pro/Ultra 可用，AA 61，軟體工程與長上下文主力）**、`Hydrogen`（$1.5/$7.5，極速日常執行）、`Argon`。
  - **Neon vs Opus 5.5 vs GPT-6.2 Sol（圖 3 DeepMind 基準）**：`GraphWalks 256k–1M` Neon 達 **95.2%**（vs Sol 80.1%、Opus 5.5 66.8%）、`CursorBench 4.1` 65.4%、`SWE-sweep` 39.0%、`SEC-bench Pro` 90.5%；`Terminal-bench 4.1`（65.2% vs Opus 5.5 65.8%）與 `FrontierCode 2.0`（46.2% vs Opus 5.5 47.3%）仍以 Opus 5.5 些微領先。
  - **成本與幻覺率**：`JAZII` 同題實測 Neon `$3.5` (20m) vs Opus 5.5 `$7.2` (18m)；`AA-Omniscience` 幻覺率 Carbon 4% / Hydrogen 8%（Sonnet 5.5 43%）。圖 18 顯示 `Carbon/Neon 規劃＋Hydrogen 執行` 較純高階模型省 24% 額度、提速 19%。
  - **風控警告（圖 13）**：作者轉貼警告指出 Google 嚴查跨區／薅羊毛帳號，主帳號封禁會波及 Gmail、Drive 與 GCP，**嚴禁使用主力帳號嘗試跨區或灰產套利**。
- **Antigravity 12 項配置提示詞盤點**：
  - 涵蓋：(1) 沙盒與工作區邊界、(2) 強制驗證禁絕對詞、(3) `verbosity: low`＋中文進度同步、(4) 安裝 `oil-oil/agy-fast-io` 批量快讀、(5) `/swarm` 派 Hydrogen、(6) `chrome-devtools-plugin`＋禁止高飽和前端色塊、(7) 清理多餘全域 skills、(8) 預設 `Orchestrator (Neon)` 防抽干 Claude 池、(9) `/grill-me`→`/plan`→`/goal`→`/learn`、(10) 遙測與 `AGY_CLI_HIDE_ACCOUNT_INFO=1`/`AGY_CLI_HIDE_LOGO=1` 隱藏隱私、(11) `codebase-memory-mcp` + Cloud Remote + Turbo、(12) `/remote-control` 手機監控。
- **評論區**：`0` 則留言。

---

## 2. 對現有系統的啟發與安全審查邊界

- **已在本機落地的條目**：第 1、2、5、6（前端規範與 `/browser`）、8、9 條均已由本機 `GEMINI.md` 全域協作規範與 `agent-assets` 覆蓋，無需重複照抄。
- **明確風險提醒（不可直接執行文章提示詞）**：
  - 文章第 4 條要求 AI 直接「安裝 `oil-oil/agy-fast-io` 並設為讀取免審白名單」、第 11 條要求直接切到 Turbo 並接入 `codebase-memory-mcp`。依全域規範硬閘門：**外部第三方 Skill／插件與 MCP 必須先經過沙盒唯讀檢視與 `verify_agent_skill_pack_safety.py` 安檢，不可直接開免審白名單**。
- **實用新技巧與可評估項**：
  - `AGY_CLI_HIDE_ACCOUNT_INFO=1` 與 `AGY_CLI_HIDE_LOGO=1`（圖 20）為實用的終端機截圖防漏個人信箱環境變數。
  - `Gemini 4 Neon` 與 `GPT-6.2 Sol` 基準數據適合補入模型路由矩陣；`DeusData/codebase-memory-mcp`（AST+LSP 圖譜減少大專案檢索 token）與 `oil-oil/agy-fast-io` 適合建立沙盒唯讀審查任務。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261120-03`**｜**[優先級：低]** 將 `Gemini 4 Neon` / `Hydrogen` / `GPT-6.2 Sol` 基準與雙模型接力數據補入 `docs/model-burn-rate-routing-matrix.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（可與 `T-20261118-01`、`T-20261120-02` 合併更新 Google 生態章節）
  - **執行步驟**：
    1. 整理 `Gemini 4 Neon`（`$3/$15`、`GraphWalks 95.2%`、`CursorBench 4.1 65.4%` vs `Opus 5.5` / `GPT-6.2 Sol`）與 `Hydrogen`（`$1.5/$7.5`）的定位與價格。
    2. 納入 Orchestrator（規劃腦＋Hydrogen 執行手省 24%／提速 19%）與「前端高飽和色塊／不主動測驗證」的規則約束提醒。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 收錄上述基準與定價對比（標明資料出處分級），且 `python tools/verify_inbox.py` 驗證通過。

- [ ] **`T-20261120-04`**｜**[優先級：低]** 沙盒唯讀安檢並評估 `DeusData/codebase-memory-mcp` 與 `oil-oil/agy-fast-io`
  - **目標範圍**：`C:\GitHub\_sandbox\agy-plugins-audit` 與 `C:\GitHub\ai-inbox\docs\agy-fast-io-and-codebase-memory-audit.md`
  - **執行步驟**：
    1. 僅唯讀 clone `DeusData/codebase-memory-mcp` 與 `oil-oil/agy-fast-io` 至沙盒目錄（嚴禁直接啟用免審白名單或執行安裝腳本）。
    2. 對 `oil-oil/agy-fast-io` 執行 `python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack <目錄>` 與人工規則審閱，檢視是否存在繞過沙盒或風險指令。
    3. 評估 `codebase-memory-mcp` 在 Windows 11 原生環境下的支援度與索引開銷，將審查與採納建議寫入 `docs/agy-fast-io-and-codebase-memory-audit.md`。
  - **驗收標準（DoD）**：產出 `docs/agy-fast-io-and-codebase-memory-audit.md`，明確記錄安全掃描結束碼、人工審閱結論與採納／拒絕決策，且 `python tools/verify_inbox.py` 驗證通過。
