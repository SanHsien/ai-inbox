#!/usr/bin/env python3
"""
tools/verify_pstack_and_fullstack_specs.py
pstack 五大工程 Playbooks、Claude 官方外掛評測與全端商業建站規範之「外部裁判」結構驗證器（純 Python stdlib）。

驗證目標：
1. docs/pstack-agent-playbooks.md：
   - 包含 /poteto-mode 路由器規格與跨 CLI (Claude Code, Codex CLI, Antigravity) 提示詞規格；
   - 完整定義五大核心 Playbooks（Bug-fix, Feature, Refactoring, Investigation, Performance）；
   - 包含至少 3 個端到端多 CLI 實例對照（Bug-fix, Feature, Refactoring 等）。
2. docs/claude-plugins-official-review.md：
   - 包含 8 款精選推薦外掛（pr-review-toolkit, security-guidance, skill-creator, etc.）；
   - 包含 6 款排除外掛（imessage, swift-lsp, csharp-lsp/jdtls, etc.）；
   - 包含明確之「未查證」(Unverified) 誠實標註與分析理由。
3. templates/fullstack-website-builder-skill.md：
   - 包含資料持久化軟刪除（deleted_at / Soft Delete）；
   - 包含伺服器端重算之不可變定價快照（pricing_snapshot）；
   - 包含不可變事件審計流水帳（registration_events）；
   - 包含五大訂單核心狀態機（pending, paid, verified, canceled, refunded）；
   - 包含 Webhook 簽名校驗與金額雙重對帳（Raw Body, Signature, Amount Reconciliation, Idempotency）。
4. templates/subject-inventory-argument-writing-prompt.md：
   - 包含主體資產盤點（Subject Inventory）前置規格與事實特徵要素；
   - 包含 Claim + Proof 爭點論證寫作規範（主張、客觀證據、排版承載）；
   - 包含完整落地驗收示範（盤點清單與區塊論證表格）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _judge_common import (  # noqa: E402
    doc_guard,
    ensure_utf8_output,
    find_repo_root as _common_find_repo_root,
    report_results,
)

# ----------------------------------------------------------------------
# 規則與常數定義
# ----------------------------------------------------------------------

# 1. pstack playbooks 規格要求
REQUIRED_PLAYBOOKS: List[Tuple[str, str]] = [
    ("Bug-fix", "bug-fix.md"),
    ("Feature", "feature.md"),
    ("Refactoring", "refactoring.md"),
    ("Investigation", "investigation.md"),
    ("Performance", "perf-issue.md"),
]

REQUIRED_PSTACK_CLIS: List[str] = [
    "Claude Code",
    "Codex CLI",
    "Antigravity",
]

# 2. Claude plugins 評測要求
REQUIRED_RECOMMENDED_PLUGINS: List[str] = [
    "pr-review-toolkit",
    "security-guidance",
    "skill-creator",
    "claude-md-management",
    "pyright-lsp",
    "typescript-lsp",
    "session-report",
    "code-simplifier",
]

REQUIRED_EXCLUDED_PLUGINS: List[str] = [
    "imessage",
    "swift-lsp",
    "csharp-lsp",
    "blackrock-advisor-center-plugin",
    "chronograph-gp",
    "laravel-boost",
]

# 3. 全端建站技能規格要求
REQUIRED_ORDER_STATUSES: List[str] = [
    "pending",
    "paid",
    "verified",
    "canceled",
    "refunded",
]

WEBHOOK_RECONCILIATION_KEYWORDS: List[Tuple[str, str]] = [
    ("Raw Body", "原始字串"),
    ("簽名驗證", "Signature"),
    ("金額雙重對帳", "Amount Reconciliation"),
    ("冪等性", "Idempotency"),
]

# 4. 主體資產盤點與論證寫作要求
SUBJECT_INVENTORY_DIMENSIONS: List[str] = [
    "地理與物理座標",
    "時間尺度",
    "精確數字",
    "感官與實體材質",
    "負向邊界",
    "核心人物",
]

ARGUMENT_WRITING_ELEMENTS: List[Tuple[str, str]] = [
    ("爭點主張", "Claim"),
    ("客觀證據", "Proof"),
    ("排版", "Visual"),
]


# ----------------------------------------------------------------------
# 輔助安全讀取函式（防範 Linux CI ENAMETOOLONG）
# ----------------------------------------------------------------------

def load_content(source: Union[str, Path]) -> str:
    """
    載入內容：支援直接傳入內文字串或檔案路徑。
    特別注意：切勿對多行內文字串直接呼叫 Path(arg).exists()，
    應先判斷 isinstance(arg, Path) 或 '\n' not in arg and len(arg) < 240，
    以避免在 Linux CI / Windows 上觸發 ENAMETOOLONG 或路徑解析異常。
    """
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8")
    if isinstance(source, str):
        if "\n" not in source and len(source) < 240:
            try:
                p = Path(source)
                if p.is_file():
                    return p.read_text(encoding="utf-8")
            except (OSError, ValueError):
                pass
        return source
    raise TypeError(f"不支援的型別：{type(source)}")


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄（共用實作見 _judge_common）。"""
    return _common_find_repo_root(start, markers=('notes', 'docs'), anchor=Path(__file__))


