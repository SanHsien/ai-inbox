#!/usr/bin/env python3
"""Claude 資安審查與閒置壓縮設定之外部裁判機械驗證器 (verify_claude_security_config.py)

依據任務 T-20261025-01 與 docs/external-judge-audit.md 規範實作：
1. 驗證 docs/claude-idle-compaction-setup.md 中 CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS 門檻範圍 (>= 100000) 與 JSON 設定範例合法性。
2. 驗證 templates/claude-security-guidance.md 內自訂規則區塊之 byte 大小 (<= 8192 bytes / 8 KB 預算上限) 與四大硬閘門條款完整性。
3. 實作對抗式靜態掃描函式 scan_code_snippet(code: str)，檢測：
   (a) 硬編碼敏感憑證 (GitHub token, API key, PEM 私鑰等)
   (b) 越界路徑 (../, ~/.ssh, C:\\Users\\...\\id_rsa 等)
   (c) 空殼函式 (return True / return 0 / except Exception: pass 等假邏輯)
   (d) 高危呼叫 (eval(), os.system() 等注入點)
   支援行內或上一行 `# safe:` / `nosec` 豁免。
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# 門檻常數
MIN_IDLE_COMPACT_TOKENS = 100000
MAX_GUIDANCE_BUDGET_BYTES = 8192  # 8 KB Prompt 預算上限

# 四大硬閘門條款識別特徵 (條款編號, 名稱關鍵字)
MANDATORY_CLAUSES = [
    ("條款一", "憑證與敏感資訊零暴露"),
    ("條款二", "工作目錄與檔案邊界防禦"),
    ("條款三", "代碼真實性與禁止空殼實作"),
    ("條款四", "高危執行階段函式與指令注入防範"),
]

# 豁免正則 (行內或上一行)
EXEMPTION_PATTERN = re.compile(
    r"""(?i)(?:#|//|/\*)\s*(?:safe(?::|\b)|nosec\b)"""
)

# 靜態掃描正則規則庫
CREDENTIAL_PATTERNS = [
    (re.compile(r"""\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{16,}\b"""), "GitHub Personal Access Token"),
    (re.compile(r"""\bsk-(?:proj-)?[A-Za-z0-9_\-]{20,}\b"""), "OpenAI / Claude API Key"),
    (re.compile(r"""\bsk_(?:live|test)_[0-9a-zA-Z]{20,}\b"""), "Stripe / Service Secret Key"),
    (re.compile(r"""\bAKIA[0-9A-Z]{16}\b"""), "AWS Access Key ID"),
    (re.compile(r"""-----BEGIN (?:(?:RSA|EC|DSA|OPENSSH|PGP)\s+)?(?:PRIVATE\s+)?KEY-----"""), "Private Key PEM Block"),
    (
        re.compile(
            r"""(?i)\b(?:GITHUB_TOKEN|API_KEY|SECRET_KEY|ACCESS_TOKEN|PRIVATE_KEY)\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]"""
        ),
        "Hardcoded Secret Assignment",
    ),
]

PATH_TRAVERSAL_PATTERNS = [
    (re.compile(r"""(?:\.\./|\.\.\\)"""), "Relative Directory Traversal (../)"),
    (re.compile(r"""~[/\\]\.(?:ssh|aws|gnupg)\b"""), "User Secret Directory (~/.ssh, ~/.aws, etc.)"),
    (
        re.compile(r"""\bC:[/\\]Users[/\\][^/\\]+[/\\]\.(?:ssh|aws|gnupg)\b""", re.IGNORECASE),
        "Windows User Profile Secret Directory",
    ),
    (re.compile(r"""\bid_(?:rsa|ed25519|ecdsa|dsa)\b"""), "SSH Private Key File Access (id_rsa)"),
    (re.compile(r"""/(?:etc/passwd|etc/shadow)\b"""), "POSIX Sensitive System Path"),
    (
        re.compile(r"""\bC:[/\\]Windows[/\\]System32[/\\]config\b""", re.IGNORECASE),
        "Windows SAM/System Registry Path",
    ),
]

