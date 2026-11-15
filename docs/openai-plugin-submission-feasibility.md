# OpenAI Plugins（原 Apps SDK）上架可行性檢核表

> 本文件收錄於 `docs/openai-plugin-submission-feasibility.md`，為任務 `T-20261115-10` 的交付物，對應筆記 [`notes/2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh.md`](../notes/2026-11-15-chatgpt-apps-mcp-proactive-discovery-and-dsh.md)。
>
> - **查證日期**：2026-11-15（以下每一列都是這一天實際取回官方頁面後核對的結果）
> - **查證方式**：以 Python `urllib` 匿名取回 `developers.openai.com` 與 `developers.cloudflare.com` 的公開頁面（OpenAI 頁面取 `.md` 版）。沒有登入任何帳號、沒有進入 `platform.openai.com` 提交入口、沒有部署、沒有建立 repo。
> - **結論先講**：**暫不開發**。理由與重新提案的條件見第 5 節。

---

## 1. 現行術語：Apps SDK 的網址已全部轉到 Plugins

2026-11-15 實際請求下列舊網址，全部被轉址到 Plugins 文件：

| 舊網址（Apps SDK） | 轉址後 |
| --- | --- |
| `https://developers.openai.com/apps-sdk` | <https://developers.openai.com/plugins> |
| `https://developers.openai.com/apps-sdk/build/auth` | <https://developers.openai.com/plugins/build/auth> |
| `https://developers.openai.com/apps-sdk/deploy/submission` | <https://developers.openai.com/plugins/deploy/submission> |
| `https://developers.openai.com/apps-sdk/app-developer-guidelines` | <https://developers.openai.com/plugins/plugin-guidelines> |

官方文件索引把這一組稱為「ChatGPT plugins and Apps SDK」（<https://developers.openai.com/llms.txt>）。現行操作契約是「plugin」：一個 ZIP 套件，內容可以是 MCP 連線、skills，或兩者都有；上架後出現在 ChatGPT 與 Codex 共用的目錄。動手前要以當天的官方文件為準，不要沿用「Apps SDK」時期的說法。

---

## 2. 上架檢核表

「必要性」欄的意思：**必要**＝官方寫明送審前一定要有；**可選**＝官方寫明可以不做；**條件必要**＝符合條件才必要；**未查證**＝本次沒有取得一手依據。

「決策」欄是針對第 4 節的候選（匿名、唯讀的公開 API 檢索工具）而寫。

