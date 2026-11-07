---
id: 2026-11-07-gemini-notebook-official-api-mcp-preview
title: "Gemini Notebook（前 NotebookLM）官方 API 與 MCP 預覽版評估：7 個工具只能寫入不能查詢、GCP ADC 憑證風險與實際用途界定"
source_url: "https://www.threads.com/@be.ai.curator/post/DfY954CkZ9V"
source_platform: "Threads (@be.ai.curator)"
author: "AI 主理人 (@be.ai.curator)"
analyzed_at: 2026-11-07
analyzed_by: "Antigravity"
status: done
cluster: 3
cluster_role: "Google 研究工具 MCP 接入評估"
short_title: "Gemini Notebook MCP 預覽評估"
tags:
  - gemini-notebook
  - notebooklm
  - mcp
  - google-cloud
  - adc
  - credential-hygiene
---

# Gemini Notebook（前 NotebookLM）官方 API 與 MCP 預覽版評估：7 個工具只能寫入不能查詢、GCP ADC 憑證風險與實際用途界定

- **來源連結**：[Threads 貼文：@be.ai.curator](https://www.threads.com/@be.ai.curator/post/DfY954CkZ9V) ｜ [分享短網址](https://www.threads.com/share/BAbZwU2wnu)
- **官方文件**：[Gemini Notebook API：Model Context Protocol (MCP)](https://developers.google.com/notebook/docs/mcp)、[Authentication](https://developers.google.com/notebook/docs/authentication)
- **抓取時間**：2026-11-07（貼文約 1 天前，20.5K views）
- **歸屬集群**：集群 3（角色：`Google 研究工具 MCP 接入評估`）
- **評估結論**：`🟡 消息屬實、目前用途有限`：不衍生任務，等可查詢版本再評估
- **相關交叉參照**：
  - [`notes/2026-11-04-nicholas-lin-gcp-vertex-ai-amos-llmjacking.md`](./2026-11-04-nicholas-lin-gcp-vertex-ai-amos-llmjacking.md)（GCP 專案開 API、憑證外洩的風險鏈）

---

## 1. 貼文重點

- Gemini Notebook（2026-07-16 起由 NotebookLM 改名）推出個人用官方 API 與 MCP 預覽版：AI 工具可以自己**建筆記本、加入網頁、有字幕的 YouTube、純文字**。
- 作者自己標明限制：**不能問問題、不能產生語音摘要、不能傳 PDF，Workspace 帳號還不開放**。
- 作者主張：從額度分工角度，beta 免費值得先接，可分擔 Grok／Claude Code／Codex 研究影片的額度。
- 值得留意的留言：
  - `zhenheco`：工具接越多，要維護的流程越多；只為每週跑三次以上的事接工具。
  - `zz950907`：當「研究前置處理器」，「研究時叫 AI 先查筆記本再回答」。**這點與官方 API 不符，見第 2 節。**

## 2. 查證官方文件（關鍵修正）

- **端點**：`https://notebook.googleapis.com/mcp`，Streamable HTTP（JSON-RPC 2.0）。
- **只有 7 個工具，全部是管理與匯入**：

| 工具 | 作用 |
| --- | --- |
| `create_notebook`／`get_notebook`／`list_notebooks`／`update_notebook` | 建立、讀取中繼資料、列出、改名 |
| `create_source` | 匯入網頁 URL、YouTube、純文字或 Markdown |
| `get_source`／`list_sources` | 查看來源中繼資料與處理狀態（`PROCESSING`／`ACTIVE`／`FAILED`） |

- **沒有任何查詢、問答或取回摘要的工具**。所以 coding agent **無法**「先查筆記本再回答」。目前的流程只能是：

```text
Agent ──create_source──► Gemini Notebook ──► 人在網頁 UI 問答 / 產生 Audio Overview
   ▲                                              │
   └──────── 拿不回答案（API 沒有查詢工具）─────────┘
```

- 「分擔 Claude Code／Codex 研究額度」在這一版**不成立**：agent 讀不到 Notebook 的分析結果，研究仍要自己做。

## 3. 接入門檻與憑證風險

官方安裝流程要求：

1. 一個 **GCP 專案**，並執行 `gcloud services enable notebook.googleapis.com`。
2. 以 ADC 登入，scope 同時包含 `cloud-platform` 與 `notebook`。
3. 用 `gcloud auth application-default print-access-token` 取得 Bearer token，**直接寫進 MCP 設定檔的 header**（官方範例甚至把 token 放在 `claude mcp add --header` 指令列）。

風險與摩擦：

- **憑證進指令列與設定檔**：與「API key、token 不進程式碼、指令列、對話」的硬閘門衝突。
- **ADC 帶 `cloud-platform` 全權 scope**：本機一旦被竊（參照 Nicholas Lin 案的 AMOS 竊密鏈），拿到的是整個 GCP 專案權限，不只 Notebook。
- **Access token 有效期短（Google OAuth 通常約 1 小時）**：靜態寫入 header 會很快失效，要另外處理更新，否則會**默默失敗**。
- 若要試，應開一個**專用、未綁計費帳戶的 GCP 專案**，只開 `notebook.googleapis.com`，並用包裝腳本即時取 token，不把 token 寫入任何檔案。

## 4. 評估

| 面向 | 判斷 |
| --- | --- |
| 消息真實性 | ✅ 屬實，官方文件已上線 |
| 對 coding agent 的實際價值 | 低：只能寫入，拿不回分析結果 |
| 對人的價值 | 中：可讓 agent 批次把研究來源丟進筆記本，人再用 UI 問答、聽 Audio Overview |
| 接入成本與風險 | 中高：GCP 專案、ADC 全權 scope、短效 token 管理 |

## 5. 待辦

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

本篇**不衍生新任務**。理由：API 目前不能查詢，對 agent 研究流程沒有回饋路徑；為「批次匯入來源」單一用途建 GCP 專案與憑證管理，不符合「每週真的會跑三次以上才接工具」的門檻。**重新評估的觸發條件**：官方加入查詢／問答工具，或支援 OAuth 自動更新、不必把 token 寫進設定檔。
