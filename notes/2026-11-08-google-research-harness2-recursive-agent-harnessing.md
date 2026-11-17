---
id: 2026-11-08-google-research-harness2-recursive-agent-harnessing
title: "Google Research 開源 Harness²（Harness Squared）：無標準答案開放世界的雙層遞迴 Agent Harness 自我優化框架"
source_url: "https://www.threads.com/share/_toE5mWj3"
source_platform: "Threads (@wayturn_) / GitHub (google-research/harness2)"
author: "偉騰 (@wayturn_) / Google Research (Ruiyao Xu, Tomas Pfister et al.)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "工程紀律與設計審查"
short_title: "Google Harness²雙層遞迴優化"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 7
source_replies: 41
tags:
  - google-research
  - harness2
  - agent-harness
  - recursive-optimization
  - context-engineering
  - benchmark-contamination
---

# Google Research 開源 Harness²（Harness Squared）：無標準答案開放世界的雙層遞迴 Agent Harness 自我優化框架

- **來源連結**：[Threads 原文分享](https://www.threads.com/share/_toE5mWj3) ｜ [貼文永久網址 (@wayturn_)](https://www.threads.com/@wayturn_/post/DfR0PG7mTz6) ｜ [GitHub (google-research/harness2)](https://github.com/google-research/harness2) ｜ [官方論文 (arXiv:2610.14224)](https://arxiv.org/pdf/2610.14224)
- **核心作者**：偉騰（`@wayturn_`）／ Google Research（Ruiyao Xu, Yanfei Chen, Zhongying CuiZhu, Bhavana Dalvi Mishra, Yifei Ming, Han Yu, Rujun Han, Chen-Yu Lee, Tomas Pfister）
- **分析主題**：剖析 Google Research 開源的 **Harness²（Harness Squared：Recursive Agent Harnessing for an Open World）**（23,026 Stars、2,301 Forks，快照日 2026-11-08；2026-11-16 為 24,072 Stars、2,422 Forks；Apache-2.0 License），在固定語言模型權重且無須標準答案（without ground-truth feedback）的開放世界任務中，透過雙層遞迴（Task-level `Propose–Probe–Compose` 與 Harnessing-level `Experience Reflector`）自動精煉 8 大外部 Harness 模組；並檢視其官方 README 揭露之「關閉沙盒與無網路限制導致公開 Benchmark 答案洩漏」防弊邊界。
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md`](./2026-11-08-agent-autoloop-event-sourcing-zero-cost-suspend.md)（Agent Autoloop 事件溯源與 8 跳 TTL 熔斷防線）
  - [`docs/external-judge-audit.md`](../docs/external-judge-audit.md)（外部裁判防弊與驗證器設計規範）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看 Threads 貼文：貼文文字（當時記為無圖，實際有 2 張輪播圖，見下方 2026-11-17 補讀）、留言 19 則（含作者 8 則；貼文標示 37 則回覆，其餘要登入才看得到；留言是捲到才載入，逐段捲動收集）、作者留言裡的 GitHub 連結預覽卡。另看 GitHub README 的 3 張架構圖，並以 GitHub API 讀最近 8 則 issue／PR 的標題與摘要、其中 #201 讀全文與 1 則回覆。README 的安裝示範 GIF 未看。

- **作者圖片**：首輪看過的 4 張（貼文的 2 張輪播圖當時漏看，見下方 2026-11-17 補讀）：
  - 圖 1（留言區的 GitHub 連結預覽卡）：repo 名稱與統計數字（約 24k Stars、2k Forks、10 位貢獻者）。
  - 圖 2（README 流程圖）：左邊大框是 Task-Level Recursion，依序為 Agent Executor（拿初始 harness 跑出軌跡與產出）→ Harness Editor（提出 Invariant 與 Domain 兩類修改）→ Candidate Probes（兩類候選各自試跑）→ Harness Composer（合併定稿）；右邊是 Harnessing-Level Recursion，Experience Reflector 反思後更新 Improvement Harness，再帶到下一個任務。
  - 圖 3（README 元件圖）：8 個元件依執行期角色分組並標了檔名與注入時機：Context construction 有 system prompt、guardrails、memory（這三個每次呼叫都注入）與 skills（呼叫時才載入）；Tool interface 有 tool guidance（每次呼叫）與 scripts（經 bash 執行）；Orchestration 有 subagents（經 task 工具）；Middleware 有 plugin（攔截每次工具呼叫，不經模型裁量）。中間是凍結的模型。
  - 圖 4（README 擴展模式圖）：Parallel 是 K 組候選各自獨立、最後一起合成；Sequential 是每一步把上一步的結果與累積證據帶到下一步。
- **作者留言補充**：
  - 貼出 repo 連結。
  - 回覆網友時補了一個原貼文沒寫的保留：**試跑與調整本身也會吃 token，能不能省回來要看後面用多少次**。
  - 回覆權限邊界的留言時表示認同：能調流程不代表能自己擴權。
  - 用一句話解釋原理：提出幾種提示詞與工具使用規則的改法，拿同一個任務試跑，再看執行差異組合出新設定。
- **網友留言重點**：
  - `alert.human`：只改流程不換模型像是在省成本；被作者提醒前期成本後，同意只用一兩次不一定划算。
  - `applechisonnkonn`：能迭代的只能是流程設定，權限與對外動作不能一起放開，對外訊息要留人工確認。
  - `more.yu_` 與作者的一串往返：流程自己進化的代價是說不清它為什麼有效，哪天在沒人看的任務上走歪，連要回滾到哪一版都不知道。作者回覆設定版本與執行紀錄要一起留，並說「這次有效、換個任務還有沒有效」才是更值得追的問題。
  - `hanbingjheng` 說這讓調 agent 像做實驗；作者補一句：**看得出行為變了，跟確認真的變好，是兩件事**（與下面 issue #201 的實測結果正好呼應）。
  - **GitHub issue #201（第三方實測，2026-11-12）**：回報者把 Propose–Probe–Compose 與持久化的 improvement harness 移植到自己的 agent CLI，在 WorkBuddy-Bench v1.0 的 code 與 office 子集跑兩輪自測。第一輪 80 組配對任務（k=1、parallel）整體分數由 0.890 變 0.877；第二輪 28 組（k=3、刻意挑掉接近滿分的題目）由 0.827 變 0.824，**兩輪都量不到分數提升**。機制本身有在運作（七成以上任務採用了與原本不同的 harness），token 降到約 0.91 倍、回合數與工具錯誤略降。回報者自己列的可能原因：基準分數已高、k 小時候選常常一模一樣、被採用的修改多半只改過程不改產出、效果與重跑雜訊同量級、執行器與論文不同。截至讀取時官方尚未回覆。
  - 其餘近期 issue／PR 多是正確性修補（不同任務 ID 正規化後撞到同一個目錄、評分綁到舊的執行結果等），顯示評測管線本身還在修。
- **2026-11-17 登入補讀**：
  - **更正：貼文其實有 2 張圖**（輪播），首輪寫「無圖」是漏看。圖 5 是 README 開頭的截圖：Harness² 字標、副標「Recursive Agent Harnessing for an Open World」、四個徽章（論文、網站、基準測試文件、Apache 2.0 授權）與一行指令 `harness2 --bench jb --k 1 --mode parallel`。圖 6 是 README 流程圖的裁切，內容與上面的圖 2 相同。兩張都直接取自 repo，沒有作者自己的實測畫面。
  - **圖 7（README 的安裝示範 GIF）**：只是終端機打字動畫，依序打出三行指令：`uv pip install -e '.[render]'`、`harness2-setup jb`、`harness2 --bench jb --k 1 --mode parallel`，沒有顯示執行輸出或結果。
  - **Threads 留言**：登入後以「熱門」「最新」兩種排序各捲到底、子回覆全部點開，共讀到 32 則（含作者 9 則）；貼文標示 37 則，其餘 5 則平台不顯示。加上先前讀的 GitHub issue／PR 9 則，共 41 則。新讀到的是 `more.yu_` 那串的後半：他追問「連這次為什麼有效都說不清，換任務只能重抽一次，有效的那次到底留下什麼可複用的東西」，作者回說連有效的定義都講不清楚是人的問題；`laglms` 接著分享自己的做法——每次有效的設定寫成三行（任務是什麼、改了什麼、為什麼有效），寫不下來的就當成運氣；`more.yu_` 補充第三行才是判斷，多數人只寫前兩行。`fix_norma` 問原理（作者的一句話解釋已列在上面）。其餘是「存」「留」。
  - **GitHub issue #201**：2026-11-17 以 API 重查，仍只有回報者自己補證據的 1 則留言，官方尚未回覆，狀態仍是開啟。
- **對分析的影響**：
  1. **第 3 節的基準數據要加一個反例**：原筆記只列論文的提升幅度。現在補上 issue #201 的第三方實測（不同執行器與模型，量不到提升），並把結論寫成「論文配置內有提升；換執行器後能否重現未獲證實」。
  2. **補成本面**：作者自己在留言承認試跑會吃 token。第 3 節補一句：Propose–Probe–Compose 每個任務至少多跑數次候選，前期成本要靠重複使用攤回。
  3. **第 2 節補上元件圖的細節**（各元件的注入時機），原筆記的方塊圖只有分組、沒有這一層。
  4. Stars 數字更新註記：分析主題寫的 23,026 Stars 是 2026-11-08 的快照，2026-11-16 以 API 查為 24,072 Stars、2,422 Forks。
  5. 已完成的 `T-20261108-03` 不改狀態；其產出文件需不需要補上述反例，列在本次重審的回報裡交整合者決定。無新增任務。
  6. **2026-11-17 補讀**：貼文兩張圖與 GIF 都是 repo 現成素材，沒有新的事實；留言新增的「三行紀錄」做法與第 3 節「改了行為不等於變好」的結論同方向，是使用者經驗、不是對 Harness² 的實測。分析結論不變，無新增任務。

---

## 1. 資訊初篩（5W1H）

- **Who**：Google Research 團隊（Ruiyao Xu, Tomas Pfister 等）開源，由偉騰（`@wayturn_`）於 Threads 整理分享。
- **What**：開源 **Harness²（Harness Squared）**（[`google-research/harness2`](https://github.com/google-research/harness2)），一套在不修改底層語言模型權重（Frozen Weights）、且**無須依賴標準答案（without ground-truth feedback）**的開放世界環境中，透過雙層遞迴自動精煉 Agent 外部控制架構（Harness）的系統。
- **Where**：
  - Threads 原文：`https://www.threads.com/@wayturn_/post/DfR0PG7mTz6`（短網址：`https://www.threads.com/share/_toE5mWj3`）
  - 官方 GitHub：`https://github.com/google-research/harness2`
  - 官方論文：[arXiv:2610.14224](https://arxiv.org/pdf/2610.14224)（*Harness²: Recursive Agent Harnessing for an Open World*）
  - 專案首頁：`https://harness2.github.io`
  - 社群延伸導讀（未查證）：`https://medium.com/@simon3458/ai-agent-harness-squared-intro-bdb182241a04`
- **When**：2026 年 10 月發表論文並開源，2026 年 11 月納入知識庫分析。
- **Why**：真實世界的複雜長程任務（辦公室文件處理、網頁操作、跨檔案軟體工程、法律審查）缺乏可即時計算 Reward 的 Ground Truth。傳統 Prompt Optimizer 需要驗證集標準答案打分；Harness² 改用「同任務多候選執行軌跡的行為對照（Behavioral Contrasts）」來驅動外部 8 大 Harness 模組演化。
- **How**：在單一任務內執行 **Task-level recursion（`Propose–Probe–Compose` 對比精煉）**，並在任務結束後透過 **Harnessing-level recursion（`Experience Reflector` 經驗蒸餾）** 將經過實證的修改規則寫入持久化的 *Improvement Harness* 資料庫。

---

## 2. 核心架構與 8 大可編輯 Harness 模組

Harness² 將包覆在基礎模型外部的執行環境拆解為 **4 大執行期角色、8 個可編輯模組**：

```
+-------------------------------------------------------------------+
|                     Agent Harness (8 Modules)                     |
+---------------------------------+---------------------------------+
| 1. Context Construction         | 2. Tool Interface               |
|   - system prompt (系統提示詞)  |   - tool guidance (工具使用指南)|
|   - guardrails (安全與格式護欄) |   - scripts (輔助執行腳本)      |
|   - memory (長短期記憶狀態)     |                                 |
|   - skills (領域知識與工作流)   | 4. Middleware                   |
| 3. Delegation                   |   - plugins (執行期攔截與日誌)  |
|   - subagents (子代理角色配置)  |                                 |
+---------------------------------+---------------------------------+
```

各元件何時進入模型的視野（依 README 元件圖，2026-11-16 補）：`system prompt`、`guardrails`、`memory`、`tool guidance` 每次呼叫都注入；`skills` 被呼叫時才載入；`scripts` 經 bash 執行；`subagents` 經 task 工具派出；`plugins` 攔截每一次工具呼叫，不經模型裁量。

### 雙層遞迴機制（Two Levels of Recursion）

```
[Level 1: Task-Level Recursion (單一任務內無標準答案對比精煉)]
  初始執行 (Initial Run)
       │
       ▼
  Harness Editor (Propose) ──► 產生兩類修改方案：
       ├─ General / Invariant (通用型優化)
       └─ Domain-Specific (領域專用優化)
       │
       ▼
  Candidate Probes (Probe) ──► 在同一任務上平行/序列試跑 K 個候選 Harness
       │
       ▼
  Harness Composer (Compose) ─► 對比各軌跡行為差異 (Behavioral Contrasts)，合成最佳 Harness

[Level 2: Harnessing-Level Recursion (跨任務經驗累積)]
  任務結束後執行器重置 (Executor Reset)
       │
       ▼
  Experience Reflector ──────► 萃取有證據支撐的教訓 (Evidence-supported lessons)
                               寫入持久化 Improvement Harness，指導未來新任務的 Editor
```

1. **平行與序列擴展模式（Scaling Modes）**：
   - `--mode parallel --k K`：廣度探索（Breadth），同時探測 $K$ 個通用型與 $K$ 個領域型候選配置後一次合成。
   - `--mode sequential --k K`：深度精煉（Depth），將合成後的 Harness 與累積軌跡證據連續迭代 $K$ 輪。
2. **雙執行基底支援（Substrates）**：
   - 支援預設的 `OpenCode` 以及 `Codex`（`--substrate cx`）。

---

## 3. CQR 品質檢驗與基準測試剖析

### 論文基準數據核驗

> 下表基準值來自論文，未逐一核對。

| 基準測試 (Benchmark) | 涵蓋領域 | 基礎配置表現 | Harness² 優化後表現 | 淨提升幅度 |
| :--- | :--- | :--- | :--- | :--- |
| **WorkBuddy-Bench** | `office` / `web` / `code` | Gemini 3.5 Flash (`72.4`) / GLM-5 (`64.2`) | Gemini 3.5 Flash (`80.8`) / GLM-5 (`75.7`) | **+8.4 分** / **+11.5 分**（單步 `K=1`） |
| **JobBench** | 專業知識工作任務 | 基準 Harness | 雙層遞迴精煉 Harness | 最高 **+4.5 分** |
| **LAB (Legal Agent Benchmark)** | 複雜法律條文與合約推理 | 基準 Harness | 雙層遞迴精煉 Harness | Partial pass rate 最高 **+11.8%** |

**第三方重現與成本（2026-11-16 補）**：

- GitHub issue [#201](https://github.com/google-research/harness2/issues/201)（2026-11-12）有人把同一套迴圈移植到自己的執行器，在 WorkBuddy-Bench 的 code 與 office 子集用兩個模型跑了兩輪（80 組與 28 組配對任務），兩輪都量不到分數提升（0.890 → 0.877、0.827 → 0.824），只看到 token 與回合數略降。回報者列出的可能原因包含基準分數已高、候選常常相同、修改多半只改過程、效果與雜訊同量級、執行器與論文不同；官方尚未回覆。所以上表的提升只能讀成「論文配置內的結果」，換執行器或模型後能否重現未獲證實。
- 貼文作者在留言提醒：試跑與調整本身會吃 token。每個任務至少要多跑數次候選，這筆前期成本要靠調好的 harness 被重複使用才攤得回來。

### 工程與安全邊界批判（Critical Audit）

檢視 [`google-research/harness2` 官方 README](https://github.com/google-research/harness2) 的 `Web access` 節，官方明確揭露了一項重大評估與安全風險：

> *"Executor network access is unrestricted, and Codex runs with its sandbox disabled. Public benchmark rubrics may be accessible online. Before evaluation, configure network restrictions to prevent access to benchmark answers and grading criteria."*

1. **基準汙染與作弊風險（Benchmark Contamination / Reward Hacking）**：
   - 在 `--substrate cx`（Codex）或 `OpenCode` 預設配置下，執行器關閉了沙盒且擁有無限制的對外網路存取權。
   - 當 Agent 在 `Candidate Probes` 階段遇到公開基準（如 WorkBuddy-Bench 或公開 GitHub 上的題庫）時，自主編寫的 `scripts` 或 `tool guidance` 可能直接透過網路搜尋抓回公開的評分標準（Rubrics）甚至標準答案，導致「行為對照（Behavioral Contrasts）」挑選出會上網偷看答案的 Harness。
2. **無沙盒自動生成腳本的宿主機風險**：
   - Harness² 允許 `Harness Editor` 動態生成並修改 `scripts` 與 `plugins`，若在無沙盒（sandbox disabled）環境下連續執行 $K$ 個候選 Probe，一旦生成具破壞性的 Shell/Python 指令，將直接危及宿主機檔案系統與憑證。

---

## 4. 與本庫架構之對映與吸收價值

| Harness² 模組 | 本庫對應實作 | 差距與優化空間 |
| :--- | :--- | :--- |
| `system prompt` / `guardrails` | `AGENTS.md`、`GEMINI.md`、`tools/verify_*.py` | 已具備硬閘門，可引入「通用 vs 領域」雙軌變更分類。 |
| `memory` / `Experience Reflector` | `notes/`、`docs/`、`checkpoint` / `neat-freak` | 可定義標準化的「軌跡對照證據（Behavioral Contrast Evidence）」欄位。 |
| `skills` / `tool guidance` / `scripts` | `.gemini/config/skills/`、`tools/*.py` | 當腳本或規則在 Probe 失敗時，應強制檢查是否違反沙盒與網路隔離契約。 |
| `subagents` / `plugins` | `invoke_subagent`、Pre/Post-tool Hooks | 需防範子代理在評估模式下繞過沙盒或觸發無限制外網抓取。 |

---

## 5. 拆解待辦事項（Action Items）

- [x] **`T-20261108-03`**｜**[優先級：高]** 撰寫《Harness² 雙層遞迴與 8 大模組演進及防弊規範》（`docs/harness2-recursive-agent-harnessing-spec.md`）
  - **目標範圍**：`docs/harness2-recursive-agent-harnessing-spec.md`
  - **具體實作步驟**：
    1. 定義 8 大可編輯 Harness 模組（`system prompt`, `guardrails`, `memory`, `skills`, `tool guidance`, `scripts`, `subagents`, `plugins`）至本庫與本地多 Agent 架構的映射表及驗證閘門。
    2. 規範無標準答案任務的第一層遞迴（Task-Level `Propose–Probe–Compose` 對比精煉流程）與第二層遞迴（Harnessing-Level `Experience Reflector` 經驗蒸餾三項證據門檻）。
    3. 針對 `google-research/harness2` 預設關閉 Codex 沙盒且未限制網路存取的問題，制定「沙盒強制開啟與基準 Rubric 網域隔離」防弊安全契約。
  - **驗收標準（DoD）**：
    - 產出 `docs/harness2-recursive-agent-harnessing-spec.md` 並通過 `python tools/build_index.py` 與 `python tools/verify_inbox.py` 契約及 100% 目錄覆蓋率校驗。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正（2026-11-14）：+11.8 改為「個百分點」並標明是作者報告的 LAB partial pass rate；答案洩漏改寫為官方 Web access 章節揭露的風險，註明本庫沒有已發生洩漏的證據。
