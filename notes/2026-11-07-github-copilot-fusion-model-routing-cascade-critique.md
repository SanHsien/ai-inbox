---
id: 2026-11-07-github-copilot-fusion-model-routing-cascade-critique
title: "GitHub Copilot Fusion 自動模型分派評估：Single／Cascade／Critique 三流程、NeMo Switchyard 軌跡式升級，與既有 orchestration／token-optimizer 路由規則對照"
source_url: "https://www.facebook.com/groups/1713764039757273/permalink/1874715543662121/"
source_platform: "Facebook 社團（Codex 中文社群）"
author: "Gary Hsieh"
analyzed_at: 2026-11-07
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "模型路由與配額分流"
short_title: "Copilot Fusion 模型分派評估"
tags:
  - model-routing
  - github-copilot-fusion
  - cascade
  - critique
  - nemo-switchyard
  - prompt-cache
  - token-optimizer
---

# GitHub Copilot Fusion 自動模型分派評估：Single／Cascade／Critique 三流程、NeMo Switchyard 軌跡式升級，與既有 orchestration／token-optimizer 路由規則對照

- **來源連結**：[Facebook 社團貼文：Codex 中文社群](https://www.facebook.com/groups/1713764039757273/permalink/1874715543662121/)
- **發布時間**：2026-11-04 10:26 (UTC+8)（39 reactions、11 留言、12 分享；Facebook 標記為 AI content）
- **歸屬集群**：集群 1（角色：`模型路由與升級策略對照`）
- **評估結論**：`🟡 中等價值：概念整理好，但與既有路由規則大幅重疊`：不衍生新任務
- **相關交叉參照**：
  - [`notes/2026-10-17-model-routing-opusplan-advisor.md`](./2026-10-17-model-routing-opusplan-advisor.md)（模型路由與 advisor 模式）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（模型燒錢速率、快取與路由矩陣）
  - [`notes/2026-11-02-microphone-anti-overengineering-eight-agent-rules.md`](./2026-11-02-microphone-anti-overengineering-eight-agent-rules.md)（撞牆兩次即停、兩輪審查上限）

---

## 1. 貼文重點

GitHub Copilot Fusion 推出自動模型分派，使用者只選投入程度（Standard／High／Max），系統替每個 prompt 決定模型與協作流程：

| 流程 | 做法 | 對應的既有模式 |
| --- | --- | --- |
| **Single** | 一個模型直接完成 | Anthropic Routing |
| **Cascade** | 便宜模型先做，judge 評估不過就升級 | FrugalGPT cascade |
| **Critique** | 主模型先寫，其他模型審查，回來修改 | Anthropic Evaluator–Optimizer |

- 作者引用官方數據：Artificial Analysis Coding Agent Index 上 Fusion Max 60 分，比 Claude Code + Opus 5.5 Max 少 2 分，平均 API 成本約一半、時間少約 40%（**廠商公布數字，未獨立驗證**）。
- 生態系整理：RouteLLM／FrugalGPT（研究）、Not Diamond（自訓 router）、LiteLLM／vLLM Semantic Router（共用分派服務）、OpenRouter（auto router 與評測）。
- 作者結論：模型選擇正在變成工具內建能力，人的工作前移到「講清需求、定義完成、驗收結果」。

## 2. 查證

- **Fusion 官方說明**與貼文一致：三種執行方式 + 三種努力等級；主對話盡量留在同一模型以保 prompt cache，審查模型只拿必要 context；**沒有額外訂閱費，但按實際呼叫的每個模型計費**，High／Max 可能觸發多模型呼叫，消耗高於 Standard。
- **NVIDIA NeMo Switchyard**：stage router 觀察最近幾輪工具活動（讀取／寫入／測試），**重複失敗、空轉迴圈 → 升級到強模型**；穩定寫入、測試通過 → 降回便宜模型；有 `capable_hold_turns` 升級後保持期，訊號不明時可問 LLM judge。可作為 middleware 或獨立 proxy。

## 3. 最有價值的反證：第一線留言

> Tim Wang：用這個選的模型噴很大，殺雞用牛刀……最後還是手動 routing。gpt-6.1-terra 能做的幫你選 Claude Opus 5.5，本來消耗的 credit 從十位數變百位數。

這和官方「成本約一半」的說法相反。合理解讀：**benchmark 的平均成本 ≠ 你的任務分佈下的成本**。當 router 對難度判斷偏保守時，會系統性地選貴模型；而按模型計費下，這筆錢由使用者承擔。

## 4. 和既有規則的對照

```text
貼文概念               本機既有對應                                   差距
──────────────────────────────────────────────────────────────────────────
Routing（開工前分派）  orchestration：solo / delegate(flash|pro) / audit   無
Cascade（便宜先做）    flash 為預設 delegate，pro 僅限判斷重的工作        無
Critique（他模型審查） audit 路線 + ai-review 跨模型二審 + 兩輪上限         無
軌跡式中途升級         「撞牆兩次即停」+「新風險出現才可升級」            小
快取邊界               model-burn-rate-routing-matrix 快取章節            無
```

- 唯一小差距：Switchyard 的「**中途依失敗訊號升級，成功後降回**」比本機的「撞兩次就停、交給人」多了一步自動升級。但本機規則刻意讓人來決定（避免自動燒錢、符合單向門原則），加上留言的實際經驗，**不建議把升級改成自動**。
- 依規則淨零增長原則，不新增規則。

## 5. 可帶走的判斷

1. 評估任何 auto router，要用**自己的任務分佈**算總成本（含重試、換模型失去快取、審查模型的費用），不看廠商平均值。
2. 便宜模型不等於便宜任務：做錯重試、反覆塞大 context，省下的錢會花回去。
3. 人的價值在驗收標準：與本機 DoD／外部裁判做法一致。

## 6. 待辦

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

本篇**不衍生新任務**。理由：三種流程與快取考量都已由 `orchestration`、`token-optimizer`、`ai-review` 與路由矩陣覆蓋；唯一差距（自動中途升級）刻意不採用。若日後實際在 GitHub Copilot 使用 Fusion，再以自己的任務記錄比較 Standard 與手動選模的 credit 消耗。
