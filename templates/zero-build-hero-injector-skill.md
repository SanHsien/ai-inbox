---
name: zero-build-hero-injector
description: 把一段自包含的 WebGL 全螢幕片段著色器 Hero 背景注入既有網頁：4 個自寫模板（液態金屬、流體、點狀粒子場、字元密度風）、含 context 恢復與 dispose 的注入腳本、可獨立執行的瀏覽器驗證腳本。不含 3D Raymarching 與圖片／捲動型模板。
triggers:
  - "zero-build shader"
  - "hero section shader"
  - "注入液態金屬"
  - "WebGL hero"
  - "流體背景"
  - "反 AI 罐頭視覺"
  - "generative ui hero"
---

# Zero-Build Hero Section 快速注入技能 (Skill 範本)

> 對照規範：ai-inbox 的 `docs/zero-build-shader-hero-sections-spec.md`。本範本可獨立複製到別的專案使用；唯一要另外安裝的是第 2 節步驟 4 的 Playwright（只有驗證要用，網頁本身不需要）。

---

## 0. 先讀：這份範本是什麼、不是什麼

| 項目 | 內容 |
| :--- | :--- |
| 是什麼 | 4 個自行撰寫的全螢幕片段著色器（模板 A～D）＋ 1 段注入腳本 ＋ 1 支驗證腳本。注入後頁面只多一個 `<canvas>` 與一段內嵌 `<script>`，沒有 npm、沒有外部檔案。 |
| 不是什麼 | 不是 Hacktemplates（dvklab）的程式碼或素材，沒有複製其任何檔案。 |
| 沒有提供 | 3D Raymarching 模板、需要圖檔／深度圖的模板、GSAP＋Lenis 捲動體驗、真正的 `GL_POINTS` 粒子系統、字型圖集式 ASCII。想要這些請見下一列。 |
| 想用原作 | 到 [diiviikk5/Hacktemplates](https://github.com/diiviikk5/Hacktemplates)，本範本對照的是 commit `7b019b5debdf0b2b0e92eb475c8d76793162103f`。其程式碼是 MIT（`Copyright (c) 2026 diiviikk5`），複製時要保留授權聲明；它的圖片模板所用的參考圖不在 MIT 範圍內，商用前要換成你有權利的圖。圖片模板要用 `http://` 開啟：實測 `abyss` 以 `file://` 開啟時貼圖被 CORS 擋掉、以 `http://` 則正常（Edge 無頭模式，2026-11-02）；其餘圖片模板未逐一實測。 |

模板 C 與 D 的名稱要照字面理解：C 是「用片段著色器模擬的點狀粒子場」（每格一顆點，游標附近的點被推開並變亮），D 是「字元密度風格的程式生成點陣」（6 級亮度對應 `空白 . : + # @` 六種手繪形狀）。它們不是粒子系統，也不是字型文字。

---

## 1. 技能背景與執行定位

要在單檔 HTML、Landing Page 或 Generative UI 預覽裡放一個會動的首屏背景，又不想為此引入打包器時，可以直接寫一段 WebGL 片段著色器。這份範本把容易漏掉的部分補齊：

- context 遺失後要**重建 Program**（只重啟動畫迴圈會一直報 `INVALID_OPERATION`）；
- 編譯與連結失敗要**回報並降級**，不是留一塊空白畫布；
- 提供 `dispose()` 釋放 GL 資源與監聽器；
- 尊重 `prefers-reduced-motion`；
- 附驗證腳本，用真實瀏覽器量像素，而不是只看程式碼有沒有那幾個字。

---

## 2. 端到端注入工作流程（5 步 SOP）

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ [ 步驟 1：調性識別與挑選模板 ] 依專案調性在模板 A～D 擇一                    │
│           │                                                                │
│           ▼                                                                │
│ [ 步驟 2：注入 HTML 結構 ]   canvas 底層 + 遮罩中層 + 內容頂層，填佔位欄位  │
│           │                                                                │
│           ▼                                                                │
│ [ 步驟 3：注入著色器腳本 ]   貼上腳本，把模板 GLSL 填進 __SELECTED_FS_CODE__ │
│           │                                                                │
│           ▼                                                                │
│ [ 步驟 4：執行驗證腳本 ]     verify_hero.py：像素、滑鼠、context、dispose    │
│           │                                                                │
│           ▼                                                                │
│ [ 步驟 5：人工驗收 ]         真實螢幕、縮放、對比、換色                      │
└────────────────────────────────────────────────────────────────────────────┘
```

### 步驟 1：調性識別與挑選模板

| 專案調性 | 建議模板 | 畫面特徵 |
| :--- | :--- | :--- |
| 金融科技、硬體、精品等偏冷硬質感 | 模板 A：液態金屬 | 冷灰高光，游標位置會改變高光 |
| 設計、音樂、品牌等偏柔和流動 | 模板 B：流體 | 深青色波浪，游標周圍產生漣漪 |
| 資料、雲端、AI 平台等偏點陣資訊感 | 模板 C：點狀粒子場 | 上飄的細點，游標附近的點被推開 |
| 開發者工具、CLI、開源專案 | 模板 D：字元密度風 | 手繪字元點陣，游標處變亮變密 |

上表是本範本作者的搭配建議，不是研究結論；專案已有品牌指引時以品牌指引為準。

### 步驟 2：注入 HTML 結構

把下面整段放在目標頁面 `<body>` 開頭，並替換 5 個佔位欄位：`__HERO_KICKER__`、`__HERO_TITLE__`、`__HERO_DESCRIPTION__`、`__PRIMARY_CTA_TEXT__`、`__PRIMARY_CTA_LINK__`（想要第二顆按鈕就複製 `<a>` 並自行命名）。**驗證腳本會拒絕任何殘留的 `__大寫佔位__`。**

<!-- block:skeleton -->
```html
<!-- [HERO-INJECT: BEGIN] Zero-Build Shader Hero Section -->
<header style="position:relative; width:100%; min-height:100vh; overflow:hidden; background:linear-gradient(160deg, #020617 0%, #0f172a 55%, #1e293b 100%);">
  <!-- 底層：WebGL 畫布。失敗時腳本會把它隱藏，露出上面這層 CSS 漸層 -->
  <canvas id="zero-hero-canvas" aria-hidden="true" style="position:absolute; inset:0; width:100%; height:100%; display:block;"></canvas>

  <!-- 中層：暗角與對比保護，不攔截滑鼠 -->
  <div aria-hidden="true" style="position:absolute; inset:0; pointer-events:none; background:radial-gradient(circle at 50% 50%, rgba(2,6,23,0.25) 0%, rgba(2,6,23,0.85) 100%);"></div>

  <!-- 頂層：內容。外層不攔截滑鼠，只有可互動元素恢復 pointer-events -->
  <div style="position:relative; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:2rem; text-align:center; pointer-events:none;">
    <div style="pointer-events:auto; max-width:800px;">
      <p style="margin:0; font-family:ui-monospace, Consolas, monospace; font-size:0.75rem; color:#94a3b8;">__HERO_KICKER__</p>
      <h1 style="margin:1rem 0; font-size:clamp(2.5rem, 6vw, 4.5rem); line-height:1.1; letter-spacing:-0.03em; color:#f8fafc;">__HERO_TITLE__</h1>
      <p style="margin:0 auto 2rem; max-width:600px; font-size:1.125rem; line-height:1.6; color:#94a3b8;">__HERO_DESCRIPTION__</p>
      <a href="__PRIMARY_CTA_LINK__" style="display:inline-block; padding:0.75rem 1.75rem; border-radius:6px; background:#f8fafc; color:#020617; font-weight:600; text-decoration:none;">__PRIMARY_CTA_TEXT__</a>
    </div>
  </div>
</header>
<!-- [HERO-INJECT: END] -->
```

### 步驟 3：注入著色器腳本

放在頁面 `</body>` 之前。把第 3 節選好的模板整段 GLSL（不含 `glsl` 程式碼圍欄）貼進 `__SELECTED_FS_CODE__`。GLSL 內不可出現反引號或 `${`，因為它被包在 JavaScript 樣板字串裡。

<!-- block:injector -->
```html
<script>
(function () {
  'use strict';

  // ---- 設定（可改）------------------------------------------------------------
  var CANVAS_ID = 'zero-hero-canvas';
  var STILL_TIME = 6.0;       // prefers-reduced-motion 時使用的固定時間點（秒）
  var MOUSE_TAU = 0.12;       // 游標平滑時間常數（秒）
  var MAX_DPR = 2.0;          // DPR 上限（本範本的取捨，不是外部標準）

  var VS_SRC = [
    'attribute vec2 a_pos;',
    'void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }'
  ].join('\n');

  // 由第 3 節挑選的模板 A～D 其中之一貼在這裡（整段 GLSL，不含 ```glsl 圍欄）
  var FS_SRC = `__SELECTED_FS_CODE__`;

  // ---- 狀態 -----------------------------------------------------------------
  var canvas = document.getElementById(CANVAS_ID);
  if (!canvas) { console.error('[zero-hero] 找不到 #' + CANVAS_ID); return; }

  var gl = null, program = null, vs = null, fs = null, buffer = null;
  var uRes = null, uTime = null, uMouse = null;
  var rafId = null, lastT = null;
  var disposed = false, contextLost = false, errorMessage = null, noWebGL = false;
  var pageVisible = !document.hidden, intersecting = true, reduceMotion = false;
  var targetX = 0, targetY = 0, mouseX = 0, mouseY = 0, frozenTime = null;
  var state = 'init', observer = null, resizeObserver = null, motionQuery = null;
  var startT = performance.now();

  function setState(next, message) {
    if (state === next && !message) return;
    state = next;
    canvas.setAttribute('data-hero-state', next);
    canvas.dispatchEvent(new CustomEvent('zerohero:statechange', { detail: { state: next, message: message || '' } }));
  }

  // ---- WebGL 管線（context 恢復時整段重跑）------------------------------------
  function compile(type, src, label) {
    var s = gl.createShader(type);
    if (!s) throw new Error(label + ' 建立失敗（context 可能已遺失）');
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      var log = gl.getShaderInfoLog(s) || '(無 info log)';
      gl.deleteShader(s);
      throw new Error(label + ' 編譯失敗：' + log);
    }
    return s;
  }

  function release() {
    if (!gl) return;
    if (buffer) { gl.deleteBuffer(buffer); buffer = null; }
    if (vs) { gl.deleteShader(vs); vs = null; }
    if (fs) { gl.deleteShader(fs); fs = null; }
    if (program) { gl.deleteProgram(program); program = null; }
  }

  function build() {
    release();
    try {
      vs = compile(gl.VERTEX_SHADER, VS_SRC, '頂點著色器');
      fs = compile(gl.FRAGMENT_SHADER, FS_SRC, '片段著色器');
      program = gl.createProgram();
      gl.attachShader(program, vs);
      gl.attachShader(program, fs);
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        throw new Error('Program 連結失敗：' + (gl.getProgramInfoLog(program) || '(無 info log)'));
      }
    } catch (err) {
      release();
      throw err;
    }
    gl.useProgram(program);
    uRes = gl.getUniformLocation(program, 'u_resolution');
    uTime = gl.getUniformLocation(program, 'u_time');
    uMouse = gl.getUniformLocation(program, 'u_mouse');
    buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    var aPos = gl.getAttribLocation(program, 'a_pos');
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);
  }

  function showFallback() {
    canvas.style.display = 'none';   // 露出容器底色／CSS 漸層，不留一塊空白畫布
  }

  function fail(err) {
    errorMessage = String(err && err.message ? err.message : err);
    console.error('[zero-hero] ' + errorMessage);
    showFallback();
    sync();
  }

  // ---- 尺寸與繪製 -------------------------------------------------------------
  function resize() {
    if (!gl) return;
    var dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    var w = Math.max(1, Math.floor(canvas.clientWidth * dpr));
    var h = Math.max(1, Math.floor(canvas.clientHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    if (!gl.isContextLost()) gl.viewport(0, 0, canvas.width, canvas.height);
    if (!rafId) draw();   // 靜態畫面時縮放後補畫一幀
  }

  function draw(timeOverride) {
    if (!gl || !program || disposed || gl.isContextLost()) return false;
    var t = timeOverride !== undefined ? timeOverride
      : (frozenTime !== null ? frozenTime
        : (reduceMotion ? STILL_TIME : (performance.now() - startT) * 0.001));
    var r = canvas.getBoundingClientRect();
    var sx = canvas.width / Math.max(r.width, 1);
    var sy = canvas.height / Math.max(r.height, 1);
    gl.useProgram(program);
    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform1f(uTime, t);
    gl.uniform2f(uMouse, (mouseX - r.left) * sx, (r.bottom - mouseY) * sy);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    return true;
  }

  function loop(now) {
    rafId = null;
    if (!shouldRun()) return;
    var dt = lastT === null ? 0.016 : Math.min((now - lastT) / 1000, 0.25);
    lastT = now;
    var k = 1 - Math.exp(-dt / MOUSE_TAU);
    mouseX += (targetX - mouseX) * k;
    mouseY += (targetY - mouseY) * k;
    if (draw() && state !== 'running') setState('running');
    rafId = requestAnimationFrame(loop);
  }

  function shouldRun() {
    return !disposed && !contextLost && !errorMessage && !noWebGL && !!program &&
           !reduceMotion && pageVisible && intersecting;
  }

  // 依條件啟停渲染迴圈，並讓 data-hero-state 反映真實原因
  function sync() {
    if (disposed) setState('disposed');
    else if (noWebGL) setState('nowebgl', 'WebGL 不可用');
    else if (errorMessage) setState('error', errorMessage);
    else if (contextLost) setState('lost');
    else if (reduceMotion) setState('static');
    else if (!pageVisible || !intersecting) setState('paused');

    if (shouldRun()) {
      if (!rafId) { lastT = null; rafId = requestAnimationFrame(loop); }
    } else {
      if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
      if (reduceMotion && program && !contextLost && !disposed) draw();
    }
  }

  // ---- 事件 -----------------------------------------------------------------
  function onPointer(e) { targetX = e.clientX; targetY = e.clientY; }
  function onVisibility() { pageVisible = !document.hidden; sync(); }
  function onMotion(e) { reduceMotion = e.matches; sync(); }

  function onLost(e) {
    e.preventDefault();   // 不呼叫就不會收到 restored
    contextLost = true;
    program = vs = fs = buffer = null;   // 舊物件已失效：只丟參考，不要 delete*
    sync();
  }

  function onRestored() {
    contextLost = false;
    try { build(); resize(); } catch (err) { fail(err); return; }   // 必須重建 Program
    sync();
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    if (observer) { observer.disconnect(); observer = null; }
    if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null; }
    window.removeEventListener('resize', resize);
    window.removeEventListener('pointermove', onPointer);
    document.removeEventListener('visibilitychange', onVisibility);
    canvas.removeEventListener('webglcontextlost', onLost);
    canvas.removeEventListener('webglcontextrestored', onRestored);
    if (motionQuery) motionQuery.removeEventListener('change', onMotion);
    release();
    sync();
  }

  // ---- 啟動 -----------------------------------------------------------------
  motionQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  reduceMotion = !!(motionQuery && motionQuery.matches);
  var box = canvas.getBoundingClientRect();
  targetX = mouseX = box.left + box.width / 2;
  targetY = mouseY = box.top + box.height / 2;

  gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  if (!gl) {
    noWebGL = true;
    showFallback();
  } else {
    try { build(); resize(); } catch (err) { errorMessage = String(err.message || err); console.error('[zero-hero] ' + errorMessage); showFallback(); }
  }

  window.addEventListener('resize', resize);
  window.addEventListener('pointermove', onPointer, { passive: true });
  document.addEventListener('visibilitychange', onVisibility);
  canvas.addEventListener('webglcontextlost', onLost);
  canvas.addEventListener('webglcontextrestored', onRestored);
  if (motionQuery) motionQuery.addEventListener('change', onMotion);
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(function (entries) {
      intersecting = entries[entries.length - 1].isIntersecting;
      sync();
    }, { threshold: 0.05 });
    observer.observe(canvas);
  }
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(canvas);
  }
  sync();

  // 公開介面：dispose() 與 getState() 供正式使用；其餘是驗證腳本用的測試掛鉤，可刪除。
  window.ZeroHero = {
    dispose: dispose,
    getState: function () {
      return { status: state, error: errorMessage, contextLost: contextLost, reduceMotion: reduceMotion,
               running: rafId !== null, mouse: [mouseX, mouseY], target: [targetX, targetY] };
    },
    freezeTime: function (sec) { frozenTime = sec; },
    drawFrame: function () { return draw(); },
    getGL: function () { return gl; },
    getProgram: function () { return program; }
  };
})();
</script>
```

腳本的行為契約：

| 事件 | 行為 |
| :--- | :--- |
| 編譯／連結失敗 | `console.error('[zero-hero] …')`（含 GPU 的 info log）、隱藏 canvas 露出 CSS 漸層、狀態 `error` |
| 取不到 WebGL | 同上，狀態 `nowebgl` |
| `webglcontextlost` | `preventDefault()`、停止迴圈、丟掉舊物件參考（不對失效物件呼叫 `delete*`）、狀態 `lost` |
| `webglcontextrestored` | 重新編譯、連結、建緩衝區並取回 uniform 位置，再重啟迴圈 |
| `prefers-reduced-motion: reduce` | 只畫一幀固定時間點的靜態畫面，不跑迴圈、不隨游標重畫；執行中切換偏好也會跟著變 |
| 分頁在背景／畫布離開可視範圍 | 暫停迴圈，狀態 `paused` |
| `ZeroHero.dispose()` | 取消迴圈、斷開 observer、移除所有監聽器、`deleteBuffer/deleteShader/deleteProgram`，狀態 `disposed` |

狀態寫在 `<canvas data-hero-state="…">`，並在狀態改變時對 canvas 觸發 `zerohero:statechange`（`detail.state`、`detail.message`）。可以用它在畫面上顯示真實狀態，不要寫死「執行中」。`window.ZeroHero` 的 `dispose()` 與 `getState()` 是正式介面，其餘（`freezeTime`、`drawFrame`、`getGL`、`getProgram`）是驗證腳本使用的測試掛鉤，上線時可以刪掉，但刪掉後就不能再跑驗證腳本。

### 步驟 4：執行驗證腳本

驗證腳本要用真實瀏覽器，所以需要 Playwright（只有驗證要用）：

```bash
pip install playwright
python -m playwright install chromium     # 或直接使用本機的 Edge／Chrome：加 --channel msedge / chrome
python verify_hero.py path/to/index.html
```

把下面的程式存成 `verify_hero.py`。結束碼 `0` 全部通過、`1` 有檢查失敗、`2` 環境問題（沒有 Playwright／瀏覽器／WebGL，或機器太忙導致 Playwright 動作逾時；這不是通過，請稍後重跑）。它檢查：沒有殘留佔位字串與 console 錯誤；迴圈持續繪製；畫面不是單色或全黑；時間改變畫面跟著變；**真實滑鼠移動會改變像素**；context 遺失期間停止繪製、恢復後 Program 重新連結且畫面一致；`prefers-reduced-motion` 只畫靜態畫面；`dispose()` 真的釋放資源。門檻（單色標準差、像素差比例）是這支腳本自訂的取捨，不是外部標準；沒有提供放寬或略過檢查的旗標。

<!-- block:verify_hero.py -->
```python
#!/usr/bin/env python3
"""verify_hero.py：驗證已注入 Zero-Build Shader Hero 的 HTML 檔（可獨立複製到任何專案，只依賴 Playwright）。

用法：  python verify_hero.py path/to/index.html [--channel msedge|chrome|chromium] [--width 320 --height 180]
結束碼：0 全部通過；1 有檢查失敗（輸出每一項）；2 環境問題（沒有 Playwright／瀏覽器／WebGL，或 Playwright 動作逾時），不代表頁面有錯也不代表通過。

檢查項目（全部必過，沒有略過旗標）：
  1. 沒有殘留的 __PLACEHOLDER__ 字串；頁面載入沒有 console error / pageerror / WebGL 警告
  2. 渲染迴圈持續繪製；畫面不是單色或全黑；u_time 改變畫面跟著變
  3. 真實滑鼠移動會改變像素（時間凍結後比對）
  4. 模擬 WEBGL_lose_context：遺失期間停止繪製，恢復後 Program 重新連結、畫面與遺失前一致
  5. prefers-reduced-motion: reduce 時只畫靜態畫面、不跑迴圈
  6. dispose() 後 deleteProgram/deleteShader/deleteBuffer 被呼叫、迴圈停止、滑鼠監聽移除
門檻（單色標準差、像素差比例）是本腳本自訂的取捨，不是外部標準。
"""
import argparse
import re
import statistics
import sys
from pathlib import Path

