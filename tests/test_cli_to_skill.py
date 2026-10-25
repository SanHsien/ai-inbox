#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli_to_skill.py 單元測試
驗證 CLI 中繼描述檔 (JSON) 能正確轉換為符合協議的 SKILL.md。
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 讓 `tools` 套件不依賴執行目錄
from tools.cli_to_skill import convert_cli_to_skill


class TestCliToSkill(unittest.TestCase):
    def test_basic_conversion(self):
        schema = {
            "name": "sample-tool",
            "version": "1.0.0",
            "description": "測試用範例 CLI 工具",
            "triggers": ["sample-tool", "測試工具"],
            "commands": [
                {
                    "name": "run",
                    "description": "執行任務",
                    "destructive": False,
                    "args": [
                        {"name": "--input", "required": True, "type": "string", "help": "輸入路徑"}
                    ]
                },
                {
                    "name": "purge",
                    "description": "清除快取",
                    "destructive": True,
                    "args": [
                        {"name": "--force", "required": False, "type": "boolean", "default": False, "help": "強制刪除"}
                    ]
                }
            ]
        }

        output = convert_cli_to_skill(schema)

        # 驗證 frontmatter
        self.assertIn("name: sample-tool", output)
        self.assertIn("description: 測試用範例 CLI 工具", output)
        self.assertIn('- "sample-tool"', output)
        self.assertIn('- "測試工具"', output)

        # 驗證指令與參數
        self.assertIn("### `sample-tool run`", output)
        self.assertIn("### `sample-tool purge`", output)
        self.assertIn("`--input` [必填, string]", output)

        # 驗證高危指令警示區塊
        self.assertIn("[!CAUTION] 高危破壞性指令", output)
        self.assertIn("Blast Radius: High", output)

    def test_frontmatter_special_chars_are_quoted(self):
        schema = {
            "name": "evil",
            "description": "desc: with colon\nsecond line # not comment",
            "triggers": ['say "hi"', "plain"],
        }
        output = convert_cli_to_skill(schema)
        front = output.split("---")[1]
        self.assertIn('description: "desc: with colon second line # not comment"', front)
        self.assertIn(r'- "say \"hi\""', front)
        # frontmatter 內不得因說明文字換行而多出任何看似新鍵的行
        keys = [ln for ln in front.splitlines() if ln and not ln.startswith(" ")]
        self.assertEqual(keys, ["name: evil", 'description: "desc: with colon second line # not comment"', "triggers:"])

    def test_malformed_schema_entries_do_not_crash(self):
        output = convert_cli_to_skill({"name": "x", "commands": ["bad", {"name": "ok", "args": [None, {"name": "--a"}]}]})
        self.assertIn("### `x ok`", output)
        with self.assertRaises(ValueError):
            convert_cli_to_skill(["not", "a", "dict"])

    def test_main_reports_missing_file_without_traceback(self):
        import io
        from contextlib import redirect_stderr
        from unittest import mock

        from tools import cli_to_skill

        err = io.StringIO()
        with mock.patch.object(sys, "argv", ["cli_to_skill.py", "no_such_file.json"]), redirect_stderr(err):
            self.assertEqual(cli_to_skill.main(), 1)
        self.assertIn("錯誤", err.getvalue())


if __name__ == "__main__":
    unittest.main()
