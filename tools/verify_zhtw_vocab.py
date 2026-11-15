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

skip_code=True（CLI 預設）先保護程式碼、成對中文引號與 URL／連結目的地。
引號保護最多 200 字且不可跨空白段落或表格欄；錯配引號不保護。
裸 URL 允許中文，遇空白、全形標點或未配對右括號即停；含規則詞時 CLI 提示人工確認。
連結目的地限同一行，標題照常檢查；不是完整 Markdown 或語義解析器。
未加引號的產品名稱仍無專名保護；不判斷標題、語義、標點或最終成品佔位。
「支持」未加入自動替換。skip_code=False 保留既有全文替換模式。
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
    ("服務器", "伺服器", "技術術語：server"),
    ("軟件", "軟體", "技術術語：software"),
    ("硬件", "硬體", "技術術語：hardware"),
    ("短視頻", "短影音", "長詞優先：short video"),
    ("視頻", "影片", "技術術語：video"),
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
_BARE_URL_RE = re.compile(
    r"(?:https?://|ftp://|www\.)[^\s<>`，。；：、（）「」『』【】《》！？\uff00-\uffef]+"
)
_AUTOLINK_RE = re.compile(r"<(?:https?://|ftp://|www\.)[^<>\s]+>")
_QUOTE_LIMIT = 200
_REFERENCE_RE = re.compile(r"(?m)^ {0,3}\[(?!\^)[^\]\n]+\]:[ \t]*(<[^<>\n]+>|[^\s]+)")
# Match immediate neighbours, independent of the surrounding sentence.
_CONTEXT_EXCEPTIONS = {
    "視頻": (("電衛監", ""), ("", "率")),
    "服務器": (("", "材"),),
    "軟件": (("", "數"),),
    "硬件": (("堅", ""),),
}
_PROTECTED_START_RE = re.compile(r"[「『]|\]\(|<(?=(?:https?://|ftp://|www\.))|(?:https?://|ftp://|www\.)")


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


def _rule_matches(text: str, src: str):
    """Use the same narrow context exceptions in checking and rewriting."""
    for match in re.finditer(re.escape(src), text):
        before = text[match.start() - 1:match.start()] if match.start() else ""
        after = text[match.end():match.end() + 1]
        if not any((not left or (bool(before) and before in left)) and
                   (not right or (bool(after) and after in right))
                   for left, right in _CONTEXT_EXCEPTIONS.get(src, ())):
            yield match


def _line_parentheses(text: str) -> Dict[int, int]:
    """Pair parentheses once, resetting at each line; no repeated suffix scans."""
    pairs = {}
    stack = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in "\r\n":
            stack.clear()
        elif char == "\\" and i + 1 < len(text) and text[i + 1] not in "\r\n":
            i += 1
        elif char == "(":
            stack.append(i)
        elif char == ")" and stack:
            pairs[stack.pop()] = i
        i += 1
    return pairs


def _destination_end(text: str, start: int, close: int, pairs: Dict[int, int]) -> int:
    """Return the destination only, leaving whitespace and link titles as prose."""
    end = start
    if end < close and text[end] == "<":
        angle = text.find(">", end + 1, close)
        return angle + 1 if angle >= 0 else start
    while end < close and not text[end].isspace():
        if text[end] == "\\":
            end = min(end + 2, close)
        elif text[end] == "(":
            end = pairs[end] + 1
        else:
            end += 1
    return end


def _transform_non_code_segment(segment: str) -> str:
    out = segment
    seen = set()
    while out not in seen:
        seen.add(out)
        previous = out
        for src, dst, _ in ALL_RULES:
            if src != dst and src in out:
                matches = list(_rule_matches(out, src))
                for match in reversed(matches):
                    out = out[:match.start()] + dst + out[match.end():]
        if out == previous:
            return out
    raise ValueError("詞庫規則循環，無法收斂至固定點")


