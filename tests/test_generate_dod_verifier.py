"""tools/generate_dod_verifier.py 的單元測試：DoD 解析、白名單、注入防護，以及「產生的腳本真的能判紅綠」。"""

import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "generate_dod_verifier.py"
sys.path.insert(0, str(TOOL.parent))
import generate_dod_verifier as g  # noqa: E402

# 以下三段是 repo 內真實任務的 DoD 原文
DOD_TOOL = (
    '產出 `tools/render_artifact_html.py` 與 `tests/test_render_artifact_html.py`，'
    '通過 `python -m unittest discover -s tests -p "test_render_artifact_html.py"`。'
)
DOD_DOC = (
    "產出 `docs/visual-agent-artifacts-engineering-spec.md`，內含架構原理、Draft 語法規格、8x Token 節流實測數據與互動回饋機制；"
    "以 `Test-Path docs/visual-agent-artifacts-engineering-spec.md` 驗證存在。"
)
DOD_PROSE = "在本地終端跑通 minimal example，確認無 Windows 路徑報錯，並在工作筆記中記錄安裝指令與執行輸出。"


def run_script(script_text, cwd, *args):
    p = Path(cwd) / "verify_delivery.py"
    p.write_text(script_text, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(p), "--root", str(cwd), *args], capture_output=True, text=True, encoding="utf-8"
    )
    return proc.returncode, proc.stdout


class ParseDodTest(unittest.TestCase):
    def test_tool_dod_gives_files_and_command_and_no_manual(self):
        plan = g.plan_from_dod(DOD_TOOL)
        paths = [c["path"] for c in plan["checks"] if c["type"] == "file_exists"]
        self.assertEqual(sorted(paths), ["tests/test_render_artifact_html.py", "tools/render_artifact_html.py"])
        cmds = [c["argv"] for c in plan["checks"] if c["type"] == "command"]
        self.assertEqual(
            cmds, [["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_render_artifact_html.py"]]
        )
        self.assertEqual(plan["manual"], [])

    def test_doc_dod_keeps_content_requirement_as_manual(self):
        plan = g.plan_from_dod(DOD_DOC)
        self.assertEqual([c["path"] for c in plan["checks"]], ["docs/visual-agent-artifacts-engineering-spec.md"])
        self.assertEqual(len(plan["manual"]), 1)  # 「內含…」不能靠檔案存在驗證，也不做關鍵字檢查
        self.assertIn("內含架構原理", plan["manual"][0])

    def test_prose_only_dod_has_no_auto_checks(self):
        plan = g.plan_from_dod(DOD_PROSE)
        self.assertEqual(plan["checks"], [])
        self.assertEqual(len(plan["manual"]), 3)

    def test_test_path_and_backtick_path_are_deduplicated(self):
        plan = g.plan_from_dod("產出 `docs/a.md`；以 `Test-Path docs/a.md` 驗證存在。")
        self.assertEqual(len(plan["checks"]), 1)
        self.assertEqual(plan["manual"], [])

    def test_unsafe_paths_become_manual(self):
        for bad in ("../secret.txt", "C:\\Windows\\x.txt", "/etc/passwd"):
            with self.subTest(bad=bad):
                plan = g.plan_from_dod(f"以 `Test-Path {bad}` 驗證存在")
                self.assertEqual([c for c in plan["checks"] if c["type"] == "file_exists"], [])
                self.assertTrue(any("不安全" in m for m in plan["manual"]))

    def test_disallowed_commands_become_manual_not_checks(self):
        for cmd in (
            "python -c \"import os; os.system('x')\"",
            "python -m unittest; rm -rf /",
            "python -m unittest discover -s ../other",
            "python -m pip install evil",
            "python tools/other.py",
        ):
            with self.subTest(cmd=cmd):
                plan = g.plan_from_dod(f"通過 `{cmd}`")
                self.assertEqual([c for c in plan["checks"] if c["type"] == "command"], [])
                self.assertTrue(any("允許清單" in m for m in plan["manual"]))


