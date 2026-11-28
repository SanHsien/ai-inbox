# 獨立審查報告：2026-11-25-google-procedural-graphs-self-evolving-agents

- reviewer: codex/gpt-6.1-sol@01a22256-d10d-7752-9452-83ad88552491
- content_sha256: 5f95a0af3dacf2eaddc93f70919a783537c595bb758e4ea0bf2eab306bf24c80
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 5；source_review: partial（作者聲明 partial）
- source_ref: codex thread 01a22256-d10d-7752-9452-83ad88552491

---
結論：`changes_requested`，共 5 處更正。未修改任何檔案；審查前後內容雜湊均符合指定值。

1. **原始資料讀完度（source）**

   已讀論文文字與相關表格，但工具未傳回可檢視的圖像，無法確認全部 6 張圖。因此移除本次 `source` 範圍，保留作者的 `partial`，不把讀取限制列為筆記錯誤。實際看過圖片 0 張、留言 0 則；arXiv 論文頁無留言串。

2. **事實查核（facts）**

   - **F1｜第 43 行：屬性位置寫錯。** 論文把 `condition`、`guidance`、`pitfalls` 定義為**邊的屬性**，不是節點與邊都有。應修正資料結構描述。[論文 §3.1](https://arxiv.org/html/2609.09153v1#S3.SS1)
   - **F2｜第 45 行：局部擷取缺少例外。** 節點配對成功才取局部鄰域；失敗時使用全圖。應補上退回全圖的分支。[論文 §3.2](https://arxiv.org/html/2609.09153v1#S3.SS2)
   - **F3｜第 51 行：混用輪次、資料集與指標。** 85% 是最終回傳圖譜的測試集存活率；17.23→3.08 是第 2 輪驗證集的每月**全部工具呼叫**，不是重複呼叫的獨立計數。該輪驗證存活率為 80%。應拆開陳述。[論文 §5.4、附錄 E 表 11](https://arxiv.org/html/2609.09153v1#A5)
   - **F4｜第 58 行：Harness² 對照過度概括。** 它沒有 PG 的保留驗證集分數守門，但已有候選執行比較、保留原設定，以及記錄有害修改的反思。應比較兩者的判定依據，不能概括為沒有拒絕記憶。[Harness² §2.2–2.3、附錄 H](https://arxiv.org/html/2610.14224v1#S2)

3. **證據分級（evidence）**

   - **一手來源確認**：作者、機構、三元組架構、不更新權重、驗證守門與拒絕記憶，均有論文支持。
   - **二手實測**：issue #201 的結果是第三方移植後自述；筆記已標第三方，不能延伸成 Harness² 普遍無效。[原始回報](https://github.com/google-research/harness2/issues/201)
   - **F5｜第 31 行：官方開源狀態證據不足。** 社群重實作確實存在，但其 README 對官方程式碼狀態的說法仍是第三方聲明。應改為「本次未找到作者官方程式碼連結」，或補作者公告；目前無法確認「尚未釋出」這個全面斷言。[社群 README](https://github.com/vikm2o/proceduralgraph#readme)
   - **工程推論**：套用到本地 Skill 與規則迭代屬建議，尚未實測；不應當成已證明的改善效果。

4. **任務影響（task_impact）**

   唯一任務 `T-20261125-04` 尚未完成，沒有已完成產出需要追修。目標文件 `docs/harness2-recursive-agent-harnessing-spec.md` 尚無本篇 PG 對照節；整合者應先修正上述前提再補入。

```json
{
  "verdict": "changes_requested",
  "source_review": "partial",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 5,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第43行將三個文字屬性同時配置於節點與邊",
      "problem": "論文的屬性映射將 condition、guidance、pitfalls 配置於邊。",
      "evidence": "https://arxiv.org/html/2609.09153v1#S3.SS1",
      "fix": "改為邊附帶三個文字屬性；節點代表工具、技能、推理步驟或任務狀態。"
    },
    {
      "kind": "fact",
      "claim": "第45行將線上導引描述為只抽取局部子圖",
      "problem": "省略節點配對失敗時使用全圖的分支。",
      "evidence": "https://arxiv.org/html/2609.09153v1#S3.SS2",
      "fix": "註明成功配對時取2-hop鄰域，失敗時使用全圖。"
    },
    {
      "kind": "fact",
      "claim": "第51行合併85%存活率與17.23降至3.08的重複工具呼叫數",
      "problem": "85%屬最終回傳圖譜的測試結果；17.23至3.08屬第2輪驗證集全部工具呼叫的月平均，該輪驗證存活率為80%。",
      "evidence": "https://arxiv.org/html/2609.09153v1#A5",
      "fix": "拆開最終測試存活率與第2輪驗證效率數據，將重複工具呼叫次數改為平均工具呼叫次數。"
    },
    {
      "kind": "fact",
      "claim": "第58行概括Harness²缺乏驗證守門與拒絕記憶",
      "problem": "它缺少PG式保留驗證集分數守門，但已有候選執行比較、保留原設定及有害修改反思，不能概括為沒有負向經驗機制。",
      "evidence": "https://arxiv.org/html/2610.14224v1#S2 ; https://arxiv.org/html/2610.14224v1#A8",
      "fix": "比較PG的驗證分數與拒絕候選紀錄，以及Harness²的行為對照與反思經驗，限縮缺口描述。"
    },
    {
      "kind": "evidence",
      "claim": "第31行斷言作者尚未釋出官方倉庫",
      "problem": "可確認社群重實作存在，但其對官方程式碼狀態的描述屬第三方聲明；目前沒有作者一手證據支持全面斷言。",
      "evidence": "https://github.com/vikm2o/proceduralgraph#readme ; https://arxiv.org/abs/2609.09153",
      "fix": "改為本次未找到作者官方程式碼連結，或補作者公告及查證日期。"
    }
  ],
  "task_impact": []
}
```
