#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taiwan Traditional Chinese Technical Vocabulary & OpenCC Second-Pass Guard (verify_zhtw_vocab.py)
-------------------------------------------------------------------------------------------------
借鑑 Will 保哥 doggy8088/answer-me-with-html@zh-tw 之 scripts/zh-tw/vocab.mjs 與 check.mjs：
1. 修補與攔截 OpenCC (cn -> tw2) 二次轉換退化詞（如：連線埠→連接埠、隻影響→只影響、選一個類別型→選一個類型、
   型別別→型別、字面量（Literal）（Literal）→字面量（Literal）、瞭什麼→了什麼）
2. 修補語境多義詞與大陸慣用詞（如：其他寫程式的 WAV→其他編碼的 WAV、渲染時會打印→渲染時會輸出、
   參考檔案→參考文件、摁下→按下）
3. 驗證轉換函數之嚴格冪等性：apply_zhtw_vocab(apply_zhtw_vocab(text)) == apply_zhtw_vocab(text)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# 第一階段：高確定性台灣技術複合詞與大陸動作詞修補（避免單字全面取代造成語境誤傷）
GLOBAL_VOCAB_RULES: Tuple[Tuple[str, str, str], ...] = (
    ("命令列界面", "命令列介面", "複合詞：命令行界面"),
    ("命令行介面", "命令列介面", "複合詞：命令行介面"),
    ("命令行", "命令列", "技術術語：command line"),
    ("環境變量", "環境變數", "技術術語：environment variable"),
    ("源代碼", "原始碼", "技術術語：source code"),
    ("數據庫", "資料庫", "技術術語：database"),
    ("正則表達式", "正規表示式", "技術術語：regular expression"),
    ("佔位符", "佔位符", "保持台灣慣用寫法"),
    ("字符集", "字元集", "技術術語：character set"),
    ("默認值", "預設值", "技術術語：default value"),
    ("可執行文件", "可執行檔", "技術術語：executable file"),
    ("中間件", "中介軟體", "技術術語：middleware"),
    ("重定向", "重新導向", "技術術語：redirect"),
    ("摁下", "按下", "台灣繁體中文慣用動詞（禁用大陸用語「摁下」）"),
)

# 第二階段：OpenCC (cn -> tw2) 二次轉換退化修補與語境多義詞還原（源自 doggy8088/answer-me-with-html@zh-tw vocab.mjs）
DEGRADED_AND_CONTEXT_RULES: Tuple[Tuple[str, str, str], ...] = (
    # OpenCC 二次退化（second-pass degradation）
    ("連線埠", "連接埠", "OpenCC 二次轉換將「連接埠」誤退化為「連線埠」"),
    ("隻影響", "只影響", "OpenCC 將副詞「只」誤轉為量詞「隻」"),
    ("選一個類別型", "選一個類型", "OpenCC 疊字退化（類別 + 類型）"),
    ("型別別", "型別", "OpenCC 二次轉換疊字退化"),
    ("字面量（Literal）（Literal）", "字面量（Literal）", "括號英文註記二次重複附加"),
    ("瞭什麼", "了什麼", "OpenCC 將助詞「了」誤轉為「瞭」"),
    # 語境多義詞（一詞多譯修補）
    ("其他寫程式的 WAV", "其他編碼的 WAV", "簡體「编码」於音訊語境應為「編碼」而非「寫程式」"),
    ("自己寫程式並下載", "自己編碼並下載", "簡體「编码」於音訊處理語境應為「編碼」"),
    ("渲染時會打印", "渲染時會輸出", "終端機 stdout 語境應為「輸出」而非紙本「打印/列印」"),
    ("並打印路徑", "並輸出路徑", "終端機 stdout 語境應為「輸出」"),
    ("參考檔案", "參考文件", "Documentation 語境被轉為「參考檔案」，應還原為「參考文件」"),
)

