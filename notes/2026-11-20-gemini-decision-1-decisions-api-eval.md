---
id: "2026-11-20-gemini-decision-1-decisions-api-eval"
title: "InfoQ 深度評析：Gemini Decision 1 與 Decisions API（$0.10/M 輸入、零輸出費、0.0250 ECE 低誤差路由模型）"
source_url: "https://www.infoq.cn/article/E7QKIMUz3h0G0IE5Paii"
source_platform: "InfoQ / Google Blog"
author: "李冬梅 (InfoQ) / Google DeepMind"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 4
source_replies: 0
source_reviewed_at: "2026-11-21"
status: done
cluster: 1
cluster_role: "決策路由專用模型"
short_title: "Gemini Decision 1"
tags:
  - gemini-decision-1
  - decisions-api
  - model-routing
  - calibration
  - multimodal
  - infoq
---

# InfoQ 深度評析：Gemini Decision 1 與 Decisions API（$0.10/M 輸入、零輸出費、0.0250 ECE 低誤差路由模型）

- **來源文章**：[谷歌发布首款决策模型 Gemini Decision 1（InfoQ）](https://www.infoq.cn/article/E7QKIMUz3h0G0IE5Paii)
- **官方原文**：[Google Blog — Gemini Decisions API](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/)
- **官方文件**：[Decisions API 文件](https://aistudio.google.com/docs/decisions-api)、[Gemini API 價格頁](https://aistudio.google.com/docs/pricing)（2026-11-21 查閱）
- **發布平台 / 作者**：`InfoQ` / `李冬梅`（`2026-11-12`；Google 官方部落格發表於 `2026-11-11`，作者 Min Choi、Felix Yu）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-18-gemini-4-carbon-argon-swarm-evals.md`](./2026-11-18-gemini-4-carbon-argon-swarm-evals.md)（Gemini 4 Carbon / Argon 基準與調價分析）
  - [`notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md`](./2026-11-19-anthropic-building-always-on-agents-blueprint.md)（Always-On Agents 事件過濾與路由）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型速查表）

---

## 1. 原始資料盤點（正文、4 張附圖與評論區）

- **正文核心與 SDK 核實**（官方文件寫明需 SDK 3.2 以上，`google-genai` 或 `@google/genai`）：
  - `gemini-decision-1` 為**非生成式（Non-generative）決策專用模型**，不逐字生成文本或 JSON，而是透過**單次前向傳播**對封閉選項集評分，直接回傳結構化結果、歸一化機率與置信度（`0～1`）。
  - **規格與計費**：支援最高 `256K` 多模態輸入（文本、JSON、圖片、音訊、影片、PDF）；單次請求可混合執行最多 `1,000` 題，包含 **`noul`**（Yes/No 二元判斷；`noul` 是官方 API 的型別名，不是筆誤）、**`choice`**（2–255 選項單選）與 **`score`**（有序等級評分，等級從 0 起算）；定價 **`$0.10 / 1M input tokens`、輸出 `$0`**（端到端延遲 `150–250 ms`）。
  - **Google 內部實際落地**：`Gemini Notebook` 用於即時模型路由（日常查詢延遲最高降 `40%`）；`Google Stitch` 的 rapid canvas 實驗功能用於秒級互動線框圖；`Google Labs CC` 用於 200+ Emoji 選擇；`Google Search` 用於建置 **`MCP` 工具安全檢測層**（識別對抗性行為）。以上都是 Google 自述，沒有公開量測方法。
- **圖片逐張盤點（文章內文共 4 張，2026-11-21 重審逐張開啟）**：
  - **圖 1**：Sundar Pichai 在 X 的發布貼文截圖，內含 Stitch rapid 實驗功能的 10 頁產品流程線框圖畫面（影片第 3 秒）。
  - **圖 2（API 資料流架構圖）**＆**圖 3（茶水間實拍示意圖）**：展示單次輸入圖片同時執行 `noul`（`has_spill` 0.95）、`choice`（`next_action` 為 `wipe_with_cloth`，0.98）、`score`（嚴重度 1.19/2.00，置信度 0.77）。兩張都是 Google 官方部落格的圖。
  - **圖 4（多模型基準測試與校準／成本對比表，與官方部落格的表格相同）**：
    - 9 項基準拿下 7 項第一：`JevBench` (**92.2%**)、`Amazon ESCI` (**58.7%**)、`New Yorker Caption` (**79.7%**)、`PubMedQA` (**79.8%**)、`Global-MMLU-Lite` (**86.0%**)、`MMAU` (**71.8%**)、`Video-MME` (**69.1%**)。MMAU 與 Video-MME 只有 Decision 1 與 Flash-Lite 兩個模型有分數。
    - **落後項（重要邊界）**：`Mind2Web Multimodal`（86.2% vs `TypeSafe Jev 1.14` 86.8%）與 Agent 工具調用關鍵指標 **`When2Call`（79.9% vs `TypeSafe Jev 1.14` 82.0%）** 仍由專用模型領先。
    - **校準誤差（Top-1 ECE，越低越好，7 項共用評測）**：`Gemini Decision 1` 僅 **`0.0250`**，優於 `TypeSafe Jev 1.14`（0.0494）、`GPT-6 Luna`（0.0721）與 `Gemini 3.5 Flash-Lite`（0.2104）。
    - **7 項共用評測總成本**：`$0.88`；`TypeSafe Jev 1.14` 為 `$0.68`（**四者最便宜**，表格也把它標成該列最佳）、`GPT-6 Luna` `$0.93`、Flash-Lite `$4.14`（Flash-Lite ÷ Decision 1 約 4.7 倍【推算】）。
  - 原稿另列「封面圖」與「圖 5：InfoQ AICon 大會廣告橫幅」，重審時文章內文只有上面 4 張圖；AICon 是頁尾的會議連結，不是作者上傳的圖，已刪除。
- **評論區**：`0` 則留言（2026-11-21 捲到頁尾，評論區顯示「暂无评论」）。
- **2026-11-21 重審更正與官方補充**：
  - 原稿寫圖 2 的題型是 `bool`，官方圖與文件都是 `noul`，已改正。原稿寫 `score` 是「2–255 有序等級」，官方文件只寫等級從 0 起算，255 的上限是 `choice` 的。
  - 原稿把 `TypeSafe Jev` 的成本寫成對照項，沒點出它比 Decision 1 便宜；Google 自己的表格顯示 Decision 1 贏的是 Flash-Lite，不是全部對手。
  - 官方部落格寫明 50–100 ms 模型運算與 150–250 ms 端到端延遲，是在 **16K tokens 以內**的情境量的；256K 上限附近的延遲沒有公開。
  - 官方文件的限制：只在 Gemini Developer API（`v1beta`）提供；**不支援 context caching、Batch、Flex、Priority**，重複送同樣的輸入每次都全額計費；是／否機率固定落在 0.01～0.99，門檻要設在這個範圍內；官方建議用自己流量的標註樣本訂門檻。
  - 價格頁：付費層輸入 $0.10／百萬 tokens、輸出不計費；AI Studio 另有免費層（免費層資料會用於改進產品）。

---

## 2. 對現有系統的啟發與落差評估

- **對模型路由與安全閘門的直接啟發**：
  - 傳統使用輕量生成模型（如 Flash-Lite / Haiku）做「是否需要喚醒 Worker」「該派給哪個模型」「這段外部內容有無 Prompt Injection」分類時，除了 JSON 解析脆弱之外，最大問題是**校準誤差高（Flash-Lite ECE 達 `0.2104`）**，導致無法放心用 `confidence` 做自動／人工分流門檻。
  - `Gemini Decision 1` 將 `Top-1 ECE` 壓到 `0.0250` 且輸出零費用（150–250ms），適合評估作為**多 Agent 路由（Router / Fast-Slow Path 事件過濾）與 MCP 安全對抗檢測層**的前置守門員。但 `When2Call`（判斷該不該呼叫工具）的正確率只有 79.9%，約每 5 題錯 1 題【推算】，而且輸給 `TypeSafe Jev 1.14`；ECE 與基準都是 Google 自己公布的數字【官方自述】，用來訂自動放行門檻前要先拿自己的標註樣本量一次（2026-11-21 重審改寫：原稿寫「保留 79.9% 的誤判餘裕」，把正確率寫成誤判率）。
- **與既有任務的銜接**：
  - 可併同 `T-20261118-01`（Carbon / Argon）將 `Gemini Decision 1` 的非生成式路由定位與校準數據納入 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261120-02`**｜**[優先級：低]** 將 `Gemini Decision 1`（Decisions API）前置路由／安全守門定位補入 `docs/model-burn-rate-routing-matrix.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（與 `T-20261118-01` 協同增補 Google 模型選型章節）
  - **執行步驟**：
    1. 在 `docs/model-burn-rate-routing-matrix.md` 記錄 `gemini-decision-1` 的計費（`$0.10/1M` 輸入、輸出 `$0`）、延遲（`150–250ms`）、支援題型（`noul` / `choice` / `score`）與 `Top-1 ECE = 0.0250` 置信度門檻優勢。
    2. 明確註記其在 `When2Call`（79.9%）與 `Mind2Web Multimodal`（86.2%）略遜於 `TypeSafe Jev 1.14` 的客觀邊界，以及作為「Router／Fast-Slow Path／MCP 安全前置檢測」的建議用法。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 已收錄 `Gemini Decision 1` 規格、校準數據與 `When2Call` 邊界，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-21
  - **實作紀錄 / 證據**：docs/model-burn-rate-routing-matrix.md 第 11.9、11.10 節收錄 Gemini Decision 1 規格（官方部落格與 Decisions API 文件，2026-11-21）、Top-1 ECE 0.0250（官方圖表）、When2Call 79.9% 輸 TypeSafe Jev 82.0% 的邊界與前置路由用法、限制；筆記重審 full
