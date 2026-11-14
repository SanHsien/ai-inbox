---
id: 2026-11-08-claude-code-builtin-advisor-command-evaluation
title: "Claude Code 原生 `/advisor` 指令與伺服端 `advisor_20260301` 工具評估：Sonnet 主模型＋Opus/Fable 顧問機制與本地 `SanHsien/agent-advisor` 架構對比"
source_url: "https://www.facebook.com/share/p/1CJd6WMoUA/"
source_platform: "Facebook (Claude Taiwan 社團)"
author: "Claude Taiwan 社團分享"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "模型路由與配額分流"
short_title: "Claude原生/advisor指令評估"
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
- **當前狀態**：`⚪ 已封存 (Archived)`（本機已透過 [`SanHsien/agent-advisor`](https://github.com/SanHsien/agent-advisor) 之 `claude-3p.md` 與 `cost-policy.md` 明確規範此功能，無須衍生新任務）
- **相關交叉參照**：
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（Claude Code 四級模型分工架構）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（Claude Code 四角色動態調用原則）
  - [`notes/2026-11-01-will-claude-code-opus-haiku-dynamic-workflows-benchmark.md`](./2026-11-01-will-claude-code-opus-haiku-dynamic-workflows-benchmark.md)（Will 保哥 Opus + Haiku 動態工作流實測）

---

## 1. 資訊初篩（5W1H）與貼文原文

- **貼文原文**（Claude Taiwan 社團）：
  > 「大家知道 Claude 可以自己請顧問嗎？最近才發現這個指令：輸入 `/advisor 模型`，例如 `/advisor opus`。假設使用的主模型是 sonnet，可以安排 opus 或 fable 顧問給他，當 sonnet 無法處理的，會請顧問協助..還滿有趣的」
- **Who**：Claude Taiwan 臉書社團成員分享，底層為 Anthropic 官方於 Claude Code CLI 與 Messages API 推出的 **Advisor Mode（`advisor_20260301`）**。
- **What**：讓較輕量、低成本的執行模型（Executor，如 `sonnet` 或 `haiku`）擔任主模型處理日常讀寫與工具呼叫，並在遇到架構歧義、卡關或收尾前，於同一次推論請求中自動呼叫高階模型（Advisor，如 `opus` 或 `fable`）提供 400–700 tokens 的結構化指導。
- **Where**：
  - Claude Code 互動指令：`/advisor opus` 或 `/advisor fable`
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
| **3P Gateway 相容性** | 依賴 Anthropic 伺服端專用 `advisor-tool-2026-03-01` Beta，第三方代理（如 OpenCodex）未必支援 | 純標準 Subagent / Tool 契約，跨原生與 3P 環境、跨五大平台（Claude/Codex/AGY/Cursor/Hermes）皆可運作 |
| **Fable 額度風險** | 若設 `/advisor fable`，每次自動觸發皆消耗額外點數（Credits），且觸發時機不受控 | 本機 `~/.claude/doctrine/10-model-dispatch.md` 明訂：`fable` 需額外點數，預設禁用，不自動混搭 |

---

## 3. 本機現況核對與評估結論

經核對本機 `SanHsien/agent-advisor` 與 `~/.claude/` 現行配置：
1. **已明確納管並預設關閉原生 `/advisor`**：
   - 在 `C:\GitHub\agent-advisor\claude\plugins\agent-advisor-claude\skills\orchestration\references\cost-policy.md` 第 12 行已明訂：*「顧問建議不等於 fresh reviewer 的獨立最終審查。原生顧問功能保持選用；要使用必須先確認該 runtime、provider、模型配對與費用來源支援，遵守該版路由及角色合約。」*
   - 在同目錄 `claude-3p.md` 第 10、16 行已明訂：*「Anthropic server-side advisor 預設不開啟；只有 gateway 完整支援且取得可核對證據才選用。顧問不是獨立終審……原生維持既有 Opus family primary，保留使用者的 Opus 5.5／中偏好；不為混搭架構自動改用 Fable 或舊版本。」*
2. **結論（不衍生新待辦任務）**：
   - 該貼文介紹的 `/advisor opus | fable` 屬於「以 Sonnet 為主模型」的省費折衷用法；而本機環境已採用更嚴謹的「Opus 5.5 主控 ＋ `SanHsien/agent-advisor` 風險分流 ＋ Fresh-Context 獨立審查」架構，並已在制度檔中針對原生 `/advisor` 與 `fable` 點數消耗訂立明確邊界。因此本篇作為技術情報歸檔備查（`status: archived`），不額外衍生重複任務。
