---
id: "2026-11-15-pi-hybrid-harness-codex-claude-antigravity"
title: "Agent Harness 深度解析與 Pi 混合型架構設計：串接 Codex CLI、Claude Code 與 Antigravity"
source_url: "https://github.com/paul800901/K-harness"
source_platform: "GitHub"
author: "paul800901（參考目標 404）；核心基準：earendil-works/pi"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 1
cluster_role: "混合型Harness"
short_title: "Pi混合型Harness"
tags:
  - agent-harness
  - pi-coding-agent
  - codex-cli
  - claude-code
  - antigravity
  - orchestration
  - windows-native
---

# Agent Harness 深度解析與 Pi 混合型架構設計：串接 Codex CLI、Claude Code 與 Antigravity

- **來源連結**：[paul800901/K-harness（已失效 404）](https://github.com/paul800901/K-harness) ｜ [官方上游參考：earendil-works/pi](https://github.com/earendil-works/pi)
- **發布平台 / 作者**：`GitHub` / `earendil-works/pi`（原 `badlogic/pi-mono`，Mario Zechner，MIT License，121,989 stars）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

> **查證註記**：使用者提供的參考專案 `paul800901/K-harness` 經 GitHub API 與 HTTP 實查皆回傳 `404 Not Found`，且 `paul800901` 公開倉庫清單中亦無該專案（可能已轉私有或移除）。本分析以 `pi` 官方上游倉庫 `earendil-works/pi` 原始碼與文件（`providers.md`、`cli-integration.md`、`windows.md`、`security.md`、`custom-provider.md`）為事實基準。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：Mario Zechner（libGDX 作者）與 Earendil Works 團隊維護的開源專案 `earendil-works/pi`（MIT 授權）。
- **What（什麼是 Agent Harness，以及 Pi 是什麼）**：
  - **Agent Harness（代理外骨骼 / 執行底座）**：大語言模型（LLM）本身只具備「文字進、文字出」的推理能力；**Harness 是把模型包覆起來並接到真實環境的軟體外殼**，負責決定：
    1. **系統提示詞與上下文工程**：模型看得到什麼檔案、工具描述、壓縮（Compaction）與專案記憶。
    2. **工具層（Tools）與權限邊界**：誰能讀寫檔、跑 Shell、做審批攔截、或隔離到容器／Git Worktree。
    3. **代理迴圈（Agent Loop）與狀態機**：Tool call 循環、錯誤重試、Interrupt/Steering 中途插話、Tree-structured 會話分叉。
    4. **外部介面**：終端機 TUI、Headless Print/JSON 串流、長駐 RPC 子程序、或 TypeScript SDK。
  - **Pi 的核心定位（Primitives, Not Features）**：與 Claude Code / Codex CLI 這類高度封裝的重型 Harness 相反，Pi 故意只保留極簡核心（僅 `read`、`write`、`edit`、`bash` 4 個內建工具、低於 1,000 tokens 的系統提示詞，不硬編碼 Plan Mode、Sub-agents 與 MCP），把所有客製邏輯開放給 **TypeScript Extensions / Pi Packages** 組合。
- **Why（為什麼想用 Pi 做「三家混合型 Harness」）**：
  - 單一廠商 CLI 各自有強項與限制：Codex CLI 強在沙盒化大規模寫碼與 Plus/Pro 額度（如 GPT-6.1 Terra）；Claude Code 強在深度架構推理、Hooks 與 Plugin 生態；Antigravity 強在多模型切換、IDE/Browser 雙向整合與 Sidecar 視覺化。
  - 若直接使用各家封閉 Harness，會受限於各自的上下文注入黑箱與 UI 綁定；以 `pi` 為統一底座，理論上可把「互動控制權、樹狀會話與路由邏輯」收歸己有，再依任務特性呼叫三家核心。
- **How（`earendil-works/pi` 的實際架構與三家串接真相）**：
  - **官方內建 Provider 實況（已查證 `packages/ai/src/providers/`）**：
    - 內建 `openai-codex.ts`（ChatGPT OAuth Responses API）、`anthropic.ts`（API key / `ANTHROPIC_OAUTH_TOKEN` / `ANTHROPIC_AUTH_TOKEN`）、`google.ts` / `google-vertex.ts`（API key / Vertex ADC）。
    - **官方無 `antigravity` provider**（全倉庫 provider 目錄搜尋為 0 筆）。
  - **關鍵架構分層（避免違規反代，改用「大腦 + 委派核心」雙層混合）**：
    - ❌ **不建議的做法**：試圖用非官方 OAuth 擷取或反代腳本把三家桌面／訂閱憑證硬接到 `pi.registerProvider()` 當作免費模型 API（易觸發帳號封鎖、且違反憑證安全原則）。
    - ✅ **合規且極盡利用三家核心的雙層架構**：

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    Pi Hybrid Harness (本地控制平面)                      │
│  [TUI / RPC / Tree Session / Project Trust / PowerShell+GitBash 工具]    │
│                                                                         │
│  TypeScript Extension (`pi-hybrid-relay`)：                              │
│   ├─ /codex, dispatch_codex() ───────▶ codex.exe (worktree + Terra/Sol) │
│   ├─ /claude, dispatch_claude() ─────▶ claude.exe (深度架構 / Hooks)     │
│   ├─ /agy, dispatch_antigravity() ───▶ language_server.exe / agent-relay│
│   └─ /relay-ask, /relay-inbox ───────▶ SanHsien/agent-relay (ask/answer)│
└─────────────────────────────────────────────────────────────────────────┘
```

- **When & Where（適用時機與環境條件）**：
  - 維護者環境為 **Windows 11 原生（非 WSL）**。依 `pi` 官方 `windows.md`，Pi 原生支援 Windows（預設使用 Git Bash，並可設定 `defaultTools: ["read", "powershell", "edit", "write"]` 讓模型直接呼叫 `pwsh.exe`），建議搭配 **Windows Terminal**（避免舊版 `conhost` 全螢幕切換崩潰或字元殘留問題）。
- **Key Metrics / Numbers（客觀事實數據）**：
  - `earendil-works/pi` 內建工具數：**4** 個（`read` / `write` / `edit` / `bash`，Windows 可選換為 `powershell`）；系統提示詞規模：**< 1,000 tokens**。
  - 提供 **4** 種執行模式：Interactive TUI、Print（`--print`）、JSON（`--mode json` JSONL 事件流）、RPC（`--mode rpc` 雙向長駐 JSONL 控制），另附 Node.js/Bun TypeScript SDK。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/agent-relay`（已實作跨機/跨代理信箱與 `ask` / `answer` 非同步決策流，為非同步派工的標準傳輸骨幹）。
  - `SanHsien/agent-cortex`（Windows 原生控制平面與新會話啟動）。
  - `SanHsien/agent-advisor`（風險分級與預設／Flash／Pro 路由策略）。
  - `SanHsien/harness-guard`（執行前／結案前防呆 Hook）。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **樹狀會話（Tree-Structured Sessions）＋ Steering 即時插話**：Pi 允許在單一會話任意節點開分支實驗再回到主幹，這是目前單純使用獨立 CLI session 時最欠缺的「單人極速試錯」體驗。
    2. **Pi 的輕量 Extension 與 RPC 介面**：不需要 fork `pi` 本體，只要寫一個 TypeScript Extension（註冊 `dispatch_codex`、`dispatch_claude`、`dispatch_antigravity` 三個工具與 `/relay` 指令），就能把現有 `agent-relay` 與本機三個核心接進同一個操作面板。
    3. **Project Trust 保護機制**：Pi 遇到工作目錄的 `.pi/extensions`、`.pi/mcp.json` 等可執行設定時會先要求信任決定（`~/.pi/agent/trust.json`），與全域規則「外部擴充零信任」理念相容，但須注意 `AGENTS.md` / `CLAUDE.md` 仍會依設定載入，對外部 repo 仍應保持隔離審查。
  - **不適用 / 需調整的部分**：
    1. **不要用 Pi 重寫一個全新的 `agent-relay` 或 `agent-cortex`**：維護者已經有經過實測的 `agent-relay`（含 `ask`/`answer`、worktree 隔離、SSH 簽章驗證、461 tests 綠燈），重複造輪子只會分散維護精力；Pi 應定位為**人類面向的前端指揮台（Commander TUI）＋ 即時編寫工具**，長任務與跨機派工仍交給 `agent-relay`。
    2. **Antigravity 不可透過非官方 API/OAuth 塞進 `pi-ai`**：必須透過官方 `language_server.exe agentapi new-conversation` 或 `agent-relay send --to antigravity --ref antigravity-session:new` 驅動 Desktop 頂層會話，才能穩定使用其 IDE／Sidecar／多模型能力。
    3. **Windows 終端與安全邊界**：Pi 本身沒有內建 OS 沙盒（官方 `security.md` 明言工具以當前使用者權限執行），在 Windows 上委派破壞性或大規模實作任務時，應固定交給 `codex --sandbox workspace-write` 或 git worktree 執行，而非放任 Pi 直接在主分支裸跑。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-01`**｜**[優先級：中]** 在 Windows 11 原生環境沙盒安裝並實測 `earendil-works/pi`，驗證 TUI、`powershell` 工具與 `openai-codex` / `anthropic` provider 相容性，並定案與 `agent-relay` 的分工邊界
  - **目標範圍**：本機測試環境（Windows Terminal + `C:\GitHub\_sandbox\pi-test`）與 `C:\GitHub\ai-inbox` 評估紀錄
  - **具體做法**：
    1. 依 `earendil-works/pi` 官方文件於隔離目錄安裝 Pi CLI，確認於 Windows Terminal 下全螢幕切換、中文輸入與 Git Bash / `powershell` 工具（`["read", "powershell", "edit", "write"]`）皆正常運作。
    2. 實測官方內建 `openai-codex` OAuth 與現有 API key 環境變數連線，以及 `--mode json` / `--mode rpc` 輸出格式。
    3. 產出簡短實測結論與架構定案（確認 Pi 作為「單人即時 TUI + 委派面板」，不取代 `agent-relay` 既有信箱／決策流）。
  - **驗收標準（DoD）**：留下 Windows Terminal 實跑紀錄（`pi --version`、工具呼叫成功輸出、`--mode json` 樣本）與定位定案紀錄。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*

- [ ] **`T-20261115-02`**｜**[優先級：低]** 實作 Pi 混合型擴充套件 `pi-hybrid-relay`（於 Pi 內統一委派 `codex` CLI、`claude` CLI、Antigravity 頂層對話與 `agent-relay` 問答）
  - **目標範圍**：新建 `C:\GitHub\pi-hybrid-harness`（對應 `SanHsien/pi-hybrid-harness`）或作為 `agent-relay` 擴充套件（依 `T-20261115-01` 結論定案）
  - **具體做法**：
    1. 以 TypeScript 撰寫 Pi Extension，透過 `pi.registerTool` 與 `pi.registerCommand` 封裝四項核心能力：`dispatch_codex`（強制 worktree 與可選 Terra 模型路由）、`dispatch_claude`（呼叫 `claude -p` 或 `claude --bg`）、`dispatch_antigravity`（呼叫 `agent-relay send --to antigravity --ref antigravity-session:new`）、以及 `relay_questions`（串接 `agent-relay inbox --questions` 與 `answer`）。
    2. 實作 `tool_call` 安全攔截 Hook，對高風險刪除／跨 repo 寫入要求二次確認。
    3. 補齊 TypeScript 型別檢查與單元／整合測試。
  - **驗收標準（DoD）**：在 `T-20261115-01` 通過前提下，於 Pi TUI 實測成功透過 extension 工具各委派一次任務並收回結果，且型別檢查與測試全綠、推送至 `SanHsien` 個人 repo。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
