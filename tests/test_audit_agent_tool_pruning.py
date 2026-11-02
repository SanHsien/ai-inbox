"""tools/audit_agent_tool_pruning.py 的單元測試。只用暫存資料夾裡的假 transcript，不讀真實會話紀錄。"""

import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "audit_agent_tool_pruning.py"
sys.path.insert(0, str(TOOL.parent))
import audit_agent_tool_pruning as a  # noqa: E402


def user(text="請幫我改檔", **extra):
    ev = {"type": "user", "message": {"role": "user", "content": text}}
    ev.update(extra)
    return ev


def tool_result_entry(tid="t0"):
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tid, "content": "ok"}]}}


def assistant(msg_id, *tools):
    """tools: (tool_use_id, name, input) 三元組；每個 block 一個條目，重複 message id（模擬互動 transcript）。"""
    return [{"type": "assistant", "message": {"role": "assistant", "id": msg_id, "content": [
        {"type": "tool_use", "id": tid, "name": name, "input": inp}]}} for tid, name, inp in tools]


def jsonl(entries):
    return "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n"


def session(prompts, calls=(), *, start=0):
    """prompts 個 prompt；calls 是工具名列表，每個呼叫成為一次 assistant 請求。"""
    entries = []
    for i in range(prompts):
        entries.append(user(f"prompt {i}"))
    for i, name in enumerate(calls):
        entries += assistant(f"m{start + i}", (f"toolu_{start + i}", name, {"x": "y"}))
        entries.append(tool_result_entry(f"toolu_{start + i}"))
    return entries


class Workdir:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.n = 0

    def transcript(self, entries):
        self.n += 1
        p = self.root / f"s{self.n}.jsonl"
        p.write_text(entries if isinstance(entries, str) else jsonl(entries), encoding="utf-8", newline="\n")
        return p

    def catalog(self, data):
        p = self.root / "catalog.json"
        p.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
        return p

    def close(self):
        self._tmp.cleanup()


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = a.main([str(x) for x in argv])
        except SystemExit as exc:  # argparse 的用法錯誤
            code = exc.code
    return code, out.getvalue(), err.getvalue()


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.w = Workdir()
        self.addCleanup(self.w.close)

    def parse(self, entries):
        return a.parse_transcript(self.w.transcript(entries))

    def analyze(self, sessions, catalog=None, **kw):
        return a.analyze(sessions, catalog, **kw)


class ParseTest(BaseTest):
    def test_counts_calls_prompts_and_requests(self):
        s = self.parse(session(3, ["Read", "Read", "Edit"]))
        self.assertEqual(s["prompts"], 3)
        self.assertEqual(s["calls"], {"Read": 2, "Edit": 1})
        self.assertEqual(s["requests"], 3)

    def test_duplicate_tool_use_id_counted_once(self):
        entries = [user()] + assistant("m1", ("toolu_a", "Read", {"p": 1})) + assistant("m1", ("toolu_a", "Read", {"p": 1}))
        self.assertEqual(self.parse(entries)["calls"], {"Read": 1})

    def test_same_message_id_is_one_request(self):
        entries = [user()] + assistant("m1", ("t1", "Read", {}), ("t2", "Grep", {}))
        s = self.parse(entries)
        self.assertEqual(s["requests"], 1)
        self.assertEqual(s["calls"], {"Read": 1, "Grep": 1})

    def test_tool_result_and_meta_and_sidechain_are_not_prompts(self):
        entries = [
            user("真的 prompt"),
            tool_result_entry(),
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "t9", "content": "ok"},
                {"type": "text", "text": "附帶說明文字"}]}},
            user("meta", isMeta=True),
            user("子 agent", isSidechain=True),
            user("摘要", isCompactSummary=True),
            user("<local-command-stdout>x</local-command-stdout>"),
            user("[Request interrupted by user]"),
            user("   "),
        ]
        self.assertEqual(self.parse(entries)["prompts"], 1)

    def test_text_block_list_prompt_counts(self):
        entries = [{"type": "user", "message": {"content": [{"type": "text", "text": "hi"}]}}]
        self.assertEqual(self.parse(entries)["prompts"], 1)

    def test_other_entry_types_are_ignored_not_counted_twice(self):
        blob = {"type": "api-request-blob", "message": {"content": [
            {"type": "tool_use", "id": "toolu_0", "name": "Read", "input": {}}]}}
        entries = session(1, ["Read"]) + [blob, {"type": "summary", "summary": "x"}]
        self.assertEqual(self.parse(entries)["calls"], {"Read": 1})

    def test_input_chars_grow_with_input_size(self):
        small = self.parse([user()] + assistant("m1", ("t1", "Read", {"p": "a"})))
        big = self.parse([user()] + assistant("m1", ("t1", "Read", {"p": "a" * 400})))
        self.assertGreater(big["input_chars"]["Read"], small["input_chars"]["Read"] + 390)

    def test_utf8_bom_is_accepted(self):
        p = self.w.root / "bom.jsonl"
        p.write_bytes(b"\xef\xbb\xbf" + jsonl(session(1, ["Read"])).encode("utf-8"))
        self.assertEqual(a.parse_transcript(p)["calls"], {"Read": 1})


