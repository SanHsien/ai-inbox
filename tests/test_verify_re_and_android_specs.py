#!/usr/bin/env python3
"""
tests/test_verify_re_and_android_specs.py
測試 tools/verify_re_and_android_specs.py 外部裁判驗證器（相容 unittest 與 pytest）：
1. 真實 4 份規格與證據文件全數驗證通過。
2. 逆向工程流水線三階段（觀測、結構、重造）缺失反例攔截。
3. 逆向工程流水線未明確標註 desktop-sense 為「選用、未採用」反例攔截。
4. 逆向工程流水線 Cleanroom 無菌室規範缺失反例攔截。
5. REA 沙盒實測證據 SHA-256 比對或 MATCH 缺失反例攔截。
6. REA 沙盒實測證據 ASAR 解包統計或原始碼隔離政策缺失反例攔截。
7. REA 沙盒實測證據系統 PATH 零污染或全域登錄檔零變更結論缺失反例攔截。
8. Android 官方 Skills 數量不足 33 個或核心關鍵技能遺漏反例攔截。
9. Android 官方 Skills XML 轉 Compose 或 Play Billing 合規防線缺失反例攔截。
10. Android CLI 在 Windows 11 之 Registry PATH 違規或超過 1 GB 硬閘門缺失反例攔截。
11. CLI main() 執行成功 (exit 0) 與指定無效目錄之失敗 (exit 1) 驗證。
12. 驗證直接傳遞多行長字串時具備 Linux CI ENAMETOOLONG 安全防護。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_re_and_android_specs as vre  # noqa: E402


class TestVerifyReAndAndroidSpecs(unittest.TestCase):
    def test_real_specs_all_pass(self):
        """1. 驗證現存於 repo 的真實 4 份文件全數通過外部裁判檢查。"""
        all_passed, results = vre.verify_all_specs(REPO_ROOT)
        self.assertTrue(all_passed, f"真實文件驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤")

    def test_re_pipeline_missing_stages(self):
        """2. 反例攔截：逆向流水線三階段（觀測行為、理解結構、重造功能）缺失。"""
        raw = (REPO_ROOT / "docs" / "reverse-engineering-pipeline-spec.md").read_text(encoding="utf-8")

        # 缺少行為觀測
        bad_stage1 = (
            raw.replace("階段一：動態行為觀測", "階段一：一般啟動")
            .replace("階段一：行為觀測", "階段一：一般啟動")
            .replace("動態行為觀測", "一般啟動")
            .replace("行為觀測", "一般啟動")
            .replace("Behavior Observation", "Generic Startup")
        )
        errors1 = vre.verify_re_pipeline_spec(bad_stage1)
        self.assertTrue(any("階段一" in e or "行為觀測" in e for e in errors1), f"未攔截階段一缺失：{errors1}")

        # 缺少結構逆向
        bad_stage2 = (
            raw.replace("階段二：結構反編譯與靜態分析", "階段二：軟體安裝")
            .replace("階段二：結構逆向", "階段二：軟體安裝")
            .replace("結構反編譯", "軟體安裝")
            .replace("結構逆向", "軟體安裝")
            .replace("Structural Decompilation", "Software Setup")
        )
        errors2 = vre.verify_re_pipeline_spec(bad_stage2)
        self.assertTrue(any("階段二" in e or "結構" in e for e in errors2), f"未攔截階段二缺失：{errors2}")

        # 缺少無菌重造
        bad_stage3 = (
            raw.replace("階段三：無菌室乾淨重造", "階段三：日常操作")
            .replace("階段三：無菌重造", "階段三：日常操作")
            .replace("無菌室乾淨重造", "日常操作")
            .replace("無菌重造", "日常操作")
            .replace("Cleanroom Re-implementation", "Daily Operation")
            .replace("Cleanroom", "Generic")
        )
        errors3 = vre.verify_re_pipeline_spec(bad_stage3)
        self.assertTrue(any("階段三" in e or "重造" in e for e in errors3), f"未攔截階段三缺失：{errors3}")

    def test_re_pipeline_desktop_sense_rejection(self):
        """3. 反例攔截：未將 desktop-sense 明確標註為「選用、未採用」或刪除該項。"""
        raw = (REPO_ROOT / "docs" / "reverse-engineering-pipeline-spec.md").read_text(encoding="utf-8")

        # 刪除 desktop-sense
        no_ds = raw.replace("desktop-sense", "visual-sense")
        errors_no_ds = vre.verify_re_pipeline_spec(no_ds)
        self.assertTrue(any("desktop-sense" in e for e in errors_no_ds), f"未攔截 desktop-sense 缺失：{errors_no_ds}")

        # 改為已採用
        adopted_ds = raw.replace("【選用、未採用】", "【核心採用】").replace("選用、未採用", "核心採用")
        errors_adopted = vre.verify_re_pipeline_spec(adopted_ds)
        self.assertTrue(any("選用、未採用" in e for e in errors_adopted), f"未攔截 desktop-sense 標記為未採用：{errors_adopted}")

    def test_re_pipeline_cleanroom_spec_missing(self):
        """4. 反例攔截：Cleanroom 無菌室規範或防版權污染聲明缺失。"""
        raw = (REPO_ROOT / "docs" / "reverse-engineering-pipeline-spec.md").read_text(encoding="utf-8")

        no_cleanroom = raw.replace("Cleanroom", "Standard").replace("無菌室", "標準流程").replace("防版權污染", "一般注意事項")
        errors = vre.verify_re_pipeline_spec(no_cleanroom)
        self.assertTrue(any("Cleanroom" in e or "無菌" in e for e in errors), f"未攔截 Cleanroom 規範缺失：{errors}")

    def test_rea_sandbox_sha256_evidence_missing(self):
        """5. 反例攔截：JDK 21 / Ghidra 之 SHA-256 雜湊或 MATCH 比對結果缺失。"""
        raw = (REPO_ROOT / "docs" / "rea-sandbox-evaluation-evidence.md").read_text(encoding="utf-8")

        # 移除 MATCH 比對結果
        no_match = raw.replace("`MATCH`", "`FAILED`").replace("完全一致", "不相符")
        errors = vre.verify_rea_sandbox_evidence(no_match)
        self.assertTrue(any("SHA-256" in e or "MATCH" in e for e in errors), f"未攔截 MATCH 比對缺失：{errors}")

        # 移除 SHA-256 雜湊碼
        no_hash = raw.replace("f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e", "none")
        no_hash = no_hash.replace("2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67", "none")
        errors_hash = vre.verify_rea_sandbox_evidence(no_hash)
        self.assertTrue(any("SHA-256" in e for e in errors_hash), f"未攔截 SHA-256 雜湊碼缺失：{errors_hash}")

    def test_rea_sandbox_asar_and_isolation_missing(self):
        """6. 反例攔截：Electron app.asar 解包統計或原始碼隔離政策缺失。"""
        raw = (REPO_ROOT / "docs" / "rea-sandbox-evaluation-evidence.md").read_text(encoding="utf-8")

        # 缺少解包統計
        no_stats = raw.replace("node_count", "item_a").replace("occurrence_count", "item_b").replace("1,221", "0")
        errors_stats = vre.verify_rea_sandbox_evidence(no_stats)
        self.assertTrue(any("app.asar" in e or "解包統計" in e for e in errors_stats), f"未攔截解包統計缺失：{errors_stats}")

        # 缺少隔離政策
        no_isolation = (
            raw.replace("沙盒暫存區", "正式專案目錄")
            .replace("%TEMP%", "C:\\Projects")
            .replace("未寫入任何 Git 倉庫", "已 commit 入庫")
            .replace("嚴禁 commit", "直接 commit")
        )
        errors_iso = vre.verify_rea_sandbox_evidence(no_isolation)
        self.assertTrue(any("隔離" in e or "Git" in e for e in errors_iso), f"未攔截原始碼隔離政策缺失：{errors_iso}")

    def test_rea_sandbox_path_zero_pollution_missing(self):
        """7. 反例攔截：系統 PATH 零污染、全域登錄檔零變更結論缺失。"""
        raw = (REPO_ROOT / "docs" / "rea-sandbox-evaluation-evidence.md").read_text(encoding="utf-8")

        bad_path = raw.replace("系統環境變數 PATH：零變更", "系統環境變數 PATH：已永久覆寫")
        errors = vre.verify_rea_sandbox_evidence(bad_path)
        self.assertTrue(any("PATH" in e or "環境清潔度" in e for e in errors), f"未攔截 PATH 零污染結論缺失：{errors}")

    def test_android_skills_count_and_key_skills(self):
        """8. 反例攔截：Android 官方 Skills 清單不足 33 個或核心技能遺漏。"""
        raw = (REPO_ROOT / "docs" / "android-official-skills-anti-hallucination.md").read_text(encoding="utf-8")

        # 破壞數量宣告
        bad_claim = raw.replace("33 個 Skills", "20 個 Skills").replace("33 個", "20 個")
        # 刪減表格列
        lines = [line for line in bad_claim.splitlines() if not line.startswith("| 3")]
        bad_count_text = "\n".join(lines)
        errors_count = vre.verify_android_skills_anti_hallucination(bad_count_text)
        self.assertTrue(any("不足 33 個" in e for e in errors_count), f"未攔截 Skills 數量不足：{errors_count}")

        # 遺漏核心技能
        no_compose_skill = raw.replace("migrate-xml-views-to-jetpack-compose", "legacy-converter")
        errors_key = vre.verify_android_skills_anti_hallucination(no_compose_skill)
        self.assertTrue(any("遺漏核心關鍵技能" in e for e in errors_key), f"未攔截關鍵技能遺漏：{errors_key}")

    def test_android_skills_table_padding_and_duplicates_rejected(self):
        """反例：灌水(重複編號/缺 SKILL.md 路徑的數字列)不得湊成 33 個。"""
        raw = (REPO_ROOT / "docs" / "android-official-skills-anti-hallucination.md").read_text(encoding="utf-8")
        self.assertEqual(vre.verify_android_skills_anti_hallucination(raw), [])
        lines = raw.splitlines()
        # 把最後一個編號列改成與前一列相同編號(重複)
        idx = [i for i, l in enumerate(lines) if l.startswith("| 33 |")][0]
        dup = "\n".join(lines[:idx] + [lines[idx].replace("| 33 |", "| 32 |", 1)] + lines[idx + 1:])
        self.assertTrue(any("不足 33 個" in e for e in vre.verify_android_skills_anti_hallucination(dup)))
        # 移除 SKILL.md 路徑的數字列不算數
        nopath = "\n".join(l.replace("SKILL.md", "README.txt") if l.startswith("| 5 |") else l for l in lines)
        self.assertTrue(any("不足 33 個" in e for e in vre.verify_android_skills_anti_hallucination(nopath)))

    def test_android_skills_compose_and_play_billing_guardrails(self):
        """9. 反例攔截：XML 轉 Compose 防幻覺或 Play Billing 合規防線缺漏。"""
        raw = (REPO_ROOT / "docs" / "android-official-skills-anti-hallucination.md").read_text(encoding="utf-8")

        # 缺少 findViewById 禁令
        no_toxic_ban = raw.replace("findViewById", "someViewFinder")
        errors_compose = vre.verify_android_skills_anti_hallucination(no_toxic_ban)
        self.assertTrue(any("Compose" in e or "findViewById" in e for e in errors_compose), f"未攔截 Compose 規範缺失：{errors_compose}")

        # 缺少 AcknowledgePurchaseParams
        no_ack = raw.replace("AcknowledgePurchaseParams", "SomeOtherApi")
        errors_billing = vre.verify_android_skills_anti_hallucination(no_ack)
        self.assertTrue(any("Play Billing" in e or "AcknowledgePurchaseParams" in e for e in errors_billing), f"未攔截 Play Billing 缺失：{errors_billing}")

    def test_android_cli_registry_and_size_limit_gates(self):
        """10. 反例攔截：Registry PATH 違規攔截或超過 1 GB 下載硬閘門缺漏。"""
        raw = (REPO_ROOT / "docs" / "android-cli-plugin-windows-validation.md").read_text(encoding="utf-8")

        # 缺少 Registry 違規記錄
        no_reg = (
            raw.replace("HKCU\\Environment", "TEMP_ENV")
            .replace("HKCU", "TEMP_ENV")
            .replace("強制修改系統註冊表", "正常註冊")
            .replace("Registry Violation", "Normal Operation")
        )
        errors_reg = vre.verify_android_cli_validation(no_reg)
        self.assertTrue(any("Registry" in e for e in errors_reg), f"未攔截 Registry 違規缺漏：{errors_reg}")

        # 缺少 1 GB 硬閘門
        no_size_gate = (
            raw.replace("硬閘門觸發停下", "順利下載完成")
            .replace("需要下載超過 1 GB 就停在那一項", "全數下載完成")
            .replace("超過 1 GB 就停在那一項", "全數下載完成")
            .replace("1.5 GB ~ 3.5 GB", "10 MB")
            .replace("1 GB", "10 MB")
        )
        errors_size = vre.verify_android_cli_validation(no_size_gate)
        self.assertTrue(any("超過 1 GB" in e or "硬閘門" in e for e in errors_size), f"未攔截 1 GB 硬閘門缺漏：{errors_size}")

    def test_cli_main_success_and_failure(self):
        """11. 驗證 CLI main() 執行成功 (exit 0) 與無效目錄 (exit 1)。"""
        exit_code = vre.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(exit_code, 0, "CLI 在合法 repo 應返回 0")

        # 指向非 repo 根目錄應返回 1
        empty_dir = REPO_ROOT / "assets"
        exit_code_fail = vre.main(["--repo-root", str(empty_dir)])
        self.assertEqual(exit_code_fail, 1, "CLI 在無效目錄應返回 1")

    def test_enametoolong_safe_string_handling(self):
        """12. 驗證直接傳遞多行或超長字串至驗證函式，不觸發 ENAMETOOLONG 並正常工作。"""
        # 生成一個長度 > 4096 的多行字串，模擬真實大型 markdown
        huge_multiline_text = ("# Fake Document\n\n" + "This is a long content line.\n" * 200)
        self.assertGreater(len(huge_multiline_text), 4096)

        # 測試 load_content 安全性
        content = vre.load_content(huge_multiline_text)
        self.assertEqual(content, huge_multiline_text)

        # 測試直接傳給驗證函式不會拋出 OSError: [Errno 36] File name too long
        errors = vre.verify_re_pipeline_spec(huge_multiline_text)
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) > 0)  # 假文件應攔截到錯誤


if __name__ == "__main__":
    unittest.main()
