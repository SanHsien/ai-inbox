---
id: 2026-10-26-ai-shared-memory-template-team-collaboration
title: "AI 共用記憶系統泛用範本解構：三跳索引、糾正審核佇列與 Git 機械防線的團隊記憶工程"
source_url: "https://github.com/Leoceeport/ai-memory-template"
source_platform: "GitHub (Leoceeport/ai-memory-template) / Facebook"
author: "Leoceeport"
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: pending
cluster: 1
cluster_role: "團隊共用記憶架構"
short_title: "AI 共用記憶範本解構"
tags:
  - shared-memory
  - git-workflow
  - context-optimization
  - correction-queue
  - index-health
  - secret-scanning
---

# AI 共用記憶系統泛用範本解構：三跳索引、糾正審核佇列與 Git 機械防線的團隊記憶工程

- **官方開源倉庫**：[`Leoceeport/ai-memory-template`](https://github.com/Leoceeport/ai-memory-template)
- **社群討論來源**：[Facebook 社團貼文討論串](https://www.facebook.com/groups/1224997379198346/permalink/1423729639325118)
- **分析主題**：跨人/跨 Agent 團隊共用記憶、三跳查詢防線（3-Hop Query Protocol）、動詞寫入契約、糾正審核佇列（Correction Queue）、索引健檢防腐蝕與 Git 機械防線
- **分析日期**：`2026-10-26`
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-19-ai-shared-brain-multi-agent-architecture.md`](./2026-10-19-ai-shared-brain-multi-agent-architecture.md)（多 Agent 共同大腦與跨環境同步）
  - [`notes/2026-10-26-github-trending-agent-skills-benchmark.md`](./2026-10-26-github-trending-agent-skills-benchmark.md)（熱門技能評估與上下文預算工程）
  - [`notes/2026-10-26-codync-open-source-agent-relay-fallback.md`](./2026-10-26-codync-open-source-agent-relay-fallback.md)（開源中繼與多代理協同）

---

## 1. 核心內容摘要與痛點剖析（Key Insights）

開發者 Leoceeport 在開源社群分享了專為工程團隊打造的 **`ai-memory-template`（AI 共用記憶系統泛用範本）**。該專案旨在解決多位工程師各自使用 Claude Code、Codex 或 Cursor 時的團隊級記憶斷裂：
1. **開新對話就失憶**：不同工作 Session 之間無法繼承歷史決策，工程師必須重複說明背景。
2. **各養各的 AI 導致規則打架**：不同成員的本機設定與 Prompt 互相衝突，難以維護統一的工程防線。
3. **多人接力斷線**：上一位開發者做過的架構決策與實施紀錄未能結構化沉澱，下一位接手者難以銜接。

### 1.1 核心解法：Git + Markdown + 機械防線
專案捨棄了複雜繁瑣、難以版本控制的外部向量資料庫（Vector DB），採用極簡且高度工程化的 **「Git 倉庫 ＋ 樹狀 Markdown 索引 ＋ 機械腳本驗證」** 體系，讓團隊成員與多個 AI 代理人共用同一個真實資料來源（SSOT）。

---

## 2. 深入技術拆解與架構原理（Deep Dive）

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

### 2.1 記憶讀寫的三大核心鐵律

1. **三跳查詢協議（The 3-Hop Query Protocol）**：
   - 傳統記憶系統最常犯的錯誤是將全部背景資料打包一股腦塞入 System Prompt，造成 Context 嚴重浪費與注意力稀釋。
   - 本範本嚴格規定：**「入口索引 $\to$ 主題索引 $\to$ 具體檔，最多三次查詢，嚴禁整包讀取」**。模型只讀取當前任務絕對需要的上下文片段。
2. **動詞寫入契約（Action-Verb Writing Contract）**：
   - 記錄必須由強動詞開頭（`implemented`、`fixed`、`decided`、`discovered`、`flagged`、`reversed`、`deferred`）。
   - 必須帶日期檔名或日期段落，直寫對應主題資料夾，並同時更新該資料夾的 `_index.md`。不具持久參考價值的事情「不寫就不寫」，防止記憶庫長出冗餘雜草。
3. **糾正審核佇列（Correction Queue & Single Gatekeeper）**：
   - 為防止多位成員或不同 Agent 隨意破壞最核心的規則主表（`domains/rules/rules_summary.md`），任何日常的糾正與教訓**嚴禁直接修改主表**。
   - 所有改動先追加至 `domains/lessons/correction-queue.jsonl`，由管理員或主負責人定期審核後才正式合入主表，實現規則的單一寫入權威。

### 2.2 四大機械腳本防線（Scripts & Hooks）

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
  - 我們目前在 `C:\GitHub\agent-assets` 建立了 SSOT 跨 AI 共用規則庫，在 `C:\GitHub\ai-inbox` 建立了任務與知識收件匣。
  - `Leoceeport/ai-memory-template` 提出的設計與我們的架構高度同頻，且在「多工程師團隊協作」與「防腐蝕索引管理」上提供了極佳的借鏡。

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
  - **目標範圍**：`docs/ai-shared-memory-engineering-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳解三跳查詢協議（MEMORY.md $\to$ 主題索引 $\to$ 具體文檔）的 Context 預算控制原理。
    2. 定義動詞寫入契約、糾正審核佇列（`correction-queue.jsonl`）與單一權威審核機制。
    3. 規範索引防腐蝕門檻（超過 60 條拆分/歸檔）與 Git 原子同步退回機制。
  - **驗收標準（DoD）**：產出 `docs/ai-shared-memory-engineering-spec.md`，內含三跳架構拓撲、目錄結構範例與 Git 防線說明；以 `Test-Path docs/ai-shared-memory-engineering-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-24`**｜**[優先級：中]** 實作 `tools/check_memory_index.py` 跨平台記憶索引健檢工具與單元測試
  - **目標範圍**：`tools/check_memory_index.py` 與 `tests/test_check_memory_index.py`
  - **具體做法**：
    1. 以純 Python 3.11+ 實作索引健全性檢查器，完美相容 Windows 11 原生環境。
    2. 自動驗證：(1) 索引指向不存在檔案的壞連結、(2) 未編入索引的同層文檔、(3) 索引行數超過 60 條的過長警示。
    3. 撰寫單元測試覆蓋正常索引、壞連結、漏編檔案與過長條目。
  - **驗收標準（DoD）**：產出 `tools/check_memory_index.py` 與 `tests/test_check_memory_index.py`，通過 `python -m unittest discover -s tests -p "test_check_memory_index.py"`。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-25`**｜**[優先級：低]** 在 `C:\GitHub\agent-assets` 評估引進「糾正審核佇列（`correction-queue.jsonl`）」架構
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
