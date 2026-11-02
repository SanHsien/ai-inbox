# GitHub Apps Server-to-Server 與 Copilot SDK 工作負載身分整合指南

> 對應範本：[`templates/github-app-s2s-agent-workflow.md`](../templates/github-app-s2s-agent-workflow.md)（可直接複製的交換腳本與夜間 Agent 工作流）。
> 查證日：2026-11-02。GitHub 把「用 GitHub App 安裝權杖呼叫 Copilot」標為 **public preview**，行為可能變動；本文每個外部事實的來源在第 8 節，查不到官方來源的句子都標「未驗證」。
> 讀完能做的事：決定自己的場景該走 `GITHUB_TOKEN` 還是 GitHub App、依最小權限建立 App、把私鑰換成 1 小時權杖並交給 Copilot SDK、替夜間無人值守的 Agent 設好審核與回滾防線。

---

## 0. 先讀：本 repo 筆記的說法與官方文件不一致的地方

來源筆記（[`notes/2026-10-31-github-apps-server-to-server-copilot-agent-workload-identity.md`](../notes/2026-10-31-github-apps-server-to-server-copilot-agent-workload-identity.md)）是社群貼文的整理，只當線索。逐項對照官方文件後，下列幾點要照官方的寫，照筆記做會失敗或做錯：

| 筆記的說法 | 官方文件（2026-11-02 開啟比對） | 本指南怎麼寫 |
| :--- | :--- | :--- |
| SDK 設 `useLoggedInUser: false`，再用環境變數 `COPILOT_GITHUB_TOKEN` 注入 token | `useLoggedInUser: false` 會**關掉**自動憑證探測，包含 `COPILOT_GITHUB_TOKEN` 這類環境變數；權杖必須用 SDK 的明確選項傳入（TypeScript `gitHubToken`、Python `github_token`）。`COPILOT_GITHUB_TOKEN` 只用在「連到既有 runtime URI」時，設在那個 runtime 行程上。官方疑難排解表也列了這個症狀（`Not authenticated`） | 第 4 節：用明確選項傳入 |
| 權限叫 `copilot_requests` | 設定頁的名稱是組織權限 **Copilot Requests**（Read-only）；用 REST 領權杖時，請求本文的權限鍵是 `organization_copilot_requests` | 第 2、3 節用官方鍵名 |
| 「GitHub Actions 內建 `GITHUB_TOKEN` 支援 `copilot-requests: write`」放在 App 對照表裡，暗示是同一條路 | 這是**另一條路**：在組織擁有的 repo 的 workflow 裡，`permissions:` 加 `copilot-requests: write`，用內建 `GITHUB_TOKEN`，不需要 App、不需要存任何認證 secret，但組織必須開啟「Allow use of Copilot CLI billed to the organization」政策。GitHub App 這條路**不需要**開那個政策 | 第 5 節決策表 |
| App 用量有「獨立預算」「集中配額控管」 | 官方：**不能**為單一 App 或單一安裝建立預算；用量計入組織的 Copilot 預算，且預算只設警示不會擋用量，要擋必須開 **Stop usage when budget limit is reached** | 第 6 節 |
| 稽核可看 `app_client_id` | 只出現在 **AI usage 報表的 CSV 匯出**，不在 GitHub 上的「AI usage」畫面；使用者、GitHub Actions、其他 GitHub 自有 App 與舊資料的該欄位是空的 | 第 6 節 |
| PAT 長效「30~90 天，甚至無期限」 | 這組數字查不到官方來源 | **不採用**，不寫進本指南 |
| 權杖長得像 `ghs_xxx`（40 字元的印象） | 2026-04-27 起 GitHub 分階段把新的 installation token 改成較長的無狀態格式（`ghs_APPID_JWT`）；官方提醒不要假設長度為 40 字元 | 程式只檢查 `ghs_` 前綴 |
| 未提的限制 | 只支援**組織**安裝的 App（個人帳號與 enterprise 安裝不行）；組織要有 Copilot Business 或 Enterprise；「Read-only」不代表不花錢，它授權 App 消耗組織的 AI credits | 第 2、6 節 |

筆記裡引用的 Threads 貼文與留言（@alicken、@ginsengtrycatch 等人的說法）**本次未開啟驗證**，本指南不引用其中的任何斷言；GitHub 官方 Changelog 與文件才是依據。

