# AI 影片電影級鏡頭語言與分鏡 Prompt 工程指引

> 任務：`T-20261026-14`｜來源筆記：[`notes/2026-10-26-cinematic-ai-video-reference-pipeline.md`](../notes/2026-10-26-cinematic-ai-video-reference-pipeline.md)（原文為 Threads 貼文，作者玖桃 `@xbox002000`；以下凡寫「作者宣稱」者未獨立重現）
> 配套範本：[`templates/cinematic-storyboard-template.md`](../templates/cinematic-storyboard-template.md)｜查證日期：2026-10-26
> **實測聲明**：本文沒有對任何影片生成模型做對照生成實驗。表中的光學詞是「攝影語義錨點」，模型是否照物理規律反應、反應多強，**未實測**，各模型與版本不同。請用自己的模型小批量試跑再調整。

---

## 1. 要解決的問題與核心做法

作者的觀察（原文稱）：多數 AI 影片看起來像「公司尾牙簡報」，因為 Prompt 只用空泛形容詞。本文的做法是把每個形容詞換成**可以拍出來的東西**：一個焦段、一個光圈、一種光源、一個機位或運鏡、一個調色參考。

```text
 空泛形容詞 Prompt                      電影語言 Prompt
 "cinematic, 8k, dramatic"      ──▶     [主體] + [景別與機位] + [焦段/光圈/片幅]
 （無法驗證、模型自行猜）                 + [光源與方向] + [運鏡與速度] + [調色/底片]

 流程：
 找參考靜幀 ──▶ 拆出 5 個屬性 ──▶ 套第 6 節規則 ──▶ 寫成分鏡 ──▶ 小批量試跑 ──▶ 回頭改詞
 (第 2 節)      (景別/焦段/光/色/動)  (黑名單+六要素)   (範本檔)      (自己的模型)
```

---

## 2. 六大參考資料庫：怎麼檢索、對應到哪個 Prompt 欄位

下表「可檢索維度」是 2026-10-26 查證到的現況（各站首頁或第三方介紹），會變動；筆記中的片數規模（「上萬部」「數萬張」）為作者宣稱，未查證。

| 站 | 網址 | 可檢索維度（已查證） | 拿來填 Prompt 的哪一欄 |
| :--- | :--- | :--- | :--- |
| Shot Cafe | <https://shot.cafe> | 電影與廣告靜幀；依導演、攝影指導、美術指導、年份、類型、標籤、顏色、畫幅瀏覽；鏡頭屬性含日/夜、內/外景、黑白，景別標籤含 extreme wide、wide、medium wide、medium、medium close-up、close-up、extreme close-up、over-the-shoulder、two-shot、insert、profile、establishing、low-angle、high-angle、dutch-angle、top-down、overhead、aerial。**首頁未列焦段篩選** | 景別、機位 |
| Film-Grab | <https://film-grab.com> | 依片名 A–Z、導演／攝影指導／美術指導／服裝設計師、畫幅、國家、類型、年份瀏覽；首頁未見標籤篩選 | 調色參考圖（找「某攝影指導的某部片」） |
| Eyecandy | <https://eyecannndy.com> | 以「技法」分類的視覺技法庫（如 dolly、zoom、transition、split diopter、match cut），每個技法附範例（自動抓取受限，內容來自搜尋結果摘要，**建議親自開站確認**）；不是靜幀資料庫，沒有焦段篩選 | 運鏡名稱與寫法 |
| ShotDeck | <https://shotdeck.com> | 由攝影指導 Lawrence Sher 發起（[CineD 報導](https://www.cined.com/shotdeck-collaborative-searchable-online-library-movie-images-lawrence-sher-asc/)）；每張圖有 50+ 關鍵字；篩選含顏色、畫幅、光學格式、沖洗流程、片幅、日夜、鏡頭焦段、使用機型等（第三方介紹）；付費，有試用（價格未查證） | 焦段、機型、片幅、底片流程 |
| Flim | <https://flim.ai> | 自稱「AI search engine for film stills and visual references」；涵蓋電影、MV、廣告；首頁可見主題標籤（如 Noir、Giallo）；**顏色／情緒／自然語言查詢的具體能力，首頁未載明** | 用文字反查氛圍 |
| Frameset | <https://frameset.app> | 商業廣告、MV、電影靜幀與動態；篩選含顏色、畫幅、飽和度、色溫、日夜等（第三方介紹）；搜尋免費，付費方案價格未查證 | 色溫、飽和度、廣告節奏 |

