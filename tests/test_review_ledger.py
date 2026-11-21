"""tools/review_ledger.py：獨立審查紀錄的每條失敗條件都要有反例（docs/review-pipeline-plan.md 2.2、2.5 節）。"""

import datetime as dt
import hashlib
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_index as bi  # noqa: E402
import review_ledger as rl  # noqa: E402
import task_cli as tc  # noqa: E402

TODAY = dt.date(2026, 11, 25)
AUTHOR = "claude/opus-5.5@author-session-1"
REVIEWER = "codex/gpt-6.1-sol@019a-reviewer"
AUDITOR = "claude/opus-5.5@auditor-session-9"
WEAK = "claude/sonnet-5.5@sonnet-session-3"

NOTE = """---
id: {slug}
title: "測試筆記"
source_url: "https://example.com/post"
analyzed_at: 2026-11-22
written_by: "{written_by}"
status: pending
cluster: 1
cluster_role: "測試"
short_title: "測試"
source_review: full
source_reviewed_at: 2026-11-22
source_images: 1
source_replies: 3
{extra_meta}---

# 測試筆記

- **當前狀態**：`🔴 未做 (Pending)`

本文主張 {claim}。

- [ ] **`T-20261122-01`**｜**[優先級：中]** 任務
  - **目標範圍**：`some/repo`
  - **驗收標準（DoD）**：做完
"""


class Base(unittest.TestCase):
    def setUp(self):
        if getattr(self, "_tmp", None):  # 同一測試內重設環境時，先清掉上一個暫存目錄
            self._tmp.cleanup()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "notes").mkdir()
        (self.root / "reviews").mkdir()
        self.slug = "2026-11-22-test-note"

    def tearDown(self):
        self._tmp.cleanup()

    def write_note(self, written_by=AUTHOR, extra_meta="", claim=None, want_sampled=False):
        """寫筆記；預設挑一個不會被抽查（雜湊 mod 5 != 0）的版本，want_sampled=True 則挑會被抽中的。"""
        path = self.root / "notes" / f"{self.slug}.md"
        for i in range(200):
            text = NOTE.format(slug=self.slug, written_by=written_by, extra_meta=extra_meta, claim=claim or f"X{i}")
            sampled = int(rl.content_hash(text)[:8], 16) % rl.SAMPLE_MODULO == 0
            if sampled == want_sampled or claim:
                break
        path.write_text(text, encoding="utf-8")
        return bi.parse_note(path)

    def sha(self):
        return rl.content_hash((self.root / "notes" / f"{self.slug}.md").read_text(encoding="utf-8"))

    def add_review(self, reviewer=REVIEWER, sha=None, n=None, report_body=None, **over):
        path = self.root / "reviews" / f"{self.slug}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"note": self.slug, "reviews": []}
        n = n if n is not None else len(data["reviews"]) + 1
        sha = sha or self.sha()
        report = f"reviews/reports/{self.slug}/2026-11-23-{n}.md"
        rp = self.root / report
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(report_body if report_body is not None else f"# 審查報告\n\n- reviewer: {reviewer}\n- content_sha256: {sha}\n", encoding="utf-8")
        entry = {
            "reviewed_at": "2026-11-23", "reviewer": reviewer, "role": "review",
            "scope": list(rl.SCOPES), "content_sha256": sha, "verdict": "pass",
            "source_review": "full", "author_claim": "full", "corrections": 0, "report": report,
        }
        entry.update(over)
        data["reviews"].append(entry)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return entry

    def state(self, note=None, legacy=None, today=TODAY):
        note = note or bi.parse_note(self.root / "notes" / f"{self.slug}.md")
        return rl.evaluate(note, legacy or {}, today, self.root)


class HashTest(Base):
    def test_task_state_changes_do_not_change_hash(self):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        before = self.sha()
        tc.apply_claim(path, "T-20261122-01")
        self.assertEqual(before, self.sha())
        tc.apply_complete(path, "T-20261122-01", "commit abc\n多行", "2026-11-24")
        self.assertEqual(before, self.sha())
        self.assertIn("status: done", path.read_text(encoding="utf-8"))

    def test_close_and_crlf_do_not_change_hash(self):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        before = self.sha()
        tc.apply_close(path, "T-20261122-01", "不做")
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual(before, self.sha())

    def test_any_analysis_edit_changes_hash(self):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        before = self.sha()
        for old, new in (("本文主張", "本文改口主張"), ("source_review: full", "source_review: partial"),
                         ("做完", "做一半"), ("[優先級：中]", "[優先級：高]")):
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            self.assertNotEqual(before, self.sha(), old)
            path.write_text(text, encoding="utf-8")

    def test_new_task_changes_hash(self):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n- [ ] **`T-20261122-02`**｜**[優先級：高]** 建立在錯誤前提上的新任務\n  - **目標範圍**：x\n")
        self.assertNotEqual(before, self.sha())


