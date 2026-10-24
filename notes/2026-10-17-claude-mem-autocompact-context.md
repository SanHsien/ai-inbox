---
id: 2026-10-17-claude-mem-autocompact-context
title: "Claude-Mem 跨 Session 記憶中樞與 Autocompact 400K 雙軌協同架構分析"
source_url: "https://github.com/thedotmack/claude-mem"
source_platform: "GitHub"
author: "thedotmack"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: archived
cluster: 1
cluster_role: "記憶繼承"
short_title: "Claude-Mem 跨 Session 記憶"
tags:
  - context-management
  - long-term-memory
  - autocompact-400k
  - claude-code
  - mcp
  - agent-architecture
---

# Claude-Mem 跨 Session 記憶中樞與 Autocompact 400K 雙軌協同架構分析

- **來源連結**：[thedotmack/claude-mem (GitHub)](https://github.com/thedotmack/claude-mem)
- **專案作者**：`thedotmack`
- **開源協議**：`Apache-2.0`（9k+ GitHub Stars）
- **分析日期**：`2026-10-17`
- **當前狀態**：`⚪ 封存不做 (Archived)`
- **相關交叉參照**：[`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](./2026-10-17-claude-code-idle-compaction-cc-session-reader.md)

---

## 1. 核心內容摘要與技術深挖

### 1.1 痛點分析：超長會話中的「失憶」與「上下文爆炸」
在 AI Coding Agent（如 Claude Code, Codex, Antigravity）的日常大型開發實踐中，經常面臨兩難困境：
1. **上下文爆炸（Context Bloat）**：頻繁執行 Bash 指令、大型檔案檢視與測試報表，導致 Token 快速逼近 200K / 400K 窗口極限，造成推論延遲激增、費用飆升，甚至引發模型注意力渙散。
2. **壓縮失憶（Compact Amnesia）**：當觸發原生的 `/compact` 截斷壓縮時，系統通常進行盲目摘要，往往剪除關鍵因果資訊（如「為什麼放棄某種架構設計」、「測試失敗的真正根因」、「環境中特定的編碼與路徑坑」）。重啟或 Compact 後，Agent 容易陷入重蹈覆轍的無效循環。

### 1.2 雙軌協同架構：Autocompact 400K + Claude-Mem
使用者提出的關鍵實踐假說：**「用 autocompact 400K + claude-mem 試試」**。這構建了一套解耦的「短期工作記憶防爆」與「外置長期海馬迴」雙軌協同機制：

```text
┌────────────────────────────────────────────────────────────────────────┐
│             Autocompact 400K + Claude-Mem 雙軌協同架構                 │
└────────────────────────────────────────────────────────────────────────┘

 [Agent 執行互動 (Tool Calls / File Edits / Bash Logs)]
         │
         ├───▶ [即時上下文 (Active Context Window: 上限 400K)]
         │        │
         │        ├─ 容納多輪代碼對比、編譯報表、測試執行
         │        │
         │        ▼ (當 Token 達到 400K 臨界閾值)
         │     ┌──────────────────────────────────────────────┐
         │     │ 原生 Autocompact 觸發                        │
         │     │ └─ 快速剪除臨時性輸出，重置工作推論空間      │
         │     └──────────────────────────────────────────────┘
         │
         └───▶ [Claude-Mem 後台觀察者 (Async Observer Hook)]
                  │
                  ├─ 1. 異步攔截 Tool Outputs 與關鍵對話
                  ├─ 2. 結構化提煉「針式記憶 (Needle Observations)」
                  │     • [Decision] 架構決策與邊界選擇
                  │     • [Bugfix] 踩坑紀錄與環境修復因果
                  │     • [Workflow] 驗收指令與依賴關係
                  │
                  ▼
         ┌────────────────────────────────────────────────────┐
         │ 外置持久化存儲 (SQLite Vector / Local Markdown Log) │
         └────────────────────────────────────────────────────┘
                  │
                  ▼ (Compact 後或新 Session 啟動)
         ┌────────────────────────────────────────────────────┐
         │ MCP 記憶檢索器 (Claude-Mem MCP Server)             │
         │ └─ 0-token 開場常駐，Agent 依需求主動 Semantic 召回 │
         └────────────────────────────────────────────────────┘
```

### 1.3 Claude-Mem 核心運作機制解密
1. **非侵入式 Observer Hook**：
   - 透過命令列或執行環境的 Pre/Post Hook，在工具執行完畢的瞬間，於背景異步呼叫輕量模型（如 Claude Haiku / Flash）將執行過程提煉成 1~2 句高密度觀察。
2. **針式觀察分類（Observation Tagging）**：
   - 標籤化管理記憶：`decision`、`bugfix`、`pattern`、`todo`，避免無結構的文字流水帳。
3. **分層記憶檢索（Hierarchical Retrieval）**：
   - **Tier 1 (Timeline Overview)**：Session 開場或 Compact 後，僅注入最近數筆時間線索引（~500 tokens）。
   - **Tier 2 (On-demand MCP Query)**：當 Agent 遭遇特定錯誤或需要歷史決策時，主動調用 `search_memory` 進行向量或關鍵字檢索，按需提取深度細節。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與 `agent-handoff` 及 `pickup/dropoff` 互補**：現有的 `agent-handoff` 依賴手動或特定指令產出 `HANDOFF.md`；`claude-mem` 則是自動、持續且非同步地在背景記錄，兩者可形成「自動底層日誌 + 主動交接協議」的立體防護。
  - **適配 Windows 11 原生環境**：需驗證 Hook 在 Windows PowerShell 環境下的執行效能，確保不會因背景進程喚醒造成指令阻塞。
  - **符合本庫「零機密洩漏」規範**：外置記憶儲存時必須嚴格執行敏感資訊遮蔽（Redaction），禁止將 API Keys、Tokens 或個人認證資訊寫入持久化資料庫。

- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **400K 臨界點配置策略**：在支援 400K+ 上下文的模型（如 Claude 3.5 Sonnet / Gemini 1.5 Pro）中，將 autocompact 閾值設在 350K~400K，能最大化發揮長上下文的推論連貫性。
    2. **外置海馬迴理念**：將「記憶持久化」移出即時 Context Window，徹底解決長程專案跨天、跨 Session 的失憶問題。
  - **適用性界線**：
    - 小型腳本或一兩步就完成的修復任務不需開啟 Observer；對於多步驟、涉及 5 個以上模組的大型重構專案，雙軌記憶機制是防止退化（Regression）的關鍵護城河。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261017-25`**｜**[優先級：低]** 評估並實作「Claude-Mem 本地環境部署與 Tool Hook / MCP Observer 整合測試」
  - **目標範圍**：`SanHsien/ai-inbox` 與 Coding Agent 本地工具鏈
  - **狀態**：⚪ 不做（跨 Session 記憶已由 agent-relay context 與 Obsidian 知識庫打通，無須另行引入複雜的 Claude-Mem Hook）
  - **具體實作步驟**：
    1. 研究 `thedotmack/claude-mem` 在 Windows 11 本地環境的安裝配置流程（npm/pip/binary）。
    2. 配置 MCP 伺服器設定，驗證 Claude Code / Codex 能否正常加載 `claude-mem` 提供的記憶檢索工具。
    3. 實測 Observer Hook：執行一組包含代碼修改、錯誤排查與測試驗證的流程，確認背景日誌是否成功結構化記錄至本地資料庫。
  - **驗收標準（DoD）**：在不洩漏機密的前題下，完成本機整合驗證，記錄記憶寫入與檢索的延遲及 Token 開銷報告。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261017-26`**｜**[優先級：低]** 建立「400K Autocompact 臨界閾值與針式記憶（Needle Observations）檢索評估基準」
  - **目標範圍**：長上下文管理規範與評測協議
  - **狀態**：⚪ 不做（外置針式記憶機制已由 agent-relay 集中中樞與 cc-session-reader 取代）
  - **具體實作步驟**：
    1. 設計高壓測試場景：模擬累積 300K~400K 原始上下文（包含大量測試日誌與 AST diff）。
    2. 觀察 Autocompact 觸發前後，原生記憶保留率與因果鏈條完整度。
    3. 評估引入 `claude-mem` 針式記憶檢索後，Agent 是否能 100% 準確召回 200K 前的關鍵架構決策。
  - **驗收標準（DoD）**：產出評估報告，明確定義 400K Autocompact 搭配外置記憶的最佳實踐參數與觸發門檻。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---
