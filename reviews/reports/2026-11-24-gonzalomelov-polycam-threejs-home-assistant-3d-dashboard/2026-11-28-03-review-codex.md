# 獨立審查報告：2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard

- reviewer: codex/gpt-6.1-sol@01a2224b-d33c-7890-a733-0c9d4479d948
- content_sha256: ef20e8e23572cbcf38fad1f949e83cfef68067a91013dfa52172039a459f1937
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）
- source_ref: codex thread 01a2224b-d33c-7890-a733-0c9d4479d948

---
結論：`changes_requested`，共 3 處更正。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度：不在本次範圍**

   X 原貼文回傳 403，本次未觀看影片或讀取留言。沿用作者的 `source_review: full`，不因本次存取限制下修；影片細節、互動數與留言內容未獨立確認。

2. **事實查核：1 處更正**

   比較表的「完整 MIT 開源」須補授權邊界。上游現行授權明確排除 `data/` 與宣傳縮圖；程式碼、技能採 MIT，不代表展示素材全部採 MIT。建議改成「程式碼與技能採 MIT；展示素材另有條款」。本次未取得歷史版本，不推斷該條款何時加入。[官方授權](https://raw.githubusercontent.com/wesbos/3d-model-anything/main/LICENSE)、[素材條款](https://raw.githubusercontent.com/wesbos/3d-model-anything/main/ASSETS-LICENSE.md)

   GPT-6 Astra 的名稱與已發布狀態可由[官方公告](https://openai.com/index/gpt-6-astra/)確認；Polycam 的室內掃描與匯出能力有[官方文件](https://learn.poly.cam/hc/en-us/articles/36655587097620-How-to-Use-Space-Mode-with-LiDAR-enabled-devices)支持，但不能據此確認本案實際使用的掃描模式或格式。

3. **證據分級：2 處更正**

   - **點擊機制被寫成已確認**：第 1 節將 Raycasting 列入影片可直接證明的實作。畫面能呈現點擊結果，不能證明底層演算法。Three.js 文件只證明 Raycaster 可用於物件點選，不能證明作者使用它。應改成「展示物件點擊互動；Raycasting 是可採用方案，實作未查證」。[官方文件](https://threejs.org/docs/pages/Raycaster.html)、[筆記第 1 節](notes/2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard.md)
   - **未公開規格書被賦予具體內容**：架構圖斷言規格書定義了 Entity 對應與介面需求，但同節又說規格書未公開。其內容目前無法查證，應標為本筆記的設計推測，或刪除括號內的具體描述。[筆記架構圖及限制段](notes/2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard.md)

   證據應分開記錄：

   ```text
   官方文件確認工具能力
   作者貼文描述個案作法
   筆記提出可能實作方案
   ```

   先前 Chrome 報告屬本次的間接證據，不能當成本次直接觀看來源的紀錄。

4. **已完成任務產出檔**

   唯一任務 `T-20261124-01` 仍未勾選，沒有已完成產出需回報。已讀取目標文件 `docs/scan-to-threejs-spatial-agent-spec.md`，未見該任務要求的裝置綁定章節。

   任務可保留；整合者修正筆記時，應將 Raycasting 明列為擬採方案。下一步是修正上述 3 處後再審。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 2 節比較表將 wesbos 專案概括為完整 MIT 開源",
      "problem": "現行官方授權排除 data/ 與宣傳縮圖，展示素材另有條款；未取得歷史版本，無法判定條款加入日期。",
      "evidence": "https://raw.githubusercontent.com/wesbos/3d-model-anything/main/LICENSE ; https://raw.githubusercontent.com/wesbos/3d-model-anything/main/ASSETS-LICENSE.md",
      "fix": "改為程式碼與技能採 MIT，展示素材另有條款，附素材授權連結。"
    },
    {
      "kind": "evidence",
      "claim": "第 1 節將 Raycasting 列為影片與貼文直接證實的實作",
      "problem": "可見的點擊互動不能證明底層使用 Raycasting；官方文件僅說明該技術可用於物件點選。",
      "evidence": "notes/2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard.md 第 1 節；https://threejs.org/docs/pages/Raycaster.html",
      "fix": "保留點擊互動的展示描述，將 Raycasting 改列為可能方案、實作未查證。"
    },
    {
      "kind": "evidence",
      "claim": "第 1 節架構圖認定一頁規格書定義 Entity 對應與介面需求",
      "problem": "同節明載規格書未公開，具體內容無法查證，卻未標為推測。",
      "evidence": "notes/2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard.md 第 1 節架構圖與未揭露／未查證段落",
      "fix": "刪除未獲證實的內容描述，或明列為本筆記建議的規格書內容。"
    }
  ],
  "task_impact": []
}
```