---

## 1. 認證全貌

```text
 一次性設定（人做）                         每次執行（程式做，全程不碰任何人的帳號）
 ┌──────────────────────────┐              ┌────────────────────────────────────────────────┐
 │ 組織擁有者建立 GitHub App │              │ 1. 用私鑰簽 JWT（RS256，iss=client ID，        │
 │  - 組織權限 Copilot       │              │    exp 距現在 ≤ 10 分鐘）                       │
 │    Requests: Read-only    │              │ 2. POST /app/installations/{id}/access_tokens   │
 │  - repo 權限只開需要的    │ 私鑰(.pem)   │    body 可帶 permissions / repositories 縮小範圍│
 │ 安裝到「組織」            │ ───────────► │ 3. 取回 ghs_ 權杖，1 小時後過期                  │
 └──────────────────────────┘ 存成 secret   └───────────────┬────────────────────────────────┘
                                                            │
                          ┌─────────────────────────────────┴───────────────┐
                          ▼                                                 ▼
          Copilot 用權杖（只含 Copilot Requests）                 repo 用權杖（contents/PR/issues write）
          傳給 SDK 的 gitHubToken / github_token                  推分支、開 Draft PR
          用量記在「安裝所屬組織」，套用組織的模型政策與預算       介面上顯示為 App 的名稱，不是某位工程師
```

重點：**兩種權杖用途不同，權限也分開領**。一顆權杖要同時能花 Copilot 額度又能寫 repo，外洩時的損失就是兩者相加；分開領，Agent 本體（會吃不受信任的 issue 內容）只拿得到 Copilot 那顆。

---

## 2. 建立 Organization GitHub App 與最小權限

### 2.1 建立步驟（官方 Registering a GitHub App 頁，2026-11-02 核對）

1. 組織頁面 → **Settings** → 左側 **Developer settings** → **GitHub Apps** → **New GitHub App**。（Copilot 計費歸屬於安裝所在的組織，所以 App 最終要安裝在組織上，見第 7 步。）
2. 名稱不得超過 34 個字元；官方步驟要求填 Homepage URL，沒有專屬網站時可填公開 repo 的網址。
3. **Webhook**：Agent 只用排程或手動觸發、不需要接事件時，取消勾選 **Active**。官方文件明說「只用於認證、不需回應 webhook」時可以取消。
4. **Where can this GitHub App be installed?** 選 **Only on this account**，不要公開。
5. 權限：官方的原則是「GitHub App 預設沒有任何權限，只選需要的最小集合」。見 2.2。
6. **Create GitHub App**，再到 App 的 **Edit** → **Credentials** → **Key pairs** → **New key** 產生私鑰；下載到的 `.pem` 要自己保管，GitHub 只保存公鑰。
7. 在組織的 **Install App** 把它裝到組織，**Repository access 選 Only select repositories**，只勾要讓 Agent 動的 repo。

### 2.2 權限配置（本 repo 的最小集合）

| 權限 | 等級 | 層級 | 為什麼 |
| :--- | :--- | :--- | :--- |
| Copilot Requests | Read-only | 組織 | 讓安裝權杖能呼叫 Copilot。官方定義的 App 認證必要權限。注意它仍會消耗組織的 AI credits |
| Contents | Read and write | repository | 推 `ai-agent/...` 分支。官方 `actions/create-github-app-token` 對此權限的描述是「repository contents, commits, branches, downloads, releases, and merges」 |
| Pull requests | Read and write | repository | 開 Draft PR（官方 Create a pull request 端點要求 Pull requests: write） |
| Issues | Read and write | repository | 在 issue 留言回報 PR 連結（同一份 action 描述涵蓋 issues 及其留言、標籤） |

不要勾的（本 repo 的取捨，不是 GitHub 的規定；範本腳本的拒絕清單也內建這些）：`Administration`、`Members`、`Secrets`、組織層級的 `Administration`／`Secrets`、`Workflows`。`Workflows: write` 會讓 Agent 能改 `.github/workflows/`，等於讓它能改自己的關卡；爆破半徑關卡也預設拒絕 `.github/` 路徑。

