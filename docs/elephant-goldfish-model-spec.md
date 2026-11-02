# 大象-金魚模型（EGM）規格手冊：長上下文起草、零上下文審查與 CUJ 驅動設計流程

> 對應筆記：[`notes/2026-11-02-google-elephant-goldfish-model-software-design-review.md`](../notes/2026-11-02-google-elephant-goldfish-model-software-design-review.md)（任務 `T-20261102-04`）。配套範本：[`templates/egm-workflow-prompts.md`](../templates/egm-workflow-prompts.md)。
>
> 讀完這份手冊，你能：判斷一個功能要不要走 EGM；知道三個角色各自看得到什麼；照五個審查階段逐項驗核一份設計文件；把 `concepts_brief.md` 一路推到 `docs/designs/`；並分得清哪些是上游（Google 的 EGM 專案）的規定、哪些是本 repo 自己的取捨。

## 0. 查證基準與範圍

| 項目 | 內容 |
| :--- | :--- |
| 上游 repo | <https://github.com/google/elephant-goldfish-model> |
| 查證 commit | `403d8881d62022490637d740657b33f01e321ea8`（2026-10-30 的 `main`，查證日 2026-11-02 為最新）；以下「上游」一律指這個 commit 的內容，檔案路徑也以此為準 |
| 擁有者 | GitHub 組織 `google`（以 GitHub API 查證，`owner.type` 為 `Organization`）；授權 Apache-2.0 |
| 官方程度 | 上游 README 末段寫明：「This is not an officially supported Google product.」所以「Google 官方開源」只能說「放在 `google` 組織下的開源專案」，不能說是 Google 官方支援的產品 |
| 原創文獻 | Dave Rensin〈Elephants, Goldfish, and the New Golden Age of Software Engineering〉（Medium）。上游 `docs/designs/architecture.md` 的作者欄列有 Dave Rensin，並引用該文。**本手冊沒有開啟該文章頁面，文章內容一概未驗證** |
| 官網 | <https://egm.dev>：上游 README 與 `.claude-plugin/plugin.json` 把它列為 homepage，本手冊**未開啟該網站**，內容未驗證 |

本手冊的來源是上游 repo 的原始檔（README、`skills/*/SKILL.md`、`agents/*.md`、`resources/`、`docs/`）。上游的 Claude Code 外掛、Codex、Antigravity 整合細節，我只讀了文件，**沒有實際安裝或執行過外掛**；凡是「實測」二字，只用在本 repo 自己跑過的東西。

### 0.1 筆記與上游不一致之處（以上游為準）

筆記是 agent 自動產生的線索，下列幾點與上游原始檔對不上，本手冊已改正，後續引用請以本手冊為準：

| 筆記的說法 | 上游實際內容 | 本手冊的處理 |
| :--- | :--- | :--- |
| 五階段審查是「完整性、清晰度、代碼適配、實作可行性、假設審查」 | `skills/egm-review/SKILL.md` 的五階段是 Stage 5 Initial Zoom Out Review、Stage 6 Comprehension Review（Comprehension Test）、Stage 7 Design Critique（Critic Review）、Stage 8 Intermediate Zoom Out Review、Stage 9 Implementation Readiness（Test）。筆記那五項名稱在上游找不到 | 第 4 節照上游階段名稱與編號 |
| 七大工作流是 Brainstorm、Draft、Review、Resolve、Bootstrap、Review-loop、Drift-report | 名單與上游 `skills/` 目錄、`docs/designs/architecture.md` 的 Skills Layer 一致（`egm-brainstorm`、`egm-draft`、`egm-review`、`egm-review-loop`、`egm-resolve`、`egm-drift-report`、`egm-bootstrap`） | 沿用 |
| 「未通過審查並核准前，嚴禁產生任何功能代碼」 | 上游沒有這種硬閘門。`resources/execution_instructions.md` 規定的是：**在 EGM 設計流程進行中**，agent 不得在原始碼樹內寫正式實作檔（Design-Only Scope）。`docs/getting_started.md` 說流程「is not a prescription」，單純 bug 修復不必走設計優先。核准後才實作是上游流程圖的順序，不是工具強制的閘門 | 第 6 節把「核准前不寫碼」標為**本 repo 建議**，不當成上游規定 |
| 審查員檢查「CUJ 是否有未覆蓋的情境」 | CUJ 出現在設計文件範本（`skills/egm-draft/references/design_doc.md` 的 `Critical User Journeys (CUJs)` 一節，格式為 Given/When/Then）與 `architecture.md` 的 Elephant 定義；上游 `agents/*.md` 的審查員提示詞中沒有任何一個提到 CUJ | 第 5 節說明 CUJ 寫法；第 4 節的 CUJ 驗核項標為**本 repo 補充** |
| 「Star: 8,600+」 | 2026-11-02 以 GitHub API 查到 9468 | 手冊不寫星數（會隨時間變動，沒有引用價值） |

