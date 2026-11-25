---
id: "2026-11-25-google-aqua-adk-recipes-ambient-quality-eval"
title: "Google 開源環境品質智慧體 AQuA 與 `google/adk-recipes` 評析：請求鏈路外唯讀邊車、五階段聚類診斷與佐證溯源機制"
source_url: "https://www.infoq.cn/article/YAc2TqCHc09kAFF1A7BS"
source_platform: "InfoQ 中文 / GitHub (google/adk-recipes)"
author: "Leela Kumili（InfoQ 原著）／明知山（譯）／Google ADK Team"
analyzed_at: "2026-11-25"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 2
source_replies: 0
source_reviewed_at: "2026-11-25"
source_review_note: "已透過內建瀏覽器完整閱讀 InfoQ 中文全文（含 2 張配圖、4 個行內程式碼標記，留言區確認 0 則），並透過 gh api 唯讀檢閱 google/adk-recipes（README、AGENTS.md、.agents/skills/ 及 core/python/ambient-quality-agent 原始碼結構與 README）。"
status: pending
cluster: 3
cluster_role: "AQuA邊車品質稽核"
short_title: "Google AQuA邊車稽核評析"
tags:
  - google-adk
  - aqua
  - ambient-agent
  - telemetry
  - root-cause-analysis
  - evaluation
  - sidecar
---

# Google 開源環境品質智慧體 AQuA 與 `google/adk-recipes` 評析：請求鏈路外唯讀邊車、五階段聚類診斷與佐證溯源機制

