#!/usr/bin/env python3
"""關鍵幀縮圖總覽與自檢評審門禁工具 (verify_video_storyboard.py)

Code-as-Video 影視工作室品質保證門禁：
在影片正式執行重型渲染前，抽取 8~12 個關鍵影格（Keyframes；與 templates/video-studio-harness.md 第 4 節一致），
依照構圖層次、動態動機、對比光影與反 AI 罐頭設計準則進行 1-10 分自檢打分。
全數影格達到 8.0 分以上方可放行渲染，自動標記劣質分鏡並輸出微調修正建議。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _judge_common import ensure_utf8_output  # noqa: E402

# 關鍵影格數量範圍（templates/video-studio-harness.md 第 4 節：8~12 張 Contact Sheet）
MIN_KEYFRAMES = 8
MAX_KEYFRAMES = 12

# 反 AI 視覺罐頭特徵及其扣分權重
ANTI_SLOP_RULES = [
    {
        "id": "centered_title_3lines",
        "name": "置中三行大標題罐頭",
        "penalty": 2.5,
        "keywords": ["置中大標題", "置中標題", "三行標題", "centered title", "center-aligned title", "centered_title"],
        "remediation": "改用大斜角 (Oblique Angle) 懸浮平板視角，焦平面鎖定於文字前兩行，背景自然虛化。",
    },
    {
        "id": "blue_purple_gradient",
        "name": "泛濫藍紫漸層底色",
        "penalty": 2.5,
        "keywords": ["藍紫漸層", "紫色漸層", "科技漸層", "blue purple gradient", "purple gradient", "gradient_bg"],
        "remediation": "改用深黑虛空 (Dark Void, #000000) 或乾淨純色背景，靠介面高光與光斑營造質感。",
    },
    {
        "id": "fade_in_all",
        "name": "無腦全屏淡入",
        "penalty": 2.0,
        "keywords": ["全部淡入", "全屏淡入", "無腦淡入", "fade in all", "fade_in_all"],
        "remediation": "改用動作剪接 (Cut on Action) 或文字打字/串流有機揭示 (Stream Reveal)。",
    },
    {
        "id": "corner_badge",
        "name": "角落漂浮小標籤",
        "penalty": 1.5,
        "keywords": ["角落小標", "浮動小標", "膠囊標籤", "floating badge", "tagline badge", "corner_badge"],
        "remediation": "移除裝飾性小標，將必要資訊融入介面核心狀態或 Outro 標語。",
    },
]


@dataclass
class Keyframe:
    frame_id: str
    timestamp: float
    shot_type: str
    description: str
    camera_angle: str = "oblique"  # oblique, flat, top-down
    pitch_deg: float = 34.0
    focal_plane: str = "selective"  # selective (shallow DoF), full_sharp
    effects: List[str] = field(default_factory=list)
    elements: List[str] = field(default_factory=list)
    thumbnail_color: str = "#111827"


@dataclass
class ScoreBreakdown:
    composition_score: float
    motion_score: float
    anti_slop_score: float


@dataclass
class KeyframeEvaluation:
    frame_id: str
    timestamp: float
    shot_type: str
    total_score: float
    passed: bool
    breakdown: ScoreBreakdown
    violations: List[str]
    remediation: List[str]


@dataclass
class StoryboardGateReport:
    total_frames: int
    average_score: float
    gate_passed: bool
    threshold: float
    passed_frames: int
    flagged_frames: int
    evaluations: List[KeyframeEvaluation]
    summary: str


def evaluate_keyframe(kf: Keyframe, threshold: float = 8.0) -> KeyframeEvaluation:
    """對單一關鍵影格執行 1-10 分自檢打分"""
    score = 10.0
    violations: List[str] = []
    remediations: List[str] = []

    # 1. 檢查反 AI 罐頭規則
    desc_lower = kf.description.lower()
    effects_str = " ".join(kf.effects).lower()
    combined_text = f"{desc_lower} {effects_str}"

    anti_slop_deduction = 0.0
    for rule in ANTI_SLOP_RULES:
        violated = False
        if rule["id"] in kf.effects:
            violated = True
        else:
            for kw in rule["keywords"]:
                if kw in combined_text:
                    violated = True
                    break

        if violated:
            violations.append(f"{rule['name']} (-{rule['penalty']} 分)")
            remediations.append(rule["remediation"])
            anti_slop_deduction += rule["penalty"]

    score -= anti_slop_deduction
    anti_slop_score = max(0.0, 10.0 - anti_slop_deduction)

    # 2. 構圖與視角檢查 (Composition)
    composition_score = 10.0
    if kf.shot_type.lower() != "outro" and (kf.camera_angle == "flat" or abs(kf.pitch_deg) < 5.0):
        composition_score -= 2.5
        violations.append("死板正視角構圖 (-2.5 分)")
        remediations.append("增加 30°~45° 俯仰傾斜角度與淺景深，使軟體介面具備物理懸浮質感。")

    if kf.focal_plane == "full_sharp" and kf.shot_type.lower() in ("hero", "close-up"):
        composition_score -= 1.5
        violations.append("全平面死板對焦 (-1.5 分)")
        remediations.append("改用極薄焦平面（僅保留當前操作行銳利，周遭柔和虛化）。")

    score -= (10.0 - composition_score)

    # 3. 動態與光影檢查
    motion_score = 10.0
    if "no_motivated_motion" in kf.effects or "隨機漂移" in desc_lower:
        motion_score -= 2.0
        violations.append("無動機隨機位移 (-2.0 分)")
        remediations.append("攝影機位移方向必須永遠預判下一個使用者互動熱區（輸入框或按鈕）。")

    score -= (10.0 - motion_score)

    # 光影質感無法從分鏡 JSON 機械判斷，不打分（曾以常數 9.0 充當分數，已移除）
    total_score = round(max(1.0, min(10.0, score)), 2)
    passed = (total_score >= threshold and len(violations) == 0)

    breakdown = ScoreBreakdown(
        composition_score=round(composition_score, 1),
        motion_score=round(motion_score, 1),
        anti_slop_score=round(anti_slop_score, 1),
    )

    return KeyframeEvaluation(
        frame_id=kf.frame_id,
        timestamp=kf.timestamp,
        shot_type=kf.shot_type,
        total_score=total_score,
        passed=passed,
        breakdown=breakdown,
        violations=violations,
        remediation=remediations,
    )


def evaluate_storyboard(keyframes: List[Keyframe], threshold: float = 8.0) -> StoryboardGateReport:
    """對整個 Storyboard 進行門禁審查"""
    evaluations = [evaluate_keyframe(kf, threshold) for kf in keyframes]
    total = len(evaluations)
    if total == 0:
        return StoryboardGateReport(
            total_frames=0,
            average_score=0.0,
            gate_passed=False,
            threshold=threshold,
            passed_frames=0,
            flagged_frames=0,
            evaluations=[],
            summary="無關鍵影格資料",
        )

    avg_score = round(sum(e.total_score for e in evaluations) / total, 2)
    flagged = [e for e in evaluations if not e.passed]
    passed_count = total - len(flagged)
    count_ok = MIN_KEYFRAMES <= total <= MAX_KEYFRAMES
    gate_passed = (len(flagged) == 0 and avg_score >= threshold and count_ok)

    if gate_passed:
        summary = f"門禁通過！全數 {total} 個關鍵影格評分均達標 (平均 {avg_score} 分)。"
    elif not count_ok and not flagged:
        summary = f"門禁阻擋！關鍵影格數 {total} 超出規定範圍 {MIN_KEYFRAMES}~{MAX_KEYFRAMES} 張。"
    else:
        summary = f"門禁阻擋！發現 {len(flagged)} 個影格未達標準 (門檻 {threshold} 分，平均 {avg_score} 分)。"

    return StoryboardGateReport(
        total_frames=total,
        average_score=avg_score,
        gate_passed=gate_passed,
        threshold=threshold,
        passed_frames=passed_count,
        flagged_frames=len(flagged),
        evaluations=evaluations,
        summary=summary,
    )


def generate_contact_sheet_html(keyframes: List[Keyframe], report: StoryboardGateReport) -> str:
    """生成 Contact Sheet 縮圖總覽 HTML 頁面"""
    eval_map = {e.frame_id: e for e in report.evaluations}
    cards = []

    for kf in keyframes:
        ev = eval_map.get(kf.frame_id)
        score_val = ev.total_score if ev else 0.0
        badge_class = "badge-pass" if (ev and ev.passed) else "badge-fail"
        badge_text = f"{score_val} / 10"

        violations_html = ""
        if ev and ev.violations:
            items = "".join(f"<li>{html.escape(v)}</li>" for v in ev.violations)
            violations_html = f"<div class='violations'><strong>違規項：</strong><ul>{items}</ul></div>"

        remedy_html = ""
        if ev and ev.remediation:
            items = "".join(f"<li>{html.escape(r)}</li>" for r in ev.remediation)
            remedy_html = f"<div class='remediation'><strong>優化建議：</strong><ul>{items}</ul></div>"

        card = f"""
        <div class="frame-card">
          <div class="thumb-header">
            <span class="frame-id">{html.escape(kf.frame_id)} ({kf.timestamp}s)</span>
            <span class="shot-type">{html.escape(kf.shot_type)}</span>
            <span class="badge {badge_class}">{badge_text}</span>
          </div>
          <div class="thumb-box" style="background-color: {kf.thumbnail_color};">
            <div class="thumb-label">{html.escape(kf.shot_type)} - {kf.pitch_deg}°</div>
          </div>
          <div class="frame-body">
            <p class="desc">{html.escape(kf.description)}</p>
            {violations_html}
            {remedy_html}
          </div>
        </div>
        """
        cards.append(card)

    gate_status_class = "status-pass" if report.gate_passed else "status-fail"
    gate_status_text = "PASS 放行渲染" if report.gate_passed else "FAIL 阻擋渲染 (需重調)"

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <title>Keyframe Storyboard Gate Report</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #090b0e;
      color: #e5e7eb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 32px;
    }}
    .header {{
      max-width: 1200px;
      margin: 0 auto 32px auto;
      border-bottom: 1px solid #1f2937;
      padding-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    h1 {{ font-size: 24px; font-weight: 700; color: #f9fafb; }}
    .gate-badge {{
      font-size: 16px;
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: 600;
    }}
    .status-pass {{ background: #065f46; color: #34d399; border: 1px solid #059669; }}
    .status-fail {{ background: #881337; color: #fb7185; border: 1px solid #be123c; }}
    .summary-text {{ font-size: 14px; color: #9ca3af; margin-top: 8px; }}
    .grid {{
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }}
    .frame-card {{
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .thumb-header {{
      padding: 10px 14px;
      background: #161f2e;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }}
    .frame-id {{ font-weight: 600; color: #60a5fa; }}
    .shot-type {{ color: #9ca3af; }}
    .badge {{ padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 12px; }}
    .badge-pass {{ background: #064e3b; color: #34d399; }}
    .badge-fail {{ background: #7f1d1d; color: #f87171; }}
    .thumb-box {{
      height: 180px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-bottom: 1px solid #1f2937;
      color: rgba(255,255,255,0.4);
      font-size: 14px;
      font-weight: 500;
    }}
    .frame-body {{ padding: 14px; font-size: 13px; line-height: 1.5; flex: 1; }}
    .desc {{ color: #d1d5db; margin-bottom: 8px; }}
    .violations {{ color: #f87171; background: #261014; padding: 8px 10px; border-radius: 4px; margin-bottom: 8px; }}
    .violations ul, .remediation ul {{ margin-left: 16px; margin-top: 4px; }}
    .remediation {{ color: #fbbf24; background: #241c0e; padding: 8px 10px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>Code-as-Video 關鍵幀自檢評審總覽 (Storyboard Gate)</h1>
      <div class="summary-text">{html.escape(report.summary)}</div>
    </div>
    <div class="gate-badge {gate_status_class}">{gate_status_text}</div>
  </div>
  <div class="grid">
    {''.join(cards)}
  </div>
</body>
</html>
"""


