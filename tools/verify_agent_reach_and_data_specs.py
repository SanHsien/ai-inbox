#!/usr/bin/env python3
"""
tools/verify_agent_reach_and_data_specs.py
Agent-Reach 16 平台路由範本、Public APIs 檢索技能與健康存摺匯出規格之「外部裁判」結構驗證器（純 Python stdlib）。

驗證目標：
1. templates/agent-reach/SKILL.md 與 templates/agent-reach/references/：
   - 驗證 7 大領域分類 references 檔案齊全（search, social, career, dev, web, video, finance）；
   - 驗證路由表結構完整、覆蓋 7 大分類，且所有 markdown 參照無斷鏈。
2. templates/public-apis-search-skill.md 與 docs/free-public-apis.md：
   - 驗證 Auth: No、CORS: Yes、HTTPS 三道篩選門檻；
   - 驗證 462 筆公開端點與 42 類別目錄索引、表格欄位結構與每筆資料符合零金鑰/跨域放行條件。
3. docs/health-bank-export-format.md、templates/health-bank-dashboard-prompt.md 與 templates/health-report-pdf-prompt.md：
   - 驗證離線脫敏欄位規範（姓名、身分證、生日、電話、地址、病歷號、健保卡就醫序號，以及純本地離線、不得入 git repo）；
   - 驗證民國年轉 ISO 規範（民國年 + 1911、<欄位>_iso）；
   - 驗證醫療免責聲明（不下確定診斷、不調整藥物、非醫療診斷、需諮詢醫師）。
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
    strip_html_comments,
)

# ---------------------------------------------------------------------------
# 常數定義
# ---------------------------------------------------------------------------

REQUIRED_AGENT_REACH_DOMAINS: List[Tuple[str, str]] = [
    ("search", "search.md"),
    ("social", "social.md"),
    ("career", "career.md"),
    ("dev", "dev.md"),
    ("web", "web.md"),
    ("video", "video.md"),
    ("finance", "finance.md"),
]

REQUIRED_PUBLIC_APIS_GATING = [
    ("Auth: No", re.compile(r"Auth:\s*No|零金鑰免註冊", re.IGNORECASE)),
    ("CORS: Yes", re.compile(r"CORS:\s*Yes|瀏覽器跨域放行", re.IGNORECASE)),
    ("HTTPS", re.compile(r"HTTPS(?::\s*Yes)?|安全傳輸", re.IGNORECASE)),
]

TOTAL_PUBLIC_APIS_COUNT = 462
TOTAL_PUBLIC_APIS_CATEGORIES = 42

REQUIRED_HEALTH_PII_KEYWORDS = [
    ("姓名", "name"),
    ("身分證", "id_number"),
    ("出生日期/生日", "birth_date"),
    ("電話", "phone"),
    ("地址", "address"),
    ("病歷號", "medical_record_no"),
    ("健保卡就醫序號", "card_seq"),
]


# ---------------------------------------------------------------------------
# 輔助函式：安全路徑與文字解析（防範 Linux CI ENAMETOOLONG）
# ---------------------------------------------------------------------------

def _is_path_string(val: str) -> bool:
    """判斷字串是否可能為單行路徑，防範長字串呼叫 Path(val).exists() 觸發 ENAMETOOLONG。"""
    return "\n" not in val and "\r" not in val and len(val) < 240


def _resolve_content_and_path_raw(
    arg: Union[Path, str],
    default_subpath: Optional[str] = None,
) -> Tuple[str, Optional[Path]]:
    """
    安全解析輸入內容與來源 Path。
    若 arg 為多行文字，直接回傳文字與 None，絕不呼叫 Path(arg).exists()。
    """
    if isinstance(arg, Path):
        if arg.is_file():
            return arg.read_text(encoding="utf-8"), arg
        elif arg.is_dir() and default_subpath:
            target = arg / default_subpath
            if target.is_file():
                return target.read_text(encoding="utf-8"), target
            return "", target
        return "", arg

    if isinstance(arg, str):
        if _is_path_string(arg):
            try:
                p = Path(arg)
                if p.is_file():
                    return p.read_text(encoding="utf-8"), p
                elif p.is_dir() and default_subpath:
                    target = p / default_subpath
                    if target.is_file():
                        return target.read_text(encoding="utf-8"), target
                    return "", target
            except OSError:
                pass
        # 多行字串或不存在之路徑字串，視為純文字內容
        return arg, None

    raise TypeError(f"輸入型態必須為 Path 或 str，實際為：{type(arg)}")


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄（共用實作見 _judge_common）。"""
    return _common_find_repo_root(start, markers=('notes', 'docs'), anchor=Path(__file__))


