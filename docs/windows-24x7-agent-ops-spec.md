# Windows 11 常駐 Agent 維運規格

日期：2026-11-15。T-20261115-20 的交付範圍是文件與唯讀工具，沒有部署、自動登入、遠端連線或變更系統。現況證據見 [唯讀檢查紀錄](evidence/windows-agent-ops-readonly-check.md)。

## 邊界與 Windows 三問

```text
維護者 -> 人工設定與回復 -> Windows 電源 / 排程 / 選用 VPN
                                 |
                       本機 Agent 與工作目錄
                         |               |
                    對外 HTTPS       選用 VPN 終端通道
                         |               |
                  Remote Control     既有遠端存取服務

唯讀腳本 -> 固定查詢 -> 去識別 stdout
獨立裝置 -> 有界限人工觀察 -> 分項驗收紀錄
```

| 問題 | 本規格的處理 |
| --- | --- |
| 偵測器與被監控物同生共死？ | 同機腳本在主機休眠、關機或網路中斷時無法回報；由另一台裝置觀察，不能把同機 loop 當獨立存活證據。 |
| 既有機制已提供？ | 優先沿用 Task Scheduler、既有 relay 輪詢與資產漂移檢查；維護者確認用途、owner、精準名稱與路徑後才查，未確認不建立第二個 watchdog。 |
| Windows 原生能跑？ | 工具使用 PowerShell 7 與 Windows 查詢介面，不依賴 WSL、sh 或 Herdr。互動成功與排程成功須分開驗收。 |

## 官方依據與適用條件

以下一手來源於 2026-11-15 查閱；安裝與未來設定以來源當時內容為準。

