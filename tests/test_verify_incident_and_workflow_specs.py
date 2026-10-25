#!/usr/bin/env python3
"""
tests/test_verify_incident_and_workflow_specs.py
測試 tools/verify_incident_and_workflow_specs.py 外部裁判驗證器：
1. 真實文件全數驗證通過。
2. zeabur 稽核報告首行結論缺失反例攔截。
3. zeabur 稽核報告疑似高危金鑰暴露反例攔截。
4. zeabur 稽核報告缺少掃描或授權表格反例攔截。
5. 應變清單範本必備段落缺失或勾選項不足 (< 3) 反例攔截。
6. WebToApp 評估文件結論缺失或權限/簽名分析缺漏反例攔截。
7. WebToApp 接案流程缺少六大步驟或四大免責條款反例攔截。
8. CLI main() 執行成功與失敗退出碼驗證。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_incident_and_workflow_specs as vsp  # noqa: E402


class TestVerifyIncidentAndWorkflowSpecs(unittest.TestCase):
    def test_real_specs_all_pass(self):
        """1. 驗證現存於 repo 的真實文件全數通過檢查。"""
        all_passed, results = vsp.verify_all_specs(REPO_ROOT)
        self.assertTrue(all_passed, f"真實文件驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤")

    def test_zeabur_missing_conclusion_first_line(self):
        """2. 反例攔截：zeabur 報告首行非『結論：(有使用|無使用) Zeabur』。"""
        raw = (REPO_ROOT / "docs" / "zeabur-incident-credential-audit.md").read_text(encoding="utf-8")
        # 破壞首行
        bad_text = raw.replace("結論：無使用 Zeabur", "# Zeabur 稽核報告草稿", 1)
        errors = vsp.verify_zeabur_audit(bad_text)
        self.assertTrue(any("首行不符合規範" in e for e in errors), f"未攔截到首行結論缺失：{errors}")

    def test_zeabur_secret_leak_detected(self):
        """3. 反例攔截：zeabur 報告疑似暴露真實金鑰（ghp_、sk-、AKIA）。"""
        raw = (REPO_ROOT / "docs" / "zeabur-incident-credential-audit.md").read_text(encoding="utf-8")
        
        # 注入假金鑰
        leaks = [
            ("ghp_" + "12345678901234567890abcdefgh", "GitHub token"),
            ("sk-" + "live_12345678901234567890abcdef", "Anthropic / OpenAI key"),
            ("AKIA" + "IOSFODNN7EXAMPLE", "AWS access key"),
        ]
        for fake_secret, label in leaks:
            bad_text = raw + f"\n\n測試金鑰暴露：{fake_secret}\n"
            errors = vsp.verify_zeabur_audit(bad_text)
            self.assertTrue(
                any(label in e or fake_secret[:6] in e for e in errors),
                f"未能成功攔截金鑰暴露 {label}：{errors}",
            )

    def test_zeabur_missing_audit_tables(self):
        """4. 反例攔截：zeabur 報告缺少倉庫掃描或 GitHub 授權稽核表格。"""
        raw = (REPO_ROOT / "docs" / "zeabur-incident-credential-audit.md").read_text(encoding="utf-8")
        # 移除倉庫掃描表格
        no_repo_table = raw.replace("## 2. 本機 `C:\\GitHub` 全專案倉庫掃描結果", "## 2. 略過掃描")
        errors = vsp.verify_zeabur_audit(no_repo_table)
        self.assertTrue(any("倉庫掃描" in e for e in errors), f"未攔截倉庫掃描表格缺失：{errors}")

        # 移除 GitHub 授權表格
        no_gh_table = raw.replace("## 3. GitHub 帳號與倉庫授權安全稽核", "## 3. 略過授權稽核")
        errors_gh = vsp.verify_zeabur_audit(no_gh_table)
        self.assertTrue(any("GitHub" in e for e in errors_gh), f"未攔截 GitHub 授權表格缺失：{errors_gh}")

    def test_breach_template_missing_section_or_insufficient_items(self):
        """5. 反例攔截：應變清單段落缺失或勾選項不足 (< 3)。"""
        raw = (REPO_ROOT / "templates" / "platform-breach-response.md").read_text(encoding="utf-8")

        # 缺少「遷移評估」段落
        missing_sec_text = raw.replace("## 遷移評估", "## 備援評估")
        errors = vsp.verify_platform_breach_response(missing_sec_text)
        self.assertTrue(any("缺少必備應變段落「遷移評估」" in e for e in errors), f"未攔截段落缺失：{errors}")

        # 「立即處置」段落的 - [ ] 刪減至僅剩 2 項
        reduced_items_text = raw.replace("- [ ] 終止平台控制台的所有活躍登入工作階段", "").replace("- [ ] 輪換（先撤銷再重建）", "")
        errors_count = vsp.verify_platform_breach_response(reduced_items_text)
        self.assertTrue(
            any("立即處置」檢核項不足" in e for e in errors_count),
            f"未攔截檢核項不足：{errors_count}",
        )

    def test_web_to_app_evaluation_missing_conclusion_or_analysis(self):
        """6. 反例攔截：WebToApp 評估文件結論缺失或權限/簽名分析缺漏。"""
        raw = (REPO_ROOT / "docs" / "web-to-app-evaluation.md").read_text(encoding="utf-8")

        # 缺少結論
        no_conclusion = raw.replace("結論：可行", "評估：已完成")
        errors = vsp.verify_web_to_app_evaluation(no_conclusion)
        self.assertTrue(any("缺少明確可行性結論" in e for e in errors), f"未攔截結論缺失：{errors}")

        # 缺少權限分析
        no_perm = raw.replace("## 3. AndroidManifest.xml 權限宣告清單", "## 3. 其它設定清單")
        errors_perm = vsp.verify_web_to_app_evaluation(no_perm)
        self.assertTrue(any("AndroidManifest.xml" in e for e in errors_perm), f"未攔截權限分析缺失：{errors_perm}")

        # 缺少簽名分析
        no_keystore = raw.replace("## 4. Keystore 簽名架構與備份機制", "## 4. 其它備份機制")
        errors_key = vsp.verify_web_to_app_evaluation(no_keystore)
        self.assertTrue(any("Keystore" in e for e in errors_key), f"未攔截簽名分析缺失：{errors_key}")

    def test_web_to_app_workflow_missing_steps_or_disclaimers(self):
        """7. 反例攔截：接案流程缺少六大步驟或四大免責條款。"""
        raw = (REPO_ROOT / "docs" / "web-to-app-freelance-workflow.md").read_text(encoding="utf-8")

        # 缺少步驟四（金鑰簽名）
        no_step4 = raw.replace("步驟四：金鑰簽名與安全管理", "步驟四：雜項處理")
        errors_step = vsp.verify_web_to_app_workflow(no_step4)
        self.assertTrue(any("金鑰簽名" in e for e in errors_step), f"未攔截步驟四缺失：{errors_step}")

        # 缺少免責條款（金鑰保管）
        no_disclaimer = raw.replace("金鑰保管與終生更新維護責任免責", "檔案交接約定")
        errors_disc = vsp.verify_web_to_app_workflow(no_disclaimer)
        self.assertTrue(any("金鑰保管" in e for e in errors_disc), f"未攔截金鑰免責條款缺失：{errors_disc}")

    def test_cli_main_success_and_failure(self):
        """8. 驗證 CLI main() 執行成功與指定無效目錄之失敗。"""
        exit_code = vsp.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(exit_code, 0, "CLI 在合法 repo 應返回 0")

        # 指向非 repo 根目錄應返回 1
        empty_dir = REPO_ROOT / "assets"
        exit_code_fail = vsp.main(["--repo-root", str(empty_dir)])
        self.assertEqual(exit_code_fail, 1, "CLI 在無效目錄應返回 1")


if __name__ == "__main__":
    unittest.main()
