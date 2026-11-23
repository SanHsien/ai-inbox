# 獨立審查報告：2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog

- reviewer: codex/gpt-6.1-sol@01a20897-41a6-7510-b2ef-c6dfad8ad0b0
- content_sha256: 81db246a10f798fc2be2c01a3c180c4045bcce0bd91271861c7bb46856532388
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-23
- verdict: changes_requested；corrections: 3；source_review: unavailable（作者聲明 unavailable）
- source_ref: codex thread 01a20897-41a6-7510-b2ef-c6dfad8ad0b0

---
結論：`changes_requested`，共 3 處更正。筆記雜湊與指定值一致；未修改任何檔案。

### 1. 原始資料讀完度（source）

提供的網址是本 repo，無法重開原社群貼文。已用 Jev、1,528、SanHsien 等關鍵字搜尋，未找回原文；圖片、留言計數與留言內容均無法核對。

依本次交付規則，`source` 不列入已完成範圍，保留作者的 `unavailable`，不因此新增 finding。作者圖片看過 0 張，原貼文留言計數未知。

### 2. 事實查核（facts）

需更正 3 處：

1. **第 1 節：Choice 上限的計算單位錯誤。**  
   255 是**每一道 Choice 題目**的選項上限；同一請求可包含多道題目。應改成「每道 Choice 題目最多 255 個選項」，不能寫成整個請求合計上限。[官方 Choice 文件](https://docs.typesafe.ai/primitives/choice)

2. **第 2.4 節：limpet 並非完全沒有量化資料。**  
   README 自述每次停止檢查約 0.7 秒、成本約 US$0.0001。應改成「有延遲及成本自述，未確認標準化準確率基準，未獨立重測」。[limpet README](https://github.com/noplan-inc/limpet#readme)

3. **第 2.4 節：jev-guard 已提供作者自測數據。**  
   README 列出台灣直連約 0.75 秒，以及 21 次 Gateway 校準呼叫的 p50 約 580 ms。應補上測試規模、路徑與作者自測限制，不能概括為沒有量化資料。[jev-guard README](https://github.com/leepokai/jev-guard#why-jev-price-and-speed-with-sources)

釣魚信評測的樣本組成、A/B 分組訓練及保留集結果，與一手 README 相符；搜尋排序的模型裁判偏差及信賴區間限制也已正確保留。[釣魚信評測](https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026)、[搜尋排序評測](https://github.com/zhuyansen/jev-search-rerank-eval#results)

### 3. 證據分級（evidence）

- **一手來源已確認**：官方題型、圖片支援、輸出免費，以及各專案 README 確實公布的測試方法與數字。這只能確認「作者公布過」，不代表獨立重現。
- **二手來源**：原社群盤點的 1,528／約 260／約 40，以及未唯一對應 repo 的專案敘述。筆記已有轉述與未重算標記。
- **未查證**：歷史星數快照未取得當日證據；Google 官方評測圖片本次無法讀取，因此未重新確認其中的比較數字，不判為錯誤。[Google 官方公告](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/)

沒有另計證據類 finding。

### 4. 任務影響（task_impact）

本篇只有 `T-20261122-05`，仍未勾選完成。其產出 [docs/system-one-decision-model-landscape.md](C:/GitHub/ai-inbox/docs/system-one-decision-model-landscape.md) 已存在，實讀發現：

- 第 1 節圖仍寫輸出用量為零，與官方回應範例不符；應區分輸出免費與用量欄位。[官方範例](https://docs.typesafe.ai/primitives/choice#response-structure)
- 第 3.1 節仍使用已撤回的 Hermes 153 筆／8.7 倍／4.4 倍，尚未同步修正版。[專案 Metrics](https://github.com/anpicasso/hermes-jev-approvals/blob/main/docs/METRICS.md)
- 第 3.1、4.1 節仍混淆 Choice 上限與稅表分層原因。[稅表分類器](https://github.com/kyotofin/tax-doc-classifier#how-it-works)
- 第 3.2、4.2 節把釣魚信提升至 95.0% 簡化成拆題效果，漏掉下游訓練條件。[評測方法](https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026)
- 第 5、5.1 節仍把 Tripwire 列為停止前檢查；它實際是工具執行前的風險閘。[Tripwire](https://github.com/Sraavan/tripwire#readme)

以上只回報，不計入更正處數。下一步由整合者修正筆記與既有產出後再送審。

```json
{
  "verdict": "changes_requested",
  "source_review": "unavailable",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第1節：單次請求上限255類",
      "problem": "255是每道Choice題目的選項上限，不是整個請求合計的選項上限；同一請求可包含多道題目。",
      "evidence": "https://docs.typesafe.ai/primitives/choice",
      "fix": "改為每道Choice題目最多255個選項，並同步釐清任務規格。"
    },
    {
      "kind": "fact",
      "claim": "第2.4節：limpet無量化數據",
      "problem": "README已有每次停止檢查約0.7秒及約US$0.0001的量化自述；不能將未獨立驗證寫成完全沒有數據。",
      "evidence": "https://github.com/noplan-inc/limpet#readme",
      "fix": "補列作者自述的延遲與成本，註明未確認標準化準確率基準、未獨立重測。"
    },
    {
      "kind": "fact",
      "claim": "第2.4節：jev-guard無量化數據",
      "problem": "README列出台灣直連約0.75秒，以及21次Gateway校準呼叫的p50約580ms。",
      "evidence": "https://github.com/leepokai/jev-guard#why-jev-price-and-speed-with-sources",
      "fix": "補列測試日期、規模與連線路徑，標為作者自測且未獨立重現。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "任務未勾選完成，但產出已存在。第1節圖將輸出用量寫為零；應區分輸出免費與usage.output_tokens可能非零。依據：https://docs.typesafe.ai/primitives/choice#response-structure"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第3.1節仍使用Hermes已撤回的153筆、8.7倍、4.4倍；需同步156筆、9.8倍、4.2倍及其限制。依據：https://github.com/anpicasso/hermes-jev-approvals/blob/main/docs/METRICS.md"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第3.1及4.1節仍混淆每題255選項與整個請求上限，並將稅表分層歸因於類別上限；需同步筆記已補充的母表辨識原因。依據：https://docs.typesafe.ai/primitives/choice 及 https://github.com/kyotofin/tax-doc-classifier#how-it-works"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第3.2及4.2節把95.0%簡化成拆解訊號即可取得，需補上A組選門檻與訓練邏輯迴歸、B組保留集評估及正則規則對照。依據：https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第5節階段C及5.1節仍把Sraavan/tripwire列為防提早收工參考；應移至PreToolUse工具執行前風險審核類別。依據：https://github.com/Sraavan/tripwire#readme"
    }
  ]
}
```
