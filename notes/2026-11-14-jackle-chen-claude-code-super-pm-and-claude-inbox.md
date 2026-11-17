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
source_review: full
source_reviewed_at: 2026-11-17
source_images: 8
source_replies: 20
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

## 0. 原始資料盤點

> 2026-11-16～17 以未登入瀏覽器重看 Facebook 貼文與作者在留言貼的部落格好讀版，「最相關」排序下讀到 16 則。2026-11-17 以登入狀態補讀：改用「所有留言」排序並展開回覆串，補到另外 4 則，20 則全部讀完（作者 9 則＋網友 11 則）。貼文開頭就寫「圖文好讀版在留言」，所以部落格的圖一併算作者圖片。

- **作者圖片**（Facebook 1 張＋部落格 7 張，共 8 張）：
  - **圖 1（Facebook 與部落格的題圖）**：版畫風插圖，多條纜車線從群山匯集到一間小屋，屋裡坐著一個人。是意象圖，沒有資訊。
  - **圖 2（session 清單）**：Claude Code v2.1.318 的 session 列表，頂部寫 1 awaiting input、21 working、4 completed，新 session 預設 Opus 5.5、medium effort。最上面一條是「總 PM」，存活 20 天；下面每條 session 名稱前都有一個中文角色標籤（收件匣、測試、合併、查詢、進度員、知識庫、日誌，以及十多條同一個改版專案的實作線），存活時間從數小時到 7 天。狀態欄已打馬賽克。
  - **圖 3（You should know 提醒）**：寫文章時 Claude Code 跳出的提醒，指出開源的 `claude-inbox` 只有「決定信箱」那一塊，儀表板、撈 log、工作線進度可能都不在 repo，建議文章分清楚。下方三個選項：Understood、Chat in main session、Dismiss。
  - **圖 4（作者自用的「指揮台」）**：三欄版面——左欄是待回的題目清單（當下 2 題），中欄是目前這題的完整說明與送出按鈕，右欄是各工作線狀況，頂部有一條期限時間軸。細節已打馬賽克。**這個不在開源範圍內。**
  - **圖 5（總 PM 匯報面板）**：指揮台右側展開的面板，分「匯報內文／要你動手（2 張卡，各有去回答按鈕）／回你與告知／我接下來要做的事」。內容已打馬賽克。不在開源範圍內。
  - **圖 6（進度頁）**：上方三個數字（今天上線、在路上、接下來要我在場），中間是未來一週時間軸，下方是各主線的下一步。不在開源範圍內。
  - **圖 7（開源的收件匣網頁）**：每題一張卡，有來源專案標籤、出題時間、期限徽章、題目說明、A／B 選項（其中一個標「推薦」）、補充說明欄，卡片上有「這題先送」，頁尾有「已答 N 題／送出全部已答」。
  - **圖 8（手機版收件匣）**：同一頁在手機寬度下直向排列。
- **作者留言補充**：
  - 第一則留言放好讀版連結 `jackle.pro/articles/claude-inbox`（連結預覽卡就是圖 1）。
  - 回 Leo Tong 的成本質疑：總 PM 用 Opus 也行，搭配 Codex 可以撐更久。
  - 回 Atticus Wu：儀表板是被同事每天催出來的。其餘是道謝與玩笑。
- **網友留言重點**：
  - **Atticus Wu**：也在做類似工具（給不懂程式的人、多電腦多人協作）；從貼文得到的提醒是「一個專案／待辦事項對應到哪些 session」要能追蹤。
  - **Leo Tong**：儀表板不燒錢，但常駐的總 PM 很燒錢，還用 Fable。
  - **蔡忠栩**：像「grok boss」的概念，一個總工程師收集情報與分派，等於把 Claude Code agent 化。
  - **曾友志、Norris Chen**：已給星。其餘 4 則是稱讚。沒有人回報安裝後的實際使用結果，也沒有人提到 Windows。
  - **Chris Lin**（登入補讀，2 則）：貼出 `scyprodigy/shadowMAS`，說明做法是不同家的 agent 用統一格式的訊息封包丟進同一個訊息匣，最後要給人審閱或提問的部分參考認知科學設計；並說訊息匣怎麼架設沒什麼技術成分。另有 1 則稱讚與作者的回應。
