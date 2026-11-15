---
id: "2026-11-15-hujiaxi-24x7-local-agent-cluster-architecture"
title: "胡嘉璽 24×7 地端多機 Agent 實戰架構：Remote Control、Herdr + Tailscale、Git 技能同步與 Windows 11 落地評估"
source_url: "https://www.facebook.com/groups/gaitech/permalink/1840405647143642/"
source_platform: "Facebook (Generative AI 技術交流中心)"
author: "胡嘉璽"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 1
cluster_role: "24x7常駐Agent"
short_title: "24x7地端Agent架構"
tags:
  - 24x7-agent
  - remote-control
  - herdr
  - tailscale
  - claude-code
  - multi-agent
  - nas
---

# 胡嘉璽 24×7 地端多機 Agent 實戰架構：Remote Control、Herdr + Tailscale、Git 技能同步與 Windows 11 落地評估

- **來源連結**：[Facebook 原貼文（Generative AI 技術交流中心）](https://www.facebook.com/groups/gaitech/permalink/1840405647143642/)
- **發布平台 / 作者**：`Facebook 公開社團` / `胡嘉璽`
- **分析日期**：`2026-11-15`
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（Herdr 終端復用與 Magpie 網關）
  - [`docs/buzz-nas-deployment-and-heartbeat-spec.md`](../docs/buzz-nas-deployment-and-heartbeat-spec.md)（NAS 24×7 常駐中樞與心跳規格）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（多代理與排程架構）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：開發者暨講者胡嘉璽分享其從「龍蝦 → Hermes → 回歸 Claude Code」後的 **24×7 全時運行地端 Agent 架構**（3 台 Mac＋外接 TB4/TB5 NVMe＋8 個 Tart VM，分掛於 2 個 Claude Code Ultra 帳號；區網另有 PVE Cluster 跑數十台 Windows／Linux VM 與 NAS）。
- **Why（為何放棄純雲端 Agent）**：
  - 曾測試 Muse、Dot、Grok Bot、Duet 等雲端 VM 產品，但**純雲端無法存取本機檔案與區網內 PVE 虛擬機／NAS 服務**，與真實開發、寫書、講義、資料搜集與日常瑣事自動化無法配合。
  - 必須解決「主機休眠就斷線」與「外出時無法即時遙控」兩大痛點，才能讓 Agent 真正 24×7 運作。
- **How（三大核心支柱＋多代理協作機制）**：
  1. **主力工具與不斷線實體環境**：以 Claude Code Ultra 作為 24×7 背景執行主力（ChatGPT Pro 輔助查問題）；透過獨立實體機＋不休眠設定確保持續在線。
  2. **Claude Web Remote Control（預設開啟）**：出差／外出時直接用筆電瀏覽器或手機透過 Web Remote Control 即時遙控與編輯區網內 Agents，大幅減少開啟 RDP / VNC / SSH。
  3. **Herdr App + Tailscale（預設終端與內網穿透）**：將 Herdr 設為開機自動啟動預設終端機（取代 iTerm2 / Ghostty / PowerShell / tmux），搭配 Tailscale 打通跨網遠端管理（作者稱 90% 工作時間都在 Herdr 內）。
  4. **跨 Agent 記憶、共享儲存與技能同步**：
     - 任務盡量獨立分工；跨 session 記憶仰賴內建 cross-session memory（留言亦補充每次結束寫交接紀錄）。
     - 所有 Agent 掛載同一個 **區網 NAS 資料夾**進行讀寫交換。
     - **共用技能（Agent Skills）推上 Git 版控**，各 Agent 定時自動拉取同步更新。

---

## 2. 啟發與適用性評估（對照本機 Windows 11 基建）

- **已有且可無縫對接的本機資產**：
  - **Git 版控共用規則與 Skills**：已建置 `C:\GitHub\agent-assets`（SSOT），結構比單純散落各機的 Skill 更完整，只差「排程定時自動 `git pull` 同步」。
  - **結構化交接**：已具備 `agent-handoff`（`dropoff` / `pickup`）與 `checkpoint`，無須從零手寫會議紀錄交接法。
  - **跨代理派工**：`SanHsien/agent-relay` 已能跨終端／代理派工與驗收。
- **達成 Windows 11「24×7 常駐 Agent」仍需補齊的關鍵實作**：
  1. **電源不斷線與常駐服務化**：Windows 11 主機必須明確鎖定電源計畫（AC 不休眠、停用睡眠／休眠）、設定自動登入／鎖屏不休眠，並讓常駐中樞（如 `agent-relay`／Herdr／Scheduled Task）具備開機自啟動與斷線重連能力。
  2. **安全遠端遙控通道實測**：
     - 在 Windows 11 實測 **Claude Code Remote Control（Web／行動端）** 與 **Tailscale** 搭配 **Herdr（或 Windows Terminal / SSH）** 的實際穩定度。
     - **安全閘門提醒**：24×7 背景運行若搭配預設權限，必須確保外部 `harness-guard` 與 `RULE[user_global]` 專案外讀寫攔截始終生效，不可為了圖方便而常駐開啟 `--dangerously-skip-permissions` / 繞過沙盒。
  3. **`agent-assets` 定時自動同步**：透過 Windows Task Scheduler 定時執行只讀 `git pull --ff-only`（不自動 merge 衝突），讓所有常駐對話或工作機隨時保有最新規則與技能。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-20`**｜**[優先級：高]** 制定並實測《Windows 11 24×7 常駐 Agent 維運規格》（防休眠電源、開機自啟動、Tailscale 與 Claude Remote Control 遠端控制）
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\windows-24x7-agent-ops-spec.md` 與本機 Windows 11 常駐服務環境
  - **具體做法**：
    1. 盤點並設定 Windows 11 防休眠／防斷網電源參數（AC 模式不睡眠、NIC 不省電斷線）。
    2. 實測 Claude Code `Remote Control` 搭配本機常駐 session，以及 `Tailscale` 內網穿透連回本機終端／`agent-relay` 的連線穩定度與斷線復原。
    3. 明訂 24×7 無人值守下的安全邊界（嚴禁全域關閉沙盒／權限檢查，維持 `harness-guard` 攔截與任務配額上限）。
  - **驗收標準（DoD）**：完成規格文件撰寫，並實測從外部裝置（或同網段不同終端）透過 Remote Control / Tailscale 成功檢視並操控本機常駐 Agent，無休眠斷線或安全護欄失效情形。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*

- [ ] **`T-20261115-21`**｜**[優先級：中]** 建立 `SanHsien/agent-assets` 定時唯讀同步腳本與跨機共享目錄規範
  - **目標範圍**：`C:\GitHub\agent-assets`（同步腳本）與 Windows Task Scheduler
  - **具體做法**：
    1. 撰寫安全的定時同步腳本（僅執行 `git fetch` + `git pull --ff-only`，若工作區有未提交變更則安全跳過並寫入 log，避免覆蓋本地修改）。
    2. 評估多 Agent 共享輸出交換目錄（本機／NAS 共享區）與既有專案目錄隔離原則的寫入白名單規範。
  - **驗收標準（DoD）**：同步腳本於 Windows 11 排程實測成功執行且不破壞本地未提交修改，完成說明文件更新。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
