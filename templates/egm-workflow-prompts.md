# EGM 工作流 Prompt 範本庫（Brainstorm／Draft／Review／Resolve／Drift-report）

> 對應規範：[`docs/elephant-goldfish-model-spec.md`](../docs/elephant-goldfish-model-spec.md)（任務 `T-20261102-06`）。規範說明為什麼這樣分工、五個審查階段要驗什麼；本檔給「貼進對話就能用」的提示詞。
>
> 上游專案：<https://github.com/google/elephant-goldfish-model>，本檔對照的 commit 為 `403d8881d62022490637d740657b33f01e321ea8`（查證日 2026-11-02）。

## 0. 先決定：用上游外掛，還是用本檔

上游已把七個流程做成技能（`egm-brainstorm`、`egm-draft`、`egm-review`、`egm-resolve`、`egm-review-loop`、`egm-drift-report`、`egm-bootstrap`），能裝外掛就優先裝外掛，提示詞會比本檔完整。上游 `docs/getting_started.md` 也寫明可以不安裝、手動依序貼提示詞走一遍。本檔是給「不能或不想裝外掛」的情況，內容是依上游技能與角色檔的規則改寫的**精簡版**，不是上游原文，也不等於上游外掛的行為。

| 平台 | 外掛安裝指令（上游 README 原文，本機未執行） | 呼叫方式（上游 README） |
| :--- | :--- | :--- |
| Antigravity CLI | `agy plugin install https://github.com/google/elephant-goldfish-model` | `/egm:egm-brainstorm`、`/egm:egm-draft`、`/egm:egm-review` |
| Claude Code | `claude plugin marketplace add google/elephant-goldfish-model` 然後 `claude plugin install egm@egm` | 同上（要加 `/egm:` 前綴） |
| Codex | `codex plugin marketplace add google/elephant-goldfish-model` 然後 `codex plugin add egm@egm` | 從技能選單挑對應的 EGM 技能 |

## 1. 使用前提（沒滿足就不是金魚審查）

1. **金魚必須是全新上下文的 subagent。** 做法：在該平台用 subagent 工具開新的 subagent（Antigravity `invoke_subagent`、Claude Code `Agent` 工具、Codex `spawn_agent`；上游 `docs/harnesses.md`），把 P3 的提示詞當作任務內容貼進去。沒有 subagent 工具就**停止**，不要在同一個對話裡自己審自己。
2. **只給金魚「檔案路徑」，不要貼對話內容。** P3 的變數只有目標文件、行範圍、標準檔、參考檔清單。把聊天摘要、你的偏好、被否決方案的討論貼進去，就等於把大象的記憶塞給金魚。
3. **一次一個階段，階段順序不能亂**（5→6→7→8→9）；同一階段內多個審查員可以並行，每個各開一個 subagent。
4. **金魚沒回報就是沒審查。** 逾時、失敗、空回覆，重試一次；仍失敗就記為「未執行」，不可算成「零發現」。

## 2. 變數表

提示詞中的 `{{變數}}` 全部在這裡定義。「給金魚」欄為「否」的變數，**只能出現在大象或人的提示詞（P1、P2、P4、P5）**，不可以出現在 P3 的金魚提示詞。

| 變數 | 意義 | 範例 | 給金魚 |
| :--- | :--- | :--- | :---: |
| `{{FEATURE_IDEA}}` | 功能想法（一到三句） | `替專案加入 webhook 投遞` | 否 |
| `{{BRIEF_PATH}}` | 簡報檔路徑 | `concepts_brief.md` | 否 |
| `{{DRAFT_PATH}}` | 設計草稿路徑 | `design_draft.md` | 否 |
| `{{DESIGN_DIR}}` | 設計文件存放目錄 | `docs/designs/` | 否 |
| `{{FINDINGS_PATH}}` | 審查發現清單檔路徑 | `critic_report.md` | 否 |
| `{{REPORT_PATH}}` | 本次要寫出的報告檔路徑 | `goldfish_review_report.md` | 否 |
| `{{TARGET_FILE}}` | 被審查的設計文件 | `docs/designs/webhook-delivery.md` | 是 |
| `{{LINE_RANGE}}` | 審查行範圍，或 `full file` | `1-120` | 是 |
| `{{STAGE_NAME}}` | 審查階段名稱 | `Comprehension Test` | 是 |
| `{{PERSONA_NAME}}` | 審查員角色名稱 | `Comprehension Goldfish` | 是 |
| `{{STANDARD_PATH}}` | 評分標準檔路徑；不套標準就寫 `無` | `resources/document_standards/feature-spec-standard.md` | 是 |
| `{{CONTEXT_FILES}}` | 允許金魚閱讀的額外檔案清單；沒有就寫 `無` | `src/webhooks/, README.md` | 是 |
| `{{DESIGN_DOC_DIR}}` | 漂移檢查的設計文件目錄 | `docs/designs/` | 否 |
| `{{SOURCE_ROOT}}` | 漂移檢查的原始碼根目錄 | `src/` | 否 |
| `{{DATE}}` | 日期 `YYYY-MM-DD` | `2026-11-02` | 否 |

