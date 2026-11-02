# 代碼驅動 Motion Design Agent 工作室規範指南 (Code-driven Motion Design Studio Spec)

本規範收錄於 `docs/code-driven-motion-design-studio-spec.md`，定義以程式碼驅動動態設計（Code-driven Motion Design）的工程化標準體系。旨在徹底消除傳統生成式影片的隨機漂移、文字變形與 AI 視覺罐頭疲勞（AI Slop），建立具備確定性、像素級精確度與可自動化迴歸測試的動態設計 Harness 工作流。

---

## 1. 核心理念：以「確定性 Harness」取代「機率性 Prompt」

在 AI 影片與動效生成領域，傳統「純文字 Prompt 生成影片」面臨四項工程痛點：
1. **關鍵幀隨機漂移**：無法精確指定某一毫秒的空間佈局與物體狀態。
2. **品牌資產失真**：SVG Logo、品牌標準色 Hex、清晰字體與產品 UI 截圖容易模糊變形。
3. **不可重複性與黑箱**：同一段 Prompt 無法做小步版本控制（Git Diff）或局部細修。
4. **AI 視覺罐頭感（AI Slop）**：普遍出現俗套藍紫漸層、全體齊頭淡入、無阻尼生硬彈跳等模板特徵。

工程破局之道：**「重點是 Harness，不是 Prompt」**。
將大語言模型（如 Claude Opus / Sonnet）置入確定性的動效開發工作線束（Harness）中，模型只負責撰寫結構嚴密的動效代碼；渲染、取樣、度量與壓縮全部交由本機確定性工具鏈執行：

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                   代碼驅動 Motion Design Agent Harness 系統架構                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  [ 人類輸入 / 產品規格 ] ──► (產品網址、品牌 Hex 色票、SVG Logo、文案、關鍵影格時序)              │
│       │                                                                                          │
│       ▼                                                                                          │
│  [ Coding Agent (Opus / Sonnet) ]                                                                │
│  ├── 工作室規範約束 ──────► 明確禁止老套視覺罐頭（SLOP-M01 ~ SLOP-M05）                           │
│  ├── 品牌資產注入模組 ────► 讀取真實 SVG 向量圖形、高解析度截圖、精確色票                        │
│  └── 動效程式碼生成 ──────► 嚴格遵循純時間函式契約：Frame = f(t)，實作 window.seek(t)             │
│       │                                                                                          │
│       ▼                                                                                          │
│  [ 本地執行環境 (The Triad Harness) ]                                                            │
│  ├── 1. Node.js 執行期 ───► 承載 Web / HTML5 Canvas / SVG / GSAP / 物理彈簧引擎動效腳本         │
│  ├── 2. Playwright 瀏覽器 ─► 隔離無頭環境，調用 window.seek(t) 隨機存取抽樣關鍵影格               │
│  └── 3. FFmpeg 編碼器 ────► 視訊幀合流、H.264/ProRes 高畫質轉碼、音畫精確同步與 Web 串流優化     │
│       │                                                                                          │
│       ▼                                                                                          │
│  [ 渲染前機械自審打分循環 (Pre-render Contact Sheet Scoring) ]                                   │
│  ├── 抽樣 6~12 組關鍵時點生成縮圖總覽 (Contact Sheet)                                            │
│  ├── 外部裁判機械度量：構圖層級、對比度、物理運動自然度、Anti-Slop 罐頭特徵                      │
│  ├── 自動找出評分最低的 3 個分鏡 (Worst-3 Frames) 進行方針修正                                    │
│  └── 質量硬閘門：全部分鏡評分達 8.0 分以上，始允許啟動 FFmpeg 終端視訊渲染                      │
│       │                                                                                          │
│       ▼                                                                                          │
│  [ 終端交付產物 ] ──► 1080p/4K 60fps 視訊檔（MP4 / ProRes）＋ 影格總覽 HTML 報告                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 三位一體 Harness 執行環境標準 (The Triad Harness Standard)

工作室 Harness 由三大確定性工具構成，各司其職且邊界分明：

