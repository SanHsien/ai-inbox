#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Call Firewall & Agent Trace Span Deduplicator (verify_tool_call_firewall.py)
---------------------------------------------------------------------------------
借鑑 rohitg00/ai-engineering-from-scratch 之 03 · Tool Call Firewall 與 02 · Agent Trace Debugger：
1. 綁定請求內容雜湊之單次審批收據驗證器（Request-Bound Single-Use Approval Receipt）：
   - 攔截審批後竄改寫入內容或路徑（TOCTOU Modification / Digest Mismatch）
   - 攔截同一張審批收據重放攻擊（Single-Use Replay Defense）
   - 攔截未授權角色與路徑穿越（Path Traversal / Unauthorized Root）
2. Agent Trace 父子 Span 時間與 Token 去重分析器（Trace Span Deduplicator）：
   - 合併重疊子區間（Interval Union），扣除子 Span 重疊執行時間以算出真實 Exclusive Duration
   - 扣除父子重複計算之 Token，算出 Exclusive Tokens 與不重複總 Token 消耗
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


TOOL_ACCESS = {"read_file": "read", "write_file": "write", "edit_file": "write",
               "delete_file": "write", "run_command": "write"}

DEFAULT_WRITE_TOOLS = frozenset({"write_file", "edit_file", "delete_file", "run_command"})

# 每種工具允許的欄位白名單；出現未列欄位一律拒絕（UNKNOWN_FIELD）。
_BASE_FIELDS = frozenset({"tool", "role", "path"})
TOOL_ALLOWED_FIELDS = {
    "read_file": _BASE_FIELDS,
    "write_file": _BASE_FIELDS | {"content", "content_sha256"},
    "edit_file": _BASE_FIELDS | {"content", "content_sha256", "old_string", "new_string"},
    "delete_file": _BASE_FIELDS | {"content", "content_sha256"},
    "run_command": _BASE_FIELDS | {"content", "content_sha256", "command"},
}
# 這些欄位若出現必須是字串
_STRING_FIELDS = frozenset({"old_string", "new_string", "command"})

_RESERVED_DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul"} | {f"com{i}" for i in range(1, 10)} | {f"lpt{i}" for i in range(1, 10)}
)


def has_unsafe_windows_segment(raw_path: str) -> bool:
    """含 ':'（NTFS 替代資料串流、磁碟機代號）、結尾 '.'/空白、保留裝置名或 8.3 '~N' 短名的區段一律視為不安全。"""
    if ":" in raw_path:
        return True
    for seg in raw_path.replace("\\", "/").split("/"):
        if not seg or seg == ".":
            continue
        if seg != seg.rstrip(" .") or seg.split(".")[0].strip().lower() in _RESERVED_DEVICE_NAMES:
            return True
        if "~" in seg and any(ch.isdigit() for ch in seg.split("~", 1)[1][:1]):
            return True
    return False


def normalize_logical_path(raw_path: str) -> str:
    """將路徑統一轉為 POSIX 斜線並保留相對層級以檢查 '..' 逃逸。"""
    cleaned = raw_path.strip().replace("\\", "/")
    if not cleaned:
        return ""
    parts = [p for p in cleaned.split("/") if p and p != "."]
    return "/".join(parts)


def has_path_traversal(raw_path: str) -> bool:
    """檢查路徑是否含 '..' 穿越區段。"""
    cleaned = raw_path.strip().replace("\\", "/")
    return ".." in cleaned.split("/")


