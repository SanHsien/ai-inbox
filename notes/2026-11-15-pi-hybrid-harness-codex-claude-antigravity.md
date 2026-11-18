---
id: "2026-11-15-pi-hybrid-harness-codex-claude-antigravity"
title: "Agent Harness 深度解析與 Pi 混合型架構設計：串接 Codex CLI、Claude Code 與 Antigravity"
source_url: "https://github.com/paul800901/K-harness"
source_platform: "GitHub"
author: "paul800901（參考目標 404）；核心基準：earendil-works/pi"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
cluster: 1
cluster_role: "混合型Harness"
short_title: "Pi混合型Harness"
source_review: partial
source_reviewed_at: 2026-11-18
source_images: 2
source_replies: 131
source_review_note: "原始來源 paul800901/K-harness 仍是 404，改看上游 pi，所以維持 partial。2026-11-18 試過：GitHub API 與網頁直連、作者 15 個公開 repo 與公開事件紀錄、同名 repo 搜尋、程式碼與 issue 全站搜尋、網頁搜尋、Wayback 存檔，都找不到改名或搬家的去處。替代來源已讀全：pi README 圖 2／2 張；#9361 留言 14／14、#7547 留言 96／96（含長留言全文）、#581 留言 21／21；pi 其餘未關閉的 issue／PR（共 255 個）與本篇無關的沒有讀。2026-11-18 第二輪找存檔與轉引：repo 內容（README、原始碼）仍然讀不到，但在 ecosyste.ms 的公開索引找到它下架前的中繼資料（描述、建立與最後推送日期、8 個標籤、npm 相依清單、3 筆推送事件），網頁搜尋工具的索引裡另有兩段 README 摘要（二手、無法對原文核對）。沒有結果的管道：Wayback（availability API 查 repo 網址與作者頁都沒有存檔；CDX 介面當天回空白、不採計，所以子頁面有沒有存檔未確認）、archive.ph、Software Heritage（查無此 origin）、codeload 原始檔下載（404）、GitHub 同名 repo 與 fork（forks_count 為 0）、全站程式碼與 issue 搜尋、Bing 與 Google 加引號搜尋、Threads／Facebook／X 站內搜尋「K-harness」「K 執行中樞」、Hacker News；Reddit 查不了（內建瀏覽器擋 reddit.com、網頁搜尋工具不能限定該網域、直接請求被擋）"
tags:
  - agent-harness
  - pi-coding-agent
  - codex-cli
  - claude-code
  - antigravity
  - orchestration
  - windows-native
---

# Agent Harness 深度解析與 Pi 混合型架構設計：串接 Codex CLI、Claude Code 與 Antigravity

