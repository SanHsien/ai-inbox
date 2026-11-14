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
    @classmethod
    def setUpClass(cls):
        cls.temp_root = Path(".work-tmp")
        cls.created_temp_root = not cls.temp_root.exists()
        cls.temp_root.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if cls.created_temp_root:
            cls.temp_root.rmdir()

    def test_all_template_fields_share_injection_checks(self):
        for field in ("prompt", "command", "cwd", "program", "to", "skill", "args"):
            for token in ("{body}", "{title}", "{prompt}", "{unknown}", "{id.attr}", "{id[0]}", "{id!r}", "{id:{body}}", "{"):
                bundle = vadg.default_clean_bundle()
                bundle["rules"][0][field] = [token] if field == "args" else token
                with self.subTest(field=field, token=token):
                    self.assertTrue(vadg.audit_bundle(bundle))
        bundle = vadg.default_clean_bundle()
        bundle["rules"][0]["command"] = "echo {type} {id} {link} {context_file}"
        self.assertEqual(vadg.audit_bundle(bundle), [])

    def test_hops_require_parent_plus_one(self):
        for hops in ((1, 7), (1, 1), (1, 0), (True, 2)):
            b = vadg.default_clean_bundle()
            b["hop_chain"] = [{"hop": n} for n in hops]
            self.assertTrue(vadg.audit_bundle(b))
        self.assertEqual(vadg.check_hop_chain([{"hop": 8}, {"hop": 9, "dispatched": False}]), [])
        self.assertTrue(vadg.check_hop_chain([{"hop": 8}, {"hop": 9, "dispatched": True}]))

    def test_acl_is_explicit_allowlist(self):
        for acl in (["CURRENT_USER", "SYSTEM", "Administrators"], ["Everyone"], [], None, "SYSTEM", [3]):
            b = vadg.default_clean_bundle()
            b["isolation"]["windows_data_dir_acl"] = acl
            self.assertTrue(vadg.audit_bundle(b))

    def test_missing_empty_and_bad_schema_fail_closed(self):
        invalid = [None, [], {}, "", {"events": []}]
        for key in ("events", "rules", "hop_chain", "isolation"):
            for value in (None, [], {}, "bad", [None]):
                b = vadg.default_clean_bundle(); b[key] = value; invalid.append(b)
            b = vadg.default_clean_bundle(); del b[key]; invalid.append(b)
        for path, value in ((('max_hops',), True), (('max_hops',), "8"),
                            (('events',0,'id'), None), (('events',0,'link'), 'https://x/;evil'),
                            (('rules',0,'resume'), 'false'), (('rules',0,'when'), []),
                            (('rules',0,'command'), 3), (('hop_chain',0,'dispatched'), 'false'),
                            (('isolation','delivery'), {}), (('isolation','worker_tools'), 'read_file')):
            b = vadg.default_clean_bundle(); obj = b
            for key in path[:-1]: obj = obj[key]
            obj[path[-1]] = value; invalid.append(b)
        with tempfile.TemporaryDirectory(dir=".work-tmp") as tmp:
            p = Path(tmp) / "bundle.json"
            for b in invalid:
                with self.subTest(bundle=b), contextlib.redirect_stdout(io.StringIO()):
                    self.assertTrue(vadg.audit_bundle(b))
                    p.write_text(json.dumps(b), encoding="utf-8")
                    self.assertEqual(vadg.main(["--config", str(p)]), 1)
            for text in ('', '{'):
                p.write_text(text, encoding="utf-8")
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(vadg.main(["--config", str(p)]), 1)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(vadg.main(["--config", str(p)+'missing']), 1)

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
        self.assertEqual(len(findings), 3)
        self.assertIn("未遞增或被清零", findings[0]["message"])
        self.assertIn("超過熔斷上限", findings[2]["message"])

    def test_autoloop_004_detects_self_approval_pr_checkout_and_acl_leak(self) -> None:
        isolation = {
            "worker_tools": ["read_file", "mcp__autoloop__answer"],
            "delivery": {"checkout_pr_code": True, "allow_octopus_merge": True},
            "windows_data_dir_acl": ["CURRENT_USER", "SYSTEM", "CodexSandboxUser"],
        }
        findings = vadg.check_worker_and_delivery_isolation(isolation)
        self.assertEqual(len(findings), 4)
        self.assertTrue(all(f["rule_id"] == "AUTOLOOP-004" for f in findings))

    def _cli_rc(self, bundle) -> int:
        with tempfile.TemporaryDirectory(dir=".work-tmp") as tmp:
            p = Path(tmp) / "b.json"
            p.write_text(json.dumps(bundle), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                return vadg.main(["--config", str(p)])

    def test_round2_event_keys_case_and_nesting(self) -> None:
        for key in ("CWD", "Access", " agent ", "ＣＷＤ"):
            b = vadg.default_clean_bundle(); b["events"][0][key] = "x"
            with self.subTest(key=key):
                self.assertEqual(self._cli_rc(b), 1)
        for nested in ({"payload": {"cwd": "/x"}}, {"payload": {"Meta": [{"COMMAND": "x"}]}}):
            b = vadg.default_clean_bundle(); b["events"][0].update(nested)
            with self.subTest(nested=nested):
                self.assertEqual(self._cli_rc(b), 1)

    def test_round2_max_hops_capped_at_spec_limit(self) -> None:
        b = vadg.default_clean_bundle(); b["max_hops"] = 99
        b["hop_chain"] = [{"hop": i} for i in range(1, 40)]
        self.assertEqual(self._cli_rc(b), 1)
        b["max_hops"] = 9
        self.assertEqual(self._cli_rc(b), 1)
        self.assertTrue(vadg.check_hop_chain([{"hop": 1}], max_hops=99))
        self.assertTrue(vadg.check_hop_chain([{"hop": 9}], max_hops=99))
        b = vadg.default_clean_bundle(); b["max_hops"] = 8
        self.assertEqual(self._cli_rc(b), 0)
        b["max_hops"] = 3
        self.assertEqual(self._cli_rc(b), 1)

    def test_round2_source_allowlist_and_case(self) -> None:
        for src in ("GitHub", " GITLAB ", "slack", "discord", ""):
            b = vadg.default_clean_bundle()
            b["rules"][0]["when"]["source"] = src
            b["rules"][0]["access"] = "full"; b["rules"][0]["resume"] = True
            with self.subTest(src=src):
                self.assertEqual(self._cli_rc(b), 1)
        for src in ("slack", "Slack"):
            b = vadg.default_clean_bundle(); b["rules"][0]["when"]["source"] = src
            with self.subTest(src=src, mode="no-full"):
                self.assertEqual(self._cli_rc(b), 1)
        b = vadg.default_clean_bundle()
        b["rules"][0]["when"]["source"] = "github"; b["rules"][0]["access"] = "FULL"; b["rules"][0]["resume"] = True
        self.assertEqual(self._cli_rc(b), 1)
        for src in sorted(vadg.ALLOWED_SOURCES):
            b = vadg.default_clean_bundle(); b["rules"][0]["when"]["source"] = src
            with self.subTest(src=src, mode="allowed"):
                self.assertEqual(self._cli_rc(b), 0)

    def test_round2_self_approval_tool_names_case_insensitive(self) -> None:
        for name in ("Autoloop_Answer", " ANSWER_CARD ", "MCP__AutoLoop__Answer", "Agent-Autoloop Answer"):
            b = vadg.default_clean_bundle(); b["isolation"]["worker_tools"] = ["read_file", name]
            with self.subTest(name=name):
                self.assertEqual(self._cli_rc(b), 1)

    def test_cli_json_output_and_invalid_config_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=".work-tmp") as tmp:
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
