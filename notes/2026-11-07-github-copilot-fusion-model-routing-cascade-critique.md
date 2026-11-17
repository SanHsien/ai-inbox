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
source_review: full
source_reviewed_at: 2026-11-17
source_images: 1
source_replies: 11
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
- **發布時間**：2026-11-04 18:26 (UTC+8)（2026-11-16 重審時：43 個心情、11 則留言、15 次分享；Facebook 標記為「AI 內容」）
- **歸屬集群**：集群 1（角色：`模型路由與升級策略對照`）
- **評估結論**：`🟡 中等價值：概念整理好，但與既有路由規則大幅重疊`：不衍生新任務
- **相關交叉參照**：
  - [`notes/2026-10-17-model-routing-opusplan-advisor.md`](./2026-10-17-model-routing-opusplan-advisor.md)（模型路由與 advisor 模式）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（模型燒錢速率、快取與路由矩陣）
  - [`notes/2026-11-02-microphone-anti-overengineering-eight-agent-rules.md`](./2026-11-02-microphone-anti-overengineering-eight-agent-rules.md)（撞牆兩次即停、兩輪審查上限）

---

## 0. 原始資料盤點

> 2026-11-16 重審：未登入可讀貼文全文、1 張圖與 9 則留言。
> 2026-11-17 登入補讀：改用「所有留言」排序、回覆串全部展開，11 則全部讀完。補到的 2 則是作者的參考資料留言與 `Tim Wang` 的第二則回覆。

