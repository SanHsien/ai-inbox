#!/usr/bin/env python3
"""
tests/test_shader_hero_demo.py
測試 assets/shader-hero-demo/index.html（T-20261031-05）。

分三層：
A. 靜態檢查（永遠執行，只用標準函式庫）：檔案基礎結構、零外部依賴、Anti-Slop、突變測試的目標字串仍存在。
   這一層只能證明「檔案長什麼樣」，不能證明「會動」，所以不是主要證據。
B. 瀏覽器端到端（Playwright + 真實 Edge/Chrome/Chromium，SwiftShader 軟體渲染）：
   - 逐幀繪製、畫面非空白、FPS 顯示值與頁面實際繪製幀數／經過時間相符（把 rAF 節流到約 17 FPS 再比，
     所以寫死 60 之類的假值必定不符）；
   - 預設液態金屬模式與流體模式的游標互動：用像素差證明（真實 mouse.move，不是直接塞 uniform）；
   - 透過頁面按鈕模擬 WEBGL_lose_context：遺失期間停止繪製，恢復後 Program 必須重建，畫面與遺失前一致；
   - dispose 後 delete* 真的被呼叫、迴圈停止、監聽器移除；
   - prefers-reduced-motion（開頁時與執行中切換）；
   - 無 WebGL、著色器編譯失敗時畫面上如實顯示錯誤，而不是仍寫「正常執行中」。
   **預設不執行**（含瀏覽器的全套約 4～5 分鐘，機器忙時會逾時）：設環境變數 AI_INBOX_BROWSER_TESTS=1 才跑，
   例如 bash：  AI_INBOX_BROWSER_TESTS=1 python -m unittest tests.test_shader_hero_demo -v
   PowerShell： $env:AI_INBOX_BROWSER_TESTS = "1"; python -m unittest tests.test_shader_hero_demo -v
   沒設、沒有 playwright 套件、或沒有能建立 WebGL 的瀏覽器時，整個 B 層 skipTest 並寫明原因（不是靜默通過）。
   逾時（SHADER_E2E_TIMEOUT 秒，預設 240）不算斷言失敗，標成 skip「INCOMPLETE（逾時 N 秒）」。
C. 突變測試（需要瀏覽器）：把 index.html 刻意改壞（GLSL 打爛、渲染迴圈不啟動、drawArrays 停用、游標效果移除、
   contextlost 監聽刪除、恢復時不重建 Program、dispose 不釋放、reduced-motion 被忽略、錯誤被顯示成成功等），
   同一組 probe 必須全部報錯。若有突變存活，測試失敗。

門檻（畫面標準差、像素差比例）是本 repo 對 320x180 SwiftShader 畫面的自訂取捨，不是外部標準。
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Callable, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import shader_e2e_support as e2e  # noqa: E402
import verify_generative_ui_assets as vui  # noqa: E402
import verify_no_slop as vns  # noqa: E402

DEMO_PATH = REPO_ROOT / "assets" / "shader-hero-demo" / "index.html"
API = "__SHADER_HERO_DEMO__"

# 本 repo 自訂門檻（見模組 docstring）
MIN_LUMA_STDEV = 3.0        # 低於此值視為單色／空白畫面
MIN_LUMA_MAX = 20.0         # 最亮點低於此值視為全黑
MIN_MOUSE_CHANGE = 0.02     # 游標移動後至少 2% 取樣點的顏色改變
MIN_TIME_CHANGE = 0.02      # 時間改變後至少 2% 取樣點的顏色改變
MAX_NOISE = 0.01            # 同狀態重畫的雜訊上限（超過代表量測不可靠）
FPS_REL_TOL = 0.30          # FPS 顯示值與實測值的相對容許誤差（顯示值是最近 500ms 的平均，實測是整段平均）
FPS_ABS_TOL = 3.0           # 或絕對容許誤差（fps），取兩者較大
# 把 requestAnimationFrame 節流成每次延遲 40ms，讓實際 FPS 落在約 17 左右，遠離常見的 60
THROTTLE_RAF = "(() => { const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = cb => setTimeout(() => raf(cb), 40); })();"


# --------------------------------------------------------------------------- probes
# 每個 probe 回傳「問題清單」；空清單代表通過。真實檔案必須回傳 []，突變檔案必須回傳非空。

def _state(page) -> Dict:
    return page.evaluate(f"() => window['{API}'].getState()")


def probe_render(session: e2e.BrowserSession, url: str) -> List[str]:
    problems: List[str] = []
    page, logs = session.open(url, wait_ms=1200)
    try:
        st = _state(page)
        if st["status"] != "running":
            problems.append(f"狀態不是 running：{st['status']}（failed={st['failedMessage']}）")
        d1 = e2e.spy_counts(page)["draws"]
        page.wait_for_timeout(700)
        d2 = e2e.spy_counts(page)["draws"]
        if d2 - d1 < 3:
            problems.append(f"渲染迴圈沒有持續繪製：700ms 內 drawArrays 只增加 {d2 - d1} 次")
        fps_text = page.inner_text("#fps-display").strip()
        if not (fps_text.isdigit() and int(fps_text) > 0):
            problems.append(f"FPS 顯示不是正整數（是否與實測相符由 probe_fps 檢查）：'{fps_text}'")
        page.evaluate(f"() => window['{API}'].freezeTime(5.0)")
        frame = e2e.sample(page, API)
        if frame is None:
            problems.append("無法繪製／讀取畫面")
        else:
            stats = e2e.luminance_stats(frame)
            if stats["stdev"] < MIN_LUMA_STDEV:
                problems.append(f"畫面接近單色（亮度標準差 {stats['stdev']:.2f}）")
            if stats["max"] < MIN_LUMA_MAX:
                problems.append(f"畫面幾乎全黑（最亮 {stats['max']:.1f}）")
            if frame["glError"] != 0:
                problems.append(f"gl.getError() = {frame['glError']}")
            page.evaluate(f"() => window['{API}'].freezeTime(1.0)")
            f1 = e2e.sample(page, API)
            page.evaluate(f"() => window['{API}'].freezeTime(7.0)")
            f2 = e2e.sample(page, API)
            if f1 is None or f2 is None or e2e.changed_fraction(f1, f2) < MIN_TIME_CHANGE:
                problems.append("u_time 改變後畫面沒有變化（動畫沒有時間相依）")
        brand = page.inner_text(".brand-mark")
        if "dvk" in brand.lower():
            problems.append(f"頁面品牌標示 '{brand}' 容易被誤認為 dvklab 原作")
        body = page.inner_text("body")
        if "自行撰寫" not in body:
            problems.append("頁面沒有標示這是自製示範")
        if logs:
            problems.append(f"console 有錯誤或警告：{logs[:2]}")
    finally:
        page.context.close()
    return problems


def probe_fps(session: e2e.BrowserSession, url: str) -> List[str]:
    """顯示的 FPS 必須等於頁面實際繪製速率：用 drawnFrames 差除以經過時間，與 HUD 顯示值比對。"""
    problems: List[str] = []
    page, logs = session.open(url, wait_ms=1500, init_scripts=[THROTTLE_RAF])
    try:
        grab = f"() => ({{ frames: window['{API}'].getState().drawnFrames, now: performance.now() }})"
        a = page.evaluate(grab)
        page.wait_for_timeout(2000)
        b = page.evaluate(grab)
        shown_text = page.inner_text("#fps-display").strip()
        measured = (b["frames"] - a["frames"]) * 1000.0 / (b["now"] - a["now"])
        if not (10 <= measured <= 30):
            problems.append(f"節流後實測 FPS {measured:.1f} 不在預期的 10～30，無法比對顯示值")
        elif not shown_text.isdigit():
            problems.append(f"FPS 顯示不是數字：'{shown_text}'")
        else:
            shown = float(shown_text)
            tol = max(FPS_ABS_TOL, FPS_REL_TOL * measured)
            if abs(shown - measured) > tol:
                problems.append(f"FPS 顯示 {shown:g} 與實測 {measured:.1f} 相差超過容許 {tol:.1f}（顯示值不是實測？）")
    finally:
        page.context.close()
    return problems


def probe_mouse(session: e2e.BrowserSession, url: str) -> List[str]:
    problems: List[str] = []
    page, logs = session.open(url, wait_ms=800)
    try:
        page.evaluate(f"() => window['{API}'].freezeTime(5.0)")
        for mode, label in ((0, "液態金屬(預設)"), (1, "流體")):
            page.evaluate(f"(m) => window['{API}'].setMode(m)", mode)
            page.mouse.move(60, 40)
            if not e2e.wait_mouse_converged(page, API, tol=0.02):
                problems.append(f"{label}：游標平滑值沒有追上滑鼠位置（pointermove 沒有被處理？）")
                continue
            a = e2e.sample(page, API)
            page.mouse.move(250, 140)
            if not e2e.wait_mouse_converged(page, API, tol=0.02):
                problems.append(f"{label}：第二個游標位置沒有收斂")
                continue
            b = e2e.sample(page, API)
            b2 = e2e.sample(page, API)
            if a is None or b is None or b2 is None:
                problems.append(f"{label}：無法讀取畫面")
                continue
            noise = e2e.changed_fraction(b, b2)
            if noise > MAX_NOISE:
                problems.append(f"{label}：同狀態重畫雜訊 {noise:.4f} 過高，量測不可靠")
            change = e2e.changed_fraction(a, b)
            if change < MIN_MOUSE_CHANGE:
                problems.append(f"{label}：游標從 (60,40) 移到 (250,140) 只改變 {change:.4f} 的像素，游標互動無效")
    finally:
        page.context.close()
    return problems


def probe_restore(session: e2e.BrowserSession, url: str) -> List[str]:
    problems: List[str] = []
    page, logs = session.open(url, wait_ms=800)
    try:
        page.evaluate(f"() => window['{API}'].freezeTime(5.0)")
        page.mouse.move(100, 60)
        e2e.wait_mouse_converged(page, API, tol=0.02)
        before = e2e.sample(page, API)
        if before is None:
            return ["遺失前就無法繪製"]
        links_before = e2e.spy_counts(page)["linkProgram"]

        page.evaluate("() => document.getElementById('btn-toggle-sim').click()")
        lost_seen = False
        for _ in range(30):
            page.wait_for_timeout(100)
            if _state(page)["contextLost"]:
                lost_seen = True
                break
        if not lost_seen:
            problems.append("按下模擬按鈕後，頁面沒有進入 contextLost 狀態（webglcontextlost 沒被處理）")
            return problems
        st = _state(page)
        if st["status"] != "lost" or st["running"]:
            problems.append(f"遺失期間狀態應為 lost 且停止迴圈：{st['status']} running={st['running']}")
        if "遺失" not in page.inner_text("#lifecycle-status"):
            problems.append("遺失期間畫面狀態文字沒有反映 context 遺失")
        d1 = e2e.spy_counts(page)["draws"]
        page.wait_for_timeout(300)
        if e2e.spy_counts(page)["draws"] != d1:
            problems.append("context 遺失期間仍在呼叫 drawArrays")

        restored = False
        for _ in range(60):
            page.wait_for_timeout(100)
            st = _state(page)
            if not st["contextLost"] and st["status"] == "running":
                restored = True
                break
        if not restored:
            problems.append(f"context 沒有恢復到 running：{_state(page)['status']}")
            return problems
        counts = e2e.spy_counts(page)
        if counts["linkProgram"] != links_before + 1:
            problems.append(f"恢復後沒有重新連結 Program（link 次數 {links_before} -> {counts['linkProgram']}）")
        ok = page.evaluate(f"""() => {{
            const d = window['{API}']; const gl = d.getGL(); const p = d.getProgram();
            return !!p && gl.isProgram(p) && gl.getProgramParameter(p, gl.LINK_STATUS);
        }}""")
        if not ok:
            problems.append("恢復後 getProgram() 不是有效且已連結的 Program（仍在使用遺失前的舊物件）")
        after = e2e.sample(page, API)
        if after is None:
            problems.append("恢復後無法繪製")
        else:
            if after["glError"] != 0:
                problems.append(f"恢復後 gl.getError() = {after['glError']}")
            if e2e.luminance_stats(after)["stdev"] < MIN_LUMA_STDEV:
                problems.append("恢復後畫面是空白")
            diff = e2e.changed_fraction(before, after)
            if diff > MIN_MOUSE_CHANGE / 2:
                problems.append(f"恢復後畫面與遺失前不一致（{diff:.4f} 的像素不同）")
        d1 = e2e.spy_counts(page)["draws"]
        page.wait_for_timeout(500)
        if e2e.spy_counts(page)["draws"] - d1 < 2:
            problems.append("恢復後渲染迴圈沒有重新啟動")
        if logs:
            problems.append(f"遺失／恢復流程產生 console 錯誤或警告：{logs[:2]}")
    finally:
        page.context.close()
    return problems


def probe_dispose(session: e2e.BrowserSession, url: str) -> List[str]:
    problems: List[str] = []
    page, logs = session.open(url, wait_ms=800)
    try:
        before = e2e.spy_counts(page)
        page.evaluate(f"() => {{ window['{API}'].dispose(); window['{API}'].dispose(); }}")
        page.wait_for_timeout(100)
        after = e2e.spy_counts(page)
        if after["deleteProgram"] - before["deleteProgram"] < 1:
            problems.append("dispose 後沒有呼叫 deleteProgram")
        if after["deleteShader"] - before["deleteShader"] < 2:
            problems.append("dispose 後 deleteShader 少於 2 次（頂點與片段著色器都要釋放）")
        if after["deleteBuffer"] - before["deleteBuffer"] < 1:
            problems.append("dispose 後沒有呼叫 deleteBuffer")
        if page.evaluate(f"() => window['{API}'].getProgram()") is not None:
            problems.append("dispose 後 getProgram() 仍持有 Program")
        st = _state(page)
        if st["status"] != "disposed":
            problems.append(f"dispose 後狀態應為 disposed：{st['status']}")
        d1 = e2e.spy_counts(page)["draws"]
        page.mouse.move(10, 10)
        page.mouse.move(200, 120)
        page.wait_for_timeout(400)
        if e2e.spy_counts(page)["draws"] != d1:
            problems.append("dispose 後仍在繪製")
        if _state(page)["target"] != st["target"]:
            problems.append("dispose 後 pointermove 監聽器仍在運作")
        if logs:
            problems.append(f"dispose 流程產生 console 錯誤或警告：{logs[:2]}")
    finally:
        page.context.close()
    return problems


def probe_reduced_motion(session: e2e.BrowserSession, url: str) -> List[str]:
    problems: List[str] = []
    # 開頁時就是 reduce
    page, logs = session.open(url, reduced_motion=True, wait_ms=900)
    try:
        st = _state(page)
        if st["status"] != "static" or st["running"] or not st["reduceMotion"]:
            problems.append(f"reduce 時應為 static 且不跑迴圈：{st['status']} running={st['running']}")
        d1 = e2e.spy_counts(page)["draws"]
        if d1 < 1:
            problems.append("reduce 時沒有畫出任何靜態畫面")
        a = e2e.sample(page, API)
        page.mouse.move(30, 30)
        page.mouse.move(280, 150)
        page.wait_for_timeout(500)
        d2 = e2e.spy_counts(page)["draws"]
        if d2 - d1 > 1:   # sample() 自己會畫 1 次
            problems.append(f"reduce 時仍有連續繪製（{d2 - d1} 次）")
        b = e2e.sample(page, API)
        if a is not None and b is not None and e2e.changed_fraction(a, b) > MAX_NOISE:
            problems.append("reduce 時畫面仍隨時間或游標變動")
        if a is None or e2e.luminance_stats(a)["stdev"] < MIN_LUMA_STDEV:
            problems.append("reduce 時的靜態畫面是空白")
    finally:
        page.context.close()
    # 執行中切換
    page, logs = session.open(url, wait_ms=800)
    try:
        if not _state(page)["running"]:
            problems.append("一般偏好時迴圈沒有在跑，無法測試執行中切換")
        else:
            page.emulate_media(reduced_motion="reduce")
            page.wait_for_timeout(500)
            st = _state(page)
            if st["status"] != "static" or st["running"]:
                problems.append(f"執行中切到 reduce 後應停止迴圈：{st['status']} running={st['running']}")
            page.emulate_media(reduced_motion="no-preference")
            page.wait_for_timeout(700)
            if not _state(page)["running"]:
                problems.append("切回 no-preference 後迴圈沒有恢復")
    finally:
        page.context.close()
    return problems


def probe_no_webgl(session: e2e.BrowserSession, url: str) -> List[str]:
    problems: List[str] = []
    page, logs = session.open(url, no_webgl=True, spy=False, wait_ms=600)
    try:
        st = _state(page)
        if st["status"] != "nowebgl":
            problems.append(f"無 WebGL 時狀態應為 nowebgl：{st['status']}")
        text = page.inner_text("#lifecycle-status")
        if "WebGL" not in text or "執行中" in text:
            problems.append(f"無 WebGL 時狀態文字不誠實：{text}")
        if page.get_attribute("#lifecycle-status", "role") != "alert":
            problems.append("無 WebGL 時狀態列沒有 role=alert")
        if not page.evaluate("() => document.body.classList.contains('hero-fallback')"):
            problems.append("無 WebGL 時沒有套用 CSS 降級背景")
        if page.evaluate("() => getComputedStyle(document.getElementById('gl-canvas')).display") != "none":
            problems.append("無 WebGL 時空白畫布沒有被隱藏")
        if page.inner_text("#fps-display").strip() != "--":
            problems.append("無 WebGL 時 FPS 不該顯示數字")
        if any(entry.startswith("pageerror") for entry in logs):
            problems.append(f"無 WebGL 時出現未捕捉例外：{logs}")
    finally:
        page.context.close()
    return problems


def probe_shader_error(session: e2e.BrowserSession, url: str) -> List[str]:
    """url 必須是 GLSL 已被弄壞的版本；頁面應如實顯示編譯失敗。"""
    problems: List[str] = []
    page, logs = session.open(url, wait_ms=600)
    try:
        st = _state(page)
        text = page.inner_text("#lifecycle-status")
        if st["status"] != "error":
            problems.append(f"著色器壞掉時狀態應為 error：{st['status']}")
        if "執行中" in text or "Active" in text:
            problems.append(f"著色器壞掉卻顯示正常：{text}")
        if "編譯失敗" not in text:
            problems.append(f"狀態列沒有顯示編譯失敗原因：{text}")
        if page.get_attribute("#lifecycle-status", "role") != "alert":
            problems.append("錯誤狀態沒有 role=alert")
        if page.inner_text("#fps-display").strip() != "--":
            problems.append("著色器壞掉時 FPS 不該顯示數字")
        if not page.evaluate("() => document.body.classList.contains('hero-fallback')"):
            problems.append("著色器壞掉時沒有套用 CSS 降級背景")
        if not any("[shader-hero-demo]" in entry for entry in logs):
            problems.append("著色器壞掉時沒有 console.error 回報")
        if any(entry.startswith("pageerror") for entry in logs):
            problems.append(f"著色器壞掉時出現未捕捉例外：{logs}")
    finally:
        page.context.close()
    return problems


# --------------------------------------------------------------------------- mutants

GLSL_BREAK = ("'float hash(vec2 p) {',", "'float hash(vec2 p) { BROKEN',")

# (名稱, [(old, new), ...], 負責抓出它的 probe 名稱)
MUTANTS: List[Tuple[str, List[Tuple[str, str]], str]] = [
    ("GLSL 語法打爛", [GLSL_BREAK], "render"),
    ("渲染迴圈不啟動", [("            rafId = requestAnimationFrame(renderLoop);\n          }\n        } else {",
                          "            rafId = null;\n          }\n        } else {")], "render"),
    ("FPS 顯示寫死 60", [("if (fpsDisplay) fpsDisplay.textContent = fps;", "if (fpsDisplay) fpsDisplay.textContent = 60;")], "fps"),
    ("FPS 以固定時間窗誤算（影格數永遠算 60）", [("const fps = Math.round((frameCount * 1000) / (now - lastFpsTime));", "const fps = Math.round((60 * 1000) / (now - lastFpsTime));")], "fps"),
    ("drawArrays 停用", [("        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);\n        drawnFrames++;",
                          "        drawnFrames++;")], "render"),
    ("initGL 不執行", [("        initGL();\n\n        window.addEventListener('resize'",
                        "        window.addEventListener('resize'")], "render"),
    ("u_time 不更新", [("gl.uniform1f(uTimeLoc, t);", "gl.uniform1f(uTimeLoc, 0.0);")], "render"),
    ("液態金屬模式忽略游標（原本的缺陷）", [("return fbm(st * 1.6 + 3.0 * r) + ripple(st, m);",
                                           "return fbm(st * 1.6 + 3.0 * r);")], "mouse"),
    ("pointermove 監聽刪除", [("window.addEventListener('pointermove', onPointerMove, { passive: true });",
                              "/* removed */")], "mouse"),
    ("游標位置沒有送進 uniform", [("gl.uniform2f(uMouseLoc, currentMouseX * (canvas.width / window.innerWidth),\n"
                                  "                                (window.innerHeight - currentMouseY) * (canvas.height / window.innerHeight));",
                                  "gl.uniform2f(uMouseLoc, 0.0, 0.0);")], "mouse"),
    ("webglcontextlost 監聽刪除", [("canvas.addEventListener('webglcontextlost', onContextLost, false);",
                                    "/* removed */")], "restore"),
    ("context 恢復後不重建 Program", [("          buildPipeline();           // 舊的 Program／緩衝區在 context 遺失時已失效，必須重建\n",
                                       "")], "restore"),
    ("webglcontextrestored 監聽刪除", [("canvas.addEventListener('webglcontextrestored', onContextRestored, false);",
                                        "/* removed */")], "restore"),
    ("dispose 不釋放 GL 資源", [("        releasePipeline();\n        syncLoop();\n      }\n\n      // 7.",
                                 "        syncLoop();\n      }\n\n      // 7.")], "dispose"),
    ("dispose 不移除 pointermove 監聽", [("window.removeEventListener('pointermove', onPointerMove);",
                                         "/* removed */")], "dispose"),
    ("prefers-reduced-motion 被忽略", [("reduceMotion = !!(motionQuery && motionQuery.matches);",
                                       "reduceMotion = false;")], "reduced"),
    ("著色器失敗卻顯示執行中", [GLSL_BREAK,
                                ("setStatus('error', '著色器失敗，已改用 CSS 靜態漸層。' + failedMessage);",
                                 "setStatus('running', '執行中（WebGL 逐幀繪製）');")], "shader_error"),
    ("沒有 WebGL 卻顯示執行中", [("setStatus('nowebgl', '此環境無法建立 WebGL，已改用 CSS 靜態漸層');",
                                 "setStatus('running', '執行中（WebGL 逐幀繪製）');")], "no_webgl"),
]

PROBES: Dict[str, Callable[[e2e.BrowserSession, str], List[str]]] = {
    "render": probe_render,
    "fps": probe_fps,
    "mouse": probe_mouse,
    "restore": probe_restore,
    "dispose": probe_dispose,
    "reduced": probe_reduced_motion,
    "no_webgl": probe_no_webgl,
    "shader_error": probe_shader_error,
}


def apply_mutation(source: str, edits: List[Tuple[str, str]]) -> str:
    for old, new in edits:
        if source.count(old) != 1:
            raise AssertionError(f"突變目標字串在 index.html 中出現 {source.count(old)} 次（應為 1）：{old[:60]!r}")
        source = source.replace(old, new)
    return source


# --------------------------------------------------------------------------- A. static

class TestShaderHeroDemoStatic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEMO_PATH.is_file():
            raise AssertionError(f"展示檔案不存在: {DEMO_PATH}")
        cls.html = DEMO_PATH.read_text(encoding="utf-8")

    def test_html_baseline_and_zero_dependency(self):
        errors = vui.verify_html_baseline(self.html, "assets/shader-hero-demo/index.html")
        self.assertEqual(errors, [], f"HTML 基礎結構缺陷: {errors}")
        self.assertIn('name="viewport"', self.html)
        self.assertEqual(vui.verify_asset_security_urls(self.html, "demo"), [])
        script_srcs = re.findall(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\']', self.html, re.I)
        self.assertEqual(script_srcs, [], f"Zero-Build 禁止外部 script：{script_srcs}")

    def test_no_local_paths_or_secrets(self):
        self.assertNotRegex(self.html, r"[A-Za-z]:\\Users\\")
        self.assertNotRegex(self.html, r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]{8,}")

    def test_anti_slop(self):
        violations = vns.scan_file(DEMO_PATH)
        self.assertEqual(violations, [], [f"{v.rule_id}: {v.matched_text}" for v in violations])

    def test_slop_scanner_catches_known_bad_input(self):
        bad = self.html + '\n<div class="shadow-2xl from-indigo-500 to-purple-600">🚀 LIVE</div>'
        ids = {v.rule_id for v in vns.scan_text(bad, "bad.html")}
        self.assertTrue({"SLOP-01", "SLOP-02", "SLOP-03"} <= ids, ids)

    def test_initial_markup_hardcodes_nothing_dishonest(self):
        """初始 HTML 不得預先寫死『正常執行中』或固定 FPS／解析度。"""
        status = re.search(r'<span id="lifecycle-status"[^>]*>([^<]*)</span>', self.html).group(1)
        self.assertNotIn("正常執行", status)
        self.assertNotIn("Active", status)
        self.assertRegex(self.html, r'id="fps-display">--<')
        self.assertRegex(self.html, r'id="res-display">--<')

    def test_not_labelled_as_upstream_work(self):
        visible = re.sub(r"<!--[\s\S]*?-->|/\*[\s\S]*?\*/|<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", self.html)
        self.assertNotIn("DVK Lab", visible)
        self.assertIn("自行撰寫", visible)

    def test_mutation_targets_still_exist(self):
        """突變測試的目標字串若因重構消失，突變就變成空操作；這裡先擋住。"""
        for name, edits, _ in MUTANTS:
            with self.subTest(mutant=name):
                mutated = apply_mutation(self.html, edits)
                self.assertNotEqual(mutated, self.html)


# --------------------------------------------------------------------------- B/C. browser

@e2e.incomplete_on_timeout
class TestShaderHeroDemoBrowser(unittest.TestCase):
    """端到端：沒有 playwright 或瀏覽器時整個類別 skip，並寫明原因。"""

    @classmethod
    def setUpClass(cls):
        cls.session = e2e.shared_session()   # 可能 raise SkipTest（沒有 playwright／瀏覽器）
        cls.url = DEMO_PATH.resolve().as_uri()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.source = DEMO_PATH.read_text(encoding="utf-8")
        cls._n = 0

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def variant(self, edits: List[Tuple[str, str]]) -> str:
        type(self)._n += 1
        path = Path(self.tmp.name) / f"variant_{type(self)._n}.html"
        path.write_text(apply_mutation(self.source, edits), encoding="utf-8")
        return path.resolve().as_uri()

    def test_renders_continuously_and_honestly(self):
        self.assertEqual(probe_render(self.session, self.url), [])

    def test_fps_display_matches_actual_draw_rate(self):
        self.assertEqual(probe_fps(self.session, self.url), [])

    def test_mouse_changes_pixels_in_both_modes(self):
        self.assertEqual(probe_mouse(self.session, self.url), [])

    def test_context_restore_rebuilds_program(self):
        self.assertEqual(probe_restore(self.session, self.url), [])

    def test_dispose_releases_resources(self):
        self.assertEqual(probe_dispose(self.session, self.url), [])

    def test_prefers_reduced_motion(self):
        self.assertEqual(probe_reduced_motion(self.session, self.url), [])

    def test_no_webgl_is_reported_truthfully(self):
        self.assertEqual(probe_no_webgl(self.session, self.url), [])

    def test_broken_glsl_is_reported_truthfully(self):
        self.assertEqual(probe_shader_error(self.session, self.variant([GLSL_BREAK])), [])

    def test_resize_updates_canvas(self):
        page, logs = self.session.open(self.url, width=320, height=180, wait_ms=500)
        try:
            page.set_viewport_size({"width": 400, "height": 260})
            page.wait_for_timeout(400)
            dims = page.evaluate("() => { const c = document.getElementById('gl-canvas'); return [c.width, c.height]; }")
            self.assertEqual(dims, [400, 260])
            self.assertEqual(page.inner_text("#res-display").strip(), "400x260")
            self.assertEqual(logs, [])
        finally:
            page.context.close()

    def test_mode_buttons_switch_output(self):
        page, _ = self.session.open(self.url, wait_ms=500)
        try:
            page.evaluate(f"() => window['{API}'].freezeTime(5.0)")
            page.mouse.move(160, 90)
            e2e.wait_mouse_converged(page, API)
            metal = e2e.sample(page, API)
            page.click("#mode-fluid")
            page.mouse.move(160, 90)
            e2e.wait_mouse_converged(page, API)
            fluid = e2e.sample(page, API)
            self.assertGreater(e2e.changed_fraction(metal, fluid), 0.2)
            self.assertEqual(page.get_attribute("#mode-fluid", "aria-pressed"), "true")
            self.assertEqual(page.get_attribute("#mode-metal", "aria-pressed"), "false")
            page.click("#btn-switch-mode")
            self.assertEqual(page.get_attribute("#mode-metal", "aria-pressed"), "true")
        finally:
            page.context.close()

    def test_mutants_are_detected(self):
        """把實作改壞，對應 probe 必須報錯；存活的突變代表測試抓不到那種壞法。"""
        survivors = []
        for name, edits, probe_name in MUTANTS:
            problems = PROBES[probe_name](self.session, self.variant(edits))
            if not problems:
                survivors.append(f"{name}（probe={probe_name}）")
        self.assertEqual(survivors, [], f"以下突變沒有被測試抓到：{survivors}")


if __name__ == "__main__":
    unittest.main()