**用領權杖時再縮一次**：App 註冊時的權限是上限。官方說明領權杖時可用 `permissions` 與 `repositories` 本文縮小範圍，沒指定就繼承 App 在該安裝上的全部權限，且不能要求超過 App 已有的權限，`repositories` 最多列 500 個。所以：Copilot 用的權杖請求只帶 `{"organization_copilot_requests":"read"}`。

---

## 3. 私鑰換 1 小時權杖（金鑰輪替流程）

### 3.1 JWT 規格（官方 Generating a JSON Web Token 頁）

| 欄位 | 值 | 官方要求 |
| :--- | :--- | :--- |
| 演算法 | `RS256` | 必須 |
| `iat` | 現在往前 60 秒 | 建議，防時鐘誤差 |
| `exp` | 距現在不超過 10 分鐘 | 上限 10 分鐘 |
| `iss` | App 的 client ID | 官方建議用 client ID（App ID 也接受）；兩者是不同的值 |

### 3.2 換權杖

```bash
curl --request POST \
  --url "https://api.github.com/app/installations/INSTALLATION_ID/access_tokens" \
  --header "Accept: application/vnd.github+json" \
  --header "Authorization: Bearer JWT" \
  --header "X-GitHub-Api-Version: 2026-03-10"
```

（上面是官方頁面的範例；版本標頭 `2026-03-10` 為該頁當日所列。）回應含權杖、過期時間、實際權限與 repo；**權杖 1 小時後過期**。安裝 ID 可從 webhook payload 取得，或用 `GET /orgs/{org}/installation`、`GET /app/installations` 等端點查（官方列出的查法）。

範本腳本 `app_installation_token.py` 把這一段包好：私鑰從環境變數讀、不寫檔、不印；`--permissions` 縮權限；`--dry-run` 只簽 JWT 不連網；`--github-output` 會先輸出 `::add-mask::` 再寫入 `$GITHUB_OUTPUT`。

### 3.3 速率限制（官方 Rate limits 頁）

安裝權杖的 REST 基本額度是每小時 5,000 次；在 GitHub Enterprise Cloud 組織上是 15,000 次。不在 GHEC 的安裝，超過 20 個 repo 時每個 repo 加 50 次、組織超過 20 位使用者時每位加 50 次，上限 12,500 次。夜間批次若會大量輪詢 issue，要自己控管節流；另外還有 secondary rate limit。

### 3.4 私鑰輪替（官方 Managing private keys 頁）

- 一個 App 最多 25 把私鑰；私鑰**不會自動過期**，要手動撤銷。官方建議用多把金鑰以便不停機輪替。
- 輪替順序：新增一把 → 更新所有存放私鑰的 secret → 確認新金鑰運作 → 刪掉舊金鑰。已遺失或外洩的金鑰直接刪除；但最後一把要先產生新的才能刪。
- 私鑰**只放秘密管理（Actions secret 等），不放 repo、不貼對話、不印進 log**。下載的 `.pem` 存進 secret 後刪除本機檔案。

---

## 4. Copilot SDK 無人值守呼叫

官方 Server-to-server authentication 頁（2026-11-02）給的 TypeScript 與 Python 寫法如下；token 從環境變數 `INSTALLATION_TOKEN` 取（變數名是官方範例自取的，不是 SDK 規定）：

```typescript
import { CopilotClient, RuntimeConnection } from "@github/copilot-sdk";

const token = process.env.INSTALLATION_TOKEN;
if (!token) throw new Error("INSTALLATION_TOKEN is required");

const client = new CopilotClient({
  connection: RuntimeConnection.forStdio(),
  gitHubToken: token,
  useLoggedInUser: false,
});
```

```python
import os
from copilot import CopilotClient, RuntimeConnection

client = CopilotClient(
    connection=RuntimeConnection.for_stdio(),
    github_token=os.environ["INSTALLATION_TOKEN"],
    use_logged_in_user=False,
)
```

要點：

