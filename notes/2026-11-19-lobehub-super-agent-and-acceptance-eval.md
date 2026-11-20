---
id: "2026-11-19-lobehub-super-agent-and-acceptance-eval"
title: "Woshipm 長文評估：LobeHub（Super-agent 組織化協作）與 lobehub/acceptance 實事求是驗收架構"
source_url: "https://www.woshipm.com/ai/6489382.html"
source_platform: "woshipm (人人都是產品經理)"
author: "袋鼠帝"
github_repo: "https://github.com/lobehub/acceptance"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 33
source_replies: 0
source_reviewed_at: "2026-11-20"
status: done
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
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh.md`](./2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh.md)（DSH 主動代理探討）
  - [`notes/2026-11-19-codex-claude-multi-agent-orchestration-landscape.md`](./2026-11-19-codex-claude-multi-agent-orchestration-landscape.md)（多代理協作與證據驗收生態）

---

## 1. 原始資料盤點（正文、33 張圖與評論區）

- **正文核心架構對照（DeepSeek Super-agent vs. LobeHub 生產實踐）**：
  1. **Router 與 Worker 分層（防「人肉路由器」）**：上層常駐 Manager Agent（如 `Nasa`）在群聊統一接活、拆任務、驗收；下層 Worker Agent（如跑 Claude Code / Codex 的 `Dario`）**嚴禁直接在外部群說話**，僅沉澱產出至任務內部，完成後由 Manager 統一摘要匯報。
  2. **事件驅動與兩級過濾**：規則層 `Fast Path` 過濾大部分無關群消息，語義層 `Slow Path` 才交由模型裁決是否喚醒（無需 `@` 即可主動接單）。
  3. **存算三層分離（BYOM）**：無狀態雲端 Agent Loop + Redis/DB 狀態持久化 + 本地機器輕量 daemon（合蓋筆電仍可在常駐機繼續執行）。
  4. **Task 作為上下文錨點**：以類似 Linear 的 `Task` 頁收斂需求、代碼討論、中間產物、CI 與 PR，解開 DeepSeek 論文第 8.3 節「多 Agent 上下文邊界爆炸」的開放問題。
  5. **多模態驗收閉環（`Acceptance`）**：透過開源 `lobehub/acceptance` 將需求拆為可觀察檢查項 `C1..Cn`，無頭瀏覽器實測並打包截圖／錄屏／console 日誌成驗收報告供人類打回或放行。
- **作者實測結果（飛書群對比 LobeHub vs OpenClaw）**：
  - **主動拆活與依賴鏈**：LobeHub 未被 `@` 即在 9 秒內接單，拆出 `T-1`（統籌）與 `T-2 → T-3 → T-4 → T-5` 依賴鏈；隔天無需重述背景即可直接續接；同群的 OpenClaw 則必須 `@` 且等 3 分 36 秒才回單張靜態卡片、無任務樹與並行能力。
  - **誠實拒絕造假**：實測 `T-2` 連續 3 次被運行時取消成殭屍狀態時，LobeHub 明確回報「3 次無產物、沒有截圖可給，不會拿假的糊弄過去」，展現極佳的反假綠燈紀律。作者之後人工介入，三個子任務才全部完成；這段實測說明的是「失敗時如實回報」，不是「不需要人管」。
- **圖片明細（共 33 張，2026-11-19 讀 24 張，2026-11-20 補看其餘 9 張，已全部看完）**：先前讀的 24 張涵蓋 LobeHub 官網（83.7K Star）、Skills 市場（334,469 Skills）、`ibench.ai`（44 tasks / 832.1k combined stars / 34.1% best pass rate）、Router/Worker 圖、Discord `#dev` 與 `#v2.4 发版` 多代理核查紀錄、喚醒置信度後台、存算分離圖、Workspace 看板、飛書任務樹回覆（圖 22）及終端 `lh acceptance view` 輸出（圖 32，顯示 `rounds: 3`、`C1..C5` 檢查項狀態）。
- **2026-11-20 補看的 9 張（圖 0、圖 24–31）**：
  - 圖 0：題圖，Unsplash 圖庫照片（筆電上的程式碼），沒有資訊。
  - 圖 24：飛書群裡問「現在到哪一步」，主管 Agent 逐項回報每個任務的負責人、狀態與卡點（T-1 統籌進行中、T-2 執行中但還沒有產出、T-3／T-4 待開始並寫明依賴），還主動列出 T-2 可能卡住的兩個原因。
  - 圖 25：作者自繪的九步流程圖：群裡一句話 → 主管 Agent 判斷要不要接 → 建主 Task → 拆子 Task → 派給不同 Agent（可換模型）→ Workspace 看板並行 → 執行與中間產物 → Acceptance 驗收 → 通過才交付；**打回時回到拆子 Task 那一步，只重跑沒過的項目**。
  - 圖 26（動圖）：主管 Agent 把 T-2、T-3 的要求講清楚（差異要對照實際程式碼、逐條對應清單），並說 T-2 出結果後會按依賴鏈自動推進。
  - 圖 27（動圖）：隔天只說「繼續之前的任務」，主管 Agent 查看板後回報 T-2 核對、T-3 修訂、T-4 示例驗證都已完成，並列出四條核心差異與實際跑過的環境。
  - 圖 28：`lobehub/acceptance` 的 README 開頭，標語是「接受 AI 做的東西之前先看證據」，說明它把需求轉成可觀察的檢查、跑真的產品、把截圖／錄影／日誌掛在每個檢查項上，人可以整份接受或逐項打回。
  - 圖 29：LobeHub 任務頁。T-2 底下有「交付驗收 5」區塊，顯示 3 輪、14 分鐘、一句驗收目標，以及標著 `C1`、`C2`、`C3`、`C4`…的驗收清單（各有通過／待定圖示）。
  - 圖 30（動圖）：T-2 三次都被執行環境取消後，主管 Agent 給 A／B／C 三個處理選項，並主動更正狀態（T-2 已從執行中變成中斷，看板上不會再自己跑出結果），說明整條鏈停在這裡等人決定。
  - 圖 31：主任務 T-1 的頁面，子任務 2／3 完成；活動紀錄裡 T-2 第 2 次執行標「3／4 未通過」、T-3 標「1／1 已通過」。
  - 動圖（圖 26、27、30）是聊天畫面的捲動錄影，看到的是其中的畫面；內容與正文引用的文字一致。
