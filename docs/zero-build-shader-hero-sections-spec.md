# Zero-Build WebGL/Shader Hero Section 架構規範與視覺資產手冊

> 本規範收錄於 `docs/zero-build-shader-hero-sections-spec.md`，為 AI Coding Agent（Antigravity、Claude Code、Codex 等）在開發現代高奢商業 Landing Page、獨立 Portfolio 與 Generative UI 時，提供零依賴（Zero-Build）、零打包（No-Bundler）、高效能（60 FPS）的 WebGL/Canvas 視覺組件注入規範與資產指南。

---

## 1. 概述與問題背景（Executive Summary）

在現代前端開發與 AI Agent 生成網頁的場景中，首頁頂部首屏（Hero Section）承載著 80% 以上的使用者第一視覺印象。然而，傳統 3D/著色器視覺開發與現行大型語言模型（LLM）的介面生成普遍存在兩大結構性痛點：

1. **依賴地獄與環境構建負擔（Bundler & NPM Hell）**：
   - 現代 WebGL/3D 動效生態（如 Three.js、React Three Fiber、Spline、Babylon.js）高度仰賴 Node.js、Vite/Webpack、Babel/SWC 以及各式 loader（如 `vite-plugin-glsl`、`raw-loader`）。
   - 在 AI Agent 快速搭建原型（PoC）、產出單檔 HTML 展示或嵌入 Generative UI（如 Antigravity sidecar、iframe 預覽）時，繁重的構建配置極易導致依賴丟失、版本漂移（Version Drift）或跨框架打包失敗。
2. **AI 生成介面的「塑膠感」與同質化（Visual Slop）**：
   - LLM 直接生成的網頁介面常陷入套版陷阱：千篇一律的 Slate/Zinc 深色卡片、藍紫/粉紅漸層（`from-indigo-500 to-purple-600`）、浮誇的高擴散模糊陰影（`shadow-2xl`）以及裝飾性 Emoji。
   - 缺乏物理深度、光學折射與有機運動，使得介面呈現廉價且無質感的 AI 罐頭特徵（詳見 [`docs/anti-ai-slop-frontend.md`](./anti-ai-slop-frontend.md)）。

印度前端開發者 Manas 開發並開源的 **DVK Lab**（收錄 70 款動態 Hero Section）展示了「**Zero-Build（零構建免配置）**」的極致實踐：將 GLSL 頂點與片段著色器（Vertex & Fragment Shaders）、Canvas 生命週期迴圈與響應式 DOM 排版完全封裝於自包含的單檔結構中，在無需任何外部 npm 套件的情況下，直接透過瀏覽器原生 WebGL 1.0/2.0 API 實現 60 FPS 的光影流體、3D Raymarching 與液態金屬渲染。

本手冊將 DVK Lab 核心架構解構為標準化的 Agent 開發規範，確保 Agent 能精確、安全且穩健地產出無罐頭特徵的頂級 Hero Section。

---

## 2. Zero-Build 原生 WebGL 架構拓撲與生命週期管理

### 2.1 零依賴自包含封裝標準（Zero-Dependency Standard）

Zero-Build 的核心原則在於：**任何產出的 HTML 檔案必須在任意標準瀏覽器中雙擊即開，不發起任何非安全跨域請求，不依賴本機構建工具**。

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Zero-Build WebGL Hero Section 生命週期狀態機                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   [ 初始化階段 Init ]                                                                  │
│   ├─ 取得 WebGL 上下文 (gl = getContext('webgl') || getContext('experimental-webgl'))   │
│   ├─ 編譯頂點著色器 (Vertex Shader: 全螢幕 Quad)                                       │
│   ├─ 編譯片段著色器 (Fragment Shader: Procedural GLSL)                                 │
│   ├─ 連結 Program 並快取 Uniform Locations (u_resolution, u_time, u_mouse)             │
│   └─ 配置視窗 Resize 監聽器 (計算 DevicePixelRatio, 鋪滿容器)                           │
│           │                                                                            │
│           ▼                                                                            │
│   [ 渲染循環 Render Loop ] ◄─────────────────────────────────────────────┐             │
│   ├─ 檢查可見性 (IntersectionObserver isIntersecting && !document.hidden) │             │
│   ├─ 傳遞 Uniform 變數 (累加時間、滑鼠座標平滑內插)                      │ 60 FPS      │
│   ├─ 呼叫 gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)                         │ 動畫迭代    │
│   └─ 註冊下一幀 requestAnimationFrame(loop) ─────────────────────────────┘             │
│           │                                                                            │
│           ├──────────────────────────────────────┬───────────────────────────────────┐ │
│           ▼                                      ▼                                   ▼ │
│   [ 節流休眠 Throttle ]                 [ 上下文丟失 Context Loss ]         [ 資源釋放 Dispose ]
│   ├─ 滾動出可見範圍 (IO 觸發)           ├─ 監聽 webglcontextlost            ├─ 主動移除事件監聽
│   ├─ 分頁切換 (visibilitychange)        ├─ cancelAnimationFrame             ├─ gl.deleteProgram
│   └─ 暫停 rAF，待可見時主動喚醒         └─ 於 webglcontextrestored 重建     └─ gl.deleteShader
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### GLSL 模板字串內嵌標準
跳過 Webpack/Vite 插件，片段著色器代碼直接以 JavaScript Template Literals（ES6 模板字串）寫入：

