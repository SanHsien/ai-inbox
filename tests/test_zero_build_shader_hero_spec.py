#!/usr/bin/env python3
"""
tests/test_zero_build_shader_hero_spec.py
檢查 docs/zero-build-shader-hero-sections-spec.md（T-20261031-04）沒有再犯第一版被退回的錯誤。

這是文件，沒有行為可以跑；所以這裡只擋「已知會再犯的錯」，每一條都附反例（把壞內容塞進去必須被抓到）：
- 捏造的作品名只能出現在「勘誤」段；
- 沒有來源的效能數字不可回到正文；
- 有引用原作 repo 的特定 commit、授權與作者不確定的聲明；
- 名單數字自洽（10 + 60 = 70，清單長度與宣稱一致）；
- 內部連結指向的檔案存在；
- 引用的外部來源都出現在「來源」段，且標明查證日期。
外部事實（原作的目錄清單、README 內容）無法在離線 CI 重新查證，已在文件第 0、9 節寫明查證方式與日期。
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = REPO_ROOT / "docs" / "zero-build-shader-hero-sections-spec.md"

FABRICATED = [
    "Geometric Void", "Monolith", "Chrome Ripple", "Mercury Waves", "Cyber Platinum", "Cyber Swarm",
    "Starfield Drift", "Gravity Well", "Matrix Terminal", "ASCII Fluid", "Retro Cyber",
]
UNSOURCED_NUMBERS = [r"80\s*%", r"GPU 負載率", r"< ?15 ?\\?%", r"120\s*ms", r"50\s*MB", r"58\s*~\s*60\s*FPS", r"60 FPS 的"]
COMMIT = "7b019b5debdf0b2b0e92eb475c8d76793162103f"


def split_sections(text: str) -> dict:
    parts = re.split(r"(?m)^(### .*|## .*)$", text)
    sections = {}
    for i in range(1, len(parts), 2):
        sections[parts[i].strip()] = parts[i + 1]
    return sections


def fabricated_outside_erratum(text: str) -> List[str]:
    """回傳出現在「勘誤」小節之外的捏造作品名。"""
    bad = []
    for head, body in split_sections(text).items():
        if "勘誤" in head:
            continue
        for name in FABRICATED:
            if re.search(re.escape(name), body):
                bad.append(f"{name}（在 {head}）")
    return bad


def unsourced_numbers(text: str) -> List[str]:
    return [p for p in UNSOURCED_NUMBERS if re.search(p, text)]


class TestSpec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SPEC.is_file():
            raise AssertionError(f"規範不存在：{SPEC}")
        cls.text = SPEC.read_text(encoding="utf-8")

    def test_no_fabricated_names_in_body(self):
        self.assertEqual(fabricated_outside_erratum(self.text), [])
        # 勘誤段本身必須存在並明說「查無」
        errata = [b for h, b in split_sections(self.text).items() if "勘誤" in h]
        self.assertEqual(len(errata), 1)
        self.assertIn("查無", errata[0])
        for name in FABRICATED:
            self.assertIn(name, errata[0], f"勘誤段沒有列出 {name}")

    def test_checker_catches_injected_fabricated_name(self):
        bad = self.text.replace("## 4. 本 repo 的 Zero-Build 生命週期規範", "## 4. 本 repo 的 Zero-Build 生命週期規範\n\n代表作：Cyber Swarm。\n", 1)
        self.assertNotEqual(bad, self.text)
        self.assertTrue(fabricated_outside_erratum(bad))

    def test_no_unsourced_performance_numbers(self):
        self.assertEqual(unsourced_numbers(self.text), [])
        self.assertTrue(unsourced_numbers(self.text + "\nGPU 負載率 < 15%\n"))

    def test_cites_pinned_upstream_commit_and_license(self):
        self.assertIn("diiviikk5/Hacktemplates", self.text)
        self.assertEqual(self.text.count(COMMIT) >= 2, True)
        self.assertRegex(self.text, r"MIT")
        self.assertIn("Copyright (c) 2026 diiviikk5", self.text)
        self.assertRegex(self.text, r"(?s)2026-11-02")

    def test_author_identity_is_stated_as_uncertain(self):
        head = next(b for h, b in split_sections(self.text).items() if h.startswith("## 0."))
        row = next(line for line in head.splitlines() if line.startswith("| 作者"))
        self.assertIn("未確定", row)
        self.assertIn("diiviikk5", row)
        self.assertNotRegex(self.text, r"印度前端開發者 Manas")

    def test_does_not_claim_single_file_or_double_click_universally(self):
        self.assertIn("不是單檔", self.text)
        self.assertIn("http://", self.text)
        self.assertNotRegex(self.text, r"雙擊即開，不發起")
        self.assertNotIn("客觀真實性", self.text)

    def test_numbers_are_self_consistent(self):
        no_image = re.search(r"\*\*不含圖檔路徑（(\d+)）\*\*：([^\n]+)", self.text)
        with_image = re.search(r"\*\*含圖檔路徑（(\d+)）\*\*：([^\n]+)", self.text)
        self.assertIsNotNone(no_image)
        self.assertIsNotNone(with_image)
        a = [x.strip() for x in no_image.group(2).rstrip("。").split("、")]
        b = [x.strip() for x in with_image.group(2).rstrip("。").split("、")]
        self.assertEqual(len(a), int(no_image.group(1)))
        self.assertEqual(len(b), int(with_image.group(1)))
        self.assertEqual(len(a) + len(b), 70)
        self.assertEqual(len(set(a) | set(b)), 70, "清單內有重複或遺漏")
        self.assertEqual(sorted(a), a)
        self.assertEqual(sorted(b), b)
        # README 具名的作品都必須在 70 個目錄清單中
        readme_named = ["vermilion", "ashborne", "event-horizon", "mercury", "currents", "desert-dragon", "starmind",
                        "respite", "orbit-ascii", "vapor", "halftone", "fold", "furnace", "fluted", "relic", "ronin",
                        "signal", "sentinel"]
        for n in readme_named:
            self.assertIn(n, set(a) | set(b), f"README 具名的 {n} 不在清單中")

    def test_internal_links_resolve(self):
        for target in re.findall(r"\]\((\.{1,2}/[^)#\s]+)", self.text):
            path = (SPEC.parent / target).resolve()
            self.assertTrue(path.exists(), f"連結目標不存在：{target}")

    def test_sources_section_lists_dates_and_unverified_items(self):
        src = next(b for h, b in split_sections(self.text).items() if h.startswith("## 9."))
        self.assertIn("查證日期 2026-11-02", [h for h in split_sections(self.text) if h.startswith("## 9.")][0])
        for url in ("registry.khronos.org/webgl/specs/latest/1.0", "WEBGL_lose_context", "mediaqueries-5",
                    "intersection-observer", "page-visibility-2", "thebookofshaders.com/13"):
            self.assertIn(url, src)
        self.assertIn("未驗證", src)
        self.assertIn("dvklab.vercel.app", src)

    def test_lifecycle_requirements_mention_restore_rebuild_dispose_and_errors(self):
        body = next(b for h, b in split_sections(self.text).items() if h.startswith("## 4."))
        for needle in ("重新 compile", "preventDefault", "COMPILE_STATUS", "LINK_STATUS", "deleteProgram",
                       "prefers-reduced-motion", "只丟掉參考"):
            self.assertIn(needle, body)


if __name__ == "__main__":
    unittest.main()
