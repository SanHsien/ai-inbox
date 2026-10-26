---
id: 2026-10-26-llm-burn-rate-cache-routing-benchmark
title: "多模型連續開發實測：Sol 6.1 vs Astra 6 vs Luna 6 燒額速率、Prompt Caching 效益與長程 /goal 派工最佳實踐"
source_url: "N/A"
source_platform: "一線工程實測 (Empirical Benchmark)"
author: "維護者 (Maintainer)"
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: in-progress
cluster: 1
cluster_role: "路由分流"
short_title: "Sol/Astra/Luna 燒額與快取實測"
tags:
  - cost-control
  - model-routing
  - prompt-caching
  - quota-management
  - long-running-agent
---

# 多模型連續開發實測：Sol 6.1 vs Astra 6 vs Luna 6 燒額速率、Prompt Caching 效益與長程 /goal 派工最佳實踐

- **資料來源**：`維護者一線連續開發實測數據（2026-10-26）`
- **評測情境**：搭配 Tibo's Reset 後的多專案高強度連續開發、從零骨架建構與長程自主派工
- **分析日期**：`2026-10-26`
- **當前狀態**：`🟡 進行中 (In Progress)`
- **相關交叉參照**：[`notes/2026-10-17-model-routing-opusplan-advisor.md`](./2026-10-17-model-routing-opusplan-advisor.md)、[`notes/2026-10-17-cross-cli-subagent-orchestration-space-bunny.md`](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md)

---

## 1. 核心實測數據與技術摘要（Key Benchmark Findings）

在多專案連續推進與排程重置（Tibo's Reset）後，透過真實長程開發取得不同階層模型的「配額消耗速率比」與「吞吐邊界」實測數據：

