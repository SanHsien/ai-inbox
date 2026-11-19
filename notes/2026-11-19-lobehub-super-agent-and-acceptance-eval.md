---
id: "2026-11-19-lobehub-super-agent-and-acceptance-eval"
title: "Woshipm 長文評估：LobeHub（Super-agent 組織化協作）與 lobehub/acceptance 實事求是驗收架構"
source_url: "https://www.woshipm.com/ai/6489382.html"
source_platform: "woshipm (人人都是產品經理)"
author: "袋鼠帝"
github_repo: "https://github.com/lobehub/acceptance"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: partial
source_images: 24
source_replies: 0
source_reviewed_at: "2026-11-19"
source_review_note: "正文6315字與評論區0則已全讀；33張圖中已實讀24張（圖1至23及圖32），圖0題圖與圖24至31共9張依停止指令未展開"
status: pending
cluster: 1
cluster_role: "組織化Agent與驗收"
short_title: "LobeHub與Acceptance"
tags:
  - lobehub
  - super-agent
  - acceptance
  - deepseek-harness
  - multi-agent
  - verification-gate
---

# Woshipm 長文評估：LobeHub（Super-agent 組織化協作）與 lobehub/acceptance 實事求是驗收架構

- **來源文章**：[狂揽 83.7K Star！开源版Super-agent来了，告别AI监工～（人人都是產品經理）](https://www.woshipm.com/ai/6489382.html)
- **核心相關專案**：
  - [`lobehub/acceptance`](https://github.com/lobehub/acceptance)（開源 Agent 驗收迴圈與 `lh acceptance` 工具）
  - [`deepseek-ai/dsh-superagent-prototype`](https://github.com/deepseek-ai/dsh-superagent-prototype)（DeepSeek Super-agent 研究原型）
  - `LobeHub`（83.7K Stars / Docker 部署 700 萬+，含 Chief Agent Operator 與 Skills 市場）
- **發布平台 / 作者**：`woshipm` / `袋鼠帝`（`2026-11-05`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh.md`](./2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh.md)（DSH 主動代理探討）
  - [`notes/2026-11-19-codex-claude-multi-agent-orchestration-landscape.md`](./2026-11-19-codex-claude-multi-agent-orchestration-landscape.md)（多代理協作與證據驗收生態）

---

## 1. 原始資料盤點（正文、24 張已檢視截圖與評論區）

- **正文核心架構對照（DeepSeek Super-agent vs. LobeHub 生產實踐）**：
  1. **Router 與 Worker 分層（防「人肉路由器」）**：上層常駐 Manager Agent（如 `Nasa`）在群聊統一接活、拆任務、驗收；下層 Worker Agent（如跑 Claude Code / Codex 的 `Dario`）**嚴禁直接在外部群說話**，僅沉澱產出至任務內部，完成後由 Manager 統一摘要匯報。
  2. **事件驅動與兩級過濾**：規則層 `Fast Path` 過濾大部分無關群消息，語義層 `Slow Path` 才交由模型裁決是否喚醒（無需 `@` 即可主動接單）。
  3. **存算三層分離（BYOM）**：無狀態雲端 Agent Loop + Redis/DB 狀態持久化 + 本地機器輕量 daemon（合蓋筆電仍可在常駐機繼續執行）。
  4. **Task 作為上下文錨點**：以類似 Linear 的 `Task` 頁收斂需求、代碼討論、中間產物、CI 與 PR，解開 DeepSeek 論文第 8.3 節「多 Agent 上下文邊界爆炸」的開放問題。
  5. **多模態驗收閉環（`Acceptance`）**：透過開源 `lobehub/acceptance` 將需求拆為可觀察檢查項 `C1..Cn`，無頭瀏覽器實測並打包截圖／錄屏／console 日誌成驗收報告供人類打回或放行。
- **作者實測結果（飛書群對比 LobeHub vs OpenClaw）**：
  - **主動拆活與依賴鏈**：LobeHub 未被 `@` 即在 9 秒內接單，拆出 `T-1`（統籌）與 `T-2 → T-3 → T-4` 依賴鏈及 `T-5`；隔天無需重述背景即可直接續接；同群的 OpenClaw 則必須 `@` 且等 3 分 36 秒才回單張靜態卡片、無任務樹與並行能力。
  - **誠實拒絕造假**：實測 `T-2` 連續 3 次被運行時取消成殭屍狀態時，LobeHub 明確回報「3 次無產物、沒有截圖可給，不會拿假的糊弄過去」，展現極佳的反假綠燈紀律。
- **已檢視圖片明細（33 張中實讀 24 張，圖 0 與圖 24–31 未展開）**：涵蓋 LobeHub 官網（83.7K Star）、Skills 市場（334,469 Skills）、`ibench.ai`（44 tasks / 832.1k combined stars / 34.1% best pass rate）、Router/Worker 圖、Discord `#dev` 與 `#v2.4 发版` 多代理核查紀錄、喚醒置信度後台、存算分離圖、Workspace 看板、飛書任務樹回覆（圖 22）及終端 `lh acceptance view` 輸出（圖 32，顯示 `rounds: 3`、`C1..C5` 檢查項狀態）。
- **評論區**：0 則留言。

---

## 2. 對現有系統的啟發與落差評估

- **高度共鳴的既有防線**：
  - 本機既有 `claim_evidence_guard`、`verification-protocol` 與「Worker 不直接對外發言、主協調統一彙報與對帳」原則，與文中 Router/Worker 隔離與「拒絕拿假圖糊弄」理念高度一致。
- **具體值得借鏡的新拼圖：`lobehub/acceptance`**：
  - 目前本機的 `claim_evidence_guard` 主要把關文字/指令輸出證據；對於 **UI／Web 前端類任務的「可觀察檢查項 `C1..Cn` 拆解 + 截圖/錄屏/控制台日誌打包 + 多輪打回紀錄（`.acceptances/`）」**，開源的 `lobehub/acceptance`（`lh acceptance`）提供了一套標準化 CLI 與 `.acceptances/` 產物結構，極具參考價值。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261119-03`**｜**[優先級：中]** 在沙盒唯讀檢閱 `lobehub/acceptance` 架構與 `.acceptances/` 多模態驗收規格
  - **目標範圍**：`C:\GitHub\_sandbox\lobehub-acceptance-audit` 與 `C:\GitHub\ai-inbox\docs\lobehub-acceptance-eval.md`
  - **執行步驟**：
    1. 僅以唯讀方式 clone `lobehub/acceptance` 至沙盒目錄（不執行安裝腳本或 `lh login`）。
    2. 檢閱其 `SKILL.md`、檢查項 `C1..Cn` 結構定義、`.acceptances/` 目錄產物格式及無頭瀏覽器截圖/錄屏採證流程。
    3. 評估如何將其「可觀察檢查清單 + 多輪打回沉澱」機制借鏡至本機 UI／端到端驗證協議，將完整評析寫入 `docs/lobehub-acceptance-eval.md`。
  - **驗收標準（DoD）**：產出 `docs/lobehub-acceptance-eval.md`，記錄 `lobehub/acceptance` 核心工作流、`.acceptances/` 格式與本機 `verification-protocol` 可借鏡項目，且 `python tools/verify_inbox.py` 驗證通過。
