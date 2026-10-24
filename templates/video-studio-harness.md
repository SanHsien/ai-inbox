# Code-as-Video Studio 影視工作室規範（CLAUDE.md / SKILL.md 範本）

> **規範定位**：本範本沉澱自 `0xalpha.ai` 的「Focus on Harness, Not Prompt」方法論，並深度集成 `cinematic-shot`（宏觀運鏡）、`motion-prompt`（微觀動態字典）、`Cinetic`（音畫節奏網格）、`BeatDesign`（代碼驅動時間線）與 `Remotion`（確定性渲染）。本規範旨在將隨機黑箱的 Prompt 抽卡，升級為可預測、可定位（Scrubbable）、具備工業級美學的確定性代碼視訊管線。

---

## 1. 核心哲學：影片是時間的函式 (`V = f(t)`)

在代碼影視工作室中，影片不是一連串隨機幀的模糊拼接，而是一個純粹的時間數學函式：

$$Frame = f(t, state)$$

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                    Code-as-Video seek(t) 確定性渲染架構                       │
├───────────────────────────────────────────────────────────────────────────────┤
│ 時間軸 (Time Domain: t ∈ [0, Duration])                                        │
│    │                                                                          │
│    ├── t = 0.0s ──▶ 初始靜止狀態 (Initial State)                              │
│    ├── t = 1.2s ──▶ 相機 Dolly In ＋ 彈簧插值 (Spring Physics: 85% progress)  │
│    ├── t = 2.4s ──▶ 節奏拍點 (Beat Drop) 觸發文字 Kinetic Reveal             │
│    └── t = 5.0s ──▶ 畫面收束與 Logo 定格                                      │
│                                                                               │
│ 隨機跳轉與確定性 (Scrubbable & Deterministic):                                │
│    seek(t) 能在不依賴前一幀快取的前提下，精確計算出任意毫秒畫面的幾何位置、   │
│    透明度、相機視野 (FOV) 與光影狀態，保證每次重新渲染像素級完全一致。       │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 嚴格反 AI 視覺套路清單（Anti-AI Slop Rules）

所有由 Agent 生成之代碼與視訊畫面，**嚴格禁止**出現以下四大 AI 罐頭視覺套路（違反者門禁直接打回）：

| 禁令類型 | 罐頭視覺特徵 | 拒絕理由 | 正確替代方案 |
| :--- | :--- | :--- | :--- |
| **禁令 1：漸層置中標題** | 紫藍/粉紫大漸層背景，正中央巨大粗體字懸浮 | 廉價、缺乏品牌性格、典型的文字填充模板 | 非對稱排版（Asymmetric Layout）、真實 UI 投影、高對比實色背景、幾何網格與材質背景 |
| **禁令 2：全員無腦淡入** | 頁面上所有元素以相同的 0.3s `opacity: 0 -> 1` 浮現 | 視覺無主次、拖沓、催眠感強 | 物理彈簧（Spring Physics）、層疊瀑布（Staggered Cascade）、動量驅動的位移推進 |
| **禁令 3：角落小標與無效徽章** | 四角放 meaningless tags、裝飾性「AI Powered」發光框 | 視線干擾、資訊密度虛胖 | 移除多餘裝飾，留白（Negative Space），僅保留產品核心指標與真實操作介面 |
| **禁令 4：無節奏均速飄移** | 相機鏡頭永遠以恆定速度緩慢左右飄，沒有焦點切換 | 失去影視張力與節拍節奏感 | 結合 BPM 網格的定點聚焦（Snapping）、快進停頓（Snap & Hold）、衝擊力運鏡 |

---

## 3. 整合視覺與影視體系（已併入任務精華）

