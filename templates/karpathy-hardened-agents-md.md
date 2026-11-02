# Karpathy 風格加固版 AGENTS.md 範本

> 規範：[`docs/karpathy-rules-mechanical-hardening-spec.md`](../docs/karpathy-rules-mechanical-hardening-spec.md)｜範圍審查工具：`tools/audit_surgical_diff.py`
> 用法：複製下方「範本本體」整段到你專案根目錄的 `AGENTS.md`，把所有 `{大括號}` 換成實際內容；改完刪掉本引言與最後的「範本使用說明」。**第 2 節開頭的出處說明在範本本體內，要保留。**
> 檔名：repo 只放 `AGENTS.md`，不另建 `CLAUDE.md`／`GEMINI.md`。Claude Code 預設只在**沒有** `CLAUDE.md` 時才讀 `AGENTS.md`；專案若已有 `CLAUDE.md`，在其中放一行 `@AGENTS.md` 匯入（見規範第 6 節）。
> 出處與授權（2026-11-02 查證）：第 2 節的四條規則，標題、口號與條列內容大致逐條改寫自 forrestchang 的 [`andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills) 的 `CLAUDE.md`（查證用 commit `2c606141936f1eeef17fa3043a72095b4765b9c2`），該文件衍生自 Karpathy 2026-01-26 貼文的觀察，不是 Karpathy 本人撰寫（見規範第 1 節）。授權狀況：該 repo 的 README 寫 `MIT`，但上述 commit 的檔案樹裡**沒有 LICENSE 檔**，GitHub API 也沒有辨識出授權；因此「授權條款全文與版權人聲明」無從附上，本範本只能保留出處與連結。若你要在對外發布的產品中大量沿用其條文，請先向原作者確認授權。

---

## 範本本體（從這裡開始複製）

# {專案名稱} — Agent 作業規範 (AGENTS.md)

<!--
中文：本檔給所有 Agent（Claude Code、Codex、Antigravity 等）讀。規則只寫「腳本管不到的判斷」；能量測的一律放進第 4、5 節的指令。
English: Read by every agent. Keep only judgment rules here; anything measurable belongs in the commands of sections 4 and 5.
-->

## 1. 專案進入點 / Entry points

<!--
中文：Agent 開工前先讀這些，不要自己掃全目錄找。
English: Read these first instead of scanning the whole tree.
-->

- 專案用途：{一句話}
- 先讀：`{README.md}`、`{docs/architecture.md}`
- 程式碼在：`{src/}`；測試在：`{tests/}`
- 執行測試：`{測試指令，例如 python -m unittest discover -s tests}`
- 本檔以外的規範：{連結或「無」}

## 2. 行為規則 / Behavior rules

> 出處 / Attribution：本節四條規則改寫自 forrestchang/andrej-karpathy-skills 的 `CLAUDE.md`（https://github.com/forrestchang/andrej-karpathy-skills ，commit 2c60614，README 標示 MIT，repo 內無 LICENSE 檔），其觀察來自 Andrej Karpathy 的 2026-01-26 貼文；機械防線與範圍／DoD 區塊為本 repo 加入。 / Adapted from the above `CLAUDE.md`, which derives from Karpathy's 2026-01-26 post; the mechanical backstops and the scope/DoD blocks are added by this repo.

<!--
中文：以下四條是檢查清單，不是保證。每條後面標了機械防線；沒有機械防線的，靠你自己遵守並在回報中說明。
English: Four rules as a checklist, not a guarantee. Each has its mechanical backstop; where none exists, state in your report how you complied.
-->

### 2.1 先想再動手 / Think before coding

- 需求有一種以上合理解讀時，列出解讀並詢問，不要默默選一個。
- 動手前說出你的假設；不確定就停下來問。
- 有更簡單的做法就直接說。
- 非瑣碎任務在第一個改檔動作前，先寫一行：`ROUTE: {solo|delegate}｜理由：{一句話}`。
- 機械防線：{若有 hook 檢查前置宣告就寫檔名；沒有就寫「無，靠自律」}

### 2.2 極簡優先 / Simplicity first

- 只做被要求的事；不為只用一次的程式碼加抽象層，不加沒被要求的設定項或彈性。
- 不為不可能發生的情況寫錯誤處理。
- 200 行能寫成 50 行就重寫。
- 機械防線：`--max-files`、`--max-lines`（見 4.1）；{其他，例如技能本文 8192 位元組檢查，或「無」}

### 2.3 外科手術式修改 / Surgical changes

- 不「順手改善」相鄰的程式碼、註解、格式；不重構沒壞的東西。
- 沿用現有風格，即使你會寫得不同。
- 發現無關的壞程式碼，在回報中提出，不要刪。
- 你的改動造成的孤兒（沒人用的 import、變數、函式）要清掉；原本就存在的不要動。
- 檢驗：每一行變更都能對應到任務的要求。
- 機械防線：`tools/audit_surgical_diff.py`（見 4.1）

### 2.4 目標驅動 / Goal-driven execution

- 開工前把任務改寫成可驗證的目標：
  - 「加驗證」→ 先寫會失敗的測試，再讓它通過
  - 「修 bug」→ 先寫能重現的測試，再讓它通過
  - 「重構」→ 前後測試都要綠
- 多步驟任務先列計畫，每一步附驗證：`1. {步驟} → 驗證：{指令}`
- 機械防線：第 4.2、5 節的指令；以 exit code 為準。

## 3. 範圍 / Scope

<!--
中文：範圍由派工者填，不由執行的 Agent 自己決定；超出範圍先停下來問。
English: Filled in by whoever assigns the task, not by the executing agent. Stop and ask before leaving scope.
-->

- 本次任務：`{任務 ID 或一句話描述}`
- 允許變更的路徑（`--scope`）：
  - `{tools/foo.py}`
  - `{tests/test_foo.py}`
- 豁免路徑（`--exempt`，由腳本產生、不用人改）：`{README.md}` 或「無」
- 絕對不碰：`{.github/}`、`{secrets 或機密檔}`、{其他 repo}
- 破壞性動作（刪檔、覆寫、`git push`、改主分支）先取得人的明確同意。

## 4. 完成前必跑 / Pre-completion checks

<!--
中文：三項都 exit 0 才可回報完成。用 && 串接，不要用 ;，否則紅燈照樣往下走。
English: All must exit 0 before reporting done. Chain with &&, never ;, or a red check lets the next step run.
-->

### 4.1 範圍審查 / Scope audit

```bash
python tools/audit_surgical_diff.py --scope {tools/foo.py} --scope {tests/test_foo.py} --exempt {README.md} --max-files {10} --max-lines {400}
```

- 結束碼：`0` 通過、`1` 有違規（會列出越界檔案、空白雜訊、註解被刪等）、`2` 參數或 git 錯誤。
- 違規時不要自己調高門檻或擴大 `--scope` 讓它通過；回頭修改動，或向派工者說明為什麼需要擴大。

### 4.2 測試 / Tests

```bash
{python -m unittest discover -s tests}
```

### 4.3 串接提交 / Gate the commit

```bash
python tools/audit_surgical_diff.py --scope {tools/foo.py} --scope {tests/test_foo.py} \
  && {python -m unittest discover -s tests} \
  && git commit -m "{type}: {summary}"
```

## 5. 完成定義 / Definition of Done

<!--
中文：每一項要能被獨立進程檢查；寫不出檢查指令的項目，標為「人工」並說明誰來確認。
English: Each item must be checkable by an independent process; items with no command are marked manual with a named reviewer.
-->

| # | 驗收項 | 檢查指令或方式 | 預期 |
| :--- | :--- | :--- | :--- |
| 1 | {產出檔存在：`{docs/foo.md}`} | `{python -c "import pathlib,sys; sys.exit(0 if pathlib.Path('docs/foo.md').is_file() else 1)"}` | exit 0 |
| 2 | {測試通過} | `{python -m unittest discover -s tests}` | exit 0 |
| 3 | {範圍未越界} | 見 4.1 | exit 0 |
| 4 | {需要人判斷的項目} | 人工：{誰確認} | {確認方式} |

回報完成時，貼出實際執行的指令與輸出的關鍵行；沒有執行過的檢查，寫「未執行」，不要寫「應該可以」。

## 6. 反模式 / Anti-patterns

- 沒跑過檢查就說「已修好」；或註解掉失敗的測試讓它變綠。
- 為了讓 `audit_surgical_diff.py` 通過而擴大 `--scope` 或調高門檻。
- 順手整份檔案重新格式化、改縮排、換行符或排序 import。
- 為了「以後可能用到」加入未被要求的參數、抽象層或設定檔。
- 刪除你不理解的註解或程式碼。
- 用 `;` 串接驗證與提交。
- 在回報中引用沒查過的數字或出處。

## 7. 回報格式 / Report format

- 做了什麼（一到三句）
- 改了哪些檔案（路徑清單）
- 跑了哪些檢查、結果（指令＋exit code）
- 無法驗證或留下的疑點；沒有就寫「無」

## 範本本體結束（到這裡為止）

---

## 範本使用說明（交付前刪除）

1. 全文搜尋 `{`，每一處都要換掉或刪除；`.md` 內的 `{` 只應出現在你專案本來就需要的地方。
2. 第 3 節的範圍每次派工都重填；長期不變的部分（絕對不碰的路徑）可以留在檔內。
3. 第 4、5 節的指令必須真的能在你的專案跑；先實際執行一次再交付。`tools/audit_surgical_diff.py` 在本 repo；複製到其他專案時連同它的測試一起複製，並保持只用標準函式庫、需要系統有 git。
4. 相容性：本範本只用 Markdown 與 HTML 註解，不含任何特定 Agent 的專屬語法。各 Agent 讀取 `AGENTS.md` 的行為見規範第 6 節（Antigravity 的行為尚未驗證，因此機械檢查放在指令與 CI，不依賴它讀檔）。
5. 第 2 節開頭的出處說明請保留；若你改寫得與原文差異很大、不再是衍生作品，才可以改寫該行，並仍要說明靈感來源。
6. 規則文字不要越寫越長：能用腳本量測的，移進第 4、5 節的指令，這裡只留判斷類規則。