ALL_RULES: Tuple[Tuple[str, str, str], ...] = GLOBAL_VOCAB_RULES + DEGRADED_AND_CONTEXT_RULES

_BACKTICK_RUN_RE = re.compile(r"`+")
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _inline_parts(line: str) -> List[Tuple[bool, str]]:
    """Pair maximal backtick runs of equal length; unmatched runs are prose."""
    runs = list(_BACKTICK_RUN_RE.finditer(line))
    parts = []
    cursor = 0
    i = 0
    while i < len(runs):
        opener = runs[i]
        end = next((j for j in range(i + 1, len(runs))
                    if len(runs[j].group()) == len(opener.group())), None)
        if end is None:
            i += 1
            continue
        closer = runs[end]
        parts.append((False, line[cursor:opener.start()]))
        parts.append((True, line[opener.start():closer.end()]))
        cursor = closer.end()
        i = end + 1
    parts.append((False, line[cursor:]))
    return parts


def _transform_non_code_segment(segment: str) -> str:
    out = segment
    seen = set()
    while out not in seen:
        seen.add(out)
        previous = out
        for src, dst, _ in ALL_RULES:
            if src != dst and src in out:
                out = out.replace(src, dst)
        if out == previous:
            return out
    raise ValueError("詞庫規則循環，無法收斂至固定點")


def _transform_line_outside_inline_code(line: str) -> str:
    return "".join(part if code else _transform_non_code_segment(part)
                   for code, part in _inline_parts(line))


def apply_zhtw_vocab(text: str, skip_code: bool = False) -> str:
    """
    套用台灣繁體中文詞彙與 OpenCC 二次退化修補規則。
    - skip_code=False：直接對全文套用（等同保哥 convert.mjs 對純文件後處理）
    - skip_code=True：略過 Markdown 圍欄程式碼區塊與行內反引號 `...`（避免改壞程式碼或反例表格）
    """
    if not skip_code:
        return _transform_non_code_segment(text)

    lines = text.split("\n")
    out_lines: List[str] = []
    in_fence: Optional[str] = None

    for line in lines:
        stripped = line.lstrip(" ")
        if len(line) - len(stripped) <= 3:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                marker = m.group(1)
                if in_fence is None:
                    if marker[0] not in line[m.end():]:
                        in_fence = marker
                        out_lines.append(line)
                        continue
                elif marker[0] == in_fence[0] and len(marker) >= len(in_fence) and line[m.end():].strip() == "":
                    in_fence = None
                    out_lines.append(line)
                    continue

        if in_fence is not None:
            out_lines.append(line)
        else:
            out_lines.append(_transform_line_outside_inline_code(line))

    return "\n".join(out_lines)


def scan_degraded_vocab(text: str, skip_code: bool = True) -> List[Dict[str, Any]]:
    """
    掃描文本中是否殘留未修補的 OpenCC 二次退化詞、語境誤轉詞或禁用大陸用語。
    skip_code=True 時自動忽略圍欄程式碼與行內 `...` 引用（允許在筆記中以反引號列舉反例）。
    """
    findings: List[Dict[str, Any]] = []
    lines = text.split("\n")
    in_fence: Optional[str] = None

    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip(" ")
        if len(line) - len(stripped) <= 3:
            m = _FENCE_OPEN_RE.match(line)
            if m:
                marker = m.group(1)
                if in_fence is None:
                    if marker[0] not in line[m.end():]:
                        in_fence = marker
                        continue
                elif marker[0] == in_fence[0] and len(marker) >= len(in_fence) and line[m.end():].strip() == "":
                    in_fence = None
                    continue

        if skip_code and in_fence is not None:
            continue

        inspect_text = " ".join(part for code, part in _inline_parts(line) if not code) if skip_code else line
        line_hits: List[Tuple[int, Dict[str, Any]]] = []
        for src, dst, reason in ALL_RULES:
            if src != dst and src in inspect_text:
                pos = inspect_text.find(src)
                line_hits.append((
                    pos,
                    {
                        "line": lineno,
                        "term": src,
                        "replacement": dst,
                        "reason": reason,
                    },
                ))
        line_hits.sort(key=lambda item: item[0])
        findings.extend(h for _, h in line_hits)

    return findings