> 自動抓取 Eyecandy、ShotDeck、Frameset 首頁時回 403，上表這三站的內容來自搜尋結果摘要與第三方文章，不是直接讀站內頁面。

**使用流程（每個鏡頭）**：

1. 在 Shot Cafe／ShotDeck 用景別與類型找 1～3 張最接近的靜幀。
2. 讀出五個屬性：景別機位、焦段／光圈（ShotDeck 有就用，沒有就從景深與透視推估）、光源方向與軟硬、主色與對比、有無運鏡（Eyecandy 查名稱）。
3. 把五個屬性寫進第 7 節的分鏡範本，**文字描述屬性，不貼原圖**。
4. 本 repo 不存電影靜幀原圖（版權），只存連結與屬性描述。若你的模型支援以靜幀做圖生影片條件，原圖僅供個人 moodboard 與私下實驗，公開發布前自行評估授權；本文不提供法律意見。

---

## 3. 光學參數對照表

「焦段」以全片幅等效為準。右欄是**攝影常識**，不是對 AI 模型的保證。

### 3.1 焦段與視角

| 焦段 | 視覺特徵（攝影常識） | 適合鏡頭 | Prompt 寫法 |
| :--- | :--- | :--- | :--- |
| 14–24mm 超廣角 | 空間誇張、邊緣拉伸、近大遠小明顯 | 建築、狹小空間、動作的臨場感 | `24mm wide-angle lens, exaggerated foreground, converging lines` |
| 28–35mm 廣角 | 帶環境的人物、透視自然偏張力，紀實與劇情片常用 | 中景對話、跟拍 | `35mm lens, subject within environment, slight perspective depth` |
| 50mm 標準 | 接近一般所說的人眼視角，壓縮與變形都小 | 中性敘事、桌邊對話 | `50mm lens, natural perspective` |
| 85mm 中望遠 | 臉部比例好看、背景明顯虛化、輕度壓縮 | 人物特寫 | `85mm lens, subject isolation, compressed background` |
| 135mm 以上 | 強烈壓縮、背景被拉近、景深極薄 | 偷拍感、街景疊層 | `135mm telephoto, strong background compression` |

### 3.2 光圈、快門、畫幅

| 參數 | 數值 → 效果 | Prompt 寫法 |
| :--- | :--- | :--- |
| 光圈 f/1.4–f/2 | 景深極淺，背景融化，焦外光斑大 | `shallow depth of field, f/1.8` |
| f/2.8–f/4 | 景深中等，主體與近景皆可辨 | `moderate depth of field, f/4` |
| f/5.6–f/8 | 環境大致清晰，適合群像 | `deep focus, f/8` |
| f/11 以上 | 全景深，前中後皆清晰 | `deep focus, everything sharp` |
| 快門角 180°（24fps 即 1/48 秒） | 標準電影動態模糊 | `24fps, 180-degree shutter motion blur` |
| 快門角較窄（如 90°） | 動作顆粒分明、模糊少，戰爭／動作片常用的手法 | `narrow shutter angle, crisp staccato motion` |
| 畫幅 2.39:1／1.85:1／4:3 | 寬銀幕／平台標準／近方形 | `2.39:1 anamorphic widescreen`、`4:3 Academy ratio` |
| 變形寬銀幕鏡頭 | 橢圓焦外光斑、橫向光暈 | `anamorphic lens, oval bokeh, horizontal lens flare` |

### 3.3 光源模型

| 名稱 | 描述 | Prompt 寫法 |
| :--- | :--- | :--- |
| Rembrandt 光 | 側前方硬光，暗側臉頰出現三角光斑 | `Rembrandt lighting, triangle of light on shadow-side cheek` |
| Chiaroscuro | 強烈明暗對比，大面積深影 | `chiaroscuro, single hard key light, deep shadows` |
| Rim／Back light | 輪廓光勾邊，與背景分離 | `rim light separating subject from background` |
| High-key／Low-key | 低對比明亮，或高對比陰暗 | `high-key soft lighting`／`low-key lighting` |
| Practical 光 | 畫面內可見光源（檯燈、霓虹、車燈）當主光 | `lit only by a practical tungsten desk lamp` |
| 窗光／柔光 | 大面積擴散，陰影邊緣柔和 | `soft diffused window light from camera left` |
| 體積光 | 煙霧或塵埃中看得見的光束 | `volumetric haze, visible light shafts, dust motes` |

