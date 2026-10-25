"""影片逐字稿工具：yt-dlp 抓音訊 + faster-whisper 本機轉寫（支援 NVIDIA GPU 加速）。

用途：YouTube 字幕端點回 HTTP 429 或沒有字幕時的備案（2026-10-24 實測可用）。
前置（Windows，皆為 pip --user 安裝，不需系統管理員權限）：
    python -m pip install --user -U yt-dlp faster-whisper "av>=14,<17" nvidia-cublas-cu12 nvidia-cudnn-cu12
注意：
    - av 必須 <17，av 19 與 faster-whisper 1.2.1 不相容（open() 不接受 metadata_errors）。
    - Windows 下透過 pip 安裝的 nvidia-cublas-cu12 / nvidia-cudnn-cu12 DLL 位於 site-packages/nvidia/*/bin，
      不會自動進系統 PATH；本腳本啟動時會自動透過 os.add_dll_directory 與 PATH 掛載。
    - yt-dlp 的 Scripts 目錄不在 PATH，因此一律以 `python -m yt_dlp` 呼叫。
    - 首次執行會下載 Whisper 模型（small 約數百 MB）到使用者快取目錄。

用法：
    python tools/video_transcript.py <影片網址> --out <輸出資料夾> [--lang zh] [--model small] [--device auto|cuda|cpu]

輸出：<out>/transcript.txt，每行格式 `[mm:ss] 文字`。
限制：Whisper small 會把專有名詞誤聽（例如 HeyGen 聽成「黑捲」），使用逐字稿前需人工校對。
"""

import argparse
import os
import site
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

# yt-dlp 單次下載上限（秒）；避免網路卡死時整個流程無限等待
DOWNLOAD_TIMEOUT_SECONDS = 3600
# yt-dlp 下載中途產生的暫存檔，不可當成完整音訊重用
_PARTIAL_SUFFIXES = (".part", ".ytdl", ".temp", ".tmp")
# 記錄 audio.* 是從哪個網址下載的；同一資料夾換網址時不可誤用舊音訊
_SOURCE_URL_FILE = "audio_source_url.txt"


def _register_cuda_dlls() -> list[Path]:
    """在 Windows 將 pip 安裝的 nvidia/*/bin 加入 DLL 搜尋路徑與 PATH。"""
    roots: list[Path] = []
    try:
        user_site = site.getusersitepackages()
        if user_site:
            roots.append(Path(user_site))
    except Exception:
        pass
    try:
        for p in site.getsitepackages():
            roots.append(Path(p))
    except Exception:
        pass

    added: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        nvidia_dir = root / "nvidia"
        if not nvidia_dir.is_dir():
            continue
        for bin_dir in sorted(nvidia_dir.glob("*/bin")):
            norm = str(bin_dir.resolve())
            if norm in seen or not bin_dir.is_dir():
                continue
            seen.add(norm)
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(norm)
                except OSError:
                    pass
            os.environ["PATH"] = norm + os.pathsep + os.environ.get("PATH", "")
            added.append(bin_dir)
    return added


def _resolve_device(requested: str) -> str:
    """解析推論裝置：auto 時若 ctranslate2 偵測到 CUDA 裝置則用 cuda，否則退回 cpu。"""
    if requested in ("cpu", "cuda"):
        return requested
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda"
    except Exception:
        pass
    return "cpu"


def _validate_url(url: str) -> str:
    """只接受 http(s) 網址。開頭為 "-" 的字串會被 yt-dlp 當成選項（例如 --exec），必須擋下。"""
    url = url.strip()
    # urlparse 會默默去掉 tab、換行等字元再判斷，驗過的字串會跟實際傳給 yt-dlp 的不同，直接拒絕
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in url):
        raise ValueError(f"網址含空白或控制字元：{url!r}")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"只接受 http(s) 影片網址：{url!r}")
    return url


def _audio_files(out_dir: Path) -> list[Path]:
    return sorted(
        p for p in out_dir.glob("audio.*") if p.is_file() and not p.name.lower().endswith(_PARTIAL_SUFFIXES)
    )


