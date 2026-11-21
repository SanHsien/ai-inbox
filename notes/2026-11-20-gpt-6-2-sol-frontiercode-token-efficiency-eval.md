---
id: "2026-11-20-gpt-6-2-sol-frontiercode-token-efficiency-eval"
title: "Woshipm 評估：GPT-6.2 Sol 實測基準（FrontierCode 43.8% 比肩 Astra、GDPval 3.3萬 Token 高效壓縮）與工位路由實踐"
source_url: "https://www.woshipm.com/ai/6496545.html"
source_platform: "woshipm (人人都是產品經理)"
author: "易安说AI"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 3
source_replies: 0
source_reviewed_at: "2026-11-21"
status: done
cluster: 1
cluster_role: "Sol高性價比路由"
short_title: "Sol基準與Token效率"
tags:
  - openai
  - gpt-6-2-sol
  - gpt-6-2-astra
  - frontiercode
  - token-efficiency
  - gdpval-v2
  - model-routing
---

# Woshipm 評估：GPT-6.2 Sol 實測基準（FrontierCode 43.8% 比肩 Astra、GDPval 3.3萬 Token 高效壓縮）與工位路由實踐

- **來源文章**：[GPT 像极了“五条人”：刚想淘汰它，6.2-Sol 又杀回我的主力工位了（人人都是產品經理）](https://www.woshipm.com/ai/6496545.html)
- **官方原文**：[OpenAI〈Introducing GPT-6.2 Astra and Sol〉](https://openai.com/index/introducing-gpt-6-2-astra-sol/)（圖表資料點取自頁面圖表的無障礙標籤）、[API 模型頁 gpt-6.2-sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol)、[Codex 價格頁](https://learn.chatgpt.com/docs/pricing)（2026-11-21 查閱）
- **發布平台 / 作者**：`woshipm` / `易安说AI`（`2026-11-19`）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-20-gpt-6-2-astra-sol-routing-eval.md`](./2026-11-20-gpt-6-2-astra-sol-routing-eval.md)（GPT-6.2 雙模型定價與六階段架構）
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](./2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Gemini 4 Neon vs Sol 基準與雙模型協同）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型與燃燒率速查表）

---

## 1. 原始資料盤點（正文、3 張圖片與評論區）

- **關鍵基準實測數據**：
  - **Cognition FrontierCode 2.0（真實開源程式碼庫測試）**：
    - `GPT-6.2 Astra`：得分 **44.2%**，單任務成本約 **$5.97**。
    - `GPT-6.2 Sol`：得分 **43.8%**，單任務成本約 **$1.29**。
    - **性價比落差**：兩者得分僅差距 0.4 個百分點，但 Sol 的單任務成本不到 Astra 的五分之一（成本降低 78%）。
  - **Agents' Last Exam v1.1（多步驟專業代理測試）**：
    - Sol 得分 **73.0%**（單題約 **$1.32**），略高於 Claude Fable 5.2（72.8%）與 Claude Opus 5.5（71.6%）。
  - **Token 輸出效率（GDPval v2）**：
    - 在相同設計、金融與程式碼任務中，Claude Fable 5.2 平均輸出 22.2 萬 Token、Claude Opus 5.5 輸出 19.1 萬 Token。
    - **GPT-6.2 Sol 僅輸出約 3.3 萬 Token**（Xhigh 檔位約 1.88 萬 Token），達成更高成績的同時，Token 輸出量壓縮達 **6 至 10 倍**。
  - **前端審美與 3D 生成（AA-3D 雙盲榜）**：
    - Artificial Analysis 評測中，Sol 升至 **1259 分**（超越 Claude Opus 5.5 的 1202 分），Astra 達 **1318 分**。
    - Higgsfield 內部測試顯示複雜 3D 場景一次通過率達 73%。
- **2026-11-21 重審：逐項對照官網**（官網數字取自 OpenAI 發布頁的文字與圖表資料點）：
  - **FrontierCode 2.0**：官網文字是「兩款都用最高推理強度，Sol 與 Astra 相差不超過 0.5 分，成本約五分之一」；圖表資料點 Astra 44.2%／$5.97、Sol 43.8%／$1.29，與上面相符。「成本降低 78%」是 $1.29 ÷ $5.97 的【推算】。同一張圖上 Claude Fable 5.2 最高 49.1%（$14.19），比兩款 GPT-6.2 都高，原稿沒提。
  - **Agents' Last Exam v1.1**：Sol 最高推理 73.0%／$1.32、Fable 5.2 72.8%／$60.05、Opus 5.5 71.6%／$17.57，相符（官網圖表）。
  - **GDPval v2**：是 **OpenAI 內部基準**，原稿沒寫。圖表各推理強度的輸出 token 與分數：Sol 最高 33,428／46.9%、極高 18,790／45.0%；Fable 5.2 最高 222,344／44.8%；Opus 5.5 最高 191,241／43.5%。原稿數字相符。「壓縮 6 至 10 倍」不是官網說法：同為最高推理是 5.7～6.7 倍，拿 Sol 極高對 Claude 最高是 10.2～11.8 倍【推算】。圖表沒有說明 token 數是每任務平均還是總數。
  - **AA-3D**：官網寫 Astra 1,318 第一、Claude Fable 5.2 1,271 第二、Sol 1,259。原稿的「Opus 5.5 1,202」只在文章裡，官網沒有【單一來源自述】；文章用 Opus 對照，沒提排在 Sol 前面的 Fable 5.2。
  - **Higgsfield 73%**：官網是 Higgsfield 執行長對 **GPT-6.2 Astra** 的評語（內部 3D 生成測試 73% 一次達標，GPT-6 Astra 至少要 3 次），**不是 Sol**；原稿放在 Sol 段落下容易誤讀，已註明。
  - **Ultrafast**：文章寫 Pro 方案的 Sol 支援 Ultrafast、速度可達標準的 4.5 倍。官網寫 Pro 200 首次開放 Ultrafast、第一個支援的是 Sol，Pro 500 兩款都能用；「4.5 倍速度」本次沒有在官網找到【未查證】。Codex 價格頁寫 Ultrafast 對內含額度按標準模式的 6 倍扣。
  - **路由門檻**：「單倉庫、少於 20 個檔案、預計 10 分鐘內」是作者舉的策略示例，文章沒有量測依據【單一來源自述】。
  - 文章兩處推薦國內 API 轉接渠道，屬導流內容，不採用。
- **工位路由實施規則**：
  - **默認 Sol**：單倉庫、少於 20 個檔案、預估 10 分鐘內完成、日常功能迭代、常規代碼修復與規劃初稿。
  - **強制切換 Astra**：跨倉庫／跨系統重構、百萬級 Token 上下文、複雜財務／數學建模、多次失敗後的深度推理與復原。
  - **生產安全底線**：涉及生產發布、外部郵件寄送與資金操作，必須保留人工確認（Human-in-the-loop）。
  - **單位有效產出指標**：評測不應只看榜單最高分，應綜合衡量「完成任務所需 Token 數」、「無效過程比例」、「錯誤定位準確率」與「交付耗時」。
- **文章圖片與評論區盤點**：
  - 圖片共 3 張（2026-11-21 重審逐張開啟）：圖 1 是「GPT-6.2 · Astra · Sol」標題卡；圖 2 是 Artificial Analysis Intelligence Index v5.0.1 長條圖，作者加了標註（Astra 62 分全球第 2、Sol 57 分第 5、Sol 單任務 $1.01、「成本為 Opus 的 1/10」），第一名是 Claude Fable 5.2（66 分）；圖 3 是 FrontierCode 2.0 與 Agents' Last Exam v1.1 兩張散布圖，作者加了 Sol 的標註框。原稿寫第 3 張是「3D 原型展示」，實際沒有 3D 原型圖，已改正；作者的「1/10」標註是作者自己的比較，官網沒有這個說法。
  - 評論區：`0` 則留言（2026-11-21 重審：頁面顯示「目前还没评论」，JSON-LD 記錄 `commentCount: 0`）。

---

## 2. 對現有系統的啟發與架構映射

- **Token 輸出壓縮的連鎖效益**：Sol 的 3.3 萬 vs Claude 19-22 萬 Token 輸出，不僅是 API 費用節省，更直接減少了對話 Context Window 膨脹速度、終端轉錄負擔以及下游解析延遲。
- **避免「榜單幻覺」的量化邊界**：文章給出了明確的數值分水嶺（`<20` 檔案、單倉庫、中短任務走 Sol；跨倉庫、百萬上下文走 Astra），這與本機全域協作規範「先調研再實作、避免昂貴模型乾燒」的工程理念完全契合。
- **前端生成與驗收分離**：即便模型在 3D 與前端排版評分提高，仍不可跳過響應式、可訪問性（a11y）與功能驗收，與本機 `verification-protocol` 要求一致。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261120-06`**｜**[優先級：低]** 將 GPT-6.2 Sol 的 Token Efficiency 壓縮比與 FrontierCode / AA-3D 量化指標納入 `docs/model-burn-rate-routing-matrix.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（可與 `T-20261120-05` 協同編修）
  - **執行步驟**：
    1. 記錄 FrontierCode 2.0 實測差異（Sol 43.8% @ $1.29 vs Astra 44.2% @ $5.97，僅差 0.4% 成本少 78%）。
    2. 納入 GDPval v2 之 Token Efficiency 指標（Sol 3.3 萬 Token vs Claude 19-22 萬 Token 壓縮比）。
    3. 增列以「檔案數 <20、單倉庫、任務時長 <10 分鐘」作為 Sol 預設工位的具體量化判斷標準。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 收納上述量化標準，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-21
  - **實作紀錄 / 證據**：docs/model-burn-rate-routing-matrix.md 第 12.3、12.4、12.6 節收錄 FrontierCode 2.0（官方圖表）、GDPval v2 輸出 token 對照（OpenAI 內部基準，倍數為推算）、AA-3D 分數、少於 20 檔門檻【單一來源自述】
