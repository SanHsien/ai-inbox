#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音畫同步節拍網格引擎原型 (BPM & Beat Grid Engine)
支援計算任意 BPM 在指定 FPS 下的精確拍點影格（Beat Frames）、小節切分、
最近節拍吸附（Snap-to-Grid），以及轉場與動效卡點序列生成（Remotion / GSAP 驅動）。
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class BeatCue:
    beat_index: int       # 拍數索引 (0, 1, 2, ...)
    bar_index: int        # 小節索引 (0, 1, ...)
    beat_in_bar: int      # 該小節內的第幾拍 (1, 2, 3, 4)
    time_seconds: float   # 拍點絕對時間 (秒)
    frame: int            # 拍點精準影格 (四捨五入整數)
    is_downbeat: bool     # 是否為小節強拍 (第 1 拍)


class BeatGridEngine:
    def __init__(
        self,
        bpm: float,
        fps: int = 60,
        beats_per_bar: int = 4,
        offset_seconds: float = 0.0,
    ):
        # NaN / inf 也必須擋下：bpm=inf 會讓每拍秒數為 0，get_beat_cues 變成無窮迴圈
        if not math.isfinite(bpm) or bpm <= 0:
            raise ValueError("BPM 必須是大於 0 的有限數值")
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("FPS 必須是大於 0 的有限數值")
        if int(beats_per_bar) != beats_per_bar or beats_per_bar <= 0:
            raise ValueError("beats_per_bar 必須是正整數")
        if not math.isfinite(offset_seconds):
            raise ValueError("offset_seconds 必須是有限數值")

        self.bpm = bpm
        self.fps = fps
        self.beats_per_bar = beats_per_bar
        self.offset_seconds = offset_seconds

        # 每拍秒數與每拍影格數 (浮點精度)
        self.seconds_per_beat = 60.0 / bpm
        self.frames_per_beat = self.seconds_per_beat * fps

    def get_beat_cues(self, duration_seconds: float) -> List[BeatCue]:
        """計算在指定秒數長度內的所有拍點影格清單"""
        if not math.isfinite(duration_seconds):
            raise ValueError("duration_seconds 必須是有限數值")
        cues = []
        beat_idx = 0

        while True:
            # 以「索引 × 60 / BPM」一次除法計算，不逐拍累加，避免浮點誤差累積而多算或少算邊界拍點
            t = self.offset_seconds + beat_idx * 60.0 / self.bpm
            if t >= duration_seconds:
                break
            bar_idx = beat_idx // self.beats_per_bar
            beat_in_bar = (beat_idx % self.beats_per_bar) + 1
            is_downbeat = beat_in_bar == 1
            frame = round(t * self.fps)

            cues.append(
                BeatCue(
                    beat_index=beat_idx,
                    bar_index=bar_idx,
                    beat_in_bar=beat_in_bar,
                    time_seconds=round(t, 4),
                    frame=frame,
                    is_downbeat=is_downbeat,
                )
            )
            beat_idx += 1

        return cues

    def snap_frame_to_grid(
        self,
        target_frame: int,
        subdivision: float = 1.0,  # 1.0 = 1 拍, 0.5 = 半拍 (8分音符), 0.25 = 1/4 拍
    ) -> Tuple[int, float]:
        """
        將目標影格吸附至最近的節拍網格點。
        回傳 (吸附後的 frame, 與原始影格的時間誤差秒數)
        """
        if not math.isfinite(subdivision) or subdivision <= 0:
            raise ValueError("subdivision 必須是大於 0 的有限數值")
        step_frames = self.frames_per_beat * subdivision
        offset_frames = self.offset_seconds * self.fps

        relative_frames = target_frame - offset_frames
        snapped_units = round(relative_frames / step_frames)
        snapped_frame = round(offset_frames + (snapped_units * step_frames))

        error_seconds = (snapped_frame - target_frame) / self.fps
        return snapped_frame, round(error_seconds, 4)

    def generate_cut_transitions(
        self,
        duration_seconds: float,
        beats_per_cut: int = 4,  # 預設每 4 拍（一小節）切一次鏡頭
        transition_duration_frames: int = 15,
    ) -> List[Dict]:
        """生成影片自動卡點轉場序列 (Transition Cut Cue Sequence)"""
        if int(beats_per_cut) != beats_per_cut or beats_per_cut <= 0:
            raise ValueError("beats_per_cut 必須是正整數")
        cues = self.get_beat_cues(duration_seconds)
        transitions = []

        for cue in cues:
            if cue.beat_index > 0 and cue.beat_index % beats_per_cut == 0:
                transitions.append({
                    "trigger_beat": cue.beat_index,
                    "trigger_frame": cue.frame,
                    "trigger_time": cue.time_seconds,
                    "transition_type": "zoom_punch" if cue.is_downbeat else "glitch_cut",
                    "duration_frames": transition_duration_frames,
                    "easing": "cubic-bezier(0.16, 1, 0.3, 1)",
                })

        return transitions


if __name__ == "__main__":
    engine = BeatGridEngine(bpm=120, fps=60)
    print(f"BPM: {engine.bpm}, FPS: {engine.fps}")
    print(f"每拍影格數: {engine.frames_per_beat:.2f} frames")
    cues = engine.get_beat_cues(duration_seconds=5.0)
    print(f"5秒內共有 {len(cues)} 拍：")
    for c in cues[:6]:
        print(f"  拍 {c.beat_index}: frame={c.frame}, t={c.time_seconds}s, downbeat={c.is_downbeat}")
