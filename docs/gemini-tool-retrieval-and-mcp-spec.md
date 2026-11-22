# Gemini API Tool Retrieval 與 MCP 百級工具按需載入架構規範

> 本文件收錄於 `docs/gemini-tool-retrieval-and-mcp-spec.md`，為任務 `T-20261122-04` 之產出成果。
> 核心目的：梳理傳統 Tool Calling 全量傳遞 Schema 導致的 Token 膨脹、延遲拉長與注意力分散瓶頸，解構 Google AI Studio 針對 Gemini 3.6+ 與 Gemini 4 全系列推出的 **Gemini API Tool Retrieval（`tool_search` + `defer_loading: true`）** 按需動態載入機制，並制定其與 Model Context Protocol (MCP) 及 Prefix Caching 協同的多工具 Agent 整合規範。

---

## 0. 來源筆記與交叉參照

- [`notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md`](../notes/2026-11-22-will-gemini-api-tool-retrieval-on-demand-schema-eval.md)（Will 保哥評釋 Gemini API Tool Retrieval、待命區設計與 Prefix Caching 相容性）
- [`notes/2026-11-21-aiposthub-fastmcp-python-mcp-framework-eval.md`](../notes/2026-11-21-aiposthub-fastmcp-python-mcp-framework-eval.md)（FastMCP Python MCP 框架與工具治理）
- [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](../notes/2026-11-20-gemini-decision-1-decisions-api-eval.md)（Gemini Decision 1 在 `When2Call` 79.9% 的邊界與前置路由分工）
- [`docs/system-one-decision-model-landscape.md`](./system-one-decision-model-landscape.md)（System One 決策模型與 Tool Retrieval 的職責分工）
- [`docs/model-burn-rate-routing-matrix.md`](./model-burn-rate-routing-matrix.md)（多模型選型、Prefix Caching 折扣與 Token 燃燒率控制）

---

## 1. 傳統 Tool Calling 全量注入之三大工程瓶頸（100+ Tools Curse）

在現代 Coding Agent 與企業自動化系統（如 Antigravity、Claude Code、Codex）中，當同時掛載多個本地工具與外部 MCP Server（總工具數達 50～200 個以上）時，傳統「每次請求全量傳遞完整 Function Parameter Schema」的做法會觸發三大瓶頸：

1. **Context Token 線性暴增與配額浪費**：
   - 每個包含詳細型別、巢狀屬性、枚舉值與說明的 JSON Schema 平均佔用 `200～800 Tokens`。
   - 掛載 100 個工具即在每輪對話固定消耗 `20,000～80,000 Input Tokens`，即便該輪對話僅是簡單問答或只需調用 1 個工具，其餘 99 個未用工具的 Schema 仍不斷重複計費並擠壓有效工作上下文。
2. **首字延遲（TTFT）顯著惡化**：
   - 龐大的工具宣告區塊增加預填充（Prefill）計算量；一旦某個動態 MCP Server 連線狀態改變或工具列表增減，還可能破壞靜態前綴結構，導致每次請求重新計算數萬 Token。
3. **候選工具過多引發注意力稀釋與挑錯幻覺（Tool Hallucination）**：
   - 當上百個高度相似的工具 Schema（例如多個資料庫查詢或不同雲端服務的 CRUD 端點）同時塞入 Context 時，模型注意力被長篇 JSON 結構分散，極易發生「選錯同名近似工具」或「混用其他工具的參數欄位」。

---

## 2. Gemini API Tool Retrieval 雙階動態檢索機制

Gemini API Tool Retrieval（支援 **Gemini 3.6 以上版本及全部 Gemini 4 系列模型**，依 Google AI Studio 官方公告與 Will 保哥技術評析）將工具宣告拆解為「輕量待命區（Standby Pool）」與「伺服器端按需即時載入（Just-in-Time Schema Loading）」兩個階段：

```text
【傳統全量注入模式 (All-in-Context)】
User Prompt ──► [ System Prompt + 100 個工具的完整 JSON Parameter Schema (20K~80K Tokens) ] ──► LLM
                 └── 痛點：未用到的 99 個工具 Schema 每輪照算 Token、拉長延遲、稀釋注意力

【Gemini API Tool Retrieval (雙階按需載入模式)】
User Prompt ──► [ System Prompt + 待命區工具清單 (defer_loading: true，僅名稱與一行摘要 ~1K Tokens) ]
                                              │
                      (1. 模型依對話語意判定需使用特定工具類群)
                                              ▼
                       [ Google 伺服器端託管 tool_search 檢索 ]
                                              │
                      (2. 同一輪請求內部動態拉取目標工具之完整參數 Schema)
                                              ▼
                       [ 模型填入完整參數並回傳 Function Call ]
```

### 2.1 核心配置原語與計費特性