### 3.4 底片與色溫

| 名稱 | 說明 | Prompt 寫法 |
| :--- | :--- | :--- |
| Kodak Vision3 500T | 鎢絲燈平衡、ISO 500 的電影負片，夜景與室內常用，顆粒明顯 | `shot on Kodak Vision3 500T, visible film grain` |
| Kodak Vision3 250D／50D | 日光平衡負片（250D 較快、50D 細緻） | `Kodak Vision3 250D daylight stock` |
| 色溫 3200K／5600K | 鎢絲燈偏橘、日光偏中性 | `3200K tungsten practicals`、`5600K daylight` |

---

## 4. 鏡位、運鏡、調色映射矩陣

### 4.1 景別與機位

| 名稱 | 取景 | 情緒作用 | Prompt 寫法 |
| :--- | :--- | :--- | :--- |
| Extreme Close-up (ECU) | 眼睛、嘴、手上物件 | 壓迫、專注、細節 | `extreme close-up on eyes, 85mm, f/2` |
| Close-up (CU) | 臉部 | 情緒、對峙 | `close-up on face` |
| Medium Shot (MS) | 腰部以上 | 對話、肢體 | `medium shot, waist up` |
| Wide Shot (WS) | 全身加環境 | 關係與空間 | `wide shot, figure small in frame` |
| Extreme Wide (EWS) | 人物很小、環境為主 | 孤立、規模 | `extreme wide shot, vast empty landscape` |
| Over-the-shoulder | 越過一人肩膀看另一人 | 對話、權力關係 | `over-the-shoulder shot, foreground shoulder soft` |
| Low-angle | 機位低於視線向上 | 權威、壓迫 | `low-angle shot looking up` |
| High-angle／Top-down | 向下俯視／正上方 | 弱小、全局 | `high-angle shot`、`top-down overhead shot` |
| Dutch angle | 地平線傾斜 | 不安 | `dutch angle, horizon tilted 15 degrees` |
| Insert | 單一物件特寫 | 提示線索 | `insert shot of a key on the table` |

### 4.2 運鏡

一個鏡頭先只寫**一個主要運鏡**（經驗法則，未查證各模型文件）；其餘用靜止描述，避免互相打架。

| 運鏡 | 相機做什麼 | 常見用途 | Prompt 寫法 |
| :--- | :--- | :--- | :--- |
| Locked-off／Static | 固定 | 對稱構圖、凝視 | `static locked-off camera` |
| Push in／Pull out | 向前／向後推軌 | 逼近情緒／揭露環境 | `slow dolly push-in over 6 seconds` |
| Pan／Tilt | 原地左右／上下轉 | 掃視、揭露 | `slow pan left` |
| Whip pan | 極快橫搖，中間模糊 | 轉場、驚訝 | `whip pan to the right, motion-blurred transition` |
| Tracking／Truck | 與主體平行移動 | 跟隨、長廊 | `lateral tracking shot following the subject` |
| Orbit／Arc | 繞主體弧形移動 | 英雄時刻 | `camera arcs 90 degrees around the subject` |
| Crane／Jib | 升降搖臂 | 開場、收尾 | `crane up revealing the street` |
| Handheld | 手持輕微晃動 | 紀實、緊張 | `handheld camera, subtle shake` |
| Dolly zoom | 相機後退同時變焦推近（或相反），背景透視拉伸 | 暈眩、認知崩塌 | `dolly zoom: camera moves back while zooming in, background perspective stretches` |
| Rack focus | 焦點從一個主體移到另一個 | 注意力轉移 | `rack focus from foreground hand to background face` |

速度詞要量化：`slow`、`over 6 seconds`、`2% push` 比 `smooth` 有資訊量。

### 4.3 調色風格映射

「參考作品」是用來**描述色調**的常見說法（影視常識，未逐一回原始來源查證）；實際生成時以色彩描述為主，不建議只丟片名或人名，因各模型對作品名與人名的處理規則不同（未查證）。

