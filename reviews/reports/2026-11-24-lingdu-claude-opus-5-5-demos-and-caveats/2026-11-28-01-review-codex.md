# 獨立審查報告：2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats

- reviewer: codex/gpt-6.1-sol@01a22251-2bc7-79e0-903e-d8b97434229a
- content_sha256: 445fab325fde30df5c542e1488b8229af91bb80f9eddf0f8644d71c5fbdb795b
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 2；source_review: partial（作者聲明 partial）
- source_ref: codex thread 01a22251-2bc7-79e0-903e-d8b97434229a

---
結論：`changes_requested`，共 2 處證據表述需修正。筆記內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   已重新開啟[原始影片](https://youtu.be/sxny85UZr1A)，但只取得頁面外殼，無法讀取影片、字幕與留言。實際看過作者圖片 0 張、留言 0 則；平台留言計數無法取得。筆記所列 122 則尚未獨立確認。

   依交付規則，結果移除 `source` 範圍，保留作者的 `partial`，不把存取限制列為更正。影片日期、片長、觀看數、讚數及各時間點內容亦未核實，留待補審。

2. **事實查核（facts）**

   - **一手來源已確認**：Opus 5.5 已發布，官方預設 effort（推理用量）為 `medium`，定位包含長時間自主編碼。[官方模型文件](https://platform.claude.com/docs/en/models/opus-5-5/overview)
   - **一手來源已確認**：Claude 訂閱使用仍受用量限制，模型、effort、工具及多步驟工作都會影響用量；筆記對網頁版配額的勘誤有依據。[官方用量說明](https://support.claude.com/en/articles/9797557-usage-limit-best-practices)
   - **未查證**：個別示範的完成度、真實交通資料、留言實測時間、封號原因及網站 DNS 故障原因。筆記的留言編號無法取代可重讀的原留言證據。
   - **成本比較**：官方公告列有特定評測約五分之一成本的結果，不能據此證明或否定不同條件下的十分之一。筆記目前將十分之一列為未查證宣稱，處理合理。[官方公告](https://www.anthropic.com/claude-opus-5-5)

3. **證據分級（evidence）**

   **更正 1：effort 分流被寫成已獲支持的策略。**  
   筆記第 60 行由影片與個別留言推導固定的日常／總控分流，證據不足。官方要求以自身評測比較各 effort，沒有替這套固定分流背書。應改為「留言者的使用建議，尚未在本環境驗證」。[筆記](notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md)；[官方 effort 指引](https://platform.claude.com/docs/en/build-with-claude/effort)

   **更正 2：提示詞專業程度被寫成確定的品質原因。**  
   筆記第 50 行記錄觀眾看法，第 61 行卻升格為品質高度依賴專業提示詞的結論。文內未提供不同提示詞的對照實測，不能由觀眾評語確立因果。應改為「觀眾認為提示詞門檻高；其對品質的影響尚未驗證」。[筆記第 50、61 行](notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md)

4. **任務影響（task_impact）**

   本篇為 `archived`，沒有任務 ID 或已完成任務。交叉引用的 `docs/code-as-video-creative-patterns.md` 自述屬另一篇筆記的任務 `T-20261120-07`，不能算成本篇產出。本次無可列報的任務影響。

```json
{
  "verdict": "changes_requested",
  "source_review": "partial",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 2,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "evidence",
      "claim": "第 60 行將影片與留言視為既有 effort 分流策略的佐證。",
      "problem": "個別留言不足以驗證固定的日常 low、總控 medium 分流；官方要求依自身工作評測選擇。",
      "evidence": "notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md:51; notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md:60; https://platform.claude.com/docs/en/build-with-claude/effort",
      "fix": "標為留言者的使用建議，說明尚未在本環境驗證，不宣稱已印證分流策略。"
    },
    {
      "kind": "evidence",
      "claim": "第 61 行將專業提示詞列為成品品質的高度依賴因素。",
      "problem": "文內依據是觀眾評語，未提供提示詞對照實測，卻以確定語氣表述因果。",
      "evidence": "notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md:50; notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md:61",
      "fix": "改為觀眾認為提示詞門檻高，其對成品品質的影響尚未驗證。"
    }
  ],
  "task_impact": []
}
```
