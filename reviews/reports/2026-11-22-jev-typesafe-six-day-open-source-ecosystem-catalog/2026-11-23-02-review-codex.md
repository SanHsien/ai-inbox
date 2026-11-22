# 獨立審查報告：2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog

- reviewer: codex/gpt-6.1-sol@01a2052d-603d-7072-9104-ddb1b63bf9db
- content_sha256: d94a7d20e3649ba6c9e3905397b0b20a16b1ea68c48e0c6a8c76ba2a274719c3
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-23
- verdict: changes_requested；corrections: 6；source_review: unavailable（作者聲明 unavailable）
- source_ref: codex thread 01a2052d-603d-7072-9104-ddb1b63bf9db

---
**結論：`changes_requested`，共 6 處更正。** 內容雜湊與派審值一致；未修改任何檔案。

### 1. 原始資料讀完度（source）

已開啟提供的 GitHub 網址，但它是收件匣首頁，無法據此核對原始社群貼文。另以 Jev、1,528、六天等關鍵字搜尋，並嘗試 Facebook／Threads 站內搜尋，仍未取得可核對的原文。

貼文留言計數未知；本次未讀到作者圖片或留言。依交付規則，**移除 `source` 審查範圍**，保留作者的 `unavailable`，不將存取限制列為更正。

### 2. 事實查核（facts）

