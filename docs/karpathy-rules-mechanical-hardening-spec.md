# Karpathy 四原則工程加固指引：從 Prompt 到硬閘門

> 對應任務：`T-20261028-01`（筆記：`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`）
> 查證日期：2026-11-02。本文每個外部事實都標了來源（見文末「來源」）；查不到的標「未驗證」。
> 讀完能做的事：(1) 說清楚四原則是誰寫的、原文是什麼；(2) 知道每一條原則在本 repo 有哪個機械檢查、能抓什麼、抓不到什麼；(3) 在 Claude Code、Codex、Antigravity 共用同一份 `AGENTS.md` 加同一組檢查腳本。

---

## 1. 先釐清出處：哪些是 Karpathy 說的，哪些是後人整理的

「Karpathy 四大原則」這個說法把兩件事混在一起。查證結果：

```text
2026-01-26  Karpathy 在 X 發一篇長文（"A few random notes from claude coding..."）
            │  只描述「模型常犯的錯」與「怎麼用才有槓桿」，沒有列出四條規則
            ▼
2026-01-27  forrestchang 建立 andrej-karpathy-skills repo，
            │  第一個 commit 8462496 加入 CLAUDE.md 與 README.md
            ▼
            四條規則、標題與口號（"Think Before Coding" 等）是這個 repo 的作者整理的
            README 自己寫的是 "derived from Andrej Karpathy's observations"（衍生自），
            不是 Karpathy 本人撰寫或背書
```

### 1.1 Karpathy 本人說的（原文，來自 2026-01-26 的貼文）

下列引文是英文原文節錄，以貼文內容為準：

| 主題 | 原文（節錄） | 後人整理成 |
| :--- | :--- | :--- |
| 盲目假設 | "the models make wrong assumptions on your behalf and just run along with them without checking. They also don't manage their confusion, they don't seek clarifications, they don't surface inconsistencies, they don't present tradeoffs, they don't push back when they should" | 原則 1 Think Before Coding |
| 過度複雜 | "They also really like to overcomplicate code and APIs, they bloat abstractions, they don't clean up dead code after themselves" 以及 "implement an inefficient, bloated, brittle construction over 1000 lines of code ... cut it down to 100 lines" | 原則 2 Simplicity First |
| 順手改動 | "They still sometimes change/remove comments and code they don't like or don't sufficiently understand as side effects, even if it is orthogonal to the task at hand" | 原則 3 Surgical Changes |
| 用成功標準驅動 | "Don't tell it what to do, give it success criteria and watch it go. Get it to write tests first and then pass them." 以及 "Change your approach from imperative to declarative" | 原則 4 Goal-Driven Execution |

另有一句對本文最關鍵：Karpathy 寫到這些問題在他嘗試用 `CLAUDE.md` 的簡單指令修正後仍然發生（原文："All of this happens despite a few simple attempts to fix it via instructions in CLAUDE . md"）。也就是說，**連提出觀察的人自己都說，純文字指令擋不住**。這正是本文主張要加機械閘門的依據，而不是推論。

### 1.2 後人整理的（forrestchang 的 `CLAUDE.md`）

四個標題、每條的粗體口號、條列規則、"The test: Every changed line should trace directly to the user's request." 都出自 `forrestchang/andrej-karpathy-skills`（現在 GitHub 網址已轉到 `multica-ai/andrej-karpathy-skills`）。查證時的 `CLAUDE.md` 是 HEAD `2c606141936f1eeef17fa3043a72095b4765b9c2` 上的版本（blob `daced9bd64f25908ebedeb4701fb406985dc8366`）。

### 1.3 筆記裡說法與查證結果不一致之處

