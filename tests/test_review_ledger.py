"""tools/review_ledger.py：獨立審查紀錄的每條失敗條件都要有反例（docs/review-pipeline-plan.md 2.2、2.5 節）。"""

import datetime as dt
import hashlib
import json
import os
import subprocess
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


def sess(n: int) -> str:
    """測試用的完整 UUID session（claude／codex 的 session 格式要求）。"""
    return f"{n:08x}-0000-4000-8000-{n:012x}"


AUTHOR = f"claude/opus-5.5@{sess(1)}"
REVIEWER = f"codex/gpt-6.1-sol@{sess(2)}"
AUDITOR = f"claude/opus-5.5@{sess(3)}"
WEAK = f"claude/sonnet-5.5@{sess(4)}"
OTHER_CODEX = f"codex/gpt-6.1-sol@{sess(5)}"
OTHER_WEAK = f"claude/sonnet-5.5@{sess(6)}"
CHROME_REVIEWER = f"claude/opus-5.5@{sess(7)}"

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

FINDING = {"kind": "fact", "claim": "x", "problem": "y", "evidence": "https://example.com", "fix": "z"}


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

    def note_path(self) -> Path:
        return self.root / "notes" / f"{self.slug}.md"

    def write_note(self, written_by=AUTHOR, extra_meta="", claim=None, want_sampled=False):
        """寫筆記；預設用不會被抽查（slug 雜湊 mod 5 != 0）的 slug，want_sampled=True 則換成會被抽中的 slug。"""
        if rl.sampled(self.slug) != want_sampled:
            base = self.slug
            self.slug = next(f"{base}-{i}" for i in range(1, 200) if rl.sampled(f"{base}-{i}") == want_sampled)
        text = NOTE.format(slug=self.slug, written_by=written_by, extra_meta=extra_meta, claim=claim or "X")
        self.note_path().write_text(text, encoding="utf-8")
        return bi.parse_note(self.note_path())

    def sha(self):
        return rl.content_hash(self.note_path().read_text(encoding="utf-8"))

    def render_report(self, entry, json_over=None, header_over=None, prose=""):
        """照 ingest 寫的格式產生與紀錄一致的報告；json_over／header_over 用來製造不一致的反例。"""
        corr = entry.get("corrections")
        data = {"verdict": entry["verdict"], "source_review": entry["source_review"], "source_images": 1, "source_replies": 3,
                "corrections": corr, "scope": entry["scope"],
                "findings": [FINDING] * (corr if type(corr) is int and corr > 0 else 0), "task_impact": []}
        data.update(json_over or {})
        head = {"reviewer": entry["reviewer"], "content_sha256": entry["content_sha256"], "role": entry["role"]}
        head.update(header_over or {})
        return (f"# 獨立審查報告：{self.slug}\n\n- reviewer: {head['reviewer']}\n- content_sha256: {head['content_sha256']}\n"
                f"- role: {head['role']}；lane: codex；scope: {', '.join(map(str, entry['scope']))}\n- reviewed_at: {entry['reviewed_at']}\n\n---\n\n"
                f"{prose}逐項結果……\n\n```json\n{json.dumps(data, ensure_ascii=False)}\n```\n")

    def add_review(self, reviewer=REVIEWER, sha=None, n=None, report_body=None, json_over=None, header_over=None, prose="", **over):
        path = self.root / "reviews" / f"{self.slug}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"note": self.slug, "reviews": []}
        n = n if n is not None else len(data["reviews"]) + 1
        sha = sha or self.sha()
        report = f"reviews/reports/{self.slug}/2026-11-23-{n}.md"
        entry = {
            "reviewed_at": "2026-11-23", "reviewer": reviewer, "role": "review",
            "scope": list(rl.SCOPES), "content_sha256": sha, "verdict": "pass",
            "source_review": "full", "author_claim": "full", "corrections": 0, "report": report,
        }
        entry.update(over)
        rp = self.root / report
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(report_body if report_body is not None else self.render_report(entry, json_over, header_over, prose),
                      encoding="utf-8", newline="\n")
        data["reviews"].append(entry)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return entry

    def state(self, note=None, legacy=None, today=TODAY):
        note = note or bi.parse_note(self.note_path())
        return rl.evaluate(note, legacy or {}, today, self.root)