| 來源 | 本規格採用的事實與限制 |
| --- | --- |
| [Microsoft powercfg](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options) | `/query` 讀取電源配置；`/change` 等另有修改用途。工具只讀目前配置的睡眠閒置秒數，0 表示該閒置設定為不自動睡眠，不能推論整台主機永不休眠。 |
| [Get-CimInstance](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance) | 使用本機、具名服務篩選與操作逾時，不傳遠端電腦或認證。 |
| [Get-ScheduledTask](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/get-scheduledtask) | 精準指定 TaskName 與 TaskPath；只投影 State，不公開 Principal、Actions 或參數。Ready 不能證明工作已成功執行。 |
| [Task Scheduler 安全內容](https://learn.microsoft.com/en-us/windows/win32/taskschd/security-contexts-for-running-tasks) | 任務依指定 identity 與登入類型執行，權限、互動桌面及網路資源可用性不可由手動執行結果推定。 |
| [Claude Remote Control](https://code.claude.com/docs/en/remote-control) | 延續本機工作，需要相容訂閱與登入，API key 不支援。只發起對外 HTTPS，無須新增入站規則；主機與本機程序必須存活。對話與工具活動會經 Anthropic 服務，不可當成完全離線。 |
| [Tailscale unattended](https://tailscale.com/docs/how-to/run-unattended) | Windows 可由維護者啟用 Run unattended，登入與裝置授權為前提；登出或重啟後仍可連 VPN，不代表 Agent 或遠端桌面服務已恢復。 |

Remote Control 與 VPN 是不同層：前者延續 Claude 工作，後者提供網路通道；VPN 本身不提供終端、桌面或 Agent。Remote Control 不以 Tailscale 為必要相依。安裝入口採官方文件，工具不安裝任何產品、不執行供應商 CLI，也不呼叫登入診斷。

**不可照抄的組合：關閉權限確認＋Remote Control（2026-11-17 補）**：[來源筆記](../notes/2026-11-15-hujiaxi-24x7-local-agent-cluster-architecture.md)第 0 段記錄，原貼文作者的截圖裡，同一個工作階段狀態列顯示 `bypass permissions on`，同時被 Remote Control 遠端操控，設定頁的「Enable Remote Control for all sessions」也是 true。那套架構的便利有一部分來自關掉權限確認。本規格不採用：會接受 Remote Control 的工作階段，不得以 `bypass permissions`、`--dangerously-skip-permissions` 或等效設定執行；Remote Control 逐次由維護者啟動，不啟用全 session 預設。理由是兩者疊在一起時，任何拿得到該帳號遠端入口的人或被注入的指令，都能在主機上不經確認執行任意工具。這一條是依截圖描述訂的本地規範，本機沒有重現該組合。

## 唯讀工具介面與停止條件

從 repo 根目錄執行：

```powershell
pwsh -NoProfile -File tools/inspect_windows_agent_ops.ps1
# 維護者已核對兩個排程的精準名稱後，才選用：
pwsh -NoProfile -File tools/inspect_windows_agent_ops.ps1 -RelayTaskName 'ExampleRelay' -AssetsTaskName 'ExampleAssets' -TaskPath '\' -TimeoutSeconds 5
pwsh -NoProfile -File tests/test_inspect_windows_agent_ops.ps1
```

白名單只有：`powercfg.exe /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE`、`Get-CimInstance` 查 `Schedule`／`Tailscale` 的 State、指定排程的 `Get-ScheduledTask`、`Get-Command` 找四個程式的 Application，以及 EXE 版本中繼資料讀取。程式版本不是 PATH 中 shim 所指套件版本的保證；非 EXE、預覽版字串、拒絕存取或未能解析均標 unknown，不啟動 CLI 追查。沒有全量程序、排程列舉、網路探測、服務修改或憑證存取。

每項查詢由同一 PowerShell 執行檔在無 profile 的子程序執行，預設最多 5 秒，允許 1～30 秒；逾時只終止自己建立的查詢子程序樹，不重試。最多十項查詢，預設八項；另計程序啟動與終止開銷。錯誤原文與原始查詢結果不輸出；stdout 只含固定鍵、狀態、有限列舉或數字。睡眠 AC／DC 各查一次，並非原子快照。

`ok` 表示欄位查詢成功，`not-installed` 表示查詢所需命令不存在，`unknown` 表示 unavailable／timeout／query-failed／not-configured。缺服務或指定任務不存在也可能回 unknown，不等同未安裝。exit 0 只表示摘要已產生；unknown 不算健康，沒有任何 24×7 合格判定。參數錯誤或腳本本身失敗為非零。工具不寫檔；公開證據只保留摘要，禁止附主機名稱、帳號、IP、節點名稱、原始錯誤或任務動作。

## 維護者設定與回復（本輪未執行）

先在本機私有紀錄保存原值與 owner，不能把設定匯出、帳號或裝置資料提交到公開 repo。逐項修改、逐項驗收；無本機回復管道、權限不明、工作未保存時立即停止。

| 項目 | 維護者人工步驟 | 回復方式 |
| --- | --- | --- |
| 電源 | 在 Windows 設定的電源／螢幕與睡眠頁記下 AC／電池原值；依設備散熱、供電與實際需求選擇睡眠時間。不要停用安全鎖屏；不一律停用休眠、NIC 省電或更新。 | 在相同頁面還原記下的每個原值，再執行唯讀查詢核對。UPS、BIOS 斷電恢復與電池耗盡行為須另由維護者查設備手冊，這裡未查證。 |
| 自啟動 | 先確認既有排程 owner 與用途；需要修改時由 owner 在 Task Scheduler 保存原設定，明定 executable、引數、工作目錄、觸發條件、重試上限及禁止重疊執行。桌面型 Agent 採登入後啟動；可非互動執行的工作才評估開機觸發。 | 還原原設定；若為新建工作，只移除該工作並核對沒有重複執行個體。不得刪除其他 owner 的排程。 |
| identity／認證 | 採最小權限與正確工作目錄；驗證非互動環境下 PATH、repo 權限、網路資源及供應商支援。需要登入時由維護者操作。不可複製 token、Cookie、私鑰至排程參數、git 或 NAS；不預設 Windows 自動登入。 | 回復原 identity 與觸發條件；登入問題回到官方人工流程，不降低安全限制。 |
| Remote Control | 維護者核對官方訂閱與登入前提，在可信專案終端啟動 `claude remote-control` 或既有 session 的 `/remote-control`，自行連接。不要公開連線網址或 QR code。 | 停止該次 Remote Control；若曾自行啟用全 session 預設，從相同官方設定介面關閉，保留原本安全與防火牆設定。 |
| 選用 Tailscale | 已安裝並由維護者登入後，依官方 UI 的 Preferences → Run unattended 設定；確認 owner、裝置授權及現有遠端服務 ACL。不因本規格停用 key expiry，也不新增入站規則或公開服務。 | 在相同 UI 取消 Run unattended，確認回到原先模式；事先保留本機操作管道，避免回復時自鎖。 |

登出會結束互動登入環境；排程 identity、登入類型與工具支援決定能否繼續運行。重啟必然中斷當前程序；自啟動不等於恢復原 session 或未完成工作。要由 owner 設計 checkpoint 與去重，不能以「有排程」推定恢復成功。

## 人工驗收表（均待維護者執行）

只使用一筆唯一前綴 `ops-smoke-<日期時間>` 的無敏感測試工作，各階段沿用同一筆。每層只保留一次去識別權威證據；遇權限、登入、意外寫入、重複工作、連線失敗或安全警告即停止，按上一表回復，不反覆建立工作或重新登入。

| 階段 | 操作與成功條件 | 時限／紀錄 |
| --- | --- | --- |
| 基準 | 保存工作，核對 owner、原值、唯讀摘要與本機回復方式；unknown 項由維護者釐清。 | 10 分鐘內不能釐清就停；記通過／失敗／未執行。 |
| 外網 | 第二台裝置使用不同網路，在選定 Remote Control 或既有 VPN 終端通道讀到該筆 smoke 的狀態；記實際採用通道。 | 一次、5 分鐘；同網段成功不能替代。 |
| 鎖屏 | 鎖屏後從第二裝置確認同一工作仍可查看；不以解鎖畫面推定 Agent 存活。 | 一次、5 分鐘；記恢復耗時。 |
| 登出 | 先確認可安全中斷；登出後分開驗證 VPN 存活與 Agent 行為，應符合事前選定的互動／非互動設計。需登入才恢復的 Agent 如實記限制。 | 一次、10 分鐘；遠端通道失效即本機回復。 |
| 重啟 | 保存 checkpoint 後重啟，先驗 VPN／主機，再依設計登入或等待排程，確認工作恢復且沒有重複執行；不能只驗程序存在。 | 一次、15 分鐘；記中斷與恢復時間。 |
| 有界限觀察 | 由獨立裝置在 0、8、24 小時觀察同一筆工作與通道；記離線區間、意外重啟及未知時段。 | 最多 24 小時、三次觀察；首次異常即停。抽樣有盲區，通過只代表該期間觀察結果。 |

本表未執行，不屬文件／唯讀工具 DoD；沒有宣稱部署或 24×7 穩定。後續若需工作追蹤，僅在 [ROADMAP](../ROADMAP.md) 登記。
