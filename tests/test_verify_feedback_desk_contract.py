"""tools/verify_feedback_desk_contract.py 的單元測試：合法案例必須過，每一種違規都要有會失敗的反例。"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "verify_feedback_desk_contract.py"
sys.path.insert(0, str(TOOL.parent))
import verify_feedback_desk_contract as v  # noqa: E402

GOOD_NOTE = (
    "調整原因：登入後按鈕沒有反應，是因為送出前少了一個確認步驟。\n"
    "調整內容：現在按下「送出」會立刻顯示處理中，完成後跳出成功訊息。\n"
    "驗證方式：請到 https://example.com/orders/new 填寫表單後按「送出」，確認會看到綠色成功訊息。"
)
GOOD_HANDOFF = "做到哪：已重現問題並修好後端；改了哪些檔案：api/v1/auth.ts；下一步：補前端載入中狀態的測試；注意事項：不要動 session storage。"


def status_change(**kw):
    rec = {
        "kind": "status_change", "public_id": "abc-123", "actor_type": "ai", "actor_name": "王小明",
        "agent": "Codex", "from": "new", "to": "needs_input",
        "adjustment_note": GOOD_NOTE, "adjustment_images": ["after.png"],
    }
    rec.update(kw)
    return rec


def handoff(**kw):
    rec = {"kind": "handoff", "public_id": "abc-123", "actor_type": "ai", "actor_name": "王小明", "agent": "Codex", "note": GOOD_HANDOFF}
    rec.update(kw)
    return rec


def adjustment(**kw):
    rec = {"kind": "adjustment", "public_id": "abc-123", "actor_type": "ai", "actor_name": "王小明", "agent": "Codex", "note": GOOD_NOTE, "images": 1}
    rec.update(kw)
    return rec


def codes(rec, level="ERROR"):
    return sorted({f.code for f in v.validate_records([rec]) if f.level == level})


def run_cli(*args, stdin=None, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run([sys.executable, str(TOOL), *args], input=stdin, capture_output=True, text=True, encoding="utf-8", env=e)


class GoodCases(unittest.TestCase):
    def test_good_records_have_no_errors(self):
        for rec in (status_change(), handoff(), adjustment()):
            self.assertEqual(codes(rec), [], rec["kind"])

    def test_human_may_complete_and_chinese_labels_work(self):
        rec = status_change(actor_type="human", agent=None, **{"from": "待審核", "to": "已完成"})
        rec.pop("adjustment_note"); rec.pop("adjustment_images")
        self.assertEqual(codes(rec), [])

    def test_client_completes_only_after_review(self):
        base = dict(actor_type="client", agent=None, actor_name="客戶A")
        ok = status_change(**base, **{"from": "needs_input", "to": "completed"})
        self.assertEqual(codes(ok), [])
        bad = status_change(**base, **{"from": "new", "to": "completed"})
        self.assertIn("client-completed-without-review", codes(bad))

    def test_url_in_note_is_not_a_filename_or_path(self):
        note = GOOD_NOTE.replace("https://example.com/orders/new", "https://example.com/src/app/index.html")
        self.assertEqual(codes(adjustment(note=note)), [])

    def test_dates_and_slash_words_are_not_paths(self):
        note = GOOD_NOTE.replace("確認會看到綠色成功訊息", "確認 2026/11/02 之後的訂單和/或/及退款都正常")
        self.assertEqual(codes(adjustment(note=note)), [])


class AiGate(unittest.TestCase):
    def test_ai_completed_fails_in_every_spelling(self):
        for spelling in ("completed", "COMPLETED", " Completed ", "已完成", "ｃｏｍｐｌｅｔｅｄ", "completed\u200b"):
            self.assertIn("ai-completed", codes(status_change(to=spelling, **{"from": "needs_input"})), repr(spelling))

    def test_ai_disguised_as_human_with_agent_label_is_still_ai(self):
        self.assertIn("ai-completed", codes(status_change(actor_type="human", to="completed")))

    def test_ai_may_not_set_new(self):
        self.assertIn("ai-status-not-allowed", codes(status_change(to="new", **{"from": "needs_input"})))

    def test_ai_needs_input_requires_note_and_image(self):
        r = status_change(); r.pop("adjustment_note")
        self.assertIn("missing-adjustment-note", codes(r))
        r = status_change(adjustment_images=[])
        self.assertIn("missing-screenshot", codes(r))
        r = status_change(adjustment_images=0)
        self.assertIn("missing-screenshot", codes(r))
        r = status_change(adjustment_note="   ")
        self.assertIn("missing-adjustment-note", codes(r))

    def test_ai_without_agent_label_fails(self):
        r = status_change(); r.pop("agent")
        self.assertIn("ai-missing-agent", codes(r))

    def test_agent_label_cannot_fake_bracket_label(self):
        self.assertIn("bad-agent-label", codes(status_change(agent="Codex（管理員）")))
        self.assertIn("bad-agent-label", codes(status_change(agent="x" * 41)))

    def test_unknown_status_and_from_are_errors(self):
        self.assertIn("bad-status", codes(status_change(to="done")))
        self.assertIn("bad-status", codes(status_change(**{"from": None})))
        self.assertIn("bad-status", codes(status_change(to=None)))

    def test_missing_actor_name_fails(self):
        self.assertIn("missing-actor-name", codes(status_change(actor_name="")))

    def test_force_must_be_real_boolean(self):
        # 字串 "false" 在 Python 是 truthy；若被當成 force 就等於繞過認領檢查
        rec = status_change(claim_holder={"name": "李大華", "agent": "Claude Code"}, force="false")
        self.assertIn("bad-type", codes(rec))
        self.assertIn("claim-conflict", codes(rec))


class Claim(unittest.TestCase):
    OTHER = {"name": "李大華", "agent": "Claude Code"}

    def test_other_holder_without_force_fails(self):
        self.assertIn("claim-conflict", codes(status_change(claim_holder=self.OTHER)))

    def test_other_holder_with_force_passes(self):
        self.assertEqual(codes(status_change(claim_holder=self.OTHER, force=True)), [])

    def test_own_claim_passes_and_same_name_other_agent_does_not(self):
        self.assertEqual(codes(status_change(claim_holder={"name": "王小明", "agent": "Codex"})), [])
        self.assertIn("claim-conflict", codes(status_change(claim_holder={"name": "王小明", "agent": "Hermes Agent"})))

    def test_release_must_be_by_holder(self):
        self.assertIn("release-not-holder", codes(handoff(release=True, claim_holder=self.OTHER, force=True)))
        self.assertIn("release-without-claim", codes(handoff(release=True)))
        self.assertEqual(codes(handoff(release=True, claim_holder={"name": "王小明", "agent": "Codex"})), [])


class Handoff(unittest.TestCase):
    def test_missing_done_or_next_fails(self):
        self.assertIn("handoff-missing-section", codes(handoff(note="下一步：補測試")))
        self.assertIn("handoff-missing-section", codes(handoff(note="做到哪：修好後端")))

    def test_empty_or_placeholder_sections_fail(self):
        for body in ("做到哪：；下一步：補測試", "做到哪：無；下一步：補測試", "做到哪：修好；下一步：待補", "做到哪：修好\n下一步：TBD"):
            self.assertIn("handoff-empty-section", codes(handoff(note=body)), body)

    def test_blank_and_non_string_note(self):
        self.assertIn("missing-handoff-note", codes(handoff(note="")))
        self.assertIn("missing-handoff-note", codes(handoff(note=None)))
        self.assertIn("bad-type", codes(handoff(note=["做到哪：x", "下一步：y"])))

    def test_fullwidth_and_multiline_labels_parse(self):
        note = "做到哪：已修好\n改了哪些檔案或分支：fix/login\n下一步：補測試\n注意事項：無"
        self.assertEqual(codes(handoff(note=note)), [])
        self.assertEqual(codes(handoff(note="做到哪: 已修好\n下一步: 補測試"), "WARN"), ["handoff-missing-section"])

    def test_optional_sections_only_warn(self):
        rec = handoff(note="做到哪：已修好\n下一步：補測試")
        self.assertEqual(codes(rec), [])
        self.assertEqual(codes(rec, "WARN"), ["handoff-missing-section"])

    def test_too_long(self):
        self.assertIn("note-too-long", codes(handoff(note="做到哪：" + "字" * 5000 + "\n下一步：補")))

    def test_secrets_rejected(self):
        # 假機密在執行時才拼出來，避免 verify_inbox 的機密掃描把測試檔本身當成外洩
        fake = "a1B2c3D4e5F6g7H8i9J0"
        for leak in ("Bearer " + fake, "fdp" + "_" + fake, "sk" + "-" + fake, "password: hunter2xyz",
                     "gh" + "p_" + fake, "postgres://user:pw@host/db"):
            self.assertIn("secret-in-text", codes(handoff(note=GOOD_HANDOFF + "；" + leak)), leak)

    def test_client_cannot_write_handoff(self):
        self.assertIn("client-handoff", codes(handoff(actor_type="client", agent=None)))


class Slop(unittest.TestCase):
    def bad(self, extra):
        return codes(adjustment(note=GOOD_NOTE.replace("確認會看到綠色成功訊息", extra)))

    def test_code_fence(self):
        self.assertIn("slop-code-block", self.bad("確認\n```js\nfoo()\n```"))
        self.assertIn("slop-code-block", self.bad("確認\n~~~\nx\n~~~"))

    def test_fullwidth_backtick_fence_and_inline(self):
        self.assertIn("slop-code-block", self.bad("確認｀｀｀"))
        self.assertIn("slop-inline-code", self.bad("確認 ｀送出｀ 按鈕"))

    def test_filenames(self):
        for name in ("UserController.php", "auth.ts", "style.css", "package.json", "AGENTS.md"):
            self.assertIn("slop-filename", self.bad(f"我改了 {name} 的內容"), name)

    def test_paths(self):
        for p in ("src/api/v1/auth", "C:\\Users\\me\\proj", "./lib/util", "app\\models\\user"):
            self.assertIn("slop-path", self.bad(f"在 {p} 修正"), p)

    def test_code_call_and_trace(self):
        self.assertIn("slop-code-call", self.bad("呼叫 handleSubmit(event) 修正"))
        self.assertIn("slop-error-trace", self.bad("修正 NPE"))
        self.assertIn("slop-error-trace", self.bad("Traceback (most recent call last)"))

    def test_r24_scan_items(self):
        self.assertIn("slop-identifier", self.bad("把 user_id 對應好"))
        self.assertIn("slop-braces", self.bad("填入 {name} 欄位"))
        self.assertIn("slop-dollar-var", self.bad("使用 $total 計算"))
        self.assertIn("slop-backslash", self.bad("輸入 a\\b"))

    def test_plain_money_and_english_words_pass(self):
        self.assertEqual(self.bad("總價顯示 $100 與 NT$1,200，品牌 Google Chrome 都正確"), [])

    def test_zero_width_cannot_hide_filename(self):
        self.assertIn("slop-filename", self.bad("改了 auth\u200b.ts"))

    def test_jargon_is_warning_only(self):
        rec = adjustment(note=GOOD_NOTE.replace("確認會看到綠色成功訊息", "確認重構後的結果"))
        self.assertEqual(codes(rec), [])
        self.assertEqual(codes(rec, "WARN"), ["slop-jargon"])

    def test_missing_or_empty_note_sections(self):
        no_reason = GOOD_NOTE.split("\n", 1)[1]
        self.assertIn("note-missing-section", codes(adjustment(note=no_reason)))
        empty = GOOD_NOTE.replace("調整內容：現在按下「送出」會立刻顯示處理中，完成後跳出成功訊息。", "調整內容：")
        self.assertIn("note-empty-section", codes(adjustment(note=empty)))

    def test_slop_inside_status_change_is_checked_too(self):
        self.assertIn("slop-filename", codes(status_change(adjustment_note=GOOD_NOTE + " 改了 auth.ts")))

    def test_note_with_secret(self):
        self.assertIn("secret-in-text", codes(adjustment(note=GOOD_NOTE + " token: abcd1234efgh")))

    def test_adjustment_without_image_fails(self):
        self.assertIn("missing-screenshot", codes(adjustment(images=0)))
        self.assertIn("bad-type", codes(adjustment(images=True)))


class InputHandling(unittest.TestCase):
    def test_empty_inputs_raise_not_pass(self):
        for data in ([], {"records": []}):
            with self.assertRaises(v.InputError):
                v.validate_records(data)

    def test_bad_kind_and_non_object(self):
        with self.assertRaises(v.InputError):
            v.validate_records([{"public_id": "x"}])
        with self.assertRaises(v.InputError):
            v.validate_records([{"kind": "ticket"}])
        with self.assertRaises(v.InputError):
            v.validate_records(["status_change"])

    def test_wrapper_and_single_object(self):
        self.assertEqual(v.validate_records({"records": [handoff()]}), [])
        self.assertEqual(v.validate_records(handoff()), [])


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, content, raw=False):
        p = self.dir / name
        if raw:
            p.write_bytes(content)
        else:
            p.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        return str(p)

    def test_exit_codes(self):
        good = self.write("good.json", [status_change(), handoff(), adjustment()])
        r = run_cli(good)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("[PASS]", r.stdout)
        bad = self.write("bad.json", [status_change(to="completed")])
        r = run_cli(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ai-completed", r.stdout)

    def test_no_input_cases_exit_2(self):
        self.assertEqual(run_cli(self.write("empty_list.json", [])).returncode, 2)
        self.assertEqual(run_cli(self.write("empty_file.json", b"", raw=True)).returncode, 2)
        self.assertEqual(run_cli(self.write("broken.json", b"{not json", raw=True)).returncode, 2)
        self.assertEqual(run_cli(self.write("latin.json", b"\xff\xfe\x00", raw=True)).returncode, 2)
        self.assertEqual(run_cli(str(self.dir / "missing.json")).returncode, 2)
        self.assertEqual(run_cli().returncode, 2)
        self.assertEqual(run_cli("-", stdin="").returncode, 2)

    def test_one_bad_file_among_good_fails(self):
        good = self.write("g.json", handoff())
        bad = self.write("b.json", handoff(note="下一步：x"))
        self.assertEqual(run_cli(good, bad).returncode, 1)

    def test_strict_turns_warnings_into_failure(self):
        f = self.write("w.json", handoff(note="做到哪：已修好\n下一步：補測試"))
        self.assertEqual(run_cli(f).returncode, 0)
        self.assertEqual(run_cli(f, "--strict").returncode, 1)

    def test_stdin_and_json_output(self):
        r = run_cli("-", "--json", stdin=json.dumps(handoff(), ensure_ascii=False))
        self.assertEqual(r.returncode, 0)
        self.assertTrue(json.loads(r.stdout)["ok"])
        r = run_cli("-", "--json", stdin=json.dumps(status_change(to="completed"), ensure_ascii=False))
        self.assertEqual(r.returncode, 1)
        out = json.loads(r.stdout)
        self.assertFalse(out["ok"])
        self.assertIn("ai-completed", [x["code"] for x in out["findings"]])

    def test_cp950_console_does_not_crash(self):
        bad = self.write("bad.json", [status_change(to="completed")])
        r = run_cli(bad, env={"PYTHONIOENCODING": "cp950"})
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("UnicodeEncodeError", r.stderr)

    def test_bom_file_is_accepted(self):
        p = self.write("bom.json", b"\xef\xbb\xbf" + json.dumps(handoff(), ensure_ascii=False).encode("utf-8"), raw=True)
        self.assertEqual(run_cli(p).returncode, 0)


ROOT = TOOL.parent.parent
DOC = ROOT / "docs" / "feedback-desk-architecture-and-handoff-spec.md"
TEMPLATE = ROOT / "templates" / "feedback-desk-agent-prompt.md"


def fenced(path, info):
    import re
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```" + re.escape(info) + r"\n(.*?)\n```", text, re.S)
    assert len(blocks) == 1, f"{path.name} 需要剛好一個 ```{info} 區塊，找到 {len(blocks)}"
    return blocks[0]


class DocAndTemplateExamples(unittest.TestCase):
    """文件與範本自己的範例必須符合自己定的標準。"""

    def test_doc_examples(self):
        ok = json.loads(fenced(DOC, "json ok"))
        self.assertEqual([f for f in v.validate_records(ok) if f.level == "ERROR"], [])
        bad = json.loads(fenced(DOC, "json bad"))
        found = {f.code for f in v.validate_records(bad) if f.level == "ERROR"}
        for code in ("ai-completed", "slop-filename", "slop-code-block", "missing-screenshot", "handoff-missing-section"):
            self.assertIn(code, found)

    def test_template_adjustment_example_passes(self):
        rec = adjustment(note=fenced(TEMPLATE, "text adjustment-example"))
        self.assertEqual(codes(rec), [])
        self.assertEqual(codes(rec, "WARN"), [])

    def test_template_handoff_example_passes(self):
        rec = handoff(note=fenced(TEMPLATE, "text handoff-example"), claim_holder={"name": "王小明", "agent": "Codex"}, release=True)
        self.assertEqual(codes(rec), [])
        self.assertEqual(codes(rec, "WARN"), [])

    def test_template_bad_examples_would_fail(self):
        # 範本「不合格」表格裡的寫法，換成調整說明後驗證器要抓得到
        for bad in ("修正 OrderController.php 的空值檢查", "已重構 submit_handler 並調整 API 回傳", "見 src/pages/order.tsx"):
            self.assertTrue(codes(adjustment(note=GOOD_NOTE + " " + bad)), bad)


if __name__ == "__main__":
    unittest.main()
