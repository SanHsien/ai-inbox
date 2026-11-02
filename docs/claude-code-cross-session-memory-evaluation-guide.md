# Claude Code 跨 Session 記憶架構評測指南

> 對應任務：`T-20261031-40`｜來源筆記：[`notes/2026-10-31-claude-code-cross-session-memory-claudemem-vs-claudemd.md`](../notes/2026-10-31-claude-code-cross-session-memory-claudemem-vs-claudemd.md)
> 配套：量測工具 [`tools/audit_session_memory_compression.py`](../tools/audit_session_memory_compression.py)（`T-20261031-41`）、寫入與清理範本 [`templates/cross-session-memory-curation-spec.md`](../templates/cross-session-memory-curation-spec.md)（`T-20261031-42`）。
> 查證日期：2026-11-02。外部事實都標了出處；標「未驗證」的是沒有開到一手來源的部分，不可當事實引用。
> 讀完能做的事：判斷你的專案該把哪類資訊放進哪一層、替每一層設 Token 預算、在寫入記憶前後加上機密過濾與壓縮品質檢查。

---

## 0. 先修正筆記的三個前提

筆記是線索，不是證據。對一手來源之後，三處需要改：

| 筆記的說法 | 查到的實際情況 | 出處 |
| :--- | :--- | :--- |
| 安裝指令是 `claude skill install thedotmack/claude-mem` | README（查證 commit）整份找不到這條指令（`skill install` 出現 0 次）。README 列的安裝方式是 `npx claude-mem install`，或在 Claude Code 內執行 `/plugin marketplace add thedotmack/claude-mem` 再 `/plugin install claude-mem`。**筆記那條指令未驗證，本文不採用。** | 來源 [S2] |
| claude-mem 有 83k stars | 2026-11-02 查 GitHub API 為 109,735。星數會變，只代表關注度，不代表品質。 | [S2] |
| `CLAUDE.md` 篇幅控制在 8KB 內 | 8KB 不是官方數字。官方建議是每個 CLAUDE.md「目標少於 200 行」；25KB 與 200 行這組硬上限是 **auto memory 的 `MEMORY.md`** 才有的。 | [S1] |

另外筆記漏掉一條官方路線：Claude Code 自己就有 **auto memory**（Claude 自己寫筆記，跟 CLAUDE.md 並存），下面三方對比要把它算進路線 A。

---

## 1. 三條路線的事實對照

```text
                    寫入者            進入上下文的方式                    失真來源
 A 靜態顯式        人（或 Claude）   每個 session 開場整份載入           忘了寫 = 沒發生
   CLAUDE.md /     手動更新          （auto memory 只載 MEMORY.md
   AGENTS.md /                        前 200 行或 25KB）
   auto memory
 B 自動 Hook       Hook + 背景模型    SessionStart 注入最近 N 筆；         模型摘要（有損）
   claude-mem      壓縮成觀察紀錄     之後靠搜尋工具分層取回               + 壓縮本身耗費額外 Token
 C 外部收割        人或 Agent 顯式    需要時才呼叫 CLI，靜態抽取，         非自動；需要自己想到去查
   cc-session      呼叫工具           不經模型改寫
```

### 1.1 路線 A：CLAUDE.md、AGENTS.md 與 auto memory（官方）

出處 [S1]（`code.claude.com/docs/en/memory`）：

