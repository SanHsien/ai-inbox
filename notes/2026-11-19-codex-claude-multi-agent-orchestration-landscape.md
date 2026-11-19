---
id: "2026-11-19-codex-claude-multi-agent-orchestration-landscape"
title: "Codex 中文社群討論與 25 則留言全景：Claude Code + Codex CLI 自動協作、額度接續與工具生態矩陣"
source_url: "https://www.facebook.com/groups/1713764039757273/permalink/1889438188856523/"
source_platform: "Facebook (Codex 中文社群)"
author: "Nicky Lui（含 25 則社群實戰回覆）"
github_repo: "https://github.com/bruce601080102/ccc-mcp"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 1
source_replies: 25
source_reviewed_at: "2026-11-19"
status: done
cluster: 1
cluster_role: "雙CLI協作生態全景"
short_title: "Claude+Codex協作全景"
tags:
  - claude-code
  - codex-cli
  - multi-agent
  - ccc-mcp
  - herdr
  - orca
  - facebook
---

# Codex 中文社群討論與 25 則留言全景：Claude Code + Codex CLI 自動協作、額度接續與工具生態矩陣

- **來源貼文**：[Facebook Codex 中文社群貼文（Nicky Lui）](https://www.facebook.com/groups/1713764039757273/permalink/1889438188856523/)（原分享連結 `https://www.facebook.com/share/p/1UQiQzpdzv/`）
- **發布平台 / 作者**：`Facebook (Codex 中文社群)` / `Nicky Lui`（並彙整 25 則留言與實拍圖）
- **分析日期**：`2026-11-19`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（Herdr 多代理終端復用）
  - [`notes/2026-11-15-openai-codex-plugin-cc-collaboration.md`](./2026-11-15-openai-codex-plugin-cc-collaboration.md)（OpenAI 官方 `codex-plugin-cc`）
  - [`notes/2026-11-15-pi-hybrid-harness-codex-claude-antigravity.md`](./2026-11-15-pi-hybrid-harness-codex-claude-antigravity.md)（Pi Harness 混合架構）

---

## 1. 原始資料盤點（主文、1 張留言實拍圖與全部 25 則留言）

- **主貼文提問（Nicky Lui）**：詢問如何將 `Claude Code`（規劃／審查大腦）與 `Codex CLI`（編寫／測試執行代理）串聯成免手動切換的自動閉環，包含失敗自動修正、額度不足切換模型，以及能否直接使用各自每月 US$200 官方訂閱額度免付 API Token 費。
- **留言區彙整（共 25/25 則完整讀取）與留言附圖（1 張）**：

| 路線 / 工具 | 來源留言 | 核心機制與實戰回饋（含反駁／限制） |
| :--- | :--- | :--- |
| **原生 CLI 腳本＋工作單** | #16 Frank Liao、#22 / #25 方士軒 | **訂閱帳密認證確可走訂閱額度（非 API 費），但自動化狂跑極易撞限額**。無需上 `n8n` 重框架，用 `claude -p` 與 `codex exec` 配輕量 Python/Shell 協調，工作單寫死**允許路徑、測試方式、通過條件、重試上限**；Claude 只讀審查，修正交回原執行代理防同時改檔衝突。 |
| **`codex-plugin-cc` 等橋接外掛** | #2 TruthfulMoose5123、#21 Kwok Ming Clement Wong | 官方外掛 [`openai/codex-plugin-cc`](https://github.com/openai/codex-plugin-cc) 可從 Claude Code 呼叫 Codex；但 #21 實測認為若一開始架構與規格沒寫好，單純雙模型修補意義有限。 |
| **`bruce601080102/ccc-mcp`** | #20 Haha Jao | 開源 MCP 編排器（`pip install ccc-mcp`），主打「不輕信 AI 口頭說 tests passed」：**本機測試 + Git Diff 計算證據覆蓋率評分**、需求/決策/變更**版本化共用上下文**、19 角色/7 工作流、**額度不足自動切換接續**與 Web UI。 |
| **`Herdr`** | #3 王建智、#7 周建廷、#10 Orange Lei、#12、#23 | 同專案開多 agent 並用 `herdr wait` 等派工回傳，搭配 `herdr-web` 手機遠端控盤免持續 SSH。 |
| **`Orca`（＋附圖 1 張）** | #3、#8 刘家权、#19 Ho Lau Ho | **附圖 1 實拍**：MacBook 雙欄同時跑 Claude 主協調（`/goal`、合併多個 worktree 分支、等待 worker 訊息）＋ OpenCode Go / DeepSeek V4.1 Flash worker 跑 `vitest` 與驗證；左下角監控各家額度百分比。**但 #19 實測吐槽：rate limit 到頭自動 reuse 仍卡頓，常需開新 session 重做**。 |
| **其他桌面／流程方案** | #6 戴元衍、#13 黃祈豫、#15 張峻瑜、#17 YuHao Chen、#24 Bencent Huang | `Pyloxa`（`pyloxa.com`，Windows 版 Claude+Codex worktree 協調與 quota fallback）、`Avengents`（`avengents.ai`）、`Codex Dev Team`（`blog.sd0x.dev/blog/codex-dev-team/`）、`Paperclip` + `OpenBot` + GitHub Issue 派工。 |

- **原始資料對分析的影響**：主貼文只是新手架構提問；25 則留言與 Orca 實拍圖直接揭示了實際落地時的兩大致命現實——(1) 訂閱制雖然免 API 費但自動化會極速撞限額，且現成工具的自動額度 reuse 在實戰中依然容易卡頓；(2) `ccc-mcp` 與方士軒的「工作單寫死路徑＋本機實測證據評分」與本機自建的 `agent-relay`、`claim_evidence_guard` 高度同源。

---

## 2. 對現有系統的啟發與落差評估

- **已驗證本機現有架構走在正確路線**：
  - 本機 `agent-relay` + `claude -p` / `codex exec` + `claim_evidence_guard` + `quality_gate.py` + 全局「派工要掌控到完成」規則，正正符合留言 #22/#25 與 #21 的實務共識（重規格與證據閘門、不迷信重框架）。
- **值得進一步唯讀對照的新專案**：
  - **`bruce601080102/ccc-mcp`** 主打的「**版本化共用上下文防覆蓋**」、「**Host-run tests + Git Diff 計算證據覆蓋率評分**」與「**任務狀態保存後跨 Agent（Claude → Codex）無縫接續**」，非常值得與本機 `agent-relay` / `agent-advisor` 做一次只讀架構比對，看看有哪些設計可直接借鏡吸收（**不直接 pip 安裝到主環境**）。
- **查證註記（2026-11-19，T-20261119-02 唯讀檢閱）**：
  - `ccc-mcp`（commit `782c75ad`）的三項主打功能在原始碼都找得到對應實作；其中「證據覆蓋率」的需求覆蓋那一項是關鍵字重疊，容易灌水。
  - 額度不足改派與限流誤判防護，本機 `agent-relay` 已較完整；可借鏡的是「零測試不算綠燈」與「驗證紀錄分等級」，詳見 [`docs/ccc-mcp-architecture-review.md`](../docs/ccc-mcp-architecture-review.md)。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261119-02`**｜**[優先級：低]** 唯讀檢閱 `bruce601080102/ccc-mcp` 與本機 `agent-relay`／`claim_evidence_guard` 進行架構對照
  - **目標範圍**：`C:\GitHub\_sandbox\ccc-mcp-audit` 與 `C:\GitHub\ai-inbox\docs\ccc-mcp-architecture-review.md`
  - **執行步驟**：
    1. 僅唯讀 clone `bruce601080102/ccc-mcp` 至沙盒目錄（不執行 `pip install` 或啟動 MCP server）。
    2. 檢視其實作「版本化共用上下文防覆蓋」、「本機測試 + Git Diff 證據覆蓋率評分」與「跨 Agent 額度 fallback 任務狀態恢復」的核心程式碼與資料結構。
    3. 對照本機 `agent-relay` 與 `claim_evidence_guard`，整理可借鏡或本機已更完善的項目至 `docs/ccc-mcp-architecture-review.md`。
  - **驗收標準（DoD）**：產出 `docs/ccc-mcp-architecture-review.md` 記錄核心模組原始碼對照與可借鏡點（或明確不採納理由），且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-19
  - **實作紀錄 / 證據**：docs/ccc-mcp-architecture-review.md；唯讀檢閱 commit 782c75ad，三主題附原始碼行號並與 agent-relay 0cabfe33、harness-guard ec38c1d 逐項對照；結論不整套採用，列 2 項可借鏡與 4 項不採納理由
