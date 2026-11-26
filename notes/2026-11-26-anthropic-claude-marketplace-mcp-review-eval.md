---
id: "2026-11-26-anthropic-claude-marketplace-mcp-review-eval"
title: "Claude Marketplace 上線評析：2,000+ 生態整合、承諾額度採購、Linked Billing 合規邊界與 MCP 官方審查標準"
source_url: "https://claude.com/blog/claude-marketplace"
source_platform: "Anthropic (claude.com / X @claudeai)"
author: "Anthropic (@claudeai)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 2
source_replies: 2
source_reviewed_at: "2026-11-26"
source_review_note: "已透過內建瀏覽器完整閱讀 X 貼文 2102840851538080172（含配圖與未登入可見之 2 則回覆，頁標 272 則）、claude.com/blog/claude-marketplace（重導向至 resources/articles/claude-marketplace）、claude.com/marketplace 及三大子分頁（connectors-plugins / agents-products / service-partners），並延伸讀取 claude.com/docs/connectors/building/review-criteria 官方審查標準；未另行點擊外部新聞轉載。"
status: pending
cluster: 2
cluster_role: "MCP市集與審查"
short_title: "Claude市集與MCP審查評析"
tags:
  - claude-marketplace
  - anthropic
  - mcp
  - connectors
  - enterprise-procurement
  - linked-billing
  - security-review
---

# Claude Marketplace 上線評析：2,000+ 生態整合、承諾額度採購、Linked Billing 合規邊界與 MCP 官方審查標準

