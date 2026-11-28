# 獨立審查報告：2026-11-24-lichangzhang-4-ai-employees-workflow-patterns

- reviewer: codex/gpt-6.1-sol@01a2224e-594e-72e2-aed5-2028e1dc3044
- content_sha256: 2546f87abf98980fa037cb593547ee85b91c6219f5e5fe61d534b1512c14b0ae
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: partial（作者聲明 partial）
- source_ref: codex thread 01a2224e-594e-72e2-aed5-2028e1dc3044

---
結論：**changes_requested，共 3 處更正**。內容雜湊與指定值一致；未修改任何檔案。

### 1. 原始資料讀完度

已重新開啟[原始影片](https://youtu.be/0X5CVapfqPQ)，但頁面未提供可讀的影片內容、資訊欄及留言；下載工具亦遭網路限制。未取得逐字稿、畫面或留言。

- 平台留言計數：無法讀取，不能獨立確認筆記所列 83 則。
- 本次實讀留言：0 則；作者圖片：0 張。
- `source` 排除於本次 scope；保留作者的 `partial`，不把存取失敗列為更正。
- 頻道身分、發布日、片長、觀看數、章節與作者留言內容，均未獨立確認。

### 2. 事實查核

**更正 1：存入草稿箱不屬於唯讀操作。**

筆記第 1.1 節稱「唯讀分類＋草稿」，卻要求把回覆存入 Gmail 草稿箱。Google 官方將讀取與草稿管理區分為不同權限；`gmail.compose` 還包含寄信能力。提示詞禁止寄信，不等於帳號沒有寄信權限。

建議區分：

```text
唯讀取信 → 對話內擬稿 → 授權儲存草稿 → 另行核准寄送
```

出處：[Google Gmail 權限文件](https://developers.google.com/workspace/gmail/api/auth/scopes)、[Claude Google Workspace 說明](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors)。

**更正 2：工具費用不能一概列為每月約 20 美元。**

第 0 節將橫評工具概括為均需付費方案，但 Meta 在 Muse 發布公告明載：多數需求可免費使用，另提供訂閱方案。即使這是留言轉述，也應加上官方核對結果，避免變成購買依據。

出處：[Meta Muse 發布公告](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)。

其餘統計核對結果：

- 微軟官方確實列出每日 117 封郵件及 275 次干擾；後者是依會議、郵件、聊天通知計算的指標，不能直接當作每個人的實測值。[微軟原報告](https://www.microsoft.com/en-us/worklab/work-trend-index/breaking-down-infinite-workday/)
- JDP 原文列有 93% 面試焦慮、70% 出聲練習，調查人數為 2,018 人。[JDP 原文](https://www.jdp.com/blog/how-to-prepare-for-interviews-2020/)
- Pew 的 64%／39% 分別指一般民眾與 AI 專家，認為未來二十年美國工作機會將減少的比例。[Pew 原報告](https://www.pewresearch.org/internet/2025/04/03/public-and-expert-predictions-for-ais-next-20-years/)

### 3. 證據分級

- **一手已確認**：上述權限規則、Muse 免費使用條件及三組調查數字。
- **二手轉述**：筆記描述的影片工作流、作者留言、工具排序與安全疑慮；本次無法確認轉述是否忠實。
- **推算／未查證**：每週省八小時的實際成效、提示詞降低返工的幅度，以及跨模型分歧與真實風險的關係。

**更正 3：跨模型分歧被寫成風險判準。**

第 1.3、2 節把模型意見不同直接連到真正風險，未提供驗證依據。這只能列為待核對的線索；一致也不能據此放行。

建議改為：「模型分歧可列為人工複核候選，仍須回到原文與一手資料判斷。」

出處：`notes/2026-11-24-lichangzhang-4-ai-employees-workflow-patterns.md:77`、同檔第 90 行。這是證據分級問題，不宣稱已證明該方法無效。

### 4. 任務影響

本篇僅有 **`T-20261124-03`，尚未完成**，沒有已完成任務的產出需要回溯修正。

已開啟目標文件 `docs/agent-memory-and-prompting-best-practices.md`，未找到本篇相關模式已落地的內容。整合前應先修正權限階梯與模型分歧的表述；`task_impact` 留空。

```json
{
  "verdict": "changes_requested",
  "source_review": "partial",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 1.1 節將郵件分類並存入 Gmail 草稿箱列為唯讀階段。",
      "problem": "儲存草稿是寫入操作；gmail.compose 同時包含草稿管理及寄信能力，提示詞禁寄不等於權限隔離。",
      "evidence": "https://developers.google.com/workspace/gmail/api/auth/scopes",
      "fix": "分開描述唯讀取信、對話內擬稿、授權儲存草稿及另行核准寄送，交代實際工具權限。"
    },
    {
      "kind": "fact",
      "claim": "第 0 節工具橫評將各工具概括為均需每月約 20 美元付費方案。",
      "problem": "Meta Muse 發布公告提供多數需求可免費使用的條件，不能概括為所有工具均須付費。",
      "evidence": "https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/",
      "fix": "保留為作者留言轉述並補官方更正；費用與使用資格按產品、日期及地區分列。"
    },
    {
      "kind": "evidence",
      "claim": "第 1.3、2 節將跨模型分歧視為真正風險的判準。",
      "problem": "未附驗證依據，將經驗法則寫成事實語氣；目前無法查證分歧能可靠辨識真實風險。",
      "evidence": "notes/2026-11-24-lichangzhang-4-ai-employees-workflow-patterns.md:77; notes/2026-11-24-lichangzhang-4-ai-employees-workflow-patterns.md:90",
      "fix": "標為作者建議或待驗證方法；分歧只用來產生複核候選，一致不作為放行證據。"
    }
  ],
  "task_impact": []
}
```