def _resolve_content_and_path(
    arg: Union[Path, str],
    default_subpath: Optional[str] = None,
) -> Tuple[str, Optional[Path]]:
    """同 raw 版本，但回傳前剝除 HTML 註解（藏在註解內的關鍵字不算數）。"""
    text, path = _resolve_content_and_path_raw(arg, default_subpath)
    return strip_html_comments(text), path


# ---------------------------------------------------------------------------
# 1. Agent-Reach 16 平台路由與 7 大領域 References 驗證
# ---------------------------------------------------------------------------

def verify_agent_reach_specs(
    skill_input: Union[Path, str],
    references_dir: Optional[Union[Path, str]] = None,
) -> List[str]:
    """
    驗證 templates/agent-reach/SKILL.md 與 references/：
    - 7 大領域分類 references 檔案齊全（search, social, career, dev, web, video, finance）；
    - 路由表包含 7 大分類且參照無斷鏈；
    - 詳細文檔段落包含 7 大領域清單。
    """
    errors: List[str] = []
    text, skill_path = _resolve_content_and_path(skill_input, default_subpath="templates/agent-reach/SKILL.md")

    if not text.strip():
        return ["templates/agent-reach/SKILL.md 內容為空或檔案不存在"]

    # 推導 references 目錄
    resolved_ref_dir: Optional[Path] = None
    if references_dir is not None:
        if isinstance(references_dir, Path):
            resolved_ref_dir = references_dir
        elif isinstance(references_dir, str) and _is_path_string(references_dir):
            try:
                p = Path(references_dir)
                if p.is_dir():
                    resolved_ref_dir = p
            except OSError:
                pass
    elif skill_path is not None:
        potential_dir = skill_path.parent / "references"
        if potential_dir.is_dir():
            resolved_ref_dir = potential_dir

    # (A) 驗證 references 目錄檔案齊全度
    if resolved_ref_dir is not None:
        if not resolved_ref_dir.is_dir():
            errors.append(f"找不到 references 目錄：{resolved_ref_dir}")
        else:
            for domain, filename in REQUIRED_AGENT_REACH_DOMAINS:
                ref_file = resolved_ref_dir / filename
                if not ref_file.is_file():
                    errors.append(f"缺少必備 references 檔案：{filename}（領域：{domain}）")
                elif ref_file.stat().st_size == 0:
                    errors.append(f"references 檔案內容為空：{filename}（領域：{domain}）")

    # (B) 驗證路由表（Table）結構與斷鏈檢查
    has_routing_header = bool(re.search(r"##\s+.*路由表", text))
    if not has_routing_header:
        errors.append("SKILL.md 缺少「## 路由表」章節標題")

    # 提取路由表所有列：格式如 | 意圖 | 分類 | [doc](link) |
    # 例：| 网页搜索/代码搜索 | search | [references/search.md](references/search.md) |
    route_row_pattern = re.compile(
        r"\|\s*([^|]+?)\s*\|\s*([a-zA-Z0-9_-]+)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|"
    )
    found_routes: Dict[str, str] = {}
    for match in route_row_pattern.finditer(text):
        _intent, domain, _label, target_link = match.groups()
        found_routes[domain.strip()] = target_link.strip()

    # 校驗 7 大領域分類是否全數登錄在路由表中
    for domain, filename in REQUIRED_AGENT_REACH_DOMAINS:
        if domain not in found_routes:
            errors.append(f"路由表缺少「{domain}」分類條目")
        else:
            link = found_routes[domain]
            expected_ref = f"references/{filename}"
            if filename not in link:
                errors.append(f"路由表「{domain}」分類之參照連結異常：期望包含 '{expected_ref}'，實際為 '{link}'")

            # 斷鏈檢查（若能定位檔案系統）
            if resolved_ref_dir is not None:
                # 連結形式可能是 references/search.md 或 search.md
                link_clean = link.split("#")[0].split("?")[0]
                target_file = resolved_ref_dir.parent / link_clean if link_clean.startswith("references/") else resolved_ref_dir / link_clean
                if not target_file.is_file():
                    errors.append(f"路由表參照斷鏈：找不到檔案 '{link}'（領域：{domain}）")

    # (C) 驗證詳細文檔段落包含 7 大分類
    has_detail_docs_heading = bool(re.search(r"##\s+.*(?:詳細文檔|详细文档)", text))
    if not has_detail_docs_heading:
        errors.append("SKILL.md 缺少「## 詳細文檔 / ## 详细文档」章節標題")
    else:
        for domain, filename in REQUIRED_AGENT_REACH_DOMAINS:
            expected_ref = f"references/{filename}"
            if expected_ref not in text:
                errors.append(f"詳細文檔段落缺少「{expected_ref}」連結（領域：{domain}）")

    return errors


