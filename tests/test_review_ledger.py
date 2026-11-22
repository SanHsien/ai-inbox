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

# 雜湊算法定版用的固定範例（golden test）：涵蓋 frontmatter status（含註解）、當前狀態行、已完成與未完成與進行中與不做的任務、
# 狀態欄位、非標準欄位寫法、程式碼圍欄。不要為了讓測試綠而改這份文字或期望值。
GOLDEN_NOTE = """---
id: 2026-11-22-golden
title: "固定範例"
source_url: "https://example.com/golden"
analyzed_at: 2026-11-22
written_by: "claude/opus-5.5@00000001-0000-4000-8000-000000000001"
status: in-progress # 註解算進雜湊
cluster: 1
source_review: full
tags:
  - golden
---

# 固定範例

- **當前狀態**：`🟡 進行中 (In Progress)`

本文主張固定的內容。

```text
- [x] **`T-20261122-99`**｜**[優先級：高]** 圍欄裡的不是任務
  - **狀態**：圍欄裡的文字照算
```

- [x] **`T-20261122-01`**｜**[優先級：高]** 已完成的任務
  - **目標範圍**：`some/repo`
  - **驗收標準（DoD）**：做完
  - **完成日期**：2026-11-24
  - **實作紀錄 / 證據**：commit abc
- [ ] **`T-20261122-02`**｜**[優先級：中]** 進行中的任務
  - **狀態**：🟡 進行中
  - **目標範圍**：`some/repo`
  - **驗收標準（DoD）**：做完
- [ ] **`T-20261122-03`**｜**[優先級：低]** 不做的任務
  - **狀態**：⚪ 不做（理由）
  - **目標範圍**：`some/repo`
  - **驗收標準（DoD）**：做完
- [ ] **`T-20261122-04`**｜**[優先級：低]** 非標準寫法的任務
  - **狀態**：🟡 進行中（等人回覆）
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（任意佔位文字不在白名單，算進雜湊）*
  - **目標範圍**：`some/repo`
  - **驗收標準（DoD）**：做完
"""
GOLDEN_HASH = "36f10aeee427a2a42bd9ec55203e133e81a14ad2630b4f08a123a81cd227216a"


