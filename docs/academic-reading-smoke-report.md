# 學術論文 5W1H-CQR-KSU 實測報告：SWE-bench 基準測試論文解析

> 本報告使用 [`templates/academic-reading-prompt.md`](../templates/academic-reading-prompt.md) 所定義之標準架構，對真實世界經典 AI Agent 學術論文進行端到端實測，深入檢驗論文核心主張、實驗數據與推論邊界。  
> **依據版本**：依下列列出的實際讀取範圍整理，基於固定版本 [arXiv:2310.06770v3](https://arxiv.org/html/2310.06770v3)（2024 年 11 月更新版）。  
> 交付形式：以 `ai-inbox` 報告範本（`docs/academic-reading-smoke-report.md`）交付。

---

## 1. 論文來源與實際讀取範圍

- **論文標題**：*SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*
- **固定版本**：`arXiv:2310.06770v3 [cs.CL]`（11 Nov 2024）
- **官方來源**：
  - arXiv HTML 全文：`https://arxiv.org/html/2310.06770v3`
  - 官方代碼倉庫：`https://github.com/princeton-nlp/SWE-bench`
- **研究團隊**：Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan（Princeton Language and Intelligence, Princeton University; University of Chicago）
- **實際讀取範圍**：
  - Abstract 與 Section 1 (Introduction)
  - Section 2 (SWE-bench: 2.1 Benchmark Construction, 2.2 Task Formulation, 2.3 Features, 2.4 SWE-bench Lite)
  - Section 4 (Experimental Setup: 4.1 Retrieval-Based Approach, 4.3 Models)
  - Section 5 (Results)
  - Table 1 (Task instance attributes, Section 2.3)
  - Table 2 (Model resolve rates with BM25 across context lengths)
  - Table 5 (Main comparison on SWE-bench and SWE-bench Lite)
  - Table 7 (Pre/Post 2023 performance with Oracle retrieval)
  - Table 18 (Claude 2 Oracle retrieval, Appendix C.1)
  - Table 20 (GPT-4 evaluation subset results, Appendix C.3)
  - Appendix A.2 (Construction Process), C.1 (Results with "Oracle" Retrieval), C.3 (GPT-4 Evaluation Subset Results)

---

## 2. 第一層：5W1H 核心輪廓 (Triage)

- **Who（研究團隊）**：普林斯頓大學（Princeton University）語言與智能實驗室（PLI）與芝加哥大學學者，包含 ReAct 提出者 Shunyu Yao 等人。
- **What（研究標的）**：構建了基於真實軟體工程問題的評測基準 **SWE-bench**，包含自 12 個熱門開源 Python 倉庫（如 Django, SymPy, Pytest, Matplotlib, Sphinx, Scikit-learn, Astropy, Xarray 等）收集的 2,294 個真實 GitHub Issues 與其對應 PR 的驗收環境。
- **Why（問題背景）**：傳統代碼生成評測（如 HumanEval、MBPP）侷限於獨立、單一短函式的單元合成，無法有效評估語言模型在真實大型代碼庫中跨多檔案檢索、理解現有架構、定位故障與維持既有測試通過（Pass-to-Pass）之複合軟體工程能力。
- **How（方法與機制）**：
  - 提取真實 GitHub PR 中的 Issue 描述作為問題輸入，PR 代碼變更作為參考修復。
  - 提取 PR 新增的單元測試作為隱藏驗證集，利用 Docker 容器在隔離環境中執行自動化測試。
  - 定義嚴格評測標準：候選 Patch 必須使原本失敗的測試轉為通過（Fail-to-Pass），且既有測試必須全部維持通過（Pass-to-Pass）。
- **When & Where**：2023 年 10 月初版發表於 arXiv，獲選為 ICLR 2024 Oral 論文，v3 版本更新於 2024 年 11 月。
- **Key Metrics（核心基準表現）**：
  - 在標準 BM25 檢索設定下（Table 2 與 Table 5），前沿商用模型在完整 2,294 個 issue 上的解決率極低：**Claude 2 為 1.96%**（Table 2 報告 13k context 下為 1.96%，Table 5 報告 1.97% / Apply 率 43.07%）；**Claude 3 Opus 為 3.79%**；**GPT-4-turbo 為 1.31%**。
  - 若在提供黃金修改檔案清單的「Oracle」檢索理想設定下（Appendix C.1 / Table 18），Claude 2 的解決率可提升至 **4.80%**。
  - GPT-4 因 API 成本限制，在原論文中僅於 **25% 隨機子集 (574 instances)** 進行測試（Appendix C.3 / Table 20），在 Oracle 設定下測得 1.74% 解決率。

---

## 3. 第二層：CQR 論證與證據檢驗矩陣 (Critical Logic Auditing)

| 維度 | 內容摘要與具體論述 | 原文精準定位 (以 v3 為準) |
| :--- | :--- | :--- |
| **Claim (核心主張)** | 大型語言模型在面對真實世界 GitHub Issue 修復時，端到端自主解決能力仍處於極早期階段，僅能解決最簡單的局部問題。 | `Abstract`<br>`Section 1 (Introduction)`<br>`Section 5 (Results)` |
| **Evidence (實證數據)** | 1. **BM25 檢索設定 (Table 2 & Table 5)**：<br>   - Claude 2 (13k context)：**1.96%** (Table 2) / **1.97%** (Table 5)；<br>   - Claude 3 Opus：**3.79%**；<br>   - GPT-4-turbo：**1.31%**；<br>   - 開源微調模型 SWE-Llama 7b/13b 僅 **0.70%**。<br>2. **Oracle 檢索設定 (Table 7, Table 18 & Table 20)**：<br>   - Claude 2 達 **4.80%**；<br>   - GPT-4 在 25% 隨機評測子集（574 instances）上為 **1.74%**。 | `Table 2 (p.6)`<br>`Table 5 (p.7)`<br>`Table 7 (p.8)`<br>`Table 18 (Appendix C.1)`<br>`Table 20 (Appendix C.3)` |
| **Reasoning (推論邏輯)** | 模型無法解決主要受制於三項核心瓶頸：<br>1. **上下文檢索與故障定位 (Localization)**：在包含平均 3,010 個檔案、438K 行代碼的代碼庫中，檢索器無法精準命中真正需修改的檔案（BM25 下模型解決率顯著低於 Oracle）；<br>2. **回歸測試破壞 (Regression Breakage)**：模型生成的 Patch 常破壞既有單元測試（無法滿足 Pass-to-Pass）；<br>3. **缺少交互執行回饋**：單次預測生成 Patch 難以因應編譯與測試回饋。 | `Section 4.1`<br>`Section 5`<br>`Section 7 (Discussion)` |

---

### 可追溯性檢驗：作者明示邊界與讀者外推限制

在批判性研讀學術文獻時，需精確區分「**作者在論文中已清楚界定的實驗邊界**」與「**讀者或社群在外推引用時的適用限制**」：

1. **作者已明確揭露的範疇 (Explicitly Declared Scope)**：
   - 作者在論文標題雖然採用設問《*Can Language Models Resolve Real-World GitHub Issues?*》，但在摘要與 `Section 2 (p.2-4)` 中已明確界定資料來源：收集自 **12 個流行開源 Python 倉庫**（包含 Django, SymPy, Pytest 等 PyPI 套件）。
   - 資料收集機制（`Section 2.1 & Appendix A.2`）明確要求：PR 必須伴隨可驗證的測試變更（Fail-to-Pass 驗收條件），且能在 Docker 隔離環境中確定性重現。
   - 關於修改規模：依據 `Table 1 (p.4)`，SWE-bench 任務實例平均修改 1.7 個檔案（微平均 / Mean）、32.8 行代碼；但最大修改檔案數達 **31 個檔案**、最大代碼行數達 **5,888 行**（並非僅限少數檔案或短變更）。
2. **工程實踐中的外推限制 (Extrapolation Limitations)**：
   - **程式語言單一性**：基準測試完全集中於 Python 生態，缺乏靜態類型編譯語言（如 Rust、Go、C/C++）或典型前端全端生態（如 TypeScript/React、CSS 視覺版面）之驗證。
   - **驗收條件與現實偏差**：SWE-bench 高度依賴預先撰寫完備且確定性極高的單元測試套件。在真實商業開發中，大量 GitHub Issue 並無現成自動化測試可供驗證，依賴人工驗收或端到端整合環境。
   - **模型樣本分母注意**：在引用數據時，GPT-4 的 1.74% 係基於 25% 隨機子集（574 instances，見 Appendix C.3 / Table 20），不可直接將百分比乘以 2,294 題得出「解決 40 件」之斷言；而 Claude 2 的 4.80% 係 Oracle 檢索設定（Appendix C.1 / Table 18），其在常規 BM25 檢索下為 1.96%（Table 2）。
3. **研讀總結**：
   - 論文實證嚴謹且清楚交代了實驗參數與子集劃分。工程團隊在引用此論文評估 Coding Agent 時，應認識到其本質為「成熟開源 Python 倉庫中具備單元測試的演算法/邏輯層缺陷修復基準」，而不宜無邊界外推為代表所有領域的軟體工程全貌。

---

## 4. 第三層：KSU 知識資產轉化 (Knowledge Recycling)

- **S - Searchable（索引標籤）**：
  - `tags`: `swe-bench`, `code-eval`, `ai-agent`, `benchmark-methodology`, `cqr-analysis`, `unit-testing`
  - `id`: `2026-10-23-swe-bench-cqr-smoke-report`
- **R - Recyclable（可復用架構模式）**：
  - **Fail-to-Pass + Pass-to-Pass 雙向回歸測試契約**：在 Coding Agent 工作流中，要求實作前先設計出可重現問題的失敗測試（Fail-to-Pass），實作完成後確認全套測試全綠（Pass-to-Pass），防範模型產生破壞性副作用。
- **Usable（具體工程待辦事項）**：
  - **待辦項目**：在本地工具鏈（如 `tools/verify_video_storyboard.py` 或 `tools/verify_story_structure.py`）之單元測試中，持續貫徹「正向通過與邊界反例」雙重測試覆蓋，每次修改以 `python -m unittest discover -s tests` 確定性閉環。
  - **驗收標準（DoD）**：測試套件在修改前能捕捉違規案例（紅燈），修改後完全通過（綠燈），且現有既有測試零回歸。
