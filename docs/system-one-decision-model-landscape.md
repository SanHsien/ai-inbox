# System One 決策模型全景與 Agent 守門／路由架構手冊

> 本文件收錄於 `docs/system-one-decision-model-landscape.md`，為任務 `T-20261122-05` 之產出成果。
> 核心目的：彙整「非生成式（System One）分類與決策模型」在 AI Agent 安全閘門、模型路由、瀏覽器自動化與二元／枚舉判斷的量化實測數據與架構模式，並針對 **TypeSafe Jev**、**Google Gemini Decision 1（Decisions API）** 與本機開源替代方案 **`JustVugg/colibri`（`/v1/systemone`）** 進行三方對照，建立全繁體中文作業環境下的硬約束與降級策略。

---

## 0. 來源筆記與交叉參照

- [`notes/2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog.md`](../notes/2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog.md)（Jev 上線六天 1,528 個開源專案生態盤點與實測數據彙整）
- [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](../notes/2026-11-20-gemini-decision-1-decisions-api-eval.md)（Google Gemini Decision 1 與 Decisions API 評析、ECE 校準誤差與官方限制）
- [`notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md`](../notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md)（Gemini API Tool Retrieval 按需動態載入工具 Schema 與 MCP 整合）
- [`notes/2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md`](../notes/2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md)（`JustVugg/colibri` 三層式 MoE 推理引擎與零生成 `/v1/systemone` 決策端點）
- [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](../notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（四級模型分工中的快速決策層定位）
- [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](../notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（二元與枚舉決策 API 的執行期觸發機制）
- [`docs/model-burn-rate-routing-matrix.md`](./model-burn-rate-routing-matrix.md)（跨模型 Token 燃燒率與路由選型總表）
- [`docs/gemini-tool-retrieval-and-mcp-spec.md`](./gemini-tool-retrieval-and-mcp-spec.md)（Gemini Tool Retrieval 與 MCP 按需載入整合規範）

---

## 1. System One 決策模型核心機制與三大原語

傳統 LLM（System Two 生成式模型）透過自回歸（Autoregressive）逐 Token 生成文字或 JSON，當僅需判斷「是否放行指令」「該路由給哪個模型」「這封信屬於哪一類」時，不僅耗費 Output Token 與首字延遲，更容易因 JSON 格式破裂或信心度未經校準（Uncalibrated Confidence）而難以設定自動化門檻。

**System One 決策模型**完全捨棄文字生成，僅透過**單次前向傳播（Single Forward Pass）**對封閉選項集評分，回傳結構化結果與校準後的機率分佈（`0.01～0.99`）：

```text
[輸入：文字 / JSON / 多模態狀態 + 封閉選項定義]
                     │
                     ▼ (單次前向傳播，0 Output Tokens，70~250ms)
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
  [ Noul ]       [ Choice ]     [ Score ]
 二元是/否判斷    2~255 類單選   有序量尺等級評分
 (Yes/No + p)   (Top-K + p_i)  (0 起算期望值 + p)
```

| 判斷原語 | 型別名稱（Jev / Decisions API） | 輸入與輸出定義 | 典型 Agent 應用場景 |
| :--- | :--- | :--- | :--- |
| **二元判斷** | `Noul` / `noul` | 針對是非題回傳布林結果與校準機率 $p \in [0.01, 0.99]$ | 指令安全放行審核、AI 宣稱完工之證據檢核、是否觸發對話壓縮、是否有洩密風險 |
| **多選分類** | `Choice` / `choice` | 從 2 至 255 個候選類別中挑選最佳項並給出各選項歸一化機率 | 模型與思考深度路由（Opus / Sonnet / Flash）、信件與報稅表單分類、UI 下一步點擊目標 |
| **量尺評分** | `Score` / `score` | 依據 Rubric 量尺（等級從 0 起算）回傳加權評分與信心度 | 程式碼變更風險等級、客服工單緊急度、搜尋結果重排序（Re-ranking）輔助分數 |

---

## 2. Jev / Gemini Decision 1 / Colibri 三方規格與基準對照表

以下整合 TypeSafe AI 官方與社群基準、Google Decisions API 官方部落格／文件（2026-11-21 查證）以及 `JustVugg/colibri`（v2.1.0）本機適配數據：

| 比較維度 | TypeSafe Jev (`Jev 1.14`) | Google Gemini Decision 1 (`gemini-decision-1`) | 本機開源 `JustVugg/colibri` (`System One`) |
| :--- | :--- | :--- | :--- |
| **定位與部署形態** | 雲端專用 System One API（先行者，2026-09-15 發布） | 雲端多模態決策 API（`v1beta`，需 `google-genai` SDK $\ge$ 3.2） | 本機離線推理引擎（內建 `laya` / `gliner_decide`，相容 Jev API `POST /v1/systemone`） |
| **輸入模態與上下文** | **純文字 / JSON**（無法直接讀圖，視覺應用須先轉文字或 DOM/A11y 樹） | **最高 256K 多模態**（文字、JSON、圖片、音訊、影片、PDF）；單次可混跑 1,000 題 | 純文字 / JSON（本機模型權重約 `0.85 GB` / `1.95 GB`，RAM 需求 `1.7–1.9 GB`） |
| **計費模式** | 僅計 Input Token、輸出 Token 為 $0（7 項共用基準總成本 **$0.68**，四者最便宜） | 付費層 **`$0.10 / 1M input tokens`**、輸出 **`$0`**（7 項共用基準總成本 **$0.88**；不支援 Context Caching / Batch） | **本機零 API 費用**（消耗本機 CPU / GPU 電力） |
| **端到端延遲** | 官方宣稱 **70–500 ms**（語音瀏覽器實測每字約 ~300 ms） | 模型運算 50–100 ms、端到端 **150–250 ms**（官方註明於 $\le$ 16K tokens 情境量測） | 官方 CUDA 基準約 **13–57 ms/題**（本機 RTX 3060 12GB 預估可常駐，尚未實測） |
| **置信度校準誤差（Top-1 ECE，越低越準）** | **`0.0494`**（顯著優於 GPT-6 Luna `0.0721` 與 Flash-Lite `0.2104`） | **`0.0250`**（7 項共用評測最佳，最可信賴的自動／人工分流機率門檻）【官方自述】 | 未公布標準 ECE 數據（依賴底層 `laya` / `gliner_decide` 校準品質） |
| **基準強項（Benchmark Wins）** | **`When2Call`（82.0%，勝 Decision 1）**、`Mind2Web Multimodal`（86.8%，勝 Decision 1） | **`JevBench`（92.2%）**、`Global-MMLU-Lite`（86.0%）、`PubMedQA`（79.8%）、`Amazon ESCI`（58.7%）等 9 項拿 7 項第一 | 離線零網路延遲、無隱私外流風險、與 `COLI_PARK` 跨輪 KV 暫存協同 |
| **已知短板與反面限制** | 釣魚郵件檢測準確率僅 **62.6%**（輸 Haiku 4.5 的 81.3%）；單獨做中英搜尋排序不如一般語意搜尋；**官方明載中文精準度較低** | `When2Call`（判斷是否呼叫工具）僅 **79.9%**（約每 5 題錯 1 題）；不支援 Context Caching，重複長前綴每次全額計費 | 僅適合輕量分類，複雜多語意推理能力受限於 1B~2B 級本地小模型容量 |
| **與 Tool Retrieval 互補性** | 透過社群 `jev-rules` / `skillranker` 在客戶端預篩規則與 Skill | 與 Gemini API 原生 **Tool Retrieval（`tool_search` + `defer_loading: true`）** 同平台互補（Decisions API 負責前置路由，Tool Retrieval 負責百級 MCP Schema 按需載入） | 可作為本機 MCP 工具或規則載入前的零成本本地粗篩器 |

---

## 3. Jev 上線六日（1,528 專案）量化實測數據與反面案例總覽

根據社群盤點（截至 2026-09-21 共 1,528 個 GitHub 專案，約 260 個進入精選清單，其中約 40 個附帶量化測試數據），以下萃取具明確指標的代表性專案與反面校準案例（均標記為【社群單一專案自述】，未經第三方獨立重現）：

### 3.1 具量化指標之正向實測專案

| 領域分類 | 專案名稱 | 核心機制與測試規模 | 量化實測指標（速度 / 成本 / 準確率） | 架構啟發與限制備註 |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 指令審核閘門** | `hermes-jev-approvals` | 以 Jev 預審 Hermes Agent 待執行指令：安全直接放行、可疑才跳出問人（153 個真實指令測試） | 審核速度**快 8.7 倍**、需人工介入回答次數**減少 4.4 倍** | 證明高頻 CLI 指令審核可用 `Noul` + 信心門檻取代全量人工確認或慢速 LLM 審查 |
| **Agent 模型與深度路由** | `jev-codex-router` | 每一輪對話先用 Jev (`Choice`) 決定該派給哪個模型與思考深度（237 個歷史對話回合回測） | 總成本較「全程使用最貴模型」**節省約 60%** | 作者自註為舊版規則回測模擬，不代表現版實際節省；但驗證了前置路由的經濟效益 |
| **瀏覽器高速自動化** | `jev-ultrafast` (`browser-use` 團隊) | 瀏覽器每一步操作與點擊目標（DOM 元素選擇）交由 Jev 決定，僅在需要打字輸入時才呼叫小模型（13,061 Stars） | Google 航班搜尋「蘇黎世飛倫敦」端到端**僅需 7.1 秒** | 將 GUI 導航拆解為「高頻封閉選項選擇（Jev）+ 低頻文字生成（LLM）」，大幅消減延遲 |
| **高多樣性表單歸類** | `tax-doc-classifier` | 逐頁辨識美國報稅文件屬於 261 種官方表單中的哪一種（753 頁空白官方表單測試 + 數千份自家實務文件） | 753 頁測試**零分錯**（約 5% 把握度偏低轉人工）；每頁成本約 **$0.001 美元** | 完美契合 `Choice`（上限 255~261 類）+ 低信心度 Fallback 人工複核的生產級流水線 |
| **影音字幕業配跳過** | `jev-skip` | 讀取 YouTube 字幕逐段判斷是否為業配並自動跳過（23 支影片對照 SponsorBlock 群眾標註） | 抓出 SponsorBlock 標註業配秒數的 **77%**；每支影片成本約 **$0.0008 美元**；每小時誤跳約 **34 秒** | 作者註明數據經轉接服務測試；顯示長文本分段二元分類成本極低，但存在假陽性誤跳邊界 |
| **即時語音操控** | `jev-voice-browser` | 邊說話邊以 Jev 判斷操作意圖與點擊目標 | 每說一個字約花 **0.3 秒（300 ms）** 完成意圖判斷 | 反應速度快到「話還沒說完就開始動作」，需注意誤觸發防護 |

### 3.2 測出不理想之反面案例（關鍵校準邊界）

| 反面案例專案 | 測試設計與樣本規模 | 實測數據結果 | 失敗原因與架構教訓 |
| :--- | :--- | :--- | :--- |
| **`jev-phishing-bench`（釣魚郵件偵測）** | 2,000 封釣魚郵件測試，對比 Jev 與 Anthropic 小型生成模型 `Claude Haiku 4.5` | Jev 準確率僅 **62.6%** vs. Claude Haiku 4.5 達 **81.3%** | 釣魚郵件涉及深層語意偽裝、上下文矛盾與社交工程推理，System One 單次前向分類無法取代具備基礎推理能力的生成式小模型。**安全攸關的複雜語意判斷不可單靠 Jev。** |
| **`jev-search-rerank-eval`（中英搜尋排序）** | 164 個中英文查詢、9,831 組人工評分測試搜尋結果排序 | **Jev 單獨排序表現不如一般語意搜尋（Embedding Search）**；將兩者合併使用才取得最佳成績 | System One 模型不適合直接替代稠密向量檢索（Dense Retrieval），正確位置是在 Embedding 召回後作為多重訊號融合（Hybrid Reranking）的一環，且受限於中文語意精準度下降。 |

---

## 4. 全繁體中文作業環境之硬約束與降級策略

TypeSafe AI 官方文件明確聲明：**Jev 以英文輸入最準確，中文、日文、韓文雖可使用但精準度較低**；同時 `jev-search-rerank-eval` 亦涵蓋中英文查詢的表現落差。針對本機與團隊之**全繁體中文作業環境**，訂定以下四條硬約束與降級策略：

1. **禁止在繁體中文高風險安全閘門單獨使用 Jev 裸判**：
   - 凡涉及「外部中文網頁／貼文之 Indirect Prompt Injection 檢測」「中文業務指令放行」「釣魚與社交工程識別」，嚴禁單靠 Jev 的中文 `Noul` 分數直接放行（參考釣魚信僅 62.6% 準確率）。
   - **降級策略**：優先採用確定性規則（Regex / AST / 路徑白名單，如 `verify_agent_skill_pack_safety.py` 與 `screen_privacy.py`）作為第一道硬防線；若需模型語意判斷，改用多語能力經 Global-MMLU-Lite（86.0%）驗證的 `Gemini Decision 1` 或直接交由 `Claude Haiku 4.5` / `Gemini 3.8 Flash` 進行結構化審查。
2. **結構化特徵英文化（English-Normalized Feature Extraction）**：
   - 當在本地 Agent 工具鏈（如 CLI 指令審核、Git diff 密鑰掃描、DOM 元素選擇）調用 System One 模型時，應將輸入狀態轉換為**程式碼、CLI 參數、英文 Schema 標籤或路徑結構**，並以**英文撰寫選項標籤與 Rubric 判準**，避開中文字元分詞與語意偏移。
3. **強制設定置信度雙門檻與灰區降級（Confidence Threshold & Gray-Zone Fallback）**：
   - 無論使用 Jev（ECE `0.0494`）或 Gemini Decision 1（ECE `0.0250`），機率が固定落在 `[0.01, 0.99]`。
   - 實務部署必須設定雙門檻：高信心區（如 $p \ge 0.90$）自動執行、低信心拒絕區（如 $p \le 0.20$）直接攔截，**中間灰區（$0.20 < p < 0.90$）一律降級至使用者確認或高階模型（System Two）複審**（呼應 `tax-doc-classifier` 將 5% 低把握度表單轉人工而達成零錯誤的做法）。
4. **工具選擇（When2Call）與百級工具檢索的職責分離**：
   - `Gemini Decision 1` 在 `When2Call` 基準僅 79.9%（約每 5 題錯 1 題），落後 Jev 1.14 的 82.0%。因此**不要用 Decision 1 自己硬寫百個工具的路由表**；在 Gemini 生態中，應直接使用伺服器端原生 **Tool Retrieval（`tool_search` + `defer_loading: true`）** 處理按需 Schema 載入，將 Decision 1 / Jev 留給「模型檔位選擇（Fast/Slow Path）」與「執行前後狀態檢核」。

---

## 5. Agent 守門員與模型路由通用架構模板

結合 Jev 生態四大守門模式（`hermes-jev-approvals`、`jev-belay` / `limpet`、`jev-git` / `jev-secret-detection`、`progressgate`）與模型路由（`jev-codex-router`），提煉出可套用於本地 Coding Agent 的三段式攔截與路由流水線：

```text
[使用者任務 / Agent 迴圈]
   │
   ├─► 階段 A：前置路由與規則預篩 (Pre-Routing & Context Pruning)
   │     ├── 模型檔位路由 (jev-codex-router / Decision 1 Choice)
   │     │     └─► 簡單查詢/單檔修改 ──► Flash / Haiku / Sol
   │     │     └─► 跨模組重構/除錯   ──► Opus / Neon / Astra
   │     └── 工具與規則按需掛載
   │           └─► Gemini Tool Retrieval (defer_loading: true) 或 jev-rules 預篩
   │
   ├─► 階段 B：執行期安全與進度守門 (Runtime Approval & Progress Gate)
   │     ├── 指令審核閘 (hermes-jev-approvals 模式：確定性黑名單 + Noul 信心門檻)
   │     │     └─► 唯讀/白名單測試指令 ($p \ge 0.92$) ──► 自動放行
   │     │     └─► 跨目錄/網路/刪改高危指令           ──► 強制跳出人工審批
   │     ├── 密鑰與變更守門 (jev-git / jev-secret-detection 模式)
   │     │     └─► Commit 前比對 Regex + 語意洩密檢測
   │     └── 原地打轉偵測 (progressgate 模式)
   │           └─► 連續 3 輪錯誤相同或無實質 diff ──► 觸發升級或請求使用者介入
   │
   └─► 階段 C：收尾防提早收工閘門 (Anti-Premature-Exit / Belay Gate)
         └── 完工證據檢核 (jev-belay / limpet 模式)
               └─► Agent 宣稱「已完成/測試通過」時，掃描對話紀錄是否含實際驗證指令與綠燈 stdout
               └─► 若無實測證據 ($p < 0.85$) ──► 攔截收尾回覆，強制退回補跑驗證
```

### 5.1 三大核心守門員實作規格對照

| 守門員類型 | 代表開源專案 | 判斷原語與輸入狀態 | 通過／攔截準則（結合本機硬閘門） |
| :--- | :--- | :--- | :--- |
| **1. 指令風險審核閘（Command Approval Gate）** | `hermes-jev-approvals`、`pi-jev`、`jev-guard` | 原語：`Noul`（`is_safe_readonly_command`）<br>輸入：待執行之 CLI 字串、工作目錄、目標路徑 | 1. **先過機械靜態防線**：若觸及專案目錄外讀寫、金鑰變數、破沙盒旗標，直接攔截。<br>2. **次過 System One 分類**：僅當 $p \ge 0.92$ 判定為常規建置／唯讀查詢時免打擾放行，其餘一律交由客戶端審批。 |
| **2. 防提早收工閘（Anti-Premature-Exit Belay Gate）** | `jev-belay`、`limpet`、`tripwire` | 原語：`Noul`（`has_verified_test_output`）<br>輸入：Agent 擬輸出的結案宣告 + 最近 3 輪 Tool Call 執行輸出摘要 | 對齊全域規範「回報完成之前，要真的執行過檢查並貼出它的輸出」：<br>- 若檢核未見實際測試／驗證腳本之退出碼 0 與 stdout，直接拒絕結案並注入提示詞要求補跑驗證。 |
| **3. 原地打轉與壓縮閘（Progress & Compaction Gate）** | `progressgate`、`compact-adviser`、`jev-pruner` | 原語：`Choice`（`making_progress` / `spinning_loop` / `needs_compaction`）<br>輸入：最近 N 輪錯誤訊息摘要與 Context 長度指標 | - 判定為 `spinning_loop` 時，暫停自動重試並切換至強模型覆核或向使用者報告卡點。<br>- 判定為 `needs_compaction` 時，提醒執行 `/compact` 或裁剪過長 Bash 輸出（`jev-pruner`）。 |
