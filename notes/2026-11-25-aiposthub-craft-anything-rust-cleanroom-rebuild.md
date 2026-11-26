---
id: "2026-11-25-aiposthub-craft-anything-rust-cleanroom-rebuild"
title: "AI郵報 Threads 與 `storytold/craft-anything` 評析：純 Rust 320 項工具之 Clean-Room 逆向重建引擎與 Early Alpha 邊界"
source_url: "https://www.threads.com/@aiposthub/post/DgIWKmTATLX"
source_platform: "Threads (@aiposthub) / GitHub (storytold/craft-anything)"
author: "AI郵報 (@aiposthub) / storytold"
analyzed_at: "2026-11-25"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; codex/gpt-6.2-sol@01a21765-3f7c-7ed1-93a3-ae4311b8a38b"
revised_at: "2026-11-26"
source_review: full
source_images: 1
source_replies: 6
source_reviewed_at: "2026-11-26"
source_review_note: "依 2026-11-26 Chrome 登入審查報告，已讀主貼文、1 張連結預覽卡及平台顯示的全部 6 則串內回覆（3 則作者續樓、3 則留言）。貼文計數為 7 則，差 1 則登入後也不顯示。另讀 2 則引用，未計入串內回覆。本次修正採用審查報告的登入可見內容。"
status: pending
cluster: 2
cluster_role: "純Rust逆向重建"
short_title: "Craft Anything評析"
tags:
  - craft-anything
  - rust
  - reverse-engineering
  - clean-room
  - mcp
  - claude-code
  - game-rebuild
---

# AI郵報 Threads 與 `storytold/craft-anything` 評析：純 Rust 320 項工具之 Clean-Room 逆向重建引擎與 Early Alpha 邊界

