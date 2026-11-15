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

測試不需 Pester 或其他第三方套件。使用五種 mock：正常、缺程式、拒絕存取、逾時、偽裝成功的敏感輸出；也實際建立無 profile 的 PowerShell 子程序驗證逾時終止與錯誤遮蔽。AST 逐一檢查主腳本與生成的查詢：命令與方法白名單、精準服務與任務選擇器、powercfg 僅 `/query`、無遠端／憑證讀取、無輸出重新導向。拒絕存取與缺命令另以 mock 放入真實子程序測試 wrapper 的 catch 分支。

| 命令 | 結束碼／結果 |
| --- | --- |
| `pwsh -NoProfile -File tests/test_inspect_windows_agent_ops.ps1` | 0；706 assertions，五種 mock 模式、真實子程序逾時／錯誤；另證明 AST 守門會拒絕修改服務、powercfg 修改參數、遠端／全量查詢及寫檔方法。 |
| `python tools/build_index.py` | 0；README 已重產。 |
| `python tools/verify_zhtw_vocab.py --check docs` | 0；繁中詞彙檢查通過。 |
| `python tools/verify_inbox.py` | 0；125 篇筆記、235 項任務契約通過。 |
| `python -m unittest discover -s tests` | 0；749 tests，169.387 秒，OK（skipped=2）。輸出中的故意缺檔／錯誤輸入訊息為反例測試，整體結束碼為 0。 |

上述 repo 命令使用 `&&` 串接，Python 執行環境設 `PYTHONUTF8=1`。完整 Python 單元測試通過，兩項跳過不算已執行；未把逾時或缺權限當成通過。

## 未執行範圍

未修改電源、NIC、睡眠、安全、登錄、服務、防火牆、排程或遠端設定；未讀憑證、全量列舉程序或排程。未執行外網、鎖屏、登出、重啟與 24 小時觀察；這些是規格中的維護者人工驗收，不屬本輪工具 DoD。`notes/` 沒有修改或結案；沒有 push。
