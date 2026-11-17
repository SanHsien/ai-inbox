---
id: 2026-10-17-hansun-fullstack-agent-deployment-manual
title: "HanSun 網站從零建置與部署技術手冊：Next.js、Supabase、Vercel 與 Agent Workflow"
source_url: "https://www.hansunarchitects.com/zh-TW/knowledge/hansun-website-build-deployment-technical-manual-2026"
source_platform: "Web / Blog"
author: "HanSun Architects (瀚森建築)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: "4"
cluster_role: "全端部署與自動化落地"
short_title: "HanSun 全端建置部署手冊"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 0
source_replies: 0
tags:
  - fullstack-architecture
  - agent-workflow
  - supabase
  - vercel
  - nextjs
  - security-audit
---

# HanSun 網站從零建置與部署技術手冊：Next.js、Supabase、Vercel 與 Agent Workflow

- **來源連結**：[HanSun Architects 知識文章](https://www.hansunarchitects.com/zh-TW/knowledge/hansun-website-build-deployment-technical-manual-2026)
- **發表作者**：`HanSun Architects (瀚森建築)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 0. 原始資料盤點

> 2026-11-16 重審：官網文章全文（十章，2026-10-15 發布）讀過。文章沒有留言區。文末另有一份放在 Google Drive 的完整手冊（Word 檔），依本 repo 規則不下載，**沒有看**。
> 2026-11-17 補讀：那份 Word 完整手冊（檔名標 2026-06-09 版，十三章，自稱「內部技術交接文件，已去識別化」）用 Google 文件的線上檢視頁全文讀完，沒有下載。文件內沒有圖，只有表格與指令區塊。

- **作者圖片**：文章內文沒有圖，沒有架構圖或截圖。頁面上唯一的圖是文末的官方 LINE QR Code，與內容無關，不計。
- **作者留言補充**：無。文末只有官方 LINE 的加入說明與防詐提醒。
- **Word 完整手冊重點**（2026-11-17 補讀；官網文章是它的精簡版，以下只列文章沒有的）：
  - 技術版本寫得更細：Next.js 16 App Router、React 19、Tailwind CSS 4；金流是 Stripe、LINE Pay 與 ATM 轉帳核帳三種；通知用 Nodemailer 加 LINE；另有 Cloudflare Turnstile、CSP、HSTS、rate limit。
  - **第 12 章「Agent Workflow 與 TODO Tree」**：列了 **6 個 Agent 角色**（PM、Backend、Frontend、QA、Ops、Security）與各自責任、一份 P0～P7 的分階段待辦樹，以及 5 條給 Cursor／Codex 的規則（改金額要同時改計價、對帳、匯出、學員看板與測試；動報名資料先查再改並寫明原因；client component 不得引入 service role；新增 API 要先定義驗證、限流、錯誤處理與紀錄；部署前至少跑 build 與相關測試）。
  - 文章沒提的防呆與安全細節：**匯出 CSV 要防公式注入**（以 `=`、`+`、`-`、`@` 開頭的儲存格）；`NEXT_PUBLIC_*` 變數瀏覽器讀得到，不可放 secret；同課程同 Email 同電話、未付款且未填末五碼的舊報名會被新報名取代；同 Email 不能重複用同一張折價券；Vercel 排程用 UTC，要自己換算營運時區；對帳以已付款報名的 `charged_amount` 加總為準。
  - 附了兩支專用測試指令（課程容量、團報與折價券金額）與常見事件的排查順序。
- **網友留言重點**：無（頁面沒有留言功能）。
- **對分析的影響**：
  - **1.3 節「作者提煉的 6 大 Agent 轉化實踐模式」在網頁文章裡找不到**。文章十章是：學習目標、建置順序、系統與資料流、資料庫與 Migration、報名價格與折價券、金流與通知、Vercel 部署、QA 與安全交接、學員檢查清單、參考文件，沒有 Website Builder Agent、SaaS 範本這六項。可能出自沒看的 Word 完整版，也可能是當初分析時自行延伸。已在 1.3 節標明出處未查證；標題原本也寫了「6 大 Agent 轉化實踐」，已拿掉，改用官網文章自己的標題（`<h1>`：「HanSun 網站從零建置與部署技術手冊｜Next.js、Supabase、Vercel 與 Agent Workflow」）。
  - 1.1 節三處與原文不符，已改：文章定位是「學員專屬」教材，沒有提團隊是否為非工程背景；通知寫的是 Email／LINE，沒有指名 LINE Notify；回滾寫的是「回到上一個已驗證版本」，沒有說零停機。
  - 文章有而原筆記沒寫的做法，補進 1.1 節：建置順序是「先資料模型再 UI、先後端計價再前台顯示」；Webhook 除了簽章還要核對金額、幣別、課程與 Email；GitHub 用私有 repo 加明確的正式分支。
  - 兩個已完成任務依據的價格快照、軟刪除、RLS、Webhook 驗證、檢查清單，文章裡都有，不受影響。
  - **2026-11-17 補讀後定案：1.3 節那六項在 Word 完整手冊裡也沒有**，確定是當初分析時自行延伸，不是作者的主張。Word 手冊裡數量同樣是「6」的是第 12 章的六個 Agent 角色，內容完全不同；1.3 節已改寫，把作者真正寫的六個角色與五條規則補上，原六項降為「本筆記的延伸構想」。
  - Word 手冊的 CSV 公式注入防護、`NEXT_PUBLIC_*` 不放 secret、排程時區換算三項，已完成任務 `T-20261017-24` 的產出 `docs/production-smoke-security-checklist.md` 沒有涵蓋；任務狀態不動，列入回報由整合者決定是否補進檢核表。

---

## 1. 核心內容摘要與技術深挖

### 1.1 案例背景：非傳統工程團隊透過 Agent 打造商業級全端系統
- **背景**：台灣建築事務所「HanSun Architects（瀚森建築）」把自家官網（多語系、學員登入、課程報名、多元金流、後台管理）的建置與部署做法，寫成給課程學員的技術手冊，工作流用到 **Codex 與 Claude Code**。文章沒有說明團隊的工程背景；「建築事務所所以非工程背景」是推測。
- **技術架構全貌**：
  - **前端展示與路由**：Next.js App Router (TypeScript) + Tailwind CSS + Framer Motion + `next-intl` (多語系繁中/EN/日文)。
  - **資料層與儲存**：Supabase PostgreSQL + Storage + Migration 腳本化管理 + RLS (Row Level Security)。
  - **金流結算與對帳**：Stripe、LINE Pay、ATM 銀行轉帳（末五碼人工核對）+ 後端防竄改 `pricing_snapshot` 機制。
  - **通知與防護**：Nodemailer (Email)、LINE 通知（文章未指名用哪個 LINE 服務）、Turnstile (人機防刷)。
  - **部署與維運**：Vercel (Preview、Production、監控與回滾；回滾是回到上一個已驗證版本)；GitHub 用私有 repo 加明確的正式分支。
  - **建置順序（文章第二章）**：先做資料模型與 db adapter 再做 UI；先做課程 CRUD 再做報名表；先做後端計價再接前台顯示；先有價格快照再做匯出與對帳；測試與 build 通過後才部署正式環境。
  - **Webhook 驗證範圍（文章第六章）**：Stripe／LINE Pay 的請求、確認與 webhook 都要核對金額、幣別、課程編號、Email 與 webhook secret，不只驗簽章。

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

### 1.3 作者寫的 Agent 分工，與本筆記的延伸構想

**作者實際寫的**（Word 完整手冊第 12 章，2026-11-17 補讀）：把建站工作分給六個 Agent 角色——PM（拆需求、排優先級、維護待辦樹、確認驗收標準）、Backend（API、資料模型、migration、金流 webhook、安全邏輯）、Frontend（公開頁、報名表、學員看板、後台介面）、QA（測試腳本、build、資料一致性、對帳抽查）、Ops（Vercel、Supabase、網域、環境變數、回滾、監控）、Security（secret 掃描、RLS、CSP、限流、個資與匯出安全），搭配 P0～P7 的分階段待辦樹與五條給 Cursor／Codex 的規則（見第 0 段）。

> ⚠️ 以下六項**不是作者的主張**：2026-11-16 重審時在官網文章找不到，2026-11-17 讀完 Word 完整手冊也沒有，確定是當初分析時自行延伸。保留作為本筆記的延伸構想，不可當成作者的說法引用。

原筆記寫：作者將這份從實戰中淬鍊的手冊，抽象出 6 種極具商業價值的 AI 延伸應用：
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
