# SaaS 訂閱與 API 鑑權防繞過架構設計規範

> 對應任務：`T-20261028-13`（筆記 [`2026-10-28-grok-oauth-subscription-proxy-api-bypass.md`](../notes/2026-10-28-grok-oauth-subscription-proxy-api-bypass.md)）。
> 查證日期：2026-11-02。外部事實都附來源（見文末「來源」）；查不到的標「未驗證」。

## 0. 範圍與立場

- **讀者**：要設計「同時賣個人訂閱與開發者 API」的平台工程師；其次是自己用 Coding Agent、想判斷某條接法合不合規的使用者。
- **只談防禦與合規設計**：服務方怎麼讓訂閱額度不被轉成 API 用量、使用者怎麼保管自己的憑證。本文不收錄任何繞過、偽裝客戶端或規避偵測的操作步驟；社群工具只引用它自己 README 寫的風險聲明。
- **本 repo 的立場（維護者政策）**：生產管線不使用非官方代理去消耗訂閱額度。自動化要嘛走官方客戶端本身提供的無人值守模式，要嘛走標準 API 金鑰，要嘛用本機模型（容錯做法見 [`templates/upstream-proxy-fallback-policy.md`](../templates/upstream-proxy-fallback-policy.md)）。
- 配套工具：[`tools/audit_oauth_credentials.py`](../tools/audit_oauth_credentials.py)（使用者自查憑證檔，見第 9 節）。

## 1. 事件背景：已查證的事實與未驗證的說法

筆記起點是一則貼文，說「訂閱制 Grok 的 OAuth 登入可以被轉成本機 OpenAI 相容 API」。逐項核對如下。

| 說法 | 查證結果 |
| :--- | :--- |
| 有社群工具把 Grok CLI 的 OAuth 登入包成本機 API | 屬實。`kimws/grok-oauth`（查證時最新 commit `d1d698f`，2026-08-04）與 `dvcrn/grok-oauth-proxy` 兩個 repo 都存在且未封存。 |
| 該工具預設只聽本機、沒有用戶端鑑權 | 屬實，但這是**它自己 README 的自述**：預設綁 `127.0.0.1:10541`，「The local server has no client authentication」，並警告 auth.json 含 bearer／refresh 憑證、不要分享或轉售，個人訂閱掛成對外服務有帳號與條款風險。 |
| 它是非官方專案 | README 開頭就聲明 unofficial，與 xAI 無隸屬。 |
| 憑證放在 `~/.grok/auth.json` | 來自該 README；xAI 官方 CLI 文件列了 `grok login`、`grok logout`（清除快取憑證），但**沒有寫檔案路徑**，路徑本身未從官方文件驗證。 |
| 後端「只靠 HTTP 標頭判斷客戶端身分」 | **未驗證。** 只有社群 README 提到轉發時會帶上「Grok CLI 工作階段代理預期的標頭」。xAI 沒有公開該端點的驗證邏輯，本文不複述標頭名稱，也不評斷實際怎麼驗。下一節把它當**設計反例**處理：就算真是如此，這種設計為什麼不夠。 |
| 「訂閱額度」與「API 計費」本來就是兩套 | xAI 文件相符：API 用 `api.x.ai` 加 `XAI_API_KEY`；X Subscription 的每週額度池明寫「eligible first-party usage only」，涵蓋 Grok 與 Cursor 的受支援介面。 |

服務方對「拿訂閱憑證去做訂閱以外的事」的明文立場（各家不同，這是設計時要對齊的基準）：

- **Anthropic**（Claude Code 文件「Legal and compliance」）：OAuth 認證專供 Free／Pro／Max／Ultra／Team／Enterprise 方案購買者日常使用 Claude Code 與其他 Anthropic 原生應用；開發產品或服務（包含用 Agent SDK）的人應使用 API 金鑰；不允許第三方以 Free／Pro／Max／Ultra 方案憑證代使用者轉送請求，也不允許蒐集、儲存或居中轉手 Claude.ai 憑證；保留不事先通知就執法的權利。同頁也寫明：使用者用自己的訂閱登入**未修改的** Claude Code 是允許的。
- **OpenAI**（Codex 認證文件）：Codex 提供兩種登入，「Sign in with ChatGPT」走訂閱額度，「Sign in with an API key」走用量計費；兩者適用的管理控制與資料保存政策也不同。
- **xAI**：見上表；另外 Grok CLI 官方提供無人值守模式（第 7 節）。

