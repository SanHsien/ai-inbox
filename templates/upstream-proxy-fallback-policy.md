# Coding Agent 上游端點容錯切換策略範本

> 對應任務：`T-20261028-15`；規範依據：[`docs/saas-subscription-and-api-defense-spec.md`](../docs/saas-subscription-and-api-defense-spec.md) 第 7 節。
> 查證日期：2026-11-02。本檔是**填空範本**：複製到你的專案，把 `<尖括號>` 換成自己的值，刪掉用不到的端點。

## 0. 這份範本管什麼、不管什麼

**管**：Coding Agent 的模型路由層，在「官方 API」與「本機模型」這兩類合規端點之間，遇到錯誤時怎麼分類、要不要重試、能不能換下一個端點、什麼情況下必須停下來叫人。

**不管、也不接受**：把訂閱登入包成 API 的非官方代理、或任何用訂閱憑證直接打內部端點的做法。這類端點**不能出現在 `endpoints:` 清單裡**。理由有三：

1. 各家條款對「轉送訂閱憑證」的立場不一，Anthropic 文件明文不允許（見第 7 節）；
2. 這類端點隨時可能被廠商關閉或限制，不適合當生產路徑的一環；
3. 容錯機制拿來「接住這類端點的失敗」，等於把它變成預設依賴。

要自動化就走：官方 API 金鑰、官方客戶端自己的無人值守模式、或本機模型。

## 1. 六條原則（先讀這個，再填設定）

| # | 原則 | 為什麼 |
| :--- | :--- | :--- |
| P1 | **端點白名單**：`kind` 只能是 `official_api` 或 `local_model`。 | 避免容錯清單悄悄塞進不合規端點 |
| P2 | **帳務錯誤不重試、不自動換更貴的端點**：402、額度用盡、支出上限，一律 `BUDGET_STOP`，通知人，由人決定。 | 重試不會恢復；自動換端點等於讓費用失控 |
| P3 | **403 不換端點繞過**：地區、政策、權限類拒絕是 `POLICY_STOP`，停下來。 | 拿別家端點去避開拒絕，是在規避限制，不是容錯 |
| P4 | **401 隔離該端點並通知**：金鑰錯誤或失效，該端點進 `AUTH_DISABLED`，需人工重置；請求可交給白名單內的下一個端點。 | 不讓壞金鑰被反覆重試，也不默默吞掉告警 |
| P5 | **換端點等於資料換地方**：每個端點宣告 `data_classes`，請求的資料等級不在其中就不能切過去。 | 本機模型可處理內部資料，外部 API 不一定 |
| P6 | **每次切換都留紀錄**（第 5 節欄位），不含提示詞內容。 | 事後才查得出為什麼費用或品質變了 |

## 2. 錯誤分類

分類來源：各供應商 API 文件的錯誤碼說明。**分類是範本的設計選擇，不是供應商規定**；你可以調，但要保留 P2、P3 的精神。

| 類別 | 動作 | 典型情況（查證自官方文件） |
| :--- | :--- | :--- |
| `TRANSIENT` | 同一端點指數退避重試（有 `Retry-After` 就照它）；超過次數後換下一個端點 | 逾時、網路錯誤；500、504、529 overloaded（Anthropic）；503 model overloaded（OpenAI，文件要求照 Retry-After）；429 速率限制且有 `Retry-After`；xAI 超過 RPS／TPM 回 429 |
| `BUDGET_STOP` | 不重試、不換端點；通知人 | 402 billing（Anthropic）；OpenAI 429 `credit_balance_exhausted`、`insufficient_quota`（文件寫明：重試帳務或配額錯誤不會恢復存取）；Anthropic 達到組織用量層級（tier）上限時回 429，`error.details.error_code` 為 `enforced_spend_limit_reached`、**沒有** `retry-after`，重試（含 SDK 自動重試）到恢復前都會失敗；Anthropic 達到**你自己設定**的支出上限時回 **400**（`invalid_request_error`），訊息開頭固定是 `You have reached your specified API usage limits`，工作區上限則是 `You have reached your specified workspace API usage limits`（來源：Anthropic Rate limits 文件，見文末） |
| `AUTH_DISABLE` | 端點進 `AUTH_DISABLED`，通知人；本次請求可交給下一個端點 | 401（金鑰錯誤、失效、組織不符） |
| `POLICY_STOP` | 停止；通知人 | 403（權限不足；OpenAI 另有「地區不支援」的 403） |
| `REQUEST_STOP` | 不重試、不換端點；錯誤回給呼叫端 | 400、404、413、422 等請求本身有問題的錯誤（400 的訊息若符合 `BUDGET_MESSAGE_PREFIXES`，則改判 `BUDGET_STOP`；只比對訊息開頭） |

