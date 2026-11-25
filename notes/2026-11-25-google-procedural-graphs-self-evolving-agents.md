---
id: "2026-11-25-google-procedural-graphs-self-evolving-agents"
title: "Google《Procedural Graphs (arXiv:2609.09153)》評析：不重訓權重的 `(procedure, relation, procedure)` 自演化執行圖譜、驗證守門與拒絕記憶"
source_url: "https://arxiv.org/abs/2609.09153"
source_platform: "arXiv (Google / Georgia Tech / Peking University)"
author: "Yuxing Lu, Yicheng Chen, Shanchan Wu, Sercan Ö. Arık"
analyzed_at: "2026-11-25"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-25"
source_review_note: "已核對使用者提供摘要並透過 search_web 查證原論文 arXiv:2609.09153（作者群、三元組圖譜架構、2-hop 局部導引與 EnterpriseArena 81.8% 工具呼叫降幅）及社群重實作 vikm2o/proceduralgraph；未下載全文 PDF 或執行第三方程式碼。"
status: pending
cluster: 1
cluster_role: "程序圖譜自我演化"
short_title: "Google程序圖譜PG評析"
tags:
  - procedural-graphs
  - self-evolving-agents
  - google-research
  - enterprise-arena
  - validation-gate
  - rejection-memory
---

# Google《Procedural Graphs (arXiv:2609.09153)》評析：不重訓權重的 `(procedure, relation, procedure)` 自演化執行圖譜、驗證守門與拒絕記憶

- **原論文**：[`arXiv:2609.09153`](https://arxiv.org/abs/2609.09153)（*Procedural Graphs: Self-Evolving Execution Structures for LLM Agents*，2026 年 9 月，作者 Yuxing Lu, Yicheng Chen, Shanchan Wu, Sercan Ö. Arık — Google、Georgia Tech、北京大學）
- **開源狀況**：作者尚未釋出官方倉庫；社群另有獨立 Python 重實作 [`vikm2o/proceduralgraph`](https://github.com/vikm2o/proceduralgraph)（僅作參考記錄，未執行）。
- **分析日期**：`2026-11-25`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md`](./2026-11-08-google-research-harness2-recursive-agent-harnessing.md)（Google Research `Harness²`：無標準答案雙層遞迴 Harness 優化）
  - [`docs/harness2-recursive-agent-harnessing-spec.md`](../docs/harness2-recursive-agent-harnessing-spec.md)（本庫自我演化 Harness 規格目標文件）

---

## 0. 原始資料盤點與查證

- **核心結構（Procedural Graphs, PG）**：
  - 類比知識圖譜用 `(entity, relation, entity)` 組織「是什麼」，PG 用 **`(procedure, relation, procedure)` 三元組**組織「該怎麼做」，節點與邊附帶 `guidance`、`condition` 與 `pitfalls`（避錯規則），作為模型權重之外可讀、可編輯的顯式控制層。
- **線上執行期導引（Online Guidance）**：
  - 每一步動態定位 Agent 當前所在節點，僅抽取局部子圖（典型為 **2-hop 鄰域**）翻譯為當下情境提示與避錯提醒，在不完全剝奪模型自主推理彈性的前提下抑制長程目標漂移與重複空轉。
- **離線自我演化閉環（Offline Self-Evolution）**：
  1. **成功／失敗軌跡對比**：Refiner LLM 在任務批次間比較成功與失敗執行軌跡，提出拓撲或屬性修訂（增刪改節點、邊與轉移條件）。
  2. **驗證集守門（Validation Gating）**：所有修改必須在保留的驗證集上實測，**僅保留提升或維持表現的修訂**。
  3. **拒絕記憶（Rejection Memory）**：明確記錄被驗證集退回的失敗修訂，避免未來演化迴圈重複提出相同的錯誤改法。
- **EnterpriseArena 實測數據（132 個月新創企業 CFO 長程模擬）**：
  - 依使用者摘要與論文檢索資料：Gemini 3.5 Flash 透過自我修正工作指南學會提前預測現金流耗盡時間並及早融資，模擬公司存活率由 **0% 提升至 85%（17/20 次）**；同時因減少無效循環，每月重複工具呼叫次數由 `17.23` 次降至 `3.08` 次（降幅 **81.8%**）。
- **已知代價**：執行期每次決策須額外查詢圖譜並呼叫導引模型，會增加單步 Token 與延遲開銷（須靠長程任務減少空轉來攤平）。

---

## 1. 與本專案現有架構的對照與啟發

1. **補足 `Harness²` 缺乏「驗證守門」與「拒絕記憶」的缺口**：
   - 本庫先前收錄的 [`Harness²` (`arXiv:2610.14224`)](./2026-11-08-google-research-harness2-recursive-agent-harnessing.md) 針對無標準答案的開放世界修改平鋪 Harness 模組，但在第三方實測（issue #201）中曾出現「七成任務改了設定卻量不到分數提升」的現象。
   - **Procedural Graphs** 提供了兩個可直接借鏡的工程防線：**Validation Gating（沒在驗證集變好或持平就回滾）**與 **Rejection Memory（把被拒改法寫入負向記憶避免重蹈覆轍）**，非常適合套用到本庫的規則／Skill 迭代流程。
2. **局部 2-hop 注入取代全量提示詞膨脹**：
   - 以狀態圖節點的 **2-hop 局部子圖**動態注入 `guidance / condition / pitfalls`，比把所有長篇規則一次性塞進 `system prompt` 更能控管上下文預算（對應 `audit_skills_context_budget.py` 精神）。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261125-04`**｜**[優先級：低]** 將 Google `Procedural Graphs`（`arXiv:2609.09153`）之「`(procedure, relation, procedure)` 2-hop 局部導引、Validation Gating 與 Rejection Memory」模式補入 `docs/harness2-recursive-agent-harnessing-spec.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\harness2-recursive-agent-harnessing-spec.md`（收錄於集群 1）
  - **執行步驟**：
    1. 在 `docs/harness2-recursive-agent-harnessing-spec.md` 新增「與 Procedural Graphs (`arXiv:2609.09153`) 的有驗證集對照模式」小節。
    2. 整理三項核心機制（2-hop 局部導引降低上下文膨脹、離線 Validation Gating 防回歸、Rejection Memory 防重複失敗修訂）與單步導引額外 Token 成本權衡，並註明不採用無驗證的盲目自我改寫。
  - **驗收標準（DoD）**：`docs/harness2-recursive-agent-harnessing-spec.md` 完成上述對照節補充，且 `python tools/verify_inbox.py` 驗證通過。
