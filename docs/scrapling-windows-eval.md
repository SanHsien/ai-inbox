# Scrapling 在 Windows 11 的沙盒實測（T-20261117-01）

> 實測日 2026-11-19。對象：[`D4Vinci/Scrapling`](https://github.com/D4Vinci/Scrapling) commit `2998c9ebba52ef6116f0a483c7d2f21908250024`（2026-11-17）與 PyPI `scrapling==0.5.1`。
> 環境：Windows 11 Pro、Python 3.14.10、pip 26.2.2。沙盒在 `C:\GitHub\_sandbox\scrapling-eval`（獨立 venv，沒有裝進系統 Python）。
> 來源筆記：[`notes/2026-11-17-scrapling-python-mcp-crawler-eval.md`](../notes/2026-11-17-scrapling-python-mcp-crawler-eval.md)。

## 1. 結論

| 問題 | 結論 |
| --- | --- |
| 套件本身有沒有可疑行為 | 靜態檢視沒有發現安裝腳本、匯入時副作用、遙測或背景連線。安裝的 wheel 與檢視過的原始碼逐檔相同 |
| Windows 11 能不能用 | 能。基本 HTTP 抓取、轉 Markdown、`scrapling mcp` 啟動都正常，Python 3.14 也能跑（官方只標到 3.13） |
| 轉 Markdown 的品質 | 有指定內容區塊的 CSS 選擇器時可用；不指定時導覽列全部留著。程式碼區塊沒有語言標記，相對連結不會轉成絕對網址 |
| Adaptive Parser | **目標元素不存在時會靜默回傳別的元素**，預設門檻下連無關的錯誤頁都會配到東西。不能用在要求資料正確的流程 |
| 隱藏內容清洗 | 只擋掉一部分。`hidden` 屬性、移到畫面外、白底白字、圖片替代文字裡的注入文字都留在輸出 |
| 要不要把 `scrapling mcp` 接給本機 agent | **不建議**。17 個工具的定義約 5 萬字元；預設就偽裝成瀏覽器；內建給 agent 的指示包含破解滑塊驗證的操作方式 |

範圍限制先講清楚：這次**沒有**執行 `scrapling install`、沒有啟動任何瀏覽器、沒有用隱身或繞過反爬的功能、沒有對需要登入或有反爬的網站測試。貼文主打的「過盾」完全不在實測範圍，本文對它不下任何結論。

與任務原始寫法的差異：任務的驗收標準寫「實測 `scrapling mcp` 轉 Markdown」。這次 `scrapling mcp` 只做到啟動、握手、列出工具，**沒有透過 MCP 呼叫抓取工具**；Markdown 轉換是用函式庫直接呼叫 `Response.markdown()` 測的。原始碼註明這個方法與 MCP 伺服器用的是同一套清洗流程（`scrapling/engines/toolbelt/custom.py` 第 92～96 行），但「經由 MCP 工具呼叫取得 Markdown」這一步本身沒有跑。原因見第 5.3 節：MCP 的抓取工具預設會偽裝瀏覽器指紋，要測就得每次明確關掉。

## 2. 流程

```text
(1) 淺層 clone（停用 hooks）──▶ 靜態檢視 ──▶ 安全檢查工具
                                    │              │
                                    │         結束碼 1（14 項）
                                    │              │
                                    └──── 人工逐項複核：都是同一句參數說明，誤判
                                                   │
(2) 獨立 venv ◀────────────────────────────────────┘
      │  pip 只裝預建 wheel、固定版本、留雜湊
      ▼
    比對 wheel 與原始碼（逐檔相同）
      │
      ├─▶ 基本 Fetcher：3 個公開靜態頁，各 1 次請求，先查 robots.txt，關閉偽裝
      ├─▶ 本機離線：隱藏內容清洗、Adaptive Parser 誤配
      └─▶ scrapling mcp：啟動 → initialize → tools/list → 關閉
      │
(3) 查殘留行程（0 個）
```

## 3. 靜態安全檢視

### 3.1 取得原始碼

```text
$ git clone --depth 1 -c core.hooksPath=NUL https://github.com/D4Vinci/Scrapling.git src
$ git -C src rev-parse HEAD
2998c9ebba52ef6116f0a483c7d2f21908250024
```

### 3.2 人工檢視結果

| 檢查項目 | 結果 | 位置 |
| --- | --- | --- |
| 安裝時執行的程式 | 沒有 `setup.py`；`setup.cfg` 只有中繼資料；建置後端是 setuptools，沒有自訂建置步驟 | `pyproject.toml`、`setup.cfg` |
| 匯入時的副作用 | 套件進入點只有延遲匯入對照表，不連網、不寫檔 | `scrapling/__init__.py` |
| 啟動子行程 | 全套件只有一處：`scrapling install` 指令呼叫 `python -m playwright install chromium`（不經 shell）。只有使用者自己下這個指令才會執行，這次沒有執行 | `scrapling/cli.py` 第 25～28、110～143 行 |
| 動態執行（`eval`／`exec`） | 套件程式碼裡沒有；只有測試檔有一處 | `tests/fetchers/test_public_api.py` 第 17 行 |
| 遙測、回報、分析 | 沒有。搜尋到的大量 analytics／telemetry 字樣全部在廣告與追蹤網域的**封鎖清單**裡 | `scrapling/engines/toolbelt/ad_domains.py` |
| 寫死的對外網址 | 會實際用到的只有三類：預設把 `https://www.google.com/` 填進 Referer 標頭（不是連到 Google）；瀏覽器模式選用的 DNS over HTTPS 參數；MCP 伺服器圖示的圖片網址。其餘都在註解與說明文字 | `scrapling/engines/static.py` 第 196 行；`scrapling/engines/_browsers/_base.py` 第 544 行；`scrapling/core/ai/server.py` 第 1056 行 |
| 反序列化 | 爬蟲的斷點續跑用 `pickle` 讀寫本機檢查點檔。檢查點目錄若被別人放進檔案會有風險；這次沒有用到爬蟲功能 | `scrapling/spiders/checkpoint.py` 第 49、74 行 |
| 附帶的技能壓縮檔 | `agent-skill/Scrapling-Skill.zip` 內容只有 Markdown 說明與 4 個範例 `.py`，與同目錄已解開的版本同名對應；沒有執行檔 | 以 Python `zipfile` 列出檔名 |
| MCP 的 HTTP 傳輸 | 預設綁 `127.0.0.1`；沒有給權杖就拒絕啟動，除非明確加 `--no-auth`。預設傳輸是 stdio | `scrapling/cli.py` 第 152～188 行；`scrapling/core/ai/server.py` 第 1207～1228 行 |
| 轉址 | HTTP 抓取器預設拒絕轉到內部或私有 IP 的轉址 | `scrapling/engines/static.py` 第 83、310 行 |

需要知道的預設行為（不是惡意，是這個工具的定位）：

- 基本的 `Fetcher` **預設就會偽裝**：TLS 指紋模仿 Chrome（`impersonate="chrome"`）、產生仿真瀏覽器標頭並加上 Google 的 Referer（`stealthy_headers=True`）。位置：`scrapling/engines/static.py` 第 74～75、179～198 行。這次實測把兩者都關掉，並送出誠實的 User-Agent。
- MCP 的 `make_request` 工具同樣預設 `impersonate="chrome"`（`scrapling/core/ai/server.py` 第 722～727 行）。

### 3.3 安全檢查工具

```text
$ python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack C:\GitHub\_sandbox\scrapling-eval\src
[FAIL] ...\scrapling-eval\src：已掃描 685 個檔案，FAIL 14 項、需人工審查 4 項、未掃描 28 個
  FAIL      [CRED-ACCESS] scrapling/engines/_browsers/_stealth.py（第 72 行）— 瀏覽器設定檔內的 Cookie／登入資料庫：user data directory, which stores browser session data like cookies
  FAIL      [CRED-ACCESS] scrapling/fetchers/stealth_chrome.py（第 48 行）— （同一句）
  ...（其餘 12 項是同一句話出現在另外 2 處程式註解與 10 個語言的文件範本）
  REVIEW    [DYNAMIC-EXEC] .git/hooks/pre-receive.sample（第 14 行）
  REVIEW    [DYNAMIC-EXEC] tests/fetchers/test_public_api.py（第 17 行）
  REVIEW    [CRED-ACCESS] docs/fetching/stealthy.md（第 126 行）、agent-skill/.../stealthy.md（第 113 行）
  UNSCANNED agent-skill/Scrapling-Skill.zip 與 27 張圖片
結束碼 1
```

逐項複核：

- **14 項 FAIL 是同一句參數說明**。完整原文是 `user_data_dir` 參數的說明：指定瀏覽器使用者資料目錄的路徑，預設是建立暫存目錄。驗證器的預設值是空字串（`scrapling/engines/_browsers/_validators.py` 第 81 行），也就是不指定就用暫存目錄，**不會去讀使用者平常用的瀏覽器設定檔**。這是選用參數的說明文字，判定為誤判。
- 但這個參數確實讓呼叫端可以把路徑指向真實的瀏覽器設定檔。透過 MCP 的 `browser_open` 工具，agent 也能填這個值。這是把它接給 agent 時要擋的地方，不是套件自己會做的事。
- 4 項 REVIEW：git 內建的範例 hook（clone 時已停用 hooks）、測試檔的 `exec`、兩份文件裡的同一句話。都不在安裝後會執行的路徑上。
- 未掃描的壓縮檔已人工列出內容（第 3.2 節）。圖片是贊助商標誌與文件插圖，沒有檢查。

判斷：檢查工具的結束碼是 1，照規則不算通過。人工複核後沒有找到實際的疑慮，所以繼續做第 4 節的沙盒安裝；**這是本文作者的判斷，不是工具放行**。如果要正式採納到 agent 環境（不只是沙盒評估），這 14 項要先在檢查工具那邊留下複核紀錄。

### 3.4 留言裡三項未附出處的說法

| 說法 | 核對結果 | 依據 |
| --- | --- | --- |
| Python 3.10 以上即可 | 正確 | `pyproject.toml` 的 `requires-python = ">=3.10"`；`README.md` 第 529 行 |
| MCP Server 是 v0.5 之後加的 | **不正確**。v0.3（2025-09-01）就有內建 MCP 伺服器；v0.4.15（2026-08-23）大改過一次並有不相容變更 | `docs/changelog.md` 第 963、988～989 行；第 142～148 行 |
| `StealthyFetcher` 是改過的 Firefox | **現行版本不正確**。現在是 Chromium，透過 `patchright`（改過的 Playwright）。v0.3.13（2026-01-01）的變更紀錄寫明停用 Camoufox（以 Firefox 為基礎），所以這個說法對舊版成立 | `scrapling/engines/_browsers/_stealth.py` 第 7～10、101 行；`scrapling/fetchers/stealth_chrome.py` 第 8 行；`docs/changelog.md` 第 720～728 行 |

## 4. 沙盒安裝

```text
$ python -m venv .venv
$ .venv\Scripts\python.exe -m pip install --disable-pip-version-check --only-binary :all: --report pip-report.json "scrapling[ai]==0.5.1"
Successfully installed ... scrapling-0.5.1 ...（共 49 個套件）
```

- `--only-binary :all:`：只接受預建的 wheel，安裝過程不會執行任何套件的建置腳本。
- 沒有執行 `scrapling install`。本機 Playwright 的瀏覽器快取目錄是其他工具早先建立的，最新一筆修改時間是 2026-10-31，這次沒有新增內容。
- 安裝的 wheel 與檢視過的原始碼一致：

```text
$ diff -rq --strip-trailing-cr -x __pycache__ src/scrapling .venv/Lib/site-packages/scrapling
（沒有輸出，結束碼 0）
```

主要套件的版本與 sha256（pip 安裝報告的 `archive_info.hashes`）：

```text
scrapling==0.5.1      c9eb0ef22a05e00e19827a179544fea2bc91b663585f637d428453d3b00ceb17
curl_cffi==0.17.0     4c3993c7df155d622869b82a56adb018440587fd3faffeaf8d01cc016d2e1357
lxml==6.1.3           66299564c046bc7e0cc5de5106601eae907e9fa5904cd68a323380a8502f7861
markdownify==1.2.4    e0375484fdd2bb007e86779fe34c59673d0011b14f8299953aaf0bf092269220
mcp==2.3.0            dd0c44c089d16453e8ae31a3877a0054d7a2314caaa81f5e0541b9b1734b2377
patchright==1.64.4    91ede516076a12196def89ff89ee7eb30deea4ba074ca136f1022d59e98b0352
playwright==1.65.2    d0aec9e1c97b6f497f3d9f2ad6e1b7f299968e61239d71f100298b0690f3c776
browserforge==1.2.4   fb1c14e62ac09de221dcfc73074200269f697596c642cb200ceaab1127a17542
protego==0.7.0        944638aaee608f6c83fcad442695f3f9381a60be8d5007248f46b00f201fa5fc
orjson==3.13.0        6adcaa85d79977659a448b4123a88eb33511a11ed2db243535ad7ea88a6668e0
msgspec==0.22.0       749899563d26b211379f142b8ffd7e2d7da149a51717798f0ce994dce50324f0
w3lib==2.6.0          e62ce6b7f845b5e8588223d44e64990673a0fefd6815d6b3f2e6d39bf9ef308c
```

全部 49 個套件的版本與雜湊在沙盒的 `C:\GitHub\_sandbox\scrapling-eval\pip-report.json`。venv 佔 327 MB，其中 `playwright` 的 wheel 就有 42.7 MB：只想用 HTTP 抓取也得把兩套瀏覽器自動化套件裝進來，因為 `ai` 與 `rag` 這兩組選用相依都包含 `fetchers`。

## 5. 實測

測試腳本在沙盒的 `eval\` 目錄：`fetch_md.py`、`local_tests.py`、`mcp_probe.py`；輸出在 `eval\out\`。

### 5.1 基本 Fetcher 轉 Markdown

設定：`impersonate=None`、`stealthy_headers=False`、自訂誠實的 User-Agent；每個網址先讀 `robots.txt` 並用 `protego` 判斷，允許才抓；每個頁面只發 1 次請求。

```text
$ .venv\Scripts\python.exe eval\fetch_md.py
== example https://example.com/
   robots.txt status=404 allowed=True
   GET status=200 html_chars=573 seconds=0.08 sent_ua=scrapling-eval/0.5.1 (one-off local evaluation; honest client)
   md full                         {'chars': 172, 'lines': 3, 'links': 0, 'raw_html_tags': 0, ...}
== pydocs-json https://docs.python.org/3/library/json.html
   robots.txt status=200 allowed=True
   GET status=200 html_chars=114898 seconds=0.21 sent_ua=scrapling-eval/0.5.1 (...)
   md full                         {'chars': 40079, 'lines': 860, 'links': 220, 'raw_html_tags': 0, 'pilcrow': 36, ...}
   md body                         {'chars': 40016, 'lines': 858, 'links': 220, 'raw_html_tags': 0, 'pilcrow': 36, ...}
   md css[div.body]                {'chars': 36039, 'lines': 742, 'links': 159, 'raw_html_tags': 0, 'pilcrow': 36, ...}
== pep8 https://peps.python.org/pep-0008/
   robots.txt status=404 allowed=True
   GET status=200 html_chars=120530 seconds=0.21 sent_ua=scrapling-eval/0.5.1 (...)
   md full                         {'chars': 54353, 'lines': 1587, 'links': 162, ...}
   md body                         {'chars': 54298, 'lines': 1585, 'links': 162, ...}
   md css[section#pep-content]     {'chars': 51576, 'lines': 1522, 'links': 116, ...}
python 3.14.10
```

`sent_ua` 是回應物件記錄的實際送出標頭，確認偽裝已關閉。

不指定選擇器時的開頭（Python 文件頁，節錄）：

```text
json — JSON encoder and decoder — Python 3.15.2 documentation

[![Python logo](../_static/py.svg)](https://www.python.org/)

Theme
AutoLightDark

### [Table of Contents](../contents.html)

* [`json` — JSON encoder and decoder](#)
  + [Basic Usage](#basic-usage)
  ...
### Navigation

* [index](../genindex.html "General Index")
* [modules](../py-modindex.html "Python Module Index") |
```

指定 `css_selector="div.body"` 後的開頭：

```text
`json` — JSON encoder and decoder[¶](#module-json "Link to this heading")
=========================================================================

**Source code:** [Lib/json/\_\_init\_\_.py](https://github.com/python/cpython/tree/3.15/Lib/json/__init__.py)
```

品質觀察：

| 項目 | 結果 |
| --- | --- |
| 殘留的 HTML 標籤、`script`／`style` 內容 | 三頁都是 0 |
| 把 HTML 縮成 Markdown 的幅度 | Python 文件頁 114,898 → 40,079 字元（約 35%）；PEP 8 頁 120,530 → 54,353（約 45%） |
| `main_content_only=True` 的效果 | 幾乎沒有：三頁只少 16～63 個字元。它只是改成從 `<body>` 開始，不會判斷哪裡是正文；導覽列、目錄、頁尾都還在 |
| 指定正文的 CSS 選擇器 | 有效：Python 文件頁再少約 10%（40,079 → 36,039），導覽全部消失。但選擇器每個網站不同，要自己找 |
| 表格 | 轉成管線表格，內容正確。但放在定義清單裡的表格與段落會帶 4 格縮排，嚴格的 Markdown 解析器會把它當成程式碼區塊 |
| 程式碼區塊 | 圍欄都沒有語言標記（行首的圍欄標記 22 行，帶語言的 0 行） |
| 相對連結 | 不會轉成絕對網址。正文 159 個連結裡有 144 個是相對路徑或頁內錨點，離開原網址後就失效 |
| 標題旁的錨點符號 | 保留在標題文字裡（Python 文件頁 36 個） |
| 速度 | 每頁 0.08～0.21 秒，瓶頸在網路，不在轉換 |

小結：轉換本身交給 `markdownify`，Scrapling 加的是轉換前的清洗與選擇器。對靜態文件頁，品質取決於有沒有給對選擇器。

### 5.2 隱藏內容清洗（本機離線）

原始碼說轉 Markdown 前會移除可用來做提示詞注入的隱藏內容。用一份本機 HTML 字串放 17 種藏法（另加一段 `script` 內文），看哪些留在輸出：

```text
$ .venv\Scripts\python.exe eval\local_tests.py
=== 1. sanitizer: markers that SURVIVE in markdown
  'SCRIPT-TEXT'    removed
  'H1 '            removed     display:none
  'H2 '            removed     visibility:hidden
  'H3 '            removed     aria-hidden="true"
  'H4 '            removed     <template>
  'H5 '            removed     HTML 註解
  '\u200b'         removed     零寬字元
  'H6 '            SURVIVES    hidden 屬性
  'H7 '            SURVIVES    position:absolute; left:-9999px
  'H8 '            removed     font-size:0
  'H9 '            SURVIVES    白底白字
  'H10'            removed     opacity:0
  'H11'            SURVIVES    靠 CSS class 隱藏（例如 sr-only）
  'H12'            SURVIVES    圖片替代文字
  'H13'            SURVIVES    連結的 title 屬性
  'H14'            removed     <noscript>
  'H15'            SURVIVES    收合的 <details>
  'H16'            removed     隱藏的表單欄位
```

（右欄的中文說明是本文加的註解，不是程式輸出。）

17 種藏法擋掉 10 種，7 種留在輸出。留下來的幾種不算程式錯誤：靠外部樣式表隱藏的內容，不載入 CSS 就無從判斷；替代文字與 title 本來就是給讀者的資訊。但結論很明確：**輸出仍然是不可信的外部內容，不能因為「已清洗」就當成安全**。`hidden` 屬性沒擋是可以修的漏洞（`scrapling/core/shell.py` 第 73 行的規則只認 `slot[hidden]`）。

### 5.3 Adaptive Parser 的誤配邊界（本機離線）

做法：第一版頁面有三個商品，用 `#p1` 選第一個並存下特徵（`auto_save=True`）。之後換四種新頁面，用同一個選擇器加 `adaptive=True` 去找，門檻分別試 40%（預設）、70%、90%。

```text
=== 2. adaptive: saved from V1 -> Product 1 (default threshold 40%)
  A redesign, target present     plain=0 adaptive@40% -> <article {'class': 'product new', 'data-id': 'p1'}> h3='Product 1'
  A redesign, target present     plain=0 adaptive@70% -> <article {'class': 'product new', 'data-id': 'p1'}> h3='Product 1'
  A redesign, target present     plain=0 adaptive@90% -> NOTHING (empty result)
  B same layout, target REMOVED  plain=0 adaptive@40% -> <article {'class': 'product', 'id': 'p2'}> h3='Product 2' | <article {'class': 'product', 'id': 'p3'}> h3='Product 3'
  B same layout, target REMOVED  plain=0 adaptive@70% -> <article {'class': 'product', 'id': 'p2'}> h3='Product 2' | <article {'class': 'product', 'id': 'p3'}> h3='Product 3'
  B same layout, target REMOVED  plain=0 adaptive@90% -> NOTHING (empty result)
  C redesign + target REMOVED    plain=0 adaptive@40% -> ... h3='Product 2' | ... h3='Product 3'
  C redesign + target REMOVED    plain=0 adaptive@70% -> ... h3='Product 2' | ... h3='Product 3'
  C redesign + target REMOVED    plain=0 adaptive@90% -> NOTHING (empty result)
  D unrelated error page         plain=0 adaptive@40% -> <article {'class': 'notice', 'id': 'n1'}> h3='Maintenance'
  D unrelated error page         plain=0 adaptive@70% -> NOTHING (empty result)
  D unrelated error page         plain=0 adaptive@90% -> NOTHING (empty result)
```

| 情境 | 預設門檻（40%）的結果 | 判定 |
| --- | --- | --- |
| A 改版，目標還在 | 找回正確的商品 1 | 功能如宣稱 |
| B 版面沒變，目標下架 | 回傳商品 2 與商品 3 | **靜默誤配**：程式拿第一筆就會把商品 2 當成商品 1 |
| C 改版而且目標下架 | 回傳商品 2 與商品 3 | **靜默誤配** |
| D 被導到無關的錯誤頁 | 回傳錯誤頁上的公告區塊 | **靜默誤配** |

- 沒有例外，回傳的物件上沒有相似度分數；呼叫端分不出「找回原本的元素」和「找到長得像的別人」。分數只寫在除錯層級的紀錄裡：把紀錄層級開到 DEBUG 重跑情境 B，看到 `Highest probability was 86.46%`，也就是下架商品的兄弟元素拿到 86 分。
- 門檻調到 70% 可以擋掉情境 D，擋不住 B、C（同版面的兄弟元素相似度太高）；調到 90% 三種誤配都擋掉，但情境 A 也找不回來，等於功能失效。這四個案例裡**沒有一個門檻能同時做對**。
- 留言裡「誤配時約 47% 會靜默抓錯」的數字找不到出處。本文的四個案例是自己設計的小樣本，只能說明誤配**會發生而且沒有訊號**，不能換算成比例。

要用的話，呼叫端必須自己驗證：找回來的元素要再比對一個不會變的識別值（商品編號、標題文字），不符就當成沒找到。

### 5.4 `scrapling mcp` 啟動與工具清單

用自寫的探測腳本以 stdio 啟動，只送 `initialize` 與 `tools/list`，不呼叫任何工具，然後關閉標準輸入讓它結束。

```text
$ .venv\Scripts\scrapling.exe --version
Scrapling, version 0.5.1
$ .venv\Scripts\python.exe eval\mcp_probe.py
pid=37080 initialize ok in 2.24s
serverInfo: {"name": "Scrapling", "version": "0.5.1"} protocol: 2025-06-18
instructions chars: 1219
tools: 17
  browser_open               schema_chars=4456   openWorld
  browser_save_state         schema_chars=703    destructive,openWorld
  browser_load_state         schema_chars=749    destructive,openWorld
  open_request_session       schema_chars=2502   openWorld
  close_session              schema_chars=805    openWorld
  list_sessions              schema_chars=1368   readOnly
  make_request               schema_chars=5926   openWorld,readOnly
  browser_fetch_once         schema_chars=6320   openWorld,readOnly
  browser_fetch              schema_chars=3880   openWorld,readOnly
  session_make_request       schema_chars=4447   openWorld,readOnly
  browser_extract            schema_chars=1694   openWorld,readOnly
  browser_actions            schema_chars=9003   destructive,openWorld
  browser_evaluate           schema_chars=1215   destructive,openWorld
  browser_network_requests   schema_chars=2110   readOnly
  browser_network_request    schema_chars=2007   readOnly
  browser_screenshot         schema_chars=1577   openWorld,readOnly
  browser_observe            schema_chars=961    openWorld,readOnly
tools/list total chars: 49723
server exited after stdin close, exit code 0, pid 37080
```

- Windows 11 上 2.24 秒完成握手，關閉標準輸入後自己結束，結束碼 0。
- 17 個工具的定義合計 49,723 字元，另有 1,219 字元的使用指示。接上去之後，這些每個對話都會佔用 context。
- 17 個裡純 HTTP 的有 3 個（`make_request`、`open_request_session`、`session_make_request`），12 個 `browser_` 開頭的要瀏覽器，另外 2 個管理連線階段。
- 伺服器送給 agent 的內建指示（`scrapling/core/ai/server.py` 第 1061～1068 行）有兩條和本機規則衝突：一條要 agent 依網站的「防護強度」選工具，防護強的改用瀏覽器；一條教 agent 怎麼拖曳速度會變的滑塊驗證。變更紀錄也把「幾乎能解任何 CAPTCHA」列為 MCP 伺服器的賣點（`docs/changelog.md` 第 69 行）。
- 工具面的風險：`browser_evaluate` 在頁面裡執行任意 JavaScript；`browser_save_state`／`browser_load_state` 在伺服器所在的機器上讀寫檔案；`browser_open` 可指定使用者資料目錄（第 3.3 節）；`make_request` 能從本機對任意網址發請求，預設偽裝成 Chrome。

### 5.5 收尾

```text
$ powershell -NoProfile -Command "... 比對 python／pythonw／scrapling／scrapling-mcp 且命令列含 scrapling 的行程 ..."
count=0
pid37080=False
```

查詢條件只比對這四個執行檔名，所以不會算到查詢用的 PowerShell 本身。沒有殘留行程。沙盒目錄保留。

## 6. 適用場景與分工

| 需求 | 建議用什麼 | 理由 |
| --- | --- | --- |
| 單篇公開文章或文件頁，讀進對話 | 維持現有的網頁讀取工具 | 已經會轉成精簡文字，不用多裝東西 |
| 社群平台、需要平台路由的來源 | 維持 `Agent-Reach` | Scrapling 的 HTTP 抓取對這類網站沒有優勢，隱身功能不在允許範圍 |
| 要點擊、填表、看畫面的頁面 | 維持瀏覽器類工具（內建瀏覽器、Playwright MCP） | 互動與截圖本來就是它們的工作 |
| **批次**把一個靜態文件站轉成 Markdown 存檔（給 RAG 或離線閱讀） | 可以用 Scrapling，**以函式庫方式**在獨立 venv 跑腳本 | 這是它相對有用的地方：選擇器加清洗加轉換一行完成。每個網站要先找正文選擇器，並自己處理相對連結 |
| 網站改版後自動追蹤元素 | 不採用 Adaptive Parser，或只在有二次驗證時用 | 第 5.3 節：誤配沒有訊號 |
| 把 `scrapling mcp` 註冊成 agent 的常駐工具 | **不做** | 第 5.4 節：context 成本、預設偽裝、內建指示與規則衝突、工具權限過大 |
| 繞過反爬、解驗證、隱身抓取 | 不做 | 不在本 repo 允許的範圍；作者本人在留言裡也承認沒有測過 |

對本機現有做法的具體建議：

- 不要把 `scrapling mcp` 加進任何 agent 的 MCP 設定檔。目前沒有加，維持現狀即可，不需要改檔。
- 之後真的需要批次轉文件站時，沿用這次的沙盒 venv，照 `eval\fetch_md.py` 的寫法（關掉 `impersonate` 與 `stealthy_headers`、先查 `robots.txt`、每頁之間停一下），並在呼叫時指定正文選擇器。不要裝進系統 Python。
- 轉出來的 Markdown 一律當成不可信的外部內容處理，和其他網頁內容一樣。

沒有比較的對象：筆記提到的 `Crawl4AI` 與 `Firecrawl` 這次沒有裝、沒有測，本文不對它們和 Scrapling 的優劣下結論。

## 7. 限制

- 只測了 3 個公開靜態頁，各 1 次請求。沒有測 JavaScript 產生內容的頁面、沒有測大量抓取、沒有測 429 與限流行為。
- 沒有啟動瀏覽器，所以 `DynamicFetcher`、`StealthyFetcher` 與 MCP 的 12 個瀏覽器工具都沒有實際執行；它們在 Windows 11 能不能用，這次不知道。本機已有其他工具安裝的 Playwright 瀏覽器，這些工具有可能不需要 `scrapling install` 就能啟動，沒有驗證。
- 沒有透過 MCP 呼叫抓取工具（第 1 節已說明）。
- HTTP 抓取器直接對私有 IP 發請求時會不會擋，沒有測；原始碼只確認了**轉址**到私有 IP 會被拒絕。
- 靜態檢視是人工閱讀加關鍵字搜尋，涵蓋 `scrapling/` 套件本身；49 個相依套件只確認來自 PyPI 的預建 wheel 並記錄雜湊，沒有逐一檢視原始碼。
- 圖片檔沒有檢查。
