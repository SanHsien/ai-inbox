---
id: "2026-11-22-bnext-gemini-skills-setup-and-prompt-anchoring-eval"
title: "數位時代評析：Gemini Gems 轉型 Skills 實戰——SKILL.md 跨平台通用規範與防跳步首句定錨 Prompting"
source_url: "https://www.bnext.com.tw/article/93097/gemini-skills-setup-guide"
source_platform: "bnext.com.tw (數位時代)"
author: "韋惟珊"
analyzed_at: "2026-11-22"
analyzed_by: "antigravity"
written_by: "legacy/unknown@pre-review; claude/opus-5.5@e7344aab-d6b6-4fcb-961e-1304a5af6031; antigravity/gemini-4-argon@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; codex/gpt-6.1-sol@01a2125a-4d1e-73b1-86ee-52ace903a7f4"
revised_at: "2026-11-25"
source_review: full
source_images: 7
source_replies: 0
source_reviewed_at: "2026-11-25"
status: pending
cluster: 3
cluster_role: "Gemini技能規格"
short_title: "Gemini技能教學評估"
tags:
  - gemini
  - gemini-skills
  - skill-md
  - prompt-engineering
  - workflow-automation
  - agent-skills
---

# 數位時代評析：Gemini Gems 轉型 Skills 實戰——SKILL.md 跨平台通用規範與防跳步首句定錨 Prompting