API = "ZeroHero"
MIN_STDEV, MIN_MAX_LUMA = 3.0, 20.0
MIN_CHANGE = 0.02      # 游標／時間改變後至少 2% 取樣點變色
MAX_NOISE = 0.01       # 同狀態重畫的雜訊上限

SPY = """
(() => {
  const orig = HTMLCanvasElement.prototype.getContext;
  window.__spy = {draws:0, linkProgram:0, deleteProgram:0, deleteShader:0, deleteBuffer:0};
  const table = [['drawArrays','draws'],['linkProgram','linkProgram'],['deleteProgram','deleteProgram'],
                 ['deleteShader','deleteShader'],['deleteBuffer','deleteBuffer']];
  HTMLCanvasElement.prototype.getContext = function (type, ...rest) {
    const ctx = orig.call(this, type, ...rest);
    if (ctx && /webgl/.test(String(type)) && !ctx.__spied) {
      ctx.__spied = true;
      for (const [fn, key] of table) { const o = ctx[fn].bind(ctx); ctx[fn] = (...a) => { window.__spy[key]++; return o(...a); }; }
    }
    return ctx;
  };
})();
"""

SAMPLE = """
() => {
  const d = window.ZeroHero; const gl = d.getGL();
  if (!gl || !d.drawFrame()) return null;
  const W = gl.drawingBufferWidth, H = gl.drawingBufferHeight;
  const buf = new Uint8Array(W * H * 4);
  gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, buf);
  const px = [];
  for (let i = 0; i < buf.length; i += 28) px.push(buf[i], buf[i + 1], buf[i + 2]);
  return { err: gl.getError(), px };
}
"""


