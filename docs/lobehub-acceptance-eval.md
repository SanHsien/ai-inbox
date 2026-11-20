# lobehub/acceptance 唯讀檢閱：驗收回合格式與本機 verification-protocol 的借鏡點

檢閱日期：2026-11-19。任務：T-20261119-03。作者：Claude Code。
來源筆記：[`notes/2026-11-19-lobehub-super-agent-and-acceptance-eval.md`](../notes/2026-11-19-lobehub-super-agent-and-acceptance-eval.md)。

**結論：不安裝技能與 `lh` CLI；借鏡它的規則與目錄格式。** 這個 repo 只有一份技能文件與幾支輔助腳本，真正做驗證、產生報告頁、上傳的 `lh` CLI 不在裡面，無法檢閱。但技能文件把「什麼才算一次有效的驗收」寫得很具體，其中五條規則本機的 `verification-protocol` 沒有，可以直接改寫進去。

與筆記的差異（先講）：筆記與來源文章寫檢查項是 `C1..Cn`。在這個 commit 的 repo 裡，檢查項的識別碼是 `plan[].id` 這個自由字串，範例用的是 `"1"`、`"2"`（`skills/acceptance/references/report-schema.md:19`、`:76`）；全庫沒有 `C1..Cn` 的命名規定。`references/probe-mock-patterns.md` 第 196 至 238 行有 `C1` 到 `C5`，那是該檔 C 節的條目編號，與檢查項無關。文章截圖裡的 `C1..C5` 同時出現在 LobeHub 任務頁（文章圖 29）與 `lh acceptance view` 的 `C#` 欄（圖 32），較可能是產品與 CLI 顯示時加的編號，不是某次執行自取的名字；CLI 不在 repo 內，未查證（2026-11-20 補看全部 33 張圖後更正原先的推測）。

## 1. 來源與審查範圍

