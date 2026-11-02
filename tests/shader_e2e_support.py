#!/usr/bin/env python3
"""
tests/shader_e2e_support.py
shader hero 端到端測試（Playwright + 真實瀏覽器）的共用輔助。

本模組只在測試內使用，不是 CI 必備相依：
- 沒有安裝 playwright 套件、或找不到能建立 WebGL 的瀏覽器時，一律 raise unittest.SkipTest
  並寫明原因（測試輸出會顯示 skipped，不是靜默通過，也不會讓整套變紅）。
- 瀏覽器預設依序嘗試 Edge、Chrome、Playwright 內建 Chromium；可用環境變數
  SHADER_E2E_CHANNEL 指定單一 channel（例如 msedge、chrome、chromium）。
- 無頭模式使用 SwiftShader 軟體渲染，所以不需要實體 GPU。
"""

from __future__ import annotations

import atexit
import os
import statistics
import unittest
from typing import Any, Dict, List, Optional

LAUNCH_ARGS = [
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
]

# 掛在 getContext 上的間諜：統計 drawArrays／linkProgram／delete* 的呼叫次數。
SPY_SCRIPT = """
(() => {
  const orig = HTMLCanvasElement.prototype.getContext;
  window.__spy = { draws: 0, createProgram: 0, linkProgram: 0, deleteProgram: 0, deleteShader: 0, deleteBuffer: 0 };
  const table = [['drawArrays', 'draws'], ['createProgram', 'createProgram'], ['linkProgram', 'linkProgram'],
                 ['deleteProgram', 'deleteProgram'], ['deleteShader', 'deleteShader'], ['deleteBuffer', 'deleteBuffer']];
  HTMLCanvasElement.prototype.getContext = function (type, ...rest) {
    const ctx = orig.call(this, type, ...rest);
    if (ctx && /webgl/.test(String(type)) && !ctx.__spied) {
      ctx.__spied = true;
      for (const [fn, key] of table) {
        const original = ctx[fn].bind(ctx);
        ctx[fn] = function (...args) { window.__spy[key]++; return original(...args); };
      }
    }
    return ctx;
  };
})();
"""

NO_WEBGL_SCRIPT = "HTMLCanvasElement.prototype.getContext = function () { return null; };"

SAMPLE_JS = """
([api, step]) => {
  const d = window[api];
  const gl = d.getGL();
  if (!gl || !d.drawFrame()) return null;
  const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
  const buf = new Uint8Array(W * H * 4);
  gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, buf);
  const px = [];
  for (let i = 0; i < buf.length; i += 4 * step) { px.push(buf[i], buf[i + 1], buf[i + 2]); }
  return { W, H, glError: gl.getError(), px };
}
"""


def load_playwright():
    """回傳 sync_playwright；套件缺少時明確 skip。"""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # ImportError 或環境壞掉
        raise unittest.SkipTest(f"未安裝 playwright（{type(exc).__name__}），略過瀏覽器端到端測試")
    return sync_playwright


