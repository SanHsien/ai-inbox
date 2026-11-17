---
id: 2026-10-24-feedback-desk-client-ticket-ai-handoff
title: "feedback-desk 解構：客戶開單 × 多 AI 認領與交接的輕量工單系統（Cloudflare Workers 免費版／Laravel 主機版）、MCP 接入 Claude Code 與 Codex，及與本地交接機制的對照"
source_url: "https://www.facebook.com/groups/1224997379198346/posts/1423750565989692/"
source_platform: "Facebook 社團（Claude Taiwan）/ Threads / GitHub"
author: "aixwangtw（部落格：aixwang.dev）"
github_repo: "https://github.com/aixwangtw/feedback-desk"
analyzed_at: 2026-10-24
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: "1"
cluster_role: "A2A 通訊與協同工作區"
short_title: "feedback-desk 客戶工單與 AI 交接"
source_review: full
source_reviewed_at: 2026-11-18
source_images: 11
source_replies: 4
tags:
  - feedback-desk
  - ticketing
  - ai-handoff
  - mcp
  - cloudflare-workers
  - claude-code
  - codex
---

# feedback-desk 解構：客戶開單 × 多 AI 認領與交接的輕量工單系統（Cloudflare Workers 免費版／Laravel 主機版）、MCP 接入 Claude Code 與 Codex，及與本地交接機制的對照

