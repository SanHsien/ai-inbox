---
id: "2026-11-19-atonny-shen-antigravity-swarm-tw-pack"
title: "Threads 情報與留言評估：Antigravity /swarm 實戰邊界、pipeline 防翻車三原則與 antigravity2-TW 安全提醒"
source_url: "https://www.threads.com/@atonny_shen/post/Df4Jpu8FOoU"
source_platform: "Threads / GitHub"
author: "@atonny_shen (沈建志)"
github_repo: "https://github.com/atonnyshen/antigravity2-TW"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 1
source_replies: 35
source_reviewed_at: "2026-11-20"
status: archived
cluster: 1
cluster_role: "Swarm實戰與繁中包"
short_title: "Antigravity蜂群與繁中"
tags:
  - antigravity
  - swarm
  - teamwork
  - localization
  - multi-agent
  - threads
---

# Threads 情報與留言評估：Antigravity /swarm 實戰邊界、pipeline 防翻車三原則與 antigravity2-TW 安全提醒

- **來源貼文**：[Threads 原貼文（`@atonny_shen` 沈建志）](https://www.threads.com/@atonny_shen/post/Df4Jpu8FOoU)（原分享連結 `https://www.threads.com/share/BAaOLyUtB5`）
- **提及 GitHub**：[`atonnyshen/antigravity2-TW`](https://github.com/atonnyshen/antigravity2-TW)（Google Antigravity 台灣繁體中文在地化套件；2026-11-20 查為 121 Stars／9 Forks，是簡體中文版 [`qqxpee/antigravity2-cn`](https://github.com/qqxpee/antigravity2-cn) 的 fork）
- **發布平台 / 作者**：`Threads` / `@atonny_shen`（`2026-11-18`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-18-gemini-4-carbon-argon-swarm-evals.md`](./2026-11-18-gemini-4-carbon-argon-swarm-evals.md)（Gemini 4 Carbon / Argon 與 Antigravity `/swarm` 評測）

---

## 1. 原始資料盤點（主文、釘選續樓、預覽卡片與 35 則串內留言與回覆）

- **主貼文與釘選續樓**：
  1. **Antigravity `/swarm` 模型分工推薦**：`Orchestrator (Carbon)` 負責規劃協調與審查，搭配 `Hydrogen` 高速並行執行，能即時觀察各 agent 對話與執行路線圖。
  2. **`antigravity2-TW` 繁中在地化套件**：補齊翻譯並支援 Mac/Win 自動化背景守護（宣稱更新不掉中文化）；釘選回覆教導使用者讓 AI 下載該 repo 並依 `AI_INSTALL_GUIDE.md` 引導安裝。
- **圖片／預覽卡片（1 張）**：GitHub 連結預覽卡片顯示 `atonnyshen/antigravity2-TW`（113 Stars / 9 Forks，支援獨立 IDE 與 VS Code）。
- **網友回應與技術討論（登入後讀完，見下方「登入補讀完成」）**：
  1. **防毒軟體攔截實例（`@cccwilkins` 回報）**：留言實測回報「防毒把它擋住了，連 `config.json` 都被關起來」；作者回覆已移除易引發誤判元件並請更新最新版。
  2. **`/swarm` 適用邊界與不翻車條件（`@zz950907` 與 `@atonny_shen`）**：
     - `/swarm` 真正省時的不是開越多 agent，而是**可視化看到每條線在做什麼、卡在哪裡**。
     - **適用前提**：任務必須「**可切開、彼此不依賴、驗收標準可寫死**」（例如大批量獨立翻譯比對、大量文稿審閱、無依賴多檔案修改搭配 `Verifier`）；小 bug 用單一 agent 反而更快。
     - **作者自製 `pipeline skill` 補強三痛點**：分包編號＋記錄任務版本（防重複派工）、中斷或額度用完後的續跑規範、回報完成前的交付檢查。
  3. **`/swarm` vs `/teamwork` 體感差異（`@pliantart` / `@atonny_shen` / `@hanbingjheng`）**：
     - `/teamwork` 偏以天為單位、有順序分工的大型專案（但作者體感未見類似蜂群面板）；`/swarm` 偏以小時為單位、去中心化多併發獨立任務。
- **2026-11-20 補讀（最新排序，未登入只顯示 14 則）**：
  1. `@kacho_life` 回報 Windows 點兩下 `.bat` 安裝會出現亂碼、裝不起來；作者請他改丟給 Antigravity 對話讓 AI 跑（成功），之後回覆亂碼已修正。
  2. `@gentlemen_10.06` 指出 `/swarm` 的額度吃的是 `Carbon`，不然會更實用——是成本面的實測意見。
  3. `@pohanschiu` 提另一種玩法：開兩個不同模型互相批評。`@00fji` 問 `/teamwork` 與 `/swarm` 的差別。
  4. 其餘是收藏、道謝；有一則稱讚留言附了購物網站連結，疑似導購帳號，不採計。
- **2026-11-20 登入補讀完成**：貼文計數 39 則，平台顯示 37 則已全部讀完，差 2 則登入後也不顯示。37 則＝串內 35 則（作者釘選續樓 1 則加 34 則留言與回覆，其中作者回覆 10 則、`meta.ai` 自動回覆 4 則）加 2 則引用貼文（`@garlia.t` 道謝、`@shouchenho` 稱讚 Google 便宜大碗）。熱門、最新兩種排序都捲到底，列出同一批人；所有「顯示回覆」都已展開。新讀到的重點：
  1. **作者說明為何不能走 VS Code 語言包（`@yie_qq` 問與 Open VSX 中文包的差別）**：作者回覆，Open VSX 的 Language Pack for Antigravity 是給 VS Code 分支版的 Antigravity IDE 用的；現在主推的 Antigravity 2.0 是 Windsurf 核心團隊加入 Google 後另外打造的 Electron App，不是 VS Code 分支，沒辦法用語言包機制，只能用字典直接把繁中注入 App 的資源檔，也就是這個專案在做的事。這與官方 repo 查到的「修補 `app.asar`」一致，也說明它不是官方管道，介面更新後要靠常駐守護重套。作者另建議優先用 2.0，IDE 與 VS Code 擴充套件版的功能更新較慢。
  2. **官方尚無原生繁中（`@theodore039`）**：留言問 Google 原生的中文介面還要等多久，作者的回應是舊版不成熟、有很多漏譯，建議更新並開背景守護。沒有人提到官方時程。
  3. **防毒事件有後續**：`@cccwilkins` 回報被擋後，作者回覆已移除易觸發誤判的元件，並貼出「請幫我下載 … 依 `AI_INSTALL_GUIDE.md` 檢查與安裝」的一句話安裝法；`@cccwilkins` 後來回「感恩分享與修復」，沒有說更新後是否還被擋。作者另在 `@emily_togola` 的串裡把懶人安裝法說成「貼連結、打請替我安裝、同意同意同意、重啟」，這種一路同意的流程正是零信任規範要擋的型態（見第 2 節），列入風險欄。
  4. **`meta.ai` 自動回覆共 4 則（不是作者、不是權威）**：解釋 `/swarm` 作用、附和作者的體感，以及對 `@batmanspawn777` 問「能不能跟 Hermes 結合」說「可以，而且是現在最強的組合」，並舉了 Hermes 當 sub-agent 的例子。沒有任何來源佐證，不採計。
  5. **其餘**：`@hanbingjheng` 補充 `/teamwork` 依文件是有順序分工、`/swarm` 是去中心化多併發，但中小任務體感差不多；`@ericshen19555` 指出作者把 Harness 打成 Harmness（作者承認筆誤）；`@emily_togola` 的留言附酷澎購物連結，疑似導購，不採計，未點開；其餘是稱讚、收藏與愛心。沒有人貼出 `/swarm` 的失敗案例或額度數字。
- **2026-11-20 查核官方 repo（改正原稿的「防毒誤判」）**：
  1. **不是單純誤判**。`CHANGELOG.md` 的 v3.7.0（2026-11-19）寫明這版**移除了 `proxy_config` 的 DLL 注入（`version.dll`、`dbghelp.dll`、`config.json`）、盲目的 `taskkill /f` 與 `powershell -ExecutionPolicy Bypass`**，並把根因之一列為「防毒啟發式特徵」。`@cccwilkins` 說連 `config.json` 都被隔離，對得上這組檔案。也就是舊版真的帶 DLL 側載元件，防毒攔它有道理；作者在留言裡稱為「容易引發誤判的元件」。
  2. **運作方式**：直接修補 Antigravity 的 `resources/app.asar`（原版備份成 `app.asar.bak`），背景守護每 5 分鐘巡檢官方更新後重套，每 24 小時向 GitHub 取翻譯資料。
  3. **自動更新反覆**：v3.7.1（11-19）加入守護程式**自動下載並更新自己的程式碼**；隔天 v3.7.2（11-20）又整個移除，並在更新紀錄裡承認 v3.7.1 有「任意 ZIP 選取漏洞」。兩天內連發三版，安全設計還在快速變動。
  4. **亂碼修正對得上**：v3.7.0 把 `.bat` 改成純 ASCII 加 CRLF，根因是換行與編碼。
  5. **`AI_INSTALL_GUIDE.md`**：內容是寫給 AI 助手的指令——先唯讀檢查、再請使用者從 1～4 選項決定才動手。設計上有先問再做，但「叫 AI 下載 repo 並照裡面的文件執行」本身就是把外部文件當指令，仍屬本機零信任規範要擋的型態。
  6. 星數原稿寫 113，2026-11-20 查為 121。
- **原始資料對分析的影響**：主貼文只講了優點與一鍵安裝；留言區與官方更新紀錄補齊了兩項關鍵現實——(1) `antigravity2-TW` 舊版帶 DLL 側載元件而被 Windows 防毒攔截，v3.7.0 才移除；(2) `/swarm` 若未先將任務切開與寫死驗收，開多 agent 只會浪費額度與增加合併成本。

---

## 2. 對現有系統的啟發與安全評估

- **`/swarm` 實戰準則對齊**：
  - 貼文與 `@zz950907` 總結的三大原則（分包編號防重派、額度中斷續跑規範、結案前實查驗收），與本機全域協作規範「**派工要掌控到完成**」及 `swarm` / `orchestration` 規則完全一致。
  - **高階 `Carbon` 規劃審查＋`Hydrogen` 高速並行**的分工模式，可在後續遇到「數十至數百份獨立檔案審閱／無依賴批量修改」時直接採用。
- **`antigravity2-TW` 零信任與實務評估**：
  - 依全域規範硬閘門，**禁止未經靜態安全審查就讓 AI 直接依 `AI_INSTALL_GUIDE.md` 下載並啟用改寫 IDE 本體檔案與常駐背景守護的腳本**；考量繁體中文開發環境僅限於輸出語言，IDE 本身維持原廠英文介面更穩定、沒有防毒攔截與更新破壞風險。
  - 補充理由（2026-11-20）：這個套件會修補 `app.asar`、常駐排程，舊版還帶過 DLL 側載與自動更新自身程式碼（都已移除），上游是簡體中文版專案；即使要評估，也必須指定版本並先過靜態安全檢查。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：`/swarm` 派工紀律已由本機「派工要掌控到完成」規範覆蓋，且本機暫無將 Antigravity IDE 介面積極中文化（或承擔背景守護修改風險）的需求；歸檔留存 `/swarm` 實戰邊界與 `antigravity2-TW` 防毒／零信任提醒即可。
