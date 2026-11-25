# 獨立審查報告：2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval

- reviewer: claude/opus-5.5@498c74d5-8c16-46e8-9fdc-3a900cc320b6
- content_sha256: d8c4e4adaf1e44205f20567d5f173066817d71738ffdeae7d46c8d9ec0015ad9
- role: audit；lane: chrome；scope: source, facts, evidence, task_impact
- reviewed_at: 2026-11-25
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）

---
# 強模型覆核報告：2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval

- 角色：audit；範圍：source、facts、evidence、task_impact
- 審查者：Claude（Chrome 道，Facebook 已登入）
- 查核日期：2026-11-25

## 1. 原始資料讀完度（source）

- 開 `https://www.facebook.com/will.fans/posts/1606150151539068/`，讀完貼文全文（約 20 行）。逐句比對筆記第 1 段轉述：痛點三項、「留在待命區」、`tool_search`、MCP、「也相容 prefix caching」、「沒有額外收費」、「工具越多，省得越明顯」、「支援 Gemini 3.6 以上」都與原文一致。
- 發文時間：頁面懸停提示顯示的是瀏覽器所在時區時間；`creation_time=1795161940` 換算為 `2026-11-20 16:05:40+08:00`，與筆記相符。
- 作者圖片：1 張，是 X 連結的預覽卡（不是作者上傳的圖片），已看過。
- 留言：顯示「尚無留言」，貼文計數 0、讀到 0。
- 判定：`full`，與作者相同。

## 2. 事實查核（facts）

對照官方一手文件逐項核對：

- Tool retrieval 官方文件 https://aistudio.google.com/docs/tool-retrieval
  - 預覽版、需 `v1beta`、只在 Interactions API、`generateContent` 不支援（文件開頭與 Limitations）：相符。
  - 加 `{"type": "tool_search"}` 並在工具設 `defer_loading: true`；模型看得到延後工具的名稱與描述：相符。
  - 計費：無獨立收費；延後工具只把 `name` 與 `short_description`（或 `description` 第一句）計入 `total_input_tokens`；每次伺服器端搜尋觸發一次額外模型呼叫，完整上下文加已載入 schema 計入 `total_tool_use_tokens`、按輸入費率；工具少或長上下文每輪都搜尋時靜態載入可能更便宜（Pricing and token usage）：相符。
  - 支援型號 6 款（gemini-4-carbon、gemini-4-neon、gemini-4-hydrogen、gemini-4-argon、gemini-3.8-flash、gemini-3.6-flash）：相符。
  - 遠端 MCP：在 `mcp_server` 項目設 `defer_loading: true` 即延後該伺服器全部工具（Deferring remote MCP servers）：相符。
  - 已載入工具保留到對話結束、不能卸載（Limitations）：與筆記第 3 段第 1 點相符。
  - 已載入 schema 以附加方式放進對話、不改前綴，隱式快取在達到最小長度後仍適用；延後工具會讓提示變短、可能掉到門檻以下：與筆記第 6 點「有最低長度門檻、保持前綴穩定不等於保證命中」相符。
- 快取官方文件 https://aistudio.google.com/docs/caching
  - Interactions API 只支援隱式快取；顯式快取不支援 Interactions API，也不支援 Gemini 4；要用顯式快取須在支援的 Gemini 3／2.5 模型改用 `generateContent`：與筆記第 6 點及比較表「快取支援」列相符。
  - 回應欄位 `total_cached_tokens` 存在於文件：相符。
- 官方 X 文章 https://x.com/GoogleAIStudio/status/2123489911684866251
  - 「works with Gemini 3.6 and later models, including all Gemini 4 models」：與筆記第 8 點「X 推文概括寫支援 3.6 以上」相符。
  - 「plays well with prefix caching」：貼文的說法有官方 X 文章來源，筆記把它對照到官方快取文件的邊界，處理正確。

### 更正

1. 筆記第 1 段「隨文附圖：1 張（…主視覺橫幅，解析度 2048x819，WEBP 格式）」：Facebook 貼文上的圖是連結預覽卡（Facebook 端顯示為 1500x783 的裁切版）；X 文章的原圖（`pbs.twimg.com/media/HXgZfNKW4AIwKHG`，`name=orig`）實測為 2784x1114。2048x819 只是 X 的 `large` 縮圖尺寸、WEBP 是請求參數決定的傳輸格式，都不是圖片本身的規格。建議刪掉解析度與格式，改寫「1 張：X 文章連結預覽卡（Google AI Studio 主視覺橫幅）」。

## 3. 證據分級（evidence）

- 第 1 段把貼文觀點逐點標成「貼文觀點」或「貼文未提」，並把官方規格標出出處，分級清楚。
- 比較表「實際端到端延遲尚無公開基準實測」「準確率提升幅度尚待基準實測」有明寫為未查證，符合要求。
- 沒有發現把二手或推算寫成事實語氣的地方。

## 4. 已完成任務的產出檔（task_impact）

- `T-20261122-04` 的產出檔 `docs/gemini-tool-retrieval-and-mcp-spec.md` 已存在。核對端點限制、6 款型號、`short_description` 截短規則、`total_tool_use_tokens` 計費、隱式快取、已載入工具保留等前提，都與上面查到的官方文件一致，沒有建立在錯誤前提上。
- 給整合者的備註（不計入更正）：
  - 產出檔已存在，但筆記第 4 段該任務仍是 `- [ ]`，狀態可能沒更新。
  - 筆記內有兩處簡體字：比較表「贴文」、第 3 段標題「迁移」。

## 結論

changes_requested，1 處更正（附圖規格）。其餘主張都有官方一手來源支持。

```json
{"verdict": "changes_requested", "source_review": "full", "source_images": 1, "source_replies": 0, "corrections": 1, "scope": ["source", "facts", "evidence", "task_impact"],
 "findings": [
  {"kind": "fact", "claim": "隨文附圖：1 張（引用自 Google AI Studio 官方 X 發布之架構主視覺橫幅，解析度 2048x819，WEBP 格式）", "problem": "貼文附圖是 X 連結預覽卡；X 原圖實測 2784x1114，2048x819 只是 large 縮圖尺寸，WEBP 是請求參數決定的傳輸格式，不是圖片規格", "evidence": "https://x.com/GoogleAIStudio/status/2123489911684866251（圖片 pbs.twimg.com/media/HXgZfNKW4AIwKHG，name=orig 實測 2784x1114）", "fix": "刪掉解析度與格式，改寫「1 張：X 文章連結預覽卡（Google AI Studio 主視覺橫幅）」"}
 ],
 "task_impact": []}
```