### 2.1 Node.js 執行期環境標準
- **職責**：動態效果代碼承載、資產打包與本機靜態伺服器（Local Preview Server）。
- **依賴邊界**：
  - 核心繪製優先使用純 Web 標準（Canvas 2D API、SVG DOM、CSS Transforms）。
  - 動效引擎允許使用輕量成熟函式庫（如 GSAP 或自研 Spring 物理計算模組），嚴禁引入不支援確定性時間跳轉的隨機定時器（如裸用 `setInterval`、`Date.now()`）。
- **規格要求**：
  - Node.js LTS（v20+）。
  - 單檔 HTML 或模組化腳本均可獨立開啟，不依賴外部連網 CDN（所有資產皆本機化或內聯 Base64/SVG）。

### 2.2 Playwright 自動化渲染環境標準
- **職責**：精準視窗隔離渲染、時間跳轉驅動與無損影格擷取。
- **配置參數規範**：
  ```javascript
  const browser = await chromium.launch({
    headless: true,
    args: ['--enable-surface-synchronization', '--run-all-compositor-stages-before-draw']
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1, // 預設 1x；高解析度可指定 2
  });
  ```
- **執行要求**：
  - 透過 `page.evaluate((t) => window.seek(t), timestamp)` 控制動效時間軸。
  - 等待 `seek(t)` 的 Promise 決議完成後，再以 `page.screenshot({ type: 'png' })` 擷取影像。
  - 禁止在動畫播放期間以螢幕錄製方式粗暴錄影，必須逐影格（Frame-by-frame）或按關鍵影格抽樣。

### 2.3 FFmpeg 終端導出標準
- **職責**：影像序列無損組合、視訊轉碼、色彩空間校準與音訊合流。
- **高畫質導出參數模板**：
  ```bash
  # 1. 網頁交付標準 (MP4 / H.264 / yuv420p)
  ffmpeg -y -framerate 60 -i frames/frame_%04d.png \
    -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
    -movflags +faststart output.mp4

  # 2. 廣播後期級交付標準 (Apple ProRes 422 HQ)
  ffmpeg -y -framerate 60 -i frames/frame_%04d.png \
    -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le output.mov
  ```
- **畫質與相容性要求**：
  - `pix_fmt` 必須明確指定 `yuv420p`，防止 QuickTime 與各平台行動瀏覽器黑屏無法解碼。
  - `-movflags +faststart` 將 `moov atom` 前移至檔案開頭，確保網頁串流時隨開即播。
  - CRF（Constant Rate Factor）控制在 18~22 之間，達到視覺無失真且檔案體積受控。

---

## 3. 時間函式契約：Frame = f(t) 與 seek(t) 規範

### 3.1 數學模型與純函式定義
整部動效在數學上嚴格視為時間參數 $t$（毫秒為單位，$\mathbb{R}_{\ge 0}$）的純函式：
$$\text{Frame State} = f(t)$$
- **冪等性（Idempotence）**：對任意時間 $t$，無論被呼叫一次或連續呼叫十次，產出的 DOM 樹、SVG 屬性或 Canvas 像素矩陣必須百分之百一致。
- **無歷史累積依賴（Zero History Dependency）**：當時間從 $t=1000$ 跳躍至 $t=2000$ 時，畫面狀態僅由 $t=2000$ 的參數計算得出，嚴禁出現 `position += velocity * dt` 這類依賴中途每一影格累加的遞推副作用。
- **任意隨機存取（Random Access）**：動態時間軸必須支援逆向跳轉（例如由 $t=3000$ 直接跳至 $t=500$），且結果與正向播放至 $t=500$ 完全相同。

### 3.2 `window.seek(t)` JavaScript 介面契約規格
任何交付的 HTML5 動態設計頁面，必須在全域 `window` 物件上實作符合以下規格的 `seek` 函式：

```typescript
/**
 * 將整頁動畫瞬移至指定的時間點（毫秒）並完成繪製
 * @param tInMs - 時間軸偏移量（毫秒），從 0 開始
 * @returns 當繪製完成時決議的 Promise（或同步 return）
 */
window.seek = function(tInMs: number): Promise<void> | void;
```

