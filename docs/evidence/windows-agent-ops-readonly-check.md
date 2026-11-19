# Windows Agent 維運唯讀檢查證據

日期：2026-11-15。任務 T-20261115-20；基準 HEAD `9fe96637a5a187226ced59fab06b1fcb0e4f6543`，分支 `worker/t20`。僅為文件／工具驗收，不代表部署完成。規格見 [維運規格](../windows-24x7-agent-ops-spec.md)。

## Windows 原生實際查詢

命令：`pwsh -NoProfile -File tools/inspect_windows_agent_ops.ps1`，exit **0**。在 Windows 上實際執行一次，未提升權限、未連線、未登入。無參數，不查任何使用者排程；輸出只保留固定欄位，原始錯誤及識別資訊不寫入本檔。

| 固定欄位 | status | reason | value |
| --- | --- | --- | --- |
| sleep_ac | unknown | unavailable | null |
| sleep_dc | unknown | unavailable | null |
| scheduler | unknown | unavailable | null |
| tailscale_service | unknown | unavailable | null |
| version_claude | unknown | unavailable | null |
| version_codex | unknown | unavailable | null |
| version_tailscale | not-installed | missing-command | null |
| version_pwsh | unknown | unavailable | null |
| relay_task | unknown | not-configured | null |
| assets_task | unknown | not-configured | null |

unknown 是實際結果，不作健康推定；可能涉及權限、不可取得的版本中繼資料或格式，沒有追查原始錯誤。`version_tailscale` 只代表此執行環境找不到對應 Application，不保證整台主機未安裝。未取得實際排程名稱與路徑，所以不列舉、不推測服務 owner 或 runtime。

## 測試與 repo 檢查

測試不需 Pester 或其他第三方套件。使用五種 mock：正常、缺程式、拒絕存取、逾時、偽裝成功的敏感輸出；也實際建立無 profile 的 PowerShell 子程序驗證逾時終止與錯誤遮蔽。AST 逐一檢查目前主腳本與生成的查詢：命令及完整方法接收者／呼叫白名單、精準服務與任務選擇器、powercfg 僅 `/query`、遠端／憑證相關語法限制與無輸出重新導向；成員賦值僅允許固定啟動設定及結果欄位，依[守門測試](../../tests/test_inspect_windows_agent_ops.ps1)，New-Object 一律拒絕，::new 僅允許原始碼中兩種固定、無參數的 ProcessStartInfo／Process 呼叫；三種建構路徑共用危險型別清單（IO.StreamWriter、IO.StreamReader、IO.FileStream、IO.FileInfo、IO.DirectoryInfo、Diagnostics.ProcessStartInfo、Diagnostics.Process），ConvertExpressionAst 型別轉換拒絕清單內型別，涵蓋簡寫及 System. 完整名稱，其他型別轉換未作全面限制。FileName 固定為目前 PowerShell 執行檔，ArgumentList 僅允許既有五項呼叫；Start／Kill 另檢查本地建構、未重新綁定／傳出別名、啟動順序與逾時分支。這是目前原始碼及已列反例的回歸契約，並非任意 PowerShell 的安全沙盒或完整資料流證明；不保證命令搜尋路徑不受同名程式遮蔽。拒絕存取與缺命令另以 mock 放入真實子程序測試 wrapper 的 catch 分支。

