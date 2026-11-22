# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a2052a-ce77-7b30-b118-5fc6f9bdcce9
- content_sha256: 306845f40ccbb30c4b9c3a7e944cad3cd42ae487635f9d0ddd0e60b0918e0b00
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-23
- verdict: pass；corrections: 0；source_review: full（作者聲明 full）
- source_ref: codex thread 01a2052a-ce77-7b30-b118-5fc6f9bdcce9

---
結論：`pass`，僅限 `facts、evidence、task_impact`；原始來源未讀到，`source` 留待補審。未修改任何檔案，內容雜湊與指定值一致。

1. **原始資料讀完度（source）**

   [數位時代原文](https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts)無法開啟，正文、圖片、留言計數均未能獨立核對。因此排除本次 `source` 範圍，保留作者的 `full` 聲明，不將讀取限制列為更正。實際看過原文圖片 0 張、留言 0 則。

2. **事實查核（facts）**

   - **研究日期、分數與案例一致**：官方研究發布於 2026-11-06；Opus 5.5 的資料庫任務分數為 0.655→0.838，相對增幅約 27.94%。Sonnet 3.7、Fable 5 的檔案數與徽章數，以及 Opus 5.5 通關的敘述均符合原文。筆記也保留了單次案例、非因果證明的限制。[官方研究](https://www.anthropic.com/research/components-of-agent-memory)
   - **Projects 隔離設定正確**：官方說明確認可關閉 `Use account memory`，保持專案記憶分離。[專案記憶說明](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)
   - **對話修正與幻覺限制正確**：官方支持後續提示查核、修正回答；編輯較早訊息可建立不同版本的對話。筆記沒有把編輯提示詞當作唯一解法，也未保證消除幻覺。[減少幻覺](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)、[對話版本說明](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them)
   - **整合與檔案功能有官方依據**：Google Workspace 側邊欄、GitHub 檔案整合、CSV 分析及 Word／Excel／PDF 產出皆已提供。[Workspace](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)、[GitHub](https://support.claude.com/en/articles/10167454-use-the-github-integration)、[檔案功能](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)
   - **隱私與模型切換描述正確**：回饋可能涉及完整對話、最長五年保留與訓練用途；筆記有註明商業方案範圍。安全檢查觸發模型切換、預設啟用及通知機制也符合官方說明。[隱私政策說明](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)、[模型切換說明](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5)

3. **證據分級（evidence）**

   官方數據與功能可確認；28% 為依官方分數計算。寶可夢比較已標為案例觀察；105→26 條記憶及十行摘要已標為二手轉述、待測。其他提示方式屬操作建議，未宣稱量化成效。未發現需更正的證據混用。

   原文作者、發布日期與 Hassid 建議的轉述忠實度，仍待原始來源補審。

4. **任務影響（task_impact）**

   唯一任務 `T-20261122-02` 仍未勾選完成。其產出 `docs/agent-memory-and-prompting-best-practices.md` 已存在並已讀取；主要數據、案例限制與二手建議標示和筆記一致。未發現需回報的錯誤前提；本次不認定任務已完成。

```json
{
  "verdict": "pass",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 0,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [],
  "task_impact": []
}
```
