#!/usr/bin/env python3
"""
tools/audit_session_memory_compression.py
跨 Session 記憶的「壓縮品質」稽核：拿原始對話日誌（Transcript JSONL）和壓縮後的記憶 Markdown 對照，
量測關鍵工程事實有多少被留下來（資訊損失率），並檢查記憶本身有沒有洩漏機密、真實家目錄路徑或客套話。唯讀，不改任何檔案。

用法：
    python tools/audit_session_memory_compression.py --transcript T.jsonl --memory M.md
        [--format md|json] [--output FILE] [--max-loss 0.4] [--decision-overlap 0.5]
        [--max-filler 0] [--max-unsupported 0] [--min-facts 3] [--max-decision-loss 0.5] [--fail-not-compressed]
    （--min-facts 最低 1；抽不到任何事實一律結束碼 2。decisions 另有類別門檻，因為總體損失率擋不住因果丟失。）

結束碼：0 [PASS]；1 [FAIL]（損失率超標，或有 FAIL 級發現）；2 輸入或參數錯誤、或量不出來（不是通過，也不是 assertion 失敗）。
只使用 Python 標準函式庫。

指標定義（全部由輸入即時計算，沒有寫死的分數）：
    事實 = 從 transcript 抽出的四類、去重後的可比對單位
        paths             檔案路徑（Windows 絕對、~、%USERPROFILE%、POSIX 絕對、含副檔名的相對路徑）
        error_codes       錯誤代碼（*Error／*Exception 名稱、ENOENT 一類 errno 名、0x 十六進位碼、HTTP 4xx/5xx、
                          exit code N、WinError N、TSnnnn、CVE-yyyy-nnnn）
        test_conclusions  測試結論（Ran N tests、N passed／failed／skipped、FAILED (...)、單獨一行 OK、N 個測試通過／失敗）
        decisions         含原因或取捨標記的句子（因為／改用／決定／because／instead of ...），只取一般文字訊息，不取工具輸出
    保留 = 記憶（去掉 HTML 註解後）以同一套規則抽得同一個事實；decisions 改用詞元重疊：
        該句在每個原因／決定標記處切成幾段，記憶中同一行或同一段對『每一段』詞元的涵蓋率都 >= --decision-overlap，
        且該行／段本身也含原因標記（所以只留做法、丟掉原因，會算損失）
    資訊損失率 = 1 - 保留事實數 / 事實總數（總體，各類別另列；某類別沒有事實時該類別為 null，不拿 0 充數）
    unsupported = 記憶抽得、但 transcript 抽不到的路徑／錯誤代碼／測試結論（壓縮把事實改錯或憑空出現）

已知限制（報告也會印出）：
    1. 比對是字面與詞元層級，不理解語意。換句話說的決策原因會被算成損失（偏嚴）；
       把關鍵字拼湊進一句話則可能被算成保留（偏鬆）。decisions 類別尤其要人工抽查。
    2. 抽取規則是啟發式：可能漏抽（例如沒副檔名的路徑）或誤抽。損失率是「可抽取事實」的保留比例，不是全部資訊的比例。
    3. transcript 結構只假設為 Claude Code 本機 JSONL 的常見形狀（每行一個 JSON；字串散在 message.content 的
       text／tool_use／tool_result 區塊），沒有官方格式保證；工具遞迴收集所有字串，只排除 uuid／時間戳／cwd 等中繼欄位。
    4. 家目錄路徑一律先正規化成 ~ 再比對，所以「C:\\Users\\<帳號>\\a.py」與「~/a.py」視為同一個事實；
       記憶若仍寫出真實帳號的家目錄路徑，會另外被 leak-home-path 擋下。
    5. 預設門檻（--max-loss 0.4 等）是本 repo 的取捨，沒有外部基準；請依自己的記憶用途調整。
    6. 含機密樣式的 transcript 句子不列入事實（要求記憶保留機密本身就是錯的），數量記在 excluded_secret_facts。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CATEGORIES = ("paths", "error_codes", "test_conclusions", "decisions")

# ---------------------------------------------------------------- 機密與家目錄（規則與 verify_inbox.py 同源）
SECRET_PATTERNS = {
    "GitHub token": r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "Anthropic / OpenAI key": r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}",
    "Google API key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "Bearer token": r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}",
    "JWT": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}",
    "assigned credential": r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|passwd|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+]{8,}",
}
_SECRET_RES = {label: re.compile(p) for label, p in SECRET_PATTERNS.items()}

HOME_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9_.-])(?:\b[a-z]:|/[a-z](?=[\\/]))?(?:\\{1,2}|/)(?:users|home)(?:\\{1,2}|/)([^\\/\s'\"`<>|*?:、，。（）)]+)"
)
PLACEHOLDER_ACCOUNTS = {"username", "user", "admin", "test", "me", "x", "you", "public", "default", "all users", "...", "…"}


def _is_placeholder(name: str) -> bool:
    return name.lower() in PLACEHOLDER_ACCOUNTS or name.startswith(("<", "$", "%"))


def real_home_accounts(text: str) -> list[str]:
    return sorted({m.group(1) for m in HOME_PATH.finditer(text) if not _is_placeholder(m.group(1))})


def canon_home(text: str) -> str:
    """把帶真實帳號的家目錄前綴換成 ~，比對與輸出都用這個形式。"""

    def sub(m: re.Match) -> str:
        return "~" if not _is_placeholder(m.group(1)) else m.group(0)

    return HOME_PATH.sub(sub, text)


def secret_labels(text: str) -> list[str]:
    return [label for label, rx in _SECRET_RES.items() if rx.search(text)]


def redact(text: str) -> str:
    for rx in _SECRET_RES.values():
        text = rx.sub("[REDACTED]", text)
    return canon_home(text)


# ---------------------------------------------------------------- 讀取 transcript
SKIP_KEYS = {
    "uuid", "parentUuid", "sessionId", "session_id", "timestamp", "cwd", "version", "gitBranch", "userType",
    "id", "tool_use_id", "requestId", "signature", "model", "role", "type", "isSidechain", "entrypoint",
}
TOOL_BLOCK_TYPES = {"tool_use", "tool_result", "server_tool_use"}
TOOL_KEYS = {"toolUseResult", "tool_result", "tool_use_result"}


class InputError(Exception):
    """輸入無法讀取、損壞、或量不出來。對應結束碼 2。"""


def _walk(obj, kind: str, out: list[tuple[str, str]]) -> None:
    if isinstance(obj, str):
        if obj.strip():
            out.append((kind, obj))
    elif isinstance(obj, list):
        for item in obj:
            _walk(item, kind, out)
    elif isinstance(obj, dict):
        block_kind = "tool" if obj.get("type") in TOOL_BLOCK_TYPES else kind
        for key, value in obj.items():
            if key in SKIP_KEYS:
                continue
            _walk(value, "tool" if key in TOOL_KEYS else block_kind, out)


def read_text_file(path: Path, what: str) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise InputError(f"無法讀取{what}：{path}（{exc.strerror or exc}）") from exc
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"{what}不是合法 UTF-8：{path}") from exc


def load_transcript(path: Path) -> list[tuple[str, str]]:
    """回傳 [(kind, text)]，kind 為 'text'（一般訊息文字）或 'tool'（工具輸入輸出）。"""
    raw = read_text_file(path, "transcript")
    segments: list[tuple[str, str]] = []
    records = 0
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"transcript 第 {lineno} 行不是合法 JSON：{exc.msg}") from exc
        if not isinstance(obj, (dict, list)):
            raise InputError(f"transcript 第 {lineno} 行是 JSON 純量，不是物件")
        records += 1
        _walk(obj, "text", segments)
    if records == 0:
        raise InputError("transcript 沒有任何 JSON 記錄（空檔或只有空白行）")
    if not segments:
        raise InputError("transcript 有記錄但沒有任何文字內容可供抽取")
    return segments


# ---------------------------------------------------------------- 事實抽取
_URL = re.compile(r"https?://\S+")
_SEG = r"[A-Za-z0-9_@.+-]"  # 路徑片段只收 ASCII：全形標點與中文緊接在路徑後面時不可被吃進去
_PATH_RES = [
    re.compile(r"[A-Za-z]:[\\/](?:" + _SEG + r"+[\\/])*" + _SEG + r"*"),
    re.compile(r"(?:~|%USERPROFILE%)[\\/](?:" + _SEG + r"+[\\/])*" + _SEG + r"*"),
    re.compile(r"(?<![A-Za-z0-9_.:/\\~%-])(?:\.{1,2}/|/)?(?:" + _SEG + r"+/)+" + _SEG + r"*\.[A-Za-z0-9]{1,6}(?![A-Za-z0-9_/])"),
    re.compile(r"(?<![A-Za-z0-9_.:/\\~%-])(?:" + _SEG + r"+\\)+" + _SEG + r"+\.[A-Za-z0-9]{1,6}(?![A-Za-z0-9_\\])"),
]
_ERRNO_NAMES = (
    "ENOENT|EACCES|EPERM|EEXIST|EADDRINUSE|ECONNREFUSED|ECONNRESET|ETIMEDOUT|ENOTFOUND|EISDIR|ENOTDIR|"
    "EMFILE|ENOSPC|EPIPE|EBUSY|EAGAIN|EINVAL"
)
_ERROR_RES = [
    (re.compile(r"\b(?!WinError\b)[A-Z][A-Za-z0-9]*(?:Error|Exception)\b"), lambda m: m.group(0).lower()),
    (re.compile(rf"\b(?:{_ERRNO_NAMES})\b"), lambda m: m.group(0).lower()),
    (re.compile(r"\b0x[0-9A-Fa-f]{4,}\b"), lambda m: m.group(0).lower()),
    (re.compile(r"\bHTTP[ /]?(?:\d\.\d )?([45]\d{2})\b"), lambda m: f"http {m.group(1)}"),
    (re.compile(r"(?i)\bexit(?:ed)?(?: with)?[ _-]?(?:status|code)[ :=]*(-?\d+)\b"), lambda m: f"exit code {m.group(1)}"),
    (re.compile(r"(?i)\breturncode[ :=]+(-?\d+)\b"), lambda m: f"exit code {m.group(1)}"),
    (re.compile(r"\bWinError[ :=]*(\d+)\b"), lambda m: f"winerror {m.group(1)}"),
    (re.compile(r"\bTS\d{4}\b"), lambda m: m.group(0).lower()),
    (re.compile(r"\bCVE-\d{4}-\d{4,7}\b"), lambda m: m.group(0).lower()),
]
_TEST_RES = [
    re.compile(r"(?i)\bRan \d+ tests?\b"),
    re.compile(r"(?i)\b\d+ (?:passed|failed|skipped|errors?)\b"),
    re.compile(r"\bFAILED \([^)\n]*\)"),
    re.compile(r"(?m)^[ \t]*(?:[-*][ \t]+)?OK(?: \([^)\n]*\))?[ \t]*$"),
    re.compile(r"(?i)(?:結果|result|status)[ \t]*[:：=]?[ \t]*OK\b"),
    re.compile(r"\d+\s*(?:個|項)?\s*測試\s*(?:全部)?\s*(?:通過|失敗)"),
]
_DECISION_MARK = re.compile(
    r"因為|由於|所以|因此|改用|改為|改成|決定|放棄|原因是|根因|"
    r"(?i:\bbecause\b|\bdecided\b|\binstead of\b|\brather than\b|\broot cause\b|\bswitch(?:ed)? to\b|\bso that\b)"
)
_SENT_SPLIT = re.compile(r"[。！？!?;；\n]|(?<=[A-Za-z0-9)])\.(?=\s)")
_STOP = {
    "the", "and", "that", "this", "with", "for", "was", "were", "are", "from", "have", "has", "had", "not", "but",
    "because", "instead", "rather", "than", "then", "will", "would", "should", "can", "could", "use", "used",
    "using", "its", "our", "your", "you", "all", "any", "into", "so", "decided",
}
_CJK_RUN = re.compile(r"[\u4e00-\u9fff]+")
_ASCII_WORD = re.compile(r"[A-Za-z0-9_]{3,}")


def norm_path(p: str) -> str:
    p = p.strip().rstrip(".,:;)")
    p = canon_home(p.replace("\\", "/"))
    p = re.sub(r"/{2,}", "/", p)
    if p.startswith("./"):
        p = p[2:]
    p = p.replace("%USERPROFILE%", "~").replace("%userprofile%", "~")
    return p.casefold()


def extract_paths(text: str) -> set[str]:
    text = _URL.sub(" ", text)
    found: set[str] = set()
    for rx in _PATH_RES:
        for m in rx.finditer(text):
            found.add(norm_path(m.group(0)))
    return {p for p in found if p and p != "~"}


def extract_errors(text: str) -> set[str]:
    found: set[str] = set()
    for rx, fmt in _ERROR_RES:
        for m in rx.finditer(text):
            found.add(fmt(m))
    return found


def extract_tests(text: str) -> set[str]:
    found: set[str] = set()
    for rx in _TEST_RES:
        for m in rx.finditer(text):
            fact = re.sub(r"\s+", " ", m.group(0).strip()).casefold().lstrip("-* ")
            if "ok" in fact and not fact.startswith(("ran", "failed")) and "(" not in fact:
                fact = "ok"  # 「OK」單獨一行，或「結果：OK」這類行內寫法，視為同一個測試結論
            found.add(fact)
    return found


def decision_sentences(text: str) -> list[str]:
    out = []
    for s in _SENT_SPLIT.split(text):
        s = re.sub(r"\s+", " ", s).strip(" -*>#\t")
        if 10 <= len(s) <= 400 and _DECISION_MARK.search(s):
            out.append(s)
    return out


def tokens(s: str) -> set[str]:
    s = s.casefold()
    toks = {w for w in _ASCII_WORD.findall(s) if w not in _STOP}
    for run in _CJK_RUN.findall(s):
        if len(run) == 1:
            toks.add(run)
        else:
            toks.update(run[i : i + 2] for i in range(len(run) - 1))
    return toks


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def memory_units(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.split("\n")]
    units = [ln for ln in lines if ln]
    paras, cur = [], []
    for ln in lines + [""]:
        if ln:
            cur.append(ln)
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    return units + paras


def sentence_segments(sentence: str) -> list[set[str]]:
    """把決策句在每個原因／決定標記處切開，回傳各段詞元（至少 2 個詞元的段才算）。

    記憶必須在『同一行或同一段』裡同時涵蓋每一段，所以只留「改用 X」而丟掉「因為 Y」會被算成損失。
    切不出符合條件的段時，退回整句。"""
    segs = [t for t in (tokens(part) for part in _DECISION_MARK.split(sentence)) if len(t) >= 2]
    return segs or [tokens(sentence)]


def best_overlap(sentence: str, units: list[str]) -> float:
    segs = sentence_segments(sentence)
    best = 0.0
    for u in units:
        if not _DECISION_MARK.search(u):
            continue
        ut = tokens(u)
        best = max(best, min(len(seg & ut) / len(seg) for seg in segs))
    return best


# ---------------------------------------------------------------- 稽核本體
_FILLER = (
    "好的", "沒問題", "當然", "太棒了", "讓我來", "我來幫", "我會幫", "很高興", "希望這", "如果還有", "感謝", "謝謝",
    "sure", "certainly", "of course", "great", "absolutely", "let me", "i'll help", "i hope", "happy to",
    "hope this helps", "as an ai",
)
_LEADING = re.compile(r"^[\s>#*\-+\d.)\]]+")


def filler_lines(memory: str) -> list[str]:
    hits = []
    for ln in memory.split("\n"):
        body = _LEADING.sub("", ln).casefold()
        for ph in _FILLER:
            if body.startswith(ph) and (ph[-1] > "\u2e80" or not body[len(ph) : len(ph) + 1].isalnum()):
                hits.append(ln.strip())
                break
    return hits


def audit(
    segments: list[tuple[str, str]],
    memory_raw: str,
    *,
    max_loss: float,
    decision_overlap: float,
    max_filler: int,
    max_unsupported: int,
    min_facts: int,
    max_decision_loss: float = 0.5,
    fail_not_compressed: bool = False,
) -> dict:
    all_text = "\n".join(t for _, t in segments)
    prose = [t for k, t in segments if k == "text"]
    memory = strip_comments(memory_raw)

    excluded_secret = 0
    t_paths = extract_paths(all_text)
    t_errors = extract_errors(all_text)
    t_tests = extract_tests(all_text)
    t_dec: list[str] = []
    for chunk in prose:
        for s in decision_sentences(chunk):
            if secret_labels(s):
                excluded_secret += 1
            elif len(tokens(s)) >= 3 and s not in t_dec:
                t_dec.append(s)

    m_paths, m_errors, m_tests = extract_paths(memory), extract_errors(memory), extract_tests(memory)
    units = memory_units(memory)

    lost: dict[str, list[str]] = {
        "paths": sorted(t_paths - m_paths),
        "error_codes": sorted(t_errors - m_errors),
        "test_conclusions": sorted(t_tests - m_tests),
        "decisions": [s for s in t_dec if best_overlap(s, units) < decision_overlap],
    }
    totals = {"paths": len(t_paths), "error_codes": len(t_errors), "test_conclusions": len(t_tests), "decisions": len(t_dec)}
    cats = {}
    for c in CATEGORIES:
        total, n_lost = totals[c], len(lost[c])
        cats[c] = {
            "total": total,
            "retained": total - n_lost,
            "lost": n_lost,
            "loss_rate": (n_lost / total) if total else None,
            "lost_items": [redact(x) for x in lost[c]],
        }
    degraded = sorted(
        p for p in lost["paths"]
        if re.search(r"(?<![A-Za-z0-9_./~-])" + re.escape(p.rsplit("/", 1)[-1]) + r"(?![A-Za-z0-9_])", memory, re.I)
    )
    total_facts = sum(totals.values())
    if total_facts == 0 or total_facts < min_facts:
        raise InputError(
            f"transcript 只抽得 {total_facts} 個事實（--min-facts {min_facts}，且至少要 1 個），樣本不足，無法量測損失率；"
            "這不是通過。請確認 transcript 內容，或調低 --min-facts（最低 1）。"
        )
    total_lost = sum(len(v) for v in lost.values())
    overall = total_lost / total_facts

    unsupported = {
        "paths": sorted(p for p in m_paths if p not in t_paths and p not in norm_path(all_text)),
        "error_codes": sorted(m_errors - t_errors),
        "test_conclusions": sorted(m_tests - t_tests),
    }
    n_unsupported = sum(len(v) for v in unsupported.values())

    findings: list[dict] = []

    def add(code: str, severity: str, detail: str) -> None:
        findings.append({"code": code, "severity": severity, "detail": detail})

    if not memory.strip():
        add("empty-memory", "FAIL", "記憶沒有任何內容（去掉 HTML 註解後為空）")
    if overall > max_loss:
        add("loss-over-threshold", "FAIL", f"資訊損失率 {overall:.3f} > --max-loss {max_loss}")
    dec_rate = cats["decisions"]["loss_rate"]
    if dec_rate is not None and dec_rate > max_decision_loss:
        add("decision-loss-over-threshold", "FAIL",
            f"decisions（含原因的決策句）損失率 {dec_rate:.3f} > --max-decision-loss {max_decision_loss}；總體損失率不會反映因果丟失，所以單獨設門檻")
    mem_secrets = secret_labels(memory_raw)
    if mem_secrets:
        add("leak-secret", "FAIL", "記憶含疑似機密：" + "、".join(mem_secrets))
    accounts = real_home_accounts(memory_raw)
    if accounts:
        add("leak-home-path", "FAIL", f"記憶含帶真實帳號的家目錄路徑（{len(accounts)} 個帳號名稱）；請改寫為 ~ 或 %USERPROFILE%")
    fl = filler_lines(memory)
    if len(fl) > max_filler:
        add("filler", "FAIL", f"{len(fl)} 行以客套話開頭（上限 {max_filler}）：" + "；".join(redact(x)[:40] for x in fl[:5]))
    if n_unsupported > max_unsupported:
        shown = [f"{c}:{x}" for c, v in unsupported.items() for x in v][:8]
        add("unsupported-fact", "FAIL", f"記憶有 {n_unsupported} 個 transcript 找不到的事實（上限 {max_unsupported}）：" + "；".join(redact(s) for s in shown))
    t_len, m_len = len(all_text), len(memory_raw)
    ratio = m_len / t_len if t_len else None
    if ratio is not None and ratio >= 1.0:
        add("not-compressed", "FAIL" if fail_not_compressed else "WARN", f"記憶字元數 {m_len} 不小於 transcript 文字 {t_len}，這不算壓縮，損失率可能只是複製貼上的結果")

    failed = any(f["severity"] == "FAIL" for f in findings)
    return {
        "verdict": "FAIL" if failed else "PASS",
        "information_loss_rate": overall,
        "facts_total": total_facts,
        "facts_lost": total_lost,
        "categories": cats,
        "degraded_paths_basename_only": [redact(p) for p in degraded],
        "unsupported": {k: [redact(x) for x in v] for k, v in unsupported.items()},
        "excluded_secret_facts": excluded_secret,
        "compression_ratio_chars": ratio,
        "findings": findings,
        "thresholds": {
            "max_loss": max_loss, "decision_overlap": decision_overlap, "max_filler": max_filler,
            "max_unsupported": max_unsupported, "min_facts": min_facts,
            "max_decision_loss": max_decision_loss, "fail_not_compressed": fail_not_compressed,
        },
        "limitations": [
            "字面與詞元比對，不理解語意：換句話說的決策原因會被算損失，關鍵字拼湊可能被算保留；decisions 需人工抽查",
            "抽取規則是啟發式，損失率只代表『可抽取事實』的保留比例",
            "transcript 結構為假設的 Claude Code 本機 JSONL 形狀，無官方格式保證",
            "預設門檻是本 repo 的取捨，沒有外部基準",
            "記憶整份複製原文時預設只出 not-compressed 警告（短樣本的記憶本來就可能比原文長）；要擋就加 --fail-not-compressed",
            "家目錄路徑偵測會略過 URL 內的 /users/、/home/ 片段，但不會偵測沒有固定路徑格式的帳號名稱",
        ],
    }


# ---------------------------------------------------------------- 輸出
def render_md(rep: dict) -> str:
    rate = rep["information_loss_rate"]
    out = [
        f"[{rep['verdict']}] 跨 Session 記憶壓縮稽核：資訊損失率 {rate:.3f}（{rep['facts_lost']}/{rep['facts_total']} 個事實未保留）",
        "",
        "| 類別 | 事實數 | 保留 | 損失 | 損失率 |",
        "| :--- | ---: | ---: | ---: | ---: |",
    ]
    for c in CATEGORIES:
        d = rep["categories"][c]
        lr = "n/a（無此類事實）" if d["loss_rate"] is None else f"{d['loss_rate']:.3f}"
        out.append(f"| {c} | {d['total']} | {d['retained']} | {d['lost']} | {lr} |")
    out += ["", "## 發現", ""]
    out += [f"- [{f['severity']}] {f['code']}：{f['detail']}" for f in rep["findings"]] or ["- 無"]
    out += ["", "## 未保留的事實（每類最多列 20 筆）", ""]
    any_lost = False
    for c in CATEGORIES:
        for item in rep["categories"][c]["lost_items"][:20]:
            out.append(f"- {c}: {item}")
            any_lost = True
    if not any_lost:
        out.append("- 無")
    if rep["degraded_paths_basename_only"]:
        out += ["", "僅剩檔名、路徑被抽象化（算損失）：" + "、".join(rep["degraded_paths_basename_only"][:20])]
    out += [
        "",
        f"其他：機密樣式而排除的句子 {rep['excluded_secret_facts']} 句；記憶／transcript 字元比 "
        + ("n/a" if rep["compression_ratio_chars"] is None else f"{rep['compression_ratio_chars']:.3f}"),
        "門檻（本 repo 取捨）：" + json.dumps(rep["thresholds"], ensure_ascii=False),
        "",
        "## 限制",
        "",
    ]
    out += [f"- {x}" for x in rep["limitations"]]
    return "\n".join(out) + "\n"


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _ratio(value: str) -> float:
    try:
        f = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"不是數字：{value}") from None
    if not 0.0 <= f <= 1.0:
        raise argparse.ArgumentTypeError(f"需介於 0 到 1：{value}")
    return f


def _nonneg(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"不是整數：{value}") from None
    if n < 0:
        raise argparse.ArgumentTypeError(f"不可為負：{value}")
    return n


def _pos(value: str) -> int:
    n = _nonneg(value)
    if n < 1:
        raise argparse.ArgumentTypeError(f"至少要 1：{value}")
    return n


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="稽核壓縮後的跨 Session 記憶相對於原始 transcript 的資訊損失（唯讀）。")
    ap.add_argument("--transcript", required=True, help="原始對話日誌（JSONL，UTF-8）")
    ap.add_argument("--memory", required=True, help="壓縮後的記憶 Markdown（UTF-8）")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--output", help="報告寫到檔案（預設印到 stdout）")
    ap.add_argument("--max-loss", type=_ratio, default=0.4, help="總體損失率上限，0~1，預設 0.4（本 repo 取捨）")
    ap.add_argument("--decision-overlap", type=_ratio, default=0.5, help="decisions 詞元涵蓋率下限，0~1，預設 0.5")
    ap.add_argument("--max-filler", type=_nonneg, default=0, help="允許以客套話開頭的行數，預設 0")
    ap.add_argument("--max-unsupported", type=_nonneg, default=0, help="允許 transcript 找不到的記憶事實數，預設 0")
    ap.add_argument("--min-facts", type=_pos, default=3, help="transcript 至少要抽得幾個事實才量測，預設 3，最低 1")
    ap.add_argument("--max-decision-loss", type=_ratio, default=0.5,
                    help="decisions 類別損失率上限，0~1，預設 0.5（本 repo 取捨）；總體門檻擋不住因果丟失，所以另設")
    ap.add_argument("--fail-not-compressed", action="store_true", help="記憶字元數不小於 transcript 時判 FAIL（預設只警告）")
    return ap


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    args = build_parser().parse_args(argv)
    try:
        segments = load_transcript(Path(args.transcript))
        memory_raw = read_text_file(Path(args.memory), "記憶檔")
        rep = audit(
            segments,
            memory_raw,
            max_loss=args.max_loss,
            decision_overlap=args.decision_overlap,
            max_filler=args.max_filler,
            max_unsupported=args.max_unsupported,
            min_facts=args.min_facts,
            max_decision_loss=args.max_decision_loss,
            fail_not_compressed=args.fail_not_compressed,
        )
    except InputError as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 2
    text = json.dumps(rep, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_md(rep)
    if args.output:
        try:
            Path(args.output).write_text(text, encoding="utf-8", newline="\n")
        except OSError as exc:
            print(f"錯誤：無法寫入報告：{args.output}（{exc.strerror or exc}）", file=sys.stderr)
            return 2
        print(f"[{rep['verdict']}] 損失率 {rep['information_loss_rate']:.3f}；報告已寫入 {args.output}")
    else:
        sys.stdout.write(text)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
