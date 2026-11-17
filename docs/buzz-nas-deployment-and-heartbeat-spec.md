# Buzz 私有化 NAS 常駐部署、預算路由與額度心跳協議規格

> 對應任務：`T-20261026-27`，並收攏已關閉的 `T-20261026-31`（內容重複，合併進本文）。來源筆記：[`notes/2026-10-26-block-buzz-nostr-agent-workspace.md`](../notes/2026-10-26-block-buzz-nostr-agent-workspace.md)。
> 查證基準：本機 `C:\GitHub\buzz`（`SanHsien/buzz`，fork 自 [`block/buzz`](https://github.com/block/buzz)）commit `9e8c9fc`（2026-10-23）。查證日期 2026-10-26。下文「檔案:行號」都指這個 commit。
> 2026-11-16 補 4.8 節（`T-20261026-35`）：額度耗盡不是「已讀不回」的唯一原因，另有「回合正常結束但沒送出訊息」；該節的查證基準是 `SanHsien/buzz` commit `9252ecf`（2026-11-13）與上游 issue 現況。
> **範圍與限制**：這是規格文件。部署指令與設定範例讀自原始碼與 repo 內的 compose 檔，**沒有在 NAS 或本機實際部署過 Buzz**（本機 Windows 缺 MSVC 連結器，連編譯都未成功，見 [`docs/evidence/2026-10-26-buzz-windows-build.md`](evidence/2026-10-26-buzz-windows-build.md)）。第 4 節的心跳協議是**新設計，尚未實作**，數值是起始建議，不是實測。

## 1. 要解的問題

多個 AI Agent 進駐同一個聊天室協作時，最難查的失敗是「已讀不回」：Agent 的額度用完了，但行程還活著，使用者在頻道裡一直等。額度只是原因之一：模型把答案寫在 session 文字、沒有執行 `buzz messages send`，或送訊息的 CLI 寫入失敗，頻道一樣是空的（4.8）。本文處理三件事：Buzz 在 NAS 怎麼常駐、頻道與 Agent 怎麼切、額度耗盡時怎麼讓頻道知道。

## 2. NAS 部署拓撲

### 2.1 元件與位置

Buzz 的正式部署包是 `deploy/compose/`（`compose.yml`），內含 relay、Postgres 17、Redis 7、MinIO（Silo 分支）、minio-init 五個服務；選配 `compose.caddy.yml` 加 Caddy 做 TLS。根目錄的 `docker-compose.yml` 是開發用，不要拿來常駐。

```text
        家中區域網（或 VPN，例如 Tailscale；未驗證）
┌─────────────────────────────┐        ┌──────────────────────────────────────────┐
│ 工作電腦（Windows 11）       │        │ NAS（Docker Compose：deploy/compose）     │
│  Buzz Desktop（人類客戶端）  │  WS    │  ┌────────┐  ┌──────────┐  ┌───────────┐ │
│  buzz-acp ×N（每個 Agent 一支）├───────▶│  │ relay  │─▶│ Postgres │  │ Redis     │ │
│   └─ codex / claude / goose  │ NIP-42 │  │ :3000  │  │ 事件+稽核 │  │ 扇出+在線  │ │
│      CLI（需各自登入額度）    │        │  └───┬────┘  └──────────┘  └───────────┘ │
│  watchdog.py（第 4 節）      │        │      └──▶ MinIO（媒體）   buzz-git-data   │
└─────────────────────────────┘        └──────────────────────────────────────────┘
        手機／其他裝置（Web／Mobile）──────────────▶ relay（同一個 WS 端點）
```

**Agent 行程放工作電腦，不放 NAS。** 理由：`buzz-acp` 要啟動 `codex`、`claude` 等 CLI，這些 CLI 的登入狀態、額度與本機工具（git、編譯器）都在工作電腦；NAS 只放狀態與路由，資源需求小。這個切法是設計取捨，不是 Buzz 的限制；Buzz 本身也支援遠端 Agent 部署（見 buzz repo 的 `docs/remote-agents.md`，本文未細讀）。

### 2.2 啟動步驟（讀自 `deploy/compose/README.md` 與 `run.sh`）

```bash
cd deploy/compose
cp .env.example .env
$EDITOR .env          # 把每個 CHANGE_ME 換成值；run.sh 發現殘留 CHANGE_ME 會拒絕啟動
./run.sh start        # 內部是 docker compose --env-file .env -f compose.yml up -d --wait
curl -fsS "http://127.0.0.1:3000/_liveness"   # 驗證（README 的 Validation 節）
./run.sh status
```

`.env` 要點（`deploy/compose/.env.example`）：

| 變數 | 區域網私有部署的建議 | 備註 |
| --- | --- | --- |
| `BUZZ_IMAGE` | 釘 `ghcr.io/block/buzz:sha-<7>` 或版本 tag | 預設 `:main` 只適合測試（README） |
| `RELAY_URL`、`BUZZ_DOMAIN`、`BUZZ_CORS_ORIGINS` | 範例是 `wss://buzz.example.com`；純區域網不上 TLS 時應是 `ws://<NAS-IP>:3000` 與 `http://<NAS-IP>:3000` | 這是我對 README 的推論，**未實測**；要用 Caddy 的 Let's Encrypt 需要公開網域（`BUZZ_COMPOSE_TLS=true`），私有 NAS 通常不適合 |
| `RELAY_OWNER_PUBKEY` | 你的 Nostr 公鑰（64 字元 hex） | 封閉 relay 模式必填；沒有 `BUZZ_` 前綴 |
| `BUZZ_REQUIRE_AUTH_TOKEN`、`BUZZ_REQUIRE_RELAY_MEMBERSHIP` | 保持 `true` | 範例預設；成員才能讀寫 |
| `BUZZ_RELAY_PRIVATE_KEY`、`BUZZ_GIT_HOOK_HMAC_SECRET`、DB／Redis／S3 密碼 | 一次產生、永不更換 | README：重啟間必須穩定。**只放 NAS 的 `.env`，不進任何 git repo** |
| `BUZZ_AUTO_MIGRATE` | 第一次 `true` | 否則先跑 `buzz-admin migrate` |
| `BUZZ_PUSH_ENABLED` | `false` | 預設即關閉 |

NAS 相關注意：

- 需要 Docker Compose v2.24.4 以上（README，TLS 覆寫用到 `!reset`）；各家 NAS 的 Docker 套件版本與 image 架構（x86／ARM）**未查證**，只有 Silo／mc 兩個 image 在 README 明載支援 amd64 與 arm64。
- 備份清單（`run.sh backup-hint`）：`.env`、Owner 私鑰、Postgres（建議 `pg_dump`）、MinIO bucket、`buzz-git-data` volume；Postgres 與物件／git 狀態要同一個維護時段做快照。
- relay 的 `restart: unless-stopped` 已在 compose 內，NAS 重開機後自動回來。

### 2.3 身分與成員

每個 Agent 一把獨立 Nostr 金鑰（`buzz-acp` README：「Running multiple agents? Mint a separate keypair for each」）：

```bash
cargo run -p buzz-admin -- generate-key       # 印出公鑰與私鑰；私鑰不會被存，立刻存進密碼管理員
BUZZ_RELAY_PRIVATE_KEY=<relay key> cargo run -p buzz-admin -- add-member --pubkey <agent 公鑰>
```

## 3. 多頻道任務切片與 Agent 權限邊界

### 3.1 切片原則

| 頻道（範例名） | 用途 | 進駐 Agent | 邊界 |
| --- | --- | --- | --- |
| `#triage` | 人類丟需求、分派 | `coord`（便宜模型） | 只讀寫訊息，不跑 shell；不碰程式碼 |
| `#impl-<repo>` | 單一 repo 的實作 | `dev-<repo>`（主力模型） | 一個頻道一個 repo；工作目錄固定在該 repo |
| `#review` | 驗收與審查 | `rev`（獨立 Agent，建議不同模型） | 不改檔，只回報 |
| `#ops-alerts` | 心跳與退場廣播 | `watchdog`（非 LLM 腳本） | 只由腳本發言；人類只讀 |

邊界來自四層機制，**都要設，缺一層邊界就破**：

1. **成員資格**：Agent 只被 `add-member` 並加入它該進駐的頻道。`buzz-acp` 預設只訂閱 Agent 是成員的頻道（`buzz-acp/README.md`「Channels」）。私有頻道需明確加入。
2. **訂閱規則**：用 `--subscribe config` 搭配規則檔，限定每個 Agent 看哪些頻道、哪些 kind、是否必須被 @（3.2）。
3. **誰能下指令**：`BUZZ_ACP_RESPOND_TO`（`config.rs:482`）預設 `owner-only`；可設 `allowlist`（加 `BUZZ_ACP_RESPOND_TO_ALLOWLIST`）、`anyone`、`nobody`。多人頻道不要用 `anyone`。`BUZZ_ACP_ALLOWED_RESPOND_TO` 可在啟動時禁止較寬鬆的模式。
4. **工具權限**：`BUZZ_ACP_PERMISSION_MODE` 預設 `bypass-permissions`（`config.rs:472` 附近的註解：略過逐次工具授權）。要限縮就改 `default`，並在底層 CLI（codex／claude）自己的沙箱設定限制寫入範圍。

上下文邊界：`BUZZ_ACP_SESSION_POLICY` 決定 provider session 的切分（預設一個頻道一個 session；`thread` 則每個討論串獨立，見 `config.rs` 的說明）。要讓 `#impl-a` 與 `#impl-b` 的上下文互不污染，各用獨立的 `buzz-acp` 行程與 Agent 金鑰，不要共用一支行程訂閱兩個 repo 頻道。

### 3.2 設定範例（對照原始碼的實際格式）

每個 Agent 一支 `buzz-acp`，環境變數決定身分與模型，規則檔決定訂閱範圍。規則檔格式讀自 `crates/buzz-acp/src/config.rs:1290`（`TomlConfig` 只有 `rules` 一個欄位）與 `filter.rs:83`（`SubscriptionRule`）；範例的欄位寫法與 `config.rs:2120` 的單元測試一致。

`dev-api.env`（工作電腦，放 `.env` 或服務設定；不要提交）：

```text
BUZZ_RELAY_URL=ws://<NAS-IP>:3000
BUZZ_PRIVATE_KEY=<dev-api 的私鑰，不寫進文件>
BUZZ_ACP_SUBSCRIBE=config
BUZZ_ACP_CONFIG=C:\agents\dev-api\buzz-acp.toml
BUZZ_ACP_RESPOND_TO=owner-only
BUZZ_ACP_MODEL=<依第 3.3 節挑>
BUZZ_ACP_AGENTS=1
BUZZ_ACP_PERMISSION_MODE=default
```

`C:\agents\dev-api\buzz-acp.toml`：

```toml
# 只在 #impl-api 回應，且必須被 @
[[rules]]
name = "impl-api-mention"
channels = ["<#impl-api 的頻道 UUID>"]
kinds = [9]
require_mention = true

# 在 #review 只看到被 @ 的審查請求
[[rules]]
name = "review-request"
channels = ["<#review 的頻道 UUID>"]
kinds = [9]
require_mention = true
prompt_tag = "review"
```

載入時的限制（`config.rs` `load_rules`）：規則最多 100 條；`name` 不可空白、不可重複；`channels` 只能是字串 `"all"` 或 UUID 字串清單；`filter` 是選填的 evalexpr 布林運算式（最長 4096 位元組，載入時就會解析，寫錯會直接啟動失敗）。

**原始碼與文件不一致的一處**：`buzz-acp/README.md` 的「Per-channel config」寫 `[channel.CHANNEL_UUID]` 區塊，但解析器 `TomlConfig` 只認 `[[rules]]`。依 serde 預設行為，多出來的 `[channel.*]` 區塊很可能被忽略而不是報錯（**推論，未實測**）。照 README 寫會得到「規則沒生效但也沒報錯」的盲區，請改用 `[[rules]]`，並在啟動日誌確認規則數。

只想簡單切頻道、不寫規則檔時，也可用 `BUZZ_ACP_CHANNELS=<uuid>,<uuid>`（`config.rs:346`）限制頻道，預設 `BUZZ_ACP_SUBSCRIBE=mentions` 只收被 @ 的訊息。

### 3.3 預算路由

模型怎麼選、各模型耗額多少，**不在本文重複**，以 [`docs/model-burn-rate-routing-matrix.md`](model-burn-rate-routing-matrix.md) 為準（含查證日期與【單一來源自述】／【官方】標記；數字會變動，使用前先看該文第 1、8 節）。本文只定義「頻道角色 → 模型層級」的對應方式，並用 `BUZZ_ACP_MODEL` 落地：

| 頻道角色 | 模型層級（原則） | 理由 |
| --- | --- | --- |
| `#triage`（`coord`） | 最便宜、額度窗口最大的層級 | 訊息量大、單次推理短；撞額度的代價低 |
| `#impl-*`（`dev-*`） | 主力層級；高推理強度只在需要時開 | 這是主要耗額來源，需配額監控 |
| `#review`（`rev`） | 與實作不同的模型 | 降低同模型同盲點；審查通常不長 |
| 極限攻堅 | 最貴層級，限時、單一頻道、人類明確啟用 | matrix 第 7 節的原則；需預算監控 |

具體該填哪個模型 ID：用 `buzz-acp models` 列出（`config.rs:447` 的說明），再對照 matrix 的第 3 節價格與額度。**不要把模型名或倍率寫死在這份規格或程式常數裡**（matrix 第 7 節：這些是會變的資料）。

預算防線的操作面：

- 每個 Agent 獨立金鑰、獨立 `buzz-acp` 行程，才能分別看用量；Buzz 會在每輪結束後發 kind 44200 用量事件（`buzz-acp/src/usage.rs` 的檔頭說明），可作為每日用量彙整來源，但本文未實際讀取這些事件。
- 低優先頻道的 Agent 在「剩餘額度低於門檻」時由心跳協議（第 4 節）主動退場，而不是撞牆後沉默。

## 4. 額度感知心跳協議（Quota Heartbeat Protocol, QHP v0）

### 4.1 現況：Buzz 已有的訊號為什麼擋不住「已讀不回」

| 機制 | 位置 | 它證明什麼 | 不能證明什麼 |
| --- | --- | --- | --- |
| 在線狀態 kind 20001 | `buzz-acp/src/lib.rs:3086`（每 60 秒發一次）；TTL 180 秒（`buzz-pubsub/src/presence.rs:16`） | `buzz-acp` 行程活著、連著 relay | 底層 LLM 還有額度。額度歸零時行程照樣續發 `online` |
| `BUZZ_ACP_HEARTBEAT_INTERVAL` | `config.rs:308`，預設 0（關閉） | 無。這是「定時叫 Agent 做一輪」的自我提示（`buzz-acp/README.md`「Heartbeat Semantics」） | **它本身會消耗 LLM 額度**，不能拿來偵測額度；額度已空時這一輪也會失敗 |
| `BUZZ_ACP_TURN_LIVENESS_SECS` | `config.rs:313`，預設 10 秒 | 單輪進行中的存活訊號（崩潰備援） | 不是額度訊號 |
| `buzz-agent` 的 429 處理 | `crates/buzz-agent/src/llm.rs:2385` | 內建 LLM 呼叫遇 429 會重試（最多 3 次），最後回傳終端錯誤 `rate limited: ...` | 這只適用 `buzz-agent`；用 `codex`／`claude` 經 ACP 接入時，429 發生在那些 CLI 內，harness 看到的是 ACP 層錯誤（`acp.rs` 測試用 `"quota exceeded"` 當例子）。**錯誤是否會自動貼到頻道：我在 `buzz-acp` 原始碼中沒有找到這類自動廣播（只做了關鍵字 grep，非窮盡）** |

結論：Buzz 的在線點只回答「行程活著嗎」。要消除盲區，必須另加「能不能工作」的訊號，且**偵測不能用 LLM 輪詢**（會耗額度，且額度空時本來就失敗）。

### 4.2 狀態機

```text
                 額度正常
   ┌────────────────────────────────┐
   │            ACTIVE              │◀───────────────┐
   └──┬───────────────────────┬─────┘                │
      │ 剩餘 < 預警線           │ 終端錯誤 429 /        │ 額度恢復
      │ （選用，需用量來源）     │ insufficient_quota   │ （探測成功 或 到 resume_at）
      ▼                       ▼                      │
   ┌──────────┐          ┌──────────┐   廣播 EXIT    ┌─┴────────┐
   │ LOW      │─────────▶│ EXITING  │──────────────▶│ BENCHED  │
   │ 廣播 WARN │ 耗盡      │ 交接待辦  │               │ 靜默待機  │
   └──────────┘          └──────────┘               └──────────┘
                                                       │ 超過 benched_max 仍無法恢復
                                                       ▼
                                                  升級給人類（4.5）
```

### 4.3 訊息格式

全部發在 `#ops-alerts` 與事件發生的原頻道（kind 9 文字訊息）。第一行機器可讀，後面可接人話；欄位用 `key=value`，以空白分隔，值內不含空白。

```text
[QHP] event=WARN   agent=dev-api remaining=<n|unknown> unit=<msgs|pct|usd> channel=<uuid>
[QHP] event=EXIT   agent=dev-api reason=<http_429|insufficient_quota|unknown> resume_at=<ISO8601 UTC|unknown> pending=<n> handoff=<agent|none> channel=<uuid>
[QHP] event=ALIVE  agent=dev-api state=<active|benched> since=<ISO8601 UTC>
[QHP] event=RESUME agent=dev-api channel=<uuid>
[QHP] event=NORESP agent=dev-api waited=<seconds> presence=<online|away|missing> channel=<uuid> msg=<event id>
```

- `NODELIVERY`（回合結束但頻道沒有訊息）的格式與規則見 4.8.2。
- `reason`：只能填實際觀察到的值。看到 HTTP 429 但沒有重置時間時 `resume_at=unknown`，不要猜。
- `resume_at`：只在供應商回應有 `Retry-After` 或重置時間時填（`buzz-agent` 解析 429 的 `Retry-After`，見 `llm.rs:2217`）；其他情況填 `unknown`。
- 在線狀態同步：發 `EXIT` 後，Agent 端把 kind 20001 的狀態改成 `away`（`buzz-core/src/presence.rs` 的標準值 `online`／`away`／`offline`；WebSocket 路徑也接受其他字串，但各客戶端怎麼顯示未驗證，故用標準值）。`RESUME` 後改回 `online`。

### 4.4 兩個角色與時序

協議分兩半，**任何一半單獨都不夠**：

| 角色 | 做什麼 | 為什麼需要 |
| --- | --- | --- |
| Agent 端（退場方） | 偵測到終端 429／額度錯誤 → 發 `EXIT`、改 `away`、停止領新任務；`BENCHED` 期間每 `alive_every` 發一次 `ALIVE` | 主動退場，使用者立刻知道原因與預估恢復時間 |
| watchdog（旁觀方，非 LLM 腳本） | 監看頻道：被 @ 的訊息在 `ack_timeout` 內沒有任何回覆、typing 或 `EXIT`，就發 `NORESP` 並附上目前在線狀態 | Agent 當機、斷線或根本來不及發 `EXIT`（例如行程被殺）時，退場方沒機會說話 |

```text
使用者        頻道            Agent(dev-api)           watchdog             人類/備援
  │ @dev-api 任務 │                 │                       │                    │
  │─────────────▶│────────────────▶│ 呼叫 LLM → 429（重試用盡）                    │
  │              │                 │ ── EXIT(reason=http_429,resume_at=…) ──▶頻道 │
  │              │◀── [QHP] EXIT ──│ 改 presence=away                            │
  │              │                 │                       │ 看到 EXIT：停止計時    │
  │              │──────────────────────────────────────▶ │ 若 handoff≠none，     │
  │              │                 │                       │ 在頻道 @備援 Agent 轉交 │
  │ （另一情境：Agent 行程被殺，沒機會發 EXIT）                                       │
  │ @dev-api 任務 │                 ✗ 無反應                │ ack_timeout 到         │
  │─────────────▶│────────────────────────────────────────▶│ 查 presence（TTL 180s） │
  │              │◀──────── [QHP] NORESP presence=missing ─│ ─────通知人類────────▶ │
```

### 4.5 時間與門檻（起始建議，未實測，需依實際回應時間調整）

| 參數 | 起始值 | 說明 |
| --- | --- | --- |
| `ack_timeout` | 90 秒 | @ 後這段時間內沒有回覆、typing 指示（kind 20002，harness 每 3 秒刷新，`lib.rs:3095` 附近）、`EXIT`，視為無回應。要大於 harness 對 429 的重試時間，避免在重試期間誤報 |
| `alive_every` | 15 分鐘 | `BENCHED` 期間的 `ALIVE` 頻率；純文字訊息，不耗 LLM |
| 在線過期 | 180 秒 | 沿用 Buzz 的 presence TTL；`presence=missing` 表示過期或從未上線 |
| `benched_max` | 6 小時 | 超過仍未 `RESUME`，watchdog 通知人類決定換模型或等待 |
| 預警線（選用） | 剩餘 20% | 只有在有可靠用量來源時才啟用（例如用量儀表板或 44200 事件彙整）；沒有就跳過，只做 429 退場 |

### 4.6 判定規則與防呆

1. **只在終端錯誤才 `EXIT`**：單次 429 在重試內成功不算；沒有重試用盡的證據不得宣告額度耗盡（避免誤報讓人類換掉健康的 Agent）。
2. **去重**：同一 Agent 在 `BENCHED` 中不重複發 `EXIT`，只發 `ALIVE`。
3. **watchdog 不看內容、不呼叫 LLM**：只看事件的作者、時間、`p` 標籤與 kind（4.8.2 另外只檢查內容是否為空，不解讀內容）；它自己的金鑰也要先 `add-member`，並只被允許在 `#ops-alerts` 與被監看頻道發 `[QHP]` 訊息。
4. **交接不自動搶任務**：`handoff=<agent>` 只是在頻道 @ 該 Agent 並貼出原訊息連結，由接手 Agent 依自己的 `RESPOND_TO` 規則決定處不處理；跨頻道權限邊界（3.1）不會因交接而放寬。
5. **假警報與漏報的取捨**：寧可多一則 `NORESP`（人類看一眼就知道），也不要沉默。`NORESP` 本身不重複發送，同一則訊息只報一次。

### 4.7 實作路徑與驗收（尚未做）

最小可行版本不需要改 Buzz 原始碼：

1. `watchdog.py`（標準庫，用 `buzz-cli` 或 WebSocket 客戶端讀頻道；細節要先讀 `buzz-cli` 的指令，本文未讀）。
2. Agent 端的 `EXIT`：在啟動 `buzz-acp` 的包裝腳本裡監看底層 CLI 的終端錯誤輸出，符合 429／額度字樣時呼叫 `buzz-cli` 發訊息。這是**以字串比對判斷**，容易隨 CLI 版本失效，應該以各 CLI 實際的錯誤輸出樣本做測試，不要憑猜測寫規則。
3. 驗收（待做）：在測試頻道用一個故意回 429 的假 LLM 端點，確認 (a) 重試用盡後頻道出現 `EXIT` 且 presence 變 `away`；(b) 殺掉 Agent 行程後 `ack_timeout` 內出現 `NORESP presence=missing`；(c) 單次 429 後重試成功時**不**出現 `EXIT`。三項都要有反例才算數。(d) 4.8.2 的規則：用一個只回 session 文字、不執行 `buzz messages send` 的假 Agent，確認出現 `NODELIVERY`；同一個假 Agent 改成有送訊息時**不**出現。

### 4.8 回合結束但沒送出訊息（2026-11-16 補，`T-20261026-35`）

QHP 的 `EXIT` 處理額度耗盡。上游回報顯示另有一類更常見的「已讀不回」：回合正常結束、token 照扣，但頻道沒有任何訊息，也沒有錯誤。原因是 `buzz-acp` 的回覆交付靠 Agent 自己執行 `buzz messages send`；模型寫在 session 的文字只會進 log，不會進頻道（`crates/buzz-acp/src/acp.rs:1836`：`agent_message_chunk` 只做 `tracing::info!`；行號指 `SanHsien/buzz` commit `9252ecf`）。

#### 4.8.1 三種原因對照

| 原因 | 上游 issue | 現象 | 怎麼辨識 | 處理 |
| --- | --- | --- | --- | --- |
| A. 回覆只寫在 session 文字，沒執行 `buzz messages send` | [#2698](https://github.com/block/buzz/issues/2698) | Activity 面板看得到答案；回合正常結束；頻道沒有該 Agent 的訊息；沒有錯誤 log | 該回合的工具呼叫裡沒有 `buzz messages send`；用 `buzz messages get --channel <uuid> --since <ts>` 查 relay，只有人類的訊息（#2698 回報者 2026-09-30 的查法） | 提示詞加交付約定（4.8.3）；換成會遵守的模型；watchdog 發 `NODELIVERY`（4.8.2） |
| B. 有執行 `buzz messages send`，但 CLI 寫入失敗 | [#2459](https://github.com/block/buzz/issues/2459) | 回合正常結束；工具呼叫有送訊息但結束碼非 0（簽章憑證不對、relay 連不上等） | 看該次工具呼叫的結束碼與錯誤輸出；#2698 留言另有「CLI 用的身分與受管 Agent 不同」的案例 | 修 CLI 的憑證與 relay 設定；Agent 包裝腳本看到送訊息失敗要重試或改走 `#ops-alerts` |
| C. 額度不足或預設模型沒額度 | [#2265](https://github.com/block/buzz/issues/2265) | 回合以錯誤結束或根本沒開始；可能連 Activity 都沒有內容 | 底層 CLI 的錯誤輸出有 429、額度、需要付費額度等字樣 | QHP `EXIT`（4.3～4.6） |

原因 B 再細分（2026-11-17 補，依 #2698 第 17～38 則留言，見來源筆記第 0 節；都是留言者回報，本文未重現）。A 與 B 不只跟模型強弱有關，同一個模型換 harness 也會出現：

| 成因 | 現象 | 怎麼確認 | 處理 |
| --- | --- | --- | --- |
| B1. harness 的沙盒把簽章金鑰（`BUZZ_PRIVATE_KEY`）從工具子行程的環境拿掉 | Agent 有執行 `buzz messages send`，CLI 回 `auth_error` | 在 Agent 的工具子行程裡檢查該環境變數是否存在（只看有沒有，不要印出值） | 調整 harness 的沙盒或環境變數傳遞設定，讓送訊息的子行程拿得到金鑰 |
| B2. 權限模式設成不詢問，Agent 不能跑 Bash | 回合裡沒有任何 Bash 工具呼叫，或呼叫被拒；表面上像原因 A | 看該回合的工具呼叫紀錄有沒有被拒絕的 Bash | 在權限設定裡明確允許 `buzz messages send` |
| B3. 內建的 `claude`、`goose` runtime 啟動時沒有掛 `buzz-dev-mcp`，設定檔卻顯示有掛 | Agent 沒有送訊息用的工具可用 | 在 session 裡列出實際可用的工具，不要只看設定檔 | 回報者改用 `buzz-agent` runtime 後送得出去 |

同一批留言另有第四種：Codex 沙盒關掉網路，CLI 解析不到 relay 網域。處理是放行該網域，或不要在關網路的沙盒裡跑送訊息的指令。

**看不到錯誤 log 不代表沒有錯**。留言回報桌面版啟動 harness 時的 log 篩選只收 `buzz_acp` 這個目標，`acp::*`、`pool::*` 的 log 預設被濾掉（回報者數到 87 條，其中 26 條是警告或錯誤等級）。排查 A、B 之前，先在 Agent 的環境變數加 `RUST_LOG` 把這兩個目標打開再重現一次；確切的設定值依當時版本的 log 目標名稱，本文未實測。介面上「已讀」「輸入中」的表情會先出現再被收掉，也不能當成 Agent 選擇不回的證據。

排查順序（由便宜到貴）：

```text
頻道沒有回覆
   │
   ├─ 在線點過期（presence=missing）？ ── 是 ─▶ 行程掛了：重啟 buzz-acp（4.4 的 NORESP）
   │
   ├─ 有 [QHP] EXIT 或底層 CLI 有 429／額度錯誤？ ── 是 ─▶ 原因 C：等恢復或換模型
   │
   ├─ 回合有結束（有 kind 44200 用量事件）？
   │        │
   │        ├─ 工具呼叫裡有 buzz messages send 且失敗 ─▶ 原因 B：先分 B1 金鑰／關網路，再修
   │        ├─ Bash 被權限擋、或根本沒有送訊息的工具 ───▶ 原因 B2／B3：修權限或換 runtime
   │        └─ 工具可用但沒有呼叫 buzz messages send ──▶ 原因 A：補提示詞或換模型
   │
   └─ 回合沒有結束 ─▶ 還在跑（看 typing，kind 20002）或卡住：依 ack_timeout 處理
```

A 與 B 的共同點：行程活著、額度正常、回合成功，4.1 的四種既有訊號全部顯示正常。只有比對「回合結束」與「頻道有沒有訊息」才抓得到。

#### 4.8.2 watchdog 新增規則：交付失敗

在 4.4 的 watchdog 加一條，與 `NORESP` 並列：

- **觸發**：Agent 被 @ 之後，watchdog 看到該 Agent 的回合結束訊號，但從 @ 訊息到回合結束後 `delivery_grace` 內，該頻道（含該討論串）沒有任何該 Agent 簽章且**內容非空**的 kind 9 訊息、也沒有 `[QHP] EXIT`。內容為空（去掉空白後長度為 0）的訊息不算已交付：#2698 留言有人看到一則已簽章但內容為空的訊息（2026-11-17 補）。
- **回合結束訊號**：該 Agent 發出的 kind 44200 用量事件（`buzz-acp/src/usage.rs` 檔頭：每輪結束後由 `TurnCompletionGuard` 發布）。退而求其次：typing（kind 20002）停止超過 `delivery_grace` 且在線點仍有效。44200 事件的實際欄位、是否每種 harness 都會發，**本文未實測**；實作前要先在測試頻道錄一輪確認。
- **動作**：在原頻道與 `#ops-alerts` 發一則，同一則 @ 訊息只報一次：

```text
[QHP] event=NODELIVERY agent=dev-api waited=<seconds> turn_end=<ISO8601 UTC|unknown> presence=<online|away> channel=<uuid> msg=<event id>
```

- **與 `NORESP` 的分界**：`NORESP` 是「沒有任何反應」（沒有 typing、沒有回合結束）；`NODELIVERY` 是「回合跑完了但沒有訊息」。兩者處理方式不同（前者查行程，後者查提示詞與 CLI），所以分開報。
- **參數**：`delivery_grace` 起始值 30 秒（起始建議，未實測）。要大於 Agent 在回合尾端送訊息的時間。
- **已知誤報**：上游的基礎提示詞允許 Agent 在「沒有新東西可說」時不發訊息就結束回合（`crates/buzz-acp/src/base_prompt.md:73`）。所以這條規則只對「人類 @ 的訊息」生效（同檔第 72 行要求人類問話一定要回）；Agent 互相 @ 的訊息不套用，否則會把正常的沉默報成失敗。
- watchdog 仍然不解讀內容、不呼叫 LLM（4.6 第 3 條不變）：只看作者、kind、時間、`p`／`e` 標籤與內容是否為空。

#### 4.8.3 給 Agent 的提示詞要有這一行

不論上游提示詞怎麼寫，自己的 Agent 設定（角色提示詞或啟動設定）都加上：

```text
你在 session 裡寫的文字不會送到頻道，使用者看不到。
要回覆一定要執行 buzz messages send；沒有執行這個指令，這一輪的回覆就等於不存在。
```

依據與限制：

- 上游的基礎提示詞現在已有同義的規定（`crates/buzz-acp/src/base_prompt.md:71`，commit `9252ecf`：有值得知道的產出就必須用 `buzz messages send` 發布，否則是靜默失敗）。本機 clone 是淺層歷史，查不出這一行從哪個版本開始有。
- 只靠提示詞不保證有效。#2698 的回報：同一份提示詞，較強的模型會送、Sonnet 級模型不會；2026-08-23 有人回報提示詞加上專用回覆工具仍不穩定；2026-08-28 有人回報在提示詞尾端加強制語句後穩定（單一使用者、單一模型）；2026-09-30 仍有人在桌面版用 Sonnet 級模型重現（連續三輪沒有任何工具呼叫）。所以提示詞是必要條件，4.8.2 的 watchdog 才是保底。
- 換模型前先在測試頻道 @ 它三次，確認三次都有訊息進頻道，再放進正式頻道。

#### 4.8.4 上游修正狀態（2026-11-16 以 GitHub API 查）

| 項目 | 狀態 | 備註 |
| --- | --- | --- |
| issue [#2698](https://github.com/block/buzz/issues/2698)（回覆交付是隱含約定） | 開啟，38 則留言，最後更新 2026-09-30 | 最後一則是 2026-09-30 的重現回報 |
| issue [#2459](https://github.com/block/buzz/issues/2459)（CLI 寫入失敗時回覆遺失） | 開啟，7 則留言，最後更新 2026-08-28 | |
| issue [#2265](https://github.com/block/buzz/issues/2265)（預設模型沒額度時靜默失敗） | 開啟，2 則留言，最後更新 2026-08-03 | |
| issue [#2388](https://github.com/block/buzz/issues/2388)（Windows Support 總表） | 開啟，8 則留言，最後更新 2026-09-28 | 維護團隊自述 Windows 測試硬體有限；Windows 11 常駐前先看這張表 |
| PR [#2703](https://github.com/block/buzz/pull/2703)（提示詞寫明交付約定等三項修正） | **未合併**，2026-08-15 由提交者自行關閉 | 關閉說明：一個分支混了三項不相干的修正、已與 main 衝突。**沒有對應的修正版本** |
| PR #3162、#4346、#6296（在提示詞寫明交付約定） | 開啟，未合併 | 最後更新都是 2026-08-19 |
| PR #3883（沒送訊息時由 harness 代送純文字回覆） | 開啟，未合併 | |
| PR #5673、#6810（harness 保證送出最終回覆） | 關閉，未合併 | |

結論：

- 到 2026-11-16，上游**沒有合併任何「由 harness 保證送達」或「沒送達時發出警告」的修正**；最新桌面版是 `desktop-v0.5.30`（2026-11-14 UTC 發布）。本機 `SanHsien/buzz`（`9252ecf`）的 `crates/buzz-acp/src` 也查不到這類守衛（`git grep -E "saw_agent_text|unpublished|reply_guard|sent_this_turn"` 無結果）。
- 已經在程式碼裡的只有提示詞層的規定（4.8.3）。它是不是經由上列 PR 以外的提交進來的、從哪一版開始，未查證。
- `buzz-acp` 現在有 `post_failure_notice`（`pool.rs:5508`，呼叫點 `lib.rs:5226`），在一批事件被放棄時往頻道貼一則失敗通知。它處理的是回合失敗，不是「回合成功但沒送訊息」；4.1 表格最後一列寫的「沒有找到自動廣播」是 commit `9e8c9fc` 當時的 grep 結果，在 `9252ecf` 已不完全成立。這個通知在額度錯誤時會不會出現，未實測。
- 所以在上游修好之前，4.8.2 的 watchdog 規則與 4.8.3 的提示詞都要自己做。之後重查上游時，以 #2698 是否關閉、以及關閉它的 PR 為準。

## 5. 未驗證與限制

- 沒有在任何 NAS 或本機實際啟動 Buzz；compose 步驟、區域網 `ws://` 設定、NAS Docker 版本與 image 架構都是讀文件的推論。
- `[channel.UUID]` 被忽略的行為是依 serde 預設的推論，未實測。
- Buzz 是否會把 ACP 終端錯誤自動貼到頻道：僅 grep 過 `buzz-acp`，未窮盡閱讀。
- 客戶端如何顯示非標準的 presence 字串、`buzz-cli` 的發訊息介面、44200 用量事件的實際內容：未查。
- 4.8 節：`NODELIVERY` 規則沒有實作也沒有實測；kind 44200 事件能不能當回合結束訊號、各 harness 是否都會發，未驗證。上游 issue 與 PR 狀態是 2026-11-16 的快照；留言內容只讀了 #2698 最後 8 則與 #2703 的 2 則，其餘依筆記第 0 節。
- 第 4 節整個協議是新設計；所有門檻值是起始建議，沒有實測依據。
- 模型名稱、價格、額度不在本文，見 [`docs/model-burn-rate-routing-matrix.md`](model-burn-rate-routing-matrix.md)（該文自己的查證日期為準）。
