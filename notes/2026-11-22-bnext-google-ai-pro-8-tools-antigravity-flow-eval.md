---
id: "2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval"
title: "數位時代評析：Google AI Pro 八大工具全景實測——Antigravity 電腦檔案代理、Flow 影片生成與跨產品 AI 點數制"
source_url: "https://www.bnext.com.tw/article/93098/google-ai-pro-8-tools-features-tutorial"
source_platform: "bnext.com.tw (數位時代)"
author: "蘇柔瑋"
analyzed_at: "2026-11-22"
analyzed_by: "antigravity"
written_by: "legacy/unknown@pre-review; claude/opus-5.5@e7344aab-d6b6-4fcb-961e-1304a5af6031; antigravity/gemini-4-argon@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; codex/gpt-6.1-sol@01a20b8d-8bc2-7191-a7cc-7a104940ed47; codex/gpt-6.1-sol@01a21248-1b6a-7223-8678-a9a474c169fa"
revised_at: "2026-11-25"
source_review: full
source_images: 8
source_replies: 0
source_reviewed_at: "2026-11-22"
status: pending
cluster: 3
cluster_role: "Google八工具"
short_title: "GoogleAIPro八工具評估"
tags:
  - google-ai-pro
  - gemini
  - antigravity
  - google-flow
  - gemini-notebook
  - ai-credits
---

# 數位時代評析：Google AI Pro 八大工具全景實測——Antigravity 電腦檔案代理、Flow 影片生成與跨產品 AI 點數制

