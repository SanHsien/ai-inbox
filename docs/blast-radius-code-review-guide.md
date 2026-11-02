# 爆破半徑審查（Blast Radius Review）與核心 5 檔案門檻指南

> 任務：`T-20261028-05`｜來源筆記：[`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](../notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)
> 查證日期：2026-11-02。「作者原文」指 Thorsten Ball 的 X Article〈How I work with Agents〉（2026-10-25，來源見文末）。
> 讀完能做的事：拿到一個 Agent 產出的 diff，在幾分鐘內判斷哪些要逐行看、哪些只要確認四個問題。

---

## 1. 作者說了什麼、本 repo 加了什麼

作者原文關於審查的段落（白話轉述）：他只審查影響範圍大的程式碼。他的專案裡核心檔案少於 5 個，這些他自己審；資料庫遷移（database migrations）也審。至於 closure 或 class、型別是否更漂亮、變數命名，甚至重複的程式碼，他說自己不在乎了。他改問四件事：能不能正常運作？在「圖上的箭頭」這個層級我懂它嗎？Agent 有沒有端到端測過？一個月後我還改得動嗎？

| 項目 | 歸屬 |
| :--- | :--- |
| 只審高爆破半徑的程式碼；資料庫遷移要審；風格、命名、重複不再審；四個問題 | 作者原文 |
| 「核心檔案少於 5 個」 | 作者原文，但這是**他自己程式碼庫的描述**（"There are <5 central files"），不是他提出的通用門檻 |
| 「核心 ≤ 5 檔」當成可套用的審查門檻、以及用 diff 指令劃分梯隊 | **本 repo 的取捨**，原文沒有這個規則，也沒有說其他專案該用 5 |
| 授權／憑證層列為高風險 | **本 repo 延伸**，原文只明說核心檔案與遷移 |
| 第 3 節的梯隊判斷樹、第 4 節的指令與閾值 | **本 repo 延伸** |

一處原文需要註明：原文最後一句寫 "If yes, might review code"。依上下文，四個問題都回答「是」時應是「可以不審」，字面看起來像漏了 not 的筆誤。本文**按「四項皆是 → 免微觀審查」解讀**，這是推測，不是確認過的作者原意。

此外要記得作者的前提：他描述的是自己用最新模型、有端到端測試與工具、可以觀察整個開發流程的情境。前提不成立（沒有測試、Agent 看不到執行結果）時，免審的依據就不存在，見第 6 節。

---

## 2. 為什麼 5 這個數字不能照抄

- 專案小時，「核心」可能只有 3 個檔案；專案大時，可能有 30 個。把 5 當門檻會變成「前 5 個才算核心」的人為切割。
- 本 repo 採 5 的理由是**審查者注意力有限**：一次要逐行審的核心檔案超過 5 個，品質會下降。所以本文的規則是：**核心集合由風險決定（第 3 節）；若單次變更逐行審的檔案超過 5 個，拆成多個 PR，或請第二位審查者／獨立審查 Agent 分擔**。這是本 repo 的做法，不是原文主張。
- 專案要自訂核心清單，寫進該專案的 `AGENTS.md`（見第 7 節範例）。

---

## 3. 爆破半徑評估樹

對 diff 中的**每個檔案**依序問，第一個「是」決定梯隊：

```text
檔案被修改
   │
   ├─ 觸及授權／憑證／金流／加解密？ ──是──▶ 【T1 逐行審，必須人審】
   │
   ├─ 資料庫 schema 遷移，或不可逆的資料操作？ ──是──▶ 【T1 逐行審，必須人審】
   │
   ├─ 刪除檔案／改動 CI／發佈流程／權限設定？ ──是──▶ 【T1 逐行審】
   │
   ├─ 屬於專案列的「核心清單」（高扇入、全域共用）？ ──是──▶ 【T1 逐行審（作者明說核心檔案要審）】
   │
   ├─ 公開介面（函式簽名、CLI 參數、輸出格式、檔案格式）有變？ ──是──▶ 【T2】
   │
   ├─ 測試或驗證器被修改？ ──是──▶ 【T2 看有無被削弱，見證據規範黑名單第 4 條】
   │
   └─ 其餘（獨立的業務邏輯、文件、新增的獨立檔案）
            │
            └─▶ 【T3 免微觀審查，只問第 5 節四個問題】
```

| 梯隊 | 審什麼 | 不審什麼 |
| :--- | :--- | :--- |
| T1 | 每一行（授權／憑證／遷移／刪除／CI／核心清單）；遷移加回滾方式 | 無，不省略 |
| T2 | 公開介面、依賴方向、錯誤處理、測試是否被削弱 | 命名、風格、內部寫法 |
| T3 | 四個問題的答案與證據 | 其餘全部 |

「高扇入」的判定：被多少其他檔案引用。可以用 `git grep` 數一個模組被引用的檔案數；超過專案自訂的數字（本 repo 建議起點：被 10 個以上檔案引用）就列為核心候選。範例：本 repo 的 `tools/_judge_common.py` 被 11 個 `tools/`、`tests/` 內的檔案引用（2026-11-02 以 `git grep -l -E "^(from|import) _judge_common|from tools import _judge_common|import _judge_common" -- tools tests` 數得，數字會隨 repo 變動），所以它若列入核心清單，任何對它的改動都走 T1。

---

## 4. 用 `git diff` 劃分梯隊

以下指令預設用 Git Bash 語法；步驟 2、4、5、6 另附 PowerShell 版（2026-11-02 在 PowerShell 7 實跑：步驟 5、6 有命中結果；步驟 2、4 只確認語法可執行、無命中情境）。`BASE` 是要比較的基準（例如 `origin/main`），三個點代表從共同祖先比較。

**步驟 1：看整體規模與涉及哪些檔案**

```bash
git diff --stat BASE...HEAD
git diff --name-status BASE...HEAD      # A 新增 / M 修改 / D 刪除 / R 更名
```

**步驟 2：把高風險路徑挑出來**（T1 候選；路徑樣式依專案調整，下方是範例）

```bash
git diff --name-only BASE...HEAD | grep -i -E "migrat|schema|auth|secret|credential|token|\.github/workflows|permission"
```

PowerShell 版本：

```powershell
git diff --name-only BASE...HEAD | Select-String -Pattern 'migrat|schema|auth|secret|credential|token|\.github/workflows|permission'
```

> `grep` 找不到任何符合時 exit code 為 1，這只代表「沒有符合的路徑」，不代表指令壞掉；腳本化時要特別處理，不要讓它中斷流程。

**步驟 3：刪除與更名**（一律至少 T1 候選）

```bash
git diff --name-status --diff-filter=DR BASE...HEAD
```

**步驟 4：測試與驗證器被改的部分**（T2，找有沒有刪斷言或加 skip）

```bash
git diff BASE...HEAD -- tests/ | grep -E "^-.*(assert|self\.assert)|^\+.*(skip|xfail)"
```

PowerShell 版：

```powershell
git diff BASE...HEAD -- tests/ | Select-String -Pattern '^-.*(assert|self\.assert)|^\+.*(skip|xfail)'
```

**步驟 5：變更量排序**（每檔增刪行數，大檔先看）

```bash
git diff --numstat BASE...HEAD | sort -rn
```

PowerShell 版：

```powershell
git diff --numstat BASE...HEAD | Sort-Object { ($_ -split '\s+')[0] -as [int] } -Descending
```

**步驟 6：核心清單命中，命中者為 T1**（把專案核心清單存成每行一個路徑的檔案，例如 `.review-core.txt`）

```bash
git diff --name-only BASE...HEAD | grep -x -F -f .review-core.txt
```

PowerShell 版：

```powershell
$core = Get-Content .review-core.txt
git diff --name-only BASE...HEAD | Where-Object { $core -contains $_ }
```

> 這些指令只是**分流輔助**，不是判定：路徑名稱對不上不代表安全（例如把授權邏輯放在名為 `utils` 的檔案）。審查者仍要掃一遍 diff 的檔案清單。

**經驗閾值（本 repo 的取捨，非原文）**

| 觀察 | 建議 |
| :--- | :--- |
| T1 檔案超過 5 個 | 拆 PR，或加一位審查者 |
| 單檔增刪超過 500 行 | 即使是 T3 也先要求 Agent 說明結構，或拆開 |
| 同一個 PR 同時有 T1 與大量 T3 | 先審 T1，T3 的證據另外驗 |

---

## 5. T3 的「免微觀審查四條件」與如何驗

對應作者的四個問題。全部要有**證據**，不是審查者的感覺。證據的標準見 [`irrefutable-evidence-and-invalid-patterns-spec.md`](./irrefutable-evidence-and-invalid-patterns-spec.md)。

| 條件 | 作者原文的問法 | 怎麼驗 |
| :--- | :--- | :--- |
| 正常運行 | Does it work? | 實際跑過，附指令、輸出、exit code |
| 架構清晰 | Do I understand it at the arrows-in-a-diagram level? | 能畫出「誰呼叫誰」的簡圖。畫不出來，就是沒懂，退回請 Agent 補一張依賴圖或模組說明 |
| 端到端測試 | Did the agent test it end to end? | 有走真實進程／檔案的測試紀錄，不是只有 mock |
| 可維護性 | Can I change it in a month? | 用一個具體的假想修改問自己或問獨立審查者（例如「若要換輸出格式，要改幾個檔案？」），答得出來才算 |

四項有任何一項「否」或「不確定」→ 升到 T2。

---

## 6. 什麼情況下不能套用免審

- 專案沒有可靠的測試與驗證（「端到端」條件不成立）。
- Agent 看不到執行結果（沒有權限跑、日誌讀不到）。作者的前提是整個開發流程對 Agent 可見。
- 模型不是你信任的等級，或你還沒有累積對這個 Agent 產出品質的直覺。作者原文提到信任與直覺要累積（見證據相關段落）。
- 變更會被公開發布或影響使用者資料。
- 法規或合約要求人工審查。

---

## 7. 審查檢查清單（可複製）

```markdown
### Blast Radius 審查：<PR / commit 範圍>

- [ ] 已執行 `git diff --name-status BASE...HEAD`，列出所有檔案與梯隊
- [ ] T1 檔案（授權／憑證／遷移／刪除／CI／核心清單）：已逐行審
  - [ ] 遷移附回滾方式，或已說明為何不可回滾
  - [ ] 沒有明文機密、token、家目錄真實路徑
- [ ] T2 檔案：公開介面、依賴方向、錯誤處理已看
  - [ ] 測試／驗證器沒有被削弱（diff 中沒有被刪的斷言、沒有新增 skip）
- [ ] T3 檔案四條件都有證據：
  - [ ] 正常運行（指令＋exit code）
  - [ ] 架構圖／箭頭層級看得懂
  - [ ] 有端到端測試紀錄（非純 mock）
  - [ ] 一個月後能改（寫得出一個具體修改案例）
- [ ] T1 檔案數 ≤ 5；超過已拆 PR 或加審查者
- [ ] 判定：通過 / 退回（原因：）
```

專案核心清單與門檻在 `AGENTS.md` 的寫法範例：

```markdown
## 審查範圍（Blast Radius）
- 核心檔案（逐行審）：`src/auth/`、`src/db/migrations/`、`src/core/scheduler.py`
- 單次變更逐行審的檔案超過 5 個時，拆 PR。
- 其餘變更只需附：能跑的證據、架構簡圖、端到端測試、一個月後可改的說明。
```

---

## 8. 已知限制

- 路徑與關鍵字分流會漏：安全邏輯藏在一般名稱的檔案裡抓不到，需要審查者掃一遍檔案清單。
- 「架構清晰」「可維護性」仍是判斷，不是機械檢查；本文只把它轉成「畫得出圖」「答得出具體修改」兩個可被質疑的動作。
- 作者的做法是他個人在特定環境下的經驗，本文未驗證它在其他團隊同樣有效；採用後要記錄漏審造成的事故，來調整梯隊規則。
- 本文的 5 檔案與 500 行、10 個引用等閾值是本 repo 的起點估計，沒有實測依據。

---

## 來源

- Thorsten Ball，〈How I work with Agents〉，X Article，2026-10-25。tweet：<https://x.com/thorstenball/status/2114386050638336082>，文章：<https://x.com/i/article/2114385531811319808>。X Article 需登入才能直接瀏覽；本文以 fxtwitter 公開 API（`https://api.fxtwitter.com/thorstenball/status/2114386050638336082`）取得的全文區塊核對，2026-11-02 查證（第 1 節的轉述與 "If yes, might review code" 一句皆出自該全文）。
- Git 指令：`git diff --stat`、`--name-status`、`--numstat`、`--diff-filter` 於 2026-11-02 在本 repo 實際執行確認可用；文件參考 <https://git-scm.com/docs/git-diff>（未逐項比對該頁，僅作為官方出處）。
- 本 repo：[`docs/irrefutable-evidence-and-invalid-patterns-spec.md`](./irrefutable-evidence-and-invalid-patterns-spec.md)、`tools/_judge_common.py`（引用數以第 3 節指令計算）。