class Base(unittest.TestCase):
    def setUp(self):
        if getattr(self, "_tmp", None):  # 同一測試內重設環境時，先清掉上一個暫存目錄
            self._tmp.cleanup()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "notes").mkdir()
        (self.root / "reviews").mkdir()
        self.slug = "2026-11-22-test-note-1"  # 第一筆審查者是 REVIEWER 時不會被抽查（rl.sampled）

    def tearDown(self):
        self._tmp.cleanup()

    def note_path(self) -> Path:
        return self.root / "notes" / f"{self.slug}.md"

    def write_note(self, written_by=AUTHOR, extra_meta="", claim=None, want_sampled=False, first_reviewer=REVIEWER):
        """寫筆記；預設用「第一筆審查者是 first_reviewer 時不會被抽查」的 slug，want_sampled=True 則換成會被抽中的 slug。"""
        if rl.sampled(self.slug, first_reviewer) != want_sampled:
            base = self.slug
            self.slug = next(f"{base}-{i}" for i in range(1, 400) if rl.sampled(f"{base}-{i}", first_reviewer) == want_sampled)
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
            "scope": list(rl.SCOPES), "content_sha256": sha, "hash_version": rl.HASH_VERSION, "verdict": "pass",
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

    def test_sampling_is_not_decided_by_content(self):
        """抽查不看內容：改內容躲不掉（舊制看內容雜湊，改一個字就能換到不被抽中的雜湊）。"""
        self.write_note(want_sampled=True)
        self.assertTrue(rl.sampled(self.slug, REVIEWER))
        self.add_review()
        path = self.note_path()
        path.write_text(path.read_text(encoding="utf-8").replace("本文主張", "改個字再主張"), encoding="utf-8")
        self.add_review(reviewer=OTHER_CODEX)  # 第一筆審查者仍是 REVIEWER
        st = self.state()
        self.assertTrue(any("抽查" in n for n in st.needs), st.needs)

    def test_sampling_depends_on_first_reviewer_which_the_author_cannot_pick(self):
        """N7：只看 slug 的話，作者自己挑 slug 就能躲；加上第一筆審查者（作者選不了）。沒有紀錄時不算抽中。"""
        self.assertFalse(rl.sampled("any-slug", None))
        self.assertFalse(rl.sampled("any-slug", ""))
        slug = "2026-11-22-test-note"
        self.assertEqual({True, False}, {rl.sampled(slug, f"codex/gpt-6.1-sol@{sess(n)}") for n in range(60, 160)})
        self.write_note(want_sampled=True)
        self.assertFalse([n for n in self.state().needs if "抽查" in n])  # 還沒有紀錄：不觸發抽查

    def test_sampling_ignores_case_and_surrounding_whitespace(self):
        """R7：同一個 session 寫成大寫或帶空白，抽查結果不能變。"""
        slug = "2026-11-22-test-note"
        for n in range(200, 230):
            r = f"claude/opus-5.5@{sess(n)}"
            self.assertEqual(rl.sampled(slug, r), rl.sampled(slug, r.upper()))
            self.assertEqual(rl.sampled(slug, r), rl.sampled(slug, f" {r} \n"))

    def test_golden_hash_of_a_fixed_note(self):
        """雜湊算法定版（R6 是上線前最後一次調整：此時 main 上還沒有任何審查紀錄，所以只重產基準、HASH_VERSION 維持 1）。
        改了 analysis_text 會讓 main 上所有審查紀錄與 legacy 基準失效。
        要改必須寫遷移（重算基準、把仍對應現行內容的紀錄重新派審）並遞增 HASH_VERSION，不可只更新這個期望值。"""
        self.assertEqual(1, rl.HASH_VERSION)
        self.assertEqual(GOLDEN_HASH, rl.content_hash(GOLDEN_NOTE),
                         "改了 analysis_text 會讓 main 上所有審查紀錄與 legacy 基準失效；要改必須寫遷移"
                         "（重算基準、把仍對應現行內容的紀錄重新派審），不可只更新這個期望值")


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

    def hash_after_inserting(self, extra_lines, complete=False):
        """在任務欄位後插入幾行，回傳（插入前雜湊, 插入後雜湊）。"""
        self.write_note()
        path = self.note_path()
        if complete:
            tc.apply_complete(path, "T-20261122-01", "commit abc", "2026-11-24")
        before = self.sha()
        text = path.read_text(encoding="utf-8")
        anchor = "  - **驗收標準（DoD）**：做完\n"
        path.write_text(text.replace(anchor, anchor + extra_lines, 1), encoding="utf-8")
        return before, self.sha()

    def test_repeated_or_malformed_state_fields_are_hashed(self):
        """N3：任務區塊內的欄位行不限行數、不限縮排地被略過，可以藏任意文字；現在只略過 task_cli 會寫的那一行。"""
        for extra in (
            "  - **狀態**：🟡 進行中\n  - **狀態**：🟡 進行中\n",                  # 同鍵第二次出現
            "  - **狀態**：偷加的非標準狀態文字\n",                                # 非標準值
            "      - **實作紀錄 / 證據**：更深縮排但長得像欄位\n",
            "  - ** 狀態 **：鍵名前後有空白\n",
            "  - **狀態**:半形冒號的偷加文字\n",
            "   - **狀態**：三格縮排\n",
            "  - **完成日期**：2026-11-24\n",                                      # 未完成任務不該有完成日期
            "  - **實作紀錄 / 證據**：未完成任務的偷加證據\n",
            "  - **完成日期**：偷加的非日期\n",
        ):
            before, after = self.hash_after_inserting(extra)
            self.assertNotEqual(before, after, extra)

    def test_repeated_fields_on_a_completed_task_are_hashed(self):
        before, after = self.hash_after_inserting("  - **實作紀錄 / 證據**：第二行證據偷藏結論\n", complete=True)
        self.assertNotEqual(before, after)
        before, after = self.hash_after_inserting("  - **完成日期**：2026-11-25\n", complete=True)
        self.assertNotEqual(before, after)

    def test_completed_task_with_non_date_completion_field_is_hashed(self):
        self.write_note()
        path = self.note_path()
        tc.apply_complete(path, "T-20261122-01", "commit abc", "2026-11-24")
        before = self.sha()
        path.write_text(path.read_text(encoding="utf-8").replace("完成日期**：2026-11-24", "完成日期**：其實沒做完", 1), encoding="utf-8")
        self.assertNotEqual(before, self.sha())

    def test_what_task_cli_writes_is_still_skipped(self):
        """反過來：task_cli 寫的格式（進行中、不做（理由）、已完成的日期與單行證據、範本佔位）不進雜湊。"""
        self.write_note()
        path = self.note_path()
        before = self.sha()
        text = path.read_text(encoding="utf-8")
        anchor = "  - **驗收標準（DoD）**：做完\n"
        for extra in ("  - **狀態**：🟡 進行中\n", "  - **狀態**：⚪ 不做（理由 含（括號））\n",
                      "  - **完成日期**：*（完成時填 YYYY-MM-DD）*\n", "  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*\n",
                      "  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*\n", "  - **完成日期**：\n"):
            path.write_text(text.replace(anchor, anchor + extra, 1), encoding="utf-8")
            self.assertEqual(before, self.sha(), extra)

    def test_unchecked_task_placeholder_window_is_a_whitelist(self):
        """R6：未完成任務的「完成日期」「實作紀錄 / 證據」不能再用任意 `*（` 開頭的文字藏分析內容；只認固定佔位字串。"""
        for key in ("完成日期", "實作紀錄 / 證據"):
            for hidden in ("*（隱藏分析：其實 X 不成立）", "*（待完成後由執行 Agent 填寫）*之外多的字", "*（待完成後由執行 Agent 填寫", "*（隱藏）*"):
                before, after = self.hash_after_inserting(f"  - **{key}**：{hidden}\n")
                self.assertNotEqual(before, after, (key, hidden))
        for key in ("完成日期", "實作紀錄 / 證據"):
            for ok in sorted(rl.PLACEHOLDER_VALUES):
                before, after = self.hash_after_inserting(f"  - **{key}**：{ok}\n")
                self.assertEqual(before, after, (key, ok))

    def test_every_placeholder_used_by_repo_notes_is_whitelisted(self):
        """白名單要涵蓋現有筆記裡未勾選任務實際用過的固定寫法（不然 task_cli 操作會讓那些筆記雜湊變動）。"""
        for note in bi.load_notes():
            for task in note.tasks:
                if task.done:
                    continue
                for key in ("完成日期", "實作紀錄 / 證據"):
                    v = task.fields.get(key, "").strip()
                    if v.startswith("*（") and v.endswith("）*"):
                        self.assertIn(v, rl.PLACEHOLDER_VALUES, (note.slug, task.id, key))

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
    # 非標準寫法的任務（例：`⚪ 不做（…）。` 句尾多了句點；退回重開的任務保留舊的「實作紀錄 / 證據」）
    # 其狀態欄位算進雜湊，task_cli 操作後雜湊會變，那篇筆記就要走審查。這是安全的方向，不為它放寬規則。
    # 這裡拿 repo 的真實筆記抽查「絕大多數任務操作後雜湊不變」，不逐篇釘死：
    # 別的 agent 寫了一個非標準任務，不該讓所有人的 CI 變紅（標準格式由 HashTest 的合成筆記嚴格把關）。
    MAX_NONSTANDARD_RATIO = 0.05

    def test_claim_complete_close_keep_hash_for_nearly_all_repo_tasks(self):
        """對 repo 現有全部筆記模擬 claim／complete／close：絕大多數任務的分析內容雜湊不變。"""
        notes = bi.load_notes()
        self.assertGreater(len(notes), 100)
        checked = 0
        tasks_seen = set()
        changed = set()
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
                        tasks_seen.add((note.slug, task.id))
                        if before != rl.content_hash(work.read_text(encoding="utf-8")):
                            changed.add((note.slug, task.id))
                        checked += 1
        self.assertGreater(checked, 50)
        limit = max(3, int(len(tasks_seen) * self.MAX_NONSTANDARD_RATIO))
        self.assertLessEqual(
            len(changed), limit,
            f"{len(changed)}／{len(tasks_seen)} 個未完成任務在 task_cli 操作後雜湊會變，超過 {limit} 個："
            f"多半是 analysis_text 或 task_cli 改壞了，不是個別筆記的寫法問題。樣本：{sorted(changed)[:5]}",
        )


