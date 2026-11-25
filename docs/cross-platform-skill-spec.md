# SKILL.md 跨平台相容性檢查清單與提示詞定錨規範

> 本文件收錄於 `docs/cross-platform-skill-spec.md`，為任務 `T-20261122-01` 之產出成果。
> 核心目的：整理 Google Gemini Skills、Anthropic Claude、OpenAI ChatGPT / Codex 與 Google Antigravity 對 `SKILL.md`（Agent Skills 標準）的檔案上傳、腳本執行、網路存取與環境相容性限制；並針對「技能已掛載但跳過流程第一步」的現象，提供可重現的對照測試設計與明確標記為「待測」的提示詞定錨寫法。

---

## 0. 來源筆記與官方依據

- **來源筆記**：`notes/2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval.md`
- **來源與延伸範圍（2026-11-25 更正）**：[數位時代原文](https://www.bnext.com.tw/article/93097/gemini-skills-setup-guide)只列 Gemini、Claude、ChatGPT；本文件加入 Antigravity 與 Codex 是本 repo 自行延伸的評估範圍，不代表原文背書或已實測相容。
- **交叉參照**：
  - [`notes/2026-10-19-android-official-skills-google-coding-agent.md`](../notes/2026-10-19-android-official-skills-google-coding-agent.md)（Google 官方 Agent Skills 目錄架構）
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](../notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Antigravity 全域與專案技能治理）
- **官方文件查證網址**：
  - [Google Gemini 技能建立與使用官方說明](https://support.google.com/gemini/answer/17094296?hl=en)
  - [Google Gemini Gems 轉移 Skills 官方指南](https://support.google.com/gemini/answer/18977944?hl=en)
  - [Google Gemini 技能運作機制與限制說明](https://support.google.com/gemini/answer/17102773)
  - [Agent Skills 開放規格 (`agentskills.io`)](https://agentskills.io/specification)

---

## 1. Gemini Skills 上傳與執行硬限制（附官方依據）

Google 自 2026 年 11 月起將個人帳號的「Gems」逐步轉移為「技能（Skills）」，年滿 18 歲之個人免費帳號即可在電腦版 Gemini「自訂 → 技能」中建立或上傳含 `SKILL.md` 的單檔或 ZIP 壓縮包。然而，格式通用不等於執行環境通用，依 [Google 官方說明](https://support.google.com/gemini/answer/17102773) 與 [使用指南](https://support.google.com/gemini/answer/17094296?hl=en)，Gemini 網頁／App 端的技能具有以下嚴格限制：

| 限制維度 | Gemini Skills 官方規範與限制內容 | 跨平台遷移影響與處置 |
| :--- | :--- | :--- |
| **呼叫快捷鍵** | 輸入框打 `/` 選取自建技能（已更新快捷鍵之帳號改打 `@`）；分享取得的技能固定用 `@` 選取 | 實際符號依帳號介面版本為準，撰寫團隊教學時應並列 `/` 與 `@` |
| **上傳容量上限** | 單一技能內所有檔案**合計不超過 100 MB** | 禁止在技能包夾帶大型二進位資產、模型權重或高畫質影片 |
| **允許／禁止的檔案格式** | 外層可上傳單一 `SKILL.md` 或技能 `.zip` 包；包內附隨檔案支援純文字與程式碼（如 `.md`、`.txt`、`.csv`、`.py` 等）以及 **PDF、DOCX、XLSX、PPTX 與 PNG、JPG 等多種圖片格式**；**明確排除** `.ts`、`.tsx`、`.sql`、舊版 Office（`.doc`、`.xls`、`.ppt`）、**包內夾帶的壓縮附件**、音訊與影片檔 | 若 Antigravity 或 Claude Code 技能內含 TypeScript (`.ts`/`.tsx`)、`.sql` 腳本或包內巢狀壓縮檔，直接上傳 Gemini 會被拒絕；須轉為受支援格式或於本地 Agent 執行 |
| **腳本網路與外部動作限制** | Gemini 技能內的腳本在受限沙盒執行，**不能連網、不能對外部網站發起請求或執行外部動作** | 凡依賴 `curl`、外部 REST API、Web Scraping 或資料庫連線的技能，在 Gemini 網頁端無法運作 |
| **`compatibility` 欄位宣告** | 依 [Agent Skills 開放規格](https://agentskills.io/specification)，YAML frontmatter 提供 `compatibility` 欄位標示環境需求 | 當技能需要特定 CLI 工具、系統套件、本機檔案系統讀寫或網路存取時，**必須在 `SKILL.md` frontmatter 明確填寫 `compatibility`** |

### 1.1 `SKILL.md` 跨平台 Frontmatter 標準寫法範例

```yaml
---
name: repo-contract-verifier
description: 執行本地儲存庫契約完整性驗證與靜態檢查。當使用者要求檢查筆記格式、驗證任務 DoD 或執行收尾檢查時觸發。
compatibility: "Requires local Python 3.11+ runtime and filesystem read/write access (Antigravity / Claude Code / Codex CLI). Not compatible with web-only sandboxed environments without local repo access."
---
```

---

## 2. 跨平台（Gemini / Claude / Antigravity / Codex）相容性檢查清單

將同一份 `SKILL.md` 部署至不同平台前，必須逐項核對下表：

| 檢查項目 | Google Gemini (Web / App Skills) | Anthropic Claude (Web Projects / Skills) | Google Antigravity / Claude Code / Codex CLI (本機 Agent) | 相容性設計建議 |
| :--- | :--- | :--- | :--- | :--- |
| **1. 核心指令檔** | `SKILL.md`（支援單檔或 ZIP 上傳） | `SKILL.md` 或 Project Instructions | `<skills_dir>/<skill_name>/SKILL.md` | 統一以標準 YAML frontmatter (`name`, `description`, `compatibility`) 撰寫 |
| **2. 觸發與載入機制** | 依名稱與描述自動判斷相關性，或手動打 `/`、`@` 點名載入 | 依 `description` 語意匹配或專案固定掛載 | 系統提示詞列出 `name` 與 `description`，模型判定相關後呼叫 `read_file` 讀取 `SKILL.md` | `description` 必須包含明確的觸發詞（Triggers）與不適用邊界（Do not use for...） |
| **3. 附隨檔案型別** | 外層支援 `SKILL.md` 或 `.zip`；包內支援純文字／程式碼（`.md`, `.txt`, `.csv`, `.py` 等）、**PDF、DOCX、XLSX、PPTX 與 PNG/JPG 等圖片**（**禁 `.ts`, `.tsx`, `.sql`, 舊版 Office, 包內壓縮附件, 影音**），總計 $\le$ 100 MB | 支援常見文字、PDF 與文件檔，受 Project 容量上限約束 | 本機檔案系統無副檔名限制，可直接放置 `scripts/`、`examples/`、`resources/` | 需跨 Web 端共用的技能，避免放入 `.ts`/`.tsx`/`.sql` 與包內壓縮檔，改用 `.md`、`.txt`、`.py`、`.pdf` 或 `.docx` |
| **4. 腳本網路存取** | **禁止連網**、禁止對外部網站動作 | Web Analysis 沙盒禁止任意外連 | 預設沙盒隔離網路，必要時可經使用者審批（`BypassSandbox`）或透過 MCP 呼叫外部服務 | 涉及外部 API 的技能應拆分為「純邏輯 Prompt 層」與「本機 CLI / MCP 執行層」 |
| **5. 本機系統與終端工具** | 無本機 Shell 與檔案系統存取權 | Web 端無本機存取權（Desktop 需透過本地 MCP） | 完整支援 PowerShell / Bash、Git、本地測試框架與子代理派工 | 僅限本機執行的技能務必於 `compatibility` 註明 `Local CLI / IDE Agent only` |

---

## 3. 提示詞定錨寫法（待測技巧）與對照測試設計

### 3.1 問題背景與證據等級標記

- **現象描述（二手轉述，出自《數位時代》作者單次實測，本 repo 未重測）**：依[同媒體刊載原文](https://1day1ai.bnextmedia.com.tw/articles/gemini-skills-setup-guide)，作者在單次實測中遇到 Gemini 畫面上方已顯示 `Skills: [技能名稱]`，模型第一次仍跳過 `SKILL.md` 定義的第一步（例如「深度提問設計師」應先反問並挖掘高維度問題，模型卻直接給出一般學習計畫）、第二次改寫提示詞後成功；原文僅記錄這一次跳步與一次改寫成功，未提供發生率數據，跳步原因亦未查證。
- **官方機制查證**：依 [Google 官方說明](https://support.google.com/gemini/answer/17102773)，Gemini 係根據技能的名稱與描述判斷與當前提示詞的相關性，判定相關時才讀取完整技能指示；**官方文件並未提及「注意力機制」或「句首點名會強制載入技能」**。
- **兩種候選寫法（目前狀態：【待測】）**：
  1. **寫法 A（句首寫出技能名稱）**：在提示詞開頭直接點名技能名稱（例如：`深度提問設計師，下週有一位新同事要加入...`）。合理推論是讓技能名稱出現在 Prompt 中以提高相關性匹配命中率，但屬推論、尚未經控制變數實測。
  2. **寫法 B（句末補上第一步強約束）**：在提示詞結尾明確點出技能流程的第一步要求（例如：`...請先依技能流程第一步，幫我找出一個更值得問的問題，不要直接給計畫。`）。

### 3.2 標準對照測試協議（A/B Testing Protocol）

在將上述兩種寫法升級為正式團隊規範前，須依下列四組對照設計完成實測（同一模型版本、同一 `SKILL.md`、同一任務情境，每組獨立開新對話跑 $N \ge 10$ 次）：

```text
[同一多步驟技能 (含明確 Step 1 前置停頓/反問要求) + 同一測試任務背景]
   ├── 對照組 C0 (Baseline) ：僅用 UI 選取 `/技能` 或 `@技能`，正文不提技能名、不重申第一步
   ├── 實驗組 T1 (句首點名) ：正文開頭寫「<技能名稱>，<任務背景>」
   ├── 實驗組 T2 (句末鎖首步)：正文結尾補「請先執行流程第一步：<Step 1 動作>，勿直接跳到後續步驟」
   └── 實驗組 T3 (首尾雙錨定)：句首點名技能名稱 + 句末重申第一步要求
```

| 評估指標 | 量測定義 | 判定通過門檻 |
| :--- | :--- | :--- |
| **技能載入命中率（Skill Activation Rate）** | 介面顯示 `Skills: [<技能名稱>]`（或 Agent 呼叫 `read_file` 讀取 `SKILL.md`）之回合比例 | 實驗組較 C0 顯著提升或達 100% |
| **首步遵循率（Step-1 Compliance Rate）** | 模型首輪回覆嚴格停留在 Step 1（如先提出深度反問或先輸出計畫等待確認），**未擅自跳步輸出最終產物**之比例 | $N \ge 10$ 次測試中，首步遵循率 $\ge 90\%$ |

> **現行規範結論**：在完成上述 $N \ge 10$ 對照實測前，「句首寫出技能名稱」與「句末補第一步要求」在文件與實務中均定位為**【待測可選技巧】**；若要在 `SKILL.md` 內部防範跳步，工程上更可靠的做法是在 `SKILL.md` 的 Step 1 明確寫入硬性停頓條件（例如：`STOP HERE: 在使用者回答上述問題前，禁止產生後續章節`）。
