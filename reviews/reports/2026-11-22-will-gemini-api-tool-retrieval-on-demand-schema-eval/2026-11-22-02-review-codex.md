# 獨立審查報告：2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval

- reviewer: codex/gpt-6.1-sol@01a203d2-d09a-7e12-a870-1ffa62081d62
- content_sha256: 220d7e8b6cc9fb47d8c6ff4c0976a002d34fa7c0902dbbcee363f873839b4083
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 7；source_review: full（作者聲明 full）
- source_ref: codex thread 01a203d2-d09a-7e12-a870-1ffa62081d62

---
**結論：`changes_requested`，共 7 處更正。** 筆記內容雜湊與指定值一致；未修改任何檔案。

### 1. 原始資料讀完度

不在本次範圍。未讀 Facebook 圖片與留言；官方 X 連結回傳 403。照抄作者聲明 `full`，不重新認證圖片、留言數與貼文時間；這些項目需 Chrome 道補讀。

### 2. 事實查核

- **F1 作者姓名錯字**：應為黃保翕。其所屬公司的[講師介紹](https://www.duotify.com/Training/Detail/32)可確認姓名與 MVP 身分。
- **F2 缺少介面限制**：功能仍為預覽，限 `v1beta` Interactions API；`generateContent` 不支援。[官方文件](https://aistudio.google.com/docs/tool-retrieval#limitations)
- **F3 模型範圍過度概括**：官方列出六個型號，不能延伸成所有較新版本皆支援。[支援清單](https://aistudio.google.com/docs/tool-retrieval#supported-models)
- **F4 計費說明不完整**：沒有獨立服務費，但搜尋會產生額外模型呼叫與輸入費用，並非工具越多就必然越省。[計費說明](https://aistudio.google.com/docs/tool-retrieval#pricing)
- **F5 快取效益寫成保證**：Interactions API 僅支援隱式快取（自動命中快取），仍有最低長度與命中條件。[快取文件](https://aistudio.google.com/docs/caching)

### 3. 證據分級

- **一手來源已確認**：`tool_search`、`defer_loading`、延後載入參數定義及遠端 MCP 整批延後載入。[官方機制說明](https://aistudio.google.com/docs/tool-retrieval)
- **二手來源**：Will 保哥對效益的評析，應明確歸因；本次未重新確認其原文。
- **推算／未查證**：
  - **F6**：每工具 Token 範圍、上下文占比及 MCP 台數門檻均缺少樣本與計算方式；「恆定」也與逐工具累加描述矛盾。
  - **F7**：低延遲、精準度顯著提高等結論缺少比較實測，不能當成通用保證。

### 4. 任務產出影響

唯一任務為 `T-20261122-04`，目前未勾選完成；但指定[產出文件已存在](/C:/GitHub/ai-inbox/docs/gemini-tool-retrieval-and-mcp-spec.md:3)，已全文檢查。

受影響處包括第 4、34 行的模型範圍，第 23～24、57、66 行的量化假設，以及第 59～60、68 行的快取與成本敘述。由整合者修正，不能以檔案存在視為驗收完成。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 7,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "frontmatter author 與正文作者姓名寫為黃保吸",
      "problem": "作者姓名末字錯誤；所屬公司講師介紹列為黃保翕。",
      "evidence": "https://www.duotify.com/Training/Detail/32",
      "fix": "將姓名統一改為黃保翕。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節第 3、4 點將加入 tool_search 描述為核心接入方式",
      "problem": "未交代必要的 API 限制，容易被理解為既有 Gemini API 呼叫均能直接套用。官方限定預覽版 v1beta Interactions API，generateContent 不支援。",
      "evidence": "https://aistudio.google.com/docs/tool-retrieval#limitations",
      "fix": "在機制與任務範圍補上預覽狀態、v1beta 與 Interactions API 限制，明列 generateContent 不支援。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節第 8 點以 Gemini 3.6 以上及所有 Gemini 4 概括支援範圍",
      "problem": "官方採型號清單，不能推論版本號較新就自動支援。",
      "evidence": "https://aistudio.google.com/docs/tool-retrieval#supported-models",
      "fix": "改列 gemini-4-carbon、gemini-4-neon、gemini-4-hydrogen、gemini-4-argon、gemini-3.8-flash、gemini-3.6-flash，並註明查核日期。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節第 7 點及比較表將成本效益歸結為省去未載入 Schema",
      "problem": "漏列搜尋的額外模型呼叫；完整上下文與載入 Schema 的提示 Token 會列入 total_tool_use_tokens 並按輸入費率計價。官方也指出部分情境靜態載入更便宜。",
      "evidence": "https://aistudio.google.com/docs/tool-retrieval#pricing",
      "fix": "區分無獨立服務費與搜尋仍有 Token 費用；成本比較納入搜尋次數、上下文長度及載入工具比例，刪除必然越多越省的推論。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節第 6 點與第 3 節快取建議將相容性寫成持續享有效益",
      "problem": "Interactions API 不支援顯式快取；隱式快取有最低長度與命中條件。前綴保持穩定不等於保證命中、折扣或低延遲。",
      "evidence": "https://aistudio.google.com/docs/caching",
      "fix": "改寫為相容隱式快取，但效益須依長度門檻及實際 usage.total_cached_tokens 判斷，避免保證語氣。"
    },
    {
      "kind": "evidence",
      "claim": "第 2、3 節的 Token 範圍、20%～40% 占比、50+ 工具及 2～3 台 MCP 門檻",
      "problem": "筆記未提供樣本、模型、Tokenizer、計算方式或實測來源，無法查證這些數字的通用性。工具名稱摘要仍隨工具數累加，不能稱為恆定負擔。",
      "evidence": "C:/GitHub/ai-inbox/notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md（第 2、3 節）",
      "fix": "刪除無依據數字，或標示為假設示例並補上計算條件；將恆定改為較小但仍隨工具數增加。"
    },
    {
      "kind": "evidence",
      "claim": "第 2 節比較表對冷啟動延遲與工具選擇精準度作出強效益判斷",
      "problem": "未提供相同模型、工具集與查詢集的比較測試，無法確認改善幅度，也不能保證所有情境都更快、更準。",
      "evidence": "C:/GitHub/ai-inbox/notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md（第 2 節比較表）",
      "fix": "改為可能改善的設計目標；若保留強結論，補上可重現的延遲與工具選擇正確率測試。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-04",
      "file": "docs/gemini-tool-retrieval-and-mcp-spec.md",
      "issue": "任務尚未勾選完成，但產出已存在。第 4、34 行沿用過廣的模型範圍且未交代 Interactions API 限制；第 23～24、57、66 行沿用未驗證的量化假設；第 59 行把快取效益寫成保證；第 60、68 行的成本模型漏算搜尋額外模型呼叫。需由整合者修正後再驗收。"
    }
  ]
}
```
