# REA + CLI-Anything 逆向分析與功能重造流水線規格 (Reverse Engineering Pipeline Spec)

> 本規格文件收錄於 `docs/reverse-engineering-pipeline-spec.md`，定義 Coding Agent 用本機工具走完「觀測行為 → 理解結構 → 重造功能」的工作流，並附一次對開源應用的實測（第 3 節）。以 ai-inbox 範本形式交付。

> **2026-11-21 更正**（依據：<https://github.com/morluto/rea> 與 <https://github.com/HKUDS/CLI-Anything> 的 README，查閱日 2026-11-21）。第 1～3 節的原稿是 2026-10 依筆記寫的設計稿，下列幾處與兩個上游的實際情形不符。**2026-11-22 已依這份更正改寫第 1～3 節**（見第 5 點），以下保留當時的更正內容，「第 N 節」指改寫前的原稿：
> 1. **CLI-Anything 不能拿來探測封閉的執行檔**。上游 README 的限制一節寫明它的 7 階段流程是**讀原始碼**來產生 CLI，只有編譯後二進位的軟體不在支援範圍；「把封閉軟體與網路服務包成 CLI」還列在待辦清單上。第 3 節步驟 1 的 `cli-anything probe --target ...` 這個指令**上游沒有**，是示意寫法；第 1.1 節的「動態參數探測」與輸出檔 `execution_trace.json` 也不是上游功能。本流水線的「行為觀測」階段實際上要靠 REA 的執行期與網路紀錄功能或人工操作。
> 2. **REA 的工具名稱是示意**。第 2 節的 `asar_extract`、`js_beautify` 與第 3 節的 `rea_unpack_asar` 在上游 repo 以程式碼搜尋找不到（0 筆）。上游有文件的入口是 `npx rea-agents setup`（向 agent 註冊 MCP 與調查技能）與命令列 `rea-agents analyze-javascript-application <目錄或 ASAR> --json`；實際的 MCP 工具名稱以安裝後列出的為準【未查證】。
> 3. **原生二進位的分析引擎**：README 寫的是 Hopper、Ghidra、IDA 或 Kuna（用本機已裝的，Hopper 可在同意後由 setup 安裝）；涵蓋範圍含原生二進位、JavaScript／Electron、網站、.NET、Android App、韌體與錄下的執行期／網路活動。README 沒有點名 JADX，第 1.1 與第 2 節的「JADX」沿用筆記【未查證】。
> 4. 第 3 節整段（封閉 Electron 轉檔軟體、SHA-256 水印）是**虛構的示意情境**，沒有對應的實測。REA 為 MIT 授權。
> 5. **2026-11-22 重做**：第 3 節換成對開源的 Electron 預設應用（MIT）實際走通的紀錄，指令與輸出都是實跑結果；第 1.1 節矩陣與第 2 節的工具名稱改成實際用到、查得到的（`@electron/asar`、`rea-agents analyze-javascript-application`、`playwright-core`）。上面第 1、2 點列的 `cli-anything probe`、`execution_trace.json`、`asar_extract`、`js_beautify`、`rea_unpack_asar` 上游都沒有，已從正文移除；虛構的轉檔軟體範例與 `tools/media_watermark.py` 一併刪除。沒有驗到的部分列在 3.4。

---

## 1. 架構概述與工具矩陣

軟體分析有兩個常見難處：只看得到行為、看不到結構；以及靠 GUI 點擊觀測不穩定。本流水線把工作拆成「觀測行為 → 理解結構 → 重造功能」三段，每一段都留下可重跑的指令與輸出當證據。第 3 節是 2026-11-22 對一個開源應用實際走通的紀錄。

### 1.1 工具責任矩陣與架構決策

