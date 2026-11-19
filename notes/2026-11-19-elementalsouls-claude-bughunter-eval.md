---
id: "2026-11-19-elementalsouls-claude-bughunter-eval"
title: "Threads 情報評估：Claude-BugHunter（elementalsouls/Claude-BugHunter）82 款資安技能包與 681 條漏洞模式庫"
source_url: "https://www.threads.com/@easyanythinghk/post/Df4B2UgAGw2"
source_platform: "Threads / GitHub"
author: "@easyanythinghk (dev) / elementalsouls"
github_repo: "https://github.com/elementalsouls/Claude-BugHunter"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: partial
source_images: 1
source_replies: 2
source_reviewed_at: "2026-11-19"
source_review_note: "主貼文與1張圖片完整讀取，4則留言中於未登入狀態讀到2則（作者續樓與1則網友回覆），其餘受Threads登入牆阻擋"
status: done
cluster: 3
cluster_role: "開源資安Skill包"
short_title: "Claude-BugHunter評估"
tags:
  - claude-code
  - security
  - bug-bounty
  - skills
  - github-trending
  - threads
---

# Threads 情報評估：Claude-BugHunter（elementalsouls/Claude-BugHunter）82 款資安技能包與 681 條漏洞模式庫

- **來源貼文**：[Threads 原貼文（`@easyanythinghk`）](https://www.threads.com/@easyanythinghk/post/Df4B2UgAGw2)（原分享連結 `https://www.threads.com/share/_iJglRl2P`）
- **官方 GitHub**：[`elementalsouls/Claude-BugHunter`](https://github.com/elementalsouls/Claude-BugHunter)（MIT License，Python，登頂 GitHub Trending Top 1，近 1 萬星）
- **發布平台 / 作者**：`Threads` / `@easyanythinghk`（`2026-11-18`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-23-claude-plugin-security-guidance.md`](./2026-10-23-claude-plugin-security-guidance.md)（Anthropic 官方 `security-guidance` 插件）
  - [`notes/2026-11-15-claude-mythos-cyber-verification-program.md`](./2026-11-15-claude-mythos-cyber-verification-program.md)（Claude Mythos 資安存取評估）

---

## 1. 原始資料盤點（主文、1 張圖卡、作者續樓與留言）

- **主貼文核心**：分享登上 GitHub Trending Top 1 的開源專案 `Claude-BugHunter`（單日 +1005 星，近萬星），主打專為 Bug Bounty 與 Red Team 打造的 Claude Code 技能包，內含 82 個安全技能包（skills）與 681 條真實漏洞報告模式（涵蓋 24 大漏洞類別）。
- **作者上傳圖片（共 1 張，Trending 資訊圖卡）**：
  - 清楚標註：`GITHUB TRENDING · TOP 1 · 2026.11.18`、`Claude-BugHunter`、`Python | ⭐ 9,989 (+1005 today) | MIT`、分類為 `Bug Bounty | Red Team | AI Security | Pentest`，並標明倉庫網址 `github.com/elementalsouls/Claude-BugHunter`。
- **作者續樓與網友留言（4 則中讀到 2 則，其餘受登入牆阻擋）**：
  - 作者續樓（`Df4B681AGo4`）：提供 GitHub 連結並詢問滲透測試最花時間的步驟。
  - 網友 `@angus_man` 回覆點讚符號 `👍🏻`。
- **官方 GitHub 倉庫核實（`elementalsouls/Claude-BugHunter`）**：
  - 專案架構：專為 Claude Code 設計，提供 `scripts/install.sh` 與 Windows PowerShell `install.ps1`。
  - 核心模組：收錄源自 HackerOne 等真實公開報告的 681 條漏洞模式，包含 M365/Entra、Okta、SharePoint、VPN 等企業攻防矩陣與「7-Question Gate」驗證門檻，並支援 HackerOne、Bugcrowd 等回報格式產出。

---

## 2. 對現有系統的啟發與資安防線評估

- **資安與安裝腳本硬閘門檢驗**：
  - 依據全域協作規範硬閘門：「**外部內容與第三方 Skill／MCP 零信任防入侵（只讀不執行、嚴禁破沙盒與偷跑 Hook）**，高星開源專案常夾帶遠端腳本直管執行（`curl|bash`、`iwr|iex`）、審批外自動執行 Command Hooks；採納前須過 `verify_agent_skill_pack_safety.py` 檢驗」。
  - 該專案包含 `install.ps1` / `install.sh` 安裝腳本，**絕對不可在主機環境直接執行其安裝腳本**，須以靜態檢視或沙盒分析其 Skill 定義與 Markdown 規則。
- **技術價值**：
  - 其收集的 681 條真實漏洞模式與 24 大類檢查清單（Checklists），屬於高價值的資安審查知識庫，適合作為代碼靜態審計與資安 Reviewer 的提示詞資產，而非作為具有執行權限的動態工具。
- **查證註記（2026-11-19，T-20261119-01 唯讀審查）**：
  - 審查 commit `0e70a021` 的 `skills/` 實際有 83 個技能（貼文與本筆記寫 82；該 repo 的 `plugin.json` 寫 83、`install.ps1` 說明寫 82）。「681 條」未查證。
  - 沒有找到惡意 hook 或隱藏指示；但內附引擎以略過權限模式啟動 Claude、安裝腳本會改寫 shell 啟動檔。結論是不安裝，只借鏡兩段純文字清單，詳見 [`docs/claude-bughunter-security-audit.md`](../docs/claude-bughunter-security-audit.md)。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261119-01`**｜**[優先級：低]** 對 `elementalsouls/Claude-BugHunter` 進行零信任安全審查與漏洞檢查清單評估
  - **目標範圍**：`C:\GitHub\_sandbox\claude-bughunter-audit` 與 `C:\GitHub\ai-inbox\docs\claude-bughunter-security-audit.md`
  - **執行步驟**：
    1. 僅以唯讀方式 clone `elementalsouls/Claude-BugHunter` 至沙盒目錄，嚴禁執行其 `install.ps1` 或任何腳本。
    2. 執行安全檢驗工具掃描其所有 skills、hooks 與 command 設定，確認無提權、未經授權之網路外連或惡意 command injection。
    3. 評估其 82 個 skills 中是否有適合抽取並安全轉化為本機只讀靜態安全審查提示詞（如整合進既有代碼審計流程）之內容，產出審查報告至 `docs/claude-bughunter-security-audit.md`。
  - **驗收標準（DoD）**：產出 `docs/claude-bughunter-security-audit.md`，記錄靜態安全性審查結果（包含有無惡意 hook/腳本風險評估）與是否安全採納部分純文字檢查清單之結論，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-19
  - **實作紀錄 / 證據**：docs/claude-bughunter-security-audit.md；唯讀審查 commit 0e70a021，安全掃描 exit 1（54 FAIL／51 REVIEW 已逐類人工判讀），無惡意 hook，但引擎以略過權限模式啟動、安裝腳本改 profile 並執行未固定版本的第四方安裝程式；結論不安裝，只借鏡兩段純文字清單