| # | 項目 | 官方要求（摘要） | 必要性 | 官方 URL | 決策 |
| --- | --- | --- | --- | --- | --- |
| 1 | 套件形式 | 以 ZIP 上傳；有 MCP 伺服器就要放進第一次上傳的 ZIP，之後不能替純 skills 的 plugin 補上 MCP。含 app 參照（`apps`／`.app.json`）或 lifecycle hooks 的 ZIP 不能送審 | 必要 | <https://developers.openai.com/plugins/deploy/submission> | 做得到，但要先定好是否含 MCP，事後不能改 |
| 2 | 開發者身分驗證 | 所有送審都必須來自已驗證的個人或組織；在 OpenAI Platform 的組織設定完成個人或企業驗證，目錄顯示該身分名稱；未驗證會被退件 | 必要 | <https://developers.openai.com/plugins/deploy/app-review>、<https://developers.openai.com/plugins/plugin-guidelines> | **卡關**：需要維護者本人登入並做身分驗證，本任務不做 |
| 3 | 提交權限 | 組織擁有者可提交；其他成員需要 Apps Management Write（`api.apps.write`） | 必要 | <https://developers.openai.com/plugins/deploy/submission> | 個人帳號為擁有者時不成問題；未實測 |
| 4 | 遠端 MCP 端點 | 公開可連的穩定 HTTPS 端點，支援 MCP streamable HTTP；不可用本機、測試端點或臨時通道；一個 plugin 只能連一個 MCP 伺服器；送審後要改網址得找客服 | 條件必要（plugin 含遠端 MCP 時） | <https://developers.openai.com/plugins/build/mcp-server>、<https://developers.openai.com/plugins/deploy/app-review> | 需要長期維運一個公開端點，見第 3 節成本 |
| 5 | 網域驗證 | 在 MCP 主機名或可用的上層網域放 `/.well-known/openai-apps-challenge`，內容是入口給的純文字 token | 條件必要（含遠端 MCP 時） | <https://developers.openai.com/plugins/deploy/submission#domain-verification> | 技術上簡單，但代表要有自己能控制的網域或主機名 |
| 6 | 驗證方式 | 入口支援三種：無驗證、OAuth、兩者混合。官方寫明許多 MCP 伺服器可用唯讀匿名模式，涉及使用者專屬資料或寫入動作才應驗證使用者；要驗證時須實作符合 MCP 授權規格的 OAuth 2.1。入口沒有 API key／bearer token 的連線流程，也不可把受保護的伺服器宣告成無驗證 | 無驗證：可選用；OAuth：條件必要 | <https://developers.openai.com/plugins/build/auth>、<https://developers.openai.com/plugins/deploy/submission> | 候選是匿名唯讀，走無驗證；「全面強制 OAuth」的說法不成立 |
| 7 | 自訂 UI（Widget） | 官方寫明自訂 UI 是可選的，而且工具沒有元件也要能完成工作；若回傳 UI 就要定義 CSP，用到 iframe 要在送審時說明理由 | 可選 | <https://developers.openai.com/plugins/build/chatgpt-ui>、<https://developers.openai.com/plugins/plugin-guidelines> | 不做 UI |
| 8 | MCP tools／resources／prompts | 指引只對 tools 訂了要求（名稱清楚、描述符合行為、標註正確、輸入最小化）。resources 與 prompts 是否必要，本次取回的頁面沒有寫成送審必要項 | tools：條件必要；resources／prompts：未查證 | <https://developers.openai.com/plugins/plugin-guidelines> | 只做 tools |
| 9 | 上架頁必填欄位 | `displayName`（30 字元內）、`shortDescription`（30 字元內）、`longDescription`、`developerName`、`category`、主要圖示。含 MCP 且要公開審查時，另外四個 HTTPS 網址全部必填：產品網站、客服頁、隱私權政策、服務條款 | 必要 | <https://developers.openai.com/plugins/deploy/submission> | **卡關**：目前沒有這四個對外頁面，要先寫並長期維護 |
| 10 | 隱私權政策內容 | 必須公開，至少說明蒐集的個資類別、用途、接收方類別、保存期限與使用者可用的控制；不得蒐集卡號、健康資訊、政府證號、憑證類資料；回應只回與請求直接相關的資料，不得重建完整對話 | 必要 | <https://developers.openai.com/plugins/plugin-guidelines> | 候選不蒐集個資，但仍要有一份公開政策 |
| 11 | 審查材料 | 首次 MCP 審查需要 5 個正向、3 個負向測試案例，加一支審查者看得到的示範影片網址與版本說明；需要登入的話要給不必二階段驗證的示範帳號 | 條件必要（含 MCP 時）；純 skills 不需要 | <https://developers.openai.com/plugins/deploy/submission> | 做得到，但影片與案例是實打實的工時 |
| 12 | 品質門檻 | 要提供產品內建能力沒有的功能；不收試用版或示範性質的 plugin；不得是靜態畫面或濫發內容；要在桌面與行動版 ChatGPT 都能穩定運作 | 必要 | <https://developers.openai.com/plugins/plugin-guidelines> | **卡關**：見第 4 節，候選與內建搜尋重疊 |
| 13 | 第三方內容 | 不得未經授權爬取外部網站或串接第三方 API；主要功能是「非官方連接器」或純轉送層的 plugin 不會核准 | 必要 | <https://developers.openai.com/plugins/plugin-guidelines> | **風險**：候選轉述他人維護的 API 清單，有被認定為轉送層的可能 |
| 14 | 命名與描述 | 名稱不可過度通用、不可在產品名後加「MCP」「Plugin」；描述不可比較或貶低其他產品、不可寫價格或促銷；不可用描述或標註操縱模型優先選自己 | 必要 | <https://developers.openai.com/plugins/plugin-guidelines> | 堆關鍵字搶曝光的做法直接違規 |
| 15 | 商務與對外導流 | 目前只允許實體商品交易；不可販售數位產品或服務（訂閱、數位內容、點數），也不可間接用免費增值方式推升級。可以說明某功能不在使用者目前方案內、可以連到介紹方案的資訊頁；不可直接連到結帳或開始訂閱的頁面。不得投放廣告，也不得以廣告為主要目的 | 必要 | <https://developers.openai.com/plugins/plugin-guidelines> | **卡關**：「用 plugin 承接付費訂閱」的商業假設與現行規範衝突 |
| 16 | 曝光方式 | 上架後使用者可透過直接連結或以名稱搜尋找到。官方寫明只有少數 plugin 會獲得加強曝光（目錄位置或主動推薦），而且開發者不能申請 | 不適用（平台行為，非開發者可控） | <https://developers.openai.com/plugins/deploy/app-review> | 「上架就有對話內主動推薦」不成立，不能拿來估流量 |
| 17 | 審查時程 | 官方只說時程不一定，不受理加速請求 | 未提供數字 | <https://developers.openai.com/plugins/deploy/app-review> | 無法排程 |
| 18 | 上架後維護 | OpenAI 每天掃描已上架的 MCP 伺服器，通過自動檢查的工具變更才生效；不活躍、不穩定或不合規的 plugin 可能被移除，OpenAI 也可隨時不經通知移除 | 必要（持續義務） | <https://developers.openai.com/plugins/deploy/submission>、<https://developers.openai.com/plugins/deploy/app-review> | 上架不是一次性工作，要算進長期維運 |
| 19 | 只給自己用的替代路徑 | 官方寫明：只打算私用或限工作區使用，就不要送審，改用自訂 MCP 伺服器連線 | 可選 | <https://developers.openai.com/plugins/deploy/app-review> | 自用需求走這條，不必上架 |
| 20 | 每週活躍用戶「12 億」 | 本次取回的開發者文件沒有任何用戶規模數字 | 未查證 | 無一手來源 | 不採用，不拿來估推薦流量 |
| 21 | 審查費或上架費 | 本次取回的頁面沒有提到費用，也沒有寫免費 | 未查證 | 無一手來源 | 提案前要登入後確認，本任務不登入 |
| 22 | 可上架的國家／地區 | 套件可用 `publication.countries` 指定國家；個人或企業驗證是否對台灣開放，本次沒有查到 | 未查證 | <https://developers.openai.com/plugins/deploy/submission> | 提案前要由維護者本人在設定頁確認 |

