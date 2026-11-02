#!/usr/bin/env python3
"""Agent 工具呼叫頻率審查與 Deny-list 建議工具 (audit_agent_tool_pruning.py)

規範：docs/token-economizer-cost-control-spec.md（第 5 節）

輸入：一或多個 Claude Code 會話紀錄（transcript JSONL，一個檔案算一個 session），
      外加可選的「工具目錄」JSON（--catalog：{"工具名": schema_token 數或 null}）。
輸出：每個工具的呼叫次數、每個 prompt 的呼叫率、呼叫輸入的 token 估算占比；
      有目錄時另外給出建議的 permissions.deny（裸工具名規則，Claude Code 官方語法，
      生效後工具定義整個從 context 移除），以及預估省下的 schema token。

為什麼需要目錄：transcript 只記錄「被呼叫過的工具」，不記錄「session 載入了哪些工具」，
所以光看 transcript 無法知道哪些工具從沒被呼叫。沒有目錄時只輸出統計，不產生 deny-list。

建議規則（取自 microsoft/TokenEconomizer 的外掛預設，數字是借用其設定的預設值，
不是本 repo 的量測；詳見規範第 5 節）：
  1. 工具在整批紀錄裡一次都沒被呼叫過（用過就不建議，哪怕只用一次）。
  2. 證據量足夠：總 prompt 數 >= --min-prompts 且有 prompt 的 session 數 >= --min-sessions，
     或有 prompt 的 session 數 >= --fallback-sessions。
  3. 基本工作面工具與人類互動工具（PROTECTED_TOOLS）永遠不建議；NotebookEdit 的證據門檻乘 3。

結束碼：0 完成（含「沒有任何建議」）；2 輸入有問題（空檔、壞 JSON、缺欄位、沒有任何 prompt、
目錄格式錯、參數錯）。量不到的情況一律回 2，不會假裝通過。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---- 本 repo 的取捨（具名參數；預設值借自 TokenEconomizer README 的 Settings 表，非本 repo 量測）----
DEFAULT_MIN_PROMPTS = 10  # TokenEconomizer: toolprune_evidence (p)
DEFAULT_MIN_SESSIONS = 2  # TokenEconomizer: toolprune_min_sessions (m)
DEFAULT_FALLBACK_SESSIONS = 5  # TokenEconomizer: toolprune_sessions (s)
DEFAULT_CHARS_PER_TOKEN = 4.0  # 呼叫輸入的 token 估算：字元數 / 4，啟發式，不是 tokenizer 實測

# 永遠不建議 deny 的工具。內容來自 TokenEconomizer 的 tools.PROTECTED_TOOLS（Claude Code 命名）
# 與其 docs/PLUGIN.md 第 2 節「a person's tools — AskUserQuestion, plan mode, sub-agents, the web」。
# 這是本 repo 的保守選擇：寧可少建議，也不要讓人類少了提問、規劃、委派的能力。
PROTECTED_TOOLS = {
    "Bash": "基本工作面（shell）",
    "Edit": "基本工作面（編輯）",
    "MultiEdit": "基本工作面（編輯）",
    "Write": "基本工作面（寫檔）",
    "Read": "基本工作面（讀檔）",
    "Grep": "基本工作面（搜尋）",
    "Glob": "基本工作面（搜尋）",
    "AskUserQuestion": "人類互動工具：真人會用它回答問題",
    "EnterPlanMode": "人類互動工具：規劃模式",
    "ExitPlanMode": "人類互動工具：規劃模式",
    "Agent": "委派子 agent，真人 session 常用",
    "WebFetch": "網路工具：真人 session 的工作常需要上網",
    "WebSearch": "網路工具：真人 session 的工作常需要上網",
}
# 證據門檻倍率：TokenEconomizer 對 NotebookEdit 要求三倍證據。
EVIDENCE_MULTIPLIER = {"NotebookEdit": 3}

# permissions.deny 的裸工具名：官方語法 Tool 或 Tool(specifier)；括號、* 會變成別的意思，
# 所以目錄裡的名字只准英數、底線、連字號（MCP 工具形如 mcp__server__tool）。
TOOL_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*$")


class InputError(Exception):
    """輸入有問題，CLI 轉成結束碼 2。"""


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- 解析


def _is_prompt(ev: dict) -> bool:
    """是不是「人給的 prompt」。規則對照 TokenEconomizer trace/claude.py 的 _is_prompt（commit 85a8247）：
    user 條目，扣掉 tool_result、meta、子 agent（sidechain）、壓縮摘要、本地指令輸出與中斷標記。"""
    if ev.get("type") != "user" or ev.get("isMeta") or ev.get("isSidechain") or ev.get("isCompactSummary"):
        return False
    content = ev["message"]["content"]
    if isinstance(content, list):
        blocks = [b for b in content if isinstance(b, dict)]
        if any(b.get("type") == "tool_result" for b in blocks):
            return False
        content = " ".join(b.get("text") or "" for b in blocks if b.get("type") == "text")
    return isinstance(content, str) and content.strip() != "" and not content.startswith(
        ("<local-command", "[Request interrupted")
    )


def parse_transcript(path: Path) -> dict:
    """解析一個 transcript，回傳 {"prompts", "requests", "calls": {name: n}, "input_chars": {name: n}}。
    任何格式問題都丟 InputError（帶檔名與行號）。"""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise InputError(f"讀不到檔案 {path}：{exc}") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"{path} 不是合法 UTF-8：{exc}") from exc
    if not text.strip():
        raise InputError(f"{path} 是空檔")

    prompts = 0
    request_ids: set[str] = set()
    anonymous_requests = 0
    seen_tool_ids: set[str] = set()
    calls: dict[str, int] = {}
    input_chars: dict[str, int] = {}
    entries = 0

    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        where = f"{path}:{lineno}"
        try:
            ev = json.loads(line)
        except ValueError as exc:
            raise InputError(f"{where} 不是合法 JSON：{exc}") from exc
        if not isinstance(ev, dict):
            raise InputError(f"{where} 不是 JSON 物件")
        etype = ev.get("type")
        if not isinstance(etype, str) or not etype:
            raise InputError(f"{where} 缺少字串欄位 type")
        entries += 1
        # 只有 assistant / user 條目帶對話內容；其他（summary、system、api-request-blob 等）
        # 會重複早先的呼叫，TokenEconomizer 也只讀這兩種，否則每個呼叫會算兩次。
        if etype not in ("assistant", "user"):
            continue
        msg = ev.get("message")
        if not isinstance(msg, dict) or "content" not in msg:
            raise InputError(f"{where} 的 {etype} 條目缺少 message.content")
        content = msg["content"]
        if not isinstance(content, (str, list)):
            raise InputError(f"{where} 的 message.content 必須是字串或陣列")
        if etype == "user" and _is_prompt(ev):
            prompts += 1
        if etype != "assistant":
            continue
        mid = msg.get("id")
        if isinstance(mid, str) and mid:
            request_ids.add(mid)
        else:
            anonymous_requests += 1
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            name = block.get("name")
            if not isinstance(name, str) or not name.strip():
                raise InputError(f"{where} 的 tool_use 缺少字串欄位 name")
            tid = block.get("id")
            if isinstance(tid, str) and tid:
                if tid in seen_tool_ids:  # 互動 transcript 一個 content block 一個條目，id 會重複
                    continue
                seen_tool_ids.add(tid)
            calls[name] = calls.get(name, 0) + 1
            try:
                chars = len(json.dumps(block.get("input", {}), ensure_ascii=False, sort_keys=True))
            except (TypeError, ValueError) as exc:
                raise InputError(f"{where} 的 tool_use.input 無法序列化：{exc}") from exc
            input_chars[name] = input_chars.get(name, 0) + chars

    if entries == 0:
        raise InputError(f"{path} 沒有任何 JSON 條目")
    return {
        "prompts": prompts,
        "requests": len(request_ids) + anonymous_requests,
        "calls": calls,
        "input_chars": input_chars,
    }


def load_catalog(path: Path) -> dict[str, int | None]:
    """工具目錄：JSON 物件 {"工具名": schema token 整數 >= 0 或 null（未量測）}。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise InputError(f"讀不到目錄 {path}：{exc}") from exc
    except ValueError as exc:
        raise InputError(f"目錄 {path} 不是合法 JSON：{exc}") from exc
    if not isinstance(data, dict) or not data:
        raise InputError(f"目錄 {path} 必須是非空的 JSON 物件 {{工具名: schema_tokens|null}}")
    out: dict[str, int | None] = {}
    for name, tokens in data.items():
        if not TOOL_NAME_RE.match(name):
            raise InputError(
                f"目錄裡的工具名 {name!r} 不能當裸 deny 規則（只准英數、底線、連字號；括號與 * 在 "
                "permissions.deny 裡有別的意思）"
            )
        if tokens is not None and (isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0):
            raise InputError(f"目錄裡 {name} 的 schema token 必須是 >= 0 的整數或 null，拿到 {tokens!r}")
        out[name] = tokens
    return out


