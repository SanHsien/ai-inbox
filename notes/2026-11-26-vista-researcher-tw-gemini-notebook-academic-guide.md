---
id: "2026-11-26-vista-researcher-tw-gemini-notebook-academic-guide"
title: "RESEARCHER.TW《Gemini Notebook 學術用法指南（101 頁）》評析：兩層語料抽屜、草稿出處體檢、三項幻覺實測與五大踩雷防線"
source_url: "https://deck.researcher.tw/decks/gemini-notebook-research-guide/#1"
source_platform: "deck.researcher.tw (研究者基地)"
author: "Vista Cheng（鄭緯筌）"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 29
source_replies: 0
source_reviewed_at: "2026-11-26"
source_review_note: "已透過內建瀏覽器完整讀取 deck.researcher.tw/decks/gemini-notebook-research-guide/ 全部 101 頁正文、28 張自製 SVG 圖表（含 aria-label）與第 101 頁書籍封面點陣圖；簡報頁面無留言區（0 則）。"
status: pending
cluster: 3
cluster_role: "學術語料庫工作流"
short_title: "GeminiNotebook學術指南"
tags:
  - gemini-notebook
  - notebooklm
  - academic-research
  - literature-review
  - zotero
  - grounding
  - hallucination
---

# RESEARCHER.TW《Gemini Notebook 學術用法指南（101 頁）》評析：兩層語料抽屜、草稿出處體檢、三項幻覺實測與五大踩雷防線

