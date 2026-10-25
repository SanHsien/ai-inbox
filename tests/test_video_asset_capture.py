"""
tests/test_video_asset_capture.py
tools/video_asset_capture.py 的單元測試。
"""

import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from video_asset_capture import (
    capture_url_assets,
    extract_css_colors,
)


class VideoAssetCaptureTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_extract_css_colors(self):
        html_snippet = """
        <html>
        <head><style>body { background-color: #121212; color: #ffffff; } a { color: #ff5500; }</style></head>
        <body><h1>Title</h1></body>
        </html>
        """
        theme = extract_css_colors(html_snippet)
        self.assertIn("primary_color", theme)
        self.assertIn("background_color", theme)
        self.assertIn("text_color", theme)
        self.assertIn("accent_color", theme)
        self.assertIn("#121212", [theme["primary_color"], theme["accent_color"]])

    def test_capture_url_assets_offline_fallback(self):
        out_dir = self.tmp / "assets"
        data = capture_url_assets("https://example.com", out_dir, offline_fallback=True)

        self.assertTrue((out_dir / "screenshot.png").exists())
        self.assertTrue((out_dir / "theme.json").exists())
        self.assertTrue((out_dir / "video_seek_canvas.html").exists())

        # 檢驗 theme.json 內容
        theme_content = json.loads((out_dir / "theme.json").read_text(encoding="utf-8"))
        self.assertEqual(theme_content["url"], "https://example.com")
        self.assertIn("primary_color", theme_content)
        self.assertIn("background_color", theme_content)

        # 檢驗 video_seek_canvas.html 內容
        html_text = (out_dir / "video_seek_canvas.html").read_text(encoding="utf-8")
        self.assertIn("window.seek", html_text)
        self.assertIn("video-canvas", html_text)
        self.assertIn("spring", html_text)
        self.assertIn("V = f(t) seek(t)", html_text)

    def test_rejects_non_http_urls(self):
        for bad in ("file:///C:/Windows/win.ini", "javascript:alert(1)", "ftp://x/y", "", "example.com",
                    "\x00http://a.com", "ht\ttp://a.com", "http://a .com"):
            with self.assertRaises(ValueError, msg=bad):
                capture_url_assets(bad, self.tmp / "o", offline_fallback=True)
        self.assertFalse((self.tmp / "o").exists())

    def test_untrusted_title_and_colors_cannot_break_out_of_html(self):
        import video_asset_capture as vac

        evil_title = '</title><script>alert(1)</script>'
        evil_color = "red;}</style><script>alert(2)</script>"
        fake = {
            "url": "https://example.com",
            "title": evil_title,
            "primary_color": evil_color,
            "background_color": "rgb(1, 2, 3)",
            "text_color": "#fff",
            "accent_color": "#38bdf8",
            "screenshot_file": "screenshot.png",
        }
        out_dir = self.tmp / "evil"

        # 走 offline 路徑，再手動以惡意資料呼叫模板產生器所用的清理函式
        self.assertEqual(vac._safe_color(evil_color, "#000"), "#000")
        self.assertEqual(vac._safe_color("rgb(1, 2, 3)", "#000"), "rgb(1, 2, 3)")
        script_json = vac._json_for_script(fake)
        self.assertNotIn("</script>", script_json)
        self.assertNotIn("<", script_json)
        self.assertEqual(json.loads(script_json)["title"], evil_title)  # 解析後內容不變

        data = capture_url_assets("https://example.com/</title>", out_dir, offline_fallback=True)
        html_text = (out_dir / "video_seek_canvas.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert", html_text)
        self.assertIn("&lt;/title&gt;", html_text)  # offline 標題含網址，已 HTML 跳脫
        self.assertEqual(html_text.count("</title>"), 1)
        self.assertNotIn("6.0.00s", html_text)
        self.assertEqual(data["url"], "https://example.com/</title>")


if __name__ == "__main__":
    unittest.main()
