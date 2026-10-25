#!/usr/bin/env python3
"""
tools/verify_incident_and_workflow_specs.py
資安事件盤點與 WebToApp 接案規格之「外部裁判」結構驗證器（純 Python stdlib）。

驗證目標：
1. docs/zeabur-incident-credential-audit.md：
   - 第一行符合 `^結論：(有使用|無使用) Zeabur`；
   - 包含倉庫掃描結果表格與 GitHub 授權稽核表格；
   - 全文零高危明文金鑰暴露（ghp_、sk-、AKIA 等）。
2. templates/platform-breach-response.md：
   - 包含「立即處置」「二次憑證」「稽核與帳單」「遷移評估」「預防」五大段落；
   - 每段各自有 >= 3 個 `- [ ]` 核取方塊項目。
3. docs/web-to-app-evaluation.md：
   - 包含明確「結論：可行／不可行」判定；
   - 包含 AndroidManifest.xml 權限宣告與 Keystore 簽名機制分析。
4. docs/web-to-app-freelance-workflow.md：
   - 包含六大標準接案步驟；
   - 包含四大風險防範與免責條款。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SECRET_PATTERNS = {
    "GitHub token": r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "Anthropic / OpenAI key": r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}",
    "Google API key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
}

ZEABUR_FIRST_LINE_RE = re.compile(r"^結論：(有使用|無使用) Zeabur")
WEB_TO_APP_CONCLUSION_RE = re.compile(r"^結論：(可行|不可行)", re.M)

REQUIRED_BREACH_SECTIONS = [
    "立即處置",
    "二次憑證",
    "稽核與帳單",
    "遷移評估",
    "預防",
]

REQUIRED_WORKFLOW_STEPS = [
    ("步驟一", "需求確認"),
    ("步驟二", "網站可用性"),
    ("步驟三", "封裝與打包"),
    ("步驟四", "金鑰簽名"),
    ("步驟五", "上架材料"),
    ("步驟六", "交付"),
]

REQUIRED_DISCLAIMERS = [
    ("第三方內容", "版權"),
    ("隱私政策", "免責"),
    ("Google Play", "審查"),
    ("金鑰保管", "免責"),
]


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄。"""
    if start is not None:
        return start.resolve()
    cur = Path(__file__).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "notes").is_dir() and (parent / "docs").is_dir():
            return parent
    return Path.cwd()


def verify_zeabur_audit(text: str) -> List[str]:
    """
    驗證 docs/zeabur-incident-credential-audit.md：
    - 第一行符合 `^結論：(有使用|無使用) Zeabur`
    - 包含倉庫掃描與 GitHub 授權稽核表格
    - 不含任何高危明文金鑰格式
    """
    errors: List[str] = []
    lines = text.strip().splitlines()
    if not lines:
        return ["檔案內容為空"]

    # 1. 第一行結論校驗
    first_line = lines[0].strip()
    if not ZEABUR_FIRST_LINE_RE.match(first_line):
        errors.append(
            f"首行不符合規範：必須符合 `^結論：(有使用|無使用) Zeabur`，實際為：'{first_line}'"
        )

    # 2. 倉庫掃描表格校驗
    has_repo_scan_heading = bool(re.search(r"##\s+2\.\s+.*倉庫掃描", text))
    has_repo_scan_table = bool(
        re.search(r"\|.*檢查項目.*\|.*檢測結果.*\|", text)
        and re.search(r"\|(?:\s*:?---+:?\s*\|){3,}", text)
    )
    if not (has_repo_scan_heading and has_repo_scan_table):
        errors.append("缺少本機專案倉庫掃描結果之結構化 Markdown 表格")

    # 3. GitHub 授權稽核表格校驗
    has_gh_audit_heading = bool(re.search(r"##\s+3\.\s+.*GitHub.*授權", text))
    has_gh_audit_table = bool(
        re.search(r"\|.*稽核項目.*\|.*稽核結果.*\|", text)
        and re.search(r"\|(?:\s*:?---+:?\s*\|){3,}", text)
    )
    if not (has_gh_audit_heading and has_gh_audit_table):
        errors.append("缺少 GitHub 帳號與倉庫授權稽核之結構化 Markdown 表格")

    # 4. 零高危金鑰暴露掃描
    for label, pattern in SECRET_PATTERNS.items():
        matched = re.search(pattern, text)
        if matched:
            errors.append(f"偵測到疑似高危明文憑證暴露（{label}）：{matched.group(0)[:12]}...")

    return errors


