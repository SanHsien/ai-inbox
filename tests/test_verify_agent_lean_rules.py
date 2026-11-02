#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
單元測試：test_verify_agent_lean_rules.py
驗證麥克風 8 條極簡規約稽核工具（verify_agent_lean_rules.py）
"""

import os
import sys
import unittest
import tempfile
import shutil

# 將 tools 加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from verify_agent_lean_rules import (
    count_lines_in_text,
    audit_change_size,
    audit_ruleset_bloat
)


class TestVerifyAgentLeanRules(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_count_lines_in_text(self):
        sample = "line 1\n\n  \nline 2\nline 3\n"
        self.assertEqual(count_lines_in_text(sample), 3)

    def test_audit_change_size_under_budget(self):
        ok, msg = audit_change_size(line_count=150, max_budget=300)
        self.assertTrue(ok)
        self.assertIn("[PASS]", msg)

    def test_audit_change_size_exact_budget(self):
        ok, msg = audit_change_size(line_count=300, max_budget=300)
        self.assertTrue(ok)
        self.assertIn("[PASS]", msg)

    def test_audit_change_size_over_budget_without_reason(self):
        ok, msg = audit_change_size(line_count=350, max_budget=300, has_explanation=False)
        self.assertFalse(ok)
        self.assertIn("[VIOLATION]", msg)

    def test_audit_change_size_over_budget_with_trivial_reason(self):
        # 理由太短小於 10 字元視為無效
        ok, msg = audit_change_size(
            line_count=450,
            max_budget=300,
            has_explanation=True,
            explanation_text="too big"
        )
        self.assertFalse(ok)
        self.assertIn("[VIOLATION]", msg)

    def test_audit_change_size_over_budget_with_valid_reason(self):
        ok, msg = audit_change_size(
            line_count=520,
            max_budget=300,
            has_explanation=True,
            explanation_text="此改動包含完整的第三方資料格式 Schema 與全套邊界單元測試用例"
        )
        self.assertTrue(ok)
        self.assertIn("[PASS-WITH-REASON]", msg)

    def test_audit_ruleset_bloat_lean_file(self):
        lean_path = os.path.join(self.test_dir, "LEAN_RULES.md")
        with open(lean_path, "w", encoding="utf-8") as f:
            f.write("# 簡約規則\n1. 跑通測試\n2. 300行上限\n3. 兩輪審查\n")

        ok, report = audit_ruleset_bloat(lean_path, max_lines=100, max_rules=10)
        self.assertTrue(ok)
        self.assertFalse(report["is_bloated"])
        self.assertEqual(report["detected_rule_items"], 3)

    def test_audit_ruleset_bloat_over_limit(self):
        bloated_path = os.path.join(self.test_dir, "BLOATED_RULES.md")
        with open(bloated_path, "w", encoding="utf-8") as f:
            f.write("# 膨脹規則庫\n")
            for i in range(50):
                f.write(f"{i+1}. 嚴格規約條款第 {i+1} 條，務必遵行不可違背。\n")

        ok, report = audit_ruleset_bloat(bloated_path, max_lines=200, max_rules=20)
        self.assertFalse(ok)
        self.assertTrue(report["is_bloated"])
        self.assertGreater(report["detected_rule_items"], 20)

    def test_audit_ruleset_bloat_nonexistent_file(self):
        ok, report = audit_ruleset_bloat(os.path.join(self.test_dir, "nonexistent.md"))
        self.assertFalse(ok)
        self.assertIn("error", report)


if __name__ == "__main__":
    unittest.main()
