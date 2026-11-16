---
id: 2026-11-04-nicholas-lin-gcp-vertex-ai-amos-llmjacking
title: "Nicholas Lin 醫師 GCP Vertex AI 盜用案深度鑑別診斷：假 Claude Code 釣魚、AMOS 竊密木馬、Cookie 劫持與 LLMJacking 雲端算力變現攻擊鏈"
source_url: "https://www.facebook.com/100044633940228/posts/29811157725155734/"
source_platform: "Facebook (Nicholas Lin)"
author: "Nicholas Lin (@nps798)"
analyzed_at: 2026-11-04
analyzed_by: "Antigravity"
status: done
cluster: "3"
cluster_role: "端點資安與雲端基建"
short_title: "假Claude Code釣魚與Vertex AI盜刷鑑別診斷"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "未登入只讀到 29 則留言（共 77 則）；貼文全文與 1 張圖已看完"
source_images: 1
source_replies: 29
tags:
  - llmjacking
  - gcp
  - vertex-ai
  - amos-stealer
  - cookie-theft
  - session-hijacking
  - cloud-security
  - claude-code-phishing
  - zero-trust
---

# Nicholas Lin 醫師 GCP Vertex AI 盜用案深度鑑別診斷：假 Claude Code 釣魚、AMOS 竊密木馬、Cookie 劫持與 LLMJacking 雲端算力變現攻擊鏈

