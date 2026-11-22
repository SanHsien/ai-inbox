---
id: 2026-10-17-claude-plugins-official-directory
title: "Anthropic 官方 Claude Code 插件生態目錄：解構標準化外掛、Skills 與 MCP 整合"
source_url: "https://www.threads.com/share/BAX6-awXHR/"
source_platform: "Threads / GitHub"
author: "Anthropic 官方 / 社群分享"
github_repo: "https://github.com/anthropics/claude-plugins-official"
official_registry: "claude-plugins-official"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: "3"
cluster_role: "外掛生態與設定治理"
short_title: "Claude Code 官方插件目錄"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 1
source_replies: 7
tags:
  - claude-code
  - agent-plugins
  - anthropic
  - mcp
  - developer-tools
---

# Anthropic 官方 Claude Code 插件生態目錄：解構標準化外掛、Skills 與 MCP 整合

- **來源貼文**：[Threads 分享連結](https://www.threads.com/share/BAX6-awXHR/)（登載於 `@easyanythinghk`） ｜ `2026-10-19` 社群後續追蹤（貼文原話是「累積 4 萬顆星、單日 +1,552」，附圖寫 40,886；不是幾天內衝到）
- **官方 GitHub**：[`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official)
- **分析日期**：`2026-10-17`（`2026-10-19` 補充最新社群追蹤）
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-16 重審：Threads 貼文（分享連結導向 `@easyanythinghk` 的貼文）文字、1 張圖、1 則留言都看過；另看了官方 repo 現行 README 與留言最多的 6 則 issue／PR。

- **作者圖片**：1 張自製資訊卡。標「GITHUB TRENDING・TOP 1・2026.10.17」，repo 名稱、一句英文定位、三個標籤：語言 Python、星數 **40,886（當日 +1,552）**、授權 Apache-2.0，底部列 MCP／Skills／Open Source／Claude Code。
- **作者留言補充**：1 則，貼 repo 連結並問讀者最缺什麼功能，沒有技術補充。
- **網友留言重點**：Threads 上沒有網友留言。GitHub issue 有三件事與本篇有關：
  - README 開頭已改版：第三方插件一律改到 claude.ai 的目錄後台送件，**這個 repo 的 PR 沒人看**，`marketplace.json` 之後只留 Anthropic 自己的插件。
  - README 的警語：Anthropic **不控制、也不驗證**插件裡的 MCP server、檔案或其他軟體，安裝前要自己確認可信。
  - #7024：約 2026-11-05 起，目錄只接受「已驗證組織」送出的 command hook 與本機 MCP server；#1272：有人的插件後台顯示已發布，卻沒出現在市集。
- **對分析的影響**：
  - 「上線幾天內突破 4.1 萬星」是錯的。貼文寫的是「累積 4 萬顆星、單日 +1,552」，圖上是 40,886；repo 建立於 2025-11-20，是累積將近一年的數字。1.1 節與來源行已改。
  - 「經官方審核、提供安全篩選」說過頭了，與 README 警語相反。1.1、1.2 節已改成「官方整理的目錄，不代表內容經過安全驗證」。
  - `T-20261017-08` 的個人插件走自己的 marketplace，不經官方目錄，不受送件規則影響；任務狀態未動。日後若要把個人插件送進官方目錄，含 command hook 的會被擋（#7024），這點記在第 2 節。

---

## 1. 核心內容摘要與專案全貌

### 1.1 核心主題與社群熱度
- **專案定位**：Anthropic 官方推出的 **Claude Code 插件市場官方目錄（Official Plugin Directory）**。
- **熱度數據**：2026-10-17 登上 GitHub Trending 第一名，當時累積約 **4.09 萬顆星**（單日 +1,552）。repo 建立於 2025-11-20，這是將近一年累積的數字，不是上線幾天衝出來的。
- **解決的痛點**：過去使用 Claude Code 時，開發者需要手動到處翻找隨機 GitHub repo、自行拼裝 MCP Server 配置、寫 Shell 腳本；該專案把 Anthropic 自家插件與早期收錄的第三方插件集中在一處、用統一格式打包，一行指令就能裝。注意 README 明寫 Anthropic 不控制也不驗證插件內容，「官方目錄」不等於「安全掛保證」。

### 1.2 2026-10-19 社群追蹤反響：從「野蠻生長」到「官方驗證」
社群開發者普遍共鳴在於**「認知負擔與資安風險的雙重下降」**：
1. **擺脫隨機 Repo 的資安隱患**：過去散落於個人倉庫的插件可能含有惡意腳本或供應鏈投毒風險；官方目錄集中了來源，比到處找 repo 好查證；但 README 警語說安裝前仍要自己確認可信，不能當成已做過安全篩選。
2. **安裝體驗極簡化**：透過一鍵指令（如 `/plugin install <plugin-name>@claude-plugins-official`）即可即裝即用，免去繁瑣的環境變數手動配置。
3. **任務對齊確認**：本項目的核心價值已完全收錄於既有任務 **`T-20261017-07`**（官方精選外掛清單檢閱）與 **`T-20261017-08`**（個人工具標準 Plugin 打包規範），無重複新增任務之必要，維持任務追蹤單一真實來源（Single Source of Truth）。

### 1.3 插件架構組成（Standard Plugin Package）

Claude Code Plugin 將一個完整能力封裝為獨立套件，通常包含：
1. **Skills（專業技能手冊）**：包含具體領域指引與 SOP 的 Markdown 定義。
2. **Slash Commands（斜線指令）**：如 `/review`、`/deploy` 等終端快捷命令。
3. **Sub-agents（子代理）**：負責特定長運行、需要獨立 Context 的專責代理人。
4. **Hooks & MCP Servers**：在特定事件觸發或連線外部 API 服務的標準連接器。

```text
[Claude Code CLI]
       │
       ▼ 一鍵安裝指令：/plugin install <plugin-name>@claude-plugins-official
┌────────────────────────────────────────────────────────┐
│ anthropics/claude-plugins-official                      │
│  ├─ Code Review 插件 (自動化靜態檢查與架構評審)          │
│  ├─ Frontend Design 插件 (UI 設計規範與組件指引)         │
│  ├─ Security Scanner 插件 (漏洞掃描與憑證偵測)           │
│  └─ Cloud / DevOps 插件 (GitHub / AWS / Azure 串接)    │
└────────────────────────────────────────────────────────┘
```

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **技能與外掛生態**：目前維護者在 Antigravity / Claude Code 專案中維護了多支 Skills（如 `agent-advisor`、`quality-loop`、`verification-protocol`）與 MCP Servers。
  - **外掛打包規範（Plugin Standard）**：Anthropic 官方規範為業界標準，其目錄結構、宣告格式（`plugin.json` 或 YAML）、依賴隔離對 `SanHsien/` 的 相關開源專案具高度借鑑價值。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **審閱官方精選插件庫**：挑選適合現有開發流程的官方插件（如自動化審查、資安掃描），避免重複造輪子。
    2. **外掛結構標準化**：未來若開發自製的跨 Agent 工具（如 `ai-inbox-helper` 或專屬 Skill），可比照官方 Plugin 規範打包，支援一鍵安裝。
  - **不適用 / 需注意的部分**：
    - 送件規則已變：第三方插件改到 claude.ai 目錄後台送件，repo 的 PR 沒人看；約 2026-11-05 起含 command hook 或本機 MCP server 的插件只收已驗證組織的（issue #7024）。個人插件維持走自己的 marketplace。
    - Windows 原生相容性：部分社群提交的 Plugin 可能預設假定 POSIX 環境（Linux/macOS），在 Windows 11 下需注意 Shell 路徑與行尾符號。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-07`**｜**[優先級：高]** 深度檢閱 `anthropics/claude-plugins-official` 精選外掛清單，篩選適合維護者工作流的插件
  - **完成日期**：2026-10-23
  - **目標範圍**：`開發工具鏈 / Claude Code Plugins 探索`
  - **官方來源**：GitHub [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official)
  - **具體實作步驟**：
    1. 查閱該倉庫目錄結構，整理出目前官方收錄的 Plugin 分類與列表（包含 code-review, security, git, testing 等）。
    2. 評估 2~3 個與維護者環境（Windows 11 + Git + 跨 Agent）高度相關的插件功能。
    3. 實測在 Claude Code 中安裝並測試其指令運作與 Windows 相容性。
  - **驗收標準（DoD）**：產出清單評估筆記，標明推薦啟用的官方外掛名稱與實測指令輸出。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `docs/claude-plugins-official-review.md`，直接 clone 並讀取 `anthropics/claude-plugins-official` 真實目錄與 `marketplace.json`，深度評比 8 款高度適配維護者 Windows 11+Python+TS 工作流之推薦插件、6 款不相容/偏離項目與排除原因，並對 3 款閉源 SaaS 標明「未查證」。 **2026-11-21 稽核後重做（2026-11-22 完成）**：原交付的指令段是「示意、未實測」，不符 DoD。改在隔離的 `CLAUDE_CONFIG_DIR` 暫存目錄（Claude Code 2.1.327、Windows 11）實際執行 `claude plugin marketplace add`、`install`（`security-guidance`、`skill-creator`、`pr-review-toolkit`）、`list`、`details`、`validate`，結束碼皆 0，輸出貼入文件第 5 節；本機設定檔 SHA-256 前後相同。實跑 `skill-creator` 的 `quick_validate.py` 發現 Windows 相容性問題：預設編碼 cp950 下 `UnicodeDecodeError`，加 `-X utf8` 才通過，且需要 PyYAML（非純標準函式庫）。未在互動 session 載入外掛，hook 與 agent 的實際執行未測；其餘 5 個推薦外掛未安裝實測。

- [x] **`T-20261017-08`**｜**[優先級：低]** 評估比照官方規格打包個人常用工具為標準 Plugin
  - **目標範圍**：`跨專案規範 / 自製 Plugin 打包`
  - **官方來源**：GitHub [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) 規範文檔
  - **具體實作步驟**：
    1. 研究官方 Plugin 的標準 Manifest 格式與宣告規範。
    2. 評估將核心工作流（如 `quality-loop` 或 `inbox-triage`）打包為相容格式的可行性。
    3. 產出打包規格筆記，供未來跨機器快速部署。
  - **驗收標準（DoD）**：完成打包規範驗證，確認可在終端中被正確識別載入。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：重評 2026-10-25：原以「不做」關閉但實質已完成——個人工具已依官方規格打包為標準 plugin agent-advisor-claude（1 skill + 3 subagent）與 myr2d2（14 skill），~/.claude/plugins/installed_plugins.json 列有 agent-advisor-claude@agent-advisor、myr2d2@myr2d2，Claude Code 2.1.309 session 內可正確載入其技能。
