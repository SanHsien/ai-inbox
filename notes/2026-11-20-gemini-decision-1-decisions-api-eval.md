---
id: "2026-11-20-gemini-decision-1-decisions-api-eval"
title: "InfoQ 深度評析：Gemini Decision 1 與 Decisions API（$0.10/M 輸入、零輸出費、0.0250 ECE 低誤差路由模型）"
source_url: "https://www.infoq.cn/article/E7QKIMUz3h0G0IE5Paii"
source_platform: "InfoQ / Google Blog"
author: "李冬梅 (InfoQ) / Google DeepMind"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 6
source_replies: 0
source_reviewed_at: "2026-11-20"
status: pending
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
- **發布平台 / 作者**：`InfoQ` / `李冬梅`（`2026-11-12`）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-11-18-gemini-4-carbon-argon-swarm-evals.md`](./2026-11-18-gemini-4-carbon-argon-swarm-evals.md)（Gemini 4 Carbon / Argon 基準與調價分析）
  - [`notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md`](./2026-11-19-anthropic-building-always-on-agents-blueprint.md)（Always-On Agents 事件過濾與路由）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型速查表）

---

## 1. 原始資料盤點（正文、6 張附圖與評論區）

- **正文核心與 SDK 核實（`google-genai >= 3.2`）**：
  - `gemini-decision-1` 為**非生成式（Non-generative）決策專用模型**，不逐字生成文本或 JSON，而是透過**單次前向傳播**對封閉選項集評分，直接回傳結構化結果、歸一化機率與置信度（`0～1`）。
  - **規格與計費**：支援最高 `256K` 多模態輸入（文本、JSON、圖片、音訊、影片、PDF）；單次請求可混合執行最多 `1,000` 題，包含 **`noul`**（Yes/No 二元判斷）、**`choice`**（2–255 選項單選）與 **`score`**（2–255 有序等級評分）；定價 **`$0.10 / 1M input tokens`、輸出 `$0`**（端到端延遲 `150–250 ms`）。
  - **Google 內部實際落地**：`Gemini Notebook` 用於即時模型路由（日常查詢延遲最高降 `40%`）；`Google Stitch Rapid` 用於秒級互動原型設計；`Google Labs CC` 用於 200+ Emoji 選擇；`Google Search` 用於建置 **`MCP` 工具安全檢測層**（識別對抗性行為）。
- **圖片逐張盤點（共 6 張：封面 1 張 + 正文 5 張，另含內嵌演示影片 1 段）**：
  - **封面圖＆圖 1**：Sundar Pichai 發布公告截圖＋`Stitch Rapid` 10 頁產品線框圖 3 秒生成演示。
  - **圖 2（API 資料流架構圖）**＆**圖 3（茶水間實拍示意圖）**：展示單次輸入圖片同時並行執行 `bool`（灑漏偵測 0.95）、`choice`（清理動作 `wipe_with_cloth` 0.98）、`score`（嚴重度 1.19/2.00，置信度 0.77）。
  - **圖 4（多模型基準測試與校準／成本對比表，重點轉錄）**：
    - 9 項基準拿下 7 項第一：`JevBench` (**92.2%**)、`Amazon ESCI` (**58.7%**)、`New Yorker Caption` (**79.7%**)、`PubMedQA` (**79.8%**)、`Global-MMLU-Lite` (**86.0%**)、`MMAU` (**71.8%**)、`Video-MME` (**69.1%**)。
    - **落後項（重要邊界）**：`Mind2Web Multimodal`（86.2% vs `TypeSafe Jev 1.14` 86.8%）與 Agent 工具調用關鍵指標 **`When2Call`（79.9% vs `TypeSafe Jev 1.14` 82.0%）** 仍由專用模型領先。
    - **校準誤差（Top-1 ECE，越低越好）**：`Gemini Decision 1` 僅 **`0.0250`**，大幅優於 `TypeSafe Jev 1.14`（0.0494）、`GPT-6 Luna`（0.0721）與 `Gemini 3.5 Flash-Lite`（0.2104）。
    - **7 項共用評測總成本**：`$0.88`（vs Flash-Lite `$4.14`，省約 4.7 倍；vs TypeSafe Jev `$0.68`）。
  - **圖 5**：InfoQ AICon 大會廣告橫幅。
- **評論區**：`0` 則留言（`· 暂无评论 ·`）。

---

## 2. 對現有系統的啟發與落差評估

- **對模型路由與安全閘門的直接啟發**：
  - 傳統使用輕量生成模型（如 Flash-Lite / Haiku）做「是否需要喚醒 Worker」「該派給哪個模型」「這段外部內容有無 Prompt Injection」分類時，除了 JSON 解析脆弱之外，最大問題是**校準誤差高（Flash-Lite ECE 達 `0.2104`）**，導致無法放心用 `confidence` 做自動／人工分流門檻。
  - `Gemini Decision 1` 將 `Top-1 ECE` 壓到 `0.0250` 且輸出零費用（150–250ms），非常適合作為**多 Agent 路由（Router / Fast-Slow Path 事件過濾）與 MCP 安全對抗檢測層**的前置守門員（惟在 `When2Call` 工具調用場景須保留 79.9% 的誤判餘裕）。
- **與既有任務的銜接**：
  - 可併同 `T-20261118-01`（Carbon / Argon）將 `Gemini Decision 1` 的非生成式路由定位與校準數據納入 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261120-02`**｜**[優先級：低]** 將 `Gemini Decision 1`（Decisions API）前置路由／安全守門定位補入 `docs/model-burn-rate-routing-matrix.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（與 `T-20261118-01` 協同增補 Google 模型選型章節）
  - **執行步驟**：
    1. 在 `docs/model-burn-rate-routing-matrix.md` 記錄 `gemini-decision-1` 的計費（`$0.10/1M` 輸入、輸出 `$0`）、延遲（`150–250ms`）、支援題型（`noul` / `choice` / `score`）與 `Top-1 ECE = 0.0250` 置信度門檻優勢。
    2. 明確註記其在 `When2Call`（79.9%）與 `Mind2Web Multimodal`（86.2%）略遜於 `TypeSafe Jev 1.14` 的客觀邊界，以及作為「Router／Fast-Slow Path／MCP 安全前置檢測」的建議用法。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 已收錄 `Gemini Decision 1` 規格、校準數據與 `When2Call` 邊界，且 `python tools/verify_inbox.py` 驗證通過。
