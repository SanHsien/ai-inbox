---
id: "2026-11-26-lingtalkai-gpt-image-2-5-eight-scenarios-eval"
title: "YouTube「GPT Image 2.5 八大場景深度實測」逐字稿拆解：座標打點修圖與 Image 關鍵幀＋Codex＋Seedance 分身管線"
source_url: "https://www.youtube.com/watch?v=Uhxt39vNWsc"
source_platform: "YouTube"
author: "灵姐说AI | Ling Talk AI (@aihublab)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 0
source_replies: 49
source_reviewed_at: "2026-11-26"
status: archived
cluster: 2
cluster_role: "Image2.5實測"
short_title: "GPT Image 2.5八大實測"
tags:
  - gpt-image
  - image-generation
  - seedance
  - codex
  - workflow
  - youtube
---

# YouTube「GPT Image 2.5 八大場景深度實測」逐字稿拆解：座標打點修圖與 Image 關鍵幀＋Codex＋Seedance 分身管線

- **來源影片**：[GPT Image 2.5 到底强在哪？8大场景深度实测 ｜ Open AI ｜ GPT 6 Codex](https://www.youtube.com/watch?v=Uhxt39vNWsc)（`2026-09-13` 發布，片長 `23:36`，22,752 次觀看、208 讚、49 則留言）
- **來源完整度**：已透過 YouTube 頁面「顯示轉錄稿」取得全部 17 個章節共 173 段逐字稿與 12 則熱門留言；說明欄無外部 GitHub 專案或工具連結。

---

## 核心結論

影片從實務角度拆解了 **GPT Image 2.5**（含高精細 `Sunburst` 與高速 `Flare` 兩個子型號，對話介面依任務自動路由）相較前代的三個核心升級：**精準（多輪局部編修不跑版）、智能（商業圖表數字比例與物理光影一致性）、產品（座標打點批注與草圖引導）**。其中最值得留存的工作流模式為「**視覺座標打點局部修圖**」以及「**Image 2.5 產出穩定關鍵影格 → Codex 串接 Seedance 生成首尾／中間幀連續動作**」的 2D IP 分身管線；因屬模型能力實測與個人 IP 創作案例（無可複用程式碼），歸檔備查，不另開任務。

---

## 一、GPT Image 2.5 八大實測與關鍵機制

1. **多輪文字與版面精準修改（`11:56`）**：茶飲海報連續修改價格（`29元` → `19元`）與文案（`秋日限定` → `周末限定`），中文字體層級與其餘背景細節維持穩定。
2. **人物換裝與微調邊界（`12:35`）**：初次誤傳 MP4 截圖導致人物身分微幅偏移；改傳真實靜態照片後完成換裝與「拉鍊往下拉到胸口」的局部控制（惟留言區亦有觀眾 `@闲来无事-r7h` 質疑拉鍊細節並未完全到位）。
3. **產品融圖與「視覺座標打點批注」（`14:55`）**：將雙杯產品融圖並切換雨天／清晨背景後，透過編輯器的「新增評論」直接於圖面錨定位置（如指定加註星巴克英文 LOGO），系統自動轉為 **x/y 座標打點指令**精準局部重繪，避免純文字多輪修改「越改越糊」的退化現象。
4. **邏輯與物理一致性（`17:00`–`18:24`）**：實測商業經營圖表（`1000:600` 與 `10%–15%` 柱狀高度比例）、單圖切換陶土／絲網印刷風格，以及玻璃反光靜物在主光源移至右側後的陰影與反射同步重算。
5. **低門檻產品化輸入（`19:05`–`19:47`）**：支援手繪簡筆畫（黑色小豬草圖經引導轉水彩繪本）、兒童磁力片拍照轉具象角色（汪汪隊 Marshall），以及真人照片套用貼紙模板生成 Q 版 IP 表情包。

---

## 二、Image 關鍵幀 + Codex + Seedance 分身管線（`20:45`–`22:45`）

作者說明其測試用流程並非單靠影片模型硬抽，而是拆分權責：
1. 先用 **GPT Image 2.5** 產生角色多個細微姿態變化（眨眼、微笑、點頭、扶眼鏡、思考等）作為**高一致性關鍵影格**。
2. 透過已打通接口的 **Codex** 驅動 **Seedance**，將關鍵影格作為首尾與中間參考幀補間生成連續動作，試圖做成影片右下角的陪播卡通分身。

---

## 三、留言區觀察與評估結論

- **觀眾真實回饋**：雖有電商與美編從業者肯定其修圖效率（`@PeeosAquatic`、`@3X-wow`），但 `@mimgliqng5643` 指出電商 AI 圖片仍存在「一眼 AI 感與實物落差導致消費者不敢下單」的信任門檻；另有 `@GodMorris` 表示真人出鏡比 Q 版動畫更能讓觀眾專注解說內容。
- **任務評估**：純模型實測與工作流概念分享，無須建立本機實作任務，狀態設為 `archived`。