```text
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│       評測模型       │     典型工程任務     │     配額消耗速率     │     折算時消耗比     │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Sol 6.1 High         │ 5~6 個專案同步維護   │ 24 小時燒 $100 帳號  │ ~2.08% 週額度 / 小時 │
│                      │ 功能實作與模組迭代   │ 50% 週額度           │ （基準線 1.0x）      │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Astra 6 High         │ 2 個專案從零開始     │ 4 小時燒乾 $100 帳號 │ ~25.0% 週額度 / 小時 │
│ (旗艦頂規重型)       │ 搭建整體架構骨架     │ 100% 週額度          │ （暴增高達 12.0x！） │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Luna 6 Max ~ High    │ 單/多專案搭配 /goal  │ 2 天燒乾 Plus 帳號   │ 均勻輸出避開 5H 限制 │
│ (Plus 帳號最佳解)    │ 24 小時不間斷推進    │ 100% 週額度          │ （吞吐利用率最大化） │
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

### 關鍵洞察 1：骨架搭建的「頂規陷阱」與 12 倍燒額落差
- **現象**：許多工程師直覺認為「從零開始搭專案骨架架構最難，應當直接上最強旗艦 Astra 6 High」，但實測顯示僅搭建 2 個專案骨架，短短 4 小時便耗盡整週 \$100 配額。
- **根因分析**：
  1. 專案初期雖然涉及模組劃分，但伴隨產生的大量產物是目錄結構、設定檔、型別定義、基礎 CRUD 與測試鷹架，其本質是「樣板代碼密度高、上下文頻繁初始化」。
  2. 頂級模型（Astra 6 High）的內部思維鏈（Thinking Token）與輸出倍率極高，在處理大篇幅樣板與上下文未完全快取的初期階段，Token 消耗呈爆炸式增長。
  3. **調度結論**：骨架期「大腦草擬架構」可短暫諮詢頂級模型，但「具體骨架生成與鷹架鋪設」應全面降級至 Sol 6.1 High 甚至 Luna 6，避免 12 倍速的配額蒸發。

### 關鍵洞察 2：Plus 帳號破局點——Luna 6 Max~High 搭配 `/goal` 避開 5H 滾動限制
- **限制痛點**：Plus 帳號通常具備「5 小時滾動上限（5-hour Rolling Cap）」。若使用重型模型，往往在 1~2 小時內即觸發上限並被強制進入數小時的冷卻期，大幅中斷自動化工作流。
- **解法機制**：
  1. 選用推理性能足夠且耗額極為節制的 **Luna 6 Max ~ High**。
  2. 搭配具備驗收閘門、有清晰停止條件的 `/goal` 指令，使 Agent 以均勻穩定的速率（Pacing）連續運行。
  3. 實測證實此組合可達成 **24 小時不間斷持續運行**，完全不撞 5H 限制，並在約 2 天內均勻用滿每週上限，實現個人帳號的最佳算力利用率。

### 關鍵洞察 3：Prompt Caching（提示詞快取）在長程運行的實質體感
- 在連續跑 24 小時且多專案並行的情境下，Prompt Caching 的命中效益極其顯著：
  - **靜態前綴高命中**：包括全域協作規範（`AGENTS.md`、`user_preferences.md`）、專案相依結構、API 契約與核心型別，在多次請求間保持不變，快取命中率可達 75%~90% 以上。
  - **首字延遲（TTFT）大幅降低**：快取命中免除了重複前綴的冗長計算，使長程連續派工維持流暢響應，不致因對話過長而嚴重降速。

---

## 2. 深入技術拆解與調度矩陣（Deep Dive & Routing Matrix）

### 2.1 任務階段與模型配對建議矩陣

```text
               ┌────────────────────────────────────────────────────────┐
               │ 任務性質判斷                                            │
               └───────────┬────────────────────────────────┬───────────┘
                           │                                │
            ┌──────────────▼─────────────┐   ┌──────────────▼─────────────┐
            │ 階段 A：高複雜決策 / 重大疑慮│   │ 階段 B：連續迭代 / 骨架與功能實作│
            │ (極深邏輯、安全攻堅、架構分歧)│   │ (多專案維護、模組擴充、Bug修復)│
            └──────────────┬─────────────┘   └──────────────┬─────────────┘
                           │                                │
                           ▼                                ▼
                 【Astra 6 High】                  【Sol 6.1 High】
                 - 限時/限次諮詢                   - 24H 連續運行骨幹
                 - 完成後立即降級                  - 搭配 Prompt Cache 最大化
                           │                                │
                           └───────────────┬────────────────┘
                                           │
                                           ▼ (Plus/個人平價帳號情境)
                                  【Luna 6 Max ~ High】
                                  - 搭配 /goal 規避 5H 窗口
                                  - 24H 穩定吞吐、2天用滿週額