| 命令 | 結束碼／結果 |
| --- | --- |
| `pwsh -NoProfile -File tests/test_inspect_windows_agent_ops.ps1` | 0；R2 修正後 1440 assertions，五種 mock 模式、真實子程序逾時／錯誤；只解析的反例涵蓋屬性賦值／遞增／索引、Put／SetValue、New-Object／危險型別建構、任意程序啟動、FileName／引數及非自建程序終止。記憶體內逐組停用六道新限制，13 個對應反例的拒絕斷言全部轉紅（13/13 killed）；測試本身維持綠燈。 |
| `python tools/build_index.py` | 0；README 已重產。 |
| `python tools/verify_zhtw_vocab.py --check docs` | 0；繁中詞彙檢查通過。（當時的紀錄；檢查器 2026-11-19 已移至 [`SanHsien/zhtw-vocab-guard`](https://github.com/SanHsien/zhtw-vocab-guard)，現在改用 `python C:\GitHub\zhtw-vocab-guard\tools\verify_zhtw_vocab.py --check docs`。） |
| `python tools/verify_inbox.py` | 0；125 篇筆記、235 項任務契約通過。 |
| `python -m unittest discover -s tests` | 0；749 tests，169.387 秒，OK（skipped=2）。輸出中的故意缺檔／錯誤輸入訊息為反例測試，整體結束碼為 0。 |

上述 repo 命令使用 `&&` 串接，Python 執行環境設 `PYTHONUTF8=1`。完整 Python 單元測試通過，兩項跳過不算已執行；未把逾時或缺權限當成通過。

## 未執行範圍

未修改電源、NIC、睡眠、安全、登錄、服務、防火牆、排程或遠端設定；未讀憑證、全量列舉程序或排程。未執行外網、鎖屏、登出、重啟與 24 小時觀察；這些是規格中的維護者人工驗收，不屬本輪工具 DoD。`notes/` 沒有修改或結案；沒有 push。

## 2026-11-19 基準階段：根因、修正與實跑

基準 HEAD `a67b04c`，改動未提交。2026-11-15 那次幾乎全欄 unknown，這次先在查詢子程序裡加暫時診斷輸出量出原因，量完已移除。

| 欄位 | 2026-11-15 回 unknown 的實際原因 | 處理 |
| --- | --- | --- |
| sleep_ac、sleep_dc | 工具的錯。`powercfg` 對這個設定輸出五個十六進位值（最小、最大、增量、AC、DC），工具要求剛好兩個，所以判成格式不符。 | 已修：接受兩個或五個，取最後兩個。 |
| tailscale_service | 這台沒有這個名稱的服務，查詢回空值。 | 設計上的 unknown；reason 改成 not-found。 |
| version_claude、version_codex | PATH 上第一個同名程式是 `.cmd` shim，沒有版本中繼資料。 | 設計上的 unknown；reason 改成 non-exe-shim。 |
| version_pwsh | PATH 上的 pwsh 是 Microsoft Store 執行別名（零位元組檔），讀不到版本。 | 設計上的 unknown；reason 改成 store-alias。 |
| scheduler | 本次量測時已是 ok；2026-11-15 回 unknown 的原因沒有重現，未查證。 | 沒改查詢內容，只加了服務不存在時回 not-found。 |

量測另外確認兩件事：Store 版 PowerShell 的套件內執行檔可以直接啟動當查詢子程序，子程序機制本身沒壞；PowerShell 執行檔的版本字串尾端帶建置雜湊，原本的格式檢查會把它判成 unknown，這個也一併修了（只輸出前面的數字版本），在本機以真實子程序加上替換過的 `Get-Command` 驗證，沒有在非 Store 安裝的機器上實跑。

兩次實跑都是 exit **0**，未提升權限。第一次無參數；第二次帶維護者提供的兩個排程名稱與 `-TaskPath '\'`，排程名稱不寫入本檔。

| 固定欄位 | 無參數 | 帶排程參數 |
| --- | --- | --- |
| sleep_ac | ok／none／0 | ok／none／0 |
| sleep_dc | ok／none／900 | ok／none／900 |
| scheduler | ok／none／Running | ok／none／Running |
| tailscale_service | unknown／not-found | unknown／not-found |
| version_claude | unknown／non-exe-shim | unknown／non-exe-shim |
| version_codex | unknown／non-exe-shim | unknown／non-exe-shim |
| version_tailscale | not-installed／missing-command | not-installed／missing-command |
| version_pwsh | unknown／store-alias | unknown／store-alias |
| relay_task | unknown／not-configured | ok／none／Ready |
| assets_task | unknown／not-configured | ok／none／Ready |

讀法：AC 的 0 只表示接電源時這個閒置設定不會自動睡眠，不能推論主機永不休眠；DC 是 900 秒。Ready 只表示排程存在且可執行，不代表執行過或成功。四個 unknown 與一個 not-installed 都不算健康，也不算故障。

| 命令 | 結束碼／結果 |
| --- | --- |
| `pwsh -NoProfile -File tests/test_inspect_windows_agent_ops.ps1` | 修正前先加回歸測試，結果非零（紅）；修正後 0，2330 assertions。mock 模式由五種增為八種（新增：細分 reason、reason 用在錯的欄位種類、清單外的 reason 字串），另有三個走真實子程序、系統命令全換成函式的端到端情境（Store 套件環境、一般安裝、非預期的十六進位值數量）。記憶體內停用限制的 mutation 檢查維持 16 個反例全部轉紅。 |

本節未執行：owner 核對、保存工作、本機回復方式確認，以及外網、鎖屏、登出、重啟、24 小時觀察。沒有修改任何 Windows 設定，沒有啟動 claude、codex 等 CLI，沒有讀憑證。`build_index.py` 沒有跑，沒有提交或推送。
