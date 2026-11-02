"""tools/verify_tool_fallback_matrix.py 的單元測試。只用暫存檔與記憶體內的假設定。"""

import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "verify_tool_fallback_matrix.py"
sys.path.insert(0, str(TOOL.parent))
import verify_tool_fallback_matrix as v  # noqa: E402


def good():
    return copy.deepcopy(v.EXAMPLE)


def codes(data):
    return sorted({f.code for f in v.check(data)})


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = v.main(argv)
    return rc, out.getvalue(), err.getvalue()


class ValidConfigTest(unittest.TestCase):
    def test_example_passes(self):
        self.assertEqual(v.check(good()), [])

    def test_example_printed_by_cli_passes_through_file(self):
        rc, out, _ = run_main(["--print-example"])
        self.assertEqual(rc, 0)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.json"
            p.write_text(out, encoding="utf-8")
            rc, out2, _ = run_main([str(p)])
            self.assertEqual(rc, 0, out2)
            self.assertIn("[PASS]", out2)

    def test_utf8_bom_file_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.json"
            p.write_bytes(b"\xef\xbb\xbf" + json.dumps(good(), ensure_ascii=False).encode("utf-8"))
            self.assertEqual(run_main([str(p)])[0], 0)


class RoadTest(unittest.TestCase):
    def test_each_required_road_missing_fails(self):
        self.assertEqual(set(v.REQUIRED_ROADS), {"video", "image", "code", "document", "dispatcher"})
        for rid in ("video", "image", "code", "document", "dispatcher"):
            with self.subTest(road=rid):
                d = good()
                del d["roads"][rid]
                self.assertIn("road-missing", codes(d))

    def test_misspelled_fallback_key_is_caught_not_silent(self):
        # 原作踩過的坑：備援鍵名打錯，主力掛掉時從未切換。
        for bad in ("fallback", "fallbaks", "fallback_tools", "Fallbacks"):
            with self.subTest(key=bad):
                d = good()
                d["roads"]["video"][bad] = d["roads"]["video"].pop("fallbacks")
                c = codes(d)
                self.assertIn("unknown-key", c)
                self.assertIn("no-fallback", c)
                self.assertIn("missing-key", c)

    def test_did_you_mean_suggests_correct_key(self):
        d = good()
        d["roads"]["video"]["fallback"] = d["roads"]["video"].pop("fallbacks")
        msgs = " ".join(f.msg for f in v.check(d) if f.code == "unknown-key")
        self.assertIn("fallbacks", msgs)

    def test_empty_fallbacks_fails(self):
        d = good()
        d["roads"]["image"]["fallbacks"] = []
        self.assertIn("no-fallback", codes(d))

    def test_fallbacks_not_a_list_fails(self):
        d = good()
        d["roads"]["image"]["fallbacks"] = "canva-template"
        self.assertIn("bad-type", codes(d))

    def test_empty_primary_fails(self):
        d = good()
        d["roads"]["image"]["primary"] = []
        self.assertIn("bad-type", codes(d))

    def test_dangling_fallback_reference_fails(self):
        d = good()
        d["roads"]["video"]["fallbacks"] = ["heygenn"]
        self.assertIn("dangling-ref", codes(d))

    def test_dangling_primary_reference_fails(self):
        d = good()
        d["roads"]["video"]["primary"] = ["nope"]
        self.assertIn("dangling-ref", codes(d))

    def test_fallback_equal_to_primary_fails(self):
        d = good()
        d["roads"]["video"]["fallbacks"] = ["url-to-video"]
        self.assertIn("self-fallback", codes(d))

    def test_duplicate_in_fallbacks_fails(self):
        d = good()
        d["roads"]["document"]["fallbacks"] = ["notion-page", "notion-page"]
        self.assertIn("self-fallback", codes(d))

    def test_same_provider_fallback_fails(self):
        d = good()
        d["tools"]["heygen"]["provider"] = d["tools"]["url-to-video"]["provider"]
        self.assertIn("same-provider", codes(d))

    def test_one_independent_fallback_is_enough_for_provider_rule(self):
        d = good()
        d["tools"]["whisper-local"]["provider"] = d["tools"]["claude-code"]["provider"]
        # document 路徑：備援 whisper-local（同 provider）+ notion-page（不同）→ 通過
        self.assertNotIn("same-provider", codes(d))

    def test_disabled_fallback_fails(self):
        d = good()
        d["tools"]["heygen"]["enabled"] = False
        self.assertIn("tool-disabled", codes(d))

    def test_missing_healthcheck_on_fallback_and_primary_fails(self):
        for tid in ("heygen", "url-to-video"):
            with self.subTest(tool=tid):
                d = good()
                del d["tools"][tid]["healthcheck"]
                self.assertIn("no-healthcheck", codes(d))

    def test_blank_healthcheck_fails(self):
        d = good()
        d["tools"]["heygen"]["healthcheck"] = "  "
        self.assertIn("bad-type", codes(d))

    def test_unused_tool_without_healthcheck_is_not_flagged(self):
        d = good()
        d["tools"]["spare"] = {"provider": "x", "side_effect": "none", "requires_human_confirm": False}
        self.assertEqual(v.check(d), [])


