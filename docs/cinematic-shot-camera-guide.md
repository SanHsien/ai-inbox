# cinematic-shot 電影級產品發表運鏡規範與視覺提示詞手冊

> 本規範整理自開源專案 [`1weiho/cinematic-shot`](https://github.com/1weiho/cinematic-shot) 之原始規格（來源路徑：`skills/cinematic-shot/SKILL.md`、`references/look.md` 與 `references/shot-list-example.md`）。  
> 交付形式：以 `ai-inbox` 範本手冊（`docs/cinematic-shot-camera-guide.md`）交付，供影視生成專案、AI 提示詞編寫及程式化動畫（CSS 3D / Remotion）復用。

---

## 1. 核心電影級美學與運鏡原則

`cinematic-shot` 將軟體介面視同高級實體工業產品（如黑石平板）進行電影級攝影調度，捨棄呆板的等比例縮放或冗長字幕解說，依靠介面自身的有機互動與光影運鏡營造高級感：

1. **舞台與背景（Stage & Void）**：
   - **Dark Void**（深色產品）：置於深黑虛空中（`#000000`），產品本體為懸浮平板，四周被柔和衰減的光線與真實邊緣高光包裹。
   - **High-Key Studio**（淺色產品）：置於潔淨高調攝影棚，低對比度漫射柔光。
2. **極淺光學景深（Optical Depth of Field & Razor-thin Focal Plane）**：
   - 焦平面極薄（僅保留 1~2 行文字或核心互動元件銳利），前景與背景自然融化為柔和光斑（Bokeh）。
3. **有機動態微漂移（Motivated Camera Drift）**：
   - 攝影機永不靜止，保持每秒 1%~5% 的緩慢位移（Push / Track / Rise），鏡頭方向永遠預判下一個互動熱區。
4. **動作剪接（Cut on Action）**：
   - 剪接點緊扣使用者互動節點（點擊、Enter、按鈕觸發、串流文字展開），長鏡（5~9 秒，展示生成或輸入）與短頓（2~3.5 秒，展示點擊或選擇）交錯呼吸。
5. **介面自敘事（The UI Does the Work）**：
   - 不加任何浮誇箭頭、指針或旁白字幕，靠 UI 自身的打字、串流動畫、狀態躍遷與焦點轉移推進敘事。
6. **確定性時間純函數渲染（Deterministic Frame = f(t)）**：
   - 每幀為時間的純函數，支援精確的多層次物理動態模糊（Motion Blur）。

---

## 2. 五種經典 Shot 規範與參數設定表

以下為標準 52 秒發表片中抽取的 5 種核心鏡頭（Hero, Close-up, Pan/Track, Action Cut, Outro）規格：

| 鏡頭類型 (Shot Type) | 典型時長 (Duration) | 放大倍率 (Magnification) | 攝影機角度 (Pitch / Roll / Yaw) | 攝影機運動 (Camera Drift) | 景深與焦點位置 (Focal Plane & DoF) | UI 行為與動作 (Organic Action) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Hero Shot** (大景/核心亮點) | 6.0 ~ 8.0s | 2.4× ~ 2.8× | Pitch: +32° ~ +36°<br>Roll: -8° ~ -10°<br>Yaw: 0° ~ +4° | 慢速前推進 4% (Push in: 2.8× → 2.9×) | 焦平面鎖定於標題與前三行主要輸出，其餘邊緣柔和散景 | 生成結果逐行揭示 (Stream reveal)，打字游標穩定跳動 |
| **2. Close-up Shot** (極致特寫/細節) | 3.5 ~ 5.0s | 4.0× ~ 6.0× (極限微距) | Pitch: +38° ~ +44°<br>Roll: +12° ~ +16°<br>Yaw: -5° ~ 0° | 沿著字行向右平移 3% (Track right) | 極致極淺景深，僅鎖定 1 個代碼標籤、按鈕或輸入游標 | 標籤切換、Token 高亮、微小狀態徽章亮起 |
| **3. Pan / Track Shot** (橫移/瀏覽運鏡) | 5.0 ~ 7.0s | 3.0× ~ 3.5× | Pitch: +30° ~ +35°<br>Roll: -6° ~ -8°<br>Yaw: +8° ~ +12° | 隨內容滾動方向平行微仰升 (Rise 4% + Track right 5%) | 焦點鎖定在當前讀取焦點列，上方已閱內容與下方未閱內容虛化 | 列表滾動、卡片滑動載入、多欄並排對比 |
| **4. Action Cut Shot** (動作切換/節奏頓點) | 2.0 ~ 3.0s | 3.2× ~ 3.8× | Pitch: +35° ~ +40°<br>Roll: -10° (與上一鏡對角線翻轉)<br>Yaw: 0° | 緊迫輕微推入 2% | 焦點定格在點擊目標（如確認按鈕或快捷鍵氣泡） | 按鈕按下、狀態躍遷（波紋擴散或顏色瞬變），動作瞬間硬切 |
| **5. Outro Shot** (收尾/定格標語) | 4.5 ~ 5.0s | 1.0× ~ 1.2× (全景) 轉純黑背景 | Pitch: 0° (正面平行或微俯 15° 虛化退出)<br>Roll: 0°<br>Yaw: 0° | 前 0.4s 模糊漸暗 (Blur & Dim)，文字與 Logo 靜止定格 | 鏡頭後退虛化，純黑背景上標題由模糊轉銳利（90px），Logo 定格無動態 | 產品名與一行精鍊 Tagline 在同一水平線呈現，最後切換至純白靜態 Logo |

---

## 3. AI 視訊模型提示詞範本 (Visual Prompts)

適用於 Runway Gen-3、Sora、Kling、Haiper 等文字/圖片轉影片模型：

### 3.1 Hero Shot 提示詞範本
```text
Prompt:
Cinematic commercial product film of a sleek dark-mode software interface floating on an oblique slab in a dark void. Steep low camera angle, pitch 34 degrees, slight negative roll. Razor-thin optical depth of field, sharp focus only on the central search input and first streaming code block, foreground and deep background melted into luxurious soft bokeh. Motivated slow camera drift pushing forward by 4%. Subtle top edge rim light illuminating the matte glass slab edge. Pure UI motion: characters typing organically with solid steady caret, streaming output resolving line by line. Zero human hands, no mouse cursor, no floating icons, photorealistic, 4k 60fps, 35mm anamorphic lens feel.

Negative Prompt:
mouse cursor, human hand, 3d cartoon characters, colorful confetti, floating generic icons, flat screenshot, bright white generic background, motion graphics template text, jerky movement, oversaturated colors.
```

### 3.2 Close-up Extreme Macro 提示詞範本
```text
Prompt:
Extreme macro close-up of a dark minimal UI component, 5x magnification. Camera angled at steep 42 degrees oblique tilt, dramatic shallow depth of field where only a single interactive pill badge is tack sharp, surrounding text completely blurred into smooth gaussian bokeh. Slow motivated lateral camera pan from left to right along the baseline. Subtle organic state change: badge glows with delicate internal cyan illumination. Pure tactile industrial design feel, dark void background, high-end tech commercial aesthetic.

Negative Prompt:
hand, finger, pointer, watermark, low resolution, messy blur, chromatic aberration, cartoon style.
```

### 3.3 Outro Shot 提示詞範本
```text
Prompt:
Cinematic outro shot. The floating UI slab gently blurs and dims over 0.5 seconds into a pure deep black void. Crisp minimalist typography un-blurs gracefully at center frame displaying the product name and one concise tagline in elegant clean sans-serif. Followed by a quiet cut to a static minimalist monochrome logo. Total stillness, premium, calm, authoritative ending.
```

---

## 4. 程式化實作運鏡參數換算 (CSS 3D / Remotion)

在基於代碼的渲染管道（如 Remotion 或 CSS 3D 視角）中，視角換算基準如下：

- **透視深度 (Perspective $P$)**：通常設為 `P = 1300px`（一般鏡頭）至 `2000px`（全景鏡頭）。
- **放大倍率與焦距關係**：
  $$\text{Magnification} \approx \frac{P}{\text{dist}}$$
  - $6\times \implies \text{dist} \approx 217\text{px}$
  - $4\times \implies \text{dist} \approx 325\text{px}$
  - $3\times \implies \text{dist} \approx 433\text{px}$
  - $2\times \implies \text{dist} \approx 650\text{px}$
  - $1\times \implies \text{dist} \approx 1300\text{px}$
- **相機推移 (Push in)**：從 $2.8\times$ 推至 $2.9\times$ 對應 `dist` 由 $464\text{px}$ 縮短至 $448\text{px}$。
- **對角線翻轉 (Diagonal Cut)**：每個硬切鏡頭之間交替反轉 Roll（例如 Shot 1 為 $-8^\circ$，Shot 2 翻轉為 $+12^\circ$），使連續特寫畫面具備清晰的視角切換動態，避免視覺疲勞。

---

## 5. 靜態發表照與社群卡（Stills）規範

針對 Twitter/X、GitHub Hero 或 Open Graph 社群卡，靜態相機與動態鏡頭不同，每張靜圖必須為該幀獨立調度：

1. **鏡頭長度**：採用較長焦段（Perspective 約為畫布寬度的 $2.0 \sim 2.2\times$），避免邊緣拉伸畸變。
2. **完整物件在框內**：至少露出面板的一個真實邊緣、圓角與投射陰影，讓介面呈現具體的物理平板質感。
3. **定格瞬間（Frozen Moment）**：切勿截取完全靜止的 UI，必須捕捉「正在生成的中途」、「剛選取的藥丸標籤」、「輸入到三分之二的提示詞」，維持生命力。
4. **社群卡（1200 × 630）**：UI 佔左半部傾斜散景，右半部留白區域放置產品名與簡約文字標語，嚴禁字體壓在 UI 之上。
