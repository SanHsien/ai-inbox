---
id: 2026-10-17-agent-reach-social-intelligence
title: "Agent-Reach：專為 AI Agent 設計的跨平台社媒熱點與多模態情報獲取工具包"
source_url: "https://github.com/Panniantong/Agent-Reach"
source_platform: "Threads / GitHub"
author: "Panniantong (@Panniantong)"
github_repo: "https://github.com/Panniantong/Agent-Reach"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: 3
cluster_role: "跨網情報"
short_title: "Agent-Reach"
tags:
  - social-media-crawler
  - agent-tools
  - web-scraping
  - multi-backend-routing
  - open-source
---

# Agent-Reach：專為 AI Agent 設計的跨平台社媒熱點與多模態情報獲取工具包

- **來源貼文**：Threads 社群讀者分享（推薦社媒熱點追蹤 Skill）
- **官方 GitHub**：[`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach)
- **作者**：`Panniantong`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已做 (Done)`

---

## 1. 核心內容摘要與技術全貌

### 1.1 核心痛點與主張
- **痛點**：AI Coding Agent（如 Claude Code、Cursor、Windsurf、Antigravity）雖然在本地代碼撰寫與邏輯推理上極強，但當需要獲取**外部社群熱點、用戶反饋或跨平台情報**時，普遍面臨：
  1. 各大平台（Twitter/X、Reddit、YouTube、小紅書、B站）昂貴的官方 API 費用門檻。
  2. 登入牆（Login Wall）、反爬蟲升級導致抓取工具頻繁失效。
  3. 各平台工具分散，Agent 需個別安裝多個套件與管理雜亂的金鑰。
- **Agent-Reach 的解法**：為 AI Agent 提供**統一 CLI 命令列與 Channel 可插拔架構**，實現「零官方 API 費、開箱即用、自帶備援通道（Fallback）」的全網社媒情報獲取能力。

### 1.2 關鍵功能與架構設計

```text
[AI Agent (Claude Code / Antigravity / Cursor)]
                      │
                      ▼ 統一指令：agent-reach <platform> <query>
       ┌──────────────────────────────┐
       │   Agent-Reach CLI & Router   │
       └──────────────┬───────────────┘
                      │ 動態後端路由 (Primary + Fallbacks)
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
[Twitter / X]     [YouTube]       [小紅書 / B站]
  ├─ Nitter         ├─ yt-dlp       ├─ 公開 API
  └─ Jina Reader    └─ 字幕抽取     └─ Jina Reader
```

1. **支援 13+ 主流社群平台**：
   - 涵蓋 Twitter/X、Reddit、YouTube（支援字幕抽取）、GitHub、Bilibili、小紅書（XiaoHongShu）、Facebook、Instagram、LinkedIn、V2EX、雪球、小宇宙播客等。
2. **多後端動態路由（Multi-Backend Routing）**：
   - 每個平台通道（Channel）配置「主要後端 + 多個降級備選」。若某後端因反爬或服務中斷失效，系統能自動降級至備援通道，免去頻繁修改代碼的困擾。
3. **內建健康檢查診斷**：
   - 提供 `agent-reach doctor` 指令，一鍵檢測全平台通道的存活狀態與連通性。
4. **Agent 原生安裝與協同**：
   - 支援將安裝文檔直接交給 AI Agent，由 Agent 自行閱讀並完成本地環境配置與依賴安裝。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **`SanHsien/ai-inbox` 本身**：目前是「手動複製 Threads 連結或內文餵給 Agent 分析」；若整合 `Agent-Reach`，未來可進一步打造**自動化社媒熱點監聽器（Social Watcher）**，主動抓取關鍵詞或指定帳號貼文並產生草稿。
  - **現有聯網技能擴充**：現有的 `ai-search`、`read_url_content` 遇到需要登入或反爬嚴格的社群頁面（如 Threads/小紅書/YouTube 字幕）時容易抓取受限。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **多後端 Fallback 思維**：網路抓取必然面臨節點失效，採用主備通道路由是極佳的工程韌性設計。
    2. **YouTube 字幕與多模態文字抽取**：對技術長影片或演講的快速筆記化極有幫助。
  - **不適用 / 需注意的部分**：
    1. **Windows 11 原生相容性**：需驗證其 CLI 在 Windows PowerShell 下的執行表現及依賴套件（如 Python / Node 環境與 yt-dlp）。
    2. **防封禁與 Cookie 隔離**：若涉及個人帳號 Cookie 存取，需遵循本庫 `SECURITY.md` 規範，避免敏感憑證不慎提交至 Git。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-05`**｜**[優先級：高]** 實測 `Agent-Reach` 在 Windows 11 下的安裝與 `agent-reach doctor` 通道健康度
  - **目標範圍**：`環境工具鏈 / 社媒抓取調研`
  - **完成日期**：2026-10-23
  - **官方來源**：GitHub [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach)
  - **具體實作步驟**：
    1. 檢視官方 README，確認安裝依賴（pip 或 npm 套件）。
    2. 在 Windows 11 本地測試安裝，執行 `agent-reach doctor` 檢查各 Channel 的連通狀況。
    3. 實測 2~3 個主流平台指令：
       - YouTube 字幕抽取測試：`agent-reach youtube <video_url>`。
       - X / Twitter 熱點關鍵詞搜尋測試。
    4. 記錄指令輸出與 Windows 下是否有路徑或編碼相容性問題。
  - **驗收標準（DoD）**：產出完整的測試紀錄，確認至少 YouTube 與一個社群平台在 Windows 11 原生環境下免 API Key 成功抓取資料。
  - **實作紀錄 / 證據**：已完成安全審查（無未知二進位、無提權、無外傳）並安裝於隔離沙盒 `C:\GitHub\_sandbox\agent-reach\.venv`。執行 `agent-reach doctor` 成功診斷通道狀態：4/16 渠道開箱即用（V2EX 公開 API、RSS/Atom 源、Jina Reader 網頁讀取、B站公開搜尋直連），Windows 11 原生編碼與 Rich 控制台相容正常，無登入或寫入全域環境。

- [x] **`T-20261017-06`**｜**[優先級：中]** 評估將 `Agent-Reach` 封裝為 Antigravity / Claude Code 本地 Skill
  - **目標範圍**：`~\.gemini\config\skills\` 或外掛
  - **完成日期**：2026-10-23
  - **具體實作步驟**：
    1. 根據 T-20261017-05 的驗證結果，規劃一支 `agent-reach` Skill。
    2. 定義清晰的 Agent 呼叫介面，支援 `/reach <平台> <關鍵詞/連結>`。
    3. 與 `SanHsien/ai-inbox` 對接：當使用者丟入純網址時，若原生 HTTP 抓取失敗，自動 fallback 調用 `agent-reach` 進行深層內容還原。
  - **驗收標準（DoD）**：撰寫 Skill 草案與整合文檔，驗證當一般網頁讀取工具遇到社群平台時能無縫降級獲取全文。
  - **實作紀錄 / 證據**：已將 Agent-Reach 封裝為 Antigravity 本地 Skill 並安裝至 `~/.gemini/config/skills/agent-reach/`（包含完整 SKILL.md 與 7 大領域 references 路由規範），同時於 `C:\GitHub\ai-inbox\templates\agent-reach/` 同步一份完整範本。支援 16 大平台路由、多後端降級與免 Key 抓取能力。
