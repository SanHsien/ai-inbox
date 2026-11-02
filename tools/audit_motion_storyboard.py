#!/usr/bin/env python3
"""
tools/audit_motion_storyboard.py
Playwright + seek(t) 動畫縮圖總覽與自審打分工具。

對照規範：docs/code-driven-motion-design-studio-spec.md
核心職責：
1. 透過 Playwright 載入 HTML/Canvas 動效檔，調用 window.seek(t) 抽取關鍵影格。
2. 生成 Contact Sheet 縮圖總覽（PNG 與 HTML 報告）。
3. 執行基礎對比度、排版可讀性與 Anti-Slop（SLOP-M01~M05）特徵機械檢測。
4. 依四維矩陣（滿分 10.0 分）進行打分，挑出 Worst-3 最低分鏡，以 8.0 分為渲染硬閘門。

結束碼：
- 0: 全部關鍵影格評分均達門檻（預設 >= 8.0 分）。
- 1: 評分未達門檻，或存在 Anti-Slop 違規阻擋。
- 2: 參數錯誤、檔案不存在、缺少依賴或執行期異常。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 安全配置 UTF-8 輸出，避免 Windows cp950 崩潰
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


# ---------------------------------------------------------------------------
# 資料結構定義
# ---------------------------------------------------------------------------

@dataclass
class SlopViolation:
    rule_id: str
    rule_name: str
    description: str
    snippet: str = ""
    line: int = 0


@dataclass
class FrameInfo:
    frame_index: int
    timestamp_ms: float
    file_path: Optional[str] = None
    mean_luminance: float = 128.0
    contrast_std: float = 50.0
    scores: Dict[str, float] = field(default_factory=dict)
    total_score: float = 10.0
    issues: List[str] = field(default_factory=list)


@dataclass
class AuditReport:
    target_path: str
    passed: bool
    min_score_threshold: float
    lowest_score: float
    average_score: float
    worst_3_frames: List[Dict[str, Any]]
    frames: List[Dict[str, Any]]
    anti_slop_violations: List[Dict[str, Any]]
    contact_sheet_image: Optional[str] = None
    contact_sheet_html: Optional[str] = None
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Anti-Slop 靜態檢查器（對齊 docs/code-driven-motion-design-studio-spec.md）
# ---------------------------------------------------------------------------

SLOP_PATTERNS = [
    (
        "SLOP-M01",
        "俗套漸層背景＋置中粗體標題",
        re.compile(
            r"(?:linear-gradient\([^)]*(?:#6366f1|#a855f7|#ec4899|indigo|purple|violet)[^)]*\))[\s\S]{0,300}?(?:text-center|align:\s*center|justify-content:\s*center|<center>)",
            re.IGNORECASE,
        ),
        "禁止使用俗套藍紫/霓虹漸層背景搭配置中文案，請改用高對比實色背景與網格排版。",
    ),
    (
        "SLOP-M02",
        "全員齊頭同時淡入",
        re.compile(
            r"transition:\s*(?:all|opacity)[^;]*\b0s\b|transition-delay:\s*0s|animation-delay:\s*0s",
            re.IGNORECASE,
        ),
        "多元素進場應有 40ms~80ms 錯落延遲（Stagger Delay），避免無焦點齊頭進場。",
    ),
    (
        "SLOP-M03",
        "浮誇無腦陰影與生硬圓角徽章",
        re.compile(
            r"\bshadow-(?:2xl|xl)\b|box-shadow:\s*0(?:px)?\s+(?:2[0-9]|[3-9][0-9])px|box-shadow:[^;]*rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,\s*(?:0\.[4-9]|[1-9])\)",
            re.IGNORECASE,
        ),
        "禁止使用巨大半透明黑色模糊陰影，請改用 1px 細緻邊框與表面色彩層次。",
    ),
    (
        "SLOP-M04",
        "荒謬線性運動與無阻尼彈跳",
        re.compile(
            r"(?:transition|animation)(?:-timing-function)?:\s*linear\b|animation:[^;]*\blinear\b",
            re.IGNORECASE,
        ),
        "位移動畫必須基於物理彈簧（Spring Physics）或阻尼曲線，禁止機械塑料感線性運動。",
    ),
    (
        "SLOP-M05",
        "罐頭裝飾 Emoji 與模型黑話",
        re.compile(
            r"[🚀💡🔥✨🎉🔮🪄🌟]|\b(?:delve|seamlessly|elevate|revolutionize|tapestry|empower|unleash)\b",
            re.IGNORECASE,
        ),
        "禁止使用無語意裝飾 Emoji 與空洞行銷黑話，請使用真實功能文案與客觀數據。",
    ),
]


def check_html_anti_slop(html_text: str) -> List[SlopViolation]:
    """檢測 HTML/CSS 代碼中是否有 Anti-Slop 違規項。"""
    violations = []
    lines = html_text.splitlines()

    for rule_id, rule_name, pattern, desc in SLOP_PATTERNS:
        match = pattern.search(html_text)
        if match:
            matched_snippet = match.group(0).strip()
            # 計算行號
            start_pos = match.start()
            line_no = html_text[:start_pos].count("\n") + 1
            snippet = matched_snippet[:100] + ("..." if len(matched_snippet) > 100 else "")
            violations.append(
                SlopViolation(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    description=desc,
                    snippet=snippet,
                    line=line_no,
                )
            )

    return violations


def check_seek_api_defined(html_text: str) -> bool:
    """檢查原始碼中是否定義了 window.seek 介面契約。"""
    seek_pattern = re.compile(
        r"(?:window\s*\.\s*seek\s*=|function\s+seek\s*\(|seek\s*:\s*function|\bwindow\.seek\b)",
        re.IGNORECASE,
    )
    return bool(seek_pattern.search(html_text))


# ---------------------------------------------------------------------------
# 影像分析與視覺度量
# ---------------------------------------------------------------------------

def analyze_image_luminance(image_path: Path) -> Tuple[float, float, List[str]]:
    """計算影格的平均亮度與標準差（對比度），並返回警告清單。"""
    issues = []
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            gray = img.convert("L")
            # 使用 tobytes() 取得原始位元組數列，避免 Pillow 14 getdata 棄用警告
            pixels = list(gray.tobytes())
            n = len(pixels)
            if n == 0:
                return 0.0, 0.0, ["影像為空"]
            mean = sum(pixels) / n
            variance = sum((p - mean) ** 2 for p in pixels) / n
            std = math.sqrt(variance)

            # 極端畫面檢測
            if mean < 4.0:
                issues.append("畫面全黑無可見內容（Mean < 4.0）")
            elif mean > 250.0 and std < 6.0:
                issues.append("畫面過曝死白缺乏內容（Mean > 250, Std < 6.0）")
            elif std < 8.0:
                issues.append("畫面缺乏對比度（Std < 8.0，整體單調平緩）")

            return float(mean), float(std), issues
    except ImportError:
        # 若無 PIL，以檔案大小與基本檔案存在確認進行降級
        if not image_path.is_file() or image_path.stat().st_size == 0:
            return 0.0, 0.0, ["影像檔不存在或大小為 0"]
        return 128.0, 45.0, []
    except Exception as exc:
        return 128.0, 45.0, [f"影像解析異常: {exc}"]


# ---------------------------------------------------------------------------
# Playwright 影格擷取引擎
# ---------------------------------------------------------------------------

def extract_keyframes_playwright(
    html_path: Path,
    timestamps_ms: List[float],
    output_dir: Path,
    viewport: Tuple[int, int] = (1280, 720),
    preferred_channel: Optional[str] = None,
) -> Tuple[List[FrameInfo], List[str]]:
    """透過 Playwright 瀏覽器載入 HTML，調用 window.seek(t) 輸出截圖序列。"""
    errors: List[str] = []
    frames: List[FrameInfo] = []

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        errors.append(
            "缺少 Playwright 套件。請執行 pip install playwright && playwright install chromium 安裝依賴。"
        )
        return frames, errors

    output_dir.mkdir(parents=True, exist_ok=True)
    file_uri = html_path.resolve().as_uri()

    try:
        with sync_playwright() as p:
            browser = None
            channels_to_try = [preferred_channel] if preferred_channel else [None, "chrome", "msedge"]

            for ch in channels_to_try:
                try:
                    if ch:
                        browser = p.chromium.launch(channel=ch, headless=True)
                    else:
                        browser = p.chromium.launch(headless=True)
                    if browser:
                        break
                except Exception:
                    continue

            if not browser:
                errors.append(
                    "找不到可用的 Chromium / Chrome / Edge 瀏覽器。請執行 playwright install chromium。"
                )
                return frames, errors

            context = browser.new_context(
                viewport={"width": viewport[0], "height": viewport[1]},
                device_scale_factor=1,
            )
            page = context.new_page()

            # 載入動效 HTML
            page.goto(file_uri, wait_until="load", timeout=15000)

            # 驗證 window.seek 介面契約
            has_seek = page.evaluate("() => typeof window.seek === 'function'")
            if not has_seek:
                errors.append(
                    "頁面執行期未暴露 window.seek(t) 函式契約（window.seek is undefined）。"
                )
                browser.close()
                return frames, errors

            # 逐影格跳轉並擷取截圖
            for idx, t_ms in enumerate(timestamps_ms):
                try:
                    # 支援 Promise 與同步 seek(t)
                    page.evaluate("(t) => Promise.resolve(window.seek(t))", t_ms)
                    # 給予微小時間讓微任務與光柵化完成
                    page.wait_for_timeout(40)

                    frame_file = output_dir / f"frame_{idx:02d}_{int(t_ms)}ms.png"
                    page.screenshot(path=str(frame_file), full_page=False)

                    mean_lum, std_con, img_issues = analyze_image_luminance(frame_file)

                    frame = FrameInfo(
                        frame_index=idx,
                        timestamp_ms=t_ms,
                        file_path=str(frame_file),
                        mean_luminance=mean_lum,
                        contrast_std=std_con,
                        issues=img_issues,
                    )
                    frames.append(frame)
                except Exception as exc:
                    errors.append(f"擷取影格 t={t_ms}ms 失敗: {exc}")

            context.close()
            browser.close()
    except Exception as exc:
        errors.append(f"Playwright 執行異常: {exc}")

    return frames, errors


# ---------------------------------------------------------------------------
# 四維自審打分矩陣（對齊 docs 5.2 節）
# ---------------------------------------------------------------------------

def calculate_frame_scores(
    frames: List[FrameInfo],
    anti_slop_violations: List[SlopViolation],
    has_seek_defined: bool,
) -> None:
    """計算各影格之四維評分（滿分 10.0 分，每維度 2.5 分）。"""
    # 全域 Anti-Slop 扣分計算（每項違規扣 0.5 分，最高扣 2.5 分）
    slop_deduction = min(2.5, len(anti_slop_violations) * 0.8)
    anti_slop_score = max(0.0, 2.5 - slop_deduction)

    for i, frame in enumerate(frames):
        # 1. 構圖與資訊層級 (0.0 ~ 2.5)
        comp_score = 2.5
        if not has_seek_defined:
            comp_score -= 1.5
            frame.issues.append("未符合 seek 介面契約規範")

        # 2. 對比度與易讀性 (0.0 ~ 2.5)
        contrast_score = 2.5
        if frame.mean_luminance < 4.0 or (frame.mean_luminance > 250.0 and frame.contrast_std < 6.0):
            contrast_score = 0.0
            frame.issues.append("畫面全黑或死白無可見對比內容")
        elif frame.contrast_std < 10.0:
            contrast_score = max(0.0, contrast_score - 1.5)
            frame.issues.append("畫面缺乏對比度")

        # 3. 節奏動態與物理 (0.0 ~ 2.5)
        motion_score = 2.5
        # 若與前一幀亮度及對比度完全無差異（靜態死幀且非初始第 0 幀）
        if i > 0 and len(frames) > 2:
            prev = frames[i - 1]
            if abs(prev.mean_luminance - frame.mean_luminance) < 0.05 and abs(prev.contrast_std - frame.contrast_std) < 0.05:
                motion_score -= 0.5
                frame.issues.append("相鄰分鏡無動態變化（靜態凍結）")

        # 4. Anti-Slop 合規性 (0.0 ~ 2.5)
        frame_slop_score = anti_slop_score

        # 總分計算與歸一化
        total = round(comp_score + contrast_score + motion_score + frame_slop_score, 2)
        total = max(0.0, min(10.0, total))

        frame.scores = {
            "composition": round(comp_score, 2),
            "contrast": round(contrast_score, 2),
            "motion": round(motion_score, 2),
            "anti_slop": round(frame_slop_score, 2),
        }
        frame.total_score = total


# ---------------------------------------------------------------------------
# Contact Sheet 縮圖總覽生成器
# ---------------------------------------------------------------------------

def generate_contact_sheet_image(
    frames: List[FrameInfo],
    output_path: Path,
    title: str = "Motion Design Storyboard Contact Sheet",
) -> Optional[Path]:
    """若具備 PIL，拼裝實體網格圖檔；否則略過實體圖。"""
    valid_frames = [f for f in frames if f.file_path and Path(f.file_path).is_file()]
    if not valid_frames:
        return None

    try:
        from PIL import Image, ImageDraw

        n = len(valid_frames)
        cols = min(3, n)
        rows = math.ceil(n / cols)

        thumb_w, thumb_h = 360, 202  # 16:9
        pad = 20
        header_h = 60

        total_w = cols * thumb_w + (cols + 1) * pad
        total_h = header_h + rows * (thumb_h + 30) + (rows + 1) * pad

        sheet = Image.new("RGB", (total_w, total_h), color=(9, 13, 22))  # #090d16
        draw = ImageDraw.Draw(sheet)

        # 標題
        draw.text((pad, 20), title, fill=(241, 245, 249))

        for idx, f in enumerate(valid_frames):
            c = idx % cols
            r = idx // cols
            x = pad + c * (thumb_w + pad)
            y = header_h + pad + r * (thumb_h + 30 + pad)

            with Image.open(f.file_path) as img:
                thumb = img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x, y))

            # 繪製邊框
            border_color = (30, 41, 59) if f.total_score >= 8.0 else (239, 68, 68)
            draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=border_color, width=2)

            # 影格標籤
            label = f"Frame {f.frame_index} (t={int(f.timestamp_ms)}ms) - Score: {f.total_score}/10"
            draw.text((x, y + thumb_h + 6), label, fill=(148, 163, 184))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(output_path)
        return output_path
    except Exception:
        return None


def generate_contact_sheet_html(
    report: AuditReport,
    output_path: Path,
) -> Path:
    """生成自包含、無依賴的 HTML 縮圖自審報告。"""
    cards_html = []
    for f in report.frames:
        score = f["total_score"]
        score_color = "#10b981" if score >= 8.0 else "#ef4444"
        img_src = Path(f["file_path"]).name if f.get("file_path") else ""
        issues_li = "".join(f"<li>{issue}</li>" for issue in f.get("issues", []))

        cards_html.append(f"""
        <div class="frame-card">
          <div class="thumb-wrap" style="border-color: {score_color}">
            <img src="{img_src}" alt="Frame {f['frame_index']}" loading="lazy" />
            <span class="badge" style="background: {score_color}">{score} / 10</span>
          </div>
          <div class="frame-meta">
            <strong>Frame #{f['frame_index']}</strong> · <span class="mono">t={int(f['timestamp_ms'])}ms</span>
            <div class="sub-scores">
              構圖: {f['scores'].get('composition')} · 對比: {f['scores'].get('contrast')} · 動態: {f['scores'].get('motion')} · Anti-Slop: {f['scores'].get('anti_slop')}
            </div>
            {f'<ul class="issues">{issues_li}</ul>' if issues_li else ''}
          </div>
        </div>
        """)

    slop_html = ""
    if report.anti_slop_violations:
        items = "".join(
            f"<li><strong>[{v['rule_id']}] {v['rule_name']}</strong>: {v['description']}<br><code class='mono'>{v.get('snippet', '')}</code></li>"
            for v in report.anti_slop_violations
        )
        slop_html = f"""
        <div class="section-box alert">
          <h3>Anti-Slop 違規偵測報告</h3>
          <ul>{items}</ul>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <title>動態分鏡自審縮圖總覽 - {Path(report.target_path).name}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #090d16; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 32px; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{ border-bottom: 1px solid #1e293b; padding-bottom: 24px; margin-bottom: 32px; }}
    h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
    .meta-bar {{ color: #94a3b8; font-size: 14px; display: flex; gap: 24px; flex-wrap: wrap; }}
    .status-pass {{ color: #10b981; font-weight: 600; }}
    .status-fail {{ color: #ef4444; font-weight: 600; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; margin-top: 24px; }}
    .frame-card {{ background: #111827; border: 1px solid #1e293b; border-radius: 8px; overflow: hidden; }}
    .thumb-wrap {{ position: relative; width: 100%; aspect-ratio: 16/9; background: #000; border-bottom: 2px solid #1e293b; }}
    .thumb-wrap img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
    .badge {{ position: absolute; top: 10px; right: 10px; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; color: #fff; }}
    .frame-meta {{ padding: 16px; font-size: 14px; }}
    .sub-scores {{ font-size: 12px; color: #64748b; margin-top: 6px; }}
    .mono {{ font-family: ui-monospace, monospace; }}
    .issues {{ margin-top: 10px; padding-left: 20px; color: #f87171; font-size: 12px; }}
    .section-box {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 24px; }}
    .section-box.alert {{ background: #3b0764; border: 1px solid #7e22ce; color: #f5d0fe; }}
    .section-box h3 {{ margin-bottom: 12px; font-size: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>動態設計分鏡自審縮圖總覽 (Contact Sheet)</h1>
      <div class="meta-bar">
        <span>目標: <span class="mono">{Path(report.target_path).name}</span></span>
        <span>判定: <span class="{'status-pass' if report.passed else 'status-fail'}">{'[PASS] 通過' if report.passed else '[FAIL] 未達門檻'}</span></span>
        <span>平均分: <strong>{report.average_score}</strong></span>
        <span>最低分: <strong>{report.lowest_score}</strong>（門檻: {report.min_score_threshold}）</span>
      </div>
    </header>

    {slop_html}

    <div class="grid">
      {''.join(cards_html)}
    </div>
  </div>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# 主審核協調器
# ---------------------------------------------------------------------------

def audit_motion_storyboard(
    html_path: Path,
    duration_ms: float = 3000.0,
    frames_count: int = 6,
    timestamps: Optional[List[float]] = None,
    output_dir: Optional[Path] = None,
    min_score: float = 8.0,
    preferred_channel: Optional[str] = None,
    mock_frames: Optional[List[FrameInfo]] = None,
) -> AuditReport:
    """執行完整的分鏡自審流程。"""
    if not html_path.is_file():
        raise FileNotFoundError(f"目標檔案不存在：{html_path}")

    html_content = html_path.read_text(encoding="utf-8")
    has_seek = check_seek_api_defined(html_content)
    anti_slop_violations = check_html_anti_slop(html_content)

    # 計算抽樣時間戳記
    if timestamps is None:
        if frames_count <= 1:
            timestamps = [0.0]
        else:
            step = duration_ms / (frames_count - 1)
            timestamps = [round(i * step, 1) for i in range(frames_count)]

    actual_output_dir = output_dir or (html_path.parent / "artifacts" / "storyboard_audit")
    actual_output_dir.mkdir(parents=True, exist_ok=True)

    errors: List[str] = []
    if mock_frames is not None:
        frames = mock_frames
    else:
        frames, extract_errors = extract_keyframes_playwright(
            html_path=html_path,
            timestamps_ms=timestamps,
            output_dir=actual_output_dir,
            preferred_channel=preferred_channel,
        )
        errors.extend(extract_errors)

    # 若未成功擷取任何影格，構造佔位影格以供評分報告
    if not frames:
        for idx, t_ms in enumerate(timestamps):
            frames.append(
                FrameInfo(
                    frame_index=idx,
                    timestamp_ms=t_ms,
                    mean_luminance=0.0,
                    contrast_std=0.0,
                    issues=["未擷取到有效影格截圖"],
                )
            )

    # 執行打分矩陣計算
    calculate_frame_scores(frames, anti_slop_violations, has_seek)

    scores = [f.total_score for f in frames]
    lowest_score = min(scores) if scores else 0.0
    average_score = round(sum(scores) / len(scores), 2) if scores else 0.0

    # 挑出 Worst-3 分鏡
    sorted_frames = sorted(frames, key=lambda f: f.total_score)
    worst_3 = [asdict(f) for f in sorted_frames[:3]]

    # 判定硬閘門
    passed = (
        lowest_score >= min_score
        and len(anti_slop_violations) == 0
        and has_seek
        and len(errors) == 0
    )

    report = AuditReport(
        target_path=str(html_path),
        passed=passed,
        min_score_threshold=min_score,
        lowest_score=lowest_score,
        average_score=average_score,
        worst_3_frames=worst_3,
        frames=[asdict(f) for f in frames],
        anti_slop_violations=[asdict(v) for v in anti_slop_violations],
        errors=errors,
    )

    # 產出 Contact Sheet 檔案
    sheet_img_path = actual_output_dir / "contact_sheet.png"
    gen_img = generate_contact_sheet_image(frames, sheet_img_path)
    if gen_img:
        report.contact_sheet_image = str(gen_img)

    sheet_html_path = actual_output_dir / "contact_sheet.html"
    gen_html = generate_contact_sheet_html(report, sheet_html_path)
    report.contact_sheet_html = str(gen_html)

    return report


# ---------------------------------------------------------------------------
# CLI 命令列入口
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Playwright + seek(t) 動態縮圖總覽與自審打分工具"
    )
    parser.add_argument("target", help="目標動效 HTML 檔案路徑")
    parser.add_argument(
        "--duration",
        type=float,
        default=3000.0,
        help="動畫總時長（毫秒，預設 3000ms）",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=6,
        help="抽樣關鍵影格數量（預設 6）",
    )
    parser.add_argument(
        "--timestamps",
        type=str,
        default="",
        help="指定抽樣時點，逗號分隔（例如: 0,500,1000,1500,2000,2500）",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="截圖與 Contact Sheet 輸出目錄",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=8.0,
        help="渲染硬閘門最低及格分數（預設 8.0）",
    )
    parser.add_argument(
        "--channel",
        type=str,
        default="",
        help="指定 Playwright 瀏覽器通道（chrome / msedge）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="輸出 JSON 格式報告",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    target_path = Path(args.target)

    if not target_path.exists():
        print(f"錯誤：目標檔案不存在：{target_path}", file=sys.stderr)
        return 2

    timestamps = None
    if args.timestamps:
        try:
            timestamps = [float(x.strip()) for x in args.timestamps.split(",") if x.strip()]
        except ValueError:
            print("錯誤：--timestamps 格式錯誤，應為以逗號分隔的數值清單", file=sys.stderr)
            return 2

    out_dir = Path(args.output_dir) if args.output_dir else None
    preferred_channel = args.channel if args.channel else None

    try:
        report = audit_motion_storyboard(
            html_path=target_path,
            duration_ms=args.duration,
            frames_count=args.frames,
            timestamps=timestamps,
            output_dir=out_dir,
            min_score=args.min_score,
            preferred_channel=preferred_channel,
        )
    except Exception as exc:
        print(f"執行自審過程發生嚴重錯誤: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print("=" * 72)
        print("Playwright + seek(t) 動畫分鏡自審打分報告")
        print("=" * 72)
        print(f"目標動效: {report.target_path}")
        print(f"抽樣影格: {len(report.frames)} 幀 ｜ 及格門檻: {report.min_score_threshold} 分")
        print(f"平均得分: {report.average_score} 分 ｜ 最低影格得分: {report.lowest_score} 分")
        print("-" * 72)

        if report.anti_slop_violations:
            print("[WARN] ⚠️ 偵測到 Anti-Slop 違規項：")
            for v in report.anti_slop_violations:
                print(f"  - [{v['rule_id']}] {v['rule_name']}: {v['description']}")
            print("-" * 72)

        print("[*] 影格明細與評分：")
        for f in report.frames:
            status = "PASS" if f["total_score"] >= report.min_score_threshold else "FAIL"
            print(
                f"  Frame #{f['frame_index']} (t={int(f['timestamp_ms'])}ms): "
                f"{f['total_score']} 分 [{status}] "
                f"(構圖: {f['scores'].get('composition')}, 對比: {f['scores'].get('contrast')}, "
                f"動態: {f['scores'].get('motion')}, Anti-Slop: {f['scores'].get('anti_slop')})"
            )
            for iss in f.get("issues", []):
                print(f"    - 問題: {iss}")

        print("-" * 72)
        print("[*] 評分最低分鏡 (Worst-3 Frames)：")
        for w in report.worst_3_frames:
            print(f"  - Frame #{w['frame_index']} (t={int(w['timestamp_ms'])}ms): {w['total_score']} 分")

        print("-" * 72)
        if report.contact_sheet_html:
            print(f"[*] HTML 自審報告已生成: {report.contact_sheet_html}")
        if report.contact_sheet_image:
            print(f"[*] 縮圖總覽圖已生成: {report.contact_sheet_image}")

        if report.errors:
            print("-" * 72)
            print("[ERROR] 執行期警告或錯誤：")
            for err in report.errors:
                print(f"  - {err}")

        print("=" * 72)
        if report.passed:
            print("🎉 [PASS] 全部分鏡評分均達 8.0 門檻，獲准啟動 FFmpeg 終端渲染！")
        else:
            print("❌ [FAIL] 分鏡評分低於門檻或存在違規項，已阻擋終端渲染，請修復 Worst-3 後再試。")
        print("=" * 72)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
