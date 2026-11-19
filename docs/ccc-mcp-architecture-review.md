# ccc-mcp 架構唯讀檢閱：與 agent-relay、claim-guard 的對照

檢閱日期：2026-11-19。任務：T-20261119-02。作者：Claude Code。
來源筆記：[`notes/2026-11-19-codex-claude-multi-agent-orchestration-landscape.md`](../notes/2026-11-19-codex-claude-multi-agent-orchestration-landscape.md)。

**結論：不安裝、不整套採用；部分借鏡。** ccc-mcp 是「ChatGPT 當專案經理，透過 MCP 指揮 Codex 與 Claude」的集中式協調器，和本機「agent 之間寄信、收件端自己把關」的 agent-relay 走不同路線，換過去沒有好處。但它有三個做法本機沒有，值得各自評估：共用上下文的版本檢查、把「證據夠不夠」與「分數高不高」分開算、對 agent 自己寫的測試打折。額度不足改派這一項，本機已經做得比它完整。

## 1. 來源與審查範圍

| 對象 | Repo | 審查 commit | 授權 |
| --- | --- | --- | --- |
| ccc-mcp | [bruce601080102/ccc-mcp](https://github.com/bruce601080102/ccc-mcp) | `782c75ad3084ac2a00eca5fa7a8d3a4700aa4ce9`（2026-11-19） | MIT |
| agent-relay | [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) | `0cabfe33c46bc0ca80234fad579c2ea8ba82896c`（2026-11-15） | 見該 repo |
| claim-guard | [SanHsien/harness-guard](https://github.com/SanHsien/harness-guard) 的 `hooks/claim-guard/windows/` | `ec38c1d`（2026-11-10） | 見該 repo |

- ccc-mcp 以 `git clone --depth 1` 加 `-c core.hooksPath=NUL -c core.symlinks=false` 取到 `C:\GitHub\_sandbox\ccc-mcp-audit`。只讀原始碼；沒有 `pip install`、沒有啟動 MCP 伺服器、沒有跑它的測試。
- 規模：550 個追蹤檔，`src/ccc_mcp/` 約 22,800 行 Python。本文讀了與三個主題直接相關的模組，其餘（Web 控制台、CLI、角色與流程定義、`prototypes/`）只看了檔名與行數。
- 本文所有行號對應上表 commit。ccc-mcp 的路徑省略 `src/ccc_mcp/` 開頭。
- 「本機沒有」這類判斷是用關鍵字搜尋 agent-relay 與 claim-guard 原始碼得到的，可能漏掉換了說法的實作。

## 2. 機器掃描結果

指令：`python C:\GitHub\agent-safety-checks\tools\verify_agent_skill_pack_safety.py --pack C:\GitHub\_sandbox\ccc-mcp-audit`

結束碼 **1**。掃描 514 個檔案：FAIL 16 項、需人工審查 15 項、未掃描 51 個（都是圖片、PDF 與 `.DS_Store`）。

| 命中 | 位置 | 人工判讀 |
| --- | --- | --- |
| Codex 審批設為從不詢問 | `adapters/agents/codex.py:22`、`:81-82` | 屬實，但同時指定了沙盒：唯讀角色 `--sandbox read-only`，實作角色 `workspace-write`（第 87-88 行），並加 `--ignore-user-config`。不是關沙盒 |
| Codex 不審批也不用沙盒 | `benchmarks/toy-agents/acqe_docker.py:317` | 只在評測用的容器內使用；同檔第 1-12 行說明主機的 Codex 登入檔不掛進容器，改給一份 refresh token 已換成失效值的複本，第 298-307 行啟動前先驗證 |
| 讀取 Codex 登入檔 | `benchmarks/toy-agents/acqe_docker.py:4`、`:60`、`:160`；`benchmarks/toy-agents/run.py:430`、`:456` | 同上，評測工具才會碰，主程式 `src/` 沒有命中 |
| 略過權限提示 | `tests/test_adapters.py:154` | 誤判。該行是斷言啟動參數**不含**這個旗標 |
| SSH 私鑰路徑 | `tests/test_directedit.py:118` | 測試資料，用來驗證路徑防護 |
| `exec(compile(...))` | `prototypes/archgraph/userstudy/build_cases.py:72` | 原型目錄的研究腳本，不在安裝套件內 |

另外兩點掃描器沒有標出、人工看到的：

- `npm/bin/codex` 在 git 裡是符號連結（mode 120000），指向 repo 外的 `../lib/node_modules/@openai/codex/bin/codex.js`。本次 clone 關了符號連結所以只是一個文字檔；正常 clone 會建立連結。
- repo 根目錄的 `AGENTS.md` 第 3-5 行是寫給 agent 的工作規定（不可新增自動觸發的 GitHub Actions、不可代選版本號）。這是它自己的專案規範，與本次檢閱無關，記錄在此，未照做也不需照做。

## 3. 三個主題的實作

### 3.1 共用上下文的版本檢查

```text
ChatGPT（PM）                       ccc-mcp（SQLite）
   │ get_context ───────────────▶ 回傳目前 snapshot 與 version = N
   │
   │ 整理各 agent 回報，寫 ContextPatch
   │   base_context_version = N
   │   semantic_review_ack = true
   │ commit ─────────────────────▶ 取專案檔案鎖
   │                               目前 version 還是 N？
   │                                 否 → Version Conflict，整份退回
   │                                 是 → 同一個交易內：
   │                                        寫入 version N+1 的完整 snapshot
   │                                        標記 patch 已提交
   │                                        寫入「下一個要派誰」的指標
   ◀──────────────────────────────  回傳新版本
```

| 機制 | 位置 | 說明 |
| --- | --- | --- |
| 修補檔必帶基準版本 | `core/models.py:88-93` | `base_context_version` 是必填欄位 |
| 版本不符就拒絕 | `core/context.py:714-719`（驗證時）、`:849-853`（提交交易內再查一次） | 兩處都查，第二次在交易內，避免驗證後到寫入前被別人搶先 |
| 歷史只能增加 | `core/context.py:472-475` | SQLite 觸發器擋下對 `context_versions` 的刪除 |
| 專案層級檔案鎖 | `core/context.py:283-286` | `portalocker`，等待上限 30 秒 |
| 證據檔附雜湊 | `core/context.py:691-703` | 修補檔引用的檔案要帶 SHA-256，提交時重算，不符就要求重讀 |
| 只有 PM 能提交 | `core/models.py:118-128`、`core/context.py:710-713` | `SYSTEM` 身分保留給內部自動流程；PM 的修補檔要帶 `semantic_review_ack` |
| 可改的區段有白名單 | `core/context.py:720-722` | `project_name` 與 `purpose` 不可改 |

共用上下文的內容是固定結構（`core/models.py:74-85`）：狀態、下一步、摘要、未決問題、不變條件、架構事實、來源檔引用、各 agent 的回報、工作區變更。agent 的回報進來時標成 `review_status: "unreviewed"`（`core/models.py:65`）。

### 3.2 主機端測試與證據覆蓋率

```text
agent 回報（自述）──────────────▶ 證據狀態 CLAIMED   ← 不算驗證
主機自己跑測試指令 ─────────────▶ 證據狀態 VERIFIED
git diff（含未追蹤新檔）────────▶ 證據狀態 VERIFIED
主機跑 ruff ─────────────────────▶ 有結果 VERIFIED／沒裝 UNVERIFIED
                │
                ▼
      五個面向各自算分：測試、需求、程式品質、安全、審查
      算不出來的面向 = None（不補 0、不補滿分）
                │
        ┌───────┴───────────────────────────┐
        ▼                                   ▼
  quality_score                       evidence_coverage
  只用算得出的面向加權平均             算得出的面向權重 ÷ 全部權重
        │                                   │
        └───────────┬───────────────────────┘
                    ▼
              task_status（由硬規則決定，分數不能推翻）
              PASSED／TASK_FAILED／NEEDS_VERIFICATION／INSUFFICIENT_EVIDENCE
```

| 規則 | 位置 |
| --- | --- |
| agent 自述一律標 `CLAIMED`，註記「不是正確性的驗證」 | `evaluation_engine/evidence_collector.py:99-107` |
| 測試結果只有「主機執行」才算 `VERIFIED` | `evaluation_engine/evidence_collector.py:144-159` |
| 測試指令是參數陣列，不是 shell 字串 | `adapters/test_runner.py:350-352` |
| pytest 結束碼 5（沒收集到測試）另外記成 `no_tests_collected` | `adapters/test_runner.py:303-306`、`:409-418` |
| 沒收集到測試 → 不能判通過 | `evaluation_engine/quality_scorer.py:112-113` |
| 主機沒跑測試 → 不能判通過 | `evaluation_engine/quality_scorer.py:109-111` |
| 實作回合沒有任何變更 → 不能判通過，原本就綠的測試不算分 | `evaluation_engine/quality_scorer.py:46-48`、`:116-119` |
| 通過的測試全是這回合新建的測試檔 → 測試分數上限 70 | `evaluation_engine/quality_scorer.py:25-27`、`:50-51`；判定在 `evaluation_engine/diffs.py:97-107` |
| 新加的測試有任何一個失敗 → 直接判失敗，舊測試全過也不能抵 | `evaluation_engine/quality_scorer.py:103-106` |
| 證據覆蓋率低於 0.60 → 最多只能是「證據不足」 | `evaluation_engine/quality_scorer.py:24`、`:138-141` |
| 審查者說不用改、但主機測試失敗 → 審查結論作廢 | `evaluation_engine/quality_scorer.py:39-42`、`:127-130`；`core/tasks.py:224` |
| 角色間的分歧只有被主機事實證實的才扣分 | `evaluation_engine/disagreement_detector.py:1-10` |

弱點（讀原始碼看到的）：

- **需求覆蓋率是關鍵字重疊**。驗收條件每一條只要有任一個三字元以上的詞出現在 agent 自己寫的文字裡就算涵蓋（`evaluation_engine/feature_extractor.py:73-84`）。agent 把驗收條件抄一遍就能拿滿分，而實作角色這一項占權重 0.25（`evaluation_engine/config.py:28`）。
- **「新測試是否由失敗轉通過」是估算**。用 diff 裡新增的測試名稱去對 pytest 的失敗清單，原始碼自己註明是近似值（`evaluation_engine/feature_extractor.py:50-55`）。它沒有在基準 commit 上先跑一次確認測試真的會紅。
- **主機會依 agent 改過的相依清單自動安裝套件**再跑測試，裝在專案專屬的虛擬環境（`adapters/test_runner.py:195-208`）。原始碼註解自己寫明這是信任邊界。

### 3.3 額度不足時改派與中斷後接續

```text
工人行程失敗
   │ 錯誤訊息＋輸出 含 "usage limit"、"rate_limit_error"、"quota exceeded" 等 12 個字串之一？
   │   （infra/telemetry.py:584-602）
   ├─ 否 → 記 ERROR，結束
   └─ 是 → 記 QUOTA_EXHAUSTED
            設定裡有 quota_fallback？
              沒有 → 結束
              與原本同一家 → 不派
              這次本身就是備援 → 不再往下接
              否則 → 用同一個角色、同一個 context 版本、同一份指示改派
                     結果（派成功或失敗原因）寫回原執行紀錄
   （worker.py:209-273）
```

中斷接續是另一套機制：`commit_context_patch` 把「上下文已提交」與「下一個要派誰」寫在同一個 SQL 交易（`core/context.py:814-826` 的說明、`:855-860`）。行程在兩步之間當掉時，資料庫留有 `pending_dispatch` 指標，之後用 `resume_pending_dispatch` 從指標接續，不重新決定、不重複提交（`core/tasks.py:1290-1307`）。

## 4. 對照表

| 主題 | ccc-mcp | 本機 | 判斷 |
| --- | --- | --- | --- |
| 整體形態 | 單一行程＋SQLite，PM 集中提交 | 信箱目錄＋git 同步，沒有中央狀態；收件端自己把關（agent-relay `SPEC.md` 第 2、3、7 節） | 路線不同，不換 |
| 防止互相覆蓋 | 對**共用上下文**做版本檢查（樂觀鎖） | 對**檔案路徑**簽出（`agent_relay/locks.py:269`），重疊就拒絕；施工後檢查有沒有改到範圍外（`SPEC.md` 第 9 節） | 兩者管的東西不同。本機沒有共用上下文庫，`HANDOFF.md` 這類交接檔沒有版本檢查。**可借鏡** |
| 上下文帶給下一個 agent | 固定結構的 snapshot，來源檔附雜湊 | `relay context` 即時組交接包，有長度上限、機密遮罩、資料界線標記（`SPEC.md` 第 8 節） | 本機的注入防護較完整；ccc-mcp 的「證據檔附雜湊、變了就重讀」本機沒有。**可借鏡** |
| 驗收閘門 | 主機跑測試＋評分規則 | 收件端跑驗證指令；可要求 TDD：基準 commit 必須綠、放進新測試必須紅（`agent_relay/gates.py:508`，`SPEC.md` 第 11 節） | **本機較嚴**：真的在基準上跑出紅燈，ccc-mcp 只用名稱估算 |
| 空殼實作 | 沒看到對應檢查 | 用語法樹找只有 `pass`、`return None` 的新函式（`agent_relay/gates.py:182-236`） | 本機已有 |
| 工人改測試設定 | 沒看到對應檢查 | 刪測試檔或改測試設定檔會被擋（`SPEC.md` 第 11 節「防護」） | 本機已有 |
| 沒收集到任何測試 | 明確處理，不算通過 | 以關鍵字搜尋 `agent_relay/gates.py` 與 `dispatch.py` 沒有找到對應處理 | **可借鏡** |
| agent 只跑自己新寫的測試 | 測試分數上限 70 | 開 TDD 時有紅燈檢查；沒開 TDD 時沒有對應處理 | **可借鏡**（概念） |
| 證據夠不夠 | 另算覆蓋率，太低就不給結論 | 閘門結果是單一狀態（`ok`、`unverified`、`skipped` 等），沒有覆蓋率 | 可借鏡概念，不必照搬數字 |
| 互動 session 的完成宣稱 | 不適用（它不管互動 session） | claim-guard：宣稱「驗證通過」時，本輪要有驗證類指令紀錄，且之後沒有再改檔（`claim_evidence_guard.py:361-380`） | 本機獨有 |
| 額度不足改派 | 失敗後才比對字串，只有一個備援，不串接 | 派工前先查兩家額度，全滿就回 `deferred` 並寫明重置時間；失敗後依路由表改派；已限流的不會派回去（`SPEC.md` 第 10 節，`agent_relay/dispatch.py:79-127`） | **本機較完整** |
| 限流判定的誤判防護 | 比對範圍含工人自己的輸出（`worker.py:210`） | 只看 runtime 自己回報的錯誤事件，工人輸出裡提到 429 不算（`SPEC.md` 第 10 節） | **本機較嚴** |
| 中斷後接續 | 交易內寫指標，不會掉步驟 | 租約＋回收行程補 `interrupted`；暫時性錯誤在同一個 worktree 原地重跑 | 做法不同，都有處理 |
| 權限邊界 | Codex 指定沙盒層級；Claude 唯讀角色只給讀取工具（`adapters/agents/claude.py:95-98`） | 由收件端設定決定可用的 runtime 與範圍 | 相當 |

## 5. 可借鏡的項目與建議

依「改動小、效益明確」排序。這些是建議，沒有動任何檔案。

1. **零測試不算綠燈**（建議改 `SanHsien/agent-relay` 的 `agent_relay/gates.py`）
   驗證指令是 pytest 時，結束碼 5 代表沒收集到測試；`python -m unittest` 則是結束碼 0 但輸出 `Ran 0 tests`。兩種都該回 `unverified` 而不是 `ok`。參考 `adapters/test_runner.py:303-306` 的判定方式。動手前先在 agent-relay 寫一個會重現的測試，確認目前確實會放行。

2. **claim-guard 的驗證紀錄分等級**（建議改 `SanHsien/harness-guard` 的 `hooks/claim-guard/windows/claim_ledger_tracker.py`）
   現在 `--version`、`git status`、`Test-Path` 與 `pytest` 都記成同一種「驗證類指令」（第 88-103 行）。可仿照 ccc-mcp 的證據種類（`evaluation_engine/evidence_collector.py` 的 `kind`），至少分成「測試或建置」與「狀態查詢」兩類；宣稱「測試通過」時要求前一類。注意：這會增加擋下的次數，要先用現有紀錄估算誤擋率，而且 hooks 只能變嚴不能變鬆。

3. **交接檔加基準版本**（評估項，暫不建議動手）
   若之後出現兩個 session 同時改寫同一份 `HANDOFF.md` 而互蓋的實例，再考慮在檔頭放版本號或內容雜湊，寫入前比對。目前沒有實際事故，先不加機制。

4. **自寫測試打折的概念**（評估項）
   沒開 TDD 的派工，若變更只新增測試檔、沒改任何既有測試，可在回信加一行提醒「通過的測試都是這次新寫的」。只提醒，不擋。

明確不採納：

- 整套 ccc-mcp：需要 ChatGPT 當 PM 並開通道連回本機（`adapters/tunnel_client.py:1-5`、`:26` 會下載 OpenAI 的通道程式），與本機「不經外部服務、收件端自決」的做法不合。
- 加權品質分數：需求覆蓋率那一項是關鍵字重疊，容易被灌水；本機規則也已決定不再新增關鍵字型裁判（[`docs/external-judge-audit.md`](external-judge-audit.md) 第 5 節）。
- 依 agent 改過的相依清單自動安裝套件：信任邊界太寬。
- 額度改派邏輯：本機已較完整。

## 6. 已知限制

- 全部是讀原始碼的判斷，沒有執行 ccc-mcp；實際行為可能與註解不符。
- 「ccc-mcp 沒看到對應檢查」只代表在讀過的模組裡沒找到。`core/tasks.py`（3833 行）與 `interfaces/` 只看了與三個主題相關的段落。
- 筆記提到的「19 個角色、7 個工作流、Web 控制台」沒有檢閱：未查證。
- ccc-mcp 當天仍有提交，之後的版本要重看。
