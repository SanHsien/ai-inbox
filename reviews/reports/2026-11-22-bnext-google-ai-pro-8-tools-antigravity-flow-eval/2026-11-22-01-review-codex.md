# 獨立審查報告：2026-11-22-bnext-google-ai-pro-8-tools-antigravity-flow-eval

- reviewer: codex/gpt-6.1-sol@01a2027d-da28-7f32-820d-92528c52e064
- content_sha256: 3e2712f7374db77b41a48b1a9c262e60ed788f619a82846ebad1a5a377fc0926
- role: review；lane: codex；scope: facts, evidence, task_impact
- reviewed_at: 2026-11-22
- verdict: changes_requested；corrections: 5；source_review: full（作者聲明 full）
- source_ref: codex thread 01a2027d-da28-7f32-820d-92528c52e064

---
結論：**changes_requested，共 5 處更正**。已審完 `facts`、`evidence`、`task_impact`；原文無法開啟，`source` 留待補審。未修改任何檔案。

1. **原始資料讀完度（source）**

   [原始文章](https://www.bnext.com.tw/article/93098/google-ai-pro-8-tools-features-tutorial)及短網址均無法讀取，因此未核實作者、發布日期、8 張圖片與留言計數。實際看圖 0 張、讀留言 0 則，不能據此判定來源沒有圖片或留言。

   依交付規則，保留作者的 `full` 聲明，從結果 `scope` 移除 `source`；上述讀取限制不列為更正。

2. **事實查核（facts）**

   - **F1：混淆 Flow 點數與跨產品 AI 點數。** 每日 50 點、Pro 每月另加 1,000 點的數字正確，但官方稱為 Google Flow credits；Antigravity 超額使用的是購買或一次性促銷的 AI credits。應分開畫出兩種點數，避免暗示訂閱附贈的 Flow 點數可供 Antigravity 扣抵。[Flow 官方說明](https://support.google.com/flow/answer/16526234?hl=en)、[Antigravity 方案](https://antigravity.google/docs/plans)
   - **F2：跨產品點數圖漏列 Gemini。** Gemini 有自己的基本用量限制，但官方也列明符合資格者可購買 AI 點數，增加 Gemini、Flow、Antigravity 的使用量。不能將 Gemini 完全隔離在跨產品點數層之外。[Google One 官方說明](https://support.google.com/googleone/answer/16287445)
   - **F3：超額點數開關位置寫錯。** 官方將開關列在 Antigravity 的 `Settings > Models`；Google One 頁面用於查看點數與活動，筆記未提供它能設定該開關的證據。[Antigravity 設定文件](https://antigravity.google/docs/settings)
   - **F4：API 配額與計費混寫。** Gemini API 限流按專案計算，並非每把 API Key 獨立計算；RPM／TPM 是用量上限，不是價格單位。應分開說明專案配額與模型計價。[API 限流文件](https://ai.google.dev/gemini-api/docs/rate-limits)、[API 價格文件](https://aistudio.google.com/docs/pricing)

   另已確認 NotebookLM 更名為 Gemini Notebook，這項不需更正。[Google 官方公告](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/)

3. **證據分級（evidence）**

   - **一手已確認**：上述點數數字、Antigravity 基本配額與超額選項、更名資訊。
   - **二手來源待核**：筆記轉述的報導實測、圖片內容與操作示例；本次未讀到原文，不判定其真偽。
   - **F5：將工作目錄選擇推論成安全隔離。** 建立獨立資料夾是操作建議，不能單憑掛載專案就宣稱已形成安全邊界。官方明列不同權限模式：部分允許暫存目錄、核准後的外部存取，Turbo 可存取完整檔案系統。應將此段改成建議，並補上實際權限、沙箱與核准設定。[官方權限文件](https://antigravity.google/docs/permissions)

4. **任務影響（task_impact）**

   本篇僅有 `T-20261122-03`，尚未完成；預定產出 `docs/google-ai-pro-ecosystem-and-credit-routing.md` 目前不存在，沒有已完成產出需要追修。

   後續實作前，應先修正點數分類、開關位置及目錄隔離前提，再據此撰寫文件。

```json
{
  "verdict": "changes_requested",
  "source_review": "full",
  "source_images": 0,
  "source_replies": 0,
  "corrections": 5,
  "scope": ["facts", "evidence", "task_impact"],
  "findings": [
    {
      "kind": "fact",
      "claim": "第 2 節將 Flow 每日及每月贈送點數列入跨產品 AI 點數層",
      "problem": "官方區分 Google Flow credits 與 AI credits；Antigravity 超額使用購買或一次性促銷的 AI credits，不能暗示訂閱附贈的 Flow 點數可跨產品扣抵。",
      "evidence": "https://support.google.com/flow/answer/16526234?hl=en ; https://antigravity.google/docs/plans",
      "fix": "分開列出 Flow 專用點數與跨產品 AI 點數，保留每日 50 點及 Pro 每月另加 1,000 點的正確數字。"
    },
    {
      "kind": "fact",
      "claim": "第 2 節將 Gemini App 僅列入獨立隔離額度層",
      "problem": "官方列明符合資格者可購買 AI 點數，增加 Gemini、Flow 與 Antigravity 的使用量；圖中漏列 Gemini 的額外點數使用。",
      "evidence": "https://support.google.com/googleone/answer/16287445",
      "fix": "區分基本用量上限與額外 AI 點數，將 Gemini 納入符合資格功能的跨產品點數說明。"
    },
    {
      "kind": "fact",
      "claim": "第 2 節將超額點數開關定位於 Google One 管理介面",
      "problem": "官方設定文件將 AI credit overages 開關列在 Antigravity 的 Settings > Models；未找到 Google One 可設定該開關的一手證據。",
      "evidence": "https://antigravity.google/docs/settings ; https://support.google.com/googleone/answer/16287445",
      "fix": "改列 Antigravity Settings > Models；Google One 僅按已確認功能說明點數查詢與活動紀錄。"
    },
    {
      "kind": "fact",
      "claim": "第 1 節以 API Key 方案與 RPM/TPM 說明 AI Studio 計費",
      "problem": "Gemini API 限流按專案而非 API Key 計算；RPM/TPM 是限流維度，不是計價單位。",
      "evidence": "https://ai.google.dev/gemini-api/docs/rate-limits ; https://aistudio.google.com/docs/pricing",
      "fix": "分開說明專案層級的配額、免費與付費層級，以及各模型的實際計價方式。"
    },
    {
      "kind": "evidence",
      "claim": "第 3 節將建立並掛載獨立資料夾視為安全邊界防護",
      "problem": "工作目錄選擇不等於強制隔離。官方權限模式可允許暫存目錄、核准後的外部存取，Turbo 更可存取完整檔案系統；筆記將操作建議推論成安全保證。",
      "evidence": "https://antigravity.google/docs/permissions",
      "fix": "改標為安全操作建議，並說明邊界取決於權限模式、沙箱、允許與拒絕規則及外部存取核准。"
    }
  ],
  "task_impact": []
}
```
