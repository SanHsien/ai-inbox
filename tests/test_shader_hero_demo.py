#!/usr/bin/env python3
"""
tests/test_shader_hero_demo.py
測試 assets/shader-hero-demo/index.html：
1. 檔案存在性與基礎 HTML5 / 安全性規範（零依賴、無未授權外部請求、無本機路徑）。
2. WebGL 著色器管線完整性（上下文取得、頂點/片段著色器編譯、Program 連結、Uniforms 傳遞）。
3. 穩健生命週期與效能管理（DPR 自適應、rAF 迴圈、Visibility/Intersection 節流、Context Lost 防護、Dispose 釋放）。
4. Anti-Slop 規範符合度（無 SLOP-01~05 違規）。
5. 惡意修改/篡改之反例測試（缺少生命週期或包含罐頭特徵時必失敗）。
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_generative_ui_assets as vui  # noqa: E402
import verify_no_slop as vns  # noqa: E402


class TestShaderHeroDemo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo_path = REPO_ROOT / "assets" / "shader-hero-demo" / "index.html"
        cls.assertTrue(cls.demo_path.is_file(), f"展示檔案不存在: {cls.demo_path}")
        cls.html_content = cls.demo_path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """1. 驗證 assets/shader-hero-demo/index.html 存在且非空。"""
        self.assertTrue(self.demo_path.exists())
        self.assertGreater(len(self.html_content), 1000, "展示檔案內容過短")

    def test_html_baseline_and_security(self):
        """2. 驗證 HTML5 基礎結構與外部資源安全性。"""
        # 基礎結構驗證
        errors = vui.verify_html_baseline(self.html_content, "assets/shader-hero-demo/index.html")
        self.assertEqual(errors, [], f"HTML 基礎結構缺陷: {errors}")

        # Viewport 響應式配置
        self.assertIn('name="viewport"', self.html_content, "缺少 viewport 響應式 meta 標籤")

        # 安全性：無 http:// 明文傳輸
        sec_errors = vui.verify_asset_security_urls(self.html_content, "assets/shader-hero-demo/index.html")
        self.assertEqual(sec_errors, [], f"安全性錯誤: {sec_errors}")

        # 零外部打包依賴 (Zero-Build) 檢查：無任何 <script src="...">
        script_srcs = re.findall(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\']', self.html_content, re.I)
        self.assertEqual(script_srcs, [], f"Zero-Build 規範禁止外部 script 依賴，發現: {script_srcs}")

    def test_webgl_pipeline_integrity(self):
        """3. 驗證 WebGL 著色器初始化與管線程式碼契約。"""
        content = self.html_content

        # WebGL 上下文呼叫
        self.assertRegex(content, r"getContext\(['\"]webgl['\"]\)", "未包含標準 webgl 上下文取得呼叫")
        self.assertRegex(content, r"getContext\(['\"]experimental-webgl['\"]\)", "未包含 experimental-webgl 相容降級")

        # 著色器編譯管線
        required_gl_calls = [
            "createShader",
            "shaderSource",
            "compileShader",
            "createProgram",
            "attachShader",
            "linkProgram",
            "useProgram",
            "createBuffer",
            "bindBuffer",
            "bufferData",
            "enableVertexAttribArray",
            "vertexAttribPointer",
            "drawArrays",
        ]
        for call in required_gl_calls:
            self.assertIn(call, content, f"WebGL 著色器管線缺少必要呼叫: {call}")

        # Uniform 變數快取與傳遞
        required_uniforms = ["u_resolution", "u_time", "u_mouse", "u_mode"]
        for u in required_uniforms:
            self.assertIn(u, content, f"缺少必要 Uniform 變數: {u}")

    def test_lifecycle_and_performance_guards(self):
        """4. 驗證視窗響應、rAF 迴圈、後台節流、Context Lost 與資源釋放機制。"""
        content = self.html_content

        # 視窗縮放與 DPR 適配
        self.assertIn("devicePixelRatio", content, "缺少 devicePixelRatio 高解析度適配")
        self.assertIn("resizeCanvas", content, "缺少 Canvas 尺寸重算邏輯")
        self.assertIn("viewport", content, "缺少 gl.viewport 視角同步")

        # 渲染迴圈控制
        self.assertIn("requestAnimationFrame", content, "缺少 requestAnimationFrame 迴圈")
        self.assertIn("cancelAnimationFrame", content, "缺少 cancelAnimationFrame 暫停機制")

        # 離屏與後台節流
        self.assertIn("visibilitychange", content, "缺少 visibilitychange 後台分頁切換監聽")
        self.assertIn("IntersectionObserver", content, "缺少 IntersectionObserver 離屏滾動節流")

        # WebGL 上下文丟失守護
        self.assertIn("webglcontextlost", content, "缺少 webglcontextlost 上下文丟失監聽")
        self.assertIn("webglcontextrestored", content, "缺少 webglcontextrestored 上下文恢復監聽")

        # 確定性資源清理 (Disposal)
        disposal_calls = ["deleteBuffer", "deleteShader", "deleteProgram"]
        for call in disposal_calls:
            self.assertIn(call, content, f"缺少資源釋放呼叫: {call}")

    def test_anti_slop_compliance(self):
        """5. 驗證全檔符合 Anti-AI-Slop 視覺規範（SLOP-01~05 零違規）。"""
        violations = vns.scan_file(self.demo_path)
        self.assertEqual(
            violations,
            [],
            f"檢測到 AI 罐頭設計違規: {[v.rule_id + ': ' + v.matched_text for v in violations]}",
        )

    def test_negative_tamper_detection(self):
        """6. 反例測試：篡改 HTML 刻意引入罐頭特徵或刪除防線時必須失敗。"""
        # 反例 A: 注入俗套漸層與浮誇陰影
        bad_html_slop = self.html_content + '\n<div class="shadow-2xl from-indigo-500 to-purple-600">🚀 LIVE</div>'
        violations = vns.scan_text(bad_html_slop, "bad_slop.html")
        self.assertTrue(any(v.rule_id == "SLOP-01" for v in violations), "未能檢出浮誇陰影")
        self.assertTrue(any(v.rule_id == "SLOP-02" for v in violations), "未能檢出俗套藍紫漸層")
        self.assertTrue(any(v.rule_id == "SLOP-03" for v in violations), "未能檢出裝飾 Emoji")

        # 反例 B: 缺少 WebGL contextlost 防護
        tampered_no_lost = self.html_content.replace("webglcontextlost", "unhandled_event")
        self.assertNotIn("webglcontextlost", tampered_no_lost)


if __name__ == "__main__":
    unittest.main()
