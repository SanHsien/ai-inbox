#!/usr/bin/env python3
"""
tools/verify_academic_and_latex_guard.py
學術論文雙語翻譯「LaTeX 公式與引用零竄改保護」及「5W1H-CQR-KSU 結構」之外部裁判驗證器（純 Python stdlib）。

驗證目標：
1. verify_latex_and_citations_preserved(source_text, translated_text):
   - 自動抽取行內公式 ($...$, \\(...\\))、區塊公式 ($$...$$, \\[...\\], \\begin{equation}...\\end{equation})、
     引用標籤 (\\cite{...}, [1]~[99], [Author et al., Year]) 與交叉參照 (\\ref{...}, \\eqref{...}, Eq. (X), Fig. X)；
   - 驗證譯文 100% 零遺漏、零竄改。
2. templates/latex-citation-protection-prompt.md:
   - 包含四大保護契約（行內公式、區塊公式、引用參照、學術文風）；
   - 內嵌之測試輸入與預期標準輸出通過 verify_latex_and_citations_preserved 檢驗；
   - 包含驗收核對清單。
3. templates/academic-reading-prompt.md:
   - 完整涵蓋 5W1H、CQR 與 KSU 三層過濾結構；
   - 包含模式選擇（簡短/深度）、結構化輸出範本與防幻覺紀律。
4. docs/academic-reading-smoke-report.md:
   - 完整落實 5W1H、CQR 表格與 KSU 轉化；
   - 包含可追溯定位與邊界限制分析。
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 正則表示式定義
# ---------------------------------------------------------------------------

# 區塊公式：$$...$$, \[...\], \begin{equation}...\end{equation}, \begin{align}...\end{align} 等
BLOCK_MATH_PATTERNS = [
    re.compile(r"\$\$[\s\S]*?\$\$"),
    re.compile(r"\\\[[\s\S]*?\\\]"),
    re.compile(
        r"\\begin\{(?:equation|align|gather|multline)\*?\}[\s\S]*?\\end\{(?:equation|align|gather|multline)\*?\}"
    ),
]

# 行內公式：$...$（排除 $$），\(...\)
INLINE_MATH_DOLLAR_RE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)")
INLINE_MATH_PAREN_RE = re.compile(r"\\\((.+?)\\\)")

# 引用標籤：
# 1. \cite{...} 或 \cite[...]{...}
CITE_CMD_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{[^}]+\}")
# 2. 數字引用標籤 [1]~[99], [3-5], [1, 2, 3] 等
CITE_NUM_RE = re.compile(r"\[\d{1,2}(?:\s*[-–,]\s*\d{1,2})*\]")
# 3. 學術作者年份引用標籤 [Kerbl et al., 2023], [Mildenhall et al., 2020; Barron et al., 2021], (He et al., 2016)
CITE_AUTHOR_BRACKET_RE = re.compile(
    r"\[[A-Z][A-Za-z\s.\-]+(?:et\s+al\.,?|\&|,)\s*\d{4}[a-z]?(?:;\s*[A-Z][A-Za-z\s.\-]+(?:et\s+al\.,?|\&|,)\s*\d{4}[a-z]?)*\]"
)
CITE_AUTHOR_PAREN_RE = re.compile(
    r"\([A-Z][A-Za-z\s.\-]+(?:et\s+al\.,?|\&|,)\s*\d{4}[a-z]?(?:;\s*[A-Z][A-Za-z\s.\-]+(?:et\s+al\.,?|\&|,)\s*\d{4}[a-z]?)*\)"
)

# 交叉參照：
# 1. \ref{...}, \eqref{...}
REF_CMD_RE = re.compile(r"\\(?:eq)?ref\{[^}]+\}")
# 2. 學術標準交叉參照縮寫：Eq. (3), Fig. 2(b), Table 3, Theorem 1 等
CROSS_REF_TEXT_RE = re.compile(
    r"\b(?:Eq\.|Equation|Fig\.|Figure|Table|Theorem|Section|Sec\.)\s+(?:\(\d+[a-z]?\)|\d+[a-z]?(?:\([a-z]\))?)"
)


@dataclass
class ExtractedAcademicItems:
    """自文本抽取的 LaTeX 公式、引用與參照清單。"""

    block_math: List[str] = field(default_factory=list)
    inline_math: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    cross_refs: List[str] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return (
            len(self.block_math)
            + len(self.inline_math)
            + len(self.citations)
            + len(self.cross_refs)
        )


def extract_academic_items(text: str) -> ExtractedAcademicItems:
    """
    從給定文本中自動抽取所有：
    1. 區塊公式 ($$...$$, \\[...\\], \\begin{equation}...\\end{equation})
    2. 行內公式 ($...$, \\(...\\))
    3. 引用標籤 (\\cite{...}, [1]~[99], [Author et al., Year])
    4. 交叉參照 (\\ref{...}, \\eqref{...}, Eq. (X), Fig. X)
    """
    items = ExtractedAcademicItems()
    work_text = text

    # 1. 抽取區塊公式，並以佔位符置換，避免干擾後續行內公式比對
    block_placeholders: Dict[str, str] = {}
    block_idx = 0
    for pattern in BLOCK_MATH_PATTERNS:
        for match in pattern.finditer(work_text):
            raw_block = match.group(0).strip()
            items.block_math.append(raw_block)
            ph = f"___BLOCK_MATH_{block_idx}___"
            block_placeholders[ph] = raw_block
            block_idx += 1

    for ph, raw in block_placeholders.items():
        work_text = work_text.replace(raw, ph)

    # 2. 抽取行內公式
    # 先抽 \( ... \)
    for match in INLINE_MATH_PAREN_RE.finditer(work_text):
        items.inline_math.append(match.group(0).strip())

    # 再抽 $ ... $（單錢字號）
    for match in INLINE_MATH_DOLLAR_RE.finditer(work_text):
        items.inline_math.append(match.group(0).strip())

    # 3. 抽取引用標籤
    # 先抽 \cite{...}
    for match in CITE_CMD_RE.finditer(work_text):
        items.citations.append(match.group(0).strip())

    # 抽取作者年份引用 [Author et al., 2023]
    for match in CITE_AUTHOR_BRACKET_RE.finditer(work_text):
        items.citations.append(match.group(0).strip())

    for match in CITE_AUTHOR_PAREN_RE.finditer(work_text):
        items.citations.append(match.group(0).strip())

    # 抽取數字引用 [1]~[99]（注意避免重複抓取）
    for match in CITE_NUM_RE.finditer(work_text):
        matched_str = match.group(0).strip()
        # 若尚未被包含則加入
        if matched_str not in items.citations:
            items.citations.append(matched_str)

    # 4. 抽取交叉參照
    for match in REF_CMD_RE.finditer(work_text):
        items.cross_refs.append(match.group(0).strip())

    for match in CROSS_REF_TEXT_RE.finditer(work_text):
        items.cross_refs.append(match.group(0).strip())

    return items


def verify_latex_and_citations_preserved(
    source_text: str, translated_text: str
) -> List[str]:
    """
    原文與譯文比對核心函式：
    驗證原文中出現的所有區塊公式、行內公式、引用標籤與交叉參照，
    在譯文中 100% 零遺漏、零竄改。
    """
    errors: List[str] = []
    src_items = extract_academic_items(source_text)

    # 輔助比對：針對四個分類逐一驗證
    categories = [
        ("區塊數學公式 (Block Math)", src_items.block_math),
        ("行內數學公式 (Inline Math)", src_items.inline_math),
        ("學術引用標籤 (Citation)", src_items.citations),
        ("交叉參照標籤 (Cross-reference)", src_items.cross_refs),
    ]

    for cat_name, items_list in categories:
        counts = Counter(items_list)
        for item, expected_count in counts.items():
            # 在譯文中統計出現次數
            actual_count = translated_text.count(item)
            if actual_count == 0:
                errors.append(
                    f"【{cat_name} 遺失或被竄改】：原文包含 `{item}`，但譯文中完全未出現或遭變更"
                )
            elif actual_count < expected_count:
                errors.append(
                    f"【{cat_name} 出現頻率不足】：原文包含 {expected_count} 次 `{item}`，但譯文僅出現 {actual_count} 次"
                )

    return errors


# ---------------------------------------------------------------------------
# 各文件專用驗證邏輯
# ---------------------------------------------------------------------------


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄。"""
    if start is not None:
        return start.resolve()
    cur = Path(__file__).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "notes").is_dir() and (parent / "docs").is_dir():
            return parent
    return Path.cwd()