# ----------------------------------------------------------------------
# 核心驗證函式
# ----------------------------------------------------------------------

@doc_guard
def verify_pstack_playbooks(source: Union[str, Path]) -> List[str]:
    """
    驗證 docs/pstack-agent-playbooks.md：
    - 包含 `/poteto-mode` 總控動態路由器章節與說明；
    - 完整定義五大核心 Playbooks（Bug-fix, Feature, Refactoring, Investigation, Performance）；
    - 包含跨 CLI（Claude Code, Codex CLI, Antigravity）提示詞規格；
    - 包含至少 3 個多 CLI 實例對照（End-to-End Walkthroughs）。
    """
    text = load_content(source)
    errors: List[str] = []
    lines = text.strip().splitlines()
    if not lines:
        return ["檔案內容為空"]

    # 1. /poteto-mode 路由器驗證
    has_router_heading = bool(re.search(r"##\s+3\.\s+.*(?:\/poteto-mode|總控動態路由器)", text))
    has_router_mention = "/poteto-mode" in text and ("路由器" in text or "Dispatcher" in text)
    if not (has_router_heading or has_router_mention):
        errors.append("缺少 `/poteto-mode` 總控動態路由器專屬章節或規格定義")

    # 2. 跨 CLI 提示詞規格驗證
    missing_clis: List[str] = []
    for cli in REQUIRED_PSTACK_CLIS:
        if cli not in text:
            missing_clis.append(cli)
    if missing_clis:
        errors.append(f"缺少以下 CLI 平台之調用或提示詞規格：{', '.join(missing_clis)}")

    # 3. 五大核心 Playbooks 規格驗證
    missing_playbooks: List[str] = []
    for name, filename in REQUIRED_PLAYBOOKS:
        has_name = bool(re.search(rf"{name}\s*Playbook", text, re.IGNORECASE))
        has_file = filename in text
        if not (has_name or has_file):
            missing_playbooks.append(f"{name} ({filename})")
    if missing_playbooks:
        errors.append(f"缺少以下核心 Playbook 規格：{', '.join(missing_playbooks)}")

    # 4. 至少 3 個多 CLI 實例對照驗證
    example_matches = re.findall(r"###\s*實例\s*(\d+)[:：]", text)
    if len(example_matches) < 3:
        alt_matches = re.findall(r"實例\s*([123])[:：]", text)
        found_count = len(set(example_matches + alt_matches))
        if found_count < 3:
            errors.append(
                f"多 CLI 實例對照數量不足（需至少 3 個實例，實際僅偵測到 {found_count} 個）"
            )

    return errors


