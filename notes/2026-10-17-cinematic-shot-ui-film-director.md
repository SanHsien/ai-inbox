---
id: 2026-10-17-cinematic-shot-ui-film-director
title: "cinematic-shot：讓 AI Agent 像拍電影般掌鏡軟體產品發表片的視覺技能"
source_url: "https://www.threads.com/@1weiho/post/DelPZ5-E2Sc"
source_platform: "Threads / GitHub"
author: "Yiwei Ho (@1weiho)"
github_repo: "https://github.com/1weiho/cinematic-shot"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: 2
cluster_role: "鏡頭語言"
short_title: "cinematic-shot 發表片導演"
tags:
  - agent-skills
  - cinematic-shot
  - video-generation
  - product-launch
  - visual-direction
---

# cinematic-shot：讓 AI Agent 像拍電影般掌鏡軟體產品發表片的視覺技能

- **來源貼文**：[Threads @1weiho 貼文](https://www.threads.com/@1weiho/post/DelPZ5-E2Sc)（慶祝 GitHub 突破 100 Stars）
- **官方 GitHub**：[`1weiho/cinematic-shot`](https://github.com/1weiho/cinematic-shot)
- **作者**：`Yiwei Ho (@1weiho)`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 核心內容摘要與視覺語法架構

### 1.1 核心主張與技術定位
- **專案定位**：專門為 Coding Agent 設計的**電影級軟體產品發表片導演技能（Agent Skill）**。
- **解決的痛點**：
  - 傳統 AI 產出的軟體宣傳片往往充斥粗糙的動態模板、死板的等比例縮放或大量的冗長文字標題。
  - `cinematic-shot` 打破常規宣傳片套路，**將軟體 UI 當作高級工業產品（如黑石平板）進行電影級光影與運鏡調度**，無需旁白解說，完全透過介面本身的有機操作（輸入、串流、選取、焦點切換）來展現產品質感。

### 1.2 五大電影級運鏡語法（Cinematic Rules）

```text
┌────────────────────────────────────────────────────────┐
│ cinematic-shot 運鏡矩陣                                │
├────────────────────────────────────────────────────────┤
│ 1. 構圖與景深：黑底懸浮 + 極低俯角 + 極淺景深 (焦平面僅保留1行字) │
│ 2. 攝影機運動：永不停歇的微幅漂移 (Motivated Camera Drift) │
│ 3. 介面自敘事：零廢話字幕，靠有機互動 (打字、串流動畫) 說故事 │
│ 4. 剪輯節奏感：依動作剪接 (Cut on Action)，長鏡 (5-9s) 搭配短頓 (2-3.5s) │
│ 5. 確定性渲染：每幀為時間純函數 (Frame = f(time))，支援真實動態模糊 │
└────────────────────────────────────────────────────────┘
```

1. **暗黑虛空與極淺景深（Dark Void & Razor-thin Focal Plane）**：
   - 介面置於深黑虛空中，採用低角度傾斜視角。焦距銳利鎖定在核心輸入框或按鈕，其餘區域柔和虛化（Bokeh）。
2. **動態微漂移（Motivated Camera Drift）**：
   - 鏡頭永不靜止，始終保持緩慢位移，運動方向永遠預判下一個使用者的互動熱區。
3. **介面自證（The UI Does the Work）**：
   - 拒絕空泛的廣告宣傳詞，完全依靠 UI 上的代碼生成、資料滾動與介面回饋來吸引眼球。
4. **動作剪接（Cut on Action）**：
   - 不按呆板的節拍器拍點切換，而是在點擊、按下 Enter 或畫面展開的瞬間精準切換鏡頭。
5. **確定性時間渲染（Deterministic Time-based Rendering）**：
   - 每一幀渲染均為時間的純函數（$Frame = f(t)$），確保匯出時具備完美的物理動態模糊（Motion Blur）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **多媒體與視覺專案**：在 `C:\GitHub` 本地有 `video-spec-builder`、`video-autopilot-kit`、`AI-drama-pound` 等影視/視覺生成專案。
  - **開源專案 Demo 展示**：當發表開源工具（如 `agent-governance-toolkit`、`ai-inbox`）時，若能用 AI 生成出高品質的極簡發表影片，能大幅提升社群影響力與傳播效果。
  - **Agent 技能庫擴充**：該專案本身就是標準的 `SKILL.md`，可透過 `npx skills add` 直接引入。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **引入其運鏡與視覺 Prompt 語法**：將其「極淺景深、低視角、微漂移、UI 自敘事」的設計規則沉澱至影視與前端 Demo 生成工作流中。
    2. **安裝並實測此 Skill**：在本地評估將 `cinematic-shot` 技能安裝至 Antigravity 或 Claude Code。
  - **不適用 / 需注意的部分**：
    - 渲染管線（如 Remotion、Three.js、Blender 或 AI Video API）的環境相依性需釐清，避免過重的依賴鏈。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-09`**｜**[優先級：高]** 檢閱 `1weiho/cinematic-shot` 倉庫結構，提取其視覺提示詞（Visual Prompts）與運鏡規則手冊
  - **完成日期**：2026-10-23
  - **目標範圍**：`視覺技能 / cinematic-shot 調研`
  - **官方來源**：GitHub [`1weiho/cinematic-shot`](https://github.com/1weiho/cinematic-shot)
  - **具體實作步驟**：
    1. 檢視該倉庫下的 `SKILL.md` 或規則手冊，提煉其攝影機角度設定、焦距設定與燈光指令。
    2. 整理出可在 Remotion、CSS 動畫或 AI 影片生成模型（如 Sora、Runway、Kling）中復用的電影級 UI 提示詞範本。
    3. 產出運鏡規範與提示詞指南筆記。
  - **驗收標準（DoD）**：整理出具體的「電影級產品發表運鏡規範表」，包含 5 種經典 Shot（Hero, Close-up, Pan, Action Cut, Outro）的參數設定。
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付於 `docs/cinematic-shot-camera-guide.md`，完整提煉 `1weiho/cinematic-shot` 倉庫中 5 種經典 Shot 參數設定表、提示詞範本與運鏡規則。

- [ ] **`T-20261017-10`**｜**[優先級：低]** 評估將 `cinematic-shot` 整合至本地影視生成專案（如 `video-spec-builder` 或 Skills）
  - **目標範圍**：`C:\GitHub\video-spec-builder` 或 `~/.gemini/config/skills/`
  - **狀態**：⚪ 不做（cinematic-shot 的運鏡規則由 T-20261017-09 抽取後併入 T-20261021-15，不另做整合評估）
  - **具體實作步驟**：
    1. 在本地測試透過 `npx skills add https://github.com/1weiho/cinematic-shot --skill cinematic-shot` 或手動安裝。
    2. 搭配既有的影視生成工具鏈，以 `ai-inbox` 為範例產品，嘗試生成一段 15 秒的極簡 UI 產品動態展示分鏡腳本。
  - **驗收標準（DoD）**：產出一份基於該語法生成的實際軟體展示分鏡腳本（Shot List + Visual Prompts），驗證其成片質感。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*
