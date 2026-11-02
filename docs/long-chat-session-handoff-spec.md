# 長會話上下文膨脹告警與一鍵交接規格手冊

## UserPromptSubmit Hook 與 Session 生命週期控制

- **文件版本**：1.0.0
- **查證日期**：2026-11-02
- **對應筆記**：[`notes/2026-11-02-littlehole-claude-saver-long-chat-session-handoff.md`](../notes/2026-11-02-littlehole-claude-saver-long-chat-session-handoff.md)
- **原作**：[`littlehole2025/claude-saver`](https://github.com/littlehole2025/claude-saver)，本文一律對照 commit `434750eb61510db40d567617862800f4fde2f65c`（v1.2.0，2026-11-01）
- **參考實作與以程式為準**：[`tools/verify_session_token_sentinel.py`](../tools/verify_session_token_sentinel.py)，測試在 [`tests/test_verify_session_token_sentinel.py`](../tests/test_verify_session_token_sentinel.py)。本文的數值與例子都用該工具實際跑過；文件與程式不一致時以程式為準，並應修文件。
- **配套範本**：[`templates/session-handoff-brief-prompt.md`](../templates/session-handoff-brief-prompt.md)

> **讀這份文件能做什麼**：(1) 自己寫一個「對話太長就提醒」的 UserPromptSubmit hook，並知道哪些邊界會踩雷；(2) 用工具重現「第幾輪該提示、第幾輪該壓制」的階梯行為；(3) 在 Claude 桌面版、Antigravity、純終端機三種環境下，知道交接與封存該用什麼動作、失敗時怎麼降級。

---

## 0. 查證狀態總表

| 項目 | 狀態 | 依據 |
| :--- | :--- | :--- |
| UserPromptSubmit 的輸入欄位、`additionalContext`／`systemMessage` 輸出、結束碼語意、逾時預設 | 已查證 | 官方 hooks 參考（第 8 節來源 1）全文開啟比對 |
| 原作 hook 的演算法（讀尾端 2MB、三欄加總、級距、狀態檔） | 已查證 | 原作固定 commit 的 `hooks/long-chat-reminder.js` 全文 |
| 原作 handoff 流程（改名加 1、先確認再封存、CLI 降級） | 已查證（僅限原作 skill 內容） | 原作 `skills/handoff/SKILL.md` |
| Claude 桌面版有 `start_session`／`get_session`／`archive_session` 這組工具及參數 | **未驗證** | 官方文件（hooks、desktop、sessions、costs、prompt-caching、context-window、model-config）全文搜尋沒有這些名稱；只在原作 skill 出現。官方只寫到「可以請 Claude 重新命名或封存其他 session」與側欄選單 Archive |
| Antigravity 的 `agentapi new-conversation`、`UpdateConversationAnnotations` | **未驗證（僅有本 repo 內部紀錄）** | 本 repo [`docs/agent-dispatch.md`](agent-dispatch.md) 第 8、10、20、22 行；未對照廠商官方文件 |
| 「150k tokens 起算、每 50k 提示」的合理性 | **無外部依據** | 這是原作的預設值，沒有找到來源或量測；見第 1.3 節 |
| Codex 的新會話／封存介面 | **未驗證** | 本文不保證，只提供貼上式降級 |
| transcript JSONL 內 `message.usage` 的欄位格式 | 未見官方文件 | 官方只說 `transcript_path` 指向對話 JSON；欄位格式以原作程式為準，工具遇到格式不符會明確失敗 |

---

## 1. 成本模型與門檻依據

### 1.1 官方文件說了什麼

- 成本隨上下文大小成長：「Token costs scale with context size: the more context Claude processes, the more tokens you use.」（costs 頁「Reduce token usage」）。
- 官方建議在不相關的工作之間清空：「Use `/clear` to start fresh when switching to unrelated work. Stale context wastes tokens on every subsequent message.」並建議清空前先 `/rename`，之後可 `/resume` 回來。
- Prompt cache 有存活時間（5 分鐘或 1 小時兩種），過期後整段前綴要重算；`/compact` 與模型切換也會造成未命中（prompt-caching 頁）。所以「有快取」不等於長對話免費，只是重複內容較便宜。
- 部分模型在提示超過一定長度後單價較高：官方 model-config 頁寫 Haiku 5.5 的提示「超過 100K tokens 時每 token 較貴」（價格另見官方定價頁）。這是單一模型的例子，不是通則。
- 各模型的上下文視窗不同（200K 或 1M，視模型與設定），自動壓縮的邊界也隨之不同。因此 150k 這個固定值不對應任何官方邊界。

### 1.2 累計成本的算式（修正筆記的說法）

筆記寫「Token 呈階乘級累積燃燒」，這不正確。每一輪都要重送目前的整段上下文，若上下文每輪平均增加 `g`，第 `k` 輪送出 `C + g(k-1)`，累計是**二次（quadratic）**成長，不是階乘：

```text
累計輸入 tokens（N 輪）= N × C + g × N × (N − 1) / 2
                          └ 線性項 ┘  └──── 二次項 ────┘
```

換成新對話後，起點從 `C` 降到 `B`（交接 brief 的大小，再加任何新對話都有的固定開銷 `F`）。兩者相減，二次項互相抵消：

```text
省下的 = N × (C − B − F)       與 g 無關；N 越大省越多
```

用工具實際算（`C`=180000、`g`=3000、`N`=20、`B`=6000，數字是假設，請換成你自己的量測）：

```text
$ python tools/verify_session_token_sentinel.py cost --context 180000 --growth 3000 --turns 20 --brief 6000
continue_total=4170000 handoff_total=690000 saving=3480000 (raw input tokens, 未加權、未計價)
$ python tools/verify_session_token_sentinel.py cost --context 180000 --growth 3000 --turns 20 --brief 6000 --baseline 25000
continue_total=4170000 handoff_total=1190000 saving=2980000 (raw input tokens, 未加權、未計價)
```

**限制**：這是原始輸入 token 數的算術，**未加權快取讀取與寫入的差價、未計價、不含輸出 token**，也不代表帳單；`--baseline` 的 25000 只是示例。換對話的代價（brief 要產生、新對話第一輪沒有快取）也沒有算進去，所以只適合判斷「值不值得考慮換」，不是精算。

### 1.3 「注意力發散」與 150k／50k 的依據

- 學術上有「長上下文中，位於中段的資訊較不容易被用到」的結果：Liu 等人，*Lost in the Middle: How Language Models Use Long Contexts*（arXiv:2307.03172）。該研究測的是當時的特定模型與任務，**不提供「超過多少 tokens 就變差」的通用門檻**，也不能直接推到現行的 Claude 模型。
- 原作把 `LONG_CHAT_TOKENS` 預設為 150000、`LONG_CHAT_STEP` 預設為 50000，兩者都可用環境變數調整；原作 README 沒有說明這兩個數字的來源，我也沒有找到量測。因此：**150k 與 50k 是原作作者的預設，在本 repo 只當作可調的起點**。
- 調整建議（本 repo 的取捨，不是定論）：門檻要明顯小於你實際使用模型的自動壓縮邊界，否則會先被自動壓縮截走；步進決定使用者看到提示的頻率，太小會刷屏。改完用第 6 節的 `simulate` 重跑一遍階梯。

---

## 2. UserPromptSubmit Hook 規格

### 2.1 官方介面（2026-11-02 對照 hooks 參考）

```text
 使用者送出 prompt
        │
        ▼
 UserPromptSubmit hook（command）── stdin：JSON ──▶ 你的程式
        │                                              │
        │   exit 0 ＋ stdout JSON／純文字               │
        │◀─────────────────────────────────────────────┘
        ▼
 additionalContext ──▶ 包成 system reminder 附在該 prompt 旁，Claude 讀得到、對話畫面不顯示
 systemMessage     ──▶ 顯示給使用者的警示
```

- **stdin 欄位**：共通欄位含 `session_id`、`transcript_path`、`cwd`、`hook_event_name`；本事件另有 `prompt`，有自訂標題時還有 `session_title`。`prompt` 若含貼上內容，會被 `<pasted_content id="…">` … `</pasted_content id="…">` 包住，解析提問時要排除這段。
- **`transcript_path` 的限制**：官方說明 transcript 是非同步寫入，可能還沒包含「當輪」最新訊息。所以本 hook 量到的是「上一輪回覆」的用量，是正確且足夠的訊號（原作 README 也這樣定義：上一筆回覆的用量即目前上下文大小）。
- **輸出**：exit 0 並印出**單一** JSON 物件；`hookSpecificOutput.additionalContext` 給 Claude，頂層 `systemMessage` 給使用者。前後混入其他文字（例如 shell 設定檔的 echo）會被當成純文字或解析失敗。
- **上限**：`additionalContext`、`systemMessage` 與純文字 stdout 各自上限 10,000 字元，超過會被存成檔案並只留預覽。
- **結束碼**：exit 0 成功；**exit 2 會擋下使用者的提問**（UserPromptSubmit 屬於可阻擋事件）；其他非 0 為非阻擋錯誤，提問照常送出，通知會帶 stderr 第一行。本 hook 的任何錯誤都只用 exit 1，**絕不用 exit 2**。
- **逾時**：UserPromptSubmit 的 command hook 預設 30 秒，逾時則輸出（含 `additionalContext`）被丟棄、提問照常送出。原作在 `hooks.json` 設 10 秒。
- **觸發時機不只是使用者打字**：定時任務（含 `/loop`）、背景 subagent 回報、其他 session 傳來的訊息也會觸發。所以這類自動訊息也會看到「上下文已很長」的提醒，語意判定時不要預設每個 prompt 都出自使用者。
- **設定位置**：寫進 `settings.json` 的 `hooks.UserPromptSubmit`（此事件不支援 matcher）：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python \"<工具所在資料夾>/verify_session_token_sentinel.py\" hook", "timeout": 10 } ] }
    ]
  }
}
```

`<工具所在資料夾>` 換成你複製腳本的實際位置；Ubuntu 若沒有 `python` 指令改用 `python3`。這是參考實作的接法，原作則是用 Node.js 執行 `long-chat-reminder.js`。

### 2.2 安全讀取 transcript

原作只讀檔案最後 `min(size, 2_000_000)` 位元組，從後往前找第一筆有 `"usage"` 的行；本規範沿用並補上下列邊界。「結果」欄是參考實作實際的處理：

| 情況 | 做法 | 參考實作的結果 |
| :--- | :--- | :--- |
| 檔案大於 2MB | 只讀最後 2,000,000 位元組；視窗的第一段可能是半行，**直接丟掉** | 讀到最新 usage |
| 最新 usage 在視窗之外（尾端被大量不含 usage 的行占滿） | 找不到就是找不到，不往前讀 | `no_usage`，不是 0 token |
| 視窗內連一行完整的行都沒有（單行超過 2MB） | 單獨標示 | `window_exhausted` |
| 中間夾雜壞 JSON 行 | 略過並計數 | 仍可讀到最新 usage |
| 整份都不是 JSON | 視為壞檔 | `corrupt` → hook exit 1 |
| usage 欄位型別不對（字串、布林、負數、小數、非物件） | **跳過該行**，不把字串相加（JS 會把數字串接成字串） | 計入 `bad_usage`，繼續往前找 |
| 單一欄位缺少（如沒有 `cache_creation_input_tokens`） | 當 0 | 照加總 |
| 三個欄位全缺（`usage: {}`） | **量不到**，不當成 0 token | 計入 `bad_usage`，繼續往前找 |
| 檔案不存在、空檔、尚無任何回覆 | 量不到 | `check`：exit 1；`hook`：預設 exit 0 並在 stderr 說明（新 session 第一個提問本來就量不到），加 `--strict` 才 exit 1 |
| 位元組不是合法 UTF-8 | 以取代字元解碼，不崩潰 | 照常解析其餘行 |

加總公式：`input_tokens + cache_read_input_tokens + cache_creation_input_tokens`，與原作一致；**這是上一輪的上下文大小，不是整段對話累計花費**。

> 本工具刻意**不從文字長度估 token**：沒有 usage 就回報量不到並失敗，避免用猜的數字讓驗證通過。

### 2.3 階梯與壓制演算法

```text
級距 level = (tokens − limit) // step            （tokens < limit 時沒有級距）

 tokens < limit ───────────────▶ silent   不輸出，不動狀態
 level  > last_level ──────────▶ notify   additionalContext ＋ systemMessage，寫入 last_level = level
 level <= last_level ──────────▶ inject   只有 additionalContext
