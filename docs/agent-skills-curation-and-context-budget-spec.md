# Agent Skills 評選矩陣與上下文預算工程規範

> 任務：`T-20261026-17`｜來源筆記：[`notes/2026-10-26-github-trending-agent-skills-benchmark.md`](../notes/2026-10-26-github-trending-agent-skills-benchmark.md)（原文為 Threads 貼文，作者「一股GoodJob」；以下凡寫「作者宣稱」者未獨立重現）
> 配套工具：[`tools/audit_skills_context_budget.py`](../tools/audit_skills_context_budget.py)｜配套範本：[`templates/lightweight-skill-template.md`](../templates/lightweight-skill-template.md)
> 查證日期：2026-10-26。動態數字（Star 數、官方限制）都標了出處與日期，之後可能變動。

---

## 1. 這份規範回答什麼

裝很多 Agent Skill 會不會拖慢、變笨？答案取決於**哪一部分成本是常駐、哪一部分是觸發才付**。本文：

1. 說清楚成本怎麼算（第 2、3 節）。
2. 定義三層治理：什麼技能該常駐、該綁專案、該按需載入（第 4 節）。
3. 給出四大熱門體系的取捨矩陣（第 5 節）。
4. 給出 YAML 觸發條件寫法與指令衝突檢查清單（第 6、7 節）。
5. 用工具稽核（第 8 節）。

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

筆記作者說「裝數十個技能，還沒開始處理問題就燒掉上萬 tokens」。就官方模型而言，**只有 name+description 常駐**，所以該說法在「本文很長」的情況下不成立；成立的情形是**技能數量很多、description 很長**（見第 3 節實測：96 個技能估約 8,150 tokens）。

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

評分是定性判斷（高／中／低），依據：筆記作者的實測描述（作者宣稱）、官方概觀文件，以及 GitHub 倉庫資訊（Star 數為 2026-10-26 經 `gh api` 讀取，會變動）。

| 體系 | 代表（來源） | 常駐成本 | 觸發精準度需求 | 衝突風險 | 適用層 | 取捨決策 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 工程紀律 | [obra/superpowers](https://github.com/obra/superpowers)（約 305k Star；`skills/` 下現有 15 個子技能，筆記稱 20+，以倉庫現況為準） | 中：技能多、每個 description 都常駐 | 高：流程技能若誤觸發會把小任務過度工程化 | 高：與「輸出要簡短」「直接改」之類規則互斥 | 第 3 層；只萃取單一原子（除錯、TDD、驗證）進第 1 層規則 | **萃取不整包裝**：保留「先查證再宣稱完成」類硬閘門，其餘按需 |
| 元技能 | `skill-creator`（見 [anthropics/skills](https://github.com/anthropics/skills)，約 184k Star）、技能搜尋工具如 [vercel-labs/skills](https://github.com/vercel-labs/skills)（約 37k Star） | 低 | 中 | 低；但會引入外部技能 | 第 3 層 | **採用建立工具；外部技能先走 [`skill-vetting`](#9-引入第三方技能的前置檢查) 檢查**，不直接安裝 |
| 前端規範 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)（約 33k Star；筆記提到的 React 最佳實務屬此類，細節**未逐項查證**） | 低～中 | 高：只該在 React／Next 專案觸發 | 中：與專案既有 lint／風格規則重疊 | 第 2 層（只放前端專案） | **綁專案**，不放全域；非前端專案載入等於白佔 R_total |
| 文件工程 | Anthropic 預建 `pptx`／`xlsx`／`docx`／`pdf`（[官方概觀](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#available-skills)；官方註明預建文件技能**不在 Claude Code 內**，但在 API／claude.ai 可用） | 低 | 低：副檔名／格式很明確，容易寫觸發詞 | 低 | 第 3 層 | **按需**；相依外部函式庫，要先確認執行環境 |

不採納：把數十個異質技能打包的大型聚合倉庫整包安裝（筆記的決策，本文沿用；理由是 R_total 無法控制、衝突無法逐一審）。

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
- 注意力稀釋、指令互斥對遵從度的影響，筆記作者宣稱「顯著下降」，**本文未做對照實驗**，因此第 7 節是預防清單，不是效果量化。
- 第 5 節的前端規範體系細節（React 瀑布流規則等）未逐項查證。
