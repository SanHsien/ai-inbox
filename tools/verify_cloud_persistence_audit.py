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
import re
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


_ENV_PLACEHOLDER_RE = re.compile(
    r"^(\$\{[A-Za-z0-9_]+\}|\$[A-Za-z0-9_]+|%[A-Za-z0-9_]+%|\{\{[^}]+\}\}|<[^>]+>)$"
)
_BEARER_VALUE_RE = re.compile(r"(?i)\bBearer\s+([^\s\"']+)")


def _is_hardcoded_token(token_val: str) -> bool:
    """判斷 Bearer token 值是否為寫死的真實憑證（排除環境變數或樣板佔位符）。"""
    val = token_val.strip().strip("\"'")
    if not val or _ENV_PLACEHOLDER_RE.match(val):
        return False
    if val.startswith("ya29."):
        return True
    if "$(" in val or "`" in val:
        return False
    return len(val) >= 16


def audit_mcp_config_credentials(config_data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    審查 MCP 設定檔（mcpServers / servers）：
    1. 攔截 headers 或 args 中直接寫死的明文 Bearer Token / Google OAuth Access Token (ya29.*)
       （既違反憑證不進設定檔與指令列硬閘門，且短效 Token 過期後會靜默失效）
    2. 攔截同時要求 cloud-platform 全權 scope 之過度授權配置
    """
    servers = config_data.get("mcpServers") or config_data.get("servers") or {}
    if not isinstance(servers, dict):
        return True, []

    anomalies: List[Dict[str, Any]] = []
    for srv_name, srv_cfg in servers.items():
        if not isinstance(srv_cfg, dict):
            continue
        reasons: List[str] = []
        severity = "MEDIUM"

        # 1. 檢查 headers 中的靜態 Bearer / ya29. token
        headers = srv_cfg.get("headers") or {}
        if isinstance(headers, dict):
            for h_key, h_val in headers.items():
                if not isinstance(h_val, str):
                    continue
                m = _BEARER_VALUE_RE.search(h_val)
                if m and _is_hardcoded_token(m.group(1)):
                    reasons.append(
                        f"headers['{h_key}'] 寫死明文 Bearer Token（外洩風險且短效 OAuth Token 過期後會靜默失效）"
                    )
                    severity = "HIGH"
                elif "ya29." in h_val and not _ENV_PLACEHOLDER_RE.match(h_val.strip()):
                    reasons.append(
                        f"headers['{h_key}'] 含寫死的 Google OAuth Access Token (ya29.*)"
                    )
                    severity = "HIGH"

        # 2. 檢查 args 中的 --header Bearer token 或 cloud-platform 全權 scope
        args_list = srv_cfg.get("args") or []
        if isinstance(args_list, list):
            joined_args = " ".join(str(a) for a in args_list)
            for m in _BEARER_VALUE_RE.finditer(joined_args):
                if _is_hardcoded_token(m.group(1)):
                    reasons.append(
                        "args 命令列參數寫死明文 Bearer Token（違反憑證不進指令列硬閘門）"
                    )
                    severity = "HIGH"
                    break
            if "cloud-platform" in joined_args:
                reasons.append(
                    "args 包含全權 'cloud-platform' OAuth scope（一旦本機憑證遭竊將危及整個 GCP 專案）"
                )
                if severity != "HIGH":
                    severity = "HIGH"

        # 3. 檢查 env 中的 ya29. 明文或 cloud-platform scope
        env_map = srv_cfg.get("env") or {}
        if isinstance(env_map, dict):
            for e_key, e_val in env_map.items():
                if not isinstance(e_val, str):
                    continue
                if e_val.startswith("ya29."):
                    reasons.append(
                        f"env['{e_key}'] 寫死短效 Google OAuth Access Token (ya29.*)"
                    )
                    severity = "HIGH"
                if "cloud-platform" in e_val:
                    reasons.append(
                        f"env['{e_key}'] 包含全權 'cloud-platform' OAuth scope"
                    )

        if reasons:
            anomalies.append({
                "server": srv_name,
                "reasons": reasons,
                "severity": severity,
            })

    return len(anomalies) == 0, anomalies


def main() -> int:
    parser = argparse.ArgumentParser(description="Cloud Persistence & Stealer Artifacts Auditor")
    parser.add_argument("--scan-dir", type=str, default="", help="掃描本地持久化後門目錄")
    parser.add_argument("--audit-accounts-json", type=str, default="", help="審查 Service Account JSON 檔案")
    parser.add_argument("--audit-mcp-config", type=str, default="", help="審查 MCP 設定檔 JSON 是否含明文 Bearer Token 或過寬 GCP scope")
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

    if args.audit_mcp_config:
        if not os.path.exists(args.audit_mcp_config):
            print(f"[ERROR] 找不到檔案：{args.audit_mcp_config}")
            return 1
        with open(args.audit_mcp_config, "r", encoding="utf-8") as mf:
            mcp_data = json.load(mf)
        is_safe, mcp_anomalies = audit_mcp_config_credentials(mcp_data)
        if is_safe:
            print(f"[PASS] MCP 設定檔稽核合格，未發現寫死的明文 Token 或過寬 cloud-platform scope。")
        else:
            print(f"[ALERT] 發現 {len(mcp_anomalies)} 個高風險 MCP Server 憑證配置！")
            for a in mcp_anomalies:
                print(f"  - [{a['severity']}] {a['server']}: {', '.join(a['reasons'])}")
            exit_code = 1

    if not args.scan_dir and not args.audit_accounts_json and not args.audit_mcp_config:
        print("[INFO] 請提供 --scan-dir、--audit-accounts-json 或 --audit-mcp-config 參數進行稽核。")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
