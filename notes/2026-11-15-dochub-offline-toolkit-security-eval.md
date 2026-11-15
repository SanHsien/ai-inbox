---
id: "2026-11-15-dochub-offline-toolkit-security-eval"
title: "DocHUB（home-999.com/dochub）離線辦公工具包查證：非開源二進位實況與開源替代評估"
source_url: "https://www.home-999.com/dochub/"
source_platform: "Web / Social"
author: "匿名開發者 (home-999.com)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 3
cluster_role: "DocHUB閉源查證"
short_title: "DocHUB離線工具查證"
tags:
  - security-audit
  - freeware
  - pdf-tools
  - privacy
  - pii-redaction
  - open-source-alternatives
---

# DocHUB（home-999.com/dochub）離線辦公工具包查證：非開源二進位實況與開源替代評估

- **來源連結**：[DocHUB 官方下載頁](https://www.home-999.com/dochub/)（當前版本 `v1.21.2`，Windows 10/11 64-bit）
- **發布平台 / 作者**：`Web` / `home-999.com`（無公開開發者／組織身分或 GitHub 帳號）
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-15-danyuchn-pii-guard-claude-mod-eval.md`](./2026-11-15-danyuchn-pii-guard-claude-mod-eval.md)（MIT 開源台灣繁中個資遮蔽引擎）

> **實查澄清**：
> 社群貼文宣稱「開源／打包出來分享」，但實測讀取 `https://www.home-999.com/dochub/` 完整頁面後，**站上無任何 GitHub 連結、開源授權聲明或原始碼倉庫**，僅提供閉源編譯後的 `DocHUB-win-Setup.zip`（172 MB）與 `DocHUB-win-Portable.zip`（171 MB）兩個執行檔壓縮包（附 SHA-256 與安裝後自動更新機制）。

---

## 1. 核心內容摘要（5W1H 初篩）

- **What（功能清單）**：整合 Windows 離線辦公工具（免裝 .NET，支援繁中／簡中／英／日／韓五語系）：
  - **PDF 轉檔與編輯**：PDF 轉圖片／Office、OCR 轉可搜尋 PDF、合併／分割／旋轉、標註、電子圖章與騎縫章。
  - **個資遮蔽**：掃描台灣身分證／統編／信用卡檢查碼並遮蔽，將頁面轉為圖片輸出並附清單報告。
  - **圖片與截圖工具**：格式互轉、AI 去背、壓縮（移除 GPS EXIF）、全螢幕／區域截圖與 `Ctrl+Alt+S` 滾動長截圖。
- **Why（訴求痛點）**：避免線上 PDF 工具上傳機密文件外洩、替代付費訂閱軟體。

---

## 2. 供應鏈安全與開源替代評估

### 2.1 零信任安全評估（不建議於主力工作機執行）
1. **閉源黑箱風險（無法驗證「純離線」宣稱）**：因未公開原始碼與可重現建置（Reproducible Build），即使提供官網 SHA-256，也只能驗證「與官網檔案一致」，**無法證明程式內部沒有遙測、網路回傳或未預期檔案讀取**。
2. **高權限暴露面**：該執行檔同時具備全域鍵盤熱鍵監聽（`Ctrl+Alt+S` 截圖）、自動更新機制（`updates/`）以及接觸敏感辦公檔案與個資的場景；依零信任原則，不應直接於存有開發憑證、SSH 金鑰或客戶檔案的 Windows 主力機運行來源不明的閉源免費 `.exe`（若需測試僅限隔離 VM / Windows Sandbox 且斷網檢查）。

### 2.2 可審查的開源替代方案對照

| 需求項目 | 建議可驗證開源替代 | 授權 / 特性 |
| :--- | :--- | :--- |
| **台灣繁中個資遮蔽** | [`danyuchn/pii-guard`](https://github.com/danyuchn/pii-guard) | **MIT 開源**，支援台灣身分證／統編／CKIP NER 與可逆補標 |
| **PDF 合併／轉檔／OCR** | **Stirling-PDF** / **BentoPDF** | 開源（自架或純瀏覽器 WASM 離線） |
| **滾動長截圖與標註** | **ShareX** / **Flameshot** | 開源 Windows 截圖與自動化標準工具 |
| **檔案差異比對** | **WinMerge** / **Meld** / VS Code Diff | 開源本機比對 |

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**不建議導入，暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：經查該工具實為閉源二進位執行檔（非貼文所稱開源專案），具備自動更新與全域熱鍵等高權限特徵且所有子功能皆已有成熟、可審查原始碼的開源替代方案，不具導入價值。
