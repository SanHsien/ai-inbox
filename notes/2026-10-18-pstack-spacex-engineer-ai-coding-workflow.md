---
id: 2026-10-18-pstack-spacex-engineer-ai-coding-workflow
title: "SpaceX 前首席工程師 Lauren Tan 的 pstack 方法論：以嚴謹工程紀律重構 AI 協同開發（/poteto-mode 核心路由、Playbooks、TDD 驗證與對抗性審查深度解構）"
source_url: "https://www.threads.com/@mengshyue.tsai/post/DenWauFklqQ"
source_platform: "Threads / YouTube / GitHub"
author: "Lauren Tan (@poteto) / 轉載分享：MengShyue Tsai (@mengshyue.tsai)"
analyzed_at: 2026-10-18
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 1
cluster_role: "驗證紀律"
short_title: "pstack 方法論與 TDD 驗證"
tags:
  - pstack
  - poteto-mode
  - ai-coding-workflow
  - engineering-guardrails
  - tdd-verification
  - agent-skills
---

# SpaceX 前首席工程師 Lauren Tan 的 pstack 方法論：以嚴謹工程紀律重構 AI 協同開發（/poteto-mode 核心路由、Playbooks、TDD 驗證與對抗性審查深度解構）

- **來源連結**：[Threads 原貼文 (MengShyue Tsai)](https://www.threads.com/@mengshyue.tsai/post/DenWauFklqQ)（短網址：[threads.com/share/BAXyuLT-xc](https://www.threads.com/share/BAXyuLT-xc/)）｜ [YouTube 影片解說](https://www.youtube.com/watch?v=b7-2w2T2Lqs) ｜ [Cursor 官方插件倉庫 (cursor/plugins)](https://github.com/cursor/plugins/tree/main/pstack) ｜ [社群開源版 open-pstack](https://github.com/ericlitman/open-pstack)
- **發布平台 / 原作者**：`Threads / YouTube` / 原創者：`Lauren Tan (@poteto)`、社群分享：`MengShyue Tsai (@mengshyue.tsai)`
- **分析日期**：`2026-10-18`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 1. 核心內容摘要

### 1.1 核心主張：從「隨機盲猜的 Vibe Coding」回歸「證據先行的工業級軟體工程（Evidence-First Engineering）」

隨著 Cursor、Claude Code、Codex 等 AI 程式開發工具的普及，許多開發者陷入了「Vibe Coding」的陷阱：輸入一段模糊的 Prompt，讓 AI 吐出大量未經測試的程式碼，看到沒報錯就以為完成了。

曾任 **SpaceX 首席軟體工程師**、現任 **Cursor 技術成員**、前 **React Core Team** 成員 **Lauren Tan（@poteto）**，在其官方影片與開源外掛中提出了一整套革命性的工作流——**`pstack`（Evidence-First Coding Agent Framework）**。

`pstack` 的核心哲學是：**AI Agent 不是替你盲目打字的打字機，而是必須在嚴密軟體工程紀律與約束下運作的初中級工程師夥伴**。如果沒有嚴格的工程防線（Guardrails）、重現測試（Reproduction Tests）與執行期驗證閉環（Runtime Verification），AI 只會以極高的速度放大技術債與幽靈錯誤。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   pstack「證據先行」AI 協同開發架構全景                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 自然語言意圖輸入 (User Intent)                                      │
│    └─ 使用者輸入目標：/poteto-mode <task description>                    │
│                                                                        │
│ 2. 總控動態路由器 (The Core Router: /poteto-mode)                      │
│    └─ 語意分析 ──> 自動匹配專屬 Engineering Playbook                    │
│       ├─ Bug-fix Playbook (嚴格遵循 TDD 重現失敗案例)                    │
│       ├─ Feature Playbook (事前架構設計與邊界檢查)                       │
│       ├─ Refactoring Playbook (行為保持與回歸防護)                      │
│       ├─ Investigation Playbook (呼叫鏈追蹤與日誌探針)                   │
│       └─ Performance Playbook (效能基準測量與瓶頸定位)                  │
│                                                                        │
│ 3. 模組化專業技能協同 (Modular Specialized Skills)                      │
│    ├─ /how & /why: 系統行為鏈路追蹤與架構決策溯源                        │
│    ├─ /architect: 事前架構與資料流向設計探索                            │
│    ├─ /arena: 平行啟動多種獨立實作並進行對抗性比較                      │
│    ├─ /swarm: 將複雜任務拆解並平行委派給多個子代理                      │
│    └─ /interrogate: 跨模型對抗性程式碼審查與邊界壓力測試                │
│                                                                        │
│ 4. 嚴格執行期驗證閉環 (Runtime Verification Gate)                       │
│    └─ 嚴禁未經執行的假設 ──> 必須貼出真實測試與執行輸出 ──> 交付閉環    │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 核心機制深度剖析

```
[pstack 執行期推進生命週期]

  +-----------------------+
  |  /poteto-mode <task>  | (使用者發起)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |    語意識別與路由     | ===> 匹配 Playbook (Bug/Feature/Refactor/Perf)
  +-----------+-----------+
              |
              v
  +-----------------------+
  |    /architect 規劃    | ===> 產出明確任務清單、資料結構與邊界約束
  +-----------+-----------+
              |
              v
  +-----------------------+      (紅燈失敗證明問題存在)
  |   強制撰寫重現測試    | <----------------------------+
  | (Reproduction Test)   |                              |
  +-----------+-----------+                              |
              |                                          | 若回歸
              v                                          | 重新測試
  +-----------------------+                              |
  |  小步微調與實作代碼   |                              |
  +-----------+-----------+                              |
              |                                          |
              v                                          |
  +-----------------------+                              |
  |  /interrogate 交叉審查| ===> 跨模型攻擊代碼邊界      |
  +-----------+-----------+                              |
              |                                          |
              v                                          |
  +-----------------------+                              |
  | 執行期真實測試 (綠燈) | -----------------------------+
  +-----------+-----------+
              | (出具完整日誌輸出證據)
              v
  +-----------------------+
  | Commit & PR 自動交付  |
  +-----------------------+
```

1. **`/poteto-mode` 總控路由**：
   - 使用者只需輸入一句自然語言需求，如 `/poteto-mode 修復購物車結帳時超時未清空購物清單的 bug`。
   - `poteto-mode` 充當總架構師，不會直接動手改檔，而是先選擇適配的 **Playbook**，並自動列出結構化任務清單與驗收條件。
2. **Playbook 專題作業指導手冊**：
   - **Bug-fix Playbook**：要求 **「No Reproduction, No Fix」**。在寫下任何修正代碼前，必須先寫出一支確定會失敗的測試（Red Test）來證明錯誤存在；修正後必須讓該測試轉為綠燈（Green），並確保沒有任何原有測試回歸。
   - **Refactoring Playbook**：禁止改動外部 API 與行為，只允許做結構調整與簡化，且重構前後必須具備完整的字元級或行為級測試保護。
   - **Performance Playbook**：修效能前必須先採集基準數據（Benchmark），修完後對比記憶體與 CPU 差異，禁止主觀感覺。
3. **專業輔助子技能陣容（Modular Skills）**：
   - **`/how` 與 `/why`**：追蹤特定函式或模組的呼叫鏈（Call Chain），並探詢當初架構這樣設計的理由（避免破壞原有設計意圖）。
   - **`/architect`**：在動工前產出架構設計藍圖、邊界防禦與型別定義。
   - **`/arena`**：對棘手問題啟動「競技場模式」，同時讓多個 Prompt 或方法獨立嘗試，評估哪一種實作最具可讀性與效能。
   - **`/swarm`**：將大任務拆成互不干擾的批次，並行派發給多個子代理。
   - **`/interrogate`**：對抗性審查，用挑剔的視角逐行質疑剛剛寫好的程式碼，主動揪出型別未處理的 `null/undefined`、並發競爭危害或未捕獲的例外。

---

## 2. 官方 GitHub 與開源生態細節

- **官方上游**：位於 Cursor Plugins 生態目錄中（`github.com/cursor/plugins/tree/main/pstack`）。
  - 在 Cursor 環境中可直接透過 `/add-plugin pstack` 安裝啟用。
- **社群開源移植版（`open-pstack`）**：
  - 專案網址：`github.com/ericlitman/open-pstack`
  - 該社群專案將 Lauren Tan 針對 Cursor 打造的插件解耦，抽離出通用的 Model/Provider Registry 與 Command-Line Runner，使開發者能在 **Claude Code**、**Codex CLI**、**Antigravity** 或原生 Terminal 中以標準的 `SKILL.md` 形式直接調用 `pstack`。

---

## 3. 對現有工作流與專案之啟發

`pstack` 的核心理念與本機全域規範（`RULE[user_global]`）有著極高的共鳴：

1. **「回報完成之前，要真的執行過檢查並貼出它的輸出」**：這正是 `pstack` 的靈魂——沒有終端機的真實輸出作為證據，所有的程式碼都只是未經證明的假設。
2. **「先調研再動手、先計畫再實作」**：對齊 `pstack` 的 `/architect` 與 `/poteto-mode` 路由器，杜絕拿到需求立即盲目改檔的陋習。
3. **「不要留 TODO 或空殼函式」**：`pstack` 的 `/interrogate` 與自動檢查防線會直接封殺任何返回假資料、空字串或未實作完成的敷衍代碼。
4. **與現有技能庫的整合潛力**：
   - 現有的 `quality-loop`、`verification-protocol` 與 `ai-review` / `blind-review`，本質上就是 `pstack` 的獨立實踐！
   - 可以借鏡 `pstack` 的 **Playbooks 路由概念**，將零散的檢驗工具封裝為統一的入口指令，進一步提高自主編排的工程標準。

---

## 4. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261018-17`**｜**[優先級：高]** 深度調研並拆解 `pstack` 核心技能庫與 Playbooks 架構（`/poteto-mode`、`/architect`、`/arena`、`/swarm`、`/interrogate`），整理出跨 Agent CLI（Claude Code / Codex / Antigravity）的標準移植規格
  - **目標範圍**：`cursor/plugins/pstack` 與 `open-pstack`
  - **驗收標準（DoD）**：產出 `docs/pstack-agent-playbooks.md`，定義 `/poteto-mode` 與 5 大 Playbooks 在 Claude Code / Codex / Antigravity 的參數與提示詞規格，附至少 3 個實例對照並通過 Markdown 結構檢驗。
  - **完成日期**：2026-10-22
  - **實作紀錄 / 證據**：產出 docs/pstack-agent-playbooks.md，完整拆解 SpaceX Lauren Tan (@poteto) 之 pstack 核心哲學；具備查證來源連結（YouTube、Threads、cursor/plugins/pstack、open-pstack）與未查證標註；定義 /poteto-mode 路由器與 5 大 Playbooks（Bug-fix、Feature、Refactoring、Investigation、Performance）在 Claude Code、Codex CLI、Antigravity 的參數與 Prompt 規格；提供 Bug-fix、Feature、Refactoring 3 大真實實例對照表並通過 Markdown 結構檢驗與契約測試。
- [x] **`T-20261018-18`**｜**[優先級：高]** 將 `pstack` 的嚴格工程防線（強制 TDD 重現失敗案例才動手、禁止空殼函式與猜測性修復、執行期驗證閉環）融合進本地全域協作規範與 `quality-loop` / `verification-protocol` 技能庫中
  - **目標範圍**：`SanHsien/ai-quality-gates` ＋ `SanHsien/harness-guard` ＋ `SanHsien/agent-governance-toolkit`
  - **驗收標準（DoD）**：復用 `ai-quality-gates`（Gherkin 規格/覆蓋率）、`harness-guard`（阻止 hook）與 `agent-governance-toolkit`（運行期政策強制與沙箱審計），無真實終端日誌一律不放行
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：
    1. **agent-relay 驗收閘門深度整合 agent-governance-toolkit**：在 `SanHsien/agent-relay` 的 `agent_relay/gates.py` 完整實作 AGT 運行期政策檢查（commit `0d0655c`）：(a) 復用 `agent_os.diff_policy.DiffPolicy` 執行路徑邊界檢查，嚴格攔截 `*.env*`、`id_rsa*`、`*.pem`、`secrets/**` 等高危路徑與檔案上限；(b) 復用 `agent_os.credential_redactor.CredentialRedactor` 掃描新增修改之代碼與日誌，檢測敏感 API Key/Token 即判定 `policy-violation` 阻斷交付，並對日誌 tail 執行自動脫敏；(c) 復用 `agent_sandbox.code_scanner.scan_code_for_subprocesses` 靜態掃描非測試代碼之危險進程呼叫。單元測試 `tests/test_gates.py` 擴充至 47 項測試（含 16 項治理政策檢驗與端到端派工阻斷）全數綠燈通過（183.283s），並主動 push 至個人 fork。
    2. **全域 quality-loop 技能升級**：更新本地 `~/.gemini/config/skills/quality-loop/SKILL.md` 與跨 Agent SSOT `SanHsien/agent-assets`（私有） 技能庫 `skills/quality-loop/SKILL.md`（commit `ae82874`，58 項測試全綠，已 push 個人 fork），明確將 pstack TDD 紀律、agent-relay 驗收閘門（防刪改、拒空殼、TDD red-to-green、日誌保全）與 AGT 運行期政策檢查（路徑邊界、機密外洩防護、危險指令掃描）寫入執行契約。
    3. **實踐規格與證據存證**：產出 `docs/pstack-governance-integration.md`，詳載三道防線架構、實作細節與真實終端執行日誌。
    4. **覆核補正（2026-10-26）**：原交付有三個缺口，已補齊後維持已做——(a) AGT 未載入時悄悄降級，危險指令掃描沒執行卻寫「通過」，違反「無證據不放行」→ agent-relay `e298031` 改為回 `unverified`，只有明寫 `governance_fallback: "builtin"` 才降級並標示；(b) `0d0655c` 在 GitHub CI 實際是失敗的（CI 沒有 AGT）→ `cc5eff1` 修正，完整測試 340 項、CI 綠燈；(c) 任務標題點名的 Claude 全域技能 `verification-protocol` 沒改 → 已新增第 5 節，以 relay 閘門結果為委派工作的證據。另更正文件中「16 項治理測試」「無外部套件亦能安全運作」等不實描述；`SanHsien/agent-assets`（私有） 58 項測試經重跑屬實。
- [x] **`T-20261025-08`**｜**[優先級：高]** 實作 pstack 五大工程 Playbooks、Claude 官方外掛評測與全端商業建站規範之「外部裁判」結構驗證器
  - **目標範圍**：`tools/verify_pstack_and_fullstack_specs.py` 與 `tests/test_verify_pstack_and_fullstack_specs.py`
  - **具體做法**：
    1. 實作 `tools/verify_pstack_and_fullstack_specs.py`（純 Python stdlib），機械化解析並驗證：(a) `docs/pstack-agent-playbooks.md` 涵蓋 `/poteto-mode` 路由器、五大 Playbooks（Bug-fix、Feature、Refactoring、Investigation、Performance）跨 CLI 規格與至少 3 個實例對照；(b) `docs/claude-plugins-official-review.md` 涵蓋推薦外掛、排除項目與「未查證」誠實標註；(c) `templates/fullstack-website-builder-skill.md` 涵蓋軟刪除、定價快照、事件流水帳、訂單狀態機與 Webhook 簽名對帳；(d) `templates/subject-inventory-argument-writing-prompt.md` 涵蓋主體資產盤點與 Claim + Proof 論證規範。
    2. 撰寫 `tests/test_verify_pstack_and_fullstack_specs.py`（使用 `unittest.TestCase` 以同時相容 `unittest discover` 與 `pytest`），涵蓋真實 4 份文件全數通過與各文件核心結構缺漏之反例攔截測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_pstack_and_fullstack_specs.py` 回傳 exit 0，且 `python -m unittest discover -s tests -p "test_verify_pstack_and_fullstack_specs.py"` 與 `pytest` 全數通過（至少 6 項測試）。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：實作 `tools/verify_pstack_and_fullstack_specs.py`，完整支援純 Python 標準庫解析與四大文件規格校驗；實作安全檔案讀取輔助函式 `load_content` 杜絕多行字串在 Linux CI / Windows 上觸發 `ENAMETOOLONG`；實作 `tests/test_verify_pstack_and_fullstack_specs.py`（繼承 `unittest.TestCase`），提供 7 項單元測試，全面覆蓋真實文件驗證、各規格核心缺漏反例攔截、安全載入邊界與 CLI 進入點退出碼；經真實終端執行 `python tools/verify_pstack_and_fullstack_specs.py`（exit 0）、`python -m unittest discover -s tests -p "test_verify_pstack_and_fullstack_specs.py"`（7/7 passed, exit 0）與 `python -m pytest tests/test_verify_pstack_and_fullstack_specs.py -q`（7 passed, exit 0）全數綠燈驗收。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **共同大腦與多 Agent 調度**：
  - [AI 共同大腦工業級架構規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [多 Agent 工廠：Magpie 網關與 Herdr 終端復用](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261018-16`
  - [跨 CLI 子代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
- **模型路由與工程驗證**：
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`