def verify_platform_breach_response(text: str) -> List[str]:
    """
    驗證 templates/platform-breach-response.md：
    - 包含「立即處置」「二次憑證」「稽核與帳單」「遷移評估」「預防」五大段落
    - 每段各自有 >= 3 個 `- [ ]` 勾選項
    """
    errors: List[str] = []

    # 解析所有 ## 二級段落
    sections: Dict[str, List[str]] = {}
    current_sec: Optional[str] = None

    for line in text.splitlines():
        heading_match = re.match(r"^##\s+(.+)$", line.strip())
        if heading_match:
            title = heading_match.group(1).strip()
            # 比對屬於哪一個必備段落
            matched_name = None
            for req in REQUIRED_BREACH_SECTIONS:
                if req in title:
                    matched_name = req
                    break
            current_sec = matched_name or title
            sections.setdefault(current_sec, [])
        elif current_sec is not None:
            if re.match(r"^-\s+\[\s*\]\s+", line.strip()):
                sections[current_sec].append(line.strip())

    for req_sec in REQUIRED_BREACH_SECTIONS:
        if req_sec not in sections:
            errors.append(f"缺少必備應變段落「{req_sec}」")
        else:
            item_count = len(sections[req_sec])
            if item_count < 3:
                errors.append(
                    f"應變段落「{req_sec}」檢核項不足（需 >= 3 項 `- [ ]`，實際僅 {item_count} 項）"
                )

    return errors


def verify_web_to_app_evaluation(text: str) -> List[str]:
    """
    驗證 docs/web-to-app-evaluation.md：
    - 包含明確「結論：可行／不可行」
    - 包含權限分析（AndroidManifest.xml）與簽名分析（Keystore / 憑證）
    """
    errors: List[str] = []

    # 1. 可行性結論
    if not WEB_TO_APP_CONCLUSION_RE.search(text):
        errors.append("缺少明確可行性結論（需包含「結論：可行」或「結論：不可行」）")

    # 2. 權限分析
    has_manifest_heading = bool(re.search(r"##\s+3\.\s+.*AndroidManifest\.xml.*權限", text))
    has_permission_details = "android.permission." in text
    if not (has_manifest_heading and has_permission_details):
        errors.append("缺少 AndroidManifest.xml 權限宣告與權限架構深度分析")

    # 3. 簽名分析
    has_keystore_heading = bool(re.search(r"##\s+4\.\s+.*Keystore.*簽名", text))
    has_signing_details = any(
        kw in text for kw in ["RSA-3072", "PKCS#12", ".p12", ".jks", "apksig", "PerAppSigningIdentity"]
    )
    if not (has_keystore_heading and has_signing_details):
        errors.append("缺少 Keystore 簽名機制、演算法與金鑰管理架構分析")

    return errors


def verify_web_to_app_workflow(text: str) -> List[str]:
    """
    驗證 docs/web-to-app-freelance-workflow.md：
    - 完整包含六大標準步驟
    - 完整包含四大風險防範與免責條款
    """
    errors: List[str] = []

    # 1. 六大步驟校驗
    for step_num, step_title in REQUIRED_WORKFLOW_STEPS:
        pattern = rf"{step_num}.*?{step_title}"
        if not re.search(pattern, text):
            errors.append(f"缺少接案標準流程之「{step_num}：{step_title}」章節")

    # 2. 四大免責條款校驗
    for kw1, kw2 in REQUIRED_DISCLAIMERS:
        pattern = rf"{kw1}.*?{kw2}|{kw2}.*?{kw1}"
        if not re.search(pattern, text):
            errors.append(f"缺少四大風險免責條款之「{kw1}/{kw2}」防範規格")

    return errors


def verify_all_specs(repo_root: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """執行全數外部裁判規格驗證。"""
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    targets = [
        ("docs/zeabur-incident-credential-audit.md", verify_zeabur_audit),
        ("templates/platform-breach-response.md", verify_platform_breach_response),
        ("docs/web-to-app-evaluation.md", verify_web_to_app_evaluation),
        ("docs/web-to-app-freelance-workflow.md", verify_web_to_app_workflow),
    ]

    for rel_path, verifier in targets:
        full_path = root / rel_path
        if not full_path.exists():
            results[rel_path] = [f"目標檔案不存在：{rel_path}"]
        else:
            content = full_path.read_text(encoding="utf-8")
            results[rel_path] = verifier(content)

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="資安事件盤點與 WebToApp 接案規格之外部裁判結構驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 notes/ 與 docs/ 之根目錄）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(f"[*] 執行外部裁判規格結構校驗，專案根目錄：{root}")

    all_passed, results = verify_all_specs(root)

    for rel_path, errs in results.items():
        if errs:
            print(f"\n[FAIL] ❌ {rel_path} 發現 {len(errs)} 項規格缺陷：")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[PASS] ✅ {rel_path} 結構與規格完全相符")

    if all_passed:
        print("\n[SUCCESS] 🎉 全數資安事件與接案規格文件均通過外部裁判結構驗證！")
        return 0
    else:
        print("\n[ERROR] 外部裁判驗證未通過，請依上述錯誤修正文件。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