```javascript
const VS_SOURCE = `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = (a_position + 1.0) * 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`;

const FS_SOURCE = `
  precision highp float;
  varying vec2 v_uv;
  uniform vec2 u_resolution;
  uniform float u_time;
  uniform vec2 u_mouse;

  void main() {
    vec2 st = (gl_FragCoord.xy * 2.0 - u_resolution) / min(u_resolution.x, u_resolution.y);
    // 著色運算...
    gl_FragColor = vec4(color, 1.0);
  }
`;
```

### 2.2 穩健生命週期管理的五大防線

1. **雙重適應視窗縮放與高解析度適配（Responsive Resize & Retina DPR）**：
   - 必須兼顧 CSS 物理尺寸與 Canvas 內部畫素緩衝區尺寸。
   - 避免直接使用 `window.devicePixelRatio` 導致 4K/Retina 螢幕 GPU 負載爆炸，一律設定安全上限：`Math.min(window.devicePixelRatio || 1, 2.0)`。
   - 視窗大小改變時，同步更新 `gl.viewport(0, 0, canvas.width, canvas.height)` 與 `u_resolution` uniform。

2. **60 FPS 記憶體與垃圾回收優化（GC-Safe Render Loop）**：
   - 嚴禁在 `requestAnimationFrame` 迴圈內動態配置陣列、物件或宣告大型臨時變數。
   - Uniform 位置（`gl.getUniformLocation`）必須在初始化（Init）階段一次性取得並快取至物件中，禁止在逐幀渲染時重複呼叫。

3. **離屏與後台效能節流（IntersectionObserver & VisibilityChange）**：
   - 當 Hero Section 滾動出可視範圍（如使用者向下閱讀文章內容）時，透過 `IntersectionObserver` 暫停 `requestAnimationFrame`。
   - 監聽 `document.addEventListener('visibilitychange')`，當分頁切換至後台（`document.hidden === true`）時立刻休眠，完全釋放 GPU 運算與電池功耗。

4. **WebGL 上下文丟失守護機制（Context Loss & Restoration Protocol）**：
   - 行動端記憶體不足或桌機睡眠喚醒時，WebGL 可能觸發 `webglcontextlost` 事件。
   - 必須於 Canvas 上掛載事件防護：
     ```javascript
     canvas.addEventListener('webglcontextlost', (event) => {
       event.preventDefault(); // 阻止預設行為，允許後續恢復
       cancelAnimationFrame(animationFrameId);
     }, false);

     canvas.addEventListener('webglcontextrestored', () => {
       initGL(); // 重建 Shader Program 與緩衝區
       startLoop();
     }, false);
     ```

5. **確定性資源釋放（Explicit Disposal）**：
   - 在單頁應用（SPA）路由切換或組件卸載時，主動呼叫 `dispose()`：
     - 取消 `cancelAnimationFrame`。
     - 呼叫 `gl.deleteProgram(program)`、`gl.deleteShader(vs)`、`gl.deleteShader(fs)` 與 `gl.deleteBuffer(buffer)`。
     - 移除全域 `window` 與 `document` 監聽器。

---

## 3. 70 款動態視覺之五大分類與 Shader 算法矩陣

DVK Lab 中收錄之 70 款組件涵蓋現代創意編程（Creative Coding）的五大核心視覺領域：

