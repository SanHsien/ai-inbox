# Ego Lite（citrolabs/ego-lite）唯讀安全審查：不安裝，只借鏡交接與清除範圍兩個設計

審查日期：2026-11-20。任務：T-20261120-01。作者：Claude Code。
來源筆記：[`notes/2026-11-20-citrolabs-ego-lite-browser-handoff-eval.md`](../notes/2026-11-20-citrolabs-ego-lite-browser-handoff-eval.md)。

**結論：不安裝、不匯入任何瀏覽器資料；部分借鏡。** 公開 repo 的內容（MIT）沒有找到惡意 hook、遠端下載後執行、遙測或寫死的對外主機。但真正接觸登入狀態的部分（瀏覽器本體、`ego-browser` 啟動器、Chrome 資料匯入、更新、資料蒐集）都在**不開源的應用程式**裡，靜態審查看不到。看得到的部分已足以判斷：它的 Space 是分頁層級的隔離，不是憑證層級的隔離，agent 腳本能讀到整個設定檔的 Cookie。這與本機「不把主瀏覽器 Cookie 交給外部工具」的規則衝突。

## 1. 來源與審查範圍

- Repo：[citrolabs/ego-lite](https://github.com/citrolabs/ego-lite)。
- 審查 commit：`f499162d1b911ba9b320ed31b741dba7ebc2e4d6`（2026-11-16，`Merge pull request #739 from citrolabs/hotfix/release-v2.2.1-beta.3`）。
- 取得方式：`git clone --depth 1`，加上 `-c core.hooksPath=NUL -c core.symlinks=false`，放在 `C:\GitHub\_sandbox\ego-lite-audit`。只讀文字；沒有執行其中任何腳本、沒有安裝套件、沒有下載或啟動它的瀏覽器與 CLI。
- 規模：296 個追蹤檔。主要是 `package/ego-browser/`（SDK 原始碼與測試）、`skills/ego-browser/`（進入用技能）、`plugins/ego/`（各 agent 主機的外掛包裝，內含同一份技能的複本）、`tools/linear-autofix/`（上游自己的開發工具，不隨產品發布）。
- 本文路徑都是該 repo 內的相對路徑，行號對應上述 commit。

```text
開源與閉源的分界（AGENTS.md:5、:7；README.md:157）

agent CLI（Claude Code、Codex…）
   │  ego-browser nodejs < task.mjs
   ▼
ego-browser 啟動器 ─────────── 閉源：子指令 nodejs／skill／upgrade、PATH 註冊
   │  載入 index.js
   ▼
SDK（package/ego-browser/src） ─ 開源 MIT：本次審查範圍
   │  globalThis.ego 繫結（sendCDPMessage、createTaskSpace、handOffTaskSpace…）
   ▼
ego lite 應用程式（Chromium 分支）─ 閉源：Space 隔離、控制權判定、
                                    Chrome 資料匯入、更新、資料蒐集
```

沒有做的事：沒有動態執行；閉源應用程式沒有取得也沒有檢查；`.git` 物件庫與 10 個二進位檔（圖片、字型、1 份測試用 PDF）沒有檢查內容；`lite.ego.app` 文件站與隱私權政策沒有讀。

## 2. 授權

| 對象 | 授權 | 證據 |
| --- | --- | --- |
| 本 repo 全部內容（SDK、技能、外掛包裝） | MIT，著作權人 CitroLabs。可商用、可修改、可再散布，需保留著作權與授權聲明 | `LICENSE:1-21`；`package/ego-browser/package.json:23`；GitHub API 回報 `MIT` |
| ego lite 瀏覽器本體 | **未查證**。README 只說是「另外提供的免費下載」，repo 內沒有它的授權條款或使用條款 | `README.md:157` |
| `.github/star-history/` 的字型 | 另有字型授權檔，不影響使用 | `.github/star-history/FONT-LICENSE.txt` |

MIT 只涵蓋驅動層。少了閉源瀏覽器，這份 SDK 沒有可連的對象（`helpers.ts:102-103`、`:372-373` 等處在沒有 `globalThis.ego` 時直接報錯），所以「開源」不等於可以自行建置出整套工具。

## 3. 機器掃描結果

指令：`python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack <目錄>`，跑了兩個範圍。

| 範圍 | 結束碼 | 摘要 |
| --- | --- | --- |
| 整個 clone | **1** | 掃描 301 個檔案：FAIL 1 項、需人工審查 2 項、未掃描 10 個 |
| `skills/ego-browser`（進入用技能） | **2** | 掃描 22 個檔案：FAIL 0、需人工審查 0、未掃描 2 個（兩張 PNG），因此判為無法完整掃描 |

| 命中 | 位置 | 人工判讀 |
| --- | --- | --- |
| FAIL：遠端內容接管線執行 | `.github/workflows/purge-camo-cache.yml:14-17` | 誤判。在上游的 GitHub Actions 裡抓自己的 README，把其中的圖片快取網址逐一送 `PURGE`；`sh -c` 只執行 `echo` 與 `curl`，不執行抓回的內容，也不會在使用者機器上跑 |
| REVIEW：動態執行 | `.git/hooks/pre-receive.sample:14` | 無關。這是 git 自帶的範例檔，不是 repo 內容 |
| REVIEW：安裝時執行 | `package/ego-browser/package.json:14` | 屬實但影響有限。在該目錄跑 `npm install` 會執行 `lefthook install`，把 `lefthook.yml` 的 pre-commit、pre-push、post-commit 裝進 `.git/hooks`。只影響想開發這個 repo 的人；本次沒有安裝 |
| 未掃描 | 10 個二進位檔 | 沒有檢查內容 |

掃描器沒有抓到、人工讀出來的項目見第 4 節 F4、F6、F7：它們是寫給 agent 的指示文字與安裝腳本裡的系統防護繞過，不在目前的比對規則內。

## 4. 人工檢閱的發現

| 編號 | 發現 | 證據 | 風險 |
| --- | --- | --- | --- |
| F1 | Space 與使用者的分頁共用同一個設定檔的 Cookie 與快取。上游自己的文件寫明：從 agent 的 Space 量測，當前頁面只看得到 1 個 Cookie，設定檔共有 3478 個、橫跨 1161 個網域 | `skills/ego-browser/references/clearing-state.md:3`；`docs/native-bindings-api.md:158-160` | **高**。隔離的是分頁與視窗，不是登入狀態 |
| F2 | agent 腳本可用 `page.cdp()` 送出任意 CDP 指令，SDK 只擋參數裡夾帶 `sessionId`，不過濾方法名稱。上游範例直接示範 `Network.getAllCookies` | `package/ego-browser/src/page-model.ts:2472-2499`、`:4419-4438`；`clearing-state.md:48` | **高**。腳本在 Node 行程內執行（`src/run.ts:96-101`），可讀寫本機檔案、可用 Node 的 `fetch` 對外連線（`skill-body/SKILL.md:480-481`）。讀到的 Cookie 要送去哪裡，完全由 agent 寫的腳本決定；遇到頁面內的提示詞注入時沒有技術上的攔阻 |
| F3 | 建立 Space 時不指定設定檔，就用「目前使用中的一般設定檔」。首次啟動會問是否搬移 Chrome 資料，同意後 agent 取得既有的登入、Cookie、擴充功能與書籤 | `docs/native-bindings-api.md:494-496`；`README.md:77`、`:35`；`skills/ego-browser/references/install.md:31` | **高**。匯入的實作在閉源應用程式內：讀哪些檔、是否解密已存密碼、存到哪裡，**未查證** |
| F4 | 控制權只靠提示文字約束。`handOff()`、`takeOverTaskSpace()`、`claimTaskSpace()` 在 SDK 都是直接轉呼叫原生繫結；原生 `claimTaskSpace` 的文件寫明可以認領「使用者自己建立的一般 Space」。「不要自行拿回控制權」是錯誤訊息裡寫給 agent 的句子 | `src/page-model.ts:927-932`；`src/helpers.ts:361-380`、`:492-502`；`docs/native-bindings-api.md:532-536`；`src/ego-errors.ts:53-66` | 中。原生端是否另有使用者確認，**未查證** |
| F5 | 公開原始碼沒有遙測、沒有寫死的對外主機。`src/` 非測試檔內的網址只有範例與字串組合用的 `https://`；更新提示只讀原生端回報的版本資訊，不自行連線 | `src/update-notice.ts:14-35`；`src/http.ts:9-22`（只有呼叫端給網址才連線） | 低（僅限開源部分）。README 承認應用程式會蒐集「簡單的產品訊號」，例如是否設為預設瀏覽器；蒐集項目清單與傳送目的地在閉源端，**未查證**（`README.md:89`） |
| F6 | 進入用技能的 `description` 要求 agent「需要瀏覽器時預設讀這份技能」「優先使用 ego-browser，而不是內建瀏覽器或其他網頁工具」 | `skills/ego-browser/SKILL.md:3` | 中。這是寫給 agent 的指示，效果是搶走既有瀏覽器工具的路由。依本 repo 規則記為風險，不照做 |
| F7 | 真正的使用指引不在技能檔裡，而是執行 `ego-browser skill` 時由已安裝的應用程式印出，升級後內容跟著變 | `skills/ego-browser/SKILL.md:12-20`；`docs/ego-browser-skill-command.md:44-62` | 中。本次讀的 `package/ego-browser/skill-body/SKILL.md`（580 行）只代表這個 commit；裝在機器上的版本印出什麼，審查技能目錄看不到 |
| F8 | 應用程式每次啟動都檢查 `~/.agents/skills/ego-browser`，不存在就寫入技能；README 說安裝後會把技能加到機器上「每個 agent 的技能目錄」 | `docs/ego-browser-skill-command.md:86-98`；`README.md:55` | 中。安裝一個瀏覽器，就等於替所有 agent 加了一份帶有 F6 文字的技能。已有的同名技能不會被覆蓋 |
| F9 | Windows 沒有安裝腳本，文件教 agent 在 SmartScreen 擋下時請使用者選「仍要執行」；macOS 腳本下載 DMG 後不驗雜湊、移除隔離屬性、必要時用 `sudo` | `skills/ego-browser/references/install-windows.md:7`、`:57`；`skills/ego-browser/scripts/install.sh:161`、`:187-188`、`:41-53`、`:72` | 中。安裝檔來自 `cdn.ego.app`，簽章狀態**未查證**。另外腳本內的 DMG 網址與 README 的下載連結檔名不同（`install.sh:7-8` 對 `README.md:10-12`），腳本可能裝到較舊的版本 |
| F10 | 頁面工作階段會對 CDP 隱藏主控台訊息，文件寫明目的是讓網站偵測不到自動化 | `package/ego-browser/skill-body/SKILL.md:404-407` | 低至中。用登入中的個人帳號做規避偵測的自動化，風險落在帳號被平台停權，與本機安全無關但要知道 |
| F11 | 沒有 Claude Code hook、沒有 MCP 伺服器、沒有遠端除錯埠 | 外掛清單只有名稱、版本、圖示（`plugins/ego/.claude-plugin/plugin.json:1-11`）；`plugins/ego/index.js:11-46` 只把技能路徑加進 OpenCode 設定；全庫搜尋 `PreToolUse`、`SessionStart`、`mcpServers` 只命中一個測試檔，內容是斷言「沒有 `mcpServers`」（`plugins/ego/tests/cross-host-plugin.test.mjs:79`）；全庫搜尋 `remote-debugging`、`9222`、`user-data-dir` 無命中。CDP 走原生繫結 `ego.sendCDPMessage`，不開 TCP 埠 | 無 |
| F12 | 剪貼簿：`keyboard.paste()` 在 Windows 會啟動系統內建的 `powershell.exe` 暫時改寫剪貼簿，貼完再還原 | `package/ego-browser/src/clipboard.ts:116-119`、`:209-217`；`skill-body/SKILL.md:345-348` | 低。期間使用者原本的剪貼簿內容會經過這個行程；還原失敗時會報錯（`clipboard.ts:37`） |

上游做得好的地方也記下來：指引要求遇到登入、驗證碼、兩步驟驗證時交給使用者而不是猜密碼（`skill-body/SKILL.md:545-548`）；會登出整個設定檔的清除指令要先取得使用者同意，並先說明代價（`clearing-state.md:60-64`）；不主動檢視或選擇設定檔（`skill-body/SKILL.md:134-136`）；升級要先問使用者（`skill-body/SKILL.md:571-574`）。這些都是提示文字層的約束，不是技術限制。

## 5. Windows CLI 的 `handOff` 流程

```text
第 N 輪（agent）                    使用者                     第 N+1 輪（agent）
────────────────                    ──────                     ──────────────────
寫 round-01.mjs（UTF-8）
ego-browser nodejs < round-01.mjs      （cmd）
ego-browser nodejs -e "await import('file:///…/round-01.mjs')"   （PowerShell）
  taskSpace("目標") → Page p1
  goto → 遇到登入／驗證碼／兩步驟驗證
  await task.handOff()
  結束本輪、說明要使用者做什麼
     ownership: agent ──▶ agentDelegatedToUser
                                    在瀏覽器裡親手登入
                                    回覆「繼續」
                                                               takeOverTaskSpace(id)
                                                               task.userPage() → 必要時 adopt
                                                               ownership ──▶ agent
完成後另開一支腳本：task.finish({ keep: [] })
```

依據：`skill-body/SKILL.md:40-66`（Windows 各 shell 的執行方式）、`:491-502`（三種所有權狀態）、`:539-557`（交接與接回）、`:518-530`（收尾）。

| 項目 | 有沒有證據 | 位置 |
| --- | --- | --- |
| Windows 安裝檔 | 有。README 提供 `cdn.ego.app` 的 x64 `.exe` 連結 | `README.md:12`、`:43` |
| Windows 專用指引 | 有。建置時依平台挑段落，產出 `SKILL.windows.md`，涵蓋 Git Bash、PowerShell、cmd | `skill-body/SKILL.md:17-84`；`docs/ego-browser-skill-command.md:28-30`、`:51-57` |
| Windows 專用程式碼 | 有。剪貼簿與鍵盤處理依 `process.platform` 分支 | `src/clipboard.ts:119`、`:209-217`；`src/driver/page-keyboard.ts:294` |
| Windows CI | **沒有**。五個 workflow 全部跑在 Ubuntu | `.github/workflows/ci.yml:20`、`:54` 等 |
| Windows 實機測試 | **未查證**。真實瀏覽器的端對端測試是開發者本機的 pre-push hook，repo 內看不出在哪個平台跑；偵錯用的覆寫路徑只寫了 macOS 的位置 | `lefthook.yml:68-78`；`docs/ego-browser-skill-command.md:48` |
| `handOff` 在 Windows 的實際行為 | **未查證**。SDK 端與平台無關，行為由閉源應用程式決定 | `src/page-model.ts:927-932` |

Windows 上要注意的坑（都來自上游指引）：PowerShell 5.1 會吃掉引號，多行腳本要寫成 `.mjs` 檔再載入；腳本不繼承呼叫端的環境變數與工作目錄，路徑都要寫絕對路徑（`skill-body/SKILL.md:44-58`、`:91-96`）。

## 6. 筆記主張對照

| 筆記主張 | 查證結果 |
| --- | --- |
| 開源的人機協作瀏覽器 | **部分不符**。開源的只有驅動 SDK 與技能；瀏覽器本體閉源（`AGENTS.md:5`、`:7`） |
| Skill `v2.2.1` | 相符（`skills/ego-browser/SKILL.md:5`；`plugins/ego/plugin.json:4`） |
| `ego-browser 0.6.3.17`、Chromium 156、Node v24.22.1 | **未查證**。這些是閉源應用程式的版本，repo 內沒有對應數字 |
| `TaskSpace` 隔離 | **需更正說法**。隔離的是分頁與控制權，Cookie 與快取與使用者共用（F1） |
| 不搶佔主滑鼠視窗 | **未查證**。README 有此宣稱（`README.md:33`、`:96-97`），實作在閉源端；repo 內有一支在 macOS 重現「頁面開出彈出視窗時 ego lite 被帶到前景」的腳本（`package/ego-browser/scripts/repro-popup-foreground.sh:5-6`），表示這類問題出現過 |
| 遇兩步驟驗證「自動」`handOff` | **需更正說法**。不是瀏覽器自動偵測，而是指引要求 agent 自己判斷後呼叫 `task.handOff()`（`skill-body/SKILL.md:545-548`）。瀏覽器只在權限提示、裝置選擇器這類情況自動把控制權交給使用者（`src/ego-errors.ts:74-101`） |
| `ego-browser import` 可匯入 Chrome／Edge／Brave 設定檔 | **未查證**。repo 內找不到 `ego-browser import` 這個子指令，也沒有 Edge、Brave 字樣；只有「首次啟動時在圖形介面選擇是否匯入 Chrome 或其他瀏覽器的資料」（`skills/ego-browser/references/install.md:31`） |
| `ego-browser upgrade`、`ego-browser skill` | 相符，但實作在閉源啟動器；repo 只有契約文件與提示文字（`docs/ego-browser-skill-command.md:44-84`；`src/update-notice.ts:30-35`） |
| 語意快照省 token | **未查證**。快照由原生端產生；效能數字是上游自己跑的 31 題評測（`README.md:122-130`） |
| Windows 版已在 `citrolabs/ego-lite/releases` 推出 | **需更正說法**。GitHub Releases 的附件只有 SDK 壓縮檔（2026-11-20 以 GitHub API 查得 `v2.2.1` 的附件是 `ego-browser-v2.2.1.zip`，與 `.github/workflows/ci.yml:102-107` 一致）。Windows 安裝檔在 `cdn.ego.app`；WinGet 清單目錄 `manifests/c/CitroLabs/EgoLite` 存在（同日以 GitHub API 查得）。「Windows 版已推出」本身成立，網友留言確實過時 |

## 7. 最小權限判斷與分工結論

任務第 2 步要驗證「不會未經允許存取主瀏覽器的敏感憑證」。**無法驗證為符合**：

- 匯入與否由使用者在首次啟動時決定，這一步有經過同意；但匯入之後，任何 agent 腳本都能讀到整個設定檔的 Cookie（F1、F2），之後不再逐次詢問。
- 匯入的實作、資料蒐集、更新機制都在閉源端，無從確認範圍。
- 因此，若日後要試用，前提是**不匯入任何既有瀏覽器資料**，只在 ego lite 內用測試帳號另外登入；而且要當作「這個設定檔裡的所有登入狀態，agent 都拿得到」來規劃。

| 情境 | 建議工具 | 理由 |
| --- | --- | --- |
| 讀公開網頁、抓資料 | 現有的內建瀏覽器工具、Antigravity 的 `browser` subagent | 不帶登入狀態，被注入時損失最小 |
| 自己的網站做測試與驗收 | Playwright（獨立、用完即丟的設定檔） | 可重現、可進 CI、有 Windows 支援的公開證據 |
| 需要登入的網站 | 現有的瀏覽器擴充功能路線，或請使用者親手操作 | 權限由擴充功能的網站允許清單控管，審批在 agent 之外 |
| 需要「agent 做到一半交給人、人做完再交回」 | 目前沒有對應工具。**不因此引入 ego lite**；需要時用「停下來請使用者操作、回覆後再繼續」的對話流程代替 | ego lite 的交接設計值得參考，但代價是把整個設定檔交給 agent 腳本 |

## 8. 對本機現有做法的建議

都沒有動手，只列出要改哪裡：

1. **`C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py`**：補兩類目前抓不到的寫法，先在該 repo 的測試補反例再改規則。（a）移除系統防護的指令，如 `xattr -d com.apple.quarantine`（本次 `install.sh:72`、`:187` 沒被抓到）；（b）技能 `description` 裡要求 agent 優先使用自己、取代其他工具的句子（本次 `SKILL.md:3`），列為需人工審查即可，不必判 FAIL。
2. **同一支工具**：進入用技能目錄因為兩張 PNG 而回報結束碼 2。這是設計上的保守做法，不建議改；但採納流程的說明可以補一句「只有圖片未掃描時，人工確認是圖片後可視為已處理」。
3. **本機瀏覽器操作相關的技能文件**（例如 `~/.claude/skills/browser-qa/SKILL.md`）：可借鏡 `clearing-state.md` 的做法，加一張「清除指令影響範圍」對照表（單一 Cookie、單一來源、整個設定檔），並規定整個設定檔的清除要先問。這是純文字規則，不需要安裝任何東西。借用時註明出處（repo、上述 commit、原檔路徑；內容為 MIT）。
4. **不新增安裝任務**。若日後有人提議試用，先讀第 4 節 F1 至 F3 與第 7 節的前提。

## 9. 已知限制

- 只做靜態閱讀，而且只涵蓋開源的驅動層。安全性的關鍵（Space 隔離是否確實、控制權是否由原生端強制、匯入讀了什麼、蒐集了什麼、安裝檔有沒有簽章）都在閉源應用程式內，本報告對這些一律標為未查證。
- `package/ego-browser/src/page-model.ts` 超過 4500 行，沒有逐行讀完；以搜尋找出 CDP 轉送、控制權、設定檔、對外連線相關的段落後人工閱讀。搜尋樣式以外的寫法可能漏掉。
- `tools/linear-autofix/` 是上游的內部自動化工具，只搜尋了略過權限的旗標（無命中），沒有細讀。
- 審查對象是單一 commit；上游在審查當天仍有推送，之後的版本要重審。