| 工具組件 | 角色與責任邊界 | 採用狀態 | 決策理由與輸入輸出契約 |
| :--- | :--- | :--- | :--- |
| **應用自己的命令列＋Playwright** | **行為觀測與操控層**<br>以旗標、環境變數操作目標並擷取 stdout／stderr／結束碼；有視窗時用 `playwright-core` 的 `_electron` 讀 DOM 文字 | **核心採用（第 3 節實測）** | 輸入輸出都是文字，可逐案重跑比對，不需要截圖。<br>輸出：每個輸入對應的 stdout、stderr、結束碼、行程是否自行結束。 |
| **CLI-Anything** | **有原始碼時的 CLI 包裝產生器**<br>上游的 7 階段流程是讀原始碼產生 CLI 外掛 | **選用（第 3 節未使用、未實測）** | 上游 README 寫明只有編譯後二進位的軟體不在支援範圍，所以它不能當封閉軟體的行為探針；目標有原始碼且想要一套 `--json` 命令列時才用。把重造結果包成 Skill 的做法見 [`docs/cli-anything-to-skill-protocol.md`](cli-anything-to-skill-protocol.md)。 |
| **REA (morluto/rea)** | **結構理解與逆向核心**<br>JavaScript／Electron 應用的結構圖（ASAR 清點、BrowserWindow、preload、IPC 頻道），以及 README 列出的原生二進位、網站、.NET、Android、韌體、執行期／網路紀錄 | **核心採用（第 3 節實測 JavaScript 應用分析一項）** | 第 3 節用的是有文件的命令列入口 `rea-agents analyze-javascript-application <目錄或 ASAR> --json`。<br>輸出：一份帶 SHA-256 的 Evidence JSON（節點、邊、IPC 摘要、限制清單）。原生二進位要搭配本機已裝的 Hopper、Ghidra、IDA 或 Kuna，第 3 節沒有用到。 |
| **`@electron/asar`** | **ASAR 清點與解包** | **核心採用（第 3 節實測）** | Electron 官方的封存工具，`asar list`、`asar extract` 兩個指令。<br>輸出：解包後的檔案目錄。 |
| **desktop-sense** | **本機螢幕截圖與 OCR 視覺感知** | **【選用、未採用】** | **未採用理由**：<br>1. **隱私與安全防線**：全域截圖容易在公開對話或日誌中洩漏桌面機密與個人隱私；而且它不是純本機工具——依上游 README，程式本身不連網，但預設的背景分析會把最新截圖與去識別化的 OCR 文字透過使用者自己的 `claude` CLI 送到雲端模型，自動研究會把錯誤訊息送去網路搜尋，要改用全本機模式或關掉 `analyzer.enabled`、`research.enabled` 畫面才不離開本機（2026-11-16 補，見[來源筆記](../notes/2026-10-18-desktop-sense-local-screen-context.md)第 0 段）；<br>2. **效率低下**：多模態截圖 Token 消耗巨大且有坐標抖動；<br>3. **有不截圖的替代做法**：第 3 節的觀測全靠命令列輸出與 Playwright 讀 DOM 文字完成，沒有用到截圖。這只代表該案例不需要，不代表所有目標都不需要。 |

---

## 2. 三階段流水線運作模型 (Pipeline Lifecycle)

