#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Persistence & Stealer Artifacts Auditor (verify_cloud_persistence_audit.py)
---------------------------------------------------------------------------------
離線啟發式稽核，不判定感染或帳號授權是否合法。
--scan-dir 僅掃指定目錄檔名，不自動發現 LaunchAgents/Startup。
--scan-run-keys 唯讀 HKCU/HKLM Run/RunOnce 32/64-bit views；非 Windows 明示跳過。
帳號輸入須為非空陣列或 {"accounts": [...]}：email 唯一、roles 字串陣列，
has_user_managed_keys 選填 boolean（未提供視為 false，非遠端金鑰查證）。
createTime 為外部補入的含時區 ISO 8601 時間；缺漏不允許成功通過。
預設在任意 3600 秒（含邊界）內建立至少 5 個帳號即標記，可用 --burst-* 調整。
MCP 檢查 mcpServers/servers 的 headers/args/env，不作完整 MCP schema 驗證。
只豁免完整 ${VAR}/$VAR/%VAR%/{{VAR}}/<VAR>，不執行替換或 shell。
結束碼：0=所選檢查未命中；1=規則命中；2=輸入/讀取失敗或只跳過。
來源：
https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys
https://docs.python.org/3/library/winreg.html
https://docs.cloud.google.com/iam/docs/roles-overview
IAM v1 ServiceAccount 不含 createTime；本地增補欄位，不宣稱可直接偵測原生匯出：
https://docs.cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
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
    """只掃指定目錄的已知檔名；無效或不可讀輸入不得通過。"""
    if not scan_dir or not os.path.isdir(scan_dir):
        raise ValueError("掃描目錄不存在或不是目錄，未掃描")
    findings = []

    def fail_walk(error):
        raise error

    for root, dirs, files in os.walk(scan_dir, onerror=fail_walk):
        for fname in files:
            if fname.lower() in KNOWN_STEALER_ARTIFACTS:
                findings.append({
                    "file_path": os.path.join(root, fname),
                    "file_name": fname,
                    "threat_description": KNOWN_STEALER_ARTIFACTS[fname.lower()],
                })
    return not findings, findings


def audit_windows_run_keys():
    """唯讀 HKCU/HKLM Run/RunOnce 的 32/64-bit views；非 Windows 回 None。"""
    if sys.platform != "win32":
        print("[SKIP] 非 Windows，未檢查 Windows Run Keys")
        return None, []
    import winreg

    findings = []
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for name in ("Run", "RunOnce"):
            key_path = rf"Software\Microsoft\Windows\CurrentVersion\{name}"
            for view in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
                try:
                    key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | view)
                except FileNotFoundError:
                    continue
                with key:
                    count = winreg.QueryInfoKey(key)[1]
                    for index in range(count):
                        value_name, value, kind = winreg.EnumValue(key, index)
                        if kind not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) or not isinstance(value, str):
                            raise ValueError("Run Key 值不是可檢查的命令字串")
                        if any(marker in (value_name + " " + value).lower()
                               for marker in KNOWN_STEALER_ARTIFACTS):
                            # 不輸出命令內容，避免憑證外洩。
                            findings.append({"key": key_path, "view": view,
                                             "reason": "Run Key 含已知可疑檔名"})
    return not findings, findings


HIGH_PRIVILEGE_ROLES = {"roles/owner", "roles/editor", "roles/admin"}


