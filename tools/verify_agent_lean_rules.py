#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Lean Rules Auditor (verify_agent_lean_rules.py)
-----------------------------------------------------
落實麥克風 8 條極簡規約：
1. 300 行預算制：單次程式碼修改若預計超過 300 行，必須帶有說明理由（EXPLANATION）。
2. 規則淨零增長：檢查規則檔案（如 AGENTS.md, CLAUDE.md）行數與條目，防止規約通膨。
"""

import os
import sys
import argparse
from typing import Dict, Any, List, Optional, Tuple

# 確保在 Windows CP950 等環境下輸出為 UTF-8（通過 test_cli_help_encoding 契約）
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def count_lines_in_text(text: str) -> int:
    """計算非空行數"""
    lines = [line.strip() for line in text.splitlines()]
    return len([l for l in lines if l])


def audit_change_size(
    line_count: int,
    max_budget: int = 300,
    has_explanation: bool = False,
    explanation_text: Optional[str] = None
) -> Tuple[bool, str]:
    """
    審查單次修改規模（300 行預算制）：
    - 行數 <= max_budget：放行
    - 行數 > max_budget 且具備有效理由（>= 10 字元）：放行並記錄理由
    - 行數 > max_budget 但無理由：阻擋並警告
    """
    if line_count <= max_budget:
        return True, f"[PASS] 程式碼規模在預算內（{line_count}/{max_budget} 行）。"

    if has_explanation and explanation_text and len(explanation_text.strip()) >= 10:
        return True, (
            f"[PASS-WITH-REASON] 變更共 {line_count} 行（超過 {max_budget} 行上限），"
            f"已附帶超額理由：\"{explanation_text.strip()}\""
        )

    return False, (
        f"[VIOLATION] 變更共 {line_count} 行，超過 {max_budget} 行上限且未附帶有效說明理由！"
        f"（請簡要說明為何此變更必須超過 300 行，例如：資料結構定義或完整測試覆蓋）"
    )


def audit_ruleset_bloat(
    rule_file_path: str,
    max_lines: int = 500,
    max_rules: int = 30
) -> Tuple[bool, Dict[str, Any]]:
    """
    審查規則檔是否過度膨脹（防範規約通膨）：
    檢查行數與可能包含的規則編號數量
    """
    if not os.path.exists(rule_file_path):
        return False, {"error": f"找不到規則檔：{rule_file_path}"}

    with open(rule_file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.splitlines()
    total_lines = len(lines)
    non_empty_lines = len([l for l in lines if l.strip()])

    import re
    # 統計編號規則數（例如 1. / 10. / - [ ] / * / ## 規則標題）
    rule_pattern = re.compile(r'^\s*(?:\d+[\.\)]|[-*]\s+\[?|[#]{2,4}\s+)')
    rule_markers = [l for l in lines if rule_pattern.match(l)]
    rule_count = len(rule_markers)

    is_bloated = total_lines > max_lines or rule_count > max_rules

    report = {
        "file_path": rule_file_path,
        "total_lines": total_lines,
        "non_empty_lines": non_empty_lines,
        "detected_rule_items": rule_count,
        "max_lines": max_lines,
        "max_rules": max_rules,
        "is_bloated": is_bloated
    }

    if is_bloated:
        return False, report
    return True, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Lean Rules Auditor")
    parser.add_argument("--lines", type=int, default=0, help="變更行數")
    parser.add_argument("--reason", type=str, default="", help="超額理由")
    parser.add_argument("--audit-rule-file", type=str, default="", help="審查規則檔案")
    args = parser.parse_args()

    if args.audit_rule_file:
        ok, report = audit_ruleset_bloat(args.audit_rule_file)
        if ok:
            print(f"[PASS] 規則檔精實合格：{report['file_path']}（{report['total_lines']} 行，約 {report['detected_rule_items']} 項規則）")
            return 0
        else:
            print(f"[WARN] 規則檔可能存在通膨風險：{report}")
            return 1

    if args.lines > 0:
        ok, msg = audit_change_size(args.lines, max_budget=300, has_explanation=bool(args.reason), explanation_text=args.reason)
        print(msg)
        return 0 if ok else 1

    print("[INFO] 請提供 --lines 或 --audit-rule-file 參數。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
