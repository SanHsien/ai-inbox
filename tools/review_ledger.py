#!/usr/bin/env python3
"""
tools/review_ledger.py
新筆記獨立審查紀錄（設計見 docs/review-pipeline-plan.md，審查標準見 docs/source-review-sop.md）。

- 每篇筆記的審查紀錄在 reviews/<slug>.json（只追加），報告在 reviews/reports/<slug>/。
- 內容雜湊只算「分析內容」：去掉任務狀態欄位的單行值，task_cli 認領／結案不會讓審查失效；其他改動都會。
- reviews/legacy-baseline.json：審查制度上線時既有筆記的內容雜湊。內容沒變的舊筆記免審，
  一改內容就要照新規則送審。基準檔雜湊釘在 LEGACY_BASELINE_SHA256，不能悄悄加入新筆記。
- 紀錄必須與報告一致（verdict、更正數、範圍、header 的身分與雜湊），已提交的紀錄與報告不可改動。

給 verify_inbox.py、build_index.py、task_cli.py、review_pipeline.py 共用。直接執行時列出每篇的審查狀態：
    python tools/review_ledger.py            # 列出待審與已審
    python tools/review_ledger.py --hash <筆記路徑>
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

REVIEWS_DIRNAME = "reviews"
REPORTS_DIRNAME = "reports"
LEGACY_BASELINE_NAME = "legacy-baseline.json"
# 基準檔（reviews/legacy-baseline.json）位元組的 SHA-256。改這個值等於宣告「這些筆記免審」，要在 REVIEW.md 說明理由。
LEGACY_BASELINE_SHA256 = "c04898281159a973668323e6841bc3a8d6a85ce906832023700b081af6b09125"

GRACE_DAYS = 7  # 新筆記（或改過內容的筆記）最多可以待審幾天
SCOPES = ("source", "facts", "evidence", "task_impact")
ROLES = ("review", "audit")
VERDICTS = ("pass", "changes_requested")
SOURCE_REVIEW_VALUES = ("full", "partial", "unavailable")
RUNTIMES = ("claude", "codex", "antigravity", "hermes", "human", "legacy")
# 制度上線前就有的筆記不知道作者 session，補審或修改時 written_by 用這個佔位；只准基準裡的筆記使用
LEGACY_AUTHOR = "legacy/unknown@pre-review"
SAMPLE_MODULO = 5  # slug 的 SHA-256 前 8 碼 mod 5 == 0 的筆記，一定要強模型覆核（抽查約 1/5）
CORRECTIONS_TRIGGER = 2  # 一次審查提出幾處以上更正，就要強模型覆核

# 強模型：可以當 audit、且當審查者時不會自動觸發覆核。其他模型（Sonnet、Haiku、Gemini Flash…）當審查者都要覆核。
# maintainer 只有 human runtime 算（見 Identity.strong）。
STRONG_MODEL = re.compile(r"^(?:opus-\d+(?:\.\d+)?|gpt-6(?:\.\d+)?-(?:sol|astra)|maintainer)$", re.IGNORECASE)

IDENTITY = re.compile(r"^(?P<runtime>[a-z][a-z0-9-]*)/(?P<model>[A-Za-z0-9._-]+)@(?P<session>[A-Za-z0-9._:-]+)$")
UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SHORT_SESSION_MIN = 8  # antigravity、hermes 沒有 UUID 格式的 session，至少要這麼長
SHA256 = re.compile(r"^[0-9a-f]{64}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATE_FIELDS = ("狀態", "完成日期", "實作紀錄 / 證據")
TASK_BOX = re.compile(r"^- \[[xX]\] (?=\*\*`T-)")
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
HEADER_FIELD = re.compile(r"^- (?P<key>reviewer|content_sha256|role): ?(?P<value>.*)$")


def _date(value) -> dt.date | None:
    if not isinstance(value, str) or not DATE.match(value):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


@dataclass
class Identity:
    runtime: str
    model: str
    session: str

    @property
    def strong(self) -> bool:
        if not STRONG_MODEL.match(self.model):
            return False
        if self.model.lower() == "maintainer":
            return self.runtime == "human"  # 別的 runtime 掛 maintainer 這個名字不算
        return True

    def __str__(self) -> str:
        return f"{self.runtime}/{self.model}@{self.session}"


def _session_ok(runtime: str, model: str, session: str) -> bool:
    """session 格式依 runtime 收緊：claude／codex 必須是完整 UUID（不接受縮寫，縮寫會讓比對形同虛設）。"""
    if runtime in ("claude", "codex"):
        return bool(UUID.match(session))
    if runtime in ("antigravity", "hermes"):
        return len(session) >= SHORT_SESSION_MIN
    if runtime == "human":
        return model == "maintainer" and _date(session) is not None
    if runtime == "legacy":
        return model == "unknown" and session == "pre-review"
    return False


def parse_identity(text: str) -> Identity | None:
    m = IDENTITY.match(text.strip())
    if not m or m["runtime"] not in RUNTIMES or not _session_ok(m["runtime"], m["model"], m["session"]):
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


def same_session(a: str, b: str) -> bool:
    """session 是否視為同一個：小寫後相等，或一方是另一方的前綴（防縮寫冒充別人）。"""
    a, b = a.lower(), b.lower()
    return bool(a) and bool(b) and (a == b or a.startswith(b) or b.startswith(a))


def sampled(slug: str) -> bool:
    """抽查：slug 的 SHA-256 前 8 碼 mod SAMPLE_MODULO == 0。用 slug 不用內容雜湊，改內容躲不掉。"""
    return int(hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8], 16) % SAMPLE_MODULO == 0


def analysis_text(text: str) -> str:
    """筆記去掉任務狀態後的「分析內容」。不算進雜湊的只有：
    - 任務勾選框（`[x]` 視同 `[ ]`）
    - 任務區塊內 狀態／完成日期／實作紀錄 / 證據 這三個欄位**那一行本身**（更深縮排的續行照算）
    - frontmatter 第一個 `status:` 行的值（值後面的註解照算）
    - 正文第一個「當前狀態」行，且值是 STATUS_BODY_LABELS 的標準標記（其他文字照算）
    所以關閉理由、證據的文字不受審查保護；單行狀態欄位別拿來寫分析。"""
    lines = text.replace("\r\n", "\n").split("\n")
    fm_end = bi.frontmatter_end(lines)
    meta_idx = bi.find_status_meta_line(lines)
    body_idx = bi.find_status_body_line(lines)
    labels = set(bi.STATUS_BODY_LABELS.values())
    out: list[str] = []
    fence: str | None = None
    in_task = False  # 狀態欄位只在任務區塊內略過；別處同名的行照算，不能拿來藏內容
    for i, line in enumerate(lines):
        if i <= fm_end:
            if i == meta_idx:
                rest = bi.STATUS_META.match(line)["rest"].strip()
                if not rest:
                    continue  # 只有值、沒有註解：整行略過（與註解以外的內容同一個雜湊）
                line = "status: " + rest
            out.append(line.rstrip())
            continue
        opened_here = fence is None
        fence, in_fence = bi.fence_step(fence, line)
        if in_fence:
            if opened_here and not line.startswith(" "):
                in_task = False  # 頂層圍欄結束目前任務的欄位區（與 bi.parse_note 一致）
        else:
            if bi.TASK_LINE.match(line):
                in_task = True
            elif line.strip() and not line.startswith(" "):
                in_task = False
            f = bi.TASK_FIELD.match(line)
            if in_task and f and f["key"].strip() in STATE_FIELDS:
                continue
            if i == body_idx and line[len(bi.STATUS_BODY_PREFIX):].strip() in labels:
                continue
            if in_task:
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


# ---------- 報告檔：結果區塊與 header ----------

def last_json_block(text: str) -> dict:
    """報告最後一個 ```json 區塊（review_pipeline.parse_result 與驗證器共用，兩邊讀到的是同一份）。"""
    blocks = JSON_BLOCK.findall(text)
    if not blocks:
        raise ValueError("報告最後沒有 ```json 結果區塊")
    try:
        data = json.loads(blocks[-1])
    except ValueError as e:
        raise ValueError(f"結果區塊不是合法 JSON：{e}") from None
    if not isinstance(data, dict):
        raise ValueError("結果區塊需為 JSON 物件")
    return data


