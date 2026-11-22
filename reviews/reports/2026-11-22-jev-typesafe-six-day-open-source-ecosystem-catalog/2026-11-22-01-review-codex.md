# 獨立審查報告：2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog

- reviewer: codex/gpt-6.1-sol@01a203cd-ed3b-73a3-a269-0afb3030f7e1
- content_sha256: 76c7774f80133997ccca5a9455b28d1ac7e5a672c383cae2895d64de25b4cebf
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 7；source_review: unavailable（作者聲明 unavailable）
- source_ref: codex thread 01a203cd-ed3b-73a3-a269-0afb3030f7e1

---
結論：**changes_requested，共 7 處更正**。未修改任何檔案；審查結束時內容雜湊仍符合指定值。

### 1. 原始資料讀完度（source）

未找回原始社群貼文。已用作者姓名、Jev、1,528／1528，以及 Threads、Facebook 網域搜尋；提供的 GitHub 倉庫網址無法核對原貼文圖片與留言。

作者聲明維持 `unavailable`，本次從 `scope` 移除 `source`。作者圖片看過 0 張、留言讀到 0 則；貼文計數未知。這項存取限制不列更正。

### 2. 事實查核（facts）

以下 7 項須修正，位置均指本篇筆記：

1. **第 1、3、4 節：混用歷史與現行規格。** Jev 於 2026-10-14 更新後已有圖片輸入及 `Box` 原語；圖片功能仍屬實驗性。九月快照可以保留，但不能據此宣稱現行 Jev 無法讀圖。見 [官方更新紀錄](https://docs.typesafe.ai/changelog)、[圖片文件](https://docs.typesafe.ai/images)。

2. **第 1、3、4.2 節：中文限制缺現行一手依據。** 本次未找到支持中、日、韓精準度排序的現行官方說明；官方更新紀錄只確認 1.14 改善多語支援。這不能證明中文限制已消失，也不足以將舊說法列為現行硬約束。應補歷史版本來源，並改為繁中能力待實測。見 [官方更新紀錄](https://docs.typesafe.ai/changelog)。

3. **第 2.8 節：9,831 組不是人工評分。** 標註主要來自 Jev 與 Haiku；README 描述的少量裁決也由 Claude 執行。應明寫模型標註與裁判偏差。見 [評測方法及限制](https://github.com/zhuyansen/jev-search-rerank-eval#method)。

4. **第 2.8、4.1 節：釣魚評測被概括為模型能力。** 2,000 封樣本包含各 1,000 封釣魚信與正常信；62.6% 是 Jev 1.13 直接判斷的結果。相同研究另有拆解訊號後達 95.0% 的保留集結果，不能省略設計差異後當成 Jev 整體準確率。見 [原始評測](https://github.com/anisselbd/jev-phishing-bench)。

5. **第 4.2 節：路由節費省略模擬限制。** 第 2.5 節有註記舊政策模擬，但第 4.2 節再次引用時移除了限制。作者明示這不是實測 Codex 配額節省，也不證明現行政策成效。見 [專案 README](https://github.com/0xNatoshi/jev-codex-router#jev-codex-router)。

6. **第 2.8 節：搜尋排序結論過強。** 合併標籤下，Jev 重排序相對 bge-m3 的差值為正，但信賴區間跨零；排除 Jev 裁判後才顯著較差。應寫成未證明優於 bge-m3，並將融合最佳限於該資料集。見 [結果與裁判穩健性分析](https://github.com/zhuyansen/jev-search-rerank-eval#results)。

7. **第 2 節及任務：缺少可追溯的專案網址。** 清單只有名稱，無法唯一辨識同名專案、版本與數據出處。例如 `jev-harness` 至少有 [nickylin 版本](https://github.com/nickylin/jev-harness)與 [AntonioCoppe 版本](https://github.com/AntonioCoppe/jev-harness)。應逐列補 owner/repo、數據來源與快照日期；任務引用的工具另補架構及安裝文件連結。

已確認發布日期、官方延遲宣稱、輸入計費及 Choice 上限；jev-skip、報稅分類器與瀏覽器示範數字可追溯至專案自述，未獨立重測。1,528／260／40、分類數量及歷史星數仍無法確認；Google 圖表內的精確成績亦未完成核對，不列為已確認。

### 3. 證據分級（evidence）

- **一手來源已確認**：官方規格、更新日期，以及專案確實公布上述測試結果。
- **二手來源**：筆記轉述社群盤點與 README 數字；不能等同獨立驗證成效。
- **推算／未查證**：生態總量、部分歷史數字，以及由單一測試推導的通用能力或節費結論。

### 4. 任務影響（task_impact）

唯一任務 `T-20261122-05` 仍未勾選完成，但產出 [docs/system-one-decision-model-landscape.md](docs/system-one-decision-model-landscape.md) 已存在，已讀取。

受影響內容包括：

- 第 2、4 節沿用純文字限制及未確認的中文硬約束。
- 第 3.2 節沿用人工評分說法，並將釣魚測試推廣為模型架構限制。
- 第 3.1 節將舊政策模擬解讀為已驗證經濟效益。
- 第 3.1 節將 Choice 上限寫成 255～261；官方上限為 255，報稅分類器靠分層請求涵蓋 261 種表單。見 [官方 Choice 文件](https://docs.typesafe.ai/primitives/choice)、[分類器架構](https://github.com/kyotofin/tax-doc-classifier#how-it-works)。

以上只回報，由整合者修正後再審。

```json
{
  "verdict": "changes_requested",
  "source_review": "unavailable",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 7,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第1、3、4節將純文字輸入及三種原語沿用為現行規格",
      "problem": "官方2026-10-14更新已加入圖片與Box；圖片功能仍屬實驗性。筆記未將九月快照與現行規格分開。",
      "evidence": "https://docs.typesafe.ai/changelog ; https://docs.typesafe.ai/images",
      "fix": "保留有版本日期的歷史描述，補上現行圖片與Box支援及實驗性限制，修正架構比較。"
    },
    {
      "kind": "evidence",
      "claim": "第1、3、4.2節以官方中文能力限制建立現行硬約束",
      "problem": "未找到支持中日韓精準度排序的現行一手依據；官方僅確認1.14改善多語支援，不能據此判定中文限制消失或仍維持原程度。",
      "evidence": "https://docs.typesafe.ai/changelog ; notes/2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog.md:186",
      "fix": "補歷史官方來源與版本；現行繁中表現標為待測，將部署建議與已確認規格分開。"
    },
    {
      "kind": "fact",
      "claim": "第2.8節將9831組搜尋相關性標註稱為人工評分",
      "problem": "標註主要由Jev及Haiku產生；README描述的少量裁決也由Claude執行，不能稱為人工標註資料集。",
      "evidence": "https://github.com/zhuyansen/jev-search-rerank-eval#method",
      "fix": "改為模型產生的相關性標註，說明裁判組成及循環評分偏差。"
    },
    {
      "kind": "fact",
      "claim": "第2.8、4.1節以2000封釣魚信及62.6%概括Jev能力",
      "problem": "樣本包含1000封釣魚信與1000封正常信；62.6%限於Jev 1.13直接判斷配置。研究另公布拆解訊號後的95.0%保留集結果。",
      "evidence": "https://github.com/anisselbd/jev-phishing-bench",
      "fix": "修正樣本組成，標明模型版本、判斷配置及拆解訊號結果，避免將單一配置概括為模型準確率。"
    },
    {
      "kind": "evidence",
      "claim": "第4.2節直接引用237回合與60%作為路由經濟效益",
      "problem": "作者明示為舊政策歷史模擬，並非實測Codex配額節省，也不支持現行政策成效；本節省略了第2.5節已有的限制。",
      "evidence": "https://github.com/0xNatoshi/jev-codex-router#jev-codex-router",
      "fix": "每次引用均保留舊政策模擬、非實測配額及不代表現行成效的限制，不與實際帳單直接互證。"
    },
    {
      "kind": "fact",
      "claim": "第2.8節概括Jev單獨排序較差且融合使用最佳",
      "problem": "合併標籤下相對bge-m3的差值為正但不顯著；排除Jev裁判後才顯著較差。融合最佳也僅適用該資料集與比較系統。",
      "evidence": "https://github.com/zhuyansen/jev-search-rerank-eval#results",
      "fix": "改為未證明優於bge-m3，交代裁判條件與信賴區間，限定融合結論的適用範圍。"
    },
    {
      "kind": "evidence",
      "claim": "第2節以無owner及網址的專案名稱承載功能與數據，並據此派工",
      "problem": "無法唯一定位專案或回查版本與數據來源；jev-harness已有不同owner的同名專案。",
      "evidence": "notes/2026-11-22-jev-typesafe-six-day-open-source-ecosystem-catalog.md:62 ; https://github.com/nickylin/jev-harness ; https://github.com/AntonioCoppe/jev-harness",
      "fix": "逐列補上owner/repo、原始數據連結及快照日期；任務涉及的專案補架構與安裝文件來源，未確認項目明標未查證。"
    }
  ],
  "task_impact": [
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "任務仍未勾選但產出已存在；第2、4節將純文字輸入及未確認的中文能力限制當作現行規格與硬約束。"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第3.2節誤稱9831組人工評分，並由62.6%的單一判斷配置推導System One無法取代生成模型，須補樣本組成與拆解訊號結果。"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第3.1節雖註明舊政策模擬，仍稱其驗證經濟效益；證據不足以支持現行路由成效。"
    },
    {
      "task": "T-20261122-05",
      "file": "docs/system-one-decision-model-landscape.md",
      "issue": "第3.1節將Choice上限寫為255至261；官方上限為255，tax-doc-classifier透過分層請求涵蓋261種表單。"
    }
  ]
}
```
