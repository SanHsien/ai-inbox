---
id: "2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration"
title: "升級 Claude Opus 5.5 前置檢查：/claude-api prompt-audit、API 破壞性變更與成本結構評估"
source_url: "https://code.claude.com/docs/en/changelog"
source_platform: "Social / Anthropic"
author: "社群實戰整理（作者宣稱最低版本 Claude Code 2.1.283+ / 本機 2.1.322，未查證）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
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

- **來源連結**：[官方 changelog](https://code.claude.com/docs/en/changelog) ｜ [官方 overview](https://platform.claude.com/docs/en/models/opus-5-5/overview) ｜ [Opus 5 overview](https://platform.claude.com/docs/en/models/opus-5/overview) ｜ [官方 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)
- **發布平台 / 作者**：`社群實戰整理`（作者宣稱最低版本需求 Claude Code `2.1.283+` / 本機環境宣稱 `2.1.322`，皆未經本輪獨立查證）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 核心內容摘要（5W1H 初篩與實查補充）

- **Who（作者背景 / 執行機構）**：社群實戰整理作者（身分未獨立查證；宣稱需求 Claude Code `2.1.283+` / 本機環境 `2.1.322`，未查證）與 Anthropic 官方（模型與 API 發布機構）。
- **What（核心產出 / 做了什麼）**：Anthropic 正式推出 Claude Opus 5.5（`claude-opus-5-5`）；社群提出提示詞衝突稽核（`prompt-audit`）、API 遷移指引與快取降價成本評估。
- **Why（為解決什麼問題 / 痛點）**：升級新模型時因自適應思考強制開啟、Tool Use 語法嚴格約束、對話歷史簽章綁定等破壞性變更，容易遭遇 API 報錯或靜默行為改變，需預先進行提示詞與相容性盤點。
- **How（核心架構與關鍵機制）**：
  - 區分 `/claude-api prompt-audit`（提示詞與 tool descriptions）與 `/doctor prompt-audit`（掃描 skills/agents/commands）。
  - API 遷移調整：以 `output_config.effort` 控制思考深度、工具選擇改 `tool_choice: {"type": "auto"}` 搭配嚴格 schema、對話歷史保留有效簽章與相容 prefix。
  - Prompt Caching Read 降價 60%，評估長對話與高重複上下文成本。
- **When & Where（適用時機與場景）**：既有專案準備切換為 Claude Opus 5.5 模型、調用 Claude Messages API 或在 Claude Code 終端執行開發時。
- **Key Metrics / Numbers（關鍵指標與量化數據）**：Prompt Cache Read 單價由 Opus 5 的每百萬 token（MTok）`$0.50` 降至 `$0.20`（降幅 60%）；預設 `effort` 為 `medium`；社群宣稱之「成本極低」無用量實測數據（未查證）。

### 1.1 切換 Opus 5.5 前的三項建議動作（作者宣稱與實查）
1. **提示檔衝突稽核（區分兩類指令）**：
   - 官方 changelog 區分 `/claude-api` 的 `prompt-audit`（針對提示詞與 tool descriptions）與 `/doctor prompt-audit`（別名 `/checkup prompt-audit`，掃描 Claude Code 指令檔／skills／agents／commands）。兩者掃描範圍不同，不可混用前者保證後者的掃描結果。
   - 掃描專案中的既有指示與跨檔案矛盾規則，列出檔名、行號與建議改法，未經確認不改檔。
2. **API 程式碼遷移（`/claude-api migrate this project to claude-opus-5-5`）**：
   - 官方提供 migration 指引；修改前先確認範圍，修改後列出需人工驗證的端點。
3. **訂閱額度與成本變化（官方定價與作者宣稱）**：
   - 原作者貼文中提及之 Usage 頁面 `Reset for free` 優惠截圖已過期，不得直接推導為目前帳號之長期福利。
   - **預設推理深度與快取降價**：依官方 overview，Opus 5.5 模型 ID 確認，預設 `effort` 降至 **`medium`**；Prompt Cache Read 單價由 Opus 5 的每百萬 token（MTok）`$0.50` 降至 `$0.20`（降幅 **60%**），高重複上下文專案受益最大。

### 1.2 實查補充：Opus 5.5 API 破壞性與靜默變更清單
- **會直接回傳 HTTP 400 的舊寫法**：
  1. **禁止關閉 Thinking**：`thinking: {"type": "disabled"}` 與手動 `budget_tokens` 失效（思考改為永遠自適應開啟），須改用 `output_config={"effort": "low" | "medium" | "high" | "xhigh" | "max"}`。
  2. **Tool Use 語法約束**：`tool_choice={"type": "any"}` 等直接鎖定語法須改為 `tool_choice={"type": "auto"}` 搭配嚴格 schema（`"strict": true` 與 `additionalProperties: false`），但約束輸入結構不代表每輪對話必定呼叫工具。
  3. **對話歷史修改約束**：修改歷史可能使 prefix check 失敗，不一定回傳 400，呼叫端須處理兩種結果，附官方 migration guide：https://platform.claude.com/docs/en/models/opus-5-5/migration-guide；thinking blocks 並非一律禁止回傳歷史，官方 migration guide 明確要求保留有效簽章與相容的歷史 prefix。遷移稽核還須納入 sampling 參數與 assistant prefill 等項目。
  4. **Computer Use 版本淘汰**：`computer_20251124` 須升級為 `computer_toolset_20260801`（但非全平台淘汰，Bedrock 等受託管環境存在例外）。
- **回傳 HTTP 200 但行為改變（靜默風險）**：
  - 未顯式指定 `effort` 時預設為 `medium`（若需最高推理深度須明確傳入 `high` 或以上）。
  - 工具呼叫間的進度文字改封裝於 `thinking` block；但 `thinking.display` 的預設省略不等於所有文字串流都空白，應檢查解析器按 block type 處理、保留簽章與最終 text，而非全面開啟 thinking 顯示。
- **Prompt Audit 清理準則**：不可僅因命中 thinking 關鍵字就刪除規則，官方 changelog 明確說明稽核會保留 Claude Code 有文件依據的關鍵字。

### 1.3 CQR 論證檢驗（Claim - Evidence - Reasoning）
- **主張（Claim）**：Opus 5.5 引入自適應思考與 prompt caching 降價，本機核心 repo 應執行 prompt audit 與 API 相容性唯讀盤點。
- **證據（Evidence）**：[官方 overview](https://platform.claude.com/docs/en/models/opus-5-5/overview)、[Opus 5 overview](https://platform.claude.com/docs/en/models/opus-5/overview)、[官方 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)、[官方 changelog](https://code.claude.com/docs/en/changelog)。
- **推論（Reasoning）**：模型降價 60%（快取讀取從 $0.50/MTok 降至 $0.20/MTok）為官方明確數據；然而原作者宣稱之「成本極低」無用量實測數據支持，且 CLI prompt-audit 與 doctor 稽核邊界不同。API 變更涉及簽章保留與 Bedrock 例外，須以唯讀盤點取代直接自動修改程式。

---

## 2. 啟發與適用性評估

- **核心資產適用性評估（`SanHsien/agent-assets`（私有）、`ai-inbox`、`agent-relay`）**：
  - 本機跨 AI 規則庫 `SanHsien/agent-assets`（私有）與各專案 `CLAUDE.md`／`skills/` 累積規則較多，可能存在替舊模型寫的過時字眼或跨檔衝突。
  - 「成本極低」僅為作者宣稱，缺乏真實用量證據；且標題承諾唯讀，若實作改動三個 repo 會造成授權矛盾。因此改由 Codex 進行只讀讀檔與輸出 findings，不呼叫 Claude。
  - 若維護者後續仍要求官方 Claude skill 的交叉檢查，應延至交辦指定的 **2026-11-16 08:00（Asia/Taipei）之後**，且先由維護者確認實際額度已重置（此時間為排程條件，非本輪帳號即時狀態）。
  - 私有 repo 寫 `SanHsien/agent-assets`（私有），其內部 findings 不得外洩至公開 repo。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-18`**｜**[優先級：中]** 由 Codex 唯讀盤點三個核心 repo 的提示檔衝突與 Anthropic API 呼叫相容性
  - **目標範圍**：唯讀檢閱 `SanHsien/agent-assets`（私有）、`SanHsien/ai-inbox`、`SanHsien/agent-relay` 的指定 checkout；公開產出限 `SanHsien/ai-inbox` 的 `docs/claude-prompt-and-api-readonly-audit.md`。私有內部 findings 只交付於 `SanHsien/agent-assets`（私有）的 `docs/prompt-api-audit-findings.md`，不得複製到公開 repo。
  - **具體做法**：先讀各 repo 指引並記錄 checkout 基準；列出實際檢閱的 AGENTS／既有 CLAUDE／rules／skills／commands／agents，不建立新的 CLAUDE.md。逐項對照官方文件，列已確認衝突、過時項目、待確認與不適用項目，附公開檔案行號及具體修改建議。確認是否真的直接呼叫 Anthropic API，區分 CLI 委派、文件範例與執行中 adapter；只有實際模型／平台適用時才列遷移風險。不得僅靠關鍵字自動刪改 thinking 規則，也不改模型路由、hooks 或 API 程式。不執行 Claude skill、API 或額外 reviewer。
  - **驗收標準（DoD）**：上述兩份具名報告存在；公開報告涵蓋三 repo 的檢閱範圍、基準、來源 URL、分類與不含私有內容的摘要。私有報告可明列「無 findings」及檢閱邊界。每個 API finding 寫明呼叫點、模型／平台、適用條件、建議修法；無直接 consumer 可列 N/A，但需列檢閱證據，不要求虛構遷移。確認私有標記、零機密與無真實家目錄帳號；對新增文件依各目標 repo 規範跑檢查，保存命令／exit code。不得把本任務稱為已完成 API 遷移或 Claude 官方 skill 實測。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：公開版 docs/claude-prompt-and-api-readonly-audit.md；私有版在 SanHsien/agent-assets（私有）docs/prompt-api-audit-findings.md（2955bab）。三個 repo 都沒找到直接呼叫 Anthropic Messages API 的程式，只有 CLI 委派、gateway 環境注入與範例。Codex 唯讀稽核，未呼叫 Claude；獨立複審後修正 R1（公開版補記私有報告已交付）。
