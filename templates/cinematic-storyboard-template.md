# 電影級分鏡提示詞範本 (Cinematic Storyboard Template)

> 任務：`T-20261026-16`｜規範：[`docs/cinematic-ai-video-prompt-guide.md`](../docs/cinematic-ai-video-prompt-guide.md)（光學對照表、黑名單、過濾規則都在那裡）
> 用法：複製本檔，先填「0. 全片設定」，再每個鏡頭複製一份「鏡頭卡」；填完用第 3 節自檢，最後才送進影片生成模型。
> 欄位對應：鏡頭卡的 ①～⑥ 就是指引第 5.3 節的「六要素」，缺一欄就是缺一個要素。

---

## 0. 全片設定

| 欄位 | 填寫 | 說明 |
| :--- | :--- | :--- |
| 片名／用途 | {例：30 秒品牌短片} | |
| 總長／鏡頭數 | {秒} / {N} | 各鏡秒數加總要等於總長 |
| 畫幅／幀率 | {2.39:1 / 1.85:1 / 4:3}、{24fps} | 整片統一，避免每鏡各寫各的 |
| 全片光學基調 | {例：35mm 變形鏡頭、Kodak Vision3 500T 顆粒} | 每鏡的 Prompt 都要帶，保持連戲 |
| 全片調色基調 | {色票與對比，例：青藍陰影、橘黃高光、低飽和} | |
| 參考靜幀 | {站名＋連結（只放連結，不存原圖）} | 例：Shot Cafe 或 Film-Grab 頁面網址 |
| 使用模型／版本 | {名稱、日期} | 動態資訊，標查證日 |

---

## 1. 鏡頭卡（每鏡一份，複製貼上）

```text
### Shot {編號，如 01}｜{秒數}s｜{一句話目的，如「建立場景」}

① 主體與動作 Subject / Action
   中：{誰、在做什麼、在哪裡；一個動作}
   EN: {subject + one action + location}

② 景別與機位 Shot size / Angle
   {ECU / CU / MCU / MS / WS / EWS / OTS / Insert}｜{eye-level / low-angle / high-angle / dutch / top-down}

③ 焦段、光圈、景深 Lens / Aperture / DoF
   {焦段 mm}｜{f/ 值}｜{景深描述：shallow / deep focus}｜{變形鏡頭? 畫幅}

④ 光源 Lighting
   {光型：Rembrandt / chiaroscuro / rim / soft window / practical…}｜{方向}｜{色溫 K}｜{體積光?}

⑤ 運鏡 Camera movement（一鏡一個主要運鏡）
   {static / push-in / pull-out / pan / whip pan / tracking / orbit / crane / handheld / dolly zoom / rack focus}
   速度與時間：{例：slow, over 6 seconds}

⑥ 調色與底片 Grade / Stock
   {色彩描述：主色、陰影色、飽和度}｜{底片或顆粒}｜參考：{連結}

轉場 Transition：{cut / whip pan / match cut / dissolve / hard cut on action}
連戲備註 Continuity：{與上一鏡相同／不同的服裝、光向、色溫}

— 最終 Prompt（英文，一段） —
{把 ①～⑥ 依序串成一段，不放黑名單詞}

— 負向提示詞（若平台有此欄；寫具體物件） —
{例：mouse cursor, watermark, extra fingers}

— 自檢 —
[ ] 沒有指引第 5 節黑名單詞（或已註明例外與來源）
[ ] ①～⑥ 都有內容（不適用的寫 N/A 與理由）
[ ] 只有一個主要運鏡，且有速度或秒數
[ ] 秒數已加入總長核對
```

---

## 2. 填好的範例（3 鏡 12 秒，中英雙語對照）

> 範例為虛構題材，目的只是示範欄位怎麼填；光學與調色詞均取自指引。

### 0. 全片設定（範例）

