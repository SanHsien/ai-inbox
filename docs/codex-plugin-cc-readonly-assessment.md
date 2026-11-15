# codex-plugin-cc 唯讀評估：Windows 權限與 hook 邊界

評估日期：2026-11-15。任務：T-20261115-15（經獨立審查改寫為唯讀評估）。作者：Claude Code。

**結論：現階段不安裝。** 三條呼叫鏈的用途已被既有的 ai-review 與 agent-relay 涵蓋，外掛多出的便利（在 Claude 對話內直接看 git 差異的原生審查、背景工作查詢）不足以抵銷它帶來的三個邊界問題：rescue 預設可寫且不鎖定可寫範圍、所有 Codex 執行都沒有逾時、Stop hook 一律註冊。本文是靜態閱讀結果，**沒有安裝、登入、啟動任何模型後端，也沒有改任何全域設定或 hooks**；凡是執行期行為都標「未實測」，不寫成相容或無衝突。

與原任務的差異：原任務要求安裝並實測 `/codex:adversarial-review`。審查後改為先做唯讀評估，本文不產生「已安裝／無衝突／比較省額度」的宣稱。

## 1. 來源與固定版本

以 `git clone --depth 1` 取得原始碼，只讀文字；未執行其中任何腳本、測試或 npm 指令。

- Repo：[openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)（Apache-2.0）
- 固定 commit：`db52e28f4d9ded852ab3942cea316258ae4ef346`（2026-07-07，`Remove shell expansion for git commands (#447)`）
- 外掛版本：1.0.6（manifest 與 `package.json` 一致）

