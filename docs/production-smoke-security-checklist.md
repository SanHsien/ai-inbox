# 全端網站上線前 QA 與資安稽核檢核表 (Production Smoke & Security Checklist)

> 本檢核表提煉自 HanSun Architects 全端商業建置架構與真實商業上線規範。  
> 適用技術棧：Next.js App Router (TypeScript)、Supabase (PostgreSQL / RLS)、Vercel、Stripe / 外部金流。  
> 交付形式：以 `ai-inbox` 範本（`docs/production-smoke-security-checklist.md`）交付，搭配標準庫稽核腳本 `tools/audit_fullstack_security.py` 進行自動化驗證。

---

## 1. 環境變數與機密隔離 (Secrets & Environment)

- [ ] **`.gitignore` 完整覆蓋**：確認 `.env`, `.env.local`, `.env.production`, `.env.*.local` 皆已列入 `.gitignore`，嚴禁提交至 Git 倉庫。
- [ ] **`.env.example` 乾淨檢查**：確認 `.env.example` 僅包含鍵名與說明佔位符號（如 `NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co`），絕無任何真實 Token、金鑰或密碼。
- [ ] **Client 前綴防禦（NEXT_PUBLIC_ 隔離）**：
  - 只有公開的 URL、公開 Anon Key、公開 Google Analytics ID 允許加上 `NEXT_PUBLIC_`。
  - 後端專用金鑰（`SUPABASE_SERVICE_ROLE_KEY`, `STRIPE_SECRET_KEY`, `LINE_PAY_SECRET`, `RESEND_API_KEY`）**絕對不可加上 `NEXT_PUBLIC_` 前綴**。
- [ ] **Client Component 代碼審查**：搜尋所有包含 `"use client"` 的檔案，確認未直接或間接引用後端專用 Keys。

---

## 2. 資料庫與 Supabase RLS 安全 (Database & RLS)

- [ ] **全表 RLS 啟用**：所有在 `public` schema 建立的資料表，必須強制執行：
  ```sql
  ALTER TABLE public.<table_name> ENABLE ROW LEVEL SECURITY;
  ```
- [ ] **零未授權寫入 (No Wildcard INSERT/UPDATE)**：
  - 公開註冊/報名表：僅允許插入特定白名單欄位，或透過受保護的 Server Action 代理寫入。
  - 嚴禁 `FOR ALL USING (true) WITH CHECK (true)` 這種無限制開放策略出現在核心資料表。
- [ ] **不可變歷史資料表保護**：`registration_events` 等審計日誌表，不可對公開 Role 開放 `UPDATE` 或 `DELETE`，僅允許 `service_role` 插入。
- [ ] **Production Migration 腳本化**：所有資料表結構與 RLS 變更皆需有版控的 `.sql` 遷移腳本，嚴禁在 Production Supabase Dashboard 手動修改。

---

## 3. 商業金流與 Webhook 防竄改 (Payment & Webhook Security)

- [ ] **伺服器重算價格 (Pricing Snapshot)**：
  - 前端傳入的商品金額、折扣額度永遠視為不可信。
  - 伺服器端必須依據 DB 原始價格與有效促銷活動重新計算應付金額，並將快照寫入資料庫。
- [ ] **Webhook 簽名驗證 (Signature Verification)**：
  - 所有來自 Stripe、LINE Pay 等第三方金流的 Webhook 回調端點，必須讀取原始 Raw Body 校驗簽名頭（如 `stripe-signature`）。
  - 簽名失敗立即回傳 HTTP 400 並終止處理。
- [ ] **金額雙重核算 (Amount Reconciliation)**：
  - Webhook 收到付款成功通知時，校驗回傳的支付金額是否與資料庫中對應訂單的 `pricing_snapshot.final_payable_amount` 完全一致。
- [ ] **冪等性處置 (Idempotency)**：
  - 相同交易 ID 或已處於 `paid` 狀態的訂單重複收到通知時，安全回傳 200，不重複觸發發信或贈點等副作用。

---

## 4. 前端防刷與介面安全 (Frontend & Anti-Spam)

- [ ] **人機驗證 (Turnstile / reCAPTCHA)**：公開表單（如諮詢、報名、登入）已接入 Cloudflare Turnstile 或同等無感人機驗證，防止自動化機器人洗單。
- [ ] **API 速率限制 (Rate Limiting)**：敏感 API（如發送驗證碼、忘記密碼、送出訂單）已設定 IP 或帳號維度的 Rate Limit。
- [ ] **CORS 與安全 Headers**：
  - 啟用 `X-Frame-Options: DENY`（防點擊劫持 Clickjacking）。
  - 啟用 `X-Content-Type-Options: nosniff`。
  - 設定嚴格的 `Content-Security-Policy (CSP)`。

---

## 5. 部署前 Smoke Test 與健康檢查 (Production Smoke Test)

- [ ] **本機嚴格編譯驗證**：在推送到遠端前，於本機終端執行完整建置：
  ```bash
  npm run build
  ```
  確認零 TypeScript 類型錯誤、零 ESLint 嚴重警告。
- [ ] **Vercel Preview 分支煙霧測試**：在 Preview 部署環境手動驗收核心黃金路徑（Golden Path）：
  1. 首頁與各語系切換正常，無版面錯位。
  2. 點選課程/商品並進入報名流程，填寫表單能順利建立 `pending` 訂單。
  3. 模擬或以測試金流（Test Mode）完成結帳，訂單狀態正確躍遷至 `paid`。
  4. 確認 Email 或 LINE 成功收到開課/購買確認通知。
  5. 測試後台管理者（Admin）頁面，確認非管理員帳號無法存取。
- [ ] **零停機發布與即時回滾準備**：確認 Production 環境環境變數已同步配置完畢，並已知曉 Vercel 一鍵 Instant Rollback 的操作入口。