def luma(frame):
    p = frame["px"]
    v = [0.299 * p[i] + 0.587 * p[i + 1] + 0.114 * p[i + 2] for i in range(0, len(p), 3)]
    return statistics.pstdev(v), max(v)


def changed(a, b, thr=4):
    pa, pb = a["px"], b["px"]
    n = len(pa) // 3
    return sum(1 for i in range(0, len(pa), 3) if max(abs(pa[i] - pb[i]), abs(pa[i + 1] - pb[i + 1]), abs(pa[i + 2] - pb[i + 2])) > thr) / n


def state(page):
    return page.evaluate(f"() => window.{API}.getState()")


def spy(page):
    return page.evaluate("() => Object.assign({}, window.__spy)")


def converge(page, tol=0.02, timeout=15000):
    waited = 0
    while waited <= timeout:
        s = state(page)
        if abs(s["mouse"][0] - s["target"][0]) <= tol and abs(s["mouse"][1] - s["target"][1]) <= tol:
            return True
        page.wait_for_timeout(100)
        waited += 100
    return False


def run(url, text, channel, width, height):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ENV] 需要 Playwright：pip install playwright && python -m playwright install chromium", file=sys.stderr)
        return 2
    problems = []
    args = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
    with sync_playwright() as pw:
        browser, errors = None, []
        for ch in ([channel] if channel else ["msedge", "chrome", "chromium"]):
            try:
                kw = {"headless": True, "args": args}
                if ch != "chromium":
                    kw["channel"] = ch
                browser = pw.chromium.launch(**kw)
                break
            except Exception as exc:
                errors.append(f"{ch}: {str(exc).splitlines()[0][:80]}")
        if browser is None:
            print("[ENV] 找不到可啟動的瀏覽器：" + "; ".join(errors), file=sys.stderr)
            return 2

        def open_page(reduced=False):
            ctx = browser.new_context(viewport={"width": width, "height": height},
                                      reduced_motion="reduce" if reduced else "no-preference")
            page = ctx.new_page()
            logs = []
            page.on("console", lambda m: logs.append(f"console.{m.type}: {m.text}")
                    if m.type in ("error", "warning") and "GL Driver Message" not in m.text else None)
            page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
            page.add_init_script(SPY)
            page.goto(url, wait_until="load")
            page.wait_for_timeout(1000)
            return ctx, page, logs

        try:
            probe = browser.new_page()
            if not probe.evaluate("() => !!document.createElement('canvas').getContext('webgl')"):
                print("[ENV] 這個瀏覽器無法建立 WebGL", file=sys.stderr)
                return 2
            probe.close()

            # 1. 載入、狀態、錯誤
            left = sorted(set(re.findall(r"__[A-Z][A-Z0-9_]+__", text)))
            if left:
                problems.append(f"殘留未填的佔位字串：{left}")
            ctx, page, logs = open_page()
            if page.evaluate(f"() => typeof window.{API}") != "object":
                print("[FAIL] 頁面沒有 window.ZeroHero，注入腳本沒有執行", file=sys.stderr)
                return 1
            st = state(page)
            if st["status"] != "running":
                problems.append(f"狀態不是 running：{st['status']}（{st['error']}）")
            if logs:
                problems.append(f"console 有錯誤或警告：{logs[:2]}")

            # 2. 持續繪製與畫面內容
            d1 = spy(page)["draws"]
            page.wait_for_timeout(600)
            if spy(page)["draws"] - d1 < 3:
                problems.append("渲染迴圈沒有持續繪製")
            page.evaluate(f"() => window.{API}.freezeTime(5.0)")
            f = page.evaluate(SAMPLE)
            if f is None:
                problems.append("無法繪製或讀取畫面")
                return report(problems)
            sd, mx = luma(f)
            if sd < MIN_STDEV:
                problems.append(f"畫面接近單色（亮度標準差 {sd:.2f}）")
            if mx < MIN_MAX_LUMA:
                problems.append(f"畫面幾乎全黑（最亮 {mx:.1f}）")
            if f["err"] != 0:
                problems.append(f"gl.getError() = {f['err']}")
            page.evaluate(f"() => window.{API}.freezeTime(1.0)")
            t1 = page.evaluate(SAMPLE)
            page.evaluate(f"() => window.{API}.freezeTime(7.0)")
            t2 = page.evaluate(SAMPLE)
            if changed(t1, t2) < MIN_CHANGE:
                problems.append("u_time 改變後畫面沒有變化")

            # 3. 滑鼠
            page.evaluate(f"() => window.{API}.freezeTime(5.0)")
            page.mouse.move(width * 0.2, height * 0.25)
            ok1 = converge(page)
            a = page.evaluate(SAMPLE)
            page.mouse.move(width * 0.8, height * 0.75)
            ok2 = converge(page)
            b = page.evaluate(SAMPLE)
            b2 = page.evaluate(SAMPLE)
            if not (ok1 and ok2):
                problems.append("游標平滑值沒有追上滑鼠位置（pointermove 沒被處理）")
            elif changed(b, b2) > MAX_NOISE:
                problems.append("同狀態重畫雜訊過高，量測不可靠")
            elif changed(a, b) < MIN_CHANGE:
                problems.append(f"滑鼠移動只改變 {changed(a, b):.4f} 的像素：著色器沒有使用 u_mouse，或 u_mouse 沒送進去")

            # 4. context 遺失與恢復
            page.mouse.move(width * 0.5, height * 0.5)
            converge(page)
            before = page.evaluate(SAMPLE)
            links = spy(page)["linkProgram"]
            page.evaluate(f"() => {{ const e = window.{API}.getGL().getExtension('WEBGL_lose_context'); e.loseContext(); setTimeout(() => e.restoreContext(), 600); }}")
            lost = False
            for _ in range(30):
                page.wait_for_timeout(100)
                if state(page)["contextLost"]:
                    lost = True
                    break
            if not lost:
                problems.append("context 遺失事件沒有被處理（webglcontextlost 監聽缺少或沒有 preventDefault）")
            else:
                d1 = spy(page)["draws"]
                page.wait_for_timeout(250)
                if spy(page)["draws"] != d1:
                    problems.append("context 遺失期間仍在繪製")
                restored = False
                for _ in range(60):
                    page.wait_for_timeout(100)
                    s = state(page)
                    if not s["contextLost"] and s["status"] == "running":
                        restored = True
                        break
                if not restored:
                    problems.append(f"context 沒有恢復到 running：{state(page)['status']}")
                else:
                    if spy(page)["linkProgram"] != links + 1:
                        problems.append("恢復後沒有重新連結 Program")
                    valid = page.evaluate(f"() => {{ const d = window.{API}; const gl = d.getGL(); const p = d.getProgram(); return !!p && gl.isProgram(p) && gl.getProgramParameter(p, gl.LINK_STATUS); }}")
                    if not valid:
                        problems.append("恢復後仍使用失效的舊 Program")
                    page.evaluate(f"() => window.{API}.freezeTime(5.0)")
                    after = page.evaluate(SAMPLE)
                    if after is None or after["err"] != 0:
                        problems.append("恢復後無法正常繪製")
                    elif changed(before, after) > MIN_CHANGE / 2:
                        problems.append("恢復後畫面與遺失前不一致")
                    if logs:
                        problems.append(f"遺失／恢復流程產生 console 警告：{logs[:2]}")
            ctx.close()

            # 5. reduced motion
            ctx, page, logs = open_page(reduced=True)
            st = state(page)
            d1 = spy(page)["draws"]
            page.mouse.move(10, 10)
            page.mouse.move(width - 10, height - 10)
            page.wait_for_timeout(500)
            if st["status"] != "static" or st["running"]:
                problems.append(f"prefers-reduced-motion 時應為 static 且不跑迴圈：{st['status']} running={st['running']}")
            if d1 < 1:
                problems.append("prefers-reduced-motion 時沒有畫出靜態畫面")
            if spy(page)["draws"] != d1:
                problems.append("prefers-reduced-motion 時仍在連續繪製")
            ctx.close()

            # 6. dispose
            ctx, page, logs = open_page()
            before = spy(page)
            page.evaluate(f"() => {{ window.{API}.dispose(); window.{API}.dispose(); }}")
            page.wait_for_timeout(100)
            after = spy(page)
            if after["deleteProgram"] - before["deleteProgram"] < 1:
                problems.append("dispose() 沒有 deleteProgram")
            if after["deleteShader"] - before["deleteShader"] < 2:
                problems.append("dispose() deleteShader 少於 2 次")
            if after["deleteBuffer"] - before["deleteBuffer"] < 1:
                problems.append("dispose() 沒有 deleteBuffer")
            tgt = state(page)["target"]
            d1 = spy(page)["draws"]
            page.mouse.move(5, 5)
            page.mouse.move(width - 5, height - 5)
            page.wait_for_timeout(300)
            if spy(page)["draws"] != d1:
                problems.append("dispose() 後仍在繪製")
            if state(page)["target"] != tgt:
                problems.append("dispose() 後 pointermove 監聽仍在運作")
            ctx.close()
        except Exception as exc:
            if type(exc).__name__ == "TimeoutError":   # Playwright 動作逾時：機器忙，不是頁面的錯，也不算通過
                print(f"[ENV] Playwright 動作逾時（機器忙？請稍後重跑）：{str(exc).splitlines()[0][:100]}", file=sys.stderr)
                return 2
            raise
        finally:
            browser.close()
    return report(problems)


