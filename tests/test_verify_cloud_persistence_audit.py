#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
單元測試：test_verify_cloud_persistence_audit.py
驗證 AMOS 竊密木馬特徵掃描與雲端 Service Account 異常稽核工具
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

# 將 tools 加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))
import verify_cloud_persistence_audit as auditor

from verify_cloud_persistence_audit import (
    audit_local_persistence_artifacts,
    audit_service_account_anomalies,
    audit_mcp_config_credentials,
)


class TestVerifyCloudPersistenceAudit(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_directory_scan(self):
        # 建立一般正常檔案
        normal_file = os.path.join(self.test_dir, "normal_script.py")
        with open(normal_file, "w", encoding="utf-8") as f:
            f.write("print('hello world')\n")

        is_clean, findings = audit_local_persistence_artifacts(self.test_dir)
        self.assertTrue(is_clean)
        self.assertEqual(len(findings), 0)

    def test_detect_amos_launch_daemon(self):
        # 建立模擬的 com.finder.helper.plist
        plist_path = os.path.join(self.test_dir, "com.finder.helper.plist")
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write("<plist>malicious</plist>\n")

        is_clean, findings = audit_local_persistence_artifacts(self.test_dir)
        self.assertFalse(is_clean)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["file_name"], "com.finder.helper.plist")

    def test_detect_hidden_mainhelper(self):
        # 建立隱藏的 .mainhelper
        helper_path = os.path.join(self.test_dir, ".mainhelper")
        with open(helper_path, "w", encoding="utf-8") as f:
            f.write("binary_payload")

        is_clean, findings = audit_local_persistence_artifacts(self.test_dir)
        self.assertFalse(is_clean)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["file_name"], ".mainhelper")

    def test_service_account_default_safe(self):
        accounts = [
            {
                "email": "123456789-compute@developer.gserviceaccount.com",
                "createTime": "2026-11-14T00:00:00Z",
                "has_user_managed_keys": False,
                "roles": ["roles/editor"]
            }
        ]
        is_safe, anomalies = audit_service_account_anomalies(accounts)
        self.assertTrue(is_safe)
        self.assertEqual(len(anomalies), 0)

    def test_service_account_high_risk_private_key(self):
        accounts = [
            {
                "email": "backup-worker@my-project.iam.gserviceaccount.com",
                "has_user_managed_keys": True,
                "roles": ["roles/aiplatform.user", "roles/vertexai.admin"]
            }
        ]
        is_safe, anomalies = audit_service_account_anomalies(accounts)
        self.assertFalse(is_safe)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["severity"], "HIGH")
        self.assertEqual(len(anomalies[0]["reasons"]), 2)

    def test_service_account_medium_risk_roles(self):
        accounts = [
            {
                "email": "ai-caller@my-project.iam.gserviceaccount.com",
                "has_user_managed_keys": False,
                "roles": ["roles/aiplatform.user"]
            }
        ]
        is_safe, anomalies = audit_service_account_anomalies(accounts)
        self.assertFalse(is_safe)
        self.assertEqual(anomalies[0]["severity"], "MEDIUM")

    def test_mcp_config_detects_hardcoded_bearer_and_cloud_platform_scope(self):
        bad_cfg = {
            "mcpServers": {
                "gemini-notebook": {
                    "url": "https://notebook.googleapis.com/mcp",
                    "headers": {
                        "Authorization": "Bearer ya29.a0AfH6SMBxExampleHardcodedToken123456"
                    },
                    "args": [
                        "--scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/notebook"
                    ],
                }
            }
        }
        is_safe, anomalies = audit_mcp_config_credentials(bad_cfg)
        self.assertFalse(is_safe)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["server"], "gemini-notebook")
        self.assertEqual(anomalies[0]["severity"], "HIGH")
        self.assertTrue(any("Bearer Token" in r for r in anomalies[0]["reasons"]))
        self.assertTrue(any("cloud-platform" in r for r in anomalies[0]["reasons"]))

    def test_mcp_config_allows_env_placeholder(self):
        safe_cfg = {
            "mcpServers": {
                "gemini-notebook": {
                    "url": "https://notebook.googleapis.com/mcp",
                    "headers": {
                        "Authorization": "Bearer ${NOTEBOOK_ACCESS_TOKEN}"
                    },
                }
            }
        }
        is_safe, anomalies = audit_mcp_config_credentials(safe_cfg)
        self.assertTrue(is_safe, anomalies)
        self.assertEqual(anomalies, [])


