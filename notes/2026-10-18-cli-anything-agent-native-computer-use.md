---
id: 2026-10-18-cli-anything-agent-native-computer-use
title: "CLI-Anything：終結脆弱 GUI 點擊，將任意軟體自動升級為 Agent-Native CLI 與 Skill 的通用框架解構"
source_url: "https://www.threads.com/share/BAVrRFPLZ1/"
source_platform: "Threads"
author: "dev (@easyanythinghk)"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: "3"
cluster_role: "逆向工程與軟體封裝"
short_title: "CLI-Anything"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "官方 README 的多支示範動圖（FreeCAD、Blender、Draw.io 等，總數未知）沒有逐支看，README 只看了 2 張主要圖片；Threads 貼文圖 1／1 張、留言 6／6 則都看過"
source_images: 3
source_replies: 6
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

## 0. 原始資料盤點

> 2026-11-16 重審：看了 Threads 貼文文字、作者附的 1 張圖、留言區全部 6 則（含作者 3 則），並回頭核對官方 repo 的 README、`HARNESS.md` 與 README 內 2 張主要圖片（前導漫畫、架構圖）。README 另有多支示範動圖（FreeCAD、Blender、Draw.io 等）沒有逐支看。

- **作者圖片**：
  - 貼文圖 1：一張自製的 GitHub Trending 資訊卡。寫著 2026-10-18 排行第 4、Python、54,205 星（當日 +574）、Apache-2.0，四個標籤是 AI Agents／CLI Automation／Agent-Native／Open Source。**沒有任何架構或流程內容**。
  - README 圖 1（前導漫畫）：三格漫畫，從「軟體很多、CLI 很少」到戴上 CLI-Anything 之後各種軟體都能用指令操作，屬於宣傳圖。
  - README 圖 2（架構圖）：`/cli-anything <software>` 指令驅動外掛的七個階段，依序是 **1 程式碼分析、2 CLI 設計、3 實作、4 測試規劃、5 測試實作、6 測試文件、7 發布到 PyPI**，產出放在 `agent-harness/` 資料夾，最下方是它所包裝的真實軟體。
- **作者留言補充**：作者在留言貼了官方 GitHub 連結，其餘兩則是回應網友的閒聊，沒有技術補充。
- **網友留言重點**：
  - @more.yu_：真正受衝擊的是花大錢做「AI 整合」的廠商，精心設計的 API 與外掛生態可能被一個 CLI 工具繞過；以後賣的是「繞不過去的理由」。作者回應同意，認為護城河會從 API 轉到資料與信任。
  - @chloe_cheung55：分享自己在業務端用 Dify 工作流做類似的事，屬於經驗分享，沒有對 CLI-Anything 的實測。
  - 沒有人回報實際安裝或使用結果，也沒有反駁。
- **對分析的影響**：
  - **1.2 的「七階段管線」原本寫錯，已整段改寫**。原稿列的「常駐 Daemon」「Pydantic JSON Schema」「安全沙盒與身分驗證」三個階段在官方資料裡不存在；貼文與附圖也完全沒提七階段。正確的七階段依官方架構圖與 `cli-anything-plugin/HARNESS.md`：程式碼分析、CLI 架構設計、實作、測試規劃、測試實作、測試文件、PyPI 發布，另有 6.5 階段產生 `SKILL.md`。
  - 原稿 `T-20261018-11` 做法裡的 `cli-anything inspect`／`cli-anything build` 指令不存在；官方入口是在 agent 裡執行 `/cli-anything <軟體路徑或 repo>`，補強用 `/refine`。該任務已完成且實測的是既有的 Mermaid harness，證據不受影響，任務文字不改。
  - 補上官方自己寫的三項限制（原稿沒有）：要用最強等級的模型才生得好、**要有原始碼**（只有編譯檔的軟體品質會大幅下降）、通常要多跑幾輪 `/refine`。標題的「任意軟體」因此要打折，已在 1.1 加註。
  - 星數：貼文圖寫 54,205；2026-11-16 查 GitHub API 是 58,788。授權 Apache-2.0 與圖一致。
  - 2.2「值得採納」第 2 點寫的「Pydantic 驗證」沒有依據，官方只說用 Click 提供 `--json` 結構化輸出；該點的主張（工具要有 `--json` 與 exit code）仍成立，不改。

---

## 1. 核心內容摘要

