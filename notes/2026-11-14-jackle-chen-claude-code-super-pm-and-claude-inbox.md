---
id: "2026-11-14-jackle-chen-claude-code-super-pm-and-claude-inbox"
title: "Claude Code 開越多越累：總 PM 派工 + claude-inbox 決定收件匣（Windows 原生不支援）"
source_url: "https://www.facebook.com/share/p/19youqwPEF/"
source_platform: "facebook"
author: "Jackle Chen"
analyzed_at: "2026-11-14"
analyzed_by: "antigravity"
status: archived
cluster: 1
cluster_role: "多session管理"
short_title: "總PM與claude-inbox"
tags:
  - claude-code
  - multi-session
  - super-pm
  - claude-inbox
  - plugin
  - hooks
  - human-in-the-loop
  - fable
  - windows-unsupported
---

## Executive Summary

**Jackle Chen**（FB 貼文，原文發表於其部落格 `jackle.pro`，2026-11-07）分享他同時帶 20 多條 Claude Code session 的做法：**一個常駐的「總 PM」session 負責派工，所有需要人決定的事統一進一個網頁「收件匣」**，人有空再一次回答，答案經 hook 自動回到對應 agent。他把收件匣核心拆出來開源為 `chenjackle45/claude-inbox`（MIT，16 stars、6 forks）。

資料來源說明：Facebook 全文被登入牆與 CAPTCHA 擋住（未繞過），貼文只取得 og 摘要；完整內容取自作者在貼文中指向的公開部落格文章 `jackle.pro/articles/claude-inbox`，以及 GitHub 倉庫原始碼實讀。

**對本機最重要的結論：`inbox.py` 使用 `fcntl`，README 明載「不支援原生 Windows」，本機（Windows 11 原生）無法直接使用，只有 WSL 可行。**

---

## 技術架構深挖

### 作者的四段演進

```
痛點：session 開多 → 每條都在等人回話，AI 還沒爆人先爆；開少 → 太慢
  │
  ├─ 1. 總 PM（Super PM skill）
  │     一個常駐 session 派卡、擋高風險、整理需拍板的事；自己不寫程式
  ├─ 2. 撈 log
  │     Claude Code mods 的「You should know」提醒只出現在各自 session，
  │     改寫程式定期撈 session log 丟給總 PM 統一發問
  ├─ 3. /leave skill
  │     離開前做記號，回來只摘要「不在期間」發生的事
  └─ 4. 儀表板
        總 PM 在開發機架網頁，人每天主要看這個
```

心法：**所有事情都拆成 task**，支線一出現就決定做或不做，決定做就先當它完成。

作者實測配置：

| 項目 | 設定 |
|------|------|
| 總 PM 模型 | Fable（其他 session 用 Opus；他認為 Fable 帶長任務較不亂） |
| Context | 600k 自動 compact |
| 常駐時間 | 總 PM 已連續開 20 天 |
| 執行主機 | Mac Studio（不佔筆電） |
| 規模截圖 | 21 條 session 在跑，1 條在等人 |
| 未解 | 常駐 session 停在舊版 Claude Code；每晚 9 點 build 上版仍須回 Claude Code 手動按允許 |

### `claude-inbox` 倉庫結構（實讀）

```
claude-inbox/
├── .claude-plugin/{plugin.json, marketplace.json}
├── bin/inbox                 # sh 入口 → python3 inbox/inbox.py
├── hooks/hooks.json          # SessionStart + UserPromptSubmit → inbox.py hook
├── inbox/inbox.py            # 17.7 KB，僅標準庫：CLI + HTTP server
├── inbox/page.html           # 16.6 KB，單頁前端
├── skills/inbox/SKILL.md     # 教 agent 用 inbox ask
├── skills/pm/SKILL.md        # /inbox:pm 總 PM 預設做法
└── tests/test_inbox.py       # unittest
```

### 運作流程

```
agent ──inbox ask --title --option A=.. --option B=.. --recommend A──▶ questions/<id>.json
                                                                           │
人（網頁，來源/期限/推薦選項/補充欄）──送出──▶ events.jsonl（只增不改）
                                                                           │
下一輪 UserPromptSubmit / SessionStart hook ──inbox.py hook──▶ 答案注入 agent context
agent 處理完 ──inbox close <題號>──▶ 收起
```

