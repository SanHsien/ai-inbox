# 獨立審查報告：2026-11-26-lingtalkai-gpt-image-2-5-eight-scenarios-eval

- reviewer: codex/gpt-6.1-sol@01a222ad-96aa-7b72-b53c-2a68e4113b4c
- content_sha256: 301f6665ba8de4ba8697cba99a4040de95f6028a303fa0e4bc4fa641b5b02400
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）
- source_ref: codex thread 01a222ad-96aa-7b72-b53c-2a68e4113b4c

---
結論：`changes_requested`，共 3 處更正。內容雜湊與指定值一致；未修改任何檔案。

1. **原始資料讀完度（source）**

   [YouTube 原始來源](https://www.youtube.com/watch?v=Uhxt39vNWsc)讀取受限，未取得影片畫面、逐字稿與留言。本次實際看過作者圖片 0 張、留言 0 則，平台留言計數無法獨立確認。

   因此移除 `source` 範圍，保留作者的 `full` 聲明，不因存取限制列更正。筆記的 49 則與正文記載的 12 則仍待來源補審核對。

2. **事實查核（facts）**

   官方確認 GPT Image 2.5 的 Sunburst、Flare 兩款模型，以及圖上留言、草圖和模板功能；Sunburst 偏重編修精度，生成時間較長。[官方公告](https://openai.com/index/introducing-chatgpt-images-2-5/)

   影片日期、長度、觀看數、讚數、各時間點案例與留言歸屬，本次無法獨立查證，不判定為錯誤。

3. **證據分級（evidence）**

   - **更正 1：自動路由。** 筆記第 36 行把介面依任務自動選用兩款模型寫成確定機制。官方公告確認兩款 API 模型，但未確認此路由規則。應補官方出處，否則標為作者說法、尚未查證。[官方公告](https://openai.com/index/introducing-chatgpt-images-2-5/)
   - **更正 2：座標轉換。** 第 44 行把圖上留言解釋成自動轉為 x/y 指令。官方只確認能在圖片指定位置留言，未交代這個內部機制。應保留操作描述，將座標轉換標為未查證。[官方公告](https://openai.com/index/introducing-chatgpt-images-2-5/)
   - **更正 3：效果與因果推論。** 第 36、44 行把局部編修不跑版、避免畫質退化寫成一般效果，並歸因於座標打點。官方文件仍列出角色一致性、文字位置與構圖控制限制。應改為影片個案觀察，不推論為普遍保證或已證實因果。[官方限制](https://developers.openai.com/api/docs/guides/image-generation#limitations)

   Seedance 官方確認支援多模態參考輸入；這不能證明影片作者已完成 Codex 串接，或使用了哪些首尾／中間影格控制。筆記第二節已有作者歸屬，應維持為作者自述，待影片補審。[Seedance 官方公告](https://seed.bytedance.com/en/blog/official-launch-of-seedance-2-0/)

4. **任務影響（task_impact）**

   筆記為 `archived`，沒有任務 ID、已完成任務或指定產出檔，無連帶產出需回報。下一步是修正上述證據語氣，並另行補審影片與留言。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 3,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "evidence",
      "claim": "第 36 行：對話介面依任務自動選用 Sunburst 或 Flare。",
      "problem": "已查官方資料確認兩款模型存在，但未確認此介面路由規則；目前無法查證。",
      "evidence": "https://openai.com/index/introducing-chatgpt-images-2-5/",
      "fix": "補官方路由規則出處；若僅出自影片，明標作者說法、尚未查證。"
    },
    {
      "kind": "evidence",
      "claim": "第 44 行：圖面留言自動轉為 x/y 座標指令。",
      "problem": "官方確認圖上留言功能，但未說明其內部使用 x/y 指令；目前無法查證。",
      "evidence": "https://openai.com/index/introducing-chatgpt-images-2-5/",
      "fix": "改寫為在圖片指定位置留言要求編修；座標轉換機制標為未查證。"
    },
    {
      "kind": "evidence",
      "claim": "第 36、44 行：局部編修不跑版，座標打點可避免多輪修改畫質退化。",
      "problem": "把案例效果推廣為一般能力，並加入未證實的因果關係；官方仍列出一致性與構圖控制限制。",
      "evidence": "https://developers.openai.com/api/docs/guides/image-generation#limitations",
      "fix": "限定為影片個案觀察，補上編修可能偏移的限制，移除座標打點能防止退化的確定語氣。"
    }
  ],
  "task_impact": []
}
```
