---
id: "2026-11-15-danyuchn-pii-guard-claude-mod-eval"
title: "danyuchn/pii-guard：台灣繁中個資可逆遮罩與 Claude Mod（Fail-Closed＋Edit 修復）架構評估"
source_url: "https://github.com/danyuchn/pii-guard"
source_platform: "GitHub / Social"
author: "danyuchn"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 3
cluster_role: "台灣個資遮罩Mod"
short_title: "PII-Guard個資遮罩Mod"
tags:
  - pii-guard
  - claude-mods
  - privacy
  - taiwan-pii
  - fail-closed
  - hookd
---

# danyuchn/pii-guard：台灣繁中個資可逆遮罩與 Claude Mod（Fail-Closed＋Edit 修復）架構評估

- **來源連結**：[danyuchn/pii-guard](https://github.com/danyuchn/pii-guard)（**MIT**，255 Stars / 23 Forks，最後更新 `2026-10-25`）
- **發布平台 / 作者**：`GitHub` / `danyuchn`（前作 `claude-work-mode` 作者）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-18-claude-code-mods-self-extending-runtime.md`](./2026-10-18-claude-code-mods-self-extending-runtime.md)（Claude Code Mods 執行期與無沙盒安全邊界）
  - [`notes/2026-11-08-dustin-gmat-danyuchn-claude-work-mode-session-modes.md`](./2026-11-08-dustin-gmat-danyuchn-claude-work-mode-session-modes.md)（同作者之會話模式插件）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：`danyuchn` 開源的繁體中文（台灣）可逆去識別化引擎 `pii-guard`，專為「讓台灣企業／顧問團隊在雲端 AI 處理敏感文件時，個資不離機」設計，包含 Python 核心 CLI／本機補標 Web UI、常駐服務 `pii-guard-hookd` 以及最新實作的 **Claude Mod 前端**（`examples/claude-code-mod/`）。
- **Why（解決什麼痛點）**：
  - 主流海外遮罩閘道（如 LiteLLM + Presidio、PrivAiTe）不支援台灣身分證／居留證字號、統一編號、本地電話與繁中人名／組織（須仰賴中研院 CKIP 中文 NER + 台灣正則）。
  - 既有 **Classic Hooks** 的 `PreToolUse` 跑在 `Edit` 工具比對 `old_string` **之後**，導致模型拿著佔位符（如 `<TW_MOBILE_1>`）編輯檔案必敗；改用 **Claude Mod 的 `tool.call`** 可在 `Edit` 驗證**之前**將佔位符換回真值，徹底補上 `Edit` 缺口。
- **How（核心架構與關鍵防線）**：
  1. **雙向遮罩／還原與外洩出口封鎖**：
     - **往下（進工具前）**：`Write` / `Edit` / `MultiEdit` / `Bash` 自動將佔位符還原為真值寫回磁碟；`WebFetch` / `WebSearch` / `Agent` / `Task` / `Workflow` / `mcp__*` 與夾帶佔位符的連網指令直接拒絕（防範資料外傳）。
     - **往上（回模型前）**：`Read` / `Bash` / `Grep` / `mcp__*` 回傳給模型的結果即時去識別化；`prompt.submit` 直接改寫使用者輸入的個資為佔位符而不中斷對話；`session.compact` 壓縮前後皆重掃。
  2. **嚴格 Fail-Closed 實作（`register.ts`）**：因為 Claude Mods 引擎若在 10 秒內超時或拋錯會預設 Fail-Open（跳過 hook 直接放行），`pii-guard` 在所有 handler 強制掛 `.catch` 攔截錯誤並回傳拒絕／扣留訊息，確保 `hookd` 離線時不會靜默裸奔。
  3. **混合保留兩條 Classic Hook**：因目前 Mod API 尚無對應介面且無法生成常駐背景行程，仍保留 `MessageDisplay` 與 `SessionStart --start-only` 兩條 classic hook 負責啟動 `hookd`。
  4. **客戶名單零曝光匯入（`/pii-terms`）**：強制禁止模型 `Read` 或 `cat` 原始 Excel 名單，僅以無值欄位摘要透過互動選單匯入種子詞庫。

---

## 2. 啟發與適用性評估（含跨平台與繞過邊界審視）

- **極高參考價值的工程實踐**：
  1. **Claude Mods 的「Fail-Open → Fail-Closed」與「`ref` 陷阱」實戰筆記**：`examples/claude-code-mod/README.md` 與 `register.ts` 直接揭露了 Claude Mods 的兩個關鍵坑（回傳不可帶原 `ref`、必須自行 `.catch` 否則超時即裸奔），可直接作為本機日後開發任何安全類 Mod 的規範範本。
  2. **台灣個資專精能力**：若未來承接台灣顧問／法律／醫療／電商客戶案件（需處理真實合約、判決書、報表、客戶清單），`pii-guard` 的「台灣正則 + CKIP NER + 本機瀏覽器人工補標介面」是目前繁中圈最成熟的本地方案。
- **實查發現的限制與 Windows 11 適配注意**：
  1. **Windows 11 原生路徑變數**：`register.ts` 預設讀取 `HOME` 環境變數（`~/.local/share/pii-guard/hookd`）；在 Windows 11 原生環境（未設 `HOME` 時），必須設定 `PII_GUARD_HOOKD_HOME` 才能正確定位 `state.env`。
  2. **機率性偵測與非個資機密邊界**：正則＋NER 專注於「可指認個人之資訊（PII）」，並不保證自動攔截專案自訂 API Token、商業機密數字（金額／合約條款刻意保留）或圖片／截圖內的文字；不能單靠它宣稱「100% 絕對不洩密」，仍須搭配人工補標 UI 或客戶名單 `/pii-terms`。
  3. **與既有 Hook／Relay 相容性**：若在本機啟用，須確認 `examples/claude-code-mod` 的 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` 與現有 `harness-guard`、`agent-relay`、`inbox-band` Mod 之插件載入不衝突。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-17`**｜**[優先級：中]** 在 Windows 11 原生環境沙盒實測 `danyuchn/pii-guard`（CLI 去識別化與 `claude-code-mod` 搭配 `PII_GUARD_HOOKD_HOME` 驗證）
  - **目標範圍**：`C:\GitHub\_sandbox\pii-guard`（唯讀／測試）與本機 Claude Code 外掛測試環境
  - **具體做法**：
    1. 以 `uv` 在隔離環境安裝 `danyuchn/pii-guard`（不預設安裝常駐全系統 hook），實測台灣個資樣本（姓名、身分證、統編、手機、地址）之 `anonymize` / `restore` 與 `pytest`（確認 Windows 相容性）。
    2. 檢查 `examples/claude-code-mod/hooks/register.ts` 在 Windows 11 原生下透過 `PII_GUARD_HOOKD_HOME` 連線 `hookd` 的可行性，並評估是否收錄為顧問接案專用按需啟用套件（平時預設關閉，處理客戶敏感文件專案時單獨掛載）。
  - **驗收標準（DoD）**：產出 Windows 11 實測結果（CLI 遮罩／還原與 `pytest` 輸出，以及 Mod 與現有 `harness-guard` 相容性結論），記錄於筆記或 `docs/`。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
