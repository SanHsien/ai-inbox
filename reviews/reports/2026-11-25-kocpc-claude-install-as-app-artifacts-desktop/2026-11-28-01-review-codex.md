# 獨立審查報告：2026-11-25-kocpc-claude-install-as-app-artifacts-desktop

- reviewer: codex/gpt-6.1-sol@01a2225a-6f06-74d0-8a8b-cef2bc02fe49
- content_sha256: 1156054708b9aa060c4c2315c7cbf681c738fd71034613d4da66726d29509f73
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-28
- verdict: changes_requested；corrections: 2；source_review: full（作者聲明 full）
- source_ref: codex thread 01a2225a-6f06-74d0-8a8b-cef2bc02fe49

---
結論：**changes_requested，共 2 處更正**。完成 `facts`、`evidence`、`task_impact`；`source` 未完成，不納入結論。未修改任何檔案。

內容雜湊與指定值一致：`1156054708b9aa060c4c2315c7cbf681c738fd71034613d4da66726d29509f73`。

### 1. 原始資料讀完度（source）

已讀[原文文字](https://www.kocpc.com.tw/archives/704598)，作者與刊登日期符合筆記。但四張配圖均載入失敗，內嵌影片未完整檢視，留言區也未完成獨立確認。

因此排除 `source`，保留作者的 `full` 聲明，不把本次存取限制列為錯誤。實際看過圖片 0 張；留言未完成核對，以 `-1` 表示未審。

### 2. 事實查核（facts）

三級權限、更新後重問授權、免費方案開放、連網登入要求及方案額度計費，均有[官方公告](https://claude.com/resources/articles/install-as-app)支持。

**更正 1：安裝範圍過度概括**

位置：筆記第 0 節功能定位。

筆記將所有 Artifact 都列為可安裝，與官方限制不符。Docs、Slides、Sheets 等範本產物、舊版 Artifacts，以及 Cowork 的 live artifacts 均有排除。

建議改為「支援的 Artifact 可安裝」，並列出例外。[官方說明：Current limitations](https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app)

### 3. 證據分級（evidence）

- **一手確認**：三級權限、自動更新、本人／同組織作者限制、安裝前不審查、解除安裝撤權等功能，可由官方公告及說明文件核對。
- **二手來源**：Rocky 的文章敘述及配圖盤點；本次未看清配圖，不替其內容背書。
- **推論**：安全模型的效果評價，必須與官方已證實的機制分開。

**更正 2：遺漏外部程式碼例外，將安全效果寫得過強**

位置：第 0 節版本授權說明、第 1 節第 1 點。

官方明列：App 從其他網站載入的程式碼，可能變更而不觸發再次授權。因此，不能由版本重授權機制推論能完整防止取得信任後的惡意更新。

```text
Artifact 版本更新 → 重新詢問授權
外站程式碼變更   → 可能不重新詢問
```

建議補上例外，將安全效果改為「降低 Artifact 版本更新風險；外部依賴仍有殘餘風險」，並標為分析判斷。[官方說明：Permissions](https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app)

### 4. 任務影響（task_impact）

本篇只有 `T-20261125-03`，仍未完成。已查看 `docs/visual-agent-artifacts-engineering-spec.md`，未見本篇提出的桌面化章節，因此沒有已完成產出需要回修。

整合者實作時應納入上述兩項限制，避免把過強的安全結論寫進規格。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": -1,
  "corrections": 2,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 0 節將 Artifact 全部列為可直接安裝的桌面程式。",
      "problem": "官方列有不可安裝的類型，包括 Docs、Slides、Sheets 等範本產物、舊版 Artifacts 與 Cowork live artifacts。",
      "evidence": "https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app",
      "fix": "改為支援的 Artifact 可安裝，並補列官方排除類型。"
    },
    {
      "kind": "evidence",
      "claim": "第 0 節及第 1 節把版本重授權延伸為能防堵取得信任後的惡意更新。",
      "problem": "官方明列外站載入的程式碼可變更而不重新請求授權；筆記遺漏此例外，並將安全效果推論寫成確定結論。",
      "evidence": "https://claude.com/resources/articles/install-as-app ; https://support.claude.com/en/articles/18516354-install-an-artifact-as-an-app",
      "fix": "補上外部程式碼更新例外，將安全效果改為降低 Artifact 版本更新風險，保留外部依賴風險，並標明是分析判斷。"
    }
  ],
  "task_impact": []
}
```
