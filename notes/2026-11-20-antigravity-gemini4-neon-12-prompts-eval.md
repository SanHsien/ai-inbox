---
id: "2026-11-20-antigravity-gemini4-neon-12-prompts-eval"
title: "Woshipm 長文評估：Gemini 4 Neon 實測基準、Antigravity 12 項配置與第三方插件零信任審查"
source_url: "https://www.woshipm.com/ai/6497136.html"
source_platform: "woshipm (人人都是產品經理)"
author: "饼干哥哥"
github_repo: "https://github.com/DeusData/codebase-memory-mcp"
analyzed_at: "2026-11-20"
analyzed_by: "antigravity"
source_review: full
source_images: 22
source_replies: 0
source_reviewed_at: "2026-11-21"
status: done
cluster: 3
cluster_role: "AGY與Neon實戰配置"
short_title: "AGY十二配置與Neon"
tags:
  - antigravity
  - gemini-4-neon
  - gemini-4-hydrogen
  - codebase-memory-mcp
  - agy-fast-io
  - model-routing
---

# Woshipm 長文評估：Gemini 4 Neon 實測基準、Antigravity 12 項配置與第三方插件零信任審查

- **來源文章**：[美国大豆包翻身了！12个提示词用满血Antigravity吊打Claude（人人都是產品經理）](https://www.woshipm.com/ai/6497136.html)
- **文中相關開源專案（經外部搜尋核實）**：
  - [`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp)（Tree-sitter AST + LSP 本地程式碼知識圖譜 MCP）
  - [`oil-oil/agy-fast-io`](https://github.com/oil-oil/agy-fast-io)（非官方 Antigravity 批量讀取規則插件）
- **官方來源（2026-11-21 查閱）**：[Gemini 4 Neon 模型卡](https://deepmind.google/models/model-cards/gemini-4-neon/)（2026-11-18）、[Neon 評測方法 PDF](https://deepmind.google/models/evals-methodology/gemini-4-neon)、[Gemini 4 Hydrogen 模型卡](https://deepmind.google/models/model-cards/gemini-4-hydrogen/)（2026-11-12）、[Antigravity 部落格：Neon](https://antigravity.google/blog/gemini-4-neon-in-google-antigravity)、[Antigravity 部落格：Hydrogen 與 Orchestrator](https://antigravity.google/blog/gemini-4-hydrogen-in-google-antigravity)、[Gemini API 價格頁](https://aistudio.google.com/docs/pricing)
- **發布平台 / 作者**：`woshipm` / `饼干哥哥`（`2026-11-20`）
- **分析日期**：`2026-11-20`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-11-18-gemini-4-carbon-argon-swarm-evals.md`](./2026-11-18-gemini-4-carbon-argon-swarm-evals.md)（Gemini 4 Carbon / Argon 與 `/swarm`）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](./2026-11-20-gemini-decision-1-decisions-api-eval.md)（Gemini Decision 1 路由與校準）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型速查表）

---

## 1. 原始資料盤點（正文、22 張圖片與評論區）

- **Gemini 4 全系列與 Neon 官方數據（圖 2、圖 3、圖 4、圖 6、圖 18）**：
  - **四款分工**：`Carbon`（$4/$20，11/30 前 $2/$10，長週期研究）、**`Neon`（$3/$15，Pro/Ultra 可用，AA 61，軟體工程與長上下文主力）**、`Hydrogen`（$1.5/$7.5，極速日常執行）、`Argon`。
  - **Neon vs Opus 5.5 vs GPT-6.2 Sol（圖 3 DeepMind 基準）**：`GraphWalks 256k–1M` Neon 達 **95.2%**（vs Sol 80.1%、Opus 5.5 66.8%）、`CursorBench 4.1` 65.4%、`SWE-sweep` 39.0%、`SEC-bench Pro` 90.5%；`Terminal-bench 4.1`（65.2% vs Opus 5.5 65.8%）與 `FrontierCode 2.0`（46.2% vs Opus 5.5 47.3%）仍以 Opus 5.5 些微領先。
  - **成本與幻覺率**：`JAZII` 同題實測 Neon 約 `3.5`（20m，原貼文沒寫幣別）vs Opus 5.5 `$7.2` (18m)，但同一則貼文的結論是 Opus 輸出仍好得多【社群實測，單次】；`AA-Omniscience` 幻覺率 Carbon 4% / Hydrogen 8%（Sonnet 5.5 43% 只在正文）【未查證】。圖 18 顯示 `Carbon 規劃＋Hydrogen 執行` 在 Terminal-Bench 4.1 省 24% 額度、提速 19%（數字出自官方部落格的 Carbon 版，Neon 版沒有公布數字；2026-11-21 重審改正）。
  - **風控警告（圖 13）**：文章轉貼第三方 X 貼文，警告 Google 嚴查共用 IP 與跨區帳號、主帳號封禁會波及 Gmail、Drive 與 GCP。但文章本身第一步就是建議走土耳其區禮品卡訂閱（圖 12），反對的只是免費領取活動（2026-11-21 重審改正，原稿把文章的立場寫反了）。
