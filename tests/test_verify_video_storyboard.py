#!/usr/bin/env python3
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from verify_video_storyboard import (
    Keyframe,
    evaluate_keyframe,
    evaluate_storyboard,
    generate_contact_sheet_html,
    load_keyframes_from_json,
)


class TestVerifyVideoStoryboard(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_storyboard_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_high_quality_keyframe_passes(self):
        kf = Keyframe(
            frame_id="KF-01",
            timestamp=2.5,
            shot_type="Hero",
            description="懸浮平板低角度俯仰，焦平面僅鎖定第一行搜尋文字，深黑虛空背景",
            camera_angle="oblique",
            pitch_deg=34.0,
            focal_plane="selective",
            effects=["stream_reveal"],
        )
        ev = evaluate_keyframe(kf, threshold=8.0)
        self.assertTrue(ev.passed)
        self.assertGreaterEqual(ev.total_score, 8.0)
        self.assertEqual(len(ev.violations), 0)

    def test_ai_slop_keyframe_flagged(self):
        kf = Keyframe(
            frame_id="KF-02",
            timestamp=5.0,
            shot_type="Hero",
            description="置中大標題搭配藍紫漸層科技背景，全部淡入出現，右上角浮動小標籤",
            camera_angle="flat",
            pitch_deg=0.0,
            focal_plane="full_sharp",
            effects=["centered_title_3lines", "blue_purple_gradient", "fade_in_all"],
        )
        ev = evaluate_keyframe(kf, threshold=8.0)
        self.assertFalse(ev.passed)
        self.assertLess(ev.total_score, 8.0)
        self.assertTrue(len(ev.violations) >= 3)
        self.assertTrue(len(ev.remediation) >= 3)

    def test_storyboard_gate_pass_and_fail(self):
        good_kf = Keyframe(
            frame_id="KF-01",
            timestamp=0.0,
            shot_type="Hero",
            description="黑石平板斜角 34 度，極淺景深代碼高亮",
            camera_angle="oblique",
            pitch_deg=34.0,
            focal_plane="selective",
        )
        bad_kf = Keyframe(
            frame_id="KF-02",
            timestamp=3.0,
            shot_type="Macro",
            description="置中標題無腦全屏淡入",
            effects=["fade_in_all", "centered_title_3lines"],
        )

        # 混合分鏡：門禁應阻擋
        report_fail = evaluate_storyboard([good_kf] * 7 + [bad_kf], threshold=8.0)
        self.assertFalse(report_fail.gate_passed)
        self.assertEqual(report_fail.flagged_frames, 1)
        self.assertEqual(report_fail.passed_frames, 7)

        # 全優良分鏡：門禁應放行
        report_pass = evaluate_storyboard([good_kf] * 8, threshold=8.0)
        self.assertTrue(report_pass.gate_passed)
        self.assertEqual(report_pass.flagged_frames, 0)

    def test_frame_count_outside_8_to_12_blocks_gate(self):
        good_kf = Keyframe(
            frame_id="KF-01", timestamp=0.0, shot_type="Hero",
            description="黑石平板斜角 34 度，極淺景深代碼高亮",
            camera_angle="oblique", pitch_deg=34.0, focal_plane="selective",
        )
        for n in (1, 7, 13):
            report = evaluate_storyboard([good_kf] * n, threshold=8.0)
            self.assertEqual(report.flagged_frames, 0)
            self.assertFalse(report.gate_passed, f"{n} 張不在 8~12 範圍，不得放行")
            self.assertIn("8~12", report.summary)
        self.assertTrue(evaluate_storyboard([good_kf] * 12, threshold=8.0).gate_passed)

    def test_cli_main_exit_codes(self):
        from verify_video_storyboard import main

        good = {"keyframes": [{"frame_id": f"KF-{i:02d}", "description": "黑石平板斜角，極淺景深", "pitch_deg": 34.0} for i in range(8)]}
        bad = {"keyframes": [dict(good["keyframes"][0], effects=["fade_in_all"]) for _ in range(8)]}
        out = self.test_dir / "out"
        gp, bp = self.test_dir / "good.json", self.test_dir / "bad.json"
        gp.write_text(json.dumps(good), encoding="utf-8")
        bp.write_text(json.dumps(bad), encoding="utf-8")
        self.assertEqual(main(["--input", str(gp), "--output", str(out)]), 0)
        self.assertEqual(main(["--input", str(bp), "--output", str(out)]), 1)
        self.assertEqual(main(["--input", str(self.test_dir / "missing.json"), "--output", str(out)]), 1)
        broken = self.test_dir / "broken.json"
        broken.write_text("{oops", encoding="utf-8")
        self.assertEqual(main(["--input", str(broken), "--output", str(out)]), 1)

    def test_empty_storyboard(self):
        report = evaluate_storyboard([], threshold=8.0)
        self.assertFalse(report.gate_passed)
        self.assertEqual(report.total_frames, 0)

    def test_contact_sheet_html_generation(self):
        kf = Keyframe(
            frame_id="KF-01",
            timestamp=1.0,
            shot_type="Hero",
            description="簡約鏡頭",
        )
        report = evaluate_storyboard([kf])
        html_out = generate_contact_sheet_html([kf], report)
        self.assertIn("<!DOCTYPE html>", html_out)
        self.assertIn("KF-01", html_out)
        self.assertIn("Storyboard Gate Report", html_out)

    def test_load_keyframes_from_json(self):
        json_file = self.test_dir / "storyboard.json"
        data = {
            "keyframes": [
                {
                    "frame_id": "KF-01",
                    "timestamp": 1.2,
                    "shot_type": "Hero",
                    "description": "測試鏡頭",
                    "pitch_deg": 32.0,
                }
            ]
        }
        json_file.write_text(json.dumps(data), encoding="utf-8")
        loaded = load_keyframes_from_json(json_file)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].frame_id, "KF-01")
        self.assertEqual(loaded[0].pitch_deg, 32.0)


if __name__ == "__main__":
    unittest.main()