1. **報稅分類器的分層原因寫錯。**  
   §2.2 將分層請求歸因於 255 類上限；README 實際說明：第一層為 230 個選項加其他選項，五組母表才觸發第二次請求，原因是頁面上的母表名稱比附表更明確。應保留分層架構，刪除未獲支持的因果。  
   出處：[分類器架構說明](https://github.com/kyotofin/tax-doc-classifier#how-it-works)。

2. **95.0% 成績漏寫訓練步驟。**  
   §2.8、§4 將改善概括為訊號拆解；實際是以五項 Jev 訊號，在 A 組選取及訓練邏輯迴歸，再於 B 組保留集評估。單一最佳訊號為 89.4%，確定性規則為 91.8%；不能讓讀者以為拆題後直接組合即可得到 95.0%。  
   出處：[釣魚信評測方法與控制實驗](https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026)。

3. **指令審核數據沿用已撤回的樣本。**  
   §2.4、§4.2 使用 153 筆、8.7 倍、4.4 倍。作者已承認舊樣本只有單一設定檔，與三個設定檔的描述不符；修正後為 156 筆、9.8 倍速度、4.2 倍較少人工中斷。應改用修正數據，並保留單機、特定比較模型的限制。  
   出處：[官方專案 Metrics](https://github.com/anpicasso/hermes-jev-approvals/blob/main/docs/METRICS.md)。

4. **Tripwire 功能對應錯誤。**  
   §2.4 將它列為回應語意檢查；該 repo 實際是工具呼叫前的 `PreToolUse` 安全閘，回傳允許、詢問或拒絕，並非結案文字或完工證據檢查器。  
   出處：[Tripwire README](https://github.com/Sraavan/tripwire#tripwire)。

5. **輸出 Token 數量與免費計費混為一談。**  
   §1 說輸出 Token 為零；官方只能支持輸出免費。Choice 回應範例的 `usage.output_tokens` 為 34。應改成不逐字生成自由文字、僅對輸入收費，避免宣稱回應用量欄位必為零。  
   出處：[官方計費說明](https://docs.typesafe.ai/models)、[Choice 回應格式](https://docs.typesafe.ai/primitives/choice)。

6. **jev-belay 並非沒有量化數據。**  
   §2.4 的描述漏掉作者公開的 100 筆標註停止案例、AUROC 0.976，以及中位延遲 346 ms。可以不採用這些數字，但應寫成專案自述、小樣本、未獨立重測。  
   出處：[jev-belay README](https://github.com/valentynkit/jev-belay)。

### 3. 證據分級（evidence）

- **一手來源已確認**：Choice 上限 255；10 月 14 日的圖片／Box 更新；1.14 改善多語支援。[TypeSafe 更新紀錄](https://docs.typesafe.ai/changelog)
- **專案作者自測**：業配跳過率、釣魚信分類、搜尋重排序及路由模擬。筆記對路由舊政策模擬、模型標註偏差的限制已交代清楚。
- **未獨立確認**：1,528 專案、約 260 個收錄項目、約 40 個附數據，以及歷史星數。正文已標為貼文統計；本次沒有重算，也沒有將它們視為官方統計。

上述 6 處更正已合併計數，不重複增加 evidence finding。

### 4. 任務與產出影響（task_impact）

本篇只有 `T-20261122-05`，仍未勾選，**沒有已完成任務**。但其產出檔已存在，實際讀取後發現：

- `docs/system-one-decision-model-landscape.md:85`、`:106`：同樣漏掉 95.0% 所需的邏輯迴歸訓練。
- 同檔 `:74`：沿用已撤回的指令審核數據。
- 同檔 `:137`、`:147`：把 Tripwire 誤列為完工證據檢查模式。
- 同檔 `:32`：同樣混淆零輸出 Token 與免費輸出。

由整合者修正筆記與既有產出，再送審。

```json
{
  "verdict": "changes_requested",
  "source_review": "unavailable",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 6,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "§2.2 報稅分類器的分層原因",
      "problem": "將分層請求歸因於255類上限；README說明第一層為230個選項加其他選項，五組母表才分層，原因是母表名稱比附表更明確。",
      "evidence": "https://github.com/kyotofin/tax-doc-classifier#how-it-works",
      "fix": "保留分層架構，改述實際兩階段流程與作者說明的原因，移除未獲支持的上限因果。"
    },
    {
      "kind": "evidence",
      "claim": "§2.8、§4 訊號拆解的95.0%成績",
      "problem": "漏寫以A組資料選取及訓練邏輯迴歸、於B組保留集評估的步驟，容易誤認為只拆題即可得到該成績。",
      "evidence": "https://github.com/anisselbd/jev-phishing-bench#controls-added-after-review-17-september-2026",
      "fix": "明寫五項Jev訊號加上訓練過的邏輯迴歸，並補充單一訊號89.4%、確定性規則91.8%的對照限制。"
    },
    {
      "kind": "fact",
      "claim": "§2.4、§4.2 指令審核測試數據",
      "problem": "153筆、8.7倍及4.4倍來自已被作者更正的單一設定檔樣本。",
      "evidence": "https://github.com/anpicasso/hermes-jev-approvals/blob/main/docs/METRICS.md",
      "fix": "改用修正後156筆、9.8倍速度、4.2倍較少人工中斷，註明舊樣本錯誤與比較條件。"
    },
    {
      "kind": "fact",
      "claim": "§2.4 Tripwire的功能分類",
      "problem": "對應repo是工具呼叫前的PreToolUse安全閘，並非AI回應或完工證據檢查器。",
      "evidence": "https://github.com/Sraavan/tripwire#tripwire",
      "fix": "改列工具執行前風險審核，說明允許、詢問、拒絕三種結果。"
    },
    {
      "kind": "fact",
      "claim": "§1 輸出Token數量",
      "problem": "官方支持輸出免費，但Choice範例的usage.output_tokens為34，不能宣稱此欄位必為零。",
      "evidence": "https://docs.typesafe.ai/models ; https://docs.typesafe.ai/primitives/choice",
      "fix": "改為不逐字生成自由文字、僅對輸入Token收費，輸出Token免費。"
    },
    {
      "kind": "fact",
      "claim": "§2.4 jev-belay的量化證據",
      "problem": "筆記稱無量化數據，但README提供100筆標註案例、AUROC 0.976與中位延遲346ms。",
      "evidence": "https://github.com/valentynkit/jev-belay",
      "fix": "補列作者自測數據與小樣本限制，或改寫為未獨立重測。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md:85",
      "issue": "任務未勾選但產出已存在；此處及第106行省略95.0%成績所需的邏輯迴歸訓練。"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md:74",
      "issue": "沿用已撤回的153筆、8.7倍及4.4倍指令審核數據。"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md:147",
      "issue": "此處及第137行將Tripwire誤列為防提早收工或完工證據檢查模式。"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md:32",
      "issue": "流程圖宣稱零輸出Token，須區分非生成式判斷、回應用量欄位與免費輸出。"
    }
  ]
}
```
