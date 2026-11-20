---
id: "2026-11-19-anthropic-building-always-on-agents-blueprint"
title: "Threads 情報與官方架構核實：Anthropic《Building Always-On Agents》五大原語與 Opus 5.5 成本結構"
source_url: "https://www.threads.com/@aiposthub/post/DfuTuZPlM_m"
source_platform: "Threads / aiposthub / Anthropic"
author: "@aiposthub (AI郵報) / William Hu (Anthropic)"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 1
source_replies: 6
source_reviewed_at: "2026-11-20"
status: done
cluster: 1
cluster_role: "常駐Agent五原語"
short_title: "Always-On架構指南"
tags:
  - always-on-agents
  - anthropic
  - opus-5-5
  - event-inbox
  - outbox
  - threads
---

# Threads 情報與官方架構核實：Anthropic《Building Always-On Agents》五大原語與 Opus 5.5 成本結構

- **來源貼文**：[Threads 原貼文（`@aiposthub` AI郵報）](https://www.threads.com/@aiposthub/post/DfuTuZPlM_m)（原分享連結 `https://www.threads.com/share/BAwstC62C5`）
- **官方原文**：[`claude.com/blog/building-always-on-agents`](https://claude.com/blog/building-always-on-agents)（William Hu，2026-11-13）
- **轉載解析文**：[`aiposthub.com/claude-always-on-agents-inbox-memory-outbox`](https://www.aiposthub.com/claude-always-on-agents-inbox-memory-outbox/)
- **發布平台 / 作者**：`Threads` / `@aiposthub`（`2026-11-14`）；原架構指南作者 `William Hu (Anthropic)`
- **分析日期**：`2026-11-19`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-15-hujiaxi-24x7-local-agent-cluster-architecture.md`](./2026-11-15-hujiaxi-24x7-local-agent-cluster-architecture.md)（24×7 本地多機 Agent 架構分析）
  - [`notes/2026-10-21-agent-relay-pipeline-phase4.md`](./2026-10-21-agent-relay-pipeline-phase4.md)（本機 `agent-relay` 通訊與任務管線）

---

## 1. 原始資料盤點（主文、圖表、3 則續樓、3 則網友留言與官方查證）

- **主貼文與 3 則續樓**：整理 Anthropic 公開的 `Always-On Agents` 架構五大核心原語（`Inbox`、`Timers`、`Memory`、`Permissions`、`Outbox`），強調常駐並非 24 小時連續運算，而是「平時休眠、事件喚醒、存進度再休眠」，並引述 `Claude Opus 5.5` 在長程程式基準上相較 `Opus 5` 單任務成本降低 78%。
- **連結預覽圖表（1 張，`Event inbox Database table`）**：
  - 欄位為 `When | What happened | Session | Status`，明確展示 **`Delivered twice, same ID` → `dropped`** 的冪等去重機制，以及 `2. Wake the worker` → `3. Read what's...` → `6. Mark done` 的喚醒狀態機。
- **網友留言與討論（貼文計數 7 則，登入後顯示 6 則全部讀完＝3 續樓 + 3 網友留言，差 1 則不顯示；另有 2 則引用貼文）**：
  - `@bigfatjj_02` 認為架構概念並不算全新；
  - `@gyozalab` 直接點出「**聽起來像是 Hermes 在做的事**」（印證與 Hermes 24×7 常駐機制同向）；
  - `@saominhuang` 表示選擇 Claude 主因在於程式撰寫能力。
- **官方文件查證（Anthropic《Building Always-On Agents》）**：
  - 核實五大原語實作重點：
    1. **Event Inbox**：持久化資料表承接 webhook/通知/使用者訊息，用來源給的唯一識別碼去重；一個**收件匣**同時只有一個工作中的 worker（原稿寫「同一串流」，已改正）。
    2. **Timers**：週期排程與自我追蹤定時器，觸發時僅是往 Inbox 投遞一筆事件。
    3. **Memory**：跨 session 檔案目錄與**任務進度檔（task progress files）**，確保喚醒後精準續跑。
    4. **Permissions**：沙盒外憑證注入代理（credential-injecting proxy）＋風險分類器＋**Deferred Tool Calls**（高風險操作暫停存檔，待人工批准再以新 Inbox 事件續跑）。
    5. **Outbox**：外發訊息管理與節流（`Start quiet` 原則），避免 Agent 背景洗版。
  - **成本數據核實（2026-11-20 重查）**：78% 與 40% 兩個數字出自這篇官方文章本身（同一句話：長程編碼基準上每個解決任務的成本少 78%，一般工作負載少 40%），不是另一份公告。原稿另寫「大幅調降 cache read 費用」，官方文章裡**沒有**這句——文章只建議用提示快取降低成本，沒有提快取讀取的價格；這句已刪除。
  - **轉載文查核**：AI郵報網站的解析文沒有任何成本數字；78% 只出現在 Threads 續樓，對得上官方原文。
- **2026-11-20 登入補讀完成**：貼文計數 7 則，平台顯示 6 則已全部讀完，差 1 則登入後也不顯示。6 則＝作者 3 則續樓加 3 則網友留言；熱門、最新兩種排序都捲到底，列出同樣的 3 則留言，網友留言都沒有回覆串，最新排序裡唯一的「顯示回覆」展開後是作者第 4 段續樓。另有 2 則引用貼文（`@enjoyaudio0715` 只寫「留友看」、`@lasxt1995` 寫「又一個，果然是大趨勢」）；引用是否算進計數無法確認，不拿來補差額。可見內容都是收藏與附和，沒有新的補充、反駁或實測，對本筆記的事實與結論沒有影響。

---

## 2. 對現有系統的啟發與落差評估

- **與本機架構比對**：
  - 本機已有 `Hermes`、`agent-relay`、`schedule` 計時器喚醒、以及全域協作規範「派工要掌控到完成」，涵蓋了 `Timers`、`Memory` 與 `Permissions` 基礎。
  - 唯對照 Anthropic 五大原語，可進一步檢查本機 `C:\GitHub\agent-relay` 目前在 **Event Inbox 冪等去重（同事件 ID 重複投遞自動 `dropped`）** 與 **Outbox 主動回報節流／靜默分級** 兩項機制是否已具備或需補齊設計規範，作為 24×7 無人值守穩定性的最後拼圖。
- **查證註記（2026-11-19，`T-20261119-04`）**：對照結果見 [`docs/always-on-relay-gap-check.md`](../docs/always-on-relay-gap-check.md)。重讀官方原文後修正兩點：原文要求的是「一個**收件匣**同時只有一個工作中的 worker」，不是每個串流；原文的 Outbox 一節沒有給節流或彙整的具體數字，只說需要控制節奏時再加 outbox 資料表與分派器。盤點結論：`agent-relay` 的事件去重與單一工人大部分已有（同 id 拒收、一張工單一個工人），主要缺口在對人的通知沒有彙整與優先級過濾。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261119-04`**｜**[優先級：低]** 對照 Anthropic 五大原語檢視 `agent-relay` 的事件去重（Idempotency）與 Outbox 通知節流機制
  - **目標範圍**：`C:\GitHub\agent-relay`（只讀盤點既有派工／訊息佇列設計）與 `C:\GitHub\ai-inbox\docs\always-on-relay-gap-check.md`
  - **執行步驟**：
    1. 檢視 `C:\GitHub\agent-relay` 現有訊息收件與分派邏輯，確認是否已處理「重複事件 ID 去重（dropped）」與「同一串流單一 worker 鎖定」。
    2. 檢視目前向使用者／主對話回報結果的機制，評估是否需要加入 Outbox 靜默原則（批次彙整、節流不洗版）與 Deferred Tool Calls 暫停續跑規範。
    3. 將現況對照結果與可選改進建議記錄於 `docs/always-on-relay-gap-check.md`（不直接修改 `agent-relay` 程式碼）。
  - **驗收標準（DoD）**：產出 `docs/always-on-relay-gap-check.md` 清楚列出 `agent-relay` 對照 `Inbox / Timers / Memory / Permissions / Outbox` 五原語的已覆蓋項目與缺口建議，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-19
  - **實作紀錄 / 證據**：docs/always-on-relay-gap-check.md：對照 agent-relay@0cabfe3 五原語逐項列出已覆蓋與缺口（附路徑:行號）與 R1–R9 建議；agent-relay 未改動
