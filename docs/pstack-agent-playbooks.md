# pstack 技能庫與 Playbooks：官方結構與跨 Agent CLI 使用說明

> **文件定位**：整理 Lauren Tan（`@poteto`）開源外掛 `pstack` 的官方結構——入口 `/poteto-mode`、22 套 playbook、34 個 skill 與 24 條原則——以及在 Claude Code、Codex CLI、Antigravity 三種 Agent CLI 上各自能怎麼用。
>
> **2026-11-16 依官方 repo 重寫**（任務 `T-20261018-19`）。舊版把 playbook 寫成只有五套、把作者背景寫錯、把 Claude Code 寫成只能靠社群移植版，還列了查無依據的內容與自行編造的呼叫方式，本版全部改正或刪除。內容以 `cursor/plugins` 的 `pstack/` 目錄為準，查證時該目錄最新 commit 為 `bf0c7cd`（2026-11-15）。**本文件沒有在任何 CLI 上實際安裝或執行 pstack**，所有流程描述都來自閱讀官方檔案。

> **2026-11-21 查證**（GitHub API，查閱日 2026-11-21）：`pstack/` 目錄最新 commit 已是 `0b46ec3`（2026-11-19），數量沒變：playbook 22 個檔、`skills/` 58 個目錄（其中 24 個 `principle-`）、`agents/` 兩個、MIT；README 的作者自述與 Claude Code 安裝指令與下文相同。社群移植版星數現為 `pstack-claude` 約 4,650、`open-pstack` 約 590。本次沒有發現要改的內容。

---

## 1. 來源依據與查證狀態表