```text
[階段一：行為觀測]             [階段二：結構逆向]              [階段三：無菌重造]
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ 應用自己的命令列  │          │ @electron/asar   │          │  Cleanroom Spec  │
│ Playwright 讀 DOM │ ──觀測─▶│ rea-agents 分析  │ ──規格─▶│  獨立重寫        │
│ 記錄輸出與結束碼  │   紀錄   │ 讀解包後的程式   │          │  逐案與原版比對  │
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

### 階段一：動態行為觀測 (Behavior Observation)
1. **目標啟動**：用應用自己的命令列旗標啟動，或以 Playwright 的 `_electron.launch()` 啟動並取得視窗。
2. **記錄可觀測結果**：每個輸入記下 stdout、stderr、結束碼，以及行程會不會自己結束。目標有網路行為時，再用 REA 的執行期／網路紀錄功能（第 3 節的目標沒有網路行為，這一項未實測）。
3. **邊界探測**：試缺參數、不認得的旗標、旗標順序對調，把「看起來怪」的結果留給階段二解釋。

### 階段二：結構反編譯與靜態分析 (Structural Decompilation)
1. **依目標類型選工具**：
   - **Electron 應用**：`asar list`／`asar extract` 解開 `app.asar`（或 `default_app.asar`），再用 `rea-agents analyze-javascript-application` 取得視窗、preload、IPC 的結構圖。
   - **網頁／前端應用**：同一個 `analyze-javascript-application` 入口吃目錄；壓縮過的 bundle 怎麼還原，第 3 節的目標沒有壓縮，未實測。
   - **Android APK／原生二進位**：依 REA README 搭配本機已裝的反編譯引擎；本文件未實測，T-20261019-09 的紀錄見 [`docs/rea-sandbox-evaluation-evidence.md`](rea-sandbox-evaluation-evidence.md)。
2. **證據提煉 (Evidence Extraction)**：
   - 把看到的行為規則寫成條列規格（輸入怎麼掃描、優先序、輸出字串格式、結束碼），每條對回階段一的一個觀測。

### 階段三：無菌室乾淨重造 (Cleanroom Re-implementation)
1. **防版權污染**：只參考階段二寫出的「規格定義（Functional Spec）」與「I/O 契約」，不複製解包或反編譯出來的程式碼。
2. **Agent-Native 生成**：以標準技術（Python stdlib、TypeScript）重新實作，輸出結構化結果。
3. **逐案比對**：同一組輸入分別餵給原版與重寫版，stdout、結束碼要一致；再故意改壞重寫版一處，確認比對真的會變紅。

---

## 3. 端到端實測：Electron 預設應用的命令列分派（2026-11-22）

### 3.0 對象、授權與環境

| 項目 | 內容 |
| :--- | :--- |
| 對象 | Electron 的**預設應用**（default app）：沒有指定應用時 Electron 自己載入的那個小應用，放在發行檔的 `resources/default_app.asar`（110,835 bytes，13 個檔案） |
| 來源與版本 | npm 官方 registry 的 `electron@45.4.1`；封存檔 SHA-256 `eac55d6cfcf4eab7e31a45356567f549ef7eb669e3699226b48a8492ad34f510` |
| 授權 | MIT（發行檔內附 `LICENSE`，原始碼在 <https://github.com/electron/electron> 的 `default_app/`）。MIT 允許使用、修改與再散布，逆向與改作不需要另外取得同意，也沒有授權保護要繞過 |
| 選擇理由 | 是上游自己打包的真實 ASAR（不是為了示範自己包的）；體積小；同時有命令列行為與視窗；行為完全在本機，不連外部服務 |
| 只分析的範圍 | 只看 `default_app.asar`。同一個發行檔裡的 Chromium 等元件另有授權，不在範圍內 |
| 環境 | Windows 11、Node.js 26.12.1、npm 11.20.0、Python 3.14.10；全部裝在隔離目錄 `C:\GitHub\_sandbox\re-walkthrough\`，做完整個目錄送資源回收筒 |
| 工具版本 | `@electron/asar@4.3.2`、`rea-agents@6.8.0`、`playwright-core@1.65.1`，都用 `npm install --ignore-scripts --save-exact` 從官方 registry 安裝；只有 `electron` 另外執行它自己的 `install.js` 下載執行檔 |

```bash
npm install --ignore-scripts --save-exact electron@45.4.1
node node_modules/electron/install.js        # exit 0，取得 dist/electron.exe 與 resources/default_app.asar
```

### 3.1 階段一：操控與行為觀測

**命令列**（以下 `electron` 指沙盒裡的 `node_modules/electron/dist/electron.exe`）：

```text
$ electron --version      → v45.4.1          exit=0
$ electron -v             → v45.4.1          exit=0
$ electron --abi          → 150              exit=0
$ electron -a             → 150              exit=0
$ electron --help         → 印出下列文字後不結束，30 秒逾時才被砍掉（exit=124）
Electron 45.4.1 - Build cross platform desktop apps with JavaScript, HTML, and CSS
Usage: electron [options] [path]
  ...
Options:
  -i, --interactive     Open a REPL to the main process.
  -r, --require         Module to preload (option can be repeated).
  -v, --version         Print the version.
  -a, --abi             Print the Node ABI version.
