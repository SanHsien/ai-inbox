# 獨立審查報告：2026-11-16-darkschen-open-weights-google-drive-backup

- reviewer: codex/gpt-6.1-sol@01a22195-53bf-76e1-bad2-923746444f6c
- content_sha256: 6fe1253c7bef07af736802a2bbddba4049180e208f63b5ade730689839ad9006
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 3；source_review: full（作者聲明 full）
- source_ref: codex thread 01a22195-53bf-76e1-bad2-923746444f6c

---
結論：`changes_requested`，共 **3 處更正**。未修改任何檔案；審查結束時內容雜湊與指定值相同。

1. **原始資料讀完度：不在本次範圍**

   未重讀 Facebook 圖片與留言。保留作者 `source_review: full`，不代表本次重新確認。作者身分、貼文日期、截圖清單及留言轉述，需 Chrome 道查核。

2. **事實查核**

   已確認 Google AI Pro 提供跨 Gmail、Drive、Photos 共用的 5TB 空間；Mac Studio 有 512GB 統一記憶體選項；GLM-5.3 官方模型頁列出 753B。[Google 方案](https://one.google.com/intl/en/about/google-ai-plans/)、[Apple 規格](https://www.apple.com/mac-studio/specs/)、[GLM-5.3](https://huggingface.co/zai-org/GLM-5.3)

   **更正 1：限速只能作為有條件的估算。**  
   筆記第 2、3 節將 `8 MB/s` 寫成足以避開 750GB 限制。以十進位計算，連續 24 小時約傳 691.2GB；但官方限制涵蓋每位使用者的上傳與複製總量，其他作業也會占額度。此外，查到的數字出自 Workspace 文件，不能直接當成已確認的 AI Pro 個人帳號條款。應補上適用帳號、總流量及計算假設。[Google 官方限制](https://knowledge.workspace.google.com/admin/drive/storage-and-upload-limits-for-google-workspace)

3. **證據分級**

   - **一手確認**：上述方案與硬體規格；模型發布者列出的下載檔約 16.55GB、SHA-256 與本機清單記錄一致。本次也確認本機檔案大小及 `GGUF` 檔頭，但未重新計算整檔雜湊。[模型檔案頁](https://huggingface.co/0bserverx/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF/blob/main/RVN-Q4_K_M-multilingual.gguf)
   - **二手轉述**：網友的取回成本、寬頻限流、Colab 提速及其他模型下架經驗；維持具名歸因，不能視為官方結論。
   - **推算／未查證**：限速保證、全站最小容量、本機推論能力。

   **更正 2：搜尋結果不能寫成全面排除。**  
   第 4 節列出的四個最小容量，可在 `D:\AgentData\uncensored-open-models\MANIFEST.md` 找到相同記錄；但該檔只有代表性倉庫，沒有可重查的完整搜尋快照與固定版本。應改成「截至查詢日，在所列倉庫中未找到符合 22GB 門檻的獨立模型」，並補各檔案網址及版本。這不是認定容量錯誤，而是更正證據能支持的範圍。

   **更正 3：下載驗證不能證明本機可運行。**  
   第 4 節結案語氣超出證據。上述清單記錄的是檔頭與雜湊檢查，沒有這台電腦的載入指令、推論輸出或記憶體用量。發布者的測試也不能替代本機驗收。應改成「下載與完整性檢查完成，本機推論尚未驗證」。[本機清單](D:/AgentData/uncensored-open-models/MANIFEST.md)、[發布者測試說明](https://huggingface.co/0bserverx/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF/raw/main/README.md)

4. **已完成任務產出**

   本篇沒有 `T-...` 任務，第 3 節明確決定不建立工程任務。已讀第 4 節引用的本機清單；其問題已列入更正 2、3，沒有已完成任務需要連帶修正。

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
      "kind": "evidence",
      "claim": "第2、3節將8 MB/s限速描述為可避開Google Drive每日750GB限制。",
      "problem": "速率換算只是有條件估算；官方限制包含同一使用者的上傳與複製總量，且所查官方文件適用Workspace，尚未確認AI Pro個人帳號的相同條款。",
      "evidence": "https://knowledge.workspace.google.com/admin/drive/storage-and-upload-limits-for-google-workspace",
      "fix": "補上8 MB/s連續24小時約691.2GB的計算假設，計入其他上傳及複製流量，並標明個人帳號適用條款尚待確認；移除保證避開限制的語氣。"
    },
    {
      "kind": "evidence",
      "claim": "第4節將四款模型列為查證無22GB以下版本，並列出最小容量。",
      "problem": "本機清單只有代表性倉庫與整理結果，缺少完整搜尋快照及固定版本，不能支持全站不存在更小版本的結論。",
      "evidence": "notes/2026-11-16-darkschen-open-weights-google-drive-backup.md:91-92；D:/AgentData/uncensored-open-models/MANIFEST.md",
      "fix": "限定為截至查詢日、在所列倉庫中未找到符合22GB門檻的獨立模型；補上各量化檔案網址、分片總和與固定版本。"
    },
    {
      "kind": "evidence",
      "claim": "第4節以可運行的無審查版已全數完成作為結案結論。",
      "problem": "清單僅記錄下載、GGUF檔頭與SHA-256驗證，沒有指定本機硬體的載入及推論紀錄；發布者測試不能替代本機驗收。",
      "evidence": "D:/AgentData/uncensored-open-models/MANIFEST.md；https://huggingface.co/0bserverx/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF/raw/main/README.md",
      "fix": "改成下載與完整性檢查完成、本機推論尚未驗證；若保留可運行結論，補上執行版本、指令、上下文長度、記憶體用量及成功生成輸出的紀錄。"
    }
  ],
  "task_impact": []
}
```