#### 介面規格嚴格約束：
1. **輸入單位**：整數或浮點數之毫秒（ms）。`t=0` 為動畫起始點。
2. **非同步決議（Async Resolution）**：若涉及 Canvas 非同步濾鏡、字型載入或圖片繪製，`window.seek` 必須回傳 `Promise<void>`，確保在 `resolve()` 呼叫時當前影格已完全光柵化至螢幕表面。
3. **播放器狀態凍結**：調用 `seek(t)` 時，如果內部包含自動播放循環（`requestAnimationFrame`），必須立即暫停自動推進，將繪製權完全交由 `seek` 接管。

### 3.3 範例實作模板：Canvas 2D 與 DOM 物理彈簧

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <title>Motion Studio seek(t) Template</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #090d16; color: #f1f5f9; font-family: -apple-system, sans-serif; }
    #canvas { display: block; width: 1280px; height: 720px; }
  </style>
</head>
<body>
  <canvas id="canvas" width="1280" height="720"></canvas>
  <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    // 阻尼彈簧物理函式：計算在 t 秒時的位移 (0 -> 1)
    function spring(t, stiffness = 120, damping = 14, mass = 1) {
      if (t <= 0) return 0;
      const omega0 = Math.sqrt(stiffness / mass);
      const zeta = damping / (2 * Math.sqrt(stiffness * mass));
      if (zeta < 1) { // 欠阻尼震盪收斂
        const omegaD = omega0 * Math.sqrt(1 - zeta * zeta);
        const decay = Math.exp(-zeta * omega0 * t);
        return 1 - decay * (Math.cos(omegaD * t) + (zeta * omega0 / omegaD) * Math.sin(omegaD * t));
      }
      return 1 - Math.exp(-omega0 * t) * (1 + omega0 * t); // 臨界阻尼
    }

    // 核心純時間渲染函式：Frame = f(t)
    function renderFrame(tInMs) {
      const tSec = Math.max(0, tInMs / 1000);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 背景深色基底
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 元素 A：標題错落進場（延遲 100ms）
      const pTitle = spring(tSec - 0.1, 140, 16);
      ctx.save();
      ctx.fillStyle = '#f8fafc';
      ctx.font = '600 48px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.globalAlpha = Math.min(1, Math.max(0, pTitle));
      ctx.translate(120, 200 + (1 - pTitle) * 40);
      ctx.fillText('代碼驅動動態設計工作室', 0, 0);
      ctx.restore();

      // 元素 B：品牌卡片彈簧進場（延遲 220ms）
      const pCard = spring(tSec - 0.22, 100, 12);
      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      ctx.globalAlpha = Math.min(1, Math.max(0, pCard));
      const cardY = 260 + (1 - pCard) * 60;
      ctx.fillRect(120, cardY, 480, 220);
      ctx.strokeRect(120, cardY, 480, 220);

      // 卡片內文
      ctx.fillStyle = '#94a3b8';
      ctx.font = '400 20px monospace';
      ctx.fillText(`Frame Time: ${Math.round(tInMs)} ms`, 150, cardY + 50);
      ctx.fillText(`Spring Progress: ${(pCard * 100).toFixed(1)}%`, 150, cardY + 90);
      ctx.restore();
    }

    // 對外暴露標準介面契約：window.seek(t)
    window.seek = function(tInMs) {
      renderFrame(tInMs);
      return Promise.resolve();
    };

    // 預設渲染 t=0
    window.seek(0);
  </script>
