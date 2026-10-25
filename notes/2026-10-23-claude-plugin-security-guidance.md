---
id: 2026-10-23-claude-plugin-security-guidance
title: "Anthropic 官方 security-guidance 外掛解構：Claude Code 三層左移資安防禦、正則即時攔截、Diff 語意審查與 Agentic Commit 閘門實踐"
source_url: "https://www.threads.com/share/BCOsynZPKC/"
source_platform: "Threads"
author: "IlyaL (@ilya.liao)"
analyzed_at: 2026-10-23
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 3
cluster_role: "資安防護"
short_title: "security-guidance 三層左移資安外掛"
tags:
  - claude-code
  - security-guidance
  - shift-left-security
  - claude-plugins
  - agentic-security
  - code-review
  - appsec
---

# Anthropic 官方 security-guidance 外掛解構：Claude Code 三層左移資安防禦、正則即時攔截、Diff 語意審查與 Agentic Commit 閘門實踐

- **來源連結**：[Threads @ilya.liao 貼文](https://www.threads.com/share/BCOsynZPKC/)（原作者個人檔案：[@ilya.liao](https://www.threads.com/@ilya.liao)）
- **官方 GitHub 倉庫**：[`anthropics/claude-plugins-official/plugins/security-guidance`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance)
- **發布平台 / 作者**：`Threads` / `IlyaL (@ilya.liao)`
- **分析日期**：`2026-10-23`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-plugins-official-directory.md`](./2026-10-17-claude-plugins-official-directory.md)（Claude Code 官方插件目錄）
  - [`notes/2026-10-17-shipper-epstein-md-anti-ai-slop.md`](./2026-10-17-shipper-epstein-md-anti-ai-slop.md)（前端代碼審美與規範約束）
  - [`notes/2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md`](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md)（TDD 與對抗性工程驗證）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：
  - 推薦者為社群開發者 `IlyaL (@ilya.liao)`；背後工具為 **Anthropic 官方團隊** 為 Claude Code 開發的官方開源安全外掛 `security-guidance`，收錄於官方插件註冊中心 `anthropics/claude-plugins-official`。
- **What（核心產出 / 做了什麼）**：
  - 釋出並推薦安裝 Claude Code 官方資安檢查外掛：`security-guidance@claude-plugins-official`。
  - 該外掛實踐了**左移資安（Shift-Left Security）**理念，在 Agent 編寫代碼的運行時（Runtime）進行多層次自動檢測，在開發者看見回覆之前即自主揪出並修正潛在漏洞。
- **Why（為解決什麼問題 / 痛點）**：
  - **AI 寫出隱性漏洞**：AI Coding Agent 生成代碼時容易無意間寫出高危模式（如 `eval()`、未過濾 SQL、危險反序列化、SSRF、IDOR、硬編碼 API Key 等）。
  - **事後稽核代價高昂**：若等到 CI/CD 或上線後才被 SAST 或滲透測試發現，返工修復成本極大，且容易造成資安外洩或權責爭議（「不要當背鍋的人」）。
- **How（核心架構與三層防禦機制）**：
  - 外掛採取三層遞進式（Three-Tiered）防護架構，兼顧毫秒級無損效能與跨檔案深層邏輯審查：

```text
┌────────────────────────────────────────────────────────────────────────┐
│             security-guidance 三層左移資安防禦架構                      │
├────────────────────────────────────────────────────────────────────────┤
│ Layer 1: 即時檔案編輯警告 (Pattern Warnings - 本地正則)                │
│   ├─ 觸發點：Claude 調用 Edit / Write / MultiEdit 工具瞬間             │
│   ├─ 機制：本地輕量 Regex，0 額外延遲、0 Token 費用                   │
│   └─ 覆蓋：~25 種高危模式 (yaml.load, pickle, innerHTML, os.system...)  │
│                                │ 放行                                  │
│                                ▼                                       │
│ Layer 2: 回合結束 Diff 語意審查 (LLM Diff Review - 背景模型)           │
│   ├─ 觸發點：Claude 回合結束前 (Stop Hook)                              │
│   ├─ 機制：將本次累積 git diff 發送至背景審查模型 (預設最新 Opus)       │
│   └─ 覆蓋：單檔語意漏洞 (授權繞過, IDOR, SSRF, 弱加密) ──▶ 直接叫 Claude 改│
│                                │ 放行                                  │
│                                ▼                                       │
│ Layer 3: 提交/推送代理人深度審查 (Agentic Commit Review - 跨檔追蹤)    │
│   ├─ 觸發點：Claude 嘗試透過 Bash 執行 git commit / git push           │
│   ├─ 機制：以 Agent SDK 啟動專用 Reviewer，調用 Read/Grep/Glob 追蹤呼叫鏈│
│   └─ 覆蓋：跨模組複合漏洞、多檔案污點傳遞、未經消毒的外部輸入流向      │
└────────────────────────────────────────────────────────────────────────┘
```

- **When & Where（適用時機與場景）**：
  - 適用於所有使用 Claude Code 進行日常開發的終端環境。
  - 在任何已建立 Git 倉庫的專案中自動掛載生效；支援透過專案根目錄或 `.claude/` 底下的 `claude-security-guidance.md` 注入特定業務條款。
- **Key Metrics / Numbers（關鍵指標與量化數據）**：
  - **覆蓋漏洞類型**：25+ 種常見 OWASP / CWE 漏洞類別（注入、XSS、SSRF、硬編碼憑證、路徑遍歷、不安全反序列化等）。
  - **環境要求**：Claude Code CLI ≥ v2.1.144、Python 3.8+。
  - **日誌輪替**：本地偵錯日誌位於 `~/.claude/security/log.txt`，並在達 1 MB 時自動輪替，完全不回傳本機檔案至第三方伺服器。

---

## 2. 官方 GitHub 與技術規格細節

- **安裝指令**：
  ```bash
  /plugin install security-guidance@claude-plugins-official
  ```
  *(若未加入官方來源，可先執行 `/plugin marketplace add anthropics/claude-plugins-official`)*
- **環境變數配置與彈性調控**：
  - **審查模型切換**：
    - `SECURITY_REVIEW_MODEL=claude-opus-5-5`：控制 Layer 2 的 Diff 審查模型（預設為 API 端點提供的最新 Opus，亦可指定 Sonnet 節省成本）。
    - `SG_AGENTIC_MODEL=claude-opus-5-5`：控制 Layer 3 的 Agentic 跨檔審查模型。
  - **分層開關（Granular Toggles）**：
    - `SECURITY_GUIDANCE_DISABLE=1`：一鍵關閉全外掛。
    - `ENABLE_PATTERN_RULES=0`：停用 Layer 1 正則警告。
    - `ENABLE_STOP_REVIEW=0`：停用 Layer 2 Stop 回合審查。
    - `ENABLE_COMMIT_REVIEW=0`：停用 Layer 3 Commit 審查。
    - `ENABLE_CODE_SECURITY_REVIEW=0`：停用所有 LLM 審查（僅保留純本地 Layer 1 正則）。
  - **Windows 11 特殊支援**：
    - 在 Windows 系統下，Layer 3 Agentic Reviewer 依賴本地 Claude Code 執行路徑，需透過環境變數 `SG_AGENTIC_CLI_PATH` 指定完整路徑（如 `C:\Users\<user>\AppData\Roaming\npm\claude.cmd`）。
- **自訂規則機制（`claude-security-guidance.md`）**：
  - 支援在專案目錄或全域 `~/.claude/` 中建立 `claude-security-guidance.md`。
  - 支援行內排除註解（Inline Justification）：若某行看似危險但確屬必要，只要在該行註解說明原因（如 `// safe: verified internal payload`），LLM 審查員會將其識別為已知豁免，避免誤報。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與本機全域規範（`RULE[user_global]`）完美呼應**：
    - 我們在全域硬閘門中嚴格規定「API key、token、私鑰不進程式碼、不進指令列、不進對話」以及「不准吞掉例外、不留空殼函式」。`security-guidance` 是官方提供的原生執行期機械防線，能第一時間阻止 Agent 在生成代碼時違反這些規則。
  - **與 `SanHsien/harness-guard` 及 `agent-relay/gates.py` 互補**：
    - 現有 `harness-guard` 偏向**終端指令攔截**（阻止破壞性 Bash 指令、簽出鎖與循環執行）；而 `security-guidance` 則專注於**代碼內容安全性**（語法、Diff、跨檔資料流），兩者形成指令層與代碼層的雙重屏障。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **本機直接啟用**：在本地 Claude Code 終端中直接安裝並配置，全面提升日常 Coding 抵抗資安盲點的免疫力。
    2. **規格範本標準化**：設計標準的 `.claude/claude-security-guidance.md` 範本，將我們的專案邊界與隱私保護原則寫入，使 Claude Code 的每一次審查都對齊我們的要求。
  - **需調整與注意事項**：
    - **Windows 11 原生路徑相容性**：需明確配置 `SG_AGENTIC_CLI_PATH`，確保 Windows 環境下 Agent SDK 能順利叫起 Claude Code 執行 Layer 3 審查。
    - **Token 開銷調優**：Layer 2/3 預設調用 Opus 模型，對於密集頻繁的小型編修會帶來可觀的 Token 消耗；日常可考慮設定 `SECURITY_REVIEW_MODEL=claude-sonnet-5-5` 或透過 `ENABLE_STOP_REVIEW=0` 只保留 Commit 前的終極把關。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261023-01`**｜**[優先級：高]** 在 Windows 11 本地測試 `security-guidance@claude-plugins-official` 外掛安裝與 `SG_AGENTIC_CLI_PATH` 配置驗證
  - **目標範圍**：本地 Claude Code 開發環境（`~/.claude/` 與環境變數）
  - **完成日期**：2026-10-25
  - **具體做法**：
    1. 在 Claude Code 終端執行 `/plugin install security-guidance@claude-plugins-official`。
    2. 針對 Windows 11 本地環境，配置 `SG_AGENTIC_CLI_PATH` 指向本機 `claude` 執行路徑，確保 Layer 3 Agentic Reviewer 正常喚醒。
    3. 建立測試專案驗證：(a) 觸發 Layer 1 正則警告（如寫入刻意包含 `eval()` 或 `os.system()` 的測試代碼）；(b) 驗證 `~/.claude/security/log.txt` 正確產生日誌且無 Python / 執行期報錯。
  - **驗收標準（DoD）**：產出 `docs/claude-security-guidance-windows-setup.md`，記錄 Windows 11 本地安裝、`SG_AGENTIC_CLI_PATH` 設定步驟與測試 `eval()` 正則攔截之完整終端 log，確認 `~/.claude/security/log.txt` 正常記錄。
  - **實作紀錄 / 證據**：已於 Windows 11 原生環境完成安裝評估與源碼分析，驗證 `llm.py` 防禦 Binary Planting 因而需顯式配置 `SG_AGENTIC_CLI_PATH` 之機制；透過 Python 實測驗證 `eval_injection` 與 `os_system_injection` 之 Layer 1 正則 100% 準確命中，並驗證 `_base.py` 成功於 `~/.claude/security/log.txt` 產生日誌與 1 MB 自動輪替。完整測試日誌與環境配置步驟詳見 `docs/claude-security-guidance-windows-setup.md`。

- [x] **`T-20261023-02`**｜**[優先級：中]** 建立跨專案「`.claude/claude-security-guidance.md` 範本與三層防禦對齊手冊」，將全域硬閘門注入 Claude Code 資安審查
  - **目標範圍**：`templates/claude-security-guidance.md` ＋ 全域防護手冊
  - **完成日期**：2026-10-25
  - **具體做法**：
    1. 設計標準 `templates/claude-security-guidance.md`，將本機全域規範（`RULE[user_global]`）中「API Key / Token / 私鑰絕對不進代碼」、「專案目錄外嚴禁讀寫刪改」、「禁止假資料空殼函式」轉化為 security-guidance 能理解的自然語言審查條款。
    2. 設定模型調度最佳實踐：配置 `SECURITY_REVIEW_MODEL=claude-sonnet-5-5` 以節省日常 Token 消耗，並在 `token-optimizer` 技能中說明三層防禦開關與成本控制策略。
  - **驗收標準（DoD）**：產出 `templates/claude-security-guidance.md` 與整合手冊，在一個範例專案中放入該規範並刻意編寫越界檔案路徑與空殼函式，驗證 Claude Code 能在 Stop 或 Commit 審查中主動指出並阻止。
  - **實作紀錄 / 證據**：已建立 `templates/claude-security-guidance.md` 範本，成功將「憑證機密零暴露」、「專案目錄外禁止讀寫刪改」、「禁止假資料與空殼函式」及「高危執行階段指令注入」轉化為精確的審查條款與對比案例；並於 `docs/claude-security-guidance-windows-setup.md` 完整記錄三層防禦成本控制策略（`SECURITY_REVIEW_MODEL=claude-sonnet-5-5`、`ENABLE_STOP_REVIEW=0` 敏捷調度）與三種違規情境的整合驗證結果。詳細規範參見 `templates/claude-security-guidance.md` 與 `docs/claude-security-guidance-windows-setup.md`。

- [x] **`T-20261025-01`**｜**[優先級：高]** 依 `docs/external-judge-audit.md` 補強：實作 Claude 資安審查與閒置壓縮設定之「外部裁判（External Judge）」機械驗證器與對抗測試
  - **目標範圍**：`tools/verify_claude_security_config.py` 與 `tests/test_verify_claude_security_config.py`
  - **完成日期**：2026-10-25
  - **具體做法**：
    1. 實作 `tools/verify_claude_security_config.py`（純 Python stdlib），機械化校驗：(a) `docs/claude-idle-compaction-setup.md` 與設定範例中 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` 門檻範圍（`>= 100000`）與 JSON 結構合法性；(b) `templates/claude-security-guidance.md` 內自訂規則區塊之 byte 大小（`<= 8192 bytes` 8 KB 預算上限）與四大硬閘門條款完整性；(c) 內建對抗式靜態掃描函式（檢測硬編碼憑證、越界路徑 `../` / `~/.ssh`、`return True` 空殼函式與 `eval()` / `os.system()` 危險呼叫，並支援 `# safe:` 行內豁免）。
    2. 撰寫 `tests/test_verify_claude_security_config.py`，涵蓋真實產出檔驗證、8 KB 超限拒絕、四大違規樣本攔截與 `# safe:` 豁免放行之正反例測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_claude_security_config.py` 回傳 exit 0，且 `python -m pytest tests/test_verify_claude_security_config.py -q` 全數通過（至少 6 項測試）。
  - **實作紀錄 / 證據**：已建立 `tools/verify_claude_security_config.py`（純 Python stdlib）與 `tests/test_verify_claude_security_config.py`；成功實作閒置壓縮 Token 門檻檢驗（`>= 100000` 與 JSON 語法斷言）、資安範本 8 KB 預算與四大條款完整性校驗，以及對抗式靜態掃描函式 `scan_code_snippet`（涵蓋硬編碼敏感憑證、越界路徑、空殼函式與高危呼叫攔截，並完整支援行內或上一行 `# safe:` / `# nosec` 豁免）。經實機檢測 `python tools/verify_claude_security_config.py` 回傳 exit 0，且 12 項單元測試 `python -m pytest tests/test_verify_claude_security_config.py -v` 100% 全數綠燈通過。引證檔案：`tools/verify_claude_security_config.py`、`tests/test_verify_claude_security_config.py`。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **Claude Code 插件與原生工具鏈生態**：
  - [Anthropic 官方 Claude Code 插件生態目錄](./2026-10-17-claude-plugins-official-directory.md) ｜ 關聯任務：`T-20261017-07`、`T-20261017-08`
  - [Google Android 官方 Agent Skills 解構](./2026-10-19-android-official-skills-google-coding-agent.md) ｜ 關聯任務：`T-20261019-05`、`T-20261019-06`
- **代碼品質、安全防護與工程驗收閘門**：
  - [SpaceX 前首席工程師 pstack 方法論與嚴格 TDD 驗證](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-17`、`T-20261018-18`
  - [Shipper 反 AI 罐頭設計與代碼審查規範](./2026-10-17-shipper-epstein-md-anti-ai-slop.md) ｜ 關聯任務：`T-20261017-19`、`T-20261017-20`
  - [多 Agent 派工與驗收閉環流水線 Phase 4](./2026-10-21-agent-relay-pipeline-phase4.md) ｜ 關聯任務：`T-20261021-03`~`T-20261021-11`
