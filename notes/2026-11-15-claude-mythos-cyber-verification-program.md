---
id: "2026-11-15-claude-mythos-cyber-verification-program"
title: "Threads 情報評估：個人 Claude Max 透過 Cyber Verification Program 申請 Mythos 5.1/5.2 資格"
source_url: "https://www.threads.com/@myzenstar365/post/DfwdlZYHTT6"
source_platform: "Threads"
author: "@myzenstar365"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 1
cluster_role: "Claude資安存取"
short_title: "Mythos資安資格申請"
source_reviewed_at: 2026-11-17
source_review: full
source_images: 2
source_replies: 20
tags:
  - claude
  - claude-mythos
  - cyber-verification-program
  - cybersecurity
  - claude-max
  - threads
---

# Threads 情報評估：個人 Claude Max 透過 Cyber Verification Program 申請 Mythos 5.1/5.2 資格

- **來源貼文**：[Threads 原貼文（@myzenstar365）](https://www.threads.com/@myzenstar365/post/DfwdlZYHTT6)（原分享連結 `https://www.threads.com/share/BADYTd4ZoJ`）
- **發布平台 / 作者**：`Threads` / `@myzenstar365`（`2026-11-15`）
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-12-austinlo49-claude-duet-resets-fable52.md`](./2026-11-12-austinlo49-claude-duet-resets-fable52.md)（Fable 5.2 與 Mythos 5.2 發布公告與配額策略）

---

## 0. 原始資料盤點

> 2026-11-17 用未登入的瀏覽器重看 Threads 原貼文，2 張圖都放大看過，頁面顯示 20 則留言，全部讀到。

- **作者圖片**：
  - 圖 1：手機 App「更多模型」清單截圖（標題列顯示是一個 Remote Control 工作階段）。依序列出 Fable 5.1、Haiku 4.5、Sonnet 5、Opus 5、Fable 5、Opus 4.8、Opus 4.7、Opus 4.6、Sonnet 4.6、Mythos 5.2、Mythos 5.1。Mythos 兩個型號排在清單最後。
  - 圖 2：一杯手搖飲的照片，與主題無關（作者留言說只是順便分享；好幾位網友誤以為是拿這張照片過審）。
- **作者留言補充**：
  - 回覆兩位網友：用個人的 Max 就能申請，不需要 Ultra 或商業方案。
  - 說明是先通過審核、後來才喝飲料，照片與審核無關。
- **網友留言重點**：
  - `matt.cheng0416`：通過後「什麼都不能用」「動不動就撞到防火牆」。
  - `oldmimi_0804`：個人用戶的 Mythos 安全限制還是很嚴，除非另外申請紅隊資格。
  - `siliconsays.tw`：用途要把範圍寫清楚（例如只檢查自己擁有的網域），之後使用比較不會踩線。
  - `franky_tzuyang` 問計費是否與 Fable 相同，`youwei_0202` 答是，`clubababyotter` 補充似乎也能用 Fable 的重置券；都是網友說法，未查證。
  - `this_is_me_404`：實際要用還得另外加錢；但拿來檢查自己作品的漏洞很好用。「要加錢」指什麼沒有說明，未查證。
  - `hackertale`：香港用戶申請不了。
  - 其餘是玩笑與道謝。
- **對分析的影響**：
  - 「個人 Max 即可申請」多了作者兩則回覆佐證。
  - 新增一個原筆記沒有的重點：**通過 ≠ 限制解除**。兩位網友回報個人層級仍常被擋，要更寬的權限得另申請紅隊資格。已寫進第 2 節「使用邊界提醒」，並把「申請就能解決誤觸安全拒答」的語氣改保守。
  - 計費、重置券、要不要加錢都只有網友說法，列為未查證，不寫進結論。
  - 封存結論不變。

---

## 1. 核心情報與官方機制核實

### 貼文實測經驗（@myzenstar365）
- **帳號資格**：**個人 Claude Max 帳號即可申請**（不需商業版或 Ultra）。
- **申請流程**：
  1. 開啟 Anthropic 官方 **Claude Cyber Verification** 說明頁 / 入口。
  2. 選擇 **Cyber Verification Program (CVP)** 並點擊 **Apply**。
  3. 選擇個人身分，照實填寫防禦性資安用途（例如：檢查自己網站的安全性／弱點排查）。
  4. 以實體證件完成 KYC 身分驗證並送出。
- **審核速度**：作者實測送出後不到半小時通過，模型選單即出現 **Mythos 5.2** 與 **Mythos 5.1**（與 Fable 5.1 / Opus 5 / Sonnet 5 等並列）。

### 官方 Cyber Verification Program (CVP) 與 Mythos 定位查證
- **Fable vs. Mythos 同源差異**：
  - Anthropic 官方將同底層前沿模型拆分為 **Claude Fable**（一般公開版本，預設啟用嚴格安全護欄）與 **Claude Mythos**（受控釋出版本，放寬合法資安防禦／弱點分析所需的雙重用途限制）。
- **分級與限制（重要實務提醒）**：
  - **Defense Access（個人/團隊防禦層級）**：開放給企業資安團隊、開源維護者與通過 KYC 的個人研究者，用於防禦性資安審查、弱點排查與事件回應。
  - **禁止與監控條款**：CVP **不解除** 純惡意用途限制（如勒索軟體或 C2 基礎設施生成），且受控存取預設包含較嚴格的安全監控與資料保留政策（如 30 天安全監控保留，依官方企業/驗證條款而定）。

---

## 2. 對現有系統與個人工作流的評估

- **情報價值**：補齊了 `2026-11-12` 筆記中「Fable 5.2 vs. Mythos 5.2」缺少的實務開通門檻細節——證實個人 Claude Max 帳號即可申請 CVP Defense Access，無須企業合約。
- **使用邊界提醒**：
  - 若僅做一般軟體工程與日常開發，**Claude Fable 5.2 / Opus 5** 已具備同級程式與推理能力，不需為了「解鎖更強模型」而貿然提交實體證件 KYC 與接受額外安全監控保留條款。
  - 若確實有針對自有網站、開源專案進行深度弱點審查或誤觸安全拒答的需求，再依上述 4 步申請 Defense Access；用途欄把範圍寫清楚（例如只檢查自己擁有的網域）。
  - **通過不等於限制解除**：原貼文留言有兩位網友回報，個人層級通過後仍常被安全機制擋下，要更寬的權限得另外申請紅隊資格（網友回報，未向官方查證）。申請前不要預期它能解掉所有拒答。
  - 計費是否與 Fable 相同、是否要另外加錢，留言區只有網友說法，未查證。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬於個人帳號資格與實體證件 KYC 手動申請事項，無須開發自動化工具或修改現有環境；保留本筆記作為日後若有自有專案深度資安盤點需求時的申請指引與風險評估依據。
