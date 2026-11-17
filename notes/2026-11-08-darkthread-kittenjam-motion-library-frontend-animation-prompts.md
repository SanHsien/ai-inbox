---
id: 2026-11-08-darkthread-kittenjam-motion-library-frontend-animation-prompts
title: "黑暗執行緒推薦「Motion Library 動態收藏」：300 多種網頁特效的 AI 提示詞庫、CSS/GSAP 實作與 Agent Skill 整合評估"
source_url: "https://www.facebook.com/share/p/1CSB7d1YQh/"
source_platform: "Facebook (黑暗執行緒 @darkthread.net) / GitHub"
author: "黑暗執行緒 (@darkthread.net) 轉介 / 原站策展 Hannah (@hannahchao)；#001–075 效果參考自 @ai_yunon_ai 與 @ai_tjb"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: archived
cluster: "2"
cluster_role: "前端動態與提示詞工程"
short_title: "Motion-Library網頁動效庫"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 1
source_replies: 32
tags:
  - motion-library
  - frontend-animation
  - darkthread
  - css-keyframes
  - gsap
  - prompt-engineering
  - agent-skills
  - anti-slop
---

# 黑暗執行緒推薦「Motion Library 動態收藏」：300 多種網頁特效的 AI 提示詞庫、CSS/GSAP 實作與 Agent Skill 整合評估

