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

# 將 tools 加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

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


if __name__ == "__main__":
    unittest.main()
