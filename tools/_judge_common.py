"""外部裁判（External Judge）驗證器共用工具（純 stdlib）。

集中以下原本在各 verify_*.py 重複複製的邏輯：
- ensure_utf8_output：Windows cp950 終端印 emoji 不再 UnicodeEncodeError。
- find_repo_root：由 marker 目錄往上推導 repo 根。
- strip_html_comments / strip_fenced_code：讓「關鍵字只藏在註解裡」不算數。
- count_headings / structural_floor：整份文件塞成一坨、包進註解或程式碼區塊會被擋下。
- doc_guard：套在 verify_*(text_or_path) 上的裝飾器（去註解 + 結構下限）。
- report_results：統一 [PASS]/[FAIL] 輸出格式。
"""

from __future__ import annotations

import functools
import re
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Union

HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")
FENCE_RE = re.compile(r"(^|\n)[ \t]*(```|~~~)[^\n]*\n[\s\S]*?\n[ \t]*\2[ \t]*(?=\n|$)")
HEADING_RE = re.compile(r"^#{1,6}[ \t]+\S", re.MULTILINE)

MIN_HEADINGS = 3


def ensure_utf8_output() -> None:
    """安全地把 stdout/stderr 改成 UTF-8（Windows cp950 終端友善）。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def find_repo_root(
    start: Optional[Path] = None,
    markers: Iterable[str] = ("notes", "docs"),
    anchor: Optional[Path] = None,
) -> Path:
    """回傳 repo 根目錄：start 優先，否則自 anchor（呼叫者 __file__）往上找含所有 markers 的目錄。"""
    if start is not None:
        return Path(start).resolve()
    cur = Path(anchor if anchor is not None else __file__).resolve()
    for parent in [cur, *cur.parents]:
        if all((parent / m).is_dir() for m in markers):
            return parent
    return Path.cwd()


def strip_html_comments(text: str) -> str:
    return HTML_COMMENT_RE.sub("", text)


def strip_fenced_code(text: str) -> str:
    return FENCE_RE.sub("\n", text)


def count_headings(text: str) -> int:
    """計算「真實」Markdown 標題數：忽略 HTML 註解與程式碼區塊內的 # 行。"""
    visible = strip_fenced_code(strip_html_comments(text))
    return len(HEADING_RE.findall(visible))


def structural_floor(text: str, min_headings: int = MIN_HEADINGS) -> List[str]:
    n = count_headings(text)
    if n < min_headings:
        return [f"文件結構不足：可見 Markdown 標題僅 {n} 個（至少需 {min_headings} 個；註解與程式碼區塊內的標題不計）"]
    return []


def read_text_safe(source: Union[str, Path]) -> str:
    """Path → 讀檔；單行短字串且為檔案 → 讀檔；其餘視為內文（避免 ENAMETOOLONG）。"""
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8")
    if isinstance(source, str):
        if "\n" not in source and len(source) < 240:
            try:
                p = Path(source)
                if p.is_file():
                    return p.read_text(encoding="utf-8")
            except (OSError, ValueError):
                pass
        return source
    raise TypeError(f"不支援的型別：{type(source)}")


def doc_guard(fn: Callable[..., List[str]]) -> Callable[..., List[str]]:
    """裝飾 verify_xxx(text_or_path, ...)：先去除 HTML 註解，並檢查結構下限，再交給原函式。

    原函式只會看到「可見內容」，因此藏在 <!-- --> 內的關鍵字不會讓檢查通過。
    """

    @functools.wraps(fn)
    def wrapper(source, *args, **kwargs):
        text = read_text_safe(source)
        if not text.strip():
            return fn(text, *args, **kwargs)
        visible = strip_html_comments(text)
        errors = structural_floor(visible)
        return errors + fn(visible, *args, **kwargs)

    return wrapper


def report_results(
    results: Dict[str, List[str]],
    success_msg: str,
    fail_label: str = "規格缺陷",
    ok_label: str = "結構與規格完全相符",
    fail_msg: str = "外部裁判驗證未通過，請依上述錯誤修正文件。",
) -> int:
    """印出統一格式報告並回傳 exit code。"""
    for rel_path, errs in results.items():
        if errs:
            print(f"\n[FAIL] ❌ {rel_path} 發現 {len(errs)} 項{fail_label}：")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[PASS] ✅ {rel_path} {ok_label}")
    if all(not errs for errs in results.values()):
        print(f"\n[SUCCESS] 🎉 {success_msg}")
        return 0
    print(f"\n[ERROR] {fail_msg}")
    return 1
