#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-Native CLI to SKILL.md 自動轉換工具
依據 CLI-Anything to Skill Protocol (docs/cli-anything-to-skill-protocol.md)，
將 CLI 中繼描述檔 (JSON) 自動轉換為 Antigravity / Claude Code 相容之 SKILL.md。
"""

import json
import re
import sys
from typing import Any, Dict

# 需要加引號才不會被 YAML 誤判的內容（冒號空白、井號註解、換行、特殊起始字元等）
_YAML_UNSAFE = re.compile(r"[\n\r\t]|: | #|:$|^[\s\-?:,\[\]{}#&*!|>'\"%@`]|\s$")


def _yaml_scalar(value: Any) -> str:
    """產生 frontmatter 用的 YAML 純量；內含特殊字元時以 JSON 雙引號字串輸出（亦為合法 YAML）。"""
    text = "" if value is None else str(value)
    if not text or _YAML_UNSAFE.search(text):
        return json.dumps(text, ensure_ascii=False)
    return text


def _one_line(value: Any) -> str:
    """壓成單行，避免內文換行破壞 Markdown 清單結構。"""
    return " ".join(("" if value is None else str(value)).split())


def convert_cli_to_skill(cli_schema: Dict[str, Any]) -> str:
    """將 CLI 描述物件轉換為合規的 SKILL.md 內容。"""
    if not isinstance(cli_schema, dict):
        raise ValueError("CLI 描述檔最外層必須是 JSON 物件")
    name = _one_line(cli_schema.get("name", "unnamed-cli")) or "unnamed-cli"
    description = _one_line(cli_schema.get("description", "Agent-Native CLI 工具封裝"))
    triggers = cli_schema.get("triggers", [name])
    if isinstance(triggers, str):
        triggers = [triggers]
    version = _one_line(cli_schema.get("version", "1.0.0"))
    commands = cli_schema.get("commands", [])

    lines = []
    # Frontmatter
    lines.append("---")
    lines.append(f"name: {_yaml_scalar(name)}")
    lines.append(f"description: {_yaml_scalar(description)}")
    lines.append("triggers:")
    for trig in triggers:
        lines.append(f"  - {json.dumps(_one_line(trig), ensure_ascii=False)}")
    lines.append("---")
    lines.append("")

    # Title & Metadata
    lines.append(f"# {name} Agent Skill")
    lines.append("")
    lines.append(f"> 由 CLI-Anything to Skill Protocol 自動生成。封裝版本：`v{version}`。")
    lines.append("")

    # General Instructions
    lines.append("## 1. 執行規範與標準參數")
    lines.append("")
    lines.append("- 所有指令呼叫預設必須帶有 `--json` 參數以取得結構化輸出。")
    lines.append("- 指令執行環境需具備目標 CLI 執行檔（檢查 Exit Code 127）。")
    lines.append("")

    # Command Tree
    lines.append("## 2. 支援子指令清單")
    lines.append("")

    for cmd in commands:
        if not isinstance(cmd, dict):
            continue
        cmd_name = _one_line(cmd.get("name", "action"))
        cmd_desc = _one_line(cmd.get("description", ""))
        destructive = cmd.get("destructive", False)
        args = cmd.get("args", [])

        lines.append(f"### `{name} {cmd_name}`")
        lines.append("")
        lines.append(f"- **功能說明**：{cmd_desc}")

        if destructive:
            lines.append("- **安全警示**：")
            lines.append("  > [!CAUTION] 高危破壞性指令")
            lines.append("  > 本操作具備破壞性（Blast Radius: High），Agent 嚴禁自主執行，必須先明確向使用者列出受影響路徑並取得確認。")

        if args:
            lines.append("- **參數規格**：")
            for arg in args:
                if not isinstance(arg, dict):
                    continue
                arg_name = _one_line(arg.get("name", ""))
                arg_req = "必填" if arg.get("required") else "選填"
                arg_type = _one_line(arg.get("type", "string"))
                arg_help = _one_line(arg.get("help", ""))
                default_val = arg.get("default")
                def_str = f"（預設：`{default_val}`）" if default_val is not None else ""
                lines.append(f"  - `{arg_name}` [{arg_req}, {arg_type}]：{arg_help}{def_str}")

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    # Windows cp950 終端遇到無法編碼的字元（例如 emoji）不應崩潰
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass

    if len(sys.argv) < 2:
        print("用法: python tools/cli_to_skill.py <cli_schema.json> [output_skill.md]")
        return 1

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        with open(input_path, "r", encoding="utf-8-sig") as f:
            schema = json.load(f)
        skill_content = convert_cli_to_skill(schema)
    except (OSError, ValueError) as err:  # JSONDecodeError 是 ValueError 的子類別
        print(f"錯誤：無法讀取或轉換 '{input_path}'：{err}", file=sys.stderr)
        return 1

    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(skill_content)
        except OSError as err:
            print(f"錯誤：無法寫入 '{output_path}'：{err}", file=sys.stderr)
            return 1
        print(f"已產出 Skill 檔案至: {output_path}")
    else:
        print(skill_content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
