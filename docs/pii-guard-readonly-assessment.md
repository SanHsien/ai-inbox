# pii-guard 唯讀採納評估

日期：2026-11-15。對應 [T-20261115-17](../notes/2026-11-15-danyuchn-pii-guard-claude-mod-eval.md)。**裁決：暫不採納、不安裝、不掛 hook**。本輪只讀第三方檔案並執行自有靜態掃描器；未執行上游程式、安裝、測試、CLI、Mod、MCP 或內嵌指令。

## 1. 固定來源與授權

來源 [danyuchn/pii-guard](https://github.com/danyuchn/pii-guard)，固定 commit `3d55636785868785e6452e5590052571dc459659`。shallow clone 首次 schannel 失敗後，以單次 OpenSSL clone 成功，未關閉憑證驗證。暫存只放工作目錄的 `.work-tmp/`。清理時已核對絕對路徑，但自動核准審查拒絕遞迴刪除（blocked by policy，未提供細節）；交付時仍保留該暫存，未納入提交，須由整合者清理。本輪因此以 PARTIAL 回報共同守則的清理缺口。

LICENSE 為 MIT，署名 Dustin Yuchen Teng；專案授權不代表全部模型與依賴授權已完成稽核。pyproject 為 0.2.0、Python >=3.11，Mod manifest 另為 0.1.0。以下全部連結固定該 commit；SHA 是 Git blob SHA，並非 SHA-256。

| 關鍵檔案（固定來源） | Git blob SHA |
|---|---|
| [LICENSE](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/LICENSE) | `cf3b9052d36f05227a3e3c364910b9f96c86cc5f` |
| [pyproject.toml](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/pyproject.toml) | `0101f0d9592419f8e0af7daa17a914c7a23b96ab` |
| [README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/README.md) | `f5a96ec393df45ba9f240f754d1668cfe807bd03` |
| [examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md) | `a0d36daf5d1edad66560598e99106989a288435b` |
| [examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts) | `b04a8d9ffe1ba092d0eddd29118b3923862fa8a1` |
| [examples/claude-code-mod/hooks/hooks.json](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/hooks.json) | `9470ce9ba630d3a986da22a5b09a646ed3e0af86` |
| [examples/claude-code-mod/.claude-plugin/plugin.json](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/.claude-plugin/plugin.json) | `bb70d69e106471c9ee5b92931e42f71e29b4b4a3` |
| [examples/claude-code-mod/commands/pii-terms.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/commands/pii-terms.md) | `dcc76c686563e649e60d1ff20c1d6aab4d73d2b8` |
| [examples/claude-code-hook/pii-guard-read.sh](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hook/pii-guard-read.sh) | `08258dd8adf269bacf31ea32c76c74bfb560776b` |
| [examples/claude-code-hookd/pii_guard_hook_client.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hookd/pii_guard_hook_client.py) | `7453d74bfae749b32e12acbcae30fdecc878d264` |
| [examples/claude-code-hookd/settings.json](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hookd/settings.json) | `008bb64476d231286249a1bafa6cece04e8d40dd` |
| [src/pii_guard/hookd/install.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/install.py) | `8f43383f080f6bd29dacf8c16daa124b55fa4254` |
| [src/pii_guard/hookd/state.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/state.py) | `4340552d599130eece3bb889e4e5a97571d85d8e` |
| [src/pii_guard/hookd/server.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/server.py) | `c57278ce56e6807eaa9b522f0858ce8741f975d5` |
| [src/pii_guard/hookd/core.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/core.py) | `1c9851f38fe396436f158c2e9402619b4361266a` |
| [src/pii_guard/hookd/policy.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/policy.py) | `dd1950871396ef56806641ccb897c1cbed2703e6` |
| [src/pii_guard/_compat.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/_compat.py) | `4d42ff72811af9307edf6d8f4233ec560d346ab6` |
| [src/pii_guard/pipeline/engine.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/pipeline/engine.py) | `69db495dbf36fde7f779651a893f880bf4636fc9` |
| [src/pii_guard/enhanced_audit.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/enhanced_audit.py) | `52d15d903b24e36f40db79d791713403b61c0249` |
| [.github/workflows/windows.yml](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/.github/workflows/windows.yml) | `70822b167143e7838a53ecd1871527a6320d4b43` |

比較對象是本機 `SanHsien/agent-safety-checks`，HEAD `060cd3d623f9003ccf65e6652dd33cdc3234c51f`；實際讀取的 `tools/screen_privacy.py` Git blob 雜湊為 `e8e318e2f9e9f8b39c777d7da0cf2b6a600d32f5`，掃描器 `tools/verify_agent_skill_pack_safety.py` 為 `b3bfd87cc39d442860841220fa57b75cf01da9df`。以工作樹內容雜湊補足 HEAD 證據；未修改該 repo。

## 2. 去識別化與 Claude Mod 掛載資料流

```text
使用者 prompt --------> prompt.submit --+
Read/Bash/Grep 結果 ---> tool.call ------+--> Mod register.ts
壓縮前後 messages ----> session.compact +        |
                                                | state.env: port + token
                                                v
                                  HTTP POST 127.0.0.1:<port>
                                                |
                               hookd: 偵測 / 已知值掃描 / 政策
                                 |                         |
                                 v                         v
                    佔位符文字 --> 雲端模型     sessions/<id>.json（含真值）
                                 |
                 Write/Edit/MultiEdit/Bash 佔位符輸入
                                 |
                       政策拒絕 <+> 本機還原 --> 工具 --> 真值落盤

安裝 --mod（本輪未執行）
  +--> Claude settings: MessageDisplay + SessionStart --start-only
  +--> plugins/pii-guard: symlink，失敗改 copy
  +--> function hooks 旗標 + --plugin-dir --> hooks.json --> register.ts
```

Mod 本身不偵測，將事件交給 hookd；Read／Bash／Grep／MCP 結果去識別化，Write／Edit／MultiEdit／Bash 輸入可逆還原。依 policy，預設拒絕 WebFetch、WebSearch、`mcp__*`；Agent／Task／Workflow **只在** `isolation=remote` 或 `opts.isolation=remote` 被拒絕，`allowed_tools` 可放寬。Bash 用命令詞與正則判斷外連／編碼，並非完整 shell parser 或系統網路隔離。

官方安裝指引（僅記錄、未執行）是 `uv sync`、文件格式另加 `--extra formats`；`uv run pii-guard-hookd install --mod [--harden]` 會改設定，之後用 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` 與 `--plugin-dir` 載入。安裝器備份 settings 並替換自家 classic hooks，保留 MessageDisplay 向人還原真值、SessionStart 按需啟動常駐。`--harden` 可加 sandbox／外送限制，但已有 sandbox 區塊不覆寫，不保證完整硬化。少帶載入旗標可能完全沒有 Mod 防護。

依據：[examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts)、[src/pii_guard/hookd/policy.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/policy.py)、[src/pii_guard/hookd/install.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/install.py)、[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)。

## 3. 權限、落盤、外連與子程序

| 面向 | 原始碼可確認行為 | 邊界與判讀 |
|---|---|---|
| Mod home | `options.hookdHome` → `PII_GUARD_HOOKD_HOME` → `EVAL_PII_GUARD_HOOKD_HOME` → `HOME/.local/share/pii-guard/hookd` | Python 端採環境變數或 expanduser 預設；須讓兩端同一路徑。變數只選資料目錄，不提供 sandbox |
| 私有狀態 | state.json／state.env 含 port、token；sessions JSON 保存可逆對照 | 非加密、非不可逆匿名化；保護本機 mapping 與原文件同樣重要 |
| CLI mapping | engine.save_mapping 用普通 JSON write_text | 不能將 hookd 私有檔保護推廣到所有 CLI 輸出 |
| POSIX 權限 | home／sessions 0700、私有檔 0600；ensure_home 收緊既有 home | 指錯目錄可能改其權限，須核對精準目標 |
| Windows 權限 | whoami 取 SID、PowerShell 讀 ACL、icacls 設 owner／移除繼承，授權目前使用者、SYSTEM、Administrators，再讀回驗證；檢查父層與 reparse point | home 必須位於使用者設定檔內；不是僅目前使用者可讀。驗證結果每 process 有快取，chmod 數字不等於 NTFS 隔離 |
| Mod HTTP | 讀 state.env，以 bearer + Host POST loopback；失敗改 python3 -c relay | relay token 在 argv，body 在 stdin；同帳號程序威脅仍需考慮。本輪未執行 relay |
| hookd server | 固定綁 127.0.0.1、檢查 Host、常數時間比對 token、避免 request log | 未做封包或代理環境驗證；不能推廣為依賴皆零外連 |
| 常駐啟動 | classic client 讀 hookd.json 的 serve_command，以 Popen(argv)、DEVNULL、start_new_session 啟動，建立啟動鎖 | 設定與 executable 完整性是信任邊界；不是無副作用函式 |
| 安裝與 doctor | 寫 Claude settings、備份、client、plugin symlink／copy、服務設定；doctor 可啟動 claude validate | 未呼叫 install／doctor／uninstall，未更動既有 hooks |

依據：[src/pii_guard/hookd/state.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/state.py)、[src/pii_guard/_compat.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/_compat.py)、[src/pii_guard/hookd/core.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/core.py)、[src/pii_guard/pipeline/engine.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/pipeline/engine.py)、[src/pii_guard/hookd/server.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/server.py)、[examples/claude-code-hookd/pii_guard_hook_client.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hookd/pii_guard_hook_client.py)、[src/pii_guard/hookd/install.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/install.py)。

**是否送外部服務**：所讀 Mod／hookd 的傳輸目的地是本機 HTTP，未見該路徑直接將文件送到雲端去識別化 API；雲端 Claude 仍會收到遮罩後內容，漏偵測與路徑人名仍可能外露。完整引擎需要依賴與 CKIP 模型下載，不能稱安裝階段完全離線。選用加強稽核會將已遮罩但可能殘留 PII 的片段送往**本機** Ollama；此版本驗證 loopback URL，HTTPConnection 固定 127.0.0.1，另驗證 listener 為目前使用者的 ollama。Windows 明確回 `LOCAL_MODEL_UNVERIFIED`；不是可任意指定遠端服務的實作。本輪沒有下載模型或使用模型服務，也未稽核所有依賴／本機模型後端的網路行為。依據：[src/pii_guard/enhanced_audit.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/enhanced_audit.py)、[README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/README.md)。

## 4. Fail-closed 與 Edit 宣稱的界線

前端有將例外轉為 deny／drop／skip／替代結果的設計，但不支持「所有 handler 均拒絕、任何超時均不洩漏」：

- session.start 的 catch 回 undefined，主要提供離線說明，並非所有事件都 deny。
- tool.call 在 reply 缺 result 時回原 answer；prompt 缺 text、Compact 缺 messages 也保留原值。這是成功 HTTP 但回覆不完整的靜態分支，未重現其觸發。
- withholdLeaves 深度 >12 回原值，不改 object key；Read 扣留結果保留 filePath，不能保證所有欄位都遮罩。
- relay process timeout 8000ms、Python urllib timeout 15 秒；前段 fetch 在此檔未指定 timeout。加上讀 state／host dispatch 時間，不能由 catch 存在推論一定趕上作者所述 host 十秒 deadline。
- host 十秒預算、next replay-safe、ref 與 Edit 驗證順序均為上游文件／註解主張。本輪只有前端改寫輸入的證據，沒有 host 時序或實測證據，不宣稱徹底修復 Edit。
- 上游明列原 prompt 可能先落本機 transcript、路徑不遮、Compact 只掃已知值。pii-terms 禁讀名單是命令檔指引與 allowed-tools 約束，不等於已證明無法繞過的隔離。

這些是設計限制與需驗證風險，不冒充已重現漏洞。依據：[examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts)、[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)、[examples/claude-code-mod/commands/pii-terms.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/commands/pii-terms.md)。

## 5. 與 screen_privacy 的重疊與差異

| 項目 | pii-guard | screen_privacy.py |
|---|---|---|
| 輸入與位置 | 文件文字、prompt、工具結果與參數 | app／視窗標題、外部 OCR 文字；本身不截圖或執行 OCR |
| 重疊 | 台灣證號、手機、email 等偵測與文字遮罩 | 同類正則；另有供應商 key／密碼，卡號加 Luhn |
| 核心目的 | 可逆佔位符、會話對照表、工具外送政策 | 截圖前 blocked／nocap 等分類；OCR 命中機密、證號、卡號或關鍵字門檻就 drop_image |
| 方法 | Presidio、CKIP／spaCy、台灣辨識器、參考名單，模式不同覆蓋不同 | 標準庫正則與分類，不提供 NER 或可逆 mapping |
| 狀態與副作用 | 常駐服務、hook 安裝、mapping 與真值輸出 | 無常駐 hook／自動還原；遮 OCR 文字不會改圖片像素 |
| 裁決 | 保留研究價值，尚未採納 | 保留既有截圖前後關卡，不能由 pii-guard 替代 |

來源：[src/pii_guard/pipeline/engine.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/pipeline/engine.py)、[screen_privacy 原始碼](https://github.com/SanHsien/agent-safety-checks/blob/060cd3d623f9003ccf65e6652dd33cdc3234c51f/tools/screen_privacy.py)。本輪未修改安全工具、規則或既有 hooks。

## 6. 靜態審計原樣結果與逐項人工判讀

執行時設定 `PYTHONUTF8=1`：

```text
python C:/GitHub/agent-safety-checks/tools/verify_agent_skill_pack_safety.py --pack .work-tmp/pii-guard
結束碼：1
```

以下是原樣輸出，未使用 --strict、--ack-unscanned 或修改掃描內容來取得綠燈：

```text
[FAIL] .work-tmp\pii-guard：已掃描 128 個檔案，FAIL 1 項、需人工審查 6 項、未掃描 2 個
  FAIL      [REMOTE-EXEC] src/pii_guard/hookd/policy.py（第 63 行）— 遠端內容接管線執行：urllib | requests | httpx | http.client | socket | fetch( | net. | Net:: | open-uri
  REVIEW    [DYNAMIC-EXEC] .git/hooks/pre-receive.sample（第 14 行）— 執行非字面內容（內容在執行期才決定）：eval value=\$GIT_PUSH_OPTION_$i
  REVIEW    [AUTO-HOOK] examples/claude-code-hook/settings.json（/hooks/PreToolUse/0/hooks/0）— command hook（審批之外自動執行）：.claude/hooks/pii-guard-read.sh
  REVIEW    [AUTO-HOOK] examples/claude-code-hookd/settings.json（/hooks/SessionStart/0/hooks/0）— command hook（審批之外自動執行）：python3 "__HOOKD_CLIENT__" SessionStart
  REVIEW    [AUTO-HOOK] examples/claude-code-hookd/settings.json（/hooks/PostToolUse/0/hooks/0）— command hook（審批之外自動執行）：python3 "__HOOKD_CLIENT__" PostToolUse
  REVIEW    [AUTO-HOOK] examples/claude-code-hookd/settings.json（/hooks/PreToolUse/0/hooks/0）— command hook（審批之外自動執行）：python3 "__HOOKD_CLIENT__" PreToolUse
  REVIEW    [AUTO-HOOK] examples/claude-code-hookd/settings.json（/hooks/MessageDisplay/0/hooks/0）— command hook（審批之外自動執行）：python3 "__HOOKD_CLIENT__" MessageDisplay
  UNSCANNED docs/annotate-demo.gif — 未掃描：二進位檔，sha256=42e5621b9508a179398096f8fdbfbdf3e287699e71805d23859fb5d5f3ef6019
  UNSCANNED docs/annotate-ui.png — 未掃描：二進位檔，sha256=fd83eb09fee60d0d7ec2203a0c68cfd922d20c067259071547d4cc1c369448fa
  NOTE      .git：只掃 config 與 hooks/，物件庫與其餘中繼資料未掃描
[FAIL] 發現問題，見上方清單。這是靜態啟發式掃描，通過不代表安全，仍需人工審查。
```

| 項目 | 人工判讀與處置 |
|---|---|
| FAIL REMOTE-EXEC，policy.py:63 | 是 INLINE_NETWORK_PATTERN 正則字串，用來攔外連，不是管線執行遠端內容。屬啟發式誤報；保留退出碼 1，不改掃描器 |
| REVIEW DYNAMIC-EXEC，.git/hooks/pre-receive.sample:14 | Git clone 產生的 sample，非上游 tree 內 hook；未啟用／未執行，不能當作上游惡意 |
| REVIEW AUTO-HOOK，classic settings.json | `.claude/hooks/pii-guard-read.sh` 用 jq／file／grep 讀設定與判斷，最後透過 uv 啟動偵測；有多條 exit 0 跳過分支，不等同 Mod fail-closed。未安裝 |
| REVIEW AUTO-HOOK，hookd SessionStart | python3 client 連 loopback，離線時按設定啟動常駐子程序；自動執行與設定完整性需審查，未啟用 |
| REVIEW AUTO-HOOK，hookd PostToolUse | 將工具結果交 hookd 遮罩，涉及內容處理與對照表保存；未驗證 host 替換結果能力，未啟用 |
| REVIEW AUTO-HOOK，hookd PreToolUse | 還原寫入／命令參數，真值重新進工具；範例 matcher 不是完整硬化模式，未啟用 |
| REVIEW AUTO-HOOK，hookd MessageDisplay | 佔位符還原給人，終端機可能出現真值；不是截圖隱私防護，未啟用 |
| UNSCANNED GIF、PNG | 二進位非文字，不開啟、不當作驗收證據。覆蓋缺口仍存在，不能宣稱完整通過 |

判讀依據：[src/pii_guard/hookd/policy.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/policy.py)、[examples/claude-code-hook/pii-guard-read.sh](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hook/pii-guard-read.sh)、[examples/claude-code-hookd/pii_guard_hook_client.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hookd/pii_guard_hook_client.py)、[examples/claude-code-hookd/settings.json](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-hookd/settings.json)。掃描器並未列出 TypeScript 的完整 capability 清單，故另做第 3、4 節人工審閱，不能把這 6 項當成全部風險。[掃描器原始碼](https://github.com/SanHsien/agent-safety-checks/blob/060cd3d623f9003ccf65e6652dd33cdc3234c51f/tools/verify_agent_skill_pack_safety.py)。

**SkillSpector**：本機可找到 skillspector.exe，只嘗試 `skillspector --help` 即結束碼 1，輸出 `error: uv trampoline failed to canonicalize script path`。未取得掃描結果，沒有重裝或安裝依賴；雙重審計尚未完成，不能採納。這個缺口屬採納條件，不冒充成功驗收。

## 7. Windows 前提與已查／未查

| 查核項目 | 狀態 | 證據或限制 |
|---|---|---|
| 固定來源、MIT、關鍵 blob | 已查 | 第 1 節固定連結與 SHA |
| 權限／mapping／子程序／網路目的地 | 已查靜態程式碼 | 第 2、3 節，不等於執行成功 |
| --pack 與 REVIEW | 已執行並判讀 | 第 6 節結束碼 1，沒有宣稱通過 |
| Windows ACL、鎖與 CI 定義 | 已讀 | _compat 用 msvcrt；workflow 有 pytest／mypy／ruff，沒有查 CI run 或在本機執行 |
| 原生 Mod runtime、Edit 時序、十秒 deadline | 未查證 | 只有上游說明及前端原始碼，沒有 host 證據 |
| Python／uv／python3 同一環境、空白繁中路徑 | 未實測 | relay 與 classic client 指定 python3，不能假設 Windows alias 可用 |
| Mod 載入、Harness Guard／relay 相容性 | 未實測 | 未登入、未啟動 Claude 或改設定 |
| Windows Ollama 加強模式 | 靜態確認拒絕 | enhanced_audit 明確拒絕 win32，不列為已可用功能 |
| 偵測率、資源成本、圖片、依賴與後端外連 | 未查證 | 未安裝依賴或模型、未執行上游測試 |
| SkillSpector | 未完成 | 啟動失敗，沒有審計結果 |

Windows home／jobs root 須位於使用者設定檔內的 NTFS 私有目錄，父層 ACL 安全且無不安全 reparse point；服務端與 Mod 路徑要一致。上游 `VAR=1 command` 是 POSIX 語法，PowerShell 須以環境變數方式設定，不能照貼。已有 Windows CI 定義不代表本機 Mod 相容性通過。依據：[src/pii_guard/_compat.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/_compat.py)、[src/pii_guard/hookd/state.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/state.py)、[.github/workflows/windows.yml](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/.github/workflows/windows.yml)、[README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/README.md)。

## 8. 採納條件與日後動態驗證界線

裁決：保留參考設計，**不接全域 hook、不用真實客戶文件**。本輪 DoD 為唯讀報告與文件驗證；任務保留未勾選，不 complete、不 push。後續觸發條件只列 [ROADMAP](../ROADMAP.md)，以下是採納判準，不新增任務 ID。

前提：修復可信本機 SkillSpector 入口，針對相同固定版本完成雙重靜態審查；逐項確認 FAIL／REVIEW 與未掃描範圍，必要時縮小採納包。另取得隔離動態實測授權，確認模型與依賴來源符合既有服務限制，備份精準設定與回復方式，不改正式設定、不繞過 sandbox／approval。

最小驗收僅一組 `T17-SMOKE-` 前綴的合成文字，含姓名、證號、手機、email、繁中與空白路徑；不使用真實資料、不連雲端、不重建第二組樣本。先用隔離 host stub 檢查遮罩／還原、Edit 參數、loopback、檔案 ACL、離線／超時／不完整回覆。若需真實 Claude host 或任何上傳，另取得明確授權。分開核對模型側資料、磁碟、transcript，不能將 MessageDisplay 終端真值當成模型外洩；每層只取一次權威證據。

停止條件：真值進模型側、未授權外連、ACL 無法驗證、Windows alias／runtime 不支援、設定超出隔離目錄、Mod 未載入或 host timeout 行為不明，立即停測並回復隔離環境。每案例一次；狀態失效依已知方法恢復一次，第二次失敗即停，達標立即停止。timeout／缺證據記 incomplete，不算通過。本節條件尚未執行。