| 筆記的說法 | 查證結果 |
| :--- | :--- |
| 第四條叫 "Goal-Driven Verification" | 原 repo 叫 **Goal-Driven Execution**，口號是 "Define success criteria. Loop until verified." 本文沿用原名，需要指本 repo 的檢查時才說「驗證」。 |
| Karpathy 指出四種毒性偏差，第四種是「自欺欺人：程式剛生出來就聲稱已修好」 | Karpathy 貼文沒有這一項。貼文談的是假設、複雜化、順手改動；「測試先行、給成功標準」是他講的槓桿，不是在講模型謊報完成。「謊報完成」是工程上真實存在的風險，但不應掛 Karpathy 的名。 |
| 上下文超過 50K／100K token 後會遺忘 Surgical Changes | **未驗證**。找不到一手數據。本文不引用這兩個數字。 |
| 來源是 Threads 貼文（@easyanythinghk） | **未驗證**。本次沒有讀到該貼文。Karpathy 原文與 forrestchang repo 已直接查證，本文不依賴 Threads 貼文。 |
| 「社群爆紅」 | 2026-11-02 以 GitHub API 查到該 repo 約 22.8 萬 star，事實成立；但 star 數不代表規則有效，本文沒有找到任何對照實驗。 |

> 這份文件的立場：四原則是好的**檢查清單**（出處是 Karpathy 的觀察），但它們是寫給人與模型讀的文字。要讓它們在長對話後仍然成立，需要機械檢查；而機械檢查只能涵蓋其中可量測的部分。

---

## 2. 四原則架構拓撲

```text
              ┌────────────── 任務進來 ──────────────┐
              ▼                                      │
   ① Think Before Coding     動手前：宣告路由、列出歧義與取捨
              │ 通過才可改檔
              ▼
   ② Simplicity First        改動中：最小實作、不加沒要求的東西
              │
              ▼
   ③ Surgical Changes        改動後：每個變更行都追溯到需求
              │  audit_surgical_diff.py（本 repo）
              ▼
   ④ Goal-Driven Execution   收尾：外部裁判跑 DoD，exit 0 才算完成
              │  unittest／verify_inbox.py／generate_dod_verifier.py
              ▼
          提交（驗證與 commit 之間用 && 串接，不用 ;）
```

四條的性質不同，加固的難度也不同：

| 原則 | 可量測的部分 | 無法機械化的部分 |
| :--- | :--- | :--- |
| ① Think Before Coding | 有沒有宣告、有沒有在宣告前改檔 | 宣告的理由是否真誠、歧義是否真的被問清楚 |
| ② Simplicity First | 檔案大小、檔數、行數 | 「是不是過度設計」本質上是判斷 |
| ③ Surgical Changes | 改了哪些檔、改了多少行、空白雜訊、註解被刪 | 範圍內的改動對不對 |
| ④ Goal-Driven Execution | 測試是否 exit 0、DoD 產出檔是否存在 | 測試本身寫得夠不夠、DoD 是否定義得好 |

---

## 3. 硬閘門對照矩陣

「本 repo 實作」欄只列實際存在且查過的檔案。沒有實作的就直接寫沒有。

| 原則 | 文字規範（容易衰減） | 機械防線 | 本 repo 實作 | 能抓到 | 抓不到 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ① | Don't assume；有歧義先問 | 路由前置宣告：非瑣碎任務在第一個改檔動作前，必須先寫出路由與一句理由 | **不在本 repo**。維護者本機用 Claude Code 的 `PreToolUse` hook 強制（hook 檔在維護者的使用者設定目錄，未公開）。 | 沒宣告就動手改檔 | 宣告內容空泛、問題沒問到點上 |
| ② | Minimum code | 8192 位元組的本文預算；檔數與行數上限 | `tools/audit_skills_context_budget.py`（技能本文預設 8192 位元組，是本 repo 政策值，不是官方數字，見其檔頭）；`audit_surgical_diff.py` 的 `--max-files`、`--max-lines` | 技能本文過長、一次改太多檔或太多行 | 該不該有這個抽象層 |
| ② | 禁止空殼函式 | 靜態檢查 `pass`／`TODO`／回傳假資料 | **本 repo 尚未實作**（筆記提到的 AST 檢查器不存在）。需要時另開任務；不要在文件裡假裝已有。 | - | - |
| ③ | Touch only what you must | Git 變更範圍審查 | `tools/audit_surgical_diff.py`（第 4 節） | 範圍外檔案（新增、修改、刪除、改名）、空白重排、註解被抹除、檔數與行數超標 | 範圍內的錯誤改動、範圍內任意擴充功能 |
| ④ | Loop until verified | 外部裁判：獨立進程跑檢查，看 exit code | `python -m unittest discover -s tests`、`tools/verify_inbox.py`（CI 同款）、`tools/task_cli.py complete`（DoD 的產出檔必須存在）、`tools/generate_dod_verifier.py`（把 DoD 拆成機械檢查與人工清單） | 測試紅燈、DoD 檔案缺漏、筆記格式錯誤 | 測試本身無效、DoD 只寫「檔案存在」的空洞驗收（見 `docs/external-judge-audit.md`） |

