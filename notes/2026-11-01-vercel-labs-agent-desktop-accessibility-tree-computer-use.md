---
id: 2026-11-01-vercel-labs-agent-desktop-accessibility-tree-computer-use
title: "Vercel Labs agent-desktop 開源架構解構：告別截圖猜座標、作業系統無障礙樹（Accessibility Tree）操作與生產級 Computer Use"
source_url: "https://www.threads.com/@yrzheee/post/DfKiW50Efc1"
source_platform: "Threads (@yrzheee & @largitdata)"
author: "Renzhe Yu (@yrzheee) / LargitData 大數軟體 (@largitdata) / Chris Tate (Vercel Labs)"
analyzed_at: 2026-11-01
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "桌面操控與代理身分"
short_title: "Vercel Labs agent-desktop無障礙樹操作"
tags:
  - agent-desktop
  - vercel-labs
  - computer-use
  - accessibility-tree
  - a11y
  - rust
  - token-optimization
  - ui-automation
  - multi-agent
---

# Vercel Labs agent-desktop 開源架構解構：告別截圖猜座標、作業系統無障礙樹（Accessibility Tree）操作與生產級 Computer Use

- **來源連結**：
  - [Threads 貼文 1：Renzhe Yu (@yrzheee)](https://www.threads.com/@yrzheee/post/DfKiW50Efc1) ｜ [短網址](https://www.threads.com/share/E6TGj94c_/)
  - [Threads 貼文 2：LargitData 大數軟體 (@largitdata)](https://www.threads.com/@largitdata/post/DfM7e2VEvwr) ｜ [短網址](https://www.threads.com/share/EC0q49Tz8/)
- **核心作者**：Chris Tate（Vercel Labs，`agent-browser` 與 `agent-desktop` 作者）
- **核心分析者**：Renzhe Yu（@yrzheee）、LargitData 大數軟體（@largitdata）
- **官方開源專案**：[vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop)（Rust 打造，跨 macOS / Windows / Linux 桌面操作工具）
- **個人 Fork 倉庫**：[SanHsien/agent-desktop](https://github.com/SanHsien/agent-desktop)（本地路徑 `C:\GitHub\agent-desktop`，已配置 upstream 與個人預設遠端）
- **辦理情形**：已正式建立獨立頂層 Session 實施 fork 成果移植、Windows UIA 驗證與全系統 Agent Skill 發布（`agent-assets` 與 CLI 整合）；完成架構規格書 `docs/agent-desktop-computer-use-spec.md`、驗證工具與單元測試，全域 Skill 已部署至 Antigravity、Claude Code、Codex、Hermes 共用環境並通過 `SanHsien/agent-assets` 登記與推送（SHA: `1c433eb`）。頂層派工會話（`2b43ab20-6ed7-468f-8a01-09e6b959ce23`）已全面結案回報：完成雙語 README（中英對齊）與 Repo About、分支與 Release/Tag 收斂（v1.0.2 正式版附帶 Windows 二進制產物）、Supply Chain / CodeQL / Fork Maintenance / CI 4 項 GitHub Actions 100% 綠燈通過、以及全面 Bug 修復（Windows 11 桌面隔離 attach_input_desktop、剪貼簿競態、特殊 SID DACL 白名單、FFI 指標安全、CachePolicy 斷言與 400 行源碼規範，3,400+ 測試全數通過，最新 commit `a67bf683`）。
- **當前狀態**：`🟢 已結案 (Resolved)`
- **相關交叉參照**：
  - [`2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md`](https://github.com/SanHsien/claude-context-audit/blob/main/notes/2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md)（經驗驅動 Token 成本控制與上下文壓縮）
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（Herdr 終端復用與統一網關調度）
  - [`notes/2026-10-19-android-official-skills-google-coding-agent.md`](./2026-10-19-android-official-skills-google-coding-agent.md)（Android 官方節點樹與 UI 結構層檢驗）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（四 Agent 平行派工與五路工具流整合）

---

## 1. 來源摘要與背景脈絡

### 1.1 傳統 Computer Use 的三大致命瓶頸
自 2024 年底 Anthropic 發布 Computer Use 以來，業界的桌面操控 Agent 大多依循「**截圖 → VLM（視覺語言模型）辨識 → 猜測點擊座標 (x, y) → 點擊 → 再次截圖確認**」的視覺閉環（Visual Loop）。此模式在生產環境中暴露了三大結構性缺陷：
1. **Token 消耗極端昂貴**：Anthropic 官方數據顯示，每張高解析度截圖約消耗 1,000～1,800 個 Input Token。連續操作 10 個步驟即燒掉近 20,000 Tokens，成本極高且容易觸發速率限制（Rate Limits）。
2. **座標漂移與高脆弱性（Fragility）**：只要視窗稍微位移、解析度縮放改變、動畫尚未播放完畢、或系統彈出無關通知，座標即刻偏離目標，導致點擊落空甚至誤點破壞性按鈕。
3. **焦點爭搶與打擾（Screen Hijacking）**：視覺方案通常需要強制將目標應用置於最上層（Foreground），並透過模擬硬體滑鼠軌跡點擊，使用者無法在同台電腦上並行工作。

### 1.2 `agent-desktop` 的破局思考：回歸 OS 語意結構
2026 年 10 月 31 日，Vercel Labs 正式開源 `agent-desktop`（由開發 `agent-browser` 的 Chris Tate 主導）。其核心主張為：**電腦看畫面本來就不該靠肉眼截圖，而應直接存取作業系統為讀屏軟體設計的無障礙樹（Accessibility Tree）**。
- **macOS**：存取 macOS Accessibility API，維護專屬 Command Host 避免物件生命週期失效。
- **Windows**：存取 UI Automation（UIA）與 Win32 API，在相同 Integrity Level 下完全無須管理員提權。
- **Linux**：存取 `at-spi2-core`，支援 X11 與 Wayland session。

---

## 2. 架構核心解構與技術深度

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                       AI Coding Agent                       │
       │           (Claude Code / Codex / Antigravity)               │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         1. snapshot --app Slack -i
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │              agent-desktop CLI / FFI (Rust Core)            │
       │   - 讀取作業系統 Accessibility Tree (a11y)                   │
       │   - 建立 Snapshot ID (例: s8f3k2p9) 與 Ref 編號 (@s8f3k2p9:e8) │
       │   - 支援 --skeleton 骨架速描 / --root 區域下鑽               │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         2. 回傳純文本結構化 JSON Tree
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                     Agent 決策與派工                        │
       │   - 不猜座標，直接鎖定元素 ID: @s8f3k2p9:e8                  │
       │   - Token 消耗自 1500 下降至 ~100 Tokens (省 90% 以上)      │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         3. click '@s8f3k2p9:e8' (Headless)
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                 作業系統原生 API 調用層                     │
       │   - macOS: NSAccessibility / Private Host (15min idle)      │
       │   - Windows: UI Automation (UIA) Provider (No-focus Click)  │
       │   - Linux: AT-SPI2 Core D-Bus Engine                        │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
               4. 返回結果 Envelope (帶 Disposition Retry 判定)
                                      ▼
                 成功: { ok: true, data: ... }
                 過期: { ok: false, error: { code: "STALE_REF",
                                             disposition: { retry: "safe" } } }
```

### 2.1 56 項純 Rust 運作指令集與 JSON Envelope
`agent-desktop` 封裝了 60 個指令（56 個即刻可用運作指令），全部透過標準 JSON 信封輸出，避免字串解析脆弱性：
- **Observe（觀察群組）**：`snapshot`（取得結構化樹）、`find`（條件尋找）、`get`（讀取屬性）、`is`（狀態驗證）、`screenshot`（按需局部或全螢幕截圖，僅作為驗證或多模態後備）、`list-surfaces`。
- **Act on Ref（Ref 動作群組）**：`click`、`double-click`、`type`、`set-value`、`scroll`、`expand`、`collapse`、`toggle`、`check` 等。所有操作皆指向 `@<snapshot_id>:<element_id>`。
- **Windows / Apps 管理群組**：`launch`、`close-app`、`list-apps`、`list-windows`、`focus-window`、`resize-window` 等。
- **Clipboard & System**：剪貼簿操作、通知中心監聽與互動、權限引導。

### 2.2 命名空間 Ref（Namespace Refs）與過期防禦（STALE_REF）
傳統 RPA 常常在點擊瞬間，介面因非同步更新而導致點到下一行的錯誤按鈕。`agent-desktop` 在設計上引入了嚴格的語意鎖定：
1. **Snapshot 綁定**：每個 Ref 都強制帶有其所屬的 Snapshot 雜湊命名空間（如 `@s8f3k2p9:e8`）。若是拿沒有帶命名空間的裸 ID（如 `@e8`），CLI 直接拋出 `INVALID_ARGS` 拒絕執行。
2. **STALE_REF 過期偵測**：若在 Agent 下達指令前，UI 元件已重繪或消失，底層會立即回傳 `STALE_REF` 或 `AMBIGUOUS_TARGET`，絕不靜默點擊現存具有相同識別碼的鄰近元件。
3. **Disposition Contract（重試安全性標籤）**：每個錯誤都會明確標註 `error.disposition.retry` 是否為 `"safe"`。若非安全（例如破壞性操作或表單已提交），Agent 嚴禁盲目循環重試。

### 2.3 預設 Headless 操作與 Token 極致節約
- **非搶佔式操作（Headless by default）**： Ref 動作直接透過 Accessibility API 驅動底層元件的動作事件，**無須移動系統滑鼠指標，亦無須強搶前景焦點**。使用者可以在螢幕上寫代碼，背景的 Agent 則在另一個視窗默默填寫表單或點選選單。只有明確加上 `--headed` 時才會模擬實體滑鼠軌跡。
- **Token 降維打擊**：
  - 傳統視覺方案：截圖 1,000～1,800 tokens/次。
  - `agent-desktop`：精簡 JSON 樹約 80～200 tokens/次，密集視窗支援 `--skeleton`（骨架模式）縮減至 50 tokens 內，降低 90% 以上 Token 成本。
- **PowerShell 語法防雷規範**：在 Windows PowerShell 環境中，`@token` 是 splatting 展開運算子，因此呼叫時必須加上單引號保護（如 `agent-desktop click '@s8f3k2p9:e8'`）。

---

## 3. 對現有系統的啟發與落差分析

| 評估維度 | `agent-desktop` 範式特徵 | 本知識庫與目前 Agent 體系現狀 | 落地借鑑與改進方向 |
| :--- | :--- | :--- | :--- |
| **GUI 操控基礎設施** | 純 Rust 底層直讀 OS 無障礙樹，不靠截圖 | 現有 Agent 操作桌面多依賴瀏覽器 Playwright 或無頭 CLI，缺乏通用 OS 級視窗操控能力 | 引入 `agent-desktop` 作為原生 OS 操作 Skill，納入跨平台桌面派工 |
| **成本與延遲** | 單次 Snapshot 僅需數十 Tokens，延遲毫秒級 | 視覺 Computer Use 成本高昂且多模態 API 延遲動輒 3~5 秒 | 將 a11y tree 作為預設觀察路徑，僅在非標準 Canvas/DirectX 遊戲畫面時才降級為截圖 |
| **錯誤防禦與重試** | 內建 `STALE_REF`、多視窗歧義警報與 Disposition 重試安全性 | 目前部分 Agent 在 GUI 腳本失敗時常盲目重試造成無限迴圈（Doom Loop） | 制定「桌面操控安全重試規約」，嚴格檢驗 `disposition.retry == 'safe'` |
| **平台相容性** | 跨 macOS、Windows（UIA）、Linux（AT-SPI）統一信封架構 | 多數開源 GUI Agent 僅針對 macOS（如 AppleScript）或特定 Linux 沙盒設計 | 支援 Windows 11 原生 UIA 驅動，符合本環境之 Windows 原生部署前提 |

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將 Vercel Labs `agent-desktop` 所確立的「無障礙樹 Computer Use」架構落實為可執行的工程規範與驗證測試，規劃以下 3 項任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261101-13`**｜**[優先級：高]** 撰寫「OS 級 Computer Use 架構規格書：Accessibility Tree 無障礙樹、命名空間 Ref 與無像素匹配設計手冊」收錄於 `docs/agent-desktop-computer-use-spec.md`
  - **目標範圍**：`docs/agent-desktop-computer-use-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 深入對比視覺截圖方案（Pixel Matching）與語意無障礙樹方案（a11y Tree）在 Token 消耗、執行延遲、座標抗噪性與安全性之矩陣。
    2. 詳解 Windows UI Automation（UIA）、macOS Accessibility API 與 Linux AT-SPI2 三大作業系統節點模型之對照映射。
    3. 規範命名空間 Ref 生成算法、過期檢測（`STALE_REF`）狀態機、以及「Safe to Retry vs Unsafe」處置合約（Disposition Contract）。
  - **驗收標準（DoD）**：產出 `docs/agent-desktop-computer-use-spec.md`，具備標準 Markdown 結構與繁體中文規範；以 `Test-Path docs/agent-desktop-computer-use-spec.md` 驗證存在。
  - **完成日期**：2026-11-01
  - **實作紀錄 / 證據**：已完成規格書撰寫，詳述 a11y 樹與截圖方案之五維對比矩陣、Windows UIA / WindowStation Desktop 隔離深層實證機制、命名空間 Ref 演算法與處置重試合約；以 `Test-Path docs/agent-desktop-computer-use-spec.md` 驗證為 True。同時同步納入 `SanHsien/agent-desktop` 倉庫 `docs/agent-desktop-computer-use-spec.md`（commit `24a548cc`）。

- [x] **`T-20261101-14`**｜**[優先級：中]** 實作「Windows UI Automation 無障礙樹快照與 Ref 點擊驗證腳本」於 `tools/verify_a11y_tree_snapshot.py` 與單元測試
  - **目標範圍**：`tools/verify_a11y_tree_snapshot.py`、`tests/test_verify_a11y_tree_snapshot.py`
  - **具體做法**：
    1. 實作純 Python 模擬與驗證工具 `tools/verify_a11y_tree_snapshot.py`，支援解析標準 `agent-desktop` JSON 快照結構。
    2. 實作 Ref 解析器與狀態機，檢驗：命名空間格式合法性（包含 PowerShell 單引號跳脫檢查）、過期 Ref 攔截（回傳 `STALE_REF`）、以及重試安全標籤（`disposition.retry`）。
    3. 撰寫完整的單元測試套件 `tests/test_verify_a11y_tree_snapshot.py`，覆蓋有效 Ref 點擊、過期 Ref 檢測、多視窗歧義攔截與錯誤信封解析。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_a11y_tree_snapshot.py` 綠燈通過。
  - **完成日期**：2026-11-01
  - **實作紀錄 / 證據**：已實作 `tools/verify_a11y_tree_snapshot.py` 與 `tests/test_verify_a11y_tree_snapshot.py`，支援 Ref 格式校驗、PowerShell Splatting 防呆剝離、STALE_REF 狀態機、骨架折疊、Windows POLICY_DENIED 限制與 Disposition 合約。執行 `python -m unittest tests/test_verify_a11y_tree_snapshot.py` 13 項測試全數綠燈通過；`tests/test_cli_help_encoding.py` 通過驗證。

- [x] **`T-20261101-15`**｜**[優先級：低]** 產出標準化「Agent 桌面操控指令集與 STALE_REF 安全重試 Prompt 模板」收錄於 `templates/agent-desktop-skill-prompt.md`
  - **目標範圍**：`templates/agent-desktop-skill-prompt.md`
  - **具體做法**：
    1. 產出可直接置入 `AGENTS.md` 或 Agent Harness 系統提示詞的標準指南，規範 Agent 如何依序調用 `snapshot`、尋找目標、採取行動與二次觀察驗證。
    2. 制定嚴格的防踩坑指令：強制要求 PowerShell 使用單引號包裹 `@ref`、遇到 `STALE_REF` 必須重新執行 `snapshot` 而非盲猜、遇到 `disposition.retry: "unsafe"` 必須立即暫停並回報使用者。
    3. 提供密集介面優化策略範例（`--skeleton` 與 `--root` 區域下鑽流程）。
  - **驗收標準（DoD）**：產出 `templates/agent-desktop-skill-prompt.md`，結構清晰且包含範例工作流；以 `Test-Path templates/agent-desktop-skill-prompt.md` 驗證存在。
  - **完成日期**：2026-11-01
  - **實作紀錄 / 證據**：已產出 `templates/agent-desktop-skill-prompt.md`，以 `Test-Path` 驗證為 True。同時已建立全系統跨 Agent 技能 `~/.gemini/config/skills/agent-desktop/SKILL.md`，並在 `SanHsien/agent-assets` 完成核准登記（`skills/agent-desktop/SKILL.md`、`knowledge/agent-desktop-os-accessibility-tree.md`），通過 90 項資產合約檢驗並完成推送（commit `1c433eb`）。