def load_keyframes_from_json(path: Path) -> List[Keyframe]:
    """從 JSON 檔案載入關鍵影格清單"""
    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    raw_frames = data.get("keyframes", data if isinstance(data, list) else [])
    frames: List[Keyframe] = []
    for f in raw_frames:
        frames.append(
            Keyframe(
                frame_id=f.get("frame_id", f.get("id", f"KF-{len(frames)+1:02d}")),
                timestamp=float(f.get("timestamp", f.get("t", 0.0))),
                shot_type=f.get("shot_type", "Hero"),
                description=f.get("description", ""),
                camera_angle=f.get("camera_angle", "oblique"),
                pitch_deg=float(f.get("pitch_deg", 34.0)),
                focal_plane=f.get("focal_plane", "selective"),
                effects=f.get("effects", []),
                elements=f.get("elements", []),
                thumbnail_color=f.get("thumbnail_color", "#111827"),
            )
        )
    return frames


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_output()
    parser = argparse.ArgumentParser(description="Code-as-Video 關鍵影格縮圖總覽與自檢評審門禁工具")
    parser.add_argument("--input", required=True, help="分鏡規格 JSON 檔案路徑")
    parser.add_argument("--output", default="./storyboard_out", help="輸出報告與 HTML 縮圖總覽目錄")
    parser.add_argument("--threshold", type=float, default=8.0, help="放行及格分數門檻 (預設 8.0)")
    parser.add_argument("--json", action="store_true", help="在終端以 JSON 輸出報告")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"錯誤：輸入檔案不存在 '{input_path}'", file=sys.stderr)
        return 1

    try:
        keyframes = load_keyframes_from_json(input_path)
    except (OSError, UnicodeDecodeError, ValueError, TypeError, AttributeError) as err:
        print(f"錯誤：無法解析分鏡 JSON '{input_path}'：{err}", file=sys.stderr)
        return 1
    report = evaluate_storyboard(keyframes, threshold=args.threshold)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 輸出結構化 JSON 報告
    report_dict = asdict(report)
    json_path = out_dir / "storyboard_gate_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)

    # 輸出 Contact Sheet HTML
    html_content = generate_contact_sheet_html(keyframes, report)
    html_path = out_dir / "storyboard_contact_sheet.html"
    html_path.write_text(html_content, encoding="utf-8")

    if args.json:
        print(json.dumps(report_dict, indent=2, ensure_ascii=False))
    else:
        print(f"[*] Storyboard 門禁評審完畢：{input_path}")
        print(f"    - 總影格數：{report.total_frames}，平均得分：{report.average_score} / 10.0")
        print(f"    - 通過影格：{report.passed_frames}，待修正影格：{report.flagged_frames}")
        print(f"    - HTML Contact Sheet 輸出至：{html_path}")
        print(f"    - JSON 評審報告輸出至：{json_path}")
        if report.gate_passed:
            print("[PASS] 關鍵影格門禁審查通過，允許推進至正式渲染階段！")
        else:
            print("[FAIL] 關鍵影格門禁未通過，已自動標記劣質分鏡，請參閱修復建議後重新生成。")

    return 0 if report.gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
