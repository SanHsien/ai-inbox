"""tools/render_artifact_html.py 的單元測試：編譯、表格、跳脫（XSS）、確定性、自包含。"""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "render_artifact_html.py"
sys.path.insert(0, str(TOOL.parent))
import render_artifact_html as r  # noqa: E402

PAYLOAD = '<script>alert(1)</script><img src=x onerror=alert(2)>'

SAMPLE = """---
title: 方案比較
---
## 結論
選 **方案 B**，指令 `make test`。

- 項目一
- 項目二

1. 先做
2. 再做

| 方案 | 成本 | 風險 |
|---|---|---|
| A | ok | no |
| B | warn | ok |

```python
print("hi")
```

```flow LR
輸入 -> 解析 -> 輸出
```

```callout warn
注意這一點。
```

```ask q1
要用哪個方案？ (single)
- 方案 A
- 方案 B
```
"""


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))


def parse(doc):
    p = _Tags()
    p.feed(doc)
    return p


class RenderTest(unittest.TestCase):
    def test_basic_blocks(self):
        doc = r.render(SAMPLE)
        self.assertIn("<h2>結論</h2>", doc)
        self.assertIn("<strong>方案 B</strong>", doc)
        self.assertIn("<code>make test</code>", doc)
        self.assertIn("<ul><li>項目一</li><li>項目二</li></ul>", doc)
        self.assertIn("<ol><li>先做</li><li>再做</li></ol>", doc)
        self.assertIn('<span class="lang">python</span>', doc)
        self.assertIn('print(&quot;hi&quot;)', doc)
        self.assertIn('<aside class="callout warn">注意這一點。</aside>', doc)
        self.assertIn("<title>方案比較</title>", doc)

    def test_table_structure_and_marks(self):
        doc = r.render(SAMPLE)
        self.assertEqual(doc.count("<th>"), 3)
        self.assertEqual(doc.count("<tr>"), 3)  # 表頭 1 + 資料 2
        self.assertIn('<td class="ok">✓</td>', doc)
        self.assertIn('<td class="no">✗</td>', doc)
        self.assertIn('<td class="warn">!</td>', doc)
        self.assertIn("<td>A</td>", doc)

    def test_table_short_row_is_padded(self):
        doc = r.render("| a | b |\n|---|---|\n| only |\n")
        self.assertEqual(doc.count("<td"), 2)

    def test_flow_chain(self):
        doc = r.render(SAMPLE)
        self.assertEqual(doc.count('class="node"'), 3)
        self.assertEqual(doc.count('class="arrow"'), 2)

    def test_ask_and_feedback_button(self):
        doc = r.render(SAMPLE)
        self.assertIn('type="radio"', doc)  # (single)
        self.assertEqual(doc.count('name="q1"'), 2)
        self.assertIn('id="fbcopy"', doc)
        self.assertIn("navigator.clipboard", doc)
        self.assertNotIn("(single)", doc)

    def test_no_ask_means_no_script_or_button(self):
        doc = r.render("# 只有文字\n\n內容\n")
        self.assertNotIn("<script", doc)
        self.assertNotIn("fbcopy", doc)

    def test_title_falls_back_to_first_heading(self):
        self.assertIn("<title>標題 X</title>", r.render("## 標題 **X**\n".replace("**", "")))

    def test_unclosed_fence_does_not_crash(self):
        doc = r.render("```python\nprint(1)\n")
        self.assertIn("<pre>", doc)

    def test_crlf_same_as_lf(self):
        self.assertEqual(r.render(SAMPLE), r.render(SAMPLE.replace("\n", "\r\n")))


