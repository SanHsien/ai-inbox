---
id: 2026-10-24-feedback-desk-client-ticket-ai-handoff
title: "feedback-desk 解構：客戶開單 × 多 AI 認領與交接的輕量工單系統（Cloudflare Workers 免費版／Laravel 主機版）、MCP 接入 Claude Code 與 Codex，及與本地交接機制的對照"
source_url: "https://github.com/aixwangtw/feedback-desk"
source_platform: "Threads / GitHub"
author: "aixwangtw（部落格：aixwang.dev）"
analyzed_at: 2026-10-24
analyzed_by: "Antigravity"
status: pending # pending | in-progress | done | archived
cluster: 3
cluster_role: "多 Agent 協作與交接"
short_title: "feedback-desk 客戶工單與 AI 交接"
tags:
  - feedback-desk
  - ticketing
  - ai-handoff
  - mcp
  - cloudflare-workers
  - claude-code
  - codex
---

# feedback-desk 解構：客戶開單 × 多 AI 認領與交接的輕量工單系統（Cloudflare Workers 免費版／Laravel 主機版）、MCP 接入 Claude Code 與 Codex，及與本地交接機制的對照

- **來源連結**：[GitHub aixwangtw/feedback-desk](https://github.com/aixwangtw/feedback-desk)；作者介紹文：[aixwang.dev/blog/feedback-desk](https://aixwang.dev/blog/feedback-desk/)（介紹文我未讀取，內容以貼文與 repo README 為準）
- **發布平台 / 作者**：`Threads` + `GitHub` / `aixwangtw`
- **查證數據（2026-10-24 以 GitHub API 取得）**：MIT 授權、TypeScript、約 31 Stars、最後推送 2026-10-20、分支 `main`（Cloudflare 版）／`cloudflare`／`laravel`（主機版）
- **分析日期**：`2026-10-24`
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-21-agent-relay-pipeline-phase4.md`](./2026-10-21-agent-relay-pipeline-phase4.md)（本地多 Agent 派工與驗收）
  - [`notes/2026-10-23-zeabur-october-2026-security-incident.md`](./2026-10-23-zeabur-october-2026-security-incident.md)（貼文提到 Cloudflare 版是作者在 Zeabur 倒掉後做的替代方案）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：接案開發者 aixwangtw，同時做 3 個專案，每案有客戶、夥伴與各自的 AI。
- **What**：開源工單／回報系統。客戶開單附截圖，開發端（人或 AI）讀單、修改、寫附圖的調整說明、改成「待審核」，客戶確認後結案。
- **Why**：訊息散落多處，沒有統一 API 讓 AI 讀需求與互相交接。
- **How**：

```text
客戶開單(+截圖) → CC 排程定時讀單 → AI 修改並驗證 → 寫簡潔調整說明
      → 狀態「待審核」 → 客戶確認 → 「已完成」
多 AI：認領（誰在處理）＋交接紀錄（下一個人/AI 讀單先看到）
      每個動作記錄「帳號＋AI 工具」，如「王小明（Codex）」
```

- **技術堆疊（README）**：Hono + D1 + R2，Cloudflare Workers 免費方案；一個 CLI 完成 init、deploy、建帳號、連接 AI；MCP（Streamable HTTP）與命令列雙通道；UI 為繁體中文。
- **身分模型**：客戶（專屬連結或個人帳號）、開發團隊 owner、公開回報者（選用，私密網址追蹤）。
- **使用者澄清**：它是**工單系統**（管每個任務），不是 CRM（管客戶名單）。
- **When & Where**：多人加多 AI 的接案、需要客戶確認閉環的場景。

> [!NOTE]
> 貼文數字與流程已與 README 對照，大致一致。README 明言對 OpenClaw、Hermes、Grok 的 MCP 設定「沒有實際測過」。貼文提到的 Opus 5.5 與排程做法是作者個人搭配，未驗證。

---

## 2. 官方 GitHub 與技術規格細節

- **安裝**：npm 套件尚未發佈，一律用 `npx --allow-git=all github:aixwangtw/feedback-desk <子命令>`；需 Node 20+、Cloudflare 免費帳號、啟用 R2。
- **主要子命令**：`init`、`deploy`、`bootstrap`、`login`（裝置碼授權）、`project create`、`client create`、`developer create`、`mcp install`、`mcp token --agent`。
- **AI 接入**：`mcp install` 為 Claude Code 與 Codex 各發獨立 token，存 `~/.config/feedback-desk/mcp/`；設定檔不含 token。其他 agent 以環境變數 `FEEDBACK_DESK_MCP_TOKEN` 與 `Authorization: Bearer` 標頭接入。
- **平台限制**：README 的指令說明寫「Linux、macOS 終端機（Windows 可用 WSL）」，而本機是 **Windows 11 原生、無 WSL**，原生可行性未知。
- **安全面**：`login` 的 token 預設不會到期（可 `--expires` 設定）；README 提示不要在非自己發起的 login 頁面授權。部署提示詞明確要求 AI 不看密碼、不把 token 寫進對話。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與 `agent-relay` 的派工、交接、驗收閉環概念重疊：認領、交接紀錄、動作署名（帳號＋AI 工具）、「待審核→已完成」的人工確認閘門，可對照取長補短。
  - 本 repo 的 `T-` 任務與 DoD 就是一種內部工單；feedback-desk 多出的是**客戶端入口與截圖留言串**。
- **落差與採納判斷**：
  - **值得採納**：先實測 Windows 11 原生是否可部署；並對照它的認領／交接欄位，看是否補強 `agent-relay`。
  - **需調整**：需 Cloudflare 帳號與 token，必須遵守全域規範（token 不進對話、不進程式碼）；部署動作屬對外帳號操作，執行前要取得維護者明確同意。
  - **不採納**：目前沒有客戶接案需求就不需要正式導入；Zeabur 事件後也不遷移到任何新託管平台，除非另有決定。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261024-03`**｜**[優先級：中]** 在 Windows 11 原生環境評估 feedback-desk 的 CLI 與 MCP 可行性（不含正式部署，除非維護者同意）
  - **目標範圍**：`docs/feedback-desk-windows-eval.md`；僅在暫存資料夾執行，不碰其他 repo
  - **具體做法**：
    1. 以 `node -v` 確認 Node 20+，再於暫存資料夾執行 `npx --allow-git=all github:aixwangtw/feedback-desk init --name <測試名>`，記錄是否在原生 Windows 成功與錯誤訊息。
    2. 先詢問維護者是否同意建立 Cloudflare 帳號資源；同意才執行 `deploy` 與後續步驟，否則停在 `init`。
    3. 若有部署：驗證 `mcp install` 後 Claude Code 的 `/mcp` 顯示已連線，並確認 token 沒有出現在設定檔與對話。
  - **驗收標準（DoD）**：產出 `docs/feedback-desk-windows-eval.md`，含 `node -v`、`init` 的實際輸出（或錯誤）、是否需要 WSL 的結論一行；若有部署再加 `/mcp` 連線輸出。以 `Select-String -Pattern '結論'` 驗證存在，並確認文件不含任何 token。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261024-04`**｜**[優先級：低]** 對照 feedback-desk 的認領／交接機制與本地 `agent-relay`，列出可借鏡與不採納項
  - **目標範圍**：`docs/feedback-desk-vs-agent-relay.md`（只讀比對，不改 `agent-relay`）
  - **具體做法**：
    1. 比對欄位：狀態機、認領、交接紀錄、動作署名（帳號＋AI 工具）、人工確認閘門、客戶可見範圍。
    2. 每項標註「已有／缺少／不需要」與理由。
  - **驗收標準（DoD）**：產出 `docs/feedback-desk-vs-agent-relay.md`，含至少 6 列對照表，每列含判斷與理由；以 `Select-String -Pattern '^\| '` 計數表格列至少 8（含表頭與分隔列）。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 派工與交接**：
  - [多 Agent 派工與驗收閉環流水線 Phase 4](./2026-10-21-agent-relay-pipeline-phase4.md) ｜ 關聯任務：`T-20261021-03`~`T-20261021-11`
- **資安與平台風險**：
  - [Zeabur 2026 年十月資安事件解構](./2026-10-23-zeabur-october-2026-security-incident.md) ｜ 關聯任務：`T-20261023-05`、`T-20261023-06`
