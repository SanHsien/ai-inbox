# 獨立審查報告：2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval

- reviewer: codex/gpt-6.1-sol@01a20282-0232-7a51-8d1f-77ffbcf9a610
- content_sha256: 7f6cef9b970e597b1c114963cc678969b3cea6729f0de8ed9feb280a7ec57384
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）
- source_ref: codex thread 01a20282-0232-7a51-8d1f-77ffbcf9a610

---
結論：`changes_requested`，共 3 處更正。已完成 `facts`、`evidence`、`task_impact`；原文無法讀取，`source` 留待補審。未修改任何檔案。

### 1. 原始資料讀完度

[原始文章](https://www.bnext.com.tw/article/93097/gemini-skills-setup-guide)及文章編號網址均無法開啟，未能核對作者、發布日期、正文、圖片與留言。

實際看過作者圖片 0 張、留言 0 則；平台留言計數未知，不能判定沒有留言。依本次規則，移除 `source` 範圍，保留作者的 `full` 聲明，不將讀取限制列為更正。

### 2. 事實查核

官方文件可確認：2026 年 11 月開始個人帳號 Gems 轉移、18 歲門檻，以及匯入 `SKILL.md`／ZIP 的功能與筆記所列附件類型。[轉移說明](https://support.google.com/gemini/answer/18560919?hl=en)、[建立與管理技能](https://support.google.com/gemini/answer/17094296?hl=en)

須更正：

1. **第 43 行：快捷鍵已全面換成 `@`。** 官方仍說可用 `/`，取得新版快捷鍵才用 `@`。應改為分批更新，避免寫成所有帳號皆已切換。[官方操作說明](https://support.google.com/gemini/answer/17094296?hl=en)

2. **第 47、59、69 行：格式共通被擴大為無縫執行。** 官方支持跨平台匯入，但 Gemini 不支援需連網的腳本，且有檔案類型與容量限制；Agent Skills 規格也明列環境相容性欄位。應區分格式可攜性與功能相容性，逐平台驗證。[Gemini 限制](https://support.google.com/gemini/answer/17094296?hl=en)、[Agent Skills 規格](https://agentskills.io/specification)

### 3. 證據分級

- **一手來源已確認**：上述轉移、建立、匯入功能及平台限制。
- **二手來源、尚未獨立重現**：筆記轉述的跳步案例、首句點名及末句補強效果。原文未讀到，不能確認轉述是否準確。
- **推算／未查證，須更正第 3 處**：第 49、51、69 行將跳步歸因於語義漂移、注意力衰減，並宣稱句首點名能強制載入權重，未提供研究或測試證據。Google 文件說明的是依名稱與描述判斷相關性，再讀取完整指令，未證實這套注意力機制。應刪除確定因果，將寫法降為待測技巧。[官方技能運作與撰寫指南](https://support.google.com/gemini/answer/17102773)

### 4. 任務影響

唯一任務 `T-20261122-01` 尚未完成；其預定產出 `docs/cross-platform-skill-spec.md` 不存在，沒有已完成產出須回報修正。

後續實作應先測平台相容性與提示寫法效果，不能直接把無縫遷移或注意力假說寫成規範。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "筆記第 43 行將技能快捷鍵描述為已全面改用 @。",
      "problem": "官方仍列出 /，並限定取得新版快捷鍵的帳號才使用 @；筆記省略更新差異。",
      "evidence": "https://support.google.com/gemini/answer/17094296?hl=en",
      "fix": "改為可輸入 /，已更新快捷鍵的帳號則使用 @，依實際介面操作。"
    },
    {
      "kind": "fact",
      "claim": "筆記第 47、59、69 行將共通格式延伸為跨平台無縫復用。",
      "problem": "可匯入相同格式不代表功能與執行環境相容。Gemini 有連網腳本、檔案類型與容量限制；規格也允許標示環境需求。",
      "evidence": "https://support.google.com/gemini/answer/17094296?hl=en ; https://agentskills.io/specification",
      "fix": "改為格式可攜，功能須逐平台驗證；補列工具、腳本、網路與附件限制。"
    },
    {
      "kind": "evidence",
      "claim": "筆記第 49、51、69 行以注意力機制解釋跳步，並宣稱句首點名能強制載入技能權重。",
      "problem": "筆記沒有提供支持此因果的研究或對照測試。官方文件說明相關性判斷與指令載入流程，未證實上述注意力機制；目前無法查證。",
      "evidence": "notes/2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval.md:49-69 ; https://support.google.com/gemini/answer/17102773",
      "fix": "刪除確定的注意力因果說法；案例標為二手轉述，提示寫法標為待測技巧，補測試後再評估效果。"
    }
  ],
  "task_impact": []
}
```
