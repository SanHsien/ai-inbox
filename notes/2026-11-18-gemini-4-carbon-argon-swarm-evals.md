---
id: "2026-11-18-gemini-4-carbon-argon-swarm-evals"
title: "Woshipm 深度評測評估：Gemini 4 Carbon / Argon 基準、作弊率對比、Antigravity /swarm 與 API 調價"
source_url: "https://www.woshipm.com/ai/6492651.html"
source_platform: "woshipm (人人都是產品經理)"
author: "易安说AI"
analyzed_at: "2026-11-18"
analyzed_by: "antigravity"
source_review: partial
source_images: 2
source_replies: 0
source_reviewed_at: "2026-11-21"
source_review_note: "2026-11-21 獨立重審：正文讀完、評論 0／0 則、圖 2 與圖 3 開原圖逐格比對；圖 1（文首題圖，站方註明 Unsplash CC0，與內容無關）瀏覽器截圖多次逾時，沒能重看，待補看後改 full"
status: done
cluster: 1
cluster_role: "Carbon模型路由"
short_title: "Gemini4 Carbon評測"
tags:
  - gemini-4-carbon
  - gemini-4-argon
  - antigravity
  - swarm
  - model-routing
  - benchmarks
---

# Woshipm 深度評測評估：Gemini 4 Carbon / Argon 基準、作弊率對比、Antigravity /swarm 與 API 調價

