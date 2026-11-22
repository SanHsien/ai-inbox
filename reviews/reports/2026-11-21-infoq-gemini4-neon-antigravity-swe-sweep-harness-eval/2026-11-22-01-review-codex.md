# 獨立審查報告：2026-11-21-infoq-gemini4-neon-antigravity-swe-sweep-harness-eval

- reviewer: codex/gpt-6.1-sol@01a20288-9539-7912-9670-61e324b39a5b
- content_sha256: db43c64dc8db4aea10732735d57091c6c7eb811eb33c064a3761febe9e495f71
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 4；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20288-9539-7912-9670-61e324b39a5b

---
結論：`changes_requested`，共 4 處更正。未修改任何檔案。

1. **原始資料讀完度（source）**

   已讀 [InfoQ 正文](https://www.infoq.cn/article/tDxNggErsJNeb53ZkYeF)，但圖片連結讀取失敗，文字版也未提供可核實的留言計數。實際看過圖片 0 張、留言 0 則；不能據此認定原站沒有留言。

   本次移除 `source` 範圍，保留作者的 `full` 聲明，不將存取限制列為更正。

2. **事實查核（facts）**

   [Google 模型卡](https://deepmind.google/models/model-cards/gemini-4-neon/)確認 SWE-sweep 六個數字；但[評測方法](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_neon_model_evaluation.pdf)明訂指標是子任務加權分數，不能直接稱為完整任務解題率。

   [Artificial Analysis 原文](https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain)支持主要成本與能力數字，但速度段落的多生成約 15% token、耗時少約四成，對應 xhigh；筆記未標明，容易與前面的 high 混讀。

3. **證據分級（evidence）**

   [官方文件](https://antigravity.google/docs/ide/overview/)確認聯合訓練存在，不能因此證明 39% 的提升有多少由聯合訓練造成。筆記的因果語氣過強。

   第 2 節比較兩篇筆記時，也把社群實測與官方評測的前後對應寫反。額度重置與 Windsurf 歷史，本次僅確認 InfoQ 有此轉述，未取得完整一手佐證。

4. **任務影響（task_impact）**

   本篇沒有新任務，僅連結已完成的 `T-20261120-03`。已讀產出 `docs/model-burn-rate-routing-matrix.md` 第 11.8～11.11 節；文件已標示 Google 自行計算、各框架差異及本機未實測，未發現上述錯誤因果結論傳入產出檔。無須列出產出修正項目。

下一步：整合者修正以下 4 處，再送審；圖片與留言另補審。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 4,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "標題與第 1 節將 SWE-sweep 百分比稱為解題率。",
      "problem": "官方方法將結果定義為 subtask-weighted reward，不能直接解讀成完整任務解決比例。",
      "evidence": "https://storage.googleapis.com/deepmind-media/gemini/gemini_4_neon_model_evaluation.pdf",
      "fix": "改稱 SWE-sweep 子任務加權分數；保留六個數字與倍率，補註 Google 自行計算及框架版本。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節速度段落未標示推理檔位，接在 high 檔成本比較後。",
      "problem": "Artificial Analysis 將多生成約 15% token、完成時間縮短約四成的比較放在 Neon xhigh 對 Carbon high 的說明中；筆記容易讓讀者誤認為也是 high 對 high。",
      "evidence": "https://artificialanalysis.ai/articles/gemini-4-neon-intelligence-gain",
      "fix": "明寫這組 token 與耗時比較的推理檔位，與 high 檔成本比較分開。"
    },
    {
      "kind": "evidence",
      "claim": "第 2 節將 Neon 的 39% 明確歸因於聯合訓練，並認定框架交互作用遠大於模型差距。",
      "problem": "官方確認聯合訓練存在，但公開比較同時改變框架與工具能力，未提供拆分聯合訓練效果的消融實驗，不能據此確立因果或一般性效果大小。",
      "evidence": "https://antigravity.google/docs/ide/overview/ ; https://storage.googleapis.com/deepmind-media/gemini/gemini_4_neon_model_evaluation.pdf",
      "fix": "改為這組配置顯示框架選擇可能大幅影響成績；聯合訓練的獨立貢獻尚未量化。"
    },
    {
      "kind": "evidence",
      "claim": "第 2 節比較本篇與 Woshipm 筆記時，把前者歸為社群實測、後者歸為官方控制實驗。",
      "problem": "依該段提及順序，前者是本篇 InfoQ 評析，後者才是 Woshipm 社群文章筆記，來源對應顛倒；官方比較也不宜直接稱為已隔離其他變因的控制實驗。",
      "evidence": "notes/2026-11-21-infoq-gemini4-neon-antigravity-swe-sweep-harness-eval.md 第 2 節；notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md",
      "fix": "直接寫明篇名：本篇轉述 Google 與 Artificial Analysis 評測，Woshipm 筆記整理社群文章及實測轉述；刪除含混的前者、後者。"
    }
  ],
  "task_impact": []
}
```
