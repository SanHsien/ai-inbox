# Single-File Creative Coding Skill 範本

> 本範本收錄於 `templates/single-file-creative-coding-skill.md`，定義 Agent 在生成「單檔 HTML / Canvas / Three.js 互動視覺化、架構解說動畫與 3D 體驗」時的標準協議與 Prompt 工程規範。以 ai-inbox 範本形式交付。

---

## 1. 技能定義 (YAML Frontmatter)

```yaml
name: single-file-creative-coding
description: 生成零依賴、純前端、高影格率（60 FPS）的單檔 HTML / Canvas / Three.js 互動視覺化與 3D 場景。適用於架構動態解說、物理模擬、粒子藝術與 Generative UI 視覺呈現。
triggers:
  - "互動視覺化"
  - "Three.js 單檔"
  - "Canvas 動畫"
  - "粒子特效"
  - "架構動態展示"
  - "creative coding"
  - "3D 互動頁面"
```

---

## 2. 核心架構鐵律

為確保產出能在瀏覽器中雙擊即開、無跨域阻擋、無版本漂移且能內嵌於 Generative UI / Artifacts，必須遵循以下六大鐵律：

1. **嚴格單檔閉環（Single-File Self-Contained）**：
   - 所有的 CSS 必須內嵌於 `<style>`，JS 必須內嵌於 `<script>`。
   - 嚴禁引用本地相對路徑的圖片、模型檔（.gltf/.obj）或音訊檔；幾何體、材質紋理與音效一律透過 Procedural Generation（程序化幾何、Canvas 動態繪製貼圖、Web Audio API 合成音效）即時生成。

2. **CDN 依賴鎖定固定版本（Pinned CDN Versions）**：
   - 嚴禁使用 `@latest` 或無版本號的 URL。
   - Three.js 推薦固定版本：
     - Core: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
     - OrbitControls: `https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js`
   - 其他常用工具：
     - GSAP: `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js`
     - Dat.GUI: `https://cdnjs.cloudflare.com/ajax/libs/dat-gui/0.7.9/dat.gui.min.js`

3. **雙重適應視窗響應（Responsive Resize）**：
   - Canvas 必須鋪滿或依容器自適應，監聽 `window.addEventListener('resize', onResize)`。
   - Three.js 必須同步更新相機長寬比與投影矩陣：
     ```javascript
     function onResize() {
       camera.aspect = window.innerWidth / window.innerHeight;
       camera.updateProjectionMatrix();
       renderer.setSize(window.innerWidth, window.innerHeight);
       renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
     }
     ```

4. **60 FPS 記憶體與垃圾回收優化（GC-Safe Render Loop）**：
   - 嚴禁在 `requestAnimationFrame` 迴圈中頻繁 `new THREE.Vector3()`、建立陣列或分配大物件。
   - 幾何與材質實例預先分配並重複重用；使用 `InstancedMesh` 或 `BufferGeometry` + Points 處理大量粒子。

5. **使用者手勢解鎖音訊（Web Audio Safety）**：
   - 若引入 Web Audio API，必須遵守瀏覽器自動播放政策：`AudioContext` 初始化為 suspended 狀態，待使用者點擊頁面或按鍵時再執行 `audioCtx.resume()`。

6. **深色現代美學與 HUD 覆蓋層（Modern Aesthetic & HUD）**：
   - 預設採深色背景（`#0a0b10` ~ `#050508`），配合霓虹、漸層或科技感色盤。
   - 提供半透明玻璃擬態（Glassmorphism）的 HUD 資訊面板，標明互動操作指引（拖曳旋轉、滾輪縮放、按鍵互動）。

---

## 3. 標準單檔結構模板

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Creative Coding Visualizer</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #07090e;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }
    #webgl-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: block;
    }
    .hud-panel {
      position: absolute;
      top: 16px;
      left: 16px;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 12px 16px;
      pointer-events: auto;
      z-index: 10;
    }
  </style>
  <!-- 鎖定版本 CDN -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
  <div class="hud-panel">
    <h2>視覺化標題</h2>
    <p>互動指引：滑鼠拖曳旋轉｜滾輪縮放</p>
  </div>
  <canvas id="webgl-canvas"></canvas>

  <script>
    // 1. 初始化 Scene, Camera, Renderer
    const canvas = document.getElementById('webgl-canvas');
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x07090e, 0.02);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 50);

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 2. 建構場景幾何體與材質 (Procedural)
    // ...

    // 3. 視窗適應
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    });

    // 4. 動畫迴圈
    let animationFrameId;
    function animate(time) {
      animationFrameId = requestAnimationFrame(animate);
      // 更新運動狀態
      renderer.render(scene, camera);
    }
    animate(0);
  </script>
</body>
</html>
```

---

## 4. Agent 提示詞調用樣板（System Prompt Injection）

```markdown
當使用者要求「視覺化展示」、「解說某演算法 / 架構」或「產生 3D / Canvas 特效」時，請依據 Single-File Creative Coding 規範生成單檔 HTML：
1. 確保包含完整的 HTML 結構、CSS 樣式與 JS 邏輯，可存為 `.html` 直接點開執行。
2. 採用固定版本 CDN（Three.js r128 或 GSAP 3.12.2），禁止使用未鎖定版本的網址。
3. 採用現代深色介面，具備自適應視窗縮放與平滑互動（支援滑鼠滾輪與拖曳）。
4. 代碼內部杜絕記憶體洩漏，維持穩定 60 FPS。
```