# ---------------------------------------------------------------------------
# 2. Public APIs 檢索技能與 free-public-apis.md 結構驗證
# ---------------------------------------------------------------------------

@doc_guard
def verify_public_apis_search_skill(skill_input: Union[Path, str]) -> List[str]:
    """
    驗證 templates/public-apis-search-skill.md：
    - 包含三大檢索門檻（Auth: No, CORS: Yes, HTTPS）；
    - 定義 name: public-apis-search 與 search_public_apis 工具規格；
    - 參照 docs/free-public-apis.md。
    """
    errors: List[str] = []
    text, _ = _resolve_content_and_path(skill_input, default_subpath="templates/public-apis-search-skill.md")

    if not text.strip():
        return ["templates/public-apis-search-skill.md 內容為空或檔案不存在"]

    # 1. 驗證三大門檻
    for label, pattern in REQUIRED_PUBLIC_APIS_GATING:
        if not pattern.search(text):
            errors.append(f"public-apis-search-skill 缺少必備篩選門檻規範：「{label}」")

    # 2. 驗證 Frontmatter / 技能定義
    if "name: public-apis-search" not in text:
        errors.append("public-apis-search-skill 缺少技能名稱宣告「name: public-apis-search」")

    # 3. 驗證資料庫參照
    if "docs/free-public-apis.md" not in text:
        errors.append("public-apis-search-skill 缺少對索引庫「docs/free-public-apis.md」之明確參照")

    # 4. 驗證 MCP 工具宣告
    if "search_public_apis" not in text:
        errors.append("public-apis-search-skill 缺少 MCP 工具「search_public_apis」定義")

    return errors


