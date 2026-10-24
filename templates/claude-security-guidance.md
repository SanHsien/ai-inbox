# Claude Code security-guidance 自訂資安審查規範範本與三層防禦配置手冊

> 本範本收錄於 `templates/claude-security-guidance.md`，旨在將全域工程硬閘門（API Key 不進代碼、專案目錄外嚴禁讀寫刪改、禁止假資料與空殼函式）轉化為 Anthropic 官方 `security-guidance` 外掛可直接解析的自然語言審查條款，並提供 Windows 11 與跨平台環境下的 Token 成本控制與模型調度策略。

---

## 1. 範本使用說明與架構掛載機制

Anthropic 官方 `security-guidance@claude-plugins-official` 外掛在執行 Layer 2（回合結束 LLM Diff 語意審查）時，會依序讀取並串聯以下三個位置的自訂規則檔，注入審查 Prompt 中：

1. **使用者全域規則**：`~/.claude/claude-security-guidance.md`（所有專案共享）
2. **專案共用規則**：`<project>/.claude/claude-security-guidance.md`（推薦簽入 Git 倉庫）
3. **專案本地覆寫**：`<project>/.claude/claude-security-guidance.local.md`（推薦加入 `.gitignore`）

### 預算限制與裁剪順序（Prompt Budget）
- 官方外掛為自訂規則保留 **8 KB** 的 Prompt 預算。
- 若三個檔案串聯後的總大小超過 8 KB，系統將**從尾端裁剪**（保留順序為：全域規則 優先於 專案規則 優先於 本地覆寫）。因此請確保核心硬閘門寫於最前段。

### 行內豁免機制（Inline Justification）
若某些代碼看似危險但確屬業務必要（例如測試案例或受信任的內部字串），維護者只需在該行代碼附上行內註解：
```python
# safe: verified internal constant, no external input
result = eval(internal_expression)
```
審查模型讀取到 `safe:`、`nosec` 或明確豁免說明時，會將其識別為已知合規項目，避免無效阻擋。

---

## 2. 自訂資安審查條款（可直接複製至 `.claude/claude-security-guidance.md`）

以下區塊為標準 Markdown 規範內容，可直接儲存為 `.claude/claude-security-guidance.md`：

```markdown
# 專案資安與代碼真實性審查規範 (Security & Code Authenticity Policy)

你是一位嚴謹的軟體資安架構師與代碼審查員。請根據以下四項不可妥協的硬閘門，嚴格審查當前變更中的所有代碼與設定檔：

### 條款一：憑證與敏感資訊零暴露 (Zero Credentials & Secrets in Code)
- **違規模式**：
  - 嚴禁在代碼、指令列、註解、設定檔或測試案例中硬編碼任何 API Key、Token、私鑰、JWT Secret、資料庫密碼或雲端連線字串（包括 `sk-...`、`ghp_...`、`AKIA...` 等敏感憑證）。
- **修復要求**：
  - 所有機密資訊必須透過環境變數（如 Python `os.environ`、Node.js `process.env`）或專用密鑰管理工具讀取。
  - 若代碼中出現真實或長度特徵符合金鑰格式之字串，必須立即提出嚴重警告並阻止合流。

### 條款二：工作目錄與檔案邊界防禦 (Filesystem Boundary Protection)
- **違規模式**：
  - 嚴禁在專案根目錄外進行任何讀取、寫入、覆寫或刪除操作。
  - 嚴禁嘗試存取使用者家目錄下的敏感路徑（如 `~/.ssh`、`~/.aws`、`~/.gnupg`、瀏覽器資料庫、憑證快取等）。
  - 嚴禁使用未經驗證的路徑遍歷（如未淨化的 `../` 或無白名單限制的絕對路徑操作）。
- **修復要求**：
  - 所有檔案 I/O 操作必須解析為專案邊界內的正規化路徑（Canonical Path）。
  - 對於暫存或測試檔案，僅允許在專案內專用目錄（如 `.tmp/`、`scratch/`）或由系統提供的隔離沙盒中建立。

### 條款三：代碼真實性與禁止空殼實作 (No Hollow Stubs & Zero Fake Logic)
- **違規模式**：
  - 嚴禁以「回傳固定值」（如 `return 0`、`return ""`、`return true`、`return []`）的空殼函式作為功能完成的交付標準。
  - 嚴禁留下未實現的 `// TODO`、`# TODO: implement later` 或 `pass` 虛擬代碼。
  - 嚴禁透過吞掉例外（如 `except Exception: pass`、`catch (e) {}` 空區塊）或偽造假資料讓流程「表面過關」。
- **修復要求**：
  - 交付之功能模組必須具備完整業務邏輯、健全的邊界檢查與合適的錯誤傳播。
  - 測試案例必須驗證真實邏輯與斷言，不得註解掉失敗測試以粉飾紅燈。

### 條款四：高危執行階段函式與指令注入防範 (Command Injection & Unsafe Runtimes)
- **違規模式**：
  - 嚴禁在未經消毒的情況下使用 `eval()`、`exec()`、`Function()`、`os.system()`、`subprocess.run(..., shell=True)`、`child_process.exec()`。
  - 嚴禁不安全反序列化操作（如 `pickle.loads`、`yaml.load` 未指定 SafeLoader）。
