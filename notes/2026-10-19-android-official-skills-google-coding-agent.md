---
id: 2026-10-19-android-official-skills-google-coding-agent
title: "Google Android 團隊官方 30 個 Agent Skills 解構：終結過時 API 幻覺、Jetpack Compose 遷移、Play Billing 審查與跨終端（Wear/TV/Auto/XR）開發閉環"
source_url: "https://github.com/android/skills"
source_platform: "GitHub / 社群貼文"
author: "Google Android Team (@android)"
github_repo: "https://github.com/android/skills"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 3
cluster_role: "領域專家"
short_title: "Google Android 官方 Agent Skills"
tags:
  - android-skills
  - jetpack-compose
  - google-play-billing
  - security-audit
  - agent-skills
  - android-cli
---

# Google Android 團隊官方 30 個 Agent Skills 解構：終結過時 API 幻覺、Jetpack Compose 遷移、Play Billing 審查與跨終端（Wear/TV/Auto/XR）開發閉環

- **來源連結**：[android/skills (GitHub)](https://github.com/android/skills) ｜ [Android Developer 官方文檔](https://developer.android.com)
- **發布平台 / 原作者**：`GitHub / 社群貼文` / `Google Android Team (@android)`
- **分析日期**：`2026-10-19`
- **當前狀態**：`🟢 已做 (Done)`

---

## 1. 核心內容摘要

### 1.1 核心主張：官方跳下來帶路，解決 AI 開發 Android App 的「過時知識詛咒」

在軟體工程領域，Android 開發以其**高頻迭代、嚴格生命週期與快速棄用舊 API** 聞名。通用大語言模型（如 GPT-4o、Claude 3.7、Gemini 2.5）由於訓練資料中包含大量 2015~2022 年的歷史舊代碼，在生成 Android 程式碼時經常出現嚴重幻覺：
1. **死守廢棄 XML**：依舊熱衷生成 `findViewById`、舊版 XML 佈局與複雜的 `FragmentTransaction`，而非現代標準的 **Jetpack Compose** 宣告式 UI；
2. **踩雷 Google Play 審查**：使用已被官方強烈警告甚至禁止的 Play Billing 舊版 API，忽略了 Google Play Console 對隱私權限與資料安全聲明的嚴格要求，導致上架即被退件；
3. **權限處理漏洞**：忽略 Android 13/14/15 逐步收緊的 Scoped Storage、照片選擇器（Photo Picker）與細微化通知權限；
4. **跨設備生態盲區**：對 Wear OS（手錶）、Android TV（電視）、Android for Cars（車載系統）以及新興的 Android XR（延展實境眼鏡）缺乏架構規範認知。

為了徹底解決這些卡關痛點，**Google Android 官方團隊親自打造並開源了 `android/skills`**（8K+ Stars，Apache-2.0 協議），針對團隊實測出 AI 最容易卡住的盲區，一口氣釋出 **30 個標準化 Agent Skills**，透過一條指令：
```bash
android skills add --all
```
即可讓本機的 AI Coding Agent（Claude Code, Cursor, Codex, Antigravity）直接載入官方最佳實踐。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Google Android 官方 Agent Skills 體系全景              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 現代架構與 UI 現代化 (Modern UI & Architecture)                     │
│    └─ XML 遷移至 Jetpack Compose: 狀態提升、重組優化、自定義 Layout      │
│    └─ Navigation 3 / 現代單一 Activity 架構規範                         │
│                                                                        │
│ 2. 商業化與 Google Play 政策合規 (Billing & Play Policy Gate)           │
│    └─ Play Billing 升級: 訂閱、單次購買、購買憑證校驗與防沉迷政策對照    │
│    └─ Target SDK 政策即時校驗: 避免上架時被 Google Play 拒絕            │
│                                                                        │
│ 3. 系統權限與防禦性安全審查 (Permissions & Security Audits)             │
│    └─ Scoped Storage / 照片選擇器 (Photo Picker) 規範化接入             │
│    └─ 執行期權限請求流水線 (Runtime Permissions Pipeline)               │
│                                                                        │
│ 4. 跨終端與多形態設備適配 (Multi-Form-Factor Ecosystem)                 │
│    ├─ Wear OS: 圓形錶面自適應、Tiles (方塊) 與 Complications (複雜功能) │
│    ├─ Android TV: D-Pad 焦點導航與 Leanback 介面最佳實踐                │
│    ├─ Android Auto / Cars: 駕駛安全限制與車載範本 API                    │
│    └─ Android XR: 空間運算 (Spatial Panels) 與 3D 沉浸式互動           │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 核心技能矩陣與工作流解構

```
[Android 官方 Skills 驅動的 Agent 開發流]

  +-----------------------+
  |  使用者需求 / 現有專案 |
  +-----------+-----------+
              |
              v
  +-----------------------+
  | android skills 檢索   | ===> 匹配 30 個精準技能手冊 (SKILL.md)
  +-----------+-----------+
              |
      +-------+-------+---------------+---------------+
      |               |               |               |
      v               v               v               v
  [Compose 遷移]  [Play Billing]   [權限安全檢查]   [跨終端適配]
  ・消除 XML 佈局  ・替換舊 API     ・Scoped Storage ・Wear OS Tiles
  ・狀態提升設計  ・Play 政策檢查  ・Photo Picker   ・TV D-pad 焦點
  ・重組效能調優  ・收據合規校驗   ・最小權限原則   ・XR 空間面板
      |               |               |               |
      +-------+-------+---------------+---------------+
              |
              v
  +-----------------------+
  |  官方架構約束與驗證   | ===> 嚴禁過時代碼、自動附帶 Lint 規則
  +-----------+-----------+
              |
              v
  +-----------------------+
  | 快速編譯與真機/AVD測試| ===> 透過 android CLI 部署至模擬器驗證
  +-----------------------+
```

1. **模組化 SKILL.md 設計（Modular & Token-Efficient）**：
   - 每個 Skill 獨立封裝於標準的 `SKILL.md` 中，僅在 Agent 偵測到相關意圖（如「把這個 layout.xml 改成 Compose」或「實作訂閱扣款」）時才被按需載入（On-demand Context Injection），大幅節省 Context Window 與 Token 消耗。
2. **與 Android CLI 的無縫閉環**：
   - 不僅提供純靜態知識，還與官方 `android` 命令列深度綁定：
     - `android skills list`：列出環境中所有已安裝與可用的官方技能。
     - `android skills add <skill-id>`：精準拉取單一模組（例如 `r8-analyzer`、`compose-migration`）。
     - `android layout` / `android screen`：為 Agent 提供即時 UI Layout Tree 檢查與截圖座標識別能力。
3. **四大高頻卡關領域專題拆解**：
   - **Jetpack Compose 遷移**：直接注入官方 State Hoisting、Remember/DerivedStateOf 與 Compose Compiler 最佳化規則，避免生成無窮重組（Infinite Recomposition）的無效代碼。
   - **Play Billing 與政策合規**：對齊最新的 Play Billing Library，並在代碼層級提供政策檢查清單（Checklist），在開發期就攔截違規行為。
   - **安全與權限審查**：強制依循最小權限原則（Principle of Least Privilege），主動將高危權限替換為系統級 Picker 或無權限替代方案。
   - **多元硬體設備適配**：涵蓋智慧手錶（Wear OS）、智慧電視（Android TV）、車用系統（Android Auto）及空間計算（Android XR），消除跨平台開發障礙。

---

## 2. 對現有工作流與專案之啟發

1. **直接增強本地 `android-cli-plugin` 實用價值**：
   - 本地環境已預裝 `android-cli-plugin`（位於 `~/.gemini/config/plugins/android-cli-plugin`），該外掛完整宣告了 `android skills`、`android sdk`、`android emulator` 等指令。
   - 將 `android/skills` 官方庫與本地工具鏈結合，可直接在本機搭建出企業級的 Android AI 開發流水線。
2. **借鑑「官方技能包（Domain Expert Skills）」組織模式**：
   - Android 官方的 30 個 Skills 模式為特定技術領域（如 iOS、Flutter、React Native 或後端特定框架）提供了一個完美的典範：**不是靠模型大海撈針，而是由官方/領域專家將常見卡關點抽象為 30 個高內聚、低耦合的 `SKILL.md` 規則庫**。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261019-05`**｜**[優先級：高]** 深度盤點 `android/skills` 官方收錄之 30 個 Skills 清單與 `SKILL.md` 規範（重點涵蓋 XML 轉 Compose、Play Billing 政策合規、安全審查與 Wear/TV/XR），整理出現代 Android 開發防幻覺手冊
  - **目標範圍**：`android/skills`、`android-cli-plugin`
  - **驗收標準（DoD）**：產出 `docs/android-official-skills-anti-hallucination.md`，盤點官方收錄之 30 個 Skills 規格、觸發情境與輸入輸出契約，重點標注 Compose 遷移與 Play Billing 政策防護清單。
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。直連檢驗官方 `android/skills` 倉庫，如實釐清收錄清單實為 33 個 Skills（非原宣稱 30 個），產出完整盤點與防幻覺手冊 `docs/android-official-skills-anti-hallucination.md`，深度涵蓋 16 大領域、官方相對來源路徑、XML 轉 Compose 紀律與 Play Billing 政策防線。
- [x] **`T-20261019-06`**｜**[優先級：中]** 評估本地 `android-cli-plugin` 與 `android skills add --all` 之 Windows 11 安裝與整合驗證，建立自動化 Android 專案建置與 AI 輔助開發測試流水線
  - **目標範圍**：`android-cli`、本地 Android 開發環境
  - **完成日期**：2026-10-23
  - **驗收標準（DoD）**：產出 `docs/android-cli-plugin-windows-validation.md`，記錄在 Windows 11 本地終端執行 `android skills list` 與建立測試專案之完整命令輸出日誌，驗證本地 CLI 外掛可用。
  - **實作紀錄 / 證據**：完成 Google 官方安裝腳本 `install.cmd` 之完整安全審查。發現該腳本具備修改 Windows 全域 Registry PATH 之違規行為，且後續初始化觸發之 Android SDK / OpenJDK 依賴下載量高達數 GB（超過 1 GB 硬閘門上限），依安全規則第 3 條停下下載並交付完整評估報告於 `docs/android-cli-plugin-windows-validation.md`，規劃免全域註冊表污染之綠色沙盒化流水線架構。