def report_header(body: str) -> tuple[dict[str, str], list[str]]:
    """報告開頭（第一條 `---` 之前）逐行解析 `- reviewer:`、`- content_sha256:`、`- role:`（ingest 寫的格式）。
    只認 header 區的行，不接受「字串出現在內文任何地方」。回傳 (欄位, 錯誤)。"""
    lines = body.replace("\r\n", "\n").split("\n")
    if "---" not in lines:
        return {}, ["沒有 `---` 分隔線，找不到報告 header"]
    fields: dict[str, str] = {}
    errs: list[str] = []
    for line in lines[: lines.index("---")]:
        m = HEADER_FIELD.match(line)
        if not m:
            continue
        key, value = m["key"], m["value"].strip()
        if key == "role":
            value = re.split(r"[；;]", value)[0].strip()  # `- role: review；lane: codex；scope: …`
        if key in fields:
            errs.append(f"header 的 {key} 出現不只一次")
        fields[key] = value
    return fields, errs


def _scope_set(value) -> set[str] | None:
    if isinstance(value, list) and all(isinstance(s, str) for s in value):
        return set(value)
    return None


def _report_errors(where: str, report: str, r: dict, body: str) -> list[str]:
    """報告內容要和紀錄一致：header 的身分、雜湊、角色，結果區塊的 verdict、更正數、範圍。"""
    errs: list[str] = []
    header, herrs = report_header(body)
    errs.extend(f"{where}: 報告 {report} {e}" for e in herrs)
    for key in ("reviewer", "content_sha256", "role"):
        if header.get(key) != r.get(key):
            errs.append(f"{where}: 報告 {report} 的 header {key}（{header.get(key)!r}）與紀錄（{r.get(key)!r}）不同"
                        "（不能拿別篇或別次的報告充數）")
    try:
        res = last_json_block(body)
    except ValueError as e:
        return errs + [f"{where}: 報告 {report} {e}"]
    findings = res.get("findings")
    if res.get("verdict") != r.get("verdict"):
        errs.append(f"{where}: 報告 {report} 的 verdict（{res.get('verdict')!r}）與紀錄（{r.get('verdict')!r}）不同")
    corrections = res.get("corrections")
    if (type(corrections) is not int or corrections != r.get("corrections") or not isinstance(findings, list)
            or corrections != len(findings)):
        errs.append(f"{where}: 報告 {report} 的 corrections（{corrections!r}）、findings 筆數與紀錄的 corrections（{r.get('corrections')!r}）不一致")
    res_scope, entry_scope = _scope_set(res.get("scope")), _scope_set(r.get("scope"))
    if res_scope is None or res_scope != entry_scope:
        errs.append(f"{where}: 報告 {report} 的 scope（{res.get('scope')!r}）與紀錄（{r.get('scope')!r}）不同")
    return errs


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
    overdue: bool = False  # 待審超過寬限
    overdue_error: str = ""  # 寬限逾期的錯誤訊息（已在 errors 裡）
    covered: set[str] = field(default_factory=set)  # 現行內容已有 pass 的範圍
    task_errors: list[str] = field(default_factory=list)  # 待審期間任務被結案或認領（已在 errors 裡）
    flagged: bool = False  # 免審舊筆記，但現行內容有未解決的 changes_requested（視為待審）
    since: dt.date | None = None  # 待審起算日

    @property
    def pending(self) -> bool:
        return (self.governed or self.flagged) and not self.reviewed