```

留給階段二的疑問：說明文字沒有列 `--help`，為什麼它會印說明卻不結束？

**視窗**：用 `playwright-core` 的 `_electron.launch({ executablePath })` 不帶參數啟動，等 `.electron-version a` 出現後讀 DOM 文字，再 `app.close()`。不截圖。

```json
{
 "title": "Electron",
 ".electron-version": "Electron v45.4.1",
 ".chrome-version": "Chromium v156.0.8078.100",
 ".node-version": "Node v24.22.3",
 ".v8-version": "v8 v15.6.75.57-electron.c2a1644ee688c616",
 ".command-example": "target\\node_modules\\electron\\dist\\electron.exe path-to-app",
 "links": 9
}
```

踩到的坑：Electron 預設把使用者資料寫到 `%APPDATA%\Electron`，在沙盒之外（這台機器上該目錄 2026-10-24 就已存在，本次只是多寫了快取）。之後啟動請加 `--user-data-dir=<沙盒內目錄>`；實測加了之後資料改寫進沙盒，預設應用不認得這個旗標所以不受影響。

### 3.2 階段二：結構逆向

```text
$ npx --no-install asar list default_app.asar          # 13 個檔案，以下併行排列
\default_app.js  \icon.png  \index.html  \main.js  \package.json  \preload.js  \styles.css
\octicon\{book-24,code-square-24,gift-24,mark-github-16,star-fill-24}.svg  \octicon\build.css
$ npx --no-install asar extract default_app.asar ../unpacked     # exit 0
$ cat ../unpacked/package.json
{ "name": "electron", "productName": "Electron", "main": "main.js", "type": "module" }
```

`main.js`（9,851 bytes）是 TypeScript 編譯後的 ES module，沒有壓縮或混淆，直接讀得懂；所以這個案例沒有驗到「還原壓縮程式碼」的能力。

```text
$ npx --no-install rea-agents analyze-javascript-application <沙盒>\...\default_app.asar --json
exit 0；stdout 是一份 2.27 MB 的 Evidence JSON，進度訊息走 stderr（33 則）
  subject.digest.sha256      eac55d6c…f510（與上表一致）
  format                     asar
  statistics                 relevant_files 5、parsed_javascript_files 3、visited_ast_nodes 1966、
                             findings 51、parse_failures 0
  graph                      62 個節點、74 條邊；含 electron-main 1、browser-window 1、
                             context-bridge-api 1、ipc-channel 1
  summary                    browser_windows 1、preload_entrypoints 1、explicit_web_preferences 4、
                             ipc: literal_channels 1、main_handlers 1、renderer_transmissions 1、
                             paired_renderer_transmissions 1
  integrity_contradictions   []
```

REA 的結果和解包後的程式對得上：`default_app.js` 建一個 `BrowserWindow`，`webPreferences` 明寫 4 項（preload、`contextIsolation: true`、`sandbox: true`、`nodeIntegration: false`）；`ipcMain.handle('bootstrap', …)` 配 `preload.js` 的 `ipcRenderer.invoke('bootstrap')`；`contextBridge` 公開一個 `electronDefaultApp`，裡面只有 `initialize`。階段一讀到的四個版本字串就是 `initialize` 填進 DOM 的。REA 給的是結構圖；下面的命令列規則是人讀 `main.js` 整理的，REA 的輸出沒有直接列出這些。

**提煉出的規格**（I/O 契約；輸入是執行檔之後的參數，依序掃描）：

| # | 規則 |
| :--- | :--- |
| S1 | `--version`／`-v`：記下「要印版本」並**停止掃描** |
| S2 | `--app=<值>`：以等號切開取第 2 段當目標並停止掃描（`--app=a=b` 的目標是 `a`） |
| S3 | `--interactive`／`-i`／`-repl`：記下互動模式，繼續掃 |
| S4 | `--require`／`-r`：下一個參數是要預先載入的模組，可重複；掃完還缺模組就往 stderr 印 `Invalid Usage: --require [file]`、結束碼 1 |
| S5 | `--abi`／`-a`、`--no-help`、`--test-type=webdriver`：各記一個旗標，繼續掃 |
| S6 | 其他以 `-` 開頭的參數**一律略過** |
| S7 | 第一個不以 `-` 開頭的參數是目標，停止掃描 |
| S8 | 分派優先序：有目標（且非 webdriver）→ 依網址／`.html`／其他分三種載入；否則版本 → ABI → 互動 → 預設視窗 |
| S9 | 版本印 `v<Electron 版本>`、ABI 印 `process.versions.modules`，結束碼都是 0；預先載入的模組在分派前就載入 |
| S10 | 互動模式在 Windows 往 stderr 印 `Electron REPL not currently supported on Windows`、結束碼 1 |
| S11 | 預設視窗：除非有 `--no-help` 或環境變數 `ELECTRON_NO_HELP`，先印歡迎文字；行程不自行結束 |

S6＋S11 回答了階段一的疑問：`--help` 不是它認得的旗標，被當成「不認得的旗標」略過，結果走到預設視窗那一支，所以印了歡迎文字又開著視窗不結束。

### 3.3 階段三：重造與一致性驗證

依 S1～S11 用 Python 標準函式庫寫一個 `decide(argv)`，回傳分派結果、應有的 stdout／stderr 與結束碼。歡迎文字沒有重現（那是字串不是邏輯）；載入網址、`.html`、找不到應用時的錯誤對話框沒有比對（見 3.4）。

```python
import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

@dataclass
class Decision:
    action: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None        # None：行程不會自己結束
    modules: list[str] = field(default_factory=list)
    target: str | None = None
    prints_welcome: bool = False

