---
id: "2026-11-28-shuhao-chang-four-claude-plugins-skillspector"
title: "Threads「四個 Claude Code 外掛與 SkillSpector 裝前安檢」查證與技術評估"
source_url: "https://www.threads.com/@eric_chang_tinyamzseller/post/DgOfrVmEnhC"
source_platform: "Threads (@eric_chang_tinyamzseller)"
author: "SHUHAO CHANG (@eric_chang_tinyamzseller)"
analyzed_at: "2026-11-28"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_reviewed_at: "2026-11-28"
source_images: 0
source_replies: 12
source_review_note: "已完整讀取原貼文正文、作者與 @alert.human 全部 5 則技術往返對話、登入牆前可見共 12 則回覆，並以 gh api 唯讀查證 4 個 GitHub 倉庫 metadata 與 README；貼文總回覆計數 13 則中尚有部分列位遭 Threads 登入彈窗遮擋無法往下捲動。"
tags:
  - claude-code
  - skillspector
  - ponytail
  - freellmapi
  - lemo-opuscar
  - skill-security
  - threads
status: pending
cluster: 3
cluster_role: "四個外掛與安檢"
short_title: "Claude四外掛與Skill安檢"
---

# Threads「四個 Claude Code 外掛與 SkillSpector 裝前安檢」查證與技術評估

