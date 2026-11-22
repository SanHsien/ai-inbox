# Code-as-Video 代碼驅動動態視覺：10 大創意反差與精密科普分鏡規範手冊

> 本文件收錄於 `docs/code-as-video-creative-patterns.md`，為任務 `T-20261120-07` 之產出成果。
> 核心目的：基於 NiceKate AI《迷上 Opus 5.5 做視頻：10 個案例》實戰拆解，將「Code-as-Video（以 HTML5 Canvas、SVG、Three.js、p5.js、CSS Keyframes 或 Remotion 代碼驅動動畫，取代傳統黑箱像素生成模型）」的編劇與工程方法論，提煉為**「高反差電影敘事（High-Contrast Framing）」**與**「精密科普動態（Deterministic Scientific Visualization）」**兩大類結構，並制定可直接供 AI Coding Agent 執行的**五步分鏡規格（5-Step Storyboard Specification）**與 Prompt 模板。

---

## 0. 來源筆記與交叉參照

- **來源筆記**：[`notes/2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md`](../notes/2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md)
- **交叉參照**：
  - [`notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`](../notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md)（Awesome Opus 5.5 Videos 700+ 代碼驅動動態視覺基準庫）
  - [`notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md`](../notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md)（反 AI 罐頭設計與審美防線）
  - [`notes/2026-10-17-tasteskill-v2-anti-slop-frontend.md`](../notes/2026-10-17-tasteskill-v2-anti-slop-frontend.md)（TasteSkill v2 前端動態與視覺規範）
  - [`docs/zero-build-shader-hero-sections-spec.md`](./zero-build-shader-hero-sections-spec.md)（Zero-Build WebGL / Shader 動態渲染規格）

---

## 1. 為什麼選擇 Code-as-Video：與傳統像素擴散模型（Diffusion Video）之本質差異

傳統文生影片（如 Sora、Runway、Kling）直接預測像素機率，在面對「精密機械咬合、物理流體相變、精準文字排版、UI 圖表」時極易出現幾何崩壞與文字亂碼（AI Slop）。**Code-as-Video** 讓大型語言模型（如 Claude Opus 5.5、Gemini 4 Neon）同時擔任**「導演＋物理引擎工程師」**，直接產出確定性的渲染程式碼：

```text
[傳統 Diffusion 文生影片]
Prompt ──► 黑箱潛空間擴散 ──► MP4 像素流
  └── 缺陷：齒輪亂轉、文字扭曲、物理因果錯誤、無法單獨修改第 3 秒的某個參數

[Code-as-Video 代碼驅動視覺管線]
五步分鏡 Prompt ──► LLM 撰寫 HTML5 Canvas / Three.js / SVG / Remotion 代碼
                      │
                      ├── 1. 數學/物理確定性運動 (正弦波、流體靜力學、光波干涉公式)
                      ├── 2. 程式化運鏡與時間軸狀態機 (t = 0s..15s, cubic-bezier)
                      └── 3. 瀏覽器即時渲染 + 100% 精準文字 HUD / 剖面標註
```

| 比較維度 | 傳統像素擴散生成（Diffusion Video） | Code-as-Video（代碼驅動動態視覺） |
| :--- | :--- | :--- |
| **幾何與物理正確性** | 低（常出現違反力學的形變或結構穿模） | **100% 確定性**（由三角函數、碰撞盒、流體與光學公式直接控制） |
| **文字與數據標註（HUD）** | 易產生拼字錯誤或邊緣融化 | **向量級清晰度**（原生 DOM / SVG / Canvas 字型渲染，支援多語系與即時數值跳動） |
| **可編輯與版控能力** | 無法局部微調，只能重抽（Re-roll） | **完全可版控（Git Diff）**：可精準修改某個鏡位的毫秒時間軸、色票或阻尼係數 |
| **最佳適用領域** | 寫實人像表演、自然風景空鏡 | **高反差科技發布會、精密工程／生物／光學科普解說、遊戲化 HUD、程序化工藝美學** |