def audit_service_account_anomalies(accounts, *, burst_window_seconds=3600, burst_threshold=5):
    """離線清單；任意滑動時間窗內 >= threshold 個不同 email 建立即標記。"""
    if not isinstance(accounts, list) or not accounts:
        raise ValueError("accounts 必須為非空陣列")
    if burst_window_seconds <= 0 or burst_threshold < 2:
        raise ValueError("時間窗須 > 0、激增門檻須 >= 2")
    anomalies = []
    timestamps = []
    seen = set()
    for acc in accounts:
        if not isinstance(acc, dict):
            raise ValueError("account 必須為物件")
        email, roles = acc.get("email"), acc.get("roles")
        if not isinstance(email, str) or not email.strip() or email in seen:
            raise ValueError("email 必須為非空且唯一字串")
        seen.add(email)
        if not isinstance(roles, list) or any(not isinstance(r, str) or not r for r in roles):
            raise ValueError("roles 必須為字串陣列，不能省略")
        has_keys = acc.get("has_user_managed_keys", False)
        if not isinstance(has_keys, bool):
            raise ValueError("has_user_managed_keys 必須為 boolean")
        if "createTime" in acc:
            raw = acc["createTime"]
            if not isinstance(raw, str):
                raise ValueError("createTime 必須為含時區 ISO 8601 字串")
            created = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if created.tzinfo is None:
                raise ValueError("createTime 缺少時區")
            timestamps.append((created.timestamp(), email))
        default = email.endswith(("-compute@developer.gserviceaccount.com", "@appspot.gserviceaccount.com"))
        reasons = []
        if has_keys:
            reasons.append("具有使用者管理 Private Key（需人工確認用途與來源）")
        high_role = any(r.lower() in HIGH_PRIVILEGE_ROLES or
                        any(part in r.lower() for part in ("admin", "vertex", "aiplatform"))
                        for r in roles)
        if not default and high_role:
            reasons.append("非預設帳號具高權限或 AI 角色")
        if reasons:
            anomalies.append({"email": email, "reasons": reasons,
                              "severity": "HIGH" if has_keys and not default else "MEDIUM"})
    timestamps.sort()
    left = 0
    burst_emails = set()
    for right, (stamp, email) in enumerate(timestamps):
        while stamp - timestamps[left][0] > burst_window_seconds:
            left += 1
        if right - left + 1 >= burst_threshold:
            burst_emails.update(item[1] for item in timestamps[left:right + 1])
    if burst_emails:
        anomalies.append({"email": "(creation burst)", "severity": "HIGH",
                          "reasons": [f"{burst_window_seconds} 秒窗內至少 {burst_threshold} 個帳號建立；共標記 {len(burst_emails)} 個"]})
    if len(timestamps) != len(accounts) and not anomalies:
        raise ValueError("缺 createTime，激增檢查不完整，不能通過")
    return not anomalies, anomalies


_ENV_PLACEHOLDER_RE = re.compile(
    r"^(\$\{[A-Za-z0-9_]+\}|\$[A-Za-z0-9_]+|%[A-Za-z0-9_]+%|\{\{[^}]+\}\}|<[^>]+>)$"
)
_BEARER_VALUE_RE = re.compile(r"(?i)\bBearer\s+([^\s\"']+)")


def _is_hardcoded_token(token_val: str) -> bool:
    return not bool(_ENV_PLACEHOLDER_RE.fullmatch(token_val.strip()))


def audit_mcp_config_credentials(config_data):
    """嚴格檢查兩種 server map，以及每個 headers/args/env 字串欄位。"""
    if not isinstance(config_data, dict):
        raise ValueError("MCP 根節點必須為物件")
    maps = [config_data[k] for k in ("mcpServers", "servers") if k in config_data]
    if not maps or any(not isinstance(m, dict) or not m for m in maps):
        raise ValueError("mcpServers/servers 必須為非空物件")
    anomalies = []
    for servers in maps:
        for srv_name, cfg in servers.items():
            if not isinstance(cfg, dict) or not cfg:
                raise ValueError("server 設定必須為物件")
            fields = []
            for group in ("headers", "env"):
                mapping = cfg.get(group, {})
                if not isinstance(mapping, dict) or any(not isinstance(v, str) for v in mapping.values()):
                    raise ValueError(f"{group} 必須為字串值物件")
                fields.extend((group, k, v) for k, v in mapping.items())
            args = cfg.get("args", [])
            if not isinstance(args, list) or any(not isinstance(v, str) for v in args):
                raise ValueError("args 必須為字串陣列")
            fields.extend(("args", str(i), v) for i, v in enumerate(args))
            reasons = []
            for group, key, value in fields:
                if group == "headers" and key.lower() == "authorization":
                    token = re.sub(r"(?i)^Bearer\s+", "", value.strip())
                    if _is_hardcoded_token(token):
                        reasons.append("headers Authorization 寫死靜態憑證 / Bearer Token")
                for match in _BEARER_VALUE_RE.finditer(value):
                    if _is_hardcoded_token(match.group(1)):
                        reasons.append(f"{group} 含靜態 Bearer Token")
                # 命令列也可能使用 Basic 或自訂 Authorization scheme。
                if group == "args" and re.search(r"(?i)authorization\s*:", value):
                    token = re.split(r"(?i)authorization\s*:\s*", value, maxsplit=1)[1]
                    token = re.sub(r"(?i)^Bearer\s+", "", token.strip())
                    if _is_hardcoded_token(token):
                        reasons.append("args 含靜態 Authorization")
                if "ya29." in value and not _ENV_PLACEHOLDER_RE.fullmatch(value.strip()):
                    reasons.append(f"{group} 含靜態 ya29. Token")
                if "cloud-platform" in value:
                    reasons.append(f"{group} 含 cloud-platform scope，需人工審查最小權限")
            if reasons:
                anomalies.append({"server": srv_name, "reasons": reasons, "severity": "HIGH"})
    return not anomalies, anomalies