- `gitHubToken`／`github_token` 才是傳權杖的地方；`useLoggedInUser: false` 讓 SDK 關閉自動憑證探測，不退回已儲存的使用者憑證（官方範例的說明是「disable fallback to stored user credentials」）。
- 官方也列了 Go、Rust、.NET、Java 的寫法，本文不重述。
- **權杖 1 小時過期，要在過期前重領**。官方的做法是重啟 SDK client（子行程模式）或重啟 host runtime；單次作業超過 1 小時的 Agent，請把作業切成每次不到一小時，或在每段開頭重領。
- 套件：npm 上確認有 `@github/copilot-sdk`（2026-11-02 查 registry，latest 1.0.28），PyPI 上有 `github-copilot-sdk`（1.0.28，專案網址指向 `github/copilot-sdk`）。
- 官方疑難排解：`401` → 權杖過期或無效，重領；`403` 且訊息說明 App 安裝權杖的 Copilot 請求未啟用 → 組織尚未支援／啟用此認證；一般 `403` → 確認安裝有組織 `Copilot Requests` 權限後重領；`Requested model is unavailable` → 組織的 Copilot 政策沒開該模型；「帳單記錯人」→ 確認安裝屬於預期的組織。
- **未驗證**：SDK 建立 session、送出 prompt 與讀串流結果的 API，本次沒有逐一核對，請照 SDK 官方 README 寫；筆記裡的「Node.js / Python 呼叫介面」只有「建立 client 並傳入權杖」這一段有官方依據。

---

## 5. 場景決策：GITHUB_TOKEN 還是 GitHub App

| 場景 | 建議 | 理由（官方文件） |
| :--- | :--- | :--- |
| 組織擁有的 repo、在 Actions 裡跑、只要呼叫 Copilot | `GITHUB_TOKEN` + `permissions: copilot-requests: write` | 不用 App、不存認證 secret；需開 Copilot CLI billed to the organization 政策；用量走 GitHub Actions 專屬的政策與預算 |
| Actions 裡要**跨 repo**或存取組織資源 | GitHub App | 官方：`GITHUB_TOKEN` 只能存取工作流所在的 repo |
| Actions 裡要開 PR 且**希望 PR 自動跑 CI** | GitHub App 權杖 | 官方：由 `GITHUB_TOKEN` 觸發的事件不會建立新的 workflow run（`workflow_dispatch`、`repository_dispatch` 例外） |
| Actions 以外的服務（自架主機、雲端排程、容器） | GitHub App | 這是官方文件列為「其他服務與 CI 系統」的路線 |
| 個人帳號或 enterprise 層級安裝 | 本方式不可用 | 官方：只支援安裝在組織的 App |

夜間 Agent 同時需要「開 PR 觸發 CI」與「Copilot」，所以範本用 App：Copilot 權杖與 repo 權杖分開領。

---

## 6. 治理：計費、稽核與熔斷（官方 Manage GitHub Apps that use your organization's Copilot）

- **用量歸屬**：記在安裝所屬的組織，套用組織的模型政策與預算；做不到「為單一 App 設預算」。要真的擋住花費，組織預算必須開 **Stop usage when budget limit is reached**，只設警示不會停。
- **核准前審查**：確認 App 擁有者、用途與預期用量；逐項檢查要求的組織與 repo 權限，確認 Copilot Requests 是組織層級且為 Read-only。
- **找出 App 的用量**：下載 AI usage 報表（CSV），找 `organization` 欄是你的組織且 `app_client_id` 有值的列；再用「List app installations for an organization」REST 端點，把報表的 `app_client_id` 對上回應的 `client_id`，`app_slug` 就是 App 名稱。
- **熔斷**：對該安裝 **Suspend** 或 **Uninstall**，Copilot 請求立刻停止；官方註明這同時會擋掉該安裝對組織其他資源的存取。
- **本 repo 的建議**：每月看一次 CSV 的 `app_client_id` 用量，異常時先 Suspend 再查；私鑰疑似外洩時，先刪金鑰（見 3.4）再查。

---

## 7. 夜間無人值守 SDLC 的防線

```text
 排程／手動觸發
      │
      ▼
 領 Copilot 專用權杖（1h）──► Agent 在 Actions 一次性 runner 上改工作目錄（沒有 repo 寫入憑證）
      │
      ▼
 有變更？──否──► 結束（綠燈，無 PR）
      │是
      ▼
 品質關卡（測試／lint／型別）──紅燈──► 失敗終止，不推送
      │綠燈
      ▼
 爆破半徑關卡（檔數上限、禁止路徑、不可無變更）──違規──► 失敗終止
      │通過
      ▼
 才領 repo 權杖（contents/PR/issues write，只限這個 repo）
      │
      ▼
 推 ai-agent/issue-N-<run id> 分支 ─► 開 **Draft** PR，標籤 ai-agent-generated，issue 留言連結
      │
      ▼
 隔日由真人 review ─► merge 或關閉（絕不自動 merge）
```

