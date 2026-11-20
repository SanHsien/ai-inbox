---
id: "2026-11-20-citrolabs-ego-lite-browser-handoff-eval"
title: "Facebook 實測評估：Ego Lite（citrolabs/ego-lite）人機協作瀏覽器與 handOff 機制及安全邊界"
source_url: "https://www.facebook.com/rh.jaine/posts/pfbid028zGYYj4nJCQ7B1Ywgt7aqPuSAm1FLJuWZdQMLs7mRSHMscxxpgEfR7NwmsxY87aAl"
source_platform: "Facebook / GitHub"
author: "簡瑞華 / citrolabs"
github_repo: "https://github.com/citrolabs/ego-lite"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 2
source_replies: 5
source_reviewed_at: "2026-11-20"
status: done
cluster: 3
cluster_role: "人機協作瀏覽器"
short_title: "Ego Lite協作瀏覽器"
tags:
  - ego-lite
  - browser-automation
  - human-in-the-loop
  - gemini-cli
  - antigravity
  - facebook
---

# Facebook 實測評估：Ego Lite（citrolabs/ego-lite）人機協作瀏覽器與 handOff 機制及安全邊界

- **來源貼文**：[Facebook 簡瑞華貼文（`10235142301633921`）](https://www.facebook.com/rh.jaine/posts/pfbid028zGYYj4nJCQ7B1Ywgt7aqPuSAm1FLJuWZdQMLs7mRSHMscxxpgEfR7NwmsxY87aAl)（原分享連結 `https://www.facebook.com/share/1DjrSB6VbN/`）
- **官方 GitHub 與下載**：[`citrolabs/ego-lite`](https://github.com/citrolabs/ego-lite) ｜ [`https://lite.ego.app/`](https://lite.ego.app/)
- **作者教學與成果示範**：[Ego Lite × Gemini / Antigravity 指南](https://jrh2025.github.io/teaching_resources/ego-lite-gemini-antigravity-guide.html) ｜ [早安圖粉專月報成果](https://jrh2025.github.io/teaching_resources/good-morning-posts-2026-11.html)
- **發布平台 / 作者**：`Facebook` / `簡瑞華`
- **分析日期**：`2026-11-20`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 原始資料盤點（主文、2 張長截圖與 5 則留言）

- **主貼文核心**：推薦開源人機協作瀏覽器 `Ego Lite`（CLI 指令 `ego-browser`），主打不搶佔主滑鼠視窗、匯入既有瀏覽器登入狀態、遇雙重驗證自動 `handOff` 交給人類接力、以及語意快照省 token 與動態同步最新指南；作者並以「一句話整理 Facebook 粉專 11 月全部 43 篇貼文成互動式 HTML」為實戰範例。
- **作者上傳截圖（共 2 張，皆已點開轉錄）**：
  - **圖片 1（1282×3267 成果網頁截圖）**：展示實際產出的《早安圖分享 — 2026 年 11 月貼文完整簡介》單頁報告（涵蓋 43 篇貼文統計、每日分佈、Top 5 排行、非典型專題與可搜尋圖鑑），證實其資料擷取與前端整理實效。
  - **圖片 2（1348×3110 技術手冊截圖）**：詳載實測版本 `ego-browser 0.6.3.17`（內建 Chromium 156、Node v24.22.1、Skill `v2.2.1`），涵蓋 `TaskSpace` 隔離架構、`task.handOff()` 流程、Windows/macOS 安裝與 `ego-browser import` / `upgrade` / `skill` 用法。
- **網友回應與查證（5/5 則全讀）**：
  - **王志賢留言反駁**：提出「可惜 windows 還沒實裝」。
  - **外部搜尋核實**：經查證 `citrolabs/ego-lite/releases`、`lite.ego.app` 與 WinGet（`CitroLabs.EgoLite`），**Windows 發行版已實際推出**，與作者圖片 2 實測紀錄相符，該網友反駁屬舊版本印象。
  - 其餘留言（`Neville Yu` 等）為正向使用回饋（「用很久了，不錯用」）。

---

## 2. 對現有系統的啟發與資安風險評估

- **架構價值（相較傳統 Playwright / 無登入 `browser` subagent）**：
  - 本機 Antigravity 雖已內建 `browser` subagent 處理公開頁面讀取，但對於**「需帳號登入／2FA 接力」**或**「交由 Claude Code / Codex CLI 從終端機調用」**的網頁工作流程，`Ego Lite` 的 **`TaskSpace` 獨立分頁不搶焦點**、**`task.handOff()` 人機接力**與 **`ego-browser skill` 隨版本吐出最新 API 指南**三項設計具有明確互補價值。
- **嚴格資安邊界（不可直接匯入主瀏覽器 Cookie）**：
  - `ego-browser import` 支援直接匯入本機 Chrome / Edge / Brave 設定檔。依據全域協作規範硬閘門：**不可把含有密碼管理器、網銀、工作憑證的主瀏覽器 Cookie 暴露給外部工具或不可信網頁環境**。若未來導入測試，必須建立獨立低權限測試設定檔，不可直接匯入日常主 Profile；Skill 檔案亦須先通過安全檢查工具。

- **原始碼查證註記（2026-11-20，Claude Code，審查 commit `f499162`，詳見 [`docs/ego-lite-security-eval.md`](../docs/ego-lite-security-eval.md)）**：
  - 「開源」只涵蓋驅動 SDK 與技能（MIT）；瀏覽器本體、`ego-browser` 啟動器、Chrome 資料匯入與更新都在不開源的應用程式裡，版本數字（`0.6.3.17`、Chromium 156、Node v24.22.1）與 `ego-browser import` 子指令在 repo 內查不到，列為未查證。
  - `TaskSpace` 隔離的是分頁與控制權，不是登入狀態：Space 與使用者共用同一個設定檔的 Cookie，agent 腳本可用 `page.cdp()` 讀到整個設定檔的 Cookie。
  - `handOff` 不是瀏覽器自動偵測兩步驟驗證，而是指引要求 agent 自行判斷後呼叫 `task.handOff()`；接回控制權只靠提示文字約束。
  - GitHub Releases 的附件只有 SDK 壓縮檔；Windows 安裝檔在 `cdn.ego.app` 與 WinGet。「Windows 版已推出」成立，但 repo 的 CI 沒有 Windows 執行環境。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261120-01`**｜**[優先級：低]** 唯讀審查 `citrolabs/ego-lite` 安全性、授權與 Windows CLI `handOff` 流程評估
  - **目標範圍**：`C:\GitHub\_sandbox\ego-lite-audit` 與 `C:\GitHub\ai-inbox\docs\ego-lite-security-eval.md`
  - **執行步驟**：
    1. 僅以唯讀方式檢視 `citrolabs/ego-lite` 倉庫授權、原始碼與 `ego-browser` Skill 包內容，並執行 `python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack <Skill目錄>` 靜態安全檢驗。
    2. 確認其 `TaskSpace` 隔離與 `ego-browser import` 的本機資料讀寫行為是否符合最小權限要求（明確驗證不會未經允許存取主瀏覽器敏感憑證）。
    3. 整理與本機現有 Playwright / `browser` subagent 的適用分工建議於 `docs/ego-lite-security-eval.md`（本評估任務不將主瀏覽器 Cookie 匯入任何外部工具）。
  - **驗收標準（DoD）**：產出 `docs/ego-lite-security-eval.md`，完整記錄安全掃描結果、授權條款與與現有瀏覽器工具之分工結論，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-20
  - **實作紀錄 / 證據**：產出 docs/ego-lite-security-eval.md（審查 commit f499162，2026-11-20 唯讀靜態檢閱，未安裝未執行）；verify_agent_skill_pack_safety 整庫結束碼 1（FAIL 1 經人工判為誤判、REVIEW 2）；結論：SDK 為 MIT 但瀏覽器本體閉源，Space 與使用者共用設定檔 Cookie 且 page.cdp 不過濾方法，不符最小權限，不安裝、不匯入，僅借鏡 handOff 流程與清除範圍對照表
