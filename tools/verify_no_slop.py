#!/usr/bin/env python3
"""
tools/verify_no_slop.py
靜態檢測 HTML / CSS 代碼中的典型 AI 罐頭設計特徵（Anti-AI-Slop Linter）。
僅使用 Python 標準函式庫。

對照規範：docs/anti-ai-slop-frontend.md
規則項目：
  SLOP-01: 浮誇無腦陰影 (shadow-2xl, 巨大半透明擴散 box-shadow)
  SLOP-02: 俗套藍紫漸層 (from-indigo, to-purple, linear-gradient 藍紫霓虹)
  SLOP-03: 無意義裝飾 Emoji (🚀, 💡, 🔥, ✨, 🎉, 🔮, 🪄, 🌟)
  SLOP-04: 虛假動態徽章 / 偽 LIVE (無即時流卻閃爍或偽 LIVE 呼吸燈)
  SLOP-05: AI 罐頭廢話黑話 (delve, elevate, seamlessly, revolutionize, 等 350+ 模型黑話)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _judge_common import ensure_utf8_output  # noqa: E402


@dataclass
class SlopViolation:
    rule_id: str
    rule_name: str
    line_number: int
    matched_text: str
    snippet: str
    file_path: str


# 剝離 HTML 與 CSS 註解，保留換行以確保行號對齊
def strip_comments(text: str) -> str:
    def replacer(match: re.Match) -> str:
        s = match.group(0)
        return "\n" * s.count("\n") + " " * (len(s) - s.count("\n"))

    # HTML 註解 <!-- ... -->
    text = re.sub(r"<!--[\s\S]*?-->", replacer, text)
    # CSS / C-style 註解 /* ... */
    text = re.sub(r"/\*[\s\S]*?\*/", replacer, text)
    return text


RULES = [
    (
        "SLOP-01",
        "浮誇無腦陰影",
        re.compile(
            r"\bshadow-(?:2xl|xl)\b|"
            r"box-shadow:\s*0(?:px)?\s+(?:2[0-9]|[3-9][0-9])px|"
            r"box-shadow:[^;]*(?:rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*(?:0\.[3-9]|[1-9])\)|50px)",
            re.IGNORECASE,
        ),
        "禁止使用高擴散、厚重黑色模糊陰影，請改用 1px 實色邊框與表面分層",
    ),
    (
        "SLOP-02",
        "俗套藍紫漸層",
        re.compile(
            r"\bfrom-indigo-(?:500|600)\b|\bto-purple-(?:500|600)\b|"
            r"\bvia-purple-(?:500|600)\b|\bto-pink-(?:500|600)\b|"
            r"linear-gradient\([^)]*(?:#6366f1|#a855f7|#ec4899|indigo|purple|violet)",
            re.IGNORECASE,
        ),
        "禁止使用俗套藍紫/霓虹漸層，請改用實色單色調對比",
    ),
    (
        "SLOP-03",
        "無意義裝飾 Emoji",
        re.compile(r"[🚀💡🔥✨🎉🔮🪄🌟]"),
        "禁止在標題或列表中使用裝飾性 Emoji，請改用語意化排版或結構化圖示",
    ),
    (
        "SLOP-04",
        "虛假動態徽章 / 偽 LIVE",
        re.compile(
            r"\[LIVE\]|"
            r"\b(?:animate-ping|animate-pulse)\b|"
            r">\s*LIVE\s*<|"
            r"\b(?:fake-live|badge-live)\b",
            re.IGNORECASE,
        ),
        "禁止使用未連接真實動態流的假 LIVE 呼吸燈或徽章",
    ),
    (
        "SLOP-05",
        "AI 罐頭黑話文案",
        re.compile(
            r"\b(?:delv(?:e[sd]?|ing)|seamless(?:ly)?|elevat(?:e[sd]?|ing)|revolutioniz(?:e[sd]?|ing)|"
            r"tapestry|empower(?:s|ed|ing|ment)?|unleash(?:e[sd]|ing)?|game-?changers?|vibe-coding)\b",
            re.IGNORECASE,
        ),
        "禁止使用空洞 AI 行銷陳腔濫調，請改用具體客觀數據與活人文案",
    ),
]


def scan_text(text: str, filename: str = "<stdin>") -> list[SlopViolation]:
    clean = strip_comments(text)
    violations: list[SlopViolation] = []
    lines = clean.splitlines()

    for rule_id, rule_name, pattern, _desc in RULES:
        for idx, line in enumerate(lines, 1):
            for match in pattern.finditer(line):
                matched = match.group(0).strip()
                snippet = line.strip()
                violations.append(
                    SlopViolation(
                        rule_id=rule_id,
                        rule_name=rule_name,
                        line_number=idx,
                        matched_text=matched,
                        snippet=snippet[:100],
                        file_path=filename,
                    )
                )

    return sorted(violations, key=lambda v: (v.file_path, v.line_number, v.rule_id))


def scan_file(path: Path) -> list[SlopViolation]:
    if not path.is_file():
        return []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as err:
        print(f"[ERROR] 無法讀取檔案 {path}: {err}", file=sys.stderr)
        return []
    return scan_text(content, filename=str(path))


def format_report(violations: list[SlopViolation]) -> str:
    if not violations:
        return "[PASS] 零罐頭特徵 (0 violations found)！"

    out = [f"[FAIL] 檢測到 {len(violations)} 處 AI 罐頭設計特徵："]
    for v in violations:
        out.append(
            f"  - [{v.rule_id} {v.rule_name}] {v.file_path}:{v.line_number} -> 違規片段: \"{v.matched_text}\""
        )
        out.append(f"    上下文: {v.snippet}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_output()
    parser = argparse.ArgumentParser(description="靜態檢測 HTML / CSS 中的 AI 罐頭設計特徵")
    parser.add_argument("paths", nargs="*", help="要掃描的 HTML 或 CSS 檔案或目錄路徑（預設: assets/）")
    args = parser.parse_args(argv)

    target_paths = [Path(p) for p in args.paths] if args.paths else [
        Path(__file__).resolve().parent.parent / "assets"
    ]

    all_violations: list[SlopViolation] = []
    scanned_count = 0

    for p in target_paths:
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.suffix.lower() in (".html", ".htm", ".css"):
                    all_violations.extend(scan_file(f))
                    scanned_count += 1
        elif p.is_file():
            all_violations.extend(scan_file(p))
            scanned_count += 1
        else:
            print(f"[WARN] 路徑不存在：{p}", file=sys.stderr)

    if scanned_count == 0:
        # 沒掃到任何檔案不能算通過（避免路徑打錯或目錄為空時恆 PASS）
        print("[ERROR] 未掃描到任何 HTML/CSS 檔案，無法判定 (0 files scanned)", file=sys.stderr)
        return 2

    report = format_report(all_violations)
    print(f"[*] 已掃描 {scanned_count} 個檔案。")
    print(report)

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