def verify_idempotence(sample_texts: Optional[Sequence[str]] = None) -> Tuple[bool, List[str]]:
    """
    驗證詞庫轉換之冪等性（Idempotence）：
    對所有內建規則與給定樣本，跑第二次轉換必須與跑第一次完全一致（零二次退化）。
    """
    samples = list(sample_texts or []) + ["型別別別別別", "字面量（Literal）（Literal）（Literal）", "命令行界面"]
    for src, dst, _ in ALL_RULES:
        samples.append(f"測試文本：{src} -> {dst}")

    failures: List[str] = []
    for idx, sample in enumerate(samples):
        once = apply_zhtw_vocab(sample, skip_code=False)
        twice = apply_zhtw_vocab(once, skip_code=False)
        if once != twice:
            failures.append(f"樣本 #{idx} 非冪等：once={once!r} != twice={twice!r}")

    return len(failures) == 0, failures


def _iter_target_files(paths: Sequence[str]) -> List[Path]:
    files: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        else:
            raise ValueError(f"路徑不存在或不是一般檔案／目錄：{p}")
    if not files:
        raise ValueError("沒有可檢查的輸入檔案")
    for p in files:
        if not p.read_text(encoding="utf-8").strip():
            raise ValueError(f"輸入檔案為空：{p}")
    return list(dict.fromkeys(files))


def _main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="台灣繁體中文詞庫檢查／固定點修補；結束碼 0=通過，1=詞彙或冪等失敗，2=輸入／讀寫錯誤"
    )
    parser.add_argument("--check", nargs="*", default=None, help="掃描指定檔案或目錄是否殘留退化詞（略過程式碼區塊）")
    parser.add_argument("--fix", nargs="*", default=None, help="就地修補指定檔案或目錄中的退化詞（略過程式碼區塊）")
    parser.add_argument("--verify-idempotent", action="store_true", help="驗證所有詞彙轉換規則具備嚴格冪等性")
    args = parser.parse_args(argv)

    if args.check is None and args.fix is None and not args.verify_idempotent:
        print("[INFO] 請提供 --check <paths>、--fix <paths> 或 --verify-idempotent。")
        return 2

    # Validate all inputs before any --fix mutation.
    try:
        check_files = _iter_target_files(args.check) if args.check is not None else []
        fix_files = _iter_target_files(args.fix) if args.fix is not None else []
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    exit_code = 0

    if args.verify_idempotent:
        ok, failures = verify_idempotence()
        if ok:
            print(f"[PASS] 冪等性驗證通過（共 {len(ALL_RULES)} 條詞彙與二次退化防禦規則）。")
        else:
            for f in failures:
                print(f"[FAIL] {f}")
            exit_code = 1

    if args.fix is not None:
        for fpath in fix_files:
            orig = fpath.read_text(encoding="utf-8")
            fixed = apply_zhtw_vocab(orig, skip_code=True)
            if fixed != orig:
                fpath.write_text(fixed, encoding="utf-8")
                print(f"[FIXED] {fpath}")

    if args.check is not None:
        total_findings = 0
        for fpath in check_files:
            content = fpath.read_text(encoding="utf-8")
            hits = scan_degraded_vocab(content, skip_code=True)
            for h in hits:
                total_findings += 1
                print(
                    f"[ALERT] {fpath}:{h['line']}: 發現 '{h['term']}' -> 應改為 '{h['replacement']}'（{h['reason']}）"
                )
        if total_findings == 0:
            print("[PASS] 繁體中文詞彙與 OpenCC 退化檢查全數通過。")
        else:
            exit_code = 1

    return exit_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        return _main(argv)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