---

## 2. 10 大經典案例之兩大敘事與視覺範式拆解

將 NiceKate AI 實測的 10 個案例按敘事張力與技術核心，歸納為兩大創作流派：

### 2.1 範式 A：高反差電影／大片敘事（High-Contrast Cinematic Framing，6 案例）

**核心公式**：`極度接地氣的市井／日常／古老物件（Low/Mundane Subject） × 頂級科技發布會／好萊塢諜戰／精密工業紀錄片語法（High/Epic Framing）`

| 案例編號與名稱 | 日常／古典本體（Subject） | 高維度降維包裝框架（Framing） | 核心代碼視覺與動態技法 |
| :--- | :--- | :--- | :--- |
| **案例 1：刺繡版《錦鯉活了》（`00:00`）** | 靜態傳統東方刺繡紋樣 | 活體流體游動與數位工藝展演 | 以程序化線段陣列模擬絲線針腳光澤（Directional Anisotropic Specular），結合脊椎正弦波相位差驅動魚身擺動 |
| **案例 2：三蹦子 ULTRA MAX（`01:33`）** | 農用載貨三輪車（三蹦子） | Apple / 旗艦超跑全球科技發表會 | Three.js 暗調攝影棚聚光燈、金屬車漆環境反射、3D 環繞運鏡、超大無襯線字體切入（`ULTRA MAX / Ti-Alloy Frame`） |
| **案例 3：兵馬俑街舞（`02:45`）** | 秦代剛硬陶土兵馬俑 | 高重拍現代 Breaking / Popping 街舞 MV | 2D/3D 骨骼關節正向／逆向運動學（FK/IK）綁定，以高頻 BPM 節拍器觸發定格震點（Hit）與陶土微塵粒子噴發 |
| **案例 4：碟中蛋（`03:26`）** | 超市挑雞蛋、怕打破的日常採買 | 《不可能的任務》特務拆彈諜戰片 | 手持攝影機呼吸感微晃（Perlin Noise Shake）、高反差明暗對比（Chiaroscuro）、紅外線掃描線與倒數計時 HUD |
| **案例 6：突突突 · Tractor GP（`05:51`）** | 鄉間慢速農用拖拉機 | F1 一級方程式賽車模擬器轉播 | 賽車遙測儀表板（轉速表、G 值圓盤、即時排名 UI）、高頻引擎震動位移、輪胎揚起之粒子塵土系統 |
| **案例 8：搓澡 × 精密工業紀錄片（`08:12`）** | 大眾澡堂搓澡巾去角質 | 半導體晶圓 CMP 化學機械拋光紀錄片 | 微米級（$\mu\text{m}$）表面粗糙度剖面圖、雷射測距網格、冷峻工業藍圖配色與極度嚴肅的工程參數疊加 |

### 2.2 範式 B：精密科普與物理原理動態圖解（Deterministic Sci-Viz，4 案例）

**核心公式**：`肉眼不可見或反直覺的物理／生物現象 × 多層次幾何剖面 + 數學參數即時連動對照`

