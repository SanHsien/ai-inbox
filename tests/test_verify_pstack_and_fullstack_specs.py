#!/usr/bin/env python3
"""
tests/test_verify_pstack_and_fullstack_specs.py
測試 tools/verify_pstack_and_fullstack_specs.py 外部裁判驗證器：
1. 真實 4 份規格與手冊文件全數驗證通過。
2. pstack Playbooks 文件缺漏反例攔截（缺少 /poteto-mode、官方 Playbook 缺漏或多列、CLI 規格、實例不足、
   「五大 Playbook」與未標註的 SpaceX 頭銜）。
3. Claude 外掛評測文件缺漏反例攔截（缺少推薦外掛、缺少排除項目、缺少未查證標註）。
4. 全端商業建站規範缺漏反例攔截（缺少軟刪除、定價快照、事件流水帳、狀態機狀態、Webhook 對帳）。
5. 主體資產盤點與論證規範缺漏反例攔截（缺少盤點維度、缺少 Claim+Proof、缺少示範表格）。
6. 安全載入函式 load_content 驗證（防範 ENAMETOOLONG 與各型別處理）。
7. CLI main() 執行成功與退出碼驗證。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_pstack_and_fullstack_specs as vps  # noqa: E402


class TestVerifyPstackAndFullstackSpecs(unittest.TestCase):
    """驗證 pstack 與全端規格外部裁判結構驗證器。"""

    def test_real_specs_all_pass(self):
        """1. 驗證現存於 repo 的真實 4 份文件全數通過檢查。"""
        all_passed, results = vps.verify_all_specs(REPO_ROOT)
        self.assertTrue(all_passed, f"真實文件驗證失敗：{results}")
        for path, errs in results.items():
            self.assertEqual(errs, [], f"{path} 應無任何錯誤，實際發現：{errs}")

    def test_pstack_playbooks_missing_core_components(self):
        """2. 反例攔截：pstack 缺少路由器、Playbook、CLI 規格或實例數量不足。"""
        raw = (REPO_ROOT / "docs" / "pstack-agent-playbooks.md").read_text(encoding="utf-8")

        # 2.1 缺少 /poteto-mode 路由器
        no_router = raw.replace("/poteto-mode", "/other-mode").replace("總控動態路由器", "次要工具清單")
        errors = vps.verify_pstack_playbooks(no_router)
        self.assertTrue(any("缺少 `/poteto-mode`" in e for e in errors), f"未攔截路由器缺失：{errors}")

        # 2.2 缺少某一套官方 Playbook（每一套都要擋得到），改掉的檔名同時算「官方沒有」
        for filename in vps.OFFICIAL_PLAYBOOK_FILES:
            dropped = raw.replace(f"playbooks/{filename}", f"playbooks/x-{filename}")
            errors_pb = vps.verify_pstack_playbooks(dropped)
            self.assertTrue(
                any("缺少以下官方 Playbook" in e and filename in e for e in errors_pb),
                f"未攔截 {filename} 缺失：{errors_pb}",
            )
            self.assertTrue(
                any("官方 playbooks 目錄沒有的檔名" in e and f"x-{filename}" in e for e in errors_pb),
                f"未攔截杜撰的 playbook 檔名：{errors_pb}",
            )

        # 2.3 缺少特定 CLI（例如 Antigravity）
        no_ag = raw.replace("Antigravity", "OtherCLI")
        errors_cli = vps.verify_pstack_playbooks(no_ag)
        self.assertTrue(any("Antigravity" in e for e in errors_cli), f"未攔截 CLI 規格缺失：{errors_cli}")

        # 2.4 實例不足 3 個（刪除實例 2 與實例 3）
        reduced_examples = raw.replace("### 實例 2：", "### 略過 2：").replace("### 實例 3：", "### 略過 3：")
        errors_ex = vps.verify_pstack_playbooks(reduced_examples)
        self.assertTrue(any("實例對照數量不足" in e for e in errors_ex), f"未攔截實例不足：{errors_ex}")

    def test_pstack_official_playbook_list_and_corrected_premises(self):
        """2b. 官方清單常數正確，且已更正的錯誤前提（五大 Playbook、未標註的 SpaceX）會被擋下。"""
        raw = (REPO_ROOT / "docs" / "pstack-agent-playbooks.md").read_text(encoding="utf-8")

        # 官方清單：22 套、不重複、含原本誤以為是全部的五套
        files = vps.OFFICIAL_PLAYBOOK_FILES
        self.assertEqual(len(files), 22)
        self.assertEqual(len(set(files)), 22)
        for name in ("bug-fix.md", "feature.md", "refactoring.md", "investigation.md", "perf-issue.md"):
            self.assertIn(name, files)
        self.assertRegex(vps.OFFICIAL_PLAYBOOKS_VERIFIED_AT, r"^\d{4}-\d{2}-\d{2}$")

        # 真實文件：列出的 playbook 檔名與官方清單完全一致
        self.assertEqual(set(vps.PLAYBOOK_REF_RE.findall(raw)), set(files))

        # 多列一個官方沒有的 playbook
        extra = raw + "\n另有 `playbooks/made-up.md`。\n"
        errors_extra = vps.verify_pstack_playbooks(extra)
        self.assertTrue(any("made-up.md" in e for e in errors_extra), f"未攔截杜撰 playbook：{errors_extra}")

        # 「五大／5 大 Playbook」
        for phrase in ("## 4. 五大核心 Playbooks 規格拆解", "定義 5 大 Playbooks 的規格"):
            errors_five = vps.verify_pstack_playbooks(raw + f"\n{phrase}\n")
            self.assertTrue(any("五大" in e for e in errors_five), f"未攔截「{phrase}」：{errors_five}")

        # 未標註的 SpaceX 頭銜；標了「未查證」則放行
        errors_sx = vps.verify_pstack_playbooks(raw + "\n作者是前 SpaceX 首席工程師。\n")
        self.assertTrue(any("SpaceX" in e for e in errors_sx), f"未攔截未標註的 SpaceX 頭銜：{errors_sx}")
        labeled = raw + "\n轉述來源稱作者任職 SpaceX，未查證。\n"
        self.assertEqual(vps.verify_pstack_playbooks(labeled), [])
        # 2026-11-21 稽核：改寫成 Space X、Space-X、全形也要擋；workspace 之類的字不誤擋
        for variant in ("Space X", "Space-X", "ＳｐａｃｅＸ", "SpaceX首席"):
            errors_v = vps.verify_pstack_playbooks(raw + f"\n作者是前 {variant} 工程師。\n")
            self.assertTrue(any("SpaceX" in e for e in errors_v), f"未攔截 {variant}：{errors_v}")
        self.assertEqual(vps.verify_pstack_playbooks(raw + "\n切到 workspace X 再執行。\n"), [])

    def test_claude_plugins_review_missing_plugins_or_unverified(self):
        """3. 反例攔截：Claude 外掛評測缺少推薦、排除或未查證標註。"""
        raw = (REPO_ROOT / "docs" / "claude-plugins-official-review.md").read_text(encoding="utf-8")

        # 3.1 缺少推薦外掛（例如 security-guidance）
        no_rec = raw.replace("`security-guidance`", "`custom-sec`")
        errors_rec = vps.verify_claude_plugins_review(no_rec)
        self.assertTrue(any("security-guidance" in e for e in errors_rec), f"未攔截推薦外掛缺失：{errors_rec}")

        # 3.2 缺少排除外掛（例如 imessage）
        no_exc = raw.replace("`imessage`", "`custom-msg`")
        errors_exc = vps.verify_claude_plugins_review(no_exc)
        self.assertTrue(any("imessage" in e for e in errors_exc), f"未攔截排除外掛缺失：{errors_exc}")

        # 3.3 缺少未查證段落或標註
        no_unverified = raw.replace("## 4. 未查證或需環境驗證項目", "## 4. 補充說明").replace("[未查證]", "[已查證]").replace("未查證", "已驗證")
        errors_uv = vps.verify_claude_plugins_review(no_unverified)
        self.assertTrue(any("未查證" in e for e in errors_uv), f"未攔截未查證標註缺失：{errors_uv}")

    def test_fullstack_builder_missing_architectural_guards(self):
        """4. 反例攔截：全端建站規範缺少軟刪除、定價快照、事件流水帳、狀態機或 Webhook 對帳。"""
        raw = (REPO_ROOT / "templates" / "fullstack-website-builder-skill.md").read_text(encoding="utf-8")

        # 4.1 缺少軟刪除
        no_sd = raw.replace("deleted_at", "removed_at").replace("軟刪除", "硬刪除").replace("Soft Delete", "Hard Delete")
        errors_sd = vps.verify_fullstack_website_builder(no_sd)
        self.assertTrue(any("軟刪除" in e for e in errors_sd), f"未攔截軟刪除缺失：{errors_sd}")

        # 4.2 缺少定價快照
        no_ps = raw.replace("pricing_snapshot", "order_price").replace("final_payable_amount", "amount")
        errors_ps = vps.verify_fullstack_website_builder(no_ps)
        self.assertTrue(any("定價快照" in e for e in errors_ps), f"未攔截定價快照缺失：{errors_ps}")

        # 4.3 缺少事件流水帳
        no_el = raw.replace("registration_events", "logs").replace("事件審計", "一般紀錄").replace("Event Ledger", "Logs")
        errors_el = vps.verify_fullstack_website_builder(no_el)
        self.assertTrue(any("事件流水帳" in e for e in errors_el), f"未攔截事件流水帳缺失：{errors_el}")

        # 4.4 缺少狀態機核心狀態（如 refunded）
        no_rf = raw.replace("refunded", "done_refund")
        errors_st = vps.verify_fullstack_website_builder(no_rf)
        self.assertTrue(any("refunded" in e for e in errors_st), f"未攔截狀態機缺漏：{errors_st}")

        # 4.5 缺少 Webhook 金額對帳
        no_wh = raw.replace("金額雙重對帳", "金額忽略").replace("Amount Reconciliation", "Skip Check")
        errors_wh = vps.verify_fullstack_website_builder(no_wh)
        self.assertTrue(any("金額雙重對帳" in e for e in errors_wh), f"未攔截 Webhook 對帳防線缺失：{errors_wh}")

    def test_subject_inventory_missing_inventory_or_claim_proof(self):
        """5. 反例攔截：主體資產盤點缺少維度、Claim+Proof 或示範表格。"""
        raw = (REPO_ROOT / "templates" / "subject-inventory-argument-writing-prompt.md").read_text(encoding="utf-8")

        # 5.1 缺少主體資產盤點核心要素（例如地理座標或時間尺度）
        no_inv = raw.replace("地理與物理座標", "地點說明").replace("時間尺度與節奏", "時程進度")
        errors_inv = vps.verify_subject_inventory_prompt(no_inv)
        self.assertTrue(any("主體資產盤點缺少" in e for e in errors_inv), f"未攔截盤點維度缺失：{errors_inv}")

        # 5.2 缺少 Claim + Proof 要素
        no_claim = raw.replace("爭點主張", "文案標題").replace("Claim", "Title")
        errors_cp = vps.verify_subject_inventory_prompt(no_claim)
        self.assertTrue(any("爭點論證寫作缺少" in e for e in errors_cp), f"未攔截 Claim+Proof 缺失：{errors_cp}")

        # 5.3 缺少落地示範表格
        no_demo = raw.replace("| 區塊 (Section) | 爭點主張 (Claim) |", "| 欄位一 | 欄位二 |")
        errors_demo = vps.verify_subject_inventory_prompt(no_demo)
        self.assertTrue(any("缺少完整主題落地示範" in e for e in errors_demo), f"未攔截示範表格缺失：{errors_demo}")

    def test_load_content_safety_and_enametoolong_prevention(self):
        """6. 驗證 load_content 在長字串、多行字串與各型別下的安全性（防範 ENAMETOOLONG）。"""
        # 多行字串（絕不能直接 Path(s).exists()）
        multiline_str = "Line 1\nLine 2\n" + "A" * 500
        content = vps.load_content(multiline_str)
        self.assertEqual(content, multiline_str)

        # 超過 240 字元的單行長字串
        long_str = "X" * 300
        content_long = vps.load_content(long_str)
        self.assertEqual(content_long, long_str)

        # Path 物件
        sample_path = REPO_ROOT / "docs" / "pstack-agent-playbooks.md"
        loaded_from_path = vps.load_content(sample_path)
        self.assertTrue(len(loaded_from_path) > 100)

        # 非法型別
        with self.assertRaises(TypeError):
            vps.load_content(12345)  # type: ignore

    def test_cli_main_exit_codes(self):
        """7. 驗證 CLI main() 成功 (exit 0) 與失敗 (exit 1) 退出碼。"""
        # 成功退出
        code_success = vps.main(["--repo-root", str(REPO_ROOT)])
        self.assertEqual(code_success, 0)

        # 失敗退出（指向空目錄或無效目錄）
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            code_fail = vps.main(["--repo-root", tmpdir])
            self.assertEqual(code_fail, 1)


if __name__ == "__main__":
    unittest.main()
