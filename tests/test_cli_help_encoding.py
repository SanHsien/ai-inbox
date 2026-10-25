"""每支 tools/*.py 的 --help 在 cp950 環境下都要輸出合法 UTF-8。

Windows 管線預設用系統編碼（cp950）。工具若在 argparse 之後才把輸出改成 UTF-8，
--help 會在改之前就印出來，Agent 讀到的是亂碼；沒有 argparse 的工具甚至會把 --help 當成檔名。
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
SKIP = {"_judge_common.py"}  # 共用模組，不是指令


class CliHelpEncodingTest(unittest.TestCase):
    def test_every_tool_help_is_utf8_under_cp950(self):
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        tools = sorted(p for p in TOOLS.glob("*.py") if p.name not in SKIP)
        self.assertGreater(len(tools), 0)
        for tool in tools:
            with self.subTest(tool=tool.name):
                proc = subprocess.run(
                    [sys.executable, str(tool), "--help"], capture_output=True, env=env, timeout=60
                )
                self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace")[-300:])
                text = proc.stdout.decode("utf-8")  # 不是 UTF-8 會在這裡丟 UnicodeDecodeError
                self.assertIn("usage", text)


if __name__ == "__main__":
    unittest.main()
