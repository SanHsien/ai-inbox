"""templates/team-dispatch-skill-template.md 的測試：frontmatter 預算稽核、放行正規式、內附 append_handoff.py 實跑。"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "team-dispatch-skill-template.md"
AUDIT = ROOT / "tools" / "audit_skills_context_budget.py"
NOTES_MARK = "\n## 範本使用說明（交付前刪除）"


def split_template():
    text = TEMPLATE.read_text(encoding="utf-8")
    head, sep, notes = text.partition(NOTES_MARK)
    assert sep, "找不到範本使用說明分隔標題"
    head = head.rstrip()
    if head.endswith("---"):
        head = head[:-3].rstrip()
    return head + "\n", notes


def script_from_notes(notes):
    m = re.search(r"```python\n(.*?)\n```", notes, re.S)
    assert m, "使用說明裡找不到 python 程式碼區塊"
    return m.group(1) + "\n"


class TemplateStructureTest(unittest.TestCase):
    def test_skill_part_passes_budget_audit_strict(self):
        skill, _ = split_template()
        with tempfile.TemporaryDirectory() as d:
            sk = Path(d) / "team-dispatch"
            sk.mkdir()
            (sk / "SKILL.md").write_text(skill, encoding="utf-8")
            r = subprocess.run([sys.executable, str(AUDIT), d, "--strict"], capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_audit_would_fail_if_name_folder_or_frontmatter_broken(self):
        # 反例：確認上面的稽核不是恆真。
        skill, _ = split_template()
        with tempfile.TemporaryDirectory() as d:
            sk = Path(d) / "team-dispatch"
            sk.mkdir()
            (sk / "SKILL.md").write_text(skill.replace("name: team-dispatch", "name: Claude_Team", 1), encoding="utf-8")
            r = subprocess.run([sys.executable, str(AUDIT), d, "--strict"], capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertNotEqual(r.returncode, 0)

    def test_four_column_header_and_four_states_present(self):
        skill, _ = split_template()
        header = "| 要做哪一塊（含項次） | 由誰做 | 怎麼派、怎麼回（理由） | 完成證據 |"
        self.assertIn(header, skill)
        for state in ("完成", "完成但有疑慮", "需要資料", "卡住"):
            self.assertRegex(skill, rf"- {state}：")

    def test_placeholders_are_all_in_braces_and_documented_for_fill_in(self):
        skill, _ = split_template()
        self.assertGreaterEqual(len(re.findall(r"\{[^{}\n]+\}", skill)), 4)

    def test_no_forbidden_antigravity_path_taught(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        # 只能以「不使用」的形式出現；不得有任何 agy -p 的使用示範或 8045 轉送。
        for m in re.finditer(r"agy\s+-p", text):
            self.assertIn("不使用", text[max(0, m.start() - 10) : m.start()])
        self.assertNotIn("8045", text)


class DispatchRegexTest(unittest.TestCase):
    def setUp(self):
        skill, _ = split_template()
        m = re.search(r"必須完全符合 `([^`]+)`", skill)
        self.assertIsNotNone(m, "步驟 3 找不到放行正規式")
        self.rx = re.compile(m.group(1))

    def accepts(self, s):
        return bool(self.rx.match(s.strip()))

    def test_accepts_valid_release_messages(self):
        for s in ("派", " 派 ", "派 1", "派 1,3", "派 1, 3", "派1,3", "派 1，3", "派 1、3、5"):
            with self.subTest(s=s):
                self.assertTrue(self.accepts(s))

    def test_rejects_everything_else(self):
        for s in ("", "好", "OK", "可以", "派吧", "請派", "派 ", "派,1", "派 a", "派 1,", "派 ,1", "不派", "派\n派", "派 全部", "dispatch", "派工"):
            with self.subTest(s=s):
                # 注意 .strip() 之後 "派 " 會變成 "派"，那是合法的，所以不用它當反例。
                if s.strip() == "派":
                    continue
                self.assertFalse(self.accepts(s))


class HandoffScriptTest(unittest.TestCase):
    def setUp(self):
        _, notes = split_template()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.script = self.root / "append_handoff.py"
        self.script.write_text(script_from_notes(notes), encoding="utf-8")
        (self.root / ".team-dispatch").mkdir()
        self.pending = self.root / ".team-dispatch" / "pending-handoff.json"
        self.handoff = self.root / "HANDOFF.md"

    def run_hook(self, payload=None, raw=None):
        stdin = raw if raw is not None else json.dumps(payload if payload is not None else {"cwd": str(self.root)})
        return subprocess.run([sys.executable, str(self.script)], input=stdin, capture_output=True, text=True, encoding="utf-8", timeout=60)

    def row(self, **kw):
        base = {"item": "1. 重構匯入", "owner": "本機主控", "status": "完成", "evidence": "pytest exit 0; abc1234", "pitfall": "無"}
        base.update(kw)
        return base

    def put(self, rows, version="v2"):
        self.pending.write_text(json.dumps({"split_version": version, "rows": rows}, ensure_ascii=False), encoding="utf-8")

    def test_valid_pending_appends_and_is_consumed(self):
        self.put([self.row(), self.row(item="2. 審查", owner="Antigravity", status="完成但有疑慮", evidence="審查結論 + 1 條建議")])
        r = self.run_hook()
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.handoff.read_text(encoding="utf-8")
        self.assertIn("## 派工沉澱 v2", text)
        self.assertIn("1. 重構匯入", text)
        self.assertIn("2. 審查", text)
        self.assertFalse(self.pending.exists())

    def test_appends_without_overwriting_existing_handoff(self):
        self.handoff.write_text("# HANDOFF\n舊內容\n", encoding="utf-8")
        self.put([self.row()])
        self.assertEqual(self.run_hook().returncode, 0)
        text = self.handoff.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# HANDOFF\n舊內容\n"))
        self.assertIn("派工沉澱", text)

    def test_no_pending_is_a_noop(self):
        r = self.run_hook()
        self.assertEqual(r.returncode, 0)
        self.assertFalse(self.handoff.exists())

    def test_empty_or_garbage_stdin_does_not_crash(self):
        self.assertEqual(self.run_hook(raw="").returncode, 0)
        self.assertEqual(self.run_hook(raw="not json").returncode, 0)

    def assert_rejected(self, rows=None, raw_pending=None):
        if raw_pending is not None:
            self.pending.write_text(raw_pending, encoding="utf-8")
        else:
            self.put(rows)
        r = self.run_hook()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotEqual(r.returncode, 2)  # exit 2 在 Stop 事件會要求 Claude 繼續
        self.assertFalse(self.handoff.exists())
        self.assertTrue(self.pending.exists())

    def test_done_without_evidence_is_rejected(self):
        self.assert_rejected([self.row(evidence="   ")])

    def test_unknown_status_is_rejected(self):
        self.assert_rejected([self.row(status="done")])
        self.assert_rejected([self.row(status="差不多")])

    def test_empty_rows_is_rejected(self):
        self.assert_rejected([])

    def test_missing_field_is_rejected(self):
        bad = self.row()
        del bad["owner"]
        self.assert_rejected([bad])

    def test_corrupt_pending_is_rejected(self):
        self.assert_rejected(raw_pending="{broken")

    def test_non_done_state_may_have_empty_evidence_only_if_state_is_not_done(self):
        self.put([self.row(status="需要資料", evidence="缺：客戶名單欄位定義")])
        self.assertEqual(self.run_hook().returncode, 0)


if __name__ == "__main__":
    unittest.main()