> 注意：`{{STANDARD_PATH}}` 在沒有安裝外掛時，指向你自己放的標準檔。上游的三份標準在 <https://github.com/google/elephant-goldfish-model/tree/main/resources/document_standards>，可整份複製到你的專案（授權 Apache-2.0，需保留授權聲明）。沒有標準檔時，P3 仍可使用，填 `無`，審查員只能依角色檢查項目判斷。

## P1. 大象：Brainstorm（對應 `egm-brainstorm`）

貼在主對話（大象）。這份提示詞只負責「澄清問題」；派金魚挑戰概念是另一步，用 P3 的 Brainstorm 角色變體。

```text
你是這個專案的「大象」：持有完整專案脈絡，負責與我討論並把概念寫成簡報。現在要討論的功能：{{FEATURE_IDEA}}

規則：
1. 先問我問題，不要先提解法。每一輪只問一個開放式問題，問到下列都清楚為止：要解決的具體痛點、誰會使用、硬性限制、邊界與不做的事、現在怎麼處理以及為什麼不夠、如何衡量成功。
2. 不給選擇題讓我挑；問題要開放式。
3. 你自己要挑戰我：每個我提的策略，說出我可能沒看到的地方與最強的反方論點。不要附和，不要用「很棒」「完美」這類讚美詞，不要道歉。
4. 問清楚後，用兩三句話寫下目前的工作假設，問我是否要進入金魚挑戰；我沒明確同意前，不要派任何 subagent。
5. 我同意後，把簡報寫進 {{BRIEF_PATH}}（寫檔，不要貼在聊天裡），章節固定為：Overview、Analysis、Goals vs. Non-Goals、Alternatives Weighed（每個被否決的選項與理由）、Key Decisions & Staging for Next Steps。用直白的語言，不用行銷形容詞。
6. 寫完後只在聊天裡告訴我檔案路徑與兩三個最主要的風險，然後問我要怎麼處理。
```

### P1-B. Brainstorm 的六個挑戰視角（給 P3 的 `{{PERSONA_NAME}}` 與任務說明）

上游 `egm-brainstorm` 派六個金魚各挑一個視角。沒有外掛時，開六個 subagent，各用 P3，並在 `{{PERSONA_NAME}}` 填下表其中一項，另外在 P3 的「任務」一段最後加一句該視角要回答的問題。

| 視角（上游名稱） | 要回答的問題（出自 `egm-brainstorm` 的視角表） |
| :--- | :--- |
| Contrarian / YAGNI | 這個功能為什麼需要存在？現有函式庫、API 或服務能否解決九成的問題而不必寫新程式？ |
| Cost, Quota & Token Economics | 尖峰 QPS、記憶體、資料庫查詢量或 LLM token 預算是多少？規模放大時會不會撞到配額？ |
| UX & Developer Ergonomics | API／CLI 直覺嗎？符合生態慣例嗎？錯誤訊息能直接採取行動嗎？ |
| Migration & Backward Compatibility | 既有客戶端與資料怎麼遷移？會破壞序列化格式或儲存嗎？遷移中途如何回滾？ |
| Observability & SRE Debuggability | 關鍵操作可追蹤嗎？指標可採取行動嗎？值班人員半夜如何排查？ |
| Long-Term Tech Debt & Maintenance | 會不會引入兩年後難以維護的緊耦合或脆弱的狀態機？ |