## 2. 為什麼只靠 HTTP 標頭做客戶端鑑權會破

把「誰在呼叫」拆開看，標頭式鑑權卡在四個結構性問題：

```text
  請求 ──► [ Authorization: Bearer <token> ]   token 有效嗎？      → 驗得出「這個登入存在」
           [ User-Agent / 版本 / 模式 標頭   ]   是官方客戶端嗎？    → 驗不出：標頭由送出方自己填
           [ 來源 IP / 時間 / 併發            ]   行為像人類互動嗎？  → 只能用統計，不是證明
```

1. **標頭是自報的**。伺服器收到的只是一串字串，官方客戶端送得出來，任何照抄格式的程式也送得出來。標頭只能當遙測與灰度開關，不能當鑑權依據。
2. **bearer token 本來就是「持有即可用」**。RFC 6750 對 bearer 的定義是：持有 token 的任何一方都能和其他持有者用得一樣，使用時不需要證明持有任何密鑰（proof-of-possession）。
3. **原生應用是公開用戶端（public client）**。RFC 8252 §8.4：除非用動態註冊配發每個實例的密鑰，原生應用一律是 public client。PKCE（RFC 7636）防的是授權碼被攔截，不是證明「這個客戶端是官方版本」。登入流程再嚴謹，也無法讓伺服器分辨拿到 token 之後是誰在用。
4. **一把憑證同時能打多個計價面**。若互動端點與批次端點接受同一種 token、audience 沒分開，「訂閱」與「API」的計價邊界就只剩端點網址這一道牆。

### 2.1 攻防案例（抽象化；只取已查證部分）

| 案例 | 發生了什麼 | 對應的防線 |
| :--- | :--- | :--- |
| A. 社群轉接代理 | 非官方程式讀取官方 CLI 的憑證檔，在本機開 OpenAI 相容端點，讓其他 Coding Agent 共用訂閱額度（社群 README 自述）。 | 第 4 節 audience 與 client 分流；第 6 節用量形態異常偵測；第 7 節提供正規的無人值守與 API 路徑，降低誘因；使用者側見第 9 節。 |
| B. 訂閱憑證被代為轉送 | Anthropic 文件明文禁止第三方以方案憑證代使用者轉送，並要求產品開發者用 API 金鑰。 | 條款先行，加上 client 註冊與撤銷（第 4 節 R4、R8）。 |
| C. 憑證檔留在磁碟 | Codex 文件說明登入快取預設可存成 `~/.codex/auth.json` 明文檔，或改用作業系統憑證庫（`cli_auth_credentials_store` 可設 `file`／`keyring`／`auto`／`ephemeral`）；Claude Code 文件說明 Linux 與 Windows 存於 `.credentials.json`（Linux 權限 0600，Windows 繼承使用者資料夾 ACL），macOS 預設用 Keychain。 | 憑證外洩是 RFC 9700 的範疇：sender-constrained token、refresh token 輪替（第 4、5 節）；使用者側用 `audit_oauth_credentials.py` 自查。 |

## 3. 防禦架構拓撲

核心想法：**不同計價面用不同的 audience／scope／client_id，伺服器在資源端逐請求驗證，並把用量記到對應的額度池**。

```text
 [官方客戶端]                      [授權伺服器 AS]                         [資源伺服器 RS]
  官方 CLI／App ──授權碼+PKCE──►   client_id = official-cli
                                   發 access token：
                                     aud   = rs-interactive
                                     scope = chat:interactive
                                     cnf   = 裝置金鑰（DPoP／mTLS，可選）
        │                                                                 
        └────── 請求 + token (+DPoP proof) ───────────────────────────►  RS-interactive
                                                                          ├ 驗 aud／scope／exp／cnf
                                                                          └ 扣「訂閱額度池」
 [自建 Agent／第三方工具]
  API 金鑰 或 client_credentials ──►  client_id = api-key／org-app
                                   發 token：aud = rs-api
                                             scope = api:inference
        └────── 請求 + token ───────────────────────────────────────►  RS-api
                                                                          ├ 驗 aud／scope／exp
                                                                          └ 扣「按量計費」
 [合作夥伴整合（選配）]
  授權碼+PKCE，專屬 client_id ──►   client_id = partner-xyz
                                   發 token：aud = rs-partner
                                             scope = partner:agent
        └────── 請求 + token ───────────────────────────────────────►  RS-partner
                                                                          └ 扣「夥伴專屬額度池」

 [風控／計量服務]  ◄── 三個 RS 都回報：client_id、token 家族 id、並行數、用量形態 ──
        │  分級處置：記錄 → 限速 → 步進驗證 → 暫停 token 家族 → 帳號處置（附申訴）
        └► 撤銷端點（RFC 7009）／AS 端失效整個 refresh token 家族
```

