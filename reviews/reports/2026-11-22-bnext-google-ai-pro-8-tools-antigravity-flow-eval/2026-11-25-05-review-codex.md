# 獨立審查報告：2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval

- reviewer: codex/gpt-6.1-sol@01a20f7b-9b2b-7261-a92b-0a05ad41a64d
- content_sha256: a0fc6b527a485100cc03989669b1be78f805a18b46c43a98c3151d08bcf24dc4
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-25
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20f7b-9b2b-7261-a92b-0a05ad41a64d

---
結論：`changes_requested`，共 1 處更正。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   [原始報導](https://www.bnext.com.tw/article/93098/google-ai-pro-8-tools-features-tutorial)及文章編號短網址皆無法開啟，無法核實正文、作者、發布日期、8 張圖片及留言計數。實際看圖 0 張，留言未讀。

   本次移除 `source` 範圍，保留作者的 `full` 聲明；存取失敗不列更正，另派可讀來源者補審。

2. **事實查核（facts）**

   下列主要說法與目前官方資料相符：

   - Flow 每日 50 點，Pro 每月另加 1,000 點，未用點數不遞延。[Flow 官方說明](https://support.google.com/flow/answer/16526234?hl=en)
   - 另購 AI 點數可增加 Gemini、Flow、Antigravity 用量；Antigravity 超額開關位於 `Settings > Models`。[Google One 說明](https://support.google.com/googleone/answer/16287445?hl=en)、[Antigravity 設定](https://antigravity.google/docs/settings)
   - Gemini Notebook 採運算用量限制，每 5 小時更新，另有每週上限。[官方用量說明](https://support.google.com/gemininotebook/answer/17670842?hl=en)
   - AI Pro 提供 AI Studio 指定模型較高用量；API 限流按專案計算，價格依模型與功能採不同單位。[訂閱權益](https://support.google.com/googleone/answer/14534406?hl=en)、[API 限流](https://aistudio.google.com/docs/rate-limits)、[價格頁](https://aistudio.google.com/docs/pricing)
   - Antigravity 四種權限預設及舊版跨工作區設定有官方依據；專用資料夾本身不構成安全隔離。[權限文件](https://antigravity.google/docs/permissions)、[代理設定](https://antigravity.google/docs/agent-settings)

   未確認原文案例是否確實出現在報導，不替這部分背書。

3. **證據分級（evidence）**

   - **一手確認**：上述配額、點數、API 與權限機制。
   - **二手轉述**：8 張圖片案例已明標報導案例、未獨立實測，分級適當。
   - **更正 E1**：第 1 節工具矩陣的星等難度未標明評分者或依據。矩陣置於報導解構段落，容易被視為報導評分或實測結果；本筆記任務步驟 4 也已要求標明這類作者分析。建議在表前註明「操作難度為筆記作者主觀評估，非官方評級或獨立實測」。出處：`notes/2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval.md` 第 1 節、任務步驟 4。

4. **任務影響（task_impact）**

   本篇只有 `T-20261122-03`，仍未完成，沒有已完成任務可追溯。

   已存在的 `docs/google-ai-pro-ecosystem-and-credit-routing.md` 仍有兩項待修：第 1 節將 API 付費層概括成每百萬 token 計價；第 2.1 節第 4 點又概括成輸入／輸出 token 計費。官方價格頁另有圖片、歌曲等計價單位。筆記已將此修正納入待辦，整合者應完成後再結案；不另計筆記更正數。

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
      "claim": "第 1 節工具矩陣列出操作難度星等。",
      "problem": "未標明評分者或依據，也未區分作者主觀評估與報導或實測結果。",
      "evidence": "notes/2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval.md：第 1 節工具矩陣及 T-20261122-03 執行步驟 4",
      "fix": "在表前標明操作難度為筆記作者主觀評估，非官方評級或獨立實測；若轉引報導評分，則補明確出處。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-03",
      "file": "docs/google-ai-pro-ecosystem-and-credit-routing.md",
      "issue": "任務仍未完成，但既有產出第 1 節 AI Studio 列與第 2.1 節第 4 點仍將 API 計價概括為 token 計費；應依 https://aistudio.google.com/docs/pricing 區分模型與功能的計價單位。此修正已列入筆記待辦，完成前不宜結案。"
    }
  ]
}
```
