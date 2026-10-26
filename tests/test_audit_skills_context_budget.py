#!/usr/bin/env python3
"""tools/audit_skills_context_budget.py 的單元測試：用暫存資料夾裡的假技能，含會讓錯誤實作失敗的反例。"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "audit_skills_context_budget.py"
sys.path.insert(0, str(TOOL.parent))
from audit_skills_context_budget import audit_directory, estimate_tokens, parse_simple_yaml  # noqa: E402

GOOD_DESC = "Extracts text from PDF files. Use when the user mentions PDFs or document extraction."


def make_skill(root: Path, folder: str, content: str) -> Path:
    d = root / folder
    d.mkdir(parents=True, exist_ok=True)
    f = d / "SKILL.md"
    f.write_text(content, encoding="utf-8")
    return f


def skill_text(name="pdf-tools", desc=GOOD_DESC, body="# Body\n\nDo the thing.\n"):
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n{body}"


class AuditSkillsContextBudgetTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="skills_audit_"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def report_for(self, folder, **kwargs):
        result = audit_directory(self.root, **kwargs)
        matches = [r for r in result["reports"] if Path(r.path).parent.name == folder or Path(r.path).name == folder]
        self.assertEqual(len(matches), 1, [r.path for r in result["reports"]])
        return matches[0], result

    def test_compliant_skill_has_no_errors_or_warnings(self):
        make_skill(self.root, "pdf-tools", skill_text())
        rep, result = self.report_for("pdf-tools")
        self.assertEqual(rep.errors, [])
        self.assertEqual(rep.warnings, [])
        self.assertEqual(result["summary"]["errors"], 0)
        # 常駐成本 = name + description 的字元數，不是整個檔案
        self.assertEqual(rep.resident_chars, len("pdf-tools") + len(GOOD_DESC))
        self.assertGreater(rep.resident_tokens_est, 0)

    def test_resident_cost_ignores_body_size(self):
        make_skill(self.root, "small", skill_text(name="small"))
        make_skill(self.root, "big", skill_text(name="big", body="x" * 20000))
        small, _ = self.report_for("small")
        big, _ = self.report_for("big")
        self.assertEqual(small.resident_chars + len("big") - len("small"), big.resident_chars)
        self.assertGreater(big.body_bytes, 20000)

    def test_oversize_body_warns_at_threshold_boundary(self):
        body_ok = "a" * 8192
        make_skill(self.root, "at-limit", skill_text(name="at-limit", body=body_ok))
        rep, _ = self.report_for("at-limit")
        # 本文 = frontmatter 之後的內容（含開頭空行），先量實際 bytes 再決定邊界
        exact = rep.body_bytes
        rep_loose, _ = self.report_for("at-limit", max_body_bytes=exact)
        self.assertEqual([w for w in rep_loose.warnings if "本文" in w], [])
        rep_tight, _ = self.report_for("at-limit", max_body_bytes=exact - 1)
        self.assertTrue(any("本文" in w for w in rep_tight.warnings))

    def test_default_budget_is_8192_bytes(self):
        make_skill(self.root, "fat", skill_text(name="fat", body="y" * 9000))
        rep, result = self.report_for("fat")
        self.assertTrue(any("8192" in w for w in rep.warnings))
        self.assertEqual(result["summary"]["skills_over_body_budget"], 1)

    def test_body_bytes_counts_utf8_bytes_not_chars(self):
        make_skill(self.root, "zh", skill_text(name="zh", body="中" * 3000))  # 3000 字 = 9000 bytes
        rep, _ = self.report_for("zh")
        self.assertGreaterEqual(rep.body_bytes, 9000)
        self.assertTrue(any("本文" in w for w in rep.warnings))

    def test_missing_frontmatter_is_error(self):
        make_skill(self.root, "nofm", "# Just a heading\n\nno frontmatter\n")
        rep, _ = self.report_for("nofm")
        self.assertTrue(any("frontmatter" in e for e in rep.errors))

    def test_unterminated_frontmatter_is_error(self):
        make_skill(self.root, "open", "---\nname: open\ndescription: Use when testing.\n\n# no closing marker\n")
        rep, _ = self.report_for("open")
        self.assertTrue(any("結尾" in e for e in rep.errors))

    def test_missing_name_and_description_are_errors(self):
        make_skill(self.root, "noname", "---\ndescription: Use when needed.\n---\nbody\n")
        make_skill(self.root, "nodesc", "---\nname: nodesc\n---\nbody\n")
        make_skill(self.root, "emptydesc", "---\nname: emptydesc\ndescription:\n---\nbody\n")
        self.assertTrue(any("name" in e for e in self.report_for("noname")[0].errors))
        self.assertTrue(any("description" in e for e in self.report_for("nodesc")[0].errors))
        self.assertTrue(any("description" in e for e in self.report_for("emptydesc")[0].errors))

    def test_invalid_names_are_errors(self):
        for folder, name in [("upper", "PDF_Tools"), ("claudey", "claude-helper"), ("tagged", "a<b>c"),
                             ("toolong", "a" * 65)]:
            make_skill(self.root, folder, skill_text(name=name))
            with self.subTest(name=name):
                rep, _ = self.report_for(folder)
                self.assertTrue(rep.errors, f"{name} 應該是 ERROR")

    def test_64_char_name_is_valid(self):
        name = "a" * 64
        make_skill(self.root, name, skill_text(name=name))
        rep, _ = self.report_for(name)
        self.assertEqual(rep.errors, [])

    def test_description_over_1024_chars_is_error_but_1024_is_not(self):
        base = "Use when testing limits. "
        ok = base + "d" * (1024 - len(base))
        too_long = ok + "d"
        make_skill(self.root, "exact", skill_text(name="exact", desc=ok))
        make_skill(self.root, "over", skill_text(name="over", desc=too_long))
        self.assertEqual(self.report_for("exact")[0].errors, [])
        self.assertTrue(any("1024" in e for e in self.report_for("over")[0].errors))

    def test_xml_tag_in_description_is_error(self):
        make_skill(self.root, "xml", skill_text(name="xml", desc="Use when <tag>things</tag> happen."))
        self.assertTrue(any("XML" in e for e in self.report_for("xml")[0].errors))

    def test_description_without_trigger_is_warning_not_error(self):
        make_skill(self.root, "vague", skill_text(name="vague", desc="Helps with documents"))
        rep, _ = self.report_for("vague")
        self.assertEqual(rep.errors, [])
        self.assertTrue(any("觸發" in w for w in rep.warnings))

    def test_chinese_trigger_description_is_accepted(self):
        make_skill(self.root, "zhdesc", skill_text(name="zhdesc", desc="整理會議記錄。當使用者提到會議紀錄或逐字稿時使用。"))
        self.assertEqual([w for w in self.report_for("zhdesc")[0].warnings if "觸發" in w], [])

    def test_name_folder_mismatch_warns(self):
        make_skill(self.root, "folder-a", skill_text(name="other-name"))
        rep, _ = self.report_for("folder-a")
        self.assertTrue(any("資料夾" in w for w in rep.warnings))

    def test_folder_without_skill_md_is_reported(self):
        (self.root / "empty-dir").mkdir()
        make_skill(self.root, "ok-skill", skill_text(name="ok-skill"))
        result = audit_directory(self.root)
        self.assertEqual(result["summary"]["folders_without_skill_md"], 1)
        self.assertEqual(result["summary"]["skills"], 1)
        self.assertEqual(result["summary"]["errors"], 1)

    def test_resident_threshold_and_total_budget(self):
        long_desc = "Use when " + "word " * 120
        make_skill(self.root, "wordy", skill_text(name="wordy", desc=long_desc))
        make_skill(self.root, "short", skill_text(name="short"))
        wordy, result = self.report_for("wordy", max_resident_tokens=100, total_resident_tokens=50)
        short, _ = self.report_for("short", max_resident_tokens=100)
        self.assertTrue(any("常駐" in w for w in wordy.warnings))
        self.assertEqual([w for w in short.warnings if "常駐" in w], [])
        self.assertTrue(result["summary"]["over_total_budget"])
        self.assertEqual(result["summary"]["resident_tokens_est_total"], wordy.resident_tokens_est + short.resident_tokens_est)

    def test_block_scalar_and_quoted_values_parse(self):
        make_skill(self.root, "folded", "---\nname: folded\ndescription: >\n  Extracts data.\n  Use when parsing logs.\n---\nbody\n")
        make_skill(self.root, "quoted", "---\nname: \"quoted\"\ndescription: 'Use when quoting: matters.'\n---\nbody\n")
        folded, _ = self.report_for("folded")
        quoted, _ = self.report_for("quoted")
        self.assertEqual(folded.description, "Extracts data. Use when parsing logs.")
        self.assertEqual(quoted.name, "quoted")
        self.assertEqual(quoted.description, "Use when quoting: matters.")
        self.assertEqual(folded.errors + quoted.errors, [])

    def test_non_utf8_file_is_error(self):
        d = self.root / "bad"
        d.mkdir()
        (d / "SKILL.md").write_bytes(b"---\nname: bad\ndescription: \xff\xfe Use when.\n---\n")
        self.assertTrue(any("UTF-8" in e for e in self.report_for("bad")[0].errors))

    def test_bom_is_tolerated(self):
        d = self.root / "bom"
        d.mkdir()
        (d / "SKILL.md").write_bytes("﻿".encode("utf-8") + skill_text(name="bom").encode("utf-8"))
        self.assertEqual(self.report_for("bom")[0].errors, [])

    def test_recursive_flag_finds_nested_skills(self):
        make_skill(self.root / "group", "nested-skill", skill_text(name="nested-skill"))
        self.assertEqual(audit_directory(self.root)["summary"]["skills"], 0)
        self.assertEqual(audit_directory(self.root, recursive=True)["summary"]["skills"], 1)

    def test_estimate_tokens_ascii_vs_cjk(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("a" * 40), 10)
        self.assertEqual(estimate_tokens("中" * 10), 10)
        self.assertEqual(estimate_tokens("a" * 40, chars_per_token=2), 20)
        self.assertGreater(estimate_tokens("中文" * 50), estimate_tokens("ab" * 50))

    def test_parse_simple_yaml_reports_unclosed_quote(self):
        _, problems = parse_simple_yaml('name: "oops\n')
        self.assertTrue(problems)


class CliTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="skills_audit_cli_"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, timeout=60)

    def test_exit_codes_clean_error_and_strict(self):
        make_skill(self.root, "pdf-tools", skill_text())
        self.assertEqual(self.run_cli(str(self.root)).returncode, 0)
        make_skill(self.root, "vague", skill_text(name="vague", desc="Helps with documents"))
        self.assertEqual(self.run_cli(str(self.root)).returncode, 0)  # 只有 WARN
        self.assertEqual(self.run_cli(str(self.root), "--strict").returncode, 1)
        make_skill(self.root, "broken", "no frontmatter")
        self.assertEqual(self.run_cli(str(self.root)).returncode, 1)  # 有 ERROR

    def test_json_output_is_valid_and_utf8(self):
        make_skill(self.root, "zh", skill_text(name="zh", desc="整理逐字稿。當使用者提到逐字稿時使用。"))
        proc = self.run_cli(str(self.root), "--json")
        data = json.loads(proc.stdout.decode("utf-8"))
        self.assertEqual(data["summary"]["skills"], 1)
        self.assertIn("整理逐字稿", data["reports"][0]["description"])

    def test_missing_directory_returns_2(self):
        self.assertEqual(self.run_cli(str(self.root / "nope")).returncode, 2)

    def test_audit_does_not_modify_files(self):
        f = make_skill(self.root, "pdf-tools", skill_text())
        before = (f.read_bytes(), f.stat().st_mtime_ns)
        self.run_cli(str(self.root))
        self.assertEqual((f.read_bytes(), f.stat().st_mtime_ns), before)


if __name__ == "__main__":
    unittest.main()
