#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_verify_a11y_tree_snapshot.py

單元測試套件：驗證 agent-desktop 無障礙樹快照結構、Ref 解析、
PowerShell 單引號跳脫檢查、STALE_REF 狀態機、以及重試安全處置合約。
"""

import unittest
import sys
import os

# 將 tools 加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from verify_a11y_tree_snapshot import (
    Ref,
    RefValidationError,
    SnapshotEngine,
    A11yNode,
    Disposition
)


class TestA11yTreeSnapshot(unittest.TestCase):
    def setUp(self):
        self.engine = SnapshotEngine()
        # 建立測試樹
        self.btn_submit = A11yNode("e2", "button", "Submit")
        self.btn_disabled = A11yNode("e3", "button", "Cancel", states=["disabled"])
        self.input_search = A11yNode("e4", "text_field", "Search Input", value="")
        self.chk_agree = A11yNode("e5", "checkbox", "I Agree", states=[])
        
        self.panel = A11yNode("e6", "pane", "Settings Panel", is_container=True, children=[
            A11yNode("e7", "button", "Reset"),
            A11yNode("e8", "button", "Apply")
        ])

        self.root = A11yNode("e1", "window", "Main Window", is_container=True, children=[
            self.btn_submit,
            self.btn_disabled,
            self.input_search,
            self.chk_agree,
            self.panel
        ])
        
        self.snap_id = self.engine.register_snapshot("s8f3k2p9", self.root)

    # 1. Ref 語法與解析測試
    def test_ref_parsing_valid(self):
        ref1 = Ref.parse("@s8f3k2p9:e12")
        self.assertEqual(ref1.snapshot_id, "s8f3k2p9")
        self.assertEqual(ref1.element_id, "e12")

        # 包含單引號的情形 (PowerShell 傳入常態)
        ref2 = Ref.parse("'@s8f3k2p9:e2'")
        self.assertEqual(ref2.snapshot_id, "s8f3k2p9")
        self.assertEqual(ref2.element_id, "e2")

    def test_ref_parsing_powershell_splatting_error(self):
        # 測試缺少 @ 或格式不合格
        with self.assertRaises(RefValidationError) as ctx:
            Ref.parse("s8f3k2p9:e12")
        self.assertEqual(ctx.exception.code, "INVALID_ARGS")
        self.assertIn("PowerShell", ctx.exception.suggestion)

        with self.assertRaises(RefValidationError) as ctx2:
            Ref.parse("invalid_ref")
        self.assertEqual(ctx2.exception.code, "INVALID_ARGS")

    def test_ref_parsing_unqualified_bare_ref(self):
        # 測試未帶命名空間的裸 ref 被拒絕
        with self.assertRaises(RefValidationError) as ctx:
            Ref.parse("@e12")
        self.assertEqual(ctx.exception.code, "INVALID_ARGS")
        self.assertIn("namespaced refs", str(ctx.exception))

    # 2. 正常點擊與屬性修改 (Headless Semantic)
    def test_semantic_click_success(self):
        res = self.engine.execute_action("click", "'@s8f3k2p9:e2'")
        self.assertTrue(res["ok"])
        self.assertEqual(res["command"], "click")
        self.assertEqual(res["data"]["role"], "button")
        self.assertEqual(res["data"]["disposition"]["delivery"], "delivered_verified")
        self.assertEqual(res["data"]["disposition"]["retry"], "safe")

    def test_semantic_set_value_success(self):
        res = self.engine.execute_action("set-value", "'@s8f3k2p9:e4'", value="Test Query")
        self.assertTrue(res["ok"])
        self.assertEqual(res["data"]["value"], "Test Query")
        self.assertEqual(self.input_search.value, "Test Query")

    def test_toggle_checkbox(self):
        res = self.engine.execute_action("toggle", "'@s8f3k2p9:e5'")
        self.assertTrue(res["ok"])
        self.assertTrue(res["data"]["checked"])

        # 再 toggle 一次應為 False
        res2 = self.engine.execute_action("toggle", "'@s8f3k2p9:e5'")
        self.assertTrue(res2["ok"])
        self.assertFalse(res2["data"]["checked"])

    # 3. 節點禁用狀態測試
    def test_disabled_element_fails(self):
        res = self.engine.execute_action("click", "'@s8f3k2p9:e3'")
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"]["code"], "ACTION_FAILED")
        self.assertFalse(res["error"]["details"]["retryable"])

    # 4. STALE_REF 與 SNAPSHOT_NOT_FOUND 狀態機測試
    def test_stale_ref_after_snapshot_invalidation(self):
        # 產生新快照，舊快照過期
        self.engine.register_snapshot("t9g4l3q1", self.root)
        self.engine.invalidate_old_snapshots()

        # 拿舊的 Ref 嘗試點擊
        res = self.engine.execute_action("click", "'@s8f3k2p9:e2'")
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"]["code"], "STALE_REF")
        self.assertEqual(res["error"]["disposition"]["delivery"], "not_delivered")
        self.assertEqual(res["error"]["disposition"]["retry"], "safe")

    def test_snapshot_not_found(self):
        res = self.engine.execute_action("click", "'@nonexist:e2'")
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"]["code"], "SNAPSHOT_NOT_FOUND")

    # 5. Windows 平台 Headless vs Headed 限制測試 (type vs set-value)
    def test_type_headless_policy_denied(self):
        res = self.engine.execute_action("type", "'@s8f3k2p9:e4'", value="Typing", headed=False)
        self.assertFalse(res["ok"])
        self.assertEqual(res["error"]["code"], "POLICY_DENIED")
        self.assertIn("set-value", res["error"]["suggestion"])

    def test_type_headed_success_and_unsafe_retry(self):
        res = self.engine.execute_action("type", "'@s8f3k2p9:e4'", value="Typing", headed=True)
        self.assertTrue(res["ok"])
        # 鍵盤模擬為 delivered_unverified，retry 必須為 unsafe，防止盲目重複輸入
        self.assertEqual(res["data"]["disposition"]["delivery"], "delivered_unverified")
        self.assertEqual(res["data"]["disposition"]["retry"], "unsafe")

    # 6. 骨架速描 (--skeleton) 與區域下鑽測試
    def test_skeleton_representation(self):
        tree_dict = self.root.to_dict("s8f3k2p9", skeleton=True)
        # Settings Panel 是容器，應折疊並提供 children_count
        panel_dict = None
        for child in tree_dict["children"]:
            if child["name"] == "Settings Panel":
                panel_dict = child
                break
        self.assertIsNotNone(panel_dict)
        self.assertEqual(panel_dict["children_count"], 2)
        self.assertNotIn("children", panel_dict)

    # 7. 節點搜尋 (find) 測試
    def test_find_nodes(self):
        buttons = self.engine.find_nodes("s8f3k2p9", role="button")
        self.assertEqual(len(buttons), 4) # Submit, Cancel, Reset, Apply

        exact_submit = self.engine.find_nodes("s8f3k2p9", role="button", name="Submit", exact=True)
        self.assertEqual(len(exact_submit), 1)
        self.assertEqual(exact_submit[0].name, "Submit")


if __name__ == "__main__":
    unittest.main()
