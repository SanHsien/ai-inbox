#!/usr/bin/env python3
"""
tools/verify_session_token_sentinel.py
長會話 Token 哨兵的驗證工具與 UserPromptSubmit hook 參考實作（規範見 docs/long-chat-session-handoff-spec.md）。

行為依據：littlehole2025/claude-saver 的 hooks/long-chat-reminder.js（固定在 commit
434750eb61510db40d567617862800f4fde2f65c）。本工具是用 Python 重寫的對照版，不是該外掛本身。

子命令：
    check <transcript.jsonl>   讀 transcript 末端 2MB，反向找最後一筆有效 usage，判定本輪會是 silent / notify / inject
    simulate --tokens a,b,c    用一串假 token 讀數跑狀態機，可用 --expect 比對每輪預期
    classify "<提問>"           延續 vs 新話題的啟發式判定（只是回歸用的粗規則，不是產品邏輯）
    title "<對話名稱>"          算出交接後新對話的名稱（結尾數字加 1，沒有數字補 -2）
    cost                       純算術：繼續留在長對話 vs 開新對話的累計輸入 token（未加權、未計價）
    hook                       讀 stdin 的 UserPromptSubmit JSON，輸出 hook JSON（可直接當 command hook 用）

判定語意（與原作一致）：
    tokens < limit                 -> silent  （不輸出、不動狀態）
    tokens >= limit，級距沒升高     -> inject  （只給 Claude 的 additionalContext，使用者看不到提示）
    tokens >= limit，級距升高       -> notify  （additionalContext + 使用者看得到的 systemMessage，並記錄級距）
    級距 = (tokens - limit) // step

結束碼：
    0  通過（check 量得到；simulate/--expect 全符合；classify/title/cost 成功；hook 正常）
    1  驗證失敗或量不到：transcript 缺檔、空檔、沒有有效 usage、整份壞掉、--expect 不符、
       hook 收到壞參數（含 argparse 錯誤）、壞 stdin／缺欄位／不安全的 session_id／壞門檻
       （hook 預設對「量不到」寬容：缺檔或還沒有 usage 時 exit 0 並在 stderr 說明，加 --strict 才 exit 1；
        整份壞掉、壞 stdin 永遠 exit 1）
    2  命令列參數錯誤（argparse；hook 子命令例外，一律 1）
hook 絕不使用 exit 2：官方文件規定 UserPromptSubmit 的 exit 2 會擋掉使用者的提問。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path

DEFAULT_LIMIT = 150_000
DEFAULT_STEP = 50_000
DEFAULT_TAIL_BYTES = 2_000_000
USAGE_KEYS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
_SAFE_SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


class SentinelError(Exception):
    """量不到或輸入不合法；CLI 一律轉成 exit 1。"""


# ---------------------------------------------------------------- 讀 transcript 末端

def read_tail(path: Path, max_bytes: int = DEFAULT_TAIL_BYTES) -> tuple[bytes, bool]:
    """回傳 (末端位元組, 是否被截斷)。只讀檔尾 max_bytes。"""
    if max_bytes <= 0:
        raise SentinelError("max_bytes 必須為正數")
    size = path.stat().st_size
    length = min(size, max_bytes)
    with path.open("rb") as fh:
        fh.seek(size - length)
        data = fh.read(length)
    return data, size > length


def _usage_tokens(usage: object) -> int | None:
    """三個欄位加總；單一欄位缺少當 0，但三欄都缺（如 `{}`）視為量不到；型別不對（字串、布林、負數、小數）回 None。"""
    if not isinstance(usage, dict):
        return None
    if all(usage.get(key) is None for key in USAGE_KEYS):
        return None
    total = 0
    for key in USAGE_KEYS:
        value = usage.get(key, 0)
        if value is None:
            value = 0
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return None
        total += value
    return total


class ScanResult:
    def __init__(self, status: str, tokens: int | None, parsed_lines: int, bad_lines: int, bad_usage: int):
        self.status = status  # ok | no_usage | window_exhausted | corrupt
        self.tokens = tokens
        self.parsed_lines = parsed_lines
        self.bad_lines = bad_lines
        self.bad_usage = bad_usage

    def describe(self) -> str:
        return (f"status={self.status} tokens={self.tokens} parsed_lines={self.parsed_lines} "
                f"bad_lines={self.bad_lines} bad_usage={self.bad_usage}")


def scan_usage(data: bytes, truncated: bool) -> ScanResult:
    """反向找最後一筆 message.usage 合法的行。

    被截斷時第一段可能是半行，直接丟掉（原作靠 JSON.parse 失敗略過，結果相同，這裡明說）。
    """
    text = data.decode("utf-8", errors="replace")
    lines = text.split("\n")
    if truncated and lines:
        lines = lines[1:]
    parsed = bad = bad_usage = 0
    found: int | None = None
    for raw in reversed(lines):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except ValueError:
            bad += 1
            continue
        parsed += 1
        if not isinstance(obj, dict):
            continue
        message = obj.get("message")
        if not isinstance(message, dict) or "usage" not in message:
            continue
        tokens = _usage_tokens(message["usage"])
        if tokens is None:
            bad_usage += 1
            continue
        found = tokens
        break
    if found is not None:
        return ScanResult("ok", found, parsed, bad, bad_usage)
    if parsed == 0 and bad > 0:
        return ScanResult("corrupt", None, parsed, bad, bad_usage)
    if parsed == 0 and truncated:
        return ScanResult("window_exhausted", None, parsed, bad, bad_usage)
    return ScanResult("no_usage", None, parsed, bad, bad_usage)


def measure_file(path: Path, max_bytes: int = DEFAULT_TAIL_BYTES) -> ScanResult:
    try:
        data, truncated = read_tail(path, max_bytes)
    except FileNotFoundError:
        raise SentinelError(f"找不到 transcript：{path}") from None
    except OSError as exc:
        raise SentinelError(f"讀不了 transcript：{path}（{exc}）") from None
    return scan_usage(data, truncated)


# ---------------------------------------------------------------- 狀態機

def validate_thresholds(limit: int, step: int) -> None:
    for name, value in (("limit", limit), ("step", step)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise SentinelError(f"{name} 必須是正整數，收到 {value!r}")


def level_of(tokens: int, limit: int, step: int) -> int | None:
    validate_thresholds(limit, step)
    if tokens < limit:
        return None
    return (tokens - limit) // step


def decide(tokens: int, limit: int, step: int, last_level: int) -> tuple[str, int]:
    """回傳 (verdict, 新的 last_level)。last_level 初始為 -1。"""
    level = level_of(tokens, limit, step)
    if level is None:
        return "silent", last_level
    if level > last_level:
        return "notify", level
    return "inject", last_level


def simulate(readings: list[int], limit: int, step: int, last_level: int = -1) -> list[tuple[int, str, int]]:
    out = []
    for tokens in readings:
        verdict, last_level = decide(tokens, limit, step, last_level)
        out.append((tokens, verdict, last_level))
    return out


# ---------------------------------------------------------------- 語意啟發式

CONTINUE_ZH = ("繼續", "接著", "修正", "剛剛", "剛才", "上一步", "再改", "還有一個地方", "補一下")
NEW_ZH = ("新增", "換一個", "另外想要", "另外想", "全新", "新功能", "新模組", "換個話題")
CONTINUE_EN = ("continue", "keep going", "just now", "the previous", "fix that", "follow up")
NEW_EN = ("new feature", "another thing", "unrelated", "switch to", "different topic", "new module")
_NEGATION_BEFORE = ("不要", "不用", "別", "先不", "不")
_PASTE_BLOCK = re.compile(r'<pasted_content id="[^"]*">.*?</pasted_content id="[^"]*">', re.DOTALL)


def _count_hits(text: str, zh: tuple[str, ...], en: tuple[str, ...]) -> int:
    hits = 0
    for term in zh:
        start = 0
        while True:
            idx = text.find(term, start)
            if idx < 0:
                break
            before = text[max(0, idx - 2):idx]
            if not any(before.endswith(neg) for neg in _NEGATION_BEFORE):
                hits += 1
            start = idx + len(term)
    lowered = text.lower()
    for term in en:
        if re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lowered):
            hits += 1
    return hits


def classify_prompt(prompt: str) -> str:
    """continue / new_topic / ambiguous。兩邊都命中或都沒命中就是 ambiguous，不硬猜。"""
    if not isinstance(prompt, str) or not prompt.strip():
        raise SentinelError("提問是空的，無法判定")
    text = _PASTE_BLOCK.sub(" ", prompt)
    cont = _count_hits(text, CONTINUE_ZH, CONTINUE_EN)
    new = _count_hits(text, NEW_ZH, NEW_EN)
    if cont and not new:
        return "continue"
    if new and not cont:
        return "new_topic"
    return "ambiguous"


# ---------------------------------------------------------------- 會話名稱

def next_title(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise SentinelError("對話名稱是空的")
    name = name.strip()
    match = None
    for match in re.finditer(r"\d+", name):
        pass
    if match is None:
        return name + "-2"
    digits = match.group(0)
    bumped = str(int(digits) + 1).zfill(len(digits))
    return name[:match.start()] + bumped + name[match.end():]


# ---------------------------------------------------------------- 成本算術

def cumulative_input_tokens(context: int, growth: int, turns: int, baseline: int = 0) -> int:
    """第 k 輪送出的上下文 = context + growth*(k-1)，k=1..turns；總和 = turns*context + growth*turns*(turns-1)/2。"""
    for name, value in (("context", context), ("growth", growth), ("baseline", baseline)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SentinelError(f"{name} 必須是非負整數")
    if isinstance(turns, bool) or not isinstance(turns, int) or turns < 1:
        raise SentinelError("turns 必須是 >= 1 的整數")
    return turns * (baseline + context) + growth * turns * (turns - 1) // 2


# ---------------------------------------------------------------- hook

def hook_messages(tokens: int) -> tuple[str, str]:
    k = int(math.floor(tokens / 1000 + 0.5))
    user = f"這段對話已經很長了（約 {k}k tokens），每一輪都更耗 token。要做新功能時建議開新對話。"
    claude = (
        f"對話上下文已約 {k}k tokens。判斷使用者這則訊息是不是要開始新功能或新話題"
        "（不是接續目前做到一半的事、不是修正或追問）：是的話，先問使用者要不要開新對話並附上交接重點，"
        "不要直接開始做；是接續目前的事就照常做，不要提開新對話。"
    )
    return user, claude


def state_path(state_dir: Path, session_id: str) -> Path:
    if not isinstance(session_id, str) or not _SAFE_SESSION_ID.match(session_id):
        raise SentinelError("session_id 缺少或含不安全字元（只允許英數、底線、連字號，最長 128）")
    return state_dir / f"claude-long-chat-{session_id}.txt"


def read_state(path: Path) -> int:
    """狀態檔不存在 -> -1。內容壞掉 -> 當作 -1 並回報（狀態只是快取，自我修復；呼叫端會在 stderr 說明）。"""
    try:
        raw = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return -1
    except (OSError, UnicodeDecodeError):
        raise SentinelError(f"狀態檔讀不了：{path}") from None
    if re.fullmatch(r"-?\d{1,9}", raw):
        value = int(raw)
        if value >= -1:
            return value
    raise ValueError(raw)


def write_state(path: Path, level: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(str(level))
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def run_hook(stdin_bytes: bytes, limit: int, step: int, state_dir: Path, strict: bool,
             max_bytes: int = DEFAULT_TAIL_BYTES) -> tuple[int, str, str]:
    """回傳 (exit code, stdout, stderr)。純函式，方便測試。"""
    try:
        validate_thresholds(limit, step)
        try:
            payload = json.loads(stdin_bytes.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise SentinelError("stdin 不是合法的 UTF-8 JSON") from None
        if not isinstance(payload, dict):
            raise SentinelError("stdin 的 JSON 必須是物件")
        transcript = payload.get("transcript_path")
        if not isinstance(transcript, str) or not transcript.strip():
            raise SentinelError("stdin 缺少 transcript_path（字串）")
        spath = state_path(state_dir, payload.get("session_id"))
        try:
            scan = measure_file(Path(transcript), max_bytes)
        except SentinelError as exc:
            if strict:
                raise
            return 0, "", f"sentinel: 略過（{exc}）\n"
        if scan.status == "corrupt":
            raise SentinelError(f"transcript 整份無法解析（{scan.describe()}）")
        if scan.status != "ok":
            if strict:
                raise SentinelError(f"量不到 usage（{scan.describe()}）")
            return 0, "", f"sentinel: 略過，目前量不到 usage（{scan.describe()}）\n"
        note = ""
        try:
            last = read_state(spath)
        except ValueError:
            last = -1
            note = f"sentinel: 狀態檔內容壞掉，已重置：{spath}\n"
        verdict, new_last = decide(scan.tokens, limit, step, last)
        if verdict == "silent":
            return 0, "", note
        user, claude = hook_messages(scan.tokens)
        out: dict = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": claude}}
        if verdict == "notify":
            write_state(spath, new_last)
            out["systemMessage"] = user
        elif note:
            write_state(spath, last)
        return 0, json.dumps(out, ensure_ascii=True), note
    except SentinelError as exc:
        return 1, "", f"sentinel: {exc}\n"


# ---------------------------------------------------------------- CLI

def _positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"不是整數：{text!r}") from None
    if value <= 0:
        raise argparse.ArgumentTypeError(f"必須為正整數：{text!r}")
    return value


def _nonneg_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"不是整數：{text!r}") from None
    if value < 0:
        raise argparse.ArgumentTypeError(f"不可為負數：{text!r}")
    return value


def _int_list(text: str) -> list[int]:
    parts = [p.strip() for p in text.split(",")]
    if not parts or any(not p for p in parts):
        raise argparse.ArgumentTypeError("清單不可為空或含空項目")
    return [_nonneg_int(p) for p in parts]


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise SentinelError(f"環境變數 {name} 不是整數：{raw!r}") from None
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="長會話 Token 哨兵驗證工具（見模組說明）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def thresholds(p: argparse.ArgumentParser) -> None:
        p.add_argument("--limit", type=_positive_int, default=None, help=f"門檻 tokens（預設 {DEFAULT_LIMIT}）")
        p.add_argument("--step", type=_positive_int, default=None, help=f"提示步進 tokens（預設 {DEFAULT_STEP}）")

    p = sub.add_parser("check", help="量測 transcript 末端的 usage")
    p.add_argument("transcript")
    thresholds(p)
    p.add_argument("--last-level", type=int, default=-1)
    p.add_argument("--tail-bytes", type=_positive_int, default=DEFAULT_TAIL_BYTES)
    p.add_argument("--expect", choices=["silent", "inject", "notify"], help="不符就 exit 1")

    p = sub.add_parser("simulate", help="用假讀數跑狀態機")
    p.add_argument("--tokens", type=_int_list, required=True, help="逗號分隔的 token 讀數")
    thresholds(p)
    p.add_argument("--expect", help="逗號分隔的預期 verdict（silent/inject/notify），數量須相同")

    p = sub.add_parser("classify", help="延續 vs 新話題的啟發式判定")
    p.add_argument("prompt")
    p.add_argument("--expect", choices=["continue", "new_topic", "ambiguous"])

    p = sub.add_parser("title", help="算新對話名稱")
    p.add_argument("name")
    p.add_argument("--expect")

    p = sub.add_parser("cost", help="累計輸入 token 的純算術比較")
    p.add_argument("--context", type=_nonneg_int, required=True, help="目前上下文大小")
    p.add_argument("--growth", type=_nonneg_int, required=True, help="每輪平均增加量")
    p.add_argument("--turns", type=_positive_int, required=True, help="預計再進行幾輪")
    p.add_argument("--brief", type=_nonneg_int, required=True, help="交接 brief 大小")
    p.add_argument("--baseline", type=_nonneg_int, default=0, help="任何新對話都有的固定開銷（系統提示等），預設 0")

    p = sub.add_parser("hook", help="當 UserPromptSubmit command hook 用（讀 stdin）")
    thresholds(p)
    p.add_argument("--state-dir", default=None, help="狀態檔資料夾（預設系統暫存）")
    p.add_argument("--strict", action="store_true", help="量不到時也 exit 1")
    return parser


def _cmd_check(args: argparse.Namespace) -> int:
    limit = args.limit or _env_int("LONG_CHAT_TOKENS", DEFAULT_LIMIT)
    step = args.step or _env_int("LONG_CHAT_STEP", DEFAULT_STEP)
    validate_thresholds(limit, step)
    scan = measure_file(Path(args.transcript), args.tail_bytes)
    if scan.status != "ok":
        print(f"FAIL 量不到 usage：{scan.describe()}", file=sys.stderr)
        return 1
    verdict, _ = decide(scan.tokens, limit, step, args.last_level)
    print(f"tokens={scan.tokens} limit={limit} step={step} level={level_of(scan.tokens, limit, step)} verdict={verdict}")
    if args.expect and args.expect != verdict:
        print(f"FAIL 預期 {args.expect}，實際 {verdict}", file=sys.stderr)
        return 1
    return 0


def _cmd_simulate(args: argparse.Namespace) -> int:
    limit = args.limit or _env_int("LONG_CHAT_TOKENS", DEFAULT_LIMIT)
    step = args.step or _env_int("LONG_CHAT_STEP", DEFAULT_STEP)
    validate_thresholds(limit, step)
    rows = simulate(args.tokens, limit, step)
    expected = None
    if args.expect is not None:
        expected = [e.strip() for e in args.expect.split(",")]
        if len(expected) != len(rows):
            print(f"FAIL --expect 有 {len(expected)} 項，--tokens 有 {len(rows)} 項", file=sys.stderr)
            return 1
        bad_names = [e for e in expected if e not in ("silent", "inject", "notify")]
        if bad_names:
            print(f"FAIL 不認得的 verdict：{bad_names}", file=sys.stderr)
            return 1
    failed = 0
    for i, (tokens, verdict, last) in enumerate(rows):
        mark = ""
        if expected is not None and expected[i] != verdict:
            mark = f"  <-- 預期 {expected[i]}"
            failed += 1
        print(f"turn {i + 1}: tokens={tokens} verdict={verdict} last_level={last}{mark}")
    if failed:
        print(f"FAIL {failed} 輪與預期不符", file=sys.stderr)
        return 1
    return 0


def _cmd_cost(args: argparse.Namespace) -> int:
    stay = cumulative_input_tokens(args.context, args.growth, args.turns)
    switch = cumulative_input_tokens(args.brief, args.growth, args.turns, args.baseline)
    print(f"continue_total={stay} handoff_total={switch} saving={stay - switch} (raw input tokens, 未加權、未計價)")
    return 0


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    raw = list(sys.argv[1:] if argv is None else argv)
    try:
        args = build_parser().parse_args(raw)
    except SystemExit as exc:
        # hook 的參數錯誤不可回 2：UserPromptSubmit 的 exit 2 會擋掉使用者的每一則提問
        if raw and raw[0] == "hook" and exc.code not in (0, None):
            return 1
        raise
    try:
        if args.cmd == "check":
            return _cmd_check(args)
        if args.cmd == "simulate":
            return _cmd_simulate(args)
        if args.cmd == "classify":
            label = classify_prompt(args.prompt)
            print(label)
            if args.expect and args.expect != label:
                print(f"FAIL 預期 {args.expect}，實際 {label}", file=sys.stderr)
                return 1
            return 0
        if args.cmd == "title":
            title = next_title(args.name)
            print(title)
            if args.expect is not None and args.expect != title:
                print(f"FAIL 預期 {args.expect!r}，實際 {title!r}", file=sys.stderr)
                return 1
            return 0
        if args.cmd == "cost":
            return _cmd_cost(args)
        if args.cmd == "hook":
            limit = args.limit or _env_int("LONG_CHAT_TOKENS", DEFAULT_LIMIT)
            step = args.step or _env_int("LONG_CHAT_STEP", DEFAULT_STEP)
            state_dir = Path(args.state_dir) if args.state_dir else Path(tempfile.gettempdir())
            code, out, err = run_hook(sys.stdin.buffer.read(), limit, step, state_dir, args.strict)
            if out:
                sys.stdout.write(out)
            if err:
                sys.stderr.write(err)
            return code
    except SentinelError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