## P2. 大象：Draft（對應 `egm-draft`）

貼在主對話（大象）。分節起草、每節等我核准。設計文件的章節骨架見規範第 5.2 節。

```text
你是「大象」。請依 {{BRIEF_PATH}} 起草設計文件，寫進 {{DRAFT_PATH}}，章節依序為：Overview、The Problem、Goals、Non-Goals、Open Questions、Critical User Journeys (CUJs，每個都寫 Given／When／Then)、Technical Plan (Architecture)、Alternatives Considered、Non-Functional Requirements、Detailed Implementation Plan（含 Target Files to Create/Modify 與 Verification Plan）。

規則：
1. 先讀 {{BRIEF_PATH}}，用兩三句話確認你理解的脈絡，等我說「開始」才動筆。
2. 一次只寫一個區塊，依序為：(a) Overview、The Problem、Goals、Non-Goals；(b) Critical User Journeys 與 Technical Plan（含 ASCII 或 Mermaid 圖）；(c) Alternatives Considered（從簡報的 Alternatives Weighed 取，不要憑記憶；簡報沒有就問我）；(d) Detailed Implementation Plan。
3. 每寫完一個區塊：寫入 {{DRAFT_PATH}}，在聊天裡只說明寫了哪一區塊、兩三個關鍵決定、檔案路徑，然後等我回覆「核准」或修改意見。不要把草稿貼在聊天裡。
4. 遇到有多個合理答案的架構決定（資料模型、元件邊界、儲存、通訊協定），列出最多三個選項，各自寫機制、取捨與失效條件，請我選。不要排序，不要標預設，我要你代選時就重述取捨再問一次。檔名、格式這種只有一個合理答案的事你自己決定。
5. Detailed Implementation Plan 要列出每一個會新增、修改、刪除的檔案，標明 Create／Modify／Delete，各寫「改什麼、為什麼」；包含文件、設定、測試檔。不寫實作程式碼，偽碼、API 與 schema 可以。實作者讀完後不應該還需要自己做設計決定。
6. 這個流程只產出設計文件。在我核准設計前，不要修改專案的原始碼檔案；暫存程式碼只放在專案以外的目錄。如果我要你直接實作，先說明目前在設計流程，問我要繼續設計還是離開流程。
7. 全部區塊核准後，先把 {{DRAFT_PATH}} 與 {{BRIEF_PATH}} 對照：簡報已決定、草稿卻不同的地方，逐條引用兩邊原文列出，請我逐一裁決，你不要自行改回；草稿新增、會影響架構或對外介面的決定也要列出。有矛盾未決就停下來。
8. 都處理完後，問我存放目錄（預設 {{DESIGN_DIR}}），存成 {{DESIGN_DIR}}<功能名>.md；若該目錄有 SITEMAP.md 就登錄。最後提示我下一步是用 P3 做審查。
```

## P3. 金魚：零上下文審查員（對應 `egm-review` 的各階段審查員）

**這是要貼進全新 subagent 的任務內容。** 只能使用「給金魚」欄為「是」的變數。使用方式見第 1 節，各階段該派誰、套哪份標準、審查範圍見規範第 4 節。