| 風格 | 色彩描述（寫進 Prompt 的部分） | 常被聯想的作品類型 |
| :--- | :--- | :--- |
| 青橘 Teal & Orange | 膚色偏橘、陰影與背景偏青藍 | 動作／科幻大片 |
| 琥珀霧 Amber haze | 鈉燈橘黃霧中的大尺度建築，低飽和 | 近年科幻片的荒涼城市 |
| 霓虹綠紅 | 螢光燈偏綠、霓虹偏紅洋紅，高飽和、膠片顆粒 | 90 年代香港都會片 |
| 粉彩對稱 | 粉紅、薄荷、淡黃，大面積平塗，飽和但明亮 | 對稱構圖喜劇 |
| 黑白高反差 | 單一硬光、純黑背景、強剪影 | 黑色電影 |
| 去飽和冷藍 | 灰藍、低飽和、霧氣 | 北歐懸疑、戰爭片 |
| 暖鎢絲 | 3200K 橘黃室內光、柔暗角 | 年代劇、家庭劇 |

---

## 5. 常見 AI 罐頭詞黑名單與替換對照

**為何列這張表**：這些詞沒有單一、可驗證的視覺對應物，同一個詞在不同模型可能被讀成不同東西；作者宣稱它們已被稀釋成「平均值罐頭特徵」（這是作者主張，未實測）。替換原則：換成**能指出鏡頭、光、色或數字**的詞。

### 5.1 英文

| 黑名單詞 | 為何要避免 | 替換建議（擇一或組合） |
| :--- | :--- | :--- |
| `cinematic` / `movie style` / `film look` | 沒有指定任何具體攝影參數 | `35mm anamorphic lens, 2.39:1, shallow depth of field f/2` 加一個光源與調色詞 |
| `hyperrealistic` / `photorealistic` / `ultra realistic` | 只說「像真的」，沒說像哪種真 | 指定載體：`shot on Kodak Vision3 500T, visible grain` 或 `50mm, natural window light` |
| `8k` / `4k` / `UHD` / `HD` / `high resolution` | 解析度是輸出設定，不是畫面內容；多數平台在介面選擇 | 刪除，改在平台輸出設定選；真要寫格式改寫畫幅與幀率：`24fps, 2.39:1` |
| `masterpiece` / `best quality` / `award-winning` / `trending on artstation` | 自誇用語，沒有畫面資訊 | 刪除；把空間讓給光、鏡位 |
| `highly detailed` / `intricate` | 細節要指在哪 | `visible skin pores, fabric weave in close-up, 85mm` |
| `stunning` / `beautiful` / `amazing` / `breathtaking` / `epic` | 純評價 | 描述構圖：`low-angle extreme wide shot, figure against a vast sky` |
| `dramatic lighting` | 「戲劇化」可以是任何方向的光 | `chiaroscuro, single hard key light from camera right, deep shadows` |
| `moody` / `atmospheric` | 沒有指出成因 | `low-key lighting, volumetric haze, desaturated teal` |
| `warm nostalgic` / `vintage vibes` | 情緒詞，沒有物理對應 | `3200K tungsten practicals, Kodak Vision3 500T grain, soft vignette` |
| `vibrant colors` / `colorful` | 哪個顏色、飽和多少 | `saturated magenta neon against teal shadows` |
| `professional` / `high quality` | 無資訊 | 刪除 |
| `Hollywood` / `blockbuster` | 籠統聯想 | 指定具體調色，如 `teal and orange grade` |
| `smooth camera movement` | 沒有方向與速度 | `slow dolly push-in over 6 seconds` |
| `bokeh` 單獨出現 | 沒有景深量級 | `shallow depth of field f/1.8, background bokeh` |
| `unreal engine` / `octane render` / `3D render` | 把風格導向遊戲渲染，與實拍質感衝突（想要 3D 風格時例外） | 若要實拍感就刪除 |

### 5.2 中文

| 黑名單詞 | 替換方向 |
| :--- | :--- |
| 電影感、電影質感、大片感 | 同英文 `cinematic` 列：換成焦段、光圈、畫幅、光源 |
| 超寫實、極致細節、高畫質、8K | 指定載體與細節位置；解析度改在平台設定 |
| 大師級、傑作、頂級 | 刪除 |
| 唯美、絕美、震撼、驚艷 | 改寫成構圖與機位 |
| 氛圍感、高級感、質感 | 改寫成光源、色溫、顆粒 |
| 復古、懷舊、溫暖治癒 | 改寫成色溫、底片、暗角（見 3.4） |
| 流暢運鏡 | 改寫成運鏡名稱＋速度＋秒數 |