class HashHidingTest(Base):
    """雜湊略過的欄位不能拿來藏分析內容。"""

    def changed_by(self, addition, anchor="本文主張"):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        before = self.sha()
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(anchor, addition + anchor, 1), encoding="utf-8")
        return before != self.sha()

    def test_state_field_outside_task_block_is_hashed(self):
        self.assertTrue(self.changed_by("  - **狀態**：其實官方說沒有版權風險\n\n"))
        self.assertTrue(self.changed_by("  - **實作紀錄 / 證據**：偷加的結論\n    - 更多偷加的內容\n\n"))

    def test_second_status_line_is_hashed(self):
        self.assertTrue(self.changed_by("- **當前狀態**：偷加的第二行狀態\n\n"))

    def test_checkbox_outside_task_line_is_hashed(self):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n後記：新增一段分析。\n")
        self.assertNotEqual(before, self.sha())

    def test_indented_text_after_state_field_ends_with_task_block(self):
        self.write_note()
        path = self.root / "notes" / f"{self.slug}.md"
        tc.apply_complete(path, "T-20261122-01", "commit abc", "2026-11-24")
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n## 新段落\n\n    縮排的新主張（不屬於任務欄位）\n")
        self.assertNotEqual(before, self.sha())


class GovernanceTest(Base):
    def test_edited_legacy_note_needs_a_real_author(self):
        note = self.write_note(written_by=rl.LEGACY_AUTHOR)
        st = self.state(note, legacy={self.slug: "0" * 64})
        self.assertTrue(any("還要加上改的人" in e for e in st.errors), st.errors)
        note = self.write_note(written_by=f"{rl.LEGACY_AUTHOR}; {AUTHOR}")
        self.assertEqual([], self.state(note, legacy={self.slug: "0" * 64}).errors)

    def test_legacy_placeholder_rejected_on_new_note(self):
        st = self.state(self.write_note(written_by=f"{rl.LEGACY_AUTHOR}; {AUTHOR}"))
        self.assertTrue(any("只能用在制度上線前" in e for e in st.errors), st.errors)

    def test_legacy_identity_cannot_review(self):
        self.write_note()
        self.add_review(reviewer=rl.LEGACY_AUTHOR)
        self.assertTrue(any("legacy 佔位身分" in e for e in self.state().errors))

    def test_backfill_evaluates_unchanged_legacy_note(self):
        note = self.write_note(written_by="")
        legacy = {self.slug: self.sha()}
        st = rl.evaluate(note, legacy, TODAY, self.root, backfill=True)
        self.assertFalse(st.governed)
        self.assertFalse(st.reviewed)
        self.assertEqual([], st.errors)  # 補審不算寬限、不要求 written_by
        self.add_review()
        st = rl.evaluate(note, legacy, TODAY, self.root, backfill=True)
        self.assertTrue(st.reviewed, st.needs)

    def test_unchanged_legacy_note_exempt(self):
        note = self.write_note(written_by="")
        st = self.state(note, legacy={self.slug: self.sha()})
        self.assertFalse(st.governed)
        self.assertEqual([], st.errors)

    def test_edited_legacy_note_becomes_governed(self):
        note = self.write_note(written_by="")
        st = self.state(note, legacy={self.slug: "0" * 64})
        self.assertTrue(st.governed)
        self.assertTrue(any("written_by" in e and "revised_at" in e for e in st.errors), st.errors)

    def test_missing_or_malformed_written_by(self):
        for wb in ("", "Claude Code", "claude/opus@ab", "robot/x@session-1"):
            st = self.state(self.write_note(written_by=wb))
            self.assertTrue(any("written_by" in e for e in st.errors), (wb, st.errors))

    def test_pending_within_grace_warns_only(self):
        st = self.state(self.write_note(), today=dt.date(2026, 11, 29))
        self.assertTrue(st.pending)
        self.assertEqual([], st.errors)
        self.assertTrue(st.warnings)

    def test_pending_after_grace_fails(self):
        st = self.state(self.write_note(), today=dt.date(2026, 11, 30))
        self.assertTrue(any("超過寬限" in e for e in st.errors), st.errors)

    def test_grace_counts_from_revised_at(self):
        st = self.state(self.write_note(extra_meta="revised_at: 2026-11-28\n"), today=dt.date(2026, 12, 4))
        self.assertEqual([], st.errors)

    def test_future_dates_rejected(self):
        st = self.state(self.write_note(extra_meta="revised_at: 2026-12-31\n"))
        self.assertTrue(any("revised_at" in e for e in st.errors), st.errors)
        st = self.state(self.write_note(extra_meta="revised_at: 2026-11-01\n"))
        self.assertTrue(any("revised_at" in e for e in st.errors), st.errors)
        st = self.state(today=dt.date(2026, 11, 21))
        self.assertTrue(any("analyzed_at" in e for e in st.errors), st.errors)