# --------------------------------------------------------------------------- 分析


def analyze(
    sessions: list[dict],
    catalog: dict[str, int | None] | None = None,
    *,
    min_prompts: int = DEFAULT_MIN_PROMPTS,
    min_sessions: int = DEFAULT_MIN_SESSIONS,
    fallback_sessions: int = DEFAULT_FALLBACK_SESSIONS,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
) -> dict:
    """彙整統計並產生 deny 建議。sessions 是 parse_transcript 的輸出列表。沒有任何 prompt 就丟 InputError。"""
    for label, value in (("min_prompts", min_prompts), ("min_sessions", min_sessions),
                         ("fallback_sessions", fallback_sessions)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise InputError(f"{label} 必須是 >= 1 的整數")
    if not isinstance(chars_per_token, (int, float)) or isinstance(chars_per_token, bool) or chars_per_token <= 0:
        raise InputError("chars_per_token 必須 > 0")
    if not sessions:
        raise InputError("沒有任何 session")

    total_prompts = sum(s["prompts"] for s in sessions)
    if total_prompts == 0:
        raise InputError("所有 session 加起來沒有任何 prompt，無從判斷工具有沒有被用到")
    sessions_with_prompts = sum(1 for s in sessions if s["prompts"] > 0)
    total_requests = sum(s["requests"] for s in sessions)

    names = set()
    for s in sessions:
        names.update(s["calls"])
    total_calls = sum(sum(s["calls"].values()) for s in sessions)
    total_input_tokens = 0.0
    per_tool: dict[str, dict] = {}
    for name in names:
        calls = sum(s["calls"].get(name, 0) for s in sessions)
        used_in = sum(1 for s in sessions if s["calls"].get(name, 0) > 0)
        est = sum(s["input_chars"].get(name, 0) for s in sessions) / chars_per_token
        total_input_tokens += est
        per_tool[name] = {"name": name, "calls": calls, "sessions_used": used_in,
                          "input_tokens_est": est}
    # 目錄裡有、transcript 沒出現的工具：呼叫 0 次
    for name in (catalog or {}):
        per_tool.setdefault(name, {"name": name, "calls": 0, "sessions_used": 0, "input_tokens_est": 0.0})

    catalog_total = None
    if catalog is not None:
        known = [v for v in catalog.values() if v is not None]
        catalog_total = sum(known) if known else None

    tools = []
    for name, t in per_tool.items():
        row = {
            "name": name,
            "calls": t["calls"],
            "sessions_used": t["sessions_used"],
            "calls_per_prompt": round(t["calls"] / total_prompts, 4),
            "call_share": round(t["calls"] / total_calls, 4) if total_calls else 0.0,
            "input_tokens_est": round(t["input_tokens_est"], 1),
            "input_token_share": round(t["input_tokens_est"] / total_input_tokens, 4)
            if total_input_tokens else 0.0,
            "in_catalog": catalog is not None and name in catalog,
            "schema_tokens": (catalog or {}).get(name),
            "schema_share": None,
        }
        if catalog is not None and row["schema_tokens"] is not None and catalog_total:
            row["schema_share"] = round(row["schema_tokens"] / catalog_total, 4)
        tools.append(row)
    tools.sort(key=lambda r: (-r["calls"], r["name"]))

    result = {
        "params": {"min_prompts": min_prompts, "min_sessions": min_sessions,
                   "fallback_sessions": fallback_sessions, "chars_per_token": chars_per_token},
        "sessions": len(sessions),
        "sessions_with_prompts": sessions_with_prompts,
        "prompts": total_prompts,
        "requests": total_requests,
        "tool_calls": total_calls,
        "tools": tools,
        "used_but_not_in_catalog": sorted(n for n, t in per_tool.items()
                                          if catalog is not None and t["calls"] > 0 and n not in catalog),
    }

    deny = {"status": "no-catalog", "rules": [], "skipped": [], "expected_savings": None}
    if catalog is not None:
        rules, skipped = [], []
        for name in sorted(catalog):
            if per_tool[name]["calls"] > 0:
                continue  # 用過就不建議
            if name in PROTECTED_TOOLS:
                skipped.append({"tool": name, "reason": f"受保護，不建議 deny：{PROTECTED_TOOLS[name]}"})
                continue
            mult = EVIDENCE_MULTIPLIER.get(name, 1)
            need_prompts, need_fallback = min_prompts * mult, fallback_sessions * mult
            enough = ((total_prompts >= need_prompts and sessions_with_prompts >= min_sessions)
                      or sessions_with_prompts >= need_fallback)
            if not enough:
                skipped.append({
                    "tool": name,
                    "reason": (f"證據不足：{total_prompts} 個 prompt / {sessions_with_prompts} 個 session，"
                               f"需要 >= {need_prompts} 個 prompt 且 >= {min_sessions} 個 session，"
                               f"或 >= {need_fallback} 個 session"),
                })
                continue
            rules.append(name)
        deny["rules"] = rules
        deny["skipped"] = skipped
        if rules:
            deny["status"] = "ok"
            known = [catalog[r] for r in rules if catalog[r] is not None]
            unmeasured = [r for r in rules if catalog[r] is None]
            per_request = sum(known)
            deny["expected_savings"] = {
                "schema_tokens_per_request": per_request,
                "requests_in_window": total_requests,
                "tokens_if_denied_during_window": per_request * total_requests,
                "unmeasured_tools": unmeasured,
                "note": "上限估計：每次 API 請求都會重送工具定義；未計快取折扣，也未計該窗口之後的 session。"
                        + (" 有工具沒有 schema token 量測值，這些沒算進去。" if unmeasured else ""),
            }
        else:
            deny["status"] = "none"
    result["deny"] = deny
    result["permissions"] = {"deny": list(deny["rules"])}
    return result


# --------------------------------------------------------------------------- 輸出


def render_text(res: dict) -> str:
    p = res["params"]
    lines = [
        "# Agent 工具呼叫頻率審查",
        f"session：{res['sessions']}（有 prompt 的 {res['sessions_with_prompts']}）｜prompt：{res['prompts']}"
        f"｜API 請求：{res['requests']}｜工具呼叫：{res['tool_calls']}",
        f"門檻（本 repo 取捨，預設借自 TokenEconomizer）：min_prompts={p['min_prompts']}、"
        f"min_sessions={p['min_sessions']}、fallback_sessions={p['fallback_sessions']}",
        "",
        "| 工具 | 呼叫 | 用到的 session | 每 prompt 呼叫 | 呼叫輸入 token 估算占比 | schema tokens |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for t in res["tools"]:
        schema = "-" if t["schema_tokens"] is None else str(t["schema_tokens"])
        lines.append(f"| {t['name']} | {t['calls']} | {t['sessions_used']} | {t['calls_per_prompt']:.2f} "
                     f"| {t['input_token_share'] * 100:.1f}% | {schema} |")
    d = res["deny"]
    lines.append("")
    if d["status"] == "no-catalog":
        lines.append("deny-list：未產生。沒有給 --catalog，transcript 無法告訴我們 session 載入了哪些工具。")
    elif d["status"] == "none":
        lines.append("deny-list：沒有建議的規則。")
    else:
        lines.append("建議的 permissions.deny：")
        for r in d["rules"]:
            lines.append(f"  - {r}")
        s = d["expected_savings"]
        lines.append(f"預估：每次請求省 {s['schema_tokens_per_request']} schema tokens；"
                     f"窗口內 {s['requests_in_window']} 次請求，若當時已 deny 約省 "
                     f"{s['tokens_if_denied_during_window']} tokens。{s['note']}")
    for sk in d["skipped"]:
        lines.append(f"  略過 {sk['tool']}：{sk['reason']}")
    if res["used_but_not_in_catalog"]:
        lines.append("警告：transcript 用到、但不在目錄裡的工具（目錄可能過期）："
                     + "、".join(res["used_but_not_in_catalog"]))
    return "\n".join(lines)


# --------------------------------------------------------------------------- CLI


def _positive_int(s: str) -> int:
    try:
        v = int(s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"需要整數，拿到 {s!r}") from exc
    if v < 1:
        raise argparse.ArgumentTypeError("必須 >= 1")
    return v


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="審查 Agent 工具呼叫頻率並建議 permissions.deny（唯讀）。")
    ap.add_argument("transcripts", nargs="+", help="Claude Code transcript JSONL；一個檔案算一個 session")
    ap.add_argument("--catalog", help='工具目錄 JSON：{"工具名": schema_tokens 或 null}')
    ap.add_argument("--min-prompts", type=_positive_int, default=DEFAULT_MIN_PROMPTS)
    ap.add_argument("--min-sessions", type=_positive_int, default=DEFAULT_MIN_SESSIONS)
    ap.add_argument("--fallback-sessions", type=_positive_int, default=DEFAULT_FALLBACK_SESSIONS)
    ap.add_argument("--json", action="store_true", help="輸出完整 JSON（含 permissions.deny 片段）")
    ap.add_argument("--deny-out", help="把 {\"permissions\": {\"deny\": [...]}} 片段寫到這個檔案（不會改既有設定）")
    return ap


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    # argparse 的用法錯誤本來就是結束碼 2
    args = build_parser().parse_args(argv)
    try:
        sessions = [parse_transcript(Path(p)) for p in args.transcripts]
        catalog = load_catalog(Path(args.catalog)) if args.catalog else None
        res = analyze(sessions, catalog, min_prompts=args.min_prompts, min_sessions=args.min_sessions,
                      fallback_sessions=args.fallback_sessions)
        if args.deny_out:
            if res["deny"]["status"] != "ok":
                raise InputError(f"沒有可寫的 deny 規則（狀態：{res['deny']['status']}），不寫 --deny-out")
            Path(args.deny_out).write_text(
                json.dumps({"permissions": res["permissions"]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
    except InputError as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_text(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
