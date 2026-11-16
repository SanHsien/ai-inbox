---
id: 2026-10-17-shipper-epstein-md-anti-ai-slop
title: "對抗 AI 罐頭設計：Shipper 釋出 92 萬字元 epstein.md 終結 Vibe Coding 視覺審美疲勞"
source_url: "https://www.threads.com/@kufutw/post/Dei87mJmgvR"
source_platform: "Threads"
author: "Kufu 酷服 (@kufutw) / Shipper (@shipper_now)"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: "2"
cluster_role: "審美防線與字型排版"
short_title: "Shipper 反 AI 罐頭設計"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "Shipper 在 X 的原始貼文回覆要登入，讀到 0 則（總數未知）；Threads 留言讀到 6／6 則；27 秒影片只抽看 8 個畫面"
source_images: 8
source_replies: 6
tags:
  - anti-ai-slop
  - design-system
  - frontend-ui
  - prompt-engineering
  - vibe-coding
---

# 對抗 AI 罐頭設計：Shipper 釋出 92 萬字元 epstein.md 終結 Vibe Coding 視覺審美疲勞

- **來源貼文**：[Threads @kufutw 貼文](https://www.threads.com/@kufutw/post/Dei87mJmgvR)
- **原始發起**：Shipper (`@shipper_now`)，[X 原貼文](https://x.com/shipper_now/status/2110637576935891122)（2026-10-15）
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已做 (Done)`

---

## 0. 原始資料盤點

> 2026-11-16 重審：Threads 貼文文字、附的 1 支 27 秒影片（抽看 8 個畫面）、6 則留言（作者 3 則、網友 3 則）都看過；另看了作者留言連結的 Shipper 在 X 的原始貼文本文（X 的回覆要登入，沒看到）。

- **作者圖片**（1 支影片，抽 8 個畫面）：是 Shipper 產品的宣傳短片，**沒有出現 epstein.md 的內容**。畫面依序是品牌字樣、輸入框打字「做一個 Airbnb 風格的租車平台」、分階段的任務清單（第一階段打勾完成、第二階段待做）、使用者管理後台、多語系勾選、螢幕上的數據分析面板、收尾品牌字樣。風格是白底、細邊框、綠色重點色。
- **作者留言補充**（3 則，等於貼文正文）：
  - 第 1 則：檔案超過 **927,400 個字元**，附 Shipper 在 X 的原貼文連結。
  - 第 2 則：禁用清單（卡片陰影、Emoji、綠色 LIVE 標籤、藍紫漸層、350 個 AI 常用詞）；Shipper 說這是團隊 11 個月、每天約 8 小時刷 X，持續把觀察到的問題加進自家 AI 開發工具累積出來的。
  - 第 3 則：這不是新模型，是 Markdown 規則；**目前缺乏公開測試，證明它在不同 AI 開發工具上有效**。
- **網友留言重點**：
  - `benhoooooooo`：「又一個 AI slop」（5 個讚，三則裡最多）。
  - `leo_2783_`：質疑讀一次的 token 量（留言寫約 23k；以 92 萬字元估算實際會遠高於此）。
  - `vlk.dimitrov`：拿檔名開玩笑。
- **對分析的影響**：
  - 字元數統一為 927,400+（原寫「82 萬～92 萬」沒有依據），已改。
  - X 原貼文與 Threads 貼文**都沒有給檔案下載連結**，Shipper 說的是「加進我們 vibe coding 介面的 codebase」。原筆記寫成「釋出一份可放進 AGENTS.md／.cursorrules 的規範檔」，但檔案是否公開、怎麼取得，來源沒說；已在 1.2 節標明。
  - 1.2 節「正向工程標準」那一行（純色高對比、語意化排版、格線對齊）原貼文沒有，是分析時的延伸，已標明。
  - 補上轉述者自己的保留意見（無公開測試）與網友的質疑。兩個已完成任務是依「禁用清單」自己蒸餾規範與寫掃描腳本，不依賴拿到原檔，不受影響。

---

## 1. 核心內容摘要與技術深挖

### 1.1 痛點：AI 介面生成的「千篇一律罐頭感（AI Slop）」
- **現象**：當前使用 AI（如 v0, bolt.new, Lovable, Claude Artifacts 等）生成 Web 前端介面或 Landing Page 時，普遍面臨嚴重的**視覺趨同（Visual Convergence）**與**審美疲勞**。
- **典型 AI 罐頭病徵（Vibe Coding Slop）**：
  1. **無腦陰影（Overused Box Shadows）**：任何卡片元件一律加上厚重的黑色/半透明擴散陰影，缺乏物理光源層次感。
  2. **濫發 Emoji（Decorative Emojis）**：標題和列表前充斥 🚀、💡、🔥、✨、🎉 等裝飾符號，顯得廉價且非專業。
  3. **俗氣藍紫漸層（Blue/Purple Gradients）**：背景與按鈕千篇一律採用 Cyberpunk 式的紫藍漸層（`from-indigo-500 to-purple-600`）。
  4. **虛假動態徽章（Fake LIVE Badges）**：莫名其妙出現閃爍綠點的 `LIVE` 或 `Active Now` 徽章。
  5. **空洞行銷黑話（350+ AI Buzzwords）**：文案充斥 *delve*, *vibe*, *seamlessly*, *elevate*, *revolutionize*, *tapestry*, *empower* 等缺乏實質內容的模型慣用語。

### 1.2 Shipper 的解法：92 萬字元的負向約束規格 `epstein.md`
- **核心哲學**：**「好設計不是告訴 AI 要做什麼，而是嚴格禁止它做什麼（Negative Constraints）」**。
- **做法**：
  - 由 AI 應用開發平台 **Shipper** (`@shipper_now`) 介紹一份超過 927,400 字元的超大 Markdown 規則檔（`epstein.md`）。Shipper 說這是團隊 11 個月、每天約 8 小時刷 X，持續把看到的設計問題加進自家開發工具累積出來的。
  - **取得方式不明**：X 原貼文與 Threads 轉述都沒有給檔案下載連結，原話是「加進我們 vibe coding 介面的 codebase」。能不能拿來當 Claude Code／Cursor 的專案規則（類似 `AGENTS.md` / `.cursorrules`）是本筆記的推想，來源沒說。
  - **效果未經驗證**：轉述者自己寫明，目前缺乏公開測試證明這份規則在不同 AI 開發工具上有效；留言區也有人回「又一個 AI slop」、質疑一次要吃的 token 量。
  - **強硬禁令（Explicit Banning）**：
    - ❌ **視覺禁令**：嚴禁無腦 box-shadow、嚴禁未經說明的 Emoji、嚴禁藍紫漸層、嚴禁虛構的 LIVE 標籤。
    - ❌ **文案黑名單**：嚴格過濾 350+ 個 AI 高頻陳腔濫調，強制使用清晰、具體、活人感的技術與產品描述。
    - ✅ **正向工程標準**（原貼文沒有這一項，是本筆記依禁令反推的延伸）：回歸簡潔、純色高對比、語意化排版（Semantic Typography）、真實留白與扎實的格線對齊。

### 1.3 罐頭 AI 設計 vs 反 Slop 工程規範對比

```text
┌────────────────────────────────────────────────────────────────────────┐
│               罐頭 AI 設計 (Slop) vs 反 Slop 簡潔工程架構              │
└────────────────────────────────────────────────────────────────────────┘

 【❌ 罐頭 AI 生成特徵 (AI Slop)】
  ┌───────────────────────────────────────────────────────────┐
  │ 🚀 [LIVE] Elevate Your Seamless Workflow with AI Magic ✨  │ <── 濫用 Emoji + 偽狀態 + 空洞黑話
  │ ┌───────────────────────────────────────────────────────┐ │
  │ │ (from-indigo-500 via-purple-500 to-pink-500 藍紫漸層)  │ │ <── 俗套漸層背景
  │ │                                                       │ │
  │ │ [卡片區塊]                                            │ │
  │ │  - 巨大模糊陰影 (box-shadow: 0 25px 50px -12px ...)   │ │ <── 浮誇厚重陰影
  │ │  - "Delve into the vibrant tapestry of your data"     │ │ <── 典型 Delve 廢話
  │ └───────────────────────────────────────────────────────┘ │
  └───────────────────────────────────────────────────────────┘

                           ▼  經過 epstein.md 規範洗鍊

 【✅ 專業簡潔現代設計 (Clean & Opinionated)】
  ┌───────────────────────────────────────────────────────────┐
  │ Real-time Metrics Dashboard                               │ <── 明確語意標題、無裝飾 Emoji
  │ ┌───────────────────────────────────────────────────────┐ │
  │ │ 實色底襯 + 1px 細緻邊框 (border-slate-200 / slate-800) │ │ <── 去除漸層與浮誇陰影
  │ │ 乾淨排版層級 (Clean Typography + Inter / Roboto)       │ │
  │ │                                                       │ │
  │ │ 99.98% Uptime · 12ms Average Latency · 0% Drop Rate   │ │ <── 數據與功能說話，零廢話文案
  │ └───────────────────────────────────────────────────────┘ │
  └───────────────────────────────────────────────────────────┘
```

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與既有的文案規則高度契合**：現有的 `skills/human-writing` 已明定「清除商業黑話和模型慣用黑話、不灌水」。`epstein.md` 則是將此原則推廣至**前端介面與視覺設計**領域。
  - **與全域規則契合**：`RULE[user_global]` 規定「前端介面沒指定風格時：深色模式、現代字型、流暢過場、Flexbox/Grid 響應式」，恰好也是追求實體可用性而非浮誇裝飾。
  - **與 `cinematic-shot` / `motion-prompt` 形成完整前端美學閉環**：
    1. `epstein.md`：奠定**靜態視覺底色**（拒絕廉價陰影與漸層，保證專業克制）。
    2. `motion-prompt`：賦予**微觀元件動態**（120 款具名動畫，去除生硬過渡）。
    3. `cinematic-shot`：負責**宏觀展示運鏡**（導引使用者視覺，完成發布展示）。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **負向邊界約束（Negative Constraints as Spec）**：在給 Agent 的前端提示詞中，明確列出禁用的老套路（No generic box-shadows, No blue-purple gradients, No decorative emojis, No AI buzzwords）。
    2. **黑名單自動化檢查**：可建立一個簡單的 Linter 腳本，快速掃描生成的前端代碼是否存在典型 AI 罐頭痕跡。
  - **需調整之處**：
    - 92 萬字元的超大規則檔若整份丟入上下文會嚴重耗費 Token；應將其精華**蒸餾**為結構化、模組化的一頁式規則（One-page Guidelines），僅在執行 UI 生成任務時按需載入。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-19`**｜**[優先級：高]** 蒸餾並建立「反 AI 罐頭設計 (Anti-AI-Slop) 前端工程規範」，納入全域前端生成準則
  - **目標範圍**：`C:\GitHub\ai-inbox\notes\` 與前端設計規範
  - **完成日期**：2026-10-23
  - **具體實作步驟**：
    1. 汲取 `epstein.md` 核心哲學，歸納四大禁制清單（視覺陰影、俗套漸層、無用 Emoji、350+ AI 廢話辭庫）。
    2. 定義正向替代方案（精確 1px 邊框、俐落實色對比、Inter 現代字型層級、純數據活人文案）。
    3. 產出一份緊湊高密度的 Markdown 規範，可直接供 Claude Code / Antigravity 前端生成時快速引用。
  - **驗收標準（DoD）**：產出規範文檔，並在一次模擬前端元件生成測試中，成功產出零罐頭感、乾淨俐落的介面。
  - **實作紀錄 / 證據**：產出 `docs/anti-ai-slop-frontend.md` 前端規範與 `assets/anti-slop-demo/index.html` 示範元件（1px 邊框、無裝飾 Emoji、零漸層與純數據文案），`python tools/verify_inbox.py` 通過。

- [x] **`T-20261017-20`**｜**[優先級：中]** 實作輕量化「AI 罐頭特徵靜態掃描腳本 (verify_no_slop.py)」
  - **目標範圍**：`tools/` 或專案品質檢查腳本
  - **完成日期**：2026-10-23
  - **具體實作步驟**：
    1. 編寫 Python 腳本，利用正規表示式檢測 HTML/CSS/Tailwind 代碼中的罐頭特徵（如 `from-indigo.*to-purple`、巨大 `shadow-2xl`、文字包含 `delve/vibe/seamlessly`）。
    2. 輸出清晰的警告與違規行號報告。
    3. 整合至前端驗收檢查流程。
  - **驗收標準（DoD）**：腳本能準確偵測故意包含罐頭特徵的測試 HTML 檔案，並在乾淨代碼下回報 Pass。
  - **實作紀錄 / 證據**：實作 `tools/verify_no_slop.py` 與 `tests/test_verify_no_slop.py`，驗證 demo 檔案 0 違規 Pass 且罐頭測試抓出全部 SLOP-01~05 違規，單元測試通過。