def decide(argv, *, electron_version, node_abi, platform="win32", env_no_help=False):
    file = None
    version = abi = interactive = webdriver = False
    no_help, modules, want_module = env_no_help, [], False
    for arg in argv:
        if want_module:
            modules.append(arg); want_module = False
        elif arg in ("--version", "-v"):
            version = True; break
        elif arg.startswith("--app="):
            file = arg.split("=")[1]; break
        elif arg in ("--interactive", "-i", "-repl"):
            interactive = True
        elif arg == "--test-type=webdriver":
            webdriver = True
        elif arg in ("--require", "-r"):
            want_module = True
        elif arg in ("--abi", "-a"):
            abi = True
        elif arg == "--no-help":
            no_help = True
        elif arg[:1] == "-":
            pass
        else:
            file = arg; break
    if want_module:
        return Decision("usage-error", exit_code=1,
                        stderr='Invalid Usage: --require [file]\n\n"file" is required\n')
    d = Decision("default-window", modules=modules)
    if file and not webdriver:
        d.target = file
        scheme = urlsplit(file).scheme.lower() if "://" in file or file.startswith("file:") else ""
        if scheme in {"http", "https", "file", "chrome"}:
            d.action = "load-url"
        elif os.path.splitext(file)[1] in (".html", ".htm"):
            d.action = "load-html"
        else:
            d.action = "load-package"
    elif version:
        d.action, d.stdout, d.exit_code = "version", f"v{electron_version}\n", 0
    elif abi:
        d.action, d.stdout, d.exit_code = "abi", f"{node_abi}\n", 0
    elif interactive:
        if platform == "win32":
            d.action, d.exit_code = "repl-unsupported", 1
            d.stderr = "Electron REPL not currently supported on Windows\n"
        else:
            d.action = "repl"
    else:
        d.prints_welcome = not no_help
    return d
```

**比對方式**：30 組參數各自真的執行一次 `electron.exe`，把 stdout、stderr、結束碼和 `decide()` 的預測比。要驗「載入哪個應用、預先載入哪些模組」時，用自己寫的探針：三個只會印 `APP:<名稱>` 然後結束的小應用（有 `package.json` 的目錄、只有 `index.js` 的目錄、單一 `.js` 檔），兩個只會印 `PRELOAD:<名稱>` 的模組；預測的目標與模組清單換算成應該出現的標記行。預設視窗那一支的判準是「7 秒內沒有自行結束」加上「歡迎文字有沒有出現」，然後連同子行程一起砍掉。比較時去掉空白行與行尾空白（Windows 上輸出前面會多一個空行）。

```text
$ python -I rebuild/compare.py 150          # 150 是階段一觀測到的 ABI
PASS  --version                                    -> version           exit=0
PASS  -v                                           -> version           exit=0
PASS  --abi                                        -> abi               exit=0
PASS  -a                                           -> abi               exit=0
PASS  -a -v                                        -> version           exit=0
PASS  -v -a                                        -> version           exit=0
PASS  --abi --version                              -> version           exit=0
PASS  -r                                           -> usage-error       exit=1
PASS  --require                                    -> usage-error       exit=1
PASS  -a -r                                        -> usage-error       exit=1
PASS  -i                                           -> repl-unsupported  exit=1
PASS  --interactive                                -> repl-unsupported  exit=1
PASS  -repl                                        -> repl-unsupported  exit=1
PASS  -i -a                                        -> abi               exit=0
PASS  -r ./pre1.cjs -v                             -> version           exit=0
PASS  -r ./pre1.cjs --require ./pre2.cjs -a        -> abi               exit=0
PASS  appdir                                       -> load-package      exit=0
PASS  appidx                                       -> load-package      exit=0
PASS  single.js                                    -> load-package      exit=0
PASS  --app=appdir                                 -> load-package      exit=0
PASS  --app=appdir=zzz                             -> load-package      exit=0
PASS  --unknown-flag appdir                        -> load-package      exit=0
PASS  -r ./pre1.cjs appdir                         -> load-package      exit=0
PASS  appdir -v                                    -> load-package      exit=0
PASS  -a appdir                                    -> load-package      exit=0
PASS  -v appdir                                    -> version           exit=0
PASS  --no-help -i appidx                          -> load-package      exit=0
PASS  --help                                       -> default-window    exit=None
PASS  --no-help                                    -> default-window    exit=None
PASS  (無參數)  [ELECTRON_NO_HELP=1]               -> default-window    exit=None