class BadInputTest(BaseTest):
    def assert_input_error(self, entries, fragment=""):
        with self.assertRaises(a.InputError) as ctx:
            self.parse(entries)
        self.assertIn(fragment, str(ctx.exception))

    def test_empty_file(self):
        self.assert_input_error("", "空檔")

    def test_whitespace_only_file(self):
        self.assert_input_error("\n  \n\t\n", "空檔")

    def test_broken_json_reports_line_number(self):
        self.assert_input_error(jsonl(session(1)) + "{這不是 json\n", ":2")

    def test_truncated_json_line(self):
        self.assert_input_error(jsonl([user()]) + '{"type": "assistant", "message": {"con', "不是合法 JSON")

    def test_line_not_an_object(self):
        self.assert_input_error("[1, 2, 3]\n", "不是 JSON 物件")

    def test_missing_type(self):
        self.assert_input_error([{"message": {"content": "x"}}], "type")

    def test_non_string_type(self):
        self.assert_input_error([{"type": 5}], "type")

    def test_assistant_without_message(self):
        self.assert_input_error([user(), {"type": "assistant"}], "message.content")

    def test_user_without_content(self):
        self.assert_input_error([{"type": "user", "message": {}}], "message.content")

    def test_content_wrong_type(self):
        self.assert_input_error([{"type": "user", "message": {"content": 7}}], "字串或陣列")

    def test_tool_use_without_name(self):
        entries = [user(), {"type": "assistant", "message": {"id": "m", "content": [
            {"type": "tool_use", "id": "t", "input": {}}]}}]
        self.assert_input_error(entries, "name")

    def test_tool_use_with_blank_or_non_string_name(self):
        for bad in ("", "  ", 3, None):
            entries = [user(), {"type": "assistant", "message": {"id": "m", "content": [
                {"type": "tool_use", "id": "t", "name": bad, "input": {}}]}}]
            with self.subTest(name=bad):
                self.assert_input_error(entries, "name")

    def test_invalid_utf8(self):
        p = self.w.root / "bad.jsonl"
        p.write_bytes(b'{"type": "user", "message": {"content": "\xff\xfe"}}\n')
        with self.assertRaises(a.InputError):
            a.parse_transcript(p)

    def test_missing_file(self):
        with self.assertRaises(a.InputError):
            a.parse_transcript(self.w.root / "nope.jsonl")

    def test_only_unknown_entries_yields_no_prompts_error(self):
        s = self.parse([{"type": "summary", "summary": "x"}])
        with self.assertRaises(a.InputError) as ctx:
            self.analyze([s])
        self.assertIn("prompt", str(ctx.exception))

    def test_calls_without_any_prompt_is_error(self):
        s = self.parse(assistant("m1", ("t1", "Read", {})))
        with self.assertRaises(a.InputError):
            self.analyze([s], {"Read": 10, "Foo": 5})

    def test_no_sessions(self):
        with self.assertRaises(a.InputError):
            self.analyze([])


class CatalogTest(BaseTest):
    def load(self, data):
        return a.load_catalog(self.w.catalog(data))

    def test_valid_catalog(self):
        self.assertEqual(self.load({"Read": 500, "mcp__srv__tool-x": None}), {"Read": 500, "mcp__srv__tool-x": None})

    def test_rejects_bad_catalogs(self):
        cases = {
            "not json": "{oops",
            "empty object": {},
            "array": ["Read"],
            "negative tokens": {"Foo": -1},
            "float tokens": {"Foo": 1.5},
            "string tokens": {"Foo": "100"},
            "bool tokens": {"Foo": True},
            "specifier in name": {"Bash(rm *)": 10},
            "glob in name": {"mcp__*": 10},
            "space in name": {"Stop Task": 10},
            "empty name": {"": 10},
            "leading digit": {"1tool": 10},
        }
        for label, data in cases.items():
            with self.subTest(label):
                with self.assertRaises(a.InputError):
                    self.load(data)

    def test_missing_catalog_file(self):
        with self.assertRaises(a.InputError):
            a.load_catalog(self.w.root / "nope.json")