def _validate_entry(name: str, idx: int, r, slug: str, root: Path, today: dt.date, sha: str,
                    note_claim: str) -> tuple[Identity | None, list[str]]:
    where = f"{name} 第 {idx + 1} 筆"
    if not isinstance(r, dict):
        return None, [f"{where}: 需為物件"]
    errs = []
    ident = parse_identity(str(r.get("reviewer", "")))
    if ident and ident.runtime == "legacy":
        errs.append(f"{where}: reviewer 不能是 legacy 佔位身分")
    if not ident:
        errs.append(f"{where}: reviewer 需為 <runtime>/<model>@<session>，runtime 為 {'/'.join(RUNTIMES)}；"
                    "claude／codex 的 session 要完整 UUID，antigravity／hermes 至少 8 字元，human 只能是 human/maintainer@YYYY-MM-DD")
    d = _date(r.get("reviewed_at"))
    if not d or d > today:
        errs.append(f"{where}: reviewed_at 需為不晚於今天的 YYYY-MM-DD")
    if r.get("role") not in ROLES:
        errs.append(f"{where}: role 需為 {'/'.join(ROLES)}")
    scope = r.get("scope")
    if not isinstance(scope, list) or not scope or any(s not in SCOPES for s in scope) or len(set(scope)) != len(scope):
        errs.append(f"{where}: scope 需為 {'/'.join(SCOPES)} 的非空子集")
    elif r.get("role") == "audit" and set(scope) != set(SCOPES):
        errs.append(f"{where}: audit 的 scope 必須涵蓋全部範圍（{'/'.join(SCOPES)}）；讀不到來源時 audit 要改派能讀的那一道")
    if not SHA256.match(str(r.get("content_sha256", ""))):
        errs.append(f"{where}: content_sha256 需為 64 碼小寫十六進位")
    if r.get("verdict") not in VERDICTS:
        errs.append(f"{where}: verdict 需為 {'/'.join(VERDICTS)}")
    for key in ("source_review", "author_claim"):
        if r.get(key) not in SOURCE_REVIEW_VALUES:
            errs.append(f"{where}: {key} 需為 {'/'.join(SOURCE_REVIEW_VALUES)}")
    if r.get("content_sha256") == sha and r.get("author_claim") in SOURCE_REVIEW_VALUES and r.get("author_claim") != note_claim:
        errs.append(f"{where}: author_claim（{r.get('author_claim')}）與筆記現在的 source_review（{note_claim or '未填'}）不同"
                    "（author_claim 由 ingest 從筆記讀取，不能由審查者自填）")
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
        errs.extend(_report_errors(where, report, r, report_path.read_text(encoding="utf-8", errors="ignore")))
    return ident, errs


