#!/usr/bin/env python3
"""
tools/review_ledger.py
新筆記獨立審查紀錄（設計見 docs/review-pipeline-plan.md，審查標準見 docs/source-review-sop.md）。

- 每篇筆記的審查紀錄在 reviews/<slug>.json（只追加），報告在 reviews/reports/<slug>/。
- 內容雜湊只算「分析內容」：去掉任務狀態欄位，task_cli 認領／結案不會讓審查失效；其他改動都會。
- reviews/legacy-baseline.json：審查制度上線時既有筆記的內容雜湊。內容沒變的舊筆記免審，
  一改內容就要照新規則送審。基準檔雜湊釘在 LEGACY_BASELINE_SHA256，不能悄悄加入新筆記。

給 verify_inbox.py、build_index.py、task_cli.py、review_pipeline.py 共用。直接執行時列出每篇的審查狀態：
    python tools/review_ledger.py            # 列出待審與已審
    python tools/review_ledger.py --hash <筆記路徑>
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

REVIEWS_DIRNAME = "reviews"
REPORTS_DIRNAME = "reports"
LEGACY_BASELINE_NAME = "legacy-baseline.json"
# 基準檔（reviews/legacy-baseline.json）位元組的 SHA-256。改這個值等於宣告「這些筆記免審」，要在 REVIEW.md 說明理由。
LEGACY_BASELINE_SHA256 = "6a3be2dc169ee5323de9a1dbd1770bedfd2fc4df62988fa00a152a03333a022a"

GRACE_DAYS = 7  # 新筆記（或改過內容的筆記）最多可以待審幾天
SCOPES = ("source", "facts", "evidence", "task_impact")
ROLES = ("review", "audit")
VERDICTS = ("pass", "changes_requested")
SOURCE_REVIEW_VALUES = ("full", "partial", "unavailable")
RUNTIMES = ("claude", "codex", "antigravity", "hermes", "human", "legacy")
# 制度上線前就有的筆記不知道作者 session，補審或修改時 written_by 用這個佔位；只准基準裡的筆記使用
LEGACY_AUTHOR = "legacy/unknown@pre-review"
SAMPLE_MODULO = 5  # 現行雜湊前 8 碼 mod 5 == 0 的筆記，一定要強模型覆核（抽查約 1/5）
CORRECTIONS_TRIGGER = 2  # 一次審查提出幾處以上更正，就要強模型覆核

# 強模型：可以當 audit、且當審查者時不會自動觸發覆核。其他模型（Sonnet、Haiku、Gemini Flash…）當審查者都要覆核。
STRONG_MODEL = re.compile(r"^(?:opus(?:-[\w.]+)?|gpt-6(?:\.\d+)?-(?:sol|astra)|maintainer)$", re.IGNORECASE)

IDENTITY = re.compile(r"^(?P<runtime>[a-z][a-z0-9-]*)/(?P<model>[A-Za-z0-9._-]+)@(?P<session>[A-Za-z0-9._:-]{4,})$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATE_FIELDS = ("狀態", "完成日期", "實作紀錄 / 證據")
TASK_BOX = re.compile(r"^- \[[xX]\] (?=\*\*`T-)")


@dataclass
class Identity:
    runtime: str
    model: str
    session: str

    @property
    def strong(self) -> bool:
        return bool(STRONG_MODEL.match(self.model)) or self.runtime == "human"

    def __str__(self) -> str:
        return f"{self.runtime}/{self.model}@{self.session}"


def parse_identity(text: str) -> Identity | None:
    m = IDENTITY.match(text.strip())
    if not m or m["runtime"] not in RUNTIMES:
        return None
    return Identity(m["runtime"], m["model"], m["session"])


def parse_identities(text: str) -> tuple[list[Identity], list[str]]:
    """`written_by` 以 `;` 分隔多個身分；回傳 (合法身分, 不合法的片段)。"""
    good, bad = [], []
    for part in (p.strip() for p in str(text or "").split(";")):
        if not part:
            continue
        ident = parse_identity(part)
        (good if ident else bad).append(ident or part)
    return good, bad


def analysis_text(text: str) -> str:
    """筆記去掉任務狀態後的「分析內容」：frontmatter status、正文「當前狀態」行、任務勾選框，
    以及任務底下的 狀態／完成日期／實作紀錄 / 證據 欄位（含其更深縮排的續行）。"""
    lines = text.replace("\r\n", "\n").split("\n")
    fm_end = -1
    if lines and lines[0].strip() == "---":
        fm_end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), -1)
    out: list[str] = []
    fence: str | None = None
    skipping = False
    for i, line in enumerate(lines):
        if 0 < i < fm_end:
            if re.match(r"^status\s*:", line):
                continue
            out.append(line.rstrip())
            continue
        if i <= fm_end:
            out.append(line.rstrip())
            continue
        fence, in_fence = bi.fence_step(fence, line)
        if not in_fence:
            if skipping and line.startswith("    ") and line.strip():
                continue
            skipping = False
            f = bi.TASK_FIELD.match(line)
            if f and f["key"].strip() in STATE_FIELDS:
                skipping = True
                continue
            if line.startswith("- **當前狀態**"):
                continue
            line = TASK_BOX.sub("- [ ] ", line)
        out.append(line.rstrip())
    return "\n".join(out).strip() + "\n"


def content_hash(text: str) -> str:
    return hashlib.sha256(analysis_text(text).encode("utf-8")).hexdigest()


def reviews_dir(root: Path | None = None) -> Path:
    return (root or bi.REPO_ROOT) / REVIEWS_DIRNAME


def load_legacy(root: Path | None = None) -> tuple[dict[str, str], list[str]]:
    path = reviews_dir(root) / LEGACY_BASELINE_NAME
    if not path.exists():
        return {}, []  # 沒有基準＝所有筆記都要審（比較嚴，不是放寬）
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != LEGACY_BASELINE_SHA256:
        return {}, [f"reviews/{LEGACY_BASELINE_NAME}: 內容與 tools/review_ledger.py 的 LEGACY_BASELINE_SHA256 不符"
                    "（基準凍結，不可增改；免審名單變更要改常數並在 REVIEW.md 說明）"]
    try:
        data = json.loads(raw.decode("utf-8"))
    except ValueError as e:
        return {}, [f"reviews/{LEGACY_BASELINE_NAME}: 不是合法 JSON：{e}"]
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.get("notes", {}).items()):
        return {}, [f"reviews/{LEGACY_BASELINE_NAME}: 格式需為 {{\"notes\": {{slug: sha256}}}}"]
    return dict(data["notes"]), []


def load_ledger(slug: str, root: Path | None = None) -> tuple[list[dict], list[str]]:
    path = reviews_dir(root) / f"{slug}.json"
    if not path.exists():
        return [], []
    name = f"reviews/{slug}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        return [], [f"{name}: 不是合法 JSON：{e}"]
    if not isinstance(data, dict) or data.get("note") != slug or not isinstance(data.get("reviews"), list):
        return [], [f"{name}: 格式需為 {{\"note\": \"{slug}\", \"reviews\": [...]}}"]
    return data["reviews"], []


@dataclass
class ReviewState:
    slug: str
    content_sha256: str
    governed: bool  # False＝內容與舊筆記基準相同，免審
    reviewed: bool = False
    needs: list[str] = field(default_factory=list)  # 還缺什麼（給 queue 與錯誤訊息）
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    authors: list[Identity] = field(default_factory=list)
    overdue: bool = False  # 待審超過寬限（errors 最後一筆就是這個訊息）
    covered: set[str] = field(default_factory=set)  # 現行內容已有 pass 的範圍

    @property
    def pending(self) -> bool:
        return self.governed and not self.reviewed


def _date(value) -> dt.date | None:
    if not isinstance(value, str) or not DATE.match(value):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _validate_entry(name: str, idx: int, r, slug: str, root: Path, today: dt.date) -> tuple[Identity | None, list[str]]:
    where = f"{name} 第 {idx + 1} 筆"
    if not isinstance(r, dict):
        return None, [f"{where}: 需為物件"]
    errs = []
    ident = parse_identity(str(r.get("reviewer", "")))
    if ident and ident.runtime == "legacy":
        errs.append(f"{where}: reviewer 不能是 legacy 佔位身分")
    if not ident:
        errs.append(f"{where}: reviewer 需為 <runtime>/<model>@<session>，runtime 為 {'/'.join(RUNTIMES)}")
    d = _date(r.get("reviewed_at"))
    if not d or d > today:
        errs.append(f"{where}: reviewed_at 需為不晚於今天的 YYYY-MM-DD")
    if r.get("role") not in ROLES:
        errs.append(f"{where}: role 需為 {'/'.join(ROLES)}")
    scope = r.get("scope")
    if not isinstance(scope, list) or not scope or any(s not in SCOPES for s in scope) or len(set(scope)) != len(scope):
        errs.append(f"{where}: scope 需為 {'/'.join(SCOPES)} 的非空子集")
    if not SHA256.match(str(r.get("content_sha256", ""))):
        errs.append(f"{where}: content_sha256 需為 64 碼小寫十六進位")
    if r.get("verdict") not in VERDICTS:
        errs.append(f"{where}: verdict 需為 {'/'.join(VERDICTS)}")
    for key in ("source_review", "author_claim"):
        if r.get(key) not in SOURCE_REVIEW_VALUES:
            errs.append(f"{where}: {key} 需為 {'/'.join(SOURCE_REVIEW_VALUES)}")
    corrections = r.get("corrections")
    if not isinstance(corrections, int) or isinstance(corrections, bool) or corrections < 0:
        errs.append(f"{where}: corrections 需為非負整數")
    elif r.get("verdict") == "pass" and corrections > 0:
        errs.append(f"{where}: verdict 為 pass 卻有 {corrections} 處更正；有更正就是 changes_requested，修完再審")
    if r.get("role") == "audit" and ident and not ident.strong:
        errs.append(f"{where}: audit 要由強模型執行（{ident.model} 不在強模型清單）")
    report = str(r.get("report", ""))
    prefix = f"{REVIEWS_DIRNAME}/{REPORTS_DIRNAME}/{slug}/"
    report_path = root / report
    if not report.startswith(prefix) or ".." in Path(report).parts or not report.endswith(".md"):
        errs.append(f"{where}: report 需為 {prefix}<檔名>.md")
    elif not report_path.is_file():
        errs.append(f"{where}: 報告檔不存在 {report}")
    else:
        body = report_path.read_text(encoding="utf-8", errors="ignore")
        if str(r.get("content_sha256", "")) not in body or str(r.get("reviewer", "")) not in body:
            errs.append(f"{where}: 報告 {report} 沒有寫出這筆紀錄的 content_sha256 與 reviewer（不能拿別篇或別次的報告充數）")
    return ident, errs


def evaluate(note: bi.Note, legacy: dict[str, str], today: dt.date, root: Path | None = None,
             backfill: bool = False) -> ReviewState:
    """一篇筆記的審查狀態與錯誤。規則見 docs/review-pipeline-plan.md 第 2.2、2.5 節。

    backfill=True：給 review_pipeline 補審免審舊筆記用，當成受管筆記算出還缺什麼（作者用 legacy 佔位、不算寬限）。"""
    root = root or bi.REPO_ROOT
    slug = note.slug
    text = note.path.read_text(encoding="utf-8")
    sha = content_hash(text)
    governed = legacy.get(slug) != sha
    st = ReviewState(slug=slug, content_sha256=sha, governed=governed)
    name = note.path.name
    reviews, ledger_errs = load_ledger(slug, root)
    st.errors.extend(ledger_errs)

    authors, bad = parse_identities(note.meta.get("written_by", ""))
    if any(a.runtime == "legacy" for a in authors) and slug not in legacy:
        st.errors.append(f"{name}: written_by 的 {LEGACY_AUTHOR} 只能用在制度上線前就有的筆記（reviews/{LEGACY_BASELINE_NAME}）")
    if backfill and not governed and not authors:
        authors = [parse_identity(LEGACY_AUTHOR)]
    st.authors = authors
    author_sessions = {a.session.lower() for a in authors}
    if governed:
        if bad or not authors:
            st.errors.append(
                f"{name}: frontmatter 'written_by' 需列出寫過內容的 agent（<runtime>/<model>@<session>，多人以 ; 分隔）"
                + (f"；不合法：{', '.join(bad)}" if bad else "")
                + ("。這篇是改過內容的舊筆記，改的人要把自己加進去並填 revised_at" if slug in legacy else "")
            )
    analyzed = _date(note.meta.get("analyzed_at"))
    revised_raw = note.meta.get("revised_at")
    revised = _date(revised_raw) if revised_raw else None
    if analyzed and analyzed > today:
        st.errors.append(f"{name}: analyzed_at {analyzed} 晚於今天")
    if revised_raw:
        if not revised:
            st.errors.append(f"{name}: revised_at 需為 YYYY-MM-DD")
        elif revised > today or (analyzed and revised < analyzed):
            st.errors.append(f"{name}: revised_at {revised} 需介於 analyzed_at 與今天之間")

    # 逐筆驗證紀錄（舊雜湊的紀錄也要合法：紀錄只追加，不能有壞資料）
    idents: list[Identity | None] = []
    prev_date = None
    for idx, r in enumerate(reviews):
        ident, errs = _validate_entry(f"reviews/{slug}.json", idx, r, slug, root, today)
        st.errors.extend(errs)
        idents.append(ident)
        d = _date(r.get("reviewed_at")) if isinstance(r, dict) else None
        if d and prev_date and d < prev_date:
            st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: reviewed_at 早於前一筆（紀錄只能追加）")
        if d and analyzed and d < analyzed:
            st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: reviewed_at 早於筆記的 analyzed_at")
        prev_date = d or prev_date

    # 獨立性：審查者不是作者；audit 不是自上次 audit 以來的審查者
    cycle_sessions: set[str] = set()
    for idx, (r, ident) in enumerate(zip(reviews, idents)):
        if not ident or not isinstance(r, dict):
            continue
        s = ident.session.lower()
        current = r.get("content_sha256") == sha
        if s in author_sessions and current:
            st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: 審查者 {ident} 也在 written_by，不能審自己寫的內容")
        if r.get("role") == "audit":
            if s in cycle_sessions:
                st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: audit 的 session 與同輪審查者相同，覆核要換人")
            if r.get("verdict") == "pass":
                cycle_sessions = set()
        else:
            cycle_sessions.add(s)

    if not governed and not backfill:
        return st
    if st.errors:
        st.needs.append("先修正上列錯誤")
        st.errors = list(dict.fromkeys(st.errors))
        return st

    cur = [(i, r, ident) for i, (r, ident) in enumerate(zip(reviews, idents)) if r.get("content_sha256") == sha]
    passes = [(i, r, ident) for i, r, ident in cur if r["verdict"] == "pass"]
    audit_pass_idx = [i for i, r, _ in cur if r["role"] == "audit" and r["verdict"] == "pass"]
    note_sr = str(note.meta.get("source_review", "")).strip()
    for i, r, _ in passes:
        if r["source_review"] != note_sr:
            st.errors.append(
                f"reviews/{slug}.json 第 {i + 1} 筆: 審查判定 source_review 為 {r['source_review']}，筆記寫 {note_sr}；筆記要照審查結論改，改完再審"
            )
    if not passes:
        st.needs.append("審查（現行內容沒有 pass 紀錄）")
    for i, r, _ in cur:
        if r["verdict"] == "changes_requested" and not any(j > i for j in audit_pass_idx):
            st.needs.append(f"修正後再審（第 {i + 1} 筆要求修改，報告 {r['report']}）")
    covered = {s for _, r, _ in passes for s in r["scope"]}
    st.covered = covered
    missing = [s for s in SCOPES if s not in covered]
    if passes and missing:
        st.needs.append(f"補審範圍 {'/'.join(missing)}")

    last_audit_any = max((i for i, r in enumerate(reviews) if r["role"] == "audit" and r["verdict"] == "pass"), default=-1)
    triggers = []
    for i in range(last_audit_any + 1, len(reviews)):
        r, ident = reviews[i], idents[i]
        if r["role"] != "review":
            continue
        if r["author_claim"] == "full" and r["source_review"] != "full":
            triggers.append(f"第 {i + 1} 筆把 full 下修為 {r['source_review']}")
        if r["corrections"] >= CORRECTIONS_TRIGGER:
            triggers.append(f"第 {i + 1} 筆提出 {r['corrections']} 處更正")
        if ident and not ident.strong:
            triggers.append(f"第 {i + 1} 筆審查者 {ident.model} 不是強模型")
    if int(sha[:8], 16) % SAMPLE_MODULO == 0 and not audit_pass_idx:
        triggers.append("抽查（雜湊抽中）")
    if triggers:
        st.needs.append("強模型覆核 audit（" + "；".join(triggers) + "）")
    st.errors = list(dict.fromkeys(st.errors))
    st.reviewed = not st.needs and not st.errors
    return _grace(st, note, analyzed, revised, today)


def _grace(st: ReviewState, note: bi.Note, analyzed, revised, today: dt.date) -> ReviewState:
    if st.reviewed or not st.governed:  # 補審舊筆記不算寬限
        return st
    start = max(d for d in (analyzed, revised, dt.date.min) if d)
    waited = (today - start).days
    msg = f"{note.path.name}: 待獨立審查（{waited} 天）：{'；'.join(st.needs) or '—'}"
    if waited > GRACE_DAYS:
        st.overdue = True
        st.errors.append(msg + f"。超過寬限 {GRACE_DAYS} 天，跑 python tools/review_pipeline.py queue 派審")
    else:
        st.warnings.append(msg)
    return st


def evaluate_all(notes: list[bi.Note], today: dt.date | None = None, root: Path | None = None) -> tuple[dict[str, ReviewState], list[str]]:
    """全部筆記的審查狀態，以及與單篇無關的錯誤（基準被改、孤兒紀錄）。"""
    root = root or bi.REPO_ROOT
    today = today or dt.date.today()
    legacy, errors = load_legacy(root)
    states = {n.slug: evaluate(n, legacy, today, root) for n in notes}
    rdir = reviews_dir(root)
    if rdir.is_dir():
        for p in sorted(rdir.glob("*.json")):
            if p.name != LEGACY_BASELINE_NAME and p.stem not in states:
                errors.append(f"reviews/{p.name}: 對應的筆記 notes/{p.stem}.md 不存在")
    return states, errors


def pending_slugs(notes: list[bi.Note]) -> set[str]:
    """待審筆記（給 README 標記與 task_cli 鎖用）；紀錄有錯也算待審。"""
    states, _ = evaluate_all(notes)
    return {s for s, st in states.items() if st.pending}


def main(argv: list[str] | None = None) -> int:
    bi.ensure_utf8_stdout()
    import argparse

    ap = argparse.ArgumentParser(description="列出筆記的獨立審查狀態，或計算單篇的分析內容雜湊")
    ap.add_argument("--hash", metavar="NOTE", help="印出這篇筆記的分析內容雜湊")
    args = ap.parse_args(argv)
    if args.hash:
        print(content_hash(Path(args.hash).read_text(encoding="utf-8")))
        return 0
    states, errors = evaluate_all(bi.load_notes())
    for st in states.values():
        if st.governed:
            label = "已審" if st.reviewed else "待審"
            print(f"{label}  {st.slug}  {'；'.join(st.needs)}")
    for e in errors:
        print(f"[!] {e}")
    legacy_count = sum(not st.governed for st in states.values())
    print(f"[*] 免審舊筆記 {legacy_count} 篇、受管 {len(states) - legacy_count} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
