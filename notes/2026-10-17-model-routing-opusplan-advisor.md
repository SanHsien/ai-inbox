---
id: 2026-10-17-model-routing-opusplan-advisor
title: "Claude 混合模型分工實踐：/model opusplan 與 /advisor 雙軌架構緩解 Token 焦慮"
source_url: "https://www.threads.com/@mors_tw/post/DelWFwWEibA"
source_platform: "Threads"
author: "Mors (@mors_tw)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "模型路由與配額分流"
short_title: "/model opusplan 與 /advisor 雙軌架構"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "貼文顯示 15 則回覆，未登入只讀到 11／15 則；貼文無圖（0／0 張）"
source_images: 0
source_replies: 11
tags:
  - model-routing
  - claude-code
  - token-optimization
  - agent-architecture
  - cost-efficiency
---

# Claude 混合模型分工實踐：/model opusplan 與 /advisor 雙軌架構緩解 Token 焦慮

- **來源貼文**：[Threads @mors_tw 貼文](https://www.threads.com/@mors_tw/post/DelWFwWEibA)
- **發布者**：`Mors (@mors_tw)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`⚪ 封存不做 (Archived)`
- **相關交叉參照**：[`notes/2026-10-17-cross-cli-subagent-orchestration-space-bunny.md`](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md)

---

## 0. 原始資料盤點

> 2026-11-16 重審：貼文文字與未登入看得到的 11 則留言（含作者 5 則回覆）都讀過。貼文顯示 15 則回覆，其餘 4 則未登入看不到。

- **作者圖片**：無。這是純文字貼文。
- **作者留言補充**：5 則都是「感謝補充／分享」，等於認同下面網友的更正，沒有自己加新內容。
- **網友留言重點**：
  - `ryan_ilili`：opusplan 一年前就有了。`b95505017` 附上 Claude Code 團隊成員在 X 的貼文連結，說去年（2025 年）8 月就有。→ 貼文開頭「最近 Claude 加了一個新的 model 叫 opusplan」**不對**，作者也回了感謝補充。
  - `kaka.terminal`：opusplan 是看模式切換的——在 plan mode 裡才用 Opus，退出來動手做就換 Sonnet；要讓 Opus 出場得先按 Shift+Tab 進 plan mode 再下指令。
  - `alert.human`：除了切模型，開 prompt caching 也省，規劃階段的 context 在執行階段被反覆引用時命中快取。（這則語氣像自動回覆帳號，內容是常識，未另外查證。）
  - `an.ler.13`：context 管理與 workflow 規劃做好，省 token 的效果也很明顯。
- **對分析的影響**：
  - 1.1 節補上「opusplan 不是新功能，2025 年 8 月就有」，並補貼文原有但原筆記漏掉的背景：作者說舊的 4 系列模型不穩，以前是「Fable 設計、Opus 執行」，Opus 5 之後變穩才改成現在的組合。
  - 1.2 節第 1 點補上觸發條件：不進 plan mode，opusplan 全程就是 Sonnet。原筆記寫「自動啟用旗艦模型」容易讓人以為不用切模式。
  - 兩個任務原本就是「不做」，結論不變。`T-20261017-12` 的做法（別名帶 `--model opusplan`）若日後重開，要記得光設模型不夠，還得進 plan mode。

---

## 1. 核心內容摘要與模型分工機制

### 1.1 核心主張與技術痛點
- **痛點**：AI Coding Agent 每天頻繁執行大量讀檔、改字、跑測試等機械性工作。若全時段無腦使用頂級旗艦模型（如 Opus），Token 消耗速度極快、容易撞到配額上限並引發「Token 焦慮」；但若全時段降級使用輕量模型（如 Sonnet 或 Flash），又容易在架構設計或複雜重構時「降智」出錯。
- **解法（模型動態分工）**：**「大腦設計用頂級模型，四肢執行交給快省模型」**。
  - 作者分享當前最穩定的組合為：**`/model opusplan`** 搭配 **`/advisor fable`**，聲稱可覆蓋 90% 的複雜工程需求，兼顧頂級智商與成本控制。
  - **背景（貼文原文）**：作者說這種分工概念早就有人做，但舊的 4 系列模型不夠穩，複雜工作他以前是「Fable 設計、Opus 執行」；Opus 5 之後穩定度變高，日常使用上 Opus 5.5 與 Fable 5.1 差異不大，才改用現在的組合。
  - **更正（留言）**：貼文說 opusplan 是「最近新加的」，網友指出 2025 年 8 月就有了，作者回覆認同。

### 1.2 兩大分工維度對比（階段分工 vs 決策求助）

```text
【模式 1：階段性切換 — /model opusplan】
[使用者輸入任務]
      │
      ▼
┌──────────────┐
│  Plan Mode   │ ──(調用 Opus / Fable 頂級架構大腦，產出縝密設計計畫)
└──────┬───────┘
      │ 自動無縫切換
      ▼
┌──────────────┐
│  Exec Mode   │ ──(交由 Sonnet / 執行模型跑指令、編輯檔案、執行測試)
└──────────────┘

【模式 2：決策時求助 — /advisor 顧問架構】
[主力模型 (Sonnet)] ──平時高速執行常規代碼與工具呼叫
       │
       ▼ 遇到複雜邏輯、架構分歧或重構疑慮
┌──────────────┐
│ Advisor 求助 │ ──(動態向 Opus / Fable 請求顧問指導，決策完畢返回主力)
└──────────────┘
```

1. **`opusplan`（Plan-then-Execute 階段分工）**：
   - 在計畫階段（Plan Mode）自動啟用旗艦模型（如 Opus）做深度推理與架構拆解；一旦計畫拍板進入實作，自動切換為高性價比模型（如 Sonnet）寫代碼與執行驗收。
   - **觸發條件（留言補充）**：切換是跟著模式走的。要先按 Shift+Tab 進 plan mode，Opus 才會出場；沒進 plan mode 直接下指令，全程都是 Sonnet。
2. **`advisor`（On-demand Escalation 顧問模式）**：
   - 輕量主力模型在執行過程中，遇到關鍵決策點時主動向後台頂級顧問（如 Fable / Opus）請益，避免整段 Session 浸泡在昂貴模型上下文。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **編排架構**：現有的 `orchestration`（Antigravity-native risk-gated routing）與 `token-optimizer` 正是實踐此思維的典型。
  - **跨模型分工現狀**：目前的子代理分工（`advisor-flash-implementer`、`advisor-pro-implementer`、`advisor-pro-reviewer`）與此概念完全一致。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **強化 Claude Code 與 CLI 的默認設定**：在日常啟動 Claude Code 時，明確將 `opusplan` 或雙軌路由寫入預設工作別名（Aliases）或啟動參數，避免手動輸入。
    2. **對標評估 Antigravity 中的 Flash / Pro 階層配置**：持續驗證在 Antigravity 體系下，以 Flash 做實作批次（Mechanical Batches）、Pro 做規劃與 Review 的 Token 節約幅度。
  - **不適用 / 需注意的部分**：
    - 模型名稱會隨版本迭代（如 Opus 5、Fable 5.1 等），規則與腳本設計應使用「抽象階層」（Planner Tier / Executor Tier），避免寫死特定過期模型字串。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261017-11`**｜**[優先級：低]** 整理 Claude Code / Antigravity 混合模型路由指南，納入 `token-optimizer` 規則手冊
  - **目標範圍**：`~\.gemini\config\skills\token-optimizer\SKILL.md`
  - **狀態**：⚪ 不做（混合模型分工已於 agent-relay 額度感知顧問與 token-optimizer 完整落地，無須重複整理）
  - **具體實作步驟**：
    1. 檢視現有 `token-optimizer` 技能說明。
    2. 增補章節「混合模型分工策略（Hybrid Routing Strategy）」：詳解 `opusplan`（階段分工）與 `advisor`（動態求助）的觸發時機與指令語法。
    3. 明列具體省 Token 數值期望（規劃階段僅佔總 Context 10-20%，其餘由輕量模型承擔，整體節省可達 60-70% 費用）。
  - **驗收標準（DoD）**：更新完成，並驗證各 Agent 在派工與日常開發時能優先推薦或套用階層化模型。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261017-12`**｜**[優先級：低]** 評估本地 Claude Code 終端別名與自定義啟動腳本配置
  - **目標範圍**：`環境工具鏈 / CLI 啟動配置`
  - **狀態**：⚪ 不做（CLI 啟動已由 agent-relay 派工器與 Windows Terminal 整合標準化，不維護散落的終端別名腳本）
  - **具體實作步驟**：
    1. 檢測本地 PowerShell profile（`$PROFILE`）或環境設定。
    2. 建立便捷指令別名（例如 `claude-plan` 自動附加 `--model opusplan`）。
    3. 實測啟動並確認終端能正確辨識並進入混合模型路由狀態。
  - **驗收標準（DoD）**：在 PowerShell 執行新別名能成功以 `opusplan` 模式啟動 Claude Code。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
