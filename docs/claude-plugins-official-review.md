# Anthropic 官方 Claude Code 外掛清單深度檢閱與工作流適配報告

> 本檢閱報告直接讀取開源倉庫 [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) 之實際內容（檢閱當時記為 `plugins/` 40 個、第三方 100 個以上；2026-11-17 以 GitHub API 重查：`plugins/` 43 個目錄、`external_plugins/` 14 個目錄，`marketplace.json` 共 317 筆，其中 262 筆指向外部 repo）。  
> ⚠️ **2026-11-16 更正**：舊版把 `external_plugins/` 稱為「第三方驗證插件」「生態驗證插件」，這是錯的。上游 README 的警語是 Anthropic **不控制**插件內含的 MCP server、檔案或其他軟體，也**無法驗證**它們會照預期運作或日後不變；被收錄在這個目錄不代表內容經過安全審查。安裝任何一個（含下方推薦項）之前都要自己看過內容，第三方技能包另依維護者規則先過靜態檢查。README 也寫明 `marketplace.json` 的第三方條目會逐步移除，第三方改到 claude.ai 的目錄後台送件。依據見[來源筆記](../notes/2026-10-17-claude-plugins-official-directory.md)第 0 段。  
> 檢閱基準：維護者工作流環境（**Windows 11 原生**、Python/TypeScript、多 Agent 協作、Git 個人 fork 規範、嚴格零機密與品質閘門）。  
> 交付形式：以 `ai-inbox` 範本（`docs/claude-plugins-official-review.md`）交付。

> **2026-11-21 更正**：以 `.claude-plugin/marketplace.json` 重查（<https://github.com/anthropics/claude-plugins-official>，查閱日 2026-11-21）：`plugins/` 43 個目錄、`external_plugins/` 14 個、清單 317 筆（262 筆指向外部 repo），與 2026-11-17 的數字相同；本文點名的 18 個外掛都還在清單內。改了三處與清單不符的地方：`pr-review-toolkit` 與 `code-simplifier` 的分類是 `productivity`（舊版寫 `development`），兩者與 `security-guidance` 的功能敘述改照清單的 `description`（舊版的「架構、邊界、效能」「敏感路徑過濾」「死碼」清單裡沒有）。`skill-creator` 的 `quick_validate.py`、`run_eval.py` 確實存在，路徑是 `plugins/skill-creator/skills/skill-creator/scripts/`。「適合理由」欄是本 repo 的評估；2026-11-22 已在隔離設定目錄實際安裝其中三個（`security-guidance`、`skill-creator`、`pr-review-toolkit`），輸出見第 5 節，其餘五個未安裝實測。

---

## 1. 檢閱總覽與生態架構

官方倉庫將插件生態分為兩大維度：
1. **官方原生插件 (`plugins/`)**：由 Anthropic 團隊第一方維護，聚焦於代碼品質、LSP 語言支援、安全防護、技能建立與工作流管理。
2. **第三方插件 (`external_plugins/`)**：送件方式改版前收錄的第三方整合（2026-11-17 目錄內有 Asana、Context7、Firebase、GitHub、GitLab、Laravel Boost、Linear、Playwright、Serena、Terraform），加上 Anthropic 自己的頻道插件（Discord、fakechat、iMessage、Telegram）。Anthropic 不驗證其內容。

---

## 2. 適合維護者工作流的官方外掛評選 (Recommended)

針對維護者「Windows 11 原生 + Python/TS + 跨 Agent 調度 + 零機密防護」之工作流特徵，篩選出以下高度適配的插件：

| 插件名稱 (Plugin Name) | 分類 | 核心功能 | 適合理由與實測評估 | 推薦安裝指令 |
| :--- | :--- | :--- | :--- | :--- |
| **`pr-review-toolkit`** | `productivity` | 多個 PR 審查 agent：註解、測試、錯誤處理、型別設計、程式碼品質與簡化 | **極高適配**。維護者工作流極其注重交付前的嚴格審查與防線檢查，可無縫補充二審與盲審管線。 | `/plugin install pr-review-toolkit@claude-plugins-official` |
| **`security-guidance`** | `security` | 針對 Claude 產生的程式碼做安全審查：編輯時依樣式警告、Stop 時用模型審 diff | **極高適配**。完全契合維護者「API key、Token 零洩漏」硬性閘門。 | `/plugin install security-guidance@claude-plugins-official` |
| **`skill-creator`** | `development` | 建立、改進、基準評測與打包 Agent Skills | **極高適配**。提供 `quick_validate.py`、`run_eval.py` 等 Python 腳本，支援自製 Skill 的驗收與說明優化（`quick_validate.py` 需要 PyYAML，Windows 上要加 `-X utf8`，實測見第 5.4 節）。 | `/plugin install skill-creator@claude-plugins-official` |
| **`claude-md-management`** | `productivity` | 依據對話反思與教訓自動修訂與維護 `CLAUDE.md` / 規則庫 | **高適配**。符合維護者「被糾正後將教訓寫入對應規則檔」之工作習慣，維持全域規則健全。 | `/plugin install claude-md-management@claude-plugins-official` |
| **`pyright-lsp`** | `development` | Python 靜態類型檢查與代碼導引 LSP 伺服器 | **高適配**。Windows 11 環境下支援 Python 3 專案即時符號導引與語法分析，零外部重型依賴。 | `/plugin install pyright-lsp@claude-plugins-official` |
| **`typescript-lsp`** | `development` | TypeScript/JavaScript 語言伺服器 LSP 支援 | **高適配**。支援前端與全端專案（如 Next.js/React）在終端內的快速類型推斷與補全。 | `/plugin install typescript-lsp@claude-plugins-official` |
| **`session-report`** | `productivity` | 解析會話紀錄並產生視覺化 HTML 分析報告 | **中高適配**。便於事後覆盤 Agent 的 Tool 調用頻次、Token 消耗與任務耗時。 | `/plugin install session-report@claude-plugins-official` |
| **`code-simplifier`** | `productivity` | 在不改變功能的前提下簡化並整理程式碼（清晰、一致、好維護） | **高適配**。契合維護者「拒絕罐頭空殼與長篇無用架構」的精實原則。 | `/plugin install code-simplifier@claude-plugins-official` |