兩個容易踩的坑：

- **429 不等於可重試**。同樣是 429，可能是速率限制（等一下就好），也可能是額度用完（等多久都沒用）。判斷順序：先看錯誤碼是否為帳務類 → 再看有沒有 `Retry-After` → 都沒有時，連續幾次（預設 3）才升級成 `BUDGET_STOP`。
- **串流中途失敗**不能直接當 `TRANSIENT` 重送整個請求，除非你的任務是冪等的（沒有已執行的工具呼叫副作用）。範本預設：已有工具呼叫副作用的請求，失敗後交回呼叫端，不自動重送。

### 2.1 參考實作（分類函式）

這段是第 2 節表格的最小實作。下面附上斷言（同一份程式碼區塊接在函式後面，複製整段到檔案執行，沒有輸出就代表全部通過）。語言不同就照邏輯改寫。

**400 與 429 怎麼認**：Anthropic 的 Rate limits 文件明確寫了兩種帳務類回應，函式照著判斷：

- 你自己設的支出上限 → HTTP 400、`invalid_request_error`，訊息以固定前綴開頭（上述兩個，一般與工作區各一）。400 本身有很多種原因，所以**只比對訊息開頭**，不做「訊息裡含 billing／limit」這類寬鬆比對（那樣會把 `unknown field billing_address` 之類的格式錯誤誤判成帳務問題）。
- 用量層級上限 → HTTP 429，`error.details.error_code == "enforced_spend_limit_reached"`，用這個欄位和一般速率限制區分。呼叫時把這個欄位值傳進 `code`（OpenAI 則傳 `error.code`）。

文件提到的例外：Claude Code 工作區超過上限時，可能改回**帶有 `retry-after`** 的 429；這種回應在下面函式會被當成 `TRANSIENT`（照 `Retry-After` 重試），不會停下來。你的流量若包含該工作區，請在呼叫端另外處理。前綴字串若日後文件改版，函式會漏判成 `REQUEST_STOP`，所以要定期對照來源頁。

```python
# 帳務類錯誤碼：OpenAI 的 error.code；Anthropic 的 error.details.error_code（用量層級上限的 429）
BUDGET_CODES = {"credit_balance_exhausted", "insufficient_quota", "enforced_spend_limit_reached"}
# Anthropic：達到自己設定的支出上限時回 400，訊息以這兩個前綴之一開頭（小寫比對）。只比對開頭，不比對關鍵字。
BUDGET_MESSAGE_PREFIXES = (
    "you have reached your specified api usage limits",
    "you have reached your specified workspace api usage limits",
)


def classify(status=None, code=None, retry_after=False, timeout=False, message="",
             streak_429_no_retry_after=0, streak_limit=3):
    """回傳 TRANSIENT｜BUDGET_STOP｜AUTH_DISABLE｜POLICY_STOP｜REQUEST_STOP。"""
    if timeout or status is None:            # 逾時、連線錯誤
        return "TRANSIENT"
    if status == 402 or code in BUDGET_CODES:
        return "BUDGET_STOP"
    if status == 400 and (message or "").strip().lower().startswith(BUDGET_MESSAGE_PREFIXES):
        return "BUDGET_STOP"                 # 只對 400 比對訊息開頭，429 走下面的規則
    if status == 429:
        if retry_after:
            return "TRANSIENT"
        # 連續多次沒有 retry-after 的 429，當作額度問題，不再重試
        return "BUDGET_STOP" if streak_429_no_retry_after + 1 >= streak_limit else "TRANSIENT"
    if status == 401:
        return "AUTH_DISABLE"
    if status == 403:
        return "POLICY_STOP"
    if status in (500, 502, 503, 504, 529):
        return "TRANSIENT"
    return "REQUEST_STOP"


# ---- 斷言（每一類至少一個正例、一個反例）----
assert classify(timeout=True) == "TRANSIENT"
assert classify(status=None) == "TRANSIENT"
for st in (500, 502, 503, 504, 529):
    assert classify(st) == "TRANSIENT", st
assert classify(429, retry_after=True) == "TRANSIENT"                        # 速率限制，照 Retry-After 等
assert classify(429) == "TRANSIENT"                                          # 第一次沒有 Retry-After，先當速率限制
assert classify(429, streak_429_no_retry_after=2) == "BUDGET_STOP"           # 連續第 3 次，升級
assert classify(429, retry_after=True, streak_429_no_retry_after=9) == "TRANSIENT"
assert classify(429, code="credit_balance_exhausted", retry_after=True) == "BUDGET_STOP"
assert classify(402) == "BUDGET_STOP"
assert classify(400, code="invalid_request_error",
                message="You have reached your specified API usage limits. You will regain access on 2026-09-01 at 00:00 UTC.") == "BUDGET_STOP"
assert classify(400, message="  you have reached your specified workspace api usage limits ...") == "BUDGET_STOP"  # 工作區版、不分大小寫
assert classify(429, code="enforced_spend_limit_reached") == "BUDGET_STOP"                        # tier 上限，第一次就停
assert classify(429, code="enforced_spend_limit_reached", retry_after=True) == "BUDGET_STOP"      # 錯誤碼優先於 retry-after
assert classify(400, message="tools.0: unknown field billing_address") == "REQUEST_STOP"          # 含 billing 的格式錯誤不是帳務
assert classify(400, message="max_tokens: usage limit for this model is 8192") == "REQUEST_STOP"  # 含 usage limit 的格式錯誤也不是
assert classify(400, message="Error: You have reached your specified API usage limits") == "REQUEST_STOP"  # 只認開頭
assert classify(400, code="invalid_request_error", message="messages: field required") == "REQUEST_STOP"
assert classify(400) == "REQUEST_STOP"                                       # 沒有訊息就無從判斷，當請求錯誤
assert classify(429, message="You have reached your specified API usage limits") == "TRANSIENT"  # 訊息比對只對 400
assert classify(401) == "AUTH_DISABLE"
assert classify(403) == "POLICY_STOP"
for st in (404, 413, 422):
    assert classify(st) == "REQUEST_STOP", st
```