class ValidatorTest(unittest.TestCase):
    def test_unittest_whitelist(self):
        ok = [
            ["python", "-m", "unittest"],
            ["python", "-m", "unittest", "discover", "-s", "tests"],
            ["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_x.py", "-v"],
            ["python", "-m", "unittest", "tests.test_x"],
        ]
        bad = [
            ["python", "-m", "pytest"],
            ["python", "-m", "unittest", "-s"],
            ["python", "-m", "unittest", "-s", "/abs"],
            ["python", "-m", "unittest", "-s", "C:x"],
            ["python", "-m", "unittest", "a;b"],
            ["python", "-m", "unittest", "--help"],
            ["sh", "-m", "unittest"],
            [],
        ]
        for a in ok:
            self.assertTrue(g.validate_unittest_argv(a), a)
        for a in bad:
            self.assertFalse(g.validate_unittest_argv(a), a)

    def test_validate_check_rejects_bad_specs(self):
        bad = [
            {"type": "shell", "cmd": "rm -rf /"},
            {"type": "file_exists", "path": "../x"},
            {"type": "env", "name": "A B"},
            {"type": "http", "url": "file:///etc/passwd"},
            {"type": "http", "url": "http://x/", "status": 99},
            {"type": "html_element", "file": "a.html", "tag": "div><script"},
            {"type": "command", "argv": "rm -rf /"},
        ]
        for c in bad:
            with self.subTest(c=c), self.assertRaises(ValueError):
                g.validate_check(c)

    def test_plan_from_spec_requires_checks_list(self):
        with self.assertRaises(ValueError):
            g.plan_from_spec({"title": "x"})


class GeneratedScriptTest(unittest.TestCase):
    def test_pass_and_fail_on_file_exists(self):
        script = g.generate_script({"checks": [{"type": "file_exists", "path": "a/b.txt"}], "manual": []}, "t")
        with tempfile.TemporaryDirectory() as d:
            code, out = run_script(script, d)
            self.assertEqual(code, 1, out)  # 反例：檔案不存在必須紅
            self.assertIn("[FAIL] file_exists", out)
            (Path(d) / "a").mkdir()
            (Path(d) / "a" / "b.txt").write_text("x")
            code, out = run_script(script, d)
            self.assertEqual(code, 0, out)
            self.assertIn("[PASS] file_exists", out)

    def test_env_check(self):
        script = g.generate_script(
            {"checks": [{"type": "env", "name": "DOD_TEST_VAR", "equals": "yes"}], "manual": []}, "t"
        )
        with tempfile.TemporaryDirectory() as d:
            os.environ.pop("DOD_TEST_VAR", None)
            self.assertEqual(run_script(script, d)[0], 1)
            os.environ["DOD_TEST_VAR"] = "no"
            try:
                self.assertEqual(run_script(script, d)[0], 1)
                os.environ["DOD_TEST_VAR"] = "yes"
                self.assertEqual(run_script(script, d)[0], 0)
            finally:
                os.environ.pop("DOD_TEST_VAR", None)

    def test_html_element_check(self):
        checks = [
            {"type": "html_element", "file": "p.html", "tag": "button", "id": "go", "text_contains": "送出"},
        ]
        script = g.generate_script({"checks": [g.validate_check(c) for c in checks], "manual": []}, "t")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "p.html").write_text('<div><button id="stop">送出</button></div>', encoding="utf-8")
            self.assertEqual(run_script(script, d)[0], 1)  # id 不符
            (Path(d) / "p.html").write_text('<div><button id="go"><b>請</b>送出</button></div>', encoding="utf-8")
            self.assertEqual(run_script(script, d)[0], 0)
            (Path(d) / "p.html").write_text('<div><button id="go">取消</button></div>', encoding="utf-8")
            self.assertEqual(run_script(script, d)[0], 1)  # 文字不符

    def test_http_check_against_local_server(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200 if self.path == "/health" else 404)
                self.end_headers()

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            base = f"http://127.0.0.1:{srv.server_address[1]}"
            good = g.generate_script({"checks": [g.validate_check({"type": "http", "url": base + "/health"})], "manual": []}, "t")
            wrong = g.generate_script({"checks": [g.validate_check({"type": "http", "url": base + "/nope"})], "manual": []}, "t")
            expect404 = g.generate_script(
                {"checks": [g.validate_check({"type": "http", "url": base + "/nope", "status": 404})], "manual": []}, "t"
            )
            with tempfile.TemporaryDirectory() as d:
                self.assertEqual(run_script(good, d)[0], 0)
                self.assertEqual(run_script(wrong, d)[0], 1)
                self.assertEqual(run_script(expect404, d)[0], 0)
                code, out = run_script(wrong, d, "--no-network")
                self.assertEqual(code, 0)
                self.assertIn("[SKIP]", out)
        finally:
            srv.shutdown()
            srv.server_close()

    def test_commands_skipped_by_default_and_run_only_with_flag(self):
        plan = g.plan_from_dod('通過 `python -m unittest discover -s tests -p "test_*.py"`')
        script = g.generate_script(plan, "t")
        with tempfile.TemporaryDirectory() as d:
            tests = Path(d) / "tests"
            tests.mkdir()
            marker = Path(d) / "ran.txt"
            (tests / "test_m.py").write_text(
                "import unittest\nfrom pathlib import Path\n"
                f"class T(unittest.TestCase):\n    def test_a(self):\n        Path(r'{marker}').write_text('x')\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            code, out = run_script(script, d)
            self.assertEqual(code, 0, out)
            self.assertIn("[SKIP] command", out)
            self.assertFalse(marker.exists(), "預設不得執行任何指令")
            self.assertEqual(run_script(script, d, "--strict")[0], 3)
            code, out = run_script(script, d, "--run-commands")
            self.assertEqual(code, 0, out)
            self.assertTrue(marker.exists())
            (tests / "test_m.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.fail('x')\n", encoding="utf-8"
            )
            code, out = run_script(script, d, "--run-commands")
            self.assertEqual(code, 1, out)  # 反例：測試紅燈，驗收也必須紅

    def test_manual_items_listed_and_strict(self):
        plan = g.plan_from_dod(DOD_DOC)
        script = g.generate_script(plan, "t")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "docs").mkdir()
            (Path(d) / "docs" / "visual-agent-artifacts-engineering-spec.md").write_text("x")
            code, out = run_script(script, d)
            self.assertEqual(code, 0, out)
            self.assertIn("[MANUAL]", out)
            self.assertEqual(run_script(script, d, "--strict")[0], 3)

    def test_json_report(self):
        script = g.generate_script({"checks": [{"type": "file_exists", "path": "x"}], "manual": ["人工"]}, "t")
        with tempfile.TemporaryDirectory() as d:
            code, out = run_script(script, d, "--json")
            data = json.loads(out)
            self.assertEqual(code, 1)
            self.assertEqual(data["results"][0]["status"], "FAIL")
            self.assertEqual(data["manual"], ["人工"])


