# Gemini API Tool Retrieval 與 MCP 工具按需延遲載入架構規範

> 本文件收錄於 `docs/gemini-tool-retrieval-and-mcp-spec.md`，為任務 `T-20261122-04` 之產出成果。
> 核心目的：基於 [Gemini API Tool Retrieval 官方文件](https://aistudio.google.com/docs/tool-retrieval)、[官方快取文件](https://aistudio.google.com/docs/caching)（2026-11-22 查核）與 Will 保哥（黃保翕）之社群技術評析，解構預覽版 **`v1beta` Interactions API** 專屬的 **Tool Retrieval（`tool_search` + `defer_loading: true`）** 按需載入機制，釐清其支援的 6 款官方模型型號、`total_tool_use_tokens` 搜尋額外呼叫計費邊界（含靜態載入反而更便宜的反轉情境）與隱式快取（Implicit Caching）規範，並建立遠端 MCP 工具分層掛載準則。

---

## 0. 來源筆記與官方依據

- **來源筆記**：`notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md`
- **交叉參照**：
  - [`notes/2026-11-21-aiposthub-fastmcp-python-mcp-framework-eval.md`](../notes/2026-11-21-aiposthub-fastmcp-python-mcp-framework-eval.md)（FastMCP Python MCP 框架與工具治理）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](../notes/2026-11-20-gemini-decision-1-decisions-api-eval.md)（Gemini Decision 1 在 `When2Call` 79.9% 的邊界與前置路由分工）
  - [`docs/system-one-decision-model-landscape.md`](./system-one-decision-model-landscape.md)（System One 決策模型與 Tool Retrieval 的職責分工）
  - [`docs/model-burn-rate-routing-matrix.md`](./model-burn-rate-routing-matrix.md)（多模型選型、快取折扣與 Token 燃燒率控制）
