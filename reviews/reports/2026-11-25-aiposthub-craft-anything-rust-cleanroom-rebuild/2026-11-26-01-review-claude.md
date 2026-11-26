# 獨立審查報告：2026-11-25-aiposthub-craft-anything-rust-cleanroom-rebuild

- reviewer: claude/opus-5.5@f3fabcc5-ccb8-40bf-8a7b-d4e8eeeb8641
- content_sha256: 828b7b9e390550cd215540f097695bbd8c2f8721ac0ad7f56b43a5a4714487f4
- role: review；lane: chrome；scope: source
- reviewed_at: 2026-11-26
- verdict: changes_requested；corrections: 4；source_review: full（作者聲明 full）

---
# 獨立審查（Chrome 道，review，範圍 source）：AI郵報 Threads 與 storytold/craft-anything

- 審查日期：2026-11-26
- 審查者：claude/opus-5.5（Claude in Chrome，維護者已登入的 Threads）
- 原始來源：https://www.threads.com/@aiposthub/post/DgIWKmTATLX

## 1. 原始資料讀完度（範圍 source）

- **貼文文字**：登入後讀完主貼文（1/4）與 3 則作者續樓（2/4 四階段、3/4 功能清單與 Clean Room、4/4 Deep Mode 與「留言『重建』索取資料」導流）。
- **圖片**：只有 1 張連結預覽卡（aiposthub.com 文章「4.2 萬星爆紅！Craft Anything 是什麼？…」），沒有作者上傳的圖片。筆記計 1 張正確。
- **互動數**：159 讚、7 則回覆、20 轉發、239 分享、1.6 萬次瀏覽。
- **留言**：熱門與最新（`?sort_order=recent&filter_type=all`）兩種排序都捲到底，兩邊是同一批，畫面上沒有其他可展開的回覆：
  - 作者續樓 3 則（2/4、3/4、4/4）。
  - `b8601166`：問能不能逆向遊戲、有沒有案例。
  - `meta.ai`：回覆 b8601166，平台自動產生的 Meta AI 回答（下方有「私訊 Meta AI 以瞭解詳情」）。
  - `xinhuang700716`（19 小時前）：問能不能用舊網路遊戲的客戶端逆向做成單機遊戲。
  - 合計串內 6 則，貼文計數 7，差 1 則登入後也不顯示。
- **引用內容**：2 則。`mpbill531` 只引用、沒有文字；`yuminwellness` 只寫一個「學」字。兩則都沒有資訊內容。
- **判定**：`full`（兩種排序到底、無可展開回覆，差 1 則為平台不顯示）。但筆記的讀完度紀錄與留言內容有下列更正。

### 更正

1. **拿 meta.ai 自動回覆當證據**：筆記第 0 段「Threads 留言重點」寫 `@meta.ai` 彙整、「社群實測仍屬 Early Alpha（如 Chrome 小恐龍…）」「官方明言不繞過登入／DRM／反作弊」。這則是 Threads 平台的 Meta AI 自動回覆，不是網友實測、也不是官方說法；SOP 審查清單第 1 項規定平台自動產生的內容不是證據。
2. **漏讀網友留言**：`xinhuang700716` 問能不能用舊網路遊戲客戶端逆向做單機版，筆記沒寫。這則和 Deep 模式、DRM／智慧財產權邊界直接相關。
3. **漏寫引用貼文**：引用內容 2 則（`mpbill531`、`yuminwellness`），筆記第 0 段沒寫。SOP 第 3 節要求引用要讀完並寫進第 0 段（兩則都沒有資訊內容，寫一行即可）。
4. **讀完度紀錄自相矛盾**：`source_review_note` 寫用內建瀏覽器（未登入）只看到 2 則可見回覆、2 則未登入不顯示，卻標 `full`、`source_replies: 5`。依 SOP，未登入讀不全應標 `partial`；實際登入後是貼文計數 7、平台顯示 6 則（3 則作者續樓＋3 則留言）全部讀完、差 1 則登入後也不顯示，可以標 `full`，但紀錄要改成這個事實。

## 2. 事實查核（範圍 facts）

不在本次範圍（由 Codex 道負責）。另提一點供 Codex 道參考、不計入本次更正：貼文本身星數前後不一致（主貼文寫 41,000、4/4 寫 4.1 萬、連結卡寫 4.2 萬）。

## 3. 證據分級（範圍 evidence）

不在本次範圍。

## 4. 已完成任務的產出檔（範圍 task_impact）

不在本次範圍。

## 結論

`changes_requested`：4 處更正。

```json
{"verdict": "changes_requested", "source_review": "full", "source_images": 1, "source_replies": 6, "corrections": 4, "scope": ["source"], "findings": [{"kind": "source", "claim": "第 0 段「Threads 留言重點」：@meta.ai 彙整……社群實測仍屬 Early Alpha……官方明言不繞過登入／DRM／反作弊", "problem": "meta.ai 那則是 Threads 平台的 Meta AI 自動回覆，不是網友實測或官方說法；SOP 規定平台自動產生的內容不是證據", "evidence": "https://www.threads.com/@aiposthub/post/DgIWKmTATLX", "fix": "註明該則為平台自動回覆、不作證據；『不繞過 DRM』等說法若要保留，改引 craft-anything README 一手來源"}, {"kind": "source", "claim": "第 0 段留言重點只寫 b8601166 與 meta.ai", "problem": "漏讀 xinhuang700716 留言：問能否用舊網路遊戲客戶端逆向做成單機遊戲（登入後可見）", "evidence": "https://www.threads.com/@aiposthub/post/DgIWKmTATLX?sort_order=recent&filter_type=all", "fix": "第 0 段補這則留言，並連到 Deep 模式與 DRM／授權邊界的討論"}, {"kind": "source", "claim": "第 0 段未提引用貼文", "problem": "引用內容 2 則（mpbill531 無文字、yuminwellness「學」）未寫進第 0 段，SOP 第 3 節要求寫入", "evidence": "https://www.threads.com/@aiposthub/post/DgIWKmTATLX", "fix": "補一行：引用 2 則，皆無資訊內容；差額不用引用數補"}, {"kind": "source", "claim": "source_review_note：內建瀏覽器……2 則可見回覆（頁標 7 則，其餘 2 則未登入不顯示）；source_review: full；source_replies: 5", "problem": "未登入讀不全卻標 full，數字也和實際不符；登入後實為計數 7、平台顯示 6 則（3 續樓＋3 留言）", "evidence": "https://www.threads.com/@aiposthub/post/DgIWKmTATLX?sort_order=recent&filter_type=all", "fix": "改寫為『貼文計數 7 則，平台顯示 6 則（3 則作者續樓＋3 則留言）已全部讀完，差 1 則登入後也不顯示；引用 2 則另計』，source_replies 改 6"}], "task_impact": []}
```
