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
