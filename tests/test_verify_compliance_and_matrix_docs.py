"""
tests/test_verify_compliance_and_matrix_docs.py
測試 tools/verify_compliance_and_matrix_docs.py：
  1. 真實文件全數通過結構驗證 (Pass)。
  2. 反例攔截：
     - ai-persona-compliance-checklist: 分類缺漏 (<5 類) 或每類勾選項不足 (<3 項)。
     - ai-persona-compliance-checklist: URL 格式不合法或合法 URL 數量不足 (<5 個)。
     - ai-influencer-claims-check: 宣稱缺少法定結論（官方證實/官方未提及/與官方矛盾）。
     - ai-influencer-claims-check: 宣稱缺少有效 https:// 來源連結。
     - feedback-desk-vs-agent-relay: 對照表列數不足 (<8 列) 或欄位數不一致。
     - feedback-desk-vs-agent-relay: 對照表含有空白單元格。
     - ambition-prompt-checklist: 缺少四大面向之一或勾選項不足。
     - ambition-prompt-checklist: 缺少「改寫前」或「改寫後」對照區塊。
"""

from __future__ import annotations

import sys
from pathlib import Path

import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import verify_compliance_and_matrix_docs as vcmd  # noqa: E402


def test_real_docs_all_pass():
    """驗證 repo 中四份真實文件皆能 100% 通過結構驗證。"""
    results = vcmd.verify_all_docs(REPO_ROOT)
    for key, res in results.items():
        assert res.is_valid, f"真實文件 {key} 驗證失敗: {res.errors}"
        assert len(res.errors) == 0

    # 細部檢驗真實文件詳情
    persona_res = results["persona_compliance"]
    assert len(persona_res.details["categories"]) == 5
    assert persona_res.details["valid_urls"] >= 5

    claims_res = results["influencer_claims"]
    assert len(claims_res.details["claims"]) == 3

    matrix_res = results["feedback_matrix"]
    assert matrix_res.details["data_rows_count"] >= 8
    assert matrix_res.details["header_columns"] == 5

    ambition_res = results["ambition_checklist"]
    assert len(ambition_res.details["aspects"]) == 4
    assert ambition_res.details["has_before_section"] is True
    assert ambition_res.details["has_after_section"] is True


def test_persona_compliance_category_deficit():
    """反例測試：分類不足 5 類，或某分類底下勾選項不足 3 個。"""
    # 只有 4 個分類
    short_content = """# 合規清單
## 1. 合規檢查清單
### 類別一：AI 揭露
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別二：肖像同意
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別三：聲音授權
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別四：商用條款
- [ ] 項一
- [ ] 項二
- [ ] 項三
## 2. 官方參考來源
https://example.com/1
https://example.com/2
https://example.com/3
https://example.com/4
https://example.com/5
"""
    res = vcmd.verify_persona_compliance_checklist(short_content)
    assert not res.is_valid
    assert any("分類區塊數量不足 5 大類" in err for err in res.errors)

    # 5 個分類，但其中一個只有 2 個勾選項
    few_checkboxes = """# 合規清單
## 1. 合規檢查清單
### 類別一：AI 揭露
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別二：肖像同意
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別三：聲音授權
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別四：商用條款
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別五：平台政策
- [ ] 項一
- [ ] 項二
## 2. 官方參考來源
https://example.com/1
https://example.com/2
https://example.com/3
https://example.com/4
https://example.com/5
"""
    res2 = vcmd.verify_persona_compliance_checklist(few_checkboxes)
    assert not res2.is_valid
    assert any("勾選項不足 3 個" in err for err in res2.errors)


def test_persona_compliance_invalid_urls():
    """反例測試：URL 格式不合法或合法 URL 數量少於 5 個。"""
    content = """# 合規清單
## 1. 合規檢查清單
### 類別一：AI 揭露
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別二：肖像同意
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別三：聲音授權
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別四：商用條款
- [ ] 項一
- [ ] 項二
- [ ] 項三
### 類別五：平台政策
- [ ] 項一
- [ ] 項二
- [ ] 項三
## 2. 官方參考來源
https://example.com/1
https://bad-domain
https://valid.org/path
"""
    res = vcmd.verify_persona_compliance_checklist(content)
    assert not res.is_valid
    # 應攔截到不合法 URL 格式與總數不足 5 個
    assert any("發現不合法的 https URL 格式" in err or "合法 https:// 官方連結總數不足 5 個" in err for err in res.errors)


def test_influencer_claims_missing_legal_verdict():
    """反例測試：宣稱項目未包含法定結論（自創或缺少結論）。"""
    bad_claims = """# 宣稱查證
| 項次 | 影片宣稱內容 | 官方查證結果 | 官方來源連結 | 查閱日期 | 判定 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **(a)** | 宣稱一 | 說明一 | [連結](https://example.com/a) | 2026-10-25 | **大致正確** |
| **(b)** | 宣稱二 | 說明二 | [連結](https://example.com/b) | 2026-10-25 | **與官方矛盾** |
| **(c)** | 宣稱三 | 說明三 | [連結](https://example.com/c) | 2026-10-25 | **官方證實** |
"""
    res = vcmd.verify_influencer_claims_check(bad_claims)
    assert not res.is_valid
    assert any("第 1 項宣稱未包含法定結論" in err for err in res.errors)


