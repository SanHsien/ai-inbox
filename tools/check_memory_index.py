#!/usr/bin/env python3
"""
tools/check_memory_index.py
跨平台檢查「記憶索引」(MEMORY.md，一行一個指標) 與實際記憶檔是否一致。唯讀，不改任何檔案。

索引行格式：`- [name.md](name.md) — 一行描述`
子索引：MEMORY.md 指向的頂層 `INDEX-*.md`（例如 INDEX-reference.md）也當索引讀，裡面列到的檔一樣算「有進索引」；
子索引可再指向子索引（防循環）。沒被指到的 INDEX-*.md 不跟隨。INDEX-*.md 本身不要求 frontmatter。
--max-entries 只算 MEMORY.md 本身的指標（開場載入的是它）。

檢查項目（ERROR 一定失敗；WARN 預設只提醒，加 --strict 才失敗）：
    ERROR  broken-link     索引指向不存在的檔（含大小寫不符，Windows 不分大小寫但 Linux／macOS 分）
    ERROR  outside-dir     索引指向記憶資料夾之外
    ERROR  unindexed       資料夾頂層的 .md 沒進主索引或子索引（預設排除 daily-log-*.md；可加 --ignore）
    ERROR  no-frontmatter  缺 frontmatter，或缺 name／description／type（type 可在頂層或 metadata: 底下）
    ERROR  unreadable      檔案不是合法 UTF-8
    WARN   duplicate       同一個檔在主索引／子索引出現多次
    WARN   multi-pointer   一行出現多個指標
    WARN   long-line       索引行（含子索引）超過 --max-line-chars 字元
    WARN   too-many        MEMORY.md 的指標超過 --max-entries 條
    WARN   name-mismatch   frontmatter 的 name 與檔名不同
    WARN   unknown-type    type 不是 user／feedback／project／reference／insight（可用 --types 改）
    WARN   dead-wikilink   [[name]] 指向不存在的記憶（程式碼區塊與行內程式碼內的不算）

用法：
    python tools/check_memory_index.py <記憶資料夾> [--ignore GLOB ...] [--no-default-ignore] [--skip-frontmatter GLOB ...] [--json] [--strict]
結束碼：0 通過；1 有 ERROR（或 --strict 且有 WARN）；2 參數或資料夾錯誤。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

INDEX_NAME = "MEMORY.md"
SUB_INDEX_GLOB = "INDEX-*.md"
DEFAULT_TYPES = ("user", "feedback", "project", "reference", "insight")
DEFAULT_IGNORE = ("daily-log-*.md",)
REQUIRED_FIELDS = ("name", "description", "type")

_ENTRY = re.compile(r"\[([^\]\n]*)\]\(([^)\n]+)\)")
_BULLET = re.compile(r"^\s*[-*]\s+")
_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_WIKILINK = re.compile(r"\[\[([^\[\]\n]+)\]\]")
_KEY = re.compile(r"^([A-Za-z_][\w-]*):[ \t]*(.*)$")
_INDENT_TYPE = re.compile(r"^[ \t]+type:[ \t]*(.*)$")


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


class Finding:
    def __init__(self, level: str, code: str, file: str, line: int, msg: str):
        self.level, self.code, self.file, self.line, self.msg = level, code, file, line, msg

    def as_dict(self) -> dict:
        return {"level": self.level, "code": self.code, "file": self.file, "line": self.line, "message": self.msg}

    def __str__(self) -> str:
        loc = f"{self.file}:{self.line}" if self.line else self.file
        return f"{self.level:5} {self.code:14} {loc}  {self.msg}"


def parse_frontmatter(text: str) -> dict | None:
    """回傳 {欄位: 值}（metadata 底下的 type 也算 type）；沒有 frontmatter 或沒收尾回 None。"""
    lines = text.lstrip("﻿").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            break
    else:
        return None
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        m = _KEY.match(line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip("\"'")
            continue
        m = _INDENT_TYPE.match(line)
        if m and "type" not in fields:
            fields["type"] = m.group(1).strip().strip("\"'")
    return fields


def strip_code(text: str) -> str:
    """去掉圍欄程式碼區塊與行內程式碼，避免把範例裡的 [[x]] 當成連結。"""
    out, in_fence = [], False
    for line in text.split("\n"):
        if _FENCE.match(line):
            in_fence = not in_fence
            out.append("")
        elif in_fence:
            out.append("")
        else:
            out.append(_INLINE_CODE.sub("", line))
    return "\n".join(out)


def wikilink_target(raw: str) -> str:
    name = raw.split("|", 1)[0].split("#", 1)[0].strip()
    return name[:-3] if name.lower().endswith(".md") else name


def _matches(name: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(name, g) for g in globs)


def _scan_index(
    root: Path, index_file: str, text: str, indexed: dict[str, str], findings: list[Finding], stats: dict, max_line_chars: int
) -> list[str]:
    """解析一份索引（主索引或子索引），把指標記進 indexed；回傳它指到的頂層子索引檔名。"""
    sub_targets: list[str] = []
    for lineno, line in enumerate(text.split("\n"), 1):
        if not _BULLET.match(line):
            continue
        entries = [e for e in _ENTRY.findall(line) if not re.match(r"^[a-z][a-z0-9+.-]+:", e[1].strip(), re.I)]
        entries = [e for e in entries if not e[1].strip().startswith("#")]
        if not entries:
            continue
        if len(entries) > 1:
            findings.append(Finding("WARN", "multi-pointer", index_file, lineno, f"一行有 {len(entries)} 個指標，應一行一個"))
        if len(line) > max_line_chars:
            findings.append(Finding("WARN", "long-line", index_file, lineno, f"索引行 {len(line)} 字元，超過 {max_line_chars}"))
        for _label, raw in entries:
            stats["index_entries" if index_file == INDEX_NAME else "sub_index_entries"] += 1
            target = raw.strip().split("#", 1)[0].strip().replace("\\", "/")
            if target.startswith("./"):
                target = target[2:]
            parts = target.split("/")
            if target.startswith("/") or re.match(r"^[A-Za-z]:", target) or ".." in parts:
                findings.append(Finding("ERROR", "outside-dir", index_file, lineno, f"指向記憶資料夾之外：{raw.strip()}"))
                continue
            if target in indexed:
                findings.append(Finding("WARN", "duplicate", index_file, lineno, f"重複指標 {target}（首見 {indexed[target]}）"))
                continue
            indexed[target] = f"{index_file}:{lineno}"
            parent = root.joinpath(*parts[:-1])
            names = {q.name for q in parent.iterdir() if q.is_file()} if parent.is_dir() else set()
            exists = parts[-1] in names
            case_hit = next((n for n in names if n.lower() == parts[-1].lower()), None) if not exists else None
            if exists and len(parts) == 1 and _matches(parts[0], [SUB_INDEX_GLOB]):
                sub_targets.append(parts[0])
            if not exists:
                hint = f"（大小寫不符，實際檔名 {case_hit}）" if case_hit else ""
                findings.append(Finding("ERROR", "broken-link", index_file, lineno, f"指向不存在的檔：{target}{hint}"))
    return sub_targets


def check(
    root: Path,
    ignore: list[str] | None = None,
    skip_frontmatter: list[str] | None = None,
    max_entries: int = 60,
    max_line_chars: int = 200,
    types: tuple[str, ...] = DEFAULT_TYPES,
) -> tuple[list[Finding], dict]:
    """ignore 為 None 時用 DEFAULT_IGNORE；傳 [] 代表不排除任何檔。"""
    ignore = list(DEFAULT_IGNORE) if ignore is None else ignore
    skip_frontmatter = skip_frontmatter or []
    findings: list[Finding] = []
    stats = {"index_entries": 0, "sub_index_entries": 0, "memory_files": 0}
    index_path = root / INDEX_NAME
    if not index_path.is_file():
        findings.append(Finding("ERROR", "no-index", INDEX_NAME, 0, "找不到索引檔"))
        return findings, stats

    top_names = {p.name for p in root.iterdir() if p.is_file()}
    top_md = sorted(n for n in top_names if n.lower().endswith(".md") and n != INDEX_NAME)
    memory_files = [n for n in top_md if not _matches(n, ignore)]
    stats["memory_files"] = len(memory_files)

    try:
        index_text = index_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        findings.append(Finding("ERROR", "unreadable", INDEX_NAME, 0, "索引不是合法 UTF-8"))
        return findings, stats

    indexed: dict[str, str] = {}
    queue: list[tuple[str, str]] = [(INDEX_NAME, index_text)]
    followed = {INDEX_NAME}
    while queue:
        index_file, text = queue.pop(0)
        sub_targets = _scan_index(root, index_file, text, indexed, findings, stats, max_line_chars)
        for target in sub_targets:
            if target in followed:
                continue
            followed.add(target)
            try:
                queue.append((target, (root / target).read_text(encoding="utf-8-sig")))
            except (UnicodeDecodeError, OSError):
                pass  # 下面逐檔讀取時會報 unreadable

    if stats["index_entries"] > max_entries:
        findings.append(Finding("WARN", "too-many", INDEX_NAME, 0, f"索引有 {stats['index_entries']} 條指標，超過 {max_entries}"))

    for name in memory_files:
        if name not in indexed:
            findings.append(Finding("ERROR", "unindexed", name, 0, "沒有出現在 MEMORY.md 或其子索引"))

    stems = {n[:-3] for n in top_md}
    stems.update(Path(k).with_suffix("").as_posix() for k in indexed if "/" in k)
    stems.add(INDEX_NAME[:-3])

    for name in [INDEX_NAME] + top_md:
        if _matches(name, ignore):
            continue
        try:
            text = (root / name).read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            findings.append(Finding("ERROR", "unreadable", name, 0, "不是合法 UTF-8"))
            continue
        except OSError as e:
            findings.append(Finding("ERROR", "unreadable", name, 0, f"讀取失敗：{type(e).__name__}"))
            continue
        if name != INDEX_NAME and not _matches(name, [SUB_INDEX_GLOB, *skip_frontmatter]):
            fm = parse_frontmatter(text)
            if fm is None:
                findings.append(Finding("ERROR", "no-frontmatter", name, 1, "缺 frontmatter（或沒有結尾的 ---）"))
            else:
                missing = [k for k in REQUIRED_FIELDS if not fm.get(k)]
                if missing:
                    findings.append(Finding("ERROR", "no-frontmatter", name, 1, f"frontmatter 缺欄位：{', '.join(missing)}"))
                if fm.get("name") and fm["name"] != name[:-3]:
                    findings.append(Finding("WARN", "name-mismatch", name, 1, f"name 是 {fm['name']}，檔名是 {name[:-3]}"))
                if fm.get("type") and fm["type"] not in types:
                    findings.append(Finding("WARN", "unknown-type", name, 1, f"type 是 {fm['type']}，不在 {', '.join(types)}"))
        for lineno, line in enumerate(strip_code(text).split("\n"), 1):
            for raw in _WIKILINK.findall(line):
                target = wikilink_target(raw)
                if target and target not in stems:
                    findings.append(Finding("WARN", "dead-wikilink", name, lineno, f"[[{target}]] 沒有對應的記憶檔"))
    return findings, stats


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="檢查記憶索引 MEMORY.md 與實際記憶檔是否一致（唯讀）。")
    ap.add_argument("dir", help="記憶資料夾（內含 MEMORY.md）")
    ap.add_argument("--ignore", action="append", default=[], metavar="GLOB", help="再多排除的頂層檔名（可重複；預設已排除 daily-log-*.md）")
    ap.add_argument("--no-default-ignore", action="store_true", help="不套用預設排除（daily-log-*.md）")
    ap.add_argument("--skip-frontmatter", action="append", default=[], metavar="GLOB", help="不檢查 frontmatter 的檔名（仍須進索引）")
    ap.add_argument("--max-entries", type=int, default=60, help="索引指標數上限（預設 60，超過只警告）")
    ap.add_argument("--max-line-chars", type=int, default=200, help="單行索引字元上限（預設 200，超過只警告）")
    ap.add_argument("--types", default=",".join(DEFAULT_TYPES), help="合法的 type 值，逗號分隔")
    ap.add_argument("--strict", action="store_true", help="WARN 也算失敗")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    return ap


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    args = build_parser().parse_args(argv)
    root = Path(args.dir)
    if not root.is_dir():
        print(f"錯誤：不是資料夾：{root}", file=sys.stderr)
        return 2
    findings, stats = check(
        root,
        ([] if args.no_default_ignore else list(DEFAULT_IGNORE)) + args.ignore,
        args.skip_frontmatter,
        args.max_entries,
        args.max_line_chars,
        tuple(t.strip() for t in args.types.split(",") if t.strip()),
    )
    errors = sum(f.level == "ERROR" for f in findings)
    warns = sum(f.level == "WARN" for f in findings)
    by_code: dict[str, int] = {}
    for f in findings:
        by_code[f.code] = by_code.get(f.code, 0) + 1
    if args.json:
        print(
            json.dumps(
                {"stats": stats, "errors": errors, "warnings": warns, "by_code": by_code, "findings": [f.as_dict() for f in findings]},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for f in findings:
            print(f)
        print(
            f"索引指標 {stats['index_entries']} 條（子索引另 {stats['sub_index_entries']} 條）；頂層記憶檔 {stats['memory_files']} 個；"
            f"ERROR {errors}、WARN {warns}" + (f"（{', '.join(f'{k}={v}' for k, v in sorted(by_code.items()))}）" if by_code else "")
        )
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