def report(problems):
    if problems:
        for p in problems:
            print(f"[FAIL] {p}")
        print(f"驗證失敗：{len(problems)} 項")
        return 1
    print("[PASS] 全部檢查通過")
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="驗證 Zero-Build Shader Hero 注入結果")
    ap.add_argument("html", help="要驗證的 HTML 檔")
    ap.add_argument("--channel", help="msedge / chrome / chromium（預設依序嘗試）")
    ap.add_argument("--width", type=int, default=320)
    ap.add_argument("--height", type=int, default=180)
    args = ap.parse_args()
    path = Path(args.html)
    if not path.is_file():
        print(f"[ENV] 找不到檔案：{path}", file=sys.stderr)
        return 2
    return run(path.resolve().as_uri(), path.read_text(encoding="utf-8"), args.channel, args.width, args.height)


if __name__ == "__main__":
    sys.exit(main())
```

另外，在 ai-inbox 倉庫內還可以跑 `python tools/verify_no_slop.py <檔案>` 掃描陰影、漸層、Emoji 等靜態樣式特徵；這支工具只存在於 ai-inbox，複製範本到別的專案時沒有它，不影響上面的驗證。

### 步驟 5：人工驗收

腳本用 320x180 的軟體渲染畫面量測，不能取代人眼：

- 用真實螢幕開啟，確認文字與背景對比足夠（遮罩層的暗角可以調 `rgba` 的不透明度）。
- 縮放視窗與在手機尺寸確認沒有橫向捲軸、畫面沒有被拉伸。
- 開作業系統的「減少動態效果」設定，確認畫面靜止。
- 換色：模板裡有 `// 換色` 註解的 `vec3` 常數就是調色盤。品牌色從專案 CSS 取（例如搜尋 `--primary`、`--accent`、`brand`），把 `#rrggbb` 的每個 16 進位分量除以 255 得到 `vec3`。範例：`#38bdf8` → `vec3(0.220, 0.741, 0.973)`。

