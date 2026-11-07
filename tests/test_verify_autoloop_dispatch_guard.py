"""
tests/test_verify_autoloop_dispatch_guard.py
測試 tools/verify_autoloop_dispatch_guard.py 的四層派工安全防線（AUTOLOOP-001 ~ 004）。
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import verify_autoloop_dispatch_guard as vadg  # noqa: E402


class VerifyAutoloopDispatchGuardTest(unittest.TestCase):
    def test_default_clean_bundle_passes(self) -> None:
        bundle = vadg.default_clean_bundle()
        self.assertEqual(vadg.audit_bundle(bundle), [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = vadg.main([])
        self.assertEqual(rc, 0)
        self.assertIn("[PASS]", out.getvalue())

    def test_autoloop_001_detects_forbidden_event_fields_and_unsafe_chars(self) -> None:
        events = [
            {"id": "ev-1", "type": "issues.opened", "cwd": "/tmp/pwn", "access": "full"},
            {"id": "bad;rm -rf /", "type": "issues.opened"},
        ]
        findings = vadg.check_event_payloads(events)
        rules = [f["rule_id"] for f in findings]
        self.assertEqual(rules, ["AUTOLOOP-001", "AUTOLOOP-001"])
        self.assertIn("access, cwd", findings[0]["message"])

    def test_autoloop_002_detects_untrusted_prompt_interpolation_and_unsafe_resume(self) -> None:
        rules = [
            {
                "name": "bad-prompt",
                "when": {"source": "github"},
                "access": "full",
                "resume": True,
                "prompt": "請修復此問題：{title}\n{issue_body}",
            }
        ]
        findings = vadg.check_dispatch_rules(rules)
        self.assertEqual(len(findings), 3)
        self.assertTrue(all(f["rule_id"] == "AUTOLOOP-002" for f in findings))

    def test_autoloop_003_detects_hop_reset_and_unthrottled_overflow(self) -> None:
        chain = [
            {"step_id": "s1", "hop": 2, "via": "event", "dispatched": True},
            {"step_id": "s2", "hop": 0, "via": "ask", "dispatched": True},
            {"step_id": "s3", "hop": 9, "via": "event", "dispatched": True},
        ]
        findings = vadg.check_hop_chain(chain, max_hops=8)
        self.assertEqual(len(findings), 2)
        self.assertIn("未遞增或被清零", findings[0]["message"])
        self.assertIn("超過熔斷上限", findings[1]["message"])

    def test_autoloop_004_detects_self_approval_pr_checkout_and_acl_leak(self) -> None:
        isolation = {
            "worker_tools": ["read_file", "mcp__autoloop__answer"],
            "delivery": {"checkout_pr_code": True, "allow_octopus_merge": True},
            "windows_data_dir_acl": ["CURRENT_USER", "SYSTEM", "CodexSandboxUser"],
        }
        findings = vadg.check_worker_and_delivery_isolation(isolation)
        self.assertEqual(len(findings), 4)
        self.assertTrue(all(f["rule_id"] == "AUTOLOOP-004" for f in findings))

    def test_cli_json_output_and_invalid_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_cfg = Path(tmp) / "bad.json"
            bad_bundle = vadg.default_clean_bundle()
            bad_bundle["events"][0]["agent"] = "claude"
            bad_cfg.write_text(json.dumps(bad_bundle), encoding="utf-8")

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = vadg.main(["--config", str(bad_cfg), "--json"])
            self.assertEqual(rc, 1)
            parsed = json.loads(out.getvalue())
            self.assertFalse(parsed["passed"])
            self.assertEqual(parsed["findings"][0]["rule_id"], "AUTOLOOP-001")


if __name__ == "__main__":
    unittest.main()