class HashTest(Base):
    def test_task_state_changes_do_not_change_hash(self):
        self.write_note()
        path = self.note_path()
        before = self.sha()
        tc.apply_claim(path, "T-20261122-01")
        self.assertEqual(before, self.sha())
        tc.apply_complete(path, "T-20261122-01", "commit abc\n多行", "2026-11-24")
        self.assertEqual(before, self.sha())
        self.assertIn("status: done", path.read_text(encoding="utf-8"))

    def test_close_and_crlf_do_not_change_hash(self):
        self.write_note()
        path = self.note_path()
        before = self.sha()
        tc.apply_close(path, "T-20261122-01", "不做")
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual(before, self.sha())

    def test_any_analysis_edit_changes_hash(self):
        self.write_note()
        path = self.note_path()
        before = self.sha()
        for old, new in (("本文主張", "本文改口主張"), ("source_review: full", "source_review: partial"),
                         ("做完", "做一半"), ("[優先級：中]", "[優先級：高]")):
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            self.assertNotEqual(before, self.sha(), old)
            path.write_text(text, encoding="utf-8")

    def test_new_task_changes_hash(self):
        self.write_note()
        path = self.note_path()
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n- [ ] **`T-20261122-02`**｜**[優先級：高]** 建立在錯誤前提上的新任務\n  - **目標範圍**：x\n")
        self.assertNotEqual(before, self.sha())

    def test_sampling_is_by_slug_not_by_content(self):
        """抽查看 slug：改內容躲不掉（舊制看內容雜湊，改一個字就能換到不被抽中的雜湊）。"""
        self.write_note(want_sampled=True)
        self.assertTrue(rl.sampled(self.slug))
        self.add_review()
        path = self.note_path()
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "改個字再主張"), encoding="utf-8")
        self.add_review(reviewer=OTHER_CODEX)
        st = self.state()
        self.assertTrue(any("抽查" in n for n in st.needs), st.needs)