---

## 3. 著色器模板庫（GLSL 片段）

四個模板都只使用 `u_resolution`（畫布像素）、`u_time`（秒）、`u_mouse`（畫布像素座標，原點在左下）三個 uniform，所以可以互換貼進 `__SELECTED_FS_CODE__`。以下每一個都用 `verify_hero.py` 在 Edge 無頭模式（SwiftShader 軟體渲染）實際跑過並通過。

### 模板 A：液態金屬（Liquid Metal）

高度場 = 域扭曲 fBM ＋ 游標漣漪，法線由這個高度場差分而來，所以游標會真的改變高光（上一版把漣漪算出來卻沒用到法線，游標沒有任何效果）。

<!-- block:glsl-A -->
```glsl
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
float noise(vec2 p) {
  vec2 i = floor(p); vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p) {
  float v = 0.0; float a = 0.5;
  mat2 rot = mat2(0.877, 0.479, -0.479, 0.877);
  for (int i = 0; i < 4; i++) {
    v += a * noise(p);
    p = rot * p * 2.0 + vec2(0.1, 0.2);
    a *= 0.5;
  }
  return v;
}

// 滑鼠漣漪：以游標為圓心向外擴散並衰減的高度偏移
float ripple(vec2 st, vec2 m) {
  float d = length(st - m);
  return sin(d * 14.0 - u_time * 4.5) * exp(-d * 2.5) * 0.30;
}
// 高度場 = 域扭曲 fBM + 滑鼠漣漪；法線由這個高度場差分而來，所以游標會改變高光
float heightAt(vec2 st, vec2 r, vec2 m) { return fbm(st * 1.6 + 3.0 * r) + ripple(st, m); }

void main() {
  float s = min(u_resolution.x, u_resolution.y);
  vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / s;
  vec2 m = (u_mouse * 2.0 - u_resolution) / s;

  vec2 q = vec2(fbm(st * 1.4 + vec2(0.0, u_time * 0.12)),
                fbm(st * 1.4 + vec2(5.2, 1.3 - u_time * 0.10)));
  vec2 r = vec2(fbm(st * 1.8 + 4.0 * q + vec2(1.7, 9.2) + u_time * 0.08),
                fbm(st * 1.8 + 4.0 * q + vec2(8.3, 2.8) - u_time * 0.06));

  vec2 e = vec2(0.006, 0.0);
  float hx = (heightAt(st + e.xy, r, m) - heightAt(st - e.xy, r, m)) * 7.0;
  float hy = (heightAt(st + e.yx, r, m) - heightAt(st - e.yx, r, m)) * 7.0;
  vec3 N = normalize(vec3(-hx, -hy, 1.0));

  vec3 L = normalize(vec3(0.5, 0.7, 1.0));
  vec3 V = vec3(0.0, 0.0, 1.0);
  vec3 H = normalize(L + V);
  float diff = max(dot(N, L), 0.0);
  float spec = pow(max(dot(N, H), 0.0), 28.0);
  float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);

  // 換色：改這三個 vec3（品牌色的 RGB 各除以 255）
  vec3 baseCol = vec3(0.03, 0.05, 0.08);
  vec3 midCol = vec3(0.16, 0.20, 0.26);
  vec3 highCol = vec3(0.85, 0.90, 0.95);

  vec3 col = mix(baseCol, midCol, diff) + highCol * (spec * 0.75 + fresnel * 0.35);
  gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
```

