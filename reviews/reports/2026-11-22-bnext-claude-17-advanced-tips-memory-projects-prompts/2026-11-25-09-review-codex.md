# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a20f79-b639-7f82-8f6b-4bc03392afe9
- content_sha256: c318128df15019bea41c127ba0c7a83f9364399b40bba1d7500c050b8ca43bc8
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-25
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20f79-b639-7f82-8f6b-4bc03392afe9

---
結論：`changes_requested`，共 1 處更正。已核對內容雜湊，與派工值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   [數位時代原文](https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts)無法開啟，未能核對正文、圖片與留言。實際看過來源圖片 0 張、留言 0 則；平台留言計數未知。

   依本次規則，移除 `source` 審查範圍，保留作者的 `full` 聲明，不將讀取失敗列為更正。作者、發布日期與 Hassid 原話仍待來源道補核。

2. **事實查核（facts）**

   - 官方研究支持筆記所列 CL-Bench 分數、相對提升約 28%，以及寶可夢記憶案例；筆記已有區分案例觀察與因果證明。[研究原文](https://www.anthropic.com/research/components-of-agent-memory)
   - Projects 的帳號記憶開關、Google Workspace 測試版與檔案生成功能均有官方依據。[記憶說明](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)、[Workspace 說明](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)、[檔案生成](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)
   - 回饋資料最長保留 5 年、可能用於訓練，以及特定安全檢查造成模型切換，均有官方依據；筆記保留了適用限制。[隱私說明](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)、[模型切換說明](https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5)

   **更正 1：編輯原提問建立分支，缺少介面限制。**

   筆記第 50 行將編輯重送描述成可直接使用的分支操作，但官方目前明列：逐步推出的 Chat／Cowork 整合介面尚不支援從較早節點分支。這不代表舊介面也不支援；問題是筆記沒有區分適用介面。[官方新介面限制](https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude)

   建議改為：僅在介面提供編輯／分支功能時採用；已切換新整合介面的帳號，改整理確認資訊另開對話。

3. **證據分級（evidence）**

   - **一手已確認**：上述官方研究數據、功能與隱私規則。
   - **二手轉述**：105→26 條記憶、10 行摘要等 Hassid 建議；筆記已有標示待測。
   - **推算／未查證**：編輯分支比持續糾正更有效，屬策略判斷，沒有本機比較實測；應維持可選建議語氣。原文歸因待補讀，不因本次讀不到而新增 finding。

4. **任務與產出影響（task_impact）**

   唯一任務 `T-20261122-02` 目前未勾選完成，但產出檔已存在，已讀完。

   `docs/agent-memory-and-prompting-best-practices.md:76` 將 Claude Web／Desktop 的編輯分支操作概括適用，受更正 1 影響；第 64 行流程也須同步補上介面條件。由整合者修正，本次只回報。

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
      "claim": "筆記第 50 行將編輯使用者原提問後重送，描述為會建立新的對話分支，未區分介面。",
      "problem": "官方目前指出，逐步推出的 Chat／Cowork 整合介面尚不支援從較早節點建立分支；筆記缺少此適用限制。",
      "evidence": "https://support.claude.com/en/articles/16761823-claude-cowork-and-chat-are-one-claude",
      "fix": "註明僅適用於提供編輯／分支功能的介面；新整合介面改採整理已確認資訊另開對話，並同步修正任務步驟。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-02",
      "file": "docs/agent-memory-and-prompting-best-practices.md",
      "issue": "任務尚未勾選完成，但產出檔已存在。第 76 行概括 Claude Web／Desktop 可編輯建立分支，第 64 行流程亦依賴此功能；兩處須補上新整合介面尚不支援的限制。"
    }
  ]
}
```