@doc_guard
def verify_free_public_apis_index(index_input: Union[Path, str]) -> List[str]:
    """
    驗證 docs/free-public-apis.md：
    - 篩選條件宣告包含 Auth: No 與 CORS: Yes；
    - 宣告與實際結構完全相符：462 筆端點、42 個分類；
    - 目錄索引（TOC）包含 42 個分類且加總筆數為 462；
    - 表格資料行共有 462 筆，且每筆 Auth 均為 No、CORS 均為 Yes、包含 HTTPS 欄位。
    """
    errors: List[str] = []
    text, _ = _resolve_content_and_path(index_input, default_subpath="docs/free-public-apis.md")

    if not text.strip():
        return ["docs/free-public-apis.md 內容為空或檔案不存在"]

    # 1. 篩選條件與筆數宣告校驗
    if "Auth: No" not in text or "CORS: Yes" not in text:
        errors.append("docs/free-public-apis.md 缺少「Auth: No 且 CORS: Yes」篩選條件宣告")

    has_count_declaration = bool(
        re.search(r"462\s*個公開端點.*42\s*個分類|462\s*筆.*42\s*類別", text)
    )
    if not has_count_declaration:
        errors.append("docs/free-public-apis.md 缺少「462 個公開端點，跨 42 個分類」之數據規格宣告")

    # 2. 目錄索引（TOC）校驗：- [Category](#anchor) (count)
    toc_pattern = re.compile(r"^-\s+\[([^\]]+)\]\((#[^\)]+)\)\s+\((\d+)\)", re.MULTILINE)
    toc_matches = toc_pattern.findall(text)
    toc_categories_count = len(toc_matches)
    toc_total_sum = sum(int(count) for _cat, _anchor, count in toc_matches)

    if toc_categories_count != TOTAL_PUBLIC_APIS_CATEGORIES:
        errors.append(
            f"目錄索引分類數異常：期望 {TOTAL_PUBLIC_APIS_CATEGORIES} 個分類，實際解析出 {toc_categories_count} 個"
        )
    if toc_total_sum != TOTAL_PUBLIC_APIS_COUNT:
        errors.append(
            f"目錄索引筆數加總異常：期望 {TOTAL_PUBLIC_APIS_COUNT} 筆，實際加總為 {toc_total_sum} 筆"
        )

    # 3. 分類詳細清單結構與表格資料列解析
    api_rows: List[List[str]] = []
    lines = text.splitlines()
    for line in lines:
        line_s = line.strip()
        # 匹配表格資料列：以 | [ 開頭
        if line_s.startswith("| [") and "|" in line_s[3:]:
            parts = [p.strip() for p in line_s.split("|")[1:-1]]
            # 欄位應為：API、說明、驗證 (Auth)、HTTPS、跨域 (CORS)
            if len(parts) >= 5:
                api_rows.append(parts)

    actual_row_count = len(api_rows)
    if actual_row_count != TOTAL_PUBLIC_APIS_COUNT:
        errors.append(
            f"API 詳細表格資料列數異常：期望 {TOTAL_PUBLIC_APIS_COUNT} 筆，實際解析出 {actual_row_count} 筆"
        )

    # 檢查每筆資料的 Auth: No 與 CORS: Yes 門檻
    invalid_auth_rows: List[str] = []
    invalid_cors_rows: List[str] = []
    missing_https_rows: List[str] = []

    for parts in api_rows:
        api_name = parts[0]
        auth_val = parts[2]
        https_val = parts[3]
        cors_val = parts[4]

        if auth_val != "No":
            invalid_auth_rows.append(f"{api_name} (Auth: {auth_val})")
        if cors_val != "Yes":
            invalid_cors_rows.append(f"{api_name} (CORS: {cors_val})")
        if not https_val:
            missing_https_rows.append(api_name)

    if invalid_auth_rows:
        errors.append(
            f"發現 {len(invalid_auth_rows)} 筆 API 未通過 'Auth: No' 門檻，例如：{invalid_auth_rows[:3]}"
        )
    if invalid_cors_rows:
        errors.append(
            f"發現 {len(invalid_cors_rows)} 筆 API 未通過 'CORS: Yes' 門檻，例如：{invalid_cors_rows[:3]}"
        )
    if missing_https_rows:
        errors.append(
            f"發現 {len(missing_https_rows)} 筆 API 缺少 HTTPS 欄位資料，例如：{missing_https_rows[:3]}"
        )

    return errors


def verify_public_apis_specs(
    skill_input: Union[Path, str],
    index_input: Union[Path, str],
) -> List[str]:
    """整合驗證 Public APIs 檢索技能與索引手冊。"""
    errors: List[str] = []
    errors.extend(verify_public_apis_search_skill(skill_input))
    errors.extend(verify_free_public_apis_index(index_input))
    return errors


# ---------------------------------------------------------------------------
# 3. 健康存摺匯出格式與 Prompt 範本規格驗證
# ---------------------------------------------------------------------------

