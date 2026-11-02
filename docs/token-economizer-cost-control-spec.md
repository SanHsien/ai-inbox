# TokenEconomizer 黑盒成本控制手冊：Micro-Skill 注入、工具裁剪與死循環熔斷

> 任務：`T-20261031-43`｜來源筆記：[`notes/2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md`](../notes/2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md)（原文為 Threads 貼文，轉述微軟研究院與 UC Berkeley 的論文）
> 配套工具：[`tools/audit_agent_tool_pruning.py`](../tools/audit_agent_tool_pruning.py)（第 5 節）｜測試：[`tests/test_audit_agent_tool_pruning.py`](../tests/test_audit_agent_tool_pruning.py)
> 查證日期：2026-11-02。外部事實的標記：「論文」= arXiv 2610.22732v1 全文；「README」「PLUGIN.md」= 官方 repo 固定在 commit `85a8247bf4fc276a6f681446c359d7ca021b83b9` 的檔案；「本 repo 取捨」= 本文自訂、沒有來源也沒有量測的數字。

---

## 1. 這份手冊讓你能做什麼

1. 看懂論文真正主張了什麼、哪些數字有原文可查（第 2、3 節）。
2. 判斷自己的 Coding Agent 用量是否值得做成本控制，並用同一套會計方式算成本（第 3 節）。
3. 照步驟設計三個機制：經驗微技能（第 4 節）、工具裁剪（第 5 節，附可執行的審查工具）、死循環熔斷（第 6 節）。
4. 知道筆記裡哪些說法在原文找不到，不要照抄（第 2.2 節）。

## 2. 出處與筆記的出入

### 2.1 一手來源

| 項目 | 內容 |
| :--- | :--- |
| 論文 | *TokenEconomizer: Experience-Driven Black-Box Cost Control for Coding Agents*，Aaron J. Li 等（UC Berkeley、Microsoft Research、Microsoft Security），arXiv:2610.22732v1，2026-10-15 |
| 程式碼 | `github.com/microsoft/TokenEconomizer`（Apache-2.0），本文固定在 commit `85a8247bf4fc276a6f681446c359d7ca021b83b9`（2026-11-01） |
| 論文摘要的主結論 | 在 Claude Code、Codex、GitHub Copilot CLI 搭配前沿模型下，平均 token 成本降低 18.4–30.9%，任務成功率相當；Web-Bench 與資安稽核類任務降低 6.4–21.2% |
| README 補充 | 30 個「repo × agent-model」格子全部變便宜；Pass@1 在 5 個設定中有 4 個上升（Opus 4.8 下降 1.0 個百分點，論文 4.2 節） |

實驗設定：5 組 agent-model，277 個 SWE-Bench 任務、6 個 repo，每個 repo 內依時間順序跑，控制器只能從先前任務學習；成本含控制器自己的所有模型呼叫（論文 4.1 節、附錄 E）。

### 2.2 筆記中原文找不到的說法

下列內容出現在筆記，但我在論文（關鍵字搜尋全文，並讀過第 2、3 節與附錄 C、E、F、H）與 repo 的 README、ARCHITECTURE.md、PLUGIN.md、toolprune 與 loopguard 的 README 都找不到對應文字，**本手冊不採用**：

| 筆記說法 | 查證結果 |
| :--- | :--- |
| 「超過 40% 的 Token 開銷屬於結構性無效消耗」 | 找不到。論文量到的是：重複動作占 tool 呼叫收發位元組的 12–28%（附錄 B 配對方法），失敗任務占 17% 任務、32% 花費，失敗特徵重複後的花費占 51%（論文 2.2 節）。三者定義不同，不能合成 40% |
| 「Micro-Skill 以 <150 Token 取代數萬 Token」「2~4 行」 | 找不到。論文把每個 micro-skill 描述為「一行操作事實」（one-line operational facts），整組渲染成插在 system 指令與任務描述之間的短手冊，沒有給 token 上限，也沒有「2~4 行」 |
| 「冷啟動探索 5~15 輪」「Schema 佔 3,000~8,000 tokens」「每輪減少 3,000~6,000 tokens」 | 找不到。論文實測的是 23 個工具 schema 每輪都送，沒有一個 repo 呼叫超過 7 個，16 個從未被呼叫，3 個占 98% 的呼叫（論文 2.2 節）；沒有給 schema 的 token 數 |
| 「兩階段工具暴露：探索階段只給唯讀工具，實作階段才開放編輯」 | 找不到。原做法是跨任務累積證據：連續數個任務沒被呼叫的工具才遮蔽，核心工具（shell、讀、寫、編輯）永遠保留（論文 3.2 節） |
| 「連續 2 次同質報錯即強制打斷」「編輯距離與嵌入相似度」 | 找不到，而且與原文方向相反。原文用「錯誤特徵」（第一行錯誤訊息去掉數字、記憶體位址、路徑）比對，且指出 50 個成功的執行中有 36 個也出現過重複特徵，所以重複本身不能判定卡住，要交給判斷模型（論文 2.2、3.3 節、附錄 F） |
| 「語意死循環熔斷」會自行結束分支 | 論文實驗版是重導一次後仍卡住就終止；**外掛版從不終止回合**，只通知使用者（PLUGIN.md 第 2 節） |

