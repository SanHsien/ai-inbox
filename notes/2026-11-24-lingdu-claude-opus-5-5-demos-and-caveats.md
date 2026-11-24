---
id: "2026-11-24-lingdu-claude-opus-5-5-demos-and-caveats"
title: "零度解說 YouTube 實測評析：《Opus 5.5 正式發布！實測做動畫、遊戲、寫代碼》——長程自主執行展示與「網頁版不耗配額」誤區勘誤"
source_url: "https://youtu.be/sxny85UZr1A"
source_platform: "youtube"
author: "零度解说 (@lingdujieshuo)"
analyzed_at: "2026-11-24"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 122
source_reviewed_at: "2026-11-24"
source_review_note: "已完整解析影片資訊欄、全片 10:36 音訊 Whisper 逐字稿（364 段）及全部 122 則 YouTube 留言；未擷取影片畫面截圖，亦未下載外部部落格（freedidi.com）附件。"
status: archived
cluster: 3
cluster_role: "Opus5.5影音實測"
short_title: "零度Opus5.5實測評析"
tags:
  - claude-opus-5-5
  - code-as-video
  - webgl
  - prompt-engineering
  - quota-management
---

# 零度解說 YouTube 實測評析：《Opus 5.5 正式發布！實測做動畫、遊戲、寫代碼》——長程自主執行展示與「網頁版不耗配額」誤區勘誤

- **來源影片**：[`youtu.be/sxny85UZr1A`](https://youtu.be/sxny85UZr1A)（頻道：`零度解说`，發布於 `2026-09-26`，片長 `10:36`，`108,914` 次觀看、`641` 讚、`122` 則留言）
- **分析日期**：`2026-11-24`
- **當前狀態**：`⚪ 歸檔參考 (Archived — 不另開工單)`
- **相關交叉參照**：
  - [`notes/2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md`](./2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md)（Claude Opus 5.5 官方遷移、預設 `medium` effort 與快取降價結構）
  - [`notes/2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md`](./2026-11-20-nicekate-opus-5-5-code-as-video-10-cases.md)（Opus 5.5 Code-as-Video 十種程式化動畫案例深度拆解）
  - [`docs/code-as-video-creative-patterns.md`](../docs/code-as-video-creative-patterns.md)（本庫程式化影片／動畫實作規範）

---

## 0. 原始資料盤點（資訊欄、10:36 逐字稿與 122 則留言）

- **作者自測展示（`00:00–06:50`）**：
  1. **3D 日本車站 FPS 網頁遊戲**：於 Claude 網頁版單次長提示詞連續跑近 1 小時產出完整本地專案（`localhost:8080`），含 GLTF、PBR 材質、環境光、Bloom 後期、櫻花與動態列車，以及槍口火焰／後座力／環境音效。
  2. **兩分鐘沙畫歷史動畫與 BBC 風格英語紀錄片**：單次合成劇本、畫面、旁白、雙語字幕與背景音樂／音效。
  3. **東京末班車互動式地圖**：調用真實資料一次生成線路、站點與末班車時刻查詢。
- **引述社群高難度案例與成本宣稱（`06:50–09:51`）**：
  - 展示「紐約開放世界模擬（自寫自跑自改近一天）」「1,113 零件真實可拼樂高鴨＋141 頁說明書」「無遊戲引擎純 Three.js + Blender《蜘蛛人》」「瀏覽器版《真·三國無雙》」「瑞士划船小遊戲」。
  - 影片宣稱相同長任務下 Opus 5.5 成本約為 GPT-6 / Astra 的十分之一（僅為影片轉述之視覺化對比宣稱，留言 #60 亦追問 `7:08` 圖表來源，未附可查證之基準測試連結）。
- **122 則留言關鍵勘誤與社群反饋**：
  - **勘誤「網頁版不消耗 Token」說法（留言 #18、#19、#83–86）**：作者於 `00:43` 稱網頁版「不用 API、不消耗 token」，留言 #18 明確指正網頁版同樣消耗訂閱配額；#83–86 多位用戶實測表示 Pro 訂閱跑大型遊戲／重度 coding 額度「絕對不夠」。
  - **高階提示詞門檻（留言 #50、#66、#73）**：觀眾指出 FPS 等示範背後的提示詞極度專業，「不是普通人寫得出來的」，高讚留言 #73 提醒勿誤以為一般訂閱用戶隨手一句話即可複現相同品質。
  - **Effort 分級實戰（留言 #80、#89）**：留言 #89 建議日常主力用 `low effort`、總領指揮才開 `medium`；留言 #80 則對比 `Opus 5.5 Medium`（70 分鐘完成修復）與 `Astra Ultra Fast`（跑 4 小時仍有遺留問題）。
  - **封號與史實／地理爭議（留言 #5、#21–23、#53、#76）**：大量留言討論中國區使用 Claude 易因網路環境／DNS 洩漏遭封號；另指出片中「改革開放小漁村」指深圳／珠海而非視頻口誤的香港／澳門。
  - **外部連結狀況（留言 #41–42、#58、#95–96）**：資訊欄導流之 `freedidi.com` 曾因 IPv6 AAAA 記錄指向錯誤伺服器導致 `ERR_SSL_UNRECOGNIZED_NAME_ALERT`，作者後續回覆已恢復。

---

## 1. 評估結論與不另開工單理由

- **價值與邊界釐清**：
  - 影片直觀展示了長時程自主編碼（單次運行 ~1 小時）與 3D WebGL / 程式化動畫（Code-as-Video）的產出上限，並側面印證本庫已知的 **`low` 日常執行 / `medium` 總控** effort 分流策略。
  - 但同時凸顯三個不可忽略的誤區：**網頁版同樣受限於訂閱配額上限**、**成品質量高度依賴專業級結構化提示詞**，以及**未附可復現基準來源的 1/10 成本宣稱不可直接採信**。
- **不另開工單理由**：Opus 5.5 的官方定價、`/claude-api prompt-audit`、effort 預設值與 Code-as-Video 實作模式已分別完整收錄於 [`2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md`](./2026-11-15-claude-opus-5-5-prompt-audit-and-api-migration.md) 與 [`docs/code-as-video-creative-patterns.md`](../docs/code-as-video-creative-patterns.md)，本片無新增待辦工程項目，故採歸檔備查。