@doc_guard
def verify_health_bank_format_doc(format_input: Union[Path, str]) -> List[str]:
    """
    驗證 docs/health-bank-export-format.md：
    - 離線脫敏欄位規範（包含姓名、身分證字號、出生日期、電話、地址、病歷號、健保卡就醫序號一律遮蔽）；
    - 資料安全性原則（不得放進任何 git repo、私人資料夾）；
    - 民國年轉 ISO 規範（民國年 + 1911、<欄位>_iso）；
    - 醫療免責界線（不下確定診斷、不建議增減停用藥物）。
    """
    errors: List[str] = []
    text, _ = _resolve_content_and_path(format_input, default_subpath="docs/health-bank-export-format.md")

    if not text.strip():
        return ["docs/health-bank-export-format.md 內容為空或檔案不存在"]

    # 1. 安全原則：不得進 git repo
    has_git_prohibition = bool(re.search(r"不得放進任何\s*git\s*repo|repo\s*外.*私人資料夾", text))
    if not has_git_prohibition:
        errors.append("docs/health-bank-export-format.md 缺少「原始檔與解析結果不得放進任何 git repo」之安全原則")

    # 2. 脫敏欄位遮蔽校驗
    has_redaction_heading = bool(re.search(r"##\s+7\.\s+脫敏欄位", text))
    if not has_redaction_heading:
        errors.append("docs/health-bank-export-format.md 缺少「## 7. 脫敏欄位」章節")

    missing_pii: List[str] = []
    for label_zh, _keyword in REQUIRED_HEALTH_PII_KEYWORDS:
        # 部分標籤有多關鍵字（如「出生日期/生日」）
        sub_kws = label_zh.split("/")
        if not any(kw in text for kw in sub_kws):
            missing_pii.append(label_zh)
    if missing_pii:
        errors.append(f"docs/health-bank-export-format.md 脫敏遮蔽清單缺少關鍵個資欄位：{missing_pii}")

    # 3. 日期民國年轉 ISO 規範校驗
    has_roc_date_rule = bool(
        re.search(r"民國年.*\+?\s*1911|112/10/12\s*=\s*2023-10-12", text)
    )
    has_iso_field_rule = "_iso" in text
    if not (has_roc_date_rule and has_iso_field_rule):
        errors.append("docs/health-bank-export-format.md 缺少民國年轉西元 ISO（_iso 欄位）轉換規範")

    # 4. 醫療免責聲明與行為邊界校驗
    has_medical_boundary = bool(
        re.search(r"不下確定診斷.*不建議增減|不建議增減.*停用.*更換藥物", text)
    )
    if not has_medical_boundary:
        errors.append("docs/health-bank-export-format.md 缺少「不下確定診斷、不建議增減/停用/更換藥物」之醫療邊界規範")

    return errors


@doc_guard
def verify_health_bank_dashboard_prompt(dashboard_input: Union[Path, str]) -> List[str]:
    """
    驗證 templates/health-bank-dashboard-prompt.md：
    - 純本地離線運算原則（100% Client-Side Privacy、嚴禁向外部伺服器發送）；
    - 醫療免責聲明（Medical Disclaimer、不構成任何醫療診斷、指標異常諮詢專業主治醫師）；
    - 脫敏 JSON Schema 規範（包含 rules_applied 與核心遮蔽標籤）。
    """
    errors: List[str] = []
    text, _ = _resolve_content_and_path(dashboard_input, default_subpath="templates/health-bank-dashboard-prompt.md")

    if not text.strip():
        return ["templates/health-bank-dashboard-prompt.md 內容為空或檔案不存在"]

    # 1. 本地離線隱私
    has_offline_privacy = bool(
        re.search(r"純本地離線運算|100%\s*Client-Side Privacy|嚴禁向任何外部伺服器發送", text)
    )
    if not has_offline_privacy:
        errors.append("templates/health-bank-dashboard-prompt.md 缺少純本地離線隱私保護（Client-Side Privacy）鐵律")

    # 2. 醫療免責聲明
    has_disclaimer = bool(
        re.search(r"醫療免責聲明|Medical Disclaimer", text)
        and re.search(r"不構成任何醫療診斷", text)
        and re.search(r"諮詢專業主治醫師", text)
    )
    if not has_disclaimer:
        errors.append("templates/health-bank-dashboard-prompt.md 缺少頁首/頁尾強制醫療免責聲明規範")

    # 3. 脫敏資料結構契約
    has_schema_rules = bool(
        re.search(r'"rules_applied"', text)
        and re.search(r'"name"|"id_number"|"birth_date"', text)
    )
    if not has_schema_rules:
        errors.append("templates/health-bank-dashboard-prompt.md 缺少脫敏數據結構契約（rules_applied）")

    return errors