```

注意「壓制」只壓制**使用者看得到的** `systemMessage`；超過門檻後**每一輪都會**給 Claude `additionalContext`（讓 Claude 判斷這則訊息是不是新話題）。筆記把兩者混在一起寫，實際行為以此為準。

用工具跑預設值（limit=150000、step=50000）的階梯，並用 `--expect` 驗證每輪預期；預期不符會 exit 1：

```text
$ python tools/verify_session_token_sentinel.py simulate --tokens 100000,150000,160000,199999,200000,250000 --expect silent,notify,inject,inject,notify,notify
turn 1: tokens=100000 verdict=silent last_level=-1
turn 2: tokens=150000 verdict=notify last_level=0
turn 3: tokens=160000 verdict=inject last_level=0
turn 4: tokens=199999 verdict=inject last_level=0
turn 5: tokens=200000 verdict=notify last_level=1
turn 6: tokens=250000 verdict=notify last_level=2
（exit 0）
$ python tools/verify_session_token_sentinel.py simulate --tokens 100000,150000 --expect silent,inject
...
turn 2: tokens=150000 verdict=notify last_level=0  <-- 預期 inject
FAIL 1 輪與預期不符
（exit 1）
```

邊界：剛好等於門檻（150000）就觸發；199999 仍在同一級距；200000 進入下一級。

### 2.4 狀態暫存隔離

- 狀態檔：`<系統暫存資料夾>/claude-long-chat-<session_id>.txt`，內容只有最近一次通知的級距（整數，與原作相容）。參考實作可用 `--state-dir` 改位置（測試用）。
- **`session_id` 必須先驗證**：只允許英數、底線、連字號、最長 128 字元，否則 exit 1。原作直接把 `session_id` 串進路徑，若出現 `../` 會寫到暫存資料夾之外；`session_id` 正常來自 Claude Code 本身，風險低，但驗證成本幾乎為零。
- 狀態檔內容壞掉（非整數、小於 -1、位數過長）：參考實作**重置為 -1、在 stderr 提示、並重寫**，因為它只是快取。原作遇到壞內容時 `Number()` 得 `NaN`，之後永遠不再通知。
- 寫入用「暫存檔＋`os.replace`」，避免兩個 hook 同時寫入留下半截內容。
- **已知限制（與原作相同，刻意不修）**：上下文被壓縮或清空後縮小、再長回來時，狀態檔仍記著舊的高級距，同級距不會再通知（`simulate --tokens 200000,100000,200000` → notify、silent、inject）。要在壓縮後重設級距，需另外掛 SessionStart（`compact`／`clear`）hook 刪狀態檔，本文不含實作。

### 2.5 語意邊界判定

真正的「這是新功能還是接續」判定交給 Claude 本身（hook 只注入提示）。本 repo 另提供一個**啟發式規則**，只用來做回歸測試與範例驗證，不是產品邏輯：

- 延續詞：繼續、接著、修正、剛剛、剛才、上一步、再改、補一下、continue、keep going、just now、the previous、fix that、follow up
- 新話題詞：新增、換一個、另外想要、全新、新功能、新模組、換個話題、new feature、another thing、unrelated、switch to、different topic、new module
- 詞表是本 repo 的取捨，不是原作的名單（原作沒有詞表）。
- 只命中一邊 → `continue` 或 `new_topic`；兩邊都命中或都沒命中 → `ambiguous`，**不硬猜**。
- 詞前面緊接「不要、不用、別、先不、不」時不計（「不要新增了，繼續修正」→ `continue`）。
- 先移除 `<pasted_content>` 區塊再判定（貼上的 log 裡出現「新增」不能代表使用者意圖）。
- 空白提問無法判定，直接 exit 1。

```text
$ python tools/verify_session_token_sentinel.py classify "繼續修正剛剛的錯誤"        -> continue
$ python tools/verify_session_token_sentinel.py classify "新增一個匯出功能"          -> new_topic
$ python tools/verify_session_token_sentinel.py classify "新增欄位後再修正剛剛的錯誤"  -> ambiguous
```

限制：關鍵字無法處理反諷、省略主語或純代名詞（例如只回「好」）；中文以子字串比對，詞表外的說法一律 `ambiguous`。

### 2.6 與原作的差異（逐項列出）

| 項目 | 原作（Node.js） | 本參考實作 |
| :--- | :--- | :--- |
| 壞 stdin／缺欄位 | `JSON.parse(input \|\| "{}")`，空輸入、缺 `transcript_path` 都靜默結束 | exit 1 並說明 |
| 例外處理 | 整段 `catch {}` 吞掉所有錯誤 | 錯誤都明確回報 |
| `session_id` | 直接串進路徑 | 白名單驗證 |
| usage 型別 | 沿用 JS 動態型別，字串會被串接 | 型別不對就跳過該行 |
| 半截首行 | 靠 `JSON.parse` 失敗略過 | 明確丟棄 |
| 門檻環境變數 | `Number(env \|\| 預設)`，亂填得 `NaN` 而行為不明 | 非正整數 exit 1 |
| 狀態檔壞掉 | `NaN`，之後永不通知 | 重置並提示 |
| 提示語言 | `LONG_CHAT_LANG` 中英兩版 | 只有繁體中文，措辭自寫，且不指名 `start_session`（該工具未驗證） |
| 是否讀 `prompt` | 不讀 | 不讀（判定交給 Claude） |

本參考實作**沒有**逐位元組與原作輸出對照過（沒有在本機執行第三方腳本），行為一致性僅來自對原作程式碼的逐行閱讀與上述表格；若要接入生產環境，請用原作實測一次。

---

## 3. 統一的會話生命週期控制介面

### 3.1 抽象操作

```text
 ┌──────────────┐   ┌───────────────────────┐   ┌──────────────────┐   ┌────────────────┐
 │ 1 get_title  │──▶│ 2 start_new(title,    │──▶│ 3 confirm_started │──▶│ 4 archive_self │
 │ 取得目前名稱  │   │   brief)              │   │ 確認新會話已存在   │   │ 封存舊會話      │
 └──────────────┘   └───────────┬───────────┘   └────────┬─────────┘   └────────────────┘
                                │ 失敗／被拒              │ 無法確認
                                ▼                        ▼
                         不封存，說明原因         不封存，說明原因