- 每個 session 都從全新的 context 開始；跨 session 的機制有兩種：你寫的 CLAUDE.md，與 Claude 自己寫的 auto memory。兩者都在每個對話開場載入，但 Claude 把它們當作**上下文，不是強制設定**；要保證擋下某個動作，要用 PreToolUse hook。
- CLAUDE.md：建議每份目標少於 200 行；用 `@path` 匯入，最多遞迴四層；匯入只幫你整理檔案，**不會降低 Token 成本**（被匯入的檔案跟著一起載入）。專案根目錄的 CLAUDE.md 會在 `/compact` 後從磁碟重新讀入；只在對話裡講過的指示不會留下。
- AGENTS.md：Claude Code 在工作目錄與其上層**沒有** CLAUDE.md 時，才會直接讀 AGENTS.md（文件註明需要 v2.1.277 以上）。同時有兩者時只讀 CLAUDE.md，要共用就在 CLAUDE.md 放一行 `@AGENTS.md`。
- auto memory：預設開啟；存在 `~/.claude/projects/<project>/memory/`，同一個 git repo 的所有 worktree 共用，**只存在本機**。`MEMORY.md` 是索引，**開場只載入前 200 行或前 25KB（先到者為準）**，超出的部分不會載入；其他主題檔不在開場載入，需要時才由 Claude 讀取。關閉方式是 `/memory` 內切換（寫入 `autoMemoryEnabled`），或環境變數 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`。記憶檔不受 `cleanupPeriodDays` 的 transcript 清理影響，會留到有人改或刪。
- 單一 CLAUDE.md 超過 4 MiB 會整份略過。子目錄 CLAUDE.md 與路徑規則另有較小的單檔上限，**數值本次未擷取，未驗證**。

### 1.2 路線 B：claude-mem（第三方）

出處 [S2]（`thedotmack/claude-mem`，commit `52a1dfea2556e126c959c26d8e25f6fa7da14521`，2026-11-02 為 main 最新）：

- 授權 Apache-2.0。生命週期 Hook 有六種：SessionStart、UserPromptSubmit、PreToolUse、PostToolUse、Stop、SessionEnd。元件是本機 worker（HTTP API，Bun 管理）、SQLite（存 session、觀察、摘要）、Chroma 向量庫（語意加關鍵字的混合搜尋）、`mem-search` skill。
- 預設設定（`src/shared/SettingsDefaultsManager.ts`）：壓縮用的 provider 為 `claude`、model 為 `haiku`；SessionStart 注入的觀察數 `CLAUDE_MEM_CONTEXT_OBSERVATIONS` 為 50、`CLAUDE_MEM_CONTEXT_SESSION_COUNT` 為 10（變數名稱看似是 session 數，實際用途未逐行查證）；注入範圍預設只含目前專案（`CLAUDE_MEM_CONTEXT_PROJECTS=current`）；worker 預設綁 `127.0.0.1`。設定檔在 `~/.claude-mem/settings.json`。
- 搜尋是三層：`search`（回傳含 ID 的精簡索引）、`timeline`（前後脈絡）、`get_observations`（只對篩選過的 ID 取全文）。README 自述每筆索引約 50 至 100 Token、全文約 500 至 1,000 Token、可省約 10 倍；**這是廠商自述的數字，本文沒有獨立量測**。
- 隱私：README 說可用 `<private>` 標籤排除內容。原始碼 `src/utils/tag-stripping.ts` 實際處理的標籤有六種：`private`、`claude-mem-context`、`system_instruction`、`system-instruction`、`persisted-output`、`system-reminder`。
- **資料外送面要先讀**：README 說安裝程式會引導登入 claude-mem 帳號；要略過可傳明確的 `--provider`、設 `CLAUDE_MEM_ONLINE_OPTIN=false` 或在非互動環境安裝。同一個 commit 的訊息寫到，先前瀏覽器版 setup 會掃本機各 agent 歷史並在載入頁面時上傳近 30 天的 prompt 全文，該 commit 改成需明確同意才上傳。結論：把它裝到有機密的機器前，要看你裝的版本是否已含這個修正，並實際確認 provider 與同意選項。

### 1.3 路線 C：外部收割（cc-session-reader 與 mission-log）

- cc-session-reader：出處 [S3]（`Mapleeeeeeeeeee/cc-session-reader`，commit `7a60e5ce4a2be191db2f93bdd6caec8696cd0639`，Apache-2.0）。README 自述「純靜態抽取，不用 LLM」；工具呼叫、Bash 輸出、thinking 區塊被收成摘要或單行標記，使用者與助理的對話文字完整保留；`inherit` 子指令分頁輸出（每頁至多 28K 字元）。`list` 只讀 `~/.claude/usage-data/session-meta/` 的中繼資料，因此列出的比磁碟上的 transcript 少。本 repo 的整合說明見 [`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](../notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md)。
- `mission-log`：筆記提到，**本次沒有查到一手來源，未驗證**，不納入比較。

