---
id: 2026-11-02-littlehole-claude-saver-long-chat-session-handoff
title: "我的小樹洞 claude-saver 開源架構解構：UserPromptSubmit Hook 實時感知長對話 Token 門檻、新功能自動跳轉與一鍵交接封存"
source_url: "https://www.threads.com/@my.little.hole/post/DfKaSZSGatE"
source_platform: "Threads (@my.little.hole)"
author: "我的小樹洞 (@my.little.hole / littlehole2025)"
analyzed_at: 2026-11-02
analyzed_by: "Antigravity"
status: done
cluster: 1
cluster_role: "長對話自動交接與Token節流外掛"
short_title: "claude-saver長對話自動交接外掛"
tags:
  - claude-code
  - claude-saver
  - token-saver
  - token-optimization
  - user-prompt-submit-hook
  - session-handoff
  - archive-session
  - context-management
---

# 我的小樹洞 claude-saver 開源架構解構：UserPromptSubmit Hook 實時感知長對話 Token 門檻、新功能自動跳轉與一鍵交接封存

- **來源連結**：[Threads 原文貼文 (@my.little.hole)](https://www.threads.com/@my.little.hole/post/DfKaSZSGatE) ｜ [短網址](https://www.threads.com/share/GZvFE_6Oq/)
- **核心作者**：我的小樹洞（@my.little.hole / GitHub: littlehole2025）
- **官方開源專案**：[littlehole2025/claude-saver](https://github.com/littlehole2025/claude-saver)（原名 `token-saver`，Claude Code 官方 Plugin 體系）
- **分析主題**：解構開發者「我的小樹洞」開源之 Claude Code 節費與會話管理外掛 `claude-saver`。剖析其如何透過 `UserPromptSubmit` Hook 實時監聽 `transcript` 的 Token 消耗量（以 150k Tokens 為基礎門檻、每 50k 為階段步進），結合語意意圖判定（新功能 vs 做到一半的接續工作），在長對話下自動跳出「開新對話」原生按鈕；並深入解構單字指令「換」背後的標準化交接三步曲（流水號自動 +1、結構化 Brief 提取、舊會話安全封存），為多 Agent 長期執行環境提供低摩擦、防上下文發散與大幅節省 Token 的生產級範本。
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](./2026-10-17-claude-code-idle-compaction-cc-session-reader.md)（Claude Code 閒置壓縮與 cc-session-reader 歷史會話提取）
  - [`notes/2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md`](./2026-10-31-microsoft-tokeneconomizer-experience-driven-cost-control.md)（經驗驅動成本控制與動態上下文壓縮）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（四 Agent 派工與五路工具流整合）
  - [`notes/2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md`](./2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md)（跨會話工單交接與狀態封存協定）

---

## 1. 來源摘要與背景脈絡

### 1.1 長對話（Long Chat）的隱形吞金獸與性能衰減
在 Coding Agent（如 Claude Code / Antigravity）的日常開發中，使用者習慣在同一個會話內不斷疊加需求。然而長對話面臨三大核心問題：
1. **Token 呈階乘級累積燃燒**：即使具備 Prompt Caching 機制，每次送出哪怕只有一句話，模型都必須將前面 150k～200k 的完整歷史整段重新加載與處理，費用與耗能隨輪數飆升。
2. **推論延遲與注意力發散（Lost in the Middle）**：上下文過長時，大模型容易遺忘早期關鍵規則、混淆不同階段的架構約定，甚至進入幻覺或回答速度極度遲緩。
3. **手動更換會話的高摩擦力（Friction）**：使用者知道該換對話，但手動更換需繁瑣地手動複製上下文、整理進度、手動開新會話與手動關閉舊視窗，導致使用者寧願冒著燒 token 的風險硬撐。

### 1.2 `claude-saver` 的核心破局點：Hook 哨兵 + 意圖感知 + 一鍵無痛交接
作者「我的小樹洞」打造了極簡卻高精準的 Claude Code 外掛 `claude-saver`，安裝指令極簡：
```text
/plugin marketplace add littlehole2025/claude-saver
/plugin install claude-saver@claude-saver
```
其運作哲學在於：**不要讓使用者記掛 Token 數字，而是由外掛在背景監聽，在適當的語意邊界提供無痛跳轉按鈕**。

---

## 2. 架構核心解構與技術深度

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                 使用者提交 Prompt (例如：「換」)             │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         UserPromptSubmit 事件觸發
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             hooks/long-chat-reminder.js (Node.js)           │
       │   1. 讀取 transcript 最後 2MB 內容反向搜尋 "usage"           │
       │   2. 計算 input_tokens + cache_tokens >= 150k               │
       │   3. 檢查系統暫存，每隔 50k 提示一次使用者                  │
       │   4. 動態注入系統提示：指示 Claude 進行新功能/話題語意邊界判定│
       └──────────────────────────────┬──────────────────────────────┘
                                      │
             ┌────────────────────────┴────────────────────────┐
             ▼ (接續做到一半的事/追問)                          ▼ (偵測為新功能或收到「換」)
 ┌───────────────────────────────┐             ┌───────────────────────────────┐
 │       照常執行目前任務         │             │   啟動 skills/handoff 流程    │
 │       不打擾、不彈提示         │             └───────────────┬───────────────┘
 └───────────────────────────────┘                             │
                                                               ▼
                                               ┌───────────────────────────────┐
                                               │ 1. get_session("self")        │ -> 取得當前會話名稱
                                               │ 2. 名稱流水號 +1 (「專案-3」→「專案-4」)│
                                               │ 3. start_session(context:fresh│ -> 開立新會話帶入 Brief
                                               │ 4. archive_session("self")    │ -> 舊會話安全封存
                                               └───────────────────────────────┘
```

### 2.1 UserPromptSubmit Hook：輕量高效的上下文哨兵
外掛在 `hooks/hooks.json` 中掛載 `UserPromptSubmit` 事件，執行 `hooks/long-chat-reminder.js`：
1. **反向局部讀取優化**：為避免長對話 transcript 檔案過大造成 I/O 阻塞，腳本僅截取檔案末端最多 2MB（`Math.min(size, 2_000_000)`），反向解析最新一筆包含 `"usage"` 的助手回覆。
2. **總輸入 Token 實時核算**：
   $$\text{Tokens} = \text{input\_tokens} + \text{cache\_read\_input\_tokens} + \text{cache\_creation\_input\_tokens}$$
3. **階梯式靜默保護（Suppression Window）**：
   - 預設起始門檻 `LONG_CHAT_TOKENS = 150000`。
   - 提示步進 `LONG_CHAT_STEP = 50000`。
   - 使用者看得到的提示只在初次越過 150k、以及其後每多 50k 時在終端顯示一次（記錄於 `%TEMP%` 或 `/tmp` 下狀態檔），避免每輪刷屏引發反感。

### 2.2 語意邊界判定（Semantic Task Boundary）
長對話最大的挑戰在於：若每輪都逼使用者開新對話，會打斷正在修 bug 或寫到一半的思路。`claude-saver` 透過 Hook 注入微提示，賦予 Claude 語意辨識能力：
- **放行情境（Continue In-Place）**：接續目前做到一半的事、修正剛寫好的代碼、追問細節。此時 Claude 絕不跳出開新對話按鈕，亦不在輪末嘮叨。
- **切換情境（Offer New Conversation）**：使用者提出了全新的獨立功能、全新模組、或切換了討論話題。此時 Claude 在當前輪次優先調用 `start_session(initiation: "offer", context: "fresh")`，在 UI 上直接跳出原生「開新對話／在這裡做」按鈕，brief 載入新需求與交接要點，交由使用者自主決定。

### 2.3 一鍵交接三步曲（`handoff` Skill）
當使用者手動輸入單字「**換**」、「**開新**」、或英文 `new` / `handoff`，或按下 UI 的「開新對話」按鈕時，觸發標準化會話交接鏈路：
1. **標題流水號自動遞增**：透過 `get_session(session: "self")` 查詢當前名稱，使用正規表達式抓取尾部數字自動加 1（例如「對話-3」→「對話-4」、「網站」→「網站-2」），免除命名心智負擔。
2. **結構化交接 Brief 提取**：新會話的 `brief` 強制具備獨立可讀性（禁止出現「如上所述」），涵蓋：
   - **已完成事項**（Commit SHA、PR、修改檔案清單）。
   - **未完成卡點**與阻礙。
   - **後續待辦事項（Action Items）**。
   - **需繼承之約束**（語言偏好、環境設定、專案硬閘門）。
3. **雙向狀態安全保證**：透過 `start_session` 的返回值確認新對話已確實啟動後，才調用 `archive_session(session: "self")` 封存當前對話。若新會話建立失敗，則嚴禁封存，確保工作上下文不丟失。
4. **終端機 CLI 降級保護**：若當前環境無 GUI 桌面工具（如純終端 CLI），自動降級為輸出精簡版交接文本，並引導使用者手動新建對話貼入。

---

## 3. 對現有系統的啟發與落差分析

| 評估維度 | `claude-saver` 實踐特徵 | 本知識庫與現有 Agent 體系現狀 | 落地借鑑與改進方向 |
| :--- | :--- | :--- | :--- |
| **會話膨脹監控** | Hook 實時讀取 transcript usage，階梯式提醒（150k + 50k step） | 目前多依賴手動感知，或依賴平台溢出前之自動壓縮（無法主動控制切換時機） | 引入 `UserPromptSubmit` Token 哨兵機制，實施會話健康度階梯告警 |
| **話題切換摩擦力** | 單字「換」觸發自動遞增流水號（-1 → -2）與結構化 Brief 傳遞 | 換會話需人工開新對話、手動複製貼上背景，或跨 session 讀檔 | 整合 Antigravity / Claude 原生 Session API，實現單字無痛交接閉環 |
| **舊會話生命週期** | 驗證新對話建立後，自動調用 `archive_session` 封存舊會話 | 舊會話多長久閒置殘留於左側欄，需定期手動手動整理或膨脹 | 實作「交接成功即自動封存（Auto-Archive）」機制，維持工作區極度整潔 |
| **語意切分智慧度** | 區分「做到一半的事（繼續）」與「新功能（推薦新對話）」 | 常見規則常採固定輪數暴力切斷，容易打斷連續除錯流程 | 引入「語意任務邊界判定準則」，不打斷連續工作流 |

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將 `claude-saver` 的長會話上下文感知、單字快速交接與會話生命週期管理納入工程落地，規劃以下 3 項任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261102-01`**｜**[優先級：高]** 撰寫「長會話上下文膨脹告警與一鍵自動交接規格手冊（UserPromptSubmit Hook 與 Session 生命週期控制）」收錄於 `docs/long-chat-session-handoff-spec.md`
  - **目標範圍**：`docs/long-chat-session-handoff-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 深入剖析長會話之 Token 遞增成本模型與「注意力發散」臨界點（150k Tokens 門檻依據與 50k 階梯步進演算法）。
    2. 規範 `UserPromptSubmit` Hook 的安全讀取機制（限制讀取末端 2MB、反向解析 usage、狀態暫存隔離）。
    3. 制定跨平台（Claude Desktop `start_session`/`archive_session` vs Antigravity `agentapi new-conversation`/`UpdateConversationAnnotations`）的統一會話生命週期控制介面與降級策略。
  - **驗收標準（DoD）**：產出 `docs/long-chat-session-handoff-spec.md`，具備標準 Markdown 結構與繁體中文規範；以 `Test-Path docs/long-chat-session-handoff-spec.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：docs/long-chat-session-handoff-spec.md：對照 littlehole2025/claude-saver @ 434750e（v1.2.0）與 code.claude.com hooks 官方頁；更正筆記把 token 成長寫成階乘級（實為平方級），分開每輪注入與給人看的提示；start_session 等工具名稱在官方文件查無，標未驗證。獨立審查逐項核對相符。

- [x] **`T-20261102-02`**｜**[優先級：中]** 實作「會話 Token 上下文感知度量與語意換話題判定驗證腳本」於 `tools/verify_session_token_sentinel.py` 與單元測試
  - **目標範圍**：`tools/verify_session_token_sentinel.py`、`tests/test_verify_session_token_sentinel.py`
  - **具體做法**：
    1. 實作純 Python 版本的 Token 哨兵驗證工具 `tools/verify_session_token_sentinel.py`，支援解析模擬 transcript JSONL 末端之 usage 數據。
    2. 實作狀態機邏輯：驗證當 Token < 150k 時靜默、越過 150k 觸發初次提示、未滿 50k 間隔時壓制提醒、越過 200k/250k 再次觸發之階梯行為。
    3. 實作任務連續性 vs 新功能語意啟發式規則判定（延續詞「繼續、修正、剛剛」vs 新話題詞「新增、換一個、另外想要」）。
    4. 撰寫單元測試套件 `tests/test_verify_session_token_sentinel.py`，覆蓋大檔案尾部讀取、損毀 JSON 容錯、階梯計算與提示抑制邏輯。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_session_token_sentinel.py` 綠燈通過。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：tools/verify_session_token_sentinel.py＋tests：只用 transcript 的 usage 計 token，量不到不通過（含 usage 為空物件）；hook 在任何參數或輸入錯誤下都回 1、從不回 2（避免擋掉使用者提問）。審查抓到參數錯誤回 2，已修正並由整合者實跑確認。

- [x] **`T-20261102-03`**｜**[優先級：低]** 產出標準化「跨 Agent 桌面會話編號流水遞增與結構化交接 Brief Prompt 模板」收錄於 `templates/session-handoff-brief-prompt.md`
  - **目標範圍**：`templates/session-handoff-brief-prompt.md`
  - **具體做法**：
    1. 產出適用於 Claude Code、Antigravity、Codex 的單字「換」觸發交接 Prompt 模板。
    2. 制定會話標題命名規則（自動提取結尾數字遞增，如「專案-1」→「專案-2」）。
    3. 規範四段式結構化 Brief 提取格式（已完工項目與 SHA、未完工卡點、下一步待辦清單、環境偏好與全域約束），確保新會話無縫接軌且舊會話可安全封存。
  - **驗收標準（DoD）**：產出 `templates/session-handoff-brief-prompt.md`，結構清晰且包含變數替換標記；以 `Test-Path templates/session-handoff-brief-prompt.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：templates/session-handoff-brief-prompt.md：共用提示核心加 Claude Code／Antigravity／Codex 附加段、命名規則（5 個範例由測試驗證）、四段式交接格式與檢查清單；各環境工具名稱已驗證與未驗證分開列。
