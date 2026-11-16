---
id: 2026-10-17-moonlight-bilingual-paper-reader
title: "AI 學術論文雙語閱讀：開源 PaperRead 雙欄對照、公式保護與 MinerU/Zotero/Moonlight 對照"
source_url: "https://www.threads.com/@jokdooaa/post/Dejc_d5GWh_"
source_platform: "Threads"
author: "jokdooaa (@jokdooaa)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: "4"
cluster_role: "學術論文閱讀與視覺分割"
short_title: "PaperRead 論文雙語對照"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "貼文顯示 104 則回覆，未登入只讀到 10／104 則；圖看了 3／3 張；source_replies 的 15 含 repo 的 5 則 issue"
source_images: 3
source_replies: 15
tags:
  - paper-reading
  - ai-tools
  - bilingual-translation
  - academic-workflow
  - pdf-parsing
---

# AI 學術論文雙語閱讀：開源 PaperRead 雙欄對照、公式保護與 MinerU/Zotero/Moonlight 對照

- **來源貼文**：[Threads @jokdooaa 貼文](https://www.threads.com/@jokdooaa/post/Dejc_d5GWh_)
- **發布者**：`jokdooaa (@jokdooaa)`
- **工具 GitHub**：[`YuriyLin/PaperRead`](https://github.com/YuriyLin/PaperRead)（MIT，作者在留言區給的連結）
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-16 重審：貼文文字、3 張圖、未登入看得到的 10 則留言（含作者 2 則）都看過；貼文顯示 104 則回覆，其餘未登入看不到。另看了作者留言連結的 repo README 與 5 則 issue。

- **作者圖片**（3 張，都是同一套閱讀器的畫面）：
  - 圖 1：雙欄對照。左欄中文譯文（有螢光筆與底線標記、公式照原樣排版），右欄原始 PDF 頁面，對應段落同步反白。上方工具列有「原文／譯文／雙語」切換與 PDF、筆記、問 AI、研究幾個按鈕。
  - 圖 2：左欄譯文，右欄「問 AI」面板。使用者選了一段公式請它解釋，AI 逐項說明體積渲染公式的每個符號；面板下方可選模型，並顯示已用的 token 數。
  - 圖 3：左欄譯文加劃線，右側邊欄列出「我的劃線」筆記與「AI 問答」摘要，一段對一則。
- **作者留言補充**：
  - 第 1 則直接給出工具連結：**[`YuriyLin/PaperRead`](https://github.com/YuriyLin/PaperRead)**（論文閱讀、研究探索與知識整理工作區）。
  - 第 2 則回答網友：想複製原文可切到右上角的「雙語」顯示。
- **網友留言重點**：
  - `_zhi07`：閱讀器裡的 PDF 變成純圖片，原文不能複製（這是留言當時的狀況；上游 v1.5.2 已加「PDF 原頁透明文字層」，見 1.1 節。）
  - `ivan0915`、`_yvyu936_`：問這是什麼 app（答案就在作者第 1 則留言）。
  - `rph.wei`：自己為了大學教學也想做類似工具。其餘是收藏用的短留言。
  - repo issue：#9 用本機 3B／4B 小模型翻譯時，提示詞裡的公式與表格範例會被照抄進譯文；#10 背景翻譯或自動儲存時閱讀位置會往上跳；#8 本機 Ollama 模型翻譯報錯；#7 macOS 版連不到 OpenAlex（憑證問題）；#6 Linux Firefox 上工具列按鈕失效。
- **對分析的影響**：
  - **原筆記把工具認錯了。** 原筆記沒看留言，只憑截圖猜成商業服務 Moonlight（themoonlight.io）。作者留言明寫是開源的 PaperRead。標題、短標題、1.1 節、1.3 節對照表、第 2 節都已改。
  - PaperRead 的性質與 Moonlight 相反：MIT 授權、文獻庫存在本機、有 Windows 安裝檔、AI 可接 Claude Code／Codex CLI／Antigravity CLI 或本機 Ollama。原筆記「雲端商業服務，機密論文不可上傳」的顧慮是針對 Moonlight 的，對 PaperRead 要改成「看你接哪個模型」。
  - 已完成的 `T-20261017-13` 交付的是「Moonlight 與 MinerU 對比指南」，比錯對象；任務狀態未動，列入回報由整合者決定是否重開。`T-20261017-14`（公式與引用保護提示詞）與工具是哪一套無關，不受影響；issue #9 反而是它的實例。
  - 新增 `T-20261017-35`：實測 PaperRead。筆記狀態因此由 done 改為 in-progress（已做 3、待做 1）。

---

## 1. 核心內容摘要與技術深挖

### 1.1 貼文背景與工具識別
- **痛點**：研讀英文學術論文（尤其是 CV/AI 領域論文，如貼文中展示的 CVPR 3D 視覺論文 *OpenVoxel / Dr.Splat*）時，傳統機器翻譯（如 Google 翻譯、常見瀏覽器擴充套件）會引發三大災難：
  1. **排版崩壞**：雙欄 PDF 排版錯亂，行尾斷詞拼裝失敗。
  2. **公式亂碼**：數學公式（如 $\sum_{j \in HW} 1(M_j=k) \cdot \mathbf{f}_j^{pts}$、$\arg\min$）被粗暴翻譯或吃字，喪失學術嚴密性。
  3. **引用混淆**：論文內引用（如 `[Sun et al., 2025]`）被機械式翻譯，無法點擊對照。
- **工具識別**：貼文截圖裡的閱讀器是 **[PaperRead](https://github.com/YuriyLin/PaperRead)**，作者在留言區直接給了 repo 連結。（原筆記沒看留言，憑畫面猜成商業服務 Moonlight，2026-11-16 更正。）
  - 開源、MIT 授權，建立在 [EasyRead](https://github.com/Edwardxlai/easyread) 之上；repo 於 2026-10-09 建立，重審時約 370 顆星、版本 v1.5.3。
  - 提供 Windows x64 安裝檔、macOS（Apple Silicon）DMG、Linux AppImage，另有 Docker 瀏覽器版（`docker compose up -d` 後開 `http://localhost:8765`）。
  - 文獻庫存在本機（JSON 檔，可用 Git 管理）；用雲端模型或文獻搜尋時，相關內容才會送到所選的服務。
  - AI 模型可接本機 CLI（Antigravity CLI、Claude Code、Codex CLI）、雲端 API、或本機 Ollama／LM Studio；不設模型時 PDF 閱讀、手寫註記、文獻管理仍可用，翻譯與問答才需要模型。
- **核心功能架構**（依截圖與 README）：
  - **雙欄同步對照**：左欄中文譯文，右欄原始 PDF 頁面，對應段落同步反白。
  - **公式保留**：截圖中譯文裡的公式照原樣排版，沒有被翻譯。實作方式 README 沒寫；issue #9 顯示用太小的本機模型時，提示詞範例會污染譯文。
  - **輔助研究套件**：頂部「原文／譯文／雙語」切換，另有 PDF、筆記、問 AI、研究幾個面板；README 還列出閱讀看板、閱讀路徑、手寫註記、心智圖、跨論文檢索與 Obsidian 匯出。
  - **已知限制（留言與 issue）**：背景翻譯時閱讀位置會跳動（issue #10）。
  - **「PDF 原頁不能複製」看來已處理（2026-11-17 以 GitHub API 查證，未實跑）**：這是貼文留言（`_zhi07`）回報的舊狀況，當時作者建議改用雙語模式。上游 `CHANGELOG.md` 的 v1.5.2（2026-10-31 發布）列有「PDF 原頁透明文字層」，寫明提取文字座標、複製原文不再逐字斷行或漏空格；原始碼有對應的 `easyread/selectable_text.py`（commit `3ffd3d0` 加入，另有 `tests/test_selectable_text.py`）。所以不再列為已知限制；實際能不能複製，留給 `T-20261017-35` 實測確認。
  - **安全注意**：PaperRead 接 Antigravity CLI 時會帶 `--dangerously-skip-permissions`（`easyread/engines.py` 第 205 行，commit `22ccc94`；另見 [`docs/academic-bilingual-paper-reader-guide.md`](../docs/academic-bilingual-paper-reader-guide.md) 的呼叫方式表）。這是略過權限確認的旗標，依 AGENTS 零信任規則不實跑這條路徑；要實測只用 Claude Code（限讀檔工具）或 Codex CLI（唯讀沙盒）後端。

### 1.2 論文閱讀器架構可視化（通用管線，非 PaperRead 的實際實作）

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   AI 學術論文雙語解析與閱讀管線                         │
└────────────────────────────────────────────────────────────────────────┘

    [學術 PDF 論文] (包含雙欄排版、複雜 LaTeX 數學公式、圖表、文獻引用)
           │
           ▼
    ┌───────────────────────────────────┐
    │ 1. 文檔版面分析 (Layout Analysis)  │ (如 MinerU / LayoutLMv3 / PDF-Extract)
    │    - 文本區塊 vs 數學公式 vs 圖表 │
    └──────────────────┬────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
    【LaTeX 公式 / 程式碼】     【正文與段落文字】
    (以 Token 隔離保護，        (透過學術 Prompt 送交 LLM 翻譯，
     避免被模型竄改)             保持術語精準度與專業文風)
         │                           │
         └─────────────┬─────────────┘
                       │ 重新編排組裝 (KaTeX / Markdown)
                       ▼
    ┌───────────────────────────────────┐
    │ 2. 雙欄同步渲染器 (Dual Renderer)  │
    │    ├─ 左欄：繁/簡中文對照 (保留公式)
    │    └─ 右欄：原始 PDF (保留原始座標與高亮)
    └──────────────────┬────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────┐
    │ 3. 內嵌 RAG 與文獻知識問答        │ (問 AI、提取核心貢獻、查閱關聯論文)
    └───────────────────────────────────┘
```

### 1.3 官方與開源生態對照

| 方案 | 類型 | 核心特點 | 隱私與成本 |
| :--- | :--- | :--- | :--- |
| **PaperRead** (`YuriyLin/PaperRead`) | 開源桌面程式／Docker（**貼文介紹的就是這套**） | 雙欄對照、問 AI、劃線筆記、閱讀看板、Obsidian 匯出；可接 Claude Code／Codex CLI 當翻譯模型 | MIT；資料存本機；成本取決於接的模型 |
| **Moonlight** (`themoonlight.io`) | 商業 SaaS / Chrome 擴充（原筆記誤認的對象，留作對照） | 開箱即用、雙欄對照、支援手機端閱讀 | Freemium（基礎免費額度，進階功能採訂閱制） |
| **MinerU** (`opendatalab/MinerU`) | 開源工具 (GitHub 20k+ ⭐) | 超強 PDF 轉 Markdown/JSON，公式表格精準度頂級 | 100% 本地開源、免額度、適合自動化管線批次轉檔 |
| **Immersive Translate** (沉浸式翻譯) | 瀏覽器擴充 | 支援多翻譯引擎（DeepL, OpenAI, Claude）、通用網頁與 PDF 雙語 | 需自備 API Key 或購買會員 |
| **Zotero + PDF Translate / SciSpace** | 本地文獻庫生態 | 本地文獻管理與即時劃詞翻譯無縫整合，支援本地 Ollama 模型 | 完全私有化，不外洩研究隱私 |

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **學術文獻檢索技能組**：已具備多支官方生醫與學術搜尋 Skill（如 `literature-search-arxiv`, `literature-search-biorxiv`, `literature-search-europepmc`, `literature-search-openalex`）。
  - **文獻研讀方法論**：已收錄 `notes/2026-10-17-academic-reading-framework.md`（5W1H-CQR-KSU 結構化精讀）。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **公式保護意識**：任何涉及論文研讀、摘要提取或翻譯的 Agent 技能，必須將 LaTeX 區塊（`$...$`、`$$...$$`）視為保護區塊，嚴禁讓翻譯模型破壞變數名稱與上下標。
    2. **雙欄/結構化閱讀工具鏈**：日常研讀 arXiv 論文可先評估 PaperRead（開源、有 Windows 安裝檔、可直接用本機的 Claude Code／Codex CLI 當模型）；批次轉檔仍可用 MinerU。
  - **不適用 / 需注意的部分**：
    - PaperRead 的文獻庫在本機，但翻譯與問答會把內容送到所接的模型；未公開的專利草稿、內部白皮書要接本機模型（Ollama／LM Studio）才不外流。Moonlight 這類雲端服務則一律不可上傳機密文件。
    - PaperRead 是剛滿一個月的個人專案（v1.5.x），安裝檔執行前要照維護者的第三方程式檢查流程走一遍。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-13`**｜**[優先級：高]** 整理學術論文雙語排版與公式保護閱讀工具手冊（Moonlight 與開源 MinerU 對比指南）
  - **完成日期**：2026-10-23
  - **目標範圍**：`C:\GitHub\ai-inbox\notes\` 與文獻閱讀參考手冊
  - **具體實作步驟**：
    1. 實測 Moonlight Chrome 擴充套件於 arXiv 論文（如 3DGS / LLM 論文）上的雙語對照流暢度與公式保留度。
    2. 梳理開源工具 `opendatalab/MinerU` 的本地安裝與 CLI 轉檔指令，撰寫「保護 LaTeX 公式並轉為雙語 Markdown」之標準流程。
    3. 輸出比較表格與情境推薦（快速泛讀 vs 機密深度研讀）。
  - **驗收標準（DoD）**：在文獻研讀指南中補全 Moonlight 快速上手與 MinerU 本地雙語工作流，經驗證無格式遺漏。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `docs/academic-bilingual-paper-reader-guide.md`，完整梳理 Moonlight 雙欄對照與開源 MinerU 本地 CLI 轉檔之全方位對比、排版公式保護機制與場景選型決策樹。

- [x] **`T-20261017-14`**｜**[優先級：中]** 在學術論文摘要與翻譯提示詞中注入「LaTeX 數學公式與引用保護規則」
  - **完成日期**：2026-10-23
  - **目標範圍**：文獻閱讀 Prompt / 全域學術閱讀技能規範
  - **具體實作步驟**：
    1. 檢視現有論文摘要與解讀類 Prompts。
    2. 加入公式保護規範：要求 Agent 遇到行內公式 `$...$` 或塊狀公式 `$$...$$` 時，原封不動保留英文變數與符號，不得自行翻譯變數名。
    3. 加入引用索引保護規範：論文引用標籤（如 `[Author et al., Year]` 或 `[1]`）強制保留超連結或原文代號。
  - **驗收標準（DoD）**：隨機抽測一篇含密集數學公式的 arXiv 論文進行 AI 解讀，所有 LaTeX 符號與引用標記保持 100% 原始語法。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `templates/latex-citation-protection-prompt.md`，制定包含行內公式、區塊公式、引用標籤與交叉參照四項零竄改保護契約，並附 3DGS 論文真實測試輸入案例與預期標準輸出。

- [x] **`T-20261025-05`**｜**[優先級：高]** 實作學術論文雙語翻譯「LaTeX 公式與引用零竄改保護」及「5W1H-CQR-KSU 結構」之外部裁判驗證器
  - **完成日期**：2026-10-25
  - **目標範圍**：`tools/verify_academic_and_latex_guard.py` 與 `tests/test_verify_academic_and_latex_guard.py`
  - **具體做法**：
    1. 實作 `tools/verify_academic_and_latex_guard.py`（純 Python stdlib），包含：(a) 原文與譯文比對函式 `verify_latex_and_citations_preserved(source_text, translated_text)`，自動抽取所有行內公式 `$...$` / `\(...\)`、區塊公式 `$$...$$` / `\begin{equation}...\end{equation}`、引用標籤 `\cite{...}` / `[1]`–`[99]` 與交叉參照 `\ref{...}` / `\eqref{...}`，斷言譯文 100% 零遺漏、零竄改；(b) 機械驗證 `templates/latex-citation-protection-prompt.md` 內嵌之測試輸入與預期輸出符合零竄改契約；(c) 機械驗證 `templates/academic-reading-prompt.md` 與 `docs/academic-reading-smoke-report.md` 完整涵蓋 5W1H、CQR 與 KSU 三層結構。
    2. 撰寫 `tests/test_verify_academic_and_latex_guard.py`，涵蓋真實範本通過、公式變數被誤譯攔截、引用標籤遺失攔截、交叉參照竄改攔截與 5W1H-CQR-KSU 缺漏攔截測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_academic_and_latex_guard.py` 回傳 exit 0，且 `python -m pytest tests/test_verify_academic_and_latex_guard.py -q` 全數通過（至少 6 項測試）。
  - **實作紀錄 / 證據**：完成 `tools/verify_academic_and_latex_guard.py` 與 `tests/test_verify_academic_and_latex_guard.py`，實作原文與譯文雙向公式/引用精確比對、四大契約校驗與 5W1H-CQR-KSU 三層架構外部裁判，並通過 9 項單元測試與 CLI 驗證。

- [ ] **`T-20261017-35`**｜**[優先級：中]** 實測開源論文閱讀器 PaperRead，並更正雙語閱讀指南比錯對象的問題
  - **狀態**：⚪ 不做（已做唯讀評估並把雙語閱讀指南改以 PaperRead 為主角（docs/academic-bilingual-paper-reader-guide.md）；實跑部分不做：PaperRead 呼叫 Antigravity CLI 時帶 --dangerously-skip-permissions（easyread/engines.py:205），依 AGENTS 零信任規則不在本機執行此第三方程式。）
  - **目標範圍**：`docs/academic-bilingual-paper-reader-guide.md` 與本機隔離環境（`C:\GitHub\_sandbox\paperread`）
  - **具體做法**：
    1. 先做安全檢查：clone [`YuriyLin/PaperRead`](https://github.com/YuriyLin/PaperRead) 到隔離目錄，只讀原始碼，確認沒有外傳資料或執行遠端腳本的行為，再決定用 Docker 瀏覽器版還是原始碼啟動；不直接執行 Releases 的安裝檔。
    2. 用一篇含密集公式的 arXiv 論文實測：雙語對照、公式是否原樣保留、引用標記是否保留、問 AI 能否接本機 Claude Code 或 Codex CLI。
    3. 重現留言與 issue 提到的兩個限制：PDF 原頁文字不能複製、背景翻譯時閱讀位置跳動，記錄在本機是否發生。
    4. 把 `docs/academic-bilingual-paper-reader-guide.md` 的主角由 Moonlight 改為 PaperRead，Moonlight 降為對照項，並寫明原貼文介紹的是哪一套。
  - **驗收標準（DoD）**：`docs/academic-bilingual-paper-reader-guide.md` 內有 PaperRead 的實測段落（安裝方式、公式與引用保留結果、兩個限制是否重現），且文中不再把貼文工具寫成 Moonlight；`python tools/verify_inbox.py` 通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
