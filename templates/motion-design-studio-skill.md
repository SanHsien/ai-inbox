---
name: motion-design-studio
description: 代碼驅動 Motion Design Agent 工作室規範與 Skill 範本。以 Node.js + Playwright + FFmpeg 為 Harness，強制時間函式 Frame = f(t) 與 seek(t) 介面、Anti-Slop 視覺黑名單、Contact Sheet 8 分門檻自審循環，以及 Effort 分層路由。
triggers:
  - "motion-design"
  - "代碼驅動動效"
  - "seek(t)"
  - "contact-sheet"
  - "anti-slop"
  - "分鏡自審"
  - "playwright ffmpeg"
---

# Motion Design Studio Agent Skill (代碼驅動動態設計工作室技能規格)

> 本技能規格收錄於 `templates/motion-design-studio-skill.md`，定義 Coding Agent 在動態設計專案中以確定性 Harness 取代虛浮 Prompt 的標準實踐 SOP。  
> 適用技術棧：**Node.js (Canvas 2D / SVG / GSAP / Spring) + Playwright + FFmpeg**。  
> 核心規範對照：[`docs/code-driven-motion-design-studio-spec.md`](../docs/code-driven-motion-design-studio-spec.md)。

---

## 1. 工作室核心原則與邊界契約

```text
┌────────────────────────────────────────────────────────┐
│ 動態設計工作室四大不妥協原則                            │
├────────────────────────────────────────────────────────┤
│ 1. Harness 勝於 Prompt：以可執行的程式碼定義動畫       │
│ 2. 影片即純時間函式：Frame = f(t)，實作 seek(t) 介面    │
│ 3. 嚴格杜絕視覺罐頭：明文禁止老套 AI 藍紫漸層與齊頭淡入 │
│ 4. 8 分門檻自審循環：縮圖總覽未達 8.0 分禁止渲染視訊    │
└────────────────────────────────────────────────────────┘
```

1. **零隨機漂移（Zero Generative Drift）**：所有動畫元素的位置、透明度、縮放與旋轉必須透過確定性程式碼計算，禁止使用不可控的生成式影片擴散模型。
2. **純時間函式（Frame = f(t)）**：所有畫面狀態均為傳入時間 $t$（毫秒）的確定性映射，支援任意隨機時間跳轉（`window.seek(t)`），嚴禁內部狀態隨影格累加。
3. **客觀機械外部裁判**：正式編碼前，必須透過 `tools/audit_motion_storyboard.py` 生成縮圖總覽（Contact Sheet）並通過 8.0 分門檻自審。

---

## 2. 專案根目錄 CLAUDE.md 工作室規範範本

動態設計專案可直接將以下內容複製至專案根目錄的 `CLAUDE.md`：

````markdown
# Motion Design Studio Rules (CLAUDE.md)

## 核心開發原則
- 動畫即純時間函式：所有動畫邏輯必須封裝為 `renderFrame(tInMs)` 並暴露 `window.seek(tInMs)`。
- 禁止使用 `setInterval` 或依賴遞推的狀態累加（如 `x += v * dt`）；必須使用絕對時間公式 `x = f(t)`。
- 所有樣式禁止引入外部未授權 CDN，資產必須內聯或存放於 `assets/`。

## 視覺禁制清單（Negative Constraints 黑名單）
- ❌ SLOP-M01: 禁止漸層背景 ＋ 置中粗體標題。改用單色高對比表面（如 `#090d16`）與清晰網格排版。
- ❌ SLOP-M02: 禁止全體元素同一時間淡入。多元素進場強制使用 40ms~80ms 錯落延遲（Stagger Delay）。
- ❌ SLOP-M03: 禁止浮誇無腦陰影（`shadow-2xl`）與生硬圓角徽章。改用 1px 細緻邊框（`#1e293b`）。
- ❌ SLOP-M04: 禁止荒謬線性運動與無阻尼彈跳。位移動畫必須基於物理彈簧（Spring Physics）。
- ❌ SLOP-M05: 禁止虛假隨機數字跳動與罐頭裝飾 Emoji（🚀✨🔥）。