## 3. 容錯狀態機

每個端點各有一個狀態；路由層另有一條「依序嘗試」的鏈。

```text
 單一端點的狀態

   ┌────────┐   TRANSIENT 連續失敗 >= FAIL_THRESHOLD    ┌──────┐
   │ CLOSED │ ────────────────────────────────────────► │ OPEN │  隔離 COOLDOWN_SEC 秒
   │ (健康) │                                            └──┬───┘
   └────────┘                                               │ 冷卻結束
      ▲                                                     ▼
      │            探測成功                          ┌─────────────┐
      └───────────────────────────────────────────── │  HALF_OPEN  │ 只放 1 個探測請求
                                                     └──────┬──────┘
                                    探測失敗：回到 OPEN，冷卻加倍 ┘

   任一狀態 ── 401 (AUTH_DISABLE) ─────────► AUTH_DISABLED   需人工 reset
   任一狀態 ── BUDGET_STOP / POLICY_STOP ──► HELD            需人工 release

 路由鏈（依 routes 順序；只挑 CLOSED／HALF_OPEN 且 data_classes 符合的端點）

   請求 ─► [端點 1] ──成功──► 回應
              │ TRANSIENT 且重試用完，或 AUTH_DISABLE
              ▼
           [端點 2] ──成功──► 回應（並寫一筆切換紀錄）
              │ 同上
              ▼
           [本機模型] ──成功──► 回應（allow_quality_drop = false 時跳過這一步）
              │ 同上
              ▼
           EXHAUSTED ──► 回錯誤給呼叫端並通知人，不再無限重試

   任何一步遇到 BUDGET_STOP / POLICY_STOP / REQUEST_STOP：不往下一個端點走，直接停。
```

| 狀態轉換 | 條件 | 預設值（請依自己的流量調整） |
| :--- | :--- | :--- |
| CLOSED → OPEN | 連續 `TRANSIENT` 失敗次數 | `<FAIL_THRESHOLD>` = 3 |
| OPEN → HALF_OPEN | 冷卻時間 | `<COOLDOWN_SEC>` = 60 |
| HALF_OPEN → CLOSED | 探測請求成功 | 1 次 |
| HALF_OPEN → OPEN | 探測請求失敗 | 冷卻時間加倍，上限 `<COOLDOWN_MAX_SEC>` = 900 |
| 任一 → AUTH_DISABLED | `AUTH_DISABLE` | 需人工 `reset` |
| 任一 → HELD | `BUDGET_STOP`、`POLICY_STOP` | 需人工 `release` |

## 4. 設定範例

