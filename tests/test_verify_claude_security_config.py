"""Claude 資安審查與閒置壓縮設定之外部裁判測試套件 (test_verify_claude_security_config.py)

測試覆蓋：
1. 真實檔案檢驗（docs/claude-idle-compaction-setup.md 與 templates/claude-security-guidance.md 通過）
2. 閒置壓縮 Token 門檻檢驗（低於 100k、無效 JSON 拒絕）
3. 資安規範 8 KB 預算上限拒絕測試
4. 四大硬閘門條款缺失拒絕測試
5. 四大對抗式代碼違規攔截（憑證、路徑、空殼、高危呼叫）
6. 行內與上一行 # safe: / # nosec 豁免放行測試
7. CLI 入口點與整合檢驗測試
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# 將 tools 加入 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from verify_claude_security_config import (
    MAX_GUIDANCE_BUDGET_BYTES,
    MIN_IDLE_COMPACT_TOKENS,
    extract_guidance_rules,
    main,
    scan_code_snippet,
    verify_all_configs,
    verify_idle_compaction_doc,
    verify_security_guidance_template,
)


def test_real_idle_compaction_doc_passes():
    """驗證真實的 docs/claude-idle-compaction-setup.md 符合門檻與 JSON 結構規範。"""
    doc_path = PROJECT_ROOT / "docs" / "claude-idle-compaction-setup.md"
    assert doc_path.exists(), f"找不到文件: {doc_path}"

    issues = verify_idle_compaction_doc(doc_path)
    assert issues == [], f"閒置壓縮設定文件檢驗未通過: {issues}"


def test_idle_compaction_threshold_too_low(tmp_path: Path):
    """驗證當 CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS 小於 100000 時被拒絕。"""
    bad_doc = tmp_path / "claude-idle-compaction-setup.md"
    bad_content = """# Test Doc
```json
{
  "env": {
    "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS": "50000"
  }
}
```
"""
    bad_doc.write_text(bad_content, encoding="utf-8")
    issues = verify_idle_compaction_doc(bad_doc)

    assert len(issues) > 0
    assert any("低於最低限制 100000" in iss for iss in issues)


def test_idle_compaction_invalid_json(tmp_path: Path):
    """驗證當 JSON 設定範例語法損壞時被拒絕。"""
    bad_doc = tmp_path / "claude-idle-compaction-setup.md"
    bad_content = """# Test Doc
```json
{
  "env": {
    "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS": 350000,
  }
}
```
"""
    bad_doc.write_text(bad_content, encoding="utf-8")
    issues = verify_idle_compaction_doc(bad_doc)

    assert len(issues) > 0
    assert any("語法無效" in iss for iss in issues)


def test_real_security_guidance_template_passes():
    """驗證真實的 templates/claude-security-guidance.md 預算在 8 KB 內且四大條款完整。"""
    tpl_path = PROJECT_ROOT / "templates" / "claude-security-guidance.md"
    assert tpl_path.exists(), f"找不到範本: {tpl_path}"

    rules_text = extract_guidance_rules(tpl_path)
    rule_bytes = len(rules_text.encode("utf-8"))
    assert rule_bytes <= MAX_GUIDANCE_BUDGET_BYTES, f"規則區塊大小超限: {rule_bytes} bytes"

    issues = verify_security_guidance_template(tpl_path)
    assert issues == [], f"資安規範範本檢驗未通過: {issues}"


def test_security_guidance_budget_exceeded(tmp_path: Path):
    """驗證當自訂規則區塊超過 8192 bytes 時被拒絕。"""
    bad_tpl = tmp_path / "claude-security-guidance.md"
    oversized_rule = "### 條款一：憑證與敏感資訊零暴露\n" + ("A" * 9000) + "\n### 條款二：工作目錄與檔案邊界防禦\n### 條款三：代碼真實性與禁止空殼實作\n### 條款四：高危執行階段函式與指令注入防範\n"
    content = f"""# Test Guidance
```markdown
{oversized_rule}
```
"""
    bad_tpl.write_text(content, encoding="utf-8")
    issues = verify_security_guidance_template(bad_tpl)

    assert len(issues) > 0
    assert any("超過 8 KB (8192 bytes) 預算上限" in iss for iss in issues)


def test_security_guidance_missing_clause(tmp_path: Path):
    """驗證當缺少四大硬閘門條款任一項時被拒絕。"""
    bad_tpl = tmp_path / "claude-security-guidance.md"
    incomplete_rule = """
### 條款一：憑證與敏感資訊零暴露
### 條款二：工作目錄與檔案邊界防禦
### 條款三：代碼真實性與禁止空殼實作
"""
    content = f"""# Test Guidance
