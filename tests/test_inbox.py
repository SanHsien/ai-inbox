"""tools/ 的單元測試：python -m unittest discover -s tests"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_index as bi  # noqa: E402
import task_cli as tc  # noqa: E402
import verify_inbox as vi  # noqa: E402

NOTE = """---
id: {slug}
title: "測試筆記"
source_url: "N/A"
analyzed_at: 2026-10-20
status: {status} # pending | in-progress | done | archived
cluster: 1
cluster_role: "訊息傳輸"
short_title: "測試短標題"
tags:
  - a
  - b
---

# 測試

- [{box}] **`T-20261020-01`**｜**[優先級：高]** 第一項任務
  - **目標範圍**：`some/repo`
  - **驗收標準（DoD）**：跑 X 通過
{extra}
- [ ] **`T-20261020-02`**｜**[優先級：低]** 第二項任務
  - **目標範圍**：`other`
  - **狀態**：🟡 進行中

## 4. 關聯
- 引用 `T-20261020-01`
"""


def make_note(tmp: Path, slug="2026-10-20-sample", status="in-progress", box="x",
              extra="  - **完成日期**：2026-10-21\n  - **實作紀錄 / 證據**：commit abc123") -> bi.Note:
    path = tmp / f"{slug}.md"
    path.write_text(NOTE.format(slug=slug, status=status, box=box, extra=extra), encoding="utf-8")
    return bi.parse_note(path)


class ParseTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_parses_frontmatter_and_tasks(self):
        n = make_note(self.tmp)
        self.assertEqual(n.meta["status"], "in-progress")  # 行內註解被去掉
        self.assertEqual(n.tags, ["a", "b"])
        self.assertEqual([t.id for t in n.tasks], ["T-20261020-01", "T-20261020-02"])
        t1, t2 = n.tasks
        self.assertTrue(t1.done)
        self.assertEqual(t1.fields["目標範圍"], "`some/repo`")
        self.assertEqual(t1.fields["實作紀錄 / 證據"], "commit abc123")
        self.assertTrue(t2.in_progress)
        self.assertEqual(t2.created, "2026-10-20")

    def test_valid_note_has_no_errors(self):
        self.assertEqual(vi.check_notes([make_note(self.tmp)]), [])

    def test_status_mismatch_detected(self):
        errs = vi.check_notes([make_note(self.tmp, status="pending")])
        self.assertTrue(any("status 應為 'in-progress'" in e for e in errs), errs)

    def test_done_without_evidence_detected(self):
        errs = vi.check_notes([make_note(self.tmp, extra="")])
        self.assertTrue(any("沒有「實作紀錄 / 證據」" in e for e in errs), errs)

    def test_placeholder_evidence_rejected(self):
        errs = vi.check_notes([make_note(self.tmp, extra="  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*")])
        self.assertTrue(any("沒有「實作紀錄 / 證據」" in e for e in errs), errs)

    def test_multiline_field_value(self):
        n = make_note(self.tmp, extra="  - **完成日期**：2026-10-21\n  - **實作紀錄 / 證據**：\n    - commit def456")
        self.assertEqual(n.tasks[0].fields["實作紀錄 / 證據"], "commit def456")
        self.assertEqual(vi.check_notes([n]), [])

    def test_id_filename_mismatch_detected(self):
        n = make_note(self.tmp)
        n.meta["id"] = "something-else"
        self.assertTrue(any("與檔名不一致" in e for e in vi.check_notes([n])))

    def test_duplicate_and_undefined_ids_detected(self):
        a = make_note(self.tmp, slug="2026-10-20-a")
        b = make_note(self.tmp, slug="2026-10-20-b")
        texts = {a.path: a.path.read_text(encoding="utf-8") + "\n見 T-20991231-99",
                 b.path: b.path.read_text(encoding="utf-8")}
        errs = vi.check_task_ids([a, b], texts)
        self.assertTrue(any("重複定義" in e for e in errs), errs)
        self.assertTrue(any("T-20991231-99" in e for e in errs), errs)

    def test_loose_task_line_detected(self):
        n = make_note(self.tmp)
        text = n.path.read_text(encoding="utf-8") + "\n- [ ] **T-20261020-03**: 簡寫格式\n"
        errs = vi.check_task_ids([n], {n.path: text})
        self.assertTrue(any("格式不符範本" in e for e in errs), errs)

    def test_secret_and_session_link_detected(self):
        p = self.tmp / "x.md"
        texts = {p: "key ghp_" + "a" * 30 + "\n[s](conversation://abc)"}
        errs = vi.check_secrets(texts)
        self.assertEqual(len(errs), 2, errs)

    def test_private_alias_checks(self):
        p = self.tmp / "x.md"
        public = {"個人記憶庫": "說明"}
        local = {"個人記憶庫": "owner/secret-repo"}
        ok = {p: "用 [Private Repo: 個人記憶庫] 通過驗證，格式說明 [Private Repo: <別名>]"}
        self.assertEqual(vi.check_private_aliases(ok, public, local, ok), [])
        bad = {p: "[Private Repo: 未登記] 與 secret-repo"}
        errs = vi.check_private_aliases(bad, public, local, bad)
        self.assertTrue(any("未登記" in e for e in errs), errs)
        self.assertTrue(any("真實名稱 'secret-repo'" in e for e in errs), errs)
        # CI 沒有本機對照表：只檢查別名登記，不做真名掃描
        self.assertEqual(len(vi.check_private_aliases(bad, public, {}, bad)), 1)

    def test_render_moves_done_task_to_done_table(self):
        out = bi.render_tasks([make_note(self.tmp)])
        pending, done = out.split("### 🟢 已做")
        self.assertIn("T-20261020-02", pending)
        self.assertIn("🟡 進行中", pending)
        self.assertNotIn("T-20261020-01", pending)
        self.assertIn("T-20261020-01", done)
        self.assertIn("commit abc123", done)

    def test_render_archived_task_as_not_doing(self):
        archived_note = """---