class CloudAuditRegressions(unittest.TestCase):
    def test_owner_editor_admin_roles(self):
        for role in ('roles/owner', 'roles/editor', 'roles/admin', 'roles/iam.serviceAccountAdmin'):
            with self.subTest(role=role):
                self.assertFalse(audit_service_account_anomalies([
                    {'email': 'evil@p.iam.gserviceaccount.com', 'roles': [role],
                     'createTime': '2026-11-14T00:00:00Z'}])[0])

    def test_account_burst_sliding_window(self):
        rows = [{'email': f'new-{i}@p.iam.gserviceaccount.com', 'roles': [],
                 'createTime': '2026-11-14T00:00:00Z'} for i in range(100)]
        self.assertFalse(audit_service_account_anomalies(rows)[0])
        self.assertTrue(audit_service_account_anomalies(rows[:4])[0])
        spread = [dict(row, createTime=f'2026-11-{i+1:02}T00:00:00+00:00')
                  for i, row in enumerate(rows[:6])]
        self.assertTrue(audit_service_account_anomalies(spread)[0])
        with self.assertRaises(ValueError):
            audit_service_account_anomalies([dict(rows[0], createTime='bad')])

    def test_account_schema_fail_closed(self):
        for rows in ([], {}, [None], [{}], [{'email': 'x', 'roles': 'roles/owner'}],
                     [{'email': 'x', 'roles': [], 'has_user_managed_keys': 'false'}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                audit_service_account_anomalies(rows)

    def test_missing_creation_time_cannot_pass(self):
        with self.assertRaises(ValueError):
            audit_service_account_anomalies([{'email': 'x', 'roles': []}])

    def test_burst_threshold_and_window_edges(self):
        rows = [{'email': str(i), 'roles': [], 'createTime': '2026-11-14T00:00:00Z'}
                for i in range(4)]
        rows.append({'email': 'last', 'roles': [], 'createTime': '2026-11-14T01:00:00Z'})
        self.assertFalse(audit_service_account_anomalies(rows)[0])
        rows[-1]['createTime'] = '2026-11-14T01:00:01Z'
        self.assertTrue(audit_service_account_anomalies(rows)[0])
        self.assertFalse(audit_service_account_anomalies(rows, burst_threshold=4)[0])
        rows[-1]['createTime'] = '2026-11-14T02:00:00+01:00'
        self.assertFalse(audit_service_account_anomalies(rows)[0])
        for kwargs in ({'burst_threshold': 1}, {'burst_window_seconds': 0}):
            with self.assertRaises(ValueError):
                audit_service_account_anomalies(rows, **kwargs)

    def test_short_and_non_bearer_authorization(self):
        for value in ('Bearer abc123', 'Basic abc', 'abc', 'Bearer $(cmd)', 'Bearer `cmd`', ''):
            with self.subTest(value=value):
                self.assertFalse(audit_mcp_config_credentials(
                    {'mcpServers': {'x': {'headers': {'authorization': value}}}})[0])

    def test_placeholder_and_token_length_boundaries(self):
        for value in ('${TOKEN}', '$TOKEN', '%TOKEN%', '{{TOKEN}}', '<TOKEN>'):
            self.assertTrue(audit_mcp_config_credentials(
                {'servers': {'x': {'headers': {'Authorization': 'Bearer ' + value}}}})[0])
        for value in ('a', 'abc123', 'a' * 16):
            self.assertFalse(audit_mcp_config_credentials(
                {'servers': {'x': {'args': ['Bearer ' + value]}}})[0])

    def test_args_env_scan_each_token_field(self):
        for cfg in ({'args': ['--access-token', 'ya29.synthetic-review-only']},
                    {'env': {'X': 'prefix ya29.synthetic-review-only'}},
                    {'args': ['--header', 'Authorization: Basic abc']},
                    {'env': {'X': 'Bearer abc'}},
                    {'env': {'SCOPES': 'cloud-platform'}}):
            with self.subTest(cfg=cfg):
                self.assertFalse(audit_mcp_config_credentials({'mcpServers': {'x': cfg}})[0])

    def test_mcp_schema_fail_closed(self):
        for cfg in (None, [], {}, {'mcpServers': []}, {'mcpServers': {}}, {'servers': {'x': {}}},
                    {'servers': {'x': []}}, {'servers': {'x': {'args': 'bad'}}},
                    {'servers': {'x': {'args': [5]}}},
                    {'servers': {'x': {'env': {'X': 5}}}},
                    {'servers': {'x': {'headers': None}}},
                    {'mcpServers': [], 'servers': {'x': {}}}):
            with self.subTest(cfg=cfg), self.assertRaises(ValueError):
                audit_mcp_config_credentials(cfg)

    def test_run_keys_read_only_and_errors(self):
        registry = MagicMock()
        registry.HKEY_CURRENT_USER = 'HKCU'
        registry.HKEY_LOCAL_MACHINE = 'HKLM'
        registry.KEY_READ = 0x20019
        registry.KEY_WOW64_32KEY = 0x200
        registry.KEY_WOW64_64KEY = 0x100
        registry.REG_SZ, registry.REG_EXPAND_SZ = 1, 2
        registry.QueryInfoKey.return_value = (0, 1, 0)
        registry.EnumValue.return_value = ('helper', r'C:\test\.mainhelper', 1)
        with patch.object(auditor.sys, 'platform', 'win32'), patch.dict(sys.modules, {'winreg': registry}):
            safe, findings = auditor.audit_windows_run_keys()
            self.assertFalse(safe)
            self.assertTrue(findings)
            self.assertEqual(registry.OpenKey.call_count, 8)
            for call in registry.OpenKey.call_args_list:
                self.assertEqual(call.args[2], 0)
                self.assertIn(call.args[3], (0x20119, 0x20219))
            registry.SetValue.assert_not_called()
            registry.EnumValue.return_value = ('normal', r'C:\Program Files\app.exe', 1)
            self.assertTrue(auditor.audit_windows_run_keys()[0])
            registry.OpenKey.side_effect = PermissionError('denied')
            with self.assertRaises(OSError):
                auditor.audit_windows_run_keys()
            registry.OpenKey.side_effect = FileNotFoundError()
            self.assertTrue(auditor.audit_windows_run_keys()[0])

    def test_non_windows_run_keys_explicit_skip(self):
        with patch.object(auditor.sys, 'platform', 'linux'), patch('builtins.print') as out:
            self.assertIsNone(auditor.audit_windows_run_keys()[0])
            self.assertIn('[SKIP]', str(out.call_args_list))

    def test_cli_invalid_inputs_and_missing_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for flag, content in (('--audit-accounts-json', '[]'), ('--audit-mcp-config', '{}'),
                                  ('--audit-mcp-config', '{'), ('--audit-mcp-config', '')):
                p = root / 'input.json'
                p.write_text(content, encoding='utf-8')
                result = subprocess.run([sys.executable, '-B', auditor.__file__, flag, str(p)], capture_output=True)
                self.assertEqual(result.returncode, 2, result.stdout)
            for args in ([], ['--scan-dir', str(root / 'absent')], ['--scan-dir', str(p)],
                         ['--audit-mcp-config', str(root / 'absent')]):
                result = subprocess.run([sys.executable, '-B', auditor.__file__, *args], capture_output=True)
                self.assertEqual(result.returncode, 2, result.stdout)


if __name__ == "__main__":
    unittest.main()
