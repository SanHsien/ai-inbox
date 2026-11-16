# Agent Skills 評選矩陣與上下文預算工程規範

> 任務：`T-20261026-17`｜來源筆記：[`notes/2026-10-26-github-trending-agent-skills-benchmark.md`](../notes/2026-10-26-github-trending-agent-skills-benchmark.md)（原文為 Threads 貼文，作者「一股GoodJob」）
> 配套工具：[`tools/audit_skills_context_budget.py`](../tools/audit_skills_context_budget.py)｜配套範本：[`templates/lightweight-skill-template.md`](../templates/lightweight-skill-template.md)
> 查證日期：2026-10-26（第 1～10 節）、2026-11-17（第 11、12 節）。動態數字（Star 數、官方限制）都標了出處與日期，之後可能變動。
> **2026-11-16 更正（`T-20261026-36`）**：第 5 節的四大體系（工程紀律、元技能、前端規範、文件工程）是原筆記自己對熱門技能生態的分類整理，**不是貼文實測的對象**。原筆記沒讀留言；貼文作者把實測結果寫在留言裡，測的是 `garrytan/gbrain`、`mattpocock/skills` 的 grill-me、`garrytan/gstack`、`VoltAgent/awesome-agent-skills`。這四個的評估在第 11 節，作者的挑選方法改寫成第 12 節的查核清單。本文先前寫「筆記作者說」「作者宣稱」的三處（第 2、5、10 節）講的其實是原筆記的延伸論述，貼文沒有那些內容，已逐處改正。

---

## 1. 這份規範回答什麼

裝很多 Agent Skill 會不會拖慢、變笨？答案取決於**哪一部分成本是常駐、哪一部分是觸發才付**。本文：

1. 說清楚成本怎麼算（第 2、3 節）。
2. 定義三層治理：什麼技能該常駐、該綁專案、該按需載入（第 4 節）。
3. 給出四大熱門體系的取捨矩陣（第 5 節；這是分類整理，貼文實測的四包見第 11 節）。
4. 給出 YAML 觸發條件寫法與指令衝突檢查清單（第 6、7 節）。
5. 用工具稽核（第 8 節）。
6. 評估貼文實測的四包（第 11 節），並給出挑選第三方技能的查核清單（第 12 節）。

---

## 2. 成本模型：常駐的是 name／description，本文是觸發後才載入

官方文件（[Agent Skills 概觀](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)，2026-10-26 讀取）把技能內容分三層載入：

| 層級 | 何時進上下文 | 官方給的成本 | 內容 |
| :--- | :--- | :--- | :--- |
| Level 1 中繼資料 | 啟動時一律載入，放進 system prompt | 「約 100 tokens／每個技能」 | frontmatter 的 `name`、`description` |
| Level 2 指令 | 技能被觸發時才讀 | 「Under 5k tokens」 | `SKILL.md` 本文 |
| Level 3 資源 | 本文引用且被讀到才載入 | 讀到才算；腳本只有輸出進上下文 | 附屬 `.md`、腳本、資料 |

官方原話要點：「until a Skill is triggered, only its name and description occupy context」。所以：

