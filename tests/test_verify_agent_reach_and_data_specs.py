#!/usr/bin/env python3
"""
tests/test_verify_agent_reach_and_data_specs.py
測試 tools/verify_agent_reach_and_data_specs.py 外部裁判結構驗證器：
1. 真實規格文件全數驗證通過（Exit 0，零缺陷）。
2. Agent-Reach references 檔案缺失或為空反例攔截。
3. Agent-Reach 路由表分類缺漏或參照斷鏈反例攔截。
4. Public APIs 檢索技能缺少三大門檻（Auth: No, CORS: Yes, HTTPS）反例攔截。
5. Free Public APIs 索引庫筆數/類別異常或未達門檻反例攔截。
6. 多行字串防範 Linux CI ENAMETOOLONG 機制驗證。
7. CLI main() 命令列執行成功與失敗退出碼驗證。
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_agent_reach_and_data_specs as vsp  # noqa: E402


class TestVerifyAgentReachAndDataSpecs(unittest.TestCase):
    def test_1_real_specs_all_pass(self):
        """1. 驗證現存於 repo 的真實文件全數通過檢查。"""
        all_passed, results = vsp.verify_all_specs(REPO_ROOT)
        self.assertTrue(all_passed, f"真實文件驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤，但發現：{errs}")

    def test_2_agent_reach_missing_reference_file(self):
        """2. 反例攔截：references 目錄缺少必備領域檔案或檔案為空。"""
        skill_text = (REPO_ROOT / "templates" / "agent-reach" / "SKILL.md").read_text(encoding="utf-8")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_refs = Path(tmpdir)
            # 建立除 video.md 以外的檔案
            for domain, filename in vsp.REQUIRED_AGENT_REACH_DOMAINS:
                if filename != "video.md":
                    (temp_refs / filename).write_text(f"# {domain}", encoding="utf-8")
                else:
                    # 建立一個空檔案
                    (temp_refs / "empty_video.md").touch()

            errors = vsp.verify_agent_reach_specs(skill_text, references_dir=temp_refs)
            self.assertTrue(
                any("缺少必備 references 檔案：video.md" in e for e in errors),
                f"未攔截到缺少 video.md：{errors}",
            )

    def test_3_agent_reach_broken_link_or_missing_route(self):
        """3. 反例攔截：路由表缺少分類或參照檔案斷鏈。"""
        raw_skill = (REPO_ROOT / "templates" / "agent-reach" / "SKILL.md").read_text(encoding="utf-8")
        refs_dir = REPO_ROOT / "templates" / "agent-reach" / "references"

        # (A) 移除 finance 分類
        bad_skill_missing = raw_skill.replace(
            "| 雪球/股票行情 | finance | [references/finance.md](references/finance.md) |",
            "",
        )
        errors_missing = vsp.verify_agent_reach_specs(bad_skill_missing, references_dir=refs_dir)
        self.assertTrue(
            any("缺少「finance」分類條目" in e for e in errors_missing),
            f"未攔截到路由表缺少 finance：{errors_missing}",
        )

        # (B) 將 search.md 竄改成不存在的斷鏈連結
        bad_skill_broken = raw_skill.replace(
            "[references/search.md](references/search.md)",
            "[references/search.md](references/broken_not_exist.md)",
        )
        errors_broken = vsp.verify_agent_reach_specs(bad_skill_broken, references_dir=refs_dir)
        self.assertTrue(
            any("路由表參照斷鏈" in e or "參照連結異常" in e for e in errors_broken),
            f"未攔截到斷鏈參照：{errors_broken}",
        )

    def test_4_public_apis_missing_gating_threshold(self):
        """4. 反例攔截：public-apis-search-skill 缺少必備篩選門檻。"""
        raw_skill = (REPO_ROOT / "templates" / "public-apis-search-skill.md").read_text(encoding="utf-8")

        # 缺少 CORS 門檻
        no_cors = raw_skill.replace("CORS: Yes", "CORS: Optional").replace("瀏覽器跨域放行", "瀏覽器放行")
        errors = vsp.verify_public_apis_search_skill(no_cors)
        self.assertTrue(
            any("CORS: Yes" in e for e in errors),
            f"未攔截到缺少 CORS: Yes 門檻：{errors}",
        )

        # 缺少 Auth: No 門檻
        no_auth = raw_skill.replace("Auth: No", "Auth: Bearer").replace("零金鑰免註冊", "需要金鑰")
        errors_auth = vsp.verify_public_apis_search_skill(no_auth)
        self.assertTrue(
            any("Auth: No" in e for e in errors_auth),
            f"未攔截到缺少 Auth: No 門檻：{errors_auth}",
        )

    def test_5_free_public_apis_index_corrupted(self):
        """5. 反例攔截：free-public-apis.md 筆數宣告被破壞或表格資料出現非 No/Yes 異常。"""
        raw_index = (REPO_ROOT / "docs" / "free-public-apis.md").read_text(encoding="utf-8")

        # (A) 破壞筆數宣告
        corrupted_count = raw_index.replace("共 462 個公開端點", "共 400 個公開端點")
        errors_count = vsp.verify_free_public_apis_index(corrupted_count)
        self.assertTrue(
            any("462 個公開端點" in e for e in errors_count),
            f"未攔截到筆數宣告異常：{errors_count}",
        )

        # (B) 注入一筆未通過 Auth: No 門檻的資料行
        bad_row = "| [BadAPI](https://bad.com) | Bad test | apiKey | Yes | Yes |\n"
        corrupted_row = raw_index.replace(
            "| [Cat Facts](https://catfact.ninja/) | Random cat facts | No | Yes | Yes |",
            bad_row + "| [Cat Facts](https://catfact.ninja/) | Random cat facts | No | Yes | Yes |",
        )
        errors_row = vsp.verify_free_public_apis_index(corrupted_row)
        self.assertTrue(
            any("未通過 'Auth: No' 門檻" in e or "資料列數異常" in e for e in errors_row),
            f"未攔截到異常資料行：{errors_row}",
        )

    def test_9_safe_resolve_no_enametoolong_on_multiline_string(self):
        """9. 驗證多行巨量字串傳入時絕不觸發 Linux CI ENAMETOOLONG 異常。"""
        huge_multiline_text = ("測試行一\n" + "x" * 300 + "\n") * 50
        # 測試 _resolve_content_and_path
        content, resolved_path = vsp._resolve_content_and_path(huge_multiline_text)
        self.assertEqual(content, huge_multiline_text)
        self.assertIsNone(resolved_path)

        # 傳入驗證函式測試是否安全解析且不噴例外
        errs = vsp.verify_public_apis_search_skill(huge_multiline_text)
        self.assertIsInstance(errs, list)
        self.assertTrue(len(errs) > 0)

    def test_10_cli_main_exit_codes(self):
        """10. 驗證 CLI main() 執行成功回傳 0，無效目錄回傳 1。"""
        # 正常專案根目錄
        ret_ok = vsp.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(ret_ok, 0)

        # 故意指定無效路徑
        with tempfile.TemporaryDirectory() as empty_dir:
            ret_fail = vsp.main(["--repo-root", empty_dir])
            self.assertEqual(ret_fail, 1)


if __name__ == "__main__":
    unittest.main()