class GatewayTest(unittest.TestCase):
    def gw(self, allowlist):
        d = good()
        d["gateways"][0]["allowlist"] = allowlist
        return d

    def test_username_entry_fails(self):
        self.assertIn("gateway-id", codes(self.gw([{"username": "going_li"}])))

    def test_bare_string_entries_fail(self):
        for entry in ("going_li", "@going_li", "123456789012345678"):
            with self.subTest(entry=entry):
                self.assertIn("gateway-id", codes(self.gw([entry])))

    def test_username_alongside_user_id_still_fails(self):
        self.assertIn("gateway-id", codes(self.gw([{"user_id": "123456789012", "username": "x"}])))

    def test_non_numeric_or_wildcard_id_fails(self):
        for uid in ("abc123456", "*", "@123456789", "12 345 678", "", "1234"):
            with self.subTest(uid=uid):
                self.assertIn("gateway-id", codes(self.gw([{"user_id": uid}])))

    def test_integer_id_fails_because_json_numbers_lose_precision(self):
        self.assertIn("gateway-id", codes(self.gw([{"user_id": 123456789012345678}])))

    def test_empty_allowlist_fails(self):
        self.assertIn("gateway-id", codes(self.gw([])))

    def test_missing_user_id_fails(self):
        self.assertIn("gateway-id", codes(self.gw([{"note": "x"}])))

    def test_no_gateways_declared_fails(self):
        d = good()
        d["gateways"] = []
        self.assertIn("bad-type", codes(d))
        del d["gateways"]
        self.assertIn("missing-key", codes(d))

    def test_one_bad_entry_among_good_ones_fails(self):
        self.assertIn("gateway-id", codes(self.gw([{"user_id": "123456789012"}, {"username": "x"}])))


class ConfirmFlagTest(unittest.TestCase):
    def test_external_send_without_confirm_fails(self):
        d = good()
        d["tools"]["line-send"]["requires_human_confirm"] = False
        self.assertIn("confirm-missing", codes(d))

    def test_external_send_with_confirm_key_removed_fails(self):
        d = good()
        del d["tools"]["line-send"]["requires_human_confirm"]
        c = codes(d)
        self.assertIn("confirm-missing", c)
        self.assertIn("missing-key", c)

    def test_payment_without_confirm_fails(self):
        d = good()
        d["tools"]["stripe"] = {"provider": "stripe", "side_effect": "payment", "requires_human_confirm": False, "healthcheck": "x"}
        self.assertIn("confirm-missing", codes(d))

    def test_string_true_is_not_true(self):
        d = good()
        d["tools"]["line-send"]["requires_human_confirm"] = "true"
        c = codes(d)
        self.assertIn("bad-type", c)
        self.assertIn("confirm-missing", c)

    def test_payment_with_confirm_passes(self):
        d = good()
        d["tools"]["stripe"] = {"provider": "stripe", "side_effect": "payment", "requires_human_confirm": True, "healthcheck": "x"}
        self.assertEqual(v.check(d), [])

    def test_unknown_side_effect_value_fails(self):
        d = good()
        d["tools"]["line-send"]["side_effect"] = "external-send"
        self.assertIn("bad-type", codes(d))

    def test_mislabelled_outbound_tool_is_caught(self):
        for tid, desc in (("line-send2", ""), ("x", "GAS 自動發送節慶小卡"), ("y", "Send newsletter by email"), ("billing-bot", "")):
            with self.subTest(tid=tid, desc=desc):
                d = good()
                d["tools"][tid] = {"provider": "p", "side_effect": "none", "requires_human_confirm": False, "description": desc}
                self.assertIn("side-effect-lie", codes(d))

    def test_innocent_words_are_not_flagged(self):
        d = good()
        d["tools"]["payload-parser"] = {"provider": "p", "side_effect": "none", "requires_human_confirm": False, "description": "postgres payload viewer"}
        self.assertNotIn("side-effect-lie", codes(d))


