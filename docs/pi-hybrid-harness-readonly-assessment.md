# Pi 混合型 Harness 唯讀評估

評估日期：2026-11-15。任務：T-20261115-01。作者：Codex。

**結論：目前不採納 Pi 作為第四層控制平面。** 可保留其會話樹與 TUI 客製化作設計參考，但目前沒有足以抵銷額外模型用量、憑證面與維護成本的使用者需求。此結論是靜態評估，沒有安裝、登入、OAuth、模型呼叫或動態相容性測試。

## 來源與查閱範圍

Pi 固定 commit：`c3cc91632d0a1950fb122605b190233f2aa0006e`；以下 P 連結皆指向此版本，不使用浮動 main 推定固定版本行為。

| 代號 | 實際查閱的一手來源 | 用途 |
|---|---|---|
| P1 | [根 package.json](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/package.json)、[package-lock.json](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/package-lock.json) | 工作區、生命週期、依賴快照 |
| P2 | [coding-agent/package.json](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/package.json)、[cli.ts](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/src/cli.ts)、[quickstart](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/docs/quickstart.md) | 發行入口及安裝方式 |
| P3 | [security.md](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/docs/security.md)、[windows.md](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/docs/windows.md) | 權限、信任與 Windows 前提 |
| P4 | [extensions.md](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/docs/extensions.md)、[loader.ts](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/src/core/extensions/loader.ts)、[package-manager.ts](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/src/core/package-manager.ts) | 模組載入與子程序安裝路徑 |
| P5 | [providers.md](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/coding-agent/docs/providers.md)、[openai-codex.ts](https://github.com/earendil-works/pi/blob/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/ai/src/providers/openai-codex.ts)、[provider 目錄](https://github.com/earendil-works/pi/tree/c3cc91632d0a1950fb122605b190233f2aa0006e/packages/ai/src/providers) | 技術接入，不能代替供應商授權 |

以 Git 淺層複製取得來源，只讀文字及 JSON；未執行來源中的任何程式。來源作者為 Earendil Works／Mario Zechner；套件宣告 MIT（P2）。未檢查每個間接依賴的完整程式碼、發行二進位或官方網站安裝器實體；不作完整供應鏈安全認證。

## 安裝期與執行期風險

| 階段 | 靜態證據 | 判斷與限制 |
|---|---|---|
| 安裝入口 | P2 的 bin 是 `dist/bundle/cli.js`；原始碼 `cli.ts` 呼叫 setup 與 main。Quickstart 分別列官方網站安裝器與 npm 路徑 | 文件中的遠端直管安裝命令未執行；網站安裝器內容未查證，不能用 repo HEAD 保證實際下載物 |
| npm 依賴 | P2 要求 Node.js >=22.19.0、直接依賴有固定版本；P1 根鎖檔 lockfileVersion=3，470 個 packages 記錄 | 根工作區鎖檔不代表使用者全域 npm 安裝會沿用完整鎖定；quickstart 也明說 npm 路徑不固定間接依賴 |
| 生命週期 | 根 package 有 `prepare: husky`；鎖檔八個記錄帶 hasInstallScript，包含 esbuild、canvas、ssh2、workerd | 這是整個工作區清冊，不等於八個都會進入 coding-agent 正式部署。未執行或逐支審計；quickstart 建議的 npm 路徑含 ignore-scripts，不代表所有 Pi package 安裝路徑都禁腳本 |
| 擴充安裝 | P4 package-manager 的 npm 安裝參數含 prefix、legacy-peer-deps、no-audit、no-fund；所查參數未加入 ignore-scripts | 不應把主程式安裝建議推廣為擴充套件安裝保證；完整套件管理器與所有分支未全面審計 |
| 擴充執行 | P4 以 jiti 載入 TypeScript；文件明示 extensions 與 Pi 程序同權限，能接觸提示詞、檔案、憑證及會話 | tool_call hook 是同程序邏輯；不可據此聲稱惡意 extension 被 OS 限制 |
| 模型／外連 | P5 openai-codex 使用 ChatGPT backend；providers 支援 API key、OAuth 與命令取密鑰 | 輸入／工具輸出可能送往所選模型服務；憑證與會話持久化另增保護責任。未讀取任何本機憑證 |

## 三種邊界與 Windows 前提

```text
worktree / 工作資料夾 --> 分開版本與預設工作位置
project trust         --> 決定是否載入部分專案資源
OS / VM 隔離          --> 真正限制可讀寫檔案、程序與網路
```

P3 明示工作目錄不阻止存取其他可存取路徑；project trust 也不限制工具權限。拒絕 trust 仍可能先讀 sessionDir，AGENTS／CLAUDE 類上下文仍可載入。只把內建工具放進容器，也未把 Pi 主程序與擴充放入同一隔離邊界。這些都不能以觀看 transcript 補足（P3）。

Windows 原生是官方列出的使用方式：npm 路徑要求上述 Node 版本；Bash 預設尋找 Git for Windows，模型可透過 defaultTools 選用 PowerShell。PowerShell 工具優先 pwsh，再退回 Windows PowerShell，啟動參數含 NoProfile、NonInteractive、ExecutionPolicy Bypass；這不是取得管理員權限，也不是沙盒。`!`／`!!` 仍走 Bash。Windows Terminal 是文件建議環境；以上只確認文件與程式契約，未測本機安裝或終端行為（P2、P3）。

上游 issue 的 Windows 實測回報（2026-11-17 補；以 GitHub API 查證狀態，內容是回報者自述，本庫沒有重現，細節見[來源筆記](../notes/2026-11-15-pi-hybrid-harness-codex-claude-antigravity.md)第 0 節）：

| 上游 issue | 回報的情形 | 狀態（2026-11-17） | 對本評估的意義 |
|---|---|---|---|
| [#9361](https://github.com/earendil-works/pi/issues/9361) | 根因已確定，不是偶發：擴充只要自己重建 bash 工具而沒把設定傳進去，設定檔的 `shellPath` 與 `shellCommandPrefix` 就一定被丟掉；官方附的擴充範例也這樣寫，macOS 上同樣重現。Windows 另有一半：沒有 `shellPath` 可用時會退回 PATH 上第一個 `bash.exe`，開了 WSL 的機器拿到的是 `C:\Windows\System32\bash.exe`（WSL 啟動器），指令就跑進 Linux 環境 | issue 開啟（14 則留言）。修正 PR [#10538](https://github.com/earendil-works/pi/pull/10538) 於 2026-10-06 關閉、**未合併**；最新發行版 v1.5.2 | 混合 harness 要自己寫擴充，這是寫擴充時必須自己處理的事：重建 bash 工具時把工作階段的 shell 設定明確傳進去，不要直接呼叫 `bash`。不是等上游修好就沒事 |
| [#7547](https://github.com/earendil-works/pi/issues/7547) | 協作者彙整 Windows 四種跑法（Git Bash、WSL bash、純 PowerShell、整個放 WSL2），每一種都有毛病。可選的 PowerShell 工具加入後，多位使用者回報把 bash 整個關掉、只留 PowerShell 錯誤明顯變少；也有人測到兩個工具都開時部分模型仍一律選 bash。PowerShell 工具自己的已知問題：指令太長會在啟動前被 Windows 拒絕、系統語言不是英文時輸出可能亂碼 | issue 開啟（96 則留言） | 與上段「可透過 defaultTools 選用 PowerShell」一致。Windows 原生若要試，關掉 bash、只留 PowerShell 是目前回報最穩的組合；但很多擴充不支援 PowerShell，`!`／`!!` 也仍走 Bash |

```text
擴充重建 bash 工具、沒傳設定 ──▶ shellPath／shellCommandPrefix 被丟掉（各平台都會）
                                      │
                                      ▼ 只在 Windows
                       退回 PATH 上第一個 bash.exe
                                      │
                         有開 WSL ──▶ System32\bash.exe（WSL 啟動器）
                                      │
                                      ▼
                         指令跑進 Linux 環境，專案工具找不到
```

這兩則不改變本文結論：它們是終端相容性問題，不是隔離能力；Pi 仍然沒有新增強制隔離。

## 三家授權與費用證據

以下官方網頁查閱日同為 2026-11-15；網頁會變動，不等同固定 Pi commit 的授權附件。

| 廠商 | 官方產品委派 | 直接 Pi provider | 證據狀態與費用界線 |
|---|---|---|---|
| OpenAI | [官方驗證文件](https://developers.openai.com/codex/auth/)區分 ChatGPT 訂閱登入與 API key；可保留官方 Codex CLI 自行驗證 | P5 宣告 openai-codex OAuth／isSubscription，連 ChatGPT backend | 官方 CLI 的兩種驗證方式已查；Pi 使用特定訂閱憑證的廠商明確授權未查證。API key 用量走 API 計費；官方 CLI 仍耗方案用量，不推定免費或無限 |
| Anthropic | [官方產品文件](https://code.claude.com/docs/en/overview)提供 CLI；[法律與合規文件](https://code.claude.com/docs/en/legal-and-compliance)要求使用原版程式與各自帳號 | P5 接受 API key／OAuth token／bearer token，只代表接得上 | 官方文件將 OAuth 定位於原生應用，且禁止第三方代收／中介 Claude.ai 憑證及代用個人方案。不可把 Max／Pro token 轉接 Pi 當採納路徑；API 或支援的雲端供應商須另核費用 |
| Google | [Antigravity 方案文件](https://antigravity.google/docs/plans)列產品與 CLI 用量；現有 relay 走 Desktop sidecar | P5 目錄有 Google／Vertex，未列 antigravity provider；不推論全倉不存在任何擴充 | 官方方案額度與 API／Vertex 憑證是不同通路。Pi 重用 Antigravity 個人額度的明確授權未查證；不提取 token。relay 的 agentapi 相容契約不等於 Google 官方穩定介面保證 |

官方 CLI 委派的優點是驗證留在官方程式內；仍須遵守各產品條款與本機路由政策，不能據此宣稱所有包裝方式均獲授權。Pi 控制平面若也使用模型，會在下游 CLI 用量以外多消耗一份模型上下文與工具迴圈；本輪未量測 token、沒有美元或節省比例結論（P5 及上列官方文件）。

## 與現有能力重疊

現有 relay 的一手依據為本機唯讀查閱的 [SPEC](https://github.com/SanHsien/agent-relay/blob/main/SPEC.md) 第 3、20 節；浮動連結只供導覽，版本見驗證紀錄。advisor 依本次已讀取的安裝版本 1.1.0 orchestration 與 cost-policy 契約評估，未重新執行其模型路由。

| 需要 | 現有能力 | Pi 新增價值／代價 |
|---|---|---|
| 跨 agent 任務／問答 | relay 已有 task、question、inbox、answer；Antigravity 可指定新 Desktop 對話 | 只是多一個 TUI 入口；需維護 extension 與回傳轉譯 |
| 選擇是否委派／審查 | advisor 已有 solo、delegate、audit、full 及成本契約 | 再加 Pi 路由容易重複決策，尚無缺口案例 |
| 互動 UI 與會話 | Pi quickstart 有續接／分支導覽，extensions 可客製 TUI | 有潛在 UI 價值，尚無實測或使用者確認的痛點 |
| 強制隔離 | Pi 文件要求另提供 OS 邊界；relay／advisor 契約也不能代替 OS 控制 | 沒有新增強制隔離能力，反增同權限程序與套件面 |

判斷：保留現有官方客戶端＋relay／advisor。未來只有明確的會話操作痛點且可證明簡單包裝不足時，才值得另提小範圍評估；本文件不新增待辦、不修改全域設定。

## 驗證紀錄與 DoD

固定來源、安全／安裝風險、Windows 前提、三家授權狀態、重疊表與採納結論均已列於上文。文件檢查結果在本節記錄；檢查只能驗證 repo 文件契約，不能證明 Pi 動態安全、授權或相容性。

- relay 唯讀版本：`0cabfe33c46bc0ca80234fad579c2ea8ba82896c`；[固定 SPEC](https://github.com/SanHsien/agent-relay/blob/0cabfe33c46bc0ca80234fad579c2ea8ba82896c/SPEC.md)。第 16 節另有維護者禁用 agy 工人政策，應維持 Desktop sidecar 路徑。
- 2026-11-15 整合時先執行 `python tools/build_index.py` 把本輪三份報告列入 README，再執行 `python tools/verify_zhtw_vocab.py --check docs && python tools/verify_inbox.py`：兩者結束碼 0（117 篇筆記、229 項任務）。撰寫時 README 尚未重產，inbox 檢查曾回 1，原因只有 README 過期與漏列本報告。
- 文件檢查只驗 repo 文件契約，不代表 Pi 通過動態測試；第三方程式全程未執行。
