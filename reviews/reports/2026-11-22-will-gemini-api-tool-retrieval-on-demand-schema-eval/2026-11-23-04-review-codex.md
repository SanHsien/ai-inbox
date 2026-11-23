# 獨立審查報告：2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval

- reviewer: codex/gpt-6.1-sol@01a2089b-24d0-7f53-a807-fff881aacbeb
- content_sha256: 316adfaec19447b7d29af536bd3300f76c64cb4837732d2c4bbb7b6db753e4e5
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-23
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）
- source_ref: codex thread 01a2089b-24d0-7f53-a807-fff881aacbeb

---
結論：**changes_requested，共 3 處更正**。已完成 `facts`、`evidence`、`task_impact` 審查；未修改任何檔案。

### 1. 原始資料讀完度

不在本次範圍。未重讀 Facebook 圖片與留言，沿用作者的 `source_review: full`，不替作者重新背書。官方 X 連結回傳 403，其貼文內容無法獨立確認；需 Chrome 道補讀。

### 2. 事實查核

預覽狀態、API 限制、六款支援型號、遠端 MCP 與搜尋計費說明均與目前官方文件一致。以下兩處需更正：

- **F1：待命摘要不等於完整描述。** 筆記第 1 節第 2 點與架構表未說明截短規則。官方規定初始計入名稱及 `short_description`；未設定時只取 `description` 第一句。建議明列此規則，避免描述長度與成本估算失準。[官方計費說明](https://aistudio.google.com/docs/tool-retrieval#pricing)
- **F2：顯式快取仍受模型限制。** 第 2 節把 `generateContent` 概括成支援兩種快取，漏掉 Gemini 4 不支援顯式快取。應限定為支援顯式快取的 Gemini 3／2.5 模型。[官方快取文件](https://aistudio.google.com/docs/caching?generate-content=true)

### 3. 證據分級

- **一手已確認**：上述 API、模型、計費與快取規格；作者姓名與 MVP 身分亦有[講師介紹](https://www.duotify.com/Training/Detail/32)支持。
- **二手轉述**：Will 保哥對延遲、選錯工具及省費的評論。筆記已有標示；本次未獨立確認社群原文。
- **推算需修正（F3）**：第 3 節把高頻使用與每輪重新搜尋連結，並概括為雙倍上下文計費。官方指出，已載入工具會留在對話中；高頻呼叫不等於高頻搜尋。應區分：
  
  ```text
  工具使用頻率 ≠ 新搜尋頻率 → 依實際用量估算成本
  ```

  冷熱分層可保留為建議，但須補上跨輪保留條件，移除固定倍數暗示。[官方限制](https://aistudio.google.com/docs/tool-retrieval#limitations)

發布時間的 Unix 秒數換算正確；它是否確實來自該貼文，留待來源審查確認。

### 4. 任務與產出影響

唯一任務 `T-20261122-04` 仍未勾選完成，沒有已完成任務可驗收。但其[規格文件](/C:/GitHub/ai-inbox/docs/gemini-tool-retrieval-and-mcp-spec.md)已存在，須由整合者同步修正：

- 第 2.1 節第 3 列、第 3.1 節第 2 點：補上摘要截短規則。
- 第 3.1 節第 1 點：補上已載入工具跨輪保留，區分使用機率與搜尋機率。

下一步：修正筆記與相關規格後送再審。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第1節第2點及第2節：待命工具僅載入名稱與描述",
      "problem": "未交代描述的截短規則，容易被理解為完整 description 都進入初始上下文。",
      "evidence": "https://aistudio.google.com/docs/tool-retrieval#pricing",
      "fix": "明列使用 short_description；未設定時僅取 description 第一句。"
    },
    {
      "kind": "fact",
      "claim": "第2節快取比較列：generateContent 支援兩種快取",
      "problem": "缺少模型限制；Gemini 4 不支援顯式快取。",
      "evidence": "https://aistudio.google.com/docs/caching?generate-content=true",
      "fix": "限定顯式快取適用於支援它的 Gemini 3／2.5 模型，補註 Gemini 4 僅支援隱式快取。"
    },
    {
      "kind": "evidence",
      "claim": "第3節第1點：高頻工具每輪搜尋造成雙倍計費",
      "problem": "已載入工具會留在對話中，使用頻率不能直接當成搜尋頻率；雙倍費用也不是通用結論。",
      "evidence": "https://aistudio.google.com/docs/tool-retrieval#limitations ; https://aistudio.google.com/docs/tool-retrieval#pricing",
      "fix": "補上跨輪保留條件，分開估算工具使用與新搜尋頻率，將固定倍數改成依實際用量評估。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-04",
      "file": "docs/gemini-tool-retrieval-and-mcp-spec.md",
      "issue": "任務尚未完成，但文件已存在。第2.1節第3列與第3.1節第2點須補摘要截短規則；第3.1節第1點須補跨輪保留，區分使用機率與搜尋機率。"
    }
  ]
}
```