class ReviewTest(Base):
    def test_valid_independent_review_passes(self):
        self.write_note()
        self.add_review()
        st = self.state()
        self.assertTrue(st.reviewed, (st.needs, st.errors))
        self.assertEqual([], st.errors)

    def test_self_review_rejected(self):
        self.write_note(written_by=f"{AUTHOR}; {REVIEWER}")
        self.add_review()
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("不能審自己寫的內容" in e for e in st.errors), st.errors)

    def test_same_session_different_model_label_is_self_review(self):
        self.write_note(written_by="claude/opus-5.5@SHARED-1")
        self.add_review(reviewer="claude/sonnet-5.5@shared-1")
        self.assertTrue(any("不能審自己寫的內容" in e for e in self.state().errors))

    def test_edit_after_review_needs_rereview(self):
        self.write_note()
        self.add_review()
        path = self.root / "notes" / f"{self.slug}.md"
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "本文偷改主張"), encoding="utf-8")
        st = self.state()
        self.assertTrue(st.pending)
        self.assertFalse(st.reviewed)

    def test_report_must_exist_and_carry_hash_and_reviewer(self):
        self.write_note()
        e = self.add_review()
        (self.root / e["report"]).unlink()
        self.assertTrue(any("報告檔不存在" in x for x in self.state().errors))

        self.setUp()
        self.write_note()
        self.add_review(report_body="# 別篇的報告\n")
        self.assertTrue(any("不能拿別篇" in x for x in self.state().errors))

    def test_report_path_must_be_under_this_notes_folder(self):
        self.write_note()
        self.add_review(report="reviews/reports/other-note/x.md")
        self.assertTrue(any("report 需為" in x for x in self.state().errors))
        self.setUp()
        self.write_note()
        self.add_review(report=f"reviews/reports/{self.slug}/../../../notes/{self.slug}.md")
        self.assertTrue(any("report 需為" in x for x in self.state().errors))

    def test_malformed_fields_rejected(self):
        bad = [{"verdict": "ok"}, {"role": "self"}, {"scope": []}, {"scope": ["vibes"]}, {"content_sha256": "abc"},
               {"corrections": -1}, {"corrections": True}, {"source_review": "text-only"}, {"author_claim": ""},
               {"reviewed_at": "2026-12-31"}, {"reviewed_at": "2026-11-01"}, {"reviewer": "someone"}]
        for over in bad:
            self.setUp()
            self.write_note()
            self.add_review(**over)
            st = self.state()
            self.assertTrue(st.errors, over)
            self.assertFalse(st.reviewed, over)

    def test_pass_with_corrections_rejected(self):
        self.write_note()
        self.add_review(corrections=1)
        self.assertTrue(any("有更正就是 changes_requested" in e for e in self.state().errors))

    def test_pass_source_review_must_match_note(self):
        self.write_note()
        self.add_review(source_review="partial", author_claim="partial")
        self.assertTrue(any("筆記要照審查結論改" in e for e in self.state().errors))

    def test_scope_must_be_covered(self):
        self.write_note()
        self.add_review(scope=["facts", "evidence", "task_impact"])
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("source" in n for n in st.needs), st.needs)
        self.add_review(reviewer="claude/opus-5.5@chrome-lane-7", scope=["source"])
        self.assertTrue(self.state().reviewed)

    def test_review_on_other_hash_does_not_count(self):
        self.write_note()
        self.add_review(sha="a" * 64)
        self.assertFalse(self.state().reviewed)

    def test_changes_requested_blocks_until_fixed(self):
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=1)
        self.add_review(reviewer="codex/gpt-6.1-sol@another-1")
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("修正後再審" in n for n in st.needs), st.needs)

    def test_dates_must_not_go_backwards(self):
        self.write_note()
        self.add_review(reviewed_at="2026-11-24")
        self.add_review(reviewer="codex/gpt-6.1-sol@another-1", reviewed_at="2026-11-23")
        self.assertTrue(any("只能追加" in e for e in self.state().errors))

    def test_ledger_for_wrong_note_rejected(self):
        self.write_note()
        (self.root / "reviews" / f"{self.slug}.json").write_text(json.dumps({"note": "other", "reviews": []}), encoding="utf-8")
        self.assertTrue(self.state().errors)


