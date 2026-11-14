# 雲端算力竊盜防禦：LLMJacking、AMOS 與延遲式自動停用

本文件區分威脅研究、個案來源與本地建議；查證日期為 2026-11-14。LLMJacking 指濫用遭竊雲端或模型憑證來使用、轉售模型資源，已有 [Google 威脅研究](https://cloud.google.com/blog/topics/threat-intelligence/llmjacking-monetizing-compromised-cloud-models) 記錄。這不代表下述個案的攻擊者、入侵方式或轉售行為已獲確認。

## 1. 個案與歸因的證據邊界

| 證據層級 | 可寫入的內容 | 來源與限制 |
| :--- | :--- | :--- |
| 來源自述（未查證原文） | 既有筆記將 Nicholas Lin 的遭遇描述為假 Claude Code 下載後發生 GCP 異常費用 | [原貼文](https://www.facebook.com/100044633940228/posts/29811157725155734/) 本次無法取得全文；[本庫轉述](../notes/2026-11-04-nicholas-lin-gcp-vertex-ai-amos-llmjacking.md) 不是獨立證據。姓名歸屬、日期、損失及細節皆未查證。 |
| 個案鑑別推測 | 木馬竊取 Cookie／憑證，再建立服務帳號維持存取，最後呼叫模型 API，是待驗假說 | 需個案端點鑑識、登入與 Cloud Audit Logs 支持；目前未取得。不能宣稱「完美繞過 2FA」、精確啟用時間／數量、來源 IP 國別或特定模型已確認。 |
| 已確認的一般威脅指標 | Huntress 調查另一宗 AMOS 入侵，列出 `/Library/LaunchDaemons/com.finder.helper.plist`、`.agent` 與 `.helper` | [Huntress 原始調查及 IOC 表](https://www.huntress.com/blog/amos-stealer-chatgpt-grok-ai-trust)；不能用另一案 IOC 證明本案感染 AMOS。`~/.mainhelper` 作為本案特徵仍未查證。 |
| 已確認的一般雲端濫用行為 | 竊取憑證、建立未授權身分與濫用模型資源有研究紀錄 | [Google 原始調查](https://cloud.google.com/blog/topics/threat-intelligence/llmjacking-monetizing-compromised-cloud-models)；不是 Nicholas Lin 案的鑑識報告。 |

以下是**待驗攻擊鏈**，不是已確認的個案時序：

```text
假下載來源 -> 執行惡意內容 -> 竊取憑證或工作階段
                               |
                               v
                  未授權雲端身分 -> 模型 API 濫用 -> 異常費用
```

## 2. 建議防線（本文件制定的政策）

以下是本地建議，不是已部署或能保證阻止入侵的機制。安裝來源政策回應 [Huntress 調查](https://www.huntress.com/blog/amos-stealer-chatgpt-grok-ai-trust) 的惡意指令誘導；身分與金鑰政策回應 [Google 調查](https://cloud.google.com/blog/topics/threat-intelligence/llmjacking-monetizing-compromised-cloud-models) 的憑證濫用。

1. **下載審查**：從產品官方文件逐層核對 repo owner、套件名稱及發行者；不能只因網址在 `github.com` 就信任任意 repo。不執行搜尋廣告或第三方文章夾帶的安裝指令；先閱讀下載腳本及其後續下載來源。
2. **端點稽核**：依已知 IOC 檢查 macOS LaunchDaemons、LaunchAgents；Windows 檢查 Run、Startup 與排程。命中名稱只當調查線索，先隔離與保存證據，勿單憑檔名判定感染或任意刪除。
3. **雲端 IAM 審批**：建立身分、匯出長期金鑰、擴大權限或開放模型存取前要求人類核准；優先採用短期工作負載身分。服務帳號金鑰管理可參照 [Google 官方最佳實務](https://docs.cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys)。
4. **預算回應與備援**：先隔離測試專案並演練，再接自動處置；以額外的用量監控與人工事件回應補足計費通知延遲。不可把預算當即時花費上限。

## 3. GCP／AWS／Azure 計費與對等處置比較

| 平台 | AI 計費範圍（不列固定價格） | 預算通知後可採取的機制 | 邊界與限制 |
| :--- | :--- | :--- | :--- |
| GCP Vertex AI | 模型與輸入／輸出等使用量依 [官方價目](https://cloud.google.com/vertex-ai/generative-ai/pricing)；不同模式／SKU 須逐項查價 | Budget -> Pub/Sub -> 函式比對成本 -> `projects.updateBillingInfo` 清空計費帳戶 | 屬於**延遲式自動停用**；[官方 Limitations](https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications#limitations) 明言仍可能超支。停用波及專案服務，可能造成資源刪除；重新啟用需手動配置，不能保證服務復原。 |
| AWS Bedrock | 隨選依模型用量計價，另有預佈建等模式，參照 [官方價目](https://aws.amazon.com/bedrock/pricing/) | [Budgets Actions](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-controls.html) 可自動或核准後套用 IAM／SCP，或處置指定 EC2／RDS；模型呼叫須另設拒絕策略 | [AWS 通知延遲說明](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) 指出收到通知前可能已超支。停 EC2 不等同封鎖 Bedrock；策略範圍外的資源與既有費用須另查。 |
| Azure OpenAI | 用量與部署計費模式應依 [官方成本規劃](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/manage-costs) 核對 | Cost Management Budget -> Action Group -> Logic App／Automation Runbook 等，[官方範例](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/cost-management-budget-scenario) 示範自動化資源處置 | [官方預算文件](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets) 明言預算本身不停用資源；資料通常延遲 8–24 小時、每 24 小時評估。Action Group 僅支援訂用帳戶與資源群組範圍；不是全訂用帳戶即時停費保證。 |

## 4. GCP 延遲式自動停用的操作邊界

依 [官方通知格式](https://docs.cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications)，Pub/Sub 通知包含週期性成本更新，零成本也可能發送；不能把「收到訊息」視為「達到門檻」。本庫採 `costAmount >= budgetAmount` 才允許處置，實作及離線測試見 [防禦模板](../templates/llmjacking-defense-checklist-prompt.md)。

```text
成本產生 -> 計費資料延遲 -> Pub/Sub -> 驗證來源與資料
                                         |
                         未達門檻 <-------+-------> 達到門檻
                            |                         |
                           返回              查詢狀態 -> 模擬或解綁
```

處置後先撤銷遭竊憑證、調查未授權身分，再人工評估復原。依 [Google 停用教學警告](https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications)，解綁可能導致無法復原的資源損失；本文件不保證費用上限、復原時間或資料完整性。此為設計建議，未執行真實部署或個案鑑識。
