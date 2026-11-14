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
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from verify_zhtw_vocab import (
    apply_zhtw_vocab,
    main,
    scan_degraded_vocab,
    verify_idempotence,
)


class TestVerifyZhtwVocab(unittest.TestCase):
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