def _protected_parts(text: str, url_hints: Optional[List[Tuple[int, str]]] = None) -> List[Tuple[bool, str]]:
    """Share exact protected spans between checking and rewriting.

    Code is masked first so quote characters inside code cannot open a quote.
    Quotes are bounded by length, paragraphs and table cells. Same-line Markdown
    destinations support nested/escaped parentheses and reference definitions;
    titles remain prose. This deliberately is not a full Markdown parser.
    """
    spans = []
    offset = 0
    in_fence = None
    for line in text.splitlines(keepends=True):
        match = _FENCE_OPEN_RE.match(line)
        was_in_fence = in_fence is not None
        if match:
            marker = match.group(1)
            if in_fence is None and marker[0] not in line[match.end():]:
                in_fence = marker
            elif (in_fence is not None and marker[0] == in_fence[0]
                  and len(marker) >= len(in_fence)
                  and not line[match.end():].strip()):
                in_fence = None
        if was_in_fence or in_fence is not None:
            spans.append((offset, offset + len(line)))
        else:
            part_offset = offset
            for protected, part in _inline_parts(line):
                if protected:
                    spans.append((part_offset, part_offset + len(part)))
                part_offset += len(part)
        offset += len(line)

    masked = list(text)
    for start, end in spans:
        masked[start:end] = ["\n" if c == "\n" else " " for c in text[start:end]]
    prose = "".join(masked)
    pairs = _line_parentheses(prose)
    # Protect definitions before scanning quotes or URLs in their destinations.
    for reference in _REFERENCE_RE.finditer(prose):
        destination = reference.group(1)
        if not (destination.startswith("<") or any(c in destination for c in ("/", ".", "#", "://"))):
            continue
        start, end = reference.span(1)
        spans.append((start, end))
        masked[start:end] = [" "] * (end - start)
    prose = "".join(masked)
    cursor = 0
    while match := _PROTECTED_START_RE.search(prose, cursor):
        start = match.start()
        token = match.group()
        end = match.end()
        if token in ("「", "『"):
            stack = ["」" if token == "「" else "』"]
            while end < min(len(prose), start + _QUOTE_LIMIT) and stack:
                char = prose[end]
                if char == "\\" and end + 1 < len(prose) and prose[end + 1] in "\\|":
                    end += 2
                    continue
                if char == "|" or (char == "\n" and
                                   re.match(r"[ \t\r]*\n", prose[end + 1:end + _QUOTE_LIMIT])):
                    break
                if char in ("」", "』") and char != stack[-1]:
                    break
                if char in ("「", "『"):
                    stack.append("」" if char == "「" else "』")
                elif char == stack[-1]:
                    stack.pop()
                end += 1
            if stack:
                cursor = match.end()
                continue
        elif token == "<":
            autolink = _AUTOLINK_RE.match(prose, start)
            if autolink is None:
                cursor = match.end()
                continue
            end = autolink.end()
        elif token == "](":
            close = pairs.get(end - 1)
            if close is None:
                cursor = match.end()
                continue
            start = end
            while start < close and prose[start] in " \t":
                start += 1
            end = _destination_end(prose, start, close, pairs)
        else:
            url = _BARE_URL_RE.match(prose, start)
            if url is None:
                cursor = match.end()
                continue
            end = url.end()
            depth = 0
            for index in range(match.end(), end):
                if prose[index] == "(":
                    depth += 1
                elif prose[index] == ")":
                    if depth == 0:
                        end = index
                        break
                    depth -= 1
            if url_hints is not None and any(src != dst and src in prose[start:end]
                                            for src, dst, _ in ALL_RULES):
                url_hints.append((text.count("\n", 0, start) + 1, text[start:end]))
        spans.append((start, end))
        cursor = end

    merged = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    parts = []
    cursor = 0
    for start, end in merged:
        parts.extend([(False, text[cursor:start]), (True, text[start:end])])
        cursor = end
    parts.append((False, text[cursor:]))
    return parts


def apply_zhtw_vocab(text: str, skip_code: bool = False) -> str:
    """
    套用台灣繁體中文詞彙與 OpenCC 二次退化修補規則。
    - skip_code=False：直接對全文套用（等同保哥 convert.mjs 對純文件後處理）
    - skip_code=True：保護程式碼、成對中文引號、連結目的地及裸 URL。
    """
    if not skip_code:
        return _transform_non_code_segment(text)

    return "".join(part if protected else _transform_non_code_segment(part)
                   for protected, part in _protected_parts(text))


def scan_degraded_vocab(text: str, skip_code: bool = True) -> List[Dict[str, Any]]:
    """
    掃描文本中是否殘留未修補的 OpenCC 二次退化詞、語境誤轉詞或禁用大陸用語。
    skip_code=True 時與改寫共用程式碼、中文引號與 URL 保護範圍。
    """
    findings: List[Dict[str, Any]] = []
    if skip_code:
        text = "".join(
            "".join("\n" if c == "\n" else " " for c in part)
            if protected else part
            for protected, part in _protected_parts(text)
        )
    # Match longer terms first, masking their extent so 短視頻 never also
    # recommends the shorter 視頻 replacement inside the same occurrence.
    rules = sorted(ALL_RULES, key=lambda rule: len(rule[0]), reverse=True)
    for lineno, line in enumerate(text.split("\n"), 1):
        inspect_text = line
        line_hits: List[Tuple[int, Dict[str, Any]]] = []
        for src, dst, reason in rules:
            if src != dst and src in inspect_text:
                matches = list(_rule_matches(inspect_text, src))
                if not matches:
                    continue
                pos = matches[0].start()
                line_hits.append((
                    pos,
                    {
                        "line": lineno,
                        "term": src,
                        "replacement": dst,
                        "reason": reason,
                    },
                ))
                for match in reversed(matches):
                    inspect_text = (inspect_text[:match.start()] + " " * len(src)
                                    + inspect_text[match.end():])
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

    # Report once per file, including when --fix and --check share the input.
    for fpath in dict.fromkeys([*fix_files, *check_files]):
        hints: List[Tuple[int, str]] = []
        _protected_parts(fpath.read_text(encoding="utf-8"), hints)
        for line, url in hints:
            print(f"[REVIEW] {fpath}:{line}: 裸 URL 含規則詞，保留原文，請人工確認：{url}")

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