class DenyRuleTest(BaseTest):
    def sessions(self, n_sessions, prompts_each, calls=("Read",)):
        return [self.parse(session(prompts_each, list(calls), start=i * 100)) for i in range(n_sessions)]

    def test_unused_tool_with_enough_evidence_is_denied(self):
        res = self.analyze(self.sessions(2, 5), {"Read": 600, "Foo": 300})
        self.assertEqual(res["deny"]["rules"], ["Foo"])
        self.assertEqual(res["permissions"], {"deny": ["Foo"]})

    def test_used_tool_is_never_denied_even_once(self):
        ss = self.sessions(5, 5, calls=())
        ss[0] = self.parse(session(5, ["Foo"]))
        res = self.analyze(ss, {"Foo": 300, "Bar": 300})
        self.assertEqual(res["deny"]["rules"], ["Bar"])

    def test_prompt_threshold_boundary(self):
        # 2 個 session 共 10 個 prompt：剛好達標；共 9 個：不足
        ok = self.analyze(self.sessions(2, 5), {"Foo": 1}, min_prompts=10, min_sessions=2)
        short = self.analyze(self.sessions(2, 5), {"Foo": 1}, min_prompts=11, min_sessions=2)
        self.assertEqual(ok["deny"]["rules"], ["Foo"])
        self.assertEqual(short["deny"]["rules"], [])
        self.assertEqual(short["deny"]["skipped"][0]["tool"], "Foo")
        self.assertIn("證據不足", short["deny"]["skipped"][0]["reason"])

    def test_single_long_session_is_not_enough(self):
        res = self.analyze(self.sessions(1, 50), {"Foo": 1}, min_prompts=10, min_sessions=2, fallback_sessions=5)
        self.assertEqual(res["deny"]["rules"], [])

    def test_fallback_sessions_rule(self):
        few = self.analyze(self.sessions(4, 1), {"Foo": 1}, fallback_sessions=5, min_prompts=10)
        many = self.analyze(self.sessions(5, 1), {"Foo": 1}, fallback_sessions=5, min_prompts=10)
        self.assertEqual(few["deny"]["rules"], [])
        self.assertEqual(many["deny"]["rules"], ["Foo"])

    def test_session_without_prompts_does_not_count_as_evidence_session(self):
        ss = self.sessions(4, 1) + [self.parse(session(0, ["Read"], start=900))]
        res = self.analyze(ss, {"Foo": 1}, fallback_sessions=5, min_prompts=10)
        self.assertEqual(res["sessions"], 5)
        self.assertEqual(res["sessions_with_prompts"], 4)
        self.assertEqual(res["deny"]["rules"], [])

    def test_protected_tools_are_never_denied_and_explained(self):
        catalog = {name: 100 for name in a.PROTECTED_TOOLS}
        catalog["Foo"] = 100
        res = self.analyze(self.sessions(6, 5, calls=("Zzz",)), catalog)
        self.assertEqual(res["deny"]["rules"], ["Foo"])
        skipped = {s["tool"]: s["reason"] for s in res["deny"]["skipped"]}
        self.assertEqual(set(skipped), set(a.PROTECTED_TOOLS))
        for tool in ("Read", "Edit", "Bash", "Write", "Grep", "Glob", "AskUserQuestion"):
            self.assertIn("受保護", skipped[tool])

    def test_protected_set_contains_basic_work_tools(self):
        for tool in ("Read", "Edit", "Write", "Bash", "Grep", "Glob", "MultiEdit"):
            self.assertIn(tool, a.PROTECTED_TOOLS)

    def test_notebookedit_needs_triple_evidence(self):
        catalog = {"NotebookEdit": 100, "Foo": 100}
        mid = self.analyze(self.sessions(2, 5), catalog)  # 10 個 prompt：Foo 夠、NotebookEdit 要 30
        self.assertEqual(mid["deny"]["rules"], ["Foo"])
        big = self.analyze(self.sessions(2, 15), catalog)  # 30 個 prompt
        self.assertEqual(big["deny"]["rules"], ["Foo", "NotebookEdit"])

    def test_no_catalog_means_no_deny_list(self):
        res = self.analyze(self.sessions(10, 10))
        self.assertEqual(res["deny"]["status"], "no-catalog")
        self.assertEqual(res["permissions"], {"deny": []})

    def test_all_catalog_tools_used_gives_none_status(self):
        res = self.analyze(self.sessions(3, 5), {"Read": 10})
        self.assertEqual(res["deny"]["status"], "none")
        self.assertIsNone(res["deny"]["expected_savings"])

    def test_savings_arithmetic(self):
        ss = self.sessions(2, 5)  # 每個 session 1 次請求 -> 共 2 次
        res = self.analyze(ss, {"Read": 600, "Foo": 300, "Bar": 200})
        sv = res["deny"]["expected_savings"]
        self.assertEqual(res["deny"]["rules"], ["Bar", "Foo"])
        self.assertEqual(sv["schema_tokens_per_request"], 500)
        self.assertEqual(sv["requests_in_window"], 2)
        self.assertEqual(sv["tokens_if_denied_during_window"], 1000)
        self.assertEqual(sv["unmeasured_tools"], [])

    def test_unmeasured_schema_is_reported_not_counted_as_zero(self):
        res = self.analyze(self.sessions(2, 5), {"Read": 600, "Foo": 300, "Bar": None})
        sv = res["deny"]["expected_savings"]
        self.assertEqual(sv["schema_tokens_per_request"], 300)
        self.assertEqual(sv["unmeasured_tools"], ["Bar"])
        self.assertIn("沒有 schema token", sv["note"])

    def test_rules_are_valid_bare_tool_names(self):
        catalog = {"mcp__github__create_issue": 400, "mcp__db-x__query": 300, "Foo": 10}
        res = self.analyze(self.sessions(2, 5), catalog)
        self.assertEqual(len(res["deny"]["rules"]), 3)
        for rule in res["deny"]["rules"]:
            self.assertRegex(rule, a.TOOL_NAME_RE)
            self.assertNotRegex(rule, r"[()*:]")

    def test_used_but_not_in_catalog_is_listed(self):
        res = self.analyze(self.sessions(2, 5, calls=("Read", "Surprise")), {"Read": 10, "Foo": 10})
        self.assertEqual(res["used_but_not_in_catalog"], ["Surprise"])

    def test_bad_thresholds_rejected(self):
        for kw in ({"min_prompts": 0}, {"min_sessions": -1}, {"fallback_sessions": 0},
                   {"min_prompts": True}, {"min_prompts": 2.5}, {"chars_per_token": 0}):
            with self.subTest(kw=kw):
                with self.assertRaises(a.InputError):
                    self.analyze(self.sessions(2, 5), {"Foo": 1}, **kw)