## 渲染前自審硬閘門
- 正式調用 FFmpeg 導出前，必須在終端執行：
  ```bash
  python tools/audit_motion_storyboard.py index.html --output-dir artifacts/storyboard
  ```
- 若評分低於 8.0 分，檢視輸出的 Worst-3 分鏡並針對性修正，直到全數通過。
````

---

## 3. 品牌色與向量資產注入流程

在開始動態編程前，Agent 必須先完成品牌資產提取與變數注入：

```text
  [ 輸入品牌網址 / 設計稿 ] ──► 抽取 Brand Identity (Hex / Fonts / SVGs)
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │ 注入動效常數表 (Brand Theme Tokens)   │
               │                                      │
               │ BG_PRIMARY:    '#090d16'             │
               │ BG_SURFACE:    '#111827'             │
               │ BORDER_SUBTLE: '#1f2937'             │
               │ TEXT_PRIMARY:  '#f9fafb'             │
               │ ACCENT_BRAND:  '#0ea5e9'             │
               │ LOGO_VECTOR:   '<svg ...></svg>'     │
               └──────────────────────────────────────┘
```

- **真實向量圖標優先**：優先使用乾淨的 SVG 代碼直接繪入 DOM 或 Canvas，禁止使用模糊的低解析度點陣截圖。
- **等寬數字防抖動**：若畫面有倒數計時或數據變化，字型必須指定等寬特徵（`font-family: monospace` 或 `font-variant-numeric: tabular-nums`），防止數值躍遷時版面寬度抖動。

---

## 4. `window.seek(t)` 標準代碼實作範本

以下為可直接取用的單檔 Canvas 動效範本（包含物理彈簧阻尼算法與 `seek(t)` 介面契約）：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <title>Motion Design Component</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #090d16; overflow: hidden; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    #viewport { width: 1280px; height: 720px; background: #090d16; position: relative; }
    canvas { width: 100%; height: 100%; display: block; }
  </style>
</head>
<body>
  <div id="viewport">
    <canvas id="stage" width="1280" height="720"></canvas>
  </div>

  <script>
    const canvas = document.getElementById('stage');
    const ctx = canvas.getContext('2d');

    // 1. 物理彈簧解析解公式（欠阻尼震盪，無歷史累積）
    function spring(tSec, stiffness = 120, damping = 14, mass = 1) {
      if (tSec <= 0) return 0;
      const omega0 = Math.sqrt(stiffness / mass);
      const zeta = damping / (2 * Math.sqrt(stiffness * mass));
      if (zeta < 1) {
        const omegaD = omega0 * Math.sqrt(1 - zeta * zeta);
        const decay = Math.exp(-zeta * omega0 * tSec);
        return 1 - decay * (Math.cos(omegaD * tSec) + (zeta * omega0 / omegaD) * Math.sin(omegaD * tSec));
      }
      return 1 - Math.exp(-omega0 * tSec) * (1 + omega0 * tSec);
    }

    // 2. 確定性純時間渲染：Frame = f(t)
    function render(tMs) {
      const t = Math.max(0, tMs / 1000);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 背景深色基底
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 錯落進場元素 A：標題（延遲 80ms）
      const p1 = spring(t - 0.08, 140, 16);
      ctx.save();
      ctx.fillStyle = '#f8fafc';
      ctx.font = '700 44px -apple-system, sans-serif';
      ctx.globalAlpha = Math.min(1, Math.max(0, p1));
      ctx.fillText('確定性動效工作室', 100, 240 + (1 - p1) * 30);
      ctx.restore();

      // 錯落進場元素 B：數據卡片（延遲 160ms）
      const p2 = spring(t - 0.16, 110, 13);
      ctx.save();
      ctx.fillStyle = '#111827';
      ctx.strokeStyle = '#1f2937';
      ctx.lineWidth = 1;
      ctx.globalAlpha = Math.min(1, Math.max(0, p2));
      const cardY = 300 + (1 - p2) * 50;
      ctx.fillRect(100, cardY, 520, 200);
      ctx.strokeRect(100, cardY, 520, 200);

      ctx.fillStyle = '#38bdf8';
      ctx.font = '600 24px monospace';
      ctx.fillText(`STATUS: ACTIVE (t=${Math.round(tMs)}ms)`, 130, cardY + 60);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '400 18px -apple-system, sans-serif';
      ctx.fillText('零隨機漂移 · 像素級渲染 · 物理彈簧阻尼', 130, cardY + 110);
      ctx.restore();
    }

    // 3. 暴露時間跳轉介面契約
    window.seek = function(tMs) {
      render(tMs);
      return Promise.resolve();
    };

    // 初始渲染
    window.seek(0);
  </script>
