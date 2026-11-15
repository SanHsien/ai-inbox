---
id: "2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration"
title: "升級 Claude Opus 5.5 前置檢查：/claude-api prompt-audit、API 破壞性變更與成本結構評估"
source_url: "https://code.claude.com/docs/en/changelog"
source_platform: "Social / Anthropic"
author: "匿名社群分享（實測版本 Claude Code 2.1.283+ / 本機 2.1.322）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 3
cluster_role: "Opus5.5遷移與稽核"
short_title: "Opus5.5稽核與遷移"
tags:
  - claude-opus-5-5
  - prompt-audit
  - claude-api
  - adaptive-thinking
  - prompt-caching
  - migration
---

# 升級 Claude Opus 5.5 前置檢查：/claude-api prompt-audit、API 破壞性變更與成本結構評估

- **來源連結**：Claude Code 內建指令 `/claude-api prompt-audit` & `/claude-api migrate this project to claude-opus-5-5`
- **發布平台 / 作者**：`社群實戰整理`（本機實測 `claude --version` 為 `2.1.322 (Claude Code)`，高於最低需求 `2.1.283`）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要與實查補充

### 1.1 切換 Opus 5.5 前的三項建議動作
1. **提示檔衝突稽核（`/claude-api prompt-audit`）**：
   - 掃描專案中的 `CLAUDE.md`、`rules/`、`skills/`、`commands/`、`agents/`，抓出「替舊模型寫的過時指示」與「跨檔案彼此矛盾的規則」（例如一個檔案寫已自動化、另一個檔案還要求手動操作），列出檔名、行號與建議改法，**未經確認不改檔**。
2. **API 程式碼遷移（`/claude-api migrate this project to claude-opus-5-5`）**：
   - 自動更新 `model` ID 與不相容參數；修改前先確認範圍，修改後列出需人工驗證的端點。
3. **訂閱額度與成本變化**：
   - Usage 頁面的 `Reset for free`（原文帳號顯示 `10/23` 到期，截至 `2026-11-15` 多已過期，以帳號實際頁面為準）。
   - **預設推理深度與快取降價**：Opus 5.5 預設 `effort` 由 Opus 5 的 `high` 降至 **`medium`**；Prompt Cache Read 單價由 `\$0.50` 降至 `\$0.20`（降幅 **60%**），高重複上下文專案受益最大。

### 1.2 實查補充：Opus 5.5 API 破壞性與靜默變更清單
- **會直接回傳 HTTP 400 的舊寫法**：
  1. **禁止關閉 Thinking**：`thinking: {"type": "disabled"}` 與手動 `budget_tokens` 失效（思考改為永遠自適應開啟），須改用 `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`。
  2. **強制 Tool Use 語法**：`tool_choice={"type": "any"}` 等直接鎖定語法須改為 `tool_choice={"type": "auto"}` 搭配嚴格 schema（`"strict": true` 與 `additionalProperties: false`）。
  3. **對話歷史修改**：中途篡改歷史訊息或重播 thinking block 會報錯，對話歷史須嚴格維持 append-only。
  4. **Computer Use 版本淘汰**：`computer_20251124` 須升級為 `computer_toolset_20260801`。
- **回傳 HTTP 200 但行為改變（靜默風險）**：
  - 未顯式指定 `effort` 時預設為 `medium`（若需最高推理深度須明確傳入 `high` 或以上）。
  - 工具呼叫間的進度文字改封裝於 `thinking` block，若前端只擷取一般文字串流會呈現空白，須調整 `display` 顯示模式。
- **Prompt Audit 清理準則**：移除舊版 `"Think step by step"`、`<scratchpad>`、`"answer immediately / don't think"` 等易與 Adaptive Thinking 衝突的詞句，改為在單一區塊明確定義完成標準（Done definition）與何時停下來發問。

---

## 2. 啟發與適用性評估

- **直接適用本機資產（`agent-assets`、`ai-inbox`、`agent-relay`）**：
  - 本機跨 AI 規則庫 `C:\GitHub\agent-assets` 與各專案 `CLAUDE.md`／`skills/` 累積規則較多，極可能存在替舊模型寫的過時字眼或跨檔衝突；先跑一次只讀 `/claude-api prompt-audit` 成本極低且能避免上下文浪費。
  - 若有專案程式（如 `agent-relay`、`agent-advisor` 或周邊腳本）直接呼叫 Anthropic Messages API，應同步檢查是否殘留 `thinking.type = disabled`、`budget_tokens` 或 `tool_choice = any`。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-18`**｜**[優先級：中]** 對 `agent-assets`、`ai-inbox` 與 `agent-relay` 執行 `/claude-api prompt-audit` 只讀稽核，並盤點程式端 Claude API 相容性
  - **目標範圍**：`C:\GitHub\agent-assets`、`C:\GitHub\ai-inbox`、`C:\GitHub\agent-relay`
  - **具體做法**：
    1. 於本機 Claude Code（實測 `2.1.322`）依序對上述核心專案執行 `/claude-api prompt-audit`（只輸出矛盾與過時清單，不直接自動覆寫）。
    2. 搜尋並檢查各 repo 原始碼是否直接呼叫 Anthropic API 並殘留 `thinking: disabled`、`budget_tokens`、`tool_choice: any` 或 `computer_20251124`。
    3. 依稽核清單人工確認後清理矛盾規則，確保 SSOT 規則與 Opus 5.5 Adaptive Thinking 行為對齊。
  - **驗收標準（DoD）**：完成三個核心 repo 的只讀稽核報告，修正確認的跨檔衝突或過時 API 參數，並通過各 repo 既有測試與 `verify_inbox.py`。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
