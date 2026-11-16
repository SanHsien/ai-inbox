---
id: 2026-11-08-ccckmit-cloudflare-wrangler-deploy-serverless-stack
title: "陳鍾誠教授分享「AI 寫網站＋Cloudflare `npx wrangler deploy` 一鍵上線」評估：免虛擬主機全端免費全家桶（Workers/KV/D1/R2）與 Wrangler 機密防洩漏稽核"
source_url: "https://www.facebook.com/share/1GJKuLJkSt/"
source_platform: "Facebook (@ccckmit 陳鍾誠)"
author: "陳鍾誠 (國立金門大學資訊工程系教授, @ccckmit)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: done
cluster: "4"
cluster_role: "全端部署與自動化落地"
short_title: "陳鍾誠Cloudflare一鍵部署評估"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "未登入只讀到 18 則留言（共 38 則），頁面註明排序可能濾掉部分回覆；作者留言區 6 張圖已逐張看完"
source_images: 6
source_replies: 18
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
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-17-hansun-fullstack-agent-deployment-manual.md`](./2026-10-17-hansun-fullstack-agent-deployment-manual.md)（HanSun 全端建置部署手冊與 `audit_fullstack_security.py`）
  - [`notes/2026-10-31-cloudflare-agents-sdk-browser-run-verification-loop.md`](./2026-10-31-cloudflare-agents-sdk-browser-run-verification-loop.md)（Cloudflare Agents SDK 與 Durable Objects 邊緣運行時）
  - [`notes/2026-10-31-zeabur-open-source-paas-architecture-analysis.md`](./2026-10-31-zeabur-open-source-paas-architecture-analysis.md)（Zeabur 開源 PaaS 架構與雲端部署對比）

---

## 0. 原始資料盤點

> 2026-11-16 重審：Facebook 未登入可讀貼文全文（2026-11-03 15:42 發布；568 個心情、38 則留言、150 次分享）、作者在留言區貼的 6 張圖與部分留言。

- **作者圖片**：貼文本身沒有圖。作者在留言區連貼 6 則只有圖片的留言，前 5 張是同一份 Cloudflare 產品整理文件的截圖（文件以他的 `mini-lang-expert` 專案為例），第 6 張是成品畫面。逐張放大看過：
  - 圖 1「算與呈現」：Workers（核心）、Static Assets（和 Worker 綁在一起的靜態目錄，前端靠它）、Pages（上一代產品，**新專案建議改用 Workers + Static Assets**）、Cron Triggers、Durable Objects（單一實例、強一致、WebSocket、鎖）。
  - 圖 2「資料」：KV（最終一致，讀取最長 60 秒延遲生效；適合設定、提示詞、額度、快取）、D1（邊緣 SQLite，有索引與交易；使用者資料與要 JOIN 的資料）、R2（相容 S3、出口流量免費）、Vectorize（向量資料庫）、Hyperdrive（外部 Postgres／MySQL 的加速層）。
  - 圖 3「AI 相關」：Workers AI（內建開源模型推論）、AI Gateway（放在應用與外部模型供應商之間，統一記錄、快取、限流、重試、備援）、AutoRAG（R2 加 Vectorize 的現成管線）。
  - 圖 4「串接與安全」：Queues、Rate Limiting binding（保護公開 API）、Secrets／Variables（密鑰用 `wrangler secret put`，文件舉例他的模型 API 金鑰就是這樣放）、Web Analytics／Observability（已開 `observability.enabled = true`）。
  - 圖 5「選型速查」：靜態網頁用 Static Assets、設定值與簡單狀態用 KV、多張表要 SQL 用 D1、檔案與備份用 R2、**即時協作與強一致計數用 Durable Objects（標示需付費方案）**、背景慢工作用 Queues、定時用 Cron Triggers、呼叫模型要記錄與限流用 AI Gateway。
  - 圖 6：部署在 `workers.dev` 子網域的飲料店點單系統畫面，有登入帳號、點單、訂單、報表、商品分頁與購物車。這是含登入與交易資料的全端應用，不是靜態頁。
- **作者留言補充**：除上述 6 張圖外，讀到的範圍內沒有文字回覆。貼文末句原筆記漏引：作者說唯一缺點是要照 Cloudflare 的寫法（主要是 Worker），但交給 AI 就沒問題。
- **網友留言重點**（頁面標示 38 則，未登入讀到 18 則含作者 6 則；頁面註明「最相關」排序可能濾掉部分回覆）：
  - `吳佳駿`：建技能或 MCP 讓 Agent 自己發布。`Jey Wang`：本機跑通後直接叫 Agent 部署，只會要求登入授權一次就完成。
  - `Jia-ming Ma`：原本想用 AWS 無伺服器方案；做法是資料庫與外部服務都先套一層介面，同一套程式可以本機容器、AWS 或 Cloudflare 三處部署，用 AI 之後架構規劃要比以往更早做。
  - `Hugo Wong`：反駁「AI 全包」：容量規劃、架構設計、資料搬遷仍要人做；商用還有流程與套件審核，應用若要存取公司內部地端資料或目錄服務，放到邊緣就接不通。
  - `謝昌勳`、`Lin Chin An`：補充還有 SQL／NoSQL／物件儲存與 CDN 防護。
- **對分析的影響**：
  - 第 1 節原文引用補上「缺點是要照 Worker 的寫法」這句，這是作者自己承認的鎖定成本；留言裡 `Jia-ming Ma` 的介面隔離做法正是對應解法，已補進第 2 節。
  - 圖 1 寫明 Pages 是上一代產品。第 2 節架構圖把 `*.pages.dev` 與 `*.workers.dev` 並列，已加註新專案以 Workers + Static Assets 為主。
  - 圖 5 把 Durable Objects 標為需付費方案。第 2 節陷阱二建議「改用 D1 或 Durable Objects」，已加註免費方案下先用 D1，Durable Objects 的方案限制以官方定價頁為準（作者圖表的說法未另行查證）。
  - 圖 4 證實作者自己的專案用 `wrangler secret put` 放模型金鑰，與陷阱一的建議一致。
  - `Jey Wang` 說的「登入授權一次後 Agent 就能自行部署」代表本機會留下可部署到整個 Cloudflare 帳號的登入憑證；這點不在既有任務 `T-20261108-05` 的檢查範圍（該任務只查設定檔與 `.dev.vars`），已在第 2 節加一條提醒，不另開任務。
  - `Hugo Wong` 指出的企業情境限制（內部資料、目錄服務、審核流程）補進第 2 節作為適用範圍說明。

---

## 1. 資訊初篩（5W1H）與貼文原文

- **貼文原文**（國立金門大學資工系陳鍾誠教授 `@ccckmit`）：
  > 「用 AI 寫網站放在 cloudflare 上，實在太方便了。cloudflare 提供了幾乎所有功能都有免費額度，寫完用 `npx wrangler deploy` 就能上線，超級方便啊！接下來『現代軟體工程』和『網頁設計』都用這個來 deploy 就好了 ... (不用申請虛擬主機，原生就有 domain name, 有 KV，資料庫，Blob Store，不用自己掛 ssl...)」作者接著補一句：唯一缺點是要符合 Cloudflare 的寫法（主要是 Worker），但這交給 AI 就沒問題。
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
   - KV 適合存設定檔、Session 快取或短網址映射；若用於課程名額扣減、購物車結帳或點數餘額，會因邊緣節點最多 60 秒的快取同步延遲產生 Race Condition（應改用 **D1** 或 **Durable Objects**）。作者在留言區的選型表把 Durable Objects 標為需付費方案（未另行查證，以官方定價頁為準）；只用免費額度時先選 D1。

### 留言區補充的四個適用邊界（2026-11-16 重審新增）

1. **平台鎖定**：作者自己說缺點是要照 Worker 的寫法。留言的解法是資料庫與外部服務一律先套介面，讓同一套程式能在本機容器、AWS 與 Cloudflare 之間換；請 AI 生成時要在一開始就要求這層介面。
2. **Agent 自行部署的憑證範圍**：留言提到叫 Agent 部署只需登入授權一次。這表示本機留有能部署到整個帳號的登入憑證，Agent 之後可以不經確認重複部署；教學或實驗用建議開獨立的 Cloudflare 帳號，不和正式網域放在同一個帳號。
3. **不適用的情境**：需要存取公司內部地端資料或目錄服務、需要走套件與資安審核流程的商用系統，不能直接照這個做法搬上邊緣。作者的使用情境是課程與個人專案。
4. **Pages 與 Workers**：作者貼的產品表把 Pages 列為上一代產品，新專案建議用 Workers + Static Assets；上方架構圖的 `*.pages.dev` 只在維護舊專案時才會用到。

---

## 3. 拆解待辦事項（Action Items）

本庫既有 `T-20261017-24` 已建置 [`docs/production-smoke-security-checklist.md`](../docs/production-smoke-security-checklist.md) 與 [`tools/audit_fullstack_security.py`](../tools/audit_fullstack_security.py)，但原先僅涵蓋 Next.js + Supabase + Vercel，尚未納管 Cloudflare `wrangler.toml` / `.dev.vars` 的機密防洩漏檢查。直接擴充既有工具與檢核表完成閉環：

- [x] **`T-20261108-05`**｜**[優先級：中]** 擴充 `tools/audit_fullstack_security.py` 與 `docs/production-smoke-security-checklist.md`，納入 Cloudflare Wrangler (`wrangler.toml` / `.dev.vars`) 機密隔離與 D1/KV/R2 邊緣部署防呆檢核
  - **目標範圍**：`tools/audit_fullstack_security.py`、`tests/test_audit_fullstack_security.py`、`docs/production-smoke-security-checklist.md`
  - **具體實作步驟**：
    1. 在 `tools/audit_fullstack_security.py` 新增 `check_wrangler_config(root)`：當專案存在 `wrangler.toml` / `wrangler.json` / `wrangler.jsonc` 或 `.dev.vars` 時，強制驗證 `.gitignore` 是否忽略 `.dev.vars`，並攔截在 `wrangler.toml` 明文定義 `SECRET` / `API_KEY` / `PRIVATE_KEY` / `ACCESS_TOKEN` / `PASSWORD` 或真實金鑰特徵。
    2. 在 `tests/test_audit_fullstack_security.py` 新增 Wrangler 明文金鑰攔截、缺 `.dev.vars` 忽略規則攔截與合規配置放行之單元測試。
    3. 在 `docs/production-smoke-security-checklist.md` 新增第 6 節「Cloudflare Serverless (`npx wrangler deploy`) 邊緣部署與配額防呆」。
  - **驗收標準（DoD）**：
    - `python -m unittest tests/test_audit_fullstack_security.py -v` 全數通過。
    - `python tools/verify_inbox.py` 契約與覆蓋率檢查回傳 `[PASS]`。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正兩輪（2026-11-14）：用 tomllib／json（JSONC 去註解）解析 wrangler 設定並遞迴找子目錄；遍歷 vars 與 env.*.vars 所有型別；敏感鍵名涵蓋 TOKEN/KEY/SECRET/PASSWORD/CREDENTIAL，值掃內嵌帳密與 rk_live_ 等樣式；.dev.vars 與 .dev.vars.* 須被 .gitignore 忽略並處理 ! 否定規則；checklist 的 KV 延遲依官方文件更正。原審查與 Opus 新繞過共 8 例由 exit 0 變 1。限制：鍵名含 KEY 的一般變數會誤報。