@doc_guard
def verify_claude_plugins_review(source: Union[str, Path]) -> List[str]:
    """
    驗證 docs/claude-plugins-official-review.md：
    - 包含 8 款精選推薦外掛；
    - 包含 6 款排除外掛；
    - 包含明確之「未查證」(Unverified) 誠實標註與分析理由。
    """
    text = load_content(source)
    errors: List[str] = []
    lines = text.strip().splitlines()
    if not lines:
        return ["檔案內容為空"]

    # 1. 8 款推薦外掛校驗
    missing_recommended: List[str] = []
    for plugin in REQUIRED_RECOMMENDED_PLUGINS:
        pattern = rf"`{re.escape(plugin)}`"
        if not re.search(pattern, text):
            missing_recommended.append(plugin)
    if missing_recommended:
        errors.append(f"推薦外掛清單缺少以下項目：{', '.join(missing_recommended)}")

    # 2. 6 款排除外掛校驗
    missing_excluded: List[str] = []
    for plugin in REQUIRED_EXCLUDED_PLUGINS:
        pattern = rf"`{re.escape(plugin)}`"
        if not re.search(pattern, text):
            missing_excluded.append(plugin)
    if missing_excluded:
        errors.append(f"排除外掛清單缺少以下項目：{', '.join(missing_excluded)}")

    # 3. 「未查證」(Unverified) 誠實標註驗證
    has_unverified_section = bool(re.search(r"##\s+4\.\s+.*未查證.*(?:Unverified)?", text))
    has_unverified_tags = "[未查證]" in text or "未查證" in text
    if not (has_unverified_section and has_unverified_tags):
        errors.append("缺少明確之「未查證 (Unverified)」段落或標註")
    else:
        unverified_examples = ["vsql-extension-builder", "zocks-advisor", "chronograph"]
        if not any(item in text for item in unverified_examples):
            errors.append("未查證段落缺少具體案例（如 vsql-extension-builder, zocks-advisor, chronograph）之未查證理由")

    return errors


@doc_guard
def verify_fullstack_website_builder(source: Union[str, Path]) -> List[str]:
    """
    驗證 templates/fullstack-website-builder-skill.md：
    - 資料持久化軟刪除（deleted_at / Soft Delete）；
    - 伺服器端重算之不可變定價快照（pricing_snapshot）；
    - 不可變事件審計流水帳（registration_events）；
    - 五大訂單核心狀態機（pending, paid, verified, canceled, refunded）；
    - Webhook 簽名校驗與金額雙重對帳（Raw Body, Signature, Amount Reconciliation, Idempotency）。
    """
    text = load_content(source)
    errors: List[str] = []
    lines = text.strip().splitlines()
    if not lines:
        return ["檔案內容為空"]

    # 1. 軟刪除 (Soft Delete) 校驗
    has_soft_delete = "deleted_at" in text and ("軟刪除" in text or "Soft Delete" in text)
    if not has_soft_delete:
        errors.append("缺少軟刪除（Soft Delete / `deleted_at`）資料庫綱要與業務原則說明")

    # 2. 定價快照 (Pricing Snapshot) 校驗
    has_pricing_snapshot = (
        "pricing_snapshot" in text
        and "final_payable_amount" in text
        and ("定價快照" in text or "Pricing Snapshot" in text)
    )
    if not has_pricing_snapshot:
        errors.append("缺少不可變定價快照（`pricing_snapshot` / `final_payable_amount`）結構與伺服器重算規範")

    # 3. 事件流水帳 (Event Ledger) 校驗
    has_event_ledger = "registration_events" in text and ("事件審計" in text or "Event Ledger" in text or "流水帳" in text)
    if not has_event_ledger:
        errors.append("缺少不可變訂單事件流水帳（`registration_events` / Event Ledger）綱要與審計規範")

    # 4. 訂單狀態機 (Order State Machine) 校驗
    missing_statuses: List[str] = []
    for st in REQUIRED_ORDER_STATUSES:
        pattern = rf"\b{st}\b"
        if not re.search(pattern, text):
            missing_statuses.append(st)
    if missing_statuses:
        errors.append(f"訂單狀態機缺少以下核心狀態：{', '.join(missing_statuses)}")

    # 5. Webhook 簽名校驗與金額對帳
    missing_webhook_guards: List[str] = []
    for kw_zh, kw_en in WEBHOOK_RECONCILIATION_KEYWORDS:
        if kw_zh not in text and kw_en not in text:
            missing_webhook_guards.append(f"{kw_zh} / {kw_en}")
    if missing_webhook_guards:
        errors.append(f"Webhook 安全驗證守則缺少以下關鍵防線：{', '.join(missing_webhook_guards)}")

    return errors


