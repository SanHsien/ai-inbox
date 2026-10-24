"""
tests/test_video_transcript.py
tools/video_transcript.py 的單元測試。

只測不需網路與模型的路徑：yt-dlp 失敗、找不到輸出檔、快取音訊重用、CUDA 裝置解析、轉寫結果為空。
真正的下載與 GPU/CPU 轉寫見 docs/video-transcript-howto.md 的實測紀錄。
"""

import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import video_transcript  # noqa: E402


def _completed(returncode: int, stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout="", stderr=stderr)


class DownloadAudioTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_nonzero_exit_raises_with_stderr(self):
        with mock.patch.object(video_transcript.subprocess, "run", return_value=_completed(1, "HTTP Error 429")):
            with self.assertRaises(RuntimeError) as ctx:
                video_transcript.download_audio("https://example.invalid/v", self.tmp)
        self.assertIn("429", str(ctx.exception))

    def test_success_without_output_file_raises(self):
        with mock.patch.object(video_transcript.subprocess, "run", return_value=_completed(0)):
            with self.assertRaises(RuntimeError) as ctx:
                video_transcript.download_audio("https://example.invalid/v", self.tmp)
        self.assertIn("audio.*", str(ctx.exception))

    def test_reuses_existing_nonempty_audio_without_calling_ytdlp(self):
        (self.tmp / "audio.webm").write_bytes(b"x")
        with mock.patch.object(video_transcript.subprocess, "run") as run:
            path = video_transcript.download_audio("https://example.invalid/v", self.tmp)
        run.assert_not_called()
        self.assertEqual(path.name, "audio.webm")

    def test_uses_current_interpreter_module_call(self):
        """必須用 python -m yt_dlp：yt-dlp 的 Scripts 目錄通常不在 PATH。"""
        with mock.patch.object(video_transcript.subprocess, "run", return_value=_completed(1)) as run:
            with self.assertRaises(RuntimeError):
                video_transcript.download_audio("https://example.invalid/v", self.tmp)
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[:3], [sys.executable, "-m", "yt_dlp"])


class DeviceResolveTest(unittest.TestCase):
    def test_explicit_cpu_or_cuda_preserved(self):
        self.assertEqual(video_transcript._resolve_device("cpu"), "cpu")
        self.assertEqual(video_transcript._resolve_device("cuda"), "cuda")

    def test_auto_picks_cuda_when_device_count_positive(self):
        fake_ct2 = types.SimpleNamespace(get_cuda_device_count=lambda: 1)
        with mock.patch.dict(sys.modules, {"ctranslate2": fake_ct2}):
            self.assertEqual(video_transcript._resolve_device("auto"), "cuda")

    def test_auto_falls_back_to_cpu_when_no_gpu(self):
        fake_ct2 = types.SimpleNamespace(get_cuda_device_count=lambda: 0)
        with mock.patch.dict(sys.modules, {"ctranslate2": fake_ct2}):
            self.assertEqual(video_transcript._resolve_device("auto"), "cpu")


class TranscribeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _fake_module(self, segments):
        info = types.SimpleNamespace(duration=12.0)
        model = mock.Mock()
        model.transcribe.return_value = (iter(segments), info)
        wm = mock.Mock(return_value=model)
        return types.SimpleNamespace(WhisperModel=wm), wm

    def test_empty_result_raises(self):
        mod, _ = self._fake_module([])
        with mock.patch.dict(sys.modules, {"faster_whisper": mod}):
            with self.assertRaises(RuntimeError):
                video_transcript.transcribe(self.tmp / "a.webm", self.tmp / "t.txt", "zh", "small", "cpu")

    def test_writes_timestamped_lines_in_utf8_and_uses_float16_on_cuda(self):
        seg = types.SimpleNamespace(start=65.4, text=" 你好 ")
        out = self.tmp / "t.txt"
        mod, wm = self._fake_module([seg])
        with mock.patch.dict(sys.modules, {"faster_whisper": mod}):
            duration, actual_device = video_transcript.transcribe(
                self.tmp / "a.webm", out, "zh", "small", "cuda"
            )
        self.assertEqual(duration, 12.0)
        self.assertEqual(actual_device, "cuda")
        wm.assert_called_once_with("small", device="cuda", compute_type="float16")
        self.assertEqual(out.read_text(encoding="utf-8"), "[01:05] 你好\n")


if __name__ == "__main__":
    unittest.main()
