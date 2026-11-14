---
id: "2026-11-13-hao0321-editkin-free-ai-video-editor-windows"
title: "Editkin：免費 Windows 本地優先 AI 剪輯器（0.16 起轉閉源 freeware，原始碼凍結於 0.15）"
source_url: "https://www.threads.com/share/BATqCv2_uX"
source_platform: "threads"
author: "@hao0321_studio"
analyzed_at: "2026-11-13"
analyzed_by: "antigravity"
status: archived
cluster: 2
cluster_role: "AI影片剪輯"
short_title: "Editkin免費AI剪輯"
tags:
  - editkin
  - video-editing
  - local-first
  - mcp
  - editgraph
  - freeware
  - windows
  - video-autopilot
  - claude-code
  - codex
---

# Editkin：免費 Windows 本地優先 AI 剪輯器（0.16 起轉閉源 freeware，原始碼凍結於 0.15）

- **來源連結**：[Threads 貼文：@hao0321_studio](https://www.threads.com/share/BATqCv2_uX)
- **發布平台 / 作者**：`threads` / `@hao0321_studio`
- **分析日期**：`2026-11-13`
- **當前狀態**：`⚪ 不做 (Archived)`

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：作者 Hao0321（倉庫 `Hao0321/Editkin`）。
- **What**：Windows 本地優先 AI 剪輯器，可編輯時間軸 + EditGraph + MCP 命令。
- **Why**：把 AI 規劃落到可編輯時間軸，而非一鍵黑盒出片。
- **How**：Editkin 出引擎、Agent 做決策（見下方技術架構）。
- **When & Where**：Windows x64 桌面；v0.17.0 安裝檔約 1.5 GB（2026-11-14 以 GitHub API 查證）。
- **Key Metrics / Numbers**：122 stars、GPL-3.0（原始碼版，快照日 2026-11-14 查證）；最新 Release v0.17.0（2026-11-12）。

### 摘要原文

**@hao0321_studio**（2026-11-05，2.1K views）以一句話介紹「完全免費 AI 自動剪輯 Editkin（Windows）」。貼文本身資訊極少，以下內容來自官方倉庫 `Hao0321/Editkin`、Release 附件與 EULA 的實查。

核心事實：

- Editkin 是 **local-first** 影片編輯器：可編輯時間軸 + 共用 `EditGraph` + 給 AI 工具的結構化命令（MCP）。
- **授權在 0.16.0 轉折**：2026-11-05 起新版為免費閉源 freeware（可商用、永久免費）；公開原始碼凍結於 `0.15.0-preview.20261029`，維持 GPL，**不再更新**。
- 最新 Release `v0.17.0`（2026-11-12），Windows x64 安裝檔 **約 1.5 GB**，附 `SHA256SUMS.txt`。

---

## 技術架構深挖

### 倉庫結構（`Hao0321/Editkin`，122 stars，GPL-3.0，社群源碼版）

```
Hao0321/Editkin
├── src/            # 前端 UI + core TypeScript（EditGraph、時間軸）
├── src-tauri/      # Tauri（Rust）桌面殼
├── electron/       # Electron 殼（forge.config.cjs）
├── native/         # 原生媒體層（FFmpeg / Whisper 對接）
├── plugins/ config/ assets/ docs/ scripts/ spikes/
├── AGENTS.md / CLAUDE.md          # agent 指引
├── PUBLIC_SOURCE_MANIFEST.json    # 公開源碼清單
├── video-autopilot-skill-integration.json
└── TRADEMARKS.md                  # 官方品牌與簽章由維護者控管
```

### 自動剪輯機制：Editkin 出引擎，Agent 做決策

```
素材（有人講話的橫式影片）
     │
     ▼
Agent（Codex / Claude Code / 其他 MCP agent）
  讀 Video Autopilot Kit（Hao0321/video-autopilot-kit）
  ├─ 規則：資訊密度剪輯規劃、效果來源對照
  └─ 設定 EDITKIN_VIDEO_AUTOPILOT_SKILL → codex-skill/video-autopilot/SKILL.md
     │  MCP（npm run mcp，本機）
     ▼
Editkin 本機 MCP tools：prepare → audit → apply → render
     │
     ▼
可編輯 v4 plan（EditGraph）→ 人可在時間軸手動微調
```

重點設計：

- **Skill 綁定與變更檢查**：Editkin 把選定的 Skill 與其 workflow contract 綁進 plan，套用前再次檢查是否被改動。
- **audited v4 plan**：AI 的輸出先審計再套用，不是黑盒直出成品。
- **簡單模式**：不需外部 AI 帳號即可做基礎粗剪；進階流程才接 MCP agent。
- **瀏覽器版限制**：只能匯入、預覽、編輯時間軸；無法渲染，「Export project」只下載 EditGraph JSON，重新整理即丟失專案。語音轉錄（Whisper）與媒體分析需桌面版。
- **動態預設**：浮動影片框（邊緣柔化）、人像透視 orbit、雙人像背景面板；為 2.5D 透視平面，非 3D mesh。

### EULA 要點（v1.0，2026-11-05）

> 下表摘自 Release 附件 EULA，未逐條核對。

| 條款 | 內容 |
|------|------|
| 授權 | 免費、永久、可商用、任意台數 |
| 作品權利 | 產出影片/字幕/專案檔歸使用者 |
| 內建素材 | 可用於自己的作品；不得單獨轉售或做成素材庫；標示「AI 生成」者發佈時依平台規定揭露 |
| 限制 | 禁反組譯、禁散布修改版、禁出售/出租、禁用於製作競品 |
| AI 旁白 | 只能用本人或已取得同意者的聲音，禁冒充/詐騙 |
| 第三方 | 含 GPL 的 FFmpeg（附取得方式），見 THIRD_PARTY_NOTICES.md |
| 準據法 | 中華民國（台灣）法 |

---

## 風險與疑點

| 項目 | 評估 |
|------|------|
| **開源變閉源** | 「開源」宣傳需修正：目前主線是 freeware，原始碼停在 0.15；GPL 凍結版可 fork 但無官方更新 |
| **未簽章** | 0.15 preview 為 unsigned，會觸發 Windows SmartScreen；0.17.0 簽章狀態未實測 |
| **安裝檔 1.5 GB** | 內含媒體 runtime/模型，下載與磁碟成本高 |
| **閉源二進位** | 無法審計；MCP 工具有本機檔案與渲染權限，屬高權限工具 |
| **第三方衍生套件** | `geniefu/editkin-video-autopilot`（0 stars，自稱 Antigravity 整合 + 64 MCP tools）非官方，依零信任規則不安裝、不執行 |
| **Kit 遷移** | Video Autopilot Kit 近版更改預設資料夾名稱，升級前需看 CHANGELOG 遷移段 |
| **未驗證** | 剪輯品質、0.17.0 安裝檔簽章與 SHA256 實比對、MCP 實際可用性均未實測 |

---

## 2. CQR 深入論證檢驗（選填）

- **Claim**：免費、本地優先、可商用的 AI 自動剪輯器。
- **Evidence**：Release 附件 EULA 與 `SHA256SUMS.txt` 存在（API 查證）；EULA 條款未逐條核對；剪輯品質未實測。
- **Reasoning**：授權由 GPL 轉閉源 freeware，二進位無法審計；證據只涵蓋「存在與條款文字」，不涵蓋功能與安全。

---

## 3. 啟發與適用性評估

### 與本機防線對照

- 官方來源明確（作者倉庫與 Releases 均為 `Hao0321`），EULA 可讀、無強制遙測條款，但為閉源二進位。
- 若要試用：先核對 `SHA256SUMS.txt`，在隔離環境（VM 或 Simular Box 類）安裝，MCP 僅接本機、不給雲端 agent 長期權限。
- 與 `jackiechin073` 等筆記的「Agent 技能包」路線互補：Editkin = 引擎，Video Autopilot Kit = 技能層。

---

### 評估結論與處置

**評分：⭐⭐⭐（3/5）**

「AI 規劃落到可編輯時間軸」的設計比一鍵黑盒出片更實用，EULA 對商用友善。扣分：授權由 GPL 轉閉源、安裝檔大、簽章與實際剪輯品質未驗證，且貼文只有一句話，不構成可複製的做法。

**處置**：僅歸檔備查；無可驗收的具體任務，不衍生待辦。若日後試用，建議先比對 `SHA256SUMS.txt` 並在隔離環境安裝（原核取清單因無可驗收 DoD 已刪除）。

---

## 4. 拆解待辦事項（Action Items）

無（零任務判斷：維持歸檔）。

**參考連結**：
- 倉庫：https://github.com/Hao0321/Editkin
- Releases：https://github.com/Hao0321/Editkin/releases
- Skill Kit：https://github.com/Hao0321/video-autopilot-kit
