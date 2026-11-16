---
id: YYYY-MM-DD-<slug>
title: "<文章標題或主題摘要>"
source_url: "<原始連結，若為貼文截圖或純文字可填 N/A>"
source_platform: "<X / Threads / Reddit / GitHub / Blog / Paper / WeChat>"
author: "<作者名稱或帳號>"
analyzed_at: YYYY-MM-DD
analyzed_by: "<Agent 名稱，如 Antigravity / Claude Code / Codex>"
status: pending # pending | in-progress | done | archived
cluster: 1 # 知識圖譜集群：1 多 Agent 協同｜2 影音視覺與 Generative UI｜3 Agent 工具鏈｜4 研究與全端工程
cluster_role: "<這篇在集群裡的角色，例如 訊息傳輸、動效字典>"
short_title: "<知識圖譜顯示的短標題>"
source_review: full # full（文字、全部圖片、全部留言都看過）| partial（有沒看到的，另填 source_review_note）| unavailable（另填 source_review_note）
source_reviewed_at: YYYY-MM-DD # 原始資料（圖片、留言）看完的日期
source_images: 0 # 看過的作者圖片／影片截圖張數
source_replies: 0 # 讀過的留言數（含作者回覆）
tags:
  - agent-workflow
  - prompt-engineering
---

# <文章標題或主題摘要>

- **來源連結**：[<顯示名稱>](<URL>)
- **發布平台 / 作者**：`<Platform>` / `<Author>`
- **分析日期**：`YYYY-MM-DD`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**：（逐張寫重點：圖 1 …、圖 2 …；沒有圖寫「無」）
- **作者留言補充**：（作者在留言區放的連結、Prompt、勘誤）
- **網友留言重點**：（補充、反駁、出處更正、實測回報；沒有寫「無」）
- **對分析的影響**：（這些資料讓本篇結論或任務改了什麼）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：<作者、研究團隊或組織架構背景>
- **What（核心產出 / 做了什麼）**：<新模型 / 新框架 / 工具庫 / 資料集或改進基準>
- **Why（為解決什麼問題 / 痛點）**：<為解決領域內的什麼核心痛點或文獻空白>
- **How（核心架構與關鍵機制）**：
  - （具體實作方法、運作管線，必要時附 ASCII 流程圖）
- **When & Where（適用時機與場景）**：<在什麼場景、什麼條件下適用或被觸發>
- **Key Metrics / Numbers（關鍵指標與量化數據）**：<基準提升百分比、延遲、吞吐量、參數量等客觀數據，無數據則填無>

---

## 2. CQR 深入論證檢驗（論文 / 技術報告選填）

> 遇到包含明確實驗數據、基準測試（Benchmarks）或學術論文時，應拆解 CQR 檢驗推論鏈：
>
> **名稱出處**：CQR 出自王啟樺的學術閱讀框架，作者原版的三個字母是 **Claim（作者的核心主張）／Question（有哪些疑問或漏洞）／Relation（與我的研究有何關聯）**。下面的 Claim／Evidence／Reasoning 是**本 repo 的改編版**，參考 Toulmin 論證模型，專門檢查證據能不能推出主張；它涵蓋原版的 Claim 與 Question，原版的 Relation 由下一節「啟發與適用性評估」承接。依據見 [`notes/2026-10-17-academic-reading-framework.md`](../notes/2026-10-17-academic-reading-framework.md) 第 0 段（圖 5、圖 6）。

- **Claim（核心主張）**：<作者的主要發現、關鍵論點或性能宣稱>
- **Evidence（實驗數據 / 消融實驗）**：<作者拿出的具體實驗數據、Ablation Study 或對比基準（如 MMLU / HumanEval / 實測 TPS）>
- **Reasoning（推論邏輯與潛在局限）**：<證據是否足以支撐主張？是否存在資料集偏差、過度泛化、未控制變因或特定硬體限制？>

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - （指明這跟維護者的哪個 Repo、哪支 Skill、哪條全域規則或工作流有關）
- **落差與採納判斷**：
  - **值得採納的部分**：...
  - **不適用 / 需調整的部分**：...

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。
> 任務行格式必須完全照下方範例，否則總表讀不到、驗證會失敗。

- [ ] **`T-YYYYMMDD-01`**｜**[優先級：高/中/低]** <具體一句話任務標題>
  - **目標範圍**：`<Repo 名稱 / Skill 路徑 / 全域設定>`
  - **具體做法**：<明確寫出要改哪個檔案、新增什麼邏輯或腳本>
  - **驗收標準（DoD）**：<怎麼證明做完了？跑哪個測試或實際執行什麼指令驗證？>
  - **狀態**：🟡 進行中 *（認領時才加；完成後刪除此行）*
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
