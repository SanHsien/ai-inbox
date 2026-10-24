#!/usr/bin/env python3
"""全端商業網站上線前資安與架構自檢工具 (audit_fullstack_security.py)

依據 HanSun 全端建置架構規範進行四大硬性資安稽核：
1. .gitignore 是否忽略 .env / .env.local 等敏感檔案
2. .env.example 是否洩漏真實金鑰特徵
3. Client Components ("use client") 是否誤引後端專用密鑰
4. SQL Migration 檔案中新建的資料表是否皆啟用 RLS (Row Level Security)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# 後端專用敏感關鍵字（嚴禁出現在 Client 端代碼中）
SERVER_ONLY_SECRETS = [
    "SUPABASE_SERVICE_ROLE_KEY",
    "STRIPE_SECRET_KEY",
    "LINE_PAY_SECRET",
    "RESEND_API_KEY",
    "DATABASE_URL",
    "JWT_SECRET",
]

# 真實金鑰特徵（嚴禁出現在 .env.example 或提交至版控）
SUSPICIOUS_KEY_PATTERNS = [
    (re.compile(r"sk" + r"_live_[0-9a-zA-Z]{20,}"), "Stripe Live Secret Key"),
    (re.compile(r"sbp_[0-9a-fA-F]{20,}"), "Supabase Service Role Key"),
    (re.compile(r"ghp_[0-9a-zA-Z]{20,}"), "GitHub Personal Access Token"),
    (re.compile(r"-----BEGIN (RSA|EC|PRIVATE) KEY-----"), "Private Key PEM block"),
]


def check_gitignore(root: Path) -> list[str]:
    """檢查 .gitignore 是否忽略敏感環境變數檔案"""
    issues = []
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        issues.append("找不到 .gitignore 檔案")
        return issues

    content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

    required_patterns = [".env", ".env.local"]
    for pattern in required_patterns:
        # 簡單判定 pattern 是否出現在 gitignore 中
        if not any(pattern == line or pattern in line for line in lines):
            issues.append(f".gitignore 未明確包含 '{pattern}' 忽略規則")

    return issues


def check_env_example(root: Path) -> list[str]:
    """檢查 .env.example 是否含有真實敏感金鑰值"""
    issues = []
    example_path = root / ".env.example"
    if not example_path.exists():
        return issues

    content = example_path.read_text(encoding="utf-8", errors="ignore")
    for lineno, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        for pattern, desc in SUSPICIOUS_KEY_PATTERNS:
            if pattern.search(line):
                issues.append(f".env.example 第 {lineno} 行疑似包含真實金鑰 ({desc})")

    return issues


def check_client_components(root: Path) -> list[str]:
    """檢查 Client Components 中是否洩漏後端專用密鑰字串"""
    issues = []
    extensions = {".js", ".jsx", ".ts", ".tsx"}

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in extensions:
            continue
        # 略過 node_modules, .next, .git
        parts = path.parts
        if any(p in ("node_modules", ".next", ".git", "dist", "build") for p in parts):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 判定是否為 Client Component
        is_client = '"use client"' in content or "'use client'" in content
        if not is_client:
            continue

        for secret in SERVER_ONLY_SECRETS:
            if secret in content:
                rel_path = path.relative_to(root)
                issues.append(f"Client Component '{rel_path}' 引用了後端專用敏感金鑰 '{secret}'")

    return issues


def check_sql_rls(root: Path) -> list[str]:
    """檢查 SQL Migration 檔案中建立的表格是否都啟用 RLS"""
    issues = []
    create_table_re = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?([a-zA-Z0-9_]+)", re.IGNORECASE)
    enable_rls_re = re.compile(r"ALTER\s+TABLE\s+(?:public\.)?([a-zA-Z0-9_]+)\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY", re.IGNORECASE)

    for path in root.rglob("*.sql"):
        parts = path.parts
        if any(p in ("node_modules", ".git") for p in parts):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        created_tables = set(create_table_re.findall(content))
        enabled_tables = set(enable_rls_re.findall(content))

        for table in created_tables:
            if table not in enabled_tables:
                rel_path = path.relative_to(root)
                issues.append(f"SQL 遷移檔 '{rel_path}' 建立了資料表 '{table}'，但未在同一檔案中啟用 RLS (ENABLE ROW LEVEL SECURITY)")

    return issues


def audit_fullstack_security(target_dir: Path) -> dict[str, Any]:
    """執行完整安全稽核並回傳結果"""
    target = target_dir.resolve()
    results = {
        "target": str(target),
        "passed": True,
        "checks": {
            "gitignore": check_gitignore(target),
            "env_example": check_env_example(target),
            "client_components": check_client_components(target),
            "sql_rls": check_sql_rls(target),
        },
        "total_issues": 0,
    }

    total = sum(len(issues) for issues in results["checks"].values())
    results["total_issues"] = total
    results["passed"] = (total == 0)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="全端商業網站上線前資安自檢稽核工具")
    parser.add_argument("--target", default=".", help="待稽核專案根目錄路徑 (預設為當前目錄)")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"錯誤：目錄不存在 '{target_path}'", file=sys.stderr)
        return 1

    report = audit_fullstack_security(target_path)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["passed"] else 1

    print(f"[*] 開始執行全端網站資安上線前稽核：{report['target']}")
    if report["passed"]:
        print("[PASS] 全端資安稽核 100% 通過，無發現安全違規項目！")
        return 0

    print(f"[FAIL] 稽核失敗，發現 {report['total_issues']} 項資安風險：")
    for category, issues in report["checks"].items():
        if issues:
            print(f"\n- 類別 [{category}]：")
            for issue in issues:
                print(f"  * {issue}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