### 3.1 宏觀運鏡語法庫（抽取自 `cinematic-shot`，原 T-20261017-18）
在代碼層級，鏡頭運鏡透過相機三維坐標 $(X, Y, Z)$、視野（FOV）與旋轉角度矩陣控制：
- **Hero Close-up（焦點特寫）**：相機貼近產品核心互動區域（如一鍵轉換按鈕、輸入框），景深虛化背景。
- **Feature Pan（水平橫搖）**：相機從左側側邊欄順滑橫搖至主數據儀表板，搭配物理慣性阻尼。
- **Isometric Orbit（等角環繞）**：保持 30° 俯角，對產品 3D 卡片視角進行 45° 慢速軌道環繞。
- **Macro Dolly Zoom（滑軌推拉／眩暈效果）**：鏡頭向前推進的同時放大 FOV，背景急速擴張而主體尺寸不變，用於強調關鍵特性登場。

### 3.2 微觀動態字典（抽取自 `motion-prompt`，原 T-20261018-02）
- **Staggered Cascade（階梯瀑布動效）**：列表或卡片元素以 40ms~60ms 的間隔依序登場，禁止同步出現。
- **Spring Physics（真實物理彈簧）**：
  $$\text{stiffness} = 220, \quad \text{damping} = 20, \quad \text{mass} = 1$$
  拒絕生硬的線性 `linear` 與機械式 `ease-in-out`。
- **Kinetic Typography（動能文字編排）**：關鍵動詞伴隨剪影翻轉、縮放與遮罩揭示，字距隨時間微幅收攏。

### 3.3 代碼時間線流水線規格（抽取自 `BeatDesign` + `Cinetic`，原 T-20261020-04）
將時間線標準化為結構化 Timeline JSON，支援多軌並行：
```json
{
  "project": "Code-as-Video Studio",
  "fps": 60,
  "duration_in_frames": 360,
  "bpm": 128,
  "beat_grid": {
    "bar_duration_seconds": 1.875,
    "beat_interval_seconds": 0.46875
  },
  "tracks": [
    {
      "id": "video-track-ui",
      "type": "canvas",
      "clips": [
        { "id": "clip-intro", "start_frame": 0, "duration": 120, "shot": "Hero Close-up" },
        { "id": "clip-feature", "start_frame": 120, "duration": 240, "shot": "Feature Pan" }
      ]
    },
    {
      "id": "audio-track-bgm",
      "type": "audio",
      "clips": [
        { "id": "beat-drop", "start_frame": 60, "src": "assets/bgm-beat.mp3" }
      ]
    },
    {
      "id": "caption-track",
      "type": "text",
      "clips": [
        { "start_frame": 60, "end_frame": 120, "text": "Evidence-First Engineering", "animation": "Kinetic Typography" }
      ]
    }
  ]
}
```

### 3.4 確定性渲染架構（抽取自 Remotion / Canvas Pipeline，原 T-20261018-01）
- **Remotion 原則**：使用 `useCurrentFrame()` 與 `interpolate()` 進行數學插值，嚴禁使用 `setInterval` 或 `requestAnimationFrame` 進行不可控時間步進。
- **HTML Canvas / WebCodecs 原則**：暴露全局 `window.seek(targetTimeInSeconds)` 函式，供外層無頭瀏覽器（Playwright / Puppeteer）逐幀截圖轉碼。

---

## 4. 專案常駐規範範本：`CLAUDE.md`

當建立新的代碼影視專案時，將以下內容寫入專案根目錄之 `CLAUDE.md`：

