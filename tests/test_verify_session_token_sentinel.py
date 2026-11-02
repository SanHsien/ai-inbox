"""tools/verify_session_token_sentinel.py 的單元與子程序測試。

hook 的測試一律用子程序從真正的 stdin 餵假資料，確認結束碼與輸出。只用假資料。
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "verify_session_token_sentinel.py"
sys.path.insert(0, str(ROOT / "tools"))

import verify_session_token_sentinel as S  # noqa: E402


def usage_line(inp=0, read=0, create=0, **extra):
    msg = {"role": "assistant", "usage": {"input_tokens": inp, "cache_read_input_tokens": read,
                                          "cache_creation_input_tokens": create}}
    return json.dumps({"type": "assistant", "message": msg, **extra})


def write_lines(path, lines):
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_tool(*args, stdin=None, env=None):
    full_env = dict(os.environ)
    full_env.pop("LONG_CHAT_TOKENS", None)
    full_env.pop("LONG_CHAT_STEP", None)
    if env:
        full_env.update(env)
    return subprocess.run([sys.executable, "-I", str(TOOL), *args], input=stdin, capture_output=True,
                          env=full_env, timeout=60)


class TailAndUsageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "t.jsonl"

    def test_sums_three_fields_of_latest_usage(self):
        write_lines(self.path, [usage_line(1, 1000000, 1), usage_line(10, 20000, 300)])
        r = S.measure_file(self.path)
        self.assertEqual((r.status, r.tokens), ("ok", 20310))

    def test_missing_fields_count_as_zero(self):
        write_lines(self.path, [json.dumps({"message": {"usage": {"input_tokens": 5}}})])
        self.assertEqual(S.measure_file(self.path).tokens, 5)

    def test_skips_trailing_lines_without_usage(self):
        write_lines(self.path, [usage_line(7, 0, 0), json.dumps({"type": "user", "message": {"content": "hi"}}), ""])
        self.assertEqual(S.measure_file(self.path).tokens, 7)

    def test_reads_only_last_2mb_and_prefers_newest(self):
        junk = json.dumps({"type": "user", "message": {"content": "x" * 1000}})
        lines = [usage_line(900000)] + [junk] * 2100 + [usage_line(160000)]
        write_lines(self.path, lines)
        self.assertGreater(self.path.stat().st_size, S.DEFAULT_TAIL_BYTES)
        self.assertEqual(S.DEFAULT_TAIL_BYTES, 2_000_000)
        r = S.measure_file(self.path)
        self.assertEqual(r.tokens, 160000)

    def test_old_usage_outside_window_is_not_found(self):
        junk = json.dumps({"type": "user", "message": {"content": "x" * 1000}})
        write_lines(self.path, [usage_line(900000)] + [junk] * 2100)
        r = S.measure_file(self.path)
        self.assertEqual(r.status, "no_usage")
        self.assertIsNone(r.tokens)

    def test_single_giant_line_exhausts_window(self):
        giant = json.dumps({"type": "user", "message": {"content": "x" * 2_100_000}})
        write_lines(self.path, [usage_line(900000), giant])
        r = S.measure_file(self.path)
        self.assertEqual(r.status, "window_exhausted")

    def test_partial_first_line_is_dropped_not_counted_as_corrupt(self):
        line = usage_line(123)
        write_lines(self.path, [line, line])
        data, _ = S.read_tail(self.path, max_bytes=len(line.encode()) + 10)
        r = S.scan_usage(data, truncated=True)
        self.assertEqual((r.status, r.tokens), ("ok", 123))

    def test_corrupt_lines_in_middle_are_tolerated(self):
        write_lines(self.path, [usage_line(42), "{not json", "garbage"])
        r = S.measure_file(self.path)
        self.assertEqual((r.status, r.tokens, r.bad_lines), ("ok", 42, 2))

    def test_entirely_corrupt_file_is_corrupt(self):
        write_lines(self.path, ["{oops", "also bad", "[1,"])
        self.assertEqual(S.measure_file(self.path).status, "corrupt")

    def test_empty_file_is_no_usage(self):
        self.path.write_bytes(b"")
        r = S.measure_file(self.path)
        self.assertEqual((r.status, r.tokens), ("no_usage", None))

    def test_missing_file_raises(self):
        with self.assertRaises(S.SentinelError):
            S.measure_file(Path(self.tmp.name) / "nope.jsonl")

    def test_invalid_usage_types_are_skipped_not_summed(self):
        for bad in ('"150000"', "true", "-5", "1.5", "[1]", "null"):
            line = '{"message":{"usage":{"input_tokens":%s}}}' % bad
            if bad == "null":
                # 單一欄位 null 當缺值；三欄都缺則量不到
                write_lines(self.path, [line])
                self.assertEqual(S.measure_file(self.path).status, "no_usage")
                continue
            write_lines(self.path, [line])
            r = S.measure_file(self.path)
            self.assertEqual(r.status, "no_usage", bad)
            self.assertEqual(r.bad_usage, 1, bad)

    def test_empty_usage_object_is_unmeasurable(self):
        for body in ("{}", '{"input_tokens":null}', '{"other":5}'):
            write_lines(self.path, ['{"message":{"usage":%s}}' % body])
            r = S.measure_file(self.path)
            self.assertEqual((r.status, r.tokens, r.bad_usage), ("no_usage", None, 1), body)
        # 空 usage 不可蓋掉更早的有效讀數以外的結論：只往前找到有效行
        write_lines(self.path, [usage_line(77), '{"message":{"usage":{}}}'])
        self.assertEqual(S.measure_file(self.path).tokens, 77)
        self.assertEqual(run_tool("check", str(self.path)).returncode, 0)
        write_lines(self.path, ['{"message":{"usage":{}}}'])
        self.assertEqual(run_tool("check", str(self.path)).returncode, 1)

    def test_usage_not_a_dict_is_skipped(self):
        write_lines(self.path, [usage_line(10), '{"message":{"usage":"lots"}}'])
        self.assertEqual(S.measure_file(self.path).tokens, 10)

    def test_non_utf8_bytes_do_not_crash(self):
        self.path.write_bytes(usage_line(55).encode() + b"\n\xff\xfe\xfa not utf8\n")
        self.assertEqual(S.measure_file(self.path).tokens, 55)


class StateMachineTests(unittest.TestCase):
    def verdicts(self, readings, limit=150000, step=50000):
        return [v for _, v, _ in S.simulate(readings, limit, step)]

    def test_default_staircase_boundaries(self):
        got = self.verdicts([100000, 149999, 150000, 150001, 199999, 200000, 249999, 250000, 500000])
        self.assertEqual(got, ["silent", "silent", "notify", "inject", "inject", "notify", "inject", "notify", "notify"])

    def test_custom_limit_and_step_not_swapped(self):
        got = self.verdicts([999, 1000, 1499, 1500, 2000], limit=1000, step=500)
        self.assertEqual(got, ["silent", "notify", "inject", "notify", "notify"])
        swapped = self.verdicts([999, 1000, 1499, 1500, 2000], limit=500, step=1000)
        self.assertNotEqual(got, swapped)

    def test_level_formula(self):
        self.assertIsNone(S.level_of(149999, 150000, 50000))
        self.assertEqual(S.level_of(150000, 150000, 50000), 0)
        self.assertEqual(S.level_of(349999, 150000, 50000), 3)
        self.assertEqual(S.level_of(350000, 150000, 50000), 4)

    def test_silent_does_not_touch_state(self):
        self.assertEqual(S.decide(10, 150000, 50000, 3), ("silent", 3))

    def test_notify_records_new_level_and_inject_keeps_it(self):
        self.assertEqual(S.decide(250000, 150000, 50000, -1), ("notify", 2))
        self.assertEqual(S.decide(250000, 150000, 50000, 2), ("inject", 2))

    def test_stale_level_after_context_shrinks_matches_original(self):
        # 壓縮後再長回來，原作不重設級距：同級距不再通知（已知限制，見規格第 4 節）
        self.assertEqual(self.verdicts([200000, 100000, 200000]), ["notify", "silent", "inject"])

    def test_bad_thresholds_rejected(self):
        for limit, step in ((0, 50000), (-1, 50000), (150000, 0), (150000, -5), (True, 5), ("150000", 5)):
            with self.assertRaises(S.SentinelError, msg=(limit, step)):
                S.decide(200000, limit, step, -1)


class ClassifyTests(unittest.TestCase):
    def test_labels(self):
        cases = {
            "繼續剛剛那個修正": "continue",
            "請修正剛才的函式": "continue",
            "新增一個登入頁面": "new_topic",
            "另外想要一個匯出功能": "new_topic",
            "Please continue with the previous change": "continue",
            "I want a new feature for export": "new_topic",
            "新增欄位後再修正剛剛的錯誤": "ambiguous",
            "好": "ambiguous",
            "what time is it": "ambiguous",
        }
        for text, want in cases.items():
            self.assertEqual(S.classify_prompt(text), want, text)

    def test_negation_before_term(self):
        self.assertEqual(S.classify_prompt("不要新增了，繼續修正"), "continue")
        self.assertEqual(S.classify_prompt("先不新增"), "ambiguous")

    def test_pasted_content_is_ignored(self):
        text = '繼續\n<pasted_content id="1">\n新增 另外想要 new feature\n</pasted_content id="1">'
        self.assertEqual(S.classify_prompt(text), "continue")

    def test_english_needs_word_boundary(self):
        self.assertEqual(S.classify_prompt("discontinued"), "ambiguous")

    def test_empty_input_fails(self):
        for bad in ("", "   \n", None, 5):
            with self.assertRaises(S.SentinelError):
                S.classify_prompt(bad)


class TitleTests(unittest.TestCase):
    def test_examples(self):
        cases = {"對話-3": "對話-4", "Yoto 網站 9": "Yoto 網站 10", "SEO 調整": "SEO 調整-2", "網站": "網站-2",
                 "專案-009": "專案-010", "v2 專案-3": "v2 專案-4", "專案-3 (修)": "專案-4 (修)", "  對話-1 ": "對話-2",
                 "對話-99": "對話-100"}
        for old, new in cases.items():
            self.assertEqual(S.next_title(old), new, old)

    def test_empty_fails(self):
        for bad in ("", "  ", None):
            with self.assertRaises(S.SentinelError):
                S.next_title(bad)


class CostTests(unittest.TestCase):
    def test_closed_form_matches_brute_force(self):
        for context, growth, turns, baseline in ((1000, 10, 3, 0), (180000, 3000, 20, 0), (0, 5, 1, 7), (50, 0, 9, 3)):
            brute = sum(baseline + context + growth * k for k in range(turns))
            self.assertEqual(S.cumulative_input_tokens(context, growth, turns, baseline), brute)

    def test_known_value(self):
        self.assertEqual(S.cumulative_input_tokens(1000, 10, 3), 3030)

    def test_saving_is_linear_in_turns_not_growth(self):
        stay = S.cumulative_input_tokens(180000, 3000, 20)
        sw = S.cumulative_input_tokens(6000, 3000, 20)
        self.assertEqual(stay - sw, 20 * (180000 - 6000))

    def test_bad_values(self):
        for args in ((-1, 0, 1), (1, -1, 1), (1, 1, 0), (True, 1, 1)):
            with self.assertRaises(S.SentinelError):
                S.cumulative_input_tokens(*args)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_simulate_expect_pass_and_fail(self):
        ok = run_tool("simulate", "--tokens", "100000,150000,160000,200000",
                      "--expect", "silent,notify,inject,notify")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bad = run_tool("simulate", "--tokens", "100000,150000", "--expect", "silent,inject")
        self.assertEqual(bad.returncode, 1)
        short = run_tool("simulate", "--tokens", "100000,150000", "--expect", "silent")
        self.assertEqual(short.returncode, 1)
        unknown = run_tool("simulate", "--tokens", "1", "--expect", "loud")
        self.assertEqual(unknown.returncode, 1)

    def test_simulate_bad_arguments_exit_2(self):
        for args in (["--tokens", ""], ["--tokens", "1,,2"], ["--tokens", "abc"], ["--tokens", "-5"],
                     ["--tokens", "1", "--limit", "0"], ["--tokens", "1", "--step", "-1"]):
            self.assertEqual(run_tool("simulate", *args).returncode, 2, args)

    def test_check_exit_codes(self):
        good = self.dir / "good.jsonl"
        write_lines(good, [usage_line(10, 190000, 5)])
        r = run_tool("check", str(good), "--expect", "notify")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"tokens=190015", r.stdout)
        self.assertEqual(run_tool("check", str(good), "--expect", "silent").returncode, 1)
        self.assertEqual(run_tool("check", str(good), "--last-level", "0", "--expect", "inject").returncode, 0)
        self.assertEqual(run_tool("check", str(good), "--limit", "300000", "--expect", "silent").returncode, 0)
        empty = self.dir / "empty.jsonl"
        empty.write_bytes(b"")
        self.assertEqual(run_tool("check", str(empty)).returncode, 1)
        self.assertEqual(run_tool("check", str(self.dir / "missing.jsonl")).returncode, 1)
        garbage = self.dir / "garbage.jsonl"
        write_lines(garbage, ["{x", "y"])
        self.assertEqual(run_tool("check", str(garbage)).returncode, 1)

    def test_classify_title_cost_cli(self):
        self.assertEqual(run_tool("classify", "新增一個頁面", "--expect", "new_topic").returncode, 0)
        self.assertEqual(run_tool("classify", "新增一個頁面", "--expect", "continue").returncode, 1)
        self.assertEqual(run_tool("classify", "   ").returncode, 1)
        self.assertEqual(run_tool("title", "對話-3", "--expect", "對話-4").returncode, 0)
        self.assertEqual(run_tool("title", "對話-3", "--expect", "對話-3").returncode, 1)
        cost = run_tool("cost", "--context", "180000", "--growth", "3000", "--turns", "20", "--brief", "6000")
        self.assertEqual(cost.returncode, 0)
        self.assertIn(b"saving=3480000", cost.stdout)
        self.assertEqual(run_tool("cost", "--context", "1", "--growth", "1", "--turns", "0", "--brief", "1").returncode, 2)


class HookSubprocessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.state = self.dir / "state"
        self.transcript = self.dir / "t.jsonl"

    def payload(self, **over):
        base = {"session_id": "sess-1", "transcript_path": str(self.transcript), "cwd": str(self.dir),
                "hook_event_name": "UserPromptSubmit", "prompt": "hi"}
        base.update(over)
        return base

    def hook(self, payload, *extra, env=None, raw=None):
        data = raw if raw is not None else json.dumps(payload).encode("utf-8")
        return run_tool("hook", "--state-dir", str(self.state), *extra, stdin=data, env=env)

    def test_below_limit_is_silent_and_writes_nothing(self):
        write_lines(self.transcript, [usage_line(1000, 2000, 3000)])
        r = self.hook(self.payload())
        self.assertEqual((r.returncode, r.stdout), (0, b""))
        self.assertFalse(self.state.exists())

    def test_staircase_through_real_stdin(self):
        sid = self.payload()
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        first = self.hook(sid)
        self.assertEqual(first.returncode, 0, first.stderr)
        out = json.loads(first.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("160k", out["hookSpecificOutput"]["additionalContext"])
        self.assertIn("systemMessage", out)
        self.assertEqual((self.state / "claude-long-chat-sess-1.txt").read_text(), "0")
        second = self.hook(sid)
        out2 = json.loads(second.stdout)
        self.assertNotIn("systemMessage", out2)
        self.assertIn("additionalContext", out2["hookSpecificOutput"])
        write_lines(self.transcript, [usage_line(0, 210000, 0)])
        third = json.loads(self.hook(sid).stdout)
        self.assertIn("systemMessage", third)
        self.assertEqual((self.state / "claude-long-chat-sess-1.txt").read_text(), "1")

    def test_sessions_do_not_share_state(self):
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        self.assertIn("systemMessage", json.loads(self.hook(self.payload(session_id="a")).stdout))
        self.assertIn("systemMessage", json.loads(self.hook(self.payload(session_id="b")).stdout))

    def test_output_is_pure_ascii_json(self):
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        raw = self.hook(self.payload()).stdout
        raw.decode("ascii")
        json.loads(raw)

    def test_bad_stdin_fails_loudly_and_never_exit_2(self):
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        cases = {
            "empty": b"",
            "not json": b"{oops",
            "array": b"[1,2]",
            "string": b'"x"',
            "invalid utf8": b"\xff\xfe\xfa",
            "missing transcript_path": json.dumps({"session_id": "s"}).encode(),
            "transcript_path not str": json.dumps({"session_id": "s", "transcript_path": 5}).encode(),
            "blank transcript_path": json.dumps({"session_id": "s", "transcript_path": "  "}).encode(),
            "missing session_id": json.dumps({"transcript_path": str(self.transcript)}).encode(),
            "traversal session_id": json.dumps({"session_id": "../evil", "transcript_path": str(self.transcript)}).encode(),
            "slash session_id": json.dumps({"session_id": "a/b", "transcript_path": str(self.transcript)}).encode(),
            "numeric session_id": json.dumps({"session_id": 5, "transcript_path": str(self.transcript)}).encode(),
        }
        for name, raw in cases.items():
            r = self.hook(None, raw=raw)
            self.assertEqual(r.returncode, 1, (name, r.stderr))
            self.assertEqual(r.stdout, b"", name)
            self.assertTrue(r.stderr.strip(), name)
        self.assertFalse((self.dir / "evil.txt").exists())
        self.assertFalse(list(self.dir.glob("claude-long-chat-*")))

    def test_hook_never_exits_2_for_any_argument_or_input(self):
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        arg_sets = [["--limit", "150k"], ["--foo"], ["--limit"], ["--step", "0"], ["--step", "-1"], ["--limit", "0"],
                    ["extra"], ["--state-dir"], ["--strict", "--bogus"]]
        for extra in arg_sets:
            r = run_tool("hook", *extra, stdin=json.dumps(self.payload()).encode())
            self.assertEqual(r.returncode, 1, extra)
            self.assertTrue(r.stderr.strip(), extra)
            self.assertEqual(r.stdout, b"", extra)
        for raw in (b"", b"{x", b"[]", b"\xff"):
            self.assertNotEqual(run_tool("hook", stdin=raw).returncode, 2, raw)
        self.assertEqual(run_tool("hook", "--help", stdin=b"").returncode, 0)

    def test_corrupt_transcript_fails(self):
        write_lines(self.transcript, ["{x", "y"])
        self.assertEqual(self.hook(self.payload()).returncode, 1)

    def test_unmeasurable_is_lenient_by_default_and_fails_with_strict(self):
        for setup in ("missing", "empty", "no_usage"):
            if setup == "empty":
                self.transcript.write_bytes(b"")
            elif setup == "no_usage":
                write_lines(self.transcript, [json.dumps({"type": "user", "message": {"content": "hi"}})])
            lenient = self.hook(self.payload())
            self.assertEqual((lenient.returncode, lenient.stdout), (0, b""), setup)
            self.assertTrue(lenient.stderr.strip(), setup)
            self.assertEqual(self.hook(self.payload(), "--strict").returncode, 1, setup)

    def test_bad_thresholds_fail(self):
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        self.assertEqual(self.hook(self.payload(), "--limit", "0").returncode, 1)  # argparse 錯誤在 hook 也是 1
        for env in ({"LONG_CHAT_TOKENS": "abc"}, {"LONG_CHAT_TOKENS": "0"}, {"LONG_CHAT_STEP": "-3"}, {"LONG_CHAT_STEP": "x"}):
            r = self.hook(self.payload(), env=env)
            self.assertEqual(r.returncode, 1, env)

    def test_env_thresholds_are_honoured(self):
        write_lines(self.transcript, [usage_line(0, 1500, 0)])
        r = self.hook(self.payload(), env={"LONG_CHAT_TOKENS": "1000", "LONG_CHAT_STEP": "400"})
        self.assertIn("systemMessage", json.loads(r.stdout))
        self.assertEqual((self.state / "claude-long-chat-sess-1.txt").read_text(), "1")

    def test_hook_limit_and_step_are_not_swapped(self):
        env = {"LONG_CHAT_TOKENS": "1000", "LONG_CHAT_STEP": "300"}
        write_lines(self.transcript, [usage_line(0, 500, 0)])
        below = self.hook(self.payload(), env=env)
        self.assertEqual((below.returncode, below.stdout), (0, b""))
        write_lines(self.transcript, [usage_line(0, 1700, 0)])
        above = self.hook(self.payload(), env=env)
        self.assertIn("systemMessage", json.loads(above.stdout))
        self.assertEqual((self.state / "claude-long-chat-sess-1.txt").read_text(), "2")

    def test_corrupt_state_file_heals_with_notice(self):
        write_lines(self.transcript, [usage_line(0, 160000, 0)])
        self.state.mkdir()
        sf = self.state / "claude-long-chat-sess-1.txt"
        for junk in ("abc", "", "-7", "1e3", "99999999999"):
            sf.write_text(junk)
            r = self.hook(self.payload())
            self.assertEqual(r.returncode, 0, junk)
            self.assertIn("systemMessage", json.loads(r.stdout), junk)
            self.assertIn(b"sentinel", r.stderr, junk)
            self.assertEqual(sf.read_text(), "0", junk)

    def test_chinese_path_and_cp950_safe_stdout(self):
        zh = self.dir / "中文資料夾"
        zh.mkdir()
        t = zh / "紀錄.jsonl"
        write_lines(t, [usage_line(0, 170000, 0)])
        r = self.hook(self.payload(transcript_path=str(t)), env={"PYTHONIOENCODING": "cp950"})
        self.assertEqual(r.returncode, 0, r.stderr)
        json.loads(r.stdout)


class TemplateExampleTests(unittest.TestCase):
    """範本裡的「`舊名` → `新名`」範例必須真的符合 next_title。"""

    def test_template_title_examples_are_valid(self):
        tpl = ROOT / "templates" / "session-handoff-brief-prompt.md"
        self.assertTrue(tpl.is_file(), "範本不存在")
        text = tpl.read_text(encoding="utf-8")
        pairs = re.findall(r"`([^`\n]+)`\s*→\s*`([^`\n]+)`", text)
        self.assertGreaterEqual(len(pairs), 4, "範本應列出至少 4 組命名範例")
        for old, new in pairs:
            self.assertEqual(S.next_title(old), new, old)


if __name__ == "__main__":
    unittest.main()