def verify_health_report_pdf_prompt(pdf_input: Union[Path, str]) -> List[str]:
    """
    驗證 templates/health-report-pdf-prompt.md：
    - 資料安全性提醒（解壓至私人資料夾、不要放進 repo）；
    - 角色定位與醫療免責（助理不是醫師、不下確定診斷、不調整藥物）；
    - 嚴格個資脫敏規範（不寫姓名、身分證、生日、電話、地址、病歷號、健保卡就醫序號）；
    - 參照 docs/health-bank-export-format.md 判讀規則。
    """
    errors: List[str] = []
    text, _ = _resolve_content_and_path(pdf_input, default_subpath="templates/health-report-pdf-prompt.md")

    if not text.strip():
        return ["templates/health-report-pdf-prompt.md 內容為空或檔案不存在"]

    # 1. 安全原則
    has_repo_warning = bool(re.search(r"私人資料夾.*不要放進\s*repo|repo\s*以外的私人資料夾", text))
    if not has_repo_warning:
        errors.append("templates/health-report-pdf-prompt.md 缺少「報告存在私人資料夾，不要放進 repo」之安全提醒")

    # 2. 角色定位與醫療免責
    has_role_disclaimer = bool(
        re.search(r"不是醫師", text)
        and re.search(r"不下確定診斷", text)
        and re.search(r"不調整藥物|不建議增加、減少、停用或更換任何藥物", text)
    )
    if not has_role_disclaimer:
        errors.append("templates/health-report-pdf-prompt.md 缺少「不是醫師、不下確定診斷、不調整藥物」之核心免責界線")

    # 3. 嚴格個資不寫規範
    missing_pii: List[str] = []
    for label_zh, _kw in REQUIRED_HEALTH_PII_KEYWORDS:
        sub_kws = label_zh.split("/")
        if not any(kw in text for kw in sub_kws):
            missing_pii.append(label_zh)
    if missing_pii:
        errors.append(f"templates/health-report-pdf-prompt.md 報告規則缺少禁止寫出之個資欄位：{missing_pii}")

    # 4. 參照格式文件
    if "docs/health-bank-export-format.md" not in text:
        errors.append("templates/health-report-pdf-prompt.md 缺少對判讀格式文件「docs/health-bank-export-format.md」之參照")

    return errors


def verify_health_bank_specs(
    format_input: Union[Path, str],
    dashboard_input: Union[Path, str],
    pdf_input: Union[Path, str],
) -> List[str]:
    """整合驗證健康存摺三份規格文件。"""
    errors: List[str] = []
    errors.extend(verify_health_bank_format_doc(format_input))
    errors.extend(verify_health_bank_dashboard_prompt(dashboard_input))
    errors.extend(verify_health_report_pdf_prompt(pdf_input))
    return errors


# ---------------------------------------------------------------------------
# 4. 全專案規格總體驗證器
# ---------------------------------------------------------------------------

def verify_all_specs(repo_root: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """執行全數外部裁判規格驗證。"""
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    # (1) Agent-Reach 路由與 references 驗證
    agent_reach_skill = root / "templates" / "agent-reach" / "SKILL.md"
    agent_reach_refs = root / "templates" / "agent-reach" / "references"
    results["templates/agent-reach/SKILL.md"] = verify_agent_reach_specs(
        agent_reach_skill, references_dir=agent_reach_refs
    )

    # (2) Public APIs 檢索技能與索引手冊
    pub_skill = root / "templates" / "public-apis-search-skill.md"
    pub_index = root / "docs" / "free-public-apis.md"
    results["templates/public-apis-search-skill.md"] = verify_public_apis_search_skill(pub_skill)
    results["docs/free-public-apis.md"] = verify_free_public_apis_index(pub_index)

    # (3) 健康存摺匯出格式與 Prompt 範本
    hb_format = root / "docs" / "health-bank-export-format.md"
    hb_dashboard = root / "templates" / "health-bank-dashboard-prompt.md"
    hb_pdf = root / "templates" / "health-report-pdf-prompt.md"
    results["docs/health-bank-export-format.md"] = verify_health_bank_format_doc(hb_format)
    results["templates/health-bank-dashboard-prompt.md"] = verify_health_bank_dashboard_prompt(hb_dashboard)
    results["templates/health-report-pdf-prompt.md"] = verify_health_report_pdf_prompt(hb_pdf)

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_output()
    parser = argparse.ArgumentParser(
        description="Agent-Reach 路由、Public APIs 檢索與健康存摺規格外部裁判結構驗證器"
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
        success_msg='全數 Agent-Reach、Public APIs 與健康存摺規格文件均通過外部裁判結構驗證！',
        fail_label='規格缺陷',
        ok_label='結構與規格完全相符',
        fail_msg='外部裁判驗證未通過，請依上述錯誤修正文件。',
    )


if __name__ == "__main__":
    sys.exit(main())
