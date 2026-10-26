---
id: 2026-10-26-ai-shared-memory-template-team-collaboration
title: "AI 共用記憶系統全景分析：從 Going Li 三 Agent 同腦架構、社團留言實踐到 Leoceeport 工程範本"
source_url: "https://github.com/Leoceeport/ai-memory-template"
source_platform: "Facebook (Claude Taiwan) / GitHub (Leoceeport/ai-memory-template)"
author: "Going Li / Leoceeport / 社團社群"
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: in-progress
cluster: 1
cluster_role: "團隊共用記憶架構"
short_title: "AI 共用記憶與三 Agent 全景"
tags:
  - shared-memory
  - git-workflow
  - context-optimization
  - correction-queue
  - multi-agent
  - handoff-protocol
  - index-health
  - secret-scanning
---

# AI 共用記憶系統全景分析：從 Going Li 三 Agent 同腦架構、社團留言實踐到 Leoceeport 工程範本

- **社群討論來源**：[Facebook 社團貼文討論串 (Claude Taiwan)](https://www.facebook.com/groups/1224997379198346/permalink/1423729639325118)
- **官方開源倉庫**：[`Leoceeport/ai-memory-template`](https://github.com/Leoceeport/ai-memory-template)
- **分析主題**：跨 Agent「住進同一顆大腦」實戰、SSOT 資料夾架構、非同步交接帳本（`HANDOFF.md`）、滾動視窗 Hook、三跳查詢防線（3-Hop Query Protocol）、動詞寫入契約與糾正審核佇列
- **分析日期**：`2026-10-26`
- **當前狀態**：`🟡 進行中 (In Progress)`
- **相關交叉參照**：
  - [`notes/2026-10-19-ai-shared-brain-multi-agent-architecture.md`](./2026-10-19-ai-shared-brain-multi-agent-architecture.md)（多 Agent 共同大腦與跨環境同步）
  - [`notes/2026-10-26-github-trending-agent-skills-benchmark.md`](./2026-10-26-github-trending-agent-skills-benchmark.md)（熱門技能評估與上下文預算工程）
  - [`notes/2026-10-26-codync-open-source-agent-relay-fallback.md`](./2026-10-26-codync-open-source-agent-relay-fallback.md)（開源中繼與多代理協同）

---

## 1. 核心內容摘要與討論串全景剖析（Key Insights）

本次調研源自 Facebook **Claude Taiwan** 社團熱門討論串，由開發者 Going Li 分享其實戰配置，並引發社群成員（顏志吉、Max DDuan 等）與開源作者 Leoceeport 的深度技術交鋒。

### 1.1 Going Li 主貼文核心：三 Agent 住進同一顆大腦

- **痛點根源（記憶分裂）**：
  同時使用多個 AI 開發工具時，最大瓶頸不是模型智商差異，而是「記憶與規則分裂」——在主力 AI 身上踩過的 300 多條工程坑、定好的開發規矩、積累的 78 支 Skill，換到另一個工具全部歸零，換手接力時痛苦不堪。
- **解法架構（不搬家、不複製檔案，以 Claude Code 目錄為 SSOT 母體）**：
  1. **Claude Code（主力工程師）**：負責深度架構與主力代碼開發，直接掌管單一真實資料來源（SSOT）：全域規矩（`CLAUDE.md`）、長期記憶（`MEMORY.md`）與 78 支 Skill。
  2. **Antigravity（架構師與第二主力）**：撰寫本機橋接外掛，以外部引用將 Claude 全域規則與記憶索引動態掛載進來；利用系統 symlink 映射 78 支 Skill；共用危險指令攔截 Hook（禁止危險 `rm`），並在對話結束時透過腳本自動把記憶回寫至 Obsidian 知識庫。
  3. **Hermes Agent（調度與接力手）**：負責反應迅速的輕量任務，背後調用 GitHub Copilot 的 GPT-4o / Sonnet 模型（實現零額外 API 成本備援）；專屬配置 `agent-handoff` CLI，統一管理專案根目錄的 `HANDOFF.md` 交接帳本。
- **無縫接力工作流**：
  各 Agent 開工第一步均讀取專案禁區與 `HANDOFF.md`；任務切片完成或即將抵達 Token/Rate Limit 上限前，執行 `agent-handoff checkpoint` 記錄 Git commit 與下一步待辦，下一個 Agent 立即無痛接棒。
- **核心哲學**：個人 AI 工作台的真正護城河不是綁定頂級訂閱，而是長期沉澱的**記憶結構、防呆護欄與跨 AI 交接協定**。

### 1.2 留言串關鍵互動與各家流派交鋒

1. **顏志吉的實踐（Hook 自動載入最新 10 份 Summary 流派）**：
   - **實作方式**：在 Session 啟動的 Hook 中強制規定 AI 必須先讀取專案的 `memory`、規格書與「最新 10 份 summary」。
   - **優缺點剖析**：屬於「滑動視窗（Sliding Window）」策略。優點是配置簡單、能確保接手者掌握近期脈絡；但缺點是缺乏層級索引，當專案規模擴大或歷史踩坑分散時，載入 10 份文件會快速膨脹 Context 預算，且容易漏掉關鍵的長期歷史架構決策。
2. **Max DDuan 的核心疑問（跨 Agent 溝通機制）**：
   - **提問關鍵**：「你是用什麼機制讓三者可以互相溝通？」
   - **技術維度拆解**：跨 Agent 協同本質上有兩種路徑：
     - **檔案非同步中繼（File-based Handoff）**：Going Li 採用的 `HANDOFF.md` + Git commit。無行程相依、跨機器相容性最強、最不易因連線中斷丟失狀態。
     - **即時行程通訊（RPC / Relay / ACP）**：透過語言伺服器 API、Socket 或 Message Relay（如 Codync / Nostr Relay）進行即時推播，適合需要秒級自動派工的自動化管線。
3. **Leoceeport 的回饋（泛用型工程範本 `ai-memory-template`）**：
   - 留言串中釋出開源專案，將 Going Li 的單人跨 Agent 特化架構進一步抽象為**團隊多工程師協作的標準模板**，補足了「三跳查詢防線（3-Hop Query）」與「Git 機械健檢防線」。

---

## 2. 深入技術拆解與架構原理（Deep Dive）

### 2.1 四大記憶流派對比

| 維度 | Going Li（三 Agent 同腦） | 顏志吉（滾動視窗 Hook） | Leoceeport（ai-memory-template） | 現有 agent-assets 體系 |
| :--- | :--- | :--- | :--- | :--- |
| **核心定位** | 單人多 Agent 跨工具無縫切換 | 單人輕量級快速無痛接手 | 多人團隊/跨 Agent 標準記憶庫 | 跨 AI 助理全域 SSOT 知識資產 |
| **記憶儲存體** | Claude Code 目錄 + Obsidian | 本機專案目錄 + Summary | 獨立 Git 倉庫 (Markdown + jsonl) | `C:\GitHub\agent-assets` (Git) |
| **讀取策略** | `HANDOFF.md` + 動態符號連結 | Hook 讀取最新 10 份 Summary | 三跳查詢協議（嚴禁整包讀取） | 按需 JIT 讀取（入口 + 領域檔） |
| **寫入防線** | `agent-handoff checkpoint` | 手動/自動撰寫 Summary 檔案 | 動詞寫入契約 + 糾正審核佇列 | 規範強制要求、主表集中收斂 |
| **跨工具溝通** | 檔案帳本（`HANDOFF.md`） | 檔案帳本（專案文件） | Git Pull/Push Rebase 同步 | Git + Task CLI + 跨平台通訊 |
| **優缺點評估** | 靈活高產，但仰賴個人環境配置 | 直覺易用，但缺乏防腐蝕機制 | 規範嚴密、防呆健全，適合團隊 | 跨專案泛用，兼顧規範與自動化 |

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI 共用記憶系統三跳查詢拓撲                          │
└─────────────────────────────────────────────────────────────────────────┘

  [ 每次開工注入 ]
        │
        ▼ 查詢跳轉 1
 ┌──────────────────────────────────────────────────┐
 │ MEMORY.md (入口索引)                             │
 │ ・一行一條指針，不放任何具體內容                 │
 │ ・指向組織側寫、規則主表、主題總索引與糾正佇列   │
 └──────┬───────────────────────────────────────────┘
        │
        ▼ 查詢跳轉 2 (按需定位，嚴禁整包讀取)
 ┌──────────────────────────────────────────────────┐
 │ domains/<主題>/_index.md (主題索引)              │
 │ ・收錄具體檔案指針 (people / projects / lessons) │
 │ ・門檻限制：單一索引超過 60 條即報警要求歸檔拆分 │
 └──────┬───────────────────────────────────────────┘
        │
        ▼ 查詢跳轉 3
 ┌──────────────────────────────────────────────────┐
 │ domains/<主題>/<具體檔案>.md                     │
 │ ・結構化 frontmatter (kind / date / status)      │
 │ ・動詞開頭：implemented / fixed / decided        │
 └──────────────────────────────────────────────────┘
```

### 2.2 記憶讀寫的三大核心鐵律（Leoceeport 範本核心）

1. **三跳查詢協議（The 3-Hop Query Protocol）**：
   - 傳統記憶系統最常犯的錯誤是將全部背景資料打包一股腦塞入 System Prompt，造成 Context 嚴重浪費與注意力稀釋。
   - 本範本嚴格規定：**「入口索引 $\to$ 主題索引 $\to$ 具體檔，最多三次查詢，嚴禁整包讀取」**。模型只讀取當前任務絕對需要的上下文片段。
2. **動詞寫入契約（Action-Verb Writing Contract）**：
   - 記錄必須由強動詞開頭（`implemented`、`fixed`、`decided`、`discovered`、`flagged`、`reversed`、`deferred`）。
   - 必須帶日期檔名或日期段落，直寫對應主題資料夾，並同時更新該資料夾的 `_index.md`。不具持久參考價值的事情「不寫就不寫」，防止記憶庫長出冗餘雜草。
3. **糾正審核佇列（Correction Queue & Single Gatekeeper）**：
   - 為防止多位成員或不同 Agent 隨意破壞最核心的規則主表（`domains/rules/rules_summary.md`），任何日常的糾正與教訓**嚴禁直接修改主表**。
   - 所有改動先追加至 `domains/lessons/correction-queue.jsonl`，由管理員或主負責人定期審核後才正式合入主表，實現規則的單一寫入權威。

### 2.3 四大機械腳本防線（Scripts & Hooks）

專案之所以能長期維持健康而不腐爛，關鍵在於將管理紀律交給自動化腳本：
- **收工安全同步（`scripts/memory_commit.sh`）**：
  自動執行 `git add -A` $\to$ 產生具備時間戳與使用者的 Commit $\to$ `git pull --rebase` $\to$ `git push`。若與遠端衝突，**立即執行 `git rebase --abort` 自動退回乾淨狀態並明講錯誤**，絕不將半成品的 Git 衝突標記留在工作區。
- **索引健檢防腐爛（`scripts/check_index.sh`）**：
  機械化掃描四類缺陷：(1) 未編入索引的檔案、(2) 索引指向不存在檔案的壞連結、(3) 入口 `MEMORY.md` 壞指針、(4) 索引行數超過 60 條的肥大警告。回傳非 0 即擋下 CI。
- **金鑰防護（`scripts/scan_secrets.sh`）**：
  掛載於 `pre-commit` 鉤子，以正規表示式嚴密阻擋 AWS 金鑰、GitHub PAT、OpenAI/Anthropic sk- 憑證與私鑰，防範意外洩漏。
- **週期性維護清單（`docs/monthly_consolidation.md`）**：
  建立每月定檢制度，歸檔已結案的過期項目，重整索引樹。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`agent-assets` 與 `ai-inbox`）的對照**：
  - 我們目前在 `C:\GitHub\agent-assets` 建立了跨 AI 共用規則與記憶庫，並透過 `CLAUDE.md` / `AGENTS.md` 達成單一事實來源（SSOT）。
  - Going Li 的「Claude Code + Antigravity + Hermes」三位一體分工與 `HANDOFF.md` 切片交接，印證了我們在本地多 Agent 分工上的可行性。
  - 顏志吉的 Hook 載入經驗提醒我們：**不能單靠無腦讀取最新 N 份紀錄**，必須搭配三跳索引協議，否則隨著專案疊代，Context 膨脹將吞噬有限預算。
  - Leoceeport 的 `ai-memory-template` 則提供了最關鍵的「防腐蝕檢查」與「糾正審查佇列」，能直接強化我們的協作穩定度。

- **採納與落地行動**：
  1. **跨平台記憶索引檢查工具（移植至 Python）**：
     - 原範本的 `check_index.sh` 依賴 bash/grep/sed，在 Windows 原生環境執行不便。
     - 在本 repo 中以 Python 3.11+ 實作跨平台的 `tools/check_memory_index.py`，支援掃描壞連結、未登錄檔案與索引過長門檻（>60 條）。
  2. **在 `agent-assets` 引入「糾正審查佇列（`correction-queue.jsonl`）」**：
     - 目前多個 Agent 在記錄 `lessons.md` 時均直接寫檔。引入 jsonl 格式的審核佇列，能使各 Session 的除錯反思先非同步排隊，再由主 Session 批次精煉收錄，杜絕規則主表混亂。
  3. **吸收三跳查詢協議至全域指引**：
     - 在 `agent-assets` 明訂索引指針與具體文檔的分層邊界，杜絕一次性載入全文造成的 Token 浪費。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261026-23`**｜**[優先級：高]** 撰寫「多 Agent 團隊共用記憶系統工程規範」收錄於 `docs/ai-shared-memory-engineering-spec.md`
  - **狀態**：🟡 進行中
  - **目標範圍**：`docs/ai-shared-memory-engineering-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳解三跳查詢協議（MEMORY.md $\to$ 主題索引 $\to$ 具體文檔）的 Context 預算控制原理。
    2. 定義動詞寫入契約、糾正審核佇列（`correction-queue.jsonl`）與單一權威審核機制。
    3. 規範索引防腐蝕門檻（超過 60 條拆分/歸檔）與 Git 原子同步退回機制。
  - **驗收標準（DoD）**：產出 `docs/ai-shared-memory-engineering-spec.md`，內含三跳架構拓撲、目錄結構範例與 Git 防線說明；以 `Test-Path docs/ai-shared-memory-engineering-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-24`**｜**[優先級：中]** 實作 `tools/check_memory_index.py` 跨平台記憶索引健檢工具與單元測試
  - **狀態**：🟡 進行中
  - **目標範圍**：`tools/check_memory_index.py` 與 `tests/test_check_memory_index.py`
  - **具體做法**：
    1. 以純 Python 3.11+ 實作索引健全性檢查器，完美相容 Windows 11 原生環境。
    2. 自動驗證：(1) 索引指向不存在檔案的壞連結、(2) 未編入索引的同層文檔、(3) 索引行數超過 60 條的過長警示。
    3. 撰寫單元測試覆蓋正常索引、壞連結、漏編檔案與過長條目。
  - **驗收標準（DoD）**：產出 `tools/check_memory_index.py` 與 `tests/test_check_memory_index.py`，通過 `python -m unittest discover -s tests -p "test_check_memory_index.py"`。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-25`**｜**[優先級：低]** 在 `C:\GitHub\agent-assets` 評估引進「糾正審查佇列（`correction-queue.jsonl`）」架構
  - **狀態**：🟡 進行中
  - **目標範圍**：`C:\GitHub\agent-assets\knowledge\` 與擴充評估文檔
  - **具體做法**：
    1. 評估各 Agent 在會話糾正時將教訓先寫入 `correction-queue.jsonl`，再由主 Session 審核合入 `lessons.md` 的操作流。
    2. 撰寫評估報告與資料綱要定義。
  - **驗收標準（DoD）**：產出評估紀錄收錄於 `agent-assets` 或 `ai-inbox` 文檔。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 共同大腦與跨環境同步**：
  - [AI 共同大腦跨環境實踐](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
- **上下文預算與技能工程**：
  - [GitHub 必裝 Skill 實測](./2026-10-26-github-trending-agent-skills-benchmark.md) ｜ 關聯任務：`T-20261026-17`、`T-20261026-18`
- **開源中繼與多代理協同**：
  - [Codync 開源 Agent 中繼](./2026-10-26-codync-open-source-agent-relay-fallback.md) ｜ 關聯任務：`T-20261026-20`