def main() -> int:
    parser = argparse.ArgumentParser(
        description="離線持久化與憑證規則稽核；0=所選檢查未命中，1=規則命中，2=輸入/讀取失敗或僅跳過")
    parser.add_argument("--scan-dir", help="只掃指定目錄的已知檔名（含 Startup 或 LaunchAgents）")
    parser.add_argument("--scan-run-keys", action="store_true", help="唯讀 Windows Run/RunOnce；非 Windows 明示跳過")
    parser.add_argument("--audit-accounts-json", help="離線帳號 JSON 陣列或 accounts 物件")
    parser.add_argument("--burst-window-seconds", type=int, default=3600)
    parser.add_argument("--burst-threshold", type=int, default=5)
    parser.add_argument("--audit-mcp-config", help="MCP JSON headers/args/env 檢查")
    args = parser.parse_args()
    selected = args.scan_dir or args.scan_run_keys or args.audit_accounts_json or args.audit_mcp_config
    if not selected:
        parser.error("至少選擇一項稽核")
    exit_code = 0
    completed = 0
    try:
        if args.scan_dir:
            safe, findings = audit_local_persistence_artifacts(args.scan_dir)
            completed += 1
            print(f"[{'PASS' if safe else 'ALERT'}] 指定目錄已知檔名檢查：{len(findings)} 筆命中")
            exit_code |= int(not safe)
        if args.scan_run_keys:
            safe, findings = audit_windows_run_keys()
            if safe is not None:
                completed += 1
                print(f"[{'PASS' if safe else 'ALERT'}] Run Keys 已知檔名檢查：{len(findings)} 筆命中")
                exit_code |= int(not safe)
        if args.audit_accounts_json:
            data = json.loads(Path(args.audit_accounts_json).read_text(encoding="utf-8-sig"))
            accounts = data.get("accounts") if isinstance(data, dict) else data
            safe, findings = audit_service_account_anomalies(
                accounts, burst_window_seconds=args.burst_window_seconds, burst_threshold=args.burst_threshold)
            completed += 1
            print(f"[{'PASS' if safe else 'ALERT'}] 帳號規則檢查：{len(findings)} 筆命中")
            exit_code |= int(not safe)
        if args.audit_mcp_config:
            data = json.loads(Path(args.audit_mcp_config).read_text(encoding="utf-8-sig"))
            safe, findings = audit_mcp_config_credentials(data)
            completed += 1
            print(f"[{'PASS' if safe else 'ALERT'}] MCP 規則檢查：{len(findings)} 筆命中")
            exit_code |= int(not safe)
    except (OSError, ValueError, TypeError) as exc:
        # 不回顯原始輸入或解析片段，以免錯誤訊息洩漏 Token。
        print(f"[ERROR] 輸入或讀取失敗，稽核未完成（{type(exc).__name__}）", file=sys.stderr)
        return 2
    return exit_code if completed else 2


if __name__ == "__main__":
    sys.exit(main())