- **來源簡報**：[`deck.researcher.tw/decks/gemini-notebook-research-guide/#1`](https://deck.researcher.tw/decks/gemini-notebook-research-guide/#1)（作者：Vista Cheng 鄭緯筌／研究者基地，共 101 頁；完整長文見 `researcher.tw/articles/gemini-notebook-research-guide`）
- **分析日期**：`2026-11-26`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-17-academic-reading-framework.md`](./2026-10-17-academic-reading-framework.md)（5W1H + CQR + KSU 學術論文精讀框架）
  - [`templates/academic-reading-prompt.md`](../templates/academic-reading-prompt.md)（本庫學術閱讀提示詞範本目標文件）
  - [`notes/2026-11-07-gemini-notebook-official-api-mcp-preview.md`](./2026-11-07-gemini-notebook-official-api-mcp-preview.md)（Gemini Notebook 官方 API / MCP 預覽版評估）
  - [`notes/2026-11-24-cultiwise-gemini-notebook-shorts-video-eval.md`](./2026-11-24-cultiwise-gemini-notebook-shorts-video-eval.md)（Gemini Notebook 中文短影音實測）

---

## 0. 原始資料盤點（101 頁結構、實測數字與五大方法論）

- **版本與額度基線（p.9–16，2026 年 9 月資料）**：
  - `2026-07-16` NotebookLM 更名為 **Gemini Notebook**（`notebook.google.com`），公布達 3,000 萬用戶／60 萬組織並加入原生程式碼分析沙箱；免費版每本 50 來源／100 本／每日 50 提問／每日 3 語音摘要，AI Pro 升至每本 300 來源／500 本／每日 500 提問，但**單一來源上限皆為 50 萬字或 200MB**。
- **能力邊界（「三件做得到」vs「四件做不到」，p.17–26）**：
  - 做得到：答案鎖定來源並附跳轉原文引用；跨來源橫向比較（測量方式／結論矛盾／定義差異）；多形態輸出（4 種語音摘要、影片摘要、心智圖、測驗與學習指南）。
  - 做不到：`Discover sources` 僅為網頁搜尋非學術資料庫（無 DOI 驗證）；引用可追溯但**不保證正確**；不能外包研究缺口與理論對話選擇；無官方 Zotero／Mendeley 或完整筆記本匯出。
- **架構設計三決定（p.27–40）**：
  1. **一本對一個問題**：單本超過 **20 篇**來源後回答明顯平均化，建議學位論文拆為 4 本（理論對話 8–15 篇／方法論／實證資料／投稿與規範）。
  2. **兩層來源結構＋掃描檔前檢**：外圍層（Staging ~30 篇，僅做篩選）→ 核心層（Production 8–15 篇，用於產出句子）；掃描 PDF 無文字層時**完全讀不到且靜默不報錯**，上傳前必先測可否選取文字。
  3. **隱私與帳號分水嶺**：**個人 AI Pro / Ultra 隱私政策與免費版相同**——按讚／倒讚會把提問＋來源＋輸出送審最長保留 3 年；僅 **Workspace 與教育版**免人工審閱與訓練；`Chat View` 僅隱藏 UI、**未撤銷底層內容存取權**。
- **五種學術用法與四大 Prompt 約束（p.41–62）**：
  - 四大約束：① 限定範圍、② 寫死輸出欄位、③ 強制標註篇名與段落出處、④ **允許說「無法確認，不要推測」**。
  - 涵蓋：7 欄文獻矩陣＋操作型定義分組、方法論步驟分歧拆解、質性逐字稿「附原話」追問、**草稿上傳做出處體檢＋單獨開本聽批判版語音摘要**，以及口試前兩週百萬 Token 審稿人模擬。
- **三項實證幻覺／遺漏數字（p.23、p.74–80）**：
  - **Tozuka et al. (`arXiv:2410.10869`)**：100 個肺癌分期案例，引用定位正確率 **95%**（意即每 20 筆有 1 筆指錯）、判斷正確率 **86%**。
  - **Hagar, Agustianto & Diakopoulos (2025, `arXiv:2509.25498`)**：300 份文件語料，Gemini Notebook 幻覺率 **13%**（優於 Gemini 2.5 Pro 與 ChatGPT 的 40%），但**一旦出錯平均含 3 個幻覺**，且出現「把學者觀點改寫成『研究顯示』」的詮釋越界。
  - **Samaan et al. (2026)**（57 篇 / 1,710 格）：格層級正確率 **91.17%**，工時由 165h 降至 17.7h，但主要錯誤是**遺漏（抽取不完整）**；匹茲堡大學實測 3 篇火星火山學語音摘要則全在結尾段出錯。
- **外部串接與五大踩雷（p.81–95）**：
  - 用 **Zotero MCP** 取代 `Discover sources` 找文獻；用一次性腳本把多篇 PDF 合併為帶分隔標記的 Markdown（順便 OCR＋省來源額度），輸出矩陣轉 CSV 並與 Zotero 對帳存本地版控。
  - 消費者版無公開 API，社群逆向工具（`roomi-fields/notebooklm-mcp`、`tmc/nlm`、`PleasePrompto` 2026/9/10 已封存）均屬未授權端點，不可放進不可出錯的交稿流程或主力帳號。

---

## 1. 與本專案現有架構的對照與啟發

1. **與 `5W1H-CQR-KSU` 及 `academic-reading-prompt.md` 高度互補**：
   - 本庫既有 [`templates/academic-reading-prompt.md`](../templates/academic-reading-prompt.md) 聚焦單篇論文精讀與 CQR 拆解；本簡報補齊了**多篇跨文獻語料庫（8–15 篇核心層）**的操作紀律，特別是**「草稿上傳做出處反查」**與**「四大約束（強制『無法確認』退路）」**，可直接納入範本與學術 SOP。
2. **「外圍層 → 核心層」與「掃描 PDF 靜默失敗」屬於通用資料前處理防線**：
   - 單本 >20 篇平均化、以及無文字層 PDF 靜默回傳空泛答案，兩者都印證了本庫「工具靜默失效最危險」與「嚴控上下文雜訊」的設計原則。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261126-03`**｜**[優先級：低]** 將《Gemini Notebook 學術用法指南》之「外圍／核心兩層語料切分、四大約束（含『無法確認』退路）、草稿出處反查與掃描 PDF／13% 幻覺／遺漏對帳紀律」補入 `templates/academic-reading-prompt.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\templates\academic-reading-prompt.md`（收錄於集群 3）
  - **執行步驟**：
    1. 在 `templates/academic-reading-prompt.md` 新增「多篇跨文獻語料庫與草稿反查模組」，納入 7 欄文獻矩陣 Prompt、四大約束（範圍／欄位／出處／「找不到就填無法確認」）與「草稿上傳做逐段出處體檢」步驟。
    2. 補註實務防呆提醒：單本 ≤15 篇（超過 20 篇易平均化）、上傳前檢查 PDF 文字層防止靜默失敗、以及引用定位 95%／資料抽取遺漏率風險須回原文核對。
  - **驗收標準（DoD）**：`templates/academic-reading-prompt.md` 完成上述模組補充且不破壞既有 5W1H-CQR-KSU 結構，執行 `python tools/verify_inbox.py` 驗證通過。