class IdentityTest(unittest.TestCase):
    def test_runtime_specific_session_formats(self):
        uuid = "01a1fcb9-6070-7fc1-9407-2a5b4823514b"
        ok = [f"claude/opus-5.5@{uuid}", f"codex/gpt-6.1-sol@{uuid}", "antigravity/gemini-3@abcdefgh",
              "hermes/xiaoma@hermes-session-1", "human/maintainer@2026-11-21", rl.LEGACY_AUTHOR]
        for text in ok:
            self.assertIsNotNone(rl.parse_identity(text), text)
        bad = [f"claude/opus-5.5@{uuid[:8]}",  # 縮寫
               f"claude/opus-5.5@{uuid.upper()}", f"codex/gpt-6.1-sol@{uuid.upper()}",  # R7：UUID 必須小寫
               f"codex/GPT-6.1-Sol@{uuid}", f"claude/Opus-5.5@{uuid}", f"Claude/opus-5.5@{uuid}",  # runtime、model 必須小寫
               f"codex/gpt-6.1-sol@{uuid}0", f"claude/opus-5.5@{uuid[:-1]}", "claude/opus-5.5@author-session-1",
               "antigravity/gemini-3@abcdefg", "hermes/xiaoma@short",
               "human/maintainer@today", "human/maintainer@2026-13-45", "human/someone@2026-11-21", "human/maintainer@798b1dc7",
               "legacy/unknown@other-session", "legacy/other@pre-review", "robot/x@session-1", "claude/opus-5.5"]
        for text in bad:
            self.assertIsNone(rl.parse_identity(text), text)

    def test_strong_model_is_strict(self):
        uuid = sess(9)
        strong = [f"claude/opus-5.5@{uuid}", f"claude/opus-5@{uuid}", f"codex/gpt-6.1-sol@{uuid}", f"codex/gpt-6-astra@{uuid}",
                  f"codex/gpt-6.2-sol@{uuid}"]
        # N1：模型綁 runtime；human/maintainer 不再是強模型
        weak = [f"claude/opus-anything@{uuid}", f"claude/opus@{uuid}", f"claude/opus-5.5-fast@{uuid}", f"codex/gpt-5.5-sol@{uuid}",
                f"codex/gpt-6.1-solx@{uuid}", f"claude/sonnet-5.5@{uuid}", f"claude/maintainer@{uuid}",
                "hermes/maintainer@abcdefgh", "antigravity/maintainer@abcdefgh", "human/maintainer@2026-11-21",
                "hermes/opus-5@abcdefgh", "antigravity/opus-5@abcdefgh", f"codex/opus-5.5@{uuid}", f"claude/gpt-6.1-sol@{uuid}",
                "hermes/gpt-6.1-sol@abcdefgh"]
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
        self.write_note(written_by=f"antigravity/gemini-3@{sess(8)[:20]}")
        self.add_review(reviewer=f"claude/opus-5.5@{sess(8)}")
        self.assertTrue(any("不能審自己寫的內容" in e for e in self.state().errors))

    def test_same_uuid_under_another_runtime_cannot_audit_own_round(self):
        self.write_note()
        self.add_review(reviewer=f"codex/gpt-6.1-sol@{sess(9)}", verdict="changes_requested", corrections=2)
        self.add_review(reviewer=f"claude/opus-5.5@{sess(9)}", role="audit")
        self.assertTrue(any("覆核要換人" in e for e in self.state().errors))

    def test_reviewer_runtime_must_be_claude_or_codex(self):
        """N1：human、hermes、antigravity 都不能當審查者（也不能 audit）；它們可以當作者。"""
        for reviewer in ("human/maintainer@2026-11-22", "hermes/opus-5@whatever-1234", "antigravity/opus-5@whatever-1234"):
            for role in ("review", "audit"):
                self.setUp()
                self.write_note()
                self.add_review(reviewer=reviewer, role=role)
                st = self.state()
                self.assertFalse(st.reviewed, (reviewer, role))
                self.assertTrue(any("runtime 只接受" in e for e in st.errors), (reviewer, role, st.errors))

    def test_forged_human_maintainer_pair_cannot_release_a_note(self):
        """N1 重現：human/maintainer 的 review 加 audit 兩筆放行的做法，現在每一筆都報錯。"""
        self.write_note()
        self.add_review(reviewer="human/maintainer@2026-11-22")
        self.add_review(reviewer="human/maintainer@2026-11-21", role="audit")
        st = self.state()
        self.assertFalse(st.reviewed)
        self.assertEqual(2, sum("runtime 只接受" in e for e in st.errors), st.errors)

    def test_other_runtimes_can_still_be_authors(self):
        for wb in ("hermes/xiaoma@hermes-session-1", "antigravity/gemini-3@abcdefgh", "human/maintainer@2026-11-22"):
            st = self.state(self.write_note(written_by=wb))
            self.assertEqual([], [e for e in st.errors if "written_by" in e], (wb, st.errors))

    def test_hash_version_is_required_and_must_match(self):
        """N2：紀錄要帶 hash_version，不等於現行版本就報錯並指向遷移。"""
        for over in ({"hash_version": 0}, {"hash_version": rl.HASH_VERSION + 1}, {"hash_version": None}):
            self.setUp()
            self.write_note()
            self.add_review(**over)
            st = self.state()
            self.assertFalse(st.reviewed, over)
            self.assertTrue(any("hash_version" in e and "遷移" in e for e in st.errors), (over, st.errors))
        self.setUp()
        self.write_note()
        entry = self.add_review()
        path = self.root / "reviews" / f"{self.slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        del data["reviews"][0]["hash_version"]
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.assertTrue(any("hash_version" in e for e in self.state().errors), entry)


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
        self.add_review(reviewer=f"claude/sonnet-5.5@{sess(11)}")
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
        env = {k: v for k, v in os.environ.items() if k != "AI_INBOX_REVIEW_BASE"}
        patcher = unittest.mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        run_git(self.root, "init", "-q")
        self.write_note()
        self.add_review(verdict="changes_requested", corrections=1)
        self.add_review(reviewer=OTHER_CODEX)
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", "init")
        self.first_commit = run_git(self.root, "rev-parse", "HEAD").strip()

    def test_tampering_that_was_committed_is_caught_against_the_ci_base(self):
        """N4：改紀錄 verdict 並在報告尾端加一個新的 pass 區塊，一旦 commit，只比 HEAD 就看不出來；CI 用前一個 commit 當基準。"""
        data = json.loads(self.ledger().read_text(encoding="utf-8"))
        data["reviews"][0].update(verdict="pass", corrections=0)
        self.ledger().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        report = self.root / data["reviews"][0]["report"]
        with report.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write('\n```json\n{"verdict": "pass", "corrections": 0, "scope": ["source", "facts", "evidence", "task_impact"], "findings": []}\n```\n')
        self.assertTrue(self.errors())  # 未提交：HEAD 基準擋得住
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", "tamper")
        self.assertEqual([], self.errors())  # 提交之後只比 HEAD：沒東西可比，等於失效（N4 的原始洞）
        with unittest.mock.patch.dict(os.environ, {"AI_INBOX_REVIEW_BASE": self.first_commit}):
            errors = self.errors()
        self.assertTrue(any("已提交的審查紀錄被改動" in e and "AI_INBOX_REVIEW_BASE" in e for e in errors), errors)
        self.assertTrue(any("已提交的審查報告被改動或刪除" in e for e in errors), errors)

    def test_blank_or_all_zero_bases_are_skipped(self):
        for base in ("0" * 40, "0" * 64, "  ", ""):
            with unittest.mock.patch.dict(os.environ, {"AI_INBOX_REVIEW_BASE": base}):
                self.assertEqual([], self.errors(), base)

    def test_missing_or_non_ancestor_base_is_an_error(self):
        """R2：CI 給了真的基準卻抓不到（force-push、checkout 太淺）或不是 HEAD 的祖先，不可默默略過。"""
        # 存在但不是祖先：從 first_commit 分岔出去的另一條線
        run_git(self.root, "checkout", "-q", "-b", "other", self.first_commit)
        (self.root / "other.txt").write_text("x", encoding="utf-8")
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", "diverged")
        diverged = run_git(self.root, "rev-parse", "HEAD").strip()
        run_git(self.root, "checkout", "-q", "-")
        for base in ("1" * 40, "no-such-ref", diverged):
            with unittest.mock.patch.dict(os.environ, {"AI_INBOX_REVIEW_BASE": base}):
                errors = self.errors()
            self.assertTrue(any("AI_INBOX_REVIEW_BASE" in e and "祖先" in e for e in errors), (base, errors))
        with unittest.mock.patch.dict(os.environ, {"AI_INBOX_REVIEW_BASE": self.first_commit}):
            self.assertEqual([], self.errors())  # 真正的祖先照常通過

    def test_merge_base_with_origin_main_is_a_base_too(self):
        """本機分支上已提交但還沒進 main 的改動：比 merge-base origin/main。"""
        run_git(self.root, "update-ref", "refs/remotes/origin/main", self.first_commit)
        data = json.loads(self.ledger().read_text(encoding="utf-8"))
        data["reviews"] = data["reviews"][::-1]
        self.ledger().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        run_git(self.root, "commit", "-q", "-am", "reorder")
        errors = self.errors()
        self.assertTrue(any("merge-base origin/main" in e for e in errors), errors)

    def test_staged_new_report_is_not_flagged(self):
        """N5：已 git add 的新報告不是「被改動或刪除」。"""
        new = self.root / "reviews" / "reports" / self.slug / "2026-11-24-new.md"
        new.write_text("新報告\n", encoding="utf-8")
        run_git(self.root, "add", "-A")
        self.assertEqual([], self.errors())

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


