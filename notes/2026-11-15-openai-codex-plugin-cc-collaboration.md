---
id: "2026-11-15-openai-codex-plugin-cc-collaboration"
title: "openai/codex-plugin-cc：在 Claude Code 內直接叫用 Codex 協作與對抗式審查評估"
source_url: "https://be-ai-curator.com/blog/claude-code-codex-collaboration"
source_platform: "Blog / GitHub"
author: "OpenAI (openai/codex-plugin-cc) & be-ai-curator"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
cluster: 3
cluster_role: "Codex插件協作"
short_title: "CodexPluginCC雙AI協作"
source_review: partial
source_reviewed_at: 2026-11-16
source_images: 16
source_replies: 18
source_review_note: "部落格全文與 6 張圖已看、文末無留言區；Threads 輪播 11 張看了 10 張圖，第 7 張是影片只看到封面；Threads 留言讀到 18 則／共 85 則（其餘要登入）；README 示範影片與 Instagram Reel 未看；外掛 issue 只看留言最多的 8 則標題"
tags:
  - claude-code
  - codex
  - codex-plugin-cc
  - adversarial-review
  - multi-agent
  - ssot
---

# openai/codex-plugin-cc：在 Claude Code 內直接叫用 Codex 協作與對抗式審查評估

- **來源連結**：[openai/codex-plugin-cc (GitHub)](https://github.com/openai/codex-plugin-cc)（Apache-2.0，35,129 Stars，為查詢當下快照）｜ [Claude Code × Codex 協作長文 (be-ai-curator，No.73，2026-10-01)](https://be-ai-curator.com/blog/claude-code-codex-collaboration)｜ [同篇 Threads 圖文版](https://www.threads.com/@be.ai.curator/post/Dd84mwfkZ2Z)
- **發布平台 / 作者**：`GitHub / Blog` / `OpenAI` & `be-ai-curator`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（模型燒額度分權矩陣）
  - [`notes/2026-11-15-multi-ai-20-dollar-role-routing-anti-fake-green.md`](./2026-11-15-multi-ai-20-dollar-role-routing-anti-fake-green.md)（多 AI 角色路由與反假綠燈）

---

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**：
  - 部落格 6 張（2026-11-16 看）：封面、書桌、雙視窗、模型層架 4 張是情境插畫，沒有額外資訊；「示範過程」圖左邊是 Codex 畫的 5 張拼貼素材（人物、兩個視窗、圓餅、紅筆箭頭、牛皮紙），右邊是 Claude 拼成的片段；「海報」圖是 Codex 內建生圖畫的秋季咖啡活動海報，中文標題字沒有亂碼。
  - [Threads 同篇貼文](https://www.threads.com/@be.ai.curator/post/Dd84mwfkZ2Z)輪播 11 張：1 選邊還是串起來；2 兩邊都用最累的是人；3 人只待在 Claude（畫面出現 `/codex:rescue`）；4 為什麼待在 Claude（旗艦燒得快）；5 桌面版三步驟（設定→外掛、加入 OpenAI 的 Codex、跟 Claude 說幫我設定 Codex）；6 Vox 短片五步分工；7 示範短片（影片，只看到封面，註明素材 Codex 畫、動態與剪接 Claude）；8 做完請 Codex 挑毛病（`/codex:adversarial-review`）；9 用到 OpenAI 功能交給 Codex；10 兩個 AI 讀同一份 `CLAUDE.md`；11 導流到長文。
- **作者留言補充**（Threads 串文 5 則＋回覆）：
  - 桌面版不用打指令的三步驟；免費 ChatGPT 方案也能用外掛，但要 Codex 畫素材得是付費方案。
  - 回覆網友：網頁版也能用外掛，但拿不到本機的共同規則，做法是把規則放進一個 repo。
  - 回覆網友：可以叫 Claude 與 Codex 互相討論到雙方同意（只有一句話，沒有示範）。
- **網友留言重點**（讀到 13 則）：多數是道謝與留言「協作」索取連結。有用的一則是 `@tnstiger`：交給另一個模型畫素材時，除了畫面描述還要寫明這張圖在影片裡要說明什麼，審片時才判斷得出該換圖還是改分鏡。`@ckk225403` 問網頁版能否使用（作者回覆見上）。沒有人回報安裝失敗或用量數字。
- **外掛 repo**：README 只有一支示範影片（未看）。未關閉的 issue／PR 共 544 個，留言最多的幾則都在修 broker 與背景工作殘留（如 #541、#652、#836、#623），只看了標題；與 `docs/codex-plugin-cc-readonly-assessment.md` 記錄的「三條呼叫鏈都沒有逾時」方向一致。指令目錄現有 8 個指令，含 `transfer`。
- **對分析的影響**：
  1. 原筆記寫「be-ai-curator 原文與此成本優勢均未查證」。這次原文讀得到，已改寫第 1 節：成本說法是作者自述的使用經驗（文末「資料查核」段自己標明），不是量測。
  2. 第 1 節的指令清單補上文章主推的 `/codex:transfer`，並更正 `/codex:rescue` 的定位：文章把它當「整包交辦」用（例如畫素材），不只是卡關救援。
  3. 「Claude Desktop 安裝流程未查證」改為：文章有寫出步驟，本機仍未實測。
  4. 「規則一致性」補上文章的具體做法（Codex 設定 `project_doc_fallback_filenames`）與「同層有 `CLAUDE.md` 時 Claude Code 會略過 `AGENTS.md`、可在 `CLAUDE.md` 寫 `@AGENTS.md` 匯入」的說法；後者與維護者現行做法相同，但屬作者引用官方文件的轉述，本篇未另查。
  5. 已完成的 `T-20261115-15` 報告已涵蓋 `transfer`（會送出整份對話紀錄），不需重開。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：OpenAI 官方開源插件 `openai/codex-plugin-cc`（Apache-2.0），讓使用者不必在 Claude 與 ChatGPT/Codex 雙視窗間來回複製貼上背景脈絡，直接在 Claude Code（含桌面 App Code 分頁）內呼叫 Codex 執行任務與程式碼審查。
- **Why（解決什麼痛點）**：
  - 單一模型自寫自審容易產生盲點，而雙視窗人工貼背景則會打斷專注力、浪費上下文重建時間。
  - 文章作者宣稱：高階旗艦模型（如 Fable、GPT-6 Astra）在簡單任務過度發散時極易燒爆週用量；日常改以 **Claude Opus 5.5** 為主力規劃與實作，僅在需要第二意見或 OpenAI 專屬能力時呼叫 Codex。原文 2026-11-16 已讀到：作者自述兩邊都訂 200 美元方案，舉例「30 秒短片 Claude 花 12 分鐘、用掉 Max 20x 週用量 1%」，並在文末標明這些用量與「Opus 5.5 完勝 GPT-6.1 Sol」都是個人使用經驗，不是量測；本篇同樣只當作者宣稱。
- **How（核心運作機制與指令）**：
  1. **安裝方式**：依[官方 README](https://github.com/openai/codex-plugin-cc/blob/main/README.md)，前置為 Node.js 18.18 以上，以及可用的 Codex 安裝與驗證（ChatGPT 訂閱含 Free，或 OpenAI API key）；步驟為加入市集（marketplace add）、安裝插件、重新載入、執行 `/codex:setup`。只有 ChatGPT 帳號不等於前置全部滿足。插件沒有額外的獨立額度，用量計入 Codex 用量上限（見[官方定價入口](https://developers.openai.com/codex/pricing)）；README 沒有依方案區分生圖功能的說法。Claude Desktop 的安裝流程，文章寫的是「設定 → Plugins → Add marketplace 輸入 `openai/codex-plugin-cc` → 找到 Codex 按 Add → 回 Code 分頁請 Claude 設定 Codex」，並說外掛只在 Code 分頁有效；本機未實測。文章另稱免費 ChatGPT 方案不能用 Codex 內建生圖（作者引用 OpenAI 文件，本篇未另查）。
  2. **核心斜線指令**：
     - `/codex:review`：標準 Code Review（支援 `--background` 背景執行）。
     - `/codex:adversarial-review`：對抗式審查，請沒有參與撰寫過程的 Codex 從反方挑出隱含假設與邊界漏網。
     - `/codex:rescue`：把一件事整包交給 Codex 做。官方定位是卡關或測試失敗時交棒；文章主要拿它交辦生圖素材。
     - `/codex:transfer`：把目前整段對話轉到 Codex 接手（文章有實測；會送出整份對話紀錄，見 `docs/codex-plugin-cc-readonly-assessment.md`）。
     - 文章提醒：`/codex:adversarial-review` 審的是 repo 裡還沒提交的改動，要審的檔案得放在 git repo 裡；本機 Codex 版本太舊會報錯。
  3. **多媒體與平台功能接力（文章作者提出的應用構想，不是插件內建的生成能力）**：如 Vox 風格短片由 Claude 規劃分鏡與動畫程式碼，將「生圖素材」或「OpenAI Realtime 語音模組」交給 Codex 產出後再拼回專案。
  4. **規則一致性**：透過 GitHub Repo 維護同一份規範說明書（Instructions），讓 Claude 與 Codex 讀取相同專案約束（網頁版無法讀取本機規則檔時亦可透過 Repo 同步，出自作者在 Threads 的回覆）。文章的具體做法：專案只放一份 `CLAUDE.md`，在 `~/.codex/config.toml` 加 `project_doc_fallback_filenames = ["CLAUDE.md"]` 讓 Codex 找不到 `AGENTS.md` 時改讀它；已有 `AGENTS.md` 的人則在 `CLAUDE.md` 寫一行 `@AGENTS.md` 匯入。後者就是維護者現行做法。
- **When & Where**：日常以 Claude Code 為主工作台，需要跨模型對抗審查、卡關救援或整合 OpenAI 原生生態工具時。

---

## 2. 啟發與適用性評估

- **與現有本機基建的高度共鳴與對照**：
  1. **「共讀同一份說明書」已落地為 `SanHsien/agent-assets`（私有）SSOT**：本機已建置 `C:\GitHub\agent-assets`（入口 `rules/AGENTS.md` 與 `knowledge/`），正是跨 Claude / Codex / Antigravity / Hermes 共用規則的單一真實來源。
  2. **跨代理協作與跨模型審查已有現有架構**：
     - **跨模型審查**：本機已有 `ai-review` Skill（預設走 Codex CLI 做二審）與 `SanHsien/agent-advisor`。
     - **跨代理派工**：本機已有 `SanHsien/agent-relay`（含 `ask`/`answer`、worktree 隔離與合併閘門）。
  3. **`openai/codex-plugin-cc` 的互補定位**：當使用者單純停留在 Claude Code CLI 或 Claude Desktop 內工作、不想額外啟動 `agent-relay` 派工管線時，官方插件提供 `/codex:adversarial-review` 與 `/codex:rescue` 的對話內入口；切換成本未量測。插件是 Codex app-server 的包裝，既有認證與設定仍須逐項檢查（見[官方整合說明](https://github.com/openai/codex-plugin-cc/blob/main/README.md#codex-integration)）。
- **實查邊界與避坑提醒**：
  - **「Codex 畫素材」的前提**：`codex-plugin-cc` 本身是 Code Review 與任務委派外掛，並非獨立繪圖模型；能否生圖取決於 Codex 端自身的工具與帳號權限，無法從插件功能推導，本篇未查證。
  - **避免職責重疊與環境衝突**：若同時啟用 `codex-plugin-cc` 與本機 `agent-relay`／自訂 hooks，應先確認兩者的 hook 生命週期與 Codex CLI 認證路徑不互相干擾。插件的 [`hooks.json`](https://github.com/openai/codex-plugin-cc/blob/main/plugins/codex/hooks/hooks.json) 註冊 SessionStart、SessionEnd、Stop 三個 hook。
  - **成本風險（review gate）**：README 明示選用的 [review gate](https://github.com/openai/codex-plugin-cc/blob/main/README.md#enabling-review-gate) 可能形成長迴圈並快速耗盡用量；評估時維持關閉。安裝後看得到斜線指令，不算完整的相容性證據。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-15`**｜**[優先級：低]** 唯讀評估 codex-plugin-cc 與既有 ai-review／agent-relay 的 Windows 權限與 hook 邊界，決定是否值得另案試用
  - **目標範圍**：本 repo `docs/codex-plugin-cc-readonly-assessment.md`；僅讀已安裝工具的非機密規格，不修改 Claude／Codex 全域配置或 hooks。
  - **具體做法**：固定官方 plugin manifest、hooks、啟動 wrapper、app-server 權限處理與依賴宣告之版本／SHA。追查 review、adversarial-review、rescue 三條呼叫鏈，列 sandbox、approval、模型／effort 選擇、背景工作取消與資料落點；辨別 policy 與實際 runtime 證據。檢查是否有禁止的 bypass 旗標、自動安裝、憑證外傳或隱性 Stop review gate 迴圈。以現有 ai-review／agent-relay 文件比對用途，不啟動任一模型後端，不安裝插件、不登入、不啟用 gate。只有明確缺口才建議後續最小實測。
  - **驗收標準（DoD）**：上述報告存在，提供三條呼叫鏈對照、來源 SHA、Windows 已知限制、與現有工具重疊／缺口，以及採納裁決。禁止用「沒看到衝突」取代相容性驗收。若建議另案實測，規格限一個隔離測試專案、一次 readonly adversarial-review 及一次最小 rescue；不跑多工具模型基準，必須明列用量未知的情況、timeout、取消及停止條件，維持 optional review gate 關閉。登入／UI 若必要由維護者處理；不能把登入完成視為整體實測成功。第三方安全審計未通過不建議安裝。後續實作需更新 ROADMAP、重建 README 並通過 verify_inbox；本任務不產生「已安裝／無衝突／比較省額度」的 runtime 宣稱。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/codex-plugin-cc-readonly-assessment.md，固定 openai/codex-plugin-cc db52e28（1.0.6），22 個 blob SHA。三條呼叫鏈對照：review／adversarial 為 read-only；rescue 可由模型主動觸發，預設 workspace-write；三鏈都沒有逾時。Stop hook 無條件註冊，gate 開啟後非 ALLOW 全擋且不查 stop_hook_active。上游 CI 只跑 ubuntu。agent-safety-checks --pack 結束碼 0（7 項人工審查已讀）。用途與 ai-review、agent-relay 重疊；裁決現階段不安裝，附另案實測規格與停止條件。Fable 撰寫，Fable 獨立複審後修正用語；唯讀評估，未安裝、未生圖、未啟動模型。