- **來源文章**：[Gemini技能叫了卻不照流程跑？從安裝到呼叫教學，讓AI照你的工作流執行（數位時代 BusinessNext）](https://www.bnext.com.tw/article/93097/gemini-skills-setup-guide)
- **發布平台 / 作者**：`bnext.com.tw` / `韋惟珊`（`2026-11-18`）
- **分析日期**：`2026-11-22`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-19-android-official-skills-google-coding-agent.md`](./2026-10-19-android-official-skills-google-coding-agent.md)（Google 官方 Agent Skills 規格與目錄架構）
  - [`notes/2026-11-19-omar-six-skills-web-ai-build-and-verification-gate.md`](./2026-11-19-omar-six-skills-web-ai-build-and-verification-gate.md)（建站六技能與驗證閘）
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](./2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Antigravity 12 項配置與全域技能治理）
  - [`notes/2026-11-21-ben-thompson-write-things-down-harness-memory.md`](./2026-11-21-ben-thompson-write-things-down-harness-memory.md)（Harness 與外部 Markdown 狀態管理）

---

## 0. 原始資料盤點（正文與 7 張圖片：封面、5 張教學截圖、1 張裝飾插畫）

- **Google 生態轉移重要信號**：
  - **Gems 走向 Skills**：Google 自 2026 年 11 月起陸續將個人 Google 帳號的「Gems」升級轉移為「技能（Skills）」，原有的 Gems 會由系統自動重構為技能。呼叫方式依[官方說明](https://support.google.com/gemini/answer/17094296?hl=en)是在輸入框打 `/` 選技能，已更新快捷鍵的帳號改打 `@`；分享來的技能用 `@` 選。實際用哪個符號以自己帳號的介面為準。
  - **免費帳號門檻**：年滿 18 歲之個人免費帳號即可在電腦版 Gemini「自訂」→「技能」分頁中啟用與建立，無需付費訂閱。
- **SKILL.md 成為跨平台統一標準**：
  - Gemini 技能建立支援兩種方式：(1) 與 Gemini 對話生成；(2) **直接上傳包含 `SKILL.md` 的單檔或 ZIP 壓縮包**（可附帶 CSV、PY、TXT、MD 等參考資源檔）。
  - 文章說 `SKILL.md` 可用在 **Gemini、Claude、ChatGPT**；**Antigravity 是本 repo 自行延伸的相容性評估範圍，未經該文章背書**。格式可以帶著走，但功能要逐平台驗證：依[官方說明](https://support.google.com/gemini/answer/17094296?hl=en)與[官方遷移指南](https://support.google.com/gemini/answer/18977944?hl=en)，Gemini 技能的腳本不能連網、不能對外部網站動作；外層可上傳單一 `SKILL.md` 或技能 `.zip` 壓縮包，包內附隨檔案除純文字與程式碼（`.md`、`.txt`、`.csv`、`.py` 等）外，**亦支援 PDF、DOCX、XLSX、PPTX 及 PNG、JPG 等多種圖片格式**；明確排除的是 `.ts`、`.tsx`、`.sql`、舊版 Office（如 `.doc`、`.xls`、`.ppt`）、**包內夾帶的壓縮附件**與音訊影片檔，且全部檔案合計不超過 100 MB。[Agent Skills 規格](https://agentskills.io/specification)另有 `compatibility` 欄位可標示環境需求（工具、套件、網路），有這類需求的技能應填上。
- **「假呼叫」與流程跳步之實戰解法**：
  - **實測痛點（文章作者的單次實測，二手轉述，本 repo 未重測）**：依[同媒體刊載原文](https://1day1ai.bnextmedia.com.tw/articles/gemini-skills-setup-guide)，作者在單次實測中遇到畫面上方已顯示 `Skills: [技能名稱]`，模型第一次仍跳過流程第一步（例如「深度提問設計師」本應先挖掘更高維度的潛在問題，模型卻直接輸出一般學習計畫），第二次改寫提示詞後成功；原文僅記錄這一次跳步與一次改寫成功，未提供發生率數據，跳步原因亦未查證。
  - **文章建議的兩個寫法（待測技巧，效果未經對照測試）**：
    1. **句首寫出技能名稱**：在提示詞開頭直接寫出技能名稱（如 `深度提問設計師，下週有一位新同事...`）。文章沒有提供支持「這樣能強制載入技能」的研究或對照測試；[官方說明](https://support.google.com/gemini/answer/17102773)只寫 Gemini 依技能的名稱與描述判斷相關性，相關才讀完整指示，沒有提到注意力機制或句首點名會強制載入。比較可能的解釋是：技能名稱出現在提示詞裡，讓相關性判斷更容易命中，但這也是推論，要測過才知道。
    2. **邊界與首步強約束**：在句末明確補上最在意的第一步防呆要求（如 `請先依技能流程，幫我找出一個更值得問的問題`）。
- **7 張圖片盤點**（2026-11-25 逐張開啟公開原圖核對）：
  - [封面圖](https://image-cdn.learnin.tw/bnextmedia/image/album/2026-11/img-mcp-3987ebbaf7de1da6.jpg)：貓整理盒子的插畫與 Gemini 免費版技能教學標題，沒有額外技術資訊。
  - 圖 1：Gemini 技能安裝路徑（自訂 → 技能分頁）。
  - 圖 2：建立技能之兩大途徑（對話引導 vs 上傳 ZIP/SKILL.md）。
  - 圖 3：對話輸入框呼叫方式（`@` 選單選擇）。
  - [圖 4](https://image-cdn.learnin.tw/bnextmedia/image/album/2026-11/img-mcp-435f8346eda37227.jpg)：已叫用技能，卻直接產出 Day 1–5 計畫表，是跳過首步的失敗畫面。
  - [圖 5](https://image-cdn.learnin.tw/bnextmedia/image/album/2026-11/img-mcp-3fa75ebaaabbc359.jpg)：句首寫技能名稱後的成功回覆，先列已知事實與待確認假設，再進入深化流程；改寫前的跳步畫面在圖 4，圖 5 本身沒有前後對照。
  - [圖 6](https://image-cdn.learnin.tw/bnextmedia/image/album/2026-11/img-mcp-8bc017f858d2fefe.jpg)：貓帶行李箱站在月台、旁邊有三色列車的裝飾插畫，沒有工具名稱、`SKILL.md` 或技術規格內容。
- **留言與本次修正影響**：文章頁沒有留言區，`source_replies: 0`。原文只列三個平台；修正 Antigravity 的歸屬及圖 5／6 的描述，並補計封面，不把裝飾圖當作跨平台相容性的證據。

---

## 2. 對現有系統的啟發與架構映射

- **加固本機全域規範中的「防假執行」意識**：
  - 文章揭露的使用者痛點（UI 標記已調用技能，但實質輸出卻跳過關鍵步驟），與本機全域協作規範「**回報完成前要真的執行過檢查並貼出輸出、指令成功不等於做對了**」高度同構。
  - 在多 Agent 或外部技能調用時，不能僅依賴「平台回傳已啟用該 tool/skill」，必須對其執行的第一動（Initial Pre-condition）做確定性驗證。
- **SKILL.md 標準化模板相容性**：
  - 本機與各大平台對齊的 `SKILL.md` 格式，在加入 Gemini 平台後進一步確認了其標準地位；但格式相容不等於功能相容，跨平台使用前要逐平台確認工具、腳本、網路與附件限制。「句首寫出技能名稱」可列為待測寫法，有對照測試證明能減少跳步前，不寫進規範。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261122-01`**｜**[優先級：低]** 評估 `SKILL.md` 跨平台（Gemini / Claude / Antigravity）相容性檢查清單，並將「首句技能名稱定錨」與「前置步驟防跳步防呆語法」納入 `docs/cross-platform-skill-spec.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\cross-platform-skill-spec.md`（收錄於集群 3）
  - **執行步驟**：
    1. 整理 Gemini Skills 上傳 `SKILL.md` 與附隨檔案的限制（可收／不收的檔案類型、合計 100 MB、腳本不能連網），以及何時要填 `compatibility` 欄位。
    2. 逐平台列出相容性檢查清單：工具、腳本、網路、附件限制各平台是否支援。
    3. 「句首寫出技能名稱」與「句末補第一步要求」兩個寫法先設計對照測試（同一技能、同一任務，有寫與沒寫各跑多次，記錄有沒有跳過第一步）；有測試結果才寫成建議，沒有就標為待測。
    4. 產出 `docs/cross-platform-skill-spec.md`。
  - **驗收標準（DoD）**：產出 `docs/cross-platform-skill-spec.md`，包含逐平台檢查清單與附官方網址的限制說明；提示寫法附對照測試結果，或明確標為待測，且 `python tools/verify_inbox.py` 驗證通過。
