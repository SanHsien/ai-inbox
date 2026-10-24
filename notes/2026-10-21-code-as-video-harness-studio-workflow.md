---
id: 2026-10-21-code-as-video-harness-studio-workflow
title: "Code-as-Video 影視工作室架構解構：以 Harness 取代 Prompt、seek(t) 時間函式、反 AI 視覺套路與分鏡縮圖自檢門禁實踐"
source_url: "https://www.threads.net/@0xalpha.ai/post/DeMtM1bE4j_"
source_platform: "Threads"
author: "0x Alpha (@0xalpha.ai)"
analyzed_at: 2026-10-21
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 2
cluster_role: "影視框架"
short_title: "Code-as-Video 工作室架構"
tags:
  - code-as-video
  - video-harness
  - remotion
  - playwright
  - anti-ai-slop
  - storyboard-gate
  - agent-skills
---

# Code-as-Video 影視工作室架構解構：以 Harness 取代 Prompt、seek(t) 時間函式、反 AI 視覺套路與分鏡縮圖自檢門禁實踐

- **來源連結**：[0x Alpha (@0xalpha.ai) Threads 貼文](https://www.threads.net/@0xalpha.ai/post/DeMtM1bE4j_)
- **發布平台 / 原作者**：`Threads` / `0x Alpha (@0xalpha.ai)`
- **分析日期**：`2026-10-21`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 1. 核心內容摘要

### 1.1 核心主張：工程約束勝於提示詞（Focus on Harness, Not Prompt）

在 AI 影片生成領域，依賴黑箱提示詞（Prompting）往往伴隨著嚴重的隨機性與風格失控。`0xalpha.ai` 總結了一套基於 Coding Agent（Claude Code / Codex / Antigravity）與代碼驅動（Code-as-Video）的確定性影視製作管線：**「重點是 harness，不是 prompt」**。

其核心體系包含以下 7 大支柱：
1. **基礎工程工具鏈**：Node.js + ffmpeg + Playwright，配合旗艦級推理模型（Opus 5.5）；
2. **工作室規範常駐化（Persistent Studio Harness）**：將影片工程規範沉澱進 `CLAUDE.md` 或專用 `SKILL.md`，使 Agent 每支影片均嚴格遵循標準管線，無須每次重複提示；
3. **底層物理原則：影片是時間的函式 (`V = f(t)`)**：透過 `seek(t)` 能夠在任意時刻精確繪製出任何單一幀（Frame），具備高度確定性與可隨機定位性（Scrubbable）；
4. **硬性剔除 AI 視覺罐頭套路（Anti-AI Slop）**：在規範中嚴格明令禁止三大老套設計：**「漸層背景＋置中標題」、「全部淡入淡出」、「角落小標」**；
5. **真實品牌資產抓取（Real Asset Ingestion）**：製作產品影片時，直接輸入官網 URL，由 Agent 調用 Playwright 擷取真實高解析度截圖、向量 Logo 與官方 CSS 品牌色，拒絕虛構 UI；
6. **渲染前關鍵影格縮圖自檢評估（Storyboard Gate）**：正式耗時渲染前，先輸出分鏡縮圖總覽（Contact Sheet），Agent 自行打 1~10 分，強制修掉評分最低的 3 個分鏡，直到所有鏡頭均達到 8 分以上才放行渲染；
7. **技能封裝與思考成本動態縮放（Reasoning Effort Scaling）**：
   - 小修用 `medium`
   - 新片用 `xhigh`
   - 發表會開場級大片才開 `max`
   - 整體流程打包為單一 Skill，實現「一句話開新片」。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Code-as-Video 確定性影視工作室架構                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 真實素材捕獲 (Playwright)                                           │
│    └─ 注入產品 URL ──▶ 截取真機畫面、SVG Logo、CSS 主色與品牌字體      │
│                                                                        │
│ 2. 時間函式架構 (seek(t) Engine)                                       │
│    └─ Frame = f(time, state) ──▶ 確定性動態、無隨機抽卡偏差           │
│    └─ 嚴格遵守「反罐頭規範」：禁漸層置中標題、禁無腦淡入、禁角落小標   │
│                                                                        │
│ 3. 關鍵影格自審門禁 (Storyboard Gate & Self-Scoring)                   │
│    └─ 導出 8~12 張關鍵影格縮圖矩陣 (Contact Sheet)                     │
│    └─ 多模態 Agent 打分 (1-10)：淘汰最低 3 個鏡頭，全達 8 分才放行   │
│                                                                        │
│ 4. 本地轉碼與封裝 (ffmpeg / WebCodecs)                                  │
│    └─ 合成 MP4 視訊 ──▶ 封裝為 Agent 可覆用之 Standard Skill          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 對現有工作流與專案之啟發

### 2.1 貫穿集群 2 的影音與動效體系（核心樞紐）

本篇方法論為已建立的視覺與動效資產庫提供了最清晰的「集成黏合劑」：
- **與 BeatDesign（Note 33）的結合**：BeatDesign 提供了本地時間線與 29 個 MCP 工具，而本篇的「以 Playwright 抓取真資產」與「分鏡縮圖打分」可直接作為 BeatDesign 外部 Agent 的前端調度邏輯；
- **與 Cinetic（Note 29）的結合**：Cinetic 具備 273 種動畫技法與音畫節拍網格（Beat Grid），可直接作為 `seek(t)` 函式庫的時間節奏運算核心；
- **與 Shipper 反 AI 罐頭設計（Note 15）的共振**：本篇明確點名的「漸層背景＋置中標題」、「全部淡入」、「角落小標」三大視覺毒瘤，直接對齊了 `epstein.md` 的去油膩準則；
- **與 cinematic-shot（Note 3）的運鏡對照**：運鏡標籤在代碼層級具現化為相機視野（FOV）、平移（Pan）與縮放（Zoom）的精確數學插值。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261021-15`**｜**[優先級：高]** 建立「Code-as-Video Studio 影視工作室規範（`CLAUDE.md` / `SKILL.md` 範本）」，將「影片是時間函式 seek(t)」、反 AI 視覺套路清單與 Playwright 網頁素材自動擷取封裝為標準模組
  - **目標範圍**：`~/.gemini/config/skills/code-as-video` 或 `templates/video-studio-harness.md`
  - **具體做法**：撰寫標準 Studio 規範範本，內建禁止「漸層背景＋置中標題、全部淡入、角落小標」之反套路規則庫，實作以 Playwright 抓取產品網址真實截圖與 CSS 品牌色提取腳本，並規範影片以 `seek(t)` 確定性時間函式渲染
  - **驗收標準（DoD）**：產出完整的規範檔案與測試腳本，輸入一個公開網址能自動抓取截圖與主色系，並生成一個包含時間函式架構的單檔代碼範例
  - **完成日期**：2026-10-22
  - **實作紀錄 / 證據**：產出 templates/video-studio-harness.md 影視工作室規範（含 CLAUDE.md / SKILL.md 範本），整合 seek(t) 時間函式架構、四大反 AI 視覺套路禁令，並併入 T-20261017-18（運鏡）、T-20261018-02（動效字典）、T-20261020-04（時間線規格）與 T-20261018-01（Remotion/Canvas 渲染工作流）；實作 tools/video_asset_capture.py 與 tests/test_video_asset_capture.py（單元測試通過）；實測以 Playwright 抓取 https://openlibrary.org 產出截圖、theme.json 與單檔時間函式範例 assets/openlibrary_demo/video_seek_canvas.html。
- [x] **`T-20261021-16`**｜**[優先級：中]** 實作「關鍵幀縮圖總覽與 1-10 分自檢評審門禁（Keyframe Storyboard Gate）」，在影片正式渲染前自動剔除劣質分鏡
  - **完成日期**：2026-10-23
  - **目標範圍**：`tools/verify_video_storyboard.py` 或 Agent 審查 Hook
  - **具體做法**：撰寫縮圖拼接腳本，在正式渲染前批次抽取 6~12 個關鍵影格拼成 Contact Sheet，調用多模態 Agent 依照構圖、層次、對比進行 1-10 分打分，自動回報評分低於 8 分的影格並觸發微調重新生成
  - **驗收標準（DoD）**：以單一測試影片腳本執行，能正確輸出 Storyboard 縮圖並產出打分 JSON，對低分影格能觸發重繪邏輯
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `tools/verify_video_storyboard.py` 與測試 `tests/test_verify_video_storyboard.py`（6/6 通過），實作關鍵影格 1-10 分評審打分機制、四大反 AI 罐頭套路檢測、自動輸出 HTML Contact Sheet 與 JSON 門禁報告。

---

## 4. 關聯筆記與相關任務（Related Notes & Sessions）

- **Code-as-Video 與視覺動效體系**：
  - [BeatDesign 開源 AI 影片工作台](./2026-10-20-beatdesign-open-source-ai-video-studio.md) ｜ 關聯任務：`T-20261020-03`、`T-20261020-04`
  - [Cinetic 動態導演 Agent Skill](./2026-10-19-cinetic-motion-director-agent-skill.md) ｜ 關聯任務：`T-20261019-03`、`T-20261019-04`
  - [Shipper 反 AI 罐頭設計 (epstein.md)](./2026-10-17-shipper-epstein-md-anti-ai-slop.md) ｜ 關聯任務：`T-20261017-19`、`T-20261017-20`
  - [cinematic-shot：AI Agent 掌鏡軟體發表片](./2026-10-17-cinematic-shot-ui-film-director.md) ｜ 關聯任務：`T-20261017-09`、`T-20261017-10`
  - [Prompt Motion 代碼動效視頻策展庫](./2026-10-18-prompt-motion-claude-video-showcase.md) ｜ 關聯任務：`T-20261018-01`、`T-20261018-02`
- **長上下文外包與模型分流**：
  - [0x Alpha (GLM-5.3-Flash) 1M 模型](./2026-10-21-0x-alpha-glm-5-3-flash-1m-context.md) ｜ 關聯任務：`T-20261021-13`、`T-20261021-14`
