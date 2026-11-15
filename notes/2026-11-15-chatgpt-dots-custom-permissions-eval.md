---
id: "2026-11-15-chatgpt-dots-custom-permissions-eval"
title: "ChatGPT Dots 自訂權限規則（Settings > Personalization > Permissions）安全邊界評估"
source_url: "https://chatgpt.com/"
source_platform: "Social / OpenAI"
author: "匿名社群分享"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 3
cluster_role: "Dots權限規則評估"
short_title: "ChatGPT Dots權限評估"
tags:
  - chatgpt-dots
  - permissions
  - safety-barrier
  - custom-rules
  - prompt-injection
---

# ChatGPT Dots 自訂權限規則（Settings > Personalization > Permissions）安全邊界評估

- **來源連結**：OpenAI ChatGPT Desktop（`Settings > Personalization > Permissions` / Custom Rules）
- **發布平台 / 作者**：`社群平台` / `匿名分享`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`docs/karpathy-rules-mechanical-hardening-spec.md`](../docs/karpathy-rules-mechanical-hardening-spec.md)（文字規則 vs 機械防線硬化規格）
  - [`notes/2026-11-15-danyuchn-pii-guard-claude-mod-eval.md`](./2026-11-15-danyuchn-pii-guard-claude-mod-eval.md)（本機 Fail-Closed 個資遮罩與外洩防護）

---

## 1. 核心內容摘要與官方機制查證

- **What（社群分享的規則範本）**：
  - 針對 ChatGPT Dots 的「自訂規則（`設定 > 個人化 > 權限`）」提供一段繁體中文安全準則：
    - **純讀取放行**：查看、搜尋、閱讀、分析與整理可直接進行。
    - **變更前必問**：凡涉及刪除、移動、更名、覆寫、改碼、改 DB／系統設定、跑終端機腳本、安裝軟體、對外傳送／寄信／表單／付費／金鑰或任何不可逆操作，皆須先說明「內容、影響範圍、是否可復原」並取得明確同意。
    - **本人親辦紅線**：刪除、付款、帳號權限、密碼、安全設定與不可逆操作不得代為執行；風險不明一律先問。
- **官方機制實況查證**：
  - ChatGPT 桌面版與網頁版確實提供 **Dots**（可跨對話背景運作並依授權存取雲端應用或單一桌面本機的個人代理），並在 `Settings > Personalization > Permissions` 提供自然語言 `Custom Rules`。
  - 官方另設有無法關閉的系統層 **`Auto-review`** 安全網與三層權限分界（自動執行／需明確確認／僅限手動），且**預設不開放存取本機檔案**（須手動在電腦設定開啟 `Allow access`），遇到密碼登入畫面時會暫停畫面擷取交由人工接管。

---

## 2. 技術評估：軟防線價值與三大盲點

1. **Prompt 層規則的本質是「軟防線（Soft Barrier）」**：
   - 官方介面亦明確提示「你的 dot 總會盡力遵守這些規則，但仍可能犯錯」。當對話拉長、遭遇網頁或文件中的 **Indirect Prompt Injection**，或模型誤判風險等級時，自然語言規則仍可能被繞過，無法替代系統層權限隔離（不授權本機全域存取、不授權無關連接器）與外部機械閘門。
2. **「寫規則不能防止自己把金鑰貼進對話」**：
   - 若使用者自己在聊天輸入框貼出 API Key、密碼或個資，該資訊在模型「思考如何遵守規則」之前就已經離開本機並進入雲端上下文紀錄。真正的防線是**憑證不進對話／不進指令列**（改用環境變數或本機秘密管理），搭配本機端前置遮罩。
3. **開發情境的「確認疲勞（Approval Fatigue）」副作用**：
   - 此規則將所有「修改程式碼、執行 Terminal、修改檔案」一律列為每次都要確認，非常適合**一般非工程師使用 ChatGPT Dots 處理日常行政／檔案／瀏覽器任務**；但若直接套用到高頻程式開發代理，會因過多確認彈窗導致使用者麻痺盲按同意，開發環境仍應採「工作 Repo 沙盒內可逆修改放行＋專案外讀寫與高危指令由機械 Hook 攔截」的分層設計。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：本機開發環境已由 `RULE[user_global]`、`harness-guard` 與 `agent-relay/gates.py` 實作更嚴格的機械防線；本篇留存作為 ChatGPT Dots 使用者（或非工程師客戶端電腦）快速貼入 `Settings > Personalization > Permissions` 的防呆範本與安全邊界說明即可。