## 1. 何時用、何時不用

上游 README 的原話是：功能需要在實作前做設計決策時才用；「small, clear bug fix」用平常的工作流程。`docs/getting_started.md` 同樣說各技能可以亂序使用。

```text
需求進來
  |
  +-- 小而明確的 bug 修復、單檔調整 ----> 不走 EGM，直接實作
  |
  +-- 需要先決定架構、資料模型、介面、
      失敗處理的功能（例如要加 webhook 投遞）
         |
         +--> /egm-brainstorm -> /egm-draft -> /egm-review -> 人工審查 -> 實作
```

## 2. 角色與權責（Elephant / Goldfish / Human）

上游 README「How it works」表與 `docs/designs/architecture.md` 的定義如下，我把它整理成可對照的矩陣。

| 角色 | 是誰 | 看得到什麼 | 負責什麼 | 不可以做什麼 |
| :--- | :--- | :--- | :--- | :--- |
| Elephant（大象） | 主要對話中的 agent，長期持有專案脈絡 | 專案、需求、先前所有決定、整段對話 | 與人討論需求；寫 `concepts_brief.md`、`design_draft.md`；在 `egm-resolve` 中分類審查意見並套用修改 | 不可自己審自己的文件當作 Goldfish 審查（`egm-review` 寫明：沒有 subagent 工具就停止，因為「a review in the same context is not a Goldfish review」）；`egm-resolve` 規定「想反駁」不算證據，反駁要引用審查員讀得到的檔案與符號 |
| Goldfish（金魚） | 每次新開的 subagent，沒有對話歷史 | 角色提示詞（`agents/<file>.md`）、指定的標準（`resources/document_standards/`）、目標文件的指定行範圍、使用者額外給的 `GoldfishContext` 閱讀清單、文件內明確提到或連結的檔案 | 找出未明言的假設、不清楚的需求、實作風險；回報嚴重度（Blocker／Major／Nit）、範圍、描述 | 唯讀：上游每個審查員提示詞都寫「Strict Read-Only Protocol」，不得改檔；Claude Code 的轉接檔 `.claude-plugin/agents/*.md` 把工具限制為 `Read, Grep, Glob`，並設 `omitClaudeMd: true`（上游 `docs/claude.md` 把它列為金魚隔離所需的設定；其確切行為本手冊未驗證） |
| Human（人） | 工程師本人 | 全部成品與審查報告 | 在權衡取捨上做決定；核准設計；決定要實作什麼；再送給另一個人做 PR 審查（`getting_started.md` 第 4 步：「EGM does not replace human oversight」） | 上游 `egm-draft` 規定 agent 遇到有多種合理答案的架構決策時，列出最多三個選項與失效條件，由人選，agent 不得排序、不得標預設 |

### 2.1 上下文可見性矩陣（誰看得到什麼）

「V」看得到，「-」看不到。這張表是設計任何派工時的檢查表：金魚那一欄出現 V 的項目，必須有理由。

| 資訊 | Elephant | Goldfish | Human |
| :--- | :---: | :---: | :---: |
| 對話歷史、被否決的方案的討論過程 | V | - | V |
| `concepts_brief.md` 的「Alternatives Weighed」 | V | 只有在文件內寫出或連結才看得到 | V |
| 目標設計文件（指定行範圍） | V | V | V |
| 文件內提到或連結的原始碼與文件 | V | V | V |
| `GoldfishContext` 閱讀清單 | V | V（由人或 Elephant 指定） | V |
| 其他 Goldfish 的報告 | V（Elephant 彙整） | -（同一階段各自獨立） | V |
| 專案的 `CLAUDE.md`／`AGENTS.md` | V | 預期為 -（Claude Code 轉接檔設 `omitClaudeMd: true`，行為未驗證）；其他平台未驗證 | V |
| 修改檔案的權限 | V | -（唯讀） | V |

