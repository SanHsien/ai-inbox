#!/usr/bin/env python3
"""
tests/test_verify_motion_and_video_specs.py
測試 tools/verify_motion_and_video_specs.py 動態視覺字典與 Code-as-Video 外部裁判驗證器：
1. 真實 4 份文件全數驗證通過。
2. cinetic 技法字典分類缺漏或宣告總量不符反例攔截。
3. cinetic 技法字典 60 FPS Easing / Spring 時間配方缺漏反例攔截。
4. motion-prompt 動效列數不足 (< 144 款) 或套件缺失反例攔截。
5. motion-prompt 表格空白單元格反例攔截。
6. cinematic-shot 經典運鏡 Shot 缺失或提示詞範本缺漏反例攔截。
7. video-studio-harness seek(t) 時間函式契約或反 AI 套路禁令缺漏反例攔截。
8. CLI main() 執行成功與退出碼驗證。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_motion_and_video_specs as vms  # noqa: E402


class TestVerifyMotionAndVideoSpecs(unittest.TestCase):
    def test_real_motion_specs_all_pass(self):
        """1. 驗證現存於 repo 的真實 4 份文件全數通過驗證。"""
        all_passed, results = vms.verify_all_motion_specs(REPO_ROOT)
        self.assertTrue(all_passed, f"真實文件驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤")

    def test_cinetic_missing_category_or_count_mismatch(self):
        """2. 反例攔截：cinetic 字典分類缺漏、子章節缺失或技法列數不足。"""
        raw = (REPO_ROOT / "docs" / "cinetic-motion-dictionary.md").read_text(encoding="utf-8")

        # 破壞分類代碼：將 opening_hook 替換為 custom_hook
        bad_cat_text = raw.replace("`opening_hook`", "`custom_hook`")
        errors = vms.verify_cinetic_motion_dictionary(bad_cat_text)
        self.assertTrue(
            any("opening_hook" in e for e in errors),
            f"未攔截分類代碼 opening_hook 缺失：{errors}",
        )

        # 破壞總計宣告
        no_summary_text = raw.replace("14 大分類、273 種動態技法", "多種分類與動畫技法")
        errors_summary = vms.verify_cinetic_motion_dictionary(no_summary_text)
        self.assertTrue(
            any("核心總計規格" in e for e in errors_summary),
            f"未攔截總計宣告缺失：{errors_summary}",
        )

    def test_cinetic_missing_easing_or_spring_recipes(self):
        """3. 反例攔截：cinetic 字典缺少 60 FPS 基準、Easing 曲線或 Spring 預設。"""
        raw = (REPO_ROOT / "docs" / "cinetic-motion-dictionary.md").read_text(encoding="utf-8")

        # 移除 Easing Tokens 中的 out 與 exit
        bad_easing = raw.replace("| `out` |", "| `custom_out` |").replace("| `exit` |", "| `custom_exit` |")
        errors_easing = vms.verify_cinetic_motion_dictionary(bad_easing)
        self.assertTrue(
            any("out" in e or "exit" in e for e in errors_easing),
            f"未攔截 Easing Token 缺失：{errors_easing}",
        )

        # 移除 Spring Presets 中的 snap 與 micro
        bad_spring = raw.replace("| `snap` |", "| `custom_snap` |").replace("| `micro` |", "| `custom_micro` |")
        errors_spring = vms.verify_cinetic_motion_dictionary(bad_spring)
        self.assertTrue(
            any("snap" in e or "micro" in e for e in errors_spring),
            f"未攔截 Spring Presets 缺失：{errors_spring}",
        )

    def test_motion_prompt_insufficient_rows_or_missing_packs(self):
        """4. 反例攔截：motion-prompt 動效列不足 144 款或套件缺失。"""
        raw = (REPO_ROOT / "docs" / "motion-prompt-cheatsheet.md").read_text(encoding="utf-8")

        # 刪減 1 款動效（刪除 #144 列）
        bad_rows_text = raw.replace("| **#144** |", "| --#144-- |")
        errors = vms.verify_motion_prompt_cheatsheet(bad_rows_text)
        self.assertTrue(
            any("動效列數量不符" in e or "動效編號缺漏" in e for e in errors),
            f"未攔截動效列不足 144 款：{errors}",
        )

        # 缺少套件 Pack: motion2
        no_pack_text = raw.replace("Pack: motion2", "Pack: experimental")
        errors_pack = vms.verify_motion_prompt_cheatsheet(no_pack_text)
        self.assertTrue(
            any("motion2" in e for e in errors_pack),
            f"未攔截套件 motion2 缺失：{errors_pack}",
        )

    def test_motion_prompt_empty_cells_detected(self):
        """5. 反例攔截：motion-prompt 表格單元格出現空白。"""
        raw = (REPO_ROOT / "docs" / "motion-prompt-cheatsheet.md").read_text(encoding="utf-8")

        # 將 #001 的「對 AI 的說法範例」單元格清空
        bad_cell_text = raw.replace(
            "請用 Pop-in 讓 Logo 出現，大約 0.4 秒，Overshoot 只要一點點。",
            "   ",
        )
        errors = vms.verify_motion_prompt_cheatsheet(bad_cell_text)
        self.assertTrue(
            any("空白單元格" in e and "#001" in e for e in errors),
            f"未攔截 #001 空白單元格：{errors}",
        )

    def test_cinematic_shot_missing_shots_or_prompts(self):
        """6. 反例攔截：cinematic-shot 缺少 5 種經典 Shot 或提示詞範本。"""
        raw = (REPO_ROOT / "docs" / "cinematic-shot-camera-guide.md").read_text(encoding="utf-8")

        # 缺少 Outro Shot
        no_outro = raw.replace("| **5. Outro Shot**", "| **5. Conclusion**")
        errors_shot = vms.verify_cinematic_shot_camera_guide(no_outro)
        self.assertTrue(
            any("Outro Shot" in e for e in errors_shot),
            f"未攔截 Outro Shot 缺失：{errors_shot}",
        )

        # 缺少 Negative Prompt
        no_neg_prompt = raw.replace("Negative Prompt:", "Avoid Things:")
        errors_neg = vms.verify_cinematic_shot_camera_guide(no_neg_prompt)
        self.assertTrue(
            any("Negative Prompt" in e for e in errors_neg),
            f"未攔截反向提示詞規範缺失：{errors_neg}",
        )

    def test_video_studio_harness_missing_seek_or_anti_slop(self):
        """7. 反例攔截：video-studio-harness 缺少 seek(t) 契約或反 AI 套路禁令。"""
        raw = (REPO_ROOT / "templates" / "video-studio-harness.md").read_text(encoding="utf-8")

        # 移除 seek(t) 契約
        no_seek = raw.replace("seek(t)", "render()")
        errors_seek = vms.verify_video_studio_harness(no_seek)
        self.assertTrue(
            any("seek(t)" in e for e in errors_seek),
            f"未攔截 seek(t) 契約缺失：{errors_seek}",
        )

        # 移除禁令 1：漸層置中標題
        no_ban1 = raw.replace("禁令 1：漸層置中標題", "建議 1：標題排版優化")
        errors_ban = vms.verify_video_studio_harness(no_ban1)
        self.assertTrue(
            any("禁令 1" in e for e in errors_ban),
            f"未攔截反 AI 套路禁令 1 缺失：{errors_ban}",
        )

    def test_cli_main_exit_codes(self):
        """8. 測試 CLI main() 在根目錄執行傳回 0，傳入空目錄或錯誤目錄傳回 1。"""
        code_success = vms.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(code_success, 0, "CLI 於標準專案根目錄執行應回傳 0")

        # 測試不存在的目錄
        code_fail = vms.main(["--repo-root", str(REPO_ROOT / "non_existing_dir")])
        self.assertEqual(code_fail, 1, "CLI 於無效目錄執行應回傳 1")


if __name__ == "__main__":
    unittest.main()
