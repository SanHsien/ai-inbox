# 獨立審查報告：2026-11-26-claude-long-thread-pr-intent-drift-prompt

- reviewer: codex/gpt-6.1-sol@01a2225e-d175-76b2-a7c7-8c203ff690a1
- content_sha256: f9d0d85e74f8f26cf01f170ec2afbbdb07151b8e5987a432e1a80e27a7c28a2c
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 2；source_review: unavailable（作者聲明 unavailable）
- source_ref: codex thread 01a2225e-d175-76b2-a7c7-8c203ff690a1

---
結論：`changes_requested`，共 2 處更正。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   已開啟[指定來源](https://github.com/SanHsien/ai-inbox)，但它是收件匣首頁，無法獨立核對使用者提供提示詞的原始對話。以提示詞關鍵片語搜尋，也未找到可核對的原始發布頁。

   原圖、留言總數與實際內容均無法確認。本次移除 `source` 範圍，保留作者的 `unavailable`，不列為錯誤。

2. **事實查核（facts）**

   筆記對提示詞的四項文字要求，大致符合檔內所載句意；原始作者與提供日期無法獨立確認。[AGENTS.md](AGENTS.md:154) 確實要求主動揭露中途變更。

   但「要求依時序解說」不能證明模型會忠實還原內部決策。Anthropic 的[官方研究](https://www.anthropic.com/research/tracing-thoughts-language-model)指出，模型可能產生看似合理、卻不反映實際推理的解釋；該研究不是這句提示詞的效果測試。

3. **證據分級（evidence）**

   - **更正 1：[筆記第 42、44 行](notes/2026-11-26-claude-long-thread-pr-intent-drift-prompt.md:42)**  
     白話敘事能迫使模型還原因果決策、揭露隱藏問題的說法，屬**推算／未查證**。應改成預期用途，並要求以程式碼、測試與執行紀錄核對；不得將模型敘事當成真實決策證據。依據同上官方研究。

   - **更正 2：[筆記第 48 行](notes/2026-11-26-claude-long-thread-pr-intent-drift-prompt.md:48)**  
     行內粗體只是呈現格式，不能保證找出全部偏離。筆記未提供漏報測試或完整覆蓋證據。應改成「方便定位已辨識的偏離」，並將最新需求與實際差異列為必要輸入。[官方文件](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)也要求用來源核對主張、允許資訊不足，不能只靠提示格式保證正確。

   檔內提示詞屬使用者轉交材料；上述效果尚未經測試。專案規則則有本地一手文件可核對。

4. **已完成任務的產出檔（task_impact）**

   唯一任務 `T-20261126-04` 尚未完成，目標為 `docs/agent-memory-and-prompting-best-practices.md`。已開啟該檔，未見本任務要求新增的小節；沒有已完成產出受影響。整合者應先修正效果宣稱，再收錄提示詞。

```json
{
  "verdict": "changes_requested",
  "source_review": "unavailable",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 2,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "evidence",
      "claim": "第 42、44 行將白話時序敘事描述為能還原真實決策並揭露隱藏問題。",
      "problem": "將提示詞的預期作用寫成已確認效果，未提供實測；模型的敘事也不能直接視為內部決策證據。",
      "evidence": "notes/2026-11-26-claude-long-thread-pr-intent-drift-prompt.md:42-44；https://www.anthropic.com/research/tracing-thoughts-language-model",
      "fix": "標示為設計推論、尚未實測；要求以程式碼、測試及執行紀錄核對敘事。"
    },
    {
      "kind": "evidence",
      "claim": "第 48 行將行內粗體描述為足以定位全部範圍外改動或意圖偏離。",
      "problem": "呈現格式不能證明偵測完整性，筆記沒有漏報測試或覆蓋證據。",
      "evidence": "notes/2026-11-26-claude-long-thread-pr-intent-drift-prompt.md:48；https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations",
      "fix": "改成方便定位已辨識的偏離；要求提供最新需求、實際差異與逐項證據，資訊不足時明示限制。"
    }
  ],
  "task_impact": []
}
```