> 備註：Claude Code 版本要求。上游 `docs/claude.md` 寫「Use Claude Code 2.1.271 or later for `omitClaudeMd` support. Older versions must not be treated as verified Goldfish isolation environments.」低於此版本，不能當作已驗證的金魚隔離環境。本手冊未驗證你本機的版本。

### 2.2 權責分離協議（上游規定）

1. 起草者不當審查者：審查必須由全新上下文的 subagent 執行；平台沒有 subagent 工具就停止，不得退回同一上下文審查。
2. 審查員只讀不寫；改文件只能由 Elephant 在 `egm-resolve` 後、經人同意才動手（`egm-resolve` 提供「Auto accept」「Continue」「Interactive breakdown」等選項，且在使用者回覆前不呼叫任何工具）。
3. 審查員沒有回報就是沒有審查：`egm-review-loop` 與 `agents/synthesizer.md` 規定逾時、失敗或沒回報的審查員，重試一次，仍失敗記為 `not run`，**不可算成零發現**，且有 `not run` 的一輪不算乾淨。
4. 反駁要可檢查：`egm-resolve` 把每條發現分成 `CONTEST`（附審查員讀得到的證據）、`ESCALATE`（證據在審查員讀不到的地方，交給人）、`PROPOSE FIX`、`DECLINE`（Nit）。「這是故意的」不是證據；也不為了讓零上下文的審查員滿意而硬加內容。
5. 不改嚴重度：覺得 Blocker 其實是 Nit，就用 `CONTEST` 並寫理由，不能直接降級。

## 3. 工程流轉：從 `concepts_brief.md` 到 `docs/designs/`

```text
 人 + Elephant
   |  /egm-brainstorm：多輪開放式提問，直到人確認「Review with Goldfishes」
   v
 [6 個 Goldfish 並行挑戰：egm-design, egm-codebase-details, egm-zoom-out,
                         egm-comprehension, egm-implementation-readiness, egm-structural]
   |  彙整、去重
   v
 concepts_brief.md      (工作目錄；章節：Overview, Analysis, Goals vs. Non-Goals,
   |                     Alternatives Weighed, Key Decisions & Staging)
   |  /egm-draft：Overview/Goals -> Technical Plan -> Alternatives -> Detailed Implementation
   |             每節寫完都停下來等人核准（Section Approval Gate）
   v
 design_draft.md        (工作目錄)
   |  定稿前：對照 concepts_brief.md 找矛盾，有矛盾就停下等人決定
   |  選存放目錄（預設偵測到的 docs/designs/）；若有 SITEMAP.md 就登錄
   v
 docs/designs/<FEATURE>.md
   |  /egm-review <路徑>：Stage 5 -> 6 -> 7 -> 8 -> 9（見第 4 節）
   |  /egm-resolve：逐條處理發現
   v
 人工 PR 審查 -> 核准合併 -> 依設計文件實作 -> 定期 /egm-drift-report
```

各步驟的交付物與出口條件（皆出自上游對應的 `SKILL.md`）：