沒有逐段核對的官方頁面：<https://developers.openai.com/plugins/guides/security-privacy>、<https://developers.openai.com/plugins/deploy/desktop-only>、<https://developers.openai.com/plugins/concepts/ui-guidelines>。這三頁的內容在本表中一律視為未查證。

---

## 3. 託管成本：Cloudflare Workers

以下數字取自 Cloudflare 官方頁面（限制頁標示最後更新 2026-11-13），查證日期 2026-11-15。

| 項目 | Workers Free | Workers Paid | 官方 URL |
| --- | --- | --- | --- |
| 請求數 | 每天 100,000 次，UTC 午夜重置 | 每月含 1,000 萬次，超過每百萬次 0.30 美元 | <https://developers.cloudflare.com/workers/platform/limits/>、<https://developers.cloudflare.com/workers/platform/pricing/> |
| CPU 時間 | 每次請求 10 毫秒 | 每月含 3,000 萬 CPU 毫秒，超過每百萬毫秒 0.02 美元；單次上限 5 分鐘（預設 30 秒） | 同上 |
| 子請求 | 每次請求 50 個 | 每次請求 10,000 個 | <https://developers.cloudflare.com/workers/platform/limits/> |
| 記憶體 | 128 MB | 128 MB | 同上 |
| 最低月費 | 0 | 每個帳號 5 美元 | <https://developers.cloudflare.com/workers/platform/pricing/> |
| Workers KV（若拿來放索引） | 每天讀 100,000 次、寫 1,000 次，儲存 1 GB | 每月讀 1,000 萬次，超過每百萬次 0.50 美元 | 同上 |

