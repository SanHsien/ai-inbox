"""tools/audit_session_memory_compression.py 的單元測試。

全部使用假資料（暫存資料夾裡現場組出來的假 transcript 與假記憶），不讀任何真實 transcript 或記憶。
機密樣式的假字串在執行期才用字串相加組出，避免這份檔案本身被 verify_inbox.py 的機密掃描擋下。
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "audit_session_memory_compression.py"
sys.path.insert(0, str(TOOL.parent))
import audit_session_memory_compression as a  # noqa: E402

FAKE_HOME = "C:\\Users\\" + "alice" + "\\proj"  # 假帳號 alice，只存在於這份測試

CAUSAL = "因為 CRLF 換行符讓正則失效，所以改用 re.MULTILINE 搭配先正規化換行。"
ABANDON = "決定放棄 lookbehind 方案，因為 Python 3.8 不支援可變長度。"


def transcript_records(extra_text=None):
    recs = [
        {"type": "user", "uuid": "u1", "cwd": FAKE_HOME, "message": {"role": "user", "content": "Windows 上測試掛了，請查。"}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": CAUSAL},
            {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "python -m unittest tests/test_parser.py"}},
        ]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t1", "content":
                "FileNotFoundError: " + FAKE_HOME + "\\src\\parser.py\nENOENT\nRan 12 tests in 0.5s\nFAILED (failures=2)\n"
                "exit code 1 because the log said so"},
        ]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": ABANDON}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t2", "content": "Ran 14 tests in 0.6s\n\nOK\n"},
        ]}},
    ]
    if extra_text:
        recs.append({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": extra_text}]}})
    return recs


# 事實清單（人工數出來，不是用工具算的）：
#   paths 3：tests/test_parser.py、~/proj/src/parser.py（家目錄正規化）…… 實際只有 2 個；見 EXPECTED_TOTALS
#   error_codes：filenotfounderror、enoent、exit code 1
#   test_conclusions：ran 12 tests、failed (failures=2)、ran 14 tests、ok
#   decisions：CAUSAL、ABANDON（tool_result 裡的 "because the log said so" 不算，因為不是一般文字訊息）
EXPECTED_TOTALS = {"paths": 2, "error_codes": 3, "test_conclusions": 4, "decisions": 2}

GOOD_MEMORY = """\
# 解析器測試失敗紀錄

## 背景事實
- 失敗檔案：~/proj/src/parser.py，測試檔 tests/test_parser.py
- 錯誤：FileNotFoundError，errno 名 ENOENT，exit code 1

## 根因分析
- 因為 CRLF 換行符讓正則失效，所以改用 re.MULTILINE 搭配先正規化換行。