---

## 3. 不適合或應排除的外掛清單 (Not Recommended / Excluded)

| 插件名稱 (Plugin Name) | 分類 | 不適合理由 |
| :--- | :--- | :--- |
| **`imessage`** | `productivity` | **平台不相容**：底層依賴 macOS 的 Messages 資料庫與 AppleScript，在 Windows 11 原生環境完全不可用。 |
| **`swift-lsp`** | `development` | **技術棧偏離**：維護者本地主力為 Windows/Python/TypeScript，無 Swift/iOS 開發需求，引入僅徒增進程開銷。 |
| **`csharp-lsp` / `jdtls-lsp`** | `development` | **技術棧偏離**：維護者無 C# / Java 開發流，且 JDTLS 依賴重量級 JDK 運行時。 |
| **`blackrock-advisor-center-plugin`** | `productivity` | **特定商用閉源 SaaS**：僅限貝萊德認證財務顧問使用，一般開發者無法通過身份驗證。 |
| **`chronograph-gp` / `chronograph-lp`** | `productivity` | **私募股權專用系統**：高度垂直且受商業許可限制，與個人技術情報與 AI 任務總管無關。 |
| **`laravel-boost`** | `development` | **生態偏離**：專為 PHP Laravel 框架設計，維護者全端環境為 Next.js + Python。 |

---

## 4. 未查證或需環境驗證項目 (Unverified)

以下插件收錄於市場目錄中，但受限於相依服務狀態或缺乏公開驗收測試，標註為「未查證」：

1. **`vsql-extension-builder`**：
   - 狀態：**未查證**
   - 理由：VillageSQL 為小眾 MySQL 擴充生態，缺乏公開詳細文檔與本機 Windows 編譯工具鏈說明。
2. **`zocks-advisor`**：
   - 狀態：**未查證**
   - 理由：需綁定第三方 Zocks AI 語音財務顧問專有帳號，無公開免費 API 可供實測驗證。
3. **`chronograph-*` 系列**：
   - 狀態：**未查證**
   - 理由：企業內網專有 API，無法自公開網路進行單元測試與連通性驗證。

---

## 5. 外掛實測指令輸出（2026-11-22，Windows 11 原生）

> **2026-11-21 稽核後重做**：舊版這一節是「示意，未於本 repo 實測」，不符合任務 DoD 的「實測指令輸出」。以下全部是 2026-11-22 實際執行的輸出。
> **做法**：把環境變數 `CLAUDE_CONFIG_DIR` 指到一個全新的暫存目錄，所有指令都寫進那裡，不動本機原本的 Claude 設定；實測前後比對本機 `installed_plugins.json`、`known_marketplaces.json`、`settings.json` 的 SHA-256，三個檔都沒變。輸出裡的暫存目錄路徑改寫成 `<隔離設定目錄>`，其餘照實貼上，過長處以 `…` 省略並註明。
> **環境**：Claude Code 2.1.327、Git Bash、Python 3.14.10（系統預設編碼 `cp950`）、PyYAML 6.0.3。官方 marketplace 當下的 commit 是 `73c8cf3ea7e296057b467990f2f5d61b4c922260`（2026-11-20）。
> **沒測的**：沒有在互動 session 裡載入這三個外掛，所以 hook 實際觸發（`security-guidance` 的 SessionStart hook 會跑 `ensure_agent_sdk.py`）、`pr-review-toolkit` 的 agent 與 `/review-pr` 的執行結果都**未實測**；其餘 5 個推薦外掛（`claude-md-management`、`pyright-lsp`、`typescript-lsp`、`session-report`、`code-simplifier`）也未安裝實測。

### 5.1 加入官方 marketplace 並安裝三個推薦外掛

