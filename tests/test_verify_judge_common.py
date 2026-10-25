#!/usr/bin/env python3
"""
tests/test_verify_judge_common.py
測試 tools/_judge_common.py 與各外部裁判驗證器的「反作弊」行為：
1. 把真實文件整份包進 HTML 註解、程式碼區塊或壓成一行，驗證器必須判定失敗（關鍵字出現在無關位置不算數）。
2. 共用函式（註解/程式碼區塊剝除、標題計數、repo 根推導）的行為。
3. 各驗證器 main() 在 cp950 這類無法編碼 emoji 的 stdout 下不得丟 UnicodeEncodeError。
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import _judge_common as jc  # noqa: E402
import verify_academic_and_latex_guard as vag  # noqa: E402
import verify_agent_reach_and_data_specs as var  # noqa: E402
import verify_claude_security_config as vcs  # noqa: E402
import verify_compliance_and_matrix_docs as vcm  # noqa: E402
import verify_generative_ui_assets as vgu  # noqa: E402
import verify_incident_and_workflow_specs as vis  # noqa: E402
import verify_no_slop as vns  # noqa: E402
import verify_pstack_and_fullstack_specs as vps  # noqa: E402
import verify_re_and_android_specs as vre  # noqa: E402
import verify_story_structure as vss  # noqa: E402

# (相對路徑, verifier) -- 這些 verifier 都接受內文字串並回傳 List[str]
DOC_VERIFIERS = [
    ("templates/latex-citation-protection-prompt.md", vag.verify_latex_citation_protection_prompt),
    ("templates/academic-reading-prompt.md", vag.verify_academic_reading_prompt),
    ("docs/academic-reading-smoke-report.md", vag.verify_academic_reading_smoke_report),
    ("docs/zeabur-incident-credential-audit.md", vis.verify_zeabur_audit),
    ("templates/platform-breach-response.md", vis.verify_platform_breach_response),
    ("docs/web-to-app-evaluation.md", vis.verify_web_to_app_evaluation),
    ("docs/web-to-app-freelance-workflow.md", vis.verify_web_to_app_workflow),
    ("docs/pstack-agent-playbooks.md", vps.verify_pstack_playbooks),
    ("docs/claude-plugins-official-review.md", vps.verify_claude_plugins_review),
    ("templates/fullstack-website-builder-skill.md", vps.verify_fullstack_website_builder),
    ("templates/subject-inventory-argument-writing-prompt.md", vps.verify_subject_inventory_prompt),
    ("docs/reverse-engineering-pipeline-spec.md", vre.verify_re_pipeline_spec),
    ("docs/rea-sandbox-evaluation-evidence.md", vre.verify_rea_sandbox_evidence),
    ("docs/android-official-skills-anti-hallucination.md", vre.verify_android_skills_anti_hallucination),
    ("docs/android-cli-plugin-windows-validation.md", vre.verify_android_cli_validation),
]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


class TestCommonHelpers(unittest.TestCase):
    def test_strip_html_comments(self):
        self.assertEqual(jc.strip_html_comments("a<!-- x\ny -->b"), "ab")

    def test_headings_in_fences_do_not_count(self):
        text = "# T\n```\n# not heading\n```\n## Real\n"
        self.assertEqual(jc.count_headings(text), 2)

    def test_headings_in_comments_do_not_count(self):
        self.assertEqual(jc.count_headings("<!--\n# a\n## b\n### c\n-->\ntext"), 0)

    def test_structural_floor(self):
        self.assertTrue(jc.structural_floor("# a\n## b"))
        self.assertEqual(jc.structural_floor("# a\n## b\n### c"), [])

    def test_find_repo_root_explicit_and_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(jc.find_repo_root(Path(tmp)), Path(tmp).resolve())
        self.assertEqual(jc.find_repo_root(markers=("notes", "docs"), anchor=Path(__file__)), REPO_ROOT)

    def test_report_results_exit_codes(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            self.assertEqual(jc.report_results({"a.md": []}, "ok"), 0)
            self.assertEqual(jc.report_results({"a.md": ["bad"]}, "ok"), 1)
        finally:
            sys.stdout = old
        self.assertIn("[FAIL]", buf.getvalue())


class TestKeywordsMustBeVisibleAndStructured(unittest.TestCase):
    """真實文件經過「藏起來」的改造後，必須讓驗證器失敗。"""

    def test_real_docs_pass_baseline(self):
        for rel, fn in DOC_VERIFIERS:
            with self.subTest(doc=rel):
                self.assertEqual(fn(_read(rel)), [])

    def test_wrapped_in_html_comment_fails(self):
        for rel, fn in DOC_VERIFIERS:
            with self.subTest(doc=rel):
                text = _read(rel).replace("-->", "")
                self.assertTrue(fn("<!--\n" + text + "\n-->"), "整份文件藏在註解內不得通過")

    def test_wrapped_in_code_fence_fails(self):
        for rel, fn in DOC_VERIFIERS:
            with self.subTest(doc=rel):
                text = _read(rel).replace("```", "")
                self.assertTrue(fn("```\n" + text + "\n```"), "整份文件塞進程式碼區塊不得通過")

    def test_flattened_to_one_line_fails(self):
        for rel, fn in DOC_VERIFIERS:
            with self.subTest(doc=rel):
                text = _read(rel)
                self.assertTrue(fn(" ".join(text.splitlines())), "壓成一行(無標題結構)不得通過")


class TestOtherValidators(unittest.TestCase):
    def test_security_clause_number_and_title_must_be_one_heading(self):
        tpl = REPO_ROOT / "templates/claude-security-guidance.md"
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "t.md"
            fake.write_text(
                "```markdown\n條款一 條款二 條款三 條款四\n"
                "憑證與敏感資訊零暴露 工作目錄與檔案邊界防禦 代碼真實性與禁止空殼實作 高危執行階段函式與指令注入防範\n```\n",
                encoding="utf-8",
            )
            self.assertTrue(vcs.verify_security_guidance_template(fake), "編號與名稱散落各處不得通過")
        self.assertEqual(vcs.verify_security_guidance_template(tpl), [])

    def test_security_template_commented_out_block_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "t.md"
            fake.write_text(
                "<!--\n```markdown\n### 條款一：憑證與敏感資訊零暴露\n### 條款二：工作目錄與檔案邊界防禦\n"
                "### 條款三：代碼真實性與禁止空殼實作\n### 條款四：高危執行階段函式與指令注入防範\n```\n-->\n",
                encoding="utf-8",
            )
            self.assertTrue(vcs.verify_security_guidance_template(fake))

    def test_compliance_commented_checklist_fails(self):
        text = _read("docs/ai-persona-compliance-checklist.md").replace("-->", "")
        res = vcm.verify_persona_compliance_checklist("<!--\n" + text + "\n-->")
        self.assertFalse(res.is_valid)

    def test_agent_reach_commented_skill_fails(self):
        text = _read("templates/public-apis-search-skill.md").replace("-->", "")
        self.assertTrue(var.verify_public_apis_search_skill("<!--\n" + text + "\n-->"))

    def _story(self, foreshadowing):
        node = "少年立志登高峰，手握木劍向天指，誓斬惡龍救故里，無懼風雪踏荒山。"
        return {
            "nodes": {n: {"text": node} for n in "ABCDEFG"},
            "arrows": {
                "H1": {"text": "心境昇華超原志，守護眾生化英雄。"},
                "H2": {"text": "洞悉弱點破重圍，化解困局覓生機。"},
                "H3": {"text": "深入險境探秘道，觸發古陣引異象。"},
            },
            "foreshadowing": foreshadowing,
        }

    def test_story_requires_three_good_foreshadowings(self):
        good = [
            {"clue_node": "A", "reveal_node": "D"},
            {"clue_node": "B", "reveal_node": "F"},
            {"clue_node": "C", "reveal_node": "E"},
        ]
        self.assertTrue(vss.verify_story_structure(self._story(good)).is_valid)
        self.assertFalse(vss.verify_story_structure(self._story([])).is_valid, "沒有任何伏筆不得通過")
        self.assertFalse(vss.verify_story_structure(self._story(good[:2])).is_valid, "不足 3 組不得通過")
        too_tight = good[:2] + [{"clue_node": "C", "reveal_node": "D"}]
        self.assertFalse(vss.verify_story_structure(self._story(too_tight)).is_valid, "太緊的伏筆不得通過")

    def test_story_main_bad_json_returns_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            self.assertEqual(vss.main(["--input", str(bad)]), 1)


class TestCp950Stdout(unittest.TestCase):
    """模擬 Windows cp950 終端: main() 不得因 emoji 丟 UnicodeEncodeError。"""

    def test_mains_survive_cp950(self):
        mains = [
            vag.main,
            vis.main,
            vps.main,
            vre.main,
            vgu.main,
            var.main,
            lambda argv: vns.main([str(REPO_ROOT / "assets/anti-slop-demo/index.html")]),
        ]
        old_out, old_err = sys.stdout, sys.stderr
        try:
            for fn in mains:
                raw = io.BytesIO()
                wrapper = io.TextIOWrapper(raw, encoding="cp950", errors="strict")
                sys.stdout = wrapper
                sys.stderr = wrapper
                try:
                    code = fn([])
                    wrapper.flush()
                finally:
                    sys.stdout, sys.stderr = old_out, old_err
                    wrapper.detach()
                self.assertEqual(code, 0)
        finally:
            sys.stdout, sys.stderr = old_out, old_err


if __name__ == "__main__":
    unittest.main()
