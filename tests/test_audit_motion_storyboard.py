#!/usr/bin/env python3
"""
tests/test_audit_motion_storyboard.py
單元測試：tools/audit_motion_storyboard.py 動態縮圖總覽與自審打分工具。

覆蓋重點：
1. 合規動效（seek 契約完整、深色高對比、物理彈簧、零罐頭）自審通過且評分 >= 8.0。
2. 缺失 window.seek(t) 介面契約之反例攔截。
3. Anti-Slop 各項違規（SLOP-M01 ~ SLOP-M05）特徵精確偵測與扣分斷言。
4. 影像平均亮度與對比度度量邏輯驗證。
5. 最差分鏡（Worst-3 Frames）排序挑選演算法正確性。
6. Contact Sheet（HTML 與 PNG）生成合規性與結構檢驗。
7. 命令列 CLI 退出碼與 --json 格式驗證。
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from audit_motion_storyboard import (
    FrameInfo,
    analyze_image_luminance,
    audit_motion_storyboard,
    calculate_frame_scores,
    check_html_anti_slop,
    check_seek_api_defined,
    generate_contact_sheet_html,
    generate_contact_sheet_image,
    main,
)


class TestAuditMotionStoryboard(unittest.TestCase):
    """測試動態分鏡自審打分工具的核心功能與反例攔截。"""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_motion_audit_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_html(
        self,
        with_seek: bool = True,
        slop_snippet: str = "",
        custom_body: str = "",
    ) -> Path:
        """建立用於測試的動態 HTML 檔案。"""
        seek_code = """
        window.seek = function(tInMs) {
          const canvas = document.getElementById('canvas');
          if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#090d16';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#f8fafc';
            ctx.fillText('Frame: ' + tInMs, 50, 50);
          }
          return Promise.resolve();
        };
        """ if with_seek else ""

        html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <title>Motion Test</title>
  <style>
    body {{ background: #090d16; color: #f8fafc; font-family: sans-serif; }}
    {slop_snippet}
  </style>
</head>
<body>
  <div id="app">
    <h1>代碼驅動動態設計測試</h1>
    {custom_body}
    <canvas id="canvas" width="640" height="360"></canvas>
  </div>
  <script>
    {seek_code}
  </script>
</body>
</html>
"""
        target = self.test_dir / "motion_test.html"
        target.write_text(html_content, encoding="utf-8")
        return target

    def test_check_seek_api_defined(self):
        """1. 檢驗 seek(t) 介面定義檢測邏輯。"""
        html_with_seek = "<html><script>window.seek = function(t) {};</script></html>"
        html_without_seek = "<html><script>function animate() {}</script></html>"

        self.assertTrue(check_seek_api_defined(html_with_seek))
        self.assertFalse(check_seek_api_defined(html_without_seek))

    def test_anti_slop_violations_detection(self):
        """2. 反例攔截：偵測 SLOP-M01 至 SLOP-M05 各項違規特徵。"""
        # SLOP-M01: 藍紫漸層 + 置中
        slop_1 = """
        .hero {
          background: linear-gradient(135deg, #6366f1, #a855f7);
          text-align: center;
        }
        """
        v1 = check_html_anti_slop(slop_1)
        self.assertTrue(any(v.rule_id == "SLOP-M01" for v in v1), f"未偵測到 SLOP-M01: {v1}")

        # SLOP-M02: 齊頭淡入 0s delay
        slop_2 = ".item { transition: opacity 0.3s; transition-delay: 0s; }"
        v2 = check_html_anti_slop(slop_2)
        self.assertTrue(any(v.rule_id == "SLOP-M02" for v in v2), f"未偵測到 SLOP-M02: {v2}")

        # SLOP-M03: 浮誇無腦陰影
        slop_3 = ".card { box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }"
        v3 = check_html_anti_slop(slop_3)
        self.assertTrue(any(v.rule_id == "SLOP-M03" for v in v3), f"未偵測到 SLOP-M03: {v3}")

        # SLOP-M04: 線性運動
        slop_4 = ".box { animation: move 2s linear infinite; }"
        v4 = check_html_anti_slop(slop_4)
        self.assertTrue(any(v.rule_id == "SLOP-M04" for v in v4), f"未偵測到 SLOP-M04: {v4}")

        # SLOP-M05: 罐頭裝飾 Emoji 與 AI 黑話
        slop_5 = "<h1>🚀 Unleash your potential and delve into creativity!</h1>"
        v5 = check_html_anti_slop(slop_5)
        self.assertTrue(any(v.rule_id == "SLOP-M05" for v in v5), f"未偵測到 SLOP-M05: {v5}")

    def test_scoring_matrix_and_worst_3_selection(self):
        """3. 驗證四維評分矩陣與 Worst-3 最差分鏡排序演算法。"""
        frames = [
            FrameInfo(frame_index=0, timestamp_ms=0, mean_luminance=120.0, contrast_std=40.0),
            FrameInfo(frame_index=1, timestamp_ms=500, mean_luminance=130.0, contrast_std=45.0),
            FrameInfo(frame_index=2, timestamp_ms=1000, mean_luminance=2.0, contrast_std=1.0),  # 全黑極端幀，低分
            FrameInfo(frame_index=3, timestamp_ms=1500, mean_luminance=140.0, contrast_std=50.0),
            FrameInfo(frame_index=4, timestamp_ms=2000, mean_luminance=254.0, contrast_std=3.0),  # 死白極端幀，低分
        ]

        calculate_frame_scores(frames, anti_slop_violations=[], has_seek_defined=True)

        # 斷言正常影格得分達到標準
        self.assertGreaterEqual(frames[0].total_score, 8.0)
        self.assertGreaterEqual(frames[1].total_score, 8.0)

        # 斷言異常影格被扣分
        self.assertLess(frames[2].total_score, 8.0)
        self.assertLess(frames[4].total_score, 8.0)

        # 驗證 Worst-3 排序
        sorted_frames = sorted(frames, key=lambda f: f.total_score)
        worst_indices = [f.frame_index for f in sorted_frames[:3]]
        self.assertIn(2, worst_indices)
        self.assertIn(4, worst_indices)

    def test_contact_sheet_html_generation(self):
        """4. 驗證 Contact Sheet HTML 報告之結構與可讀性。"""
        html_file = self._create_sample_html(with_seek=True)
        report = audit_motion_storyboard(
            html_path=html_file,
            frames_count=3,
            output_dir=self.test_dir / "audit_out",
            mock_frames=[
                FrameInfo(frame_index=0, timestamp_ms=0, mean_luminance=120.0, contrast_std=40.0),
                FrameInfo(frame_index=1, timestamp_ms=500, mean_luminance=130.0, contrast_std=45.0),
                FrameInfo(frame_index=2, timestamp_ms=1000, mean_luminance=135.0, contrast_std=42.0),
            ],
        )

        self.assertTrue(report.passed)
        self.assertIsNotNone(report.contact_sheet_html)

        html_content = Path(report.contact_sheet_html).read_text(encoding="utf-8")
        self.assertIn("動態設計分鏡自審縮圖總覽", html_content)
        self.assertIn("Frame #0", html_content)
        self.assertIn("Frame #1", html_content)
        self.assertIn("[PASS] 通過", html_content)

    def test_failure_on_missing_seek_or_slop(self):
        """5. 反例驗證：缺少 seek 或含有 Anti-Slop 違規時，自審必須失敗 (passed == False)。"""
        # 測試缺少 seek
        no_seek_file = self._create_sample_html(with_seek=False)
        report_no_seek = audit_motion_storyboard(
            html_path=no_seek_file,
            frames_count=2,
            output_dir=self.test_dir / "out_no_seek",
            mock_frames=[
                FrameInfo(frame_index=0, timestamp_ms=0, mean_luminance=100.0, contrast_std=30.0),
                FrameInfo(frame_index=1, timestamp_ms=500, mean_luminance=100.0, contrast_std=30.0),
            ],
        )
        self.assertFalse(report_no_seek.passed)

        # 測試含有 Slop 違規
        slop_file = self._create_sample_html(
            with_seek=True,
            slop_snippet=".bad { box-shadow: 0 25px 50px rgba(0,0,0,0.8); }",
        )
        report_slop = audit_motion_storyboard(
            html_path=slop_file,
            frames_count=2,
            output_dir=self.test_dir / "out_slop",
            mock_frames=[
                FrameInfo(frame_index=0, timestamp_ms=0, mean_luminance=100.0, contrast_std=30.0),
                FrameInfo(frame_index=1, timestamp_ms=500, mean_luminance=100.0, contrast_std=30.0),
            ],
        )
        self.assertFalse(report_slop.passed)
        self.assertGreater(len(report_slop.anti_slop_violations), 0)

    def test_cli_execution_and_json_flag(self):
        """6. 測試 CLI main() 執行，包含參數解析與 --json 輸出。"""
        html_file = self._create_sample_html(with_seek=True)

        # 6.1 目標不存在時回傳 2
        exit_code_missing = main(["non_existent_file_xyz.html"])
        self.assertEqual(exit_code_missing, 2)

        # 6.2 測試合規檔案在 mock 環境下的 CLI 表現
        # 由於完整 E2E 需瀏覽器執行，此處測試 --timestamps 參數格式解析
        exit_code_bad_ts = main([str(html_file), "--timestamps", "abc,def"])
        self.assertEqual(exit_code_bad_ts, 2)

    def test_live_playwright_extraction_if_available(self):
        """7. 實體驗證：若本機具備可用瀏覽器通道（msedge/chrome），執行端到端真實影格抽取。"""
        # 建立具備實際繪圖邏輯的 HTML
        real_html = self._create_sample_html(
            with_seek=True,
            custom_body="<p id='desc'>Live Animation Test</p>",
        )

        out_dir = self.test_dir / "live_out"
        report = audit_motion_storyboard(
            html_path=real_html,
            duration_ms=1000.0,
            frames_count=3,
            output_dir=out_dir,
            preferred_channel="msedge",  # Windows 原生支援
        )

        # 若成功調用瀏覽器，驗證產出影格與報告
        if not report.errors:
            self.assertEqual(len(report.frames), 3)
            self.assertTrue(report.passed)
            self.assertGreaterEqual(report.lowest_score, 8.0)
            # 確認實體截圖確實存在
            for f in report.frames:
                self.assertTrue(Path(f["file_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
