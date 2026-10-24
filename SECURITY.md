# 安全政策 (Security Policy)

## 資料邊界與隱私防線

本倉庫 (`SanHsien/ai-inbox`) 為公開的 AI 情報分析與任務看板。所有 Agent 與協作者禁止提交：

1. **憑證與機密**：API Key、Personal Access Token (PAT)、SSH 私鑰、Cookie、Session Identifier、完整 Auth 檔。
2. **私有專案敏感細節**：私有 Repo 內部網址、內部商業邏輯代碼、未公開之產品計畫。
3. **未去敏資料**：包含使用者真實姓名、電子郵件、電話、未經公開授權之私人對話記錄或付費內容完整原文。

## 任務驗收之去敏標準

當任務實作完成並回寫至 `README.md`（🟢 已做）或 `notes/` 時：
- 若目標為公開專案：可標記公開的 PR / Commit 連結。
- 若目標為私有專案：一律使用 `[Private Repo: <別名>] 通過驗證` 抽象化處理，嚴禁洩露內部儲存庫名稱或未公開代碼。

## 安全漏洞回報

若在此倉庫中發現任何安全疏漏或意外提交的敏感資訊：
- 請使用 GitHub 的 [Private Vulnerability Reporting](https://github.com/SanHsien/ai-inbox/security/advisories/new) 向 `SanHsien/ai-inbox` 回報。
- 若無法使用該功能，請建立不含利用細節的最小 Issue 進行通知，維護者將立即處理。