class HashHidingTest(Base):
    """雜湊略過的欄位不能拿來藏分析內容。"""

    def changed_by(self, addition, anchor="本文主張"):
        self.write_note()
        path = self.note_path()
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
        path = self.note_path()
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n後記：新增一段分析。\n")
        self.assertNotEqual(before, self.sha())

    def test_indented_text_after_state_field_ends_with_task_block(self):
        self.write_note()
        path = self.note_path()
        tc.apply_complete(path, "T-20261122-01", "commit abc", "2026-11-24")
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n## 新段落\n\n    縮排的新主張（不屬於任務欄位）\n")
        self.assertNotEqual(before, self.sha())

    def test_continuation_lines_of_state_fields_are_hashed(self):
        """F10(a)：只略過欄位那一行，更深縮排的續行算進雜湊（舊制整段續行都被略過，可以藏內容）。"""
        self.write_note()
        path = self.note_path()
        tc.apply_complete(path, "T-20261122-01", "commit abc", "2026-11-24")
        before = self.sha()
        text = path.read_text(encoding="utf-8")
        marker = "  - **實作紀錄 / 證據**：commit abc\n"
        self.assertIn(marker, text)
        path.write_text(text.replace(marker, marker + "    - 偷藏在證據續行裡的結論\n"), encoding="utf-8")
        self.assertNotEqual(before, self.sha())

    def test_top_level_fence_ends_task_block(self):
        """F10(c)：頂層圍欄結束任務欄位區（與 bi.parse_note 一致），圍欄後的「狀態」行不再被略過。"""
        self.write_note()
        path = self.note_path()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n```text\nx\n```\n")
        before = self.sha()
        with path.open("a", encoding="utf-8") as fh:
            fh.write("  - **狀態**：圍欄後偷加的結論\n")
        self.assertNotEqual(before, self.sha())

    def test_status_comment_is_hashed_but_value_is_not(self):
        """F10(d)：frontmatter status 只略過值；行尾註解算進雜湊。"""
        self.write_note()
        path = self.note_path()
        before = self.sha()
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("status: pending\n", "status: done\n", 1), encoding="utf-8")
        self.assertEqual(before, self.sha())
        path.write_text(text.replace("status: pending\n", "status: pending # 偷藏的註解\n", 1), encoding="utf-8")
        self.assertNotEqual(before, self.sha())

    def test_nonstandard_status_body_line_is_hashed(self):
        """F10(e)：正文「當前狀態」行只有標準標記才略過，其餘文字算進雜湊。"""
        self.write_note()
        path = self.note_path()
        before = self.sha()
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("`🔴 未做 (Pending)`", "`🟢 已完成 (Done)`", 1), encoding="utf-8")
        self.assertEqual(before, self.sha())
        path.write_text(text.replace("`🔴 未做 (Pending)`", "`🔴 未做 (Pending)`（偷加的說明）", 1), encoding="utf-8")
        self.assertNotEqual(before, self.sha())
        path.write_text(text.replace("`🔴 未做 (Pending)`", "`⚪ 封存 (Archived)`", 1), encoding="utf-8")
        self.assertNotEqual(before, self.sha())

    def test_task_cli_skips_fenced_status_line_and_nonstandard_value(self):
        """F11：task_cli 找「當前狀態」行要跳過程式碼圍欄；非標準值不改寫（那是筆記內容）。"""
        fenced = "```text\n- **當前狀態**：`🔴 未做 (Pending)`\n```\n"
        text = NOTE.format(slug="s", written_by=AUTHOR, extra_meta="", claim="X").replace("# 測試筆記\n", "# 測試筆記\n\n" + fenced, 1)
        out = tc._update_note_frontmatter_status(text, "done")
        self.assertIn(fenced, out)
        self.assertIn("- **當前狀態**：`🟢 已完成 (Done)`\n\n本文主張", out)
        odd = text.replace("`🔴 未做 (Pending)`\n\n本文", "`⚪ 封存 (Archived)`\n\n本文", 1).replace(fenced, "")
        self.assertIn("`⚪ 封存 (Archived)`", tc._update_note_frontmatter_status(odd, "done"))


class TaskCliKeepsHashOnRealNotesTest(unittest.TestCase):
    def test_claim_complete_close_never_change_hash_of_any_repo_note(self):
        """對 repo 現有全部筆記模擬 claim／complete／close：分析內容雜湊都不變（task_cli 不會讓舊筆記變回待審）。"""
        notes = bi.load_notes()
        self.assertGreater(len(notes), 100)
        checked = 0
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "n.md"
            for note in notes:
                raw = note.path.read_bytes()
                before = rl.content_hash(raw.decode("utf-8"))
                for task in note.tasks:
                    if task.done:
                        continue
                    for ops in (("claim",), ("complete",), ("close",), ("claim", "complete")):
                        work.write_bytes(raw)
                        for op in ops:
                            if op == "claim":
                                tc.apply_claim(work, task.id)
                            elif op == "complete":
                                tc.apply_complete(work, task.id, "commit abc", "2026-11-24")
                            else:
                                tc.apply_close(work, task.id, "不做")
                        self.assertEqual(before, rl.content_hash(work.read_text(encoding="utf-8")), (note.slug, task.id, ops))
                        checked += 1
        self.assertGreater(checked, 50)


