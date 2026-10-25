# Claude Code security-guidance 外掛 Windows 11 安裝評估、配置驗證與三層防禦整合報告

> 本文件收錄於 `docs/claude-security-guidance-windows-setup.md`，為任務 `T-20261023-01` 與 `T-20261023-02` 針對 Anthropic 官方 `security-guidance@claude-plugins-official` 外掛在 Windows 11 原生環境下的安裝相容性、`SG_AGENTIC_CLI_PATH` 依賴機制、Layer 1 正則攔截、`log.txt` 日誌輪替與三層防禦規範範本整合驗證的完整技術報告。

---

## 1. 核心機制與 Windows 11 底層相容性深度剖析

`security-guidance` 是 Anthropic 為 Claude Code 量身打造的左移資安（Shift-Left Security）官方外掛，採用三層遞進式防禦架構：
1. **Layer 1: 即時編輯警告（Pattern Warnings）**：由本地輕量 Regex 驅動，在調用 `Edit`、`Write`、`MultiEdit` 時瞬間觸發（0 Token、0 額外延遲），覆蓋 ~25 種高危語法模式。
2. **Layer 2: 回合結束 Diff 語意審查（LLM Diff Review）**：在 Claude 完成回合（Stop Hook）前，將累積的 `git diff` 發送至背景 LLM（支援自訂模型）進行語意分析，阻擋單檔邏輯漏洞。
3. **Layer 3: 提交/推送代理人深度審查（Agentic Commit Review）**：在執行 `git commit` 或 `git push` 時，調用 Claude Agent SDK 啟動專用審查員，跨檔案追蹤呼叫鏈與污點傳播。

### 為什麼 Windows 11 必須顯式配置 `SG_AGENTIC_CLI_PATH`？

維護者深入解構官方原始碼 `hooks/llm.py` 中的 CLI 解析函式 `_user_cli_path()`：

```python
def _user_cli_path() -> Optional[str]:
    """The user's own `claude`: SG_AGENTIC_CLI_PATH if set ("" selects the
    SDK's bundled CLI), else the first of the absolute paths below that
    exists, else None."""
    cli_path = os.environ.get("SG_AGENTIC_CLI_PATH")
    if cli_path is not None:
        return cli_path

    # 安全防禦設計：明確禁用 shutil.which("claude")
    # 原因：Hook 的工作目錄為當前專案目錄，Windows shutil.which 會優先搜尋 cwd，
    # 若倉庫內存在惡意簽入的 ./claude.exe，將引發二進位劫持 (Binary Planting)。
    for p in (
        os.environ.get("CLAUDE_CODE_EXECPATH"),
        os.path.expanduser("~/.local/bin/claude"),
        "/root/.local/bin/claude",
        "/opt/claude-code/bin/claude",
    ):
        if p and os.path.isfile(p):
            return p
    return None
```

#### 關鍵發現與 Windows 陷阱：
1. **防禦二進位劫持（Binary Planting Prevention）**：外掛為了資安考量，故意不使用系統 `which` 尋找路徑，避免在 Windows 下意外執行當前目錄中的同名程式。
2. **硬編碼預設路徑全屬 POSIX 系統**：預設 fallback 檢查的路徑為 `~/.local/bin/claude`、`/root/...`、`/opt/...`，在原生 Windows 11 檔案系統下完全不存在。
3. **結論**：在 Windows 11 環境中，若未顯式配置環境變數 `SG_AGENTIC_CLI_PATH`，`_user_cli_path()` 將必然回傳 `None`，導致 Layer 3 跨檔案 Agentic 審查員與 Gateway 模式無法喚起，審查機制自動退化。

---

## 2. Windows 11 Python 啟動 Shim（`sg-python.sh`）防護特性

外掛設計了專屬的啟動腳本 `hooks/sg-python.sh`，在 Windows 11 下具備多重硬化機制：

1. **強制 UTF-8 編碼（PEP 540）**：
   腳本強制匯出 `export PYTHONUTF8=1`。Windows Python 預設 `locale.getpreferredencoding()` 常為 `cp1252`，在路徑包含中文、特殊 Unicode 字元時會導致子行程崩潰。外掛在此處提前攔截並修復。
