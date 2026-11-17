---
id: 2026-10-23-web-to-app-android-packaging
title: "WebToApp 解構：手機端把網站打包成 Android App、內建 Node/PHP/Python 執行環境、AI Agent 生成與 AAB 簽名上架，及接案變現評估"
source_url: "https://www.facebook.com/permalink.php?story_fbid=pfbid08GLCiREBieh5tyzwonWwssu622TDG7HG2qpiJz3Esi2gCcjFk2SyKMSyAhjGEN1Dl&id=61588107756334"
source_platform: "Facebook 粉絲專頁（一人公司研究所）/ GitHub"
author: "shiaho777"
github_repo: "https://github.com/shiaho777/web-to-app"
analyzed_at: 2026-10-23
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: "3"
cluster_role: "逆向工程與軟體封裝"
short_title: "WebToApp 網站轉 Android App"
source_review: full
source_reviewed_at: 2026-11-18
source_images: 17
source_replies: 22
tags:
  - webtoapp
  - android
  - apk
  - aab
  - webview
  - ai-agent
  - freelance
---

# WebToApp 解構：手機端把網站打包成 Android App、內建 Node/PHP/Python 執行環境、AI Agent 生成與 AAB 簽名上架，及接案變現評估

- **來源連結**：[WebToApp README_CN](https://github.com/shiaho777/web-to-app/blob/main/.github/docs/README_CN.md)
- **官方 GitHub 倉庫**：[`shiaho777/web-to-app`](https://github.com/shiaho777/web-to-app)
- **發布平台 / 作者**：`GitHub` / `shiaho777`
- **分析日期**：`2026-10-23`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-19-android-official-skills-google-coding-agent.md`](./2026-10-19-android-official-skills-google-coding-agent.md)（Android 官方 Agent Skills）
  - [`notes/2026-10-17-claude-plugins-official-directory.md`](./2026-10-17-claude-plugins-official-directory.md)（Claude Code 官方插件目錄）

---

## 0. 原始資料盤點

> 2026-11-18 補讀：**找回原貼文**。用 Facebook 貼文搜尋找到「一人公司研究所」粉絲專頁 2026-10-19 的貼文：<https://www.facebook.com/permalink.php?story_fbid=pfbid08GLCiREBieh5tyzwonWwssu622TDG7HG2qpiJz3Esi2gCcjFk2SyKMSyAhjGEN1Dl&id=61588107756334>。粉專在留言貼的連結就是本筆記原本的 `source_url`（簡中版 README）。`source_url` 已改成這則貼文；原值 `https://github.com/shiaho777/web-to-app/blob/main/.github/docs/README_CN.md` 仍列在文首「來源連結」，repo 另記在 `github_repo`。
>
> - **貼文文字**：介紹 WebToApp 能在手機上跑 Node.js、PHP、Python，把 WordPress 塞進 APK，打包、簽名到產出可上架的 AAB 都不需要電腦；內建 AI Agent；當時 GitHub 6,850 顆星、Unlicense 授權。「一人公司視角」那段說最直接的變現是接案，幫店家把官網、菜單、預約頁打包成 App，一次收幾千到上萬元，「展示即成交」。
> - **作者圖片 1 張**：App 的「My Apps」清單畫面（列出幾個已建立的網站 App 與「Create App」按鈕），是 README 的示範截圖，不是粉專自己的實測。
> - **留言**：貼文計數 17 則，「由新到舊」排序捲到底、所有回覆都展開，17 則全部讀完。
>   - **粉專承認由 AI 代管**：有人要求真人回覆，粉專回說整個頻道都是 AI 助理接管的；還有人貼提示詞想套出它的模型資訊。
>   - **質疑**：有人稱它是「垃圾製造者」並獲得附和；有人問這和 PWA 有什麼差別，沒有人回答；有人說隨便一個 AI agent 就做得到；有人認為把後端放在前端跑不是好做法。
>   - 有人求 iOS 版，粉專回不可能有；另一位說網頁加到主畫面就行。
> - **對分析的影響**：貼文的接案行情（一次幾千到上萬、展示即成交）出自 **AI 代管的粉專文案**，沒有任何實際接案紀錄；留言也沒有人回報真的靠它接到案。這些數字不可當報價依據，已在第 2 節補註。「和 PWA 有何差別」是接案前要先回答客戶的問題，`docs/web-to-app-freelance-workflow.md` 的需求確認步驟應涵蓋（只回報，不改已完成任務）。

> 2026-11-16 重審：來源是 GitHub README（簡中版）。原筆記提到的「貼文」沒有留下連結，無從回看。這次看了 README 全文、README 內 16 張 App 截圖，以及 issue #1496、#308 的留言共 5 則與 #1582 的標題（無留言）；Discussions 共 13 則，多數無回覆。

- **作者圖片**：共 16 張手機截圖（圖示與徽章不計），依 README 的說明文字與畫面內容整理：
  - 圖 1～4：主頁的應用清單、12 種應用類型的建立面板（網頁、多站、HTML、離線包、前端專案、WordPress、Node.js、PHP、Python、Go 等）、單一應用的操作選單（建置 APK、分享 APK、匯出原始碼、清快取、刪除）、工具箱選單（Agent、AI 設定、外掛、本地建置環境、連接埠管理、瀏覽器核心、Hosts 封鎖、Google Play、資料備份）。
  - 圖 5～11：編輯器各卡片——圖示／名稱／網址與站點分析、啟動碼（本地啟動碼或線上驗證、每次啟動都驗證）、全螢幕與方向、懸浮視窗、啟動畫面／背景音樂／公告彈窗／自動翻譯、外掛與廣告攔截、自訂 DNS／裝置偽裝／開機自啟／APK 匯出設定。
  - 圖 12～13：Agent 介面與一段實際對話，Agent 先問要包哪種 App（網址包裝、HTML、後端服務、媒體應用）再動手。
  - 圖 14：本地建置環境頁，顯示核心工具鏈「未安裝」，Node.js、npm 等要另外下載。
  - 圖 15～16：內建外掛清單（內容增強、深色模式、元素封鎖、頁內搜尋、媒體下載、隱私保護等）與「關於」頁。
- **作者留言補充**：issue #1496（Google billing）中，repo 擁有者表示正考慮**移除 Google Play 相關功能**，原因是它妨礙 F-Droid 上架與合規，之後可能改放到別的 App 實作。#308 中擁有者表示準備同時上架 F-Droid 與 Google Play（尚未完成）。
- **網友留言重點**：#308 有使用者要求上架 F-Droid；#1582 回報「CORS 繞過」功能會把跨來源的 POST 送出兩次（非冪等請求重送），目前未修；其餘 open issue 為功能請求。
- **對分析的影響**：
  - 圖 6、圖 11 顯示產出的 App 可加啟動碼、裝置偽裝、廣告攔截等功能；圖 14 顯示 Node 等執行環境不是開箱即有，要在手機上另外下載。已補進第 2 節。
  - 擁有者考慮移除 Google Play 功能這一點，直接影響「AAB 簽名上架」的賣點與 `docs/web-to-app-freelance-workflow.md` 的上架步驟；已在第 2 節「風險面」與第 3 節「不採納」各補一句。`T-20261023-04` 已完成，狀態不動，是否要回頭修訂該文件列在重審回報裡交整合者決定。
  - #1582 的重複送出問題補進風險面：表單送出、下單類網站若開啟 CORS 繞過要先測。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：開源作者 `shiaho777`；授權 Unlicense（公有領域，可商用改作）；貼文稱約 6,850 顆 Stars（查證時點數字，會變動）。
- **What**：把網站打包成 Android App 的開源工具，且不限於 WebView 殼：可在手機內執行 Node.js、PHP、Python、Go，甚至整個 WordPress；可在手機端完成打包、簽名，輸出 APK 與可上架 Google Play 的 AAB，全程不需電腦。
- **Why**：傳統流程要 Android Studio、JDK、簽名金鑰與電腦；WebToApp 把這些收斂到手機單機操作，降低接案「官網轉 App」的門檻。
- **How**：
  - 本地以 apksig 做 V1/V2/V3 簽名，keystore 自動管理。
  - 內建 AI Agent，以自然語言對話生成 App（支援 LLM Key 輪換）。
  - 提供多種 App 建立模板、整合 AdMob 與 IAP 變現。
- **When & Where**：店家官網、菜單、預約頁等輕量資訊型 App；以手機為主要操作環境。
- **Key Metrics**：Stars 約 6,850、Unlicense、輸出 APK + AAB。

> [!NOTE]
> 以上功能描述來自貼文與 README，本筆記尚未實機驗證；「手機內跑 WordPress」「不需電腦上架」等宣稱需在任務 `T-20261023-03` 中實測。

---

## 2. 官方 GitHub 與技術規格細節

- 倉庫：`https://github.com/shiaho777/web-to-app`（授權 Unlicense）。
- 打包輸出：APK、AAB；本地 apksig V1/V2/V3 簽名。
- 執行環境：Node.js / PHP / Python / Go / WordPress（App 內嵌）。
- AI Agent：自然語言生成 App；LLM Key 可輪換。
- 截圖可見的附加功能（2026-11-16 補）：啟動碼（本地或線上驗證）、裝置偽裝、自訂 DNS、廣告攔截、開機自啟；Node.js、npm 等建置工具鏈要在手機上另外安裝，不是開箱即有。
- 上架路徑的不確定性（2026-11-16 補）：repo 擁有者在 issue #1496 表示考慮移除 Google Play 相關功能以利 F-Droid 上架，AAB 上架流程可能改動，報價前要先確認當時版本還有沒有這個功能。
- 接案行情沒有實績（2026-11-18 補）：原貼文「一次收幾千到上萬、展示即成交」出自 AI 代管的粉專文案，留言區沒有人回報真的接到案，還有人問「和 PWA 有什麼差別」而無人回答；報價不可引用這些數字，接案前要先能回答 PWA 的問題。
- 已知未修問題（2026-11-16 補）：issue #1582 回報 CORS 繞過會把跨來源 POST 送出兩次，含表單送出或下單的網站要先測再交付。
- 風險面：內嵌多語言 runtime 增加 APK 體積與攻擊面；自動管理 keystore 需確認備份與保管方式；AI Agent 需自備 LLM Key，不得寫入程式碼或對話。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與 `android-cli` 技能互補：`android-cli` 面向開發機上的原生專案；WebToApp 面向「現有網頁快速封裝」，兩者場景不同，不互相取代。
  - 可把本機已有的靜態網頁小工具（例如 ai-inbox 衍生的儀表頁）封裝成 APK 做實測樣本。
- **落差與採納判斷**：
  - **值得採納**：先在 Windows 11 實測可行性與產物品質，再決定是否進入接案流程。
  - **需調整**：手機端流程不一定能在 Windows 自動化；Unlicense 不保證品質與安全，需審視簽名與權限。
  - **不採納**：不在未實測前承諾客戶「手機內跑 WordPress」等進階能力；也不把「可直接上架 Google Play」寫成固定承諾（見第 2 節上架路徑的不確定性）。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261023-03`**｜**[優先級：中]** 取得 WebToApp 並實測：把一個本機靜態網頁打包成可安裝 APK，記錄限制
  - **完成日期**：2026-10-25
  - **目標範圍**：`docs/web-to-app-evaluation.md`（實測紀錄；不修改其他 repo）
  - **具體做法**：
    1. 確認 `shiaho777/web-to-app` 最新 release 與授權檔（Unlicense）。
    2. 於 Android 實機或模擬器安裝，將一個本機靜態頁打包成 APK 並安裝執行。
    3. 檢查簽名資訊（keystore 位置與備份方式）與 APK 權限清單。
  - **驗收標準（DoD）**：產出 `docs/web-to-app-evaluation.md`，內含安裝步驟、打包後 APK 的安裝截圖或 log、權限清單與已知限制；以 `Test-Path docs/web-to-app-evaluation.md` 驗證存在，且文件含「結論：可行／不可行」一行。
  - **實作紀錄 / 證據**：已於 Windows 11 本機環境利用既有 Android SDK（Emulator 32.1.15.0、API 34 google_apis x86_64 映像檔、Build-tools 36.0.0 aapt/apksigner、ADB 34.0.4）建立 AVD 完成完整實測：1. 下載官方 release `web-to-app-2.8.2.APK`（26.3 MB）並以 `aapt dump badging/permissions` 與 `apksigner verify` 取得真實權限與 v2 簽章；2. 啟動模擬器成功開機（`sys.boot_completed=1`），安裝 WebToApp 宿主（`com.webtoapp.ui.MainActivity`）；3. 撰寫本機深色風格測試頁 `index.html`，透過本機 HTTP server 搭配 `adb reverse tcp:8080 tcp:8080` 供 WebToApp 進行分析與建立應用；4. 於手機端成功調用 `ApkBuilder` 從 `assets/template/webview_shell.apk` 模板完成二進位補丁與簽名，於設備私有目錄生成 `webtoapp_keystore.p12`（RSA-2048、V1+V2+V3 簽章）並輸出子包 `WebToAppSample_v1.0.0.APK`（8.3 MB，包名 `com.w2a.rybz`）；5. 實機安裝該子 APK（`Performing Streamed Install -> Success`）並啟動 `com.webtoapp.ui.shell.ShellActivity`（PID 9093），Logcat 證實成功啟動系統 WebView 載入 `http://127.0.0.1:8080/index.html`；6. 完整記錄前端表單 URL 嚴格校驗（拒絕 `file://`）、軟體鍵盤遮蔽保存按鈕與 ADB 版本衝突等邊界限制，全數數據與真實終端輸出已完整寫入 `docs/web-to-app-evaluation.md`，獲致「結論：可行」。

- [x] **`T-20261023-04`**｜**[優先級：低]** 在 T-20261023-03 結論為「可行」的前提下，撰寫「網站轉 App 接案流程規格」
  - **完成日期**：2026-10-25
  - **目標範圍**：`docs/web-to-app-freelance-workflow.md`
  - **具體做法**：
    1. 列出接案步驟：需求確認、網站可用性檢查、打包、簽名、上架材料、交付與維護。
    2. 列出風險與免責：第三方內容授權、隱私政策、Google Play 政策、金鑰保管。
  - **驗收標準（DoD）**：產出 `docs/web-to-app-freelance-workflow.md`，含上述六個步驟與風險清單；若 T-20261023-03 結論為「不可行」，改標記本任務為不做並寫一句理由。
  - **實作紀錄 / 證據**：已於 `docs/web-to-app-freelance-workflow.md` 完整定義網站轉 App 接案之六大標準步驟（1. 需求確認與範疇界定、2. 網站可用性檢查、3. 封裝與打包作業、4. 金鑰簽名與安全管理、5. 上架材料準備與商店送審、6. 交付驗收與後續維護）及四大風險防範與免責條款清單（第三方內容授權、隱私政策合規、Google Play 政策審查與被拒風險、金鑰保管與終生更新維護責任），全篇規範嚴謹並採用統一維護者視角。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **Claude Code 插件與原生工具鏈生態**：
  - [Anthropic 官方 Claude Code 插件生態目錄](./2026-10-17-claude-plugins-official-directory.md) ｜ 關聯任務：`T-20261017-07`、`T-20261017-08`
  - [Google Android 官方 Agent Skills 解構](./2026-10-19-android-official-skills-google-coding-agent.md) ｜ 關聯任務：`T-20261019-05`、`T-20261019-06`
