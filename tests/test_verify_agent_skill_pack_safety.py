#!/usr/bin/env python3
"""tests/test_verify_agent_skill_pack_safety.py — verify_agent_skill_pack_safety.py 單元測試 (T-20261108-04)"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_agent_skill_pack_safety as guard  # noqa: E402


class TestVerifyAgentSkillPackSafety(unittest.TestCase):
    def test_default_suite_passes(self) -> None:
        suite = guard.default_suite()
        errors = guard.validate_suite(suite)
        self.assertEqual(errors, [])

    def test_skillpack_001_blocks_bypass_sandbox_flags_and_unsafe_live_mode(self) -> None:
        suite = copy.deepcopy(guard.default_suite())
        suite["packs"][0]["cli_invocations"].append(
            "codex --dangerously-bypass-approvals-and-sandbox exec 'apply edits'"
        )
        suite["packs"][0]["env_overrides"]["IMPECCABLE_LIVE_COPY_AGENT"] = "auto"
        errors = guard.validate_suite(suite)
        self.assertTrue(any("SKILLPACK-001" in e and "--dangerously-bypass-approvals-and-sandbox" in e for e in errors))
        self.assertTrue(any("SKILLPACK-001" in e and "IMPECCABLE_LIVE_COPY_AGENT" in e for e in errors))

    def test_skillpack_002_requires_telemetry_off_and_hook_review(self) -> None:
        suite = copy.deepcopy(guard.default_suite())
        suite["packs"][1]["config"]["telemetry"] = True
        suite["packs"][1]["config"]["hook_reviewed"] = False
        errors = guard.validate_suite(suite)
        self.assertTrue(any("SKILLPACK-002" in e and "telemetry" in e for e in errors))
        self.assertTrue(any("SKILLPACK-002" in e and "hook_reviewed" in e for e in errors))

    def test_skillpack_003_enforces_human_publish_and_placeholder(self) -> None:
        suite = copy.deepcopy(guard.default_suite())
        suite["packs"][2]["human_publish_only"] = False
        suite["packs"][2]["unknown_metric_placeholder"] = "10,000+"
        errors = guard.validate_suite(suite)
        self.assertTrue(any("SKILLPACK-003" in e and "human_publish_only" in e for e in errors))
        self.assertTrue(any("SKILLPACK-003" in e and "unknown_metric_placeholder" in e for e in errors))

    def test_skillpack_004_requires_deterministic_tools_and_blocks_overclaims(self) -> None:
        suite = copy.deepcopy(guard.default_suite())
        suite["packs"][3]["deterministic_tools"] = []
        suite["packs"][3]["claims"] = ["This humanizer is 100% undetectable by GPTZero"]
        errors = guard.validate_suite(suite)
        self.assertTrue(any("SKILLPACK-004" in e and "deterministic_tools" in e for e in errors))
        self.assertTrue(any("SKILLPACK-004" in e and "100% undetectable" in e for e in errors))

    def test_cli_json_and_custom_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "suite.json"
            cfg_path.write_text(json.dumps(guard.default_suite(), ensure_ascii=False), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(REPO_ROOT / "tools" / "verify_agent_skill_pack_safety.py"), "--config", str(cfg_path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["pack_count"], 5)


if __name__ == "__main__":
    unittest.main()