DANGEROUS_CALL_PATTERNS = [
    (re.compile(r"""\beval\s*\("""), "eval() dynamic execution"),
    (re.compile(r"""\bos\.system\s*\("""), "os.system() command execution"),
    (re.compile(r"""\bexec\s*\("""), "exec() dynamic execution"),
    (
        re.compile(r"""\bsubprocess\.(?:run|Popen|call|check_call|check_output)\s*\([^)]*shell\s*=\s*True"""),
        "subprocess shell=True execution",
    ),
    (re.compile(r"""\bpickle\.loads\s*\("""), "pickle.loads() unsafe deserialization"),
]

HOLLOW_STUB_PATTERNS = [
    (re.compile(r"""except(?:\s+Exception)?\s*:\s*pass\b"""), "Swallowed Exception (except Exception: pass)"),
    (re.compile(r"""catch\s*\([^)]*\)\s*\{\s*\}"""), "Empty Catch Block (catch (e) {})"),
    (re.compile(r"""^\s*return\s+(?:True|0)\s*(?:#.*)?$"""), "Hollow Return Constant (return True / return 0)"),
]


def verify_idle_compaction_doc(doc_path: Path | str) -> list[str]:
    """驗證 docs/claude-idle-compaction-setup.md 的 JSON 範例與數值門檻。"""
    path = Path(doc_path)
    issues: list[str] = []

    if not path.exists():
        return [f"閒置壓縮說明文件不存在: {path}"]

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"讀取文件失敗: {e}"]

    # 1. 驗證是否提及環境變數
    if "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS" not in content:
        issues.append("文件中未提及環境變數 'CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS'")

    # 2. 提取 markdown 中所有 json code block
    json_blocks = re.findall(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if not json_blocks:
        issues.append("文件中未包含任何 ```json 設定範例區塊")
        return issues

    valid_config_found = False
    for idx, block in enumerate(json_blocks, start=1):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as err:
            issues.append(f"第 {idx} 個 JSON 設定範例語法無效: {err}")
            continue

        # 檢驗 env 設定物件
        if isinstance(data, dict) and "env" in data and isinstance(data["env"], dict):
            env_vars = data["env"]
            if "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS" in env_vars:
                raw_val = env_vars["CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS"]
                try:
                    val = int(str(raw_val))
                except ValueError:
                    issues.append(
                        f"CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS 值 '{raw_val}' 無法解析為整數"
                    )
                    continue

                if val < MIN_IDLE_COMPACT_TOKENS:
                    issues.append(
                        f"CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS 門檻值 {val} 低於最低限制 {MIN_IDLE_COMPACT_TOKENS}"
                    )
                else:
                    valid_config_found = True

    if not valid_config_found and not any("CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS" in iss for iss in issues):
        issues.append("未在 JSON 範例中找到包含 CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS 的合規設定")

    return issues


def extract_guidance_rules(template_path: Path | str) -> str:
    """自 templates/claude-security-guidance.md 中提取自訂規則區塊。"""
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"範本檔案不存在: {path}")

    content = path.read_text(encoding="utf-8")
    # 提取第二節中的 ```markdown ... ``` 區塊
    match = re.search(r"```markdown\s*\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise ValueError("未在範本中找到 ```markdown 自訂規則區塊")
    return match.group(1).strip()


def verify_security_guidance_template(template_path: Path | str) -> list[str]:
    """驗證 templates/claude-security-guidance.md 的規則大小預算與四大條款完整性。"""
    path = Path(template_path)
    issues: list[str] = []

    if not path.exists():
        return [f"資安規範範本不存在: {path}"]

    try:
        rules_text = extract_guidance_rules(path)
    except Exception as e:
        return [f"提取自訂規則區塊失敗: {e}"]

    # 1. 驗證 byte 預算上限 (<= 8192 bytes)
    rule_bytes = len(rules_text.encode("utf-8"))
    if rule_bytes > MAX_GUIDANCE_BUDGET_BYTES:
        issues.append(
            f"自訂規則區塊大小為 {rule_bytes} bytes，超過 8 KB ({MAX_GUIDANCE_BUDGET_BYTES} bytes) 預算上限"
        )

    # 2. 驗證四大硬閘門條款完整性
    for clause_id, clause_desc in MANDATORY_CLAUSES:
        if clause_id not in rules_text:
            issues.append(f"自訂規則區塊缺少重要硬閘門：{clause_id} ({clause_desc})")
        elif clause_desc not in rules_text and not any(k in rules_text for k in clause_desc.split("與")):
            issues.append(f"自訂規則區塊中 {clause_id} 描述不完整，缺少主題關鍵字 '{clause_desc}'")

    return issues


def _is_exempted(lines: list[str], line_idx: int) -> bool:
    """判斷某一行或其上一行是否帶有 `# safe:` 或 `nosec` 豁免標記。"""
    # 1. 檢查當前行行內註解
    if EXEMPTION_PATTERN.search(lines[line_idx]):
        return True

    # 2. 往前尋找最近的一個非空白行（即上一行）
    prev_idx = line_idx - 1
    while prev_idx >= 0 and not lines[prev_idx].strip():
        prev_idx -= 1

    if prev_idx >= 0 and EXEMPTION_PATTERN.search(lines[prev_idx]):
        return True

    return False


def scan_code_snippet(code: str, include_exempted: bool = False) -> list[dict[str, Any]]:
    """對抗式靜態掃描函式。

    檢測：
    (a) 硬編碼敏感憑證
    (b) 越界路徑
    (c) 空殼函式 (AST + 正則模式)
    (d) 高危呼叫

    支援行內或上一行 `# safe:` / `nosec` 豁免。
    """
    findings: list[dict[str, Any]] = []
    lines = code.splitlines()

    # 1. AST 深度結構分析（若可被解析為有效 Python 代碼）
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 過濾 docstring
                stmts = [
                    s
                    for s in node.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
                ]
                line_no = node.lineno
                line_idx = line_no - 1 if 0 <= line_no - 1 < len(lines) else 0

                is_hollow = False
                reason = ""

                if len(stmts) == 0:
                    is_hollow = True
                    reason = f"空殼函式 '{node.name}' (僅包含 docstring)"
                elif len(stmts) == 1:
                    stmt = stmts[0]
                    if isinstance(stmt, ast.Pass):
                        is_hollow = True
                        reason = f"空殼函式 '{node.name}' (僅包含 pass)"
                    elif isinstance(stmt, ast.Return):
                        if isinstance(stmt.value, ast.Constant) and stmt.value.value in (True, 0, "", False, None):
                            is_hollow = True
                            reason = f"空殼函式 '{node.name}' (回傳固定常數 {stmt.value.value!r})"
                        elif isinstance(stmt.value, (ast.List, ast.Dict, ast.Set)) and not getattr(stmt.value, "elts", getattr(stmt.value, "keys", [])):
                            is_hollow = True
                            reason = f"空殼函式 '{node.name}' (回傳空集合)"

                if is_hollow:
                    exempt = _is_exempted(lines, line_idx)
                    findings.append({
                        "category": "hollow_stub",
                        "line_number": line_no,
                        "line_content": lines[line_idx].strip() if line_idx < len(lines) else "",
                        "message": reason,
                        "exempted": exempt,
                    })

            elif isinstance(node, ast.Try):
                for handler in node.handlers:
                    h_stmts = [
                        s
                        for s in handler.body
                        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
                    ]
                    if len(h_stmts) == 1 and isinstance(h_stmts[0], ast.Pass):
                        line_no = handler.lineno
                        line_idx = line_no - 1 if 0 <= line_no - 1 < len(lines) else 0
                        exempt = _is_exempted(lines, line_idx)
                        findings.append({
                            "category": "hollow_stub",
                            "line_number": line_no,
                            "line_content": lines[line_idx].strip() if line_idx < len(lines) else "",
                            "message": "吞掉例外區塊 (except Exception: pass)",
                            "exempted": exempt,
                        })
    except SyntaxError:
        # 非完整 Python 腳本或單行片段，依賴正則掃描 fallback
        pass

    # 2. 逐行正則模式掃描
    for idx, line in enumerate(lines):
        line_no = idx + 1
        trimmed = line.strip()
        if not trimmed:
            continue

        exempt = _is_exempted(lines, idx)

        # (a) 憑證檢測
        for pattern, desc in CREDENTIAL_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "category": "credential",
                    "line_number": line_no,
                    "line_content": trimmed,
                    "message": f"檢測到疑似敏感憑證或金鑰暴露: {desc}",
                    "exempted": exempt,
                })

        # (b) 越界路徑
        for pattern, desc in PATH_TRAVERSAL_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "category": "path_traversal",
                    "line_number": line_no,
                    "line_content": trimmed,
                    "message": f"檢測到越界或敏感檔案系統路徑: {desc}",
                    "exempted": exempt,
                })

        # (c) 空殼函式 / 吞掉例外正則
        is_multi_line_except_pass = False
        prev_idx = idx - 1
        while prev_idx >= 0 and not lines[prev_idx].strip():
            prev_idx -= 1
        if trimmed == "pass" and prev_idx >= 0 and re.search(r"""except(?:\s+\w+)?\s*:""", lines[prev_idx]):
            is_multi_line_except_pass = True

        if is_multi_line_except_pass and not any(f["line_number"] in (line_no, prev_idx + 1) and f["category"] == "hollow_stub" for f in findings):
            findings.append({
                "category": "hollow_stub",
                "line_number": line_no,
                "line_content": trimmed,
                "message": "檢測到空殼實作或吞掉例外模式: 多行 except: pass",
                "exempted": exempt,
            })

        for pattern, desc in HOLLOW_STUB_PATTERNS:
            if pattern.search(line):
                # 避免與 AST 報告重複
                if not any(f["line_number"] == line_no and f["category"] == "hollow_stub" for f in findings):
                    findings.append({
                        "category": "hollow_stub",
                        "line_number": line_no,
                        "line_content": trimmed,
                        "message": f"檢測到空殼實作或吞掉例外模式: {desc}",
                        "exempted": exempt,
                    })

        # (d) 高危呼叫
        for pattern, desc in DANGEROUS_CALL_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "category": "dangerous_call",
                    "line_number": line_no,
                    "line_content": trimmed,
                    "message": f"檢測到高危執行階段函式呼叫: {desc}",
                    "exempted": exempt,
                })

    if include_exempted:
        return findings
    return [f for f in findings if not f["exempted"]]