- **官方文件查證網址（2026-11-22 核實）**：
  - [Gemini API Tool Retrieval 機制與教學](https://aistudio.google.com/docs/tool-retrieval)
  - [Tool Retrieval 支援模型清單 (`#supported-models`)](https://aistudio.google.com/docs/tool-retrieval#supported-models)
  - [Tool Retrieval 計費說明 (`#pricing`)](https://aistudio.google.com/docs/tool-retrieval#pricing)
  - [Tool Retrieval 限制說明 (`#limitations`)](https://aistudio.google.com/docs/tool-retrieval#limitations)
  - [Gemini API Caching 快取機制文件](https://aistudio.google.com/docs/caching)

---

## 1. 傳統靜態全量注入（Static Tool Loading）之設計取捨

在多工具 Agent 系統中，傳統做法是在每次 API 請求中將所有工具的完整 JSON Parameter Schema 一併傳入。當掛載的工具數量龐大且多數工具在單輪對話中不會被觸發時，容易面臨三個設計取捨（依貼文評析與官方設計背景）：

1. **未用工具 Schema 的重複輸入消耗**：
   - 每個工具的完整參數定義（含巢狀屬性、型別與說明）在每一輪請求都會計入 Input Tokens；當工具集很龐大但單輪僅使用極少數工具時，未觸發工具的 Schema 會持續佔用上下文與輸入成本。
2. **動態增減工具對前綴穩定度的影響**：
   - 若客戶端為節省 Token 而自行在每輪動態拼接不同的工具子集，會改變請求前綴，進而影響快取命中機會。
3. **候選工具過多的干擾風險**：
   - 當大量功能相近的工具 Schema 同時出現時，設計上較容易增加模型挑選工具與填入參數時的干擾（惟具體延遲與正確率差異仍取決於實際模型、工具集與查詢集，需以對照基準實測評估）。

---

## 2. Gemini API Tool Retrieval 運作機制與官方硬限制

Gemini API Tool Retrieval 將工具載入拆分為「待命區（`defer_loading: true`，初始僅提供工具名稱與描述）」與「伺服器端按需檢索（`tool_search`，命中時才載入完整 Schema）」兩個階段：

```text
【傳統靜態全量載入 (Static Loading，支援 generateContent / Interactions API)】
User Prompt ──► [ System Prompt + 全部工具的完整 JSON Parameter Schema ] ──► Gemini (單次模型呼叫)

【Gemini API Tool Retrieval (雙階按需載入，僅限預覽版 v1beta Interactions API)】
User Prompt ──► [ System Prompt + 待命區工具清單 (defer_loading: true，僅名稱與描述) ]
                                              │
                      (1. 若模型依對話語意判定需檢索待命工具)
                                              ▼ (觸發額外搜尋模型呼叫，計入 total_tool_use_tokens)
                       [ Google 伺服器端託管 tool_search 檢索 ]
                                              │
                      (2. 動態拉取命中工具之完整參數 Schema)
                                              ▼
                       [ 模型填入參數並回傳 Function Call ]
```

### 2.1 官方介面限制、支援型號、計費與快取規格表（2026-11-22 核實）

| 規格維度 | 官方一手規範與限制內容 | 工程實作注意事項 |
| :--- | :--- | :--- |
| **1. API 端點與預覽狀態** | **僅限預覽版（Preview）`v1beta` Interactions API 支援**；**傳統 `generateContent` 端點不支援**（[官方限制](https://aistudio.google.com/docs/tool-retrieval#limitations)） | 既有基於 `generateContent` 的應用程式無法只加 `tool_search` 就直接使用，必須先遷移至 `v1beta` Interactions API。 |
| **2. 官方支援模型清單（共 6 款）** | 依 [官方支援型號表](https://aistudio.google.com/docs/tool-retrieval#supported-models)（2026-11-22），僅明確列出 6 款型號：<br>- `gemini-4-carbon`<br>- `gemini-4-neon`<br>- `gemini-4-hydrogen`<br>- `gemini-4-argon`<br>- `gemini-3.8-flash`<br>- `gemini-3.6-flash` | **嚴禁以「Gemini 3.6 以上皆支援」做版本號萬用字元推論**；路由設定必須嚴格核對這 6 個明確型號字串。 |
| **3. 延遲載入、摘要截短與遠端 MCP** | 單一工具或整台**遠端 MCP Server** 的工具集合可設定 `defer_loading: true` 並搭配 `tool_search` 按需載入（[官方說明](https://aistudio.google.com/docs/tool-retrieval)）；依[計費規則](https://aistudio.google.com/docs/tool-retrieval#pricing)，初始上下文僅計入待命工具的 `name` 與 **`short_description`（若未設定 `short_description`，則僅取 `description` 的第一句話）** | 待命工具的名稱與單句摘要仍會隨每個待命工具累加進入初始請求（非恆定常數）；且根據[官方限制](https://aistudio.google.com/docs/tool-retrieval#limitations)，**已被檢索載入的工具會保留在該段對話後續回合中**。 |
| **4. 計費模型與成本反轉邊界** | 依 [官方計費說明](https://aistudio.google.com/docs/tool-retrieval#pricing)：<br>1. 無獨立的檢索服務費。<br>2. **但觸發 `tool_search` 會產生額外的模型呼叫**：搜尋時的完整對話上下文與被載入工具的 Schema 提示 Token 會計入 `total_tool_use_tokens`，並按該模型的 Input Token 費率計價。 | **並非「掛載工具越多就必然越省」**。官方明確提示：若工具集較小、或對話上下文很長且頻繁觸發新工具搜尋（導致長上下文在搜尋呼叫中被計費），**傳統靜態載入反而可能比 Tool Retrieval 更便宜**。 |
| **5. 快取機制（僅隱式快取）** | 依 [官方快取文件](https://aistudio.google.com/docs/caching?generate-content=true)，**Interactions API 不支援顯式快取（Explicit Caching），僅相容隱式快取（Implicit Caching）**（註：即使在 `generateContent` 下，顯式快取亦僅適用於支援它的 Gemini 3 / 2.5 模型，**Gemini 4 模型同樣僅支援隱式快取**） | 隱式快取需滿足最低 Token 長度門檻與自動命中條件；前綴穩定不代表保證命中或保證低延遲，實務上必須檢查 API 回應的 `usage.total_cached_tokens` 確認實際快取效益。 |

---

## 3. 多工具與 MCP Server 整合之損益評估與分層架構

結合官方計費模型（`total_tool_use_tokens` 額外呼叫成本）與端點限制，在 `v1beta` Interactions API 下整合大量工具與 MCP Server 時，應採用以下三層式分流規範：

```text
[Interactions API 工具箱冷熱分層架構]
  ├── Tier 0：高頻核心工具 (Static Loading / defer_loading: false)
  │     └── 條件：幾乎每輪對話都會用到的基礎工具
  │     └── 理由：直接靜態載入可省去 tool_search 的額外模型呼叫與長上下文重複計入 total_tool_use_tokens
  │
  ├── Tier 1：低頻大型工具集與遠端 MCP Server (Deferred Standby / defer_loading: true)
  │     └── 條件：工具數量龐大、Schema 複雜，但單輪觸發機率低的外掛或遠端 MCP 工具集
  │     └── 機制：標記 defer_loading: true 並啟用 tool_search，平時不載入完整 Schema
  │
  └── Tier 2：高危與外部未信任 MCP 隔離閘 (Zero-Trust Security Gate)
        └── 結合 Decisions API / Jev 前置審核與本地沙盒白名單，禁止未審批自動執行
```

### 3.1 開發與配置四大設計準則

1. **區分「工具使用頻率」與「新搜尋觸發頻率」（Cost Break-Even Check）**：
   - 依 [官方限制說明](https://aistudio.google.com/docs/tool-retrieval#limitations)，**一旦待命工具在對話中被檢索並載入，其完整 Schema 會保留在該段對話的後續回合中**，後續在同一對話重複呼叫該工具時，並不會再次觸發 `tool_search`。
   - 因此，**「工具使用頻率」不等於「新搜尋觸發頻率」**。在評估損益時，設靜態全量 Schema 為 $S_{\text{full}}$、待命短摘要為 $S_{\text{stub}}$、觸發新搜尋時的對話上下文為 $C$：每次**新觸發** `tool_search` 會產生約 $C + S_{\text{loaded}}$ 的 `total_tool_use_tokens`。對於幾乎每段新對話都會用到的核心工具，維持靜態載入（`defer_loading: false`）可省去首次搜尋的額外模型呼叫；而對於單次對話中極少動用的大型外掛或遠端 MCP 工具集，則設定 `defer_loading: true`，並依實際 `usage.total_tool_use_tokens` 數據評估成本。
2. **優化 `short_description` 與 `description` 首句（遵循官方截短規則）**：
   - 依 [官方計費與機制說明](https://aistudio.google.com/docs/tool-retrieval#pricing)，在 `defer_loading: true` 待命階段，系統初始僅計入並檢索工具的 `name` 與 **`short_description`；若未提供 `short_description`，則僅截取 `description` 的第一句話**。因此務必明確填寫 `short_description`（或將「核心動作 + 領域實體 + 適用條件」濃縮在 `description` 的第一句內），避免重要觸發關鍵詞寫在第二句以後而在待命階段被截斷漏檢。
3. **監控 `total_tool_use_tokens` 與 `total_cached_tokens` 遙測指標**：
   - 在生產環境或基準測試中，不可僅憑理論推算宣稱省費或加速；必須在日誌中實際記錄 API 回應的 `usage.total_tool_use_tokens`（評估搜尋呼叫開銷）與 `usage.total_cached_tokens`（確認隱式快取是否真正命中）。
4. **MCP 安全零信任防線不因按需載入而豁免**：
   - `tool_search` 僅負責按需載入 Schema，**不代表該 MCP 工具已獲安全授權**。所有第三方 MCP Server 在接入前仍須通過本機靜態安全檢驗（`verify_agent_skill_pack_safety.py --pack`），且涉及外部寫入或高危操作之呼叫仍須遵守沙盒邊界與審批閘門。