| 步驟 | 技能 | 輸入 | 交付物 | 可前進的條件 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `egm-brainstorm` | 人的初步想法 | `concepts_brief.md`（寫檔，不貼在聊天裡） | 人在 Readiness Gate 選「Review with Goldfishes」後才會派金魚；簡報經人確認後選下一步（發 RFC、進 `egm-draft`、續修、結束） |
| 2 | `egm-draft` | `concepts_brief.md`（優先順序 1）、否則 `discussion_summary.md`、否則互動詢問 | `design_draft.md` | 每一節（Overview & Goals、Technical Plan、Alternatives Considered、Detailed Implementation）人都選「Approve」才寫下一節 |
| 3 | `egm-draft` 定稿 | `design_draft.md` + 步驟 1 的簡報 | `<DESIGN_DIR>/<FEATURE>.md`（預設 `docs/designs/`） | 簡報與草稿的矛盾（簡報已決定、草稿改判）逐條由人裁決；沒有簡報則略過此檢查 |
| 4 | `egm-review` | 設計文件路徑、選填 `GoldfishContext`、選填 `Step`（`interactive`／`uninterrupted`／`feature_spec`／`implementation` 或單一階段 5–9） | 各階段報告（`zoom_out_report.md`、`comprehension_report.md`、`critic_report.md`、`intermediate_zoom_out_report.md`、`implementation_readiness_report.md`）；全程模式另有 `consolidated_review_report.md` | 人選擇處理的發現；每階段最多重審 1 次（manual 修改路徑）；Stage 之間依賴順序 5→6→7→8→9 |
| 5 | `egm-resolve` | 發現清單 | `goldfish_review_report.md`，標註 `CONTEST`／`ESCALATE`／`PROPOSE FIX`／`DECLINE` | 人回覆後才套用修改 |
| 6 | 人工審查 | 設計文件 PR | 核准 | 由你的團隊流程決定（上游不規定） |
| 7 | 實作與漂移檢查 | 已核准設計文件 | 程式碼；`{YYYY-MM-DD}_DRIFT_REPORT.md` | `egm-drift-report` 建議每週跑一次，差異由人決定改文件還是改程式 |

設計文件的段落骨架（上游 `skills/egm-draft/references/design_doc.md`）：Overview、The Problem、Goals、Non-Goals、Open Questions、Critical User Journeys (CUJs)、Technical Plan (Architecture)、Alternatives Considered、Non-Functional Requirements、Additional Resources、Future Improvements、Detailed Implementation Plan（含 Target Files to Create/Modify 與 Verification Plan）。可直接貼用的空白版在本手冊第 5.2 節。

## 4. 五階段金魚審查驗核清單

階段編號 5–9 沿用上游（前面的 1–4 是簡報與起草步驟的內部編號）。每一階段列出：派哪些審查員、套用哪份標準、審查範圍，以及你（人）收到報告後可以拿來驗核的清單。清單的每一項若有上游依據，標註來源檔；上游沒有的，標為「本 repo 補充」。

審查範圍：`FeatureRange` 是設計文件中「Detailed Implementation Plan」（或同義標題 `Implementation Plan`、`Work Breakdown`、`Implementation Steps`）之前的部分；`DetailedRange` 是該標題起到文末。找不到實作計畫時，`DetailedRange` 為 N/A，只做 Stage 5–8。

### Stage 5：Initial Zoom Out Review（第一次高空檢視）

- 審查員：`egm-zoom-out`；標準：`zoom-out-standard.md`；範圍：整份文件。
- [ ] 文件足以讓陌生讀者說出「要達成什麼、為什麼」。標準的 0 節寫明：若審查員判斷不出來，直接以「需要補充背景」判不通過。（`zoom-out-standard.md` §0）
- [ ] 解的是根因，不是症狀的局部補丁；與專案 `README.md`／`context.md` 的目標一致。（§1）
- [ ] 沒有為了假想的未來需求設計的抽象、設定、介面（YAGNI）；沒有在瓶頸被證實前就加快取、分片、非同步佇列。（§2）
- [ ] 資料經過的元件數最少；介面留有擴充空間但不先實作。（§2）
- [ ] 高階章節沒有掉到程式碼層級（輔助函式、迴圈變數）；新邏輯放在對的層。（§3）
- [ ] 提出新工具、模組、類別時，審查員已用程式碼搜尋確認沒有可重用的現成品。（`agents/zoom_out.md`：審查員必須搜尋）
- [ ] 沿用既有設計模式與標準函式庫，沒有自製輪子；點名的反模式（例如繞過標準認證、寫死部署設定）已排除。（§4）
- 本 repo 補充：此階段通過條件是「報告中沒有未處理的 Blocker」，上游沒有數值門檻。

### Stage 6：Comprehension Test（理解測試）