### 1.4 三方權衡

| 面向 | A 靜態顯式 | B claude-mem | C cc-session |
| :--- | :--- | :--- | :--- |
| 額外模型呼叫 | 無（auto memory 由當前 session 的 Claude 順手寫） | 有：背景觀察者每次工作都要壓縮（預設 haiku；provider 可換） | 無 |
| 失真風險 | 低但不為零：寫錯或過期的條目會一直被載入 | 較高：摘要是模型改寫，見第 2 節 | 低：保留原文；風險在過濾規則會丟掉你需要的輸出 |
| 能否自動回憶 | 是（開場載入，有上限） | 是（SessionStart 注入加搜尋工具） | 否，要顯式呼叫 |
| 機密外洩面 | 檔案在本機，風險是被 commit | 觀察紀錄含工具輸出；有外送選項（見 1.2） | 只讀本機 transcript；輸出給模型前仍需過濾 |
| 適合放什麼 | 不可妥協的規則、指令、架構決策 | 探索期的過程紀錄、很難事先分類的線索 | 要追究「上週到底怎麼解的」的深度回溯 |

建議的分工（本 repo 的取捨）：規則與已定案的決策放 A；B 只在你願意承擔第 2、3 節的檢查成本時啟用，且只當「找線索」用、不當事實來源；C 作為 B 查不到時的備援，因為它保留原文。

---

## 2. 壓縮衰減與噪聲污染

### 2.1 壓縮衰減的成因（推論，不是 claude-mem 的實測缺陷）

claude-mem 的壓縮由模型完成（預設 haiku），所以只要是模型改寫，就有下列三種已知風險。這幾條是由「摘要=改寫」推出來的，**沒有針對 claude-mem 實測**：

1. 因果丟失：寫成「修了一處正則」，沒寫「因為 CRLF 讓正則失效」。
2. 邊界模糊：把完整路徑、錯誤代碼、測試結果行改成概述（「專案筆記目錄」「測試通過」）。
3. 錯誤固化：前一輪的錯誤判斷被寫進記憶，之後每個 session 都當前提。

### 2.2 解決策略（對應到可檢查的項目）

| 風險 | 策略 | 怎麼檢查 |
| :--- | :--- | :--- |
| 因果丟失 | 記憶條目強制「根因分析」欄，且要用「因為…所以／改用…因為」的句型寫出原因 | 工具的 `decisions` 類別：原因句的詞元要在記憶同一行或同一段出現 |
| 邊界模糊 | 路徑、錯誤代碼、測試結果行**原樣**抄寫，不改寫、不縮寫 | `paths`、`error_codes`、`test_conclusions` 三類比對 |
| 錯誤固化 | 每條事實附出處（commit、transcript 位置），查不到就寫「未驗證」；寫入前後各跑一次檢查 | 工具的 `unsupported`：記憶有、原始紀錄找不到的事實會直接 FAIL |
| 越積越舊 | 條目有到期日與覆蓋規則 | 範本第 4、5 節 |

量測做法與限制見工具檔頭。重點是：資訊損失率 = 1 - 保留事實數 / 事實總數，由輸入現場計算；它只量「可抽取的」四類事實，`decisions` 用詞元重疊近似，所以換句話說會被算成損失、關鍵字拼湊可能被算成保留，**這一類要人工抽查**。預設門檻（總體損失率 0.4 等）是本 repo 的取捨，沒有外部基準，請用自己的 transcript 校準。