30/30 一致
exit=0
```

**反向對照**（確認比對不是永遠綠）：把重寫版 S1 的「停止掃描」拿掉再跑其中 4 組，`-v appdir` 變紅，結束碼 1。

```text
FAIL  -v appdir                                    -> load-package      exit=0
     預期 stdout: ['APP:appdir'] exit: 0 stderr: []
     實際 stdout: ['v45.4.1'] stderr: []
3/4 一致
exit=1
```

### 3.4 這次走通沒有涵蓋的事

- **不是嚴格的無菌室**：讀程式整理規格的和寫重寫版的是同一個 agent、同一段對話，沒有做到「分析者與實作者分開」。對象是 MIT 授權，這裡不構成侵權風險；要拿這套流程處理授權較嚴的對象，兩個角色必須分開，實作者只能拿到 3.2 那張規格表。
- **對象沒有壓縮、混淆，也沒有網路行為**：還原壓縮 bundle、攔截網路請求這兩件事沒有驗到。
- **只在 Windows 跑**：S10 在其他平台會進入 REPL，那一支沒有比對。
- **沒有比對的分支**：載入網址與 `.html`（會開視窗）、目標不存在時的錯誤對話框（會跳出要人按的視窗）、`--test-type=webdriver`、`package.json` 的 `version`／`productName`／`v8Flags` 處理。重寫版對前兩者只回傳分類，沒有實跑驗證。
- **CLI-Anything 沒有用到**；REA 只用了 JavaScript 應用分析一個入口，是命令列不是 MCP。MCP 工具清單的實際名稱仍未查證。
- **沒有和上游原始碼逐行對照**：規格來自解包後的 `main.js`，沒有另外去比對 GitHub 上的 `default_app/main.ts`。
- 沙盒已刪除，上面的重寫版程式碼是唯一留存；比對腳本沒有收進本 repo 的 `tools/`。

---

## 4. 法律與道德合規宣告

- 本流水線規格僅限用於**自有軟體安全性審計**、**開源專案技術學習**、**協定互通性研究（Interoperability）**及**合法除錯**。
- 嚴禁利用此流水線規避數位版權保護機制（DRM）或破解未經授權之商業機密軟體。

---

## 5. 合規防線與拒答處理規範

> 來源：`notes/2026-10-19-rea-reverse-engineer-anything-agent.md` 第 2.3 節的實務心得（作者宣稱）。任務原稱此節為「審查避障」；本文件的立場是：**用準確、可查證的用途宣告取得雲端模型的協助；被拒答就停手，不換說法試探、不靠改寫繞過安全對齊。** 理由見 5.2。

### 5.1 動手前的閘門（全部成立才進入雲端分析）

| # | 檢查項 | 不成立時 |
| :--- | :--- | :--- |
| G1 | 目標是**自有軟體**、有**書面授權**的客戶軟體，或為**協定互通性**（見 5.4）所需 | 停止，不上傳任何位元組 |
| G2 | 目的是靜態分析、Call Graph、重建功能規格與資料格式；**不是**取得序號、略過授權／試用／DRM 檢查 | 停止 |
| G3 | 已記錄 `authorization_ref`（合約編號、自有 repo、授權信 ID） | 補齊再開始 |
| G4 | 上傳雲端的內容已評估：不含客戶機密、個資、憑證（遵守 `AGENTS.md` 第 4 節） | 只上傳必要的函式片段，不傳整檔 |
| G5 | 產出只留規格與 I/O 契約，不入庫反編譯程式碼與修補後的二進位 | 依第 2 節階段三 |

### 5.2 為什麼不教「避障」

- 筆記提到的有效做法，本質是**把真實用途與限制講清楚**（靜態分析、重建功能與資料格式、不用原版程式碼、不商用、不做違法用途）。這是準確宣告，不是話術；宣告內容必須與事實一致，G1～G5 就是讓它成立的條件。
- 宣告不實、或宣告為真但被拒答後反覆改寫試探，等於把安全對齊當作要繞過的對象。本流水線的處理是：**拒答一次就記錄，改走非模型路徑**（人工使用 Ghidra／JADX 閱讀、補充授權證明後由人決定是否重試），不做第二種措辭。
- 以「本地未審查模型」執行修補，**不改變行為的合法性**：責任閘門在 5.5 的契約驗證器與 G1～G5，不在模型有沒有拒答機制。

### 5.3 Clean Room 合規宣告 Prompt 範本

用於對雲端模型發起靜態分析。`{{ }}` 為必填欄位，缺任何一項不得送出。

```text
【用途與授權宣告】
我正在對 {{目標名稱與版本}} 進行 {{自有軟體安全審計 | 已授權的客戶軟體除錯 | 協定互通性研究}}。
授權依據：{{authorization_ref，例如合約編號或自有 repo}}。
本次僅做「靜態分析」，採 Clean Room 原則：
 - 目的是理解功能並重建「功能規格」與「資料格式」，之後由另一個不接觸原始程式碼的實作者獨立重寫；
 - 不會複製或散布原版程式碼或二進位，不做商業轉售，不用於略過授權、試用限制、DRM 或任何違法用途。

