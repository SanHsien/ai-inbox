# 獨立審查報告：2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval

- reviewer: claude/opus-5.5@498c74d5-8c16-46e8-9fdc-3a900cc320b6
- content_sha256: 74fe7830046104c20a71f85d64315e0aabb8d44c1ff48f4b8df58c9a5f7fe579
- role: review；lane: chrome；scope: source
- reviewed_at: 2026-11-25
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）

---
# 獨立審查報告：2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval

- 角色：review；範圍：source
- 審查者：Claude（Chrome 道）；原文用 Claude in Chrome 讀正文，圖片因 Chrome 截圖逾時改用內建瀏覽器直接開圖片網址查看（公開 CDN，不需登入）
- 原始來源：https://www.bnext.com.tw/article/93097/gemini-skills-setup-guide（2026.11.18，韋惟珊）

## 1. 原始資料讀完度（source）

- 正文：從頭讀到「延伸閱讀」之前全文。
- 作者圖片：共 7 張，全部開原圖看過。
  - 封面圖（`img-mcp-3987ebbaf7de1da6.jpg`）：插畫加標題「免費版 Gemini 也能裝技能」，無額外資訊。
  - 圖卡 1（`df64b7…`）：自訂 → 技能分頁 → 建立按鈕，與筆記一致。
  - 圖卡 2（`f2135a…`）：建立選單「運用 Gemini 建立／手動建立／上傳」，標出對話建立與上傳技能，與筆記一致。
  - 圖卡 3（`8e9964…`）：輸入框打 `@`，從「技能」區選 deep-question-designer，與筆記一致。
  - 圖卡 4（`435f83…`）：已叫用技能，但回覆直接給 Day 1–5 計畫表（即跳步的失敗案例），筆記寫「執行回覆檢查」大致相符。
  - 圖卡 5（`3fa75e…`）：只有改寫後的成功畫面（句首寫技能名稱 → 先列已知事實與假設 → 進入深化流程），**沒有前後對照**。
  - 圖卡 6（`8bc017…`）：插畫（貓提行李箱在月台，旁邊三色列車），**不是 SKILL.md 用在不同 AI 工具的示意圖**，畫面上沒有任何工具名或檔案。
- 留言：數位時代文章頁沒有留言區，`source_replies: 0` 正確。
- 判定：作者標 `full` 合理（正文與全部圖片皆可讀、無留言區）。封面圖沒列進盤點不影響讀完度，但圖片數建議改 7（或註明 6 張圖卡＋1 張封面）。

### 更正

1. 筆記第 1 節「文章說 `SKILL.md` 可用在 Gemini、Claude、ChatGPT、Antigravity」：原文只列「Gemini、Claude和ChatGPT」，沒有 Antigravity。Antigravity 是筆記自己加的，卻寫成「文章說」。
2. 圖卡盤點「圖 5：提示詞句首定錨寫法改進前後對照」：圖卡 5 只有改寫後的畫面，失敗的「前」是圖卡 4。應改成「圖 5：句首寫技能名稱後的成功回覆（先列已知事實與假設、再深化）；改寫前的跳步見圖 4」。
3. 圖卡盤點「圖 6：同一份 `SKILL.md` 用在不同 AI 工具的示意圖」：圖卡 6 是插畫（貓帶行李箱在月台），沒有工具或檔案內容，筆記把配圖描述成資訊圖卡。應改成「圖 6：裝飾插畫（帶著行李換車的比喻），無資訊內容」。

## 2. 事實查核（facts）

不在本次範圍。

## 3. 證據分級（evidence）

不在本次範圍。

## 4. 已完成任務的產出檔（task_impact）

不在本次範圍。（備註供整合者：T-20261122-01 若把 Antigravity 列為文章背書的平台，會受更正 1 影響；本次未打開產出檔核對。）

## 結論

changes_requested，3 處更正。

```json
{"verdict": "changes_requested", "source_review": "full", "source_images": 7, "source_replies": 0, "corrections": 3, "scope": ["source"],
 "findings": [
  {"kind": "source", "claim": "文章說 SKILL.md 可用在 Gemini、Claude、ChatGPT、Antigravity", "problem": "原文只列 Gemini、Claude和ChatGPT，沒有 Antigravity", "evidence": "https://www.bnext.com.tw/article/93097/gemini-skills-setup-guide（「同一份SKILL.md可以帶到不同AI工具嗎？」段）", "fix": "改成「文章說可用在 Gemini、Claude、ChatGPT」，Antigravity 另註為本 repo 自行延伸、未經文章背書"},
  {"kind": "source", "claim": "圖 5：提示詞句首定錨寫法改進前後對照", "problem": "圖卡 5 只有改寫後的成功畫面，沒有前後對照；改寫前的跳步畫面是圖卡 4", "evidence": "https://image-cdn.learnin.tw/bnextmedia/image/album/2026-11/img-mcp-3fa75ebaaabbc359.jpg", "fix": "改成「圖 5：句首寫技能名稱後的成功回覆（先列已知事實與假設，再進入深化流程）；改寫前見圖 4」"},
  {"kind": "source", "claim": "圖 6：同一份 SKILL.md 用在不同 AI 工具的示意圖", "problem": "圖卡 6 是裝飾插畫（貓帶行李箱在月台），畫面沒有任何工具或 SKILL.md 內容", "evidence": "https://image-cdn.learnin.tw/bnextmedia/image/album/2026-11/img-mcp-8bc017f858d2fefe.jpg", "fix": "改成「圖 6：裝飾插畫（帶行李換車的比喻），無資訊內容」；另補列封面圖，source_images 改 7"}
 ],
 "task_impact": []}
```
