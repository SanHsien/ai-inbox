---
id: "2026-11-13-hujiaxi-claude-code-artifacts-slides-canva-killer"
title: "Claude Code Artifacts 內建簡報編輯器：Canva 式介面、可分享、可匯出 PPTX/PDF"
source_url: "https://www.facebook.com/share/1CRZAaRBW7/"
source_platform: "facebook"
author: "胡嘉璽"
analyzed_at: "2026-11-13"
analyzed_by: "antigravity"
status: pending
cluster: 1
cluster_role: "簡報工作流"
short_title: "Claude Artifacts簡報"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 2
source_replies: 15
tags:
  - claude-code
  - artifacts
  - slides
  - canva
  - pptx
  - html-artifact
  - anthropic
  - claude-plugins-official
---

# Claude Code Artifacts 內建簡報編輯器：Canva 式介面、可分享、可匯出 PPTX/PDF

- **來源連結**：[Facebook 貼文：胡嘉璽](https://www.facebook.com/share/1CRZAaRBW7/)
- **發布平台 / 作者**：`facebook` / `胡嘉璽`
- **分析日期**：`2026-11-13`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 0. 原始資料盤點

> 2026-11-16 以未登入瀏覽器重看原貼文。作者圖片 2 張（都開原尺寸看過）、留言 15 則全部讀到（含作者 2 則回覆），另看了作者留言裡附的 1 張截圖。

- **作者圖片**：
  - **圖 1（成品畫面）**：瀏覽器開在 `claude.ai/artifact/...` 的頁面，是一份 75 頁的深色投影片（畫面停在第 2 頁講者介紹）。上方有文字／圖片／表格／形狀的編輯工具列，下方是整排投影片縮圖，右上有留言、分享按鈕與播放、縮放控制。作者用紅框標出下載選單，選項是：PDF、Web page（.html）、Current slide as an image（.png）、PowerPoint, current fonts（.pptx）、PowerPoint, basic fonts（.pptx），並註明 basic fonts 在任何電腦都能用。
  - **圖 2（觸發過程）**：Claude Code 終端畫面。作者前一句在交代大綱與簡報不要放 emoji，下一句只打「開始做簡報」（紅框），Claude Code 隨即呼叫 `Artifact(quickstart slides)`，接著「new artifact from type」從一個 claude.ai 上的 Artifact 類型建立新的 Artifact，並提到成品是 75 頁簡報、留言可自動回覆。
- **作者留言補充**：
  - 回 QQnice Lin：成品可以直接在瀏覽器上修改。
  - 回 Ke Chen Lung「有推薦的簡報 Skill 嗎」：「去裝預設的這個就行」，附 Claude Code 的 Plugins › Marketplaces 截圖，列出內建的 Anthropic Directory 與 `anthropics/claude-plugins-official` 兩個來源（後者顯示已裝 10 個）。
- **網友留言重點**：
  - **QQnice Lin**：Artifacts 本來就可以分享；他的學生也做了 HTML 版的簡報。
  - **Jeff Hung**：PPT／HTML 比 Markdown 好，是因為 AI 產出太冗長、不得不花 token 加視覺輔助（原稿已收）。
  - **紀彥甫**：「你發現得有點晚了」——暗示這功能已上線一段時間。
  - **Chris Amber Hs**：「右上方的最左邊」，指下載按鈕的位置。
  - **陳秀環**：稱 Canva 裁員 22%（未查證，不採用）。
  - 其餘是對產業衝擊的感嘆，以及兩則討論貼文中校名寫法的離題留言。
- **對分析的影響**：
  - **「PPTX／PDF 匯出只有第三方摘要佐證」已被作者圖 1 推翻**：下載選單清楚列出 PDF、HTML、PNG 與兩種 PPTX。原稿「未驗證：Canva 式編輯器與 PPTX 匯出」一節已改寫為「已有截圖佐證」，5W1H、CQR、路線對照表同步更正。匯出檔的品質（版面是否跑掉、字型替換）仍未實測。
  - **「觸發條件不明、無法複製」已被作者圖 2 推翻**：不是 Canva MCP、也不是 `pptx` skill 造成的。Claude Code 內建的 `Artifact` 工具有一步 quickstart，意圖是 slides 時會從 claude.ai 上現成的「簡報類型」建立 Artifact；作者只是說「開始做簡報」。原稿對 Canva MCP 與措辭的推測已刪除，改寫為圖上看到的流程。
  - **網址形式補正**：圖上是 `claude.ai/artifact/<id>`，原稿架構圖只寫 `claude.ai/code/artifact/<uuid>`，已並列。
  - **「可用性：beta，Team／Enterprise」這一列未能從貼文印證或推翻**：作者沒說自己的方案，保留原文並標明來源是官方 plugin 文件。
  - **處置改變**：原稿因「無法複製」而歸檔、不衍生任務。現在觸發方式與匯出選項都有畫面佐證，值得在本機實測一次再決定簡報路線，新增 `T-20261113-01`，狀態由 archived 改為 pending。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：作者胡嘉璽（貼文）；功能出自 Anthropic 官方 Claude Code。
- **What**：Claude Code 做投影片時產出可分享、可在瀏覽器直接編輯的 Artifact 簡報，可下載 PDF／HTML／PNG／PPTX（作者截圖佐證，匯出品質未實測）。
- **Why**：作者以此取代 Canva；本筆記要釐清是新功能還是誤解。
- **How**：內建 `Artifact` tool 先跑 quickstart（意圖 slides），從 claude.ai 上的簡報類型建立 Artifact 再填內容（作者圖 2；見下方技術架構）。
- **When & Where**：需 claude.ai 登入的互動 session；官方文件寫 beta、Team／Enterprise。
- **Key Metrics / Numbers**：貼文 262 reactions、76 shares；無實測數據。

### 摘要原文

**胡嘉璽**（2026-11-08，262 reactions、76 shares）發現：用 Claude Code 做投影片時，輸出不再是 `.pptx`，而是開啟一個 **Claude Code Artifacts 網頁**，介面與 Canva 幾乎一樣，可分享，且能下載成 PDF 或 PPTX。作者因此退訂 Canva，並問「是新功能還是我大驚小怪」。

查證結論：

- 「Artifact 發布到 `claude.ai` 的私有頁面並可分享」有官方倉庫佐證（見下）。
- 「Canva 式簡報編輯器 + PPTX/PDF 匯出」：作者圖 1 的下載選單與編輯工具列可佐證功能存在（2026-11-16 重看圖片後更正；原稿只查到第三方網頁摘要）。編輯器與匯出是 claude.ai 的 Artifact 檢視頁提供的，不是 Claude Code 終端裡的功能。
- 觸發條件：貼文文字沒寫（作者自述「不知我啟動了什麼」），但圖 2 顯示只是對 Claude Code 說「開始做簡報」，由內建 `Artifact` 工具的 quickstart 走簡報類型。

---

## 技術架構深挖

### 已驗證：Claude Code 內建 `Artifact` tool

來源：`anthropics/claude-plugins-official`（`plugins/project-artifact`，Anthropic 官方，README 與 SKILL.md 實讀）。

```
Claude Code session
   │  內建 Artifact tool（需 claude.ai 登入）
   ▼
單檔自包含 HTML（CSP 禁止所有外部 host → 資源必須內嵌，僅允許極少 script）
   │ publish
   ▼
https://claude.ai/code/artifact/<uuid>   預設私有（作者圖上的簡報網址是 claude.ai/artifact/<id>）
   ├─ owner 有版本選擇器（version picker）
   └─ 可從 claude.ai viewer 分享給 teammates
```

| 項目 | 實況（官方文件） |
|------|------|
| 可用性 | beta，Team / Enterprise 方案 |
| 登入限制 | 需 claude.ai 登入；API key、Bedrock、Vertex 工作階段沒有此 tool |
| 自動化限制 | 無頭 `claude -p` 沒有 Artifact tool，發布步驟必須在互動 session |
| 更新 | 重新發布可沿用同一 URL（project-artifact 以設定檔記住 URL） |
| 分享 | 預設私有，owner 於 viewer 手動分享 |

這修正了貼文中「Claude Code 的 Artifacts 是不能分享的」的舊認知：新版可分享。

### 傳統路線：`anthropics/skills` 的 `pptx` skill

倉庫 193,948 stars，`skills/` 內含 `pptx`、`web-artifacts-builder`、`canvas-design`、`frontend-design` 等。

- 建立新簡報：寫 `pptxgenjs` script。
- 編輯既有簡報：解壓 → 改 `ppt/slides/slideN.xml` → 重新壓縮。
- 讀取：`markitdown deck.pptx`；縮圖：`scripts/thumbnail.py`。
- 觸發詞：只要提到 deck、slides、presentation 或 `.pptx` 檔名就觸發。

作者原本的流程就是這條（輸出 `.pptx` 再手動或請 Claude 修改）。本次改走 Artifact 路線的原因，作者圖 2 已經交代：他只說「開始做簡報」，Claude Code 自己呼叫 `Artifact(quickstart slides)` 並從簡報類型建立 Artifact；與 Canva MCP 無關（原稿的推測已刪）。

### 有截圖佐證：Canva 式編輯器與 PPTX 匯出

作者圖 1 是實際畫面：編輯工具列（文字、圖片、表格、形狀）、投影片縮圖列、留言與分享按鈕，下載選單有 PDF、Web page（.html）、目前這頁存成 PNG、PowerPoint（current fonts）、PowerPoint（basic fonts）。作者也在留言確認可直接在瀏覽器修改。

仍未確認的部分：匯出 PPTX 在 PowerPoint 開啟後的版面與字型是否正確、Google Slides 匯出（第三方摘要提到，圖上沒有）、這個簡報類型在哪些方案可用。

### 作者背景脈絡：HTML 作為中間產物

作者提到半年前社群討論過「HTML 比 Markdown 更適合當中間產物」，寫程式、書、講義時瀏覽器 + HTML 已是常用檢視介面。留言反方觀點：PPT/HTML 勝過 Markdown 只是因為 AI slop 太多、文字不精簡，才靠視覺輔助（多花 token）。此爭議有道理，兩種說法可並存。

---

## 對照：兩條簡報路線

```
需求：做簡報
   ├─ A. pptx skill（pptxgenjs / OOXML）
   │     輸出 .pptx → 本機 PowerPoint 可編輯、可離線、可版控
   └─ B. Artifact（單檔 HTML，發布到 claude.ai）
         輸出網頁 → 可分享連結、版本管理；可下載 PDF／HTML／PNG／PPTX（截圖佐證）；
         受 CSP 限制、需登入、beta、非無頭
```

| 面向 | pptx skill | Artifact |
|------|-----------|----------|
| 離線與自控 | 高 | 低（綁 claude.ai 帳號） |
| 協作分享 | 手動寄檔 | 連結分享 |
| 自動化（CI / 無頭） | 可 | 發布不可 |
| 設計品質 | 受 pptxgenjs 限制 | 網頁排版彈性高 |
| 隱私 | 檔案在本機 | 內容上傳到 Anthropic 託管頁面 |

---

## 2. CQR 深入論證檢驗（選填）

- **Claim**：Claude Code 做簡報會開啟 Canva 式編輯網頁並可匯出 PPTX／PDF。
- **Evidence**：官方 `project-artifact` plugin 佐證 Artifact 發布與分享；作者圖 1（下載選單、編輯工具列）與圖 2（`Artifact(quickstart slides)` 呼叫紀錄）佐證編輯器、匯出與觸發方式。
- **Reasoning**：功能存在與觸發方式有畫面可證；匯出品質未實測，單一用戶經驗不足以支撐「Canva 殺手」結論。

---

## 3. 啟發與適用性評估

### 與本機防線對照

- **隱私**：發布 Artifact 等於把簡報內容上傳到 claude.ai 託管；含客戶或內部資料者不應使用，預設私有但分享後即外流。
- **方案限制**：Team/Enterprise beta，個人方案可能沒有此功能（需 Team／Enterprise）；本機若無 claude.ai 登入的互動 session 也無法使用。
- **「Canva 被斬殺」是情緒化結論**：沒有實測匯出品質，單一用戶經驗不足以推論產業判斷。
- 本機若要穩定產簡報，在 `T-20261113-01` 實測完成前仍以 `pptx` skill 路線為主。

---

### 評估結論與處置

**評分：⭐⭐⭐（3/5）**

提供了有用的線索：Claude Code 已有可發布分享的內建 Artifact tool，且 `pptx` skill 與 Artifact 是兩條不同路線。扣分：貼文文字沒說清楚觸發方式（要看圖 2 才知道）；匯出品質沒有實測；標題帶有誇張成分。

**處置**（2026-11-16 更新）：原稿因「無法複製」歸檔。重看作者圖片後觸發方式與匯出選項都已明確，改為新增一項實測任務。含敏感內容者仍不要發布到 Artifact。

---

## 4. 拆解待辦事項（Action Items）

- [ ] **`T-20261113-01`**｜**[優先級：低]** 實測 Claude Code 簡報 Artifact 的 PPTX／PDF 匯出品質，決定本機簡報走哪條路線
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/`；本機 Claude Code 互動 session
  - **具體做法**：在 claude.ai 登入的 Claude Code 互動 session，用一份不含敏感資料的 5 頁大綱（含 1 張表格、1 張圖、中英文混排）請它做簡報，確認是否走 `Artifact` 的簡報類型；從檢視頁各下載一次 PDF、PowerPoint（current fonts）、PowerPoint（basic fonts），用 PowerPoint 開啟比對版面、字型、表格是否與網頁一致。同一份大綱再用 `pptx` skill 產一次作對照。
  - **驗收標準（DoD）**：產出 `docs/claude-artifact-slides-export-test.md`，記錄：實際觸發的工具呼叫、帳號方案是否可用、三種匯出檔逐頁比對結果（跑版處逐項列出）、與 `pptx` skill 產出的對照、最後的路線建議；若本機方案沒有這個功能，照實記錄並關閉任務。

**參考連結**：
- 官方 plugin：https://github.com/anthropics/claude-plugins-official/tree/main/plugins/project-artifact
- 官方 skills：https://github.com/anthropics/skills/tree/main/skills/pptx