這張圖的邊界要說清楚：audience 分流**擋得住「拿互動 token 去打 API 計價面」**，擋不住「在同一個互動端點上，用不是官方的程式送請求」。後者要靠第 5、6 節的組合，再加上第 7 節把正規出口開好。

## 4. OAuth Token Scope／Audience 隔離規則

下列規則給 AS 與 RS 兩端各自實作；每條都附驗證方法，方便放進第 8 節檢驗清單。

| 編號 | 規則 | 依據 | 怎麼驗 |
| :--- | :--- | :--- | :--- |
| R1 | 每個資源伺服器一個 audience。AS 簽發 token 時寫入 `aud`；**RS 每個請求都要檢查這個 token 是不是發給自己的，不是就拒絕。** | RFC 9700 §2.3（access token SHOULD 限定 audience；RS 若 token 不是給它的，MUST 拒絕）；`aud` 宣告格式見 RFC 9068 | 拿 `rs-interactive` 的 token 打 `rs-api`，必須 401／403 |
| R2 | 互動用途與 API／批次用途的 scope 分開命名，不共用。refresh 時**不得擴大** scope。 | RFC 6749 §6（refresh 請求的 scope 不得超出原授權） | 用 refresh token 要求更大的 scope，必須被拒 |
| R3 | 支援 `resource` 參數，讓客戶端宣告要用在哪個 RS；AS 依 `client_id` 的白名單決定它能拿到哪些 audience。 | RFC 8707 | 官方 CLI 的 client_id 請求 `rs-api` 應被拒；反之亦然 |
| R4 | **官方客戶端與第三方各自註冊 client_id**，各有 scope 上限與額度池。自報標頭（User-Agent、版本、模式）只做遙測，不進授權決策。 | RFC 8252 §8.4（原生應用註冊為 public client） | 改掉標頭重送，授權結果不得改變 |
| R5 | access token 短效；public client 的 refresh token **必須**二擇一：sender-constrained，或每次換發就輪替（rotation）並偵測舊 token 重放。refresh token 要綁定使用者同意的 scope 與資源。 | RFC 9700 §2.2.2、§4.14.2 | 重放已被替換的 refresh token，整個授權家族要失效 |
| R6 | 對外洩風險高的 token 採 sender-constrained：DPoP（RFC 9449）或 mTLS（RFC 8705）。 | RFC 9700 §2.2.1、§4.10.1 | 不帶 proof 或帶別把金鑰簽的 proof，RS 必須拒收；proof 不可重放 |
| R7 | RS 把每個請求的 `client_id`、scope、token 家族 id 寫入計量帳，額度扣在對應的池；不得用「token 有效」就預設扣訂閱池。 | 設計要求（無 RFC 條文） | 同一帳號用兩種 client_id 呼叫，兩個池各自遞減 |
| R8 | 提供撤銷端點，且 AS 能依 client_id 或 token 家族一次撤銷。偵測到 refresh token 重放時，撤銷現行有效的那一把。 | RFC 7009；RFC 9700 §4.14.2 | 撤銷後立刻重放，RS 與 AS 都拒絕 |
| R9 | 拒絕要回**明確的錯誤碼與說明**（「此 client 不得使用此端點」），不要靜默降級或亂回 500。合法整合才知道要改走哪條正規路徑。 | 設計要求 | 錯誤回應含可機讀的 error 與文件連結 |
| R10 | 官方文件寫明：什麼用法屬於訂閱、什麼要走 API、無人值守怎麼做。條款與技術限制要一致。 | 設計要求 | 文件與 R1~R4 的實際行為逐項對照 |

## 5. Client Attestation 與設備綁定：能做什麼、做不到什麼

