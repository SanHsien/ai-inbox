---
name: zero-build-hero-injector
description: 零構建、零依賴 WebGL Shader 與 Canvas Hero Section 快速注入技能。將高奢流體光影、液態金屬、3D Raymarching、粒子場與 ASCII 字符流原生嵌入網頁首屏，免 npm 編譯，兼具完整生命週期與 Anti-Slop 規範。
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

> 本技能範本收錄於 `templates/zero-build-hero-injector-skill.md`，專供 AI Coding Agent（Antigravity、Claude Code、Codex 等）在協助使用者開發 Landing Page、Portfolio 或 Generative UI 時，端到端自動注入高階、零依賴且具備完整生命週期管理之 WebGL Shader Hero Section。對照架構規範見 `docs/zero-build-shader-hero-sections-spec.md`。

---

## 1. 技能背景與執行定位

傳統網頁開發在引入 WebGL 或 3D 視覺時，往往需要配置龐大的 npm 套件庫（如 Three.js、React Three Fiber 等），在單檔 HTML 展示或 Generative UI 快速原型場景中極易遇到打包與依賴困難；而直接由大型語言模型生成的網頁則充斥著千篇一律的紫色漸層與平庸陰影（Visual Slop）。

本技能提供標準化管線，讓 Agent 能依據目標專案調性，一鍵將自包含的純原生 WebGL/Canvas 片段注入至既有或新建的網頁中，保證 60 FPS 順暢度且雙擊即開。

---

## 2. 端到端注入工作流程（5 步 SOP）

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   Zero-Build Hero Section 注入工作流程 (5 步 SOP)                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   [ 步驟 1: 調性識別 ] ──▶ 依專案類型挑選視覺維度 (金屬 / 流體 / 粒子 / ASCII / 3D)  │
│           │                                                                            │
│           ▼                                                                            │
│   [ 步驟 2: 提取模板 ] ──▶ 從第 3 節填空庫選取對應 GLSL 與 Canvas 驅動腳本             │
│           │                                                                            │
│           ▼                                                                            │
│   [ 步驟 3: 注入結構 ] ──▶ 寫入 HTML (Canvas 底層 + 遮罩中層 + 內容頂層)               │
│           │                                                                            │
│           ▼                                                                            │
│   [ 步驟 4: 補齊守護 ] ──▶ 加入 DPR Resize + 離屏節流 + Context Lost 防護 + Dispose    │
│           │                                                                            │
│           ▼                                                                            │
│   [ 步驟 5: 驗證驗收 ] ──▶ 跑 Anti-Slop 檢驗，確認 0 罐頭特徵，瀏覽器實測 60 FPS        │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 步驟 1：專案調性與視覺維度匹配

Agent 根據使用者需求或網站主題，匹配合適的 Shader 分類：

| 專案類型 / 業務領域 | 建議視覺分類 | 核心特徵與氛圍 | 推薦著色器模式 |
| :--- | :--- | :--- | :--- |
| **金融科技 / Web3 / 奢華硬體** | 液態金屬 (Liquid Metal) | 高反光水銀波動、冷調鈦金灰、鏡面高光 | 模板 A: Liquid Metal Chrome |
| **設計工作室 / 創意 / 音樂串流** | 流體光影 (Fluid Aurora) | 有機極光變幻、fBM 多頻煙霧、深海暗流 | 模板 B: Fluid Aurora Wave |
| **前沿科研 / 旗艦算力 / 深科技** | 3D Raymarching 空間 | 旋轉幾何多面體、無限分形、光學折射 | 模板 C: 3D Raymarching Monolith |
| **開發者工具 / CLI / 極客專案** | ASCII Art 字符矩陣 | 動態字符流、灰階亮度轉化、復古終端感 | 模板 D: Dynamic ASCII Matrix |

### 步驟 2：DOM 與 CSS 階層注入規範

在目標 HTML 檔案的 `<body>` 首部注入三層標準結構：