def verify_latex_citation_protection_prompt(content: str) -> List[str]:
    """
    驗證 templates/latex-citation-protection-prompt.md：
    1. 涵蓋四大保護契約（行內公式、區塊公式、引用參照、學術文風）；
    2. 內嵌之測試輸入與預期標準輸出通過 verify_latex_and_citations_preserved 檢驗；
    3. 包含驗收核對清單。
    """
    errors: List[str] = []

    # 1. 四大保護契約校驗（中英文名稱皆必須完整涵蓋）
    required_contracts = [
        ("行內數學公式保護", "Inline Math"),
        ("區塊數學公式保護", "Display Block Math"),
        ("學術引用與交叉參照保護", "Citation & Cross-reference"),
        ("專業術語精確性與文風", "Academic Tone"),
    ]
    for name_zh, name_en in required_contracts:
        if name_zh not in content or name_en not in content:
            errors.append(f"缺少四大保護契約之一：「{name_zh} ({name_en})」")

    # 2. 測試輸入 (Test Input) 與 預期標準輸出 (Expected Output) 抽取與驗證
    test_input_match = re.search(
        r"##\s+2\.\s+測試案例：測試輸入[^\n]*\n+[\s\S]*?```(?:text)?\n([\s\S]*?)```",
        content,
    )
    expected_output_match = re.search(
        r"##\s+3\.\s+測試案例：預期標準輸出[^\n]*\n+[\s\S]*?```(?:markdown)?\n([\s\S]*?)```",
        content,
    )

    if not test_input_match:
        errors.append("未找到「## 2. 測試案例：測試輸入」之代碼區塊")
    if not expected_output_match:
        errors.append("未找到「## 3. 測試案例：預期標準輸出」之代碼區塊")

    if test_input_match and expected_output_match:
        source_text = test_input_match.group(1).strip()
        translated_text = expected_output_match.group(1).strip()

        # 檢驗測試案例本身是否包含公式與引用
        items = extract_academic_items(source_text)
        if len(items.block_math) == 0:
            errors.append("測試輸入中未偵測到任何區塊數學公式 ($$...$$)")
        if len(items.inline_math) == 0:
            errors.append("測試輸入中未偵測到任何行內數學公式 ($...$)")
        if len(items.citations) == 0:
            errors.append("測試輸入中未偵測到任何學術文獻引用")
        if len(items.cross_refs) == 0:
            errors.append("測試輸入中未偵測到任何交叉參照標籤")

        # 比對測試輸入與預期輸出
        tamper_errors = verify_latex_and_citations_preserved(
            source_text, translated_text
        )
        if tamper_errors:
            errors.extend(
                [f"測試輸入與預期輸出比對失敗：{err}" for err in tamper_errors]
            )

    # 3. 驗收核對檢查表校驗
    has_checklist_heading = "驗收核對檢查表" in content or "Verification Checklist" in content
    has_checked_boxes = content.count("- [x]") >= 3
    if not (has_checklist_heading and has_checked_boxes):
        errors.append("缺少驗收核對檢查表 (Verification Checklist) 或完成勾選項目不足 (< 3)")

    return errors


