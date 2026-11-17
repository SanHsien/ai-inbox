---
id: 2026-11-07-gemini-notebook-official-api-mcp-preview
title: "Gemini Notebook（前 NotebookLM）官方 API 與 MCP 預覽版評估：7 個工具只能寫入不能查詢、GCP ADC 憑證風險與實際用途界定"
source_url: "https://www.threads.com/@be.ai.curator/post/DfY954CkZ9V"
source_platform: "Threads (@be.ai.curator)"
author: "AI 主理人 (@be.ai.curator)"
analyzed_at: 2026-11-07
analyzed_by: "Antigravity"
status: done
cluster: "3"
cluster_role: "跨網情報與知識檢索"
short_title: "Gemini Notebook MCP 預覽評估"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 8
source_replies: 11
tags:
  - gemini-notebook
  - notebooklm
  - mcp
  - google-cloud
  - adc
  - credential-hygiene
---

# Gemini Notebook（前 NotebookLM）官方 API 與 MCP 預覽版評估：7 個工具只能寫入不能查詢、GCP ADC 憑證風險與實際用途界定

- **來源連結**：[Threads 貼文：@be.ai.curator](https://www.threads.com/@be.ai.curator/post/DfY954CkZ9V) ｜ [分享短網址](https://www.threads.com/share/BAbZwU2wnu)
- **官方文件**：[Gemini Notebook API：Model Context Protocol (MCP)](https://developers.google.com/notebook/docs/mcp)、[Authentication](https://developers.google.com/notebook/docs/authentication)
- **抓取時間**：2026-11-07（貼文 2026-11-06 發布；2026-11-16 重審時 2.1 萬次瀏覽、279 讚、13 則留言）
- **歸屬集群**：集群 3（角色：`Google 研究工具 MCP 接入評估`）
- **評估結論**：`🟡 消息屬實、目前僅支援寫入無查詢 API；已將靜態 Bearer Token 與 cloud-platform 全權 scope 風險轉為自動化稽核規則`
- **相關交叉參照**：
  - [`notes/2026-11-04-nicholas-lin-gcp-vertex-ai-amos-llmjacking.md`](./2026-11-04-nicholas-lin-gcp-vertex-ai-amos-llmjacking.md)（GCP 專案開 API、憑證外洩的風險鏈）

---

## 0. 原始資料盤點

> 2026-11-16 重審：未登入可讀主文、8 張輪播圖（逐張放大到原尺寸看過）、作者留言與連結預覽卡、10 則留言。
> 2026-11-17 登入補讀：熱門、最新兩種排序都捲到頁尾，並點進有子回覆的留言頁，讀到 11 則；頁面標示 13 則，差的 2 則兩種排序都不顯示（平台隱藏或已刪）。

- **作者圖片**（8 張輪播，皆為作者自製圖卡，標「操作示意」，不是官方畫面截圖）：
  - 圖 1 封面：改名後第一次開放給個人 Google 帳號，預覽期間免費，含 MCP。
  - 圖 2：Claude Code、Cursor 接上官方 MCP 伺服器後能開新筆記本、加資料。
  - 圖 3：可加入 4 種來源（公開網頁、有字幕的 YouTube、純文字、Markdown），每份最多 50 萬字。
  - 圖 4：三種用法：追蹤的 YouTube 頻道出新片就加入、一個題目 30 個網頁一次建好、Markdown 筆記整批搬入。三種都是「寫入」。
  - 圖 5：能做（建筆記本、改名、加網頁／YouTube、純文字／Markdown、讀取和列出來源）與還不能做（問問題、語音摘要、傳 PDF、接雲端硬碟、**刪除**、Workspace 帳號）。
  - 圖 6：各方案上限：免費 100 本／每本 50 個來源；Google AI Plus 200 本／100 個；Pro 500 本／300 個；Ultra 500 本／600 個。
  - 圖 7：分工示意，Gemini Notebook 負責資料庫／研究／筆記，Claude Code 與 Codex 負責開發／測試／除錯。
  - 圖 8：三步開始用：個人 Gmail 先登入 Gemini Notebook 一次、複製官方 MCP 網址、貼給 AI 叫它帶你裝。
- **作者留言補充**（3 則）：
  - 放官方 MCP 設定頁連結（預覽卡是 Google for Developers 的「Model Context Protocol (MCP)｜Gemini Notebook API」頁，與本筆記引用的官方文件同一頁），並提醒帳號要先用個人 Gmail 登入過 Gemini Notebook 至少一次。
  - 回 `lockislunatic`：目前免費，之後額度跟著 Google 訂閱走。
  - 回 `flipped_education`（2026-11-17 補讀到的長回覆）：NotebookLM 的優勢是快、精確率尚可，處理 YouTube 與沒有付費牆的簡單網頁可以省下爬蟲額度；要問答可在 Gemini App 裡用 @ 指定筆記本，但作者認為 Gemini 現有模型比 Claude、GPT 的頂級模型差一截。作者也承認 Claude Code 原生的資料分析與網路搜尋，加上瀏覽器操作和幾個 skill 就能做到差不多的事，接回 Notebook 主要是想把額度省下來給開發。
- **網友留言重點**（頁面標示 13 則，讀到 11 則含作者 3 則）：
  - `zhenheco`：工具接越多要維護的流程越多，只為每週跑三次以上的事接工具。
  - `aj.admin.ai`：先挑一個每週重複的資料整理任務試，確認匯入後來源連結與引用有沒有保留，再決定要不要接。
  - `zz950907`：當研究前置處理器，研究時叫 AI 先查筆記本。與官方 API 不符，見第 2 節。
  - `ai_future88888`：把「收集來源」和「產出判斷」分兩段，客戶個資與未公開報價不要放進測試資料。
  - `flipped_education`：使用習慣已漸漸移到能持續對話產出的 Claude／Codex。
  - `lockislunatic`：問能不能接訂閱。其餘為「存」與附和。
  - 沒有任何留言提到要建 GCP 專案或憑證風險。
- **對分析的影響**：
  - 圖 5 多列了兩項官方限制：不能刪除、不能接雲端硬碟。這與第 2 節「7 個工具沒有 delete」一致；已補進第 1 節與第 3 節。**不能刪除**代表 agent 批次建立的筆記本與來源只能由人到網頁介面清理，是新增的營運風險。
  - 圖 3 的單一來源 50 萬字上限、圖 6 的方案額度表，原筆記沒有，已補進第 1 節（來源是作者圖卡，未對照官方文件）。
  - 圖 8 把安裝寫成三步，完全沒提 GCP 專案、`gcloud`、ADC 與 token；第 3 節的門檻分析正好補上這段落差，已在第 3 節開頭寫明。
  - 作者說明額度之後跟著 Google 訂閱，已補進第 1 節。
  - 既有任務 `T-20261107-05` 的範圍不受影響，不新增任務。
  - 2026-11-17 補讀：作者自己在回覆裡把這個 MCP 的價值定位成「省額度」，不是能力上的增加，而且說問答要回到 Gemini App 用 @ 筆記本做。這與第 2 節「官方 API 沒有問答工具」一致，也讓 `zz950907`「研究時叫 AI 先查筆記本」的用法更站不住（外部 agent 只能列出與讀取來源，不能對筆記本提問）。結論與任務不變。

---

## 1. 貼文重點

- Gemini Notebook（2026-07-16 起由 NotebookLM 改名；未查證，官方文件頁未見此說明）推出個人用官方 API 與 MCP 預覽版：AI 工具可以自己**建筆記本、加入網頁、有字幕的 YouTube、純文字**。
- 作者自己標明限制：**不能問問題、不能產生語音摘要、不能傳 PDF，Workspace 帳號還不開放**。圖卡另列兩項：**不能刪除、不能接雲端硬碟**。
- 圖卡列出的量：單一來源最多 50 萬字；免費 100 本／每本 50 個來源，Google AI Plus 200／100，Pro 500／300，Ultra 500／600（作者整理，未對照官方文件）。作者在留言說目前免費，之後額度跟著 Google 訂閱。
- 作者主張：從額度分工角度，beta 免費值得先接，可分擔 Grok／Claude Code／Codex 研究影片的額度。
- 值得留意的留言：
  - `zhenheco`：工具接越多，要維護的流程越多；只為每週跑三次以上的事接工具。
  - `zz950907`：當「研究前置處理器」，「研究時叫 AI 先查筆記本再回答」。**這點與官方 API 不符，見第 2 節。**

## 2. 查證官方文件（關鍵修正）

- **端點**：`https://notebook.googleapis.com/mcp`，Streamable HTTP（JSON-RPC 2.0）。
- **只有 7 個工具，全部是管理與匯入**：

| 工具 | 作用 |
| --- | --- |
| `create_notebook`／`get_notebook`／`list_notebooks`／`update_notebook` | 建立、讀取中繼資料、列出、改名 |
| `create_source` | 匯入網頁 URL、YouTube、純文字或 Markdown |
| `get_source`／`list_sources` | 查看來源中繼資料與處理狀態（`PROCESSING`／`ACTIVE`／`FAILED`） |

- **沒有任何查詢、問答或取回摘要的工具**。所以 coding agent **無法**「先查筆記本再回答」。目前的流程只能是：

```text
Agent ──create_source──► Gemini Notebook ──► 人在網頁 UI 問答 / 產生 Audio Overview
   ▲                                              │
   └──────── 拿不回答案（API 沒有查詢工具）─────────┘
```

- 「分擔 Claude Code／Codex 研究額度」在這一版**不成立**：agent 讀不到 Notebook 的分析結果，研究仍要自己做。

## 3. 接入門檻與憑證風險

作者圖卡把安裝寫成三步（個人 Gmail 先登入一次、複製官方 MCP 網址、貼給 AI 帶你裝），沒有提到下列前置條件。官方安裝流程要求：

1. 一個 **GCP 專案**，並執行 `gcloud services enable notebook.googleapis.com`。
2. 以 ADC 登入，scope 同時包含 `cloud-platform` 與 `notebook`。
3. 用 `gcloud auth application-default print-access-token` 取得 Bearer token，**直接寫進 MCP 設定檔的 header**（官方範例甚至把 token 放在 `claude mcp add --header` 指令列）。

風險與摩擦：

- **憑證進指令列與設定檔**：與「API key、token 不進程式碼、指令列、對話」的硬閘門衝突。
- **ADC 帶 `cloud-platform` 全權 scope**：本機一旦被竊（參照 Nicholas Lin 案的 AMOS 竊密鏈），拿到的是整個 GCP 專案權限，不只 Notebook。
- **Access token 有效期短（Google OAuth 通常約 1 小時；文件未載明，屬 OAuth 一般行為）**：靜態寫入 header 會很快失效，要另外處理更新，否則會**默默失敗**。
- **建了刪不掉**：這一版沒有刪除工具，agent 誤建或測試用的筆記本與來源，只能由人到網頁介面清理；批次匯入前要先想好命名與數量上限。
- 若要試，應開一個**專用、未綁計費帳戶的 GCP 專案**，只開 `notebook.googleapis.com`，並用包裝腳本即時取 token，不把 token 寫入任何檔案。

## 4. 評估

| 面向 | 判斷 |
| --- | --- |
| 消息真實性 | ✅ 屬實，官方文件已上線 |
| 對 coding agent 的實際價值 | 低：只能寫入，拿不回分析結果 |
| 對人的價值 | 中：可讓 agent 批次把研究來源丟進筆記本，人再用 UI 問答、聽 Audio Overview |
| 接入成本與風險 | 中高：GCP 專案、ADC 全權 scope、短效 token 管理 |

## 5. 待辦

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261107-05`**｜**[優先級：中]** 擴充 `tools/verify_cloud_persistence_audit.py` 新增 MCP 設定檔靜態 Bearer／`ya29.` Token 與過寬 `cloud-platform` Scope 稽核器
  - **目標範圍**：`tools/verify_cloud_persistence_audit.py`、`tests/test_verify_cloud_persistence_audit.py`
  - **具體做法**：
    1. 針對官方 Gemini Notebook MCP 教學將 `gcloud auth application-default print-access-token` 產出之短效 `ya29.*` Bearer Token 直接寫進 MCP 設定檔 `headers`／`args`（易外洩且 1 小時（文件未載明，屬 OAuth 一般行為）過期後靜默失效）與申請 `cloud-platform` 全權 scope 之風險，實作 `audit_mcp_config_credentials()` 與 `--audit-mcp-config` 參數。
    2. 支援攔截硬編碼 Bearer Token 與 `ya29.*` 憑證，同時放行環境變數佔位符（如 `${NOTEBOOK_ACCESS_TOKEN}`）。
  - **驗收標準（DoD）**：執行 python -m unittest tests/test_verify_cloud_persistence_audit.py 綠燈通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正兩輪（2026-11-14）：MCP 設定的 env／headers 敏感鍵名與已知 token 樣式（ghp_、github_pat_、sk-、sk-ant-、xox、ya29.、AKIA）、url 查詢參數與 user:pass@ 都會報出；佔位符放行；壞 schema 回 2。原審查反例（短 Bearer、args 的 ya29.、陣列 schema）與 Opus 新繞過（env GITHUB_TOKEN、url access_token、X-API-Key）全部由 exit 0 變 1／2。 **搬移註記（2026-11-14）**：工具與測試已移至 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks)（保留 git 歷史）。

> 備註：Gemini Notebook MCP 本身因目前 7 個工具僅支援寫入、無問答或取回摘要 API，暫不接入日常研究流水線；待官方新增查詢工具或 OAuth 自動刷新機制後再評估接入。