@doc_guard
def verify_subject_inventory_prompt(source: Union[str, Path]) -> List[str]:
    """
    驗證 templates/subject-inventory-argument-writing-prompt.md：
    - 主體資產盤點（Subject Inventory）前置規格與事實特徵要素；
    - Claim + Proof 爭點論證寫作規範（主張、客觀證據、排版承載）；
    - 完整落地驗收示範（盤點清單與區塊論證表格）。
    """
    text = load_content(source)
    errors: List[str] = []
    lines = text.strip().splitlines()
    if not lines:
        return ["檔案內容為空"]

    # 1. 主體資產盤點 (Subject Inventory) 校驗
    has_subject_inventory = (
        "主體資產盤點" in text
        and "Subject Inventory" in text
    )
    if not has_subject_inventory:
        errors.append("缺少「主體資產盤點 (Subject Inventory)」前置階段核心定義")

    missing_dimensions: List[str] = []
    for dim in SUBJECT_INVENTORY_DIMENSIONS:
        if dim not in text:
            missing_dimensions.append(dim)
    if missing_dimensions:
        errors.append(f"主體資產盤點缺少以下特徵維度指引：{', '.join(missing_dimensions)}")

    # 2. 爭點論證寫作 (Claim + Proof) 校驗
    missing_elements: List[str] = []
    for kw_zh, kw_en in ARGUMENT_WRITING_ELEMENTS:
        if kw_zh not in text and kw_en not in text:
            missing_elements.append(f"{kw_zh} / {kw_en}")
    if missing_elements:
        errors.append(f"爭點論證寫作缺少以下核心要素要求：{', '.join(missing_elements)}")

    # 3. 落地示範（主題、階段一盤點清單、階段二區塊論證表格）
    has_demo_topic = "主題：" in text or "驗收示範" in text
    has_demo_section_table = (
        "| 區塊" in text
        and "爭點主張" in text
        and "硬核客觀證據" in text
    )
    if not (has_demo_topic and has_demo_section_table):
        errors.append("缺少完整主題落地示範（包含階段一盤點清單與階段二區塊論證 Markdown 表格）")

    return errors


# ----------------------------------------------------------------------
# 外部裁判整合呼叫與 CLI 進入點
# ----------------------------------------------------------------------

TARGET_SPECS: List[Tuple[str, callable]] = [
    ("docs/pstack-agent-playbooks.md", verify_pstack_playbooks),
    ("docs/claude-plugins-official-review.md", verify_claude_plugins_review),
    ("templates/fullstack-website-builder-skill.md", verify_fullstack_website_builder),
    ("templates/subject-inventory-argument-writing-prompt.md", verify_subject_inventory_prompt),
]


def verify_all_specs(repo_root: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """執行全數外部裁判規格驗證。"""
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    for rel_path, verifier in TARGET_SPECS:
        full_path = root / rel_path
        if not full_path.exists():
            results[rel_path] = [f"目標檔案不存在：{rel_path}"]
        else:
            results[rel_path] = verifier(full_path)

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_output()
    parser = argparse.ArgumentParser(
        description="pstack Playbooks、Claude 外掛評測與全端建站規範之外部裁判結構驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 notes/ 與 docs/ 之根目錄）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(f"[*] 執行外部裁判規格結構校驗，專案根目錄：{root}")

    all_passed, results = verify_all_specs(root)

    return report_results(
        results,
        success_msg='全數 pstack、外掛評測與全端商業建站規格文件均通過外部裁判結構驗證！',
        fail_label='規格缺陷',
        ok_label='結構與規格完全相符',
        fail_msg='外部裁判驗證未通過，請依上述錯誤修正文件。',
    )


if __name__ == "__main__":
    sys.exit(main())