### 模板 B：流體（Fluid Waves）

<!-- block:glsl-B -->
```glsl
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
float noise(vec2 p) {
  vec2 i = floor(p); vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p) {
  float v = 0.0; float a = 0.5;
  mat2 rot = mat2(0.877, 0.479, -0.479, 0.877);
  for (int i = 0; i < 4; i++) {
    v += a * noise(p);
    p = rot * p * 2.0 + vec2(0.1, 0.2);
    a *= 0.5;
  }
  return v;
}

float ripple(vec2 st, vec2 m) {
  float d = length(st - m);
  return sin(d * 14.0 - u_time * 4.5) * exp(-d * 2.5) * 0.30;
}

void main() {
  float s = min(u_resolution.x, u_resolution.y);
  vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / s;
  vec2 m = (u_mouse * 2.0 - u_resolution) / s;

  float t = u_time * 0.25;
  vec2 p = st * 1.8;
  float w1 = sin(p.x * 2.2 + t) * cos(p.y * 1.8 - t * 0.9);
  float w2 = sin(p.x * 1.5 - t * 1.1) * cos(p.y * 2.2 + t);
  float w3 = fbm(p + vec2(t * 0.15, -t * 0.12)) * 1.2;
  float wave = (w1 + w2 + w3) * 0.35 + ripple(st, m) * 0.7;

  // 換色：改這三個 vec3
  vec3 deepWater = vec3(0.02, 0.05, 0.08);
  vec3 oceanTeal = vec3(0.06, 0.22, 0.28);
  vec3 waveFoam = vec3(0.35, 0.75, 0.85);

  float foam = smoothstep(0.15, 0.55, wave);
  vec3 col = mix(deepWater, oceanTeal, wave + 0.3);
  col = mix(col, waveFoam, foam * 0.45);
  col *= 1.0 - smoothstep(0.8, 1.8, length(st));
  gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
```

