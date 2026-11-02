# Zero-Build WebGL/Shader Hero Section 架構規範與視覺資產手冊

> 對象：要在網頁首屏放 WebGL 全螢幕著色器背景的開發者與 AI Coding Agent（Antigravity、Claude Code、Codex 等）。
> 讀完能做的事：判斷原作（Hacktemplates／dvklab）哪些東西可以直接拿、哪些要自己補；用本 repo 的範本把一段著色器背景注入網頁，並用腳本驗證它真的會動、會回應游標、context 遺失後能恢復。
> 對應檔案：自製示範 [`assets/shader-hero-demo/index.html`](../assets/shader-hero-demo/index.html)、注入範本 [`templates/zero-build-hero-injector-skill.md`](../templates/zero-build-hero-injector-skill.md)。

---

## 0. 來源、版本與授權（先讀）

| 項目 | 內容（皆於 2026-11-02 實際開啟或呼叫 API 確認） |
| :--- | :--- |
| 原作 repo | [`diiviikk5/Hacktemplates`](https://github.com/diiviikk5/Hacktemplates)；本文所有「原作」事實都對照 commit [`7b019b5debdf0b2b0e92eb475c8d76793162103f`](https://github.com/diiviikk5/Hacktemplates/tree/7b019b5debdf0b2b0e92eb475c8d76793162103f)（2026-10-27 15:50:28 UTC，訊息 `analytics: Microsoft Clarity on the gallery page (not in templates)`）。repo 之後的變動不在本文範圍。 |
| 名稱 | README 標題是 `dvklab`，repo 名稱是 `Hacktemplates`。本 repo 的筆記寫作 DVK Lab。 |
| 授權 | `LICENSE` 為 MIT，`Copyright (c) 2026 diiviikk5`。README 另聲明：MIT 只涵蓋程式碼（HTML、CSS、JS、GLSL），圖片模板所用的參考圖不在授權範圍，商用前要換成自己有權利的圖。 |
| 作者 | 筆記寫「印度開發者 Manas（@Menace_thakur）」。**查不到這個說法的依據**：repo 的 contributors API 只有一位 `diiviikk5`（157 次提交），其 GitHub 公開資料顯示名稱 `Divik Arora`。`diiviikk5` 與 Manas／@Menace_thakur 是否為同一人、國籍為何，本文一律視為**未確定**，不採用筆記的說法。 |
| 展示站 | `https://dvklab.vercel.app` 與 `/templates/vermilion/` 於 2026-11-02 回傳 404（`DEPLOYMENT_NOT_FOUND`）。README 的「Copy hero」流程（貼上後資源從託管站載入）目前走不通，原作的線上效果本文**未驗證**。 |
| 本 repo 的程式碼 | demo 與範本的 GLSL／JS 都是本 repo 自行撰寫，沒有複製原作任何檔案。若你改為直接複製原作檔案，要保留其 MIT 授權聲明。 |

---

## 1. 「Zero-Build」在原作裡實際是什麼

原作 README 的說法是 `No build, no install. Each hero is one HTML file plus one bg.js.`，也就是**不是單檔**，雙擊也不一定能開。依實際檢查，可以分成四種交付形態：

```text
  形態 1  單檔內嵌            ← 本 repo 的 demo 與範本：一個 HTML，著色器寫在內嵌 <script>
          雙擊（file://）可開，沒有外部請求

  形態 2  HTML + bg.js         ← 原作的 10 個純程式生成模板（bg.js 內沒有圖檔路徑）
          同目錄放兩個檔；file:// 實測可跑（mercury）

  形態 3  HTML + bg.js + 圖檔   ← 原作其餘 60 個（bg.js 內有 .jpg／.png 路徑）
          必須 http(s)://；file:// 會被瀏覽器的 CORS 規則擋掉貼圖

  形態 4  形態 3 + CDN          ← 原作的 ashborne、vermilion：另外從 jsdelivr 載入
          GSAP 3.12.5、ScrollTrigger 3.12.5、Lenis 1.1.13（捲動型體驗）
```

形態 3 的實測（Edge 無頭模式，2026-11-02，檔案取自上述 commit）：`abyss/bg.html` 以 `file://` 開啟，console 出現 `Access to image at 'file:///…/scene.jpg' from origin 'null' has been blocked by CORS policy`；同一份檔案經 `python -m http.server` 以 `http://127.0.0.1` 開啟則沒有錯誤。`mercury/bg.html`（形態 2）兩種方式都正常。其餘圖片模板沒有逐一實測，只依 README 與 bg.js 載入圖檔的方式推論。

因此本規範的 Zero-Build 定義是：**沒有 npm、沒有打包器、沒有框架；網頁是否單檔、是否需要 http:// 要明說，不可一概宣稱「雙擊即開」**。

---

## 2. 原作 repo 的可驗證結構

在 commit `7b019b5` 的 `templates/` 下有 **70 個目錄**（遞迴列出整棵樹共 520 個檔案，未被截斷）。每個目錄固定有 `index.html`（完整 hero）、`bg.html`（只有動態背景）、`bg.js`（背景本體，掛載在 `canvas[data-bg]`）與縮圖；圖片模板另有 `scene.jpg`、`maps.png` 等。

以下數字是**對 70 個 `bg.js` 做文字搜尋**得到的，不是逐檔人工閱讀：

| 項目 | 結果 |
| :--- | :--- |
| 含 `getContext('webgl2')` | 60 個 |
| 只用 WebGL 1（`getContext('webgl')`） | 10 個：cloudline、currents、event-horizon、fold、furnace、mercury、orbit-globe、prism-glass、seascape、signal |
| 掛載點 `canvas[data-bg]`、支援 `?preview` 低解析度 | 70 / 70 |
| 含 `prefers-reduced-motion` | 70 / 70 |
| 含 `IntersectionObserver`（離屏暫停） | 64 個；沒有的 6 個：ashborne、halftone、orbit-ascii、relic、vapor、vermilion |
| 含 `webglcontextlost` / `webglcontextrestored` | **0 個** |
| 含 `dispose` 或 `deleteProgram` | **0 個** |
| 檢查 `COMPILE_STATUS` | 70 / 70；檢查 `LINK_STATUS` 的是 **0 個** |
| bg.js 含圖檔路徑（形態 3、4） | 60 個；不含的 10 個即上列 WebGL 1 那組 |

抽查 `mercury/bg.js`：取不到 WebGL 時把 canvas 的 CSS `background` 設成漸層並結束；著色器編譯失敗只 `console.error` info log，沒有畫面提示（全部 70 個都沒有檢查 program 的連結狀態，見上表）。

**結論：** context 遺失恢復、Dispose、編譯與連結錯誤回報，在原作 bg.js 裡搜尋不到，是本 repo 第 4 節額外要求的工程品質，不是原作的做法。

---

## 3. 原作的分類與名單（照 README，不自編）

### 3.1 README「What's inside」的五個家族

README 只為每個家族列出 3 個範例，**沒有給 70 個作品的完整歸屬**。下表逐字對應 README（作品名即 README 所列）：

| 家族（README 原文） | README 對家族的描述 | README 所列範例 |
| :--- | :--- | :--- |
| Experiences | 多房間捲動故事：Lenis＋GSAP ScrollTrigger 驅動一個 WebGL 場景，房間之間有鏡頭俯衝 | Vermilion、Ashborne |
| Shaders & 3D | 光線步進與光線追蹤場景，全程式生成：黑洞、液態鉻、海洋、雲、玻璃 | Event Horizon、Mercury、Currents |
| Living artwork | 讓插畫動起來：景深視差、骨架翅膀、流動火焰、風、天氣 | Desert Dragon、Starmind、Respite |
| ASCII & print | 以字元或半色調網點呈現的即時 3D 與模擬 | Orbit ASCII、Vapor、Halftone |
| Gradients & glass | 顆粒漸層、條紋玻璃、絲綢摺痕、穿過條紋玻璃的火光 | Fold、Furnace、Fluted |

其他 README 明列的作品：Featured 區的 Relic、Ronin、Signal、Event Horizon、Fold、Orbit ASCII、Sentinel、Vapor、Mercury；Build log 的批次說明（Batch 3 full-motion heroes、Batch 4 experiences：Vermilion 與 Relic、Batch 5 ASCII family＋Ember experience：Orbit ASCII、Halftone、Vapor、Ashborne、Ronin、Respite）。另外 `seascape`、`cloudline`、`orbit-globe`、`prism-glass` 四個目錄存在，但 README 全文沒有提到。

### 3.2 70 個目錄清單（commit `7b019b5`）

依 bg.js 是否含圖檔路徑分兩組（分組是本文依檔案內容的機械分類，**不是 README 的家族**）：

- **不含圖檔路徑（10）**：cloudline、currents、event-horizon、fold、furnace、mercury、orbit-globe、prism-glass、seascape、signal。
- **含圖檔路徑（60）**：abyss、ash-king、ashborne、aura、aurora、aurora-horizon、beam、bokeh、canyon-blue、canyon-magenta、canyon-violet、daybreak、desert-dragon、dusk、eclipse、ember、evergreen、fluted、fuji、glitch、grotto、halftone、ink-dragon、meadow、nimbus、orbit-ascii、pixel-sword、pocket、prism、red-dragon、redwood、reed-crimson、reed-ember、reed-flame、reed-rose、reed-spectrum、relic、respite、riptide、ronin、ruins、sandstorm、savanna、sentinel、silk、smoke-dragon、solstice、spectrum、starmind、static、stipple、stratosphere、sunset-ridge、thermal、tidewave、twilight、ukiyo、ultraviolet、vapor、vermilion。

README 說明 `Currents` 是「Robert Beatty 的《Currents》封面外觀的 shader 重建」、`Starmind` 的海報作者是 Dogan Ural；`Signal` 的風格參考圖帶浮水印，所以只重建效果不用圖。

### 3.3 勘誤：筆記與上一版規範寫的作品名

筆記與本文上一版引用了下列作品名。在 commit `7b019b5` 的目錄樹、README 與全部 `bg.js`／`index.html` 中**都查無**：Geometric Void、Monolith、Chrome Ripple、Mercury Waves、Cyber Platinum、Cyber Swarm、Starfield Drift、Gravity Well、Matrix Terminal、ASCII Fluid、Retro Cyber。本文不再使用這些名稱。

筆記的「五大分類」（流體光影、3D Raymarching、液態金屬、粒子星系、ASCII）也不是原作的分類：README 沒有「粒子」家族，Vermilion 與 Relic 在 README 屬於 Experiences 而不是「流體光影」，Currents 屬於 Shaders & 3D。概念上相近的原作作品只能這樣對照，**它們並不是同一件作品**：

| 筆記的概念 | 原作中概念相近的作品（README 描述） |
| :--- | :--- |
| 液態金屬 | Mercury（liquid chrome that takes any shape）、Currents（chrome sphere in op-art streamlines） |
| ASCII 字符矩陣 | Orbit ASCII（ASCII 引擎：scene → cell buffer → JetBrains Mono 字型圖集）、Vapor（可用游標攪動的 ASCII 煙霧） |
| 粒子 | README 沒有對應家族；Ronin 的描述有 `wisps stream`，但那不是粒子系統的證據 |

---

## 4. 本 repo 的 Zero-Build 生命週期規範

下表是本 repo 對**自行撰寫**的 hero 背景的要求（原作做到的部分已在第 2 節標明）。每一項都有對應的瀏覽器實測，見第 7 節。

```text
          ┌─────────────┐  取不到 WebGL
          │    init     ├──────────────────────────▶ nowebgl（隱藏 canvas，露出 CSS 漸層）
          └──────┬──────┘  編譯／連結失敗
                 │         ─────────────────────────▶ error  （同上，console.error 含 info log）
                 ▼
   ┌──▶ ┌─────────────┐  分頁在背景／畫布離開可視範圍
   │    │   running   ├──────────────────────────▶ paused ──(恢復可見)──┐
   │    └──────┬──────┘                                                  │
   │           │ webglcontextlost                                        │
   │           ▼                                                         │
   │    ┌─────────────┐  webglcontextrestored：重新 compile → link →     │
   │    │    lost     ├──────────────────────────  建緩衝區 → 取 uniform ─┘
   │    └─────────────┘          位置，再重啟迴圈
   └─────────────────────────────────────────────────────────────────────
   prefers-reduced-motion: reduce → static（只畫一幀，不跑迴圈）；dispose() → disposed
```

1. **取得 context 與降級**：`getContext('webgl')` 取不到時，隱藏 canvas、露出容器的 CSS 漸層，狀態標為 `nowebgl`；不要留下空白畫布，也不要在畫面上寫「執行中」。
2. **編譯與連結錯誤回報**：對每個 shader 檢查 `COMPILE_STATUS`，對 program 檢查 `LINK_STATUS`，失敗時取 `getShaderInfoLog`／`getProgramInfoLog`，用 `console.error` 輸出並顯示在畫面狀態上，同時釋放已建立的半成品。
3. **Resize 與 DPR**：畫布像素尺寸 = CSS 尺寸 × `min(devicePixelRatio, 2.0)`，並同步 `gl.viewport`。`2.0` 是本 repo 的取捨，不是外部標準。
4. **渲染迴圈**：由一個 `sync()` 函式依「是否已釋放、是否 context 遺失、是否出錯、是否 reduced-motion、分頁是否可見、是否在可視範圍」決定要不要跑 `requestAnimationFrame`，並把原因寫進狀態。游標平滑用 `1 - exp(-dt/τ)`，與影格率無關。
5. **離屏與背景節流**：`IntersectionObserver` 與 `visibilitychange`（W3C Page Visibility）。
6. **Context 遺失與恢復**：依 Khronos WebGL 規範，`webglcontextlost` 必須呼叫 `event.preventDefault()` 才會收到 `webglcontextrestored`；恢復後 context 遺失前建立的 WebGL 資源（紋理、緩衝區、program 等）都已失效。所以：
   - 遺失時**只丟掉參考，不要對失效物件呼叫 `delete*`**（會產生 `INVALID_OPERATION: delete: object does not belong to this context`）；
   - 恢復時**整條管線重建**，只重啟動畫迴圈會持續出現 `INVALID_OPERATION: no valid shader program in use`（上一版範本就是這個問題）。
7. **Dispose**：取消 rAF、斷開兩個 observer、移除 `resize`／`pointermove`／`visibilitychange`／context 兩個事件／媒體查詢的監聽，再 `deleteBuffer`、`deleteShader`×2、`deleteProgram`；重複呼叫不可出錯。
8. **prefers-reduced-motion**：開頁時為 `reduce` 只畫一幀固定時間點的畫面、不跑迴圈、不隨游標重畫；執行中切換偏好要跟著變（`matchMedia(...).addEventListener('change', …)`）。原作 70 個 bg.js 都有處理此項，是少數與原作一致的地方。
9. **游標互動必須進得了像素**：只在著色器裡算出變數但沒有接到輸出顏色，等於沒有互動（上一版液態金屬模式就是這樣）。本 repo 的做法是讓游標漣漪同時進入高度場，法線由高度場差分而來，所以高光會隨游標改變。
10. **狀態文字不可寫死**：FPS、解析度與生命週期狀態都來自實際執行結果；著色器壞掉時不可顯示「正常執行中」。

可執行的實作在範本的注入腳本與 demo 內；範本附的 `verify_hero.py` 把上述 3～10 項做成可跑的檢查。

---

## 5. 本 repo 提供的模板與它們的限制

| 模板 | 內容 | 與原作的關係 | 限制 |
| :--- | :--- | :--- | :--- |
| A 液態金屬 | 域扭曲 fBM 高度場＋游標漣漪，由高度場差分求法線，Blinn-Phong 高光與近似菲涅爾項 | 概念與 Mercury 相近；程式碼自寫 | 不是光線追蹤，沒有環境反射 |
| B 流體 | 正弦波疊加 fBM，游標周圍有漣漪 | 無對應 | 純色階，沒有物理模擬 |
| C 點狀粒子場 | 片段著色器內每格一顆點，上飄、閃爍，游標附近的點被推開並變亮 | README 沒有粒子家族 | **不是 `GL_POINTS` 粒子系統**；點被限制在自己的格子內 |
| D 字元密度風 | 亮度場量化成 6 級，每級對應 `空白 . : + # @` 的手繪形狀 | 概念與 Orbit ASCII／Vapor 相近 | **不是字型文字**，沒有字型圖集，也不需要圖檔 |

沒有提供：3D Raymarching 場景、需要圖檔／深度圖的模板、GSAP＋Lenis 捲動體驗。需要這些時請使用原作並遵守其授權（第 0 節）。

fBM 與 domain warping 是通用技法，可參考 The Book of Shaders 第 13 章；fBM 定義為多個倍頻的雜訊相加，每過一個倍頻頻率乘 2、振幅乘 0.5：

```text
fBM(p) = Σ_{i=0..n-1}  a^i · noise(2^i · p)      本 repo 的實作：n = 4、a = 0.5，每層再旋轉座標
```

---

## 6. AI Agent 呼叫規格

### 6.1 DOM 三層結構

```text
  <header>        容器：CSS 漸層底色（canvas 被隱藏時露出的降級畫面）
    ├─ <canvas>   底層：WebGL，aria-hidden，不攔截任何互動
    ├─ <div>      中層：暗角與對比保護遮罩，pointer-events: none
    └─ <div>      頂層：標題、說明、CTA；外層 pointer-events: none，只有連結與按鈕設為 auto
```

滑鼠監聽掛在 `window`，所以不會被遮罩或內容層擋住。完整 HTML 在範本的步驟 2。

### 6.2 Prompt 範本（填空即可交給 Agent）

```text
任務：在 <專案路徑/index.html> 的 <body> 開頭加入 Shader Hero 背景。
依據：templates/zero-build-hero-injector-skill.md（若不在這個 repo，請改用我提供的範本檔）。
專案調性：<金融科技／設計工作室／資料平台／開發者工具／其他：____>
指定模板：<A 液態金屬 | B 流體 | C 點狀粒子場 | D 字元密度風>   （不確定就依範本步驟 1 的建議）
文案：kicker=<____>  title=<____>  description=<____>  CTA 文字=<____>  CTA 連結=<____>
品牌色：<#rrggbb，沒有就沿用範本預設>
限制：不得新增 npm 相依與外部腳本；不得刪除既有內容；著色器失敗時要降級成 CSS 漸層。
驗收：執行 verify_hero.py 並貼出完整輸出；結束碼必須是 0。結束碼 2（環境問題）不算通過，要回報原因。
```

### 6.3 Anti-Slop 靜態檢查

在 ai-inbox 內可跑 `python tools/verify_no_slop.py <檔案>` 掃描高擴散陰影、藍紫漸層、裝飾 Emoji 等特徵（規則見 [`anti-ai-slop-frontend.md`](./anti-ai-slop-frontend.md)）。它只存在於本 repo，且只看靜態樣式，**不能**證明背景會動；動態行為以第 7 節的驗證為準。

---

## 7. 驗證方式（可重現）

```bash
python -m unittest discover -s tests          # 全套；沒有 Playwright 時瀏覽器測試會明確 skip
python -m unittest tests.test_shader_hero_demo tests.test_zero_build_hero_injector_template -v
```

| 驗證項目 | 作法 | 對應測試 |
| :--- | :--- | :--- |
| 畫面不是空白、迴圈持續繪製、FPS 是實測值 | 真實 Edge/Chrome，間諜統計 `drawArrays` 次數、`readPixels` 取樣 | `test_shader_hero_demo.py` |
| 游標有效 | 真實 `mouse.move` 兩個位置，凍結 `u_time` 後比對像素；液態金屬與流體兩種模式都測 | 同上 |
| context 恢復 | 按頁面按鈕呼叫 `WEBGL_lose_context`，檢查遺失期間不繪製、恢復後 `linkProgram` 多一次、`gl.isProgram` 為真、畫面與遺失前一致、console 無警告 | 同上；範本以 `verify_hero.py` 驗 |
| Dispose | 間諜統計 `deleteProgram`／`deleteShader`／`deleteBuffer`，並確認之後不再繪製、`pointermove` 不再更新狀態 | 同上 |
| reduced-motion | `reduced_motion='reduce'` 開頁與執行中切換 | 同上 |
| 失敗狀態如實顯示 | 無 WebGL、GLSL 被弄壞時，狀態文字、`role=alert`、CSS 降級、`console.error` | 同上 |
| 測試抓得到壞實作 | 突變測試：把 index.html 與注入腳本刻意改壞（GLSL 打爛、迴圈不啟動、`drawArrays` 停用、游標不進 uniform、刪掉 `contextlost` 監聽、恢復不重建 Program、dispose 不釋放、reduced-motion 被忽略…），同一組 probe 必須報錯，存活者使測試失敗 | 同上 |
| 範本內的程式真的能跑 | 測試從 Markdown 抽出骨架、注入腳本、模板 A～D 與 `verify_hero.py` 組成 HTML，真的跑；壞輸入（GLSL 打爛、佔位字串沒填、著色器不用 `u_mouse`）必須 exit 1 | `test_zero_build_hero_injector_template.py` |

瀏覽器測試需要 `pip install playwright`，以及 Edge、Chrome 或 `python -m playwright install chromium` 安裝的 Chromium；沒有時整個類別 `skipTest` 並寫明原因，不會讓全套變紅，也不會靜默當作通過。畫面標準差、像素差比例等門檻是本 repo 對 320×180 軟體渲染（SwiftShader）畫面的自訂取捨，不是外部標準。

---

## 8. 效能與降級：只寫有依據的部分

上一版寫的 GPU 使用率、編譯耗時、行動端記憶體等門檻數字，沒有來源也沒有量測，已刪除。本 repo 目前**只有軟體渲染（SwiftShader）下的觀測，沒有實體 GPU 的量測**，因此不訂 FPS、GPU 使用率或記憶體的硬門檻。要訂門檻請在目標裝置上量測後寫進該專案，並標明量測條件。

可以直接採用的降級策略（皆為 feature detection，不靠 User-Agent 判斷）：

| 情境 | 做法 | 是否已實測 |
| :--- | :--- | :--- |
| 沒有 WebGL | 隱藏 canvas，露出 CSS 漸層 | 是（無頭瀏覽器強制 `getContext` 回傳 null） |
| 著色器編譯／連結失敗 | 同上，並回報 info log | 是 |
| 偏好減少動態 | 單幀靜態畫面 | 是 |
| 分頁在背景、畫布離開可視範圍 | 暫停迴圈 | 離屏與背景狀態未做自動化實測（邏輯與其他條件同一個 `sync()`） |
| 高 DPR 螢幕 | DPR 上限 2.0（本 repo 取捨） | 上限已寫進程式；測試只在 DPR=1 驗證畫布尺寸，上限本身未測 |
| 行動裝置較弱的 GPU | `mediump` 退回；也可再降低 DPR 上限或迴圈次數 | 未在實體手機驗證 |

原作 README 另提到 `?preview` 參數可得半解析度渲染，這是原作的功能，本 repo 範本沒有實作。

---

## 9. 來源與查證（查證日期 2026-11-02）

已實際開啟並確認內容的：

- 原作 repo `diiviikk5/Hacktemplates` @ `7b019b5`：`README.md`、`LICENSE`、整棵樹（Git Trees API，遞迴 591 筆，`truncated: false`，其中 `templates/` 下 70 個目錄）、70 個 `bg.js` 與 `index.html` 的原始檔、contributors API（1 位，`diiviikk5`）、`users/diiviikk5` 公開資料；`abyss`、`mercury` 兩個模板以 `file://` 與 `http://` 實際載入比較。
- [WebGL 1.0 規範（Khronos）](https://registry.khronos.org/webgl/specs/latest/1.0/)：`webglcontextlost` 需 `preventDefault()` 才送 `webglcontextrestored`；恢復後遺失前建立的資源失效。
- [WEBGL_lose_context 擴充（Khronos）](https://registry.khronos.org/webgl/extensions/WEBGL_lose_context/)：`loseContext()`／`restoreContext()` 模擬遺失與恢復。
- [Media Queries Level 5（W3C）](https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-motion)、[MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)。
- [Intersection Observer（W3C）](https://www.w3.org/TR/intersection-observer/)、[Page Visibility Level 2（W3C）](https://www.w3.org/TR/page-visibility-2/)。
- [The Book of Shaders 第 13 章（Fractal Brownian Motion）](https://thebookofshaders.com/13/)。

**未驗證或已移除**：

- Threads 貼文與 X（@Menace_thakur）頁面：本次未重新開啟，筆記裡關於貼文的敘述不在本文範圍。
- `https://dvklab.vercel.app`：404，無法確認任何線上展示內容。
- iquilezles.org（SDF 與 domain warping 文章）：同日整站回傳 404，上一版的引用已刪除，不再作為來源。
- Stefan Gustavson 的 Simplex Noise PDF：審查時連不上，本文不使用。
- 上一版規範的「首屏佔第一印象八成以上」說法、「五大分類」、「16 個代表作品」、GPU／編譯／記憶體門檻：無來源或與原作不符，已移除。