**超額時會發生什麼**

```text
Free 方案
  每日請求超過 100,000 ──▶ Cloudflare 回 Error 1027
                           ├─ 路由設 fail open ：跳過 Worker（MCP 端點等於不存在）
                           └─ 路由設 fail closed：回 1027 錯誤頁
  單次 CPU 超過 10 毫秒 ──▶ 回 Error 1102（Worker exceeded resource limits）
  KV 當日額度用完        ──▶ 該類操作直接失敗

Paid 方案
  超過內含用量 ──▶ 照單價計費，沒有自動上限
                  └─ 要自己設定 Workers spending limit，達到門檻後拒絕新的呼叫
```

Free 方案超額不會產生帳單，但服務會中斷。第 2 節第 18 列寫明不穩定的 plugin 可能被移除，所以「免費額度用完就停」本身就是下架風險。

**用量假設與估算**（假設值，沒有實測流量）

| 情境 | 假設 | 結果 |
| --- | --- | --- |
| 低用量 | 每天 1,000 次工具呼叫，加上 OpenAI 每日掃描；每次 CPU 低於 10 毫秒 | 落在 Free 額度內，月費 0 美元 |
| 中用量 | 每天 150,000 次工具呼叫 | 超過 Free 每日上限，要升級 Paid；每月約 450 萬次，仍在內含 1,000 萬次以內，月費 5 美元 |
| 高用量 | 每月 1,500 萬次、平均 7 毫秒 CPU（Cloudflare 官方計價頁的範例 1） | 月費 8 美元（訂閱 5＋請求 1.50＋CPU 1.50） |

一次工具呼叫實際會產生幾個 HTTP 請求（初始化、列工具、呼叫）沒有實測，上表的「次」是 HTTP 請求數，換算成使用者操作次數要再打折。

**未知或另計的費用**

- 網域：網域驗證與四個必填網址需要自己控制的主機名。用 `workers.dev` 子網域是否符合「同一發布者」的要求，未查證。
- 隱私權政策、服務條款、客服頁的撰寫與維護工時。
- 示範影片的錄製與存放。
- 後端資料來源若改用付費 API 或資料庫（D1、R2、Durable Objects 各有自己的計價），另計。
- 若工具內部呼叫語言模型，模型費用另計。本候選刻意不用。
- OpenAI 端的審查或上架費用：未查證（第 2 節第 21 列）。

**不承諾零成本**：只有在流量低、不用付費後端、不買網域的前提下，現金支出才可能是 0；工時成本不是 0，流量一旦成長就會開始計費或中斷。

---

## 4. 候選比較（只比一個）

依任務範圍，只評估一個不用中國服務、沒有付費模型依賴的既有需求。

**候選：免金鑰公開 API 檢索工具**

- 既有基礎：[`tools/public_apis_indexer.py`](../tools/public_apis_indexer.py) 與 [`docs/free-public-apis.md`](./free-public-apis.md)（462 個免金鑰且支援 CORS 的端點、42 個分類），資料來自 `SanHsien/public-apis`。任務 `T-20261020-02` 已經做過「Public APIs 動態檢索 Skill／MCP 伺服器規格」，見 [`notes/2026-10-20-public-apis-free-open-resources.md`](../notes/2026-10-20-public-apis-free-open-resources.md)。
- 符合的條件：純靜態資料、唯讀、匿名，不需要 OAuth、不需要模型、不用中國服務；CPU 用量低，適合 Workers Free。

