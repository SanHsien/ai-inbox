---
name: fullstack-website-builder
description: Standard operating procedure and architecture specification for building, auditing, and deploying production-grade commercial fullstack websites using Next.js App Router, Supabase, and Vercel. Enforces deterministic pricing snapshots, soft delete, audit event logs, order state machines, and strict RLS policies.
---

# Fullstack Website Builder Agent Skill (全端商業建站技能規格)

> 本技能規格提煉自非傳統工程團隊借助 AI 成功建構商業級系統之實戰手冊（HanSun 全端網站部署架構）。  
> 適用技術棧：**Next.js App Router (TypeScript) + Supabase (PostgreSQL / Storage / Auth) + Vercel**。  
> 交付形式：以 `ai-inbox` 範本（`templates/fullstack-website-builder-skill.md`）交付，可直接複製至專案或 Agent 技能庫中。

---

## 1. 核心架構原則與安全邊界

```text
┌────────────────────────────────────────────────────────┐
│ 全端商業建站三大不妥協原則                              │
├────────────────────────────────────────────────────────┤
│ 1. 零信任前端金額：價格由伺服器重算，寫入不可變快照     │
│ 2. 嚴格權限隔離：service_role 禁入 Client，全表 RLS 防護│
│ 3. 審計追蹤無遺漏：全面軟刪除 + 不可變事件流水帳        │
└────────────────────────────────────────────────────────┘
```

1. **零信任前端金額（Ignore Client-Supplied Price）**：
   - 瀏覽器傳入的任何 `total_amount`、`discount` 均視為惡意偽造候選值。
   - 伺服器端（Next.js Server Action 或 Route Handler）必須根據商品 ID / 課程 ID、當前時間、有效折價券重新計算實付總額，並立即生成不可變的 **`pricing_snapshot` (JSONB)** 存入資料庫。
2. **金鑰嚴格分層隔離**：
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`：僅限 Client 端公開讀取已受 RLS 保護的公開資源。
   - `SUPABASE_SERVICE_ROLE_KEY`：**絕對不可加上 `NEXT_PUBLIC_` 前綴**，僅限在 Server 端（Route Handlers / Webhooks）作為管理員權限使用。
3. **資料持久化防呆原則**：
   - **軟刪除（Soft Delete）**：業務核心資料表（訂單、用戶、課程）一律具備 `deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL`，查詢預設過濾 `deleted_at IS NULL`。
   - **事件審計（Event Ledger）**：關鍵業務狀態躍遷必須伴隨不可變的 `registration_events` 流水帳。

---

## 2. 訂單生命週期狀態機 (Order State Machine)

商業訂單流轉必須嚴格遵循單向確定性狀態機，禁止非法跨躍遷：

```text
       [學員填表提交]
              │
              ▼
       ┌──────────────┐
       │   pending    │ 建立訂單，生成 pricing_snapshot，等待付款/審核
       └──────┬───────┘
              │
      ┌───────┴────────────────────────┐
      │ (Webhook 簽章通過 / ATM 對帳核准)│ (超時未付 / 使用者手動取消)
      ▼                                ▼
┌──────────────┐                 ┌──────────────┐
│  paid /      │                 │   canceled   │
│  verified    │                 └──────────────┘
└──────┬───────┘                        │ (不可逆)
       │ (申請退課 / 爭議退款)           ▼
       ▼                             [TERMINATED]