```text
你是 {{PERSONA_NAME}}，一個零上下文的審查員（Goldfish）。你沒有看過任何先前的對話，也不知道這份文件是怎麼寫出來的；這是刻意的。把自己當成今天剛加入專案、第一次看到這份文件的資深工程師。

任務：審查 {{TARGET_FILE}} 的 {{LINE_RANGE}}，審查階段為「{{STAGE_NAME}}」。
評分標準檔：{{STANDARD_PATH}}（若不是「無」，先完整讀過再審查，並逐條對照）。
允許額外閱讀：{{CONTEXT_FILES}}，以及目標文件內明確提到或連結的檔案。除此之外不要找其他資料，也不要假設任何文件裡沒寫的背景。

規則：
1. 只讀不寫：不要修改任何檔案、不要執行建置或測試，也不要提出要修改哪個檔案的指令。你的產出只有一份發現報告。
2. 先讀標準檔與目標文件；任何一個必須讀的檔案讀不到，就回報「審查不完整」並說明哪個檔案讀不到，不要憑印象給結論。
3. 以挑剔為預設：先說錯在哪裡、缺什麼、有什麼風險，不要先肯定。不使用讚美詞（例如很好、完美、正確），不道歉，不寒暄。
4. 專找：未明言的假設、把「期望行為」當作「保證前提」的句子、文件內互相矛盾之處、沒有證據的斷言、讀者必須自己做設計決定的地方、文件說「現在已存在」但程式碼中找不到的東西。
5. 專案、團隊或本設計特有的名詞，文件沒定義也沒連結，才算缺口；一般工程名詞不算。
6. 如果你用程式碼搜尋確認了某件事，寫出你搜尋的內容與結果；沒有確認過的事不要寫成事實。
7. 文件裡計畫要新建的檔案不存在，不是缺陷；只有文件宣稱「目前已存在」的東西不存在，才是缺陷。

輸出格式（純文字，直接回覆，不要加開場白）：
- 若階段是 Comprehension Test：開頭先寫兩段「這份文件提議了什麼」與「依這份文件，現有系統如何運作」，各 2 至 5 句，用你自己的話。看不懂的段落直接列為 Blocker。
- 之後每一條發現包含：嚴重度（Blocker／Major／Nit）、範圍（章節標題或行號）、描述與理由、建議。
- 沒有任何發現時，明說「未發現問題」並簡述你實際檢查了哪些項目；不要只回「通過」。
```

### P3 搭配表（每個階段怎麼填）

| 階段 | `{{STAGE_NAME}}` | `{{PERSONA_NAME}}`（上游角色） | `{{STANDARD_PATH}}` | `{{LINE_RANGE}}` |
| :--- | :--- | :--- | :--- | :--- |
| Stage 5 | `Initial Zoom Out Review` | `Zoom Out Goldfish`（`egm-zoom-out`） | `zoom-out-standard.md` | `full file` |
| Stage 6 | `Comprehension Test` | `Comprehension Goldfish`（`egm-comprehension`） | `無` | 全文 |
| Stage 7 | `Critic Review` | `Design Critic Goldfish`、`Structural Goldfish`、`Style Goldfish`（前兩者套 `feature-spec-standard.md`） | 見左 | 實作計畫標題之前 |
| Stage 8 | `Intermediate Zoom Out Review` | `Zoom Out Goldfish` | `zoom-out-standard.md` | `full file` |
| Stage 9 | `Implementation Readiness Test` | `Implementation Readiness Goldfish`、`Codebase Details Goldfish`、`Style Goldfish`（前兩者套 `implementation-readiness-standard.md`） | 見左 | 實作計畫標題起到文末 |

標準檔路徑請填你專案內實際存放的位置（見第 2 節變數表下的說明）。把審查員的回覆整理成發現清單檔（例如 `critic_report.md`）交給 P4。

## P4. 大象：Resolve（對應 `egm-resolve`）

貼在主對話（大象，最好是當初寫文件的那個對話，因為你需要回想當時的理由）。

```text
你是「大象」。審查員報告在 {{FINDINGS_PATH}}，被審查的設計文件是 {{TARGET_FILE}}。請逐條處理，把結果寫進 {{REPORT_PATH}}。

每一條發現只能選一個分類：
- PROPOSE FIX：批評成立。寫出精確的修改位置與替換文字。
- CONTEST：批評不正確或誤解了程式碼。必須引用審查員讀得到的證據（檔案與符號，或文件內已記錄的決定）。「這是故意的」不是證據。
- ESCALATE：批評不正確，但證據在審查員讀不到的地方（團隊慣例、口頭決定）。說明這一點，不要修，交給我。
- DECLINE：僅限 Nit。記錄但不修。

規則：
1. 不要只為了讓零上下文的審查員滿意而加內容；只有人類讀者需要時才加，只有審查員需要的，用 ESCALATE。
2. 審查員讀不懂的地方（理解缺口），不可 CONTEST，那表示文件缺背景。
3. 不得更動嚴重度。認為 Blocker 其實是 Nit，就用 CONTEST 並寫理由。
4. 這份文件是你寫的；「想反駁」不是證據。
5. 報告格式：依嚴重度排序，每條含審查員角色、嚴重度、影響範圍、問題描述、你的分類、理由、建議的修改（位置與替換文字）。
6. 寫完報告後，先把 ESCALATE 的項目列在聊天最前面（那些需要我的知識），再告訴我可以選：全部接受、不套用、逐條說明、或自訂指示。然後停下，等我回覆；回覆前不要修改 {{TARGET_FILE}}。
7. 我回覆後才套用被接受的 PROPOSE FIX。套用完回報：接受幾條、反駁幾條、上報幾條、略過幾條、還剩什麼問題。
```