def verify_academic_reading_prompt(content: str) -> List[str]:
    """
    驗證 templates/academic-reading-prompt.md：
    1. 包含 5W1H 核心輪廓（Who, What, Why, How, When & Where, Key Metrics）；
    2. 包含 CQR 論證檢驗矩陣（Claim, Evidence, Reasoning, 缺失證據處理, 適用範圍與覆蓋落差）；
    3. 包含 KSU 知識資產轉化（Searchable, Recyclable, Usable 與明確 DoD）；
    4. 包含模式選擇（簡短模式/深度模式）與結構化輸出範本。
    """
    errors: List[str] = []

    # 1. 5W1H 六大維度
    five_w_one_h = ["Who", "What", "Why", "How", "When", "Key Metrics"]
    for dim in five_w_one_h:
        if dim not in content:
            errors.append(f"第一層 5W1H 缺少核心維度「{dim}」")

    # 2. CQR 三大維度與邊界審查
    cqr_dims = ["Claim", "Evidence", "Reasoning"]
    for dim in cqr_dims:
        if dim not in content:
            errors.append(f"第二層 CQR 缺少核心維度「{dim}」")

    if "缺失證據" not in content:
        errors.append("第二層 CQR 缺少「缺失證據處理」防呆規範")
    if "宣稱" not in content or "落差" not in content:
        errors.append("第二層 CQR 缺少「宣稱適用範圍 vs 實際覆蓋範圍」之落差分析要求")

    # 3. KSU 三大知識資產轉化
    ksu_dims = [
        ("Searchable", "可搜尋"),
        ("Recyclable", "可復用"),
        ("Usable", "可應用"),
    ]
    for dim_en, dim_zh in ksu_dims:
        if dim_en not in content and dim_zh not in content:
            errors.append(f"第三層 KSU 缺少核心資產「{dim_en} ({dim_zh})」")

    if "DoD" not in content or "驗收標準" not in content:
        errors.append("第三層 KSU 缺少工程可驗收待辦之「驗收標準 (DoD)」要求")

    # 4. 模式選擇與防幻覺規範
    if "簡短模式" not in content or "深度模式" not in content:
        errors.append("缺少「簡短模式 (Triage Mode)」與「深度模式 (Deep-dive Mode)」模式選擇定義")

    if "防幻覺" not in content and "嚴禁捏造數據" not in content:
        errors.append("缺少防幻覺與嚴禁捏造數據之紀律約束")

    return errors


