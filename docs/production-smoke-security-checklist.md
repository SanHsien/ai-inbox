# 全端網站上線前 QA 與資安稽核檢核表 (Production Smoke & Security Checklist)

> 本檢核表提煉自 HanSun Architects 全端商業建置架構、Cloudflare Serverless 全家桶（Workers / Pages / KV / D1 / R2）與真實商業上線規範。  
> 適用技術棧：Next.js App Router (TypeScript)、Supabase (PostgreSQL / RLS)、Vercel、Cloudflare Workers (`npx wrangler deploy`)、Stripe / 外部金流。  
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

---

## 6. Cloudflare Serverless (`npx wrangler deploy`) 邊緣部署與配額防呆

採用 Cloudflare Workers 時，另依以下五項人工檢核；本機靜態工具不驗證部署結果。

- [ ] **`.dev.vars` 機密隔離**：本地機密放入 `.dev.vars` 並忽略 `.dev.vars*`；不要將機密放入 `wrangler.toml` / `wrangler.json` / `wrangler.jsonc` 的 `vars` 或 `env.*.vars`。[Cloudflare Secrets](https://developers.cloudflare.com/workers/configuration/secrets/)、[設定格式](https://developers.cloudflare.com/workers/wrangler/configuration/)。
- [ ] **Production 機密注入**：依本檢核表政策，用 `npx wrangler secret put <KEY>` 管理正式環境機密，不隨原始碼提交；此命令由官方 [Secrets 文件](https://developers.cloudflare.com/workers/configuration/secrets/) 說明。
- [ ] **D1 參數化查詢與遷移版控**：本檢核表要求用 `prepare("... ?1").bind(...)` 綁定使用者輸入，並將結構變更寫入遷移檔；API 與 `wrangler d1 migrations apply` 用法見 [Prepared statements](https://developers.cloudflare.com/d1/worker-api/prepared-statements/)、[Migrations](https://developers.cloudflare.com/d1/reference/migrations/)。
- [ ] **KV 最終一致性邊界**：其他地區可能需 60 秒或更久才看見更新，並非 60 秒上限；提高 `cacheTtl` 也會影響快取期限，寫入所在地立即可見亦無保證。本檢核表禁止用 KV 單獨處理庫存扣減、餘額計算或防重放鎖；需要原子操作或交易時應另行設計，官方建議考慮 Durable Objects。[How KV works](https://developers.cloudflare.com/kv/concepts/how-kv-works/)。
- [ ] **R2 公開桶權限**：R2 bucket 預設不公開；本檢核表要求只有公開素材才開啟公開存取，私人檔案另作存取驗證。[Public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)。

### 本機工具的檢查範圍與結束碼

[`check_wrangler_config`](../tools/audit_fullstack_security.py) 以 Python 3.11+ 標準庫 `tomllib` / `json` 解析目標目錄下遞迴找到的所有 `wrangler.toml` / `wrangler.json` / `wrangler.jsonc`（略過 `node_modules` 與 `.git`；目錄走訪失敗視為未完成稽核）；JSONC 會先移除字串外註解及尾端逗號。遍歷 `vars`、`env.*.vars` 及其巢狀值：鍵名含 TOKEN、KEY、SECRET、PASSWORD、CREDENTIAL（不分大小寫）者，所有值型別都報錯（包含空值或佔位符）；所有字串值另掃描 `scheme://user:pass@host` 內嵌帳密與工具列出的金鑰樣式（Stripe `sk_live_`／`rk_live_`／`whsec_`、GitHub `ghp_`／`github_pat_`、`sk-`、`sk-ant-`、`xox[abp]-`、`ya29.`、AWS `AKIA`、PEM 私鑰、Supabase `sbp_`）。`.dev.vars` 與 `.dev.vars.<env>`（`.dev.vars.example` 除外）所在目錄須有 `.gitignore`（根目錄加該目錄各自的檔案，依序套用）忽略它們，以最後一條符合規則為準、`!` 否定規則會把檔案放回未忽略；工具以 `.dev.vars` 與 `.dev.vars.production` 兩個探針代表 `.dev.vars` 與 `.dev.vars.*`，另加實際存在的檔名。`.gitignore` 規則只以檔名比對（`fnmatch`），不實作 git 完整語意（含斜線的路徑規則不會被視為涵蓋）。不執行環境變數替換、不驗證完整 Wrangler schema，也不查雲端權限、D1/KV/R2 或配額。[工具原始碼](../tools/audit_fullstack_security.py)、[回歸測試](../tests/test_audit_fullstack_security.py)、[tomllib](https://docs.python.org/3/library/tomllib.html)。

`python tools/audit_fullstack_security.py --target <目錄>`：exit 0 表示本機規則未命中；exit 1 表示規則命中、路徑無效或設定為空／無法解析／受檢 schema 錯誤；exit 2 是命令列用法錯誤。未使用 Wrangler 的專案不強制提供 Wrangler 檔案；空白專案仍因缺 `.gitignore` 而失敗。這些是本工具契約，不是 Cloudflare 的安全認證。[CLI 實作](../tools/audit_fullstack_security.py)。