- **來源貼文**：[Threads `@aiposthub`](https://www.threads.com/@aiposthub/post/DgIWKmTATLX)（分享短網址 [`__0IJjeWt`](https://www.threads.com/share/__0IJjeWt)，`2026-11-25 00:06`，`1.5 萬`瀏覽、`147` 讚、`7` 則留言；附導流連結 [`aiposthub.com/craft-anything-reverse-rebuild-20261124`](https://www.aiposthub.com/craft-anything-reverse-rebuild-20261124/)）
- **開源倉庫**：[`storytold/craft-anything`](https://github.com/storytold/craft-anything)（`MIT OR Apache-2.0`，`43,245` stars、`8,556` forks、`457` open issues，純 Rust 1.97+，狀態標示 `early alpha`）
- **分析日期**：`2026-11-25`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-19-rea-reverse-engineer-anything-agent.md`](./2026-10-19-rea-reverse-engineer-anything-agent.md)（`REA` 逆向工程代理與 Cleanroom 重造實測）
  - [`docs/reverse-engineering-pipeline-spec.md`](../docs/reverse-engineering-pipeline-spec.md)（本庫三階段逆向分析流水線規格目標文件）

---

## 0. 原始資料盤點（Threads 串文與 `storytold/craft-anything` README 實查）

- **四階段工作流（`Study → Build → Check → Ready`）**：
  1. **Study**：以真實檢測工具分析目標網站／App／遊戲（版面、字體、色彩、間距、檔案結構與行為），每項結論附帶證據。
  2. **Build**：呼叫本地 Coding Agent（優先實測 **Claude Code**，另支援經 ACP 介接 Copilot / Grok / Kimi / Gemini CLI / opencode / goose / Hermes / Maki / Devin，但多數 ACP 代理與 Codex adapter 尚未在實機全面驗證）依指定語言／框架從零建構新專案。
  3. **Check**：針對網站執行**三種螢幕寬度視覺比對**，針對遊戲執行自測，列出尚未吻合的差異並迭代修正。
  4. **Ready**：預覽／遊玩或繼續在底部對話框微調。
- **兩種模式與安全邊界（README 關鍵揭露）**：
  - **Clean room（預設）**：只讀可見外觀（截圖、文字、排版與視窗畫面），拒絕讀取目標原始碼、檔案或網頁原始碼。
  - **Deep**：啟用內建反組譯／反編譯引擎（原生二進位、.NET、Java、Android、Apple、Electron/JS、韌體、封包、資料庫與遊戲檔；已安裝 Ghidra 時亦會調用）。
  - **重要澄清**：README 明言 **Clean room 僅是工具層的拒絕規則，不是作業系統沙盒**——調用的 Coding Agent 仍以使用者本人權限運行。
- **純 Rust 引擎與 320 項工具（`crates/` 實查）**：
  - 13 個 crate（`ai`, `analysis`, `disasm`, `engine`, `engines`, `evidence`, `formats`, `js`, `mcp`, `platform`, `setup`, `testkit`, `ui-egui`），引擎層 300 工具＋AI／設定層 20 工具共 320 項，同時暴露為桌面 App（`egui`）、CLI（`craft-anything-cli`）與 MCP Server（`craft-anything-cli mcp`）。
  - 大型證據先回傳摘要再以 `core_evidence_browse` 分頁讀取；專案目錄結構固定為 `craft.json`、`capture/`、`app/`、`checks/`、`investigation.cany/`、`inbox/`。
- **Threads 留言與引用**（依 [2026-11-26 Chrome 審查報告](../reviews/reports/2026-11-25-aiposthub-craft-anything-rust-cleanroom-rebuild/2026-11-26-01-review-claude.md)）：
  - 網友 @b8601166 問能否逆向遊戲及是否有案例。@xinhuang700716 問能否把舊網路遊戲的客戶端做成單機版。兩則都是提問，沒有提供實測結果。
  - @meta.ai 的回覆由平台自動產生，無法佐證社群實測或專案官方政策。專案的 Early Alpha 狀態以倉庫 README 為準。
  - 兩則引用來自 @mpbill531（無文字）與 @yuminwellness（僅一字回應），都沒有技術補充。引用另計，未納入 6 則串內回覆。

---

## 1. 與本專案現有架構的對照與啟發

1. **對比本庫既有 `REA` 流水線（`docs/reverse-engineering-pipeline-spec.md`）**：
   - 本庫先前以 `rea-agents`（Node/JS）＋ Playwright ＋ `@electron/asar` 走通「觀測 → 逆向 → Cleanroom 重造」；`Craft Anything` 則將同一範式以**純 Rust + 320 MCP 工具**工程化，並補上兩項值得借鏡的規格：
     - **證據分頁與帳本（`evidence` + `unknowns` + `core_evidence_browse`）**：大型反編譯／網站分析結果不一次塞爆 Agent Context，強制先回摘要再分頁調閱。
     - **三視窗寬度自動比對（`checks/`）**：將前端／網站重建的驗收直接綁定三種螢幕寬度對照，並明確區分 `Clean room` 與 `Deep` 權限提示。
2. **現階段採納節制**：專案仍標示 `early alpha`（457 open issues、需 Rust 1.97+ 且多個 ACP 代理尚未實測），且本機已有 `SanHsien/rea` 驗證環境，暫不直接編譯或導入為依賴，先以規格對照方式吸收其優良契約。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261125-05`**｜**[優先級：低]** 唯讀對照 `storytold/craft-anything` 的 `Study → Build → Check → Ready` 目錄契約、`core_evidence_browse` 分頁模式與三視窗視覺比對規格，補入 `docs/reverse-engineering-pipeline-spec.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\reverse-engineering-pipeline-spec.md`（收錄於集群 2；僅做規格對照，不編譯或安裝 Early Alpha 二進位依賴）
  - **執行步驟**：
    1. 在 `docs/reverse-engineering-pipeline-spec.md` 補充 `Craft Anything` 與 `REA` 的架構對照表（Clean room vs Deep 模式邊界、證據先摘要後分頁 `core_evidence_browse`、專案標準目錄 `capture/` / `checks/` / `inbox/`）。
    2. 明註「Clean room 非 OS 沙盒」與「不繞過 DRM／登入／反作弊」之合規與安全前提。
  - **驗收標準（DoD）**：`docs/reverse-engineering-pipeline-spec.md` 完成對照節補充，且 `python tools/verify_inbox.py` 驗證通過。
