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


def download_audio(url: str, out_dir: Path) -> Path:
    """用 yt-dlp 下載最佳音訊，回傳音訊檔路徑；失敗時丟出 RuntimeError。"""
    existing = sorted(out_dir.glob("audio.*"))
    if existing and existing[0].stat().st_size > 0:
        return existing[0]
    template = str(out_dir / "audio.%(ext)s")
    result = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "-f", "bestaudio", "-o", template, url],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp 下載失敗（exit {result.returncode}）：{result.stderr[-500:]}")
    candidates = sorted(out_dir.glob("audio.*"))
    if not candidates:
        raise RuntimeError("yt-dlp 回報成功，但找不到 audio.* 輸出檔")
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
    with out_file.open("w", encoding="utf-8") as handle:
        for seg in segments:
            handle.write(f"[{int(seg.start) // 60:02d}:{int(seg.start) % 60:02d}] {seg.text.strip()}\n")
            count += 1
    if count == 0:
        raise RuntimeError("轉寫結果為空：音訊可能無人聲，或語言設定不符")
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

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio = download_audio(args.url, out_dir)
    out_file = out_dir / "transcript.txt"
    duration, actual_device = transcribe(audio, out_file, args.lang, args.model, args.device)
    print(f"完成：{out_file}（音訊 {duration:.0f} 秒，device={actual_device}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
