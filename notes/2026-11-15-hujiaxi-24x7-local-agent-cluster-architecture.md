---
id: "2026-11-15-hujiaxi-24x7-local-agent-cluster-architecture"
title: "胡嘉璽 24×7 地端多機 Agent 實戰架構：Remote Control、Herdr + Tailscale、Git 技能同步與 Windows 11 落地評估"
source_url: "https://code.claude.com/docs/en/remote-control"
source_platform: "Facebook (Generative AI 技術交流中心)"
author: "胡嘉璽"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
cluster: 1
cluster_role: "24x7常駐Agent"
short_title: "24x7地端Agent架構"
source_reviewed_at: 2026-11-17
source_review: full
source_images: 7
source_replies: 34
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

- **來源連結**：[官方 Remote Control](https://code.claude.com/docs/en/remote-control) ｜ [terminal README](https://raw.githubusercontent.com/SuperCodeAgents/herdr-terminal/master/README.md) ｜ [core README](https://raw.githubusercontent.com/herdrdev/herdr-core/master/README.md) ｜ [Git 官方 pull 文件](https://git-scm.com/docs/git-pull) ｜ [Tailscale unattended 官方文件](https://tailscale.com/docs/how-to/run-unattended) ｜ [Facebook 原貼文](https://www.facebook.com/groups/gaitech/permalink/1840405647143642/)（2026-11-17 已用瀏覽器讀到全文、圖片與留言）
- **發布平台 / 作者**：`Facebook 公開社團` / `胡嘉璽`（2026-11-14 發文；3 台 Mac、8 個 Tart VM、2 個 Ultra 帳號等細節已與貼文原文核對，仍屬作者自述，硬體規模無法另外驗證）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（Herdr 終端復用與 Magpie 網關）
  - [`docs/buzz-nas-deployment-and-heartbeat-spec.md`](../docs/buzz-nas-deployment-and-heartbeat-spec.md)（NAS 24×7 常駐中樞與心跳規格）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（多代理與排程架構）

---

## 0. 原始資料盤點

> 2026-11-17 用未登入的瀏覽器重看。**原筆記寫「Facebook 原貼文 Cache miss、未查證」，這次讀得到全文、4 張圖與留言**（貼文日期 2026-11-14，458 個心情、106 次分享）。

- **作者圖片**：
  - 圖 1：Herdr App 的**Windows 桌面版**畫面。左側「Spaces」列出本機與 5 台遠端機器，另有兩個雲端 bot 項目；下方顯示 9 個 agents。右側是一個 Claude Code 工作階段（工作目錄在 `F:\`），狀態列顯示 Fable 5.2、中等推理、上下文 361k/1M、**`bypass permissions on`**。
  - 圖 2：同一個工作階段在 Claude 網頁版 Code 介面的樣子，右側面板標示 Remote Control、上下文已用 36%（360.5k／1M）及各類別占用；左下角顯示 Ultra 方案。
  - 圖 3：Claude Code 設定的 Config 分頁，搜尋 remote，「Enable Remote Control for all sessions」值是 true。
  - 圖 4：Windows 檔案總管對資料夾按右鍵的選單，有「在 Herdr 中開啟」一項。
- **作者留言補充**：
  - 回答「8 個 agent 的記憶怎麼串」：大部分 agent 的工作各自獨立；靠 Claude Code 內建的跨工作階段記憶；所有工作階段都能存取同一台 NAS 上的資料夾，需要時寫進去；共用技能寫成 agent skill 進版控，固定時間各自同步更新。**本篇第 1 節第 3 點「共享儲存與 Git 技能同步」就是出自這則留言，不是貼文正文。**
  - 已經連續跑了幾個月，除了例行更新系統重開機之外大多沒停；不是每次都能精準完成；唯一的限制是額度用完。
  - 最新一則：現在週一額度就用掉 50%，覺得 Ultra 的額度變少了。
  - 雲端的兩個 bot 其實有開放使用本機電腦，他在某些虛擬機裡就是用其中一個。
  - 回應質疑：他沒有做不完的工作要一直跑，重點是 agent 一直在線。
- **網友留言重點**：
  - 質疑「24×7」的定義：有人認為任務一定有斷點、Claude Code 常要人按下一步，設一堆排程不算真正的自主 agent。反方回應可以讓 Claude 自己設排程醒來接續。
  - 額度是共同痛點：另一位 Max 訂戶說 24×7 很燒額度，他會控制到重置前一天才全部用完。
  - 交接做法：有人說每個工作階段結束都寫交接檔（做到哪、待辦增減），下一個模型接手先讀它。
  - 風險提醒：有人指出哪天 Claude Code 限制某類用途，整套工作流就停擺。
  - 其他：有人用多家模型分頻道以省錢；有人問每月花費，作者沒有回答。
  - **2026-11-17 登入後補讀**（排序改成「所有留言」，回覆全部展開，34／34 則；網友貼的 3 張圖也放大看了）：
    - 補讀到的 4 則裡有用的兩則：一位自架 MCP 伺服器串多家 agent 的網友說，他原本接的其中一家因為開始抓第三方用法而撤掉，並附和作者「同樣工作量、額度消耗變多，等於變相漲價」；另一位說追最新模型與工作流本身就耗掉大量時間，懷疑到底是 AI 替人做事還是人替 AI 做事。
    - 另有一位說他用的開源外掛也是近乎全天運作來處理 issue，據他了解背後是 3 個 20 倍方案的帳號（轉述，未查證）。
    - 網友圖 1、2：`Dionysus Chan` 把這篇貼文丟給自己的 Hermes 機器人摘要的 Discord 截圖，內容只是重述貼文三點（高階訂閱、Remote Control 預設開、Herdr 當預設終端機），沒有新資訊。摘要裡「200 美元換到接近 10,000 美元用量」是機器人轉述貼文的說法，不是另外的證據。
    - 網友圖 3：同一個機器人對該網友說，他是單一 Hermes 設定檔加 Discord 前端、排程本來就在伺服器端跑，沒有「關視窗就斷」的問題，所以 Herdr 對他不是必需品。這與本篇對維護者環境的判斷方向相同（本機排程已由既有機制負責），但它是模型產生的建議，只當旁證。
- **對分析的影響**：
  - **撤除「原貼文未查證」**：3 台 Mac、8 個 agent、每個一台 Tart 虛擬機、兩個 Ultra 帳號、Remote Control 預設開、Herdr 加 Tailscale，都與貼文原文一致。仍是作者自述，硬體規模無法另外驗證。已改 frontmatter、來源行、作者行、第 1 節、第 1.1 節。
  - **更正 Herdr 的 Windows 判斷依據**：原筆記只憑 README 推論「Windows 支援有前提」。圖 1、圖 4 顯示作者實際在 Windows 上用 Herdr App，並有檔案總管右鍵整合。App 在 Windows 可用這點有圖為證；README 提到的 `sh` 相依是否仍影響 App，圖上看不出來。已改第 1 節第 2 點。
  - **新增安全觀察**：圖 1 的工作階段開著 `bypass permissions`，又同時被 Remote Control 遠端操控。這正是第 2 節「嚴禁全域關閉沙盒或繞過權限檢查」要擋的組合；這套架構的便利有一部分來自關掉權限確認，不可照抄。已補進第 2 節。
  - **「純雲端無法存取本機」要打折**：作者自己在留言承認雲端 bot 也能開放使用本機電腦，與第 1 節 Why 的保留一致。已補一句。
  - 額度是這套做法的實際上限（作者與網友都提到），已補進第 1 節。
  - `T-20261115-20`、`T-20261115-21` 的產出不依賴貼文細節，結論不變。
  - 2026-11-17 補讀的 4 則留言與 3 張網友圖沒有推翻任何一點；「額度是實際上限」又多兩位網友附和，正文不用再改。

---

## 1. 核心內容摘要（5W1H 初篩與實查）

- **Who / What**：原作者分享其「24×7 全時運行地端 Agent 架構」（3 台 Mac、8 個 Tart VM、2 個 Claude Code Ultra 帳號等硬體規模為作者自述，已與貼文原文核對，不作為維護者現況）。作者在留言說已連續跑了幾個月，實際上限是訂閱額度（最近週一就用掉 50%）。
- **Why（作者宣稱之純雲端限制）**：
  - 原作者提及「純雲端無法存取本機／NAS」：此屬該案例未配置所需通道或授權之限制（作者宣稱），不能概括推導為所有雲端架構均無法透過受控 connector、VPN 或代理存取本機。作者自己也在留言承認，他用的兩個雲端 bot 都有開放使用本機電腦。
- **How（核心技術實查與邊界）**：
  1. **Claude Remote Control 實查**：官方確有此功能（`claude remote-control` 或 `/remote-control`），但需符合訂閱與登入條件，API key 不支援。工作仍於本機執行，僅建立對外 HTTPS，無須新增入站防火牆規則，亦非將 Tailscale 視為必要依賴。「所有 session 預設開啟」為可選設定而非通用既定事實。主機與本機程序仍需存活，自動重連無法保證停電或休眠期間持續運作。
  2. **Herdr 終端復用實查**：不可無版本區分地宣稱「無縫替換 PowerShell」。舊版 terminal README 僅支援 Linux/macOS；現行 `herdr-core` README 雖具 Windows x86_64 二進位檔，但部分模板與 quoted shell command 仍依賴 `sh` 環境。此屬元件與版本差異，需固定元件、版本與 Windows 前提。貼文附圖顯示作者實際在 Windows 上使用 Herdr App（含檔案總管右鍵「在 Herdr 中開啟」），App 在 Windows 可用有圖為證；`sh` 相依是否仍影響 App，圖上看不出來。
  3. **共享儲存與 Git 技能同步（安全邊界）**：
     - 多 session 共享 NAS 或目錄交換。
     - **「唯讀同步」概念糾正**：`git pull --ff-only` 仍會寫入並更新工作樹；`git fetch` 亦會寫入 `.git`。fast-forward 僅代表線性合併，不等於只讀、不等於安全審查、不等於技能熱更新；dirty tree 檢查亦無法防禦拉進惡意 hooks 或技能。憑證、本機設定與私有記憶絕不可與共享技能混雜同步。

### 1.1 CQR 論證檢驗（Claim - Evidence - Reasoning）
- **主張（Claim）**：地端多機 Agent 透過 Remote Control 與排程同步可構建持續運作工作流，需評估 Windows 11 落地規格。
- **證據（Evidence）**：[官方 Remote Control](https://code.claude.com/docs/en/remote-control)、[Git 官方 pull 文件](https://git-scm.com/docs/git-pull)、[Tailscale unattended 官方文件](https://tailscale.com/docs/how-to/run-unattended)、[core README](https://raw.githubusercontent.com/herdrdev/herdr-core/master/README.md)；Facebook 原貼文（2026-11-17 已讀到全文、4 張圖與 30 則留言）。
- **推論（Reasoning）**：Remote Control 具備官方基礎，但不能由 AI 代改電源與系統安全；Git ff-only 並非唯讀亦無法保證熱更新安全；Windows 落地須以唯讀腳本與人工規格為交付邊界。

---

## 2. 啟發與適用性評估（對照本機 Windows 11 基建）

- **已有且可對接的本機資產**：
  - **Git 版控共用規則與 Skills**：已建置 `SanHsien/agent-assets`（私有）（SSOT），結構完整。
  - **結構化交接**：已具備 `agent-handoff`（`dropoff` / `pickup`）與 `checkpoint`。
  - **跨代理派工**：`SanHsien/agent-relay` 已具備跨終端派工與驗收機制。
- **交付邊界與安全鐵律**：
  1. **禁止代改系統設定**：自動登入非 24×7 必然條件；AI 嚴禁修改電源、NIC、休眠、防火牆、登錄檔、服務、Task Scheduler、Tailscale 或遠端控制設定。Tailscale 無人值守運行須由維護者手動設定，不自動停用 key expiry。
  2. **安全閘門提醒**：嚴禁全域關閉沙盒或繞過權限檢查。貼文附圖裡作者的工作階段正是開著 `bypass permissions` 又接受 Remote Control 遠端操控；這套架構的便利有一部分來自關掉權限確認，不可照抄。
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