def test_influencer_claims_missing_url():
    """反例測試：宣稱項目缺少 https:// 來源連結。"""
    bad_claims = """# 宣稱查證
| 項次 | 影片宣稱內容 | 官方查證結果 | 官方來源連結 | 查閱日期 | 判定 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **(a)** | 宣稱一 | 說明一 | 官方口頭說明無網址 | 2026-10-25 | **官方未提及** |
| **(b)** | 宣稱二 | 說明二 | [連結](https://example.com/b) | 2026-10-25 | **與官方矛盾** |
| **(c)** | 宣稱三 | 說明三 | [連結](https://example.com/c) | 2026-10-25 | **官方證實** |
"""
    res = vcmd.verify_influencer_claims_check(bad_claims)
    assert not res.is_valid
    assert any("第 1 項宣稱缺少有效的 https:// 來源連結" in err for err in res.errors)


def test_feedback_matrix_insufficient_rows_or_col_mismatch():
    """反例測試：對照表資料列數少於 8 列或每列欄位數不一致。"""
    # 只有 5 列資料列
    short_table = """# 對照分析
| 維度 | A 機制 | B 現況 | 判斷 | 理由 |
| :--- | :--- | :--- | :--- | :--- |
| **狀態機** | desc | desc | 已有 | reason |
| **認領** | desc | desc | 已有 | reason |
| **交接** | desc | desc | 已有 | reason |
| **署名** | desc | desc | 缺少 | reason |
| **閘門** | desc | desc | 已有 | reason |
"""
    res = vcmd.verify_feedback_desk_matrix(short_table)
    assert not res.is_valid
    assert any("對照表資料列數不足 8 列" in err for err in res.errors)

    # 欄位數不一致
    mismatch_table = """# 對照分析
| 維度 | A 機制 | B 現況 | 判斷 | 理由 |
| :--- | :--- | :--- | :--- | :--- |
| **狀態機** | desc | desc | 已有 | reason |
| **認領** | desc | desc | 已有 | reason |
| **交接** | desc | desc | 已有 | reason |
| **署名** | desc | desc | 缺少 |
| **閘門** | desc | desc | 已有 | reason |
| **範圍** | desc | desc | 不需要 | reason |
| **架構** | desc | desc | 不需要 | reason |
| **邊界** | desc | desc | 已有 | reason |
"""
    res2 = vcmd.verify_feedback_desk_matrix(mismatch_table)
    assert not res2.is_valid
    assert any("欄位數不一致" in err for err in res2.errors)


def test_feedback_matrix_blank_cells():
    """反例測試：對照表含有空白單元格。"""
    blank_cell_table = """# 對照分析
| 維度 | A 機制 | B 現況 | 判斷 | 理由 |
| :--- | :--- | :--- | :--- | :--- |
| **狀態機** | desc | desc | 已有 | reason |
| **認領** | desc |  | 已有 | reason |
| **交接** | desc | desc | 已有 | reason |
| **署名** | desc | desc | 缺少 | reason |
| **閘門** | desc | desc | 已有 | reason |
| **範圍** | desc | desc | 不需要 | reason |
| **架構** | desc | desc | 不需要 | reason |
| **邊界** | desc | desc | 已有 | reason |
"""
    res = vcmd.verify_feedback_desk_matrix(blank_cell_table)
    assert not res.is_valid
    assert any("第 2 列第 3 欄為空白單元格" in err for err in res.errors)


def test_ambition_checklist_missing_aspect_or_checkboxes():
    """反例測試：缺少四大面向之一標題，或某面向勾選項不足。"""
    # 缺少面向四
    missing_aspect = """# Ambition Checklist
## 面向一：目標背後的目標
- [ ] 勾選 1
- [ ] 勾選 2
## 面向二：深度四問
- [ ] 勾選 1
- [ ] 勾選 2
## 面向三：廣度動詞化
- [ ] 勾選 1
- [ ] 勾選 2
### 改寫前
原始內容
### 改寫後
優化內容
"""
    res = vcmd.verify_ambition_prompt_checklist(missing_aspect)
    assert not res.is_valid
    assert any("缺少四大面向之一標題：面向四" in err for err in res.errors)

    # 包含四大面向但某面向勾選項不足
    lacking_boxes = """# Ambition Checklist
## 面向一：目標背後的目標
- [ ] 勾選 1
## 面向二：深度四問
- [ ] 勾選 1
- [ ] 勾選 2
## 面向三：廣度動詞化
- [ ] 勾選 1
- [ ] 勾選 2
## 面向四：外部裁判
- [ ] 勾選 1
- [ ] 勾選 2
### 改寫前
原始內容
### 改寫後
優化內容
"""
    res2 = vcmd.verify_ambition_prompt_checklist(lacking_boxes)
    assert not res2.is_valid
    assert any("勾選項不足" in err for err in res2.errors)


def test_ambition_checklist_missing_before_after():
    """反例測試：缺少「改寫前」或「改寫後」對照區塊。"""
    no_before_after = """# Ambition Checklist
## 面向一：目標背後的目標
- [ ] 勾選 1
- [ ] 勾選 2
## 面向二：深度四問
- [ ] 勾選 1
- [ ] 勾選 2
## 面向三：廣度動詞化
- [ ] 勾選 1
- [ ] 勾選 2
## 面向四：外部裁判
- [ ] 勾選 1
- [ ] 勾選 2
"""
    res = vcmd.verify_ambition_prompt_checklist(no_before_after)
    assert not res.is_valid
    assert any("缺少「改寫前」對照區塊標題" in err for err in res.errors)
    assert any("缺少「改寫後」對照區塊標題" in err for err in res.errors)


def load_tests(loader, tests, pattern):
    """unittest discover 不收集裸函式；把本模組的 test_* 包成 FunctionTestCase。"""
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(fn, description=name))
    return suite


if __name__ == "__main__":
    unittest.main()
