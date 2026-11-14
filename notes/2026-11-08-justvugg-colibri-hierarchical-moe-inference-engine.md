---
id: 2026-11-08-justvugg-colibri-hierarchical-moe-inference-engine
title: "開源專案 `JustVugg/colibri` 解構：VRAM/RAM/NVMe 三層式 MoE 推理引擎、零生成 `System One`（Jev API 相容）決策端點與本機 RTX 3060 適配評估"
source_url: "https://www.threads.com/share/_791NkszU"
source_platform: "Threads (@shipped_ai) / GitHub (JustVugg/colibri)"
author: "shipped_ai (@shipped_ai) / Vincenzo Fornaro (JustVugg)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: archived
cluster: "1"
cluster_role: "模型路由與配額分流"
short_title: "colibri三層MoE推理與System One決策"
tags:
  - colibri
  - moe-inference
  - expert-offloading
  - nvme-streaming
  - system-one
  - jev-api
  - glm-5-2
  - qwen3-6
  - local-llm
---

# 開源專案 `JustVugg/colibri` 解構：VRAM/RAM/NVMe 三層式 MoE 推理引擎、零生成 `System One`（Jev API 相容）決策端點與本機 RTX 3060 適配評估

- **來源連結**：[Threads 分享短網址](https://www.threads.com/share/_791NkszU) ｜ [貼文永久網址 (@shipped_ai)](https://www.threads.com/@shipped_ai/post/DfQi-FRmfpw) ｜ [官方 GitHub (`JustVugg/colibri`)](https://github.com/JustVugg/colibri) ｜ [官方繁體中文 README (`README.zh-TW.md`)](https://github.com/JustVugg/colibri/blob/main/README.zh-TW.md)
- **核心作者**：`@shipped_ai`（Threads 整理介紹）／ Vincenzo Fornaro（`JustVugg`，`colibri` 作者）
- **專案數據（2026-11-08 實查 GitHub API）**：`48,798 Stars`、`5,691 Forks`、`Apache-2.0 License`，最新版本 `v2.1.0`
- **歸屬集群**：集群 1：多 Agent 編排、模型路由與 Context 治理（角色：`模型路由與配額分流`）
- **當前狀態**：`⚪ 已封存 (Archived)`（已完成架構深挖、CQR 速度吞吐量實證檢驗與本機 `msi-P50` 32GB RAM + RTX 3060 12GB 適配精算；因本機主力開發走雲端 Opus/Codex/Gemini 且本地超大 MoE 模型需 23GB–429GB 磁碟空間，不自動下載模型或衍生重複建置任務）
- **相關交叉參照**：
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（四級模型分工中的 L4 JEV 快速決策層）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（JEV「只回答是／否、選哪個」的二元與枚舉決策 API）

---

## 1. 資訊初篩（5W1H）與核心原理

- **Who**：義大利開發者 Vincenzo Fornaro（[`JustVugg/colibri`](https://github.com/JustVugg/colibri)）開源，由 `@shipped_ai` 於 Threads 介紹。
- **What**：一套以**純 C 語言**編寫（每個模型家族單一 `.c` 檔，無外部 BLAS 依賴）的階層式混合專家（MoE, Mixture-of-Experts）本地推理引擎，支援將權重跨 **VRAM（CUDA/Vulkan/Metal）$\rightarrow$ 系統 RAM $\rightarrow$ NVMe SSD 硬碟** 三層動態配置，讓一般家用電腦也能執行 30B 至 2.8T（如 744B 的 `GLM-5.2`、1.02T 的 `MiMo-V2.6 Pro`、2.8T 的 `Kimi K3`）的開放權重模型。
- **Why**：
  - 現代前沿開源模型多為稀疏啟用的 MoE 架構。以 **GLM-5.2（744B 參數，int4 總大小 429 GB）** 為例，每生成 1 個 token 僅啟用約 **40B 參數（約 5.4%）**，其中隨 token 改變的路由專家（Routed Experts）僅約 11 GB。
  - 傳統推理引擎要求將整個模型放進 VRAM 或 RAM；`colibri` 只把每次必用的**稠密層（Attention、共享專家、Embedding，約 9.9 GB）常駐於 RAM/VRAM**，其餘專家留在 NVMe SSD 上按需 `pread` 讀取，並透過 `.coli_usage` 記錄歷史對話的路由熱度（Weight JIT + LRU 快取 + 提前一層 71.6% 命中率的路由預取）。

```text
+-----------------------------------------------------------------------------------+
|               JustVugg/colibri 三層式 MoE 權重配置與單 Token 5 步管線             |
+-----------------------------------------------------------------------------------+
  [單一 Token 5 步管線]: 1. 路由 (Route) -> 2. 聯集 (Union) -> 3. 配置 (Place)
                         -> 4. 運算/IO 重疊 (Overlap) -> 5. 學習熱度 (.coli_usage)

  ┌───────────────────────────────────────────────────────────────────────────────┐
  │ Tier 1: GPU VRAM (CUDA / Vulkan / Metal)                                      │
  │  • 存放稠密層鏈 (Dense Chain) + 最常命中的 Hot Routed Experts                 │
  ├───────────────────────────────────────────────────────────────────────────────┤
  │ Tier 2: System RAM (9.9 GB resident for GLM-5.2 744B)                         │
  │  • 若無大 VRAM，存放 Attention / Shared Experts / MLA 壓縮 KV (小 57 倍)      │
  │  • 存放 Per-Layer LRU 專家快取與歷史對話固定的 Pinned Experts                 │
  ├───────────────────────────────────────────────────────────────────────────────┤
  │ Tier 3: NVMe SSD (Cold Experts Streaming, 支援雙碟 COLI_MODEL_MIRROR +37.5%)  │
  │  • 單次 pread 讀取一個專家的 3 個矩陣；CPU/GPU 算常駐專家時背景預載缺失專家   │
  └───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 四大工程亮點深挖（超越「無 GPU 跑大模型」的實用價值）

深挖 [`JustVugg/colibri` 原始碼與繁中文件](https://github.com/JustVugg/colibri/blob/main/README.zh-TW.md) 後，發現該專案對 AI Agent 架構最具啟發的其實不是「硬跑 744B 模型」，而是以下四項工程設計：

### 2.1 `POST /v1/systemone`：零 Token 生成的確定性決策端點（直接相容 TypeSafe Jev API）
- 在本庫先前分析的 [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md) 中，曾提及四級模型分工的第 4 層 **JEV（只回答是／否、選哪個的決策 API）**。
- `colibri` 內建了完全相容 TypeSafe Jev API 的本地端點 **`POST /v1/systemone`**（僅需將 `TYPESAFE_BASE_URL=http://127.0.0.1:8000` 指向本機 `coli serve`）：
  - **零生成（Zero-Token Generation）**：只做 1 次 Forward Pass 讀取輸入狀態（`state`），直接讀取各允許選項的機率分布與信心值（`confidence` 0~1），**完全不跑自迴歸文字生成**，因此絕對不會跳出允許清單之外，且同一份文件問 4 個問題比生成答案快 **5.7 倍**。
  - **三種決策題型**：`choice`（多選一＋各選項機率＋信心度）、`noul`（二元是／否機率）、`score`（期望評分等級）。
  - **兩款輕量專用決策模型（Laya、GLiNER2.5-Decide，僅需 1.7–1.9 GB RAM）；Clef 為 27B，RAM 19–55 GB**（README 第 263 行）：
    1. **`Laya`**（下載 `0.85 GB`，RAM `1.7 GB`）：CPU 單題 `219 ms`，CUDA 12 題僅 `0.69s`。
    2. **`GLiNER2.5-Decide`**（下載 `1.95 GB`，RAM `1.9 GB`）：CPU 單題 `294 ms`，CUDA 12 題僅 `0.16–0.21s`。
    3. **`Clef`**（Cloudflare 開源，基於 Qwen3.8-27B 加上決策頭）。

### 2.2 `COLI_PARK`：為 Coding Agent 多輪呼叫設計的 KV 狀態暫存
- Coding Agent（如 Claude Code、Hermes）在兩輪正式工具呼叫之間，常會插播一個短請求（例如「幫這段對話取個 5 字標題」或路由分類）。
- 傳統本地推理引擎（如單槽 `llama.cpp`）收到短請求時會把原本長達數萬 token 的主對話 KV Cache 洗掉，下一輪又得重跑幾十秒 Prompt Prefill。
- `colibri` 內建 `COLI_PARK` 與 `--kv-slots N`（最多 16 槽）：自動將主對話 KV 狀態「路邊停車（Park）」保留，短請求結束後毫秒級恢復。實測在 `Qwen3.8-Flash-Next` 上執行 **Hermes Agent 第二輪（14,810 tokens）的反應時間從 86 秒降至 4.9 秒（快 17.5 倍）**。

### 2.3 原生雙協定閘門（OpenAI `/v1/chat/completions` ＋ Anthropic `/v1/messages`）與 `coli mcp`
- `c/openai_server.py` 同時暴露 `http://127.0.0.1:8000/v1`（OpenAI 相容）與 `http://127.0.0.1:8000`（Anthropic `/v1/messages` 相容），Claude Code 與各家 SDK 可直接連入。
- `c/mcp_server.py`（`py -3 c\coli mcp`）以純 Python 標準庫實作 MCP Server，提供 `detect_hardware`、`recommend_models`、`install`、`start`、`stop`、`status` 六個標準工具。

---

## 3. CQR 論證與實證數據檢驗（Claim - Evidence - Reasoning）

| 檢驗維度 | 社群貼文 / 專案宣稱 (Claim) | 官方基準實測證據 (Evidence) | 工程推理與實用性判定 (Reasoning) |
| :--- | :--- | :--- | :--- |
| **1. 744B 模型在普通電腦的可用性** | 「在家裡的普通電腦上跑 7,440 億參數的 GLM-5.2，常駐記憶體只有 9.9 GB」 | - 磁碟佔用需 **429 GB**（`int4-g64`）。<br>- 25 GB RAM 筆電冷啟動解碼僅 **0.05–0.1 tok/s**（生 1 個字要 10–20 秒）。<br>- 128 GB RAM（Ryzen AI Max+ 395）暖機後為 **1.83 tok/s**。<br>- 6 張 RTX 5090 全常駐為 **9.0–9.2 tok/s**。 | **「能跑通（Runs）」不等於「能日常互動（Usable）」**。當大多數路由專家都不在 RAM 時，每個 token 都要從 SSD 讀數 GB 權重，受限於 PCIe/NVMe 頻寬，0.1 tok/s 無法用於即時對話或 Coding Agent。 |
| **2. 消費級硬體真正實用的甜區（Sweet Spot）** | 「比較實際的玩法是先從 30B–40B MoE 或輕量決策模型開始」 | - **Qwen3.6-35B-A3B**（下載 23 GB，RAM 10/20 GB）：CPU 6.0 tok/s、內顯 780M Vulkan 9.9 tok/s、**RTX 3070 8GB CUDA 達 30.0 tok/s**（開啟 `Q36_DN_GPU=1` 將 30 個 DeltaNet 層放進 VRAM）。<br>- **Flint 40B-A2.5B**（UD-Q4_K_XL）：CUDA **77.4 tok/s**、Vulkan **77.7 tok/s**、CPU **15.8 tok/s**。<br>- **OLMoE 7B-A1B**：CUDA **354.6 tok/s**、CPU **22–47 tok/s**。 | 對於 16–32 GB RAM 搭配 8–12 GB 獨顯的桌面機，**30B–40B 稀疏 MoE（每 token 僅啟用 2.5B–3B）才是黃金甜區**——稠密層與 DeltaNet 塞進 VRAM、全數專家塞進系統 RAM，完全不碰硬碟 I/O，即可跑出 30–77 tok/s 的流暢速度。 |

---

## 4. 本機硬體（`msi-P50`）適配精算與評估結論

實測本機（Windows 11 原生）硬體規格如下：
- **CPU / RAM**：`31.9 GB Total RAM`（日常開發常駐後可用約 `6.6–12 GB`）
- **GPU**：`NVIDIA GeForce RTX 3060 (12,288 MiB VRAM, Compute Capability 8.6)`（完全符合 `colibri` Windows CUDA DLL `compute_cap >= 8.0` 要求）
- **磁碟可用空間**：`C:\` 剩餘 `233.5 GB`

對照 `JustVugg/colibri` 的硬體規劃器（`c/resource_plan.py`），本機各檔位適配結論如下表：

| 模型檔位 | 模型 ID (`--model`) | 下載大小 | RAM 需求 (最低/理想) | 本機 `msi-P50` (32GB RAM + RTX 3060 12GB) 適配判定與預估表現 |
| :--- | :--- | :---: | :---: | :--- |
| **Tier S：極速決策 API (`System One`)** | `laya` / `gliner_decide` | `0.85 GB` / `1.95 GB` | `1.7–1.9 GB` | **極佳（首選）**：VRAM/RAM 佔用極微，官方基準（非 3060）約 **13–57 ms/題**（CUDA 12 題 0.16–0.69 s 換算；RTX 3060 未實測）可完成二元或枚舉分類，可作為零成本本地 JEV 決策器。 |
| **Tier A：本地 Coding / 工具呼叫甜區** | `qwen3-coder-30b` / `qwen36-35b` / `Flint-40B` | `19–23 GB` | `8–10 GB` / `18–20 GB` | **預估可執行（30–60+ tok/s，預估，未實測）**：RTX 3060 12GB VRAM 比官方基準機 C（RTX 3070 8GB，實測 30 tok/s）多出 4GB VRAM，開啟 `CUDA` + `Q36_DN_GPU=1` 可將稠密層、DeltaNet 與熱點專家放入 12GB VRAM，其餘專家放 32GB RAM。 |
| **Tier B：中型硬碟串流 MoE** | `deepseek-v4-flash-reap` (150B) / `deepseek-v4-flash` (284B) | `85 GB` / `167 GB` | `16 / 32 GB` | **勉強可跑但慢（~1 tok/s）**：167 GB 會吃掉 `C:\` 71% 剩餘空間，僅適合外接高速 NVMe 實驗。 |
| **Tier C：超巨型 MoE** | `glm-5.2` (744B) / `kimi-k3` (2.8T) | `429 GB` / `1.56 TB` | `16–64 GB` | **不適用**：`C:\` 可用空間（233.5 GB）放不下 429 GB 權重檔。 |

### 評估結論（歸檔備查，不自動下載大檔或衍生新任務）

1. **遵循本機硬閘門**（見 `docs/AI_SETUP.md`，2026-11-14 以 `gh api repos/JustVugg/colibri/contents/docs/AI_SETUP.md` 確認存在）：`colibri` 最小聊天模型需下載 19–23 GB，且本機主力 Agent（Claude Opus 5.5、Codex、Antigravity、Hermes）皆已有穩定的雲端配額，目前無需耗費數十 GB 磁碟空間安裝本地 LLM。
2. **留存架構資產**：將 `JustVugg/colibri` 的三層 MoE 記憶體規劃、本機 RTX 3060 12GB 適配表、以及 `POST /v1/systemone`（本地零生成 Jev API 替代方案）與 `COLI_PARK`（Agent 跨輪 KV 暫存）完整記錄於本筆記備查（`status: archived`），日後若有離線推理或本地微秒級分類器需求，可直接按第 4 節 Tier S / Tier A 參數啟用。
