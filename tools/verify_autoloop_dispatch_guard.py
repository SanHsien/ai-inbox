#!/usr/bin/env python3
"""
tools/verify_autoloop_dispatch_guard.py
Agent Autoloop 事件溯源派工與四層安全防線驗證器：
1. AUTOLOOP-001 (Route Override Guard)：外部事件 payload 禁止夾帶 cwd/agent/access/command 等控制欄位。
2. AUTOLOOP-002 (Prompt Parameterization Guard)：規則 prompt 禁止直接拼接 {body}/{title} 等外部自由文本，僅允許 {type}/{id}/{link}/{context_file}。
3. AUTOLOOP-003 (TTL Hop Limit Guard)：事件鏈 hop 必須單調遞增（經 ask/later 不得清零），超過 max_hops (預設 8) 必須熔斷阻斷派工。
4. AUTOLOOP-004 (Anti-Self-Approval & Isolation Guard)：Worker 禁止掛載卡片回答工具（防自問自答）、PR 交付禁止檢出執行 PR 程式碼、Windows ACL 僅允許本人與 SYSTEM。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_EVENT_FIELDS = frozenset({
    "cwd",
    "agent",
    "to",
    "access",
    "program",
    "command",
    "skill",
    "parallel",
    "hop",
})

ALLOWED_PROMPT_PLACEHOLDERS = frozenset({
    "type",
    "id",
    "link",
    "context_file",
    "prompt",
})

UNTRUSTED_PLACEHOLDERS = frozenset({
    "body",
    "title",
    "issue_body",
    "issue_title",
    "comment",
    "description",
    "payload",
    "raw_text",
})

SELF_APPROVAL_TOOLS = frozenset({
    "autoloop_answer",
    "answer_card",
    "approve_delivery",
    "mcp__autoloop__answer",
    "agent-autoloop answer",
})

SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9._:/-]+$")
PLACEHOLDER_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")


def ensure_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def check_event_payloads(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    """AUTOLOOP-001: 檢查外部事件是否夾帶禁止的控制欄位，以及識別元是否符合字元白名單。"""
    findings: list[dict[str, str]] = []
    for idx, ev in enumerate(events):
        ev_id = str(ev.get("id", f"event[{idx}]"))
        injected = sorted(set(ev.keys()) & FORBIDDEN_EVENT_FIELDS)
        if injected:
            findings.append({
                "rule_id": "AUTOLOOP-001",
                "target": ev_id,
                "message": f"事件 payload 夾帶禁止的路由／權限控制欄位：{', '.join(injected)}",
            })
        for key in ("type", "id"):
            val = ev.get(key)
            if isinstance(val, str) and val and not SAFE_IDENTIFIER_RE.match(val):
                findings.append({
                    "rule_id": "AUTOLOOP-001",
                    "target": ev_id,
                    "message": f"事件欄位 '{key}' 含非白名單字元：{val!r}",
                })
    return findings


def check_dispatch_rules(rules: list[dict[str, Any]]) -> list[dict[str, str]]:
    """AUTOLOOP-002: 檢查規則是否將外部不可信正文直接拼入 prompt，或對不可信來源開啟無隔離 resume+full。"""
    findings: list[dict[str, str]] = []
    for idx, rule in enumerate(rules):
        name = str(rule.get("name", f"rule[{idx}]"))
        prompt = str(rule.get("prompt", ""))
        for ph in PLACEHOLDER_RE.findall(prompt):
            if ph in UNTRUSTED_PLACEHOLDERS or ph not in ALLOWED_PROMPT_PLACEHOLDERS:
                findings.append({
                    "rule_id": "AUTOLOOP-002",
                    "target": name,
                    "message": f"規則 prompt 直接內插未受信任佔位符 '{{{ph}}}'，應改由獨立資料檔 context.json 讀取",
                })
        when = rule.get("when") or {}
        untrusted_source = when.get("source") in ("github", "gitlab", "webhook", "external")
        if untrusted_source and rule.get("access") == "full" and rule.get("resume") is True:
            findings.append({
                "rule_id": "AUTOLOOP-002",
                "target": name,
                "message": "外部事件來源同時啟用 access='full' 與 resume=True，跨輪次殘留外部文字易導致權限劫持",
            })
    return findings


def check_hop_chain(chain: list[dict[str, Any]], max_hops: int = 8) -> list[dict[str, str]]:
    """AUTOLOOP-003: 檢查事件跳數是否單調遞增（經 ask/later 不可清零）且超過 max_hops 時強制熔斷。"""
    findings: list[dict[str, str]] = []
    prev_hop: int | None = None
    for idx, step in enumerate(chain):
        step_id = str(step.get("step_id", f"step[{idx}]"))
        hop = step.get("hop")
        via = str(step.get("via", "event"))
        dispatched = bool(step.get("dispatched", True))
        if not isinstance(hop, int) or hop < 0:
            findings.append({
                "rule_id": "AUTOLOOP-003",
                "target": step_id,
                "message": f"無效的 hop 計數：{hop!r}",
            })
            continue
        if prev_hop is not None and hop <= prev_hop:
            findings.append({
                "rule_id": "AUTOLOOP-003",
                "target": step_id,
                "message": f"事件跳數在經由 '{via}' 後未遞增或被清零（前次 hop={prev_hop}，本次 hop={hop}）",
            })
        if hop > max_hops and dispatched:
            findings.append({
                "rule_id": "AUTOLOOP-003",
                "target": step_id,
                "message": f"hop={hop} 已超過熔斷上限 max_hops={max_hops}，但 dispatched 仍為 True（未熔斷阻斷）",
            })
        prev_hop = hop
    return findings


def check_worker_and_delivery_isolation(isolation: dict[str, Any]) -> list[dict[str, str]]:
    """AUTOLOOP-004: 檢查 Worker 是否掛載自審工具、PR 交付是否檢出外部程式碼、Windows ACL 是否外洩。"""
    findings: list[dict[str, str]] = []
    worker_tools = set(isolation.get("worker_tools") or [])
    overlap = sorted(worker_tools & SELF_APPROVAL_TOOLS)
    if overlap:
        findings.append({
            "rule_id": "AUTOLOOP-004",
            "target": "worker_tools",
            "message": f"Worker 掛載了卡片拍板工具 {', '.join(overlap)}，Agent 可自問自答繞過人工審批",
        })

    delivery = isolation.get("delivery") or {}
    if delivery.get("checkout_pr_code") is True:
        findings.append({
            "rule_id": "AUTOLOOP-004",
            "target": "delivery.checkout_pr_code",
            "message": "交付流水線啟用了 checkout_pr_code=True，違反 PR 零檢出（僅讀 Git objects diff）原則",
        })
    if delivery.get("allow_octopus_merge") is True:
        findings.append({
            "rule_id": "AUTOLOOP-004",
            "target": "delivery.allow_octopus_merge",
            "message": "交付流水線允許章魚合併（allow_octopus_merge=True），可能隱藏未審查差異",
        })

    acl_principals = set(isolation.get("windows_data_dir_acl") or [])
    allowed_principals = {"CURRENT_USER", "SYSTEM", "Administrators"}
    leaked = sorted(acl_principals - allowed_principals)
    if leaked:
        findings.append({
            "rule_id": "AUTOLOOP-004",
            "target": "windows_data_dir_acl",
            "message": f"Windows 資料目錄 ACL 含未授權讀取主體（如沙盒帳號）：{', '.join(leaked)}",
        })
    return findings


def audit_bundle(bundle: dict[str, Any]) -> list[dict[str, str]]:
    max_hops = int(bundle.get("max_hops", 8))
    return [
        *check_event_payloads(bundle.get("events") or []),
        *check_dispatch_rules(bundle.get("rules") or []),
        *check_hop_chain(bundle.get("hop_chain") or [], max_hops=max_hops),
        *check_worker_and_delivery_isolation(bundle.get("isolation") or {}),
    ]


def default_clean_bundle() -> dict[str, Any]:
    return {
        "max_hops": 8,
        "events": [
            {"id": "issue-101", "type": "issues.opened", "link": "https://github.com/org/repo/issues/101"},
        ],
        "rules": [
            {
                "name": "handle-issue",
                "when": {"source": "github", "types": ["issues.opened"]},
                "to": "codex",
                "cwd": "~/code/app",
                "access": "edit",
                "resume": False,
                "prompt": "處理事件 {type} #{id}，詳見資料檔 {context_file}",
            }
        ],
        "hop_chain": [
            {"step_id": "s1", "hop": 1, "via": "event", "dispatched": True},
            {"step_id": "s2", "hop": 2, "via": "ask", "dispatched": True},
            {"step_id": "s3", "hop": 3, "via": "later", "dispatched": True},
            {"step_id": "s9", "hop": 9, "via": "event", "dispatched": False},
        ],
        "isolation": {
            "worker_tools": ["read_file", "edit_file", "run_tests"],
            "delivery": {"checkout_pr_code": False, "allow_octopus_merge": False},
            "windows_data_dir_acl": ["CURRENT_USER", "SYSTEM"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="驗證 Agent Autoloop 事件溯源派工之路由隔離、指令資料分離、TTL 跳數熔斷與反自審防線"
    )
    parser.add_argument("--config", type=Path, help="要檢驗的派工設定與事件鏈 JSON 檔路徑（未指定則執行內建基準驗證）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出檢驗結果")
    args = parser.parse_args(argv)

    if args.config is not None:
        try:
            bundle = json.loads(args.config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] 無法讀取設定檔 {args.config}: {exc}", file=sys.stderr)
            return 1
    else:
        bundle = default_clean_bundle()

    findings = audit_bundle(bundle)
    if args.json:
        print(json.dumps({"passed": len(findings) == 0, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        if findings:
            print(f"[FAIL] 偵測到 {len(findings)} 項 Autoloop 派工安全違規：")
            for f in findings:
                print(f"  - [{f['rule_id']}] {f['target']}: {f['message']}")
        else:
            print("[PASS] Agent Autoloop 四層派工安全防線檢驗通過。")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
