---
id: 2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide
title: "ChatGPT-6.1 生態系全景評測：GPT Work、Codex 與 Skills 的進階落地方案與 Session 工具鏈實戰映射"
source_url: "https://youtu.be/6n14rKV6oJc"
source_platform: "YouTube (孔老師AI研習社)"
author: "孔老師AI研習社 (@Teacher_Kong)"
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: in-progress
cluster: 1
cluster_role: "終端派工"
short_title: "ChatGPT-6.1 全景實測與工具鏈映射"
tags:
  - chatgpt-6-1
  - gpt-work
  - codex
  - skills
  - agents-md
  - threejs-generative-ui
  - burn-rate-optimization
  - buzz-nostr
---

# ChatGPT-6.1 生態系全景評測：GPT Work、Codex 與 Skills 的進階落地方案與 Session 工具鏈實戰映射

- **來源連結**：[YouTube 影片完整教學 (孔老師AI研習社)](https://youtu.be/6n14rKV6oJc)
- **影片標題**：〈ChatGPT-6.1 完整教學，全新15大功能＋所有場景實測！GPT Work、Codex、Skills 一次搞懂，從入門到進階，新手也能用 AI 賺錢、效率翻10倍！〉
- **頻道作者**：孔老師AI研習社（@Teacher_Kong，80.4K 訂閱）
- **發布日期**：`2026-10-01` ｜ 觀看次數：113,000+
- **分析主題**：ChatGPT-6.1 桌面生態系（GPT Work 辦公協同、Codex 程式代理、Skills 模組化流程）、大眾化操作盲區破解、Session 實戰工具鏈（AGENTS.md 派工、Three.js 視覺工件、Buzz NAS 常駐、雲地雙軌實操、Cache 燃燒率矩陣）深度映射
- **當前狀態**：`🟡 進行中 (In Progress)`
- **相關交叉參照**：
  - [`notes/2026-10-26-llm-burn-rate-cache-routing-benchmark.md`](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md)（Sol 6.1 vs Astra 6 燃燒率與 Cache 基準）
  - [`notes/2026-10-26-block-buzz-nostr-agent-workspace.md`](./2026-10-26-block-buzz-nostr-agent-workspace.md)（Buzz 類 Slack 聊天室與 NAS 常駐拓撲）
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（Grok Bot + Herdr 統一進入點與 AGENTS.md 驅動）
  - [`notes/2026-10-19-rea-reverse-engineer-anything-agent.md`](./2026-10-19-rea-reverse-engineer-anything-agent.md)（Clean Room 合規 Prompt 與雲地雙軌實操）
  - [`notes/2026-10-26-3d-model-anything-iphone-lidar-threejs.md`](./2026-10-26-3d-model-anything-iphone-lidar-threejs.md)（Three.js Generative UI 與 3D 空間運算）

---

## 1. 核心內容摘要與影片全景剖析（Key Insights）

孔老師在本作中系統性梳理了 OpenAI 最新桌面與 Agent 生態系（ChatGPT-6.1）的 15 大核心升級，重點拆解三大旗艦模組：

### 1.1 影片核心主張：從「單純聊天視窗」邁向「代理型工作台（Agentic Workspace）」

1. **GPT Work（辦公型自動化代理）**：
   - 專門針對文檔處理、試算表自動化、專案進度追蹤與商業報告排版設計。
   - 具備跨應用感知與檔案深度讀取能力，將傳統多步驟的「複製→貼上→調整格式」整合成一鍵交付的 SOP。
2. **Codex（工程與桌面操作 Agent）**：
   - 與 GPT Work 共用底層 GPT-6 系列推理能力，但專精於軟體工程、全端開發、本機指令列執行與外掛擴充。
   - 支援呼叫電腦環境工具，具備自主除錯與多檔案修改閉環。
3. **Skills（可複用標準作業程序）**：
   - 使用者將日常固定模式（如知乎長帖撰寫、週報提取、代碼安全審計）封裝為獨立 Skill。
   - 透過提及（如 `@Skill` 或 `$Skill`）即時掛載特定指令與知識範本，避免反覆輸入冗長 Prompt。

### 1.2 大眾化教學的工程落差與觀眾實務痛點

影片雖然對入門新手極具吸引力，但在實際落地至進階工程與複雜生產力場景時，暴露出一般使用者無法跨越的五大鴻溝（反映在觀眾留言與社群討論中）：
1. **外部專業軟體操控障礙**：如觀眾 `@payson1998` 提問：「請問 3D 的部份是要安裝外掛程式嗎？還是進工作模式跟他聊天就可以了？因為我請他操作 3D 軟體他表示無法直接操作。」——大模型本質無法憑空「魔法點擊」本機閉源 3D GUI 軟體。
2. **技能呼叫繁瑣與專案失憶**：一般人依賴手動 `@Skill`，換到不同專案或不同對話就必須重新交代環境背景與架構規範。
3. **單機桌面端的額度撞牆與已讀不回**：官方桌面端在高強度任務中極易觸發 Rate Limit，一旦額度耗盡便直接中斷或無回應。
4. **二進位逆向與敏感工程審查攔截**：一般使用者直接要求 AI 進行代碼修補或反組譯時，容易被對齊過濾器判定違規而拒答。
5. **天價 Token 燃燒率**：新手若未掌握模型選型與 Context Cache 機制，盲目開啟頂級旗艦模型，數小時內即會燒乾一週額度。

---

## 2. 運用 Session 實戰工具鏈之進階映射（Session Mastery Mapping）

運用本對話 Session 中所沉澱的**五大資深實戰技巧、架構與軟體工具**，能對孔老師提出的教學框架進行徹底的工程升級與降維打擊：

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               ChatGPT-6.1 教學盲區 vs. Session 實戰工具鏈降維升級映射                  │
├───────────────────────────────┬────────────────────────────────────────────────────────┤
│ 孔老師教學模式 (大眾入門)     │ 本 Session 實戰工具鏈 (資深架構升級)                   │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. 聊天手動呼叫 @Skill        │ ➔ 專案根目錄 AGENTS.md 規範驅動起步 (Grok/Herdr 派工)  │
│ 2. 詢問 3D 軟體遭拒答卡關     │ ➔ Three.js Generative UI 確定性工件 + CLI-Anything/MCP │
│ 3. 官方桌面端 RateLimit 中斷  │ ➔ Buzz Nostr 類 Slack 私有常駐 (NAS) + Quota 心跳退場  │
│ 4. 逆向工程與二進位審查拒答   │ ➔ Clean Room 合規宣告 + 雲地雙軌管線 (GPT+本地未審查)  │
│ 5. 盲目選模型導致額度暴燒     │ ➔ Sol 6.1 vs Astra 6 燃燒率模型路由 + Cache 命中優化   │
└───────────────────────────────┴────────────────────────────────────────────────────────┘
```

### 2.1 升級一：以 `AGENTS.md` 規範驅動起步，徹底解放手動 `@Skill`
- **問題**：官方 Skills 需要手動 `@`，且無法解決跨專案規範繼承問題。
- **Session 解法**：
  - 借鏡 **「Grok Bot + Herdr 統一進入點」** 實戰心法：統一所有 Agent 對專案目錄的進入點感知。
  - 將專案專屬規範、禁區、驗收標準（DoD）沉澱在各專案根目錄的 `AGENTS.md`。
  - 當 Codex 或 Coding CLI 啟動時，第一步強制讀取當前專案的 `AGENTS.md`，自動掛載環境契約，達成「零重複交待、即起即幹」。

### 2.2 升級二：破解 3D 與外部 GUI 操控障礙（回應觀眾 payson1998 提問）
- **問題**：觀眾要求 ChatGPT 直接操控本機 Blender/Cinema4D 等 3D 軟體被拒絕。
- **Session 解法**：
  - **路徑 A（Generative UI 視覺工件）**：運用我們在 `3d-model-anything-iphone-lidar-threejs` 與 `answer-me-with-html` 的技術，讓 Agent 輸出標準 **Three.js WebGL 互動 HTML 工件**，在瀏覽器中即時渲染 3D 模型、光影與網格，無需依賴外部 3D 軟體。
  - **路徑 B（Agent-Native CLI / MCP 橋接）**：若必須操控本機軟體，則透過 **CLI-Anything** 將 GUI 封裝為 Agent-Native CLI，或撰寫專屬 MCP Server（如 Blender Python API MCP），讓 Agent 透過標準 RPC 控制軟體內核，而非天真地進行桌面視覺點擊。

### 2.3 升級三：以 Buzz Nostr 私有化常駐打破桌面端 Rate Limit 與單兵侷限
- **問題**：官方桌面端僅支援單一工作機，遇到限流或斷線直接中斷。
- **Session 解法**：
  - 運用 **Block Buzz** 的開源 Nostr Relay，將協同平台部署在**本地或私有 NAS**，打造 24/7 常駐的類 Slack 協同工作空間。
  - 利用不同 Channel 隔離專案上下文；多個 Agent（地端與雲端）按職能進駐群組。
  - 引入 **Quota Heartbeat 心跳機制**：當某個 Agent 額度用盡時，主動在聊天室廣播退場，消除「已讀不回」的等待盲區。

### 2.4 升級四：以 Clean Room 合規宣告與「雲地雙軌」跨越逆向工程審查
- **問題**：大模型內建強烈的安全對齊，遇到二進位分析、記憶體修補或逆向會直接拒絕。
- **Session 解法**：
  - **合規 Prompt 工程防線**：先清楚交代目的為「純靜態分析、Call Graph 與功能/資料格式重建，完全不使用原版程式代碼，無商用與非法用途」。
  - **雲地雙軌分工**：由雲端 GPT-4o / Claude 輸出完整 Assembly、呼叫位址、`TfmRegKey` 與精確 Patch 資訊；再交由地端本地未審查模型（Local Uncensored LLM）或二進位工具鏈執行真實 Hex/Assembly Patch 實操。

### 2.5 升級五：以燃燒率矩陣與 Cache 命中構築個人護城河
- **問題**：新手容易在簡單工單上濫用高算力模型，導致配額迅速見底。
- **Session 解法**：
  - 嚴格落實實測基準：高階架構規劃使用 **Sol 6.1 High**（24H 持續跑 5~6 個專案僅燒 50% 額度）；嚴格避開 **Astra 6 High**（4 小時即燒完一週額度）；日常施工選用 **Luna 6 Max ~ High**（搭配合適 Goal 可 24H 穩定推進）。
  - 最大化利用 **Prompt Caching** 機制，將靜態 SSOT 規範與系統指令放在最前方，降低 80% 以上的重複 Token 成本。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **架構借鏡**：
  - 孔老師梳理的 GPT Work / Codex / Skills 三位一體概念，印證了目前主流 AI 開發環境的發展方向。
  - 但其大眾化教學缺乏「工程防線、進程管理、額度心跳與合規避障」的硬核基礎設施。
- **採納與落地行動**：
  1. **規格化 `AGENTS.md` 自動掛載與 Skill 預算防稀釋協議**：將 Grok/Herdr 進入點心法正式沉澱為可跨專案複用的規範文檔。
  2. **收錄 3D / GUI 外部控制橋接手冊**：為後續遇到 3D、音視訊或外部軟體操作的任務提供標準路徑（WebGL 工件 vs MCP 橋接）。
  3. **整合 Buzz 私有常駐與額度防燒指南**：制定個人工作台長程維護與 Token 經濟學 SOP。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261026-29`**｜**[優先級：高]** 撰寫「GPT Work / Codex 之 AGENTS.md 規範驅動起步與 Skill 預算控制手冊」收錄於 `docs/codex-skills-agents-bootstrap-guide.md`
  - **狀態**：🟡 進行中
  - **目標範圍**：`docs/codex-skills-agents-bootstrap-guide.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳解專案根目錄 `AGENTS.md` 作為單一進入點的設計原理，徹底解決手動 `@Skill` 換專案失憶問題。
    2. 制定 Skills 載入的 8KB 上下文預算上限與 JIT 按需載入規則，防止多 Skill 同時掛載造成注意力稀釋。
    3. 提供相容於 Codex、Claude Code 與 Antigravity 的標準啟步協議範本。
  - **驗收標準（DoD）**：產出 `docs/codex-skills-agents-bootstrap-guide.md`，內含起步序列圖、目錄範例與預算檢驗標準；以 `Test-Path docs/codex-skills-agents-bootstrap-guide.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-30`**｜**[優先級：中]** 撰寫「AI Agent 操控 3D 與本機 GUI 軟體之雙軌橋接方案規格」收錄於 `docs/3d-gui-agent-control-bridge.md`
  - **狀態**：🟡 進行中
  - **目標範圍**：`docs/3d-gui-agent-control-bridge.md`
  - **具體做法**：
    1. 剖析大模型無法直接操作本機 3D GUI 軟體的底層原因，並解答觀眾 payson1998 提問之本質。
    2. 定義方案 A（Three.js WebGL 互動 HTML 工件渲染）之資料交換契約與適用場景。
    3. 定義方案 B（Blender Python / CLI-Anything / MCP 外部指令轉發）之架構實施指引。
  - **驗收標準（DoD）**：產出 `docs/3d-gui-agent-control-bridge.md`，涵蓋 WebGL 渲染管線與 MCP 控制架構圖；以 `Test-Path docs/3d-gui-agent-control-bridge.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-31`**｜**[優先級：低]** 撰寫「多 Agent 私有化常駐工作台與 Token 燃燒率控制指引」收錄於 `docs/desktop-agent-burn-rate-and-buzz-guide.md`
  - **狀態**：⚪ 不做（不做：內容與 T-20261026-01（模型耗額與路由速查表）及 T-20261026-27（Buzz NAS 常駐部署與心跳協議）重複，兩份文件已涵蓋部署拓撲、預算路由矩陣與心跳協議，不另寫一份。）
  - **目標範圍**：`docs/desktop-agent-burn-rate-and-buzz-guide.md`
  - **具體做法**：
    1. 整合 Buzz Nostr 類 Slack 聊天室在 NAS 私有長程常駐之最佳實踐，制定多頻道任務切片架構。
    2. 整合 Sol 6.1 vs Astra 6 燃燒率基準，提供月預算下的模型路由選擇策略與 Cache 命中配置手冊。
    3. 定義 Agent 額度耗盡（已讀不回）之自動心跳偵測與退場廣播機制。
  - **驗收標準（DoD）**：產出 `docs/desktop-agent-burn-rate-and-buzz-guide.md`，包含部署拓撲、預算路由矩陣與心跳協議；以 `Test-Path docs/desktop-agent-burn-rate-and-buzz-guide.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **額度燃燒率與模型路由**：
  - [LLM 燃燒率與 Cache 路由實測基準](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md) ｜ 關聯任務：`T-20261026-03`
- **去中心化常駐工作台與進程防線**：
  - [Block Buzz: Nostr 協同工作台](./2026-10-26-block-buzz-nostr-agent-workspace.md) ｜ 關聯任務：`T-20261026-08`、`T-20261026-27`
- **多 Agent 統一進入點與派工**：
  - [多 Agent 生產力工廠架構](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261026-28`
- **逆向合規與雲地雙軌實操**：
  - [REA 逆向工程 Agent 框架](./2026-10-19-rea-reverse-engineer-anything-agent.md) ｜ 關聯任務：`T-20261019-09`、`T-20261026-26`
- **3D 空間運算與 WebGL 工件**：
  - [3D Model Anything 空間運算](./2026-10-26-3d-model-anything-iphone-lidar-threejs.md) ｜ 關聯任務：`T-20261026-11`