class IdentityTest(unittest.TestCase):
    def test_runtime_specific_session_formats(self):
        uuid = "01a1fcb9-6070-7fc1-9407-2a5b4823514b"
        ok = [f"claude/opus-5.5@{uuid}", f"codex/gpt-6.1-sol@{uuid.upper()}", "antigravity/gemini-3@abcdefgh",
              "hermes/xiaoma@hermes-session-1", "human/maintainer@2026-11-21", rl.LEGACY_AUTHOR]
        for text in ok:
            self.assertIsNotNone(rl.parse_identity(text), text)
        bad = [f"claude/opus-5.5@{uuid[:8]}",  # 縮寫
               f"codex/gpt-6.1-sol@{uuid}0", f"claude/opus-5.5@{uuid[:-1]}", "claude/opus-5.5@author-session-1",
               "antigravity/gemini-3@abcdefg", "hermes/xiaoma@short",
               "human/maintainer@today", "human/maintainer@2026-13-45", "human/someone@2026-11-21", "human/maintainer@798b1dc7",
               "legacy/unknown@other-session", "legacy/other@pre-review", "robot/x@session-1", "claude/opus-5.5"]
        for text in bad:
            self.assertIsNone(rl.parse_identity(text), text)

    def test_strong_model_is_strict(self):
        uuid = sess(9)
        strong = [f"claude/opus-5.5@{uuid}", f"claude/opus-5@{uuid}", f"codex/gpt-6.1-sol@{uuid}", f"codex/gpt-6-astra@{uuid}",
                  f"codex/GPT-6.2-Sol@{uuid}", "human/maintainer@2026-11-21"]
        weak = [f"claude/opus-anything@{uuid}", f"claude/opus@{uuid}", f"claude/opus-5.5-fast@{uuid}", f"codex/gpt-5.5-sol@{uuid}",
                f"codex/gpt-6.1-solx@{uuid}", f"claude/sonnet-5.5@{uuid}", f"claude/maintainer@{uuid}",
                "hermes/maintainer@abcdefgh", "antigravity/maintainer@abcdefgh"]
        for text in strong:
            self.assertTrue(rl.parse_identity(text).strong, text)
        for text in weak:
            ident = rl.parse_identity(text)
            self.assertIsNotNone(ident, text)
            self.assertFalse(ident.strong, text)

    def test_same_session_is_case_insensitive_prefix_match(self):
        self.assertTrue(rl.same_session("ABCDEF12-0000", "abcdef12-0000"))
        self.assertTrue(rl.same_session("abcdef12", "abcdef12-0000-4000"))
        self.assertTrue(rl.same_session("abcdef12-0000-4000", "ABCDEF12"))
        self.assertFalse(rl.same_session("abcdef12", "abcdef13"))
        self.assertFalse(rl.same_session("", "abcdef12"))


class IdentityEnforcementTest(Base):
    def test_abbreviated_session_in_written_by_is_invalid(self):
        st = self.state(self.write_note(written_by="claude/opus-5.5@798b1dc7"))
        self.assertTrue(any("written_by" in e and "完整 UUID" in e for e in st.errors), st.errors)

    def test_abbreviated_reviewer_session_is_invalid(self):
        self.write_note()
        self.add_review(reviewer="claude/opus-5.5@" + sess(1)[:8])
        self.assertTrue(any("reviewer 需為" in e for e in self.state().errors))

    def test_prefix_of_author_session_cannot_review(self):
        self.write_note(written_by="antigravity/gemini-3@abcdefgh12345")
        self.add_review(reviewer="hermes/xiaoma@abcdefgh")
        self.assertTrue(any("不能審自己寫的內容" in e for e in self.state().errors))

    def test_prefix_of_reviewer_session_cannot_audit(self):
        self.write_note()
        self.add_review(reviewer="hermes/xiaoma@abcdefgh12345", verdict="changes_requested", corrections=2)
        self.add_review(reviewer="antigravity/gemini-3@abcdefgh", role="audit")  # 不是強模型也會報，但覆核要換人這條一定要在
        self.assertTrue(any("覆核要換人" in e for e in self.state().errors))

    def test_maintainer_name_under_other_runtime_is_not_strong_audit(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer="hermes/maintainer@abcdefgh", role="audit")
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("強模型執行" in e for e in st.errors), st.errors)

    def test_human_maintainer_can_audit(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer="human/maintainer@2026-11-24", role="audit")
        self.assertTrue(self.state().reviewed, self.state().needs)


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
        self.assertFalse(st.pending)

    def test_edited_legacy_note_becomes_governed(self):
        note = self.write_note(written_by="")
        st = self.state(note, legacy={self.slug: "0" * 64})
        self.assertTrue(st.governed)
        self.assertTrue(any("written_by" in e and "revised_at" in e for e in st.errors), st.errors)

    def test_missing_or_malformed_written_by(self):
        for wb in ("", "Claude Code", "claude/opus@ab", "robot/x@session-1", "claude/opus-5.5@798b1dc7-…",
                   f"claude/opus-5.5@{sess(1)[:13]}"):
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
        self.assertTrue(st.overdue)

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