| 案例編號與名稱 | 科普核心問題 | 關鍵科學／工程機制 | 核心代碼視覺與動態技法 |
| :--- | :--- | :--- | :--- |
| **案例 5：無骨章魚手臂（`04:39`）** | 沒有骨骼支撐，章魚如何精準伸長與彎曲手臂？ | **肌肉流體靜力學（Muscular Hydrostats）**（體積恆定不可壓縮：$V = \pi r^2 L = \text{const}$） | 繪製橫向環肌、縱向肌與斜肌剖面；以代碼強制約束面積守恆——當環肌收縮（半徑 $r \downarrow$）時，長度 $L$ 必然依比例非線性伸展 |
| **案例 7：3D 列印一體成型龍（`06:57`）** | 剛從列印床取下的龍，為何無需組裝就能靈活擺動？ | **一體成型活動鉸鏈（Print-in-Place Articulated Hinge）**與懸空公差間隙（Clearance Gap） | 雙視角同步渲染：左側展示逐層堆疊（Z-axis Layer Slicing）剖面，右側放大標註 `0.3mm ~ 0.5mm` 不沾黏間隙與鏈環扣合自由度 |
| **案例 9：棉花糖形成機制（`09:25`）** | 固體砂糖如何瞬間變成蓬鬆雲朵狀棉花糖？ | **高溫熔融 + 高速離心噴射 + 空氣急冷非晶態固化（Phase Transition）** | 三階段粒子狀態機：中心加熱腔（晶體格點崩解為液態紅粒子）$\rightarrow$ 離心微孔切線拋出（阿基米德螺線軌跡）$\rightarrow$ 接觸冷空氣瞬間拉伸為白色玻璃態細絲 |
| **案例 10：蝴蝶的結構色（`10:38`）** | 閃蝶翅膀沒有藍色色素，耀眼藍光從何而來？ | **奈米鱗片多層膜光波干涉（Structural Coloration & Thin-Film Interference）** | 繪製閃蝶鱗片脊狀奈米樹（Christmas-tree nanostructures）放大剖面；以正弦波模擬入射白光，動態演示紅黃波長相消干涉（Destructive）、藍光波長同相疊加放大（Constructive） |

---

## 3. Code-as-Video 五步分鏡規格（5-Step Storyboard Specification）

為讓 AI Coding Agent 穩定產出高品質、無罐頭感（Anti-Slop）的單檔或組件化動態視覺程式碼，所有 Code-as-Video 請求一律遵循以下**五步分鏡結構**：

```text
Step 1: 場景與時間軸狀態機定義 (Scene & Timeline FSM)
   ▼
Step 2: 核心反差或科普解構公式 (Core Contrast / Scientific Formula)
   ▼
Step 3: 確定性物理與數學運動規則 (Deterministic Math & Physics Rules)
   ▼
Step 4: 程式化鏡頭運動與 HUD 疊加層 (Programmatic Camera & HUD Overlay)
   ▼
Step 5: 渲染引擎與驗收約束標記 (Rendering Engine & DoD Constraints)
```

### 3.1 五步分鏡欄位詳細規格表

| 步驟 | 欄位名稱 | 必填規範與設計要點 | 禁止事項（Anti-Slop 防線） |
| :--- | :--- | :--- | :--- |
| **Step 1** | **場景與時間軸狀態機（Scene & Timeline FSM）** | 明確定義總時長（如 `15s`）與 3～5 個離散分鏡幕次（Act 1..N），每幕標明精確起訖秒數（`t ∈ [0.0, 3.5]`）、主視覺構圖與背景色調 | 禁止只寫「做一個好看的動畫」而無明確時間軸分段（無分段會導致所有元素從頭到尾原地單調循環） |
| **Step 2** | **核心反差／科普公式（Contrast / Sci Formula）** | - **創意敘事類**：明寫「低維本體 × 高維包裝」的詞彙映射表（如：搓澡巾 $\rightarrow$ 纖維陣列研磨頭；泥垢 $\rightarrow$ 表層氧化微粒）。<br>- **科普解說類**：明寫待證明的物理不變量與宏觀／微觀雙視窗對照關係 | 禁止使用空洞形容詞（如「超酷炫、科技感滿滿」）；必須給出具體的領域術語與視覺隱喻對照 |
| **Step 3** | **物理與數學運動規則（Math & Physics Rules）** | 指定驅動畫面元素的具體數學函數：如簡諧運動 $\theta(t) = A \sin(\omega t + \phi)$、彈簧阻尼（Spring Physics）、體積守恆公式 $r^2 L = C$、光程差干涉 $\Delta = 2nd\cos\theta$ 或 Perlin Noise | 禁止使用生硬的等速線性移動（`linear`）；所有轉場與機構運動必須具備加速度曲線或物理守恆連動 |
| **Step 4** | **鏡頭運動與 HUD 圖層（Camera & HUD Layer）** | 定義程式化攝影機動作（如：`Zoom(1.0 -> 4.5x)` 聚焦微觀剖面、`Orbit(0° -> 120°)`、`CameraShake`）以及同步跳動的工程遙測 HUD（比例尺、即時參數讀數、剖面引線標註） | 禁止固定死板視角到底；文字標註必須與動畫幾何座標動態綁定（Leader Lines 跟隨目標點移動），不可遮擋主體 |
| **Step 5** | **渲染引擎與執行約束（Engine & Constraints）** | 指定目標技術棧（如：`Single-file HTML5 Canvas + SVG HUD`、`Three.js WebGL` 或 `Remotion React`）、畫布比例（`16:9` 或 `9:16`）、幀率（`60 FPS requestAnimationFrame`）及播放控制列（Play/Pause/Scrub 時間軸滑桿） | 禁止依賴外部失效圖片 URL 或未打包字型；所有幾何圖形與紋理一律由程式碼程序化生成（Procedural Generation） |

