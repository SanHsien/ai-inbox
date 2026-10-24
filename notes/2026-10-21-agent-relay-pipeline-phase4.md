---
id: 2026-10-21-agent-relay-pipeline-phase4
title: "多 Agent 派工與驗收閉環流水線 Phase 4：前三階段檢討補強、Hermes／Codex 工人、跨機器結果回傳與指揮者驗收合併"
source_url: "https://github.com/SanHsien/agent-relay"
source_platform: "GitHub"
author: "SanHsien"
analyzed_at: 2026-10-21
analyzed_by: "Claude Code"
status: done # pending | in-progress | done | archived
cluster: 1
cluster_role: "派工落地"
short_title: "agent-relay Phase 4：工人擴充、跨機器回傳與驗收合併"
tags:
  - agent-workflow
  - multi-agent
  - agent-relay
---

# 多 Agent 派工與驗收閉環流水線 Phase 4：前三階段檢討補強、Hermes／Codex 工人、跨機器結果回傳與指揮者驗收合併

- **來源連結**：[SanHsien/agent-relay](https://github.com/SanHsien/agent-relay)（Phase 1～3 實作與實測紀錄）
- **發布平台 / 作者**：`GitHub` / `SanHsien`
- **分析日期**：`2026-10-21`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 核心內容摘要

- **核心主張 / 解決的問題**：
  - Phase 1～3 的 9 項任務已完成（見 [AI 共同大腦全景規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) 第 1.3 節與 README 流水線段落）。寄信、門鈴、自動開 Session 施工、交接包、簽出鎖、額度分派、驗收閘門、回流升級都已實測。
  - 回頭盤點「各 Agent 自動互傳訊息、由指揮者派工與驗收」的目標，再加上 fresh Opus 審查對前三階段的檢討（第 1.1 節），缺口分三類：
    1. **安全前提**：寄件者可以冒名；施工起點由收件端決定；回信沒有給機器讀的欄位。這三項不補，跨機器回傳程式碼就不安全。
    2. **閉環缺口**：Hermes 不能被派工；Codex 從沒實際派工過；結果拿不回指揮者；指揮者端也沒有「驗收後合併」的動作。
    3. **營運缺口**：沒有並發、花費上限；看不到收件端是否還活著；worktree、分支、runs 只增不減；從沒在真的兩台機器上測過。
- **關鍵機制 / 做法**：

```text
指揮者 send --run hermes|codex|claude|auto --base <sha>   （信件以 SSH 金鑰簽章）
   └─▶ 收件端：驗簽 → 政策（senders 預設拒絕）→ 並發／額度上限
          └─▶ 簽出 → worktree（起點 = base）→ 工人 → 驗收閘門（→ 回流升級）→ commit
                 └─▶ push relay/<id> 到 origin（opt-in）
                        └─▶ 回信：結構化欄位 {status, branch, commit, base, gate.sha256, usage}
指揮者 relay accept <回信 id>
   └─▶ fetch → 核對 commit／base → 暫時 worktree 用「指揮者自己的」驗證指令重跑 → 通過才 merge --no-ff
relay status（信箱、跑中工單、心跳）   relay gc（清 worktree／分支／runs）
```

### 1.1 Phase 1～3 檢討（2026-10-21，fresh Opus 審查）

| 問題 | 證據 | 處置 |
| --- | --- | --- |
| 沒設 `senders` 時任何寄件者都放行，`from` 是任意字串；閘門會執行工人寫的測試，claude 工人「不給 shell」的防線因此被繞過 | `dispatch.py` policy_check、SPEC §7／§11 | `T-20261021-07` |
| worktree 以收件端當下 HEAD 為起點，推送分支會夾帶不相干 commit | `dispatch.py` make_worktree | `T-20261021-08` |
| 回信只有一段文字，accept 只能解析文字 | `dispatch.py` 回信組裝 | `T-20261021-08` |
| 每封信開一個分頁、重試 3 次 × 2 輪、逾時 120 分，沒有並發與花費上限；同一張工單可能重跑 | `dispatch.py` 開分頁、重試迴圈 | `T-20261021-09` |
| 沒有總覽指令；排程用 InteractiveToken，登出就停，指揮者看不出 | `cli.py`、`poller.py` | `T-20261021-10` |
| worktree、`relay/*` 分支、`runs/`、done 信件只增不減 | `dispatch.py`、`store.py` | `T-20261021-11` |
| Phase 1／2 的跨機器實測是同主機的兩份 clone | `docs/evidence/2026-10-20-phase1.md` | 原第 12 項（已取消，見 3.1） |
| DoD 比步驟寬鬆：`T-20261017-32` 的步驟要求端到端，DoD 只要求交報告，Space Bunny 未實測就標了完成；`T-20261018-18` 的 DoD 提到整合 agent-governance-toolkit，實際沒有整合 | 兩則筆記的 DoD | 不改既有勾選（依當時 DoD 確實達成），差額原由第 06 項（已取消，見 3.1）與 SPEC §11 的已知限制承接。之後的 DoD 一律寫明真實拓撲，並至少一個反例 |

**原計畫（Gemini 3.8 Flash 撰寫）的共通弱點**：DoD 多是「做出來並實測一次」，沒有反例。安全邊界（冒名、越界寫入、沙箱）用正向實測測不出來。Phase 4 起每個 DoD 都附反例。

## 2. 對現有工作流與專案之啟發

- Hermes CLI（Windows desktop 版 v0.22.2）的 `-z` 單次模式會**自動略過核可**，所以安全只能靠工具組與寫入根目錄。2026-10-21 實測：
  - `-t file` 只剩 `read_file`、`write_file`、`patch`、`search_files`，沒有 shell。
  - 但 `write_file` 能寫到 `--in` 以外的目錄。
  - 設 `HERMES_WRITE_SAFE_ROOT=<worktree>` 後，越界寫入被擋（`Write denied ... outside HERMES_WRITE_SAFE_ROOT`）。
  - worktree 的 `.git` 是指向主 repo 的檔案，hooks 目錄在根目錄外。
- 「驗收在收件端做一次、指揮者端再做一次」，符合本流水線「工人報告只是聲明、主 session 自己驗證」的原則（agent-advisor cross-cli 規範）。指揮者重跑時只用**自己 config 裡的**驗證指令，不採用分支裡的設定檔。
- 推送分支只推到 repo 自己的 `origin`，而且只限維護者的 repo（全域規範：push／PR 只打 `SanHsien/<repo>`）。
- 寄件者驗證用 OpenSSH 內建的 `ssh-keygen -Y sign/verify`（Windows 11 內建），簽在信件本身。這樣身分綁的是 `from`，不是誰推了 store 的 commit；不需要 GPG。

## 3. 具體評估待辦事項

執行順序：`T-03` → `T-07` → `T-08` → `T-05` → `T-04` → `T-09` → `T-10` → `T-11`（全部完成）。

- [x] **`T-20261021-03`**｜**[優先級：高]** 把 Hermes 接成 agent-relay 的派工 runtime（`--run hermes`），讓指揮者能用一封信叫 Hermes 在 worktree 施工
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@06171bf](https://github.com/SanHsien/agent-relay/commit/06171bf)，實測見 [docs/evidence/2026-10-21-t03-hermes.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t03-hermes.md)。
    - 正向：`--run hermes` 派工 status ok，relay commit `2d16fbc`，閘門 green 並附 sha256，回信附 Hermes 用量（16 次 API 呼叫，249k tokens）。
    - 反例：shell 沒有工具可用；寫 worktree 外被 `HERMES_WRITE_SAFE_ROOT` 擋下，檔案系統確認沒有越界檔案。
    - 實測時發現並修正 `gitsync.commit` 在空的 `claims/` 資料夾時失敗的 bug（回信卡在收件端）。
    - 231 項測試、CI（Windows＋Ubuntu）綠燈；fresh Opus 審查 fix-first，修正後複查 ship。
  - **目標範圍**：`SanHsien/agent-relay`（`agent_relay/dispatch.py` runtime 與指令組法、SPEC 第 7 節）＋ Hermes Windows desktop 版 CLI
  - **具體實作步驟**：
    1. runtime 加 `hermes`：`hermes.exe -z <prompt> --in <worktree> -t file --usage-file runs/<id>/hermes-usage.json`，以 `HERMES_WRITE_SAFE_ROOT=<worktree>` 限制寫入；不給 `--yolo`，不給 terminal、code_execution 工具組；plan 模式也只用 `-t file`，並在 prompt 要求只讀（另由 relay 偵測改動）。
    2. 只執行真正的 `hermes.exe`；prompt 一律寫入 run 目錄的檔案，命令列只放「讀取該檔並照做」的短指令（避開 32K 命令列上限）。
    3. 單元測試涵蓋指令組法、環境變數與政策檢查。
  - **驗收標準（DoD）**：
    - 正向：一封 `--run hermes` 派工在收件端 worktree 施工、通過驗收閘門、由 relay commit 並自動回信；回信附 Hermes 用量報告。
    - 反例：同一封信要 Hermes 執行 shell，並寫 worktree 外的檔案，兩者都不得成功（以檔案系統與 log 證明）。各實測一次。

- [x] **`T-20261021-07`**｜**[優先級：高]** 寄件者驗證：信件 SSH 簽章＋`senders` 預設拒絕
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@1fb8194](https://github.com/SanHsien/agent-relay/commit/1fb8194)、[@aefead5](https://github.com/SanHsien/agent-relay/commit/aefead5)（SPEC 第 13 節），實測見 [docs/evidence/2026-10-21-t07-signing.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t07-signing.md)。
    - 正例：簽章派工 ok，relay commit `4284800`。
    - 反例：未簽冒名 commander、錯誤金鑰冒名 commander 都被 refused，也沒有建立 worktree。三封回信都有收件端簽章，指揮者驗證通過。
    - 審查後補上的防護：本機 run 紀錄防重放、`max_age_hours`、`trust` 名稱檢查。
    - 單元測試涵蓋竄改、轉寄、身分綁信箱、重放。CI 綠燈；fresh Opus 審查 fix-first，修正後 ship。
  - **目標範圍**：`SanHsien/agent-relay`（`envelope.py`、`cli.py send`、`dispatch.py policy_check`、SPEC 新章節）
  - **具體實作步驟**：
    1. 寄信時若 config 有 `signing.key`，用 `ssh-keygen -Y sign -n agent-relay` 對信件正規化 JSON 簽章，簽章放進信件欄位。
    2. 收件端以 `signing.allowed_signers`（身分 = 信箱名）做 `ssh-keygen -Y verify`。
    3. 啟用 `dispatch` 時，`senders` 未設定 → 一律拒絕派工；`dispatch.require_signature`（預設 true）→ 簽章缺漏或不符時回 refused。
  - **驗收標準（DoD）**：簽章正確的派工照常執行；以未簽章或錯誤金鑰冒名 `commander` 的派工被 refused（單元測試＋實測各一次）。

- [x] **`T-20261021-08`**｜**[優先級：高]** 指定施工起點與結構化回信
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@aefead5](https://github.com/SanHsien/agent-relay/commit/aefead5)、[@7833baa](https://github.com/SanHsien/agent-relay/commit/7833baa)，實測見 [docs/evidence/2026-10-21-t08-base-result.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t08-base-result.md)。
    - 收件端 HEAD 帶本機獨有的 commit 時，worktree 仍從指定的 base 開工（先從 origin fetch）。
    - 不存在的 base 回 refused。
    - 回信的 `result` 欄位含 status、branch、commit、base、gate sha256、usage，而且有簽章。
    - 審查建議 base 只收 40 位 sha，已採用。fresh Opus 審查 ship。
  - **目標範圍**：`SanHsien/agent-relay`（`send --base`、`make_worktree`、回信 `result` 欄位、SPEC §7）
  - **具體實作步驟**：
    1. 派工信可帶 `dispatch.base`（commit sha）；收件端本機沒有這個 sha 時先 `git fetch origin`，仍找不到就回 refused。
    2. 回信加機器可讀的 `result` 欄位：`{status, runtime, branch, commit, base, gate:{status, log_sha256}, usage}`。
  - **驗收標準（DoD）**：收件端 HEAD 在別的 commit 時，worktree 仍以指定 sha 為起點；找不到 sha 時被 refused；回信 JSON 含上述欄位（單元測試＋實測）。

- [x] **`T-20261021-05`**｜**[優先級：高]** 結果分支回傳與指揮者驗收合併（`dispatch.push_branch`＋`relay accept`）
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@9889863](https://github.com/SanHsien/agent-relay/commit/9889863)、[@35dfb33](https://github.com/SanHsien/agent-relay/commit/35dfb33)（SPEC 第 14 節），實測見 [docs/evidence/2026-10-21-t05-accept.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t05-accept.md)。
    - 接受：A 由指揮者自己的驗收腳本驗證「main＋分支」的合併後，fast-forward 合入（`1090ab9`）。
    - 驗證失敗拒收：B 收件端閘門通過，但指揮者驗證 exit 1。
    - 分支被動過拒收：C 在回信後被多推一個 commit，accept 時未執行驗證、未合併。
    - 實測時發現並修正 store 同步的 directory rename 衝突（`7396db1`，這個 bug 從 Phase 1 就存在）。
    - CI 綠燈；fresh Opus 審查 fix-first，修正後 ship。
  - **目標範圍**：`SanHsien/agent-relay`（新增 accept 指令、SPEC 新章節）
  - **具體實作步驟**：
    1. 收件端設定 `dispatch.push_branch: true` 時，閘門通過並 commit 後把 `relay/<id>` 推到 repo 的 `origin`（只限 `SanHsien/` 的 repo）。
    2. 指揮者執行 `relay accept <回信 id> --repo <本機 clone> --into <分支>`，依序：
       - 讀回信的結構化欄位（`T-08`），fetch 該分支，核對分支 HEAD 等於回信的 commit、merge-base 含 base。
       - 在暫時 worktree 用**指揮者自己 config** 的驗證指令重跑（不採用分支內的 loop-policy、package.json）。
       - 通過才 `merge --no-ff`；主工作目錄不乾淨就拒絕。
       - 結果記入 audit，並回信給收件端。
    3. 單元測試以兩份 clone 加本機 bare remote 模擬跨機器。
  - **驗收標準（DoD）**：通過的分支被合併；驗證失敗的分支被拒絕；回信後被多推一個 commit 的分支被拒絕。三種情況各實測一次。

- [x] **`T-20261021-04`**｜**[優先級：高]** Codex runtime 實際派工驗證（workspace-write 沙箱）
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@390cf16](https://github.com/SanHsien/agent-relay/commit/390cf16)、[@be147aa](https://github.com/SanHsien/agent-relay/commit/be147aa)，實測見 [docs/evidence/2026-10-21-t04-codex.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t04-codex.md)。
    - 第 1 封發現：維護者的 codex 設定裡的 `writable_roots`（`%TEMP%`）把 workspace-write 撐大，工人寫得進主 repo 的 `.git/hooks`。
    - 修正：relay 每次都把寫入範圍釘回 worktree，並關閉網路。
    - 修正後實測一次完成：status ok，relay commit `9561cd3`，閘門 green，已推送；`argv.json` 證明使用 workspace-write；`.git/hooks` 與 worktree 外的寫入都被拒（Access denied）。
    - 曾因 OpenCodex 代理回 429 被限流；維護者調整 OpenCodex 後重試成功。限流期間 relay 記為 rate-limited，不 commit。
    - fresh Opus 審查：ship。
  - **目標範圍**：`SanHsien/agent-relay`（`dispatch.py` 的 codex 路徑）＋ 本機 Codex CLI
  - **具體實作步驟**：
    1. 開工前先確認 OpenCodex 代理與 Codex 額度狀態（SPEC §7 已知限制）。
    2. 以 `--run codex` 寄一張有測試的小工單，確認 codex 在 `workspace-write` 沙箱內能改 worktree。
    3. 確認 relay 代為 commit、閘門與回信正常；遇額度不足時記錄 `runtime auto` 的改派行為。
  - **驗收標準（DoD）**：一封 `--run codex` 派工通過驗收閘門並 commit，回信與 log 證明使用 workspace-write 沙箱；反例：工單要求寫 `.git/hooks` 與 worktree 外的檔案，被沙箱擋下。各實測一次。

- [x] **`T-20261021-09`**｜**[優先級：中]** 並發、花費上限與防重跑
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@f535f11](https://github.com/SanHsien/agent-relay/commit/f535f11)、[@276344b](https://github.com/SanHsien/agent-relay/commit/276344b)、[@35c7556](https://github.com/SanHsien/agent-relay/commit/35c7556)（SPEC 第 15 節），實測見 [docs/evidence/2026-10-21-t09-limits.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t09-limits.md)。
    - 實測：一次寄 5 封、`max_concurrent: 2`，同時最多只有 2 個工人，其餘排隊後依序跑完，5 封都 ok。重複觸發被拒（`already being run`）。
    - 實測順帶發現並修正：多個分頁同時同步 store 會撞 git 鎖。
    - CI 抓到 Linux 上的名額競態（同時跑了 3 個工人），審查也指出同一問題。名額、每日上限、同單持有權改在同一把短鎖內完成「檢查＋寫入」。
    - fresh Opus 審查：fix-first，修正後 ship。
  - **目標範圍**：`SanHsien/agent-relay`（`dispatch.py`、`poller.py`、config `dispatch.max_concurrent`／`daily_limit`）
  - **具體實作步驟**：
    1. 收件端同時執行中的派工超過 `max_concurrent` 時，新信留在 new 等下一輪。
    2. 當日派工數超過 `daily_limit` 時回 deferred。
    3. 同一封信的租約仍有效且 pid 存活時，拒絕再跑。
    4. 回信附每次嘗試的用量（有的話）。
  - **驗收標準（DoD）**：一次寄 5 封、`max_concurrent: 2`，同時最多 2 個工人；重複觸發同一封信不會跑第二次（單元測試＋實測）。

- [x] **`T-20261021-10`**｜**[優先級：中]** `relay status` 總覽與收件端心跳
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@26d4dea](https://github.com/SanHsien/agent-relay/commit/26d4dea)（SPEC 第 16 節），實測見 [docs/evidence/2026-10-21-t10-status.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t10-status.md)。
    - 收件端停 150 秒後，指揮者 `relay status` 顯示「⚠ 心跳逾時」並回傳 exit 8；收件端恢復一輪 `watch` 後，標示消失。
    - 指揮者自己的常駐排程也會寫心跳。fresh Opus 審查：ship。
  - **目標範圍**：`SanHsien/agent-relay`（`cli.py`、`poller.py`、store 新目錄 `hosts/`）
  - **具體實作步驟**：
    1. `watch` 每輪寫心跳 `hosts/<agent>@<host>.json`（時間、版本、執行中工單）。
    2. `relay status` 列出：各信箱 new／cur 封數、執行中租約、逾期工單、超過 N 分鐘沒心跳的收件端。
  - **驗收標準（DoD）**：停掉收件端排程後，指揮者的 `relay status` 標示該收件端心跳逾時；恢復後消失。實測一次。

- [x] **`T-20261021-11`**｜**[優先級：中]** `relay gc` 清理
  - **完成日期**：2026-10-21
  - **實作紀錄 / 證據**：[SanHsien/agent-relay@d209958](https://github.com/SanHsien/agent-relay/commit/d209958)、[@276344b](https://github.com/SanHsien/agent-relay/commit/276344b)、[@35c7556](https://github.com/SanHsien/agent-relay/commit/35c7556)（SPEC 第 17 節），實測見 [docs/evidence/2026-10-21-t11-gc.md](https://github.com/SanHsien/agent-relay/blob/main/docs/evidence/2026-10-21-t11-gc.md)。
    - 前後數量對照：worktree 27→3、本機分支 26→2、run 紀錄 32→2、done 信 36→0。
    - 已驗收的遠端分支被刪，未驗收的 24 個保留；沒有本機紀錄的舊 worktree 不動。
    - 審查後再修兩點：沒推送過的成果預設保留（要加 `--force` 才刪）；重放窗口沒設好時，gc 拒絕執行。
    - fresh Opus 審查：fix-first，修正後 ship。
  - **目標範圍**：`SanHsien/agent-relay`（`cli.py`、`dispatch.py`、`store.py`）
  - **具體實作步驟**：`relay gc --older-than <天>`：
    - 已 accept 或已拒絕的工單：刪 worktree、本機 `relay/<id>` 分支，以及自己推上去的遠端分支。
    - `runs/` 與 done 信件超過保留期就清掉。
    - 預設 dry-run，加 `--apply` 才刪。
    - 執行中、未結案的工單一律不碰。
  - **驗收標準（DoD）**：gc 前後的數量對照；執行中的工單不被刪（單元測試＋實測）。


### 3.1 不執行（維護者 2026-10-21 決定）

- **原第 12 項：真兩台機器端到端實測**：維護者沒有第二台電腦，取得成本高。所有跨機器行為都已在同一台主機的兩份 clone 上實測，包括簽章、回傳、驗收、並發與 gc。尚未涵蓋的差異已寫進 agent-relay SPEC 第 14 節的「測試拓撲限制」：兩台機器時鐘不同步、各自的 git 認證、真實網路延遲與斷線。
- **原第 06 項：MiniMax M3.1 Flash（原 Space Bunny）實測**：維護者不使用 MiniMax 這類中國服務。agent-relay 的基準報告與回流範本已移除 MiniMax 的路由建議，low 層維持 haiku／codex low／agy。

---

## 4. 關聯筆記、會話溯源與相關任務（Related Notes & Sessions）

- **流水線前三階段**：
  - [AI 共同大腦工業級架構規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [Crossroad A2A 跨機器寄信協議](./2026-10-19-crossroad-a2a-agent-mail-relay.md) ｜ 關聯任務：`T-20261019-01`、`T-20261019-02`
  - [跨 CLI 多代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
  - [多 Agent 工廠：Magpie 網關與 Herdr 終端復用](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261018-16`
  - [SpaceX 首席工程師 pstack 方法論](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-18`