class ExemptNoteReviewOutcomeTest(Base):
    """R5：免審舊筆記的補審結論不可被忽略。只有「還沒審完」才維持免審。"""

    def exempt(self, today=TODAY):
        note = self.write_note(written_by="")
        return note, {self.slug: self.sha()}

    def evaluate(self, note, legacy, today=TODAY):
        return rl.evaluate(note, legacy, today, self.root)

    def test_record_with_errors_makes_the_note_pending(self):
        note, legacy = self.exempt()
        self.add_review(verdict="changes_requested", corrections=1)
        self.add_review(reviewer="someone")  # 壞資料
        st = self.evaluate(note, legacy)
        self.assertTrue(st.flagged and st.pending)
        self.assertTrue(any(e.startswith("reviews/") for e in st.errors), st.errors)
        self.assertEqual([], [e for e in st.errors if "超過寬限" in e])  # 寬限內

    def test_corrupt_ledger_file_makes_the_note_pending(self):
        note, legacy = self.exempt()
        (self.root / "reviews" / f"{self.slug}.json").write_text("{壞掉", encoding="utf-8")
        st = self.evaluate(note, legacy)
        self.assertTrue(st.pending)
        self.assertTrue(any("不是合法 JSON" in e for e in st.errors), st.errors)

    def test_pass_that_disagrees_with_note_source_review_makes_the_note_pending(self):
        note, legacy = self.exempt()
        self.add_review(source_review="partial")  # 筆記寫 full，審查者判 partial（下修）
        st = self.evaluate(note, legacy)
        self.assertTrue(st.flagged and st.pending)
        self.assertTrue(any("筆記要照審查結論改" in e for e in st.errors), st.errors)
        st = self.evaluate(note, legacy, today=dt.date(2026, 12, 2))  # 審查 11-23，第 9 天
        self.assertTrue(st.overdue)

    def test_unfinished_review_keeps_the_note_exempt(self):
        """缺範圍、需要 audit 但還沒做：不算待審，只在 queue --legacy 出現。"""
        note, legacy = self.exempt()
        self.add_review(scope=["facts"])
        st = self.evaluate(note, legacy)
        self.assertFalse(st.pending)
        self.assertEqual([], st.errors)
        self.setUp()
        note, legacy = self.exempt()
        self.add_review(reviewer=WEAK)  # 弱模型 pass：要 audit，但還沒做
        st = self.evaluate(note, legacy)
        self.assertFalse(st.pending)
        self.assertEqual([], st.errors)
        backfill = rl.evaluate(note, legacy, TODAY, self.root, backfill=True)
        self.assertTrue(any("強模型覆核" in n for n in backfill.needs), backfill.needs)

    def test_open_changes_requested_still_pending(self):
        note, legacy = self.exempt()
        self.add_review(verdict="changes_requested", corrections=1)
        self.assertTrue(self.evaluate(note, legacy).pending)