【請你做】
1. 就我貼上的組合語言片段 {{函式名稱或位址範圍}}，說明該函式的輸入、輸出與副作用。
2. 列出 Call Graph（呼叫者／被呼叫者、呼叫位址），註明哪些是推測。
3. 重建所處理的資料結構欄位（偏移、型別、長度），註明信心程度。
4. 每一項結論附上對應的位址或指令作為證據；無法確定的寫「未能確定」。

【請你不要做】
- 不要輸出可直接用於略過授權檢查或啟用驗證的修補建議；若你判斷這份分析的用途不符合上述宣告，請直接說明並停止。

【輸出格式】
JSON，符合第 5.5 節的 re_handoff.v1（findings 欄位）；無法填的欄位留空字串。
```

使用規則：
1. 宣告必須是真的；欄位由人填寫，不由 Agent 自動補齊「授權依據」。
2. 模型回答拒絕或要求更多說明時，補**事實**（授權文件、目的），不補話術；補完仍拒絕就停止。
3. 範本中「請你不要做」那段不可刪除；它讓模型與日後審查者看到限制是雙向的。

### 5.4 法律背景（一般性說明，非法律意見）

以下僅為方便查找的出處清單，各法域的要件與例外不同，實際案件請洽律師。

| 法域 | 內容（摘要） | 出處 |
| :--- | :--- | :--- |
| 歐盟 | 軟體指令 2009/24/EC 第 6 條：在取得互通性資訊所必需時，取得合法使用權的人可進行還原（decompilation）；官方文字列有三項累積條件（合法使用者、資訊先前不易取得、僅限互通所需部分），另對取得資訊的用途設有限制。第 6(2) 款細節本次未取得官方全文，**未查證** | [legislation.gov.uk 第 6 條](https://www.legislation.gov.uk/eudr/2009/24/article/6)（2026-10-26 查證第 6(1) 款）；官方全文請另查 EUR-Lex |
| 美國 | 17 U.S.C. §1201(a)(1)(A) 禁止規避控制存取的技術措施；§1201(f) 為互通性逆向的有限例外，要求合法持有程式副本、僅為取得獨立程式互通所需且先前不易取得的元素 | [Cornell LII 17 USC 1201](https://www.law.cornell.edu/uscode/text/17/1201)（2026-10-26 查證） |
| 台灣 | 著作權法第 80 條之 2 規範「防盜拷措施」的規避與相關設備提供；第 3 項有例外、第 4 項授權主管機關訂定例外認定要點。現行條文與要點**本次未能從全國法規資料庫取得，未查證** | 次級來源：[智慧局文件](https://www.tipo.gov.tw/wSite/public/Attachment/0/f1747972069582.pdf)；請自行核對 [全國法規資料庫](https://law.moj.gov.tw/) |

要點：
- Clean Room 是一種**降低侵權風險的作法**（分析團隊產規格、實作團隊不接觸原碼），**不是法定的安全港**；契約條款（EULA 禁止逆向）也可能另有拘束力，本表未涵蓋。
- 規避 DRM／授權機制，即使目的是互通，各法域例外都很窄；本流水線一律列為 G2 不通過。

### 5.5 雲地雙軌管線與資料介接契約

```text
 [人]  填寫 authorization_ref、purpose，檢查 G1~G5
   │
   ▼
┌───────────────────────────────┐   片段（最小必要）   ┌──────────────────────────────┐
│ 地端：REA / Ghidra / JADX     │ ───────────────────▶ │ 雲端 LLM（靜態分析）          │
│ 取得 Assembly、位址、位元組   │                      │ 5.3 Prompt                   │
└───────────────────────────────┘ ◀─────────────────── │ 輸出 re_handoff.v1 findings  │
        ▲                          findings JSON       │  ・Assembly 說明、呼叫位址    │
        │                                              │  ・TfmRegKey（見下方說明）    │
        │                                              │  ・Patch 檔案偏移量           │
        │                                              └───────────────┬──────────────┘
        │                                                              │ re_handoff.v1
        │                                                              ▼
        │                                              ┌──────────────────────────────┐
        │                                              │ 契約驗證器 check_handoff.py   │
        │                                              │ （閘門：不過就不進地端）      │
        │                                              └───────────────┬──────────────┘
        │                                                              │ 通過
        │            result JSON（套用結果、位元組）                    ▼
        └────────────────────────────────────────────  ┌──────────────────────────────┐
                                                       │ 地端執行：本地模型／二進位工具 │
                                                       │ 在「副本」上做位元修補與動態除錯│
                                                       └──────────────────────────────┘