- **Antigravity 12 項配置提示詞盤點**：
  - 涵蓋：(1) 沙盒與工作區邊界、(2) 強制驗證禁絕對詞、(3) `verbosity: low`＋中文進度同步、(4) 安裝 `oil-oil/agy-fast-io` 批量快讀、(5) `/swarm` 派 Hydrogen、(6) `chrome-devtools-plugin`＋禁止高飽和前端色塊、(7) 清理多餘全域 skills、(8) 預設 `Orchestrator (Neon)` 防抽干 Claude 池、(9) `/grill-me`→`/plan`→`/goal`→`/learn`、(10) 遙測與 `AGY_CLI_HIDE_ACCOUNT_INFO=1`/`AGY_CLI_HIDE_LOGO=1` 隱藏隱私、(11) `codebase-memory-mcp` + Cloud Remote + Turbo、(12) `/remote-control` 手機監控。
- **評論區**：`0` 則留言（2026-11-21 重審：頁面顯示「目前还没评论」，JSON-LD 的 `commentCount` 為 0；正文那句「求评论区分享」是作者的話，不是留言）。
- **22 張圖逐張盤點（2026-11-21 重審逐張開啟）**：
  - 圖 1 題圖（Unsplash 的 Google 霓虹字照片）；圖 9 作者頭像橫幅；圖 5 是動態 GIF（開啟時停在 Nano Banana 生成的霓虹招牌畫面，正文說是 Neon 把照片渲染成 3D 表格的官方演示）。
  - 圖 2：APPSO 製作的三款模型對比卡（資料來源標 Google、2026-11-18）：Carbon AA 60、$4／$20（11-30 前 $2／$10）、限 Ultra；Neon AA 61、$3／$15、Pro 與 Ultra；Hydrogen AA 54、$1.5／$7.5、面向所有人。
  - 圖 3：Neon 對 Opus 5.5、GPT-6.2 Sol 的基準表，與 DeepMind 模型卡的表格**完全相同**（含 SWE-sweep 兩種執行框架、Terminal-bench 4.1 註明「作弊校正後正確率」）。
  - 圖 4：JAZII 的 X 貼文截圖（中文翻譯版）：同一提示、最高推理，Neon 20 分鐘、成本約 3.5（**沒寫幣別**），Opus 5.5 18 分鐘、約 7.2 美元；貼文最後一句是「**Opus 仍然表現好得多**，但 Google 追得很快」。原稿只寫成本，漏了這句結論，已補。
  - 圖 6：AA-Omniscience 幻覺率長條圖的**裁切畫面**，只看得到 Carbon 4%、Argon（high）4%、Hydrogen 8%／9%／12%、Carbon（high）11%；正文寫的「Sonnet 5.5 43%」不在圖裡。
  - 圖 7、圖 8：「差評 X.PIN」的聽音辨識（英雄聯盟造型音效）與二階魔方截圖，屬單次展示。
  - 圖 10：作者的「Google AI Ultra 額度核算」圖卡（約 7 倍回報、雙機每天 $60～$70 約耗 10% 週額度）；圖 11：DeepMind 的 Genie 4 X 貼文截圖；**圖 12：App Store 土耳其區禮品卡的購買截圖（¥282）**；圖 13：第三方帳號的 X 貼文截圖，警告 Google 會連坐封號、波及 Gmail／雲端硬碟／GCP。
  - 圖 14：Project／Workspace／Sandbox 三層關係圖；圖 15：逐個讀取 vs 批量讀取示意；圖 16：Hydrogen 思考檔位示意；圖 17：Antigravity 桌面版擴充市集截圖；圖 18：「Orchestrator 動態雙模型接力」圖卡（**Carbon 規劃＋Hydrogen 執行**，Terminal-Bench 4.1 省 24% 額度、提速 19%）；圖 19：CLI `/effort` 檔位示意；圖 20：`AGY_CLI_HIDE_ACCOUNT_INFO=1`、`AGY_CLI_HIDE_LOGO=1` 前後對比；圖 21：內建瀏覽器／Swarm／Cloud Remote 三板斧；圖 22：Remote Control 手機畫面。
