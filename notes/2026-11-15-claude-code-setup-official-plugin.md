---
id: "2026-11-15-claude-code-setup-official-plugin"
title: "Claude Taiwan 貼文評估：Anthropic 官方 `claude-code-setup` 專案自動化推薦外掛"
source_url: "https://www.facebook.com/groups/1224997379198346/permalink/1448040616894020/"
source_platform: "Facebook (Claude Taiwan) / GitHub"
author: "Richie Yang（社群分享）/ Anthropic 官方（Isabella He）"
github_repo: "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 3
cluster_role: "專案配置推薦外掛"
short_title: "claude-code-setup外掛"
source_reviewed_at: 2026-11-17
source_review: partial
source_review_note: "作者附圖 1 張已放大看過；未登入的 Facebook 頁面不顯示留言數也不顯示任何留言，無法確認有沒有留言（讀到 0 則，總數不明）"
source_images: 1
source_replies: 0
tags:
  - claude-code
  - claude-desktop
  - claude-plugins-official
  - automation-recommender
  - skills
  - hooks
---

# Claude Taiwan 貼文評估：Anthropic 官方 `claude-code-setup` 專案自動化推薦外掛

- **來源貼文**：[Facebook Claude Taiwan 貼文（Richie Yang）](https://www.facebook.com/groups/1224997379198346/permalink/1448040616894020/)（原分享連結 `https://www.facebook.com/share/p/1E93U2P4WW/`）
- **官方 GitHub**：[`anthropics/claude-plugins-official/plugins/claude-code-setup`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-code-setup)
- **發布平台 / 作者**：`Facebook (Claude Taiwan)` / `Richie Yang`；外掛原作者 `Isabella He (Anthropic)`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-plugins-official-directory.md`](./2026-10-17-claude-plugins-official-directory.md)（Anthropic 官方 Claude Code 插件生態目錄）
  - [`notes/2026-10-23-claude-plugin-security-guidance.md`](./2026-10-23-claude-plugin-security-guidance.md)（Anthropic 官方 `security-guidance` 安全外掛）

---

## 0. 原始資料盤點

> 2026-11-17 用未登入的瀏覽器重看 Facebook 原貼文。

- **作者圖片**：
  - 圖 1（唯一一張）：作者請 AI 整理的中文說明卡。上半是「推薦的五大類別」表：MCP Servers（例：Playwright、Context7）、Skills、Hooks（存檔自動排版、push 前型別檢查、阻擋修改敏感檔案）、Subagents（資安／效能／公司規範審查）、Slash Commands（`/test`、`/pr-review`、`/explain`）。下半是在 VS Code 終端機的兩行安裝指令，以及裝好後輸入 `recommend automations for this project`。圖上寫明「只分析、不改任何檔案」。
- **作者留言補充**：看不到（見下）。
- **網友留言重點**：未登入時頁面只顯示 188 個心情、97 次分享，沒有留言數也沒有留言內容；無法分辨是沒有留言還是要登入才看得到。
- **對分析的影響**：圖片內容與本篇第 1 節讀原始碼的結果一致（五類建議、唯讀、兩行安裝指令），沒有要更正的地方。貼文作者只是轉介並說「跑完覺得不錯」，沒有給出他專案的實際建議清單，所以沒有實測數據可引用。封存結論不變。

---

## 1. 核心內容與官方源碼盤點

本篇社群貼文介紹 Anthropic 官方釋出的 `claude-code-setup`（`v1.0.0`）外掛。實讀本機已同步之官方 marketplace 快取（`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/claude-code-setup`），其完整架構如下：

- **純唯讀 Markdown Skill 設計**：
  - 核心僅包含 `.claude-plugin/plugin.json`、`README.md` 與 `skills/claude-automation-recommender/SKILL.md`（外加 `references/` 下 5 份範本：`hooks-patterns.md`、`mcp-servers.md`、`plugins-reference.md`、`skills-reference.md`、`subagent-templates.md`）。
  - **無背景常駐程式、無 Command Hooks、無執行腳本**：安全審查風險極低，且不依賴特定 OS 的 Python/Bash hook 執行器。
- **掃描與推薦邏輯（Read-Only）**：
  - 觸發詞如 `"recommend automations for this project"`、`"help me set up Claude Code"`、`"what hooks should I use?"`。
  - 掃描目標 repo 的 `package.json`、`pyproject.toml`、`Cargo.toml`、`go.mod`、`pom.xml`、`.claude/`、`CLAUDE.md` 與目錄結構後，針對 **MCP Servers、Skills、Hooks、Subagents、Plugins（含 Slash Commands）** 五大類別各給出 Top 1–2 項建議（若指定單一類別則給出 3–5 項）。
- **官方安裝方式**：
  - CLI / VS Code 終端機：
    ```bash
    claude plugin marketplace add anthropics/claude-plugins-official
    claude plugin install claude-code-setup@claude-plugins-official
    ```
  - Claude Desktop：Plugins → Add plugin → 搜尋 `claude-code-setup` 安裝。

---

## 2. 對現有系統的啟發與落差評估

- **與現有本機基礎設施對比**：
  - 本機已具備完整的全域協作規範與自動化體系（`SanHsien/agent-assets` SSOT、`agent-advisor-claude`、全域 hooks 與 `ai-inbox` 工作流），核心 repo 無需再靠推薦器生成基礎設定。
  - 當時（`2026-10-17`）盤點 `docs/claude-plugins-official-review.md` 時尚未收錄此 plugin；現已在官方 `claude-plugins-official` marketplace 上架且同步至本機快取。
- **實際適用情境**：
  - **接手陌生或新建立的單一專案 repo 時**（例如快速盤點某個 React/FastAPI/Supabase 專案缺哪些專屬 `.claude/` hooks、Context7 / Playwright MCP 或 review subagent），可作為快速的「唯讀冷啟動體檢清單」。
- **資安與環境相容性**：
  - `SKILL.md` 明確限制僅做唯讀分析（`Read, Glob, Grep, Bash` 只讀探測），不會自動寫入或修改專案檔案；純 Markdown Skill 形式在 Windows 11 原生環境完全相容。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：`claude-code-setup` 已是官方 marketplace 內的現成純 Markdown Skill（本機快取已同步，無跨平台 hook 相容性風險、無需額外開發或封裝）。留存本筆記作為新專案冷啟動體檢工具參考即可；有需要時直接執行 `/plugin install claude-code-setup@claude-plugins-official` 啟用。