下面是完整可填的 YAML。端點網址已查證（見第 7 節來源）；環境變數名稱是你自己的約定，不是廠商規定；模型 ID 一律留空白讓你填，因為模型名稱更新很快。**金鑰只放環境變數，不進設定檔、不進 git。**

```yaml
policy:
  version: 1
  allow_kinds: [official_api, local_model]    # P1：不得加入其他 kind
  allow_quality_drop: true                    # false = 不自動切到本機模型，直接 EXHAUSTED
  retry:
    max_attempts_per_endpoint: 3
    backoff: { base_sec: 1, factor: 2, max_sec: 30, jitter: true }
    honor_retry_after: true
  circuit:
    fail_threshold: 3
    cooldown_sec: 60
    cooldown_max_sec: 900
  budget_guard:
    streak_429_no_retry_after: 3              # 連續幾次無 Retry-After 的 429 升級為 BUDGET_STOP
    monthly_cap_usd: <MONTHLY_CAP>            # 自己設的軟上限，超過就 HELD
  notify: { channel: <YOUR_CHANNEL>, events: [BUDGET_STOP, POLICY_STOP, AUTH_DISABLE, EXHAUSTED] }   # 不要用 on 當鍵：YAML 1.1 會把它讀成布林
  log: { path: <LOG_PATH>, include_prompt: false }

endpoints:
  - id: xai_api
    kind: official_api
    base_url: https://api.x.ai/v1
    auth: { type: bearer, env: <XAI_KEY_ENV> }
    billing: metered
    data_classes: [public, internal]
    model: <XAI_MODEL_ID>
    timeout_sec: 120

  - id: anthropic_api
    kind: official_api
    base_url: https://api.anthropic.com
    auth: { type: api_key_header, env: <ANTHROPIC_KEY_ENV> }
    billing: metered
    data_classes: [public, internal]
    model: <ANTHROPIC_MODEL_ID>
    timeout_sec: 120

  - id: openai_api
    kind: official_api
    base_url: https://api.openai.com/v1
    auth: { type: bearer, env: <OPENAI_KEY_ENV> }
    billing: metered
    data_classes: [public, internal]
    model: <OPENAI_MODEL_ID>
    timeout_sec: 120

  - id: local_ollama
    kind: local_model
    base_url: http://localhost:11434/v1/      # Ollama 的 OpenAI 相容端點；api_key 欄位需填值但不會被檢查
    auth: { type: none }
    billing: none
    data_classes: [public, internal, confidential]
    model: <LOCAL_MODEL_NAME>
    timeout_sec: 300

routes:
  coding_agent:                               # 依序嘗試
    - xai_api
    - anthropic_api
    - local_ollama
  confidential_tasks:                         # 資料等級 confidential 只能走本機
    - local_ollama
```

填完後對照這張表自我檢查：

| 檢查 | 預期 |
| :--- | :--- |
| `endpoints` 裡每個 `kind` 都在 `allow_kinds` 內 | 是 |
| 任何 `base_url` 是 loopback 以外的 http（明文）或非官方網域 | 沒有 |
| 設定檔裡有任何金鑰字串 | 沒有（只有 `env` 名稱） |
| `confidential_tasks` 路由只含 `data_classes` 有 `confidential` 的端點 | 是 |
| 本機端點 `base_url` 是 `localhost` 或 `127.0.0.1`，且本機模型服務沒有對外網卡開放 | 是（服務綁在哪個位址依該服務的文件確認；它的設定檔若有 bind／listen 欄位，可用 `python C:\GitHub\agent-safety-checks\tools\audit_oauth_credentials.py --dir <設定檔資料夾>` 掃一遍） |

## 5. 切換事件紀錄欄位

每次換端點、進入／離開 `OPEN`、`AUTH_DISABLED`、`HELD`，寫一筆 JSON Lines。**不要記提示詞或回應內容。**

```json
{
  "ts": "<ISO8601>",
  "route": "coding_agent",
  "from": "xai_api",
  "to": "anthropic_api",
  "error_class": "TRANSIENT",
  "status": 529,
  "attempts": 3,
  "retry_after_sec": null,
  "data_class": "internal",
  "decision": "failover",
  "approved_by": "auto"
}
```

`decision` 的值：`failover`、`retry`、`hold`、`disable`、`exhausted`。`approved_by` 為 `auto` 或人名／帳號代稱；`hold` 之後的放行一定要是人。

## 6. 切換前的檢查清單（人工放行 `HELD` 或擴充路由時用）

