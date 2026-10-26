# Buzz 私有化 NAS 常駐部署、預算路由與額度心跳協議規格

> 對應任務：`T-20261026-27`，並收攏已關閉的 `T-20261026-31`（內容重複，合併進本文）。來源筆記：[`notes/2026-10-26-block-buzz-nostr-agent-workspace.md`](../notes/2026-10-26-block-buzz-nostr-agent-workspace.md)。
> 查證基準：本機 `C:\GitHub\buzz`（`SanHsien/buzz`，fork 自 [`block/buzz`](https://github.com/block/buzz)）commit `9e8c9fc`（2026-10-23）。查證日期 2026-10-26。下文「檔案:行號」都指這個 commit。
> **範圍與限制**：這是規格文件。部署指令與設定範例讀自原始碼與 repo 內的 compose 檔，**沒有在 NAS 或本機實際部署過 Buzz**（本機 Windows 缺 MSVC 連結器，連編譯都未成功，見 [`docs/evidence/2026-10-26-buzz-windows-build.md`](evidence/2026-10-26-buzz-windows-build.md)）。第 4 節的心跳協議是**新設計，尚未實作**，數值是起始建議，不是實測。

## 1. 要解的問題

多個 AI Agent 進駐同一個聊天室協作時，最難查的失敗是「已讀不回」：Agent 的額度用完了，但行程還活著，使用者在頻道裡一直等。本文處理三件事：Buzz 在 NAS 怎麼常駐、頻道與 Agent 怎麼切、額度耗盡時怎麼讓頻道知道。

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

模型怎麼選、各模型耗額多少，**不在本文重複**，以 [`docs/model-burn-rate-routing-matrix.md`](model-burn-rate-routing-matrix.md) 為準（含查證日期與【作者實測】／【官方】標記；數字會變動，使用前先看該文第 1、8 節）。本文只定義「頻道角色 → 模型層級」的對應方式，並用 `BUZZ_ACP_MODEL` 落地：

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
3. **watchdog 不看內容、不呼叫 LLM**：只看事件的作者、時間、`p` 標籤與 kind；它自己的金鑰也要先 `add-member`，並只被允許在 `#ops-alerts` 與被監看頻道發 `[QHP]` 訊息。
4. **交接不自動搶任務**：`handoff=<agent>` 只是在頻道 @ 該 Agent 並貼出原訊息連結，由接手 Agent 依自己的 `RESPOND_TO` 規則決定處不處理；跨頻道權限邊界（3.1）不會因交接而放寬。
5. **假警報與漏報的取捨**：寧可多一則 `NORESP`（人類看一眼就知道），也不要沉默。`NORESP` 本身不重複發送，同一則訊息只報一次。

### 4.7 實作路徑與驗收（尚未做）

最小可行版本不需要改 Buzz 原始碼：

1. `watchdog.py`（標準庫，用 `buzz-cli` 或 WebSocket 客戶端讀頻道；細節要先讀 `buzz-cli` 的指令，本文未讀）。
2. Agent 端的 `EXIT`：在啟動 `buzz-acp` 的包裝腳本裡監看底層 CLI 的終端錯誤輸出，符合 429／額度字樣時呼叫 `buzz-cli` 發訊息。這是**以字串比對判斷**，容易隨 CLI 版本失效，應該以各 CLI 實際的錯誤輸出樣本做測試，不要憑猜測寫規則。
3. 驗收（待做）：在測試頻道用一個故意回 429 的假 LLM 端點，確認 (a) 重試用盡後頻道出現 `EXIT` 且 presence 變 `away`；(b) 殺掉 Agent 行程後 `ack_timeout` 內出現 `NORESP presence=missing`；(c) 單次 429 後重試成功時**不**出現 `EXIT`。三項都要有反例才算數。

## 5. 未驗證與限制

- 沒有在任何 NAS 或本機實際啟動 Buzz；compose 步驟、區域網 `ws://` 設定、NAS Docker 版本與 image 架構都是讀文件的推論。
- `[channel.UUID]` 被忽略的行為是依 serde 預設的推論，未實測。
- Buzz 是否會把 ACP 終端錯誤自動貼到頻道：僅 grep 過 `buzz-acp`，未窮盡閱讀。
- 客戶端如何顯示非標準的 presence 字串、`buzz-cli` 的發訊息介面、44200 用量事件的實際內容：未查。
- 第 4 節整個協議是新設計；所有門檻值是起始建議，沒有實測依據。
- 模型名稱、價格、額度不在本文，見 [`docs/model-burn-rate-routing-matrix.md`](model-burn-rate-routing-matrix.md)（該文自己的查證日期為準）。