| 核心機制 | 參數／介面規格 | 運作行為與工程效益 |
| :--- | :--- | :--- |
| **延遲載入標記** | `defer_loading: true`（出處：[Google AI Studio 官方 X 公告](https://x.com/GoogleAIStudio/status/2123489911684866251)） | 將工具或整台 MCP Server 的工具集放入待命區（Standby Pool）。初始 Context 中模型僅接收工具的 `name` 與簡短 `description`（每工具僅約 `10～30 Tokens`），不載入龐大的 `parameters` JSON Schema。 |
| **託管式工具搜尋** | `tool_search` | 開發者**無需自建本地向量資料庫（Vector DB）或 Embedding 檢索微服務**。當對話語意需要呼叫工具時，由 Google 伺服器端在同一次 API 請求內部自動執行 `tool_search`，精準拉取命中的少數工具完整 Schema。 |
| **Prefix Caching 相容性** | 原生相容 Gemini Context / Prefix Caching | 工具搜尋與動態 Schema 注入由伺服器端在推論鏈路中處理，**不會破壞對話歷史與 System Prompt 的靜態前綴快取（Prefix Cache）**，長對話多輪調用依然享有快取折扣與低延遲。 |
| **零加價計費架構** | 無額外檢索服務費 | 完全沿用原本模型的 Input / Output Token 單價計費。所有在待命區未被觸發載入的完整參數 Schema 均不計入 Token，**掛載工具數量越多，相對傳統全量注入節省的 Token 比例越高**。 |

### 2.2 傳統全量模式 vs. Tool Retrieval 量化結構對比

| 比較維度 | 傳統全量宣告模式 (All-in-Context) | Gemini API Tool Retrieval (`tool_search` + `defer_loading`) |
| :--- | :--- | :--- |
| **100 個工具之初始 Context 負擔** | 約 `20,000～80,000 Tokens`（全量 JSON Schema） | 約 `1,000～3,000 Tokens`（僅工具名稱與一行功能描述，節省 **85%～95%** 工具前綴 Token）【推算】 |
| **單輪無工具對話成本** | 仍須支付全部 100 個工具的完整 Schema Token | 僅支付輕量名稱摘要 Token，零冗余 Schema 消耗 |
| **單輪調用 1 個工具之消耗** | 100 個完整 Schema Token | 輕量清單 + **僅被命中之 1～K 個工具的完整 Schema Token** |
| **基礎設施維運成本** | 無額外組件，但受 Context 視窗與成本硬上限卡死 | **零自建檢索基建**（由 Google 伺服器端全託管） |
| **百級工具挑選精準度** | 易受 100 組相似參數干擾而挑錯工具或填錯欄位 | 先由語意檢索收斂至極少數候選工具再展開 Schema，降低注意力稀釋 |

---

## 3. 與 Model Context Protocol (MCP) 整合之最佳實踐架構

MCP 解決了「跨平台工具通訊協定標準」，卻也導致開發者極易一次掛載多台大型 MCP Server（如 GitHub、檔案系統、資料庫、瀏覽器、科學分析等數十至上百個端點），瞬間塞爆 Context。結合 Tool Retrieval 與本機 Agent 治理規範，建立以下三層式 MCP 工具掛載標準：

```text
[Agent 工具箱分層治理架構]
  ├── Tier 0：核心高頻常駐工具 (Eager Loading / defer_loading: false，建議 <= 10 個)
  │     └── 如：read_file, edit_file, run_command, ask_question
  │     └── 理由：幾乎每輪必用，直接放入靜態 Prefix Cache 省去檢索步驟
  │
  ├── Tier 1：領域專精與大型 MCP Server 工具集 (Deferred Standby / defer_loading: true，10 ~ 200+ 個)
  │     └── 如：生物結構檢視器、資料庫深度查詢、第三方 SaaS API、低頻管理腳本
  │     └── 機制：整批標記 defer_loading: true 並啟用 tool_search，按需動態載入完整 Schema
  │
  └── Tier 2：高危與外部未信任 MCP 隔離閘 (Zero-Trust Security Gate)
        └── 結合 Decisions API / Jev 前置審核與本地沙盒白名單，禁止未審批自動執行
```

### 3.1 開發與配置四大設計準則

1. **冷熱工具分層（Eager vs. Deferred Tiering）**：
   - **熱工具（Tier 0，預設載入）**：使用率超過 50% 的基礎工具（如檔案讀寫、終端機執行）保持常駐，並固定排列於 System Prompt 最前端以最大化 Prefix Caching 命中率。
   - **溫／冷工具（Tier 1，延遲載入）**：所有外掛 MCP Server 與特定領域工具一律設定 `defer_loading: true` 並交由 `tool_search` 按需檢索（與 Antigravity 本機 MCP 架構中的 `Eager` vs. `Lazy` 工具分層哲學完全一致）。
2. **優化待命區工具名稱與一行摘要（Retrieval-Friendly Naming & Description）**：
   - 由於在 `defer_loading: true` 待命階段，伺服器端 `tool_search` 與模型僅能根據工具的 `name` 與 `description` 判斷是否需要拉取完整 Schema，**工具描述的第一句話必須精準包含「動詞 + 領域實體 + 觸發條件 / 排除條件」**（例如：明確寫出「查詢 ChEMBL 生物活性與 IC50 數據；若僅有蛋白質序列則勿使用」），避免使用含糊的通用名稱（如 `process_data`、`run_task`）。
3. **與 Decisions API（`Gemini Decision 1`）的職責邊界劃分**：
   - 根據 [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](../notes/2026-11-20-gemini-decision-1-decisions-api-eval.md)，`Gemini Decision 1` 在 `When2Call` 基準的正確率為 `79.9%`。因此**切勿自行用 Decision 1 硬刻百級工具的 Schema 挑選器**；百級工具的按需載入應直接交給 Gemini API 原生 **Tool Retrieval（`tool_search`）**，而將 Decision 1 用於「對話是否需升級強模型（Fast/Slow Path）」或「MCP 呼叫前的對抗性安全檢測」。
4. **MCP 安全零信任防線不因按需載入而豁免**：
   - `tool_search` 僅負責按需載入 Schema 與生成 Function Call 建議，**不代表該 MCP 工具已獲安全授權**。所有第三方 MCP Server 在接入前仍須通過本機靜態安全檢驗（`verify_agent_skill_pack_safety.py --pack`），且涉及外部寫入、網路傳送或跨目錄操作之工具呼叫，仍必須遵守沙盒邊界與客戶端審批閘門。