class PendingTaskLockTest(Base):
    """F4：筆記待審時，任務不可手動結案或認領（task_cli 的鎖之外，驗證器事後也要擋）。"""

    def test_task_completed_while_pending_is_error(self):
        self.write_note()
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-22")
        st = self.state()
        self.assertTrue(any("在審查通過前結案" in e for e in st.errors), st.errors)
        self.assertEqual(st.task_errors, [e for e in st.errors if "在審查通過前結案" in e])

    def test_task_claimed_while_pending_on_new_note_is_error(self):
        self.write_note()
        tc.apply_claim(self.note_path(), "T-20261122-01")
        self.assertTrue(any("在審查通過前被認領" in e for e in self.state().errors))

    def test_completed_task_is_fine_once_reviewed(self):
        self.write_note()
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-24")
        self.assertTrue(self.state().task_errors)
        self.add_review()
        st = self.state()
        self.assertTrue(st.reviewed, (st.needs, st.errors))
        self.assertEqual([], st.errors)

    def test_task_errors_do_not_block_the_review_itself(self):
        """task 錯誤不能讓審查永遠過不了：審查 pass 之後錯誤自然消失。"""
        self.write_note()
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-23")
        self.add_review()
        self.assertTrue(self.state().reviewed)

    def test_legacy_edit_only_flags_tasks_finished_since_revision(self):
        legacy = {self.slug: "0" * 64}
        wb = f"{rl.LEGACY_AUTHOR}; {AUTHOR}"
        self.write_note(written_by=wb, extra_meta="revised_at: 2026-11-24\n")
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-23")  # 改內容之前就完成
        self.assertEqual([], self.state(legacy=legacy).task_errors)
        self.write_note(written_by=wb, extra_meta="revised_at: 2026-11-24\n")
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-24")  # 改內容之後才完成
        self.assertTrue(any("在審查通過前結案" in e for e in self.state(legacy=legacy).errors))

    def test_legacy_edit_allows_in_progress_but_new_note_does_not(self):
        legacy = {self.slug: "0" * 64}
        self.write_note(written_by=f"{rl.LEGACY_AUTHOR}; {AUTHOR}", extra_meta="revised_at: 2026-11-24\n")
        tc.apply_claim(self.note_path(), "T-20261122-01")
        self.assertEqual([], self.state(legacy=legacy).task_errors)