- [ ] 要切過去的端點在 `allow_kinds` 內，帳務主體是你自己（金鑰在你的組織下）。
- [ ] 預算：新端點的單價與你的 `monthly_cap_usd` 相容；`BUDGET_STOP` 的原因已處理（儲值或調整上限），而不是換端點躲過。
- [ ] 資料等級：請求內容的等級在新端點的 `data_classes` 內。
- [ ] 能力相容：新端點的模型支援你用到的工具呼叫格式與上下文長度（不同供應商不一定相同，實測再放進路由）。
- [ ] `403` 的原因已查明（權限、地區、政策）；不是用換端點去避開它。
- [ ] 切換紀錄已寫，通知對象知道發生了什麼。

## 7. 各供應商的使用邊界（以官方文件為準）

這裡只列**官方文件明文寫的**邊界，不列任何偵測或風控細節。條款會改，採用前以來源頁面最新版為準。

| 供應商 | 文件明文 | 範本的對應做法 |
| :--- | :--- | :--- |
| Anthropic | Claude Code 的 OAuth 認證僅供方案購買者日常使用 Claude Code 與其他原生應用；開發產品或服務（含 Agent SDK）應使用 API 金鑰；不允許第三方以 Free／Pro／Max／Ultra 方案憑證代使用者轉送請求，也不允許蒐集、儲存或居中轉手 Claude.ai 憑證 | 路由層只放 API 金鑰端點 |
| OpenAI | Codex 提供「ChatGPT 登入」與「API 金鑰登入」兩種，後者按用量計費、適用 API 組織的資料政策 | 路由層只放 API 金鑰端點；用 ChatGPT 登入的是官方 Codex 客戶端本身，不是你自己的路由層 |
| xAI | API 為 `https://api.x.ai/v1` 加 `XAI_API_KEY`；X Subscription 的每週額度池只涵蓋 Grok 與 Cursor 受支援介面的第一方用量；Grok CLI 另提供 `grok -p` 與 `grok agent stdio`（ACP）供無人值守使用 | 路由層放 API 金鑰端點；要用訂閱額度就直接執行官方 `grok` 客戶端，不要經過自己的路由層轉送 |

## 8. 已知限制

- 錯誤碼對照來自 Anthropic 與 OpenAI 的錯誤頁、xAI 的速率限制頁；xAI 完整的錯誤碼分類與 `Retry-After` 行為**未逐項驗證**，範本對 xAI 只套用「429 且有 `Retry-After` 才直接重試，否則依連續次數判斷」的通用規則。
- 本機模型的品質與工具呼叫能力常低於雲端模型，`allow_quality_drop` 預設 `true` 只是為了示範；對品質敏感的任務請設為 `false`。
- 範本不處理跨端點的對話狀態遷移（各家 session／response id 不互通）；切換端點時請由呼叫端帶完整上下文。
- 第 2.1 節的函式只做錯誤分類，重試、冷卻、狀態機要自己實作；沒有附整套路由器。

## 來源（查證日期 2026-11-02）

- Anthropic，API 錯誤碼：<https://platform.claude.com/docs/en/api/errors>
- Anthropic，Rate limits（支出上限的 400 訊息前綴、`enforced_spend_limit_reached`；2026-11-02 查證）：<https://platform.claude.com/docs/en/api/rate-limits>
- Anthropic，API 概覽（基底網址 `https://api.anthropic.com`）：<https://platform.claude.com/docs/en/api/overview>
- Anthropic，Claude Code「Legal and compliance」：<https://code.claude.com/docs/en/legal-and-compliance>
- OpenAI，API 錯誤碼：<https://developers.openai.com/api/docs/guides/error-codes>
- OpenAI，Codex「Authentication」：<https://developers.openai.com/codex/auth>
- xAI，API 概覽：<https://docs.x.ai/docs/overview>；速率限制：<https://docs.x.ai/docs/key-information/consumption-and-rate-limits>；用量限制：<https://docs.x.ai/x-subscription/usage-limits.md>；Headless 與 ACP：<https://docs.x.ai/build/cli/headless-scripting.md>
- Ollama，OpenAI 相容 API（`http://localhost:11434/v1/`）：<https://github.com/ollama/ollama/blob/c1db5f9ef203b2e946161bf4c6bd4f2ec7f123b3/docs/api/openai-compatibility.mdx>
- OpenAI，Quickstart（基底網址 `https://api.openai.com/v1`）：<https://developers.openai.com/api/docs/quickstart>