- **裝很多技能的固定成本 = 所有技能的 name+description**，與本文多長無關。
- **本文肥大的代價在觸發當下**：一旦載入，每個 token 都和對話歷史、其他技能競爭注意力（[最佳實務](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：「once Claude loads it, every token competes with conversation history」）。
- 官方建議本文「under 500 lines」，超過就拆成同層級的附屬檔案（SKILL.md 直接連結，不要巢狀多層）。

原筆記寫「裝數十個技能，還沒開始處理問題就燒掉上萬 tokens」（這是原筆記的延伸論述，貼文沒有這句，也沒有量測數據）。就官方模型而言，**只有 name+description 常駐**，所以該說法在「本文很長」的情況下不成立；成立的情形是**技能數量很多、description 很長**（見第 3 節實測：96 個技能估約 8,150 tokens）。

```text
 啟動時（每個 session 都付）            觸發後才付                    讀到才付
┌───────────────────────────┐   ┌─────────────────────────┐   ┌───────────────────────┐
│ system prompt             │   │ SKILL.md 本文  (B_j)    │   │ 附屬檔案 (L_k)        │
│  + Σ name+description     │──▶│ 被 description 比對到   │──▶│ 腳本只付「輸出」      │
│    (R_total, 與本文無關)  │   │ 才讀進來                │   │ 沒讀到 = 0            │
└───────────────────────────┘   └─────────────────────────┘   └───────────────────────┘
        常駐層（要壓低）                 觸發層（要精簡）                資源層（可放大）
```

---

## 3. 預算計算公式

符號：`tok(x)` = 文字 x 的 token 數；技能集合 `S` = 已安裝（可被載入）的技能；`T ⊆ S` = 本次任務觸發的技能；`F` = 本次任務額外讀進來的附屬檔案集合。

```text
R_i      = tok(name_i) + tok(description_i)            # 單一技能常駐成本（Level 1）
R_total  = Σ_{i∈S} R_i  (+ 各 harness 的包裝格式，未量測，本文記 0)
B_j      = tok(SKILL.md 本文_j)                         # 單一技能觸發成本（Level 2）
L_k      = tok(附屬檔案_k)；腳本只計其輸出 tokens        # 資源成本（Level 3）

Cost_task = R_total + Σ_{j∈T} B_j + Σ_{k∈F} L_k        # 這次任務的技能相關上下文成本
```

### 3.1 token 怎麼估（工具採用的方法）

`tools/audit_skills_context_budget.py` 沒有 tokenizer，採啟發式：

```text
tok_est(text) = ceil( ASCII 字元數 / 4  +  非 ASCII 字元數 × 1.0 )
```

- ASCII 每 4 字元約 1 token：常見經驗值，**未經本 repo 對 Claude tokenizer 實測**。
- 非 ASCII（中日韓）每字保守估 1 token：同樣是保守估計，**未實測**。
- 用途是排序與抓異常肥大，不是計費。要精確值請用模型供應商的 token counting 功能。可用 `--chars-per-token`、`--cjk-tokens-per-char` 調參。
- 交叉驗證：官方說 Level 1 約 100 tokens／技能；下方實測平均 84.9，量級一致。

### 3.2 門檻值：哪些是官方的、哪些是本 repo 的政策

| 項目 | 數值 | 性質 | 出處 |
| :--- | :--- | :--- | :--- |
| `name` 格式 | ≤ 64 字元；只能小寫字母、數字、連字號；不含 XML 標籤；不含 `anthropic`、`claude` | 官方 | [概觀](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure) |
| `description` | 非空；≤ 1,024 字元；不含 XML 標籤；要寫「做什麼」與「何時用」 | 官方 | 同上 |
| 本文長度 | 建議 < 500 行 | 官方建議 | [最佳實務](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#token-budgets) |
| 單一技能本文 | ≤ **8,192 bytes**（8 KiB） | **本 repo 政策** | 承襲 [`notes/2026-10-23-claude-plugin-security-guidance.md`](../notes/2026-10-23-claude-plugin-security-guidance.md) 對自訂規則區塊的 8 KB 上限，在此擴及技能本文；不是 Anthropic 官方數字 |
| 單一技能常駐成本 | ≤ 150 tokens（估） | **本 repo 政策** | 官方 Level 1 約 100，留 50% 餘裕 |
| 技能庫常駐總量 | ≤ 4,000 tokens（估） | **本 repo 政策** | 約 40 個技能 × 100；超過就該分層搬出常駐層（第 4 節） |

8,192 bytes 換算（估）：純英文約 2,000 tokens；純中文每字 3 bytes，約 2,700 字，估約 2,700 tokens。兩者都低於官方「5k tokens」，是刻意收緊。

### 3.3 實測：對本機技能庫唯讀跑一次（`[Local Config]`，2026-10-26）

```text
python tools/audit_skills_context_budget.py "<本機 ~/.claude/skills>"
技能數 96｜缺 SKILL.md 的資料夾 2｜ERROR 12｜WARN 72
常駐成本（name+description）：26860 字元，估 8150 tokens（平均 84.9/技能；總預算 4000，已超標）
本文 bytes 合計 1751830｜超過本文預算 43 個｜超過單一常駐門檻 5 個
```

解讀：常駐總量約為政策上限的 2 倍；43／96 個技能本文超過 8 KiB（單一最大約 100 KB）。這是**估算值**，且只含 name+description，不含 harness 的包裝文字。ERROR 的類型是 name 含底線或保留字、缺 name 欄位、缺 SKILL.md 的資料夾，不代表這些技能在 Claude Code 一定載入失敗：官方規則寫在 API／claude.ai 文件，Claude Code 本機載入的寬鬆程度**未查證**。

---

## 4. 三層治理架構

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ 第 1 層 常駐全域硬閘門     放：全域 AGENTS.md／CLAUDE.md 規則 + 少數技能  │
│   條件：每個 session、每個專案都必須成立，違反就出事                     │
│   例：不洩漏金鑰、回報前真實執行、破壞性操作先授權                       │
│   預算：規則文字 ≤ 8 KiB；常駐技能 ≤ 5 個                               │
├──────────────────────────────────────────────────────────────────────────┤
│ 第 2 層 專案邊界技能       放：專案內 .claude/skills/（或 .agents/skills/）│
│   條件：只有這個專案用得到，離開專案就不該佔 R_total                     │
│   例：前端視覺驗證、三維重建、該專案的部署流程                           │
│   預算：每專案 ≤ 15 個；每個本文 ≤ 8 KiB                                 │
├──────────────────────────────────────────────────────────────────────────┤
│ 第 3 層 動態按需載入       放：個人庫 ~/.claude/skills/ 中低頻技能或外掛 │
│   條件：偶爾用；靠 description 命中才讀本文；大型資料放 Level 3 附屬檔   │
│   例：文件工程（docx/pdf/pptx/xlsx）、一次性遷移、研究流程               │
│   預算：每個 R_i ≤ 150 tokens；本文 ≤ 8 KiB；其餘拆附屬檔                │
└──────────────────────────────────────────────────────────────────────────┘
放置位置依據官方文件：Claude Code 技能放 ~/.claude/skills/（個人）或 .claude/skills/（專案）。
各層「≤ N 個」是本 repo 的起點建議值，沒有實測依據，請依第 3 節公式實算後調整。
```

判斷一個技能放哪一層（由上往下問，第一個「是」就定案）：

```text
違反它會造成資安／資料損失，而且與任務無關？ ── 是 ─▶ 第 1 層（寫成規則，不必做成技能）
只有某一個專案會用到？ ────────────────────── 是 ─▶ 第 2 層（放專案內）
其餘 ───────────────────────────────────────────────▶ 第 3 層，且 description 必須寫出觸發時機
```

---

## 5. 四大體系評選矩陣

評分是定性判斷（高／中／低），依據：官方概觀文件與 GitHub 倉庫資訊（Star 數為 2026-10-26 經 `gh api` 讀取，會變動）。**這四個體系不是貼文測的對象**（2026-11-16 更正）：先前這裡寫的「筆記作者的實測描述」並不存在，貼文沒有測這四類，下表沒有任何實測依據，只是依文件與倉庫內容做的分類判斷。貼文實測的四包見第 11 節。

| 體系 | 代表（來源） | 常駐成本 | 觸發精準度需求 | 衝突風險 | 適用層 | 取捨決策 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 工程紀律 | [obra/superpowers](https://github.com/obra/superpowers)（約 305k Star；`skills/` 下現有 15 個子技能，原筆記稱 20+，以倉庫現況為準） | 中：技能多、每個 description 都常駐 | 高：流程技能若誤觸發會把小任務過度工程化 | 高：與「輸出要簡短」「直接改」之類規則互斥 | 第 3 層；只萃取單一原子（除錯、TDD、驗證）進第 1 層規則 | **萃取不整包裝**：保留「先查證再宣稱完成」類硬閘門，其餘按需 |
| 元技能 | `skill-creator`（見 [anthropics/skills](https://github.com/anthropics/skills)，約 184k Star）、技能搜尋工具如 [vercel-labs/skills](https://github.com/vercel-labs/skills)（約 37k Star） | 低 | 中 | 低；但會引入外部技能 | 第 3 層 | **採用建立工具；外部技能先走 [`skill-vetting`](#9-引入第三方技能的前置檢查) 檢查**，不直接安裝 |
| 前端規範 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)（約 33k Star；原筆記提到的 React 最佳實務屬此類，細節**未逐項查證**） | 低～中 | 高：只該在 React／Next 專案觸發 | 中：與專案既有 lint／風格規則重疊 | 第 2 層（只放前端專案） | **綁專案**，不放全域；非前端專案載入等於白佔 R_total |
| 文件工程 | Anthropic 預建 `pptx`／`xlsx`／`docx`／`pdf`（[官方概觀](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#available-skills)；官方註明預建文件技能**不在 Claude Code 內**，但在 API／claude.ai 可用） | 低 | 低：副檔名／格式很明確，容易寫觸發詞 | 低 | 第 3 層 | **按需**；相依外部函式庫，要先確認執行環境 |

不採納：把數十個異質技能打包的大型聚合倉庫整包安裝（原筆記的決策，本文沿用；理由是 R_total 無法控制、衝突無法逐一審）。

---

## 6. YAML 觸發條件明確性

`description` 是 Claude 從（可能上百個）技能中挑技能的唯一依據（[最佳實務](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions)）。規則：

1. **兩句結構**：第一句寫「做什麼」，第二句寫「何時用」（`Use when …` 或「當…時使用」）。
2. **第三人稱**（官方明說因為 description 會被注入 system prompt，人稱不一致會影響技能發現）。不寫 "I can help you…"、"You can use this…"。
3. **寫出觸發詞與情境**：檔案類型、動詞、使用者會說的片語。反例：`Helps with documents`、`Processes data`。
4. **寫出邊界**（可選，視需要）：「不要用於 X」可降低誤觸發，但也佔常駐成本，只在確有混淆時加。
5. 長度：常駐成本門檻 150 tokens；超過先砍形容詞，不要砍觸發詞。
6. 一個技能一個職責；description 要同時涵蓋兩件不相干的事，就拆成兩個技能。

工具的觸發檢查**只是啟發式**（看有沒有 `Use when`／「當…時」之類的說法），輸出為 WARN 不是 ERROR；它無法判斷觸發詞是否真的精準。最終仍要用真實對話測：說出觸發情境，看技能有沒有被載入（官方建議至少建 3 個評測情境，並在 Haiku／Sonnet／Opus 都試）。

---

## 7. 指令衝突防範清單

新增或修改技能時逐項過：

- [ ] 同一件事（輸出長度、語言、格式、是否自動 commit）是否已有全域規則或其他技能定義？有就**引用而非重述**，或明確寫「以全域規則為準」。
- [ ] 是否用了絕對詞（「必須」「禁止」「永遠」）？只留給硬閘門；一般偏好寫成預設值加例外。
- [ ] 兩個技能可能同時觸發嗎（description 有重疊的觸發詞）？有就在其中一個寫出邊界，或合併。
- [ ] 技能是否要求修改全域設定、hooks、記憶或安裝其他技能？這類動作需另有授權說明，不可由技能暗中夾帶。
- [ ] 步驟是否依賴特定工具／套件？寫明前置條件（官方：API 環境無網路也不能裝套件；Claude Code 有完整網路）。
- [ ] 術語是否前後一致？官方建議整份技能只用一個詞表達同一概念。
- [ ] 有沒有寫會過期的資訊（日期、版本）？放到「舊做法」區塊。
- [ ] 路徑用正斜線；附屬檔案只從 SKILL.md 直接連結一層。
- [ ] 同時載入兩個最可能衝突的技能做一次演練，確認指令不互斥。

---

## 8. 稽核流程

```text
  新增／修改技能
        │
        ▼
  python tools/audit_skills_context_budget.py <skills 目錄> [--strict] [--json]
        │
        ├─ ERROR（缺欄位／格式錯／name 不合規／description > 1024）→ 必修，退出碼 1
        ├─ WARN：本文 > 8,192 bytes → 拆附屬檔案或刪內容
        ├─ WARN：單一常駐 > 150 tokens → 縮 description（保留觸發詞）
        ├─ WARN：總常駐 > 4,000 tokens → 依第 4 節把技能搬到第 2／3 層，或停用
        └─ WARN：看不出觸發時機 → 補「Use when／當…時」
```

工具行為：預設只掃第一層子目錄（每個子目錄一個 `SKILL.md`），`--recursive` 才遞迴；唯讀，不改檔；只用標準庫。`--strict` 讓 WARN 也回傳退出碼 1，可放進 CI。

---

## 9. 引入第三方技能的前置檢查

官方安全提醒（[概觀](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations)）：只使用自己寫的或來自可信來源的技能；審查所有附帶檔案；會抓外部 URL 的技能風險特別高。引入前：讀完 `SKILL.md` 與 `scripts/`；跑第 8 節稽核看成本；確認不與現有技能衝突（第 7 節）。

---

## 10. 限制與未查證

- token 估算是啟發式，未對 Claude tokenizer 實測。
- 8 KiB、150、4,000 是本 repo 政策值，不是官方數字；官方只給「約 100 tokens／技能」「本文 < 500 行」「Level 2 under 5k tokens」。
- Claude Code 實際注入 system prompt 的格式與是否有額外上限，**未查證**；本文只依官方概觀文件描述。
- 注意力稀釋、指令互斥對遵從度的影響，原筆記寫「顯著下降」（原筆記的延伸論述，貼文沒有這個說法，也沒有出處），**本文未做對照實驗**，因此第 7 節是預防清單，不是效果量化。
- 第 5 節的前端規範體系細節（React 瀑布流規則等）未逐項查證。
- 第 11 節是唯讀評估：只讀了四個 repo 的 README、檔案樹與少數 `SKILL.md`，沒有安裝、沒有執行、沒有跑 SkillSpector。貼文作者的實測結果（記得週報格式、問出 6 個問題等）未重現。
- 第 11 節的 `SKILL.md` 大小是 git 檔案樹回報的位元組數，含 frontmatter；第 3.2 節的 8,192 bytes 政策原本指本文，兩者差一個 frontmatter 的大小，在門檻邊緣的技能要用稽核工具重算。

---

## 11. 貼文實測的四包：唯讀評估（2026-11-17，`T-20261026-36`）

方法：只用 GitHub API 讀 repo 資訊、檔案樹與 README／`SKILL.md` 原文。**沒有 clone、沒有安裝、沒有執行任何安裝腳本**。星數、授權、最後推送時間來自 `gh api repos/<owner>/<repo>`（2026-11-17 讀取）；`SKILL.md` 數量與大小來自 `gh api repos/<owner>/<repo>/git/trees/<預設分支>?recursive=1`（四個都回報 `truncated: false`）。「貼文作者實測」的說法轉述自作者留言（見來源筆記第 0 節），未重現。

### 11.1 基本資料

| 貼文測的對象 | Repo | 星數 | 授權 | 最後推送 | 它實際是什麼 |
| :--- | :--- | ---: | :--- | :--- | :--- |
| GBrain | [`garrytan/gbrain`](https://github.com/garrytan/gbrain) | 33,153 | MIT | 2026-11-16 | 不是單一技能。是一套記憶系統：`gbrain` CLI、本機資料庫（PGLite 或 Postgres）、MCP 伺服器、hooks，外加一批技能 |
| grill-me | [`mattpocock/skills`](https://github.com/mattpocock/skills) 的 `skills/productivity/grill-me` | 325,929（整個 repo） | MIT | 2026-11-13 | 一個只能由使用者叫用的技能，本文只有一行：轉呼叫同 repo 的 `grilling` 技能 |
| GStack | [`garrytan/gstack`](https://github.com/garrytan/gstack) | 141,806 | MIT | 2026-11-16 | 一整套開發流程技能（`/office-hours`、`/plan-ceo-review`、`/review`、`/ship`、`/qa` 等），附安裝程式、hooks、內建瀏覽器與自動更新檢查 |
| Awesome Agent Skills | [`VoltAgent/awesome-agent-skills`](https://github.com/VoltAgent/awesome-agent-skills) | 37,246 | MIT | 2026-11-15 | 不是技能包。是一份連結目錄：repo 只有 4 個檔案，沒有任何 `SKILL.md` |

貼文作者對這四個的實測情境（作者宣稱，未重現）：GBrain 交代週報格式後開新對話仍記得；grill-me 對一個活動計畫一次問出 6 個漏洞並附建議答案；GStack 丟 App 點子先追問需求證據；Awesome Agent Skills 是目錄，作者提醒不要看到就裝。

### 11.2 大小、資料讀寫與重疊

| 對象 | `SKILL.md` 大小（對照 8,192 bytes 政策） | 會讀寫哪些資料（依 README） | 與本機已裝技能的重疊 | 判斷 |
| :--- | :--- | :--- | :--- | :--- |
| GBrain | repo 內共 256 個 `SKILL.md`（含 `plugin/`、`plugin-variants/` 的重複副本）；中位數 8,540 bytes，最大 31,661 bytes（`skills/skillify`），134 個超過 8,192 | `gbrain setup claude-code` 會設定 MCP、hooks，並在 Agent 的指令檔（`~/.claude/CLAUDE.md` 或 Codex 對應檔）寫入一段「先查記憶庫」的指示；README 說會先顯示要寫什麼，可用 `--dry-run` 預覽、`--remove` 復原。讀你指定的 Markdown 資料夾並建索引。預設不需 API key（關鍵字搜尋）；設定了雲端 embedding／rerank／抽取服務後，文字會送到那些服務。另有付費託管版，安裝指令是把遠端腳本直接接給 shell 執行 | 本機沒有裝。功能與現有的記憶檔＋本機 Markdown 搜尋重疊（都是「跨 session 記住偏好與決策」） | **不裝**。它會改全域指令檔與 hooks，屬於要先授權的變更；功能與現有記憶機制重疊。託管版的安裝方式違反「不把遠端腳本直接接給 shell」的規則。可參考的只有「每個新 session 先查記憶」這個做法 |
| grill-me | `grill-me` 157 bytes；它轉呼叫的 `grilling` 2,077 bytes。兩個都遠低於 8,192。整個 repo 39 個 `SKILL.md`，中位數 3,629，最大 12,594，5 個超過 | 不讀寫檔案、沒有腳本、沒有網路呼叫。`grilling` 的本文要求：把待決定事項排成樹狀，每一輪把目前能問的問題全部問完、每題附建議答案；查得到的事實由 Agent 自己查（派子 Agent），不問使用者；使用者確認前不動手 | 本機沒有 `grill-me`。部分重疊：`mindmap-confirm`（動手前對齊）、`plan-ceo-review`（挑戰前提）；但「一輪問完所有可問的問題並附建議答案」這個做法本機沒有對應技能 | **四個裡唯一合乎本文政策的**：小、單一職責、`grill-me` 設了 `disable-model-invocation: true`（只能手動叫用，不會誤觸發）。要用的話只取 `grill-me` 與 `grilling` 兩個，不整包裝；照第 12 節查核後再決定 |
| GStack | 71 個 `SKILL.md`；中位數 21,751 bytes，最大 85,181 bytes（`design-review`）；`office-hours`（貼文測的那個）43,885 bytes。**63／71 個超過 8,192** | 安裝方式是 clone 到 `~/.claude/skills/gstack` 後跑 `./setup`，並要求在 `CLAUDE.md` 加一段指示。README 自述：使用統計預設關閉、問一次；**更新檢查預設開啟**（每個 session 開始時向 GitHub 查版本）；「外部審查」預設開啟，會把程式碼送給 Codex 或 Claude Code（用你自己的登入）；對外傳送會留下可查的紀錄。另有 `/setup-browser-cookies` 會把瀏覽器 Cookie 複製到它內建的瀏覽器 | **已在用**：本機有 23 個技能的 description 標了 `(gstack)`（如 `plan-ceo-review`、`ship`、`review`、`qa`、`autoplan`）。本機沒有 `office-hours`。本機的 `plan-ceo-review` 103,537 bytes、`ship` 108,246 bytes，比上游現行版（60,600、61,438）更大 | **維持現狀，不整包重裝**。已裝的部分早就超過 8 KiB 政策（第 3.3 節的 43 個超標裡有它們），是觸發後才付的成本，但單次觸發很貴。上游版本與本機副本已有差異，未逐一比對。`/setup-browser-cookies` 與「不讀瀏覽器 Cookie」的規則衝突，不用。要補 `office-hours` 的話，先比對它與 `plan-ceo-review` 的重疊 |
| Awesome Agent Skills | 沒有 `SKILL.md`。`README.md` 247,701 bytes，徽章寫「1497+」個技能 | 目錄本身不讀寫任何資料；風險在它連出去的每一個技能。README 的 Security Notice 自己寫明：清單是挑選過的、**沒有稽核過**，原作者隨時可能改內容，安裝前要自己審查 | 不適用 | **只當搜尋入口**，不當推薦清單。從這裡找到的每個候選都要個別走第 12 節。與貼文作者「不要看到就裝」的提醒一致 |

### 11.3 對照本文的政策，這四包說明什麼

```text
            符合 8 KiB 政策？   會改全域設定／hooks？       結論
GBrain            否（半數超標）         會                        不裝
grill-me          是                     不會                      可個別評估後採用
GStack            否（63/71 超標）       會（安裝程式＋更新檢查）   已在用的留著，不再擴大
Awesome 清單      不適用（不是技能）     不會                      只當搜尋入口
```

- 貼文說的「4 包」性質差很多：一個記憶系統、一個 157 bytes 的技能、一套 71 個技能的流程、一份目錄。拿「裝了幾包」來比沒有意義，要比的是各自的常駐成本、觸發成本與它動到哪些設定。
- 貼文的重點不是「這四包好不好」，而是作者在留言寫的挑選方法：先講清楚需求、不只看星數、先做安全檢查、確認前不安裝。這部分整理成第 12 節。
- 星數與大小無關的例子就在這四個裡：星數最高的 `mattpocock/skills` 剛好技能最小；星數第二的 GStack 幾乎每個技能都超過本文的大小政策。

---

## 12. 挑選第三方技能的查核清單（改寫自貼文作者的提示詞）

貼文作者在留言附了一段找技能的提示詞。原文不轉貼；它要求的事項是：用多種說法搜尋、列 3～5 個候選、逐一檢查更新狀況／說明／範例／issue 處理／讀取哪些資料／需要哪些權限／是否外傳資料、用表格比較後推薦一個、確認前不安裝不執行。以下改寫成本 repo 的查核清單，並標出每一項在現有 `skill-vetting` 流程（維護者本機的技能，四步：SkillSpector 掃描 → 人工審查 → 效用判斷 → 記錄結論；第 9 節的前置檢查即指它）裡有沒有對應。

### 12.1 清單

**A. 找之前**

- [ ] 用一兩句話寫下要解決的問題與「怎樣算解決」。寫不出來就先不找。
- [ ] 先查本機已有的技能、MCP、外掛能不能做（`skill-vetting` 的效用判斷已有）。
- [ ] 用至少三種不同說法搜尋（功能描述、使用情境、同類工具名稱）；目錄型清單（如第 11 節的 Awesome Agent Skills）只當搜尋入口。

**B. 列候選**

- [ ] 列 3～5 個候選；只找到 1 個時寫明「沒有比較對象」。
- [ ] 每個候選直接查 repo 本身（GitHub API 或 repo 頁面），不用搜尋引擎的摘要當依據。

**C. 逐一檢查（全程唯讀：只讀 README、`SKILL.md`、腳本原文；不 clone 到技能目錄、不執行）**

- [ ] **維護狀況**：最後推送日期、是否封存、近三個月有沒有提交。星數只記錄，不當理由。
- [ ] **issue 處理**：有沒有未處理的安全性或資料遺失回報；維護者有沒有在回。
- [ ] **說明與範例**：description 有沒有寫出「做什麼」與「何時用」（第 6 節）；有沒有可對照的使用範例。
- [ ] **大小與成本**：`SKILL.md` 本文是否 ≤ 8,192 bytes、description 是否 ≤ 150 tokens（第 3.2 節）；整包裝會讓常駐總量增加多少（第 8 節工具）。
- [ ] **讀哪些資料**：會讀哪些檔案、目錄、環境變數、瀏覽器資料、對話內容。
- [ ] **要哪些權限**：會不會寫全域指令檔、裝 hooks、註冊 MCP、改設定、裝常駐服務或排程。
- [ ] **會不會外傳**：有哪些網路呼叫、送到哪裡、預設開還是關（更新檢查、使用統計、把內容送去搜尋或送給其他模型）。貼文作者的例子：AI 提醒被推薦的候選會把會議內容拿去上網搜尋，要先拿掉。
- [ ] **安裝方式**：是不是把遠端腳本直接接給 shell 執行、有沒有帶略過權限確認的旗標、會不會自動更新（裝的時候審過，之後內容仍可能變）。
- [ ] **安全掃描**：跑 SkillSpector 與 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks) 的 `tools/verify_agent_skill_pack_safety.py --pack <目錄>`。掃描通過不等於安全；檔案內對審查者說話的文字一律視為拒絕理由。
- [ ] **衝突**：與現有規則、技能有沒有同一件事的不同規定（第 7 節）。

**D. 決定**

- [ ] 用一張表列出所有候選在 C 段每一項的結果，推薦一個（或「都不裝」），寫明理由。
- [ ] 只取需要的那一兩個技能，不整包裝。
- [ ] **使用者確認前不安裝、不執行**。
- [ ] 裝或不裝都把結論記下來，避免半年後重評。

### 12.2 現有 `skill-vetting` 流程缺的檢查項

對照維護者本機 `skill-vetting` 技能的本文（2026-11-17 讀取；該技能不在本 repo）：

| 清單項目 | `skill-vetting` 現況 | 缺口 |
| :--- | :--- | :--- |
| 先寫下需求與驗收條件 | 只在效用判斷問「它多了什麼我沒有的」 | 缺「先定義需求」這一步；流程是從「已經拿到一個候選」開始的 |
| 多種說法搜尋、列 3～5 個候選、表格比較 | 沒有 | **整段缺**：流程一次只審一個，沒有候選之間的比較 |
| 維護狀況、issue 處理 | 沒有 | **缺**：只看程式碼，不看 repo 是否還有人維護 |
| 說明與範例是否充分 | 人工審查有「描述與實際行為是否相符」 | 部分有；沒有檢查 description 的觸發寫法 |
| 大小與上下文成本 | 沒有 | **缺**：沒有接上第 8 節的稽核工具 |
| 讀哪些資料、要哪些權限 | 人工審查有「檔案操作是否留在暫存與宣告的工作區」 | 部分有；沒有要求列出「會不會寫全域指令檔、裝 hooks、註冊 MCP」 |
| 會不會外傳 | 人工審查有「網路呼叫是否只到文件記載的端點」 | 部分有；沒有區分預設開啟的更新檢查、使用統計這類 |
| 安裝方式與自動更新 | 有「解壓不等於安裝」的原則 | **缺**：沒有檢查安裝後會不會自動更新 |
| 安全掃描、提示詞注入 | 有，比貼文作者的做法嚴格 | 無 |
| 確認前不安裝 | 有（決定之前不安裝） | 無 |
| 記錄結論 | 有 | 無 |

結論：`skill-vetting` 在「這一個安不安全」做得比貼文完整；貼文的方法補的是前段（先定義需求、找多個候選比較）與 repo 健康度（維護狀況、issue）。本文只列出缺口，**沒有修改 `skill-vetting` 技能本身**；要補進去需另開任務。
