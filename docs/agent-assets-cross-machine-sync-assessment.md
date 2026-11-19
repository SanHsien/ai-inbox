# 共享資產跨機更新唯讀評估

日期：2026-11-15（Asia/Taipei）；對應 T-20261115-21。執行者：Codex，路由 solo。

**結論：採納既有「審查後發布＋漂移比較」的責任分工；暫緩新增跨機自動更新，不採納無條件定時 git pull。** 本輪沒有取得第二台 consumer 機器、目標版本或更新時限的需求證據。這是「需求未證實」，不是斷言使用者沒有其他機器。現有發布能力與 relay 信箱傳輸用途不同，無須另造同步常駐程式。

只讀 `C:/GitHub/agent-assets`、`C:/GitHub/agent-relay` 與 `C:/GitHub/ai-inbox`；`SanHsien/agent-assets`（私有）的能力只提供抽象結論，不公開內部檔名、排程參數、規則或程式。本輪沒有 fetch／pull、登入、credential store 讀取、排程查詢或變更，沒有執行發布、漂移檢查或通知工具。

## 1. 四個階段不能混為一談

```text
canonical repo（資產 owner 維護）
         |
         v  來源／授權／隱私／差異審查
核准版本（固定 commit + 內容 hash）
         |
         v  維護者核准、逐機備份與發布
consumer 副本（各機器、各平台原生位置）
         |
         v  原生 discovery；必要時另授權一次 smoke
已載入 session（實際使用版本，可能仍舊）

repo／核准紀錄／consumer 比較 --> 漂移證據
relay 信箱傳輸 -------------> 任務與回報，不替代技能部署
```