def _first_date(text: str) -> dt.date | None:
    m = re.search(r"\d{4}-\d{2}-\d{2}", str(text))
    return _date(m.group(0)) if m else None


def _task_errors(note: bi.Note, st: ReviewState, in_legacy: bool) -> list[str]:
    """待審期間任務不可手動結案或認領：任務可能建立在還沒查核的前提上（task_cli 也鎖，這裡是事後驗證）。"""
    if st.since is None:
        return []
    name = note.path.name
    errs = []
    for t in note.tasks:
        if t.done:
            d = _first_date(t.fields.get("完成日期", ""))
            if d is None and in_legacy:
                continue  # 舊筆記的完成日期格式五花八門，讀不出來就無從判斷
            if d is None or d >= st.since:
                errs.append(f"{name}: {t.id} 在審查通過前結案（完成日期 {d or '讀不出來'}，待審起算 {st.since}）；"
                            "任務要等審查通過才能完成（關閉不受限）"
                            + ("；改過內容的舊筆記要填 revised_at，完成日期早於它的任務不受影響" if in_legacy else ""))
        elif t.in_progress and not in_legacy:
            errs.append(f"{name}: {t.id} 在審查通過前被認領（進行中）；任務要等審查通過才能認領")
    return errs


def _add_task_errors(note: bi.Note, st: ReviewState, legacy: dict[str, str]) -> None:
    if st.pending:
        st.task_errors = _task_errors(note, st, note.slug in legacy)
        st.errors.extend(st.task_errors)
        st.errors = list(dict.fromkeys(st.errors))


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
    if governed and authors and all(a.runtime == "legacy" for a in authors):
        st.errors.append(f"{name}: 舊筆記的內容改過了，written_by 除了 {LEGACY_AUTHOR} 還要加上改的人（; <runtime>/<model>@<session>）")
    if backfill and not governed and not authors:
        authors = [parse_identity(LEGACY_AUTHOR)]
    st.authors = authors
    author_sessions = [a.session for a in authors]
    if governed:
        if bad or not authors:
            st.errors.append(
                f"{name}: frontmatter 'written_by' 需列出寫過內容的 agent（<runtime>/<model>@<session>，多人以 ; 分隔；"
                "claude／codex 的 session 要完整 UUID，不可縮寫）"
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
    note_sr = str(note.meta.get("source_review", "")).strip()

    # 逐筆驗證紀錄（舊雜湊的紀錄也要合法：紀錄只追加，不能有壞資料）
    idents: list[Identity | None] = []
    prev_date = None
    for idx, r in enumerate(reviews):
        ident, errs = _validate_entry(f"reviews/{slug}.json", idx, r, slug, root, today, sha, note_sr)
        st.errors.extend(errs)
        idents.append(ident)
        d = _date(r.get("reviewed_at")) if isinstance(r, dict) else None
        if d and prev_date and d < prev_date:
            st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: reviewed_at 早於前一筆（紀錄只能追加）")
        if d and analyzed and d < analyzed:
            st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: reviewed_at 早於筆記的 analyzed_at")
        prev_date = d or prev_date

    # 獨立性：審查者不是作者；audit 不是自上次 audit 以來的審查者
    cycle_sessions: list[str] = []
    for idx, (r, ident) in enumerate(zip(reviews, idents)):
        if not ident or not isinstance(r, dict):
            continue
        s = ident.session
        current = r.get("content_sha256") == sha
        if current and any(same_session(s, a) for a in author_sessions):
            st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: 審查者 {ident} 也在 written_by，不能審自己寫的內容")
        if r.get("role") == "audit":
            if any(same_session(s, c) for c in cycle_sessions):
                st.errors.append(f"reviews/{slug}.json 第 {idx + 1} 筆: audit 的 session 與同輪審查者相同，覆核要換人")
            if r.get("verdict") == "pass":
                cycle_sessions = []
        else:
            cycle_sessions.append(s)

    if not governed and not backfill:
        return _evaluate_exempt(note, st, reviews, idents, sha, today)
    start = max((d for d in (analyzed, revised) if d), default=dt.date.min)
    st.since = start
    if st.errors:
        st.needs.append("先修正上列錯誤")
        st.errors = list(dict.fromkeys(st.errors))
        _add_task_errors(note, st, legacy)
        return st

    cur = [(i, r, ident) for i, (r, ident) in enumerate(zip(reviews, idents)) if r.get("content_sha256") == sha]
    passes = [(i, r, ident) for i, r, ident in cur if r["verdict"] == "pass"]
    audit_pass_idx = [i for i, r, _ in cur if r["role"] == "audit" and r["verdict"] == "pass"]
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
    if sampled(slug) and not audit_pass_idx:
        triggers.append("抽查（slug 抽中）")
    if triggers:
        st.needs.append("強模型覆核 audit（" + "；".join(triggers) + "）")
    st.errors = list(dict.fromkeys(st.errors))
    st.reviewed = not st.needs and not st.errors
    _add_task_errors(note, st, legacy)
    return _grace(st, note, today)


def _evaluate_exempt(note: bi.Note, st: ReviewState, reviews: list, idents: list, sha: str, today: dt.date) -> ReviewState:
    """內容與舊筆記基準相同的免審筆記。例外：現行雜湊上有未被後續 audit pass 推翻的 changes_requested
    （補審被要求修改）視為待審，寬限從該筆 reviewed_at 起算；內容還沒被改，所以不要求 written_by。"""
    st.errors = list(dict.fromkeys(st.errors))
    if st.errors:
        return st
    cur = [(i, r) for i, r in enumerate(reviews) if r.get("content_sha256") == sha]
    audit_pass_idx = [i for i, r in cur if r["role"] == "audit" and r["verdict"] == "pass"]
    open_idx = [i for i, r in cur if r["verdict"] == "changes_requested" and not any(j > i for j in audit_pass_idx)]
    if not open_idx:
        return st
    st.flagged = True
    st.needs.extend(f"修正後再審（第 {i + 1} 筆要求修改，報告 {reviews[i]['report']}）" for i in open_idx)
    st.since = min(_date(reviews[i]["reviewed_at"]) for i in open_idx)
    _add_task_errors(note, st, {note.slug: sha})  # 免審筆記一定在基準裡
    return _grace(st, note, today)


def _grace(st: ReviewState, note: bi.Note, today: dt.date) -> ReviewState:
    if st.reviewed or not st.pending:  # 補審舊筆記不算寬限
        return st
    waited = (today - st.since).days if st.since else 0
    msg = f"{note.path.name}: 待獨立審查（{waited} 天）：{'；'.join(st.needs) or '—'}"
    if waited > GRACE_DAYS:
        st.overdue = True
        st.overdue_error = msg + f"。超過寬限 {GRACE_DAYS} 天，跑 python tools/review_pipeline.py queue 派審"
        st.errors.append(st.overdue_error)
    else:
        st.warnings.append(msg)
    return st


# ---------- 已提交的紀錄與報告不可改動（只追加）----------

def _git(root: Path, *args: str):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None


def committed_history_errors(root: Path) -> list[str]:
    """git 可用且 root 就是 repo 根目錄時：HEAD 上的 reviews/<slug>.json 必須是現行陣列的前綴，
    HEAD 已追蹤的 reviews/reports/** 內容不可變更或刪除。git 不可用或檔案不在 HEAD 就略過。"""
    top = _git(root, "rev-parse", "--show-toplevel")
    if top is None or top.returncode != 0:
        return []
    try:
        if not os.path.samefile(top.stdout.strip(), root):
            return []
    except OSError:
        return []
    head = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    if head is None or head.returncode != 0:
        return []
    tree = _git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", REVIEWS_DIRNAME)
    if tree is None or tree.returncode != 0:
        return []
    errors: list[str] = []
    for rel in (p for p in tree.stdout.split("\0") if p):
        parts = rel.split("/")
        if len(parts) != 2 or not rel.endswith(".json") or parts[1] == LEGACY_BASELINE_NAME:
            continue
        old_raw = _git(root, "show", f"HEAD:{rel}")
        if old_raw is None or old_raw.returncode != 0:
            continue
        try:
            old = json.loads(old_raw.stdout)["reviews"]
        except (ValueError, KeyError, TypeError):
            continue
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel}: 已提交的審查紀錄被刪除（紀錄只能在尾端追加）")
            continue
        try:
            cur = json.loads(path.read_text(encoding="utf-8"))["reviews"]
        except (ValueError, KeyError, TypeError):
            continue  # 壞掉的格式由 load_ledger 報
        if not isinstance(old, list) or not isinstance(cur, list) or cur[: len(old)] != old:
            errors.append(f"{rel}: 已提交的審查紀錄被改動、刪除或重排（紀錄只能在尾端追加）")
    diff = _git(root, "diff", "--name-only", "-z", "--no-renames", "HEAD", "--", f"{REVIEWS_DIRNAME}/{REPORTS_DIRNAME}")
    if diff is not None and diff.returncode == 0:
        errors.extend(f"{p}: 已提交的審查報告被改動或刪除（報告只能新增）" for p in diff.stdout.split("\0") if p)
    return errors


def evaluate_all(notes: list[bi.Note], today: dt.date | None = None, root: Path | None = None) -> tuple[dict[str, ReviewState], list[str]]:
    """全部筆記的審查狀態，以及與單篇無關的錯誤（基準被改、孤兒紀錄、已提交的紀錄被改動）。"""
    root = root or bi.REPO_ROOT
    today = today or dt.date.today()
    legacy, errors = load_legacy(root)
    states = {n.slug: evaluate(n, legacy, today, root) for n in notes}
    rdir = reviews_dir(root)
    if rdir.is_dir():
        for p in sorted(rdir.glob("*.json")):
            if p.name != LEGACY_BASELINE_NAME and p.stem not in states:
                errors.append(f"reviews/{p.name}: 對應的筆記 notes/{p.stem}.md 不存在")
        errors.extend(committed_history_errors(root))
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
        if st.governed or st.flagged:
            label = "已審" if st.reviewed else "待審"
            print(f"{label}  {st.slug}  {'；'.join(st.needs)}")
    for e in errors:
        print(f"[!] {e}")
    legacy_count = sum(not st.governed for st in states.values())
    print(f"[*] 免審舊筆記 {legacy_count} 篇、受管 {len(states) - legacy_count} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