```

不變式（所有環境一致）：

1. **先確認、後封存**：沒有看到新會話確實建立的證據，就不得封存舊會話。
2. 新名稱由舊名稱機械產生（第 3.3 節），不要重新命名。
3. brief 要能獨立閱讀（第 3.4 節與範本）。
4. 使用者只說一個字（「換」「開新」「new」「handoff」）就直接做，不再追問；若是 hook 判定的新話題，先給選項（開新對話／在這裡做），選「在這裡做」就不開、不封存。

### 3.2 各環境對應與降級

| 環境 | get_title | start_new | archive_self | 狀態 |
| :--- | :--- | :--- | :--- | :--- |
| Claude 桌面版（Code 分頁） | `get_session(session:"self")` | `start_session(context:"fresh", title, brief)`；要跳按鈕用 `initiation:"offer"` | `archive_session(session:"self")` | 工具名稱與參數**僅見於原作 skill，官方文件查無，未驗證**。官方有文件的只有：請 Claude 封存 session、側欄選單 **Archive** |
| Antigravity | 由代理程式自己的對話識別（環境變數）取得，細節見 `docs/agent-dispatch.md` | `language_server.exe agentapi new-conversation`（本 repo 紀錄：建立頂層新對話） | Connect-RPC `UpdateConversationAnnotations`，`annotations.archived=true`，並帶 `mergeAnnotations=true` 保留標題 | **未對照廠商文件**，僅有本 repo 內部紀錄 |
| Claude Code 純終端機 | `/rename` 可改名（官方 costs 頁） | 無對應工具；官方做法是 `/clear` 之後用 `/resume` 回到舊對話 | 無封存概念 | 降級為輸出 brief 文字，請使用者貼到新對話 |
| Codex | 未驗證 | 未驗證 | 未驗證 | 降級為輸出 brief 文字 |

降級順序（由上而下，任何一步失敗就退到下一步，不要跳過確認去封存）：

```text
 能呼叫建立＋封存工具 ──▶ 完整交接（建立 → 確認 → 封存）
        │ 工具不存在／被拒
        ▼
 只能建立不能封存     ──▶ 建立後告訴使用者「舊對話請手動封存」
        │ 連建立都不行
        ▼
 純文字降級           ──▶ 輸出四段式 brief（範本），由使用者貼到新對話；舊對話不動