### 模板 C：點狀粒子場（片段著色器模擬）

<!-- block:glsl-C -->
```glsl
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

// 注意：這是「用片段著色器模擬的點狀粒子場」，不是 GL_POINTS 粒子系統。
// 每個格點最多一顆點，游標附近的點被推離中心並變亮；點的位移被限制在自己的格子內。
float hash21(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }

void main() {
  float s = min(u_resolution.x, u_resolution.y);
  vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / s;
  vec2 m = (u_mouse * 2.0 - u_resolution) / s;

  vec3 bg = vec3(0.012, 0.022, 0.04);
  vec3 dotCol = vec3(0.62, 0.82, 0.95);   // 換色：粒子顏色
  vec3 col = bg;

  for (int layer = 0; layer < 3; layer++) {
    float fl = float(layer);
    float scale = 6.0 + fl * 5.0;                     // 越遠的層點越小越密
    float drift = u_time * (0.10 + 0.05 * fl);
    vec2 p = st * scale + vec2(0.0, drift * scale);   // 整層往上漂
    vec2 id = floor(p);
    vec2 f = fract(p) - 0.5;

    float h = hash21(id + fl * 17.0);
    vec2 off = (vec2(hash21(id + 1.7), hash21(id + 9.2)) - 0.5) * 0.5;
    off += 0.10 * vec2(sin(u_time * 0.6 + h * 6.2831), cos(u_time * 0.5 + h * 6.2831));

    vec2 cellSt = (id + 0.5 - vec2(0.0, drift * scale)) / scale;   // 這顆點所在格子中心（st 座標）
    vec2 away = cellSt - m;
    float dm = length(away);
    float push = exp(-dm * 2.2);
    off += normalize(away + vec2(1e-4)) * push * 0.55;
    off = clamp(off, vec2(-0.42), vec2(0.42));

    float radius = 0.10 + 0.08 * h;
    float a = 1.0 - smoothstep(radius * 0.6, radius, length(f - off));
    float twinkle = 0.55 + 0.45 * sin(u_time * (0.8 + h * 1.5) + h * 40.0);
    float glow = 0.35 + 0.65 * push;
    col += dotCol * a * twinkle * glow * (0.55 - 0.12 * fl);
  }
  gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
```

### 模板 D：字元密度風格（程式生成點陣）

