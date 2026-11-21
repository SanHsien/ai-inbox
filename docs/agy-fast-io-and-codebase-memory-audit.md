# agy-fast-io 與 codebase-memory-mcp 唯讀安全審查：都不跑安裝程式，各借鏡一部分

審查日期：2026-11-21。任務：T-20261120-04。作者：Claude Code。
來源筆記：[`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](../notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)。

**結論**

| 對象 | 決策 | 一句話理由 |
| --- | --- | --- |
| `oil-oil/agy-fast-io` | **不安裝；部分借鏡**（兩段寫法改寫後放進自己的規則） | 只有一份給 agent 的規則文字，沒有程式、hook、MCP，也不改 Antigravity 檔案、不走 API／OAuth。但規則會全域套用到每個 Antigravity 對話，其中「把要送審的命令併成一次」「多檔修改改用一支腳本」會降低桌面版安全審查的粒度，「失敗也繼續就用 `;`」「不為確認多翻檔」與本機測試閘門、完成驗證規則衝突；命令全是 POSIX 寫法，沒有 Windows 證據 |
| `DeusData/codebase-memory-mcp` | **不跑 `install`；部分借鏡，可在限縮條件下試用** | MIT、純本機、正式版沒有對外連線與遙測（原始碼查證），根目錄拒絕清單擋家目錄與 `.ssh` 等憑證目錄。風險集中在安裝程式：`install.ps1` 以 `install -y --force` 一次改寫偵測到的所有 agent 設定（含 `~/.claude.json`、`$CODEX_HOME`、`~/.gemini/GEMINI.md`、Hermes），預設裝 hook。維護者已有自己的 fork，要試用就手動註冊單一 client、關 hook、限定索引根目錄 |

兩者都**沒有**違反維護者「禁止 agent 經 API／OAuth 吃 Antigravity 訂閱額度」的規則：agy-fast-io 是在 Antigravity 裡由維護者自己使用的規則檔；codebase-memory-mcp 不呼叫任何模型。

## 1. 來源與審查範圍

| 項目 | agy-fast-io | codebase-memory-mcp |
| --- | --- | --- |
| Repo | [oil-oil/agy-fast-io](https://github.com/oil-oil/agy-fast-io) | [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) |
| 審查 commit | `c9231ac580437829ccd7950efa5ea79b3a7e0503`（2026-11-12，`docs(readme): 改成浅色视觉…`） | `1111d9a9e1380a0429ef2250f63223706af6289a`（2026-11-19，`Merge pull request #3016 …`），與 `git ls-remote` 查到的上游 `HEAD` 相同 |
| 規模 | 14 個追蹤檔，文字檔只有 README、`plugin/plugin.json`、`plugin/rules/AGENTS.md` 等 9 個 | 3,726 個追蹤檔（`internal/` 1,305、`graph-ui/` 1,010、`tests/` 520、`src/` 347…），51 個二進位檔 |
| 授權 | MIT（`LICENSE:1-3`，著作權人 linzhihuang） | MIT（`LICENSE:1-3`，著作權人 DeusData）；第三方元件見 `THIRD_PARTY.md` |

取得方式：`git clone --depth 1 -c core.hooksPath=NUL -c core.symlinks=false`，放在 `C:\GitHub\_sandbox\agy-plugins-audit\`。只讀文字；沒有執行 repo 內任何腳本，沒有 `npm`／`pip`／`go install`，沒有下載 release 執行檔，沒有啟動 MCP server、daemon 或 CBM Lens。審查完成後沙盒已送資源回收筒。

本文的路徑都是各 repo 內的相對路徑，行號對應上表的 commit。

```text
審查流程

唯讀淺層 clone（關 hook、關 symlink）
   │
   ├─▶ verify_agent_skill_pack_safety.py --pack <clone>   （各一次，第 2 節）
   │
   ├─▶ 人工閱讀：授權、對外連線、讀寫路徑、安裝與更新、
   │             提權／關防護、hook、MCP 工具、Windows 證據（第 3、4 節）
   │
   ├─▶ 唯讀查本機：有沒有安裝或註冊、本機 fork 現況（第 5 節）
   │
   └─▶ 筆記主張逐項對照（第 6 節）→ 決策與建議（第 7 節）
```

沒有做的事：沒有動態執行，因此索引耗時、記憶體與 token 節省都沒有在本機量測；兩個 repo 的二進位檔（圖片、字型、測試語料）沒有檢查內容；`.git` 物件庫沒有檢查；Antigravity 使用條款原文本次未查證。

## 2. 機器掃描結果

指令：`python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack <clone 目錄>`。掃描器是靜態啟發式，只比對已知危險寫法；結束碼 0 也不代表安全。

| 範圍 | 結束碼 | 摘要 |
| --- | --- | --- |
| `agy-fast-io` 整個 clone | **2** | 掃描 25 個檔案：FAIL 0、需人工審查 1、未掃描 4 個（全是圖片），因此判為無法完整掃描 |
| `codebase-memory-mcp` 整個 clone | **1** | 掃描 3,624 個檔案：FAIL 22 項、需人工審查 30 項、未掃描 117 個（65 個超過大小上限，例如 `vendored/sqlite3/sqlite3.c`；其餘為二進位檔） |

### 2.1 agy-fast-io 命中判讀

| 命中 | 位置 | 人工判讀 |
| --- | --- | --- |
| REVIEW：動態執行 | `.git/hooks/pre-receive.sample:14` | 無關。git 自帶的範例檔，不是 repo 內容 |
| 未掃描 | `assets/readme/before-after.webp`、`hero.webp`、`source/antigravity-logo.png`、`source/hero-subject.png` | README 插圖，沒有檢查內容。兩個 SVG 已人工看過，沒有 `<script>`、事件屬性或外部連結，只引用同目錄的 PNG（`assets/readme/source/hero-layout.svg:10`、`:19`） |

掃描器抓不到、人工讀出來的項目見第 3 節：全部是寫給 agent 的指示文字，不在比對規則內。

### 2.2 codebase-memory-mcp 命中判讀

依類別合併判讀。FAIL 22 項裡，真正落在使用者機器、會影響本機的是前三列；其餘是測試語料、CI 或防護清單本身。

| 類別（數量） | 位置 | 人工判讀 |
| --- | --- | --- |
| FAIL REMOTE-EXEC（README 4） | `README.md:73`（`curl … install.sh \| bash`）、`:90`（下載後執行 `install.ps1`）、`:524`（`curl … setup.sh \| bash`）、`:530`（`irm … setup-windows.ps1 \| iex`） | **屬實**。官方安裝說明就是下載遠端腳本後執行，違反本機規則 15，不照做。Windows 那條 `irm \| iex` 會執行 `scripts/setup-windows.ps1`，它再以 `-ExecutionPolicy Bypass` 跑 `install.ps1`（`scripts/setup-windows.ps1:327`），並可互動式改寫 `~/.claude/settings.json`（`:61`） |
| FAIL DEFENSE-OFF（6） | `README.md:87`、`:125` 與 `src/cli/cli.c:14951`（`Unblock-File install.ps1`）；`install.sh:335`、`scripts/smoke-test.sh:3656`、`:4023`（`xattr -d com.apple.quarantine`） | **屬實但有前提**。`Unblock-File` 是教使用者移除下載標記；`cli.c:14951` 是 `update` 指令印出的說明文字，不會自己執行。`xattr` 是 macOS 安裝與 CI，Windows 不受影響 |
| FAIL INSTALL-EXEC（1） | `pkg/npm/package.json` 的 `postinstall: node install.js` | **屬實**。`npm install` 會自動下載 release 執行檔（`pkg/npm/install.js:24`），雖有雜湊驗證，仍是安裝時自動執行。Claude Code 外掛路線的 `npx -y` 也會走到這裡 |
| FAIL CRED-ACCESS（6） | `src/foundation/workspace.c:142-144`；`tests/test_grammar_probe_g.c:920`、`tests/test_infrascan.c:27`、`tests/test_security.c:309` | **誤判**。`workspace.c` 是「拒絕索引憑證目錄」的清單；其餘是測試字串 |
| FAIL REMOTE-EXEC（其餘 4） | `scripts/smoke-test.sh:3979`、`:3985`；`tests/test_security.c:304`；`tests/test_setup_scripts_contract.sh:315` | **誤判**。smoke test 核對下載檔雜湊；`test_security.c` 是攻擊字串樣本；契約測試是輸出訊息 |
| FAIL OBFUSCATED（1） | `test-infrastructure/vm/ssh-common.sh:67` | **屬實但只在上游測試基礎設施**。把明文 PowerShell 腳本轉 UTF-16LE＋base64 後用 `-EncodedCommand` 送進 Windows 測試 VM（`:63` 可見原文來源），不隨產品發布 |
| REVIEW MCP-SERVER（1） | `plugin/.mcp.json:3-7` | Claude Code 外掛用 `npx -y codebase-memory-mcp@0.12.1` 啟動，版本有釘，但每次啟動仍經 npm |
| REVIEW AGENT-STEER（1） | `pkg/go/cmd/codebase-memory-mcp/main.go:2247` | 誤判。是註解裡的「replace the native command result」，不是引導 agent 的文字 |
| REVIEW AUTO-HOOK（4） | `docs/EVALUATION_PLAN.md:2029`、`:3530`、`:5719` | 誤判。評估文件裡的反引號片段，不是技能檔 |
| REVIEW DYNAMIC-EXEC（20） | `src/mcp/mcp.c:15841`、`:15859`、`:15870`；`Makefile.cbm:1471`；`scripts/soak-test.sh:267-268`；`.github/workflows/_smoke.yml:368`；文法掃描器與測試語料 | `mcp.c` 三處是 `search_code` 在 POSIX 上組 `find`／`xargs`／`grep` 指令（Windows 分支改用 `powershell -Command` 的 `Select-String`，`:15790-15830`）。搜尋字串經暫存檔傳入，路徑與 `file_pattern` 先過字元檢查，擋掉引號、`;`、`\|`、`$`、反引號、重導向（`:17466-17514`），本次沒找到注入路徑。其餘為建置、CI、文法程式碼與測試字串 |
| REVIEW DEFENSE-OFF、CRED-ACCESS（4） | `README.md:288`、`:514`；`docs/CONFIGURATION.md:295` | `:514` 屬實（SmartScreen「仍要執行」）；`:288` 是更新說明；`CONFIGURATION.md` 是拒絕清單的說明 |
| 未掃描（117） | 二進位檔與超過 5 MB 的檔案 | 沒有檢查內容 |

## 3. agy-fast-io 人工審閱

### 3.1 它是什麼

一個 Antigravity 本機外掛，內容只有一份規則檔（`README.md:5`、`plugin/README.md:3`）。`plugin/plugin.json:2-8` 宣告名稱 `fast-io`、版本 `0.2.1`；結構與本機 Antigravity 外掛目錄一致（`plugin.json` 加 `rules/`）。README 自稱「非官方，與 Google 無關」（`README.md:7`）。

```text
安裝後的作用方式

~/.gemini/config/plugins/fast-io/rules/AGENTS.md
   │  Antigravity 載入外掛規則（每個新對話）
   ▼
Antigravity agent 的系統脈絡
   │  改變的是 agent 的習慣：怎麼搜、讀多少、命令怎麼寫、回答多長
   ▼
工具呼叫 ──▶ 桌面版內建白名單 ──命中──▶ 直接執行
                    │
                    └─未命中─▶ 雲端小模型審查（約 2–3 秒）─▶ 執行
```

### 3.2 重點檢查項

| 檢查項 | 結果 | 證據 |
| --- | --- | --- |
| 程式碼、hook、MCP | 沒有。repo 只有規則、README 與插圖 | `README.md:5`；`plugin/README.md:3`；`git ls-files` 14 個檔 |
| 對外連線、遙測 | 沒有可執行內容，因此沒有 | 同上 |
| 修補或注入 Antigravity 程式檔 | 沒有。安裝只是把 `plugin/` 放進 `~/.gemini/config/plugins/fast-io`，或用官方 `agy plugin install` | `README.md:65`、`:71`；`plugin/README.md:15` |
| 改 Antigravity 設定、開免審白名單 | 沒有。作者明說找不到關掉雲端審查的設定；規則只是讓 agent 改用內建白名單裡的命令 | `README.md:32`；`plugin/rules/AGENTS.md:20-30` |
| 走 API／OAuth 吃訂閱額度 | 沒有。不呼叫任何模型，也不包裝 `agy` | 全 repo |
| 讀寫的本機路徑 | 規則本身不指定路徑；要求 agent 搜尋時寫明源碼目錄、不對 `.` 遞迴 | `plugin/rules/AGENTS.md:8` |
| Windows 支援證據 | 沒有。安裝指令是 `cp -R`，白名單命令是 POSIX 名稱（`grep`、`head`、`wc`…），只在一個 Swift 專案測過；Antigravity 在 Windows 上 `run_command` 用哪個 shell、白名單是否相同，本次未查證 | `README.md:11`、`:71`、`:91`；`plugin/rules/AGENTS.md:26` |
| 自動更新 | 沒有 | 全 repo |

### 3.3 寫給 agent 的指示（風險欄）

規則檔是外掛的全部內容，裝上之後每個 Antigravity 對話都會讀到。下表逐條判讀它要 agent 做的事：

| 位置 | 指示內容（摘要） | 判讀 |
| --- | --- | --- |
| `plugin/rules/AGENTS.md:5-16` | 先用一條 `grep -rn` 定位，再同一輪並行讀；一次讀 150–200 行，300 行以內整份讀 | 無害，值得借鏡 |
| `plugin/rules/AGENTS.md:24-31` | 檢索只用白名單命令；不寫 `&&`、`;`、重導向、`cd`、`$(...)` | 無害。只是挑會被直接放行的寫法，沒有繞過審查 |
| `plugin/rules/AGENTS.md:36-38` | 白名單外的命令（`python3`、`npm`、建置、測試）用 `&&` 串成一次，「只審一次」；失敗也要繼續就用 `;` | **降低審查粒度**：雲端審查從每步一次變成整串一次。`;` 那句與本機規則 11（測試與提交之間只准 `&&`）衝突 |
| `plugin/rules/AGENTS.md:48` | 跨 5 個以上檔案的機械替換改用一支 `python3` 腳本，「避免多次排隊送審」 | **降低審查粒度**：每次 `edit_file` 的審查換成一次腳本審查，審查者看不到逐檔差異 |
| `plugin/rules/AGENTS.md:56` | 回答一般控制在 1,500 字以內，先結論 | 無害，與本機精簡規則一致 |
| `plugin/rules/AGENTS.md:60` | 找到答案就回答，「不為了確認再多翻文件」 | 與本機規則 5（完成必附證據）衝突 |
| `plugin/rules/AGENTS.md:61` | 小任務不寫計畫、清單、總結文件 | 無害 |

`plugin/rules/AGENTS.md:36` 把 `ego-browser` 列為常見的送審命令，表示作者同時在用 Ego Lite；該工具的審查見 [`docs/ego-lite-security-eval.md`](./ego-lite-security-eval.md)。

### 3.4 條款與維護者規則

- **維護者規則（禁止 agent 經 API／OAuth 吃 Antigravity 訂閱額度）**：不違反。規則檔在 Antigravity 裡由維護者自己使用，不讓第三方 agent 取得 Antigravity 的模型。
- **Antigravity 條款**：本次未讀條款原文，無法斷言。可以確定的是 repo 沒有改 Antigravity 程式檔、沒有偽裝用戶端、沒有改寫審查設定；它利用的是官方外掛機制與內建白名單（`README.md:65`、`:92`）。
- **規避偵測疑慮**：第 3.3 節兩條「降低審查粒度」的指示，目的寫明是少等審查（`plugin/rules/AGENTS.md:36`、`:48`）。這不是繞過，但會讓桌面版安全審查看到的單位變大，與本機「不做規避偵測處理」的立場方向相反，所以不採用這兩條。

## 4. codebase-memory-mcp 人工審閱

### 4.1 它是什麼

純 C 寫的本機 MCP server：用內建的 tree-sitter 文法（164 種語言）加上自寫的型別解析（README 稱 Hybrid LSP，不是啟動真的語言伺服器）建程式碼知識圖譜，存進本機 SQLite，提供 17 個 MCP 工具（`README.md:23`、`:1106-1130`、`:1134`、`:1146-1162`）。另附可選的瀏覽器介面 CBM Lens，與一支會設定 46 種 agent 用戶端的安裝程式（`README.md:23`、`:704`）。

```text
元件與資料流

agent（Claude Code、Codex、Antigravity…）
   │  stdio MCP
   ▼
codebase-memory-mcp（前端）──IPC──▶ 共用 daemon（每個帳號一個）
                                        │
                     ┌──────────────────┼────────────────────┐
                     ▼                  ▼                    ▼
               索引 worker         背景 watcher          CBM Lens（可選）
               讀被索引的專案       輪詢 git 變更         127.0.0.1:9749
                     │                                        │  瀏覽器端模型（啟用才下載，
                     ▼                                        │  來源 Hugging Face）
          ~/.cache/codebase-memory-mcp/*.db  ◀────────────────┘
```

### 4.2 重點檢查項

| 檢查項 | 結果 | 證據 |
| --- | --- | --- |
| 授權 | MIT | `LICENSE:1-3`；`README.md:1196-1198` |
| 遙測 | 文件宣稱不收集；原始碼沒找到回報端點 | `README.md:483`、`:286` |
| 執行檔自己對外連線 | 正式版沒有。下載與查最新版本的程式碼（呼叫 `curl`）只包在 `CBM_CLI_ENABLE_TEST_API` 條件編譯裡，這個旗標只出現在測試建置 | `src/cli/cli.c:8596-8649`、`:14603-14785`（`fetch_latest_tag` 在 `:14725`）；`Makefile.cbm:121-123` |
| 其他對外連線 | CBM Lens 的 CSP 允許連 `huggingface.co` 與 `us.aws.cdn.hf.co`（瀏覽器下載可選模型，約 567 MB 起）；另允許 `127.0.0.1:4141`，用途未查證 | `src/ui/http_server.h:27-29`；`README.md:215-216` |
| 本機網路暴露 | UI 只綁 `127.0.0.1`；CORS 只回應同一埠的 `127.0.0.1`／`localhost` 來源 | `src/ui/http_server.c:13`、`:88-130` |
| 讀取範圍 | 只讀被索引的目錄。永遠拒絕：磁碟根目錄、`C:\Windows`、`C:\Users`、`C:\ProgramData`、`C:\Program Files`、家目錄本身、任何層級的 `.ssh`、`.aws`、`.gnupg`、`.kube`、`.docker`、`.netrc`、`.git-credentials`、`.azure`、`.gcloud`、`.password-store` 等 | `docs/CONFIGURATION.md:285-295`；`src/foundation/workspace.c:134-165`、`:314-316` |
| 讀取範圍的缺口 | 拒絕清單**沒有** `.claude`、`.codex`、`.gemini`、瀏覽器設定檔目錄（`%LOCALAPPDATA%` 下）。家目錄底下的子目錄都允許索引；JSON、TOML、YAML 會被解析。agent 若對 `~/.gemini` 跑 `index_repository`，`oauth_creds.json` 這類檔案的內容可能進索引，再被 `search_code` 讀出。`CBM_ALLOWED_ROOT` 預設未設 | `src/foundation/workspace.c:134-150`；`README.md:1043`、`:1079` |
| 寫入路徑 | 索引與設定在 `~/.cache/codebase-memory-mcp`（可用 `CBM_CACHE_DIR` 改）；執行檔裝在 `%LOCALAPPDATA%\Programs\codebase-memory-mcp` | `README.md:1044`、`:1085`；`install.ps1:28` |
| 安裝方式 | README 首推 `curl … \| bash`（macOS／Linux）；Windows 是下載 `install.ps1` 後執行，遇執行原則錯誤建議 `Set-ExecutionPolicy -Scope Process Bypass`；SmartScreen 警告建議點「仍要執行」。另有 npm、PyPI、Scoop、`go install`、Claude Code 外掛（`npx -y codebase-memory-mcp@0.12.1`） | `README.md:73`、`:78-94`、`:412`、`:514`、`:585-607`；`plugin/.mcp.json:1-9` |
| 安裝時改寫其他 agent 設定 | **主要風險**。`install.ps1` 驗證雜湊後執行 `install -y --force`，不詢問、會取代被使用者改過的檔案；偵測到哪個 client 就寫哪個。Antigravity 只要 `~/.gemini/antigravity-cli` 存在或 `antigravity` 在 PATH 就算偵測到，會寫 `~/.gemini/config/mcp_config.json` 與在 `~/.gemini/GEMINI.md` 加入管理區塊 | `install.ps1:426-428`；`README.md:704-708`、`:725-772`、`:779-782`；`src/cli/cli.c:10894-10920`；`docs/WINDOWS_TROUBLESHOOTING.md:39-41` |
| hook | 預設啟用。Claude Code 加 `SessionStart`、`SubagentStart`、`PreToolUse`（`Grep`／`Glob`／`Bash`）與 `Read` 後的提示；Codex 加 `PreToolUse`（`Bash`）；Antigravity 不裝 hook。文件稱只補充脈絡、失敗放行、不擋工具 | `README.md:146-148`、`:727-728`、`:786-790`；`docs/WINDOWS_TROUBLESHOOTING.md:41` |
| 自動更新 | 沒有。`update` 只印出要執行的 `install.ps1` 指令；背景不檢查新版 | `README.md:272-290` |
| 提權、關防護 | 沒有要求系統管理員權限。關防護的建議只在 README：`ExecutionPolicy Bypass`（限該程序）、SmartScreen「仍要執行」；macOS 的 `install` 會移除隔離屬性並自簽 | `README.md:94`、`:131`、`:514`；`src/cli/cli.c:8652-8663` |
| 發行驗證 | 安裝腳本強制核對 SHA-256；release 另有 SLSA 出處證明、cosign 簽章、VirusTotal 掃描結果 | `install.ps1:245-276`；`README.md:1164-1173` |
| Windows 支援 | 有原生 Windows x64／ARM64 執行檔與 `install.ps1`；CI 在 `windows-latest`、`windows-11-arm` 建置與長時間測試。已知未解：索引 worker 卡住（#1130）、啟動即退出（#1145） | `README.md:12`、`:510`；`.github/workflows/_build.yml:118`、`:180`；`.github/workflows/_soak.yml:115`；`docs/WINDOWS_TROUBLESHOOTING.md:25-33` |
| 索引開銷 | 只有上游在 Apple M3 Pro 的數字：Linux kernel（2,800 萬行）完整索引 3 分鐘，Django 約 6 秒。`auto_index` 預設關、`auto_watch` 預設開；四個資源上限預設都關。Windows 上的耗時與記憶體本次沒有量測，未查證 | `README.md:463-475`、`:1035-1037`；`docs/CONFIGURATION.md:89`、`:92` |

### 4.3 MCP 工具與權限面

17 個工具中 13 個標為唯讀（`readOnlyHint`），會寫入狀態的 4 個是 `index_repository`、`delete_project`、`manage_adr`、`ingest_traces`（`src/mcp/mcp.c:919-937`）。寫入對象都是 `~/.cache` 下的圖譜資料庫，不改被索引的原始碼。`query_graph` 只接受唯讀的 Cypher 子集（`README.md:999-1009`）。

| 工具 | 讀寫 | 需要注意的地方 |
| --- | --- | --- |
| `index_repository` | 寫索引 | 會讀整個目標目錄；成功後該目錄被 watcher 持續輪詢（`README.md:919`） |
| `search_code`、`get_code_snippet`、`get_file_outline` | 讀 | 會回傳原始碼內容；範圍等於已索引的目錄 |
| `delete_project` | 刪索引 | 標為 destructive；只刪圖譜，不刪原始碼 |
| `manage_adr`、`ingest_traces` | 寫索引旁的資料 | 不改原始碼 |
| 其餘 9 個查詢工具 | 讀 | 無 |

另有一處會影響 agent 行為：`search_graph`、`trace_path`、`get_code_snippet` 帶 `_meta["anthropic/alwaysLoad"]`，要 Claude Code 一開始就載入這三個工具的定義（約 4.6K 字元），不放在延遲載入區（`src/mcp/mcp.c:913-918`）。

### 4.4 寫給 agent 的指示（風險欄）

| 位置 | 內容 | 判讀 |
| --- | --- | --- |
| `README.md:579-583` | 範例對話：叫 Claude Code「Install this MCP server: <repo 網址>」 | 叫 agent 自己安裝，違反本機規則 15，不照做 |
| `README.md:65`、`:134-148` | 安裝程式替 agent 寫入技能、Scout／Verify／Auditor 三種子 agent 定義與 hook，引導 agent 優先用圖譜工具 | 屬於持續性指示，會進每個對話；要用就自己寫一份短的，不用它的安裝程式 |
| `README.md:774-777` | Codex 的全域 `AGENTS.md` 會被加入一段管理用的指標 | 會改到本機 agent 的全域指示檔 |

## 5. 本機現況（唯讀查證，2026-11-21）

### 5.1 `C:\GitHub\codebase-memory-mcp` 是什麼

| 項目 | 結果 |
| --- | --- |
| remote | `origin` = `SanHsien/codebase-memory-mcp`；`upstream` = `DeusData/codebase-memory-mcp`（push 設為 `DISABLE`） |
| 性質 | 維護者自己的維護 fork：繁中 README、`AGENTS.md`、`REVIEW.md`、Windows 維護檢查與上游追蹤工具（fork 的 `FORK.md:1-15`） |
| `main` | `524ea157`（2026-11-21），與 `origin/main` 同步；工作區乾淨 |
| 與上游的關係 | 歷史在 2026-10-01 壓成單一提交（root `adb47cac`），與上游沒有共同祖先，所以 `git rev-list` 的「落後 5,660」不代表真實差距。fork 用三方合併同步，上游審查基準線是 `a3e9c91a`（2026-11-13，`tools/upstream_baseline.json`） |
| 落後上游 | 基準線之後上游有 121 個 commit 尚未審查；本機的 `upstream/main` 已是最新（`1111d9a9`，與本次審查的 commit 相同） |

本次審查沒有動這份 fork：沒有 `fetch`、沒有切分支、沒有寫檔。

### 5.2 有沒有安裝或註冊

| 查的地方 | 結果 |
| --- | --- |
| `~/.claude.json` 的使用者層級 MCP | 只有 `github`、`qmd`；沒有任何專案註冊它。唯一命中是 fork 某個 worktree 的專案項目 |
| `~/.claude/settings.json` | 沒有命中（沒有它的 hook） |
| Codex `config.toml` | 沒有 `[mcp_servers.codebase-memory*]`；唯一命中是把 fork 目錄設為 trusted 的專案項目 |
| `~/.gemini`（Antigravity） | `config/mcp_config.json`、`antigravity-ide/mcp_config.json` 都是 0 位元組；`antigravity-cli/settings.json` 沒有 MCP；`GEMINI.md` 沒有命中；外掛目錄沒有 `fast-io` |
| 執行檔、技能 | PATH 上沒有；`%LOCALAPPDATA%\Programs\codebase-memory-mcp` 不存在；`~/.agents/skills`、`~/.claude/skills` 沒有 |
| 快取 | `~/.cache/codebase-memory-mcp` 存在但是空目錄（2026-09-30 建立，推測是 fork 開發測試留下，未查證） |

結論：本機**沒有安裝、也沒有在任何 agent 註冊** codebase-memory-mcp；agy-fast-io 也沒有裝。全部只看鍵名與命中數，沒有輸出任何憑證值。

注意：本機有 `~/.gemini/antigravity-cli`，所以若有人執行上游 `install.ps1`，Antigravity 會被判定為已安裝，`~/.gemini/GEMINI.md` 與 `~/.gemini/config/mcp_config.json` 會被改寫（第 4.2 節）。

## 6. 筆記主張對照

| 筆記主張（所在段落） | 查證結果 |
| --- | --- |
| codebase-memory-mcp 是「Tree-sitter AST + LSP 本地程式碼知識圖譜 MCP」（開頭「文中相關開源專案」） | 大致相符。tree-sitter 屬實；「LSP」是作者自寫的 C 型別解析，不啟動語言伺服器（`README.md:1108`） |
| agy-fast-io 是「非官方 Antigravity 批量讀取規則插件」（同上） | 相符（`README.md:5`、`:7`） |
| 文章要 AI「安裝 agy-fast-io 並設為讀取免審白名單」（第 2 節風險提醒） | repo 沒有任何設定白名單的機制，作者也說找不到關閉審查的設定；它只是讓 agent 改用內建白名單裡的命令（`README.md:32`；`plugin/rules/AGENTS.md:20-30`）。文章原句本次未重讀 |
| 第 11 條「codebase-memory-mcp + Cloud Remote + Turbo」（第 1 節 12 項配置盤點） | repo 只涉及 MCP 註冊；Cloud Remote、Turbo 是 Antigravity 本身的設定，repo 內沒有，未查證 |
| codebase-memory-mcp 能「減少大專案檢索 token」（第 2 節可評估項） | 是作者自己的數字：論文預印本稱 token 少 10 倍、工具呼叫少 2.1 倍（`README.md:477`），沒有獨立重現；本次未量測 |
| 兩者「適合建立沙盒唯讀審查任務」（第 2 節可評估項） | 已完成，見本文 |

## 7. 建議（未動手）

1. **agy-fast-io 不裝進 Antigravity。** 規則檔會進每個對話；第 3.3 節有四條與本機規則方向相反。要借鏡的只有兩段，改寫後放進自己的規則來源（`SanHsien/agent-assets`（私有）的跨 AI 規則），不放第三方外掛：
   - 搜尋與閱讀：「先用一條搜尋拿到檔名與行號，再同一輪並行讀；一次讀足 150–200 行，不分段回頭補」（`plugin/rules/AGENTS.md:5-16`）。
   - 回答：「先結論，不貼大段程式碼，不複述讀到的內容」（`plugin/rules/AGENTS.md:54-56`）。
   - 不借：「併成一次只審一次」「多檔改用腳本避開逐次審查」「失敗也繼續用 `;`」「不為確認多翻檔」（`:36-38`、`:48`、`:60`）。
   - 命令要先確認 Antigravity 在 Windows 上的 shell 與白名單再寫，不能照抄 POSIX 清單。
2. **codebase-memory-mcp 不執行上游安裝程式**（`install.ps1`、`install.sh`、`codebase-memory-mcp install`、Claude Code 外掛的 `npx -y`）。
3. **若要試用，條件如下**，且先交維護者決定：
   - 執行檔用維護者 fork 的 release（已鏡像並核對雜湊）或自行從 fork 建置；不用 `npx`、`pip`。
   - 只手動註冊一個 client（例如單一 repo 的專案層級 `.mcp.json`），不跑 `install`，因此不會有 hook、技能與子 agent 定義。
   - 在註冊的 `env` 設 `CBM_ALLOWED_ROOT=C:\GitHub`，擋掉 `~/.gemini`、`~/.claude`、`~/.codex` 這類拒絕清單沒涵蓋的憑證目錄。
   - 先關 `auto_watch` 或 `watcher_enabled`，避免背景輪詢；必要時設 `index_max_rss_mb`、`index_max_duration_seconds`。
   - 先在一個中型 repo 量索引時間、記憶體、`~/.cache` 佔用，再談 token 節省。
4. **回饋 fork**：拒絕清單缺 `.claude`、`.codex`、`.gemini` 與瀏覽器設定檔目錄，可以在 fork 的 `REVIEW.md` 記一筆；是否回貢上游由維護者決定。

## 8. 已知限制

- 純靜態審查：沒有執行任何程式，正式版「不對外連線」是讀原始碼與 Makefile 得出的，沒有用封包側錄驗證。
- codebase-memory-mcp 的 3,726 個檔案沒有逐一人工閱讀；人工範圍是 README、`docs/CONFIGURATION.md`、`docs/WINDOWS_TROUBLESHOOTING.md`、`install.ps1`、`plugin/`、`src/cli/cli.c` 的下載與 Antigravity 安裝段、`src/foundation/workspace.c`、`src/mcp/mcp.c` 工具表、`src/ui/http_server.*` 的綁定與 CORS。`graph-ui/` 前端、`internal/` 文法與 `tests/` 只靠機器掃描。
- Antigravity 使用條款、Antigravity 在 Windows 上的 shell 與白名單內容、`127.0.0.1:4141` 的用途：未查證。
