#!/usr/bin/env python3
"""Agent Skills 上下文預算稽核工具 (audit_skills_context_budget.py)

規範：docs/agent-skills-curation-and-context-budget-spec.md

掃描一個 skills 目錄（每個子目錄一個 SKILL.md，開頭有 YAML frontmatter），回報：
1. 常駐成本：frontmatter 的 name + description（官方文件說這兩個欄位會在啟動時放進 system prompt）。
   輸出字元數與「估算」token 數。估算法見 estimate_tokens()：這是啟發式，不是 tokenizer 的實測值。
2. 本文成本：SKILL.md 本文（frontmatter 之後）的位元組數，觸發後才載入；超過 --max-body-bytes（預設 8192）警告。
3. 格式錯誤或缺欄位：沒有 frontmatter、沒結尾 ---、缺 name／description、name 格式不合官方規則、
   description 超過 1024 字元、含 XML 標籤。

退出碼：有 ERROR → 1；加 --strict 時有 WARN 也回 1；其餘 0。只用 Python 標準庫。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# 官方文件（2026-10-26 查證）：name ≤ 64 字元、僅小寫字母／數字／連字號、不可含 XML 標籤、
# 不可含保留字 anthropic／claude；description 非空、≤ 1024 字元、不可含 XML 標籤。
# https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED_WORDS = ("anthropic", "claude")
MAX_DESCRIPTION_CHARS = 1024
XML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")

# 以下是本 repo 的政策值，不是官方數字（見規範文件第 4 節）。
DEFAULT_MAX_BODY_BYTES = 8192
DEFAULT_MAX_RESIDENT_TOKENS = 150  # 單一技能常駐上限；官方文件對 Level 1 的說法是「約 100 tokens」
DEFAULT_TOTAL_RESIDENT_TOKENS = 4000  # 整個技能庫常駐總量
DEFAULT_CHARS_PER_TOKEN = 4.0  # ASCII：約 4 字元 1 token（常見經驗值）
DEFAULT_CJK_TOKENS_PER_CHAR = 1.0  # 非 ASCII（中日韓等）：保守估每字 1 token

# 觸發提示：只是啟發式，只產生 WARN，不影響 ERROR。
TRIGGER_HINTS = ("use when", "use for", "when the user", "when working", "triggers:", "trigger when",
                 "當", "使用於", "使用時機", "觸發", "適用於", "用於")


@dataclass
class SkillReport:
    path: str
    name: str = ""
    description: str = ""
    name_chars: int = 0
    description_chars: int = 0
    resident_chars: int = 0
    resident_tokens_est: int = 0
    body_bytes: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def estimate_tokens(text: str, chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
                    cjk_tokens_per_char: float = DEFAULT_CJK_TOKENS_PER_CHAR) -> int:
    """估算 token 數（啟發式）：ASCII 字元 / chars_per_token + 非 ASCII 字元 * cjk_tokens_per_char，無條件進位。

    這不是 tokenizer 實測。要精準值請用模型供應商的 token counting；本工具只用來排序與抓異常肥大。
    """
    if not text:
        return 0
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    other_chars = len(text) - ascii_chars
    return math.ceil(ascii_chars / chars_per_token + other_chars * cjk_tokens_per_char)


def split_frontmatter(raw: str) -> tuple[str | None, str, str | None]:
    """回傳 (frontmatter 文字, 本文, 錯誤訊息)。frontmatter 必須在檔案第一行 '---' 開頭。"""
    text = raw.lstrip("﻿")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text, "沒有 YAML frontmatter（檔案第一行必須是 ---）"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1:]), None
    return None, text, "frontmatter 沒有結尾的 ---"


def parse_simple_yaml(block: str) -> tuple[dict[str, str], list[str]]:
    """極簡 YAML 解析：頂層 key: value、引號字串、| 與 > 區塊、縮排續行。其餘結構忽略。"""
    data: dict[str, str] = {}
    problems: list[str] = []
    lines = block.splitlines()
    i = 0
    key_re = re.compile(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$")
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in " \t":
            i += 1  # 不屬於頂層 key 的縮排內容（例如清單項目），略過
            continue
        m = key_re.match(line)
        if not m:
            problems.append(f"無法解析的 frontmatter 行：{line[:60]!r}")
            i += 1
            continue
        key, value = m.group(1), m.group(2).strip()
        i += 1
        if value in ("|", ">", "|-", ">-", "|+", ">+"):
            folded = value.startswith(">")
            parts: list[str] = []
            while i < len(lines) and (not lines[i].strip() or lines[i][0] in " \t"):
                parts.append(lines[i].strip())
                i += 1
            data[key] = (" " if folded else "\n").join(p for p in parts if p or not folded).strip()
            continue
        if value[:1] in ("'", '"'):
            q = value[0]
            if len(value) >= 2 and value.endswith(q) and len(value) > 1:
                value = value[1:-1]
            else:
                problems.append(f"{key} 的引號沒有閉合")
                value = value[1:]
        else:
            # 純量允許下一行縮排續行（YAML plain multi-line scalar）
            while i < len(lines) and lines[i][:1] in (" ", "\t") and lines[i].strip():
                value += " " + lines[i].strip()
                i += 1
        data[key] = value
    return data, problems


def audit_skill_file(skill_md: Path, *, max_body_bytes: int, max_resident_tokens: int,
                     chars_per_token: float, cjk_tokens_per_char: float) -> SkillReport:
    rep = SkillReport(path=str(skill_md))
    try:
        raw_bytes = skill_md.read_bytes()
        raw = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        rep.errors.append("檔案不是合法 UTF-8")
        return rep
    except OSError as exc:
        rep.errors.append(f"無法讀取：{exc}")
        return rep

    fm, body, err = split_frontmatter(raw)
    rep.body_bytes = len(body.encode("utf-8"))
    if err:
        rep.errors.append(err)
        return rep
    assert fm is not None
    data, problems = parse_simple_yaml(fm)
    rep.errors.extend(problems)

    name = data.get("name", "").strip()
    desc = data.get("description", "").strip()
    rep.name, rep.description = name, desc
    rep.name_chars, rep.description_chars = len(name), len(desc)

    if "name" not in data or not name:
        rep.errors.append("缺少 name（或為空）")
    else:
        if not NAME_RE.match(name):
            rep.errors.append("name 只能是 1～64 個小寫字母、數字、連字號")
        if any(w in name for w in RESERVED_WORDS):
            rep.errors.append("name 含保留字 anthropic／claude")
        if XML_TAG_RE.search(name):
            rep.errors.append("name 含 XML 標籤")
        if skill_md.parent.name != name:
            rep.warnings.append(f"name 與資料夾名不同（資料夾：{skill_md.parent.name}）")

    if "description" not in data or not desc:
        rep.errors.append("缺少 description（或為空）")
    else:
        if len(desc) > MAX_DESCRIPTION_CHARS:
            rep.errors.append(f"description {len(desc)} 字元，超過官方上限 {MAX_DESCRIPTION_CHARS}")
        if XML_TAG_RE.search(desc):
            rep.errors.append("description 含 XML 標籤")
        low = desc.lower()
        if not any(h in low for h in TRIGGER_HINTS):
            rep.warnings.append("description 看不出觸發時機（啟發式：沒有 Use when／當…時 等說法）")

    resident_text = f"{name} {desc}".strip()
    rep.resident_chars = len(name) + len(desc)
    rep.resident_tokens_est = estimate_tokens(resident_text, chars_per_token, cjk_tokens_per_char)

    if rep.resident_tokens_est > max_resident_tokens:
        rep.warnings.append(f"常駐成本估 {rep.resident_tokens_est} tokens，超過單一技能門檻 {max_resident_tokens}")
    if rep.body_bytes > max_body_bytes:
        rep.warnings.append(f"本文 {rep.body_bytes} bytes，超過預算 {max_body_bytes}")
    return rep


def find_skill_files(root: Path, recursive: bool) -> tuple[list[Path], list[Path]]:
    """回傳 (SKILL.md 清單, 沒有 SKILL.md 的子資料夾)。預設只看第一層子目錄。"""
    if recursive:
        found = sorted(p for p in root.rglob("SKILL.md") if p.is_file())
        return found, []
    found, missing = [], []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        skill = child / "SKILL.md"
        (found if skill.is_file() else missing).append(skill if skill.is_file() else child)
    return found, missing


def audit_directory(root: Path, *, max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
                    max_resident_tokens: int = DEFAULT_MAX_RESIDENT_TOKENS,
                    total_resident_tokens: int = DEFAULT_TOTAL_RESIDENT_TOKENS,
                    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
                    cjk_tokens_per_char: float = DEFAULT_CJK_TOKENS_PER_CHAR,
                    recursive: bool = False) -> dict:
    files, missing = find_skill_files(root, recursive)
    reports = [audit_skill_file(f, max_body_bytes=max_body_bytes, max_resident_tokens=max_resident_tokens,
                                chars_per_token=chars_per_token, cjk_tokens_per_char=cjk_tokens_per_char)
               for f in files]
    for d in missing:
        r = SkillReport(path=str(d))
        r.errors.append("子資料夾沒有 SKILL.md")
        reports.append(r)
    total_tokens = sum(r.resident_tokens_est for r in reports)
    summary = {
        "root": str(root),
        "skills": len(files),
        "folders_without_skill_md": len(missing),
        "resident_chars_total": sum(r.resident_chars for r in reports),
        "resident_tokens_est_total": total_tokens,
        "resident_tokens_est_mean": round(total_tokens / len(files), 1) if files else 0,
        "total_resident_budget": total_resident_tokens,
        "over_total_budget": total_tokens > total_resident_tokens,
        "body_bytes_total": sum(r.body_bytes for r in reports),
        "errors": sum(len(r.errors) for r in reports),
        "warnings": sum(len(r.warnings) for r in reports),
        "skills_with_errors": sum(1 for r in reports if r.errors),
        "skills_over_body_budget": sum(1 for r in reports if r.body_bytes > max_body_bytes),
        "skills_over_resident_threshold": sum(1 for r in reports if r.resident_tokens_est > max_resident_tokens),
        "estimator": f"ASCII/{chars_per_token:g} + 非ASCII*{cjk_tokens_per_char:g}（啟發式，非 tokenizer 實測）",
    }
    return {"summary": summary, "reports": reports}


def render_text(result: dict, top: int) -> str:
    s, reports = result["summary"], result["reports"]
    out = [f"Skills 上下文預算稽核：{s['root']}", ""]
    out.append(f"技能數 {s['skills']}｜缺 SKILL.md 的資料夾 {s['folders_without_skill_md']}｜"
               f"ERROR {s['errors']}｜WARN {s['warnings']}")
    out.append(f"常駐成本（name+description）：{s['resident_chars_total']} 字元，估 {s['resident_tokens_est_total']} tokens"
               f"（平均 {s['resident_tokens_est_mean']}/技能；總預算 {s['total_resident_budget']}"
               f"{'，已超標' if s['over_total_budget'] else ''}）")
    out.append(f"本文 bytes 合計 {s['body_bytes_total']}｜超過本文預算 {s['skills_over_body_budget']} 個｜"
               f"超過單一常駐門檻 {s['skills_over_resident_threshold']} 個")
    out.append(f"token 估算法：{s['estimator']}")
    out.append("")
    ranked = sorted(reports, key=lambda r: r.resident_tokens_est, reverse=True)[:top]
    out.append(f"常駐成本最高的 {len(ranked)} 個：")
    for r in ranked:
        out.append(f"  {r.resident_tokens_est:>5} tok  {r.resident_chars:>5} chars  body {r.body_bytes:>6} B  {Path(r.path).parent.name}")
    flagged = [r for r in reports if r.errors or r.warnings]
    if flagged:
        out.append("")
        out.append("問題清單：")
        for r in flagged:
            label = Path(r.path).parent.name if r.path.endswith("SKILL.md") else Path(r.path).name
            for e in r.errors:
                out.append(f"  [ERROR] {label}: {e}")
            for w in r.warnings:
                out.append(f"  [WARN ] {label}: {w}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    # 要在解析參數之前設定：--help 由 argparse 直接印出，晚設就會用系統編碼（Windows cp950）輸出成亂碼
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

    p = argparse.ArgumentParser(
        description="稽核 skills 目錄的常駐上下文成本（name+description）、本文大小與 frontmatter 格式。唯讀。")
    p.add_argument("skills_dir", help="skills 目錄（每個子目錄一個 SKILL.md）")
    p.add_argument("--max-body-bytes", type=int, default=DEFAULT_MAX_BODY_BYTES, help="本文位元組預算（預設 8192）")
    p.add_argument("--max-resident-tokens", type=int, default=DEFAULT_MAX_RESIDENT_TOKENS,
                   help="單一技能常駐 token 估算門檻（預設 150）")
    p.add_argument("--total-resident-tokens", type=int, default=DEFAULT_TOTAL_RESIDENT_TOKENS,
                   help="整個技能庫常駐 token 估算總預算（預設 4000）")
    p.add_argument("--chars-per-token", type=float, default=DEFAULT_CHARS_PER_TOKEN, help="ASCII 每 token 字元數（預設 4）")
    p.add_argument("--cjk-tokens-per-char", type=float, default=DEFAULT_CJK_TOKENS_PER_CHAR,
                   help="非 ASCII 字元每字 token 數（預設 1）")
    p.add_argument("--recursive", action="store_true", help="遞迴尋找所有 SKILL.md（預設只看第一層子目錄）")
    p.add_argument("--top", type=int, default=10, help="列出常駐成本最高的前 N 個（預設 10）")
    p.add_argument("--json", action="store_true", help="輸出 JSON")
    p.add_argument("--strict", action="store_true", help="WARN 也視為失敗（退出碼 1）")
    args = p.parse_args(argv)

    root = Path(args.skills_dir)
    if not root.is_dir():
        print(f"[ERROR] 不是目錄：{root}", file=sys.stderr)
        return 2
    result = audit_directory(
        root, max_body_bytes=args.max_body_bytes, max_resident_tokens=args.max_resident_tokens,
        total_resident_tokens=args.total_resident_tokens, chars_per_token=args.chars_per_token,
        cjk_tokens_per_char=args.cjk_tokens_per_char, recursive=args.recursive)
    if args.json:
        print(json.dumps({"summary": result["summary"], "reports": [asdict(r) for r in result["reports"]]},
                         ensure_ascii=False, indent=2))
    else:
        print(render_text(result, args.top))
    s = result["summary"]
    failed = s["errors"] > 0 or (args.strict and (s["warnings"] > 0 or s["over_total_budget"]))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
