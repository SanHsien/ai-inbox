#!/usr/bin/env python3
"""
verify_agent_skill_pack_safety.py — 第三方 Claude Code / Agent Skill 與 MCP 工具鏈採納前安全與決定性靜態審計器 (T-20261108-04)

針對社群熱門 Agent Skill Pack 與 MCP 擴充（如 pbakaus/impeccable、chaseai-yt/claudex-loop、
Jakeschincariol/instagram-agent-skill、Leonxlnx/earshot 等）定義四條機械檢驗規則：
  - SKILLPACK-001 (No-Bypass-Sandbox-Escalation): 攔截 Skill / Script / Live Server 中夾帶
      `--dangerously-bypass-approvals-and-sandbox`、`--permission-mode bypassPermissions`、
      `--dangerously-skip-permissions` 等關閉沙盒與審批的自動提權參數（除非顯式標記拒絕或僅出現在安全警告文件中）。
  - SKILLPACK-002 (Hook-And-Telemetry-Gate): 當安裝器或配置啟用背景 Command Hook 或遠端目錄請求時，
      必須具備顯式關閉開關（如 `disableAllHooks`、`DO_NOT_TRACK=1`、`telemetry: false`）與預先審查機制。
  - SKILLPACK-003 (Zero-Fabrication-Placeholder): 自媒體與文案生成類 Skill 遇到未知數據時，
      必須強制使用佔位符（如 `{{your number}}`）並阻斷虛構指標（Fabricated Metrics），且發佈端必須維持「草稿唯讀、人工發佈（Human-Publish Gate）」。
  - SKILLPACK-004 (Deterministic-Linter-Backing): 宣稱具備評分或去 AI 味（Anti-Slop / Humanizer / Hook Scorer）的 Skill，
      必須附帶零網路依賴的確定性本地腳本或規則集，並诚實標註啟發式指標之統計邊界（如 AUC 限制），禁止宣稱「100% 不可偵測（Undetectable）」。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

def _ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

FORBIDDEN_BYPASS_FLAGS = (
    "--dangerously-bypass-approvals-and-sandbox",
    "--permission-mode bypassPermissions",
    "--dangerously-skip-permissions",
)

BANNED_OVERCLAIMS = (
    "100% undetectable",
    "guaranteed viral",
    "auto-post unattended without approval",
)


def default_suite() -> dict[str, Any]:
    """預設自我檢驗套件：涵蓋 2026-11-08 盤點的五大開源 Agent Skill / MCP 工具鏈設定。"""
    return {
        "packs": [
            {
                "id": "pbakaus/impeccable",
                "category": "ui-design-anti-slop",
                "cli_invocations": [
                    "npx impeccable detect src/",
                    "npx impeccable detect --json .",
                ],
                "env_overrides": {
                    "IMPECCABLE_LIVE_COPY_AGENT": "chat",
                    "DO_NOT_TRACK": "1",
                },
                "config": {
                    "telemetry": False,
                    "hook_reviewed": True,
                    "disable_hooks_flag": "--settings '{\"disableAllHooks\": true}'",
                },
                "human_publish_only": True,
                "unknown_metric_placeholder": "{{your number}}",
                "deterministic_tools": ["npx impeccable detect (62 deterministic rules)"],
                "claims": ["heuristic usability and anti-slop detector"],
            },
            {
                "id": "Jakeschincariol/instagram-agent-skill",
                "category": "social-content-workflow",
                "cli_invocations": [
                    "python3 skills/ig-reel/hookscore.py hooks.txt",
                    "python3 skills/ig-human/humanize.py draft.txt --report",
                    "python3 skills/ig-human/detect.py draft.txt",
                ],
                "env_overrides": {
                    "DO_NOT_TRACK": "1",
                },
                "config": {
                    "telemetry": False,
                    "hook_reviewed": True,
                    "disable_hooks_flag": "none-required",
                },
                "human_publish_only": True,
                "unknown_metric_placeholder": "{{your number}}",
                "deterministic_tools": [
                    "hookscore.py",
                    "beats.py",
                    "caption.py",
                    "humanize.py",
                    "detect.py",
                    "swipe.py",
                ],
                "claims": ["local heuristic 5-check panel, hookscore AUC 0.83 on bad hooks / 0.56 on winners"],
            },
            {
                "id": "Jakeschincariol/youtube-agent-skill",
                "category": "social-content-workflow",
                "cli_invocations": [
                    "python3 skills/yt-script/hookscore.py --hook 'example'",
                    "python3 skills/yt-package/title.py --title 'A' --thumb 'B'",
                    "python3 skills/yt-edit/deadair.py transcript.srt",
                ],
                "env_overrides": {
                    "DO_NOT_TRACK": "1",
                },
                "config": {
                    "telemetry": False,
                    "hook_reviewed": True,
                    "disable_hooks_flag": "none-required",
                },
                "human_publish_only": True,
                "unknown_metric_placeholder": "{{your number}}",
                "deterministic_tools": [
                    "hookscore.py",
                    "title.py",
                    "deadair.py",
                    "chapters.py",
                    "retention.py",
                    "swipe.py",
                ],
                "claims": ["heuristic hook panel calibrated on 74 hooks, draft-only"],
            },
            {
                "id": "Leonxlnx/earshot",
                "category": "multimedia-audio-verification",
                "cli_invocations": [
                    "earshot describe enter.ogg",
                    "earshot critique film.mp4",
                    "earshot timeline film.mp4",
                ],
                "env_overrides": {
                    "DO_NOT_TRACK": "1",
                },
                "config": {
                    "telemetry": False,
                    "hook_reviewed": True,
                    "disable_hooks_flag": "none-required",
                },
                "human_publish_only": True,
                "unknown_metric_placeholder": "{{your number}}",
                "deterministic_tools": [
                    "earshot measure (LUFS, true peak, LRA, spectrum)",
                    "earshot critique (23 scored metrics against reference profile)",
                ],
                "claims": ["CPU-only local audio measurement and reference comparison"],
            },
            {
                "id": "chaseai-yt/claudex-loop",
                "category": "cross-model-plan-and-review",
                "cli_invocations": [
                    "python scripts/validate.py",
                    "python -m unittest discover -s tests -v",
                ],
                "env_overrides": {
                    "DO_NOT_TRACK": "1",
                },
                "config": {
                    "telemetry": False,
                    "hook_reviewed": True,
                    "disable_hooks_flag": "read-only-review-sandbox",
                },
                "human_publish_only": True,
                "unknown_metric_placeholder": "{{your number}}",
                "deterministic_tools": [
                    "SHA256 plan approval fingerprint",
                    "read-only shell sandbox for reviews",
                ],
                "claims": ["four-phase cross-model review with SHA256 plan invalidation"],
            },
        ]
    }


def validate_suite(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    packs = data.get("packs")
    if not isinstance(packs, list) or not packs:
        return ["[SKILLPACK-000] 'packs' 必須為非空陣列"]

    for idx, pack in enumerate(packs):
        if not isinstance(pack, dict):
            errors.append(f"[SKILLPACK-000] packs[{idx}] 必須為物件")
            continue
        pid = str(pack.get("id") or f"pack#{idx}")

        # SKILLPACK-001: No-Bypass-Sandbox-Escalation
        invocations = pack.get("cli_invocations", [])
        if not isinstance(invocations, list):
            errors.append(f"[SKILLPACK-001] {pid}: cli_invocations 必須為陣列")
        else:
            for cmd in invocations:
                cmd_str = str(cmd)
                for flag in FORBIDDEN_BYPASS_FLAGS:
                    if flag in cmd_str:
                        errors.append(
                            f"[SKILLPACK-001] {pid}: 偵測到禁止的免審批／破沙盒旗標 '{flag}' 於指令：{cmd_str}"
                        )

        env_map = pack.get("env_overrides", {})
        if pid == "pbakaus/impeccable":
            live_agent = env_map.get("IMPECCABLE_LIVE_COPY_AGENT") if isinstance(env_map, dict) else None
            if live_agent not in ("chat", "off"):
                errors.append(
                    f"[SKILLPACK-001] {pid}: 必須設定 IMPECCABLE_LIVE_COPY_AGENT 為 'chat' 或 'off'，"
                    "以防止 Live Mode 逾時後自動以 --dangerously-bypass-approvals-and-sandbox 喚起背景 CLI"
                )

        # SKILLPACK-002: Hook-And-Telemetry-Gate
        cfg = pack.get("config", {})
        if not isinstance(cfg, dict):
            errors.append(f"[SKILLPACK-002] {pid}: config 必須為物件")
        else:
            if cfg.get("telemetry") is not False:
                errors.append(f"[SKILLPACK-002] {pid}: config.telemetry 必須顯式設為 false")
            if cfg.get("hook_reviewed") is not True:
                errors.append(f"[SKILLPACK-002] {pid}: config.hook_reviewed 必須為 true（確認已審查背景 Hook）")
            if not str(cfg.get("disable_hooks_flag") or "").strip():
                errors.append(f"[SKILLPACK-002] {pid}: 必須記錄 disable_hooks_flag 緊急停用機制")

        # SKILLPACK-003: Zero-Fabrication-Placeholder & Human-Publish Gate
        if pack.get("human_publish_only") is not True:
            errors.append(f"[SKILLPACK-003] {pid}: human_publish_only 必須為 true（禁止未經人工確認自動發文或推送）")
        placeholder = str(pack.get("unknown_metric_placeholder") or "")
        if "{{" not in placeholder or "}}" not in placeholder:
            errors.append(
                f"[SKILLPACK-003] {pid}: unknown_metric_placeholder 必須使用顯式模板佔位符（如 '{{{{your number}}}}'），禁止捏造數據"
            )

        # SKILLPACK-004: Deterministic-Linter-Backing & Anti-Overclaim
        det_tools = pack.get("deterministic_tools", [])
        if not isinstance(det_tools, list) or not det_tools:
            errors.append(f"[SKILLPACK-004] {pid}: deterministic_tools 不可為空，必須附帶確定性本地檢驗工具")
        claims = pack.get("claims", [])
        if isinstance(claims, list):
            for c in claims:
                c_low = str(c).lower()
                for banned in BANNED_OVERCLAIMS:
                    if banned in c_low:
                        errors.append(f"[SKILLPACK-004] {pid}: 偵測到誇大不實宣稱 '{banned}' 於：{c}")

    return errors


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="驗證第三方 Claude Code / Agent Skill 與 MCP 工具鏈之沙盒安全與決定性規範"
    )
    parser.add_argument("--config", type=Path, help="自訂 JSON 設定檔路徑（未提供則驗證內建五大工具基準套件）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出結果")
    args = parser.parse_args(argv)

    if args.config:
        data = json.loads(args.config.read_text(encoding="utf-8"))
    else:
        data = default_suite()

    errors = validate_suite(data)
    ok = len(errors) == 0

    if args.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "pack_count": len(data.get("packs", [])) if isinstance(data.get("packs"), list) else 0,
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if ok:
            print(f"[PASS] Agent Skill Pack 安全與決定性審計通過（共檢驗 {len(data['packs'])} 組工具鏈）。")
        else:
            print("[FAIL] Agent Skill Pack 安全與決定性審計失敗：")
            for err in errors:
                print(f"  - {err}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
