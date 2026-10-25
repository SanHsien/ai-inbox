#!/usr/bin/env python3
"""
tests/test_verify_generative_ui_assets.py
測試 tools/verify_generative_ui_assets.py 外部裁判驗證器：
1. 真實 4 個 Generative UI HTML 展示檔全數通過驗證。
2. DOCTYPE 宣告缺失反例攔截。
3. UTF-8 charset 或非空 <title> 缺失反例攔截。
4. 非安全外部資源（http://、file://、本機磁碟路徑、協定相對路徑 //）反例攔截。
5. CLI main() 執行成功（exit 0）與失敗（exit 1）行為驗證。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_generative_ui_assets as vui  # noqa: E402


class TestVerifyGenerativeUIAssets(unittest.TestCase):
    def test_real_assets_all_pass(self):
        """1. 驗證現存於 assets/ 的真實 4 個 HTML 展示檔全數合規。"""
        all_passed, results = vui.verify_all_generative_ui_assets(REPO_ROOT)
        self.assertTrue(all_passed, f"真實 HTML 展示檔驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤，實際：{errs}")
        self.assertEqual(len(results), 4, "應涵蓋全部 4 個展示檔")

    def test_missing_doctype_intercepted(self):
        """2. 反例攔截：HTML 缺少 <!DOCTYPE html> 宣告。"""
        sample_html = """
        <html lang="zh-TW">
        <head>
          <meta charset="UTF-8">
          <title>示範測試標題</title>
        </head>
        <body><div id="root">Hello</div></body>
        </html>
        """
        errors = vui.verify_html_baseline(sample_html, "test.html")
        self.assertTrue(
            any("缺少標準 HTML5 <!DOCTYPE html>" in e for e in errors),
            f"未攔截到缺少 DOCTYPE：{errors}",
        )

    def test_missing_charset_or_empty_title_intercepted(self):
        """3. 反例攔截：缺少 UTF-8 編碼宣告或 <title> 標籤為空。"""
        # 缺少 charset
        html_no_charset = """<!DOCTYPE html>
        <html><head><title>有標題但無編碼</title></head><body></body></html>"""
        errs_charset = vui.verify_html_baseline(html_no_charset)
        self.assertTrue(
            any("缺少 UTF-8 編碼宣告" in e for e in errs_charset),
            f"未攔截缺少 UTF-8：{errs_charset}",
        )

        # title 標籤為空
        html_empty_title = """<!DOCTYPE html>
        <html><head><meta charset="UTF-8"><title>   </title></head><body></body></html>"""
        errs_title = vui.verify_html_baseline(html_empty_title)
        self.assertTrue(
            any("<title> 標籤內容不可為空" in e for e in errs_title),
            f"未攔截空 title：{errs_title}",
        )

    def test_insecure_urls_intercepted(self):
        """4. 反例攔截：外部資源使用 http://、file://、本機磁碟路徑或協定相對路徑 //。"""
        bad_cases = [
            ('<script src="http://cdn.jsdelivr.net/npm/vue@3"></script>', "HTTP 協定"),
            ('<link href="http://example.com/style.css" rel="stylesheet">', "HTTP 協定"),
            ('<script src="file:///C:/Users/test/lib.js"></script>', "file:// 協定"),
            ('<script src="C:\\tools\\secret.js"></script>', "本機磁碟絕對路徑"),
            ('<script src="//cdn.tailwindcss.com"></script>', "協定相對路徑"),
        ]

        for snippet, label in bad_cases:
            html = f"""<!DOCTYPE html>
            <html><head><meta charset="UTF-8"><title>Test</title>{snippet}</head><body></body></html>"""
            errors = vui.verify_asset_security_urls(html, "bad_url_test.html")
            self.assertTrue(
                len(errors) > 0 and any(label in e for e in errors),
                f"未能攔截不安全資源 ({label})：{errors}",
            )

    def test_cli_main_exit_codes(self):
        """8. 驗證 CLI main() 執行成功返回 0，指定不存在之根目錄返回 1。"""
        # 成功狀況
        code_success = vui.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(code_success, 0)

        # 失敗狀況（空目錄）
        code_fail = vui.main(["--repo-root", str(REPO_ROOT / "tools")])
        self.assertEqual(code_fail, 1)


if __name__ == "__main__":
    unittest.main()
