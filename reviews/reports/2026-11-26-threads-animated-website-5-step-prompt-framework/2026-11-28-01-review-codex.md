# 獨立審查報告：2026-11-26-threads-animated-website-5-step-prompt-framework

- reviewer: codex/gpt-6.1-sol@01a222c2-9581-7da3-bbe0-74907cbbd262
- content_sha256: 4a05b58c08619c6bc43d3e540078c68f078adc4c5f8728c095e74b57a843dc12
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: unavailable（作者聲明 unavailable）
- source_ref: codex thread 01a222c2-9581-7da3-bbe0-74907cbbd262

---
結論：`changes_requested`，共 3 處更正。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   筆記提供的網址是收件匣 repo，沒有 Threads 原文連結。網頁查證遭帳號額度鎖定，未能搜尋原文或核對圖片、作者補充及留言。貼文留言計數未知；實際讀取圖片 0 張、留言 0 則。

   本次排除 `source`，保留作者的 `unavailable`，不將存取限制列為更正。原始資料需另派 Chrome 道補讀。

2. **事實查核（facts）**

   發現 1 處更正：筆記第 59 行稱本庫有 `inspect.mjs`，但目前檔案清單與內容搜尋均未找到。筆記引用的 [Hero 規格第 7 節](docs/zero-build-shader-hero-sections-spec.md)實際列的是瀏覽器測試及範本內的 `verify_hero.py`，應改指可核對的驗收方法。

   作者身分、五步原文及遊艇範例品質均無法獨立查證，不判定為錯誤。

3. **證據分級（evidence）**

   發現 2 處更正：

   - 第 56 行的「降低了……遺漏率」屬**推算／未查證**。所引[盤點範本](templates/subject-inventory-argument-writing-prompt.md)提供流程，沒有此框架的遺漏率對照測試。應改為預期效益。
   - 第 58 行將角色形容詞與特效堆疊連成常見因果，屬**推算／未查證**。[反罐頭規範](docs/anti-ai-slop-frontend.md)列出輸出限制，但沒有驗證這些形容詞造成該結果。應改為作者的風險判斷。

   **一手來源已確認**：引用的三份本庫文件存在，分別提供設計限制、素材盤點流程與動態行為驗收方法。這只能支持文件內容，不能證明貼文框架的效果。原文轉述仍屬二手資料，本次未核實。

4. **已完成任務的產出檔（task_impact）**

   本篇為歸檔參考，沒有任務 ID、待辦或已完成任務。上述文件是交叉參照，沒有本篇任務產出可追查；`task_impact` 為空。

下一步：整合者修正以下 3 處，再送審；原始資料另補讀。

```json
{
  "verdict": "changes_requested",
  "source_review": "unavailable",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 59 行稱本庫有 inspect.mjs／CDP 檢驗",
      "problem": "目前 repo 找不到 inspect.mjs；所引 Hero 規格列出的驗收方法也不是該檔案。",
      "evidence": "notes/2026-11-26-threads-animated-website-5-step-prompt-framework.md:59；docs/zero-build-shader-hero-sections-spec.md 第 7 節；git ls-files '*inspect.mjs' 無結果",
      "fix": "移除 inspect.mjs，改指 Hero 規格第 7 節列出的瀏覽器測試及範本內 verify_hero.py，並區分動態行為驗證與截圖驗收。"
    },
    {
      "kind": "evidence",
      "claim": "第 56 行將分層描述與素材盤點寫成已降低遺漏率",
      "problem": "沒有提供對照測試、量測條件或結果；引用範本不能證明該效果。",
      "evidence": "notes/2026-11-26-threads-animated-website-5-step-prompt-framework.md:56；templates/subject-inventory-argument-writing-prompt.md",
      "fix": "改為作者推論：預期有助減少遺漏，但本篇未實測。"
    },
    {
      "kind": "evidence",
      "claim": "第 58 行將浮誇角色形容詞與模型常堆疊特效連成因果",
      "problem": "引用規範未提供這項因果或發生頻率的測試，不能當成已確認的模型行為。",
      "evidence": "notes/2026-11-26-threads-animated-website-5-step-prompt-framework.md:58；docs/anti-ai-slop-frontend.md 第 0 至 2 節",
      "fix": "改為作者的設計風險判斷，註明未經對照實測，並以實際輸出是否違反規範作判定。"
    }
  ],
  "task_impact": []
}
```