- **來源貼文**：[Facebook 黑暗執行緒貼文（`1675948690568224`）](https://www.facebook.com/share/p/1CSB7d1YQh/)
- **原作網站**：[Motion Library 動態收藏（`kittenjam-motion-library.vercel.app`）](https://kittenjam-motion-library.vercel.app/)（策展作者：Hannah，UI/UX Designer，[作品集](https://hannahchao-portfolio.vercel.app/)）
- **社群衍生倉庫（主動深挖補齊；yazelin 無 LICENSE，hevangel 為 MIT，但內容源自原站，授權以原作者為準；2026-11-14 以 GitHub API 查證）**：
  - [`yazelin/kittenjam-motion-library-mirror`](https://github.com/yazelin/kittenjam-motion-library-mirror)：原站每日快取鏡像（GitHub Pages）、`effects.json`、`llms.txt`，以及零依賴 Python 查詢工具與 Agent Skill（`skills/motion-library/`）。
  - [`hevangel/motion-library-prompts`](https://github.com/hevangel/motion-library-prompts)：全量 327 種動效逆向萃取庫，提供 `prompts.json`、`prompts.md`、`prompts.csv`、中英雙語對照檔與單檔範例目錄（`examples/`）。
- **分析日期**：`2026-11-08`
- **分析者**：`Antigravity`
- **當前狀態**：`📁 歸檔備查 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-17-tasteskill-v2-anti-slop-frontend.md`](./2026-10-17-tasteskill-v2-anti-slop-frontend.md)（TasteSkill v2 藝術指導與反 AI Slop 前端）
  - [`notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md`](./2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md)（前端設計五件套與反 AI Slop 規則）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看 Facebook 貼文：貼文文字、連結預覽圖 1 張（放大看過）、留言 22 則（貼文標示共 33 則；Facebook 在「最相關」排序下過濾掉部分回覆，其餘未登入看不到）。另開原站首頁核對數量。
> 2026-11-17 登入補讀：改用「所有留言」排序、回覆串全部展開，讀到 32 則；貼文標示 33 則，差 1 則平台不顯示。

- **作者圖片**：圖 1 是原站首頁截圖（連結預覽）。可讀到三件事：(1) 站名是「Hannah's Motion Library」，當時寫「目前共 331 種」；(2) 置頂說明寫明 **#001–040 文字效果參考 @ai_yunon_ai 的「40 種文字動態效果」、#041–075 參考 @ai_tjb 的貼文，名稱與描述來自原作者整理，預覽動畫是重新製作的示意**，之後收錄的效果若參考他人會在卡片標「參考自」；(3) 各分類數量（文字 106、按鈕 21、卡片・群組 41…）與卡片上的「複製 AI 提示詞」按鈕。
- **作者留言補充**：黑暗執行緒在留言回覆 3 則，都是閒聊（回應「十年前該學 JavaScript」的話題、向原站作者致謝），沒有補充連結或勘誤。
- **網友留言重點**：
  - **原站作者現身**：帳號「趙小貓」在留言自述是這個網站的作者本人，並說當週被資遣（回覆「這是否也打擊到 UI/UX 設計師」的提問）；黑暗執行緒回覆致謝。這是作者自述，未另外查證。
  - **實測負評**：YoCheng Chang 說實際用起來不算好用，產一個效果很花時間、成效不一定滿意，AI 還常搞錯、產出圖檔而不是動畫文字。
  - **用法建議**：Ivy Charlotte 說直接把網站網址交給 AI（29 讚）；Yich Lin 分享先叫 AI 產十種風格的 mock 再挑幾個延伸；KY Lau 希望有 MCP 可直連（社群的 `yazelin` 鏡像已提供查詢工具與 Skill，見下方）。
  - 其餘是對「AI 生成設計有 AI 味、罐頭會不會貶值」的討論，沒有可查證的新事實。
  - 2026-11-17 補讀到的：
    - **負評有人反駁**：`Rossi Aaliyah` 回 `YoCheng Chang` 說是用法不對，這些提示詞是搭配 HyperFrames、Remotion 這類以程式產生影片的工具用的。這是留言者的說法；原站卡片寫的是「複製 AI 提示詞」，沒有指定工具。
    - `莊念迪`：還能自動依自己網站的配色調整。`Pulipuli Chen`：看起來像動態歌詞 MV 會用的特效。
    - `趙小貓` 的第二則回覆是感謝與宣傳自己的其他設計商品，與動效庫無關。
    - `Chen Qianxiang`、`陳猴子`、`張清忠` 等是前端從業者談工作受衝擊，沒有技術資訊。
- **對分析的影響**：
  1. **數量更正**：原筆記標題與內文寫「327 種」，那是衍生倉庫當時萃取到的數量。原站貼文當時自述 331 種，2026-11-16 實際開站為 335 種（文字 106、按鈕 22、表單・控制項 17、卡片・群組 44、圖片・媒體 22、圖形・SVG 35、背景・氛圍 36、版面・頁面 37、游標 16）。標題改為「300 多種」，第 2 節補上原站數字並註明 2.1 的統計表是衍生倉庫的舊快照。
  2. **出處補正**：原筆記把全部效果都歸給 Hannah 策展。依原站置頂說明，前 75 種的名稱與描述來自 @ai_yunon_ai 與 @ai_tjb，Hannah 重做預覽動畫並標示出處。已改作者欄，並在第 5 節授權提醒加上這一層：提示詞文字的原始出處不只原站一人。
  3. **實用性評價降一級**：原結論只寫「優質參考資源」。加上留言的實測負評後，改寫為「當作描述動效的詞彙表有用，但提示詞貼給 AI 不保證一次做對」。
  4. 仍維持歸檔、不開任務。
  5. 2026-11-17 補讀：第 3 點的負評現在有一則反駁（要搭配程式化影片工具用）。兩則都是單一使用者的說法、都沒有附實測結果，所以「提示詞貼給 AI 不保證一次做對」的寫法維持，另補一句「效果好壞看接的是哪一種產出工具：做網頁動效與做影片是兩回事」。`Pulipuli Chen` 的觀察（像動態歌詞特效）與此同向。其餘 9 則沒有新資訊。

---

## 1. 核心內容摘要：前端工程典範轉移與痛點還原

黑暗執行緒貼文指出：
> 「前端設計這一行被 AI 無情爆破，知道網頁怎麼寫已失去價值，知道網頁能怎麼設計丟給 AI 寫，才是這個時代值錢的本事。無意滑到大祕寶 - 收藏超過 300 種網頁特效，一鍵複製提示詞，想要什麼叫 AI 生給你~」

這段話精準揭示了目前 AI 輔助前端開發的深層瓶頸：

```
+-----------------------------------------------------------------------------------+
|                        AI 前端開發的「動態詞彙量貧乏」陷阱                        |
+-----------------------------------------------------------------------------------+
| 傳統指令困境:                                                                     |
|   使用者:「幫我做一個酷炫的進場動畫」                                            |
|   AI 模型: (由於提示詞欠缺具體物理隱喻與時間參數，只能調用機率最高的安全解)       |
|            -> opacity: 0 -> 1; transform: translateY(20px); (標準 AI Slop 平庸感) |
+-----------------------------------------------------------------------------------+
| Motion Library 的解法:                                                            |
|   1. 參數化詞彙庫: 300+ 種具名特效 (雷射切斷 / 亂碼解讀 / 錯誤震動 / 指紋掃描)   |
|   2. 明確時間與節奏: 標明秒數 (0.45s / 2.4s)、貝茲曲線與多階段 Keyframes          |
|   3. 設計系統解耦: 強制後綴「配色請依照網站既有主題色自行搭配，不要指定顏色」     |
+-----------------------------------------------------------------------------------+
```

---

## 2. 結構化分類體系（Taxonomy）與規模分析

原站貼文當時自述收錄 331 種（貼文預覽圖），2026-11-16 開站為 **335 種**，仍在增加。衍生倉庫 `hevangel/motion-library-prompts` 於本筆記初次分析時萃取到編號 1–331、其中 225, 259, 300, 303 四個 ID 抓不到，共 327 種；下表是那份快照的統計，與原站現況略有出入（例如原站文字類為 106、卡片・群組為 44）。

### 2.1 四大向度統計

| 向度 | 類別與數量分佈（衍生倉庫快照，327 種） |
| :--- | :--- |
| **元件 (Components)** | 文字 `text` (105) / 卡片群組 `card` (39) / 版面頁面 `layout` (37) / 背景氛圍 `bg` (36) / 圖形SVG `shape` (35) / 按鈕 `button` (21) / 圖片媒體 `media` (21) / 表單控制項 `control` (17) / 游標 `cursor` (16) |
| **時機 (Timing)** | 循環待機 `loop` (98) / 懸停點擊 `hover` (95) / 進場 `enter` (75) / 切換 `switch` (60) / 捲動觸發 `scroll` (34) / 退場 `exit` (22) / 拖曳手勢 `drag` (12) |
| **情境 (Uses)** | 介面互動 `ui` (146) / 標題Hero `hero` (110) / 強調重點 `emph` (60) / 背景裝飾 `bg` (59) / App介面 `app` (56) / 轉場切換 `trans` (43) / 數字資訊 `data` (43) / Logo品牌 `logo` (28) / 捲動效果 `scroll` (28) |
| **技術 (Tech)** | 純 CSS Keyframes (194) / GSAP Timeline (119) / HTML5 Canvas 2D (14) |

### 2.2 特效代表案例解析

1. **文字類（CSS - 001 閃電砸落 Lightning Strike）**：
   - *提示詞*：畫面先閃兩下強光並出現一道閃電線，文字從 2 倍大瞬間砸下縮回原尺寸，落地時輕微震動，之後保持柔和的外發光。整段約 2.4 秒，節奏急促有爆發力。
   - *技術實現*：利用 SVG polyline 繪製折線閃電，配合 CSS keyframes 控制 `transform: scale(2) -> scale(1)` 與震動位移。
2. **控制項類（CSS - 151 錯誤震動提示 Shake on Error）**：
   - *提示詞*：登入時密碼錯誤，輸入框左右快速震動幾下（像搖頭說不，約 0.45 秒，幅度由小到大再變小），邊框同時切換成錯誤提示色，下方的錯誤訊息從上方 4px 淡入滑出；修正輸入後邊框與訊息恢復。
   - *技術實現*：`cubic-bezier(.36,.07,.19,.97)` 的 `translateX` 衰減震盪，搭配 `navigator.vibrate` 行動裝置觸覺回饋。
3. **圖形/SVG類（GSAP - 331 指紋掃描解鎖 Fingerprint Scan）**：
   - *提示詞*：手機指紋解鎖畫面：圓角方形感應區中，指紋的弧線紋路由內而外一圈圈依序畫出；接著一條發光的掃描光條由上往下、再由下往上掃過，下方文字顯示「掃描中…」；掃描完成後指紋紋路變淡，一個粗勾勾快速畫出，感應區外框發出光暈，文字變成「驗證成功」。
   - *技術實現*：GSAP Timeline 串聯 DrawSVG 插件，控制多道 SVG 路徑的 `strokeDashoffset` 逐層顯現與光暈動畫。

---

## 3. Agent Skill 架構化整合方式

若將這 300 多種效果的提示詞或程式碼硬塞進 Prompt 或 Context，將耗損大量 Token 且容易造成模型幻覺。社群專案 `yazelin/kittenjam-motion-library-mirror` 示範了極佳的 Agent Skill 整合設計：

```text
┌───────────────────────────────────────────────────────────────┐
│              Agent Skill 零 Token 過濾與調用架構               │
└───────────────────────────────────────────────────────────────┘

       Coding Agent (Antigravity / Claude / Codex)
                           │
           1. 搜尋特定動態 (在 Context 外執行)
                           ▼
     [ python motion.py search button hover ]
                           │
           2. 輸出符合的 ID 清單 (精簡 2~3 行)
                           ▼
     [ 142 磁吸按鈕 / 151 錯誤震動 / 189 懸停波紋 ]
                           │
           3. 僅取出單一目標的確定性規格
                           ▼
     [ python motion.py show 151 ]
                           │
                           ▼
   輸出: 準確提示詞 + 原生 CSS Keyframes / GSAP 原始碼
                           │
                           ▼
     Agent 快速對齊專案既有 Design Tokens 完成實作
```

### 3.1 核心檔案與介面

- **資料層**：`effects.json`（結構化收錄 `id`, `zh`, `en`, `desc`, `comp`, `when`, `tech`, `uses`, `prompt`, `copy_prompt`）。
- **工具層**：`motion.py`（純 Python 3 標準函式庫，無第三方依賴，支援多關鍵字交集檢索與格式化印出）。
- **規範層**：`llms.txt`（提供 AI 可直接理解的站點目錄與 API 入口）。

---

## 4. 前端設計防線整合架構

本資源與本庫現存的前端設計防線形成完整互補：

| 防線層級 | 負責工具 / 規範 | 核心職責 |
| :--- | :--- | :--- |
| **宏觀藝術指導** | [`TasteSkill v2`](./2026-10-17-tasteskill-v2-anti-slop-frontend.md) | 主體資產清單、爭點論證寫作、整體版面構成、3 寬度瀏覽器截圖審查。 |
| **負向約束守門** | `epstein.md` / `pbakaus/impeccable` | 攔截 Inter 字體濫用、藍紫漸層、過度圓角與無意義卡片套卡片。 |
| **微觀動效積木** | **`Motion Library`（本筆記）** | 提供 300 多種具備明確物理隱喻、時間軸刻度與 CSS/GSAP 原生實作的動態元件。 |

---

## 5. 評估結論與處置

1. **實用性判定**：
   - 本庫當作「描述動效的詞彙表」有用，解決了工程師「想加動畫卻不知如何精確描述物理特性與時間軸」的痛點；但留言有實測回報指出，把提示詞貼給 AI 不保證一次做對（耗時、成效不穩、有時產出圖檔而非動畫），採用時要自己在瀏覽器驗收。
   - 提示詞尾部強制帶入「配色依照既有主題色」的解耦設計，對保護現有 Design Tokens 具高度借鏡價值。
2. **任務處置**：
   - 經評估，社群已具備完整靜態站點、中英雙語 JSON 萃取庫（`hevangel/motion-library-prompts`）與零依賴查詢工具（`yazelin`）。
   - 本機目前無需維護額外專用伺服器或鏡像，在需要前端動效設計時直接查閱本筆記與對應衍生倉庫即可（授權風險：內容源自原站，yazelin 倉庫無 LICENSE、hevangel 的 MIT 不代表原站內容可任意再利用，商用或轉載前先確認原作者授權；且原站前 75 種效果的名稱與描述另參考自 @ai_yunon_ai 與 @ai_tjb，出處不只一人），**歸檔備查（`status: archived`），不衍生獨立代碼任務**。