結論：筆記把方向講對了（三個機制、成本降幅區間），但細節數字多半是補寫的。要引用請引論文或本手冊第 3 節的數字。

## 3. 成本從哪裡來

### 3.1 論文的會計方式

每個任務的有效成本（論文附錄 E，式 (4)）：

```text
C_eff(i) = w_u·N_u + w_c·N_c + w_o·N_o + H_i
           未快取輸入   快取讀取   輸出     控制器自己的模型呼叫（提案、判斷、重導文字）
```

`w_*` 是各 token 類別的單價（或相對權重）。重點有兩個：快取讀取通常比新輸入便宜，所以「省了多少 token」不等於「省了多少錢」；控制器的花費要算進去，否則優化看起來會比實際便宜。

### 3.2 三種可移除的浪費（論文第 2.2 節，60 個剖析任務）

| 浪費 | 論文量到的數字 | 對應機制 |
| :--- | :--- | :--- |
| 同 repo 內重複的操作 | 在至少一半任務出現的動作，占工具呼叫收發位元組的 12–28%；與先前任務相同的呼叫比例，從第 2、3 個任務的 14%，升到前面已有 5 個任務之後的 30%；對照組（用別的 repo 的歷史）只有 7% | Micro-skills |
| 載入卻沒用的工具 | 每輪載 23 個 schema；沒有 repo 呼叫超過 7 個；16 個從未呼叫；3 個占 98% 呼叫 | 工具裁剪 |
| 失敗與死循環 | 10 個失敗任務占 17% 任務、32% 花費；45 條軌跡重複過先前的失敗特徵，51% 的花費發生在第一次重複之後；但 50 個成功執行中 36 個也重複過 | 死循環熔斷 |

三個機制各自單獨使用時，Claude Code + Sonnet 5 的 SWE-Bench 成本變化為：micro-skills −11.8%、工具裁剪 −13.2%、失敗迴圈守衛 −7.1%、三者合併 −23.6%；Opus 4.8 為 −14.3%、−17.7%、−5.4%、−30.9%（論文 Table 2a）。可見三者大致可疊加，工具裁剪單項最大。

### 3.3 用來估算自己值不值得做的簡化模型

下面是**本文從式 (4) 推出的估算，不是論文公式**：

```text
工具裁剪省下的 token（上限）≈ Σ(被拒絕工具的 schema token) × 請求次數
```

這是上限：每次 API 請求都會重送工具定義，但實際付費要乘上快取折扣；而且改了工具清單，已快取的前綴會失效（第 5.4 節）。`tools/audit_agent_tool_pruning.py` 的 `expected_savings` 就用這個式子，並明說未計快取折扣。

## 4. Micro-Skill 經驗沉澱管線

### 4.1 流程

```text
 已完成的 session / 任務
        │  每 k 個完成後
        ▼
 ① 摘要 digest：指令樣板、測試呼叫、編輯過的檔名、遇到的錯誤（不含解答）
        │
        ▼
 ② 提案：模型根據 digest 提出少量候選事實；每條附可程式檢查的偵測器
        │
        ▼
 ③ 驗證：之後每個 session 用偵測器檢查「事實被用到嗎、被推翻了嗎」
        │
   confirmed（多次獨立證據）──── 被推翻 ───▶ retired（永不再啟用，可用新 ID 重提）
        │
        ▼
 ④ 注入：session 開頭放進短手冊（additionalContext 或 prompt 前綴）
```

### 4.2 數字與出處

