---
id: 2026-10-18-claude-code-mods-self-extending-runtime
title: "Claude Code Mods 自體改造機制解構：從外部腳本 Hook 到 In-Session 中介軟體（Middleware）、動態 UI 渲染與即時熱重載"
source_url: "https://claude.dev/blog/getting-started-with-claude-code-mods/"
source_platform: "Anthropic Official Blog & X"
author: "Addy Osmani (Anthropic) & @NFT_Chen"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: archived
cluster: 3
cluster_role: "自體改造"
short_title: "Claude Code Mods"
tags:
  - claude-code
  - claude-mods
  - in-session-middleware
  - ui-render
  - runtime-extension
  - blast-radius
  - token-weather
  - security-interception
---

# Claude Code Mods 自體改造機制解構：從外部腳本 Hook 到 In-Session 中介軟體（Middleware）、動態 UI 渲染與即時熱重載

- **來源連結**：
  - [Anthropic 官方入門教學 (claude.dev Blog)](https://claude.dev/blog/getting-started-with-claude-code-mods/)
  - [Anthropic 官方說明 (claude.com Blog)](https://claude.com/blog/claude-code-mods)
  - [社群貼文分析 (@NFT_Chen on X)](https://x.com/NFT_Chen/status/2105738805785596166)
- **分析日期**：`2026-10-18`
- **當前狀態**：`⚪ 封存不做 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-plugins-official-directory.md`](./2026-10-17-claude-plugins-official-directory.md)（Claude Code 插件生態）
  - [`notes/2026-10-18-desktop-sense-local-screen-context.md`](./2026-10-18-desktop-sense-local-screen-context.md)（Hook 螢幕注入）
  - [`notes/2026-10-17-model-routing-opusplan-advisor.md`](./2026-10-17-model-routing-opusplan-advisor.md)（模型路由策略）

---

## 1. 核心內容摘要與技術深挖

### 1.1 什麼是 Claude Code Mods？
Anthropic 在 **Claude Code 2.1.287+** 正式開放了 **Mods（外掛模組自體擴充架構）**。
這標誌著 AI 終端編程工具從「只能使用官方寫死功能」跨入「**開發者可用程式碼深度改造 AI 執行期行為與終端 UI**」的新紀元。

過去開發者若要調整行為，僅能依賴 `hooks.json` 呼叫外部 Shell 腳本傳遞 JSON，每觸發一次就啟動一次短暫進程，延遲高、無法維持狀態且無法繪製介面。
而 **Mods** 是常駐於 Claude Code 執行期的 JavaScript / TypeScript 模組（In-Session Runtime Modules），具備**中介軟體鏈式調度（Middleware Chain）**、**宿主狀態記憶（`$.state`）**、**自定義終端 UI 渲染（`ui.render`）** 與 **即時熱重載（Hot Reload）**。

```text
┌────────────────────────────────────────────────────────────────────────┐
│             Claude Code Mods 執行期鏈式中介軟體 (Middleware) 架構       │
└────────────────────────────────────────────────────────────────────────┘

 [ 觸發事件 (如 tool.call: Bash, ui.render, turn.complete) ]
                            │
                            ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 你的 Mod (Your Mod Hook: register(on))                                │
 │ ├─ 1. Observe (觀察): const r = await next(e); 記錄統計 / 收集數據     │
 │ ├─ 2. Rewrite (改寫): return next({ ...e, command: saferCmd });       │
 │ └─ 3. Answer / Intercept (攔截): return { deny: "高危禁止" } (不 call next)│
 └──────────────────────────┬────────────────────────────────────────────┘
                            │ next(e) 傳遞
                            ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 其他已安裝之社區 / 官方 Plugins (如 next-steps, desktop-sense)        │
 └──────────────────────────┬────────────────────────────────────────────┘
                            │ next(e) 傳遞
                            ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ Claude Code 核心引擎 (底層終端工具執行 / 預設渲染)                   │
 └───────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 五大核心亮點與底層 API 機制

#### 1. 改寫行為（Behavior Interception & Rewrite）
- **攔截高危指令**：透過 `on("tool.call", { tool: "Bash" }, async ($, e, next) => ...)`，在指令執行前進行靜態分析。若檢測到高危刪除（如 `rm -rf`、`Drop Table`），可直接 `return { deny: "..." }`，不呼叫 `next(e)`，直接在終端阻絕風險。
- **敏感資訊脫敏**：在 Prompt 提交或工具輸出時自動過濾 API Key 或私密憑證。

#### 2. 自定義終端與桌面介面（`ui.render`）
- 過去終端 UI 完全由官方寫死。Mods 支援掛接 `ui.render` 事件，透過 `$.ui.resolve(e)` 取得 `Box`、`Text` 等元件建構自定義介面：
  - **`AbovePrompt`**：在輸入框上方插入自定義資訊列（如官方範例 **Token Weather**，即時以氣象圖標 ☀/☁/☂/☇ 與條形圖展示 Context 飽和度）。
  - **側邊面板與 Diff 視圖**：自定義程式碼差異展示器。
  - **下一步建議（Next Steps）**：官方社區插件在對話結尾動態生成 3 個可點擊執行的後續行動按鈕。

#### 3. 自然語言驅動自體改寫與即時熱重載（Hot Reloading）
- 開發者甚至**不需要手寫代碼**！在 Claude Code 對話中直接說：「*幫我做一個 Token Weather mod，在輸入框上方顯示當前 Context 百分比*」。
- Claude 會自動在本地建立 `.claude-plugin/plugin.json` 與 `hooks/token-weather.mjs`，並提示開發者開啟 Hot Reload。
- 一旦儲存檔案，**不需重開終端，新介面與邏輯立刻原地生效**！

#### 4. 宿主級狀態管理（`$.state`）
- 在熱重載或多次 Turn 之間，傳統模組變數會被重置。
- Mods 提供 `$.state.get(key)` 與 `$.state.set(key, val)`，將歷史狀態（如過去 12 次 Turn 的 Token 消耗曲線）保存在宿主進程中，即便 Mod 代碼重新編譯載入，歷史資料依然完好如初。

#### 5. 自動派生背景小助手（Background Turn Assistants）
- 在 `turn.complete` 時，Mod 可在背景開闢無干擾的分身進程（Sub-agent）自動整理會議筆記、同步文獻或執行程式碼靜態掃描，完全不佔用主對話線路。

---

### 1.3 官方經典 Mod 案例解構

1. **Token Weather（上下文氣象站）**：
   - 僅約 80 行代碼，掛接 `AbovePrompt`。
   - 依據 `$.session.usage()`，在 `<25%` 顯示 ☀ Clear，`50-74%` 顯示 ☂ Showers，`>90%` 顯示 ↯ Compact soon，並繪製 ▁▂▃▄▅ 迷你字元走勢圖。
2. **Blast Radius（爆炸半徑安全守門員）**：
   - 攔截 `Bash` 工具中的刪除類指令（如 `rm -rf build`）。
   - 在執行前先展開計算將會被刪除的檔案清單與數量，在介面上彈出預覽卡，確認無誤後才放行。
3. **Replay Theater（重播劇場）**：
   - 逐步回放複雜重構（如變數重新命名）的影響節奏。

---

## 2. 對現有系統的啟發與適用性評估

- **對應現有系統 / 專案**：
  - **Windows 11 原生相容性**：
    Claude Code Mods 為跨平台 JavaScript/TypeScript 規範，在 Windows 11 下透過 Node.js 執行，路徑支援標準相容。
  - **大幅強化全域防護（`RULE[user_global]`）**：
    全域規範要求「嚴禁在專案目錄外讀寫或刪改」、「API Key 不得洩漏」。過去只能靠提示詞約束（Soft Barrier），現在可直接透過 Mod 實作**機械級硬閘門（Hard Barrier）**，在 `tool.call` 階段由程式碼直接拒絕違規行為！
  - **與 `desktop-sense`（筆記 20）聯動**：
    `desktop-sense` 原本以 external hook 注入畫面 context，未來可直接重構成為標準 Claude Code Mod，以常駐中介軟體的形式獲得更低延遲與更豐富的終端介面展現。

- **落差與採納判斷**：
  - **極高優先級採納**：
    1. 在本機驗證 Claude Code Mods 運作環境（升級 Claude Code 至 2.1.287+）。
    2. 打造符合全域規則之「安全防護與 Context 視覺化 Mod」。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [ ] **`T-20261018-09`**｜**[優先級：低]** 在 Windows 11 本地測試 Claude Code Mods 執行期機制（驗證 Hot-Reload、`AbovePrompt` UI 渲染與 `$.state` 持久化）
  - **目標範圍**：本地 Claude Code 開發環境與外掛架構
  - **狀態**：⚪ 不做（Claude Code 官方已轉向標準 Plugins 架構，非官方 Mods 機制過時且維護風險高）
  - **具體實作步驟**：
    1. 檢查並確保本機 Claude Code 版本符合 `>= 2.1.287`（`claude --version`）。
    2. 參考官方 `token-weather` 樣板，在本地建立第一個測試 Mod，驗證 `AbovePrompt` 介面渲染。
    3. 實測熱重載（Hot Reload）機制，驗證修改 `.mjs` 檔案後終端 UI 是否即時原地刷新。
    4. 驗證 `$.state` 在熱重載前後的數值持久性。
  - **驗收標準（DoD）**：在本地 Claude Code 終端成功渲染出自定義上下文狀態列，且熱重載能即時更新無拋錯。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261018-10`**｜**[優先級：低]** 評估將全域高危指令攔截（Blast Radius）與安全規範包裝為本地 Claude Code Mod 防護插件
  - **目標範圍**：全域安全規範（`RULE[user_global]`）機械防線
  - **狀態**：⚪ 不做（高危防護已在 harness-guard 與 agent-relay/gates.py 透過原生 Hook/閘門實現，不依賴 Mods）
  - **具體實作步驟**：
    1. 實作 `Bash` 工具攔截器：比對目錄邊界，阻止超出 `C:\GitHub\` 之外的刪除或高危指令。
    2. 實作 API Key 與金鑰即時打碼改寫器（Rewrite Hook）。
    3. 將全域硬閘門從單純提示詞層級，提升為 Mod 中介軟體機械阻擋層。
  - **驗收標準（DoD）**：產出 `safe-guard-mod` 插件，在 Claude Code 嘗試執行非預期高危指令時能主動中斷並於終端輸出警告。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---