class BrowserSession:
    """啟動一個能建立 WebGL 的瀏覽器；做不到就 SkipTest。"""

    def __init__(self) -> None:
        self._pw_cm = None
        self.pw = None
        self.browser = None
        self.channel: Optional[str] = None

    def __enter__(self) -> "BrowserSession":
        sync_playwright = load_playwright()
        self._pw_cm = sync_playwright()
        self.pw = self._pw_cm.start()
        forced = os.environ.get("SHADER_E2E_CHANNEL")
        channels = [forced] if forced else ["msedge", "chrome", "chromium"]
        errors: List[str] = []
        for ch in channels:
            try:
                kwargs: Dict[str, Any] = {"headless": True, "args": LAUNCH_ARGS}
                if ch != "chromium":
                    kwargs["channel"] = ch
                self.browser = self.pw.chromium.launch(**kwargs)
                self.channel = ch
                break
            except Exception as exc:
                errors.append(f"{ch}: {str(exc).splitlines()[0][:80]}")
        if self.browser is None:
            self.close()
            raise unittest.SkipTest("找不到可啟動的瀏覽器，略過瀏覽器端到端測試：" + "; ".join(errors))
        # 確認這個瀏覽器真的能建立 WebGL，否則後面的失敗不是程式的錯
        page = self.browser.new_page()
        try:
            ok = page.evaluate("() => !!document.createElement('canvas').getContext('webgl')")
        finally:
            page.close()
        if not ok:
            self.close()
            raise unittest.SkipTest(f"瀏覽器 {self.channel} 無法建立 WebGL context，略過瀏覽器端到端測試")
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        if self.browser is not None:
            try:
                self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self._pw_cm is not None:
            try:
                self._pw_cm.stop()
            except Exception:
                pass
            self._pw_cm = None

    def open(self, url: str, *, width: int = 320, height: int = 180, reduced_motion: bool = False,
             spy: bool = True, no_webgl: bool = False, wait_ms: int = 600):
        """開頁並回傳 (page, logs)；logs 收集 console error 與 pageerror。"""
        ctx = self.browser.new_context(
            viewport={"width": width, "height": height},
            reduced_motion="reduce" if reduced_motion else "no-preference",
        )
        page = ctx.new_page()
        logs: List[str] = []
        page.on("console", lambda m: logs.append(f"console.{m.type}: {m.text}")
                if m.type in ("error", "warning") and "GL Driver Message" not in m.text else None)
        page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
        if spy:
            page.add_init_script(SPY_SCRIPT)
        if no_webgl:
            page.add_init_script(NO_WEBGL_SCRIPT)
        page.goto(url, wait_until="load")
        if wait_ms:
            page.wait_for_timeout(wait_ms)
        return page, logs


_SESSION: Optional["BrowserSession"] = None
_SESSION_ERROR: Optional[str] = None


def shared_session() -> "BrowserSession":
    """整個測試行程共用一個瀏覽器：Playwright sync API 在同一行程內 stop 後無法再 start，
    所以多個測試類別必須共用。啟動失敗會把原因快取，之後每個類別都以相同原因 skip。"""
    global _SESSION, _SESSION_ERROR
    if _SESSION_ERROR is not None:
        raise unittest.SkipTest(_SESSION_ERROR)
    if _SESSION is None:
        try:
            session = BrowserSession().__enter__()
        except unittest.SkipTest as exc:
            _SESSION_ERROR = str(exc)
            raise
        _SESSION = session
        atexit.register(session.close)
    return _SESSION


# ---- 像素統計 ----------------------------------------------------------------

def sample(page, api: str, step: int = 7) -> Optional[Dict[str, Any]]:
    """用頁面自己的 drawFrame() 畫一幀並立刻 readPixels（同一個 task，避免 drawing buffer 被清掉）。"""
    return page.evaluate(SAMPLE_JS, [api, step])


def luminance_stats(frame: Dict[str, Any]) -> Dict[str, float]:
    px = frame["px"]
    lum = [0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2] for i in range(0, len(px), 3)]
    return {
        "mean": statistics.fmean(lum),
        "stdev": statistics.pstdev(lum),
        "max": max(lum),
        "n": len(lum),
    }


def changed_fraction(a: Dict[str, Any], b: Dict[str, Any], threshold: int = 4) -> float:
    """兩幀之間任一色頻道差異超過 threshold 的取樣點比例。"""
    pa, pb = a["px"], b["px"]
    if len(pa) != len(pb):
        raise AssertionError("兩幀取樣大小不同，無法比較")
    n = len(pa) // 3
    changed = 0
    for i in range(0, len(pa), 3):
        if max(abs(pa[i] - pb[i]), abs(pa[i + 1] - pb[i + 1]), abs(pa[i + 2] - pb[i + 2])) > threshold:
            changed += 1
    return changed / n


def wait_mouse_converged(page, api: str, tol: float = 1.5, timeout_ms: int = 15000) -> bool:
    """等游標平滑值追上目標（頁面渲染迴圈在跑時才會收斂）。"""
    waited = 0
    while waited <= timeout_ms:
        st = page.evaluate(f"() => window['{api}'].getState()")
        if abs(st["mouse"][0] - st["target"][0]) <= tol and abs(st["mouse"][1] - st["target"][1]) <= tol:
            return True
        page.wait_for_timeout(100)
        waited += 100
    return False


def spy_counts(page) -> Dict[str, int]:
    return page.evaluate("() => Object.assign({}, window.__spy)")