| 項目 | 論文（SWE-Bench 實驗） | 外掛預設（README、PLUGIN.md） |
| :--- | :--- | :--- |
| 提案頻率 | 第 4 個任務後，之後每 5 個 | 每 3 個 session（`microskills_propose_every`），預設**關閉**，因為提案器多花模型呼叫 |
| 摘要視窗 | 最近 8 個任務，每次最多 4 個候選，至少引用視窗內 2 個任務 | README 未列 |
| 啟用條件 | 在編輯檔案集合互不重疊的 3 個任務上被確認，且需求率 ≥ 0.4（至少 4 次）才注入 | 「3 個 session 確認才在開頭陳述，後續被推翻就丟棄」 |
| 退休 | 支持分數 q_i(f) < 0，或高風險技能（如測試指令）第一次被推翻 | 同上方向 |
| 資安稽核類 | 每個任務換 repo，無處累積，所以停用 | — |

支持分數（論文式 (2)）：`q_i(f) = Σ_{j<i} γ^{i-j} · ( 1[j 確認 f] − λ·1[j 推翻 f] )`，γ<1 讓舊證據衰減，λ>1 讓一次推翻抵過一次確認。Table 4 把 γ、λ 列為「0.8, 5」，但 PDF 文字擷取把希臘字母弄丟了，**哪個數字對應哪個符號我沒能從擷取文字確認**，要引用請看原圖表。

### 4.3 在你自己的 repo 怎麼做

1. 事實只寫「這個 repo 的環境怎麼用」：測試指令的正確拼法、需要的環境變數、先要跑的建置步驟、產生檔位置。不要寫通用常識。
2. 每條事實附一個檢查方式（正規表示式或條件），否則無法判斷被推翻。沒有檢查方式的事實不要自動注入，只能人工維護。
3. 單次注入的量：**本 repo 取捨**，每條事實 1 行、整段不超過 4 行；這是為了讓注入成本遠小於它省下的探索，沒有量測依據。超過就先退休最久沒被用到的。
4. 注入一律放在 session 開頭，session 中途不改，原因同第 5.4 節（前綴變動會讓快取失效）。外掛的實作也是這樣（PLUGIN.md 第 3 節）。
5. 事實來源是指令輸出時，輸出內容可被 repo 控制（可能含惡意文字）。外掛因此預設關閉；自己做就要人工審過再啟用。

## 5. 工具裁剪

### 5.1 原作怎麼做

- 核心工具（shell、讀、寫、編輯）永遠保留；其他工具「連續 3 個任務沒被呼叫」才遮蔽，另外有每任務一次的判斷模型評估「從未被呼叫」的工具是否與這個任務無關；每 5 個任務重新載入完整清單做一次覆查，覆查中被呼叫的工具永不再遮蔽（論文 3.2 節、Table 4、附錄 F）。
- 外掛版沒有任務描述、也從不呼叫模型來裁剪，**只看證據**：工具在 `toolprune_evidence`＝10 個 prompt、橫跨至少 `toolprune_min_sessions`＝2 個 session 沒被用，或 `toolprune_sessions`＝5 個 session 沒被用，才列入；`NotebookEdit` 要三倍證據；曾經用過的工具、受保護工具永不列入。實測：把 10 個 prompt 的規則放寬成只看 1 個 session，會誤裁 7 次，原規則 1 次（PLUGIN.md「Counting prompts, 2026-10-24」表格）。
- 外掛等使用者所有 session 閒置 `toolprune_quiet_minutes`＝60 分鐘才寫入拒絕清單，原因見第 5.4 節。

### 5.2 Claude Code 的 `permissions.deny` 語法

下列來自 Claude Code 官方權限文件（<https://code.claude.com/docs/en/permissions>，2026-11-02 讀取）：

- 規則格式是 `Tool` 或 `Tool(specifier)`。**只有工具名、沒有括號**的 deny 規則會把該工具從 Claude 的 context 整個移除，Claude 看不到它。
- 帶括號的規則（如 `Bash(rm *)`）只是工具仍在、符合的呼叫被擋，**不會省 schema token**。
- 必須用正式工具名；畫面上顯示的標籤（例如 `Stop Task`）不是名稱，正式名是 `TaskStop`。
- MCP 工具名形如 `mcp__<server>__<tool>`；工具名位置也接受 glob，例如 `mcp__*`。帶括號的 `mcp__` 規則會被忽略並警告。
- 規則的評估順序是 deny、ask、allow，deny 優先；allow 不能替 deny 開例外。

因此本工具只產生**裸工具名**規則。Codex 與 Copilot CLI 的對應機制不同（Codex 以 `.codex/config.toml` 關閉能力包，Copilot 的 `permissions.deny` 只擋執行、不省 schema，要用啟動旗標或排除整個 MCP server），本手冊與工具都**不處理**這兩者（README、PLUGIN.md）。

