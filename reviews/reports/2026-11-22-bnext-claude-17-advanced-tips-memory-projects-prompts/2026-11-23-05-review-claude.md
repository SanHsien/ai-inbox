# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- reviewer: claude/opus-5.5@875b2527-34d5-49c0-8720-89827cc71a07
- content_sha256: 306845f40ccbb30c4b9c3a7e944cad3cd42ae487635f9d0ddd0e60b0918e0b00
- role: review；lane: chrome；scope: source
- reviewed_at: 2026-11-23
- verdict: changes_requested；corrections: 2；source_review: full（作者聲明 full）

---
# 獨立審查報告：2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts

- 審查者：claude/opus-5.5（Chrome 道）
- 角色：review；範圍：source
- 審查日期：2026-11-23
- 讀取方式：Claude in Chrome 開 `https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts`，捲到底讓圖片載入，分段讀完第一篇 `article` 的全文（約 7100 字，到 FAQ 與資料來源為止；頁面後面自動接續的下一篇不算），截圖看圖。

## 1. 原始資料讀完度（範圍 `source`）

- **正文**：已讀完。作者蘇柔瑋，2026-11-18；整理 Ruben Hassid〈Claude 101〉，文末註明「本文初稿為AI編撰」。17 個技巧、限制表、FAQ 都讀過。
- **圖片**：1 張。「Claude 17 個進階技巧一覽」分類表（圖／數位時代），同一張圖同時當封面（1200x1431）與內文圖（2000x2385，長寬比相同），已截圖看過。筆記 `source_images: 1` 正確。
- **留言**：文章頁沒有留言區，`source_replies: 0` 正確。
- **判定**：`full`，與作者相同。

### 發現的更正

1. **技巧 10 的轉述把文章的替代建議當成原技巧，還加了原文沒有的「對照矩陣」**：筆記第 56 行寫「要求產出 20 個差異明顯的選項並以客群/價格/風格建立對照矩陣」。原文的 Hassid 原技巧是「要求 20 個差異明顯的選項，並估計其他 AI 給出相同答案的可能性」；文章接著提醒 AI 自估的機率不能當統計數據，才另外建議改用不同客群、價格策略、風格或使用情境讓差異可比較。原文沒有「對照矩陣」。建議改寫成：原技巧（含自估機率）＋文章的但書與替代做法，並拿掉「對照矩陣」。
2. **技巧 17 漏了文章的但書，寫成中性建議**：筆記第 62 行寫「避免過度定義『我的風格』導致模型回答陷入僵化範本」，沒有標註來源等級。原文明寫這是 Hassid 的主張、不是 Anthropic 官方要求、不一定適合所有人；需要維持品牌語氣或格式時保留清楚的自訂指令仍有用；文末限制表也把「自訂指令全部清空」列為應視為個人建議的項目。筆記第 64 行「研究邊界」段也沒收這一條。建議第 62 行標成「Hassid 個人主張（二手）」並轉述文章的反方說明。

另外供整合者參考（不列更正）：第 49 行「第二類（技巧 4～6）」只列了技巧 4 與 6，技巧 5（模型自動切換）放在第 64 行處理；第 57 行技巧 11 只寫截圖，漏了原文的「語音交代需求」；第 59 行技巧 12、13 未轉述原文的但書（Workspace 整合是測試版且限方案；貼 GitHub 連結不代表 Claude 能讀整個專案）。

出處皆為 `https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts`。

## 2. 事實查核（範圍 `facts`）

不在本次範圍。

## 3. 證據分級（範圍 `evidence`）

不在本次範圍。

## 4. 已完成任務的產出檔（範圍 `task_impact`）

不在本次範圍（任務 `T-20261122-02` 未勾選）。

## 結論

`changes_requested`，更正 2 處，讀完度判定 `full`。

```json
{"verdict": "changes_requested", "source_review": "full", "source_images": 1, "source_replies": 0, "corrections": 2, "scope": ["source"], "findings": [{"kind": "source", "claim": "具體多樣性約束（技巧 10）：要求產出 20 個差異明顯的選項並以客群/價格/風格建立對照矩陣", "problem": "原技巧是要求 20 個選項並估計其他 AI 給相同答案的可能性；客群／價格／風格是文章提出的替代做法；原文沒有「對照矩陣」", "evidence": "https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts（技巧10）", "fix": "分開寫 Hassid 原技巧（含自估機率與文章但書）與文章的替代做法，拿掉「對照矩陣」"}, {"kind": "source", "claim": "精簡過長的自訂指令（技巧 17）：避免過度定義「我的風格」導致模型回答陷入僵化範本", "problem": "原文明寫這是 Hassid 個人主張、非官方要求、不一定適合所有人，並說明保留清楚自訂指令仍有用；筆記寫成中性建議、未標來源等級", "evidence": "https://www.bnext.com.tw/article/93067/claude-17-advanced-tips-memory-projects-prompts（技巧17 與文末限制表）", "fix": "標成 Hassid 個人主張（二手），並轉述文章的反方說明"}], "task_impact": []}
```
