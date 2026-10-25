#!/usr/bin/env python3
"""
tools/verify_motion_and_video_specs.py
動態視覺字典（Cinetic／Motion Prompt／cinematic-shot）與 Code-as-Video 規範之「外部裁判」結構驗證器（純 Python stdlib）。

驗證目標：
1. docs/cinetic-motion-dictionary.md：
   - 涵蓋 14 大分類統計清冊與對應章節清冊；
   - 涵蓋 273 種技法項目（數量與結構完全吻合）；
   - 涵蓋 60 FPS 基準、Easing 貝茲時間曲線與 Spring 物理彈簧預設配方。
2. docs/motion-prompt-cheatsheet.md：
   - 涵蓋 6 大套件（motion, camera, ui, lp, photo, motion2）；
   - 共 144 款動效對照表（#001 至 #144）；
   - 表格各列均無任何空白單元格。
3. docs/cinematic-shot-camera-guide.md：
   - 涵蓋 5 種經典運鏡 Shot 參數設定表（Hero, Close-up, Pan/Track, Action Cut, Outro）；
   - 涵蓋核心 Shot 的 AI 視訊提示詞範本（Prompt / Negative Prompt）。
4. templates/video-studio-harness.md：
   - 涵蓋 seek(t) 確定性時間函式契約與時間純函數哲學；
   - 涵蓋四大反 AI 視覺套路禁令（Anti-AI Slop Rules）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 1. Cinetic 14 大分類定義 (key, 中文名稱, 技法數量)
EXPECTED_CINETIC_CATEGORIES: List[Tuple[str, str, int]] = [
    ("opening_hook", "開場視覺鉤子", 10),
    ("transition", "轉場切換", 22),
    ("camera", "虛擬運鏡與相機", 22),
    ("typography_motion", "動態文字排版", 25),
    ("ui_choreography", "介面佈局編舞", 19),
    ("data_and_numbers", "數據與計數動態", 17),
    ("product_demo", "產品演示與場景", 22),
    ("logo_and_end_card", "品牌與結尾卡片", 18),
    ("color_and_light", "色彩與光影節奏", 25),
    ("texture_and_finish", "質感後製與幀率", 20),
    ("layout_and_composition", "版面與動態構圖", 16),
    ("pacing_structure", "速度曲線與結構", 23),
    ("micro_interaction", "微互動與點擊響應", 20),
    ("depth_and_3d", "景深與空間 3D", 14),
]
TOTAL_CINETIC_TECHNIQUES = sum(count for _, _, count in EXPECTED_CINETIC_CATEGORIES)  # 273

# 2. Motion Prompt 6 大套件定義 (序號, slug, 中文名稱)
EXPECTED_MOTION_PACKS: List[Tuple[str, str, str]] = [
    ("1", "motion", "Motion Graphics 基礎動效"),
    ("2", "camera", "攝影機運鏡與轉場"),
    ("3", "ui", "現代 UI 元件與互動動效"),
    ("4", "lp", "著陸頁與網頁演出"),
    ("5", "photo", "攝影布光與質感風格"),
    ("6", "motion2", "進階動態手法與轉場"),
]
TOTAL_MOTION_PROMPTS = 144

# 3. cinematic-shot 5 種經典運鏡
EXPECTED_CINEMATIC_SHOTS: List[Tuple[int, str]] = [
    (1, "Hero Shot"),
    (2, "Close-up Shot"),
    (3, "Pan / Track Shot"),
    (4, "Action Cut Shot"),
    (5, "Outro Shot"),
]

# 4. video-studio-harness 四大反 AI 罐頭禁令
EXPECTED_ANTI_SLOP_BANS: List[Tuple[int, str]] = [
    (1, "漸層置中標題"),
    (2, "全員無腦淡入"),
    (3, "角落小標與無效徽章"),
    (4, "無節奏均速飄移"),
]


def find_repo_root(start: Optional[Path] = None) -> Path:
    """自動推導 repository 根目錄。"""
    if start is not None:
        return start.resolve()
    cur = Path(__file__).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "notes").is_dir() and (parent / "docs").is_dir():
            return parent
    return Path.cwd()


def verify_cinetic_motion_dictionary(text: str) -> List[str]:
    """
    驗證 docs/cinetic-motion-dictionary.md：
    - 涵蓋 14 大分類統計清冊與對應章節
    - 技法清冊累計達 273 種技法項目
    - 涵蓋 60 FPS 基準、Easing 貝茲時間配方與 Spring 彈簧物理配方
    """
    errors: List[str] = []
    if not text.strip():
        return ["檔案內容為空"]

    # 1. 驗證總量宣告
    if not re.search(r"總計：\*\*14\s*大分類、273\s*種", text):
        errors.append("未宣告涵蓋「14 大分類、273 種動態技法」之核心總計規格")

    # 2. 驗證 14 大分類統計清冊表格與各分類子章節
    for cat_key, cat_name, expected_count in EXPECTED_CINETIC_CATEGORIES:
        # 清冊表格中是否有該分類
        if not re.search(rf"`{cat_key}`", text):
            errors.append(f"統計清冊表格缺少分類代碼：`{cat_key}` ({cat_name})")

        # 第 3 節中是否有該分類章節
        if not re.search(rf"###\s+3\.\d+\s+.*{cat_name}", text):
            errors.append(f"缺少第 3 節分類章節：{cat_name} (`{cat_key}`)")

    # 3. 驗證各分類的「完整技法清冊」表格與技法列數
    # 標題格式如：#### `opening_hook` 完整技法清冊 (10 項)
    cat_table_pattern = re.compile(
        r"####\s+`([a-z0-9_]+)`\s+完整技法清冊\s*\(\s*(\d+)\s*項\s*\)(.*?)(?=\n###|\Z)",
        re.S,
    )
    found_tables = {m.group(1): (int(m.group(2)), m.group(3)) for m in cat_table_pattern.finditer(text)}

    total_parsed_techniques = 0
    for cat_key, cat_name, expected_count in EXPECTED_CINETIC_CATEGORIES:
        if cat_key not in found_tables:
            errors.append(f"缺少分類 `{cat_key}` 之「完整技法清冊」表格")
            continue

        decl_count, table_block = found_tables[cat_key]
        if decl_count != expected_count:
            errors.append(
                f"分類 `{cat_key}` 清冊宣告技法數 ({decl_count}) 與預期 ({expected_count}) 不符"
            )

        # 解析表格中的技法資料列（以 | ` 開頭）
        tech_rows = [
            line.strip()
            for line in table_block.strip().splitlines()
            if line.strip().startswith("| `")
        ]
        if len(tech_rows) != expected_count:
            errors.append(
                f"分類 `{cat_key}` 清冊實際表格列數 ({len(tech_rows)}) 與預期 ({expected_count}) 不符"
            )
        total_parsed_techniques += len(tech_rows)

    if total_parsed_techniques != TOTAL_CINETIC_TECHNIQUES:
        errors.append(
            f"技法清冊解析總列數 ({total_parsed_techniques}) 不等於預期 273 種技法"
        )

    # 4. 驗證 60 FPS 基準、貝茲時間曲線與物理彈簧預設
    if not re.search(r"60\s*FPS", text):
        errors.append("缺少 60 FPS 渲染幀率基準說明")

    # 貝茲時間字典 (Easing Tokens - E.)
    if not (re.search(r"貝茲時間曲線字典|Easing Tokens", text) and re.search(r"`E\.", text)):
        errors.append("缺少 60 FPS 貝茲時間曲線字典（Easing Tokens - `E`）規格")

    for token in ["out", "in", "exit", "inOut", "smooth", "ui", "cam"]:
        if not re.search(rf"\|\s*`{token}`\s*\|", text):
            errors.append(f"Easing Tokens 缺少核心時間曲線 Token：`{token}`")

    # 物理彈簧預設字典 (Spring Presets - SPR)
    if not (re.search(r"物理彈簧預設字典|Spring Presets", text) and re.search(r"`SPR`|SPR\.", text)):
        errors.append("缺少物理彈簧預設字典（Spring Presets - `SPR`）規格")

    for preset in ["snap", "pop", "land", "micro", "firm", "soft"]:
        if not re.search(rf"\|\s*`{preset}`\s*\|", text):
            errors.append(f"Spring Presets 缺少核心物理彈簧預設：`{preset}`")

    # 節拍網格公式
    if not re.search(r"BPM|Beat Grid", text):
        errors.append("缺少音畫同步節拍網格（Beat Grid Engine）計算規範")

    return errors


def verify_motion_prompt_cheatsheet(text: str) -> List[str]:
    """
    驗證 docs/motion-prompt-cheatsheet.md：
    - 涵蓋 6 大套件（motion, camera, ui, lp, photo, motion2）
    - 涵蓋共 144 款動效對照表（#001 至 #144）
    - 表格所有單元格均填寫完整，無任何空白單元格
    """
    errors: List[str] = []
    if not text.strip():
        return ["檔案內容為空"]

    # 1. 驗證 6 大套件
    for num, slug, name in EXPECTED_MOTION_PACKS:
        pattern = rf"Pack:\s*{slug}"
        if not re.search(pattern, text, re.I):
            errors.append(f"缺少套件 {num}：{name} (Pack: {slug})")

    # 2. 驗證 144 款動效列
    # 格式：| **#001** | ... |
    row_pattern = re.compile(r"^\|\s*\*\*#(\d+)\*\*\s*\|(.*)$", re.M)
    matches = row_pattern.findall(text)

    if len(matches) != TOTAL_MOTION_PROMPTS:
        errors.append(
            f"動效列數量不符：解析出 {len(matches)} 款，預期應為 {TOTAL_MOTION_PROMPTS} 款"
        )

    # 檢查編號連續性
    expected_ids = [f"{i:03d}" for i in range(1, TOTAL_MOTION_PROMPTS + 1)]
    actual_ids = [m[0] for m in matches]

    missing_ids = set(expected_ids) - set(actual_ids)
    if missing_ids:
        errors.append(f"動效編號缺漏：{sorted(list(missing_ids))[:5]} 等共 {len(missing_ids)} 項")

    # 3. 檢查單元格是否無空白
    # 每列預期欄位：編號 | 繁體中文名稱 | 英文名稱 | 一句話效果說明 | 對 AI 的說法範例 | 核心規格與參數 (Timing / Easing)
    for idx_str, rest in matches:
        raw_cells = rest.split("|")
        # 去掉 Markdown 表格結尾的空字串
        if raw_cells and raw_cells[-1].strip() == "":
            raw_cells.pop()

        cells = [c.strip() for c in raw_cells]
        if len(cells) < 5:
            errors.append(
                f"動效 #{idx_str} 欄位數量不足 (實際 {len(cells) + 1} 欄，預期 6 欄)"
            )

        for col_idx, cell_content in enumerate(cells, start=2):
            if not cell_content:
                errors.append(f"動效 #{idx_str} 第 {col_idx} 欄為空白單元格")

    return errors


def verify_cinematic_shot_camera_guide(text: str) -> List[str]:
    """
    驗證 docs/cinematic-shot-camera-guide.md：
    - 涵蓋 5 種經典運鏡 Shot 參數設定表（Hero, Close-up, Pan/Track, Action Cut, Outro）
    - 涵蓋核心提示詞範本（Prompt / Negative Prompt）
    """
    errors: List[str] = []
    if not text.strip():
        return ["檔案內容為空"]

    # 1. 驗證 5 種經典 Shot 規範表格
    for num, shot_name in EXPECTED_CINEMATIC_SHOTS:
        # 表格中應包含如：| **1. Hero Shot** ...
        pattern = rf"\|\s*\*\*{num}\.\s*{re.escape(shot_name)}\*\*"
        if not re.search(pattern, text):
            errors.append(f"經典 Shot 參數表中缺少鏡頭 {num}：{shot_name}")

    # 檢查表格參數欄位
    required_columns = [
        "鏡頭類型",
        "典型時長",
        "放大倍率",
        "攝影機角度",
        "攝影機運動",
        "景深與焦點位置",
        "UI 行為與動作",
    ]
    for col in required_columns:
        if col not in text:
            errors.append(f"經典 Shot 參數設定表缺少必要欄位：{col}")

    # 2. 驗證提示詞範本
    if not re.search(r"AI 視訊模型提示詞範本|Visual Prompts", text):
        errors.append("缺少 AI 視訊模型提示詞範本（Visual Prompts）章節")

    required_prompt_sections = [
        ("Hero Shot", r"Hero Shot.*提示詞範本"),
        ("Close-up Shot", r"Close-up.*提示詞範本"),
        ("Outro Shot", r"Outro.*提示詞範本"),
    ]
    for name, pattern in required_prompt_sections:
        if not re.search(pattern, text):
            errors.append(f"缺少 {name} 之提示詞範本區塊")

    # 檢查是否包含具體 Prompt 與 Negative Prompt 代碼塊
    if text.count("Prompt:") < 3:
        errors.append("提示詞範本中的 `Prompt:` 區塊少於 3 組")
    if "Negative Prompt:" not in text:
        errors.append("提示詞範本缺少反向提示詞（Negative Prompt）規範")

    return errors


def verify_video_studio_harness(text: str) -> List[str]:
    """
    驗證 templates/video-studio-harness.md：
    - 涵蓋 seek(t) 時間函式契約與時間純函數哲學 (V = f(t))
    - 涵蓋四大反 AI 視覺套路禁令（Anti-AI Slop Rules）
    """
    errors: List[str] = []
    if not text.strip():
        return ["檔案內容為空"]

    # 1. 驗證 seek(t) 時間函式契約
    seek_count = len(re.findall(r"seek\(t\)", text))
    if seek_count < 2:
        errors.append(f"未完整建立 `seek(t)` 確定性時間函式契約（僅出現 {seek_count} 次，預期 >= 2 次）")

    if not re.search(r"f\(t|\bf\(t,", text):
        errors.append("缺少時間純函數哲學宣告（`V = f(t)` 或 `Frame = f(t, state)`）")

    if not re.search(r"window\.seek|seek\(targetTimeInSeconds\)", text):
        errors.append("缺少全局 `window.seek(t)` 外部呼叫契約宣告")

    if not re.search(r"確定性|Deterministic", text, re.I):
        errors.append("缺少渲染「確定性」（Deterministic）原則宣告")

    # 2. 驗證四大反 AI 視覺套路禁令
    for ban_num, ban_title in EXPECTED_ANTI_SLOP_BANS:
        # 表格中應包含如：| **禁令 1：漸層置中標題** |
        pattern = rf"\*\*禁令\s*{ban_num}[:：]\s*{re.escape(ban_title)}\*\*"
        if not re.search(pattern, text):
            errors.append(f"缺少四大反 AI 罐頭套路之「禁令 {ban_num}：{ban_title}」")

    # 檢查禁令表格要素
    ban_table_headers = ["禁令類型", "罐頭視覺特徵", "拒絕理由", "正確替代方案"]
    for header in ban_table_headers:
        if header not in text:
            errors.append(f"反 AI 罐頭套路禁令表格缺少欄位：{header}")

    return errors


def verify_all_motion_specs(repo_root: Optional[Path] = None) -> Tuple[bool, Dict[str, List[str]]]:
    """執行全數動態視覺字典與 Code-as-Video 規範之外部裁判驗證。"""
    root = repo_root or find_repo_root()
    results: Dict[str, List[str]] = {}

    targets = [
        ("docs/cinetic-motion-dictionary.md", verify_cinetic_motion_dictionary),
        ("docs/motion-prompt-cheatsheet.md", verify_motion_prompt_cheatsheet),
        ("docs/cinematic-shot-camera-guide.md", verify_cinematic_shot_camera_guide),
        ("templates/video-studio-harness.md", verify_video_studio_harness),
    ]

    for rel_path, verifier in targets:
        full_path = root / rel_path
        if not full_path.exists():
            results[rel_path] = [f"目標檔案不存在：{rel_path}"]
        else:
            content = full_path.read_text(encoding="utf-8")
            results[rel_path] = verifier(content)

    all_passed = all(len(errs) == 0 for errs in results.values())
    return all_passed, results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="動態視覺字典（Cinetic／Motion Prompt／cinematic-shot）與 Code-as-Video 規範之外部裁判結構驗證器"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="專案根目錄（預設自動搜尋包含 notes/ 與 docs/ 之根目錄）",
    )
    args = parser.parse_args(argv)

    root = find_repo_root(args.repo_root)
    print(f"[*] 執行外部裁判規格結構校驗，專案根目錄：{root}")

    all_passed, results = verify_all_motion_specs(root)

    for rel_path, errs in results.items():
        if errs:
            print(f"\n[FAIL] ❌ {rel_path} 發現 {len(errs)} 項規格缺陷：")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"[PASS] ✅ {rel_path} 結構與規格完全相符")

    if all_passed:
        print("\n[SUCCESS] 🎉 全數動態視覺字典與 Code-as-Video 規範文件均通過外部裁判結構驗證！")
        return 0
    else:
        print("\n[ERROR] 外部裁判驗證未通過，請依上述錯誤修正文件。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