```

**雲端 → 地端 `re_handoff.v1`**

| 欄位 | 型別 | 說明 |
| :--- | :--- | :--- |
| `schema` | string | 固定 `re_handoff.v1` |
| `purpose` | enum | `interoperability`／`own-software-bugfix`／`security-audit-authorized` |
| `authorization_ref` | string | 必填；人填，Agent 不得自行產生 |
| `target.sha256` | string(64) | 目標檔雜湊，地端套用前先比對 |
| `findings[]` | array | `function`、`va`（位址）、`asm_note`、`confidence`、`evidence` |
| `registry_keys[]` | array | 分析中看到的登錄機碼名稱（筆記所稱 `TfmRegKey` 即屬此類；該名稱的含義**未查證**，本文件只當成字串欄位） |
| `patches[]` | array | `id`、`file_offset`(int)、`original_bytes`、`new_bytes`、`reason` |

**地端 → 雲端 result**：`patch_id`、`applied`(bool)、`post_bytes`、`test_log_ref`（日誌路徑，不貼機密）。

**地端執行規則**
1. 只改**副本**；套用前比對 `target.sha256` 與 `file_offset` 處的 `original_bytes`，不一致就中止。
2. `original_bytes` 與 `new_bytes` 長度必須相同；修補前備份。
3. `reason` 涉及授權、序號、啟用、試用、DRM 的 patch 由驗證器拒絕（驗證器為關鍵字**黑名單輔助**，不能取代 G2 的人工判斷）。
4. 修補後的二進位與反編譯輸出不入庫（沿用 `docs/rea-sandbox-evaluation-evidence.md` 的隔離政策）。

**驗證器範例與實測輸出**（2026-10-26，Python 3.14，純 stdlib，內容為本節規則的最小實作；`check_handoff.py` 並未收錄於本 repo `tools/`，需要時可自行存檔）：

```python
import json, sys
ALLOWED = {"interoperability", "own-software-bugfix", "security-audit-authorized"}
BANNED = ("license", "licence", "serial", "activation", "trial", "drm", "授權", "序號", "啟用", "試用")
def check(h):
    e = []
    if h.get("schema") != "re_handoff.v1": e.append("schema must be re_handoff.v1")
    if h.get("purpose") not in ALLOWED: e.append("purpose not in allowlist")
    if not h.get("authorization_ref"): e.append("authorization_ref required")
    if len(str(h.get("target", {}).get("sha256", ""))) != 64: e.append("target.sha256 must be 64 hex chars")
    for p in h.get("patches", []):
        if len(p.get("original_bytes", "")) != len(p.get("new_bytes", "x")): e.append(f"{p.get('id')}: byte length mismatch")
        if any(b in p.get("reason", "").lower() for b in BANNED): e.append(f"{p.get('id')}: reason touches licensing/DRM -> reject")
        if not isinstance(p.get("file_offset"), int): e.append(f"{p.get('id')}: file_offset must be int")
    return e
if __name__ == "__main__":
    errs = check(json.load(open(sys.argv[1], encoding="utf-8")))
    print("\n".join(errs) or "OK"); sys.exit(1 if errs else 0)
```

```text
$ python check_handoff.py good.json        # 自有 build 修正反向分支
OK
exit=0
$ python check_handoff.py bad.json         # 無授權、雜湊錯、長度不符、reason 為略過授權檢查
authorization_ref required
target.sha256 must be 64 hex chars
P1: byte length mismatch
P1: reason touches licensing/DRM -> reject
exit=1
```

### 5.6 未查證與限制

- 「合規宣告能提高雲端模型配合度」是筆記作者的實務經驗，**未獨立重現**；本文件未對任何模型做拒答率測試。
- 筆記所述模型（GPT-4o／Claude 3.7）為作者提及的版本，本文件不依賴特定模型。
- 歐盟第 6(2) 款與台灣第 80 條之 2 現行條文見 5.4 說明，未取得官方全文。
