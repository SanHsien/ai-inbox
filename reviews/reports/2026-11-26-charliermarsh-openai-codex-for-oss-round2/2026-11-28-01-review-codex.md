# 獨立審查報告：2026-11-26-charliermarsh-openai-codex-for-oss-round2

- reviewer: codex/gpt-6.1-sol@01a222b7-9e8b-7fd0-88dd-50ff4bd73002
- content_sha256: 3c91d2916be98a0f7232857134655e268b67713a0266141d97aad1541d398529
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: partial（作者聲明 partial）
- source_ref: codex thread 01a222b7-9e8b-7fd0-88dd-50ff4bd73002

---
結論：`changes_requested`，共 3 處更正。未修改任何檔案；筆記內容雜湊與指定值一致。

1. **原始資料讀完度：不在本次範圍**

   沿用作者的 `partial`。X 原文讀取遭拒，未查看圖片與留言；不因此列為筆記錯誤。

2. **事實查核：2 處更正**

   - **F1：把 Pro 月費寫成美元額度。** 第 0 節把資助描述為每月提供 100 美元額度，混淆訂閱價格與可支用點數。官方分別列出半年 Pro 訂閱及另外審核的 API credits；Pro 100 的 100 美元是月費。應改為「公告當時提供半年 Pro 100 訂閱」，勿稱每月美元額度。[官方方案說明](https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers)、[資助申請頁](https://openai.com/form/codex-for-oss/)

   - **F2：Anthropic 比較採用過時條件。** 第 0 節把 5,000 星或每月百萬 npm 下載描述成競品現行硬門檻。現行官方條款提供多種資格途徑，另有未達數字門檻者可申請的生態影響途徑；方案目前稱 Claude Ultra。應更新比較，若保留舊制則標明日期並附歷史來源。[官方申請頁](https://claude.com/contact-sales/claude-for-oss)、[官方條款第 2 節](https://www.anthropic.com/claude-for-oss-terms)

3. **證據分級：1 處更正**

   - **F3：把第二輪延續推成固定續約制度。** 第 1 節宣稱資助已常態化並每半年續約，超出已確認證據。官方條款只承諾經核准的限期福利，期限與內容可不同，也保留調整或停止計畫的權利。應改為「本次延續計畫；未確認固定半年續辦或續約承諾」。[官方條款第 1、8 節](https://learn.chatgpt.com/docs/codex-for-oss-terms)

   其餘證據分級如下：

   - **一手來源已確認：** 半年 Pro 含 Codex；API credits 與 Codex Security 為另行評估福利；依使用情形、生態重要性及維護活動評選，未列固定星數下限。[OpenAI 官方說明](https://developers.openai.com/community/codex-for-oss)
   - **一手來源已確認：** Rust Foundation 公告總額 60 萬美元，包含白金會員資格與額外維護支援。[基金會公告](https://rustfoundation.org/media/rust-foundation-welcomes-openai-as-platinum-member-announces-donation-to-rust-project/)
   - **本次未取得一手確認：** 第二輪名額、鼓勵重新申請、GitHub Sponsors 16 萬美元，以及貼文日期與互動數。搜尋轉述不能提升為一手證據；本次讀取限制本身不列更正。涉及串文與回覆者需 Chrome 道補讀。

4. **任務影響**

   本篇為 `archived`，沒有任務 ID、已完成任務或指定產出檔，`task_impact` 為空。由整合者修正上述 3 處後再審。

```json
{
  "verdict": "changes_requested",
  "source_review": "partial",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第0節將Pro 100資助描述為每月提供100美元額度",
      "problem": "混淆訂閱月費與可支用點數；API credits是另外評估的福利。",
      "evidence": "https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers ; https://openai.com/form/codex-for-oss/",
      "fix": "改為公告當時提供半年Pro 100訂閱，並將API credits另列。"
    },
    {
      "kind": "fact",
      "claim": "第0節將Anthropic的5000星或每月百萬npm下載描述為現行硬門檻",
      "problem": "現行官方資格已有多種途徑及生態影響例外，方案目前稱Claude Ultra。",
      "evidence": "https://claude.com/contact-sales/claude-for-oss ; https://www.anthropic.com/claude-for-oss-terms",
      "fix": "更新現行條件與方案名稱；若比較舊制，標明日期並附歷史來源。"
    },
    {
      "kind": "evidence",
      "claim": "第1節認定資助已常態化並每半年續約",
      "problem": "把本次延續推成固定制度；官方條款未承諾固定半年續辦或續約。",
      "evidence": "https://learn.chatgpt.com/docs/codex-for-oss-terms",
      "fix": "改為本次延續計畫，並說明未確認固定續辦或續約承諾。"
    }
  ],
  "task_impact": []
}
```
