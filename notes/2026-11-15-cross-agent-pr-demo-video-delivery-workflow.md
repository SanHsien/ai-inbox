---
id: "2026-11-15-cross-agent-pr-demo-video-delivery-workflow"
title: "跨 Agent PR + Demo 影片交付工作流評估：Grok Bot 案例拆解與本機免新 Repo 整合方案"
source_url: "https://www.aiposthub.com/grok-bot-cursor-coding-pr-video-update/"
source_platform: "Blog / AI Post Hub"
author: "AI Post Hub（Grok Bot + Cursor Cloud Agent 案例）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 1
cluster_role: "PR錄影證據交付"
short_title: "跨Agent PR錄影交付"
tags:
  - pr-automation
  - demo-video
  - playwright
  - ffmpeg
  - gh-cli
  - agent-relay
  - cross-agent-workflow
---

# 跨 Agent PR + Demo 影片交付工作流評估：Grok Bot 案例拆解與本機免新 Repo 整合方案

- **來源連結**：[AI Post Hub: Grok Bot + Cursor PR 與 Demo 影片工作流](https://www.aiposthub.com/grok-bot-cursor-coding-pr-video-update/)
- **發布平台 / 作者**：`AI Post Hub`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：Grok Bot 整合 Cursor Cloud Agent，將傳統「Agent 回報我改好了」升級為「**自動拆解派工 $\rightarrow$ 開出 PR $\rightarrow$ 附帶實機操作 Demo 影片與修改摘要 $\rightarrow$ 人類審核合併**」（官方示範為修復 CSV 匯出逾時，帶回 2 個 PR、進度提示與 1 段操作 Demo）。另介紹官方 Engineering Bot 角色範本（Projects Manager / QA Bot / Engineering Lead / Nightly Audit Engineer）。
- **Why**：單純「貼 Diff + 說我改好了」讓人類驗收成本極高；附帶操作影片能讓 PM、設計師或忙碌的維護者幾十秒內確認畫面行為是否符合預期（但貼文亦誠實提醒：**Demo 影片 $\neq$ 測試通過**，邊界條件與權限仍須靠測試與 Code Review）。
- **How（跨 Agent 通用等效技術拆解，非 Grok Bot 專利）**：
  - 經實查業界開源實作（Playwright `recordVideo`、Testreel / Argo、`charmbracelet/vhs`）與本機工具現況，**所有支援 Tool Use / Shell 的 Agent（Claude Code、Codex CLI、Antigravity、Hermes、Pi）皆可共用同一套標準流程**：

```text
[任一 Agent 完成實作 (Claude / Codex / Antigravity / Hermes)]
       │
       ├─ 1. 確定性測試閘門：跑通單元／整合測試並輸出 Log（不可只錄影不測）
       │
       ├─ 2. 視覺證據錄製（依介面類型擇一）：
       │     ├─ Web UI：Playwright BrowserContext({ recordVideo }) ─▶ .webm
       │     └─ CLI / 終端工具：charmbracelet/vhs 或 asciinema
       │
       ├─ 3. 後製壓縮：本機 ffmpeg.exe (已安裝 9.0.2) 轉輕量 .mp4 (去空白幀 / 控制 <=100 MiB)
       │
       └─ 4. 交付閉環：
             ├─ 單倉 PR：gh pr create --attach ./demo.mp4 (本機 gh 2.104.0 已原生支援內嵌播放器)
             └─ 跨代理派工：agent-relay send --kind result --refs <PR_URL> <demo.mp4>
```

---

## 2. 本機與開源資源盤點（2026-11-15 實查）

- **本機已就緒的零成本工具鏈（無須新裝重型平台）**：
  1. **`gh` CLI `2.104.0`**（支援 >= `2.99.0` 新增之 `--attach` 旗標）：可直接把 `.mp4`/`.webm`/`.mov`/`.png`（上限 100 MiB）上傳至 GitHub 資產並自動改寫 PR Markdown 內嵌播放器。
  2. **`ffmpeg` `9.0.2-full_build`**（已安裝於 WinGet 目錄）：負責 `.webm` $\rightarrow$ `.mp4` 轉檔、裁切無效等待幀與壓縮體積。
  3. **`playwright.exe`**（已安裝於 `C:\Python314\Scripts\playwright.exe`）：透過 `recordVideo` 錄製可重現的操作影片。
- **開源生態補充資源（僅作參考，採納前須經審查）**：
  - `greentfrapp/testreel`（108 stars）：LLM 透過 Playwright 錄製產品展示影片。
  - `howseen-ai/claude-motion-design`（826 stars）：HTML + Playwright + ffmpeg 純程式動態展示。
  - `charmbracelet/vhs`：以 `.tape` 宣告式腳本錄製 CLI 終端操作影片／GIF（適合 `agent-relay`、`agent-advisor` 這類純 CLI 工具）。

---

## 3. 關鍵決策評估：是否獨立成 Repo？是否優先處理？

1. **是否需要獨立建立一個新的 Repo？— 結論：`不需要`（避免過度工程）**：
   - 錄影與上傳底層（Playwright + FFmpeg + `gh pr create --attach`）皆已是成熟單兵工具且本機已就緒；派工與交接骨幹（worktree 隔離、`result` 回報、`accept` 本地複驗）已在 `SanHsien/agent-relay`；跨 Agent 通用規範則由共用 Skills 與 `SanHsien/agent-assets` 管理。
   - 若僅為了串接這三個 CLI 指令就另開一個新 Repo，只會增加多餘的版本同步與維護負擔。**最乾淨的落地方式是「寫成跨 Agent 共用的 `pr-demo-evidence` Skill（配輕量共用腳本）＋ 整合進 `agent-relay` 的 `result` 證據參考」**。
2. **是否需要優先處理？— 結論：`中優先級`（高槓桿驗收升級，排在主線穩定之後）**：
   - `agent-relay` 剛完成 `ask`/`answer` 非同步問答，核心文字派工與自動化測試驗收已暢通；PR Demo 影片對「有 Web UI／前端展示／未來接案交付給客戶看」的案型價值最高，列為**中優先級**，可搭配下一個前端專案或接案營運總綱（`T-20261115-08`）推進。

---

## 4. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-12`**｜**[優先級：中]** 建立跨 Agent 共用技能 `pr-demo-evidence`（整合 Playwright `recordVideo` + `ffmpeg` + `gh pr create --attach` 與測試證據門檻）
  - **目標範圍**：共用技能（`~/.gemini/config/skills/pr-demo-evidence/` 與 `SanHsien/agent-assets` 同步）
  - **具體做法**：
    1. 撰寫跨 Agent 通用 `SKILL.md`（適用 Claude Code / Codex / Antigravity / Hermes），規範「先跑通測試 $\rightarrow$ 錄製關鍵操作（Web 用 Playwright `recordVideo`，CLI 可選 VHS/文字錄影）$\rightarrow$ `ffmpeg` 壓縮轉 `.mp4`（<= 100 MiB、遮蔽敏感資訊）$\rightarrow$ `gh pr create --attach`（僅推個人 fork `SanHsien/<repo>`）」。
    2. 附帶一支輕量無外部框架依賴的 `ffmpeg` 轉檔／壓縮輔助腳本，並以真實小型測試頁面實跑產出 1 支有效 `.mp4` 驗證流程可行。
  - **驗收標準（DoD）**：產出 `SKILL.md` 與壓縮腳本，於 Windows 11 原生環境實跑 Playwright `recordVideo` $\rightarrow$ `ffmpeg` 轉 `.mp4` 成功產出可播放影片（並驗證測試通過才允許進入錄影）。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*

- [ ] **`T-20261115-13`**｜**[優先級：低]** 評估於 `SanHsien/agent-relay` 的 `result` 回報與 `accept` 驗收清單支援顯示 Demo 影片附件路徑（`refs` / `result` 證據整合，不另開 Repo）
  - **目標範圍**：`C:\GitHub\agent-relay`（`SPEC.md`、`agent_relay/cli.py`）
  - **具體做法**：
    1. 評估在派工 `task`（如 UI/前端任務）可選擇要求 Worker 回傳的 `result` 信封於 `refs` 附上錄影檔路徑或含 `--attach` 影片的 PR URL，於 `relay read` / `relay accept` 時高亮提示人類審閱該視覺證據。
  - **驗收標準（DoD）**：確認擴充方案不破壞既有 `envelope@1` 相容性，並通過 `agent-relay` 單元測試與 doc parity。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