class FlaggedLegacyTest(Base):
    """F7：免審舊筆記的補審被要求修改，現行內容視為待審。"""

    def flagged(self, today=TODAY):
        note = self.write_note(written_by="")
        legacy = {self.slug: self.sha()}
        self.add_review(verdict="changes_requested", corrections=1)
        return rl.evaluate(note, legacy, today, self.root), legacy, note

    def test_unresolved_changes_requested_makes_exempt_note_pending(self):
        st, _, _ = self.flagged()
        self.assertFalse(st.governed)
        self.assertTrue(st.flagged)
        self.assertTrue(st.pending)
        self.assertFalse(st.reviewed)
        self.assertEqual([], st.errors)  # 不要求 written_by，寬限內只警告
        self.assertTrue(st.warnings)
        self.assertTrue(any(n.startswith("修正後再審") for n in st.needs), st.needs)

    def test_grace_counts_from_the_review_date(self):
        st, _, _ = self.flagged(today=dt.date(2026, 11, 30))  # 審查 11-23，第 7 天
        self.assertEqual([], st.errors)
        st, _, _ = self.flagged(today=dt.date(2026, 12, 1))  # 第 8 天
        self.assertTrue(st.overdue)
        self.assertTrue(any("超過寬限" in e for e in st.errors), st.errors)

    def test_audit_pass_clears_the_flag(self):
        _, legacy, note = self.flagged()
        self.add_review(reviewer=AUDITOR, role="audit")
        st = rl.evaluate(note, legacy, TODAY, self.root)
        self.assertFalse(st.pending)
        self.assertEqual([], st.errors)

    def test_exempt_note_with_only_a_pass_is_not_pending(self):
        note = self.write_note(written_by="")
        legacy = {self.slug: self.sha()}
        self.add_review()
        self.assertFalse(rl.evaluate(note, legacy, TODAY, self.root).pending)

    def test_changes_requested_on_old_hash_does_not_flag(self):
        note = self.write_note(written_by="")
        legacy = {self.slug: self.sha()}
        self.add_review(sha="a" * 64, verdict="changes_requested", corrections=1)
        self.assertFalse(rl.evaluate(note, legacy, TODAY, self.root).pending)

    def test_tasks_finished_after_the_flagged_review_are_errors(self):
        note = self.write_note(written_by="")
        legacy = {self.slug: self.sha()}
        self.add_review(verdict="changes_requested", corrections=1)
        tc.apply_complete(self.note_path(), "T-20261122-01", "commit abc", "2026-11-24")
        st = rl.evaluate(bi.parse_note(self.note_path()), legacy, TODAY, self.root)
        self.assertTrue(any("在審查通過前結案" in e for e in st.errors), st.errors)


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
        self.write_note(written_by=f"claude/opus-5.5@{sess(11)}")
        self.add_review(reviewer=f"claude/sonnet-5.5@{sess(11).upper()}")
        self.assertTrue(any("不能審自己寫的內容" in e for e in self.state().errors))

    def test_edit_after_review_needs_rereview(self):
        self.write_note()
        self.add_review()
        path = self.note_path()
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
        self.add_review(source_review="partial")
        self.assertTrue(any("筆記要照審查結論改" in e for e in self.state().errors))

    def test_author_claim_must_equal_notes_source_review(self):
        """F5：author_claim 不由審查者自填；現行雜湊上的紀錄必須等於筆記現在的 source_review。"""
        self.write_note()
        self.add_review(author_claim="partial", source_review="partial")  # 筆記寫 full，審查者自填 partial 想把下修藏掉
        st = self.state()
        self.assertTrue(any("author_claim" in e and "不能由審查者自填" in e for e in st.errors), st.errors)
        self.assertFalse(st.reviewed)

    def test_scope_must_be_covered(self):
        self.write_note()
        self.add_review(scope=["facts", "evidence", "task_impact"])
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("source" in n for n in st.needs), st.needs)
        self.add_review(reviewer=CHROME_REVIEWER, scope=["source"])
        self.assertTrue(self.state().reviewed)

    def test_review_on_other_hash_does_not_count(self):
        self.write_note()
        self.add_review(sha="a" * 64)
        self.assertFalse(self.state().reviewed)

    def test_changes_requested_blocks_until_fixed(self):
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=1)
        self.add_review(reviewer=OTHER_CODEX)
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("修正後再審" in n for n in st.needs), st.needs)

    def test_dates_must_not_go_backwards(self):
        self.write_note()
        self.add_review(reviewed_at="2026-11-24")
        self.add_review(reviewer=OTHER_CODEX, reviewed_at="2026-11-23")
        self.assertTrue(any("只能追加" in e for e in self.state().errors))

    def test_ledger_for_wrong_note_rejected(self):
        self.write_note()
        (self.root / "reviews" / f"{self.slug}.json").write_text(json.dumps({"note": "other", "reviews": []}), encoding="utf-8")
        self.assertTrue(self.state().errors)


