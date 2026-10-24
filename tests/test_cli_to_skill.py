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


if __name__ == "__main__":
    unittest.main()