```

### 3.3 會話命名規則

取名稱**最後一個連續數字**加 1，其餘照抄；沒有數字就補 `-2`；保留前導零的位數。工具與原作範例一致（以下每一行都由 `title` 子命令實際算過，且範本內的範例有測試逐筆驗證）：

```text
$ python tools/verify_session_token_sentinel.py title "對話-3"        -> 對話-4
$ python tools/verify_session_token_sentinel.py title "Yoto 網站 9"   -> Yoto 網站 10
$ python tools/verify_session_token_sentinel.py title "SEO 調整"      -> SEO 調整-2
```

限制：名稱結尾若本來是年份或版本號（「報告 2025」）會被當流水號加 1；有這類名稱時請在名稱後面另加流水號（「報告 2025-1」）。

### 3.4 Brief 的四段式結構

詳見範本。重點：已完工項目（含 commit SHA、PR、檔案）、未完工與卡點、下一步待辦、環境偏好與全域約束；每段都要能獨立閱讀，禁止「如上所述」這類回頭指涉。

---

## 4. 已知限制與留給實作者的決定

1. 本工具只驗證**演算法與介面契約**，沒有在真實 Claude Code 工作階段內端對端執行過 hook（僅以假 stdin 驅動）。實際接入前請在一個拋棄式專案內觀察一次，並用官方的 debug log 確認 hook 輸出被接收（hooks 參考「Debug hooks」）。
2. 150k／50k 沒有外部依據（第 1.3 節）。
3. 第 3.2 節桌面版與 Antigravity 的工具介面未對照官方文件；介面改版時以官方為準。
4. 壓縮／清空後的級距重設不在本文範圍（第 2.4 節）。
5. 語意判定的最終品質取決於 Claude 對提示的遵循，hook 無法保證；啟發式規則只能做回歸測試。

---

## 5. 驗收與自我檢查清單

- [ ] 門檻、步進是正整數，且門檻小於你模型的自動壓縮邊界
- [ ] `session_id` 在拼路徑前有白名單驗證
- [ ] 壞 stdin、缺欄位、整份壞檔、錯誤的命令列參數（包含 argparse 錯誤）都是 exit 1，絕不是 2
- [ ] 量不到 usage 時工具不會回報通過
- [ ] 級距邊界用 `simulate --expect` 驗過（至少含：門檻前一刻、剛好門檻、同級距內、下一級起點）
- [ ] 封存永遠排在「確認新會話已建立」之後

---

## 6. 重現本文的驗證指令

在 repo 根目錄：

```bash
python -m unittest tests.test_verify_session_token_sentinel
python tools/verify_session_token_sentinel.py simulate --tokens 100000,150000,160000,199999,200000,250000 --expect silent,notify,inject,inject,notify,notify
python tools/verify_session_token_sentinel.py check <你的 transcript.jsonl> --expect notify
```

用假資料手動驅動 hook（stdin 是官方格式的 JSON）：

```bash
printf '%s\n' '{"type":"assistant","message":{"usage":{"input_tokens":6,"cache_read_input_tokens":171000,"cache_creation_input_tokens":2000}}}' > t.jsonl
echo '{"session_id":"demo-1","transcript_path":"t.jsonl","hook_event_name":"UserPromptSubmit","prompt":"hi"}' \
  | python tools/verify_session_token_sentinel.py hook --state-dir ./state     # exit 0，輸出含 systemMessage（第一次）