| 欄位 | 填寫 |
| :--- | :--- |
| 片名／用途 | 〈雨夜加油站〉概念短片 12 秒 |
| 總長／鏡頭數 | 12s / 3（4s + 4s + 4s） |
| 畫幅／幀率 | 2.39:1、24fps |
| 全片光學基調 | 35mm 變形鏡頭、橢圓焦外光斑、Kodak Vision3 500T 顆粒 |
| 全片調色基調 | 青藍陰影、鈉燈橘黃高光、低飽和、黑位微抬 |
| 參考靜幀 | 於 [Shot Cafe](https://shot.cafe) 以夜景／外景／wide shot 檢索後挑選（僅記屬性，不存原圖） |
| 使用模型／版本 | {填入實際使用的模型與日期} |

### Shot 01｜4s｜建立場景

| 欄位 | 中文 | English |
| :--- | :--- | :--- |
| ① 主體與動作 | 一位穿風衣的男子站在雨夜的加油站遮雨棚下，低頭點菸 | A man in a trench coat stands under a gas station canopy in night rain, lighting a cigarette |
| ② 景別機位 | 廣角，平視 | Wide shot, eye-level |
| ③ 焦段光圈景深 | 35mm 變形鏡頭、f/2.8、景深中等，遠處招牌散景成橢圓 | 35mm anamorphic, f/2.8, moderate depth of field, distant signs as oval bokeh |
| ④ 光源 | 遮雨棚下的鎢絲日光燈為 practical 主光，色溫約 3200K；地面積水反射橘光 | Practical tungsten canopy lights at about 3200K as key, orange reflections on wet asphalt |
| ⑤ 運鏡 | 緩慢推軌，4 秒內前進約 5% | Slow dolly push-in, about 5% over 4 seconds |
| ⑥ 調色底片 | 青藍陰影、橘黃高光、低飽和；500T 顆粒 | Teal shadows, orange highlights, low saturation; 500T grain |
| 轉場 | 硬切（動作點：火光亮起） | Hard cut on the lighter flare |

最終 Prompt：

```text
Wide shot, eye-level. A man in a trench coat stands under a gas station canopy in night rain, lighting a cigarette. 35mm anamorphic lens, f/2.8, moderate depth of field, distant signs as oval bokeh, 2.39:1. Practical tungsten canopy lights at about 3200K as key light, orange reflections on wet asphalt. Slow dolly push-in, about 5% over 4 seconds. Teal shadows, orange highlights, low saturation, lifted blacks, Kodak Vision3 500T film grain.
```

負向提示詞：`watermark, text overlay, extra fingers, cartoon`

### Shot 02｜4s｜情緒特寫

| 欄位 | 中文 | English |
| :--- | :--- | :--- |
| ① 主體與動作 | 同一名男子的臉，火光熄滅後望向遠方 | The same man's face, looking into the distance after the flame goes out |
| ② 景別機位 | 特寫，略低機位 | Close-up, slightly low angle |
| ③ 焦段光圈景深 | 85mm、f/1.8、景深極淺，只有眼睛銳利 | 85mm, f/1.8, very shallow depth of field, only the eyes sharp |
| ④ 光源 | 側面 Rembrandt 光，暗側臉頰有三角光斑；背後霓虹作輪廓光 | Side Rembrandt lighting with a triangle of light on the shadow cheek; neon rim light from behind |
| ⑤ 運鏡 | 靜止（locked-off），僅雨絲與煙霧在動 | Static locked-off camera; only rain and smoke move |
| ⑥ 調色底片 | 同 Shot 01，膚色偏橘，背景青藍 | Same grade as Shot 01, warm skin tones against teal background |
| 轉場 | 快速橫搖（whip pan）接下一鏡 | Whip pan into next shot |

最終 Prompt：

```text
Close-up, slightly low angle. The same man's face, looking into the distance after the flame goes out. 85mm lens, f/1.8, very shallow depth of field, only the eyes sharp, 2.39:1. Side Rembrandt lighting with a triangle of light on the shadow-side cheek, magenta neon rim light from behind, rain and smoke drifting. Static locked-off camera. Same teal and orange grade, warm skin tones against teal background, Kodak Vision3 500T film grain.
```

負向提示詞：`watermark, text overlay, extra fingers, cartoon`

### Shot 03｜4s｜收尾

| 欄位 | 中文 | English |
| :--- | :--- | :--- |
| ① 主體與動作 | 男子走進雨中，背影縮小，加油站燈光留在身後 | The man walks into the rain, his back shrinking, station lights behind him |
| ② 景別機位 | 超廣角，高機位 | Extreme wide shot, high angle |
| ③ 焦段光圈景深 | 24mm、f/8、全景深 | 24mm, f/8, deep focus |
| ④ 光源 | 鈉燈橘光與地面反射，遠景有薄霧（體積光） | Sodium-orange light with wet-ground reflections, thin volumetric haze in the distance |
| ⑤ 運鏡 | 升降搖臂緩慢上升，4 秒內升高約 3 公尺 | Slow crane up, rising about 3 meters over 4 seconds |
| ⑥ 調色底片 | 同前，遠處對比降低（大氣透視） | Same grade, lower contrast in the distance (atmospheric perspective) |
| 轉場 | 淡出至黑 | Fade to black |

最終 Prompt：

```text
Extreme wide shot, high angle. The man walks into the rain, his back shrinking, gas station lights behind him. 24mm lens, f/8, deep focus, 2.39:1. Sodium-orange light with reflections on wet ground, thin volumetric haze in the distance, lower contrast far away. Slow crane up, rising about 3 meters over 4 seconds. Same teal and orange grade, low saturation, Kodak Vision3 500T film grain.
```

負向提示詞：`watermark, text overlay, extra fingers, cartoon`

### 範例總表核對

| Shot | 秒數 | 景別 | 運鏡 | 轉場 |
| :-: | :-: | :--- | :--- | :--- |
| 01 | 4 | Wide | Dolly push-in | Hard cut |
| 02 | 4 | Close-up | Static | Whip pan |
| 03 | 4 | Extreme wide | Crane up | Fade to black |
| 合計 | 12 | 與全片設定 12s 相符 | 每鏡一個主要運鏡 | |

---

## 3. 交稿前自檢（整份分鏡）

1. 各鏡秒數加總 = 全片總長。
2. 每個最終 Prompt 都沒有指引第 5 節黑名單詞；有例外者已註明模型文件出處。
3. 連戲：畫幅、片種顆粒、調色基調、色溫在各鏡之間一致（或在「連戲備註」寫明刻意改變）。
4. 同一份分鏡先用 1 個鏡頭試跑 3 次，穩定再批量生成（效果因模型而異，指引未做實測）。
5. 參考靜幀只放連結與屬性描述，不把受版權保護的原圖提交進 repo。