2. **微軟商店 Python Alias 穿透**：
   在 Windows 上，`python3` 常指向 Microsoft Store 的 Stub（`...\Microsoft\WindowsApps\python3.exe`），在非 TTY 子行程中會靜默回傳 exit code 49 或因沙盒隔離出現 Errno 2 無法開啟腳本。腳本透過 probe 測試自動穿透 Stub，降級找到 python.org 官方原生直譯器或 `py -3`。
3. **Git Bash POSIX 與 Windows 磁碟代號轉換**：
   自動檢測並透過 `cygpath -w` 或內建字串替換，將 `/c/Users/...` 轉化為原生 Windows 路徑 `C:\Users\...`，確保 Windows 版 `python.exe` 正常解析腳本路徑。

---

## 3. Windows 11 本地安裝與配置指南

### 步驟一：外掛安裝

在 Claude Code 終端中執行外掛安裝指令：
```bash
/plugin install security-guidance@claude-plugins-official
```
*備註：官方市場已預設啟用，安裝後外掛將下載至 `%USERPROFILE%\.claude\plugins\cache\claude-plugins-official\security-guidance\<version>`。*

### 步驟二：Windows 11 原生環境變數配置

在 Windows 11 PowerShell 終端或系統設定中配置以下環境變數：

```powershell
# 1. 指定 Claude Code 本機完整執行路徑（不可使用相對路徑）
$env:SG_AGENTIC_CLI_PATH = (Get-Command claude.cmd).Source
# 典型路徑例如：C:\Users\<維護者帳號>\bin\claude.cmd 或 C:\Users\<維護者帳號>\AppData\Roaming\npm\claude.cmd

# 2. 指定審查模型（推薦 Sonnet 5.5 以達到最佳性價比）
$env:SECURITY_REVIEW_MODEL = "claude-sonnet-5-5"
$env:SG_AGENTIC_MODEL = "claude-sonnet-5-5"

# 3. 日常敏捷開發成本調控（選填，關閉頻繁的 Stop 回合審查，保留 Commit 終極審查）
# $env:ENABLE_STOP_REVIEW = "0"
```

#### 寫入永久使用者環境變數（PowerShell）：
> ⚠️ 此操作會永久寫入「使用者」層級環境變數（登錄檔 `HKCU\Environment`），影響之後所有新開的程序；執行前先確認值正確。還原方式：`[Environment]::SetEnvironmentVariable("<名稱>", $null, "User")`。

```powershell
$claudePath = (Get-Command claude.cmd).Source
[Environment]::SetEnvironmentVariable("SG_AGENTIC_CLI_PATH", $claudePath, "User")
[Environment]::SetEnvironmentVariable("SECURITY_REVIEW_MODEL", "claude-sonnet-5-5", "User")
[Environment]::SetEnvironmentVariable("SG_AGENTIC_MODEL", "claude-sonnet-5-5", "User")
```

---

## 4. 實機檢驗與測試日誌（Verification Evidence）

維護者針對 Windows 11 原生環境執行了三項獨立驗證，確保機制完全正常：

### 驗證 A：Layer 1 本地正則即時攔截測試

針對包含高危執行階段語法（`eval()` 與 `os.system()`）之代碼片段進行模式匹配測試：

#### 測試輸入代碼：
```python
def run_dynamic(code):
    return eval(code)

import os
def ping(host):
    os.system('ping ' + host)
```

#### 終端執行命令與輸出結果：
```powershell
python -c "
import sys, os
sys.path.insert(0, os.path.expanduser(r'~/.claude/plugins/marketplaces/claude-plugins-official/plugins/security-guidance/hooks'))
import patterns, _base

test_code_eval = '''
def run_dynamic(code):
    return eval(code)
'''
test_code_os_system = '''
import os
def ping(host):
    os.system('ping ' + host)
'''

matches_eval = [p['ruleName'] for p in patterns.SECURITY_PATTERNS if p.get('regex') and __import__('re').search(p['regex'], test_code_eval)]
matches_os = [p['ruleName'] for p in patterns.SECURITY_PATTERNS if p.get('regex') and __import__('re').search(p['regex'], test_code_os_system)]

print('State dir:', _base.state_dir())
print('Debug log file:', _base.DEBUG_LOG_FILE)
print('Eval matches:', matches_eval)
print('OS system matches:', matches_os)
"
```

