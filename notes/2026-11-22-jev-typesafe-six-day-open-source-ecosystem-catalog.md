---
id: "2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog"
title: "社群原創盤點：Jev by TypeSafe AI 上線六天 1,528 專案生態——Agent 守門員、模型路由、瀏覽器自動化與分類判斷全景分析"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "使用者直接提供全文（疑似 Threads / Facebook 原創貼文）"
author: "楊三賢 (SanHsien)"
analyzed_at: "2026-11-22"
analyzed_by: "antigravity"
written_by: "antigravity/claude-opus-4.6@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
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

- **來源**：使用者（楊三賢）直接提供全文（無 URL），內容為原創社群貼文，發表時間推估 `2026-09-21` 或之後
- **分析日期**：`2026-11-22`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-17-github-open-source-ai-toolkit-matrix.md`](./2026-10-17-github-open-source-ai-toolkit-matrix.md)（GitHub 開源 AI 工具矩陣：Jev 亞秒路由）
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（Claude Code 四級模型分工：Jev 快速決策角色）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（Jev 作為「是/否、選哪個」決策 API 的執行期觸發機制）
  - [`notes/2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md`](./2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md)（Jev API 相容的零生成 System One 端點）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](./2026-11-20-gemini-decision-1-decisions-api-eval.md)（Google Decisions API 與 JevBench 基準）

---

## 1. Jev 模型定位摘要（依貼文與 TypeSafe AI 官方說明轉述）

TypeSafe AI 於 2026-09-15 發布 Jev。依貼文整理之官方文件核心特徵（二手轉述）：

- **不生成文字**：只接收文字/JSON 狀態與有界選項集，回傳選擇結果與校準後的信心機率。
- **三種判斷原語**：`Choice`（多選分類，最多 255 類）、`Noul`（布林機率）、`Score`（量尺評分）。
- **延遲**：70～500 ms（貼文引述官方文件宣稱值，未獨立重測）。
- **計費**：輸出 Token 為零、僅計入 Input Token。
- **語言能力**：官方文件聲明英文最準；中文、日文、韓文可用但精準度較低。

---

## 2. 六日生態概觀：1,528 專案的結構化拆解（各專案 README 自述快照）

依貼文統計（截至 2026-09-21 快照），GitHub 上 2026-09-12 以後建立、名稱或介紹同時提到 Jev 與 TypeSafe 的專案計 **1,528** 個。兩份社群清單加展示牆約收錄 260 個，其中附具體測試數字的約 40 個。

> **證據等級聲明**：下表所列各專案功能、星數與實測數據，均為**貼文作者轉述各該開源專案 README 之自述數據（二手轉述，截至 2026-09-21 快照）**，多數專案未附完整測試集與重現腳本，本 repo 未逐一獨立重跑驗證。

### 2.1 內容過濾與雜訊清除（6 專案）

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| **✓ jev-skip** | 讀 YouTube 字幕判斷業配並自動跳過 | 23 支影片：抓出 SponsorBlock 標註之 77%，每支成本 ~\$0.0008，每小時誤跳 ~34 秒 |
| ✓ sift | Chrome 擴充功能：X 貼文六分類（有料/幽默/閒聊/推銷/垃圾/AI 寫的）並隱藏 | 無 |
| ✓ unclutter | 判斷網頁區塊為雜訊並移除 | 無 |
| typesafe-adblock | 判斷網頁元素是否廣告（作者自述「好玩的專案」） | 無 |
| ✓ jev_antispam_bot | Telegram 群組防灌水 | 無 |
| ✓ youtube-sponsor-detection | YouTube 業配片段偵測 | 無 |

### 2.2 信箱與文件分類（3 專案）

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| **✓ jevmail** | Gmail 五分類（需回覆/通知/促銷/推銷/垃圾），只讀不刪、本機執行 | 無 |
| ✓ jev-mail-classifier | 信件分類並自動貼標籤、搬資料夾、提醒 | 無 |
| **✓ tax-doc-classifier** | 美國報稅文件逐頁辨識 261 種表單 | 753 頁空白官方表單零錯誤（~5% 低信心）；每頁 ~\$0.001 |

### 2.3 語音/電腦/家電操作（4 專案）

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| **✓ jev-voice-browser** | 語音操作瀏覽器（每字 Jev 判斷 ~0.3s） | 常常話未說完即開始動作 |
| ✓ jev-use | 一句話操作 Mac（讀系統輔助功能畫面資訊，不截圖） | 無 |
| ✓ HA-Jev | Home Assistant 居家自動化問答與觸發 | 無 |
| ✓ mobile-jev | 手機畫面操作 | 無 |

### 2.4 AI Agent 守門員（17+ 專案，核心類別）

此類別直接對應本專案已追蹤的「Agent 安全閘門與執行期控制」主題，與既有 `2026-10-31` / `2026-11-01` 兩篇 Claude Code 四級分工筆記高度關聯：

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| **✓ hermes-jev-approvals** | Hermes Agent 指令語意審核：安全直接放行、可疑才問人 | **153 個真實指令：審核快 8.7×、人工介入頻率降 4.4×** |
| **✓ jev-belay** | Claude Code 說「做完了」先查對話紀錄找證據 | 無 |
| **✓ limpet** | 不讓 AI 助理提早收工 | 無 |
| ✓ pi-jev | Pi 工具風險閘 | 無 |
| jev-guard | 提示注入與危險動作守門 | 無 |
| jev-harness | 判斷閘與影子模式 | 無 |
| jevshield | LangChain 安全閘 | 無 |
| jev-git | commit 前擋密鑰與危險指令 | 無 |
| jev-secret-detection | 程式變更是否洩密 | 無 |
| progressgate | AI 是否原地打轉 | 無 |
| tripwire | AI 回應七項語意檢查 | 無 |

### 2.5 模型路由與 Token 節省（14+ 專案）

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| **✓ jev-codex-router** | Codex 每輪用 Jev 選模型與思考深度 | **237 回合回測：成本較全量最貴模型降 ~60%**（舊版規則模擬，作者自註不代表現版） |
| jev-router | Claude Code 選最便宜可用模型 | 無 |
| ✓ jev-pruner | 修剪過長 Bash 輸出 | 無 |
| ✓ jev-skill-suggester | 推薦該用哪個 skill（中英雙語） | 無 |
| compact-adviser | 何時適合壓縮對話 | 無 |
| jev-rules | 挑出適用規則減少 Claude 讀取量 | 無 |
| skillranker | 依當下狀況排序 skill | 無 |

### 2.6 瀏覽器自動化（9+ 專案）

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| **✓ jev-ultrafast (browser-use 團隊)** | AI 瀏覽器自動操作：每步操作交 Jev 判斷、需要打字才請小模型 | **13,061 顆星**（該批次最多收藏）；示範 Google Flights 搜尋蘇黎世→倫敦 7.1 秒 |

### 2.7 程式開發工具（15+ 專案）

| 專案 | 功能 | 實測數據 |
| :--- | :--- | :--- |
| ✓ jev-review | 分階段程式碼審查 | 無 |
| ✓ jev-semgrep | 語意搜尋程式碼（日英雙語） | 無 |
| ✓ jev-shell-history | 終端機歷史指令建議 | 無 |
| ✓ jevcache | 判斷結果快取 | 無 |

### 2.8 測出不理想的反面案例（2 專案，重要校準參考）

| 專案 | 結果 |
| :--- | :--- |
| **✓ jev-phishing-bench** | 2,000 封釣魚郵件：Jev 準確率 **62.6%**，Claude Haiku 4.5 為 **81.3%**（Jev 贏在速度/成本但精準度輸） |
| **✓ jev-search-rerank-eval** | 164 中英文查詢、9,831 組人工評分：Jev 單獨排序不如一般語意搜尋；**合併使用才是最佳組合** |

### 2.9 遊戲與展示（15+ 專案）

超級瑪利歐、寶可夢、俄羅斯方塊、五子棋、星海爭霸、文明帝國二代等。所有專案皆將遊戲狀態轉成文字餵入（Jev 不讀畫面），用以展示反應速度而非遊戲能力。文明帝國作者明載尚未驗證能完整贏一場。

### 2.10 交易（高風險，僅供知悉）

| 專案 | 功能 |
| :--- | :--- |
| ✓ QuantDinger | 開源 AI 交易系統整合 Jev |
| ✓ jev-trader | 鏈上每個區塊做一次交易決策 |

---

## 3. 原文附帶的四項注意事項（作者自述）

原作者明確列出的健康警告，本身即構成高價值的校準聲明：

1. **大多數專案沒有附數字**：~260 個收錄專案中僅 ~40 個附具體測試數據，其餘僅一句話描述。
2. **星星多不等於效果好**：收藏數反映關注度而非品質；多數專案為上線一週內建立，尚未經過長時間驗證。
3. **文字以外的東西不能直接處理**：官方文件明載 Jev 只讀文字；看似「看畫面」的專案全部是先把畫面轉文字。
4. **中文要自己測**：官方聲明英文最準，中/日/韓可用但精準度較低。

---

## 4. 對既有專案與架構之結構性啟發

### 4.1 Jev 生態與 Gemini Decisions API / Tool Retrieval 的戰略對位

```
[決策模型光譜：System One 分類判斷]
  ├── TypeSafe Jev（先行者，2026-09-15）
  │     ├── 優勢：生態先發、1,528+ 開源專案、MCP 工具支援
  │     └── 侷限：釣魚信 62.6% 準確率、中文精準度較低、無法讀圖
  │
  ├── Google Decisions API / Decision 1（後發者，2026-11-11）
  │     ├── Google 官方自述 JevBench 92.2%、Top-1 ECE 0.0250、支援多模態輸入
  │     └── 邊界：When2Call (79.9% vs Jev 82.0%) 與 7 項評測總成本 ($0.88 vs Jev $0.68) 仍由 Jev 領先
  │
  └── 本機替代方案
        └── JustVugg/colibri（三層式 MoE、Jev API 相容端點）
