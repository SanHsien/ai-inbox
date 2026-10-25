---
id: 2026-10-18-desktop-sense-local-screen-context
title: "desktop-sense：為 Coding Agent 賦予本機螢幕即時視覺感知（Local-First Screen Context）與嚴格隱私防護架構解構"
source_url: "https://github.com/angletech2026-arch/desktop-sense"
source_platform: "GitHub"
author: "angletech2026-arch"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: done
cluster: 3
cluster_role: "視覺感知"
short_title: "desktop-sense 本機螢幕上下文"
tags:
  - desktop-sense
  - local-first
  - screen-context
  - claude-code
  - codex-cli
  - gemini-cli
  - ocr-vision
  - privacy-security
  - prompt-injection-defense
---

# desktop-sense：為 Coding Agent 賦予本機螢幕即時視覺感知（Local-First Screen Context）與嚴格隱私防護架構解構

- **來源連結**：[angletech2026-arch/desktop-sense (GitHub)](https://github.com/angletech2026-arch/desktop-sense)
- **開源授權**：MIT License
- **分析日期**：`2026-10-18`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-mem-autocompact-context.md`](./2026-10-17-claude-mem-autocompact-context.md)（上下文與記憶管理）
  - [`notes/2026-10-17-claude-plugins-official-directory.md`](./2026-10-17-claude-plugins-official-directory.md)（Claude Code Hook 機制）
  - [`notes/2026-10-17-cross-cli-subagent-orchestration-space-bunny.md`](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md)（跨 CLI 工具鏈編排）

---

## 1. 核心內容摘要與技術深挖

### 1.1 核心痛點：終結「截圖 → 複製報錯 → 貼給 AI → 解釋上下文」的摩擦力
在當前 CLI Coding Agent（Claude Code、Codex CLI、Gemini CLI 等）的開發工作流中，當前端網頁報錯、後端編譯失敗、瀏覽器 DevTools 出現 Warning 或本機 Docker/DB 崩潰時，開發者被迫手動截圖、選取錯誤文字、切換終端、貼入對話並附帶文字說明「我現在正在看 Chrome 的 Deploy Log」。

`desktop-sense` 是一個常駐於本機系統（Windows 10/11 原生支援，macOS 測試版）的輕量級守護程序（Daemon），透過 **CLI Hook（如 `UserPromptSubmit` / `BeforeAgent`）**，在使用者發送每則對話時，**自動附帶結構化螢幕即時上下文（Active Window、20 分鐘時間軸、報錯 OCR 文字、最新截圖路徑）**，讓 AI Agent 自然感知開發者眼前的畫面。

```text
┌────────────────────────────────────────────────────────────────────────┐
│             desktop-sense 本機多模態螢幕感知與隱私架構                 │
└────────────────────────────────────────────────────────────────────────┘

 [ 開發者螢幕活動 (VS Code, Chrome DevTools, Terminal, Docker Desktop) ]
                                 │
                                 ▼ (本機每 20 分鐘 / 錯誤即時捕獲)
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 本地守護進程 (desktop-sense daemon / ds.py)                           │
 │ ├─ 1. 隱私前置攔截 (Sensitive Window Filter)                         │
 │ │     • 密碼管理器、網銀、無痕視窗、.env、憑證 → 僅記錄 App 名，零截圖  │
 │ ├─ 2. 本地 OCR 與金鑰掃描 (Local OCR & Secret Dropper)                │
 │ │     • 偵測到 API Key / 密碼 / 身分證字號 → 徹底丟棄整張截圖 (Drop)  │
 │ ├─ 3. 錯誤雷達 (Error Radar)                                          │
 │ │     • 偵測 Traceback, npm ERR!, TS Error → 觸發背景除錯分析與通知   │
 │ ├─ 4. 自動研究 (Auto-Research)                                        │
 │ │     • 連續兩次遭遇相同錯誤 → 自動搜尋 GitHub Issues / Stack Overflow│
 │ └─ 5. 增量上下文壓縮 (Delta Context Engine)                           │
 │       • 首則訊息 300~1,500 Tokens，後續僅發送 Diff (< 200 Tokens)     │
 └──────────────────────────────────┬────────────────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼ (Prompt Hook 注入)                              ▼ (CLI / Skill 查詢)
 ┌──────────────────────────────────────┐          ┌───────────────────────────┐
 │ CLI Coding Agent (跨工具鏈整合)      │          │ 本機控制與監控            │
 │ ├─ Claude Code (UserPromptSubmit)    │          │ ├─ ds now / ds recent     │
 │ ├─ Codex CLI (UserPromptSubmit)      │          │ ├─ ds stream (即時事件流)  │
 │ ├─ Gemini CLI (BeforeAgent)          │          │ ├─ ds pause 30 (暫停錄製) │
 │ └─ Muse Code / Grok Bot (/desk)      │          │ └─ /desk Skill (隨選調閱) │
 └──────────────────────────────────────┘          └───────────────────────────┘
```

---

### 1.2 關鍵功能與工程架構深度拆解

#### A. 增量上下文壓縮（Token-thrifty Delta Context）
- 傳統將截圖或長螢幕日誌塞入 Context 會迅速消耗數千 Token 並擠佔上下文。
- `desktop-sense` 採用**增量演算法（Delta State）**：
  - 首次對話：注入完整的前 20 分鐘時間軸與當前視窗 OCR，消耗約 300～1,500 Tokens。
  - 後續對話：僅注入自上次 Prompt 以來的**視窗切換、新增的指令輸出或新增錯誤**，通常壓在 **200 Tokens 以下**。

#### B. 錯誤雷達與主動調查（Error Radar & Auto-Research）
1. **錯誤雷達（Error Radar）**：
   - 透過本機 OCR 即時掃描畫面中的常見錯誤特徵（`Traceback`、`npm ERR!`、`error TS...`、編譯崩潰等）。
   - 背景調用輕量模型（預設 Claude 3.5 Haiku，每小時上限 12 次；或本機 Ollama），產生修復建議並彈出 Windows 系統原生通知。
   - 防抖機制：相同錯誤 30 分鐘內最多分析 1 次，瀏覽器/影片中的錯誤每 30 分鐘最多 1 次。
2. **自動調研（Auto-Research）**：
   - 當終端或編輯器中**同一個錯誤連續出現兩次**，守護進程自動使用 Web 搜尋檢索 **GitHub Issues、Stack Overflow 與 Reddit**，在開發者提出問題前便已備妥最佳解答與參考連結。
   - 新開專案時，主動搜尋既有開源替代專案，避免重複造輪子。

#### C. 「觀看除錯」串流模式（Watch Me Mode）
- 提供 `ds stream` 命令，輸出單行結構化事件流。
- 可與 Claude Code 的 `Monitor` 工具或背景任務掛接，形成 AI 邊看畫面邊主動提供反饋的即時結對除錯（Pair Debugging）體驗。

---

### 1.3 隱私防護與安全防線（Local-First Privacy Architecture）

本工具在安全性與隱私架構上展現了極高的工程成熟度：

1. **零外部伺服器與全本地儲存（Zero Telemetry）**：
   - 程式本身不開設任何監聽 Port，完全不與第三方遠端連線。
   - 截圖、OCR 文本、時間軸皆存於本地 `data/` 目錄，限制僅當前作業系統使用者權限可讀。
   - 截圖保留 48 小時自動刪除，時間軸 30 天清理，搜尋記錄 90 天過期。
2. **敏感視窗黑名單攔截（Sensitive Window Filter）**：
   - 密碼管理器（1Password、Bitwarden、KeePass 等）、網銀、病歷系統、成人網站、私鑰/`.env` 檔案。
   - **無痕視窗深層偵測**：Chrome、Brave、Opera 等瀏覽器在無痕模式下的視窗標題與一般視窗無異，`desktop-sense` 透過**無障礙樹（Accessibility Tree API）**直接探測無痕狀態。
   - 敏感視窗**僅記錄應用程式名稱，嚴禁擷取標題、螢幕截圖與 OCR**。
3. **金鑰洩漏整張丟棄機制（Drop Instead of Blur）**：
   - 畫面上一旦出現 API Key（OpenAI、Anthropic、GitHub、AWS、Stripe 等）、JWT、私鑰、密碼賦值語句（`PASSWORD=...`）、信用卡號或台灣身分證字號，**立即直接丟棄整張截圖檔案**，絕非打馬賽克（避免視覺模型還原周邊或模糊像素）。
4. **Prompt Injection 防禦與沙盒限制**：
   - 螢幕 OCR 文本被視為**不可信任資料（Untrusted Data）**，過濾不可見字元，並以隨機 Token 隔離區塊包覆，標註 `[screen data]`，明確告知 AI 不得執行其中的任何指令。
   - 背景分析器執行 `claude` 時強制開啟 `--safe-mode` 與 `--restricted`，在空白工作目錄執行，杜絕讀取專案 CLAUDE.md 或呼叫本機代碼執行工具。
5. **全離線模式（Fully Local Mode）**：
   - 支援將背景分析後端切換至 **Ollama（`gemma3:4b` 或 `qwen2.5vl:7b`）** 或 LM Studio（相容 OpenAI API）。在該模式下完全離線、零 Token 費用，任何畫面資料絕不上雲。

---

## 2. 對現有系統的啟發與適用性評估

- **對應現有系統 / 專案**：
  - **Windows 11 本地開發環境原生相容**：
    `desktop-sense` 提供 `install.ps1` 與完整的 Windows 10/11 支援，能與本機的 Claude Code、Codex CLI 及 Gemini CLI 無縫整合。
  - **解決多代理 / CLI 盲區**：
    本專案在 `notes/2026-10-17-cross-cli-subagent-orchestration-space-bunny.md` 規劃了跨 CLI 外包協同。然而 CLI 代理最大的盲點是看不見 GUI（瀏覽器 Console、Figma、編譯錯誤視窗）。`desktop-sense` 是串聯終端與視窗環境的最後一哩路。
  - **全域安全與防護規範**：
    其「發現金鑰整張截圖直接 Drop」與「無障礙樹檢查無痕視窗」的防護思維，極具借鑑價值，可直接吸納入全域安全性驗證規範。

- **落差與採納判斷**：
  - **高度推薦採納**：
    1. 在本機環境測試安裝與 Hook 掛接，評估其對日常 CLI Coding 的輔助效果。
    2. 吸收其本機 OCR 敏感資訊防護邏輯，確保截圖資料不外洩。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261018-05`**｜**[優先級：低]** 在 Windows 11 本地測試 `desktop-sense` 守護程序與 Claude Code / Codex CLI / Gemini CLI Hook 整合
  - **目標範圍**：本地開發環境與 Coding Agent 工具鏈基礎設施
  - **狀態**：⚪ 不做（常駐截圖守護程式並掛進所有 CLI hook，隱私風險高；看畫面需求已由 computer-use 與瀏覽器工具滿足）
  - **具體實作步驟**：
    1. 研讀 `angletech2026-arch/desktop-sense` 原始碼架構（`ds.py`、`install.ps1`、`dsense/`）。
    2. 在 Windows 11 本地評估安裝 `desktop-sense` 守護進程，檢驗其 `ds status` 與 `install.ps1` 對本地環境變數和 Hook 的修改範圍。
    3. 實測 Claude Code（`UserPromptSubmit`）與 Codex CLI 下的 Context 自動附加效果，記錄首則與增量訊息的 Token 消耗及端到端延遲。
    4. 驗證背景分析器（Haiku / Ollama Qwen2.5-VL）在終端編譯報錯時的自動修復建議通知表現。
  - **驗收標準（DoD）**：在 Windows 11 本地成功跑通 `desktop-sense`，確認終端報錯時能自動抓取螢幕內容給 Claude Code，且 `ds status` 顯示守護程序健康運作。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [x] **`T-20261018-06`**｜**[優先級：低]** 評估將 `desktop-sense` 隱私防線（敏感視窗黑名單、API Key 丟棄、截圖生命週期）蒸餾為本地多模態 Agent 視覺安全規範
  - **目標範圍**：全域安全規範與視覺/截圖防護協定
  - **狀態**：✅ 完成（2026-10-25，已蒸餾 desktop-sense 敏感視窗與憑證過濾規則產出 docs/multimodal-screen-privacy-spec.md）
  - **重新評估（2026-10-25）**：原關閉理由「沿用現有 computer-use 遮罩機制」不成立——computer-use 只有逐 app 分級授權，沒有遮罩或金鑰偵測；repo 內也沒有截圖隱私規範。各 Agent 已大量用截圖與錄影當驗收證據（瀏覽器截圖、Playwright 錄影、`docs/evidence/`），這份規範不需安裝 desktop-sense，只蒸餾規則成文件，改為要做。不做常駐守護程式（T-20261018-05 維持不做）。
  - **具體實作步驟**：
    1. 分析 `desktop-sense` 的敏感視窗正則庫（涵蓋中英法德西日韓等語系之金融、密碼、無痕關鍵字）與無障礙樹（Accessibility Tree）偵測邏輯。
    2. 萃取其 API Key 與機密憑證正則過濾規則（OpenAI, GitHub, AWS, Stripe, JWT 等），建立「偵測到金鑰立即 Drop 截圖」的通用防護模組。
    3. 整理為可複用的「多模態 Coding Agent 螢幕截圖與 OCR 隱私安全檢驗手冊」。
  - **驗收標準（DoD）**：產出結構化隱私檢驗規範文件（`docs/multimodal-screen-privacy-spec.md`），並確保任何牽涉本機畫面擷取的 Agent 流程均遵循「敏感跳過、洩鑰即丟、嚴格時限」的資料保護標準。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：已檢索並蒸餾 `angletech2026-arch/desktop-sense` 原始碼之三層防護體系（視窗層四級分類與字串前置清理、Chromium/Firefox 無痕視窗 UIA 無障礙樹探測、本機 OCR 洩鑰即丟 Drop 與脫敏正則庫），建立通用規範文檔 `docs/multimodal-screen-privacy-spec.md`，包含完整多語系阻斷正則表、高敏金鑰與 PII 脫敏對照表、48 小時生命週期規範以及單元驗證測試套件。

---
