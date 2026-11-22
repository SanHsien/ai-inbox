# 獨立審查報告：2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval

- reviewer: claude/opus-5.5@f5e4b602-97a8-42e0-a0f4-660098002a1f
- content_sha256: c1c3ce02545e23fbc0f6600632c8fd74b1035f3c4cad5e4ad207d737444ed93c
- role: review；lane: chrome；scope: source
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）

---
# 獨立審查報告：2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval

- 審查者：claude/opus-5.5（Chrome 道，role `review`，scope `source`）
- 審查日：2026-11-22
- 讀取方式：Claude in Chrome（維護者已登入的 Chrome）開 `https://www.facebook.com/will.fans/posts/1606150151539068/`，貼文以對話框開啟，用無障礙樹讀全文、互動數與留言區；另開貼文連結的 X 文章 `https://x.com/GoogleAIStudio/status/2123489911684866251` 讀全文。

## 1. 原始資料讀完度（範圍 `source`）

- **貼文文字**：已讀完。內容是約 20 句短句的中文摘要，最後附一張 X 文章的連結預覽卡。
- **作者圖片**：貼文沒有作者上傳的圖片，只有 Facebook 自動產生的連結預覽卡（alt 為 X 文章標題）。這張卡的像素內容沒看到：Chrome 擴充功能截圖在兩個分頁都失敗（錯誤 `Cannot access a chrome-extension:// URL of different extension` 與 script injection timeout）。改讀卡片連到的 X 文章全文代替。`source_images` 填 0（沒有作者上傳圖）。
- **留言**：貼文對話框顯示「尚無留言」「留言搶頭香」，讚 39、分享 6。貼文計數 0 則，實際讀到 0 則，相等。沒有排序選單可切（無留言）。
- **判定**：`full`，與作者一致。

### 原始資料比對發現的更正（筆記把貼文沒有的內容寫成貼文內容）

筆記第 1 節標題寫「貼文核心內容逐字重點」，但下列內容不在貼文裡：

1. **發文時間**：筆記寫 `2026-11-20T16:05:40+08:00`。Facebook 貼文顯示「2026年11月20日 星期五上午12:05」，瀏覽器時區為 `Etc/GMT-8`（UTC+8），即 `2026-11-20T00:05+08:00`，筆記差 16 小時。疑似把 UTC 時間（11-19 16:05Z）換算錯。
2. **第 3 點的 `defer_loading: true`**：貼文只寫「程式只要加一個 tool_search 就好」，沒提 `defer_loading`。這個旗標出自 X 文章（"set defer_loading: true on the tools you want to hold back"）。應標明出處是官方文章、不是貼文。
3. **第 8 點「包含 Neon、Pro、Flash 等」**：貼文只寫「目前支援 Gemini 3.6 以上，包含所有 Gemini 4 模型」；X 文章也只寫 "Gemini 3.6 and later models, including all Gemini 4 models, in the Interactions API"。兩處都沒列 Neon／Pro／Flash 型號，這是撰寫者自加的。

### 非更正、供整合者參考

- 附圖描述「解析度 2048x819，WEBP」無法驗證（截圖失效）；X 頁面上同一張封面圖載入尺寸是 1200x480，比例相同，可能只是不同 CDN 尺寸，不列更正。
- 「隨文附圖 1 張」實為自動連結預覽卡，不是作者上傳；建議第 0 段寫明，但不影響 full 判定。
- X 文章指出功能是 Interactions API 的 preview，另有 client-side retrieval（`"execution": "client"`）模式；筆記未提，屬事實／完整度範圍，不在本次範圍。
- 作者欄「黃保吸」疑為錯字（貼文頁未顯示本名，屬事實範圍，交 Codex 道）。

## 2. 事實查核（範圍 `facts`）

不在本次範圍。

## 3. 證據分級（範圍 `evidence`）

不在本次範圍。

## 4. 已完成任務的產出檔（範圍 `task_impact`）

不在本次範圍。（筆記唯一任務 `T-20261122-04` 仍是未勾選狀態。）

## 結論

`changes_requested`，3 處更正，皆為原始資料轉述錯誤。

```json
{"verdict": "changes_requested", "source_review": "full", "source_images": 0, "source_replies": 0, "corrections": 3, "scope": ["source"], "findings": [{"kind": "source", "claim": "發布於 `2026-11-20T16:05:40+08:00`", "problem": "Facebook 貼文顯示 2026年11月20日 星期五上午12:05（瀏覽器時區 UTC+8），即 2026-11-20T00:05+08:00，筆記差 16 小時", "evidence": "https://www.facebook.com/will.fans/posts/1606150151539068/", "fix": "改為 2026-11-20T00:05+08:00（秒數以頁面中繼資料為準）"}, {"kind": "source", "claim": "第 3 點：（`tool_search` 配合 `defer_loading: true`）", "problem": "貼文只提 tool_search，沒提 defer_loading；該旗標出自 Google AI Studio 的 X 文章，卻寫在「貼文核心內容逐字重點」裡", "evidence": "https://www.facebook.com/will.fans/posts/1606150151539068/ ；https://x.com/GoogleAIStudio/status/2123489911684866251", "fix": "移出貼文重點，或註明「依官方文章」"}, {"kind": "source", "claim": "第 8 點：全數支援所有 Gemini 4 系列模型（包含 Neon、Pro、Flash 等）", "problem": "貼文與官方 X 文章都只寫「Gemini 3.6 以上，包含所有 Gemini 4 模型」，沒列 Neon／Pro／Flash", "evidence": "https://www.facebook.com/will.fans/posts/1606150151539068/ ；https://x.com/GoogleAIStudio/status/2123489911684866251", "fix": "刪除括號內型號，或改寫為撰寫者推論並標明未查證"}], "task_impact": []}
```