- **作者圖片**：共 1 張，手寫字風格標題卡：「讓 AI 自己選擇適合的模型執行」「模型路由（Model Routing）到自動模型分派（Model Orchestration）」。沒有評測圖表、官方截圖或數據來源，貼文裡的 60 分、成本一半、時間少 40% 都只有文字轉述。
- **作者留言補充**（5 則；2026-11-17 更正：上次寫「沒有補連結或數據出處」是錯的，未登入時那則留言被濾掉）：
  - **參考資料留言**（附 12 個連結，開頭 5 個與 Fusion／NVIDIA／OpenRouter 相關的已確認可開啟）：
    - GitHub Copilot Fusion [正式推出公告](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/)、前身 [HydraFusion 研究文](https://github.blog/ai-and-ml/project-hydrafusion-frontier-quality-via-multi-model-orchestration/)、[官方文件](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)（快取邊界、context 分配、計費與限制）。
    - Anthropic [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)、[RouteLLM](https://arxiv.org/abs/2406.18665)、[FrugalGPT](https://arxiv.org/abs/2305.05176)。
    - NVIDIA [NeMo Switchyard 介紹文](https://developer.nvidia.com/blog/route-ai-agent-workloads-across-models-with-nvidia-nemo-switchyard)。
    - [Not Diamond](https://docs.notdiamond.ai/docs/router-training-quickstart)、[LiteLLM Auto Routing](https://docs.litellm.ai/docs/proxy/auto_routing)、[vLLM Semantic Router](https://vllm-sr.ai/docs/overview/semantic-router-overview/)、[OpenRouter Auto Router](https://openrouter.ai/openrouter/auto/) 與 [Model Router Benchmarks](https://openrouter.ai/blog/announcements/model-router-benchmarks/)。
  - 回 `Tim Wang`：先有自動路由，品質會慢慢優化。作者沒有反駁「選得太貴」這個實測，也沒有說自己實際用過 Fusion。
  - 回其他人：選模型是要練的技能，現在連這個都能外包；看看大家在發展什麼沒有壞處。
- **網友留言重點**（頁面標示 11 則，全部讀完，含作者 5 則）：
  - `Tim Wang`（公司內實際用過）：自動選的模型消耗很大，便宜模型能做的事被分給最貴的模型，credit 消耗從十位數變百位數，最後改回手動選；公司配發的 credit 要省著用才撐得到月底。
  - `Tim Wang` 第二則（回作者的「一步一步來」）：公司專案等不到慢慢優化，有了 AI 之後交付量是幾倍，客戶與對手也都有 AI。
  - `Yenhung Wu`：交給它選，燒錢不手軟。與上一則同方向。
  - `Nathaniel Lee`：直接固定用最強模型、自己驗收修錯就好，不需要這套。
  - 其餘為玩笑。
- **對分析的影響**：
  - 發布時間原寫「10:26 (UTC+8)」，頁面顯示下午 6:26，原值其實是 UTC；互動數一併更新。
  - 圖片沒有提供任何可查證的數據，所以第 1 節「廠商公布數字，未獨立驗證」的標註維持，並補一句作者未附出處。
  - 五則網友留言裡沒有任何一則回報「用了有省錢」，兩則回報或認為更貴；作者回覆也只說「會慢慢優化」。第 3 節補上第二則同方向留言與作者的回應。
  - 結論（不採用自動升級、不衍生任務）不變，反而多一則佐證。
  - 2026-11-17 補讀後的修改：
    - 作者其實有附出處。第 1 節「貼文與附圖都沒有附評測連結」改成「出處在作者留言」；60 分、成本一半、時間少 40% 仍是廠商數字，這點不變。
    - 第 2 節原標「未查證：本筆記未附官方網址」，現在依作者給的官方文件逐項核對過，標註拿掉並補上官方文件才有的三點（限時 7 折、草稿被捨棄時已改的檔案不會還原、Critique 是多個模型平行審查）。
    - `Tim Wang` 的第二則回覆補進第 3 節。

---

## 1. 貼文重點

GitHub Copilot Fusion 推出自動模型分派，使用者只選投入程度（Standard／High／Max），系統替每個 prompt 決定模型與協作流程：

| 流程 | 做法 | 對應的既有模式 |
| --- | --- | --- |
| **Single** | 一個模型直接完成 | Anthropic Routing |
| **Cascade** | 便宜模型先做，judge 評估不過就升級 | FrugalGPT cascade |
| **Critique** | 主模型先寫，其他模型審查，回來修改 | Anthropic Evaluator–Optimizer |

- 作者引用官方數據：Artificial Analysis Coding Agent Index 上 Fusion Max 60 分，比 Claude Code + Opus 5.5 Max 少 2 分，平均 API 成本約一半、時間少約 40%（**廠商公布數字，未獨立驗證**；貼文與附圖沒有連結，出處在作者留言，見第 0 節）。
- 生態系整理：RouteLLM／FrugalGPT（研究）、Not Diamond（自訓 router）、LiteLLM／vLLM Semantic Router（共用分派服務）、OpenRouter（auto router 與評測）。
- 作者結論：模型選擇正在變成工具內建能力，人的工作前移到「講清需求、定義完成、驗收結果」。

## 2. 查證

- **Fusion 官方說明**與貼文一致（2026-11-17 已對照 [GitHub 官方文件](https://docs.github.com/en/copilot/concepts/models/copilot-fusion)）：三種執行方式 + 三種努力等級；主對話盡量留在同一模型以保 prompt cache，審查模型只拿必要 context；**沒有額外訂閱費，但按實際呼叫的每個模型計費**，High／Max 可能觸發多模型呼叫，消耗高於 Standard。
  - 官方文件另外寫明的三點：(1) 到 2026-11-30 為止，付費方案用 Fusion 的模型費用打 7 折，所以現在量到的成本偏低，折扣結束後要重算；(2) Fusion 捨棄某份草稿時，那份草稿已經對工作區做的檔案修改**不會自動還原**，提交前要自己檢查；(3) Critique 是一個模型寫、**多個模型平行審查**後彙整意見再改，不是只找一個審查者，呼叫數比貼文描述的多。
  - Fusion 與 subagent 分開運作，不會自己啟動 subagent；Max 等級需要的模型若被管理員停用，選單裡就不會出現。
- **[NVIDIA NeMo Switchyard](https://github.com/NVIDIA-NeMo/Switchyard)**：stage router 觀察最近幾輪工具活動（讀取／寫入／測試），**重複失敗、空轉迴圈 → 升級到強模型**；穩定寫入、測試通過 → 降回便宜模型；有 `capable_hold_turns` 升級後保持期（README 未見；僅在 repo 原始碼搜尋到該字串，行為未查證），訊號不明時可問 LLM judge。可作為 middleware 或獨立 proxy。

## 3. 最有價值的反證：第一線留言

> Tim Wang：用這個選的模型噴很大，殺雞用牛刀……最後還是手動 routing。gpt-6.1-terra 能做的幫你選 Claude Opus 5.5，本來消耗的 credit 從十位數變百位數。

另一則留言（`Yenhung Wu`）也說交給它選「燒錢不手軟」。作者對這個實測的回覆是「先有自動路由，品質慢慢會優化」，沒有提出反例；`Tim Wang` 再回：公司專案等不到慢慢優化。

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