id: 2026-10-20-archived
title: "封存測試"
source_url: "N/A"
analyzed_at: 2026-10-20
status: archived
tags:
  - test
---

# 封存測試

- [ ] **`T-20261020-03`**｜**[優先級：低]** 已過時任務
  - **目標範圍**：`none`
  - **狀態**：⚪ 不做（已過時退役）
  - **驗收標準（DoD）**：測試
"""
        p = self.tmp / "2026-10-20-archived.md"
        p.write_text(archived_note, encoding="utf-8")
        note = bi.parse_note(p)
        self.assertTrue(note.tasks[0].archived)
        self.assertEqual(note.tasks[0].archive_reason, "已過時退役")
        out = bi.render_tasks([note])
        active_part, rest = out.split("### 🟢 已做")
        self.assertNotIn("T-20261020-03", active_part)  # 不污染待辦佇列
        self.assertIn("⚪ 不做 1", out)
        self.assertIn("### ⚪ 不做 / 已關閉（Archived）", rest)
        self.assertIn("| `T-20261020-03` | ⚪ 不做 | 低 | 已過時任務 | 已過時退役 |", rest)

    def test_expected_note_status_handles_done_plus_archived(self):
        n = make_note(self.tmp)
        n.tasks[1].fields["狀態"] = "⚪ 不做（已取代）"
        self.assertEqual(bi.expected_note_status(n), "done")
        n.tasks[0].done = False
        n.tasks[0].fields["狀態"] = "⚪ 不做（全部關閉）"
        self.assertEqual(bi.expected_note_status(n), "archived")

    def test_task_cli_claim_complete_and_close(self):
        n = make_note(self.tmp, status="pending", box=" ", extra="  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*")
        # 先把 T-02 的進行中拿掉，測試從純 pending 開始
        text = n.path.read_text(encoding="utf-8").replace("  - **狀態**：🟡 進行中\n", "")
        n.path.write_text(text, encoding="utf-8")

        st = tc.apply_claim(n.path, "T-20261020-01")
        self.assertEqual(st, "in-progress")
        self.assertTrue(bi.parse_note(n.path).tasks[0].in_progress)

        st = tc.apply_complete(n.path, "T-20261020-01", "commit 999999", "2026-10-24")
        self.assertEqual(st, "in-progress")  # T-02 仍未完成

        st = tc.apply_close(n.path, "T-20261020-02", "與現有工具重複")
        self.assertEqual(st, "done")  # 1 done + 1 archived => 筆記 done
        parsed = bi.parse_note(n.path)
        self.assertEqual(vi.check_notes([parsed]), [])

    def test_build_readme_replaces_only_generated_blocks(self):
        readme = ("手寫\n<!-- BEGIN GENERATED: tasks -->\nold\n<!-- END GENERATED: tasks -->\n"
                  "中間\n<!-- BEGIN GENERATED: index -->\n<!-- END GENERATED: index -->\n"
                  "<!-- BEGIN GENERATED: clusters -->\n<!-- END GENERATED: clusters -->\n尾")
        out = bi.build_readme(readme, [make_note(self.tmp)])
        self.assertTrue(out.startswith("手寫\n") and out.endswith("尾"))
        self.assertIn("中間", out)
        self.assertNotIn("old", out)
        self.assertEqual(out, bi.build_readme(out, [make_note(self.tmp)]))  # 冪等

    def test_missing_cluster_fields_detected(self):
        n = make_note(self.tmp)
        n.meta["cluster"] = "9"
        del n.meta["short_title"]
        errs = vi.check_notes([n])
        self.assertTrue(any("'cluster'" in e for e in errs), errs)
        self.assertTrue(any("'short_title'" in e for e in errs), errs)

    def test_render_clusters_groups_notes_by_role(self):
        a = make_note(self.tmp, slug="2026-10-20-a")
        b = make_note(self.tmp, slug="2026-10-20-b")
        b.meta["short_title"] = "第二篇"
        out = bi.render_clusters([a, b])
        self.assertIn("**集群 1：", out)
        self.assertIn("- 訊息傳輸：[測試短標題](./notes/2026-10-20-a.md)、[第二篇](./notes/2026-10-20-b.md)", out)
        self.assertIn("**集群 4：", out)
        self.assertIn("*（尚無筆記）*", out)

    def test_self_reference_detected(self):
        word = vi.SELF_REFERENCES[0]
        errs = vi.check_self_references({self.tmp / "a.md": f"經{word}決定", self.tmp / "b.md": "經維護者決定"})
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("a.md", errs[0])

    def test_archived_matches_status_prefix_only(self):
        n = make_note(self.tmp)
        t = n.tasks[1]
        t.fields["狀態"] = "🟡 進行中（等待關閉 PR）"
        self.assertFalse(t.archived)
        self.assertTrue(t.in_progress)
        t.fields["狀態"] = "⚪ 不做（進行中的重複項）"
        self.assertTrue(t.archived)
        self.assertFalse(t.in_progress)  # 已封存就不是進行中

    def test_complete_on_done_task_is_rejected_and_file_untouched(self):
        n = make_note(self.tmp)
        before = n.path.read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            tc.apply_complete(n.path, "T-20261020-01", "new evidence", "2026-11-01")
        self.assertEqual(before, n.path.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            tc.apply_claim(n.path, "T-20261020-01")
        with self.assertRaises(ValueError):
            tc.apply_close(n.path, "T-20261020-01", "x")

    def test_cli_main_reports_unknown_id_without_traceback_and_survives_captured_stdout(self):
        out, err = io.StringIO(), io.StringIO()  # StringIO 沒有 reconfigure
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = tc.main(["show", "T-99999999-99"])
        self.assertEqual(rc, 1)
        self.assertIn("T-99999999-99", err.getvalue())

    def test_secret_scan_skip_labels_and_non_md_files(self):
        texts = {self.tmp / "page.html": "AKIA" + "A" * 16 + " conversation://abc"}
        errs = vi.check_secrets(texts, skip_labels=(vi.SESSION_LINK_LABEL,))
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("AWS", errs[0])
        self.assertIn(".html", vi.SCANNED_SUFFIXES)

    def test_links_percent_encoding_and_query(self):
        (self.tmp / "a b.md").write_text("x", encoding="utf-8")
        ok = {self.tmp / "r.md": "[a](a%20b.md) [b](a%20b.md?x=1#h)"}
        self.assertEqual(vi.check_links(ok), [])
        bad = {self.tmp / "r.md": "[a](missing.md)"}
        self.assertEqual(len(vi.check_links(bad)), 1)

    def test_stale_readme_detected(self):
        n = make_note(self.tmp)
        readme = self.tmp / "README.md"
        body = "".join(f"<!-- BEGIN GENERATED: {k} -->\n<!-- END GENERATED: {k} -->\n"
                       for k in ("tasks", "index", "clusters"))
        readme.write_text(bi.build_readme(body, [n]), encoding="utf-8")
        old = bi.README_FILE
        bi.README_FILE = readme
        try:
            self.assertEqual(vi.check_readme([n]), [])
            readme.write_text(readme.read_text(encoding="utf-8").replace("共 2 項", "共 9 項"), encoding="utf-8")
            self.assertEqual(len(vi.check_readme([n])), 1)
        finally:
            bi.README_FILE = old

    def test_build_readme_requires_markers(self):
        with self.assertRaises(SystemExit):
            bi.build_readme("沒有標記", [])


if __name__ == "__main__":
    unittest.main()