### 5.3 哪些工具不建議拒絕

論文只保證「shell、讀、寫、編輯」永遠保留。外掛另外保護真人會用的工具（`AskUserQuestion`、規劃模式、子 agent、網路，PLUGIN.md 第 2 節的 Pruning candidates 列）。本工具的 `PROTECTED_TOOLS` 取兩者聯集，**遇到就略過並在報告裡說明原因**，不會默默不列：

| 工具 | 為什麼保護 |
| :--- | :--- |
| `Bash`、`Read`、`Edit`、`MultiEdit`、`Write`、`Grep`、`Glob` | 基本工作面；拒絕後 agent 幾乎做不了事 |
| `AskUserQuestion`、`EnterPlanMode`、`ExitPlanMode` | 真人 session 會用來提問與規劃 |
| `Agent` | 委派子 agent；子 agent 用到的工具也算「有在用」 |
| `WebFetch`、`WebSearch` | 真人工作常需要上網；無頭 benchmark 才可以預設拿掉 |

這個名單是本 repo 的保守取捨，依 TokenEconomizer 的名單與外掛文件整理，不是 Claude Code 官方的建議。

### 5.4 為什麼不能隨時寫入拒絕清單

PLUGIN.md 在 Claude Code 2.1.307 等版本實測（對本機假 API，未花真實模型費用）：session 啟動時就存在的拒絕清單會讓請求少送這些工具；已在跑的 session 維持原樣；但**接續舊對話**（`claude --continue`）會用新的工具清單，整段歷史前綴要重新寫入快取而不是讀取。所以：

1. 修改拒絕清單的時機是「這個 repo 的 session 都閒置夠久」之後。
2. 官方權限文件則寫「於 session 中途新增裸名稱 deny 規則，Claude 從下一次工具呼叫起就不能呼叫該工具」。兩者講的層次不同（能不能呼叫 vs. 請求裡有沒有 schema），我沒有自行驗證哪個在你的版本成立，所以工具只輸出建議，不自動寫入設定檔。

### 5.5 `audit_agent_tool_pruning.py` 用法

```text
python tools/audit_agent_tool_pruning.py S1.jsonl S2.jsonl ... --catalog catalog.json
python tools/audit_agent_tool_pruning.py S*.jsonl --catalog catalog.json --json
python tools/audit_agent_tool_pruning.py S*.jsonl --catalog catalog.json --deny-out deny.json
```

輸入：

- 每個 transcript JSONL 算一個 session。解析規則對照 TokenEconomizer 的 Claude Code 讀取器（`tokeneconomizer/trace/claude.py`，同一個 commit）：只讀 `assistant`、`user` 條目（其他類型如 `api-request-blob` 會重複呼叫）；`tool_use` 以 `id` 去重（互動 transcript 一個內容區塊一個條目）；真人 prompt 要排除 `tool_result`、`isMeta`、`isSidechain`、`isCompactSummary`、本地指令輸出、中斷標記。
- `--catalog`：JSON 物件 `{"工具名": schema_token 數或 null}`。**transcript 只記錄呼叫過的工具、不記錄 session 載入了哪些工具**（PLUGIN.md：「An interactive transcript does not record the tool list a session loaded」），所以沒有目錄就不知道哪些工具「從沒被呼叫」；此時只輸出統計，不產生拒絕清單。schema token 數要自己量，工具不編造；填 `null` 代表未量測，節省估算會明說這部分沒算。

建議規則與門檻（具名參數，預設值借自 TokenEconomizer 外掛的預設，**不是本 repo 量測**）：

| 參數 | 預設 | 意義 |
| :--- | ---: | :--- |
| `--min-prompts`（`min_prompts`） | 10 | 工具沒被用的證據：總 prompt 數 |
| `--min-sessions`（`min_sessions`） | 2 | 上列 prompt 要橫跨幾個有 prompt 的 session |
| `--fallback-sessions`（`fallback_sessions`） | 5 | 或有 prompt 的 session 數達到此值 |

預設值寫成設定就是 `min_prompts=10`、`min_sessions=2`、`fallback_sessions=5`（測試會核對文件與程式碼一致）。

以上三個條件取 (`min_prompts` 且 `min_sessions`) 或 `fallback_sessions`；`NotebookEdit` 的 `min_prompts` 與 `fallback_sessions` 乘 3。工具在整批紀錄裡呼叫過一次，就永遠不建議。