### 5.3 過濾規則（人或 Agent 交稿前照順序做）

1. **掃描**：不分大小寫，把 Prompt 對照 5.1、5.2。命中就進第 2 步。需要快速掃時可用：
   `grep -n -i -E "cinematic|photorealistic|hyperrealistic|ultra realistic|\b(4k|8k|uhd)\b|masterpiece|best quality|award-winning|stunning|breathtaking|dramatic lighting|vibrant|smooth camera" prompt.txt`
   這只是找候選詞的輔助，不能代替第 3 步的人工判斷。
2. **替換**：每個命中詞換成「能指出鏡頭、光、色或數字」的詞；換不出來就直接刪。
3. **六要素檢查**：每個鏡頭都要有：① 主體與動作 ② 景別與機位 ③ 焦段／光圈（或片幅、畫幅）④ 光源與方向 ⑤ 運鏡與速度（靜止也要寫 `static`）⑥ 調色或底片。缺的要補；真的不適用寫 `N/A` 並說明。
4. **例外**：某個模型官方文件明定要用的關鍵字或參數（例如平台自己的風格開關），照該平台文件寫，並在分鏡備註來源。
5. **負向提示詞**：若平台有負向欄，可放你**不想要的具體物件**（如 `mouse cursor, watermark, extra fingers`），不要把整份黑名單搬進去。
6. **一鏡一運鏡**：同一鏡頭最多一個主要運鏡（經驗法則）。
7. **定稿後試跑**：同一 Prompt 至少跑 3 次，看光與運鏡是否穩定；不穩就簡化詞而不是堆詞。

---

## 6. 經典電影風格 Prompt 實例

以下只描述**風格與技法**，不引用任何劇本、台詞或畫面細節。技法歸屬（如「某片首創」）屬影視常識，**未逐一回原始來源查證**，因此正文用「常被用於」而不下定論。每例先列罐頭版，再列改寫版。

### 6.1 黑色電影審訊室（黑白高反差）

- 罐頭版：`cinematic dramatic noir interrogation scene, 8k, masterpiece`
- 改寫版：
  ```text
  Black and white, 4:3 Academy ratio. Medium close-up of a man seated at a metal table in a bare room. Single hard key light through venetian blinds casts stripes across his face, chiaroscuro, deep black background, cigarette smoke catching the light as volumetric haze. 50mm lens, f/2.8. Slow dolly push-in over 8 seconds. High-contrast monochrome with crushed blacks.
  ```
- 為什麼：光源（單一硬光＋百葉窗）、畫幅、景別、速度全部可驗證。

### 6.2 都會夜晚的霓虹與動態拖影（霓虹綠紅）

- 罐頭版：`cinematic neon night street, vibrant colors, 4k, moody`
- 改寫版：
  ```text
  Night, narrow crowded street. Medium shot of a woman in a doorway frame, shot through a gap between foreground objects. Saturated green fluorescent spill from the shop interior against red neon signage, 35mm lens, f/2, handheld with slight sway. Step-printed motion: passersby smear into long streaks while the subject stays sharp. Kodak Vision3 500T grain, high saturation, lifted blacks.
  ```
- 為什麼：「選擇性動態模糊」「膠片顆粒」「綠紅對比」是拍得出的東西；「step-printed」這類技法詞模型是否理解**未實測**，不穩時改成 `subject sharp, background motion-blurred streaks`。

### 6.3 粉彩對稱構圖（平面、置中）

- 罐頭版：`cinematic pastel hotel, beautiful symmetrical, nostalgic`
- 改寫版：
  ```text
  Perfectly centered, symmetrical wide shot of a hotel lobby, camera at eye level, flat planimetric composition, 4:3 Academy ratio. Pastel pink walls, mint staircase, pale yellow uniforms, even soft frontal light with no hard shadows. 40mm lens, deep focus f/8. Quick whip pan to the right ending on a second centered frame. 5600K daylight, slightly faded print.
  ```