| 代號 | 檔案（連結皆指向固定 commit） | blob SHA | 用途 |
| --- | --- | --- | --- |
| S1 | [`.claude-plugin/marketplace.json`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/.claude-plugin/marketplace.json) | `870246242b10e862119a72442e686553b62dd27b` | 市集清單 |
| S2 | [`plugins/codex/.claude-plugin/plugin.json`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/.claude-plugin/plugin.json) | `e91e5238c2a1cd02bf9d52d6f007aba53a6bca30` | 外掛 manifest |
| S3 | [`plugins/codex/hooks/hooks.json`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/hooks/hooks.json) | `19e33b818d143aa7bdb666ffc00f93de8f275eab` | 三個 hook 的註冊 |
| S4 | [`scripts/codex-companion.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/codex-companion.mjs) | `83df468ad3eec7687e9ab5eee935751ecf70d6d0` | 所有斜線指令的進入點 |
| S5 | [`scripts/lib/codex.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/lib/codex.mjs) | `fead00cc44c8b945a292481c490ba0a50b0c5c64` | thread／turn 參數、權限設定 |
| S6 | [`scripts/lib/app-server.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/lib/app-server.mjs) | `72b30a7646a3de20060dc4cb5cb90ea3ee604820` | 啟動 `codex app-server` 的包裝層 |
| S7 | [`scripts/app-server-broker.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/app-server-broker.mjs)、[`lib/broker-lifecycle.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/lib/broker-lifecycle.mjs) | `1954274fe7c743ef5a6c971f65ba742b443364e3`、`ef763819c8c11359698e403b43c7db7cca7c87ea` | 共用 app-server 的常駐行程 |
| S8 | [`scripts/stop-review-gate-hook.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/stop-review-gate-hook.mjs) | `2346bdcf484d5acb1a8f54a9513971e2f42f664d` | Stop hook |
| S9 | [`scripts/session-lifecycle-hook.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/session-lifecycle-hook.mjs) | `778571e6ce81b11bcd79de1b6718f33e34c6c9fa` | SessionStart／SessionEnd hook |
| S10 | [`lib/state.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/lib/state.mjs)、[`lib/process.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/lib/process.mjs)、[`lib/git.mjs`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/scripts/lib/git.mjs) | `2da23498f893dd2a936199ba0020eeb62ba6b3c8`、`dd8fc3751fb446e264635287e54b45dde0af3a43`、`c401f0ca1375c14794df8dc8b3fe45a590549b68` | 資料落點、行程終止、審查內容收集 |
| S11 | [`commands/`](https://github.com/openai/codex-plugin-cc/tree/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/commands) 的 `review.md`、`adversarial-review.md`、`rescue.md`、`setup.md`；[`agents/codex-rescue.md`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/agents/codex-rescue.md) | `fb70a487…`、`da440ab4…`、`56de9555…`、`fb33a150…`；`7009ec86a091285eb2a2ab8b1b634c7d63925261` | 指令與子 agent 的提示詞 |
| S12 | [`package.json`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/package.json)、[`package-lock.json`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/package-lock.json) | `b1d984d1a1a9634d90df3e23078a29f1ecf67f17`、`0c919c3db9de915f67a0e748dc69f92e3b373b4c` | 依賴宣告 |
| S13 | [`README.md`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/README.md)、[`.github/workflows/pull-request-ci.yml`](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/.github/workflows/pull-request-ci.yml) | `937a3037b3fe6716f01b755d798255361af7287e`、`ebcff0b6556494ca54ea3a6a3a28f5d01944264d` | 官方說明、CI 平台 |

依賴宣告（S12）：沒有執行期依賴，只有兩個開發依賴（`@types/node`、`typescript`），鎖檔共三筆套件紀錄；沒有 `preinstall`／`postinstall`。`prebuild` 會呼叫 `codex app-server generate-ts`，只在開發者手動 build 時觸發。Claude Code 安裝外掛時會不會執行 npm 指令，本次未查證。

比對用的本機工具（只讀文件與一行呼叫參數）：

| 工具 | 來源 | 版本 |
| --- | --- | --- |
| ai-review skill | [SanHsien/MyR2D2](https://github.com/SanHsien/MyR2D2) 的 `skills/ai-review/SKILL.md`（本機安裝版 0.9.1） | commit `1a85057b6804e25cc63af0fb0f287278a4d021c5`，SKILL.md blob `107ca9c6c8a2f2c995715e19bb11920a1232975f` |
| agent-relay | [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) 的 `README.md`、`SPEC.md` | commit `0cabfe33c46bc0ca80234fad579c2ea8ba82896c`，blob `cfd7c06c0ab52db9e8cb035c844168f139650989`、`104b3494808d8db87d04fc9c083ac55bcc9d5971` |

## 2. 三條呼叫鏈

```text
/codex:review ───────────┐
/codex:adversarial-review┼─▶ node codex-companion.mjs <子指令>
/codex:rescue ─▶ 子 agent ┘        │
   codex:codex-rescue              ▼
   （sonnet，只有 Bash）    broker（常駐，具名管道）──忙線或連不上──▶ 直接啟動
                                   │                                    │
                                   └──────────▶ codex app-server ◀──────┘
                                                 │ thread/start → review/start 或 turn/start
                                                 ▼
                                          Codex 設定的模型後端
```

| 項目 | review | adversarial-review | rescue |
| --- | --- | --- | --- |
| 進入點 | `review.md` → `handleReview`（S4） | `adversarial-review.md` → `handleReviewCommand`（S4） | `rescue.md` → 子 agent `codex:codex-rescue` → `task` → `handleTask`（S4、S11） |
| 模型能否自行觸發 | 否（`disable-model-invocation: true`） | 否（同左） | **能**：指令沒有該設定，子 agent 的描述以 Proactively use 開頭 |
| app-server 呼叫 | `thread/start` → `review/start`（Codex 內建審查） | `thread/start` → `turn/start`，附輸出 JSON schema | `thread/start` 或 `thread/resume` → `turn/start` |
| sandbox 參數 | `read-only`（S5 第 1012 行寫死） | `read-only`（S4 第 414 行寫死） | **`workspace-write`**（子 agent 預設加 `--write`，S11 第 34 行）；沒有 `--write` 才是 `read-only`（S4 第 491 行） |
| approval 參數 | `never`（S5 第 67、80 行，三條鏈共用） | `never` | `never` |
| 伺服器端反向請求 | 一律回 `-32601` 拒絕（S6 第 156–159 行） | 同左 | 同左 |
| 模型選擇 | `--model`／`-m` 可傳，未傳就用 Codex 設定檔的預設 | 同左 | `--model`，`spark` 對應 `gpt-5.3-codex-spark`；未傳用預設 |
| effort 選擇 | 不可指定 | 不可指定（`turn/start` 傳 `null`） | `--effort none`～`xhigh`；未傳用預設 |
| thread 是否保留 | 不保留（`ephemeral: true`） | 不保留 | **保留**（`persistThread: true`），可用 `codex resume` 接續 |
| 送給模型的內容 | 由 Codex 自己讀工作樹或分支差異 | 外掛先收集 git 狀態與差異；兩個檔案以內且差異 256 KB 以內就整段放進提示詞，未追蹤的文字檔每個 24 KB 以內也會整檔附上（S10 `git.mjs`） | 使用者的請求文字；子 agent 可先改寫提示詞 |
| 背景執行 | 靠 Claude 的 `Bash(run_in_background)`；外掛本身仍是前景行程 | 同左 | `task --background` 另起 detached 的 `task-worker` 行程（S4 第 671–682 行） |
| 逾時 | **無** | **無** | **無** |
| 取消 | `/codex:cancel`：先送 `turn/interrupt`，再砍行程樹 | 同左 | 同左 |

三點補充：

1. **`approval: never` 不是取消沙箱。** 它表示 Codex 不會停下來問人；遇到沙箱擋下的動作就直接失敗。外掛也沒有回應核可請求的程式，所以即使改了設定，核可請求也只會被拒絕。這是政策層的讀碼結果；Codex 在 Windows 上實際擋不擋得住，取決於本機 Codex 版本與設定，本次未實測。
2. **外掛沿用使用者的 Codex 設定**（S13 的 Codex Integration 段）。它只把 `sandbox` 字串交給 app-server，沒有覆寫可寫範圍或網路存取。本機 `config.toml` 裡的 `sandbox_workspace_write.writable_roots`、MCP 伺服器、模型供應商設定都會一併生效。
3. **取消的範圍**：`/codex:cancel` 不帶編號時只取消目前 Claude 對話的工作；有多筆執行中會要求指定編號。SessionEnd hook 會砍掉該對話仍在執行的工作並刪除紀錄（S9 第 65 行），所以背景工作不會活過 Claude 對話。SessionEnd hook 的逾時只有 5 秒，砍不完會怎樣未實測。

### 資料落點

| 資料 | 位置 | 內容 |
| --- | --- | --- |
| 工作狀態 | `${CLAUDE_PLUGIN_DATA}/state/<repo 名>-<路徑雜湊>/state.json`；沒有該環境變數時退到系統暫存資料夾的 `codex-companion/`（S10 `state.mjs` 第 10、42 行） | gate 開關、最近 50 筆工作 |
| 單筆工作 | 同資料夾 `jobs/<id>.json`、`jobs/<id>.log` | **完整提示詞**、Codex 最終輸出、thread 編號 |
| broker | 系統暫存資料夾 `cxc-XXXXXX/` 的 `broker.pid`、`broker.log`，以及狀態資料夾的 `broker.json` | 行程編號、管道名稱、app-server 的 stderr |
| Codex thread | Codex 自己的家目錄（預設 `~/.codex`） | rescue 與 Stop gate 的完整對話 |
| 對話環境變數 | Claude 的 `CLAUDE_ENV_FILE`（SessionStart 追加三行 `export`，S9 第 78–80 行） | 對話編號、transcript 路徑、外掛資料夾路徑 |
| 模型後端 | Codex 設定的供應商 | 差異、未追蹤檔內容、提示詞；`/codex:transfer` 會送出整份 Claude 對話紀錄 |

未追蹤檔的收集用 `git ls-files --others --exclude-standard`，所以被 `.gitignore` 排除的檔案不會送出；沒被排除的憑證檔（例如忘了加進 `.gitignore` 的 `.env`）會被當成審查內容送出。

## 3. 四項禁止行為檢查

| 檢查 | 結果 | 證據與限制 |
| --- | --- | --- |
| 破沙箱旗標 | 未發現 | 全庫（含測試）搜尋 `dangerously`、`bypass-approvals`、`skip-permissions`、`bypassPermissions`、`danger-full-access`、`--yolo`、`full-auto` 皆零筆。沙箱值只有 `read-only` 與 `workspace-write` 兩種 |
| 自動安裝 | 有條件 | `/codex:setup` 在找不到 Codex 且有 npm 時，會先用一次選項詢問，使用者選了才執行 `npm install -g @openai/codex`（S11 `setup.md`）。這道詢問寫在提示詞裡，不是程式強制；該指令允許 `Bash(npm:*)`，且沒有設 `disable-model-invocation`。程式本身不安裝任何東西 |
| 憑證外傳 | 未發現 | 外掛程式沒有任何網路呼叫（搜尋 `fetch(`、`node:http`、`node:https`、`WebSocket` 零筆），也不讀 Codex 的憑證檔；登入狀態靠 app-server 的 `account/read` 查詢，參數是 `refreshToken: false`。對外連線全部由本機 `codex` 執行檔負責，不在本次閱讀範圍。子行程繼承完整環境變數 |
| Stop review gate 迴圈 | **有風險** | 見下段 |

本機靜態檢查器 `verify_agent_skill_pack_safety.py --pack <clone>/plugins/codex` 的結果：掃描 43 個檔案，FAIL 0 項、需人工審查 7 項，結束碼 0（三個 command hook、四個載入時自動執行的行內指令）。這七項本文都已逐一讀過（S3、S8、S9 與 `cancel`／`result`／`status`／`transfer` 四個指令）。該檢查器是靜態啟發式，通過不代表安全。**SkillSpector 沒有執行**，因此「第三方安全審計通過」這個前提尚未成立。

### Stop hook 與 review gate

```text
每次 Claude 要停下
   │  Stop hook（逾時 900 秒，一律註冊，S3）
   ▼
gate 關（預設）──▶ 只在 stderr 提醒還有工作在跑 ──▶ 放行
gate 開 ──▶ 跑一次 Codex task（唯讀、保留 thread、上限 15 分鐘）
              ├─ 首行 ALLOW ──▶ 放行
              └─ 首行 BLOCK、逾時、非零結束、空輸出、JSON 解析失敗
                    ──▶ decision: block ──▶ Claude 繼續做 ──▶ 再次 Stop ──▶ 再跑一次
```

- gate 預設關閉（S10 `state.mjs` 第 23 行），要 `/codex:setup --enable-review-gate` 才會開，沒有隱性啟用的路徑。
- **Stop hook 本身無法關閉**：gate 關著時，每次停下仍會啟動一次 node、讀狀態檔、跑 `git rev-parse`。與既有的全域 Stop hook 並存時的執行順序與總耗時未實測。
- **gate 開啟後的迴圈沒有程式上的終止條件**：hook 沒有檢查 `stop_hook_active`（全庫搜尋零筆），而且**除了 ALLOW 以外的結果全部擋下**（S8 第 120 行起）。Codex 額度用完、未登入或逾時時，每次停下都會被擋，Claude 會一直被推回去工作。Claude Code 自己有沒有另一層防迴圈機制，本次未查證。官方 README 也明寫 gate 可能造成長迴圈並快速耗盡用量。
- gate 的每次審查都是一次保留 thread 的 Codex 執行，會在 Codex 家目錄累積對話。
- 提示詞（含 Claude 上一則回覆全文）以單一命令列參數傳給子行程（S8 第 105 行）。Windows 的命令列長度上限約 32,767 字元，回覆很長時可能啟動失敗，而失敗會被當成擋下。這是讀碼推論，未實測。

## 4. Windows 已知限制

以下全部是靜態讀碼的結果。**「沒看到衝突」不等於相容**；任何一項都要實測才算數。

| 項目 | 讀到的事實 | 風險或未知 |
| --- | --- | --- |
| 官方支援範圍 | README 沒有任何 Windows 段落；CI 只跑 `ubuntu-latest`（S13 的 CI 設定第 12 行） | 上游沒有 Windows 的自動化驗證 |
| 啟動 Codex | Windows 上以 `shell: process.env.SHELL \|\| true` 啟動 `codex app-server`（S6 第 190–195 行）；`taskkill` 與版本檢查也走同一設定（S10 `process.mjs`） | 從 Git Bash 啟動 Claude 時 `SHELL` 通常是 POSIX 路徑，Node 拿它當 shell 會不會成功未實測；沒設時走 `cmd.exe`。git 指令已改成不經 shell |
| 環境變數傳遞 | SessionStart 寫入的是 POSIX 語法的 `export NAME='值'` | 若 Claude 的指令環境沒有載入這些變數：對話編號過濾失效，狀態會落到系統暫存資料夾；hook 與指令可能讀到不同的狀態資料夾，導致 gate 開關與工作清單對不上。未實測 |
| broker 管道 | 具名管道 `\\.\pipe\cxc-XXXXXX-codex-app-server`，行程 detached | 管道的存取權限沿用 Node 預設；同機其他行程能不能連上並操作 app-server 未查證 |
| 取消與清理 | `taskkill /PID <pid> /T /F` 砍整棵行程樹 | 被防毒或權限擋下時的行為未實測；SessionEnd hook 只有 5 秒 |
| 沙箱實際效力 | 外掛只傳 `read-only`／`workspace-write` 字串 | Windows 上的檔案寫入隔離由 Codex 的 Windows 沙箱執行，效力取決於本機設定。agent-relay SPEC 第 7 節記錄過實測：使用者設定檔的 `writable_roots` 會把 workspace-write 撐大，工人曾因此寫進主 repo 的 `.git/hooks`；agent-relay 為此每次都覆寫 `writable_roots=[]`、排除暫存資料夾、關閉網路。**外掛沒有這些覆寫** |
| 暫存資料夾 | broker 的工作資料夾與狀態退路都在系統暫存資料夾 | 暫存資料夾若在 Codex 的可寫範圍內，rescue 可以改到 broker 檔案；未實測 |

## 5. 與既有工具的重疊與缺口

| 用途 | 外掛 | ai-review | agent-relay | 判斷 |
| --- | --- | --- | --- | --- |
| 找另一個模型審一份產出 | `adversarial-review`：以 git 差異為對象，結構化輸出 | 以單一檔案或 stdin 為對象，三份 rubric，可換後端 | — | 重疊。ai-review 多了逾時（預設 600 秒，到時停止後端）、狀態行與「沒審到要明講」的規則 |
| 審查沙箱 | `read-only`，在 repo 根目錄執行 | `codex exec -s read-only --ephemeral --skip-git-repo-check`，工作目錄是暫存資料夾，不碰 repo | — | ai-review 的範圍更小 |
| 原生 diff 審查 | `review`：Codex 內建審查器直接讀工作樹或分支差異 | 要自己先把差異存成檔案 | — | **外掛獨有**，但屬於便利性，直接在 Codex 裡跑 `/review` 也能做到 |
| 把工作交給 Codex 實作 | `rescue`：直接改目前工作樹，`workspace-write`，無逾時、無驗收 | — | `send --run codex`：獨立 worktree、鎖定可寫範圍、關網路、逾時 1–120 分鐘（預設 30）、驗收閘門、簽章、每日上限 | 重疊，agent-relay 的邊界嚴格得多 |
| 背景工作查詢與取消 | `status`／`result`／`cancel` | 無（同步執行） | `status`、逾時自動結束、中斷補回信 | 重疊 |
| 接續 Codex 對話 | `rescue --resume`、`codex resume <id>` | 無 | 無（每張工單一個新對話） | **外掛獨有** |
| 把 Claude 對話搬進 Codex | `transfer` | 無 | 交接包（`context`）只帶摘要 | **外掛獨有**；代價是整份對話紀錄送到 Codex 後端 |
| 停下前強制審查 | Stop review gate | 無（skill 文字明講它不是強制機制） | 驗收閘門在收件端執行 | 外掛有，但迴圈風險見第 3 節 |

缺口只有三項：對話內的原生 diff 審查、接續 Codex 對話、搬移 Claude 對話。目前沒有任何一項有具體需求在等。

## 6. 採納裁決

**不採納安裝；不主動開實測任務。** 理由：

1. **用途已涵蓋**：跨模型審查有 ai-review，交辦實作有 agent-relay，兩者的邊界都比外掛嚴格。
2. **rescue 的預設與本機紀律相反**：模型可以不經使用者要求就主動呼叫子 agent，預設可寫、直接改目前工作樹、不鎖可寫範圍、沒有逾時。agent-relay 已經用實測證明不鎖 `writable_roots` 會寫出範圍外。
3. **Stop hook 無法單獨停用**：裝了就多一個每次停下都會執行的 hook，即使 gate 永遠不開。
4. **Windows 沒有上游驗證**：第 4 節的每一項都要自己實測。
5. **第三方安全審計未完成**：SkillSpector 未執行。依任務的驗收標準，審計未通過不建議安裝。

可以重新評估的條件：出現「要在 Claude 對話內反覆做 git 差異審查，而且 ai-review 的檔案式流程明顯不夠用」的具體需求，並且先完成 SkillSpector 掃描。

## 7. 若日後另案實測：規格與停止條件

本節只是未來任務的驗收設計，不代表建議現在就做，也不宣稱有任何實測結果。

**前置條件（任一不成立就不開始）**

- SkillSpector 與 `verify_agent_skill_pack_safety.py` 對固定 commit 的掃描都已完成並由人看過結果。
- 釘在本文的 commit；上游有新版就先重做第 2–4 節的讀碼。
- 登入與外掛安裝畫面由維護者操作。登入完成只代表前置條件成立，不算實測成功。
- 測試期間 Stop review gate 全程關閉，不執行 `/codex:setup --enable-review-gate`。

**範圍**

- 一個隔離的測試專案：全新的小型 git repo，放在平常的 repo 資料夾之外，只有兩三個無機密的文字檔，沒有 `.env`。只在這個專案啟用外掛（專案層級安裝），不裝到使用者層級。
- 一次 `/codex:adversarial-review --wait`，對象是一個兩個檔案以內的小差異。
- 一次最小 rescue，明確要求唯讀：請它說明某個函式做什麼，不加 `--write`。
- 不跑多工具或多模型的比較基準，不測 `transfer`，不測 gate。

**每次執行要記錄的證據**

| 項目 | 記錄什麼 |
| --- | --- |
| 版本 | Claude Code、Codex CLI、Node 的版本；啟動 Claude 的 shell |
| 用量 | 執行前後的 Codex 用量畫面。**外掛不回報用量**，查不到就寫「用量未知」，不可推估 |
| 權限 | Codex thread 紀錄裡實際的 sandbox 與 approval 值；工作樹在執行前後的 `git status` |
| 資料落點 | 狀態資料夾的實際路徑（是外掛資料夾還是系統暫存資料夾）；`jobs/` 裡留下了什麼 |
| 行程 | 執行結束後還有沒有殘留的 broker、`codex`、`node` 行程 |
| hook | Stop hook 每次執行的耗時；與既有全域 hook 並存時有沒有錯誤輸出 |

**逾時與取消**

- 外掛沒有逾時，由操作者計時：審查 10 分鐘、rescue 10 分鐘。到時執行 `/codex:cancel <id>`，再確認工作狀態變成 cancelled、行程樹已消失。
- 取消本身要測一次：對一個執行中的背景工作下 `/codex:cancel`，記錄 `turn/interrupt` 有沒有成功、`taskkill` 有沒有清乾淨。

**停止條件（任一發生就停，不重試，照實記錄後移除外掛）**

- 唯讀執行後 `git status` 出現任何變動，或測試專案以外的檔案被改。
- 出現任何核可提示被自動通過的跡象。
- Stop hook 擋下停止，或出現連續兩次以上的自動續跑。
- 取消後 60 秒仍有殘留行程。
- 額度錯誤、登入失效或網路錯誤：停下回報，不換帳號、不重跑。
- Codex 執行總次數達到三次（一次審查、一次 rescue、一次取消測試）。

**結案要求**

- 實測報告寫在本 repo 的 `docs/`，逐項對照上表；沒量到的寫「未實測」。
- 通過的定義是「上述證據齊全且沒有觸發停止條件」，不是「指令看得到」或「登入成功」。
- 同一個 commit 更新 `ROADMAP.md`、重建 README 並通過 `verify_inbox.py`。
- 結束後移除外掛與測試專案，確認狀態資料夾、暫存資料夾與 Codex 家目錄裡的測試 thread 已清掉。

## 8. 本次沒做與未查證

- 沒有安裝外掛、沒有登入、沒有啟動 Codex 或任何模型後端、沒有改全域設定或 hooks。
- 沒有執行上游的測試或任何 npm 指令。
- 沒有讀 `codex` 執行檔或 app-server 的原始碼；sandbox 與 approval 在執行期的實際效力未查證。
- 沒有逐行讀完 `render.mjs`、`job-control.mjs`、`args.mjs`、三個 prompting skill 的參考檔與測試；它們不在權限路徑上，只做過關鍵字搜尋。
- SkillSpector 未執行。
- Claude Code 的外掛安裝流程是否執行 npm、`CLAUDE_ENV_FILE` 在 Windows 各 shell 的載入方式、Claude Code 對 Stop hook 迴圈的內建保護，皆未查證。
- 筆記裡的星數、免費方案額度、生圖能力不在本文範圍，另見獨立審查對該筆記的逐條意見。
