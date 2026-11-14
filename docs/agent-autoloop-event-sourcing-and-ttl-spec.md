# Agent Autoloop 事件溯源內核、掛起零消耗與四層安全防線規格

> 對應任務：`T-20261108-02`；本文件定義本 repo 的離線檢驗契約，以[驗證器原始碼](../tools/verify_autoloop_dispatch_guard.py)與[回歸測試](../tests/test_verify_autoloop_dispatch_guard.py)為準。

## 1. 架構與查證邊界

參考專案 [KKKKhazix/agent-autoloop 官方 README](https://github.com/KKKKhazix/agent-autoloop/blob/main/README.md)描述事件來源、派工、Worker 回覆後退出及人工回答後續接的流程。此為上游文件描述，本次未安裝或執行上游；「1,850 行」、交易持久性、整個系統 0 RSS／0 Token 等量化保證未查證，不作為本工具驗收結論。

以下是本 repo 的檢驗模型；輸入是設定快照，不是實際執行環境。來源：[audit_bundle 與 default_clean_bundle](../tools/verify_autoloop_dispatch_guard.py)。

```text
事件快照 + 本機規則 + 依序排列的單一父子事件鏈 + 隔離設定
                      |
                      v
                必要 schema 檢查
                      |
                      v
           AUTOLOOP-001 / 002 / 003 / 004
                      |
                      v
          findings 非空 -> exit 1；否則 exit 0
```

## 2. 四層檢驗契約

- `AUTOLOOP-001`：事件禁止出現下列欄位，鍵名先做 NFKC、去頭尾空白、轉小寫後比對，並遞迴檢查巢狀物件與清單（如 `payload.cwd`、`CWD`）： `cwd`、`agent`、`to`、`access`、`program`、`command`、`skill`、`parallel`、`hop`。事件 `type`／`id` 必填；`link`／`context_file` 若有提供，也必須符合 `^[A-Za-z0-9._:/-]+$`。來源：[FORBIDDEN_EVENT_FIELDS、check_event_payloads、validate_bundle_schema](../tools/verify_autoloop_dispatch_guard.py)。
- `AUTOLOOP-002`：遞迴檢查規則中所有字串欄位，包括 `prompt`、`command`、`cwd`、`program` 及巢狀參數，共用同一模板檢查。只接受 `{type}`、`{id}`、`{link}`、`{context_file}`；拒絕未知欄位、屬性／索引存取、轉換及格式規格，也拒絕無法解析的括號。`when.source` 採白名單制（NFKC、去空白、轉小寫後比對）：信任度低的外部來源 `github`、`gitlab`、`webhook`、`external`，與本機來源 `local`、`manual`、`cron`；其他來源（例如 `slack`）一律拒絕。外部來源同時使用 `access="full"`（大小寫不拘）與 `resume=true` 會被拒絕。白名單常數為原始碼 `ALLOWED_SOURCES`，新增來源須同步修改原始碼、測試與本節。來源：[template_strings 與 check_dispatch_rules](../tools/verify_autoloop_dispatch_guard.py)。
- `AUTOLOOP-003`：`hop` 是非負整數，布林值不算整數；相鄰節點必須滿足 `child.hop == parent.hop + 1`，包括 `ask`／`later`。首節點可代表既有鏈的片段，沒有可比較的父節點。`max_hops` 預設 8，且上限固定為 8（`MAX_HOPS_LIMIT`）：設定檔填大於 8 的值本身就判違規，檢查超限時也以 8 為準，不能靠調高設定放行第 9 跳以後的派工。超限節點只能 `dispatched=false`，缺省 `dispatched` 視為 true。來源：[check_hop_chain 與 validate_bundle_schema](../tools/verify_autoloop_dispatch_guard.py)。
- `AUTOLOOP-004`：Worker 工具清單拒絕原始碼 `SELF_APPROVAL_TOOLS` 列出的名稱（比對前一律 NFKC、去空白、轉小寫，故 `Autoloop_Answer` 同樣被拒）；`delivery.checkout_pr_code` 與 `delivery.allow_octopus_merge` 必須明列為布林值，且 true 會被拒絕。ACL 清單不得空白，僅接受 `CURRENT_USER` 與 `SYSTEM`，包含 `Administrators` 在內的其他名稱都拒絕。來源：[check_worker_and_delivery_isolation 與 validate_bundle_schema](../tools/verify_autoloop_dispatch_guard.py)。

## 3. Schema 與結束碼

`events`、`rules`、`hop_chain` 必須是非空物件清單，`isolation` 必須包含 `worker_tools` 字串清單（可空）、`delivery` 物件與非空 `windows_data_dir_acl` 字串清單。規則必填非空 `name`、`to`、`cwd`、`access`、`prompt`、布林 `resume` 及含非空 `source` 的 `when` 物件。缺少必要區塊或型別錯誤產生 `AUTOLOOP-SCHEMA`。來源：[validate_bundle_schema](../tools/verify_autoloop_dispatch_guard.py)。

```powershell
# 只檢查內建正常範例；不執行反例測試，也不驗證本機部署
python tools/verify_autoloop_dispatch_guard.py
# 檢查指定快照；不讀取實際 Windows ACL
python tools/verify_autoloop_dispatch_guard.py --config path/to/autoloop_bundle.json --json
# 正反例與回歸測試
python -m unittest discover -s tests -p test_verify_autoloop_dispatch_guard.py -v
```

結束碼：0 表示提供的快照通過；1 表示違規、schema 無效、JSON 空白／損壞或檔案無法讀取；2 是 argparse 的命令列用法錯誤。`--json` 對成功載入的 JSON 輸出 `passed` 與 `findings`；讀檔／解析失敗輸出 stderr 文字。來源：[main](../tools/verify_autoloop_dispatch_guard.py)與 [argparse 官方文件](https://docs.python.org/3/library/argparse.html#exiting-methods)。

## 4. 限制

本工具沒有執行派工、建立 context 檔案、強制終止程序、發送告警、驗證實際 OS ACL 或讀取 Git PR；它只檢查快照中的宣告，無法證明執行器遵守宣告。模板字元檢查也不是 shell escaping 或完整 prompt injection 防護；呼叫端仍須以資料傳遞外部正文，並對實際代入值及使用情境另行驗證。來源：[完整驗證器](../tools/verify_autoloop_dispatch_guard.py)。

防火牆工具另以實際 `content` 計算 UTF-8 SHA-256，拒絕自附雜湊不符、絕對／磁碟機／UNC 路徑與未知工具，依 workspace 解析後比較允許根目錄。每種工具有欄位白名單（例如 `run_command` 才可帶 `command`、`edit_file` 才可帶 `old_string`／`new_string`），出現白名單外欄位回 `UNKNOWN_FIELD`；審批收據的 `request_digest` 涵蓋整個 canonical call（所有欄位、path 正規化、鍵排序後序列化），因此審批後替換 `command`、`new_string` 等任何欄位都回 `DIGEST_MISMATCH`。同一程序內除已消費的 `receipt_id` 外也記錄已消費的 digest，同一請求換新 `receipt_id` 重送回 `REPLAYED_REQUEST`。路徑含 `:`（NTFS 替代資料串流、磁碟機代號）、前後空白、區段結尾為 `.` 或空白、Windows 保留裝置名（CON、NUL、COM1 等）或 8.3 `~N` 短名者回 `UNSAFE_PATH`。其 CLI 結束碼為 0（全通過）、1（拒絕或輸入路徑不存在）、2（輸入／schema／命令列用法無效）；未指定輸入也回 2。收據狀態僅存於單次程序記憶體，解析路徑後的檔案系統競態與收據簽章驗真不在此工具範圍內。來源：[ToolCallFirewall、compute_request_digest 與 main](../tools/verify_tool_call_firewall.py)、[防火牆測試](../tests/test_verify_tool_call_firewall.py)。
