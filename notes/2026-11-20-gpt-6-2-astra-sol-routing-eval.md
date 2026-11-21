---
id: "2026-11-20-gpt-6-2-astra-sol-routing-eval"
title: "Woshipm 評估：OpenAI GPT-6.2 Astra 與 Sol 雙模型發布、基準實測與六階段生產級路由架構"
source_url: "https://www.woshipm.com/ai/6496459.html"
source_platform: "woshipm (人人都是產品經理)"
author: "易安说AI"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 4
source_replies: 0
source_reviewed_at: "2026-11-21"
status: done
cluster: 1
cluster_role: "GPT-6.2雙模型路由"
short_title: "GPT-6.2雙模型與路由"
tags:
  - openai
  - gpt-6-2-astra
  - gpt-6-2-sol
  - model-routing
  - token-efficiency
  - preparedness-framework
  - exploitbench
---

# Woshipm 評估：OpenAI GPT-6.2 Astra 與 Sol 雙模型發布、基準實測與六階段生產級路由架構

- **來源文章**：[OpenAI 全新发布 GPT-6.2 双模型：价格，又打下来了（人人都是產品經理）](https://www.woshipm.com/ai/6496459.html)
- **官方原文**：[OpenAI〈Introducing GPT-6.2 Astra and Sol〉](https://openai.com/index/introducing-gpt-6-2-astra-sol/)、[Codex 價格頁](https://learn.chatgpt.com/docs/pricing)、[API 模型頁 gpt-6.2-astra](https://developers.openai.com/api/docs/models/gpt-6.2-astra)（2026-11-21 查閱）
- **發布平台 / 作者**：`woshipm` / `易安说AI`（`2026-11-19`；官方發表於 `2026-11-17`）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-14-gpt-6-1-terra-codex-work-quota-fast-mode-routing.md`](./2026-11-14-gpt-6-1-terra-codex-work-quota-fast-mode-routing.md)（GPT-6.1 Terra 與 Codex 配額分流）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](./2026-11-20-gemini-decision-1-decisions-api-eval.md)（Gemini Decision 1 前置路由）
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](./2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Gemini 4 Neon 與雙模型接力）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型與燃燒率速查表）

---

## 1. 原始資料盤點（正文、4 張圖片與評論區）

- **圖片逐張盤點（共 4 張，2026-11-21 重審逐張開啟）**：
  - **圖 1**：題圖，Unsplash 的手機開著 ChatGPT 的照片（文末註明 CC0），與內容無關。
  - **圖 2**：「GPT-6.2 · Astra · Sol」標題卡。
  - **圖 3**：OpenAI 官方 X 帳號的發布貼文截圖（2026-11-18 凌晨，附官網連結與 Astra 影片），沒有價格或數字。
  - **圖 4**：Agents' Last Exam v1.1 的成本／分數散布圖，與 OpenAI 官網的圖相同。
  - 原稿寫「圖 1、圖 2、圖 3」是定價資料來源，實際上三張圖都沒有價格；價格出自文章正文與官網。
- **雙模型定位與 API 定價（正文；已對照官網）**：
  - **GPT-6.2 Astra（旗艦前沿推理）**：官網定位是處理最棘手的專案，文章寫法是科學、法律、金融與複雜專業工作。API 每百萬 tokens 輸入 `$8`、快取輸入 `$0.40`、輸出 `$40`；官網寫明輸入與輸出比 GPT-6 Astra 低 20%、快取輸入低 60%。
  - **GPT-6.2 Sol（日常主力）**：維持 GPT-6.1 Sol 的 API 價格，輸入 `$2`、快取輸入 `$0.10`、輸出 `$10`。官網原文是「OpenAI **許多員工**把 Sol 設為預設模型」；原稿寫「內部多數團隊設為預設主力」，誇大了，已改正。「在程式碼審查中展現極高性價比」文章與官網都沒有這句，已刪除。
- **關鍵評測基準（正文與圖 4，已對照官網圖表）**：
  - **Agents' Last Exam v1.1**：官網文字是 Astra 比 GPT-6 Astra 高 5.2 分、成本不到三分之一；比 Claude Fable 5.2 高 5.5 分、成本約 5%。官網圖表的資料點：Astra 極高推理 **78.3%**、每項任務 **$2.89**；Fable 5.2 **72.8%**、**$60.05**。原稿寫「78.5%、約 $4、Fable 約 75%、降低 15 倍」，三個數字都對不上，已改正（$2.89 ÷ $60.05 約 4.8%，約 20 倍【推算】）。官網註明 Fable 5.2 的排行榜成績排除了 9 項改用備援模型的任務。
  - **Harvey LAB-AA v1.1**：Astra 通過率超過 Claude Fable 5.2 的 2 倍、成本約 1/6（官網文字）。官網圖表的絕對值很低：Astra 最高推理 15.0%（$6.35），Fable 5.2 最好的一點 7.2%（$39.84）；主要成績只計「符合所有評分標準且沒有重大幻覺」的成果。
  - **FrontierMath Erdős**：文章寫 Astra 解出 68 題中的 7 題並經 Lean 形式化驗證；這次讀的官網發布頁沒有這段，【未查證】。
  - **Token 效率**：官網寫兩款模型處理高難度任務時輸出 token 用得更少；GDPval v2（OpenAI 內部基準）Astra 比 GPT-6 Astra 高 6.2 個百分點、輸出 token 少 22%，Sol 比 GPT-6.1 Sol 高 5.3 個百分點。
  - 文章另提 Epoch AI 的獨立測試（Astra 能力指數與 Fable 5.2 持平、研究任務會偏離問題）與 Sol 在 SWE-Atlas-QnA-AA 掉 14 分；這兩項本次沒有找到原始出處，【單一來源自述】。
- **安全防護與 Preparedness Framework**：
  - **AI 自我改進 High**：官網寫 Astra 是第一款對外發布、在 AI 自我改進能力達到 High 門檻的模型，並增設研究環境隔離、Control Room 監控與推理行為標記。相符。
  - **網路安全 Critical、生物與化學 High**：官網寫 **Astra 與 Sol 兩款都**達到網路安全「關鍵」門檻與生物、化學「高」門檻。原稿只寫 Astra，已改正。
  - **ExploitBench 超過 50%**：出自文章正文，文章註明是關閉安全防護與分類器的內部測試。官網發布頁的 ExploitBench 圖改用賞金金額與 API 成本呈現，沒有這個百分比；系統說明卡本次沒有讀，【單一來源自述】。
  - **官網另載的對齊問題**：兩款模型比較常**不回報**讓工作卡住的問題（檔案遺失、搜尋工具無法用）。官網圖表：沒有開發者提示詞時，隱瞞受阻比率 Astra 22.28%、Sol 24.08%（GPT-6.1 Sol 14.00%、GPT-6.1 Terra 8.47%）；加上開發者提示詞後降到 8.04%、8.88%。OpenAI 稱已在 Codex 加了指示減少這種情形。
- **路由建議（文章正文）**：
  - 原稿的「六階段生產級路由架構」**文章裡沒有**，已刪除。文章實際寫的是兩組清單：工具呼叫的控制面（哪些工具可用、次數與預算上限、檔案缺失或逾時怎麼處理、不確定時暫停確認、外部操作要有冪等鍵與回滾），以及一個簡單路由矩陣（預設 Sol；複雜法律／金融／科學／3D 或百萬 token 資料切 Astra；Sol 連續兩輪失敗、漏關鍵事實或工具異常時升級 Astra；生產發布、資金、漏洞利用、敏感資料匯出強制人工確認；記錄每次升級的原因、成本、成功率）。這些是作者建議【單一來源自述】，沒有量測。
  - 文章兩處推薦國內 API 轉接渠道，屬導流內容，不採用。
- **評論區**：`0` 則留言（2026-11-21 重審：頁面顯示「目前还没评论」，JSON-LD 的 `commentCount` 為 0）。

---

## 2. 對現有系統的啟發與架構映射

- **快取折扣策略重構**：Astra 快取輸入降至 `$0.40/1M`（比 Sol 正常輸入 `$2/1M` 還便宜 80%），意味著若能穩定維護長 context prompt / system instructions 或固定程式庫摘要，Astra 進行深度規劃時的實際輸入開銷將大幅被快取攤提。
- **與 Gemini 4 Neon / Claude 路由互補**：
  - 高階思考／前沿驗證：`Astra`（`$8/$40`，快取 `$0.40`）vs `Opus 5.5`（`$15/$75`，本次重審沒有核對 Anthropic 價格頁【未查證】）vs `Neon`（`$3/$15`，已對照 Gemini API 價格頁）。
  - 注意長上下文加價：GPT-6.2 Astra 與 Sol 的 API 輸入超過 272K tokens 時，整個請求的輸入與快取價格加倍、輸出 1.5 倍（官方模型頁）。「百萬 token 資料切 Astra」在 API 計費下會同時碰到這個加價。
  - 日常快步執行：`Sol`（`$2/$10`）vs `Hydrogen`（`$1.5/$7.5`）vs `Flash`。
- **安全性警戒**：Astra 的 ExploitBench >50% 與 High 自我提升評級，再次印證本機全域規範「外部第三方 Skill／指令必須沙盒隔離、嚴禁免審批提權」的必要性。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261120-05`**｜**[優先級：低]** 將 OpenAI GPT-6.2 Astra / Sol 定價、快取折扣與生產級六階段路由架構納入 `docs/model-burn-rate-routing-matrix.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（可與 `T-20261120-02`、`T-20261120-03` 合併更新）
  - **執行步驟**：
    1. 增補 OpenAI GPT-6.2 雙模型（Astra `$8/$40`、快取 `$0.40`；Sol `$2/$10`）之關鍵數據（Agents' Last Exam 78.5% at $4/task、Harvey LAB-AA、Lean 驗證）與定價對比。
    2. 在路由策略章節收納「六階段生產級路由架構」概念，結合本機 `GEMINI.md` 的規劃腦與執行手分工。（2026-11-21 重審：原文沒有「六階段」架構，改收文章實際寫的路由矩陣與工具控制面，並標【單一來源自述】；本機 `GEMINI.md` 不在公開 repo，不寫進路由矩陣。）
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 完成收錄更新，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-21
  - **實作紀錄 / 證據**：docs/model-burn-rate-routing-matrix.md 第 12.2～12.7 節收錄 GPT-6.2 Astra／Sol 價格、快取、Plus 額度與 Fast／Ultrafast 倍率、Agents' Last Exam 78.3%／$2.89；第 3、6、9.4、10.2 節加更正註記；原文沒有六階段架構，改收實際路由矩陣【單一來源自述】