class InjectionTest(unittest.TestCase):
    def test_hostile_dod_text_stays_data(self):
        evil = "'''; import os; os.system('echo pwned > pwned.txt') #\"\"\"\n"
        plan = g.plan_from_dod(f"產出 `docs/a.md`，{evil}")
        script = g.generate_script(plan, evil)
        compile(script, "verify_delivery.py", "exec")  # 必須仍是合法 Python
        with tempfile.TemporaryDirectory() as d:
            code, out = run_script(script, d)
            self.assertEqual(code, 1)  # docs/a.md 不存在
            self.assertFalse((Path(d) / "pwned.txt").exists())
            self.assertFalse(Path("pwned.txt").exists())

    def test_generating_does_not_execute_commands(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / "ran.txt"
            (Path(d) / "test_x.py").write_text(f"open(r'{marker}','w').write('x')\n", encoding="utf-8")
            plan = g.plan_from_dod("通過 `python -m unittest test_x`")
            g.generate_script(plan, "t")
            self.assertFalse(marker.exists())


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        env = {**os.environ, "PYTHONUTF8": "1"}
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, encoding="utf-8", env=env)

    def test_text_plan_and_output_file(self):
        proc = self.run_cli("--text", DOD_TOOL, "--plan")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(json.loads(proc.stdout)["checks"]), 3)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "v.py"
            proc = self.run_cli("--text", DOD_TOOL, "-o", str(out))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            compile(out.read_text(encoding="utf-8"), str(out), "exec")

    def test_unknown_task_and_bad_spec_exit_2(self):
        self.assertEqual(self.run_cli("--task", "T-00000000-99").returncode, 2)
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "s.json"
            spec.write_text(json.dumps({"checks": [{"type": "shell", "cmd": "x"}]}), encoding="utf-8")
            self.assertEqual(self.run_cli("--spec", str(spec)).returncode, 2)

    def test_real_repo_task_and_open_summary(self):
        proc = self.run_cli("--open-summary")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for line in proc.stdout.strip().splitlines():
            self.assertEqual(len(line.split("\t")), 4, line)

    def test_help_utf8_under_cp950(self):
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        proc = subprocess.run([sys.executable, str(TOOL), "--help"], capture_output=True, env=env)
        self.assertEqual(proc.returncode, 0)
        proc.stdout.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
