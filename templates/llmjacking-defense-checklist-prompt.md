# 雲端 AI API 預算硬熔斷與防釣魚安裝審查 Prompt 模板

本模板旨在幫助 AI Agent、開發者與 DevOps 工程師在日常開發、工具安裝與雲端架構配置中，機械化落實 Nicholas Lin 事件之資安防禦，徹底杜絕 **釣魚下載惡意木馬**、**瀏覽器 Session 洩漏** 與 **雲端 Vertex AI / Bedrock 算力竊盜（LLMJacking）**。

---

## 1. AI 開發工具安裝前置檢查 Prompt（Anti-Phishing Checklist）

```markdown
### 外部軟體與 AI Agent 工具安裝防禦協議
在安裝或執行任何第三方 AI 工具、Agent CLI、擴充套件或腳本前，必須先完成以下自檢：
1. **來源網域檢驗**：
   - 是否來自官方頂層網域（如 `anthropic.com`, `openai.com`, `github.com`）？
   - 嚴禁點擊搜尋引擎「贊助廣告（Sponsored）」或類似 `something.mssg.com`、`claude-code-download.net` 的仿冒釣魚網址。
2. **安裝指令檢驗**：
   - 優先使用官方套件管理器（`npm install -g @anthropic-ai/claude-code`, `pip install ...`, `brew install ...`）。
   - 若遇到 `curl -fsSL https://... | sh`，必須先將腳本下載至本地閱讀原始碼，確認無可疑 `LaunchDaemons` 或二進位下載行徑。
3. **無憑證洩露原則**：
   - 工具執行時若要求輸入主機密碼（`sudo`）、要求授權存取 Keychain / 瀏覽器 Cookie，一律立即終止並通報。
```

---

## 2. 雲端 IAM 單向門（One-Way Door）高危審批 Prompt

```markdown
### 雲端資源與 Service Account 操作硬閘門
任何涉及雲端身分與存取管理（IAM）的操作均屬於「單向門不可逆決策」，嚴格禁止 AI Agent 自行放行：
1. **嚴禁自動建立 Service Account**：凡要求在 GCP/AWS 建立新服務帳號，必須暫停並向人類說明業務必要性。
2. **嚴禁下載 Private Key（JSON）**：強烈禁止建立長期私鑰檔案（.json / .pem）。建議引導人類改採 Workload Identity Federation 或 Cloud Functions 綁定身分。
3. **嚴禁批量啟用 AI API**：未使用的模型 API（Vertex AI、Claude on Bedrock）維持預設 Disable，防止帳號遭入侵後成為黑產提款機。
```

---

## 3. GCP Cloud Billing 預算硬熔斷架構（Hard Budget Cap Terraform 快速參考）

```hcl
# GCP 預算警報綁定 Pub/Sub 主題，達到 100% 預算時觸發 Cloud Function 解綁計費帳戶
resource "google_billing_budget" "emergency_hard_cap" {
  billing_account = var.billing_account_id
  display_name    = "Vertex AI Emergency Hard Cap ($50 USD)"

  budget_filter {
    projects = ["projects/${var.project_id}"]
    services = ["services/aiplatform.googleapis.com"] # 針對 Vertex AI 限制
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "50"
    }
  }

  threshold_rules {
    threshold_percent = 1.0 # 達到 100% 觸發
    spend_basis       = "CURRENT_SPEND"
  }

  all_updates_rule {
    pubsub_topic = google_pubsub_topic.billing_hard_cap_topic.id
  }
}
```

Cloud Function 執行之關鍵程式碼：
```python
from googleapiclient import discovery

def stop_billing(data, context):
    project_id = "YOUR_PROJECT_ID"
    service = discovery.build('cloudbilling', 'v1')
    # 將專案之計費帳戶清空，立即強制中斷所有收費 API
    service.projects().updateBillingInfo(
        name=f"projects/{project_id}",
        body={"billingAccountName": ""}
    ).execute()
    print(f"Emergency Hard Cap Triggered: Project {project_id} detached from billing.")
```