# 同一指令再跑一次：只有 additionalContext，沒有 systemMessage
echo '{oops' | python tools/verify_session_token_sentinel.py hook --state-dir ./state   # exit 1，stderr 說明
```

---

## 7. 結論

長對話的成本是「每輪重送上下文」造成的二次成長，換新對話的價值在於把起點從 `C` 降到 `B`。工程上最容易出錯的不是演算法，而是邊界：視窗截斷、型別不符、狀態檔、`session_id` 入路徑、壞輸入被靜默吞掉。本規範把這些邊界逐項列出並用測試鎖住；封存永遠在確認新會話建立之後。

---

## 8. 來源（查證日期 2026-11-02）

1. Claude Code hooks 參考：<https://code.claude.com/docs/en/hooks.md>（UserPromptSubmit、Common input fields、JSON output、Exit code、SessionStart／SessionEnd）
2. Claude Code 成本管理：<https://code.claude.com/docs/en/costs.md>（Reduce token usage、`/clear`、`/rename`）
3. Prompt caching：<https://code.claude.com/docs/en/prompt-caching.md>（快取存活時間、壓縮與未命中）
4. Model configuration：<https://code.claude.com/docs/en/model-config.md>（上下文視窗、auto-compact window、Haiku 5.5 長提示計價）
5. Claude Code Desktop：<https://code.claude.com/docs/en/desktop.md>（Archive a session、請 Claude 重新命名或封存 session）
6. 原作 `littlehole2025/claude-saver` commit `434750eb61510db40d567617862800f4fde2f65c`：`hooks/long-chat-reminder.js`、`hooks/hooks.json`、`skills/handoff/SKILL.md`、`README.md`：<https://github.com/littlehole2025/claude-saver/tree/434750eb61510db40d567617862800f4fde2f65c>
7. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*：<https://arxiv.org/abs/2307.03172>
8. 本 repo [`docs/agent-dispatch.md`](agent-dispatch.md)（Antigravity 介面的內部紀錄，未獨立驗證）
9. 原貼文（Threads）：<https://www.threads.com/@my.little.hole/post/DfKaSZSGatE>——**未開啟驗證**（需要登入或動態載入），其內容僅經由筆記轉述，本文不引用其中任何數字。