使用規則：

1. 每條機械防線都要有一個「會失敗的反例」測試，並確認把實作弄壞時測試會變紅。只比對關鍵字的檢查，不算外部裁判（理由見 `docs/external-judge-audit.md` 第 5 節）。
2. 機械檢查只回報 exit code 與違規清單，不替 Agent 自動回滾。回滾由人或 Agent 依清單決定，避免檢查工具自己造成新的破壞。
3. 門檻（`--max-files` 等）是政策值，依任務大小調整，不是通則。

---

## 4. Surgical Diff 邊界審查：`tools/audit_surgical_diff.py`

### 4.1 它做什麼

讀真實的 `git diff --name-status`、`--numstat`（含 `-w` 忽略空白版本）與 `-U0`，對照開工前宣告的 `--scope`，回報違規。唯讀，不改檔、不改 git 狀態。

```text
 宣告 --scope ──┐
                ├─▶ git 實際變更（新增／修改／刪除／改名／未追蹤檔）──▶ 違規清單 + exit code
 門檻 ─────────┘
```

| 違規 | 觸發條件 |
| :--- | :--- |
| `out-of-scope` | 任一變更路徑不在 `--scope`（改名時，舊路徑與新路徑都要在範圍內） |
| `too-many-files` / `too-many-lines` | 受審檔數或新增＋刪除行數超過門檻（預設 10 檔、400 行） |
| `whitespace-only` | 檔案變更忽略空白後是 0 行（整份重排縮排、換行符改動） |
| `whitespace-noise` | 有實質變更，但夾帶超過 10 行（新增＋刪除合計）的空白雜訊 |
| `comment-erasure` | 非刪除檔案中，被刪的註解行比新增的多出超過 3 行 |

`--exempt` 指定的路徑（例如由腳本產生的 `README.md`、lockfile）不檢查範圍、不計入檔數與行數，但會列在「豁免」清單，不會悄悄消失。

結束碼：`0` 通過、`1` 有違規、`2` 參數或 git 錯誤。

### 4.2 用法

```bash
# 工作樹（含已暫存與未追蹤檔）對 HEAD，提交前檢查
python tools/audit_surgical_diff.py --scope tools/foo.py --scope tests/test_foo.py

# 兩個 commit 之間（例如 PR 整體檢查），README 由腳本產生所以豁免
python tools/audit_surgical_diff.py --base main --head HEAD --scope docs/ --exempt README.md --json
```

實際跑出的輸出（本 repo 工作樹，故意只宣告一個檔案）：

```text
範圍審查（HEAD -> 工作樹）：受審 2 個檔案、813 行變更
  A  tests/test_audit_surgical_diff.py  (+420 -0)
  A  tools/audit_surgical_diff.py  (+393 -0)
[FAIL] 2 項違規：
  [out-of-scope] tests/test_audit_surgical_diff.py - 新增了不在宣告範圍內的路徑
  [too-many-lines] - - 新增＋刪除共 813 行，上限 400
```