- **2026-11-21 重審更正**：
  - **跨區訂閱**：文章第一步是**建議**用 App Store 土耳其區禮品卡訂閱 Ultra（圖 12、約 ¥280／月），反對的只是「免費領一個月」這類薅羊毛；圖 13 的封號警告是文章轉貼的第三方說法。原稿只寫成「嚴禁跨區」，把文章的建議講反了。本 repo 不收錄跨區購買做法：這涉及帳號與付款條款，跟模型路由無關。
  - **Orchestrator 的 24%／19%**：出自 Antigravity 官方部落格（2026-11-12），量的是 **Carbon＋Hydrogen** 組合在 Terminal-Bench 4.1 的結果，官方沒有公開方法【官方自述】。2026-11-18 的 Neon 部落格說 Orchestrator 改為也能用 Neon 規劃，**沒有給 Neon 版的數字**。文章第 8 條把這組數字套到「Orchestrator (Neon)」，原稿又寫成「Carbon/Neon 規劃」，都不精確，已改正。
  - **GraphWalks「登頂」**：Neon 95.2% 是 Google 自己算的（評測方法 PDF 寫 GraphWalks 為自行計算），而且同家族的 Carbon 是 96.2%（見路由矩陣第 11.3 節），Neon 不是最高。
  - **SWE-sweep 39.0%**：是 Google 自行計算的「provider harness」成績，Neon 用的 Antigravity CLI 內建可把子代理分散到整個程式庫的工具，評測方法 PDF 自己說這特別適合找 bug 類任務；改用統一的 mini-SWE 框架時是 Neon 12.8%、Sol 11.6%、Opus 3.6%，差距小很多。原稿只寫 39.0%。
  - **官方另載**：Neon 在預設「高」思考層級下單任務成本比 Carbon 低 32%；「極高」層級 AA Index 61 分、總排名第 3，Artificial Analysis Coding Agent Index 58.6 與 AutomationBench 56.3% 第 1（Antigravity 部落格）【官方自述】。Hydrogen 的 AA Index 51、最高設定 54（同上，51 分是哪個思考層級沒寫）。
  - **未查證**：AA-Omniscience 幻覺率（本次沒有開 Artificial Analysis 網站核對）、Ultra 每週約 $600 Hydrogen／$200 Carbon 或 Neon 用量、CLI 上下文 256K 翻倍到 512K、Carbon 首字提速 1.5 倍，都只有文章或作者圖卡的說法。

---

## 2. 對現有系統的啟發與安全審查邊界

- **已在本機落地的條目**：第 1、2、5、6（前端規範與 `/browser`）、8、9 條均已由本機 `GEMINI.md` 全域協作規範與 `agent-assets` 覆蓋，無需重複照抄。（2026-11-21 重審沒有核對本機設定，此句未查證。）
- **明確風險提醒（不可直接執行文章提示詞）**：
  - 文章第 4 條要求 AI 直接「安裝 `oil-oil/agy-fast-io` 並設為讀取免審白名單」、第 11 條要求直接切到 Turbo 並接入 `codebase-memory-mcp`。依全域規範硬閘門：**外部第三方 Skill／插件與 MCP 必須先經過沙盒唯讀檢視與 `verify_agent_skill_pack_safety.py` 安檢，不可直接開免審白名單**。
- **實用新技巧與可評估項**：
  - `AGY_CLI_HIDE_ACCOUNT_INFO=1` 與 `AGY_CLI_HIDE_LOGO=1`（圖 20）為實用的終端機截圖防漏個人信箱環境變數。
  - `Gemini 4 Neon` 與 `GPT-6.2 Sol` 基準數據適合補入模型路由矩陣（2026-11-21 已補入 `docs/model-burn-rate-routing-matrix.md` 第 11.8～11.10 節）；`DeusData/codebase-memory-mcp`（AST+LSP 圖譜減少大專案檢索 token）與 `oil-oil/agy-fast-io` 適合建立沙盒唯讀審查任務。

---

## 3. 拆解出的待辦任務 (Action Items)

