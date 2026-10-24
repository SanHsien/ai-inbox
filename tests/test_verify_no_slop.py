"""
tests/test_verify_no_slop.py
測試 verify_no_slop.py：
1. 範例乾淨頁面 (assets/anti-slop-demo/index.html) 必須 0 違規回報 Pass。
2. 故意包含罐頭特徵 (SLOP-01 ~ SLOP-05) 的 HTML 必須被準確抓到並回報 Fail。
3. 註解中的說明文字不應被誤判為違規。
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
        demo_path = str(REPO_ROOT / "assets" / "anti-slop-demo" / "index.html")
        exit_code = vns.main([demo_path])
        self.assertEqual(exit_code, 0, "CLI 掃描乾淨範例應返回 exit code 0")


if __name__ == "__main__":
    unittest.main()