def verify_all_configs(base_dir: Path | str) -> dict[str, Any]:
    """執行全量資安與閒置壓縮設定檔檢驗。"""
    root = Path(base_dir).resolve()
    idle_doc = root / "docs" / "claude-idle-compaction-setup.md"
    guidance_tpl = root / "templates" / "claude-security-guidance.md"

    idle_issues = verify_idle_compaction_doc(idle_doc)
    guidance_issues = verify_security_guidance_template(guidance_tpl)

    all_passed = (len(idle_issues) == 0 and len(guidance_issues) == 0)

    return {
        "base_dir": str(root),
        "all_passed": all_passed,
        "idle_compaction": {
            "path": str(idle_doc),
            "passed": len(idle_issues) == 0,
            "issues": idle_issues,
        },
        "security_guidance": {
            "path": str(guidance_tpl),
            "passed": len(guidance_issues) == 0,
            "issues": guidance_issues,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude 資安審查與閒置壓縮設定之外部裁判機械驗證器"
    )
    parser.add_argument(
        "--target-dir",
        default=".",
        help="專案根目錄路徑 (預設為當前目錄)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式輸出結果",
    )
    args = parser.parse_args()

    results = verify_all_configs(args.target_dir)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0 if results["all_passed"] else 1

    print("=" * 70)
    print("Claude 資安審查與閒置壓縮設定外部裁判檢驗報告")
    print("=" * 70)
    print(f"目標目錄: {results['base_dir']}\n")

    # 1. 閒置壓縮設定檢驗
    idle_res = results["idle_compaction"]
    if idle_res["passed"]:
        print("[PASS] docs/claude-idle-compaction-setup.md 檢驗通過")
        print("       - CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS >= 100000 門檻合法")
        print("       - JSON 設定範例結構合法")
    else:
        print("[FAIL] docs/claude-idle-compaction-setup.md 檢驗失敗:")
        for iss in idle_res["issues"]:
            print(f"       * {iss}")

    print()

    # 2. 資安審查範本檢驗
    guidance_res = results["security_guidance"]
    if guidance_res["passed"]:
        print("[PASS] templates/claude-security-guidance.md 檢驗通過")
        print("       - 自訂規則區塊 byte 大小 <= 8192 bytes (8 KB 預算上限)")
        print("       - 四大硬閘門條款完整齊全")
    else:
        print("[FAIL] templates/claude-security-guidance.md 檢驗失敗:")
        for iss in guidance_res["issues"]:
            print(f"       * {iss}")

    print("-" * 70)
    if results["all_passed"]:
        print("[SUCCESS] 全數外部裁判機械檢驗通過 (All checks passed)！")
        return 0
    else:
        print("[FAILURE] 檢驗未通過，請修正上述問題。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
