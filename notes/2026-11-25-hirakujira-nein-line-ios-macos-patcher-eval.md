---
id: "2026-11-25-hirakujira-nein-line-ios-macos-patcher-eval"
title: "GitHub 專案評析：`Black-Magic-Lab/NEIN`（原 `hirakujira/NEIN`）——LINE iOS/macOS 副裝置雙開與去廣告二進位修補工具"
source_url: "https://github.com/hirakujira/NEIN"
source_platform: "GitHub (Black-Magic-Lab/NEIN)"
author: "Black-Magic-Lab (hirakujira)"
analyzed_at: "2026-11-25"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-25"
source_review_note: "已透過 gh api 唯讀檢閱 Black-Magic-Lab/NEIN（原 hirakujira/NEIN）之 repo metadata、完整檔案樹、README.md 與 README-macOS.md；未執行任何建置或修補腳本。"
status: archived
cluster: 4
cluster_role: "LINE逆向修補評析"
short_title: "NEIN LINE去廣告雙開評析"
tags:
  - ios
  - macos
  - line
  - reverse-engineering
  - macho
  - objc-hooks
---

# GitHub 專案評析：`Black-Magic-Lab/NEIN`（原 `hirakujira/NEIN`）——LINE iOS/macOS 副裝置雙開與去廣告二進位修補工具

- **來源倉庫**：[`github.com/hirakujira/NEIN`](https://github.com/hirakujira/NEIN)（重導向至 `Black-Magic-Lab/NEIN`，`176` stars，最近更新 `2026-11-23`，`license: null`）
- **分析日期**：`2026-11-25`
- **當前狀態**：`⚪ 歸檔參考 (Archived — 不另開工單)`
- **相關交叉參照**：
  - [`notes/2026-10-19-rea-reverse-engineer-anything-agent.md`](./2026-10-19-rea-reverse-engineer-anything-agent.md)（逆向工程工具鏈與 cleanroom 規範）
  - [`notes/2026-11-06-fengxue-ida-pro-ai-mcp-reverse-engineering-concern.md`](./2026-11-06-fengxue-ida-pro-ai-mcp-reverse-engineering-concern.md)（商業二進位逆向與合規邊界討論）

---

## 0. 原始資料盤點（`gh api` 唯讀檢閱）

- **專案定位**：針對 Apple 生態（iOS 18+ 與 macOS）LINE 客戶端的研究型二進位修補與 Objective-C / Mach-O Runtime Hook 工具，主打 iPhone 以副裝置（偽裝 iPad）登入雙開、移除廣告與精簡版面。
- **iOS 版機制（`README.md`、`tools/main.py`、`patch_profiles/`、`hooks/`）**：
  - 僅接受已核對的解密 LINE IPA（`26.14.0`、`26.15.1`、`26.17.0`），其餘版本直接拒絕處理；需自行以 AltStore / Sideloadly 重簽安裝（Bundle ID `kinta.ma.nein`），可與原版 LINE 並存。
  - 只在登入入口修改裝置判斷為 iPad（不全域偽裝），並透過 `NEINKeychainHooks.m` / `NEINAppGroups.h`（`--keychain-compat`）處理重簽後的 Keychain 與 App Group 相容問題。
  - 選項包含 `--remove-ads`（網域封鎖見 `ad_domains.txt`）、`--collapse-friends-on-launch`、`--skin-theme`、iPhone Duo 直向版面與預設啟用貼圖／主題小舖（無法在 NEIN 內儲值）。
  - 明確限制：不支援推播通知、不含分享／Widget／Siri／Watch 擴充功能、不接管 LINE 連結，且官方免責聲明提示修改 IPA 可能影響帳號／資料並違反服務條款。
- **macOS 版機制（`README-macOS.md`、`tools/mac_main.py`、`hooks/NEINMacHooks.mm`）**：
  - 針對 macOS LINE `26.5.0`（build 3975）與 `26.4.2`（build 3955），因 macOS 版採 Qt/QML 無法共用 iOS hook，改採「雙層 App（外層 `NEIN.app` 啟動器＋內層保留 `jp.naver.line.mac` Bundle ID）」且固定每版本 runtime 路徑以減少 macOS 權限重複彈窗，原 `/Applications/LINE.app` 不受改動。
  - 穩定版僅攔截已核對的 `WKWebView` 廣告 URL，刻意關閉容易造成登入視窗消失、圖片卡住、已讀異常或高 CPU 的 Qt/QML 可見性實驗 hook（`--disable-qt-ad-hiding`）。
  - 隨包輸出 `.manifest.json`（記錄雜湊、簽名、啟用功能與 `shops_skipped`），並提供 `check_mac_ad_activity.py` 統計系統日誌次數——明定無法證明廣告已顯示時狀態標示為「未知」，不得誤判為通過實測。

---

## 1. 評估結論與不另開工單理由

- **工程設計亮點（僅作跨領域參考）**：
  1. **版本白名單＋可稽核 Manifest**：透過 `patch_profiles/*.json` 嚴格拒收未核對版本，並於產物旁寫出 `.manifest.json` 記錄跳過項與雜湊。
  2. **誠實未知狀態（Honest Unknowns）**：`check_mac_ad_activity.py` 明確區分「日誌未出現事件」與「廣告未出現」，不以缺席推論通過，符合本庫 `verification-protocol` 的零假陽性紀律。
- **不另開工單理由**：
  - 目標平台為 iOS 18+ 與 macOS LINE 二進位客戶端，與本機 **Windows 11 原生 + AI Agent 開發工作流**無交集。
  - 專案未宣告開源授權（`license: null`），且修改專有通訊軟體二進位檔存在帳號風控與 ToS 合規風險，不納入本庫工具鏈或實作計畫，故採純歸檔參考。
