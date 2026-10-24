---
id: 2026-10-23-zeabur-october-2026-security-incident
title: "Zeabur 2026 年十月資安事件解構：內部明文憑證外洩、共享叢集與 GCP 專用伺服器淪陷、平台資料庫環境變數被讀取，及對自身雲端憑證衛生的應變清單"
source_url: "https://www.threads.com/share/_qH3yIe8s/"
source_platform: "Threads"
author: "Zeabur (@zeabur.app)"
analyzed_at: 2026-10-23
analyzed_by: "Antigravity"
status: pending # pending | in-progress | done | archived
cluster: 3
cluster_role: "資安防護"
short_title: "Zeabur 十月資安事件與憑證輪替"
tags:
  - zeabur
  - security-incident
  - credential-rotation
  - secrets-management
  - paas
  - incident-response
---

# Zeabur 2026 年十月資安事件解構：內部明文憑證外洩、共享叢集與 GCP 專用伺服器淪陷、平台資料庫環境變數被讀取，及對自身雲端憑證衛生的應變清單

- **來源連結**：[Threads @zeabur.app 貼文](https://www.threads.com/share/_qH3yIe8s/)
- **完整初步調查報告**：[Zeabur 2026 年十月資安事件（初步報告）](https://zeabur.com/zh-TW/blogs/october-2026-security-incident)（2026-10-19 發布，時間皆為 UTC，調查仍在進行，內容可能更新）
- **發布平台 / 作者**：`Threads` / `Zeabur`（報告作者 Yuanlin Lin）
- **分析日期**：`2026-10-23`
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-23-claude-plugin-security-guidance.md`](./2026-10-23-claude-plugin-security-guidance.md)（Agent 寫碼時攔截硬編碼憑證）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：PaaS 平台 Zeabur（官方報告）。這是其不到兩個月內的第二起資安事件（前一起為 2026 年 8 月）。
- **What**：2026-10-14 至 15 日，攻擊者以外洩的內部憑證入侵共享叢集、GCP 專用伺服器與內部網路，最終讀取平台資料庫。
- **Why / 根因（官方自述）**：長期有效的管理憑證以明文保存且可從公網使用，並非單一漏洞。
- **How（攻擊鏈）**：

```text
路徑 A：共享叢集 + AWS                      路徑 B：GCP 專用伺服器
  明文 AWS 金鑰 + 無期限叢集管理權杖           舊 GCP 金鑰（可讀初始化設定）
        │（管理介面對公網開放）                      │（設定中明文 root 密碼）
        ▼                                           ▼
  9 區共享叢集：所有服務環境變數            101 台伺服器 root 登入
  865 個資料庫容器內執行讀取指令                     │
        │（過大權限金鑰讀舊叢集備份）                │
        ▼                                           │
  機密管理服務：約 53 筆正式環境機密 ──內網憑證──▶ 加入內部網路節點
                                                     ▼
                                          讀取平台資料庫（唯讀帳號）
```

- **Key Metrics（官方已確認數字）**：
  - 環境變數 3,218,965 筆被讀取；帳號 321,810 筆；zSend API 金鑰 566 把（明文，已撤銷）；平台存取權杖 11,536 筆（僅雜湊，已全數撤銷）。
  - GCP 專用伺服器 101 台、92 位使用者確認被 root 登入；其中 50 台被加入攻擊者 SSH 金鑰。
  - 攻擊者最後已知活動 10 月 15 日 21:05；從首次憑證使用到啟動調查約 36 小時未觸發告警。
- **When**：攻擊 2026-10-14 01:36 起；使用者回報後 10-15 13:56 啟動調查；報告 10-19 發布。
- **攻擊者意圖（官方觀察）**：搜尋可直接使用的 API 金鑰，特別是 AI 服務金鑰（n8n、new-api／one-api 憑證），並嘗試呼叫 Amazon Bedrock（失敗）。

> [!WARNING]
> 報告區分「已確認／研判／無法確認／推測」。初始憑證如何取得**無法確認**；「與八月事件 GitHub App 私鑰有關」僅是推測，不可當事實引用。

---

## 2. 官方報告技術細節（可轉用為檢查項）

- **影響範圍**：共享叢集服務與 GCP 專用伺服器為主；Hetzner（359 台）、DigitalOcean（48 台）專用伺服器的管理權杖外洩，無法確認是否被使用。八月後已把環境變數遷移到自有專用伺服器的專案，不在平台資料庫被讀取範圍內。
- **使用者必做**（官方）：
  1. 更換存放在 Zeabur 的所有環境變數憑證（API Key、雲端金鑰、資料庫密碼、簽章與加密金鑰），先在供應商撤銷舊的再建新的並重新部署；八月後換過的也要再換。
  2. 重新登入並重建 Access Token；zSend 使用者重建 API 金鑰。
  3. GitHub 使用者檢查 10-15 15:05–18:54 來自 Zeabur GitHub App 的操作（非預期 clone/推送、新增 deploy key、被改的 webhook）。
  4. 核對帳單（自 10-14 起；GCP 專用伺服器回溯到 9-01）。
  5. 共享叢集：資料庫內也要換密碼；n8n 換加密金鑰並重建第三方憑證；new-api 撤銷上游 AI 金鑰。
  6. GCP 專用伺服器：視為已遭入侵，備份後重建；至少移除 `/root/.ssh/authorized_keys` 中註解為 `@zeabur-pentest` 的金鑰、換 root 密碼並關閉密碼登入。
- **入侵指標**：官方列有攻擊者 IP、SSH 金鑰指紋與 AWS 用戶端 User-Agent（見報告「入侵指標」章節，本筆記不複製完整清單，以官方更新為準）。
- **重要營運事實**：Zeabur 已宣布將於 **2026-12-31 停止營運**（官方稱為營運決策）。若有服務在其上，遷移已是硬期限。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與全域規範「API key、token、私鑰不進程式碼、不進指令列、不進對話」直接呼應；本事件是「明文長效憑證」風險的真實案例。
  - 本機尚未確認是否使用 Zeabur；需先盤點，不可假設有或沒有。
- **落差與採納判斷**：
  - **值得採納**：(a) 盤點是否曾在 Zeabur 部署並輪替；(b) 把本事件教訓寫成可重用的平台入侵應變範本（輪替範圍、備份與金鑰隔離、遷移出平台）。
  - **需注意**：「換密碼」不等於已止血，資料庫內密碼、n8n 加密金鑰等二次憑證都要處理。
  - **不採納**：不需要追查攻擊者歸因或複製 IOC 清單，那是平台方的工作。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261023-05`**｜**[優先級：高]** 盤點本人是否使用 Zeabur，並對曾存放其上的憑證做輪替確認
  - **目標範圍**：`docs/zeabur-incident-credential-audit.md`（僅記錄遮蔽後資訊，嚴禁貼入任何仍有效的金鑰）
  - **具體做法**：
    1. 檢查 Zeabur 帳號登入信箱是否有官方事件通知信，並登入控制台確認是否有專案、服務或專用伺服器。
    2. 若有：列出其環境變數中的憑證種類（只記種類與供應商，不記值），在各供應商撤銷舊的並重建，重新部署。
    3. 檢查 GitHub 稽核紀錄 10-15 15:05–18:54 來自 Zeabur GitHub App 的操作，並核對自 10-14 起的雲端與 AI 供應商帳單。
    4. 評估 2026-12-31 停運前的遷移時程。
  - **驗收標準（DoD）**：產出 `docs/zeabur-incident-credential-audit.md`，第一行明寫「結論：有使用／無使用 Zeabur」；若有使用，列出每項憑證「供應商、已撤銷日期、已重建日期」表格（不含值）與 GitHub 稽核與帳單檢查結果；以 `Select-String -Path docs/zeabur-incident-credential-audit.md -Pattern '結論'` 驗證，並以 secret 掃描確認文件不含金鑰。若結論為「無使用」，本任務可直接標示完成並附登入控制台的確認時間。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261023-06`**｜**[優先級：中]** 建立「託管平台入侵事件應變清單」範本，供日後任一 PaaS 事件重用
  - **目標範圍**：`templates/platform-breach-response.md`
  - **具體做法**：
    1. 依本事件整理通用步驟：先撤銷再重建、輪替範圍（含資料庫內密碼、加密金鑰、Access Token）、檢查第三方稽核紀錄與帳單、評估是否遷出平台。
    2. 加入「預防面」檢查項：憑證不明文落地、長效權杖設期限、備份與金鑰分離。
  - **驗收標準（DoD）**：產出 `templates/platform-breach-response.md`，含「立即處置／二次憑證／稽核與帳單／遷移評估／預防」五個段落且每段至少 3 項可勾選項目；以 `Select-String -Pattern '^## '` 確認五個段落標題存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **資安防護**：
  - [Anthropic 官方 security-guidance 外掛解構](./2026-10-23-claude-plugin-security-guidance.md) ｜ 關聯任務：`T-20261023-01`、`T-20261023-02`