- **修復要求**：
  - 呼叫系統指令必須使用參數清單（List of Arguments），禁用 Shell 字串拼接。
  - 資料序列化一律優先使用 `json`、`msgspec` 或 Pydantic 型別驗證器。
```

---

## 3. 三層防禦架構與 Token 成本控制策略

`security-guidance` 採取三層防護，不同層級的運算延遲與 Token 開銷截然不同：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       security-guidance 成本與防禦矩陣                       │
├─────────┬─────────────────────┬──────────────┬──────────────┬───────────────┤
│ 防禦層級 │ 觸發點               │ 運算機制     │ Token 消耗   │ 延遲 / 衝擊   │
├─────────┼─────────────────────┼──────────────┼──────────────┼───────────────┤
│ Layer 1 │ Edit / Write / Multi │ 本地 Regex   │ 0 Token      │ < 5 ms (無感) │
├─────────┼─────────────────────┼──────────────┼──────────────┼───────────────┤
│ Layer 2 │ Stop 回合結束        │ LLM Diff 審查│ 1K ~ 5K Token│ 1 ~ 3 秒      │
├─────────┼─────────────────────┼──────────────┼──────────────┼───────────────┤
│ Layer 3 │ git commit / push   │ Agentic 追蹤 │ 10K~50K Token│ 5 ~ 15 秒     │
└─────────┴─────────────────────┴──────────────┴──────────────┴───────────────┘
```

### 成本調度實踐指南

1. **審查模型優化（推薦 Sonnet 替代預設 Opus）**：
   - 官方預設採用最新 Opus 模型進行 Layer 2 與 Layer 3 審查。雖然理解力極高，但在密集修改場景下會快速累積 API 費用。
   - **優化配置**：
     ```bash
     # 指定 Layer 2 使用 Sonnet（具備極佳資安語意辨識能力，成本僅 Opus 的 1/5）
     SECURITY_REVIEW_MODEL=claude-sonnet-5-5
     # 指定 Layer 3 Agentic Reviewer 同步使用 Sonnet
     SG_AGENTIC_MODEL=claude-sonnet-5-5
     ```

2. **開發場景分級調度（Development Profiles）**：
   - **日常高頻編碼模式（Cost-Saver Profile）**：
     關閉每個回合的 Stop 審查，僅保留 Layer 1 本地正則與 Commit 前的終極審查：
     ```bash
     ENABLE_STOP_REVIEW=0
     SECURITY_REVIEW_MODEL=claude-sonnet-5-5
     ```
     - *優點*：日常對話流暢無延遲、零額外回合費用；只有在執行 `git commit` 時才觸發深度審查。
   - **發布與重構模式（Full Defense Profile）**：
     啟用完整三層防禦，並掛載本範本條款：
     ```bash
     ENABLE_PATTERN_RULES=1
     ENABLE_STOP_REVIEW=1
     ENABLE_COMMIT_REVIEW=1
     SECURITY_REVIEW_MODEL=claude-sonnet-5-5
     ```
   - **純離線/零成本模式（Offline / Zero-Token Profile）**：
     全面停用所有 LLM 審查，僅保留純本地毫秒級正則攔截：
     ```bash
     ENABLE_CODE_SECURITY_REVIEW=0
     ```

---

## 4. 典型對比案例（Bad vs. Good）

### 案例 1：敏感憑證暴露
- ❌ **違規代碼**：
  ```python
  GITHUB_TOKEN = "<HARDCODED_PAT_EXAMPLE_DO_NOT_COMMIT>"
  headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
  ```
- ✅ **合規模式**：
  ```python
  import os
  github_token = os.environ.get("GITHUB_TOKEN")
  if not github_token:
      raise RuntimeError("Missing GITHUB_TOKEN environment variable")
  headers = {"Authorization": f"Bearer {github_token}"}
  ```

### 案例 2：目錄越界操作
- ❌ **違規代碼**：
  ```python
  # 試圖讀取使用者全域配置
  with open(r"C:\Users\username\.ssh\id_rsa", "r") as f:
      key_data = f.read()
  ```
- ✅ **合規模式**：
  ```python
  # 僅操作專案邊界內的隔離路徑
  from pathlib import Path
  project_root = Path(__file__).resolve().parent.parent
  safe_target = (project_root / ".tmp" / "test_key.pub").resolve()
  if not safe_target.is_relative_to(project_root):
      raise PermissionError("Access outside project boundary denied")
  ```

### 案例 3：空殼實作與例外吞噬
- ❌ **違規代碼**：
  ```python
  def verify_signature(payload: bytes, signature: str) -> bool:
      # TODO: Implement real HMAC verification
      try:
          return True
      except Exception:
          pass
      return True
  ```
- ✅ **合規模式**：
  ```python
  import hmac
  import hashlib

  def verify_signature(payload: bytes, signature: str, secret: bytes) -> bool:
      if not payload or not signature or not secret:
          raise ValueError("Payload, signature, and secret must not be empty")
      expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
      return hmac.compare_digest(expected, signature)
  ```
