---
id: "2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog"
title: "社群原創盤點：Jev by TypeSafe AI 上線六天 1,528 專案生態——Agent 守門員、模型路由、瀏覽器自動化與分類判斷全景分析"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "使用者直接提供全文（疑似 Threads / Facebook 原創貼文）"
author: "楊三賢 (SanHsien)"
analyzed_at: "2026-11-22"
analyzed_by: "antigravity"
written_by: "antigravity/claude-opus-4.6@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; antigravity/gemini-4-argon@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; antigravity/gemini@88a0bc60-2711-4499-b5fd-829fab9292d8; codex/gpt-6.1-sol@01a20b8d-8bc2-7191-a7cc-7a104940ed47"
revised_at: "2026-11-26"
source_review: unavailable
source_reviewed_at: "2026-11-22"
source_review_note: "使用者於對話直接提供完整正文與留言區專案分類清單全文（無原始貼文 URL，無法於網頁重開原貼文核對圖片與留言計數）"
status: pending
cluster: 3
cluster_role: "Jev六天開源生態"
short_title: "Jev六天開源生態盤點"
tags:
  - jev
  - typesafe-ai
  - agent-guardrails
  - model-routing
  - browser-automation
  - classification
  - mcp
  - open-source
---

# 社群原創盤點：Jev by TypeSafe AI 上線六天 1,528 專案生態——Agent 守門員、模型路由、瀏覽器自動化與分類判斷全景分析