| 檢核點 | 結果 | 依據 |
| --- | --- | --- |
| 有沒有明確的對外需求 | **沒有**。既有需求是「給維護者自己的 Agent 查」，已由本機工具與文件滿足；repo 內沒有任何外部使用者要求這項功能的紀錄 | `T-20261020-01`、`T-20261020-02` 的範圍都是本機與自用 |
| 是否提供內建能力沒有的功能 | 不明顯。ChatGPT 內建網頁搜尋就能找公開 API 清單；差異只剩「已篩過免金鑰與 CORS」 | 第 2 節第 12 列 |
| 第三方內容風險 | 清單內容來自上游社群專案，plugin 只是轉述；有被認定為轉送層的可能 | 第 2 節第 13 列 |
| 能不能承接付費或接案引流 | 不能賣訂閱或數位服務，不能直接連結帳頁，不能當廣告載具；只能連到資訊頁 | 第 2 節第 15 列 |
| 曝光 | 上架後預設只有直接連結與名稱搜尋，主動推薦不能申請 | 第 2 節第 16 列 |
| 送審前還缺什麼 | 身分驗證、自有網域、四個對外頁面、5＋3 測試案例、示範影片、長期維運的公開端點 | 第 2 節第 2、5、9、11、18 列 |
| 自用的替代做法 | 已經有：本機工具與文件；要在 ChatGPT 裡用，官方建議走自訂 MCP 連線，不必上架 | 第 2 節第 19 列 |

---

## 5. 結論：暫不開發

```text
候選需求 ──▶ 有明確對外需求嗎？ ── 沒有 ──▶ 暫不開發（本次結論）
                  │
                  有
                  ▼
            能過品質門檻（#12、#13）嗎？ ── 不能 ──▶ 不提案
                  │
                  能
                  ▼
            維護者願意做身分驗證、維護四個對外頁面與公開端點嗎？ ── 否 ──▶ 不提案
                  │
                  是
                  ▼
            重新提案（附用量假設與成本上限）
```

理由：

1. 找不到明確的對外需求。唯一符合「不用中國服務、無付費模型依賴」的既有候選是自用工具，需求已經在本機滿足。
2. 原貼文的三個賣點在一手文件面前都站不住：主動推薦不能申請且只有少數 plugin 會有；不能賣訂閱或數位服務；免洗工具過不了「內建沒有的功能」「不收示範性質」這兩條。
3. 送審的固定成本不低（身分驗證、網域、四個對外頁面、測試案例、影片、每日掃描下的長期維運），而可預期的回報是零。

**重新提案的條件**（要同時成立）

- 出現一個具體的對外需求：有可指名的使用者或客戶，而且需要的是外部資料或垂直領域規則，不是模型內建就能做的事。
- 該需求的變現方式不依賴在 plugin 內賣數位產品或導向結帳頁。
- 維護者本人同意完成身分驗證，並確認台灣可以驗證與上架（第 2 節第 22 列）、確認沒有未預期的費用（第 21 列）。
- 提案附上用量假設、Workers 方案選擇、spending limit 設定值與每月成本上限。

在這些條件成立之前，自用的 MCP 需求一律走自訂 MCP 連線，不進上架流程。

---

## 6. 本任務沒有做的事

- 沒有登入 OpenAI Platform 或 Cloudflare，沒有看到提交入口的實際畫面；第 2 節的入口行為全部來自官方文件的描述。
- 沒有部署任何 Worker 或 MCP 伺服器，第 3 節的用量是假設值。
- 沒有提交上架、沒有建立 repo。
- 沒有查證 OpenAI 的用戶規模、審查費用、可驗證的國家清單與實際審查天數。
