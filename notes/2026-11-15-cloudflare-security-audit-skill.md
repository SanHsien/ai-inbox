---
id: "2026-11-15-cloudflare-security-audit-skill"
title: "Cloudflare security-audit-skill 解構：用六階段隔離、對抗式證偽與零依賴閘門馴服 LLM 幻覺"
source_url: "https://github.com/cloudflare/security-audit-skill"
source_platform: "GitHub & Social"
author: "Cloudflare Security AI Research（社群解讀：工程師米奇）"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: pending
cluster: 3
cluster_role: "資安稽核Harness"
short_title: "Cloudflare資安稽核Skill"
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
- **當前狀態**：`🔴 未做 (Pending)`

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
  - 官方實測揭露：**單次執行大約只找到「多輪反覆執行加總」所發現漏洞的一半左右**。
  - 核心裁決嚴格分為三類：`confirmed`（完整原始碼追蹤鏈＋可觀察結果）、`needs_validation`（明確卡在特定未解決事實且**不給嚴重度**）、`rejected`（已被證偽）。
  - 嚴重度公式綁定 `likelihood × impact`；若 A 層已阻擋攻擊，缺 B 層僅列為「加固建議（hardening note）」，不計入漏洞。

---

## 2. 原始碼安全與 Windows 11 相容性補充查證

直接檢閱 `skills/security-audit/SKILL.md` 後發現三個貼文未深入、但對實務落地至關重要的設計細節：

1. **寫隔離與防 symlink 競爭條件（Write Isolation）**：
   - `Parent` 是唯一能寫入 `coverage-ledger.json`、`findings.json` 等共用檔的角色；每個 Sub-agent 的 `agent-id` 強制符合 `^[a-z0-9][a-z0-9_-]{0,63}$` 且排除 Windows 保留字（`con`、`prn`、`aux`、`nul`、`com1-9`、`lpt1-9`）。
   - 子代理僅能寫入專屬 `scratch/`；`artifacts/` 由 Parent 保管，晉升（promote）檔案時須透過無跟隨（`no-follow`）目錄描述符逐層驗證常規檔案、link count 為 1 與位元組上限，禁止 glob 複製或解壓縮，防止惡意 repo 透過 symlink 跳脫污染宿主。
2. **OS 級沙盒硬閘門**：執行目標專案建置／測試時，硬性要求無外網、淨空環境變數（僅白名單）、目標唯讀、資源上限；若環境不具備完整 OS 沙盒（例如 Windows 11 原生下未掛載隔離容器），Skill 會自動保守退回，將需要動態執行的線索標為 `needs_validation`，不會硬跑未受保護的目標程式。
3. **兩支零依賴 Node.js 驗證器**：`validate-findings.cjs` 與 `validate-coverage-ledger.cjs`（皆附 `.test.cjs`）無第三方 npm 依賴，只須本機具備 Node.js 即可執行確定性 schema 檢查。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/agent-advisor`（`advisor-pro-reviewer`）：目前審查輸出偏重通過／修補／重想，可吸收 **`needs_validation` 一等公民裁決** 與 **「證偽導向」對抗式審查原則**，降低子代理在證據不足時硬猜結論的機率。
  - `SanHsien/agent-safety-checks` / `harness-guard`：其零依賴驗證器設計與「寫隔離 / 禁止隨意覆寫共用檔」契約，與維護者現有的確定性閘門哲學高度一致。
  - `SanHsien/agent-relay`：支援多輪累加帳本（`coverage-ledger.json`）與隔離工作區的模式，正好適合未來在 `agent-relay` 上執行長週期安全審查派工。
- **落差與採納判斷**：
  - **值得直接採納**：
    1. 直接將 `cloudflare/security-audit-skill`（先經過只讀安全審查與 `.test.cjs` 測試）納入沙盒與測試工具箱，用於個人重要 repo（如 `agent-relay`、`agent-safety-checks`）的 `quick` / 靜態唯讀稽核。
    2. 抽取出 `needs_validation` 三態裁決與「A 層已防禦則缺 B 層只算建議」原則，優化 `agent-advisor` 與 `blind-review` 審查提示詞。
  - **需注意成本與環境限制**：
    - `standard` / `deep` 全套六階段需要多次隔離子代理，token 消耗較高；個人日常開發應以 `guidance` 模式或 `quick` scoped run 為主，重要釋出前才跑完整剖面。
    - Windows 11 原生缺乏 POSIX `O_NOFOLLOW` 語意與完整目標沙盒時，應嚴守其規範只做唯讀原始碼審查（將動態驗證留給 `needs_validation` 或容器／CI 環境）。

---

## 4. 拆解待辦事項（Action Items）

- [ ] **`T-20261115-04`**｜**[優先級：中]** 審查並沙盒實測 `cloudflare/security-audit-skill`（驗證零依賴 `.cjs` 測試與 Windows 11 `quick` 模式靜態稽核）
  - **目標範圍**：`C:\GitHub\_sandbox\security-audit-skill`（先唯讀審查）與個人測試目標 repo（如 `SanHsien/agent-relay` 局部 scoped `quick` 試跑）
  - **具體做法**：
    1. 檢視 `validate-findings.cjs`、`validate-coverage-ledger.cjs` 與兩份 `.test.cjs` 原始碼，確認無任何外部連線、提權或 Hook 偷跑風險後，於 Windows 11 原生環境跑通兩支 `.test.cjs` 單元測試。
    2. 挑選單一小型個人 repo 範圍，以 `quick` + 唯讀靜態模式試跑一次（輸出導向 repo 外部暫存目錄），驗證 `coverage-ledger.json`、`findings.json` 與 `REPORT.md` 產出品質與 token 成本。
    3. 依實測結果決定是否安裝至全域 Skill 目錄（`~/.gemini/config/skills/` 或 `~/.claude/skills/`）。
  - **驗收標準（DoD）**：兩支 `.test.cjs` 測試於 Windows 11 實測全綠，並產出一份含 `coverage-ledger.json`、`findings.json` 與 `validate-findings.cjs` 通過輸出的實測紀錄。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*

- [ ] **`T-20261115-05`**｜**[優先級：低]** 評估將 `needs_validation` 三態裁決與「證偽導向」對抗式檢查精神整合至 `SanHsien/agent-advisor` 審查協定
  - **目標範圍**：`C:\GitHub\agent-advisor`（`advisor-pro-reviewer` 與相關審查參考文件）
  - **具體做法**：
    1. 檢視現有 `advisor-pro-reviewer` 與 `blind-review` 輸出格式，評估加入「當證據鏈卡在特定未解決事即時，標註 `needs_validation` 並寫出確切缺失事實，禁止硬猜嚴重度或通過」規則。
    2. 明確區分「邊界失效（Blocking Defect）」與「防禦縱深建議（Hardening Note）」，避免審查報告被低價值理論警告淹沒。
  - **驗收標準（DoD）**：完成 `agent-advisor` 對應規則更新，通過該 repo 既有檢核測試並推送至 `SanHsien/agent-advisor`。
  - **完成日期**：*（完成時填 YYYY-MM-DD）*
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫 Commit / PR / 驗證輸出摘要）*
