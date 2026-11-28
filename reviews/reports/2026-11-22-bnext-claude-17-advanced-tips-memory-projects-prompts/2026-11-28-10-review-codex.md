# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a2219c-8bfc-7153-aa20-d6a5b8793dc7
- content_sha256: 5e9ba87dbee97751cb24417429ec57aa7c85479b72abedb7b23fb24dfd37642f
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: pass；corrections: 0；source_review: full（作者聲明 full）
- source_ref: codex thread 01a2219c-8bfc-7153-aa20-d6a5b8793dc7

---
結論：`pass`，限 `facts、evidence、task_impact`。沒有找到需更正的主張；原始來源未能讀取，`source` 留待補審。全程未修改檔案，內容雜湊與指定值一致。

1. **原始資料讀完度（source）**

   數位時代完整網址及文章編號網址均無法開啟，搜尋也未取得可讀原文。本次未讀到原頁圖片或留言，無法確認圖片總數與留言計數。

   依交付規則，移除 `source` 範圍，保留作者的 `full` 聲明；這不代表本次已確認其讀完度。

2. **事實查核（facts）**

   - 記憶研究日期、Opus 5.5 的兩個得分、相對提升約 28%，以及三個模型的寶可夢紀錄，均符合[官方研究](https://www.anthropic.com/research/components-of-agent-memory)。筆記已限制適用情境，也未把檔案數寫成因果證明。
   - Projects 的帳號記憶開關符合[官方記憶說明](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)；新整合介面不支援較早節點分支，符合[官方限制](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)。
   - 安全檢查觸發模型切換、預設啟用及顯示通知，符合[官方說明](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5)。
   - Workspace 側邊欄的測試版限制與文件生成功能，分別有[Workspace 文件](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)及[檔案建立文件](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)支持。
   - 回饋對話最長保留五年、可能用於訓練，以及商業方案適用範圍，符合[官方隱私說明](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)。

   原文作者、發布日期及 Hassid 建議的逐字歸屬，本次未能獨立確認，不列為已查證。

3. **證據分級（evidence）**

   - **一手來源已確認**：上述研究數據、功能限制、隱私條款；防幻覺及後續查核策略也符合[官方指引](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)。
   - **二手來源**：記憶條數收斂、十行摘要、選項數量及清空自訂指令等建議。筆記已標示轉述、個人主張或待測。
   - **推算／未查證**：約 28% 為官方得分的算術換算；本機策略效果與作者模型切換個案已保留限制。

   未發現把二手建議或未測效果冒充官方實證的情形。

4. **任務影響（task_impact）**

   僅有 `T-20261122-02`，目前未勾選完成。另已讀取既有產出 `docs/agent-memory-and-prompting-best-practices.md`：核心數據、非因果限制及對話分支條件均與查證結果相符，未發現需回報的錯誤前提。

下一步：另派可讀原頁的審查者完成 `source`。

```json
{
  "verdict": "pass",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 0,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [],
  "task_impact": []
}
```
