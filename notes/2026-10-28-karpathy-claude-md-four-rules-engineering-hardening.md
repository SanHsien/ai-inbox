---
id: 2026-10-28-karpathy-claude-md-four-rules-engineering-hardening
title: "依 Karpathy 觀察整理的 CLAUDE.md 四大準則解構：從軟性文字勸導到機械硬閘門的工程加固實踐"
source_url: "https://www.threads.com/share/BAa3ZgQnJW/"
source_platform: "Threads (dev @easyanythinghk)"
author: "forrestchang（andrej-karpathy-skills，依 Andrej Karpathy 的觀察整理）/ dev (@easyanythinghk)"
analyzed_at: 2026-10-28
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "工程紀律與設計審查"
short_title: "Karpathy 四大原則工程加固"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 1
source_replies: 5
tags:
  - karpathy-rules
  - claude-md
  - agents-md
  - prompt-engineering
  - surgical-changes
  - goal-driven-verification
  - mechanical-invariants
---

# 依 Karpathy 觀察整理的 CLAUDE.md 四大準則解構：從軟性文字勸導到機械硬閘門的工程加固實踐

- **來源連結**：[Threads 貼文 (@easyanythinghk)](https://www.threads.com/share/BAa3ZgQnJW/)
- **核心來源**：[`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills)（原 `forrestchang/andrej-karpathy-skills`）——其他開發者依 Andrej Karpathy 在 X 的長文整理成的 `CLAUDE.md`，**不是 Karpathy 本人寫的**
- **分析主題**：Karpathy 程式碼行為四大黃金原則（Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Verification）、軟性提示詞衰減（Prompt Decay）防線、由文字勸導升級為機械硬閘門（Mechanical Invariants）之工程實務
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（AGENTS.md 規範驅動起步機制）
  - [`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](./2026-10-26-ai-shared-memory-template-team-collaboration.md)（三跳索引與動詞寫入契約）
  - [`notes/2026-10-26-github-trending-agent-skills-benchmark.md`](./2026-10-26-github-trending-agent-skills-benchmark.md)（8KB 上下文預算與防注意力稀釋）
  - [`notes/2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md`](./2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md)（確定性交付與自動化 DoD 驗證）

---

## 0. 原始資料盤點

> 2026-11-16 重審：未登入瀏覽器讀 Threads 貼文與留言串（文字、1 張作者圖、留言 5 則含作者 2 則）。

- **作者圖片**：圖 1 是套版的 GitHub Trending 標題卡，只有 repo 名稱 `andrej-karpathy-skills` 與一句英文副標（Karpathy 的 LLM 寫碼陷阱指南），沒有規則內容或實測畫面。
- **作者留言補充**：留言放 repo 連結 [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills)（原 `forrestchang/andrej-karpathy-skills`，舊網址會轉址）；回覆 bounce12340 時認同其出處更正。
- **網友留言重點**：
  - **出處更正（bounce12340）**：這個 repo 不是 Karpathy 本人寫的。Karpathy 今年 1 月在 X 發長文談模型會自己亂假設、把 100 行能解決的寫成 1000 行；之後其他開發者依這篇整理成 `CLAUDE.md`，README 也寫明是由他的觀察整理而來。Karpathy 原文還提到，他自己在 `CLAUDE.md` 寫過指示，這些問題照樣發生。
  - bounce12340 的做法：規則寫成「能檢查的句子」（例如門檻數字不准自己編、要先問），再讓另一個 bot 對著規則審稿。
  - mielm_ori：貼進去前先自己讀一遍，刪掉不適合專案的規則再存成專案的 `CLAUDE.md`；規則留少數幾條比整包照貼好管。
- **對分析的影響**：
  - **標題與作者欄更正**：原標題「Andrej Karpathy 版 CLAUDE.md」與貼文的「Karpathy 親手整理」都不對。已查證 README 第一行標題是 Karpathy-Inspired，內文寫 derived from Karpathy 的觀察並連到他的 X 貼文。標題改為「依 Karpathy 觀察整理的 CLAUDE.md」，作者欄改成 repo 作者，第 1 節補上出處說明。
  - **補上一個重要事實**：Karpathy 自己說過在 `CLAUDE.md` 寫了指示問題仍會發生。這正好支持本筆記第 2 節「文字規範會失效、要升級成機械檢查」的主軸，已寫進第 2 節開頭。
  - 留言的兩個做法（規則寫成可檢查的句子＋另一個 Agent 審稿、規則只留少數幾條）與本筆記的硬閘門方向一致，補在第 3 節。
  - 已完成的 `T-20261028-01` 當時就已分清 Karpathy 原話與 repo 整理，不需重開。repo 現況（2026-11-16）：約 23.4 萬星，GitHub 未偵測到授權檔。

---

## 1. 核心內容摘要：Karpathy 程式碼行為四大黃金原則（Key Insights）

AI 領域權威 Andrej Karpathy 在長期的 AI Coding 實踐中，指出了大型語言模型（如 Claude 3.5/3.7 Sonnet, GPT-4o, Codex）在撰寫代碼時的四種典型「毒性預設偏差」：
1. **盲目猜測**：需求模糊時自己腦補假設，做出錯誤的架構選擇；
2. **過度工程**：為了展現聰明，引入不必要的抽象層、未要求的架構與大量冗餘樣板；
3. **順手破壞**：修改一個小功能，卻擅自重構周圍無關的代碼、格式或註解，造成難以追蹤的 Git 污染；
4. **自欺欺人**：缺乏客觀檢驗標準，程式碼剛生出來就聲稱「已經修好了」，實質完全跑不通。

社群將 Karpathy 的觀察提煉為目前 GitHub 爆紅的專案級行為準則檔案（`CLAUDE.md` / `AGENTS.md`）。四條準則的文字是 repo 作者的整理，不是 Karpathy 的原話；Threads 貼文寫「Karpathy 親手整理」是錯的，留言已有人更正、貼文作者也認同（見第 0 節）：

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   Karpathy 版 AI Coding 行為四大黃金原則                               │
├───────────────────────────────┬────────────────────────────────────────────────────────┤
│ 原則名稱                      │ 核心規範指令 (Core Invariant)                          │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. 先想再動手                 │ Don't assume. Don't hide confusion. Surface tradeoffs. │
│    (Think Before Coding)      │ 拒絕盲猜；暴露矛盾困惑；主動列出方案權衡給人定奪。     │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. 極簡優先                   │ Minimum code that solves the problem.                  │
│    (Simplicity First)         │ Nothing speculative. 寫最少代碼解決問題，拒絕投機擴充。│
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. 外科手術式修改             │ Touch only what you must. Clean up only your own mess. │
│    (Surgical Changes)         │ 只動必須改動的行；絕不順便改其他代碼；保持目錄乾淨。   │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. 目標驅動與循環驗證         │ Define success criteria. Loop until verified.          │
│    (Goal-Driven Verification) │ 先定義客觀成功標準；進入「改碼-測試」循環直至真綠燈。  │
└───────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. 深入技術拆解：從「文字勸導」邁向「機械硬閘門」（Deep Dive）

> 2026-11-16 補：Karpathy 在原貼文自己提到，他在 `CLAUDE.md` 寫過指示，這些問題仍然發生（Threads 留言引述）。光靠規則檔不夠，正是本節要談的事。

雖然這四條原則在直覺上非常優雅，但一線資深開發者實測後往往發現：**純文字 Prompt 會隨上下文拉長而發生「軟性衰減（Prompt Decay）」**。當對話超過 50K 或 100K token 時，LLM 會遺忘「Surgical Changes」，再度開始漫無邊際地重構周遭檔案。

要真正馴服 AI Coding Agent，必須將 Karpathy 的四大原則**全面升級為「機械硬閘門（Mechanical Invariants）」**：

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                  Karpathy 四大原則：從文字勸導到機械硬閘門對照                         │
├───────────────────────────────┬────────────────────────────────────────────────────────┤
│ Karpathy 文字規範 (容易衰減)   │ 本 Session 工程硬閘門 (機械保證、永不失效)             │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Don't assume               │ ➔ 強制 SELECTIVE ROUTE 宣告 ＋ 方案對比表 (Tradeoffs)   │
│ 2. Simplicity First           │ ➔ 8KB 技能預算審計器 ＋ 零空殼 (Zero-Dummy) 靜態檢查   │
│ 3. Surgical Changes           │ ➔ Git Diff 範圍審查腳本 (檔案/行數超標自動拒止)        │
│ 4. Loop until verified        │ ➔ 外部裁判自動化 DoD 腳本 (Exit 0 綠燈才准回報完成)     │
└───────────────────────────────┴────────────────────────────────────────────────────────┘
```

### 2.1 硬閘門一：以 `SELECTIVE ROUTE` 與權衡表落實「Think Before Coding」
- **文字軟肋**：模型看到任務容易迫不及待直接呼叫 `edit_file` 或 `write_file`。
- **機械硬防線**：
  - 在執行任何修改前，強制在輸出首行進行 `SELECTIVE ROUTE: <solo|delegate>` 宣告，並列出選擇理由。
  - 遇到曖昧需求，強制列出「方案 A（最小侵入性）vs 方案 B（完整重構）」的成本與風險矩陣，未獲確認前嚴禁動手改碼。

### 2.2 硬閘門二：以「8KB 預算審計與零空殼」落實「Simplicity First」
- **文字軟肋**：模型喜歡寫大量的包裝類別（Wrapper）、預留未使用的工廠介面與泛型。
- **機械硬防線**：
  - 部署 `tools/audit_skills_context_budget.py`，嚴密控制所有提示詞與模組大小在 8KB 內，防範注意力稀釋。
  - 全域規則強制禁止 `// TODO`、`pass` 或回傳假資料的空殼函式，由靜態 AST 檢查器抓出未使用的投機結構。

### 2.3 硬閘門三：以 `tools/audit_surgical_diff.py` 落實「Surgical Changes」
- **文字軟肋**：模型動了目標函式，順手格式化整個檔案，導致 `git diff` 出現上百行無意義的空白或逗號變更。
- **機械硬防線**：
  - 實作前置/後置 Git 檢查：每次改動後自動執行 `git status` 與 `git diff --stat`。
  - 若偵測到任務範圍外的未授權檔案改動，或變更行數超過預期閾值，腳本自動觸發警報並要求回滾（Rollback），徹底消滅雜質提交。

### 2.4 硬閘門四：以「外部裁判自動化 DoD」落實「Goal-Driven Verification」
- **文字軟肋**：模型自稱「已修復」，實質未跑過任何單元測試，甚至註解掉失敗的測試來假裝通過。
- **機械硬防線**：
  - 嚴格落實全域規則：「回報完成之前，要真的執行過檢查並貼出它的真實輸出」。
  - 結合本 repo 的 `verify_inbox.py` 與 `tools/generate_dod_verifier.py`，以獨立進程執行 exit code 檢查，非 0 一律視為失敗，杜絕任何口頭承諾。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有資產（`agent-assets` 與 `ai-inbox`）的整合**：
  - 我們目前在 `agent-assets/rules/GLOBAL_RULES.md` 與 `AGENTS.md` 中已經蘊含了類似的紀律精神。
  - 將 Karpathy 的「四大原則」作為頂層架構框架收錄，並轉化為標準的範本與驗證工具，能使所有多 Agent（Claude Code, Antigravity, Codex, Hermes, Grok Bot）具備完全一致的行為準繩。

- **採納與落地行動**：
  1. **撰寫規格指南**：產出 `docs/karpathy-rules-mechanical-hardening-spec.md`，詳解四大原則與對應的機械硬防線實作。
  2. **開發 Surgical Changes 審查工具**：實作 `tools/audit_surgical_diff.py`，提供自動判定代碼變更是否符合外科手術式修改之檢查器。
  3. **產出加固版範本**：在 `templates/karpathy-hardened-agents-md.md` 產出開箱即用的 `CLAUDE.md` / `AGENTS.md` 範本，供其他專案一鍵復用。

- **留言帶來的兩個做法（2026-11-16 補）**：
  - 規則寫成能檢查的句子（例如「門檻數字不准自己編，要先問」），再讓另一個 Agent 對著規則審稿——等於替規則加測試。維護者現有的獨立審查與 hook 已是這個方向。
  - 貼進專案前先刪掉不適用的規則，只留少數幾條；整包照貼反而難管。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261028-01`**｜**[優先級：高]** 撰寫「Karpathy 四大原則工程加固指引：從 Prompt 到硬閘門」收錄於 `docs/karpathy-rules-mechanical-hardening-spec.md`
  - **目標範圍**：`docs/karpathy-rules-mechanical-hardening-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 系統性解構 Karpathy 四大原則（Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Verification）的背景與底層痛點。
    2. 定義對應的機械化防線：SELECTIVE ROUTE 前置宣告、8KB 預算上限、Surgical Diff 邊界審查與客觀 DoD 外部裁判。
    3. 提供多 Agent 協同（Claude Code, Codex, Antigravity）的統一整合實例。
  - **驗收標準（DoD）**：產出 `docs/karpathy-rules-mechanical-hardening-spec.md`，內含四大原則架構拓撲、硬閘門對照矩陣與範例說明；以 `Test-Path docs/karpathy-rules-mechanical-hardening-spec.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：docs/karpathy-rules-mechanical-hardening-spec.md：分清 Karpathy 貼文原話與 forrestchang repo 的整理（commit 8462496、2c60614），筆記的 token 衰減數字標未驗證；獨立審查逐字核對貼文與 commit 相符。

- [x] **`T-20261028-02`**｜**[優先級：中]** 實作「外科手術式修改（Surgical Changes）Git 變更範圍審查工具」於 `tools/audit_surgical_diff.py`
  - **目標範圍**：`tools/audit_surgical_diff.py` 與 `tests/test_audit_surgical_diff.py`
  - **具體做法**：
    1. 讀取 `git diff` 輸出，比對當前修改的檔案列表是否超出任務授權的目標範圍（Scope）。
    2. 檢查非預期的周邊空白重排、註解抹除或跨目錄越界改動，超過閾值回傳非 0 並列出越界檔案。
    3. 撰寫單元測試覆蓋正常小範圍修改、越界檔案攔截與大範圍無效重構偵測。
  - **驗收標準（DoD）**：產出 `tools/audit_surgical_diff.py` 與單元測試，執行測試全綠通過。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：tools/audit_surgical_diff.py＋tests/test_audit_surgical_diff.py：以真實 git repo 測範圍、改名、刪除、子模組、空白、註解抹除；給 --head 用 merge-base，head 是 base 祖先時 exit 2。審查兩輪修正 SQL 註解、子模組越界、main 前進誤報、參數寫反假綠，重現步驟重跑全過。

- [x] **`T-20261028-03`**｜**[優先級：低]** 產出標準化「Karpathy-Style CLAUDE.md / AGENTS.md 範本」收錄於 `templates/karpathy-hardened-agents-md.md`
  - **目標範圍**：`templates/karpathy-hardened-agents-md.md`
  - **具體做法**：
    1. 融合 Karpathy 四大原則與本 repo 實戰硬閘門，打造標準化 Markdown 範本。
    2. 範本內含清晰的專案進入點宣告、Scope 限制清單、DoD 定義區塊與反模式警示。
    3. 相容 Claude Code、Antigravity 與 Codex CLI。
  - **驗收標準（DoD）**：產出 `templates/karpathy-hardened-agents-md.md`，內含完整結構與中英雙語註解；以 `Test-Path templates/karpathy-hardened-agents-md.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：templates/karpathy-hardened-agents-md.md：可填空的 AGENTS.md 範本，每條行為規則附機械後盾；出處放在範本本體，授權現況照實寫（README 寫 MIT、該 commit 無 LICENSE 檔）。獨立審查 PASS。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **規範驅動與多 Agent 派工**：
  - [多 Agent 生產力工廠實戰架構](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261026-28`
  - [GPT Work / Codex 之 AGENTS.md 規範驅動起步](./2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md) ｜ 關聯任務：`T-20261026-29`
- **防腐蝕與三跳查詢協議**：
  - [AI 共用記憶系統全景分析](./2026-10-26-ai-shared-memory-template-team-collaboration.md) ｜ 關聯任務：`T-20261026-23`、`T-20261026-24`
- **上下文預算與技能工程**：
  - [GitHub 必裝 Skill 實測與 8KB 預算](./2026-10-26-github-trending-agent-skills-benchmark.md) ｜ 關聯任務：`T-20261026-17`、`T-20261026-18`
- **確定性交付與自動化 DoD**：
  - [AI 接案的確定性交付工程](./2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md) ｜ 關聯任務：`T-20261026-32`、`T-20261026-34`