- **來源連結**：[GitHub aixwangtw/feedback-desk](https://github.com/aixwangtw/feedback-desk)；作者介紹文：[aixwang.dev/blog/feedback-desk](https://aixwang.dev/blog/feedback-desk/)（介紹文我未讀取，內容以貼文與 repo README 為準）
- **發布平台 / 作者**：`Facebook 社團（Claude Taiwan）` + `Threads` + `GitHub` / `aixwangtw`（王士麟；2026-11-18 更正：內容對得上的原貼文在 Facebook 社團，不是 Threads）
- **查證數據（2026-10-24 以 GitHub API 取得）**：MIT 授權、TypeScript、約 31 Stars、最後推送 2026-10-20、分支 `main`（Cloudflare 版）／`cloudflare`／`laravel`（主機版）
- **分析日期**：`2026-10-24`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-21-agent-relay-pipeline-phase4.md`](./2026-10-21-agent-relay-pipeline-phase4.md)（本地多 Agent 派工與驗收）
  - [`notes/2026-10-23-zeabur-october-2026-security-incident.md`](./2026-10-23-zeabur-october-2026-security-incident.md)（貼文提到 Cloudflare 版是作者在 Zeabur 倒掉後做的替代方案）

---

## 0. 原始資料盤點

> 2026-11-18 補讀：**找回原貼文**。原筆記把平台記成 Threads，實際上內容對得上的是作者（王士麟，即 `aixwangtw`）2026-10-20 發在 Facebook 社團「Claude Taiwan」的貼文：<https://www.facebook.com/groups/1224997379198346/posts/1423750565989692/>。同時接 3 個專案、搭配 Opus 5.5 與排程、Cloudflare 版是 Zeabur 倒掉後的替代方案，這幾句都只出現在這一則。`source_url` 已改成這則貼文；原值 `https://github.com/aixwangtw/feedback-desk` 移到 `github_repo`。作者在 Threads（`@alex_wang.ai`）10-18 另有一則較短的版本：<https://www.threads.com/@alex_wang.ai/post/Deo2W1ekhFm>，沒有上述幾句。
>
> - **Facebook 貼文文字**：說明動機（訊息分散、沒有統一 API 讓 AI 讀需求與交接）；自己用 Claude Code 同時回 3 個客戶、夥伴用 Codex、用排程定時掃新單、特別調過 AI 寫調整說明的規則；流程是客戶開單、排程讀單、AI 修改並驗證、AI 寫調整說明、客戶確認後標記「已完成」；Cloudflare 免費版與主機版分在不同分支。
> - **作者圖片 1 張**（Facebook）：「老師題庫回報」的問題清單畫面。狀態有待處理、待審核、已完成三種，**每一列都有可以直接切換狀態的下拉選單**；欄位還有圖片、調整說明、建立日期與編輯、刪除按鈕。Threads 那則另附 1 張圖，沒有放大看（不是本筆記的來源）。
> - **留言**：Facebook 1 則（作者放介紹文與 repo 連結），已讀完。Threads 計數 3 則已全部讀完：一位質疑客戶講的需求有時連人都聽不懂，要 AI 聽懂是強人所難；作者回覆可以直接在系統上向客戶發問，由 AI 判斷哪些能直接處理、哪些要先確認，這段判斷邏輯會再調整。
> - **對分析的影響**：貼文與截圖呈現的是 **10 月中的舊版**：狀態是「待處理／待審核／已完成」，而且可以手動切換、客戶確認後「標記」完成。下面 2026-11-16 依作者介紹文（11-07 更新）改寫的三種狀態（等工程師／等客戶／已完成）、「待審」改指留言草稿、只有客戶按「通過」才能結案，是後來的改版。兩種說法各自對應當時的版本，原筆記的寫法在當時並沒有錯；第 1 節維持現行版本。

> 2026-11-16 重審：原筆記註明沒讀的作者介紹文（`aixwang.dev/blog/feedback-desk`，2026-10-18 發布、11-07 更新）這次全文讀完，文內 9 張圖與 README 的 1 張圖都看過；repo 的 2 則 issue 與 1 個 PR 也讀了（都沒有留言回覆）。原始 Threads 貼文沒有留下連結，無從回看；介紹文頁面沒有留言區。

- **作者圖片**：共 10 張（介紹文 9 張、README 1 張），介紹文註明截圖用的是假資料。
  - 圖 1：文章封面。
  - 圖 2：團隊端問題清單。頁籤是「等工程師／等客戶／已完成／全部」，列表五欄（編號、標題、狀態、建立者、最後更新），頁首鈴鐺展開列出客戶新留言與一則待審留言。
  - 圖 3～4：單張詳情（電腦版從右側滑出、手機版整頁），含說明、相簿、活動紀錄與「完成」按鈕。
  - 圖 5～6：留言可拖入圖片與影片並預覽；客戶端可直接播放團隊附的操作影片。
  - 圖 7：右下角留言面板自動打開，顯示一則「待審留言」與送出、捨棄、編輯按鈕。
  - 圖 8～9：團隊按「完成」後跳出可改字的確認留言；客戶端在該留言上按「通過」。
  - 圖 10（README）：命令列裝置碼授權頁，要使用者自己輸入終端機上的授權碼。
- **作者留言補充**（介紹文內容，取代原筆記「介紹文未讀」的缺口）：
  - 狀態只有固定 3 種：等工程師、等客戶、已完成；狀態跟著留言自動切換，網頁上沒有改狀態的選單。**團隊和 AI 都不能自己結案，一定要客戶按「通過」。**
  - 「待審」指的是**待審留言**：AI 或排程先擬好、客戶看不到的草稿留言，團隊按「送出」才發出。它不是一種工單狀態。
  - AI 用 MCP 或 CLI 改別人認領中的單時會先停下，確認接手才繼續，並記錄這次接手；認領與交接紀錄只有團隊看得到。
  - 附件上限：一則留言最多 5 個檔，圖片 10 MB、影片 50 MB。
  - 定位：不是專案管理工具，沒有排程、優先順序、報表；文中拿 Jira／JSM 的計價對照。
  - 作者自己的用法：Claude Code 排程定時掃新單、夥伴用 Codex；寫給客戶的留言規則另開源在 `aixwangtw/de-ai-slop`。
- **網友留言重點**：
  - issue #1（使用者回報，未回覆）：原生 Windows 下 CLI 以 `shell: true` 啟動子程序、參數不跳脫，`mcp install --claude` 的 JSON 引號被吃掉、寫 D1 的 SQL 被拆成多個參數，`mcp install`、`bootstrap` 會失敗。
  - issue #2（同一位使用者）：`laravel` 分支自動處理同時傳 `--sandbox` 與 `--approve-for-me`，Codex CLI 直接拒絕，新單自動處理全數失敗。
  - PR #3（未合併）：新增 Docker 自行託管，內網主機不需 Cloudflare 帳號。
- **對分析的影響**：
  - 第 1 節的流程原寫「狀態『待審核』→客戶確認→『已完成』」，與現行設計不符；已改成三種狀態加「待審留言」。
  - issue #1 補強 `T-20261024-03` 的結論：除了該任務實測到的安裝階段失敗，就算裝得起來，原生 Windows 的 `mcp install`、`bootstrap` 也會壞。結論「需 WSL」不變，已在第 2 節「平台限制」補上。
  - PR #3 若合併，不想用 Cloudflare 帳號時多一條自架路線；目前未合併，只記錄，不開新任務。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：接案開發者 aixwangtw，同時做 3 個專案，每案有客戶、夥伴與各自的 AI。
- **What**：開源工單／回報系統。客戶開單附截圖，開發端（人或 AI）讀單、修改、在單上留言寫附圖的調整說明，單自動轉為「等客戶」，客戶按「通過」後結案（2026-11-16 依作者介紹文更正：狀態只有等工程師／等客戶／已完成三種，團隊與 AI 都不能自行結案）。
- **Why**：訊息散落多處，沒有統一 API 讓 AI 讀需求與互相交接。
- **How**：

```text
客戶開單(+截圖) → CC 排程定時讀單 → AI 修改並驗證 → 寫簡潔調整說明
      → 留言後狀態自動變「等客戶」 → 客戶按「通過」 → 「已完成」
      （AI 可先寫「待審留言」草稿，團隊送出後客戶才看得到）
多 AI：認領（誰在處理）＋交接紀錄（下一個人/AI 讀單先看到）
      每個動作記錄「帳號＋AI 工具」，如「王小明（Codex）」
```

- **技術堆疊（README）**：Hono + D1 + R2，Cloudflare Workers 免費方案；一個 CLI 完成 init、deploy、建帳號、連接 AI；MCP（Streamable HTTP）與命令列雙通道；UI 為繁體中文。
- **身分模型**：客戶（專屬連結或個人帳號）、開發團隊 owner、公開回報者（選用，私密網址追蹤）。
- **使用者澄清**：它是**工單系統**（管每個任務），不是 CRM（管客戶名單）。
- **When & Where**：多人加多 AI 的接案、需要客戶確認閉環的場景。

> [!NOTE]
> **版本差異（2026-11-18 補）**：本節寫的是 **2026-11-07 更新後的現行版**（等工程師／等客戶／已完成；「待審」是留言草稿；只有客戶按「通過」才結案），於 2026-11-16 依作者介紹文改寫。**2026-10-20 原貼文與截圖呈現的是 10 月中的舊版**：狀態是待處理／待審核／已完成，可以用下拉選單手動切換，客戶確認後「標記」完成。原筆記（2026-10-24）照舊版寫，在當時是對的。
>
> 貼文數字與流程已與 README 對照，大致一致。README 明言對 OpenClaw、Hermes、Grok 的 MCP 設定「沒有實際測過」。貼文提到的 Opus 5.5 與排程做法是作者個人搭配，未驗證。

---

## 2. 官方 GitHub 與技術規格細節

- **安裝**：npm 套件尚未發佈，一律用 `npx --allow-git=all github:aixwangtw/feedback-desk <子命令>`；需 Node 20+、Cloudflare 免費帳號、啟用 R2。
- **主要子命令**：`init`、`deploy`、`bootstrap`、`login`（裝置碼授權）、`project create`、`client create`、`developer create`、`mcp install`、`mcp token --agent`。
- **AI 接入**：`mcp install` 為 Claude Code 與 Codex 各發獨立 token，存 `~/.config/feedback-desk/mcp/`；設定檔不含 token。其他 agent 以環境變數 `FEEDBACK_DESK_MCP_TOKEN` 與 `Authorization: Bearer` 標頭接入。
- **平台限制**：README 的指令說明寫「Linux、macOS 終端機（Windows 可用 WSL）」，而本機是 **Windows 11 原生、無 WSL**，原生可行性未知。（2026-11-16 補：repo issue #1 有使用者回報原生 Windows 下子程序參數未跳脫，`mcp install`、`bootstrap` 會失敗，尚無修正。）
- **安全面**：`login` 的 token 預設不會到期（可 `--expires` 設定）；README 提示不要在非自己發起的 login 頁面授權。部署提示詞明確要求 AI 不看密碼、不把 token 寫進對話。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與 `agent-relay` 的派工、交接、驗收閉環概念重疊：認領、交接紀錄、動作署名（帳號＋AI 工具）、「待審核→已完成」的人工確認閘門，可對照取長補短。
  - 本 repo 的 `T-` 任務與 DoD 就是一種內部工單；feedback-desk 多出的是**客戶端入口與截圖留言串**。
- **落差與採納判斷**：
  - **值得採納**：先實測 Windows 11 原生是否可部署；並對照它的認領／交接欄位，看是否補強 `agent-relay`。
  - **需調整**：需 Cloudflare 帳號與 token，必須遵守全域規範（token 不進對話、不進程式碼）；部署動作屬對外帳號操作，執行前要取得維護者明確同意。
  - **不採納**：目前沒有客戶接案需求就不需要正式導入；Zeabur 事件後也不遷移到任何新託管平台，除非另有決定。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261024-03`**｜**[優先級：中]** 在 Windows 11 原生環境評估 feedback-desk 的 CLI 與 MCP 可行性（不含正式部署，除非維護者同意）
  - **完成日期**：2026-10-25
  - **目標範圍**：`docs/feedback-desk-windows-eval.md`；僅在暫存資料夾執行，不碰其他 repo
  - **具體做法**：
    1. 以 `node -v` 確認 Node 20+，再於暫存資料夾執行 `npx --allow-git=all github:aixwangtw/feedback-desk init --name <測試名>`，記錄是否在原生 Windows 成功與錯誤訊息。
    2. 先詢問維護者是否同意建立 Cloudflare 帳號資源；同意才執行 `deploy` 與後續步驟，否則停在 `init`。
    3. 若有部署：驗證 `mcp install` 後 Claude Code 的 `/mcp` 顯示已連線，並確認 token 沒有出現在設定檔與對話。
  - **驗收標準（DoD）**：產出 `docs/feedback-desk-windows-eval.md`，含 `node -v`、`init` 的實際輸出（或錯誤）、是否需要 WSL 的結論一行；若有部署再加 `/mcp` 連線輸出。以 `Select-String -Pattern '結論'` 驗證存在，並確認文件不含任何 token。
  - **實作紀錄 / 證據**：已於暫存目錄 `$env:TEMP\fd-eval-test` 執行 `node -v`（`v26.12.1`）與 `npx --yes --allow-git=all github:aixwangtw/feedback-desk init --name test-desk`。確認 package.json 未發布 npm registry 且 git 忽略 `dist/`，套件安裝觸發 `prepare` 腳本時因 Windows 無法直接呼叫無副檔名之 `.bin/tailwindcss` 導致 `ENOENT` / `EINVAL`。產出評估文件 `docs/feedback-desk-windows-eval.md`，內含錯誤日誌與明確「結論：...」說明需 WSL 或手動修補，並已依規清理暫存資料夾。

- [x] **`T-20261024-04`**｜**[優先級：低]** 對照 feedback-desk 的認領／交接機制與本地 `agent-relay`，列出可借鏡與不採納項
  - **完成日期**：2026-10-25
  - **目標範圍**：`docs/feedback-desk-vs-agent-relay.md`（只讀比對，不改 `agent-relay`）
  - **具體做法**：
    1. 比對欄位：狀態機、認領、交接紀錄、動作署名（帳號＋AI 工具）、人工確認閘門、客戶可見範圍。
    2. 每項標註「已有／缺少／不需要」與理由。
  - **驗收標準（DoD）**：產出 `docs/feedback-desk-vs-agent-relay.md`，含至少 6 列對照表，每列含判斷與理由；以 `Select-String -Pattern '^\| '` 計數表格列至少 8（含表頭與分隔列）。
  - **實作紀錄 / 證據**：完成 feedback-desk 與 agent-relay 多維度機制對照，產出 `docs/feedback-desk-vs-agent-relay.md`。涵蓋狀態機、認領、交接紀錄、動作署名（帳號＋AI 工具）、人工確認閘門、客戶可見範圍、通訊傳輸架構與機密邊界等 8 項維度對照表，逐項標記已有／缺少／不需要及具體理由，表格列數經驗證達 10 列（>= 8）。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 派工與交接**：
  - [多 Agent 派工與驗收閉環流水線 Phase 4](./2026-10-21-agent-relay-pipeline-phase4.md) ｜ 關聯任務：`T-20261021-03`~`T-20261021-11`
- **資安與平台風險**：
  - [Zeabur 2026 年十月資安事件解構](./2026-10-23-zeabur-october-2026-security-incident.md) ｜ 關聯任務：`T-20261023-05`、`T-20261023-06`