- 資料目錄 `~/.claude-inbox/`（可用 `CLAUDE_INBOX_HOME` 改）：`questions/*.json`、`events.jsonl`、`config.json`。
- 答案路由：靠環境變數 `CLAUDE_CODE_SESSION_ID` 認出題對話；該對話 30 分鐘未取，同 git 根目錄的其他對話也可取；每則答案只送一次。
- 其他 agent（Codex 等）無此環境變數與 hook：題目變匿名，須自行跑 `wait` / `take`；同專案同時出題可能拿到對方答案。作者承認此用法未實測。

### 安全設計（讀碼確認）

| 項目 | 實作 |
|------|------|
| 綁定 | 預設 `127.0.0.1`，`is_loopback` 判斷；遠端（Tailscale/內網）需手動改 `config.json`，僅支援 IPv4 |
| 認證 | 所有 API 需 `X-Inbox-Token`，以 `secrets.compare_digest` 比對；token 首次以 `secrets.token_urlsafe(24)` 產生，設定檔權限 600、資料夾 700 |
| 反 DNS rebinding / CSRF | 檢查 `Host` 與 `Origin`，不符回 403 |
| 注入面 | 題目文字以純文字顯示，僅網址轉連結 |
| 日誌 | 服務 log 不印 token |
| 資料外送 | 無；但題目與答案為明文，不應放密碼或金鑰 |
| 殘留風險 | token 同時出現在 `inbox url` 的 `?t=` query（會進瀏覽器歷史）；改設定後須重啟服務，舊 token 在重啟前仍有效 |

### 平台相容性（對本機決定性）

- 程式 `import fcntl`（POSIX 專有），README「需求」寫明支援 macOS、Linux、WSL，**原生 Windows 不支援**。
- hook 指令寫死 `python3`，Windows 上通常只有 `python`/`py`。
- 結論：在 Windows 11 原生環境直接安裝會失敗；須在 WSL 內跑 Claude Code，或自行改寫鎖檔邏輯。

---

## 與本機防線對照

| 評估維度 | 結論 |
|---------|------|
| **採用可行性** | 低：Windows 原生不可用；本機主力為 Antigravity，且無 `CLAUDE_CODE_SESSION_ID` 與 Claude hook |
| **概念可借用** | 高：「問人的事排隊、答案由 hook 注入下一輪」與本機 `ai-inbox`、hook 防線、派工清單思路同源 |
| **安全性** | 良好：loopback 預設、token、Host/Origin 檢查、純文字顯示；唯一外部輸入是人本人的答案 |
| **第三方 plugin 風險** | 屬社群個人專案（16 stars），依零信任規則：只讀分析，不安裝；採納前須過 SkillSpector 與 `verify_agent_skill_pack_safety.py` |
| **對照既有規範** | 本機已有「派工要掌控到完成」規範；總 PM 模式與之吻合，但作者的「決定做就當作完成」心法與「結案前要實查」衝突，不宜照搬 |
| **成本** | 總 PM 用旗艦模型常駐 20 天，配額消耗高，未提供用量數字 |

---

## 評估結論與處置

**評分：⭐⭐⭐⭐（4/5）**

方法論有實戰數據（21 條 session、20 天常駐），且作者主動坦承限制（未實測 Codex、常駐版本停滯、每晚仍須人工允許），開源範圍也交代清楚（儀表板、撈 log、進度頁不在 repo 內）。扣分：Windows 原生不可用；FB 貼文本身只是導流，細節在部落格；「決定做就當作完成」的心法在無實查時有漏洞。

**處置**：
- [ ] 不安裝 `claude-inbox`；若要試，只在 WSL 隔離環境，且先審 `inbox.py`、`hooks.json` 全文
- [ ] 評估把「決定收件匣」概念移植到本機：以 `agent-relay` 或 `ai-inbox` 現有機制承接，不必依賴 Claude hook
- [ ] 參考總 PM 的職責切分（派卡、擋高風險、整理待拍板事項），對照本機「派工逐件清單」規範補強缺口
- [ ] 追蹤作者部落格其他文章：`claude-code-worktree`、`claude-code-project-insights`、`claude-code-status-line`（本次未讀）
- [ ] 追蹤 `claude-inbox` 是否加入 Windows 支援（以 `fcntl` 替代方案）

**參考連結**：
- 部落格原文：https://jackle.pro/articles/claude-inbox
- 倉庫：https://github.com/chenjackle45/claude-inbox
