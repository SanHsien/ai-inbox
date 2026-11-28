# 獨立審查報告：2026-11-26-vista-researcher-tw-gemini-notebook-academic-guide

- reviewer: codex/gpt-6.1-sol@01a222bf-0b87-7663-975b-3d30f9731970
- content_sha256: b5ac47d022adc38c6265db624f4848404412fbaa9156843161f4c46ac1969071
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 6；source_review: full（作者聲明 full）
- source_ref: codex thread 01a222bf-0b87-7663-975b-3d30f9731970

---
結論：**changes_requested，共 6 處更正**。筆記內容雜湊與指定值一致；未修改任何檔案。

### 1. 原始資料讀完度（source）

已重新開啟[來源簡報](https://deck.researcher.tw/decks/gemini-notebook-research-guide/)，讀取正文，但未完成全部 SVG 圖表與封面圖片的視覺核對，實際看過圖片數為 0。文字頁未見留言區，讀到留言 0 則。

因此本次 **不對 source 下結論，從 scope 移除**；保留作者的 `full` 聲明，不把審查工具的限制算成作者錯誤。29 張圖片與完整讀完度須另補審。

### 2. 事實查核（facts）

確認相符：更名日期、用戶與組織數、四種語音摘要、Chat View 的存取限制，以及 PleasePrompto 專案封存日期。出處為 [Google 公告](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/)、[語音摘要文件](https://support.google.com/gemininotebook/answer/16212820?hl=en)、[分享文件](https://support.google.com/gemininotebook/answer/16322204?hl=en)與[專案頁](https://github.com/PleasePrompto/notebooklm-mcp)。

須更正：

1. **容量單位**：官方限制是 500,000 **words**，不能直接寫成 50 萬中文字。應保留原文單位。[官方限制](https://support.google.com/gemininotebook/answer/16269187?hl=en)
2. **工時比較**：Samaan 研究的人工基準是**推估 165.1 人時**，不是同場實測從 165 小時降至 17.7 小時；該文也是預印本。[論文摘要與方法](https://pubmed.ncbi.nlm.nih.gov/42396330/)
3. **隱私保障範圍**：免人工審閱與模型改進用途的保障不僅有 Workspace／教育帳號，官方也列出 Google Cloud 方案。「僅」應刪除，並分方案說明。[方案文件](https://support.google.com/gemininotebook/answer/16213268?hl=en)

### 3. 證據分級（evidence）

另有三處把限定結果或作者建議寫得過於確定：

4. **20 篇門檻**：簡報確實提出此建議，但未提供可驗證的比較實驗。應標成作者經驗建議，不能據此把所有筆記本固定限制為 15 篇。[簡報相關段落](https://deck.researcher.tw/decks/gemini-notebook-research-guide/#1)
5. **掃描 PDF 必然失敗**：未找到一手文件支持「無文字層必定完全讀不到且不報錯」。可保留文字辨識前檢建議，但須降為作者回報及待驗證風險；官方目前列有圖片與 PDF 支援，也提醒部分圖片效果有限。[官方來源文件](https://support.google.com/gemininotebook/answer/16215270?hl=en)
6. **13% 的分母與適用範圍**：這是 2025 年新聞文件查詢實驗中，NotebookLM **15 次回答有 2 次含幻覺**；300 是語料庫文件數，不是回答樣本數。平均 3 個幻覺也只針對出錯回答，不能當成現行產品或學術任務的固定錯誤率。[論文 §4–5](https://arxiv.org/html/2509.25498v1)

分級結果：

- **一手來源已確認**：官方功能、政策，以及論文在自身實驗範圍內的數據。
- **二手轉述**：簡報轉述研究與使用經驗。
- **推算／未查證**：20 篇通用門檻、掃描 PDF 必然失敗；人工工時則是研究明示的推估基準。

### 4. 任務影響（task_impact）

只有 `T-20261126-03`，目前未完成。已開啟 `templates/academic-reading-prompt.md`，未見本任務擬加入的模組，**沒有已完成產出需要回修**。

整合者應先修任務規格中的 15／20 篇硬門檻、掃描 PDF 斷言，以及研究數字的適用範圍，再實作範本。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 6,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第0節將單一來源容量寫成50萬字。",
      "problem": "官方單位為500,000 words，不能直接等同50萬中文字。",
      "evidence": "https://support.google.com/gemininotebook/answer/16269187?hl=en",
      "fix": "改為500,000 words，並保留本機上傳200MB限制。"
    },
    {
      "kind": "evidence",
      "claim": "第0節將Samaan研究描述為工時從165小時降至17.7小時。",
      "problem": "165.1人時是依既有基準推估，並非同場人工對照實測；引用版本為預印本。",
      "evidence": "https://pubmed.ncbi.nlm.nih.gov/42396330/",
      "fix": "標示預印本，改寫為流程使用17.7人時，對比推估人工基準165.1人時。"
    },
    {
      "kind": "fact",
      "claim": "第0節將免人工審閱與訓練保障限定於Workspace及教育版。",
      "problem": "官方方案頁也列出Google Cloud方案的相關資料保障，排他性的限定不完整。",
      "evidence": "https://support.google.com/gemininotebook/answer/16213268?hl=en",
      "fix": "刪除僅限兩類帳號的說法，分別列明個人、合資格Workspace／教育及Google Cloud方案。"
    },
    {
      "kind": "evidence",
      "claim": "第0、1節與任務步驟把20篇視為品質下降門檻，並要求單本不超過15篇。",
      "problem": "目前只有簡報作者建議，未提供支持通用數量門檻的比較實驗。",
      "evidence": "https://deck.researcher.tw/decks/gemini-notebook-research-guide/#1",
      "fix": "標為作者經驗建議；依研究問題、來源內容與回答驗證結果決定分組，不設定通用硬上限。"
    },
    {
      "kind": "evidence",
      "claim": "第0、1節把無文字層掃描PDF描述為必然完全無法讀取且不報錯。",
      "problem": "未找到一手來源證實這項必然性；不能把作者回報提升為通用產品限制。",
      "evidence": "https://support.google.com/gemininotebook/answer/16215270?hl=en ; https://deck.researcher.tw/decks/gemini-notebook-research-guide/#1",
      "fix": "標示作者回報與尚未獨立驗證，保留抽查辨識結果、必要時先做文字辨識的建議。"
    },
    {
      "kind": "evidence",
      "claim": "第0節與任務標題引用13%幻覺率，未交代回答樣本及測試年代。",
      "problem": "13%為2025年特定新聞文件實驗中2／15次NotebookLM回答含幻覺；300是語料庫文件數。平均3個幻覺只針對出錯回答。",
      "evidence": "https://arxiv.org/html/2509.25498v1",
      "fix": "補上測試年代、任務、回答分母及條件，明示不代表現行產品或一般學術任務的固定錯誤率。"
    }
  ],
  "task_impact": []
}
```
