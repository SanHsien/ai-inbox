---
id: 2026-11-02-opencut-open-source-capcut-alternative-video-editor
title: "OpenCut 開源 CapCut 替代品解析：97K Stars 多軌剪輯，以及重寫中的 Rust 核心、MCP Server 與無頭渲染規劃"
source_url: "https://github.com/OpenCut-app/OpenCut"
source_platform: "GitHub (OpenCut-app/OpenCut) & 社群推薦"
author: "OpenCut 團隊 (@opencutapp / OpenCut-app)"
analyzed_at: 2026-11-02
analyzed_by: "Antigravity"
status: archived
cluster: "2"
cluster_role: "開源剪輯與動效提示庫"
short_title: "OpenCut開源視訊編輯器與AI Agents"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 0
source_replies: 4
tags:
  - opencut
  - capcut-alternative
  - video-editor
  - rust
  - webcodecs
  - mcp-server
  - headless-rendering
  - generative-ui
  - code-as-video
---

# OpenCut 開源 CapCut 替代品解析：97K Stars 多軌剪輯，以及重寫中的 Rust 核心、MCP Server 與無頭渲染規劃

- **來源連結**：[GitHub 專案庫 (OpenCut-app/OpenCut)](https://github.com/OpenCut-app/OpenCut) ｜ [經典版本庫 (OpenCut-Classic)](https://github.com/opencut-app/opencut-classic) ｜ [官方網站 (opencut.app)](https://opencut.app)
- **核心團隊**：OpenCut 團隊（X: @opencutapp）
- **贊助者**：fal.ai（README 只列這一家；原寫的 Vercel OSS Program 在 README 找不到，2026-11-16 移除）
- **分析主題**：解構在 GitHub 斬獲 **97,000+ Stars**、被譽為「開源無浮水印 CapCut 替代品」的現象級視訊編輯器專案 **OpenCut**。深入剖析其針對 CapCut 付費牆與雲端隱私問題提出的「本機優先（Local-first）多軌剪輯」架構，解析其**進行中的重寫計畫**（2026-11-16 更正：README 把下列項目全列為「即將推出」，都還不是現有功能）——以 **Rust Core** 統一 Web、Desktop 與 Mobile 渲染核心、給 AI Agents 用的 **MCP Server**、**Headless 無頭渲染模式**、以及外掛優先（Plugin-first）與編輯器內嵌腳本標籤頁（In-Editor Scripting），推導新一代「AI Agent 驅動全自動視訊剪輯」的工程架構標準。
- **當前狀態**：`⚪ 已封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-17-reelbird-open-source-screen-recorder.md`](./2026-10-17-reelbird-open-source-screen-recorder.md)（Reelbird 開源螢幕錄影：輕量流暢錄製與展示）
  - [`2026-10-28-motion-design-agent-harness-opus-55.md`](https://github.com/SanHsien/code-as-video-studio/blob/main/notes/2026-10-28-motion-design-agent-harness-opus-55.md)（代碼驅動 Motion Design Agent：Harness、seek(t) 與分鏡自審循環）
  - [`2026-11-01-designer-riven-claude-opus-55-code-motion-design-12-demos.md`](https://github.com/SanHsien/code-as-video-studio/blob/main/notes/2026-11-01-designer-riven-claude-opus-55-code-motion-design-12-demos.md)（設計師 Riven Claude Opus 5.5 動態設計 12 大純代碼視覺特效規格）
  - [`notes/2026-10-26-answer-me-with-html-visual-agent-artifacts.md`](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md)（Visual Artifacts 與 Generative UI 互動展示規範）

---

## 0. 原始資料盤點

> 2026-11-16 重審：來源是 GitHub repo，沒有社群貼文。讀了 README 全文、repo 目錄結構、GitHub API 的 repo 資訊，以及三則相關 issue／PR（#827、#778、#752）與 #778 的 4 則留言。

- **作者圖片**：README 沒有架構圖或畫面截圖，只有專案標誌與三個徽章（Discord、X、MIT 授權），不計入。
- **作者留言補充**（README 的「Status」段，等同作者的現況聲明）：
  - **OpenCut 正在從頭重寫**。Editor API、外掛優先架構、Rust 核心（桌面／行動／瀏覽器共用一套程式碼）、**MCP server、Headless 模式、編輯器內的腳本分頁，全部列在「What's coming」（即將推出）**，不是現有功能。
  - 目前能用的是舊版 `opencut-app/opencut-classic`，`opencut.app` 跑的也是舊版；重寫版放在 `new.opencut.app`，還沒準備好接手。
  - 架構設計期間暫不接受外部貢獻。
  - 贊助者只列 fal.ai 一家。
- **網友留言重點**（issue 區）：
  - #827（2026-06，開啟中、無人回覆）：使用者要求「能直接接上 Claude 做基本剪輯」的 API／CLI／Headless 模式——也就是這個功能當時還不存在。
  - #778（2026-04，開啟中）：提案做 Headless 渲染 SDK，明講 OpenCut 目前缺少程式化入口、AI agent 無法驅動它。留言裡 `JasonLovesDoggo` 指出 Rust 的合成、特效、遮罩 crate 已能脫離瀏覽器渲染；提案人 `lfzm` 回覆說盤點後 Rust 只涵蓋匯出流程約三成，其餘（影格描述、各類節點渲染、文字排版等）還在 TypeScript／Web API 裡。
  - #752（2026-03）：社群送的「MCP server」PR，已關閉、未合併。
  - #867 是官方的里程碑項目（引擎核心＋Editor API＋外掛 API＋MCP Server＋Headless 執行環境），標題顯示這些是同一批規劃中的工作。
- **對分析的影響**：
  - **最大的更正**：原筆記把 MCP Server、Headless 模式、編輯器內腳本寫成「已內建」「正式列為一級架構公民」。依 README 與 issue，這些在重審當下都還沒推出。標題、分析主題、1.2 節、2.2 節、2.3 節與第 3 節已改成「規劃中」。
  - **2.3 節的指令 `opencut render --timeline … --quality 4k` 與 2.2 節的工具名稱（`split_clip`、`insert_track` 等）查無出處**，是分析者推測的寫法；Headless 模式尚未存在，所以這個指令目前不可能可用。已加註。
  - **fal.ai「深度整合」不成立**：README 只把 fal.ai 列為贊助者，沒有說時間軸能直接呼叫它生成素材。「Vercel OSS Program」在 README 找不到，已從贊助者移除並註明。
  - **repo 結構查證屬實的部分**：`apps/web`、`apps/desktop`、`apps/api` 與 `crates/media` 確實存在；主要語言是 TypeScript；授權 MIT。依 #778 的留言，Rust 目前只涵蓋匯出流程的一部分，2.1 節「Rust 統一渲染核心」是目標而非現況，已加註。
  - 星數：2026-11-16 查 GitHub API 為 98,637（筆記寫 97K，差異不大）。最後一次推送是 2026-09-24，重寫版已近兩個月沒有新提交。
  - 任務維持關閉；新資料讓「不做」的理由更充分——要驗證的 MCP 與 Headless 介面根本還沒發布。

---

## 1. 來源摘要與背景脈絡

### 1.1 傳統視訊剪輯軟體的雙重困境
短影音與視訊內容創作已成為數位經濟的核心支柱，然而市面主流剪輯軟體（如剪映 / CapCut）面臨顯著困境：
1. **全面訂閱收費牆（Paywall Escalation）**：原先吸引創作者的語音辨識字幕、高清匯出、降噪、高級特效等基礎功能，逐步被移入昂貴的 Pro 訂閱機制；免費版常伴隨片尾廣告或強制水印。
2. **資料隱私與雲端綁定（Cloud-Lockin & Privacy Risks）**：個人自媒體或企業敏感視訊素材必須上傳至廠商雲端伺服器進行處理，面臨資安洩漏風險。
3. **缺乏現代化 AI 程式化介面（No Agent-first Automation）**：傳統軟體僅設計給人類手工拖曳剪輯，缺乏開放的 API 或標準化通訊協定，無法與當前主流 Coding Agent（Claude Code / Codex / Antigravity）直接整合以達成無人值守自動粗剪。

### 1.2 OpenCut 的定位：開源、無水印、AI 優先
OpenCut 自發布以來迅速引爆開源社群，其核心主張為：
- **完全免費、開源（MIT License）與零水印**：視訊匯出不夾帶片尾，完全開放自由。
- **本機運算（Privacy First）**：所有視訊解碼、濾鏡與合成均在使用者本機運行，素材不離開電腦。
- **架構重塑（The Next-Gen Rewrite）**：正在從頭重寫，規劃以 Rust 為核心並加入 MCP Server 與 Headless 渲染；**這些都還沒推出**。目前可用的是舊版 `opencut-classic`，`opencut.app` 跑的也是舊版，重寫版在 `new.opencut.app`（2026-11-16 依 README 更正）。

---

## 2. 架構核心解構與技術深度

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                       AI Coding Agent                       │
       │           (Claude Code / Codex / Antigravity)               │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         Model Context Protocol (MCP)
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                    OpenCut MCP Server                       │
       │   - 暴露 Timeline API (切分、拼接、調速、音量)              │
       │   - 調用 AI 模型 (fal.ai 多模態圖像/視訊生成)               │
       │   - 控制 In-Editor Scripting 腳本執行                       │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
             ┌────────────────────────┴────────────────────────┐
             ▼ (GUI 互動模式)                                  ▼ (Headless 批次模式)
 ┌───────────────────────────────┐             ┌───────────────────────────────┐
 │   OpenCut 跨端前端 (Web/App)  │             │   Headless CLI / Runner       │
 │   - Next.js / TypeScript UI   │             │   - 無介面背景執行            │
 │   - 多軌視覺化時間軸 (Timeline)│             │   - 批次生成短影音            │
 │   - 即時預覽 (Canvas / WebGL) │             │   - 自動轉碼與壓製            │
 └───────────────┬───────────────┘             └───────────────┬───────────────┘
                 │                                             │
                 └──────────────────────┬──────────────────────┘
                                        │
                                        ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             OpenCut Rust Core (crates/media)                │
       │   - 跨端 GPU 合成引擎 (GPU Compositor)                      │
       │   - 硬體加速解碼 (WebCodecs / FFmpeg 原生綁定)              │
       │   - 特效與遮罩計算 (Filters & Masks)                        │
       │   - 統一支援 Web (WASM)、Desktop (原生) 與 Mobile           │
       └─────────────────────────────────────────────────────────────┘
```

### 2.1 雙層技術棧：TypeScript 上層生態 + Rust 底層運算核心
OpenCut 在重構版架構中採行了清晰的職責劃分（目錄結構已查證存在；但依 issue #778 的討論，Rust 目前只涵蓋匯出流程約三成，其餘仍在 TypeScript，「Rust 統一渲染」是目標不是現況）：
1. **上層應用層（`apps/`）**：
   - `apps/web`：以 Next.js + TypeScript 構建的高響應性現代化前端，實現多軌時間軸拖曳、音訊波形繪製、文字樣式即時編輯。
   - `apps/desktop`：原生桌面端封裝，支援跨 macOS、Windows、Linux 本地執行。
   - `apps/api`：輕量 API 網關與遠端協同模組。
2. **底層媒體引擎（`crates/media`）**：
   - 由 Rust 開發的高效能 GPU 合成器（GPU Compositor），負責畫面疊加、透明度處理、關鍵影格（Keyframe）插值計算與視訊遮罩。
   - 透過 WebAssembly（WASM）將 Rust 核心編譯至瀏覽器端，兼具 Web 的易部署性與接近原生的渲染性能。

### 2.2 專為 AI Agent 設計的 MCP Server 架構
> **2026-11-16 重審註記**：MCP Server 在 README 屬於「即將推出」，尚未發布；社群送過的 MCP PR（#752）沒有合併。本節的工具名稱（`split_clip` 等）、fal.ai 直通與腳本分頁的行為描述都是分析者的推測，沒有出處。

與傳統視訊編輯器最大差異在於，OpenCut 的重寫計畫把 **MCP Server（Model Context Protocol）** 列為規劃項目：
- **工具化時間軸控制（Timeline as Tools）**：Agent 可透過標準工具呼叫執行 `split_clip`、`insert_track`、`apply_transition`、`generate_subtitles`，無須透過脆弱的滑鼠座標點擊（GUI Clicking）。
- **生成式 AI 模型直通（fal.ai Integration）**：深度整合 fal.ai 等多模態服務，Agent 可在時間軸特定標籤位置直接調用生成式影像或音訊填充 B-Roll 鏡頭。
- **編輯器內嵌腳本標籤頁（In-Editor Scripting Tab）**：允許 Agent 生成輕量 TypeScript/JavaScript 腳本，直接在時間軸引擎中運行複雜的程序化動效（如字體彈跳、音量漸變）。

### 2.3 Headless 模式與自媒體工業化自動批次剪輯
> **2026-11-16 重審註記**：Headless 模式尚未存在（README 列為即將推出；issue #827、#778 仍在要求這個功能）。下方的 `opencut render` 指令查無出處，目前不可能可用，請勿照抄。

OpenCut **規劃中**的 Headless Mode（無頭渲染模式），目標是為自媒體矩陣提供工業化能力：
- 脫離瀏覽器與桌面視窗，純以命令列與伺服器行程執行：
  ```bash
  opencut render --timeline ./project.json --output ./final.mp4 --quality 4k
  ```
- 支援透過 JSON 定義整條時間軸結構（包含素材路徑、裁切起止點、轉場特效代碼），Agent 只需產出合法的 Timeline JSON，即可在背景排程批次輸出數十支直式短影音。

---

## 3. 對現有系統的啟發與落差分析

| 評估維度 | OpenCut 開源實踐特徵 | 本知識庫與現有 Agent 體系現狀 | 落地借鑑與改進方向 |
| :--- | :--- | :--- | :--- |
| **視訊編輯生態** | 開源無水印、MIT 授權、多軌時間軸、Rust GPU 渲染 | 目前以程式碼、文字與靜態 Generative UI 為主，缺乏完整視訊編輯層支援 | 將 OpenCut 作為 Code-as-Video 與短影音自動化剪輯之後端基礎設施 |
| **Agent 操作介面** | 規劃提供 MCP Server（尚未發布） | 過去視訊剪輯多需人工作業或呼叫複雜難懂的原始 FFmpeg 參數 | 引入 OpenCut MCP 接口規範，讓 Agent 具備「結構化剪輯時間軸」能力 |
| **自動化渲染** | 規劃支援 Headless 批次渲染（尚未發布） | 既有動態設計（如 Reelbird/Riven 12 大規格）多為前端 Canvas 預覽 | 串聯前端動態代碼與 OpenCut Headless 引擎，實現短影音生產自動化閉環 |
| **多模態生成整合** | fal.ai 是贊助者；「直接回填時間軸」沒有出處 | AI 生成內容（AIGC）與剪輯軟體斷裂，需創作者手動下載上傳 | 制定 AI 素材生成到時間軸自動組裝的標準管線 Prompt 模板 |

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將 OpenCut 的開源多軌剪輯、Rust GPU 渲染與 MCP Server 整合架構納入工程落地，規劃以下 3 項任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261102-07`**｜**[優先級：高]** 撰寫「OpenCut 開源多軌剪輯架構手冊：Rust Core、WebCodecs 本地渲染與 MCP Server 整合規格」收錄於 `docs/opencut-video-editor-architecture-spec.md`
  - **狀態**：⚪ 不做（維護者不用 OpenCut 剪片，上游也在快速變動；時間軸驗證器與 Prompt 範本沒有實際使用情境。）
  - **目標範圍**：`docs/opencut-video-editor-architecture-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 深入剖析 OpenCut 雙層架構（Next.js 前端 + `crates/media` Rust GPU 合成器）與 WASM 渲染管線。
    2. 規範 OpenCut MCP Server 的協議標準（包含時間軸操作、軌道管理、多模態模型擴展）。
    3. 詳解 Headless 無頭渲染模式的 JSON Schema 與命令列呼叫規範。
  - **驗收標準（DoD）**：產出 `docs/opencut-video-editor-architecture-spec.md`，具備標準 Markdown 結構與技術架構圖；以 `Test-Path docs/opencut-video-editor-architecture-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261102-08`**｜**[優先級：中]** 實作「OpenCut Headless 批次剪輯與時間軸 JSON 驗證腳本」於 `tools/verify_opencut_timeline.py` 與單元測試
  - **狀態**：⚪ 不做（維護者不用 OpenCut 剪片，上游也在快速變動；時間軸驗證器與 Prompt 範本沒有實際使用情境。）
  - **目標範圍**：`tools/verify_opencut_timeline.py`、`tests/test_verify_opencut_timeline.py`
  - **具體做法**：
    1. 實作純 Python 版本的 OpenCut 時間軸驗證工具 `tools/verify_opencut_timeline.py`，支援解析 OpenCut 標準時間軸 JSON 格式。
    2. 檢驗項目包含：軌道層級（Tracks）、視訊片段起止時間（In/Out Point）、轉場效果有效性、字幕樣式配置與音訊增益範圍。
    3. 模擬 Headless 渲染排程命令列生成，確保參數符合規格。
    4. 撰寫單元測試套件 `tests/test_verify_opencut_timeline.py`，覆蓋多軌合法時間軸、時間戳重疊異常、缺失素材路徑等情境。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_opencut_timeline.py` 綠燈通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261102-09`**｜**[優先級：低]** 產出標準化「AI Agent 驅動 OpenCut 自動粗剪、字幕生成與分鏡剪輯 Prompt 模板」收錄於 `templates/opencut-agent-editing-prompt.md`
  - **狀態**：⚪ 不做（維護者不用 OpenCut 剪片，上游也在快速變動；時間軸驗證器與 Prompt 範本沒有實際使用情境。）
  - **目標範圍**：`templates/opencut-agent-editing-prompt.md`
  - **具體做法**：
    1. 產出適用於 Claude Code、Codex 與 Antigravity 的視訊自動化剪輯 Prompt 範本。
    2. 包含三大典型情境：訪談長片自動去停頓與粗剪（Silence Removal & Rough Cut）、短影音高潮片段自動卡點抽取（Hook Extracting）、以及自動字幕打標與關鍵詞高亮樣式設計。
    3. 提供符合 OpenCut MCP 工具呼叫格式的標準 Example Payload。
  - **驗收標準（DoD）**：產出 `templates/opencut-agent-editing-prompt.md`，結構清晰且包含變數替換標記；以 `Test-Path templates/opencut-agent-editing-prompt.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
