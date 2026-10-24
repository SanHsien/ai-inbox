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


if __name__ == "__main__":
    unittest.main()