- **來源連結**：[SHUHAO CHANG (@eric_chang_tinyamzseller) Threads 貼文](https://www.threads.com/@eric_chang_tinyamzseller/post/DgOfrVmEnhC)（原分享網址 `https://www.threads.com/share/_7XGwBwQv`，`2026-11-27` 上午 9:25 發布；1 萬次瀏覽、133 讚、13 回覆、32 轉發、288 分享）
- **分析日期**：`2026-11-28`
- **當前狀態**：`🔴 待辦 (Pending)`

---

## 0. 原始資料盤點與 GitHub 實查

> 以無頭瀏覽器讀取貼文正文與登入牆前可見之 12 則回覆（含作者與 `@alert.human` 的 5 則實測討論），並透過 `gh api` 唯讀查證文中 4 個專案之星數、授權與 README 邊界。

| 貼文推薦項目 | GitHub 倉庫 | 授權 / 星數（`2026-11-28` `gh api`） | README 實查定位與風險邊界 | 本庫既有狀態 |
| --- | --- | --- | --- | --- |
| 1. `FreeLLMAPI` | [`tashfeenahmed/freellmapi`](https://github.com/tashfeenahmed/freellmapi) | `MIT` / `59,402` stars | 聚合 87 家免費 LLM 供應商、1,313 個免費端點於單一 `/v1` OpenAI 相容路由器（加密存金鑰、自動故障轉移、單 key 用量追蹤）；**明言「Personal experimentation only」**，多供應商免費額度與 ToS 變動高，不適合作為正式生產依賴。 | 尚未收錄 |
| 2. `Lemo Opuscar` | [`lemomo-ai/lemo-opuscar`](https://github.com/lemomo-ai/lemo-opuscar) | `NOASSERTION` / `22,050` stars | 免影片模型、純程式碼生成 99 種電影風格短片（為 Claude Code 設計，註記以 Claude Fable 5.2 審計改進、建議 `/effort high`）。**授權顯示 `NOASSERTION`，搬運前須先核對授權條款。** | 可對接 [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio) 設計參考 |
| 3. `Ponytail` | [`DietrichGebert/ponytail`](https://github.com/DietrichGebert/ponytail) | `MIT` / `200,243` stars | 主打讓 AI 像「最懶的資深工程師：少寫程式、高風險邏輯附測試」（`works with 20 agents`、npm `@dietrichgebert/ponytail`）。 | 舊筆記 [`2026-11-08-dustin-gmat-danyuchn-claude-work-mode-session-modes`](./2026-11-08-dustin-gmat-danyuchn-claude-work-mode-session-modes.md) 曾被留言提及省 token 但當時未知其詳 |
| 4. `SkillSpector` | [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector) | `Apache-2.0` / `27,972` stars | NVIDIA 技能安全掃描器（Python 3.12+）；README 數據指 31,132 份研究樣本中 **26.1% 含弱點、5.2% 具潛在惡意意圖**。 | **已納入全域規範與 `SanHsien/agent-safety-checks` 前置流程** |

- **留言區重點（`@alert.human` 與作者往返）**：
  - `@alert.human` 詢問 `SkillSpector`（71 種弱點模式）實際掃描誤報率；作者回應「把它當機場安檢門，嗶一聲不代表你是壞人，有標記仍會點進去看那幾行」，並坦承自己樣本尚少未敢排名常見弱點。此觀點與本庫既有的 [`2026-11-15-cloudflare-security-audit-skill`](./2026-11-15-cloudflare-security-audit-skill.md)（資安教材型 Skill 曾被誤報為 CRITICAL）實測一致。
  - `@scottvision6` 提問 `Lemo Opuscar` 做影片的 token 消耗量（尚無作者回覆）。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：Threads 用戶 `SHUHAO CHANG (@eric_chang_tinyamzseller)`。
- **What**：精選四個針對不同面向的 Claude Code 輔助工具——免費模型路由（`FreeLLMAPI`）、純程式碼電影短片（`Lemo Opuscar`）、精簡寫碼省 Token（`Ponytail`）與裝前安全掃描（`SkillSpector`）。
- **Why**：強調「缺的不是更多外掛，而是裝之前先檢查的習慣」。
- **How**：把安全檢查（`SkillSpector`）放在採用工作流之前，其餘三項依需求分別處理多模型免費額度、程式碼動畫生成與精簡重構。
- **When & Where**：選用第三方 Claude Code / Agent Skills 與模型工具前的篩選與安全檢核情境。
- **Key Metrics / Numbers**：`SkillSpector` 31,132 樣本中 26.1% 含弱點、5.2% 疑惡意；`Ponytail` 200k stars；`FreeLLMAPI` 59k stars（87 家／1,313 端點）；`Lemo Opuscar` 22k stars（99 種電影風格）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 全域安全規範：`SkillSpector` 與 `SanHsien/agent-safety-checks` 早已成為強制門檻。
  - [`docs/agent-memory-and-prompting-best-practices.md`](../docs/agent-memory-and-prompting-best-practices.md)（`Ponytail` 精簡寫碼／高風險附測試原則）。
  - [`docs/code-as-video-creative-patterns.md`](../docs/code-as-video-creative-patterns.md) 與 [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)（`Lemo Opuscar` 99 種純程式碼電影風格參考）。
- **落差與採納判斷**：
  - **`SkillSpector`**：已在本機流程落地，延續「工具標警訊 → 人工複核」立場，不新開任務。
  - **`FreeLLMAPI`**：明確標記僅限個人實驗且仰賴大量免費層聚合，不列入穩定架構依賴，僅留筆記備查。
  - **`Ponytail` 與 `Lemo Opuscar`**：兩者皆具高關注度與明確應用場景（補齊 2026-11-08 筆記對 `ponytail` 的未知空白，並對照 `code-as-video` 風格設計），值得開立**唯讀檢閱**任務（先過授權與安全檢查，不直接安裝）。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261128-04`**｜**[優先級：低]** 唯讀檢閱 `DietrichGebert/ponytail`（MIT），評估其省 Token／「少寫程式＋高風險附測試」提示設計並補充至 `docs/agent-memory-and-prompting-best-practices.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\agent-memory-and-prompting-best-practices.md`（收錄於集群 1；僅透過 GitHub API 唯讀檢閱規則與實作，不執行 `npm`／安裝腳本）
  - **具體做法**：讀取 `DietrichGebert/ponytail` 的主要提示詞／規則檔與安全邊界，補齊 2026-11-08 筆記遺留之「`ponytail` 實際機制」空白，並萃取可重用規則寫入 `docs/agent-memory-and-prompting-best-practices.md`。
  - **驗收標準（DoD）**：`docs/agent-memory-and-prompting-best-practices.md` 完成增補且附來源檔案檢閱紀錄，`python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：
  - **實作紀錄 / 證據**：

- [ ] **`T-20261128-05`**｜**[優先級：低]** 唯讀檢閱 `lemomo-ai/lemo-opuscar`（先核對授權條款），萃取無影片模型之電影風格編排原則補入 `docs/code-as-video-creative-patterns.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\code-as-video-creative-patterns.md`（收錄於集群 2；因 repo 授權為 `NOASSERTION`，若無明確開源授權則僅記錄高階風格架構概念，嚴禁搬運程式碼或直接安裝）
  - **具體做法**：透過 GitHub API 檢查 `lemomo-ai/lemo-opuscar` 的實際授權檔案、風格定義結構與高 effort／token 消耗說明，將可跨模型復用的編排概念補充至 `docs/code-as-video-creative-patterns.md` 供 `code-as-video-studio` 參考。
  - **驗收標準（DoD）**：`docs/code-as-video-creative-patterns.md` 完成增補並寫明授權核對結果，`python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：
  - **實作紀錄 / 證據**：