Git repo 更新不等於核准新版本、部署到 consumer 或讓既有 session 重新載入。Git 官方說明 [pull 會先 fetch 再整合](https://git-scm.com/docs/git-pull)，[fetch 也會寫入物件、refs 與 FETCH_HEAD](https://git-scm.com/docs/git-fetch)；`--ff-only` 只是整合限制，兩者都不是純唯讀比較，也不代表新技能安全。

## 2. 既有能力、重疊與缺口

| 既有責任 | 本輪一手檢閱證據 | 能做什麼／不能證明什麼 | Owner |
| --- | --- | --- | --- |
| 共用資產來源、核准、發布及回復 | 私有 repo 指引、契約、操作文件及發布原始碼；只讀分析 | 已有核准版本、複製發布、舊版保留與內容比較機制；不能從來源檔存在推導其他機器已部署 | 資產維護者；每項資產有單一變更 owner |
| 漂移檢查與排程包裝 | 私有 repo 相關原始碼及操作文件；未執行 | 有既存比較／排程設計，足以避免先造第二套 watchdog；本機任務是否啟用、身分、最近結果及通知送達均未查證 | 原排程維護者；本輪不新增 owner 或任務 |
| relay 跨機信箱同步 | [`agent_relay/gitsync.py:24`](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/gitsync.py#L24)、`:138–168`、`:210–216` | 同步信箱與協調資料，有提交、pull、push 與鎖；不是共享技能發布器，也不是唯讀查詢 | relay 維護者；收件端負責本機授權 |
| relay 輪詢生命週期 | [`agent_relay/poller.py:23–60`](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/poller.py#L23) | 已有 Windows Task Scheduler XML；採 InteractiveToken、LeastPrivilege、IgnoreNew、具工作目錄。原始碼不等於本機已安裝或登出仍執行 | relay 排程維護者 |
| consumer discovery／session 使用 | [Claude 官方指令載入說明](https://code.claude.com/docs/en/memory)；本輪未操作任何 consumer | 檔案一致不代表已載入。須按具體平台、版本與 session 取得證據；不能概括保證熱更新 | 每台 consumer 的操作維護者 |

特別注意：relay 既有信箱同步使用 rebase／autostash（上述 `gitsync.py:146`），其假設不應直接搬到共享技能 repo。資產更新遇 dirty／diverged 時應停止，不預設替使用者 stash、reset 或 merge。

缺口是**跨機需求與逐機版本證據未建立**，不是缺少另一支 pull 腳本。既有發布紀錄能否隔離同平台不同機器、如何彙整離線節點，也未實測；若後續需要，先在私有環境確認，不把裝置清單或私有結構放進公開報告。

## 3. Windows 三問

| 問題 | 逐項答案與本輪限制 |
| --- | --- |
| 偵測器與被監控物是否同生共死？ | 同機排程／session 與主機一起休眠、離線或停電時，不能自行證明失聯。缺少外部觀察時只能標 stale／unknown；不以「沒有警報」代表健康，也不在此啟動獨立服務 |
| 既有 Task Scheduler／plugin 是否已提供？ | 已有資產漂移檢查設計與 relay poller。保留兩者原 owner，先查既有用途及結果再決定是否有缺口；本輪沒有查詢實際排程或 runtime plugin，不宣稱正在運行 |
| Windows 原生能否執行？ | 原始碼已有 Python／PowerShell／Git 與 Windows 排程路徑，不需為本評估加 WSL。後續須固定程式絕對路徑、工作目錄、執行身分、權限與 logon type；互動終端成功不代表非互動成功 |

Microsoft 說明任務在特定安全內容與 logon type 下執行（[官方 Security Contexts for Tasks](https://learn.microsoft.com/en-us/windows/win32/taskschd/security-contexts-for-running-tasks)）。未登入、登出、重新啟動與互動 token 的可用性要分開驗收。非互動 Git 認證只能由維護者使用既有核准機制處理；不得讀出或搬運 token 來「修好同步」，也不為此開啟自動登入或擴大權限。

## 4. 人工更新與回復規格（未執行）

這是後續確有需求時的操作契約，不是新增排程提案；本輪不提供可直接啟動的同步腳本。

1. **維護者定義批次**：指定一台目標、平台、資產、既有來源位置、核准 commit／hash 與更新理由；指定資產 owner 和 consumer owner，不含任何憑證值。
2. **只讀比較先行**：由既有機制比較本機 repo、核准版本與 consumer；辨識來源、分支、dirty、diverged、離線、目標漂移及並行 owner。未取最新遠端資料就明標 freshness unknown；不把舊 tracking ref 當成遠端現況。
3. **人工核准更新操作**：確認來源與候選版本經來源／授權／隱私及靜態安全審查，列出實際 diff、精準目標與回復版本，再由維護者核准。fetch／pull 是這個寫入階段的操作，不冒充前一步的純比較。
4. **沿用既有發布流程**：在私有環境依原 runbook 備份、檢查核准版本、逐一發布；發布前再次核對來源 hash、目標 hash 與 owner，避免比較後被另一個 session 改寫。只有一個寫入 owner，沒有可靠互斥或狀態改變就停止。
5. **驗收即停**：只對該批次取一次內容一致證據，再取一次平台 discovery 證據；確需 runtime smoke 才另授權，預設一筆合成案例。既有 session 未重新載入就標舊版／unknown，不重試到「看起來有用」。
6. **回復**：發布失敗或 discovery 不相容時停止後續目標，由 consumer owner 保留診斷摘要並回復本批次的既有備份；核對回復 hash 與原生 discovery。來源的新內容用另一次受審變更修正，不重寫 Git 歷史、不遞迴刪原生目錄、不覆蓋未備份的本機修改。回復失敗即 blocked，交維護者處理。

## 5. 停止規則與合成情境

下表全部是**設計案例，非實測**；未執行 Git 同步、失敗注入或排程驗證。

| 情境 | 預期決策 | 恢復前條件 |
| --- | --- | --- |
| dirty：repo 或 consumer 有未提交／未登記修改 | STOP；保留現場，不自動 stash／reset／覆蓋 | 原 owner 辨識並處理差異，重新比較 |
| diverged：本機分支與核准來源無法 fast-forward | STOP；不自動 rebase／merge | 維護者另行決定整合策略及新核准版本 |
| 離線：來源或目標無法取得 | DEFER；保留目前可用版，freshness unknown | 連線恢復後由同一 owner 開新有界限批次，不無限重試 |
| 來源錯誤：remote、分支、owner 或 hash 不符 | BLOCK；不更新、不導向替代來源 | 核對 canonical 身分與核准紀錄 |
| 審查未通過／缺審查證據 | BLOCK；repo 最新不代表可部署 | 補齊審查並取得版本核准 |
| 並行更新或比較後 hash 改變 | STOP；不得搶鎖或終止另一個 session | 原 owner 交接或結束後重新比較與核准 |
| 舊副本回復後仍無 discovery 證據 | BLOCK／unknown；不宣稱已恢復可用 | consumer owner 依原平台 runbook 檢查，不擴大本批操作 |

## 6. 憑證、公開隱私與基準

交換範圍只限經核准的共用技能／知識／規則。native 設定、token、cookies、私鑰、私人記憶、session DB 及排程憑證都留在原生位置；NAS／共享目錄不取代 ACL、repo 權限與逐機授權。備份若含原生私密狀態，仍留在維護者既有私密備份邊界，不放進交換 repo。本輪未讀任何憑證或備份內容。

來源 Git 的 `rev-parse HEAD`／`status --short` 在三個 checkout 皆 exit 128（dubious ownership）；未調整全域 safe.directory、未確認遠端版本。公開文件只連公開來源，私有來源只寫抽象能力；基準與檢閱範圍詳見[提示檔與 API 稽核第 1 節](claude-prompt-and-api-readonly-audit.md)。交付 clone HEAD 為 `9fe96637a5a187226ced59fab06b1fcb0e4f6543`。

## 7. 文件驗收紀錄

驗收只涵蓋本輪兩份文件及索引，不代表跨機同步、技能部署、排程或通知已實測。檢查命令：

```powershell
python tools/build_index.py && python tools/verify_zhtw_vocab.py --check docs && python tools/verify_inbox.py
```

（詞彙檢查器已於 2026-11-19 移至 [`SanHsien/zhtw-vocab-guard`](https://github.com/SanHsien/zhtw-vocab-guard)，上列指令是當時的紀錄；現在改用 `python C:\GitHub\zhtw-vocab-guard\tools\verify_zhtw_vocab.py --check docs`。）

2026-11-15 執行結果：上述串接命令 exit 0，三項皆成功；README 已更新，詞彙檢查 PASS，契約驗證 PASS（125 篇筆記、235 項任務）。本輪沒有新增 runtime 需求或變更任務狀態；後續工作仍以 ROADMAP 與整合者採納結果為準。

T-21 DoD 對照：本文件包含四階段資料流、能力重疊與 owner、Windows 三問、隱私邊界、人工更新／回復、停止規則與三種以上合成情境。採納既有機制、暫緩自動更新、不採納定時拉取的結論，均屬唯讀評估交付。
