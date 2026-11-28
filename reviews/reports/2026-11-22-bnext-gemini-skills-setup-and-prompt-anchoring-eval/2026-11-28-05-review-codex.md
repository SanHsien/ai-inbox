# 獨立審查報告：2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval

- reviewer: codex/gpt-6.1-sol@01a221a5-921b-74d2-89c7-ebe3d014b0be
- content_sha256: 19bdcba4eaa638861bdc6ed886122933cafe3bd02481842bd0227da150622d46
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: pass；corrections: 0；source_review: full（作者聲明 full）
- source_ref: codex thread 01a221a5-921b-74d2-89c7-ebe3d014b0be

---
結論：`pass`，限 `facts`、`evidence`、`task_impact`。未發現需更正處；`source` 尚未完成，不代表全範圍放行。全程未改檔。

內容雜湊已核對，與指定值一致：
`19bdcba4eaa638861bdc6ed886122933cafe3bd02481842bd0227da150622d46`

1. **原始資料讀完度（source）**

   原始網址無法開啟；已讀完[同媒體刊載版本](https://1day1ai.bnextmedia.com.tw/articles/gemini-skills-setup-guide)，但其中 7 張文章圖片均載入失敗，實際看過 0 張。無法確認原頁留言計數，實際未讀留言。

   因此從 `scope` 移除 `source`，保留作者的 `full` 聲明，不把本次存取限制列為更正。圖片內容與「沒有留言區」仍待補審。

2. **事實查核（facts）**

   未發現需更正處：

   - 個人帳號於 2026 年 11 月開始轉移、既有 Gems 自動轉成技能，符合[Google 轉移公告](https://support.google.com/gemini/answer/18560919?hl=en)。
   - 年齡門檻、建立入口、`SKILL.md`／ZIP 上傳、附件類型、合計 100 MB、腳本不得連網或對外部網站動作，以及 `/`／`@` 呼叫差異，符合[Google 使用說明](https://support.google.com/gemini/answer/17094296?hl=en)與[匯入指南](https://support.google.com/gemini/answer/18977944?hl=en)。
   - 依名稱與描述判斷相關性，再讀完整指示，符合[官方載入機制說明](https://support.google.com/gemini/answer/17102773?hl=en)。
   - `compatibility` 可描述工具、套件與網路需求，符合[Agent Skills 規格](https://agentskills.io/specification)。筆記的填寫建議未冒稱為官方必填規則。
   - 作者與日期符合上述同媒體版本；ChatGPT 支援技能亦有[官方說明](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)。筆記已另列 Antigravity 為自行延伸的評估範圍。

3. **證據分級（evidence）**

   分級適當：平台限制與載入機制有一手來源；跳步與改寫成功明列為作者單次實測、二手轉述；名稱可能提高匹配機率明列推論。兩種提示寫法均標為待測，未將一次成功寫成因果或效果保證。

4. **任務影響（task_impact）**

   僅有 `T-20261122-01`，仍為未完成。已讀 `docs/cross-platform-skill-spec.md`；相關段落同樣保留單次實測、推論與待測標記。沒有已完成任務須回報受錯誤前提影響。

下一步：補審原頁、7 張圖片與留言狀態，再決定是否放行 `source`。

```json
{
  "verdict": "pass",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 0,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [],
  "task_impact": []
}
```
