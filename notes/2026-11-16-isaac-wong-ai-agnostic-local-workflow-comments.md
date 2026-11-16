---
id: "2026-11-16-isaac-wong-ai-agnostic-local-workflow-comments"
title: "Claude Taiwan 貼文與留言串評估：不依賴單一 AI 的本地 Skill/Handoff/Memory 工作流"
source_url: "https://www.facebook.com/groups/1317626560441303/permalink/1434572405413384/"
source_platform: "Facebook (Claude Taiwan)"
author: "Isaac Wong（含 Ghibili Shu / Thlee Eafb / Ray Huang / Jabus Liu 等留言討論）"
analyzed_at: "2026-11-16"
analyzed_by: "antigravity"
source_review: full
source_images: 2
source_replies: 5
status: archived
cluster: 1
cluster_role: "記憶交接與去噪對照"
short_title: "不綁定單一AI本地系統"
tags:
  - claude-code
  - handoff
  - markdown-memory
  - cleanupPeriodDays
  - obsidian
  - facebook
---

# Claude Taiwan 貼文與留言串評估：不依賴單一 AI 的本地 Skill/Handoff/Memory 工作流

- **來源貼文**：[Facebook Claude Taiwan 貼文（Isaac Wong）](https://www.facebook.com/groups/1317626560441303/permalink/1434572405413384/)（原分享連結 `https://www.facebook.com/share/p/19u9giaefR/`）
- **發布平台 / 作者**：`Facebook (台灣 Claude Taiwan)` / `Isaac Wong`（含資訊圖表 1 張、網友留言 5 串＋`cleanupPeriodDays` 截圖 1 張）
- **分析日期**：`2026-11-16`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](./2026-10-17-claude-code-idle-compaction-cc-session-reader.md)（Claude Code session 紀錄與讀取架構）
  - [`notes/2026-10-17-claude-mem-autocompact-context.md`](./2026-10-17-claude-mem-autocompact-context.md)（Claude Mem 跨 Session 記憶機制）
  - [`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](./2026-10-26-ai-shared-memory-template-team-collaboration.md)（AI 共用記憶與多 Agent 協作範本）

---

## 1. 主貼文與附圖核心整理

作者（Isaac Wong）以「我不相信 Claude，也不相信 ChatGPT」為題，主張工作流程與 SOP 不應鎖在單一雲端對話介面，並以主文與資訊圖表提出四點本地化做法：

1. **SOP 轉成 Skill 並用 Git 管理**：將重複 workflow、寫作風格、coding 規則存成 Skill（作者自承目前僅下載至本地尚未上 Git）。
2. **透過 CLI / VS Code 保留本地檔案**：利用 Claude Code 將 session transcript、Skills、Memory 存在本地檔案系統，並搭配開源工具 `Claude Mem` 保存對話紀錄。
3. **Session 交接延續**：結束前請 Agent 寫成 `handoff summary` 檔案，或搭配 `/pickup`、`/brain wrap-up` 等 Skill 延續脈絡。
4. **Obsidian Vault 建立 Memory 系統**：安裝 `obsidian-skills`，將 AI 關鍵決策存入自己的 Obsidian Vault。

---

## 2. 網友留言與截圖關鍵洞察（技術精華）

本貼文最有價值的工程討論集中於底下 5 串留言與截圖：

| 留言者 | 核心觀點 / 實務陷阱 | 與本機現有系統對照 |
| :--- | :--- | :--- |
| **Thlee Eafb**<br>（留言串 2） | **「檔案解決的是存，不是找與版本有效性」**：同一個決定改過三次時，純搜尋無法分辨哪份是現行有效；應記錄**「決定＋理由＋被否決的選項」**，更新時採**取代（supersede）**而非單純堆疊。且 **Memory 與 Skill/Code 應分開管理**，避免日常 memory 成為 Git commit 噪音。 | 本機採 `SanHsien/agent-assets`（SSOT）搭配 `neat-freak` 定期對帳清理與取代過時事實，並把日常工作記憶與 repo 程式碼分離。 |
| **Ray Huang**<br>（留言串 4 ＋截圖） | **Claude Code `cleanupPeriodDays` 預設 30 天靜默刪除**：截圖指出 `~/.claude/settings.json` 預設 `cleanupPeriodDays: 30`，每次啟動 Claude Code 會直接永久刪除 `~/.claude/projects/` 下超過 30 天的 `.jsonl` transcript（無警告、無垃圾桶）；建議調高至 90/365 並配合 `cc-session` browser 封存搜尋。 | **已實查本機 `~/.claude/settings.json`**：已明確設定 `"cleanupPeriodDays": 36500`，並已配備 `cc-session` skill 與 `qmd` 搜尋，無靜默刪除風險。 |
| **Jabus Liu**<br>（留言串 5） | **交接雜訊與幻覺傳染風險**：把交接判斷全權交給 Agent，發生幻覺時會污染下一個 session；全量保留所有紀錄亦會累積雜訊稀釋真正重要訊號。 | 本機已透過 `claim_evidence_guard`、`claim_ledger_tracker` 與 `verification-protocol` 強制交接／結案事實須附指令輸出與檔案證據，防止幻覺傳遞。 |
| **Ghibili Shu / 鍾丞 / Jabus Liu**<br>（留言串 1） | Markdown（`.md`）＋ index 可大幅縮短上下文讀取並省 token；YAML frontmatter 利於 Agent 解析，但巢狀結構不宜過深。 | 本機 `ai-inbox` 正是採用扁平 YAML frontmatter + Markdown 筆記 + `build_index.py` 自動索引架構。 |
| **Ray Huang**<br>（留言串 3） | 雲端 Agent 輔助養成地端模型能力與工具鏈，減少對單一雲端服務的依賴。 | 本機維持雲端與地端工具鏈並用。 |

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：主貼文四原則（Skill Git 化、本地檔案、Handoff、Knowledge Vault）與留言串點出的三大陷阱（`cleanupPeriodDays` 30 天刪除、決策版本取代與去噪、交接幻覺防護），皆已在本機 `agent-assets` SSOT、`settings.json`（`cleanupPeriodDays: 36500`）、`cc-session`、`neat-freak` 與 `claim_evidence_guard` 完整落地並驗證。保留本筆記作為社群實務痛點對照紀錄即可。