- Repo：[lobehub/acceptance](https://github.com/lobehub/acceptance)，Apache-2.0，技能版本 0.10.2（`.claude-plugin/plugin.json:3`、`skills/acceptance/SKILL.md:5`）。
- 審查 commit：`5e9115da117f54fafadd56083e83394ba2dc4a76`（2026-11-14）。
- 取得方式：`git clone --depth 1`，加上 `-c core.hooksPath=NUL -c core.symlinks=false`，放在 `C:\GitHub\_sandbox\lobehub-acceptance-audit`。只讀文字；沒有安裝、沒有執行腳本、沒有 `lh login`。
- 規模：48 個追蹤檔，共 7185 行。`skills/acceptance/` 37 個檔：`SKILL.md`（455 行）、`references/` 22 份、`surfaces/` 5 份、`scripts/` 5 支。
- 本文路徑省略 `skills/acceptance/` 開頭（`README.md` 與 `.github/` 除外），行號對應上述 commit。

**不在這個 repo 裡、因此未查證的部分**：`lh` CLI（README 第 191 行寫安裝方式是 `npm install -g @lobehub/cli`）。以下行為都是技能文件的說法，沒有原始碼可對：上傳時丟掉不合格的檢查項、缺證據類型時標成 `uncertain`、產生 `report.html`、讀回審閱者的決定。`agent-browser` 這個瀏覽器驅動工具同樣不在 repo 內。

## 2. 機器掃描結果

指令：`python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack C:\GitHub\_sandbox\lobehub-acceptance-audit`

結束碼 **1**。掃描 63 個檔案：FAIL 1 項、需人工審查 2 項、未掃描 0 個。

| 命中 | 位置 | 人工判讀 |
| --- | --- | --- |
| 遠端內容接管線執行 | `surfaces/electron.md:70` | 誤判。對象是本機 `localhost:9222` 的除錯埠，把回傳的 JSON 交給 `python3 -c` 取出分頁識別碼，不是下載後執行 |
| 動態執行 | `references/probe-mock-patterns.md:274` | 說明文字裡提到 `agent-browser` 的 `eval` 子指令，不是程式 |
| 動態執行 | `.git/hooks/pre-receive.sample:14` | git 內建範例檔 |

人工另外看到的風險（都是文件裡寫給 agent 的指示，依規則記錄、不照做）：

| 編號 | 內容 | 位置 | 風險 |
| --- | --- | --- | --- |
| R1 | 安裝方式之一是叫 agent 去讀一個網址並照上面的指示做 | `README.md:183` | 高。遠端內容隨時可改，等於把指令來源交給外部網頁 |
| R2 | 登入後預設把報告與證據上傳到 LobeHub；個人帳號的報告「有連結的人都能開」 | `README.md:156`、`:159` | 高（對本機而言）。截圖與錄影可能含私人資料。未登入時只產生本機報告（`README.md:149`、`SKILL.md:190-193`） |
| R3 | 要求不要向使用者請求一般性的計畫核准 | `SKILL.md:78`、`references/acceptance-checker.md`「The checker replaces routine user plan approval」段 | 中。與本機「多解先問」的規則方向相反 |
| R4 | 登入用「直接注入」，並提供把瀏覽器請求的 Cookie 標頭複製進自動化工作階段的做法 | `SKILL.md:273`、`references/auth-web.md:47-66` | 中。文件自己限定只用於本機與開發環境（`auth-web.md:65-66`），但本機規則是不讀瀏覽器 Cookie |
| R5 | 輔助腳本會結束行程 | `scripts/resource-guard.sh:355-363` | 低。註解寫明只處理本次執行登記的行程群組，不依名稱結束（第 39 行）；未執行，行為未驗證 |

平台：`.github/workflows/test.yml:21` 的測試只跑 Ubuntu 與 macOS；原生 App 與 iOS 兩種執行面只支援 macOS（`surfaces/native.md:1-10`、`surfaces/ios-simulator.md:4`）；輔助腳本都是 bash。Windows 上能不能用：未查證。

## 3. 核心工作流

```text
使用者的需求（一句話的目標）
   │
   ▼
① 判斷要不要跑 ── 純文件／重構、或已有涵蓋這次交付的報告 → 不重跑，沿用舊證據
   │              （SKILL.md:26-56）
   ▼
② 寫計畫 plan[] ── 每項：id、標題、類別、驗證者、方法、預期、必要證據類型
   │               只能寫「人看得到、能決定收不收」的結果
   │               測試、型別檢查、lint、建置通過 不可列為檢查項（SKILL.md:232-246）
   ▼
③ 計畫審查 ── 另一個全新上下文的 checker，最多回饋兩次（SKILL.md:73-80）
   ▼
④ 選執行面並採證 ── CLI／Web／Electron／macOS 原生／iOS 模擬器（SKILL.md:285-292）
   │                邊做邊存：證據進 assets/，結果進 result.json（SKILL.md:420-422）
   ▼
⑤ 證據審查 ── checker 親自打開每張圖、每段影片，只審一次（references/report.md 步驟 7）
   ▼
⑥ 自查覆蓋 ── 每個檢查項宣告的證據類型都至少有一份；缺 → uncertain，交付擱置
   │           （SKILL.md:364-367）
   ▼
⑦ 產生報告 ── 未登入：本機 report.html　已登入：上傳到 LobeHub
   ▼
⑧ 人審閱 ── 逐項接受或打回（可在截圖上圈出區域並留言）
   │
   └─ 被打回 → 開「新的一回合」：只重做被打回與受影響的項目，
                已接受的不重跑；舊回合不可改（SKILL.md:248-261）
```

角色分工（`SKILL.md:58-86`、`references/acceptance-checker.md:1-50`）：

```text
primary（寫程式的那個 agent）   保留範圍、產品決定、修程式、交付責任
   ├─ acceptance-runner         全新上下文、較便宜的模型：環境、操作產品、採證、組報告、清理
   └─ acceptance-checker        全新上下文：審計畫、審證據；不得啟動服務、不得改程式、不得上傳
```

採證流程（Web，`surfaces/web.md`）：以具名工作階段開瀏覽器 → 讀頁面結構 → 操作 → 截圖；前後端都有變更時同時錄網路請求（HAR）與截圖；隨時間變化的行為要錄影而不是截圖，影片要標章節（步驟、驗證點、發現的異常，`references/video-chapters.md:15-50`）；結束時關掉自己開的工作階段，不可一次關全部。

## 4. `.acceptances/` 目錄與 `result.json` 格式

目錄（`references/report.md:67-83`）：

```text
.acceptances/
├── .gitignore                     內容只有 *，整棵樹不進 git
└── <主題鍵>/                      topic-… ／ task-… ／ document-… ／ standalone-<代稱>
    ├── acceptance.json            這些回合屬於哪一個驗收（CLI 寫）
    ├── report.html                本機模式：所有回合合成的一頁（CLI 寫）
    ├── reviews.json               本機模式：審閱者存下的決定（CLI 寫）
    └── <YYYYMMDD-HHMMSS>-<代稱>/  一個回合；寫完不可再改
        ├── result.json            報告本體，頁面由它產生
        ├── proposal.md            這一回合交付什麼、希望審閱者看哪裡
        ├── report.md              只放敘述性的結尾（結論、後續、分數）
        └── assets/                證據檔
```

`result.json` 的欄位（`references/report-schema.md:15-103`、`references/report.md` 的「Closed vocabularies」表）：

| 區塊 | 欄位 | 可用值或說明 |
| --- | --- | --- |
| `plan[]` | `id`、`title`、`category`、`method`、`expected` | `id` 是穩定鍵，後續回合沿用；`category` 寫需求領域，不寫技術層 |
| `plan[]` | `verifier` | `program`／`agent`／`llm`，預設 `agent` |
| `plan[]` | `requiredEvidence` | `screenshot`／`gif`／`video`／`audio`／`text`／`markdown`／`dom_snapshot`／`transcript` |
| `plan[]` | `supersedes` | 這一項取代哪個舊識別碼 |
| `cases[]` | `id`、`name`、`category`、`surface`、`observation` | `id` 對應計畫項；`observation` 一到三句 |
| `cases[]` | `status` | `pass`／`fail`／`blocked`（沒辦法跑；不算通過） |
| `cases[]` | `evidence[]` | `{path, description}`，描述必填；前後對比另加 `comparison: {id, role: before/after, layout, label}` |
| `cases[]` | `datasets[]`、`visualizations[]` | 結構化數據用內建圖表呈現，不要截成圖片 |
| `summary` | `total`、`passed`、`failed`、`blocked`、`verdict`、`conclusion` | `verdict`：`pass`／`fail`／`partial` |
| 頂層 | `title`、`entry`、`surfaces`、`createdAt` | `surfaces`：`web`／`desktop`／`cli`／`mobile`／`bot` |
| 頂層（選填） | `branch`、`commit`、`pullRequest` | 來源資訊 |

多輪打回怎麼沉澱：

- **每個檢查項各自有歷史**。修復前先讀彙總，最新決定是「接受」的項目略過；被打回的項目用原本的識別碼重做（`SKILL.md:254-261`）。
- **失誤清單分兩層**。隨技能發行的通用層唯讀；專案自己的放在 `.agents/acceptance/common-mistakes.md`（`references/common-mistakes.md:3-7`）。每一條帶 `since`（第一次發生）與 `holds-while`（它依賴的機制）；一旦有工具能自動擋下，那一條就刪掉，不留著當參考（同檔第 23-29 行）。
- **專案層另有三個檔**記錄怎麼啟動、流程規定、怎麼強制製造狀態（`SKILL.md:95-100`）。

## 5. 本機 verification-protocol 可借鏡的項目

本機現況：`verification-protocol` 技能正本在 [`SanHsien/harness-guard`](https://github.com/SanHsien/harness-guard) 的 `skills/verification-protocol/SKILL.md`（99 行，檢閱時為 commit `ec38c1d`）。它的證據是「指令與結束碼」；對畫面行為只寫了一句：無法自動驗證就回報「未驗證，需人工確認」（第 1 節）。也就是說，本機對「使用者看得到的結果」沒有驗收格式。

| 編號 | lobehub/acceptance 的規則 | 位置 | 本機現況 | 建議 |
| --- | --- | --- | --- | --- |
| B1 | 先寫可觀察的檢查項，每項宣告必要的證據類型；缺那一類證據就不能算過 | `SKILL.md:17-20`、`:364-367` | 沒有 | **採用**。畫面類變更動工前先列檢查項與各自要的證據（截圖、錄影、文字輸出） |
| B2 | 程式化的關卡（測試、lint、建置）不是驗收檢查項，只在報告裡寫一行 | `SKILL.md:232-246` | 相反：目前只有程式化關卡 | **採用為補充**。兩種都要：測試綠燈是必要條件，但不能代替「打開來看過」 |
| B3 | 不可能失敗的執行不能當證明：先重現失敗的前提，再在同樣前提下驗證 | `SKILL.md:275` | agent-relay 的 TDD 閘門有同樣精神，技能文字沒寫 | **採用**，一句話即可 |
| B4 | 截圖要由指定的人實際打開看過才能支持通過；檔案存在或有圖說不算 | `references/common-mistakes.md` 的 M1、`references/report.md` 步驟 2 | 協作規則有「介面用瀏覽器截圖當證據」，沒寫要打開看內容 | **採用** |
| B5 | 證明正在跑的是工作目錄裡的程式：量一個改過的值 | `references/common-mistakes.md` 的 M6 | 沒有 | **採用**。開發伺服器沒重啟、快取沒清是常見的假通過來源 |
| B6 | 改到既有畫面要有前後對比，同一畫面、同一狀態、各一張 | `SKILL.md:304-312` | 沒有 | 採用為建議，不強制 |
| B7 | 非畫面的行為要兩份文字證據：推理（主張、方法、通過條件）與執行紀錄（指令、原始輸出、結束碼） | `references/evidence.md`「Dual text evidence」段 | 「回報指令與實際輸出」已涵蓋後半 | 不必改 |
| B8 | 回合不可改；修完重驗是新的一回合 | `SKILL.md:248-252` | 沒有回合的概念 | 見下方第 3 點 |
| B9 | 舊證據仍涵蓋這次交付就沿用，不因 commit 不同就重跑 | `SKILL.md:44-50` | 已有（「Do not repeat valid checks by habit」段） | 不必改 |
| B10 | 沒跑到的項目標 `blocked`，不算通過 | `references/report.md` 步驟 3 | 已有（「not run 不是通過」） | 不必改 |

具體建議（都沒有動手，等維護者決定）：

1. **在 `SanHsien/harness-guard` 的 `skills/verification-protocol/SKILL.md` 加一節「使用者看得到的結果」**，內容是 B1 至 B5 的改寫，約 15 行。細節放新檔 `skills/verification-protocol/references/observable-checks.md`，附一份最小的檢查項範例。改完依該 repo 的安裝流程同步到各 agent。
2. **截圖證據沿用既有的隱私檢查**。lobehub 的規則只寫「不要上傳憑證與無關視窗」（`references/evidence.md`「Artifact safety」段）；本機已有更具體的 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks) `tools/screen_privacy.py`，新增的那一節要指向它。
3. **目錄格式先不落地**。`.acceptances/<主題>/<時間>-<代稱>/result.json + assets/` 這個形狀值得記下來，但它的價值來自那個能把多回合合成一頁、讓人逐項接受或打回的報告頁，而那是 `lh` CLI 做的。本機若要有同樣的東西得自己寫產生器，目前沒有足夠多的畫面類驗收需求撐起這個成本。等出現第二個需要多輪打回的畫面類專案時再評估。
4. **失誤清單的 `since`／`holds-while` 寫法**可用在本機任何「踩過的坑」清單：每條寫明它依賴什麼機制，機制被工具取代就刪。這與本機「撞到坑就修根因，不留操作提醒」的做法一致，屬於寫法上的參考，不需要改檔。

明確不採納：

- 安裝技能或 `lh` CLI：CLI 無原始碼可審，登入後預設上傳（R2）。
- 「不向使用者請求計畫核准」（R3）與 Cookie 注入登入（R4）：與本機規則相反。
- runner 與 checker 的三角色分工：本機已有「派子 agent、重要產出交全新上下文驗收」的規則，不需要另一套角色名稱。

## 6. 已知限制

- 只讀了技能文件與腳本的原始碼。`lh` CLI 與 `agent-browser` 沒有檢閱，所有「上傳時會擋」的說法都是文件的自述。
- 22 份 `references/` 沒有全部逐行讀完：完整讀了 `SKILL.md`、`report.md`、`report-schema.md`，其餘讀了與 DoD 相關的段落（`plan-format.md`、`evidence.md`、`acceptance-checker.md`、`common-mistakes.md`、`auth-web.md`、`surfaces/web.md`、`video-chapters.md`）。`flows.md`、`delegation.md`、`interaction-cost.md`、iOS 與 macOS 原生相關文件只看了檔名或片段。
- 沒有實際跑過一個回合，`report.html` 長什麼樣、審閱決定怎麼存回來，都沒有親眼確認。
- README 第 183 行那個安裝說明網址沒有打開：打開它等於去讀一份寫給 agent 的遠端指示，不在唯讀檢閱範圍內。