- **補看後對先前描述的修正**：
  - 圖 32 的終端輸出要讀細一點：表頭有 `C#` 欄，`C1` 是「Task delivery acceptance」且狀態是**未執行**，`C2`–`C5` 通過；`USER` 欄五項都是待定；`BLOCK` 欄四項 `gate`、一項 `soft`；三輪分別是 planned、failed、passed；整體 `status: delivered`。也就是說，**整體標成已交付時，還有一項沒執行、人也還沒逐項確認**。
  - `C1`…`C5` 同時出現在任務頁（圖 29）與 CLI 的 `C#` 欄（圖 32），兩處一致。這比較像 LobeHub 產品與 `lh` CLI 顯示時的編號，不像單次執行時 agent 自己取的名字；CLI 不在公開 repo 內，仍無法從原始碼確認。
  - 作者實測到最後是「人介入之後才做完」：正文寫明干預後 T-2、T-3、T-4 才全部完成。原稿只寫了誠實回報失敗，沒寫這一句，已補在下面。
- **評論區**：0 則留言（2026-11-20 重看仍是 0）。

---

## 2. 對現有系統的啟發與落差評估

- **高度共鳴的既有防線**：
  - 本機既有 `claim_evidence_guard`、`verification-protocol` 與「Worker 不直接對外發言、主協調統一彙報與對帳」原則，與文中 Router/Worker 隔離與「拒絕拿假圖糊弄」理念高度一致。
- **具體值得借鏡的新拼圖：`lobehub/acceptance`**：
  - 目前本機的 `claim_evidence_guard` 主要把關文字/指令輸出證據；對於 **UI／Web 前端類任務的「可觀察檢查項 `C1..Cn` 拆解 + 截圖/錄屏/控制台日誌打包 + 多輪打回紀錄（`.acceptances/`）」**，開源的 `lobehub/acceptance`（`lh acceptance`）提供了一套標準化 CLI 與 `.acceptances/` 產物結構，極具參考價值。
- **查證註記（2026-11-19，T-20261119-03 唯讀檢閱）**：
  - `lobehub/acceptance`（commit `5e9115da`）只含技能文件與輔助腳本；做驗證、產生報告頁與上傳的 `lh` CLI 不在 repo 內，未查證。
  - repo 裡沒有 `C1..Cn` 的命名規定，檢查項識別碼是 `plan[].id` 自由字串；文章截圖的 `C1..C5` 原先推測是該次執行自取的識別碼（未查證）。2026-11-20 補看圖 29 後，這個推測要保留：同一組編號也出現在 LobeHub 任務頁，CLI 表頭直接叫 `C#`，較可能是產品端顯示的編號（仍未查證）。借鏡項目見 [`docs/lobehub-acceptance-eval.md`](../docs/lobehub-acceptance-eval.md)。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261119-03`**｜**[優先級：中]** 在沙盒唯讀檢閱 `lobehub/acceptance` 架構與 `.acceptances/` 多模態驗收規格
  - **目標範圍**：`C:\GitHub\_sandbox\lobehub-acceptance-audit` 與 `C:\GitHub\ai-inbox\docs\lobehub-acceptance-eval.md`
  - **執行步驟**：
    1. 僅以唯讀方式 clone `lobehub/acceptance` 至沙盒目錄（不執行安裝腳本或 `lh login`）。
    2. 檢閱其 `SKILL.md`、檢查項 `C1..Cn` 結構定義、`.acceptances/` 目錄產物格式及無頭瀏覽器截圖/錄屏採證流程。
    3. 評估如何將其「可觀察檢查清單 + 多輪打回沉澱」機制借鏡至本機 UI／端到端驗證協議，將完整評析寫入 `docs/lobehub-acceptance-eval.md`。
  - **驗收標準（DoD）**：產出 `docs/lobehub-acceptance-eval.md`，記錄 `lobehub/acceptance` 核心工作流、`.acceptances/` 格式與本機 `verification-protocol` 可借鏡項目，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-19
  - **實作紀錄 / 證據**：docs/lobehub-acceptance-eval.md；唯讀檢閱 commit 5e9115da，記錄八步工作流、.acceptances/ 目錄與 result.json 欄位、對 verification-protocol 的 10 項對照（5 項建議採用）；lh CLI 不在 repo 內標未查證，結論不安裝只借鏡規則
