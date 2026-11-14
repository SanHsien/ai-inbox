# Claude Code 垂直領域 Skill 與 MCP 生態系盤點及安全採納規範

> **對應任務**：`T-20261108-04`
> **來源筆記**：[notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md](../notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md)
> **驗證工具**：[`tools/verify_agent_skill_pack_safety.py`](https://github.com/SanHsien/agent-safety-checks/blob/main/tools/verify_agent_skill_pack_safety.py) ｜ [`tests/test_verify_agent_skill_pack_safety.py`](https://github.com/SanHsien/agent-safety-checks/blob/main/tests/test_verify_agent_skill_pack_safety.py)
> **修訂**：2026-11-14 依獨立審查改寫第 4 節。工具改成實際讀取技能包目錄的靜態掃描；原本「強制執行四條防線」的說法不符實況，已刪除。

---

## 1. 背景與核心洞察：從「空白 Prompt」走向「確定性 Linter + 閉環驗證」

2026 年 9 月至 11 月 Instagram 上 8 則 AI 工作流貼文，表面上都是「留言關鍵字領取連結」的私訊導流，底下指向的 GitHub 開源專案有一個共同方向：

```
[舊做法：單純 Prompt 填空]
  "幫我寫一個 X 的 Hook / 做一個好看的網頁 / 配個音效"
       │
       ▼ 缺乏量化探針與感官回饋
  [AI Slop：紫色漸層、破折號氾濫、音效慢半拍、單一模型盲目自信]

[新做法：Domain Skill Pack + Deterministic CLI + Multi-Modal/Cross-Model Critique]
  1. 前置基準鎖定 (voice.md / PRODUCT.md / DESIGN.md / 192 Palettes)
       │
       ▼
  2. 確定性本地探針 (hookscore.py / humanize.py / impeccable 62 rules / earshot LUFS & sync)
       │
       ▼
  3. 雙向對抗與人工閘門 (Claudex Loop 跨模型互審 + Human-Publish Gate 草稿唯讀)
```

---

## 2. 四大垂直領域開源工具鏈完整對照矩陣

> **查證狀態（2026-11-14）**：下表的星數是 2026-11-08 的快照，本次未重新查證。8 則 IG 貼文的內容、各專案的 Skill 數量與 CLI 子指令，除第 3 節與第 4.9 節另外註明來源者之外，都取自來源筆記，本次**未查證**。Impeccable 的「62 條決定性規則」已對照其 [README](https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md)（2026-11-14 讀取，原文 `62 deterministic rules`）。

| 領域象限 | 來源 IG 貼文 | 核心開源專案 / 工具 | GitHub Stars / 授權 | 核心確定性工具與架構機制 |
| :--- | :--- | :--- | :--- | :--- |
| **A. 影音音效自動合成與聽覺自審** | [`DfMpBTvh_Yj`](https://www.instagram.com/reel/DfMpBTvh_Yj/) (`@kwons_en`) | 1. **Openverse API**<br>2. [`hkchengrex/MMAudio`](https://github.com/hkchengrex/MMAudio)<br>3. [`Leonxlnx/earshot`](https://github.com/Leonxlnx/earshot) | MMAudio: `2,307★` (MIT)<br>Earshot: `4,156★` (MIT) | - **Openverse**：檢索 500 萬+ CC0/開放授權音效。<br>- **MMAudio**（CVPR 2025）：依影片畫面幀同步合成音訊。<br>- **Earshot**：純 CPU 本地執行 CLI/MCP，提供 `describe`、`match`、`timeline`、`sheet` 與 `critique`（對照 7 部專業宣傳片計算 23 項指標、LUFS 響度與 80ms 轉場對齊誤差），以及 `earshot forge` / `fit` 程式碼合成音效。 |
| **B. 自媒體頻道經營與去 AI 味（YouTube / IG）** | [`DfRwxagKLG9`](https://www.instagram.com/reel/DfRwxagKLG9/) (`@airi_aimagic`)<br>[`DfKHNzYq_s7`](https://www.instagram.com/reel/DfKHNzYq_s7/) (`@airi_aimagic`)<br>[`DfFHkoEOs-F`](https://www.instagram.com/reel/DfFHkoEOs-F/) (`@hsing.daily`)<br>[`DfMnV6sGAUE`](https://www.instagram.com/p/DfMnV6sGAUE/) (`@renakeung`)<br>[`DfPQ-yeEzYJ`](https://www.instagram.com/p/DfPQ-yeEzYJ/) (`@its_hana_digital`) | 1. [`Jakeschincariol/youtube-agent-skill`](https://github.com/Jakeschincariol/youtube-agent-skill)<br>2. [`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill) | YouTube: `4,992★` (MIT)<br>Instagram: `5,302★` (MIT) | - **個人語氣錨點**：先填寫 `templates/voice.md`。<br>- **YouTube 11 Skills + 6 Python 工具**：`/yt-script`（21 公式 + `hookscore.py`）、`/yt-package`（`title.py` 標題封面聯合檢查）、`/yt-edit`（`deadair.py` SRT 轉剪輯清單）、`/yt-retention`（`retention.py` 觀眾流失點定位）、`/yt-viral`（`swipe.py` 自頻道中位數倍數排名）。<br>- **IG 13 Skills + 5 Python 工具**：`/ig-reel`（26 公式 + `beats.py` 165 wpm 秒數估算）、`/ig-caption`（`caption.py` 預覽前 125 字截斷與 2025/12 新規 5 個 Hashtag 上限）、`/ig-human`（`humanize.py` 清除 18 類零寬隱藏字元與 154 個套話詞彙 + `detect.py` 5 維度評分）。 |
| **C. 前端 UI/UX 反 AI Slop 設計工具鏈** | [`DebpuRpkfnw`](https://www.instagram.com/reel/DebpuRpkfnw/) (`@chloemakesdesign`) | 1. [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)<br>2. [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)<br>3. [`21st-dev/magic-mcp`](https://github.com/21st-dev/magic-mcp)<br>4. Figma MCP & Chrome DevTools MCP | UI UX Pro Max: `146,485★` (MIT)<br>Impeccable: `105,368★` (Apache-2.0)<br>21st MCP: `6,414★` (ISC) | - **先定風格**：`UI UX Pro Max`（192 條推理規則、80 種可搜尋 UI 風格）+ `Impeccable` `/impeccable init` 產出 `PRODUCT.md` 與 `DESIGN.md`。<br>- **元件與畫稿橋接**：`21st MCP`（原 Magic MCP，檢索 10,000+ React/Tailwind 元件）+ `Figma MCP`。<br>- **確定性收尾檢查**：`npx impeccable detect` 內建 **62 條決定性規則**（不需要 LLM，抓 Inter 濫用、藍紫漸層、卡片套卡片、對比度不足），搭配 `Chrome DevTools MCP` 實機渲染巡檢。 |
| **D. 跨模型四階段計畫硬化與互審** | [`DdX7C1YP5Kj`](https://www.instagram.com/reel/DdX7C1YP5Kj/) (`@lynexaai`) | [`chaseai-yt/claudex-loop`](https://github.com/chaseai-yt/claudex-loop) | `3,374★` (MIT) | - **四階段工作流**：Recon → Interrogate → Cross-Model Adversarial Plan Review → Role-Swapped Build & Inspection。<br>- **建造者不自審（Whoever built it never grades it）**：寫計畫的模型不審計畫，寫 Code 的模型不驗 Code。<br>- **雜湊鎖定與唯讀沙盒**：核准紀錄綁定計畫檔路徑與 `SHA256`（改動計畫即失效）；審查階段跑在唯讀沙盒並關閉外部 Plugin/MCP。 |

---

## 3. CQR 實證數據與作者自己揭露的限制

社群貼文常用「爆款引擎」「自動抓出流量密碼」這類說法。以下數字都是作者自己寫在 [instagram-agent-skill README](https://raw.githubusercontent.com/Jakeschincariol/instagram-agent-skill/main/README.md) 裡的（2026-11-14 讀取核對）。本文只確認「作者這樣寫」，沒有重跑他的實驗。

1. **Hook 評分器只能淘汰爛開頭，不能預測爆款**：
   - `hookscore.py` 的語料是 5 個頻道共 74 支真實短影音的開頭，觀看數 931 至 550,000。
   - 區分「刻意寫爛的開頭」與「真實開頭」的 **AUC 為 `0.83`**。README 的範例輸出裡，被扣分的開頭包括以 `Hey guys` 打招呼、以 `Stop scrolling` 討注意力。
   - 區分「同一創作者的爆款」與「同一創作者的平庸作」的 **AUC 只有 `0.56`**（`0.50` 等於擲硬幣）。五項指標裡只有 `SPECIFICITY` 有明顯區辨力，兩組相差 60 分。
2. **模板正則與真實口語的落差**：
   - 作者最初寫的模板只對得上 **8%** 的真實開頭；改用真實逐字稿重寫，並補入 `Contrarian Flip`、`The Statistic`、`The Reveal`、`Someone Else's Result`、`The Superlative` 之後到 **49%**。剩下 51% 工具選擇不判斷，README 的說明是很多短影音是 Podcast 切片，沒有固定公式。
   - 口語裡的數字常拼成英文單字（README 的例子是 `zero dollars`、`three marketing books`），只算阿拉伯數字會誤判成不具體。
3. **Humanizer 清的是套話與隱藏字元，不是破解浮水印**：
   - `humanize.py` 處理零寬與格式字元、破折號，以及 `slop.json` 的 154 個套話詞彙（README 記載 18 類隱藏字元）。未知數字輸出 `{{your number}}` 並加上提醒。
   - README 明寫這不是破解密碼學浮水印，該 repo 也不做這種宣稱。

---

## 4. 採納前的靜態掃描：`verify_agent_skill_pack_safety.py` 做什麼、不做什麼

### 4.1 定位

- 這是**靜態啟發式掃描**。它讀取技能包目錄裡的檔案，把內容解析成 argv 等級的 token，再對照一張已知危險寫法的規則表。它不執行、不安裝、不下載任何東西。
- **通過不代表安全**。結束碼 0 只表示「掃得到的檔案裡，沒有找到規則表列出的樣式」。採納前仍然要人工審查：讀完工具列出的 REVIEW 項目、每一條 hook 與 MCP 指令，以及技能本身要模型做的事。
- 它不是沙盒，也不是惡意程式偵測器。有心要躲的人躲得掉，躲法見 4.7。

### 4.2 用法與結束碼

```bash
# 主要用法：掃描一個或多個技能包目錄
python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack path/to/pack
python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack pack-a --pack pack-b --json

# 把需要人工審查的項目也算成失敗
python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack path/to/pack --strict
```

| 結束碼 | 意思 |
| :--- | :--- |
| `0` | 通過：掃描完整，沒有 FAIL。REVIEW 項目仍須人工審查。 |
| `1` | 發現問題：至少一項 FAIL。加 `--strict` 時 REVIEW 也算。宣告模式下則是違反 `SKILLPACK` 規則。 |
| `2` | 輸入錯誤或無法掃描：沒有指定檢查對象、目錄或檔案不存在、讀不到、是空的、宣告 JSON 壞掉或結構不合法，或有檔案未掃描且沒有確認。 |

同時有 FAIL 和未掃描檔時回 `1`。

不帶 `--pack`、`--config`、`--self-test` 的裸執行什麼都沒檢查：工具會印出「採納檢查請用 --pack <目錄>」並回 `2`，不會印 `[PASS]`。

其他選項：

- `--max-bytes N`：單檔大小上限，預設 5 MiB。超過的檔案列為未掃描。
- `--ack-unscanned SHA256`：人工看過某個未掃描檔（例如圖片）之後，用它的 sha256 確認，該檔就不再讓結束碼變成 2。工具會在輸出裡印出每個未掃描檔的 sha256；檔案內容一變，確認就失效。可重複指定。
- `--config FILE`、`--self-test`：宣告模式，見 4.8。

未掃描的情況有五種：讀不到、二進位檔（內容含 NUL 位元組，且不是帶 BOM 的 UTF-16）、超過大小上限、符號連結（不跟隨）、JSON 解析失敗。JSON 解析失敗時仍會把內容當純文字掃一次，但 hook 與 scripts 無法逐項列出，所以算掃描不完整。

### 4.3 掃描範圍

工具會走訪目錄下的每一個檔案，不是只看特定檔名。處理方式依檔案類型而定：

| 檔案 | 處理方式 |
| :--- | :--- |
| `SKILL.md`、`*.md`、`*.mdx`、`*.txt`、`*.rst`、沒有副檔名的 `README`／`LICENSE` 等 | 圍欄程式碼區塊（三個以上的反引號或波浪號）當成可執行內容。其餘說明文字與行內程式碼只列 REVIEW。YAML frontmatter 的 `hooks:` 區塊、行內的驚嘆號加反引號指令、以驚嘆號開頭的圍欄區塊另外列為自動執行項目。 |
| `*.json`（含 `.claude/settings*.json`、`plugin.json`、`hooks/hooks.json`、`.mcp.json`、`package.json`） | 先解析 JSON。hook、MCP 伺服器、`scripts`、`command`／`args` 等會被執行的欄位當成可執行內容，其餘字串（例如 `description`）只列 REVIEW。 |
| `*.sh`、`*.ps1`、`*.py`、`*.js`、`*.ts`、`hooks/` 底下的檔案，以及其他所有文字檔 | 整個檔案當成可執行內容。依副檔名剝掉 `#` 或 `//`、`/* */` 註解；`.bat`、`.cmd` 與不認得的副檔名不剝註解。 |
| `.git/` | 只掃 `.git/config` 與 `.git/hooks/`。物件庫與其餘中繼資料不掃，輸出會註明。 |

### 4.4 偵測類別

嚴重度只有兩級。**FAIL** 是在可執行的位置找到已知危險樣式。**REVIEW** 是工具無法替人判斷、列出來要人看的項目，預設不影響結束碼。

| 類別 | FAIL | REVIEW |
| :--- | :--- | :--- |
| `BYPASS` 免審批／破沙盒 | 4.10 表列的旗標與設定值，例如 `--dangerously-skip-permissions`、`--dangerously-bypass-approvals-and-sandbox`、`--yolo`、`--permission-mode bypassPermissions`、`defaultMode: bypassPermissions`、`--sandbox danger-full-access`、`--ask-for-approval never` | 權限模式設為 `acceptEdits` 或 `auto`；`--approve-for-me`；不在清單上的 `--dangerously-*` 旗標；單獨出現的 `bypassPermissions` 或 `danger-full-access`（例如先存進變數，或拿來做比較） |
| `REMOTE-EXEC` 遠端內容直接執行 | 下載指令接管線到直譯器（`curl`、`wget`、`irm`、`iwr`、`Invoke-WebRequest`、`Invoke-RestMethod` 接到 `sh`、`bash`、`python`、`node`、`iex`、`Invoke-Expression` 等）；指令替換與行程替換；`iex (irm …)`、`DownloadString`；同一份檔案裡先下載再執行同名檔；程式裡同一個敘述同時出現 `exec`／`eval` 與 `urlopen`／`requests.get`／`fetch` | 無 |
| `OBFUSCATED` 無法判讀 | PowerShell 的 `-EncodedCommand`（含 `-enc`、`-e` 等縮寫）；`base64 -d` 之類的解碼結果接管線到直譯器 | 無 |
| `DYNAMIC-EXEC` 執行非字面內容 | 無（只列 REVIEW） | 參數在執行期才決定的執行：`iex $c`、`Invoke-Expression $code`、`eval "$s"`、`bash -c "$s"`（`sh`、`zsh`、`pwsh -Command` 同理）、`eval(code)`、`exec(code)`（括號內第一個參數不是字串常值）。字面內容（`eval "echo hi"`）與 `re.exec(x)` 這類方法呼叫不列。工具無法得知變數內容，所以只列出來要人看，不判 FAIL；加 `--strict` 才會讓結束碼變 1 |
| `CRED-ACCESS` 讀取 Cookie 或憑證 | Chrome／Edge／Brave 等設定檔目錄下的 `Cookies`、`Login Data`、`Web Data`、`Local State`；Firefox 的 `cookies.sqlite`、`key4.db`；`~/.aws/credentials`；`~/.ssh/id_*` 私鑰；`.netrc`、`.git-credentials`、Docker／Kubernetes／gcloud／GitHub CLI 的憑證檔；`.claude/.credentials.json`、`.codex/auth.json`；`--cookies-from-browser`、`browser_cookie3` 等工具；macOS 鑰匙圈查詢 | 無 |
| `INSTALL-EXEC` 安裝時自動執行 | `package.json` 的 `preinstall`、`install`、`postinstall` | `package.json` 的 `prepublish`、`preprepare`、`prepare`、`postprepare`；存在 `setup.py` 或 `binding.gyp` |
| `AUTO-HOOK` 審批之外自動執行 | 不會單獨 FAIL。hook 指令本身若命中其他類別，會另外列 FAIL | 列出每一條指令：任何 JSON 裡 `type: command` 的項目（含 `statusLine`）、`hooks` 底下的 `http`／`prompt`／`agent`／`mcp_tool` 項目、Skill frontmatter 的 hook、技能載入時自動執行的行內指令與指令區塊、`.git/hooks/` 裡沒有 `.sample` 結尾的檔案 |
| `MCP-SERVER` | 同上，指令命中其他類別才 FAIL | 列出 `mcpServers` 每個伺服器的啟動指令或遠端網址 |

`INSTALL-EXEC` 把任務點名的三個腳本列 FAIL，是保守的選擇：很多正常套件也有 `postinstall`，遇到時請讀過腳本內容，或安裝時加 `--ignore-scripts`。

### 4.5 比對前的正規化

比對不是找固定子字串。工具先把文字切成 token，再比對 token。以下寫法都會被還原成同一組 token：

- `--flag=value`、`--flag value`、多個空白、Tab、不換行空白、全形空白
- 單引號、雙引號，包含只包住旗標一部分的引號
- 大小寫
- 續行：行尾的反斜線、PowerShell 的反引號、cmd 的 `^`
- argv 陣列：`["claude", "--permission-mode", "bypassPermissions"]`，寫成一行或分成多行都算；JSON 的 `args` 陣列與 YAML 清單也算
- 同一行內用 `+` 相加的字串常值
- 零寬字元、全形字元、`${IFS}`
- 指令名前面的路徑與 `.exe`，`sudo`、`env`、`VAR=value` 這類前綴，指令名裡的反斜線、反引號、`^` 跳脫
- 包在引號裡的完整指令（`bash -c "…"`、`os.system("…")`、`powershell -Command "…"`）會往內再解析，最多三層
- 管線符號在行尾或下一行行首換行

`==`、`!=` 會讓前後兩個 token 不被當成「設定」，所以 `if mode == "bypassPermissions"` 這種檢查只列 REVIEW。

### 4.6 說明文字與程式碼區塊的取捨

文件裡提到旗標名稱，可能是在叫你這樣做，也可能是在警告你別這樣做。工具分不出來，所以用位置區分：

- **說明文字、行內程式碼、JSON 的 `description` 這類欄位**：一律降成 REVIEW，結束碼不變。代價是：如果 `SKILL.md` 用一般文字叫模型帶上破沙盒旗標，工具只會給 REVIEW。這就是 REVIEW 一定要有人讀的原因；不想冒這個險就加 `--strict`。
- **圍欄程式碼區塊**：當成可執行內容，命中就 FAIL。代價是：把「不要這樣做」的反面示範放進程式碼區塊也會 FAIL。這種誤報需要人工判定，工具目前沒有逐項豁免的機制。
- **縮排式程式碼區塊與 HTML**：當成說明文字。
- **腳本與程式檔裡的字串**（含 docstring 與 `echo` 的內容）：當成可執行內容。剝掉的只有註解。

### 4.7 抓不到的東西

- **執行期才組出來的內容**：變數間接（旗標或指令先存進變數再展開，最多只會有 REVIEW）、`printf`／`join`／格式化字串拼出來的旗標、相鄰字串常值的隱式相接、跨行的字串相加、從檔案或環境變數讀進來的參數。
- **各種編碼與混淆**：base64 或十六進位編碼的旗標與指令、壓縮檔、被壓縮混淆過的 JavaScript。只有 PowerShell 編碼指令與「解碼後接管線」這兩種會被標成 `OBFUSCATED`。執行變數內容的 `iex $c`、`eval "$s"`、`bash -c "$s"` 只會列 `DYNAMIC-EXEC` REVIEW，變數裡實際是什麼仍要人判斷。
- **不經管線也不經替換的遠端執行**：下載和執行分在不同檔案或不同敘述且檔名對不上；`npx`、`uvx`、`pipx run`、`pip install git+https://…` 這類直接執行遠端套件的指令；`mshta`、`regsvr32`、`certutil -urlcache` 等系統內建工具；程式裡用 HTTP 函式庫下載後再寫檔執行。
- **二進位檔與壓縮檔的內容**：只會列為未掃描。`.mcpb`、`.dxt`、`.zip`、執行檔、圖片都一樣。
- **技能包以外的東西**：`npm install` 會拉進來的相依套件、hook 或 MCP 伺服器在執行期再下載的程式、遠端 MCP 伺服器的行為。
- **不靠危險旗標的攻擊**：提示詞注入（用文字要模型外傳資料、改設定、關掉檢查）、合法指令的濫用（例如把檔案 `POST` 到外部網址）、規則表沒列的憑證路徑、遙測與資料外傳。
- **旗標清單會過期**：新版 CLI 增加或改名的旗標，要有人更新規則表才抓得到。不在清單上的 `--dangerously-*` 會列 REVIEW，其他命名方式的不會。
- **YAML**：標準函式庫沒有 YAML 解析器。frontmatter 的 hook 只認得區塊式寫法；寫成一行的 flow 樣式會被當成說明文字。
- **符號連結**：測試環境（Windows）無法建立符號連結，這條路徑的自動測試在該環境會被略過。

### 4.8 宣告模式（補充）

```bash
python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --config declaration.json
python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --self-test   # 只對內建的五組宣告範例做自檢，回 0 或 1
```

`--config` 與 `--self-test` 不能同時給。兩者都可以和 `--pack` 一起用，結束碼照 4.2 的規則合併計算：任一邊發現問題就是 `1`，否則任一邊輸入錯誤或掃描不完整就是 `2`。

宣告模式檢查的是一份**人工填寫的 JSON**，不讀任何第三方檔案。每一欄都是填寫者自述，工具無法驗證真偽：把 `hook_reviewed` 填成 `true`、把 `deterministic_tools` 填一個不存在的檔名，檢查照樣通過。所以宣告模式的結果**不能當作採納依據**，輸出與 JSON 的 `adoption_evidence: false` 都會這樣標示。它的用途是當檢查清單，提醒填寫者有沒有想過下面四件事。

| 規則 | 檢查什麼 |
| :--- | :--- |
| `SKILLPACK-001` | `cli_invocations` 裡的指令用和目錄掃描同一套解析，不能出現 `BYPASS` 類的 FAIL。`id` 為 `pbakaus/impeccable` 時，`IMPECCABLE_LIVE_COPY_AGENT` 必須填 `chat` 或 `off`。 |
| `SKILLPACK-002` | `config.telemetry` 填 `false`、`config.hook_reviewed` 填 `true`、`config.disable_hooks_flag` 不是空的。 |
| `SKILLPACK-003` | `human_publish_only` 填 `true`；`unknown_metric_placeholder` 是 `{{…}}` 形式的佔位符。 |
| `SKILLPACK-004` | `deterministic_tools` 不是空的；`claims` 裡沒有 `100% undetectable`、`guaranteed viral` 這類字眼。 |

宣告檔不存在、不是合法 JSON、`packs` 是空的或欄位型別不對，結束碼是 `2`。違反上表規則是 `1`。

### 4.9 實際案例：為什麼要看 hook 和背景指令

以下內容對照 [Impeccable README](https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md)（2026-11-14 讀取）。本文沒有安裝或執行 Impeccable。

- **Live Mode 的後備路徑**：README 寫明，在瀏覽器按 Apply 時，如果過去一分鐘沒有聊天 session 在輪詢，Live Server 會改從 `PATH` 執行 `codex`（沒有 codex 時用 `claude`），而且關掉審批、權限檢查與沙盒（`--dangerously-bypass-approvals-and-sandbox` 或 `--permission-mode bypassPermissions`），並繼承你的環境變數。README 給的關法是在啟動 Live Mode 的環境設 `IMPECCABLE_LIVE_COPY_AGENT=chat`，或設成 `off` 停用 Apply。
- **套用文案修改會跑專案腳本**：README 寫明這個動作會以你的權限執行 `package.json` 裡選用的 `impeccable:manual-edit-validate` 腳本。
- **hook 不受模型審批管**：README 寫明在 Claude Code 裡，已安裝的 command hook 在你拒絕模型自己的指令時照樣會跑，所以第一次編輯就可能下載引擎；它建議無人值守前先檢視 hook，或用 `--settings '{"disableAllHooks": true}'` 關掉。引擎二進位檔在技能旁邊，或下載一次到 `~/.impeccable/bin/`。Claude Code 官方文件對 command hook 的說法是：以你完整的使用者權限執行 shell 指令（[Hooks reference](https://code.claude.com/docs/en/hooks)）。
- **遙測**：README 寫明新設計開始時會向 impeccable.style 取一組視覺方向，關掉遙測不會停掉這個請求，只會停掉「顯示了哪些、你選了哪個」的匿名紀錄。關法是 `npx impeccable telemetry off`、`DO_NOT_TRACK=1`，或在 `.impeccable/config.json` 寫 `"telemetry": false`。

這類行為寫在 README 與原始碼裡，不會出現在一份自填的宣告裡。要用 `--pack` 掃實際檔案，並人工讀過 hook。

另外兩項屬於使用習慣，工具不檢查，只在宣告模式提醒：

- **人工發佈**：社群平台類的 Skill 只產出本地草稿與檢查報告，不用非官方爬蟲或無頭瀏覽器自動代發貼文、留言或私訊。
- **不捏造數字**：使用者沒提供的案例數字或成效指標，保留 `{{your number}}` 佔位符。

### 4.10 規則來源

以下連結都在 2026-11-14 讀取。標「未查證」的項目是沒有找到或沒有去找一手來源，仍列入規則是因為誤報的代價比漏報低。

| 規則 | 來源 |
| :--- | :--- |
| `--dangerously-skip-permissions`（等同 `--permission-mode bypassPermissions`）、`--allow-dangerously-skip-permissions`、`--permission-mode` 可用的值 | [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference) |
| `permissions.defaultMode: "bypassPermissions"`；各權限模式的行為 | [Claude Code permission modes](https://code.claude.com/docs/en/permission-modes)。該頁同時寫明這個值放在專案的 `.claude/settings.json` 或 `.claude/settings.local.json` 不會生效；工具仍列 FAIL，因為同一份設定可能被複製到使用者層級。 |
| `skipDangerousModePermissionPrompt`、`enableAllProjectMcpServers`、`statusLine`、`disableAllHooks` | [Claude Code settings reference](https://code.claude.com/docs/en/settings-reference) |
| Agent SDK 的 `permissionMode: 'bypassPermissions'`、`allowDangerouslySkipPermissions: true` | [Agent SDK permissions](https://code.claude.com/docs/en/agent-sdk/permissions) |
| hook 的五種 `type`（`command`、`http`、`mcp_tool`、`prompt`、`agent`）；hook 可以放在 settings、plugin 的 `hooks/hooks.json`、Skill 與 subagent 的 frontmatter | [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) |
| `plugin.json` 的 `hooks` 與 `mcpServers` 可以是路徑或內嵌設定；hook 檔可以只有事件對照表 | [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) |
| Skill 內文的行內指令（驚嘆號加反引號）與驚嘆號開頭的圍欄區塊，會在內容送給模型之前執行 | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| 專案層級 `.mcp.json` 的伺服器需要核准 | [Claude Code MCP](https://code.claude.com/docs/en/mcp) |
| `--dangerously-bypass-approvals-and-sandbox` 與別名 `--yolo`、`--dangerously-bypass-hook-trust`、`--sandbox`／`-s` 的值 `danger-full-access`、`--ask-for-approval`／`-a` 的值 `never`、`--approve-for-me` 與別名 `--not-so-yolo` | [Codex CLI reference](https://developers.openai.com/codex/cli/reference) |
| 設定鍵 `approval_policy`、`sandbox_mode` | [Codex config reference](https://developers.openai.com/codex/config-reference)。只查到鍵名；設定檔可填的值沒有逐一查證，工具沿用 CLI 旗標的值。 |
| `--full-auto` | **未查證**。2026-11-14 的 Codex CLI reference 與本機 `codex-cli 0.167.0-alpha.4.1` 的 `--help` 都沒有這個旗標。 |
| 其他 CLI（例如 Gemini CLI）的 `--yolo` | **未查證**。工具不分 CLI，看到 `--yolo` 就列 FAIL。 |
| `npm install` 會執行 `preinstall`、`install`、`postinstall`、`prepublish`、`preprepare`、`prepare`、`postprepare`；有 `binding.gyp` 且沒有自訂 `install`／`preinstall` 時預設跑 `node-gyp rebuild` | [npm scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts) |
| `setup.py` 在 `pip install` 時執行 | **未查證** |
| Chromium 的使用者資料目錄存放 Cookie 等設定檔資料 | [Chromium user data directory](https://chromium.googlesource.com/chromium/src/+/main/docs/user_data_dir.md)。該頁沒有列出 `Cookies`、`Login Data` 等檔名，檔名**未查證**。 |
| `--cookies-from-browser` 會讀取並解密瀏覽器 Cookie | [yt-dlp README](https://github.com/yt-dlp/yt-dlp/blob/master/README.md) |
| `~/.aws/credentials` | **未查證**。[AWS CLI 文件](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)是動態載入，本次沒有讀到內文。 |
| Firefox 的 `cookies.sqlite`／`key4.db`、SSH 私鑰、`.netrc`、`.git-credentials`、Docker／Kubernetes／gcloud／GitHub CLI 憑證檔、`.claude/.credentials.json`、`.codex/auth.json`、`browser_cookie3`／`pycookiecheat`／`rookiepy`、`CryptUnprotectData`、macOS 鑰匙圈指令 | **未查證**。依常見路徑與工具名稱列入。 |