失敗行為（結束碼 2，不輸出報告）：空檔、純空白、壞 JSON（錯誤訊息帶檔名與行號）、不是 UTF-8、行不是物件、條目缺 `type`、`assistant`/`user` 缺 `message.content`、`tool_use` 缺字串 `name`、整批沒有任何真人 prompt、目錄格式錯誤（含工具名帶括號或 `*`，那會變成別的規則）、門檻不是 ≥ 1 的整數。「沒有任何建議」是正常結果，結束碼 0。

範例（假資料；2 個 session、共 10 個 prompt，目錄如 `{"Read": 640, "Bash": 1100, "Edit": 700, "NotebookEdit": 520, "WebSearch": 300, "mcp__github__create_issue": 420, "mcp__playwright__browser_click": 380}`）：

- `mcp__github__create_issue`、`mcp__playwright__browser_click` 證據足夠且沒用過，列入。
- `Edit`、`WebSearch` 沒用過但受保護，略過並說明。
- `NotebookEdit` 需要 30 個 prompt，只有 10 個，略過並說明證據不足。
- 預估：每次請求省 800 schema tokens，窗口內 10 次請求約省 8,000 tokens（上限，未計快取折扣）。

產生的片段（`--deny-out`，已有同名檔不會合併，請自行合併進 `.claude/settings.local.json` 的 `permissions.deny`）：

```json
{
  "permissions": {
    "deny": [
      "mcp__github__create_issue",
      "mcp__playwright__browser_click"
    ]
  }
}
```

### 5.6 使用後的檢查與回復

1. 套用後用 `/permissions` 確認規則已載入（PLUGIN.md 以此確認過規則讀入）。下一個請求實際少送了哪些工具，transcript 看不出來（它不記載入的工具清單），要靠 API 請求紀錄；本手冊與工具都沒提供這項量測。
2. 之後再用本工具審查新的紀錄；若原本被拒絕的工具變成需要，把它從 `deny` 拿掉即可，這是 TokenEconomizer「可還原」原則（README 的 Keep every action reversible）。
3. 原作每 5 個任務重載完整清單做覆查，因為只看「沒被呼叫」會誤判（拒絕後它當然沒被呼叫）。**本工具看的是拒絕之前的紀錄**；對已經拒絕過的環境，要先暫時移除拒絕規則跑一段，再審查。

## 6. 死循環熔斷

### 6.1 論文的做法

```text
 每次工具呼叫之後
        │
        ▼
 規則閘（不呼叫模型）：重複的失敗特徵？錯誤輸出密集？超過回合預算 B？
        │ 有跡象
        ▼
 判斷模型（看最近動作與計數器的摘要，不看全文）
   ├─ 卡住且信心 ≥ 0.7 ──▶ 重導一次（動作摘要 + 請換個假設）
   │                          └─ 重導後仍卡住 ──▶ 論文：終止；外掛：只通知使用者
   └─ 有進展 / 不確定 ───▶ 繼續，不打斷
 備援（判斷模型不能否決）：回合數 ≥ β·B 且「嚴格停滯規則」成立 ──▶ 終止
```

論文與 repo 的數值（Table 4、附錄 F、README Settings）：

| 項目 | 數值 | 說明 |
| :--- | :--- | :--- |
| 回合預算 B | 1.25 × 該 repo 過去成功任務回合數的第 90 百分位 | 式 (3)；用百分位不用最大值，避免單一超長成功拉高；Web-Bench 任務太少，改用預先登記的 30 回合直到 5 個任務成功 |
| 判斷信心門檻 | 0.7 | README：`loopguard.judge_confidence` |
| 重導次數 | 1 | 論文「1, then stop」；外掛 `loopguard_nudges`＝1 且從不終止 |
| 強制停止倍率 β | 2.5 | 回合數達 β·B 且嚴格停滯規則成立 |
| 嚴格停滯規則 | 三條同時成立：編輯搖擺（同一檔 ≥ 4 次編輯，或 ≥ 3 個檔被編輯）、錯誤輸出密集（≥ 6 次）、重複（≥ 20% 的失敗輸出重複先前失敗特徵） | 附錄 F |
| 判斷模型呼叫頻率 | 觸發時最多每 5 回合一次；每次判定有進展後間隔加 5，上限 20 | 附錄 F |
| 外掛學習期 | 該 repo 先累積 `loopguard.envelope_min_samples`＝5 個正常結束的回合才啟動 | README |
| 實際動作頻率 | 判斷模型每個 stream 約被問 10–13 次；重導約每 10 個任務 1 次，終止不到每 20 個任務 1 次 | 論文附錄 H（Claude Code 設定） |