- **來源文章**：[買了Google AI Pro只會用Gemini聊天？這8種隱藏AI工具，幫你把訂閱費用好用滿（數位時代 BusinessNext）](https://www.bnext.com.tw/article/93098/google-ai-pro-8-tools-features-tutorial)
- **發布平台 / 作者**：`bnext.com.tw` / `蘇柔瑋`（發布於 `2026-11-18`）
- **分析日期**：`2026-11-22`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](./2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Gemini 4 Neon 與 Antigravity 提示詞架構）
  - [`notes/2026-11-21-infoq-gemini4-neon-antigravity-swe-sweep-harness-eval.md`](./2026-11-21-infoq-gemini4-neon-antigravity-swe-sweep-harness-eval.md)（Gemini 4 Neon 與 Antigravity SWE-Sweep Harness）
  - [`notes/2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval.md`](./2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval.md)（Gemini Skills 官方配置指南與錨定語法）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（跨模型與點數消耗矩陣）

---

## 1. 原始資料盤點（正文解構與 8 大工具分工矩陣）

報導針對眾多使用者「訂閱 Google AI Pro 僅當作純文字聊天工具」之痛點，系統性盤點 Google AI Pro 訂閱體系所涵蓋之 8 大工具能力光譜，涵蓋搜尋、研究、辦公、多模態影音創作與程式代理：

操作難度星等為筆記作者主觀評估，非官方評級或獨立實測，也未確認為報導評分；不代表功能品質或實測效能。[Google AI Pro 官方權益](https://support.google.com/googleone/answer/14534406?hl=en)僅作權益與功能查證依據，不作星等依據。

| 工具名稱 | 核心場景與功能特徵 | 操作難度 | 額度計算機制 |
| :--- | :--- | :---: | :--- |
| **Gemini App** | 日常對話、創意發想、多語言翻譯、文字潤飾與程式碼諮詢 | ★☆☆ | 依選用模型與進階功能設定基本使用上限；符合資格者可另購 AI 點數增加用量（與 Flow、Antigravity 共用同一種購買點數） |
| **Google 搜尋 AI 模式** | 即時網路資訊查詢、規格與價格跨店比價、多模態圖文搜尋 | ★☆☆ | 依搜尋次數與模型配額計算，進階模型提供較高上限 |
| **Gemini Notebook**（原 NotebookLM） | 匯入 PDF、研究報告與網站，進行可溯源 Grounding 問答與語音摘要 | ★★☆ | 分為**結構上限**（筆記本數量、單本來源文件數）與**共用動態運算額度**（依提示複雜度、模型、音訊／問答功能與對話長度計算，每 5 小時更新，另有每週上限） |
| **Gmail / Google 文件內建 Gemini** | 跨郵件長串摘要、內聯草擬回覆、段落潤飾與 PTCF 提示框架 | ★★☆ | 依**個人 Google AI 方案（如 Google AI Pro）**或 Google Workspace 帳號方案、帳號資格、語言與地區限制而異（[官方權益說明](https://support.google.com/googleone/answer/14534406?hl=en)） |
| **Google Antigravity** | 桌面端 Agent 開發工具、授權本地資料夾多檔案修改、網站建置與 Vibe Coding | ★★★ | **Pro 基本配額**；用完後可自選是否消耗**購買或一次性促銷取得的 AI 點數**（開關在 Antigravity `Settings > Models`） |
| **Google Flow** | 文字描述或參考圖片生成影片、運鏡視角控制、社群短影音素材製作 | ★★☆ | **Google Flow credits**：每日 50 點（所有使用者，不累計）+ **Pro 每月另加 1,000 點**（不遞延）；不夠時可另用購買的 AI 點數 |
| **Google AI Studio** | 開發者模型原型驗證、Prompt 調校、Gemini API Key 配額調用 | ★★★ | 分為**AI Studio 訂閱權益**（AI Pro 可提高 AI Studio 中 `Gemini 4 Neon`、`Nano Banana Pro` 的使用上限，見[官方權益](https://support.google.com/googleone/answer/14534406?hl=en)）與 **Gemini API 專案額度／計費**（API 的 RPM／TPM／RPD 限流按 Google Cloud 專案計算而非按 API Key；API 獨立計費，依模型與功能按 token、圖片或其他單位計價） |
| **Google Colab** | 雲端 Jupyter/Python 環境、GPU/TPU 算力調用、資料分析與 ML 運算 | ★★★ | 依運算單元（Compute Units）與連線工作階段時長限制 |

### 8 張插圖實測解析（報導案例，二手轉述，未獨立實測）
1. **圖 1（Google 搜尋 AI 模式）**：展示小家庭掃地機器人多維度比價與規格表輸出，並標註即時商家來源。
2. **圖 2（Gemini Notebook）**：展示匯入 3 份研究報告後，針對共同結論、數據差異與趨勢之對照摘要。
3. **圖 3（Gmail 內建 Gemini）**：展示針對十餘封來回郵件長串，快速萃取「已確認事項、待解問題、需回覆內容」之三欄摘要。
4. **圖 4（Google 文件內建 Gemini）**：展示針對特定段落進行「精簡、自然、不增添新事實」之重寫建議。
5. **圖 5（Antigravity 建立專案）**：展示桌面應用介面中，透過「New Project -> Add Folder」掛載本機資料夾（如日本旅遊網站專案）。
6. **圖 6（Antigravity 提示詞與計畫）**：展示 Agent 接收「建立行程網站」提示詞後，主動輸出逐步變更計畫並要求使用者確認之互動流程。
7. **圖 7（Google Flow 運鏡介面）**：展示影片生成介面中的文字描述輸入框、運鏡速度與景深參數。
8. **圖 8（Google Flow 生成成果）**：展示產出之陽光灑落咖啡廳寫實短影片。

---

## 2. 額度機制解構（獨立配額 vs 跨產品 AI 點數制）

報導最關鍵之架構資訊在於釐清 Google AI Pro 的**「混合額度結算機制」**，破除使用者對「全共用」或「全獨立」之誤解：

```
[Google AI Pro 訂閱體系]
  ├── 【各產品基本用量】（各自計算、各自重置）
  │     ├── Gemini App（依模型與功能的使用上限）
  │     ├── Google 搜尋 AI 模式
  │     ├── Gemini Notebook（結構上限：筆記本與來源數；共用運算額度：每 5 小時更新＋每週上限）
  │     ├── Gmail / Google 文件內建 Gemini（個人 Google AI 方案或 Workspace 方案，依帳號資格與語系地區開放）
  │     ├── Google AI Studio（AI Pro 提高 Studio 內 Gemini 4 Neon 與 Nano Banana Pro 使用上限；Gemini API 則按 Cloud 專案限流與計費）
  │     └── Google Antigravity（Pro 基本配額）
  │
  ├── 【Google Flow credits】（只能用在 Flow）
  │     ├── 每日 50 點（所有使用者，用不完不累計）
  │     └── Pro 每月另加 1,000 點（用不完不遞延）
  │
  └── 【AI credits】（購買或一次性促銷取得，不是訂閱附贈）
        └── 增加 Gemini、Flow、Antigravity 的用量（日本除外）
              ├── Antigravity：基本配額用完後，是否扣 AI 點數由 Settings > Models 的開關決定
              └── Google One：查點數餘額與使用紀錄
```

- **兩種點數不要混為一談**：訂閱附贈的是 Google Flow credits，只能用在 Flow；Antigravity 超額用的是購買或一次性促銷取得的 AI credits。官方說明沒有寫 Flow 點數能拿去扣 Antigravity。
- **點數不累計**：Flow 每日點數當天用不完不累計，每月點數不遞延到下個月。購買的 AI 點數依購買時的條款到期，官方沒寫固定天數。
- **防止點數意外燒光的開關**：開關在 Antigravity 的 `Settings > Models`（toggle AI credit overages），不在 Google One；Google One 只能查點數餘額與使用紀錄。長時間執行或自動迴圈的工作，先確認這個開關的狀態。
- **API 配額不是價格**：AI Studio／Gemini API 的 RPM、TPM、RPD 是限流上限，按 Google Cloud 專案計算（同專案多把 Key 共用）；API 獨立計費，依模型與功能按 token、圖片或其他單位計價；每百萬 token 僅適用於採該單位的項目（[官方價格頁](https://aistudio.google.com/docs/pricing)，2026-11-24 核對：含圖片與 Lyria 按首計費項目）。
- **官方查證（2026-11-23，依獨立審查報告修正）**：[Google AI Pro 官方權益](https://support.google.com/googleone/answer/14534406?hl=en)、[Flow 點數](https://support.google.com/flow/answer/16526234?hl=en)、[Gemini Notebook 用量說明](https://support.google.com/gemininotebook/answer/17670842?hl=en)、[Gemini Notebook 方案限制](https://support.google.com/gemininotebook/answer/16213268?hl=en)、[Antigravity 方案](https://antigravity.google/docs/plans)、[Antigravity 設定](https://antigravity.google/docs/settings)、[Antigravity 權限規則](https://antigravity.google/docs/permissions)、[Antigravity 舊版與企業代理設定](https://antigravity.google/docs/agent-settings)、[Google One AI 點數](https://support.google.com/googleone/answer/16287445)、[Gemini API 限流](https://aistudio.google.com/docs/rate-limits)、[Gemini API 價格](https://aistudio.google.com/docs/pricing)。

---

## 3. Antigravity 實戰定位與安全邊界評估

報導首度將 Antigravity 列入主流消費級 AI 訂閱評析，並給出三個核心操作指引：
1. **先計畫再實作（Show me your plan before making any changes）**：
   報導推薦之提示詞範式明訂要求 Agent 先輸出變更計畫，確認無誤後才允許寫入。此機制完全契合本專案與全域規範之「先調研再動手、先計畫再實作」原則。
2. **專用資料夾是操作建議，不是安全邊界**：
   報導建議建立獨立資料夾（如「日本旅遊網站」），在「New Project」中載入。這能減少誤改其他檔案的機會，但不等於隔離：實際能存取什麼，取決於所使用的權限設定體系。依[官方權限文件（新版預設）](https://antigravity.google/docs/permissions)，App 提供 Request Review、Default、Auto、Turbo 四種權限預設（Default 與 Auto 可存取工作區加暫存目錄，Turbo 可存取整個檔案系統、終端指令不受限），並可配置明確的允許／詢問／拒絕規則與沙盒外執行授權；而在[舊版設定體系（以及沿用該組設定的企業帳號）](https://antigravity.google/docs/agent-settings)中，則提供 `Non-Workspace Access` 開關（預設關閉）控制是否允許代理讀寫工作區外的檔案。要落實安全邊界，新版設定應確認權限預設不是 Turbo、檢查明確權限規則與沙盒授權且不隨意在核准提示擴大範圍；使用舊版或企業設定體系者則須確認 `Non-Workspace Access` 保持關閉。
3. **開發者工具邊界**：
   報導特別提示「Antigravity 目前偏向程式開發與技術工作，非一般文書處理軟體」，初學者切勿將重要系統磁區或非專案目錄隨意掛載，且須防範高風險指令。

---

## 4. 對既有專案與架構之啟發

1. **多模型與額度路由矩陣收斂**：
   目前 `docs/model-burn-rate-routing-matrix.md` 著重於 API Token 與成本計算。本文所呈現之 Google AI Pro 點數邏輯（Flow 專用點數與購買的 AI 點數分開計算）應正式被納入資產治理，建立日常開發時的「基本配額優先、溢出點數嚴格警示」控管準則。
2. **工具分工與鏈路清晰化**：
   日常知識庫 ingestion 與文獻分析優先派工至 Gemini Notebook / Search AI，程式庫批次修改交由 Antigravity，避免將重度程式碼編輯交由純網頁端 Gemini App 造成斷頭與上下文丟失。

---

## 5. 行動清單（Action Items）

- [ ] **`T-20261122-03`**｜**[優先級：低]** 將 Google AI Pro 跨產品 AI 點數制度（Flow 點數、Antigravity 基本配額與溢出點數開關）與 8 大工具能力邊界梳理至 `docs/google-ai-pro-ecosystem-and-credit-routing.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\google-ai-pro-ecosystem-and-credit-routing.md`（收錄於集群 3）
  - **執行步驟**：
    1. 記錄 8 大工具定位（聊天、搜尋、文件、筆記、影音、程式代理、API、雲端運算）。
    2. 分開寫 Google Flow credits（50 點/日、Pro 另加 1,000 點/月，只能用在 Flow）與購買的 AI credits（Gemini、Flow、Antigravity 共用），以及 Antigravity 超額開關的位置（`Settings > Models`）。
    3. 寫 Antigravity 權限設定規則：區分新版四種權限預設（各能存取什麼、哪些情況禁用 Turbo、明確權限規則與沙盒授權）與舊版／企業設定體系（`Non-Workspace Access` 保持關閉），以及先計畫再實作。
    4. 同步修正既有產出第 1 節 AI Studio 列與第 2.1 節第 4 點：API 獨立計費，依模型與功能按 token、圖片或其他單位計價；每百萬 token 僅限適用項目。報導操作案例、圖片解析與提示詞保留為二手轉述／待測，操作難度與治理建議標明為作者分析。
  - **驗收標準（DoD）**：產出 `docs/google-ai-pro-ecosystem-and-credit-routing.md`，兩種點數分開說明並附官方網址，權限規則對應官方權限預設，既有第 1 節與第 2.1 節的 API 計費描述限定適用模型與功能、附官方價格頁，報導案例與作者分析分級清楚，且 `python tools/verify_inbox.py` 驗證通過。
