---
id: "2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog"
title: "社群原創盤點：Jev by TypeSafe AI 上線六天 1,528 專案生態——Agent 守門員、模型路由、瀏覽器自動化與分類判斷全景分析"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "使用者直接提供全文（疑似 Threads / Facebook 原創貼文）"
author: "楊三賢 (SanHsien)"
analyzed_at: "2026-11-22"
analyzed_by: "antigravity"
written_by: "antigravity/claude-opus-4.6@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; antigravity/gemini-4-argon@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
revised_at: "2026-11-22"
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
  - **2026-09-21 貼文快照**：當時僅支援**純文字 / JSON 輸入**，並提供三種原語——[`Choice`](https://docs.typesafe.ai/primitives/choice)（多選分類，單次請求上限 **255 類**）、`Noul`（布林機率）、`Score`（量尺評分）。
  - **2026-10-14 官方更新後現行規格**：依 [官方更新紀錄 (`Changelog`)](https://docs.typesafe.ai/changelog) 與 [圖片文件](https://docs.typesafe.ai/images)，Jev 自 `2026-10-14` 起**已新增圖片輸入支援（目前仍標為實驗性 Experimental）以及第四種原語 `Box`（邊界框定位）**。因此「Jev 無法讀圖、只能純文字輸入」僅適用於 2026-09 貼文快照，不代表現行 Jev 規格。
- **延遲與計費**：官方宣稱延遲 70～500 ms（未獨立重測）；輸出 Token 為零、僅計入 Input Token。
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
| `sift`、`typesafe-adblock`、`jev_antispam_bot`、`youtube-sponsor-detection` | X 貼文六分類隱藏、網頁廣告判斷（作者自述好玩專案）、Telegram 防灌水、YouTube 業配偵測 | 貼文僅列名稱與用途描述，未附量化數據（同名通用詞或未唯一確認 repo，列為貼文二手轉述） |

### 2.2 信箱與文件分類

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與架構細節核實 |
| :--- | :--- | :--- |
| **[`fazlerocks/jevmail`](https://github.com/fazlerocks/jevmail)** | Gmail 五分類（需回覆/通知/促銷/推銷/垃圾），只讀不刪、本機執行 | 無量化準確率數據 |
| **[`kyotofin/tax-doc-classifier`](https://github.com/kyotofin/tax-doc-classifier)** | 美國報稅文件逐頁辨識 261 種表單 | 專案自述：753 頁空白官方表單測試零分錯（~5% 把握偏低）；每頁 ~\$0.001。**架構核實（[`#how-it-works`](https://github.com/kyotofin/tax-doc-classifier#how-it-works)）**：因官方 `Choice` 單次上限為 255 類，該專案透過**分層請求（Hierarchical Requests）**涵蓋 261 種表單 |
| `jev-mail-classifier` | 信件分類並自動貼標籤、搬資料夾（近親專案如 [`ilyamk/jev-gmail-ai-spam-filter-and-labeling`](https://github.com/ilyamk/jev-gmail-ai-spam-filter-and-labeling)） | 無量化數據（貼文二手轉述） |

### 2.3 語音/電腦/家電操作

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與來源限制 |
| :--- | :--- | :--- |
| **[`moritzkremb/jev-voice-browser`](https://github.com/moritzkremb/jev-voice-browser)** | 語音操作瀏覽器 | 專案自述：每說一字約 ~0.3 秒判斷意圖與點擊目標（未獨立重測） |
| **[`AboveColin/HA-Jev`](https://github.com/AboveColin/HA-Jev)** | Home Assistant 居家自動化問答與觸發 | 無量化基準數據 |
| `jev-use`、`mobile-jev` | 一句話操作 Mac（讀系統輔助功能資訊，2026-09 快照時點）、手機畫面操作（相關清單見 [`walidboulanouar/awesome-jev-use-cases`](https://github.com/walidboulanouar/awesome-jev-use-cases)） | 無量化數據（貼文二手轉述） |

### 2.4 AI Agent 守門員（核心類別）

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與來源限制 |
| :--- | :--- | :--- |
| **[`anpicasso/hermes-jev-approvals`](https://github.com/anpicasso/hermes-jev-approvals)** | Hermes Agent 指令語意審核：安全直接放行、可疑才跳出問人 | 專案 README 自述（153 個真實指令測試）：審核速度**快 8.7×**、需人工回答次數**少 4.4×**（單一專案自述，未獨立重測） |
| **[`valentynkit/jev-belay`](https://github.com/valentynkit/jev-belay)** | Claude Code 說「做完了」時先查對話紀錄找證據 | 無量化數據（架構設計參考） |
| **[`noplan-inc/limpet`](https://github.com/noplan-inc/limpet)** | 不讓 AI 寫程式助理提早收工 | 無量化數據（架構設計參考） |
| **[`y0usaf/pi-jev`](https://github.com/y0usaf/pi-jev)** | Pi 工具風險閘 | 無量化數據 |
| **[`leepokai/jev-guard`](https://github.com/leepokai/jev-guard)** | 提示注入與危險動作守門 | 無量化數據 |
| **`jev-harness`（同名多專案）** | 判斷閘與影子模式；GitHub 上至少存在 [`nickylin/jev-harness`](https://github.com/nickylin/jev-harness)、[`AntonioCoppe/jev-harness`](https://github.com/AntonioCoppe/jev-harness) 與 [`TianyuCodings/JevHarness`](https://github.com/TianyuCodings/JevHarness) | 貼文未指定單一 owner，各倉庫皆無標準化第三方基準數據 |
| **[`lgy1027/jevshield`](https://github.com/lgy1027/jevshield)** | LangChain 安全閘（另有同名 [`rajatrao/jevshield`](https://github.com/rajatrao/jevshield)） | 無量化數據 |
| **[`AshutoshVJTI/progressgate`](https://github.com/AshutoshVJTI/progressgate)** | 偵測 AI 是否原地打轉 | 無量化數據 |
| **[`Sraavan/tripwire`](https://github.com/Sraavan/tripwire)** | AI 回應語意檢查 | 無量化數據 |
| `jev-git`、`jev-secret-detection` | commit 前擋密鑰與危險指令、程式變更是否洩密 | 貼文僅列名稱，未附量化數據（未查證具體單一 repo） |

### 2.5 模型路由與 Token 節省

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與重要模擬限制（一手 README 核對） |
| :--- | :--- | :--- |
| **[`0xNatoshi/jev-codex-router`](https://github.com/0xNatoshi/jev-codex-router#jev-codex-router)** | Codex 每輪用 Jev 決定模型與思考深度 | 專案自述：237 個歷史回合回測較全用最貴模型少 ~60%。**重要限制**：作者於 README 明示此數字為**舊版路由政策（Legacy Policy）的歷史模擬回測，並非實際量測的 Codex 配額或帳單節省，也不證明現行版本政策的實際成效** |
| **`jev-router`（同名多專案）** | Claude Code 模型路由，對應 [`gargpratyush/jev-router`](https://github.com/gargpratyush/jev-router) 與 [`BillionsBobby/JevRouter`](https://github.com/BillionsBobby/JevRouter) | 無統一第三方實測數據 |
| **[`tamaratran/jev-pruner`](https://github.com/tamaratran/jev-pruner)** | 修剪過長 Bash 輸出 | 無量化數據 |
| **[`win4r/jev-skill-suggester`](https://github.com/win4r/jev-skill-suggester)** | 推薦該用哪個 skill（中英雙語） | 無量化數據 |
| **[`kunchenguid/compact-adviser`](https://github.com/kunchenguid/compact-adviser)** | 判斷何時適合壓縮對話 | 無量化數據 |
| **[`EliaAlberti/jev-rules`](https://github.com/EliaAlberti/jev-rules)** | 挑出適用規則減少 Claude 讀取量 | 無量化數據 |
| **[`Dicklesworthstone/skillranker`](https://github.com/Dicklesworthstone/skillranker)** | 依當下狀況排序 skill | 無量化數據 |

### 2.6 瀏覽器自動化

| 專案名稱與可追溯出處 | 功能描述 | 實測數據與快照差異 |
| :--- | :--- | :--- |
| **[`browser-use/jev-ultrafast`](https://github.com/browser-use/jev-ultrafast)** | AI 瀏覽器自動操作：每步點哪裡交 Jev 決定、需要打字才請小模型 | 貼文 2026-09-21 快照記錄為 **13,061 顆星**（2026-11-22 查 GitHub API 已增長至 24,708 顆星）；README 示範 Google 航班搜尋蘇黎世→倫敦 7.1 秒（專案自述示範） |

### 2.7 程式開發工具、遊戲與交易（貼文概覽）

- **程式開發**：`jev-review`、`jev-semgrep`、`jev-shell-history`、`jevcache`（貼文僅列名稱，無量化數據）。
- **遊戲展示**：超級瑪利歐、寶可夢、俄羅斯方塊、五子棋、星海爭霸、文明帝國二代等。於 2026-09 快照時點皆將遊戲狀態轉文字餵入以展示反應速度，文明帝國作者明載未驗證能完整贏一場。
- **交易（高風險，僅供知悉）**：`QuantDinger`、`jev-trader`（無驗證數據）。

### 2.8 兩項評測基準專案之一手方法與結果核實（重要校準）

貼文簡述了兩項「測出不理想」的案例，經查核兩專案之 GitHub 原始 README，必須補齊其真實樣本組成、實驗配置與裁判偏差：

| 評測專案與一手出處 | 貼文簡述 | 原始 README 一手核實結果（關鍵細節與修正） |
| :--- | :--- | :--- |
| **[`anisselbd/jev-phishing-bench`](https://github.com/anisselbd/jev-phishing-bench)** | 2,000 封釣魚郵件：Jev 準確率 62.6%，Claude Haiku 4.5 為 81.3% | 1. **樣本組成**：2,000 封測試集實為 **1,000 封釣魚郵件 + 1,000 封正常郵件**（非全為釣魚信）。<br>2. **版本與配置差異**：`62.6%`（對照 Haiku 4.5 的 `81.3%`）僅限於 **Jev 1.13 直接單次判斷（Direct Classification）**配置；**同一研究將問題拆解為多項訊號（Decomposed Signals）後，在保留集（Holdout Set）達到 `95.0%` 準確率**。因此不能將 `62.6%` 直接概括為 Jev 整體模型能力上限。 |
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
  │     └── 邊界：直接單次判斷複雜釣魚信較弱 (Jev 1.13 為 62.6%，拆解訊號可達 95.0%)；繁中表現待實測
  │
  ├── Google Decisions API / Decision 1（後發者，2026-11-11）
  │     ├── Google 官方自述 JevBench 92.2%、Top-1 ECE 0.0250、原生多模態輸入
  │     └── 邊界：When2Call (79.9%) 與 7 項基準總成本 ($0.88) 略遜於 Jev 1.14
  │
  └── 本機替代方案
        └── JustVugg/colibri（三層式 MoE、本地零 API 成本之 Jev 相容 /v1/systemone 端點）
```

### 4.2 與本專案的直接交集與證據邊界

1. **Agent 守門員模式**：[`anpicasso/hermes-jev-approvals`](https://github.com/anpicasso/hermes-jev-approvals)（153 指令自述快 8.7×）、[`valentynkit/jev-belay`](https://github.com/valentynkit/jev-belay) 與 [`noplan-inc/limpet`](https://github.com/noplan-inc/limpet)（防提早收工）提供了以 `Noul` 二元判斷輔助執行期把關的架構參考，可與本專案確定性檢查腳本互補。
2. **模型路由模擬與實測的區分**：[`0xNatoshi/jev-codex-router`](https://github.com/0xNatoshi/jev-codex-router#jev-codex-router) 的 237 回合省 ~60% **僅為舊版路由政策的歷史模擬回測，非實測 Codex 配額節省，亦不證明現行政策成效**；在與本專案 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 對照時，僅能視為路由模擬概念，不能當作已驗證的實際帳單節省證據。
3. **訊號拆解（Signal Decomposition）與繁中防禦部署建議**：從 [`anisselbd/jev-phishing-bench`](https://github.com/anisselbd/jev-phishing-bench)（Jev 1.13 直接判斷 62.6% vs. 拆解訊號保留集 95.0%）可知，使用 System One 模型處理安全判斷時，**應將複雜問題拆解為具體、可判定的結構化子訊號**；且在 `Jev 1.14` 繁體中文表現完成本地實測前，本機防禦上建議優先搭配確定性規則與置信度門檻（此為本專案部署建議，非官方硬性限制規格）。

---

## 5. 行動清單（Action Items）

- [ ] **`T-20261122-05`**｜**[優先級：中]** 將 Jev by TypeSafe AI 生態中與 Agent 安全閘門（`anpicasso/hermes-jev-approvals`、`valentynkit/jev-belay`、`noplan-inc/limpet`、`AshutoshVJTI/progressgate`）與模型路由（`0xNatoshi/jev-codex-router`、`gargpratyush/jev-router`）相關的專案架構與數據限制，對照 Google Decisions API / Colibri 整理至 `docs/system-one-decision-model-landscape.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\system-one-decision-model-landscape.md`（收錄於集群 3）
  - **執行步驟**：
    1. 彙整 Jev 生態代表性專案（附確切 `owner/repo` 網址與 2026-09-21 快照日期），區分 2026-09 純文字快照與 2026-10-14 新增實驗性圖片／`Box` 原語之現行規格，並註明 `Choice` 上限 255 類與 `kyotofin/tax-doc-classifier` 分層請求（261 種表單）架構。
    2. 完整記錄 `0xNatoshi/jev-codex-router`（舊政策歷史模擬、非實測配額節省、不代表現行成效）、`anisselbd/jev-phishing-bench`（1,000 釣魚 + 1,000 正常樣本；Jev 1.13 直接判斷 62.6% vs. 拆解訊號保留集 95.0%）與 `zhuyansen/jev-search-rerank-eval`（9,831 組為 Jev/Haiku 模型標註與 Claude 裁決、合併標籤下相對 `bge-m3` 信賴區間跨零、排除 Jev 裁判後顯著較差）之一手方法與限制。
    3. 標明 `Jev 1.14` 已改善多語支援、現行繁中表現為【待實測】，並將本專案的防禦性部署建議（結構化訊號拆解、置信度門檻）與已確認官方規格分開。
    4. 整合 Agent 守門員模式（指令審核、防提早收工、原地打轉偵測）的通用架構模板。
  - **驗收標準（DoD）**：產出 `docs/system-one-decision-model-landscape.md`，含 Jev（區分 9 月快照與 10 月圖片/`Box` 更新）/ Decision 1 / Colibri 三方對照表、各專案 `owner/repo` 出處與實驗限制（釣魚信拆解訊號 95.0%、搜尋排序模型標註偏差、路由舊政策模擬聲明），且 `python tools/verify_inbox.py` 驗證通過。
