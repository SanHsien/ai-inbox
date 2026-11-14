#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
單元測試：test_verify_tool_call_firewall.py
驗證單次審批收據防火牆（防審批後竄改、防收據重放、防路徑穿越）與 Agent Trace 父子 Span 去重計算。
"""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
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
    @classmethod
    def setUpClass(cls):
        cls.temp_root = Path(".work-tmp")
        cls.created_temp_root = not cls.temp_root.exists()
        cls.temp_root.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if cls.created_temp_root:
            cls.temp_root.rmdir()

    def setUp(self) -> None:
        self.fw = ToolCallFirewall(
            allowed_roles=("implementer", "maintainer"),
            allowed_roots=("src/", "docs/", "tools/"),
        )

    def test_content_hash_spoof_and_digest_recomputation(self):
        from verify_tool_call_firewall import compute_content_sha256
        call = dict(tool="write_file", role="implementer", path="src/x", content="safe",
                    content_sha256=compute_content_sha256("safe"))
        receipt = issue_approval_receipt("hash", call)
        evil = dict(call, content="evil")
        self.assertNotEqual(compute_request_digest(call), compute_request_digest(evil))
        self.assertFalse(self.fw.verify_call(evil, receipt)[0])
        mismatched = dict(call, content_sha256="0" * 64)
        self.assertEqual(self.fw.verify_call(mismatched, receipt)[1], "CONTENT_HASH_MISMATCH")
        self.assertTrue(self.fw.verify_call(call, receipt)[0])

    def test_absolute_drive_unc_and_unknown_tools_blocked(self):
        call = dict(tool="read_file", role="implementer", path="src/x")
        for path in ("/src/x", "C:/src/x", "C:src/x", "\\\\server/share/src/x", "\\src/x"):
            with self.subTest(path=path):
                self.assertEqual(self.fw.verify_call(dict(call, path=path))[1], "ABSOLUTE_PATH")
        for tool in ("Write", "Read", "unknown", "WRITE_FILE"):
            self.assertEqual(self.fw.verify_call(dict(call, tool=tool))[1], "UNKNOWN_TOOL")
        self.assertEqual(self.fw.verify_call(dict(call, tool="write_file", content="x"))[1], "MISSING_RECEIPT")
        write = dict(call, tool="write_file", content="x")
        invalid_receipt = issue_approval_receipt("r", write)
        invalid_receipt["receipt_id"] = 123
        self.assertEqual(self.fw.verify_call(write, invalid_receipt)[1], "INVALID_RECEIPT")


    def test_resolved_path_escape_and_invalid_envelopes(self):
        call = dict(tool="read_file", role="implementer", path="src/link/x")
        real_resolve = Path.resolve
        target = self.fw.workspace_root / "src/link/x"
        def resolve(path, *args, **kwargs):
            if path == target:
                return self.fw.workspace_root.parent / "outside/x"
            return real_resolve(path, *args, **kwargs)
        with patch.object(Path, "resolve", resolve):
            self.assertEqual(self.fw.verify_call(call)[1], "OUTSIDE_ALLOWED_ROOT")
        for invalid in (None, {}, dict(call, path=1), dict(call, content=[])):
            self.assertFalse(self.fw.verify_call(invalid)[0])
        with self.assertRaises(ValueError):
            ToolCallFirewall(allowed_roots=[])

    def test_cli_fail_closed_schema_empty_and_missing(self):
        from verify_tool_call_firewall import main
        from contextlib import redirect_stdout
        import io
        with tempfile.TemporaryDirectory(dir=".work-tmp") as tmp, redirect_stdout(io.StringIO()):
            p = Path(tmp) / "calls.json"
            for data in ({}, [], {"invocations": []}, {"invocations": [None]},
                         {"invocations": [{"call": {}}], "allowed_roots": []},
                         {"invocations": [{"call": {}}], "allowed_roles": "all"}):
                p.write_text(json.dumps(data), encoding="utf-8")
                self.assertNotEqual(main(["--verify-calls", str(p)]), 0)
            p.write_text("", encoding="utf-8")
            self.assertNotEqual(main(["--verify-calls", str(p)]), 0)
            self.assertNotEqual(main(["--verify-calls", str(p)+"missing"]), 0)
            self.assertNotEqual(main([]), 0)

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
