#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Persistence & Stealer Artifacts Auditor (verify_cloud_persistence_audit.py)
---------------------------------------------------------------------------------
落實 Nicholas Lin 案與 LLMJacking 防範：
1. 本地持久化與竊密木馬特徵掃描（AMOS Stealer 檔案特徵：com.finder.helper.plist, .mainhelper, .agent 等）
2. 雲端 Service Account 異常稽核（偵測非預設名稱、下載 Private Key 與短期激增帳號）
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple

# 確保在 Windows CP950 等環境下輸出為 UTF-8（通過 test_cli_help_encoding 契約）
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


KNOWN_STEALER_ARTIFACTS = {
    "com.finder.helper.plist": "AMOS 木馬常用持久化 LaunchDaemon 設定檔",
    ".mainhelper": "AMOS 木馬憑證竊取後門元件",
    ".agent": "偽裝成 AI Agent 之惡意常駐腳本",
    ".pass": "明文或弱加密暫存憑證檔",
    ".id": "遭竊設備識別指紋檔"
}


def audit_local_persistence_artifacts(scan_dir: str) -> Tuple[bool, List[Dict[str, str]]]:
    """
    掃描目標目錄中是否包含已知的 AMOS / Stealer 持久化與竊密特徵檔案
    """
    findings = []
    if not os.path.exists(scan_dir):
        return True, findings

    for root, dirs, files in os.walk(scan_dir):
        # 同時檢查隱藏檔與一般檔案
        for fname in files:
            lower_fname = fname.lower()
            for pattern, desc in KNOWN_STEALER_ARTIFACTS.items():
                if lower_fname == pattern.lower() or fname == pattern:
                    full_p = os.path.join(root, fname)
                    findings.append({
                        "file_path": full_p,
                        "file_name": fname,
                        "threat_description": desc
                    })

    is_clean = len(findings) == 0
    return is_clean, findings


def audit_service_account_anomalies(accounts: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    審查雲端 Service Account 清單：
    - 標注帶有使用者下載 Private Key 的帳號
    - 標注非預設 compute service account 且具備高權限/AI 呼叫能力的可疑帳號
    """
    anomalies = []
    for acc in accounts:
        email = acc.get("email", "")
        has_user_managed_keys = acc.get("has_user_managed_keys", False)
        roles = acc.get("roles", [])
        is_default_compute = email.endswith("-compute@developer.gserviceaccount.com") or email.endswith("@appspot.gserviceaccount.com")

        reasons = []
        if has_user_managed_keys:
            reasons.append("具有使用者自建/下載之 Private Key（存在離線洩漏與 LLMJacking 風險）")

        if not is_default_compute and any("admin" in r.lower() or "vertex" in r.lower() or "aiplatform" in r.lower() for r in roles):
            reasons.append(f"具備高危或 AI 模型呼叫角色（roles: {roles}），非雲端平台預設帳號")

        if reasons:
            anomalies.append({
                "email": email,
                "reasons": reasons,
                "severity": "HIGH" if has_user_managed_keys and not is_default_compute else "MEDIUM"
            })

    is_safe = len(anomalies) == 0
    return is_safe, anomalies


def main() -> int:
    parser = argparse.ArgumentParser(description="Cloud Persistence & Stealer Artifacts Auditor")
    parser.add_argument("--scan-dir", type=str, default="", help="掃描本地持久化後門目錄")
    parser.add_argument("--audit-accounts-json", type=str, default="", help="審查 Service Account JSON 檔案")
    args = parser.parse_args()

    exit_code = 0

    if args.scan_dir:
        is_clean, findings = audit_local_persistence_artifacts(args.scan_dir)
        if is_clean:
            print(f"[PASS] 本地目錄安全，未發現已知竊密木馬特徵：{args.scan_dir}")
        else:
            print(f"[ALERT] 發現 {len(findings)} 個可疑持久化/竊密特徵檔案！")
            for f in findings:
                print(f"  - {f['file_path']} ({f['threat_description']})")
            exit_code = 1

    if args.audit_accounts_json:
        if not os.path.exists(args.audit_accounts_json):
            print(f"[ERROR] 找不到檔案：{args.audit_accounts_json}")
            return 1
        with open(args.audit_accounts_json, "r", encoding="utf-8") as jf:
            data = json.load(jf)
        accounts_list = data if isinstance(data, list) else data.get("accounts", [])
        is_safe, anomalies = audit_service_account_anomalies(accounts_list)
        if is_safe:
            print(f"[PASS] Service Account 稽核合格，無高危外洩風險帳號。")
        else:
            print(f"[ALERT] 發現 {len(anomalies)} 個可疑或高危 Service Account！")
            for a in anomalies:
                print(f"  - [{a['severity']}] {a['email']}: {', '.join(a['reasons'])}")
            exit_code = 1

    if not args.scan_dir and not args.audit_accounts_json:
        print("[INFO] 請提供 --scan-dir 或 --audit-accounts-json 參數進行稽核。")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