class StatsTest(BaseTest):
    def test_frequencies_and_shares(self):
        s = self.parse(session(4, ["Read", "Read", "Read", "Grep"]))
        res = self.analyze([s], {"Read": 600, "Grep": 200, "Foo": 200})
        by = {t["name"]: t for t in res["tools"]}
        self.assertEqual(by["Read"]["calls"], 3)
        self.assertEqual(by["Read"]["calls_per_prompt"], 0.75)
        self.assertEqual(by["Read"]["call_share"], 0.75)
        self.assertEqual(by["Grep"]["call_share"], 0.25)
        self.assertEqual(by["Foo"]["calls"], 0)
        self.assertEqual(by["Read"]["schema_share"], 0.6)
        self.assertAlmostEqual(sum(t["input_token_share"] for t in res["tools"]), 1.0, places=3)
        self.assertEqual([t["name"] for t in res["tools"]][:2], ["Read", "Grep"])

    def test_sessions_used_counts_files(self):
        ss = [self.parse(session(2, ["Read"])), self.parse(session(2, [])), self.parse(session(2, ["Read"], start=50))]
        res = self.analyze(ss)
        self.assertEqual(next(t for t in res["tools"] if t["name"] == "Read")["sessions_used"], 2)


class CliTest(BaseTest):
    def two_sessions(self):
        return [self.w.transcript(session(5, ["Read"], start=i * 10)) for i in range(2)]

    def test_exit_0_and_report(self):
        t = self.two_sessions()
        cat = self.w.catalog({"Read": 600, "Foo": 300})
        code, out, err = run_cli(*t, "--catalog", cat)
        self.assertEqual((code, err), (0, ""))
        self.assertIn("建議的 permissions.deny", out)
        self.assertIn("- Foo", out)
        self.assertNotIn("- Read", out)

    def test_json_output_has_permissions_deny(self):
        t = self.two_sessions()
        cat = self.w.catalog({"Read": 600, "Foo": 300})
        code, out, _ = run_cli(*t, "--catalog", cat, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["permissions"], {"deny": ["Foo"]})

    def test_deny_out_file_shape(self):
        t = self.two_sessions()
        cat = self.w.catalog({"Read": 600, "Foo": 300})
        dest = self.w.root / "deny.json"
        code, _, _ = run_cli(*t, "--catalog", cat, "--deny-out", dest)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(dest.read_text(encoding="utf-8")), {"permissions": {"deny": ["Foo"]}})

    def test_deny_out_refuses_when_nothing_to_write(self):
        t = self.two_sessions()
        dest = self.w.root / "deny.json"
        code, _, err = run_cli(*t, "--deny-out", dest)  # 沒有目錄
        self.assertEqual(code, 2)
        self.assertIn("no-catalog", err)
        self.assertFalse(dest.exists())

    def test_no_catalog_exit_0_without_deny_list(self):
        code, out, _ = run_cli(*self.two_sessions())
        self.assertEqual(code, 0)
        self.assertIn("未產生", out)

    def test_exit_2_cases(self):
        good = self.two_sessions()
        empty = self.w.transcript("")
        broken = self.w.transcript("{nope\n")
        bad_catalog = self.w.catalog("{nope")
        cases = {
            "empty transcript": [empty],
            "broken json": [broken],
            "good + broken": good + [broken],
            "missing file": [self.w.root / "nope.jsonl"],
            "bad catalog": good + ["--catalog", bad_catalog],
            "zero threshold": good + ["--min-prompts", "0"],
            "non-int threshold": good + ["--min-sessions", "x"],
            "no args": [],
        }
        for label, argv in cases.items():
            with self.subTest(label):
                code, out, _ = run_cli(*argv)
                self.assertEqual(code, 2)
                self.assertEqual(out, "")

    def test_exit_2_when_no_prompts(self):
        t = self.w.transcript(assistant("m1", ("t1", "Read", {})))
        code, _, err = run_cli(t)
        self.assertEqual(code, 2)
        self.assertIn("prompt", err)

    def test_subprocess_exit_codes_and_cp950_safe_output(self):
        t = self.two_sessions()
        cat = self.w.catalog({"Read": 600, "Foo": 300})
        env = dict(os.environ, PYTHONIOENCODING="cp950")
        ok = subprocess.run([sys.executable, str(TOOL), *map(str, t), "--catalog", str(cat)],
                            capture_output=True, env=env)
        self.assertEqual(ok.returncode, 0, ok.stderr.decode("utf-8", "replace"))
        self.assertIn("Foo", ok.stdout.decode("utf-8"))
        bad = subprocess.run([sys.executable, str(TOOL), str(self.w.transcript(""))], capture_output=True, env=env)
        self.assertEqual(bad.returncode, 2)
        self.assertIn("錯誤", bad.stderr.decode("utf-8"))


