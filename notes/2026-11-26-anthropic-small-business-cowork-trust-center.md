---
id: "2026-11-26-anthropic-small-business-cowork-trust-center"
title: "Claude for Small Business（43 工作流／27 整合）與 Anthropic Trust Center 合規安全評析"
source_url: "https://trust.anthropic.com/"
source_platform: "Anthropic Trust Center / Anthropic 企業方案公告"
author: "Anthropic"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
source_review_note: "已透過內建瀏覽器完整檢視 trust.anthropic.com（Overview、Resources、Subprocessors、FAQ、Updates 五大分頁、12×9 合規矩陣與 22 家子處理商），並以 search_web 查證 Claude for Small Business（43 工作流、27 整合與 Cowork Approval Mode）；未申請下載需授權存取之 SOC 2 / Cowork v5 完整 PDF。"
status: pending
cluster: 2
cluster_role: "Claude企業合規"
short_title: "Claude中小企與合規評析"
tags:
  - anthropic
  - claude-cowork
  - claude-for-small-business
  - trust-center
  - compliance
  - soc2
  - iso42001
  - cve-2026-22561
---

# Claude for Small Business（43 工作流／27 整合）與 Anthropic Trust Center 合規安全評析

- **來源頁面**：[Anthropic Trust Center (`trust.anthropic.com`)](https://trust.anthropic.com/)（由 Vanta 驅動）
- **分析日期**：`2026-11-26`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/claude-security-guidance-windows-setup.md`](../docs/claude-security-guidance-windows-setup.md)（本機 Windows Claude 安全指引與安裝檢查）
  - [`notes/2026-11-24-cubelv-handoff-cards-progressive-autonomy.md`](./2026-11-24-cubelv-handoff-cards-progressive-autonomy.md)（多 Agent 人機協作審批與漸進放手對照）
  - [`notes/2026-11-25-kocpc-claude-install-as-app-artifacts-desktop.md`](./2026-11-25-kocpc-claude-install-as-app-artifacts-desktop.md)（Claude Desktop 權限模型與商業方案差異）

---

## 0. 原始資料盤點

### 0.1 Claude for Small Business 擴充重點（`search_web` 查證）
- **規模**：擴充至 **43 個預建工作流**（含週報 Monday Brief、Speed-to-Lead 潛客跟進、月結對帳、行銷與發票支付）與 **27 項整合連接器**，涵蓋 Shopify、Salesforce、Stripe、Square、Xero、Gusto、Zoom、TikTok、Atlassian、Zapier 等。
- **運行載體與防呆**：主要透過 **Claude Cowork** 執行營運／財會／銷售流程，並**預設啟用審核模式（Approval Mode）**——AI 可草擬、規劃或填表，但**所有對外發送、發文或付款動作均須人類點擊核准**後才執行。

### 0.2 Anthropic Trust Center（`trust.anthropic.com` 全分頁實查）
- **六大核心合規認證**：SOC 2 Type II、ISO 27001:2022、**ISO/IEC 42001:2023**（AI 管理系統，將自願性 RSP 交由第三方年度監督稽核）、CSA STAR、HIPAA、FedRAMP High（C4G / Bedrock GovCloud / Vertex Assured Workloads）與 UK Cyber Essentials。
- **HIPAA / BAA 明確邊界**：僅涵蓋 **Claude Enterprise Chat**、**Anthropic 1P API** 與**符合資格且啟用 ZDR（零資料保留）的 Claude Code**；**明確排除 Beta 產品及 Free / Pro / Max / Team 方案**（中小企業用 Team/Pro 接醫療或受監管資料不可誤認具 BAA 保護）。
- **資料保留、加密與訓練政策**：
  - 商業方案（Claude for Work、API）**預設不用客戶對話或 coding sessions 訓練模型**（Enterprise 可關閉回饋）。
  - 客戶刪除資料後，系統最長仍可能保留 **30 天**（觸發 AUP 違規標記除外）。
  - 靜態 **AES-256 GCM**、傳輸 **TLS 1.2+**；推論採**多租戶邏輯隔離**（不提供單租戶實體環境）。
- **關鍵安全公告與文件**：
  - 安全公告區揭露 **`CVE-2026-22561`（Claude for Windows 安裝程式 DLL 搜尋順序劫持漏洞）**。
  - 白皮書清單收錄 `Claude Cowork 桌面安全架構概覽 (v5)`、`Data Handling & Key Management`、`Claude Code FISMA Best Practices (v1.0)`、`Microsoft 365 Connector` 等（部分需 `Request access` 申請）。
- **子處理商與前沿合規**：共列 **22 家子處理商**（GCP/AWS/Azure/Cloudflare、Stripe/WorkOS、Brave Search/TurboPuffer/Parallel Web Systems、ElevenLabs 等）；另有加州 TFAIA (SB 53) / EU AI Act 之 Frontier Compliance Framework（FCF）與 AB 2013 訓練資料摘要。

---

## 1. 與本專案現有架構的對照與啟發

1. **Windows 桌面版安全公告追蹤（`CVE-2026-22561`）**：
   - 本機開發環境為 Windows 11 原生，Trust Center 直接揭露了 Claude for Windows 安裝程式曾有 DLL 搜尋順序劫持漏洞（`CVE-2026-22561`），應納入本庫 Windows 安全檢核提醒（勿從非官方目錄或殘留下載資料夾執行舊版安裝程式）。
2. **商業方案合規邊界釐清**：
   - Team / Pro / Beta 功能（包含部分中小企業導入之 Beta Connectors）**不在 HIPAA BAA 範圍內**，且刪除資料有 30 天殘留期，敏感企業資料導入前須以 ZDR／1P API 或 Enterprise 邊界規劃。
3. **Cowork Approval Mode 與 HITL 一致性**：
   - 與本庫 `T-20261124-02`（CubeLV 交件卡三級放手）相同，涉及對外通訊與金流（Stripe/Square/Xero）時必須保留強制人工核准閘門。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261126-01`**｜**[優先級：低]** 將 Anthropic Trust Center 揭露之 `CVE-2026-22561`（Windows 安裝程式 DLL 劫持）與商業方案資料保留／BAA 排除邊界補入 `docs/claude-security-guidance-windows-setup.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\claude-security-guidance-windows-setup.md`（收錄於集群 2）
  - **執行步驟**：
    1. 在 `docs/claude-security-guidance-windows-setup.md` 新增 Windows Claude 安裝程式防劫持檢核（參考 `CVE-2026-22561`，僅使用官方最新安裝包與乾淨執行目錄）。
    2. 補充 Anthropic Trust Center 商業資料邊界表（30 天刪除殘留期、Free/Pro/Max/Team 與 Beta 排除於 HIPAA BAA 之外、僅 Enterprise / 1P API / ZDR Claude Code 可簽 BAA）。
  - **驗收標準（DoD）**：`docs/claude-security-guidance-windows-setup.md` 完成上述安全與合規邊界補充，且 `python tools/verify_inbox.py` 驗證通過。