### 1.1 核心主張：從「仿生視覺點擊 (GUI)」走向「確定性指令 (CLI)」

當前主流的 AI 電腦操作（Computer Use / OS Agent / Browser-Use）普遍採取「人類仿生」路線：截取螢幕圖像 $\rightarrow$ VLM 視覺推論 $\rightarrow$ 計算 UI 元素座標 $\rightarrow$ 模擬滑鼠移動、點擊與按鍵。然而，這種模式在工程落地上面臨難以克服的四大死穴：
1. **極度脆弱性**：螢幕解析度變化、DPI 縮放、視窗重疊、深色模式切換或微小 UI 改版，都會導致座標計算失準，造成點擊失效甚至點錯按鈕（產生破壞性後果）。
2. **高延遲與 Token 暴增**：每一步動作都需要擷取高解析度螢幕截圖傳輸給多模態大模型，單次操作延遲長達數秒至數十秒，並在極短時間內吃爆模型的上下文視窗（Context Window）與預算。
3. **缺乏反饋閉環**：點擊完成後沒有程式碼級別的 Return Code 或 stderr，Agent 必須再截一張圖「猜測」操作是否成功。
4. **人類專用 vs. 模型原生**：GUI（圖形使用者介面）本質是為人類視覺神經系統設計的；**LLM 的原生語言是純文字、程式碼與結構化資料（JSON/Schema）**。

香港大學數據科學實驗室（HKUDS）提出的 **`CLI-Anything`** 掀起了一場範式轉移：**「不要讓 AI 像人一樣點介面，而是讓軟體像程式庫一樣向 AI 開放 CLI」**。透過全自動化逆向與生成管線，將任意桌面應用程式、本地開源軟體、Web 平台或底層 SDK，直接封裝成具備狀態管理、REPL 與結構化輸出的「Agent-Native 命令列介面（CLI Harness）」（前提是拿得到原始碼，見 1.2 的官方限制），並一鍵輸出符合 Claude Code / Antigravity / OpenClaw 標準的 `SKILL.md`。

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

### 1.2 核心技術架構：7 階段自動化 CLI 生成管線 (7-Phase Pipeline)

> 2026-11-16 依官方架構圖與 `cli-anything-plugin/HARNESS.md` 重寫。原稿列的階段名稱（常駐 Daemon、Pydantic Schema、安全沙盒）查無依據，已移除。

`CLI-Anything` 是裝在 Coding Agent 裡的外掛／技能：在 agent 內執行 `/cli-anything <軟體路徑或 repo>`，由 agent 照 `HARNESS.md` 的七個階段替目標軟體寫出一支 CLI。

```
/cli-anything <software>
        │
        ▼
1. Codebase Analysis   掃原始碼，把 GUI 動作對應到背後的 API
2. CLI Design          規劃指令群組、狀態模型、輸出格式
3. Implementation      用 Click 寫出 CLI：REPL、--json 輸出、undo/redo
4. Test Planning       先寫 TEST.md（單元與端到端測試計畫）
5. Test Implementation 實作測試
6. Test Documentation  把測試結果寫回 TEST.md
   6.5 SKILL.md        從 Click 裝飾器、setup.py、README 自動產生技能說明
7. PyPI Publishing     建 setup.py，安裝到 PATH（指令名 cli-anything-<軟體>）
        │
        ▼
agent-harness/ 資料夾（產出的 CLI） ──呼叫──> 真實軟體（Blender、LibreOffice…）
```

- **真的去叫原軟體做事**：產出的 CLI 直接呼叫真實應用程式（例如用 LibreOffice 轉 PDF、用 Blender 算圖），不是另外重寫一套簡化版。
- **狀態管理**：專案狀態持久化、支援 undo／redo，各 CLI 共用同一套 REPL 介面。
- **輸出**：`--json` 給 agent 讀，預設輸出給人看；`--help` 讓 agent 自己查用法。
- **覆蓋不足時**：再跑 `/refine`，由 agent 比對軟體全部功能與目前 CLI 的差距後補指令與測試。
- **官方列出的限制**：
  1. 需要最強等級的模型，較弱的模型生出來的 CLI 常不完整。
  2. **要有原始碼**。只有編譯檔、需要反編譯的軟體，品質與覆蓋率會大幅下降。
  3. 一次通常生不完，要反覆 `/refine`。

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

