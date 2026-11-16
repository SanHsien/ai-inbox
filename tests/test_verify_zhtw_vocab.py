#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
單元測試：test_verify_zhtw_vocab.py
驗證台灣繁體中文技術詞彙轉換、OpenCC 二次退化修補、程式碼區塊保護與嚴格冪等性。
"""

import os
import sys
import tempfile
import unittest
import time
import io
from contextlib import redirect_stdout
from unittest.mock import patch

from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

import verify_zhtw_vocab as vocab

from verify_zhtw_vocab import (
    apply_zhtw_vocab,
    main,
    scan_degraded_vocab,
    verify_idempotence,
)


class TestVerifyZhtwVocab(unittest.TestCase):
    def test_context_exceptions_require_the_exact_neighbours(self):
        cases = [
            ("安裝的軟件數量與軟件數據、軟件數十款", "安裝的軟體數量與軟體數據、軟體數十款", ["軟件"] * 3),
            ("這段視頻率先曝光", "這段影片率先曝光", ["視頻"]),
            ("家電視頻教學、充電視頻、閃電視頻", "家電影片教學、充電影片、閃電影片", ["視頻"] * 3),
            ("服務器材質與服務器材料", "伺服器材質與伺服器材料", ["服務器"] * 2),
            ("視頻道、視頻譜、服務器材質", "影片道、影片譜、伺服器材質", ["視頻", "視頻", "服務器"]),
            ("輕鬆軟件安裝、放鬆軟件", "輕鬆軟體安裝、放鬆軟體", ["軟件"] * 2),
            ("柔軟件、鬆軟件", "柔軟體、鬆軟體", ["軟件"] * 2),
        ]
        for raw, expected, terms in cases:
            for skip in [True, False]:
                with self.subTest(raw=raw, skip=skip):
                    self.assertEqual([h["term"] for h in scan_degraded_vocab(raw, skip_code=skip)], terms)
                    self.assertEqual(apply_zhtw_vocab(raw, skip_code=skip), expected)
                    self.assertEqual(apply_zhtw_vocab(expected, skip_code=skip), expected)
        for left in "電衛監檢透收巡探注審":
            for right in "道率譜段寬繁":
                self.assert_protected(left + "視頻" + right)
        for raw in ["柔軟件數", "鬆軟件數", "堅硬件",
                    "售後服務器材", "提供服務器材"]:
            self.assert_protected(raw)

    def test_frequent_tv_reports_and_visit_frequencies_are_preserved(self):
        for raw in ["電視頻繁報導、監視頻繁", "巡視頻率、探視頻率、注視頻率、審視頻率"]:
            for skip in [True, False]:
                with self.subTest(raw=raw, skip=skip):
                    self.assertEqual(apply_zhtw_vocab(raw, skip_code=skip), raw)
                    self.assertEqual(scan_degraded_vocab(raw, skip_code=skip), [])

    def test_context_exception_limitations_are_documented(self):
        self.assertIn("兩側字集仍可能誤排除罕見組合", vocab.__doc__)
        for raw in ["接收視頻寬高", "回收視頻道具"]:
            self.assertIn(raw, vocab.__doc__)

    def test_bare_url_typographic_boundaries(self):
        for delimiter in "“”‘’〈〉《》—…":
            raw = "https://a.org/x" + delimiter + "視頻很好而且軟件也不錯"
            with self.subTest(delimiter=delimiter):
                self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], ["視頻", "軟件"])
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=True),
                                 "https://a.org/x" + delimiter + "影片很好而且軟體也不錯")
        for raw in ["“https://a.org/x”視頻很好而且軟件也不錯", "https://a.org/x——視頻很好"]:
            self.assertTrue(scan_degraded_vocab(raw))

    def test_www_requires_a_word_boundary(self):
        for prefix in ["a", "1", "_"]:
            raw = prefix + "www.視頻軟件"
            with self.subTest(prefix=prefix):
                self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], ["視頻", "軟件"])
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), prefix + "www.影片軟體")
        for prefix in ["", " ", "(", "\n", "中", "請見"]:
            self.assert_protected(prefix + "www.視頻軟件")
        self.assert_protected("請見www.example.org/數據庫")
        hints = []
        vocab._protected_parts("請見www.example.org/數據庫 awww.視頻軟件", hints)
        self.assertEqual(hints, [(1, "www.example.org/數據庫")])

    def test_reference_period_in_prose_is_not_a_path(self):
        for suffix in ["v2.0很重要", "v2.0", "v2.123"]:
            raw = "[備註]: 視頻教學" + suffix
            with self.subTest(suffix=suffix):
                self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], ["視頻"])
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), "[備註]: 影片教學" + suffix)
        for destination in ["視頻.md", "視頻.mp4", "視頻.example.org", "docs/視頻.md"]:
            self.assert_protected("[v]: " + destination)

    def test_review_exit_code_is_documented(self):
        self.assertIn("[REVIEW]", vocab.__doc__)
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as result:
            main(["--help"])
        self.assertEqual(result.exception.code, 0)
        self.assertIn("[REVIEW]", output.getvalue())
        self.assertIn("不影響結束碼", output.getvalue())

    def assert_protected(self, raw):
        self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), raw)
        self.assertEqual(scan_degraded_vocab(raw), [])

    def test_quote_protection_is_bounded(self):
        cases = [
            ("他說「視頻很好\n\n中間段落 軟件\n\n結尾」之後 硬件", ["視頻", "軟件", "硬件"]),
            ("| 「視頻 | 軟件 |\n| 硬件 | 服務器」 |", ["視頻", "軟件", "硬件", "服務器"]),
            ("「a『b」 視頻\n\n段落 軟件\n\n』 x 」", ["視頻", "軟件"]),
            ("「" + "a" * 200 + "視頻」", ["視頻"]),
            ("「a『b」 視頻』", ["視頻"]),
            ("「視頻\n  \n軟件」", ["視頻", "軟件"]),
        ]
        for raw, terms in cases:
            with self.subTest(raw=raw):
                self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], terms)
                self.assertNotEqual(apply_zhtw_vocab(raw, skip_code=True), raw)
        self.assert_protected("「" + "a" * 196 + "視頻」")

    def test_unclosed_protection_has_bounded_runtime(self):
        for token in ["「", "]("]:
            with self.subTest(token=token):
                raw = (token + " 視頻\n") * 5000
                started = time.perf_counter()
                self.assertEqual(len(scan_degraded_vocab(raw)), 5000)
                self.assertLess(time.perf_counter() - started, 3.0)

    def test_url_stops_before_chinese_prose(self):
        for raw, expected in [
            ("（見 https://a.org/x）這個視頻很好看而且軟件也不錯 硬件", ["視頻", "軟件", "硬件"]),
            ("(https://a.org/x)視頻教學與軟件", ["視頻", "軟件"]),
            ("https://a.org/x：視頻", ["視頻"]),
            ("https://a.org/x_(a))視頻", ["視頻"]),
        ]:
            with self.subTest(raw=raw):
                self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], expected)
                self.assertEqual(scan_degraded_vocab(apply_zhtw_vocab(raw, skip_code=True)), [])

    def test_url_unmatched_parenthesis_ends_protection(self):
        # An ASCII probe makes the ')' boundary observable independently of CJK.
        with patch.object(vocab, "ALL_RULES", (("video", "film", "probe"),)):
            raw = "https://a.org/x_(a))video"
            self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], ["video"])
            self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), "https://a.org/x_(a))film")

    def test_context_exceptions_preserve_real_words(self):
        raw = "電視頻道與衛視頻道、電視頻率；售後服務器材 柔軟件數 堅硬件 監視頻率 提供服務器材 鬆軟件數"
        for skip in [True, False]:
            with self.subTest(skip=skip):
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=skip), raw)
                self.assertEqual(scan_degraded_vocab(raw, skip_code=skip), [])
        self.assertEqual([h["term"] for h in scan_degraded_vocab(raw + " 視頻 軟件 硬件 服務器")],
                         ["視頻", "軟件", "硬件", "服務器"])

    def test_link_destinations_exclude_titles_and_newlines(self):
        raw = '[x](docs/視頻.md "軟件") 硬件\n[x](docs/視頻.md\n軟件)'
        self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)],
                         ["軟件", "硬件", "視頻", "軟件"])
        self.assertEqual(apply_zhtw_vocab(raw, skip_code=True),
                         '[x](docs/視頻.md "軟體") 硬體\n[x](docs/影片.md\n軟體)')
        self.assertEqual([h["term"] for h in scan_degraded_vocab('[x](docs/視頻.md)軟件')], ["軟件"])

    def test_reference_destinations_are_protected(self):
        raw = '[v]: docs/視頻.md "軟件"\n  [v2]: <docs/服務器.md> "硬件"\n視頻'
        self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], ["軟件", "硬件", "視頻"])
        self.assertEqual(apply_zhtw_vocab(raw, skip_code=True),
                         '[v]: docs/視頻.md "軟體"\n  [v2]: <docs/服務器.md> "硬體"\n影片')

    def test_scanner_sorts_rules_even_if_input_order_is_short_first(self):
        rules = (("視頻", "影片", "short"), ("短視頻", "短影音", "long"))
        with patch.object(vocab, "ALL_RULES", rules):
            self.assertEqual([(h["term"], h["replacement"]) for h in scan_degraded_vocab("短視頻")],
                             [("短視頻", "短影音")])

    def test_assessment_section_six_counterexamples(self):
        # Every row of the section 6 counterexample probe, including the explicit
        # fallback: unquoted product names still have no entity protection.
        cases = [
            ("「數據庫」是引用原話。", "「數據庫」是引用原話。"),
            ("[來源](https://example.org/數據庫)",
             "[來源](https://example.org/數據庫)"),
            ("產品名：數據庫工具。", "產品名：資料庫工具。"),
            ("這個服務器支持中文。", "這個伺服器支持中文。"),
            ("渲染時會打印日誌。", "渲染時會輸出日誌。"),
            ("`數據庫`\n```text\n數據庫\n```", "`數據庫`\n```text\n數據庫\n```"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), expected)
                self.assertEqual(scan_degraded_vocab(expected), [])

    def test_chinese_quotes_protect_original_words(self):
        for raw in ["產品名「服務器助手」", "『數據庫』", "「外『數據庫』內」",
                    "「數據庫\n源代碼」", "「數據庫與 `代碼`」"]:
            with self.subTest(raw=raw):
                self.assert_protected(raw)
        self.assertEqual(
            apply_zhtw_vocab("「數據庫」及數據庫", skip_code=True),
            "「數據庫」及資料庫",
        )

    def test_markdown_destinations_protect_relative_nested_and_escaped_paths(self):
        for raw in ["[來源](docs/數據庫.md)",
                    "[來源](https://example.org/數據庫_(軟件))",
                    r"![圖](docs/數據庫\(軟件\).png)"]:
            with self.subTest(raw=raw):
                self.assert_protected(raw)
        self.assertEqual(
            apply_zhtw_vocab("[數據庫](docs/數據庫.md)與數據庫", skip_code=True),
            "[資料庫](docs/數據庫.md)與資料庫",
        )

    def test_bare_urls_protect_path_query_fragment(self):
        for raw in ["https://example.org/path?q=video#part", "<https://example.org/path>",
                    "https://example.org/數據庫?軟件=硬件#視頻",
                    "<https://example.org/數據庫>", "www.example.org/數據庫",
                    "見 https://zh.wikipedia.org/wiki/數據庫 一文",
                    "<https://zh.wikipedia.org/wiki/數據庫>",
                    "<https://a.org/視頻：軟件>",
                    "https://a.org/s?q=視頻&x=1",
                    "www.example.org/path", "https://a.org/x_(nested)"]:
            self.assert_protected(raw)
        self.assertEqual(apply_zhtw_vocab("https://example.org/數據庫。數據庫", skip_code=True),
                         "https://example.org/數據庫。資料庫")
        self.assertEqual(apply_zhtw_vocab("https:// 數據庫 www. 數據庫", skip_code=True),
                         "https:// 資料庫 www. 資料庫")

    def test_ambiguous_bare_url_is_preserved_with_cli_hint(self):
        raw = "https://a.org/x視頻教學"
        self.assert_protected(raw)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "url.md"
            p.write_text(raw, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--fix", str(p), "--check", str(p)]), 0)
            self.assertEqual(p.read_text(encoding="utf-8"), raw)
            self.assertEqual(output.getvalue().count("[REVIEW]"), 1)
            self.assertIn("人工確認", output.getvalue())

    def test_footnotes_and_plain_labels_are_prose(self):
        for raw, expected in [
            ("正文[^1]\n\n[^1]: 視頻教學很重要而且軟件也是", ["視頻", "軟件"]),
            ("[^n]: 這個服務器的硬件 很舊", ["服務器", "硬件"]),
            ("[^n]: docs/視頻.md", ["視頻"]),
            ("[備註]: 視頻教學很重要", ["視頻"]),
        ]:
            with self.subTest(raw=raw):
                self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], expected)
                self.assertNotEqual(apply_zhtw_vocab(raw, skip_code=True), raw)
        for destination in ["docs/視頻", "視頻.md", "#視頻", "<視頻>"]:
            self.assert_protected("[v]: " + destination)

    def test_escaped_pipes_do_not_end_quote_protection(self):
        self.assert_protected(r"他說「a \| b 視頻」")
        self.assert_protected(r"他說「a \\\| b 視頻」")
        for raw in ["他說「a | b 視頻」", r"他說「a \\| b 視頻」"]:
            self.assertEqual([h["term"] for h in scan_degraded_vocab(raw)], ["視頻"])

    def test_candidate_rules_have_positive_and_protected_negative_cases(self):
        for raw, expected in [("啟動服務器", "啟動伺服器"),
                              ("安裝軟件", "安裝軟體"),
                              ("更新硬件", "更新硬體"),
                              ("短視頻教學", "短影音教學"),
                              ("視頻教學", "影片教學")]:
            with self.subTest(raw=raw):
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), expected)
                self.assertTrue(scan_degraded_vocab(raw))
                self.assert_protected(f"「{raw}」 `短視頻` [x](https://example.org/{raw})")
                self.assertEqual(apply_zhtw_vocab(expected, skip_code=True), expected)

    def test_long_video_rule_wins_in_transform_and_findings(self):
        raw = "短視頻教學與視頻教學"
        self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), "短影音教學與影片教學")
        self.assertEqual(
            [(h["term"], h["replacement"]) for h in scan_degraded_vocab("短視頻教學")],
            [("短視頻", "短影音")],
        )

    def test_existing_mappings_and_semantic_exclusions(self):
        self.assertEqual(
            apply_zhtw_vocab("源代碼 默認值 渲染時會打印", skip_code=True),
            "原始碼 預設值 渲染時會輸出",
        )
        for raw in ["支持 UTF-8 編碼、支持中文、支持開源社群、支持候選人",
                    "完成,請重試；4,800 元；a,b；Hello, world",
                    "最終成品：[產品名稱]；templates/ 的 [產品名稱]",
                    "孤立的 turn0search0；教學中的 `turn0search0`"]:
            with self.subTest(raw=raw):
                self.assert_protected(raw)

    def test_protected_spans_do_not_join_words_or_lose_line_numbers(self):
        raw = "源「原話」代碼\n「數據庫」與數據庫\n```text\n數據庫\n```\n默認值"
        self.assertEqual(
            [(h["line"], h["term"]) for h in scan_degraded_vocab(raw)],
            [(2, "數據庫"), (6, "默認值")],
        )

    def test_repairs_opencc_second_pass_degradations(self) -> None:
        degraded = (
            "這個連線埠設定隻影響本地服務。請先選一個類別型，確認型別別與"
            "字面量（Literal）（Literal），看看發生瞭什麼事，最後摁下確認鍵。"
        )
        expected = (
            "這個連接埠設定只影響本地服務。請先選一個類型，確認型別與"
            "字面量（Literal），看看發生了什麼事，最後按下確認鍵。"
        )
        fixed = apply_zhtw_vocab(degraded)
        self.assertEqual(fixed, expected)
        # 驗證二次執行完全冪等
        self.assertEqual(apply_zhtw_vocab(fixed), expected)

    def test_repairs_context_specific_phrases(self) -> None:
        raw = (
            "支援其他寫程式的 WAV 音訊，或自己寫程式並下載；"
            "渲染時會打印結果並打印路徑，詳見官方參考檔案。"
        )
        expected = (
            "支援其他編碼的 WAV 音訊，或自己編碼並下載；"
            "渲染時會輸出結果並輸出路徑，詳見官方參考文件。"
        )
        self.assertEqual(apply_zhtw_vocab(raw), expected)

    def test_skip_code_preserves_inline_backticks_and_fenced_blocks(self) -> None:
        md = (
            "正文誤寫連線埠與摁下應被抓出，但表格反例 `連線埠` 與 `摁下` 應被保護。\n"
            "```text\n"
            "代码块內的 連線埠 與 型別別 不應被更動\n"
            "```\n"
        )
        hits = scan_degraded_vocab(md, skip_code=True)
        self.assertEqual([h["term"] for h in hits], ["連線埠", "摁下"])

        fixed = apply_zhtw_vocab(md, skip_code=True)
        self.assertIn("正文誤寫連接埠與按下應被抓出，但表格反例 `連線埠` 與 `摁下` 應被保護。", fixed)
        self.assertIn("代码块內的 連線埠 與 型別別 不應被更動", fixed)
        self.assertEqual(scan_degraded_vocab(fixed, skip_code=True), [])

    def test_inline_runs_pair_by_exact_length(self):
        for raw in ["`` `連線埠` ``", "``` a `型別別` b ```", "``連線埠`仍在程式碼``"]:
            with self.subTest(raw=raw):
                self.assertEqual(apply_zhtw_vocab(raw, skip_code=True), raw)
                self.assertEqual(scan_degraded_vocab(raw), [])
        self.assertTrue(scan_degraded_vocab("`連線埠``"))
        self.assertEqual(apply_zhtw_vocab("`連線埠``", skip_code=True), "`連接埠``")

    def test_overlapping_and_consecutive_degradations_reach_fixed_point(self):
        for raw, expected in [("型別別別", "型別"), ("型別別別別別型別別別", "型別型別"),
                              ("字面量（Literal）（Literal）（Literal）", "字面量（Literal）"),
                              ("命令行界面", "命令列介面")]:
            with self.subTest(raw=raw):
                self.assertEqual(apply_zhtw_vocab(raw), expected)
                self.assertTrue(verify_idempotence([raw])[0])

    def test_cli_rejects_missing_and_zero_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty.md"
            empty.write_text("", encoding="utf-8")
            for mode in ["--check", "--fix"]:
                for paths in [[], [str(Path(tmp) / "missing.md")], [tmp], [str(empty)]]:
                    with self.subTest(mode=mode, paths=paths):
                        self.assertEqual(main([mode, *paths]), 2)
            valid = Path(tmp) / "valid.md"
            valid.write_text("連線埠", encoding="utf-8")
            for mode in ["--check", "--fix"]:
                self.assertEqual(main([mode, str(valid), str(Path(tmp) / "missing.md")]), 2)
            self.assertEqual(valid.read_text(encoding="utf-8"), "連線埠")
            self.assertEqual(main([]), 2)

    def test_cli_rejects_invalid_encoding_before_fixing_other_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.md"
            bad = Path(tmp) / "bad.md"
            good.write_text("連線埠", encoding="utf-8")
            bad.write_bytes(b"\xff")
            self.assertEqual(main(["--fix", str(good), str(bad)]), 2)
            self.assertEqual(good.read_text(encoding="utf-8"), "連線埠")

    def test_paste_and_misconverted_number_rules(self):
        # T-20261107-06：來源是 doggy8088/answer-me-with-html README.zh-TW.md 的殘留詞。
        cases = {
            "把提示詞粘貼給你的 Agent": "把提示詞貼上給你的 Agent",
            "複製粘貼": "複製貼上",
            "每次都得到同樣的數位": "每次都得到同樣的數字",
            "同樣的數位。": "同樣的數字。",
            "面板標題：關鍵數位": "面板標題：關鍵數字",
            "關鍵數位（MSL、ISN）": "關鍵數字（MSL、ISN）",
        }
        for src, expected in cases.items():
            with self.subTest(src=src):
                self.assertEqual(vocab.apply_zhtw_vocab(src, skip_code=True), expected)
                self.assertEqual(vocab.apply_zhtw_vocab(expected, skip_code=True), expected)
                self.assertTrue(vocab.scan_degraded_vocab(src))
                self.assertEqual(vocab.scan_degraded_vocab(expected), [])

    def test_digital_compounds_are_not_rewritten(self):
        # 「數位」是台灣對 digital 的正確用詞：整詞與 digital 複合詞一律不動。
        preserved = (
            "數位轉型", "數位簽章", "數位相機", "數位化", "數位",
            "公司推動數位轉型", "用數位簽章驗證",
            "關鍵數位轉型專案", "關鍵數位基礎建設", "關鍵數位技術",
            "同樣的數位相機", "同樣的數位簽章", "同樣的數位轉型路徑",
        )
        for text in preserved:
            with self.subTest(text=text):
                self.assertEqual(vocab.apply_zhtw_vocab(text, skip_code=True), text)
                self.assertEqual(vocab.apply_zhtw_vocab(text, skip_code=False), text)
                self.assertEqual(vocab.scan_degraded_vocab(text), [])

    def test_new_rules_skip_code_quotes_and_backticks(self):
        text = (
            "行內 `粘貼` 與 `關鍵數位` 不動；「同樣的數位」是引述也不動。\n"
            "```text\n粘貼 同樣的數位 關鍵數位\n```\n"
            "內文的粘貼要改。\n"
        )
        fixed = vocab.apply_zhtw_vocab(text, skip_code=True)
        self.assertIn("`粘貼`", fixed)
        self.assertIn("`關鍵數位`", fixed)
        self.assertIn("「同樣的數位」", fixed)
        self.assertIn("粘貼 同樣的數位 關鍵數位", fixed)
        self.assertIn("內文的貼上要改。", fixed)
        hits = vocab.scan_degraded_vocab(text, skip_code=True)
        self.assertEqual([(h["line"], h["term"]) for h in hits], [(5, "粘貼")])
        self.assertEqual(vocab.apply_zhtw_vocab(fixed, skip_code=True), fixed)

    def test_fix_preserves_line_endings(self):
        # --fix 不可改動換行：LF 檔維持 LF，CRLF 檔維持 CRLF（Windows 文字模式會全寫成 CRLF）。
        with tempfile.TemporaryDirectory() as tmp:
            for name, eol in (("lf.md", b"\n"), ("crlf.md", b"\r\n")):
                path = Path(tmp) / name
                path.write_bytes("第一行粘貼".encode("utf-8") + eol + "第二行".encode("utf-8") + eol)
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(vocab.main(["--fix", str(path)]), 0)
                self.assertEqual(
                    path.read_bytes(),
                    "第一行貼上".encode("utf-8") + eol + "第二行".encode("utf-8") + eol,
                )

    def test_all_rules_are_strictly_idempotent(self) -> None:
        ok, failures = verify_idempotence([
            "預設值與環境變數的連接埠設定只影響命令列介面輸出，詳見參考文件。",
        ])
        self.assertTrue(ok, failures)

    def test_cli_check_and_fix_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.md"
            p.write_text("請檢查連線埠並摁下按鈕。\n", encoding="utf-8")
            self.assertEqual(main(["--check", str(p)]), 1)
            self.assertEqual(main(["--fix", str(p)]), 0)
            self.assertEqual(main(["--check", str(p)]), 0)
            self.assertEqual(p.read_text(encoding="utf-8"), "請檢查連接埠並按下按鈕。\n")


if __name__ == "__main__":
    unittest.main()