def verify_academic_reading_smoke_report(content: str) -> List[str]:
    """
    驗證 docs/academic-reading-smoke-report.md：
    1. 包含論文固定版本定位（arXiv 固定版本與官方來源）；
    2. 完整實測 5W1H 六大維度；
    3. 包含 CQR Markdown 檢驗矩陣表格與落差/邊界分析；
    4. 包含 KSU（Searchable tags, Recyclable 模式, Usable DoD 待辦事項）。
    """
    errors: List[str] = []

    # 1. 論文來源定位
    if "SWE-bench" not in content:
        errors.append("實測報告未定位至目標論文（缺少 SWE-bench 關鍵字）")
    if "arXiv:" not in content:
        errors.append("實測報告缺少精確版本號定位（例如 arXiv:2310.06770v3）")

    # 2. 第一層 5W1H 實測輪廓
    five_w_one_h = ["Who", "What", "Why", "How", "When", "Key Metrics"]
    for dim in five_w_one_h:
        if dim not in content:
            errors.append(f"實測報告第一層缺少 5W1H 核心維度「{dim}」之具體實測內容")

    # 3. 第二層 CQR 論證檢驗矩陣表格
    has_cqr_heading = "CQR" in content
    has_cqr_table = bool(
        re.search(r"\|\s*維度\s*\|\s*內容摘要.*\s*\|\s*原文精準定位.*\|", content)
        and re.search(r"\|\s*\*\*Claim.*\|", content)
        and re.search(r"\|\s*\*\*Evidence.*\|", content)
        and re.search(r"\|\s*\*\*Reasoning.*\|", content)
    )
    if not (has_cqr_heading and has_cqr_table):
        errors.append("實測報告缺少第二層 CQR 論證檢驗矩陣 Markdown 表格")

    has_boundary_analysis = "邊界" in content or "外推限制" in content
    if not has_boundary_analysis:
        errors.append("實測報告缺少論文作者明示邊界與工程外推限制之深度分析")

    # 4. 第三層 KSU 知識轉化
    has_ksu_heading = "KSU" in content
    has_searchable = "Searchable" in content or "tags" in content
    has_recyclable = "Recyclable" in content
    has_usable = "Usable" in content
    has_dod = "DoD" in content or "驗收標準" in content

    if not (has_ksu_heading and has_searchable and has_recyclable and has_usable and has_dod):
        errors.append("實測報告缺少完整第三層 KSU 知識資產轉化（需含 S、R、U 與明確 DoD 驗收標準）")

    return errors


def verify_all_academic_and_latex_guards(
    repo_root: Optional[Path] = None,
) -> Tuple[bool, Dict[str, List[str]]]:
    """執行全數學術與 LaTeX 保護規範外部裁判驗證。"""
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    targets = [
        (
            "templates/latex-citation-protection-prompt.md",
            verify_latex_citation_protection_prompt,
        ),
        ("templates/academic-reading-prompt.md", verify_academic_reading_prompt),
        ("docs/academic-reading-smoke-report.md", verify_academic_reading_smoke_report),
    ]

    for rel_path, verifier in targets:
        full_path = root / rel_path
        if not full_path.exists():
            results[rel_path] = [f"目標檔案不存在：{rel_path}"]
        else:
            content = full_path.read_text(encoding="utf-8")
            results[rel_path] = verifier(content)

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="學術論文雙語翻譯「LaTeX 公式與引用零竄改保護」及「5W1H-CQR-KSU 結構」之外部裁判驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 notes/ 與 docs/ 之根目錄）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(
        f"[*] 執行學術論文 LaTeX 保護與 5W1H-CQR-KSU 外部裁判驗證，專案根目錄：{root}"
    )

    all_passed, results = verify_all_academic_and_latex_guards(root)

    for rel_path, errs in results.items():
        if errs:
            print(f"\n[FAIL] ❌ {rel_path} 發現 {len(errs)} 項規格缺陷：")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[PASS] ✅ {rel_path} 結構與規格完全相符")

    if all_passed:
        print("\n[SUCCESS] 🎉 全數學術論文雙語翻譯保護與結構規範均通過外部裁判驗證！")
        return 0
    else:
        print("\n[ERROR] 外部裁判驗證未通過，請依上述錯誤修正文件。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
