#!/usr/bin/env python3
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from verify_story_structure import (
    evaluate_causality,
    evaluate_foreshadowing,
    extract_cjk_sentences,
    verify_length_contract,
    verify_story_structure,
)


class TestVerifyStoryStructure(unittest.TestCase):
    def setUp(self):
        # 建立標準合格的 4 句 7 字範例文本
        # 每句 7 字：少年立志登高峰，手握木劍向天指，誓斬惡龍救故里，無懼風雪踏荒山
        self.valid_node_text = "少年立志登高峰，手握木劍向天指，誓斬惡龍救故里，無懼風雪踏荒山。"
        # 每句 7 字：心境昇華超原志，守護眾生化英雄。
        self.valid_arrow_text = "心境昇華超原志，守護眾生化英雄。"

    def test_extract_cjk_sentences(self):
        text = "少年立志登高峰，手握木劍向天指！誓斬惡龍救故里？無懼風雪踏荒山。"
        s = extract_cjk_sentences(text)
        self.assertEqual(len(s), 4)
        for sentence in s:
            self.assertEqual(len(sentence), 7)

    def test_verify_length_contract(self):
        # 合格測試 (4 句 7 字)
        v = verify_length_contract("Node A", self.valid_node_text, 4, 7)
        self.assertIsNone(v)

        # 違規測試 (句子長度不對：少一字)
        bad_text = "少數立志登高峰，手握木劍天，誓斬惡龍救故里，無懼風雪踏荒山。"
        v2 = verify_length_contract("Node A", bad_text, 4, 7)
        self.assertIsNotNone(v2)
        self.assertIn("Node A 違反字數契約", v2.message)

        # 缺失顯式標記測試
        v_missing = verify_length_contract("Node B", "缺失", 4, 7)
        self.assertIsNone(v_missing)

    def test_valid_story_full_pipeline(self):
        story = {
            "nodes": {
                node: {"text": self.valid_node_text} for node in ["A", "B", "C", "D", "E", "F", "G"]
            },
            "arrows": {
                "H1": {"text": "心境昇華超原志，守護眾生化英雄。", "strength": "強"},
                "H2": {"text": "洞悉弱點破重圍，化解困局覓生機。", "strength": "強"},
                "H3": {"text": "深入險境探秘道，觸發古陣引異象。", "strength": "強"},
            },
            "foreshadowing": [
                {"clue_node": "A", "reveal_node": "D", "note": "伏一至結果"},
                {"clue_node": "B", "reveal_node": "F", "note": "伏二至轉彎"},
                {"clue_node": "C", "reveal_node": "E", "note": "伏三至意外"},
            ],
        }

        report = verify_story_structure(story)
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.length_violations), 0)
        self.assertIn("結構完備", report.most_critical_fix)

    def test_causal_post_hoc_flagged(self):
        story = {
            "nodes": {
                node: {"text": self.valid_node_text} for node in ["A", "B", "C", "D", "E", "F", "G"]
            },
            "arrows": {
                "H1": {"text": "回到原點無成長，心境停留在此刻。", "strength": "弱"},
                "H2": {"text": "天降神兵逢奇遇，忽聞仙人賜靈丹。", "strength": "弱"},
                "H3": {"text": "忽遇地震突發災，純屬天意難預測。", "strength": "弱"},
            },
        }

        evals = evaluate_causality(story)
        h3_eval = next(e for e in evals if e.link_id == "H3")
        self.assertTrue(h3_eval.post_hoc_risk)
        self.assertIn("外部隨機事件", h3_eval.rationale)

        report = verify_story_structure(story)
        self.assertFalse(report.is_valid)
        self.assertIn("【因果斷裂】", report.most_critical_fix)

    def test_foreshadowing_tension(self):
        fs_list = [
            {"clue_node": "A", "reveal_node": "B"},  # 跨 1 步：太緊
            {"clue_node": "A", "reveal_node": "D"},  # 跨 3 步：剛好
            {"clue_node": "A", "reveal_node": "G"},  # 跨 6 步：太鬆
            {"clue_node": "E", "reveal_node": "B"},  # 倒錯：缺失
        ]
        results = evaluate_foreshadowing(fs_list)
        self.assertEqual(results[0].tension, "太緊")
        self.assertEqual(results[1].tension, "剛好")
        self.assertEqual(results[2].tension, "太鬆")
        self.assertEqual(results[3].tension, "缺失")


if __name__ == "__main__":
    unittest.main()
