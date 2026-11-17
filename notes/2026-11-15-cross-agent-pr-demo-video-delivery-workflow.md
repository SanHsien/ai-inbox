---
id: "2026-11-15-cross-agent-pr-demo-video-delivery-workflow"
title: "跨 Agent PR + Demo 影片交付工作流評估：Grok Bot 案例拆解與本機免新 Repo 整合方案"
source_url: "https://www.aiposthub.com/grok-bot-cursor-coding-pr-video-update/"
source_platform: "Blog / AI Post Hub"
author: "Philo／AI Post Hub（Grok Bot + Cursor Cloud Agent 案例）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
cluster: 1
cluster_role: "PR錄影證據交付"
short_title: "跨Agent PR錄影交付"
source_reviewed_at: 2026-11-17
source_review: full
source_images: 4
source_replies: 0
tags:
  - pr-automation
  - demo-video
  - playwright
  - ffmpeg
  - gh-cli
  - agent-relay
  - cross-agent-workflow
---

# 跨 Agent PR + Demo 影片交付工作流評估：Grok Bot 案例拆解與本機免新 Repo 整合方案

- **來源連結**：[AI Post Hub: Grok Bot + Cursor PR 與 Demo 影片工作流](https://www.aiposthub.com/grok-bot-cursor-coding-pr-video-update/)
- **發布平台 / 作者**：`AI Post Hub` / `Philo`（2026-10-01）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-17 用瀏覽器重看 AI Post Hub 原文：3 張圖都放大看過，內嵌的 1 支 YouTube 影片讀了字幕（計入圖片數，共 4）；同日另把影片每 7 秒抽一格、共 16 格看過畫面。文章沒有留言區。

- **作者圖片**（文章署名 Philo，2026-10-01；圖片都轉自官方）：
  - 圖 1（官方公告示意圖，文中出現兩次）：桌面 App 對話。使用者要求 Cursor 專案修復 CSV 匯出逾時 → Bot 回「已交給該專案」→ 回報完成，附兩個 PR（分批串流匯出、加匯出進度提示）與一段 14 秒的操作影片縮圖（進度條 64%）→ 使用者說看起來可以、出貨 → Bot 回報兩個 PR 已 squash 合併到 main。畫面裡**沒有測試結果**。
  - 圖 2（官方工程指南）：手機畫面，Bot 回報一張 PR 卡片（Done、11 個檔案、+439／-17，有「View PR」「Open in Cursor」按鈕）；下一則訊息卻寫同一個 PR「仍是草稿、CI 還是紅的」。
  - 圖 3（官方工程指南）：共享表格的 PR 追蹤板，欄位是任務名稱、負責的 Bot、階段（Working／Watching 3/3／Ready for review）、PR 編號。
  - 影片（官方產品介紹「Introducing Grok Bot」，1 分 46 秒，2026-08-11 上傳）：使用者訪談式宣傳片，講 Bot 在自己的雲端電腦上工作、可互相交辦。畫面是辦公室實景與受訪者，穿插幾個介面特寫：各人的 Bot 名稱與一句用途（整理大量信件、學會並重做複雜流程、在雲端自己工作、產生客戶素材）、「Teach a task」按鈕、聊天訊息（從筆記找資料做日文簡報）。**畫面裡沒有 PR 卡片，也沒有錄影交付的示範**，與字幕一致，對本篇沒有新資訊。
- **作者留言補充**：無（文章沒有留言區）。
- **網友留言重點**：無（文章沒有留言區）。
- **對分析的影響**：
  - 圖 2 是官方自己的圖，卻顯示「卡片標 Done、CI 仍紅」；這比文字更直接支持本篇「不可只錄影不測」「Demo 影片不等於測試通過」的閘門順序。已補進第 1 節 Why。
  - 圖 1 的流程是使用者看完影片就讓 Bot 合併到 main，沒有任何測試證據；`pr-demo-evidence` 技能要求先有測試通過證據再錄製，方向正確。
  - 圖 3 的「階段」欄（Watching n/3、Ready for review）是可參考的追蹤欄位設計，但 `T-20261115-13` 已判定不做，不重開。
  - 補上文章作者與日期（原筆記只寫站名）。其餘結論與任務不變。
  - 2026-11-17 補看影片畫面後確認：影片與 PR／Demo 影片交付無關，分析不用改。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：Grok Bot 整合 Cursor Cloud Agent，將傳統「Agent 回報我改好了」升級為「**自動拆解派工 $\rightarrow$ 開出 PR $\rightarrow$ 附帶實機操作 Demo 影片與修改摘要 $\rightarrow$ 人類審核合併**」（官方示範為修復 CSV 匯出逾時，帶回 2 個 PR、進度提示與 1 段操作 Demo；這是產品示意，不是可重現的修復 benchmark。[xAI 工程指南](https://x.ai/bot/guides/grok-bot-for-engineering)支持「委派 Cursor、查看 PR 證據」這個流程，不能據此證明修復品質）。另介紹官方 Engineering Bot 角色範本（Projects Manager / QA Bot / Engineering Lead / Nightly Audit Engineer）。
- **Why**：單純「貼 Diff + 說我改好了」讓人類驗收成本極高；附帶操作影片能讓 PM、設計師或忙碌的維護者幾十秒內確認畫面行為是否符合預期（但貼文亦誠實提醒：**Demo 影片 $\neq$ 測試通過**，邊界條件與權限仍須靠測試與 Code Review）。文中轉載的官方工程指南截圖就有一例：PR 卡片標示 Done，下一則訊息卻說同一個 PR 仍是草稿、CI 還是紅的。
- **How（跨 Agent 通用等效技術拆解，非 Grok Bot 專利）**：
  - 經實查業界開源實作（Playwright `recordVideo`、Testreel / Argo、`charmbracelet/vhs`）與本機工具現況，支援 Tool Use / Shell 的 Agent（Claude Code、Codex CLI、Antigravity、Hermes、Pi）理論上可共用下面這套流程。這是規格目標：各 agent 的錄影、檔案讀取、技能載入位置與權限都還沒逐一實測。

```text
[任一 Agent 完成實作 (Claude / Codex / Antigravity / Hermes)]
       │
       ├─ 1. 確定性測試閘門：跑通單元／整合測試並輸出 Log（不可只錄影不測）
       │
       ├─ 2. 視覺證據錄製（依介面類型擇一）：
       │     ├─ Web UI：Playwright BrowserContext({ recordVideo }) ─▶ .webm
       │     └─ CLI / 終端工具：charmbracelet/vhs 或 asciinema
       │
       ├─ 3. 後製壓縮：本機 ffmpeg.exe (已安裝 9.0.2) 轉輕量 .mp4 (去空白幀 / 控制檔案大小)
       │
       └─ 4. 交付閉環：
             ├─ 單倉 PR：gh pr create --attach ./demo.mp4 (本機 gh 2.104.0 的 help 有此旗標；未實際上傳驗證)
             └─ 跨代理派工：agent-relay send --kind result --ref <PR_URL>   (--ref 可重複；不是 --refs)
```

> **`--ref` 只存字串，不會上傳檔案**：[`cli.py`](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/cli.py#L670) 定義的是可重複的單數 `--ref`，[envelope](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/envelope.py#L165) 只保存 refs 字串。寫本機 mp4 路徑不等於跨機附件，另一台機器未必讀得到；要跨機就給 PR URL 或共享儲存位置。

---

## 2. 本機與開源資源盤點（2026-11-15 實查）

- **本機已就緒的零成本工具鏈（無須新裝重型平台）**：
  1. **`gh` CLI `2.104.0`**：本機 help 與[官方手冊](https://cli.github.com/manual/gh_pr_create)都有 `--attach` 旗標，可把影片／圖片附到 PR。首次引入的版本（原稿寫 2.99.0）與檔案大小上限（原稿寫 100 MiB）未查證；本筆記沒有實際上傳過。
  2. **`ffmpeg` `9.0.2-full_build`**（已安裝於 WinGet 目錄）：負責 `.webm` $\rightarrow$ `.mp4` 轉檔、裁切無效等待幀與壓縮體積。
  3. **`playwright.exe`**（已安裝於 `C:\Python314\Scripts\playwright.exe`）：透過 `recordVideo` 錄製可重現的操作影片。可執行檔存在不代表瀏覽器 runtime 與錄影全流程已通，未實測。
- **開源生態補充資源（僅作參考，採納前須經審查）**：
  - `greentfrapp/testreel`（108 stars）：LLM 透過 Playwright 錄製產品展示影片。
  - `howseen-ai/claude-motion-design`（826 stars）：HTML + Playwright + ffmpeg 純程式動態展示。
  - `charmbracelet/vhs`：以 `.tape` 宣告式腳本錄製 CLI 終端操作影片／GIF（適合 `agent-relay`、`agent-advisor` 這類純 CLI 工具）；在 Windows 的安裝相依性未驗證。

---

## 3. 關鍵決策評估：是否獨立成 Repo？是否優先處理？

1. **是否需要獨立建立一個新的 Repo？— 結論：`不需要`（避免過度工程）**：
   - 錄影與上傳底層（Playwright + FFmpeg + `gh pr create --attach`）皆已是成熟單兵工具且本機已就緒；派工與交接骨幹（worktree 隔離、`result` 回報、`accept` 本地複驗）已在 `SanHsien/agent-relay`；跨 Agent 通用規範則由共用 Skills 與 `SanHsien/agent-assets`（私有）管理。
   - 若僅為了串接這三個 CLI 指令就另開一個新 Repo，只會增加多餘的版本同步與維護負擔。**最乾淨的落地方式是「寫成跨 Agent 共用的 `pr-demo-evidence` Skill（配輕量共用腳本）＋ 在 `agent-relay` 的 `result` 用既有 `--ref` 引用證據」**（relay 本身不用改，`T-20261115-13` 已關閉）。
2. **是否需要優先處理？— 結論：`中優先級`（高槓桿驗收升級，排在主線穩定之後）**：
   - `agent-relay` 剛完成 `ask`/`answer` 非同步問答，核心文字派工與自動化測試驗收已暢通；PR Demo 影片對「有 Web UI／前端展示／未來接案交付給客戶看」的案型價值最高，列為**中優先級**，可搭配下一個前端專案推進。

---

## 4. 拆解待辦事項（Action Items）

- [x] **`T-20261115-12`**｜**[優先級：中]** 建立以假資料錄影與離線驗收為核心的 PR Demo 證據技能，明確分開錄製、引用與上傳
  - **目標範圍**：`SanHsien/agent-assets`（私有）；預定新增 `skills/pr-demo-evidence/SKILL.md`、`skills/pr-demo-evidence/scripts/compress-demo.ps1`、`skills/pr-demo-evidence/examples/demo.html`、`skills/pr-demo-evidence/VALIDATION.md`。這些是建議新增路徑，本輪未查其是否已存在。
  - **具體做法**：先讀 SSOT repo 指引、確認現有技能是否重複。依 agent-safety-checks 的螢幕／錄影隱私規範，先限制為本機合成測試頁、獨立 context、無登入與假資料；錄製前完成許可判斷，錄製後依規範檢查，不合格素材丟棄。以已安裝 Playwright 與 ffmpeg 做一筆最小錄製／壓縮；未安裝所需元件就停，不下載。文件示範 gh 的顯式 `--repo SanHsien/<repo>` 與重複 `--ref`，區分 PR URL 與僅本機可讀路徑。
  - **驗收標準（DoD）**：先有測試通過證據再錄製；影片可完整解碼、具有非零時長與預期尺寸，大小低於技能設定上限，並記實際工具版本。至少驗證一個壞輸入／轉檔失敗案例，保留原檔且回非零碼；隱私檢查與清除期限有紀錄。上述 VALIDATION.md 列來源 SHA、執行命令、影音摘要與限制；實際影片保存在 repo 外。不得把 help 支援旗標寫成上傳成功；本任務不建立 PR、不上傳、不派 relay 工單、不寫全域 `~/.gemini`／`~/.claude`／`~/.codex` 設定，安裝同步另依各 agent 載入契約處理。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15，SanHsien/agent-assets（私有） main 6d3ab8d、f808065、2d3312c、eceedf0，CI 綠）：skills/pr-demo-evidence（SKILL.md、scripts/record-demo.py、scripts/compress-demo.ps1、examples/demo.html、VALIDATION.md）＋25 項測試，ASSET_REGISTER 登記為候選、未核准發布。用系統 Edge 157 以 headless 逐格截取頁面＋系統 ffmpeg 實錄，h264 1280x720、2.4 秒、完整解碼結束碼 0。錄前錄後都做隱私檢查且 fail-closed：fill 值、表單值、短暫文字、iframe／img／XHR 讀本機檔、optgroup label、open shadow root 等反例都會擋下並刪檔。Fable 獨立複審兩輪通過。限制：Playwright 內建錄影器（--capture video）未實測，closed shadow root 與 CSS content 看不到，gh 附件旗標未實測。不建 PR、不上傳。

- [ ] **`T-20261115-13`**｜**[優先級：低]** 評估於 `SanHsien/agent-relay` 的 `result` 回報與 `accept` 驗收清單支援顯示 Demo 影片附件路徑（`refs` / `result` 證據整合，不另開 Repo）
  - **狀態**：⚪ 不做（2026-11-15 獨立審查：envelope@1 已接受 refs 字串、CLI 已有可重複的 --ref，沒有無法保存或讀取影片引用的反例，也沒有高亮顯示的使用需求與驗收案例；先由 T-20261115-12 說明證據交付方式，不改 protocol 或 accept）
  - **目標範圍**：`C:\GitHub\agent-relay`（`SPEC.md`、`agent_relay/cli.py`）
  - **具體做法**：
    1. 評估在派工 `task`（如 UI/前端任務）可選擇要求 Worker 回傳的 `result` 信封於 `refs` 附上錄影檔路徑或含 `--attach` 影片的 PR URL，於 `relay read` / `relay accept` 時高亮提示人類審閱該視覺證據。
  - **驗收標準（DoD）**：確認擴充方案不破壞既有 `envelope@1` 相容性，並通過 `agent-relay` 單元測試與 doc parity。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
