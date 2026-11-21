"""tools/review_pipeline.py：分道、審查指示來自 SOP、報告格式與入帳的防呆。"""

import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import review_ledger as rl  # noqa: E402
import review_pipeline as rp  # noqa: E402
from test_review_ledger import AUTHOR, REVIEWER, WEAK, Base  # noqa: E402

SOP_PATH = Path(__file__).resolve().parent.parent / "docs" / "source-review-sop.md"


def report(verdict="pass", findings=(), scope=rl.SCOPES, source_review="full", corrections=None, extra=""):
    data = {"verdict": verdict, "source_review": source_review, "source_images": 1, "source_replies": 3,
            "corrections": len(findings) if corrections is None else corrections, "scope": list(scope),
            "findings": list(findings), "task_impact": []}
    return f"# 報告\n\n逐項結果……{extra}\n\n```json\n{json.dumps(data, ensure_ascii=False)}\n```\n"


class PipelineBase(Base):
    def setUp(self):
        super().setUp()
        (self.root / "docs").mkdir()
        (self.root / "docs" / "source-review-sop.md").write_text(SOP_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    def ingest(self, text, reviewer=REVIEWER, role="review", scope=rl.SCOPES, sha=None, claim="full"):
        return rp.ingest(self.slug, text, reviewer, "codex", role, list(scope), sha or self.sha(), claim,
                         root=self.root, today=dt.date(2026, 11, 23))


class LaneTest(PipelineBase):
    def orders(self, note):
        st = rl.evaluate(note, {}, dt.date(2026, 11, 23), self.root)
        return rp.orders_for(note, st)

    def test_social_note_splits_source_to_chrome(self):
        note = self.write_note()
        note.meta["source_url"] = "https://www.threads.com/@someone/post/abc"
        lanes = {(o.lane, tuple(o.scopes)) for o in self.orders(note)}
        self.assertEqual({("chrome", ("source",)), ("codex", ("facts", "evidence", "task_impact"))}, lanes)

    def test_non_social_note_goes_to_codex(self):
        note = self.write_note()
        orders = self.orders(note)
        self.assertEqual([("codex", list(rl.SCOPES))], [(o.lane, o.scopes) for o in orders])

    def test_changes_requested_goes_to_fix_lane(self):
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=1)
        self.assertEqual(["fix"], [o.lane for o in self.orders(bi.parse_note(self.root / "notes" / f"{self.slug}.md"))])

    def test_only_source_missing_goes_to_chrome_even_for_non_social(self):
        self.write_note()
        self.add_review(scope=["facts", "evidence", "task_impact"])
        orders = self.orders(bi.parse_note(self.root / "notes" / f"{self.slug}.md"))
        self.assertEqual([("chrome", ["source"])], [(o.lane, o.scopes) for o in orders])

    def test_weak_review_produces_audit_order(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        orders = self.orders(bi.parse_note(self.root / "notes" / f"{self.slug}.md"))
        self.assertEqual([("codex", "audit")], [(o.lane, o.role) for o in orders])


class PromptTest(PipelineBase):
    def test_prompt_embeds_sop_sections_verbatim(self):
        note = self.write_note()
        order = rp.orders_for(note, rl.evaluate(note, {}, dt.date(2026, 11, 23), self.root))[0]
        prompt = rp.build_prompt(note, order, self.root)
        for name in ("REVIEW-CHECKLIST", "FULL-CRITERIA"):
            self.assertIn(rp.sop_section(name, self.root), prompt)
        self.assertIn(order.sha, prompt)
        self.assertNotIn(rp.sop_section("BROWSER-PRACTICE", self.root), prompt)  # codex 道不需要瀏覽器實務
        order.lane = "chrome"
        self.assertIn(rp.sop_section("BROWSER-PRACTICE", self.root), rp.build_prompt(note, order, self.root))

    def test_sop_edit_flows_into_prompt(self):
        sop = self.root / "docs" / "source-review-sop.md"
        sop.write_text(sop.read_text(encoding="utf-8").replace("#### 審查清單", "#### 審查清單（新增一條：XYZZY）"), encoding="utf-8")
        self.assertIn("XYZZY", rp.sop_section("REVIEW-CHECKLIST", self.root))

    def test_missing_sop_markers_fail_loudly(self):
        (self.root / "docs" / "source-review-sop.md").write_text("# 空的 SOP\n", encoding="utf-8")
        with self.assertRaises(rp.PipelineError):
            rp.sop_section("REVIEW-CHECKLIST", self.root)

    def test_repo_sop_has_all_sections(self):
        for name in ("REVIEW-CHECKLIST", "FULL-CRITERIA", "BROWSER-PRACTICE"):
            self.assertTrue(rp.sop_section(name))


class IngestTest(PipelineBase):
    def test_valid_report_is_recorded_and_passes_verifier(self):
        self.write_note()
        entry = self.ingest(report())
        self.assertEqual("pass", entry["verdict"])
        body = (self.root / entry["report"]).read_text(encoding="utf-8")
        self.assertIn(entry["content_sha256"], body)
        st = rl.evaluate(bi.parse_note(self.root / "notes" / f"{self.slug}.md"), {}, dt.date(2026, 11, 23), self.root)
        self.assertTrue(st.reviewed, (st.needs, st.errors))

    def test_stale_note_rejected(self):
        self.write_note()
        sha = self.sha()
        path = self.root / "notes" / f"{self.slug}.md"
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "審查期間被改"), encoding="utf-8")
        with self.assertRaises(rp.PipelineError) as ctx:
            self.ingest(report(), sha=sha)
        self.assertIn("被改過", str(ctx.exception))

    def test_self_review_rejected(self):
        self.write_note()
        with self.assertRaises(rp.PipelineError):
            self.ingest(report(), reviewer=AUTHOR)

    def test_weak_audit_rejected(self):
        self.write_note()
        with self.assertRaises(rp.PipelineError):
            self.ingest(report(), reviewer=WEAK, role="audit")

    def test_malformed_reports_rejected(self):
        finding = {"kind": "fact", "claim": "x", "problem": "y", "evidence": "https://example.com", "fix": "z"}
        bad = [
            "# 沒有 json",
            report().replace('"verdict": "pass"', '"verdict": "maybe"'),
            report(findings=[finding]),  # 有 findings 卻 pass
            report(verdict="changes_requested", findings=[finding], corrections=3),
            report(verdict="changes_requested", findings=[{**finding, "evidence": ""}]),  # 更正沒附出處
            report(scope=["facts", "vibes"]),  # 範圍不在派工內
            report(scope=[]),
            report(verdict="changes_requested", scope=["facts"], findings=[{**finding, "kind": "source"}]),  # 沒審 source 卻怪筆記
            "```json\n{\"verdict\": \"pass\"}\n```",
        ]
        for text in bad:
            self.setUp()
            self.write_note()
            with self.assertRaises(rp.PipelineError, msg=text[:80]):
                self.ingest(text)
            self.assertFalse((self.root / "reviews" / f"{self.slug}.json").exists())

    def test_reviewer_may_drop_scope_it_could_not_do(self):
        self.write_note()
        entry = self.ingest(report(scope=["facts", "evidence", "task_impact"], source_review="partial"))
        self.assertEqual(["facts", "evidence", "task_impact"], entry["scope"])
        self.assertEqual("full", entry["source_review"])  # 沒審 source 就不判定讀完度
        st = rl.evaluate(bi.parse_note(self.root / "notes" / f"{self.slug}.md"), {}, dt.date(2026, 11, 23), self.root)
        self.assertFalse(st.reviewed)
        self.assertTrue(any("source" in n for n in st.needs), st.needs)

    def test_report_taken_from_events_not_last_message(self):
        body = report()
        events = "\n".join(json.dumps(e, ensure_ascii=False) for e in [
            {"type": "thread.started", "thread_id": "t-1"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "開始審查"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": body}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "已補核對，結論不變。"}},
        ]) + "\nnot json\n"
        self.assertEqual(body, rp.report_from_events(events))
        self.assertEqual("", rp.report_from_events("{}\n"))

    def test_last_json_block_wins(self):
        self.write_note()
        text = "```json\n{\"verdict\": \"pass\"}\n```\n" + report(verdict="changes_requested", findings=[
            {"kind": "fact", "claim": "x", "problem": "y", "evidence": "https://example.com", "fix": "z"}])
        self.assertEqual("changes_requested", self.ingest(text)["verdict"])

    def test_home_paths_are_masked_in_report(self):
        self.write_note()
        entry = self.ingest(report(extra=r" 讀了 C:\Users\realname\x.md 與 /home/realname/y"))
        body = (self.root / entry["report"]).read_text(encoding="utf-8")
        self.assertNotIn("realname", body)
        self.assertIn("%USERPROFILE%", body)

    def test_scope_without_source_keeps_author_claim(self):
        self.write_note()
        entry = self.ingest(report(scope=["facts", "evidence", "task_impact"], source_review="partial"),
                            scope=["facts", "evidence", "task_impact"])
        self.assertEqual("full", entry["source_review"])


if __name__ == "__main__":
    unittest.main()
