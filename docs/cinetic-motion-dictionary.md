# Cinetic 動態技法手冊 (Cinetic Motion Dictionary)

本手冊深入解構開源專案 [`Leonxlnx/cinetic`](https://github.com/Leonxlnx/cinetic)，提煉其專為 Coding Agent 設計的 **Motion Director（動態導演）** 代碼驅動影片（Code-as-Video）技法體系。

---

## 1. 技法庫概況與真實性審查報告

- **來源檔案**：`skills/cinetic/assets/library/techniques.json`
- **架構版本**：Version 1
- **資料審查結論**：
  - 筆記原記載「14 大分類、273 種技法」經實體檔案解析完全屬實，**無任何增減或空泛拼湊**。
  - 技法分為三大角色職責：
    - **Workhorse (主力)**：承載全片基礎視覺骨架，可重複循環出現。
    - **Accent (點綴)**：關鍵拍點的強化動作，為單一鏡頭增添層次。
    - **Signature (標誌英雄動態)**：單部短片僅允許出現 1~2 次的高光動作，用於產品靈魂展現。

### 14 大分類統計清冊

| 序號 | 類別代碼 (Key) | 中文分類名稱 | 技法數量 | 核心職責 |
| :---: | :--- | :--- | :---: | :--- |
| 1 | `opening_hook` | 開場視覺鉤子 (Opening Hooks) | **10** 種 | A strong opener shows its first visible change by ... |
| 2 | `transition` | 轉場切換 (Transitions) | **22** 種 | A transition is a designed handoff, not a cut betw... |
| 3 | `camera` | 虛擬運鏡與相機 (Camera Moves) | **22** 種 | The camera is one transform on one world container... |
| 4 | `typography_motion` | 動態文字排版 (Typography in Motion) | **25** 種 | Measured type arrives on expo-out moves that cover... |
| 5 | `ui_choreography` | 介面佈局編舞 (UI Choreography) | **19** 種 | UI choreography is layout logic in motion: every r... |
| 6 | `data_and_numbers` | 數據與計數動態 (Data & Numbers) | **17** 種 | Numbers are proof, so they must read at a glance a... |
| 7 | `product_demo` | 產品演示與場景 (Product Demo) | **22** 種 | A product shot depends on cause and effect: every ... |
| 8 | `logo_and_end_card` | 品牌與結尾卡片 (Logo & End Card) | **18** 種 | The end card is the film's poster. The lockup appe... |
| 9 | `color_and_light` | 色彩與光影節奏 (Color & Light) | **25** 種 | Colour carries meaning, so ration it. Keep one acc... |
| 10 | `texture_and_finish` | 質感後製與幀率 (Texture & Finish) | **20** 種 | Texture and finish decide whether a film built fro... |
| 11 | `layout_and_composition` | 版面與動態構圖 (Layout & Composition) | **16** 種 | In motion, layout means two things: where the eye ... |
| 12 | `pacing_structure` | 速度曲線與結構 (Pacing & Structure) | **23** 種 | Pacing is the shape of speed over time, and the st... |
| 13 | `micro_interaction` | 微互動與點擊響應 (Micro-interactions) | **20** 種 | A micro-interaction is the visible cause of a cut.... |
| 14 | `depth_and_3d` | 景深與空間 3D (Depth & 3D) | **14** 種 | Depth looks expensive only when it is physical and... |

> 總計：**14 大分類、273 種動態技法**。

---

## 2. 60 FPS 貝茲時間配方與彈簧物理字典

- **來源路徑**：`skills/cinetic/references/motion-tokens.md` 與 `skills/cinetic/references/timing-grid.md`
- **標準基準**：以 60 FPS 渲染幀率與 Remotion / GSAP 為度量標準。

### 2.1 貝茲時間曲線字典 (Easing Tokens - `E`)

在 Remotion 代碼中對應 `src/lib/anim.ts` 的 `E.<token>`，底層封裝 `Easing.bezier(x1, y1, x2, y2)`：

| Token | Bezier 參數 | 25% / 50% 達成度 | 速度峰值 (Peak) | 最佳適用場景 | 絕對禁用情境 |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `out` | `0.16, 1, 0.3, 1` | 83% / 97% | 起始幀即達峰值 | 元素抵達 (Arrivals)、單詞入場 | 淡出 (Fade-outs)、離場 |
| `outSoft` | `0.22, 1, 0.36, 1` | 77% / 96% | 起始幀 | 柔和定格、次要元件入場 | 英雄衝擊動效 (Hero impacts) |
| `in` | `0.7, 0, 0.84, 0` | 0% / 3% | 結束幀 | 元素崩解塌陷、硬切收縮離場 | 簡短淡出 (短於 1 幀會直接消失) |
| `exit` | `0.55, 0.055, 0.675, 0.19` | 4% / 15% | 結束幀 (2.7x) | 切鏡前的快速離場 (最後 10~24 幀加速) | 元素進場 (Arrivals) |
| `inOut` | `0.87, 0, 0.13, 1` | 4% / 50% | 50% 正中央 (7.7x) | 快速鞭甩 (Whips)、變形滑動 (Morphs) | 慢速位移 (會有突兀跳躍感) |
| `smooth` | `0.65, 0, 0.35, 1` | 7% / 50% | 50% 正中央 (2.9x) | 漸層淡化、漂浮、微呼吸 (Breath) | 元素進場 (啟動太遲緩) |
| `ui` | `0.4, 0, 0.2, 1` | 24% / 78% | 30% 處 | UI 元件微調 (Toggle, Chip, List Row) | 鏡頭運鏡 (Camera) |
| `cam` | `0.48, 0.1, 0, 0.9` | 28% / 83% | 27% 處 | 鏡頭推進 (Camera pushes): 緩起步長沉澱 | 一般 UI 元件位移 |
| `glide` | `0.47, 0.2, 0.15, 1` | 27% / 82% | 31% 處 | 150~350px 範圍元件柔和滑行著陸 | 長距離跨屏位移 |
| `rest` | `0.45, 0, 0.1, 1` | 23% / 82% | 29% 處 | 必須精確靜止收斂的動作、連鎖位移 | 衝擊型動效 (Impacts) |
| `contact` | `0.55, 0, 0.9, 0.55` | 4% / 17% | 結束幀 (4.5x) | 物件碰撞接觸前夕的高速衝刺 | 平滑定格 |

### 2.2 物理彈簧預設字典 (Spring Presets - `SPR`)

基於真實物理模擬，Remotion 中呼叫 `spring({frame, fps, config: {damping, stiffness, mass, overshootClamping}})`：

| 預設名稱 | Damping / Stiffness / Mass | 阻尼比 (ζ) | 超調量 (Overshoot) | 沉澱穩定時間 (Settles) | 特性與適用對象 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `snap` | 18 / 260 / 0.7 | 0.67 | 6% | 22 幀 (0.37s) | 輕微超調後鎖定：撞擊卡位、鍵入鎖定 |
| `pop` | 11 / 180 / 0.6 | 0.53 | 14% | 32 幀 (0.53s) | 小型物件彈入插槽（如 Checkmark 徽章） |
| `land` | 14.5 / 200 / 1.0 | 0.51 | 15% | 40 幀 (0.67s) | 真實重力落地反彈（著陸動效專用） |
| `micro` | 30 / 500 / 0.6 | 0.87 | 0.4% | 11 幀 (0.18s) | 極速精準：標籤、開關、微狀態變更 |
| `firm` | 24 / 140 / 1.0 | 1.01 (臨界) | 0% | 38 幀 (0.63s) | 臨界阻尼主力：UI 面板常規進場，無回彈 |
| `soft` | 26 / 120 / 1.0 | 1.19 (過阻尼) | 0% | 41 幀 (0.68s) | 具份量感：大型卡片、對話框、大標題 |
| `heavy` | 30 / 90 / 1.4 | 1.34 | 0% | 56 幀 (0.93s) | 沉重巨大表面：全螢幕背景底襯切換 |
| `calm` | 16 / 64 / 1.0 | 1.0 | 0% | 55 幀 (0.92s) | **文字專用唯一推薦**：單詞、標籤與文字行 |

### 2.3 統一節拍網格同步原理 (Beat Grid Engine)

音畫同步杜絕「畫面播畫面、聲音播聲音」。
```text
每拍幀數 (Frames Per Beat) = (60 FPS * 60 秒) / BPM
例如 120 BPM: 每拍 30 幀；128 BPM: 每拍 28.125 幀
拍點吸附點: Beat 1 (0f) -> Beat 2 (30f) -> Beat 3 (60f) -> Beat 4 (90f)
```
- 轉場切換、衝擊點（Impacts）、相機急停與音效（SFX）必須強制對齊拍點（On-beat）或半拍（Off-beat）。

---

## 3. 14 大分類動態技法字典詳解 (The 273 Techniques)

本章完整收錄 14 大分類共 273 項動態技法。
資料來源：`skills/cinetic/assets/library/techniques.json` 與 `skills/cinetic/references/technique-library.md`。

### 3.1 開場視覺鉤子 (Opening Hooks) — 共 10 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `opening_hook`
- **核心導演準則**：A strong opener shows its first visible change by frame 2-6 at 60 fps, or after one deliberate empty beat of 20-26 f that turns the first event into a hard cut; it never fades up from black or starts on a title card. The hook becomes readable information within about 40-70 f (a metric settled at 41 f, a seven-word line done at about 70 f), then passes its energy on by cutting at peak speed: E.in into the cut, with the next shot starting at that velocity. Brand is either held back (a number or a question first, the mark at most a corner tag until about 60% of the runtime) or shown as the mark alone, already moving; the full lockup is saved for the end. The sound for the first ~2 s stays sparse, about 14 dB under the body with no sub, and the drop lands on the first hard cut: kick on the cut frame, sub 8-12 f before it. Readable type moves at no more than 20 px/f (letters travel faded and resolve as the move slows), edges move at no more than 60-80 px/f with master motion blur above 12 px/f, and every hold stays alive with a 0.3-0.5 px/f drift or a 0.04-0.07 %/f breath.

#### 核心精選技法深入配方

##### `oh-live-grid-cold-open`：Four live cells from frame 2
- **角色 / 能量**：`signature` ｜ `high` 能量
- **60 FPS 時間時序**：First arrivals on f2, f2, f2 and f6 (no cell later than f8). Typical entrances: a type lockup settles in 18 f on E.out, a counter finishes in 28 f. Loop periods 260 / 462 / 244 / 428 f. Something changes somewhere about every 20 f (longest gap about 62 f). Cells 960x540 at 1080p.
- **構建配方 (Recipe)**：Root AbsoluteFill with a CSS grid (grid-template 1fr 1fr / 1fr 1fr, gap 0); every cell is overflow:hidden on the same stage colour (C.ink), so the seams disappear, with its content on the cell's own optical centre at 50-90% of the cell's width. Render each cell's scene at full 1920x1080 inside a wrapper with scale(0.5) and transformOrigin '0 0', so type keeps its native sizing and a cell can later go full-frame sharp. Wrap each cell's composition in Remotion <Loop durationInFrames={P}> with mutually awkward periods so the four never repeat in sync, and start each cell's first arrival by frame 2-6 on its own E.out curve with no shared global ease: for example a line converging with SPR.word, a Roll counter driven by countSteps(..., E.out), and an orbit whose angular speed decays as w = 11.25*e^(-t/10) + 2 deg/f, with satellites spawning on f10, f18 and f28. Only the one story element in each cell (pin, payoff word, button) gets C.accent; everything else stays greyscale. Merge every cell's cut frames into one list and nudge apart any two that fall within 6 f, and use no per-event SFX: one continuous groove carries the sound.
- **適用時機**：A hero or social loop that must show several features at once, or a launch whose first second has to prove breadth.
- **禁用避開**：The story needs one idea at a time, a single-message sting, or a 9:16 frame where the cells would shrink below about 540 px wide.

##### `oh-macro-scramble-snap-out`：Macro number scramble, one-frame snap-out
- **角色 / 能量**：`signature` ｜ `high` 能量
- **60 FPS 時間時序**：Macro 29 f; snap 1 f at f29; settle 12 f; final string forced from f41 (0.68 s); hold 72 f with only the scale drift. Ticks at about 0.17, 0.23, 0.31, 0.36 and 0.40 s.
- **構建配方 (Recipe)**：Lay out the final figure once with typeStyle('display') (tabular figures, fixed group separator) at a size where the whole string spans about 0.9 W, and draw each digit column as a Roll-style strip whose mask stays 1.6 lines tall during the macro phase, so outgoing digits stack and overflow vertically. Macro phase: scale the wrapper to 1.22 about the frame centre and, on every whole frame (fd), give 1-2 columns a new digit from rand(`${seed}:${fd(frame)}`). Snap: on a single frame decided with fd (so the motion-blur sub-samples agree), cut the scale to 1.0 with no tween, clip the masks to one line and lock the columns left to right 3 f apart until the final string is forced; then hold on breath (scale +0.065%/f) with no glints or sparkles, and keep the brand out until the end lockup. Sound: five dry glitch ticks inside the first 0.6 s, then the bed drops at least 30 dB within one frame on the lock frame and stays silent through the hold; reuse the identical tick cluster under the closing sting as a bookend.
- **適用時機**：The strongest proof is one metric (users, hours saved, uptime) and the film earns attention with the outcome before the brand.
- **禁用避開**：There is no credible or impressive number, or the tone is calm and premium.

##### `oh-mark-build-and-throw`：Mark builds, then is thrown into a macro of itself
- **角色 / 能量**：`accent` ｜ `high` 能量
- **60 FPS 時間時序**：Dot to mark 18 f on E.out (edge about 49 px/f on its first frame); grow 32 f from f8; hold 8 f (f40-48); exit 20 f on E.in (f48-68), cut at f68 (1.13 s); macro pull-back 24 f through zoomHandoff from about 2.2x.
- **構建配方 (Recipe)**：Show the mark only; the wordmark lockup is kept for the end. A 12 px dot at frame centre scales into the 320 px mark over 18 f on E.out, while a wrapper grows 0.83 -> 1 on E.out over 32 f from f8; then hold 8 f. Exit: wrapper scale 1 -> 0.55 over 20 f on E.in, with the hard cut on the exit's last (fastest) frame. The next shot opens on the same mark at the same screen point, its k multiplied by zoomHandoff(t, v0, 24) with v0 = zoomSpeed(kOut, cut - 1) (about -0.168): it starts near 2.2x and slows to 1x with no speed step at the cut, revealing the stage and the first UI as it settles. No overshoot anywhere; the master's motion-blur pass handles the fast frames (incoming edges peak at about 59 px/f).
- **適用時機**：A brand-first logo sting where recognition must land in under half a second and the energy must pour into the next shot.
- **禁用避開**：The mark is unfamiliar and needs a longer hold to be learned, or the film already uses a scale-continuity cut elsewhere. Never use it to show the full lockup.

#### `opening_hook` 完整技法清冊 (10 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `oh-live-grid-cold-open` | Four live cells from frame 2 | signature | high | There is no title. The film opens on a flush 2x2 grid where ... |
| `oh-macro-scramble-snap-out` | Macro number scramble, one-frame snap-out | signature | high | Huge digits fill and overflow the frame, re-rolling every fr... |
| `oh-mark-build-and-throw` | Mark builds, then is thrown into a macro of itself | accent | high | On frame 1 a dot swells into the brand mark. The mark grows ... |
| `oh-quiet-intro-drop` | Sparse intro, drop on the first hard cut | workhorse | any | (Sound and picture.) The first ~2 s carry only light plucks ... |
| `oh-cursor-search-push` | Cursor into a field, two-stage push, typed provocation | accent | medium | A small search pill sits still on a dark stage; a text curso... |
| `oh-oversize-fly-then-small` | Oversize line flies through, restarts small | signature | high | A huge fragment of the headline, about a quarter of frame he... |
| `oh-pile-up-freeze-turn` | Problem pile-up, freeze, turn | workhorse | high | The film opens inside the problem: cards, alerts or rows pil... |
| `oh-result-first-rewind` | Finished result first, then rewind | accent | medium | The film opens on the finished end state at its most impress... |
| `oh-click-starts-film` | A click starts the film | accent | medium | From frame 0 a cursor is already travelling toward the one b... |
| `oh-cropped-word-pull-back` | Cut in mid-sentence, pull back to the line | accent | medium | The film opens inside one giant word, its first letter cropp... |

### 3.2 轉場切換 (Transitions) — 共 22 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `transition`
- **核心導演準則**：A transition is a designed handoff, not a cut between unrelated pictures. Something always crosses the seam: a velocity, a shape held within ±20-30 px of the same screen point, a dot, a line or a stage colour. The default that carries most edits is the velocity handoff. The outgoing move speeds up about ×1.13-1.2 per frame over its last 16-24 f, the cut lands on its fastest frame at 25-40 px/f, and the incoming shot opens at that speed or faster and slows about ×0.92-0.94 per frame to rest in 45-90 f. A scale jump of 1.3-2.5x (8-9x for a frame-filling macro of a related mark) is invisible when the scale velocity matches in log space, about −8% per frame on both sides of the cut. One-take seams (morphs, irises, portals, carets) run 20-90 f and keep every element edge under about 80 px/f, and only flat mask edges may move faster. Polarity flips, where mean luma jumps by 150 or more of 255, are the loudest punctuation: put them on downbeats, once or twice per film. Blending appears only as 1-2 ghost frames at a motion peak, never as a crossfade seam.

#### 核心精選技法深入配方

##### `tr-velocity-handoff-cut`：Velocity handoff cut
- **角色 / 能量**：`workhorse` ｜ `any` 能量
- **60 FPS 時間時序**：Exit: last 16-24 f on E.exit (speed grows about ×1.1-1.2 per frame), ending at 25-40 px/f (never above 60) or −6 to −8% scale per frame. Entry: 30-55 px/f on frame 0, slowing about ×0.92-0.94 per frame (E.out over 45-90 f; entryDistance(40, 60) is about 400 px). A 1-3 px/f drift may run under the hold before the ramp. Text inside a moving shot must be under 20 px/f by the time it has to be read.
- **構建配方 (Recipe)**：Make the cut an act boundary in timeline.ts so motion-blur samples never straddle it, and place it on a beat with b(). In the outgoing act, drive the camera (src/lib/camera.ts) or the hero's translate on E.exit (E.contact, or E.in for a harder snap) over its last 16-24 f, so it ends at peak speed on the final frame; for a zoom, apply the same ramp to k through lmix. In the incoming act, start the key element moving on frame 0 in the same screen direction at 1.0-1.5x that speed and slow it on E.out over 45-90 f. Size the two sides with exitSpeed(D, T, ease) and entryDistance(v, T) from references/transitions.md; for a flicked list, use y = v0·(1 − k^f)/(1 − k) with k = 0.92-0.943 and no overshoot. Give each act one dominant screen vector (+x in one act, −x in the next) and start every incoming element on the side it would enter from.
- **適用時機**：Most cuts between moving shots: feature-to-feature edits, montages, chapter changes, and any film that must never stop. Velocity-matched cuts are exempt from the two-uses-per-type limit.
- **禁用避開**：One side has to be still (a held statement or a designed freeze), or the two shots would move in opposite directions. Carry a shape or an anchor across instead.

##### `tr-scale-through-cut`：Scale-through cut
- **角色 / 能量**：`signature` ｜ `high` 能量
- **60 FPS 時間時序**：Exit: 16-24 f on E.in to 0.70-0.80 (last frame −7 to −9% per frame). Cut on a downbeat. Entry: 1.7-2.0x → 1 over 30-40 f on E.out (first frame −8 to −9%), or an 8-9x macro shrinking toward rest ×0.84 per frame and settled by about 30 f. Anchor drift ≤ 30 px. Push variant: +20-25% over 16-24 f, then 0.8 → 1 over 30 f.
- **構建配方 (Recipe)**：Choose an anchor screen point and keep both objects centred on it within ±30 px (fixed sx, sy in an anchor-camera Shot, or transform-origin on the anchor). Outgoing: k = lmix(1, 0.75, prog(f, T − 20, T, E.in)), so the last frame shrinks about 7.8%; cut on an act boundary. Incoming: the same subject in a new medium (3D render to flat map, device to flat UI, brand card to product world) with k = lmix(1.8, 1, prog(f, 0, 40, E.out)). Its first frame shrinks about 8.4%, so scale velocity is continuous in log space. For a related mark shown as a frame-filling macro, use k = 1 + (S0 − 1)·0.84^f from S0 = 8-9 and snap to 1 once |1 − k| < 0.01. Push version: the hero swells 1 → 1.22 on E.in over the last 16-24 f while the rest of the frame dims (brightness 1 → 0.6 on a dark stage), and the next shot opens at 0.8 and grows to 1 over 30 f on E.out.
- **適用時機**：Changing medium or world while keeping the subject: 3D to flat, device to UI, brand card to product, a mark coming back as a macro. Also hero pull-backs at act changes.
- **禁用避開**：The two objects cannot share a centre point, or both sides are calm; a scale jump without matched scale velocity reads as a jump cut. Use it at most twice per film.

##### `tr-anchor-overlay-cut`：Anchored overlay, background swap
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Background holds of 10-22 f each in a montage (2-3 swaps), or a single swap. Overlay offset across the cut: 0 px ideally, 30 px at most. Overlay drift 0.5-1 px/f. Follow-up move 40 f on E.glide. Cuts on beats or 16ths.
- **構建配方 (Recipe)**：Render the overlay from one absolute-frame function drawn by every act it crosses (deviceAt in references/transitions.md §4.1). Use the identical transform string on both sides of each cut, so its last frame in one act and its first in the next are consecutive samples of one curve. Each background change is an act boundary; a montage is 2-3 background acts in a row behind the same overlay. The overlay keeps its own clock through the cut (a running scale tween, a 0.5-1 px/f drift or a breath() push), so it is never static for more than 48 f. After the last swap the overlay acts on the new world: it travels into its slot on E.glide over 40 f (moves up to 350 px), or FLIPs into an input.
- **適用時機**：Showing that one thing persists across contexts: a location going from 3D city to map, a request going from an empty void to the full app, a claim held over a run of photos.
- **禁用避開**：The overlay is text that must be reread after each swap, or the backgrounds are busy and bright enough to swallow it. Keep backgrounds near 5% mean luma under light overlays.

#### `transition` 完整技法清冊 (22 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `tr-velocity-handoff-cut` | Velocity handoff cut | workhorse | any | The outgoing shot speeds up in one direction and is cut on i... |
| `tr-scale-through-cut` | Scale-through cut | signature | high | An object shrinks faster and faster toward a fixed point, th... |
| `tr-anchor-overlay-cut` | Anchored overlay, background swap | workhorse | medium | A foreground element (a pin, a status pill, a modal, a big w... |
| `tr-polarity-flip-cut` | Polarity flip cut | accent | high | A hard cut flips the stage between near-black and near-white... |
| `tr-shape-match-cut` | Shape match cut | workhorse | medium | The hero shape leaves one shot at a known point and size, an... |
| `tr-giant-word-punch-out` | Giant word punch-out | signature | high | A hard cut lands on an extreme close-up of an oversized word... |
| `tr-dot-relay` | Collapse to a dot relay | signature | medium | The hero collapses into one small dot, or the whole world sh... |
| `tr-defocus-cut` | Defocus cut | accent | medium | The outgoing shot throws itself out of focus in a few frames... |
| `tr-path-relay` | Path relay | workhorse | calm | A line and its lead dot carry the eye from one place to the ... |
| `tr-iris-from-glyph` | Iris from a glyph | accent | high | A small dot appears on a word or icon in the current shot an... |
| `tr-portal-aspect-zoom` | Portal zoom with aspect morph | signature | high | A window opens in the middle of a solid tile. Tile and windo... |
| `tr-band-wipe` | Band wipe | accent | medium | A band crosses a region (snapping up, lingering, then whippi... |
| `tr-horizon-rise` | Horizon rise | accent | medium | A huge disc rises from the bottom edge like a planet horizon... |
| `tr-cover-wipe` | Product surface cover wipe | workhorse | medium | A product surface (a UI panel, a window, a device) moves in ... |
| `tr-subtract-reveal` | Reveal by subtraction | workhorse | medium | The clutter in front of the hero flies off toward the frame ... |
| `tr-conveyor-line-swap` | Conveyor line swap | workhorse | medium | The current line floats up and fades, the stage is empty for... |
| `tr-motion-masked-swap` | Motion-masked swap | workhorse | medium | Content changes on exactly the frame something else moves fa... |
| `tr-tip-back-exit` | Tip-back exit | workhorse | medium | The outgoing scene tips away from camera like a sheet laid o... |
| `tr-envelope-match-type-cut` | Envelope-matched type cut | accent | medium | A big line hard-cuts to a much smaller, longer line whose wo... |
| `tr-drift-matched-angle-cut` | Angle change on a shared drift | workhorse | calm | A hard cut jumps to a new angle or the next state of the sam... |
| `tr-select-retype-swap` | Select and retype swap | accent | calm | A finished headline is selected like text in an editor, the ... |
| `tr-stepped-column-fill` | Stepped column fill | accent | medium | Columns rise from the bottom edge in a stepped pyramid centr... |

### 3.3 虛擬運鏡與相機 (Camera Moves) — 共 22 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `camera`
- **核心導演準則**：The camera is one transform on one world container (src/lib/camera.ts). A shot frames a world point at a screen point at scale k, and lc() blends shots with k in log space, so a zoom keeps an even perceived speed and the subject travels a straight line. What makes camera work feel expensive is the speed profile more than the path. Moves arrive fast and brake (E.out, E.cam), cruise at 3 px/f or less under readable copy, and leave by accelerating over the last 18-24 f into a cut on the fastest frame, ending at 13-47 px/f, and the incoming shot is already moving when it opens. Hero moves are 2-3x pushes over 60-67 f on E.smooth, peaking around 4-5% scale per frame, with the caption starting in the last 25% of the move so the text and the settle land together. No hold is ever dead: a 0.04-0.07%/f creep or a 0.3-1.5 px/f drift runs under every read longer than about 30 f. Keep camera speed under 60-80 px/f at the frame edge, render anything above 12 px/f with the motion-blur pass (--blur), keep roll under 11 deg and give each act one rotation axis.

#### 核心精選技法深入配方

##### `cam-living-hold`：Living hold creep
- **角色 / 能量**：`workhorse` ｜ `calm` 能量
- **60 FPS 時間時序**：Scale creep 0.04-0.07%/f (+2.4 to +4.2%/s), at most 0.1%/f in a 40-60 f tail after a big push. Pulls about -0.08%/f. End card 0.0125%/f. Lateral drift 0.3-0.5 px/f for UI and cards, 1.5-3 px/f for big display type. E.linear once at speed, with a 20 f exponential ease-in from a seam. Released over the next move's own ease.
- **構建配方 (Recipe)**：Set the anchor camera's ax, ay on the focal element so the creep pivots there. Multiply k by breath(prog(f, holdStart, holdEnd, E.linear) * (1 - nextMove), amount), where amount = 0.0005 x the hold length in frames and nextMove is the next move's 0..1 progress, so the next move releases the creep with no velocity step. Push on proof and result shots, pull (negative amount) on busy or chaotic boards, and use a tiny creep on the end card. For type or a single card, drift sideways instead: with g = f - holdStart, sx = sx0 - v * (g - 20 * (1 - Math.exp(-g / 20))), which leaves the seam at zero velocity and reaches v after about 60 f. Keep every layer the camera carries static inside the one transform, so nothing stair-steps on the pixel grid during the creep.
- **適用時機**：Any hold longer than about 30 f: reading a caption, watching a counter, a UI state sitting after an action, the end card.
- **禁用避開**：A designed freeze of at most 15 f on a silence, or a shot where a big camera move or a travelling cursor already supplies the life. Never stack a creep on top of a punch-in drift on the same axis.

##### `cam-breathing-zoom`：Breathing zoom between interactions
- **角色 / 能量**：`workhorse` ｜ `calm` 能量
- **60 FPS 時間時序**：Pull after a reveal: -0.25%/f falling to 0 over 72 f (about -9% total). Push into the next interaction: 0 rising to +0.14%/f over 36 f, about +6% within 60 f of the zero crossing; table and list acts run +0.03 to +0.17%/f (about +6.6% total). Rate keyframes 36-90 f apart, linear. Exhale x0.94 over 60 f on E.out.
- **構建配方 (Recipe)**：Drive only k, from a keyframed zoom rate rather than from poses: rate(i) = interpolate(i, [s0, s0 + 72, s0 + 108, s0 + 168], [-0.0025, 0, 0.0014, 0.0011], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) with linear interpolation, and k = k0 * Math.exp(sum of rate(i) for i = s0..f), computed in a pure loop every frame with no state kept between renders. Put ax, ay on the element the next interaction touches, so the zoom pivots on it and it holds its screen position. Keyframe the rate so it crosses zero rather than resting there: |rate| may stay under 0.0002 for no more than 12 f. Close the act with a short exhale under the final hold: k x lmix(1, 0.94, prog(f, T, T + 60, E.out)).
- **適用時機**：Dashboard, analytics or table acts of 4-10 s with several interactions in one framing, where cutting would cost orientation.
- **禁用避開**：Shots shorter than about 90 f, acts that already move pose to pose with big pushes, or a scrolling feed (a zoom on a moving list reads as wobble).

##### `cam-punch-in-insert`：Punch-in insert on the same render
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Wide holds 20-64 f before an on-axis punch (90-220 f when it establishes the scene). On-axis close-up about 60 f. Macro insert 46-74 f, up to 76-154 f when it carries an action. Scale 2.0-2.5 on-axis, 3-4.5 macro. Drift inside the insert 1-2 px/f linear (3-5 px/f for a 2.5x component slide). Cut on the click, keystroke or beat, with no transition frames. Chain 2-3 punches on consecutive beats for a staccato build.
- **構建配方 (Recipe)**：Lay the product out once and define two Shots on it: WIDE, and INSERT with ax, ay on the control's centre (or the cursor tip), sx, sy at frame centre or on a third, and k = 2.0-2.5 for an on-axis punch or 3-4.5 for a macro insert. Switch on a whole frame, cam = fd(f) >= CUT ? INSERT : WIDE, and keep the cursor path, hover lift, typing and counters on their own clocks so they carry on mid-motion across the cut; place the cursor with toScreen() of the active shot. Never hold the insert still: give it a 1-2 px/f linear drift along the action's direction, or open it with a decaying offset (+8% of frame width, decayed on E.out over 96 f). Build the UI as live layout at its final size, never as an upscaled bitmap, so text stays sharp at k = 4.5, and cut back out on the next action or at the peak of an exit move.
- **適用時機**：Small UI actions that need hero weight (send, picking a date, a chip), long walkthroughs that need their visual scale reset, and a wide/close rhythm that keeps both context and legibility.
- **禁用避開**：The UI doesn't hold up at 3-4.5x, or the close-up isn't obviously the same place (keep the cut on-axis or anchored to the cursor, or it reads as a jump).

#### `camera` 完整技法清冊 (22 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `cam-living-hold` | Living hold creep | workhorse | calm | Under every hold the frame keeps a barely visible push, pull... |
| `cam-breathing-zoom` | Breathing zoom between interactions | workhorse | calm | After a reveal the camera slowly pulls back, coasts through ... |
| `cam-punch-in-insert` | Punch-in insert on the same render | workhorse | medium | A hard cut jumps from the wide view to a 2-2.5x on-axis clos... |
| `cam-detail-first-pullback` | Detail first, then pull back | workhorse | medium | A shot opens tight on the one thing that matters (giant prom... |
| `cam-hero-push-yaw` | Hero push with a 3D turn | signature | high | From a wide view of the whole app, one continuous move pushe... |
| `cam-dolly-surge-foreground` | Dolly surge with a foreground pass | signature | high | The camera surges from a wide shot into a 3x medium close-up... |
| `cam-push-dutch-roll` | Push-in with a roll swing | accent | medium | The camera dives into one corner of the UI, rolls a few degr... |
| `cam-isolating-push` | Isolating push into one item | workhorse | medium | The camera pushes into one row, card or column while everyth... |
| `cam-reframe-to-subject` | Reactive reframe | workhorse | calm | When something new appears (a popover, a result, the hero ic... |
| `cam-pull-lands-event` | Pull-back that lands an event | workhorse | calm | A long, gentle pull-back runs from a close-up to the full vi... |
| `cam-cursor-whip-orbit` | Cursor-led whip orbit | accent | high | Following a cursor that leads the way to the next panel, the... |
| `cam-offframe-whip-relay` | Off-frame whip relay | signature | high | The cursor accelerates up and out of frame, the camera whips... |
| `cam-lead-follow` | Follow the lead dot | workhorse | medium | A small lead (a progress dot, a travelling packet, a drawing... |
| `cam-crane-push` | Crane down with a delayed push | accent | calm | The camera tilts down the page past the chart to the detail ... |
| `cam-crash-zoom-through` | Extrude then crash in | accent | high | An object grows toward camera (a disc extruding into a tall ... |
| `cam-impact-kick` | Directional impact kick | accent | high | On a true impact (a card landing, a lock-in, a slam) the who... |
| `cam-parallax-truck` | Layered parallax truck | workhorse | calm | The camera trucks sideways across a scene split into two or ... |
| `cam-seamless-loop-orbit` | Seamless loop drift | workhorse | calm | In a looping clip the camera drifts along a slow, closed fig... |
| `cam-inside-object-pullout` | Pull out from inside the object | signature | medium | The shot opens on what reads as a full-bleed colour field or... |
| `cam-z-field-flythrough` | Fly-through of a depth field | signature | high | Dozens of flat screens or tokens float at different depths a... |
| `cam-fit-bounds-follow` | Fit-to-content follow | workhorse | calm | As a route, graph or plan builds, the camera widens just eno... |
| `cam-zoom-out-hop` | Zoom-out hop between areas | workhorse | medium | To travel between two distant parts of one product, the came... |

### 3.4 動態文字排版 (Typography in Motion) — 共 25 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `typography_motion`
- **核心導演準則**：Measured type arrives on expo-out moves that cover 30-45% of their travel on the first frame and settle in 12-24 f at 60 fps, staggered 4-10 f per word (20-24 f for a calm one-word-per-beat read). What matters most is the readable moment: a word is either legible from its first frame (40% strength, rising at most 0.6 em at about 14 px/f) or it flies faded and streaked and resolves only once it slows below 20 px/f, and it always lands sharp, with any blur gone by 60% of the move. Colour carries recency: the newest glyph or word arrives in the one accent and relaxes to ink over 12-24 f. Lines never freeze and never jump: layouts are pre-solved or re-centred on a critically damped spring, a landed line tightens 2-3% or drifts 0.3-0.5 px/f, and a hold swells about 6% on an ease-in into the cut. Typing is time-boxed (any length done in about 68 f, half of it visible within 6 f), and the film's one discrete trick (a step edit, a scramble, a letter morph) acts out the copy instead of decorating it.

#### 核心精選技法深入配方

##### `ty-phrase-clamp-junction`：Phrase clamp at a junction
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：Vertical: 18 f E.out, 64 px and 40 px travel (peak 19.7 and 12.3 px/f on frame 1), 2 f word stagger, 1 f pre-pose, opacity 3 f. Snap: 35 px per side over 10 f E.out (about 20 px/f on frame 1) to 0.75 of the gap, back over 18 f E.outSoft. Calm close: 80 f E.outSoft. Hold the locked line at least 54 f with a 0.3 px/f drift.
- **構建配方 (Recipe)**：Fix a junction (x about 48% of the frame, on the shared baseline): the first half is right-aligned to it and the second half left-aligned, both measured with measureTracked so the junction gap is exactly one word space. Vertical default: hold the first half alone for 1 f at +64 px (the pre-pose), then translateY +64 -> 0 on arrive(p), p = prog(f, s, s + 18, E.out), while each word of the second half drops -40 -> 0 the same way, word i starting at s + 2i; give every piece opacity 0 -> 1 over 3 f and blurIn(p, 8), because frame 1 moves about 20 px/f. Horizontal snap: the line cuts in at full strength with each half 35 px out from the junction, closes to 0.75 of the word space over 10 f on E.out, then eases back to the true gap over 18 f on E.outSoft (the one designed undershoot, never closing the space); calm variant: a 1.7x gap closes to 1x over 80 f on E.outSoft. Put the lock on a beat and give it one 1.5% scale punch with hitPulse(t, 1, 4).
- **適用時機**：A two-part claim whose halves mean more together (subject + promise, problem + fix); the payoff line; a junction that a slot roller will reuse.
- **禁用避開**：Lines over 5 words or halves of very unequal length; more than once per film; the end lockup.

##### `ty-slot-roller-fixed-phrase`：Slot roller beside a fixed phrase
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：Step 20 f E.whip (0.18 x pitch frames above a 110 px pitch) every 29-34 f (0.48-0.57 s), 3 steps, then a 28 f hold before the cut. Accelerating run: 26/14/12/8/8/4/4 f (7 items in 76 f), last item on SPR.detent (home in about 9 f), held at least 54 f under a 0.3 px/f line drift. Pitch 1.5x the font size; ticks at least 3 f apart.
- **構建配方 (Recipe)**：The fixed phrase sits in its own layer and never moves; the slot is a column of alternatives aligned to the junction, line pitch 1.5x the font size, translated by -index x pitch and cut by a feathered mask-image (transparent beyond +-1.2 pitch, opaque within +-0.5 pitch) so neighbours show only as slivers. Each step rolls on E.whip over 20 f (peak about 0.18 x pitch per frame, 12 px/f at a 68 px pitch); above a 110 px pitch, stretch the step to 0.18 x pitch frames so the rolling word stays at or under 20 px/f; the row on the junction baseline is ink and every other row is C.mute at no more than 1.3:1 contrast, flipped binary when |rowY - baselineY| < pitch/2 (no colour tween). For a run of 5 or more items, accelerate: intervals 26, 14, 12, 8, 8, 4, 4 f, where intervals under 12 f are whole-frame swaps chosen by fd(f) with no tween, the final item rolls home on SPR.detent, and every step gets a tick. For a loop, make the last item equal the first and wrap the index modulo the list.
- **適用時機**：One sentence frame that fits many subjects or capabilities; listing use-cases without spending screen time; a feature loop that cycles items.
- **禁用避開**：Items of very different widths in a centred layout (the fixed phrase would have to move); more than about 7 items; any mask loose enough that the neighbours read as a list.

##### `ty-masked-baseline-rise`：Masked baseline rise
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Per word 12 f E.out (10-14 f), travel 110% of the line box (about 132 px at 120 px type): 57, 34, 18 px/f on frames 1-3; opacity 3 f; stagger 6 f (4-10); per letter 3 f stagger; letter drop 0.25 em over 8 f, 4 f apart; mask exit 10 f E.in.
- **構建配方 (Recipe)**：Wrap each word in an inline-block with overflow:hidden and padding-bottom 0.15 em (room for descenders); the inner span goes translateY 110% -> 0 on arrive(p), p = prog(f, s_i, s_i + 12, E.out), s_i = start + 6i, with opacity 0 -> 1 linear over the first 3 f, because frame 1 moves about 57 px/f and must be streaked by the blurred master (render.sh --blur). Optional ink resolve: color = mixColor(C.mute, C.ink, prog(f, s_i, s_i + 10, E.linear)). For one short hero word, run it per letter with a 3 f stagger, or drop the letters unmasked from -0.25 em over 8 f, 4 f apart, so a small word falls into place. Exit back into the same mask (translateY 0 -> -110% on depart(q), q on E.in over 10 f) or with ty-reading-order-exit.
- **適用時機**：Editorial headlines and in-UI headings that must land fast (a 3-word line in under 0.5 s) without stealing focus; titles that build while the plane or camera is still moving.
- **禁用避開**：Tight leading where the mask would clip the line above; a calm voice-paced read (use ty-blur-focus-word-rise); per-letter runs on anything but one short hero word.

#### `typography_motion` 完整技法清冊 (25 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `ty-phrase-clamp-junction` | Phrase clamp at a junction | signature | medium | Two halves of a phrase arrive from opposite directions and l... |
| `ty-slot-roller-fixed-phrase` | Slot roller beside a fixed phrase | signature | medium | A fixed phrase holds still while the word in its slot rolls ... |
| `ty-masked-baseline-rise` | Masked baseline rise | workhorse | medium | Each word rises out of an invisible line at its own baseline... |
| `ty-blur-focus-word-rise` | Blur-to-focus word rise | workhorse | calm | Words materialise one per beat out of a soft blur, rising a ... |
| `ty-inplace-light-up-beats` | In-place word light-up on beats | workhorse | calm | The finished line is laid out from the start and its words l... |
| `ty-typeon-timeboxed` | Time-boxed eased type-on | workhorse | medium | Text types in with most of the line appearing in the first f... |
| `ty-recentre-line-build` | Re-centring line build | workhorse | medium | Words or typed glyphs join a centred line one at a time whil... |
| `ty-staggered-word-roll` | Staggered word roll | workhorse | medium | The words of a phrase roll up and away one after another whi... |
| `ty-reading-order-exit` | Reading-order word exit | workhorse | any | Words leave one by one in reading order, each lifting a few ... |
| `ty-kinetic-word-slams` | One-word slam sequence | signature | high | A line is read one huge word at a time: each word hits overs... |
| `ty-multi-direction-assemble` | Multi-direction slam assembly | accent | high | Each word of a short sentence flies in from a different side... |
| `ty-oversize-blur-slide-in` | Oversize word slide-in | signature | high | A huge word arrives streaked from beside the frame and brake... |
| `ty-blur-swap-rescale` | Blur-swap rescale | workhorse | medium | A big word blurs out and instantly re-forms smaller as the s... |
| `ty-step-edit-performs-copy` | Hard-step edits that act out the copy | accent | medium | The headline does what it says with one-frame edits: broken ... |
| `ty-shared-letter-morph` | Shared-letter morph | accent | medium | One word turns into another: the letters both words share st... |
| `ty-scramble-decode` | Scramble decode | accent | medium | A string of random glyphs locks into the real text from left... |
| `ty-front-restyle-sweep` | Travelling front restyles a word | accent | medium | A front sweeps left to right across a settled word and resty... |
| `ty-occlusion-spill-from-mark` | Words spill out from behind a mark | workhorse | medium | A glyph or icon slides aside and the words shoot out from be... |
| `ty-vertical-word-stack` | Vertical word stack | workhorse | medium | In a tall frame each new word lands on its own line under th... |
| `ty-slice-band-assembly` | Slice-band glyph assembly | accent | medium | Each letter builds up from thin horizontal slices that slide... |
| `ty-slice-glitch-streak` | Slice glitch into a speed streak | accent | high | A word jolts into sideways-displaced horizontal slices for t... |
| `ty-scaled-echo-extrusion` | Scaled-echo extrusion | accent | medium | A hero title carries two or three faint copies scaled out be... |
| `ty-swell-on-drop` | Quiet type swells on the drop | signature | high | A word appears small and low-contrast and waits through the ... |
| `ty-centre-out-unmask` | Centre-out line unmask | workhorse | calm | A short line opens from its own centre outward behind a soft... |
| `ty-line-rebreak-glide` | Animated line re-break | workhorse | medium | A centred one-line statement re-breaks into a two-line stack... |

### 3.5 介面佈局編舞 (UI Choreography) — 共 19 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `ui_choreography`
- **核心導演準則**：UI choreography is layout logic in motion: every rect is a function of the frame and the product's state, siblings reflow from computed positions instead of crossfading, and a container is on screen before its contents, which start once their slot is about 60% open. Entrances decay with no overshoot (a 200 px window rise on E.out covers about half its travel in the first 6 f and settles in 50 f) and exits accelerate, handing over to the next panel or the cut on their fastest frame with at most a 4 f gap. Size every move from peak speed = distance x the token's peak slope / frames (E.out 6.2 on its first frame, E.inOut 7.7, E.contact 4.4 on its last, E.whip 3.8, E.rest 3.5, E.glide 3.0, E.smooth 2.9, E.ui 2.7, E.dolly 1.5), so UI text stays at or under 20 px/f and nothing passes about 70 px/f; scale spawns and collapses with lmix so a small surface does not explode on its first frame. Cadence carries meaning: 4-6 f per row reads as data streaming in, 5 f per dealt card as tactile, a 14 f metronome of inserts as abundance, and uneven gaps such as 4, 15 and 18 f as a person deciding. The strongest moves make one motion do two jobs, an incoming panel's edge pushing its neighbour or a hero holding its exact screen position while the world changes around it, so the edit happens inside the product instead of at a cut.

#### 核心精選技法深入配方

##### `ui-orbit-gather-merge`：Orbit gather and merge
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：omega = 13.25*exp(-f/10) + 2 deg/f, radius 95 px at 1080p. Spawns f10/f18/f28, 10 f each (E.out). Merges 16 f each (E.contact), landing f72/f82/f86 at < 60 px/f; hitPulse(t, 2, 5) on the exit node. Exit line f92, 12 f (E.out). About 105 f in all.
- **構建配方 (Recipe)**：Place 4 tokens on a 95 px radius around the source node (above the node, below the exit line) and drive each angle in closed form: theta_i(f) = theta0 + 90*i - (132.5*(1 - exp(-f/10)) + 2*f) deg, a 13 deg/f swing (about 22 px/f of arc) that decays to a 2 deg/f spin within 30 f. Token 0 is there at f0; tokens 1-3 spawn at f10, f18 and f28, each scaling 0 to 1 over 10 f on E.out. Pick theta0 so each token is 90-120 deg short of the exit angle (3 o'clock) when its merge starts; token i then covers that remaining angle forward over 16 f on E.contact, landing at f72, f82 and f86 at under 60 px/f, its scale cutting to 0 on arrival while the exit node takes scale 1 + 0.08*hitPulse(t) and a tick. At f92 a line draws out of the exit point (pathLength 1, strokeDashoffset 1 to 0 over 12 f on E.out) and carries the story to the next diagram.
- **適用時機**：Several inputs, funds or sources gather before one action (pooling, batching, syncing, sending) and the idea should be told by physics with no words.
- **禁用避開**：The tokens are UI cards carrying text (unreadable while orbiting), or the story has no single output point.

##### `ui-path-fracture-fan`：Path fractures into a fan, then re-converges
- **角色 / 能量**：`accent` ｜ `medium` 能量
- **60 FPS 時間時序**：Trunk 12 f (E.linear); dashes at +12 f over 8 f to '24 12'; fan at +26 f: 6 curves x 24 f (E.glide), 2 f stagger, complete at +60 f; punch-in cut at ~+70 f (2.5x). Converge 24 f (E.smooth); camera landing 210 px over 60 f (E.out), 22 px/f at its start.
- **構建配方 (Recipe)**：Draw the trunk from the source node as an SVG path with pathLength 1, strokeDashoffset 1 to 0 on E.linear over 12 f; at +12 f let it degrade by tweening strokeDasharray from 'L 0' to '24 12' over 8 f (dash = mix(L, 24, p), gap = mix(0, 12, p)). At +26 f split it into 6 cubic beziers from one shared point with their ends spread +-200 px in y, each revealed by its own dashoffset on E.glide over 24 f at a 2 f stagger so the drawing head stays under about 70 px/f, and pop a labelled obstacle pill at each end as its curve arrives (opacity step plus scale 0.9 to 1 over 8 f on E.out). Hard-cut to a 2.5x punch-in on the pills about 10 f after the fan completes. To resolve, give each pill a trailing bezier ending on one point, the next diagram's first node, draw them over 24 f on E.smooth while the camera travels the same way with no cut, and finish the camera's travel with an E.out landing of about 210 px over 60 f (22 px/f at its start) through lib/camera.ts.
- **適用時機**：Explaining the friction of an old way (one simple path turning into many obstacles) before the turn to one clean path.
- **禁用避開**：The viewer needs real product UI on screen; this is diagram language, and a diagram act longer than about 4 s loses the thread.

##### `ui-stalled-state`：Stalled state by dimming
- **角色 / 能量**：`accent` ｜ `calm` 能量
- **60 FPS 時間時序**：Node dim 8 f (E.smooth) to 30%. Status words at +6/+28/+40 f, 8 f each (E.out, 6 px rise); first word dims at +51 f. Freeze <= 15 f on a silence, then 0.3 px/f drift.
- **構建配方 (Recipe)**：Split the rail at the stalled token: the travelled part solid, the part ahead dotted (strokeDasharray '2 4'), both drawn from the same path and clipped at the token's position. On the stall frame the destination node dims to 30% (opacity, or mixColor toward C.mute) over 8 f on E.smooth; status words then appear beside the token at +6, +28 and +40 f, each an opacity step with a 6 px rise through arrive() over 8 f on E.out, and at +51 f the first word dims to 40% so the decisive word (the reason, the day) stands alone. Bring the camera to zero velocity for a designed freeze of at most 15 f on a gap in the sound, then resume a 0.3 px/f drift so nothing sits static past 48 f.
- **適用時機**：The problem beat: money, a message or a task stuck waiting (closed, pending, rejected) just before the product unblocks it.
- **禁用避開**：The film has no problem act, or the block would sit longer than about 1.5 s; stillness only works as a short contrast to the motion around it.

#### `ui_choreography` 完整技法清冊 (19 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `ui-orbit-gather-merge` | Orbit gather and merge | signature | medium | Tokens swing into orbit around a node, slow to a lazy spin, ... |
| `ui-path-fracture-fan` | Path fractures into a fan, then re-converges | accent | medium | A solid line draws out, breaks into dashes, splits into a fa... |
| `ui-stalled-state` | Stalled state by dimming | accent | calm | A token stops on its rail, the destination greys out, short ... |
| `ui-clutter-pileup-strip` | Clutter pile-up, then strip to one | accent | high | Clicks spawn copies of a control until the frame is a messy ... |
| `ui-card-grid-arrival` | Cards dealt or dropped into a grid | workhorse | medium | Cards land in a row or grid one after another, either dealt ... |
| `ui-live-reflow` | Container resizes, content reflows | workhorse | medium | A card or window changes size because its content or the use... |
| `ui-row-cascade` | Row cascade | workhorse | medium | List rows or cards appear one after another from top to bott... |
| `ui-fan-resolve-to-slots` | Fanned stack resolves into slots | signature | medium | A tilted, overlapping stack of cards spreads into an even ro... |
| `ui-lens-list-scroll` | Lens list scroll | workhorse | medium | A list scrolls with momentum past an invisible lens line, an... |
| `ui-discard-into-bin` | Toss into a bin with one rebound | signature | high | Icons or chips are thrown into a container that rises in to ... |
| `ui-push-aside-reflow` | Push-aside with bound layout | workhorse | medium | An incoming panel or card enters from the edge and the neigh... |
| `ui-outline-led-reveal` | Outline-led insert and spawn | signature | medium | A thin accent line or a heavy outline appears first and open... |
| `ui-anchor-point-spawn` | Spawn from the anchor point | workhorse | medium | Menus, popovers, drop targets and detail cards scale out of ... |
| `ui-shell-first-build` | Shell first, then contents, then the action | workhorse | medium | The empty container is on screen first, its contents arrive ... |
| `ui-top-insert-push` | Top insert pushes the list down | workhorse | medium | New items arrive at the top of a list one at a time and ever... |
| `ui-container-morph` | Container morph into its next role | workhorse | medium | One element changes shape into what it becomes, a button unf... |
| `ui-drag-reorder-makeway` | Drag to reorder, siblings make way | workhorse | calm | An item lifts under the cursor, travels on a slight arc to a... |
| `ui-progress-spine-steps` | Progress spine leads the steps | workhorse | calm | A thin line grows down the side of a step list with a dot at... |
| `ui-genie-launch-from-icon` | Genie launch from an icon | accent | medium | A dock or home-screen icon flares open at its top into a cur... |

### 3.6 數據與計數動態 (Data & Numbers) — 共 17 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `data_and_numbers`
- **核心導演準則**：Numbers are proof, so they must read at a glance and stay true on any paused frame: tabular figures, a fixed digit count, and every shown value computed from fd(frame) so no motion-blur sub-sample shows two values. Hero counts are short, 28-46 f, starting from a credible 85-90% of the target on a quad-out (E.type) so the last unit lands in the final ~6 f instead of stalling; ambient UI counters may run 36-104 f. Charts draw in 24-96 f, bars grow 12-20 f each at 1.6-5 f staggers with any group landing within 30 f, and every bar tip, scan edge or line head stays at or under about 60-70 px/f at 1080p. A figure starts changing on the frame its cause lands (a press, a landing, a tab; effects follow the interaction by 2 f) and then holds at least 36 f plus 6 f per word of its label under a 2-3% breath. The one accent marks the hero series or the chosen item while comparison data stays grey, and two numbers are never crossfaded in place: cut them, count them or roll them.

#### 核心精選技法深入配方

##### `dn-ease-out-count-up`：Ease-out count-up from a near-final value
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Hero count 28 f on E.type (quad-out: 2x the mean rate at the start, so the last unit lands in the final ~6 f). Prices and recounts 36-46 f; ambient UI KPIs 36-104 f. Start at 85-90% of the target. Hold the landed figure at least 36 f (plus 6 f per word of any label) under a 2-3% breath before anything covers it.
- **構建配方 (Recipe)**：Compute the shown value on whole frames: v = Math.round(mix(a, b, prog(fd(frame), at, at + 28, E.type))), with a at 85-90% of b (173 to 195, 734 to 799), so early frames jump 2-3 units and the last ones step by 1. Use E.out only for ranges over ~500 units, where its long tail still has digits to tick. Render the value as plain text through typeStyle (tabular-nums), with a fixed digit count and Intl.NumberFormat separators so the box never changes width, and let the digits replace in place each frame: no roll, no crossfade. Start the count on the frame its cause lands and put ticks on countSteps(a, b, at, 28, E.type) frames, thinned to at most one every 2 f. After it lands, keep the block alive with breath() on the camera (2-3%) until the next element covers it.
- **適用時機**：A single proof figure (countries, users, a price) must register in under a second, or a number inside a UI shot should feel live.
- **禁用避開**：The number is the film's hero reveal and deserves a reel or a snap-out; nothing on screen causes the count to start.

##### `dn-count-glyph-swap`：Companion glyph swaps mid-count
- **角色 / 能量**：`accent` ｜ `medium` 能量
- **60 FPS 時間時序**：Swap at ~60% of the count (frame 17 of a 28 f count). Drop 8-12 px at 1080p over 8 f on E.out through arrive. The count lands 10-11 f after the swap.
- **構建配方 (Recipe)**：Set a 0.45 em glyph at the number's top-right as a superscript (translateY -0.35 em). Swap its source on the first whole frame where the shown value reaches the threshold (an fd-based v >= T compare, about 60% of the way through the count), cutting between the two images with no crossfade. On that frame start the drop: translateY from -0.35 em to 0 over 8 f with arrive(prog(frame, swap - 1, swap + 7, E.out)), so the new glyph seats on the baseline while the count is still finishing. Put a soft tick on the swap frame, separate from the count ticks.
- **適用時機**：The count carries a from-to story (origin to destination, free to paid, pending to done) that one icon can tell.
- **禁用避開**：The glyph would only be decoration; counts shorter than 20 f, where the swap gets lost.

##### `dn-status-pill-ring`：Process-status pill with ring progress
- **角色 / 能量**：`accent` ｜ `calm` 能量
- **60 FPS 時間時序**：Arrival on SPR.firm (~24 f to settle). Ring fill 30 f on E.out. Step roll 14 f. Dot pulse: attack 2 f, tau 8 f. Visible 46-90 f.
- **構建配方 (Recipe)**：Draw a rounded rect (radius 25% of its height) in C.ink2 with a 1.5 px C.line hairline border. Left to right, place an 8 px accent dot, a mono uppercase label (FONT.mono, 24 px at 1080p, tracking 0.15 em), an SVG ring (r 14 px, 3 px stroke, pathLength 1, strokeDasharray `${p} 1` over a C.line track), primary text at weight 500 ('Step 5/6 · Motion') and a C.mute date line. Animate it rather than parking it: the capsule rises 24 px on SPR.firm with opacity over 10 f on E.smooth; from the landing, the ring fills from 4/6 to 5/6 over 30 f on E.out, and the step digit rolls 4 to 5 through Roll on the fill's 50% frame. On the roll frame the dot pulses once, scale 1 + 0.4 * hitPulse(t, 2, 8).
- **適用時機**：Proving that a real, structured process exists (pipeline, build, delivery) as an overlay on process footage.
- **禁用避開**：The step and percentage aren't true to the story; frames that already carry a headline, which the pill would compete with.

#### `data_and_numbers` 完整技法清冊 (17 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `dn-ease-out-count-up` | Ease-out count-up from a near-final value | workhorse | medium | A proof figure counts up in place from a credible value just... |
| `dn-count-glyph-swap` | Companion glyph swaps mid-count | accent | medium | A small icon riding a counting number (a flag, an avatar, a ... |
| `dn-status-pill-ring` | Process-status pill with ring progress | accent | calm | A compact capsule shows where a process stands in one glance... |
| `dn-metric-cold-open` | Metric as the first statement | signature | high | The film opens on its proof number already moving, with no t... |
| `dn-tucked-unit-label` | Tucked unit under the last digits | accent | calm | A small lowercase unit word fades in right-aligned under a b... |
| `dn-hero-bar-pullback` | Hero bar in close-up, then pull back | signature | medium | The winning bar (or the hero chart) grows across a tight fra... |
| `dn-answer-card-bars` | Mini bar-chart answer card | workhorse | calm | Inside a chat or a panel, an answer arrives as a small card ... |
| `dn-line-draw-tracked-head` | Line chart draws with a tracking head | workhorse | medium | A line or stepped series draws left to right behind a solid ... |
| `dn-bar-sweep-lit-caps` | Constant-speed bar sweep with lit caps | workhorse | medium | A row of bars grows in a wave that travels at constant speed... |
| `dn-linked-control-counters` | One control drives several live numbers | workhorse | calm | Dragging a slider visibly drives every dependent figure in l... |
| `dn-flag-then-select` | Flag cascade, then one chosen | workhorse | calm | Status marks appear on a set of cards one after another, the... |
| `dn-row-cascade-value-swap` | Top-to-bottom row refresh | accent | medium | When a filter changes, a thin scan line crosses each table r... |
| `dn-digit-reel-detent` | Mechanical digit reel | workhorse | medium | Each digit sits in its own masked column and rolls verticall... |
| `dn-ring-gauge-sync` | Ring gauge filling with its centre number | workhorse | calm | A circular gauge sweeps to its value while the number at its... |
| `dn-delta-chip-compare` | Before-to-after with a delta chip | accent | medium | The old figure steps back to a small grey 'before', the new ... |
| `dn-unit-grid-tally` | Unit grid that fills to the count | accent | calm | A grid of small squares, each standing for a fixed number of... |
| `dn-area-ratio-compare` | Area-true ratio comparison | accent | calm | A multiplier claim ('10x smaller') plays as a block that shr... |

### 3.7 產品演示與場景 (Product Demo) — 共 22 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `product_demo`
- **核心導演準則**：A product shot depends on cause and effect: every action has a visible cause, the state changes on the cause frame itself (a 1 f swap, never a crossfade), and the result holds at least 36 f before the camera leaves. Give small UI hero weight through scale contrast, not length: alternate a wide with a 2-5x macro of the exact control, or open on the value moment at 1.6-2.2x and pull back to context over about 56 f, landing the next UI event within 2 f of the settle. Product arrivals are real motion. A device or window enters already moving (about 20 px/f on its first frame, settled by 44 f on E.out), and scrolls, sheets and widening bars peak at 35-60 px/f under the motion-blur pass. Holds stay alive with a 2-4% breath push instead of a dead lock. A person types at 30 cps. A fast product types at 50-72 cps, or to a fixed 68 f time box, with the newest characters arriving in the accent. Wherever possible let the product's own behaviour do the editing (a headline that grows into the input bar, an element that stays put while the page rebuilds around it, a window that recedes to its corner), so every transition also shows a feature.

#### 核心精選技法深入配方

##### `pd-device-rise-on-cut`：Device rises already moving
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：On a cut: 140-160 px over 44 f on E.out, first frame ≈ 6.2 × rise / 44 (about 20-23 px/f), 75% of the travel by f9, settled by f44; shot scale 1 → 0.9 over 48 f on E.outSoft. Over a title: ≈ 1,000 px in 48 f on E.glide, title fade 36 f starting 16 f early. Peek variant: 14 f peek, 4 f hover, 40 f launch on E.whip, 60 f scale drift.
- **構建配方 (Recipe)**：Drive the device group's translateY = tw(f, cut − 1, cut + 43, rise, 0, E.out) with rise 140-160 px, so it already moves about 20 px/f on the cut frame (prog is 0 on its first frame, hence cut − 1); no fade-in, since the cut hides the start, and the shadow travels with the device. Under it, scale the whole shot 1 → 0.9 over 48 f on E.outSoft; a desaturated photo backdrop (grayscale(1) contrast(1.1) brightness(0.7)) keeps the device the only colour. When the device must push a title off screen without a cut, rise it from a full frame height below over 48 f on E.glide (peak ≈ 59 px/f at 31%, motion blur on), fade the title on E.smooth starting 16 f before the device moves, and keep the device above the title in z. For anticipation, peek first: 170 px in 14 f on E.out, hover 4 f, then launch the rest on E.whip over 40 f (peak under 70 px/f) and drift the scale 1 → 0.93 over 60 f.
- **適用時機**：The first product shot after a type card or a photo, when the previous shot's energy should carry straight into the product.
- **禁用避開**：The device is already on screen; a calm film where a 20 px/f arrival feels pushy; it would be the third rise in a row (vary with a tilt or a pull-back).

##### `pd-tilted-plane-flattens`：Tilted product plane flattens
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：Rise 68 f on E.out: top edge ≈ 35 px/f on the first frame, ≈ 12 px/f by f4, ≈ 5.5 px/f by f8, then ≈ 3.5 px/f drift and an exit at ≈ 5.5 px/f on E.in; tilt follow-through 20 f, starting 6 f before the position lands; hero de-skew: hold ≤ 34 f, then 80 f on E.glide (peak edge speed ≈ 60-70 px/f at about 31%).
- **構建配方 (Recipe)**：Give the page's parent perspective 1800-2000 px; on the page set transform-origin 50% 100% and tween translateY 270 → −60 px, rotateX 25° → 8° and scale 1 → 1.3 over 68 f on E.out, then drift linearly at about 3.5 px/f and leave on E.in. Resolve the last 8° → 0 as follow-through on its own E.out over 20 f, starting 6 f before the translate lands, so position and tilt settle at different moments. Hero version: hold the plane tilted for up to 34 f with progressive depth of field (4-6 horizontal bands, each a RackFocus at 0/2/4/6/8 px by distance from the focal row), then rotate rotateX and rotateZ to 0 over 80 f on E.glide while every band racks to sharp as the rotation reaches zero. Edge the page with a 1.5 px solid C.line hairline rather than a lit rim; an in-page headline may build with src/fx/Words.tsx while the plane still moves, but nothing is meant to be read until it lands.
- **適用時機**：Introducing a real web page or app screen as the real thing while keeping the camera alive; the first frontal look at the product.
- **禁用避開**：The UI must be read during the move; the plane would need more than about 30° of tilt (text shears and aliases); the same flatten ran within the last 10 s.

##### `pd-hard-swap-on-cause`：Hard swap on the cause frame
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Swap 1 f on the cause frame; hover 6 f before the press; recount 36-46 f on E.out with 14 f digit rolls; punch attack 2 f, tau 5; kick peaks on the swap frame and settles in 6-8 f; at most one swap per 30 f, 54 f apart in a repeating sequence.
- **構建配方 (Recipe)**：Export the cause frame once (the press of pressAt from src/fx/Cursor.tsx after a hover state shown 6 f earlier, or a selection marker's landing) and switch state on fd(f) >= CAUSE so every motion-blur sub-sample agrees; never crossfade the two states. Re-count numbers with Roll fed countSteps(next − delta, next, CAUSE, 40, E.out), delta about 5-10% of the value, so the digits roll instead of cutting. Punch the swapped object with scale 1 + 0.02 · hitPulse(f − CAUSE, 2, 5). For a print or card beside a list, kick it: perspective 900 px, transform-origin on its left edge, rotateY = 12° · hitPulse(f − CAUSE + 1, 1, 2.5) with skewY 2° on the same envelope and a soft shadow (0 18px 40px rgba(0,0,0,.18)), while the list's selection marker moves 6 f before the swap.
- **適用時機**：A choice changes the product instantly: a variant picker, filter, plan selector, theme switch, a canvas that appears whole on launch.
- **禁用避開**：The change is a process the viewer should watch; two numbers would sit half-and-half in place; swaps faster than one per 30 f (the clicks read as a macro).

#### `product_demo` 完整技法清冊 (22 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `pd-device-rise-on-cut` | Device rises already moving | workhorse | medium | A phone or app window enters from below already travelling o... |
| `pd-tilted-plane-flattens` | Tilted product plane flattens | signature | medium | A real product page lies tipped back in perspective, rises t... |
| `pd-hard-swap-on-cause` | Hard swap on the cause frame | workhorse | medium | On a click or selection the product image, view or value cha... |
| `pd-blur-resolve-load` | Generated view resolves from soft | accent | medium | A freshly generated window or row appears as a soft, out-of-... |
| `pd-agent-status-then-answer` | Agent status beat, then streamed answer | workhorse | calm | The product's tiny working status is shown at hero size, as ... |
| `pd-headline-becomes-input` | Headline becomes the product input | signature | medium | Without a cut the headline turns into the product: a caret a... |
| `pd-fast-prompt-true-scale` | Fast prompt at true scale | workhorse | medium | The real prompt bar fills with a long, honest instruction in... |
| `pd-mark-docks-into-app` | Mark docks into the app | accent | medium | An integration mark or icon travels to an app tile or page a... |
| `pd-ui-native-transitions` | Edit with the product's own UI | workhorse | medium | Instead of cuts, the film moves between product areas the wa... |
| `pd-shared-element-page` | Shared element survives the page change | signature | medium | The cursor clicks a row; the page drains away except the row... |
| `pd-flick-scroll-lands-target` | Flick scroll lands the target | workhorse | medium | A list or page scrolls like a trackpad flick, entering alrea... |
| `pd-single-control-hero` | One native control as the demo | workhorse | calm | Instead of a screenshot, the feature is shown as the single ... |
| `pd-drag-assets-skeleton-fill` | Drag assets in, skeletons fill | accent | medium | The cursor drags a fanned stack of images into the input; af... |
| `pd-pin-field-pullback` | Pin field pull-back | accent | medium | A map pulls back from a close view to reveal a field of loca... |
| `pd-before-after-drag-wipe` | Before/after drag divider | accent | medium | The cursor grabs a vertical divider on the product and drags... |
| `pd-page-runway-flyover` | Long page flown like a runway | accent | high | A whole long page lies on a steeply tilted plane that recede... |
| `pd-ghost-suggestion-accept` | Ghost suggestion accepted with a key | workhorse | calm | As someone types, the product proposes the rest of the line ... |
| `pd-live-filter-narrows` | List narrows with each keystroke | workhorse | medium | A shortcut opens a command palette or search field, and as t... |
| `pd-chart-scrub-readout` | Scrub a chart with a live readout | workhorse | calm | The cursor glides across a chart; a hairline and a dot ride ... |
| `pd-terminal-burst-output` | Command runs, output prints in bursts | workhorse | medium | A command is typed at human speed and entered; the terminal ... |
| `pd-diff-hunks-apply` | Change applied as a visible diff | workhorse | calm | A proposed edit lands in a code or document view as a diff: ... |
| `pd-presence-cursors` | Several people at work at once | accent | medium | Two or three named cursors move and act on the same canvas a... |

### 3.8 品牌與結尾卡片 (Logo & End Card) — 共 18 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `logo_and_end_card`
- **核心導演準則**：The end card is the film's poster. The lockup appears once, sized at 28-45% of frame width, resolves within about 36-80 f, then holds 90-120 f (1.5-2.0 s, never past ~150 f) while it keeps building: a 10-20% push on E.dolly and tracking that tightens 0.03-0.06 em over ~46 f. Anything static past 48 f reads as a stalled player. The strongest endings come out of the story instead of starting a new logo animation: the last object lands on the mark's exact position and size, or the product clears the stage to uncover it, or the opening's mechanic returns carrying the name. Scale moves run in log space (lmix). Collapses from 9-12x settle in 36-66 f, and the fastest frames are flat fill, low contrast or motion-blurred. The name follows the mark at 55-60% of its slide, with letters 2-3.5 f apart and readable type never faster than 20 px/f. Sound carries half the weight: cut the music dead on the end-card frame, leave ~36 f of near-silence, put one hit on the frame the name resolves, and let its tail decay to digital zero inside a tail of at least 60 f. The last frame must show the mark plus the name, with at most one CTA at 44-56 px that stays readable for at least 1.7 s, and it never fades to black.

#### 核心精選技法深入配方

##### `le-mark-slide-name-follow`：Mark slides aside, name follows
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Slide: 36 f for up to ~250 px (E.smooth peaks ~20 px/f), 60 f for ~350 px (~17 px/f). Motion-blur pass on the mark whenever it moves faster than 12 px/f. Name starts at 0.55-0.6 x D: a block takes 14 f; letters take 16 f each at a 3 f stagger (10 letters inside ~43 f). Tracking: 46 f on E.out. Lockup resolved by about D + 20 f, then hold 90-120 f.
- **構建配方 (Recipe)**：Lay the finished lockup out first: LOCKUP token with mark height = the name's cap height, gap = 0.25-0.4x the mark height, and the name's width from measureTracked. Then slide the mark from frame centre to its lockup slot with x = tw(f, a, a+D, 0, -(nameW + gap)/2, E.smooth). If it was larger as a hero, scale it lmix(heroK, 1, same progress) with heroK about 1.6. Start the name when the slide passes 55-60% of its progress. As one block: opacity on E.smooth, blurIn(p, 10), translateX +30 -> 0 on E.out. Per letter: the same over 16 f at a 3 f stagger, with colour mixColor(C.mute, C.ink, p) so letters arrive grey and settle to ink. From the name's resolve, tighten its letter-spacing from +0.04 em to the TYPE.display track over 46 f on E.out; this hands into the hold's push. For a round mark, add roll: rotate = -(dx / r) * 180/pi degrees, so it rolls without slipping and stops exactly when x does. In 9:16, stack instead: the mark rises by (nameH + gap)/2 and the name rises in under it with MaskRise.
- **適用時機**：Any end card whose mark is already on screen (it was the story device or the hero) and the name still has to arrive. The default lockup build.
- **禁用避開**：The mark has not been seen yet (give it its own beat first). The film already used a slide-to-make-room for the product. Long names that would push the slide past ~400 px (stack vertically instead).

##### `le-reverse-type-recentre`：Name types backwards, group stays centred
- **角色 / 能量**：`accent` ｜ `calm` 能量
- **60 FPS 時間時序**：3.5 f per character (10 characters in 36 f), each fading in over 4 f on E.ui. Each width step eases on SPR.firm (no overshoot, ~20 f to settle). The mark travels ~270 px at 7-8 px/f on average. Dot-to-mark darkening takes 12 f. The lockup settles ~20 f after the last character, then holds 90-120 f under a 10-15% push (le-living-hold).
- **構建配方 (Recipe)**：Lay out [mark][gap][name], with every character laid out from the start and untyped characters at opacity 0. Measure each character's advance with measureTracked. Character i of n shows from frame t0 + 3.5 * (n-1-i), decided on fd, with a 4 f opacity ramp on E.ui, so the name grows leftward from its last letter. Keep the group centred without stepping: markLeft = cx - (markW + gap + ws(f))/2, where ws(f) = sum of adv_k * spr(f, t_k, SPR.firm) over the characters revealed so far. That is one critically damped spring per character, which glides the mark outward as each letter lands. If the story device is a dot, let it become the mark in place first: fill mixColor(C.mist, C.ink, p) over 12 f on E.smooth, with the glyph inside fading in over the last 4 f.
- **適用時機**：Agent, assistant or persona products whose mark is an avatar or a disc. Names of 4-12 characters. A centred lockup that must never jump.
- **禁用避開**：Two-word names whose second word makes no sense on its own first. Right-to-left scripts (it becomes an ordinary type-on). The headline already used a typewriter.

##### `le-macro-pullout-breathe`：Pull out of the mark, undershoot, breathe
- **角色 / 能量**：`signature` ｜ `high` 能量
- **60 FPS 時間時序**：Collapse: N = 43 x ln(s0 / 0.93) frames on E.outSoft (72 f from 5x; log rate about 0.105/f at the start, outer edge under about 80 px/f, under 0.07/f by f10). Breathe: the last 24 f on E.smooth (0.93 -> 1.0), bottoming at 0.94 near f52. Settled by f72. Hold the mark ~20 f before the name follows.
- **構建配方 (Recipe)**：Place the Mark with placeMark at its final spot; centre it where the lockup needs it, e.g. 80 px left of frame centre to leave room for the name. Pick the start scale s0 so the mark's outer edge starts about 750 px from its centre (s0 = 750 / the mark's half-width at rest, about 5x for a 300 px mark), so only fragments fill the frame. Scale it about its own centre in log space: s = lmix(s0, 0.93, prog(f, a, a+N, E.outSoft)) * lmix(1, 1/0.93, prog(f, a+N-24, a+N, E.smooth)), with N = 43 x ln(s0 / 0.93) frames (72 f from 5x). The log rate then starts near 0.105/f, so the outer edge never passes about 80 px/f; from 5x it crosses 1.0 near f35, bottoms out at 0.94 near f52 and breathes up to rest at 1.0 by f72 with no velocity step. Enter it on a cut: the outgoing shot shrinks into its centre on E.in over its last 24 f and cuts at a matching log speed (or start from zoomHandoff in camera.ts at the outgoing log speed). Render with the motion-blur pass. Keep the mark's counters and small parts outside the frame until the log rate falls below 0.07/f (~f10). Put the bottom of the undershoot on the strongest low hit after a ~15 f bass gap.
- **適用時機**：The mark's first full appearance at the end, or a logo sting. A hit after a short bass gap. Marks with a strong silhouette or inner shapes that read as abstract fragments when huge.
- **禁用避開**：Thin line marks (at macro scale they become two hairlines crossing the frame). Right after another zoom-through seam. The mark was already shown at hero size earlier (that makes this a replayed reveal).

#### `logo_and_end_card` 完整技法清冊 (18 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `le-mark-slide-name-follow` | Mark slides aside, name follows | workhorse | medium | The centred mark glides sideways, shrinking if it was hero-s... |
| `le-reverse-type-recentre` | Name types backwards, group stays centred | accent | calm | The name appears from its last letter to its first while the... |
| `le-macro-pullout-breathe` | Pull out of the mark, undershoot, breathe | signature | high | The mark arrives so large that only fragments of it fill the... |
| `le-slam-spin-pullout` | Dark slam, spin and brighten | signature | high | After a near-still beat, giant low-contrast arms of the mark... |
| `le-seed-stroke-build` | Seed build with stroke draw-on | workhorse | medium | The mark grows from a small seed while its strokes, stripes ... |
| `le-gooey-merge-to-mark` | Liquid blob resolves into the mark | signature | medium | A dot, or two soft lobes sliding in from the sides, swells i... |
| `le-clone-stack-morph` | Staircase echo shape morph | accent | medium | A large brand shape collapses into a slim pill around the UR... |
| `le-device-becomes-mark` | Story object becomes the mark | workhorse | any | The film's last object (a dot, circle, coin or pill) ends at... |
| `le-words-part-url-types` | Words part, URL types into the gap | accent | calm | The closing line splits at its middle, both halves slide out... |
| `le-card-to-pill-flank` | Card shrinks to a pill, words close in | accent | medium | The last content card empties and shrinks into a small pill ... |
| `le-accordion-cta-collapse` | CTA line closes its gaps | accent | calm | The end line starts with exaggerated spaces between its word... |
| `le-stage-clears-to-brand` | The product clears the stage | workhorse | any | The last product element leaves (dropping out of frame, acce... |
| `le-bookend-replay` | End card replays the opening | workhorse | any | The ending reuses the opening's stage and its mechanic, now ... |
| `le-living-hold` | Lockup keeps building through the hold | workhorse | calm | Once resolved, the lockup never freezes: the card slowly pus... |
| `le-strobe-sting` | Stop-motion brand strobe | accent | high | A burst of hard-cut brand states (the poster, the lockup til... |
| `le-hot-to-neutral-cool` | Accent icon cools to its neutral mark | accent | medium | The app icon pops up from tiny in the film's hot accent, coo... |
| `le-mark-glint-turn` | Mark turns through a key light | accent | calm | The mark (an extruded glyph, a coin or a tile) turns a few d... |
| `le-mark-ticks-in-lockup` | Device keeps time inside the lockup | accent | calm | During the hold, the story device that became part of the ma... |

### 3.9 色彩與光影節奏 (Color & Light) — 共 25 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `color_and_light`
- **核心導演準則**：Colour carries meaning, so ration it. Keep one accent with one job. It should cover roughly 0.05-6% of frame pixels on average (peaking near 12%) on a stage that fills 85-90% of the frame, and it should change on cut or impact frames, never through slow fades. Brightness is the strongest lever here: give every shot a planned mean luma, spend polarity flips of 160-240 levels on downbeats and act changes, and use at most one inverted card (about 60 f) in a dark film. Light moves are short and asymmetric: accent floods rise in 10-12 f and release over 20-26 f, sheens cross in about 36 f, and washes rise over about 40 f and recede over about 90 f. Stages never freeze: breathe them ±15% luma on a period of about 160 f, or drift them under 1 px/f. Build every gradient from tonal steps of one hue mixed in OKLab with mixColor, on normal blend, and let a hard edge or a one-frame white flash do the work a glow would.

#### 核心精選技法深入配方

##### `cl-mono-one-accent`：Monochrome world, one accent
- **角色 / 能量**：`workhorse` ｜ `any` 能量
- **60 FPS 時間時序**：The palette stays the same for the whole film. The accent swaps on the cue frame (a step, 0 f). Focus outlines land 6-10 px wide with their container (26 f, E.out), thin to 1 px over 12 f on E.in, then decay to 30% opacity over 24 f on E.linear.
- **構建配方 (Recipe)**：Declare neutrals plus one accent in brand/tokens.ts: C.ink for the stage, C.ink2 for surfaces, C.mute for labels, C.line for strokes, C.white for type, C.accent, and a press step of mixColor(C.accent, C.ink, 0.08). Grade every photo, map, clay render or backdrop screenshot with filter: grayscale(1) so mixed media reads as one world. Paint the accent on exactly one thing per shot (the payoff word, the pin, the pressed button, the focus ring) and keep one meaning for it all film. Focus devices use three steps of it: the full accent for strokes, mixColor(C.accent, C.ink, 0.65) for fills and a mid step for decaying outlines. Colour arrives on a cut or an impact frame (fd(frame) >= cue), never through a slow fade, and when you audit rendered stills the accent should average 0.05-6% of frame pixels (peak about 12.5%) with the stage at 85-90%.
- **適用時機**：Films that mix photos, 3D, maps and UI, multi-cell layouts, or any shot where several things compete and the eye needs exactly one target.
- **禁用避開**：The product's own colourful UI is the subject of every shot and greying it would misrepresent it, or the story needs two semantic colours on screen at once.

##### `cl-one-hue-light-ramp`：One-hue light ramp
- **角色 / 能量**：`workhorse` ｜ `calm` 能量
- **60 FPS 時間時序**：The palette stays the same. The end-card field holds 90-120 f with the bands drifting 0.3 px/f on E.linear.
- **構建配方 (Recipe)**：Build five tokens of one hue with mixColor, running from the stage to a pale tint: C.ink, then mixColor(C.ink, C.accent, 0.2 / 0.45 / 0.75), then mixColor(C.accent, C.white, 0.5). Only ever draw a gradient between two adjacent steps, so the whole film's light comes from one decision. Rims, rings and orb lobes use the upper steps as crisp strokes or flat fills, never as soft halos or bloom, and the stage holds 63-99% of pixels on dark frames. For an end-card field behind a wordmark, use linear-gradient(to top, step0, step2 45%, step4) plus a repeating-linear-gradient(90deg) of flat, hard-edged 60-120 px bands at ±6% lightness (no blur, so they never read as fluted glass); the band layer drifts 0.3 px/f so the hold never freezes. Against banding, bake the field as a dithered PNG with scripts/dither-gradient.py and let the film's global 1.5-2% grain sit over it.
- **適用時機**：Dark launch films with many light-built shapes (orbs, rings, rims) that need a recognisable look. It also makes a single bright card hit harder.
- **禁用避開**：Light-mode walkthroughs where the UI's own colours dominate, or films already using the monochrome-plus-accent system (pick one system).

##### `cl-accent-claim-grounds`：Accent ground for claims only
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：Grounds swap on cut frames. The radial flood takes 6 f, with tint steps on f0, f2 and f4 decided with fd(). The ring stays from f4 to the end of the shot. Claim shots run 60-120 f each.
- **構建配方 (Recipe)**：Use two ground tokens (C.paper or C.ink, and C.accent) and one ink. Tag each shot 'story' or 'claim' in timeline.ts. The accent floods the frame once per film: give the full-bleed accent ground to the one hero claim (about 72 f) or to the closing card, and set every other claim on the opposite neutral stage (C.ink after C.paper, or the reverse) with the accent only on its one key word, so accent pixels stay near 8% across the film. Switch grounds on hard cuts; elsewhere the accent appears only as a one-word highlight or a soft single-hue wash that previews the flood. Let the accent ground arrive as a radial flood. Layer order: the accent ground; a disc of radius 640 px whose fill steps mixColor(C.accent, C.paper, 0.75), then 0.4, then 0; a 60 px ring of mixColor(C.accent, C.ink, 0.1) at r 600 px, which appears with the last step and stays for the shot to frame the hero word; then the type.
- **適用時機**：Films with a few big statements that must feel louder than the walkthrough around them, and endings that need to feel conclusive.
- **禁用避開**：The accent fails contrast as a ground for display type, or the film has no distinct claims (a pure UI tour).

#### `color_and_light` 完整技法清冊 (25 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `cl-mono-one-accent` | Monochrome world, one accent | workhorse | any | Everything is black, white and grey, and one saturated accen... |
| `cl-one-hue-light-ramp` | One-hue light ramp | workhorse | calm | Every lit thing (rims, rings, stage lifts, the end-card fiel... |
| `cl-accent-claim-grounds` | Accent ground for claims only | signature | medium | Narrative shots sit on the neutral stage, other claims flip ... |
| `cl-inversion-card` | Single inversion card | signature | medium | In an otherwise dark film, one card cuts to a near-white fie... |
| `cl-theme-flip-in-motion` | Theme flip mid-move | signature | high | In the middle of a camera fly-over, the dark page and stage ... |
| `cl-context-palette-shift` | Palette shift as context cue | workhorse | medium | The world's colour changes behind a steady foreground, for a... |
| `cl-ink-resolve` | Ink resolve on arrival | workhorse | any | Text never simply fades in: it arrives pale (or dim on a dar... |
| `cl-accent-on-newest` | Accent on the newest arrival | workhorse | medium | Whatever just arrived (a typed character, a snapped word, a ... |
| `cl-accent-hit-envelope` | Accent hit envelope | accent | medium | On a press or an impact, the element floods with the accent ... |
| `cl-specular-sweep` | Specular sweep | workhorse | calm | A soft bright band glides once across a settled number, word... |
| `cl-rim-light-sweep` | Rim streak on card edges | accent | calm | A bright streak travels along a dark card's border while its... |
| `cl-tone-band-fill` | Travelling tone band fill | accent | medium | A word, URL or logo mark fills through a band of colour (dar... |
| `cl-living-stage` | Living gradient stage | accent | calm | Behind static cards the background never freezes: soft pools... |
| `cl-light-swell-bridge` | Light swell bridge into the hero | signature | high | Light swells around a small panel until the frame is bright,... |
| `cl-rising-wash-carrier` | Rising colour wash carrier | accent | medium | A soft single-hue field rises from the bottom edge behind th... |
| `cl-drain-stage-keep-hero` | Drain the stage, keep the hero | workhorse | calm | Everything around the hero fades and the world drops to dark... |
| `cl-tilt-linked-sheen` | Tilt-linked sheen | accent | calm | As a card or device tilts in 3D, a faint highlight band slid... |
| `cl-duotone-until-featured` | Duotone until featured | accent | medium | Screenshots and photos sit in a two-tone grade until their b... |
| `cl-key-light-edge-hairline` | Key-light edge hairline | workhorse | calm | Every card, device bezel and bevelled shape on a dark stage ... |
| `cl-brightness-rides-move` | Brightness rides the move | accent | high | A mark or icon takes its brightness from the same progress t... |
| `cl-read-state-tone-ladder` | Now, was, next tone ladder | workhorse | any | Items in a sequence sit on three neutral tones: the one bein... |
| `cl-graphic-blurs-into-stage` | Graphic softens into the stage | accent | calm | A crisp graphic that has just finished its move, such as a w... |
| `cl-rolling-band-flood` | Rolling band flood | signature | medium | A light frame fills with the brand colour as soft horizontal... |
| `cl-hue-tinted-shadow` | Shadows tinted by the stage | accent | calm | On a tinted light stage, lifted cards and solid pills cast s... |
| `cl-type-solidity-arc` | Type solidity arc | accent | calm | The type gains body across the film. Early statements are tr... |

### 3.10 質感後製與幀率 (Texture & Finish) — 共 20 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `texture_and_finish`
- **核心導演準則**：Texture and finish decide whether a film built from code reads as photographed or as a slideshow, and almost all of it works at the edge of perception: grain at a sigma of 1-2 code levels (a 1.5-2% layer), dot fields about 4% off their ground, photo plates graded to 5-8% mean luma, gobo shadows drifting under 0.5 px/f. Speed is finished in the render, not faked per layer: anything over 12 px/f gets the 240-degree float-accumulated blur pass, holds sit under 2 px/f so they render pin-sharp, and no element passes about 70-80 px/f. Every soft ramp ships as a dithered PNG, because a CSS gradient spanning fewer than about 30 code values bands, and every texture that animates is keyed to fd(frame) so the motion-blur sub-samples agree. Each texture must name its job (context, material, concealment, a hit) and keep one strength for the whole film. One signature surface move (a 34 f scanline transmutation, a ring field, a locked mosaic) is plenty for a film.

#### 核心精選技法深入配方

##### `tx-speed-gated-motion-blur`：Speed-gated motion blur
- **角色 / 能量**：`workhorse` ｜ `any` 能量
- **60 FPS 時間時序**：Whip 12-20 f on E.whip with a 40-70 px/f peak, the shots either side at 0.3-1.5 px/f; streak length is about 2/3 of the per-frame travel (a 60 px/f card smears ~40 px); a flick is inertia(f, start, 50-70, 0.89), coasting ~8.6 x v0 px and under 0.5 px/f after its `settle` frames; nothing above 80 px/f.
- **構建配方 (Recipe)**：Never fake speed blur per layer in the browser (CameraMotionBlur and an animated filter: blur() quantise to 8 bits and step); design the moves and let the master's render pass make the blur: `bash scripts/render.sh Film out/film.mp4 --blur` renders a 240-degree shutter centred on each frame, takes samples from measured speed (1 under 2 px/f, 4 up to 18 px/f, 14 at 60, 18 at 80) and averages them in float. Shape every fast move so its peak sits between 12 and 70 px/f (E.whip or E.inOut, or inertia() for a flicked scroll) and both ends fall under 2 px/f, so the streak exists only mid-move. Put every hard cut on an act boundary so samples never smear across it, and drive typed text, counters, carets and grain from fd(frame) so all sub-samples of a frame agree. Where optical flow cannot see the speed (a flat band wiping the whole frame) pass `--floor A-B:px` or analytic speed; in HyperFrames render at 4x fps and run `accumulate.py --uniform 4`, which is clean only to about 12-18 px/f.
- **適用時機**：Any film with whips, flings, drops or flicked scrolls; walkthroughs that travel fast between setups and need every hold razor-sharp.
- **禁用避開**：Moves that would need more than 80 px/f (redesign as a cut on the beat, a match cut or a mask wipe); readable text moving above 20 px/f; a deliberately stepped on-twos section.

##### `tx-on-twos-cadence`：Stepped cadence on twos
- **角色 / 能量**：`accent` ｜ `medium` 能量
- **60 FPS 時間時序**：Steps every 2 f (30 Hz in a 60 fps file); moves of 60-150 px over 24-40 f on E.glide or SPR.firm evaluated at f2, peaking at or under 24 px per step; at least one full shot or act long.
- **構建配方 (Recipe)**：Inside the chosen layer compute `const f2 = 2 * Math.floor(fd(frame) / 2)` and pass f2 instead of frame to every prog, tw, spr and hitPulse call it makes (or use interpolate(..., { posterize: 2 }) for a single value), so every motion-blur sub-sample of a frame agrees and each held pair renders sharp. Because a held frame cannot carry blur, keep every stepped element under 24 px per step (12 px/f average) and type under 20 px per step; leave the camera, backgrounds and grain on the native frame. Apply it to a whole act (a UI-precision section, a sting) or to the type layer only, never switching on and off inside a shot.
- **適用時機**：Mechanical, developer or precision brands; a UI section that should feel like a live screen; a short sting that wants a punchy graphic cadence.
- **禁用避開**：Slow drifts and camera pushes (they judder); moves that would exceed 24 px per step; a few isolated shots in a smooth film, where it reads as dropped frames.

##### `tx-mixed-media-grade`：One grade across mixed media
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Swap media inside a shot or cell every 48-90 f, on beats; hard cuts between media need no transition because the value range already matches.
- **構建配方 (Recipe)**：Normalise each medium before it enters a shot: photos get `filter: grayscale(1) brightness(0.65) contrast(1.05)`; 3D or clay renders use matte grey materials (base around 40% grey, no coloured speculars) with C.accent on the hero prop only; vector maps fill land at C.ink plus OKLCH 0.03-0.04 lightness with 1.5 px borders at 15-25% white; line diagrams draw in white at 60-80% with the accent on the one active path. Check that every medium's mean luma lands within 8-25% and that nothing except the accent exceeds OKLCH chroma 0.03, then hard-cut or swap media inside a shot or grid cell on beats. The accent keeps the same single meaning in every medium.
- **適用時機**：Films that must combine photos, renders, maps, diagrams and UI, especially grid or bento layouts with several media on screen at once.
- **禁用避開**：Light, pastel or colourful brands; single-medium films; hero product photography that must keep its true colour.

#### `texture_and_finish` 完整技法清冊 (20 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `tx-speed-gated-motion-blur` | Speed-gated motion blur | workhorse | any | Fast whips, flings and flicked scrolls streak like a real sh... |
| `tx-on-twos-cadence` | Stepped cadence on twos | accent | medium | One designated layer or section updates only on every second... |
| `tx-mixed-media-grade` | One grade across mixed media | workhorse | medium | Desaturated photography, matte grey 3D, flat vector maps and... |
| `tx-low-luma-photo-plate` | Low-luma photo plate | workhorse | calm | A real photograph sits behind the UI or type, graded almost ... |
| `tx-global-grain` | Global frame-keyed grain | workhorse | any | A fine, even grain sits over the whole film at one strength,... |
| `tx-ramp-masked-stipple` | Stipple only in lit ramps | accent | calm | A visible dithered stipple lives only inside lit edges and l... |
| `tx-dot-matrix-silhouette` | Faint dot-matrix silhouette | accent | calm | Behind a claim, a barely visible field of dots forms a meani... |
| `tx-scanline-transmute` | Scanline transmutation | signature | medium | A bright bar sweeps down a hero object: above the bar the ob... |
| `tx-locked-mosaic` | Locked-state mosaic | signature | medium | Withheld content shows as pixelated, desaturated, darkened a... |
| `tx-ring-field` | Intersecting ring field | signature | medium | Above and below a centred band of type, families of huge ove... |
| `tx-brushed-micro-streaks` | Brushed micro-streaks | accent | calm | Fine directional streaks and a satin grain across a hero obj... |
| `tx-glyph-grid-pulse` | Glyph-grid shock pulse | accent | high | On the film's biggest hit, the dark background flashes a gri... |
| `tx-gobo-studio-shadows` | Gobo-lit studio backdrop | workhorse | calm | The UI floats over an off-white studio backdrop crossed by h... |
| `tx-fog-floor` | Fog floor | workhorse | calm | The bottom fifth of the frame lightens toward the stage's br... |
| `tx-micro-tick-ui-sound` | Micro-tick UI sound | workhorse | any | (Sound) Typing and UI changes get tiny, dry ticks at or unde... |
| `tx-surface-edge-finish` | Hairline edge and key shadow | workhorse | any | Every floating surface gets a 1 px edge plus one soft key sh... |
| `tx-feathered-edge-mask` | Feathered edge mask | workhorse | any | Lists, reels and overflowing lines dissolve into the stage a... |
| `tx-mosaic-resolve` | Stepped mosaic resolve | accent | medium | An image or screen arrives as coarse grey blocks that halve ... |
| `tx-wireframe-scan-build` | Wireframe-to-product scan | signature | medium | A thin accent line sweeps across a UI card: ahead of it the ... |
| `tx-halftone-shading` | Halftone shading | accent | calm | A flat hero shape gains volume from a single-colour halftone... |

### 3.11 版面與動態構圖 (Layout & Composition) — 共 16 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `layout_and_composition`
- **核心導演準則**：In motion, layout means two things: where the eye lands, and how space gets made when something new arrives. The default is one subject per frame. That is a UI card at 72-92% of frame width or one line of type no wider than 80%, with captured UI shown at about 2x so body text is at least 27 px at 1080p, and everything that is not the hero dimmed to 0.6-0.7 brightness or defocused. When something enters, the layout makes room physically rather than overlaying it: neighbours move 0.43x the newcomer's travel and start up to 28 f early, and centred lines re-centre on a critically damped spring (20-45 px over 16-38 f) and then keep a 0.4-1.5 px/f drift so type never freezes. Captions go in the space the subject leaves: a 25-30% band, at most 24% of the frame width, inset 8-10% from the edge, starting in the last 25% of the move. To show breadth, use flush cells with no gutters on one shared stage, looping on coprime periods so a change lands somewhere about every 20 f. Any mark inside a sentence sits on the baseline at cap height, in a reserved slot.

#### 核心精選技法深入配方

##### `lc-swarm-cluster-burst`：Swarm, cluster and burst reveal
- **角色 / 能量**：`signature` ｜ `high` 能量
- **60 FPS 時間時序**：Fly-in 28-40 f, entering at 56 px/f and decaying. Swirl 60 f. Converge 32 f (cluster width 1474 to 1076 px at 1080p). Build 104 f at +0.2%/f, E.linear. Burst 24 f, peaking at 72 px/f with motion blur; the last cards clear by f24, then hold the hero. Shorter scatter-only version: cards leave on E.in over 22 f, with travel scaled by (1 + 0.1 * index).
- **構建配方 (Recipe)**：Place the hero (lockup, stat card, product) centred at z 0, already at final size, with N = 16-24 cards above it. Give card i a slot in a packed cluster (a grid jittered by rand(i): up to 40 px and 6 deg, overlapping, larger cards higher in z) and a unit radial vector from the centre through that slot. Fly-in: set the card's offset along its vector to total - inertia(f, s_i, 56, 0.95).x, so it starts about 1090 px out and coasts into its slot, with start frames spread by stagger(i, N, 24, E.out). Over the next 60 f the slots rotate about the centre by an angle that decays from 24 deg to 0 on E.outSoft (the swirl), contract to 73% spread over 32 f on E.out, and then the whole cluster scales up linearly by 0.2% per frame. Burst: each card travels along its vector by d(n) = 3n^2 px for n <= 12, then 432 + 72(n - 12), with scale 1 + 2(n/24)^3 under a true motion-blur pass, so the hero is uncovered in about 18 f.
- **適用時機**：A crescendo near the end that proves breadth (many apps, templates, outputs) and clears the stage for the lockup or a hero stat; the film's single biggest motion spike.
- **禁用避開**：Calm or minimal films, more than once per film, or when the cards' content has to be read (nothing in the swarm is legible). If it reveals the lockup, the lockup still holds only 1.5-2.0 s.

##### `lc-arc-carousel`：Arc carousel
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：90 f per pass. Card speed 58 px/f on entry, about 8 px/f through the middle, 39 px/f on exit (angular 1.9, then 0.25, then 1.3 deg/f). Spacing 11 deg, about 336 px of arc, for cards 260-300 px wide.
- **構建配方 (Recipe)**：Use a circle of R = 1750 px centred at (960, -790) at 1080p. Card i sits at angle theta_i = theta0(f) + i * 11 deg, with x = 960 + R sin(theta_i), y = -790 + R cos(theta_i) and rotateZ(-theta_i), so the arc bottoms out at y = 960 and the cards lean outward toward the edges. Drive it with a U-shaped speed: theta0(f) = 12 deg * (1 - prog(f, 0, 45, E.out)) - 0.25 deg * (f - 45) - 7.6 deg * prog(f, 45, 90, E.in), over 12 opaque cards with soft drop shadows, z-ordered so the centre card is on top. Behind them, a large flat ellipse (or one accent hue fading to transparent) centred above the arc acts as the dome. Apply the motion-blur pass while card speed exceeds 12 px/f (roughly the first 15 f and the last 20 f).
- **適用時機**：Showing an inventory or collection (templates, cards, products, integrations) where several items should read at once and the set should feel endless; a looping feature beat.
- **禁用避開**：Items with dense text that must be read at the edges (tilted edge cards are glanced at, not read), or vertical frames where the arc gets too tight.

##### `lc-hero-flips-to-inline-glyph`：Hero icon becomes the inline glyph
- **角色 / 能量**：`accent` ｜ `medium` 能量
- **60 FPS 時間時序**：Icon travel 22-30 f on E.smooth, scaling to about 0.42 (cap height). Words at icon landing + 2, + 6 and + 10 f, each a 14 f slide of 24 px with a 12 f colour resolve. Residual drift 0.5-1 px/f.
- **構建配方 (Recipe)**：Lay out the final line first with an empty inline slot one cap height square (inkBox gives the cap height, measureTracked the widths), and read the slot's rect. FLIP the hero from its centred rect to that rect with translate and scale on prog(f, a, a + 26, E.smooth), with motion blur while it exceeds 12 px/f; for extra life add a wobble of rotateY = sin(pi p) * 25 deg and rotateX = -sin(pi p) * 15 deg under perspective(800px). The words start behind the icon in z and spill outward: each word's translateX runs from -24 px to 0 over 14 f on E.out while its opacity rises and its colour moves from C.mute to C.ink through mixColor over 12 f. The first word starts 2 f after the icon lands and the rest follow 4 f apart; then the line drifts at 0.5 px/f.
- **適用時機**：Bridging from a hero object to a claim about it: an icon becoming the bullet of its benefit, a mark becoming the subject of a sentence, a feature glyph leading a metric line.
- **禁用避開**：Detailed icons that will not read at cap height (50-90 px), or sentences long enough to wrap.

#### `layout_and_composition` 完整技法清冊 (16 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `lc-swarm-cluster-burst` | Swarm, cluster and burst reveal | signature | high | About twenty cards or screenshots fly in from every edge, sw... |
| `lc-arc-carousel` | Arc carousel | signature | medium | A row of cards rides a wide smile-shaped arc across the lowe... |
| `lc-hero-flips-to-inline-glyph` | Hero icon becomes the inline glyph | accent | medium | The centred hero icon shrinks and travels into a slot at the... |
| `lc-headline-over-ghost-ui` | Headline over a ghost of the UI | accent | calm | A headline inks in from light grey to near-black while a fai... |
| `lc-icon-ragged-stack` | Icon-led ragged word stack | accent | medium | A short lead word is followed by three or four keywords on s... |
| `lc-hub-spoke-diagram` | Hub-and-spoke concept diagram | accent | calm | A central product tile sits inside two thin concentric rings... |
| `lc-mark-as-inline-word` | Mark set as a word | accent | calm | A logo, partner mark or icon sits inside a sentence on the b... |
| `lc-negative-space-caption` | Caption in the subject's negative space | workhorse | calm | Each camera move ends on a pose where the product covers abo... |
| `lc-opposite-corner-relay` | Opposite-corner caption relay | accent | calm | One caption fades out of one upper corner while the next sta... |
| `lc-one-centred-subject` | One huge centred subject | workhorse | any | Every frame has exactly one subject, centred and large: a si... |
| `lc-symmetric-flank` | Centre object with mirrored flanks | accent | medium | A narrow centre object (a phone-width window, a pill, a big ... |
| `lc-subtract-to-one` | Subtract to the one | workhorse | medium | A busy board loses its elements one by one until a single su... |
| `lc-gap-open-insert` | Words part for an inserted object | workhorse | medium | Inside a finished line, the words slide apart to open a gap ... |
| `lc-live-split-view` | Live cause-and-effect split | workhorse | calm | Two panels share the frame side by side, the cause on one si... |
| `lc-bento-cell-takeover` | Bento cell takes over the frame | signature | high | In a flush four-cell grid, one cell grows to fill the whole ... |
| `lc-vertical-band-stack` | Vertical clear-band stack | workhorse | any | In a 9:16 frame, the caption and the subject stack verticall... |

### 3.12 速度曲線與結構 (Pacing & Structure) — 共 23 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `pacing_structure`
- **核心導演準則**：Pacing is the shape of speed over time, and the strongest films control it at three scales. Per shot the shape is a U: arrive on E.out over 20-50 f, keep living through the hold at 0.3-1 px/f (no near-dead run longer than about 22 f), then accelerate over the last 18-24 f so the cut lands on the fastest frame at 17-38 px/f and the next shot opens already moving. Stillness is spent like money. One near-still hold of 60-90 f on the key claim, or a 12-15 f freeze on true silence before the lockup, reads as intent only because everything else moves. Per sequence, repetition teaches the viewer: a fixed 180 f ask beat with answers of varying length, a second instance at 0.6x length, phrase chunks landing one per beat. Per film, acts sit on the bar grid (a 30-60 s launch splits roughly 19/14/58/9%), stage polarity flips 3-5 times, and the score's arrangement follows the acts, with 12-24 f music holes before key statements and every slam within ±1 f of a picture event.

#### 核心精選技法深入配方

##### `ps-breath-envelope`：Breath envelope per card
- **角色 / 能量**：`workhorse` ｜ `medium` 能量
- **60 FPS 時間時序**：Arrival 20-50 f E.out (default 36, peak about 15 px/f). Hold = 36 f + 6 f per word at 0.4-1 px/f or +0.06%/f scale; the drift rate is never 0 for more than 6 f. Exit 14-20 f E.in, reaching 19-39 px/f on the cut frame. Example U: 14 then 3 then 39 px/f across 56 f. No near-still run over about 22 f before the end card.
- **構建配方 (Recipe)**：Drive each card's container with one summed transform of three terms. Arrival: tw(f, 0, 36, 90, 0, E.out) px of translate (or scale lmix(1.08, 1, prog(f, 0, 36))), with arrive() on vertical text moves and blurIn only while the card travels faster than 12 px/f. Hold: a linear drift of 0.4-1 px/f, or breath() from src/lib/camera.ts at about +0.06%/f, optionally with letter-spacing tightening 2-3% over 40 f on E.outSoft from the landing frame. Exit: tw(f, T-16, T, 0, 100, E.in) px (or +6% scale) with blurOut, and the hard cut on frame T, which is the exit's fastest frame. Because the terms add, speed follows a U (fast, slow, fast) and never touches zero mid-card; the hold length follows the copy rule (36 f + 6 f per word).
- **適用時機**：Statement cards, kinetic type and feature cards in a fast-cut film where nothing should ever look frozen.
- **禁用避開**：Dense UI that needs a dead-still read (lock the camera instead), and the final lockup hold.

##### `ps-locked-camera-holds`：Camera locks, the interface performs
- **角色 / 能量**：`workhorse` ｜ `calm` 能量
- **60 FPS 時間時序**：Holds 60-240 f (median about 150 f) at exactly 0 px/f; an in-frame event at least every 40 f; moves between holds 56-108 f E.cam; caption exit 26-28 f E.smooth, ending 0-56 f before the next move.
- **構建配方 (Recipe)**：Between poses, blend with lc(A, B, E.cam(p)) from src/lib/camera.ts. At each pose, hold the Shot exactly: no breath(), scale constant, 0.0 px/f. Schedule events from the move's end so that no gap between visible changes exceeds 40 f: the UI action at moveEnd - 10 f, the caption word reveal (src/fx/Words.tsx) at moveEnd - 0.25 * moveDuration, cursor travel (src/fx/Cursor.tsx) on E.glide. Ambient life lives only in the background, for example a single-hue wash breathing ±3% opacity on a 240 f sine. The caption leaves as one block, opacity on E.smooth over 26-28 f with no stagger, and is gone 0-56 f before the next move starts.
- **適用時機**：Dense product UI that must be read, walkthroughs, and films where every move should feel deliberate because it contrasts with stillness.
- **禁用避開**：Kinetic type or fast montages where a dead camera reads as a stalled player, or holds with nothing in the UI to animate.

##### `ps-one-long-hold`：The one long hold
- **角色 / 能量**：`accent` ｜ `any` 能量
- **60 FPS 時間時序**：Settle 20-36 f; hold 60-90 f at under 0.3 px/f; exit creep +6% over 18 f E.in. Every other near-still run stays at or under 30 f.
- **構建配方 (Recipe)**：Reserve exactly one statement per film for this. After it settles (words on SPR.word or src/fx/Words.tsx), hold it 60-90 f with the type effectively still: breath(t, 0.015-0.02) from src/lib/camera.ts on its container (under 0.3 px/f at the edges) and a background breathing ±3% opacity, with no new element entering. Every other shot keeps a breath envelope or a camera move, so this hold is at least twice as long as any other near-still stretch. Leave on an E.in scale creep of +6% over the last 18 f, cutting on the creep's fastest frame.
- **適用時機**：The single claim or number the film exists to say, in a launch film or short spot that is relentless everywhere else.
- **禁用避開**：Films already built on long holds, where it stops reading as special, or when two lines compete for the slot.

#### `pacing_structure` 完整技法清冊 (23 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `ps-breath-envelope` | Breath envelope per card | workhorse | medium | Every card arrives fast and decelerates, keeps moving gently... |
| `ps-locked-camera-holds` | Camera locks, the interface performs | workhorse | calm | After each move the camera stops dead, and for a 1-4 s read ... |
| `ps-one-long-hold` | The one long hold | accent | any | In a film that otherwise never stops, a single key claim sit... |
| `ps-silent-sign-off` | Hard stop into a silent sign-off | workhorse | high | Tension rises under the back half, the music stops dead on t... |
| `ps-four-sequence-launch` | Spectacle, diagram, walkthrough, sign-off | workhorse | medium | A launch film in four sequences: a short spectacle open, one... |
| `ps-image-act-then-type-act` | Image act, then type act | workhorse | medium | A short spot splits in half: the first half is pure imagery ... |
| `ps-luma-act-map` | Light and dark as chapters | workhorse | any | Acts are planned by stage polarity, dark for the abstract or... |
| `ps-oner-morph-chain` | Oner through a morph chain | signature | medium | The whole film plays as one continuous shot, every new scene... |
| `ps-single-camera-journey` | One camera journey across one surface | signature | calm | Every product state lives on one large surface and the film ... |
| `ps-continuity-thread` | Travelling thread object | signature | high | One small accent object (a dot, a packet or a streak) recurs... |
| `ps-faster-each-repeat` | Each repeat runs faster | workhorse | medium | The first instance of a repeated action plays at full length... |
| `ps-fixed-ask-variable-answer` | Fixed-length ask, variable answer | workhorse | medium | A demo repeats a fixed-length ask beat followed by a result ... |
| `ps-beat-quantized-chunks` | Phrase chunks on the beat | workhorse | medium | A line arrives in two or three chunks split by meaning, each... |
| `ps-empty-ground-after-cut` | Empty ground after a cut | accent | medium | Right after some hard cuts the new stage shows for two empty... |
| `ps-music-hole-slam` | Music hole, then slam on the cut | workhorse | high | The low end, or the whole bed, vanishes for a fraction of a ... |
| `ps-score-mapped-to-acts` | Score arranged to the acts | signature | any | The music's arrangement tells the story's structure: a spars... |
| `ps-silent-ui-steady-bed` | Silent UI over a steady bed | workhorse | high | In dense, fast-changing sequences the interface makes no sou... |
| `ps-accelerando-to-climax` | Accelerando into the climax | accent | high | Shot lengths shrink step by step toward the climax, then one... |
| `ps-loop-seam-on-motion-peak` | Loop seam hidden at a motion peak | workhorse | medium | A loop wraps around on the fastest frame of a whip or push, ... |
| `ps-silence-first-sound` | Silence as the default bed | signature | calm | There is no running music: most of the film is true silence,... |
| `ps-long-tail-beat-lengths` | Long-tailed beat lengths | workhorse | any | Beat lengths follow a long tail instead of an even grid: mos... |
| `ps-direction-per-act` | One screen direction per act | workhorse | medium | Each act owns one direction of travel, so every entrance, ex... |
| `ps-machine-grid-human-gaps` | Machine on the grid, hands off it | workhorse | medium | Work the product does (rows inserting, items stacking, text ... |

### 3.13 微互動與點擊響應 (Micro-interactions) — 共 20 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `micro_interaction`
- **核心導演準則**：A micro-interaction is the visible cause of a cut. The response starts on the press frame, never a beat later, and the result holds at least 36 f before the camera moves on. A press works as a light envelope, not a bounce: an accelerating attack of 8-12 f, a one-frame peak and a release about twice as long (tau about 8 f), with no scale overshoot, because spring overshoot is kept for true landings. Small elements get weight by deforming with speed. A tab pill whose leading edge arrives in 12 f and trailing edge in 20 f stretches to about 1.9x its width mid-travel, and a moving dot stretches to its rest length plus about 4-5 f of travel. A cursor arrives 6-12 f before it acts and the target shows its hover state about 4 f after arrival; the press goes down in 4 f and recoils in 8 f, with at most one click per 30 f at uneven gaps such as 4, 15 and 18 f. Keep sound sparse: about 6-8 dry ticks in 45 s, each on the frame its element reaches 50% opacity and 12-18 dB under the landing hit, stepping up about 3 dB per action only across a counted run.

#### 核心精選技法深入配方

##### `mi-focus-ring-pop-or-trim`：Focus ring: pop on click, trim to point
- **角色 / 能量**：`accent` ｜ `any` 能量
- **60 FPS 時間時序**：Pop: outset 4 to 14 px in 8 f E.out; opacity 0.9 to 0 over 20 f, linear from the press. Trim: draw 24 f and erase 24 f, both E.smooth (a 48 f loop); dashes 10/8 px, 3 px stroke; next target about 108 f later.
- **構建配方 (Recipe)**：Draw an SVG rounded rect around the control's bounds, with rx equal to the control radius plus the outset, a crisp 2-3 px stroke and no blur copy. Pop mode: on the press frame, grow the outset from 4 to 14 px with prog(..., E.out) over 8 f and fade the stroke from 0.9 to 0 linearly over 20 f. For a handoff, keep the ring at 14 px instead so it becomes the border of the next element (an alert card, or the frame of the next shot). Trim mode: 6 px outset, dasharray '10 8', masked by a second rect with pathLength 1 that shows only the run from tail to head (strokeDasharray `${h - t} 1`, strokeDashoffset -t). Here head = prog(f, s, s + 24, E.smooth) and tail = prog(f, s + 24, s + 48, E.smooth). Repeat on the next target about 108 f later while the cursor rests nearby. Use C.accent for the stroke only when the accent's one meaning is 'act here'; otherwise use C.ink on light stages and C.white on dark ones.
- **適用時機**：A click needs a visible result the next shot can build on, or a calm frame must point at the next action without moving a cursor.
- **禁用避開**：The cursor already sits on the target (the ring is redundant), or the ring would need a glow or blurred halo to read.

##### `mi-in-place-char-rewrite`：In-place character rewrite
- **角色 / 能量**：`accent` ｜ `medium` 能量
- **60 FPS 時間時序**：Overwrite at about 1 character per frame (13 characters in 12 f), linear, starting 8 f after the press peak. Redact: 1 f swap, then 1 dot deleted every 2 f; camera pan 40 f E.inOut.
- **構建配方 (Recipe)**：Set the field in FONT.mono with whiteSpace pre so every character keeps its column. Overwrite: k = fd(prog(f, s, s + 12, E.linear) * max(oldLen, newLen)) and text = next.slice(0, k) + prev.slice(k). Start it 8 f into the press release, so the status changes as the button's light fades. Optionally lift a companion icon 10 px over 4 f E.out and bring it back over 8 f. Redact: on the click frame, swap the value to '•'.repeat(n) in one frame, then set n = len - fd((f - s) / 2) so one dot deletes every 2 f. Meanwhile, an anchor-camera pan over 40 f E.inOut keeps the toggle icon centred; put the click on a downbeat.
- **適用時機**：The product's own status (sending, receiving, connected) or a privacy claim should change in place and read as the machine's voice.
- **禁用避開**：The text is decorative rather than real UI status (it becomes filler text), or the field uses a proportional face, so the columns jump.

##### `mi-anticipation-dip-unlock`：Anticipation dip before an unlock
- **角色 / 能量**：`signature` ｜ `medium` 能量
- **60 FPS 時間時序**：Build 14 f E.in to 1.5x. Dip 12 f E.out to 0.8x, with the shackle at -30 degrees. Pop 12 f (7 f on the repeat) with a hitPulse(t, 3, 6) brightness pulse and a 2.4% scale pulse. About 38 f in all.
- **構建配方 (Recipe)**：Drive the card wrapper's filter brightness through a tw chain: 1.0 to 1.5 over 14 f E.in (the build), then 1.5 to 0.8 over 12 f E.out (the dip). On the pop frame, swap the locked art for the clean art in one frame (decided with fd), hidden inside the brightness pulse, never crossfading the two. Set brightness to 1 + 0.35 * hitPulse(t, 3, 6) and scale to 1 + 0.024 * hitPulse(t, 4, 4): a pulse, not a spring. During the dip, rotate the shackle -30 degrees about its hinge (transformOrigin at the hinge point) with E.out and lift it 4 px. Repeat it faster on a second card (a 7 f pop instead of 12 f) so the second read is snappier, and put a 'pop' or 'snap' event on each pop frame.
- **適用時機**：Something locked, gated or hidden becomes available (an unlock, a reveal, access granted) and the moment should land as a payoff.
- **禁用避開**：The brightness would clip whites into a bloom, or the film already has two big payoff beats.

#### `micro_interaction` 完整技法清冊 (20 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `mi-focus-ring-pop-or-trim` | Focus ring: pop on click, trim to point | accent | any | A thin outline around a control either pops outward and fade... |
| `mi-in-place-char-rewrite` | In-place character rewrite | accent | medium | A small monospace status field is overwritten left to right ... |
| `mi-anticipation-dip-unlock` | Anticipation dip before an unlock | signature | medium | Light builds on a locked card, the card briefly darkens as t... |
| `mi-pre-event-tell` | One-element tell before the event | accent | calm | Just before a state change or a cut, exactly one small thing... |
| `mi-chip-bloom` | Chip bloom around content | workhorse | medium | A container grows out of its content: a dropped icon tile wi... |
| `mi-shape-handoff-morph` | Shape handoff: pill becomes the icon | signature | medium | A labelled capsule empties its text, then collapses at a fix... |
| `mi-guide-cursor-hover-press` | Guide cursor: arrive, hover, press | workhorse | any | A cursor travels a bowed path to the element about to act, t... |
| `mi-velocity-stretch-dot` | Velocity-stretch dot | signature | medium | A small round dot (a cursor or a list marker) stretches into... |
| `mi-shared-highlight-walk` | Shared highlight walks the menu | workhorse | calm | One rounded highlight slides from row to row of a sidebar or... |
| `mi-stretch-tab-indicator` | Stretchy tab indicator | signature | medium | The selected pill of a segmented control shoots to the new o... |
| `mi-radial-dash-burst` | Radial dash burst around a word | accent | high | Short dashes burst outward around a hero word on the beat, d... |
| `mi-launch-hop` | Launch hop that never lands | accent | medium | A centred app icon hops up as if launching, hangs at the top... |
| `mi-two-beat-confirm-cascade` | Two-beat confirm cascade | workhorse | calm | A row of buttons or toggles confirms one by one: the label o... |
| `mi-spinner-to-check` | Spinner resolves to a check | workhorse | calm | A working indicator (a rotating dashed ring in a step list, ... |
| `mi-send-ghost-handoff` | Send as a ghosted handoff | workhorse | calm | On send, the composer's text drifts up and fades away while ... |
| `mi-drag-lift-seat` | Drag, lift and seat | workhorse | medium | A chip or file picked up by the cursor lifts off the surface... |
| `mi-badge-count-bump` | Badge count bump | accent | medium | A notification badge or counter chip ticks up: the digit rol... |
| `mi-field-focus-caret` | Click to focus: I-beam, ring, caret | workhorse | calm | An arrow cursor turns into an I-beam as it enters an empty f... |
| `mi-cursor-glyph-context` | Cursor glyph follows context | workhorse | any | The pointer changes shape with what it is over, as a real sy... |
| `mi-drag-select-highlight` | Drag-select snaps glyph by glyph | accent | calm | An I-beam presses at the start of a phrase and drags across ... |

### 3.14 景深與空間 3D (Depth & 3D) — 共 14 種

- **來源路徑**：`skills/cinetic/assets/library/techniques.json` -> `depth_and_3d`
- **核心導演準則**：Depth looks expensive only when it is physical and used sparingly. Use one rotation axis per act and perspective of 1800-2600 px for UI planes (about 3-4x the object's width for a small icon or coin), and tilt live components that have their own shadow and ground, never tilted screenshots. Most moves here are short and offset, not simultaneous: flips run 10-12 f, a tilt resolves over 20 f starting 6 f before the position settles, an unfold takes 24 f, and the state change lands on the edge-on or peak-tilt frame. Long moves (de-skews of 81 f, dollies of 60-68 f) ride E.cam or E.rest so they start gently and settle slowly. Keep speed honest: E.out puts about 5.5x its mean speed into the first frame (E.in into the last), so cap travel to keep peaks near 70 px/f and let the master's sub-frame blur carry anything over 12 px/f. Chromium decides the finish: keep roll outside the tilt and at most 11 deg, sort layers by z yourself (overflow, opacity and filters flatten preserve-3d), lay text out at shot scale with CSS zoom, and rack depth of field with RackFocus copies, never an animated filter blur.

#### 核心精選技法深入配方

##### `d3-card-fan-bury-scatter`：Card fan that buries, then scatters
- **角色 / 能量**：`signature` ｜ `high` 能量
- **60 FPS 時間時序**：Per card 50 f on E.outSoft, starts 2 f apart (22 f span): the fan covers 50% of its final area by f6, 90% by f26 and all of it by f50 (peak about 62 px/f). Drift 84 f at 0.2-0.5 px/f plus breath +2%. Scatter 26 f on E.in, peak about 75 px/f (master motion blur). The hero figure locks 4-6 f after the last card clears.
- **構建配方 (Recipe)**：Place N = 12 card divs along a cubic bezier from two opposite corners toward the centre (sample it with getPointAtLength from @remotion/paths). Card i gets rotateZ = the path tangent, rotateY = 35 - 4i deg, rotateX = 18 deg and translateZ = -60i px inside one perspective(2000px) stage; the shot clips with overflow hidden, which flattens preserve-3d, so sort the cards by z yourself before rendering. Each card flies from just beyond the corner (travel at most about 700 px) to its slot on E.outSoft with start offsets stagger(i, 12, 22), then the whole fan drifts 15-40 px and breathes +2% on E.smooth. The hero card sits small and lowest in z at frame centre from the start. The scatter moves every fan card 340 px outward along its own radial vector while translateZ rises +700 px (about x1.5) on E.in, so they leave by scale and travel and uncover the hero card, whose figure then locks (Roll or Words). Card faces use a single-hue tonal ramp (dark to light of one colour, as a dithered PNG) so the repetition reads as one material.
- **適用時機**：A big count or scale claim (cards issued, transactions, users) needs to feel physical before it collapses to one legible number.
- **禁用避開**：The film already has a card or tile swarm, or the stat must be read at once; in a calm film the 50 f bury is too loud.

##### `d3-pinned-label-world-swap`：Pinned label over a swapping world
- **角色 / 能量**：`accent` ｜ `medium` 能量
- **60 FPS 時間時序**：Pin 8 f E.out; leader 8 f from +4 f; name 25 px over 12 f E.out from +12 f; orbit yaw 0.1-0.2 deg/f E.linear. 3D segment about 90 f, flat segment about 70 f; cut on the zoom's velocity peak, zoomHandoff settle 30 f. Flat-to-3D: 8x to 1x over 18 f E.out (fastest per-frame ratio about 0.65 at frame 2), settled by f22.
- **構建配方 (Recipe)**：Keep two layers: the world (a pre-rendered 3D plate played with OffthreadVideo, or a CSS 3D stage whose container uses transformOrigin 0 0) and a screen-space overlay. Every frame, project the pin's world point with the same matrix the world uses: new DOMMatrix(cameraTransformString).transformPoint(new DOMPoint(x, y, z)), then divide x and y by w (or do the rotateX, rotateY and perspective divide by hand as references/camera.md describes). Place the overlay with one translate() and add skewY of about 0.15x the camera yaw so the tag leans with the ground. The pin scales 0 to 1 on E.out over 8 f with a ring of hitPulse(t, 2, 6), the leader line draws by stroke-dashoffset over 8 f from +4 f, the mono tag (a value or status, not a decorative kicker) types on with TypeOn, and the place name slides 25 px on E.out over 12 f from +12 f. For the swap, cut only the world layer on the velocity peak of a pull-back and continue the zoom with zoomHandoff (in the flat map the same point sits about 1.8x larger and keeps shrinking, decelerating) while the overlay keeps animating untouched; the flat-to-3D version cuts a shrinking flat mark to its 3D twin at the same screen position, starting 8x large and pulling back on E.out.
- **適用時機**：Location or geography matters ('this happens in a real place'), or a flat diagram should be revealed as a real object, and back.
- **禁用避開**：There is no real 3D plate or scene to anchor to; a tag floating over a flat screenshot gains nothing from projection.

##### `d3-spotlit-tilted-object`：Tilted object on a spotlit ground
- **角色 / 能量**：`workhorse` ｜ `calm` 能量
- **60 FPS 時間時序**：Shot 30-84 f. Drift 0.5 px/f E.linear (eased in from rest over about 60 f at a seam), plus yaw 0.03 deg/f or an orbit of 0.1 deg/f. Pool radius about 35-40% of the frame. Content state changes over 10-14 f on E.ui.
- **構建配方 (Recipe)**：Stage on ink. Put a ground plane (a bezel slab, a tile or rib pattern, or a rect one step lighter than the stage) under the object at the same rotation, and transform both with perspective(2200px) rotateZ(4deg) rotateX(8deg) rotateY(-12deg), so the roll stays outside the tilt. The light is a dithered PNG of a single-hue radial falloff (white at 12% alpha down to 0 at 60% radius, centred at 60%/55% of the frame) over ground and object, plus a 35-40% edge vignette; the object casts a soft contact shadow (blur 36 px, alpha 0.35) offset away from the pool's centre. The pool stays fixed in screen space while the object drifts translateX -0.5 px/f and yaws +0.03 deg/f (or orbits at 0.1 deg/f for a device), so the highlight travels across its surface; start the drift from rest at a seam with the camera.md drift formula. Fill the card solid, never frosted, and let its content change state on E.ui while the plane drifts.
- **適用時機**：A single notification, card or device should feel like an object in a room, not on a slide, especially in a dark, low-key film.
- **禁用避開**：The same act already tilts things on this axis, or the film is bright and flat; never on a bare screenshot without ground and shadow.

#### `depth_and_3d` 完整技法清冊 (14 項)

| 技法 ID | 技法名稱 | 角色 (Role) | 能量 (Energy) | 摘要說明 |
| :--- | :--- | :---: | :---: | :--- |
| `d3-card-fan-bury-scatter` | Card fan that buries, then scatters | signature | high | A dozen identical cards swoop in from two corners along a cu... |
| `d3-pinned-label-world-swap` | Pinned label over a swapping world | accent | medium | A pin pops on a 3D-rendered place and a short data tag on a ... |
| `d3-spotlit-tilted-object` | Tilted object on a spotlit ground | workhorse | calm | A real card or device lies in perspective on a dark surface ... |
| `d3-orbit-ring-collapse` | Depth orbit ring that collapses into the mark | accent | medium | Small icons orbit the central mark on a tilted ellipse: they... |
| `d3-fold-out-channel` | Folded channel that unfolds flat | accent | medium | A wide card starts bent into a U-shaped channel with its sid... |
| `d3-flip-face-swap` | 3D flip that swaps state | workhorse | medium | An icon or card turns over in 3D and comes back around chang... |
| `d3-peek-launch-recede` | Peek, hover, launch and recede | accent | high | A device or product panel barely rises from the bottom edge,... |
| `d3-coin-edge-to-face` | Edge-on sliver snaps face-on | accent | medium | A thin edge-on sliver snaps open into a full face-on coin or... |
| `d3-extruded-slab-orbit` | Product on a thick extruded slab | workhorse | medium | The live interface sits on the front of a thick matte slab w... |
| `d3-impact-morph-stretch` | Impact morph with stretch and floor ripple | signature | high | Something accelerates into a 3D tile. On contact the tile sw... |
| `d3-icon-lift-to-hero` | Icon lifts out of its row into a 3D hero | signature | medium | A small icon tile peels out of a settings row and inverts fr... |
| `d3-cube-turn-face` | Cube turn to a blank face | accent | medium | Words converge and slide under an icon, then the icon turns ... |
| `d3-press-tilt-swap` | Press tilt that hides a swap | accent | calm | A card tips in 3D toward the point that was clicked or tappe... |
| `d3-exploded-layer-stack` | Exploded layer stack | accent | medium | A live UI component turns to a three-quarter view and separa... |

---

## 4. 雙渲染引擎適配指南 (Dual Rendering Engines)

Cinetic 支援兩套代碼驅動視訊渲染架構：

### 4.1 Remotion 引擎 (React-Based)
- **來源路徑**：`skills/cinetic/references/remotion-engine.md`
- **核心哲學**：利用 React 的組件樹與 `const frame = useCurrentFrame()`。
- **優勢**：極度適合直接複用現有的 React / Tailwind Web 元件庫，無縫渲染高保真 SaaS / Dashboard 介面。

### 4.2 HyperFrames 引擎 (HTML + GSAP)
- **來源路徑**：`skills/cinetic/references/hyperframes-engine.md`
- **核心哲學**：純 HTML/CSS 搭配 GSAP `timeline({ paused: true })`。
- **同步機制**：在渲染迴圈中根據當前影格強制執行 `timeline.seek(frame / fps)`，兼具 GSAP 強大時間軸補間與逐幀確定性渲染。

---

## 5. 動態防罐頭戒律 (Motion Anti-Slop Discipline)

- **來源路徑**：`skills/cinetic/references/taste-and-slop.md` 與 `skills/cinetic/references/craft-rules.md`

1. **嚴禁無物理起因的鏡頭漂浮 (No Drift Without Cause)**：鏡頭運動必須伴隨使用者操作（點擊、滾動、切頁）或視線引導，禁止無意義的全景慢速旋轉漂浮。
2. **文字排版絕對禁止彈簧亂晃 (No Type Springs)**：文字入場必須使用 `SPR.calm` 或 `E.out`，嚴禁對文字使用帶有 Overshoot 彈跳的彈簧（如 `SPR.pop` 或 `SPR.land`），確保文字立即可讀。
3. **切鏡必有動量接力 (Velocity Handoff Across Cuts)**：轉場不可直接死切，前一個鏡頭的位移方向與速度，必須在切鏡後的下一個元件上延續。
4. **保持足夠的閱讀定格時間 (Respect Reading Holds)**：文字在屏幕上的停留時間必須滿足生理閱讀時間（每行英文至少 24~36 幀，標題至少 45 幀），禁止剛出現即消失。
