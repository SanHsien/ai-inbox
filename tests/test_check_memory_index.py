"""tools/check_memory_index.py 的單元測試。只用暫存資料夾裡的假記憶，不讀真實記憶庫。"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "check_memory_index.py"
sys.path.insert(0, str(TOOL.parent))
import check_memory_index as c  # noqa: E402


def fm(name, desc="d", typ="user", nested=True, body=""):
    meta = f"metadata:\n  type: {typ}\n" if nested else f"type: {typ}\n"
    return f"---\nname: {name}\ndescription: {desc}\n{meta}---\n\n{body}\n"


class MemoryDir:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def index(self, *names, extra=""):
        lines = ["# MEMORY.md", ""] + [f"- [{n}]({n}) — 說明" for n in names] + ([extra] if extra else [])
        self.write("MEMORY.md", "\n".join(lines) + "\n")

    def close(self):
        self._tmp.cleanup()


def codes(findings, level=None):
    return sorted(f.code for f in findings if level is None or f.level == level)


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.m = MemoryDir()
        self.addCleanup(self.m.close)

    def run_check(self, **kw):
        return c.check(self.m.root, **kw)

    def test_clean_memory_has_no_findings(self):
        self.m.write("a.md", fm("a", body="見 [[b]]"))
        self.m.write("b.md", fm("b", typ="feedback", nested=False))
        self.m.index("a.md", "b.md")
        findings, stats = self.run_check()
        self.assertEqual(findings, [])
        self.assertEqual(stats, {"index_entries": 2, "sub_index_entries": 0, "memory_files": 2})

    def test_broken_link(self):
        self.m.write("a.md", fm("a"))
        self.m.index("a.md", "ghost.md")
        findings, _ = self.run_check()
        self.assertEqual(codes(findings, "ERROR"), ["broken-link"])
        self.assertIn("ghost.md", findings[0].msg)

    def test_unindexed_file(self):
        self.m.write("a.md", fm("a"))
        self.m.write("orphan.md", fm("orphan"))
        self.m.index("a.md")
        findings, _ = self.run_check()
        self.assertEqual([(f.code, f.file) for f in findings], [("unindexed", "orphan.md")])

    def test_ignore_glob_excludes_from_all_checks(self):
        self.m.write("a.md", fm("a"))
        self.m.write("daily-log-1.md", "沒有 frontmatter，也有 [[死連結]]\n")
        self.m.index("a.md")
        self.assertNotEqual(self.run_check(ignore=[])[0], [])
        findings, stats = self.run_check(ignore=["daily-log-*.md"])
        self.assertEqual(findings, [])
        self.assertEqual(stats["memory_files"], 1)

    def test_daily_log_ignored_by_default(self):
        self.m.write("a.md", fm("a"))
        self.m.write("daily-log-2026-10-27.md", "沒有 frontmatter\n")
        self.m.index("a.md")
        findings, stats = self.run_check()
        self.assertEqual(findings, [])
        self.assertEqual(stats["memory_files"], 1)

    def test_insight_is_default_type(self):
        self.m.write("a.md", fm("a", typ="insight"))
        self.m.index("a.md")
        self.assertEqual(self.run_check()[0], [])

    def test_sub_index_entries_count_as_indexed(self):
        self.m.write("a.md", fm("a"))
        self.m.write("r1.md", fm("r1", typ="reference"))
        self.m.write("old.md", fm("old", typ="project"))
        self.m.write("archive/done.md", fm("done", typ="project"))
        self.m.write("INDEX-reference.md", "# 子索引\n\n- [r1.md](r1.md) — x\n- [old](old.md) — y\n- [done](archive/done.md) — z\n")
        self.m.index("a.md", "INDEX-reference.md", extra="- 參考 [[done]] 與 [[archive/done]]")
        findings, stats = self.run_check(max_entries=2)
        self.assertEqual(codes(findings), ["dead-wikilink"])  # [[done]] 不在頂層，只有 archive/done 算數
        self.assertEqual(stats, {"index_entries": 2, "sub_index_entries": 3, "memory_files": 4})

    def test_sub_index_problems_report_sub_index_file(self):
        self.m.write("a.md", fm("a"))
        self.m.write("INDEX-x.md", "- [a](a.md) — 重複\n- [g](ghost.md) — 壞\n- [o](../o.md) — 外\n")
        self.m.index("a.md", "INDEX-x.md")
        findings, _ = self.run_check()
        self.assertEqual(
            sorted((f.code, f.file) for f in findings),
            [("broken-link", "INDEX-x.md"), ("duplicate", "INDEX-x.md"), ("outside-dir", "INDEX-x.md")],
        )

    def test_unlinked_sub_index_is_not_followed(self):
        self.m.write("a.md", fm("a"))
        self.m.write("r1.md", fm("r1"))
        self.m.write("INDEX-orphan.md", "- [r1](r1.md)\n")
        self.m.index("a.md")
        findings, _ = self.run_check()
        self.assertEqual(sorted((f.code, f.file) for f in findings), [("unindexed", "INDEX-orphan.md"), ("unindexed", "r1.md")])

    def test_nested_and_cyclic_sub_indexes(self):
        self.m.write("a.md", fm("a"))
        self.m.write("b.md", fm("b"))
        self.m.write("INDEX-one.md", "- [two](INDEX-two.md)\n")
        self.m.write("INDEX-two.md", "- [b](b.md)\n- [one](INDEX-one.md)\n")
        self.m.index("a.md", "INDEX-one.md")
        findings, stats = self.run_check()
        self.assertEqual(codes(findings), ["duplicate"])
        self.assertEqual(stats["sub_index_entries"], 3)

    def test_skip_frontmatter_still_requires_index(self):
        self.m.write("a.md", "沒有 frontmatter\n")
        self.m.write("b.md", "沒有 frontmatter\n")
        self.m.index("a.md")
        findings, _ = self.run_check(skip_frontmatter=["*.md"])
        self.assertEqual(codes(findings), ["unindexed"])

    def test_frontmatter_missing_or_incomplete(self):
        self.m.write("none.md", "只有內文\n")
        self.m.write("noend.md", "---\nname: noend\n沒收尾\n")
        self.m.write("nodesc.md", "---\nname: nodesc\ntype: user\n---\n")
        self.m.write("notype.md", "---\nname: notype\ndescription: d\n---\n")
        self.m.index("none.md", "noend.md", "nodesc.md", "notype.md")
        findings, _ = self.run_check()
        by_file = {f.file: f.msg for f in findings if f.code == "no-frontmatter"}
        self.assertEqual(sorted(by_file), ["nodesc.md", "noend.md", "none.md", "notype.md"])
        self.assertIn("description", by_file["nodesc.md"])
        self.assertIn("type", by_file["notype.md"])

    def test_name_mismatch_and_unknown_type_are_warnings(self):
        self.m.write("a.md", fm("other", typ="weird"))
        self.m.index("a.md")
        findings, _ = self.run_check()
        self.assertEqual(codes(findings), ["name-mismatch", "unknown-type"])
        self.assertEqual(codes(findings, "ERROR"), [])
        self.assertEqual(codes(self.run_check(types=("weird",))[0]), ["name-mismatch"])

    def test_dead_wikilink_with_alias_anchor_and_code_exclusions(self):
        body = (
            "好：[[b]] [[b|別名]] [[b#段落]] [[b.md]]\n"
            "壞：[[ghost]]\n"
            "行內程式碼 `[[inline-ghost]]` 不算\n"
            "```\n[[fenced-ghost]]\n```\n"
        )
        self.m.write("a.md", fm("a", body=body))
        self.m.write("b.md", fm("b"))
        self.m.index("a.md", "b.md")
        findings, _ = self.run_check()
        self.assertEqual([f.code for f in findings], ["dead-wikilink"])
        self.assertIn("ghost", findings[0].msg)
        self.assertNotIn("inline", findings[0].msg)
        self.assertNotIn("fenced", findings[0].msg)

    def test_wikilink_in_index_is_checked(self):
        self.m.write("a.md", fm("a"))
        self.m.index("a.md", extra="- 參考 [[nope]]")
        self.assertEqual(codes(self.run_check()[0]), ["dead-wikilink"])

    def test_duplicate_and_multi_pointer(self):
        self.m.write("a.md", fm("a"))
        self.m.write("b.md", fm("b"))
        self.m.write("MEMORY.md", "- [a](a.md) — x\n- [a](a.md) — again\n- [b](b.md) 與 [a](a.md)\n")
        findings, _ = self.run_check()
        self.assertEqual(codes(findings), ["duplicate", "duplicate", "multi-pointer"])
        self.assertEqual(codes(findings, "ERROR"), [])

    def test_too_many_and_long_line(self):
        names = [f"m{i}.md" for i in range(5)]
        for n in names:
            self.m.write(n, fm(n[:-3]))
        self.m.write("MEMORY.md", "".join(f"- [{n}]({n}) — {'長' * 30}\n" for n in names))
        findings, _ = self.run_check(max_entries=4, max_line_chars=20)
        self.assertEqual(codes(findings), ["long-line"] * 5 + ["too-many"])
        self.assertEqual(self.run_check(max_entries=5, max_line_chars=500)[0], [])

    def test_boundary_exactly_at_limit_is_ok(self):
        for i in range(3):
            self.m.write(f"m{i}.md", fm(f"m{i}"))
        self.m.index("m0.md", "m1.md", "m2.md")
        self.assertEqual(self.run_check(max_entries=3)[0], [])

    def test_outside_dir_links(self):
        self.m.write("a.md", fm("a"))
        for bad in ("../x.md", "/etc/passwd", "C:/Windows/x.md", "sub/../../x.md"):
            with self.subTest(bad=bad):
                self.m.write("MEMORY.md", f"- [a](a.md)\n- [x]({bad})\n")
                findings, _ = self.run_check()
                self.assertEqual(codes(findings), ["outside-dir"])

    def test_urls_and_anchors_are_not_files(self):
        self.m.write("a.md", fm("a"))
        self.m.write("MEMORY.md", "- [a](a.md#top)\n- [web](https://example.com/x.md)\n- [here](#sec)\n")
        self.assertEqual(self.run_check()[0], [])

    def test_subdirectory_link_and_case_mismatch(self):
        self.m.write("a.md", fm("a"))
        self.m.write("sub/Note.md", "x\n")
        self.m.write("MEMORY.md", "- [a](a.md)\n- [n](sub/Note.md)\n- [bad](sub/note.md)\n- [A](A.md)\n")
        findings, _ = self.run_check()
        self.assertEqual(codes(findings), ["broken-link", "broken-link"])
        self.assertTrue(all("大小寫不符" in f.msg for f in findings))

    def test_subdirectory_files_are_not_required_in_index(self):
        self.m.write("a.md", fm("a"))
        self.m.write("backup/old.md", "x\n")
        self.m.index("a.md")
        self.assertEqual(self.run_check()[0], [])

    def test_missing_index(self):
        self.m.write("a.md", fm("a"))
        findings, _ = self.run_check()
        self.assertEqual(codes(findings), ["no-index"])

    def test_invalid_utf8(self):
        self.m.write("a.md", fm("a"))
        (self.m.root / "bad.md").write_bytes(b"\xff\xfe\x00bad")
        self.m.index("a.md", "bad.md")
        findings, _ = self.run_check()
        self.assertEqual(codes(findings, "ERROR"), ["unreadable"])

    def test_crlf_and_bom_files(self):
        (self.m.root / "a.md").write_bytes("\ufeff---\r\nname: a\r\ndescription: d\r\ntype: user\r\n---\r\n".encode("utf-8"))
        (self.m.root / "MEMORY.md").write_bytes("- [a](a.md) — x\r\n".encode("utf-8"))
        self.assertEqual(self.run_check()[0], [])


class CliTest(unittest.TestCase):
    def run_cli(self, *args, env=None):
        return subprocess.run(
            [sys.executable, str(TOOL), *args], capture_output=True, text=True, encoding="utf-8", env=env or {**os.environ, "PYTHONUTF8": "1"}
        )

    def test_exit_codes(self):
        m = MemoryDir()
        self.addCleanup(m.close)
        m.write("a.md", fm("other"))  # 只有 WARN
        m.index("a.md")
        self.assertEqual(self.run_cli(str(m.root)).returncode, 0)
        self.assertEqual(self.run_cli(str(m.root), "--strict").returncode, 1)
        m.index("a.md", "ghost.md")  # ERROR
        proc = self.run_cli(str(m.root))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("broken-link", proc.stdout)
        self.assertEqual(self.run_cli(str(m.root / "nope")).returncode, 2)

    def test_json_output(self):
        m = MemoryDir()
        self.addCleanup(m.close)
        m.write("a.md", fm("a"))
        m.index("a.md", "ghost.md")
        data = json.loads(self.run_cli(str(m.root), "--json").stdout)
        self.assertEqual(data["errors"], 1)
        self.assertEqual(data["by_code"], {"broken-link": 1})
        self.assertEqual(data["findings"][0]["file"], "MEMORY.md")

    def test_help_utf8_under_cp950(self):
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        proc = subprocess.run([sys.executable, str(TOOL), "--help"], capture_output=True, env=env)
        self.assertEqual(proc.returncode, 0)
        proc.stdout.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
