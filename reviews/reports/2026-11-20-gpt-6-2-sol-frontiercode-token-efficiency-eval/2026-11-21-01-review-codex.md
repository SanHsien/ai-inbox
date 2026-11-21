# 獨立審查報告：2026-11-20-gpt-6-2-sol-frontiercode-token-efficiency-eval

- reviewer: codex/gpt-6.1-sol@01a1fcb9-6070-7fc1-9407-2a5b4823514b
- content_sha256: 18bac7ec5a0e7f4707071c9a7c8af6299b9b413ac0bce0223d715c96f4e06b2a
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-21
- verdict: changes_requested；corrections: 5；source_review: full（作者聲明 full）
- source_ref: codex thread 01a1fcb9-6070-7fc1-9407-2a5b4823514b

---
結論：`changes_requested`，共 5 處更正。未修改任何檔案。

審查內容雜湊已確認相符：`18bac7ec5a0e7f4707071c9a7c8af6299b9b413ac0bce0223d715c96f4e06b2a`。

### 1. 原始資料讀完度

[原始文章](https://www.woshipm.com/ai/6496545.html)讀取失敗，無法核對正文、作者、發布日期、3 張圖片及留言計數。

依交付規則，本次排除 `source`，保留作者的 `full` 聲明，不因讀取限制列更正。實際看過作者圖片 0 張、留言 0 則；不代表來源沒有圖片或留言。

### 2. 事實查核

- **FrontierCode**：官方確認 Sol 與 Astra 相差不到 0.5 個百分點，成本約五分之一，且**兩者皆為 max 設定**。筆記漏寫設定，會讓數字被誤用於其他推理強度。按筆記金額計算，成本減少約 78.39%，其 78% 近似值合理。[OpenAI 公告](https://openai.com/index/introducing-gpt-6-2-astra-sol/)
- **AA-3D**：Astra 1318、Sol 1259、Opus 5.5 1202，均與評測方排行榜相符。[Artificial Analysis 排行榜](https://artificialanalysis.ai/evaluations/aa-3d)
- **Higgsfield 73%**：官方引述明確指向 **GPT-6.2 Astra**，屬合作方內部測試自述。筆記未標模型，放在 Sol 評估脈絡下容易誤認。[OpenAI 公告 Higgsfield 段落](https://openai.com/index/introducing-gpt-6-2-astra-sol/)
- **Agents’ Last Exam 與 GDPval 精確數字**：本次取得的官方文字未提供全部數值，不能將搜尋到的轉述升格為一手確認。官方另註明 Fable 的 Agents’ Last Exam 成績排除了 9 個使用備援模型的任務，筆記比較時須補此限制。[OpenAI 公告](https://openai.com/index/introducing-gpt-6-2-astra-sol/)

### 3. 證據分級與更正

1. FrontierCode 比較補上雙方 `max` 設定。
2. Higgsfield 73% 明確歸屬 Astra，並標為合作方內部自述。
3. Agents’ Last Exam 比較補上 Fable 排除備援任務的限制；精確數字補可複核的一手圖表。
4. GDPval 的 Token 數字目前只能列未完成一手核對；「6 至 10 倍」也混合不同設定。依筆記數字，3.3 萬對應約 5.79–6.73 倍，1.88 萬對應約 10.16–11.81 倍，應分列。
5. 從評測輸出量直接推論對話上下文、終端轉錄及解析延遲都減少，缺乏本機量測；應改為待驗證假設。

「少於 20 個檔案、10 分鐘內」未找到官方驗證，應保留為來源作者建議，不能當成已驗證的模型能力邊界。

### 4. 任務影響

唯一任務 `T-20261120-06` 尚未完成。

已讀取其目標檔 `docs/model-burn-rate-routing-matrix.md`，未找到本篇的 GPT-6.2、FrontierCode 或 Token 數字已被納入，因此沒有已完成產出需要回報修正。下一步由整合者修正筆記，再補原始來源審查。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 5,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "evidence",
      "claim": "第 1 節 FrontierCode 的模型得分與單任務成本比較",
      "problem": "漏寫 Astra 與 Sol 都使用 max 推理設定，不能直接套用到其他設定。",
      "evidence": "https://openai.com/index/introducing-gpt-6-2-astra-sol/",
      "fix": "標明兩者皆為 max，並補官方圖表來源及查閱日期。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節 Higgsfield 的 3D 一次通過率 73%",
      "problem": "官方引述指的是 GPT-6.2 Astra；筆記未標模型，置於 Sol 評估脈絡下容易誤認。此數字也是合作方內部測試自述。",
      "evidence": "https://openai.com/index/introducing-gpt-6-2-astra-sol/",
      "fix": "明寫模型為 Astra，標註 Higgsfield 內部自述，不作為 Sol 能力證據。"
    },
    {
      "kind": "evidence",
      "claim": "第 1 節 Agents’ Last Exam 的 Sol 與 Claude 成績比較",
      "problem": "未交代官方註明 Fable 成績排除了 9 個使用備援模型的任務；本次也未從一手文字核對完整精確數字。",
      "evidence": "https://openai.com/index/introducing-gpt-6-2-astra-sol/",
      "fix": "補比較條件、推理設定及可複核的一手圖表；取得前將精確數字標為轉述、未完成一手核對。"
    },
    {
      "kind": "evidence",
      "claim": "第 1 節 GDPval Token 數字與 6 至 10 倍結論",
      "problem": "精確 Token 數字未完成一手核對，且混合不同設定的比值。依筆記數字計算，3.3 萬對應 5.79–6.73 倍，1.88 萬對應 10.16–11.81 倍。",
      "evidence": "notes/2026-11-20-gpt-6-2-sol-frontiercode-token-efficiency-eval.md，第 1 節；https://openai.com/index/introducing-gpt-6-2-astra-sol/",
      "fix": "補一手圖表與設定，分列比值並標為推算；避免將較少輸出描述為已驗證的壓縮機制。"
    },
    {
      "kind": "evidence",
      "claim": "第 2 節將較少輸出直接推論為上下文、轉錄及解析延遲的改善",
      "problem": "筆記未提供對話歷程、轉錄量或延遲量測；評測輸出量本身不足以證明這些本機效益。",
      "evidence": "notes/2026-11-20-gpt-6-2-sol-frontiercode-token-efficiency-eval.md，第 2 節",
      "fix": "改寫為可能效益、尚未驗證，並說明實際效果取決於工具輸出、歷程保留及執行環境。"
    }
  ],
  "task_impact": []
}
```
