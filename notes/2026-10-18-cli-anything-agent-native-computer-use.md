---
id: 2026-10-18-cli-anything-agent-native-computer-use
title: "CLI-Anything：終結脆弱 GUI 點擊，將任意軟體自動升級為 Agent-Native CLI 與 Skill 的通用框架解構"
source_url: "https://www.threads.com/share/BAVrRFPLZ1/"
source_platform: "Threads"
author: "dev (@easyanythinghk)"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 3
cluster_role: "軟體升級"
short_title: "CLI-Anything"
tags:
  - cli-anything
  - agent-native
  - computer-use
  - cli-generation
  - tool-use
---

# CLI-Anything：終結脆弱 GUI 點擊，將任意軟體自動升級為 Agent-Native CLI 與 Skill 的通用框架解構

- **來源連結**：[Threads 原貼文 (easyanythinghk)](https://www.threads.com/share/BAVrRFPLZ1/)
- **官方 GitHub 倉庫**：[HKUDS/CLI-Anything (香港大學數據科學實驗室 HKUDS)](https://github.com/HKUDS/CLI-Anything)
- **學術論文**：[*CLI-Anything: Towards Agent-Native Computer Use* (arXiv:2606.03854)](https://arxiv.org/abs/2606.03854)
- **CLI-Hub 註冊表**：[clianything.cc](https://clianything.cc/)
- **發布平台 / 作者**：`Threads` / `dev (@easyanythinghk)`
- **分析日期**：`2026-10-18`
- **當前狀態**：`🟢 已做 (Done)`

---

## 1. 核心內容摘要

### 1.1 核心主張：從「仿生視覺點擊 (GUI)」走向「確定性指令 (CLI)」

當前主流的 AI 電腦操作（Computer Use / OS Agent / Browser-Use）普遍採取「人類仿生」路線：截取螢幕圖像 $\rightarrow$ VLM 視覺推論 $\rightarrow$ 計算 UI 元素座標 $\rightarrow$ 模擬滑鼠移動、點擊與按鍵。然而，這種模式在工程落地上面臨難以克服的四大死穴：
1. **極度脆弱性**：螢幕解析度變化、DPI 縮放、視窗重疊、深色模式切換或微小 UI 改版，都會導致座標計算失準，造成點擊失效甚至點錯按鈕（產生破壞性後果）。
2. **高延遲與 Token 暴增**：每一步動作都需要擷取高解析度螢幕截圖傳輸給多模態大模型，單次操作延遲長達數秒至數十秒，並在極短時間內吃爆模型的上下文視窗（Context Window）與預算。
3. **缺乏反饋閉環**：點擊完成後沒有程式碼級別的 Return Code 或 stderr，Agent 必須再截一張圖「猜測」操作是否成功。
4. **人類專用 vs. 模型原生**：GUI（圖形使用者介面）本質是為人類視覺神經系統設計的；**LLM 的原生語言是純文字、程式碼與結構化資料（JSON/Schema）**。

香港大學數據科學實驗室（HKUDS）提出的 **`CLI-Anything`** 掀起了一場範式轉移：**「不要讓 AI 像人一樣點介面，而是讓軟體像程式庫一樣向 AI 開放 CLI」**。透過全自動化逆向與生成管線，將任意桌面應用程式、本地開源軟體、Web 平台或底層 SDK，直接封裝成具備狀態管理、REPL 與結構化輸出的「Agent-Native 命令列介面（CLI Harness）」，並一鍵輸出符合 Claude Code / Antigravity / OpenClaw 標準的 `SKILL.md`。

```
[傳統 Computer Use vs. CLI-Anything Agent-Native 範式對比]

  傳統 GUI Computer Use:
  [Agent] ──> 截圖 (VLM 推論) ──> 像素座標 (x, y) ──> 滑鼠點擊 ──> 再截圖猜測結果
                ▲                      ▲                     │
                └── 高延遲 / 吃 Token  └── 容易點歪 / 視窗遮擋 ──┘ (脆弱無閉環)

  CLI-Anything (Agent-Native):
  [Agent] ──> 結構化指令 (JSON Args) ──> [CLI Harness] ──> [軟體 API / 引擎內部]
                ▲                              │
                └── 結構化輸出 (--json) / ExitCode ◄─ 確定性結果 (亞秒級 / 零猜測)
```

---

### 1.2 核心技術架構：7 階段自動化 CLI 生成管線 (7-Stage Pipeline)

`CLI-Anything` 具備一整套全自動將既有軟體或原始碼轉化為 Agent-Ready CLI 的引擎，其管線劃分為七大階段：

```
┌────────────────────────────────────────────────────────────────────────┐
│               CLI-Anything 7-Stage Harness Generation Pipeline         │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Codebase & API Inspection ── 掃描目標軟體之源碼、API、配置或內部物件架構 │
│         │                                                              │
│         ▼                                                              │
│ 2. Command Tree Extraction  ── 提煉階層式指令樹 (e.g. app domain action) │
│         │                                                              │
│         ▼                                                              │
│ 3. Stateful Daemon / REPL   ── 構建常駐背景行程與 Session，免去冷啟動開銷 │
│         │                                                              │
│         ▼                                                              │
│ 4. Structured JSON Schemas  ── 注入 `--json` 旗標與明確 Pydantic/Type 契約│
│         │                                                              │
│         ▼                                                              │
│ 5. Safe Sandboxing & Auth   ── 注入身份驗證隔離、權限檢查與危險操作確認機制 │
│         │                                                              │
│         ▼                                                              │
│ 6. End-to-End Test Suite    ── 自動合成 CLI 測試用例與契約驗證 (Verify Suite)│
│         │                                                              │
│         ▼                                                              │
│ 7. Agent Skill Synthesis    ── 產出 Claude Code / Antigravity `SKILL.md` 規範│
└────────────────────────────────────────────────────────────────────────┘
```

1. **源碼與介面分析 (Inspection)**：自動掃描目標軟體（如 Blender、FreeCAD、GIMP 或內部專案）的 SDK、Python 綁定、C/C++ 標頭檔或 REST/IPC 協定，抽取出所有核心操作集合。
2. **語意指令樹合成 (Command Tree)**：將扁平或複雜的 API 抽象為符合自然語言直覺的 POSIX CLI 指令，例如 `blender scene add-mesh --type cube` 或 `inkscape layer export --format svg`。
3. **狀態維護與長效 Daemon (Stateful Harness)**：針對啟動耗時的重型軟體（如 3D 渲染器、CAD 工具），CLI Harness 提供後台 Daemon 與 Socket 通訊機制，避免 Agent 每次下指令都要重新啟動一次主程式。
4. **純淨確定性輸出 (`--json`)**：所有指令預設或透過 `--json` 提供經過嚴格 Pydantic 驗證的結構化回傳，包含明確的物件 ID、執行狀態、數值資料與標準錯誤碼，徹底消除文字解析幻覺。
5. **安全閘門與沙盒邊界 (Safety & Sandbox)**：在 CLI 層面攔截高危參數（如未授權覆寫檔案、外部未受控執行），支援唯讀模式與審計日誌。
6. **自動化測試合成 (Contract Verification)**：系統自動生成單元測試與端到端測試，確認 CLI 每個指令都能正確與軟體核心通訊並回傳預期結果。
7. **Agent 技能自描述 (SKILL.md Generation)**：自動生成包含參數說明、少樣本範例（Few-shot examples）與最佳實踐的 Agent Skill 說明文檔，讓任何 Coding Agent 能夠直接載入使用。

---

### 1.3 生態與 CLI-Hub (`clianything.cc`)

除了自動化生成工具外，官方與社群設立了開源註冊中心 **CLI-Hub (`clianything.cc`)**，開箱即用收錄主流生產力工具的 Agent-Native CLI：
- **3D 與電腦圖學**：`blender-cli`（支援場景構建、材質調整、相機運鏡與渲染）、`freecad-cli`（參數化建模、STEP 導出）。
- **平面設計與向量**：`inkscape-cli`（SVG 幾何操作、路徑布林運算）、`gimp-cli`（圖片濾鏡、圖層合成）。
- **多媒體與串流**：`audacity-cli`（音軌剪輯、降噪）、`obs-cli`（場景切換、即時串流控制）。
- **辦公與知識庫**：`libreoffice-cli`（文件無損轉換）、`calibre-cli`（電子書格式重構）。

---

## 2. 對現有系統的啟發與落差分析

### 2.1 對應現有系統與專案

| 現有專案 / 規範 / 技能 | 關聯性與啟發重點 |
| :--- | :--- |
| **`RULE[user_global]`** (全域規範) | 「工具靜靜失效比大聲報錯危險得多」、「回報前要真正執行過檢查並貼出輸出」。CLI-Anything 的 `--json` 輸出與 Exit Code 天然提供確定性證據，比 GUI 截圖更能提供無可辯駁的驗收閉環。 |
| **`desktop-sense`** (Note 20) | `desktop-sense` 專注於**被動視覺感知**（從畫面自動擷取報錯上下文與視窗狀態）；`CLI-Anything` 專注於**主動動作執行**。兩者結合形成「螢幕看問題 $\rightarrow$ CLI 精準下指令修復」的完美多模態架構。 |
| **`cross-cli-subagent`** (Note 14) | 當 Opus 擔任規劃顧問外包給便宜 Agent 時，最忌諱叫便宜 Agent 去操作複雜的 GUI 軟體。透過 CLI-Anything 將所有軟體抽象為統一 CLI，各子代理（OpenCode / Codex / AGY）皆可用低成本的標準命令列完成複雜操作。 |
| **`SanHsien/agent-advisor`** | 可作為 Agent Advisor 推薦的工具延伸協議，將本地軟體快速包裝成 Antigravity / Claude Code 的標準 Plugin 或 Skill。 |

### 2.2 落差與採納判斷

- **值得採納的部分**：
  1. **禁止用 GUI 模擬取代 CLI 介面**：在 Agent 工作流中，凡是能透過 CLI / API / 腳本控制的工具，嚴禁使用滑鼠點擊座標（Computer Use）來操作。
  2. **標準化 `--json` 與狀態契約**：所有為 Agent 編寫的本地工具或封裝，必須落實 `--json` 結構化輸出與 Exit Code 規範，防止文字解析偏差。
  3. **自動化產生 `SKILL.md` 的思想**：借鑑其從 API / CLI 自動萃取參數與範例並組裝成標準 Skill 的管線，減少手動撰寫 Skill 的摩擦。
- **不適用 / 需調整的部分**：
  1. **Windows 11 原生相容性**：社群部分 Linux/POSIX 工具鏈（如依賴 Unix Domain Socket 或 bash 子程序的設計）在 Windows 11 原生環境下需要替換為具名管道（Named Pipes）或 Windows 原生通訊機制，需注意路徑編碼與換行問題。
  2. **避免非必要的重型 Daemon**：對於輕量任務，直接調用 Python CLI 即可，無需為了常駐狀態而常態性背景掛載吃記憶體的守護行程。

---

## 3. 拆解待辦事項（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261018-11`**｜**[優先級：高]** 在 Windows 11 本地環境測試 `HKUDS/CLI-Anything` 安裝與 CLI 生成管線（驗證 7-Stage Harness 生成、`--json` 輸出與 REPL 模式）
  - **目標範圍**：`SanHsien/ai-inbox` 與 本地 Agent 工具鏈環境（`C:\GitHub\CLI-Anything` 調研）
  - **完成日期**：2026-10-23
  - **具體做法**：
    1. 調研 `HKUDS/CLI-Anything` 開源倉庫（https://github.com/HKUDS/CLI-Anything）與 `clianything.cc` 註冊中心，整理其依賴清單與架構。
    2. 在 Windows 11 本地 Python 環境下測試 CLI-Anything 的核心生成命令（例如 `cli-anything inspect` / `cli-anything build`）。
    3. 以一項代表性軟體（如本地多媒體或文件處理庫）為目標，驗證其自動生成的 CLI Harness 是否具備完整的 `--json` 結構化回傳、錯誤處理與 exit code。
  - **驗收標準（DoD）**：產出之 CLI Harness 於 Windows 11 終端實際執行通過，提供 `--json` 輸出樣本與端到端測試通過截圖/紀錄，寫入實作報告。
  - **實作紀錄 / 證據**：完成套件安全審查（純 Python / Click / Prompt-Toolkit，無惡意二進位、無提權）並安裝至沙盒 `C:\GitHub\_sandbox\cli-anything\.venv`。選取開源無害之 Mermaid 圖表小工具（`mermaid/agent-harness`）實測，單元測試 `test_core.py` 5/5 通過、E2E 測試 `test_full_e2e.py` 5/5 通過（包含 SVG/PNG 渲染與 URL 生成），`--json` 結構化輸出、REPL 指令與 exit code 錯誤處理均在 Windows 11 原生環境驗證成功。

- [x] **`T-20261018-12`**｜**[優先級：中]** 建立「Agent-Native CLI 封裝與自動生成 Skill 標準協議（CLI-Anything to Skill Protocol）」
  - **目標範圍**：本地 Agent Skills 規範與 Antigravity / Claude Code 擴充工具庫
  - **具體做法**：
    1. 制定標準映射規則：將 CLI-Anything 產生的 command tree、參數 schema 與 exit code 規範，自動對齊至 Antigravity / Claude Code 的 `SKILL.md` 格式。
    2. 納入全域安全防線：在生成的 Skill 規範中預設注入高危指令攔截（Blast Radius）條款，禁止 Agent 在無確認情況下執行全域覆寫或具破壞性的 CLI 參數。
    3. 產出一份範例模板與自動轉換腳本原型（`tools/cli_to_skill.py`）。
  - **驗收標準（DoD）**：執行轉換腳本能正確將 CLI schema 轉換為符合 `AGENTS.md` 規範的 `SKILL.md`，並通過 `python tools/verify_inbox.py` 檢查。
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。撰寫標準協議文件 `docs/cli-anything-to-skill-protocol.md`，實作轉換腳本 `tools/cli_to_skill.py`，並新增單元測試 `tests/test_cli_to_skill.py`（單元測試通過）。

---

## 4. 關聯筆記與相關任務（Related Notes & Tasks）

- **Agent 原生工具鏈與環境感知**：
  - [desktop-sense 本機螢幕上下文與隱私防護](./2026-10-18-desktop-sense-local-screen-context.md) ｜ 關聯任務：`T-20261018-05`、`T-20261018-06`
  - [Agent-Reach 全網免 Key 檢索層](./2026-10-17-agent-reach-social-intelligence.md) ｜ 關聯任務：`T-20261017-05`、`T-20261017-06`
  - [Claude Code Mods 自體改造與熱重載](./2026-10-18-claude-code-mods-self-extending-runtime.md) ｜ 關聯任務：`T-20261018-09`、`T-20261018-10`
  - [Google Android 官方 30 個 Agent Skills](./2026-10-19-android-official-skills-google-coding-agent.md) ｜ 關聯任務：`T-20261019-05`、`T-20261019-06`