- **對分析的影響**：
  - 沒有推翻原稿的結論。圖 3 與圖 4～6 印證了原稿「開源範圍只有收件匣，儀表板、撈 log、進度頁不在 repo」的判斷，而且是作者自己用截圖交代的。
  - 圖 7 補上原稿沒寫到的介面細節：每題可以單獨先送，也可以一次送出全部已答。`T-20261114-05` 在 `agent-relay` 做的「一次回答多題」與此對應；單題先送本來就有（`answer` 單一 id）。不需要改任務。
  - 圖 2 補上兩個可借鏡的做法：session 名稱前加角色標籤、同一專案拆十多條實作線並行。技術架構段的配置表已補一列。
  - 成本質疑有了作者的回應（Opus 也行、搭配 Codex），已補進評估表「成本」列；仍然沒有用量數字。
  - **多一個同類專案**：`scyprodigy/shadowMAS`（2026-11-17 以 GitHub API 查：Python、Apache-2.0、4 stars，自述是重治理、有記憶的人機協作系統）。與本篇「跨 agent 共用收件匣＋人只回答決定題」同方向，本機已有 `agent-relay` 對應；只讀了 repo 基本資料、沒讀程式碼，不衍生任務。其餘補讀到的留言沒有改變結論。
  - 原稿寫「前 10 則公開留言」；首輪展開回覆串後讀到 16 則，登入補讀後 20 則全讀。

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
| 規模截圖 | 21 條 session 在跑，1 條在等人，4 條已完成；Claude Code v2.1.318，新 session 預設 Opus 5.5／medium effort |
| session 命名 | 名稱前加角色標籤（收件匣、測試、合併、進度員、知識庫等）；同一改版專案拆成十多條實作線 |
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
| **成本** | 總 PM 用旗艦模型常駐 20 天，配額消耗高（留言區亦被質疑；作者回覆「Opus 也行，搭配 Codex 撐更久」），未提供用量數字 |

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
  - **重開紀錄（2026-11-14 獨立審查，判「先修」）**：主流程實跑可用、461 tests 全綠，但 DoD 範圍內有四項未達成：(1) `recommend` 不在 `options` 內照樣寄出，與 SPEC 第 39 行「須為 options 其中之一」矛盾；(2) `relay answer` 不檢查對象是不是 question，對 note 也會回覆並結案；(3) `answer` 不檢查選項、不擋重複回答；(4) 具體做法 2 要求的「一次回答多題」未實作（`answer` 只收一個 id）。另有建議：options 至少兩個不重複、`--questions` 與 `--kind` 互斥、`cmd_ask` 補允許清單檢查、SPEC 補 ask／answer 流程與回覆內文格式、補 deadline 顯示與上述負向測試。已交 Codex 修正，修完再做獨立審查。
  - **原結案證據（審查前）**：commit `2044f9b` 已推送至 `SanHsien/agent-relay` `main`）：`agent_relay/envelope.py` 新增 `kind="question"` 與 `question` 結構驗證（`options`/`recommend`/`deadline`）；`agent_relay/cli.py` 新增 `relay ask`、`relay inbox --questions`／`--kind`、`relay answer` 與 `relay read` 選項呈現；同步更新 `SPEC.md`/`SPEC.en.md`、`README.md`/`README.en.md` 並自 `ROADMAP.md` 移除已完成列；新增 `tests/test_questions.py`（5 tests），全套驗證通過：`python tools/check_doc_parity.py`（PASS，5 pairs）、`python tools/check_links.py`（30 files，0 broken links）、`python -m unittest discover -s tests -q`（461 tests OK）。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：Antigravity 初版 2044f9b 經獨立審查判先修，Codex 修正為 88addb6、0cabfe3（SanHsien/agent-relay main，CI 與 CodeQL 綠燈）。recommend 必須是選項代號、answer 只接受 question、選項須在清單內、已答題不可重答、可一次回答多題且任一失敗整批不送；另補 note 禁止換行、選項代號拒絕不可見字元、SPEC 中英補 ask／answer 流程與舊格式升級說明。整合者沙盒外實跑：Python 3.14 與 3.11 各 485 tests OK、doc parity PASS、links 0 broken、mutation 25/25 killed；Fable 複審四項必修全部通過。
