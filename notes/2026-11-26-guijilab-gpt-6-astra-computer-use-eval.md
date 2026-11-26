---
id: "2026-11-26-guijilab-gpt-6-astra-computer-use-eval"
title: "YouTube「GPT-6 Astra 自己動鼠標替你幹活」逐字稿拆解：Computer Use、授權鑰匙邊界與 9.9 億 Token 帳單警示"
source_url: "https://www.youtube.com/watch?v=bq5cxNqzzeY"
source_platform: "YouTube"
author: "硅基实验室 (@GuijiLab)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-26"
status: archived
cluster: 1
cluster_role: "Astra成本與授權"
short_title: "GPT-6 Astra工作流拆解"
tags:
  - gpt-6-astra
  - chatgpt-work
  - computer-use
  - token-economics
  - human-in-the-loop
  - youtube
---

# YouTube「GPT-6 Astra 自己動鼠標替你幹活」逐字稿拆解：Computer Use、授權鑰匙邊界與 9.9 億 Token 帳單警示

- **來源影片**：[GPT-6 Astra 自己动鼠标替你干活：一场会开完，纪要待办幻灯片一起交](https://www.youtube.com/watch?v=bq5cxNqzzeY)（`2026-09-04` 發布，片長 `07:30`，242 次觀看、5 讚、0 則留言）
- **相關筆記**：
  - [ChatGPT-6.1 生態系全景評測：GPT Work、Codex 與 Skills](2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md)
  - [GPT-6.2 Astra 與 Sol 雙模型路由架構](2026-11-20-gpt-6-2-astra-sol-routing-eval.md)

---

## 核心結論

這支影片是針對 2026-09-03 OpenAI 發布 `GPT-6 Astra` 與 `ChatGPT Work` 官方資料的精煉拆解，點出從「問答模型」跨入「桌面與跨系統自主執行」的三個關鍵結構：**以 Computer Use 接管無 API 老系統、以細粒度授權勾選與 Human-in-the-loop 控管風險、以及長鏈自主執行的 Token 帳單指數放大效應**。因屬發布初期的功能與定價評析（且後續已有 GPT-6.1 / 6.2 實戰筆記落地），歸檔作為成本估算與授權設計參考，不另開實作任務。

---

## 一、核心能力演進（影片拆解重點）

1. **跨產物管線銜接**：不再只交單一張圖或文字草稿，而是能讓前一階段輸出直接進入下一工序（例如會後逐字稿一次產出可編輯的執行摘要文件、含負責人與截止日的行動項表、以及排版完成的簡報原件）。
2. **Computer Use 接管網頁與舊系統**：模型直接看螢幕、移動滑鼠與敲鍵盤（如填寫 Workday 請假單至最後一步），使「沒有開放 API 的十幾年老系統」只要人類點得動，AI 就能操作。
3. **「流程存成技能」與確認停靠點**：
   - 在最終提交前強制停在「待確認清單（Human-in-the-loop）」，企業管理員開關預設關閉。
   - 支援把跑通的步驟存成可重複呼叫的 Skill（首次人教、二次自動跑），但同時警示「一條存錯的流程也會被照樣執行一百遍」。

---

## 二、權限與 Token 經濟學帳單核實

- **授權即邊界**：在插件目錄（螢幕操作、簡報、信箱、雲盤）安裝整合時，授權勾選框決定了它「能讀哪些檔、能否新建、能否對外發送」；便利性與出事時的波及半徑完全成正比。
- **官方價目表算術對照（片中註記採 2026-09-03 `platform.openai.com/docs/pricing` 抓取）**：
  - `gpt-6-astra`：輸入 `\$10` / 輸出 `\$50` 每百萬 token（長上下文 `\$20 / \$75`、優先 `\$20 / \$100`、批量 `\$5 / \$25`、快取輸入 `\$1`）。
  - 輸出單價為同表 `gpt-5.6-terra`（`\$12`）的 **4.2 倍**、`gpt-5.6-luna`（`\$1.2`）的 **41.7 倍**。
  - **9.9 億 Token 案例警示**：官方開發者初體驗畫面顯示 10 路並跑研究面板耗用 9.9 億 token，換算最便宜快取價亦近 `\$1,000`、若按輸出價計算逼近 `\$50,000`——真正決定費用的不是單價，而是讓 Agent 自主連跑的時間長度。

---

## 三、評估與適用分級

- **適用分級建議**：單純問答、寫文案與翻譯繼續使用低價檔位即可；適合導入高階自主執行者，為「每週都有固定重複、跨多網站搬運與對帳流程」的場景，且須先小規模試跑一周觀察實際帳單。
- **任務評估**：已有更近期的 GPT-6.1 / 6.2 路由與 Codex Skills 筆記追蹤落地，本篇設為 `archived`。
