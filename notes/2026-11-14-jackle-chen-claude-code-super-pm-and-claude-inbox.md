---
id: "2026-11-14-jackle-chen-claude-code-super-pm-and-claude-inbox"
title: "Claude Code 開越多越累：總 PM 派工 + claude-inbox 決定收件匣（Windows 原生不支援）"
source_url: "https://www.facebook.com/share/p/19youqwPEF/"
source_platform: "facebook"
author: "Jackle Chen"
analyzed_at: "2026-11-14"
analyzed_by: "antigravity"
status: done
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

# Claude Code 開越多越累：總 PM 派工 + claude-inbox 決定收件匣（Windows 原生不支援）

- **來源連結**：[Facebook 貼文：Jackle Chen](https://www.facebook.com/share/p/19youqwPEF/)
- **發布平台 / 作者**：`facebook` / `Jackle Chen`
- **分析日期**：`2026-11-14`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：Jackle Chen；開源倉庫 `chenjackle45/claude-inbox`（MIT）。
- **What**：常駐「總 PM」session 派工，需人決定的事集中到網頁收件匣，答案經 hook 回到對應 agent。
- **Why**：同時開 20 多條 Claude Code session 時，人被各處提問打斷。
- **How**：`inbox.py` 起本機服務、hook 注入答案（見下方技術架構）。
- **When & Where**：macOS／Linux／WSL（README 載明原生 Windows 不支援）。
- **Key Metrics / Numbers**：16 stars、6 forks；作者自述 21 條 session、20 天常駐（未重現）。

### 摘要原文

**Jackle Chen**（FB 貼文，原文發表於其部落格 `jackle.pro`，2026-11-07）分享他同時帶 20 多條 Claude Code session 的做法：**一個常駐的「總 PM」session 負責派工，所有需要人決定的事統一進一個網頁「收件匣」**，人有空再一次回答，答案經 hook 自動回到對應 agent。他把收件匣核心拆出來開源為 `chenjackle45/claude-inbox`（MIT，16 stars、6 forks）。

資料來源說明：早期透過純文字爬蟲被導向登入頁與 CAPTCHA 擋住；2026-11-14 改由瀏覽器（無登入狀態、關閉登入彈窗後）實際讀取確認 Facebook 貼文全文與前 10 則公開留言完全可見（無需繞過 CAPTCHA），內文與作者公開部落格 `jackle.pro/articles/claude-inbox` 一致。留言區另有兩項實用討論：Atticus Wu 提醒「一個專案／待辦對應到哪些 session」的追蹤關聯性；Leo Tong 指出常駐 Fable PM 的 Token 燃燒成本過高。

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

## 2. CQR 深入論證檢驗（選填）

- **Claim**：總 PM + 決定收件匣可同時帶 20 多條 Claude Code session。
- **Evidence**：作者部落格與倉庫原始碼；21 條 session、20 天常駐為作者自述，未重現。
- **Reasoning**：方法論有實戰描述但缺用量數字；Windows 原生不可用，限縮了對本機的適用性。

---

## 3. 啟發與適用性評估

### 與本機防線與現有派工系統對照（2026-11-14 實查 `agent-relay` / `agentdeck`）

| 評估維度 | 結論 |
|---------|------|
| **採用可行性** | 低：本機為 Windows 11 原生，`inbox.py` 用 `fcntl`（POSIX 專有）、hook 寫死 `python3`（2026-11-14 以 GitHub API 查證） |
| **對比 `agent-relay`（核心強項）** | 本機 `agent-relay` + `agentdeck` + `harness-guard` + `ai-quality-gates` 在跨 CLI 派工、SSH 簽章、worktree 隔離、`dispatch.verify` 驗收閘門、`/recap` 期間摘要皆已遠勝 `claude-inbox` 單一插件，無需重造輪子 |
| **對比 `agent-relay`（唯一真實缺口）** | 實查 `agent_relay/envelope.py:17` 僅有 `KINDS = ("task", "reply", "note", "result")`。當 Worker 施工中遇到需人類「二選一／拍板」但不想中斷整條線時，尚缺類似 `claude-inbox` 的**結構化待決策問題格式與統一篩選／批次回覆介面** |
| **安全性** | 良好：loopback 預設、token、Host/Origin 檢查、純文字顯示；唯一外部輸入是人本人的答案 |
| **第三方 plugin 風險** | 屬社群個人專案（16 stars），依零信任規則：只讀分析，不安裝；採納前須過 SkillSpector 與 [`verify_agent_skill_pack_safety.py`](https://github.com/SanHsien/agent-safety-checks/blob/main/tools/verify_agent_skill_pack_safety.py) |
| **對照既有規範** | 本機已有「派工要掌控到完成」規範；總 PM 模式與之吻合，但作者的「決定做就當作完成」心法與「結案前要實查」衝突，不宜照搬 |
| **成本** | 總 PM 用旗艦模型常駐 20 天，配額消耗高（留言區亦被質疑），未提供用量數字 |

---

### 評估結論與處置

**評分：⭐⭐⭐（3/5）**

方法論有實戰數據（21 條 session、20 天常駐），且作者主動坦承限制（未實測 Codex、常駐版本停滯、每晚仍須人工允許），開源範圍也交代清楚（儀表板、撈 log、進度頁不在 repo 內）。扣分：Windows 原生不可用且不安裝；「決定做就當作完成」的心法在無實查時有漏洞。

**處置**：不安裝 `claude-inbox`（Windows 原生不可用）。對比本機派工系統後，確認無需引入總 PM 常駐對話或 `/leave`（已有 `agent-relay` + `agentdeck` + `/recap`），僅將「結構化非同步決策問答（`ask`／待拍板佇列篩選與回傳）」列為 `SanHsien/agent-relay` 的近期優先事項（已同步更新至 `agent-relay/ROADMAP.md` 與本篇 `T-20261114-05`）。

**參考連結**：
- 部落格原文：https://jackle.pro/articles/claude-inbox
- 倉庫：https://github.com/chenjackle45/claude-inbox

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261114-04`**｜**[優先級：中]** `tools/verify_inbox.py` 新增檢查：筆記裡沒有任務 ID 的待辦核取方塊一律報錯，並清掉 11-11 至 11-14 六篇筆記的殘留清單
  - **目標範圍**：`tools/verify_inbox.py`、`tests/test_inbox.py`，以及 `notes/` 下 2026-11-11 astryx、11-12 duet、11-13 editkin、11-13 hujiaxi、11-13 soveryai、11-14 jackle 六篇筆記
  - **具體做法**：
    1. 在 `check_task_ids` 旁新增檢查：圍欄外符合 `^- \[[ xX]\] ` 但不含任務 ID 的行，報「待辦行缺任務 ID，總表讀不到：檔名:行號」；`templates/` 不掃，圍欄內範例不報。
    2. `tests/test_inbox.py` 加三個測試：無 ID 的核取方塊報錯、合格任務行不報、圍欄內範例不報。
    3. 六篇筆記的核取清單整段刪除（沒有可驗收的 DoD），並補齊範本要求的章節。
  - **驗收標準（DoD）**：`python -m unittest tests/test_inbox.py` 綠燈且含上述三個新測試；清理前 `python tools/verify_inbox.py` 對六篇報錯（附輸出），清理後回 `[PASS]`；`python -m unittest discover -s tests` 全綠。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：完成（2026-11-14）：verify_inbox 新增 check_idless_checkboxes（圍欄外、非 templates/），函式測試 3 項＋實際執行 verify_inbox.py 的整合測試；清理前對 7 篇筆記報 32 行缺 ID（exit 1），清理後 PASS。六篇筆記同時補齊範本章節並依審查改寫事實。

- [x] **`T-20261114-05`**｜**[優先級：高]** 在 `agent-relay` 實作非同步結構化決策問答（`ask`／待拍板佇列篩選與回傳，不另起 Web 服務）
  - **目標範圍**：`C:\GitHub\agent-relay`（`ROADMAP.md`、`SPEC.md`、`SPEC.en.md`、`agent_relay/envelope.py`、`agent_relay/cli.py`、`tests/`）
  - **具體做法**：
    1. 在 `SPEC.md`／`SPEC.en.md` 定義結構化決策問題欄位（來源專案、`thread`、選項 `A/B`、推薦選項、期限與補充欄），評估採 `question` kind 或 `note` 擴充欄位。
    2. 在 `agent_relay/cli.py` 新增對應篩選（如 `relay inbox --questions`）與回覆指令，讓使用者一次回答多題並回傳至對應 Worker `thread`（由 `hooks/session_start.py` 或 `poller` 帶入下一輪上下文）。
    3. 補齊單元測試並通過 `python -m unittest discover -s tests`、`tools/check_doc_parity.py`、`tools/check_links.py`。
  - **驗收標準（DoD）**：`agent-relay` 可透過 CLI 送出結構化決策問題、篩選待拍板佇列並回覆回原 `thread`，中英規格對齊且測試與 doc parity 全綠（已先登錄於 `agent-relay/ROADMAP.md` 近期優先事項）。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：完成（2026-11-14，commit `2044f9b` 已推送至 `SanHsien/agent-relay` `main`）：`agent_relay/envelope.py` 新增 `kind="question"` 與 `question` 結構驗證（`options`/`recommend`/`deadline`）；`agent_relay/cli.py` 新增 `relay ask`、`relay inbox --questions`／`--kind`、`relay answer` 與 `relay read` 選項呈現；同步更新 `SPEC.md`/`SPEC.en.md`、`README.md`/`README.en.md` 並自 `ROADMAP.md` 移除已完成列；新增 `tests/test_questions.py`（5 tests），全套驗證通過：`python tools/check_doc_parity.py`（PASS，5 pairs）、`python tools/check_links.py`（30 files，0 broken links）、`python -m unittest discover -s tests -q`（461 tests OK）。
