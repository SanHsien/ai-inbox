---
id: "2026-11-15-rei-four-ai-work-modes-claude-codex-eval"
title: "Eugenia叡一「4 種 AI 工作模式完整解析」：Chat vs Cowork/Work vs Claude Code/Codex 選型與落地陷阱評估"
source_url: "https://youtu.be/daHC9dnhH-w"
source_platform: "YouTube"
author: "Eugenia叡一（@EugeniaWu0）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 3
cluster_role: "四種AI工作模式地圖"
short_title: "叡一四種AI工作模式"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 36
source_replies: 6
tags:
  - claude-code
  - codex
  - claude-cowork
  - chatgpt-work
  - workflow-routing
  - youtube
---

# Eugenia叡一「4 種 AI 工作模式完整解析」：Chat vs Cowork/Work vs Claude Code/Codex 選型與落地陷阱評估

- **來源連結**：[YouTube 原片（音訊 1,453 秒）](https://youtu.be/daHC9dnhH-w)
- **發布平台 / 作者**：`YouTube` / `Eugenia叡一（@EugeniaWu0）`（2026-09-27 上架；原筆記誤記為 Rei）
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md`](./2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md)（ChatGPT Work 與 Codex Skills 實務比較）
  - [`notes/2026-11-15-openai-codex-plugin-cc-collaboration.md`](./2026-11-15-openai-codex-plugin-cc-collaboration.md)（Claude Code × Codex 雙 AI 協作）

---

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**（2026-11-17 抽格補看，全片每 40 秒一格共 36 格；其餘依逐字稿與說明欄 14 個章節時間戳）：
  - 畫面是作者對鏡頭講解，穿插圖卡；沒有任何實際操作 Claude 或 Codex 的螢幕錄影。逐字稿提到的「AI 剪輯系統」那段，畫面也只是示意圖（專案資料夾樹、Whisper／ElevenLabs／FFmpeg 的名稱卡、「一句自然語言啟動完整流程」的清單），看不到真實執行結果。
  - 圖卡內容與逐字稿一致：「四個工具一條線看懂」把兩家各分成一般工作（Cowork／Work）與專案環境（Claude Code／Codex）；「三種工作方式怎麼選」是快速提問、文件成果、專案環境三列對兩家的對照表，就是本篇第 1 節那張表的來源。
  - 方案圖卡寫的是 Claude Pro 20 美元、Max 5x 100 美元、Max 20x 200 美元，並註明 Pro 含 Cowork 與 Claude Code；只列了 Claude 的價位，沒有列 OpenAI 的。
  - 後段圖卡依序是「不只生成，還要驗證」「不是固定一包 Token」（列了資料量、任務長度、模型、修改次數等影響用量的因素）「好資料加清楚規則才有穩定成果」「做得更快之前，先選對方向」，最後兩張是作者課程（SMART 自媒體創業系統、完整研討會）的宣傳畫面。
- **作者留言補充**：
  - 說明欄開頭與結尾都在導流到作者的「SMART 1 對 1 陪跑」面談申請，本片同時是課程行銷內容。影片 2026-09-27 上架，查看時約 4.9 萬次觀看。
  - 作者回覆網友：自己用每月 100 美元方案，Chat、Cowork、Claude Code 都用，額度通常用不完；並說明長對話、附件、模型、思考強度與工具操作都會增加消耗。
- **網友留言重點**（6 則全讀）：`@userrock-s7b` 說 Claude 等 5 小時重置後只問一句就用掉 15% 額度，不敢用 Cowork 與 Claude Code；並轉述 ChatGPT 自己的說法「Chat 額度與 Work、Codex 分開算」（未查證，是模型自述不是官方文件）。`@martintsai777` 問「Antigravity 呢？」沒有得到回答。其餘是道謝。
- **對分析的影響**：
  1. **作者名更正**：頻道是「Eugenia叡一」（`@EugeniaWu0`），不是「Rei」；原筆記的名字應是逐字稿聽寫的音。標題、作者欄、短標題都已改。
  2. 第 1 節訂閱原則補上作者自己用 100 美元方案的說法，以及網友「一句話吃 15%」的反例：額度感受因人而異，影片的方案建議只能當起點。
  3. 補記本片有課程導流；第 1 節末的「商業提醒」正是導流段落的鋪陳。
  4. 影片只比 Claude 與 OpenAI 兩家，沒有談 Antigravity；結論仍是封存、不開任務。
  5. **2026-11-17 抽格後補一個限制**：第 1 節表格裡「作者將 5 支 YouTube 影片交由 Codex 跑轉錄與剪輯，自身僅花 1 小時」只有口述與示意圖，畫面沒有出現實際流程或成品對照，屬作者自述。已在表格該格標明。價位圖卡只有 Claude 一家，「兩家同一份訂閱都涵蓋三種模式」的 OpenAI 那半是口述，沒有圖卡佐證。

---

## 1. 核心內容摘要（基於 CUDA 轉錄逐字稿）

- **核心命題**：多數人把「Claude 還是 Codex 誰比較聰明」當成選型標準，但真正決定效率的是**選對工作模式**。只要選錯模式（例如在一般 Chat 視窗一份一份上傳檔案處理多檔專案），原本 5 分鐘的工作就會被拉長成數十分鐘。
- **三層工作模式對照表**：

| 層級定位 | Anthropic（Claude） | OpenAI（ChatGPT / Codex） | 適用任務類型 |
| :--- | :--- | :--- | :--- |
| **對話顧問層** | Claude Chat | ChatGPT Chat | 快速提問、改一段文字、即時腦力激盪 |
| **知識交付層** | Claude Cowork（片尾註記已整合為新版 Claude 內建長任務能力） | ChatGPT Work | 跨資料整理、研究彙整、產出報告／簡報／試算表 |
| **專案環境層** | Claude Code | Codex | 深入本機資料夾、讀寫多檔、執行 CLI 指令、做網站與自動化管線（如作者將 5 支 YouTube 影片交由 Codex 跑轉錄與剪輯，自身僅花 1 小時下指令與驗收；作者自述，畫面只有示意圖、沒有實際流程） |

- **訂閱選擇原則（\$20 / \$100 / \$200）**：兩家各自同一份訂閱即可涵蓋上述三種模式，差別主要在額度與併發任務量；輕度從 \$20 起步，高頻日常內容＋網站＋剪輯流程建議 \$100，長期多大型任務併發再看 \$200。作者在留言區說自己用 100 美元方案、三種模式都用也用不完；同一則留言串裡有網友回報 Claude 問一句話就用掉 5 小時額度的 15%，可見額度感受差異很大。重點不在比較單次生成能力，而是觀察「誰能自己跑測試、發現錯誤並修正、讓你安全檢查 diff」。
- **三大實務陷阱**：
  1. **功能存在 ≠ 自己帳號／作業系統可用**：Web、Mac、Windows、Desktop App 與各付費方案權限更新步調不一，須以當前環境實測為準。
  2. **權限一把梭風險**：切忌一開始就把整台電腦與所有帳號授權給 AI，應從獨立資料夾與低風險任務開始，並確保重要成果由人類檢查。
  3. **把 Skill 當萬靈丹**：Skill 只會照既定規則與資料跑；若目標資料夾混亂、來源未標註、完成定義（DoD）不明，AI 只會更快產出彼此無關的內容。
- **商業提醒（說明欄顯示本片同時導流到作者的 1 對 1 陪跑課程，這段是鋪陳）**：AI 把產製門檻壓低後，同質化內容會迅速飽和；真正拉開差距的是工具之前的「市場與對象選擇、最小產品測試、完整變現路徑」。

---

## 2. 啟發與適用性評估

- **對現有知識庫與架構的印證**：
  1. 影片點出的三大陷阱（平台差異、權限一把梭、Skill 需有明確資料與 DoD 治理）與 `C:\GitHub\ai-inbox` 的設計完全吻合：`RULE[user_global]` 的專案外隔離、Windows 11 原生實測規定，以及每項任務強制定義 DoD，正是為了解決這三個問題。
  2. 適合作為日後向**非工程師／一人公司合作對象**說明「Chat / Work / Code-Codex 分層差異」的教學對照教材。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：本片屬入門至中階的工作模式心智地圖與自媒體商業思維整理，未提出新的可實作工具或框架缺口；現有本機環境的跨 Agent 路由、Windows 隔離與 Skill 治理已涵蓋更細緻的實作規範，保留本篇作為教學／選型參考即可。
