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


    def test_rejects_non_http_urls_and_option_injection(self):
        for bad in ("--exec=calc", "-o/etc/x", "file:///C:/secret.mp4", "javascript:alert(1)", "", "example.com/v"):
            with mock.patch.object(video_transcript.subprocess, "run") as run:
                with self.assertRaises(ValueError, msg=bad):
                    video_transcript.download_audio(bad, self.tmp)
            run.assert_not_called()

    def test_url_goes_after_double_dash_without_shell(self):
        with mock.patch.object(video_transcript.subprocess, "run", return_value=_completed(1)) as run:
            with self.assertRaises(RuntimeError):
                video_transcript.download_audio("https://example.invalid/v?a=1&b=2", self.tmp)
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[-2:], ["--", "https://example.invalid/v?a=1&b=2"])
        self.assertIn("--no-playlist", cmd)
        self.assertFalse(run.call_args.kwargs.get("shell", False))
        self.assertIsNotNone(run.call_args.kwargs.get("timeout"))

    def test_timeout_becomes_runtime_error(self):
        err = subprocess.TimeoutExpired(cmd="yt-dlp", timeout=1)
        with mock.patch.object(video_transcript.subprocess, "run", side_effect=err):
            with self.assertRaises(RuntimeError) as ctx:
                video_transcript.download_audio("https://example.invalid/v", self.tmp)
        self.assertIn("逾時", str(ctx.exception))

    def test_partial_download_is_not_reused(self):
        (self.tmp / "audio.webm.part").write_bytes(b"half")
        with mock.patch.object(video_transcript.subprocess, "run", return_value=_completed(0)) as run:
            with self.assertRaises(RuntimeError):
                video_transcript.download_audio("https://example.invalid/v", self.tmp)
        run.assert_called_once()

    def test_cached_audio_from_other_url_is_redownloaded(self):
        (self.tmp / "audio.webm").write_bytes(b"old")
        (self.tmp / "audio_source_url.txt").write_text("https://example.invalid/OLD\n", encoding="utf-8")
        with mock.patch.object(video_transcript.subprocess, "run", return_value=_completed(0)) as run:
            video_transcript.download_audio("https://example.invalid/NEW", self.tmp)
        run.assert_called_once()
        self.assertIn("--force-overwrites", run.call_args.args[0])
        marker = (self.tmp / "audio_source_url.txt").read_text(encoding="utf-8").strip()
        self.assertEqual(marker, "https://example.invalid/NEW")


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

    def test_empty_result_keeps_previous_transcript_and_leaves_no_tmp(self):
        out = self.tmp / "t.txt"
        out.write_text("[00:00] 舊的好結果\n", encoding="utf-8")
        mod, _ = self._fake_module([])
        with mock.patch.dict(sys.modules, {"faster_whisper": mod}):
            with self.assertRaises(RuntimeError):
                video_transcript.transcribe(self.tmp / "a.webm", out, "zh", "small", "cpu")
        self.assertEqual(out.read_text(encoding="utf-8"), "[00:00] 舊的好結果\n")
        self.assertEqual([p.name for p in self.tmp.iterdir()], ["t.txt"])

    def test_timestamp_over_one_hour_keeps_minutes(self):
        seg = types.SimpleNamespace(start=3725.0, text="x")
        out = self.tmp / "t.txt"
        mod, _ = self._fake_module([seg])
        with mock.patch.dict(sys.modules, {"faster_whisper": mod}):
            video_transcript.transcribe(self.tmp / "a.webm", out, "zh", "small", "cpu")
        self.assertEqual(out.read_text(encoding="utf-8"), "[62:05] x\n")

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
