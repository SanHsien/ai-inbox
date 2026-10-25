#!/usr/bin/env python3
"""
tools/task_cli.py
AI 與維護者共用的任務佇列查詢、認領、結案與狀態同步 CLI。

用法：
    python tools/task_cli.py next [--priority 高|中|低] [--limit 10] [--json]
    python tools/task_cli.py show <TASK_ID>
    python tools/task_cli.py claim <TASK_ID>
    python tools/task_cli.py complete <TASK_ID> --evidence "<Commit/路徑/測試輸出摘要>" [--date YYYY-MM-DD]
    python tools/task_cli.py close <TASK_ID> --reason "<不做原因>"
    python tools/task_cli.py sync-status
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402

STATUS_BODY_LABELS = {
    "pending": "`🔴 未做 (Pending)`",
    "in-progress": "`🟡 進行中 (In Progress)`",
    "done": "`🟢 已完成 (Done)`",
    "archived": "`⚪ 已封存 (Archived)`",
}


def find_task(notes: list[bi.Note], task_id: str) -> bi.Task:
    for n in notes:
        for t in n.tasks:
            if t.id == task_id:
                return t
    raise KeyError(f"找不到任務 ID：{task_id}")


def _update_note_frontmatter_status(text: str, new_status: str) -> str:
    """更新 YAML frontmatter 中的 status 欄位與正文頂部的當前狀態標記。"""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        try:
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
            for i in range(1, end):
                m = re.match(r"^(status:\s*)([^\s#]+)(.*)$", lines[i])
                if m:
                    lines[i] = f"{m.group(1)}{new_status}{m.group(3)}"
                    break
        except StopIteration:
            pass
    body_label = STATUS_BODY_LABELS.get(new_status)
    if body_label:
        for i, line in enumerate(lines[:45]):
            if line.startswith("- **當前狀態**："):
                lines[i] = f"- **當前狀態**：{body_label}"
                break
    return "\n".join(lines)


def _one_line(text: str) -> str:
    """把使用者輸入壓成單行。欄位值只有一行：換行後的內容會落到沒縮排的位置，
    被當成任務區塊結束，README 只剩第一行，其餘變成筆記裡的孤兒文字（甚至多出假任務行）。"""
    return " ".join(text.split())


def _read_note(note_path: Path) -> tuple[str, str]:
    """讀取筆記內容（內部統一以 \\n 切行）並回傳原檔換行符號（\\r\\n 或 \\n）。"""
    raw = note_path.read_bytes()
    crlf = raw.count(b"\r\n")
    # 多數決：只有幾行 CRLF 的 LF 檔（例如貼上的片段）寫回時不該整份變成 CRLF
    nl = "\r\n" if crlf > raw.count(b"\n") - crlf else "\n"
    return raw.decode("utf-8").replace("\r\n", "\n"), nl


def _locate_task_span(lines: list[str], task_id: str) -> tuple[int, int]:
    """回傳任務標題行 index (0-based) 與該任務區塊結束 index (exclusive)。"""
    start = -1
    for i, line in bi.iter_outside_fences(lines):
        m = bi.TASK_LINE.match(line)
        if m and m["id"] == task_id:
            start = i
            break
    if start < 0:
        raise KeyError(f"在檔案中找不到任務行：{task_id}")
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if bi.TASK_LINE.match(line):
            break
        if line.strip() and not line.startswith(" "):
            break
        end += 1
    # 退回尾端空白行，讓插入欄位緊貼在任務欄位最後一行
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return start, end


def apply_claim(note_path: Path, task_id: str) -> str:
    text, nl = _read_note(note_path)
    lines = text.split("\n")
    start, end = _locate_task_span(lines, task_id)
    if re.match(r"^- \[[xX]\] ", lines[start]):
        raise ValueError(f"{task_id} 已是完成狀態，無法認領")

    status_idx = next(
        (i for i in range(start + 1, end) if re.match(r"^\s{2,}- \*\*狀態\*\*[：:]", lines[i])),
        None,
    )
    status_line = "  - **狀態**：🟡 進行中"
    if status_idx is not None:
        lines[status_idx] = status_line
    else:
        lines.insert(start + 1, status_line)

    note_path.write_text("\n".join(lines), encoding="utf-8", newline=nl)
    return sync_single_note_status(note_path)


def apply_close(note_path: Path, task_id: str, reason: str) -> str:
    reason = _one_line(reason)
    if not reason:
        raise ValueError("關閉理由不可為空")
    text, nl = _read_note(note_path)
    lines = text.split("\n")
    start, end = _locate_task_span(lines, task_id)
    if re.match(r"^- \[[xX]\] ", lines[start]):
        raise ValueError(f"{task_id} 已是完成狀態，不可直接關閉")

    status_idx = next(
        (i for i in range(start + 1, end) if re.match(r"^\s{2,}- \*\*狀態\*\*[：:]", lines[i])),
        None,
    )
    status_line = f"  - **狀態**：⚪ 不做（{reason}）"
    if status_idx is not None:
        lines[status_idx] = status_line
    else:
        lines.insert(start + 1, status_line)

    note_path.write_text("\n".join(lines), encoding="utf-8", newline=nl)
    return sync_single_note_status(note_path)


def apply_complete(note_path: Path, task_id: str, evidence: str, date_str: str) -> str:
    evidence = _one_line(evidence)
    if not bi.filled(evidence):
        raise ValueError("驗收證據不可為空或佔位文字")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        raise ValueError(f"完成日期需為 YYYY-MM-DD：{date_str}")

    text, nl = _read_note(note_path)
    lines = text.split("\n")
    start, end = _locate_task_span(lines, task_id)
    if re.match(r"^- \[[xX]\] ", lines[start]):
        raise ValueError(f"{task_id} 已是完成狀態，不可重複結案（會覆寫既有完成日期與證據）")

    lines[start] = re.sub(r"^- \[[ xX]\] ", "- [x] ", lines[start], count=1)

    # 移除 `狀態` 行，並更新或新增 `完成日期` 與 `實作紀錄 / 證據`
    block = [line for line in lines[start + 1 : end] if not re.match(r"^\s{2,}- \*\*狀態\*\*[：:]", line)]

    date_line = f"  - **完成日期**：{date_str}"
    ev_line = f"  - **實作紀錄 / 證據**：{evidence}"

    date_idx = next((i for i, l in enumerate(block) if re.match(r"^\s{2,}- \*\*完成日期\*\*[：:]", l)), None)
    if date_idx is not None:
        block[date_idx] = date_line

    ev_idx = next((i for i, l in enumerate(block) if re.match(r"^\s{2,}- \*\*實作紀錄 / 證據\*\*[：:]", l)), None)
    if ev_idx is not None:
        block[ev_idx] = ev_line
        if date_idx is None:
            block.insert(ev_idx, date_line)
    else:
        if date_idx is None:
            block.append(date_line)
        block.append(ev_line)

    lines[start + 1 : end] = block
    note_path.write_text("\n".join(lines), encoding="utf-8", newline=nl)
    return sync_single_note_status(note_path)


def sync_single_note_status(note_path: Path) -> str:
    note = bi.parse_note(note_path)
    expected = bi.expected_note_status(note)
    text, nl = _read_note(note_path)
    updated = _update_note_frontmatter_status(text, expected)
    if updated != text:
        note_path.write_text(updated, encoding="utf-8", newline=nl)
    return expected


def cmd_next(args: argparse.Namespace) -> int:
    notes = bi.load_notes()
    active = [
        t
        for n in notes
        for t in n.tasks
        if not t.done and not t.archived and (not args.priority or t.priority == args.priority)
    ]
    active.sort(key=lambda t: (0 if t.in_progress else 1, bi.PRIORITY_RANK.get(t.priority, 9), t.id))
    selected = active[: args.limit] if args.limit else active

    if args.json:
        payload = [
            {
                "id": t.id,
                "status": "in-progress" if t.in_progress else "pending",
                "priority": t.priority,
                "title": t.title,
                "scope": t.fields.get("目標範圍", ""),
                "dod": t.fields.get("驗收標準（DoD）", ""),
                "note": f"notes/{t.note.path.name}",
                "line": t.line,
            }
            for t in selected
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"[*] 待辦佇列共 {len(active)} 項（顯示前 {len(selected)} 項）：\n")
    for t in selected:
        state = "🟡 進行中" if t.in_progress else "🔴 未做"
        print(f"{t.id} [{state}｜優先級：{t.priority}] {t.title}")
        print(f"  筆記：notes/{t.note.path.name}:{t.line}")
        print(f"  範圍：{t.fields.get('目標範圍', '-')}")
        print(f"  DoD ：{t.fields.get('驗收標準（DoD）', '-')}\n")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    notes = bi.load_notes()
    task = find_task(notes, args.task_id)
    lines = task.note.path.read_text(encoding="utf-8").split("\n")
    start, end = _locate_task_span(lines, args.task_id)
    print(f"# 來源：notes/{task.note.path.name}:{task.line}（筆記 status: {task.note.meta.get('status')}）")
    print("\n".join(lines[start:end]))
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    notes = bi.load_notes()
    task = find_task(notes, args.task_id)
    new_status = apply_claim(task.note.path, args.task_id)
    bi.main([])
    print(f"[*] 已認領 {args.task_id}（{task.note.path.name} status -> {new_status}）")
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    notes = bi.load_notes()
    task = find_task(notes, args.task_id)
    missing = bi.missing_dod_artifacts(task)
    if missing:
        raise ValueError(f"{args.task_id} 的 DoD 要求產出的檔案不存在，不可結案：{', '.join(missing)}")
    date_str = args.date or dt.date.today().isoformat()
    new_status = apply_complete(task.note.path, args.task_id, args.evidence, date_str)
    bi.main([])
    print(f"[*] 已完成 {args.task_id}（{task.note.path.name} status -> {new_status}）")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    notes = bi.load_notes()
    task = find_task(notes, args.task_id)
    new_status = apply_close(task.note.path, args.task_id, args.reason)
    bi.main([])
    print(f"[*] 已關閉 {args.task_id} 為不做（{task.note.path.name} status -> {new_status}）")
    return 0


def cmd_sync_status(_args: argparse.Namespace) -> int:
    notes = bi.load_notes()
    changed = []
    for n in notes:
        if not n.tasks:
            continue
        expected = bi.expected_note_status(n)
        current = n.meta.get("status", "")
        if current != expected:
            sync_single_note_status(n.path)
            changed.append((n.path.name, current, expected))
    bi.main([])
    for name, old, new in changed:
        print(f"[*] 修正 {name}: {old} -> {new}")
    print(f"[*] 共同步 {len(changed)} 篇筆記狀態。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ai-inbox 任務查詢、認領、結案與狀態同步 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_next = sub.add_parser("next", help="列出待辦任務佇列（按進行中與優先級排序）")
    p_next.add_argument("--priority", choices=bi.PRIORITIES, help="只看特定優先級（高/中/低）")
    p_next.add_argument("--limit", type=int, default=15, help="最多顯示幾筆（預設 15，0 為全部）")
    p_next.add_argument("--json", action="store_true", help="輸出 JSON 格式供 Agent 解析")
    p_next.set_defaults(func=cmd_next)

    p_show = sub.add_parser("show", help="顯示指定任務的完整區塊與 DoD")
    p_show.add_argument("task_id", help="任務 ID，例如 T-20261023-01")
    p_show.set_defaults(func=cmd_show)

    p_claim = sub.add_parser("claim", help="認領任務（標記 🟡 進行中並同步 README）")
    p_claim.add_argument("task_id", help="任務 ID")
    p_claim.set_defaults(func=cmd_claim)

    p_done = sub.add_parser("complete", help="完成任務（勾選 [x]、寫入完成日期與證據並同步 README）")
    p_done.add_argument("task_id", help="任務 ID")
    p_done.add_argument("--evidence", required=True, help="實作紀錄與驗收證據")
    p_done.add_argument("--date", help="完成日期 YYYY-MM-DD（預設今天）")
    p_done.set_defaults(func=cmd_complete)

    p_close = sub.add_parser("close", help="將任務標記為 ⚪ 不做並寫入理由")
    p_close.add_argument("task_id", help="任務 ID")
    p_close.add_argument("--reason", required=True, help="不做／關閉理由")
    p_close.set_defaults(func=cmd_close)

    p_sync = sub.add_parser("sync-status", help="同步全庫筆記 frontmatter status 與 README")
    p_sync.set_defaults(func=cmd_sync_status)
    return p


def main(argv: list[str] | None = None) -> int:
    bi.ensure_utf8_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (KeyError, ValueError) as e:
        print(f"[FAIL] {e.args[0] if e.args else e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