def compute_content_sha256(content: str) -> str:
    """計算字串內容之 SHA-256 hex digest。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def canonical_call(call: Dict[str, Any]) -> Dict[str, Any]:
    """
    整個工具呼叫的 canonical 形式：所有欄位（含 command、old_string、new_string 等）都納入，
    path 正規化、tool/role 去空白；自附 content_sha256 由實際 content 重算，不採信。
    """
    canon: Dict[str, Any] = {}
    for key, value in call.items():
        if key == "content_sha256":
            continue
        if key in ("tool", "role"):
            value = str(value).strip()
        elif key == "path":
            value = normalize_logical_path(str(value))
        canon[str(key)] = value
    canon["content_sha256"] = compute_content_sha256(call.get("content", ""))
    return canon


def compute_request_digest(call: Dict[str, Any]) -> str:
    """對整個 canonical call（鍵排序後序列化）計算確定性 SHA-256 請求雜湊。"""
    payload = json.dumps(canonical_call(call), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def issue_approval_receipt(receipt_id: str, call: Dict[str, Any]) -> Dict[str, str]:
    """為特定工具呼叫簽發綁定內容雜湊與角色的單次審批收據。"""
    return {
        "receipt_id": str(receipt_id).strip(),
        "approved_role": str(call.get("role", "")).strip(),
        "request_digest": compute_request_digest(call),
    }


class ToolCallFirewall:
    """狀態化工具呼叫防火牆：在單次執行（Invocation）內強制單次審批收據消費與路徑邊界。"""

    def __init__(
        self,
        allowed_roles: Sequence[str] = ("implementer", "maintainer"),
        allowed_roots: Sequence[str] = ("workspace/", "src/", "docs/", "tools/", "tests/"),
        write_tools: Sequence[str] = tuple(DEFAULT_WRITE_TOOLS),
        workspace_root: Optional[Path] = None,
    ) -> None:
        self.workspace_root = (workspace_root or Path.cwd()).resolve()
        if not self.workspace_root.is_dir():
            raise ValueError("workspace_root 必須是存在的目錄")
        if not allowed_roots or any(not isinstance(r, str) or not r.strip() or
                                    PureWindowsPath(r).drive or r.replace("\\", "/").startswith("/") or
                                    has_path_traversal(r) for r in allowed_roots):
            raise ValueError("allowed_roots 必須是非空 workspace 相對路徑清單")
        self.allowed_roles: Set[str] = {r.strip() for r in allowed_roles if r.strip()}
        self.allowed_roots: Tuple[str, ...] = tuple(
            normalize_logical_path(r).rstrip("/") + "/" for r in allowed_roots if normalize_logical_path(r)
        )
        self.write_tools: Set[str] = set(write_tools)
        self.consumed_receipts: Set[str] = set()
        self.consumed_digests: Set[str] = set()

    def verify_call(
        self,
        call: Dict[str, Any],
        receipt: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str, str]:
        """
        驗證單筆工具呼叫。
        回傳 (allowed: bool, code: str, reason: str)。
        """
        if not isinstance(call, dict):
            return False, "INVALID_ENVELOPE", "呼叫信封必須為 JSON 物件"

        if any(not isinstance(call.get(k), str) or not call[k].strip()
               for k in ("tool", "role", "path")):
            return False, "INVALID_ENVELOPE", "必要欄位必須是非空字串"
        tool, role, raw_path = (call[k].strip() for k in ("tool", "role", "path"))
        if tool not in TOOL_ACCESS:
            return False, "UNKNOWN_TOOL", "未列於明確工具對照表"
        unknown = sorted(str(k) for k in call if k not in TOOL_ALLOWED_FIELDS[tool])
        if unknown:
            return False, "UNKNOWN_FIELD", f"工具 '{tool}' 不允許欄位：{', '.join(unknown)}"
        if any(k in call and not isinstance(call[k], str) for k in _STRING_FIELDS):
            return False, "INVALID_ENVELOPE", "command／old_string／new_string 必須是字串"
        if tool == "run_command" and not call.get("command", "").strip():
            return False, "INVALID_ENVELOPE", "run_command 必須提供非空 command"
        if "content" in call and not isinstance(call["content"], str):
            return False, "INVALID_ENVELOPE", "content 必須是字串"
        if TOOL_ACCESS[tool] == "write" and not isinstance(call.get("content"), str):
            return False, "INVALID_ENVELOPE", "寫入型工具必須提供實際 content（無內容時用空字串）"
        if "content_sha256" in call and call["content_sha256"] != compute_content_sha256(call.get("content", "")):
            return False, "CONTENT_HASH_MISMATCH", "自附雜湊與實際 content 不符"
        if PureWindowsPath(raw_path).drive or raw_path.replace("\\", "/").startswith("/"):
            return False, "ABSOLUTE_PATH", "禁止絕對、UNC 與磁碟機路徑"

        if role not in self.allowed_roles:
            return False, "UNAUTHORIZED_ROLE", f"角色 '{role}' 未獲授權執行工具呼叫"

        if has_path_traversal(raw_path):
            return False, "PATH_TRAVERSAL", f"路徑 '{raw_path}' 含 '..' 越界區段"
        if call["path"] != raw_path or has_unsafe_windows_segment(raw_path):
            return False, "UNSAFE_PATH", f"路徑 '{raw_path}' 含 ':'（ADS／磁碟機）、結尾點或空白、保留裝置名或 8.3 短名"

        norm_path = normalize_logical_path(raw_path)
        try:
            target = (self.workspace_root / norm_path).resolve()
            roots = [(self.workspace_root / r).resolve() for r in self.allowed_roots]
            if not target.is_relative_to(self.workspace_root) or not any(
                root.is_relative_to(self.workspace_root) and target.is_relative_to(root) for root in roots
            ):
                return False, "OUTSIDE_ALLOWED_ROOT", "解析後路徑不在 workspace 允許目錄內"
        except (OSError, ValueError, RuntimeError):
            return False, "INVALID_PATH", "無法解析路徑"

        if TOOL_ACCESS[tool] == "write" or tool in self.write_tools:
            if not receipt or not isinstance(receipt, dict):
                return False, "MISSING_RECEIPT", f"寫入型工具 '{tool}' 必須附帶單次審批收據"

            if any(not isinstance(receipt.get(k), str) or not receipt[k].strip()
                   for k in ("receipt_id", "approved_role", "request_digest")):
                return False, "INVALID_RECEIPT", "收據欄位必須是非空字串"

            receipt_id = str(receipt.get("receipt_id", "")).strip()
            approved_role = str(receipt.get("approved_role", "")).strip()
            expected_digest = str(receipt.get("request_digest", "")).strip().lower()

            if not receipt_id or not expected_digest:
                return False, "INVALID_RECEIPT", "審批收據缺少 receipt_id 或 request_digest"

            if receipt_id in self.consumed_receipts:
                return False, "REPLAYED_RECEIPT", f"審批收據 '{receipt_id}' 已被消費過，拒絕重放"

            if approved_role != role:
                return False, "RECEIPT_ROLE_MISMATCH", f"審批收據綁定角色 '{approved_role}' 與呼叫者 '{role}' 不符"

            actual_digest = compute_request_digest(call)
            if actual_digest != expected_digest:
                return (
                    False,
                    "DIGEST_MISMATCH",
                    "呼叫內容或目標路徑於審批後遭竄改（request_digest 不吻合）",
                )

            if actual_digest in self.consumed_digests:
                return False, "REPLAYED_REQUEST", "同一請求內容已被審批消費過，換 receipt_id 重送也拒絕"

            self.consumed_receipts.add(receipt_id)
            self.consumed_digests.add(actual_digest)

        return True, "ALLOWED", "驗證通過"


def _merge_intervals(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """合併重疊或相接的時間區間 [start, end]。"""
    valid = [(max(0.0, float(s)), max(0.0, float(e))) for s, e in intervals if float(e) > float(s)]
    if not valid:
        return []
    valid.sort(key=lambda x: (x[0], x[1]))
    merged: List[Tuple[float, float]] = [valid[0]]
    for cur_s, cur_e in valid[1:]:
        prev_s, prev_e = merged[-1]
        if cur_s <= prev_e:
            merged[-1] = (prev_s, max(prev_e, cur_e))
        else:
            merged.append((cur_s, cur_e))
    return merged


def analyze_trace_spans(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析 Agent Trace Spans：
    - 扣除直接子 Span 在父 Span 時間範圍內的聯集重疊時間，計算 exclusive_duration_ms
    - 扣除直接子 Span 的 total_tokens，計算每個 Span 的 exclusive_tokens（若父 Span 為匯總型）
    - 找出第一個報錯的 Span、耗時最長的 Span 與花費最多 Exclusive Token 的 Span
    """
    children_by_parent: Dict[str, List[Dict[str, Any]]] = {}
    for sp in spans:
        pid = sp.get("parent_id")
        if pid:
            children_by_parent.setdefault(str(pid), []).append(sp)

    analyzed: List[Dict[str, Any]] = []
    first_error_span_id: Optional[str] = None
    first_error_time: Optional[float] = None

    for sp in spans:
        sid = str(sp.get("span_id", ""))
        start_ms = float(sp.get("start_ms", 0.0))
        end_ms = float(sp.get("end_ms", start_ms))
        inclusive_ms = max(0.0, end_ms - start_ms)

        direct_children = children_by_parent.get(sid, [])
        clipped_child_intervals: List[Tuple[float, float]] = []
        children_token_sum = 0

        for ch in direct_children:
            ch_s = max(start_ms, float(ch.get("start_ms", 0.0)))
            ch_e = min(end_ms, float(ch.get("end_ms", ch_s)))
            if ch_e > ch_s:
                clipped_child_intervals.append((ch_s, ch_e))
            children_token_sum += int(ch.get("total_tokens", 0))

        merged_child = _merge_intervals(clipped_child_intervals)
        child_covered_ms = sum(e - s for s, e in merged_child)
        exclusive_ms = max(0.0, inclusive_ms - child_covered_ms)

        raw_tokens = int(sp.get("total_tokens", 0))
        if direct_children and raw_tokens >= children_token_sum:
            exclusive_tokens = raw_tokens - children_token_sum
        else:
            exclusive_tokens = raw_tokens

        status = str(sp.get("status", "ok")).lower()
        if status in ("error", "failed") and (first_error_time is None or start_ms < first_error_time):
            first_error_time = start_ms
            first_error_span_id = sid

        analyzed.append({
            "span_id": sid,
            "parent_id": sp.get("parent_id"),
            "name": sp.get("name", sid),
            "status": status,
            "inclusive_duration_ms": round(inclusive_ms, 3),
            "exclusive_duration_ms": round(exclusive_ms, 3),
            "raw_tokens": raw_tokens,
            "exclusive_tokens": exclusive_tokens,
        })

    max_token_span = max(analyzed, key=lambda x: x["exclusive_tokens"])["span_id"] if analyzed else None
    max_dur_span = max(analyzed, key=lambda x: x["exclusive_duration_ms"])["span_id"] if analyzed else None

    return {
        "spans": analyzed,
        "deduplicated_total_tokens": sum(x["exclusive_tokens"] for x in analyzed),
        "raw_sum_tokens": sum(x["raw_tokens"] for x in analyzed),
        "first_error_span_id": first_error_span_id,
        "max_exclusive_token_span_id": max_token_span,
        "max_exclusive_duration_span_id": max_dur_span,
    }