| 項目 | 來源 | 查證狀態 | 說明 |
| :--- | :--- | :--- | :--- |
| **作者背景** | 官方 [`pstack/README.md`](https://github.com/cursor/plugins/blob/main/pstack/README.md) | `[已查證]` | README 自述：待過 Meta、Netflix、Cursor，是 React 核心團隊成員（React Compiler），pstack 是她每天在 Cursor 用的 skill |
| **SpaceX 頭銜** | 轉述的 [Threads 貼文](https://www.threads.com/@mengshyue.tsai/post/DenWauFklqQ) 與 [YouTube 解說影片](https://www.youtube.com/watch?v=b7-2w2T2Lqs) | `[未查證]` | 貼文與影片稱她現任 SpaceX 首席工程師；官方 README 沒有這個說法，沒有第一手來源可查證 |
| **官方外掛** | [`cursor/plugins` 的 `pstack/`](https://github.com/cursor/plugins/tree/main/pstack) | `[已查證]` | 2026-11-16 以 GitHub API 列目錄：`skills/poteto-mode/playbooks/` 共 23 個檔，2026-11-17 重查為 22 個（上游 2026-11-16 移除 `orchestrate.md`）；`skills/` 共 58 個目錄（34 個 skill、24 個 `principle-` 原則）；`agents/` 有 `poteto-agent`、`comment-sicko`。授權 MIT |
| **Claude Code 官方支援** | 官方 README 與 [`docs/harness/claude-code.md`](https://github.com/cursor/plugins/blob/main/pstack/docs/harness/claude-code.md) | `[已查證]` | README 直接給 Claude Code 安裝指令，另有一份名稱對照表 |
| **社群移植版 `pstack-claude`** | [`michael-denyer/pstack-claude`](https://github.com/michael-denyer/pstack-claude) | `[已查證]` repo 存在與自述；`[未查證]` 安裝與實際可用性 | 原貼文作者在留言推薦的版本。repo 自述涵蓋 Antigravity、Claude Code、Codex、Copilot、Gemini、OpenCode 等（GitHub API：約 4,400 星） |
| **社群移植版 `open-pstack`** | [`ericlitman/open-pstack`](https://github.com/ericlitman/open-pstack) | `[已查證]` repo 存在與自述；`[未查證]` 安裝與實際可用性 | repo 自述是給 Claude Code 與 Codex 用、追蹤官方上游的版本（約 580 星） |
| **解說影片的數字** | YouTube 解說影片字幕 | `[已查證]` 與官方不完全一致 | 影片說「24 條原則、23 套 playbook、30 個 skill」；原則數量相符；playbook 在 2026-11-16 查證時相符、隔天上游移除一套後為 22 套；skill 在查證當天是 34 個 |

---

## 2. 整體結構

官方 README 的定位是：少寫、但寫出品質高且可驗證的程式碼，而不是衝產出量。使用者只需要記得兩步——先跑 `/setup-pstack` 選模型，之後需要嚴謹工程時用 `/poteto-mode`。

```text
/poteto-mode <任務>
      │
      ├─ 1. 先用自己的話複述使用者的目標、要解決的問題、預期的最小改動（不等確認）
      ├─ 2. 讀原則索引（24 條，分 core／architecture／verification／delegation／meta）
      ├─ 3. 把任務對到一套 playbook，開待辦清單，前幾項照抄該 playbook 的步驟
      │      └─ 沒有合適的 playbook、或大型跨區域工作 ──▶ figure-it-out skill
      ├─ 4. 步驟需要時再呼叫其他 skill
      │      （why、architect、arena、swarm、interrogate、tdd、unslop、no-comments…）
      ├─ 5. 在對應的介面上實際驗證；「不確定」或驗錯介面都不算通過
      └─ 6. 以「Opening a PR」playbook 收尾（每套 playbook 最後都會呼叫它）
```

- **收到指令的那個對話負責跑 playbook**，並擁有待辦清單與所有子代理；寫程式的工作多半交給子代理（官方附 `poteto-agent` 子代理定義），主對話負責規劃、審查與驗證。
- **自主程度**：可逆的工作直接做；不可逆的寫入（對共用分支強制推送、部署、刪資料、發訊息給客戶）一定先停下來。
- **官方沒有規劃類 skill**：README 說明作者認為最好的規格就是程式碼，要做計畫時 `/poteto-mode` 可以處理，但不是預設。

---

## 3. 入口 `/poteto-mode` 在三種 CLI 的用法

### 3.1 各 CLI 支援情況

| CLI | 官方是否支援 | 安裝與呼叫 | 查證狀態 |
| :--- | :--- | :--- | :--- |
| **Cursor** | 是（原生） | `/add-plugin pstack`，之後用 `/setup-pstack`、`/poteto-mode <任務>` | `[已查證]` 官方 README |
| **Claude Code** | 是 | `/plugin marketplace add cursor/plugins` → `/plugin install pstack@cursor-plugins`；指令多一個前綴：`/pstack:setup-pstack`、`/pstack:poteto-mode <任務>` | `[已查證]` 官方 README；未在本機實測 |
| **Codex CLI** | 否 | 官方沒有提供安裝方式。兩個社群移植版都自述支援 Codex | `[未查證]` 移植版的安裝與呼叫方式 |
| **Antigravity** | 否 | 官方沒有提供安裝方式。`pstack-claude` 自述支援 Antigravity | `[未查證]` 移植版的安裝與呼叫方式 |

Codex CLI 與 Antigravity 這兩列刻意不寫指令：官方沒有，移植版的也沒有讀過與試過，寫出來就是編的。要用的話先讀移植版自己的 README；安裝前照本機規範對技能包做安全檢查，不直接執行來路不明的安裝腳本。

### 3.2 Claude Code 與 Cursor 的差異

依官方 `docs/harness/claude-code.md`：

| 項目 | Cursor | Claude Code |
| :--- | :--- | :--- |
| 指令與子代理名稱 | `/poteto-mode`、`poteto-agent`、`comment-sicko` | `/pstack:poteto-mode`、`pstack:poteto-agent`、`pstack:comment-sicko` |
| 在一個 skill 裡呼叫另一個 pstack skill | 直接用 `/名稱` | 讀該 skill 的 `SKILL.md` 後照做（文件寫明 `Skill` 工具會拒絕多數 pstack skill） |
| 派子代理 | `Task` | `Agent` |
| 問使用者 | `AskQuestion` | `AskUserQuestion` |
| 模型設定檔 | `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md`（由 `/pstack:setup-pstack` 寫入） |
| 非 Claude 的模型（例如 Gemini） | 可指定 | 不指定模型，改用目前對話的模型，並說明 |
| 只有 Cursor 才有的功能（Automations、Bugbot、雲端代理） | 可用 | 跳過該步驟，回覆中留一行說明後繼續 |
| 自動更新 | — | 第三方市集預設不自動更新；可在 `/plugin` 的市集分頁開啟，或手動 `claude plugin update pstack@cursor-plugins` |

多模型互審是 `interrogate`、`arena` 等 skill 的重點；在 Claude Code 上非 Claude 的模型會退回目前對話的模型，審查的多樣性會比在 Cursor 上少。這一點是依對照表推論，沒有實測。

---

## 4. 官方 22 套 Playbook

檔案都在官方 `pstack/skills/poteto-mode/playbooks/` 底下（查證日期 2026-11-16）。

### 4.1 詳述的 5 套

以下步驟是官方檔案的摘要，不是逐字翻譯。

#### Bug fix（`playbooks/bug-fix.md`）

每一行要出貨的程式都要能追溯到執行期證據；「可能有幫助」的防禦性修改只是假說，不出貨。

1. **自己重現**：在對應的介面上重現問題。只有在說得出具體理由、而且已經盡量推進之後，才請使用者幫忙重現。
2. **二分找原因**：列出候選假說，每一輪選能排除最多可能性的切法，拿執行期證據逐一排除；狀態不清楚就加紀錄，不用猜的。
3. **規劃修法**：跨函式邊界先跑 `architect`，實作交給子代理並給明確範圍。
4. **在同一個介面上驗證**：原本的重現步驟現在要通過。單元測試只說明分支行為，不代表問題消失。
5. **整理 commit**：讓「會失敗的重現」排在修正之前；有便宜的本機測試路徑時搭配 `tdd` skill。
6. 執行 Opening a PR。

回覆要包含：壞了什麼、根因、修法、怎麼驗證，並原樣貼出先失敗後通過的輸出。

#### Feature（`playbooks/feature.md`）

1. 追蹤受影響的子系統。
2. 用 `architect` 平行探索設計。
3. 寫下四項「產能檢查點」：必須先做的步驟、可獨立進行的工作、共用的可變狀態、最小的安全拆法。不適用的項目保留並註明原因。
4. 把寫程式交給子代理，範圍要具體（檔案路徑、資料形狀與組織方式、成功條件）；有多種合理寫法時改用 `arena`。
5. 在對應的介面上驗證。
6. 整理成小而有順序的 commit。
7. 設計有爭議就在出貨前跑 `interrogate`。
8. 執行 Opening a PR。

#### Refactoring（`playbooks/refactoring.md`）

結構改變、行為不變。清理途中發現缺功能或真的 bug，要拆出去另外處理。

1. **先固定行為**：寫特徵測試、快照或等價比對工具，記下目前行為。型別檢查與 lint 不算。
2. 指出程式缺的是什麼結構；改寫必須刪掉分支或不合法狀態，而不是多加一層。
3. 寫下目標形狀（模組配置、型別、呼叫關係）。
4. **先減後加**：先刪死碼、只有一個呼叫者的包裝、多餘的檢查。
5. 小步移動，每一步都保持測試通過；改 API 時在同一波把所有呼叫者搬完並刪掉舊 API，不留相容層。
6. 在真實產物上證明行為沒變，不是「編得過」就算。
7. 確認值得保留：衡量標準是讀的人負擔變輕，沒有就還原。
8. 整理成小 commit（先刪減、再改形狀、再收尾），執行 Opening a PR。

#### Investigation（`playbooks/investigation.md`）

唯讀，產出有引用依據的解釋或建議，不改程式。

1. 追蹤問題相關的程式；問「為什麼這樣做」時另外走 `why` skill。
2. 產能檢查點只寫一行「不適用，唯讀調查」。
3. 產出說明（總覽／關鍵概念／運作方式／東西在哪／注意事項），或在要做選擇時給附取捨表的建議。
4. 對回覆套用 `unslop`。

不開 PR。調查完若要改程式，交還給使用者並改走 Bug fix 或 Feature。

#### Perf issue（`playbooks/perf-issue.md`）

每個修正都要對應到量測，不能用讀原始碼代替量測。

1. 擷取基準追蹤，並用 `benchmark-checklist` 檢查這個數字與之後每個數字可不可信。
2. 追蹤程式來建立假說。依序嘗試七個做法，從最便宜的開始：不做、做了別再做、少做、晚點做、趁沒人注意時做、平行做、做得更便宜；前面的做法達標就停。
3. 依追蹤結果規劃修法，實作交給子代理，審查差異後再擷取一次。
4. 解析並比較前後產物。
5. 在 PR 中引用量測結果。
6. 執行 Opening a PR。

要對某個指標持續改善而不是一次性修正，改用 Hillclimb。

### 4.2 僅列名的 18 套

用途依官方 README 的 playbook 表整理。

| 檔案 | 用途 |
| :--- | :--- |
| `playbooks/hillclimb.md` | 針對單一指標持續改善：反覆提出假說、前後量測，每個被接受的改善一個 commit |
| `playbooks/runtime-forensics.md` | 從即時觀測診斷執行期症狀（洩漏、閒置時吃 CPU、畫面異常）；產出是診斷，不是修正 |
| `playbooks/trace-forensics.md` | 診斷事後拿到的效能剖析檔（CPU profile、追蹤、堆積快照） |
| `playbooks/prototype.md` | 用完即丟的草稿，便宜地做出設計或行為上的決定 |
| `playbooks/visual-parity.md` | 兩個實作之間像素等級的介面一致 |
| `playbooks/authoring-a-skill.md` | 撰寫或修改 `SKILL.md` |
| `playbooks/eval.md` | 以盲測檢驗 skill 或提示詞的改動對 agent 行為的影響 |
| `playbooks/babysit.md` | 把一個 PR 或一疊 PR 帶到可合併：衝突、審查討論、CI |
| `playbooks/shipping.md` | 獨立驗證已通過檢查的一疊 PR，再由下往上合併連續通過驗證的那一段 |
| `playbooks/autonomous-run.md` | 把長任務一路做到完成，中途不停 |
| `playbooks/autopilot-full.md` | 多個互相獨立的 PR 一路做到合併，每個 PR 一個負責者 |
| `playbooks/autopilot-stack.md` | 同上但不合併，建好並驗證後交給操作者審查與合併 |
| `playbooks/session-pickup.md` | 接續或接手先前 agent 進行到一半的工作 |
| `playbooks/pause-safely.md` | 乾淨地暫停進行中的工作，之後可以接續 |
| `playbooks/multi-phase-plan.md` | 跨多個階段或堆疊 PR 的工作 |
| `playbooks/worktree-cleanup.md` | 清掉已合併或已放棄的 worktree 與過期的 iOS 模擬器來釋放磁碟空間 |
| `playbooks/opening-a-pr.md` | 以小而有順序的 commit 開 PR；每套 playbook 結束時都會呼叫 |

---

## 5. 官方 Skill 與原則

`/poteto-mode` 會在步驟需要時自動呼叫大部分 skill，也可以單獨使用。官方 `skills/` 目錄在查證當天有 34 個 skill 與 24 個以 `principle-` 開頭的原則。

### 5.1 playbook 最常用到的 skill

| Skill | 官方說明的用途 |
| :--- | :--- |
| `/how` | 說明一個子系統怎麼運作 |
| `/why` | 回答「為什麼做成這樣」：依據是 commit 與 PR 討論等紀錄，不是只看程式；會標出哪些是自己的推論 |
| `/architect` | 程式要跨函式邊界之前，先定好呼叫方式、型別與模組形狀 |
| `/arena` | 同一件事平行做 N 份，再取各份最好的部分 |
| `/swarm` | N 個平行工作者各做不同切片，最後合成一份報告 |
| `/interrogate` | 把一份差異交給不同模型設法找出問題，只保留實際執行能證明的發現 |
| `/tdd` | 修 bug 且有便宜的本機測試路徑時：先寫會失敗的測試，再修 |
| `/no-comments` | 審查前清理註解 |
| `/unslop` | 清理文字裡的 AI 腔 |
| `/benchmark-checklist` | 量到加速或退步之後，回報或採取行動前先檢查這個數字 |
| `/figure-it-out` | 沒有合適的內建 playbook 時，替這個任務設計一套嚴謹、可稽核的 playbook |
| `/show-me-your-work` | 留下可審查的決策紀錄 |

### 5.2 其餘 skill（僅列名）

入口與設定：`poteto-mode`、`poteto-help`、`setup-pstack`、`automate-me`。
理解與回顧：`recall`、`ketchup`、`ketchup-video`、`teach`、`bro`、`in-your-own-words`、`sharpen`、`blast-radius`。
驗證：`create-verification-skill`、`maintain-verification-skill`、`create-formal-verification-skill`、`maintain-formal-verification-skill`、`statechart`。
其他：`reflect`、`correct`、`technical-writing`、`typescript-best-practices`、`make-bot-ui`。

### 5.3 24 條原則的分組

| 分組 | 數量 | 例子 |
| :--- | :--- | :--- |
| core | 10 | `laziness-protocol`（偏向刪除與最小改動）、`subtract-before-you-add` |
| architecture | 6 | `model-the-domain`、`boundary-discipline` |
| verification | 5 | `prove-it-works`（對真實產物驗證）、`fix-root-causes` |
| delegation | 2 | `guard-the-context-window`、`never-block-on-the-human` |
| meta | 1 | `encode-lessons-in-structure` |

### 5.4 官方沒有附帶的東西

`/poteto-mode` 會提到但不在 pstack 裡的：`deslop`、`control-cli`、`control-ui` 在另一個外掛 `cursor-team-kit`；`/create-skill` 是 Cursor 內建。另外 pstack 附了一組預設不啟用的自動化套件，只能在 Cursor 上跑。

---

## 6. 三個使用實例

以下三個任務情境是本文件自己設計的示意，用來對照官方步驟；**沒有實際執行過，表中沒有任何一格是實測輸出**。Codex CLI 與 Antigravity 沒有官方安裝方式，要透過社群移植版，呼叫方式未查證，所以只列 Cursor 與 Claude Code 的輸入。

### 實例 1：Bug fix（訂單逾時取消後沒有歸還庫存）

| 項目 | 內容 |
| :--- | :--- |
| **Cursor 輸入** | `/poteto-mode 訂單逾時取消後沒有歸還預扣的庫存。先重現，再修正並驗證。` |
| **Claude Code 輸入** | `/pstack:poteto-mode 訂單逾時取消後沒有歸還預扣的庫存。先重現，再修正並驗證。` |
| **對到的 playbook** | `playbooks/bug-fix.md` |
| **官方步驟對應** | 自己在同一個介面上重現逾時取消 → 二分找出沒有歸還庫存的那一段 → 規劃修法並交給子代理 → 用原本的重現步驟驗證 → 讓失敗的重現排在修正之前 → 開 PR |
| **回覆應包含** | 壞了什麼、根因、修法、驗證方式，以及先失敗後通過的輸出原文 |

### 實例 2：Feature（替資料抓取模組加上有期限的磁碟快取）

| 項目 | 內容 |
| :--- | :--- |
| **Cursor 輸入** | `/poteto-mode 替資料抓取模組加上有期限、會寫入磁碟的快取。確認它真的能用。` |
| **Claude Code 輸入** | `/pstack:poteto-mode 替資料抓取模組加上有期限、會寫入磁碟的快取。確認它真的能用。` |
| **對到的 playbook** | `playbooks/feature.md` |
| **官方步驟對應** | 追蹤抓取模組 → `architect` 探索設計 → 寫四項產能檢查點 → 指定資料形狀與範圍後交給子代理（有多種寫法時用 `arena`）→ 實際驗證 → 整理 commit → 有爭議時 `interrogate` → 開 PR |
| **回覆應包含** | 做了什麼、選了什麼與原因、產能檢查點、還沒決定的事 |

### 實例 3：Refactoring（把巢狀條件的查詢組裝改成鏈式呼叫）

| 項目 | 內容 |
| :--- | :--- |
| **Cursor 輸入** | `/poteto-mode 重構查詢組裝模組，把巢狀條件改成鏈式呼叫，行為不變。` |
| **Claude Code 輸入** | `/pstack:poteto-mode 重構查詢組裝模組，把巢狀條件改成鏈式呼叫，行為不變。` |
| **對到的 playbook** | `playbooks/refactoring.md` |
| **官方步驟對應** | 先寫特徵測試固定目前輸出 → 指出缺的結構與目標形狀 → 先刪死碼與多餘包裝 → 小步改寫且每步保持測試通過、同一波搬完呼叫者並刪舊 API → 在真實產物上證明行為沒變 → 確認讀的人負擔有變輕 → 整理 commit 並開 PR |
| **回覆應包含** | 改了什麼結構、用什麼固定行為、等價證明、讀者負擔的變化、哪些出貨哪些還原 |

---

## 7. 與本機既有做法的對照

這一節是本文件自己整理的類比，不是官方內容；左右兩邊只是目的相近，做法並不相同。

| pstack 的做法 | 本機目的相近的規範或技能 |
| :--- | :--- |
| 修 bug 先重現、每行修改對應執行期證據 | 全域規範「完成必附證據」、`ai-quality-gates` |
| `prove-it-works`：對真實產物驗證 | `verification-protocol` |
| `interrogate`：多模型找問題 | `ai-review`、`blind-review` |
| `arena`／`swarm`：平行派工 | 子代理平行派工 |
| `/poteto-mode` 依任務選 playbook | `task-orchestrator` 的任務分派 |

pstack 的嚴格驗證做法落到本機規範與關卡的過程，見 [`pstack-governance-integration.md`](./pstack-governance-integration.md)。