- **官方公告**：[`claude.com/blog/claude-marketplace`](https://claude.com/blog/claude-marketplace)（`2026-09-23` 發布，重導向至 `resources/articles/claude-marketplace`）
- **市集與子頁**：[`claude.com/marketplace`](https://claude.com/marketplace) ｜ [`/agents-products`](https://claude.com/marketplace/agents-products) ｜ [客戶觀點（CodeRabbit / Power Digital / ThoughtSpot）](https://claude.com/blog/how-coderabbit-power-digital-and-thoughtspot-scale-with-snowflake-and-vercel-on-claude-marketplace)
- **X 官方貼文**：[`x.com/claudeai/status/2102840851538080172`](https://x.com/claudeai/status/2102840851538080172)（`92 萬`瀏覽、`5,691` 讚、`272` 則回覆）
- **分析日期**：`2026-11-26`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/claude-code-domain-skill-packs-and-mcp-audit.md`](../docs/claude-code-domain-skill-packs-and-mcp-audit.md)（本庫 MCP 與技能包安全稽核規範目標文件）
  - [`notes/2026-11-26-anthropic-small-business-cowork-trust-center.md`](./2026-11-26-anthropic-small-business-cowork-trust-center.md)（Anthropic Trust Center 合規與 ZDR/HIPAA 邊界）

---

## 0. 原始資料盤點（市集三大目錄、採購雙軌與 MCP 官方審查準則）

### 0.1 市集目錄實查規模（`2026-11-26` 頁面實測）
1. **Connectors & Plugins**：公告整體宣稱逾 2,000 項；`/connectors-plugins` 目錄實測列示 Top connectors `1,227`＋Top plugins `545`（合計 `1,772` 公開可見項，另含 Trending `9` / New `7`，分 17 類），代表包含 Google Workspace、Microsoft 365、Slack、Notion、Figma、Atlassian MCP、HubSpot、Superpowers、Code Review、Context7、Playwright 等。
2. **Agents & Products（`48` 項）**：分 9 類，包含 Cursor、CodeRabbit、GitLab、Lovable、Vercel、Netlify Enterprise、Datadog Agent Observability、CrowdStrike Charlotte AI、Checkmarx、Chainguard、Cyera、Snowflake、ClickHouse Cloud、Harvey、Glean、Zoom Agentic Search 等。
3. **Service Partners（`362` 家）**：分 Global Premier（`17` 家，如 Accenture、Bain、BCG、Capgemini、Cognizant、Deloitte）、Preferred（`43` 家）與 Select（`302` 家）。

### 0.2 雙軌企業採購與計費機制（`Buy with your commit` vs `Link your billing`）
- **Buy with your commit（`33` 項支援）**：企業將已承諾的年度 Anthropic spend 直接撥用於採購合作夥伴產品（例如公告案例：CodeRabbit 用於 Vercel、Power Digital 與 ThoughtSpot 用於 Snowflake），縮短跨廠商合約與採購審批。
- **Link your billing（Beta，`19` 項支援）**：Admin/Billing 透過 Claude Console OAuth App 一次授權連結合作夥伴產品並設每月上限，免分享 API Key；僅限直接由 Anthropic 計費的 Platform 組織（Pro/Max/Ultra/Team/Enterprise 訂閱或雲端代計費不適用）。
- **關鍵合規邊界（官方明示）**：Linked Billing 的請求係在**合作夥伴的組織**內執行，因此**客戶自身的資料保留與 Zero Data Retention (ZDR) 設定不適用**；若工作負載需受 **HIPAA、FERPA 或 CMEK** 涵蓋，官方明確提醒**不可連結計費**。

### 0.3 官方 MCP Connectors 兩階段安全審查規範（`claude.com/docs/connectors/building/review-criteria`）
1. **階段一（自動政策掃描 → Community）**：遠端 MCP Server 經自動掃描後先上架為 Community connector。
2. **階段二（人工功能實測 → Verified）**：高實用度項目升級人工逐一實測工具，僅 **Verified** 標籤可使用 MCP App 嵌入式網站。
3. **硬性安全基準**：
   - **強制讀寫分離**：禁止單一工具同時混用 `GET` 與 `POST/PUT/PATCH/DELETE`；
   - **權限提示必填**：必須提供 `readOnlyHint`／`destructiveHint`；
   - **嚴禁 Prompt Injection 描述**：工具描述不可指示呼叫未經請求之外部工具、干擾其他工具、從外部拉取指令或夾帶隱藏／編碼指令；
   - **禁止窺探私有狀態**：不可查詢 Claude 記憶、對話紀錄或使用者檔案；
   - **領域限制**：網域須為第一方或合法代理 API，且不接受資金／加密貨幣轉移或 AI 影音圖片生成類連接器。

---

## 1. 與本專案現有架構的對照與啟發

1. **MCP 安全審查基準可直接落實為本庫檢核規則**：
   - Anthropic 官方公開的 `review-criteria` 具體列出了可機械化驗證的原則：**單一工具讀寫分離**、**強制 `readOnlyHint`/`destructiveHint` 標註**、**工具描述 Prompt Injection 模式掃描**與**禁止讀取記憶／對話紀錄**——這四條與本庫 `verify_agent_skill_pack_safety.py` 及 MCP 開發規範高度契合。
2. **企業多方代理計費的 ZDR 斷點警覺**：
   - 使用 Linked Billing 等跨組織代理計費機制時，資料保留與 ZDR 邊界會切換至合作夥伴組織，受監管資料（HIPAA/CMEK）不可輕易串接。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261126-02`**｜**[優先級：中]** 萃取 Anthropic 官方 MCP Connectors 安全審查標準（讀寫分離、`readOnlyHint`/`destructiveHint`、Prompt Injection 禁令）與 Linked Billing 合規斷點，補入 `docs/claude-code-domain-skill-packs-and-mcp-audit.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\claude-code-domain-skill-packs-and-mcp-audit.md`（收錄於集群 2）
  - **執行步驟**：
    1. 在 `docs/claude-code-domain-skill-packs-and-mcp-audit.md` 新增「官方 MCP Connectors 上架與自檢安全標準（對應 `review-criteria`）」小節，收錄讀寫工具分離、Hint 標註、工具描述防注入及禁讀記憶／對話紀錄規則。
    2. 補充 Claude Marketplace 雙軌採購（Committed Spend vs Linked Billing Beta）的 ZDR／HIPAA／FERPA／CMEK 排除邊界提醒。
  - **驗收標準（DoD）**：`docs/claude-code-domain-skill-packs-and-mcp-audit.md` 完成上述安全基準與合規邊界補充，且 `python tools/verify_inbox.py` 驗證通過。
