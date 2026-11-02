#!/usr/bin/env python3
"""
tools/audit_surgical_diff.py
外科手術式修改（Surgical Changes）的 Git 變更範圍審查。唯讀，不改任何檔案、不改 git 狀態。
規範：docs/karpathy-rules-mechanical-hardening-spec.md（第 3 節）

做的事：用真實的 git 輸出（--name-status／--numstat／-U0），檢查一次變更有沒有超出宣告的範圍。

    比較範圍   預設：工作樹（含已暫存、未暫存、未追蹤檔）對 --base（預設 HEAD）
               給 --head：只比 --base 與 --head 兩個 commit（不看工作樹）
               兩種模式都先把 --base 換成「它與 head（或 HEAD）的 merge-base」再比較（等同 git diff base...head），
               所以 base 分支（例如 main）在分出後前進，別人的改動不會被算成越界。
    違規種類
      out-of-scope        變更（新增、修改、刪除、改名的舊路徑或新路徑）不在任何 --scope 內
      too-many-files      受審檔案數超過 --max-files
      too-many-lines      受審檔案新增＋刪除行數超過 --max-lines
      whitespace-only     檔案變更忽略空白與空白行後是 0 行（純重排、縮排、換行符、增刪空行）
      whitespace-noise    檔案有實質變更，但另外夾帶超過 --max-whitespace-lines 行（新增＋刪除合計）的空白雜訊
      comment-erasure     非刪除檔案中，被刪的註解行比新增的註解行多出超過 --max-comment-removed 行
    --exempt 路徑：不檢查範圍、不計入檔數與行數、也不做上列各項檢查（例如由腳本產生的 README、lockfile），
                   但仍列在報告的「豁免」清單，讓人看得到。

路徑樣式（--scope／--exempt，可重複）：
    docs/a.md        精確檔案
    docs/            目錄（以 / 結尾，含子目錄）
    docs/*.md        * 不跨目錄；** 可跨目錄；? 一個非 / 字元
    不接受含 .. 的樣式、絕對路徑。

已知限制（誠實揭露）：
    - 註解判斷是依行首符號的啟發式（#、//、/*、*、--、<!--），不解析語言語法；
      .md／.markdown／.txt／.rst 不做註解檢查；C 系列副檔名的 # 開頭視為前處理指令而非註解。
    - 它判斷「改了哪裡、改了多少」，不判斷「改得對不對」；範圍內的壞改動它看不出來。
    - 工作樹模式下，未暫存的改名會被 git 看成「刪除＋未追蹤新檔」，兩個路徑都會各自檢查範圍。
    - 子模組指標、符號連結各算一個檔案、只按路徑檢查範圍，不展開內容；子模組內部的改動要到子模組 repo 另外審。

用法：
    python tools/audit_surgical_diff.py --scope tools/foo.py --scope tests/test_foo.py
    python tools/audit_surgical_diff.py --repo . --base main --head HEAD --scope docs/ --exempt README.md --json
結束碼：0 通過；1 有違規；2 參數或 git 錯誤（不是 git repo、base 不存在等）。
只使用 Python 標準函式庫；需要系統有 git。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_BASE = "HEAD"
DEFAULT_MAX_FILES = 10
DEFAULT_MAX_LINES = 400
DEFAULT_MAX_WS_LINES = 10
DEFAULT_MAX_COMMENT_REMOVED = 3

NO_COMMENT_CHECK_EXT = {".md", ".markdown", ".txt", ".rst"}
C_FAMILY_EXT = {".c", ".h", ".cc", ".cpp", ".hpp", ".cs"}
COMMENT_PREFIXES = ("//", "/*", "*/", "--", "<!--")


class AuditError(Exception):
    """參數或 git 錯誤（對應結束碼 2）。"""


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


@dataclass
class Change:
    status: str  # A M D R C T
    path: str  # 新路徑（刪除時為被刪的路徑）
    old_path: str | None = None  # 改名／複製的舊路徑
    added: int = 0
    deleted: int = 0
    ws_noise: int = 0  # 只因空白而不同的行數（新增＋刪除合計，等於 added+deleted 扣掉 -w 後的）
    binary: bool = False
    removed_comments: int = 0
    added_comments: int = 0

    @property
    def lines(self) -> int:
        return self.added + self.deleted

    @property
    def paths(self) -> list[str]:
        return [self.path] + ([self.old_path] if self.old_path else [])


@dataclass
class Violation:
    kind: str
    path: str
    detail: str


@dataclass
class Report:
    base: str
    head: str | None
    changes: list[Change] = field(default_factory=list)
    exempt: list[str] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0

    @property
    def ok(self) -> bool:
        return not self.violations


# ---------------------------------------------------------------- 路徑樣式

def compile_pattern(pattern: str) -> re.Pattern[str]:
    p = pattern.replace("\\", "/")
    if not p or p.startswith("/") or re.match(r"^[A-Za-z]:", p):
        raise AuditError(f"路徑樣式必須是相對於 repo 根目錄的非空路徑：{pattern!r}")
    if any(seg == ".." for seg in p.split("/")):
        raise AuditError(f"路徑樣式不可含 ..：{pattern!r}")
    if p.startswith("./"):
        p = p[2:]
    is_dir = p.endswith("/")
    out: list[str] = []
    i = 0
    while i < len(p):
        c = p[i]
        if c == "*":
            if p[i : i + 2] == "**":
                out.append(".*")
                i += 2
                if p[i : i + 1] == "/":  # **/ 可匹配零層目錄
                    out[-1] = "(?:.*/)?"
                    i += 1
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(c))
        i += 1
    body = "".join(out)
    return re.compile(("^" + body + ".*$") if is_dir else ("^" + body + "$"))


def matches_any(path: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.match(path) for p in patterns)


# ---------------------------------------------------------------- git

def _git(repo: str, *args: str) -> bytes:
    cmd = ["git", "--literal-pathspecs", "-c", "core.quotepath=off", "-C", repo, *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, check=False)
    except FileNotFoundError as exc:
        raise AuditError("找不到 git 指令") from exc
    if proc.returncode != 0:
        msg = proc.stderr.decode("utf-8", errors="replace").strip()
        raise AuditError(f"git {' '.join(args[:2])} 失敗（exit {proc.returncode}）：{msg}")
    return proc.stdout


def _dec(b: bytes) -> str:
    return b.decode("utf-8", errors="replace")


def _revs(repo: str, base: str, head: str | None) -> list[str]:
    """傳給 git diff 的 rev 清單。base 換成它與 head（或 HEAD）的 merge-base：
    base 分支在分出之後前進時，別人的改動不會被算成這次的越界（兩點 diff 會誤判）。"""
    for rev in (base, head):
        if rev is not None and rev.startswith("-"):
            raise AuditError(f"commit 參照不可以 - 開頭：{rev!r}")
    if head is None and base == "HEAD":  # merge-base(HEAD, HEAD) 就是 HEAD，省一次 git 呼叫
        return ["HEAD"]
    mb = _dec(_git(repo, "merge-base", base, head or "HEAD")).strip()
    return [mb, head] if head else [mb]


def parse_raw_numstat(raw: bytes) -> tuple[list[Change], dict[str, tuple[int, int, bool]]]:
    """解析 `git diff --raw --numstat -z`：前段是 :mode mode sha sha 狀態\0路徑...，後段是 numstat。"""
    parts = raw.split(b"\0")
    changes: list[Change] = []
    i = 0
    while i < len(parts) and parts[i].startswith(b":"):
        code = _dec(parts[i]).split(" ")[-1][0]
        if code in "RC":
            changes.append(Change(status=code, old_path=_dec(parts[i + 1]), path=_dec(parts[i + 2])))
            i += 3
        else:
            changes.append(Change(status=code, path=_dec(parts[i + 1])))
            i += 2
    return changes, parse_numstat(b"\0".join(parts[i:]))


def parse_numstat(raw: bytes) -> dict[str, tuple[int, int, bool]]:
    """回傳 新路徑 -> (added, deleted, binary)。"""
    parts = raw.split(b"\0")
    result: dict[str, tuple[int, int, bool]] = {}
    i = 0
    while i < len(parts) and parts[i]:
        head = _dec(parts[i]).split("\t")
        a, d, rest = head[0], head[1], "\t".join(head[2:])
        if rest == "":  # 改名／複製：後面接 old\0new\0
            path = _dec(parts[i + 2])
            i += 3
        else:
            path = rest
            i += 1
        if a == "-" or d == "-":
            result[path] = (0, 0, True)
        else:
            result[path] = (int(a), int(d), False)
    return result


def _is_comment(line: str, ext: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith("#"):
        return ext not in C_FAMILY_EXT
    if s.startswith(COMMENT_PREFIXES):
        return True
    return s == "*" or s.startswith("* ")


def count_comment_lines(repo: str, revs: list[str], change: Change) -> tuple[int, int]:
    ext = Path(change.path).suffix.lower()
    if ext in NO_COMMENT_CHECK_EXT or change.binary or change.status in "AD":
        return 0, 0
    pathspecs = [change.path] + ([change.old_path] if change.old_path else [])
    raw = _git(repo, "diff", "-M", "-U0", "--no-color", "--no-ext-diff", "--no-textconv", *revs, "--", *pathspecs)
    removed = added = 0
    in_hunk = False  # 第一個 @@ 之前是檔頭（---／+++ 是路徑）；之後 "---" 開頭的行是內容（例如被刪的 "-- 註解"）
    for line in _dec(raw).split("\n"):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("-") and _is_comment(line[1:], ext):
            removed += 1
        elif line.startswith("+") and _is_comment(line[1:], ext):
            added += 1
    return removed, added


def _count_file_lines(repo: str, rel: str) -> tuple[int, bool]:
    data = (Path(repo) / rel).read_bytes()
    if b"\0" in data[:8000]:
        return 0, True
    n = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    return n, False


def collect_changes(repo: str, base: str, head: str | None) -> list[Change]:
    revs = _revs(repo, base, head)
    flags = ["-M", "--no-color", "--no-ext-diff", "--no-textconv"]
    changes, full = parse_raw_numstat(_git(repo, "diff", "--raw", "--numstat", "-z", *flags, *revs))
    nows = parse_numstat(_git(repo, "diff", "--numstat", "-z", "-w", "--ignore-blank-lines", *flags, *revs))
    for ch in changes:
        a, d, binary = full.get(ch.path, (0, 0, False))
        ch.added, ch.deleted, ch.binary = a, d, binary
        wa, wd, _ = nows.get(ch.path, (0, 0, False))  # -w 沒變更的檔不會出現在 numstat
        ch.ws_noise = max(0, (a + d) - (wa + wd))
        ch.removed_comments, ch.added_comments = count_comment_lines(repo, revs, ch)
    if head is None:  # 工作樹模式：加上未追蹤檔（遵守 .gitignore）
        raw = _git(repo, "ls-files", "--others", "--exclude-standard", "-z")
        for p in raw.split(b"\0"):
            if not p:
                continue
            rel = _dec(p)
            try:
                n, binary = _count_file_lines(repo, rel)
            except OSError:
                n, binary = 0, False
            changes.append(Change(status="A", path=rel, added=n, binary=binary))
    return changes


# ---------------------------------------------------------------- 判定

def audit(
    changes: list[Change],
    scope: list[re.Pattern[str]],
    exempt: list[re.Pattern[str]],
    *,
    base: str = DEFAULT_BASE,
    head: str | None = None,
    max_files: int = DEFAULT_MAX_FILES,
    max_lines: int = DEFAULT_MAX_LINES,
    max_ws_lines: int = DEFAULT_MAX_WS_LINES,
    max_comment_removed: int = DEFAULT_MAX_COMMENT_REMOVED,
) -> Report:
    rep = Report(base=base, head=head)
    audited: list[Change] = []
    for ch in changes:
        if all(matches_any(p, exempt) for p in ch.paths):
            rep.exempt.append(ch.path)
        else:
            audited.append(ch)
    rep.changes = audited
    rep.total_files = len(audited)
    rep.total_lines = sum(c.lines for c in audited)
    for ch in audited:
        for p in ch.paths:
            if not matches_any(p, scope) and not matches_any(p, exempt):
                kind = {"A": "新增", "D": "刪除", "R": "改名", "C": "複製"}.get(ch.status, "修改")
                rep.violations.append(Violation("out-of-scope", p, f"{kind}了不在宣告範圍內的路徑"))
        if ch.binary:
            continue
        if ch.status in "MRC" and ch.lines > 0 and ch.ws_noise == ch.lines:
            rep.violations.append(Violation("whitespace-only", ch.path, f"{ch.lines} 行變更全是空白／換行符差異"))
        elif ch.ws_noise > max_ws_lines:
            rep.violations.append(
                Violation("whitespace-noise", ch.path, f"實質變更之外夾帶 {ch.ws_noise} 行空白雜訊（上限 {max_ws_lines}）")
            )
        net = ch.removed_comments - ch.added_comments
        if net > max_comment_removed:
            rep.violations.append(
                Violation(
                    "comment-erasure",
                    ch.path,
                    f"刪 {ch.removed_comments} 行註解、增 {ch.added_comments} 行，淨少 {net} 行（上限 {max_comment_removed}）",
                )
            )
    if rep.total_files > max_files:
        rep.violations.append(Violation("too-many-files", "-", f"受審檔案 {rep.total_files} 個，上限 {max_files}"))
    if rep.total_lines > max_lines:
        rep.violations.append(Violation("too-many-lines", "-", f"新增＋刪除共 {rep.total_lines} 行，上限 {max_lines}"))
    return rep


def render(rep: Report) -> str:
    rng = f"{rep.base}..{rep.head}" if rep.head else f"{rep.base} -> 工作樹"
    out = [f"範圍審查（{rng}）：受審 {rep.total_files} 個檔案、{rep.total_lines} 行變更"]
    for c in rep.changes:
        old = f"{c.old_path} -> " if c.old_path else ""
        out.append(f"  {c.status}  {old}{c.path}  (+{c.added} -{c.deleted})")
    if rep.exempt:
        out.append("豁免（不計入）：" + ", ".join(rep.exempt))
    if rep.ok:
        out.append("[PASS] 變更都在宣告範圍內且未超過門檻")
    else:
        out.append(f"[FAIL] {len(rep.violations)} 項違規：")
        for v in rep.violations:
            out.append(f"  [{v.kind}] {v.path} - {v.detail}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    ap = argparse.ArgumentParser(description="Surgical Changes：審查 git 變更是否超出宣告範圍")
    ap.add_argument("--repo", default=".", help="git repo 路徑（預設目前目錄）")
    ap.add_argument("--base", default=DEFAULT_BASE, help="比較基準 commit／分支（預設 HEAD）")
    ap.add_argument("--head", default=None, help="比較終點 commit；省略則比較工作樹（含未追蹤檔）")
    ap.add_argument("--scope", action="append", required=True, help="允許變更的路徑樣式，可重複，至少一個")
    ap.add_argument("--exempt", action="append", default=[], help="豁免路徑樣式（不審查、不計數），可重複")
    ap.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    ap.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    ap.add_argument("--max-whitespace-lines", type=int, default=DEFAULT_MAX_WS_LINES)
    ap.add_argument("--max-comment-removed", type=int, default=DEFAULT_MAX_COMMENT_REMOVED)
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code not in (0, None) else 0
    try:
        scope = [compile_pattern(s) for s in args.scope]
        exempt = [compile_pattern(s) for s in args.exempt]
        changes = collect_changes(args.repo, args.base, args.head)
    except AuditError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    rep = audit(
        changes,
        scope,
        exempt,
        base=args.base,
        head=args.head,
        max_files=args.max_files,
        max_lines=args.max_lines,
        max_ws_lines=args.max_whitespace_lines,
        max_comment_removed=args.max_comment_removed,
    )
    if args.json:
        payload = asdict(rep)
        payload["ok"] = rep.ok
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(rep))
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