| 分類維度 | 核心算法與數學運算元 | 代表作品 | GPU 負載級別 | 推薦商業場景 |
| :--- | :--- | :--- | :---: | :--- |
| **1. 流體光影著色器 (Fluids & Aurora)** | Simplex Noise / Perlin Noise 疊加 Fractional Brownian Motion (fBM)、Domain Warping 座標擾動 | Vermilion, Currents, Seascape, Aurora | 中 (Medium) | 設計工作室、品牌行銷、創意藝術、音樂串流 |
| **2. 3D Raymarching (Distance Fields)** | Signed Distance Functions (SDF)、Sphere Tracing 步進演算法、數值梯度法線 (Gradient Normal)、軟陰影 | Relic, Geometric Void, Monolith | 高 (High) | 旗艦硬體、高階資安、深度運算、前沿研究展示 |
| **3. 液態金屬波動 (Liquid Metal)** | 法線擾動 (Normal Perturbation)、Matcap 環境光貼圖採樣、菲涅爾反射 (Fresnel Effect)、高光 Blinn-Phong | Chrome Ripple, Mercury Waves, Cyber Platinum | 中 (Medium) | 金融科技 (FinTech)、Web3、奢華精品、硬核工程 |
| **4. 互動式粒子場 (Particle Fields)** | 點圖元 (GL_POINTS) 渲染、滑鼠徑向引力/斥力場 (Radial Force Field)、軌跡阻尼物理衰減 | Cyber Swarm, Starfield Drift, Gravity Well | 低~中 (Low-Med) | AI 模型平台、大數據分析、雲端基礎設施 |
| **5. ASCII Art 動態字符矩陣 (ASCII Shaders)** | 畫面灰階亮度 (Luminance `dot(c, vec3(0.299,0.587,0.114))`)、等寬字符密度映射 (Char-Density Ramp) | Matrix Terminal, ASCII Fluid, Retro Cyber | 極低 (Very Low) | 開發者工具、命令列 CLI 工具、開源專案、極客風格 |

### 3.1 分類一：流體光影著色器（Fluids & Aurora Shaders）
- **數學原理**：透過多倍頻（Octaves）疊加噪聲函數：
  $$\text{fBM}(p) = \sum_{i=0}^{n-1} a^i \cdot \text{noise}(2^i \cdot p)$$
  搭配 Domain Warping（以噪聲輸出再作為下一層噪聲輸入）：
  $$q = \text{vec2}(\text{fBM}(p), \text{fBM}(p + \text{vec2}(5.2, 1.3)))$$
  $$r = \text{vec2}(\text{fBM}(p + 4.0 \cdot q + \text{vec2}(1.7, 9.2)), \text{fBM}(p + 4.0 \cdot q + \text{vec2}(8.3, 2.8)))$$
  $$\text{color} = \text{fBM}(p + 4.0 \cdot r)$$
- **視覺效果**：有機的液體流動、極光變幻、大氣煙霧與海洋波浪。

### 3.2 分類二：3D Raymarching 空間著色器（Raymarching Distance Fields）
- **數學原理**：在片段著色器中模擬光線從相機出發，沿著視線向量 $R_d$ 步進：
  $$p = R_o + t \cdot R_d$$
  以幾何體的符號距離函數 $d = \text{SDF}(p)$ 作為步長，若 $d < \epsilon$ 即判定擊中物體表面；表面法線透過微小步長偏移 $\delta$ 計算數值梯度：
  $$N = \text{normalize}(\text{vec3}(d(p+\delta_x) - d(p-\delta_x), d(p+\delta_y) - d(p-\delta_y), d(p+\delta_z) - d(p-\delta_z)))$$
- **視覺效果**：即時旋轉的立體幾何多面體、無限折疊分形、極致光影折射與景深霧化。

### 3.3 分類三：液態金屬波動（Liquid Metal Surfaces）
- **數學原理**：將 2D 平面視為動態高度場（Heightmap）$h(u, v)$，利用三角函數與時間波形疊加：
  $$h(u, v, t) = \sum_{k} A_k \sin(\vec{K}_k \cdot \vec{u} + \omega_k t + \phi_k)$$
  表面反射率由視角與法線夾角決定，使用菲涅爾近似公式（Schlick's approximation）：
  $$F \approx F_0 + (1 - F_0)(1 - \vec{N} \cdot \vec{V})^5$$
- **視覺效果**：如水銀或液態鉻金屬般的流光波浪，對滑鼠軌跡產生即時漣漪反應。

### 3.4 分類四：互動式粒子場（Interactive Particle Fields）
- **數學原理**：每個粒子擁有原始位置、速度向量與受力加速度。滑鼠游標產生向量場 $\vec{F} = \frac{G \cdot (\vec{M} - \vec{P})}{|\vec{M} - \vec{P}|^2 + \epsilon}$，驅使粒子產生排斥或聚集迴旋。
- **視覺效果**：數千顆具備引力軌跡的微光粒子，兼具高響應性與絲滑運動。