### 2.3 噪聲污染

開場注入越多，留給當前工作的視窗越小。具體量化（均為上面查到的數字，不是本文量測）：

- 官方 `MEMORY.md`：前 200 行或 25KB 為硬上限。
- claude-mem：預設開場注入 50 筆觀察（`CLAUDE_MEM_CONTEXT_OBSERVATIONS`），另有 `CLAUDE_MEM_CONTEXT_SESSION_COUNT=10`。
- Codex：AGENTS.md 串接鏈在 `project_doc_max_bytes`（預設 32 KiB）停止加入檔案，見 [S4]。

對策是「索引在開場、內容按需取」：開場只放一行一條的索引，內文靠搜尋或讀檔取回。這跟官方 auto memory 的設計（`MEMORY.md` 一行一條，細節放主題檔）與 claude-mem 的三層搜尋是同一個思路。

---

## 3. 跨平台記憶注入規範

### 3.1 各平台已查到的載入行為與上限

| 平台 | 載入行為 | 查到的上限 | 出處 |
| :--- | :--- | :--- | :--- |
| Claude Code | CLAUDE.md 開場載入；auto memory 只載 `MEMORY.md` | MEMORY.md：200 行或 25KB；CLAUDE.md：建議少於 200 行，4 MiB 以上整份略過 | [S1] |
| Codex | 全域與專案各層 AGENTS.md 由根往下串接，每層至多一個檔 | 串接總量預設 32 KiB（`project_doc_max_bytes`），到上限就不再加入檔案 | [S4] |
| Gemini CLI | 全域、工作區、按需（JIT）三種 GEMINI.md，串接後**每個 prompt 都送出**；可用 `context.fileName` 改檔名（可列入 AGENTS.md） | 該頁未列數值上限，**未驗證**是否另有 | [S5] |
| OpenClaw | 工作區 `MEMORY.md` 等 bootstrap 檔注入；超過「bootstrap 檔預算」時磁碟檔保持完整、只截短注入的副本 | 預算數值本次未擷取，**未驗證**；用 `/context list`、`/context detail` 看實際注入與截斷 | [S6] |

跨平台共用同一份知識時，最保守的做法是把共用核心限制在**最小的已知上限內**（目前已知最小是 Claude Code 的 25KB 與 200 行），平台專屬內容各自放自己的檔。

### 3.2 Token 預算（本 repo 的取捨，非外部標準）

```text
 開場注入總預算
   ├─ 規則層（CLAUDE.md / AGENTS.md）   每檔 < 200 行
   ├─ 記憶索引（MEMORY.md 一類）         < 200 行 且 < 25KB，每條 1 行
   └─ 自動注入的歷史（如 claude-mem）    條數設上限（claude-mem 預設 50），內文不在開場展開
 按需取回：先索引 → 再前後脈絡 → 最後才取全文（每一步都有條數上限）
```

數字沿用已查到的官方與預設值，沒有自創。要改請先在自己的 transcript 上量過再調。

### 3.3 相關度檢索規範

不指定單一演算法（各工具內部不同），但驗收時要求下列行為，並且可以用假資料測：

1. 先過濾再排序：範圍（專案）、狀態（已被覆蓋的條目不回傳）、到期（過期不回傳）。claude-mem 預設就只取目前專案。
2. 排序用關鍵字（BM25 一類）或混合檢索；同分時較新者在前。claude-mem 的做法是 SQLite FTS5 加 Chroma 混合搜尋（README 與其文件連結列出，**FTS5 細節本文未逐檔查證**）。
3. 回傳條數與總字數都有上限，並且回傳時帶出處與日期，讓模型知道新舊。
4. 命中後的內容仍視為「可能過期的線索」；動手前對照當前程式碼或檔案確認。官方文件也說 Claude 會跳過可從程式碼推得的資訊，記憶存的是推不出來的脈絡。

### 3.4 敏感憑證過濾硬閘門