- **來源連結**：[Facebook 貼文：Nicholas Lin](https://www.facebook.com/100044633940228/posts/29811157725155734/) ｜ [分享短網址](https://www.facebook.com/share/p/1A5PDvd5HD/)
- **核心作者**：Nicholas Lin（家醫科醫師、資工所碩士，使用 Google Cloud 超過 10 年）
- **發布時間**：2026-11-04 00:03 (UTC+8)（即 2026-11-03 16:03 UTC）
- **歸屬集群**：集群 3：Agent 原生工具鏈、環境感知與擴充生態（角色：`雲端憑證竊取與LLMJacking防禦`）
- **當前狀態**：`🟢 已完成 (Done)`
- **官方資安威脅報告參照**：
  - [Google Cloud Threat Intelligence: LLMJacking - Monetizing Compromised Cloud Models](https://cloud.google.com/blog/topics/threat-intelligence/llmjacking-monetizing-compromised-cloud-models)
  - [Huntress Threat Report: AMOS Stealer Targeting macOS Developers via AI Lures](https://www.huntress.com/blog/amos-stealer-chatgpt-grok-ai-trust)
- **相關交叉參照**：
  - [`notes/2026-11-02-microphone-anti-overengineering-eight-agent-rules.md`](./2026-11-02-microphone-anti-overengineering-eight-agent-rules.md)（麥克風 8 條規約：雙向門自主推進 vs 單向門高危資安審批）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（Claude Code 四角色派工與執行時期規範）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（四 Agent 平行派工與憑證隔離硬閘門）

---

## 0. 原始資料盤點

> 2026-11-16 重審：原永久連結未登入顯示「目前無法查看此內容」，改由分享短網址開啟，讀到貼文全文、1 張圖與部分留言。

- **作者圖片**：共 1 張。圖 1 是黑白標題卡，寫「Google Cloud 被盜用，一個小時帳單將近 3 萬台幣」，背景浮水印字樣 Painful Lessons；沒有帳單截圖、Log 截圖或木馬檔案截圖，所以攻擊細節全部只有作者文字自述。
- **作者留言補充**（作者回覆 11 則）：
  - 目前用 Malwarebytes 免費版，掃得到那隻惡意程式；網友指出免費版沒有即時防護，作者回「再研究」。
  - 對「改用短效憑證」的建議表示認同，但還沒實作。
  - 希望 Google 對近期同類事件有處理措施。
- **網友留言重點**（頁面標示 77 則；未登入只載入 10 則主留言與 19 則回覆，共讀 29 則，其餘需登入）：
  - `李啟瑞`：把自己的電腦當公用電腦看待，與其靠防毒與手動輪替金鑰，不如改用短效憑證，登入至少要 2FA 或可同步的 Passkey。
  - `劉虔瑋`：自家也被盜刷 1.8 萬美元，Google 要求付款並由代理商催收，要 Log 也拿不到。
  - `曾耀賢`：8 月遇到服務帳戶憑證疑遭濫用，未授權 Vertex AI 費用近二萬（未寫幣別），專案內另有 8 台未授權虛擬主機；Google 多次延長審查、尚無結果。
  - `Kung KaiLin`：曾被刷約新台幣 800 元，找客服後全額退款；之後改成「取用金鑰要先在手機刷臉」的自製流程。
  - `林強生`：GCP 登入改硬體金鑰或 Passkey 可擋掉部分路徑；Hard cap「能設的先設」。
  - `Alexander Chen`：建議定期讓 Agent 掃 LaunchDaemons 類目錄。
  - 其餘為慰問、玩笑與不相關的新聞連結。
- **對分析的影響**：
  - 發布時間原寫「2026-11-03 16:03 (UTC+8)」，頁面顯示為 11 月 4 日上午 12:03，原值其實是 UTC；已更正。
  - 互動數原寫「2,300 次迴響、1,100 次轉發」，重審當下是 4,697 個心情、77 則留言、2,068 次分享；已更正。
  - 原寫「有人專案被未授權建立 8 台 GPU 虛擬機器」，留言原文只說「八台未授權建立的虛擬主機」，沒提 GPU；已刪掉 GPU。
  - 損失金額依圖 1 與內文改為「將近新台幣 3 萬元」，並補上作者說 Google 當天傍晚受理申訴、最後減免大部分費用。
  - 「Cookie／Session 被偷」是作者用排除法得到的推論：`~/.agent` 腳本已不存在、無法分析，也沒有直接證據顯示 AMOS 送出了哪些資料。第 2 節攻擊鏈圖把這段畫成既定事實，已在圖下加註。
  - 作者提到 Google 近期推出 Hard cap，但只涵蓋部分服務；已補進 2.1。
  - 留言的短效憑證、Passkey／硬體金鑰建議，已補進第 4 節第 2 層。既有三個任務的範圍不受影響，不新增任務。

---

## 1. 來源摘要與事件全貌

2026 年 11 月 3 日，擁有資工所碩士背景與 10 年 GCP 開發經驗的家醫科醫師 Nicholas Lin 於 Facebook 發布長文，詳述其 Google Cloud 帳號遭受 **LLMJacking（雲端 AI 算力竊盜與轉售）** 攻擊的親身經歷。截至 2026-11-16 重審，該貼文有 4,697 個心情、77 則留言、2,068 次分享，留言區有多位工程師回報類似遭遇。

### 1.1 災情爆發概況
- **攻擊時間**：某日凌晨 4 點起，大量國外 IP（巴拿馬等跳板）於 1 小時內狂暴呼叫作者 GCP 專案的 **Vertex AI API**（主要為 Gemini Flash 與視訊生成模型）。
- **財務損失**：1 小時內產生將近新台幣 30,000 元帳單（事後 Google 當天傍晚受理申訴，經協商減免大部分費用）；若非作者清晨 6 點早起收到 Google「Early signal anomaly detection（異常暴增 1000%）」警告信並緊急**關閉 Billing Account、撤下專案與網站止血**，帳單恐於幾小時內達到數萬美元破產級別。
- **產業災情共振**：貼文下方多位工程師回報相同遭遇——有人被盜刷 18,000 美元（Google 甚至派遣代理商追討帳單），有人專案被未授權建立 8 台虛擬主機、Vertex AI 費用近二萬（留言未寫幣別），Google 多次延長審查仍無結果。

---

## 2. 深入鑑別診斷：攻擊鏈全貌與根因剖析

```text
+-----------------------------------------------------------------------------------------+
|                  Nicholas Lin GCP Vertex AI 盜用案端到端攻擊鏈 (Kill Chain)              |
+-----------------------------------------------------------------------------------------+
| [8 個月前] 感染源 (Initial Access)                                                     |
| Google 搜尋 "Claude Code 安裝" -> 搜尋首位遭惡意廣告 (Malvertising) 綁架               |
| 進入釣魚假網站 (claude-code-something.mssg.com) 下載惡意 pkg/dmg/sh                     |
|                                                                                         |
|                                         ▼                                               |
| [8 個月前] 本地持久化與竊密 (Persistence & Stealing)                                   |
| 植入 AMOS (Atomic macOS Stealer) 木馬:                                                  |
| - 持久化設定: /Library/LaunchDaemons/com.finder.helper.plist                            |
| - 惡意後門啟動腳本: /bin/bash ~/.agent                                                  |
| - 憑證暫存檔案: ~/.mainhelper, ~/.pass, ~/.id                                           |
| - 扒走瀏覽器 Session Cookie 與 Google OAuth Token (完全繞過 2FA，無新裝置登入告警)      |
|                                                                                         |
|                                         ▼                                               |
| [2 週前] 潛伏與後門埋設 (Privilege Escalation & Persistence in Cloud)                   |
| 駭客利用偷得之 Session 透過美國 IP 登入 GCP Console:                                    |
| 1. 列舉專案清單 (Search Projects)                                                       |
| 2. 在主要專案中 4 秒內開通 17 個 Vertex AI 相關 API                                      |
| 3. 自建非預設名稱之 Service Account                                                     |
| 4. 2 分鐘後建立並下載 Private Key (取得永久獨立 API 存取權限，脫離 Session 依賴)        |
|                                                                                         |
|                                         ▼                                               |
| [發動日] 雲端算力變現 (LLMJacking & Impact)                                             |
| 凌晨利用巴拿馬跳板 IP，持 Service Account Private Key 大量呼叫 Vertex AI (Gemini Flash)  |
| 進行黑產模型推理或轉售給下游黑產顧客 (每小時消耗數百至數千美元算力)                     |
+-----------------------------------------------------------------------------------------+
```

> 註（2026-11-16 重審）：圖中「感染源」與「扒走 Session Cookie／OAuth Token」兩段是作者的推論，不是鑑識結果。作者只記得當時進過釣魚網站、推測下載了 dmg 或 sh；後門腳本 `~/.agent` 已不存在，無法確認實際外傳了什麼。有紀錄可查的部分是：木馬檔案的建立時間、兩週前的 GCP Log（列舉專案、4 秒開 17 個 API、建 Service Account、下載金鑰）、Google Takeout 裡同一天的美國 IP 操作紀錄、發動日的 Vertex AI 呼叫。

### 2.1 為什麼傳統防護完全失效？
1. **沒有 API Key 洩漏**：作者電腦沒有存 `.env`，沒有 push 到 GitHub，也沒有安裝 `gcloud` CLI。傳統的 Git Secrets Scanner（如 TruffleHog、GitGuardian）在此情境完全靜默。
2. **2FA（雙身分驗證）形同虛設**：AMOS 木馬竊取的是**已認證的瀏覽器 Session Cookie 與 Token**。駭客直接將 Cookie 導入瀏覽器發送請求，在 Google 看來完全是本人在正常操作，完全不會觸發「新裝置登入」通知或 2FA 推播。
3. **GCP Budget Alert 只是「事後軟提醒」而非「即時硬熔斷」**：
   - 作者原本已設定 50 美元花費通知，但 GCP 傳統的 Budget Alert 是**非即時的批次通知**（常延遲 3～5 小時）。
   - 更致命的是：**Budget Alert 預設不會中斷服務**！攻擊者可以毫無阻礙地繼續狂刷 API，直到信用卡額度刷爆。
   - 作者補充：Google 近期才推出 Hard cap（達上限即停用服務），但只涵蓋部分服務，不是整個專案都能設；事發當時擋不住這次攻擊。

---

## 3. LLMJacking 新型態雲端威脅解構

依據 Google Cloud Threat Intelligence 官方報告，**LLMJacking** 是 2024～2026 年威脅暴增最快的雲端攻擊手手法：

| 攻擊維度 | 傳統虛擬貨幣挖礦（Cryptojacking） | 新型 LLM 算力竊取（LLMJacking） |
| :--- | :--- | :--- |
| **目標資源** | 雲端 CPU / GPU 實例算力 | Vertex AI, Bedrock, Azure OpenAI API |
| **變現路徑** | 挖門羅幣等加密貨幣（收益每小時幾美分） | 透過反向代理轉售便宜 LLM Token（收益暴利） |
| **偵測難度** | 高 CPU 使用率易被警報抓包 | 正常 HTTPS API 請求，偽裝成合法應用流量 |
| **財務破壞力** | 受限於 VM 配額（每小時數十美元） | 依賴模型調用量計費，1 小時可刷破數千美元 |
| **潛伏期** | 幾天內被監控驅逐 | 可埋設 Service Account 潛伏數週至數月 |

---

## 4. 對本系統與 AI Agent 開發者的硬閘門防禦映射

本案例對使用 Antigravity、Claude Code、Codex 的開發者帶來重大啟示，必須建立機械式防護：

```
+-----------------------------------------------------------------------------------------+
|                  AI Agent 開發者四層防禦縱深 (Defense in Depth)                         |
+-----------------------------------------------------------------------------------------+
| 1. 本地環境隔離 (Local Sandboxing)                                                     |
|    - 搜尋與安裝熱門 AI 工具時嚴格比對官方域名 (如 anthropic.com / google.com)           |
|    - 定期掃描 macOS / Windows 原生持久化目錄 (LaunchDaemons / Startup / Registry)       |
|                                                                                         |
| 2. 憑證與 Session 保護 (Credential & Session Armor)                                     |
|    - 瀏覽器開發環境與個人日常環境隔離 (專用 Profile，限制 Cookie 導出)                   |
|    - 嚴禁 Agent 具備讀取主機 Keychain / DPAPI / 瀏覽器資料庫之權限                      |
|    - 留言建議: 改用短效憑證, 登入用 Passkey 或硬體金鑰 (降低長效 Session 被盜的影響)    |
|                                                                                         |
| 3. 雲端 IAM 最小權限與審批 (Cloud IAM Zero Trust)                                       |
|    - Service Account 建立與 Key 生成列為「單向門 (One-Way Door)」一級高危操作            |
|    - 未使用之 Vertex AI / GPU API 預設處於 Disable 狀態                                 |
|                                                                                         |
| 4. 財務硬熔斷與即時異常阻斷 (Automated Hard Budget Cap)                                 |
|    - 部署 Pub/Sub + Cloud Function 自動禁用 Billing Account 之 Hard Cap 腳本            |
|    - 導入異常計費速率檢測 (Spike Detection) 即時熔斷                                    |
+-----------------------------------------------------------------------------------------+
```

---

## 5. 具體待辦任務與落地拆解（Action Items）

為將 Nicholas Lin 事件所揭露的 AMOS 釣魚木馬與 LLMJacking 攻擊防護落實為可實施的工程規範，規劃以下 3 項任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261104-01`**｜**[優先級：高]** 撰寫「AI 時代雲端算力竊盜防禦手冊：AMOS 釣魚木馬、Cookie 劫持與 LLMJacking 防範規格」收錄於 `docs/llmjacking-cloud-defense-spec.md`
  - **目標範圍**：`docs/llmjacking-cloud-defense-spec.md`（規範文檔；不修改業務程式）
  - **具體做法**：
    1. 完整記錄 Nicholas Lin 受害案例、攻擊鏈時序圖與 AMOS 木馬檔案特徵（`com.finder.helper.plist`、`~/.mainhelper`）。
    2. 對比 GCP/AWS/Azure 雲端 AI API 計費模式，詳解 Soft Budget Alert 之致命缺陷與 Hard Cap 自動停機架構。
    3. 制定 AI 開發工具下載白名單檢驗機制，防範搜尋引擎惡意廣告釣魚。
  - **驗收標準（DoD）**：產出 `docs/llmjacking-cloud-defense-spec.md`，具備完整繁體中文結構；以 `Test-Path docs/llmjacking-cloud-defense-spec.md` 驗證存在。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：重寫（2026-11-14）：GCP 預算通知改為延遲式自動停用並寫明仍可能超支（引用官方 Limitations）；個案分為來源自述／待驗推測／已確認威脅三層；補 AWS Budgets Actions 與 Azure Budget＋Action Group 對等比較，附官方連結。修正前被審查退回（Hard Cap 誇大、只寫 GCP）；最終 Opus 驗收通過。

- [x] **`T-20261104-02`**｜**[優先級：中]** 實作「本地持久化後門與未授權雲端 Service Account 異常稽核腳本」於 `tools/verify_cloud_persistence_audit.py` 與單元測試
  - **目標範圍**：`tools/verify_cloud_persistence_audit.py`、`tests/test_verify_cloud_persistence_audit.py`
  - **具體做法**：
    1. 實作純 Python 稽核工具 `tools/verify_cloud_persistence_audit.py`，支援掃描本地持久化後門路徑（macOS LaunchDaemons/Agents、Windows Run Keys/Startup）與疑似 AMOS 檔案標記。
    2. 提供 GCP/雲端 Service Account 清單格式解析器，依據「非預設命名規則」、「短期內激增生成」與「下載 Private Key」規則標注高危可疑帳號。
    3. 撰寫單元測試套件 `tests/test_verify_cloud_persistence_audit.py`，覆蓋木馬持久化特徵偵測、合法 Service Account 豁免與高危後門攔截。
  - **驗收標準（DoD）**：執行 python -m unittest tests/test_verify_cloud_persistence_audit.py 綠燈通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正（2026-11-14）：高權限角色明列 owner/editor/admin 類；不存在路徑與只跳過時回 2；Windows Run Keys 唯讀掃描（非 Windows 明示跳過）；Service Account 依 createTime 滑動時間窗偵測大量建立。審查反例由 exit 0 變 1／2，mutation 皆被測試抓到。限制：tokenCreator、secretAccessor、自訂角色不在本任務規格內，仍放行。 **搬移註記（2026-11-14）**：工具與測試已移至 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks)（保留 git 歷史）。

- [x] **`T-20261104-03`**｜**[優先級：低]** 產出標準化「雲端 AI API 預算硬熔斷與防釣魚安裝審查 Prompt 模板」收錄於 `templates/llmjacking-defense-checklist-prompt.md`
  - **目標範圍**：`templates/llmjacking-defense-checklist-prompt.md`
  - **具體做法**：
    1. 產出適用於 Agent 或工程師的開工檢查 Prompt 模板，在安裝任何 CLI/Agent 前自動要求比對官方開源倉庫。
    2. 制定「雲端 IAM 敏感操作確認協議」：凡是創立 Service Account、啟用收費 AI API、導出憑證均觸發單向門審批。
    3. 附帶 GCP/AWS 預算硬熔斷 Terraform / Cloud Functions 快速部署清單。
  - **驗收標準（DoD）**：產出 `templates/llmjacking-defense-checklist-prompt.md`；以 `Test-Path templates/llmjacking-defense-checklist-prompt.md` 驗證存在。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：重寫（2026-11-14）：熔斷函式改為解碼 Pub/Sub、cost >= budget 才處置、先查 billingEnabled 達成冪等、預設只模擬須顯式啟用；Terraform 改用 projects/{project_number} 與 Billing Catalog service ID；補 AWS 清單與延遲／復原限制。tests/test_llmjacking_budget_killswitch.py 14 項離線測試（cost=0、1、49 不解綁、50 解綁），9 個 mutation 全被抓到。