</body>
</html>
```

---

## 5. FFmpeg 壓縮與導出參數矩陣

當動態分鏡自審通過後，調用 FFmpeg 進行終端導出：

| 交付目標 | 編碼格式 | 完整 FFmpeg 命令列範本 | 關鍵參數說明 |
| :--- | :--- | :--- | :--- |
| **網頁交付 (MP4)** | `libx264` | `ffmpeg -y -framerate 60 -i frames/f_%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart output.mp4` | `crf 18` 視覺無失真；`pix_fmt yuv420p` 通用相容；`+faststart` 網頁秒開。 |
| **廣播後期 (ProRes)**| `prores_ks` | `ffmpeg -y -framerate 60 -i frames/f_%04d.png -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le master.mov` | `profile:v 3`（ProRes 422 HQ），10-bit 色深無失真母帶。 |
| **高畫質動圖 (GIF)** | `gif` | `ffmpeg -y -i output.mp4 -vf "fps=20,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" demo.gif` | 兩階段調色盤優化（palettegen + paletteuse），消除雜色斑點。 |
| **音畫對齊合成** | `aac` | `ffmpeg -y -i video.mp4 -i audio.wav -c:v copy -c:a aac -b:a 256k -shortest final.mp4` | `-c:v copy` 視訊流直接直通複製，精確音畫對齊。 |

---

## 6. 8 分門檻自檢指令與循環 SOP

### 6.1 自檢指令呼叫
在專案目錄下執行：
```bash
python tools/audit_motion_storyboard.py path/to/index.html \
  --duration 3000 \
  --frames 6 \
  --output-dir artifacts/audit_output \
  --min-score 8.0
```

### 6.2 評審循環 SOP（三步閉環）
1. **讀取終端報告**：檢查每幀的四維得分（構圖、對比度、物理運動、Anti-Slop）。
2. **定位 Worst-3 分鏡**：
   - 若有幀數得分 $< 8.0$：定位該時間點 $t$，檢視對應的截圖。
   - 依扣分項修訂代碼（例如：加長進場延遲以避免重疊、調高文字對比度、移除違規 Emoji）。
3. **重新驗證至綠燈**：
   - 重新執行審查工具，直到終端顯示 `[PASS]` 且 Exit Code 為 0。

---

## 7. Effort 路由決策樹

```text
                             [ 新的動態設計任務 ]
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │ 評估任務規模與鏡頭複雜度      │
                      └───────────────┬───────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
      [ 局部調整 ]              [ 單一場景短片 ]          [ 旗艦多鏡頭大片 ]
      - 微調 50ms 延遲          - 5~15 秒功能動效         - 品牌旗艦宣傳片
      - 修改 Hex 色票           - 產品 Hero Section       - 複雜數據動態可視化
      - 抽換文案標題            - 包含彈簧與錯落進場      - 跨場景轉場與音畫合流
            │                         │                         │
            ▼                         ▼                         ▼
     Effort: medium             Effort: xhigh              Effort: max
```
