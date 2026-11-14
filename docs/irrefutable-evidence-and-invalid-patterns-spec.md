# 無可辯駁證據（Irrefutable Evidence）與無效證據黑名單規範

> 任務：`T-20261028-04`｜來源筆記：[`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](../notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)
> 查證日期：2026-11-02。文中「作者原文」指 Thorsten Ball 的 X Article〈How I work with Agents〉（2026-10-25 發表，來源見文末）。
> 讀完能做的事：把第 5 節的片段貼進任何專案的 `AGENTS.md`，並用第 4 節的清單判斷一份「完成回報」收不收。

---

## 1. 哪些是作者原文、哪些是本 repo 的延伸

| 內容 | 歸屬 |
| :--- | :--- |
| 「Ask for irrefutable proof」是他認為影響最大的一項（原文用語 "Biggest game changer"） | 作者原文 |
| Agent 擅長產出證明：端到端走查、示範影片、前後數字 | 作者原文 |
| 要累積對證據的信任與直覺；在 `AGENTS.md` 寫入「這不算證據」 | 作者原文（"Put 'this is not evidence' in your AGENTS.md"） |
| 三大支柱（真實進程日誌、外部裁判 exit code、前後指標）的分法 | **本 repo 延伸**，原文沒有這個分類 |
| 黑名單的具體條目（吞例外、註解測試、截斷日誌等） | **本 repo 延伸**；原文只說要寫「不算證據」，沒有列出清單 |
| 第 5 節的規則片段、第 6 節的審查流程 | **本 repo 延伸** |

作者沒有說過哪些具體做法算無效。黑名單的依據分兩類：

- **有紀錄可查**（2026-11-02 開 `REVIEW.md` 核對行號；行號會隨該檔更新而移動）：
  - 第 7 條（截斷日誌）：`REVIEW.md:133`，T-20261026-28 的 `herdr status`「真實輸出」少 4 行卻沒標省略。
  - 第 11 條（無來源或錯誤的外部事實）：`REVIEW.md:133` 的 `--kind` 參數寫成 `antigravity`（合法值是 `agy`）；`REVIEW.md:132` 的 MD5 無法重現（T-20261026-06）；`REVIEW.md:134` 引用不存在的規則當出處（T-20261026-30）。
  - 第 12 條（沒驗證卻當成實測，相近紀錄）：`REVIEW.md:76`，「實測指令」實為範例，且引用不存在的檔案。
  - 第 9、10 條（無外部裁判、只驗檔案存在或關鍵字）：依據是 [`external-judge-audit.md`](./external-judge-audit.md) 的開頭與第 2 節稽核結論，不是 REVIEW.md。
- **常見失敗模式的整理**：其餘條目（吞例外、註解測試、管線蓋掉 exit code 等）是 Agent 協作中常見的失敗模式整理，REVIEW.md 沒有逐條對應的事故紀錄，不要當成已發生案例。

---

## 2. 有效證據契約：三大支柱

一份完成回報要被收下，三根支柱各自要有東西，缺一根就是「未完成」或「部分完成」。

### 支柱 A：真實進程的端到端紀錄

- 要有：**完整指令列** + **實際輸出** + **exit code**，來自真的啟動的進程（CLI、服務、瀏覽器），不是在同一個測試進程內呼叫函式。
- 能被第三人重跑：指令不依賴回報者腦中的狀態（環境變數、已開的視窗要寫明）。
- UI 類：附截圖或錄影，且截圖要看得出被測的版本或時間（例如頁面上的 commit hash、URL 列）。涉及本機畫面擷取時先遵守 [`multimodal-screen-privacy-spec.md`](https://github.com/SanHsien/agent-safety-checks/blob/main/docs/multimodal-screen-privacy-spec.md)。

### 支柱 B：外部裁判的 exit code

- 判定者不是寫程式的那個 Agent：測試套件、`verify_*.py`、CI、型別檢查、linter。審查範例見 [`external-judge-audit.md`](./external-judge-audit.md)。
- 回報要貼指令與 exit code `0`，不要寫「測試通過」四個字。
- 裁判本身要能失敗：新增或修改驗證時，要附一個「故意弄壞實作就會紅」的反例（把實作改壞、確認測試轉紅、再還原）。裁判從沒紅過，等於沒驗過。

### 支柱 C：前後對比

- 修 bug：修之前的失敗輸出 + 修之後同一個指令的通過輸出（同一指令、同一輸入）。
- 效能：同一台機器、同一份資料、同一測量方式的前後數字，附單位與次數。作者的例子是前後數字（before/after numbers）。
- 新功能：「修之前不存在」可以用修之前同指令回傳「找不到／失敗」來證明。

> 不是每個任務三根都適用（純文件任務通常只有 B 與部分 A）。規則是：**不適用的支柱要在回報裡寫明理由**，不能默默省略。

---

## 3. 證據強度分級（本 repo 的簡化標準）

| 等級 | 內容 | 能不能當完成依據 |
| :--- | :--- | :--- |
| E3 | A + B + C 皆具備，且能被第三人重跑 | 可以 |
| E2 | A + B（無前後對比，因任務不適用並已說明） | 可以 |
| E1 | 只有 B，或只有 A | 不行，補另一根再回報 |
| E0 | 只有文字宣稱、或命中第 4 節黑名單 | 視為沒做 |

---

## 4. 無效證據黑名單

每一條都附「為什麼無效」與「怎麼補」。命中任何一條，該項證據作廢（不是扣分）。

| # | 反模式 | 為什麼無效 | 怎麼補 |
| :-: | :--- | :--- | :--- |
| 1 | 口頭宣稱：「已修復」「應該可以」「看起來沒問題」 | 沒有可檢驗的內容；Agent 擅長寫出像修好的敘述 | 貼指令與輸出 |
| 2 | 只貼「N tests passed」的摘要行，沒有指令與 exit code | 不知道跑了哪些測試、是否被篩選；摘要行可以手寫 | 貼完整指令與 `$?`（PowerShell 為 `$LASTEXITCODE`） |
| 3 | 用 `\| tail`、`\| head`、`; echo done` 等寫法接在指令後面，再拿結果判斷成功 | 管線會蓋掉前一個指令的 exit code | 分開執行，或開啟 pipefail，單獨回報 exit code |
| 4 | 把失敗的測試註解掉、改成 `skip`、放寬斷言後的綠燈 | 綠燈來自刪掉檢查，不是來自程式變對 | 附 `git diff` 證明測試檔沒有被削弱，或說明並獲准修改測試的理由 |
| 5 | 吞掉例外：`except: pass`、catch 後 `return 0`、`\|\| true`、`exit 0` 寫死 | 失敗被轉成成功；exit code 0 不再代表任何事 | 失敗時必須非零結束；反例測試要能讓它紅 |
| 6 | 只在記憶體內 mock 的資料，沒有涵蓋任何外部進程、檔案或網路邊界 | 驗的是自己寫的假資料；真實邊界出的錯完全看不到 | 至少有一條測試走真實檔案／進程；mock 僅限第三方付費或不可重現的服務，並在回報註明 |
| 7 | 截斷或剪輯過的日誌（只貼成功的那段、`...` 省略中間） | 失敗訊息常在被省略的地方 | 貼完整輸出，過長就存成檔案附路徑與 hash |
| 8 | 只有舊輸出：貼的是上一輪或上個 commit 的結果 | 與目前的程式碼無關 | 在最後一次修改之後重跑，回報要附 `git rev-parse HEAD` 與是否有未提交變動 |
| 9 | 自己寫的檢查自己判定：由同一個 Agent 寫腳本、跑腳本、宣布通過，腳本只比對自己剛產出的字串 | 沒有獨立的裁判 | 用既有的外部裁判，或請另一個 context 全新的審查者驗收 |
| 10 | 只驗關鍵字存在（例如 `Select-String '結論'`） | 擋不住內容錯誤或位置放錯 | 解析結構、核對來源、或交給獨立審查（見 external-judge-audit） |
| 11 | 沒有來源的外部事實：版本號、參數、數字、網址 | 本 repo 曾因此被退回 | 附一手來源網址與查證日期，查不到就標「未驗證」 |
| 12 | 把「環境不支援所以沒跑」寫成通過 | 沒跑就是沒驗證 | 明寫「未驗證」與原因，列為留下的疑點 |
| 13 | 截圖來源不明（不是目前版本、沒有可辨識的頁面資訊）或事後編輯過 | 無法確認截的是什麼 | 重新擷取，附時間與版本資訊 |
| 14 | 讀回自己剛寫的檔案內容，當作「功能運作」的證據 | 只證明檔案寫進去了 | 執行該檔案所代表的行為 |

回報者若無法避開某條（例如第 6 條，只能 mock），要在回報的「留下的疑點」寫明，而不是隱瞞。

---

## 5. 可貼進 `AGENTS.md` 的規則片段

```markdown
## 完成證據（Evidence）

回報「完成」之前，必須附上：
1. 實際執行過的完整指令，與其 exit code（不要只貼摘要行）。
2. 該指令來自真的啟動的進程，不是只在記憶體內 mock。
3. 能失敗的外部裁判（測試、驗證器、CI），不是你自己剛寫的比對。
4. 修 bug 或改效能時：修改前後、同一指令的對照輸出。
5. 外部事實（版本、參數、數字、網址）附一手來源與查證日期；查不到寫「未驗證」。

以下不算證據，一律視為未完成：
- 「已修復」「應該可以」等文字宣稱。
- 只有 `N passed` 摘要行，沒有指令與 exit code。
- 用管線（`| tail`、`| head`）後判斷成功，或 `|| true`、寫死 `exit 0`。
- 註解、skip、放寬斷言之後的綠燈；吞例外之後的綠燈。
- 全部是記憶體內假資料的測試。
- 截斷、剪輯過的日誌；最後一次修改之前的舊輸出。
- 你自己寫、自己跑、自己判定的檢查。
- 沒跑卻寫通過；環境不支援就寫「未驗證」並說明原因。

不確定某項是否算證據時，當作不算。
```

整合時的注意：

- 放在專案 `AGENTS.md` 的完成條件章節即可，不要複製到每個子目錄的 `AGENTS.md`（重複規則會增加維護成本，也會稀釋注意力；規則是否真的有用，用 [`agents-knowledge-ab-test-protocol.md`](./agents-knowledge-ab-test-protocol.md) 驗）。
- 本 repo 的 `AGENTS.md` 已有驗證指令（`python -m unittest discover -s tests`、`python tools/verify_inbox.py`）；這份片段是補充「什麼樣的回報算數」，不取代它們。
- 這份片段與本 repo 的 [`docs/pstack-governance-integration.md`](./pstack-governance-integration.md) 的驗收閘門互補：閘門是機械式擋下，片段是讓 Agent 事前就知道標準。

---

## 6. 審查者的檢查流程

收到一份完成回報時，依序檢查，遇到不合格就退回並指出是黑名單第幾條：

1. 有沒有完整指令與 exit code？（黑名單 1、2、3）
2. 輸出是否在最後一次修改之後產生？（8）
3. 測試檔、驗證器有沒有被削弱？看 `git diff` 的測試檔部分。（4、5）
4. 裁判能不能失敗？要求看過「弄壞實作會紅」的紀錄。（9、10）
5. 外部事實有沒有來源？（11）
6. 有沒有把沒跑的東西寫成通過？（12）
7. 評為 E0～E3（第 3 節）。E0、E1 退回。

---

## 7. 已知限制

- 這份規範要求的是**可檢驗性**，不保證證據內容正確：一個設計不良的測試可以全綠。所以支柱 B 要求裁判有反例，高風險變更仍需要人或獨立審查者看（見 [`blast-radius-code-review-guide.md`](./blast-radius-code-review-guide.md)）。
- 規則會增加回報長度。低風險小修改可由專案自行放寬為只要求支柱 B，但放寬要寫進該專案的 `AGENTS.md`。
- 黑名單 14 條中，第 7、9、10、11、12 條有本 repo 的紀錄或稽核可對應（見第 1 節），其餘是常見模式整理；清單不是窮盡的，之後遇到實際事故再補案例並標註出處。

---

## 來源

- Thorsten Ball，〈How I work with Agents〉，X Article，2026-10-25。tweet：<https://x.com/thorstenball/status/2114386050638336082>，文章：<https://x.com/i/article/2114385531811319808>。X Article 需登入才能直接瀏覽；本文以 fxtwitter 公開 API（`https://api.fxtwitter.com/thorstenball/status/2114386050638336082`）取得的全文區塊核對，2026-11-02 查證。第 1 節對作者的歸屬都以該全文為準。
- 作者資訊：作者 X 帳號簡介寫明任職 Amp（@ampcode）、部落格為 <https://registerspill.thorstenball.com>（同一 API 回傳，2026-11-02）。
- 本 repo：[`docs/external-judge-audit.md`](./external-judge-audit.md)、[`docs/pstack-governance-integration.md`](./pstack-governance-integration.md)（皆已開檔確認存在）；已搬到 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks)：[`docs/multimodal-screen-privacy-spec.md`](https://github.com/SanHsien/agent-safety-checks/blob/main/docs/multimodal-screen-privacy-spec.md)。
