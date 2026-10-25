#!/usr/bin/env python3
"""
tests/test_verify_academic_and_latex_guard.py
測試 tools/verify_academic_and_latex_guard.py 外部裁判驗證器：
1. 真實文件全數驗證通過。
2. 行內數學公式變數被竄改攔截測試。
3. 區塊數學公式被竄改或遺失攔截測試。
4. 學術引用標籤遺失或被翻譯攔截測試。
5. 交叉參照標籤竄改或遺失攔截測試。
6. LaTeX 保護契約與內嵌測試輸入輸出竄改攔截測試。
7. 5W1H-CQR-KSU 提示詞架構缺漏攔截測試。
8. 實測報告 CQR 表格或 KSU DoD 缺失攔截測試。
9. CLI main() 執行成功與無效路徑失敗退出碼測試。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_academic_and_latex_guard as vag  # noqa: E402


class TestVerifyAcademicAndLatexGuard(unittest.TestCase):
    def test_real_academic_and_latex_guards_pass(self):
        """1. 驗證現存於 repo 的真實文件全數通過檢查。"""
        all_passed, results = vag.verify_all_academic_and_latex_guards(REPO_ROOT)
        self.assertTrue(all_passed, f"真實文件驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤")

    def test_latex_inline_formula_tampered_detected(self):
        """2. 反例攔截：行內數學公式變數被竄改或翻譯。"""
        source = (
            "We define the normal loss $\\mathcal{L}_{norm}$ for ray $r \\in \\mathcal{R}$ "
            "with covariance $\\boldsymbol{\\Sigma}_i = \\mathbf{R}_i \\mathbf{S}_i \\mathbf{S}_i^T \\mathbf{R}_i^T$."
        )
        # 情況 A：變數被更動（\\mathcal{L}_{norm} 變成 \\mathcal{L}_{loss}）
        tampered_a = (
            "我們為光線 $r \\in \\mathcal{R}$ 定義法向量損失 $\\mathcal{L}_{loss}$，"
            "其協方差為 $\\boldsymbol{\\Sigma}_i = \\mathbf{R}_i \\mathbf{S}_i \\mathbf{S}_i^T \\mathbf{R}_i^T$。"
        )
        errors_a = vag.verify_latex_and_citations_preserved(source, tampered_a)
        self.assertTrue(
            any("行內數學公式" in e and "\\mathcal{L}_{norm}" in e for e in errors_a),
            f"未攔截到行內公式變數被竄改：{errors_a}",
        )

        # 情況 B：希臘字母符號遺失或被替換（\mathcal{R} 變成 R）
        tampered_b = (
            "我們為光線 $r \\in R$ 定義法向量損失 $\\mathcal{L}_{norm}$，"
            "其協方差為 $\\boldsymbol{\\Sigma}_i = \\mathbf{R}_i \\mathbf{S}_i \\mathbf{S}_i^T \\mathbf{R}_i^T$。"
        )
        errors_b = vag.verify_latex_and_citations_preserved(source, tampered_b)
        self.assertTrue(
            any("行內數學公式" in e and "$r \\in \\mathcal{R}$" in e for e in errors_b),
            f"未攔截到集合符號竄改：{errors_b}",
        )

    def test_latex_display_block_tampered_detected(self):
        """3. 反例攔截：區塊數學公式被竄改或遺漏。"""
        source = (
            "The accumulated transmittance along ray $r$ is:\n\n"
            "$$T_i = \\exp \\left( -\\sum_{j=1}^{i-1} \\sigma_j \\delta_j \\right) \\cdot \\left( 1 - \\exp(-\\sigma_i \\delta_i) \\right)$$\n"
        )
        # 情況 A：區塊公式完全遺失
        tampered_missing = "沿著光線 $r$ 的累積透射率如下所示：\n\n（公式略）\n"
        errors_missing = vag.verify_latex_and_citations_preserved(
            source, tampered_missing
        )
        self.assertTrue(
            any("區塊數學公式" in e for e in errors_missing),
            f"未攔截到區塊公式遺漏：{errors_missing}",
        )

        # 情況 B：區塊公式內部細節被更動（如指數被拿掉）
        tampered_changed = (
            "沿著光線 $r$ 的累積透射率如下：\n\n"
            "$$T_i = \\sum_{j=1}^{i-1} \\sigma_j \\delta_j$$\n"
        )
        errors_changed = vag.verify_latex_and_citations_preserved(
            source, tampered_changed
        )
        self.assertTrue(
            any("區塊數學公式" in e and "$$T_i =" in e for e in errors_changed),
            f"未攔截到區塊公式內容被竄改：{errors_changed}",
        )

    def test_citation_tag_missing_or_translated_detected(self):
        """4. 反例攔截：文獻引用標籤遺失、作者名被翻譯或數字標籤遺失。"""
        source = (
            "Recent advances in 3DGS [Kerbl et al., 2023] and NeRF [Mildenhall et al., 2020] "
            "as verified in \\cite{vaswani2017} and [12]."
        )
        # 情況 A：作者被粗暴中譯
        translated_author = (
            "近期在 3DGS [克爾布爾等人，2023] 與 NeRF [Mildenhall et al., 2020] 的進展，"
            "如 \\cite{vaswani2017} 與 [12] 所驗證。"
        )
        errors_author = vag.verify_latex_and_citations_preserved(
            source, translated_author
        )
        self.assertTrue(
            any("學術引用標籤" in e and "Kerbl et al., 2023" in e for e in errors_author),
            f"未攔截到作者引用被中譯：{errors_author}",
        )

        # 情況 B：數字引用 [12] 與 \\cite{vaswani2017} 遺漏
        missing_numeric = (
            "近期在 3DGS [Kerbl et al., 2023] 與 NeRF [Mildenhall et al., 2020] 的進展。"
        )
        errors_numeric = vag.verify_latex_and_citations_preserved(
            source, missing_numeric
        )
        self.assertTrue(
            any("[12]" in e for e in errors_numeric),
            f"未攔截到數字引用 [12] 遺失：{errors_numeric}",
        )
        self.assertTrue(
            any("\\cite{vaswani2017}" in e for e in errors_numeric),
            f"未攔截到 \\cite 標籤遺失：{errors_numeric}",
        )

    def test_cross_reference_tampered_detected(self):
        """5. 反例攔截：交叉參照標籤被改寫或遺失。"""
        source = (
            "The expected depth is integrated as depicted in Eq. (3) and Fig. 2(b), "
            "referring to \\ref{sec:method}."
        )
        # 交叉參照被中文化（「式 (3)」與「圖 2(b)」）
        tampered_cross = (
            "期望深度依據式 (3) 與圖 2(b) 所示進行累加，請參考第 3 節。"
        )
        errors_cross = vag.verify_latex_and_citations_preserved(source, tampered_cross)
        self.assertTrue(
            any("交叉參照" in e and "Eq. (3)" in e for e in errors_cross),
            f"未攔截到 Eq. (3) 竄改：{errors_cross}",
        )
        self.assertTrue(
            any("交叉參照" in e and "Fig. 2(b)" in e for e in errors_cross),
            f"未攔截到 Fig. 2(b) 竄改：{errors_cross}",
        )
        self.assertTrue(
            any("交叉參照" in e and "\\ref{sec:method}" in e for e in errors_cross),
            f"未攔截到 \\ref 標籤遺失：{errors_cross}",
        )

    def test_latex_protection_prompt_tampered_detected(self):
        """6. 反例攔截：latex-citation-protection-prompt 缺少契約或測試案例被破壞。"""
        raw = (
            REPO_ROOT / "templates" / "latex-citation-protection-prompt.md"
        ).read_text(encoding="utf-8")

        # 情況 A：缺少四大保護契約之一
        missing_contract = raw.replace("行內數學公式保護", "文字快速閱讀")
        errors_contract = vag.verify_latex_citation_protection_prompt(missing_contract)
        self.assertTrue(
            any("行內數學公式保護" in e for e in errors_contract),
            f"未攔截到保護契約缺失：{errors_contract}",
        )

        # 情況 B：破壞預期標準輸出的公式（僅替換預期輸出中的超參數 $\lambda_1 = 0.05$ 為 $\lambda_1 = 0.5$）
        tampered_output = raw.replace(
            "超參數 $\\lambda_1 = 0.05$", "超參數 $\\lambda_1 = 0.5$"
        )
        errors_output = vag.verify_latex_citation_protection_prompt(tampered_output)
        self.assertTrue(
            any("\\lambda_1 = 0.05" in e for e in errors_output),
            f"未攔截到範本內嵌預期輸出之公式竄改：{errors_output}",
        )

    def test_academic_reading_prompt_missing_5w1h_cqr_ksu_detected(self):
        """7. 反例攔截：academic-reading-prompt 缺少 5W1H、CQR 或 KSU 關鍵維度。"""
        raw = (REPO_ROOT / "templates" / "academic-reading-prompt.md").read_text(
            encoding="utf-8"
        )

        # 缺少 5W1H 中的 Key Metrics
        no_metrics = raw.replace("Key Metrics", "Other Info")
        errors_metrics = vag.verify_academic_reading_prompt(no_metrics)
        self.assertTrue(
            any("Key Metrics" in e for e in errors_metrics),
            f"未攔截到 5W1H 之 Key Metrics 缺失：{errors_metrics}",
        )

        # 缺少 CQR 中的 Reasoning
        no_reasoning = raw.replace("Reasoning", "Conclusion")
        errors_reasoning = vag.verify_academic_reading_prompt(no_reasoning)
        self.assertTrue(
            any("Reasoning" in e for e in errors_reasoning),
            f"未攔截到 CQR 之 Reasoning 缺失：{errors_reasoning}",
        )

        # 缺少 KSU 中的 DoD / 驗收標準
        no_dod = raw.replace("DoD", "TODO").replace("驗收標準", "要求說明")
        errors_dod = vag.verify_academic_reading_prompt(no_dod)
        self.assertTrue(
            any("DoD" in e or "驗收標準" in e for e in errors_dod),
            f"未攔截到 KSU 之 DoD 缺失：{errors_dod}",
        )

    def test_academic_reading_smoke_report_missing_sections_detected(self):
        """8. 反例攔截：smoke-report 缺少 SWE-bench 定位、CQR 矩陣或 KSU。"""
        raw = (REPO_ROOT / "docs" / "academic-reading-smoke-report.md").read_text(
            encoding="utf-8"
        )

        # 缺少 SWE-bench 標記
        no_swe = raw.replace("SWE-bench", "Toy-Benchmark")
        errors_swe = vag.verify_academic_reading_smoke_report(no_swe)
        self.assertTrue(
            any("SWE-bench" in e for e in errors_swe),
            f"未攔截到 SWE-bench 論文標記缺失：{errors_swe}",
        )

        # 缺少 CQR 矩陣 Markdown 表格
        no_cqr_table = raw.replace("| **Claim (核心主張)** |", "| 主張論述 |")
        errors_cqr = vag.verify_academic_reading_smoke_report(no_cqr_table)
        self.assertTrue(
            any("CQR" in e for e in errors_cqr),
            f"未攔截到 CQR 表格缺失：{errors_cqr}",
        )

    def test_cli_main_success_and_failure(self):
        """9. 驗證 CLI main() 在合法 repo 返回 0，在無效目錄返回 1。"""
        exit_code = vag.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(exit_code, 0, "CLI 在合法專案目錄應返回 0")

        empty_dir = REPO_ROOT / "assets"
        exit_code_fail = vag.main(["--repo-root", str(empty_dir)])
        self.assertEqual(exit_code_fail, 1, "CLI 在無效目錄應返回 1")


if __name__ == "__main__":
    unittest.main()
