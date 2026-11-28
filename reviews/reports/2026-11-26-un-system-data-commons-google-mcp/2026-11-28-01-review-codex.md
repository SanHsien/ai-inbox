# 獨立審查報告：2026-11-26-un-system-data-commons-google-mcp

- reviewer: codex/gpt-6.1-sol@01a222b2-54e9-7ff3-8746-56018543dee0
- content_sha256: 32ec70e2c1bd163e77cb8c0cf9bac49a037d502d92139b2231e9527bf9f2d089
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 1；source_review: full（作者聲明 full）
- source_ref: codex thread 01a222b2-54e9-7ff3-8746-56018543dee0

---
結論：`changes_requested`，共 1 處更正。未修改任何檔案；內容雜湊與指定值相符。

### 1. 原始資料讀完度（source）

已讀 Google 公告全文，但主視覺圖片讀取失敗，亦未能觀看筆記所述的兩支嵌入影片。公告文字未顯示留言計數或留言區，實際讀到 0 則，不能據此確認總數為 0。

因此本次 **不將 `source` 列入已審範圍**，保留作者的 `full` 聲明，不因審查工具限制列更正。

### 2. 事實查核（facts）

一手來源已確認：

- 公告日期為 2026-09-17，作者為 Prem Ramaswami。
- 平台採用 Data Commons 知識圖譜、自然語言查詢與 MCP；2027 年涵蓋 80% 為目標。見 [Google 公告](https://blog.google/innovation-and-ai/technology/ai/google-un-data-commons-platform/)。
- 26 個 UN 實體參與有 [UN 官方說明](https://transcripts.un.org/en/asset/k1d/k1dzd1svin)支持。
- `agent-toolkit` 的 Apache-2.0 授權與頁面顯示的 149 stars 相符。見 [官方倉庫](https://github.com/datacommonsorg/agent-toolkit)。

平台頁面需要 JavaScript，所附 UN MCP 文件回傳 403；12 主題、各主題數量、2,796 合計、ABAS 七領域、CSV 操作及舊站路徑，本次未能獨立確認。這些存取限制不列為筆記錯誤。

**更正 1：工具預設資料來源與接入條件未交代。**

筆記第 1 節將平台搭配 `agent-toolkit` 描述成可直接供本機 Agent 查詢 UN 資料。官方文件卻明示：MCP 預設查詢 `datacommons.org`，自訂資料實例需要另外設定；套件快速開始亦要求 Data Commons API key。筆記應區分 UN 平台接入與通用工具的預設行為，補上端點、設定及適用的驗證要求，不能只列工具連結就視為 UN 接入方法。

來源：[MCP 官方文件](https://docs.datacommons.org/mcp/)、[套件快速開始](https://github.com/datacommonsorg/agent-toolkit/blob/main/packages/datacommons-mcp/README.md)、[自訂實例設定](https://docs.datacommons.org/custom_dc/mcp.html)。

### 3. 證據分級（evidence）

- **一手來源已確認**：上述公告、功能、目標、參與規模、授權及工具預設行為。
- **二手來源**：Field Guide 自述為非官方獨立指南，不能代替 UN 官方接入規格。見[指南聲明](https://mafiatun.github.io/un-data-commons-field-guide/)。
- **推算／未查證**：平台精確分類數字及本機 Agent 直接接入 UN 實例的可用性；後者須依更正 1 補足條件。

### 4. 任務影響（task_impact）

唯一任務 `T-20261126-06` 尚未完成，沒有已完成產出需要追溯修正。已查看 `docs/free-public-apis.md`，未見 UN Data Commons 條目。

後續新增條目時，應交代更正 1 的接入條件；目前沒有受影響的已完成任務，`task_impact` 留空。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 1,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "evidence",
      "claim": "第 1 節將 UN 平台搭配 agent-toolkit 描述為可直接供本機研究型 Agent 查詢 UN 統計。",
      "problem": "官方 MCP 文件明示預設資料來源為 datacommons.org；查詢自訂實例需要額外設定。套件快速開始亦要求 API key。筆記未區分這些條件，也未提供 UN 實例的具體接入設定。",
      "evidence": "https://docs.datacommons.org/mcp/ ; https://github.com/datacommonsorg/agent-toolkit/blob/main/packages/datacommons-mcp/README.md ; https://docs.datacommons.org/custom_dc/mcp.html",
      "fix": "區分 UN 平台接入與通用 agent-toolkit 的預設行為，補上 UN 端點、自訂實例設定及適用的驗證要求；未完成接入驗證前，改寫為可評估接入。"
    }
  ],
  "task_impact": []
}
```
