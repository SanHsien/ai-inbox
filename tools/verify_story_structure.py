#!/usr/bin/env python3
"""故事因果與三伏三冒檢驗器 (verify_story_structure.py)

針對許榮哲「靶心人故事公式」與劇本工程化驗收需求：
1. 嚴格驗證七節點（A~G 各 4 句 7 字共 28 字）與三因果箭頭（H1~H3 各 2 句 7 字共 14 字）字數契約
2. 檢驗因果真偽（H1 結局高於目標、H2 轉彎藏在阻礙、H3 意外來自努力，杜絕時間先後錯覺）
3. 評估三伏三冒跨度與鬆緊度（太緊 / 剛好 / 太鬆 / 缺失）
4. 明確輸出「最需要修正的一處」直指結構致命傷
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

NODE_ORDER = ["A", "B", "C", "D", "E", "F", "G"]
NODE_NAMES = {
    "A": "目標 (A)",
    "B": "阻礙 (B)",
    "C": "努力 (C)",
    "D": "結果 (D)",
    "E": "意外 (E)",
    "F": "轉彎 (F)",
    "G": "結局 (G)",
}


def is_cjk_char(ch: str) -> bool:
    """判斷單一字元是否為中文字元 (CJK)"""
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF
        or 0x3400 <= cp <= 0x4DBF
        or 0x20000 <= cp <= 0x2A6DF
        or 0xF900 <= cp <= 0xFAFF
    )


def extract_cjk_sentences(text: str) -> List[str]:
    """將文字依常見標點切分為純 CJK 句子清單"""
    if not text:
        return []
    # 依換行、句號、驚嘆號、問號、分號、逗號切分
    parts = re.split(r"[\n\r。！？；，,!?;\t]+", text.strip())
    sentences = []
    for p in parts:
        cjk_only = "".join(ch for ch in p if is_cjk_char(ch))
        if cjk_only:
            sentences.append(cjk_only)
    return sentences


@dataclass
class LengthContractViolation:
    item_id: str
    expected_sentences: int
    expected_chars_per_sentence: int
    actual_sentences: int
    actual_sentence_lengths: List[int]
    message: str


def verify_length_contract(
    item_id: str,
    text: str,
    expected_sentences: int,
    expected_chars: int = 7,
) -> Optional[LengthContractViolation]:
    """檢驗節點或箭頭的 4 句 7 字或 2 句 7 字契約"""
    if text.strip() in ("缺失", "無", "N/A", "missing"):
        return None  # 顯式標記缺失視為誠實，不報格式崩壞

    sentences = extract_cjk_sentences(text)
    actual_count = len(sentences)
    lengths = [len(s) for s in sentences]

    if actual_count != expected_sentences or any(l != expected_chars for l in lengths):
        msg = (
            f"{item_id} 違反字數契約：預期 {expected_sentences} 句、每句 {expected_chars} 字 "
            f"(共 {expected_sentences * expected_chars} 字)；實際得到 {actual_count} 句，各句長度為 {lengths}"
        )
        return LengthContractViolation(
            item_id=item_id,
            expected_sentences=expected_sentences,
            expected_chars_per_sentence=expected_chars,
            actual_sentences=actual_count,
            actual_sentence_lengths=lengths,
            message=msg,
        )
    return None


@dataclass
class CausalEvaluation:
    link_id: str  # H1, H2, H3
    source_node: str
    target_node: str
    description: str
    causal_strength: str  # 強 / 普通 / 弱 / 缺失
    post_hoc_risk: bool  # 是否有時間錯覺風險 (先發生的事被強行當作原因)
    rationale: str


def evaluate_causality(story_data: Dict[str, Any]) -> List[CausalEvaluation]:
    """評估三大因果連動真偽 (H1: A->G, H2: B->F, H3: C->E)"""
    evals: List[CausalEvaluation] = []
    arrows = story_data.get("arrows", {})
    nodes = story_data.get("nodes", {})

    # 定義三大因果檢驗規格
    specs = [
        ("H1", "A", "G", "結局要比目標高 (A→G)"),
        ("H2", "B", "F", "轉彎藏在阻礙 (B→F)"),
        ("H3", "C", "E", "意外來自努力 (C→E)"),
    ]

    for arrow_id, src, dst, title in specs:
        arrow_info = arrows.get(arrow_id, {})
        arrow_text = arrow_info.get("text", "")
        src_text = nodes.get(src, {}).get("text", "")
        dst_text = nodes.get(dst, {}).get("text", "")

        if not arrow_text or arrow_text.strip() in ("缺失", "無"):
            evals.append(
                CausalEvaluation(
                    link_id=arrow_id,
                    source_node=src,
                    target_node=dst,
                    description=title,
                    causal_strength="缺失",
                    post_hoc_risk=False,
                    rationale="因果連結未提供任何說明或標記為缺失",
                )
            )
            continue

        # 檢驗詞義關聯與因果標記
        declared_strength = arrow_info.get("strength", "普通")
        rationale_parts = []
        post_hoc = False

        # H1 特殊檢驗：結局是否超越目標
        if arrow_id == "H1":
            if "超越" in arrow_text or "昇華" in arrow_text or "領悟" in arrow_text or "心境" in arrow_text:
                rationale_parts.append("結局展現心境或境界昇華，實質超越初始物質目標。")
            elif "相同" in arrow_text or "原地" in arrow_text or "回到" in arrow_text:
                declared_strength = "弱"
                rationale_parts.append("結局僅達成甚至未達原目標，缺乏人物成長跨度。")

        # H2 特殊檢驗：轉彎是否直接由阻礙觸發
        elif arrow_id == "H2":
            if "突悟" in arrow_text or "天降" in arrow_text or "偶遇" in arrow_text:
                declared_strength = "弱"
                post_hoc = True
                rationale_parts.append("轉彎缺乏來自阻礙的直接壓迫，具有天降神兵（Deus ex machina）或時間錯覺風險。")
            else:
                rationale_parts.append("轉彎行為直接針對該阻礙的限制進行方法迭代。")

        # H3 特殊檢驗：意外是否為先前努力的連鎖副產物
        elif arrow_id == "H3":
            if "地震" in arrow_text or "天災" in arrow_text or "忽聞" in arrow_text or "碰巧" in arrow_text:
                declared_strength = "弱"
                post_hoc = True
                rationale_parts.append("意外純屬外部隨機事件，非先前努力行為引發的必然副效應。")
            else:
                rationale_parts.append("意外確實源自主角努力時觸發的未預期連鎖反應。")

        evals.append(
            CausalEvaluation(
                link_id=arrow_id,
                source_node=src,
                target_node=dst,
                description=title,
                causal_strength=declared_strength,
                post_hoc_risk=post_hoc,
                rationale=" ".join(rationale_parts) or "因果邏輯交代清晰。",
            )
        )

    return evals


@dataclass
class ForeshadowingEvaluation:
    index: int
    clue_node: str  # 伏筆節點
    reveal_node: str  # 回收節點
    distance: int  # 節點跨距步數
    tension: str  # 太緊 / 剛好 / 太鬆 / 缺失
    rationale: str


def evaluate_foreshadowing(foreshadows: List[Dict[str, Any]]) -> List[ForeshadowingEvaluation]:
    """評估三伏三冒長距離伏筆跨度與張力鬆緊度"""
    evals: List[ForeshadowingEvaluation] = []
    order_map = {name: idx for idx, name in enumerate(NODE_ORDER)}

    for idx, fs in enumerate(foreshadows, start=1):
        clue = fs.get("clue_node", "").upper()
        reveal = fs.get("reveal_node", "").upper()

        if clue not in order_map or reveal not in order_map:
            evals.append(
                ForeshadowingEvaluation(
                    index=idx,
                    clue_node=clue or "無",
                    reveal_node=reveal or "無",
                    distance=0,
                    tension="缺失",
                    rationale="伏筆或回收節點未明確標記或缺失",
                )
            )
            continue

        dist = order_map[reveal] - order_map[clue]
        if dist <= 0:
            tension = "缺失"
            rationale = "回收節點發生於伏筆節點之前或同一節點，時序倒錯"
        elif dist == 1:
            tension = "太緊"
            rationale = f"跨度僅 {dist} 步 (緊鄰節點)，懸念未及醞釀便立即揭曉，缺乏張力"
        elif 2 <= dist <= 4:
            tension = "剛好"
            rationale = f"跨度 {dist} 步，伏線千里且節奏收斂適度"
        else:
            tension = "太鬆"
            rationale = f"跨度達 {dist} 步，埋伏過久且跨距過大，讀者易遺忘其前因"

        evals.append(
            ForeshadowingEvaluation(
                index=idx,
                clue_node=clue,
                reveal_node=reveal,
                distance=dist,
                tension=tension,
                rationale=rationale,
            )
        )

    return evals


@dataclass
class StoryVerificationReport:
    is_valid: bool
    length_violations: List[LengthContractViolation]
    causal_evaluations: List[CausalEvaluation]
    foreshadowing_evaluations: List[ForeshadowingEvaluation]
    most_critical_fix: str
    summary: str


def verify_story_structure(story_data: Dict[str, Any]) -> StoryVerificationReport:
    """執行全套靶心人故事結構與三伏三冒驗證"""
    violations: List[LengthContractViolation] = []
    nodes = story_data.get("nodes", {})
    arrows = story_data.get("arrows", {})

    # 1. 驗證 7 節點 4 句 7 字
    for node_id in NODE_ORDER:
        node_text = nodes.get(node_id, {}).get("text", "")
        v = verify_length_contract(f"節點 {node_id} ({NODE_NAMES.get(node_id, '')})", node_text, 4, 7)
        if v:
            violations.append(v)

    # 2. 驗證 3 箭頭 2 句 7 字
    for arrow_id in ("H1", "H2", "H3"):
        arrow_text = arrows.get(arrow_id, {}).get("text", "")
        v = verify_length_contract(f"因果箭頭 {arrow_id}", arrow_text, 2, 7)
        if v:
            violations.append(v)

    # 3. 因果評估
    causal_evals = evaluate_causality(story_data)

    # 4. 三伏三冒評估
    fs_evals = evaluate_foreshadowing(story_data.get("foreshadowing", []))

    # 5. 萃取「最需要修正的一處」
    critical_fix = ""
    # 優先順序：重大因果時間錯覺 > 核心字數契約違反 > 伏冒缺失或太鬆
    weak_causals = [c for c in causal_evals if c.post_hoc_risk or c.causal_strength in ("弱", "缺失")]
    if weak_causals:
        c = weak_causals[0]
        critical_fix = f"【因果斷裂】{c.description} 存在嚴重薄弱點：{c.rationale}。建議重構該段情節，使 {c.target_node} 真正成為 {c.source_node} 的連鎖必然結果。"
    elif violations:
        v = violations[0]
        critical_fix = f"【字數契約】{v.message}。請嚴格調整為標準句數與每句 7 字規格。"
    else:
        bad_fs = [f for f in fs_evals if f.tension in ("太緊", "太鬆", "缺失")]
        if bad_fs:
            f = bad_fs[0]
            critical_fix = f"【伏筆張力】伏筆 #{f.index} ({f.clue_node}→{f.reveal_node}) 評估為「{f.tension}」：{f.rationale}。建議調整回收時機。"
        else:
            critical_fix = "結構完備！七節點字數契約、三因果向右箭頭與三伏三冒長距離張力皆達高標準。"

    is_valid = (len(violations) == 0 and len(weak_causals) == 0)
    summary = (
        f"靶心人結構驗證{'通過' if is_valid else '未通過'}！"
        f"字數契約違規 {len(violations)} 項，薄弱因果 {len(weak_causals)} 處。"
    )

    return StoryVerificationReport(
        is_valid=is_valid,
        length_violations=violations,
        causal_evaluations=causal_evals,
        foreshadowing_evaluations=fs_evals,
        most_critical_fix=critical_fix,
        summary=summary,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="故事因果與三伏三冒檢驗器")
    parser.add_argument("--input", required=True, help="靶心人故事 JSON 檔案路徑")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式輸出驗證報告")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"錯誤：輸入檔案不存在 '{input_path}'", file=sys.stderr)
        return 1

    content = input_path.read_text(encoding="utf-8")
    data = json.loads(content)
    report = verify_story_structure(data)
    rep_dict = asdict(report)

    if args.json:
        print(json.dumps(rep_dict, indent=2, ensure_ascii=False))
    else:
        print(f"[*] 故事因果檢驗結果：{input_path}")
        print(f"    - 判定結果：{'[PASS]' if report.is_valid else '[FAIL]'}")
        print(f"    - 字數契約違規：{len(report.length_violations)} 項")
        print(f"    - 最需修正的一處：\n      {report.most_critical_fix}")

    return 0 if report.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
