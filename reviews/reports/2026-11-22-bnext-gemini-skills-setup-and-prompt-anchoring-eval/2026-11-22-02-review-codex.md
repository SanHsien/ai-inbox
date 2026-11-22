# 獨立審查報告：2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval

- reviewer: codex/gpt-6.1-sol@01a203b5-fcfc-7971-84e3-cad9e4665063
- content_sha256: c7b681fb947a368c434980ec9ef2d7dac41683996546395efa049c5f6d25f34e
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 2；source_review: full（作者聲明 full）
- source_ref: codex thread 01a203b5-fcfc-7971-84e3-cad9e4665063

---
結論：`changes_requested`，共 2 處更正。內容雜湊與派審值一致；未修改任何檔案。

### 1. 原始資料讀完度（source）

原始 Bnext 網址無法開啟；已讀[同媒體刊載版本](https://1day1ai.bnextmedia.com.tw/articles/gemini-skills-setup-guide)正文，但未逐張檢視圖片，也無法確認原頁留言計數。

本次實際看圖 0 張、讀留言 0 則，留言總數未知。因此從結果 `scope` 移除 `source`，保留作者的 `full` 聲明，不將存取限制列為更正。

### 2. 事實查核（facts）

**更正 1：上傳格式限制說得過窄。**

筆記第 1 節將上傳限制概括為只收純文字，但官方支援清單也列有 PDF、DOCX、XLSX、PPTX、PNG、JPG 等格式。應依官方清單列出支援與排除項目，並區分技能外層 ZIP 與包內壓縮附件。[Google 官方說明](https://support.google.com/gemini/answer/17094296?hl=en)、[官方遷移指南](https://support.google.com/gemini/answer/18977944?hl=en)

其餘已確認：支援單一 `SKILL.md` 或 ZIP 上傳、總容量上限 100 MB、腳本禁止連網與外部網站請求，以及 `/`、`@` 呼叫差異。[Google 官方說明](https://support.google.com/gemini/answer/17094296?hl=en)

### 3. 證據分級（evidence）

**更正 2：把單次案例擴大為頻率與原因。**

筆記第 1 節將跳步描述為經常發生，並歸因於提示詞語義漂移。同媒體正文只記錄作者第一次跳步、第二次改寫後成功，未提供發生率或原因驗證。應改成單次實測轉述；原因尚未查證。[同媒體正文](https://1day1ai.bnextmedia.com.tw/articles/gemini-skills-setup-guide)

其餘分級合理：

- 一手確認：依名稱、描述判斷相關性，再讀完整指示。[Google 官方撰寫指南](https://support.google.com/gemini/answer/17102773)
- 二手轉述：作者的跳步案例與改寫後結果。
- 推算／未查證：句首點名可能提高匹配率；筆記已標明待測。
- `compatibility` 是選填環境需求欄位；筆記建議有需求時填寫，符合[開放規格](https://agentskills.io/specification)。

### 4. 任務產出影響（task_impact）

唯一任務 `T-20261122-01` 仍未完成，沒有已完成任務可驗收。

另已讀取現存的 [docs/cross-platform-skill-spec.md](C:/GitHub/ai-inbox/docs/cross-platform-skill-spec.md)。第 1 節格式限制列及第 2 節附件型別列，也沿用了過窄的純文字限制，應由整合者同步修正。本次只回報。

下一步：修正上述兩處筆記主張與相關文件，再補審原頁圖片及留言。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 2,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第1節將Gemini技能上傳格式概括為僅收純文字類格式。",
      "problem": "官方支援清單也包含PDF、DOCX、XLSX、PPTX及多種圖片格式；目前概括會錯誤排除可用附件。",
      "evidence": "https://support.google.com/gemini/answer/17094296?hl=en ; https://support.google.com/gemini/answer/18977944?hl=en",
      "fix": "依官方清單列出支援及排除格式，並區分可上傳的技能外層ZIP與包內不支援的壓縮附件。"
    },
    {
      "kind": "evidence",
      "claim": "第1節將技能跳步描述為經常發生，並歸因於提示詞語義漂移。",
      "problem": "可讀的同媒體正文只記錄一次跳步與一次改寫成功，未提供發生率或語義漂移的因果證據。",
      "evidence": "https://1day1ai.bnextmedia.com.tw/articles/gemini-skills-setup-guide",
      "fix": "改為作者單次實測曾跳過第一步；原因未查證，改寫效果仍待對照測試。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-01",
      "file": "docs/cross-platform-skill-spec.md",
      "issue": "任務仍未完成，但現存文件第1節格式限制列及第2節附件型別列，沿用僅收純文字的過窄描述，應同步依官方支援清單修正。"
    }
  ]
}
```
