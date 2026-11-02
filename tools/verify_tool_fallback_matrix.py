#!/usr/bin/env python3
"""
tools/verify_tool_fallback_matrix.py
檢查「產出導向工具流矩陣」設定檔（JSON）：五條產出路徑都要有主力與合格備援，
備援引用不能打錯鍵名而靜默失效，閘道白名單只能用不可變的數字 ID，
外發與付款的工具必須帶人類確認旗標。唯讀，不改任何檔案、不執行設定檔裡的任何指令。

這是「本 repo 自訂的設定格式」（見 docs/multi-agent-parallel-dispatch-spec.md 第 7 節），
不是 Hermes、Claude Code 或任何產品的原生設定檔；用它檢查別的格式要先轉成這個格式。
需要範例：python tools/verify_tool_fallback_matrix.py --print-example

檢查項目（全部是 ERROR；沒有「警告就放過」這一級）：
    file-*          檔案不存在／不是 UTF-8／不是 JSON／頂層不是物件／內容是空物件
    duplicate-key   JSON 同一層出現重複鍵（後者會悄悄蓋掉前者）
    unknown-key     出現規格之外的鍵（常見成因：fallbacks 打成 fallback／fallbak，會附 did-you-mean 建議）
    missing-key     缺必填鍵
    bad-type        型別不對（含 requires_human_confirm 必須是 JSON true，字串 "true" 不算）
    road-missing    五條路徑（video、image、code、document、dispatcher）少任何一條
    no-fallback     路徑沒有備援，或備援清單是空的
    dangling-ref    primary／fallbacks 引用了 tools 裡沒有定義的工具（備援永遠切不過去）
    self-fallback   備援與主力是同一個工具，或備援清單內重複
    same-provider   所有備援與主力同一個 provider（同一個故障面；本 repo 的取捨，不是外部標準）
    no-healthcheck  主力或備援工具沒有 healthcheck 說明（只檢查有寫，不會執行）
    tool-disabled   備援工具被標為 enabled=false
    gateway-id      白名單用了使用者名稱、@handle、萬用字元、空白名單，或不是純數字字串 ID
    confirm-missing 外發或付款的工具沒有 requires_human_confirm: true
    side-effect-lie 工具標 side_effect=none，但 id／description 含外發或付款字眼

用法：
    python tools/verify_tool_fallback_matrix.py <設定檔.json> [--json]
    python tools/verify_tool_fallback_matrix.py --print-example
結束碼：0 通過；1 有 ERROR；2 用法錯誤（沒給檔、讀不到檔、不是合法 JSON、不是物件）。
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REQUIRED_ROADS = ("video", "image", "code", "document", "dispatcher")
SIDE_EFFECTS = ("none", "external_send", "payment")
CONFIRM_REQUIRED = ("external_send", "payment")

TOP_KEYS = {"version", "tools", "roads", "gateways"}
TOOL_KEYS = {"provider", "side_effect", "requires_human_confirm", "healthcheck", "enabled", "description"}
TOOL_REQUIRED = ("provider", "side_effect", "requires_human_confirm")
ROAD_KEYS = {"label", "primary", "fallbacks"}
GATEWAY_KEYS = {"name", "allowlist"}
ENTRY_KEYS = {"user_id", "note"}

# 本 repo 的取捨：Discord／Telegram 等平台的使用者 ID 都是純數字；寬度 5~25 是刻意放寬的範圍，不是平台規格。
USER_ID_RE = re.compile(r"^[0-9]{5,25}$")
# side_effect=none 卻出現這些字眼，多半是標錯。只看 id 與 description，不看 healthcheck。
RISKY_WORDS = re.compile(
    r"(?<![a-z])(send(s|er|ing)?|post(s|ing)?|publish(es|er|ing)?|tweet|broadcast|e?mail(er|ing)?|sms|notify|"
    r"pay(s|ment|ments|ing)?|charge|billing|invoice|checkout)(?![a-z])|發送|寄出|發佈|發布|推播|群發|付款|扣款|收款|刷卡|結帳",
    re.IGNORECASE,
)


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


class Finding:
    def __init__(self, code: str, path: str, msg: str):
        self.code, self.path, self.msg = code, path, msg

    def as_dict(self) -> dict:
        return {"level": "ERROR", "code": self.code, "path": self.path, "message": self.msg}

    def __str__(self) -> str:
        return f"ERROR {self.code:16} {self.path}  {self.msg}"


class DuplicateKeyError(ValueError):
    pass


def _no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    seen: dict[str, object] = {}
    for key, value in pairs:
        if key in seen:
            raise DuplicateKeyError(key)
        seen[key] = value
    return seen


def load_config(text: str):
    """回傳 (資料, 重複鍵或 None)。重複鍵時資料用一般解析（讓其他檢查仍能跑）。"""
    try:
        return json.loads(text, object_pairs_hook=_no_duplicates), None
    except DuplicateKeyError as e:
        return json.loads(text), str(e)


def _suggest(key: str, allowed: set[str]) -> str:
    hit = difflib.get_close_matches(key, sorted(allowed), n=1, cutoff=0.6)
    return f"，你是不是要寫 {hit[0]}？" if hit else f"，合法的鍵：{', '.join(sorted(allowed))}"


def _check_keys(obj: dict, allowed: set[str], required: tuple[str, ...], path: str, out: list[Finding]) -> None:
    for key in obj:
        if key not in allowed:
            out.append(Finding("unknown-key", f"{path}.{key}" if path else key, f"規格之外的鍵{_suggest(key, allowed)}"))
    for key in required:
        if key not in obj:
            out.append(Finding("missing-key", f"{path}.{key}" if path else key, "缺必填鍵"))


def _is_str_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value)


def _check_tools(tools, out: list[Finding]) -> dict[str, dict]:
    good: dict[str, dict] = {}
    if not isinstance(tools, dict) or not tools:
        out.append(Finding("bad-type", "tools", "tools 必須是非空物件（工具 id -> 設定）"))
        return good
    for tid, tool in tools.items():
        path = f"tools.{tid}"
        if not isinstance(tool, dict):
            out.append(Finding("bad-type", path, "工具設定必須是物件"))
            continue
        _check_keys(tool, TOOL_KEYS, TOOL_REQUIRED, path, out)
        good[tid] = tool
        provider = tool.get("provider")
        if "provider" in tool and (not isinstance(provider, str) or not provider.strip()):
            out.append(Finding("bad-type", f"{path}.provider", "provider 必須是非空字串"))
        side = tool.get("side_effect")
        if "side_effect" in tool and side not in SIDE_EFFECTS:
            out.append(Finding("bad-type", f"{path}.side_effect", f"side_effect 必須是 {'／'.join(SIDE_EFFECTS)} 其中之一，收到 {side!r}"))
        confirm = tool.get("requires_human_confirm")
        if "requires_human_confirm" in tool and not isinstance(confirm, bool):
            out.append(Finding("bad-type", f"{path}.requires_human_confirm", f"必須是 JSON true/false，收到 {confirm!r}"))
        if side in CONFIRM_REQUIRED and confirm is not True:
            out.append(Finding("confirm-missing", path, f"side_effect={side} 的工具必須 requires_human_confirm: true"))
        if side == "none":
            text = f"{tid} {tool.get('description', '') if isinstance(tool.get('description'), str) else ''}"
            hit = RISKY_WORDS.search(text)
            if hit:
                out.append(Finding("side-effect-lie", path, f"標為 side_effect=none，但 id／description 含「{hit.group(0)}」；請改成實際的 side_effect"))
        if "enabled" in tool and not isinstance(tool["enabled"], bool):
            out.append(Finding("bad-type", f"{path}.enabled", "enabled 必須是 JSON true/false"))
        if "healthcheck" in tool and not (isinstance(tool["healthcheck"], str) and tool["healthcheck"].strip()):
            out.append(Finding("bad-type", f"{path}.healthcheck", "healthcheck 必須是非空字串（寫明怎麼確認它還活著）"))
    return good


def _needs_healthcheck(tid: str, tools: dict[str, dict], path: str, out: list[Finding]) -> None:
    tool = tools.get(tid)
    if tool is not None and "healthcheck" not in tool:
        out.append(Finding("no-healthcheck", path, f"{tid} 被當主力或備援使用，卻沒有 healthcheck"))


def _check_roads(roads, tools: dict[str, dict], out: list[Finding]) -> None:
    if not isinstance(roads, dict) or not roads:
        out.append(Finding("bad-type", "roads", "roads 必須是非空物件（路徑 id -> 設定）"))
        return
    for rid in REQUIRED_ROADS:
        if rid not in roads:
            out.append(Finding("road-missing", f"roads.{rid}", f"缺少必備的產出路徑 {rid}"))
    for rid, road in roads.items():
        path = f"roads.{rid}"
        if not isinstance(road, dict):
            out.append(Finding("bad-type", path, "路徑設定必須是物件"))
            continue
        _check_keys(road, ROAD_KEYS, ("primary", "fallbacks"), path, out)
        primary, fallbacks = road.get("primary"), road.get("fallbacks")
        if "primary" in road and not (_is_str_list(primary) and primary):
            out.append(Finding("bad-type", f"{path}.primary", "primary 必須是非空的工具 id 清單"))
            primary = None
        if "fallbacks" in road:
            if not _is_str_list(fallbacks):
                out.append(Finding("bad-type", f"{path}.fallbacks", "fallbacks 必須是工具 id 清單"))
                fallbacks = None
            elif not fallbacks:
                out.append(Finding("no-fallback", f"{path}.fallbacks", "備援清單是空的，主力掛掉時沒有退路"))
        elif "primary" in road:
            out.append(Finding("no-fallback", path, "沒有可用的 fallbacks 鍵，主力掛掉時沒有退路"))
        for field, ids in (("primary", primary), ("fallbacks", fallbacks)):
            for tid in ids or []:
                if tid not in tools:
                    out.append(Finding("dangling-ref", f"{path}.{field}", f"引用了 tools 裡沒有定義的 {tid}"))
                else:
                    _needs_healthcheck(tid, tools, f"{path}.{field}", out)
        if primary and fallbacks:
            if len(set(fallbacks)) != len(fallbacks):
                out.append(Finding("self-fallback", f"{path}.fallbacks", "備援清單內有重複的工具"))
            for tid in fallbacks:
                if tid in primary:
                    out.append(Finding("self-fallback", f"{path}.fallbacks", f"{tid} 同時是主力與備援，等於沒有備援"))
                if isinstance(tools.get(tid), dict) and tools[tid].get("enabled") is False:
                    out.append(Finding("tool-disabled", f"{path}.fallbacks", f"備援 {tid} 被標為 enabled=false"))
            prim_providers = {tools[t].get("provider") for t in primary if t in tools and isinstance(tools[t], dict)}
            fb_providers = {tools[t].get("provider") for t in fallbacks if t in tools and isinstance(tools[t], dict)}
            if prim_providers and fb_providers and fb_providers <= prim_providers:
                out.append(Finding("same-provider", f"{path}.fallbacks", f"所有備援都和主力同一個 provider（{', '.join(sorted(map(str, prim_providers)))}），同一個故障面一起掛"))


def _check_gateways(gateways, out: list[Finding]) -> None:
    if not isinstance(gateways, list) or not gateways:
        out.append(Finding("bad-type", "gateways", "gateways 必須是非空清單（至少宣告一個閘道）"))
        return
    for i, gw in enumerate(gateways):
        path = f"gateways[{i}]"
        if not isinstance(gw, dict):
            out.append(Finding("bad-type", path, "閘道設定必須是物件"))
            continue
        _check_keys(gw, GATEWAY_KEYS, ("name", "allowlist"), path, out)
        allow = gw.get("allowlist")
        if "allowlist" not in gw:
            continue
        if not isinstance(allow, list):
            out.append(Finding("bad-type", f"{path}.allowlist", "allowlist 必須是清單"))
            continue
        if not allow:
            out.append(Finding("gateway-id", f"{path}.allowlist", "白名單是空的：不是沒人能進，就是設定沒生效，兩者都不該通過"))
        for j, entry in enumerate(allow):
            epath = f"{path}.allowlist[{j}]"
            if not isinstance(entry, dict):
                out.append(Finding("gateway-id", epath, f"白名單項目必須是 {{\"user_id\": \"數字字串\"}}，收到 {entry!r}（不接受裸字串或使用者名稱）"))
                continue
            for key in entry:
                if key not in ENTRY_KEYS:
                    out.append(Finding("gateway-id", f"{epath}.{key}", f"白名單不可用 {key} 識別身分（改名就失聯、也可能被他人搶註），只能用 user_id"))
            uid = entry.get("user_id")
            if "user_id" not in entry:
                out.append(Finding("gateway-id", epath, "缺 user_id"))
            elif not isinstance(uid, str) or not USER_ID_RE.match(uid):
                out.append(Finding("gateway-id", f"{epath}.user_id", f"user_id 必須是 5~25 位純數字的『字串』，收到 {uid!r}"))


def check(data) -> list[Finding]:
    out: list[Finding] = []
    if not isinstance(data, dict):
        return [Finding("bad-type", "$", "頂層必須是 JSON 物件")]
    if not data:
        return [Finding("file-empty", "$", "設定是空物件，沒有任何東西可檢查，不算通過")]
    _check_keys(data, TOP_KEYS, ("tools", "roads", "gateways"), "", out)
    tools = _check_tools(data.get("tools"), out) if "tools" in data else {}
    if "roads" in data:
        _check_roads(data["roads"], tools, out)
    if "gateways" in data:
        _check_gateways(data["gateways"], out)
    return out


EXAMPLE = {
    "version": 1,
    "tools": {
        "url-to-video": {"provider": "claude-code", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "跑一次 1 秒測試片並確認輸出檔存在"},
        "heygen": {"provider": "heygen", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "查詢帳號額度 API 回 200"},
        "gemini-image": {"provider": "google", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "生成 1 張測試圖"},
        "canva-template": {"provider": "canva", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "開啟模板頁面不報錯"},
        "claude-code": {"provider": "anthropic", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "claude --version 回傳 0"},
        "vercel-preview": {"provider": "vercel", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "vercel whoami 回傳 0"},
        "whisper-local": {"provider": "local", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "轉寫 3 秒測試音檔"},
        "notion-page": {"provider": "notion", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "讀取測試頁面回 200"},
        "hermes-discord": {"provider": "google", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "對測試頻道回 ping"},
        "chatgpt-fallback": {"provider": "openai", "side_effect": "none", "requires_human_confirm": False, "healthcheck": "送一句 ping 回應非空"},
        "line-send": {"provider": "line", "side_effect": "external_send", "requires_human_confirm": True, "healthcheck": "只呼叫 dry-run 端點"},
    },
    "roads": {
        "video": {"label": "做影片", "primary": ["url-to-video"], "fallbacks": ["heygen"]},
        "image": {"label": "做圖像", "primary": ["gemini-image"], "fallbacks": ["canva-template"]},
        "code": {"label": "做程式", "primary": ["claude-code"], "fallbacks": ["vercel-preview"]},
        "document": {"label": "整理文", "primary": ["claude-code"], "fallbacks": ["whisper-local", "notion-page"]},
        "dispatcher": {"label": "調度員", "primary": ["hermes-discord"], "fallbacks": ["chatgpt-fallback"]},
    },
    "gateways": [{"name": "discord", "allowlist": [{"user_id": "123456789012345678", "note": "維護者本人（範例數字）"}]}],
}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="檢查產出導向工具流矩陣設定檔（JSON，唯讀）。")
    ap.add_argument("config", nargs="?", help="設定檔路徑（JSON）")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    ap.add_argument("--print-example", action="store_true", help="印出一份會通過的範例設定後結束")
    return ap


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    args = build_parser().parse_args(argv)
    if args.print_example:
        print(json.dumps(EXAMPLE, ensure_ascii=False, indent=2))
        return 0
    if not args.config:
        print("錯誤：沒有指定設定檔（沒有輸入不會算通過）。用法：verify_tool_fallback_matrix.py <設定檔.json>", file=sys.stderr)
        return 2
    path = Path(args.config)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"錯誤：找不到檔案：{path}", file=sys.stderr)
        return 2
    except (UnicodeDecodeError, OSError) as e:
        print(f"錯誤：讀不到 {path}（{type(e).__name__}）", file=sys.stderr)
        return 2
    try:
        data, dup = load_config(text)
    except json.JSONDecodeError as e:
        print(f"錯誤：不是合法 JSON：{e}", file=sys.stderr)
        return 2
    findings = check(data)
    if dup is not None:
        findings.insert(0, Finding("duplicate-key", "$", f"JSON 有重複的鍵 {dup!r}，後面的值會悄悄蓋掉前面的"))
    if args.json:
        print(json.dumps({"errors": len(findings), "findings": [f.as_dict() for f in findings]}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f)
        if findings:
            print(f"[FAIL] {path}：{len(findings)} 個錯誤")
        else:
            print(f"[PASS] {path}：五條路徑、備援、白名單與確認旗標皆符合")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
