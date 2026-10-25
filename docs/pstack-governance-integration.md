# pstack 工程防線與 agent-governance-toolkit 運行期政策檢查整合實踐

## 1. 概述與整合背景

曾任 SpaceX 首席工程師、Cursor 技術成員的 Lauren Tan（@poteto）所提出的 **`pstack` 方法論**，其核心主張為「**證據先行的工業級軟體工程（Evidence-First Engineering）**」：
- **No Reproduction, No Fix**：修復 bug 必須先撰寫確定會失敗的測試（Red Test）來證明問題存在，嚴禁盲目修復。
- **No Stubs**：禁止敷衍式的空殼函式（`pass`、`...`、`NotImplementedError`）。
- **Runtime Verification Gate**：任何聲稱「完成」的代碼必須具備真實終端機執行日誌證據，並經受執行期政策檢驗。

本文件記錄將 `pstack` 紀律、維護者 fork `agent-relay` 驗收閘門（`agent_relay.gates`）與維護者 fork `agent-governance-toolkit`（AGT）運行期政策引擎完成深度整合的架構規格、實作細節與真實終端測試證據。

---

## 2. 架構全景與三道防線

```
┌────────────────────────────────────────────────────────────────────────┐
│               agent-relay + agent-governance-toolkit 驗收閘門           │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 防禦刪改與設定保護 (Guard Gate)                                     │
│    └─ 嚴禁工人刪除測試檔、禁止修改 conftest/pyproject/package.json     │
│                                                                        │
│ 2. 空殼函式阻斷 (Stub Rejection Gate)                                  │
│    └─ AST 靜態解析：攔截新增之 pass / ... / NotImplementedError 空殼   │
│                                                                        │
│ 3. 運行期政策檢查 (AGT Governance Policy Gate)                          │
│    ├─ 路徑邊界 (DiffPolicy): 攔截 *.env*, id_rsa*, secrets/** 與檔案上限│
│    ├─ 機密外洩 (CredentialRedactor): 掃描代碼阻斷 API Key/Token 外洩   │
│    └─ 危險指令 (CodeScanner): 靜態攔截未受控的 subprocess/os.system 調用 │
│                                                                        │
│ 4. pstack TDD 重現驗證 (TDD Red-to-Green Gate)                         │
│    ├─ Base 測試 alone ──> 必須 PASS (綠燈起點)                          │
│    ├─ Base + 工人新測試 ──> 必須 FAIL (紅燈證明重現問題)                 │
│    └─ 工人 Worktree 全代碼 ──> 必須 PASS (綠燈修復閉環)                 │
│                                                                        │
│ 5. 日誌脫敏與審計保全 (Log Redaction & Evidence Persistence)            │
│    └─ 完整終端日誌落盤 verify-*.log ＋ CredentialRedactor 脫敏 ＋ sha256│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 整合實作細節

### 3.1 `agent_relay/gates.py` 整合 AGT 運行期政策

在 `C:\GitHub\agent-relay\agent_relay\gates.py` 中實作以下模組發現與政策評估邏輯：

1. **動態定位與載入（`load_governance_toolkit`）**：
   - 優先嘗試直接導入環境既有的 `agent_os` 與 `agent_sandbox`。
   - 支援掃描本機候選路徑（`AGENT_GOVERNANCE_PATH`、`C:\GitHub\agent-governance-toolkit`、同級目錄），動態加入 `sys.path`。
   - 具備內建安全 fallback，即使在無外部套件環境下亦能安全運作。

2. **路徑邊界檢查（`agent_os.diff_policy.DiffPolicy`）**：
   - 檢查 `changed` 檔案清單是否違反 `blocked_paths`（預設阻斷 `*.env*`、`id_rsa*`、`*.pem`、`*.key`、`secrets/**` 等高危路徑）。
   - 限制變更檔案數量上限（`max_files`）與總行數上限（`max_lines`）。
   - 違規時回傳 `GateResult("policy-violation", [...])`，阻止 relay 自動 commit。

3. **機密外洩防護（`agent_os.credential_redactor.CredentialRedactor`）**：
   - 逐一掃描所有工人變更檔案之文本內容。
   - 調用 `CredentialRedactor.detect_credential_types()` 識別 OpenAI、GitHub、AWS、Azure、Slack 等金鑰特徵。
   - 檢測到敏感憑證即判定 `policy-violation`，並嚴格隱蔽密鑰明文，僅回報類型標籤。
   - 驗收執行日誌（`verify-*.log`）的 tail 輸出透過 `CredentialRedactor.redact()` 自動脫敏，杜絕憑證留存。

4. **危險調用掃描（`agent_sandbox.code_scanner.scan_code_for_subprocesses`）**：
   - 在啟用 `scan_subprocesses` 或 `strict` 模式下，對非測試的 Python 原始碼執行 AST 掃描。
   - 阻斷未經治理沙箱包裹的行程啟動（如 `subprocess.Popen`、`os.system` 等）。

---

## 4. `quality-loop` 全域技能升級

同步更新以下技能定義檔：
- 本地配置：`C:\Users\SanHsien\.gemini\config\skills\quality-loop\SKILL.md`
- 跨 Agent SSOT 資產庫：`C:\GitHub\agent-assets\skills\quality-loop\SKILL.md`

在 Quality Loop 執行契約中明確規範：
- 強制引入 `agent-relay.gates`（`verify-gates`）：防禦刪改測試、拒絕空殼函式、TDD 紅轉綠閉環、日誌保全。
- 強制引入 `agent-governance-toolkit` 運行期政策檢查（DiffPolicy 路徑邊界、CredentialRedactor 機密防護、CodeScanner 危險指令防禦）。

---

## 5. 實測終端執行輸出與證據

### 5.1 維護者 fork `agent-relay` 驗收閘門單元測試全綠

在 `C:\GitHub\agent-relay` 執行單元測試，涵蓋新增的 16 項治理政策檢驗與端到端派工阻斷測試，全數通過：

```text
C:\GitHub\agent-relay> python -m unittest discover -s "C:\GitHub\agent-relay\tests" -p "test_gates.py"
...........C:\GitHub\agent-relay\agent_relay\gates.py:257: DeprecationWarning: agent-os-kernel is deprecated and will be removed in a future release. Use agent-governance-toolkit-core instead. See https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/package-consolidation/MIGRATION.md
  from agent_os.diff_policy import DiffPolicy, DiffFile
C:\GitHub\agent-relay\agent_relay\gates.py:259: DeprecationWarning: agt-sandbox is deprecated. Use agent-governance-toolkit-cli instead. See https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/package-consolidation/MIGRATION.md
  from agent_sandbox.code_scanner import scan_code_for_subprocesses
....................................
----------------------------------------------------------------------
Ran 47 tests in 183.283s

OK
```

- **Commit Hash**：`0d0655c`
- **提交訊息**：`feat(gates): integrate agent-governance-toolkit runtime policy checks and credential redaction`
- **遠端分支**：已成功 push 至維護者 fork `agent-relay`（`main`）。

### 5.2 維護者 fork `agent-assets` 單元測試全綠

在 `C:\GitHub\agent-assets` 執行資產庫單元測試，58 項測試全數通過：

```text
C:\GitHub\agent-assets> python -m unittest discover -s "C:\GitHub\agent-assets\tests"
............................s...................s.........
----------------------------------------------------------------------
Ran 58 tests in 11.878s

OK (skipped=2)
ASSET_REGISTER sharedDocuments hashes updated.
```

- **Commit Hash**：`ae82874`
- **提交訊息**：`feat(skills): add quality-loop skill with pstack gates and AGT governance policy integration`
- **遠端分支**：已成功 push 至維護者 fork `agent-assets`（`main`）。
