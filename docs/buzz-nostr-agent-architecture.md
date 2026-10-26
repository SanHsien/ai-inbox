# Block Buzz 架構解析與 Nostr + ACP/MCP 代理人協同設計指引

> 對應任務：`T-20261026-08`｜來源筆記：[`notes/2026-10-26-block-buzz-nostr-agent-workspace.md`](../notes/2026-10-26-block-buzz-nostr-agent-workspace.md)
> 查證基準：本機 `C:\GitHub\buzz`（`SanHsien/buzz`，fork 自 [`block/buzz`](https://github.com/block/buzz)，Apache-2.0），commit `9e8c9fc`（2026-10-23）。
> 查證日期：2026-10-26。下文「檔案:行號」都指這個 commit；上游之後會變動，行號僅供對照。
> 範圍：只讀原始碼與文件做解析；**未在本機建置或執行 Buzz**（編譯與 Job Object 實測是 `T-20261026-09` 的範圍）。

---

## 0. 先釐清：筆記裡與原始碼不一致的三點

| 筆記／常見說法 | 原始碼實際 | 出處 |
|---|---|---|
| `buzz-agent` 支援「多達 8 個並行 Session」 | `max_sessions` 預設 `usize::MAX`（不設限）；`8` 是 `max_parallel_tools`（單輪並行工具數） | `crates/buzz-agent/src/config.rs:729`、`:738` |
| 「Hash-Chain 審計日誌由 Nostr 金鑰簽章」 | 鏈是 **relay 端 Postgres 的 SHA-256 雜湊鏈**；Nostr 簽章保護的是**事件**（id/sig），鏈本身沒有簽章，防竄改靠「雜湊鏈 + 寫入單一入口」 | `crates/buzz-audit/src/hash.rs:43-67`、`ARCHITECTURE.md:598-612` |
| `git-sign-nostr` 可給任何 Agent 簽 commit | 模組註解寫明 **Unix-only**（依賴 `--status-fd` 檔案描述元傳遞），Windows 原生不能直接用 | `crates/git-sign-nostr/src/lib.rs:6` |

---

## 1. 系統拓撲

```text
 人類 (Desktop/Web)     AI 代理人                     Git / 外部系統
        │                  │                              │
        │ WS(NIP-01)       │ buzz-acp (WS + NIP-42)       │ NIP-98 HTTP 簽名
        ▼                  ▼                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ buzz-relay：Axum WS + REST；NIP-42 挑戰 → AUTH；EVENT → 驗簽       │
│  → 依 kind 分派 → 寫 Postgres → Redis 扇出 → (部分) buzz-audit    │
└───────┬────────────────────┬───────────────────┬─────────────────┘
        ▼                    ▼                   ▼
   Postgres              Redis pub/sub       S3/MinIO(Blossom)
   events 表 + GIN       presence/typing     媒體
   audit_log 雜湊鏈
```

出處：`ARCHITECTURE.md:72-125`（系統架構）、`:217-262`（連線生命週期）。連線順序：租戶綁定（由 host 決定 community）→ 連線額度 semaphore → relay 送 `["AUTH", challenge]` → 客戶端回簽名事件 → 進入 recv/send/heartbeat 三個迴圈（`ARCHITECTURE.md:217-262`）。

---

## 2. Nostr Relay 設計哲學、Kind 系統、Postgres FTS

### 2.1 設計哲學（原文與程式能對上的部分）

1. **單一 relay 為真實來源，非 P2P gossip**：URL/網域即工作區（`ARCHITECTURE.md:221-229`）。
2. **所有動作都是簽名事件**：`id = sha256(正規序列化)`，`sig = Schnorr(id)`（`ARCHITECTURE.md:154-166`）。連 PR 核准、成員異動都是事件。
3. **kind 是唯一分派開關**：新功能 = 新 kind 數字，舊客戶端忽略未知 kind（`ARCHITECTURE.md:168`）。

### 2.2 Kind 系統

`crates/buzz-core/src/kind.rs` 是權威註冊表（檔頭註解 `:1-3`），本 commit 有 135 個 `pub const KIND_*`；`ALL_KINDS` 陣列在 `:689`。範圍語意（`ARCHITECTURE.md:169-177`）：

| 範圍 | 語意 | 與 Agent 相關的例子（kind.rs 行號） |
|---|---|---|
| 0–9999 | 標準 Nostr | `KIND_STREAM_MESSAGE=9`（`:527`）、`KIND_REACTION=7`（`:58`） |
| 10000–19999 | 可取代 | `KIND_AGENT_PROFILE=10100`（`:90`）：Agent 中繼資料與 owner 參照 |
| 20000–29999 | 短暫（不落庫、不入審計） | `KIND_AGENT_PRESENCE=20003`（`:515`）、`KIND_AUTH=22242`（`:77`）、`KIND_AGENT_OBSERVER_FRAME=24200`（`:517`） |
| 30000–39999 | 參數化可取代 | `KIND_AGENT_ENGRAM=30174`（`:97`，Agent 加密記憶）、`KIND_MANAGED_AGENT=30177`（`:334`） |
| 40000–49999 | Buzz 自訂 | `KIND_STREAM_MESSAGE_V2=40002`（`:529`） |

注意：`ARCHITECTURE.md:179-195` 的「selected kinds」表列了 `43001 KIND_JOB_REQUEST` 等；本人未在 `kind.rs` 的前 100 行常數中逐一核對每個數字，**引用 kind 號碼請以 `kind.rs` 為準，不要抄 ARCHITECTURE 的表**。

### 2.3 Postgres FTS 結構

```text
events 表
  content ──(GENERATED ALWAYS … STORED)──▶ search_tsv = to_tsvector('simple', content)
                                            └─ 例外：kind IN (1059,30300,30622,44100,44101) → NULL
  索引：GIN (search_tsv)     查詢：WHERE community_id = $ctx AND search_tsv @@ websearch_to_tsquery('simple', …)
  排序：ts_rank_cd 相關度，同分新到舊
```

- 生成欄位定義：`migrations/0001_initial_schema.sql:223-224`；GIN 索引：`:278`；`CASE … NULL::tsvector` 讓私密 kind（gift wrap、提醒、DM 可見性等）在儲存層就搜不到（NULL 不匹配 `@@`）。`ARCHITECTURE.md:951-962` 的文字只列 `1059, 30300, 30622`，**migration 實際多了 `44100, 44101`**（`0001:223`），以 SQL 為準。
- 因為是 `GENERATED ALWAYS`，「寫入列 = 更新索引」，沒有獨立索引器或重建佇列，客戶端也無法偽造與 content 不一致的 tsvector（`crates/buzz-search/src/lib.rs:5-11`）。
- 查詢端 `buzz-search` 每個 `SearchQuery` 都帶 `CommunityId`，SQL 第一個條件固定 `community_id = $ctx`（`lib.rs:14-20`）；用 `websearch_to_tsquery('simple', …)`（`query.rs:156`）與 `ts_rank_cd`（`:259`）。搜尋命中後仍會回頭用 `buzz-db` 重抓並做權限檢查，**搜尋不是存取邊界**（`lib.rs:12-14`）。
- 限制（推論）：`'simple'` 設定不做詞幹與中文斷詞，繁中內容的檢索品質需自行評估；本文未實測。

---

## 3. ACP 與 MCP 的雙協議解耦管線

```text
 Buzz Relay ──WS/NIP-42──▶ buzz-acp ──stdio ACP(JSON-RPC)──▶ buzz-agent ──stdio MCP──▶ buzz-dev-mcp
   (事件、@mention)         ACP 客戶端 + agent 池               ACP 伺服器 + LLM 迴圈          shell/檔案編輯/目錄
                            (1–32 個子行程)                     (多 session)                  (Job Object / killpg)
```

- **buzz-acp = ACP 客戶端**：用 WebSocket 連 relay，把頻道內 @mention 排隊，**每頻道同時最多一個 in-flight prompt**，批次後以 `session/prompt` 送給 agent 子行程；池大小 1–32，子行程崩潰會重生（`ARCHITECTURE.md:769-797`）。agent 發來 `session/request_permission` 時，buzz-acp 目前**自動批准 `allow_once`**（`crates/buzz-acp/src/acp.rs:1265`、`:2005`）——代表「核准卡」在此路徑沒有人工閘門。
- **buzz-agent = ACP 伺服器 + LLM 迴圈**：`handle_request` 路由 `initialize`、`session/new`、`session/prompt`、`session/set_model`、`session/cancel` 與一個 goose 相容擴充 `_goose/unstable/session/steer`（`crates/buzz-agent/src/lib.rs:311-330`）。`initialize` 協商的 `protocolVersion` 存為連線級狀態，之後 `session/request_permission` 的線上格式由它決定（`lib.rs:62-69`）。
- **MCP 在 buzz-agent 內**：`spawn_one` 以 `env_clear()` 啟動 MCP 子行程，只放行白名單環境變數（Windows 另有一份）、用 `TokioChildProcess` 做 stdio 傳輸、`serve` 完成 initialize 後 `list_all_tools`，兩步各有 timeout（`crates/buzz-agent/src/mcp.rs:730-800`）。重啟策略：最多 3 次、基礎 500ms、上限 30s（`config.rs:725-727`）。
- **Context 滿了的自我交接**：`handoff.rs` 把歷史摘要後重置；每輪最多 10 次（`BUZZ_AGENT_MAX_HANDOFFS`，`config.rs:737`），預設 context 上限 200,000 tokens（`:736`）。

### 3.1 協議序列圖（一次完整的任務回合）

```text
人類      relay        buzz-acp          buzz-agent             LLM       buzz-dev-mcp
 │ @agent  │              │                  │                   │             │
 ├────────▶│ EVENT kind 9 │                  │                   │             │
 │         ├─────────────▶│ (排隊/批次)       │                   │             │
 │         │              ├─ initialize ────▶│ 協商 protocolVersion              │
 │         │              ├─ session/new ───▶│ ── 啟動 MCP ───────────────────▶│ initialize+tools/list
 │         │              ├─ session/prompt ▶│── 請求 ──────────▶│             │
 │         │              │                  │◀─ tool_call ──────┤             │
 │         │              │◀ session/request_permission           │             │
 │         │              ├─ allow_once ────▶│── tools/call(shell) ──────────▶│ 派生 bash，進 KillGroup
 │         │              │◀ session/update (串流) ◀── 結果 ─────────────────────┤
 │         │◀─ EVENT(Agent 簽名回覆) ─────────┤                   │             │
 │◀────────┤              │                  │                   │             │
```

（`session/update`、`request_permission` 見 `crates/buzz-agent/src/wire.rs:216-240`；`tools/call` 為 MCP 標準方法，由 `rmcp` 套件承載。）

### 3.2 為什麼這種解耦有用

1. **換 agent 不動工具、換工具不動 agent**：ACP 管「人／頻道 ↔ agent」，MCP 管「agent ↔ 工具」；`buzz-acp` 可接 goose/codex/claude 等不同 ACP agent（`ARCHITECTURE.md:773`）。
2. **危險動作集中在 MCP 子行程**：逾時、取消、輸出截斷（`CAPTURE_CAP`）都在 `buzz-dev-mcp/src/shell.rs`，agent 本體不碰 shell。

---

## 4. Windows Job Object API 實作解析

### 4.1 要解決的問題

`shell.rs:678-687` 的註解說得很直接：在 Windows 對 bash 做一次 `TerminateProcess`，會留下 MSYS 派生的孫行程（例如 `sleep`）；它們握著 stdout/stderr 管線，導致回收讀取一直卡到孫行程自己結束。Unix 靠 `process_group(0)` + `killpg`（`shell.rs:689-732`），Windows 沒有行程群組，所以改用 Job Object。

### 4.2 呼叫序列（`crates/buzz-dev-mcp/src/shell.rs`）

```text
spawn bash ──▶ KillGroup::new(&child)  (:194 呼叫, :755 定義)
                │ 1. CreateJobObjectW(NULL, NULL)                 :770  匿名 job，預設安全描述元
                │ 2. info.BasicLimitInformation.LimitFlags
                │      = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE       :777
                │ 3. SetInformationJobObject(job,
                │      JobObjectExtendedLimitInformation, &info,
                │      sizeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION)) :778-783
                │ 4. AssignProcessToJobObject(job, child.raw_handle()) :785
                ▼
 tokio::select! { cancel | timeout | child.wait }               :212-272
   ├ 取消 → kill_immediate() → terminate()                      :218 → :803
   ├ 逾時 → kill_graceful().await（Windows 與 immediate 相同）  :243 → :797
   └ 正常結束 → 仍呼叫 kill_graceful() 清殘留背景行程          :272-274
terminate():  TerminateJobObject(job, 137)                      :810  137 = 128+9，對齊 Unix SIGKILL
Drop:         CloseHandle(job)                                   :825-833 → 觸發 KILL_ON_JOB_CLOSE，最後防線
disarm():     Windows 為 no-op                                   :818
```

重點設計：

- **子行程自動繼承 job**：行程進 job 後，用 `CreateProcess` 建立的子行程預設也屬於該 job（Microsoft Learn〈Job Objects〉「Managing Processes in Jobs」）。所以 bash 之後派生的 MSYS 孫行程都在 job 內。
- **`KILL_ON_JOB_CLOSE` 同時是 Drop 保險**：job handle 必須活得比子行程久（`shell.rs:773-776` 註解），最後一個 handle 關閉時 Windows 會終止 job 內所有行程（同一份 MS 文件「Managing Job Objects」）。
- **Windows 沒有 SIGTERM 對應物**：`kill_graceful` 直接等於 `terminate`（`:797-801`），Unix 則 SIGTERM → 等 200ms → SIGKILL（`:710-718`）。
- **`unsafe impl Send/Sync`**（`:745-750`）：raw `HANDLE` 預設非 Send，但 job handle 是核心物件參照、非執行緒綁定；註解說明了安全理由。
- **依賴最小化**：只用 `windows-sys 0.61` 的 `Win32_Foundation / Security / System_JobObjects / Registry / System_Threading` 五個 feature（`crates/buzz-dev-mcp/Cargo.toml:52`，理由註解 `:46-51`）。
- **逾時語意**：預設 120,000ms、上限 1,200,000ms（`shell.rs:16`、`:130-132`、測試 `:1002-1008`）；逾時回傳 `exit_code=124`（`:297`）。回歸測試 `timeout_fires`（`:1032-1056`）用 `sleep 5` 逾時 150ms，若孫行程洩漏，測試會卡約 5 秒而不是 16 分鐘。

### 4.3 第二種用法：桌面端管理整個 agent 樹（`desktop/src-tauri/src/managed_agents/process_lifecycle.rs`）

| 函式 | 行號 | 作法 | 差異 |
|---|---|---|---|
| `create_job_for_child(pid)` | `:60-103` | `OpenProcess(PROCESS_SET_QUOTA \| PROCESS_TERMINATE)` → `AssignProcessToJobObject`；任一步失敗回 `None`，呼叫端退回 `Child::kill()` | 依 PID 開 handle，不依賴 `Child` 物件 |
| `resume_process(pid)` | `:118` | 用 ToolHelp 執行緒快照找出該 pid 的執行緒逐一 `ResumeThread` | 配合 `CREATE_SUSPENDED` |
| `taskkill_tree(pid)` | `:161` | 重啟後只剩 PID、沒有 job handle 時用 `taskkill /T` | 退而求其次 |

`create_job_for_child` 的 doc（`:44-57`）講了**競態**：一般 spawn 後再指派，要賭「子行程在被指派前還沒派生孫行程」；探測指令可能「背景化孫行程後立刻退出」，所以改用 `CREATE_SUSPENDED` → 指派 → `resume_process`，從結構上關閉競態。

### 4.4 這份實作的弱點（讀碼推論，未實測）

1. `shell.rs` 的路徑**沒有用 `CREATE_SUSPENDED`**：`cmd.spawn()` 在 `:179`，`KillGroup::new` 在 `:194`，中間有空窗；bash 若在這段時間內派生子行程，該子行程已不在 job（Windows 只會把「指派之後」建立的後代放入 job，依 MS 文件語意推論）。實務上 bash 啟動要載入 MSYS 執行環境，空窗內派生孫行程的機率低，但不是零。
2. `SetInformationJobObject` 與 `AssignProcessToJobObject` 的回傳值**被忽略**（`:778-786`）；失敗時只剩「job 存在但沒設 KILL_ON_JOB_CLOSE／行程不在 job」，且無日誌。桌面端版本則會檢查回傳並回 `None`（`process_lifecycle.rs:80-99`）。
3. 若 Buzz 本身已被外層 job 管轄（例如被 IDE、CI、任務排程器放進 job），Windows 8 以前不支援巢狀 job、指派會失敗；Windows 8 之後支援巢狀（MS Learn 同頁）。Windows 11 不受影響。
4. 該 job 沒有設 `JOB_OBJECT_LIMIT_BREAKAWAY_OK`，所以子行程用 `CREATE_BREAKAWAY_FROM_JOB` 也逃不掉；反之，MS 文件指出若子行程自己呼叫 `AssignProcessToJobObject` 把自己放進別的 job，會失敗，可能讓少數依賴自建 job 的工具（如某些 build 工具）行為異常。

---

## 5. Nostr 簽名：Agent 身分與審計鏈的工程落地

### 5.1 Agent 身分識別（有簽名、有 owner 背書）

```text
Agent 金鑰對 (secp256k1, BIP-340)
   ├─ 連線：NIP-42  relay 送 challenge → Agent 簽 kind 22242 → 驗 ±60 秒（ARCHITECTURE.md:857-861）
   ├─ HTTP ：NIP-98 簽 kind 27235（驗 URL + method）
   ├─ 事件：每則訊息 sig = Schnorr(id)，作者 = event.pubkey
   └─ 背書：NIP-OA 在事件 tags 放 ["auth", owner_pubkey, conditions, sig]
            owner 以 Schnorr 簽名授權 agent 金鑰；事件作者仍是 agent（docs/nips/NIP-OA.md）
```

- 把 owner 與 agent 分成兩把金鑰，**「誰做的」(event.pubkey) 與「誰授權的」(auth tag) 分開記錄**，不重用 NIP-26 的「事件歸屬 delegator」語意（NIP-OA 動機段）。
- `auth` tag 必須剛好 4 個元素，多於一個 `auth` tag 視為無效（NIP-OA「The Tag」）。
- `git-sign-nostr`：以 `gpg.x509.program` 介面簽 commit/tag，簽章是 BIP-340；`TRUST_FULLY` **只是建議性**（等於「簽章金鑰 = `user.signingkey`」），不是信任根；`nostr-oa-status` 另行輸出 `valid/invalid_signature/expired/...`，呼叫端必須另外檢查（`crates/git-sign-nostr/src/lib.rs:21-38`）。**Unix-only**，Windows 需另想辦法（見第 6 節）。

### 5.2 雜湊鏈審計（真正做法）

```text
append(entry):
  BEGIN
  guard_community_write()            ← 社群刪除/停用檢查
  pg_advisory_xact_lock(community)   ← 單一寫入者            service.rs:55-62
  head = SELECT seq,hash … ORDER BY seq DESC LIMIT 1          service.rs:68-74
  seq = head.seq+1 ; prev_hash = head.hash
  created_at = 截到微秒（Postgres TIMESTAMPTZ 精度）            hash.rs:14-26
  hash = SHA256( "buzz:audit:v2\0"
                 ‖ TLV(1 community_id) ‖ TLV(2 seq) ‖ TLV(3 created_at)
                 ‖ TLV(4 action) ‖ TLV(5 actor_pubkey?) ‖ TLV(6 object_id?)
                 ‖ TLV(7 canonical_json(detail)) ‖ TLV(8 prev_hash?) )   hash.rs:43-67
  INSERT audit_log; COMMIT

verify_chain(from, to): 逐筆檢查 prev_hash 等於前一筆 hash，且重算 hash 一致   service.rs:140-185
```

工程要點（可直接借用）：

1. **TLV 編碼取代拼接**：v1 把欄位直接串接，位元組可在欄位間移動而得到同一雜湊；v2 每個欄位帶 1 byte tag + 8 byte 長度，缺席的選填欄位省略（`hash.rs:28-34`、`:69-75`）。舊資料保留 `hash_version=1`，用 `CHECK (hash_version IN (1,2))` 與預設值 1 遷移（`migrations/0048_audit_hash_version.sql`）。
2. **時間戳先截斷再雜湊再存**，否則「寫入時的 preimage」與「從資料庫讀回的 preimage」不同，驗證永遠失敗（`hash.rs:14-26` 註解）。
3. **每個社群各一條鏈**，advisory lock 以社群為粒度（`service.rs:56-58`）。
4. **不記錄 `KIND_AUTH`**：直接回 `AuditError::AuthEventForbidden`（`ARCHITECTURE.md:611`），避免把簽名挑戰存起來。
5. **誠實的限制**：雜湊鏈只能「偵測」竄改，不能「防止」有資料庫寫入權的人重算整條鏈；要提高保證，需要把鏈頭（最新 hash）定期外送到 relay 管理員之外的地方（例如簽名後公布）。這是本人的推論，Buzz 文件未描述此外送機制。

### 5.3 若要自己做「Agent 簽名審計」的最小設計（建議，未實作）

```text
每個任務動作 → 一筆 JSONL： {seq, ts, agent_id, action, detail_canonical_json, prev_hash}
hash = sha256(domain_tag ‖ TLV 欄位)             ← 抄 hash.rs 的 TLV 與截斷時間戳
sig  = Schnorr/Ed25519(agent_key, hash)           ← 這一步才把「身分」加進鏈；Buzz 的鏈本身沒有
定期： 把 (最新 seq, hash) 簽名後寫到另一個位置   ← 防整鏈重寫
```

---

## 6. 本地調度啟發（對 `agent-relay` 與本機多 Agent 流程）

現況對照（`C:\GitHub\agent-relay\agent_relay\dispatch.py`）：

| 面向 | Buzz | agent-relay 現況 | 啟發 |
|---|---|---|---|
| 逾時殺行程樹 | Job Object：`TerminateJobObject` + `KILL_ON_JOB_CLOSE`（`shell.rs:770-833`） | `_kill_tree`：Windows 用 `taskkill /T /F /PID`（`dispatch.py:602-606`），由 `run()` 在 `proc.wait(timeout)` 逾時後呼叫（`:609-634`） | `taskkill /T` 是靠父子關係走訪行程樹；若中間行程已先結束，孫行程可能不在樹內（推論，未實測）。Job Object 以「建立時歸屬」判斷，不受此影響 |
| 調度程序崩潰時的孤兒 | Job handle 隨 Buzz 結束關閉 → 全樹被殺 | 父程序若被強殺，子 agent 不一定會一起死（推論） | 讓 job handle 與調度程序同生共死，等於免費的「父死子死」 |
| 通訊格式 | Nostr 簽名事件 | 本機 Mailbox/SQLite | 見 `T-20261026-10`（NIP-01 欄位對照） |
| 權限閘門 | `buzz-acp` 對 `request_permission` 自動 `allow_once` | 以 envelope 與 gate 控制 | 不要照搬自動核准；危險指令仍應有人工或規則閘門 |

可落地的三步（都只是建議，未在 agent-relay 實作；改 agent-relay 屬其他任務範圍）：

1. 在 `agent-relay` 的 `run()` 加入選用的 Job Object 路徑：Python 標準庫的 `ctypes` 可呼叫 `kernel32` 的 `CreateJobObjectW`、`SetInformationJobObject`、`AssignProcessToJobObject`、`TerminateJobObject`；`Popen` 加 `CREATE_SUSPENDED` 旗標後指派再恢復執行緒，可關閉第 4.4 節第 1 點的競態。**Python 沒有現成的 `ResumeThread` 包裝，需要自己用 `ctypes` 呼叫 ToolHelp，實作成本不低**，建議先以 `T-20261026-09` 在 Buzz 上驗證行為再決定。
2. 保留 `taskkill /T /F` 作為「重啟後只剩 PID」的退路（Buzz 桌面端同樣保留，見 4.3）。
3. 用 Buzz 的「回傳碼約定」：逾時 124、被取消回 `cancelled`、殺行程碼 137，讓日誌與重試分類更一致。

---

## 7. 查證來源與未查證項目

已查證（本機原始碼，commit `9e8c9fc`）：`crates/buzz-dev-mcp/src/shell.rs`、`crates/buzz-dev-mcp/Cargo.toml`、`desktop/src-tauri/src/managed_agents/process_lifecycle.rs`、`crates/buzz-agent/src/{lib,mcp,config,handoff,wire}.rs`、`crates/buzz-acp/src/acp.rs`、`crates/buzz-audit/src/{hash,service}.rs`、`crates/buzz-search/src/{lib,query}.rs`、`crates/buzz-core/src/kind.rs`、`migrations/0001`、`0048`、`ARCHITECTURE.md`、`docs/nips/NIP-OA.md`、`NIP-GS.md`、`crates/git-sign-nostr/src/lib.rs`。

外部文件：

- Microsoft Learn〈Job Objects〉：<https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects>（2026-10-26 讀取；頁面日期 2025-07-14）
- Buzz 倉庫：<https://github.com/block/buzz>
- ACP 協議站：<https://agentclientprotocol.com/>（取自 `ARCHITECTURE.md:771`，本次未另行讀取內容）

未查證／未實測：

- 沒有在 Windows 上建置或執行 `buzz-dev-mcp`（`T-20261026-09` 負責）。第 4.4 節弱點皆為讀碼推論。
- `ARCHITECTURE.md` kind 表中 `43001` 等數字未逐一對照 `kind.rs`。
- `'simple'` FTS 對繁體中文的實際檢索品質未測。
- ARCHITECTURE 提到的「approval gates 尚未端到端接通」（`ARCHITECTURE.md:964-975` 第 5 項）表示 Buzz 的人工核准流程仍在建構中，相關結論以該項限制為前提。
