"""tools/review_pipeline.py：分道、審查指示來自 SOP、報告格式與入帳的防呆、提交流程只動專用工作樹。"""

import contextlib
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import review_ledger as rl  # noqa: E402
import review_pipeline as rp  # noqa: E402
import task_cli as tc  # noqa: E402
from test_review_ledger import (  # noqa: E402
    AUDITOR, AUTHOR, FINDING, NOTE, OTHER_CODEX, REVIEWER, WEAK, Base, run_git, sess)

SOP_PATH = Path(__file__).resolve().parent.parent / "docs" / "source-review-sop.md"
INGEST_DAY = dt.date(2026, 11, 23)


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

    def ingest(self, text, reviewer=REVIEWER, role="review", scope=rl.SCOPES, sha=None, **kw):
        return rp.ingest(self.slug, text, reviewer, "codex", role, list(scope), sha or self.sha(),
                         root=self.root, today=INGEST_DAY, **kw)


class LaneTest(PipelineBase):
    def orders(self, note, legacy=None):
        st = rl.evaluate(note, legacy or {}, dt.date(2026, 11, 23), self.root)
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
        self.assertEqual(["fix"], [o.lane for o in self.orders(bi.parse_note(self.note_path()))])

    def test_only_source_missing_goes_to_chrome_even_for_non_social(self):
        self.write_note()
        self.add_review(scope=["facts", "evidence", "task_impact"])
        orders = self.orders(bi.parse_note(self.note_path()))
        self.assertEqual([("chrome", ["source"])], [(o.lane, o.scopes) for o in orders])

    def test_weak_review_produces_audit_order(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        orders = self.orders(bi.parse_note(self.note_path()))
        self.assertEqual([("codex", "audit")], [(o.lane, o.role) for o in orders])
        self.assertEqual(list(rl.SCOPES), orders[0].scopes)

    def test_flagged_legacy_note_goes_to_fix_lane(self):
        """F7：免審舊筆記補審被要求修改，進預設佇列的 fix 道。"""
        note = self.write_note(written_by="")
        legacy = {self.slug: self.sha()}
        self.add_review(verdict="changes_requested", corrections=1)
        self.assertEqual(["fix"], [o.lane for o in self.orders(note, legacy)])

    def test_task_closed_early_does_not_hide_the_review_order(self):
        """待審期間被結案的任務是另外的錯誤，不能讓這篇從 codex 道變成 fix 道而審不下去。"""
        note = self.write_note()
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-22")
        note = bi.parse_note(self.note_path())
        self.assertEqual(["codex"], [o.lane for o in self.orders(note)])

    def test_work_order_has_no_author_claim(self):
        self.assertFalse(hasattr(rp.WorkOrder(slug="s", lane="codex", role="review", scopes=[], sha="x", reason=""), "author_claim"))


class PromptTest(PipelineBase):
    def test_prompt_embeds_sop_sections_verbatim(self):
        note = self.write_note()
        order = rp.orders_for(note, rl.evaluate(note, {}, dt.date(2026, 11, 23), self.root))[0]
        prompt = rp.build_prompt(note, order, self.root)
        for name in ("REVIEW-CHECKLIST", "FULL-CRITERIA"):
            self.assertIn(rp.sop_section(name, self.root), prompt)
        self.assertIn(order.sha, prompt)
        self.assertIn("source_review = `full`", prompt)  # 作者聲明從筆記讀
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
        st = rl.evaluate(bi.parse_note(self.note_path()), {}, dt.date(2026, 11, 23), self.root)
        self.assertTrue(st.reviewed, (st.needs, st.errors))

    def test_ingested_changes_requested_report_also_passes_ledger_consistency(self):
        """ingest 寫出的 header 與結果區塊，驗證器要認得（含 changes_requested 與子集範圍）。"""
        self.write_note()
        self.ingest(report(verdict="changes_requested", findings=[FINDING], scope=["facts", "evidence"]),
                    scope=["facts", "evidence", "task_impact"])
        st = rl.evaluate(bi.parse_note(self.note_path()), {}, dt.date(2026, 11, 23), self.root)
        self.assertEqual([], st.errors)

    def test_stale_note_rejected(self):
        self.write_note()
        sha = self.sha()
        path = self.note_path()
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "審查期間被改"), encoding="utf-8")
        with self.assertRaises(rp.PipelineError) as ctx:
            self.ingest(report(), sha=sha)
        self.assertIn("被改過", str(ctx.exception))

    def test_self_review_rejected(self):
        self.write_note()
        with self.assertRaises(rp.PipelineError):
            self.ingest(report(), reviewer=AUTHOR)

    def test_abbreviated_or_prefix_identity_rejected(self):
        self.write_note()
        with self.assertRaises(rp.PipelineError) as ctx:
            self.ingest(report(), reviewer=f"claude/opus-5.5@{sess(40)[:8]}")
        self.assertIn("reviewer 格式不合法", str(ctx.exception))
        self.write_note(written_by=f"antigravity/gemini-3@{sess(41)[:20]}")
        with self.assertRaises(rp.PipelineError) as ctx:
            self.ingest(report(), reviewer=f"claude/opus-5.5@{sess(41)}")
        self.assertIn("written_by", str(ctx.exception))

    def test_reviewer_runtime_must_be_claude_or_codex(self):
        """N1：ingest() 函式本身也拒絕 claude／codex 以外的 runtime（不只是 CLI）。"""
        self.write_note()
        for reviewer in ("human/maintainer@2026-11-22", "hermes/opus-5@whatever-1234", "antigravity/opus-5@whatever-1234"):
            for role in ("review", "audit"):
                with self.assertRaises(rp.PipelineError, msg=reviewer) as ctx:
                    self.ingest(report(), reviewer=reviewer, role=role)
                self.assertIn("runtime 只接受", str(ctx.exception))
        self.assertFalse((self.root / "reviews" / f"{self.slug}.json").exists())

    def test_entry_records_hash_version(self):
        self.write_note()
        self.assertEqual(rl.HASH_VERSION, self.ingest(report())["hash_version"])

    def test_weak_audit_rejected(self):
        self.write_note()
        with self.assertRaises(rp.PipelineError):
            self.ingest(report(), reviewer=WEAK, role="audit")

    def test_audit_missing_scope_rejected(self):
        """F6：audit 少範圍（例如讀不到來源就拿掉 source）要被擋，訊息說明改派。"""
        self.write_note()
        with self.assertRaises(rp.PipelineError) as ctx:
            self.ingest(report(scope=["facts", "evidence", "task_impact"]), reviewer=AUDITOR, role="audit")
        self.assertIn("改派", str(ctx.exception))
        self.assertFalse((self.root / "reviews" / f"{self.slug}.json").exists())
        self.assertEqual("pass", self.ingest(report(), reviewer=AUDITOR, role="audit")["verdict"])

    def test_author_claim_comes_from_the_note(self):
        """F5：author_claim 不由呼叫端給，一律是筆記現在的 source_review。"""
        self.write_note()
        self.assertEqual("full", self.ingest(report())["author_claim"])
        path = self.note_path()
        path.write_text(path.read_text(encoding="utf-8").replace("source_review: full", "source_review: partial"), encoding="utf-8")
        entry = self.ingest(report(source_review="partial"), reviewer=OTHER_CODEX)
        self.assertEqual("partial", entry["author_claim"])
        with self.assertRaises(TypeError):
            rp.ingest(self.slug, report(), REVIEWER, "codex", "review", list(rl.SCOPES), self.sha(), "full", root=self.root)

    def test_malformed_reports_rejected(self):
        bad = [
            "# 沒有 json",
            report().replace('"verdict": "pass"', '"verdict": "maybe"'),
            report(findings=[FINDING]),  # 有 findings 卻 pass
            report(verdict="changes_requested", findings=[FINDING], corrections=3),
            report(verdict="changes_requested", findings=[{**FINDING, "evidence": ""}]),  # 更正沒附出處
            report(scope=["facts", "vibes"]),  # 範圍不在派工內
            report(scope=[]),
            report(verdict="changes_requested", scope=["facts"], findings=[{**FINDING, "kind": "source"}]),  # 沒審 source 卻怪筆記
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
        st = rl.evaluate(bi.parse_note(self.note_path()), {}, dt.date(2026, 11, 23), self.root)
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
        text = "```json\n{\"verdict\": \"pass\"}\n```\n" + report(verdict="changes_requested", findings=[FINDING])
        self.assertEqual("changes_requested", self.ingest(text)["verdict"])

    def test_parser_is_shared_with_the_verifier(self):
        text = report(verdict="changes_requested", findings=[FINDING])
        self.assertEqual(rl.last_json_block(text)["verdict"], rp.parse_result(text, list(rl.SCOPES))["verdict"])
        self.assertIs(rp.JSON_BLOCK, rl.JSON_BLOCK)

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


class CliIdentityTest(PipelineBase):
    """F2/F3：ingest（CLI）不接受 codex 身分；claude 的 session 必須等於 CLAUDE_CODE_SESSION_ID。"""

    def run_cli(self, reviewer, env=None, extra=()):
        rpt = self.root / "report.md"
        rpt.write_text(report(), encoding="utf-8")
        argv = ["ingest", self.slug, "--report", str(rpt), "--reviewer", reviewer, "--lane", "chrome", "--role", "review",
                "--scope", ",".join(rl.SCOPES), "--sha", self.sha(), *extra]
        environ = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_SESSION_ID"}
        environ.update(env or {})
        err = io.StringIO()
        with unittest.mock.patch.object(bi, "REPO_ROOT", self.root), unittest.mock.patch.object(rp, "bi_main"), \
                unittest.mock.patch.dict(os.environ, environ, clear=True), \
                contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = rp.main(argv)
        return code, err.getvalue()

    def ledger_exists(self):
        return (self.root / "reviews" / f"{self.slug}.json").exists()

    def test_non_claude_identities_are_rejected(self):
        """N1：human、hermes、antigravity、legacy 一律拒絕（只剩 claude 且 session 等於環境變數）。"""
        self.write_note()
        for reviewer in ("human/maintainer@2026-11-22", "hermes/opus-5@whatever-1234", "antigravity/opus-5@whatever-1234",
                         rl.LEGACY_AUTHOR):
            code, err = self.run_cli(reviewer, env={"CLAUDE_CODE_SESSION_ID": sess(3)})
            self.assertEqual(2, code, reviewer)
            self.assertIn("只接受 claude", err)
            self.assertFalse(self.ledger_exists())

    def test_codex_identity_is_rejected(self):
        self.write_note()
        code, err = self.run_cli(REVIEWER, env={"CLAUDE_CODE_SESSION_ID": sess(2)})
        self.assertEqual(2, code)
        self.assertIn("codex", err)
        self.assertFalse(self.ledger_exists())

    def test_claude_without_session_env_is_rejected(self):
        self.write_note()
        code, err = self.run_cli(AUDITOR)
        self.assertEqual(2, code)
        self.assertIn("CLAUDE_CODE_SESSION_ID", err)
        self.assertFalse(self.ledger_exists())

    def test_claude_with_someone_elses_session_is_rejected(self):
        self.write_note()
        code, err = self.run_cli(AUDITOR, env={"CLAUDE_CODE_SESSION_ID": sess(99)})
        self.assertEqual(2, code)
        self.assertIn("必須等於", err)
        self.assertFalse(self.ledger_exists())

    def test_claude_with_matching_session_is_accepted(self):
        self.write_note()
        code, err = self.run_cli(AUDITOR, env={"CLAUDE_CODE_SESSION_ID": sess(3).upper()})
        self.assertEqual(0, code, err)
        self.assertTrue(self.ledger_exists())

    def test_author_claim_flag_is_gone(self):
        self.write_note()
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
            self.run_cli(AUDITOR, env={"CLAUDE_CODE_SESSION_ID": sess(3)}, extra=("--author-claim", "full"))

    def test_commit_outside_dedicated_worktree_is_rejected_before_any_write(self):
        self.write_note()
        with tempfile.TemporaryDirectory() as state, unittest.mock.patch.object(rp, "STATE_DIR", Path(state)):
            code, err = self.run_cli(AUDITOR, env={"CLAUDE_CODE_SESSION_ID": sess(3)}, extra=("--commit",))
        self.assertEqual(2, code)
        self.assertIn("專用工作樹", err)
        self.assertFalse(self.ledger_exists())


class GitFlowBase(unittest.TestCase):
    """專用工作樹＋bare remote 的暫存 repo；不碰真實 repo，也不呼叫真的 verify／build_index（用 mock 控制）。"""

    SLUG = "2026-11-22-test-note"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.t = Path(self._tmp.name)
        self.state = self.t / "state"
        self.state.mkdir()
        self.wt = self.state / "repo"
        patches = [
            unittest.mock.patch.object(rp, "STATE_DIR", self.state),
            unittest.mock.patch.dict(os.environ, {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
                                                  "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}),
            unittest.mock.patch.object(rp.time, "sleep"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self._tmp.cleanup)
        self.origin = self.t / "origin.git"
        run_git(self.t, "init", "-q", "--bare", "--initial-branch=main", str(self.origin))
        self.src = self.t / "src"
        run_git(self.t, "init", "-q", "--initial-branch=main", str(self.src))
        run_git(self.src, "remote", "add", "origin", str(self.origin))
        (self.src / "notes").mkdir()
        (self.src / "reviews" / "reports" / "old").mkdir(parents=True)
        (self.src / "README.md").write_text("readme\n", encoding="utf-8", newline="\n")
        (self.src / "reviews" / "old.json").write_text('{"note": "old", "reviews": []}\n', encoding="utf-8", newline="\n")
        (self.src / "reviews" / "reports" / "old" / "a.md").write_text("old report\n", encoding="utf-8", newline="\n")
        (self.src / "notes" / f"{self.SLUG}.md").write_text(
            NOTE.format(slug=self.SLUG, written_by=AUTHOR, extra_meta="", claim="X"), encoding="utf-8", newline="\n")
        run_git(self.src, "add", "-A")
        run_git(self.src, "commit", "-q", "-m", "seed")
        run_git(self.src, "push", "-q", "origin", "main")
        run_git(self.src, "worktree", "add", "-q", "--detach", str(self.wt), "origin/main")
        self.seed = run_git(self.wt, "rev-parse", "HEAD").strip()

    def origin_log(self) -> list[str]:
        return run_git(self.origin, "log", "--format=%H", "main").split()

    def do_ingest(self, reviewer=REVIEWER, snap=None):
        snap = snap or rp.Snapshot(self.wt)
        snap.track("README.md")
        entry = rp.ingest(self.SLUG, report(), reviewer, "codex", "review", list(rl.SCOPES),
                          rl.content_hash((self.wt / "notes" / f"{self.SLUG}.md").read_text(encoding="utf-8")),
                          root=self.wt, today=INGEST_DAY, snapshot=snap)
        return entry, rp.entry_files(self.SLUG, entry), snap

    def rebuild_readme(self, root):
        with (root / "README.md").open("a", encoding="utf-8", newline="\n") as fh:
            fh.write("rebuilt\n")

    def commit(self, files, snap, base=frozenset(), after=frozenset(), msg="chore(review): test"):
        with unittest.mock.patch.object(rp, "bi_main", side_effect=self.rebuild_readme), \
                unittest.mock.patch.object(rp, "verify_errors", return_value=set(after)):
            return rp.commit_and_push(self.wt, msg, files, set(base), snap)

    def status(self) -> str:
        return run_git(self.wt, "status", "--porcelain").strip()


class CommitFlowTest(GitFlowBase):
    def test_pushes_exactly_one_commit_with_only_the_ingested_files(self):
        entry, files, snap = self.do_ingest()
        (self.wt / "reviews" / "stray.json").write_text("{}", encoding="utf-8")  # 不屬於這次入帳的檔案
        (self.wt / "reviews" / "old.json").write_text('{"note": "old", "reviews": [1]}\n', encoding="utf-8")
        self.commit(files, snap)
        log = self.origin_log()
        self.assertEqual(2, len(log))
        self.assertEqual(self.seed, log[1])
        changed = set(run_git(self.origin, "show", "--name-only", "--format=", "main").split())
        self.assertEqual({f"reviews/{self.SLUG}.json", entry["report"], "README.md"}, changed)
        status = self.status()
        self.assertIn("?? reviews/stray.json", status)  # 別人的檔案原封不動
        self.assertIn("M reviews/old.json", status)

    def test_new_verify_errors_restore_files_and_commit_nothing(self):
        _, files, snap = self.do_ingest()
        self.commit(files, snap)  # 第一筆正常提交
        before = run_git(self.wt, "rev-parse", "HEAD").strip()
        ledger_before = (self.wt / "reviews" / f"{self.SLUG}.json").read_bytes()
        readme_before = (self.wt / "README.md").read_bytes()
        entry2, files2, snap2 = self.do_ingest(reviewer=OTHER_CODEX)
        with self.assertRaises(rp.PipelineError) as ctx:
            self.commit(files2, snap2, after={"新出現的錯誤"})
        self.assertIn("新的驗證錯誤", str(ctx.exception))
        self.assertFalse((self.wt / entry2["report"]).exists())  # 新報告刪掉
        self.assertEqual(ledger_before, (self.wt / "reviews" / f"{self.SLUG}.json").read_bytes())  # 紀錄還原
        self.assertEqual(readme_before, (self.wt / "README.md").read_bytes())  # README 還原
        self.assertEqual(before, run_git(self.wt, "rev-parse", "HEAD").strip())
        self.assertEqual(2, len(self.origin_log()))
        self.assertEqual("", self.status())

    def test_first_ingest_failure_removes_new_folders(self):
        _, files, snap = self.do_ingest()
        with self.assertRaises(rp.PipelineError):
            self.commit(files, snap, after={"x"})
        self.assertFalse((self.wt / "reviews" / f"{self.SLUG}.json").exists())
        self.assertFalse((self.wt / "reviews" / "reports" / self.SLUG).exists())
        self.assertEqual("", self.status())

    def test_errors_that_already_existed_do_not_block(self):
        _, files, snap = self.do_ingest()
        self.commit(files, snap, base={"舊錯誤"}, after={"舊錯誤"})
        self.assertEqual(2, len(self.origin_log()))

    def test_push_race_rebases_and_still_pushes_a_single_commit(self):
        other = self.t / "other"
        run_git(self.t, "clone", "-q", str(self.origin), str(other))
        (other / "other.txt").write_text("x\n", encoding="utf-8")
        run_git(other, "add", "-A")
        run_git(other, "commit", "-q", "-m", "someone else")
        run_git(other, "push", "-q", "origin", "main")
        _, files, snap = self.do_ingest()
        self.commit(files, snap)
        log = self.origin_log()
        self.assertEqual(3, len(log))  # seed、別人的、我們的（一個）
        self.assertEqual(1, int(run_git(self.origin, "rev-list", "--count", f"{log[1]}..{log[0]}").strip()))
        self.assertEqual("", self.status())

    def test_push_failure_resets_to_before_ingest(self):
        run_git(self.wt, "remote", "set-url", "origin", str(self.t / "does-not-exist.git"))
        _, files, snap = self.do_ingest()
        with self.assertRaises(rp.PipelineError) as ctx:
            self.commit(files, snap)
        self.assertIn("已還原", str(ctx.exception))
        self.assertEqual(self.seed, run_git(self.wt, "rev-parse", "HEAD").strip())
        self.assertEqual("", self.status())
        self.assertFalse((self.wt / "reviews" / f"{self.SLUG}.json").exists())


class DedicatedWorktreeTest(GitFlowBase):
    def test_accepts_clean_detached_dedicated_worktree(self):
        rp.require_dedicated_worktree(self.wt)

    def test_rejects_any_other_directory(self):
        with self.assertRaises(rp.PipelineError) as ctx:
            rp.require_dedicated_worktree(self.src)
        self.assertIn("cron", str(ctx.exception))

    def test_rejects_when_head_is_on_a_branch(self):
        run_git(self.wt, "checkout", "-q", "-b", "somebody-elses-branch")
        with self.assertRaises(rp.PipelineError) as ctx:
            rp.require_dedicated_worktree(self.wt)
        self.assertIn("detached", str(ctx.exception))

    def test_rejects_modified_tracked_file_but_commit_stage_tolerates_it(self):
        (self.wt / "README.md").write_text("改過\n", encoding="utf-8")
        with self.assertRaises(rp.PipelineError) as ctx:
            rp.require_dedicated_worktree(self.wt)
        self.assertIn("未提交改動", str(ctx.exception))
        rp.require_dedicated_worktree(self.wt, clean=False)

    def test_untracked_files_do_not_block_commit(self):
        """N6：照文件把報告放進工作樹時（未追蹤檔），--commit 仍可進行；已追蹤檔有改動才擋。"""
        (self.wt / "draft-report.md").write_text("草稿\n", encoding="utf-8")
        rp.require_dedicated_worktree(self.wt)
        _, files, snap = self.do_ingest()
        self.commit(files, snap)
        self.assertEqual(2, len(self.origin_log()))
        self.assertTrue((self.wt / "draft-report.md").exists())  # 草稿原封不動、沒被提交
        self.assertNotIn("draft-report.md", run_git(self.origin, "show", "--name-only", "--format=", "main"))

    def test_drafts_dir_is_outside_every_dedicated_worktree(self):
        d = rp.drafts_dir()
        self.assertEqual(self.state / "drafts", d)
        for lane in rp.LANES_WITH_WORKTREE:
            self.assertNotIn(rp.dedicated_worktree(lane).resolve(), d.resolve().parents)

    def test_run_checks_before_doing_anything(self):
        args = unittest.mock.Mock(lane="codex", commit=True, dry_run=False)
        with unittest.mock.patch.object(bi, "REPO_ROOT", self.src), \
                unittest.mock.patch.object(rp, "queue") as queue:
            with self.assertRaises(rp.PipelineError):
                rp.cmd_run(args)
        queue.assert_not_called()

    def test_cron_reset_cleans_leftovers_of_the_dedicated_worktree(self):
        self.assertFalse(rp.reset_dedicated_worktree(self.src, self.wt))
        (self.wt / "README.md").write_text("殘留\n", encoding="utf-8")
        (self.wt / "reviews" / "leftover.json").write_text("{}", encoding="utf-8")
        self.assertTrue(rp.reset_dedicated_worktree(self.src, self.wt))
        self.assertEqual("", self.status())
        self.assertEqual("readme", (self.wt / "README.md").read_text(encoding="utf-8").strip())
        self.assertFalse((self.wt / "reviews" / "leftover.json").exists())

    def test_cron_reset_refuses_other_directories(self):
        (self.src / "scratch.txt").write_text("人的工作目錄", encoding="utf-8")
        with self.assertRaises(rp.PipelineError) as ctx:
            rp.reset_dedicated_worktree(self.src, self.src)
        self.assertIn("不是專用工作樹", str(ctx.exception))
        self.assertTrue((self.src / "scratch.txt").exists())

    def test_cron_reset_refuses_a_path_that_is_not_a_registered_worktree(self):
        other_state = self.t / "state2"
        fake = other_state / "repo"
        fake.mkdir(parents=True)
        run_git(fake, "init", "-q")
        (fake / "mine.txt").write_text("x", encoding="utf-8")
        with unittest.mock.patch.object(rp, "STATE_DIR", other_state):
            with self.assertRaises(rp.PipelineError) as ctx:
                rp.reset_dedicated_worktree(self.src, fake)
        self.assertIn("worktree list", str(ctx.exception))
        self.assertTrue((fake / "mine.txt").exists())


class VerifyErrorsParsingTest(unittest.TestCase):
    def test_collects_error_lines_and_flags_broken_tool(self):
        out = "[*] x\n\n[FAIL] 驗證失敗，發現以下問題：\n  - a: 錯誤一\n  - b: 錯誤二\n"
        with unittest.mock.patch.object(rp.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, out, "")):
            self.assertEqual({"a: 錯誤一", "b: 錯誤二"}, rp.verify_errors(Path(".")))
        with unittest.mock.patch.object(rp.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "[PASS]\n", "")):
            self.assertEqual(set(), rp.verify_errors(Path(".")))
        with unittest.mock.patch.object(rp.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "Traceback")):
            with self.assertRaises(rp.PipelineError):
                rp.verify_errors(Path("."))


if __name__ == "__main__":
    unittest.main()