class ShapeTest(unittest.TestCase):
    def test_empty_object_fails(self):
        self.assertEqual(codes({}), ["file-empty"])

    def test_top_level_list_fails(self):
        self.assertIn("bad-type", codes([]))

    def test_unknown_top_level_and_tool_keys_fail(self):
        d = good()
        d["road"] = {}
        d["tools"]["heygen"]["requires_human_confirmation"] = True
        self.assertEqual(sum(f.code == "unknown-key" for f in v.check(d)), 2)

    def test_tools_must_be_nonempty(self):
        d = good()
        d["tools"] = {}
        self.assertIn("bad-type", codes(d))

    def test_garbage_types_do_not_crash(self):
        for junk in (None, 1, "x", [1], {"a": 1}, True):
            with self.subTest(junk=junk):
                for key in ("tools", "roads", "gateways"):
                    d = good()
                    d[key] = junk
                    self.assertTrue(v.check(d))
        d = good()
        d["roads"]["video"] = None
        d["tools"]["heygen"] = []
        d["gateways"][0] = "x"
        self.assertTrue(v.check(d))


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def write(self, text, name="m.json", raw=None):
        p = self.dir / name
        if raw is not None:
            p.write_bytes(raw)
        else:
            p.write_text(text, encoding="utf-8")
        return str(p)

    def test_no_argument_is_not_a_pass(self):
        rc, _, err = run_main([])
        self.assertEqual(rc, 2)
        self.assertIn("沒有指定", err)

    def test_missing_file_exit_2(self):
        self.assertEqual(run_main([str(self.dir / "nope.json")])[0], 2)

    def test_directory_instead_of_file_exit_2(self):
        self.assertEqual(run_main([str(self.dir)])[0], 2)

    def test_invalid_json_exit_2(self):
        self.assertEqual(run_main([self.write("{not json")])[0], 2)

    def test_empty_file_exit_2(self):
        self.assertEqual(run_main([self.write("")])[0], 2)

    def test_non_utf8_exit_2(self):
        self.assertEqual(run_main([self.write("", raw=b"\xff\xfe\x00bad")])[0], 2)

    def test_empty_object_exit_1(self):
        self.assertEqual(run_main([self.write("{}")])[0], 1)

    def test_top_level_not_an_object_exit_2(self):
        # 文件寫「頂層不是物件 = 輸入無法使用 = 2」；曾經實際回 1。
        for text in ("null", "[]", '"x"', "5", "true", "[{}]"):
            with self.subTest(text=text):
                rc, out, err = run_main([self.write(text)])
                self.assertEqual(rc, 2)
                self.assertIn("JSON 物件", err)
                self.assertNotIn("[PASS]", out)

    def test_top_level_not_an_object_exit_2_via_subprocess(self):
        for text in ("[]", '"x"', "5"):
            with self.subTest(text=text):
                p = self.write(text)
                self.assertEqual(subprocess.run([sys.executable, str(TOOL), p], capture_output=True, timeout=60).returncode, 2)

    def test_invalid_config_exit_1_and_reports_fail(self):
        d = good()
        del d["roads"]["video"]
        rc, out, _ = run_main([self.write(json.dumps(d))])
        self.assertEqual(rc, 1)
        self.assertIn("[FAIL]", out)
        self.assertIn("road-missing", out)

    def test_duplicate_json_key_exit_1(self):
        text = json.dumps(good(), ensure_ascii=False)
        # 在 video 路徑再塞一個重複的 fallbacks（後者悄悄蓋掉前者）。
        text = text.replace('"fallbacks": ["heygen"]', '"fallbacks": ["heygen"], "fallbacks": []', 1)
        self.assertIn('"fallbacks": []', text)
        rc, out, _ = run_main([self.write(text)])
        self.assertEqual(rc, 1)
        self.assertIn("duplicate-key", out)

    def test_json_output_mode(self):
        d = good()
        d["gateways"][0]["allowlist"] = [{"username": "x"}]
        rc, out, _ = run_main([self.write(json.dumps(d)), "--json"])
        self.assertEqual(rc, 1)
        payload = json.loads(out)
        self.assertGreaterEqual(payload["errors"], 1)
        self.assertEqual(payload["findings"][0]["level"], "ERROR")

    def test_subprocess_cp950_stdout_does_not_crash(self):
        env = dict(os.environ, PYTHONIOENCODING="cp950", PYTHONUTF8="0")
        d = good()
        del d["roads"]["video"]
        p = self.write(json.dumps(d))
        r = subprocess.run([sys.executable, str(TOOL), p], capture_output=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 1, r.stderr.decode("utf-8", "replace"))
        self.assertNotIn(b"Traceback", r.stderr)

    def test_subprocess_exit_codes_match_docstring(self):
        p = self.write(json.dumps(good()))
        self.assertEqual(subprocess.run([sys.executable, str(TOOL), p], capture_output=True, timeout=60).returncode, 0)
        self.assertEqual(subprocess.run([sys.executable, str(TOOL)], capture_output=True, timeout=60).returncode, 2)


class SpecDocConsistencyTest(unittest.TestCase):
    """規範文件第 7 節講的檢查項目，要和驗證器實際行為對得上。"""

    DOC = TOOL.parent.parent / "docs" / "multi-agent-parallel-dispatch-spec.md"

    def test_doc_names_every_required_road_and_the_cli_flags(self):
        text = self.DOC.read_text(encoding="utf-8")
        for rid in v.REQUIRED_ROADS:
            self.assertIn(f"`{rid}`", text)
        self.assertIn("--print-example", text)
        self.assertIn("tools/verify_tool_fallback_matrix.py", text)

    def test_doc_exit_code_claim_matches_behavior(self):
        text = self.DOC.read_text(encoding="utf-8")
        self.assertIn("0 通過、1 有錯、2 輸入無法使用（沒給檔、讀不到、非 JSON、頂層不是物件）", text)
        self.assertEqual(run_main(["--print-example"])[0], 0)
        self.assertEqual(run_main([])[0], 2)


if __name__ == "__main__":
    unittest.main()
