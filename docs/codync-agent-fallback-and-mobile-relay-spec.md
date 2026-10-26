# Codync 解析：ACP 橋接、Agent 容錯降級與 E2EE 遠端審批規格

> 對應任務：`T-20261026-20`｜來源筆記：[`notes/2026-10-26-codync-open-source-agent-relay-fallback.md`](../notes/2026-10-26-codync-open-source-agent-relay-fallback.md)
> 查證基準：[`leepokai/Codync`](https://github.com/leepokai/Codync) `main` @ `21de561`（2026-10-25 19:04 UTC），Apache-2.0（程式碼；名稱、Logo、Codync Cloud relay 另有商標限制）。查證日期 2026-10-26。
> 方法：**只讀公開 GitHub 內容（WebFetch 與 `gh api` 讀取檔案文字），沒有 clone、安裝或執行 Codync**（來源未審查，維護者規則不執行來源不明的 repo）。所有「行為」都是讀文件與原始碼所得，未實測。
> 與既有機制的關係：`agent-relay` 已有限流改派（`T-20261026-21`，見第 4 節對照），本文**不重做**，只列 Codync 多出來、值得補的部分。

---

## 0. 筆記與原始碼不一致之處（先更正）

| 筆記的說法 | 查證結果 | 出處 |
|---|---|---|
| 降級到「Gemini 2.5 Flash 或 GPT-4o」等第二順位**模型** | Codync 的降級鏈是**Agent 鏈**（Claude Code → Codex → Gemini CLI），不是模型鏈；同一 agent 內的模型 fallback 留給 agent 自己（如 Claude Code 的 `fallbackModel`）。每個 bot 最多 3 個 fallback，每個 agent 在一個 turn 內最多試一次 | `docs/features/agent-fallback.md`（開頭、「The chain」）；`host/src/agent/fallback/mod.rs:20`（`MAX_FALLBACKS = 3`） |
| 「xAI Grok Bot、OpenAI Dots、Meta Muse 的開源平替」 | README 原文只寫 "open-source Grok Bot alternative"、"a Muse and Dots alternative"，**沒有**寫出三者的公司；公司歸屬未查證 | 倉庫 README（WebFetch，2026-10-26） |
| 「Rate Limit 時無縫切換」暗示一般 429 即切 | 用盡額度（usage limit）與暫時性 429 分開處理：額度用盡休息到重置時間，暫時性失敗才 1/5/25/60 分鐘退避 | `host/src/agent/fallback/rest.rs:11-24`、`reason.rs:75-99` |
| 「額度告警時將上下文切換」 | 不是預判額度，而是**只在 agent 回傳錯誤後**才動作；因為各 agent 自己會先重試（Claude Code 最多 10 次、Codex 4 次請求 5 次串流），Codync 不會再問同一個 agent | `docs/features/agent-fallback.md`「What other projects taught」；`reason.rs:1-3` |
| 「E2EE 經 Cloudflare Worker / Node private-relay」 | 屬實（`cloud/`、`private-relay/` 目錄存在），但 **webhook 不是 E2EE**：文件寫明 webhook 內容在 Cloudflare 以 HTTPS 解開，雲端看得到明文並存有 key | `docs/reference/remote-relay.md`「What the Relay Sees」 |

---

## 1. 設計哲學：BYOA / BYOS 與商業工具的差異

README 原文要點（WebFetch，2026-10-26）：

- BYOA：在**你自己的電腦**上跑 `codync-host`，「Bots run on the Claude, ChatGPT or other plan your agents are already signed in with」。
- BYOS：「Codync never calls a provider's API with your login」——它啟動已登入的 agent CLI（經 ACP），不拿你的帳號去打供應商 API；免費、無付費層。
- 支援 Claude Code、Codex、Cursor、Gemini、Copilot、OpenCode、Pi、Grok Build、Hermes Agent，另可由 ACP registry 補約 40 款。
- 網路：同網段或 Tailscale 直連，否則經 Cloudflare relay（只轉發密文）。

與商業工具的比較：筆記說商業工具有「二次收費、廠商鎖定、經手程式碼」三大缺陷。**這三點是筆記作者的評論，本文未去讀 Grok Bot／Dots／Muse 的條款或架構，不能當事實引用**。能從 Codync 端確認的只有：它免費、不綁單一模型、relay 只見密文（含上述 webhook 例外）。

```text
         商業遠端 Agent（筆記宣稱）                Codync（README + 原始碼）
 手機 ──▶ 廠商雲 ──▶ 廠商代呼叫模型 API     手機 ──E2EE──▶ 你的電腦 codync-host ──ACP──▶ 你已登入的 CLI
        （程式碼與憑證經廠商，未查證）                      relay 只見密文＋路由中繼資料
```

---

## 2. 系統架構與 ACP Client / 多 Agent 群聊路由

### 2.1 元件（出處：倉庫根目錄與 README 元件清單）

```text
 iPhone App / Desktop(Electron) / Terminal TUI / Android
          │  E2EE 通道（LAN 直連 或 Cloudflare relay：cloud/、private-relay/）
          ▼
 ┌──────────────────────────────  codync-host (Rust, host/)  ───────────────────────────────┐
 │  HTTP/SSE API (host/src/api)    SQLite transcripts    push (APNs relay: relay/)           │
 │  Bot actor (agent/bot/*): 佇列、turn、權限卡、fallback                                    │
 │  Fallback (agent/fallback/*): reason · rest · carry · mod(鏈)                             │
 │  ACP client (agent/acp.rs)                                                                │
 └──────────────────────────────────────┬───────────────────────────────────────────────────┘
                     stdio JSON-RPC 2.0 │ (ACP)
              ┌────────────┬────────────┴───┬───────────────┐
              ▼            ▼                ▼               ▼
         Claude Code     Codex          Gemini CLI    ...（ACP registry）
```

### 2.2 ACP Client 實作要點

- 每個 bot 啟動 agent 子行程，經 stdio 說 ACP，維持 session 載入；閒置 30 分鐘的 session 會關閉，全部閒置後 agent 行程停止；**Windows 的 agent 永不因閒置停止**，原因是沒有行程群組就分不出 dev server 與 MCP server，停止會殺整棵樹（`docs/architecture/conversation-runtime.md`「Agent processes」）。
- `session/request_permission` 由 `Actor::on_permission` 接手（`host/src/agent/bot/updates.rs:154-190`）：政策為 `Auto` 時直接選 `allow_once`，沒有再選 `allow_always`，再沒有就取第一個選項（`:157-166`）；否則在對話裡放一張卡（第 5 節）。
- 認證失敗用 ACP 錯誤碼 `-32000`（`host/src/agent/acp.rs:50`，`AUTH_REQUIRED`）。
- 每個 agent 各有自己的「停放 session」（`kv` 的 `fallback.session.<bot>.<agent>`），切換時停放、切回時續用（`docs/features/agent-fallback.md`「Carrying the turn over」）。

### 2.3 多 Agent 群聊路由（全部由 host 決定，客戶端不解析 @）

出處：`docs/features/groups-and-replies.md`、`docs/features/bot-collaboration.md`。

```text
使用者訊息進群組
   │ 首輪發言者 = 被 @ 或被回覆的成員；都沒有 → 全員
   ▼
輪次迴圈（最多 3 輪、共 10 則回覆）
   ├ 成員依序發言，每輪起點往後挪一位；忙碌中的成員不等，顯示通知後繼續
   ├ 第 2 輪起只叫「本回合被點名且尚未發言」的成員
   ├ 回覆 "(pass)" 不消耗額外輪次
   └ 某輪沒人發言 → 結束
bot 對 bot（群組外）：message_bot(botId, msg) → 立即回 {requestId, status:"queued"}
   ├ 每個 bot 一次只跑一個 turn；忙就排隊
   ├ 全 host 最多 64 則在途、同一寄件者最多 16 則
   ├ 請求鏈最多 8 次交接（只在 reply turn 累計；新的使用者 turn 重置）
   └ 群組內 message_bot 被拒絕，成員改用 @
```

@ 的解析（`groups-and-replies.md`「Mention parsing」）：全名、去空白名、首字皆可；`@all`／`@everyone` 叫全員；回覆某成員的訊息視為 @ 該成員。引用內容上限 500 bytes，以 `[Codync: this replies to your message: "…"]` 注入給 agent。

---

## 3. Fallback 狀態機與降級梯隊（Fallback Tier）演算法

### 3.1 Codync 的做法（已讀原始碼）

**錯誤分類 `Reason`（`host/src/agent/fallback/reason.rs:11-24`、`:75-99`）**——依 ACP 回傳的 JSON-RPC code、adapter 的 `errorKind`／`codexErrorInfo`、host 自己的 `Failure`：

| Reason | 判定 | 休息（`rest.rs:11-24`） |
|---|---|---|
| `UsageLimit` | `usage_limit_exceeded`；或 `rate_limit`／`billing_error` 且訊息含 12 個用量限制字樣之一（`reason.rs:43-56`）；或僅訊息符合 | 休到 agent 回報的重置時間（用量視窗 ≥99.5% 者的最晚 `resets_at`，`rest.rs:98-101`）；不明 → 60 分鐘 |
| `OutOfCredits` | `billing_error`／`account_on_hold` 無用量字樣 | 6 小時 |
| `RateLimited` / `Overloaded` | `rate_limit(_exceeded)`；`overloaded`、`server_error`… | 連續失敗 1 → 5 → 25 → 60 分鐘；距上次休息結束超過 60 分鐘則重算 |
| `SignedOut` | code `-32000`、`authentication_failed`… | 能代為登入的 agent：60 分鐘（登入成功即結束）；不能：10 分鐘 |
| `NotStarting` | 未設定／逾時／行程結束 | 5 分鐘 |
| `ModelMissing` | `model_not_found` 或 agent 拒絕該步驟模型 | 不休息（這是 bot 設定問題，略過該步直到設定改變） |

不切換的情況：使用者停止、拒絕、輸出或步數上限、routine 逾時、壓縮、未分類內部錯誤（`docs/features/agent-fallback.md`「When the bot moves on」）。**Context 滿不算切換理由——一律壓縮**（同文件「What other projects taught」）。

**休息是整台電腦共享**，鍵為 `rest.<account>`（agent 名，自訂指令則加指令雜湊前 6 bytes，`rest.rs:35-56`），存在 `kv`，host 重啟後仍在。一個 bot 發現 Claude Code 用完，所有 bot 都跳過它直到重置（`rest.rs:1-4`）。

**降級演算法（`host/src/agent/bot/fallback.rs:83-91`、`:248-313`）**

```text
turn 開始：從第 0 步（bot 自己的 agent）起，選「第一個本 turn 沒試過、且不在休息」的步驟
turn 失敗(error):
  若 使用者停止 / routine 逾時 / 壓縮中 / 非 turn   → 不處理
  reason = fallback::reason::of(error);  無 reason → 不處理（真正的失敗）
  rest.record(account, reason, now, resets_at)       ← 寫入電腦共享的休息
  tried.push(account)
  若 沒有下一步（全部試過或在休息）→ exhausted：回報每個 agent 現況；SignedOut 者的登入卡扣住這則訊息
  否則 在下一步「同一個 turn 重來」（保持 turn 編號、訊息、routine run、群組 turn）
回切：每個 turn 都從第一個「不在休息」的步驟開始 → 重置後的第一個 turn 自動回到本尊，絕不在 turn 中途切回
```

**狀態轉換圖**

```text
                 ┌──────────────────────── 重置時間到 / 該 agent 正常結束一個 turn / Switch back ───┐
                 ▼                                                                                   │
        ┌─────────────────┐  UsageLimit/OutOfCredits/RateLimited/Overloaded/SignedOut/NotStarting  ┌───────────────┐
 turn ─▶│ Running(step k) ├───────────────────────────────────────────────────────────────────────▶│ Rest(account) │
        └───┬─────────┬───┘  record(rest)；tried += k                                               └───────────────┘
            │         │ 有下一步（未試過且不在休息）
   成功/一般錯誤       ▼
            │   ┌──────────────────┐  carry：recap／catch-up／takeover
            │   │ Running(step k+1)│◀── 同一 turn 重來
            │   └─────────┬────────┘
            │             │ 沒有下一步
            ▼             ▼
        ┌────────┐   ┌───────────────────────────┐
        │  Done  │   │ Exhausted：失敗通知＋各 agent 現況；SignedOut 者的登入卡扣住訊息，登入後重送 │
        └────────┘   └───────────────────────────┘
```

**上下文攜帶（`host/src/agent/fallback/carry.rs`）**：新 session → 交接摘要（上一個 session 的最後摘要＋最近 12 則訊息＋未完成計畫＋`search_history` 書籤，`carry.rs:12`）；有舊 session → 補上離開期間的對話（最多 20 則，`:14`）；本 turn 已有 agent 失敗 → 列出誰最後停下、為何、每個失敗 agent 的工具呼叫（最多 40 筆，`bot/fallback.rs` 的 `TOOLS_LISTED`）、已送出的訊息與最後備註，並加一句 "check what's already done before you redo any step"。每次切換在對話裡寫一行（含 `agentSwitch` 通知與成本備註）。

### 3.2 與 `agent-relay` 現況對照（不重複設計）

`agent-relay` 已實作的（`C:\GitHub\agent-relay\agent_relay\dispatch.py`，`T-20261026-21` 已確認）：

| 能力 | agent-relay 現況 | 出處 |
|---|---|---|
| 限流辨識 | `RATE_LIMIT_RE` 涵蓋 `rate limit`、`429`、`usage limit`、`too many requests`、`limit reached`、`quota exceeded/exhausted`、`resource_exhausted`；暫時性另有 `TRANSIENT_RE` | `dispatch.py:74-78` |
| 只信 runtime 自報錯誤 | `failure_text` 只取 error 事件與最後幾行 stderr，工人輸出提到 `rate_limiter.py` 不誤判 | `dispatch.py:82-119`、SPEC §10 |
| 限流 → 改派 | 加入 `limited` 集合，從 advisor 路由表挑下一個未被限流且允許的 runtime；已限流者不回頭 | `dispatch.py:1164-1207` |
| 暫時性 → 原地重跑 | `time.sleep(min(30, 5*n))` 後重跑，次數 `dispatch.retries`（0～3） | `dispatch.py:1211`、SPEC §10 |
| 派工前額度門檻 | claude 讀 `agentdeck-status.json`、codex 用 `codex-reset-checker`；5 小時 ≥90% 或週 ≥95% 跳過；全擋下回 `deferred` 並寫最早重置時間 | SPEC §10 |
| 逾時殺行程 | `taskkill /T /F`（見 `docs/buzz-nostr-agent-architecture.md` 第 4 節的比較） | `dispatch.py:602-634` |

**Codync 多出、`agent-relay` 目前沒有（以讀碼判斷）的缺口，逐項評估**：

| # | 缺口 | Codync 做法 | 建議 | 優先 |
|---|---|---|---|---|
| G1 | **接力時不攜帶前一次做了什麼**：限流改派時沿用原 prompt（`build_prompt` 在迴圈外、`dispatch.py:1157`，迴圈內改派只換 `spec`），新 runtime 只能靠 worktree 的現狀自己判斷 | `carry::takeover`：列出失敗 agent 的工具呼叫、已送訊息，叮嚀「先確認哪些已做完」 | 改派時把前次 `output.<n>.log` 的摘要（最後 error、`git status`／`git diff --stat`）附在 prompt 尾端 | 高 |
| G2 | **限流只在單次 dispatch 內記憶**（`limited` 是區域變數），下一個工單仍可能先派到剛被限流的 runtime，再失敗一次才改派 | `rest.<account>` 寫入 `kv`，全機共享、重啟保留，附重置時間 | 在 store 寫 `rest/<runtime>.json`（`until`、`reason`、`failures`），選 runtime 前先讀；與既有額度檔並存，不取代 | 中 |
| G3 | **失敗原因只分 rate-limited / transient / 其他**：未登入、點數用盡、啟動失敗都落入「其他失敗不重試」 | 7 種 Reason，休息時間各不同 | 先加 `signed-out`（改派＋提示人工登入）與 `out-of-credits`（長休息），其餘維持 | 低 |
| G4 | **暫時性限流與用量上限不分**：`quota exceeded` 與 `429` 同樣立刻改派，沒有「暫時 429 先退避」；而 Codync 認為 agent 會先自行重試，錯誤回來時才動作 | 用量字樣先於一般 rate limit 判定（避免把週額度當暫時 429 重試一週，OpenCode 的教訓 #28431，見 `agent-fallback.md`） | 現行「一律改派」對 CLI 型 runtime 是合理的（CLI 本身已重試）；維持現狀即可，只需確認用量字樣不被當成 `transient` 重跑 | 不動 |

### 3.3 可直接用的最小梯隊設定（建議，未實作）

```json
{
  "dispatch": {
    "fallback_tiers": [
      {"runtime": "claude", "model": "sonnet"},
      {"runtime": "codex",  "effort": "medium"},
      {"runtime": "agy"}
    ],
    "rest_store": "state/rest",
    "takeover_note": true
  }
}
```

這只是 G1／G2 的欄位構想；`agent-relay` 現行 `advisor` 路由表已提供順序（SPEC §10 路由表），**不另建第二套路由**。實作前先在 `tests/test_advisor.py` 增加反例（例如：第二個工單在 `rest/claude.json` 未過期時不得選 claude），才寫程式。

---

## 4. ACP 橋接範例

以下是 Codync 這類 host 與一個 ACP agent 之間的一次 turn（stdio，一行一個 JSON-RPC 訊息）。欄位依 Codync 讀取的 `toolCall`／`options`／`outcome` 形狀（`updates.rs:154-190`、`:249-262`）與 Buzz `buzz-agent` 的參數型別（`crates/buzz-agent/src/wire.rs:50-96`）整理，**範例值是本文示意，非實際擷取**。

```json
→ {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{}}}
← {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":1,"agentCapabilities":{}}}
→ {"jsonrpc":"2.0","id":2,"method":"session/new","params":{"cwd":"/work/repo","mcpServers":[]}}
← {"jsonrpc":"2.0","id":2,"result":{"sessionId":"s-1"}}
→ {"jsonrpc":"2.0","id":3,"method":"session/prompt","params":{"sessionId":"s-1","prompt":[{"type":"text","text":"執行測試並修復失敗"}]}}
← {"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"s-1","update":{"sessionUpdate":"agent_message_chunk","content":{"type":"text","text":"先跑測試…"}}}}
← {"jsonrpc":"2.0","id":9,"method":"session/request_permission","params":{"sessionId":"s-1",
     "toolCall":{"toolCallId":"t-1","title":"rm -rf build","kind":"execute","rawInput":{"command":"rm -rf build"}},
     "options":[{"optionId":"allow_once","name":"Allow once","kind":"allow_once"},
                {"optionId":"reject_once","name":"Deny","kind":"reject_once"}]}}
→ {"jsonrpc":"2.0","id":9,"result":{"outcome":{"outcome":"selected","optionId":"allow_once"}}}
← {"jsonrpc":"2.0","id":3,"result":{"stopReason":"end_turn"}}
```

橋接時要注意的三個相容性事實（皆為讀碼所得）：

1. **版本分歧**：Buzz 的 `buzz-agent` 協商 `PROTOCOL_VERSION = 2`（`config.rs:3`），v2 的 `session/request_permission` 把工具資訊放在 `subject: {type:"tool_call", toolCall}`；v1 則是 `toolCall` 直接在 params 層（`wire.rs:171-214`）。Codync 的 `on_permission` 讀的是 `params["toolCall"]`（`updates.rs:155`）——**若直接把 Codync 接到 v2 agent，權限卡的標題與指令可能讀不到**（推論，未實測）。橋接層應在 `initialize` 時明確要求 v1，或兩種形狀都解。
2. **取消語意**：使用者按停止或卡片過期，回 `{"outcome":{"outcome":"cancelled"}}`（`updates.rs:249-262`），不要不回應。
3. **選項不要寫死 optionId**：Buzz 註解特別說 `buzz-acp` 以 `kind == "allow_once"` 選擇而非 `optionId`（`wire.rs:154-160`）；Codync 的自動政策同樣以 `kind` 找。

---

## 5. 危險指令審批卡（Approval Card）契約

### 5.1 Codync 實際的卡片資料（`updates.rs:179-190`、`:206-213`）

```json
{
  "title": "rm -rf build",
  "toolKind": "execute",
  "command": "rm -rf build",
  "detail": "（工具輸出或說明）",
  "diffs": [],
  "cwd": "/work/repo",
  "options": [{"optionId":"allow_once","name":"Allow once","kind":"allow_once"},
              {"optionId":"reject_once","name":"Deny","kind":"reject_once"}],
  "status": "pending",
  "selected": null
}
```

狀態：`pending` → `answered`（選了選項）／`cancelled`（回 cancelled）／`expired`（等待方已放棄，如工具逾時，`updates.rs:249-262` 與 `expire_abandoned`）。卡片出現時 bot 狀態改為 `NeedsInput`，並發推播「<bot> needs you」（`updates.rs:218-240`）。Codync 自己的工具（例如團隊管理）用另一種 `Answer::Codync` 通道，只有 `allow`／`deny` 兩個選項（`ask_approval`，`:200-213`）。

### 5.2 本專案建議契約（由上面整理，三段審批）

| 欄位 | 必填 | 規則 |
|---|---|---|
| `card_id` | 是 | 對應 ACP 請求的 JSON-RPC `id`，回覆必須原樣帶回 |
| `session_id`、`tool_call_id` | 是 | 防跨 session 誤答 |
| `title`、`command`、`cwd` | 是 | 讓人在手機上不用展開就看得懂要做什麼；`command` 為空時 `title` 必須是可讀的動作 |
| `diffs`／`detail` | 否 | 檔案變更時附 |
| `options[]` | 是 | 每項 `optionId`、`name`、`kind ∈ {allow_once, allow_always, reject_once, reject_always}`；**回覆以 `kind` 判斷，不寫死 `optionId`** |
| `expires_at` | 是 | 逾時視為 `cancelled`，不可預設放行。Buzz 的做法可參考：permission ask 有單一絕對期限，預設 330 秒，刻意比客戶端 300 秒自動拒絕長，讓答案或自動拒絕先到（`crates/buzz-agent/src/config.rs:587-592` 註解與 `:740-742`） |
| `status` | 是 | `pending/answered/cancelled/expired` |

三段審批對應：Allow once = `allow_once`；Always allow = `allow_always`（agent 若不提供就不顯示，不自己發明）；Deny = `reject_once`。

**預設值規則（本文建議）**：政策為「無人值守」時，只對白名單內的 `kind`（如純讀取）自動 `allow_once`；Codync 的 `Auto` 政策是對所有請求自動允許（`updates.rs:157-166`），Buzz 的 `buzz-acp` 也自動 `allow_once`（`crates/buzz-acp/src/acp.rs:1265`）。這兩者都沒有人工閘門，**不建議照搬到會碰 `rm`、`git push` 的場景**。

---

## 6. 端到端加密通道驗證標準

Codync 的設計規格是公開的（`docs/reference/remote-relay.md`），並附測試向量檔 `docs/reference/fixtures/remote-relay-vectors.json` 與 `remote-relay-vectors.py`（檔案存在於倉庫樹；**本文未讀其內容**）。下表整理規格重點，作為「驗證一個實作是否符合」的檢查清單。

| 項目 | 規格（`remote-relay.md`） | 驗證方式 |
|---|---|---|
| 金鑰交換 | 每次連線簽名的暫時 X25519；device 的 `hello` 帶 `ekD` 與 32 bytes nonce，用 Ed25519 簽 `"codync/hs1/v1"`＋電腦 ID 雜湊＋裝置金鑰＋`ekD`＋nonce；host 回 `welcome`（`ekH`＋對 `TH = SHA-256("codync/hs2/v1"‖…)` 的簽章） | 重放官方向量，逐步比對 `TH` 與雙向金鑰 |
| 金鑰導出 | `ss = X25519(...)`，全 0 結果拒絕；HKDF-SHA256（salt = `TH`）導出 `codync/d2h/v1`、`codync/h2d/v1` 兩把 32 bytes 金鑰 | 負向測試：低階點必須被拒 |
| 加密 | ChaCha20-Poly1305；nonce = 4 bytes 零＋big-endian u64 計數器（每方向從 0）；AAD = `"codync/frame/v1"`＋計數器 | 竄改任一 bit、錯誤計數器 → 解密失敗 |
| 防重放／亂序 | 接收端要求計數器完全等於預期，否則以 `4002` 關閉 | 重送舊 frame、跳號 → 必須被關 |
| 分塊與上限 | 明文 = 1 byte 旗標＋至多 256 KiB；重組上限 device→host 1 MiB、host→device 16 MiB，超過 `4013` | 邊界值 ±1 byte |
| 重新交換金鑰 | 計數器達 2^32 或 24 小時 → `4011` | 時間／計數器注入 |
| 信任錨 | device 釘住 host 的 Ed25519 簽章金鑰，電腦 ID 由該金鑰導出；配對 QR 帶 `sk`／`bk`，一次性 16 bytes 碼 10 分鐘有效，配對 socket 只接受 `pair` | 錯碼、過期碼、替換 host 金鑰 → 必須失敗 |
| 帳號存取 SAS | commit-then-reveal 六位數碼：`uint32_be(SHA-256("codync/sas/v2"‖…)[0..4]) mod 1,000,000`；被攻破的雲端猜中機率約 10⁻⁶／次 | 蒙地卡羅不必要；檢查 commit 先於 reveal 的順序即可 |
| 離線信箱 | 每則訊息新的暫時金鑰 `epk`；nonce 全 0（**僅在 `epk` 每次都新時安全，重用是 MUST-NOT**）；blob = `epk(32)‖sig(64)‖ct`；host 檢查裝置有效、簽章、解密、`clientNonce`、時間戳 ±25 小時、只允許 `send`；TTL ≤24h、blob ≤64 KiB、每裝置 50／每電腦 500／總計 8 MiB | 同一 `epk` 重用必須被實作端禁止（單元測試） |
| relay 可見範圍 | 可見：密文 frame、電腦 ID、裝置金鑰、連線 ID、在線狀態、時間／大小／頻率、信箱識別。**例外**：webhook 在 Cloudflare 解開；推播只含通用文字，標題與內文以裝置推播金鑰封裝 | 抓 relay 端封包，確認無明文欄位（webhook 除外） |
| 雲端被攻破 | 無法新增可解密的裝置（授權新增需 host 本機操作，ACL 由 host 簽章）；雲端狀態只能縮短授權、不能新增；撤銷由 Durable Object 與 host 各執行一次 | 以惡意 relay 試圖新增 grant → 必須失敗 |

殘餘風險（原文）：使用者必須真的比對 SAS 碼；直連 `ws://` 時內容加密但連線中繼資料在區網可見；複製 `identity.json` 會造成同一電腦身分的競爭連線。

**對本專案的意義**：若 `agent-relay` 日後要跨機器（`T-20261019-01/02` 的方向），不要自創密碼學；至少複用「釘住 host 金鑰＋簽名暫時 ECDH＋每方向計數器 nonce」這個結構，並以官方向量做回歸。本文**沒有**評估這套實作本身的安全性（未審計、未實測），只整理它的規格。

---

## 7. 採用建議（精簡）

1. **做**：G1（改派時攜帶前次摘要）與 G2（跨工單的 runtime 休息記憶），各自先補 `tests/test_advisor.py` 反例再實作；屬 `agent-relay` 另開任務。
2. **參考不採用**：iOS／Android App、Cloudflare relay（個人工作站不需要，筆記「不採納」一節已同意）。
3. **暫不做**：把 Codync 本體接進 `agent-relay`——`T-20261026-22` 已因「不執行未審查來源」關閉；若日後要實測，先走 `skill-vetting`。

---

## 8. 查證來源與未查證項目

已讀（2026-10-26）：

- 倉庫首頁與 README：<https://github.com/leepokai/Codync>（858 stars、103 forks、Apache-2.0；`pushed_at` 2026-10-25 23:28 UTC，`gh api repos/leepokai/Codync`）
- `docs/features/agent-fallback.md`、`docs/features/groups-and-replies.md`、`docs/features/bot-collaboration.md`、`docs/reference/remote-relay.md`、`docs/architecture/conversation-runtime.md`（片段）
- `host/src/agent/fallback/{mod,reason,rest,carry}.rs`、`host/src/agent/bot/fallback.rs`、`host/src/agent/bot/updates.rs`、`host/src/agent/acp.rs`（以 `gh api` 取文字讀取，未存入專案目錄、未建置）
- 本機：`C:\GitHub\agent-relay\agent_relay\dispatch.py`、`SPEC.md` §10；`C:\GitHub\buzz\crates\buzz-agent\src\{wire,config}.rs`

未查證／未實測：

- 沒有執行 Codync，上述行為均為讀文件與原始碼；
- 沒有讀 `remote-relay-vectors.*` 與 `docs/reference/compatibility.md`；
- Grok Bot／Dots／Muse 的廠商與商業條款；
- Codync 自身的安全審計狀態（`SECURITY.md` 未讀）；
- 筆記所稱「Sol 6.1 額度耗盡實測」為筆記引述，本文未驗證。