def _main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="驗證 Tool Call 單次審批收據與分析 Agent Trace Span 去重指標"
    )
    parser.add_argument("--verify-calls", type=str, default="", help="檢查工具呼叫與收據批次 JSON 檔")
    parser.add_argument("--analyze-trace", type=str, default="", help="分析 Agent Trace JSON/JSONL 檔案")
    args = parser.parse_args(argv)

    if not args.verify_calls and not args.analyze_trace:
        print("[INFO] 請提供 --verify-calls 或 --analyze-trace 參數。")
        return 2

    exit_code = 0
    if args.verify_calls:
        p = Path(args.verify_calls)
        if not p.is_file():
            print(f"[ERROR] 找不到檔案：{p}")
            return 1
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("invocations"), list) or not data["invocations"]:
                raise ValueError("invocations 必須是非空清單")
            for key in ("allowed_roles", "allowed_roots"):
                if key in data and (not isinstance(data[key], list) or not data[key] or
                                    any(not isinstance(x, str) or not x.strip() for x in data[key])):
                    raise ValueError(key + " 必須是非空字串清單")
            if any(not isinstance(item, dict) or not isinstance(item.get("call"), dict) for item in data["invocations"]):
                raise ValueError("invocations 項目必須包含 call 物件")
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"[ERROR] 無效輸入：{exc}")
            return 2
        fw = ToolCallFirewall(
            allowed_roles=data.get("allowed_roles", ("implementer", "maintainer")),
            allowed_roots=data.get("allowed_roots", ("workspace/", "src/", "docs/", "tools/", "tests/")),
        )
        for idx, item in enumerate(data.get("invocations", []), 1):
            ok, code, reason = fw.verify_call(item.get("call", {}), item.get("receipt"))
            if not ok:
                print(f"[BLOCK #{idx}] {code}: {reason}")
                exit_code = 1
            else:
                print(f"[ALLOW #{idx}] {code}: {reason}")

    if args.analyze_trace:
        p = Path(args.analyze_trace)
        if not p.is_file():
            print(f"[ERROR] 找不到檔案：{p}")
            return 1
        raw_text = p.read_text(encoding="utf-8").strip()
        if raw_text.startswith("["):
            spans = json.loads(raw_text)
        else:
            spans = [json.loads(line) for line in raw_text.splitlines() if line.strip()]
        if not isinstance(spans, list) or not spans or any(not isinstance(s, dict) or not {"span_id", "start_ms", "end_ms", "total_tokens"} <= s.keys() for s in spans):
            raise ValueError("trace 必須是非空且具必要欄位的 span 清單")
        report = analyze_trace_spans(spans)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return exit_code


def main(argv: Optional[Sequence[str]] = None) -> int:
    """退出碼：0 全部通過；1 拒絕／路徑不存在；2 輸入或 schema 無效。"""
    try:
        return _main(argv)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"[ERROR] 無法判斷輸入：{exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