- **來源連結**：[paul800901/K-harness（目前公開不可存取，API 回 404）](https://github.com/paul800901/K-harness) ｜ [官方上游參考：earendil-works/pi](https://github.com/earendil-works/pi)
- **發布平台 / 作者**：`GitHub` / `earendil-works/pi`（原 `badlogic/pi-mono`，Mario Zechner，MIT License，121,989 stars）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`

> **查證註記**：使用者提供的參考專案 `paul800901/K-harness` 經 GitHub API 與 HTTP 實查皆回傳 `404 Not Found`，且 `paul800901` 公開倉庫清單中亦無該專案（可能已轉私有或移除；[API 回 404](https://api.github.com/repos/paul800901/K-harness) 只能確認目前公開請求不可存取，不能確定已刪除）。2026-11-18 在公開索引找到它下架前的中繼資料：建立於 2026-09-18、最後公開推送 2026-10-22，是 Electron 桌面程式，相依清單裡沒有 pi（見第 0 段）。本分析以 `pi` 官方上游倉庫 `earendil-works/pi` 原始碼與文件（`providers.md`、`cli-integration.md`、`windows.md`、`security.md`、`custom-provider.md`）為事實基準。

---

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**：`paul800901/K-harness` 2026-11-16、2026-11-17 兩次再查都回 404，該帳號 15 個公開 repo 裡也沒有它，README 與圖都看不到。上游 `earendil-works/pi` 的 README 只有標誌與吉祥物兩張小圖和徽章，沒有架構圖或截圖。
  - 2026-11-18 再找一次去處：API 與網頁直連仍是 404；該帳號公開事件紀錄裡沒有任何 K-harness 的推送、建立或改名事件；GitHub 上找不到同名 repo，全站程式碼與 issue 搜尋「paul800901/K-harness」只命中本筆記自己；網頁搜尋與 Wayback 存檔都沒有結果。GitHub 改名會自動轉址，回 404 表示是刪除或轉私有，不是改名。該帳號名稱相近的 `kai-work-host`（網頁版 GPT 連本機執行的工作主機）README 沒有提到 harness、pi 或 Antigravity，無法認定是同一個專案。
  - **2026-11-18 第二輪（找存檔與轉引）：README 與原始碼仍然讀不到，但找到下架前的公開中繼資料。**
    - 來源是 [ecosyste.ms 的 repo 索引](https://repos.ecosyste.ms/api/v1/hosts/GitHub/repositories/paul800901%2FK-harness)（公開的開源套件索引服務，最後同步 2026-10-22）與它的[事件時間軸](https://timeline.ecosyste.ms/api/v1/events/paul800901/K-harness)。
    - repo 描述是「個人自用的 Codex／Claude Code／Antigravity 三核心 AI 工作台；公開原始碼供參考，不承諾維護或支援」。建立於 2026-09-18，最後一次公開推送 2026-10-22，主要語言 JavaScript，約 7.8 MB，0 星、0 fork、沒有授權檔，根目錄有 `README.md` 與 `AGENTS.md`。
    - 有 8 個標籤，集中在 2026-10-01 到 10-04，名稱看得出當時在做的功能：Git 整合、工作區搬移、Antigravity 設定、Gemini 媒體、對話框焦點、依帳號計算 worker 數量。
    - 2026-10-06 的相依清單快照（`package.json` 17 項、`package-lock.json` 307 項）：Electron 44、React 19、Vite 8，加上 `@assistant-ui/react`（聊天介面元件）、`@modelcontextprotocol/server`、`@playwright/mcp`、`ws`、`zod`、`pdfjs-dist`、`mammoth`。**清單裡沒有 pi 的任何套件**，也沒有 OpenAI、Anthropic、Google 的 SDK。
    - 網頁搜尋工具的索引裡還留著 README 的兩段摘要（工具轉述的二手內容，原文讀不到，無法核對）：頁面標題是「K 執行中樞｜通用工作台」；在同一個介面交辦工作，由 Codex、Claude Code、Antigravity 三家原生核心執行，沿用各家官方訂閱與權限，不改走 API 計費；範圍是一般文件、資料與程式工作；三家核心在設定裡各有手動更新按鈕，平常不自動更新，更新時保留舊核心、不動登入狀態。
    - 沒有結果的管道：Wayback 的 availability API 查 repo 網址與作者頁都沒有存檔（CDX 介面當天回空白，連一定有存檔的網址也查不到，不採計；所以 `/blob/...` 這類子頁面有沒有存檔未確認）；archive.ph 沒有；Software Heritage 查無此 origin；codeload 原始檔下載回 404；GitHub 沒有同名 repo 或 fork；Bing、Google 加引號搜尋無結果；Threads、Facebook、X 站內搜尋「K-harness」「K 執行中樞」都沒有相關貼文；Hacker News 0 筆；Reddit 查不了（內建瀏覽器擋 reddit.com，網頁搜尋工具不能限定該網域，直接請求也被擋）。
    - 還缺什麼：README 全文、原始碼、任何截圖。上面只能確認它是什麼類型的東西，不能確認它怎麼接三家核心。
  - 上游 pi 的兩張圖已放大看：圖 1 是三色方塊拼成的 π 字形標誌；圖 2 是版畫風格的河豚吉祥物（Exy）。都沒有技術資訊。
- **作者留言補充**：無（K-harness 看不到）。
- **網友留言重點**（pi 的 issue；2026-11-17 用 `gh api` 把 #9361、#7547 的留言全部讀完，補充寫在各則底下）：
  - [#9361](https://github.com/earendil-works/pi/issues/9361)（未關閉）：Windows 上只要載入擴充，設定檔的 `shellPath` 會不定時被忽略，退回去用 PATH 上第一個 `bash.exe`；有開 WSL 的機器那會是 `C:\Windows\System32\bash.exe`（WSL 啟動器），指令就跑進 Linux 環境。協作者的判斷是某些擴充換掉了內建 bash 工具卻沒讀設定，並承認設定管理沒有好好開放給擴充。
    - **補讀後（14／14 則）根因已經確定，而且不是「不定時」**：只要擴充自己重建 bash 工具而沒把設定傳進去，`shellPath` 與 `shellCommandPrefix` 就一定被丟掉；連官方附的幾個擴充範例都這樣寫。有人在 macOS 重現同一件事，所以設定遺失這一半與作業系統無關。
    - Windows 特有的另一半：有網友用第三方套件穩定重現，該套件直接呼叫 `bash`，而 Windows 找執行檔時會先找 System32，所以一定拿到 WSL 啟動器，根本不會去看 `shellPath`。
    - 外部貢獻者提的修正（[#10538](https://github.com/earendil-works/pi/pull/10538)）被新貢獻者自動關閉的機制關掉、沒有合併；issue 截至 2026-11-17 仍未關閉，最新發行版是 v1.5.2。
  - [#7547](https://github.com/earendil-works/pi/issues/7547)（未關閉，96 則）：協作者彙整 Windows 四種跑法（Git Bash、WSL bash、純 PowerShell、整個放 WSL2），說每一種都有小毛病；有留言說 Git Bash 很糟、WSL bash 常弄壞路徑、PowerShell 相對堪用但很多擴充不支援。
    - **補讀後（96／96 則；2026-11-18 把長留言全文也讀完）**：2026-08-24 維護者宣布下一版加入可選的 PowerShell 工具（[#8512](https://github.com/earendil-works/pi/pull/8512)，預設不開）。之後多位 Windows 使用者回報把 bash 整個關掉、只留 PowerShell 後錯誤明顯變少；也有人測到部分模型在兩個工具都開時仍一律選 bash。
    - PowerShell 工具自己的已知問題：指令太長會在啟動前就被 Windows 拒絕（整段指令塞在命令列參數裡）；系統語言不是英文時輸出可能亂碼。
    - Git Bash 的常見抱怨：模型會寫 `> /dev/null`，在目錄裡留下刪不掉的 `nul` 檔；找不到 `grep` 之類的工具時模型會亂試。維護者的立場是模型的 bash 訓練資料遠多於 PowerShell，不打算把 PowerShell 設成預設。
    - **權限與沙盒**：協作者明講 pi 的立場是預設不做權限控管也不做沙盒，要的人自己找擴充；多位留言者指出 Windows 上沒有開箱即用的沙盒方案，協作者只回了官方沙盒專案的一個 PR 連結（合併狀態本篇未查）。有企業使用者說只好把權限提示當成不完美的替代品。
    - **2026-11-18 讀完長留言後新增**：(1) 內建 PowerShell 工具**會弄丟原生程式的結束碼**：失敗的指令後面只要再接一句，回報的結束碼就是 0，模型會把失敗當成功（有人在 CI 的 Windows 機器上重現，並附修正建議，尚未見合併）。(2) 在 bash 裡呼叫 PowerShell 指令時，`$` 變數會被 bash 先展開，可能把範圍很窄的比對變成很寬，讓破壞性指令影響到預期以外的檔案。(3) 權限類擴充多半沒有包到新的 PowerShell 工具，企業使用者實測「權限擴充配 PowerShell 不能用、Git Bash 配微軟的沙盒工具也不能用」，目前沒有一組整套可用的組合；協作者明講不會做官方的權限參考方案，頂多補沙盒範例。(4) v1.0 起在 Git Bash 內建終端機（MinTTY）啟動會自動跳去開外部編輯器而卡住，官方建議改用 Windows Terminal。(5) 視窗重新取得焦點的那一下點擊會被當成 Enter，若當下正好是確認提示就等於自動按下同意（#10083，被自動歸類為不排程）。(6) 只開 PowerShell 的設定是在 `settings.json` 寫 `"defaultTools": ["read", "powershell", "edit", "write"]`，但 `!` 開頭的手動指令仍走 bash。
    - 安裝面的坑：獨立執行檔舊版在 Windows 找不到 Git Bash（v1.5.0 修掉）；安裝腳本遇到某些 Node 版本管理工具會想另裝一份 Node；更新後 PowerShell 執行原則擋住啟動腳本。
  - [#581](https://github.com/earendil-works/pi/issues/581)（已關閉，2026-01）：Claude 的 OAuth token 在第三方工具回 400，訊息是該憑證只授權給 Claude Code 使用；留言指出其他同類工具也應 Anthropic 要求拿掉這種支援。
    - **2026-11-18 讀完 21／21 則**：有網友抓封包比對，發現同一組憑證不帶工具時能用、帶 pi 的工具名稱就被拒，改掉工具名稱又能用，推斷伺服器端是比對工具名稱。維護者當天先拿掉登入功能，幾十分鐘後又加回來並請大家更新，也就是**用繞過偵測的方式恢復**，不是取得授權；留言者自己都說這隨時會再壞，也有人擔心帳號被停用（之後有人問是否有人被停權，無人回答）。這比原先寫的「功能被拿掉」更值得警惕：功能還在，但用了就是違反服務條款並賭帳號。
- **對分析的影響**：
  1. 第 2 節「Windows 終端與安全邊界」補上 #9361：維護者是 Windows 原生、不用 WSL，而本篇設計正好要寫擴充，這是直接踩得到的問題。
  2. #581 是「不要把訂閱憑證接進 Pi」的實例，補進第 1 節的不建議做法；與 `docs/pi-hybrid-harness-readonly-assessment.md` 的 Anthropic 那一列結論一致，`T-20261115-01` 不需重開。
  3. 結論不變：暫不採納，`T-20261115-02` 維持不做。
  4. 2026-11-18 補讀後結論仍不變，而且多三個不採納的理由：PowerShell 工具回報的結束碼不可靠、Windows 上沒有整套可用的權限加沙盒組合、訂閱憑證登入是靠繞過偵測維持的。
  4. **2026-11-17 補讀後修正第 2 節一句話**：#9361 不是「不定時」發生，而是「裝了會重建 bash 工具的擴充就一定發生」，修正還沒合併。本篇設計正好要自己寫擴充，所以這是寫擴充時必須自己處理的事（把工作階段的 shell 設定明確傳進去），不是等上游修好就沒事。已改第 2 節。
  5. #7547 的 PowerShell 工具回報與 `docs/pi-hybrid-harness-readonly-assessment.md` 第 42 行「可透過 defaultTools 選用 PowerShell」一致，並多了使用者實測：Windows 原生若要試，關掉 bash、只留 PowerShell 是目前回報最穩的組合。協作者「預設不做權限與沙盒」的說法也與該文件「沒有新增強制隔離能力」的結論一致。`T-20261115-01` 不需重開。
  6. **2026-11-18 第二輪：K-harness 不是用 pi 做的。** 依下架前的相依清單，它是一個 Electron 桌面程式（React 介面加 MCP），沒有 pi 的套件。本篇把它當參考目標、卻以 pi 為底座設計，兩者只有「一個介面交辦三家核心」這個目標相同，做法不同。本篇對 pi 的事實查證不受影響，但讀者不應把第 1 節的 pi 雙層設計當成 K-harness 的做法。
  7. 二手摘要說它「沿用各家官方訂閱與權限、不走 API 計費」，方向與第 1 節「只呼叫各家官方 CLI、不碰憑證」一致；實際怎麼接（呼叫 CLI、還是讀憑證）沒有原始碼可查，**未查證**。結論不變：暫不採納，`T-20261115-02` 維持不做。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：Mario Zechner（libGDX 作者）與 Earendil Works 團隊維護的開源專案 `earendil-works/pi`（MIT 授權）。
- **What（什麼是 Agent Harness，以及 Pi 是什麼）**：
  - **Agent Harness（代理外骨骼 / 執行底座）**：大語言模型（LLM）本身只具備「文字進、文字出」的推理能力；**Harness 是把模型包覆起來並接到真實環境的軟體外殼**，負責決定：
    1. **系統提示詞與上下文工程**：模型看得到什麼檔案、工具描述、壓縮（Compaction）與專案記憶。
    2. **工具層（Tools）與權限邊界**：誰能讀寫檔、跑 Shell、做審批攔截、或隔離到容器／Git Worktree。
    3. **代理迴圈（Agent Loop）與狀態機**：Tool call 循環、錯誤重試、Interrupt/Steering 中途插話、Tree-structured 會話分叉。
    4. **外部介面**：終端機 TUI、Headless Print/JSON 串流、長駐 RPC 子程序、或 TypeScript SDK。
  - **Pi 的核心定位（Primitives, Not Features）**：與 Claude Code / Codex CLI 這類高度封裝的重型 Harness 相反，Pi 故意只保留極簡核心（歷史設計描述為預設 `read`、`write`、`edit`、`bash` 4 個工具、低於 1,000 tokens 的系統提示詞；現行版本的完整內建工具集與提示詞 token 數**未查證**，不硬編碼 Plan Mode、Sub-agents 與 MCP），把所有客製邏輯開放給 **TypeScript Extensions / Pi Packages** 組合。
- **Why（為什麼想用 Pi 做「三家混合型 Harness」）**：
  - 單一廠商 CLI 各自有強項與限制：Codex CLI 強在沙盒化大規模寫碼與 Plus/Pro 額度（如 GPT-6.1 Terra）；Claude Code 強在深度架構推理、Hooks 與 Plugin 生態；Antigravity 強在多模型切換、IDE/Browser 雙向整合與 Sidecar 視覺化。
  - 若直接使用各家封閉 Harness，會受限於各自的上下文注入黑箱與 UI 綁定；以 `pi` 為統一底座，理論上可把「互動控制權、樹狀會話與路由邏輯」收歸己有，再依任務特性呼叫三家核心。
- **How（`earendil-works/pi` 的實際架構與三家串接真相）**：
  - **官方內建 Provider 實況（已查證 `packages/ai/src/providers/`）**：
    - 內建 `openai-codex.ts`（ChatGPT OAuth Responses API）、`anthropic.ts`（API key / `ANTHROPIC_OAUTH_TOKEN` / `ANTHROPIC_AUTH_TOKEN`）、`google.ts` / `google-vertex.ts`（API key / Vertex ADC）。
    - **[provider 目錄](https://github.com/earendil-works/pi/tree/main/packages/ai/src/providers)未列 `antigravity`**；這不能證明全倉所有 extension 都沒有相關整合。
    - Pi 支援某個 provider 或 token（見官方 [`providers.md`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/providers.md)），不等於廠商允許第三方工具使用特定訂閱憑證；各家訂閱能否接 Pi **未查證**。
  - **關鍵架構分層（避免違規反代，改用「大腦 + 委派核心」雙層混合）**：
    - ❌ **不建議的做法**：試圖用非官方 OAuth 擷取或反代腳本把三家桌面／訂閱憑證硬接到 `pi.registerProvider()` 當作免費模型 API（易觸發帳號封鎖、且違反憑證安全原則）。實例：pi 的 [#581](https://github.com/earendil-works/pi/issues/581) 記錄 2026-01 起 Claude 的 OAuth token 在第三方工具被回 400，訊息是該憑證只授權給 Claude Code 使用。
    - **待驗證的雙層設計**（只呼叫各家官方 CLI，不碰憑證；是否合規、Pi 控制平面自己用哪個模型、會不會另耗 API 費用，都還沒查證）：

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    Pi Hybrid Harness (本地控制平面)                      │
│  [TUI / RPC / Tree Session / Project Trust / PowerShell+GitBash 工具]    │
│                                                                         │
│  TypeScript Extension (`pi-hybrid-relay`)：                              │
│   ├─ /codex, dispatch_codex() ───────▶ codex.exe (worktree + Terra/Sol) │
│   ├─ /claude, dispatch_claude() ─────▶ claude.exe (深度架構 / Hooks)     │
│   ├─ /agy, dispatch_antigravity() ───▶ language_server.exe / agent-relay│
│   └─ /relay-ask, /relay-inbox ───────▶ SanHsien/agent-relay (ask/answer)│
└─────────────────────────────────────────────────────────────────────────┘
```

- **When & Where（適用時機與環境條件）**：
  - 維護者環境為 **Windows 11 原生（非 WSL）**。依 `pi` 官方 [`windows.md`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/windows.md)，Pi 原生支援 Windows（預設使用 Git Bash，並可設定 `defaultTools: ["read", "powershell", "edit", "write"]` 讓模型直接呼叫 `pwsh.exe`），建議搭配 **Windows Terminal**（避免舊版 `conhost` 全螢幕切換崩潰或字元殘留問題）。
- **Key Metrics / Numbers（客觀事實數據）**：
  - `earendil-works/pi` 預設工具：`read` / `write` / `edit` / `bash`（Windows 可選換為 `powershell`）；「內建工具共 4 個、系統提示詞 < 1,000 tokens」是歷史設計描述，現行精確數字**未查證**。
  - 提供 **4** 種執行模式：Interactive TUI、Print（`--print`）、JSON（`--mode json` JSONL 事件流）、RPC（`--mode rpc` 雙向長駐 JSONL 控制），另附 Node.js/Bun TypeScript SDK。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/agent-relay`（已實作跨機/跨代理信箱與 `ask` / `answer` 非同步決策流，為非同步派工的標準傳輸骨幹）。
  - `SanHsien/agent-cortex`（Windows 原生控制平面與新會話啟動）。
  - `SanHsien/agent-advisor`（風險分級與預設／Flash／Pro 路由策略）。
  - `SanHsien/harness-guard`（執行前／結案前防呆 Hook）。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **樹狀會話（Tree-Structured Sessions）＋ Steering 即時插話**：Pi 允許在單一會話任意節點開分支實驗再回到主幹，這是目前單純使用獨立 CLI session 時最欠缺的「單人極速試錯」體驗。
    2. **Pi 的輕量 Extension 與 RPC 介面**：不需要 fork `pi` 本體，只要寫一個 TypeScript Extension（註冊 `dispatch_codex`、`dispatch_claude`、`dispatch_antigravity` 三個工具與 `/relay` 指令），就能把現有 `agent-relay` 與本機三個核心接進同一個操作面板。
    3. **Project Trust 保護機制**：Pi 遇到工作目錄的 `.pi/extensions`、`.pi/mcp.json` 等可執行設定時會先要求信任決定（`~/.pi/agent/trust.json`），與全域規則「外部擴充零信任」理念相容，但須注意 `AGENTS.md` / `CLAUDE.md` 仍會依設定載入，對外部 repo 仍應保持隔離審查。
  - **不適用 / 需調整的部分**：
    1. **不要用 Pi 重寫一個全新的 `agent-relay` 或 `agent-cortex`**：維護者已經有經過實測的 `agent-relay`（含 `ask`/`answer`、worktree 隔離、SSH 簽章驗證；測試結果以該 repo 當前驗收為準，本筆記未重跑），重複造輪子只會分散維護精力；Pi 應定位為**人類面向的前端指揮台（Commander TUI）＋ 即時編寫工具**，長任務與跨機派工仍交給 `agent-relay`。
    2. **Antigravity 不可透過非官方 API/OAuth 塞進 `pi-ai`**：現有做法是 `agent-relay send --to antigravity --ref antigravity-session:new`，依據是 relay 自己的相容性契約（[`SPEC.md`](https://github.com/SanHsien/agent-relay/blob/main/SPEC.md)），不是 Google 官方保證；`language_server.exe agentapi` 是否為官方穩定 API **未查證**。
    3. **Windows 終端與安全邊界**：Pi 本身沒有內建 OS 沙盒（官方 [`security.md`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md) 明言工具以當前使用者權限執行、工作目錄不限制可存取路徑，project trust 也不是安全邊界）。資料夾與 git worktree 只是分開檔案，**不是 OS 隔離**；在 Windows 上委派破壞性或大規模實作任務時，不要放任 Pi 直接在主分支裸跑。另有未關閉的 [#9361](https://github.com/earendil-works/pi/issues/9361)：擴充只要自己重建 bash 工具而沒把設定傳進去，`shellPath` 就會被丟掉，退回 PATH 上的 `bash.exe`，有開 WSL 的機器會把指令送進 WSL（2026-11-17 讀完全部留言：根因已確定、修正尚未合併，連官方範例擴充都有這個寫法）。本篇設計要靠擴充，在 Windows 原生環境自己寫擴充時要明確把 shell 設定傳進去，或依 #7547 多位使用者的做法關掉 bash、只留 PowerShell 工具。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-01`**｜**[優先級：低]** 唯讀評估 Pi 在 Windows 原生環境的安全、訂閱授權與現有 agent-relay 分工，不安裝或連接帳號
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/pi-hybrid-harness-readonly-assessment.md`。
  - **具體做法**：固定 Pi commit，唯讀檢查 package／lockfile、安裝入口、extensions、providers、security 與 Windows 文件；區分作業系統隔離、project trust 與 worktree。對照現有 relay／advisor 已有能力，列真正新增的使用者價值。逐家列官方 CLI 委派與直接 provider 授權／費用的差別，確認不了就記未查證；不擷取憑證、不測 OAuth、不跑第三方腳本。
  - **驗收標準（DoD）**：產出上述報告，含固定 commit／來源 URL、安裝期與執行期風險、Windows 前提、三家授權證據狀態、既有能力重疊表與採納／不採納結論。不得承諾免費訂閱接入，不得把資料夾或 worktree 稱作 OS 沙盒；對本報告相關文件變更執行 repo 規定檢查並保存命令與結果。**不以未安裝當作本任務缺件，也不宣稱通過動態實測。**
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/pi-hybrid-harness-readonly-assessment.md，固定 earendil-works/pi c3cc916。安裝期有 husky prepare 與 8 個 install script；執行期 worktree 不是 OS 隔離；三家訂閱授權證據狀態逐家列出；與 agent-relay／advisor 能力重疊；結論暫不採納。唯讀評估，Codex 撰寫，整合者重產索引並補驗證段；Fable 獨立複審抽查來源事實全部吻合；未執行任何第三方程式。

- [ ] **`T-20261115-02`**｜**[優先級：低]** 實作 Pi 混合型擴充套件 `pi-hybrid-relay`（於 Pi 內統一委派 `codex` CLI、`claude` CLI、Antigravity 頂層對話與 `agent-relay` 問答）
  - **狀態**：⚪ 不做（2026-11-15 獨立審查：依賴的 T-20261115-01 尚無採納結論；一次包四種委派、工具 Hook、TUI 與跨機回收，成本遠超介面實驗，且現有 relay／cortex 已處理派工。日後確認有 UI 痛點，再提單一 relay 包裝切片）
  - **目標範圍**：新建 `C:\GitHub\pi-hybrid-harness`（對應 `SanHsien/pi-hybrid-harness`）或作為 `agent-relay` 擴充套件（依 `T-20261115-01` 結論定案）
  - **具體做法**：
    1. 以 TypeScript 撰寫 Pi Extension，透過 `pi.registerTool` 與 `pi.registerCommand` 封裝四項核心能力：`dispatch_codex`（強制 worktree 與可選 Terra 模型路由）、`dispatch_claude`（呼叫 `claude -p` 或 `claude --bg`；後者未查證）、`dispatch_antigravity`（呼叫 `agent-relay send --to antigravity --ref antigravity-session:new`）、以及 `relay_questions`（串接 `agent-relay inbox --questions` 與 `answer`）。
    2. 實作 `tool_call` 安全攔截 Hook，對高風險刪除／跨 repo 寫入要求二次確認。
    3. 補齊 TypeScript 型別檢查與單元／整合測試。
  - **驗收標準（DoD）**：在 `T-20261115-01` 通過前提下，於 Pi TUI 實測成功透過 extension 工具各委派一次任務並收回結果，且型別檢查與測試全綠、推送至 `SanHsien` 個人 repo。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
