"""影片逐字稿工具：yt-dlp 抓音訊 + faster-whisper 本機轉寫。

用途：YouTube 字幕端點回 HTTP 429 或沒有字幕時的備案（2026-10-24 實測可用）。
前置（Windows，皆為 pip --user 安裝，不需系統管理員權限）：
    python -m pip install --user -U yt-dlp faster-whisper "av>=14,<17"
注意：
    - av 必須 <17，av 19 與 faster-whisper 1.2.1 不相容（open() 不接受 metadata_errors）。
    - yt-dlp 的 Scripts 目錄不在 PATH，因此一律以 `python -m yt_dlp` 呼叫。
    - 首次執行會下載 Whisper 模型（small 約數百 MB）到使用者快取目錄。

用法：
    python tools/video_transcript.py <影片網址> --out <輸出資料夾> [--lang zh] [--model small]

輸出：<out>/transcript.txt，每行格式 `[mm:ss] 文字`。
限制：Whisper small 會把專有名詞誤聽（例如 HeyGen 聽成「黑捲」），使用逐字稿前需人工校對。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def download_audio(url: str, out_dir: Path) -> Path:
    """用 yt-dlp 下載最佳音訊，回傳音訊檔路徑；失敗時丟出 RuntimeError。"""
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


def transcribe(audio: Path, out_file: Path, lang: str, model_name: str) -> float:
    """以 faster-whisper 轉寫並寫出逐字稿，回傳音訊秒數。"""
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio), language=lang, vad_filter=True)
    count = 0
    with out_file.open("w", encoding="utf-8") as handle:
        for seg in segments:
            handle.write(f"[{int(seg.start) // 60:02d}:{int(seg.start) % 60:02d}] {seg.text.strip()}\n")
            count += 1
    if count == 0:
        raise RuntimeError("轉寫結果為空：音訊可能無人聲，或語言設定不符")
    return info.duration


def main() -> int:
    parser = argparse.ArgumentParser(description="下載影片音訊並以 Whisper 轉寫逐字稿")
    parser.add_argument("url", help="影片網址")
    parser.add_argument("--out", required=True, help="輸出資料夾（不存在會建立）")
    parser.add_argument("--lang", default="zh", help="語言代碼，預設 zh")
    parser.add_argument("--model", default="small", help="Whisper 模型，預設 small")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio = download_audio(args.url, out_dir)
    out_file = out_dir / "transcript.txt"
    duration = transcribe(audio, out_file, args.lang, args.model)
    print(f"完成：{out_file}（音訊 {duration:.0f} 秒）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
