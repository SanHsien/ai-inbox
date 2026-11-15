---
id: "2026-11-15-openai-codex-plugin-cc-collaboration"
title: "openai/codex-plugin-cc：在 Claude Code 內直接叫用 Codex 協作與對抗式審查評估"
source_url: "https://be-ai-curator.com/blog/claude-code-codex-collaboration"
source_platform: "Blog / GitHub"
author: "OpenAI (openai/codex-plugin-cc) & be-ai-curator"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 3
cluster_role: "Codex插件協作"
short_title: "CodexPluginCC雙AI協作"
tags:
  - claude-code
  - codex
  - codex-plugin-cc
  - adversarial-review
  - multi-agent
  - ssot
---

# openai/codex-plugin-cc：在 Claude Code 內直接叫用 Codex 協作與對抗式審查評估

- **來源連結**：[openai/codex-plugin-cc (GitHub)](https://github.com/openai/codex-plugin-cc)（Apache-2.0，35,129 Stars）｜ [Claude Code × Codex 協作長文 (be-ai-curator)](https://be-ai-curator.com/blog/claude-code-codex-collaboration)
- **發布平台 / 作者**：`GitHub / Blog` / `OpenAI` & `be-ai-curator`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（模型燒額度分權矩陣）
  - [`notes/2026-11-15-multi-ai-20-dollar-role-routing-anti-fake-green.md`](./2026-11-15-multi-ai-20-dollar-role-routing-anti-fake-green.md)（多 AI 角色路由與反假綠燈）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：OpenAI 官方開源插件 `openai/codex-plugin-cc`（Apache-2.0），讓使用者不必在 Claude 與 ChatGPT/Codex 雙視窗間來回複製貼上背景脈絡，直接在 Claude Code（含桌面 App Code 分頁）內呼叫 Codex 執行任務與程式碼審查。
- **Why（解決什麼痛點）**：
  - 單一模型自寫自審容易產生盲點，而雙視窗人工貼背景則會打斷專注力、浪費上下文重建時間。
  - 高階旗艦模型（如 Fable、GPT-6 Astra）在簡單任務過度發散時極易燒爆週用量；日常改以 **Claude Opus 5.5** 為主力規劃與實作，僅在需要第二意見或 OpenAI 專屬能力時呼叫 Codex。
- **How（核心運作機制與指令）**：
  1. **安裝方式**：Claude Code／桌面版 `設定 → Plugins` 加入市集 `openai/codex-plugin-cc`，新增 `Codex` 並登入 ChatGPT 帳號即可沿用既有 Codex CLI 驗證與獨立額度（免費方案僅支援基本協作，生圖等付費功能須付費方案）。
  2. **核心斜線指令**：
     - `/codex:review`：標準 Code Review（支援 `--background` 背景執行）。
     - `/codex:adversarial-review`：對抗式審查，請沒有參與撰寫過程的 Codex 從反方挑出隱含假設與邊界漏網。
     - `/codex:rescue`：卡關或測試失敗時將修復任務交棒給 Codex。
  3. **多媒體與平台功能接力**：如 Vox 風格短片由 Claude 規劃分鏡與動畫程式碼，將「生圖素材」或「OpenAI Realtime 語音模組」交給 Codex 產出後再拼回專案。
  4. **規則一致性**：透過 GitHub Repo 維護同一份規範說明書（Instructions），讓 Claude 與 Codex 讀取相同專案約束（網頁版無法讀取本機規則檔時亦可透過 Repo 同步）。
- **When & Where**：日常以 Claude Code 為主工作台，需要跨模型對抗審查、卡關救援或整合 OpenAI 原生生態工具時。

---

## 2. 啟發與適用性評估

- **與現有本機基建的高度共鳴與對照**：
  1. **「共讀同一份說明書」已落地為 `agent-assets` SSOT**：本機已建置 `C:\GitHub\agent-assets`（入口 `rules/AGENTS.md` 與 `knowledge/`），正是跨 Claude / Codex / Antigravity / Hermes 共用規則的單一真實來源。
  2. **跨代理協作與跨模型審查已有現有架構**：
     - **跨模型審查**：本機已有 `ai-review` Skill（預設走 Codex CLI 做二審）與 `SanHsien/agent-advisor`。
     - **跨代理派工**：本機已有 `SanHsien/agent-relay`（含 `ask`/`answer`、worktree 隔離與合併閘門）。
  3. **`openai/codex-plugin-cc` 的互補定位**：當使用者單純停留在 Claude Code CLI 或 Claude Desktop 內工作、不想額外啟動 `agent-relay` 派工管線時，官方插件提供了零切換成本的 `/codex:adversarial-review` 與 `/codex:rescue` 快捷入口。
- **實查邊界與避坑提醒**：
  - **「Codex 畫素材」的前提**：`codex-plugin-cc` 本身是 Code Review 與任務委派外掛，並非獨立繪圖模型；實際生圖仰賴 Codex 端設定的生圖工具／OpenAI Image API 權限與付費額度。
  - **避免職責重疊與環境衝突**：若同時啟用 `codex-plugin-cc` 與本機 `agent-relay`／自訂 hooks，應先確認兩者的 hook 生命週期與 Codex CLI 認證路徑不互相干擾。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-15`**｜**[優先級：低]** 在本機 Claude Code / Claude Desktop 評估安裝 `openai/codex-plugin-cc`，驗證 `/codex:adversarial-review` 與既有 `ai-review`／`agent-relay` 之分工邊界
  - **目標範圍**：本機 Claude Code 插件環境與 `C:\GitHub\ai-inbox\docs\`
  - **具體做法**：
    1. 檢查 `openai/codex-plugin-cc` 的 `plugins/` 與 `scripts/` 原始碼，確認無破壞本機全域 hooks 或繞過沙盒之預設行為。
    2. 於單一測試專案實測 `/codex:adversarial-review` 與 `/codex:rescue`，比對其與現行 `ai-review` Skill／`agent-relay` 派工在 token 消耗與報告品質上的差異，定案日常預設使用情境。
  - **驗收標準（DoD）**：完成安全檢視與實測比對，確認與現有 `agent-relay` / hooks 無衝突並記錄使用邊界。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
