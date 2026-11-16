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
cluster: "4"
cluster_role: "學術論文閱讀與視覺分割"
short_title: "5W1H / CQR / KSU"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 10
source_replies: 4
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

## 0. 原始資料盤點

> 2026-11-16 重審：貼文文字、10 張輪播圖、4 則留言都看過。

- **作者圖片**（10 張輪播，頁尾標「ACADEMIC READING SYSTEM」）：
  - 圖 1：封面，三個模板串成一條線——5W1H 快速掃讀（篩選文獻）→ CQR 批判閱讀（拆解主張）→ KSU 轉化輸出（整理筆記）。
  - 圖 2：「從頭讀到尾、被動吸收、讀完說不清」對比「先問問題、提取關鍵、轉成自己的輸出」。
  - 圖 3：模板一 5W1H 是完整六問：Who 誰寫的、What 研究什麼、When 何時發表、Where 發表在哪、Why 為何重要、How 如何做的。
  - 圖 4：5W1H 當漏斗用，依序看作者與機構、研究問題、發表時間與期刊、重要性與方法適配，篩出值得深挖的論文。
  - 圖 5：模板二 CQR 的三個字母是 **Claim（作者的核心主張）／Question（有哪些疑問或漏洞）／Relation（與我的研究有何關聯）**。
  - 圖 6：CQR 中文版：主張（擷取證據）→ 疑問（假設合理嗎、數據足夠嗎）→ 關聯（如何影響我的研究）。
  - 圖 7：模板三 KSU 的三個字母是 **Key Points（關鍵點）／Supporting Evidence（支撐證據）／Use Cases（應用情境）**。
  - 圖 8：KSU 流程：一篇論文 → 1–2 句總結 → 2–3 個證據 → 下一個應用情境；產出的筆記要「可搜尋、可引用、可發展」。
  - 圖 9：整條流程後面多一站「研究資料庫」（累積與應用，建立個人知識資產）。
  - 圖 10：四階收尾：找到值得讀的文獻 → 看見主張與漏洞 → 留下支撐證據 → 轉成自己的研究輸出。
- **作者留言補充**：1 則，只放 Substack 電子報連結（obsidianacademicnotamaking.substack.com），沒有補充框架內容。
- **網友留言重點**：3 則（`_wei_2025` 說方式不錯，另兩則是「Lm」「存」的收藏留言），沒有補充、反駁或實測。
- **對分析的影響**：
  - 原筆記只看貼文文字，把 CQR 自行解成「Claim／Evidence／Reasoning」並掛到 Toulmin 模型，把 KSU 解成「Searchable／Recyclable／Usable」。圖 5、圖 7 顯示作者的定義不是這樣，本次已把 1.2 節的圖與說明改回作者原意，並標明哪些是本 repo 自己的延伸。
  - 5W1H 原筆記只列四問，依圖 3 補上 When、Where。
  - 已完成任務 `T-20261017-03`、`T-20261017-04` 做出來的範本與提示詞沿用「Claim／Evidence／Reasoning」與「可搜尋／可回收／可應用」；這套本身可用，但不是作者的 CQR／KSU，名稱對不上原出處。任務狀態未動，是否改名或補上 Question／Relation、Use Cases 欄位由整合者決定。

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
       │ 5W1H (Who/What/When/Where/Why/How) │ ──> 快速過濾：掌握基本輪廓，判斷是否值得深入
       └──────────────┬────────────────┘
                      │ 值得深入精讀
                      ▼  【第 2 層：深驗證 (Verification)】
       ┌───────────────────────────────┐
       │ CQR (Claim / Question / Relation) │ ──> 批判閱讀：抓主張、提出疑問、連回自己的研究
       └──────────────┬────────────────┘
                      │ 提煉可落地洞見
                      ▼  【第 3 層：轉化回收 (Recycling)】
       ┌───────────────────────────────┐
       │ KSU (Key points / Supporting evidence / Use cases) │ ──> 寫成可搜尋、可引用、可發展的筆記
       └───────────────────────────────┘
```

1. **第一層：5W1H 快速篩選（Triage Phase）**
   - **目的**：在投入大量時間前，以 3~5 分鐘快速摸清全貌，決定是「存檔略過」還是「精讀」。
   - **維度**：
     - **Who**：誰做的？作者背景、機構、權威度。
     - **What**：具體做了什麼？（新模型、新演算法、新資料集、改進基準？）
     - **Why**：為什麼要做？解決領域內的什麼核心痛點或文獻空白？
     - **How**：如何完成的？關鍵架構與方法論。
     - **When／Where**（依作者圖 3 補上）：何時發表、發表在哪；作者圖 4 用它判斷文獻是否夠新、期刊是否有影響力。
2. **第二層：CQR 深入拆解論證（Deep-dive & Logic Auditing）**
   - **作者的定義（圖 5、圖 6）**：
     - **Claim（主張）**：作者的核心主張是什麼？擷取支持它的證據。
     - **Question（疑問）**：有哪些疑問或漏洞？假設合理嗎、數據足夠嗎？
     - **Relation（關聯）**：與我的研究有何關聯？它如何影響我的研究方向？
   - **本 repo 的延伸（不是作者原意）**：範本裡的「Claim／Evidence／Reasoning」是本 repo 參考 Toulmin 論證模型另外定的檢驗欄位，用來查證據能否推出主張（邏輯跳躍、混淆因果、過度泛化）。它對應作者的 Claim 與 Question 兩步，缺少 Relation。
3. **第三層：KSU 構建可回收研究資產（Knowledge Recycling）**
   - **目的**：閱讀筆記不能淪為死文檔，必須無縫接回自己的日常工作與專案中。
   - **作者的定義（圖 7、圖 8）**：
     - **Key Points（關鍵點）**：用自己的話寫 1–2 句總結，抓住核心發現。
     - **Supporting Evidence（支撐證據）**：留下 2–3 個關鍵數據、實驗或理論依據。
     - **Use Cases（應用情境）**：寫下這篇對自己研究的啟發，提出下一個研究問題或行動。
   - **筆記要達到的性質**：貼文文字說「可搜尋、可回收、可應用」，圖 8 寫「可搜尋、可引用、可發展」。這是筆記的品質要求，不是 KSU 三個字母的意思。
   - **本 repo 的對應**：Frontmatter 標籤與唯一 ID 讓筆記可搜尋；範本與提示詞可重複使用；Use Cases 對應本 repo 的**可驗收待辦事項（Action Items）**。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **`SanHsien/ai-inbox` 自身**：本專案的筆記結構對得上 KSU：摘要是 Key Points、CQR 區塊與證據是 Supporting Evidence、待辦事項是 Use Cases；tags／slug 則讓筆記可搜尋。
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