- 審查員：`egm-comprehension`，**直接派這一個，不經 synthesizer**，因為 synthesizer 的報告只留發現，而作者需要看到審查員的轉述（`egm-review` Subflow: Comprehension Test）；不套任何文件標準。範圍：`FeatureRange` 與 `DetailedRange`。
- [ ] 報告開頭有兩個標題「What this proposes」與「How the existing system works, per this document」，各 2–5 句。（`agents/comprehension.md`）
- [ ] 你拿這份轉述對照自己的本意：轉述錯了就是一條發現，要回頭改文件而不是反駁審查員。（`egm-resolve`：「Do not contest a comprehension gap」）
- [ ] 審查員讀不懂的任何一節都被列為 Blocker。（`agents/comprehension.md`）
- [ ] 專案、團隊、本設計特有的術語，在文件內定義或有連結；一般工程名詞不必定義。（同上：「Flag a term only when it is specific to this project」）
- [ ] 沒有「系統會自動處理」這類沒說明怎麼處理的句子；描述工作流程時沒有假設讀者已知未寫出的前置步驟。（同上 Audit Vectors）

### Stage 7：Critic Review（批判審查）

- 審查員：`egm-design`、`egm-structural`、`egm-style`（透過 `egm-review-loop`）；標準：`feature-spec-standard.md` 套用在 `egm-design` 與 `egm-structural`；範圍：`FeatureRange`。
- [ ] 有替代方案評估，且每個被否決的方案有具體理由（複雜度、成本、效能、擴充性）。只提單一路徑視為不通過。（`feature-spec-standard.md` The Alternatives Rule）
- [ ] 明寫風險與限制：失效模式、安全影響、規模上限、緩解方式。（同標準 Risks & Limits）
- [ ] 有 Problem Statement、Goals & Non-Goals、Proposed Architecture、Alternatives Considered、Risks & Mitigations。（同標準 Requirements；標準寫明這些是「Non-Exhaustive Examples」）
- [ ] 對外部系統能力、資料可得性、效能的斷言都有依據。（`agents/design_critic.md` Faulty Assumptions）
- [ ] 單點故障、擴充瓶頸、安全弱點有緩解。（同上 Unmitigated Risks）
- [ ] 標題層級沒有跳級、必要章節沒缺、表格與程式碼區塊語法完整、連結格式一致。（`agents/structural.md`）
- [ ] 沒有誇飾、行銷語、空泛詞、贅字、主觀評價。（`agents/style.md`）
- 本 repo 補充：CUJ 驗核。上游審查員不檢查 CUJ，若你的設計文件使用 CUJ 一節，請自行對照第 5.3 節。

### Stage 8：Intermediate Zoom Out Review（中期高空檢視）

- 審查員：`egm-zoom-out`；標準：`zoom-out-standard.md`；範圍：整份文件；輸入多帶 Stage 5 的報告路徑。
- [ ] 專注於 Stage 6、7 之後**新增或修改**的內容：修補有沒有讓設計變複雜、變囉嗦、掉進細節。（`egm-review` Subflow: Zoom Out Review：「focus on additions/mitigations from Comprehension and Critic stages」）
- [ ] （本 repo 補充）Stage 5 已解決的發現沒有被重新引入。
- 僅做「Feature spec only」預設流程時，在此階段結束。

### Stage 9：Implementation Readiness Test（實作就緒測試）

- 審查員：`egm-implementation-readiness`、`egm-codebase-details`、`egm-style`；標準：`implementation-readiness-standard.md` 套用在前兩者；範圍：`DetailedRange`。
- [ ] 零決策規則：實作者不需要自己選資料庫結構、API 路徑、相依套件、邊界情況處理方式。要選就是不通過。（`implementation-readiness-standard.md` The Zero-Decision Rule）
- [ ] 工作被切成多個階段，每一階段結束時程式碼庫都能建置、可測試。（同標準 Phasing & Checkpoints）
- [ ] 列出所有要新增、修改、刪除的檔案，每個檔案有「改什麼、為什麼」。（同標準 Target Scope；`egm-draft` Step 5 要求每個動到的檔案都要有）
- [ ] 每個檔案標明 `Create`／`Modify`／`Delete`。`egm-codebase-details` 規定：計畫中要新建的檔案不存在不是缺陷；沒標註才記一條 Major。
- [ ] 文件說「現在已存在」的檔案、函式、端點、資料表都真的存在；與程式碼矛盾者是 Blocker。（`agents/codebase_details.md` Contradicts the Code、Non-Existent References）
- [ ] 程式碼裡的寫死常數、環境變數、重試次數、例外處理分支，文件有寫。（同上 Unstated Assumptions、Undocumented Edge Cases）
- [ ] 有 Test Plan：happy path 與邊界案例。（同標準）
- [ ] 設計草稿中不含實作程式碼，只有偽碼、API、schema。（`egm-draft` Step 5：NO CODE）