- 為什麼：構圖規則（置中、平面）與色票（粉紅、薄荷、淡黃）是可檢查的。

### 6.4 暈眩感：Dolly zoom（走廊）

- 罐頭版：`cinematic dizzy corridor, dramatic zoom`
- 改寫版：
  ```text
  Medium close-up of a man standing at the end of a long hallway, tight frame on his face. Dolly zoom: camera dollies back while zooming in, his face stays the same size while the corridor walls stretch and recede behind him. 4 seconds, locked focus on his eyes, 35mm to 85mm zoom range. Cold fluorescent overhead light, desaturated green-grey grade, low-key.
  ```
- 為什麼：dolly zoom 常被認為是這種「暈眩」效果的標準做法；寫出相機與焦段如何變化，而不是只說 `zoom`。

### 6.5 荒涼大尺度城市（琥珀霧）

- 罐頭版：`cinematic epic dystopian city, hyperrealistic, 8k`
- 改寫版：
  ```text
  Extreme wide shot, a lone figure walking toward a monolithic brutalist structure through thick orange haze. Sodium-orange light diffused by fog, low saturation, very low contrast in the distance, heavy atmospheric perspective. 24mm lens, deep focus f/8, 2.39:1. Camera static, locked-off, figure moves slowly toward frame center over 10 seconds. Fine film grain.
  ```
- 為什麼：用大氣透視與單色調營造尺度，不靠「epic」。

### 6.6 一點透視長廊跟拍

- 罐頭版：`cinematic haunting hallway, smooth camera, masterpiece`
- 改寫版：
  ```text
  Symmetrical one-point perspective down a long hotel hallway, a lone figure in a grey coat walking away from camera. Camera glides behind at floor height, steady and level, keeping the vanishing point at frame center. 18mm wide-angle lens, deep focus f/8, flat institutional lighting from ceiling fixtures, warm red-brown carpet, 1.85:1. Speed: slow constant tracking over 8 seconds.
  ```
- 為什麼：一點透視、機位高度、焦段與速度都具體；跟拍穩定度取決於模型，**未實測**。

### 6.7 同一鏡頭的兩種寫法（對照）

| | 內容 |
| :--- | :--- |
| 罐頭 | `Cinematic, hyperrealistic, 8k, warm nostalgic movie feel` |
| 光學 | `Shot on 35mm anamorphic lens, shallow depth of field f/1.8, warm amber tungsten light through venetian blinds, subtle dust motes in air, Kodak Vision3 500T grain` |

（光學版整理自筆記第 2.2 節的範例。）

---

## 7. 與分鏡範本、運鏡手冊的關係

- 逐鏡填寫請用 [`templates/cinematic-storyboard-template.md`](../templates/cinematic-storyboard-template.md)，欄位與本文第 5.3 節六要素一一對應。
- 產品介面（軟體 UI）發表片的運鏡參數，另見公開 repo 的運鏡手冊：[`SanHsien/code-as-video-studio` 的 `docs/cinematic-shot-camera-guide.md`](https://github.com/SanHsien/code-as-video-studio/blob/main/docs/cinematic-shot-camera-guide.md)。該手冊針對 UI 動畫，其範例 Prompt 內含 `photorealistic`、`4k` 等本文黑名單詞；套用到人物或場景影片前，請先照第 5.3 節處理。
- 相關筆記：[`notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md`](../notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md)（同樣的「拒絕罐頭」思路，前端 UI 版）。

---

## 8. 未查證與限制

- 沒有對任何影片模型做實測；光學詞效果、運鏡穩定度、橢圓焦外光斑是否被理解，皆未驗證。
- 六站首頁部分抓取失敗（Eyecandy、ShotDeck、Frameset 回 403），相關描述來自搜尋結果與第三方文章；價格與方案請自行到官網確認。
- 筆記中「ShotDeck 為《小丑》攝影指導建立」：CineD 報導寫創辦人為 Lawrence Sher, ASC；其參與哪部片本文未另行查證。
- 第 6 節的「常被用於…」屬影視常識，未逐一回原始來源（導演訪談、攝影指導文章）查證。
- 黑名單來自筆記範例與常見做法整理，不是對某模型的實驗結論；若某詞在你的模型上確實有穩定效果，可在你的分鏡備註中寫明並例外保留。
