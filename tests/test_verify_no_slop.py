"""
tests/test_verify_no_slop.py
測試 verify_no_slop.py：
1. 範例乾淨頁面 (assets/anti-slop-demo/index.html) 與 assets/ 全目錄必須 0 違規回報 Pass。
2. 故意包含罐頭特徵 (SLOP-01 ~ SLOP-05) 的 HTML 必須被準確抓到並回報 Fail。
3. 註解中的說明文字不應被誤判為違規。
4. CLI 預設無參數掃描 assets/ 全目錄返回 exit code 0。
5. CLI 預設無參數掃描範圍必須涵蓋 assets/ 全目錄（包含 anti-slop-demo 以外的檔案）。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
import verify_no_slop as vns  # noqa: E402

SLOPPY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>🚀 Elevate Your Workflow With AI Magic ✨</title>
  <style>
    .card {
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.45);
      background: linear-gradient(135deg, #6366f1, #a855f7);
    }
  </style>
</head>
<body class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
  <div class="card shadow-2xl">
    <h1>🔥 [LIVE] Seamlessly Revolutionize Your Experience</h1>
    <span class="badge animate-ping">Active Now</span>
    <p>Delve into the vibrant tapestry of data empowered by our game-changer platform.</p>
  </div>
</body>
</html>
"""


class TestVerifyNoSlop(unittest.TestCase):
    def test_clean_demo_html_passes(self):
        demo_path = REPO_ROOT / "assets" / "anti-slop-demo" / "index.html"
        self.assertTrue(demo_path.exists(), f"範例 HTML 不存在: {demo_path}")
        violations = vns.scan_file(demo_path)
        self.assertEqual(
            violations,
            [],
            f"範例 HTML 不應有任何罐頭違規，但發現：{[v.rule_id + ': ' + v.matched_text for v in violations]}",
        )

    def test_all_assets_pass_no_slop(self):
        assets_dir = REPO_ROOT / "assets"
        self.assertTrue(assets_dir.is_dir(), f"assets 目錄不存在: {assets_dir}")
        html_css_files = [
            f for f in sorted(assets_dir.rglob("*")) if f.suffix.lower() in (".html", ".htm", ".css")
        ]
        self.assertGreater(len(html_css_files), 0, "assets 目錄下應有 HTML/CSS 檔案")
        for f in html_css_files:
            violations = vns.scan_file(f)
            self.assertEqual(
                violations,
                [],
                f"{f.relative_to(REPO_ROOT)} 不應有任何罐頭違規，但發現：{[v.rule_id + ': ' + v.matched_text for v in violations]}",
            )

    def test_sloppy_html_caught_all_rules(self):
        violations = vns.scan_text(SLOPPY_HTML, filename="sloppy.html")
        self.assertGreater(len(violations), 0, "罐頭 HTML 應該檢測出多項違規")

        caught_rules = {v.rule_id for v in violations}
        self.assertIn("SLOP-01", caught_rules, "應檢測到 SLOP-01 (浮誇陰影)")
        self.assertIn("SLOP-02", caught_rules, "應檢測到 SLOP-02 (俗套漸層)")
        self.assertIn("SLOP-03", caught_rules, "應檢測到 SLOP-03 (裝飾 Emoji)")
        self.assertIn("SLOP-04", caught_rules, "應檢測到 SLOP-04 (假 LIVE)")
        self.assertIn("SLOP-05", caught_rules, "應檢測到 SLOP-05 (AI 廢話黑話)")

    def test_comments_are_not_flagged(self):
        html_with_comment_only = """
        <!-- 這裡有註解：delve into elevate seamlessly 🚀 shadow-2xl -->
        /* CSS 註解：linear-gradient(#6366f1, #a855f7) */
        <div class="border border-slate-800 bg-slate-900 text-slate-100">
          <p>正常內容，數據為 42ms。</p>
        </div>
        """
        violations = vns.scan_text(html_with_comment_only, filename="comment_only.html")
        self.assertEqual(violations, [], "註解內的說明文字不應被誤判為違規")

    def test_main_cli_execution(self):
        exit_code_default = vns.main([])
        self.assertEqual(exit_code_default, 0, "CLI 預設無參數掃描 assets/ 全目錄應返回 exit code 0")

        demo_path = str(REPO_ROOT / "assets" / "anti-slop-demo" / "index.html")
        exit_code = vns.main([demo_path])
        self.assertEqual(exit_code, 0, "CLI 掃描乾淨範例應返回 exit code 0")

    def test_main_cli_scans_all_assets_by_default(self):
        """CLI 預設無參數掃描必須涵蓋 assets/ 全目錄，不能只掃 anti-slop-demo。"""
        from unittest.mock import patch

        scanned_files: list[Path] = []
        original_scan_file = vns.scan_file

        def record_scan(path):
            scanned_files.append(Path(path).resolve())
            return original_scan_file(path)

        with patch.object(vns, "scan_file", side_effect=record_scan):
            exit_code = vns.main([])

        self.assertEqual(exit_code, 0, "CLI 預設無參數掃描應返回 exit code 0")
        non_demo_files = [
            p for p in scanned_files if "anti-slop-demo" not in p.parts
        ]
        self.assertGreater(
            len(non_demo_files),
            0,
            f"CLI 預設掃描應包含 assets/ 底下 anti-slop-demo 以外的檔案，但實際只掃描了：{scanned_files}",
        )

    def test_word_forms_are_caught(self):
        for word in ("delves", "Elevating", "seamless", "empowers", "unleashed", "revolutionized", "game-changer"):
            v = vns.scan_text(f"<p>{word} everything</p>", filename="w.html")
            self.assertTrue(any(x.rule_id == "SLOP-05" for x in v), f"{word} 應被 SLOP-05 抓到")

    def test_clean_prose_not_flagged_by_word_forms(self):
        v = vns.scan_text("<p>The elevator and the delivery date are 42ms apart.</p>", filename="c.html")
        self.assertEqual(v, [])

    def test_empty_or_missing_target_is_not_a_pass(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vns.main([tmp]), 2, "空目錄不得視為通過")
        self.assertEqual(vns.main([str(REPO_ROOT / "no-such-dir-xyz")]), 2)


if __name__ == "__main__":
    unittest.main()
