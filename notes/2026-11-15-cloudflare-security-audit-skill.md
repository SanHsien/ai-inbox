---
id: "2026-11-15-cloudflare-security-audit-skill"
title: "Cloudflare security-audit-skill 解構：用六階段隔離、對抗式證偽與零依賴閘門馴服 LLM 幻覺"
source_url: "https://github.com/cloudflare/security-audit-skill"
source_platform: "GitHub & Social"
author: "Cloudflare Security AI Research（社群解讀：工程師米奇）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
cluster: 3
cluster_role: "資安稽核Harness"
short_title: "Cloudflare資安稽核Skill"
source_reviewed_at: 2026-11-17
source_review: partial
source_review_note: "社群解讀貼文（工程師米奇）沒有留下連結，找不到，圖與留言沒看到；repo 有 47 則未關閉 issue，只讀了前 25 則的標題與其中 4 則全文（讀到 4／共 47 則）"
source_images: 1
source_replies: 4
tags:
  - security-audit
  - cloudflare
  - harness-engineering
  - adversarial-validation
  - zero-dependency-gates
  - sandbox
---

# Cloudflare security-audit-skill 解構：用六階段隔離、對抗式證偽與零依賴閘門馴服 LLM 幻覺

- **來源連結**：[cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) ｜ [Cloudflare Engineering Blog: Build your own vulnerability harness](https://blog.cloudflare.com/build-your-own-vulnerability-harness)
- **發布平台 / 作者**：`GitHub` / `Cloudflare Security AI Research`（查證數據：MIT License、72,408 stars、最後更新 2026-09-14）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-17 用瀏覽器重看 GitHub repo、issue 列表與 Cloudflare 部落格。社群解讀貼文（工程師米奇）沒有留下連結，找不到，那篇的圖與留言**沒看到**。

- **作者圖片**：
  - repo README：沒有圖片。
  - Cloudflare 部落格（2026-06-18，作者 Dan Jones、Alexandra Godoi、Grant Bourzikas）：只有 1 張題圖，是機器人拿放大鏡檢查畫面的插畫，沒有資訊量。文中沒有架構圖。
- **作者留言補充**：無。讀到的 4 則 issue 都沒有維護者回覆。
- **網友留言重點**（GitHub issue，47 則未關閉、82 個未合併 PR；讀了前 25 則標題與 4 則全文）：
  - **#117 兩支驗證器在 Windows 完全不能用**：`O_NOFOLLOW`、`O_NONBLOCK` 在 win32 是 undefined，`readFileWithinLimit()` 一律丟錯；回報者在 Windows 11 實測兩支 CLI 都結束碼 1，`validate-findings.test.cjs` 34 項有 7 項失敗。第 4 階段把驗證器當硬閘門，所以 Windows 上的 full audit 走不完。
  - **#128 代理照 SKILL.md 做，把真實使用者設定檔清空**：Windows 11、沒有 OS 沙盒；代理為了滿足「空環境、scratch 內的 HOME」的要求，沒有另建目錄，而是直接清掉真實家目錄，刪掉代理設定、已裝 skills、SSH 金鑰、對話紀錄與系統 Python，不進回收筒。回報者指出 SKILL.md 只寫要隔離、沒給機制，也沒有 fail-closed 的環境檢查。
  - **#144 SkillSpector 把這個 skill 自己判成 100 分 CRITICAL／DO_NOT_INSTALL**：14 項全是攻擊類別說明與驗證器測試資料被關鍵字規則命中，回報者逐行看過認為是誤報。
  - **#134 捏造的 finding 也能通過驗證**：`trace[]`、`evidence[]` 只有檔名、行號與自由文字，驗證器只查結構；回報者拿不相干的檔案行號宣稱 SQL injection，零錯誤通過。
  - 其他標題：#114（65 個 PR、42 天沒有合併任何一個）、#152 與 #112（兩份獨立稽核，其中一份針對 commit `c1c8a8c`）、#148、#94（目標 repo 可控制輸出路徑）。
- **對分析的影響**：
  - **#117 用實測證實**了 [`docs/cloudflare-security-audit-readonly-review.md`](../docs/cloudflare-security-audit-readonly-review.md) 靜態讀碼得到的 Windows 限制，產出檔不用改。
  - **#128 是新的、更嚴重的風險**：原筆記只寫「缺 OS 沙盒就不跑目標程式」，沒想到代理會把「準備乾淨環境」做成清空真實家目錄。已寫進第 3 節「需注意成本與環境限制」。這是不在 Windows 原生啟動 full audit 的直接理由。
  - #134 補強第 2 節第 3 點：驗證器通過不代表 finding 是真的。已補一句。
  - #144 提醒本機的採納檢查（SkillSpector、`--pack` 掃描）對這類資安教材型 skill 會大量誤報，判讀時要逐項看。
  - #114 顯示上游 PR 幾乎沒在合併，#117、#128 短期內不一定會修。
  - `T-20261115-04`「暫不採納動態執行」的結論更站得住；`T-20261115-05` 不受影響。stars 數本輪未重查。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：Cloudflare Security AI Research 團隊開源，為其內部「跨機隊漏洞探勘 Harness」最初的單一 repo 種子版本。
- **What（核心產出 / 做了什麼）**：一套以 Agent Skill + Companion 攻擊指南 + JSON Schema + 零依賴 Node.js 驗證器構成的資安稽核流水線（預設 guidance 模式，明確要求全庫稽核才進入 full audit 模式）。
- **Why（為解決什麼問題 / 痛點）**：單一 LLM 做資安稽核容易陷入「自己發現、自己確認」的幻覺迴圈，或在資訊不足時被逼二選一（導致大量誤報或漏報），以及產生偏離 checklist 的低品質理論告警。
- **How（核心架構與關鍵機制）**：

```text
[1. Reconnaissance] ─▶ architecture.md + coverage-ledger.json (+ validate-coverage-ledger.cjs)
         │
         ▼
[2. Coverage-led Hunting] ─▶ 依帳本切分隔離 Hunter + Coverage Critic 補洞
         │
         ▼
[3. Candidate Validation] ─▶ 全新 Verifier「以證偽（推翻）為目標」獨立驗證
         │
         ▼
[4. Structured Output] ─▶ findings.json (confirmed / needs_validation / rejected)
         │                 (+ report-schema.json + validate-findings.cjs)
         ▼
[5. Independent Record Verification] ─▶ 全新 Agent 複核原始碼宣稱；實質替換須再經獨立 Verifier
         │
         ▼
[6. Target-Neutral Reporting] ─▶ REPORT.md / FINDINGS-DETAIL.md / NEEDS-VALIDATION.md
```

- **When & Where（適用時機與場景）**：
  - 提供三種執行剖面：`quick`（單波獵殺 + 單次覆蓋審查，但**不放寬證據門檻**）、`standard`（完整六階段）、`deep`（高風險專案，多波補洞且第 3 與第 5 階段嚴格分離獨立 Agent）。
  - **多輪累加**：可讀取既有 `coverage-ledger.json` 與 `findings.json`，僅重驗變更原始碼與未覆蓋單元，適合分批推進。
  - **13 份專門領域指南**（已查證倉庫目錄）：含 `AI-AND-LLM.md`、`SUPPLY-CHAIN-AND-RELEASE.md`、`DESKTOP-MOBILE-AND-LOCAL-IPC.md`、`WEB-PROTOCOL-AND-AUTH.md`、`CLIENT-SIDE.md`、`CLOUD-AND-DEPLOYMENT.md`、`PROTOCOLS-RPC-AND-MESSAGING.md`、`RESOURCE-EXHAUSTION-AND-AVAILABILITY.md`、`DATA-ISOLATION-AND-LIFECYCLE.md`、`MEMORY-SAFETY-AND-BINARY.md` 等。
- **Key Metrics / Numbers（關鍵指標與量化數據）**：
  - [Cloudflare 部落格](https://blog.cloudflare.com/build-your-own-vulnerability-harness/)的經驗敘述：單次執行大約只找到「多輪反覆執行加總」所發現漏洞的一半左右。這是作者團隊的觀察，不是通用召回率，也不是受控 benchmark。
  - 核心裁決嚴格分為三類：`confirmed`（完整原始碼追蹤鏈＋可觀察結果）、`needs_validation`（明確卡在特定未解決事實且**不給嚴重度**）、`rejected`（已被證偽）。
  - 嚴重度公式綁定 `likelihood × impact`；若 A 層已阻擋攻擊，缺 B 層僅列為「加固建議（hardening note）」，不計入漏洞。

---

## 2. 原始碼安全與 Windows 11 相容性補充查證

直接檢閱 `skills/security-audit/SKILL.md` 後發現三個貼文未深入、但對實務落地至關重要的設計細節：

1. **寫隔離與防 symlink 競爭條件（Write Isolation）**：
   - `Parent` 是唯一能寫入 `coverage-ledger.json`、`findings.json` 等共用檔的角色；每個 Sub-agent 的 `agent-id` 強制符合 `^[a-z0-9][a-z0-9_-]{0,63}$` 且排除 Windows 保留字（`con`、`prn`、`aux`、`nul`、`com1-9`、`lpt1-9`）。
   - 子代理僅能寫入專屬 `scratch/`；`artifacts/` 由 Parent 保管，晉升（promote）檔案時須透過無跟隨（`no-follow`）目錄描述符逐層驗證常規檔案、link count 為 1 與位元組上限，禁止 glob 複製或解壓縮，防止惡意 repo 透過 symlink 跳脫污染宿主。
2. **OS 級沙盒是提示詞要求，不是程式強制**：[`SKILL.md`](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md) 要求執行目標專案建置／測試時無外網、淨空環境變數（僅白名單）、目標唯讀、資源上限；缺完整 OS 沙盒（例如 Windows 11 原生下未掛載隔離容器）就不跑目標程式，把需要動態執行的線索標為 `needs_validation`。這靠執行者照做，Skill 本身不提供 Windows 的 OS 隔離；JSON 驗證器只檢查報告結構，不能證明底層程序真的沒連網、沒越權。
3. **兩支零依賴 Node.js 驗證器**：`validate-findings.cjs` 與 `validate-coverage-ledger.cjs`（皆附 `.test.cjs`）無第三方 npm 依賴，在 POSIX 系統只須具備 Node.js 即可執行確定性 schema 檢查；**在 Windows 原生完全不能用**（缺 `O_NOFOLLOW`／`O_NONBLOCK`，[issue #117](https://github.com/cloudflare/security-audit-skill/issues/117) 有實測）。驗證器只查結構，捏造的 finding 也能通過（[issue #134](https://github.com/cloudflare/security-audit-skill/issues/134)）。它們仍是待審的外部程式，不因為零依賴就直接執行。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/agent-advisor`：現行 Codex 審查的最終裁決是 ship／fix-first／rethink 三種。可以在個別 finding 層記錄「證據不足、待驗證」並採用**「證偽導向」對抗式審查原則**，降低子代理在證據不足時硬猜結論的機率；但 `needs_validation` 是 finding 狀態，不能混成第四種最終裁決。（原稿寫的 `advisor-pro-reviewer` 對應哪個平台、哪個檔案，未查證。）
  - `SanHsien/agent-safety-checks` / `harness-guard`：其零依賴驗證器設計與「寫隔離 / 禁止隨意覆寫共用檔」契約，與維護者現有的確定性閘門哲學高度一致。
  - `SanHsien/agent-relay`：支援多輪累加帳本（`coverage-ledger.json`）與隔離工作區的模式，正好適合未來在 `agent-relay` 上執行長週期安全審查派工。
- **落差與採納判斷**：
  - **值得直接採納**：
    1. 先對 `cloudflare/security-audit-skill` 做唯讀審查（見 `T-20261115-04`），審查通過、補齊 OS 隔離前不執行它的 `.cjs`／測試，也不安裝。
    2. 把「finding 可標待驗證」與「A 層已防禦則缺 B 層只算建議」兩個原則補進 `agent-advisor` 審查契約（見 `T-20261115-05`）。
  - **需注意成本與環境限制**：
    - `quick` 不是便宜的單代理靜態模式：`SKILL.md` 有 budget gate，完整審查至少預留四次 reconnaissance、coverage critic 與 verifier，獵殺另計；`quick` 只是縮減廣度。`standard` / `deep` 更高。個人日常開發以 `guidance` 模式為主，要跑完整審查先估代理呼叫預算。
    - Windows 11 原生缺乏 POSIX `O_NOFOLLOW` 語意與完整目標沙盒時，應嚴守其規範只做唯讀原始碼審查（將動態驗證留給 `needs_validation` 或容器／CI 環境）。
    - **已有人在 Windows 11 上出事**：[issue #128](https://github.com/cloudflare/security-audit-skill/issues/128) 回報，沒有 OS 沙盒時，代理為了照 `SKILL.md` 準備「空環境與 scratch 內的 HOME」，直接清空了真實家目錄（代理設定、已裝 skills、SSH 金鑰、系統 Python），不進回收筒。`SKILL.md` 只有文字要求，沒有 fail-closed 的環境檢查。在 Windows 原生不要啟動 full audit。

---

## 4. 拆解待辦事項（Action Items）

- [x] **`T-20261115-04`**｜**[優先級：中]** 唯讀審查 Cloudflare security-audit-skill 的執行契約與成本，訂出 Windows 可採用的最小範圍
  - **目標範圍**：`SanHsien/ai-inbox` 的 `docs/cloudflare-security-audit-readonly-review.md`。
  - **具體做法**：固定 commit，閱讀 SKILL、companions、schema、兩支 validator 與對應測試的程式碼，記錄輸入輸出、外連／子程序／寫檔與依賴；區分提示詞規範和可執行安全控制。計算 guidance 與 quick／standard 的最低代理呼叫預算，對照 Windows 已知隔離缺口。只閱讀，禁止執行下載的 cjs／測試、啟動多模型稽核或安裝全域 Skill。
  - **驗收標準（DoD）**：上述報告包含固定來源、檔案清冊、已查／未查表、最低成本估計、不能強制的沙盒限制、needs_validation 的正確用法，以及可採納／暫不採納結論。動態測試計畫另列所需 OS 控制與未來安全審批前提，不能把計畫寫成通過證據。通過 repo 文件檢查。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/cloudflare-security-audit-readonly-review.md，固定 cloudflare/security-audit-skill c1c8a8c。含檔案清冊 C1–C9；最低代理預算 quick 6、standard 7（SKILL.md:123）；Windows 不能強制的沙盒限制；needs_validation 只用在 finding 層；動態測試前提；結論暫不採納動態執行。唯讀評估，Codex 撰寫，整合者重產索引並補驗證段；Fable 獨立複審抽查來源事實全部吻合；未執行任何第三方程式。

- [x] **`T-20261115-05`**｜**[優先級：低]** 在 agent-advisor 的 Codex 審查契約補上證據缺口與防禦縱深的區分，保留既有三種最終裁決
  - **目標範圍**：`SanHsien/agent-advisor` 的 `codex/plugins/agent-advisor-codex/` 現行 reviewer 契約／參考文件與對應測試；新增 `docs/reviewer-evidence-gap-contract.md` 記錄修改檔案及驗收。
  - **具體做法**：先讀目標 repo 指引並定位實際 reviewer 契約，若已有等價規則則補驗收證據、不重造。將證據不足記為 finding 的待驗證狀態，列缺失事實與最小驗證方式；最終 verdict 維持 ship／fix-first／rethink，不讓未知變成安全通過。將已被另一層阻擋、無可證明影響的情況列加固建議。不得順便改模型路由、安裝或修改其他 agent 的全域 Skill。
  - **驗收標準（DoD）**：上述文件列確切修改路徑與 diff；用至少三個固定案例驗證：有可重現邊界缺陷、決定性事實未知、只有防禦縱深建議。檢核未知不會冒充已證實漏洞或無條件 ship；三 verdict 與既有解析／測試契約保持相容。執行目標 repo 相關測試與要求的文件檢核，證據綁定 commit。只推 `SanHsien/agent-advisor`。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：SanHsien/agent-advisor 9f7a53c、cecaf62（main，CI 綠燈）。Codex reviewer 契約把證據不足標為 finding 層的 needs_validation，防禦縱深標 hardening；最終 verdict 仍只有 ship／fix-first／rethink；只有 needs_validation 的 fix-first 須交新的 fresh reviewer 重判，主代理不可自驗後回報完成。docs/reviewer-evidence-gap-contract.md 有四個固定案例。Fable 獨立複審兩輪，第二輪通過：6 個 mutation 中 5 個被測試抓到，存活的同義改寫屬字串型契約測試的已知限制。dev_check 沙盒外 PASSED（76 tests）。其他平台是否同步已列入 agent-advisor ROADMAP。
