---
id: 2026-10-17-hansun-fullstack-agent-deployment-manual
title: "HanSun 全端網站從零建置部署手冊：Codex/Claude 驅動的商業系統架構與 6 大 Agent 轉化實踐"
source_url: "https://www.hansunarchitects.com/zh-TW/knowledge/hansun-website-build-deployment-technical-manual-2026"
source_platform: "Web / Blog"
author: "HanSun Architects (瀚森建築)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: 4
cluster_role: "全端部署"
short_title: "HanSun 全端建置部署手冊"
tags:
  - fullstack-architecture
  - agent-workflow
  - supabase
  - vercel
  - nextjs
  - security-audit
---

# HanSun 全端網站從零建置部署手冊：Codex/Claude 驅動的商業系統架構與 6 大 Agent 轉化實踐

- **來源連結**：[HanSun Architects 知識文章](https://www.hansunarchitects.com/zh-TW/knowledge/hansun-website-build-deployment-technical-manual-2026)
- **發表作者**：`HanSun Architects (瀚森建築)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要與技術深挖

### 1.1 案例背景：非傳統工程團隊透過 Agent 打造商業級全端系統
- **背景**：台灣建築事務所「HanSun Architects（瀚森建築）」團隊由非傳統軟體工程師背景出發，深度借助 **Codex 與 Claude Code**，從零完整建置並維運具備高專業度、多語系、會員登入、課程報名、多元金流與後台管理的官方正式商業網站。
- **技術架構全貌**：
  - **前端展示與路由**：Next.js App Router (TypeScript) + Tailwind CSS + Framer Motion + `next-intl` (多語系繁中/EN/日文)。
  - **資料層與儲存**：Supabase PostgreSQL + Storage + Migration 腳本化管理 + RLS (Row Level Security)。
  - **金流結算與對帳**：Stripe、LINE Pay、ATM 銀行轉帳（末五碼人工核對）+ 後端防竄改 `pricing_snapshot` 機制。
  - **通知與防護**：Nodemailer (Email)、LINE Notify、Cloudflare Turnstile (人機防刷)。
  - **部署與維運**：Vercel (Preview 分支驗證、Production 部署、Log 監控與零停機回滾)。

### 1.2 商業系統資料流與安全邊界可視化

```text
┌────────────────────────────────────────────────────────────────────────┐
│             HanSun 全端商業系統與 Agent 安全交付架構                   │
└────────────────────────────────────────────────────────────────────────┘

 [訪客 / 學員瀏覽器] (Client Bundle)
        │
        │ 1. 提交報名表 (含折價券、梯次、聯絡資訊)
        ▼
 ┌───────────────────────────────────────────────────────────────────┐
 │ Next.js Server App Router (Server Environment)                    │
 │ ├─ 2. 嚴格驗證身分、Cloudflare Turnstile 人機防刷                  │
 │ ├─ 3. 後端重新計算價格 (忽略前端金額，防偽造)                     │
 │ ├─ 4. 生成不可變的 pricing_snapshot (單價/早鳥/折抵/總計)         │
 │ └─ 5. 簽署付款 Intent (Stripe / LINE Pay / ATM 待審)              │
 └──────────────────┬────────────────────────────────────────────────┘
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
 ┌──────────────┐          ┌──────────────────────────────────────┐
 │ Supabase DB  │          │ 金流與通知 (Stripe / LINE / Email)   │
 │ ├─ courses   │          ├─ Webhook 簽名校驗 (金流回調)         │
 │ ├─ registers │          ├─ 金額與 pricing_snapshot 一致性對帳 │
 │ └─ RLS 安全  │          └─ 寄發購課成功/開課憑證通知           │
 └──────────────┘          └──────────────────────────────────────┘
        ▲
        │ 嚴格隔離：Service Role 僅限 Server 端，嚴禁進入 Client
 ┌──────┴────────────────────────────────────────────────────────────┐
 │ Coding Agent 交付檢查門閘 (Agent Workflow Checklist)               │
 │ ├─ 1. .env.local / Secrets 零洩漏檢查 (Git 屏蔽)                   │
 │ ├─ 2. 本機 npm run build 通過驗證                                  │
 │ ├─ 3. Migration 腳本化套用 (禁止手動改 Production 表結構)          │
 │ └─ 4. Production Smoke Test (首頁、報名、登入、匯出)              │
 └───────────────────────────────────────────────────────────────────┘
```

### 1.3 作者提煉的 6 大 Agent 轉化實踐模式
作者將這份從實戰中淬鍊的手冊，抽象出 6 種極具商業價值的 AI 延伸應用：
1. **Website Builder Agent**：輸入網站需求，AI 自動規劃專案目錄、Supabase 資料庫綱要、前後端代碼與部署驗收清單。
2. **SKILLS 技能套件**：將知識拆解為可被 Codex / Claude Code 直接調用的標準化 `SKILL.md`（如初始化、Supabase Migration、金流整合、資安檢查）。
3. **AI 網站管理控制台 (Admin CMS)**：可視化監控文章、學員報名、資料庫健康度與日誌。
4. **AI 互動式教學平台**：手冊轉化為分階段實作練習與 AI 助教指導。
5. **網站 QA 與資安稽核 Agent**：自動檢測路由、RLS 權限、Webhook 簽名與環境變數隔離。
6. **網站 SaaS 範本**：提煉為建築師事務所、設計公司或講師的小型企業可複製範本。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與 `RULE[user_global]` 嚴格呼應**：手冊強調「禁止把 `.env.local`、API key、Service Role、Webhook secret、學生個資放進 Git、對話或截圖」，與全域協作規範中的「API key、token、私鑰不進程式碼、不進指令列、不進對話」完全一致。
  - **與 `verification-protocol` 呼應**：手冊強調上線前必須本機 `npm run build`、跑測試腳本並執行 Smoke Test，禁止直接在 Production 盲目修改。
  - **定價快照防竄改思維（Pricing Snapshot）**：前端傳入的金額永遠視為無效估計，所有商業結算以伺服器端資料庫計算並寫入 Snapshot 為唯一準則，避免前端遭惡意竄改。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **Agent 建站標準流水線（SOP）**：將 Next.js + Supabase + Vercel 的起手式與驗證順序收斂為標準 Agent 流程。
    2. **金流與資安稽核清單**：將手冊中的「學員實作檢查清單」轉化為自動化驗收腳本或檢核清單。
  - **適用性界線**：
    - 一般輕量工具或展示頁不需要重型的 Supabase + Stripe 金流；此手冊適合作為「具備商業交易、資料庫持久化與會員權限」的中型全端專案的黃金參考標準。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-23`**｜**[優先級：高]** 建立「全端商業建站 Agent 技能規格（Fullstack Website Builder SKILL.md）」
  - **完成日期**：2026-10-23
  - **目標範圍**：`C:\GitHub\ai-inbox\notes\` 與全端專案架構規範
  - **具體實作步驟**：
    1. 參考 HanSun 架構，提煉出 Next.js App Router + Supabase + Vercel 的標準化 Agent 指引。
    2. 規範資料層設計守則：強制包含軟刪除（Soft Delete）、價格快照（Pricing Snapshot）、關聯事件記錄（Registration Events）。
    3. 規範狀態管理：定義訂單生命週期狀態機（Pending -> Verified/Paid -> Canceled）。
  - **驗收標準（DoD）**：產出完整的 Fullstack Builder 規範文檔，具備端到端資料流與防呆指南。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `templates/fullstack-website-builder-skill.md`，完整制定 Fullstack Builder 技能規範，包含 Next.js+Supabase 資料層守則（軟刪除、定價快照、事件流水帳）、訂單確定性狀態機與 Webhook 簽名對帳防呆。

- [x] **`T-20261017-24`**｜**[優先級：中]** 實作「全端網站上線前 QA 與資安稽核檢核表 (Production Smoke & Security Checklist)」
  - **完成日期**：2026-10-23
  - **目標範圍**：驗收檢查協議 / CI 工具
  - **具體實作步驟**：
    1. 整理資安與上線硬性檢查項目：
       - (a) `.env.example` 僅含變數名稱，無實體 Secret。
       - (b) Client Component 嚴禁引入 Supabase `service_role` 或後端專用 Keys。
       - (c) 所有公開可寫入表必須啟用 RLS 政策。
       - (d) Webhook 端點必須包含簽名驗證（Signature Verification）。
    2. 提供可由 Agent 在部署前快速自檢的 Markdown Check-list 與檢查指令。
  - **驗收標準（DoD）**：在本地專案中依檢核表執行檢查，能有效阻絕未授權存取與機密洩漏風險。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `docs/production-smoke-security-checklist.md`，並附 stdlib 稽核腳本 `tools/audit_fullstack_security.py` 與單元測試 `tests/test_audit_fullstack_security.py`（6/6 通過），覆蓋 .gitignore、.env.example、Client 端機密防護與 SQL RLS 策略。
