---
id: "2026-11-15-hujiaxi-24x7-local-agent-cluster-architecture"
title: "胡嘉璽 24×7 地端多機 Agent 實戰架構：Remote Control、Herdr + Tailscale、Git 技能同步與 Windows 11 落地評估"
source_url: "https://code.claude.com/docs/en/remote-control"
source_platform: "Facebook (Generative AI 技術交流中心)"
author: "胡嘉璽（作者宣稱，原貼文未獨立查證）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
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

- **來源連結**：[官方 Remote Control](https://code.claude.com/docs/en/remote-control) ｜ [terminal README](https://raw.githubusercontent.com/SuperCodeAgents/herdr-terminal/master/README.md) ｜ [core README](https://raw.githubusercontent.com/herdrdev/herdr-core/master/README.md) ｜ [Git 官方 pull 文件](https://git-scm.com/docs/git-pull) ｜ [Tailscale unattended 官方文件](https://tailscale.com/docs/how-to/run-unattended) ｜ [Facebook 原貼文（來源頁 Cache miss，未查證）](https://www.facebook.com/groups/gaitech/permalink/1840405647143642/)
- **發布平台 / 作者**：`Facebook 公開社團` / `胡嘉璽`（原貼文網頁工具 Cache miss 未能獨立取得；3 台 Mac、8 個 Tart VM、2 個 Ultra 帳號等細節屬作者宣稱，未經獨立查證）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（Herdr 終端復用與 Magpie 網關）
  - [`docs/buzz-nas-deployment-and-heartbeat-spec.md`](../docs/buzz-nas-deployment-and-heartbeat-spec.md)（NAS 24×7 常駐中樞與心跳規格）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（多代理與排程架構）

---

## 1. 核心內容摘要（5W1H 初篩與實查）

- **Who / What**：原作者分享其「24×7 全時運行地端 Agent 架構」（3 台 Mac、8 個 Tart VM、2 個 Claude Code Ultra 帳號等硬體規模為作者宣稱，未經獨立查證，不作為維護者現況）。
- **Why（作者宣稱之純雲端限制）**：
  - 原作者提及「純雲端無法存取本機／NAS」：此屬該案例未配置所需通道或授權之限制（作者宣稱），不能概括推導為所有雲端架構均無法透過受控 connector、VPN 或代理存取本機。
- **How（核心技術實查與邊界）**：
  1. **Claude Remote Control 實查**：官方確有此功能（`claude remote-control` 或 `/remote-control`），但需符合訂閱與登入條件，API key 不支援。工作仍於本機執行，僅建立對外 HTTPS，無須新增入站防火牆規則，亦非將 Tailscale 視為必要依賴。「所有 session 預設開啟」為可選設定而非通用既定事實。主機與本機程序仍需存活，自動重連無法保證停電或休眠期間持續運作。
  2. **Herdr 終端復用實查**：不可無版本區分地宣稱「無縫替換 PowerShell」。舊版 terminal README 僅支援 Linux/macOS；現行 `herdr-core` README 雖具 Windows x86_64 二進位檔，但部分模板與 quoted shell command 仍依賴 `sh` 環境。此屬元件與版本差異，需固定元件、版本與 Windows 前提。
  3. **共享儲存與 Git 技能同步（安全邊界）**：
     - 多 session 共享 NAS 或目錄交換。
     - **「唯讀同步」概念糾正**：`git pull --ff-only` 仍會寫入並更新工作樹；`git fetch` 亦會寫入 `.git`。fast-forward 僅代表線性合併，不等於只讀、不等於安全審查、不等於技能熱更新；dirty tree 檢查亦無法防禦拉進惡意 hooks 或技能。憑證、本機設定與私有記憶絕不可與共享技能混雜同步。

### 1.1 CQR 論證檢驗（Claim - Evidence - Reasoning）
- **主張（Claim）**：地端多機 Agent 透過 Remote Control 與排程同步可構建持續運作工作流，需評估 Windows 11 落地規格。
- **證據（Evidence）**：[官方 Remote Control](https://code.claude.com/docs/en/remote-control)、[Git 官方 pull 文件](https://git-scm.com/docs/git-pull)、[Tailscale unattended 官方文件](https://tailscale.com/docs/how-to/run-unattended)、[core README](https://raw.githubusercontent.com/herdrdev/herdr-core/master/README.md)；Facebook 貼文 Cache miss（未查證）。
- **推論（Reasoning）**：Remote Control 具備官方基礎，但不能由 AI 代改電源與系統安全；Git ff-only 並非唯讀亦無法保證熱更新安全；Windows 落地須以唯讀腳本與人工規格為交付邊界。

---

## 2. 啟發與適用性評估（對照本機 Windows 11 基建）

- **已有且可對接的本機資產**：
  - **Git 版控共用規則與 Skills**：已建置 `SanHsien/agent-assets`（私有）（SSOT），結構完整。
  - **結構化交接**：已具備 `agent-handoff`（`dropoff` / `pickup`）與 `checkpoint`。
  - **跨代理派工**：`SanHsien/agent-relay` 已具備跨終端派工與驗收機制。
- **交付邊界與安全鐵律**：
  1. **禁止代改系統設定**：自動登入非 24×7 必然條件；AI 嚴禁修改電源、NIC、休眠、防火牆、登錄檔、服務、Task Scheduler、Tailscale 或遠端控制設定。Tailscale 無人值守運行須由維護者手動設定，不自動停用 key expiry。
  2. **安全閘門提醒**：嚴禁全域關閉沙盒或繞過權限檢查。
  3. **Windows 三問核對**：
     - *同生共死*：同機 session 內的 loop 無法偵測主機休眠或離線，規格須揭露盲區。
     - *既有機制*：已有 Windows Task Scheduler 與資產漂移檢查（已有相關流程文件；實際排程是否啟用尚未查證），relay 亦有輪詢機制，不重造同步 daemon。
     - *Windows 原生*：優先原生 PowerShell／Python 查詢；Herdr 須註明版本與 `sh` 前提。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-20`**｜**[優先級：中]** 產出 Windows 11 常駐 Agent 維運規格與唯讀現況檢查，不代改系統設定
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/windows-24x7-agent-ops-spec.md`、`tools/inspect_windows_agent_ops.ps1`、`tests/test_inspect_windows_agent_ops.ps1` 與 `docs/evidence/windows-agent-ops-readonly-check.md`。
  - **具體做法**：依官方來源整理電源、登出／重啟、自啟動、Remote Control 與選用 Tailscale 的前提、人工設定／回復步驟及 Windows 三問。腳本只用具名白名單查詢電源狀態、必要服務與既有任務狀態、程式版本；僅向 stdout 輸出最小去識別摘要，缺權限／缺程式標 unknown／not-installed。不得修改電源、NIC、休眠、防火牆、registry、service、Task Scheduler、遠端控制設定，也不建立遠端 session、不讀憑證或全量列舉程序／排程。明確區分官方 Remote Control 與 VPN 終端通道，不預設自動登入。以 mock 測試腳本的正常、未安裝、拒絕存取及查詢逾時分支，不加入第三方測試相依套件。
  - **驗收標準（DoD）**：四個具名產出存在；Windows 原生執行唯讀腳本一次並記錄命令、exit code、去識別結果與 unknown。腳本測試驗證白名單查詢及輸出不含識別資訊，檢查程式無系統設定／憑證讀取／遠端啟用動作；focused 檢查與 repo 規定檢查有結果。文件給維護者一份有停止條件的人工驗收表，分清外網連線、鎖屏／登出／重啟恢復與有界限觀察期，不以一次成功稱 24×7 穩定。維護者尚未執行的項目明標待執行，**不屬本次文件／唯讀工具 DoD，也不得宣稱部署完成**。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/windows-24x7-agent-ops-spec.md、tools/inspect_windows_agent_ops.ps1、tests/test_inspect_windows_agent_ops.ps1、docs/evidence/windows-agent-ops-readonly-check.md。檢查腳本只讀現況；測試擋下成員賦值、危險型別建構（New-Object、::new、型別轉換共用一份清單）、任意程序啟動與外部 Kill，共 1486 項斷言、16/16 mutation killed；複驗員的 13 個繞法全部被拒。實際設定與人工恢復驗收由維護者執行，已列入 ROADMAP。複審兩輪後通過。

- [x] **`T-20261115-21`**｜**[優先級：低]** 唯讀評估共享技能跨機更新與既有發布流程的缺口，不建立自動拉取排程
  - **目標範圍**：唯讀檢閱 `SanHsien/agent-assets`（私有）既有發布／漂移檢查與 `SanHsien/agent-relay` 的同步責任；公開產出限 `SanHsien/ai-inbox` 的 `docs/agent-assets-cross-machine-sync-assessment.md`，只寫抽象結論。
  - **具體做法**：列清 canonical repo、核准版本、consumer 副本、已載入 session 四個不同階段；對照既有機制，先判斷是否真有跨機需求。用 Windows 三問評估排程身份、生命週期、非互動認證與獨立觀察盲區。不執行 fetch／pull、不讀 credential store、不新增排程、常駐程式或同步腳本。規格區分人工核准後的更新操作與唯讀比較；提出 dirty tree、diverged branch、來源錯誤、離線、審查未通過與並行更新時的停止規則，不預設 stash／reset／merge。共享交換目錄不得包含 native 設定、token、cookies、私鑰或私有記憶，不以 NAS 共享取代權限邊界。
  - **驗收標準（DoD）**：具名報告存在，含資料流 ASCII 圖、既有能力重疊表、Windows 三問逐項答案、憑證／公開隱私邊界、owner、人工更新與回復規格，以及採納／暫緩／不採納結論。有更新需求才描述下一階段的維護者執行驗收；若無新增價值，允許以不新增機制的結論完成本評估。至少列 dirty／diverged／離線三個合成情境的預期決策，明標設計案例而非實測；保存 repo 文件檢查結果。不得宣稱已完成跨機同步、技能部署或排程實測。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/agent-assets-cross-machine-sync-assessment.md 只寫抽象結論。建議沿用既有發布與漂移檢查，暫緩新增自動拉取排程（git pull 不是唯讀，更新 repo 也不等於部署技能）。獨立複審通過。
