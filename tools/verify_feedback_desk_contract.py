#!/usr/bin/env python3
"""
tools/verify_feedback_desk_contract.py
feedback-desk 工單合規與交接契約的外部裁判。唯讀，只用 Python 標準函式庫。

依據 docs/feedback-desk-architecture-and-handoff-spec.md。輸入是 JSON：單一紀錄、紀錄陣列，
或 {"records": [...]}。每筆紀錄必須有 kind：

    status_change  改狀態。必填 public_id、actor_type(ai|human|client)、actor_name、from、to。
                   AI（actor_type=ai，或帶了 agent 名稱）只能改成 needs_input，且必須附調整說明
                   (adjustment_note) 與至少一張圖 (adjustment_images)。
    handoff        交接紀錄。必填 public_id、actor_type、actor_name、note；note 要有「做到哪」
                   與「下一步」兩段實質內容（「改了哪些檔案」「注意事項」缺少只警告）。
    adjustment     給客戶看的調整說明。必填 public_id、note；要有「調整原因／調整內容／驗證方式」，
                   不可含程式碼區塊、行內程式碼、檔名、路徑、函式呼叫。

選填共用欄位：agent（AI 工具名稱）、claim_holder（{"name","agent"}，別人認領中）、force（布林）、release（布林）。

用法：
    python tools/verify_feedback_desk_contract.py FILE [FILE ...] [--strict] [--json]
    python tools/verify_feedback_desk_contract.py -        # 從標準輸入讀

結束碼：0 全部通過；1 有 ERROR（或 --strict 且有 WARN）；2 輸入錯誤（找不到檔、不是 JSON、
沒有任何紀錄、kind 缺漏）。「沒有東西可驗」一律是 2，不會假通過。

調整說明的「不放程式碼」規則對應 aixwangtw/de-ai-slop 的 R24（固定 commit 8eea1a9）：只掃機械可判斷的
特徵（反斜線、$、{}、底線變數名、副檔名，再加程式碼區塊、行內程式碼、路徑、函式呼叫、例外名稱）。
de-ai-slop 其餘 65 條是文風規則，無法機械判定，本工具不檢查，也不代表通過。

規則出處分兩種（見規範文件第 7 節）：標 [upstream] 的來自 aixwangtw/feedback-desk 固定 commit 的
原始碼或 README；標 [本 repo] 的是本 repo 加上去的取捨，不是原作行為。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

STATUSES = ("new", "needs_input", "completed")
STATUS_LABELS = {"待處理": "new", "待審核": "needs_input", "已完成": "completed"}
ACTOR_TYPES = ("ai", "human", "client")
KINDS = ("status_change", "handoff", "adjustment")

MAX_HANDOFF_NOTE = 5000  # [upstream] src/worker/lib/team.ts MAX_HANDOFF_NOTE
MAX_ADJUSTMENT_NOTE = 20000  # [upstream] src/worker/lib/reports.ts MAX_ADJUSTMENT_NOTE
MAX_AGENT_LENGTH = 40  # [upstream] src/worker/lib/agents.ts

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff\u00ad"), None)

# 交接紀錄的四段標籤。前兩段必填。
HANDOFF_LABELS = {
    "done": ("做到哪",),
    "files": ("改了哪些檔案或分支", "改了哪些檔案", "改過哪些檔案或分支", "改過哪些檔案"),
    "next": ("下一步",),
    "caution": ("注意事項",),
}
_LABEL_ALL = sorted({l for ls in HANDOFF_LABELS.values() for l in ls}, key=len, reverse=True)
_LABEL_RE = re.compile("(" + "|".join(map(re.escape, _LABEL_ALL)) + r")[ \t]*[：:]")
# 內容只有這些就當作沒寫
_PLACEHOLDERS = {"無", "没有", "沒有", "略", "同上", "待補", "tbd", "todo", "n/a", "na", "none", "null", "-", "—", "?", "？"}

NOTE_LABELS = {
    "reason": ("調整原因",),
    "content": ("調整內容",),
    "verify": ("驗證方式",),
}
_NOTE_LABEL_RE = re.compile("(" + "|".join(map(re.escape, [l for ls in NOTE_LABELS.values() for l in ls])) + r")[ \t]*[：:]")

_URL_RE = re.compile(r"https?://[^\s)）」』>]+", re.IGNORECASE)
_FENCE_RE = re.compile(r"(```|~~~)")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_FILE_EXT = (
    "ts|tsx|js|jsx|mjs|cjs|py|php|rb|go|rs|java|kt|swift|c|cc|cpp|h|hpp|cs|vue|svelte|css|scss|html|htm|"
    "json|jsonc|yml|yaml|toml|ini|env|md|sql|sh|bash|ps1|bat|cmd|lock|xml|gradle"
)
_FILENAME_RE = re.compile(r"(?<![\w])[\w.\-]*[\w\-]\.(?:" + _FILE_EXT + r")(?![\w])", re.IGNORECASE)
_CODE_DIRS = (
    "src|app|lib|api|test|tests|public|components|routes|node_modules|dist|build|config|views|controllers|"
    "models|services|utils|pages|assets|scripts|tools|docs|migrations|worker|client|server|vendor|bin"
)
# Windows 磁碟路徑、反斜線路徑、./ ../ 相對路徑，或以常見程式碼目錄開頭的多層路徑。
# 刻意不抓「2026/11/02」「和/或/及」這類一般斜線文字。
_PATH_RE = re.compile(
    r"(?:[A-Za-z]:\\[^\s]+|[\w.\-]+(?:\\[\w.\-]+){2,}|(?<![\w])\.{1,2}/[\w.\-]+(?:/[\w.\-]+)*"
    r"|(?<![\w/:])/?(?:" + _CODE_DIRS + r")(?:/[\w.\-]+)+)",
    re.IGNORECASE,
)
# de-ai-slop R24（commit 8eea1a9）：寫完掃反斜線、$、{}、底線變數名、副檔名。$ 只抓後面接識別字的寫法，避免誤殺金額。
_BACKSLASH_RE = re.compile(r"\\")
_BRACE_RE = re.compile(r"\{[^}\n]*\}")
_DOLLAR_RE = re.compile(r"\$[A-Za-z_{(]")
_SNAKE_RE = re.compile(r"(?<![\w])[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+(?![\w])")
_CALL_RE = re.compile(r"(?<![\w])[A-Za-z_][\w.]*\(\s*[^)]{0,40}\)")
_CJK_RE = re.compile("[぀-ヿ㐀-䶿一-鿿가-힯]")
# 函式呼叫的括號內若出現逗號、引號、等號、點，或完全沒有空白，才當成引數；
# 括號內有中日韓字元（Google(谷歌)）或只是帶空白的註記（iPhone(iOS 17)）不算。
_ARG_HINT_RE = re.compile(r"[,;'\"=.>]")
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>\n]*)?/?>")
_CAMEL_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9]*[a-z0-9][A-Z][A-Za-z0-9]*(?![A-Za-z0-9])")
# 常見品牌字（有大小寫混合但不是程式識別字）。清單是本 repo 的取捨，不完整；沒列到的品牌只會得到 WARN。
_BRANDS = frozenset(
    "iPhone iPad iPod iOS iPadOS macOS tvOS watchOS iCloud iMessage iTunes iMac MacBook AirPods FaceTime "
    "GitHub GitLab YouTube LinkedIn PayPal WordPress WhatsApp TikTok OpenAI ChatGPT JavaScript TypeScript "
    "PowerPoint OneDrive SharePoint PlayStation DeepL WeChat WooCommerce PostgreSQL MySQL MongoDB eBay "
    "LibreOffice OpenClaw WebP DevOps".split()
)
_CODE_SUFFIXES = (
    "Controller", "Handler", "Service", "Manager", "Provider", "Factory", "Repository", "Component", "Module",
    "Utils", "Util", "Helper", "Hook", "Store", "Reducer", "Middleware", "Router", "Model", "View", "Context",
    "Props", "State", "Config", "Client", "Adapter", "Listener", "Wrapper", "Builder",
)
_VERB_PREFIX_RE = re.compile(r"^(?:handle|get|set|on|use|is|has|fetch|render|validate|update|create|delete|submit|parse|init|load|save|toggle)[A-Z]")


def find_code_call(text: str) -> Optional[str]:
    """回傳第一個像函式呼叫的片段；括號內是中文或帶空白註記的不算。"""
    for m in _CALL_RE.finditer(text):
        raw = m.group(0)
        inner = raw[raw.index("(") + 1:-1]
        if _CJK_RE.search(inner):
            continue
        if inner.strip() and re.search(r"\s", inner.strip()) and not _ARG_HINT_RE.search(inner):
            continue
        return raw
    return None


def camel_identifiers(text: str) -> "tuple[List[str], List[str]]":
    """回傳 (確定是程式識別字, 疑似但可能是品牌字)。品牌清單內的略過。"""
    sure: List[str] = []
    maybe: List[str] = []
    for m in _CAMEL_RE.finditer(text):
        tok = m.group(0)
        if tok in _BRANDS:
            continue
        if tok.endswith(_CODE_SUFFIXES) or _VERB_PREFIX_RE.match(tok):
            sure.append(tok)
        else:
            maybe.append(tok)
    return sure, maybe
_TRACE_RE = re.compile(r"(Traceback \(most recent call last\)|\bat [\w.$<>]+\(.+:\d+(:\d+)?\)|\bException\b|\bNullPointer\w*|\bNPE\b)")
# [本 repo] 對客說明常見的內部詞，只警告。
_JARGON = ("重構", "依賴注入", "refactor", "commit", "merge", "endpoint", "stack trace", "null pointer", "race condition", "regex")

_SECRET_PATTERNS = (
    ("bearer-token", re.compile(r"bearer[ \t]+[A-Za-z0-9._\-]{16,}", re.IGNORECASE)),
    ("fdp-token", re.compile(r"\bfdp_[A-Za-z0-9]{8,}")),
    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghs|ghu|github_pat)_[A-Za-z0-9_]{16,}")),
    ("password-assignment", re.compile(r"(?:password|passwd|pwd|密碼|token|secret|api[_-]?key)[ \t]*[=：:][ \t]*\S{4,}", re.IGNORECASE)),
    ("connection-string", re.compile(r"\b\w+://[^\s:/@]+:[^\s@]+@")),
)


@dataclass
class Finding:
    level: str  # ERROR | WARN
    code: str
    where: str
    message: str


class InputError(Exception):
    """輸入本身不可用（結束碼 2）。"""


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def normalize_text(value: str) -> str:
    """NFKC（全形反引號、全形冒號變半形）並移除零寬字元，避免用字元變體躲過檢查。"""
    return unicodedata.normalize("NFKC", value).translate(_ZERO_WIDTH)


def normalize_status(value: Any) -> Optional[str]:
    """比照 upstream statusFromInput：去頭尾空白、不分大小寫，接受中文標籤。認不得回 None。"""
    if not isinstance(value, str):
        return None
    v = normalize_text(value).strip().lower()
    if v in STATUSES:
        return v
    return STATUS_LABELS.get(normalize_text(value).strip())


def agent_label_problem(value: str) -> Optional[str]:
    """[upstream] normalizeAgent：只允許字母數字、空白與 . _ - / +，最長 40 字，不可含括號。"""
    if value != value.strip() or value == "":
        return "不可為空白或頭尾帶空白"
    if len(value) > MAX_AGENT_LENGTH:
        return f"超過 {MAX_AGENT_LENGTH} 字"
    if re.search(r"[^\w .\-/+]", value, re.UNICODE):
        return "含有不允許的字元（括號等會冒充「名字（工具）」標籤）"
    return None


def _is_blank(v: Any) -> bool:
    return not isinstance(v, str) or normalize_text(v).strip() == ""


def _section_has_content(text: str) -> bool:
    cleaned = text.strip(" \t\r\n；;、，,。.-—*•")
    if cleaned == "":
        return False
    return cleaned.strip().lower() not in _PLACEHOLDERS


def parse_sections(text: str, label_re: "re.Pattern[str]") -> Dict[str, List[str]]:
    """把「標籤：內容」切成 {標籤: [內容...]}。標籤可在行首或接在分號之後。"""
    matches = list(label_re.finditer(text))
    out: Dict[str, List[str]] = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.setdefault(m.group(1), []).append(text[m.end():end])
    return out


def _sec_for(sections: Dict[str, List[str]], names: Iterable[str]) -> Optional[str]:
    """同義標籤任一個有實質內容就回傳該內容；有標籤但全空回傳 ""；完全沒標籤回 None。"""
    seen = False
    for n in names:
        for body in sections.get(n, []):
            seen = True
            if _section_has_content(body):
                return body
    return "" if seen else None


def scan_secrets(text: str) -> List[str]:
    return [name for name, rx in _SECRET_PATTERNS if rx.search(text)]


def slop_findings(note: str) -> List[Finding]:
    """對客調整說明的 AI Slop 特徵。回傳的 where 由呼叫端補。"""
    findings: List[Finding] = []
    text = normalize_text(note)
    if _FENCE_RE.search(text):
        findings.append(Finding("ERROR", "slop-code-block", "", "調整說明含程式碼區塊（``` 或 ~~~）"))
    # 先拿掉網址，客戶要去的頁面網址是合法內容
    no_url = _URL_RE.sub(" ", text)
    if _INLINE_CODE_RE.search(no_url):
        findings.append(Finding("ERROR", "slop-inline-code", "", "調整說明含行內程式碼（反引號）"))
    stripped = _INLINE_CODE_RE.sub(" ", no_url)
    m = _FILENAME_RE.search(stripped)
    if m:
        findings.append(Finding("ERROR", "slop-filename", "", f"調整說明含檔名：{m.group(0)}"))
    m = _PATH_RE.search(stripped)
    if m:
        findings.append(Finding("ERROR", "slop-path", "", f"調整說明含檔案路徑：{m.group(0)}"))
    for code, rx, label in (
        ("slop-backslash", _BACKSLASH_RE, "反斜線"),
        ("slop-braces", _BRACE_RE, "大括號內容"),
        ("slop-dollar-var", _DOLLAR_RE, "$ 變數寫法"),
        ("slop-identifier", _SNAKE_RE, "底線變數名"),
    ):
        m = rx.search(stripped)
        if m:
            findings.append(Finding("ERROR", code, "", f"調整說明含{label}：{m.group(0)}"))
    call = find_code_call(stripped)
    if call:
        findings.append(Finding("ERROR", "slop-code-call", "", f"調整說明含函式呼叫寫法：{call}"))
    m = _HTML_TAG_RE.search(stripped)
    if m:
        findings.append(Finding("ERROR", "slop-html-tag", "", f"調整說明含 HTML 標籤：{m.group(0)}"))
    sure, maybe = camel_identifiers(stripped)
    if sure:
        findings.append(Finding("ERROR", "slop-camelcase", "", "調整說明含程式識別字（類別、函式或元件名）：" + "、".join(sure)))
    if maybe:
        findings.append(Finding("WARN", "slop-camelcase-maybe", "", "調整說明含大小寫混合的詞，若不是品牌字請改成白話：" + "、".join(maybe)))
    m = _TRACE_RE.search(stripped)
    if m:
        findings.append(Finding("ERROR", "slop-error-trace", "", f"調整說明含錯誤堆疊或例外名稱：{m.group(0)}"))
    low = stripped.lower()
    hits = [j for j in _JARGON if j in low]
    if hits:
        findings.append(Finding("WARN", "slop-jargon", "", "調整說明含內部術語，客戶可能看不懂：" + "、".join(hits)))
    return findings


def _type_error(f: List[Finding], where: str, key: str, expect: str) -> None:
    f.append(Finding("ERROR", "bad-type", where, f"欄位 {key} 型別錯誤，需要 {expect}"))


def _bool_field(rec: Dict[str, Any], key: str, where: str, f: List[Finding]) -> bool:
    """布林欄位必須是真正的 true/false；字串 "false" 之類會被當錯誤，不是 truthy。"""
    if key not in rec or rec[key] is None:
        return False
    v = rec[key]
    if not isinstance(v, bool):
        _type_error(f, where, key, "布林值 true/false")
        return False
    return v


def _image_count(rec: Dict[str, Any], key: str, where: str, f: List[Finding]) -> int:
    v = rec.get(key)
    if v is None:
        return 0
    if isinstance(v, bool):
        _type_error(f, where, key, "整數張數或檔名清單")
        return 0
    if isinstance(v, int):
        if v < 0:
            f.append(Finding("ERROR", "bad-value", where, f"{key} 不可為負數"))
            return 0
        return v
    if isinstance(v, list):
        names = [x for x in v if isinstance(x, str) and x.strip()]
        if len(names) != len(v):
            f.append(Finding("ERROR", "bad-value", where, f"{key} 清單內有空白或非字串項目"))
        return len(names)
    _type_error(f, where, key, "整數張數或檔名清單")
    return 0


def _actor(rec: Dict[str, Any], where: str, f: List[Finding]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"type": None, "name": None, "agent": None, "is_ai": False}
    t = rec.get("actor_type")
    if not isinstance(t, str) or normalize_text(t).strip().lower() not in ACTOR_TYPES:
        f.append(Finding("ERROR", "bad-actor-type", where, f"actor_type 必須是 {'/'.join(ACTOR_TYPES)}，收到 {t!r}"))
    else:
        out["type"] = normalize_text(t).strip().lower()
    name = rec.get("actor_name")
    if _is_blank(name):
        f.append(Finding("ERROR", "missing-actor-name", where, "缺 actor_name：每個動作都要記錄是誰做的（審計）"))
    else:
        out["name"] = normalize_text(name).strip()
    agent = rec.get("agent")
    if agent is not None:
        if not isinstance(agent, str):
            _type_error(f, where, "agent", "字串")
        elif agent.strip() != "":
            problem = agent_label_problem(agent)
            if problem:
                f.append(Finding("ERROR", "bad-agent-label", where, f"agent 名稱不合格：{problem}"))
            out["agent"] = agent.strip()
    # [本 repo] 帶了 agent 名稱就當 AI，避免寫 actor_type=human 再附 agent 來躲 AI 規則
    out["is_ai"] = out["type"] == "ai" or out["agent"] is not None
    if out["type"] == "ai" and out["agent"] is None and not any(x.code == "bad-agent-label" for x in f):
        f.append(Finding("ERROR", "ai-missing-agent", where, "AI 動作缺 agent：審計紀錄要有 AI 工具名稱（例如 Codex）"))
    return out


def _claim_check(rec: Dict[str, Any], actor: Dict[str, Any], force: bool, where: str, f: List[Finding]) -> Optional[Dict[str, Any]]:
    holder = rec.get("claim_holder")
    if holder is None:
        return None
    if not isinstance(holder, dict) or _is_blank(holder.get("name")):
        f.append(Finding("ERROR", "bad-claim-holder", where, "claim_holder 需為 {\"name\": ..., \"agent\": ...}"))
        return None
    h_name = normalize_text(holder["name"]).strip()
    h_agent = holder.get("agent")
    h_agent = h_agent.strip() if isinstance(h_agent, str) and h_agent.strip() else None
    mine = actor["name"] is not None and h_name == actor["name"] and h_agent == actor["agent"]
    return {"name": h_name, "agent": h_agent, "mine": mine}


def check_adjustment_note(rec_note: Any, images: int, where: str, f: List[Finding], need_image: bool) -> None:
    if not isinstance(rec_note, str):
        if rec_note is None:
            f.append(Finding("ERROR", "missing-adjustment-note", where, "缺調整說明 (note / adjustment_note)"))
        else:
            _type_error(f, where, "note", "字串")
        return
    if _is_blank(rec_note):
        f.append(Finding("ERROR", "missing-adjustment-note", where, "調整說明是空白"))
        return
    if len(rec_note) > MAX_ADJUSTMENT_NOTE:
        f.append(Finding("ERROR", "note-too-long", where, f"調整說明超過 {MAX_ADJUSTMENT_NOTE} 字"))
    text = normalize_text(rec_note)
    sections = parse_sections(text, _NOTE_LABEL_RE)
    for key, names in NOTE_LABELS.items():
        got = _sec_for(sections, names)
        if got is None:
            f.append(Finding("ERROR", "note-missing-section", where, f"調整說明缺「{names[0]}」段"))
        elif got == "":
            f.append(Finding("ERROR", "note-empty-section", where, f"調整說明「{names[0]}」段沒有實質內容"))
    for s in slop_findings(rec_note):
        f.append(Finding(s.level, s.code, where, s.message))
    for name in scan_secrets(text):
        f.append(Finding("ERROR", "secret-in-text", where, f"調整說明疑似含機密（{name}）"))
    if need_image and images < 1:
        f.append(Finding("ERROR", "missing-screenshot", where, "調整說明沒有附任何截圖（[本 repo] 規範要至少一張驗收截圖）"))


def check_status_change(rec: Dict[str, Any], where: str) -> List[Finding]:
    f: List[Finding] = []
    if _is_blank(rec.get("public_id")):
        f.append(Finding("ERROR", "missing-public-id", where, "缺 public_id"))
    actor = _actor(rec, where, f)
    force = _bool_field(rec, "force", where, f)
    to = normalize_status(rec.get("to"))
    frm = normalize_status(rec.get("from"))
    if to is None:
        f.append(Finding("ERROR", "bad-status", where, f"to 不是合法狀態（{'/'.join(STATUSES)} 或中文），收到 {rec.get('to')!r}"))
    if frm is None:
        f.append(Finding("ERROR", "bad-status", where, f"from 不是合法狀態，收到 {rec.get('from')!r}"))
    holder = _claim_check(rec, actor, force, where, f)
    if holder and not holder["mine"] and not force:
        f.append(Finding("ERROR", "claim-conflict", where, f"單由 {holder['name']} 認領中，改狀態要明確 force=true 接手（會被記錄）[upstream]"))
    if actor["is_ai"] and to is not None:
        if to == "completed":
            f.append(Finding("ERROR", "ai-completed", where, "AI 不可把單改成 completed，只能推到 needs_input，由客戶或負責人結案 [upstream 工作規則；本 repo 當硬閘門]"))
        elif to != "needs_input":
            f.append(Finding("ERROR", "ai-status-not-allowed", where, f"AI 只能改成 needs_input，收到 {to}；驗證沒過不要改狀態，改寫交接紀錄或留言 [本 repo]"))
        else:
            images = _image_count(rec, "adjustment_images", where, f)
            check_adjustment_note(rec.get("adjustment_note"), images, where, f, need_image=True)
    if actor["type"] == "client" and not actor["is_ai"] and to == "completed" and frm is not None and frm != "needs_input":
        f.append(Finding("ERROR", "client-completed-without-review", where, f"客戶只能把待審核 (needs_input) 的單結案，這筆從 {frm} 直接 completed [本 repo]"))
    if frm is not None and to is not None and frm == to:
        f.append(Finding("WARN", "no-op-transition", where, "from 與 to 相同，沒有實際狀態變化"))
    return f


def check_handoff(rec: Dict[str, Any], where: str) -> List[Finding]:
    f: List[Finding] = []
    if _is_blank(rec.get("public_id")):
        f.append(Finding("ERROR", "missing-public-id", where, "缺 public_id"))
    actor = _actor(rec, where, f)
    force = _bool_field(rec, "force", where, f)
    release = _bool_field(rec, "release", where, f)
    if actor["type"] == "client" and not actor["is_ai"]:
        f.append(Finding("ERROR", "client-handoff", where, "交接紀錄只有團隊側能寫，客戶帳號不行 [upstream]"))
    holder = _claim_check(rec, actor, force, where, f)
    if release:
        if holder is None:
            f.append(Finding("ERROR", "release-without-claim", where, "release=true 但沒有 claim_holder：upstream 只會釋放自己的認領，這筆實際不會釋放"))
        elif not holder["mine"]:
            f.append(Finding("ERROR", "release-not-holder", where, f"release=true 但認領人是 {holder['name']}，不是 {actor['name']}：upstream 會默默不釋放"))
    note = rec.get("note")
    if note is None or (isinstance(note, str) and normalize_text(note).strip() == ""):
        f.append(Finding("ERROR", "missing-handoff-note", where, "交接紀錄 note 是空白 [upstream: note_required]"))
        return f
    if not isinstance(note, str):
        _type_error(f, where, "note", "字串")
        return f
    text = normalize_text(note)
    if len(text.strip()) > MAX_HANDOFF_NOTE:
        f.append(Finding("ERROR", "note-too-long", where, f"交接紀錄超過 {MAX_HANDOFF_NOTE} 字 [upstream]"))
    sections = parse_sections(text, _LABEL_RE)
    for key, required in (("done", True), ("next", True), ("files", False), ("caution", False)):
        names = HANDOFF_LABELS[key]
        got = _sec_for(sections, names)
        level = "ERROR" if required else "WARN"
        if got is None:
            f.append(Finding(level, "handoff-missing-section", where, f"交接紀錄缺「{names[0]}」段"))
        elif got == "":
            f.append(Finding(level, "handoff-empty-section", where, f"交接紀錄「{names[0]}」段沒有實質內容（空白或只寫「無」「待補」）"))
    for name in scan_secrets(text):
        f.append(Finding("ERROR", "secret-in-text", where, f"交接紀錄疑似含機密（{name}）[upstream: 不要寫入密碼、token]"))
    return f


def check_adjustment(rec: Dict[str, Any], where: str) -> List[Finding]:
    f: List[Finding] = []
    if _is_blank(rec.get("public_id")):
        f.append(Finding("ERROR", "missing-public-id", where, "缺 public_id"))
    actor = _actor(rec, where, f)
    if actor["type"] == "client" and not actor["is_ai"]:
        f.append(Finding("ERROR", "client-adjustment", where, "調整說明只有團隊側能寫 [upstream]"))
    _bool_field(rec, "force", where, f)
    images = _image_count(rec, "images", where, f)
    check_adjustment_note(rec.get("note"), images, where, f, need_image=True)
    return f


_CHECKERS = {"status_change": check_status_change, "handoff": check_handoff, "adjustment": check_adjustment}


def extract_records(data: Any) -> List[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "records" in data:
            if not isinstance(data["records"], list):
                raise InputError("records 必須是陣列")
            return data["records"]
        return [data]
    raise InputError("JSON 頂層必須是物件或陣列")


def validate_records(data: Any, source: str = "<input>") -> List[Finding]:
    records = extract_records(data)
    if not records:
        raise InputError(f"{source}：沒有任何紀錄可驗證（空陣列不算通過）")
    findings: List[Finding] = []
    for i, rec in enumerate(records):
        where = f"{source}#{i}"
        if not isinstance(rec, dict):
            raise InputError(f"{where}：紀錄必須是物件，收到 {type(rec).__name__}")
        kind = rec.get("kind")
        if kind not in KINDS:
            raise InputError(f"{where}：kind 必須是 {'/'.join(KINDS)}，收到 {kind!r}")
        findings.extend(_CHECKERS[kind](rec, f"{where}({kind})"))
    return findings


def load_json(path: str) -> Any:
    try:
        raw = sys.stdin.buffer.read() if path == "-" else Path(path).read_bytes()
    except OSError as exc:
        raise InputError(f"{path}：讀不到（{exc.__class__.__name__}）") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"{path}：不是合法 UTF-8") from exc
    if text.strip() == "":
        raise InputError(f"{path}：檔案是空的")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"{path}：不是合法 JSON（{exc.msg}，第 {exc.lineno} 行）") from exc


def main(argv: Optional[List[str]] = None) -> int:
    _utf8_stdio()
    ap = argparse.ArgumentParser(description="feedback-desk 工單合規與交接契約驗證器")
    ap.add_argument("files", nargs="+", help="JSON 檔路徑；- 表示標準輸入")
    ap.add_argument("--strict", action="store_true", help="WARN 也視為失敗")
    ap.add_argument("--json", action="store_true", help="以 JSON 輸出結果")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code not in (0, None) else 0
    all_findings: List[Finding] = []
    try:
        for path in args.files:
            all_findings.extend(validate_records(load_json(path), path))
    except InputError as exc:
        print(f"[ERROR] 輸入錯誤：{exc}", file=sys.stderr)
        return 2
    errors = [x for x in all_findings if x.level == "ERROR"]
    warns = [x for x in all_findings if x.level == "WARN"]
    failed = bool(errors) or (args.strict and bool(warns))
    if args.json:
        print(json.dumps({"ok": not failed, "findings": [asdict(x) for x in all_findings]}, ensure_ascii=False, indent=2))
    else:
        for x in all_findings:
            print(f"[{x.level}] {x.code} {x.where}：{x.message}")
        print(f"[{'FAIL' if failed else 'PASS'}] {len(errors)} 個 ERROR、{len(warns)} 個 WARN")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
