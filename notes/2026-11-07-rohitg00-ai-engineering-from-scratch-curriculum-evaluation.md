---
id: 2026-11-07-rohitg00-ai-engineering-from-scratch-curriculum-evaluation
title: "AI Engineering from Scratch（rohitg00）開源教材深度評估：20 階段 542 堂課、18 個 AI 助教 Skills、80+ 本地評分專案，與繁中翻譯評估"
source_url: "https://www.threads.com/@cz88422/post/DfSEJ-0D_WE"
source_platform: "Threads (@cz88422)"
author: "黃裕 (@cz88422) / Rohit Ghumare (@rohitg00)"
analyzed_at: 2026-11-07
analyzed_by: "Antigravity"
status: done
cluster: "4"
cluster_role: "開源教材與商業案例查核"
short_title: "AI Engineering from Scratch 教材評估"
tags:
  - ai-engineering-from-scratch
  - curriculum
  - agent-skills
  - mcp
  - reverse-engineering
  - local-grader
---

# AI Engineering from Scratch（rohitg00）開源教材深度評估：20 階段 542 堂課、18 個 AI 助教 Skills、80+ 本地評分專案，與繁中翻譯評估

- **來源連結**：[Threads 貼文：@cz88422](https://www.threads.com/@cz88422/post/DfSEJ-0D_WE) ｜ [分享短網址](https://www.threads.com/share/BAZ8beVvFs)
- **官方開源倉庫**：[`rohitg00/ai-engineering-from-scratch`](https://github.com/rohitg00/ai-engineering-from-scratch)（77,280 Stars、13,696 Forks、MIT 授權，最近更新 2026-11-06，撰寫當時最新版本 `v2026.11.1`，2026-11-03 發布；複查時 2026-11-14 已到 `v2026.11.3`）
- **官方學習網站**：[aiengineeringfromscratch.com](https://aiengineeringfromscratch.com)
- **歸屬集群**：集群 4：領域知識庫、論文閱讀與尖端工程手冊（角色：`AI 工程從零實作開源教材索引`）
- **評估結論**：`🟢 高參考價值教材：不預裝 18 個教學 Skills 以免污染上下文，已萃取其 Tool Call Firewall 單次授權收據與 Trace Span 去重規格落實為本機工具`
- **相關交叉參照**：
  - [`notes/2026-10-19-rea-reverse-engineer-anything-agent.md`](./2026-10-19-rea-reverse-engineer-anything-agent.md)（逆向工程路線對照）
  - [`notes/2026-11-02-microphone-anti-overengineering-eight-agent-rules.md`](./2026-11-02-microphone-anti-overengineering-eight-agent-rules.md)（規則與工具淨零增長）

---

## 1. 貼文主張與 GitHub 原始碼實查對照

| 貼文描述 | GitHub API / 原始碼查證結果（2026-11-07） |
|---|---|
| 超過 7.6 萬顆星、542 堂課、20 個階段、MIT 授權 | ✅ **屬實**：77,280 Stars，20 個階段（`phases/00` 至 `19`），542 堂課，支援 Python、TypeScript、Rust、Julia |
| 整理成六冊電子書 | ✅ **屬實**：`book/volumes.json` 定義 6 冊（Foundations、Deep Learning、Language、LLMs、Agents、Production），Releases 提供編譯好的 PDF / EPUB |
| 提供繁體中文入口，部分翻譯完整度需留意 | ⚠️ **查證細節**：`languages.json` 中 `zh`（簡體）設為 `"ci": true`（CI 自動翻譯課文與介面），但 **`zh-TW`（繁體中文）僅設 `"site": true`，未開啟 `"ci": true`**。這表示網站介面與 `i18n/zh-TW/README.md` 有繁中，但 542 堂課文主體不會由 CI 自動翻成繁體 |
| `npx skills add rohitg00/ai-engineering-from-scratch` 可裝進 Codex / Claude Code | ⚠️ **屬實但有副作用**：`skills/` 底下共有 **18 個 Skills**。一次安裝會把 18 個教學與圖表 Skills 全塞進 Agent 的技能清單，佔用每個 session 的啟動描述空間 |

---

## 2. 專案架構全貌（6 冊 20 階段 + 專項路線 + 80+ 實作專案）

```text
rohitg00/ai-engineering-from-scratch
├── phases/ (20 階段 542 課，從純數學實作到框架)
│   ├── Vol 1 Foundations   : 00-setup, 01-math, 02-ml-fundamentals
│   ├── Vol 2 Deep Learning : 03-dl-core, 04-cv, 06-speech-audio
│   ├── Vol 3 Language      : 05-nlp, 07-transformers-deep-dive
│   ├── Vol 4 LLMs          : 08-genai, 09-rl, 10-llms-from-scratch, 11-llm-engineering
│   ├── Vol 5 Agents        : 12-multimodal, 13-tools-and-protocols, 14-agent-engineering,
│   │                         15-autonomous-systems, 16-multi-agent-and-swarms
│   └── Vol 6 Production    : 17-infra-production, 18-ethics-safety, 19-capstones
├── manuals/ (6 份獨立實戰手冊)
│   └── a2a-101, docker-sandboxes-101, miles-101, reverse-engineering-101, sglang-101, vllm-101
├── skills/ (18 個 AI 助教與繪圖技能，以 LEARNING.md 等狀態檔追蹤進度)
│   ├── 學習主線：start-learning, learn, course-guide, find-your-level, check-understanding
│   ├── 專項路線：learn-mcp (17課), learn-agent-skills (5課), learn-reverse-engineering (14課)
│   ├── 認證模擬：claude-certification (CCAO/CCDV/CCAR), mcpa-certification (MCP 2026-07-28)
│   └── 產出輔助：build-project, interview-prep, write-manual, blueprint/motion/isometric-figure
└── projects/ (80+ 個帶 starter 與本地 grader 的挑戰專案，透過 scripts/project_test.py 驗收)
```

### 與本系統最相關的精華區

1. **專項學習路線（`learning-paths/`）**：不必從 Phase 0 開始。現成路線包含 `model-context-protocol.json`（17 課）、`agent-skills.json`（5 課，含契約、探索、呼叫、沙箱邊界、可攜性評測）、`reverse-engineering.json`（Phase 13 第 32–45 課，從自編譯 ELF 開始讀）、`using-coding-agents.json`、`shaping-the-build.json`。
2. **三個代表性挑戰專案（均附本地評分器 `scripts/project_test.py`）**：
   - `retrieval-evaluation-lab`（Python）：平均 NDCG 上升但單一查詢退化時，寫出逐查詢退化攔截器。
   - `agent-trace-debugger`（TypeScript）：解析 JSONL trace、扣除父子重疊時間與重複計算的 token，抓出哪個 span 開始失敗或暴增 token。
   - `tool-call-firewall`（Rust + Python）：驗證呼叫信封、角色與路徑，實作綁定請求內容的單次授權收據（防止審批後竄改或重放）。這與本機的單向門審批、攔截器規格直接呼應。
3. **6 份 101 手冊（`manuals/`）**：`a2a-101`、`docker-sandboxes-101`、`sglang-101`、`vllm-101`、`reverse-engineering-101`、`miles-101`。

---

## 3. 為什麼不建議現在執行 `npx skills add`

1. **描述區膨脹（推論，未實測）**：一次裝入 18 個 Skills，每次對話啟動都要載入這 18 個技能的說明；你日常用 Coding Agent 是做開發與調研，不是每輪都在上課。
2. **額度消耗**：貼文作者自己也提醒「如果只是想閱讀教材，直接用官網即可，不需要安裝技能，使用 Codex 會消耗額度」。讓 Opus / Codex 一堂一堂帶讀課文，等於拿最貴的推論額度當電子書閱讀器。
3. **最佳用法**：
   - **平時查閱**：直接開 [aiengineeringfromscratch.com](https://aiengineeringfromscratch.com) 或下載 Releases 的 6 冊 EPUB / PDF。
   - **想練特定專案時**：才在獨立沙箱 shallow clone，跑 `python scripts/project_test.py <project-id> --init ...`，用它內建的本地 grader 驗收，不污染全域 Skills。

---

## 4. 待辦

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261107-01`**｜**[優先級：高]** 借鑑 `tool-call-firewall` 與 `agent-trace-debugger` 實作「綁定請求雜湊之單次審批收據驗證器與 Trace Span 去重分析工具」於 `tools/verify_tool_call_firewall.py` 與單元測試
  - **目標範圍**：`tools/verify_tool_call_firewall.py`、`tests/test_verify_tool_call_firewall.py`
  - **具體做法**：
    1. 實作 `compute_request_digest()`、`issue_approval_receipt()` 與 `ToolCallFirewall`：將寫入操作審批收據綁定 `(tool, role, normalized_path, content_sha256)` 之 SHA-256 雜湊，阻斷審批後竄改內容（TOCTOU `DIGEST_MISMATCH`）、同一收據二次重放（`REPLAYED_RECEIPT`）、未授權角色與 `..` 路徑越界。
    2. 實作 `analyze_trace_spans()`：合併重疊子 Span 時間區間（Interval Union）算出真實 `exclusive_duration_ms`，並扣除父子重複計算之 Token（`deduplicated_total_tokens`）。
  - **驗收標準（DoD）**：執行 python -m unittest tests/test_verify_tool_call_firewall.py 綠燈通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正兩輪（2026-11-14）：digest 綁定整個 canonical call 並自行重算 content 雜湊；各工具欄位白名單，未知欄位拒絕；記錄已消費 digest，換 receipt_id 重送拒絕；拒絕絕對、磁碟機、UNC、ADS（含 :）、結尾點、保留裝置名路徑；未知工具預設拒絕。原審查與 Opus 新繞過（換 command／new_string、重送、src/x:evil.ps1）全部由 exit 0 變 1。限制：收據沒有簽章、consumed_digests 只存在單次程序，文件已寫明。 **搬移註記（2026-11-14）**：工具與測試已移至 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks)（保留 git 歷史）。

> 備註：教材本身的 18 個教學 Skills 不預裝至本機全域環境，以免佔用每次對話啟動的技能描述空間；平時查閱課文與 `manuals/` 直接按本篇第 2 節索引取用。
