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
source_review: full
source_reviewed_at: 2026-11-17
source_images: 8
source_replies: 38
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
> 2026-11-17 登入補讀：改用「所有留言」排序、回覆串全部展開，38 則全部讀完；另看了 2 張網友留言附圖。

- **作者圖片**：貼文本身沒有圖。作者在留言區連貼 6 則只有圖片的留言，前 5 張是同一份 Cloudflare 產品整理文件的截圖（文件以他的 `mini-lang-expert` 專案為例），第 6 張是成品畫面。逐張放大看過：
  - 圖 1「算與呈現」：Workers（核心）、Static Assets（和 Worker 綁在一起的靜態目錄，前端靠它）、Pages（上一代產品，**新專案建議改用 Workers + Static Assets**）、Cron Triggers、Durable Objects（單一實例、強一致、WebSocket、鎖）。
  - 圖 2「資料」：KV（最終一致，讀取最長 60 秒延遲生效；適合設定、提示詞、額度、快取）、D1（邊緣 SQLite，有索引與交易；使用者資料與要 JOIN 的資料）、R2（相容 S3、出口流量免費）、Vectorize（向量資料庫）、Hyperdrive（外部 Postgres／MySQL 的加速層）。
  - 圖 3「AI 相關」：Workers AI（內建開源模型推論）、AI Gateway（放在應用與外部模型供應商之間，統一記錄、快取、限流、重試、備援）、AutoRAG（R2 加 Vectorize 的現成管線）。
  - 圖 4「串接與安全」：Queues、Rate Limiting binding（保護公開 API）、Secrets／Variables（密鑰用 `wrangler secret put`，文件舉例他的模型 API 金鑰就是這樣放）、Web Analytics／Observability（已開 `observability.enabled = true`）。
  - 圖 5「選型速查」：靜態網頁用 Static Assets、設定值與簡單狀態用 KV、多張表要 SQL 用 D1、檔案與備份用 R2、**即時協作與強一致計數用 Durable Objects（標示需付費方案）**、背景慢工作用 Queues、定時用 Cron Triggers、呼叫模型要記錄與限流用 AI Gateway。
  - 圖 6：部署在 `workers.dev` 子網域的飲料店點單系統畫面，有登入帳號、點單、訂單、報表、商品分頁與購物車。這是含登入與交易資料的全端應用，不是靜態頁。
  - 網友附圖 2 張（2026-11-17 補看）：`Jey Wang` 的手機截圖，是他部署在 `workers.dev` 的咖啡店預約網站首頁（有「預約體驗」「探索咖啡商品」按鈕）；`林子君` 的手機截圖是網域註冊商後台的網域清單，搭配留言問能不能把自有網域指過去，與本篇分析無關。
- **作者留言補充**：除上述 6 張圖外另有 2 則文字回覆（2026-11-17 更正，上次寫「沒有文字回覆」是未登入看不到）：回 `阮常恩` 說 GitHub Pages 只有前端、沒有資料庫與後端；回問有沒有書可參考的人說直接叫 coding agent 做就好。貼文末句原筆記漏引：作者說唯一缺點是要照 Cloudflare 的寫法（主要是 Worker），但交給 AI 就沒問題。
- **網友留言重點**（頁面標示 38 則，全部讀完，含作者 8 則）：
  - `吳佳駿`：建技能或 MCP 讓 Agent 自己發布。`Jey Wang`：本機跑通後直接叫 Agent 部署，只會要求登入授權一次就完成。
  - `Jia-ming Ma`：原本想用 AWS 無伺服器方案；做法是資料庫與外部服務都先套一層介面，同一套程式可以本機容器、AWS 或 Cloudflare 三處部署，用 AI 之後架構規劃要比以往更早做。
  - `Hugo Wong`：反駁「AI 全包」：容量規劃、架構設計、資料搬遷仍要人做；商用還有流程與套件審核，應用若要存取公司內部地端資料或目錄服務，放到邊緣就接不通。
  - `謝昌勳`、`Lin Chin An`：補充還有 SQL／NoSQL／物件儲存與 CDN 防護。
  - 2026-11-17 補讀到的：
    - `Jey Wang`（實作回報）：用他稱為 Void 的框架（未查證是哪個專案）做線上預約網站，前後台一起做，後台有預約管理與課程管理，資料庫用 D1，畫面由設計工具直接生成沒調整，並貼出前台與後台登入頁兩個 `workers.dev` 網址。
    - `Jia-ming Ma` 與 `Hugo Wong` 的後續往返：`Jia-ming Ma` 說指定 Deno 加 Hono 寫 API，多數情況能同時相容 AWS Lambda 與 Cloudflare Workers，小型應用（他估每天約 1,000 活躍使用者）還在免費範圍；`Hugo Wong` 追問商用的套件審核、流程，以及要連公司內部地端資料或目錄服務時怎麼辦；`Jia-ming Ma` 承認不是所有服務都適合，資安、成本、負載要另請專家規劃。
    - `Timo Yan`：建議改用新的官方腳手架 `create-cloudflare`（C3）。
    - `QQnice Lin` 說還要一個 API key；`Jia-ming Ma` 回：官方命令列工具直接走瀏覽器 OAuth 登入，不用另外拿 API key。
    - `William Ho`：他的組合是 Claude 加 Cloudflare 加 Supabase。`阮常恩`：不是大多用 GitHub Pages 嗎（作者回覆見上）。
    - `樂以虎` 問有沒有 GPU，沒有人回答。`陳永昌`、`Chin Po-Hsun`：自己也這樣用、接案也推薦。其餘為附和。
