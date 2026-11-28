# 獨立審查報告：2026-11-26-vvsvs-cinematique-prompt-library

- reviewer: codex/gpt-6.1-sol@01a222c5-1544-7da2-83c1-14ba5bea4b17
- content_sha256: 8f08537208962ac7ca72b0076cbf58bfedb050f91b4af83a86149551d322dd3e
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）
- source_ref: codex thread 01a222c5-1544-7da2-83c1-14ba5bea4b17

---
結論：`changes_requested`，共 3 處需更正。筆記雜湊與指定值相符；未修改任何檔案。

### 1. 原始資料讀完度（source）

已重新讀取官方主頁、三篇技巧指南及電腦王阿達報導文字，但未逐張檢視圖片、播放參考影片或驗證動態留言。

因此本次 **不對 source 下結論，從 scope 移除**；保留作者的 `full` 聲明，不因審查工具限制下修。實際檢視圖片 0 張、留言 0 則；留言總數未確認，不能認定為零。

### 2. 事實查核（facts）

確認相符：

- Ivan Flugelman 與 VVSVS 的關係，可由[官方介紹](https://vvsvs.pro/info)確認。
- 150 項技巧、七類及各類數量，與[官方商品頁](https://vvsvs.pro/shop/cinematique)一致；同頁確認電子書標價 $29、387 頁、41 支參考短片。
- 課程標價 $250，與[官方課程頁](https://vvsvs.pro/academy)一致。
- 三筆範例的提示詞、使用時機、AI 指導、常見錯誤及參考連結，與官方 [Aerial Shot](https://vvsvs.pro/cinematique/aerial-shot)、[Close-Up](https://vvsvs.pro/cinematique/close-up)、[Three-Point Lighting](https://vvsvs.pro/cinematique/three-point-lighting) 指南相符。
- Rocky 與 2026-09-14 的報導日期，與[報導頁](https://www.kocpc.com.tw/archives/668865)一致。

三項難度、八種情緒、媒體格式與互動視窗細節，現有文字頁不足以完整確認，不判定為錯誤。

### 3. 證據分級（evidence）

上述作者、商品規格及指南內容屬一手來源；電腦王阿達對工具效果的介紹屬二手轉述。以下三處把未確認事項寫得過於確定：

1. **來源沿革與授權缺少可重現證據。**  
   筆記將改編自 grokfilm.app、開源宣稱及商用許可寫成實機確認；本次[官方主頁](https://vvsvs.pro/cinematique)文字未呈現這些資訊。這不證明作者當時看錯，但需補分析當日快照、具體段落或條款網址；否則應標為歷史觀察、目前無法重現。免費使用也不足以單獨證明開源授權。

2. **資料部署方式與介面不存在的結論過強。**  
   筆記從頁面未見入口，延伸到未公開倉庫、API、JSON 匯出，以及資料全部打包於前端。[官方主頁](https://vvsvs.pro/cinematique)不能證明完整部署方式。應限縮為「本次檢視頁面未見相關入口」，除非補上原始碼或網路請求證據。

3. **改善生成穩定性的效果未驗證。**  
   筆記將具體攝影詞彙能降低畫面不穩定寫成效果結論；[官方指南](https://vvsvs.pro/cinematique/close-up)提供的是提示詞起點，沒有比較實驗。應改為預期用途，註明未做跨模型對照測試。

另：筆記缺少規範要求的原始資料盤點段落；因本次未完成 source 審查，僅提醒後續補審者核對，不另計 finding。

### 4. 任務影響（task_impact）

本篇為 `archived`，沒有任務 ID、已完成任務或指定產出檔，無任務產出需回查。

下一步由整合者修正三處證據措辭，再補來源圖片、影片及留言審查。

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
      "claim": "核心結論及第二節將 grokfilm.app 改編來源、開源宣稱與商用許可列為實機確認事項。",
      "problem": "本次可讀的官方頁面未呈現這些聲明，無法重現筆記記載的歷史觀察；不能據此斷言原記錄錯誤，但目前證據不足以維持確定語氣。",
      "evidence": "https://vvsvs.pro/cinematique",
      "fix": "補分析當日快照、具體來源段落或授權條款網址；否則標明為作者當時觀察、目前無法重現，並分開說明免費使用與開源授權。"
    },
    {
      "kind": "evidence",
      "claim": "核心結論及第二節斷言未公開倉庫、API、JSON 匯出，並判定全部資料打包於前端。",
      "problem": "頁面未見入口只能支持觀察範圍內未找到，不能證明介面不存在，也不能證明完整部署方式。",
      "evidence": "https://vvsvs.pro/cinematique",
      "fix": "限縮為本次檢視頁面未見相關入口；資料部署方式若要保留，須補原始碼或網路請求證據。"
    },
    {
      "kind": "evidence",
      "claim": "第三節將攝影詞彙組合描述為能降低生成畫面不穩定。",
      "problem": "官方指南提供提示詞起點，未提供比較實驗；筆記也沒有跨模型對照結果，效果仍屬推論。",
      "evidence": "https://vvsvs.pro/cinematique/close-up",
      "fix": "改為可作為具體描述攝影意圖的參考，註明是否改善穩定性尚未實測。"
    }
  ],
  "task_impact": []
}
```