```

### 4.2 與本專案的直接交集

1. **Agent 守門員模式已模式化**：`hermes-jev-approvals`（153 指令實測 8.7× 加速）與本專案全域規範中「回報完成之前要真的執行過檢查」、`jev-belay` / `limpet` 防止 AI 提早收工，直接映射至全域規範中「不准用註解掉測試…讓東西過關」。
2. **模型路由經濟學**：`jev-codex-router` 237 回合回測降成本 60%，與既有 `model-burn-rate-routing-matrix.md` 中模型選用成本分析可互相校驗。
3. **中文能力警告**：Jev 官方明載中文精準度較低，對本專案（全繁體中文作業環境）的 Agent 路由決策構成硬約束——關鍵判斷不應僅依賴 Jev 中文輸入。

---

## 5. 行動清單（Action Items）

- [ ] **`T-20261122-05`**｜**[優先級：中]** 將 Jev by TypeSafe AI 生態中與 Agent 安全閘門（hermes-jev-approvals、jev-belay、limpet、progressgate）與模型路由（jev-codex-router、jev-router）相關的量化實測數據與架構模式，對照 Google Decisions API / Tool Retrieval 整理至 `docs/system-one-decision-model-landscape.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\system-one-decision-model-landscape.md`（收錄於集群 3）
  - **執行步驟**：
    1. 彙整 Jev 生態中附有量化數據的 ~40 專案之核心指標（速度倍率、成本節省比率、準確率）。
    2. 對比 Google Decision 1 在 JevBench 92.2% 的基準成績與 Jev 自身在釣魚信/搜尋排序的反面案例。
    3. 標記中文精準度限制對全繁體中文環境的作業影響與降級策略。
    4. 整合 Agent 守門員模式（指令審核、防提早收工、密鑰洩漏攔截）的通用架構模板。
  - **驗收標準（DoD）**：產出 `docs/system-one-decision-model-landscape.md`，含 Jev / Decision 1 / Colibri 三方對照表與中文限制警告，且 `python tools/verify_inbox.py` 驗證通過。
