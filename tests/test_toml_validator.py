"""tools/toml_validator.py 的單元測試（含正常案例與會失敗的反例）。"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

import toml_validator as tv  # noqa: E402


def codes(findings, severity=None):
    return sorted(f.code for f in findings if severity in (None, f.severity))


def check(text, **kw):
    raw = text.encode("utf-8") if isinstance(text, str) else text
    return tv.validate_bytes("x.toml", raw, **kw)


GOOD_PYPROJECT = """
[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.11"
"""


class ParseTest(unittest.TestCase):
    def test_valid_file_has_no_findings(self):
        self.assertEqual(check('a = 1\n[t]\nb = "x"\n'), [])

    def test_syntax_error_reports_position(self):
        f = check("a = \n")
        self.assertEqual(codes(f, "error"), ["parse"])
        self.assertIn("line 1", f[0].message)

    def test_duplicate_key_is_error(self):
        self.assertIn("parse", codes(check("a = 1\na = 2\n"), "error"))

    def test_duplicate_table_is_error(self):
        self.assertIn("parse", codes(check("[t]\na = 1\n[t]\nb = 2\n"), "error"))

    def test_windows_path_in_basic_string_is_error_but_literal_is_fine(self):
        self.assertIn("parse", codes(check('p = "C:\\GitHub\\x"\n'), "error"))
        self.assertEqual(check("p = 'C:\\GitHub\\x'\n"), [])

    def test_bom_is_reported_with_its_own_code(self):
        f = check(tv.BOM + b"a = 1\n")
        self.assertEqual(codes(f, "error"), ["bom"])

    def test_invalid_utf8_is_reported(self):
        f = check(b"a = '\xff\xfe'\n")
        self.assertEqual(codes(f, "error"), ["encoding"])

    def test_v11_syntax_gets_hint_only_when_interpreter_lacks_support(self):
        text = "a = {\n  x = 1,\n}\n"
        f = check(text)
        if tv.supports_toml_v11():
            self.assertEqual(f, [])
        else:
            self.assertEqual(codes(f, "error"), ["parse"])
            self.assertEqual(codes(f, "warning"), ["parse"])


class FloatVersionTest(unittest.TestCase):
    def test_unquoted_version_becomes_float_warning(self):
        f = check("python_version = 3.10\n")
        self.assertEqual(codes(f, "warning"), ["float-version"])
        self.assertIn("3.1", f[0].message)

    def test_quoted_version_is_fine(self):
        self.assertEqual(check('python_version = "3.10"\n'), [])

    def test_nested_and_array_of_tables_are_scanned(self):
        f = check("[[tool.x]]\nmin_version = 1.2\n")
        self.assertEqual(codes(f, "warning"), ["float-version"])
        self.assertIn("tool.x[0].min_version", f[0].message)

    def test_non_version_float_is_not_flagged(self):
        self.assertEqual(check("ratio = 0.5\n"), [])


class RequiredKeysTest(unittest.TestCase):
    def test_missing_key(self):
        f = check("a = 1\n", requires=["server.port"])
        self.assertEqual(codes(f, "error"), ["required"])

    def test_present_key_passes(self):
        self.assertEqual(check("[server]\nport = 80\n", requires=["server.port:int"]), [])

    def test_wrong_type_string_instead_of_bool(self):
        f = check('[x]\nenabled = "false"\n', requires=["x.enabled:bool"])
        self.assertEqual(codes(f, "error"), ["required"])
        self.assertIn("str", f[0].message)

    def test_bool_is_not_int(self):
        f = check("n = true\n", requires=["n:int"])
        self.assertEqual(codes(f, "error"), ["required"])

    def test_unknown_type_name_rejected(self):
        with self.assertRaises(ValueError):
            tv.parse_require("a:integer")

    def test_path_through_non_table_is_missing(self):
        f = check("a = 1\n", requires=["a.b"])
        self.assertEqual(codes(f, "error"), ["required"])


class Pep621Test(unittest.TestCase):
    def run_profile(self, text, **kw):
        return tv.validate_bytes("pyproject.toml", text.encode(), profile="pep621", **kw)

    def test_good_project_passes(self):
        self.assertEqual(self.run_profile(GOOD_PYPROJECT), [])

    def test_missing_name(self):
        f = self.run_profile('[project]\nversion = "1"\n')
        self.assertEqual(codes(f, "error"), ["pep621"])
        self.assertIn("project.name", f[0].message)

    def test_missing_version_unless_dynamic(self):
        self.assertEqual(codes(self.run_profile('[project]\nname = "d"\n'), "error"), ["pep621"])
        self.assertEqual(self.run_profile('[project]\nname = "d"\ndynamic = ["version"]\n'), [])

    def test_name_cannot_be_dynamic(self):
        f = self.run_profile('[project]\nname = "d"\nversion = "1"\ndynamic = ["name"]\n')
        self.assertEqual(codes(f, "error"), ["pep621"])

    def test_version_both_static_and_dynamic(self):
        f = self.run_profile('[project]\nname = "d"\nversion = "1"\ndynamic = ["version"]\n')
        self.assertEqual(codes(f, "error"), ["pep621"])

    def test_non_string_version(self):
        f = self.run_profile('[project]\nname = "d"\nversion = 1\n')
        self.assertIn("pep621", codes(f, "error"))

    def test_profile_ignores_other_filenames(self):
        f = tv.validate_bytes("other.toml", b'[project]\nversion = "1"\n', profile="pep621")
        self.assertEqual(f, [])

    def test_no_project_table_ok_unless_required(self):
        text = "[build-system]\nrequires = []\n"
        self.assertEqual(self.run_profile(text), [])
        self.assertEqual(codes(self.run_profile(text, require_project=True), "error"), ["pep621"])


class ScanAndCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "ok.toml").write_text("a = 1\n", encoding="utf-8")
        (self.root / "sub").mkdir()
        (self.root / "sub" / "bad.toml").write_text("a = \n", encoding="utf-8")
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "skip.toml").write_text("a = \n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOLS / "toml_validator.py"), *args],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        )

    def test_directory_scan_skips_vendored_dirs(self):
        count, findings = tv.run([str(self.root)])
        self.assertEqual(count, 2)
        self.assertEqual({Path(f.path).name for f in findings if f.severity == "error"}, {"bad.toml"})

    def test_cli_exit_code_1_on_error_and_0_when_clean(self):
        self.assertEqual(self.cli(str(self.root)).returncode, 1)
        self.assertEqual(self.cli(str(self.root / "ok.toml")).returncode, 0)

    def test_cli_strict_turns_warning_into_failure(self):
        warn = self.root / "w.toml"
        warn.write_text("python_version = 3.10\n", encoding="utf-8")
        self.assertEqual(self.cli(str(warn)).returncode, 0)
        self.assertEqual(self.cli(str(warn), "--strict").returncode, 1)

    def test_cli_json_output(self):
        proc = self.cli(str(self.root / "sub" / "bad.toml"), "--format", "json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["files"], 1)
        self.assertEqual(data["findings"][0]["code"], "parse")

    def test_cli_bad_require_type_is_usage_error(self):
        self.assertEqual(self.cli(str(self.root / "ok.toml"), "--require", "a:nope").returncode, 2)

    def test_cli_no_files_is_usage_error(self):
        empty = self.root / "empty"
        empty.mkdir()
        self.assertEqual(self.cli(str(empty)).returncode, 2)

    def test_repo_pyproject_style_file_end_to_end(self):
        p = self.root / "pyproject.toml"
        p.write_text(GOOD_PYPROJECT, encoding="utf-8")
        self.assertEqual(self.cli(str(p), "--profile", "pep621", "--require", "project.name:str").returncode, 0)
        p.write_text('[project]\nname = "d"\n', encoding="utf-8")
        self.assertEqual(self.cli(str(p), "--profile", "pep621").returncode, 1)


if __name__ == "__main__":
    unittest.main()
