---
id: 2026-10-17-cross-cli-subagent-orchestration-space-bunny
title: "跨 CLI 多代理外包編排實踐：以 Opus 擔任規劃顧問、外包 OpenCode/AGY/Grok 與 Space Bunny 免費模型的成本降維流水線"
source_url: "https://github.com/SanHsien/ai-inbox"
source_platform: "Community Discussion & Developer Practice"
author: "Community Practitioner / Antigravity"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: 1
cluster_role: "跨 CLI 編排"
short_title: "Opus 規劃顧問 + 多 Agent 降維外包"
tags:
  - multi-agent-orchestration
  - cross-cli
  - cost-optimization
  - space-bunny
  - opencode-cli
  - agy
  - model-routing
---

# 跨 CLI 多代理外包編排實踐：以 Opus 擔任規劃顧問、外包 OpenCode/AGY/Grok 與 Space Bunny 免費模型的成本降維流水線

- **來源連結**：社群開發者實戰經驗分享 / [SanHsien/ai-inbox](https://github.com/SanHsien/ai-inbox)
- **發表作者**：社群實踐者（OpenCode / AGY / Claude 混合編排）
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：[`notes/2026-10-17-model-routing-opusplan-advisor.md`](./2026-10-17-model-routing-opusplan-advisor.md)

---

## 1. 核心內容摘要與技術深挖

### 1.1 從「單端模型切換」躍升至「跨 CLI 混合外包編排」
先前在 [筆記 06](./2026-10-17-model-routing-opusplan-advisor.md) 中，探討的是 Claude Code 原生客戶端內部的 `/model opusplan` 與 `/advisor` 命令（在單一工具內切換思考模型）。

而本篇所提出的實踐思維更進一步，打破了單一 Agent 工具的藩籬，進化為**跨 Harness、跨 CLI 的多代理分工生態（Cross-CLI Subagent Orchestration）**：
1. **核心原則：頂級大腦只動腦，基礎實作全外包**：
   - 讓頂級智力模型（Claude 3.7 / 3.5 Sonnet / Opus、Fable）專注於高層次架構設計、任務拆解與規格定義（Specification & Task Planning）。
   - 將耗費大量 Token 的機械式代碼編寫、樣板文件生成、單元測試補全，透過專屬 **Skill** 外包給本機安裝的其他 CLI 工具（如 `opencode cli`、`agy`、`grok build`）。
2. **導入極致性價比與免費模型（Space Bunny）**：
   - 引入近期在社群火紅的 **Space Bunny**（`space-bunny-free` / OpenRouter `stealth/space-bunny-alpha`）：擁有 **1M 超大上下文窗口**、支援多模態輸入與高強度代碼推理，並於 OpenCode / OpenRouter 提供免費或極低成本端點，是作為機械式編碼外包的絕佳苦力模型。
3. **雙軌升級與容錯回流閉環（Fallback Escalation & Problem-Solving Loop）**：
   - 如果追求系統高穩定性，指定 Opus 同時擔任**「最終驗證者（Verifier）」**與**「升級顧問（Escalation Advisor）」**。
   - 當外包的輕量 Agent 遇到技術卡點、編譯報錯或陷入死循環時，不直接宣告失敗，而是攜帶完整 Error Traceback 回流給 Opus 求解（Solve the problem），由 Opus 給予精確修復指引後再交辦繼續執行。

---

### 1.2 跨 CLI 混合外包與雙軌回流架構圖解

```text
┌────────────────────────────────────────────────────────────────────────┐
│      跨 CLI 多代理外包編排與雙軌回流除錯架構 (Cross-CLI Orchestration) │
└────────────────────────────────────────────────────────────────────────┘

 [使用者複雜需求]
         │
         ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 頂級決策主腦 (Opus / Fable)                                           │
 │ ├─ 1. 架構設計與邊界規劃 (High-level Architecture)                   │
 │ ├─ 2. 嚴格規格拆解為獨立批次 (Well-defined Task Packets)              │
 │ └─ 3. 呼叫跨工具封裝 Skill: `delegate_cli(tool, task_spec)`          │
 └──────────────────┬────────────────────────────────────────────────────┘
                    │
                    │ (透過 CLI 派工至免費 / 低成本模型)
                    ├───▶ opencode run --model space-bunny-free "..."
                    ├───▶ agy run --model gemini-flash "..."
                    └───▶ grok build "..."
                    │
                    ▼
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 外包執行層 (Worker Agents: OpenCode / AGY / Grok / Space Bunny 1M)    │
 │ ├─ 執行機械代碼修改、巨幅終端編譯、單元測試生成                       │
 │ └─ 消耗免費或極低成本 Token (保護主腦配額)                            │
 └──────────────────┬────────────────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │ 執行結果判斷        │
         ▼ (遇到卡點 / 報錯)    ▼ (成功完成)
 ┌───────────────────────────┐ ┌─────────────────────────────────────────┐
 │ 容錯回流 (Escalation)     │ │ 最終驗證關卡 (Verification Gate)        │
 │ ├─ 攜帶 Traceback 與 Log  │ │ ├─ 回傳 Git Diff 與測試數據至主腦       │
 │ ├─ 回流向 Opus 高級顧問   │ │ ├─ Opus 執行最後審查與契約驗收          │
 │ └─ Opus 求解後指引重試    │ │ └─ 宣告完成並 Commit / Push             │
 └───────────────────────────┘ └─────────────────────────────────────────┘
```

---

## 2. 工程啟發與適用性評估

- **對應現有系統 / 專案**：
  - **與個人維護專案 [`SanHsien/agent-advisor`](https://github.com/SanHsien/agent-advisor) 深度契合**：本專案為個人維護倉庫（本地路徑 `C:\GitHub\agent-advisor`），已將「風險分流交付與多代理路由流程」實作為五大原生 Agent Runtime 的 Plugin（Codex、Claude Code、Cursor、Antigravity、Hermes）。本篇的「Opus 主腦規劃 + 外部 CLI 外包 + Fallback 顧問驗收」哲學，正是 `agent-advisor` 中 `delegate` 與 `full` 路由向「跨 CLI 外部模型」擴展的黃金實體載體。
  - **與本機工具鏈深度結合**：本地 Windows 11 環境已安裝 `agy`（Google Antigravity CLI），並具備 Python 與 Node.js 工具鏈。可輕鬆將 `opencode` 或 `grok` 封裝進 Antigravity Skill 中。
  - **與 `token-optimizer` 規則無縫融合**：本架構是 `token-optimizer` 的最高實踐形態——昂貴的頂級推理 Token 100% 用在決策與難題攻堅上，動輒上萬行輸出的測試編譯全由免費或廉價 CLI 吸收。
  - **與 `orchestration` / `advisor-pro-implementer` 的進階延伸**：系統現有的 `orchestration` 技能主要在單一平臺調度 flash 與 pro；本方案進一步將調度邊界擴展到「外部開源 CLI」，實現多 Harness 協同。

- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **跨 CLI 封裝 Skill**：建立統一的 `subagent-cli` 技能，讓任何 Coding Agent 都能以標準格式呼叫 `opencode`、`agy` 等終端工具。
    2. **Space Bunny 接入**：利用 OpenRouter 或 OpenCode 免費的 `space-bunny-free` 1M 上下文模型，承擔初級代碼編寫與測試工作。
    3. **雙軌除錯回流協定**：規範子代理回報錯誤的格式（Context + Action + Traceback），方便 Opus 快狠準指出根因。
  - **適用性界線**：
    - 涉及高敏感代碼或本機金鑰的任務，外包模型必須限制在具備零數據保留（Zero Data Retention）的端點或本地私有模型，嚴禁將私密代碼流向不明第三方。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-31`**｜**[優先級：高]** 建立「跨 CLI 外包 Agent 技能套件（Cross-CLI Subagent SKILL.md）」並整合至 `SanHsien/agent-advisor`
  - **目標範圍**：`SanHsien/agent-advisor` ＋ `SanHsien/agy-staff`（**現有可用 Repo**：直接復用 `agy-staff` 將 Antigravity CLI 作為執行端 Worker 委派給 Claude Code / Codex 調用，並在 `agent-advisor` 中統一派工路由）
  - **維護備註**：本專案為個人維護倉庫，遵循全域規範「在 fork 上，PR／push／release 只打 SanHsien/<repo>」，所有改動直接於本機與個人遠端閉環。
  - **具體實作步驟**：
    1. 調研 Windows 11 下 `opencode` CLI、`agy` CLI、`grok build` 的命令列非同步調用參數（如 headless mode, quiet output, output format）。
    2. 結合 `SanHsien/agy-staff` 的現成外包腳本，編寫標準化 `cross-cli-subagent` 技能規範，定義輸入結構（目標 CLI、指定模型、工作區路徑、待辦清單）與輸出回傳格式。
    3. 將跨 CLI 委派機制納入 `SanHsien/agent-advisor` 的 `orchestration` 規範中，支援透過外部 CLI 執行機械代碼修改。
    4. 實作防呆與逾時隔離機制，防止外包 CLI 卡死導致主流程中斷。
  - **驗收標準（DoD）**：在本地完成以主 Agent 透過 Skill 呼叫 `agy` 或 `opencode` 完成子任務之測試，並產出實測執行報告。
  - **完成日期**：2026-10-20
  - **實作紀錄 / 證據**：規範併入 `SanHsien/agent-advisor` Claude 版 orchestration 技能（`cf8ce3b`：`references/cross-cli.md`，跨 CLI 工人算 `delegate` 的那一個 auxiliary，必須設逾時、隔離 worktree、主 session 自行驗證）；派工契約（目標 CLI、模型、工作區、逾時）寫入 [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) SPEC 第 7 節。實測報告 agent-relay `docs/evidence/2026-10-20-phase2.md`：(1) 主 Agent 依 agy-staff `implementer` 技能入口派 agy（gemini-3.8-flash-low，`--timeout 10m`）在獨立 worktree 加 `mul()`，43 秒、commit `58a0f74`，主 session 自跑 unittest 通過；(2) 經 agent-relay 信件 `--run agy --mode plan` 派 agy 唯讀審查，44 秒自動回信列出缺少的邊界測試。防呆：逾時強制結束整棵行程、只執行真正的 `.exe`（拒絕 `.cmd` 外殼）、例外一律回信、中斷補救。限制：opencode CLI 本機未安裝，未測。

- [ ] **`T-20261017-32`**｜**[優先級：中]** 評估並配置 Space Bunny（1M Context 免費模型）與雙軌回流升級除錯機制（Fallback Escalation Loop）
  - **目標範圍**：`SanHsien/agent-advisor`（**現有可用 Repo**：復用 `advisor-pro-reviewer` 獨立審查軌道與升級除錯協定）
  - **狀態**：⚪ 不做（2026-10-25 實測查詢 OpenRouter API /api/v1/models 確認 stealth/space-bunny-alpha 與免費版 minimax/minimax-m3.1-flash:free 均已下架，僅存付費端點 minimax/minimax-m3.1-flash，依退回規範關閉；對應回流除錯機制已於 agent-relay commit 66e8473 落地，查驗輸出已更新至 agent-relay 報告）。
  - **具體實作步驟**：
    1. 測試 `space-bunny-free` 於 OpenRouter / OpenCode 的連線延遲、代碼生成精確度與 1M 窗口承載力。
    2. 設計雙軌回流 Prompt 協定：定義當 Worker Agent 報錯時，如何格式化提煉「失敗上下文 + 終端報錯」回送給 Opus 高級顧問或 Reviewer Lane。
    3. 驗證完整閉環：模擬一個具備語法錯誤的難題，驗證「Space Bunny 失敗 ──▶ 回送 Opus 診斷 ──▶ 指導修正 ──▶ 測試通過」的端到端修復流。
  - **驗收標準（DoD）**：產出 Space Bunny 實測基準報告與回流除錯 Prompt 範本文檔。
  - **實作紀錄 / 證據**：報告 [SanHsien/agent-relay](https://github.com/SanHsien/agent-relay) `docs/reports/2026-10-20-space-bunny-benchmark.md`、範本 `docs/templates/escalation-prompt.md`；回流升級實作於 `dispatch.py`（SPEC 第 12 節，`752fbfb`→`fa3024d`），agent-advisor Claude 版 `references/cross-cli.md` 加回流升級段（`52f3d9a`）。查證：Space Bunny Alpha 即 MiniMax M3.1 Flash，免費匿名期已結束、`stealth/space-bunny-alpha` 已無端點；現行免費版 `minimax/minimax-m3.1-flash:free`（1M ctx、$0）需 OpenRouter 金鑰，本機沒有，**MiniMax 本身的延遲／正確率／1M 承載力未實測**，報告附金鑰取得後的補測步驟。閉環實測（派工 `20261020T151929609Z-7e6d40`）：claude-haiku-5-5 只做表面修補（25.6 秒、$0.019）→ 閘門 verification-failed → 自動升級 claude-opus-5-5 引用失敗證據修正（34.5 秒、$0.685）→ 閘門 exit 0 → commit `66e8473`。219 項單元測試通過，兩輪獨立審查判定 ship。**退回（2026-10-25）**：DoD 要的是「Space Bunny 實測基準報告」，但模型本身的延遲、正確率與 1M 承載力都未實測，沒有量測數字就不算基準報告，故退回待辦（回流除錯範本部分已完成）。剩下要做：取得 OpenRouter 金鑰後，依報告附的補測步驟實測 `minimax/minimax-m3.1-flash:free`，把數字補進報告；若確認免費版也已下架，改用 `close` 關閉並寫明理由。

---

## 4. 關聯筆記與相關任務（Related Notes & Tasks）

- **共同大腦與多 Agent 工廠**：
  - [AI 共同大腦工業級架構規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [多 Agent 生產力工廠：Magpie 網關與 Herdr 終端復用](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md) ｜ 關聯任務：`T-20261018-15`、`T-20261018-16`
  - [Crossroad A2A 跨機器寄信協議](./2026-10-19-crossroad-a2a-agent-mail-relay.md) ｜ 關聯任務：`T-20261019-01`、`T-20261019-02`
- **模型路由與工程驗證**：
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`
  - [SpaceX 首席工程師 pstack 方法論](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-17`、`T-20261018-18`


---