```html
<!-- [HERO-INJECT: BEGIN] Zero-Build Shader Hero Section -->
<header class="zero-hero-wrapper" style="position: relative; width: 100%; min-height: 100vh; overflow: hidden; background: #020617;">
  <!-- 底層: 原生 WebGL 畫布 -->
  <canvas id="zero-hero-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; display: block;"></canvas>

  <!-- 中層: 暗角與對比保護遮罩 (穿透滑鼠事件) -->
  <div class="zero-hero-mask" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; background: radial-gradient(circle at 50% 50%, rgba(2, 6, 23, 0.25) 0%, rgba(2, 6, 23, 0.85) 100%);"></div>

  <!-- 頂層: 語意化內容層 -->
  <div class="zero-hero-content" style="position: relative; z-index: 2; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 2rem; pointer-events: none; text-align: center;">
    <div class="zero-hero-interactive" style="pointer-events: auto; max-width: 800px;">
      <!-- 在此填寫客觀標籤、標題、描述與 CTA 按鈕 -->
      <span style="font-family: monospace; font-size: 0.75rem; color: #94a3b8; border: 1px solid rgba(255,255,255,0.1); border-radius: 9999px; padding: 0.25rem 0.75rem;">__HERO_KICKER__</span>
      <h1 style="font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 700; color: #f8fafc; margin: 1rem 0; line-height: 1.1; letter-spacing: -0.03em;">__HERO_TITLE__</h1>
      <p style="font-size: 1.125rem; color: #94a3b8; max-width: 600px; margin: 0 auto 2rem; line-height: 1.6;">__HERO_DESCRIPTION__</p>
      <div style="display: flex; gap: 1rem; justify-content: center;">
        <a href="__PRIMARY_CTA_LINK__" style="display: inline-flex; align-items: center; justify-content: center; padding: 0.75rem 1.75rem; background: #f8fafc; color: #020617; border-radius: 6px; font-weight: 600; text-decoration: none;">__PRIMARY_CTA_TEXT__</a>
        <a href="__SECONDARY_CTA_LINK__" style="display: inline-flex; align-items: center; justify-content: center; padding: 0.75rem 1.75rem; background: rgba(15,23,42,0.8); color: #f8fafc; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; text-decoration: none;">__SECONDARY_CTA_TEXT__</a>
      </div>
    </div>
  </div>
</header>
<!-- [HERO-INJECT: END] -->
```

### 步驟 3：著色器驅動腳本注入（自包含封裝）

在頁面底部（`</body>` 前）插入以下自包含 JavaScript 程式碼片段：

```html
<script>
(function() {
  'use strict';

  // 1. 頂點與片段著色器原始碼
  const VS_SRC = [
    'attribute vec2 a_pos;',
    'varying vec2 v_uv;',
    'void main() {',
    '  v_uv = (a_pos + 1.0) * 0.5;',
    '  gl_Position = vec4(a_pos, 0.0, 1.0);',
    '}'
  ].join('\n');

  // __FS_SOURCE_PLACEHOLDER__ (由下方第 3 節替換)
  const FS_SRC = `__SELECTED_FS_CODE__`;

  // 2. 初始化與生命週期狀態管理
  let canvas = document.getElementById('zero-hero-canvas');
  if (!canvas) return;

  let gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  if (!gl) return;

  function compile(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      gl.deleteShader(s);
      return null;
    }
    return s;
  }

  const vs = compile(gl.VERTEX_SHADER, VS_SRC);
  const fs = compile(gl.FRAGMENT_SHADER, FS_SRC);
  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  gl.useProgram(prog);

  const uRes = gl.getUniformLocation(prog, 'u_resolution');
  const uTime = gl.getUniformLocation(prog, 'u_time');
  const uMouse = gl.getUniformLocation(prog, 'u_mouse');

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const aPos = gl.getAttribLocation(prog, 'a_pos');
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  let mouseX = 0, mouseY = 0, targetX = 0, targetY = 0;
  let animId = null, isRunning = false, isIntersecting = true;
  const startT = performance.now();

  function onResize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2.0);
    const w = Math.floor(window.innerWidth * dpr);
    const h = Math.floor(window.innerHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }
  }

  function loop(now) {
    if (!isRunning || !isIntersecting) { animId = null; return; }
    mouseX += (targetX - mouseX) * 0.08;
    mouseY += (targetY - mouseY) * 0.08;
    gl.uniform2f(uRes, canvas.width, canvas.height);
    gl.uniform1f(uTime, (now - startT) * 0.001);
    gl.uniform2f(uMouse, mouseX * (canvas.width / window.innerWidth),
                        (window.innerHeight - mouseY) * (canvas.height / window.innerHeight));
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    animId = requestAnimationFrame(loop);
  }

  function start() {
    if (!isRunning) {
      isRunning = true;
      if (!animId) animId = requestAnimationFrame(loop);
    }
  }

  function stop() {
    isRunning = false;
    if (animId) { cancelAnimationFrame(animId); animId = null; }
  }

  window.addEventListener('resize', onResize);
  window.addEventListener('mousemove', function(e) { targetX = e.clientX; targetY = e.clientY; }, { passive: true });
  document.addEventListener('visibilitychange', function() { document.hidden ? stop() : start(); });

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(function(entries) {
      isIntersecting = entries[0].isIntersecting;
      isIntersecting ? start() : stop();
    }, { threshold: 0.05 });
    io.observe(canvas);
  }

  canvas.addEventListener('webglcontextlost', function(e) { e.preventDefault(); stop(); });
  canvas.addEventListener('webglcontextrestored', function() { start(); });

  onResize();
  start();
})();
</script>
```