class EscalationTest(Base):
    def assert_needs_audit(self):
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("強模型覆核" in n for n in st.needs), (st.needs, st.errors))

    def fix_note(self):
        path = self.root / "notes" / f"{self.slug}.md"
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "本文修正後主張"), encoding="utf-8")

    def test_downgrade_full_requires_audit(self):
        self.write_note()
        self.add_review(verdict="changes_requested", source_review="partial", corrections=1)
        path = self.root / "notes" / f"{self.slug}.md"
        path.write_text(path.read_text(encoding="utf-8").replace("source_review: full", "source_review: partial\nsource_review_note: 留言讀到 3／共 5 則"), encoding="utf-8")
        self.add_review(source_review="partial", author_claim="partial")
        self.assert_needs_audit()
        self.add_review(reviewer=AUDITOR, role="audit", source_review="partial", author_claim="partial")
        self.assertTrue(self.state().reviewed, self.state().needs)

    def test_two_corrections_require_audit(self):
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=2)
        self.fix_note()
        self.add_review()
        self.assert_needs_audit()

    def test_weak_reviewer_requires_audit(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.assert_needs_audit()
        self.add_review(reviewer=AUDITOR, role="audit")
        self.assertTrue(self.state().reviewed)

    def test_sampled_hash_requires_audit(self):
        self.write_note(want_sampled=True)
        self.add_review()
        self.assert_needs_audit()
        self.add_review(reviewer=AUDITOR, role="audit")
        self.assertTrue(self.state().reviewed)

    def test_audit_by_weak_model_rejected(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer="claude/sonnet-5.5@other-sonnet", role="audit")
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("強模型執行" in e for e in st.errors), st.errors)

    def test_audit_by_same_session_as_reviewer_rejected(self):
        self.write_note()
        self.add_review(reviewer="codex/gpt-6.1-sol@same-9", verdict="changes_requested", corrections=2)
        self.fix_note()
        self.add_review(reviewer="codex/gpt-6.1-sol@same-9")
        self.add_review(reviewer="codex/gpt-6.1-sol@same-9", role="audit")
        self.assertTrue(any("覆核要換人" in e for e in self.state().errors))

    def test_audit_by_author_rejected(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer=AUTHOR, role="audit")
        self.assertTrue(any("不能審自己寫的內容" in e for e in self.state().errors))

    def test_audit_pass_overrules_false_alarm(self):
        self.write_note()
        self.add_review(reviewer=WEAK, verdict="changes_requested", corrections=1)
        self.add_review(reviewer=AUDITOR, role="audit")
        self.assertTrue(self.state().reviewed, self.state().needs)

    def test_audit_on_old_hash_does_not_clear_new_triggers(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer=AUDITOR, role="audit")
        self.fix_note()
        self.add_review(reviewer="claude/sonnet-5.5@sonnet-2")
        self.assert_needs_audit()


class RepoLevelTest(Base):
    def test_baseline_tamper_detected(self):
        p = self.root / "reviews" / rl.LEGACY_BASELINE_NAME
        p.write_text(json.dumps({"notes": {"2026-11-22-sneaky": "0" * 64}}), encoding="utf-8")
        legacy, errors = rl.load_legacy(self.root)
        self.assertEqual({}, legacy)
        self.assertTrue(any("LEGACY_BASELINE_SHA256" in e for e in errors), errors)

    def test_baseline_matching_constant_loads(self):
        p = self.root / "reviews" / rl.LEGACY_BASELINE_NAME
        raw = json.dumps({"notes": {self.slug: "0" * 64}}).encode()
        p.write_bytes(raw)
        with unittest.mock.patch.object(rl, "LEGACY_BASELINE_SHA256", hashlib.sha256(raw).hexdigest()):
            legacy, errors = rl.load_legacy(self.root)
        self.assertEqual({self.slug: "0" * 64}, legacy)
        self.assertEqual([], errors)

    def test_repo_baseline_matches_constant(self):
        legacy, errors = rl.load_legacy()
        self.assertEqual([], errors)
        self.assertTrue(legacy)

    def test_orphan_ledger_detected(self):
        self.write_note()
        (self.root / "reviews" / "2026-11-22-ghost.json").write_text(json.dumps({"note": "2026-11-22-ghost", "reviews": []}), encoding="utf-8")
        _, errors = rl.evaluate_all([bi.parse_note(self.root / "notes" / f"{self.slug}.md")], TODAY, self.root)
        self.assertTrue(any("ghost" in e for e in errors), errors)

    def test_task_cli_refuses_claim_and_complete_on_pending_note(self):
        note = self.write_note()
        for cmd, args in ((tc.cmd_claim, tc.argparse.Namespace(task_id="T-20261122-01")),
                          (tc.cmd_complete, tc.argparse.Namespace(task_id="T-20261122-01", evidence="x", date=None))):
            with unittest.mock.patch.object(tc.bi, "load_notes", return_value=[note]), \
                    unittest.mock.patch.object(tc.bi, "main"), \
                    unittest.mock.patch.object(rl, "pending_slugs", return_value={self.slug}):
                with self.assertRaises(ValueError) as ctx:
                    cmd(args)
            self.assertIn("獨立審查", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
