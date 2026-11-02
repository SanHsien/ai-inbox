#!/usr/bin/env python3
"""
tests/test_zero_build_hero_injector_template.py
測試 templates/zero-build-hero-injector-skill.md（T-20261031-06）。

範本裡的程式碼不是只被「讀」：測試把範本內的骨架、注入腳本、四個 GLSL 模板與 verify_hero.py
從 Markdown 抽出來，組成真正的 HTML，用真實瀏覽器跑。

A. 靜態（永遠執行）：區塊齊全、流程圖與標題對得上、範本只引用存在的模板、不依賴本 repo 路徑、
   verify_hero.py 可編譯且在缺少輸入／套件時回結束碼 2（不是通過）。
B. 瀏覽器（需要 playwright 與能建立 WebGL 的瀏覽器；否則 skipTest 並寫明原因）：
   - 模板 A～D 組好後 verify_hero.py 全部 exit 0；
   - 壞輸入必須 exit 1：GLSL 打爛、佔位字串沒填、著色器不使用 u_mouse；
   - 把注入腳本改壞（恢復時不重建 Program、不處理 contextlost、不釋放資源、忽略 reduced-motion、
     迴圈不啟動、滑鼠不送進 uniform、刪掉 pointermove 監聽）時 verify_hero.py 必須 exit 1；
   - 編譯失敗時 canvas 隱藏、data-hero-state=error、zerohero:statechange 有觸發。
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import shader_e2e_support as e2e  # noqa: E402
import verify_no_slop as vns  # noqa: E402

TEMPLATE_PATH = REPO_ROOT / "templates" / "zero-build-hero-injector-skill.md"
FILL = {
    "__HERO_KICKER__": "kicker",
    "__HERO_TITLE__": "Title",
    "__HERO_DESCRIPTION__": "description",
    "__PRIMARY_CTA_LINK__": "#start",
    "__PRIMARY_CTA_TEXT__": "Start",
}
PLACEHOLDER_RE = re.compile(r"__[A-Z][A-Z0-9_]+__")


def extract(md: str, name: str, lang: str) -> str:
    m = re.search(r"<!-- block:%s -->\n```%s\n(.*?)\n```" % (re.escape(name), lang), md, re.S)
    if not m:
        raise AssertionError(f"範本缺少區塊 block:{name}")
    return m.group(1)


class Parts:
    def __init__(self, md: str):
        self.skeleton = extract(md, "skeleton", "html")
        self.injector = extract(md, "injector", "html")
        self.verify = extract(md, "verify_hero.py", "python")
        self.glsl: Dict[str, str] = {k: extract(md, f"glsl-{k}", "glsl") for k in "ABCD"}

    def assemble(self, fs: str, *, fill: bool = True, injector: str | None = None) -> str:
        inj = (injector or self.injector).replace("__SELECTED_FS_CODE__", fs)
        body = self.skeleton + "\n" + inj
        if fill:
            for k, v in FILL.items():
                body = body.replace(k, v)
        return ("<!doctype html><html><head><meta charset=utf-8><title>t</title></head>"
                "<body style='margin:0'>" + body + "</body></html>")


# mutation: (名稱, [(old, new)], 說明)
INJECTOR_MUTANTS: List[Tuple[str, List[Tuple[str, str]]]] = [
    ("context 恢復後不重建 Program",
     [("try { build(); resize(); } catch (err) { fail(err); return; }", "try { resize(); } catch (err) { fail(err); return; }")]),
    ("webglcontextlost 監聽刪除",
     [("canvas.addEventListener('webglcontextlost', onLost);", "")]),
    ("遺失時不丟掉舊物件參考（恢復時對失效物件 delete*）",
     [("program = vs = fs = buffer = null;   // 舊物件已失效：只丟參考，不要 delete*", "")]),
    ("dispose 不釋放 GL 資源",
     [("    release();\n    sync();\n  }\n\n  // ---- 啟動", "    sync();\n  }\n\n  // ---- 啟動")]),
    ("dispose 不移除 pointermove 監聽",
     [("window.removeEventListener('pointermove', onPointer);", "")]),
    ("prefers-reduced-motion 被忽略",
     [("reduceMotion = !!(motionQuery && motionQuery.matches);", "reduceMotion = false;")]),
    ("渲染迴圈不啟動",
     [("if (!rafId) { lastT = null; rafId = requestAnimationFrame(loop); }", "")]),
    ("游標位置沒有送進 uniform",
     [("gl.uniform2f(uMouse, (mouseX - r.left) * sx, (r.bottom - mouseY) * sy);", "gl.uniform2f(uMouse, 0.0, 0.0);")]),
    ("pointermove 監聽刪除",
     [("window.addEventListener('pointermove', onPointer, { passive: true });", "")]),
]

# 每個突變在 verify_hero.py 輸出中必須出現的失敗原因；避免「因為別的原因 exit 1」或腳本自己崩潰被算成抓到
EXPECTED_FAILURE: Dict[str, str] = {
    "context 恢復後不重建 Program": "context 沒有恢復到 running",
    "webglcontextlost 監聽刪除": "context 遺失事件沒有被處理",
    "遺失時不丟掉舊物件參考（恢復時對失效物件 delete*）": "INVALID_OPERATION: delete",
    "dispose 不釋放 GL 資源": "dispose() 沒有 deleteProgram",
    "dispose 不移除 pointermove 監聽": "dispose() 後 pointermove 監聽仍在運作",
    "prefers-reduced-motion 被忽略": "prefers-reduced-motion 時應為 static",
    "渲染迴圈不啟動": "渲染迴圈沒有持續繪製",
    "游標位置沒有送進 uniform": "滑鼠移動只改變",
    "pointermove 監聽刪除": "滑鼠移動只改變",
}


def apply(source: str, edits: List[Tuple[str, str]]) -> str:
    for old, new in edits:
        if source.count(old) != 1:
            raise AssertionError(f"突變目標在範本中出現 {source.count(old)} 次（應為 1）：{old[:70]!r}")
        source = source.replace(old, new)
    return source


class TestTemplateStatic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not TEMPLATE_PATH.is_file():
            raise AssertionError(f"範本不存在：{TEMPLATE_PATH}")
        cls.md = TEMPLATE_PATH.read_text(encoding="utf-8")
        cls.parts = Parts(cls.md)

    def test_frontmatter(self):
        m = re.match(r"---\n(.*?)\n---\n", self.md, re.S)
        self.assertIsNotNone(m, "缺少 YAML frontmatter")
        fm = m.group(1)
        self.assertRegex(fm, r"(?m)^name:\s*zero-build-hero-injector\s*$")
        self.assertRegex(fm, r"(?m)^description:\s*\S")
        self.assertRegex(fm, r"(?m)^triggers:\s*$")
        self.assertGreaterEqual(len(re.findall(r"(?m)^  - ", fm)), 3)

    def test_flow_chart_matches_headings(self):
        chart = re.search(r"```text\n(┌.*?┘)\n```", self.md, re.S).group(1)
        chart_steps = dict(re.findall(r"\[ 步驟 (\d)：([^\]]+?) \]", chart))
        heading_steps = dict(re.findall(r"(?m)^### 步驟 (\d)：(.+)$", self.md))
        self.assertEqual(sorted(chart_steps), ["1", "2", "3", "4", "5"])
        self.assertEqual(sorted(heading_steps), ["1", "2", "3", "4", "5"])
        for n in chart_steps:
            self.assertEqual(chart_steps[n].strip(), heading_steps[n].strip(), f"步驟 {n} 流程圖與標題不一致")

    def test_only_defined_templates_are_referenced(self):
        defined = set(re.findall(r"(?m)^### 模板 ([A-Z])：", self.md))
        self.assertEqual(defined, set("ABCD"))
        referenced = set(re.findall(r"模板 ([A-Z])\b", self.md))
        self.assertTrue(referenced <= defined, f"引用了不存在的模板：{referenced - defined}")
        for k in "ABCD":
            self.assertGreater(len(self.parts.glsl[k]), 300, f"模板 {k} 內容過短")

    def test_promises_are_scoped_honestly(self):
        self.assertIn("沒有提供", self.md)
        self.assertIn("不是 Hacktemplates", self.md)
        self.assertIn("7b019b5debdf0b2b0e92eb475c8d76793162103f", self.md)
        self.assertIn("MIT", self.md)
        # frontmatter 不得宣稱沒有的模板
        fm = self.md.split("---")[1]
        self.assertNotIn("Raymarching 空間", fm)

    def test_glsl_templates_use_only_declared_uniforms_and_have_colour_hooks(self):
        for k, code in self.parts.glsl.items():
            with self.subTest(template=k):
                uniforms = set(re.findall(r"(?m)^uniform\s+\w+\s+(\w+);", code))
                self.assertEqual(uniforms, {"u_resolution", "u_time", "u_mouse"})
                self.assertIn("u_mouse", re.sub(r"(?m)^uniform.*$", "", code), "著色器內文沒有使用 u_mouse")
                self.assertIn("換色", code)
                self.assertNotIn("`", code)
                self.assertNotIn("${", code)

    def test_placeholders_are_documented_and_injector_slot_exists(self):
        in_skeleton = set(PLACEHOLDER_RE.findall(self.parts.skeleton))
        self.assertEqual(in_skeleton, set(FILL))
        for ph in in_skeleton:
            self.assertIn(f"`{ph}`", self.md.split("### 步驟 3")[0], f"步驟 2 沒有說明 {ph}")
        self.assertEqual(self.parts.injector.count("__SELECTED_FS_CODE__"), 1)

    def test_no_repo_specific_dependency_in_copied_blocks(self):
        for name in ("skeleton", "injector", "verify"):
            block = getattr(self.parts, name)
            with self.subTest(block=name):
                self.assertNotIn("tools/", block)
                self.assertNotIn("ai-inbox", block)
                self.assertNotRegex(block, r"[A-Za-z]:\\Users\\")
        # 文件中提到 repo 工具時，必須同時說明它只在 ai-inbox 內
        for m in re.finditer(r"tools/verify_no_slop\.py", self.md):
            window = self.md[max(0, m.start() - 200): m.end() + 200]
            self.assertIn("只存在於 ai-inbox", window)

    def test_install_steps_present(self):
        self.assertIn("pip install playwright", self.md)
        self.assertIn("playwright install chromium", self.md)

    def test_injector_does_not_advertise_missing_features(self):
        """第一版範本宣稱 Dispose、編譯錯誤回報卻沒有實作；這裡要求注入腳本真的含這些呼叫。"""
        inj = self.parts.injector
        for needle in ("deleteProgram", "deleteShader", "deleteBuffer", "LINK_STATUS", "COMPILE_STATUS",
                       "getShaderInfoLog", "getProgramInfoLog", "removeEventListener", "cancelAnimationFrame"):
            self.assertIn(needle, inj)

    def test_anti_slop_on_skeleton_and_doc(self):
        violations = vns.scan_text(self.md, str(TEMPLATE_PATH))
        self.assertEqual(violations, [], [f"{v.rule_id}: {v.matched_text}" for v in violations])

    def test_verify_script_compiles_and_reports_environment_problems_with_exit_2(self):
        compile(self.parts.verify, "verify_hero.py", "exec")
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "verify_hero.py"
            script.write_text(self.parts.verify, encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(script), str(Path(tmp) / "missing.html")],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            # 套件不存在時：以 sys.modules[...] = None 模擬 ImportError，必須 exit 2 而不是通過
            page = Path(tmp) / "p.html"
            page.write_text("<html></html>", encoding="utf-8")
            code = (
                "import sys, runpy; sys.modules['playwright'] = None; sys.modules['playwright.sync_api'] = None; "
                f"sys.argv = ['verify_hero.py', r'{page}']; "
                f"sys.exit(runpy.run_path(r'{script}', run_name='__main__') and 0)"
            )
            r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("Playwright", r.stderr)

    def test_expected_failure_table_covers_all_mutants(self):
        self.assertEqual({n for n, _ in INJECTOR_MUTANTS}, set(EXPECTED_FAILURE))

    def test_mutation_targets_exist(self):
        for name, edits in INJECTOR_MUTANTS:
            with self.subTest(mutant=name):
                self.assertNotEqual(apply(self.parts.injector, edits), self.parts.injector)


class TestTemplateInBrowser(unittest.TestCase):
    """沒有 playwright／瀏覽器時整個類別 skip（含原因），不會變紅也不會靜默通過。"""

    @classmethod
    def setUpClass(cls):
        cls.session = e2e.shared_session()         # 可能 raise SkipTest（沒有 playwright／瀏覽器）
        cls.channel = cls.session.channel
        cls.md = TEMPLATE_PATH.read_text(encoding="utf-8")
        cls.parts = Parts(cls.md)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.verify = Path(cls.tmp.name) / "verify_hero.py"
        cls.verify.write_text(cls.parts.verify, encoding="utf-8")
        cls._n = 0

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def write_page(self, html: str) -> Path:
        type(self)._n += 1
        p = Path(self.tmp.name) / f"page_{type(self)._n}.html"
        p.write_text(html, encoding="utf-8")
        return p

    def run_verify(self, page: Path) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONUTF8="1")
        r = subprocess.run([sys.executable, "-I", str(self.verify), str(page), "--channel", self.channel],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240, env=env)
        if r.returncode == 2:
            self.skipTest("verify_hero.py 回報環境問題（exit 2）：" + r.stderr.strip()[:200])
        return r

    def test_each_template_passes_verification(self):
        pages = {k: self.write_page(self.parts.assemble(self.parts.glsl[k])) for k in "ABCD"}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            results = {k: ex.submit(self.run_verify, p) for k, p in pages.items()}
        for k, fut in results.items():
            r = fut.result()
            self.assertEqual(r.returncode, 0, f"模板 {k} 驗證失敗：\n{r.stdout}{r.stderr}")
            self.assertIn("[PASS]", r.stdout)

    def test_bad_inputs_fail_verification(self):
        a = self.parts.glsl["A"]
        cases = {
            "GLSL 打爛": (self.parts.assemble("not glsl"), "狀態不是 running"),
            "佔位字串沒填": (self.parts.assemble(a, fill=False), "殘留未填的佔位字串"),
            "著色器完全不使用 u_mouse": (self.parts.assemble(apply(a, [("+ ripple(st, m);", ";")])), "滑鼠移動只改變"),
        }
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            futs = {n: ex.submit(self.run_verify, self.write_page(html)) for n, (html, _) in cases.items()}
        for n, fut in futs.items():
            r = fut.result()
            self.assertEqual(r.returncode, 1, f"{n} 應該驗證失敗：\n{r.stdout}{r.stderr}")
            self.assertIn(cases[n][1], r.stdout, f"{n}：失敗原因不符\n{r.stdout}")

    def test_broken_injector_is_caught(self):
        a = self.parts.glsl["A"]
        pages = {name: self.write_page(self.parts.assemble(a, injector=apply(self.parts.injector, edits)))
                 for name, edits in INJECTOR_MUTANTS}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            futs = {n: ex.submit(self.run_verify, p) for n, p in pages.items()}
        survivors = [n for n, fut in futs.items() if fut.result().returncode == 0]
        self.assertEqual(survivors, [], f"verify_hero.py 沒有抓到這些壞掉的注入腳本：{survivors}")
        for n, fut in futs.items():
            r = fut.result()
            self.assertEqual(r.returncode, 1, f"{n}：應為 exit 1\n{r.stdout}{r.stderr}")
            self.assertNotIn("Traceback", r.stderr, f"{n}：verify_hero.py 自己崩潰，不算抓到\n{r.stderr}")
            self.assertIn("[FAIL]", r.stdout)
            self.assertIn(EXPECTED_FAILURE[n], r.stdout, f"{n}：失敗原因不符（預期含 {EXPECTED_FAILURE[n]!r}）\n{r.stdout}")

    def test_compile_error_degrades_and_reports(self):
        page_path = self.write_page(self.parts.assemble("not glsl"))
        page, logs = self.session.open(page_path.resolve().as_uri(), wait_ms=500)
        try:
            st = page.evaluate("() => window.ZeroHero.getState()")
            self.assertEqual(st["status"], "error")
            self.assertIn("編譯失敗", st["error"])
            self.assertEqual(page.get_attribute("#zero-hero-canvas", "data-hero-state"), "error")
            self.assertEqual(page.evaluate("() => getComputedStyle(document.getElementById('zero-hero-canvas')).display"), "none")
            self.assertTrue(any("[zero-hero]" in x and "編譯失敗" in x for x in logs), logs)
            self.assertFalse(any(x.startswith("pageerror") for x in logs), logs)
        finally:
            page.context.close()

    def test_statechange_event_is_dispatched(self):
        page_path = self.write_page(self.parts.assemble(self.parts.glsl["B"]))
        ctx = self.session.browser.new_context(viewport={"width": 320, "height": 180})
        page = ctx.new_page()
        try:
            page.add_init_script(
                "window.__events = []; document.addEventListener('zerohero:statechange', e => window.__events.push(e.detail.state), true);")
            page.goto(page_path.resolve().as_uri(), wait_until="load")
            page.wait_for_timeout(800)
            page.evaluate("() => window.ZeroHero.dispose()")
            events = page.evaluate("() => window.__events")
            self.assertIn("running", events)
            self.assertEqual(events[-1], "disposed")
            self.assertEqual(page.get_attribute("#zero-hero-canvas", "data-hero-state"), "disposed")
        finally:
            ctx.close()

    def test_no_webgl_degrades(self):
        page_path = self.write_page(self.parts.assemble(self.parts.glsl["A"]))
        page, logs = self.session.open(page_path.resolve().as_uri(), no_webgl=True, spy=False, wait_ms=400)
        try:
            self.assertEqual(page.evaluate("() => window.ZeroHero.getState().status"), "nowebgl")
            self.assertEqual(page.evaluate("() => getComputedStyle(document.getElementById('zero-hero-canvas')).display"), "none")
            self.assertFalse(any(x.startswith("pageerror") for x in logs), logs)
        finally:
            page.context.close()


if __name__ == "__main__":
    unittest.main()