class ReportMatchesLedgerTest(Base):
    """F1：紀錄與報告要一致；只改紀錄檔的 verdict 就想翻成 pass 的做法要被擋。"""

    def assert_rejected(self, *needles, **kw):
        st = self.state()
        self.assertFalse(st.reviewed)
        for needle in needles:
            self.assertTrue(any(needle in e for e in st.errors), (needle, st.errors))

    def test_consistent_report_passes(self):
        self.write_note()
        self.add_review()
        self.assertTrue(self.state().reviewed)

    def test_flipping_verdict_in_ledger_only_is_rejected(self):
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=1)
        path = self.root / "reviews" / f"{self.slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["reviews"][0].update(verdict="pass", corrections=0)  # 只改紀錄、不動報告
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.assert_rejected("verdict", "corrections")

    def test_corrections_must_match_report_and_findings(self):
        self.write_note()
        self.add_review(json_over={"corrections": 3, "findings": [FINDING] * 3})
        self.assert_rejected("corrections")
        self.setUp()
        self.write_note()
        self.add_review(json_over={"findings": [FINDING] * 2})  # corrections 0 但報告列了 2 筆
        self.assert_rejected("findings 筆數")

    def test_scope_must_match_report(self):
        self.write_note()
        self.add_review(json_over={"scope": ["facts"]})
        self.assert_rejected("scope")
        self.setUp()
        self.write_note()
        self.add_review(scope=["facts"], json_over={"scope": list(rl.SCOPES)})
        self.assert_rejected("scope")

    def test_scope_order_does_not_matter(self):
        self.write_note()
        self.add_review(json_over={"scope": list(reversed(rl.SCOPES))})
        self.assertTrue(self.state().reviewed)

    def test_report_without_result_block_is_rejected(self):
        self.write_note()
        e = self.add_review()
        rp = self.root / e["report"]
        rp.write_text(rp.read_text(encoding="utf-8").split("```json")[0], encoding="utf-8")
        self.assert_rejected("結果區塊")

    def test_last_json_block_is_the_one_checked(self):
        self.write_note()
        e = self.add_review()
        rp = self.root / e["report"]
        rp.write_text(rp.read_text(encoding="utf-8") + '\n```json\n{"verdict": "changes_requested", "corrections": 0, "scope": []}\n```\n',
                      encoding="utf-8")
        self.assert_rejected("verdict", "scope")

    def test_header_identity_must_match_not_just_appear_in_body(self):
        """舊制只檢查雜湊與審查者字串「出現在內文任何地方」；現在逐行比對 header。"""
        self.write_note()
        self.add_review(header_over={"reviewer": AUDITOR}, prose=f"（內文順帶提到 {REVIEWER} 與 {self.sha()}）\n\n")
        self.assert_rejected("header reviewer")
        self.setUp()
        self.write_note()
        self.add_review(header_over={"content_sha256": "b" * 64}, prose=f"{self.sha()}\n\n")
        self.assert_rejected("header content_sha256")
        self.setUp()
        self.write_note()
        self.add_review(header_over={"role": "audit"})
        self.assert_rejected("header role")

    def test_header_must_be_before_separator_and_unique(self):
        self.write_note()
        e = self.add_review()
        rp = self.root / e["report"]
        body = rp.read_text(encoding="utf-8")
        rp.write_text(body.replace("---\n", f"- reviewer: {AUDITOR}\n\n---\n", 1), encoding="utf-8")
        self.assert_rejected("不只一次")
        rp.write_text(body.replace("\n---\n", "\n"), encoding="utf-8")
        self.assert_rejected("header")


def run_git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
                       cwd=root, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise AssertionError(f"git {args} 失敗：{r.stdout}{r.stderr}")
    return r.stdout


