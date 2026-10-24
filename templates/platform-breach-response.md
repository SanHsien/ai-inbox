# 託管平台資安事件應變清單（Platform Breach Response Checklist）

> **適用情境**：當團隊或維護者使用的 PaaS／託管平台（如 Zeabur、Render、Railway、Vercel 等）發生控制面入侵、憑證外洩或疑似未授權存取時，請依序執行本檢核清單。
> **核心原則**：先撤銷（Revoke）舊憑證與外部連線授權，確認止血後再重建（Rotate）與重新部署；切勿在未撤銷前直接覆寫，以免舊權杖持續有效。

## 立即處置

- [ ] 維護者立即盤點該託管平台上所有運行的服務、專案與環境變數清單，標記高風險對外服務。
- [ ] 先撤銷平台綁定的外部 OAuth 授權（如 GitHub、GitLab、Cloudflare、Docker Registry），確認連線中斷後再評估重建。
- [ ] 輪換（先撤銷再重建）所有注入於平台環境變數中的雲端商 API 金鑰、AI 供應商金鑰（OpenAI、Anthropic、Gemini 等）與第三方服務權杖。
- [ ] 終止平台控制台的所有活躍登入工作階段（Active Sessions），重設平台帳號密碼並強制重新啟用多因素驗證（2FA / Passkey）。

## 二次憑證

- [ ] 輪換託管資料庫（PostgreSQL、MySQL、Redis、MongoDB 等）的管理者與應用程式連線密碼，並切斷既有長連線。
- [ ] 針對資料庫內部資料表儲存的外部服務憑證、OAuth Refresh Token 與 Webhook Secret 進行全面撤銷與更新。
- [ ] 輪換應用層加密金鑰（如 n8n 的 `N8N_ENCRYPTION_KEY`、框架 `APP_KEY` 或 `SECRET_KEY`），並以新金鑰重新加密儲存的敏感憑證。
- [ ] 作廢應用程式簽發給終端使用者或內部微服務的所有 Access Token、Session Signing Key 與 JWT 簽章密鑰，強制全體重新驗證。

## 稽核與帳單

- [ ] 稽核 GitHub／GitLab 帳號與組織的 Installed GitHub Apps、Authorized OAuth Apps、專案 Webhooks 與 Deploy Keys，移除不明或不再使用的授權。
- [ ] 檢查程式碼儲存庫近期是否有異常的 Commit、未知分支、可疑 GitHub Actions Workflow 變更或非預期的容器映像檔推送紀錄。
- [ ] 回溯檢查所有關聯雲端服務與 AI API 供應商的近期帳單、Token 消耗量與呼叫日誌，確認有無異常暴增或盜刷並立刻設定硬性消費上限（Hard Limit）。
- [ ] 保存託管平台的部署紀錄、存取日誌與異常時間軸截圖，供團隊事後根因分析與資安稽核存證。

## 遷移評估

- [ ] 評估受影響託管平台的官方資安事件公告、透明度、修補時程與根因報告（Post-mortem），判斷平台是否具備持續營運與安全防護能力。
- [ ] 驗證團隊現有資料庫備份、持久化儲存卷（Volumes）與服務設定檔（Docker Compose、IaC 宣告檔）的完整性與可攜性。
- [ ] 測試於備援環境（如自管 VPS、其他合規 PaaS 或雲端原生環境）進行最小可行恢復演練，確認遷移時間目標（RTO）符合業務需求。
- [ ] 若評估決定停運遷出，在確認備援環境穩定接手流量且資料同步完成後，徹底刪除原平台上的容器實例、儲存卷、專案設定與綁定資訊。

## 預防

- [ ] 落實憑證不明文落地原則，所有機密資訊統一由外部秘密管理工具（如 1Password、Bitwarden、雲端 Secret Manager）注入，嚴禁寫入儲存庫或硬編碼。
- [ ] 為所有 API 金鑰、Personal Access Token（PAT）與服務權杖強制設定最小權限範圍（Least Privilege）與明確到期日，全面淘汰永久有效權杖。
- [ ] 執行備份與金鑰分離架構，確保資料庫自動備份檔案與應用層解密金鑰分別存放於不同信任邊界的儲存空間。
- [ ] 建立團隊定期的第三方託管平台憑證盤點與季度輪換機制，並於雲端與 AI 帳單系統配置低門檻即時異常用量告警。
