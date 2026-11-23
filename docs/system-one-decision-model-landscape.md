# System One 決策模型全景與 Agent 守門／路由架構手冊

> 本文件收錄於 `docs/system-one-decision-model-landscape.md`，為任務 `T-20261122-05` 之產出成果。
> 核心目的：彙整「非生成式（System One）分類與決策模型」在 AI Agent 安全閘門、模型路由、瀏覽器自動化與二元／枚舉判斷的架構模式與各開源專案實測數據限制，針對 **TypeSafe Jev（區分 2026-09 初版快照與 2026-10-14 新增實驗性圖片／`Box` 原語之現行規格，以及僅對輸入收費／輸出免費但 `usage.output_tokens` 非零的計費結構）**、**Google Gemini Decision 1（Decisions API）** 與本機開源替代方案 **`JustVugg/colibri`（`/v1/systemone`）** 進行三方對照，並建立將「已確認官方規格」與「本專案繁體中文環境防禦部署建議（含結構化訊號拆解與下游邏輯迴歸／確定性規則）」明確分離的工程規範。

---

## 0. 來源筆記與官方／開源一手依據

- **來源筆記**：`notes/2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog.md`
- **交叉參照**：
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](../notes/2026-11-20-gemini-decision-1-decisions-api-eval.md)（Google Gemini Decision 1 與 Decisions API 評析、ECE 校準誤差與官方限制）
  - `notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md`（Gemini API Tool Retrieval 按需動態載入工具 Schema 與 `v1beta` Interactions API 限制）
  - [`notes/2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md`](../notes/2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine.md)（`JustVugg/colibri` 三層式 MoE 推理引擎與零生成 `/v1/systemone` 決策端點）
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](../notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（四級模型分工中的快速決策層定位）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](../notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（二元與枚舉決策 API 的執行期觸發機制）
  - [`docs/model-burn-rate-routing-matrix.md`](./model-burn-rate-routing-matrix.md)（跨模型 Token 燃燒率與路由選型總表）
  - [`docs/gemini-tool-retrieval-and-mcp-spec.md`](./gemini-tool-retrieval-and-mcp-spec.md)（Gemini Tool Retrieval 與 MCP 按需載入整合規範）
- **TypeSafe AI 官方文件（2026-11-23 核實）**：
  - [TypeSafe AI Changelog (`https://docs.typesafe.ai/changelog`)](https://docs.typesafe.ai/changelog)
  - [Models 與計費說明 (`https://docs.typesafe.ai/models`)](https://docs.typesafe.ai/models)
  - [Choice 原語與回應格式 (`https://docs.typesafe.ai/primitives/choice`)](https://docs.typesafe.ai/primitives/choice)
  - [圖片輸入文件 (`https://docs.typesafe.ai/images`)](https://docs.typesafe.ai/images)

---

## 1. System One 決策模型核心機制與判斷原語演進

傳統 LLM（System Two 生成式模型）透過自回歸（Autoregressive）逐 Token 生成自由文字或 JSON；而 **System One 決策模型**不逐字生成自由文字，而是對有界選項或座標空間進行評分，直接回傳結構化結果與校準後的機率分佈（`0.01～0.99`）。在計費上**僅對 Input Token 收費、Output Token 免費**（但注意 API 回應的 `usage.output_tokens` 欄位仍可能為非零值，例如 [Choice 官方回應範例](https://docs.typesafe.ai/primitives/choice#response-structure) 中 `usage.output_tokens` 為 `34`，不可將「輸出免費」誤寫為「回應用量欄位必為 0」）：

```text
[輸入：文字 / JSON / 圖片狀態 + 有界判斷題目 (單次請求可含多道題目)]
                     │
                     ▼ (不逐字生成自由文字，僅對 Input Token 收費 / Output 免費，70~250ms)
      ┌──────────────┼──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
  [ Noul ]       [ Choice ]     [ Score ]       [ Box ]
 二元是/否判斷   每題 2~255 選項  有序量尺等級評分  2D 邊界框定位
 (Yes/No + p)   (Top-K + p_i)  (0 起算期望值+p) (Jev 2026-10-14 新增)
```

| 判斷原語 | 型別名稱與支援平台 | 輸入與輸出定義（依官方規格核實） | 典型 Agent 應用場景 |
| :--- | :--- | :--- | :--- |
| **二元判斷** | `Noul`（Jev） / `noul`（Decisions API） | 針對是非題回傳布林結果與校準機率 $p \in [0.01, 0.99]$ | 指令安全放行審核、工具執行前（`PreToolUse`）多題風險評估、AI 宣稱完工之證據檢核 |
| **多選分類** | `Choice`（Jev） / `choice`（Decisions API） | **每一道 `Choice` 題目最多 2 至 255 個候選選項**（[官方 Choice 文件](https://docs.typesafe.ai/primitives/choice)；同一 API 請求內可包含多道題目） | 模型與思考深度路由、信件分類、兩階段母表／附表報稅表單辨識、UI 下一步動作選擇 |
| **量尺評分** | `Score`（Jev） / `score`（Decisions API） | 依據 Rubric 量尺（等級從 0 起算）回傳加權評分與信心度 | 程式碼變更風險等級、客服工單緊急度、混合搜尋重排序（Hybrid Reranking）輔助訊號 |
| **邊界框定位** | `Box`（Jev 於 `2026-10-14` 新增，配合實驗性圖片輸入） | 於圖片輸入上回傳目標物件或 UI 元素之邊界框座標 | 視覺畫面元素定位（注：2026-09 上線初期專案皆未用此功能，係將畫面轉文字或 DOM/A11y 樹處理） |

---

## 2. Jev / Gemini Decision 1 / Colibri 三方規格與基準對照表

以下整合 TypeSafe AI 官方文件（2026-11-23 查核）、Google Decisions API 官方部落格／文件（2026-11-21 查核）以及 `JustVugg/colibri`（v2.1.0）本機適配數據：

| 比較維度 | TypeSafe Jev (`Jev 1.13` / `1.14`) | Google Gemini Decision 1 (`gemini-decision-1`) | 本機開源 `JustVugg/colibri` (`System One`) |
| :--- | :--- | :--- | :--- |
| **定位與版本演進** | 雲端專用 System One API（`2026-09-15` 發布；`2026-10-14` 新增實驗性圖片與 `Box`；`1.14` 改善多語支援） | 雲端多模態決策 API（`2026-11-11` 發布，`v1beta`，需 `google-genai` SDK $\ge$ 3.2） | 本機離線推理引擎（內建 `laya` / `gliner_decide`，提供相容 Jev 之 `POST /v1/systemone`） |
| **輸入模態與原語** | **文字 / JSON + 實驗性圖片輸入**（[Images 文件](https://docs.typesafe.ai/images)）；原語含 `Choice`（每題上限 255）、`Noul`、`Score`、`Box` | **最高 256K 多模態**（文字、JSON、圖片、音訊、影片、PDF）；單次可混跑 1,000 題（`noul`、`choice`、`score`） | 純文字 / JSON（本機模型權重約 `0.85 GB` / `1.95 GB`，RAM 需求 `1.7–1.9 GB`） |
| **計費模式** | **僅對 Input Token 收費、Output Token 免費**（見 [Models 文件](https://docs.typesafe.ai/models)；回應 `usage.output_tokens` 仍可能非零；Google 公布之 7 項共用基準總成本 **$0.68**，四者最低） | 付費層 **`$0.10 / 1M input tokens`**、輸出 **`$0`**（7 項共用基準總成本 **$0.88**；不支援 Context Caching / Batch） | **本機零 API 費用**（消耗本機 CPU / GPU 電力） |
| **端到端延遲** | 官方宣稱 **70–500 ms**（各社群專案自述中位延遲約 215–580 ms） | 模型運算 50–100 ms、端到端 **150–250 ms**（官方註明於 $\le$ 16K tokens 情境量測） | 官方 CUDA 基準約 **13–57 ms/題**（本機 RTX 3060 12GB 預估可常駐，尚未實測） |
| **置信度校準誤差（Top-1 ECE，越低越準）** | **`0.0494`**（優於 GPT-6 Luna `0.0721` 與 Flash-Lite `0.2104`）【出自 Google 部落格對照表】 | **`0.0250`**（7 項共用評測最佳）【Google 官方自述】 | 未公布標準 ECE 數據 |
| **基準強項（Benchmark Wins）** | **`When2Call`（82.0%，勝 Decision 1）**、`Mind2Web Multimodal`（86.8%，勝 Decision 1） | **`JevBench`（92.2%）**、`Global-MMLU-Lite`（86.0%）、`PubMedQA`（79.8%）、`Amazon ESCI`（58.7%）等 9 項拿 7 項第一 | 離線零網路延遲、無外部資料傳輸、與 `COLI_PARK` 跨輪 KV 暫存協同 |
| **多語言與實驗邊界** | 2026-09 初版曾提及中日韓精準度較低，**`1.14` 官方更新紀錄已註明改善多語支援**（現行繁中表現【待實測】）；`Jev 1.13` 直接單判釣魚信僅 62.6%（5 項訊號經 A 組訓練邏輯迴歸後於 B 組保留集達 95.0%） | `When2Call`（判斷是否呼叫工具）僅 **79.9%**（約每 5 題錯 1 題）；不支援 Context Caching，重複長前綴每次全額計費 | 僅適合輕量分類，複雜推理受限於 1B~2B 級本地小模型容量 |

---

## 3. Jev 生態代表性專案數據、可追溯出處與方法論限制核實

根據社群盤點（截至 `2026-09-21` 快照）與 `2026-11-23` 對各專案 GitHub 原始碼倉庫的一手 README / Metrics 文件核實，將核心專案的數據與**必須保留的方法論限制**整理如下：

### 3.1 具量化自述數據之正向應用專案（均為各專案作者自測／自述，本 repo 未獨立重測）

| 領域分類 | 專案 `owner/repo` 與出處連結 | 核心機制與測試規模（專案自述） | 專案公布之量化指標 | 架構細節與方法論限制（一手 README / Metrics 核對） |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 指令審核閘門** | [`anpicasso/hermes-jev-approvals`](https://github.com/anpicasso/hermes-jev-approvals/blob/main/docs/METRICS.md) | 以 Jev 預審 Hermes Agent 待執行指令：安全直接放行、可疑才跳出問人（**修正後 156 個跨三個設定檔分層抽樣真實指令**） | 審核速度**快 9.8 倍**（405 ms vs. 3,968 ms）、需人工中斷次數**少 4.2 倍**（10 次 vs. 42 次） | **舊樣本撤回與比較限制**：原版公布的 153 筆／8.7 倍／4.4 倍實僅含單一設定檔，作者已承認誤報並於 `docs/METRICS.md` 撤回更正；此基準仍受限於單機（Linux 2 vCPU、7 GB）、對比單一預設輔助聊天模型，且為未在真實線上會話運行的離線評估 |
| **收尾防假完成閘門** | [`valentynkit/jev-belay`](https://github.com/valentynkit/jev-belay) & [`noplan-inc/limpet`](https://github.com/noplan-inc/limpet#readme) | Claude Code / 程式助理想收工時，檢查對話紀錄是否具備完工證據 | - `jev-belay`：100 筆停止案例（含 12 筆假完成）**AUROC 0.976**（僅看結案文字為 0.777）、中位延遲 **346 ms**<br>- `limpet`：每次停止檢查約 **0.7 秒**、成本約 **US\$0.0001** | `jev-belay` 之 100 筆案例來自單一作者會話並由模型代理協助標註（小樣本）；`limpet` 僅提供延遲與成本自述，未提供標準化準確率基準 |
| **工具執行前風險閘** | [`Sraavan/tripwire`](https://github.com/Sraavan/tripwire#readme) & [`leepokai/jev-guard`](https://github.com/leepokai/jev-guard#why-jev-price-and-speed-with-sources) | `tripwire` 在 Claude Code 工具呼叫前（`PreToolUse`）以 7 個是非題評估並回傳 `allow` / `ask` / `deny`；`jev-guard` 攔截提示注入與危險動作 | - `tripwire`：66 情境×5 次重複中，危險呼叫 0/140 放行、安全誤擋 8.9%、p50 **215 ms**<br>- `jev-guard`：台灣直連約 **0.75 秒**，21 次 Gateway 校準呼叫 p50 約 **580 ms** | `tripwire` 案例與標籤由 Claude Code 產生、未經人工覆核且僅在 macOS 跑過 shadow mode；`jev-guard` 為 2026-09 小樣本連線自測 |
| **Agent 模型與深度路由** | [`0xNatoshi/jev-codex-router`](https://github.com/0xNatoshi/jev-codex-router#jev-codex-router) | 每輪對話用 Jev (`Choice`) 決定模型與思考深度（237 個歷史對話回合回測） | 回測成本較「全程使用最貴模型」**少約 60%** | **關鍵限制（不可當作已驗證經濟效益）**：作者於 README 明示此為**舊版路由政策（Legacy Policy）的歷史模擬，並非實際量測的 Codex 配額或帳單節省，也不證明現行政策成效** |
| **瀏覽器高速自動化** | [`browser-use/jev-ultrafast`](https://github.com/browser-use/jev-ultrafast) | 每步操作與點擊目標交由 Jev 決定，僅在需要打字時呼叫小模型（9/21 快照 13,061 星；11/22 查達 24,708 星） | Google 航班搜尋「蘇黎世飛倫敦」示範**耗時 7.1 秒** | 9 月上線初期係將頁面 DOM 狀態轉結構化文字交由 Jev `Choice` 選擇；數值為專案單一示範案例 |
| **分層多類別表單歸類** | [`kyotofin/tax-doc-classifier`](https://github.com/kyotofin/tax-doc-classifier#how-it-works) | 逐頁辨識美國報稅文件屬於 261 種官方表單中的哪一種（753 頁空白官方表單測試） | 753 頁測試**零分錯**（約 5% 把握度偏低轉複核）；每頁約 **$0.001 美元** | **兩階段分層實際原因（[`#how-it-works`](https://github.com/kyotofin/tax-doc-classifier#how-it-works)）**：第一層先在同一請求區分 7 種頁面類型與 230 個表單選項加 `not_in_this_list`；僅在命中 5 組企業／外國母表（`5471`、`8865`、`8933`、`1118`、`5713`）時才觸發第二次請求細分其 35 張附表。作者說明採用分層是因為**頁面上母表名稱比附表本身更明確**（非因每道 `Choice` 題目 255 個選項上限所致） |
| **影音字幕業配跳過** | [`valentynkit/jev-skip`](https://github.com/valentynkit/jev-skip) | 讀取 YouTube 字幕逐段判斷是否為業配並跳過（23 支影片對照 SponsorBlock 標註） | 抓出 SponsorBlock 標註秒數的 **77%**；每支約 **$0.0008 美元**；每小時誤跳約 **34 秒** | 作者註明數據係透過轉接服務測試，尚未以官方直連介面重測 |
| **即時語音操控** | [`moritzkremb/jev-voice-browser`](https://github.com/moritzkremb/jev-voice-browser) | 邊說話邊以 Jev 判斷操作意圖與點擊目標 | 每說一個字約花 **0.3 秒（300 ms）** 完成判斷 | 專案自述反應速度展示，未附標準化準確率基準 |

### 3.2 兩項評測基準專案之一手方法、樣本組成與裁判偏差校準

| 評測專案與一手出處 | 測試設計與樣本真實組成 | 一手 README 完整數據結果 | 方法論限制與架構啟發（嚴禁過度簡化） |
| :--- | :--- | :--- | :--- |
| **釣魚郵件基準：[`anisselbd/jev-phishing-bench`](https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026)** | **2,000 封平衡樣本**（含 **1,000 封釣魚郵件 + 1,000 封正常郵件**，拆為 A 組 1,000 封訓練／選門檻與 B 組 1,000 封保留集評估） | - **直接判斷（Direct Classification）**：`Jev 1.13` 準確率為 **62.6%** vs. `Claude Haiku 4.5` 為 **81.3%**<br>- **單一最佳 Jev 訊號（B 組）**：`sig_free_hosting >= 0.70` 達 **89.4%**（低於**非 AI 確定性正則規則的 91.8%**，McNemar $p = 0.0032$）<br>- **5 項訊號 + 邏輯迴歸訓練（B 組保留集）**：將 5 項 Jev 訊號於 A 組訓練邏輯迴歸（Logistic Regression）後，於 B 組保留集達 **95.0%**（AUROC 0.982；對照 Haiku 4.5 同款 5 訊號邏輯迴歸為 **93.2%**、AUROC 0.991，兩者統計無顯著差異 $p = 0.063$） | 1. **不可誤認為「只靠拆題就能直接得到 95.0%」**：單一拆解訊號（89.4%）甚至輸給純確定性正則規則（91.8%）；`95.0%` 必須依賴**5 項拆解訊號加上有標註資料（A 組）訓練出的邏輯迴歸模型**。<br>2. **核心工程啟發**：面對釣魚信等高風險安全任務，第一層應先跑零成本、高準確率（91.8%）的確定性正則／規則基線；若引入 System One 模型，必須將問題拆解為多項結構化子訊號並結合已標註樣本訓練下游聚合器。 |
| **中英搜尋重排序：[`zhuyansen/jev-search-rerank-eval`](https://github.com/zhuyansen/jev-search-rerank-eval)** | 164 個中英文查詢、共 **9,831 組模型產生的相關性標註**（見 [`#method`](https://github.com/zhuyansen/jev-search-rerank-eval#method)） | - **合併標籤（Pooled Labels）**：Jev 重排序相對 `bge-m3` 差值為正，但**信賴區間跨零（統計上未證明優於 `bge-m3`）**<br>- **排除 Jev 裁判標籤後**：Jev 單獨排序表現**顯著較差**<br>- **混合排序（Hybrid）**：在該資料集與比較系統中，結合語意搜尋與 Jev 分數取得最佳結果（見 [`#results`](https://github.com/zhuyansen/jev-search-rerank-eval#results)） | 1. **非人工評分（存在模型裁判偏差）**：9,831 組標註主要由 **Jev 與 Claude Haiku** 產生，少量分歧裁決亦由 **Claude** 執行，因此合併標籤中存在 Jev 自己當裁判的循環評分偏差（Circular Evaluation Bias）。<br>2. **適用範圍限制**：排除自評偏差後 Jev 單獨排序不如 `bge-m3`；而混合融合（Hybrid）最佳的結論**僅適用於該測試資料集與所比較的系統配置**。 |

---

## 4. 規格與部署建議分離：繁體中文環境與 System One 工程準則

為避免將「早期歷史版本說明」或「單一配置測試結果」誤寫為已確認的現行官方硬約束，本節嚴格區分**【已確認官方規格／待測狀態】**與**【本專案防禦性部署建議】**：

### 4.1 已確認官方規格 vs. 待實測項目

1. **多語言與繁體中文支援狀態（【待實測】）**：
   - 2026-09 初版社群貼文曾轉述「英文最準、中/日/韓精準度較低」（現行官方文件未見中日韓排序專頁）；而 [TypeSafe AI 官方更新紀錄](https://docs.typesafe.ai/changelog) 已確認 **`Jev 1.14` 改善了多語言支援（Improved multilingual support）**。
   - 因此，**不能宣稱現行 `Jev 1.14` 在繁體中文上存在官方硬性限制，亦不能在未測試前假設其與英文完全同分**；本機全繁體中文工作流對 `Jev 1.14` 與 `Gemini Decision 1` 的實際分類準確率，均定義為**【上線前須以本地繁中標註樣本實測驗證】**。
2. **模態與每題選項上限規格（【一手已確認】）**：
   - Jev 已於 `2026-10-14` 支援**實驗性圖片輸入**與 `Box` 原語（[官方圖片文件](https://docs.typesafe.ai/images)），而 `Gemini Decision 1` 原生支援 256K 多模態輸入。
   - Jev 與 Decisions API 的 `Choice` / `choice` **每一道題目的選項上限為 255 個**（[Choice 文件](https://docs.typesafe.ai/primitives/choice)，同一請求可包含多道題目）。實務上若存在母表與附表層級（如 [`kyotofin/tax-doc-classifier`](https://github.com/kyotofin/tax-doc-classifier#how-it-works) 因頁面上母表名稱較附表更明確，先以 230 項加 `not_in_this_list` 辨識母表、命中 5 組母表再發第二次請求細分 35 張附表），可採用兩階段分層請求架構。

### 4.2 本專案防禦性部署四項工程建議（Engineering Recommendations）

1. **確定性靜態防線優先，再輔以「多訊號拆解＋標註樣本訓練／校准」**：
   - 借鏡 [`anisselbd/jev-phishing-bench`](https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026) 的控制實驗：純確定性正則規則（`91.8%`）即已顯著優於直接裸判（`62.6%`）與單一拆解訊號（`89.4%`），而唯有將 **5 項拆解子訊號結合 A 組標註資料訓練邏輯迴歸**後，才在 B 組保留集達到 `95.0%`。
   - 因此在設計 Agent 安全閘門時：(a) 第一層必先執行確定性 Regex / AST / `Path.is_relative_to` 硬防線；(b) 第二層若調用 System One 模型，應拆解為具體子訊號（如 [`Sraavan/tripwire`](https://github.com/Sraavan/tripwire#readme) 的 7 道 `PreToolUse` 是非題），並以本地標註集校準權重與門檻，不可假設「只要拆題不經訓練／校準就能自動得到高準確率」。
2. **置信度雙門檻與灰區降級（Confidence Threshold & Gray-Zone Fallback）**：
   - 無論使用 Jev（Top-1 ECE `0.0494`）或 Gemini Decision 1（Top-1 ECE `0.0250`），回傳機率皆落在 `[0.01, 0.99]`。建議依官方指引先以本地標註樣本量測校準曲線，設定高信心放行門檻、低信心拒絕門檻，並將**中間低把握度灰區（如 [`kyotofin/tax-doc-classifier`](https://github.com/kyotofin/tax-doc-classifier) 中約 5% 的低信心樣本）強制降級至使用者確認或高階 System Two 模型複審**。
3. **工具選擇（When2Call）與百級工具檢索的職責分離**：
   - `Gemini Decision 1` 在 `When2Call` 基準為 `79.9%`（落後 `TypeSafe Jev 1.14` 的 `82.0%`）。在 Gemini `v1beta` Interactions API 環境下，低頻龐大工具集的按需 Schema 載入應交給平台原生 **Tool Retrieval（`tool_search` + `defer_loading: true`）**（詳見 [`docs/gemini-tool-retrieval-and-mcp-spec.md`](./gemini-tool-retrieval-and-mcp-spec.md)），而將 Decision 1 / Jev 用於「模型檔位路由」與「執行期狀態檢核」。

---

## 5. Agent 守門員與模型路由通用架構模板

結合 Jev 生態已開源之守門與路由專案（均附可追溯 GitHub `owner/repo`），提煉出可套用於本地 Coding Agent 的三段式攔截與路由流水線：

```text
[使用者任務 / Agent 迴圈]
   │
   ├─► 階段 A：前置路由與規則預篩 (Pre-Routing & Context Pruning)
   │     ├── 模型檔位路由 (0xNatoshi/jev-codex-router、gargpratyush/jev-router 模式)
   │     │     └─► 依任務特徵 Choice 選型（上線前須以現行配額實測，不直接套用舊政策模擬數字）
   │     └── 規則與 Skill 預篩 (EliaAlberti/jev-rules、Dicklesworthstone/skillranker、win4r/jev-skill-suggester)
   │           └─► 挑出當輪適用規則與技能，或搭配 Gemini Tool Retrieval (defer_loading: true)
   │
   ├─► 階段 B：工具執行前風險閘與進度守門 (PreToolUse Risk & Progress Gate)
   │     ├── 指令與工具呼叫前審核閘 (anpicasso/hermes-jev-approvals、Sraavan/tripwire、y0usaf/pi-jev、leepokai/jev-guard 模式)
   │     │     └─► 第 1 層：確定性路徑/金鑰黑名單硬攔截
   │     │     └─► 第 2 層：PreToolUse 多訊號拆解 Noul 評估，回傳 allow (自動放行) / ask (跳出人工審批) / deny (拒絕)
   │     └── 原地打轉與壓縮偵測 (AshutoshVJTI/progressgate、kunchenguid/compact-adviser、tamaratran/jev-pruner)
   │           └─► 連續無進展時觸發升級或請求介入；Bash 輸出過長時修剪或提醒壓縮
   │
   └─► 階段 C：收尾防提早收工閘門 (Anti-Premature-Exit / Belay Gate)
         └── 完工證據檢核 (valentynkit/jev-belay、noplan-inc/limpet 模式)
               └─► Agent 宣稱「做完了」時，掃描對話紀錄是否含實際驗證指令與綠燈 stdout
               └─► 無實測證據則攔截收尾回覆，強制退回補跑驗證
```

### 5.1 三大核心守門員實作規格與參考倉庫對照

| 守門員類型 | 可追溯開源參考倉庫 (`owner/repo`) | 判斷原語與訊號拆解設計 | 通過／攔截準則（結合本機硬閘門） |
| :--- | :--- | :--- | :--- |
| **1. 工具執行前風險與指令審核閘（`PreToolUse` & Command Approval Gate）** | [`anpicasso/hermes-jev-approvals`](https://github.com/anpicasso/hermes-jev-approvals)、[`Sraavan/tripwire`](https://github.com/Sraavan/tripwire#readme)、[`y0usaf/pi-jev`](https://github.com/y0usaf/pi-jev)、[`leepokai/jev-guard`](https://github.com/leepokai/jev-guard)、[`lgy1027/jevshield`](https://github.com/lgy1027/jevshield) | 原語：工具呼叫前（`PreToolUse`）批次多題 `Noul`（如 `tripwire` 以 7 道是非題檢查破壞性操作、憑證存取、外部傳輸與範圍越界）<br>輸入：待執行之 Tool Call / CLI 字串、工作目錄、目標路徑 | 1. **先過機械靜態防線**：若觸及專案目錄外讀寫、金鑰變數、破沙盒旗標，直接攔截（`deny`）。<br>2. **次過拆解訊號分類**：僅當所有安全子訊號皆高信心通過時回傳 `allow` 免打擾放行；存在不確定風險回傳 `ask` 交由客戶端審批；高危直接 `deny`。 |
| **2. 防提早收工閘（Anti-Premature-Exit Belay Gate）** | [`valentynkit/jev-belay`](https://github.com/valentynkit/jev-belay)、[`noplan-inc/limpet`](https://github.com/noplan-inc/limpet#readme) | 原語：停止事件（Stop Hook）拆解子題 `Noul`（`has_executed_test_command`、`test_exit_code_is_zero`、`output_matches_dod_claim`）<br>輸入：Agent 擬輸出的結案宣告 + 最近 N 輪 Tool Call 執行紀錄與 stdout 摘要 | 對齊全域規範「回報完成之前，要真的執行過檢查並貼出它的輸出」：<br>- 若只看結案文字極易被騙（`jev-belay` 實測僅看結案文字 AUROC 僅 0.777，結合對話紀錄達 0.976）；未見實際驗證腳本之退出碼 0 與 stdout 時，直接拒絕結案並要求補跑驗證。 |
| **3. 原地打轉與上下文修剪閘（Progress & Pruning Gate）** | [`AshutoshVJTI/progressgate`](https://github.com/AshutoshVJTI/progressgate)、[`kunchenguid/compact-adviser`](https://github.com/kunchenguid/compact-adviser)、[`tamaratran/jev-pruner`](https://github.com/tamaratran/jev-pruner) | 原語：`Choice`（`making_progress` / `repeating_same_error` / `oscillating_edits` / `needs_context_compaction`）<br>輸入：最近 N 輪錯誤訊息摘要、Git diff 統計與 Context 長度指標 | - 判定為 `repeating_same_error` 或 `oscillating_edits` 時，暫停自動重試並切換至強模型覆核或向使用者報告卡點。<br>- 判定為 `needs_context_compaction` 時，提醒執行 `/compact` 或修剪冗長終端輸出。 |