<!-- block:glsl-D -->
```glsl
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

// 注意：這是「字元密度風格」的程式生成點陣，不是真的字型字元；沒有字型圖集，不需要任何圖檔。
// 亮度場量化成 6 級，每級對應一種手繪形狀：空白 . : + # @
float disc(vec2 p, float r) { return 1.0 - smoothstep(r - 0.03, r + 0.03, length(p)); }
float bar(float v, float w) { return 1.0 - smoothstep(w - 0.03, w + 0.03, abs(v)); }

float glyph(float level, vec2 c) {           // c 在 [-0.5, 0.5]
  if (level < 0.5) return 0.0;
  if (level < 1.5) return disc(c, 0.07);                                           // .
  if (level < 2.5) return max(disc(c - vec2(0.0, 0.2), 0.08), disc(c + vec2(0.0, 0.2), 0.08));   // :
  if (level < 3.5) return max(bar(c.x, 0.07) * step(abs(c.y), 0.3), bar(c.y, 0.07) * step(abs(c.x), 0.3));  // +
  if (level < 4.5) {                                                                // #
    float v = max(bar(c.x - 0.15, 0.06), bar(c.x + 0.15, 0.06)) * step(abs(c.y), 0.36);
    float h = max(bar(c.y - 0.15, 0.06), bar(c.y + 0.15, 0.06)) * step(abs(c.x), 0.36);
    return max(v, h);
  }
  return max(disc(c, 0.36) - 0.65 * disc(c, 0.14), 0.0);                            // @
}

void main() {
  float cell = max(8.0, floor(min(u_resolution.x, u_resolution.y) / 36.0));   // 格子大小（像素）
  vec2 id = floor(gl_FragCoord.xy / cell);
  vec2 c = fract(gl_FragCoord.xy / cell) - 0.5;

  float s = min(u_resolution.x, u_resolution.y);
  vec2 cellSt = ((id + 0.5) * cell * 2.0 - u_resolution) / s;
  vec2 m = (u_mouse * 2.0 - u_resolution) / s;

  float t = u_time * 0.5;
  float field = 0.5 + 0.22 * sin(cellSt.x * 3.1 + t) + 0.22 * sin(cellSt.y * 2.7 - t * 0.8)
              + 0.22 * sin(length(cellSt) * 4.2 - t * 1.3);
  field += 0.7 * exp(-dot(cellSt - m, cellSt - m) * 3.0);   // 游標處的亮區

  float level = floor(clamp(field, 0.0, 0.999) * 6.0);
  float g = glyph(level, c);

  vec3 bg = vec3(0.015, 0.02, 0.025);
  vec3 ink = vec3(0.66, 0.92, 0.78);          // 換色：字元顏色
  gl_FragColor = vec4(mix(bg, ink, g), 1.0);
}
```

---

## 4. 常見地雷與除錯

1. **恢復後畫面空白、console 一直報 `INVALID_OPERATION: no valid shader program in use`**：context 遺失後舊的 Program 與緩衝區都失效，只重啟迴圈不夠，必須重新 `compile → link → 建緩衝區 → 取 uniform 位置`。本範本的 `onRestored` 做了這件事，不要刪。
2. **恢復時 console 出現 `delete: object does not belong to this context`**：不要對遺失前的物件呼叫 `delete*`，丟掉參考即可（`onLost` 已處理）。
3. **滑鼠沒有效果**：著色器有沒有真的用 `u_mouse` 去影響最終顏色？只是算出一個變數卻沒接到輸出是常見錯誤；驗證腳本會抓到。
4. **按鈕點不到**：內容層外層要 `pointer-events: none`，可互動元素再設 `pointer-events: auto`；腳本的滑鼠監聽掛在 `window`，不受遮罩影響。
5. **Retina 螢幕模糊或太吃效能**：畫布尺寸 = `clientWidth × min(devicePixelRatio, MAX_DPR)`。`MAX_DPR = 2.0` 是本範本的取捨，不是外部標準。
6. **編譯失敗只看到空白**：看 console 的 `[zero-hero] 片段著色器 編譯失敗：…`，後面是 GPU 驅動的 info log（含行號）。
7. **行動裝置**：片段著色器的 `highp` 並非所有裝置都支援，範本已用 `GL_FRAGMENT_PRECISION_HIGH` 退回 `mediump`，但 `mediump` 下 `sin(大數)` 型雜湊可能出現色帶；這點本範本沒有在實體手機上驗證。

---

## 5. 來源與查證（查證日期 2026-11-02）

- 原作參考：[diiviikk5/Hacktemplates @ 7b019b5](https://github.com/diiviikk5/Hacktemplates/tree/7b019b5debdf0b2b0e92eb475c8d76793162103f)（README、LICENSE、`templates/` 目錄清單、各模板 `bg.js` 已實際開啟）。本範本的程式碼為自行撰寫，未複製其程式碼。
- [WebGL 1.0 規範（Khronos）](https://registry.khronos.org/webgl/specs/latest/1.0/)：`webglcontextlost` 要 `preventDefault()` 才會送出 `webglcontextrestored`；恢復後 context 遺失前建立的 WebGL 資源（紋理、緩衝區等）都失效。已開啟該頁並讀到上述文字。
- [WEBGL_lose_context 擴充（Khronos）](https://registry.khronos.org/webgl/extensions/WEBGL_lose_context/)：`loseContext()`／`restoreContext()` 可模擬遺失與恢復（驗證腳本使用）。
- [Media Queries Level 5：prefers-reduced-motion](https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-motion)、[MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)。
- [Intersection Observer（W3C）](https://www.w3.org/TR/intersection-observer/)、[Page Visibility Level 2（W3C）](https://www.w3.org/TR/page-visibility-2/)。
- [The Book of Shaders 第 13 章：Fractal Brownian Motion](https://thebookofshaders.com/13/)：fBM 與 domain warping 技法。
- 未驗證：dvklab.vercel.app 展示站在 2026-11-02 回傳 404（`DEPLOYMENT_NOT_FOUND`），無法對照其線上效果；iquilezles.org 同日也回傳 404，本範本不引用該站內容。
