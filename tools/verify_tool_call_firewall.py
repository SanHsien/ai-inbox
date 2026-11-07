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
import posixpath
import sys
from pathlib import Path
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


DEFAULT_WRITE_TOOLS = frozenset({"write_file", "edit_file", "delete_file", "run_command"})


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


def compute_request_digest(call: Dict[str, Any]) -> str:
    """
    對工具呼叫信封（tool, role, path, content_sha256）計算確定性 SHA-256 請求雜湊。
    若 call 提供 'content' 原文則自動計算其 SHA-256。
    """
    content_hash = call.get("content_sha256")
    if not content_hash:
        content_hash = compute_content_sha256(str(call.get("content", "")))
    canonical = {
        "tool": str(call.get("tool", "")).strip(),
        "role": str(call.get("role", "")).strip(),
        "path": normalize_logical_path(str(call.get("path", ""))),
        "content_sha256": str(content_hash).strip().lower(),
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
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
    ) -> None:
        self.allowed_roles: Set[str] = {r.strip() for r in allowed_roles if r.strip()}
        self.allowed_roots: Tuple[str, ...] = tuple(
            normalize_logical_path(r).rstrip("/") + "/" for r in allowed_roots if normalize_logical_path(r)
        )
        self.write_tools: Set[str] = set(write_tools)
        self.consumed_receipts: Set[str] = set()

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

        tool = str(call.get("tool", "")).strip()
        role = str(call.get("role", "")).strip()
        raw_path = str(call.get("path", "")).strip()

        if not tool or not role or not raw_path:
            return False, "INVALID_ENVELOPE", "缺少必要欄位 (tool / role / path)"

        if role not in self.allowed_roles:
            return False, "UNAUTHORIZED_ROLE", f"角色 '{role}' 未獲授權執行工具呼叫"

        if has_path_traversal(raw_path):
            return False, "PATH_TRAVERSAL", f"路徑 '{raw_path}' 含 '..' 越界區段"

        norm_path = normalize_logical_path(raw_path)
        if self.allowed_roots and not any(
            norm_path == root.rstrip("/") or norm_path.startswith(root)
            for root in self.allowed_roots
        ):
            return False, "OUTSIDE_ALLOWED_ROOT", f"路徑 '{norm_path}' 不在允許根目錄範圍內"

        if tool in self.write_tools:
            if not receipt or not isinstance(receipt, dict):
                return False, "MISSING_RECEIPT", f"寫入型工具 '{tool}' 必須附帶單次審批收據"

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

            self.consumed_receipts.add(receipt_id)

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


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="驗證 Tool Call 單次審批收據與分析 Agent Trace Span 去重指標"
    )
    parser.add_argument("--verify-calls", type=str, default="", help="檢查工具呼叫與收據批次 JSON 檔")
    parser.add_argument("--analyze-trace", type=str, default="", help="分析 Agent Trace JSON/JSONL 檔案")
    args = parser.parse_args(argv)

    if not args.verify_calls and not args.analyze_trace:
        print("[INFO] 請提供 --verify-calls 或 --analyze-trace 參數。")
        return 0

    exit_code = 0
    if args.verify_calls:
        p = Path(args.verify_calls)
        if not p.is_file():
            print(f"[ERROR] 找不到檔案：{p}")
            return 1
        data = json.loads(p.read_text(encoding="utf-8"))
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
        report = analyze_trace_spans(spans)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