### 3.5 分類五：ASCII Art 動態字符矩陣（Dynamic ASCII Shaders）
- **數學原理**：將空間劃分為字元單元格（如 $8 \times 16$ px），計算單元格內背景亮度，並查表映射至等寬字符密度集：
  $$\text{Characters} = \text{" .:-=+*#%@"}$$
- **視覺效果**：復古賽博龐克終端、高科技資訊流與駭客代碼瀑布。

---

## 4. AI Coding Agent 呼叫與生成規格（AI Agent Spec）

為防止 Agent 產出同質化的「AI 罐頭設計」，本節制定明確的 HTML/CSS 排版結構、調色盤規範與 Prompt 注入標準。

### 4.1 DOM 與 CSS 層疊結構規範（Layering Protocol）

Hero Section 必須採用標準的三層架構（Three-Tier Layering）：

```html
<!-- 最外層容器：限制視窗高度與隱藏溢出 -->
<header class="hero-container">
  <!-- 第一層 (z-index: 0)：原生 WebGL 動態畫布，填滿視窗 -->
  <canvas id="gl-canvas" class="hero-canvas"></canvas>

  <!-- 第二層 (z-index: 1)：CSS 漸層遮罩與暗角疊加層，屏蔽滑鼠事件 -->
  <div class="hero-overlay-mask" aria-hidden="true"></div>

  <!-- 第三層 (z-index: 2)：語意化文字、CTA 按鈕與 HUD 狀態面板 -->
  <div class="hero-content">
    <nav class="hero-nav">...</nav>
    <div class="hero-body">
      <span class="hero-kicker">客觀規格標記</span>
      <h1 class="hero-title">高階商業主標題</h1>
      <p class="hero-desc">精確具體的產品描述與數值指標</p>
      <div class="hero-actions">
        <a href="#action" class="btn btn-primary">立即體驗</a>
        <a href="#docs" class="btn btn-secondary">架構手冊</a>
      </div>
    </div>
    <div class="hero-footer-status">...</div>
  </div>
</header>
```

```css
/* 標準 CSS 樣式規範 */
.hero-container {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  background-color: #020617; /* 預設 Slate-950 底色，防止 WebGL 載入前白屏 */
}

.hero-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  display: block;
}

.hero-overlay-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none; /* 關鍵：確保滑鼠軌跡能穿透至底層 Canvas */
  background: radial-gradient(circle at 50% 50%, rgba(2, 6, 23, 0.2) 0%, rgba(2, 6, 23, 0.85) 100%);
}

.hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
  padding: 2.5rem 2rem;
  pointer-events: none; /* 預設穿透 */
}

.hero-content a,
.hero-content button,
.hero-content input {
  pointer-events: auto; /* 互動元素恢復點擊響應 */
}
```

### 4.2 Anti-Slop 視覺美學硬閘門（嚴格檢驗）

產出物必須嚴格通過 [`tools/verify_no_slop.py`](../tools/verify_no_slop.py) 外部裁判檢驗：

1. **拒絕浮誇無腦陰影 (SLOP-01)**：
   - 嚴禁使用 `shadow-2xl` 或大半徑模糊陰影（`box-shadow: 0 25px 50px rgba(0,0,0,0.5)`）。
   - 一律採用 `1px` 實色微邊框（如 `border: 1px solid rgba(255, 255, 255, 0.1)`）與深淺表面階層（Surface Elevation）襯托層次。
2. **拒絕俗套藍紫漸層 (SLOP-02)**：
   - 嚴禁使用 `from-indigo-500 to-purple-600` 或霓虹粉紫色彩。
   - 採用極簡深階單色調（Slate/Zinc/Titanium）搭配冷調金屬銀灰、琥珀褐（Amber）或深邃翠綠（Emerald）。
3. **拒絕裝飾性 Emoji (SLOP-03)**：
   - 標題與按鈕中嚴禁出現 `🚀`、`💡`、`🔥`、`✨`、`🎉`、`🔮`、`🪄`、`🌟`。
   - 使用幾何符號（`·`、`›`、`—`）或純 CSS/SVG 幾何圖示。
4. **拒絕虛假動態徽章 (SLOP-04)**：
   - 嚴禁使用 `animate-ping`、`animate-pulse` 或無實際數據串流的 `[LIVE]` 假呼吸燈。
   - 標註具體更新頻率（如 `更新頻率：60Hz WebGL Loop`）。
