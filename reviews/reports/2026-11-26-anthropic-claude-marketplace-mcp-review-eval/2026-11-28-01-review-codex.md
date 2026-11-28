# 獨立審查報告：2026-11-26-anthropic-claude-marketplace-mcp-review-eval

- reviewer: codex/gpt-6.1-sol@01a22262-4a85-7af3-91ac-7453d3d62738
- content_sha256: e139d90fdbb619269b280c40827d5c5f1368fb2cd97436b689d7dfde378f9348
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 2；source_review: full（作者聲明 full）
- source_ref: codex thread 01a22262-4a85-7af3-91ac-7453d3d62738

---
結論：`changes_requested`，共 **2 處更正**。未修改任何檔案；審查前後內容雜湊均與指定值一致。

1. **原始資料讀完度（source）**

   官方公告與文件可讀；[X 原貼文](https://x.com/claudeai/status/2102840851538080172) 回傳 403，無法核對作者圖片與留言。筆記記載計數 272 則，本次實讀 0 則，計數亦未獨立確認。

   因此本次 **排除 source 範圍**，保留作者的 `full` 聲明，不因存取限制列更正。圖片與留言需 Chrome 道補審。

2. **事實查核（facts）**

   已確認：

   - 公告日期為 2026-09-23，宣稱超過 2,000 項整合；CodeRabbit／Vercel、Power Digital／Snowflake、ThoughtSpot／Snowflake 案例相符。[官方公告](https://claude.com/resources/articles/claude-marketplace)
   - Linked Billing 為 Beta，需直接向 Anthropic 付費；請求在合作夥伴組織執行，客戶 ZDR 等設定不適用，HIPAA／FERPA／CMEK 邊界相符。[官方文件](https://platform.claude.com/docs/en/manage-claude/oauth-apps/linked-billing)
   - MCP 的讀寫分離、Hint 標註、防注入、私有狀態限制及兩階段審查，均有依據。[官方審查清單](https://claude.com/docs/connectors/building/review-criteria)

   **更正 1：採購資格限制漏寫。** 第 0.2 節將承諾額度採購寫成企業可直接使用；官方 FAQ 明列目前為有限預覽，須確認組織與產品資格。應補入限制，避免讀成全面開放。[官方 FAQ](https://claude.com/marketplace/agents-products#frequently-asked-questions)

   **更正 2：安全工具所在 repo 寫錯。** 第 1 節稱安全掃描器為「本庫」工具；它已移至 `SanHsien/agent-safety-checks`。本 repo 的 [AGENTS.md 第 35 行](AGENTS.md#L35) 與[目標文件第 5 行](docs/claude-code-domain-skill-packs-and-mcp-audit.md#L5) 都已記載遷移，且本地舊路徑不存在。應改寫實際歸屬與連結。

3. **證據分級（evidence）**

   - **一手來源已確認**：上述公告、計費邊界及 MCP 規則；產品頁顯示 48 項，Linked Billing 篩選顯示 19 項；服務夥伴分組為 17／43／302。[產品目錄](https://claude.com/marketplace/agents-products)、[計費篩選](https://claude.com/marketplace/agents-products?howYouPay=linkedBilling)、[服務夥伴](https://claude.com/marketplace/service-partners)
   - **二手來源**：本次未以二手資料支持結論。
   - **未獨立確認**：11 月 26 日的目錄歷史計數、33 項採購計數及 X 互動數。現行整合目錄數量已有變動，不能據此認定作者當日記錄錯誤。[現行目錄](https://claude.com/marketplace/connectors-plugins)

4. **任務影響（task_impact）**

   唯一任務 `T-20261126-02` 尚未完成。已讀目標文件 `docs/claude-code-domain-skill-packs-and-mcp-audit.md`，尚無本任務新增小節，因此沒有已完成產出受影響。整合者先修上述兩處，再執行任務。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 2,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 0.2 節 Buy with your commit：企業可直接撥用年度承諾額度採購合作夥伴產品。",
      "problem": "漏列官方明示的有限預覽與資格限制，容易讀成所有企業均已可用。",
      "evidence": "https://claude.com/marketplace/agents-products#frequently-asked-questions",
      "fix": "補明目前為有限預覽，僅合資格組織可將部分承諾額度用於合資格產品；須透過 Request to buy 或帳戶團隊確認。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節將 verify_agent_skill_pack_safety.py 稱為本庫工具。",
      "problem": "工具已移至 SanHsien/agent-safety-checks，本 repo 的 tools/verify_agent_skill_pack_safety.py 不存在。",
      "evidence": "AGENTS.md:35；docs/claude-code-domain-skill-packs-and-mcp-audit.md:5",
      "fix": "改寫為 SanHsien/agent-safety-checks 的安全掃描工具，連結至該 repo 的 tools/verify_agent_skill_pack_safety.py。"
    }
  ],
  "task_impact": []
}
```