┌──────────────┐
│   refunded   │
└──────────────┘
```

| 狀態 (Status) | 定義說明 | 允許的下一個狀態 | 觸發條件與權限 |
| :--- | :--- | :--- | :--- |
| **`pending`** | 初始建立，待付款或待審核 | `paid`, `verified`, `canceled` | 伺服器端建立訂單；Client 僅能讀取自己的訂單 |
| **`paid`** | 線上金流（Stripe / LINE Pay）付款成功 | `refunded` | 僅限已驗證簽名的金流 Webhook 觸發躍遷 |
| **`verified`** | 實體轉帳（ATM 末五碼）經管理員人工核對入帳 | `refunded` | 僅限後台管理者（Admin）登入後手動核准 |
| **`canceled`** | 逾期未付（如 24 小時未轉帳）或用戶自行取消 | *(終態)* | 系統定時排程或用戶於 pending 時手動取消 |
| **`refunded`** | 全額或部分退款完成 | *(終態)* | 僅限管理員於後台處理退款後觸發 |

---

## 3. Supabase 資料庫核心綱要範本 (DDL)

```sql
-- 1. 啟用 UUID 擴充
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. 課程/商品表 (Courses)
CREATE TABLE public.courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    base_price INTEGER NOT NULL CHECK (base_price >= 0),
    early_bird_price INTEGER,
    early_bird_deadline TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

-- 3. 報名/訂單表 (Registrations)
CREATE TABLE public.registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES public.courses(id),
    user_id UUID REFERENCES auth.users(id),
    applicant_name TEXT NOT NULL,
    applicant_email TEXT NOT NULL,
    applicant_phone TEXT NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('stripe', 'linepay', 'atm')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'verified', 'canceled', 'refunded')),
    -- 不可變定價快照
    pricing_snapshot JSONB NOT NULL,
    -- ATM 匯款末五碼 (僅在 payment_method = 'atm' 時使用)
    atm_last_five TEXT,
    -- 外部金流交易 ID (Stripe session_id / LINE Pay transactionId)
    external_transaction_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);

-- 4. 訂單事件審計表 (Registration Events)
CREATE TABLE public.registration_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_id UUID NOT NULL REFERENCES public.registrations(id) ON DELETE CASCADE,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    operator TEXT NOT NULL DEFAULT 'system',
    note TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. 啟用 RLS 與安全策略
ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.registration_events ENABLE ROW LEVEL SECURITY;

-- 任何人可讀取未刪除之上架課程
CREATE POLICY "Public courses are viewable by everyone" ON public.courses
    FOR SELECT USING (is_active = true AND deleted_at IS NULL);

-- 使用者僅能檢視與建立自己的訂單
CREATE POLICY "Users can view own registrations" ON public.registrations
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert registrations" ON public.registrations
    FOR INSERT WITH CHECK (true);

-- 狀態更新與事件表僅限 Server 端 (service_role) 執行
CREATE POLICY "Service role manages registration events" ON public.registration_events
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
```

---

## 4. 定價快照結構 (Pricing Snapshot Structure)

在伺服器端計算定價時，寫入 `pricing_snapshot` 的標準 JSON 規格：

```json
{
  "calculated_at": "2026-10-23T00:30:00Z",
  "currency": "TWD",
  "course_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "course_title": "AI 驅動全端建築實戰營",
  "base_price": 12800,
  "discount_type": "early_bird",
  "discount_amount": 2000,
  "coupon_code": null,
  "coupon_discount": 0,
  "final_payable_amount": 10800,
  "tax_rate": 0.05,
  "tax_amount": 540
}
```

---

## 5. Webhook 安全簽名驗證守則

處理第三方金流回調時，伺服器端路由（如 `app/api/webhooks/stripe/route.ts`）必須遵循：

1. **讀取原始字串 (Raw Body)**：不得使用預先解析的 JSON 物件驗證簽名。
2. **簽名驗證先行**：調用金流官方 SDK（如 `stripe.webhooks.constructEvent(body, sig, webhookSecret)`），簽名失敗立即回傳 HTTP 400，中斷執行。
3. **金額雙重對帳 (Amount Reconciliation)**：比對 Webhook 回傳金額與 `registrations.pricing_snapshot.final_payable_amount`，若不一致立即標記異常，嚴禁自動標記 `paid`。
4. **冪等性保證 (Idempotency)**：若該訂單狀態已為 `paid`，直接回傳 HTTP 200，不重複發送開課通知信。