四條防線與落地方式（以下是本 repo 的設計準則，不是 GitHub 官方規定；範本已把前三項做進工作流）：

1. **主分支保護不可繞過**：主分支啟用保護規則，要求 PR 與至少一位真人核准；**不要把這個 App 放進任何 bypass 名單**。工作流本身無法替你設定，這是 repo 設定。
2. **一律 Draft PR**：`gh pr create --draft`，標題加 `[AI-Agent-Generated]`、掛 `ai-agent-generated` 標籤，內文連到工作流 run。範本用 `Refs #N` 而不是 `Closes #N`，避免 merge 時自動關閉 issue 而跳過人的判斷。
3. **爆破半徑封鎖**：預設最多 10 個檔案，且拒絕碰 `.github/`、`Dockerfile`、`docker-compose*.yml`、`*.tf`、`*.tfvars`。這些門檻是本範本的取捨，請依專案調整；有測試覆蓋好、壞兩種輸入（見範本測試）。
4. **回滾**：Agent 的變更在一條分支、一次 commit 內，merge 後要撤回就對 merge commit 做 `git revert`；若 PR 尚未 merge，直接關閉 PR 並刪分支即可。**範本沒有自動回滾機制**——「自動」回滾需要部署與監控資訊，超出本範本範圍。
5. **不受信任輸入**：issue 內容可能含提示注入。範本把它存成檔案、不內插進 shell 或 prompt 指令，Agent 那一步拿不到 repo 寫入權杖，最壞情況是產生一個會被關卡擋下或被真人拒絕的 Draft PR。這降低風險但不能消除：Agent 仍可能把惡意內容寫進程式碼，所以第 1、2 項的真人 review 不可省。

---

## 8. 來源（皆於 2026-11-02 實際開啟並比對內容）

官方：

- [GitHub Copilot supports server-to-server authentication — GitHub Changelog，2026-10-27](https://github.blog/changelog/2026-10-27-github-copilot-supports-server-to-server-authentication/)（public preview、Copilot Requests 唯讀組織權限、用量計入安裝所屬組織、`app_client_id`、Suspend／Uninstall）
- [Server-to-server authentication（Copilot SDK）](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens)（`gitHubToken`、`useLoggedInUser: false`、`organization_copilot_requests`、Actions 用 `copilot-requests: write`、疑難排解表）
- [Manage GitHub Apps that use your organization's Copilot](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-app-copilot-access)（僅組織安裝、不可設單一 App 預算、CSV 才有 `app_client_id`）
- [Generating a JSON Web Token (JWT) for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app)
- [Generating an installation access token for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app)（1 小時、`permissions`／`repositories` 縮權、新 token 格式提醒）
- [Making authenticated API requests with a GitHub App in a GitHub Actions workflow](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow)
- [Managing private keys for GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps)（最多 25 把、不自動過期、輪替）
- [Registering a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app)、[Choosing permissions for a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
- [Rate limits for GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/setting-up-a-github-app/rate-limits-for-github-apps) 與 [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)（5,000／15,000／12,500 的數字取自後者）
- [REST API endpoints for pull requests](https://docs.github.com/en/rest/pulls/pulls)（Create a pull request 需要 Pull requests: write）
- [Triggering a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow)（`GITHUB_TOKEN` 事件不觸發新 run）
- [Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)（中間環境變數、釘 SHA）
- npm registry `@github/copilot-sdk`、PyPI `github-copilot-sdk`（確認套件存在與版本號）

**未驗證／刻意不採用**：Threads 貼文與留言內容；筆記中 PAT 的 30~90 天效期數字；SDK 建立 session 與送 prompt 的 API；`bypass_pull_request_allowances` 這個權限名稱（筆記提到，本次未查官方，本指南改以「不要把 App 放進 bypass 名單」描述）。

*連結中的「Copilot SDK」頁面網址在官方 Changelog 中是 `docs.github.com/copilot/how-tos/copilot-sdk/auth/server-to-server-tokens`，開啟後會導向 `/en/` 版本。*
