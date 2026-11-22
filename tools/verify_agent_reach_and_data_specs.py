#!/usr/bin/env python3
"""
tools/verify_agent_reach_and_data_specs.py
Agent-Reach 16 平台路由範本、Public APIs 檢索技能之「外部裁判」結構驗證器（純 Python stdlib）。

驗證目標：
1. templates/agent-reach/SKILL.md 與 templates/agent-reach/references/：
   - 驗證 7 大領域分類 references 檔案齊全（search, social, career, dev, web, video, finance）；
   - 驗證路由表結構完整、覆蓋 7 大分類，且所有 markdown 參照無斷鏈。
2. templates/public-apis-search-skill.md 與 docs/free-public-apis.md：
   - 驗證 Auth: No、CORS: Yes、HTTPS 三道篩選門檻；
   - 驗證索引宣告的筆數、分類數與目錄、表格實際內容逐類對得上（數字由文件內容計算，不寫死），
     並註明來源快照 commit 與日期；每筆資料符合零金鑰/跨域放行條件。
   - 加 --public-apis-source <README.md> 時，另以 tools/public_apis_indexer.py 的解析結果逐筆對帳。
（健康存摺三份文件已於 2026-10-25 移至 SanHsien/health-bank-toolkit，相關檢查一併移除。）
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

# 2026-11-21 稽核後重做：舊版把 2026-10 快照的 462 筆／42 類寫死，來源一更新索引就不能重產。
# 現在筆數與分類數一律從文件內容計算並互相對帳；只保留任務 DoD（T-20261020-01）的下限。
MIN_PUBLIC_APIS_CATEGORIES = 10

# 來源快照行：- **來源快照**：commit `<40 位十六進位>`（YYYY-MM-DD），本檔產生日 YYYY-MM-DD
SNAPSHOT_LINE_PATTERN = re.compile(
    r"^-\s+\*\*來源快照\*\*：commit\s+`([0-9a-f]{40})`（(\d{4}-\d{2}-\d{2})），本檔產生日\s+(\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)

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
    - 註明來源快照 commit（40 位）與日期；
    - 宣告的筆數、分類數與實際結構完全相符（數字由文件內容計算，不寫死）；
    - 目錄索引（TOC）的分類與各分類筆數，逐類等於詳細清單該分類的實際列數；
    - 分類數不低於 MIN_PUBLIC_APIS_CATEGORIES；
    - 每筆 Auth 均為 No、CORS 均為 Yes、包含 HTTPS 欄位。
    """
    errors: List[str] = []
    text, _ = _resolve_content_and_path(index_input, default_subpath="docs/free-public-apis.md")

    if not text.strip():
        return ["docs/free-public-apis.md 內容為空或檔案不存在"]

    # 1. 篩選條件、來源快照與筆數宣告校驗
    if "Auth: No" not in text or "CORS: Yes" not in text:
        errors.append("docs/free-public-apis.md 缺少「Auth: No 且 CORS: Yes」篩選條件宣告")

    if not SNAPSHOT_LINE_PATTERN.search(text):
        errors.append(
            "docs/free-public-apis.md 缺少來源快照行"
            "（格式：- **來源快照**：commit `<40 位 commit>`（YYYY-MM-DD），本檔產生日 YYYY-MM-DD）"
        )

    declaration = re.search(r"共\s*(\d+)\s*個公開端點，跨\s*(\d+)\s*個分類", text)
    declared_count: Optional[int] = None
    declared_categories: Optional[int] = None
    if not declaration:
        errors.append("docs/free-public-apis.md 缺少「共 N 個公開端點，跨 M 個分類」之數據規格宣告")
    else:
        declared_count = int(declaration.group(1))
        declared_categories = int(declaration.group(2))

    # 2. 目錄索引（TOC）解析：- [Category](#anchor) (count)
    toc_pattern = re.compile(r"^-\s+\[([^\]]+)\]\((#[^\)]+)\)\s+\((\d+)\)", re.MULTILINE)
    toc_counts: Dict[str, int] = {}
    for cat, _anchor, count in toc_pattern.findall(text):
        if cat in toc_counts:
            errors.append(f"目錄索引分類重複：{cat}")
        toc_counts[cat] = int(count)
    toc_total_sum = sum(toc_counts.values())

    # 3. 分類詳細清單結構與表格資料列解析（逐分類計數）
    api_rows: List[List[str]] = []
    rows_per_category: Dict[str, int] = {}
    current_category: Optional[str] = None
    for line in text.splitlines():
        line_s = line.strip()
        if line_s.startswith("### "):
            current_category = line_s[4:].strip()
            continue
        if line_s.startswith("## "):
            current_category = None
            continue
        # 匹配表格資料列：以 | [ 開頭
        if line_s.startswith("| [") and "|" in line_s[3:]:
            parts = [p.strip() for p in line_s.split("|")[1:-1]]
            # 欄位應為：API、說明、驗證 (Auth)、HTTPS、跨域 (CORS)
            if len(parts) >= 5:
                api_rows.append(parts)
                key = current_category or "（不在任何分類標題下）"
                rows_per_category[key] = rows_per_category.get(key, 0) + 1

    actual_row_count = len(api_rows)

    # 4. 宣告、目錄、表格三者互相對帳
    if declared_count is not None and declared_count != actual_row_count:
        errors.append(
            f"筆數宣告與表格不符：宣告 {declared_count} 筆，API 詳細表格資料列數實際解析出 {actual_row_count} 筆"
        )
    if declared_categories is not None and declared_categories != len(rows_per_category):
        errors.append(
            f"分類數宣告與表格不符：宣告 {declared_categories} 個分類，詳細清單實際有 {len(rows_per_category)} 個"
        )
    if toc_total_sum != actual_row_count:
        errors.append(
            f"目錄索引筆數加總異常：目錄加總 {toc_total_sum} 筆，表格資料列數異常或實際為 {actual_row_count} 筆"
        )
    mismatched = [
        f"{cat}（目錄 {toc_counts.get(cat, 0)}／表格 {rows_per_category.get(cat, 0)}）"
        for cat in sorted(set(toc_counts) | set(rows_per_category))
        if toc_counts.get(cat, 0) != rows_per_category.get(cat, 0)
    ]
    if mismatched:
        errors.append(
            f"目錄索引與詳細清單有 {len(mismatched)} 個分類筆數不符，例如：{mismatched[:3]}"
        )
    if len(rows_per_category) < MIN_PUBLIC_APIS_CATEGORIES:
        errors.append(
            f"分類數過少：詳細清單只有 {len(rows_per_category)} 個分類，低於下限 {MIN_PUBLIC_APIS_CATEGORIES} 個分類"
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


def _index_pairs(index_text: str) -> set:
    """從索引手冊抽出 (分類, API 名稱) 配對。"""
    pairs = set()
    current: Optional[str] = None
    for line in index_text.splitlines():
        line_s = line.strip()
        if line_s.startswith("### "):
            current = line_s[4:].strip()
        elif line_s.startswith("## "):
            current = None
        elif current and line_s.startswith("| ["):
            name = re.match(r"\|\s*\[([^\]]+)\]", line_s)
            if name:
                pairs.add((current, name.group(1).strip()))
    return pairs


def verify_index_matches_source(index_text: str, source_readme_text: str) -> List[str]:
    """拿來源 README 逐筆對帳：索引應等於來源裡 Auth: No 且 CORS: Yes 的全部條目。

    來源 README 不在本 repo，CI 拿不到，所以這項只在命令列帶 --public-apis-source 時執行。
    解析與篩選直接用 tools/public_apis_indexer.py，確保與產生索引時同一套規則。
    """
    import public_apis_indexer as indexer  # 同目錄工具；延後匯入，避免沒用到時多一層相依

    expected = {
        (e.category, e.name.replace("|", "/"))
        for e in indexer.filter_apis(indexer.parse_markdown_table_rows(source_readme_text), auth="no", cors="yes")
    }
    actual = _index_pairs(index_text)
    errors: List[str] = []
    stale = sorted(actual - expected)
    missing = sorted(expected - actual)
    if stale:
        errors.append(
            f"索引有 {len(stale)} 筆已不在來源（或不再符合篩選條件），例如：{[f'{c}/{n}' for c, n in stale[:5]]}"
        )
    if missing:
        errors.append(
            f"來源有 {len(missing)} 筆符合條件但索引沒有，例如：{[f'{c}/{n}' for c, n in missing[:5]]}"
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
# 3. 全專案規格總體驗證器
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

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_output()
    parser = argparse.ArgumentParser(
        description="Agent-Reach 路由與 Public APIs 檢索規格外部裁判結構驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 notes/ 與 docs/ 之根目錄）",
    )
    parser.add_argument(
        "--public-apis-source",
        type=Path,
        default=None,
        help="public-apis 的 README.md 路徑；有給就拿它與 docs/free-public-apis.md 逐筆對帳（來源應停在索引註明的快照 commit）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(f"[*] 執行外部裁判規格結構校驗，專案根目錄：{root}")

    all_passed, results = verify_all_specs(root)

    if args.public_apis_source is not None:
        key = "docs/free-public-apis.md"
        index_path = root / "docs" / "free-public-apis.md"
        if not args.public_apis_source.is_file():
            results.setdefault(key, []).append(f"找不到 --public-apis-source 指定的檔案：{args.public_apis_source.name}")
        elif index_path.is_file():
            results.setdefault(key, []).extend(
                verify_index_matches_source(
                    index_path.read_text(encoding="utf-8"),
                    args.public_apis_source.read_text(encoding="utf-8-sig"),
                )
            )

    return report_results(
        results,
        success_msg='全數 Agent-Reach 與 Public APIs 規格文件均通過外部裁判結構驗證！',
        fail_label='規格缺陷',
        ok_label='結構與規格完全相符',
        fail_msg='外部裁判驗證未通過，請依上述錯誤修正文件。',
    )


if __name__ == "__main__":
    sys.exit(main())