提交前的串接寫法（遵守「驗證與提交之間用 `&&`」）：

```bash
python tools/audit_surgical_diff.py --scope tools/foo.py --scope tests/test_foo.py \
  && python -m unittest discover -s tests \
  && git commit -m "feat: ..."
```

### 4.3 已知限制

- 註解判斷是依行首符號的啟發式，不解析語言語法。`.md`、`.txt`、`.rst` 不做註解檢查；C 系列副檔名的 `#` 開頭視為前處理指令。
- 它回答「改了哪裡、改了多少」，不回答「改得對不對」。範圍內的壞改動它看不出來。
- 工作樹模式下，尚未 `git add` 的改名會被 git 當成「刪除＋未追蹤新檔」，兩個路徑各自檢查範圍。
- 範圍是呼叫者自己宣告的。如果 Agent 同時控制宣告與被審的變更，這道閘門只防「疏忽」，不防「刻意」；要防刻意，範圍必須由任務來源（人、任務單）提供，不由執行的 Agent 自己決定。

---

## 5. 客觀 DoD 外部裁判

原則 ④ 的硬閘門只有一句話：**完成與否由獨立進程的 exit code 決定，不由 Agent 的自述決定。**

```bash
python -m unittest discover -s tests      # 必須 exit 0
python tools/verify_inbox.py              # 必須 exit 0（CI 同款）
```

- 判斷結果直接看 exit code。不要用 `| tail` 之類會蓋掉 exit code 的寫法來判斷成功與否。
- DoD 要寫成可執行的檢查，並指出產出檔路徑（反引號標出 `docs/...`），結案時 `task_cli.py complete` 會檢查檔案存在。只寫「檔案存在」是最低標準，不代表內容正確（參見 `docs/external-judge-audit.md`）。
- 需要把一份 DoD 轉成可交給第三方單獨執行的驗收腳本時，用 `tools/generate_dod_verifier.py`；它只把能機械檢查的部分產生成檢查，其餘列入人工清單，不假裝驗過。
- 回報完成時貼出實際指令與輸出，而不是「應該可以」。

---

## 6. 多 Agent 統一整合

目標：Claude Code、Codex、Antigravity 看到同一份規則，並且被同一組腳本檢查。**規則文字用 `AGENTS.md`；機械閘門不依賴任何一家 Agent 肯不肯讀檔，放在 git 與 CI 層。**

```text
           AGENTS.md（一份規則，三個 Agent 共用）
            │
   ┌────────┼─────────────────┐
   ▼        ▼                 ▼
 Claude   Codex          Antigravity
 Code     （原生讀）      （讀取行為：未驗證）
   │        │                 │
   └────────┴────────┬────────┘
                     ▼
        git 層／CI 層（與 Agent 無關）
   audit_surgical_diff.py ──▶ unittest ──▶ verify_inbox.py
```

各 Agent 的事實（查證日期 2026-11-02）：

| Agent | 讀規則檔的方式（官方文件） | 可掛的機械攔截 |
| :--- | :--- | :--- |
| Claude Code | 預設讀 `CLAUDE.md`；**只有在工作目錄與其上層都沒有 `CLAUDE.md` 時才讀 `AGENTS.md`**。要共用一份，在 `CLAUDE.md` 放一行 `@AGENTS.md` 匯入；Windows 上官方建議用匯入而非符號連結。 | Hook：`PreToolUse` 的 hook 以 exit code 2 阻擋該次工具呼叫；`Stop` 的 hook 以 exit code 2 阻止 Claude 結束、讓對話繼續。 |
| Codex | 開工前讀 `AGENTS.md`：先讀全域（`~/.codex`），再從專案根往下到目前目錄逐層尋找（各層細節與覆寫檔規則見官方頁面，本文未逐項驗證）。 | 本次沒有查 Codex 的 hook 或等價機制，**未驗證**。用 git 層與 CI 層的檢查。 |
| Antigravity | 官方文件頁面是前端渲染，本次無法讀到內容，**未驗證**它是否原生讀 `AGENTS.md`。 | 同上，**未驗證**；用 git 層與 CI 層的檢查。 |