| 手段 | 擋得住 | 擋不住／限制 |
| :--- | :--- | :--- |
| 自報標頭 | 什麼都擋不住（第 2 節） | 只能當遙測 |
| DPoP／mTLS（sender-constrained token） | token 外洩後被**另一台機器**拿去用（RFC 9700 §4.10.1：金鑰若放在硬體或軟體安全模組、或只能經由 TLS 堆疊間接取得，至少能擋住客戶端離線時的盜用） | 持有人**本人**同時握有 token 與金鑰：他可以用任何程式送請求。RFC 9700 同節明寫：攻擊者若同時取得 token 與金鑰（例如客戶端軟體被入侵），保護就失效 |
| 平台等級 attestation（例：Android Play Integrity API） | 檢查請求是否來自正版、由 Google Play 安裝、跑在認證裝置上的 app，能偵測被改過的 app、不可信裝置、模擬器 | 官方文件說它應與其他訊號並用，不是唯一的防濫用機制；預設每日 10,000 次請求額度（跨所有安裝，可申請提高）；屬行動平台。桌面 CLI 是否有等價的通用硬體 attestation，**未驗證**，本文不假設有 |
| Apple 平台 attestation | — | 官方頁面本次抓取為前端動態渲染，沒取得可引用的內容，**未驗證**，不列效果 |

結論：**技術上無法百分之百證明「這個請求來自官方 binary」**。務實的組合是：

1. 用 R1~R4 讓「不同計價面的 token 不能互通」，把可被濫用的面縮到最小；
2. 對高價值端點加 sender-constrained token，擋住外洩後的橫向使用；
3. 用第 6 節的用量形態與併發偵測處理剩下的灰區，並且可解釋、可申訴；
4. 第 7 節把正規出口開好，讓想自動化的合法使用者不需要冒險。

## 6. 異常併發風控模型（服務端）

目標是讓處置**可解釋、成比例、可申訴**，而不是靠一個黑箱分數直接封號。本節只談模型結構，不給出具體門檻值（門檻應依自家流量校準，且不應公開）。

**輸入訊號（以 token 家族／座位為單位）**：

- 同時進行中的串流數（並行度）。
- 用量曲線與互動使用的偏離：互動使用通常有人的作息；長時間平坦的滿載是另一種形態。
- 同一個 refresh token 家族同時出現的網路來源或裝置數。
- refresh 頻率與已作廢 refresh token 的重放次數（R5 的 rotation 本身就產生這個訊號）。
- 該 client_id 允許的端點之外的嘗試次數（R1、R3 被拒的次數）。

**處置階梯**（每一階都要留紀錄與使用者可見的通知）：

```text
 L0 觀察        只記錄，不影響使用
 L1 通知        告知用量與額度池，提示正規的自動化路徑（第 7 節）
 L2 限速        降低並行度或速率，回明確的 429 與 retry 資訊
 L3 步進驗證    要求重新登入或加驗證，新的 token 家族
 L4 暫停家族    撤銷該 refresh token 家族
 L5 帳號處置    僅限明確違反條款，附申訴管道與人工複核
```

**政策檔範例（佔位符由服務方自行填入，非任何廠商的實際值）**：

```yaml
abuse_policy:
  scope: per_token_family          # 另可 per_seat、per_org
  signals:
    concurrent_streams:   { warn: <N1>, throttle: <N2> }
    sustained_utilization: { window: <DURATION>, warn: <PCT> }
    distinct_origins:     { window: <DURATION>, warn: <N3> }
    refresh_replay:       { action: revoke_family }     # R5：重放即撤銷
    cross_surface_denied: { window: <DURATION>, warn: <N4> }   # R1/R3 被拒次數
  ladder: [observe, notify, throttle, step_up, suspend_family, account_review]
  notify_channels: [in_app, email]
  appeal: { url: <APPEAL_URL>, human_review_before: account_review }
```

**誤判控管**：新訊號先以 L0 影子模式跑一段時間，對照正常使用者分佈後再開處置；合法的多裝置使用（手機加桌機）、團隊座位、CI 中的官方無人值守模式，都要有明確的白名單路徑，否則會誤傷最想守規矩的人。

## 7. Coding Agent 場景：健康、透明、可持續的計費與驗證模式

使用者要的是「Coding Agent 能自動跑」，服務方要的是「用量計到對的帳上」。兩邊都能接受的做法是把正規出口開寬，而不是只堵：

