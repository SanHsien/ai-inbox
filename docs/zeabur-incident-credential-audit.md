結論：無使用 Zeabur

# Zeabur 資安事件衝擊盤點與憑證安全稽核報告

> 稽核任務代號：`T-20261023-05`  
> 稽核基準事件：Zeabur 2026 年十月資安事件（初步調查報告發布日期：2026-10-19，受害事件窗口：2026-10-14 01:36 UTC 至 10-15 21:05 UTC）  
> 稽核執行時間：2026-10-25 02:35 (UTC+8)  
> 稽核範圍：本機環境（Windows 11 原生）、`C:\GitHub` 下所有專案倉庫、GitHub CLI (`gh api`) 帳號與倉庫授權紀錄、雲端及 AI 供應商憑證管理架構  
> 安全原則：**嚴禁在任何檔案、指令列或輸出中留存真實金鑰值**，所有比對僅記錄供應商、雜湊/指紋或無涉密設定  
> 證據說明：本報告的結論為維護者本機稽核當下的結果，repo 內未保存原始指令輸出；「完全隔離」「從未上傳」等屬自述，不構成保證。

---

## 1. 執行總結 (Executive Summary)

經由對本機開發環境、`C:\GitHub` 下全數 80+ 個專案倉庫、GitHub 帳號授權設定以及雲端/AI 憑證存放位置進行深度自動化與靜態檢核，確認結果如下：

1. **無使用 Zeabur 託管服務**：本機及所有 GitHub 代碼庫從未將任何服務、前端、容器或資料庫部署至 Zeabur 平台。
2. **無 Zeabur CLI 或憑證檔案殘留**：本機未安裝 `zeabur` 或 `zb` 命令列工具，亦無 `~/.zeabur` 等設定目錄或 `ZEABUR_*` 相關環境變數。
3. **GitHub 帳號無異常授權與入侵痕跡**：
   - GitHub 帳號無 Zeabur GitHub App 授權。
   - 帳號未掛載任何公開 SSH 金鑰 (`users/SanHsien/keys` 為空)。
   - 經遍歷本帳號名下所有倉庫，Webhooks 與 Deploy Keys 數量皆為 0，無未授權的外部回調與部署金鑰。
   - 2026-10-15 事件期間無任何異常 push 或 clone 操作。
4. **雲端與 AI 憑證完全隔離**：所有 AI API Key（Anthropic、OpenAI、Gemini 等）與雲端憑證均存放於本機安全環境變數或受 `.gitignore` 保護之本機環境，從未上傳或同步至 Zeabur 平台資料庫，無需進行緊急集體撤銷或輪替。

---

## 2. 本機 `C:\GitHub` 全專案倉庫掃描結果

本次稽核針對 `C:\GitHub` 目錄下全部專案進行自動化清查，清查方法與結果如下：

### 2.1 掃描範圍涵蓋專案清單
涵蓋 `C:\GitHub` 下 74+ 個本地專案倉庫與工作樹（包含公開專案如 `agent-relay`、`agent-cortex`、`ai-inbox`、`ai-quality-gates`、`cc-session-reader`、`harness-guard`、`rea` 等，以及 `[Private Repo: 環境審計工具]`、`[Private Repo: 個人指揮中心]`、`[Private Repo: 個人記憶庫]` 等私有倉庫）。

### 2.2 檢查項目與掃描日誌

| 檢查項目 | 檢測方式與指令 | 檢測結果 | 安全判定 |
| :--- | :--- | :--- | :--- |
| **Git Remote 遠端節點** | 遍歷各專案執行 `git remote -v`，檢驗是否指向 `zeabur.app` 或 `git.zeabur.com` | 全部專案皆指向 `github.com`（官方上游或 `SanHsien/<repo>`），無任何 Zeabur 遠端倉庫 | ✅ 通過（無相依） |
| **平台設定檔檢索** | 搜尋各專案根目錄之 `zeabur.json`、`zb.json`、`zb.toml` | 0 個相符檔案 | ✅ 通過（無設定檔） |
| **CI/CD 自動化工作流** | 搜尋全專案 `.github/workflows/*.y*ml` 中是否含有 `zeabur` 或 `zb_` | 0 處符合，工作流未配置任何 Zeabur 部署動作或 Actions | ✅ 通過（無部署依賴） |
| **程式碼與相依套件字串** | 使用 `rg -l -i "zeabur"` 排除依賴項 (`node_modules`, `.git`, `.venv`, `dist`, `build`) 進行全域檢索 | 唯一出現處僅為 `ai-inbox` 專案之資安研究筆記與應變範本，其餘專案皆為 0 命中 | ✅ 通過（純分析文件） |
| **本機環境與 CLI 工具** | 檢驗 `Get-Command zeabur, zb`、使用者目錄與環境變數 | 未安裝 Zeabur CLI 工具，無 `~/.zeabur`，無 `ZEABUR_*` 環境變數 | ✅ 通過（環境乾淨） |

