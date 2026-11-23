# Google AI Pro 八大工具分工、點數路由與 Antigravity 權限安全規範

> 本文件收錄於 `docs/google-ai-pro-ecosystem-and-credit-routing.md`，為任務 `T-20261122-03` 之產出成果。
> 核心目的：系統性梳理 Google AI Pro 訂閱體系下 8 大工具的能力定位與分工邊界，嚴格區分 **Google Flow credits（僅限 Flow 使用）** 與 **購買／促銷取得的 AI credits（跨產品共用）** 之計費與超額開關機制，並對照 Google Antigravity 官方權限文件訂定桌面端 Agent 的安全操作與權限預設規則。

---

## 0. 來源筆記與官方依據

- **來源筆記**：`notes/2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval.md`
- **交叉參照**：
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](../notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Antigravity 與 Gemini 4 Neon 配置）
  - `notes/2026-11-21-infoq-gemini4-neon-antigravity-swe-sweep-harness-eval.md`（Gemini 4 Neon 與 Antigravity SWE-sweep 評測）
  - [`docs/model-burn-rate-routing-matrix.md`](./model-burn-rate-routing-matrix.md)（多模型選型與配額燃燒率矩陣）
- **官方文件查證網址（2026-11-23 核實）**：
  - [Google AI Pro 官方訂閱權益說明](https://support.google.com/googleone/answer/14534406?hl=en)
  - [Google Flow 點數官方說明](https://support.google.com/flow/answer/16526234?hl=en)
  - [Google One AI 點數官方說明](https://support.google.com/googleone/answer/16287445)
  - [Gemini Notebook 用量與動態額度說明](https://support.google.com/gemininotebook/answer/17670842?hl=en)
  - [Gemini Notebook 方案結構限制](https://support.google.com/gemininotebook/answer/16213268?hl=en)
  - [Gemini Notebook 回答準確性與問題回報說明](https://support.google.com/gemininotebook/answer/16179536?hl=en)
  - [Google Antigravity 方案與配額說明](https://antigravity.google/docs/plans)
  - [Google Antigravity 設定文件 (`Settings > Models`)](https://antigravity.google/docs/settings)
  - [Google Antigravity 權限模式文件 (`Permissions` 新版預設)](https://antigravity.google/docs/permissions)
  - [Google Antigravity 舊版與企業代理設定 (`Agent Settings`)](https://antigravity.google/docs/agent-settings)
  - [Gemini API 限流（Rate Limits）文件](https://aistudio.google.com/docs/rate-limits)
  - [Gemini API 價格頁](https://aistudio.google.com/docs/pricing)

---

## 1. Google AI Pro 八大工具能力定位與分工矩陣

為避免「買了 Google AI Pro 卻只用 Gemini 網頁版純聊天，或把重度多檔開發塞進網頁聊天導致斷頭」，將 8 大工具按職責與額度機制分流如下：

| 類別 | 工具名稱 | 核心適用場景與交付產物 | 操作門檻 | 額度與計費機制（依官方文件核實） |
| :--- | :--- | :--- | :---: | :--- |
| **1. 聊天與通用助理** | **Gemini App** | 日常問答、發想、多語翻譯、文字改寫、單段程式碼諮詢、掛載 `SKILL.md` | ★☆☆ | 依所選模型與功能享 Pro 基本使用上限；用盡後符合資格者可動用**另購之 AI credits** |
| **2. 即時檢索與比價** | **Google 搜尋 AI 模式** | 即時網路資訊查證、跨電商規格與價格比對表、圖文多模態搜尋 | ★☆☆ | 依搜尋次數與進階模型配額計算 |
| **3. 可溯源知識庫** | **Gemini Notebook**（原 NotebookLM） | 匯入多份 PDF、研究報告、網頁進行可溯源 Grounding 對照摘要與語音導讀（[官方說明](https://support.google.com/gemininotebook/answer/16179536?hl=en)提醒仍可能出現不正確回答，非零幻覺保證） | ★★☆ | 分為**結構限制**（筆記本總數、單本來源文件數上限）與**共用動態運算額度**（依提示複雜度、模型、音訊／問答功能與對話長度計算，每 5 小時更新並設每週上限） |
| **4. 辦公文件協作** | **Gmail / Google 文件內建 Gemini** | 十餘封長串郵件三欄摘要（已確認／待解／需回覆）、文件段落精簡改寫 | ★★☆ | 依**個人 Google AI 方案（如 Google AI Pro）**或 Google Workspace 帳號方案、帳號資格、語言與地區限制開放（[官方權益](https://support.google.com/googleone/answer/14534406?hl=en)） |
| **5. 多模態影片生成** | **Google Flow** | 文字或參考圖片生成短片、運鏡視角控制、行銷與社群影音素材製作 | ★★☆ | 先扣 **Google Flow credits**（每日 50 點 + Pro 每月 1,000 點）；不足時才可另用**購買的 AI credits** |
| **6. 桌面端程式代理** | **Google Antigravity** | 本地儲存庫多檔案讀寫、網站與應用程式建置、終端機測試與自動化工作流 | ★★★ | 先用 **Pro 基本配額**；基本配額用盡後，依 `Settings > Models` 開關決定是否扣**購買的 AI credits** |
| **7. 開發者原型與 API** | **Google AI Studio** | 模型參數調校、System Prompt 原型驗證、Decisions API / Tool Retrieval 測試 | ★★★ | 分為 **AI Studio 訂閱權益**（AI Pro 提高 Studio 內 `Gemini 4 Neon`、`Nano Banana Pro` 使用上限，見[官方權益](https://support.google.com/googleone/answer/14534406?hl=en)）與 **Gemini API 專案額度／計費**（API 限流 RPM / TPM / RPD 按 **Google Cloud 專案**計算；付費層按每百萬 Token 獨立計價） |
| **8. 雲端算力與資料科學** | **Google Colab** | 雲端 Jupyter Notebook、Python 資料清洗、呼叫 GPU / TPU 執行 ML 訓練與推論 | ★★★ | 依運算單元（Compute Units）餘額與單次工作階段連線時長限制 |

---

## 2. 兩種點數制度嚴格區分與超額防呆路由

**核心戒律：訂閱附贈的「Google Flow credits」與另外購買／促銷取得的「AI credits」是兩種截然不同的點數，嚴禁混為一談。**

```text
[Google AI Pro 點數與配額雙軌架構]
  │
  ├─► 軌道 A：Google Flow credits（訂閱內含，Flow 專用）
  │     ├── 每日免費配額：50 點 / 日（所有使用者皆有，當日未用完不累計）
  │     ├── Pro 月度配額：1,000 點 / 月（Pro 訂戶專屬，當月未用完不遞延至下月）
  │     └── 適用範圍限制：僅限 Google Flow 內適用功能（含影片、圖片及 Flow Agent 生成）使用，【不可】拿去扣 Antigravity 或 Gemini App
  │
  └─► 軌道 B：AI credits（另外購買或一次性促銷取得，跨產品共用）
        ├── 適用範圍：可跨產品用於 Gemini App、Google Flow（當 Flow 點數用盡後）、Google Antigravity（當基本配額用盡後）
        ├── 到期規則：依購買或促銷發放時的條款到期（官方未定單一固定天數）
        ├── 餘額查詢：[Google One 點數頁面](https://support.google.com/googleone/answer/16287445)（僅供查餘額與消耗紀錄，無超額開關）
        └── Antigravity 超額扣點開關：位於 Antigravity 內部 `Settings > Models`（toggle AI credit overages）
```

### 2.1 點數與 API 配額四大防呆規則

1. **Flow 點數不可跨轉 Antigravity**：
   - 依 [Flow 點數官方說明](https://support.google.com/flow/answer/16526234?hl=en) 與 [Antigravity 方案說明](https://antigravity.google/docs/plans)，Pro 訂閱每月附贈的 1,000 點與每日 50 點均為 **Google Flow credits**，只能用於 Flow。Antigravity 超額消耗的是使用者另外購買或促銷取得的通用 **AI credits**。
2. **不累計、不遞延原則**：
   - Flow 每日 50 點隔日歸零重置，每月 1,000 點跨月不遞延。若有影片素材產出需求，應優先於當日／當月週期內使用完畢。
3. **Antigravity 超額點數保護開關（`Settings > Models`）**：
   - 依 [Antigravity 設定文件](https://antigravity.google/docs/settings)，控制 Antigravity 在基本配額用盡後是否自動扣減購買的 AI credits，其開關位於 **Antigravity 應用程式內的 `Settings > Models`（切换 `AI credit overages`）**，而非在 Google One 設定。
   - **操作規範**：在執行長時程自動化任務、多子代理並行（Swarm / Subagents）或大型重構迴圈前，**必須先檢查 `Settings > Models` 中的超額扣點開關狀態**，防止背景迴圈意外燒光購買的 AI 點數。
4. **AI Studio / Gemini API 限流按「Google Cloud 專案」計算，而非按 API Key**：
   - 依 [Gemini API 限流文件](https://aistudio.google.com/docs/rate-limits) 與 [價格頁](https://aistudio.google.com/docs/pricing)，RPM（每分鐘請求數）、TPM（每分鐘 Token 數）、RPD（每日請求數）等配額上限是綁定在 **Google Cloud Project（專案層級）**，同一專案下建立多把 API Key 會共用同一個配額池，無法透過「多開幾把 Key」突破限流；且 API 付費層係依實際 Input / Output Tokens 計費，不屬於 Google AI Pro 個人訂閱範圍。

---

## 3. Google Antigravity 權限設定與安全邊界規則

《數位時代》報導建議使用者「建立專用資料夾（如日本旅遊網站）並在 New Project 載入以降低誤改風險」。**從資安與工程角度，建立專用資料夾只是操作習慣建議，本身並非安全邊界**——Agent 實際能讀寫哪些路徑、能否直接執行高危指令，完全取決於 Antigravity 的**權限模式（Permission Presets）**與跨工作區設定。

### 3.1 官方四種權限預設模式對照表

依 [Antigravity 官方權限文件](https://antigravity.google/docs/permissions)，系統提供四種權限預設（Presets）：

| 權限預設模式 | 檔案系統存取範圍 | 終端機指令與動作核准行為 | 本機安全治理定位與適用規範 |
| :--- | :--- | :--- | :--- |
| **1. Request Review** | 允許當前工作區（Workspace）內檔案讀寫，工作區外存取須核准 | **每次終端機指令執行與工作區外存取前皆跳出人工確認提示** | 適合首次接觸未知外部儲存庫或高敏感系統設定檢視 |
| **2. Default** | **當前工作區 + 系統暫存／腦區目錄（Scratch / Brain）** | 常規沙盒內工作區操作可執行，高風險或沙盒外動作需人工核准 | **日常開發標準預設**：兼顧沙盒隔離與人工把關 |
| **3. Auto** | **當前工作區 + 系統暫存／腦區目錄（Scratch / Brain）** | 在工作區與沙盒邊界內提高自動執行比例，跨邊界仍受保護 | 適合在已建立 Git 版控之單一專案目錄（`C:\GitHub\<repo>`）內進行常規開發 |
| **4. Turbo** | **整個本機檔案系統（Full Filesystem Access）** | **終端機指令與外部存取不受限自動執行（無人工審批煞車）** | **高危模式（嚴格管制）**：等同解除沙盒與工作區邊界，專用資料夾在此模式下完全失去隔離作用 |

### 3.2 本機 Antigravity 四條強制安全規則（區分新版預設與舊版／企業設定體系）

1. **嚴禁將「專用資料夾」當作 Turbo 模式下的安全防線**：
   - 要讓工作區資料夾具備真正的安全隔離邊界，應依客戶端所處的設定體系分別檢查：
     - **新版權限預設體系（[Permissions](https://antigravity.google/docs/permissions)）**：(a) 權限預設**不得設為 `Turbo`**（應維持 `Default`、`Auto` 或 `Request Review`）；(b) 檢查明確的允許／詢問／拒絕（Allow / Ask / Deny）規則與沙盒設定；(c) 當跳出沙盒外執行或跨區存取核准提示（Approval Prompt）時，切勿隨意擴大授權範圍。
     - **舊版與企業帳號設定體系（[Agent Settings](https://antigravity.google/docs/agent-settings)）**：官方將 `Non-Workspace Access` 開關歸於舊版設定並由企業帳號沿用；在該體系下**必須確認 `Non-Workspace Access` 保持關閉（預設為關閉）**，禁止代理未經詢問漫遊至工作區外讀取 SSH 金鑰、憑證或瀏覽器資料。
2. **禁止啟用 `Turbo` 模式的絕對紅線情境**：
   - 凡處理外部開源專案評估、讀取社群貼文／未信任網頁、測試第三方 `SKILL.md` 或 MCP Server 時，**一律禁止使用 `Turbo` 模式**（防範 Indirect Prompt Injection 順著無審批終端機直穿本機系統）。
3. **先計畫再實作（Plan Before Execution）**：
   - 針對跨檔案修改、架構重構或刪除操作，即使客戶端處於 `Auto` 模式，Prompt 層仍須維持「先調研、提出變更計畫與影響範圍，必要時向使用者確認後再寫入」的工程紀律，不可在提示詞中強行注入「禁止停頓確認」而導致雙重煞車失效。
4. **統一專案根目錄與版控保護**：
   - 所有正式專案一律置於 `C:\GitHub\<repo>` 並確保 Git 工作樹乾淨；不將一般私人文書資料夾、桌面（Desktop）或整個家目錄掛載為 Antigravity 工作區。
