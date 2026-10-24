#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beat_grid.py 單元測試
驗證音畫同步節拍網格引擎 (BPM & Beat Grid Engine) 計算正確性，
包含拍點影格、小節切分、前奏偏移、Snap-to-Grid 吸附與卡點轉場序列生成。
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 讓 `tools` 套件不依賴執行目錄
from tools.beat_grid import BeatGridEngine


class TestBeatGridEngine(unittest.TestCase):
    def test_basic_bpm_to_frame_calculation(self):
        # 120 BPM 在 60 FPS 下，每拍 0.5 秒，每拍剛好 30 frames
        engine = BeatGridEngine(bpm=120, fps=60)
        self.assertAlmostEqual(engine.seconds_per_beat, 0.5)
        self.assertAlmostEqual(engine.frames_per_beat, 30.0)

        # 計算 2 秒內的拍點 (共 4 拍：0.0s, 0.5s, 1.0s, 1.5s)
        cues = engine.get_beat_cues(duration_seconds=2.0)
        self.assertEqual(len(cues), 4)

        expected_frames = [0, 30, 60, 90]
        actual_frames = [c.frame for c in cues]
        self.assertEqual(actual_frames, expected_frames)

    def test_bar_and_downbeat_detection(self):
        # 4/4 拍小節強拍檢驗
        engine = BeatGridEngine(bpm=120, fps=60, beats_per_bar=4)
        cues = engine.get_beat_cues(duration_seconds=4.0)  # 8 拍 (2 小節)

        self.assertEqual(len(cues), 8)
        # 第 0 拍與第 4 拍應為小節強拍 (is_downbeat == True)
        self.assertTrue(cues[0].is_downbeat)
        self.assertEqual(cues[0].bar_index, 0)
        self.assertEqual(cues[0].beat_in_bar, 1)

        self.assertFalse(cues[1].is_downbeat)
        self.assertFalse(cues[2].is_downbeat)
        self.assertFalse(cues[3].is_downbeat)

        self.assertTrue(cues[4].is_downbeat)
        self.assertEqual(cues[4].bar_index, 1)
        self.assertEqual(cues[4].beat_in_bar, 1)

    def test_offset_handling(self):
        # 音樂前奏有 0.25 秒 offset (15 frames @ 60fps)
        engine = BeatGridEngine(bpm=120, fps=60, offset_seconds=0.25)
        cues = engine.get_beat_cues(duration_seconds=1.5)

        self.assertEqual(cues[0].frame, 15)
        self.assertEqual(cues[1].frame, 45)
        self.assertEqual(cues[2].frame, 75)

    def test_snap_frame_to_grid(self):
        # 120 BPM, 60 FPS -> 網格在 0, 30, 60, 90...
        engine = BeatGridEngine(bpm=120, fps=60)

        # 影格 32 應吸附到 30
        snapped, error = engine.snap_frame_to_grid(target_frame=32)
        self.assertEqual(snapped, 30)
        self.assertAlmostEqual(error, -2 / 60, places=3)

        # 影格 58 應吸附到 60
        snapped, error = engine.snap_frame_to_grid(target_frame=58)
        self.assertEqual(snapped, 60)
        self.assertAlmostEqual(error, 2 / 60, places=3)

        # 測試細分網格 (半拍 15 frames)
        # 影格 17 在半拍 (15) 與整拍 (30) 之間，應吸附至 15
        snapped_half, _ = engine.snap_frame_to_grid(target_frame=17, subdivision=0.5)
        self.assertEqual(snapped_half, 15)

    def test_cut_transitions_generation(self):
        engine = BeatGridEngine(bpm=120, fps=60, beats_per_bar=4)
        # 6 秒 = 12 拍，每 4 拍切一次鏡頭，應觸發第 4 拍與第 8 拍
        transitions = engine.generate_cut_transitions(duration_seconds=6.0, beats_per_cut=4)

        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["trigger_beat"], 4)
        self.assertEqual(transitions[0]["trigger_frame"], 120)
        self.assertEqual(transitions[0]["transition_type"], "zoom_punch")

        self.assertEqual(transitions[1]["trigger_beat"], 8)
        self.assertEqual(transitions[1]["trigger_frame"], 240)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            BeatGridEngine(bpm=0)
        with self.assertRaises(ValueError):
            BeatGridEngine(bpm=-100)
        with self.assertRaises(ValueError):
            BeatGridEngine(bpm=120, fps=0)


if __name__ == "__main__":
    unittest.main()
