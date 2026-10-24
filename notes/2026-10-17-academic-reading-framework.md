---
id: 2026-10-17-academic-reading-framework
title: "策略性學術閱讀與知識管理三層框架：5W1H 篩選、CQR 論證拆解與 KSU 筆記回收"
source_url: "https://www.threads.net/@chihua.wang.3/post/DejwczGEQvA"
source_platform: "Threads"
author: "王啟樺 (@chihua.wang.3)"
author_background: "Purdue 商學院博士後研究員、台大數學系，專注學術力、生產力與知識管理"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: 4
cluster_role: "閱讀框架"
short_title: "5W1H / CQR / KSU"
tags:
  - academic-reading
  - knowledge-management
  - research-methodology
  - prompt-engineering
  - note-taking
---

# 策略性學術閱讀與知識管理三層框架：5W1H 篩選、CQR 論證拆解與 KSU 筆記回收

- **來源連結**：[Threads @chihua.wang.3 貼文](https://www.threads.net/@chihua.wang.3/post/DejwczGEQvA)
- **發布平台 / 作者**：`Threads` / `王啟樺 (@chihua.wang.3)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要與理論溯源

### 1.1 核心主張
- **策略性閱讀的核心原則**：「學術閱讀不必每篇都從頭讀到尾，先選對模板，才能把時間用在真正需要深入的地方。」
- 策略性閱讀不是「少讀偷懶」，而是**分層過濾**，讓每次閱讀都能產出具體、可回溯、高槓桿的研究與工程價值。

### 1.2 三層架構（5W1H -> CQR -> KSU）深度拆解

```text
[海量論文 / 技術文獻 / 開源報告]
                   │
                   ▼  【第 1 層：淺篩選 (Triage)】
       ┌───────────────────────────────┐
       │ 5W1H (Who / What / Why / How) │  ──> 快速過濾：掌握基本輪廓，判斷是否值得深入
       └──────────────┬────────────────┘
                      │ 值得深入精讀
                      ▼  【第 2 層：深驗證 (Verification)】
       ┌───────────────────────────────┐
       │ CQR (Claim / Evidence / Reas) │  ──> 深度論證拆解：檢查主張、證據與推理是否站得住腳
       └──────────────┬────────────────┘
                      │ 提煉可落地洞見
                      ▼  【第 3 層：轉化回收 (Recycling)】
       ┌───────────────────────────────┐
       │ KSU (Searchable / Recyclable) │  ──> 沉澱為可搜尋、可回收、可應用的資產與待辦
       └───────────────────────────────┘
```

1. **第一層：5W1H 快速篩選（Triage Phase）**
   - **目的**：在投入大量時間前，以 3~5 分鐘快速摸清全貌，決定是「存檔略過」還是「精讀」。
   - **維度**：
     - **Who**：誰做的？作者背景、機構、權威度。
     - **What**：具體做了什麼？（新模型、新演算法、新資料集、改進基準？）
     - **Why**：為什麼要做？解決領域內的什麼核心痛點或文獻空白？
     - **How**：如何完成的？關鍵架構與方法論。
2. **第二層：CQR 深入拆解論證（Deep-dive & Logic Auditing）**
   - **理論原型**：學術界經典圖爾敏論證模型（Toulmin Model of Argument）的現代簡化版（Claim - Evidence - Reasoning，常見於頂會評審與批判性閱讀）。
   - **維度**：
     - **Claim（主張 / 核心論點）**：作者的主要發現或斷言是什麼？
     - **Evidence / Quote（證據 / 數據）**：作者拿出什麼實驗、消融測試（Ablation study）或基準數據支持？
     - **Reasoning（推理鏈 / 邏輯橋樑）**：證據如何有效推導出主張？是否存在邏輯跳躍、混淆因果、過度泛化或未受控的變因？
3. **第三層：KSU 構建可回收研究資產（Knowledge Recycling）**
   - **目的**：閱讀筆記不能淪為死文檔，必須無縫接回自己的日常工作與專案中。
   - **三大支柱**：
     - **Searchable（可搜尋）**：具備標準 Frontmatter 標籤、唯一 ID、關鍵字，利於全文檢索（如 ripgrep / XERJ / Obsidian）。
     - **Recyclable（可回收）**：提煉成模組化的組件、Prompts、設計模式或通用原則，能在未來其他專案中重複調用。
     - **Usable（可應用）**：直接轉化為具體的**可驗收待辦事項（Action Items / Tickets）**，驅動實作改動。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **`SanHsien/ai-inbox` 自身**：本專案建立的 `ai-inbox` 架構本質上就是 KSU（Searchable: tags/slug, Recyclable: 範本模式, Usable: 轉化為 README 待辦）。
  - **學術與文獻調研 Skills**：`literature-search-arxiv`、`literature-search-openalex`、`first-principles` 與 `verification-protocol`。
  - **AI 文章/論文分析範本**：目前 `templates/article-analysis.md` 僅有「摘要 + 啟發 + 待辦」，若讀者丟進來的是論文或評測文章，缺乏嚴密的 CQR（論證與證據核驗）區塊，容易只看宣傳效果而漏看瑕疵。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **升級 `article-analysis.md` 範本**：將 CQR（主張、證據、推理邏輯檢驗）正式融入分析範本中，當分析包含數據支撐的論文或技術報告時，強制 Agent 檢查其推論鏈。
    2. **打造學術閱讀 Prompt / 技能規範**：讓各 Agent 在處理 ArXiv 論文或深度技術長文時，依循「5W1H 快速初篩 -> CQR 嚴謹論證檢驗 -> KSU 落地待辦」標準化管線執行。
  - **不適用 / 需調整的部分**：
    - 一般社群閒聊或短動態不強制跑完整的 CQR 矩陣，避免過度複雜化（Over-engineering）。可設置「簡短模式（5W1H+KSU）」與「深度模式（完整 CQR）」。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-03`**｜**[優先級：高]** 升級 `templates/article-analysis.md`，納入 5W1H 初篩與 CQR 論證拆解模組
  - **目標範圍**：`C:\GitHub\ai-inbox\templates\article-analysis.md`
  - **完成日期**：2026-10-23
  - **具體實作步驟**：
    1. 檢視現有 `templates/article-analysis.md`，保留現有 YAML frontmatter 與 Action Items 區塊。
    2. 在「1. 核心內容摘要」中，標準化為 **5W1H 結構**（Who, What, Why, How, Key Metrics）。
    3. 新增「**CQR 論證檢驗矩陣**」選填區塊：包含 `Claim（核心主張）`、`Evidence（實驗數據/消融證據）`、`Reasoning（推論邏輯與潛在盲點/局限性）`。
    4. 在 `AGENTS.md` 中補充指引：遇到有明確實證數據或論文發表的 AI 文章時，主動填寫 CQR 區塊。
  - **驗收標準（DoD）**：範本修改完成，結構清晰，且語法符合 Markdown 與 Git 標準，不破壞既有欄位相容性。
  - **實作紀錄 / 證據**：升級 `templates/article-analysis.md` 納入 5W1H 初篩與 CQR 論證檢驗矩陣，更新 `AGENTS.md` 流程 A 準則，`python tools/verify_inbox.py` 驗證通過。

- [x] **`T-20261017-04`**｜**[優先級：中]** 評估設計 `academic-reading` 或將 5W1H-CQR-KSU 整合至文獻調研工作流
  - **完成日期**：2026-10-23
  - **目標範圍**：`~\.gemini\config\skills\` 或調研 Prompt
  - **具體實作步驟**：
    1. 檢閱現有學術檢索技能（如 `literature-search-arxiv`、`literature-search-openalex`）。
    2. 設計一段專用 System Prompt 或 Skill 規則：當使用者要求「讀論文」、「總結論文」或「評估技術報告」時，強制套用此三層過濾矩陣。
    3. 實測一篇 arXiv AI Agent 論文（例如 SWE-bench 相關論文），輸出測試報告並比對其結構化深度。
  - **驗收標準（DoD）**：產出測試輸出並驗證 CQR 能有效揪出論文聲稱（Claim）與實際實驗（Evidence）之間的落差。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `templates/academic-reading-prompt.md` 與實測報告 `docs/academic-reading-smoke-report.md`，實測真實 arXiv 論文 SWE-bench (arXiv:2310.06770)，端到端產出 5W1H、CQR 論證檢驗（精確定位 Section 3.1 與 Table 1/3 指出宣稱適用度與覆蓋範圍落差）與 KSU 知識資產轉化。