5. **拒絕 AI 罐頭黑話文案 (SLOP-05)**：
   - 嚴禁使用 `delve`、`elevate`、`seamlessly`、`revolutionize`、`tapestry`、`empower`、`unleash`、`game-changer`。
   - 以真實客觀功能、技術參數與業務價值陳述。

---

## 5. 可讀性、效能優化指標與 Mobile 降級策略

### 5.1 效能指標與量化門檻
1. **桌機端（Desktop）**：
   - 渲染影格率：穩定在 **58 ~ 60 FPS**（16.6ms / frame）。
   - GPU 負載率：持續佔用率 $< 15\%$。
   - 初始化 Compile & Link 耗時：$< 120\text{ ms}$。
2. **行動端（Mobile）**：
   - 渲染影格率：$\ge 45\text{ FPS}$。
   - 記憶體消耗峰值：$< 50\text{ MB}$。

### 5.2 行動裝置自動降級階梯（Graceful Degradation）

```text
  [ 裝置能力評估 ]
  ├─ 檢查 navigator.hardwareConcurrency (核心數 <= 4 ?)
  ├─ 檢查 window.innerWidth (< 768px ?)
  └─ 檢查 GPU 渲染器字串 (WEBGL_debug_renderer_info)
          │
          ├── [ 高效能桌機 High-End Desktop ]
          │   └─ DPR = 2.0, Raymarching 步進 64 次, 完整 fBM 5 倍頻
          │
          ├── [ 標準行動端 / 平板 Mobile / Tablet ]
          │   └─ DPR = 1.0 ~ 1.5, Raymarching 步進降為 32 次, fBM 降為 3 倍頻
          │
          └── [ 極低階裝置 / WebGL 不支援 Fallback ]
              └─ 自動平滑降級為 CSS 靜態微漸變與輕量 Canvas 2D 粒子
```

降級程式碼片段實作：
```javascript
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth < 768;
const maxDpr = isMobile ? 1.25 : 2.0;
const dpr = Math.min(window.devicePixelRatio || 1, maxDpr);

// 著色器內根據 u_quality 參數調整迴圈上限：
// uniform int u_quality; // 0: mobile (32 steps), 1: desktop (64 steps)
```

---

## 6. 一手來源查證與引用（Primary Sources）

本手冊內容由執行 Agent 於 **2026-11-02** 完成一手官方規格與來源查證，所引述之專案、API 與演算法皆具備客觀真實性：

1. **DVK Lab 專案與展示**：
   - 專案官方展示站：[DVK Lab (dvklab.vercel.app)](https://dvklab.vercel.app)
   - 原文作者與推薦來源：Ethan（pizza的存錢日記＆＆自我成長，`@ethansavemoneydairy`）與原始作者 Manas（`@Menace_thakur`，[X 個人頁面](https://x.com/Menace_thakur)）。
   - 貼文永久出處：[Threads 分享貼文](https://www.threads.com/@ethansavemoneydairy/post/DfEsaOXgBNx)（查證日期：2026-10-31 / 2026-11-02）。
2. **Khronos Group 官方 WebGL 規範**：
   - [WebGL 1.0 Specification (Khronos Group)](https://registry.khronos.org/webgl/specs/latest/1.0/)：頂點/片段著色器管線、Shader 編譯與 Program 連結 API。
   - [WebGL 2.0 Specification (Khronos Group)](https://registry.khronos.org/webgl/specs/latest/2.0/)：GLSL ES 3.00 與浮點數紋理支援。
   - [WEBGL_lose_context Extension Specification](https://registry.khronos.org/webgl/extensions/WEBGL_lose_context/)：上下文遺失與恢復標準介面。
3. **W3C 網頁效能與標準 API**：
   - [W3C Intersection Observer API Specification](https://www.w3.org/TR/intersection-observer/)：視窗可視性非同步觀察與節流。
   - [W3C Page Visibility Level 2 (document.visibilitychange)](https://www.w3.org/TR/page-visibility-2/)：分頁背景休眠標準。
4. **數學與著色器算法原始文獻**：
   - Inigo Quilez (IQ)：[Distance Functions and Raymarching](https://iquilezles.org/articles/distfunctions/)（SDF 距離場公式庫與數值梯度法線）。
   - Stefan Gustavson：[Simplex Noise Demystified](http://staffwww.itn.liu.se/~stegu/simplexnoise/simplexnoise.pdf)（Procedural Noise 數學原理）。
