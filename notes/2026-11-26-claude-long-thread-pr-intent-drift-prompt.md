---
id: "2026-11-26-claude-long-thread-pr-intent-drift-prompt"
title: "長對話收斂與 PR 意圖漂移稽核提示詞評析：無術語時序敘事＋行內粗體標註偏離項目"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "使用者直接提供全文（實戰 Prompt 片段，無原始 URL）"
author: "未具名（使用者提供）"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: unavailable
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
source_review_note: "使用者於對話直接提供實戰提示詞原文與使用情境（無原始來源 URL）。"
status: pending
cluster: 1
cluster_role: "PR意圖漂移稽核"
short_title: "長對話PR意圖漂移稽核"
tags:
  - prompt-engineering
  - intent-drift
  - pr-review
  - context-management
  - claude-code
---

# 長對話收斂與 PR 意圖漂移稽核提示詞評析：無術語時序敘事＋行內粗體標註偏離項目

- **來源**：使用者直接提供實戰 Prompt 原文：
  > `In your own words, without jargon, narrate each step in the order it actually happens, and bold inline anything in the current PR that has drifted from my most recently stated intent.`
- **分析日期**：`2026-11-26`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/agent-memory-and-prompting-best-practices.md`](../docs/agent-memory-and-prompting-best-practices.md)（Agent 記憶與提示詞最佳實踐目標文件）
  - [`notes/2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts.md`](./2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts.md)（長對話防走偏與提示詞紀律）

---

## 0. 原始提示詞四重機制拆解

1. **`In your own words, without jargon`（禁止術語複述）**：
   - 迫使模型用白話重述因果決策，而非照抄檔名、符號名或工程黑話來掩蓋實作盲點。
2. **`narrate each step in the order it actually happens`（依實際發生時序敘事）**：
   - 強制按執行順序（Step 1 → Step 2 → Step 3）還原程式或代理的真實決策路徑，而不是按資料夾或模組分塊摘要，讓隱藏的繞路、假設或降級一眼現形。
3. **`against my most recently stated intent`（以「最新明確意圖」為準）**：
   - 長對話中需求常經多輪修正；指定對照「**最近一次陳述的意圖**」，避免 Agent 拿早期已被推翻的討論當作合規依據。
4. **`bold inline anything in the current PR that has drifted`（行內粗體標註漂移）**：
   - 將「審閱差異」直接嵌入敘事流中，不另起抽象免責聲明，讓審查者掃視粗體即可定位所有範圍外改動或意圖偏離。

---

## 1. 與本專案現有架構的對照與啟發

- 本庫規則已要求「計畫中途發現方向錯了就講出來並修正計畫，不要默默做成另一個樣子」，但缺少一條在**長對話結束、準備 Merge PR 前**一鍵對帳的標準提示詞。
- 這句單行 Prompt 零依賴且跨平台（Claude Code / Codex / Antigravity 皆可直接貼用），極適合收錄進 [`docs/agent-memory-and-prompting-best-practices.md`](../docs/agent-memory-and-prompting-best-practices.md) 作為「長對話收斂與 PR 意圖漂移稽核」標準句式。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261126-04`**｜**[優先級：低]** 將「無術語時序敘事＋行內粗體標註偏離最新意圖」PR 稽核提示詞補入 `docs/agent-memory-and-prompting-best-practices.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\agent-memory-and-prompting-best-practices.md`（收錄於集群 1）
  - **執行步驟**：
    1. 在 `docs/agent-memory-and-prompting-best-practices.md` 新增「長對話收斂與 PR 意圖漂移稽核（Post-Session Intent-Drift Audit）」小節，收錄原文句式與四項設計原理（去術語、時序敘事、對齊最新意圖、行內粗體標註漂移）。
    2. 註明可搭配閱讀實際 `git diff` 使用，避免模型僅憑對話記憶回答。
  - **驗收標準（DoD）**：`docs/agent-memory-and-prompting-best-practices.md` 完成上述句式與限制補充，且 `python tools/verify_inbox.py` 驗證通過。
