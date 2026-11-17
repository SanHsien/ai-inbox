---
id: 2026-11-06-fengxue-ida-pro-ai-mcp-reverse-engineering-concern
title: "風雪之閣「IDA 接上 AI，逆向工程最後一哩路」貼文評估：ida-pro-mcp／GhidraMCP 現況查證與既有 REA 逆向流水線對照"
source_url: "https://www.facebook.com/100063915135662/posts/1601705495303273/"
source_platform: "Facebook (風雪之閣)"
author: "風雪之閣 (@cooldotnet)"
analyzed_at: 2026-11-06
analyzed_by: "Antigravity"
status: archived
cluster: "3"
cluster_role: "逆向工程與軟體封裝"
short_title: "IDA接AI逆向貼文評估"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 0
source_replies: 10
tags:
  - reverse-engineering
  - ida-pro
  - ghidra
  - mcp
  - ida-pro-mcp
  - ghidra-mcp
  - client-side-secrets
---

# 風雪之閣「IDA 接上 AI，逆向工程最後一哩路」貼文評估：ida-pro-mcp／GhidraMCP 現況查證與既有 REA 逆向流水線對照

- **來源連結**：[Facebook 貼文：風雪之閣](https://www.facebook.com/100063915135662/posts/1601705495303273/) ｜ [分享短網址](https://www.facebook.com/share/1CQPaZRbZS/)
- **發布時間**：2026-11-04 17:27 (UTC+8)（2026-11-16 重審時：92 個心情、10 則留言、15 次分享）
- **歸屬集群**：集群 3（角色：`AI 輔助逆向工程現況對照`）
- **評估結論**：`🟡 資訊價值低、主題已覆蓋`：不衍生新任務，併入既有 REA 逆向筆記脈絡
- **相關交叉參照**：
  - [`notes/2026-10-19-rea-reverse-engineer-anything-agent.md`](./2026-10-19-rea-reverse-engineer-anything-agent.md)（REA：統一 MCP 橋接 Ghidra／Hopper／IDA／JADX／CDP，已在 Windows 11 沙箱實測，T-20261019-09）
  - [`docs/reverse-engineering-pipeline-spec.md`](../docs/reverse-engineering-pipeline-spec.md)（三階段逆向流水線與 Cleanroom 邊界）
  - [`docs/rea-sandbox-evaluation-evidence.md`](../docs/rea-sandbox-evaluation-evidence.md)（Ghidra 12.2 + JDK 21 沙箱 SHA-256 驗證證據）

---

## 0. 原始資料盤點

> 2026-11-16 重審：未登入可讀貼文全文與留言。2026-11-17 登入後改用「所有留言」排序、回覆串全部展開，10 則全部讀完。

- **作者圖片**：無。貼文是純文字，沒有附圖、影片或連結預覽卡（頁面上只有頭像與表情圖示）。
- **作者留言補充**（2 則回覆）：
  - 回 `謝博文`：同意「某些情境下 AI 不靠 IDA 就能逆向」，但認為單步執行、記憶體傾印、暫存器追蹤才是真正的殺手級能力。
  - 回 `Franma Hsu`：自己做過類似工具，但不會公開。
- **網友留言重點**（頁面標示 10 則，含作者 2 則回覆，全部讀完）：
  - `王景弘`、`Weber Tsai`、`Jie Liau`：這不是新東西，半年前到兩年前就有人接上了。
  - `謝博文`：現在的 AI 連 IDA 都不需要就能直接逆向。
  - `楊朝鈞`：AI 反組譯的速度很驚人。
  - `一人公司研究所`（上次被「最相關」排序濾掉的那一則）：只寫「BLA來了」並貼一支約 2 分鐘的 Facebook Reels 連結，沒有任何說明，也沒有提到 repo；屬於貼連結導流，不納入分析。
  - 其餘為感嘆與玩笑。
  - 沒有任何留言或作者回覆指出 repo 名稱。
- **對分析的影響**：
  - 原寫「附圖在抓取時無法取得」不正確，貼文本來就沒有圖；已更正第 1 節。
  - 發布時間原寫「09:27 (UTC+8)」，頁面顯示下午 5:27，原值其實是 UTC；互動數一併更新。
  - 作者的回覆把重點從「靜態反編譯」移到「動態除錯」（單步、記憶體傾印、暫存器）。`ida-pro-mcp` 的說明也列有選用的 debugger 控制，與此相符；已補進第 4 節的防守端含意。
  - 2026-11-17 補讀的第 10 則留言沒有新的技術資訊，分析不用改。
  - repo 名稱仍無法由原始資料確認，第 2 節維持「最可能的對象」的寫法。結論（不衍生任務）不變。

---

## 1. 貼文原文重點

> 昨天看到一個 github repo，把 IDA 接上 ai，這下好了，逆向工程的最後一哩路……我怎麼覺得整個風向往壞的走。
> IDA 是 soft ice 的接班者，反組譯的王者，可以直接把機器碼逆向成 c，而且還可以下中斷點、單步執行；配上網路封包攔截的軟體，在 ai 的助力下，整個就是裸奔了。

- 貼文**沒有寫出 repo 名稱**，也沒有附圖或連結（2026-11-16 重審確認是純文字貼文）；以下依時間與描述比對最可能的對象。
- 留言多數指出「不新」：「半年前就一狗票人玩了」「我兩年前就接上去了」「這不是很早就有人在玩了」。作者回覆自己做過類似工具但「暗的東西不會放出來」。
- 另有留言說現在的 AI 不靠 IDA 也能逆向；作者同意，但強調單步執行、記憶體傾印與暫存器追蹤才是關鍵。

## 2. 查證：最可能的 repo 與現況

以 GitHub API 於 2026-11-06 查詢（星數為快照日 2026-11-06 的數字，之後會變動）：

| Repo | Stars | 建立 | 最近推送 | 授權 | 說明 |
| --- | --- | --- | --- | --- | --- |
| [`mrexodia/ida-pro-mcp`](https://github.com/mrexodia/ida-pro-mcp) | 13,384 | 2025-03-25 | 2026-09-26 | MIT | IDA Pro ↔ MCP；反編譯、xrefs、call graph、可寫回改名／註解／型別；選用 debugger 控制；`idalib` headless 模式 |
| [`LaurieWired/GhidraMCP`](https://github.com/LaurieWired/GhidraMCP) | 11,783 | 2025-03-23 | 2026-10-10 | Apache-2.0 | Ghidra ↔ MCP，免費替代路線 |

- `ida-pro-mcp` 需 **IDA Pro 8.3+（建議 9+）與 Python 3.11+；IDA Free 不支援**。
- 兩者都已發布超過 **19 個月**，留言「早就有人在玩」屬實。貼文是個人感想，不是新消息。

## 3. 和既有能力的對照

```text
             反編譯核心          AI 橋接層            本 repo 狀態
IDA Pro  ──► ida-pro-mcp   ──┐
Ghidra   ──► GhidraMCP     ──┼──► MCP client（Claude / Codex / Antigravity）
Ghidra/JADX/CDP ──► REA ─────┘    └─ REA 已在 Windows 11 沙箱實測（207 個 MCP tools）
```

- **功能重疊**：REA 已統一橋接 Ghidra／IDA／JADX／CDP，並有 SHA-256 驗證的 Ghidra 12.2 沙箱。再單獨導入 GhidraMCP 價值有限。
- **IDA 路線卡在授權**：需付費 IDA Pro，沒有授權就無從實測。不應為此開一個做不完的任務。

## 4. 貼文真正值得留下的一點：防守端含意

作者的擔憂方向是對的：AI + 反編譯 + 封包攔截讓「讀懂別人的二進位」的門檻大降。對自己的專案，結論只有一條：

> **任何送到使用者端的東西（exe、APK、Electron `app.asar`、前端 JS）都要假設會被完整讀懂。** API key、私鑰、授權驗證邏輯不能只靠混淆或編譯隱藏，必須放在伺服器端。

作者在留言補充的重點是動態除錯：只要程式在對方機器上跑，記憶體裡解開的金鑰與執行流程都看得到，所以「執行時才解密」同樣擋不住，結論仍是機密不落地到用戶端。

這條與既有 [`docs/reverse-engineering-pipeline-spec.md`](../docs/reverse-engineering-pipeline-spec.md) 的 Cleanroom 邊界，以及 LLMJacking 筆記的憑證不落地原則一致，不另立新規則（規則淨零增長）。

## 5. 待辦

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

本篇**不衍生新任務**。理由：主題已由 REA 筆記與逆向流水線規格覆蓋；IDA 路線需要付費授權才能實測。若日後取得 IDA Pro 授權，再以 REA 筆記的沙箱流程比照實測 `ida-pro-mcp`。