## 踩坑結論
- 決定放棄 lookbehind 方案，因為 Python 3.8 不支援可變長度。
- 修前 Ran 12 tests，FAILED (failures=2)；修後 Ran 14 tests，結果：
OK
"""


class Env:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def transcript(self, records=None, name="t.jsonl", raw=None):
        p = self.root / name
        if raw is not None:
            p.write_bytes(raw)
        else:
            lines = [json.dumps(r, ensure_ascii=False) for r in (records if records is not None else transcript_records())]
            p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return p

    def memory(self, text, name="m.md"):
        p = self.root / name
        p.write_text(text, encoding="utf-8", newline="\n")
        return p

    def close(self):
        self._tmp.cleanup()


def run(*args):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp950"  # 模擬 Windows 中文主控台；工具必須自己切 UTF-8
    r = subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, env=env)
    return r.returncode, r.stdout.decode("utf-8"), r.stderr.decode("utf-8")


class Base(unittest.TestCase):
    def setUp(self):
        self.env = Env()
        self.addCleanup(self.env.close)

    def report(self, memory_text, *flags, records=None):
        t = self.env.transcript(records)
        m = self.env.memory(memory_text)
        code, out, err = run("--transcript", t, "--memory", m, "--format", "json", *flags)
        return code, (json.loads(out) if out.strip() else None), err

    def codes(self, rep):
        return {f["code"] for f in rep["findings"]}


class GoodPath(Base):
    def test_fixture_totals_match_hand_count(self):
        code, rep, _ = self.report(GOOD_MEMORY)
        self.assertEqual({c: rep["categories"][c]["total"] for c in a.CATEGORIES}, EXPECTED_TOTALS)

    def test_full_retention_passes_with_zero_loss(self):
        code, rep, err = self.report(GOOD_MEMORY)
        self.assertEqual(code, 0, rep and rep["findings"])
        self.assertEqual(rep["verdict"], "PASS")
        self.assertEqual(rep["information_loss_rate"], 0.0)
        self.assertEqual(rep["facts_total"], sum(EXPECTED_TOTALS.values()))
        self.assertEqual(rep["unsupported"], {"paths": [], "error_codes": [], "test_conclusions": []})

    def test_markdown_report_starts_with_verdict_and_survives_cp950(self):
        t, m = self.env.transcript(), self.env.memory(GOOD_MEMORY)
        code, out, err = run("--transcript", t, "--memory", m)
        self.assertEqual(code, 0, err)
        self.assertTrue(out.startswith("[PASS]"), out[:80])
        self.assertIn("資訊損失率", out)
        self.assertIn("## 限制", out)

    def test_output_file_written(self):
        t, m = self.env.transcript(), self.env.memory(GOOD_MEMORY)
        o = self.env.root / "report.json"
        code, out, err = run("--transcript", t, "--memory", m, "--format", "json", "--output", o)
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(o.read_text(encoding="utf-8"))["verdict"], "PASS")

    def test_loss_rate_is_computed_not_constant(self):
        # 拿掉 ENOENT 一個事實：損失率必須剛好是 1/總數；再拿掉一個，率要跟著變
        facts = sum(EXPECTED_TOTALS.values())
        mem1 = GOOD_MEMORY.replace("，errno 名 ENOENT", "")
        _, r1, _ = self.report(mem1, "--max-loss", "1")
        self.assertEqual(r1["facts_lost"], 1)
        self.assertAlmostEqual(r1["information_loss_rate"], 1 / facts)
        mem2 = mem1.replace("，exit code 1", "")
        _, r2, _ = self.report(mem2, "--max-loss", "1")
        self.assertAlmostEqual(r2["information_loss_rate"], 2 / facts)
        self.assertEqual(r2["categories"]["error_codes"]["lost"], 2)
        self.assertAlmostEqual(r2["categories"]["error_codes"]["loss_rate"], 2 / 3)


class LossDetection(Base):
    def test_empty_memory_fails_with_full_loss(self):
        for text in ("", "   \n\n"):
            code, rep, _ = self.report(text)
            self.assertEqual(code, 1)
            self.assertEqual(rep["information_loss_rate"], 1.0)
            self.assertIn("empty-memory", self.codes(rep))

    def test_facts_hidden_in_html_comment_do_not_count(self):
        code, rep, _ = self.report("# 筆記\n\n<!--\n" + GOOD_MEMORY + "\n-->\n")
        self.assertEqual(code, 1)
        self.assertEqual(rep["information_loss_rate"], 1.0)

    def test_wrong_number_is_loss_and_unsupported(self):
        code, rep, _ = self.report(GOOD_MEMORY.replace("Ran 12 tests", "Ran 11 tests"))
        self.assertEqual(code, 1)
        self.assertIn("ran 12 tests", rep["categories"]["test_conclusions"]["lost_items"])
        self.assertEqual(rep["unsupported"]["test_conclusions"], ["ran 11 tests"])
        self.assertIn("unsupported-fact", self.codes(rep))

    def test_wrong_path_is_loss_and_unsupported(self):
        code, rep, _ = self.report(GOOD_MEMORY.replace("~/proj/src/parser.py", "~/proj/src/parse.py"))
        self.assertEqual(code, 1)
        self.assertEqual(rep["categories"]["paths"]["lost_items"], ["~/proj/src/parser.py"])
        self.assertEqual(rep["unsupported"]["paths"], ["~/proj/src/parse.py"])

    def test_basename_only_is_abstracted_path_and_counts_as_lost(self):
        mem = GOOD_MEMORY.replace("~/proj/src/parser.py", "parser.py（專案解析器）")
        code, rep, _ = self.report(mem, "--max-loss", "1")
        self.assertEqual(rep["categories"]["paths"]["lost"], 1)
        self.assertEqual(rep["degraded_paths_basename_only"], ["~/proj/src/parser.py"])

    def test_decision_without_reason_is_lost(self):
        mem = GOOD_MEMORY.replace(ABANDON, "- 放棄 lookbehind。")
        mem = mem.replace("- - 放棄", "- 放棄")
        code, rep, _ = self.report(mem, "--max-loss", "1")
        self.assertEqual(rep["categories"]["decisions"]["lost"], 1)
        self.assertIn("lookbehind", rep["categories"]["decisions"]["lost_items"][0])

    def test_decision_keeping_action_but_dropping_reason_is_lost(self):
        mem = GOOD_MEMORY.replace(ABANDON, "決定放棄 lookbehind 方案。")
        _, rep, _ = self.report(mem, "--max-loss", "1")
        self.assertEqual(rep["categories"]["decisions"]["lost"], 1)
        # 原因還在、做法被縮成一個詞的情況同樣要算損失
        mem2 = GOOD_MEMORY.replace(CAUSAL, "因為 CRLF 換行符讓正則失效。")
        _, rep2, _ = self.report(mem2, "--max-loss", "1")
        self.assertEqual(rep2["categories"]["decisions"]["lost"], 1)

    def test_ok_result_inline_or_standalone_both_count(self):
        standalone = "結果：\nOK\n"
        self.assertIn(standalone, GOOD_MEMORY)
        _, rep, _ = self.report(GOOD_MEMORY.replace(standalone, "結果：OK\n"))
        self.assertEqual(rep["categories"]["test_conclusions"]["lost"], 0)
        _, rep2, _ = self.report(GOOD_MEMORY.replace(standalone, "結果：好\n"), "--max-loss", "1")
        self.assertEqual(rep2["categories"]["test_conclusions"]["lost_items"], ["ok"])

    def test_long_action_cannot_hide_a_missing_reason(self):
        # 做法很長、原因很短：整句詞元涵蓋率仍高於 0.5，但原因那一段完全沒留下，必須算損失
        action = "決定改用非同步佇列處理上傳並限制同時連線數為四個"
        reason = "因為伺服器逾時太頻繁"
        recs = [
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": action + "，" + reason + "。"}]}},
            {"type": "user", "message": {"role": "user", "content": "ENOENT\nexit code 1\nRan 3 tests\nOK"}},
        ]
        mem = "- ENOENT；exit code 1；Ran 3 tests\nOK\n- " + action + "。\n"
        _, rep, _ = self.report(mem, "--max-loss", "1", records=recs)
        self.assertEqual(rep["categories"]["decisions"]["total"], 1)
        self.assertEqual(rep["categories"]["decisions"]["lost"], 1)
        full = mem.replace(action + "。", action + "，" + reason + "。")
        _, rep2, _ = self.report(full, "--max-loss", "1", records=recs)
        self.assertEqual(rep2["categories"]["decisions"]["lost"], 0)

    def test_decision_overlap_parameter_direction(self):
        # 只保留原句約一半詞元：低門檻算保留，高門檻算損失。方向寫反兩者會同時翻轉而失敗。
        half = GOOD_MEMORY.replace(ABANDON, "決定放棄 lookbehind，因為不支援可變長度")
        _, loose, _ = self.report(half, "--decision-overlap", "0.1", "--max-loss", "1")
        _, strict, _ = self.report(half, "--decision-overlap", "0.99", "--max-loss", "1")
        self.assertEqual(loose["categories"]["decisions"]["lost"], 0)
        self.assertEqual(strict["categories"]["decisions"]["lost"], 1)

    def test_max_loss_parameter_direction(self):
        mem = GOOD_MEMORY.replace("，errno 名 ENOENT", "")  # 損失率 1/11 約 0.09
        c_low, _, _ = self.report(mem, "--max-loss", "0.05")
        c_high, _, _ = self.report(mem, "--max-loss", "0.2")
        self.assertEqual((c_low, c_high), (1, 0))

    def test_all_decisions_lost_fails_even_when_overall_loss_is_low(self):
        # 審查重現案例：總體損失率 1/3 < 0.4，但唯一一則決策（含原因）全丟
        recs = [{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text":
                 "UnicodeDecodeError 出現在 src/reader.py，因為 Windows 用 CRLF 讓正則失效，所以改用 splitlines"}]}},
                {"type": "user", "message": {"role": "user", "content": "Ran 2 tests\nOK"}}]
        mem = "- src/reader.py\n- UnicodeDecodeError\n- Ran 2 tests\nOK\n- 改用 splitlines 處理\n"
        code, rep, _ = self.report(mem, records=recs)
        self.assertEqual(rep["categories"]["decisions"]["loss_rate"], 1.0)
        self.assertLess(rep["information_loss_rate"], 0.4)
        self.assertEqual(code, 1)
        self.assertIn("decision-loss-over-threshold", self.codes(rep))
        self.assertNotIn("loss-over-threshold", self.codes(rep))
        # 門檻放寬到 1 就不再因此失敗；方向不能寫反
        code2, rep2, _ = self.report(mem, "--max-decision-loss", "1", records=recs)
        self.assertEqual(code2, 0, rep2["findings"])
        # 決策保留時通過
        code3, _, _ = self.report(mem + "- 因為 Windows 用 CRLF 讓正則失效，所以改用 splitlines\n", records=recs)
        self.assertEqual(code3, 0)

    def test_decision_threshold_skipped_when_no_decisions_exist(self):
        recs = [{"type": "user", "message": {"role": "user", "content": "ENOENT\nexit code 1\nRan 3 tests"}}]
        code, rep, _ = self.report("ENOENT exit code 1 Ran 3 tests\n", records=recs)
        self.assertEqual(code, 0, rep["findings"])
        self.assertIsNone(rep["categories"]["decisions"]["loss_rate"])

    def test_memory_line_without_reason_marker_cannot_retain_decision(self):
        # 詞元幾乎都在，但該行沒有任何原因／決定標記：不算保留
        recs = [{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text":
                 "因為 Windows 用 CRLF 讓正則失效，所以改用 splitlines"}]}},
                {"type": "user", "message": {"role": "user", "content": "ENOENT\nexit code 1\nRan 3 tests"}}]
        base = "ENOENT exit code 1 Ran 3 tests\n"
        _, rep, _ = self.report(base + "Windows CRLF 正則失效 splitlines\n", "--max-loss", "1", records=recs)
        self.assertEqual(rep["categories"]["decisions"]["lost"], 1)
        _, rep2, _ = self.report(base + "Windows CRLF 正則失效，改用 splitlines\n", "--max-loss", "1", records=recs)
        self.assertEqual(rep2["categories"]["decisions"]["lost"], 0)

    def test_tool_output_sentences_are_not_decisions(self):
        _, rep, _ = self.report(GOOD_MEMORY)
        self.assertEqual(rep["categories"]["decisions"]["total"], 2)  # tool_result 內的 because 沒被算進去

    def test_category_without_facts_is_null_not_zero(self):
        recs = [{"type": "user", "message": {"role": "user", "content": "Ran 3 tests\nOK\nexit code 0\nENOENT"}}]
        _, rep, _ = self.report("Ran 3 tests\nOK\nexit code 0\nENOENT\n", records=recs)
        self.assertIsNone(rep["categories"]["paths"]["loss_rate"])
        self.assertIsNone(rep["categories"]["decisions"]["loss_rate"])
        self.assertEqual(rep["categories"]["test_conclusions"]["loss_rate"], 0.0)


class LeakChecks(Base):
    def test_secret_in_memory_fails(self):
        for secret in ("sk-" + "a" * 30, "ghp_" + "b" * 30, "AKIA" + "C" * 16, "Bearer " + "d" * 30,
                       "api_key = " + "e" * 12):
            code, rep, _ = self.report(GOOD_MEMORY + "\n- 備註：" + secret + "\n")
            self.assertEqual(code, 1, secret)
            self.assertIn("leak-secret", self.codes(rep), secret)

    def test_secret_value_never_echoed_in_report(self):
        secret = "sk-" + "z" * 30
        code, rep, _ = self.report(GOOD_MEMORY + "\n- 備註：" + secret + "\n")
        self.assertNotIn(secret, json.dumps(rep, ensure_ascii=False))

    def test_real_home_path_in_memory_fails_but_tilde_and_placeholder_pass(self):
        code, rep, _ = self.report(GOOD_MEMORY + "\n- 見 " + FAKE_HOME + "\\notes.txt\n")
        self.assertEqual(code, 1)
        self.assertIn("leak-home-path", self.codes(rep))
        for ok in ("~/proj/x", "%USERPROFILE%\\proj\\x", "C:\\Users\\<username>\\proj\\x", "/home/user/proj"):
            code, rep, _ = self.report(GOOD_MEMORY + "\n- 見 " + ok + "\n", "--max-unsupported", "9")
            self.assertNotIn("leak-home-path", self.codes(rep), ok)

    def test_raw_home_path_in_memory_still_matches_fact_but_leak_fails(self):
        mem = GOOD_MEMORY.replace("~/proj/src/parser.py", FAKE_HOME + "\\src\\parser.py")
        code, rep, _ = self.report(mem)
        self.assertEqual(rep["categories"]["paths"]["lost"], 0)
        self.assertEqual(code, 1)
        self.assertIn("leak-home-path", self.codes(rep))

    def test_filler_lines_fail_and_limit_is_configurable(self):
        mem = "好的，沒問題！\n" + GOOD_MEMORY + "\n- Sure, here is the summary\n"
        code, rep, _ = self.report(mem)
        self.assertEqual(code, 1)
        self.assertIn("filler", self.codes(rep))
        code2, rep2, _ = self.report(mem, "--max-filler", "2")
        self.assertEqual(code2, 0, rep2["findings"])

    def test_single_filler_line_fails_at_default_limit(self):
        code, rep, _ = self.report(GOOD_MEMORY + "\n- 當然，以上就是結論\n")
        self.assertEqual(code, 1)
        self.assertIn("filler", self.codes(rep))
        code0, rep0, _ = self.report(GOOD_MEMORY + "\n- 當然，以上就是結論\n", "--max-filler", "1")
        self.assertEqual(code0, 0, rep0["findings"])

    def test_real_home_account_in_lost_decision_is_not_echoed(self):
        sent = "決定改放到 " + FAKE_HOME + "\\cache 底下，因為系統暫存區會被清掉。"
        recs = transcript_records(extra_text=sent)
        code, rep, _ = self.report(GOOD_MEMORY, "--max-loss", "1", records=recs)
        self.assertEqual(rep["categories"]["decisions"]["lost"], 1)
        self.assertNotIn("alice", json.dumps(rep, ensure_ascii=False))

    def test_secret_inside_reported_filler_line_is_redacted(self):
        secret = "sk-" + "y" * 30
        code, rep, _ = self.report(GOOD_MEMORY + "\n好的，金鑰是 " + secret + "\n")
        self.assertEqual(code, 1)
        self.assertIn("filler", self.codes(rep))
        self.assertNotIn(secret, json.dumps(rep, ensure_ascii=False))

    def test_filler_prefix_of_longer_ascii_word_is_not_flagged(self):
        code, rep, _ = self.report(GOOD_MEMORY + "\n- greatest 值與此無關\n- surely 這個詞不在清單\n")
        self.assertNotIn("filler", self.codes(rep))

    def test_filler_word_inside_sentence_is_not_flagged(self):
        code, rep, _ = self.report(GOOD_MEMORY + "\n- 這個 sure-fire 做法與 greatest 值無關\n", "--max-unsupported", "0")
        self.assertNotIn("filler", self.codes(rep))

    def test_secret_in_transcript_sentence_excluded_from_facts_and_report(self):
        secret = "sk-" + "q" * 30
        recs = transcript_records(extra_text="決定改用新金鑰 " + secret + "，因為舊的外洩了。")
        code, rep, _ = self.report(GOOD_MEMORY, records=recs)
        self.assertEqual(rep["excluded_secret_facts"], 1)
        self.assertEqual(rep["categories"]["decisions"]["total"], 2)
        self.assertEqual(code, 0)
        self.assertNotIn(secret, json.dumps(rep, ensure_ascii=False))

    def test_secret_and_home_path_hidden_in_html_comment_still_fail(self):
        secret = "ghp_" + "k" * 30
        code, rep, _ = self.report(GOOD_MEMORY + "\n<!-- " + secret + " -->\n")
        self.assertEqual(code, 1)
        self.assertIn("leak-secret", self.codes(rep))
        code2, rep2, _ = self.report(GOOD_MEMORY + "\n<!-- 見 " + FAKE_HOME + "\\x.txt -->\n")
        self.assertEqual(code2, 1)
        self.assertIn("leak-home-path", self.codes(rep2))

    def test_url_with_users_segment_is_not_a_home_path_but_real_ones_are(self):
        for text in ("https://github.com/users/octo", "see github.com/home/octo/repo"):
            self.assertEqual(a.real_home_accounts(text), [], text)
        for text in ("/home/bob/x", "C:\\Users\\bob\\x", "(/Users/bob/x)", "/c/Users/bob/x"):
            self.assertEqual(a.real_home_accounts(text), ["bob"], text)
        code, rep, _ = self.report(GOOD_MEMORY + "\n- 參考 https://github.com/users/octo\n", "--max-unsupported", "5")
        self.assertNotIn("leak-home-path", self.codes(rep))

    def test_fail_not_compressed_flag_turns_warning_into_failure(self):
        recs = [{"type": "user", "message": {"role": "user", "content": "Ran 3 tests\nOK\nexit code 0\nENOENT\n"}}]
        mem = "Ran 3 tests\nOK\nexit code 0\nENOENT\n" + "備註" * 40
        code, rep, _ = self.report(mem, records=recs)
        self.assertEqual(code, 0)
        code2, rep2, _ = self.report(mem, "--fail-not-compressed", records=recs)
        self.assertEqual(code2, 1)
        self.assertEqual([f["severity"] for f in rep2["findings"] if f["code"] == "not-compressed"], ["FAIL"])

    def test_unsupported_error_code_fails(self):
        code, rep, _ = self.report(GOOD_MEMORY + "\n- 另見 EACCES 與 HTTP 503\n")
        self.assertEqual(code, 1)
        self.assertEqual(rep["unsupported"]["error_codes"], ["eacces", "http 503"])

    def test_verbatim_copy_warns_not_compressed(self):
        recs = [{"type": "user", "message": {"role": "user", "content": "Ran 3 tests\nOK\nexit code 0\nENOENT\n"}}]
        _, rep, _ = self.report("Ran 3 tests\nOK\nexit code 0\nENOENT\n" + "備註" * 40, records=recs)
        warn = [f for f in rep["findings"] if f["code"] == "not-compressed"]
        self.assertEqual([f["severity"] for f in warn], ["WARN"])
        self.assertGreaterEqual(rep["compression_ratio_chars"], 1.0)


class BadInputs(Base):
    def expect_exit2(self, transcript, memory, *flags):
        code, out, err = run("--transcript", transcript, "--memory", memory, *flags)
        self.assertEqual(code, 2, (out, err))
        self.assertNotIn("[PASS]", out)
        return err

    def test_missing_files(self):
        m = self.env.memory(GOOD_MEMORY)
        self.assertIn("無法讀取", self.expect_exit2(self.env.root / "nope.jsonl", m))
        self.assertIn("無法讀取", self.expect_exit2(self.env.transcript(), self.env.root / "nope.md"))

    def test_corrupt_jsonl_reports_line_number(self):
        raw = (json.dumps(transcript_records()[0]) + "\n{not json\n").encode("utf-8")
        err = self.expect_exit2(self.env.transcript(raw=raw), self.env.memory(GOOD_MEMORY))
        self.assertIn("第 2 行", err)

    def test_empty_whitespace_and_scalar_transcripts(self):
        m = self.env.memory(GOOD_MEMORY)
        for raw in (b"", b"\n  \n\n", b"42\n", b'"just a string"\n'):
            self.expect_exit2(self.env.transcript(raw=raw), m)

    def test_records_without_any_text(self):
        self.expect_exit2(self.env.transcript(raw=b'{"uuid":"x","timestamp":"t"}\n'), self.env.memory(GOOD_MEMORY))

    def test_non_utf8_inputs(self):
        m = self.env.memory(GOOD_MEMORY)
        bad = "中文".encode("cp950")
        self.assertIn("UTF-8", self.expect_exit2(self.env.transcript(raw=b'{"a":"' + bad + b'"}\n'), m))
        mm = self.env.root / "bad.md"
        mm.write_bytes(bad)
        self.assertIn("UTF-8", self.expect_exit2(self.env.transcript(), mm))

    def test_transcript_with_no_extractable_facts_is_not_a_pass(self):
        recs = [{"type": "user", "message": {"role": "user", "content": "你好，今天天氣不錯"}}]
        t = self.env.transcript(recs)
        for memory_text in (GOOD_MEMORY, ""):
            err = self.expect_exit2(t, self.env.memory(memory_text))
            self.assertIn("樣本不足", err)

    def test_min_facts_zero_rejected_and_zero_facts_never_divides_by_zero(self):
        t = self.env.transcript([{"message": {"content": "hello there"}}])
        m = self.env.memory("hello there\n")
        code, out, err = run("--transcript", t, "--memory", m, "--min-facts", "0")
        self.assertEqual(code, 2, err)
        self.assertNotIn("Traceback", err)
        self.assertIn("至少要 1", err)  # 參數層就擋下，不是靠後面的保險
        # 直接呼叫 audit() 繞過參數檢查也要回 InputError，而不是 ZeroDivisionError
        with self.assertRaises(a.InputError):
            a.audit([("text", "hello there")], "hello there", max_loss=0.4, decision_overlap=0.5,
                    max_filler=0, max_unsupported=0, min_facts=0)
        code2, _, err2 = run("--transcript", t, "--memory", m)
        self.assertEqual(code2, 2, err2)

    def test_min_facts_is_configurable(self):
        recs = [{"type": "user", "message": {"role": "user", "content": "exit code 2"}}]
        t, m = self.env.transcript(recs), self.env.memory("exit code 2\n")
        self.expect_exit2(t, m)
        code, out, err = run("--transcript", t, "--memory", m, "--min-facts", "1")
        self.assertEqual(code, 0, err)

    def test_bad_thresholds_rejected(self):
        t, m = self.env.transcript(), self.env.memory(GOOD_MEMORY)
        for flags in (("--max-loss", "1.5"), ("--max-loss", "-0.1"), ("--max-loss", "abc"),
                      ("--max-filler", "-1"), ("--decision-overlap", "2")):
            self.expect_exit2(t, m, *flags)

    def test_output_path_unwritable(self):
        t, m = self.env.transcript(), self.env.memory(GOOD_MEMORY)
        self.expect_exit2(t, m, "--output", self.env.root / "no-such-dir" / "r.md")


class ExtractionUnits(unittest.TestCase):
    def test_paths_ignore_urls_and_normalize(self):
        got = a.extract_paths("see https://example.com/a/b.html and ./src/x.py and src\\y.py and " + FAKE_HOME + "\\z.py")
        self.assertEqual(got, {"src/x.py", "src/y.py", "~/proj/z.py"})

    def test_error_code_normalization(self):
        got = a.extract_errors("KeyError ENOENT 0xC0000005 HTTP 404 exit status 3 returncode=3 WinError 5 TS2304 CVE-2024-12345")
        self.assertEqual(got, {"keyerror", "enoent", "0xc0000005", "http 404", "exit code 3", "winerror 5", "ts2304", "cve-2024-12345"})

    def test_plain_error_word_not_an_error_code(self):
        self.assertEqual(a.extract_errors("Error: something. error handling. Exception"), set())

    def test_test_conclusions(self):
        got = a.extract_tests("Ran 5 tests\n3 passed, 1 failed\nFAILED (errors=1)\nOK\nrandom OK text\n12 個測試通過")
        self.assertEqual(got, {"ran 5 tests", "3 passed", "1 failed", "failed (errors=1)", "ok", "12 個測試通過"})

    def test_walk_skips_metadata_and_tags_tool_blocks(self):
        segs = []
        a._walk({"uuid": "U", "cwd": "X", "message": {"content": [
            {"type": "text", "text": "hello"}, {"type": "tool_result", "content": "out"}]}}, "text", segs)
        self.assertEqual(segs, [("text", "hello"), ("tool", "out")])


TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "cross-session-memory-curation-spec.md"


def template_block(info):
    import re
    text = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"```" + re.escape(info) + r"\n(.*?)\n```", text, re.S)
    assert m, f"範本缺少 ```{info} 區塊"
    return m.group(1) + "\n"


class TemplateExamplesHonorOwnStandards(Base):
    """templates/cross-session-memory-curation-spec.md 的範例必須通過它自己規定的稽核與清單腳本。"""

    def run_sample(self, memory_text, *flags):
        t = self.env.root / "sample.jsonl"
        t.write_text(template_block("jsonl sample-transcript"), encoding="utf-8", newline="\n")
        m = self.env.memory(memory_text)
        code, out, err = run("--transcript", t, "--memory", m, "--format", "json", *flags)
        return code, json.loads(out) if out.strip() else None, err

    def test_sample_memory_passes_audit_with_defaults(self):
        code, rep, err = self.run_sample(template_block("markdown sample-memory"))
        self.assertEqual(code, 0, rep and rep["findings"])
        self.assertEqual(rep["information_loss_rate"], 0.0)
        self.assertGreaterEqual(rep["facts_total"], 8)

    def test_sample_memory_fails_when_a_fact_is_corrupted(self):
        good = template_block("markdown sample-memory")
        for old, new in (("Ran 5 tests", "Ran 4 tests"), ("src/config/loader.py 失敗", "src/config/load.py 失敗"),
                         ("因為捕捉 FileNotFoundError 會連真正的權限問題一起吞掉", "")):
            self.assertIn(old, good)
            code, rep, _ = self.run_sample(good.replace(old, new), "--max-loss", "0.05")  # 1/12 約 0.083
            self.assertEqual(code, 1, old)
            self.assertTrue(rep["information_loss_rate"] > 0.05 or "unsupported-fact" in self.codes(rep), old)

    def test_prompt_block_exists_with_four_required_headings(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("## 背景事實 / ## 根因分析 / ## 踩坑結論 / ## 待辦事項", text)
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("\n---\n", text[4:])

    def run_lister(self, files, *flags):
        script = self.env.root / "list_expired_memory.py"
        script.write_text(template_block("python list-expired"), encoding="utf-8", newline="\n")
        self._n = getattr(self, "_n", 0) + 1
        mem = self.env.root / f"mem{self._n}"
        mem.mkdir()
        for name, text in files.items():
            (mem / name).write_text(text, encoding="utf-8", newline="\n")
        r = subprocess.run([sys.executable, str(script), str(mem), *map(str, flags)], capture_output=True)
        return r.returncode, r.stdout.decode("utf-8"), r.stderr.decode("utf-8")

    def entry(self, status="active", expires="2027-01-31"):
        return f"---\nname: x\ndescription: d\ntype: project\nstatus: {status}\nexpires: {expires}\n---\n\nbody\n"

    def test_lister_flags_expired_active_entry(self):
        files = {"project_a.md": self.entry(), "project_b.md": self.entry(expires="2026-01-01")}
        code, out, _ = self.run_lister(files, "--today", "2026-11-02")
        self.assertEqual(code, 1)
        self.assertIn("project_b.md", out)
        self.assertNotIn("project_a.md", out)
        code2, _, _ = self.run_lister({"project_a.md": self.entry()}, "--today", "2026-11-02")
        self.assertEqual(code2, 0)

    def test_lister_ignores_expired_status_but_flags_damaged_entries(self):
        files = {"p1.md": self.entry(status="expired", expires="2020-01-01"),
                 "p2.md": "沒有 frontmatter\n",
                 "p3.md": self.entry(expires="soon"),
                 "p4.md": self.entry(status="weird")}
        code, out, _ = self.run_lister(files, "--today", "2026-11-02")
        self.assertEqual(code, 1)
        self.assertNotIn("p1.md", out)
        for n in ("p2.md", "p3.md", "p4.md"):
            self.assertIn(n, out)

    def test_lister_no_files_or_bad_args_is_exit_2_not_pass(self):
        self.assertEqual(self.run_lister({}, "--today", "2026-11-02")[0], 2)
        self.assertEqual(self.run_lister({"MEMORY.md": "# index\n"}, "--today", "2026-11-02")[0], 2)
        self.assertEqual(self.run_lister({"p.md": self.entry()}, "--today", "11/02/2026")[0], 2)
        missing = subprocess.run([sys.executable, str(self.env.root / "list_expired_memory.py"), str(self.env.root / "nope")],
                                 capture_output=True)
        self.assertEqual(missing.returncode, 2)

    def test_lister_single_damaged_entry_alone_is_exit_1(self):
        for files in ({"p.md": "沒有 frontmatter\n"}, {"p.md": self.entry(expires="soon")}, {"p.md": self.entry(status="weird")}):
            self.assertEqual(self.run_lister(files, "--today", "2026-11-02")[0], 1, files)

    def test_lister_boundary_expires_today_is_still_valid(self):
        code, _, _ = self.run_lister({"p.md": self.entry(expires="2026-11-02")}, "--today", "2026-11-02")
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
