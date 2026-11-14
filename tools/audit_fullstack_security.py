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
import os
import re
import sys
import tomllib
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
    (re.compile(r"rk" + r"_live_[0-9a-zA-Z]{20,}"), "Stripe Live Restricted Key"),
    (re.compile(r"whsec" + r"_[0-9a-zA-Z]{20,}"), "Stripe Webhook Signing Secret"),
    (re.compile(r"(?<![0-9A-Za-z])sk-ant-[0-9A-Za-z_-]{20,}"), "Anthropic API Key"),
    (re.compile(r"(?<![0-9A-Za-z])sk-[0-9A-Za-z_-]{20,}"), "OpenAI-style Secret Key"),
    (re.compile(r"xox[abp]-[0-9A-Za-z-]{10,}"), "Slack Token"),
    (re.compile(r"ya29\.[0-9A-Za-z_.-]{10,}"), "Google OAuth Access Token"),
]

# 僅用於 Wrangler 設定值（.env.example 常見範本 URL，不套用）
EMBEDDED_CREDENTIAL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@")

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

    # utf-8-sig：Windows 編輯器常在檔頭加 BOM，git 會略過它；不略過的話第一行 ".env" 會變成 "\ufeff.env"
    content = gitignore_path.read_text(encoding="utf-8-sig", errors="ignore")
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

    required_patterns = [".env", ".env.local"]
    # 與 git 一樣以「最後一條符合的規則」為準：萬用字元比對，"!" 否定規則把檔案放回未忽略。
    # 舊版用子字串判斷，會讓 ".env.example" 被誤當成已忽略 ".env"；
    # 之後又把否定規則整條略過，".env*" 後面接 "!.env.local" 時仍判定為已忽略。
    rules: list[tuple[bool, str]] = []
    for line in lines:
        negated = line.startswith("!")
        glob = (line[1:] if negated else line).lstrip("/")
        if glob.startswith("**/"):
            glob = glob[3:]
        rules.append((negated, glob.rstrip("/")))

    for pattern in required_patterns:
        ignored = False
        for negated, glob in rules:
            if fnmatch.fnmatchcase(pattern, glob):
                ignored = not negated
        if not ignored:
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


def _jsonc_to_json(raw: str) -> str:
    """移除字串外的 //、/* */ 註解與尾端逗號；字串與跳脫原樣保留。"""
    tokens = re.compile(r'"(?:[^"\\]|\\.)*"|//[^\r\n]*|/\*.*?\*/', re.DOTALL)
    raw = tokens.sub(lambda m: m.group() if m.group().startswith('"') else ' ', raw)
    # 用 token 避免誤改字串內的逗號與括號。
    tokens = re.compile(r'"(?:[^"\\]|\\.)*"|,(\s*[}\]])', re.DOTALL)
    return tokens.sub(lambda m: m.group() if m.group().startswith('"') else m.group(1), raw)


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(value):
    raise ValueError("nonstandard JSON constant")