| 通道 | 適用 | 已查證的現況 |
| :--- | :--- | :--- |
| A. 官方客戶端互動使用 | 一般開發 | 計入訂閱額度池。xAI：每個付費座位有每週額度池，用量與重置日在帳戶頁可見，超量改為 Additional Usage（需預付）。 |
| B. 官方客戶端的無人值守模式 | 腳本、機器人、整合進 IDE | xAI 文件：`grok -p "<prompt>"` 為 headless 模式，另有 `grok agent stdio` 的 ACP 介面；範例前提是「本機已登入，或設定了 `XAI_API_KEY`」。Anthropic 文件：使用者以自己的訂閱登入**未修改**的 Claude Code 是允許的。OpenAI Codex CLI 支援 ChatGPT 登入。至於各家無人值守模式具體怎麼計額度，**未逐一驗證**，使用前讀各家最新文件。 |
| C. 標準 API 金鑰 | 自建 Agent、第三方工具、生產管線 | Anthropic 文件：產品與服務開發者用 Claude Console 或受支援雲端的 API 金鑰；xAI：`https://api.x.ai/v1` 加 `XAI_API_KEY`（Bearer）；OpenAI：Codex 的 API key 登入走用量計費。 |
| D. 夥伴整合（服務方可選） | 想讓第三方工具正式使用使用者訂閱 | **這是建議設計，不是任何廠商現況**：開專屬 client_id、專屬 audience 與額度池（第 3 節 `rs-partner`），在使用者同意畫面上寫明範圍，並提供撤銷。 |

給服務方的設計要點：

1. **用量可見**：額度池、重置時間、超量選項放在使用者看得到的地方，使用者才不需要自己猜。
2. **自動化有明路**：B、C 兩條路要在文件首頁就找得到；找不到的功能，使用者就會自己想辦法。
3. **條款與技術一致**：條款寫禁止的，R1~R4 就要有對應的技術限制；技術擋不住的，風控與條款要補上並可申訴。

給使用者的原則（本 repo 採用）：生產管線只使用 A~C；實驗性質的接法不寫進正式流程；遇到上游拒絕服務，容錯只在合規端點之間切換（範本見 [`templates/upstream-proxy-fallback-policy.md`](../templates/upstream-proxy-fallback-policy.md)）。

## 8. 檢驗清單

### 8.1 服務方（AS／RS 設計審查）

- [ ] 每個 RS 在每個請求都驗 `aud`，驗證失敗回 401／403（R1）。驗：用其他 RS 的 token 打它。
- [ ] 互動 scope 與 API scope 命名分開，refresh 無法擴大 scope（R2）。驗：refresh 請求更大的 scope。
- [ ] 支援 `resource` 參數，且依 client_id 白名單核發 audience（R3）。驗：官方 CLI 的 client_id 請求 API audience 被拒。
- [ ] 授權決策完全不看 User-Agent、版本、模式等自報標頭（R4）。驗：換標頭重送，結果不變。
- [ ] access token 有效期為分鐘級（數值由服務自訂並寫入文件）；public client 的 refresh token 採輪替或 sender-constrained（R5）。驗：重放舊 refresh token，家族失效。
- [ ] 高價值端點的 token 為 sender-constrained，proof 不可重放（R6）。驗：DPoP proof 重送被拒。
- [ ] 計量帳記錄 client_id、scope、token 家族，並扣到對應額度池（R7）。驗：兩種 client_id 的用量分開。
- [ ] 撤銷端點可依 client_id 或家族撤銷，生效時間已記載（R8）。
- [ ] 拒絕回應有機器可讀的錯誤碼與文件連結，不靜默降級（R9）。
- [ ] 風控處置階梯有紀錄、有使用者通知、有申訴管道；新規則先以影子模式跑過（第 6 節）。
- [ ] 文件首頁列出無人值守模式與 API 金鑰的正規做法；條款中的禁止事項都能對應到 R1~R4 的技術限制或風控規則（R10、第 7 節）。
- [ ] 本文第 5 節未驗證的平台 attestation，在採用前先到該平台一手文件確認再寫進設計。

### 8.2 使用者側（自查）

- [ ] 跑 `python tools/audit_oauth_credentials.py`，結束碼為 0（第 9 節）。
- [ ] 憑證檔不在任何 git 工作樹內，或已被 `.gitignore` 忽略且未被追蹤。
- [ ] 工具支援作業系統憑證庫時改用憑證庫（例：Codex 的 `cli_auth_credentials_store = "keyring"`）。
- [ ] 沒有任何本機代理或轉接服務聽在非 loopback 位址。
- [ ] 憑證疑似外洩時：先在帳戶頁登出所有裝置／撤銷，再重新登入；不要只刪檔案。

