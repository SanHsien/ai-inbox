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
source_review: full
source_reviewed_at: 2026-11-17
source_images: 8
source_replies: 41
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

- **來源貼文**：[Threads 貼文 `@dustin_gmat`（初次分析時 9.9K 觀看、142 讚；2026-11-16 重看為 6.2 萬次瀏覽、662 讚、50 則回覆）](https://www.threads.com/share/_gD_V1h27)（短網址 `_gD_V1h27`，真實 URL `https://www.threads.com/@dustin_gmat/post/DfeccsumJrq`）
- **官方開源 GitHub 倉庫（主動深挖查證）**：
  - [`danyuchn/claude-work-mode`](https://github.com/danyuchn/claude-work-mode)（MIT 授權，由 Dustin / danyuchn 開發，附中英雙語完整說明與展示影片）
- **分析日期**：`2026-11-08`
- **分析者**：`Antigravity`
- **當前狀態**：`📁 歸檔備查 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md`](./2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md)（Claude Code 領域技能包）
  - [`notes/2026-11-08-otto-scope-openmausbot-local-vm-agent-fleet.md`](./2026-11-08-otto-scope-openmausbot-local-vm-agent-fleet.md)（OpenMausBot 權限仲裁架構）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看 Threads 貼文：貼文文字、作者釘選留言裡的 60 秒概念影片（抽 8 格看過）、留言 21 則（含作者 2 則；貼文標示 50 則回覆，其餘要登入才看得到；Threads 的留言是捲到才載入，逐段捲動收集）。貼文本身沒有圖片，只有一張 GitHub 連結預覽卡（只讀了卡片標題文字）。

- **作者圖片／影片**：貼文本身無圖。作者在釘選留言補了一支 60 秒概念影片（全是模擬終端機畫面加大標題，共看 8 格）：
  - 格 1–2「用 Claude Code 最累：一直停下來問」：示範請它更新 12 個頁面的導覽列，講了「中間不用問我」還是每步停下來問。
  - 格 3「auto 模式：本機可回復，不再對話打斷」：`/work-mode auto` 後 12 頁一次改完並跑測試；畫面註明金流、刪除、發信這類真正有風險的事才停下確認。
  - 格 4「out 模式：大批工作外派，省下主額度」：示範逐條分類 1,000 筆使用者回饋，自動外派給背景子代理或外部模型，主線只抽樣驗收；畫面字樣寫省下 20% 以上的週額度。
  - 格 5–6「準備收工時：模型開始旁生枝節」：要它彙整進度，它卻提測試覆蓋率偏低、要不要順便重構 CSS。
  - 格 7「wrap 模式：拒絕旁生枝節，聚焦決策」：只列出要使用者決定的事，每項帶類別標籤（對外、金流）與建議。
  - 格 8 總結畫面：指令寫成 `/work-mode auto out wrap`，狀態列顯示三個模式同時啟用。
- **作者留言補充**：
  - 釘選留言說明上面那支概念影片是用 AGY（Antigravity）做的，並說只要讓 Claude 先寫好規則，Gemini 也能有正常水準的表現。
  - 有網友回報連結打開沒東西，作者回覆是 GitHub 那邊的問題，晚點就會正常。
- **網友留言重點**：
  - `meta.ai`（Meta 的 AI 帳號，被網友點名問原理）回覆的摘要：三個模式靠 `UserPromptSubmit` hook 注入 `additionalContext` 並寫狀態檔；auto 把原本會跳確認的地方改成拒絕並附理由；另有 PreToolUse 的 shell gates；`/at` 指令用來判斷人在桌機還是手機、切換回覆格式。這是 AI 生成的回覆，不能當一手資料，但前兩點與本筆記第 3 節依原始碼查到的一致；`/at` 是原筆記沒寫到的指令，未另查原始碼確認。
  - `jwenlovecats` 問這工具對 Codex 有沒有用，可見範圍內沒有人回答。
  - `ai_future88888` 建議額度節省要自己記錄前後用量才看得出來；`andy_chen0214` 提到另一個工具 ponytail 很省 token（未說明是什麼）。
  - `tysys1955` 說自己是硬寫了一套動作準則（沒到某個等級的問題不要問），因為每次等它確認很煩——同一個痛點的另一種解法。
  - 其餘十多則是「晚點丟給我的 agent 看」「先存」這類回應與兩則引用轉發，沒有實測回報或反駁。
- **2026-11-17 登入補讀**：登入後以「熱門」「最新」兩種排序各捲到底、子回覆全部點開，共看到 40 則回覆（含作者釘選留言 1 則）；首輪讀到的那則作者回覆（連結打不開是 GitHub 的問題）這次已不顯示，合計讀過 41 則。貼文標示 50 則，其餘 9 則平台不顯示。新讀到的 20 則中，`theodore039` 回報連結 504、`kuzz.vip` 問網頁是不是掛了（都是發文當下 GitHub 連線問題，兩則底下現在沒有回覆），`sherria_uvu` 開玩笑說省到額度用不完，釘選留言底下 1 則是玩笑；其餘都是「留」「存」「卡」這類標記。`jwenlovecats` 問 Codex 能不能用，登入後確認仍無人回答。**沒有實測回報、反駁或更正，分析不變**。
- **對分析的影響**：
  1. **「三態切換」的說法補正**：影片最後一格顯示三個模式可以同時啟用（`/work-mode auto out wrap`），不是三選一。第 2 節開頭已補一句。
  2. **成效數字的性質**：貼文的「人工干預少 70%、額度省 30%」與影片的「省下 20% 以上週額度」都是作者自述，兩處數字不一致，貼文、影片與留言都沒有附量測方法。第 1 節引用處已加註。
  3. 影片是概念示意（模擬畫面），不是實機錄影，不能當功能驗證。
  4. 仍維持歸檔、不開任務。

---

## 1. 核心內容摘要與痛點還原（Executive Summary）

Threads 作者 Dustin（`@dustin_gmat`）分享其開源專案 `claude-work-mode`：
> 「應該是我用 Claude Code 以來開發過最自豪的工具，讓我的人工干預少了 70%、Claude 額度節省 30%、context switching 所造成的注意力耗損都消失了。」

（上述百分比是作者自述，貼文、影片與留言都沒有量測方法；影片裡另寫「省下 20% 以上週額度」，兩處數字不一致。）

其解決了重度使用 Coding Agent 時的三大核心痛點：
1. **注意力碎片化（Attention Fragmentation）**：傳統模式下，Agent 每進行一次檔案修改、本地 commit 或測試，都中途暫停等待人類授權，迫使工程師頻繁切換注意力。
2. **Token 與上下文膨脹（Context Bloat）**：在 System Prompt 塞入冗長的「不要問我、自動執行」指令，每輪對話都會重複計費；若主線模型直接讀取數萬字元的日誌或搜尋結果，會迅速擠爆高成本模型（Opus / Sonnet）的上下文。
3. **收尾無限發散（Scope Creep）**：任務即將完成時，模型往往自作主張提出額外的架構重構或分支優化，難以乾淨結案。

---

## 2. 三態工作流（Session Work Modes）核心機制

`claude-work-mode` 以單一斜線指令 `/work-mode` 動態切換當前會話狀態，模式僅作用於當前 Session，不永久污染全域環境；三個模式可疊加啟用（作者概念影片最後示範 `/work-mode auto out wrap` 同時開啟三者）：

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
|    - Nudge 節流閥: 主線單回合讀取超過閾值未外派 → 拒絕下一次讀取，直到外派或宣告原因|
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
- 監控單回合工具返回的字元數，當超過閾值（README 設定表載明 `dispatch.nudgeThresholdChars` 預設 `20000`，2026-11-14 查證）時發出 Nudge，提醒模型不要在昂貴的主力模型主線消耗過多上下文，引導其外派給背景 Worker 或獨立 CLI。

---

## 4. 與本機資安全域規範之對照評估

依維護者規則，授權模式（auto）不應靠 Prompt 強行禁止模型的思考停頓，模型在重大疑慮時仍應保留主動向使用者確認的判斷力。

`claude-work-mode` 的設計與此規則方向一致（以 README 描述為據，未實測）：
1. **不是無腦放行**：它並未在 Prompt 中強令「禁止暫停」，而是嚴格區分「可逆本機操作（放行）」與「不可逆破壞/外部操作（後置批次確認）」。
2. **利用 Gate 回傳反饋促進自癒**：當模型踩到邊界時，透過 Gate 拒絕並給出處方，由模型自主修復，而非雙重煞車失效。
3. **收斂階段強制決策標籤**：`wrap` 模式要求所有待決事項必須標註標籤與具體得失取捨，保證使用者在最終驗收時享有完整的透明度。

---

> 環境限制：README 載明 gates 需要 `bash`、`jq`、`git`、`python3`；Windows 原生環境要先裝齊才能跑。

## 5. 評估結論與處置

1. **實用性判定**：
   - 專案程式碼簡潔扎實（TypeScript + Shell Hooks），README 載有 plugin 測試、decision-label self-test 與 gate 測試（本筆記未實跑）及中英展示，展現了專業級的 Claude Code 外掛水準。
   - 其「批次集中確認」、「Gate Deny 引導自癒」與「單次注入防 Token 膨脹」機制，對本地四大 Agent（Antigravity / Claude / Codex / Hermes）的互動節奏調校極具啟發。
2. **處置決策**：
   - 本分析建檔為 **`status: archived` 歸檔備查**，作為本庫開發調度策略與 Prompt/Hook 設計的高價值標竿範本，不衍生額外代碼維護任務。