### 4.1 發現的處理與收斂（上游規定）

`egm-review-loop` 的收斂規則：同一範圍同一問題已被反駁或記為接受的風險（settled），新審查員重提不重開；已套用修正的問題被再次提出，視為修正失敗而重開；一輪沒有未結案的 Blocker／Major 才算乾淨（Nit 不擋）；**連續兩輪乾淨**才算收斂；上限 5 輪；超過上限或出現反覆改來改去（churn）時停下問人。

## 5. CUJ 驅動設計

### 5.1 寫法

上游設計文件範本把 Critical User Journeys 定義為「這份設計支援的端到端使用者旅程」，每個 CUJ 必須含三項：

- Given：前置條件、起始狀態、環境設定。
- When：觸發動作或系統事件。
- Then：預期結果、驗證準則、事後狀態。

### 5.2 可直接貼用的空白設計文件骨架

下面是上游 `design_doc.md` 範本的繁中對照骨架（章節名稱保留上游英文，方便對照與審查員讀取）。貼到 `docs/designs/<FEATURE>.md`，把方括號填掉；填不出來的段落寫「無」並說明原因，不要留 TBD。

```markdown
# [功能名稱]

*   **Author:** [作者]
*   **Status:** [Draft | Proposed | In Review | Approved]
*   **Date:** [YYYY-MM-DD]

## Overview

[2–4 句：這個功能是什麼、解什麼問題、在系統中的位置。]

## The Problem

[現在發生什麼事、誰受影響、為什麼現有做法不夠。]

## Goals

*   [可驗證的目標 1]

## Non-Goals

*   [明確排除的範圍 1]

## Open Questions

*   **[問題]**：[未解的技術未知數；解決後刪除]

## Critical User Journeys (CUJs)

### CUJ 1: [旅程名稱]

*   **Given**: [前置條件與起始狀態]
*   **When**: [觸發動作或事件]
*   **Then**: [可觀察的結果與驗證方式]

## Technical Plan (Architecture)

[架構選擇、資料結構、資料流、元件互動；附 ASCII 或 Mermaid 圖。]

## Alternatives Considered

### Alternative A: [方案名稱]

*   **Pros**: [優點]
*   **Cons**: [缺點]
*   **Reason for Rejection**: [為何不選]

## Non-Functional Requirements

[安全與隱私、效能、上線與回滾；沒有關鍵風險就寫「無」。]

## Detailed Implementation Plan

### Target Files to Create/Modify

#### 1. `[檔案路徑]` ([Create | Modify | Delete])

*   **Type / Scope**: [檔案類型與範圍]
*   **Proposed Changes**: [新 API／函式簽章／行為；不寫實作程式碼]

### Verification Plan

*   **Build**: [指令]
*   **Unit Tests**: [指令]
*   **E2E/Integration**: [指令或手動步驟]
```

### 5.3 CUJ 的自我檢查清單（本 repo 補充，上游審查員不檢查）

- [ ] 每個 CUJ 的 Given／When／Then 三項都有，且 Then 是**可觀察**的結果（輸出、狀態、錯誤訊息），不是「系統正常運作」。
- [ ] 至少一個 CUJ 涵蓋失敗路徑（例如投遞失敗、重複事件），不只快樂路徑。
- [ ] 每個 Goal 至少被一個 CUJ 的 Then 對應到；沒有對應的 Goal 要嘛補 CUJ，要嘛改成 Non-Goal。
- [ ] `Detailed Implementation Plan` 的 `Verification Plan` 中，每個 CUJ 至少對應一項測試或手動步驟。
- 反例（不合格）：`Given: 使用者登入。When: 使用者使用功能。Then: 系統正常運作。` 三項都無法檢驗。
- 正例：`Given: 訂閱者 A 的 webhook 端點會回 500，且事件 E 已排入佇列。When: 系統第一次投遞 E。Then: 投遞紀錄標為 failed、依文件第 X 節的重試表排入下一次重試，且重複收到相同事件 ID 時訂閱者端不重複處理。`