class RemovedNotesTest(Base):
    """R4：有審查紀錄的筆記不能改名；要移出 repo 就在 reviews/removed.json 登記（只追加），同名筆記不可復活。"""

    def setUp(self):
        super().setUp()
        env = {k: v for k, v in os.environ.items() if k != "AI_INBOX_REVIEW_BASE"}
        patcher = unittest.mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        run_git(self.root, "init", "-q")
        self.write_note()
        self.add_review()
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", "init")

    def removed_path(self) -> Path:
        return self.root / "reviews" / rl.REMOVED_NAME

    def register(self, *slugs, extra=None):
        path = self.removed_path()
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"removed": []}
        for slug in slugs:
            data["removed"].append({"slug": slug, "removed_at": "2026-11-24", "reason": "移到別的 repo", **(extra or {})})
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def remove_note_and_records(self):
        self.note_path().unlink()
        (self.root / "reviews" / f"{self.slug}.json").unlink()
        for p in (self.root / "reviews" / "reports" / self.slug).glob("*"):
            p.unlink()

    def errors(self, notes=()):
        return rl.evaluate_all(list(notes), TODAY, self.root)[1]

    def test_registered_removal_passes(self):
        self.remove_note_and_records()
        self.register(self.slug)
        self.assertEqual([], self.errors())

    def test_registered_removal_may_keep_the_ledger_without_orphan_error(self):
        self.note_path().unlink()
        self.register(self.slug)
        self.assertEqual([], self.errors())

    def test_unregistered_removal_is_rejected_with_a_hint(self):
        self.remove_note_and_records()
        errors = self.errors()
        self.assertTrue(any("已提交的審查紀錄被刪除" in e and "removed.json" in e for e in errors), errors)
        self.assertTrue(any("已提交的審查報告被改動或刪除" in e and "removed.json" in e for e in errors), errors)

    def test_orphan_ledger_error_hints_at_registration(self):
        self.note_path().unlink()
        errors = self.errors()
        self.assertTrue(any("不存在" in e and "removed.json" in e for e in errors), errors)

    def test_registered_slug_cannot_come_back(self):
        """登記後同名筆記又出現：報錯（否則刪掉紀錄再放回，舊筆記就能回到免審）。"""
        self.remove_note_and_records()
        self.register(self.slug)
        note = self.write_note()
        errors = self.errors([note])
        self.assertTrue(any("不可復活" in e for e in errors), errors)

    def test_removed_list_is_append_only(self):
        self.remove_note_and_records()
        self.register(self.slug)
        run_git(self.root, "add", "-A")
        run_git(self.root, "commit", "-q", "-m", "remove")
        self.assertEqual([], self.errors())
        self.removed_path().write_text(json.dumps({"removed": []}), encoding="utf-8")  # 清掉登記
        self.assertTrue(any("removed.json" in e and "被改動" in e for e in self.errors()), self.errors())
        self.removed_path().unlink()
        self.assertTrue(any("removed.json" in e and "被刪除" in e for e in self.errors()), self.errors())
        self.register(self.slug, "another-note")  # 追加是允許的
        self.assertEqual([], self.errors())

    def test_removed_entries_are_validated(self):
        self.removed_path().write_text(json.dumps({"removed": [
            {"slug": "a", "removed_at": "2026-11-24"},                                 # 缺 reason
            {"slug": "b", "removed_at": "2027-01-01", "reason": "未來日期"},
            {"slug": "c", "removed_at": "昨天", "reason": "日期格式錯"},
            "不是物件",
        ]}), encoding="utf-8")
        errors = self.errors([bi.parse_note(self.note_path())])
        self.assertEqual(4, sum(e.startswith("reviews/removed.json 第") for e in errors), errors)
        self.removed_path().write_text("{壞", encoding="utf-8")
        self.assertTrue(any("removed.json" in e and "JSON" in e for e in self.errors()))


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
        """repo 裡現有的審查紀錄（如果有）在現行規則下合法；沒有紀錄也不該有單篇或基準錯誤。
        「對照 HEAD／基準」的只追加錯誤跟工作樹與提交狀態有關（例如尚未提交的 git rm），不在這個測試的範圍。"""
        # R1：用今天的日期，並且只斷言「審查紀錄本身」的錯誤（訊息以 reviews/ 開頭）。筆記待審逾期、缺 written_by、
        # analyzed_at 晚於寫死的日期等，是 verify_inbox 的事；寫死日期會讓合併後第一篇新筆記就把 CI 弄紅。
        notes = bi.load_notes()
        states, errors = rl.evaluate_all(notes, dt.date.today())
        ledgers = [p for p in (bi.REPO_ROOT / "reviews").glob("*.json")
                   if p.name not in (rl.LEGACY_BASELINE_NAME, rl.REMOVED_NAME)]
        for p in ledgers:
            self.assertIn(p.stem, states, p.name)
            self.assertEqual([], [e for e in states[p.stem].errors if e.startswith("reviews/")], p.name)
        self.assertEqual([], [e for e in errors if e.startswith("reviews/") and "對照" not in e])
        self.assertEqual([], [e for st in states.values() for e in st.errors if e.startswith("reviews/")])

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
