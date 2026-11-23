# 獨立審查報告：2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval

- reviewer: codex/gpt-6.1-sol@01a20a51-2e80-7d73-92ae-4c75759ab03f
- content_sha256: 745d620619e64795e4367f855708a990c2e110f6d5015ab8165bda999cd6ff4a
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-24
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20a51-2e80-7d73-92ae-4c75759ab03f

---
結論：`changes_requested`，共 1 處更正。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   原文網址無法開啟，未能核對正文、作者、日期、8 張圖片及留言。本次移除 `source` 範圍，保留作者的 `full` 聲明，不將讀取限制列為錯誤。實際看圖 0 張、留言未讀，貼文留言計數無法確認。

2. **事實查核（facts）**

   已確認以下內容符合官方資料：

   - Flow 每日 50 點，Pro 每月另加 1,000 點，未用點數不遞延。[官方說明](https://support.google.com/flow/answer/16526234?hl=en)
   - Gemini Notebook 有結構限制，以及每 5 小時更新、受每週上限約束的運算額度。[方案限制](https://support.google.com/gemininotebook/answer/16213268?hl=en)、[用量說明](https://support.google.com/gemininotebook/answer/17670842?hl=en)
   - Antigravity 超額點數設定位於 `Settings > Models`；新版權限預設與舊版設定的區分有官方依據。[設定](https://antigravity.google/docs/settings)、[權限](https://antigravity.google/docs/permissions)、[代理設定](https://antigravity.google/docs/agent-settings)
   - AI Pro 提高 AI Studio 指定模型用量；API 限流按專案而非 API Key 計算。[訂閱權益](https://support.google.com/googleone/answer/14534406?hl=en)、[API 限流](https://aistudio.google.com/docs/rate-limits)

   **更正 F1：API 計費單位概括過度。**  
   筆記第 1 節 AI Studio 列與第 2 節將 API 價格統稱為每百萬 token。官方價格頁也列有按張計費的圖片模型、按首計費的 Lyria，不能概括所有模型。建議改成「API 獨立計費；依模型與功能按 token、圖片或其他單位計價」。[官方價格頁](https://aistudio.google.com/docs/pricing)

3. **證據分級（evidence）**

   - **一手來源已確認**：上述訂閱權益、點數、額度、權限與 API 限流。
   - **二手來源、尚未複核**：報導中的操作案例、圖片解析與提示詞；原文讀取受限，本次不判其真偽。
   - **分析建議**：操作難度星級、工具分工及專案治理建議，屬筆記作者判斷，不是官方測試結果。

   F1 同一說法出現兩處，合計為 1 筆更正。

4. **任務產出影響（task_impact）**

   唯一任務 `T-20261122-03` 仍未勾選，沒有已完成任務。已額外讀取現存產出 `docs/google-ai-pro-ecosystem-and-credit-routing.md`：第 1 節 AI Studio 列也概括為每百萬 Token 計價，第 2.1 節第 4 點亦只描述輸入／輸出 Token 計費，應由整合者一併限定適用範圍。

下一步：修正計費描述，並另派可讀取原文與圖片的審查者補完 `source`。

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
      "claim": "第1節AI Studio列與第2節將Gemini API價格概括為每百萬token計算",
      "problem": "未限定模型與功能；官方價格頁也列有按張計費的圖片模型及按首計費的Lyria，不能將所有API計費概括為同一單位。",
      "evidence": "https://aistudio.google.com/docs/pricing",
      "fix": "改為API獨立計費，依模型與功能按token、圖片或其他單位計價；每百萬token的描述只用於適用模型。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-03",
      "file": "docs/google-ai-pro-ecosystem-and-credit-routing.md",
      "issue": "任務尚未勾選，但產出已存在。第1節AI Studio列概括為每百萬Token計價，第2.1節第4點亦只描述Input／Output Tokens計費；須同步限定適用模型與功能。"
    }
  ]
}
```