```markdown
# Video Studio Harness Rules (CLAUDE.md)

## 1. 影視製作物理定律
- **影片是時間的函式**：所有動畫必須由明確的時間變數 `t` (秒) 或 `frame` (影格) 驅動。
- **確定性保證**：禁止在渲染路徑中使用非種子化的 `Math.random()`；相同的 `t` 必須產出完全相同的視覺幀。
- **無依賴跳轉**：`seek(t)` 函式必須能在 16ms 內直接渲染出該時刻畫面，不依賴歷史播放紀錄。

## 2. 嚴格反套路門禁 (Anti-AI Slop)
- 嚴禁漸層背景置中標題。背景一律使用有質感的實色（深灰、純黑、象牙白）或網格/噪點微材質。
- 嚴禁全體元素淡入。使用物理彈簧（Spring）、遮罩裁切（Clip-path reveal）或階梯瀑布登場。
- 嚴禁四角裝飾性標籤與發光無效卡片。

## 3. 真實素材第一 (Real Assets First)
- 製作軟體或網站宣傳影片前，先使用 `python tools/video_asset_capture.py --url <URL>` 抓取真實截圖與 CSS 色系。
- 嚴禁繪製抽象的假假介面（Mock UI）；必須使用真實產品截圖作為紋理。

## 4. 關鍵影格縮圖門禁 (Storyboard Gate)
- 渲染整段影片前，必須先輸出 Contact Sheet（8~12 張關鍵影格縮圖矩陣）。
- 自評每一格（構圖、對比、視覺重量）：低於 8 分的影格必須重修，全部達標才可啟動完整視頻合成。
```

---

## 5. Agent 工具技能範本：`SKILL.md`

將影視工作室封裝為 Agent 可調用之 Skill（例如 `~/.gemini/config/skills/code-as-video/SKILL.md`）：

```markdown
---
name: code-as-video
description: "以確定性代碼（seek(t) 時間函式、Remotion、Playwright 素材捕獲）製作高品質產品發表影片與動效展示"
metadata:
  framework: "Code-as-Video Studio"
  guardrails: ["anti-ai-slop", "seek-t-deterministic", "real-assets-first", "storyboard-gate"]
---

# Code-as-Video Studio 技能指南

當使用者要求「做一個產品影片」、「製作軟體發表展示動效」、「將網站轉為宣傳片」時：

### 階段一：真實素材抓取 (Asset Ingestion)
1. 詢問或解析使用者提供的產品網址。
2. 執行：
   `python tools/video_asset_capture.py --url <target_url> --output-dir assets/`
3. 讀取產出的色彩設定檔 `assets/theme.json` 與高解析度截圖 `assets/screenshot.png`。

### 階段二：時間線與分鏡規劃 (Timeline & Storyboard Planning)
1. 根據產品核心亮點，規劃 15~30 秒的分鏡時間線。
2. 匹配 `cinematic-shot` 運鏡（Hero Close-up -> Feature Pan -> Isometric Orbit）。
3. 對齊 BPM 音樂節拍網格，設定各鏡頭關鍵影格點。

### 階段三：確定性代碼實作 (seek(t) Implementation)
1. 編寫單檔 HTML/Canvas 或 Remotion 組件。
2. 確保實作 `seek(t)` 介面：
   `window.seek = function(t) { /* 根據 t 計算狀態並繪製畫面 */ }`
3. 嚴格檢查 Anti-AI Slop 清單（無漸層置中字、無無腦淡入、無角落小標）。

### 階段四：自審門禁與正式合成 (Gate & Composite)
1. 抽取 8 張關鍵時間點影格拼成 Contact Sheet。
2. 執行自檢打分（1-10 分），剔除低於 8 分鏡頭並微調。
3. 呼叫 ffmpeg 批次截圖合成最終 MP4 視訊。
```

---

## 6. 思考成本動態縮放階梯（Reasoning Effort Scaling）

依據任務難度與產出目標，動態調整模型推理思考深度：

| 等級 (Effort) | 適用場景 | 關注焦點 | 交付耗時預期 |
| :--- | :--- | :--- | :--- |
| **`medium`** | 微調現有鏡頭、調整彈簧物理係數、換字換色 | 精準數值微調、不破壞既有時間線 | < 1 分鐘 |
| **`xhigh`** | 製作新分鏡、整合新產品官網截圖、設計動效轉場 | 結構合理性、Anti-AI 套路審查、BPM 節拍精確對齊 | 3 ~ 5 分鐘 |
| **`max`** | 發表會開場級大片、全片原創時間線架構重構 | 宏觀視覺敘事、深度對抗性自檢、極致影視美學 | 10+ 分鐘 |