class DocConsistencyTest(unittest.TestCase):
    """規範文件第 5 節的範例要和工具實際輸出一致。"""

    DOC = Path(__file__).resolve().parent.parent / "docs" / "token-economizer-cost-control-spec.md"

    def test_documented_defaults_match_code(self):
        text = self.DOC.read_text(encoding="utf-8")
        for needle in (f"min_prompts={a.DEFAULT_MIN_PROMPTS}", f"min_sessions={a.DEFAULT_MIN_SESSIONS}",
                       f"fallback_sessions={a.DEFAULT_FALLBACK_SESSIONS}"):
            self.assertIn(needle, text)
        for tool in a.PROTECTED_TOOLS:
            self.assertIn(f"`{tool}`", text)

    def test_documented_deny_example_is_valid_json_with_valid_names(self):
        text = self.DOC.read_text(encoding="utf-8")
        blocks = re.findall(r"```json\n(.*?)```", text, re.S)
        found = False
        for block in blocks:
            data = json.loads(block)
            if "permissions" in data:
                found = True
                for rule in data["permissions"]["deny"]:
                    self.assertRegex(rule, a.TOOL_NAME_RE)
        self.assertTrue(found, "文件缺少 permissions.deny 範例")


if __name__ == "__main__":
    unittest.main()
