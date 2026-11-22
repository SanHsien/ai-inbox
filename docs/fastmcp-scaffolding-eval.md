# PrefectHQ/fastmcp 本機 Python MCP Server 腳手架評估與安全邊界規範

> 本文件收錄於 `docs/fastmcp-scaffolding-eval.md`，為任務 `T-20261121-01` 之產出成果。
> 核心目的：唯讀評估開源框架 [`PrefectHQ/fastmcp`](https://github.com/PrefectHQ/fastmcp) 在 Windows 11 原生環境下（四大主力 Agent：Antigravity、Claude Code、Codex、Hermes）之 `stdio` 與 `SSE` / `Streamable HTTP` 傳輸通道相容性，並制定結合「Pydantic 嚴格參數驗證、路徑跨界防逃逸（Path Traversal & Symlink Guard）、顯式錯誤回報（禁止吞掉例外）」的本機 FastMCP 安全開發範本。

---

## 0. 來源筆記與交叉參照

- **來源筆記**：[`notes/2026-11-21-aiposthub-fastmcp-python-mcp-framework-eval.md`](../notes/2026-11-21-aiposthub-fastmcp-python-mcp-framework-eval.md)
- **交叉參照**：
  - [`notes/2026-10-17-github-open-source-ai-toolkit-matrix.md`](../notes/2026-10-17-github-open-source-ai-toolkit-matrix.md)（GitHub 開源 AI 工具庫矩陣與 FastMCP 相依生態）
  - [`notes/2026-10-19-rea-reverse-engineer-anything-agent.md`](../notes/2026-10-19-rea-reverse-engineer-anything-agent.md)（本機 MCP Server 封裝實務）
  - [`notes/2026-11-19-codex-claude-multi-agent-orchestration-landscape.md`](../notes/2026-11-19-codex-claude-multi-agent-orchestration-landscape.md)（多 CLI 協作與 MCP 工具鏈治理）
  - [`docs/gemini-tool-retrieval-and-mcp-spec.md`](./gemini-tool-retrieval-and-mcp-spec.md)（MCP 工具按需載入與 `defer_loading` 治理規範）

---

## 1. Windows 11 原生環境下之 FastMCP 架構與傳輸通道相容性評估

`PrefectHQ/fastmcp` 透過類似 FastAPI 的 Python 裝飾器（`@mcp.tool()`、`@mcp.resource()`、`@mcp.prompt()`）與 Pydantic 型別標註（Type Hints），將常規 Python 函式自動轉換為符合 Model Context Protocol（JSON-RPC 2.0）規範的 Tool Input Schema。

針對 **Windows 11 原生開發環境（非 WSL）**，將其兩種主要傳輸通道（`stdio` 與 `SSE` / `Streamable HTTP`）的相容性、常見踩坑與對策評估如下：

```text
[AI Agent 客戶端 (Antigravity / Claude Desktop / Claude Code / Codex)]
   │
   ├─► 通道 A：stdio (標準輸入/輸出管道，本機單一 Agent 首選)
   │     ├── 啟動方式：客戶端直接 spawn 子行程 (`python -u server.py` 或 `uv run fastmcp run`)
   │     └── Windows 11 關鍵防坑：
   │           1. 強制 UTF-8 編碼 (`PYTHONUTF8=1`)，防止預設 CP950 (Big5) 導致 JSON-RPC 解析崩潰
   │           2. 嚴禁在業務邏輯中使用 `print()` 輸出至 `stdout`（會污染 JSON-RPC 封包流，日誌一律導向 `stderr`）
   │           3. 子行程呼叫外部 CLI 時須帶 `CREATE_NO_WINDOW`，防止彈出閃爍的終端機視窗
   │
   └─► 通道 B：SSE / Streamable HTTP (本地 Loopback 常駐服務，多 Agent 共用或耗時預熱模型適用)
         ├── 啟動方式：綁定 `127.0.0.1:<port>` 獨立背景程序
         └── Windows 11 關鍵防坑：
               1. 嚴格限制綁定 `127.0.0.1`（禁止 `0.0.0.0` 暴露於區域網路）
               2. 若 Agent 執行於受限沙盒內，跨行程連線本地 Port 需顯式授權或走 `stdio`
```

### 1.1 `stdio` vs. `SSE / HTTP` 在 Windows 11 之選型對照表

| 評估維度 | `stdio`（標準輸入／輸出通道） | `SSE / Streamable HTTP`（本地網路端點） | Windows 11 本機實務建議 |
| :--- | :--- | :--- | :--- |
| **生命週期管理** | 由 Agent 客戶端按需啟動與回收，隨會話結束自動關閉 | 需自行管理背景 Daemon 啟動、Port 佔用與崩潰重啟 | **90% 本機工具優先選用 `stdio`**，免去常駐行程與殭屍程序清理負擔 |
| **Windows 編碼相容性** | 極易受 Windows 主控台預設 `cp950` 與 `\r\n` 換行影響 | 走 HTTP UTF-8 Header，不受主控台字碼頁影響 | `stdio` 伺服器開頭**必須強制重設 `sys.stdout` / `sys.stdin` 為 `utf-8`** |
| **Stdout 污染風險** | **極高**：任何第三方套件向 `stdout` 印出一行非 JSON 文字即中斷連線 | 無：標準輸出與 HTTP 回應流分離 | `stdio` 模式下，所有 `logging.StreamHandler` 必須明確指定 `stream=sys.stderr` |
| **攻擊面與存取控制** | 僅啟動該子行程的父 Agent 可讀寫管道，天然隔離 | 本機所有能連上 `localhost:<port>` 的程序（或瀏覽器惡意網頁 CSRF/SSRF）皆可能觸及 | 若必須使用 `SSE / HTTP`，**強制綁定 `127.0.0.1` 並驗證 `Origin` / Bearer Token** |

---

## 2. 本機 MCP Server 四大零信任安全邊界（繞過方式即規格）

雖然 FastMCP 讓「把一個 Python 函式變成 Agent 工具」只需一行 `@mcp.tool()`，但**開發門檻降低不等於安全邊界放寬**。設計本機 MCP 工具時，必須針對以下四種常見繞過與失效模式建立機械防線：

| 威脅與繞過場景 | 脆弱寫法（禁止採用） | 繞過方式（攻擊向量） | 強制硬化規格（Defense-in-Depth） |
| :--- | :--- | :--- | :--- |
| **1. 路徑穿越與符號連結逃逸（Path Traversal & Symlink Escape）** | 僅用 `path.startswith("C:\\GitHub")` 或字串替換 `".."` | 1. 傳入 `C:\GitHub-secrets\key.pem`（前綴碰撞）<br>2. 傳入 `C:\GitHub\repo\..\..\Users\<user>\.ssh\id_rsa`<br>3. 在工作區內建立指向家目錄的 Junction / Symlink | 使用 `Path(user_path).resolve(strict=False)` 解析真實絕對路徑，並以 **`resolved.is_relative_to(ALLOWED_ROOT.resolve())`** 驗證；同時拒絕指向白名單外的 Symlink / Junction。 |
| **2. 敏感檔案與機密讀取（Credential & Dotfile Harvesting）** | 只要在專案目錄內就允許讀取任意檔案 | Agent 被外部貼文 Prompt Injection 誘導讀取專案內的 `.env`、`.git/config`（含鑲嵌 Token）或私鑰檔 `*.pem` / `*.key` | 建立**雙重黑名單**：即使路徑位於 `C:\GitHub\<repo>` 內，仍硬性攔截 `.env*`、`*.pem`、`*.key`、`*credentials*` 與 `.git/config` 之內容讀取。 |
| **3. 殼層指令注入（Shell Command Injection）** | 將模型傳入的字串拼接到 `subprocess.run(f"git log {arg}", shell=True)` | 模型傳入 `main; powershell -c "..."` 或利用環境變數展開執行任意指令 | **全面禁用 `shell=True`**；一律傳遞參數陣列 `["git", "log", arg]`，並以 Pydantic `pattern` 或 `Literal` 嚴格限制允許的子指令與旗標（如禁止 `--upload-pack`、`-c`）。 |
| **4. 靜默吞掉例外（Silent Failure / Exception Swallowing）** | `except Exception: pass` 或回傳空字串 `""` / `[]` | 當權限檢查失敗、檔案編碼錯誤或工具壞掉時，Agent 以為「查詢結果為空（0 個問題）」而誤判安全放行 | **嚴禁吞掉例外或回傳假成功資料**；發生攔截或執行錯誤時，必須回傳結構化的明確錯誤訊息（含 `[BLOCKED]` 或 `[ERROR]` 前綴與原因），並在 `stderr` 留下完整稽核日誌。 |

---

## 3. FastMCP 安全開發標準範本（Windows 11 硬化版）

以下提供可直接作為本機自建 Python MCP Server 起點的標準範本，內建 **Windows UTF-8 與 `stderr` 日誌保護**、**Pydantic 嚴格欄位驗證**、**`is_relative_to` 路徑防逃逸檢查**與**顯式錯誤回報**：

```python
#!/usr/bin/env python3
"""
本機安全硬化版 FastMCP Server 範本 (Windows 11 Native)
用途：在嚴格鎖定 C:\\GitHub\\<repo> 白名單邊界的前提下，對 Agent 暴露唯讀檢視與受控分析工具。
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP

# 1. Windows 11 stdio 防坑：強制 stdin/stdout 為 UTF-8，並將所有日誌導向 stderr（嚴禁污染 stdout JSON-RPC 流）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("safe-local-mcp")

# Windows 子行程不彈出主控台視窗旗標
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# 2. 硬性定義允許存取的專案根目錄白名單與敏感檔名黑名單
ALLOWED_WORKSPACE_ROOT = Path(os.environ.get("MCP_WORKSPACE_ROOT", r"C:\GitHub\ai-inbox")).resolve()
FORBIDDEN_FILE_PATTERNS = {
    ".env", ".env.local", ".env.production",
    "id_rsa", "id_ed25519", ".npmrc", ".pypirc",
}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".pfx", ".p12", ".kdbx"}

mcp = FastMCP("safe-workspace-inspector")


def verify_safe_workspace_path(raw_path: str) -> Path:
    """驗證路徑是否嚴格位於白名單工作區內，且未觸及敏感憑證檔或外部 Symlink。"""
    if not raw_path or "\x00" in raw_path:
        raise ValueError("[BLOCKED] 路徑不可為空或包含空字元 (Null Byte)")

    candidate = (ALLOWED_WORKSPACE_ROOT / raw_path) if not Path(raw_path).is_absolute() else Path(raw_path)
    resolved = candidate.resolve(strict=False)

    # 防線 A：使用 Path.is_relative_to 防止前綴碰撞（如 C:\GitHub\ai-inbox-evil）與 .. 逃逸
    if not resolved.is_relative_to(ALLOWED_WORKSPACE_ROOT):
        logger.warning("攔截跨目錄存取嘗試: raw=%r -> resolved=%s", raw_path, resolved)
        raise PermissionError(
            f"[BLOCKED] 拒絕存取工作區白名單外的路徑：{resolved}（僅允許 {ALLOWED_WORKSPACE_ROOT}）"
        )

    # 防線 B：攔截敏感憑證檔、私鑰與 .git/config
    name_lower = resolved.name.lower()
    parts_lower = [p.lower() for p in resolved.relative_to(ALLOWED_WORKSPACE_ROOT).parts]
    if (
        name_lower in FORBIDDEN_FILE_PATTERNS
        or name_lower.startswith(".env.")
        or resolved.suffix.lower() in FORBIDDEN_SUFFIXES
        or (len(parts_lower) >= 2 and parts_lower[0] == ".git" and parts_lower[1] == "config")
    ):
        logger.warning("攔截敏感檔案存取嘗試: %s", resolved)
        raise PermissionError(f"[BLOCKED] 拒絕讀取敏感設定或憑證檔案：{resolved.name}")

    return resolved


class SafeReadRequest(BaseModel):
    """Pydantic 嚴格輸入模型：限制相對路徑格式與讀取行數上限。"""

    relative_path: Annotated[
        str,
        Field(description="相對於工作區根目錄的檔案路徑（例如 'docs/fastmcp-scaffolding-eval.md'）", min_length=1, max_length=260),
    ]
    max_lines: Annotated[
        int,
        Field(default=200, ge=1, le=1000, description="最大讀取行數（1~1000），防止單次傾印超大檔案塞爆 Context"),
    ]

    @field_validator("relative_path")
    @classmethod
    def reject_suspicious_prefixes(cls, v: str) -> str:
        cleaned = v.strip()
        if cleaned.startswith(("\\\\", "//")):
            raise ValueError("[BLOCKED] 禁止使用 UNC 網路路徑")
        return cleaned


@mcp.tool()
def read_workspace_file(req: SafeReadRequest) -> str:
    """安全讀取工作區內的純文字檔案（含路徑跨界攔截、敏感檔過濾與顯式錯誤回報）。"""
    try:
        target = verify_safe_workspace_path(req.relative_path)
        if not target.exists():
            return f"[ERROR] 檔案不存在：{req.relative_path}"
        if not target.is_file():
            return f"[ERROR] 目標不是一般檔案：{req.relative_path}"

        text = target.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        snippet = "\n".join(lines[: req.max_lines])
        truncated_notice = f"\n... (已截斷，共 {len(lines)} 行)" if len(lines) > req.max_lines else ""
        return snippet + truncated_notice
    except (PermissionError, ValueError) as sec_err:
        # 嚴禁吞掉例外：明確將攔截原因回傳給 Agent 並在 stderr 留存日誌
        logger.error("安全閘門攔截: %s", sec_err)
        return str(sec_err)
    except OSError as io_err:
        logger.error("I/O 讀取失敗 (%s): %s", req.relative_path, io_err)
        return f"[ERROR] 檔案讀取失敗：{io_err}"


if __name__ == "__main__":
    # 預設以 stdio 啟動，由 Agent 客戶端直接管理子行程生命週期
    mcp.run(transport="stdio")
```

---

## 4. 本機引入與驗收檢查清單（Onboarding Checklist）

在本機為四大 Agent 註冊任何基於 `FastMCP` 撰寫的自訂 MCP Server 前，必須逐項通過下列 5 點檢查：

1. **啟動設定顯式注入 `PYTHONUTF8=1` 與 `-u`（Unbuffered）**：
   - 在客戶端 MCP 設定檔（如 `mcp_config.json` 或 `claude_desktop_config.json`）中，啟動指令統一寫為 `python -u <path_to_server.py>`，並在 `env` 區塊加上 `"PYTHONUTF8": "1"`。
2. **零 `stdout` 雜訊驗證**：
   - 手動在 PowerShell 執行 `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python -u server.py`，確認 `stdout` 第一個字元即為合法的 `{` JSON 回應，無任何 Banner 或 print 雜訊。
3. **繞過測試（Bypass Test Suite）必跑**：
   - 針對所有接收路徑或字串的工具，必須以單元測試驗證：(1) `..\` 跳出工作區被擋；(2) 同名前綴兄弟目錄（如 `C:\GitHub\repo-other`）被擋；(3) `.env` 與 `.git/config` 被擋；(4) UNC 路徑 `\\server\share` 被擋。
4. **工具數量與 `defer_loading` 配對**：
   - 單一自建 MCP Server 暴露的工具數若超過 10 個，應按職責拆分或於支援 Tool Retrieval / Lazy Loading 的客戶端標記為按需載入（參見 [`docs/gemini-tool-retrieval-and-mcp-spec.md`](./gemini-tool-retrieval-and-mcp-spec.md)）。
5. **第三方 FastMCP Server 零信任審查**：
   - 若引用社群開源的 FastMCP 專案，嚴禁直接 `uvx` 或 `pip install` 執行；必須先下載原始碼並執行 `python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack <目錄>` 與人工審查其 `@mcp.tool()` 是否有任意檔案讀寫、無限制 `subprocess` 或外連遙測行為。
