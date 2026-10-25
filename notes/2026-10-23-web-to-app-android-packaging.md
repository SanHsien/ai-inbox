---
id: 2026-10-23-web-to-app-android-packaging
title: "WebToApp 解構：手機端把網站打包成 Android App、內建 Node/PHP/Python 執行環境、AI Agent 生成與 AAB 簽名上架，及接案變現評估"
source_url: "https://github.com/shiaho777/web-to-app/blob/main/.github/docs/README_CN.md"
source_platform: "GitHub"
author: "shiaho777"
analyzed_at: 2026-10-23
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 3
cluster_role: "手機端開發工具"
short_title: "WebToApp 網站轉 Android App"
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
- 風險面：內嵌多語言 runtime 增加 APK 體積與攻擊面；自動管理 keystore 需確認備份與保管方式；AI Agent 需自備 LLM Key，不得寫入程式碼或對話。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與 `android-cli` 技能互補：`android-cli` 面向開發機上的原生專案；WebToApp 面向「現有網頁快速封裝」，兩者場景不同，不互相取代。
  - 可把本機已有的靜態網頁小工具（例如 ai-inbox 衍生的儀表頁）封裝成 APK 做實測樣本。
- **落差與採納判斷**：
  - **值得採納**：先在 Windows 11 實測可行性與產物品質，再決定是否進入接案流程。
  - **需調整**：手機端流程不一定能在 Windows 自動化；Unlicense 不保證品質與安全，需審視簽名與權限。
  - **不採納**：不在未實測前承諾客戶「手機內跑 WordPress」等進階能力。

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
  - **實作紀錄 / 證據**：已完成 `shiaho777/web-to-app` 最新版本（v2.8.2，Unlicense 授權）之源碼、AndroidManifest.xml 權限（宿主 vs 生成子包）、apksig/AabSigner 簽名架構（PKCS#12、RSA-3072、有效 30 年、私有目錄儲存與備份風險）與建置架構評估；並實測 Windows 11 本機 Android 工具鏈（ADB 存在於 C:\Android\adb.exe，SDK 完整但無現成 AVD/實機運行），產出完整技術評估報告 `docs/web-to-app-evaluation.md`，包含「結論：可行（需搭配 Android 實機或模擬器執行打包與驗證）」。**覆核註記（2026-10-25）**：DoD 要求的「打包後 APK 的安裝截圖或 log」並未取得——本機無 AVD 與實機，實際未打包、未安裝；本項實為「原始碼與權限評估完成、實測未做」，任務標題的「實測」部分尚未達成。

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