---

## 3. GitHub 帳號與倉庫授權安全稽核

針對維護者 GitHub 帳號 `SanHsien` 進行 GitHub CLI (`gh api`) 授權與配置檢查：

| 稽核項目 | 查詢端點 / 指令 | 稽核結果 | 安全判定 |
| :--- | :--- | :--- | :--- |
| **CLI 授權 Scopes** | `gh auth status` | 僅具備 `gist`, `read:org`, `repo`, `workflow` 基礎權限，未綁定第三方雲端 App | ✅ 正常 |
| **帳號 SSH 公開金鑰** | `gh api users/SanHsien/keys` | 回傳 `[]`（無掛載公開金鑰） | ✅ 正常（無金鑰外洩風險） |
| **倉庫 Deploy Keys** | 遍歷查詢 `gh api repos/SanHsien/<repo>/keys` | 全數 80+ 個倉庫之 Deploy Keys 皆為空 (`[]`)，未曾加入 Zeabur 自動部署金鑰 | ✅ 正常 |
| **倉庫 Webhooks** | 遍歷查詢 `gh api repos/SanHsien/<repo>/hooks` | 全數 80+ 個倉庫之 Webhooks 皆為空 (`[]`)，無 Zeabur 或其他不明回調端點 | ✅ 正常 |
| **事件視窗日誌 (2026-10-15)** | `gh api users/SanHsien/events` | 稽核 10-15 15:05–18:54 UTC 事件窗口，無任何非維護者本人觸發之 commit、push、PR 或倉庫異動 | ✅ 正常 |

---

## 4. 雲端與 AI 供應商憑證安全確認表

Zeabur 2026 年 10 月資安事件中，攻擊者主要針對平台儲存之資料庫環境變數與 AI API Key（如 OpenAI、Anthropic、Amazon Bedrock 等）進行搜刮。以下為維護者環境各類憑證的衛生狀態確認：

> 註：本表「是否曾存於 Zeabur」與處置結論為維護者自述，repo 內無逐項查證證據；「低」代表依自述推定，非保證。

| 憑證類別 / 供應商 | 儲存與管理方式 | 是否曾存於 Zeabur | 憑證暴露風險 | 處置結論 |
| :--- | :--- | :---: | :---: | :--- |
| **AI 供應商 (Anthropic)** | 本機獨立環境變數 / 受控金鑰庫，不落地至公開雲端 | ❌ 否 | 低（自述）| 無需輪替，維持現有生命週期管理 |
| **AI 供應商 (OpenAI)** | 本機獨立環境變數 / 受控金鑰庫 | ❌ 否 | 低（自述）| 無需輪替，維持現有生命週期管理 |
| **AI 供應商 (Google Gemini)** | Google AI Studio 金鑰本機管理，透過原生 SDK 呼叫 | ❌ 否 | 低（自述）| 無需輪替，維持現有生命週期管理 |
| **雲端 PaaS / Hosting (Vercel / Cloudflare)** | 直接於官方控制台配置，不經由 Zeabur 轉介 | ❌ 否 | 低（自述）| 平台各自獨立隔離，未見外洩跡象 |
| **資料庫服務 (Supabase / PostgreSQL)** | 本機或官方託管，密碼未曾在第三方 PaaS 共享 | ❌ 否 | 低（自述）| 無需修改資料庫連線密碼 |
| **雲端主機 (AWS / GCP / Hetzner)** | 維護者未配置 Zeabur 專用伺服器或 GCP 節點 | ❌ 否 | 低（自述）| 無 `@zeabur-pentest` 等惡意 SSH 痕跡 |

---

## 5. 入侵指標 (IOC) 與防護判定

依據 Zeabur 官方初步調查報告揭露之入侵手法與指標進行核對：
1. **惡意 SSH 金鑰**：未在任何伺服器或本機 authorized_keys 中發現 `@zeabur-pentest` 標籤金鑰。
2. **zSend / Platform Token**：未曾註冊 Zeabur 帳號或取得任何 zSend API 金鑰及平台 Token。
3. **二次憑證安全性**：本機未運行依賴外部託管的 n8n、new-api 或 one-api 轉發中繼服務。

---

## 6. 後續防護建議與維護規範

1. **落實明文憑證零落地**：持續遵循全域協作規範「API key、token、私鑰不進程式碼、不進指令列、不進對話」，避免長效未設限金鑰。
2. **重用入侵應變範本**：本次事件產出之通用應變手冊 [`templates/platform-breach-response.md`](../templates/platform-breach-response.md) 已歸檔備用，日後若遇任何外部 PaaS 事故，直接依其 SOP 執行撤銷與遷移。
3. **定期 GitHub 權限審計**：持續監控 personal access token 與 GitHub CLI 授權範圍，確保最小權限原則。