### 步驟 4：Anti-Slop 靜態稽核

在完成網頁修改後，執行靜態 linter 確保產出無違規特徵：

```bash
python tools/verify_no_slop.py <目標檔案或目錄>
```
確認檢查結果顯示 `[PASS] 零罐頭特徵 (0 violations found)！`。

### 步驟 5：雙擊與瀏覽器即時渲染驗收
- 檢查瀏覽器控制台無任何 WebGL 警告或報錯。
- 測試視窗縮放，確保在 Retina 螢幕上渲染絕對銳利。
- 測試滑鼠軌跡，確認波動互動反應正常。

---

## 3. 核心 Shader 程式碼填空庫（GLSL Snippets）

### 模板 A：液態金屬波動 (Liquid Metal Chrome)

```glsl
precision highp float;
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

void main() {
  vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
  vec2 m = (u_mouse * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
  float dist = length(st - m);
  float mouseWave = sin(dist * 14.0 - u_time * 4.5) * exp(-dist * 2.5) * 0.12;

  vec2 q = vec2(fbm(st * 1.4 + vec2(0.0, u_time * 0.12)),
                fbm(st * 1.4 + vec2(5.2, 1.3 - u_time * 0.10)));
  vec2 r = vec2(fbm(st * 1.8 + 4.0 * q + vec2(1.7, 9.2) + u_time * 0.08),
                fbm(st * 1.8 + 4.0 * q + vec2(8.3, 2.8) - u_time * 0.06));
  float h = fbm(st * 1.6 + 3.0 * r) + mouseWave;

  vec2 eps = vec2(0.006, 0.0);
  float h_x = (fbm((st + eps.xy) * 1.6 + 3.0 * r) - fbm((st - eps.xy) * 1.6 + 3.0 * r)) * 7.0;
  float h_y = (fbm((st + eps.yx) * 1.6 + 3.0 * r) - fbm((st - eps.yx) * 1.6 + 3.0 * r)) * 7.0;
  vec3 N = normalize(vec3(-h_x, -h_y, 1.0));

  vec3 L = normalize(vec3(0.5, 0.7, 1.0));
  vec3 V = vec3(0.0, 0.0, 1.0);
  vec3 H = normalize(L + V);

  float diff = max(dot(N, L), 0.0);
  float spec = pow(max(dot(N, H), 0.0), 28.0);
  float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);

  vec3 baseCol = vec3(0.03, 0.05, 0.08);
  vec3 midCol = vec3(0.16, 0.20, 0.26);
  vec3 highCol = vec3(0.85, 0.90, 0.95);

  vec3 col = mix(baseCol, midCol, diff);
  col += highCol * (spec * 0.75 + fresnel * 0.35);
  gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
```

### 模板 B：流體極光光影 (Fluid Aurora Waves)

```glsl
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p); vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p) {
  float v = 0.0; float a = 0.5;
  for (int i = 0; i < 4; i++) {
    v += a * noise(p);
    p = p * 2.0 + vec2(0.3, 0.4);
    a *= 0.5;
  }
  return v;
}

void main() {
  vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
  vec2 m = (u_mouse * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
  float dist = length(st - m);
  float mouseWave = sin(dist * 12.0 - u_time * 4.0) * exp(-dist * 2.0) * 0.15;

  float t = u_time * 0.25;
  vec2 p = st * 1.8;
  float w1 = sin(p.x * 2.2 + t) * cos(p.y * 1.8 - t * 0.9);
  float w2 = sin(p.x * 1.5 - t * 1.1) * cos(p.y * 2.2 + t);
  float w3 = fbm(p + vec2(t * 0.15, -t * 0.12)) * 1.2;
  float wave = (w1 + w2 + w3) * 0.35 + mouseWave * 0.7;

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

---

## 4. 常見地雷與除錯指引（Troubleshooting）

1. **Retina 螢幕畫面模糊**：
   - 原因：未乘以 `window.devicePixelRatio`。
   - 修正：確保 `canvas.width = Math.floor(window.innerWidth * dpr)` 且 `gl.viewport(0, 0, canvas.width, canvas.height)`。
2. **滑鼠點擊穿透無效 / 無法點擊按鈕**：
   - 原因：中層遮罩或 Hero 內容外層容器未設定 `pointer-events: none`，導致攔截了使用者的滑鼠事件。
   - 修正：外層設 `pointer-events: none`，按鈕等互動元件顯式指定 `pointer-events: auto`。
3. **背景白屏或閃爍**：
   - 原因：Canvas 初始化前無底色，或 WebGL 上下文建立失敗。
   - 修正：容器預設給定深色背景色 `#020617`，確保即便在不支援 WebGL 的環境中仍保持深色現代質感。