---

## 4. 可直接執行的 Code-as-Video 雙流派分鏡 Prompt 模板

### 4.1 模板一：高反差大片／精密紀錄片敘事（High-Contrast Framing Template）

```markdown
# Role: Code-as-Video 導演與程序化視覺工程師

請使用單檔自包含 HTML5（Canvas 2D / WebGL + SVG HUD 圖層，60 FPS，支援時間軸拖曳預覽與播放/暫停控制），為我製作一段 16 秒的「高反差精密紀錄片／旗艦發表會」動態視覺作品：

## 1. 場景與時間軸狀態機 (Timeline FSM: 0s ~ 16s)
- **Act 1 [0.0s - 4.0s] 宏觀懸念開場**：暗調聚光燈緩慢亮起，展示【日常物件本體：例如一把傳統竹製掏耳勺 / 農用三輪車 / 澡堂搓澡巾】的線框藍圖（Wireframe Blueprint）與雷射掃描網格。
- **Act 2 [4.0s - 9.0s] 微觀結構拆解（4.5x Zoom-in）**：鏡頭推進至局部結構，展開爆炸圖（Exploded View）與幾何剖面，動態標註材質應力、流體向量或接觸面摩擦係數。
- **Act 3 [9.0s - 13.0s] 極限壓力測試模擬**：啟動高速運動模擬（伴隨粒子流、熱力學色彩漸層與微幅鏡頭震動），右側遙測儀表板即時跳動轉速、G 值與微米級公差曲線。
- **Act 4 [13.0s - 16.0s] 旗艦定格宣言**：鏡頭拉回全貌，浮現高對比巨幅無襯線產品稱號與反諷規格數據表。

## 2. 核心反差映射公式 (High-Contrast Mapping)
- **日常本體**：【填入日常事物，如：街邊烤地瓜爐】
- **高維包裝框架**：【填入高維框架，如：托卡馬克核融合熱對流反應爐】
- **術語映射表**：
  - 炭火熱流 ──► `Plasma Convection Thermal Field (520 K)`
  - 翻面鐵夾 ──► `Dual-Axis Robotic Manipulator`
  - 糖蜜焦化滲出 ──► `Caramelization Phase-Transition Index: 98.4%`

## 3. 確定性數學與物理規則 (Deterministic Physics)
- 使用 `requestAnimationFrame` 搭配精確秒數變數 `t`（支援滑桿任意跳轉 `seek(t)`）。
- 熱流或粒子運動須採用極座標螺旋與正弦擾動公式；機械轉動與鏡頭縮放須採用 `easeInOutCubic` 或彈簧阻尼曲線，嚴禁生硬線性移動。

## 4. 程式化運鏡與 HUD 疊加層 (Programmatic Camera & HUD)
- 實作虛擬攝影機矩陣 `Camera(x, y, zoom, shake)`，隨 Act 1~4 自動平滑插值切換宏觀與微觀視角。
- HUD 圖層需包含：動態跟隨目標幾何頂點的引線標註（Leader Lines）、即時正弦波／頻譜小圖表、右上角時間碼 `TC 00:00:XX:FF` 與比例尺（如 `Scale: 100 μm`）。

## 5. 渲染引擎與交付約束 (Engine & DoD)
- 輸出單一完整可執行的 `.html` 檔案，零外部圖片相依（所有物件、網格、粒子與光影皆以 Canvas/SVG 程序化繪製）。
- 底部附帶簡潔深色控制列：播放／暫停按鈕、Act 1~4 快捷跳轉鈕、時間軸 Scrub 滑桿。
```

