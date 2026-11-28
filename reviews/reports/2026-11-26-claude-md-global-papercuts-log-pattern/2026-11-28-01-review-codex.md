# 獨立審查報告：2026-11-26-claude-md-global-papercuts-log-pattern

- reviewer: codex/gpt-6.1-sol@01a22260-a8fa-7ce1-8e82-9308779c9e4b
- content_sha256: 3b666cb2b1e8eb53d47f0388df2a85e90842b94969ddd48a8eec567b86cf4ed9
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 1；source_review: unavailable（作者聲明 unavailable）
- source_ref: codex thread 01a22260-a8fa-7ce1-8e82-9308779c9e4b

---
結論：`changes_requested`，共 1 處更正。筆記雜湊與指定值一致；未修改任何檔案。

### 1. 原始資料讀完度

未完成，從本次 `scope` 排除 `source`，保留作者的 `unavailable` 聲明。

已開啟提供的 [repo 網址](https://github.com/SanHsien/ai-inbox)，但它無法證明使用者當時提供的原文。以 `papercuts.md` 與片段文字搜尋，只找到近似內容，無法確認來源相同。原始圖片、留言及貼文計數均無法核對；這項限制不列為筆記錯誤。

### 2. 事實查核

**更正 1：標題與第 0 節的「零常駐 Token」說法不精確。**

[官方記憶文件](https://code.claude.com/docs/en/memory#write-effective-instructions)說明，`CLAUDE.md` 內容會占用上下文。因此，留在其中的查詢指令仍有成本；能省下的是日誌本文的常駐載入成本。

建議改為「日誌按需載入，常駐僅保留短指令」。另補充：這是提示詞約定，不能保證每次遵守；若改用 `@` 匯入日誌，內容會隨規則一起載入，見[官方匯入說明](https://code.claude.com/docs/en/memory#import-additional-files)。

本 repo 的文件與 `tools/verify_agent_lean_rules.py` 均存在，工具確有規則膨脹檢查；這部分符合筆記描述。

### 3. 證據分級

- **一手來源已確認**：規則占用上下文、`@` 匯入行為、本 repo 文件與工具功能。
- **二手來源**：筆記收錄的使用者提供片段；無法獨立確認原作者及完整脈絡。
- **推算／未查證**：降低讀寫阻力、改善排錯速度等效益；應視為設計預期，尚無本機實測支持。

### 4. 已完成任務影響

唯一任務 `T-20261126-05` 尚未完成。已查看目標文件 `docs/agent-memory-and-prompting-best-practices.md`，尚無 Papercuts 章節，沒有本任務已完成的產出需要回修。

下一步由作者修正成本說法，再送審；原始來源另行補核。

```json
{
  "verdict": "changes_requested",
  "source_review": "unavailable",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 1,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "標題與第 0 節宣稱零常駐 Token 成本",
      "problem": "CLAUDE.md 中保留的短指令仍占上下文；只能說日誌本文不常駐。自然語言指令也不是保證執行的故障觸發機制。",
      "evidence": "https://code.claude.com/docs/en/memory#write-effective-instructions ; https://code.claude.com/docs/en/memory#import-additional-files",
      "fix": "改為日誌按需載入、常駐僅保留短指令；說明仍有指令與讀檔成本，避免用 @ 匯入日誌，並將排錯效益標為待測預期。"
    }
  ],
  "task_impact": []
}
```
