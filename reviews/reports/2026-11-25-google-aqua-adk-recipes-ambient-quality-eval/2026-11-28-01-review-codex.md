# 獨立審查報告：2026-11-25-google-aqua-adk-recipes-ambient-quality-eval

- reviewer: codex/gpt-6.1-sol@01a22253-59f5-7fa3-8959-e913189c530d
- content_sha256: 69e13fa57bf09c9c318cf837c37fc7bea6edd2fd2ce4ecf95ebb34cb0fece3ba
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a22253-59f5-7fa3-8959-e913189c530d

---
結論：**changes_requested，1 處更正**。已完成 `facts`、`evidence`、`task_impact`；`source` 未完成，不下修作者的 `full`。

筆記內容雜湊於審查前後均符合：
`69e13fa57bf09c9c318cf837c37fc7bea6edd2fd2ce4ecf95ebb34cb0fece3ba`

1. **原始資料讀完度（source）**

   已重新讀取 [InfoQ 原文](https://www.infoq.cn/article/YAc2TqCHc09kAFF1A7BS)文字，但兩張圖片讀取失敗，留言區與留言總數也未取得。實際看過圖片 0 張、讀到留言 0 則；無法確認作者所稱的零留言。

   因此從結果 `scope` 移除 `source`。這是本次存取限制，不列為筆記錯誤，也不以官方部落格的圖片代替原文圖片驗收。

2. **事實查核（facts）**

   **F1：首輪實驗被誤寫成生產會話抽測。**

   位置：筆記第 0 節「核心機制」第 5 點，稱「生產會話抽測」。

   Google 官方文章的實驗段明確說明：32 次會話來自四組腳本旅程的重放。修正提示詞後，再重放同一批會話比較結果。因此，**修正前後都屬受控重放**，不能讓讀者誤以為首輪是實際生產流量採樣。出處：[Google 官方文章，實驗第 2、4 節](https://developers.googleblog.com/the-outer-loop-insights-first-an-ambient-quality-agent-that-diagnoses-your-production-agent/)。

   建議改為：四組腳本旅程共重放 32 次，先進行診斷，再於修改提示詞後重放比較；整組結果均非真實線上流量成效。

   其餘主要主張可核對：三種遙測來源與 CLI 功能見 [AQuA README](https://github.com/google/adk-recipes/blob/main/core/python/ambient-quality-agent/README.md)；11 個配方見 [core/python](https://github.com/google/adk-recipes/tree/main/core/python)；技能與使用者外掛的邊界、模型使用規則見 [AGENTS.md](https://github.com/google/adk-recipes/blob/main/AGENTS.md)。

3. **證據分級（evidence）**

   - **一手來源已確認**：五階段流程、採樣與核驗上限、14 天狀態轉換，以及上述實驗數字，均有 Google 官方說明；數字應標為官方示範實驗結果。
   - **原始碼已確認**：對目標程式庫的唯讀邊界與修改建議的快照驗證，見 [root_cause_tools.py](https://github.com/google/adk-recipes/blob/main/core/python/ambient-quality-agent/src/ambient_quality_agent/core/root_cause_tools.py)。
   - **二手來源**：InfoQ 是轉述，不能據其簡化敘述，把重放實驗升格為生產流量證據。此問題已計入 F1，不重複計數。
   - **未查證**：分析當天精確的 `10,674` stars 未取得歷史快照；目前頁面的約數不足以證明或否定，不列為已確認事實，也不據此提出更正。

4. **已完成任務產出（task_impact）**

   `T-20261125-01`、`T-20261125-02` 都未完成，沒有已完成產出需要追修。第一項預定的 `docs/ambient-quality-agent-sidecar-spec.md` 目前不存在；後續撰寫時應沿用 F1 的實驗界定。

全程未修改檔案。下一步由作者修正 F1，另補審原文圖片與留言區。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 1,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 0 節核心機制第 5 點將首輪 32 條會話稱為生產會話抽測",
      "problem": "官方說明首輪即為四組腳本旅程的 32 次重放；修正後再重放同一批會話。僅限定修正後為受控重放，會誇大首輪資料的真實生產代表性。",
      "evidence": "https://developers.googleblog.com/the-outer-loop-insights-first-an-ambient-quality-agent-that-diagnoses-your-production-agent/",
      "fix": "明寫首輪與修正後均為受控腳本重放，32 次會話來自四組旅程，不將其描述為實際生產流量採樣。"
    }
  ],
  "task_impact": []
}
```