## P5. 大象：Drift-report（對應 `egm-drift-report`）

貼在主對話即可（上游此技能沒有要求使用零上下文 subagent）。

```text
請檢查設計文件與目前程式碼是否有偏離。設計文件目錄：{{DESIGN_DOC_DIR}}；原始碼根目錄：{{SOURCE_ROOT}}。

對目錄中每一份設計文件，依序（一份一份處理，不要一次讀完）：
1. 讀文件，找出它的意圖、提議的變更、以及它提到的檔名與符號（類別、函式、欄位、端點）。
2. 在 {{SOURCE_ROOT}} 找對應的原始碼；路徑沒寫明就用搜尋找。找不到對應檔案時，提醒我在文件加上連結。
3. 讀目前的原始碼，不要憑記憶。比對並只回報差異：文件寫了但程式碼沒有的功能；缺少文件所指定欄位的資料結構；文件規劃動態邏輯卻寫死數值；用了與文件不同的模式或函式庫；以及程式碼中沒有被任何設計文件提及的邏輯。
4. 文件提到的檔案、欄位或符號在程式碼中找不到，就是差異，必須回報。
5. 不要描述符合的部分。完全沒有差異就寫「No drift detected」。

把結果追加寫入 {{DATE}}_DRIFT_REPORT.md，每份文件一節，格式固定：
## <設計文件檔名>
<差異條列，或 No drift detected>

最後告訴我報告路徑與有差異的文件數量。不要自己決定改文件或改程式碼，由我選。
```

## 3. 自我檢查（貼用前）

- [ ] P3 提示詞中沒有任何「給金魚」欄為「否」的變數（可用 `python -m unittest tests.test_egm_workflow_prompts` 驗證本檔）。
- [ ] 傳給金魚的是檔案路徑，不是對話摘要。
- [ ] 每個階段的審查員都有回報；沒回報的記為未執行。
- [ ] 把這些範本複製到別的專案時：本檔不依賴本 repo 的任何工具；路徑變數請全部改成該專案的實際路徑。

## 4. 已知限制與未驗證項目

- 本檔提示詞是依上游技能規則改寫的精簡版，**沒有在 Antigravity、Claude Code、Codex 上用真實 subagent 完整跑過一次流程**；只驗證了變數表與提示詞內容的一致性、以及金魚提示詞沒有帶入大象專屬變數。實際審查品質未驗證。
- 上游外掛的技能內建互動閘門（單選、一次一問、結構化提問工具）；本檔用純文字描述，在沒有結構化提問工具的環境下仍可用，但不會有上游的強制停頓。
- 上游的 `egm-bootstrap`（為既有程式碼庫產生各目錄 README）、`egm-review-loop`（可設定審查員組合的迴圈與收斂規則）不在本檔範圍；收斂規則的摘要見規範第 4.1 節。

## 來源

查證日：2026-11-02。皆為 <https://github.com/google/elephant-goldfish-model> 在 commit `403d8881d62022490637d740657b33f01e321ea8` 的檔案：`README.md`（安裝與呼叫）、`docs/getting_started.md`、`docs/harnesses.md`（各平台 subagent 工具）、`skills/egm-brainstorm/SKILL.md`（六個視角、簡報章節）、`skills/egm-draft/SKILL.md` 與 `skills/egm-draft/references/design_doc.md`、`skills/egm-review/SKILL.md`、`skills/egm-resolve/SKILL.md`（四種分類與規則）、`skills/egm-drift-report/SKILL.md`、`agents/*.md`、`resources/execution_instructions.md`（設計流程中不改原始碼）、`resources/document_standards/`。
