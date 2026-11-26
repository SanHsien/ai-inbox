---
id: "2026-11-26-claude-md-global-papercuts-log-pattern"
title: "CLAUDE.md 實戰模式評析：跨會話共享的《開發小問題日誌（papercuts.md）》與零常駐 Token 故障查詢觸發"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "使用者直接提供全文（CLAUDE.md 規則片段，無原始 URL）"
author: "未具名（使用者提供）"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: unavailable
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
source_review_note: "使用者於對話直接提供 CLAUDE.md「小問題（papercuts.md）」規則片段原文（無原始來源 URL）。"
status: pending
cluster: 1
cluster_role: "跨會話小問題日誌"
short_title: "Papercuts跨會話踩坑日誌"
tags:
  - claude-md
  - context-budget
  - troubleshooting
  - cross-session-memory
  - dev-experience
---

# CLAUDE.md 實戰模式評析：跨會話共享的《開發小問題日誌（papercuts.md）》與零常駐 Token 故障查詢觸發

- **來源**：使用者直接提供 `CLAUDE.md` 規則原文：
  > `Maintain ~/code/papercuts.md, a global log shared by all my Claude sessions of anything that slowed down development. When you lose time to one mid-session, append date · symptom · fix · project. Check this file first when tooling fails mysteriously.`
- **分析日期**：`2026-11-26`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/agent-memory-and-prompting-best-practices.md`](../docs/agent-memory-and-prompting-best-practices.md)（Agent 記憶與提示詞最佳實踐目標文件）
  - [`notes/2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts.md`](./2026-11-22-bnext-claude-17-advanced-tips-memory-projects-prompts.md)（Agent Memory「存策略、不膨脹常駐規則」原則）

---

## 0. 核心機制拆解

1. **解決「遠距監督時代」的隱形時間流失**：
   - 當開發者不再逐行盯著會話時，Agent 常在背景撞到相同的環境小坑（例如 Windows 編碼、PATH 漏掛、特定套件版本衝突、Shell 語法差異），當場修好後便隨會話結束而遺忘，下一輪又重踩一次。
2. **單行結構化追加（`date · symptom · fix · project`）**：
   - 強制極簡四欄格式，避免寫成長篇檢討報告，降低讀寫阻力。
3. **「失敗時才先讀」的延遲載入觸發（Zero Baseline Token Cost）**：
   - 關鍵在最後一句：`Check this file first when tooling fails mysteriously.`——不把零碎環境坑塞進每次開局必載入的 `CLAUDE.md`／`AGENTS.md`，而是維持 `CLAUDE.md` 只放一條 2 行的指標，**僅在工具異常卡關時才去查這張表**，兼顧上下文預算與跨會話排錯速度。

---

## 1. 與本專案現有架構的對照與啟發

- 本機已設有跨 AI 共用資產庫 `C:\GitHub\agent-assets`（`knowledge/` 與 `rules/AGENTS.md`）以及 [`docs/agent-memory-and-prompting-best-practices.md`](../docs/agent-memory-and-prompting-best-practices.md)。
- 將環境坑拆成「**常駐規則（極簡、每輪載入）**」與「**`papercuts.md` 故障快查表（僅在工具莫名失敗時讀取、單行 `date · symptom · fix · project`）**」，可避免全域規則檔隨時間膨脹（對應 `verify_agent_lean_rules.py` 的精簡規則精神）。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261126-05`**｜**[優先級：低]** 將「跨會話小問題日誌（`papercuts.md`：`date · symptom · fix · project`＋失敗時優先按需讀取）」模式補入 `docs/agent-memory-and-prompting-best-practices.md`，並評估於 `agent-assets` 建立對應知識檔
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\agent-memory-and-prompting-best-practices.md`（收錄於集群 1；可選延伸至 `C:\GitHub\agent-assets\knowledge\`）
  - **執行步驟**：
    1. 在 `docs/agent-memory-and-prompting-best-practices.md` 新增「按需載入之跨會話故障快查日誌（Papercuts Log）」小節，記錄四欄格式與雙觸發點（卡關耗時即追加、工具莫名失敗優先讀取）。
    2. 說明與常駐全域規則（`CLAUDE.md` / `AGENTS.md`）的上下文預算分層原則：高頻不變紀律放常駐規則，零星環境／工具坑放按需查詢的 `papercuts.md`。
  - **驗收標準（DoD）**：`docs/agent-memory-and-prompting-best-practices.md` 完成上述章節補充，且 `python tools/verify_inbox.py` 驗證通過。
