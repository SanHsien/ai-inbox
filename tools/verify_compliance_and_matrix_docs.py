#!/usr/bin/env python3
"""
tools/verify_compliance_and_matrix_docs.py
合規清單、宣稱查證與對照矩陣之「外部裁判」結構驗證器。
僅使用 Python 標準函式庫。

對應任務：T-20261025-02
驗證目標：
  1. docs/ai-persona-compliance-checklist.md:
     - 至少 5 大分類區塊
     - 每類至少 3 個 `- [ ]` 勾選項
     - 所有 https:// 官方連結語法格式合法（有效 domain）且總數 >= 5
  2. docs/ai-influencer-claims-check.md:
     - 至少 3 項宣稱
     - 每項宣稱皆明確包含法定結論（「官方證實」、「官方未提及」、「與官方矛盾」之一）
     - 每項宣稱皆附有效 https:// 來源連結
  3. docs/feedback-desk-vs-agent-relay.md:
     - Markdown 對照表資料列 >= 8 列
     - 每列欄位數一致且無空白單元格
  4. templates/ambition-prompt-checklist.md:
     - 四大面向（高度/深度/廣度/外部裁判）勾選項完整
     - 同時包含「改寫前」與「改寫後」對照區塊
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VerificationResult:
    target: str
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def _load_text(content_or_path: str | Path) -> tuple[str, str]:
    if isinstance(content_or_path, Path):
        path = content_or_path
        if not path.exists():
            return "", str(path)
        return path.read_text(encoding="utf-8"), str(path)
    if isinstance(content_or_path, str):
        p = Path(content_or_path)
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8"), str(p)
        return content_or_path, "<inline_text>"
    return str(content_or_path), "<unknown>"


def is_valid_https_url(url: str) -> bool:
    """檢查是否為有效且具備合法網域的 https URL。"""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() != "https":
            return False
        netloc = parsed.netloc
        if not netloc:
            return False
        host = netloc.split(":")[0]
        parts = host.split(".")
        if len(parts) < 2:
            return False
        for part in parts:
            if not part or not re.match(r"^[a-zA-Z0-9_-]+$", part):
                return False
        return True
    except Exception:
        return False


def extract_urls(text: str) -> list[str]:
    """自 Markdown 文字中提取所有 URL 並清理結尾符號。"""
    raw_urls = re.findall(r"https://[^\s)\]\"'>]+", text)
    cleaned_urls = []
    for u in raw_urls:
        cleaned = re.sub(r"[),.\]]+$", "", u)
        if cleaned:
            cleaned_urls.append(cleaned)
    return cleaned_urls


def verify_persona_compliance_checklist(content_or_path: str | Path) -> VerificationResult:
    """驗證 docs/ai-persona-compliance-checklist.md 結構。"""
    text, target = _load_text(content_or_path)
    errors: list[str] = []
    details: dict[str, Any] = {}

    if not text.strip():
        return VerificationResult(target=target, is_valid=False, errors=["檔案為空或路徑不存在"])

    # 1. 解析分類區塊 (### 類別...)
    category_pattern = re.compile(r"^###\s+(類別[一二三四五六七八九十\d]+[：:][^\n]+)", re.M)
    cat_matches = list(category_pattern.finditer(text))

    categories_info: list[dict[str, Any]] = []
    if len(cat_matches) < 5:
        errors.append(f"分類區塊數量不足 5 大類（實際發現 {len(cat_matches)} 類）")

    for i, match in enumerate(cat_matches):
        cat_title = match.group(1).strip()
        start_pos = match.end()
        end_pos = cat_matches[i + 1].start() if i + 1 < len(cat_matches) else len(text)
        next_h2 = re.search(r"^##\s+", text[start_pos:end_pos], re.M)
        if next_h2:
            end_pos = start_pos + next_h2.start()

        section_body = text[start_pos:end_pos]
        checkboxes = re.findall(r"^\s*-\s*\[ \]\s+.+$", section_body, re.M)
        count = len(checkboxes)
        categories_info.append({"title": cat_title, "checkbox_count": count})

        if count < 3:
            errors.append(f"分類 '{cat_title}' 的 '- [ ]' 勾選項不足 3 個（實際發現 {count} 個）")

    details["categories"] = categories_info

    # 2. 檢查所有 https:// 官方連結
    urls = extract_urls(text)
    invalid_urls = [u for u in urls if not is_valid_https_url(u)]
    if invalid_urls:
        errors.append(f"發現不合法的 https URL 格式：{invalid_urls}")

    valid_urls = [u for u in urls if is_valid_https_url(u)]
    details["total_urls"] = len(urls)
    details["valid_urls"] = len(valid_urls)

    if len(valid_urls) < 5:
        errors.append(f"合法 https:// 官方連結總數不足 5 個（實際發現 {len(valid_urls)} 個）")

    return VerificationResult(
        target=target,
        is_valid=(len(errors) == 0),
        errors=errors,
        details=details,
    )


LEGAL_VERDICTS = ("官方證實", "官方未提及", "與官方矛盾")


def verify_influencer_claims_check(content_or_path: str | Path) -> VerificationResult:
    """驗證 docs/ai-influencer-claims-check.md 結構。"""
    text, target = _load_text(content_or_path)
    errors: list[str] = []
    details: dict[str, Any] = {}

    if not text.strip():
        return VerificationResult(target=target, is_valid=False, errors=["檔案為空或路徑不存在"])

    lines = [line.strip() for line in text.splitlines()]
    table_rows: list[str] = []
    in_table = False

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            if re.match(r"^\|\s*:?---+:?\s*\|", line):
                in_table = True
                continue
            if in_table:
                if line.startswith("|"):
                    table_rows.append(line)
        else:
            in_table = False

    if len(table_rows) < 3:
        errors.append(f"表格中的宣稱項目列數不足 3 項（實際發現 {len(table_rows)} 列）")

    claims_info: list[dict[str, Any]] = []
    for idx, row in enumerate(table_rows, start=1):
        matched_verdicts = [v for v in LEGAL_VERDICTS if v in row]
        if not matched_verdicts:
            errors.append(
                f"第 {idx} 項宣稱未包含法定結論（必須明確包含「官方證實」、「官方未提及」或「與官方矛盾」之一）"
            )

        row_urls = extract_urls(row)
        valid_row_urls = [u for u in row_urls if is_valid_https_url(u)]
        if not valid_row_urls:
            errors.append(f"第 {idx} 項宣稱缺少有效的 https:// 來源連結")

        claims_info.append({
            "index": idx,
            "verdicts": matched_verdicts,
            "url_count": len(valid_row_urls),
        })

    details["claims"] = claims_info

    return VerificationResult(
        target=target,
        is_valid=(len(errors) == 0),
        errors=errors,
        details=details,
    )


def verify_feedback_desk_matrix(content_or_path: str | Path) -> VerificationResult:
    """驗證 docs/feedback-desk-vs-agent-relay.md 結構。"""
    text, target = _load_text(content_or_path)
    errors: list[str] = []
    details: dict[str, Any] = {}

    if not text.strip():
        return VerificationResult(target=target, is_valid=False, errors=["檔案為空或路徑不存在"])

    lines = [line.strip() for line in text.splitlines()]
    header_cols = 0
    data_rows: list[list[str]] = []
    in_table = False

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            raw_cells = [c.strip() for c in line.split("|")[1:-1]]
            if re.match(r"^:?---+:?$", raw_cells[0]):
                in_table = True
                continue
            if not in_table:
                header_cols = len(raw_cells)
            else:
                data_rows.append(raw_cells)
        else:
            in_table = False

    details["header_columns"] = header_cols
    details["data_rows_count"] = len(data_rows)

    if len(data_rows) < 8:
        errors.append(f"對照表資料列數不足 8 列（實際發現 {len(data_rows)} 列）")

    for row_idx, cells in enumerate(data_rows, start=1):
        if len(cells) != header_cols:
            errors.append(
                f"第 {row_idx} 列欄位數不一致（表頭 {header_cols} 欄，此列 {len(cells)} 欄）"
            )
        for col_idx, cell in enumerate(cells, start=1):
            if cell == "":
                errors.append(f"第 {row_idx} 列第 {col_idx} 欄為空白單元格")

    return VerificationResult(
        target=target,
        is_valid=(len(errors) == 0),
        errors=errors,
        details=details,
    )


REQUIRED_AMBITION_ASPECTS = [
    ("面向一", "目標背後的目標"),
    ("面向二", "深度四問"),
    ("面向三", "廣度動詞化"),
    ("面向四", "外部裁判"),
]


def verify_ambition_prompt_checklist(content_or_path: str | Path) -> VerificationResult:
    """驗證 templates/ambition-prompt-checklist.md 結構。"""
    text, target = _load_text(content_or_path)
    errors: list[str] = []
    details: dict[str, Any] = {}

    if not text.strip():
        return VerificationResult(target=target, is_valid=False, errors=["檔案為空或路徑不存在"])

    # 1. 檢查四大面向標題與勾選項
    aspect_info: list[dict[str, Any]] = []
    for prefix, keyword in REQUIRED_AMBITION_ASPECTS:
        pattern = re.compile(rf"^##\s+({prefix}[：:][^\n]*{keyword}[^\n]*)", re.M)
        match = pattern.search(text)
        if not match:
            pattern_loose = re.compile(rf"^##\s+([^\n]*{keyword}[^\n]*)", re.M)
            match = pattern_loose.search(text)

        if not match:
            errors.append(f"缺少四大面向之一標題：{prefix}（{keyword}）")
            aspect_info.append({"aspect": f"{prefix}:{keyword}", "found": False, "checkbox_count": 0})
            continue

        start_pos = match.end()
        next_h2 = re.search(r"^##\s+", text[start_pos:], re.M)
        end_pos = start_pos + next_h2.start() if next_h2 else len(text)
        section_text = text[start_pos:end_pos]

        checkboxes = re.findall(r"^\s*-\s*\[[ xX]\]\s+.+$", section_text, re.M)
        count = len(checkboxes)
        aspect_info.append({"aspect": match.group(1).strip(), "found": True, "checkbox_count": count})

        if count < 2:
            errors.append(f"面向「{match.group(1).strip()}」勾選項不足（至少需 2 項，實際發現 {count} 項）")

    details["aspects"] = aspect_info

    # 2. 檢查改寫前與改寫後對照區塊
    has_before = bool(re.search(r"^###?\s+改寫前\b", text, re.M))
    has_after = bool(re.search(r"^###?\s+改寫後\b", text, re.M))

    details["has_before_section"] = has_before
    details["has_after_section"] = has_after

    if not has_before:
        errors.append("缺少「改寫前」對照區塊標題（例如 ### 改寫前）")
    if not has_after:
        errors.append("缺少「改寫後」對照區塊標題（例如 ### 改寫後）")

    return VerificationResult(
        target=target,
        is_valid=(len(errors) == 0),
        errors=errors,
        details=details,
    )


def verify_all_docs(repo_root: Path | None = None) -> dict[str, VerificationResult]:
    """執行全數四份文件的結構驗證。"""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    persona_path = repo_root / "docs" / "ai-persona-compliance-checklist.md"
    claims_path = repo_root / "docs" / "ai-influencer-claims-check.md"
    matrix_path = repo_root / "docs" / "feedback-desk-vs-agent-relay.md"
    ambition_path = repo_root / "templates" / "ambition-prompt-checklist.md"

    return {
        "persona_compliance": verify_persona_compliance_checklist(persona_path),
        "influencer_claims": verify_influencer_claims_check(claims_path),
        "feedback_matrix": verify_feedback_desk_matrix(matrix_path),
        "ambition_checklist": verify_ambition_prompt_checklist(ambition_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="合規清單、宣稱查證與對照矩陣之結構驗證器 (T-20261025-02)"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="指定 ai-inbox 的根目錄路徑（預設為腳本上一層的上一層）",
    )
    args = parser.parse_args()

    repo_root = args.root or Path(__file__).resolve().parent.parent
    results = verify_all_docs(repo_root)

    all_passed = True
    print(f"=== 執行結構驗證器 (Repo Root: {repo_root}) ===")
    for key, res in results.items():
        status = "[PASS]" if res.is_valid else "[FAIL]"
        print(f"\n{status} {key} -> {res.target}")
        if res.is_valid:
            print(f"  詳情: {res.details}")
        else:
            all_passed = False
            for err in res.errors:
                print(f"  ❌ 錯誤: {err}")

    print("\n" + "=" * 50)
    if all_passed:
        print("[PASS] 全部 4 份合規清單、宣稱查證與對照矩陣文件結構驗證通過！")
        return 0
    else:
        print("[FAIL] 結構驗證發現錯誤，請修正後重新執行！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