## 9. 使用者自查工具

`tools/audit_oauth_credentials.py` 掃描 `~/.grok/`、`~/.codex/`（或 `CODEX_HOME`）、`~/.claude/`（或 `CLAUDE_CONFIG_DIR`）的第一層檔案與 `oauth-proxy/` 子資料夾，只看 metadata 與欄位名稱，**不會輸出任何憑證值**：

```bash
python tools/audit_oauth_credentials.py                     # 掃預設目錄
python tools/audit_oauth_credentials.py --repo ./my-project # 另外檢查某個 repo 有沒有追蹤憑證檔
python tools/audit_oauth_credentials.py --json --strict     # 給 CI 或排程用：WARN 也算失敗
```

結束碼：`0` 通過；`1` 有 ERROR（或 `--strict` 且有 WARN）；`2` 參數錯誤。各檢查項目與嚴重度見該檔案開頭說明。ERROR 代表要馬上處理（權限過寬、已被 git 追蹤、代理聽在外部網卡）；`plaintext-token` 只是 WARN，因為官方工具本身就可能把憑證存成明文檔，那是提醒你「能用憑證庫就用」，不是故障。

## 10. 已知限制與未驗證項

- 社群工具的行為只引用其 README 自述；本文沒有執行它，也沒有檢視其程式碼。
- 第 1 節「後端只靠標頭識別客戶端」未獲證實；第 2 節的論點不依賴它成立。
- xAI 的 `~/.grok/auth.json` 路徑、各家無人值守模式的額度計算、Apple 平台 attestation：未從一手文件驗證。
- 第 6 節沒有數字門檻，這是刻意的；要落地需用自家流量校準。
- 第 7 節 D 通道是設計建議，不代表任何廠商已提供。
- 風控誤判無法完全避免；本文的處置階梯與影子模式是降低誤判的做法，不是保證。

## 來源（查證日期 2026-11-02）

- RFC 6749 §6（refresh 的 scope 限制）：<https://www.rfc-editor.org/rfc/rfc6749>
- RFC 6750（bearer token 的定義）：<https://www.rfc-editor.org/rfc/rfc6750>
- RFC 7009 OAuth 2.0 Token Revocation：<https://www.rfc-editor.org/rfc/rfc7009>
- RFC 7636 PKCE：<https://www.rfc-editor.org/rfc/rfc7636>
- RFC 8252 OAuth 2.0 for Native Apps（§8.4）：<https://www.rfc-editor.org/rfc/rfc8252>
- RFC 8705 OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens：<https://www.rfc-editor.org/rfc/rfc8705>
- RFC 8707 Resource Indicators for OAuth 2.0：<https://www.rfc-editor.org/rfc/rfc8707>
- RFC 9068 JWT Profile for OAuth 2.0 Access Tokens：<https://www.rfc-editor.org/rfc/rfc9068>
- RFC 9449 OAuth 2.0 DPoP：<https://www.rfc-editor.org/rfc/rfc9449>
- RFC 9700 Best Current Practice for OAuth 2.0 Security（§2.2.1、§2.2.2、§2.3、§4.10.1、§4.14.2）：<https://www.rfc-editor.org/rfc/rfc9700>
- Anthropic，Claude Code「Legal and compliance」（Authentication and credential use）：<https://code.claude.com/docs/en/legal-and-compliance>
- Anthropic，Claude Code「Authentication」（Credential management）：<https://code.claude.com/docs/en/authentication>
- OpenAI，Codex「Authentication」：<https://developers.openai.com/codex/auth>
- xAI，API 概覽：<https://docs.x.ai/docs/overview>；The X Subscription 概覽：<https://docs.x.ai/x-subscription/overview.md>；用量限制：<https://docs.x.ai/x-subscription/usage-limits.md>；CLI 參考：<https://docs.x.ai/build/cli/reference.md>；Headless 與 ACP：<https://docs.x.ai/build/cli/headless-scripting.md>
- Google，Play Integrity API 概覽：<https://developer.android.com/google/play/integrity/overview>
- 社群專案 `kimws/grok-oauth` README（commit `d1d698fd3951f9ce6301af5c390284537578599b`）：<https://github.com/kimws/grok-oauth>；`dvcrn/grok-oauth-proxy`（僅確認 repo 存在）：<https://github.com/dvcrn/grok-oauth-proxy>