```

### 2.2 Prompt Caching 友善排版原則
為確保多專案並行時 Prompt Caching 達到最高命中率，派工與上下文組裝應遵守「靜態在前、動態在後」紀律：
1. **Layer 1（全靜態，極高命中）**：系統提示詞（System Prompt）、全域規則（`AGENTS.md`）、不可變環境事實。
2. **Layer 2（專案靜態，跨輪命中）**：專案架構索引、資料庫 Schema、核心介面契約。
3. **Layer 3（半動態，當前回合局部命中）**：近期相關代碼檔案快照。
4. **Layer 4（全動態，不快取）**：當前回合使用者請求、隨機生成的暫存變數、最新測試錯誤輸出。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **採納**：
  1. 將「Sol 6.1 作為長程主力（24H 耗額 50% 週額度）」與「Astra 6 嚴格限流（4H 耗盡週額度，耗額 12x）」的實測數據納入知識庫，作為跨 AI 派工之防爆線。
  2. 於 Plus 帳號情境優先推薦「Luna 6 Max~High + `/goal`」長程自動化範式。
  3. 產出結構化速查表 `docs/model-burn-rate-routing-matrix.md` 供所有 Agent 與使用者隨時查閱。
- **不採納**：
  - 不在缺乏預算監控防線的情況下，允許背景 Agent 自動啟動 Astra 6 進行大規模全專案從零生成。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261026-01`**｜**[優先級：高]** 撰寫「長程並行開發模型選型與配額消耗速查表」收錄於 `docs/model-burn-rate-routing-matrix.md`
  - **狀態**：🟡 進行中
  - **目標範圍**：`docs/model-burn-rate-routing-matrix.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳細對比 Sol 6.1 High（24H 50%）、Astra 6 High（4H 100%）、Luna 6 Max~High（2天 100%）之耗額速度與單位成本。
    2. 總結骨架搭建、模組迭代、重構攻堅與長程自動化的選型建議。
    3. 整理 Prompt Caching 四層前綴友好排版手冊與 Plus 帳號 `/goal` 避開 5H 限制最佳實踐。
  - **驗收標準（DoD）**：產出 `docs/model-burn-rate-routing-matrix.md`，內含三大模型耗額數據對比、適用場景清單、快取排版原則與 5H 規避策略；以 `Test-Path docs/model-burn-rate-routing-matrix.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-02`**｜**[優先級：中]** 將「骨架搭建降級至 Sol 6.1、極限攻堅再開 Astra 6」與「Luna 6 避開 5H 限制」原則沉澱至 `agent-assets` 共用偏好庫
  - **狀態**：⚪ 不做（不做：要寫入的是單篇文章作者的模型選擇建議與耗額倍數（Astra 6 為 Sol 6.1 的 12 倍等），不是維護者的偏好；agent-assets RUNBOOK 也明訂模型名、價格、額度這類動態資料不寫成永久事實。這些數據改附出處與日期收錄在 T-20261026-01 的 docs/model-burn-rate-routing-matrix.md。）
  - **目標範圍**：`C:\GitHub\agent-assets\knowledge\user_preferences.md`
  - **具體做法**：
    1. 在 `user_preferences.md` 的模型調度段落中，補充實測耗額數據警示（Astra 6 耗額為 Sol 6.1 的 12 倍）。
    2. 加入從零搭建骨架時預設使用 Sol 6.1 或 Luna 6、嚴禁無界限使用頂級模型的紀律。
    3. 補充 Plus 帳號使用 Luna 6 + `/goal` 規避 5H 滾動限制的長程排程建議。
  - **驗收標準（DoD）**：更新 `knowledge/user_preferences.md`，通過 `python -m unittest discover -s tests`，並主動 git push 至 `SanHsien/agent-assets`。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261026-03`**｜**[優先級：低]** 在 `agent-relay` 派工模組中增加模型耗額等級警示與快取友善結構建議
  - **狀態**：⚪ 不做（不做：要把單篇文章的模型耗額倍數寫進派工程式，屬於會變動的資料寫死成常數；agent-relay 的 advisor 已經讀本機即時額度（Claude statusline、codex-reset-checker）決定 runtime，比固定倍數準確。耗額數據改附出處與日期收錄於 docs/model-burn-rate-routing-matrix.md（T-20261026-01）。）
  - **目標範圍**：`C:\GitHub\agent-relay\docs\` 與 `agent_relay/advise.py`
  - **具體做法**：
    1. 在 `agent-relay` 派工指南與建議中，標注各模型階層之燃燒速率。
    2. 提示派工 Prompt 應固定靜態 System Prompt 前綴以充分利用 Prompt Caching。
  - **驗收標準（DoD）**：產出或更新相關文件，跑過單元測試並推送至 `SanHsien/agent-relay`。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **模型調度與雙軌架構**：
  - [Claude 混合模型分工實踐：/model opusplan 與 /advisor 雙軌架構](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`
  - [跨 CLI 子代理人編排：Opus 規劃顧問 + 多 Agent 降維外包](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
- **成本與上下文壓縮**：
  - [Claude Code Idle Compaction 與 cc-session-reader 機制解構](./2026-10-17-claude-code-idle-compaction-cc-session-reader.md) ｜ 關聯任務：`T-20261017-03`、`T-20261017-04`