- **來源文章**：[InfoQ 中文：《谷歌开源环境质量智能体 AQuA，用于诊断生产环境 AI 智能体故障》](https://www.infoq.cn/article/YAc2TqCHc09kAFF1A7BS)（`2026-11-25`，作者 Leela Kumili、譯者明知山；英文原文 [`infoq.com/news/2026/11/google-ambient-agent-prod/`](https://www.infoq.com/news/2026/11/google-ambient-agent-prod/)）
- **開源倉庫**：[`google/adk-recipes`](https://github.com/google/adk-recipes)（`Apache-2.0`，`10,674` stars，主實作位於 `core/python/ambient-quality-agent`）
- **分析日期**：`2026-11-25`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/external-judge-audit.md`](../docs/external-judge-audit.md)（外部獨立審查與證據稽核規格）
  - [`docs/irrefutable-evidence-and-invalid-patterns-spec.md`](../docs/irrefutable-evidence-and-invalid-patterns-spec.md)（確定性證據與禁止自報信心分數之規範）
  - [`docs/agent-skills-curation-and-context-budget-spec.md`](../docs/agent-skills-curation-and-context-budget-spec.md)（Agent Skills 分層與 `.agents/skills/` 對照）

---

## 0. 原始資料盤點（InfoQ 全文、2 張配圖與 `google/adk-recipes` 實查）

- **InfoQ 文章摘要與 2 張配圖**：
  - **封面插畫**：Google「G」字角色手持刷子清理紅色愛心（無圖說）。
  - **架構圖（圖說：`AQuA 边车架构（来源：谷歌开发者博客）`）**：展示 `users → Your agent` 的請求鏈路之外，業務 Agent 非同步寫入 `session telemetry` 並於每次部署擷取 `source snapshot (written at each deploy)`；**AQuA（Sidecar）** 明確標註 **`not in the request path, never writes back`**，僅讀取遙測與不可變源碼快照後輸出至 `insights (BigQuery)`。
  - **留言區**：`0` 則留言（顯示「暂无评论」）。
- **AQuA 核心機制（InfoQ 與 `core/python/ambient-quality-agent/README.md` 交叉對照）**：
  1. **目標問題**：抓出傳統基礎設施監控漏掉的**靜默品質回歸（silent quality regressions）**，如跳過必要工具呼叫卻回傳成功回應、任務轉交時遺失使用者偏好。
  2. **三種遙測來源與運行觸發**：支援 BigQuery Agent Analytics plugin（`big_query`）、Cloud Telemetry `_AllSpans`（`cloud_ops`）與 `agents-cli` 日誌匯出（`cloud_logging`）；可排程、部署後或按需（`agents-cli aqua schedule-investigation`）採樣最多 **1,000 條近期會話**。
  3. **五階段分析管線**：`採樣 → 審查（LLM 對照 goal.md + 確定性 Python 自訂指標 agents-cli aqua metrics publish）→ 聚類發現 → 候選聚類核驗（每聚類最多抽查 3 份完整會話紀錄）→ 問題追蹤（NEW / RECURRING / 14 天無復現自動 RESOLVED）`。
  4. **不可變快照根因分析與佐證溯源**：對比部署時擷取的源碼快照，根因必須引用**追蹤鏈路（Trace）**與**已部署快照中的有效檔案路徑及行號範圍**，**不會自動修改程式碼或建立 PR**。文中引述：「有效結論靠的是佐證溯源，而不是自報的置信分數。」
  5. **文中多智慧體出行應用實測數據**：生產會話抽測 **32 條會話** → 識別 **42 條觀測** → **9 個候選聚類** → 核驗剔除 3 個無法證實的聚類，確認 **6 個問題**；修改提示詞後之**受控重放實驗**（非線上真實流量）對比：繞過座位校驗 `15 → 2`、遺漏飲食偏好 `7 → 0`、全部校驗通過 `5 → 13`。
  6. **已知兩大限制**：採樣上限可能漏掉罕見故障；重放未必能完整重現外部狀態。
- **`google/adk-recipes` 倉庫結構實查**：
  - `core/python/` 收錄 11 個官方參考配方（含 `ambient-quality-agent`、`long-horizon-harness`、`safety-plugins`、`cross-session-memory`、`oauth-user-consent-flow` 等）；另有 `contrib/`（社群／垂直領域可部署配方）與 `plugins/`（給終端使用者安裝的垂直領域技能，如 `plugins/retail/`）。
  - `.agents/skills/` 則清楚區分為**「維護此 repo 的開發者技能（Repo skills）」**（含 `github-pr-review` 及其 `check_house_rules.py` / `verify_findings.py`、`generate-python-runnability-test`、`repo-oracle` 等），`AGENTS.md` 明定不可與 `plugins/` 或 `recipes/` 改動混在同一個 PR，且標註 `gemini-2.0-flash` / `gemini-2.5-flash` 已棄用、改用 `gemini-3.7-flash`。

---

## 1. 與本專案現有架構的對照與啟發

1. **「請求鏈路外、永不回寫」的邊車稽核原則**：
   - AQuA 將「線上執行」與「離線品質診斷」徹底隔離，且明確**只產出帶 Trace＋源碼行號佐證的 Insight，不自動改碼開 PR**——這與本庫 [`docs/external-judge-audit.md`](../docs/external-judge-audit.md) 的獨立審查精神一致，並補上了「**跨時間視窗聚類＋14 天自動 `RESOLVED` 狀態機**」的長期追蹤視角。
2. **「佐證溯源取代自報信心分數」與「候選聚類二次核驗」**：
   - 審查階段先做廣度聚類，再由核驗模組抽查最多 3 份完整紀錄剔除假陽性（9 剔 3 剩 6），以及「確定性 Python 指標 + `goal.md`」雙軌評分，可作為日後強化本庫 `review_pipeline.py` 與離線日誌診斷的參考設計。
3. **`google/adk-recipes` 的 `.agents/skills/` 與 `plugins/` 嚴格邊界**：
   - 倉庫以 `AGENTS.md` 強制隔離「維護倉庫的 `.agents/skills/`」與「交付給使用者的 `plugins/`」，並配有 `check_house_rules.py` 與 `verify_findings.py` 等腳本化 PR 審查工具，值得唯讀檢閱參考。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261125-01`**｜**[優先級：中]** 萃取 Google AQuA（`ambient-quality-agent`）之「唯讀邊車架構、五階段聚類核驗與 `NEW/RECURRING/RESOLVED(14d)` 狀態機」撰寫為離線品質稽核參考規格 `docs/ambient-quality-agent-sidecar-spec.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\ambient-quality-agent-sidecar-spec.md`（收錄於集群 3）
  - **執行步驟**：
    1. 整理 AQuA 的邊車邊界（`not in the request path, never writes back`）、五階段流水線（採樣 → `goal.md`＋確定性指標審查 → 聚類 → 最多 3 份全紀錄核驗 → 問題追蹤狀態機）與不可變部署源碼快照溯源契約。
    2. 對照本庫 `review_pipeline.py` 與 `docs/external-judge-audit.md`，界定哪些機制適用於本機多 Agent 日誌事後診斷（如候選發現後二次全文核驗、禁止自報置信分數）。
  - **驗收標準（DoD）**：產出 `docs/ambient-quality-agent-sidecar-spec.md`，明確標註重放實驗與採樣限制，且 `python tools/verify_inbox.py` 驗證通過。

- [ ] **`T-20261125-02`**｜**[優先級：低]** 唯讀檢閱 `google/adk-recipes` 的 `.agents/skills/`（`github-pr-review`、`generate-python-runnability-test`、`repo-oracle`）與 `core/python/long-horizon-harness`、`safety-plugins`，評估可復用設計模式
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\`（可併入 `docs/ambient-quality-agent-sidecar-spec.md` 附錄或獨立唯讀評析報告，收錄於集群 3；嚴禁未經安全檢驗直接安裝第三方 skill）
  - **執行步驟**：
    1. 透過 `gh api` 唯讀讀取 `.agents/skills/github-pr-review/scripts/check_house_rules.py`、`verify_findings.py`、`generate-python-runnability-test` 與 `core/python/long-horizon-harness/README.md`。
    2. 評估其「Repo skills vs User plugins」隔離規範、規則漂移測試（`test_house_rules_drift.py`）與可執行性測試生成模式對 `ai-inbox` / `agent-assets` 的借鏡價值。
  - **驗收標準（DoD）**：完成唯讀檢閱並產出具體可採納與不採納項目清單，確認無執行任何未審查外部腳本，且 `python tools/verify_inbox.py` 驗證通過。
