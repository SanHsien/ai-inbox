# Grok Bot + Herdr 統一工作目錄進入點與 AGENTS.md 起步驅動規範

> 來源：`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`（任務 `T-20261026-28`）。本文件規範 Grok 派工環境如何透過 **Herdr**（終端復用器）在既有專案目錄內啟動 Coding CLI，並讓每個被啟動的 Agent 第一步就讀到該專案的 `AGENTS.md`，避免「換一個 Agent 就重新交代一次背景」。

---

## 1. 前提與查證範圍（2026-10-26 查證）

| 項目 | 狀態 | 出處 |
| :--- | :--- | :--- |
| Herdr 版本 | `0.9.1`（本機已裝，`%USERPROFILE%\.herdr`） | `herdr --version` 實測輸出，見第 4 節 |
| Herdr 支援的 Agent 清單含 `Grok CLI` | 已查證 | [herdr.dev/docs/agents](https://herdr.dev/docs/agents/)：「Herdr recognizes ... Grok CLI ...」 |
| `herdr agent start --kind` 的合法值含 `grok`；Antigravity 的值是 `agy`（不是 `antigravity`） | 已查證（本機 `--help` 實測輸出） | 見第 4 節 `herdr agent start --help` |
| Grok Build CLI 安裝方式 | 已查證 | [docs.x.ai/build/overview](https://docs.x.ai/build/overview)：PowerShell `irm https://x.ai/cli/install.ps1 \| iex` |
| Grok Build CLI 讀取 `AGENTS.md` 的順序與是否讀 `.grok/rules/` | 已查證（官方頁面文字；本機未裝 `grok`，未實機測試） | [docs.x.ai/build/features/project-rules](https://docs.x.ai/build/features/project-rules)：先讀 `~/.grok/` 全域規則，再從 repo 根目錄逐層讀到工作目錄，較深的檔優先；每層讀 `AGENTS.md`、`Agents.md`、`AGENT.md`、`CLAUDE.md`、`Claude.md`、`CLAUDE.local.md` 與 `.grok/rules/*.md`（也相容讀 `.claude/rules/`、`.cursor/rules/`）；被 `.gitignore` 排除的檔不讀；全文載入、沒有大小上限 |
| Grok Build CLI 的 headless 用法 `-p` / `--output-format streaming-json` | 已查證 | [docs.x.ai/build/overview](https://docs.x.ai/build/overview) |
| `grok inspect` 可列出目前目錄被發現的設定來源、instructions、skills、plugins、hooks、MCP servers | 已查證（官方頁面文字，未實機測試，因本機未安裝 `grok`） | 同上 |

**本機限制**：撰寫本文件時，`which grok` 於本機 PATH 中找不到結果（未安裝 Grok Build CLI），因此第 4 節「驗證範例」只能對 Herdr 側（已安裝、可實測）給出真實輸出；Grok CLI 側的指令是依官方文件轉錄，標註「未在本機實測」。

---

## 2. 派工拓撲

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Grok Bot（高階任務理解與派工指揮官，聊天介面 / API）                   │
│  - 拆解需求、決定要在哪個專案目錄動工                                   │
└───────────────────────────┬────────────────────────────────────────┘
                             │ 透過 Herdr socket API 下指令
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Herdr Server（本機常駐，herdr.sock）                                   │
│  workspace（每專案一個）── tab ── pane（終端格）                        │
└───────────────────────────┬────────────────────────────────────────┘
                             │ herdr agent start <name> --kind <kind> --pane <id>
              ┌──────────────┼───────────────┬───────────────┐
              ▼              ▼               ▼               ▼
        pane: claude    pane: codex      pane: grok      pane: antigravity
        （kind=claude） （kind=codex）   （kind=grok）    （kind=agy）
              │              │               │               │
              └──────────────┴───────┬───────┴───────────────┘
                                     ▼
                     每個 pane 的 cwd = 專案根目錄
                     Coding CLI 啟動時第一步讀該目錄的 AGENTS.md
                     （見第 3 節起步協議）
```

角色對應：
- **Grok Bot**：決策層，不直接碰程式碼；透過 Herdr 的 `agent prompt` 把任務文字送進對應 pane。
- **Herdr**：拓撲與狀態層，負責「這個 pane 現在是 idle／working／blocked／done」，不理解任務內容。
- **各 Coding CLI（Claude Code / Codex / Grok Build / Antigravity）**：施工層，各自在自己的 pane 裡以該專案目錄為 cwd 執行。

---

## 3. AGENTS.md 起步協議（Bootstrap Protocol）

### 3.1 目標

任何 Coding CLI 被 Herdr 啟動進某個專案目錄的 pane 後，**在收到第一個實質任務 Prompt 之前**，必須先掛載該專案根目錄的 `AGENTS.md`，取得：禁區、架構契約、依賴路徑、驗收標準（DoD）。

### 3.2 各 CLI 的實際讀取機制（按已查證程度分列）

| CLI | 讀取 AGENTS.md 的機制 | 查證狀態 |
| :--- | :--- | :--- |
| Claude Code | 有 `CLAUDE.md` 時只讀 `CLAUDE.md`；只有 `AGENTS.md` 時（v2.1.277 以上）直接讀；`CLAUDE.md` 內寫 `@AGENTS.md` 可匯入 | 已查證（官方文件），細節與出處見 [`codex-skills-agents-bootstrap-guide.md`](./codex-skills-agents-bootstrap-guide.md) 第 2 節 |
| Codex | 原生讀 `AGENTS.md`，每層可用 `AGENTS.override.md` 覆蓋，合併上限預設 32 KiB | 已查證（官方文件），同上 |
| Grok Build CLI | 從 repo 根目錄往工作目錄逐層讀 `AGENTS.md` 等檔與 `.grok/rules/*.md`，較深的優先 | 已查證（官方頁面，見第 1 節）；本機未裝，未實測 |
| Antigravity CLI | 官方 codelab 未提 `AGENTS.md` | **未查證**，同上文件第 2 節 |

### 3.3 無法保證「原生讀取」時的強制起步序列

因為並非每個 CLI 的 AGENTS.md 支援都在本機實測過（Antigravity 連官方說法都沒有），本規範不假設「裝好就會讀」，改用 Herdr 可控的派工流程確保讀取動作**一定發生**：

```text
1. herdr pane split --current --direction right --cwd "<專案根目錄>" --no-focus
   → 取得新 pane_id（cwd 已是專案根目錄，不是只 cd 進去）
2. herdr agent start <name> --kind <kind> --pane <pane_id>
   → 等待 agent 進入 idle（Herdr 偵測終端提示字元回到互動狀態）
3. herdr agent prompt <name> "先讀 AGENTS.md 全文並確認已載入目錄結構、禁區與 DoD 格式，讀完回報一行摘要再等待下一步指令。" --wait --until idle
   → 不論該 CLI 是否原生自動讀取，都在第一個 Prompt 明確要求讀取；
     Herdr 的 --wait 確保這一步真的執行完才送下一個任務
4. 確認回報摘要合理後，才送真正的任務 Prompt：
   herdr agent prompt <name> "<實際任務內容>" --wait
```

### 3.4 關鍵規則

1. **cwd 用 `pane split --cwd`，不要事後 `cd`**：Herdr 的 `pane split` 可在建立時直接指定工作目錄；比起起 pane 後再送 `cd` 指令，减少「CLI 已經啟動但 cwd 不對」的時序問題。
2. **第一個 Prompt 永遠是讀 AGENTS.md，不是任務本身**：即使某個 CLI 宣稱原生自動讀取，仍先用一個輕量 Prompt 驗證「它真的讀到了」，因為官方文件寫的讀取規則不等於這台機器、這個版本真的讀到了（3.2 表的 Grok 與 Antigravity 兩列都沒實機測過）。
3. **用 `--wait --until idle` 而非固定 sleep**：Herdr 的狀態偵測取代盲目等待秒數；若 CLI 卡在 `blocked`（例如要求確認），要先用 `herdr agent read <name>` 看清楚再決定。
4. **一個 pane 只對應一個專案 cwd**：不要在同一個 pane 裡切換專案目錄後繼續對話，否則該 CLI 的上下文會混雜兩個專案的規範。

---

## 4. 驗證範例

### 4.1 Herdr 側（本機已安裝 0.9.1，以下為真實指令與真實輸出）

```text
$ herdr --version
herdr 0.9.1

$ herdr status
client:
  version: 0.9.1
  channel: stable
  protocol: 22
  endpoint_protocol_generation: 1

server:
  status: running
  version: 0.9.1
  endpoint_compatible: yes
  private_protocol: 22
  private_protocol_compatible: yes
  socket: %USERPROFILE%\AppData\Roaming\herdr\herdr.sock

update:
  restart_needed: no
  server_binary_stale: no
```

（`herdr status` 為完整輸出，只把 socket 路徑的帳號改成 `%USERPROFILE%`。）

```text
$ herdr agent start --help
Usage: herdr agent start <NAME> --kind <KIND> --pane <ID> [OPTIONS] [-- [AGENT_ARG]...]
...
      --kind <KIND>
          Supported agent kind and canonical executable
          [possible values: pi, claude, codex, gemini, cursor, devin, agy, cline, omp,
           mastracode, opencode, copilot, kimi, kiro, droid, amp, grok, hermes, kilo,
           qodercli, qwen, letta, maki, muse]
```

以上為 2026-10-26 在本機以 `herdr agent start --help` 的實際輸出截取（`...` 處省略了 Arguments 與其他選項；唯讀查證，未實際建立 pane 或啟動任何 Agent）；`grok` 與 `agy` 都是合法的 `--kind` 值，與第 2 節拓撲圖一致。

### 4.2 Grok Build CLI 側（官方文件轉錄，本機未安裝，未實測）

```text
# 官方安裝（PowerShell，Windows）
irm https://x.ai/cli/install.ps1 | iex

# 查看目前目錄下 Grok 偵測到哪些設定來源（官方文件稱可列出 instructions/skills/plugins/hooks/MCP）
grok inspect

# Headless 派工（供 Herdr 的 agent prompt 以外的直接腳本呼叫參考）
grok -p "讀 AGENTS.md 並回報摘要" --output-format streaming-json
```

以上三行指令抄自 [docs.x.ai/build/overview](https://docs.x.ai/build/overview)（2026-10-26 查證），**未在本機執行**（未安裝 Grok Build CLI）；在本機真正接上 Grok Bot 派工前，應先手動跑一次 `grok inspect`，確認它是否真的列出 `AGENTS.md`，再決定 3.2 表格要不要把 Grok Build CLI 升級為「已查證：原生讀取」。

---

## 5. 與既有規範的關係

- 本文件規範的是「Grok Bot 透過 Herdr 派工時如何確保 AGENTS.md 被讀到」，不取代 `docs/agent-dispatch.md`（四套桌面端開新對話與回報的既有流程）；兩者可並用：Grok Bot 用本文件的序列起一個 pane，起完之後該 pane 內的 Agent 仍照 `docs/agent-dispatch.md` 的回報格式運作。
- Herdr 的 Socket API 細節（pane/agent/workspace 指令全貌）以本機已安裝版本的 `herdr --help`、`herdr agent --help` 等子指令輸出為準；官方線上文件版本可能領先或落後本機安裝版本，動工前先跑一次 `herdr status` 核對 client/server 版本一致。
