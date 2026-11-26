---
id: "2026-11-26-nicekate-gpt-6-sol-luna-benchmark"
title: "NiceKate AI 實測評析：《GPT-6 Sol、Luna 值不值得用？》——降價優勢、3D/寫作短板與 `AGENTS.md` 遵從度退步回報"
source_url: "https://youtu.be/mTM2Zn6zaVc"
source_platform: "youtube"
author: "NiceKate AI (kate人不错)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 22
source_reviewed_at: "2026-11-26"
source_review_note: "已完整解析影片資訊欄（含 6 段章節）、全片 13:42 音訊 Whisper 逐字稿（181 段）及全部 22 則 YouTube 留言；未擷取影片畫面截圖。"
status: archived
cluster: 1
cluster_role: "Sol與Luna實測"
short_title: "GPT-6 Sol與Luna實測"
tags:
  - openai
  - gpt-6-sol
  - gpt-6-luna
  - model-routing
  - agents-md
  - benchmark
---

# NiceKate AI 實測評析：《GPT-6 Sol、Luna 值不值得用？》——降價優勢、3D/寫作短板與 `AGENTS.md` 遵從度退步回報

- **來源影片**：[`youtu.be/mTM2Zn6zaVc`](https://youtu.be/mTM2Zn6zaVc)（頻道：`NiceKate AI`，發布於 `2026-09-23`，片長 `13:42`，`10,941` 次觀看、`68` 讚、`22` 則留言）
- **分析日期**：`2026-09-23` 原片發布 ／ `2026-11-26` 收錄歸檔
- **當前狀態**：`⚪ 歸檔參考 (Archived — 不另開工單)`
- **相關交叉參照**：
  - [`notes/2026-11-26-nicekate-opus-5-5-medium-effort-benchmark.md`](./2026-11-26-nicekate-opus-5-5-medium-effort-benchmark.md)（同日同作者對照測試：Opus 5.5 Medium）
  - [`notes/2026-11-20-gpt-6-2-astra-sol-routing-eval.md`](./2026-11-20-gpt-6-2-astra-sol-routing-eval.md)（後續 GPT-6.2 Astra / Sol 雙模型路由評估）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型與燃燒率速查表）

---

## 0. 原始資料盤點（6 段章節、13:42 逐字稿與 22 則留言）

- **定位與價格變化（`00:00–00:49`、`13:12–13:42`）**：
  - 作者評測同日推出的 **`GPT-6 Sol`（`xhigh`）** 與 **`Luna`（`Max`）**；指出 `GPT-6 Sol` 相比 `5.6 Sol` 主打輸入與輸出**價格砍半**（讓 Codex 可用額度變多），但編程欺騙率等表現仍以 `Astra` 最低、整體能力明顯落後同日發布的 `Opus 5.5 Medium`。
- **各項實測表現（`00:49–13:12`）**：
  1. **視覺與 3D 建模**：《清明上河圖》畫面簡陋且船上無人；機械蝴蝶與 OpenSCAD 手錶（左上角機械結構露出）尚可；抓娃娃機漏掉右側 Hello Kitty 元素；Blender 沙發弧度雖略勝 Opus 5.5，但 Hello Kitty 抱枕嚴重失真。
  2. **互動、遊戲與指南**：Godot 遊戲中兔子與烏鴉互動失效（不如 Astra）；IKEA 沙發床指南僅直接貼原 PDF 頁面、未生成 3D 安裝動畫；3D 魔尺（眼鏡蛇／小狗／火烈鳥）造型失準；快樂向前衝出現嚴重穿模與閃爍。
  3. **代碼動畫與中文寫作**：代碼動畫尚可；500 字中文獨白測試出現**前後邏輯矛盾**（開頭寫醫院「發來簡訊」，後段卻寫「在檢查單背面算存款」）。
  4. **`Luna Max` 實測**：快樂向前衝出現人物方向翻轉倒著走與嚴重穿模、機械蝴蝶振翅不自然；唯一亮點是耗時 1.5 小時結合 GPT Image 生成貼圖做出帶人物與屋頂材質的《清明上河圖》。
- **22 則留言區實戰警訊**：
  - **留言 #11（`@kelv4191`）**：使用者實測從 `5.6 Sol` 切到 `6 Sol` 後，**多次未遵循 `AGENTS.md` 指引與漏讀專案環境條件**。
  - **留言 #15–17（`@dingody` 與作者回覆）**：回報 `gpt-6 sol xhigh` 在實際生產任務出現**字串寫錯導致線上錯誤**，作者亦認同該版邏輯穩定度仍待加強。

---

## 1. 評估結論與不另開工單理由

- **價值定位**：紀錄了 `GPT-6 Sol (xhigh)` 與 `Luna (Max)` 發布當日的橫向實測表現與社群早期踩坑（`AGENTS.md` 指令漏讀、字串錯寫與邏輯連貫性不足），驗證了「單純降價與拉高 effort（`xhigh`/`Max`）無法彌補基礎能力與指令遵從度落差」，在架構上應維持高風險／關鍵規劃交由主力強模型、低價模型僅作輔助或後續已進化之 `GPT-6.2` 路由（見 [`2026-11-20-gpt-6-2-astra-sol-routing-eval.md`](./2026-11-20-gpt-6-2-astra-sol-routing-eval.md)）。
- **不另開工單理由**：本庫已於 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 完成模型分流與 `GPT-6.2 Astra / Sol` 評估，本片屬歷史發布當日對照測試紀錄，無新增待辦項目，故採 `archived` 歸檔備查。
