---
id: 2026-11-08-claude-code-builtin-advisor-command-evaluation
title: "Claude Code 原生 `/advisor` 指令與伺服端 `advisor_20260301` 工具評估：Sonnet 主模型＋Opus/Fable 顧問機制與本地 `SanHsien/agent-advisor` 架構對比"
source_url: "https://www.facebook.com/share/p/1CJd6WMoUA/"
source_platform: "Facebook (Claude Taiwan 社團)"
author: "Richie Yang（Claude Taiwan 社團）"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "模型路由與配額分流"
short_title: "Claude原生/advisor指令評估"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "未登入只讀到 23 則留言（共 28 則）；貼文全文與 1 張附圖已看完"
source_images: 1
source_replies: 23
tags:
  - claude-code
  - advisor-mode
  - model-routing
  - opus
  - sonnet
  - fable
  - agent-advisor
---

# Claude Code 原生 `/advisor` 指令與伺服端 `advisor_20260301` 工具評估：Sonnet 主模型＋Opus/Fable 顧問機制與本地 `SanHsien/agent-advisor` 架構對比

- **來源連結**：[Facebook 分享短網址](https://www.facebook.com/share/p/1CJd6WMoUA/) ｜ [Claude Taiwan 社團貼文永久網址](https://www.facebook.com/groups/1224997379198346/posts/1437020144662734/)
- **歸屬集群**：集群 1：多 Agent 編排、模型路由與 Context 治理（角色：`模型路由與配額分流`）
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（Claude Code 四級模型分工架構）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（Claude Code 四角色動態調用原則）
  - [`notes/2026-11-01-will-claude-code-opus-haiku-dynamic-workflows-benchmark.md`](./2026-11-01-will-claude-code-opus-haiku-dynamic-workflows-benchmark.md)（Will 保哥 Opus + Haiku 動態工作流實測）

---

## 0. 原始資料盤點

> 2026-11-16 重審：Facebook 未登入可讀貼文全文（發文者 Richie Yang，2026-11-03 18:28；1,151 個心情、28 則留言、309 次分享）、1 張附圖與 23 則留言。

- **作者圖片**：共 1 張，是 Claude 對 `/advisor` 的中文說明畫面截圖，放大看過：
  - 說明顧問只出主意，實際讀檔、改程式、跑指令的還是主模型；截圖當下狀態是 `Advisor: off`。
  - 指令表有五種：`/advisor opus`、`/advisor sonnet`、`/advisor fable`、`/advisor off`（關閉）、`/advisor`（不帶參數，查看目前設定）。
  - 四個使用例：主模型用便宜的、顧問用強的；任務很長步驟很多時用來發現方向走偏；有取捨的決定想要第二意見；簡單工作就關掉，免得多花用量。
- **作者留言補充**：發文者在讀到的範圍內沒有回覆任何留言。
- **網友留言重點**（頁面標示 28 則，未登入讀到 23 則，其餘需登入）：
  - `江品陞`（48 個讚，全串最高）：這個指令會把當輪整個 Context 送給顧問，而且沒有快取，顧問選 Fable 會非常貴；建議寫一個只給顧問必要 Context 的外掛，或改用子代理做顧問的事。
  - `Richard Chan`（12 個讚）：同一個提醒。主模型的 Context 會整包推給顧問模型，對話已經很長時對 token 用量影響很大。
  - `Jim Ho`：相反的回報，覺得好用而且很省額度。
  - `SparklyQuince4034`：自己的做法是先把目前對話整理成一份 Markdown，再請顧問只看那份檔案給意見。
  - `Taboco Cheng`、`Ken Cheng`：Opus 會自己開子代理；有人遇到一次開 26 個，高階方案不到一天用掉一週額度的三分之一。
  - `賴俊宇`、`鄧翔宇`、`Bo-Han Chen`、`Yoyo Young`：偏好由上層模型派工管下層，或用多分頁各開 Agent 互相討論，比顧問模式有彈性也比較省。
  - `Powu Chang`、`鄭麥克`：這功能已經推出好幾個月，不是新東西。
  - `ChunHao Hsu` 附了一張自己應用程式的模型選單截圖，選項裡有「Sonnet 加 Opus 複核、顧問另計」，可見有人把這個模式包進自己的產品；截圖含個人資料，不記錄內容。
- **對分析的影響**：
  - 作者欄原寫「Claude Taiwan 社團分享」，頁面顯示發文者是 Richie Yang；已更正。
  - 圖片顯示顧問也可以設成 `sonnet`，還有 `/advisor off` 與不帶參數的查詢用法；第 1 節 Where 原本只列 `opus` 與 `fable`，已補齊。
  - 最重要的新資訊是成本：兩則高讚留言都指出顧問每次被呼叫都會收到整段對話，對話越長越貴，其中一則還說沒有快取。原筆記的對照表只把「讀完整歷史」當成思路被錨定的問題，沒提到費用；已在對照表補一列。「沒有快取」是留言者的說法，本次未對照官方文件查證。
  - 留言裡的替代做法（先整理成檔案再給顧問看、用子代理、上層派工）和本機 `agent-advisor` 的路線一致，補進第 3 節作為佐證。
  - 本機 `cost-policy.md` 目前只寫「要先確認費用來源支援」，沒有寫明「顧問呼叫成本隨對話長度成長」這個具體風險。新增任務 `T-20261108-07`：先查證官方計費與快取行為，再把結論寫進成本規則。狀態因此由 `archived` 改為 `pending`。

---

## 1. 資訊初篩（5W1H）與貼文原文

- **貼文原文**（Claude Taiwan 社團，發文者 Richie Yang）：
  > 「大家知道 Claude 可以自己請顧問嗎？最近才發現這個指令：輸入 `/advisor 模型`，例如 `/advisor opus`。假設使用的主模型是 sonnet，可以安排 opus 或 fable 顧問給他，當 sonnet 無法處理的，會請顧問協助..還滿有趣的」
- **Who**：Claude Taiwan 臉書社團成員分享，底層為 Anthropic 官方於 Claude Code CLI 與 Messages API 推出的 **Advisor Mode（`advisor_20260301`）**。
- **What**：讓較輕量、低成本的執行模型（Executor，如 `sonnet` 或 `haiku`）擔任主模型處理日常讀寫與工具呼叫，並在遇到架構歧義、卡關或收尾前，於同一次推論請求中自動呼叫高階模型（Advisor，如 `opus` 或 `fable`）提供 400–700 tokens 的結構化指導。
- **Where**：
  - Claude Code 互動指令：`/advisor opus`、`/advisor sonnet` 或 `/advisor fable`；`/advisor off` 關閉，不帶參數的 `/advisor` 查看目前設定（依貼文附圖）
  - 官方文件：[Advisor tool（API）](https://docs.claude.com/en/docs/agents-and-tools/tool-use/advisor-tool)、[Claude Code commands](https://code.claude.com/docs/en/commands)（2026-11-14 兩頁可開啟，commands 頁有 advisor 字樣；以下參數名稱以官方頁為準）
  - CLI 啟動參數：`claude --advisor opus`
  - 設定檔持久化：`~/.claude/settings.json` 中的 `"advisorModel": "opus"`
  - Anthropic API Beta：`betas=["advisor-tool-2026-03-01"]`，工具型別 `type: "advisor_20260301"`
- **Why**：解決「全程跑 Opus/Fable 太貴太慢」與「全程跑 Sonnet/Haiku 在複雜邊界容易迷航（Context Anxiety）」的兩難。

---

## 2. 底層技術機制與本機 `SanHsien/agent-advisor` 架構對比

Anthropic 原生 `/advisor`（Executor 主導＋中途請教 Advisor）與本機五大 Agent 統一採用的 [`SanHsien/agent-advisor`](https://github.com/SanHsien/agent-advisor)（Architect 主導＋選擇性風險派工）代表兩種截然不同的多模型協作拓撲：

```text
[模式 A：Anthropic 原生 /advisor (Bottom-Up 執行者請教制)]
  使用者 ──► 主 Session: Sonnet (Executor)
                 ├─ 日常讀寫檔、跑 Bash
                 ├─ 覺得卡關時觸發 Server-Side Tool (advisor_20260301)
                 │       └──► Opus / Fable (Advisor) 讀完整對話，回傳 400~700 字建議
                 └─ Sonnet 繼續執行並自行拍板結案
  ⚠️ 盲點：由能力較弱的 Sonnet 自己決定「何時該問顧問」，當 Sonnet 陷入盲目自信時根本不會呼叫顧問；
           且同一上下文建議不等於 Fresh-Context 獨立終審。

[模式 B：本機 SanHsien/agent-advisor (Top-Down 主架構師路由制)]
  使用者 ──► 主 Session: Opus 5.5 / medium (Primary Architect)
                 ├─ 開工前強制宣告 SELECTIVE ROUTE (solo / delegate / audit / full)
                 ├─ delegate: 規格明確交由 Sonnet/medium 或 Haiku 施工；疑難雜症交 Sonnet/high
                 ├─ 主代理親自查核完整 git diff 與測試輸出證據
                 └─ audit / full: 啟動全新獨立 Context 的 Opus Reviewer 終審 (ship / fix-first / rethink)
```

### 關鍵差異與工程取捨對照表

| 比較維度 | Claude Code 原生 `/advisor` (`advisor_20260301`) | 本機 `SanHsien/agent-advisor` (`orchestration`) |
| :--- | :--- | :--- |
| **主會話模型（Primary）** | 較小模型（如 `sonnet`），因規則限制顧問位階必須 $\ge$ 主模型 | 旗艦推理模型（`Opus 5.5 / medium`），直接把關需求理解與最終驗收 |
| **觸發決策權** | 由較弱的 Executor 模型「自覺卡關」才觸發（顯示 `Advising` $\rightarrow$ `Reviewed`） | 由頂層 Architect 依任務風險與規格完整度事前強制分流（`SELECTIVE ROUTE`） |
| **Context 隔離性** | 顧問直接讀取主會話完整歷史（共享同一段上下文，易受既有思路錨定） | 實作子代理（Implementer）與審查子代理（Reviewer）皆為 **Fresh Context**，不帶作者偏見 |
| **顧問呼叫成本** | 留言回報：每次呼叫都把整段對話送給顧問，對話越長越貴；有留言稱沒有快取（未查證） | 派給子代理的是另外寫的精簡任務說明，不帶主對話歷史 |
| **3P Gateway 相容性** | 依賴 Anthropic 伺服端專用 `advisor-tool-2026-03-01` Beta，第三方代理（如 OpenCodex）未必支援 | 純標準 Subagent / Tool 契約，跨原生與 3P 環境、跨五大平台（Claude/Codex/AGY/Cursor/Hermes）皆可運作 |
| **Fable 額度風險** | 若設 `/advisor fable`，每次自動觸發皆消耗額外點數（Credits），且觸發時機不受控 | 本機 `~/.claude/doctrine/10-model-dispatch.md` 明訂：`fable` 需額外點數，預設禁用，不自動混搭 |

---

## 3. 本機現況核對與評估結論

經核對本機 `SanHsien/agent-advisor` 與 `~/.claude/` 現行配置：
1. **已明確納管並預設關閉原生 `/advisor`**：
   - 在 `C:\GitHub\agent-advisor\claude\plugins\agent-advisor-claude\skills\orchestration\references\cost-policy.md` 第 12 行已明訂：*「顧問建議不等於 fresh reviewer 的獨立最終審查。原生顧問功能保持選用；要使用必須先確認該 runtime、provider、模型配對與費用來源支援，遵守該版路由及角色合約。」*
   - 在同目錄 `claude-3p.md` 第 10、16 行已明訂：*「Anthropic server-side advisor 預設不開啟；只有 gateway 完整支援且取得可核對證據才選用。顧問不是獨立終審……原生維持既有 Opus family primary，保留使用者的 Opus 5.5／中偏好；不為混搭架構自動改用 Fable 或舊版本。」*
2. **留言區的實務回報與本機做法同向（2026-11-16 重審新增）**：
   - 多位留言者改用「上層模型派工給子代理」或「先把對話整理成檔案，再請另一個模型只看那份檔案」，理由是比顧問模式省、也更可控。這正是本機 `agent-advisor` 的 delegate 與 audit 路線。
   - 也有相反的回報（覺得顧問模式省額度），以及 Opus 自行開出二十多個子代理、一天內用掉大量週額度的例子。兩種模式都可能失控，差別在有沒有事前的路由宣告與數量上限。
3. **結論（原評估不衍生任務；重審後新增一項成本警語任務）**：
   - 該貼文介紹的 `/advisor opus | fable` 屬於「以 Sonnet 為主模型」的省費折衷用法；而本機環境已採用更嚴謹的「Opus 5.5 主控 ＋ `SanHsien/agent-advisor` 風險分流 ＋ Fresh-Context 獨立審查」架構，並已在制度檔中針對原生 `/advisor` 與 `fable` 點數消耗訂立明確邊界。原評估因此把本篇歸檔備查。2026-11-16 重審留言後，發現成本規則少了一條具體警語，新增下列任務。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261108-07`**｜**[優先級：低]** 查證原生顧問功能的計費與快取行為，並在 `SanHsien/agent-advisor` 的成本規則補上「顧問呼叫成本隨對話長度成長」警語
  - **目標範圍**：`SanHsien/agent-advisor` 的 `claude/plugins/agent-advisor-claude/skills/orchestration/references/cost-policy.md`；本 repo 的 `docs/claude-advisor-cost-check.md`（查證紀錄）
  - **具體做法**：
    1. 讀官方 [Advisor tool 文件](https://docs.claude.com/en/docs/agents-and-tools/tool-use/advisor-tool)的計費與快取段落，確認三件事：顧問每次呼叫是否收到完整對話、顧問端輸入是否有快取（預設開或關）、顧問 token 以哪個模型的費率計。逐項附官方原文所在段落的連結；查不到的寫「未載明」，不用留言當依據。
    2. 把查證結果寫成 `docs/claude-advisor-cost-check.md`，並對照本筆記第 0 節兩則留言的說法，標明哪些被官方文件證實、哪些沒有。
    3. 依查證結果在 `cost-policy.md` 第 12 行那一條之後補一句具體警語（例如長對話中途開顧問前先估輸入量，或改派子代理），並跑該 repo 既有的檢查。
  - **驗收標準（DoD）**：`docs/claude-advisor-cost-check.md` 存在且三個問題各有官方連結或「未載明」的結論；`SanHsien/agent-advisor` 有對應 commit，`cost-policy.md` 內可 grep 到新增的警語；該 repo 的既有測試或驗證指令通過。
  - **完成日期**：2026-11-17
  - **實作紀錄 / 證據**：docs/claude-advisor-cost-check.md（官方文件 2026-11-17 查證：顧問每次收完整對話、Claude Code 不快取、以顧問模型費率計）；SanHsien/agent-advisor commit 5ab3b22 在 Claude 版 cost-policy.md 新增警語並記入 CHANGELOG，dev_check.ps1 通過。
