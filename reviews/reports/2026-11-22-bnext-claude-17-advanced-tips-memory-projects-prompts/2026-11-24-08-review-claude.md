# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: claude/opus-5.5@e6ba4015-0a88-4012-9e1a-cef3c3754e71
- content_sha256: 30c2d1f562d4a917d645a26329bd51b66e53561654c26a0ed228b818cbed8299
- role: review；lane: chrome；scope: source
- reviewed_at: 2026-11-24
- verdict: changes_requested；corrections: 2；source_review: full（作者聲明 full）

---
# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- 審查者：claude/opus-5.5（Chrome 道）
- 角色：review；範圍：source
- 審查日期：2026-11-24
- **取代同日 `2026-11-24-07-review-claude.md`**：那份是入帳時誤用草稿目錄裡 2026-11-23 的舊報告，它列的兩處更正（技巧 10「對照矩陣」、技巧 17 缺但書）在目前版本的筆記已改好，請以本報告為準。
- 讀取方式：Claude in Chrome 開 `https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts`，讀完 `<article>` 全文，列出文章內所有 `img` 並截圖看過內容圖。

## 1. 原始資料讀完度（範圍 `source`）

- **正文**：已讀完。發布日 2026.11.18、作者蘇柔瑋，與筆記相符；17 個技巧、限制表、FAQ 都讀過。
- **圖片**：內容圖是「Claude 17 個進階技巧一覽」分類表（圖／數位時代），首圖（1200x1431）是同一張表的另一尺寸版本（內文 2000x2385）；其餘是頭像、標誌與廣告。實質圖片 1 張，筆記 `source_images: 1` 正確。
- **留言**：文章頁沒有留言區，讀到 0 則，`source_replies: 0` 正確。
- **判定**：`full`，與作者相同。
- 前一輪指出的技巧 10、17 轉述問題，目前筆記第 56、62 行已改成原文意思，確認已修。

### 轉述與原文不符處

1. **技巧 3 把「可以」寫成「必須」**：筆記第 48 行寫多客戶管理時「必須在 Project 的 Memory 設定中關閉『Use account memory』」。原文是條件式建議：「若希望隔離不同專案，可以進入專案的Memory記憶設定，關閉…」。建議改成「若要隔離不同專案，可關閉」。
2. **技巧 9 把「建議」寫成「禁止／強制」**：筆記第 55 行寫「禁止引導式讚同，強制要求提出『3 個最強的反對理由』」。原文是「避免用引導式問句」、「Hassid建議改成要求Claude主動提出不同觀點」，3 個反對理由只是範例問法。建議改成「避免引導式問句，改請模型提出反對理由（例如 3 個最強的反對理由）」，並把錯字「讚同」改為「贊同」。

出處皆為 `https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts`。

## 2. 事實查核（範圍 `facts`）

不在本次範圍。

## 3. 證據分級（範圍 `evidence`）

不在本次範圍。

## 4. 已完成任務的產出檔（範圍 `task_impact`）

不在本次範圍。

## 結論

`changes_requested`，更正 2 處，讀完度判定 `full`。

```json
{"verdict": "changes_requested", "source_review": "full", "source_images": 1, "source_replies": 0, "corrections": 2, "scope": ["source"], "findings": [{"kind": "source", "claim": "技巧 3：必須在 Project 的 Memory 設定中關閉「Use account memory」", "problem": "原文是條件式建議「若希望隔離不同專案，可以…關閉」，不是必須", "evidence": "https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts（技巧3段）", "fix": "改成「若要隔離不同專案，可在 Project 的 Memory 設定關閉 Use account memory」"}, {"kind": "source", "claim": "技巧 9：禁止引導式讚同，強制要求提出「3 個最強的反對理由」", "problem": "原文是「避免用引導式問句」與「Hassid建議改成要求Claude主動提出不同觀點」，3 個反對理由只是範例；另「讚同」為錯字", "evidence": "https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts（技巧9段）", "fix": "改成「避免引導式問句，改請模型提出反對理由（例如 3 個最強的反對理由）」，並改「讚同」為「贊同」"}], "task_impact": []}
```