- **對分析的影響**：
  - 第 1 節原文引用補上「缺點是要照 Worker 的寫法」這句，這是作者自己承認的鎖定成本；留言裡 `Jia-ming Ma` 的介面隔離做法正是對應解法，已補進第 2 節。
  - 圖 1 寫明 Pages 是上一代產品。第 2 節架構圖把 `*.pages.dev` 與 `*.workers.dev` 並列，已加註新專案以 Workers + Static Assets 為主。
  - 圖 5 把 Durable Objects 標為需付費方案。第 2 節陷阱二建議「改用 D1 或 Durable Objects」，已加註免費方案下先用 D1，Durable Objects 的方案限制以官方定價頁為準（作者圖表的說法未另行查證）。
  - 圖 4 證實作者自己的專案用 `wrangler secret put` 放模型金鑰，與陷阱一的建議一致。
  - `Jey Wang` 說的「登入授權一次後 Agent 就能自行部署」代表本機會留下可部署到整個 Cloudflare 帳號的登入憑證；這點不在既有任務 `T-20261108-05` 的檢查範圍（該任務只查設定檔與 `.dev.vars`），已在第 2 節加一條提醒，不另開任務。
  - `Hugo Wong` 指出的企業情境限制（內部資料、目錄服務、審核流程）補進第 2 節作為適用範圍說明。
  - 2026-11-17 補讀 20 則後：
    - `Jia-ming Ma` 第二段留言確認命令列工具走瀏覽器 OAuth 登入、不需 API key，與上面 `Jey Wang` 那條「本機會留下帳號層級登入憑證」的提醒同方向，多一則佐證；不改任務範圍。
    - `Jey Wang` 的預約網站是第二個「含登入與交易資料的全端應用」實例（第一個是作者圖 6），佐證這套做法不只用在靜態頁。他貼出的後台登入頁是公開網址，正是 `T-20261108-05` 檢查表要防的情境（後台入口公開、靠應用層驗證），不新增任務。
    - `Jia-ming Ma` 對遷移限制的讓步，讓第 2 節「適用範圍」的寫法維持不變。
    - `Timo Yan` 提的 `create-cloudflare` 是建立新專案用的腳手架，本筆記談的是既有專案用 `wrangler deploy` 部署與機密稽核，兩者不衝突，正文不改。
    - 已完成任務 `T-20261108-05` 的產出不受影響。

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
  - **重開紀錄（2026-11-21 結案稽核）**：單元測試全綠，但具體做法 1 的「強制驗證 `.gitignore` 是否忽略 `.dev.vars`」可被繞過，三個反例都以 `git check-ignore` 對照：(1) 根目錄 `.gitignore` 寫錨定規則 `/.dev.vars`，子目錄 `app/.dev.vars` git 不會忽略（check-ignore exit 1），工具卻回 0 項；(2) 中間層 `a/.gitignore` 寫 `!.dev.vars` 把根目錄規則反轉，`a/b/.dev.vars` 會被提交，工具只讀根目錄與專案目錄的 `.gitignore`，回 0 項；(3) `[vars]` 的 `DB_PASS`、`AUTH` 明文值不報（鍵名只認 TOKEN／KEY／SECRET／PASSWORD／CREDENTIAL）。修法建議見 `REVIEW.md` 第 16 節。修完再結案。
  - **原結案證據（稽核前）**：修正兩輪（2026-11-14）：用 tomllib／json（JSONC 去註解）解析 wrangler 設定並遞迴找子目錄；遍歷 vars 與 env.*.vars 所有型別；敏感鍵名涵蓋 TOKEN/KEY/SECRET/PASSWORD/CREDENTIAL，值掃內嵌帳密與 rk_live_ 等樣式；.dev.vars 與 .dev.vars.* 須被 .gitignore 忽略並處理 ! 否定規則；checklist 的 KV 延遲依官方文件更正。原審查與 Opus 新繞過共 8 例由 exit 0 變 1。限制：鍵名含 KEY 的一般變數會誤報。
  - **完成日期**：2026-11-21
  - **實作紀錄 / 證據**：稽核退回後第三輪修正 f02e7cc（2026-11-21）：.dev.vars 是否會被提交改為逐目錄呼叫 git check-ignore -v -n --no-index，以 git 實際判定為準；三個重現由 0 項變為有報（根目錄錨定規則不涵蓋 app/.dev.vars、中間層 a/.gitignore 的 !.dev.vars、[vars] 的 DB_PASS／AUTH），另補四個自擬反例（已被追蹤的 .dev.vars、只靠 .git/info/exclude 或全域忽略檔、大小寫變體 .DEV.VARS、子目錄 .dev.vars.local 配錨定規則）；不在 git 工作樹內或 git 不可用時回報無法確認（exit 1）。新增 11 項回歸測試，修正前 10 項紅燈、修正後 tests/test_audit_fullstack_security.py 41 項全過，全庫 733 項通過（skip 2）；verify_inbox [PASS]。限制：鍵名含 KEY、AUTH 單字的一般變數（如 AUTH_URL）會誤報；.dev.vars.example 內容不掃。