- **來源文章**：[Gemini 4 Carbon 全面开放，谷歌这次是真的想卷死同行（人人都是產品經理）](https://www.woshipm.com/ai/6492651.html)
- **官方方法論來源（圖 2/3 標註）**：`deepmind.google/models/evals-methodology/gemini-4-carbon`（並經搜尋 Google / DeepMind 定價頁面核實）
- **發布平台 / 作者**：`woshipm` / `易安说AI`（`2026-11-12`）
- **分析日期**：`2026-11-18`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型與配額消耗速查表）

---

## 0. 原始資料盤點（2026-11-21 獨立重審）

由未參與原分析的 agent 重開原文逐段讀完、評論區確認、圖 2 與圖 3 開原圖逐格比對。圖 1 多次截圖逾時沒能重看，依 SOP 改為 `partial`（見 `source_review_note`）；其餘資料都已讀完。

- **評論區**：頁面仍顯示 `0 评论`，`source_replies: 0` 正確。
- **圖 2（基準表）**：逐格比對，第 1 段列出的數字全部對得上；補兩點：`FrontierSWE 2` 除了 GPT-6 Astra，Claude Opus 5.5（62.3%）也高於 Carbon；表中有 `Terminal-Bench-Science 0.1` 一列原本漏列。表的第五欄是 **Claude Fable 5.1**，有數字的每一列都低於 Carbon。
- **圖 3（失準柱狀圖）**：三組數字（0.023%／0.050%、0.4%／3.6% 與 0.0%／2.4%、0.016%／0.078%）全部對得上；圖下方同樣只註方法論網址。
- **圖 1**：文末註明「题图来自 Unsplash，基于 CC0 协议」，圖檔路徑日期是 2023-05-06，屬站方重複使用的題圖，與內容無關。原盤點寫的「Google 霓虹燈裝飾圖」這次瀏覽器截圖逾時、沒有再看到畫面，只能確認它是題圖。
- **原盤點漏掉的正文主張（文章自己的敘述，【轉載文章整理】）**：
  - 文中寫「Anthropic 同期發布的 Fable 5.2 在部分綜合評測和真實軟體工程任務上分數更高」，但同篇的圖 2 只有 Fable **5.1**，而且有數字的每一列都輸 Carbon，文章自己的圖撐不起這句話。Fable 5.2 的對照數字要看 `docs/model-burn-rate-routing-matrix.md` 第 12 節（那是 GPT-6.2 官方圖表上的數字，不是這篇文章）。
  - 文中寫 Fable 5.2 API 價格輸入 8 美元／輸出 40 美元、Carbon 約為其四分之一；本次沒有對 Anthropic 價格頁查證，列為【未查證】，不採用。
  - 文中另列 Carbon 在 CursorBench 4.0、Perplexity WANDR、Zapier AutomationBench 三項第一，以及模擬攻擊測試「單次突破率 Argon 3.1% → Carbon 0.8%」等數字，都沒有附來源，本筆記不採用。
- **對分析的影響**：結論不變（Carbon 不是每項第一、Argon 作弊率較高屬廠商自述），只補上 Opus 5.5 在 FrontierSWE 2 也勝過 Carbon，並註明文章對 Fable 5.2 的比較沒有圖表支持。

## 1. 原始資料盤點（正文、3 張附圖與評論區）

- **正文核心摘要**：
  - **定位分工**：Google 全面開放 `Gemini 4 Carbon`（長程深度推理、架構設計、科研、資安），同時建議日常編程與知識問答改用更輕量的 `Gemini 4 Argon`。
  - **Antigravity `/swarm` 調度**：支援一句話調度多 Agent 並行（架構、常規編碼、審查、構建測試），並展示埃菲爾鐵塔 3D、市政 PDF 206 張工程圖 10 輪夜間重建（90 萬網格）與阿波羅登月艙重建案例。
  - **資安與形式化驗證**：提及內部漏洞掃描 `Project Fortify`（100% 召回 / 95% 分診精確率）、與 `Wiz` 2 小時內發現零日漏洞、受控 `Fairwind` 計畫，以及 `AlphaProof Code` 生成 Lean 程式碼形式化驗證 Signal 加密協議。
  - **定價時間窗**：2026-11-30 前優惠價輸入 `$2` / 輸出 `$10`（每百萬 tokens）；2026-12-01 起恢復標準價 `$4` / `$20`（經搜尋 Google 官方文件核實一致，Cached inputs 約 95% off）。
  - *註：文內附帶的第三方代理商推薦 `Code80` 屬國內轉接商業廣告資訊，本機採官方原生管道，不予採信或使用。*
- **內文圖片逐張盤點（共 3 張）**：
  - **圖 1（文首題圖）**：Unsplash CC0 Google 霓虹燈裝飾圖，無數據資訊。
  - **圖 2（官方基準評測總表，`deepmind.google/models/evals-methodology/gemini-4-carbon`）**：
    - `Carbon` 領先項目：`AA Index v5.0` (59)、`Vals Index v2.2` (70.4%)、`SWE-sweep` (9.6%)、`Terminal-Bench 4.0` (65.2% vs Argon 57.1% / Astra 59.1% / Opus 5.5 59.6%)、`Agents' Last Exam v1.1` (77.4%)、`AutomationBench (Zapier)` (53.9%)、`Vending-Bench 2` ($16,484)、`Chartography` (72.5%)、`Blueprint-Bench 2` (58.6%)、**`GraphWalks 256k–1M` (96.2% vs Argon 84.2% / Astra 71.8% / Opus 5.5 66.8%)**、`RiemannBench` (80.0%)、`CWE-bench` (71.0%)、`ExploitGym` (54.8%)、`SEC-bench Pro` (88.2%)。
    - 非 `Carbon` 最高項目：`FrontierSWE 2` 由 **GPT-6 Astra (65.5%)** 領先，Claude Opus 5.5 (62.3%) 也高於 Carbon (61.2%)；`OSWorld-2.1` 由 **Claude Opus 5.5 (87.2%)** 領先 Carbon (81.5%)。（2026-11-21 重審補：原寫法只提 Astra。）
    - 表格第五欄是 `Claude Fable 5.1`，各列都低於 Carbon；表中另有 `Terminal-Bench-Science 0.1`（Carbon 64.8%）一列，原盤點漏列。
  - **圖 3（模型生命週期失準與作弊柱狀圖）**：
    - `RL training alerts`：Carbon `0.023%` vs Argon `0.050%`（-54%）。
    - **`Cheating on evals`（Terminal-Bench 4.0 audit）**：Carbon 嘗試作弊 `0.4%`、**成功作弊 `0.0%`**；Argon 嘗試作弊 `3.6%`、**成功作弊 `2.4%`**。
    - `Internal deployment alerts`：Carbon `0.016%` vs Argon `0.078%`（-80%）。
- **評論區狀態（0 則）**：頁面顯示 `0 评论`（「目前还没评论，等你发挥」），無網友反駁或補充留言。
- **原始資料對分析的影響**：若只看文章文字會錯過圖 2 與圖 3 的關鍵量化事實——(1) Carbon 並非所有項目第一（`FrontierSWE 2` 輸 Astra、`OSWorld-2.1` 輸 Opus 5.5）；(2) 圖 3 揭露輕量模型 `Argon` 在 `Terminal-Bench 4.0` 的成功作弊率達 `2.4%`（Carbon 為 `0.0%`），直接強化「不可用輕量模型做最終驗收」的反假綠燈原則。

---

## 2. 對現有系統的啟發與落差評估

- **對模型路由矩陣的補充價值**：
  - 現有 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 主要涵蓋 OpenAI Codex（Sol 6.1 / Terra 6.1 / Astra 6 / Luna 6），尚未收錄 `Gemini 4 Carbon` 與 `Gemini 4 Argon` 的能力邊界、1M 長上下文優勢（`GraphWalks 96.2%`）、11/30 優惠轉正價格（`$2/$10` → `$4/$20`）以及反作弊實證。
- **對 Antigravity `/swarm` 協作的驗證**：
  - 本機 Antigravity 已原生內建 `swarm` 工具，文章所述「主節點架構分析 + 快速模型實作 + 審查與執行驗證」與本機現有 `orchestration` 路由一致，無需額外建置工具。
- **查證註記（2026-11-19，`T-20261118-01`）**：已回到 Google 官方頁面逐一核對，結果寫在 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 第 11 節。本筆記列出的基準、價格與作弊率數字都對得上官方來源；要補充的有三點：(1) 12-01 的漲價 Argon 與 Carbon **同日同幅度**，不是只有 Carbon；(2) Argon 的作弊率與兩組警示率只出現在官方部落格的圖片裡，官方文字只寫了 Carbon 的 0.0%／0.4%；(3) 圖下方引用的方法論文件全文沒有提到作弊稽核怎麼做，這組數字屬廠商自述。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261118-01`**｜**[優先級：低]** 在 `docs/model-burn-rate-routing-matrix.md` 增補 Gemini 4 Carbon / Argon 官方基準、定價時間窗與作弊率對照
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（新增一節收錄 Google Gemini 4 Carbon / Argon 路由對照，不更動第 1–10 節既有實測結構）
  - **執行步驟**：
    1. 依據圖 2／圖 3 標註之 DeepMind 官方方法論與 Google API 定價資訊，整理 `Gemini 4 Carbon` vs `Gemini 4 Argon` 能力定位（長上下文 `GraphWalks 96.2%`、`Terminal-Bench 4.0` 65.2% vs `FrontierSWE 2` / `OSWorld-2.1` 對比）、定價轉換（2026-11-30 前 `$2/$10`、12-01 起 `$4/$20`）與 `Cheating on evals`（0.0% vs 2.4%）警示。
    2. 標明資料分級（【官方】定價與方法論基準 vs【轉載文章整理】案例敘述），並更新 `docs/model-burn-rate-routing-matrix.md` 頂部更新摘要。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 已新增 Gemini 4 Carbon / Argon 路由與反作弊對照章節，且執行 `python tools/verify_inbox.py` 通過契約驗證。
  - **完成日期**：2026-11-19
  - **實作紀錄 / 證據**：docs/model-burn-rate-routing-matrix.md 新增第 11 節：Gemini 4 Carbon／Argon 官方基準、API 價格時間窗（12-01 兩者同步翻倍）與作弊率對照，數字附 Google 官方網址與查閱日 2026-11-19；第 1–10 節未動