整合步驟：

1. repo 根目錄只放一份 `AGENTS.md`（維護者規定 repo 不另建 `CLAUDE.md`、`GEMINI.md`）。若某個 Agent 已知不讀 `AGENTS.md`，才依其官方文件加匯入檔，並向維護者說明理由。範本見 `templates/karpathy-hardened-agents-md.md`。
2. 派工時在任務單寫明 `--scope`（要改的檔案）與驗收指令。範圍由派工者給，不由執行者自己決定。
3. 執行者每次準備提交前跑 `audit_surgical_diff.py`、測試與 `verify_inbox.py`，三個都 exit 0 才提交。
4. 整合者（人或另一個 Agent）在合併前，用 `--base main --head <分支>` 再跑一次，不採信執行者的自述。
5. 若使用的 Agent 支援阻擋式 hook（例如 Claude Code 的 `PreToolUse` 或 `Stop`），可讓 hook 呼叫同一支腳本，把 exit code 傳回。hook 的設定格式請依官方文件現行版本撰寫；本文不提供未驗證的設定片段。

---

## 7. 反模式

- **把機械閘門當作取代判斷**：`audit_surgical_diff.py` 通過，只代表沒越界，不代表改對。
- **把文字規則寫得越來越長**：Karpathy 自己指出簡單的 `CLAUDE.md` 指令仍擋不住；再加長只會稀釋注意力。能量測的就移進腳本，規則檔只留腳本管不到的判斷。
- **用 `;` 串接驗證與提交**：紅燈照樣提交。一律 `&&`。
- **讓執行者自己宣告範圍又自己審查**：只防疏忽，不防刻意（第 4.3 節）。
- **引用沒查證的數字**：例如 50K／100K token 衰減、「Karpathy 的第四種偏差」，見第 1.3 節。

---

## 來源（查證日期 2026-11-02）

- Karpathy 2026-01-26 貼文：`https://x.com/karpathy/status/2015883857489522876`。本次是透過 `https://api.fxtwitter.com/karpathy/status/2015883857489522876` 這個第三方鏡像取得全文（貼文時間 2026-01-26 20:25 UTC），沒有直接從 x.com 讀取；鏡像是否與原貼文逐字一致，未獨立比對。
- 四原則 `CLAUDE.md`：`https://github.com/forrestchang/andrej-karpathy-skills`（現轉址至 `multica-ai/andrej-karpathy-skills`）。第一個 commit `8462496b34419f20b32778610571ac723e91f94c`（2026-01-27 03:53 UTC，新增 `CLAUDE.md`、`README.md`）；查證用的 HEAD 為 `2c606141936f1eeef17fa3043a72095b4765b9c2`。README 的 "derived from Andrej Karpathy's observations" 寫法同在該 repo。
- Claude Code 讀取 `CLAUDE.md` 與 `AGENTS.md` 的規則：`https://code.claude.com/docs/en/memory`（"AGENTS.md" 段落）。
- Claude Code hook 的 exit code 2 行為：`https://code.claude.com/docs/en/hooks`（"Exit code 2 behavior per event"）。
- Codex 讀取 `AGENTS.md`：`https://developers.openai.com/codex/guides/agents-md`。
- Antigravity：`https://antigravity.google/docs/rules-workflows` 回應 200 但內容為前端渲染，未取得文字；相關說法一律標未驗證。
- 本 repo：`tools/audit_surgical_diff.py`、`tests/test_audit_surgical_diff.py`、`tools/audit_skills_context_budget.py`、`tools/generate_dod_verifier.py`、`tools/verify_inbox.py`、`docs/external-judge-audit.md`。
