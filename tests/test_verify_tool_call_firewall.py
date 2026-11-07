#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
單元測試：test_verify_tool_call_firewall.py
驗證單次審批收據防火牆（防審批後竄改、防收據重放、防路徑穿越）與 Agent Trace 父子 Span 去重計算。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from verify_tool_call_firewall import (
    ToolCallFirewall,
    analyze_trace_spans,
    compute_request_digest,
    issue_approval_receipt,
)


class TestVerifyToolCallFirewall(unittest.TestCase):
    def setUp(self) -> None:
        self.fw = ToolCallFirewall(
            allowed_roles=("implementer", "maintainer"),
            allowed_roots=("src/", "docs/", "tools/"),
        )

    def test_valid_single_use_receipt_allows_write(self) -> None:
        call = {
            "tool": "write_file",
            "role": "implementer",
            "path": "src/app.py",
            "content": "print('safe')\n",
        }
        receipt = issue_approval_receipt("rcpt-001", call)
        ok, code, _ = self.fw.verify_call(call, receipt)
        self.assertTrue(ok)
        self.assertEqual(code, "ALLOWED")

    def test_replayed_receipt_is_blocked(self) -> None:
        call = {
            "tool": "write_file",
            "role": "implementer",
            "path": "src/app.py",
            "content": "print('safe')\n",
        }
        receipt = issue_approval_receipt("rcpt-001", call)
        ok1, _, _ = self.fw.verify_call(call, receipt)
        self.assertTrue(ok1)

        ok2, code2, _ = self.fw.verify_call(call, receipt)
        self.assertFalse(ok2)
        self.assertEqual(code2, "REPLAYED_RECEIPT")

    def test_post_approval_content_tampering_is_blocked(self) -> None:
        approved_call = {
            "tool": "edit_file",
            "role": "implementer",
            "path": "src/config.py",
            "content": "ALLOW_EXTERNAL = False\n",
        }
        receipt = issue_approval_receipt("rcpt-002", approved_call)

        tampered_call = dict(approved_call, content="ALLOW_EXTERNAL = True\n")
        ok, code, _ = self.fw.verify_call(tampered_call, receipt)
        self.assertFalse(ok)
        self.assertEqual(code, "DIGEST_MISMATCH")

    def test_path_traversal_and_outside_root_blocked(self) -> None:
        traversal_call = {
            "tool": "read_file",
            "role": "implementer",
            "path": "src/../../etc/passwd",
        }
        ok, code, _ = self.fw.verify_call(traversal_call)
        self.assertFalse(ok)
        self.assertEqual(code, "PATH_TRAVERSAL")

        outside_call = {
            "tool": "read_file",
            "role": "implementer",
            "path": "secrets/keys.json",
        }
        ok2, code2, _ = self.fw.verify_call(outside_call)
        self.assertFalse(ok2)
        self.assertEqual(code2, "OUTSIDE_ALLOWED_ROOT")

    def test_unauthorized_role_blocked(self) -> None:
        call = {
            "tool": "read_file",
            "role": "guest",
            "path": "src/app.py",
        }
        ok, code, _ = self.fw.verify_call(call)
        self.assertFalse(ok)
        self.assertEqual(code, "UNAUTHORIZED_ROLE")

    def test_trace_span_deduplicates_overlapping_children_and_tokens(self) -> None:
        # root: [0, 1000] ms, total_tokens=1500 (含兩個子 span 的 400 + 700 = 1100，自身耗用 400)
        # child1: [100, 500] ms (400ms), tokens=400
        # child2: [300, 800] ms (500ms, 與 child1 重疊 [300, 500]), tokens=700, status=error
        # 子區間聯集為 [100, 800] = 700ms，因此 root 的 exclusive_duration_ms 應為 1000 - 700 = 300ms
        spans = [
            {
                "span_id": "root",
                "parent_id": None,
                "name": "agent_turn",
                "start_ms": 0,
                "end_ms": 1000,
                "total_tokens": 1500,
                "status": "ok",
            },
            {
                "span_id": "child-1",
                "parent_id": "root",
                "name": "retrieval",
                "start_ms": 100,
                "end_ms": 500,
                "total_tokens": 400,
                "status": "ok",
            },
            {
                "span_id": "child-2",
                "parent_id": "root",
                "name": "tool_retry_loop",
                "start_ms": 300,
                "end_ms": 800,
                "total_tokens": 700,
                "status": "error",
            },
        ]
        report = analyze_trace_spans(spans)
        by_id = {s["span_id"]: s for s in report["spans"]}

        self.assertEqual(by_id["root"]["inclusive_duration_ms"], 1000.0)
        self.assertEqual(by_id["root"]["exclusive_duration_ms"], 300.0)
        self.assertEqual(by_id["root"]["exclusive_tokens"], 400)
        self.assertEqual(by_id["child-1"]["exclusive_tokens"], 400)
        self.assertEqual(by_id["child-2"]["exclusive_tokens"], 700)

        self.assertEqual(report["raw_sum_tokens"], 2600)
        self.assertEqual(report["deduplicated_total_tokens"], 1500)
        self.assertEqual(report["first_error_span_id"], "child-2")
        self.assertEqual(report["max_exclusive_token_span_id"], "child-2")
        self.assertEqual(report["max_exclusive_duration_span_id"], "child-2")

    def test_request_digest_normalizes_windows_and_posix_slashes(self) -> None:
        c1 = {"tool": "write_file", "role": "implementer", "path": r"src\sub\a.py", "content": "x"}
        c2 = {"tool": "write_file", "role": "implementer", "path": "src/sub/a.py", "content": "x"}
        self.assertEqual(compute_request_digest(c1), compute_request_digest(c2))


if __name__ == "__main__":
    unittest.main()
