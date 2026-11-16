---
id: 2026-10-17-reelbird-open-source-screen-recorder
title: "Reelbird：免費開源螢幕錄影神器（原生 Swift、S3/R2 自託管、即時網址與 Agent MCP 整合）"
source_url: "https://github.com/btahir/reelbird"
source_platform: "GitHub"
author: "btahir"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: archived
cluster: "2"
cluster_role: "開源剪輯與動效提示庫"
short_title: "Reelbird 開源螢幕錄影"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 6
source_replies: 0
tags:
  - screen-recording
  - mcp
  - agent-tools
  - dev-tools
  - video-production
---

# Reelbird：免費開源螢幕錄影神器（原生 Swift、S3/R2 自託管、即時網址與 Agent MCP 整合）

- **來源倉庫**：[GitHub - btahir/reelbird](https://github.com/btahir/reelbird)
- **專案作者**：`btahir`（GitHub 個人檔案顯示名稱為 Bilal）
- **分析日期**：`2026-10-17`
- **當前狀態**：`⚪ 封存不做 (Archived)`
- **授權協議**：`MIT License`

---

## 0. 原始資料盤點

> 2026-11-16 重審：來源是 GitHub repo，沒有社群貼文。看了現行 README 全文與 6 張圖。repo 重審時 49 顆星，issue 與 Discussions 都是 0 則，沒有留言可讀。

- **作者圖片**（README 6 張）：
  - 圖 1 橫幅：標語「錄螢幕、送連結、之後再修」，下方是編輯器畫面。
  - 圖 2 示範動畫：錄一個待辦清單 app，游標點擊處自動放大。
  - 圖 3 編輯器（縮放）：上方預覽含圓形鏡頭畫面；右側 Zoom 面板有自動／手動／關閉三段、強度滑桿、單一縮放的深度（1.8x）與「跟隨游標」；下方時間軸有影片軌、音訊波形、一排縮放區段。右上有 Copy Link 與 Export。
  - 圖 4 錄製來源選擇：分螢幕／視窗／區域三頁，列出各 app 視窗縮圖；下方開關有麥克風、鏡頭、系統音訊、**邊錄邊分享（停止時連結已複製）**，畫質 60 fps。
  - 圖 5 編輯器（音訊）：人聲增強分四級、自動音量、系統音訊在人聲下自動壓低、一鍵剪掉長靜音。
  - 圖 6 分享視窗：顯示一條 r2.dev 的公開連結，說明「目前播的是快錄版，按 Update Link 才發布編輯結果」，另有停止分享。
- **作者留言補充**（README 現況，原筆記沒寫或寫錯的）：
  - 有付費方案 **Reelbird Pro（每月 5 美元）**：不想自己設 bucket 的人用官方代管連結，附觀看統計。app 本身免費、分享到自己的 bucket 免費。
  - 比較表多一欄 **OpenScreen**（MIT、免費、支援 Mac／Windows／Linux，但不產生分享連結）。
  - 「不規劃支援 Windows 與 Linux」README 有明寫，原筆記正確。
  - MCP 工具不只錄製：還有標記點、專案檢視、編輯（裁切、鏡頭位置、速度）、模糊區域、找出並遮蔽敏感資訊等。
- **網友留言重點**：無（issue 0、Discussions 0）。專案才建立一個月（2026-10-13）、49 顆星，沒有第三方實測回報可佐證 README 的說法。
- **對分析的影響**：
  - 作者欄的「Bashir Tahir」查無依據，GitHub 個人檔案顯示的名字是 Bilal；已改成只寫帳號 `btahir`。
  - 1.1 節與比較表的「100% 免費」「無後台伺服器」補上 Pro 代管方案；「只有登入 Pro 時才連 Reelbird 伺服器」。
  - Windows 替代方案補上 OpenScreen。兩個任務本來就是「不做」，狀態不變。

---

## 1. 核心內容摘要與技術深挖

### 1.1 痛點與核心主張
- **商業痛點**：
  - **Loom**：免費版限時 5 分鐘、限制 25 部影片、不允許直接下載高畫質影片，Business 版每月每人收費 \$18 美元以上。
  - **Screen Studio**：視覺動效極佳（平滑游標、自動縮放），但每月高達 \$29 美元（或年繳每月 \$9 美元），且分享連結必須等影片完整導出後才能生成。
- **Reelbird 解法**：**「停錄即分享、後續同網址精修、無伺服器自託管、完全開源 MIT」**。
  - **即時網址（Share-while-recording）**：邊錄邊推流（HLS / S3 分段上傳）至自己的 Cloudflare R2 / AWS S3，錄影按下停止瞬間，公開分享網址已在剪貼簿中。
  - **原地精修不換網址（Update Link）**：後續在編輯器內加入自動縮放（Auto-zoom）、平滑游標、音量平衡（-16 LUFS）、敏感資訊模糊、Apple 原生字幕等，點擊更新後直接覆蓋雲端檔案，原始分享網址不變。
  - **原生高效無外依賴**：100% 原生 Swift 6.2，基於 macOS 15+ 系統框架（ScreenCaptureKit, Metal, Apple Speech, Foundation Models），無第三方依賴、無遙測收集；分享到自己的 bucket 時不經任何 Reelbird 伺服器，只有登入付費的 Reelbird Pro 代管（每月 5 美元，附觀看統計）才會連官方伺服器。
  - **原生支援 Coding Agent（CLI & MCP）**：內建 `reelbird mcp`，讓 Claude Code、Codex、Cursor 等 Agent 能在交付程式碼後自動錄製展示 Demo，並回傳連結。

### 1.2 系統架構與 Agent 錄影管線可視化

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Reelbird 與 AI Agent 閉環錄影架構                         │
└────────────────────────────────────────────────────────────────────────┘

    [Coding Agent (Claude Code / Codex / Cursor)]
           │
           │ (透過 stdio 調用 reelbird mcp: list_sources, record, stop)
           ▼
    ┌───────────────────────────────────┐
    │ Reelbird CLI & Engine (Swift 6.2) │
    │ ├─ ScreenCaptureKit (畫面捕捉)     │
    │ ├─ Input Logger (點擊/按鍵日誌)    │
    │ └─ Metal Renderer (畫面渲染)       │
    └──────────────────┬────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼ (錄影期間實時分段串流)          ▼ (本地寫入 .reelbird 目錄)
 ┌──────────────┐                ┌──────────────┐
 │ S3 / R2 存儲 │                │ 本地完整音軌 │ (2 秒分段防崩潰保護)
 └──────┬───────┘                └──────┬───────┘
        │ 停錄即刻複製分享連結                  │ 後續精修 (Post-polish)
        ▼                               ▼
 [https://r2.dev/r/xyz]          ┌───────────────────────────────────┐
 (任何人立即可看生肉 Demo)        │ 後製引擎 (無需換連結)             │
        ▲                        │ ├─ Auto-zoom (點擊處自動放大)      │
        │ 覆蓋更新 (Update Link) │ ├─ Smooth Cursor (平滑重繪游標)   │
        └────────────────────────┤ ├─ Find Sensitive (自動辨識遮蔽)  │
                                 │ └─ On-device Captions (原生字幕)  │
                                 └───────────────────────────────────┘
```

### 1.3 競品功能與跨平台定位分析

| 特性 | Reelbird | Loom | Screen Studio | Cap (Open Source) |
| :--- | :--- | :--- | :--- | :--- |
| **價格與授權** | 免費 (MIT)；選用 Pro 代管 $5/月 | 免費受限 / $18/月起 | $29/月 (商業閉源) | 免費個人 / $29/年 (AGPLv3) |
| **儲存方式** | 自託管 (Cloudflare R2 / S3) | Loom 官方雲端 | 官方或本機導出 | Cap 雲端或自託管 |
| **停錄即出連結** | ✅ 有（推流至 R2） | ✅ 有（上傳 Loom） | ❌ 需等待導出 | ✅ Instant 模式 |
| **同連結精修更新** | ✅ 支援（無縫替換） | ❌ 無自動縮放精修 | ❌ 導出後才生連結 | ⚠️ 兩模式分離 |
| **平滑游標與縮放** | ✅ Metal 游標重繪 | ❌ 無 | ✅ 業界頂級視覺 | ✅ 支援 Studio 縮放 |
| **Agent / MCP 支援** | ✅ 內建 `reelbird mcp` | ❌ 無官方 MCP | ❌ 無官方 MCP | ❌ 無原生 MCP |
| **支援平台** | macOS (Apple Silicon 原生) | 全平台 (Web/Mac/Win) | macOS | macOS, Windows (Beta), Linux |

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **Agent 自動化交付驗收**：目前依據 `verification-protocol`，在完成程式碼或修復 Bug 時需要貼出終端輸出。未來對於前端 UI / Web 類任務，可透過 Agent MCP 自動錄製 15 秒展示影片並產生分享連結，大幅提升驗收說服力。
  - **與 cinematic-shot 互補**：
    - `cinematic-shot` 專注於「程式碼模擬純前端電影級運鏡（Web 前端錄影）」。
    - `Reelbird` 專注於「全螢幕/視窗真實錄影 + 滑鼠點擊追蹤放大 + 麥克風音訊修復」。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **「S3/R2 免伺服器即時推流與同網址覆蓋更新」架構**：利用 Cloudflare R2（零出口流量費 + 10GB 免費空間），將影片與微型 HTML 撥放器一併上傳，是個人獨立開發者極佳的展示託管方案。
    2. **Agent 錄製展示（Demo-as-a-Link via MCP）概念**：在跨平台工作流中，探索如何透過 MCP 呼叫錄影工具，完成「寫好功能 -> 跑測試 -> 自動錄 Demo -> 交付 PR / 貼連結」。
  - **環境限制與替代考量**：
    - **平台限制**：Reelbird 深度綁定 macOS 專屬底層 API（ScreenCaptureKit, Metal, Apple Speech），官方表明**不計畫支援 Windows 與 Linux**。
    - **Windows 原生因應方案**：維護者的工作環境為 Windows 11，若要在 Windows 上實現類似的「Agent 自動錄 Demo」：
      - 方案 A（Web 應用）：使用 Playwright / Puppeteer 內建 `recordVideo` 搭配 headless 瀏覽器錄製操作 Demo。
      - 方案 B（系統桌面）：調研開源跨平台的 **Cap**（Windows 為 beta）或 README 比較表列出的 **OpenScreen**（MIT、免費、支援 Windows，但不產生分享連結），或透過 OBS CLI / FFmpeg 錄影腳本封裝為 Windows 本地 MCP 工具。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261017-15`**｜**[優先級：低]** 評估並建立「AI Agent 自動錄製展示 (Demo-as-a-Link)」工作流規範與 Windows 替代方案調研
  - **目標範圍**：`C:\GitHub\ai-inbox\notes\` 與驗證流程手冊
  - **狀態**：⚪ 不做（Reelbird 原生依賴 macOS Swift，Windows 11 不適用，且已有 Playwright 錄影與 Code-as-Video 方案）
  - **具體實作步驟**：
    1. 分析 Reelbird 的 MCP 工具介面設計（`list_sources`, `start_recording`, `stop_recording`, `add_marker`）。
    2. 針對 Windows 11 環境，評估兩種自動錄影路徑：(a) Playwright 自動化錄製 Web UI，(b) Windows 平台開源工具（如 Cap Windows 版或 FFmpeg 桌面截取）。
    3. 產出跨平台「Agent 驗證展示錄影指南」，明定何時該交付動態 Video Demo。
  - **驗收標準（DoD）**：完成調研報告，並在 Windows 環境下使用腳本成功自動錄製一段 10 秒操作影片。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261017-16`**｜**[優先級：低]** 設計基於 Cloudflare R2 / S3 的個人影片展示零成本託管模板
  - **目標範圍**：雲端儲存與靜態部署方案
  - **狀態**：⚪ 不做（搭配 Reelbird 之特定託管方案，隨 Reelbird 評估終止一併關閉）
  - **具體實作步驟**：
    1. 參考 Reelbird 的 S3/R2 結構（微型 viewer 頁面 + MP4/HLS）。
    2. 撰寫單檔部署腳本（如 PowerShell / Python），支援指定本地影片上傳至 Cloudflare R2，並自動輸出公開預覽短網址。
    3. 支援 `--update` 參數原地覆蓋影片而不變更分享短網址。
  - **驗收標準（DoD）**：腳本可在本地執行，成功上傳測試影片並以固定 URL 在瀏覽器中正常播放。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
