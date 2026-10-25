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
import fnmatch
import json
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
    # RSA / EC / OPENSSH / ENCRYPTED / 無前綴的 PEM 私鑰區塊
    (re.compile(r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----"), "Private Key PEM block"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS Access Key ID"),
    (re.compile(r"github_pat_[0-9a-zA-Z_]{20,}"), "GitHub Fine-grained Token"),
]

# 掃描時略過的目錄（只比對「相對於稽核根目錄」的路徑片段，
# 避免專案本身位於 /home/x/build/app 之類路徑時整個專案被誤略過）
SKIP_DIRS = ("node_modules", ".next", ".git", "dist", "build")
CLIENT_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}


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
    # 否定規則（!.env.example）不算忽略；其餘以 gitignore 萬用字元比對。
    # 舊版用子字串判斷，會讓 ".env.example" 被誤當成已忽略 ".env"。
    ignore_globs = []
    for line in lines:
        if line.startswith("!"):
            continue
        glob = line.lstrip("/")
        if glob.startswith("**/"):
            glob = glob[3:]
        ignore_globs.append(glob.rstrip("/"))

    for pattern in required_patterns:
        if not any(fnmatch.fnmatchcase(pattern, glob) for glob in ignore_globs):
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

    for path in root.rglob("*"):
        if path.suffix.lower() not in CLIENT_EXTENSIONS or not path.is_file():
            continue
        if any(p in SKIP_DIRS for p in path.relative_to(root).parts):
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
    # 支援 IF NOT EXISTS、schema 前綴與雙引號識別字（"public"."Users"）
    ident = r'"?([A-Za-z0-9_]+)"?'
    schema = r'(?:"?[A-Za-z0-9_]+"?\s*\.\s*)?'
    create_table_re = re.compile(
        r"CREATE\s+(?:UNLOGGED\s+|TEMP(?:ORARY)?\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?" + schema + ident,
        re.IGNORECASE,
    )
    enable_rls_re = re.compile(
        r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?" + schema + ident + r"\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY",
        re.IGNORECASE,
    )
    block_comment_re = re.compile(r"/\*.*?\*/", re.DOTALL)
    line_comment_re = re.compile(r"--[^\n]*")

    for path in sorted(root.rglob("*.sql")):
        if any(p in ("node_modules", ".git") for p in path.relative_to(root).parts):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 註解掉的 CREATE TABLE 不算；未加引號的識別字在 PostgreSQL 不分大小寫
        content = line_comment_re.sub("", block_comment_re.sub("", content))
        created_tables = {t.lower() for t in create_table_re.findall(content)}
        enabled_tables = {t.lower() for t in enable_rls_re.findall(content)}

        for table in sorted(created_tables):
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
    # 要在解析參數之前設定：--help 由 argparse 直接印出，晚設就會用系統編碼（Windows cp950）輸出成亂碼
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

    parser = argparse.ArgumentParser(description="全端商業網站上線前資安自檢稽核工具")
    parser.add_argument("--target", default=".", help="待稽核專案根目錄路徑 (預設為當前目錄)")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.is_dir():
        print(f"錯誤：目錄不存在或不是資料夾 '{target_path}'", file=sys.stderr)
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