class CommittedHistoryTest(Base):
    """F1：HEAD 上的紀錄只能追加、已提交的報告不可變更（暫存 git repo）。"""

    def setUp(self):
        super().setUp()
        run_git(self.root, "init", "-q")
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=1)
        self.add_review(reviewer=OTHER_CODEX)
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", "init")

    def errors(self):
        return rl.evaluate_all([bi.parse_note(self.note_path())], TODAY, self.root)[1]

    def ledger(self):
        return self.root / "reviews" / f"{self.slug}.json"

    def test_untouched_history_and_appended_review_are_fine(self):
        self.assertEqual([], self.errors())
        self.add_review(reviewer=AUDITOR, role="audit")
        self.assertEqual([], self.errors())

    def test_editing_committed_entry_is_rejected(self):
        data = json.loads(self.ledger().read_text(encoding="utf-8"))
        data["reviews"][0].update(verdict="pass", corrections=0)
        self.ledger().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.assertTrue(any("已提交的審查紀錄被改動" in e for e in self.errors()), self.errors())

    def test_dropping_or_reordering_committed_entries_is_rejected(self):
        data = json.loads(self.ledger().read_text(encoding="utf-8"))
        self.ledger().write_text(json.dumps({**data, "reviews": data["reviews"][1:]}), encoding="utf-8")
        self.assertTrue(self.errors())
        self.ledger().write_text(json.dumps({**data, "reviews": data["reviews"][::-1]}), encoding="utf-8")
        self.assertTrue(self.errors())

    def test_deleting_committed_ledger_is_rejected(self):
        self.ledger().unlink()
        self.assertTrue(any("被刪除" in e for e in self.errors()), self.errors())

    def test_changing_or_deleting_committed_report_is_rejected(self):
        report = self.root / json.loads(self.ledger().read_text(encoding="utf-8"))["reviews"][0]["report"]
        original = report.read_bytes()
        report.write_bytes(original + b"\nextra\n")
        self.assertTrue(any("已提交的審查報告被改動或刪除" in e for e in self.errors()), self.errors())
        report.unlink()
        self.assertTrue(any("已提交的審查報告被改動或刪除" in e for e in self.errors()), self.errors())
        report.write_bytes(original)
        self.assertEqual([], self.errors())

    def test_not_a_git_repo_or_untracked_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp)
            (other / "reviews").mkdir()
            self.assertEqual([], rl.committed_history_errors(other))
        (self.root / "reviews" / "reports" / self.slug / "new.md").write_text("x", encoding="utf-8")
        self.assertEqual([], self.errors())


class EscalationTest(Base):
    def assert_needs_audit(self):
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("強模型覆核" in n for n in st.needs), (st.needs, st.errors))

    def fix_note(self):
        path = self.note_path()
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "本文修正後主張"), encoding="utf-8")

    def test_downgrade_full_requires_audit(self):
        self.write_note()
        self.add_review(verdict="changes_requested", source_review="partial", corrections=1)
        path = self.note_path()
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

    def test_sampled_slug_requires_audit(self):
        self.write_note(want_sampled=True)
        self.add_review()
        self.assert_needs_audit()
        self.add_review(reviewer=AUDITOR, role="audit")
        self.assertTrue(self.state().reviewed)

    def test_audit_by_weak_model_rejected(self):
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer=OTHER_WEAK, role="audit")
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("強模型執行" in e for e in st.errors), st.errors)

    def test_audit_by_same_session_as_reviewer_rejected(self):
        self.write_note()
        self.add_review(reviewer=OTHER_CODEX, verdict="changes_requested", corrections=2)
        self.fix_note()
        self.add_review(reviewer=OTHER_CODEX)
        self.add_review(reviewer=OTHER_CODEX, role="audit")
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
        self.add_review(reviewer=OTHER_WEAK)
        self.assert_needs_audit()

    def test_audit_must_cover_every_scope(self):
        """F6：audit 少範圍（例如讀不到來源就拿掉 source）不算數。"""
        self.write_note()
        self.add_review(reviewer=WEAK)
        self.add_review(reviewer=AUDITOR, role="audit", scope=["facts", "evidence", "task_impact"])
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertTrue(any("audit 的 scope 必須涵蓋全部範圍" in e for e in st.errors), st.errors)


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

    def test_repo_real_ledgers_are_valid(self):
        """repo 裡真實的審查紀錄（Codex 實跑入帳的那筆）在新規則下仍然合法。"""
        notes = bi.load_notes()
        states, errors = rl.evaluate_all(notes, dt.date(2026, 11, 21))
        ledgers = [p for p in (bi.REPO_ROOT / "reviews").glob("*.json") if p.name != rl.LEGACY_BASELINE_NAME]
        for p in ledgers:
            self.assertIn(p.stem, states, p.name)
            self.assertEqual([], states[p.stem].errors, p.name)
        self.assertEqual([], errors)

    def test_orphan_ledger_detected(self):
        self.write_note()
        (self.root / "reviews" / "2026-11-22-ghost.json").write_text(json.dumps({"note": "2026-11-22-ghost", "reviews": []}), encoding="utf-8")
        _, errors = rl.evaluate_all([bi.parse_note(self.note_path())], TODAY, self.root)
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