### 6.2 錯誤特徵怎麼正規化

論文附錄 F：取失敗工具輸出的**第一行錯誤訊息**（traceback、失敗測試、斷言），把數字、記憶體位址、檔案路徑拿掉，讓「同樣方式失敗」的兩個輸出相等。自己實作時可用：

```text
 原文：  AssertionError: expected 3 got 5 at ./tests/test_a.py:42
 正規化： AssertionError: expected <N> got <N> at <PATH>
```

兩次正規化後相等就算同一特徵。這是對論文描述的**我方詮釋**，原作的正規式細節沒有在論文正文給出，需要完全相同就讀 repo 的 `loopguard/state.py`（本文沒讀）。

### 6.3 不要這樣做

- **不要用「連續 N 次同樣錯誤就打斷」當唯一條件。** 論文量到 50 個成功執行中有 36 個也出現過重複特徵，超過一半在重複之後的花費最終仍成功；這種規則會打斷本來會成功的執行。
- 沒有判斷步驟就不要自動終止。外掛版選擇只通知使用者，原因是並非每個 agent 的 hook 都能終止回合，且由使用者決定（PLUGIN.md 第 2 節）。
- 預算要來自「該 repo 自己成功過的回合數」，不要用全域固定上限；論文舉例 Matplotlib 失敗回合 45 vs 成功 20，Sphinx 36 vs 31，同一個固定上限對兩者都不對。

## 7. 導入順序建議

```text
 第 1 步  量測          用 audit_agent_tool_pruning 看工具使用，記錄每次請求 token（含快取欄位）
 第 2 步  工具裁剪      風險最低、單項效益最大（論文 Sonnet 5 −13.2%，Opus 4.8 −17.7%）
 第 3 步  熔斷（通知）   先只通知，不終止；累積 5 個正常回合後再啟用
 第 4 步  Micro-skills  最後，且人工審過每條事實
```

這個順序是本 repo 的建議，依據是各機制單項效益與風險（第 3、4 節）；論文沒有規定導入順序。

## 8. 限制與未驗證

- 本文沒有在自己的環境重跑論文實驗，所有節省比例都是論文或 README 的數字，不是本 repo 量測。
- 沒讀的原始碼：`loopguard/` 與 `microskills/` 的實作；僅讀了論文、README、ARCHITECTURE.md、PLUGIN.md 以及 `toolprune/README.md`、`toolprune/tools.py`、`loopguard/README.md`、`trace/claude.py`。
- 論文 Table 4 的 γ、λ 符號對應（第 4.2 節）：文字擷取後無法確認。
- Claude Code 對「中途新增 deny」的實際行為（第 5.4 節）：兩份來源描述不同層面，未自行驗證。
- 本工具的 token 占比用「輸入 JSON 字元數 ÷ 4」估算（`chars_per_token`＝4，啟發式，本 repo 取捨），只反映呼叫輸入，不含工具回傳內容，也不是計費 token。
- 本工具沒有處理 subagent 另存的 transcript 檔；若子 agent 檔案要算，請把它們一起傳入（它們會被當成各自的 session，且沒有 prompt 的 session 不計入證據）。
- 論文與外掛都是 2026-10 的新資料，repo 持續更新；以上以固定 commit 為準。

## 9. 來源

查證日期 2026-11-02。

1. 論文：<https://arxiv.org/abs/2610.22732>（摘要頁與 PDF 全文 <https://arxiv.org/pdf/2610.22732>）。
2. 官方 repo（固定 commit）：<https://github.com/microsoft/TokenEconomizer/tree/85a8247bf4fc276a6f681446c359d7ca021b83b9>，檔案：`README.md`、`docs/ARCHITECTURE.md`、`docs/PLUGIN.md`、`tokeneconomizer/toolprune/README.md`、`tokeneconomizer/toolprune/tools.py`、`tokeneconomizer/loopguard/README.md`、`tokeneconomizer/trace/claude.py`。
3. Claude Code 權限文件：<https://code.claude.com/docs/en/permissions>（Permission rule syntax、Tool name wildcards、MCP、Rule evaluation 各段）。
4. 筆記的 Threads 貼文連結（`threads.com`）：**未驗證**（需要登入，我沒有開啟內容）；筆記對論文的轉述以上述一手來源為準。