## 6. 導入本 repo／其他專案時的建議（本 repo 的取捨，非上游規定）

1. 設計先行閘門：筆記提議「大型非平凡功能，Spec 審查綠燈後才編碼」。上游沒有工具層的強制，只在 EGM 設計流程進行中禁止 agent 寫正式實作檔。若要在你的專案強制，需要自己的機制（例如 PR 範本要求附上 Stage 5–9 報告）；本手冊不提供這種機制。
2. 零上下文審查要有實際的審查員：本 repo 的做法是由**未參與實作的審查員實際跑過產出、提出問題，修正後再複審**。這是本 repo 的作法，不是上游規定；它與上游的共同點是「審查者不與起草者共用上下文」。筆記的 `T-20261102-05` 因此標為不做：用腳本「模擬」零記憶審查驗不到真實行為，只會產生一個檢查關鍵字的假裁判（參見 [`docs/external-judge-audit.md`](external-judge-audit.md) 第 4 節的「已知限制」）。
3. 驗核手段的限度：本手冊第 4 節的清單是給人對照審查報告用的，不是自動判定程式。報告是否可信，仍取決於審查員真的有讀檔並回報（見 2.2 的第 3 點）。
4. 嚴重度門檻：上游只定義 Blocker／Major／Nit，沒有數值門檻。你的專案要訂「Blocker 必須清零才能進 PR」之類的規則，那是自訂取捨。

## 7. 已知限制與未驗證項目

- 本手冊沒有安裝或執行 EGM 外掛，所有行為描述來自上游原始檔在查證 commit 的文字；實際執行時 agent 的表現未驗證。
- Medium 原文與 <https://egm.dev> 未開啟，其中論點未驗證。
- Antigravity、Codex 的安裝指令與限制見上游 `docs/harnesses.md`、`docs/codex.md`；本手冊只確認了它們存在，沒有逐字查核其版本需求。上游 `docs/harnesses.md` 寫明獨立版 Antigravity IDE 目前不支援 Goldfish 審查（缺少 `invoke_subagent` 工具）；Codex 沒有具名角色，由一般 subagent 讀角色檔。
- 上游專案仍在更新（查證當日最新 commit 為 2026-10-30，repo 最後 push 為 2026-11-01）；階段名稱與檔案路徑可能變動，引用前請重新對照最新版。
- 第 4 節各階段清單是我從上游標準與角色提示詞逐條整理的，不是上游的原文清單；標準檔自己寫明其要求為「非窮盡的範例」。

## 來源

查證日：2026-11-02。除另註明外，皆為上游 repo 在 commit `403d8881d62022490637d740657b33f01e321ea8` 的檔案。

- 上游 repo 與擁有者、授權、星數、最後 push：GitHub API `repos/google/elephant-goldfish-model`（<https://github.com/google/elephant-goldfish-model>）
- `README.md`：角色表、技能表、安裝指令、免責聲明
- `docs/getting_started.md`：核心流程、不具強制性的說明、每週漂移檢查建議、專案目錄結構
- `docs/designs/architecture.md`：三層元件模型、五階段（Step 5–9）流程、Artifact-First 協定、作者
- `skills/egm-brainstorm/SKILL.md`、`skills/egm-draft/SKILL.md`、`skills/egm-draft/references/design_doc.md`、`skills/egm-review/SKILL.md`、`skills/egm-review-loop/SKILL.md`、`skills/egm-resolve/SKILL.md`、`skills/egm-drift-report/SKILL.md`
- `agents/*.md`（審查員角色提示詞）、`.claude-plugin/agents/zoom_out.md` 與 `.claude-plugin/plugin.json`（Claude Code 轉接設定）
- `resources/document_standards/{zoom-out,feature-spec,implementation-readiness}-standard.md`、`resources/execution_instructions.md`
- `docs/claude.md`（Claude Code 版本與隔離要求）、`docs/harnesses.md`（各平台 subagent 工具與限制）