- **來源**：使用者（楊三賢）直接提供全文（無 URL），內容為原創社群貼文（統計截止日為 `2026-09-21` 快照）
- **官方參考源**：[TypeSafe AI 官方更新紀錄 (`Changelog`)](https://docs.typesafe.ai/changelog)、[Choice 原語文件](https://docs.typesafe.ai/primitives/choice)、[圖片輸入文件 (`Images`)](https://docs.typesafe.ai/images)（2026-11-22 查核）
- **分析日期**：`2026-11-22`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-17-github-open-source-ai-toolkit-matrix.md`](./2026-10-17-github-open-source-ai-toolkit-matrix.md)（GitHub 開源 AI 工具矩陣：Jev 亞秒路由）
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（Claude Code 四級模型分工：Jev 快速決策角色）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（Jev 作為「是/否、選哪個」決策 API 的執行期觸發機制）
  - [`notes/2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md`](./2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md)（Jev API 相容的零生成 System One 端點）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](./2026-11-20-gemini-decision-1-decisions-api-eval.md)（Google Decisions API 與 JevBench 基準）

---

## 1. Jev 模型定位摘要（區分 2026-09 貼文快照與 2026-10+ 現行官方規格）

TypeSafe AI 於 `2026-09-15` 發布 Jev。以下將貼文所描述的 **2026-09 初版快照**與 **2026-11-22 查核之官方現行規格**明確分列：

- **非生成式判斷定位**：不生成自由文字，接收狀態與有界選項集，回傳選擇結果與校準後的信心機率。
- **判斷原語與輸入模態演進（歷史快照 vs. 現行規格）**：
  - **2026-09-21 貼文快照**：當時僅支援**純文字 / JSON 輸入**，並提供三種原語——[`Choice`](https://docs.typesafe.ai/primitives/choice)（多選分類，**每一道 `Choice` 題目最多 255 個選項**，同一請求可包含多道題目）、`Noul`（布林機率）、`Score`（量尺評分）。
  - **2026-10-14 官方更新後現行規格**：依 [官方更新紀錄 (`Changelog`)](https://docs.typesafe.ai/changelog) 與 [圖片文件](https://docs.typesafe.ai/images)，Jev 自 `2026-10-14` 起**已新增圖片輸入支援（目前仍標為實驗性 Experimental）以及第四種原語 `Box`（邊界框定位）**。因此「Jev 無法讀圖、只能純文字輸入」僅適用於 2026-09 貼文快照，不代表現行 Jev 規格。
- **延遲與計費**：原筆記所載延遲 70～500 ms 改列**來源未查證**，不視為已確認的官方宣稱；2026-11-24 核對[官方使用案例](https://docs.typesafe.ai/concepts/use-case-map)與[模型文件](https://docs.typesafe.ai/models)未找到此區間，使用案例頁目前描述約 150 ms（官方概述，未附此處量測條件、未獨立重測），兩者均不能當作端到端操作延遲。不逐字生成自由文字，計費上僅對 Input Token 收費、**Output Token 免費**（見[官方模型文件](https://docs.typesafe.ai/models)；OpenRouter 報價於 `@3three_AI` 長文引述 Jev 1.13 為輸入 `\$0.042 / 1M tokens`、輸出 `\$0`，未獨立重測；API 回應的 `usage.output_tokens` 欄位仍會回傳非零數值，如 [Choice 官方範例](https://docs.typesafe.ai/primitives/choice)為 `34`，不可宣稱回應用量欄位必為零）。
- **多語言與繁體中文能力狀態（歷史轉述 vs. 現行待測）**：
  - 貼文轉述 2026-09 初版說明稱「英文最準；中文、日文、韓文可用但精準度較低」（本次查核未在現行官方文件找到中、日、韓精準度排序頁）。
  - 依 [官方更新紀錄](https://docs.typesafe.ai/changelog)，官方僅確認 **`Jev 1.14` 改善了多語言支援（Improved multilingual support）**。這既不能證明中文限制已完全消失，也不足以將 9 月舊說法直接當作已確認的現行官方規格；**現行版本在繁體中文環境的實際準確率應列為【待實測】**。

---

## 2. 六日生態概觀：1,528 專案的結構化拆解（補齊 GitHub `owner/repo` 查核出處）

依貼文統計（截至 `2026-09-21` 快照，生態總數 1,528、清單收錄約 260、附數字約 40 屬貼文統計數字，未獨立重算），以下按貼文分類整理，並於 2026-11-22 透過 GitHub API 補齊可追溯之 `owner/repo` 網址與一手 README 方法核對（未在 GitHub 唯一確認對應 repo 者標為「貼文僅列名稱，未查證具體 repo」）：

### 2.1 內容過濾與雜訊清除

| 專案名稱與可追溯出處（2026-11-22 GitHub 查核） | 功能描述 | 實測數據與來源限制 |
| :--- | :--- | :--- |
| **[`valentynkit/jev-skip`](https://github.com/valentynkit/jev-skip)** | 讀 YouTube 字幕判斷業配並自動跳過 | 專案自述（23 支影片）：抓出 SponsorBlock 標註秒數之 77%，每支成本 ~\$0.0008，每小時誤跳 ~34 秒；作者註明為透過轉接服務測試，未以官方介面重測 |
| **[`kitze/unclutter`](https://github.com/kitze/unclutter)** | 判斷網頁區塊為雜訊並移除 | 無量化數據（專案 README 展示功能） |
| **Marcel Pociot X 資訊流過濾外掛**（2026-11-25 補充；[`marcelpociot/2100520134481735729`](https://x.com/marcelpociot/status/2100520134481735729)） | 接入 Jev 以自然語言規則過濾 X 平台不想看的貼文 | 開發者公開展示自述每則貼文平均判斷耗時約 **380 ms**（未唯一確認公開 GitHub 倉庫，未獨立重測） |
| **內容評分／AI 味檢測／few-shot 篩選**（2026-11-26 自 [`@3three_AI`](https://x.com/3three_AI/status/2102234751591653484) 併入） | Rob Hallam 貼文診斷（[`2100722975645598191`](https://x.com/robj3d3/status/2100722975645598191)）、Dan Willoughby「Sniff Test」AI 味 10 題逐段檢查（[`2100990605308441076`](https://x.com/DanRWilloughby/status/2100990605308441076)）、Paolo Rosson 16 則收藏 few-shot 分 `HIDE/SKIM/SAVE`（[`2100915304062710263`](https://x.com/redp314/status/2100915304062710263)） | 作者自述 Rob Hallam 1 秒可跑 61 題判斷、成本約 `\$0.0004`（基於 207 創作者 9,481 篇貼文，約 2/3 機率挑出較佳貼文；屬二手轉述，未獨立重測） |
| `sift`、`typesafe-adblock`、`jev_antispam_bot`、`youtube-sponsor-detection` | X 貼文六分類隱藏、網頁廣告判斷（作者自述好玩專案）、Telegram 防灌水、YouTube 業配偵測 | 貼文僅列名稱與用途描述，未附量化數據（同名通用詞或未唯一確認 repo，列為貼文二手轉述，【待實測】） |

### 2.2 信箱與文件分類

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與架構細節核實 |
| :--- | :--- | :--- |
| **[`fazlerocks/jevmail`](https://github.com/fazlerocks/jevmail)** | Gmail 五分類（需回覆/通知/促銷/推銷/垃圾），只讀不刪、本機執行 | 無量化準確率數據 |
| **[`kyotofin/tax-doc-classifier`](https://github.com/kyotofin/tax-doc-classifier)** | 美國報稅文件逐頁辨識 261 種表單 | 專案自述：753 頁空白官方表單測試零分錯（~5% 把握偏低）；每頁 ~\$0.001（未獨立重測）。**架構核實（[`#how-it-works`](https://github.com/kyotofin/tax-doc-classifier#how-it-works)）**：採兩階段分層請求——第一層先區分 7 種頁面類型與 230 個表單選項加 `not_in_this_list`，僅在命中 5 組企業／外國母表（`5471`、`8865`、`8933`、`1118`、`5713`）時才觸發第二次請求細分其 35 張附表；作者說明採用分層是因為這些頁面上母表名稱比附表本身更明確（非因每道 `Choice` 題目 255 個選項上限所致） |
| `jev-mail-classifier` | 信件分類並自動貼標籤、搬資料夾（近親專案如 [`ilyamk/jev-gmail-ai-spam-filter-and-labeling`](https://github.com/ilyamk/jev-gmail-ai-spam-filter-and-labeling)） | 無量化數據（貼文二手轉述，【待實測】） |

### 2.3 語音/電腦/家電操作

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與來源限制 |
| :--- | :--- | :--- |
| **[`moritzkremb/jev-voice-browser`](https://github.com/moritzkremb/jev-voice-browser)** | 語音操作瀏覽器 | 作者自述每次 Jev 判斷請求約 **250～350 ms**；部分逐字稿更新觸發請求，另有 200 ms 防抖、並行請求與完整指令判斷，**不是逐字延遲或語音操作端到端延遲**（[README](https://github.com/moritzkremb/jev-voice-browser#readme)，2026-11-24 核對；未獨立重測） |
| **[`AboveColin/HA-Jev`](https://github.com/AboveColin/HA-Jev)** | Home Assistant 居家自動化問答與觸發 | 無量化基準數據 |
| `jev-use`、`mobile-jev` | 一句話操作 Mac（讀系統輔助功能資訊，2026-09 快照時點）、手機畫面操作（相關清單見 [`walidboulanouar/awesome-jev-use-cases`](https://github.com/walidboulanouar/awesome-jev-use-cases)） | 無量化數據（貼文二手轉述，【待實測】） |

### 2.4 AI Agent 守門員（核心類別）

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與來源限制 |
| :--- | :--- | :--- |
| **[`anpicasso/hermes-jev-approvals`](https://github.com/anpicasso/hermes-jev-approvals)** | Hermes Agent 指令語意審核：安全直接放行、可疑才跳出問人 | 依[專案 Metrics](https://github.com/anpicasso/hermes-jev-approvals/blob/main/docs/METRICS.md) 修正數據（**156 個跨三個設定檔分層抽樣真實指令**）：審核速度**快 9.8×**（405 ms vs. 3,968 ms）、需人工中斷次數**少 4.2×**（10 次 vs. 42 次）。原版 153 筆／8.7×／4.4× 實僅含單一設定檔，作者已承認誤報並撤回；該基準仍受限於單機（Linux 2 vCPU、7 GB）、對比單一預設輔助聊天模型，且為未在真實線上會話運行的專案自述（未獨立重測） |
| **[`valentynkit/jev-belay`](https://github.com/valentynkit/jev-belay)** | Claude Code 說「做完了」時先查對話紀錄找證據 | 專案自述（100 筆單一作者真實會話之模型代理標註停止案例，含 12 筆假完成正例；小樣本且未獨立重測）：區分假完成與誠實停止之 **AUROC 0.976**（對照僅看結案文字 0.777），中位延遲 **346 ms** |
| **[`noplan-inc/limpet`](https://github.com/noplan-inc/limpet)** | 不讓 AI 寫程式助理提早收工 | 專案 README 自述（[`#readme`](https://github.com/noplan-inc/limpet#readme)）：每次停止檢查延遲約 **0.7 秒**、成本約 **US\$0.0001**（未確認標準化準確率基準，未獨立重測） |
| **[`y0usaf/pi-jev`](https://github.com/y0usaf/pi-jev)** | Pi 工具風險閘 | 無量化數據 |
| **[`leepokai/jev-guard`](https://github.com/leepokai/jev-guard)** | 提示注入與危險動作守門 | 專案 README 自述（[`#why-jev-price-and-speed-with-sources`](https://github.com/leepokai/jev-guard#why-jev-price-and-speed-with-sources)，2026-09 測試）：台灣直連延遲約 **0.75 秒**，經 Gateway 21 次校準呼叫之 p50 約 **580 ms**（作者自測小樣本，未獨立重現） |
| **`jev-harness`（同名多專案）** | 判斷閘與影子模式；GitHub 上至少存在 [`nickylin/jev-harness`](https://github.com/nickylin/jev-harness)、[`AntonioCoppe/jev-harness`](https://github.com/AntonioCoppe/jev-harness) 與 [`TianyuCodings/JevHarness`](https://github.com/TianyuCodings/JevHarness) | 貼文未指定單一 owner，各倉庫皆無標準化第三方基準數據 |
| **[`lgy1027/jevshield`](https://github.com/lgy1027/jevshield)** | LangChain 安全閘（另有同名 [`rajatrao/jevshield`](https://github.com/rajatrao/jevshield)） | 無量化數據 |
| **[`AshutoshVJTI/progressgate`](https://github.com/AshutoshVJTI/progressgate)** | 偵測 AI 是否原地打轉 | 無量化數據 |
| **[`Sraavan/tripwire`](https://github.com/Sraavan/tripwire)** | Claude Code 工具執行前（`PreToolUse`）風險審核安全閘，以 7 個是非題評估風險並回傳**允許（allow）、詢問（ask）或拒絕（deny）**三種決策 | 專案自述實驗評測（66 情境×5 次重複，限 macOS、案例與標籤由 Claude Code 產生未經人工覆核、實際僅跑過 shadow mode，未獨立重測）：危險呼叫 0/140 放行、安全呼叫誤擋 8.9%、p50 延遲 215 ms |
| `jev-git`、`jev-secret-detection` | commit 前擋密鑰與危險指令、程式變更是否洩密 | 貼文僅列名稱，未附量化數據（未查證具體單一 repo，列為貼文二手轉述，【待實測】） |
| **[`thruwire/foreman`](https://github.com/thruwire/foreman)**、[`devagrawal09/jev-review`](https://github.com/devagrawal09/jev-review)、[`blakestone-x/jev-mcp`](https://github.com/blakestone-x/jev-mcp)、[`awlevin/typesafe-computer-use`](https://github.com/awlevin/typesafe-computer-use)（2026-11-26 自 `@3three_AI` 併入） | Agent 監工（判斷完成／測試足夠／死迴圈）、Git diff 風險排序、Jev MCP 判斷工具、桌面動作決策；另 Vercel `fx`（[`rauchg/2100307962262872105`](https://x.com/rauchg/status/2100307962262872105)）接 Jev 作指令安全閘門 | `jev-mcp` 實戰指出**須明文指示主 Agent 何時委派給 Jev，否則大模型容易忽略該工具**；Vercel `fx` 自述測試條件下 p95 延遲最高約 18× 提升（二手轉述，未獨立重測） |
| **[`qkal/Canny`](https://github.com/qkal/Canny)**（2026-11-26 補充，136 stars） | 比對工具輸出、Diff 與測試結果防止 Coding Agent 假完工 | **確定性為主、Jev 為輔**：`Deterministic hooks decide, TypeSafe's Jev advises`，採 append-only ledger、零執行期依賴（未獨立重測） |
| **[`itsmostafa/typesafe-mcp`](https://github.com/itsmostafa/typesafe-mcp)**（366 stars）、[`jkudish/jev-mcp`](https://github.com/jkudish/jev-mcp)（593 stars）、[`sharziki/semdecide`](https://github.com/sharziki/semdecide)（87 stars） | 通用 System One MCP（支援 Jev / D1 / CLM / Laya）、型別化 Jev MCP 工具箱、Unix/CI 管線語意 CLI | 2026-11-26 GitHub API 核實存在與星數；無第三方統一基準（未獨立重測） |

### 2.5 模型路由與 Token 節省

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與重要模擬限制（一手 README 核對） |
| :--- | :--- | :--- |
| **[`0xNatoshi/jev-codex-router`](https://github.com/0xNatoshi/jev-codex-router#jev-codex-router)** | Codex 每輪用 Jev 決定模型與思考深度 | 專案自述：237 個歷史回合回測較全用最貴模型少 ~60%。**重要限制**：作者於 README 明示此數字為**舊版路由政策（Legacy Policy）的歷史模擬回測，並非實際量測的 Codex 配額或帳單節省，也不證明現行版本政策的實際成效** |
| **`jev-router`（同名多專案）** | Claude Code 模型路由，對應 [`gargpratyush/jev-router`](https://github.com/gargpratyush/jev-router) 與 [`BillionsBobby/JevRouter`](https://github.com/BillionsBobby/JevRouter) | 無統一第三方實測數據 |
| **[`tamaratran/jev-pruner`](https://github.com/tamaratran/jev-pruner)** | 修剪過長 Bash 輸出 | 無量化數據 |
| **[`tamaratran/fast-jev-compaction`](https://github.com/tamaratran/fast-jev-compaction)**（2026-11-25 補充，8,023 stars） | Claude Code 外掛＋npm 套件：以 Jev `noul` 剪枝取代有損 LLM 摘要壓縮 | **無失真剪枝機制（README 一手核實）**：保留首則與最近 `preserveRecentMessages`（預設 6）則訊息；其餘每個 `tool_use`/`tool_result` 配對問兩題 `noul`（`keepCall` 與 `keepResult`），對照 `keepThreshold=0.5`：`keepResult≥0.5` 原文保留、`keepCall≥0.5` 僅留前 `300` 字元＋註記、否則整對移除；使用者／助手文字完全不改寫。分階段將狀態壓入 `maxStateTokens=25k`、批次 `maxRequestTokens=30k` 並行送出（Jev 失敗即 throw 由 hook 決定回退） |
| **[`GhalebDweikat/winnow`](https://github.com/GhalebDweikat/winnow)**（2026-11-26 補充，115 stars） | Claude Code 上下文入口過濾（Context Sieve）：`Read`/`Bash`/`Grep` 結果進入上下文前先由 System One 篩選 | 與 `fast-jev-compaction`（事後剪枝）互補之**事前入口過濾（pre-entry sieve）**（未獨立重測） |
| **[`ellipsis-dev/blink`](https://github.com/ellipsis-dev/blink)**（106 stars）、[`jexp/neo4jev`](https://github.com/jexp/neo4jev)（190 stars） | 逐層資料夾相關性導航 Codebase、Neo4j 知識圖譜鄰邊分類探勘 | 2026-11-26 GitHub API 核實存在；無標準化基準數據（未獨立重測） |
| **[`win4r/jev-skill-suggester`](https://github.com/win4r/jev-skill-suggester)** | 推薦該用哪個 skill（中英雙語） | 無量化數據 |
| **[`kunchenguid/compact-adviser`](https://github.com/kunchenguid/compact-adviser)** | 判斷何時適合壓縮對話 | 無量化數據 |
| **[`EliaAlberti/jev-rules`](https://github.com/EliaAlberti/jev-rules)** | 挑出適用規則減少 Claude 讀取量 | 無量化數據 |
| **[`Dicklesworthstone/skillranker`](https://github.com/Dicklesworthstone/skillranker)** | 依當下狀況排序 skill | 無量化數據 |

### 2.6 瀏覽器自動化

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與快照差異 |
| :--- | :--- | :--- |
| **[`browser-use/jev-ultrafast`](https://github.com/browser-use/jev-ultrafast)** | AI 瀏覽器自動操作：每步點哪裡交 Jev 決定、需要打字才請小模型 | 貼文 2026-09-21 快照記錄為 **13,061 顆星**（2026-11-22 查 GitHub API 已增長至 24,708 顆星）；README 示範 Google 航班搜尋蘇黎世→倫敦 7.1 秒（專案自述示範） |

### 2.7 程式開發工具、遊戲與交易（貼文概覽）

- **程式開發與 UI / 資料流**（2026-11-26 GitHub API 核實補充）：[`vercel-labs/json-render`](https://github.com/vercel-labs/json-render)（`19,851` stars，生成式 UI 實驗以 Jev 挑選元件屬性）、[`lahfir/agent-desktop`](https://github.com/lahfir/agent-desktop)（`26,798` stars，無障礙樹桌面操作 CLI）、[`AkashPriyadarshii/jev-curate`](https://github.com/AkashPriyadarshii/jev-curate)（`116` stars，Rust 串流 Parquet/JSONL 訓練資料過濾，自述 24.0 rows/sec）、[`monteduro/killmyidea`](https://github.com/monteduro/killmyidea)（`280` stars，點子 `KILL/FIX/SHIP` 評分）；另有貼文僅列名稱之 `jev-semgrep`、`jev-shell-history`、`jevcache`（【待測】）。
- **遊戲展示**：[`fhshaik/typesafe-mario`](https://github.com/fhshaik/typesafe-mario)、[`RomanSlack/jev-drone`](https://github.com/RomanSlack/jev-drone)、[`emrickgarrett/OneVOneJev`](https://github.com/emrickgarrett/OneVOneJev)（44 stars，Three.js 1v1 FPS）、寶可夢、俄羅斯方塊、五子棋、星海爭霸、文明帝國二代等。皆將遊戲／模擬器 RAM 狀態轉結構化文字餵入以展示反應速度，文明帝國作者明載未驗證能完整贏一場（【待測】）。
- **交易（高風險，僅供知悉）**：[`jarrodwatts/jev-trader`](https://github.com/jarrodwatts/jev-trader)（`3,156` stars，Monad 測試網每區塊造市決策，轉述模型延遲 ~81 ms）、[`irfndi/prism-liquidity-agent`](https://github.com/irfndi/prism-liquidity-agent)（`136` stars，Meteora DLMM 流動性訊號代理，不直接下單而輸出風控狀態訊號給策略執行）與 `QuantDinger`（未獨立重測，【待測】）。

### 2.8 兩項評測基準專案之一手方法與結果核實（重要校準）

貼文簡述了兩項「測出不理想」的案例，經查核兩專案之 GitHub 原始 README，必須補齊其真實樣本組成、實驗配置與裁判偏差：

| 評測專案與一手出處 | 貼文簡述 | 原始 README 一手核實結果（關鍵細節與修正） |
| :--- | :--- | :--- |
| **[`anisselbd/jev-phishing-bench`](https://github.com/anisselbd/jev-phishing-bench)** | 2,000 封釣魚郵件：Jev 準確率 62.6%，Claude Haiku 4.5 為 81.3% | 1. **樣本組成**：2,000 封測試集實為 **1,000 封釣魚郵件 + 1,000 封正常郵件**（非全為釣魚信）。<br>2. **版本與訓練配置差異（[`#controls-added-after-review-17-september-2026`](https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026)）**：`62.6%`（對照 Haiku 4.5 的 `81.3%`）僅限於 **Jev 1.13 直接單次判斷（Direct Classification）**；而 `95.0%` 並非只靠拆題即可直接得出，而是將 **5 項 Jev 訊號先在 A 組（1,000 封）選取門檻並訓練邏輯迴歸（Logistic Regression），再於 B 組保留集（1,000 封）評估**後的成績（AUROC 0.982）。B 組對照中，Jev 單一最佳訊號（`sig_free_hosting >= 0.70`）僅達 `89.4%`，低於非 AI 確定性正則規則的 `91.8%`（McNemar p = 0.0032），且 Jev 5 訊號迴歸（`95.0%`）與 Haiku 4.5 同一 5 訊號迴歸（`93.2%`、AUROC 0.991）統計無顯著差異（p = 0.063）。 |
| **[`zhuyansen/jev-search-rerank-eval`](https://github.com/zhuyansen/jev-search-rerank-eval)** | 164 中英文查詢、9,831 組人工評分：Jev 單獨排序不如一般語意搜尋，合併使用最佳 | 1. **非人工評分（模型標註與裁判偏差）**：依 [`#method`](https://github.com/zhuyansen/jev-search-rerank-eval#method)，**9,831 組相關性標註主要由 Jev 與 Claude Haiku 產生，少量分歧裁決亦由 Claude 執行**，並非人工標註資料集，存在循環評分偏差。<br>2. **統計顯著性與範圍（[`#results`](https://github.com/zhuyansen/jev-search-rerank-eval#results)）**：在合併標籤下，Jev 重排序相對 `bge-m3` 的差值為正但**信賴區間跨零（未證明顯著優於 `bge-m3`）**；**排除 Jev 自身參與裁判的標籤後，Jev 單獨排序才顯著較差**。將兩者融合（Hybrid）取得最佳表現的結論，亦**僅限於該資料集與比較系統配置**。 |

---

## 3. 原文附帶的四項注意事項與時效校準

1. **大多數專案沒有附數字**：貼文指出約 260 個收錄專案中僅約 40 個附測試數據，其餘僅一句話描述。
2. **星星多不等於效果好**：收藏數反映關注度而非品質；多數專案為上線一週內建立，未經長期驗證。
3. **非文字處理能力的時效校準**：貼文於 2026-09 提醒「Jev 只讀文字，看畫面專案皆先轉文字」；惟官方已於 **2026-10-14 新增實驗性圖片輸入與 `Box` 原語**（[官方圖片文件](https://docs.typesafe.ai/images)），閱讀時須區分 9 月快照專案與現行 API 規格。
4. **中文能力的時效校準**：貼文引述 9 月初版「英文最準、中/日/韓精準度較低」；官方於 **`Jev 1.14` 更新紀錄已標示改善多語言支援**（未公布中英分項數據），故現行繁中精準度應視為**【待實測】**。

---

## 4. 對既有專案與架構之結構性啟發

### 4.1 Jev 生態與 Gemini Decisions API / Colibri 的戰略對位

```text
[決策模型光譜：System One 分類判斷]
  ├── TypeSafe Jev（先行者，2026-09-15；2026-10-14 新增實驗性圖片與 Box 原語）
  │     ├── 優勢：生態先發、When2Call (82.0%) 與 7 項基準總成本 ($0.68) 領先
  │     └── 邊界：直接單次判斷複雜釣魚信較弱 (Jev 1.13 為 62.6%；五項訊號經 A 組訓練邏輯迴歸於 B 組保留集達 95.0%，單一最佳訊號 89.4% 低於正則規則 91.8%)；繁中表現待實測
  │
  ├── Google Decisions API / Decision 1（後發者，2026-11-11）
  │     ├── Google 官方自述 JevBench 92.2%、Top-1 ECE 0.0250、原生多模態輸入
  │     └── 邊界：When2Call (79.9%) 與 7 項基準總成本 ($0.88) 略遜於 Jev 1.14
  │
  └── 本機替代方案
        └── JustVugg/colibri（三層式 MoE、本地零 API 成本之 Jev 相容 /v1/systemone 端點）
```

### 4.2 與本專案的直接交集與證據邊界

1. **Agent 守門員模式**：[`anpicasso/hermes-jev-approvals`](https://github.com/anpicasso/hermes-jev-approvals)（修正後 156 筆跨三個設定檔分層樣本自述快 9.8×、人工中斷少 4.2×；受限單機與單一輔助比較模型）、[`valentynkit/jev-belay`](https://github.com/valentynkit/jev-belay)（100 筆作者會話模型代理標註停止案例自述 AUROC 0.976、中位延遲 346 ms）與 [`noplan-inc/limpet`](https://github.com/noplan-inc/limpet)（防提早收工）提供了以 `Noul` 二元判斷輔助執行期把關的架構參考，[`Sraavan/tripwire`](https://github.com/Sraavan/tripwire) 則示範工具執行前（`PreToolUse`）風險審核（允許／詢問／拒絕），可與本專案確定性檢查腳本互補（以上專案量化數據皆未獨立重測）。
2. **模型路由模擬與實測的區分**：[`0xNatoshi/jev-codex-router`](https://github.com/0xNatoshi/jev-codex-router#jev-codex-router) 的 237 回合省 ~60% **僅為舊版路由政策的歷史模擬回測，非實測 Codex 配額節省，亦不證明現行政策成效**；在與本專案 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 對照時，僅能視為路由模擬概念，不能當作已驗證的實際帳單節省證據。
3. **訊號拆解、下游訓練與繁中防禦部署建議**：從 [`anisselbd/jev-phishing-bench`](https://github.com/anisselbd/jev-phishing-bench)（Jev 1.13 直接判斷 62.6%；單一最佳訊號 89.4% 低於確定性正則規則 91.8%；5 項訊號經 A 組訓練邏輯迴歸後於 B 組保留集才達 95.0%）可知，使用 System One 模型處理安全判斷時，**不僅應將複雜問題拆解為結構化子訊號，還須視任務搭配下游統計訓練或確定性規則組合**；且在 `Jev 1.14` 繁體中文表現完成本地實測前，本機防禦上建議優先搭配確定性規則與置信度門檻（此為本專案部署建議，非官方硬性限制規格）。
4. **無失真上下文剪枝與入口過濾（2026-11-25/26 補充）**：[`tamaratran/fast-jev-compaction`](https://github.com/tamaratran/fast-jev-compaction)（事後無損剪枝）與 [`GhalebDweikat/winnow`](https://github.com/GhalebDweikat/winnow)（`Read`/`Bash`/`Grep` 事前入口過濾）構成雙層防膨脹機制——保留重要 `tool_result` 全文、攔截無關雜訊，可與本庫 `idleCompaction` 及 `cc-session-reader` 策略對照評估。
5. **MCP 委派防忽略規則與「確定性裁決＋Jev 建議」原則（2026-11-26 補充）**：[`blakestone-x/jev-mcp`](https://github.com/blakestone-x/jev-mcp) 與 [`itsmostafa/typesafe-mcp`](https://github.com/itsmostafa/typesafe-mcp) / [`jkudish/jev-mcp`](https://github.com/jkudish/jev-mcp) 顯示僅掛載 MCP 易被主模型忽略，須明文強制委派規則；同時 [`qkal/Canny`](https://github.com/qkal/Canny) 示範了更安全的邊界：**「確定性 Hook 裁決、Jev 僅作顧問建議（Deterministic hooks decide, Jev advises）」**，與本庫不放任機率模型單獨放行高風險閘門的紀律一致。

---

## 5. 行動清單（Action Items）

- [ ] **`T-20261122-05`**｜**[優先級：中]** 將 Jev by TypeSafe AI 生態中與 Agent 安全閘門（`anpicasso/hermes-jev-approvals`、`valentynkit/jev-belay`、`noplan-inc/limpet`、`AshutoshVJTI/progressgate`、`Sraavan/tripwire`）與模型路由（`0xNatoshi/jev-codex-router`、`gargpratyush/jev-router`）相關的專案架構與數據限制，對照 Google Decisions API / Colibri 整理至 `docs/system-one-decision-model-landscape.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\system-one-decision-model-landscape.md`（收錄於集群 3）
  - **執行步驟**：
    1. 彙整 Jev 生態代表性專案（附確切 `owner/repo` 網址與 2026-09-21 快照日期），區分 2026-09 純文字快照與 2026-10-14 新增實驗性圖片／`Box` 原語之現行規格，釐清僅對 Input Token 收費／Output Token 免費（且回應 `usage.output_tokens` 非零），並註明每道 `Choice` 題目最多 255 個選項（同一請求可含多道題目）與 `kyotofin/tax-doc-classifier` 兩階段分層請求（第一層 230 類加 `not_in_this_list`，5 組母表因頁面母表名稱較明確而觸發第二層拆分 35 附表）架構。
    2. 完整記錄 `0xNatoshi/jev-codex-router`（舊政策歷史模擬、非實測配額節省、不代表現行成效）、`anisselbd/jev-phishing-bench`（1,000 釣魚 + 1,000 正常樣本；Jev 1.13 直接判斷 62.6%；5 項訊號經 A 組訓練邏輯迴歸於 B 組保留集達 95.0%、單一訊號 89.4%、確定性正則規則 91.8%）、`anpicasso/hermes-jev-approvals`（修正後 156 筆跨三設定檔 9.8× 速度／4.2× 較少人工中斷，註明舊 153 筆撤回與單機／單一輔助模型限制）、`valentynkit/jev-belay`（100 筆作者會話代理標註停止案例自測 AUROC 0.976、346 ms）與 `zhuyansen/jev-search-rerank-eval`（9,831 組為 Jev/Haiku 模型標註與 Claude 裁決、合併標籤下相對 `bge-m3` 信賴區間跨零、排除 Jev 裁判後顯著較差）之一手方法與限制。
    3. 標明 `Jev 1.14` 已改善多語支援、現行繁中表現為【待實測】，並將本專案的防禦性部署建議（結構化訊號拆解＋下游訓練／確定性規則、置信度門檻）與已確認官方規格分開。
    4. 整合 Agent 守門員模式（指令審核、工具執行前 `PreToolUse` 風險閘 `Sraavan/tripwire`〔允許／詢問／拒絕〕、防提早收工、原地打轉偵測）的通用架構模板。
    5. 同步修正既有產出第 2 節的延遲比較與第 3.1 節「即時語音操控」：70～500 ms 保留為來源未查證，不作已確認官方數據；語音案例改為作者自述每次 Jev 請求 250～350 ms，註明非逐字或端到端延遲，附來源與核對日期，保留未獨立重測限制。
    6. （2026-11-25 增補）收錄 `tamaratran/fast-jev-compaction`（`8,023` stars）之無失真 `noul` 上下文剪枝架構（`keepCall` / `keepResult` 雙門檻＋`preserveRecentMessages` 錨定）與 Marcel Pociot X 資訊流過濾（自述平均 380 ms/則）案例。
    7. （2026-11-26 自 `@3three_AI` 增補）補齊 `thruwire/foreman`、`devagrawal09/jev-review`、`blakestone-x/jev-mcp`（「須明文要求委派給 Jev，否則主模型易忽略」之 MCP 整合原則）與 Dan Willoughby「Sniff Test」AI 味 10 題檢查參考。
    8. （2026-11-26 續補）納入 `qkal/Canny`（「確定性 Hook 裁決、Jev 僅作顧問建議」防假完工）、`GhalebDweikat/winnow`（事前入口過濾 vs `fast-jev-compaction` 事後剪枝）、`itsmostafa/typesafe-mcp`、`jkudish/jev-mcp`、`sharziki/semdecide`、`ellipsis-dev/blink` 與 `jexp/neo4jev` 圖譜導航模式。
  - **驗收標準（DoD）**：產出 `docs/system-one-decision-model-landscape.md`，含 Jev（區分 9 月快照與 10 月圖片/`Box` 更新、僅對輸入收費／輸出免費且區分 `usage.output_tokens` 非零欄位）/ Decision 1 / Colibri 三方對照表、各專案 `owner/repo` 出處與實驗限制（釣魚信 5 訊號經 A 組訓練邏輯迴歸於保留集達 95.0% 與正則 91.8% 對照、指令審核修正後 156 筆 9.8×/4.2×、`Tripwire` 為 `PreToolUse` 風險閘、`jev-belay` 100 筆自測 AUROC 0.976、搜尋排序模型標註偏差、路由舊政策模擬聲明），既有第 2 節與第 3.1 節亦須按上述延遲單位與證據分級修正、附來源與核對日期，且 `python tools/verify_inbox.py` 驗證通過。
