---
id: 2026-10-17-claude-code-idle-compaction-cc-session-reader
title: "Claude Code 閒置壓縮（Idle Compaction）解析與 Prompt Cache 過期對策：以 cc-session-reader 實現對話無損繼承"
source_url: "https://x.com/lydiahallie/status/2110484840256819380"
source_platform: "X / Twitter & GitHub"
author: "Lydia Hallie (@lydiahallie) & SanHsien / Mapleeeeeeeeeee"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: in-progress
cluster: 1
cluster_role: "記憶繼承"
short_title: "Idle Compaction 與 cc-session-reader"
tags:
  - claude-code
  - prompt-caching
  - idle-compaction
  - cc-session-reader
  - context-optimization
  - session-resume
---

# Claude Code 閒置壓縮（Idle Compaction）解析與 Prompt Cache 過期對策：以 cc-session-reader 實現對話無損繼承

- **來源連結**：
  - [Lydia Hallie 推文發布 (X/Twitter)](https://x.com/lydiahallie/status/2110484840256819380)
  - [SanHsien/cc-session-reader (GitHub)](https://github.com/SanHsien/cc-session-reader)（Fork 自 [Mapleeeeeeeeeee/cc-session-reader](https://github.com/Mapleeeeeeeeeee/cc-session-reader)）
- **發表作者**：`Lydia Hallie (Anthropic Staff DX)` & `SanHsien / Mapleeeeeeeeeee`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：[`notes/2026-10-17-claude-mem-autocompact-context.md`](./2026-10-17-claude-mem-autocompact-context.md)

---

## 1. 核心內容摘要與技術深挖

### 1.1 背景：Prompt Cache TTL 與閒置壓縮機制（Idle Compaction）
Anthropic 官方為 Claude Code 引入了新的背景優化機制——**閒置壓縮（Idle Compaction）**：
- **Prompt Cache 壽命限制**：Anthropic 伺服器端的 Prompt Cache 有效時間（TTL）約為 5 分鐘至 1 小時。當使用者在長會話中暫時離開（如會議、用餐或跨日）超過 1 小時，服務端快取將徹底過期。
- **快取過期的成本衝擊**：若會話累積至 200k+ tokens，快取失效後使用者送出的下一條指令，必須重新支付高昂的「Cache Write / 全文重新計算」成本，且伴隨明顯的延遲（TTFT）。
- **官方應對策略**：Claude Code 在 Prompt Cache 即將過期前（約 1 小時），自動在後台觸發 Compact。當使用者返回時，模型只需重新處理壓縮後的「文字摘要（Summary）」，大幅壓低快取未命中成本。
- **配置參數**：
  - `settings.json`：可設定 `"idleCompaction": false` 選擇退出（opt-out）。
  - 環境變數：`CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`（自訂觸發閾值，預設為 `200k`）。

### 1.2 官方有損摘要 vs. cc-session-reader 對話無損繼承
雖然官方機制節省了快取重寫費用，但其致命缺點在於**「有損壓縮（Lossy Compaction）」**——模型從高度概括的摘要繼續，丟失了使用者原始提問的細緻語氣、中間探索的邊界因果與代碼微調假設。

使用者提出更優越的架構路徑：**「如果快取過期，參考 `cc-session-reader`，只保留使用者與模型的真實對話，繼承前一個對話而不是依賴粗暴摘要。」**

```text
┌────────────────────────────────────────────────────────────────────────┐
│      快取過期應對方案對比：官方有損摘要 vs. cc-session-reader 無損繼承    │
└────────────────────────────────────────────────────────────────────────┘

 原始長會話 (200k~300k Tokens，85% 為 Bash/Tool Output 雜訊)
         │
         │ (閒置即將超過 1 小時，Prompt Cache 瀕臨過期)
         ├───────────────────────────────────────────────────────┐
         ▼                                                       ▼
 ┌───────────────────────────────────┐   ┌──────────────────────────────────────────┐
 │ 路徑 A：Claude Code 官方預設       │   │ 路徑 B：cc-session-reader 方案 (推薦)    │
 │ (idleCompaction: true)            │   │ (idleCompaction: false + inherit)        │
 ├───────────────────────────────────┤   ├──────────────────────────────────────────┤
 │ • 後台自動觸發 compact            │   │ • 關閉自動有損壓縮，保留完整 JSONL 軌跡  │
 │ • 生成幾百字高度抽象「摘要」       │   │ • 由 Go 引擎在 context 外靜態高效過濾    │
 │ • 剪除所有歷史問答語境            │   │ • 剔除巨幅 Tool Outputs，保留 100% 對話  │
 │ • Token 降至 ~5k                  │   │ • Token 從 300k 直降至 30k~50k           │
 └─────────────────┬─────────────────┘   └────────────────────┬─────────────────────┘
                   │                                          │
                   ▼ (使用者返回或重啟會話)                     ▼ (以 inherit 分頁載入)
 ┌───────────────────────────────────┐   ┌──────────────────────────────────────────┐
 │ 結果：有損續接 (Lossy Resume)     │   │ 結果：無損對話繼承 (Dialogue Inherit)    │
 │ ⚠️ 遺失原始推論細節與決策因果      │   │ ✅ 保留完整使用者原始意圖與模型決策脈絡 │
 │ ⚠️ 容易出現「摘要失憶」與重蹈覆轍 │   │ ✅ 既避開快取過期天價重算，又無認知衰減 │
 └───────────────────────────────────┘   └──────────────────────────────────────────┘
```

### 1.3 cc-session-reader 的核心架構優勢
- **Context 外解析**：由本機編譯的 Go 執行檔（`cc-session.exe`）直接解析 Claude Code 原生 `transcript.jsonl`，完全不消耗任何 LLM Token。
- **過濾工具雜訊**：將 300k 的原始 Log 中動輒數千行的 Bash 編譯報表、檔案 Dump 壓縮為單行摘要（如 `Bash | cargo test` 或 `(cc-session: 1320 lines omitted)`），僅保留 `user:`、`assistant:` 與關鍵工具失敗標記。
- **分頁無損繼承（`inherit`）**：以每頁 $\le 28\text{K}$ 字元安全分頁載入歷史對話，兼顧 Context 窗口健康度與 100% 原始對話保真度。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與本地技能庫完全契合**：本地已安裝 `cc-session` 與 `agent-handoff` 技能（配置於 `~\.gemini\config\skills\cc-session\SKILL.md`），且專案源碼位於 `C:\GitHub\cc-session-reader`（由 `SanHsien` 進行 Windows-first 維護）。
  - **與前篇 `claude-mem` 互補構成完整體系**：
    - **執行期間（In-Session）**：採用 `autocompact 400K + claude-mem`，在長跑開發中透過背景 Observer 紀錄針式記憶。
    - **閒置與跨會話（Idle / Inter-Session）**：將 `idleCompaction` 設為 `false` 或拉高閾值，當面臨長時休眠或快取過期時，改由 `cc-session inherit` 進行高保真對話恢復。
- **配置策略指引**：
  - 若日常任務皆為連貫開發，建議在 `settings.json` 中配置 `"idleCompaction": false`，或將 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` 提高至 350k，避免因暫時離開 1 小時就遭遇非預期的摘要有損截斷。
  - 當需要回溯前一天或數小時前的上下文時，優先使用 `cc-session inherit <session-id>`，以 30k~50k 的輕盈開銷繼承純對話，徹底杜絕模型「失憶」。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261017-27`**｜**[優先級：高]** 配置 Claude Code `idleCompaction` 與 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` 最佳實踐環境參數
  - **目標範圍**：`~/.claude/settings.json` 與全域環境變數配置
  - **狀態**：🟡 進行中（2026-10-23：[Local Config] 已在 settings.json 的 `env` 設 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS=350000`，保留 `idleCompaction` 預設開啟。依官方文件，門檻最低 100k、無上限，閒置約 54 分鐘且在一小時快取下才觸發，需 Claude Code 2.1.299 以上；本機 CLI 為 2.1.296，尚待升級後實測觸發行為才可標完成）
  - **具體實作步驟**：
    1. 檢視本地 Claude Code 設定檔與環境變數，評估目前 `idleCompaction` 預設行為。
    2. 設定 `settings.json` 參數（評估 `idleCompaction: false` 或提升觸發門檻至 `350k`）。
    3. 驗證閒置過期後之行為，確認不會在進行大型工作時被自動壓縮洗掉上下文。
  - **驗收標準（DoD）**：產出設定範例與驗證記錄，確認參數生效且會話狀態維持可控。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [x] **`T-20261017-28`**｜**[優先級：中]** 整合 `cc-session-reader` 打造「快取過期後的無損對話重建與接手協議（Dialogue-Preserving Resume）」
  - **目標範圍**：`SanHsien/cc-session-reader`（個人維護 Fork，本地路徑 `C:\GitHub\cc-session-reader`）與 `cc-session` Skill
  - **完成日期**：2026-10-23
  - **維護備註**：本專案為個人 Fork（`SanHsien/cc-session-reader`），依全域規範在該倉庫執行 PR/Push/Release 均直接對準 `SanHsien/<repo>`，不打上游。
  - **具體實作步驟**：
    1. 測試 `cc-session inherit` 在 200k+ 超長會話下的壓縮比率與解析效能。
    2. 定義標準重啟流程：當會話超過 1 小時或跨日中斷時，以 `cc-session inherit` 提取過濾後的純對話歷史，注入新會話接手。
    3. 評估比對：對比「官方 Compact 摘要」與「`cc-session` 純對話繼承」在複雜多檔案專案中的指令執行成功率與失憶發生率。
  - **驗收標準（DoD）**：完成測試對比報告，並在 `cc-session` skill 中補充此對話恢復工作流指引。
  - **實作紀錄 / 證據**：在個人 Fork `SanHsien/cc-session-reader` 完成實作。以本機 495k 字符真實會話 `6b6c9288` 實測，驗證 85.1% 雜訊過濾比率（降至 73k 字符）與 4 頁無失真還原；於 `SKILL.md` / `SKILL.en.md` 補充快取過期後的對話無損重建指引，產出雙語架構決策紀錄 `docs/adr-010-dialogue-preserving-resume.md` 與 `docs/adr-010-dialogue-preserving-resume.en.md`，全量通過 `tools/dev_check.ps1`（12 對雙語文檔、Go test/build 全綠），已提交並推至 origin（Commit `5cac590`）。

---