寫入記憶之前、之後各一道，缺一不可：

```text
 transcript ──► [1 寫入前過濾] ──► 壓縮/寫入 ──► [2 寫入後稽核] ──► 通過才保留
                  │                                   │
        機密樣式 → 整句丟棄               audit_session_memory_compression.py
        家目錄 → 改寫成 ~                 exit 0 才算過；1 = 失敗；2 = 量不出來
        <private> 等標籤 → 移除
```

- 1 寫入前：機密樣式（GitHub／AWS／Slack／Anthropic／OpenAI 金鑰、Bearer、JWT、`password=` 一類賦值）命中就整句丟棄，不是遮罩後保留；家目錄路徑換成 `~`；claude-mem 用戶另加 `<private>` 標籤包住不該入庫的內容。
- 2 寫入後：跑量測工具。它會在記憶中發現機密樣式（`leak-secret`）、真實帳號的家目錄路徑（`leak-home-path`）、客套話開頭（`filler`）、原始紀錄查不到的事實（`unsupported-fact`）時以 exit 1 失敗；輸入壞掉或樣本不足時以 exit 2 結束，**不會當成通過**。
- 工具的偵測是樣式比對，抓不到沒有固定格式的機密（例如口語寫出的密碼）；公開 repo 另有 `python tools/verify_inbox.py` 的機密掃描。這兩者都不能保證零洩漏。
- 回報與紀錄中也不可回顯機密：工具輸出會把命中的樣式換成 `[REDACTED]`。

---

## 4. 照著做

1. 盤點：把現有記憶分三堆——規則（放 A）、已定案決策（放 A，附出處）、過程線索（B 或 C）。
2. 設預算：用 3.2 的數字當起點，用 `/context`（OpenClaw）或 `/memory`（Claude Code、Gemini）看實際載入量。
3. 啟用 B 之前：讀 1.2 最後一條，確認 provider 與是否上傳 prompt。
4. 每次產生新的壓縮記憶：用範本的 Prompt 寫入，再跑
   `python tools/audit_session_memory_compression.py --transcript <原始.jsonl> --memory <記憶.md>`；
   工具只用標準函式庫，複製這一支檔案到別的專案即可使用。
5. 每月一次依範本第 4、5 節清過期與衝突。

---

## 來源（查證日期 2026-11-02）

- [S1] Anthropic，How Claude remembers your project：<https://code.claude.com/docs/en/memory>（讀全頁，引用：auto memory 與 CLAUDE.md 對照表、載入上限、AGENTS.md、`@` 匯入、`/compact` 後行為）。
- [S2] claude-mem：<https://github.com/thedotmack/claude-mem/tree/52a1dfea2556e126c959c26d8e25f6fa7da14521>（讀 `README.md`、`src/shared/SettingsDefaultsManager.ts`、`src/utils/tag-stripping.ts`，以及該 commit 的提交訊息；星數與授權用 GitHub API 查）。
- [S3] cc-session-reader：<https://github.com/Mapleeeeeeeeeee/cc-session-reader/tree/7a60e5ce4a2be191db2f93bdd6caec8696cd0639>（讀 `README.md`；僅讀文件，**沒有執行該工具**）。
- [S4] OpenAI，Custom instructions with AGENTS.md：<https://developers.openai.com/codex/guides/agents-md>
- [S5] Gemini CLI，Provide context with GEMINI.md files：<https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md>（該檔最後修改的 commit 為 `93844dfa10f6d71edc09be40dfde205edfbcc939`）。
- [S6] OpenClaw，Memory：<https://docs.openclaw.ai/concepts/memory>
- 未驗證項目：`claude skill install thedotmack/claude-mem` 指令、`mission-log`、子目錄 CLAUDE.md 的單檔上限、Gemini CLI 與 OpenClaw 的數值上限、claude-mem 的 FTS5 實作細節與所有 Token 節省數字（廠商自述）。
