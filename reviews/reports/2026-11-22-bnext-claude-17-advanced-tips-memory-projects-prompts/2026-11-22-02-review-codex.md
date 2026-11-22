# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: codex/gpt-6.1-sol@01a203b3-c392-7960-b345-8495cb5d6585
- content_sha256: a85821d88ff3a9a406e48d0ee7c1c5758293dc68288e1e845999647cb8b6b9a4
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a203b3-c392-7960-b345-8495cb5d6585

---
結論：`changes_requested`，共 **1 處更正**。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   [數位時代原文](https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts)無法開啟，未讀到正文、圖片與留言，也無法取得留言計數。本次移除 `source` 範圍，保留作者的 `full` 聲明，不據此列更正。

2. **事實查核（facts）**

   - 官方研究支持日期、CL-Bench 得分 `0.655 → 0.838`，相對增加約 **27.94%**；筆記已限制適用情境。
   - 寶可夢案例的檔案數、資料夾數、徽章數及 Opus 5.5 通關描述符合官方文章。以下實驗次數表述需縮小。[官方研究](https://www.anthropic.com/research/components-of-agent-memory)
   - Projects 關閉帳號記憶的設定符合[官方說明](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)。
   - 回饋資料最長保留五年、可能用於訓練及使用前脫鉤身分的描述，符合[官方隱私說明](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training)。

3. **證據分級（evidence）**

   **更正 1：單次實驗的範圍擴大到第三個模型。**

   筆記第 47、82 行把三個模型合稱「各一次」。官方只明確說 Sonnet 3.7、Fable 5 各取一次、約一萬步時的紀錄；另述 Opus 5.5 使用精簡筆記通關，未交代其實驗次數。不能把未公布的次數寫成已確認。

   建議改成：Sonnet 3.7 與 Fable 5 的比較各取一次紀錄；Opus 5.5 為另述案例，實驗次數未公布。保留非因果證明的提醒。[出處：官方研究相關段落](https://www.anthropic.com/research/components-of-agent-memory#:~:text=We%20compared%20the%20memory%20folders)

   其餘分級：
   - **一手已確認**：上述研究數字、記憶設定、隱私條款；後續提示修正及防幻覺限制也符合[官方指引](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)。
   - **二手轉述**：十行摘要、105→26 條記憶，筆記已標待測；本次未能核對原文。
   - **實務建議**：反問、批判提問、多樣性限制等，不視為已量化驗證的效果。

4. **任務產出影響（task_impact）**

   唯一任務 `T-20261122-02` 仍為未完成，沒有已完成任務需要追溯。不過其產出文件已存在並已讀取：[文件第 40 行](/C:/GitHub/ai-inbox/docs/agent-memory-and-prompting-best-practices.md:40)同樣將三個模型描述為各跑一次，應由整合者一併修正。產出存在不代表任務已驗收。

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
      "kind": "evidence",
      "claim": "筆記第 47、82 行將 Sonnet 3.7、Fable 5 與 Opus 5.5 的案例統稱為不同模型各一次紀錄。",
      "problem": "官方只明確說 Sonnet 3.7 與 Fable 5 各取一次、約一萬步時的紀錄；Opus 5.5 的實驗次數未公布，不能一併視為已確認。",
      "evidence": "https://www.anthropic.com/research/components-of-agent-memory#:~:text=We%20compared%20the%20memory%20folders",
      "fix": "限定 Sonnet 3.7 與 Fable 5 各取一次紀錄；將 Opus 5.5 通關列為另述案例，註明實驗次數未公布，並保留非因果證明的提醒。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-02",
      "file": "docs/agent-memory-and-prompting-best-practices.md",
      "issue": "任務仍未完成，但既有產出第 40 行將三個模型都描述為各跑一次，沿用了同一項未獲完整支持的實驗次數主張；請整合者同步修正。"
    }
  ]
}
```