```text
$ claude plugin marketplace add anthropics/claude-plugins-official
Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): https://github.com/anthropics/claude-plugins-official.git
Clone complete, validating marketplace…
Cleaning up old marketplace cache…
✔ Successfully added marketplace: claude-plugins-official (declared in user settings)

$ claude plugin install security-guidance@claude-plugins-official
Installing plugin "security-guidance@claude-plugins-official"...✔ Successfully installed plugin: security-guidance@claude-plugins-official (scope: user)

$ claude plugin install skill-creator@claude-plugins-official
Installing plugin "skill-creator@claude-plugins-official"...✔ Successfully installed plugin: skill-creator@claude-plugins-official (scope: user)

$ claude plugin install pr-review-toolkit@claude-plugins-official
Installing plugin "pr-review-toolkit@claude-plugins-official"...✔ Successfully installed plugin: pr-review-toolkit@claude-plugins-official (scope: user)

$ claude plugin list
Installed plugins:

  ❯ pr-review-toolkit@claude-plugins-official
    Version: 1.0.1
    Scope: user
    Status: ✔ enabled

  ❯ security-guidance@claude-plugins-official
    Version: 2.0.21
    Scope: user
    Status: ✔ enabled

  ❯ skill-creator@claude-plugins-official
    Version: 73c8cf3ea7e2
    Scope: user
    Status: ✔ enabled
```

五個指令的結束碼都是 0。終端機裡的 `/plugin install …` 與這裡的 `claude plugin install …` 是同一功能的兩種入口；本節實測的是後者。

### 5.2 元件清單與預估 token 成本（`claude plugin details`）

```text
$ claude plugin details security-guidance@claude-plugins-official
security-guidance 2.0.21
  Description: Security review for Claude-generated code. Pattern-based warnings on edits, LLM-powered diff review on Stop, and an agentic commit reviewer that catches injection, XSS, SSRF, hardcoded secrets, and 25+ other vulnerability classes.
  Source: security-guidance@claude-plugins-official

Component inventory
  Skills (0)
  Agents (0)
  Hooks (4)  SessionStart, UserPromptSubmit, PostToolUse, Stop  (harness-only — no model context cost)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~0 tok   added to every session

$ claude plugin details skill-creator@claude-plugins-official
skill-creator
  Description: Create new skills, improve existing skills, and measure skill performance. …（略）
  Source: skill-creator@claude-plugins-official

Component inventory
  Skills (1)  skill-creator
  Agents (0)
  Hooks (0)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~87 tok   added to every session

Per-component (rounded)
  component      always-on  on-invoke
  skill-creator        ~90      ~8.3k

$ claude plugin details pr-review-toolkit@claude-plugins-official
pr-review-toolkit 1.0.1
  Description: Comprehensive PR review agents specializing in comments, tests, error handling, type design, code quality, and code simplification
  Source: pr-review-toolkit@claude-plugins-official

Component inventory
  Skills (1)  review-pr
  Agents (6)  code-reviewer, code-simplifier, comment-analyzer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer
  Hooks (0)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~1,268 tok   added to every session
  …（各元件明細略）
```

### 5.3 外掛結構驗證（`claude plugin validate`）

```text
$ claude plugin validate <隔離設定目錄>/plugins/cache/claude-plugins-official/security-guidance/2.0.21
…（hook 清單略）
⚠ Found 1 plugin directory warning:

  ❯ .claude-plugin/plugin.json icon: No icon (ICON_MISSING). …（略）

✔ Validation passed
```

結束碼 0。對整個 marketplace 目錄跑同一指令的結果是 `✔ Validation passed with warnings`（結束碼 0；警告多是個別外掛的 README 沒有安裝指令那一行）。

### 5.4 `skill-creator` 的 `quick_validate.py`：Windows 上要加 `-X utf8`

腳本位置：`<隔離設定目錄>/plugins/cache/claude-plugins-official/skill-creator/73c8cf3ea7e2/skills/skill-creator/scripts/quick_validate.py`。執行前先讀過全文（102 行，只讀 `SKILL.md` 並檢查 frontmatter，不寫檔、不連網）。

```text
$ python quick_validate.py <skill-creator 自己的 skill 目錄>
Traceback (most recent call last):
  …（略）
    content = skill_md.read_text()
  …（略）
UnicodeDecodeError: 'cp950' codec can't decode byte 0xe2 in position 3605: illegal multibyte sequence
（結束碼 1）

$ python -X utf8 quick_validate.py <本 repo>/templates/agent-reach
Skill is valid!
（結束碼 0）

$ python quick_validate.py
Usage: python quick_validate.py <skill_directory>
（結束碼 1）

$ python quick_validate.py <空目錄>
SKILL.md not found
（結束碼 1）
```

實測得到的兩件事：

1. **Windows 相容性問題**：腳本用 `read_text()` 讀 `SKILL.md` 而沒有指定編碼。繁體中文 Windows 的預設編碼是 `cp950`，只要 `SKILL.md` 含非 ASCII 字元就會當掉，連外掛自己的 `SKILL.md` 都過不了。加 `python -X utf8`（或設環境變數 `PYTHONUTF8=1`）就正常。
2. **不是純標準函式庫**：腳本 `import yaml`，要先裝 PyYAML；沒裝會在第 9 行 `ModuleNotFoundError`。上方第 2 節表格舊版寫的「stdlib 腳本」已更正。
