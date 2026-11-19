# agent-relay 對照常駐 Agent 五原語的缺口盤點（T-20261119-04）

> 盤點日 2026-11-19。對象：[`SanHsien/agent-relay`](https://github.com/SanHsien/agent-relay) commit [`0cabfe3`](https://github.com/SanHsien/agent-relay/tree/0cabfe33c46bc0ca80234fad579c2ea8ba82896c)。
> 做法：**只讀原始碼與 `SPEC.md`，沒有執行、沒有修改 agent-relay**。下文的「路徑:行號」都指這個 commit。
> 來源筆記：[`notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md`](../notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md)。

## 1. 結論

| 原語 | 判定 | 一句話 |
| --- | --- | --- |
| Inbox | 大部分已覆蓋，兩個缺口 | 同 id 拒收、一張工單只跑一個工人都有；缺「來源端事件鍵去重」與「同一信箱（或同一討論串）只跑一個工人」 |
| Timers | 輪詢已覆蓋，自訂提醒缺 | 排程工作定時收信與補回中斷工單都有；agent 自己設的跟催、提問期限沒有任何程式會到期觸發 |
| Memory | 讀取已覆蓋，回寫缺 | 開工前自動帶入交接資料；工單中斷後沒有進度檔可續跑，relay 也不回寫交接單 |
| Permissions | 靜態規則完整，暫停續跑缺 | 簽章、名單、沙盒、推送白名單齊全；沒有「高風險動作暫停、等人批准再續跑」，人工關卡在事後的合併驗收 |
| Outbox | **主要缺口** | 每封新信各響一次，沒有彙整、節流、優先級過濾；通知失敗不補發 |

最值得先做的是 Outbox 的兩項（第 4 節 R1、R2），改動小、直接對應「不洗版」。Inbox 的去重在目前「一律由 relay 自己產生 id」的用法下風險低，等到有排程或 hook 自動寄信時再補。

## 2. 對照依據

官方文章：Anthropic〈Building always-on agents〉，William Hu，2026-11-13，<https://claude.com/blog/building-always-on-agents>（2026-11-19 讀取，以下為轉述）。

讀原文後，筆記裡有兩處說法要修正：

- 筆記寫「同一串流同時只有單一 worker」。原文的單位是**信箱**：一個收件匣同時只有一個工作中的 worker，並建議先從「每位使用者一個收件匣」開始。
- 原文沒有提到跟催數量上限、最短間隔、摘要彙整或頻率限制的具體數字；Outbox 一節只說先用簡單的傳送工具，需要控制節奏或錯誤復原時再加正式的 outbox 資料表與分派器，並以「一開始少發」為原則。網路上流傳的上限建議出自第三方整理。

agent-relay 的資料流與五原語的對應位置：

```text
寄件端 send/ask ──▶ mailboxes/<agent>/new/<id>.json ──────────────┐  Inbox
                     （同 id 拒收；狀態只靠改名 new→cur→done）      │
                                                                   ▼
Windows 排程工作（每 N 分鐘）──▶ watch --once ──▶ 還沒響過的信     Timers
        │                            │
        │                            ├─▶ 門鈴 toast / command / handoff   Outbox（對人）
        │                            └─▶ 門鈴 dispatch：開分頁跑工人
        │                                     │
        │      寄件者名單＋簽章＋repo_roots ──┤                    Permissions
        │      交接資料 HANDOFF.md 等 ────────┤                    Memory
        │                                     ▼
        │                          worktree 內施工 → 驗收閘門
        │                                     │
        └─▶ 補回逾期／沒啟動的工單            ▼
            （回 interrupted）       回信 kind=result ＋ ack 原信   Outbox（對指揮者）
```

## 3. 逐項對照

「證據」欄的檔案都在 `agent_relay/` 底下，除非另外寫明。

### 3.1 Inbox

| 官方要求（轉述） | agent-relay 現況 | 判定 | 證據 |
| --- | --- | --- | --- |
| 持久儲存；一端寫入、一端讀取；每筆事件有狀態 | Maildir 式目錄 `new／cur／done`；先寫暫存檔再改名，讀的人看不到半封信；狀態轉換只用改名 | 已覆蓋 | `store.py:3-8`、`store.py:44-48`、`store.py:108-113` |
| 用來源的唯一識別碼去重 | 同一信箱內 id 重複會**拒收並報錯**（不是靜默丟棄）。但 id 是寄信當下由 relay 產生的時間戳加亂數，信封沒有「來源事件鍵」欄位：寄件端把同一件事重寄一次就是兩封不同 id 的信 | **缺口（部分）** | 拒收：`store.py:42-43`、`SPEC.md:77`；id 產生：`envelope.py:42-45`、`envelope.py:65-66`；必要欄位：`envelope.py:35` |
| （同上，已有的緩解） | 同步失敗時回結束碼 3 並明講「不要重寄」；門鈴用已響清單去重，逐封原子存檔；交接卡以 id 命名，重響不會多一張；已回信的工單不重跑；簽章信超過期限不執行 | 已覆蓋 | `cli.py:291-297`；`cli.py:543`、`cli.py:552-553`、`doorbell.py:236-248`；`doorbell.py:190-192`；`dispatch.py:1111-1117`；`dispatch.py:208-214` |
| 一個信箱同時只有一個工作中的 worker | 鎖的單位是**工單**與**檔案路徑**，不是信箱：一張工單只跑一個工人；有 `dispatch.paths` 時檔案範圍重疊會擋。門鈴是「一封信開一個分頁」，`max_concurrent` 沒設就不限並行，同一討論串的兩張工單路徑不重疊時會同時跑 | **設計不同，部分缺口** | 單一工人：`dispatch.py:914-929`、`SPEC.md:468`；名額：`dispatch.py:945-971`；路徑鎖：`locks.py:269-290`；路徑非必填：`dispatch.py:215-216`；一信一分頁：`dispatch.py:1431-1448`、`gitsync.py:40` |
| （同上，跨機器） | 工單持有紀錄 `.owner` 放在本機的 relay home，不進 store。兩台機器（或兩個 home）輪詢同一個信箱時互相看不到對方的持有紀錄。`SPEC.md` 自己也註明跨機器行為只在同一台主機的兩份 clone 上測過 | 缺口（目前用法碰不到） | `dispatch.py:916`、`dispatch.py:849-850`、`SPEC.md:447` |
| 排程層不重入 | 排程工作設定為已有一個在跑就忽略新的；store 的 git 操作用鎖檔排隊 | 已覆蓋 | `poller.py:45`、`gitsync.py:37-66` |
| 跑完才標記完成 | 先投遞回信，再 ack 原信；每種結局都以一封回信加一次 ack 收尾 | 已覆蓋 | `dispatch.py:1078-1079`、`dispatch.py:1101` |
| worker 當掉後，接手的 worker 可重試同一筆事件 | 逾期或沒啟動的工單會被補回一封 `interrupted` 並結案，**不會自動重跑**；要重跑得重寄或手動 `--force`。單次執行內有重試與換 runtime | 設計不同 | 補回：`dispatch.py:1380-1418`；執行內重試：`dispatch.py:1183-1185` |
| 把多筆待處理事件併成一次執行；執行中來的新事件要有處理方式 | 沒有。一封 task 一個一次性工人，執行中收到的新信等下一輪 | 缺口（一次性工人的模型下不適用） | `cli.py:545-553` |
| 收件要快，深入檢查留到執行時 | 投遞只驗信封格式；寄件者名單、簽章、時效、repo 範圍在開工前才查 | 已覆蓋 | `store.py:38-39`、`dispatch.py:190-231` |

### 3.2 Timers

| 官方要求（轉述） | agent-relay 現況 | 判定 | 證據 |
| --- | --- | --- | --- |
| 排程器固定間隔輪詢，睡眠後能補跑 | Windows 排程工作每 N 分鐘跑 `watch --once`，設定了錯過就補跑；單次上限 10 分鐘，所以工人另開行程 | 已覆蓋 | `poller.py:23-63`、`poller.py:48`、`poller.py:52`、`dispatch.py:1431-1437` |
| 定時器到期時，往收件匣放一筆事件 | 只有系統自己的期限會這樣做：工單 lease 逾期或門鈴響了卻沒啟動，下一輪 `watch` 補一封 `interrupted` 回信 | 部分覆蓋 | `dispatch.py:1136-1137`、`dispatch.py:1366-1377`、`cli.py:538-542` |
| agent 自己設的跟催（到某時間再回來看） | 沒有。store 裡沒有定時器物件，寄件端無法說「三小時後沒回就提醒我」 | **缺口** | `gitsync.py:24`（store 只同步 `mailboxes／claims／audit／hosts`） |
| 提問的期限 | `question.deadline` 只是單行文字，只在 `read` 時顯示，沒有程式會解析或到期觸發；`relay status` 的逾期清單只算工單 lease | **缺口** | `envelope.py:119-123`、`cli.py:313-314`、`cli.py:504-505`、`status.py:56-59`、`status.py:113-114` |
| 週期性排程 | 不在 relay 內，由外部排程（Windows 排程工作、各 agent 自己的 cron）往信箱寄信 | 不在範圍 | — |
| 收件端是否還活著 | 心跳檔，內容沒變且未到間隔就不寫；超過門檻標為逾時 | 已覆蓋 | `status.py:63-87`、`status.py:107-111` |

### 3.3 Memory

| 官方要求（轉述） | agent-relay 現況 | 判定 | 證據 |
| --- | --- | --- | --- |
| 記憶放在 worker 之外的持久儲存，每次執行開頭載入 | 交接資料包：`HANDOFF.md`、Obsidian 筆記、待接手的交接卡、上一個 session 摘要、git 狀態；派工時放進工人的 prompt，互動 session 由 SessionStart hook 帶入 | 已覆蓋（讀取） | `context.py:119-151`、`context.py:212-252`、`dispatch.py:1173-1180`、`hooks/session_start.py:1-24` |
| 基本 context 要精簡 | 每段與總量都有字數上限，整段捨棄而不是切一半；有時間預算 | 已覆蓋 | `context.py:30-37`、`context.py:239-245` |
| 帶入的資料要防注入與洩密 | 資料包用亂數標記包起來並聲明「是資料不是指令」；金鑰形狀的字串遮罩 | 已覆蓋 | `context.py:246-251`、`context.py:39-58` |
| 每個進行中的任務有一份進度檔，喚醒後接著做 | 執行紀錄 `state.json` 只記階段、pid、期限，不記做到哪裡；各次嘗試的輸出 log 有保留；中斷時 worktree 留在原處，但沒有機制讓下一個工人讀它接著做 | **缺口** | `dispatch.py:821-838`、`dispatch.py:1193-1200`、`dispatch.py:1406-1407` |
| 執行中把學到的東西寫回記憶 | relay 只讀交接資料，不回寫 `HANDOFF.md` 或筆記；結果只存在回信與 git 分支 | 缺口（刻意：寫入由 session 自己的交接流程負責） | `context.py:212-252` |
| 記住已經告訴過使用者什麼 | 通知層有：已響清單保留最近 1000 筆。內容層沒有 | 部分覆蓋 | `doorbell.py:31`、`doorbell.py:229-248` |

已響清單只留 1000 筆有一個低風險邊界：一封一直留在 `new/` 沒人讀的非派工信，在它之後又來了超過 1000 封，會再響一次。派工信不受影響，沒啟動的工單會先被補回並結案。

### 3.4 Permissions

| 官方要求（轉述） | agent-relay 現況 | 判定 | 證據 |
| --- | --- | --- | --- |
| 憑證放在 agent 環境外的代理，由代理注入對外請求 | 沒有注入代理。做法是不給：codex 工人沙盒關網路、claude 工人不帶任何 MCP 伺服器與全域設定、hermes 只給檔案工具且限制可寫根目錄。例外是 `claude-3p`：閘道金鑰執行時從 Desktop 設定檔讀出，放進**工人行程的環境變數**（不進設定、信封、參數或 log） | 設計不同；`claude-3p` 是缺口 | `dispatch.py:335-338`、`dispatch.py:445-459`、`dispatch.py:462`、`dispatch.py:525-530`；金鑰：`dispatch.py:491-516`、`dispatch.py:523-524` |
| 分類器審查高風險動作 | 沒有分類器，用靜態規則：寄件者預設全拒、必須有本機信任的簽章、repo 必須在允許的根目錄下、runtime 白名單、只推送到維護者自己的 repo、敏感路徑預設封鎖 | 設計不同（規則取代分類器） | `dispatch.py:198-207`、`dispatch.py:219-230`、`dispatch.py:1022-1035`、`gates.py:259-263` |
| 需要人回答的工具呼叫先暫停：存下執行中的 session，把請求給使用者，答案以收件匣事件回來後續跑 | 沒有。工人是一次性的，有逾時上限，不能中途停下等人。程式裡的 `Deferred` 是**額度不足延後**，名字相同、意思不同 | **缺口** | `dispatch.py:75-76`、`dispatch.py:953`、`dispatch.py:1147`；逾時：`dispatch.py:55-57` |
| （同上，最接近的既有機制） | 提問流程：`ask` 寄出 `kind=question`，`answer` 的回覆以 `reply` 信進到提問者信箱並結案原題。這對互動 session 等同「答案以收件匣事件回來」；派工工人用不到 | 部分覆蓋 | `cli.py:302-340`、`cli.py:343-402`、`envelope.py:98-125` |
| 最重要的決定留給使用者 | 人工關卡在事後：工人只能在 worktree 的分支上改，合併要經 `relay accept` 重新驗證；指揮者可設自動驗收 | 已覆蓋（事後） | `accept.py:100-166`、`cli.py:607-615` |

### 3.5 Outbox

| 官方要求（轉述） | agent-relay 現況 | 判定 | 證據 |
| --- | --- | --- | --- |
| 每次執行的結局是：發訊息、不發、或延後等使用者 | 對指揮者：每張工單固定回一封結果信，沒有「不發」的選項（這一層是機器對機器，應該如此） | 已覆蓋 | `dispatch.py:1066-1083`、`dispatch.py:1101` |
| 需要控制節奏時，加 outbox 資料表與分派器 | 對人的通知沒有 outbox：`watch` 對每封新信逐一按每個門鈴，一封一則。一輪收到 N 封就是 N 則 toast 加 N 則手機訊息（若接了 `command` 門鈴） | **缺口** | `cli.py:543-553`、`doorbell.py:205-222`、`SPEC.md:102-106` |
| 一開始少發 | 門鈴只能用 `kinds` 過濾信件種類。信封有 `priority`，失敗的回信會標 `high`，但門鈴不看這個欄位，無法設成「只有 high 才發手機」 | **缺口** | `doorbell.py:210-213`；標 high：`dispatch.py:1070`、`accept.py:218`；`priority` 在門鈴只出現在交接卡內文：`doorbell.py:120` |
| 純資訊不打擾 | `accepted:`／`rejected:` 通知信會自動結案，但順序是**先響門鈴再自動結案**，所以還是會跳通知 | 部分覆蓋 | `cli.py:546-547`、`cli.py:603-606` |
| 傳送失敗可復原 | 門鈴失敗只寫 log，該信照樣記入已響清單，下一輪不補發。信件本身還在，`relay status` 看得到信箱裡的數量 | **缺口** | `doorbell.py:219-221`、`cli.py:552-553`、`status.py:93-98` |
| （既有的節流） | 心跳未到間隔且內容沒變就不寫；Antigravity sidecar 一輪只通知一封、間隔至少 30 秒、被拒的信只回報一次；`watch` 常駐模式沒新信時不輸出 | 已覆蓋（局部） | `status.py:78-82`；`antigravity.py:165-172`、`antigravity.py:219`、`antigravity.py:227-230`；`cli.py:642-643` |
| （收件端的量管） | `max_concurrent`、`daily_limit` 管的是**收進來的工作量**，不是發出去的通知量 | 不是 Outbox 節流 | `dispatch.py:945-971` |

## 4. 可選的改進建議

以下都沒有實作，只是給 agent-relay 之後排工作時參考；每項寫明要改的檔案。

| 編號 | 建議 | 要改哪裡 | 理由與代價 |
| --- | --- | --- | --- |
| R1 | 門鈴加優先級過濾，寫法比照現有的 `kinds`，例如 `"priorities": ["high"]` | `doorbell.py` 的 `ring()`（第 210 行附近）＋`SPEC.md` 第 4 節 | 改動最小。手機通知可以設成只收失敗與被退回的結果，成功的只跳 toast 或完全不跳 |
| R2 | 同一輪多封新信時，對人的門鈴（`toast`、`command`）合併成一則摘要；`handoff`、`dispatch` 仍逐封處理 | `cli.py` 的 `watch_once()`＋`doorbell.py` 新增摘要格式 | 一輪 N 封變一則。要決定摘要的佔位欄位（`{count}`、`{summary}`），舊設定不能壞 |
| R3 | 自動結案的通知信不響門鈴：把 `automate()` 的判斷移到按門鈴之前，或讓這類信只走 log | `cli.py:545-553` | `accepted:` 信的內容指揮者自己剛做完，再跳一次通知沒有資訊 |
| R4 | 門鈴失敗補發：對人的門鈴全部失敗時先不記入已響清單，並設重試次數上限 | `cli.py:552-553`、`doorbell.py` | 手機通知服務斷線時不會漏；沒有上限會變成每輪重響，上限一定要有 |
| R5 | 選填的來源事件鍵：`send --dedupe-key <鍵>` 寫進信封；`Store.deliver` 發現同寄件者、同鍵的信已存在（含 `done`）就不投遞，回傳原 id 並標示已丟棄 | `envelope.py`（新欄位與驗證）、`store.py:37-53`、`cli.py` 的 `send`、`SPEC.md` 第 1、2 節 | 排程或 hook 自動寄信、失敗重試時才需要。信封加欄位要顧舊版用戶端相容與簽章範圍 |
| R6 | 提問期限改成機器可讀的時間；`relay status` 列出逾期未答的題目，`watch` 對逾期題目補響一次 | `envelope.py:119-123`、`status.py:90-114`、`cli.py` 的 `watch_once()` | 補上「定時器到期就放一筆事件」。舊題目的自由文字期限要保留相容 |
| R7 | 需要依序處理時，提供同一討論串只跑一個工人的選項 | `dispatch.py` 的 `take_task()`，比照 `.owner` 多一份以 thread 為鍵的持有紀錄 | 只有工單之間有先後相依才需要；預設維持並行，否則白白變慢 |
| R8 | 中斷續跑：`interrupted` 回信附上保留的 worktree 與分支位置，重寄時可指定從該分支接著做 | `dispatch.py:1380-1418`、`make_worktree()` | 目前中斷等於從頭來。要先想清楚半成品是否可信，這題不小 |
| R9 | 「工人需要人決定」的書面慣例：工人以 `needs-input` 結果加一封 `question` 收尾，指揮者 `answer` 後以同一討論串重派 | 先只改 `SPEC.md` 與派工信範本 | 不存 session、不改執行流程，用既有的信件種類拼出暫停續跑的效果；真正的執行中暫停不建議做 |

不建議做的：為了對齊官方架構而加憑證注入代理或風險分類器。agent-relay 的工人預設沒有網路、沒有 MCP、只能動 worktree，要保護的對外憑證本來就不在工人手上；`claude-3p` 的閘道金鑰是唯一例外，記在這裡備查即可。

## 5. 對本機現有設定的建議

2026-11-19 唯讀查看本機兩個 relay home 的設定結構（只看門鈴種類與上限，沒有改動）：

```text
指揮者 home：doorbells = [toast]；accept.auto = true、accept.push = true
收件工人 home：doorbells = [toast, dispatch]；dispatch.max_concurrent = 2、daily_limit = 20
```

- 目前對人的通知只有 toast，沒有接手機通知的 `command` 門鈴，所以洗版的實際影響限於桌面通知。**在 R1 做完之前，不建議在指揮者 home 的 `config.json` 加上 Telegram 的 `command` 門鈴**；要加的話至少帶 `"kinds": ["result", "question"]`，不要收 `note`。
- 收件工人的 `max_concurrent = 2` 已經限制了同時通知的上限，維持即可。
- 全域規則裡「有需要才回報」的判斷目前靠 agent 自己遵守；R1 做完後可以改成由門鈴設定強制（只有 `priority: high` 才發手機）。

## 6. 限制

- 只讀了原始碼與規格，沒有執行 agent-relay 的測試，也沒有實際觸發重複投遞或大量通知來觀察行為；「會響 N 次」等敘述是依程式流程推得。
- 官方文章的要求是轉述，判定欄是本文的對照，不是 Anthropic 對 agent-relay 的評價。
- 本機 Windows 排程工作是否已註冊、間隔幾分鐘，這次沒有查證。
