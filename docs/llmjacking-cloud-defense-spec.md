# AI 時代雲端算力竊盜防禦手冊：AMOS 釣魚木馬、Cookie 劫持與 LLMJacking 防範規格

本規格手冊基於 2026 年 11 月 Nicholas Lin 醫師遭受之 Google Cloud Vertex AI 算力竊盜案，深入解構新興之 **LLMJacking（雲端 AI 算力竊盜與轉售）** 攻擊鏈，並針對 AI 開發者與工程團隊制定防範「偽裝假 AI 工具釣魚」、「竊密木馬（Stealer）」、「瀏覽器 Session 劫持」與「雲端計費失控」的四層防禦縱深。

---

## 1. 核心威脅定義：什麼是 LLMJacking？

**LLMJacking** 是攻擊者在竊取開發者或企業之雲端憑證（如 IAM 憑證、Service Account Key、或已認證之 Session Cookie）後，**專門針對雲端託管之大型語言模型（LLM）API**（如 Google Cloud Vertex AI、AWS Bedrock、Azure OpenAI）發動未授權的大量推理呼叫，並將這些高價算力轉售予第三方或用於黑產活動（如大規模釣魚生成、自動化漏洞挖掘、CAPTCHA 破解）之攻擊行為。

### 1.1 與傳統 Cryptojacking（挖礦攻擊）之本質差異

| 比較維度 | 傳統虛擬貨幣挖礦（Cryptojacking） | 新型 LLM 算力竊取（LLMJacking） |
| :--- | :--- | :--- |
| **掠奪資產** | 實例之 CPU / GPU 算力 | 託管模型 API 調用配額（Tokens & Requests） |
| **特徵可見度** | 伺服器 CPU 使用率飆高至 100%，系統卡頓 | 僅為外部 HTTPS API 請求，伺服器本身無異常 |
| **變現價值** | 每小時僅幾美分至數美元（受限幣價） | 每百萬 Tokens 具備高額黑市轉售利潤 |
| **帳單破壞力** | 受限於 VM 租用費（通常有固定月費上限） | 依據 Token 與模型調用量無上限計費，數小時破萬美元 |
| **告警延遲** | 基礎架構監控可快速察覺 CPU 異常 | 雲端計費報表具備數小時延遲，察覺時已成定局 |

---

## 2. Nicholas Lin 案端到端攻擊鏈復盤

```
[1. 搜尋引誘] 搜尋 "Claude Code 安裝" -> 進入 Google Ads 偽造之釣魚假官網
       │
       ▼
[2. 惡意下載] 下載並執行夾帶 AMOS (Atomic macOS Stealer) 之 pkg / dmg / sh
       │
       ▼
[3. 本地持久化] 建立 /Library/LaunchDaemons/com.finder.helper.plist 自動拉起後門
       │
       ▼
[4. 憑證與Cookie扒竊] 竊取本機瀏覽器已登入之 Google Session Cookie (完美繞過 2FA)
       │
       ▼
[5. 雲端後門埋設] 登入 GCP Console，4 秒開通 17 個 AI API，自建 Service Account 並下載 Key
       │
       ▼
[6. 深夜發動 LLMJacking] 利用巴拿馬跳板 IP，大量狂刷 Gemini Flash，一小時刷破數萬台幣
```

---

## 3. 防禦手冊：四層縱深硬閘門防線

### 3.1 第一道防線：開發工具安裝白名單與官方網域驗證
- **防範惡意廣告（Malvertising）**：
  - 嚴禁透過搜尋引擎廣告贊助連結（Sponsored Ads）直接下載任何開發軟體。
  - 所有 AI Agent 與 CLI 必須由官方頂層網域（如 `anthropic.com`、`github.com`、`google.com`）或受信任之套件管理員（`npm`, `pip`, `cargo`, `brew`, `winget`）進行安裝。
  - 對於 `curl | sh` 安裝方式，必須先檢視腳本內容，嚴禁盲目執行未知網域之腳本。

### 3.2 第二道防線：本地持久化後門定期稽核
- 定期掃描作業系統原生自啟動設定：
  - **macOS**：`/Library/LaunchDaemons/`、`~/Library/LaunchAgents/`、`~/.mainhelper`、`~/.agent`。
  - **Windows**：`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`、工作排程器（Task Scheduler）、Startup 目錄。
- 凡發現未簽署、偽裝成系統核心元件（如 `com.finder.helper.plist`）之常駐行程，立即拔網線並終止。

### 3.3 第三道防線：雲端 IAM「單向門」審批矩陣
依據本系統之單向門（One-Way Door）規範，以下雲端動作嚴禁自動化或無感放行：
1. **建立新的 Service Account**：必須經過雙人或人類二次審核。
2. **為 Service Account 建立並下載 Private Key（JSON）**：高危動作，非必要應改用 Workload Identity Federation 或 Cloud Run 原生服務帳號，消滅本地長期金鑰。
3. **開通全新高單價 AI API**：未使用的 Vertex AI、Bedrock API 預設處於 Disable 狀態。

### 3.4 第四道防線：GCP / AWS 預算硬熔斷（Hard Budget Cap）
- **破除 Soft Alert 迷思**：
  - 傳統的「預算通知（Budget Alert）」只會寄發 Email，且延遲數小時，**完全無法阻止 API 繼續扣款**。
- **建構自動化斷開機制（Hard Cap Architecture）**：
  - 設定 GCP Cloud Billing 預算警報綁定 **Pub/Sub 主題**。
  - 當花費達到 100% 門檻時，觸發 Cloud Function 執行 `projects.billingInfo.update(billingAccountName="")`，**自動將專案從計費帳戶中解綁**。
  - 雖然解綁會導致專案內服務暫時中斷，但能徹底阻斷六位數美金破產級帳單。