</body>
</html>
```

---

## 4. 視覺設計 Anti-Slop 檢查表與專業動效標準

### 4.1 核心禁制清單（Negative Constraints 黑名單）

| 違規編號 | 老套視覺罐頭特徵 (AI Slop) | 典型代碼特徵與違規範例 | 嚴格禁止理由 |
| :--- | :--- | :--- | :--- |
| **SLOP-M01** | **漸層背景 ＋ 置中粗體標題**<br>*(Centered Gradient Hero)* | `linear-gradient(135deg, #6366f1, #a855f7)` 滿版漸層背景，搭配單一置中文案 | 典型 AI 模板偷懶風格，缺乏資訊層級、對齊動線與品牌個性。 |
| **SLOP-M02** | **全體元素齊頭同時淡入**<br>*(Uniform Simultaneous Fade-In)* | 所有元件共用相同的 `transition: opacity 0.5s` 且 `delay: 0s` | 視覺死板呆滯，缺乏動態焦點引導，無法突顯關鍵訊息優先順序。 |
| **SLOP-M03** | **角落呆板小標籤與生硬邊框**<br>*(Stiff Pill Badges & Rough Borders)* | 左上角硬塞生硬圓角標籤、浮誇無腦陰影 `shadow-2xl`、高彩霓虹邊框 | 破壞畫面平衡，分散對視覺主體的專注度，充斥廉價模板感。 |
| **SLOP-M04** | **荒謬線性運動與無阻尼彈跳**<br>*(Linear Easing & Undamped Bounce)* | `transition-timing-function: linear` 或粗暴反覆彈跳 `alternate infinite` | 違背真實物理世界物體慣性，畫面顯得廉價、生硬且具備機械塑料感。 |
| **SLOP-M05** | **虛假數字跳動與罐頭隨機粒子**<br>*(Fake Tickers & Random Particle Noise)* | 無意義的隨機亂數快速跳動、背景漂浮毫無物理邏輯的發光幾何光點 | 視覺噪音過多，試圖以低成本動態掩蓋設計內容的空洞貧乏。 |

### 4.2 專業動效工程標準（Positive Motion Standards）

1. **物理彈簧運動（Spring Physics Over Magic Numbers）**：
   - 拒絕憑空猜測貝茲曲線參數。位移與縮放動畫必須以**剛度（Stiffness $k$）**、**阻尼（Damping $c$）**與**質量（Mass $m$）**計算。
   - 介面入場偏好臨界阻尼或輕微欠阻尼（$\zeta \approx 0.7 \sim 0.85$），確保動作俐落乾脆，避免超過 2 次無效來回振盪。
2. **錯落時序與節奏編排（Staggered Entrances）**：
   - 多元素入場時，強制按視覺動線設定階梯式延遲（Stagger Delay）：每個相鄰元素延遲 40ms 至 80ms。
   - 進場順序：背景結構 $\rightarrow$ 主要圖形/數據 $\rightarrow$ 標題文字 $\rightarrow$ 補充元數據。
3. **空間景深與視差層次（Parallax & Spatial Layering）**：
   - 畫面元素必須劃分前、中、後三層，鏡頭或主體移動時，各層保持不同的相對速率（如 1.0x、0.6x、0.2x）。
4. **真實品牌素材注入**：
   - 強制載入官方真實 SVG 向量圖標、精確品牌 Hex 色票（例如背景採用深色 `#090d16`、卡片 `#1e293b`、高對比文字 `#f8fafc`）。
   - 數字採用等寬字型（`font-mono`），時間與數值動態維持字元排版穩定。

---

## 5. 渲染前 Contact Sheet 自審打分協議與 Effort 路由

### 5.1 縮圖總覽抽樣協議（Contact Sheet Sampling）
在正式交由 FFmpeg 執行逐影格視訊渲染前，Agent **必須**先抽取動效的關鍵時點畫面，拼接成一張縮圖總覽（Contact Sheet / Storyboard）：
- **抽樣原則**：
  - 總時長等分抽樣（例如 3 秒動效抽取 $t = 0\text{ms}, 500\text{ms}, 1000\text{ms}, 1500\text{ms}, 2000\text{ms}, 2500\text{ms}$ 共 6 幀）。
  - 狀態轉折點補強（元素剛進場 $t_{\text{in}}$、動態最高峰 $t_{\text{peak}}$、最終定格態 $t_{\text{end}}$）。
- **縮圖總覽排版規格**：
  - 以 $2 \times 3$ 或 $3 \times 4$ 矩陣拼接成單一高對比圖形（PNG / HTML）。
  - 每一分鏡必須清楚標記時間戳記（例如 `T: 1500ms`）與當前幀編號。

### 5.2 1~10 分機械自審打分矩陣（Scoring Rubric）

每個分鏡由四個維度評分，各佔 2.5 分，滿分 10.0 分：

```text
┌──────────────────────┬──────────────────────┬────────────────────────────────────────────────────────┐
│ 維度                 │ 配分                 │ 扣分與判定指標                                         │
├──────────────────────┼──────────────────────┼────────────────────────────────────────────────────────┤
│ 1. 構圖與資訊層級    │ 0.0 ~ 2.5 分         │ 扣分：元素重疊擠壓（-1.0）、超出安全視區截斷（-1.0）、 │
│                      │                      │ 視覺重心偏移失衡（-0.5）。                             │
│ 2. 對比度與易讀性    │ 0.0 ~ 2.5 分         │ 扣分：文字背景對比小於 4.5:1（-1.0）、畫面全黑/全白空   │
│                      │                      │ 洞（-1.5）、小字糊焦難辨（-0.5）。                     │
│ 3. 節奏動態與物理    │ 0.0 ~ 2.5 分         │ 扣分：畫面多幀靜態凍結無變化（-1.0）、線性突兀急停      │
│                      │                      │ （-1.0）、過度回彈晃動（-0.5）。                       │
│ 4. 零罐頭感合規性    │ 0.0 ~ 2.5 分         │ 扣分：觸犯 SLOP-M01~M05 任何一項（每項 -1.0）。        │
└──────────────────────┴──────────────────────┴────────────────────────────────────────────────────────┘
```

### 5.3 自審修復閉環與硬閘門（The Hard Gate）
1. **找出最低分鏡（Worst-3 Frames）**：
   自動挑出得分最低的 3 個分鏡，輸出其時間戳記、扣分項目與具體問題描述。
2. **針對性代碼重構**：
   Agent 根據扣分指標進行局部代碼修復（調整延遲階梯、修改剛度係數、替換色彩層級），禁止全盤推翻重寫。
3. **終端渲染硬閘門**：
   **所有分鏡評分必須全數達到 8.0 分以上**，才獲准調用 FFmpeg 進行逐影格合成導出；若有任一分鏡低於 8.0 分，立即阻擋渲染並強制重新驗收。

### 5.4 Effort 思考等級分層路由指南

```text
┌──────────────┬──────────────────────────────┬────────────────────────────────────────────────────────┐
│ Effort 等級  │ 適用場景                     │ 思考深度與資源分配建議                                 │
├──────────────┼──────────────────────────────┼────────────────────────────────────────────────────────┤
│ `medium`     │ 局部微調與維護               │ 適用於微調時序延遲（20ms~50ms）、修改文字文案、微調    │
│              │                              │ 色票 Hex、修復單一元素的邊界溢出問題。                 │
│ `xhigh`      │ 完整動效短片創作             │ 適用於 5~15 秒獨立功能動效、產品 Hero 區塊動態、包含   │
│              │                              │ 錯落進場與彈簧物理的全新分鏡設計。                     │
│ `max`        │ 旗艦級開場與發布大片         │ 適用於多鏡頭轉場、複雜資料可視化流動、高難度品牌空間   │
│              │                              │ 視差展演，需深度思考劇本節奏與跨鏡頭連貫性。           │
└──────────────┴──────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 6. 來源與查證依據 (References)

本規範各項事實、介面協議與命令列參數，均核實自以下一手文獻與官方標準（查證日期：2026-10-28 ｜ 2026-11-02）：

1. **0xalpha.ai Threads 實戰分享**：
   - 連結：`https://www.threads.net/@0xalpha.ai/post/DeMLz-KD1EE`
   - 核實重點：Harness 架構、seek(t) 時間純函式、CLAUDE.md 禁用老套罐頭、Contact Sheet 8 分門檻自審循環。
2. **Playwright 官方文件**：
   - 連結：`https://playwright.dev/docs/api/class-page`
   - 核實重點：`page.evaluate` 執行期環境交互、`page.screenshot` 像素光柵化與多通道（channel）瀏覽器呼叫支援。
3. **FFmpeg 官方編碼與轉碼標準**：
   - 連結：`https://ffmpeg.org/ffmpeg.html`
   - 核實重點：`libx264` 之 CRF（18~22）無損壓縮、`yuv420p` 色彩空間相容性、`+faststart` 網頁優化旗標。
4. **Remotion & Motion Canvas 時間函式架構**：
   - 連結：`https://www.remotion.dev/docs/terminology`
   - 核實重點：確定性影格取樣模型、時間軸無副作用渲染契約。
