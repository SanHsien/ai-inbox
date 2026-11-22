# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a20284-0b88-7351-91c2-f2a463c563a4
- content_sha256: 8844b559dd06eb38d84e099d24bedbaf5b35d41581582f5ecd58f82b55ae8a1b
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 5；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20284-0b88-7351-91c2-f2a463c563a4

---
結論：`changes_requested`，共 5 處更正。未修改任何檔案；內容雜湊與指定值一致。

### 1. 原始資料讀完度（source）

[數位時代原文](https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts)無法開啟，因此未完成正文、圖片與留言核對。

本次移除 `source` 審查範圍，保留作者的 `full` 聲明，不把讀取受阻列為錯誤。實際看過作者圖片 0 張、留言 0 則；留言計數無法取得。

### 2. 事實查核（facts）

已確認：

- 官方研究發布於 2026-11-06；Opus 5.5 的 CL-Bench 資料庫任務分數為 0.655 → 0.838，相對增幅約 27.94%。筆記限定為 Managed Agents 評測，這點正確。[官方研究](https://www.anthropic.com/research/components-of-agent-memory)
- Project 可關閉 `Use account memory`。[官方記憶說明](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)
- Google Workspace 側邊欄、GitHub 檔案整合與 Word／Excel／PDF 生成確有官方功能。[Workspace](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)、[GitHub](https://support.claude.com/en/articles/10167454-use-the-github-integration)、[檔案生成](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude)

須更正的事實包括：10 檔並非通關紀錄，以及回饋資料並非必然用於訓練。詳見下方 findings。

### 3. 證據分級（evidence）

- **一手來源已確認**：上述功能、研究日期、分數與遊戲紀錄。
- **二手轉述**：Hassid 的記憶整理、10 行摘要與其他操作建議；本次未取得其原稿，不能視為官方實證。
- **推算／未查證**：檔案越多必然造成效能下降、反問即可解決幻覺、所有答錯情況都應重開分支。這些結論超出現有證據。

### 4. 任務影響（task_impact）

唯一任務 `T-20261122-02` 尚未完成；預定產出 `docs/agent-memory-and-prompting-best-practices.md` 不存在，沒有已完成產出可追查。

該任務將記憶比較與 Edit 操作寫成標準流程，實作前應先修正下列前提，再送審。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 5,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "evidence",
      "claim": "第1節技巧2將記憶膨脹造成檢索噪訊寫成已證實的規律。",
      "problem": "官方比較的是不同模型各一次的遊戲紀錄，並指出過時、重複資訊造成維護負擔；沒有控制模型能力以單獨驗證檔案數的因果效果。",
      "evidence": "https://www.anthropic.com/research/components-of-agent-memory",
      "fix": "改為案例觀察：避免保存可直接取得、容易過時的狀態，保留策略與驗證過的規則；勿宣稱檔案較少必然較好。"
    },
    {
      "kind": "fact",
      "claim": "第2節把約10個記憶檔描述為通關案例。",
      "problem": "約10檔是 Fable 5 的紀錄，取得4枚徽章；通關的是 Opus 5.5，官方只說其記憶資料夾精簡，未提供相同檔案數。",
      "evidence": "https://www.anthropic.com/research/components-of-agent-memory",
      "fix": "分開寫 Fable 5 的10檔與4枚徽章，以及 Opus 5.5 精簡筆記並通關的紀錄。"
    },
    {
      "kind": "evidence",
      "claim": "第1節技巧4要求答錯後不要連續糾正，並以 Edit 重置作為正確做法。",
      "problem": "上下文污染有研究支持，但不足以推出一律禁止後續糾正。Anthropic 官方文件也建議透過後續提示檢查及修正回答；編輯重試是建立分支，不能籠統描述為重置全部上下文。",
      "evidence": "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations ; https://www.anthropic.com/research/end-subset-conversations",
      "fix": "改成可選策略：反覆受錯誤前提影響時，可編輯原提問重試或整理已確認資訊另開對話；保留直接糾正的適用情境，並明確指出編輯的是原提問。"
    },
    {
      "kind": "evidence",
      "claim": "第1節技巧7把要求模型先反問描述為能打破幻覺。",
      "problem": "先反問有助補齊需求，但沒有查到該句提示能保證解決幻覺的一手證據。官方仍要求允許不確定、依據來源與核對引用。",
      "evidence": "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations",
      "fix": "改為有助減少資訊不足時的猜測，不能保證消除幻覺；事實仍須查證。"
    },
    {
      "kind": "fact",
      "claim": "第1節技巧16將提交回饋後的對話描述為會用於模型訓練。",
      "problem": "官方區分保留與用途：相關完整對話最長保留5年，但訓練用途是可能使用，並非每筆必然使用。",
      "evidence": "https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training",
      "fix": "改為提交回饋可能使相關完整對話保留最長5年，並可能用於研究及模型訓練。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-02",
      "file": "docs/agent-memory-and-prompting-best-practices.md",
      "issue": "任務尚未完成，檔案不存在。執行步驟1、2預計將跨模型記憶比較及 Edit 操作納入標準流程，應先修正因果推論並補充適用條件。"
    }
  ]
}
```
