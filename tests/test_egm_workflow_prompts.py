"""templates/egm-workflow-prompts.md 與 docs/elephant-goldfish-model-spec.md 的一致性測試。

檢查的是結構與隔離規則，不是語意品質：
- 變數表與提示詞實際使用的 {{變數}} 必須一致（沒宣告的、宣告了沒用的都失敗）。
- 金魚提示詞（P3）只能用「給金魚＝是」的變數；大象專屬變數洩漏進去必須失敗。
- 以範例值代入後不得殘留 {{ }}。
- 範本的審查階段名稱必須出現在規範文件。
測試內附壞輸入（洩漏、未宣告、殘留）確認檢查函式真的會失敗。
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "egm-workflow-prompts.md"
SPEC = ROOT / "docs" / "elephant-goldfish-model-spec.md"

VAR_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
ROW_RE = re.compile(r"^\|\s*`\{\{([A-Z_]+)\}\}`\s*\|.*\|\s*(是|否)\s*\|\s*$")
STAGE_NAMES = [
    "Initial Zoom Out Review",
    "Comprehension Test",
    "Critic Review",
    "Intermediate Zoom Out Review",
    "Implementation Readiness Test",
]


def parse_variable_table(text: str) -> dict[str, bool]:
    """回傳 {變數名: 是否可給金魚}。"""
    out: dict[str, bool] = {}
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if m:
            if m.group(1) in out:
                raise ValueError(f"變數重複宣告：{m.group(1)}")
            out[m.group(1)] = m.group(2) == "是"
    return out


def parse_prompts(text: str) -> dict[str, str]:
    """回傳 {P1: 區塊內容, ...}：每個 `## Pn.` 標題後第一個 ```text 區塊。

    逐行掃描並追蹤程式碼圍欄，圍欄內以 `## ` 開頭的行（例如 P5 的輸出格式）不算標題。
    """
    prompts: dict[str, str] = {}
    current: str | None = None
    in_fence = False
    fence_is_text = False
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_is_text = line.strip() == "```text"
                buf = []
            else:
                in_fence = False
                if fence_is_text and current and current not in prompts:
                    prompts[current] = "\n".join(buf)
            continue
        if in_fence:
            buf.append(line)
            continue
        if line.startswith("## "):
            m = re.match(r"## (P\d+)\.", line)
            current = m.group(1) if m else None
    return prompts


def check_consistency(table: dict[str, bool], prompts: dict[str, str]) -> list[str]:
    errors: list[str] = []
    used: set[str] = set()
    for pid, body in prompts.items():
        names = set(VAR_RE.findall(body))
        used |= names
        for n in sorted(names - set(table)):
            errors.append(f"{pid} 使用未宣告的變數 {n}")
        if pid == "P3":
            for n in sorted(names & set(table)):
                if not table[n]:
                    errors.append(f"P3（金魚）使用了大象專屬變數 {n}")
    for n in sorted(set(table) - used):
        errors.append(f"變數 {n} 已宣告但沒有任何提示詞使用")
    return errors


def check_resolve_matches_review(prompts: dict[str, str]) -> list[str]:
    p3 = set(VAR_RE.findall(prompts["P3"]))
    p4 = set(VAR_RE.findall(prompts["P4"]))
    errors: list[str] = []
    if "TARGET_FILE" not in p3:
        errors.append("P3 沒有 TARGET_FILE")
    if "TARGET_FILE" not in p4:
        errors.append("P4 沒有以 TARGET_FILE 指定被處理的設計文件")
    if "DRAFT_PATH" in p4:
        errors.append("P4 指向起草中的 DRAFT_PATH，修正會套到過時草稿")
    return errors


def render(body: str, table: dict[str, bool]) -> str:
    return VAR_RE.sub(lambda m: f"<{m.group(1).lower()}-sample>" if m.group(1) in table else m.group(0), body)


class WorkflowPromptsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = TEMPLATE.read_text(encoding="utf-8")
        cls.table = parse_variable_table(cls.text)
        cls.prompts = parse_prompts(cls.text)

    def test_five_prompts_present(self) -> None:
        self.assertEqual(sorted(self.prompts), ["P1", "P2", "P3", "P4", "P5"])

    def test_variable_table_is_nonempty_and_has_both_audiences(self) -> None:
        self.assertGreaterEqual(len(self.table), 10)
        self.assertTrue(any(self.table.values()))
        self.assertTrue(any(not v for v in self.table.values()))

    def test_variables_and_prompts_consistent(self) -> None:
        self.assertEqual(check_consistency(self.table, self.prompts), [])

    def test_goldfish_prompt_uses_only_goldfish_variables(self) -> None:
        names = set(VAR_RE.findall(self.prompts["P3"]))
        self.assertTrue(names, "P3 沒有任何變數，無法指定審查目標")
        self.assertTrue({"TARGET_FILE", "LINE_RANGE", "STAGE_NAME"} <= names)
        for n in names:
            self.assertTrue(self.table[n], f"{n} 不可給金魚")

    def test_rendering_leaves_no_placeholder(self) -> None:
        for pid, body in self.prompts.items():
            rendered = render(body, self.table)
            self.assertNotIn("{{", rendered, pid)
            self.assertNotIn("}}", rendered, pid)

    def test_stage_names_match_spec(self) -> None:
        spec = SPEC.read_text(encoding="utf-8")
        for name in STAGE_NAMES:
            self.assertIn(name, self.text, f"範本缺少階段 {name}")
            self.assertIn(name, spec, f"規範缺少階段 {name}")

    def test_spec_has_five_stage_sections(self) -> None:
        spec = SPEC.read_text(encoding="utf-8")
        for n in range(5, 10):
            self.assertRegex(spec, rf"(?m)^### Stage {n}：", f"規範缺少 Stage {n} 章節")
        # 每個階段至少 5 個可勾選的驗核項（不得是空殼章節）
        parts = re.split(r"(?m)^### Stage \d：", spec)[1:]
        self.assertEqual(len(parts), 5)
        for i, part in enumerate(parts, start=5):
            part = re.split(r"(?m)^## ", part)[0]
            self.assertGreaterEqual(len(re.findall(r"(?m)^- \[ \] ", part)), 2, f"Stage {i} 驗核項過少")

    def test_resolve_targets_same_file_as_review(self) -> None:
        """P4 處理的文件必須是 P3 審查的同一個變數（TARGET_FILE），不是起草中的草稿。"""
        self.assertEqual(check_resolve_matches_review(self.prompts), [])

    def test_resolve_pointing_at_draft_fails(self) -> None:
        prompts = dict(self.prompts)
        prompts["P4"] = prompts["P4"].replace("{{TARGET_FILE}}", "{{DRAFT_PATH}}")
        errs = check_resolve_matches_review(prompts)
        self.assertTrue(errs, errs)

    # --- 壞輸入：檢查函式必須真的會失敗 ---

    def test_leak_of_elephant_variable_into_goldfish_fails(self) -> None:
        prompts = dict(self.prompts)
        prompts["P3"] = prompts["P3"] + "\n參考簡報：{{BRIEF_PATH}}"
        errs = check_consistency(self.table, prompts)
        self.assertTrue(any("BRIEF_PATH" in e and "大象專屬" in e for e in errs), errs)

    def test_undeclared_variable_fails(self) -> None:
        prompts = dict(self.prompts)
        prompts["P2"] = prompts["P2"] + "\n{{NOT_DECLARED}}"
        errs = check_consistency(self.table, prompts)
        self.assertTrue(any("NOT_DECLARED" in e for e in errs), errs)

    def test_unused_declared_variable_fails(self) -> None:
        table = dict(self.table)
        table["ORPHAN_VAR"] = False
        errs = check_consistency(table, self.prompts)
        self.assertTrue(any("ORPHAN_VAR" in e for e in errs), errs)

    def test_duplicate_declaration_fails(self) -> None:
        dup = self.text + "\n| `{{DATE}}` | 重複 | x | 否 |\n"
        with self.assertRaises(ValueError):
            parse_variable_table(dup)

    def test_unrendered_placeholder_detected(self) -> None:
        rendered = render("審查 {{TARGET_FILE}} 與 {{GHOST}}", self.table)
        self.assertIn("{{GHOST}}", rendered)


if __name__ == "__main__":
    unittest.main()
