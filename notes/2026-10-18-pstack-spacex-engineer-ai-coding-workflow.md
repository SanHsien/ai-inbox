---
id: 2026-10-18-pstack-spacex-engineer-ai-coding-workflow
title: "Lauren Tan（poteto）的 pstack 方法論：以嚴謹工程紀律重構 AI 協同開發（/poteto-mode 核心路由、22 套 Playbook、TDD 驗證與多模型審查解構）"
source_url: "https://www.threads.com/@mengshyue.tsai/post/DenWauFklqQ"
source_platform: "Threads / YouTube / GitHub"
author: "Lauren Tan (@poteto) / 轉載分享：MengShyue Tsai (@mengshyue.tsai)"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: "1"
cluster_role: "工程紀律與設計審查"
short_title: "pstack 方法論與 TDD 驗證"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 0
source_replies: 81
tags:
  - pstack
  - poteto-mode
  - ai-coding-workflow
  - engineering-guardrails
  - tdd-verification
  - agent-skills
---

# Lauren Tan（poteto）的 pstack 方法論：以嚴謹工程紀律重構 AI 協同開發（/poteto-mode 核心路由、22 套 Playbook、TDD 驗證與多模型審查解構）

- **來源連結**：[Threads 原貼文 (MengShyue Tsai)](https://www.threads.com/@mengshyue.tsai/post/DenWauFklqQ)（短網址：[threads.com/share/BAXyuLT-xc](https://www.threads.com/share/BAXyuLT-xc/)）｜ [YouTube 影片解說](https://www.youtube.com/watch?v=b7-2w2T2Lqs) ｜ [Cursor 官方插件倉庫 (cursor/plugins)](https://github.com/cursor/plugins/tree/main/pstack) ｜ [社群移植版 pstack-claude（轉貼者推薦）](https://github.com/michael-denyer/pstack-claude) ｜ [社群移植版 open-pstack](https://github.com/ericlitman/open-pstack)
- **發布平台 / 原作者**：`Threads / YouTube` / 原創者：`Lauren Tan (@poteto)`、社群分享：`MengShyue Tsai (@mengshyue.tsai)`
- **分析日期**：`2026-10-18`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-16 重審：看了 Threads 貼文與作者自己的 3 則留言（貼文顯示 16 則回覆，其餘要登入才看得到）、YouTube 解說影片的說明欄、**完整字幕**（約 7 分鐘，這次用 `yt_dlp` 抓到）與已載入的留言 10 串加 9 則回覆，並直接核對官方 repo `cursor/plugins` 的 `pstack/` 目錄與 README。作者留言貼的第二支影片（另一個頻道的 EP435）沒有看。
> 2026-11-17 登入補讀：Threads 留言兩種排序都捲到底並點進有回覆的子串，讀到 14 則（作者 3 則、網友 11 則）；貼文計數顯示 16，另外 2 則頁面不顯示，已無可再讀。第一支影片的 YouTube 留言用 `yt_dlp` 抓全（42／42 則）。第二支影片 EP435（「AI 懶人報」頻道，約 15 分鐘）用 `yt_dlp` 抓到完整字幕讀完，留言 25／25 則也讀完。並重讀官方 README 對照 EP435 的說法。

- **作者圖片**：無。貼文與留言只有連結預覽卡（兩支 YouTube 影片封面、兩張 GitHub 卡片），作者沒有另外上傳圖片。
- **作者留言補充**（Threads 轉貼者 @mengshyue.tsai 的三則留言）：
  - 官方版在 `cursor/plugins`。
  - **Claude Code 社群移植版他貼的是 `michael-denyer/pstack-claude`**（查 GitHub API：約 4,400 星，涵蓋 Claude Code、Codex、Antigravity、Gemini、OpenCode 等多種工具），不是本筆記原本寫的 `ericlitman/open-pstack`（約 580 星，只做 Claude Code 與 Codex）。兩個 repo 都存在。
  - 另一支延伸影片（EP435，談 Cursor 工程師一個月 2,000 個 PR、讓 AI 自己合併），2026-11-17 已讀完字幕，重點見下方「EP435 字幕重點」。
- **影片說明欄與字幕重點**（原稿寫作時沒有依字幕分析）：
  - 結構是 **24 條原則 → 23 套 playbook → 30 個 skill**，三者都是 Markdown 檔；`/poteto-mode` 是唯一入口，先讀原則、再挑 playbook、需要時叫其他 skill。（以上是影片的說法。官方現況（2026-11-17 以 GitHub API 列 `cursor/plugins` 目錄樹）：`pstack/skills/` 共 58 個目錄，其中 **34 個 skill、24 個 `principle-` 原則**，影片說的「30 個 skill」是錄影當時的數字；playbook 在 commit `bf0c7cd`（2026-11-15）是 23 套，到 commit `2f87c85`（2026-11-16）少了 `orchestrate.md`、剩 22 套。本筆記其餘「23 套」的寫法都是指 `bf0c7cd` 當時的清單。）
  - 影片示範的六個可單獨使用的 skill：`/recall`（翻最近七天的對話、PR、issue 整理進度）、`/tdd`（先寫測試並親眼看它失敗才改）、`/interrogate`（把改動交給多個模型各自挑毛病，結論分成一定要改／由你決定／先記下來／不用理四類，**只給結論、不動程式**）、`/no-comments`（逐條審註解，只是複述程式的刪掉、說明外部限制的留下）、`/create-verification-skill`（替專案產生一份驗證專用 skill，交付前自己先完整跑一遍，還會故意把修好的問題放回去確認驗證抓得到）、`/bro`（用白話重講一次）。
  - 說明欄寫明**官方 README 就有 Claude Code 的安裝方式**：先 `/plugin marketplace add cursor/plugins`，再 `/plugin install pstack@cursor-plugins`；指令在 Claude Code 裡會多一個前綴，例如 `/pstack:poteto-mode`；第一次先跑 `/setup-pstack` 選模型。
- **EP435 字幕重點**（2026-11-17 補讀；這支是轉述，內容多取自 Matt Pocock 訪問 Lauren 的直播與官方指南）：
  - **SpaceX 頭銜的來由**：影片說她今年三月加入 Cursor，pstack 是那段時間做出來的；今年八月 Cursor 被 SpaceX 收購，她現在在 SpaceX 的 AI 部門。所以「Cursor 工程師」與「SpaceX 工程師」兩種說法指的是同一份工作。這仍是轉述，官方 README 沒寫，本次也沒有另外查證收購一事。
  - **敢讓 agent 自己合併，靠的是三件事**：agent 自己驗證（她說整個工具箱最重要的 skill 就是驗證；`/create-verification-skill` 會替專案產生「怎麼開、怎麼操作、怎麼留證據」的說明與一張功能地圖）、寫程式的 agent 不能自己判定過關（只有沒寫這段程式的 agent 的結論才算，測試全綠也不算）、把環境改成很難犯錯（`/correct` 會翻最近的 commit 與審查留言找出重複犯的錯，處理順序是改架構 → 型別／lint／CI → 測試，寫成文件規則排最後）。
  - **過夜執行的三個條件**：完成標準要能檢查（「做四小時」不算）、留決策紀錄、留出口（卡住就停並寫明原因）。人的工作改成抽樣，抽到問題就回頭改流程。
  - **與 Matt Pocock 那套的差別**：他的 `grill-me` 是開工前一直問到有共識；pstack 相反，原則是不要卡在人身上，先做再給人看，只有不能回頭的動作才先問。pstack 沒有規劃用的 skill。
  - **什麼時候不要用**：小又明顯的改動、token 預算有限、結果很難自動驗證的工作。Lauren 自己說她在 token 用不完的公司工作，不是每個人都該照做。影片建議不要整套照抄，用 `/automate-me` 從自己的對話紀錄產生自己的 mode。
  - **與官方現況不符的兩處**：影片說「一共 54 個 skill」，官方目錄是 34 個 skill＋24 個原則檔（共 58 個目錄），數字對不上；影片說「`setup-pstack` 在 Claude Code 沒有作用」，但官方 README（2026-11-17 重讀）寫明 Claude Code 裡 `/pstack:setup-pstack` 會把模型選擇寫進 `~/.claude/rules/pstack-models.md`。兩處都以官方 README 為準。影片說預設把寫程式交給 Grok；官方 README 現在寫的預設是寫程式、文字與判斷都交給 Opus 5.5，也以 README 為準。
- **網友留言重點**（YouTube）：
  - 最多人回應的一串在談成本：整套跑下來會派子代理、找多個模型互審，**很燒 token**，適合願意大量投入 AI 成本的公司；頻道主回覆認同，建議額度吃緊的人只挑單一 skill 用。
  - 有人提醒第一次要先跑 `/setup-pstack`；有人問需要多大的 context；有人問會不會藏惡意程式（看不到有實質內容的回答）；有人建議直接讀 poteto 的原文，因為摘要省掉很多細節。
  - 沒有人回報在 Claude Code 上的完整實測結果。（2026-11-17 讀完全部留言後修正：仍沒有完整實測報告，但有幾則簡短的使用回報，見下。）
  - **2026-11-17 補讀到的使用回報**：
    - 第一支影片：`@howard5526` 說用起來跟平常的 Claude Code 加 Opus 差不多，多了幾個好用的工具，預設就是 TDD 與最小改動；`@kentchen6310` 認為現在的 Claude 不裝 skill 也這樣做事（另一人反駁說沒打好基礎一樣會產出垃圾）；`@bitmale` 說自己在 OpenCode 上搭配另一套精簡輸出的 skill 一起用；`@aneinqi1163` 提醒開源專案近來常藏惡意程式，擔心就先掃描，頻道主回覆說這套主要是 Markdown 文字檔、比較好檢查。
    - EP435：`@q7567731` 原本質疑 2,000 個 PR 是在修 AI 自己產生的問題，實際用三天後改口說好用，做法是以 Matt Pocock 的 skill 為主、pstack 為輔，**只單獨呼叫 pstack 裡的 skill，不用 `/poteto-mode` 當總入口**；`@slashman413` 說效果取決於模型能力，思考程度至少要中等，換成本機小模型後又慢又會寫出 bug；`@reedthediver0000` 估計大約三個 200 美元的訂閱可以撐住這種用法（另一人回的數字高得多，都沒有依據）；`@jackyyau1559` 指出架構層級的取捨很難用測試或 lint 抓到，只靠抽查能不能保證品質是核心疑問；`@chauchau0825` 提醒兩位當事人都有立場，沒拿出證據的說法不必當真。
  - Threads 補讀到的 11 則網友留言：`code.with.renfu` 說已經在用、還不錯（沒有細節）；一則是有人叫平台內建的 AI 帳號摘要，該摘要寫「21 條原則、一個月 2,500 個 PR」，與官方的 24 條原則及影片的 2,000 個對不上，是機器產生的內容，不採用；其餘是收藏用短留言與玩笑。
- **對分析的影響**：
  - **作者背景改寫，標題拿掉「SpaceX 前首席工程師」**。貼文與影片說的是「待過 Netflix、Meta、Cursor，**現在是** SpaceX 首席工程師」；原稿卻寫成「曾任 SpaceX、現任 Cursor」，順序相反。而官方 README 的自我介紹只寫 Meta、Netflix、Cursor 與 React 核心團隊，並說這是她每天在 Cursor 用的 skill，**完全沒提 SpaceX**。SpaceX 這個頭銜只出現在轉述的影片與貼文，本次無法從第一手來源查證，已在 1.1 標明。
  - **「五大 Playbook」是錯的，官方是 23 套（2026-11-16 查證時；隔天上游移除 `orchestrate.md`，現為 22 套）**。直接列目錄確認：除了原稿寫的 bug-fix、feature、refactoring、investigation、perf-issue 之外，還有 autonomous-run、babysit、eval、hillclimb、multi-phase-plan、opening-a-pr、orchestrate、pause-safely、prototype、runtime-forensics、session-pickup、shipping、trace-forensics、visual-parity、worktree-cleanup 等。已改 1.1 的圖與 1.2 的說明。
  - **第 2 節「要靠社群移植版才能在 Claude Code 用」是錯的**：官方 README 直接提供 Claude Code 安裝指令。已改寫，並補上轉貼者推薦的 `pstack-claude`。
  - **`/interrogate` 與 `/arena` 的描述修正**：`/interrogate` 是多模型交叉審查且不改程式；`/arena` 是讓幾個模型各寫一版再挑最好的部分。原稿寫成「同一模型用挑剔視角逐行質疑」「多個 Prompt 獨立嘗試」，已改。
  - 1.2 流程圖最後一格「Commit & PR 自動交付」沒有來源依據（影片示範到驗證與審查為止），保留圖但在圖下加註。
  - **2026-11-17 補讀後的修正**：(1) 1.1 節 SpaceX 頭銜補上 EP435 的解釋（Cursor 被 SpaceX 收購），仍標為未查證。(2) 第 2 節補上「什麼時候不要用」與網友的使用回報——回報一致指向「挑單一 skill 用」比整套 `/poteto-mode` 實際，這與本 repo 當初只融合驗證與 TDD 防線（`T-20261018-18`）的做法一致。(3) EP435 關於 Claude Code 的兩個說法與官方 README 不符，不採用；`docs/pstack-agent-playbooks.md` 現有內容（`/pstack:setup-pstack` 會寫入 `~/.claude/rules/pstack-models.md`）與 README 一致，不用改。任務不增不減。
  - **新增任務 `T-20261018-19`**：已完成的 `docs/pstack-agent-playbooks.md`（`T-20261018-17`）與它的驗證器（`T-20261025-08`）都是照「五大 Playbook、前 SpaceX、open-pstack」這些錯誤前提寫的，需要依官方 repo 更正。原任務不改狀態，另開新任務處理；本筆記狀態因此由已完成改為進行中。

---

## 1. 核心內容摘要

### 1.1 核心主張：從「隨機盲猜的 Vibe Coding」回歸「證據先行的工業級軟體工程（Evidence-First Engineering）」

隨著 Cursor、Claude Code、Codex 等 AI 程式開發工具的普及，許多開發者陷入了「Vibe Coding」的陷阱：輸入一段模糊的 Prompt，讓 AI 吐出大量未經測試的程式碼，看到沒報錯就以為完成了。

**Lauren Tan（@poteto）** 是 React 核心團隊成員（負責 React Compiler），官方 README 自述待過 Meta、Netflix、Cursor，並說 pstack 是她每天在 Cursor 用的 skill。轉述的貼文與解說影片另稱她「現在是 SpaceX 首席工程師」，官方 README 沒有這個說法，**未查證**。另一支解說影片（EP435）的解釋是 Cursor 今年八月被 SpaceX 收購、她現在在 SpaceX 的 AI 部門，所以兩種頭銜指同一份工作；這同樣是轉述，本筆記沒有另外查證。她把自己的做法開源成外掛 **`pstack`**：24 條原則、23 套 playbook、30 個 skill（數字依解說影片；官方 `skills/` 目錄另含以 `principle-` 開頭的原則檔）。官方目錄現況是 34 個 skill＋24 個 `principle-` 原則，playbook 由 23 套（commit `bf0c7cd`，2026-11-15）變為 22 套（commit `2f87c85`，2026-11-16，少了 `orchestrate.md`），查證方式見第 0 段。

`pstack` 的核心哲學是：**AI Agent 不是替你盲目打字的打字機，而是必須在嚴密軟體工程紀律與約束下運作的初中級工程師夥伴**。如果沒有嚴格的工程防線（Guardrails）、重現測試（Reproduction Tests）與執行期驗證閉環（Runtime Verification），AI 只會以極高的速度放大技術債與幽靈錯誤。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   pstack「證據先行」AI 協同開發架構全景                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 自然語言意圖輸入 (User Intent)                                      │
│    └─ 使用者輸入目標：/poteto-mode <task description>                    │
│                                                                        │
│ 2. 總控動態路由器 (The Core Router: /poteto-mode)                      │
│    └─ 先讀原則 ──> 從 22 套 Playbook 挑一套（下列僅舉 5 套）            │
│       ├─ Bug-fix Playbook (嚴格遵循 TDD 重現失敗案例)                    │
│       ├─ Feature Playbook (事前架構設計與邊界檢查)                       │
│       ├─ Refactoring Playbook (行為保持與回歸防護)                      │
│       ├─ Investigation Playbook (呼叫鏈追蹤與日誌探針)                   │
│       └─ Performance Playbook (效能基準測量與瓶頸定位)                  │
│                                                                        │
│ 3. 模組化專業技能協同 (Modular Specialized Skills)                      │
│    ├─ /how & /why: 系統行為鏈路追蹤與架構決策溯源                        │
│    ├─ /architect: 事前架構與資料流向設計探索                            │
│    ├─ /arena: 平行啟動多種獨立實作並進行對抗性比較                      │
│    ├─ /swarm: 將複雜任務拆解並平行委派給多個子代理                      │
│    └─ /interrogate: 跨模型對抗性程式碼審查與邊界壓力測試                │
│                                                                        │
│ 4. 嚴格執行期驗證閉環 (Runtime Verification Gate)                       │
│    └─ 嚴禁未經執行的假設 ──> 必須貼出真實測試與執行輸出 ──> 交付閉環    │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 核心機制深度剖析

```
[pstack 執行期推進生命週期]

  +-----------------------+
  |  /poteto-mode <task>  | (使用者發起)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |    語意識別與路由     | ===> 匹配 Playbook (Bug/Feature/Refactor/Perf)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |    /architect 規劃    | ===> 產出明確任務清單、資料結構與邊界約束
  +-----------+-----------+
              |
              v
  +-----------------------+      (紅燈失敗證明問題存在)
  |   強制撰寫重現測試    | <----------------------------+
  | (Reproduction Test)   |                              |
  +-----------+-----------+                              |
              |                                          | 若回歸
              v                                          | 重新測試
  +-----------------------+                              |
  |  小步微調與實作代碼   |                              |
  +-----------+-----------+                              |
              |                                          |
              v                                          |
  +-----------------------+                              |
  |  /interrogate 交叉審查| ===> 跨模型攻擊代碼邊界      |
  +-----------+-----------+                              |
              |                                          |
              v                                          |
  +-----------------------+                              |
  | 執行期真實測試 (綠燈) | -----------------------------+
  +-----------+-----------+
              | (出具完整日誌輸出證據)
              v
  +-----------------------+
  | Commit & PR 自動交付  |
  +-----------------------+
```

> 上圖最後一格「Commit & PR 自動交付」沒有來源依據，解說影片只示範到驗證與審查；官方另有 `opening-a-pr`、`shipping` 等 playbook，但是否自動交付未查證。

1. **`/poteto-mode` 總控路由**：
   - 使用者只需輸入一句自然語言需求，如 `/poteto-mode 修復購物車結帳時超時未清空購物清單的 bug`。
   - `poteto-mode` 充當總架構師，不會直接動手改檔，而是先選擇適配的 **Playbook**，並自動列出結構化任務清單與驗收條件。
2. **Playbook 專題作業指導手冊**（官方共 22 套，以下三套為例；完整清單見第 0 節）：
   - **Bug-fix Playbook**：要求 **「No Reproduction, No Fix」**。在寫下任何修正代碼前，必須先寫出一支確定會失敗的測試（Red Test）來證明錯誤存在；修正後必須讓該測試轉為綠燈（Green），並確保沒有任何原有測試回歸。
   - **Refactoring Playbook**：禁止改動外部 API 與行為，只允許做結構調整與簡化，且重構前後必須具備完整的字元級或行為級測試保護。
   - **Performance Playbook**：修效能前必須先採集基準數據（Benchmark），修完後對比記憶體與 CPU 差異，禁止主觀感覺。
3. **專業輔助子技能陣容（Modular Skills）**：
   - **`/how` 與 `/why`**：追蹤特定函式或模組的呼叫鏈（Call Chain），並探詢當初架構這樣設計的理由（避免破壞原有設計意圖）。
   - **`/architect`**：在動工前產出架構設計藍圖、邊界防禦與型別定義。
   - **`/arena`**：讓幾個不同的模型各寫一版，再挑出各版最好的部分。
   - **`/swarm`**：將大任務拆成互不干擾的批次，並行派發給多個子代理。
   - **`/interrogate`**：把改動同時交給不同的模型各自挑毛病，多個模型都抓到的問題最可信；結論分成「一定要改／由你決定／先記下來／不用理」四類。它只給結論，**不會自己改程式**。
   - **其他可單獨用的 skill（依解說影片）**：`/recall`（整理最近七天做到哪）、`/tdd`（先看測試失敗再改）、`/no-comments`（審註解）、`/create-verification-skill`（替專案產生驗證 skill）、`/bro`（白話重講）。

---

## 2. 官方 GitHub 與開源生態細節

- **官方上游**：位於 Cursor Plugins 生態目錄中（`github.com/cursor/plugins/tree/main/pstack`）。
  - 在 Cursor 環境中可直接透過 `/add-plugin pstack` 安裝啟用。
  - **Claude Code 官方也支援**（README 載明）：`/plugin marketplace add cursor/plugins` 後 `/plugin install pstack@cursor-plugins`；指令會多一個前綴（`/pstack:poteto-mode`），第一次先跑 `/pstack:setup-pstack` 選模型；只有 Cursor 才有的功能（如 bugbot、automations）會略過並提示。授權為 MIT。
  - **什麼時候不要用**（EP435 轉述官方指南與作者本人的說法）：小又明顯的改動、token 預算有限、結果很難自動驗證的工作。兩支影片的留言區最多人談的也是成本；有實際用過的網友多半只單獨呼叫個別 skill，不用 `/poteto-mode` 當總入口，並提醒效果取決於模型能力。
- **社群移植版（`pstack-claude`）**：`github.com/michael-denyer/pstack-claude`，原貼文作者在留言推薦的版本，涵蓋 Claude Code、Codex、Antigravity、Gemini、OpenCode 等。
- **社群開源移植版（`open-pstack`）**：
  - 專案網址：`github.com/ericlitman/open-pstack`
  - repo 自述是給 Claude Code 與 Codex 用、追蹤官方上游的版本。原稿寫的「抽離出通用的 Model/Provider Registry 與 Command-Line Runner」與支援 Antigravity 兩點，這次沒有在 repo 說明中看到，未查證。

---

## 3. 對現有工作流與專案之啟發

`pstack` 的核心理念與本機全域規範（`RULE[user_global]`）有著極高的共鳴：

1. **「回報完成之前，要真的執行過檢查並貼出它的輸出」**：這正是 `pstack` 的靈魂——沒有終端機的真實輸出作為證據，所有的程式碼都只是未經證明的假設。
2. **「先調研再動手、先計畫再實作」**：對齊 `pstack` 的 `/architect` 與 `/poteto-mode` 路由器，杜絕拿到需求立即盲目改檔的陋習。
3. **「不要留 TODO 或空殼函式」**：`pstack` 的 `/interrogate` 與自動檢查防線會直接封殺任何返回假資料、空字串或未實作完成的敷衍代碼。
4. **與現有技能庫的整合潛力**：
   - 現有的 `quality-loop`、`verification-protocol` 與 `ai-review` / `blind-review`，本質上就是 `pstack` 的獨立實踐！
   - 可以借鏡 `pstack` 的 **Playbooks 路由概念**，將零散的檢驗工具封裝為統一的入口指令，進一步提高自主編排的工程標準。

---

## 4. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261018-17`**｜**[優先級：高]** 深度調研並拆解 `pstack` 核心技能庫與 Playbooks 架構（`/poteto-mode`、`/architect`、`/arena`、`/swarm`、`/interrogate`），整理出跨 Agent CLI（Claude Code / Codex / Antigravity）的標準移植規格
  - **目標範圍**：`cursor/plugins/pstack` 與 `open-pstack`
  - **驗收標準（DoD）**：產出 `docs/pstack-agent-playbooks.md`，定義 `/poteto-mode` 與 5 大 Playbooks 在 Claude Code / Codex / Antigravity 的參數與提示詞規格，附至少 3 個實例對照並通過 Markdown 結構檢驗。
  - **完成日期**：2026-10-22
  - **實作紀錄 / 證據**：產出 docs/pstack-agent-playbooks.md，完整拆解 SpaceX Lauren Tan (@poteto) 之 pstack 核心哲學；具備查證來源連結（YouTube、Threads、cursor/plugins/pstack、open-pstack）與未查證標註；定義 /poteto-mode 路由器與 5 大 Playbooks（Bug-fix、Feature、Refactoring、Investigation、Performance）在 Claude Code、Codex CLI、Antigravity 的參數與 Prompt 規格；提供 Bug-fix、Feature、Refactoring 3 大真實實例對照表並通過 Markdown 結構檢驗與契約測試。
- [x] **`T-20261018-18`**｜**[優先級：高]** 將 `pstack` 的嚴格工程防線（強制 TDD 重現失敗案例才動手、禁止空殼函式與猜測性修復、執行期驗證閉環）融合進本地全域協作規範與 `quality-loop` / `verification-protocol` 技能庫中
  - **目標範圍**：`SanHsien/ai-quality-gates` ＋ `SanHsien/harness-guard` ＋ `SanHsien/agent-governance-toolkit`
  - **驗收標準（DoD）**：復用 `ai-quality-gates`（Gherkin 規格/覆蓋率）、`harness-guard`（阻止 hook）與 `agent-governance-toolkit`（運行期政策強制與沙箱審計），無真實終端日誌一律不放行
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：
    1. **agent-relay 驗收閘門深度整合 agent-governance-toolkit**：在 `SanHsien/agent-relay` 的 `agent_relay/gates.py` 完整實作 AGT 運行期政策檢查（commit `0d0655c`）：(a) 復用 `agent_os.diff_policy.DiffPolicy` 執行路徑邊界檢查，嚴格攔截 `*.env*`、`id_rsa*`、`*.pem`、`secrets/**` 等高危路徑與檔案上限；(b) 復用 `agent_os.credential_redactor.CredentialRedactor` 掃描新增修改之代碼與日誌，檢測敏感 API Key/Token 即判定 `policy-violation` 阻斷交付，並對日誌 tail 執行自動脫敏；(c) 復用 `agent_sandbox.code_scanner.scan_code_for_subprocesses` 靜態掃描非測試代碼之危險進程呼叫。單元測試 `tests/test_gates.py` 擴充至 47 項測試（含 16 項治理政策檢驗與端到端派工阻斷）全數綠燈通過（183.283s），並主動 push 至個人 fork。
    2. **全域 quality-loop 技能升級**：更新本地 `~/.gemini/config/skills/quality-loop/SKILL.md` 與跨 Agent SSOT `SanHsien/agent-assets`（私有） 技能庫 `skills/quality-loop/SKILL.md`（commit `ae82874`，58 項測試全綠，已 push 個人 fork），明確將 pstack TDD 紀律、agent-relay 驗收閘門（防刪改、拒空殼、TDD red-to-green、日誌保全）與 AGT 運行期政策檢查（路徑邊界、機密外洩防護、危險指令掃描）寫入執行契約。
    3. **實踐規格與證據存證**：產出 `docs/pstack-governance-integration.md`，詳載三道防線架構、實作細節與真實終端執行日誌。
    4. **覆核補正（2026-10-26）**：原交付有三個缺口，已補齊後維持已做——(a) AGT 未載入時悄悄降級，危險指令掃描沒執行卻寫「通過」，違反「無證據不放行」→ agent-relay `e298031` 改為回 `unverified`，只有明寫 `governance_fallback: "builtin"` 才降級並標示；(b) `0d0655c` 在 GitHub CI 實際是失敗的（CI 沒有 AGT）→ `cc5eff1` 修正，完整測試 340 項、CI 綠燈；(c) 任務標題點名的 Claude 全域技能 `verification-protocol` 沒改 → 已新增第 5 節，以 relay 閘門結果為委派工作的證據。另更正文件中「16 項治理測試」「無外部套件亦能安全運作」等不實描述；`SanHsien/agent-assets`（私有） 58 項測試經重跑屬實。
- [x] **`T-20261025-08`**｜**[優先級：高]** 實作 pstack 五大工程 Playbooks、Claude 官方外掛評測與全端商業建站規範之「外部裁判」結構驗證器
  - **目標範圍**：`tools/verify_pstack_and_fullstack_specs.py` 與 `tests/test_verify_pstack_and_fullstack_specs.py`
  - **具體做法**：
    1. 實作 `tools/verify_pstack_and_fullstack_specs.py`（純 Python stdlib），機械化解析並驗證：(a) `docs/pstack-agent-playbooks.md` 涵蓋 `/poteto-mode` 路由器、五大 Playbooks（Bug-fix、Feature、Refactoring、Investigation、Performance）跨 CLI 規格與至少 3 個實例對照；(b) `docs/claude-plugins-official-review.md` 涵蓋推薦外掛、排除項目與「未查證」誠實標註；(c) `templates/fullstack-website-builder-skill.md` 涵蓋軟刪除、定價快照、事件流水帳、訂單狀態機與 Webhook 簽名對帳；(d) `templates/subject-inventory-argument-writing-prompt.md` 涵蓋主體資產盤點與 Claim + Proof 論證規範。
    2. 撰寫 `tests/test_verify_pstack_and_fullstack_specs.py`（使用 `unittest.TestCase` 以同時相容 `unittest discover` 與 `pytest`），涵蓋真實 4 份文件全數通過與各文件核心結構缺漏之反例攔截測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_pstack_and_fullstack_specs.py` 回傳 exit 0，且 `python -m unittest discover -s tests -p "test_verify_pstack_and_fullstack_specs.py"` 與 `pytest` 全數通過（至少 6 項測試）。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：實作 `tools/verify_pstack_and_fullstack_specs.py`，完整支援純 Python 標準庫解析與四大文件規格校驗；實作安全檔案讀取輔助函式 `load_content` 杜絕多行字串在 Linux CI / Windows 上觸發 `ENAMETOOLONG`；實作 `tests/test_verify_pstack_and_fullstack_specs.py`（繼承 `unittest.TestCase`），提供 7 項單元測試，全面覆蓋真實文件驗證、各規格核心缺漏反例攔截、安全載入邊界與 CLI 進入點退出碼；經真實終端執行 `python tools/verify_pstack_and_fullstack_specs.py`（exit 0）、`python -m unittest discover -s tests -p "test_verify_pstack_and_fullstack_specs.py"`（7/7 passed, exit 0）與 `python -m pytest tests/test_verify_pstack_and_fullstack_specs.py -q`（7 passed, exit 0）全數綠燈驗收。

- [x] **`T-20261018-19`**｜**[優先級：中]** 依官方 `cursor/plugins` 的 pstack 更正 `docs/pstack-agent-playbooks.md` 與其驗證器的錯誤前提
  - **目標範圍**：`docs/pstack-agent-playbooks.md`、`tools/verify_pstack_and_fullstack_specs.py`、`tests/test_verify_pstack_and_fullstack_specs.py`
  - **具體做法**：
    1. 讀官方 `pstack/README.md`、`pstack/docs/harness/claude-code.md` 與 `pstack/skills/poteto-mode/playbooks/` 目錄，把文件裡「五大 Playbook」改成官方 23 套的實際清單（可分「本環境會用到」與「僅列名」兩組），skill 清單改依官方 `skills/` 目錄。
    2. 作者背景改為官方 README 的自述；「前 SpaceX 首席工程師」「SpaceX 內部遙測」等列改標未查證或刪除；`description: SpaceX Evidence-First orchestration router.` 這類杜撰的範例欄位一併改掉。
    3. Claude Code 一節改寫為官方安裝方式（`/plugin marketplace add cursor/plugins`、`/plugin install pstack@cursor-plugins`、指令前綴 `pstack:`），社群移植版補上 `michael-denyer/pstack-claude`。
    4. 驗證器若寫死「五大 Playbook」的名稱或數量，改成檢查文件列出的 playbook 檔名都真的存在於官方目錄清單（清單以常數附上查證日期），並同步調整測試。
  - **驗收標準（DoD）**：`docs/pstack-agent-playbooks.md` 內不再出現「五大」「5 大」Playbook 與未標註的 SpaceX 頭銜；文件列出的每個 playbook 名稱都能在官方 `pstack/skills/poteto-mode/playbooks/` 目錄找到；`python tools/verify_pstack_and_fullstack_specs.py` 回傳 exit 0，`python -m unittest discover -s tests -p "test_verify_pstack_and_fullstack_specs.py"` 全數通過。
  - **完成日期**：2026-11-17
  - **實作紀錄 / 證據**：依官方 cursor/plugins pstack（commit bf0c7cd，2026-11-16 以 GitHub API 列目錄並讀 README、harness/claude-code.md、poteto-mode SKILL.md 與五份 playbook）重寫 docs/pstack-agent-playbooks.md：改為官方 23 套 playbook 與 34 skill＋24 原則、作者背景改 README 自述、SpaceX 頭銜標未查證、刪除無依據內容；驗證器改以 23 個官方檔名清單雙向比對並攔截「五大 Playbook」；verify_pstack_and_fullstack_specs.py exit 0，unittest 8/8 通過。 2026-11-17 重查上游移除 orchestrate.md，文件、驗證器與測試改為 22 套。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **共同大腦與多 Agent 調度**：
  - [AI 共同大腦工業級架構規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [多 Agent 工廠：Magpie 網關與 Herdr 終端復用](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261018-16`
  - [跨 CLI 子代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
- **模型路由與工程驗證**：
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`