def download_audio(url: str, out_dir: Path) -> Path:
    """用 yt-dlp 下載最佳音訊，回傳音訊檔路徑；失敗時丟出 RuntimeError，網址不合法丟 ValueError。"""
    url = _validate_url(url)
    marker = out_dir / _SOURCE_URL_FILE
    existing = _audio_files(out_dir)
    if existing and existing[0].stat().st_size > 0:
        previous = marker.read_text(encoding="utf-8").strip() if marker.is_file() else None
        if previous is None or previous == url:
            return existing[0]
        # 資料夾裡的舊音訊來自別的網址：先移除，否則新音訊副檔名不同時（m4a→webm）會沿用舊檔
        for stale in existing:
            stale.unlink()
    template = str(out_dir / "audio.%(ext)s")
    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "-f", "bestaudio", "-o", template]
    cmd += ["--", url]  # "--" 之後一律視為位置參數，不會被解析成選項
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DOWNLOAD_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"yt-dlp 下載逾時（{DOWNLOAD_TIMEOUT_SECONDS} 秒）") from None
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp 下載失敗（exit {result.returncode}）：{(result.stderr or '')[-500:]}")
    candidates = _audio_files(out_dir)
    if not candidates:
        raise RuntimeError("yt-dlp 回報成功，但找不到 audio.* 輸出檔")
    marker.write_text(url + "\n", encoding="utf-8")
    return candidates[0]


def transcribe(audio: Path, out_file: Path, lang: str, model_name: str, device: str = "auto") -> tuple[float, str]:
    """以 faster-whisper 轉寫並寫出逐字稿，回傳 (音訊秒數, 實際使用裝置)。

    要求 cuda 但環境不支援時直接丟例外，不會靜默退回 CPU。
    """
    _register_cuda_dlls()
    actual_device = _resolve_device(device)
    from faster_whisper import WhisperModel

    compute_type = "float16" if actual_device == "cuda" else "int8"
    model = WhisperModel(model_name, device=actual_device, compute_type=compute_type)
    segments, info = model.transcribe(str(audio), language=lang, vad_filter=True)
    count = 0
    # 先寫暫存檔，成功才取代正式檔；失敗或結果為空時不會留下空的／殘缺的 transcript.txt，
    # 也不會覆蓋掉上一次的好結果。
    tmp_file = out_file.with_name(out_file.name + ".tmp")
    try:
        with tmp_file.open("w", encoding="utf-8") as handle:
            for seg in segments:
                handle.write(f"[{int(seg.start) // 60:02d}:{int(seg.start) % 60:02d}] {seg.text.strip()}\n")
                count += 1
        if count == 0:
            raise RuntimeError("轉寫結果為空：音訊可能無人聲，或語言設定不符")
        os.replace(tmp_file, out_file)
    finally:
        tmp_file.unlink(missing_ok=True)
    return info.duration, actual_device


def main() -> int:
    parser = argparse.ArgumentParser(description="下載影片音訊並以 Whisper 轉寫逐字稿")
    parser.add_argument("url", help="影片網址")
    parser.add_argument("--out", required=True, help="輸出資料夾（不存在會建立）")
    parser.add_argument("--lang", default="zh", help="語言代碼，預設 zh")
    parser.add_argument("--model", default="small", help="Whisper 模型，預設 small")
    parser.add_argument(
        "--device",
        choices=("auto", "cuda", "cpu"),
        default="auto",
        help="推論裝置，預設 auto（偵測到 NVIDIA GPU 即用 cuda，否則 cpu）；顯式指定 cuda 失敗時會直接報錯",
    )
    args = parser.parse_args()

    # Windows cp950 終端遇到無法編碼的字元不應崩潰
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass

    out_dir = Path(args.out)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        audio = download_audio(args.url, out_dir)
        out_file = out_dir / "transcript.txt"
        duration, actual_device = transcribe(audio, out_file, args.lang, args.model, args.device)
    except (RuntimeError, ValueError, OSError) as err:
        print(f"錯誤：{err}", file=sys.stderr)
        return 1
    print(f"完成：{out_file}（音訊 {duration:.0f} 秒，device={actual_device}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
