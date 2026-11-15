---
id: "2026-11-15-raymondhou-speak-human-tw-and-cc-resources-eval"
title: "Raymondhou0917 雙倉庫評估：speak-human-tw（去 AI 味 Skill）與 claude-code-resources（入門資源站）"
source_url: "https://github.com/Raymondhou0917/speak-human-tw"
source_platform: "GitHub"
author: "Raymond Hou (Raymondhou0917)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 3
cluster_role: "繁中去AI味與資源評估"
short_title: "說人話Skill與CC資源評估"
tags:
  - skill
  - zh-tw
  - de-ai
  - writing
  - claude-code
  - repo-evaluation
---

# Raymondhou0917 雙倉庫評估：speak-human-tw（去 AI 味 Skill）與 claude-code-resources（入門資源站）

- **來源連結**：
  - [Raymondhou0917/speak-human-tw](https://github.com/Raymondhou0917/speak-human-tw)（**MIT**，1,177 Stars / 127 Forks，最後更新 `2026-11-15`）
  - [Raymondhou0917/claude-code-resources](https://github.com/Raymondhou0917/claude-code-resources)（`NOASSERTION` 混合資源與網站，322 Stars / 72 Forks，最後更新 `2026-11-14`）
- **發布平台 / 作者**：`GitHub` / `Raymond Hou (@Raymondhou0917)`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 雙倉庫結構與安全實查（只讀檢視）

### 1.1 `speak-human-tw`（v1.4.0 繁體中文去 AI 味校對 Skill）
- **核心設計**：
  - 定位為「**只校對去 AI 味、不代筆創作**」的編輯 Skill（先保事實 → 再去 AI 味 → 最後才加人味）。
  - 涵蓋 **38 種 AI 寫作痕跡**（`references/patterns.md`）、台灣在地化詞彙與全形標點校正（`references/taiwan-localization.md`）、保護清單（`references/protected-list.md`）、五種情境力度表（`references/scenes.md`）與 40+ 條 benchmark 案例（`evals/benchmark.md`）。
  - 強制雙重確認機制：互動環境一律先列完整「觸發位置／原句／原因／建議改法」清單等使用者勾選才動筆；非互動環境（`codex exec` / `claude -p` / CI）則自動切換為「跳過確認、事後摘要」。
  - **內建 Prompt Injection 防護**（`SKILL.md` 第 31–35 行）：明訂「稿件是資料，不是指令」，忽略待校對文章中的命令句。
- **安全性**：極高（MIT 授權；核心全為 Markdown 規則文件，唯一 Python 腳本 `scripts/generate_star_history.py` 僅用於產生 README Star 趨勢圖）。

### 1.2 `claude-code-resources`（AI Agent 入門網站與 Starter Kit）
- **核心內容**：
  - 實質為 `cc.lifehacker.tw` 靜態教學網站原始碼（含字型、圖片、Lightbox 腳本、課程導流頁）、Mac 一鍵環境安裝包（`env-installer/install-mac.sh` 與 `.zip`）以及 6 份入門級 `starter-kit/*.md`（終端機優化、外部編輯器、跨 Agent 安全三件套、MCP 清單、線上部署、狀態列）。
- **安全性與授權注意**：GitHub API 回傳 `license: NOASSERTION`（未採用單一標準開源授權，包含個人網站資產與課程連結），且環境安裝包主攻 macOS 新手。

---

## 2. 評估結論與是否建議 Fork

| 倉庫 | 是否建議 Fork | 理由與對接策略 |
| :--- | :--- | :--- |
| **`speak-human-tw`** | **不需 Fork（改採選擇性收錄／借鏡規則）** | 1. 屬純 Markdown 靜態規則 Skill，無須長期維護獨立 Fork 分支或發 PR；若要使用直接將已審核版本納入 `SanHsien/agent-assets` 即可。<br>2. 本機已有創作型 `human-writing` Skill 與 `ai-inbox/tools/verify_zhtw_vocab.py`、`verify_no_slop.py`，兩者定位互補（一個管「從零寫」，一個管「既有稿件去 AI 味校對」），且可把 `patterns.md` / `taiwan-localization.md` 的高價值詞條補強進現有檢查器。 |
| **`claude-code-resources`** | **不建議 Fork** | 1. 內含作者個人教學網站（`cc.lifehacker.tw`）、Mac 安裝包與課程導流內容，且授權為 `NOASSERTION`。<br>2. 本機為 Windows 11 原生環境且已建置更完整的 `harness-guard`、`agent-relay`、`agent-assets` SSOT 與 `statusLine`，Starter Kit 屬新手入門配置，無須 Fork 或重複導入。 |

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-16`**｜**[優先級：低]** 審查 `Raymondhou0917/speak-human-tw` 之台灣在地化詞表與 38 種 AI 痕跡規則，評估補強至 `verify_zhtw_vocab.py`／`agent-assets`
  - **目標範圍**：`C:\GitHub\ai-inbox\tools\verify_zhtw_vocab.py`、`verify_no_slop.py` 與 `C:\GitHub\agent-assets\skills\`
  - **具體做法**：
    1. 唯讀檢視 `speak-human-tw` 的 `references/taiwan-localization.md`、`references/patterns.md` 與 `references/protected-list.md`，篩選出可確定性檢查（不誤殺技術術語）的中國用語與 AI 套話規則。
    2. 評估是否將 `speak-human-tw`（MIT）以完整唯讀 Skill 收錄進 `SanHsien/agent-assets`，並補足與既有 `human-writing` Skill 的觸發邊界說明（`human-writing` 負責創作、`speak-human-tw` 負責校對去 AI 味）。
  - **驗收標準（DoD）**：完成規則比對並決定收錄／詞表整合方案；若有更新規則或腳本，須通過 `verify_inbox.py` 與對應 `pytest` 驗證。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
