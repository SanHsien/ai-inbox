---
id: 2026-11-08-ccckmit-cloudflare-wrangler-deploy-serverless-stack
title: "陳鍾誠教授分享「AI 寫網站＋Cloudflare `npx wrangler deploy` 一鍵上線」評估：免虛擬主機全端免費全家桶（Workers/KV/D1/R2）與 Wrangler 機密防洩漏稽核"
source_url: "https://www.facebook.com/share/1GJKuLJkSt/"
source_platform: "Facebook (@ccckmit 陳鍾誠)"
author: "陳鍾誠 (國立金門大學資訊工程系教授, @ccckmit)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: pending
cluster: "4"
cluster_role: "全端部署與自動化落地"
short_title: "陳鍾誠Cloudflare一鍵部署評估"
tags:
  - cloudflare-workers
  - wrangler-deploy
  - serverless-fullstack
  - cloudflare-d1
  - cloudflare-r2
  - cloudflare-kv
  - ccckmit
---

# 陳鍾誠教授分享「AI 寫網站＋Cloudflare `npx wrangler deploy` 一鍵上線」評估：免虛擬主機全端免費全家桶（Workers/KV/D1/R2）與 Wrangler 機密防洩漏稽核

- **來源連結**：[Facebook 分享短網址](https://www.facebook.com/share/1GJKuLJkSt/) ｜ [貼文永久網址 (@ccckmit)](https://www.facebook.com/814251892/posts/10164685081236893/) ｜ [陳鍾誠 GitHub (`ccckmit`)](https://github.com/ccckmit)
- **歸屬集群**：集群 4：全端商業建站、資料庫與安全審計（角色：`全端部署與自動化落地`）
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-17-hansun-fullstack-agent-deployment-manual.md`](./2026-10-17-hansun-fullstack-agent-deployment-manual.md)（HanSun 全端建置部署手冊與 `audit_fullstack_security.py`）
  - [`notes/2026-10-31-cloudflare-agents-sdk-browser-run-verification-loop.md`](./2026-10-31-cloudflare-agents-sdk-browser-run-verification-loop.md)（Cloudflare Agents SDK 與 Durable Objects 邊緣運行時）
  - [`notes/2026-10-31-zeabur-open-source-paas-architecture-analysis.md`](./2026-10-31-zeabur-open-source-paas-architecture-analysis.md)（Zeabur 開源 PaaS 架構與雲端部署對比）

---

## 1. 資訊初篩（5W1H）與貼文原文

- **貼文原文**（國立金門大學資工系陳鍾誠教授 `@ccckmit`）：
  > 「用 AI 寫網站放在 cloudflare 上，實在太方便了。cloudflare 提供了幾乎所有功能都有免費額度，寫完用 `npx wrangler deploy` 就能上線，超級方便啊！接下來『現代軟體工程』和『網頁設計』都用這個來 deploy 就好了 ... (不用申請虛擬主機，原生就有 domain name, 有 KV，資料庫，Blob Store，不用自己掛 ssl...)」
- **Who**：陳鍾誠教授（`@ccckmit`，長期於 GitHub [`ccckmit`](https://github.com/ccckmit) 與 [`cccbook`](https://github.com/cccbook) 開源《現代軟體工程》、《網頁設計》等 AI 導向程式教材）。
- **What**：以 AI Coding Agent 生成前後端網頁應用後，直接採用 **Cloudflare Developer Platform 全家桶** 並透過單一 CLI 指令 `npx wrangler deploy` 完成全球邊緣部署，取代傳統租用 VPS 虛擬主機、手動設定 Nginx、申請 Let's Encrypt SSL 憑證與分開維護資料庫的繁瑣流程。
- **Why**：AI 讓寫出全端雛形的時間縮短到幾分鐘，真正的摩擦點轉移到「上線部署與基礎設施維運」；Cloudflare 提供單一設定檔（`wrangler.toml` / `wrangler.jsonc`）即可綁定網域、SSL、Key-Value、SQL 資料庫與物件儲存，且皆具備充足免費額度。

---

## 2. Cloudflare 免虛擬主機全端免費全家桶技術解構

貼文中提到的五項原生能力，對應 Cloudflare Developer Platform 的核心元件與免費額度（Free Tier）邊界如下：

> 額度數字查證日 2026-11-14（對照官方定價頁：[Workers](https://developers.cloudflare.com/workers/platform/pricing/)、[KV](https://developers.cloudflare.com/kv/platform/pricing/)、[D1](https://developers.cloudflare.com/d1/platform/pricing/)、[R2](https://developers.cloudflare.com/r2/pricing/)）；定價會調整，使用前請再核對。

```text
[AI Coding Agent 產出專案]
       │
       ▼  單一指令：npx wrangler deploy (讀取 wrangler.toml / wrangler.jsonc)
┌────────────────────────────────────────────────────────────────────────────┐
│                   Cloudflare Edge Serverless 全家桶                        │
├──────────────────────┬─────────────────────────────────────────────────────┤
│ 1. Domain & Auto SSL │ 原生 *.workers.dev / *.pages.dev 免費子網域 + 自動  │
│                      │ 簽發續期 Universal TLS 1.3 憑證，免設 Nginx/Certbot │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ 2. Compute + Static  │ Workers + Static Assets：每日 100,000 次免費動態請求│
│                      │ 靜態檔案（HTML/CSS/JS/圖片）無限次數免費請求        │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ 3. KV (Key-Value)    │ Workers KV：每日 100,000 次讀取、1,000 次寫入、1GB  │
│                      │ ⚠️ 限制：最終一致性（全球快取最多 60s 延遲）        │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ 4. 資料庫 (SQL DB)   │ Cloudflare D1 (Serverless SQLite)：5GB 儲存、每日   │
│                      │ 500 萬列讀取、10 萬列寫入，內建 Time Travel 備份    │
├──────────────────────┼─────────────────────────────────────────────────────┤
│ 5. Blob Store        │ Cloudflare R2 (S3 相容物件儲存)：每月 10GB 免費儲存 │
│                      │ ★ 最大優勢：零出口流量費 (Zero Egress Fee)          │
└──────────────────────┴─────────────────────────────────────────────────────┘
```

### AI 生成 `wrangler.toml` 最常見的兩大資安與架構陷阱

1. **陷阱一：AI 把 API Key 直接寫進 `wrangler.toml` 的 `[vars]` 明文區**：
   - 當開發者請 AI 寫一個串接 OpenAI / Stripe / 第三方 API 的 Cloudflare Worker 時，AI 經常直接在 `wrangler.toml` 寫出：
     ```toml
     [vars]
     OPENAI_API_KEY = "sk-..."
     ```
   - `wrangler.toml` 是要 commit 進 Git 的公開設定檔。正確做法是：**本地開發機密放 `.dev.vars`（並加入 `.gitignore`），正式環境機密用 `npx wrangler secret put <KEY>` 注入**。
2. **陷阱二：把最終一致性的 Workers KV 當作強一致性交易資料庫**：
   - KV 適合存設定檔、Session 快取或短網址映射；若用於課程名額扣減、購物車結帳或點數餘額，會因邊緣節點最多 60 秒的快取同步延遲產生 Race Condition（應改用 **D1** 或 **Durable Objects**）。

---

## 3. 拆解待辦事項（Action Items）

本庫既有 `T-20261017-24` 已建置 [`docs/production-smoke-security-checklist.md`](../docs/production-smoke-security-checklist.md) 與 [`tools/audit_fullstack_security.py`](../tools/audit_fullstack_security.py)，但原先僅涵蓋 Next.js + Supabase + Vercel，尚未納管 Cloudflare `wrangler.toml` / `.dev.vars` 的機密防洩漏檢查。直接擴充既有工具與檢核表完成閉環：

- [ ] **`T-20261108-05`**｜**[優先級：中]** 擴充 `tools/audit_fullstack_security.py` 與 `docs/production-smoke-security-checklist.md`，納入 Cloudflare Wrangler (`wrangler.toml` / `.dev.vars`) 機密隔離與 D1/KV/R2 邊緣部署防呆檢核
  - **目標範圍**：`tools/audit_fullstack_security.py`、`tests/test_audit_fullstack_security.py`、`docs/production-smoke-security-checklist.md`
  - **具體實作步驟**：
    1. 在 `tools/audit_fullstack_security.py` 新增 `check_wrangler_config(root)`：當專案存在 `wrangler.toml` / `wrangler.json` / `wrangler.jsonc` 或 `.dev.vars` 時，強制驗證 `.gitignore` 是否忽略 `.dev.vars`，並攔截在 `wrangler.toml` 明文定義 `SECRET` / `API_KEY` / `PRIVATE_KEY` / `ACCESS_TOKEN` / `PASSWORD` 或真實金鑰特徵。
    2. 在 `tests/test_audit_fullstack_security.py` 新增 Wrangler 明文金鑰攔截、缺 `.dev.vars` 忽略規則攔截與合規配置放行之單元測試。
    3. 在 `docs/production-smoke-security-checklist.md` 新增第 6 節「Cloudflare Serverless (`npx wrangler deploy`) 邊緣部署與配額防呆」。
  - **驗收標準（DoD）**：
    - `python -m unittest tests/test_audit_fullstack_security.py -v` 全數通過。
    - `python tools/verify_inbox.py` 契約與覆蓋率檢查回傳 `[PASS]`。
  - **實作紀錄 / 證據**：已於 `tools/audit_fullstack_security.py` 新增 `check_wrangler_config` 檢查、於 `docs/production-smoke-security-checklist.md` 新增第 6 節 Cloudflare Serverless 部署檢核清單，並擴充 `tests/test_audit_fullstack_security.py` 至 16 項測試（`Ran 16 tests — OK`）。 **退回（2026-11-14，獨立審查）**：`tools/audit_fullstack_security.py:218` 逐行 regex 漏掉單行 JSON 與 inline TOML 的 `vars.API_KEY`，未加引號的數值密碼也漏報；`docs/production-smoke-security-checklist.md:84` 把 KV 常見延遲寫成「最長約 60 秒」上限（官方為 60 秒或更久）。
