# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a20892-137f-77b0-a1d9-fb35ff11a7dc
- content_sha256: 30c2d1f562d4a917d645a26329bd51b66e53561654c26a0ed228b818cbed8299
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-23
- verdict: pass；corrections: 0；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20892-137f-77b0-a1d9-fb35ff11a7dc

---
結論：`pass`，筆記未發現需更正處；僅涵蓋 `facts、evidence、task_impact`。原始來源尚待補審。全程未修改檔案，內容雜湊與派審值一致。

1. **原始資料讀完度：未完成，排除 `source`**

   [數位時代原頁](https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts)無法讀取，未能重新確認正文、作者、日期、圖片及留言。圖片實讀 0 張、留言實讀 0 則；頁面留言計數未知。依交付規則，保留作者的 `full`，不把讀取限制列為更正。

2. **事實查核：通過**

   - 官方研究支持 `0.655 → 0.838`；相對提升約 `27.94%`。寶可夢各模型的檔案數、徽章數及 Opus 通關描述相符；筆記已保留案例與因果的界線。[官方研究](https://www.anthropic.com/research/components-of-agent-memory)
   - 專案關閉帳號記憶的設定有官方依據。[記憶說明](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)
   - 編輯訊息建立分支、後續提示查核修正，均有官方依據。[分支說明](https://www.anthropic.com/research/end-subset-conversations)、[減少幻覺指引](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
   - 安全降級、回饋最長保留五年及可能用於訓練的限定語正確。[降級說明](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5)、[隱私條款](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)
   - Workspace 測試版、文件生成及 GitHub 存取限制與官方說明一致。[Workspace](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)、[文件生成](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)、[GitHub 整合](https://support.claude.com/en/articles/10167454-use-the-github-integration)

3. **證據分級：通過**

   官方數字與功能已有一手來源支持；28% 是可重算的相對增幅。105→26 條、10 行摘要、選項機率與清空自訂指令，已標為二手建議或待測。因原頁不可讀，未重新確認 Hassid 建議的轉述忠實度，不宣稱已確認其原話。

4. **任務影響：尚無已完成任務**

   唯一任務 `T-20261122-02` 仍未勾選。已有[產出草稿](C:/GitHub/ai-inbox/docs/agent-memory-and-prompting-best-practices.md:35)，其中「耗盡上下文與推理資源」比官方的耗費時間與資源更強；官方未證明資源耗盡。此項交整合者修正，不計入筆記更正數。

下一步：補審原始來源，並修正草稿措辭後再驗收任務。

```json
{
  "verdict": "pass",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 0,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [],
  "task_impact": [
    {
      "task": "T-20261122-02",
      "file": "docs/agent-memory-and-prompting-best-practices.md",
      "issue": "任務尚未完成，但已有草稿。第 35 行將 Sonnet 3.7 的記憶維護成本寫成「耗盡上下文與推理資源」；官方只描述耗費更多時間與資源，未證明耗盡。建議改為增加維護與檢索成本。依據：https://www.anthropic.com/research/components-of-agent-memory"
    }
  ]
}
```
