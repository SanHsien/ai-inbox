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

    def test_json_null_fields_are_treated_as_absent(self):
        # 其他語言產生的 JSON 常把沒有的欄位寫成 null：dict.get 的預設值只管「鍵不存在」，null 會原樣穿過去
        output = convert_cli_to_skill({
            "name": "nulls",
            "description": None,
            "triggers": None,
            "commands": [{"name": "run", "args": None, "description": None}],
        })
        self.assertIn("### `nulls run`", output)
        self.assertIn('- "nulls"', output)  # triggers 缺省時預設為 [name]
        output = convert_cli_to_skill({"name": "nulls", "commands": None})
        self.assertIn("## 2. 支援子指令清單", output)

    def test_wrong_container_types_raise_value_error_not_type_error(self):
        # main() 只接 OSError／ValueError；TypeError 會變成整段 traceback
        for field, bad in (("commands", "run"), ("commands", 3), ("triggers", 3), ("triggers", {"a": 1})):
            with self.subTest(field=field, bad=bad):
                with self.assertRaises(ValueError):
                    convert_cli_to_skill({"name": "x", field: bad})
        with self.assertRaises(ValueError):
            convert_cli_to_skill({"name": "x", "commands": [{"name": "r", "args": "--a"}]})

    def test_main_reports_wrongly_typed_schema_without_traceback(self):
        import io
        import tempfile
        from contextlib import redirect_stderr

        from tools import cli_to_skill

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"name": "x", "commands": 3}', encoding="utf-8")
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(cli_to_skill.main([str(path)]), 1)
        self.assertIn("錯誤", err.getvalue())


    def test_scalars_yaml_would_not_read_as_strings_are_quoted(self):
        # 名稱叫 yes／no／on／true／null 或像數字、日期的 CLI：不加引號時 YAML 會讀成布林、null、數字、日期，
        # SKILL.md 的 name／description 就不是字串了
        for risky in ("yes", "No", "true", "FALSE", "null", "~", "on", "Off", "123", "1.5", "1e3", "0x1F",
                      "2026-10-26", ".inf"):
            with self.subTest(risky=risky):
                output = convert_cli_to_skill({"name": risky, "description": risky, "triggers": []})
                front = output.split("---")[1]
                self.assertIn(f'name: "{risky}"', front)
                self.assertIn(f'description: "{risky}"', front)

    def test_ordinary_scalars_stay_unquoted(self):
        for plain in ("sample-tool", "yes-man", "v1", "ffmpeg2", "hello world"):
            with self.subTest(plain=plain):
                front = convert_cli_to_skill({"name": plain, "description": plain}).split("---")[1]
                self.assertIn(f"name: {plain}\n", front)

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