### 4.2 模板二：精密科普與物理／工程原理解構（Deterministic Sci-Viz Template）

```markdown
# Role: 確定性科學視覺化與物理模擬工程師 (Deterministic Sci-Viz Engineer)

請使用單檔自包含 HTML5 Canvas + SVG，製作一段 18 秒、具備雙視窗同步對照與互動參數滑桿的精密科普動態圖解：

## 1. 場景與時間軸狀態機 (Timeline FSM: 0s ~ 18s)
- **Act 1 [0.0s - 4.0s] 直覺提問與宏觀現象**：展示宏觀現象（如：蝴蝶翅膀在陽光下變換藍紫色彩 / 3D 列印鉸鏈直接彎曲 / 章魚手臂無骨伸長），提出核心物理問題。
- **Act 2 [4.0s - 10.0s] 剖面放大與幾何機制**：畫面分割為「左：宏觀動作」與「右：奈米／毫米級幾何剖面放大圖」，以動態向量箭頭與幾何約束展示底層結構。
- **Act 3 [10.0s - 15.0s] 關鍵參數極端對照（Counterfactual Comparison）**：同屏上下並列「正常物理參數（如：0.4mm 公差間隙 / 同相波長干涉）」與「失效對照組（如：0.05mm 沾黏鎖死 / 反相相消干涉）」，讓因果關係一目了然。
- **Act 4 [15.0s - 18.0s] 定律總結與互動沙盒**：定格核心數學公式，並開放底部參數滑桿供使用者手動調整變數驗證。

## 2. 核心科學不變量與公式 (Scientific Invariants)
- **主題現象**：【填入科普主題，如：奈米結構色薄膜干涉 / 肌肉流體靜力學體積守恆】
- **程式碼強制守恆公式**：
  - 畫面中的幾何形變或波幅疊加**必須由真實數學公式即時算出**（例如：合成波振幅 $Y(x,t) = y_1(x,t) + y_2(x,t, \Delta\phi)$，或不可壓縮圓柱體積 $r(t)^2 \cdot L(t) = V_0$），嚴禁寫死假動畫。

## 3. 鏡頭運動與雙視窗連動標註 (Split-Screen & Dynamic Callouts)
- 宏觀視窗中的放大取樣框（Magnifier Box）位置需與微觀剖面視窗透過動態引線相連。
- 即時顯示當前物理量數值（如：波長 $\lambda = 450\text{ nm}$、相位差 $\Delta\phi$、間隙寬度 $d = 0.35\text{ mm}$）。

## 4. 渲染引擎與交付約束 (Engine & DoD)
- 採用高對比深色科研儀表板配色（深藍黑底 `#0B0F19`、青色幾何線 `#38BDF8`、琥珀色警示／強調線 `#F59E0B`、翠綠色合成結果 `#10B981`）。
- 底部提供時間軸進度條、Act 1~4 分鏡切換鈕，以及 1~2 個即時物理參數控制滑桿（如：改變入射角或間隙大小）。
```
