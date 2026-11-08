---
id: 2026-11-08-dustin-gmat-danyuchn-claude-work-mode-session-modes
title: "評析 Dustin GMAT 推薦「claude-work-mode」：Claude Code 三態工作流（auto/out/wrap）、批次確認集中化與外派節流閘門架構深挖"
source_url: "https://www.threads.com/share/_gD_V1h27"
source_platform: "Threads (@dustin_gmat) / GitHub (danyuchn/claude-work-mode)"
author: "Dustin GMAT (@dustin_gmat) / danyuchn"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "會話模式與節奏控制"
short_title: "Claude-Work-Mode三態架構深挖"
tags:
  - claude-code
  - claude-work-mode
  - work-mode
  - tempo
  - session-modes
  - autonomous-agents
  - gate-hooks
  - token-optimizer
---

# 評析 Dustin GMAT 推薦「claude-work-mode」：Claude Code 三態工作流（auto/out/wrap）、批次確認集中化與外派節流閘門架構深挖

- **來源貼文**：[Threads 貼文 `@dustin_gmat`（9.9K 觀看，142 讚）](https://www.threads.com/share/_gD_V1h27)（短網址 `_gD_V1h27`，真實 URL `https://www.threads.com/@dustin_gmat/post/DfeccsumJrq`）
- **官方開源 GitHub 倉庫（主動深挖查證）**：
  - [`danyuchn/claude-work-mode`](https://github.com/danyuchn/claude-work-mode)（MIT 授權，由 Dustin / danyuchn 開發，附中英雙語完整說明與展示影片）
- **分析日期**：`2026-11-08`
- **分析者**：`Antigravity`
- **當前狀態**：`📁 歸檔備查 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md`](./2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md)（Claude Code 領域技能包）
  - [`notes/2026-11-08-otto-scope-openmausbot-local-vm-agent-fleet.md`](./2026-11-08-otto-scope-openmausbot-local-vm-agent-fleet.md)（OpenMausBot 權限仲裁架構）

---

## 1. 核心內容摘要與痛點還原（Executive Summary）

Threads 作者 Dustin（`@dustin_gmat`）分享其開源專案 `claude-work-mode`：
> 「應該是我用 Claude Code 以來開發過最自豪的工具，讓我的人工干預少了 70%、Claude 額度節省 30%、context switching 所造成的注意力耗損都消失了。」

其解決了重度使用 Coding Agent 時的三大核心痛點：
1. **注意力碎片化（Attention Fragmentation）**：傳統模式下，Agent 每進行一次檔案修改、本地 commit 或測試，都中途暫停等待人類授權，迫使工程師頻繁切換注意力。
2. **Token 與上下文膨脹（Context Bloat）**：在 System Prompt 塞入冗長的「不要問我、自動執行」指令，每輪對話都會重複計費；若主線模型直接讀取數萬字元的日誌或搜尋結果，會迅速擠爆高成本模型（Opus / Sonnet）的上下文。
3. **收尾無限發散（Scope Creep）**：任務即將完成時，模型往往自作主張提出額外的架構重構或分支優化，難以乾淨結案。

---

## 2. 三態工作流（Session Work Modes）核心機制

`claude-work-mode` 以單一斜線指令 `/work-mode` 動態切換當前會話狀態，模式僅作用於當前 Session，不永久污染全域環境：

```
+-----------------------------------------------------------------------------------+
|                        claude-work-mode 三態工作流架構                            |
+-----------------------------------------------------------------------------------+
|  /work-mode auto (自主推進 + 批次確認)                                            |
|    - 可逆操作放行: 本地改檔、本地 commit、執行測試不中途停頓                      |
|    - 批次詢問集中: 會觸發確認提示的外部動作留到最後一口氣跑完，打斷次數降為 1 次 |
|    - 硬閘門安全網: 真正不可逆動作 (對外發訊、套件安裝、金流、刪除) 記錄為待決事項 |
|                                                                                   |
|  /work-mode out (外派節流 + 額度分流)                                             |
|    - 批次任務外派: 抽取、分類、審核工作下放至背景子代理或外部 CLI (codex/gemini)   |
|    - Nudge 節流閥: 主線單一回合讀取 > 20,000 字元未外派時，自動觸發提醒           |
|    - Quota-Aware: 依外部模型池額度表 (quotaFile) 自動動態引導分流                |
|                                                                                   |
|  /work-mode wrap (收斂結案)                                                       |
|    - 凍結新分支: 不開啟新探索，全力完成當前手頭工作                              |
|    - 待決結構化: 強制標註類別 (對外/金流/刪除/權限/取捨) 並附具體推薦建議        |
|    - 自動收工: 當手邊無待辦時，可自動執行結案命令 (autoCloseCommand)              |
+-----------------------------------------------------------------------------------+
```

---

## 3. 深層技術架構與 Token 優化精妙之處

經查證原始碼（`tempo.ts`、`nudge.ts`、`config.ts`），其具備以下關鍵工程設計：

### 3.1 零 Token 膨脹注入（Single-Shot Prompt Injection）
- **傳統做法缺點**：若將工作模式規則寫進全域提示詞，每輪請求都會消耗數百至上千 Tokens。
- **本專案解法**：`claude-work-mode` 將指令文本僅隨「下一則工具結果」或「下一則使用者提示」**送給模型一次**（透過 `takePending`）；隨後在對話過程中保持靜默，只有在經歷 Context Compaction（上下文壓縮）或 Resume（會話重啟）可能遺失記憶時，才再次重新注入。

### 3.2 智慧型閘門拒絕與導正（Gate Deny as Guidance）
配合可選安裝的 `work-mode-gates`（外掛 Shell 攔截層），它將狀態寫入 `~/.claude/state/tempo/<session_id>`：
- **傳統 Gate**：觸發敏感操作時，直接彈窗暫停問使用者「是否允許？」。
- **`auto` 模式下的 Gate**：利用 `tempo_deny "<理由>"` **直接拒絕並附帶修正建議**。例如：
  - `scratch-doc-guard.sh`：偵測到模型意圖新建多餘的 `SUMMARY*.md` 時，直接拒絕並要求「更新既有文件或在回覆中作答」。
  - `git-safe-commit-gate.sh`：偵測到帶路徑的 `git commit` 或未 stage 文件的 `git add` 時，拒絕並指示「改用 `git add -p` 再執行 commit」。
  - 模型接收到明確的拒絕原因後，會自動修正做法繼續推進，**完全不需要人類介入**。

### 3.3 額度分流與字元計量（Quota & Character Throttling）
- 監控單回合工具返回的字元數，當超過閾值（預設 20,000 字元）時發出 Nudge，提醒模型不要在昂貴的主力模型主線消耗過多上下文，引導其外派給背景 Worker 或獨立 CLI。

---

## 4. 與本機資安全域規範之對照評估

使用者全域規範中曾明確強調：
> 「使用者要求『像 Codex/Claude 那樣 auto』是指客戶端執行授權（Turbo Mode），不要在 Prompt 強行閹割思考停頓... 提示詞應保留模型在重大疑慮時主動向使用者確認的判斷力。」

`claude-work-mode` 的架構設計正好完美落實了此一原則：
1. **不是無腦放行**：它並未在 Prompt 中強令「禁止暫停」，而是嚴格區分「可逆本機操作（放行）」與「不可逆破壞/外部操作（後置批次確認）」。
2. **利用 Gate 回傳反饋促進自癒**：當模型踩到邊界時，透過 Gate 拒絕並給出處方，由模型自主修復，而非雙重煞車失效。
3. **收斂階段強制決策標籤**：`wrap` 模式要求所有待決事項必須標註標籤與具體得失取捨，保證使用者在最終驗收時享有完整的透明度。

---

## 5. 評估結論與處置

1. **實用性判定**：
   - 專案程式碼簡潔扎實（TypeScript + Shell Hooks），具備完整的單元測試與中英展示，展現了專業級的 Claude Code 外掛水準。
   - 其「批次集中確認」、「Gate Deny 引導自癒」與「單次注入防 Token 膨脹」機制，對本地四大 Agent（Antigravity / Claude / Codex / Hermes）的互動節奏調校極具啟發。
2. **處置決策**：
   - 本分析建檔為 **`status: archived` 歸檔備查**，作為本庫開發調度策略與 Prompt/Hook 設計的高價值標竿範本，不衍生額外代碼維護任務。