def check_wrangler_config(root: Path) -> list[str]:
    """檢查 Cloudflare Wrangler (wrangler.toml / wrangler.json / wrangler.jsonc) 與 .dev.vars 安全規範"""
    issues: list[str] = []
    if not root.is_dir():
        return ["Wrangler 掃描路徑不存在或不是目錄"]

    # 遞迴找出所有 wrangler.toml/json/jsonc 與 .dev.vars*（略過 node_modules、.git）；
    # 走訪失敗一律視為未完成稽核。
    wrangler_files: list[Path] = []
    dev_var_dirs: dict[Path, set[str]] = {}
    walk_errors: list[str] = []

    def on_walk_error(error: OSError) -> None:
        walk_errors.append(f"Wrangler 掃描無法讀取目錄 '{error.filename}'，未完成稽核")

    for dirpath, dirnames, filenames in os.walk(root, onerror=on_walk_error):
        dirnames[:] = sorted(d for d in dirnames if d not in ("node_modules", ".git"))
        here = Path(dirpath)
        for name in sorted(filenames):
            if name in ("wrangler.toml", "wrangler.json", "wrangler.jsonc"):
                wrangler_files.append(here / name)
                dev_var_dirs.setdefault(here, set())
            elif name == ".dev.vars" or (name.startswith(".dev.vars.") and name != ".dev.vars.example"):
                dev_var_dirs.setdefault(here, set()).add(name)
    issues.extend(walk_errors)
    if not dev_var_dirs and not wrangler_files:
        return issues

    # 1. .dev.vars 與 .dev.vars.<env> 皆須被 .gitignore 忽略（"!" 否定規則以最後符合者為準）。
    #    每個含 wrangler 設定或 .dev.vars* 的目錄：以根目錄加該目錄的 .gitignore 判定；
    #    探針 ".dev.vars" 與 ".dev.vars.production" 代表 ".dev.vars" 及 ".dev.vars.*"，另加實際存在的檔名。
    def load_rules(gitignore: Path) -> list[tuple[bool, str]]:
        rules: list[tuple[bool, str]] = []
        text = gitignore.read_text(encoding="utf-8-sig", errors="ignore")
        for line in (ln.strip() for ln in text.splitlines()):
            if not line or line.startswith("#"):
                continue
            negated = line.startswith("!")
            glob = (line[1:] if negated else line).lstrip("/")
            if glob.startswith("**/"):
                glob = glob[3:]
            rules.append((negated, glob.rstrip("/")))
        return rules

    def is_ignored(name: str, rules: list[tuple[bool, str]]) -> bool:
        ignored = False
        for negated, glob in rules:
            if fnmatch.fnmatchcase(name, glob):
                ignored = not negated
        return ignored

    root_ignore = root / ".gitignore"
    for directory in sorted(dev_var_dirs):
        rel_dir = directory.relative_to(root).as_posix()
        label = "." if rel_dir == "." else rel_dir
        candidates = [g for g in {root_ignore, directory / ".gitignore"} if g.exists()]
        if not candidates:
            issues.append(f"Cloudflare Wrangler 專案（{label}）缺少 .gitignore，無法確認 .dev.vars 隔離")
            continue
        try:
            rules: list[tuple[bool, str]] = []
            for g in sorted(candidates, key=lambda x: len(x.parts)):
                rules.extend(load_rules(g))
        except OSError:
            issues.append(f"Cloudflare Wrangler 專案（{label}）之 .gitignore 無法讀取，未完成稽核")
            continue
        probes = {".dev.vars", ".dev.vars.production"} | dev_var_dirs[directory]
        missing = [probe for probe in sorted(probes) if not is_ignored(probe, rules)]
        if missing:
            issues.append(f"Cloudflare Wrangler 專案（{label}）之 .gitignore 未忽略本地機密檔 "
                          + "、".join(f"'{m}'" for m in missing))

    # 2. 掃描 wrangler.toml / wrangler.json(c) 是否在明文 vars 中存放敏感金鑰或真實 Token
    secret_key_name_re = re.compile(
        r"(?:TOKEN|KEY|SECRET|PASSWORD|CREDENTIAL)",
        re.IGNORECASE,
    )
    def check_values(value, location, sensitive_keys=False):
        if isinstance(value, dict):
            for key, child in value.items():
                if sensitive_keys and secret_key_name_re.search(key):
                    issues.append(f"Wrangler {location}.{key} 為敏感變數，所有值型別皆須移至 secrets")
                check_values(child, f"{location}.{key}", sensitive_keys)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_values(child, f"{location}[{index}]", sensitive_keys)
        elif isinstance(value, str):
            for pattern, desc in SUSPICIOUS_KEY_PATTERNS:
                if pattern.search(value):
                    issues.append(f"Wrangler {location} 疑似包含真實金鑰 ({desc})")
            if EMBEDDED_CREDENTIAL_RE.search(value):
                issues.append(f"Wrangler {location} 含 URL 內嵌帳密 (scheme://user:pass@host)")

    for wf in wrangler_files:
        rel_wf = wf.relative_to(root).as_posix()
        try:
            raw = wf.read_text(encoding="utf-8-sig")
            if wf.suffix == ".toml":
                data = tomllib.loads(raw)
            else:
                data = json.loads(_jsonc_to_json(raw) if wf.suffix == ".jsonc" else raw,
                                  object_pairs_hook=_unique_json_object,
                                  parse_constant=_reject_json_constant)
            if not isinstance(data, dict) or not data:
                raise ValueError("empty or invalid config")
            scopes = [("vars", data)]
            envs = data.get("env", {})
            if not isinstance(envs, dict):
                raise ValueError("env must be object")
            for name, env in envs.items():
                if not isinstance(env, dict):
                    raise ValueError("env entry must be object")
                scopes.append((f"env.{name}.vars", env))
            for location, scope in scopes:
                values = scope.get("vars", {})
                if not isinstance(values, dict):
                    raise ValueError("vars must be object")
                check_values(values, f"{rel_wf}:{location}", True)
            # 其餘欄位也掃描已知金鑰特徵，不將 vars 之外的設定視為安全藏匿處。
            check_values(data, str(rel_wf))
        except (OSError, ValueError, TypeError):
            issues.append(f"Wrangler 設定檔 '{rel_wf}' 無法讀取或解析、為空或 schema 不符，未完成稽核")

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
            "wrangler_config": check_wrangler_config(target),
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

    parser = argparse.ArgumentParser(description="全端靜態規則稽核：0=未命中，1=規則命中或輸入無效，2=CLI 用法錯誤")
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
        print("[PASS] 所選靜態規則未命中；不代表完整安全保證。")
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