```markdown
{incomplete_rule}
```
"""
    bad_tpl.write_text(content, encoding="utf-8")
    issues = verify_security_guidance_template(bad_tpl)

    assert len(issues) > 0
    assert any("條款四" in iss for iss in issues)


def test_scan_catches_hardcoded_credentials():
    """驗證 scan_code_snippet 能攔截硬編碼敏感憑證。"""
    cases = [
        'GITHUB_TOKEN = "' + "ghp_" + "12345678901234567890abcdef" + '"',
        'api_key = "' + "sk-proj-" + "1234567890abcdef1234567890abcdef" + '"',
        'stripe_key = "' + "sk_" + "live_" + "1234567890abcdef1234567890" + '"',
        'aws_key = "' + "AKIA" + "1234567890ABCDEF" + '"',
        "-----BEGIN " + "RSA PRIVATE KEY-----\nMIIE...",
    ]
    for code in cases:
        findings = scan_code_snippet(code)
        assert len(findings) > 0, f"未能攔截硬編碼憑證: {code}"
        assert any(f["category"] == "credential" for f in findings)


def test_scan_catches_path_traversal():
    """驗證 scan_code_snippet 能攔截越界路徑與敏感目錄存取。"""
    cases = [
        'with open("../config.json", "r") as f: pass',
        r'with open(r"..\private\keys.txt", "r") as f: pass',
        'key_path = os.path.expanduser("~/.ssh/id_rsa")',
        r'target = r"C:\Users\admin\.ssh\id_rsa"',
        'open("/etc/passwd", "r")',
    ]
    for code in cases:
        findings = scan_code_snippet(code)
        assert len(findings) > 0, f"未能攔截越界路徑: {code}"
        assert any(f["category"] == "path_traversal" for f in findings)


def test_scan_catches_hollow_stubs():
    """驗證 scan_code_snippet 能攔截空殼函式與吞掉例外。"""
    cases = [
        "def verify():\n    return True",
        "def count_tax():\n    return 0",
        "def get_data():\n    pass",
        "try:\n    risky()\nexcept Exception:\n    pass",
        "try:\n    run()\nexcept:\n    pass",
        "try { run(); } catch (e) {}",
    ]
    for code in cases:
        findings = scan_code_snippet(code)
        assert len(findings) > 0, f"未能攔截空殼函式或吞掉例外: {code}"
        assert any(f["category"] == "hollow_stub" for f in findings)


def test_scan_catches_dangerous_calls():
    """驗證 scan_code_snippet 能攔截 eval()、os.system() 等高危呼叫。"""
    cases = [
        "result = eval(user_input)",
        'os.system("ping " + host)',
        'exec("import os")',
        'subprocess.run("rm -rf /", shell=True)',
        "data = pickle.loads(raw_bytes)",
    ]
    for code in cases:
        findings = scan_code_snippet(code)
        assert len(findings) > 0, f"未能攔截高危呼叫: {code}"
        assert any(f["category"] == "dangerous_call" for f in findings)


def test_scan_safe_exemptions():
    """驗證支援行內或上一行 # safe: / # nosec 豁免放行。"""
    # 1. 行內豁免
    code_inline_safe = 'result = eval(formula)  # safe: verified internal formula'
    assert scan_code_snippet(code_inline_safe) == []

    # 2. 上一行豁免
    fake_ghp = "ghp_" + "12345678901234567890abcdef"
    code_prev_safe = f"""# safe: internal mock credential for deterministic unit test
GITHUB_TOKEN = "{fake_ghp}"
"""
    assert scan_code_snippet(code_prev_safe) == []

    # 3. # nosec 豁免
    code_nosec = '''# nosec
os.system("ping 127.0.0.1")
'''
    assert scan_code_snippet(code_nosec) == []

    # 4. include_exempted=True 時仍可查閱到標記為 exempted 的 finding
    all_findings = scan_code_snippet(code_inline_safe, include_exempted=True)
    assert len(all_findings) == 1
    assert all_findings[0]["exempted"] is True


def test_verify_all_configs_and_cli(monkeypatch):
    """驗證全量設定檢查函式與 CLI 入口點。"""
    report = verify_all_configs(PROJECT_ROOT)
    assert report["all_passed"] is True
    assert report["idle_compaction"]["passed"] is True
    assert report["security_guidance"]["passed"] is True

    # 測試 CLI main() 執行
    monkeypatch.setattr(sys, "argv", ["verify_claude_security_config.py", "--target-dir", str(PROJECT_ROOT)])
    exit_code = main()
    assert exit_code == 0
