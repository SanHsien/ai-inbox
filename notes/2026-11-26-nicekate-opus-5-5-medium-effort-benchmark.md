---
id: "2026-11-26-nicekate-opus-5-5-medium-effort-benchmark"
title: "NiceKate AI 實測評析：《Opus 5.5 只用 Medium，就能做到這個程度？》——推論深度倒掛現象、空間演算法與 3D 建模參考圖落差"
source_url: "https://youtu.be/1_empfjtb4Y"
source_platform: "youtube"
author: "NiceKate AI (kate人不错)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 40
source_reviewed_at: "2026-11-26"
source_review_note: "已完整解析影片資訊欄（含 6 段章節）、全片 20:24 音訊 Whisper 逐字稿（279 段）及全部 40 則 YouTube 留言；未擷取影片畫面截圖。"
status: archived
cluster: 3
cluster_role: "Opus5.5實測評析"
short_title: "NiceKate Opus5.5實測"
tags:
  - claude-opus-5-5
  - effort-routing
  - code-as-video
  - 3d-modeling
  - openscad
  - blender
---

# NiceKate AI 實測評析：《Opus 5.5 只用 Medium，就能做到這個程度？》——推論深度倒掛現象、空間演算法與 3D 建模參考圖落差

- **來源影片**：[`youtu.be/1_empfjtb4Y`](https://youtu.be/1_empfjtb4Y)（頻道：`NiceKate AI`，發布於 `2026-09-23`，片長 `20:24`，`11,051` 次觀看、`101` 讚、`40` 則留言）
- **分析日期**：`2026-09-23` 原片發布 ／ `2026-11-26` 收錄歸檔
- **當前狀態**：`⚪ 歸檔參考 (Archived — 不另開工單)`
- **相關交叉參照**：
  - [`notes/2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md`](./2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md)（同作者後續 Code-as-Video 十案例拆解）
  - [`notes/2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md`](./2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md)（Opus 5.5 官方預設 `medium` effort 與遷移指南）
  - [`notes/2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md`](./2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats.md)（Opus 5.5 其他社群實測與配額勘誤）

---

## 0. 原始資料盤點（6 段章節、20:24 逐字稿與 40 則留言）

- **推論深度（Effort）與基準觀察（`00:00–01:44`）**：
  - 作者引述 Opus 5.5 較 Opus 5 成本降約 40%、長任務耗時短於 Fable 5.1（9.5h vs 12h），但同時指出思考過程較耗 token，且在 Terminal-Bench 與 FrontierCode 基準上出現**過高 effort 收益遞減甚至倒掛（FrontierCode 上 `High` 表現遜於 `Medium`）**，因此全片測試統一鎖定 **`Medium` 檔位**（測試載體為 Cursor IDE、Claude Desktop 與 Droid，見留言 #5）。
- **六項實測表現總覽（`01:44–20:24`）**：
  1. **《清明上河圖》可漫遊 3D 場景**：Cursor 內耗時 `1h 4m` 完成（留言 #3），碼頭、橋面、船棚、水波與街市質感完整、人物穿模明顯減少，僅局部輪子與少數物件仍有穿模。
  2. **魔尺工坊（Rubik's Snake）**：作者評為目前實測最強，順利完成五角星、八面體／雙球、咖啡杯、星盟球與鋼琴折疊動效，空間演算法與折疊動畫表現突出。
  3. **IKEA 沙發安裝互動指南**：優於 Fable 5.1——直接從原 PDF 擷取零件圖而非重繪易失真的 SVG，步驟、螺絲點位與儲物／睡眠動畫還原度高。
  4. **3D 建模弱項揭露（`09:31–13:26`）**：OpenSCAD 手錶與機械蝴蝶材質細膩，但錶針孔位與機芯方位有錯位；抓娃娃機與 Blender 沙發／抱枕在**參考圖輪廓與弧度還原上明顯不如 Astra**。
  5. **純 JS 代碼動畫與趣味短片**（留言 #23/#31 確認未用 skill、留言 #9 確認配音亦為 Opus 5.5 多模態輸出）：神筆馬良、小豬妖與 Anthropic 介紹短片。
  6. **中文第一人稱短篇寫作（500 字內三訊息交織）**：醫院報告、房東漲租 600 元、前任生日問候三線敘事節奏自然，作者評為大幅減少 AI 腔。
- **40 則留言補充**：留言 #34 用戶實測由 Opus 5（跑 3 天未完）切至 Opus 5.5 約 3 小時完成長任務且敘述更有條理；留言 #13–18 討論 Anthropic 配額重置與從 `High` 改試 `Medium`。

---

## 1. 評估結論與不另開工單理由

- **價值定位**：本片為 Opus 5.5 發布初期的橫向能力實測紀錄，具體印證了兩點工程直覺：(1) **`Medium` effort 常是性價比與穩定度的最佳甜蜜點**（盲目開 `High`/`Max` 可能反而倒掛）；(2) **PDF 原件擷取＋空間演算法**表現優異，但**Blender 參照圖 3D 建模精準度**仍具明顯短板。
- **不另開工單理由**：本庫已於 [`2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md`](./2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md) 與 [`2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md`](./2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md) 完整收錄 Opus 5.5 `medium` 預設值與 Code-as-Video 實作規範，本片無新增待辦工程項目，故採 `archived` 歸檔備查。