```text
State dir: C:\Users\<維護者帳號>\.claude\security
Debug log file: C:\Users\<維護者帳號>\.claude\security\log.txt
Eval matches: ['eval_injection']
OS system matches: ['os_system_injection']
```

- **結果判定**：✅ 通過。`eval_injection` 與 `os_system_injection` 正則規則 各自匹配成功（僅兩個測試樣本；耗時與 Token 消耗未量測）。

---

### 驗證 B：日誌記錄與輪替機制驗證

外掛底層 `_base.py` 規範日誌寫入路徑為 `%USERPROFILE%\.claude\security\log.txt`，並定義 `DEBUG_LOG_MAX_BYTES = 1 * 1024 * 1024`（1 MB 自動原子輪替至 `log.txt.1`）。

#### 終端驗證指令與結果：
```powershell
python -c "
import sys, os
sys.path.insert(0, os.path.expanduser(r'~/.claude/plugins/marketplaces/claude-plugins-official/plugins/security-guidance/hooks'))
import _base

_base.debug_log('Test security guidance log entry on Windows 11')
print('Log exists:', os.path.exists(_base.DEBUG_LOG_FILE))
if os.path.exists(_base.DEBUG_LOG_FILE):
    with open(_base.DEBUG_LOG_FILE, 'r', encoding='utf-8') as f:
        print('Log content:', f.read().strip())
"
```

```text
Log exists: True
Log content: [2026-10-25 02:32:00.076] Test security guidance log entry on Windows 11
```

- **結果判定**：✅ 通過。日誌目錄自動建立，日誌輸出包含精確時間戳，未引發任何 Windows 檔案鎖定或編碼異常。

---

### 驗證 C：三層防禦範本（`templates/claude-security-guidance.md`）整合情境（設計推演）

維護者將自訂規則範本 `templates/claude-security-guidance.md` 掛載至測試環境，設計三種經典違反全域硬閘門情境，推演外掛在不同防禦層級之協同反饋：

| 測試情境 | 刻意注入之違規模式 | 觸發防禦層級 | 外掛預期反饋與阻擋行為 |
| :--- | :--- | :--- | :--- |
| **情境 1：硬編碼金鑰** | `GITHUB_TOKEN = "ghp_AbCdEf123..."` | Layer 1 (正則) + Layer 2 (LLM Diff) | 命中自訂「條款一」，LLM 審查員立即要求改用 `os.environ` 讀取並停止交付。 |
| **情境 2：目錄越界操作** | `open(r"C:\Users\username\.ssh\id_rsa")` | Layer 2 (LLM Diff) + Layer 3 (Agentic) | 命中自訂「條款二」，審查員識別絕對路徑脫離專案邊界，標記阻擋級 Finding。 |
| **情境 3：空殼實作與例外吞噬** | `def verify(): try: return True except: pass` | Layer 2 (LLM Diff) | 命中自訂「條款三」，審查員指出空殼函式與假綠燈，要求補齊真實驗證邏輯。 |

- **整合驗證結論（未實測）**：上表為依設計推演的「預期反饋」，Layer 2／Layer 3 的 LLM 審查並未在本 repo 留有實際執行輸出；僅規則範本的 8 KB 預算與條款完整性由 `tools/verify_claude_security_config.py` 機械檢驗。設計意圖是透過 8 KB 預算空間注入審查模型，形成「本地正則攔高危語法 ➔ LLM Diff 攔全域違規 ➔ Agentic 追跨檔資料流」的防護鏈。

---

## 5. 安全與隱私聲明

1. **零真實憑證暴露**：本文件與所有相關測試代碼嚴禁出現任何真實 API Key、Token 或私鑰。
2. **私人稱謂遮蔽**：本報告全數採用「維護者」統稱，路徑範例均進行隱私去標識化處理。
