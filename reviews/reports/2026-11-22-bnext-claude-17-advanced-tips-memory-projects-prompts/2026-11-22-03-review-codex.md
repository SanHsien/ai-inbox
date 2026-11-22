# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a203c5-edaa-7ec0-bd2c-63b0b97f8d04
- content_sha256: 2aa965e52abf377da52682587710c88a3c96247ce6c1342a7f1c0d102562c05d
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a203c5-edaa-7ec0-bd2c-63b0b97f8d04

---
結論：`changes_requested`，共 **1 處更正**。內容雜湊與指定值一致；未修改任何檔案。

### 1. 原始資料讀完度（source）

[數位時代原頁](https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts)及不含標題的網址均無法讀取，因此未核對正文、圖片與留言。

本次結果排除 `source`，保留作者的 `full` 聲明；不把讀取限制列為筆記錯誤。作者、發布日期與原文完整度仍需補審。

### 2. 事實查核（facts）

已確認：

- 記憶研究日期、CL-Bench 分數、寶可夢檔案數與進度均符合官方資料；28% 是相對增幅，筆記已限制適用範圍，也未把檔案數當成因果證明。[Anthropic 研究](https://www.anthropic.com/research/components-of-agent-memory)
- Project 可關閉帳號記憶；編輯先前訊息可建立另一版本對話。[記憶說明](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)、[對話分支說明](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them)
- 後續提示查核、允許不確定答案與核對引用，符合官方減少幻覺指引。[官方指引](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- Workspace 側邊欄、GitHub 檔案整合、CSV 分析與文件生成都有官方依據。[Workspace](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)、[GitHub](https://support.claude.com/en/articles/10167454-use-the-github-integration)、[文件生成](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)
- 回饋保留最長五年、可能用於訓練及使用前解除 ID 關聯，符合商業產品條款；筆記有註明方案邊界。[隱私條款](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)

**更正 1：自動切換舊模型的官方依據**

第 1 節末段把自動模型降級概括為個人經驗、缺乏官方文件，說法過廣。官方已有專頁：特定安全檢查可觸發 Opus 5／5.5 降級，聊天介面預設啟用，並顯示切換通知。這不代表一般對話會任意換模型，也不能證明作者個案的原因。[官方切換說明](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5)

建議分開寫：**安全檢查觸發的降級已有官方說明；作者個案是否屬此機制，尚未確認。**

### 3. 證據分級（evidence）

- **一手已確認**：上述研究數據、產品功能與隱私條款。
- **二手／待測**：105→26 條記憶收斂、10 行交接摘要；筆記已標明，維持即可。
- **推算／未查證**：作者個案的模型切換原因，不可直接套用官方降級機制。

更正 1 同時涉及證據分級，合計仍為一處。

### 4. 任務產出影響（task_impact）

唯一任務 `T-20261122-02` 仍未勾選完成，但其[產出文件](/C:/GitHub/ai-inbox/docs/agent-memory-and-prompting-best-practices.md)已存在，已開啟檢查。

文件未沿用上述自動模型切換說法，本次更正沒有直接影響其內容。由整合者修正筆記，再補做來源完整度審查。

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
      "claim": "第1節末段將自動切換舊模型概括為作者經驗，並稱缺乏官方文件。",
      "problem": "官方已有安全檢查觸發自動模型降級的說明，因此不能概括稱無官方依據；但官方機制也不能直接證明作者個案的原因。",
      "evidence": "https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5",
      "fix": "改為：特定安全檢查觸發的自動降級已有官方文件；作者個案是否屬此機制尚未確認，不可外推為一般對話會任意切換模型。"
    }
  ],
  "task_impact": []
}
```