class SafetyTest(unittest.TestCase):
    def assert_no_live_payload(self, doc, where):
        self.assertNotIn("<script>alert", doc, where)
        self.assertNotIn("<img", doc, where)
        self.assertNotIn("onerror=", doc.replace("onerror=alert(2)&gt;", ""), where)
        p = parse(doc)
        self.assertNotIn("img", p.tags, where)
        for tag, attrs in p.attrs:
            for name in attrs:
                self.assertFalse(name.startswith("on"), f"{where}: {tag} 有事件屬性 {name}")

    def test_payload_in_every_position_is_escaped(self):
        cases = {
            "段落": f"{PAYLOAD}\n",
            "標題": f"## {PAYLOAD}\n",
            "清單": f"- {PAYLOAD}\n",
            "表格": f"| a |\n|---|\n| {PAYLOAD} |\n",
            "表頭": f"| {PAYLOAD} |\n|---|\n| x |\n",
            "程式碼": f"```js\n{PAYLOAD}\n```\n",
            "圍欄語言": f"```{PAYLOAD}\nx\n```\n",
            "flow": f"```flow\n{PAYLOAD} -> b\n```\n",
            "callout": f"```callout\n{PAYLOAD}\n```\n",
            "ask 問題": f"```ask\n{PAYLOAD}\n- x\n```\n",
            "ask 選項": f"```ask\nq\n- {PAYLOAD}\n```\n",
            "ask id": f"```ask {PAYLOAD}\nq\n- x\n```\n",
            "frontmatter 標題": f"---\ntitle: {PAYLOAD}\n---\n本文\n",
            "行內粗體": f"**{PAYLOAD}**\n",
        }
        for where, src in cases.items():
            with self.subTest(where=where):
                doc = r.render(src)
                self.assert_no_live_payload(doc, where)
                if where not in ("圍欄語言", "ask id"):  # 這兩處不是被跳脫，而是整段被丟棄／濾掉
                    self.assertIn("&lt;", doc)

    def test_attribute_breakout_in_ask_and_title(self):
        doc = r.render('---\ntitle: a" onmouseover="alert(1)\n---\n```ask\nq" onclick="x\n- o" autofocus="\n```\n')
        for tag, attrs in parse(doc).attrs:
            self.assertFalse(any(k in attrs for k in ("onmouseover", "onclick", "autofocus")), tag)

    def test_links_and_raw_html_are_not_supported(self):
        doc = r.render("[x](javascript:alert(1))\n\n<a href=\"javascript:alert(1)\">y</a>\n")
        p = parse(doc)
        self.assertNotIn("a", p.tags)
        for _tag, attrs in p.attrs:
            self.assertNotIn("href", attrs)
        self.assertIn("&lt;a href=", doc)


class StructureTest(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(r.render(SAMPLE), r.render(SAMPLE))

    def test_cli_twice_gives_identical_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.md"
            src.write_text(SAMPLE, encoding="utf-8")
            outs = []
            for n in range(2):
                out = Path(d) / f"o{n}.html"
                proc = subprocess.run([sys.executable, str(TOOL), str(src), "-o", str(out)], capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))
                outs.append(out.read_bytes())
            self.assertEqual(outs[0], outs[1])
            self.assertTrue(outs[0].startswith(b"<!DOCTYPE html>"))

    def test_different_input_different_output(self):
        self.assertNotEqual(r.render("# a\n"), r.render("# b\n"))

    def test_self_contained(self):
        doc = r.render(SAMPLE)
        p = parse(doc)
        self.assertNotIn("link", p.tags)
        for tag, attrs in p.attrs:
            self.assertNotIn("src", attrs, tag)
            self.assertNotIn("href", attrs, tag)
        self.assertIsNone(re.search(r"https?://", doc))
        self.assertIn("Content-Security-Policy", doc)
        self.assertEqual(doc.count("<script>"), doc.count("</script>"))
        self.assertTrue(doc.rstrip().endswith("</html>"))

    def test_well_formed_nesting(self):
        class Balance(HTMLParser):
            VOID = {"meta", "input", "br", "img", "link"}

            def __init__(self):
                super().__init__()
                self.stack, self.errors = [], []

            def handle_starttag(self, tag, attrs):
                if tag not in self.VOID:
                    self.stack.append(tag)

            def handle_endtag(self, tag):
                if not self.stack or self.stack[-1] != tag:
                    self.errors.append(tag)
                else:
                    self.stack.pop()

        b = Balance()
        b.feed(r.render(SAMPLE))
        self.assertEqual(b.errors, [])
        self.assertEqual(b.stack, [])

    def test_help_utf8_under_cp950(self):
        env = {**os.environ, "PYTHONIOENCODING": "cp950", "PYTHONUTF8": "0"}
        proc = subprocess.run([sys.executable, str(TOOL), "--help"], capture_output=True, env=env)
        self.assertEqual(proc.returncode, 0)
        proc.stdout.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
