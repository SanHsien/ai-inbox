---
id: "2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval"
title: "數位時代評析：Google AI Pro 八大工具全景實測——Antigravity 電腦檔案代理、Flow 影片生成與跨產品 AI 點數制"
source_url: "https://www.bnext.com.tw/article/93098/google-ai-pro-8-tools-features-tutorial"
source_platform: "bnext.com.tw (數位時代)"
author: "蘇柔瑋"
analyzed_at: "2026-11-22"
analyzed_by: "antigravity"
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

| 工具名稱 | 核心場景與功能特徵 | 操作難度 | 額度計算機制 |
| :--- | :--- | :---: | :--- |
| **Gemini App** | 日常對話、創意發想、多語言翻譯、文字潤飾與程式碼諮詢 | ★☆☆ | 依選用模型與進階功能設定使用上限，不與其他工具共佔 |
| **Google 搜尋 AI 模式** | 即時網路資訊查詢、規格與價格跨店比價、多模態圖文搜尋 | ★☆☆ | 依搜尋次數與模型配額計算，進階模型提供較高上限 |
| **Gemini Notebook**（原 NotebookLM） | 匯入 PDF、研究報告與網站，進行可溯源 Grounding 問答與語音摘要 | ★★☆ | 筆記本數量、單本來源文件數與音訊摘要生成各有獨立上限 |
| **Gmail / Google 文件內建 Gemini** | 跨郵件長串摘要、內聯草擬回覆、段落潤飾與 PTCF 提示框架 | ★★☆ | 依 Google Workspace 帳號方案與語言地區限制 |
| **Google Antigravity** | 桌面端 Agent 開發工具、授權本地資料夾多檔案修改、網站建置與 Vibe Coding | ★★★ | **Pro 基本配額**；用完後可自選是否消耗**額外跨產品 AI 點數** |
| **Google Flow** | 文字描述或參考圖片生成影片、運鏡視角控制、社群短影音素材製作 | ★★☆ | **每日 50 點免費**（當日結算）+ **Pro 每月 1,000 點**訂閱點數；可額外加購 |
| **Google AI Studio** | 開發者模型原型驗證、Prompt 調校、Gemini API Key 配額調用 | ★★★ | 依 API Key 方案與模型 RPM/TPM 獨立計費，不等於 Pro 吃到飽 |
| **Google Colab** | 雲端 Jupyter/Python 環境、GPU/TPU 算力調用、資料分析與 ML 運算 | ★★★ | 依運算單元（Compute Units）與連線工作階段時長限制 |

### 8 張插圖實測解析
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
  ├── 【獨立隔離額度層】（互不扣抵、獨立重置）
  │     ├── Gemini App（聊天次數 / 模型輪次）
  │     ├── Google 搜尋 AI 模式（即時檢索配額）
  │     ├── Gemini Notebook（筆記本數量 / 來源數 / 音訊摘要）
  │     └── Workspace 內建 Gemini（Gmail / Docs 內嵌調用）
  │
  └── 【跨產品 AI 點數（AI Credits）流通層】
        ├── Google Flow
        │     ├── 每日免費額度：50 點 / 日（當日歸零，不累計至次日）
        │     └── Pro 專屬點數：1,000 點 / 月（帳單週期重置，不遞延）
        │
        └── Google Antigravity
              ├── Pro 會員基本配額（桌面 Agent 日常專案開發基礎額度）
              └── 溢出點數控制（基本配額耗盡時，可自選「暫停」或「消耗額外加購 AI 點數」）
```

- **無效累積規則**：每日贈送點數（50 點）每日歸零；每月訂閱點數（1,000 點）次月不遞延。唯有獨立購買之付費點數封包具備自訂有效期限。
- **防止意外溢出之安全開關**：Antigravity 支援在 Google One AI 點數管理介面中設定「是否允許使用額外 AI 點數」，此機制為防止長時間運行或自動迴圈（Loop）引發非預期點數燒盡之關鍵防線。

---

## 3. Antigravity 實戰定位與安全邊界評估

報導首度將 Antigravity 列入主流消費級 AI 訂閱評析，並給出三個核心操作指引：
1. **先計畫再實作（Show me your plan before making any changes）**：
   報導推薦之提示詞範式明訂要求 Agent 先輸出變更計畫，確認無誤後才允許寫入。此機制完全契合本專案與全域規範之「先調研再動手、先計畫再實作」原則。
2. **目錄授權隔離**：
   操作時明確要求使用者建立獨立資料夾（如「日本旅遊網站」），並在「New Project」中指定載入。此與全域規範「不要在專案目錄外讀寫或刪改、所有專案統一置於 `C:\GitHub\<repo>`」形成一致的安全邊界防護。
3. **開發者工具邊界**：
   報導特別提示「Antigravity 目前偏向程式開發與技術工作，非一般文書處理軟體」，初學者切勿將重要系統磁區或非專案目錄隨意掛載，且須防範高風險指令。

---

## 4. 對既有專案與架構之啟發

1. **多模型與額度路由矩陣收斂**：
   目前 `docs/model-burn-rate-routing-matrix.md` 著重於 API Token 與成本計算。本文所呈現之 Google AI Pro 點數流通邏輯（Flow 點數與 Antigravity 跨產品點數）應正式被納入資產治理，建立日常開發時的「基本配額優先、溢出點數嚴格警示」控管準則。
2. **工具分工與鏈路清晰化**：
   日常知識庫 ingestion 與文獻分析優先派工至 Gemini Notebook / Search AI，程式庫批次修改交由 Antigravity，避免將重度程式碼編輯交由純網頁端 Gemini App 造成斷頭與上下文丟失。

---

## 5. 行動清單（Action Items）

- [ ] **`T-20261122-03`**｜**[優先級：低]** 將 Google AI Pro 跨產品 AI 點數制度（Flow 點數、Antigravity 基本配額與溢出點數開關）與 8 大工具能力邊界梳理至 `docs/google-ai-pro-ecosystem-and-credit-routing.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\google-ai-pro-ecosystem-and-credit-routing.md`（收錄於集群 3）
  - **執行步驟**：
    1. 記錄 8 大工具定位（聊天、搜尋、文件、筆記、影音、程式代理、API、雲端運算）。
    2. 詳列 Google Flow 點數刷新機制（50 點/日、1,000 點/月）與 Antigravity 專屬配額/額外點數扣抵開關。
    3. 整合 Antigravity 專案掛載目錄安全規範（目錄白名單、先計畫再實作）。
  - **驗收標準（DoD）**：產出 `docs/google-ai-pro-ecosystem-and-credit-routing.md`，定義點數路由與目錄邊界防護規則，且 `python tools/verify_inbox.py` 驗證通過。