- [x] **`T-20261120-03`**｜**[優先級：低]** 將 `Gemini 4 Neon` / `Hydrogen` / `GPT-6.2 Sol` 基準與雙模型接力數據補入 `docs/model-burn-rate-routing-matrix.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\model-burn-rate-routing-matrix.md`（可與 `T-20261118-01`、`T-20261120-02` 合併更新 Google 生態章節）
  - **執行步驟**：
    1. 整理 `Gemini 4 Neon`（`$3/$15`、`GraphWalks 95.2%`、`CursorBench 4.1 65.4%` vs `Opus 5.5` / `GPT-6.2 Sol`）與 `Hydrogen`（`$1.5/$7.5`）的定位與價格。
    2. 納入 Orchestrator（規劃腦＋Hydrogen 執行手省 24%／提速 19%）與「前端高飽和色塊／不主動測驗證」的規則約束提醒。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 收錄上述基準與定價對比（標明資料出處分級），且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-21
  - **實作紀錄 / 證據**：docs/model-burn-rate-routing-matrix.md 第 11.8、11.10 節收錄 Neon／Hydrogen 價格與基準（模型卡、價格頁，標明各項由誰計算）；24%／19% 改正為官方 Carbon＋Hydrogen 版【官方自述】；筆記重審 full（22 圖）

- [x] **`T-20261120-04`**｜**[優先級：低]** 沙盒唯讀安檢並評估 `DeusData/codebase-memory-mcp` 與 `oil-oil/agy-fast-io`
  - **目標範圍**：`C:\GitHub\_sandbox\agy-plugins-audit` 與 `C:\GitHub\ai-inbox\docs\agy-fast-io-and-codebase-memory-audit.md`
  - **執行步驟**：
    1. 僅唯讀 clone `DeusData/codebase-memory-mcp` 與 `oil-oil/agy-fast-io` 至沙盒目錄（嚴禁直接啟用免審白名單或執行安裝腳本）。
    2. 對 `oil-oil/agy-fast-io` 執行 `python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack <目錄>` 與人工規則審閱，檢視是否存在繞過沙盒或風險指令。
    3. 評估 `codebase-memory-mcp` 在 Windows 11 原生環境下的支援度與索引開銷，將審查與採納建議寫入 `docs/agy-fast-io-and-codebase-memory-audit.md`。
  - **驗收標準（DoD）**：產出 `docs/agy-fast-io-and-codebase-memory-audit.md`，明確記錄安全掃描結束碼、人工審閱結論與採納／拒絕決策，且 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：2026-11-21
  - **實作紀錄 / 證據**：docs/agy-fast-io-and-codebase-memory-audit.md：唯讀淺層 clone agy-fast-io c9231ac5／codebase-memory-mcp 1111d9a9（2026-11-21），skill-pack 掃描結束碼 2／1 逐項人工判讀；agy-fast-io 不安裝只借鏡兩段寫法，codebase-memory-mcp 不跑安裝程式、可限縮試用；本機未安裝或註冊；未用 Antigravity 訂閱額度

## 4. 查證註記（2026-11-21，T-20261120-04 唯讀審查）

審查 commit：`oil-oil/agy-fast-io` `c9231ac5`、`DeusData/codebase-memory-mcp` `1111d9a9`。全文見 [`docs/agy-fast-io-and-codebase-memory-audit.md`](../docs/agy-fast-io-and-codebase-memory-audit.md)。

- **「安裝 agy-fast-io 並設為讀取免審白名單」**：repo 沒有任何設定白名單的機制，只有一份規則檔，教 agent 改用 Antigravity 內建白名單裡的命令；作者也說找不到關閉雲端審查的設定（該 repo `README.md:32`、`plugin/rules/AGENTS.md:20-30`）。決策：不安裝，借鏡搜尋閱讀與回答精簡兩段。
- **codebase-memory-mcp「Tree-sitter AST + LSP」**：tree-sitter 屬實；「LSP」是作者自寫的 C 型別解析，不啟動語言伺服器（該 repo `README.md:1108`）。「減少檢索 token」是作者自報數字（`README.md:477`），未獨立重現。決策：不跑上游安裝程式（它會一次改寫所有偵測到的 agent 設定並預設裝 hook），限縮條件下可試用。
- **第 11 條的 Cloud Remote、Turbo**：repo 內沒有相關內容，屬 Antigravity 本身設定，未查證。
- 兩者都沒有走 API／OAuth 使用 Antigravity 訂閱額度。
