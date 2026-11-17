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
source_review: full
source_reviewed_at: 2026-11-17
source_images: 1
source_replies: 42
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
- **專案數據（2026-11-08 實查 GitHub API）**：`48,798 Stars`、`5,691 Forks`、`Apache-2.0 License`，最新版本 `v2.1.0`（2026-11-16 複查：51,506 Stars、6,223 Forks，最新版仍為 `v2.1.0`）
- **歸屬集群**：集群 1：多 Agent 編排、模型路由與 Context 治理（角色：`模型路由與配額分流`）
- **當前狀態**：`⚪ 已封存 (Archived)`（已完成架構深挖、CQR 速度吞吐量實證檢驗與本機 `msi-P50` 32GB RAM + RTX 3060 12GB 適配精算；因本機主力開發走雲端 Opus/Codex/Gemini 且本地超大 MoE 模型需 23GB–429GB 磁碟空間，不自動下載模型或衍生重複建置任務）
- **相關交叉參照**：
  - [`notes/2026-10-31-claude-code-hierarchical-multi-model-orchestration.md`](./2026-10-31-claude-code-hierarchical-multi-model-orchestration.md)（四級模型分工中的 L4 JEV 快速決策層）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（JEV「只回答是／否、選哪個」的二元與枚舉決策 API）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看 Threads 貼文：貼文文字、作者圖片 1 張（開原圖看過）、留言 18 則（含作者接續的 3 則串文；貼文標示 43 則回覆，其餘要登入才看得到；留言是捲到才載入，逐段捲動收集）。作者留言裡的 GitHub Releases 連結預覽卡只讀了標題。另以 GitHub API 讀留言數最多的 8 則 issue／PR 摘要，其中 #1405 讀了內文與最後 8 則回覆。

- **作者圖片**：圖 1 是轉介帳號自製的宣傳圖卡（筆電與蜂鳥的生成圖），大字寫 744B 開源大模型常駐記憶體只要 9.9 GB，小字補「8 GB 的電腦就能起步，但是速度要看你的硬碟」，標籤寫 GitHub 4.6 萬星。沒有任何實測畫面或數據圖。
- **作者留言補充**（3 則接續串文）：
  - 解釋 MoE 稀疏啟用與「常用的放 RAM、其餘留硬碟按需讀取」的原理，列出支援的模型家族，並提到別人發布的 GGUF 檔也能直接讀。
  - **自己先把限制講明**：8 GB 只夠跑小模型；跑 744B 的 GLM-5.2 官方建議至少 16 GB 記憶體、要 429 GB 硬碟；25 GB 記憶體筆電冷啟動只有每秒 0.05～0.1 個 token，128 GB 的機器約 1.83 個；較實際是從 Qwen3.6-35B 起步，8 核桌機 CPU 約每秒 6 個 token。安裝方式是 Windows 點兩下 `START-HERE.bat`。
  - 最後一則貼 repo 與 v2.1.0 版本說明連結。
- **網友留言重點**：
  - 對速度的失望是主調：`fatwenccc` 看到 Qwen3.6 35B 只有 6 tok/s 就打消念頭；`learnrpg` 抱怨應該先把速度寫在最前面；`scalvaria` 認為低於 60 tok/s 都算雞肋；`scsnakechen` 嘲諷這樣說的話人腦加紙筆也能跑模型。
  - `jude_qiu`：肯定作者把速度直接寫出來，「能跑」和「能用」是兩回事；認為這證明硬碟可以當權重層，日後頻寬與快取命中率提高才會變可用。
  - `zwy_4493`：提到另一個同類引擎 Strata，自稱在 12GB 顯示記憶體的筆電加 64GB RAM 上跑 763B 模型有約 5 token/s（非全精度，且有大量 SSD 寫入）；`dolannatw` 認為意義不大，少量 VRAM 加主記憶體的做法比較實用。兩則都是留言者自述，未查證。
  - `meta.ai`（Meta 的 AI 帳號，被點名回答，非一手資料）：用一堆樹莓派或 PS5 不會變快，瓶頸是硬碟到記憶體的頻寬；要提速是加 RAM、換高速 NVMe、開 Vulkan。
  - **GitHub issue #1405（Windows CUDA DLL）**：有使用者照文件在 Windows 建 CUDA DLL 失敗（找不到 `cuda-dll` 的 make 目標）。作者 2026-09-14 回覆確認當時的 Windows 發行壓縮檔只有引擎執行檔、沒有 CUDA DLL，CI 已能建出可攜的 DLL，剩下是把它放進發行檔。這則 issue 到 2026-11-16 仍是開啟狀態；v2.1.0 的發行檔有沒有附 DLL，本筆記未查。同一串裡另有一個實測：模型放在 SATA SSD 上時，GLM-5.2 約 12 秒才出一個字，作者回覆這就是該硬碟的上限。
  - 其他熱門 issue 集中在安裝包（Ubuntu 上裝不起來、希望提供 deb）、預取的 I/O 佇列深度、AMD 顯卡上的效能退化，顯示安裝與跨硬體效能仍在收斂。
- **2026-11-17 登入補讀**：
  - **Threads 留言**：登入後以「熱門」「最新」兩種排序各捲到底、子回覆全部點開，再逐一打開還有下層回覆的 6 則留言頁面，共讀到 33 則（含作者串文 3 則）；首輪讀到的 `scsnakechen` 那則這次已不顯示，合計 34 則。貼文標示 43 則，頁面底部註明「部分新增回覆無法顯示」，其餘 9 則平台不顯示。加上先前讀的 GitHub issue 8 則，共 42 則。
  - 新讀到的多半是網友點名 `meta.ai` 的問答（AI 生成，不當一手資料）：問是不是假新聞、一小時能輸出多少 token（照作者的冷啟動數字換算約 180～360 個）、加顯示卡能不能加倍、16GB 記憶體的 i5 筆電怎麼裝、PS5 的硬碟很快為什麼不行。這些回答裡的數字大多是把 README 的數字重講一次，少數對不上（例如模型大小一處說 370GB、貼文與 README 是 429GB），不採用。
  - 網友自己的意見：`mushu_ai` 說這是把「跑得動」和「跑得快」拆開算；`guiq_79043` 嘲諷速度單位應該是幾分鐘一個 token、而且很傷硬碟；`lets.jumptogether`、`freddy.kuo` 也是嫌慢。**沒有任何人回報自己裝起來的實測數字**。
  - **GitHub 發行檔查證**（補首輪「v2.1.0 有沒有附 CUDA DLL 未查」）：2026-11-17 以 GitHub API 列發行檔，v2.0.0（2026-10-06）與 v2.1.0（2026-10-31）都多了一個 `colibri-v2.1.0-windows-x86_64-cuda.zip` 這類 Windows CUDA 專用壓縮檔，v1.12.1 還沒有。所以 issue #1405 當時「發行檔沒有 CUDA 版」的缺口，從 v2.0.0 起已有對應的發行檔；壓縮檔內容本筆記沒有下載驗證，issue #1405 本身也仍是開啟狀態（最後更新 2026-09-14，沒有人回來確認）。
- **對分析的影響**：
  1. 原筆記第 3 節「能跑通不等於能日常互動」的判斷，與作者自己的補充串文及多數留言一致；留言沒有人回報比 README 更好的實測數字。結論不變。
  2. **第 4 節的本機適配表要加一個前提**：原筆記寫 RTX 3060「完全符合 Windows CUDA DLL 的要求」，那只是運算能力版本符合。依 issue #1405，Windows 發行檔曾經不含 CUDA DLL、自行建置也有人失敗，所以 Tier S 與 Tier A 的 CUDA 數字在本機能否直接取得，要先確認發行檔有附 DLL。已在第 4 節 GPU 那一行與表格下方加註。
  3. **磁碟種類也是前提**：SATA SSD 的實測（12 秒一個字）說明 Tier B、Tier C 這類要從硬碟串流的檔位，必須是 NVMe 才有討論空間。已在表格下方加註。
  4. 專案數據更新註記：2026-11-16 以 API 查為 51,506 Stars、6,223 Forks，最新版仍是 v2.1.0。
  5. 維持歸檔、不開任務。
  6. **2026-11-17 補讀**：留言沒有新的實測，結論不變。第 4 節「Windows 發行檔是否附 CUDA DLL 要先確認」的前提更新為：v2.0.0 起已有 Windows CUDA 專用發行檔（檔名查證、內容未下載驗證），已改寫第 4 節 GPU 那一行與表格下方的註記。

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
- **GPU**：`NVIDIA GeForce RTX 3060 (12,288 MiB VRAM, Compute Capability 8.6)`（運算能力版本符合 `colibri` Windows CUDA DLL `compute_cap >= 8.0` 的要求；Windows 的 CUDA 版要另外下載 `windows-x86_64-cuda` 發行檔，v2.0.0 起才有，見第 0 節）
- **磁碟可用空間**：`C:\` 剩餘 `233.5 GB`

對照 `JustVugg/colibri` 的硬體規劃器（`c/resource_plan.py`），本機各檔位適配結論如下表：

| 模型檔位 | 模型 ID (`--model`) | 下載大小 | RAM 需求 (最低/理想) | 本機 `msi-P50` (32GB RAM + RTX 3060 12GB) 適配判定與預估表現 |
| :--- | :--- | :---: | :---: | :--- |
| **Tier S：極速決策 API (`System One`)** | `laya` / `gliner_decide` | `0.85 GB` / `1.95 GB` | `1.7–1.9 GB` | **極佳（首選）**：VRAM/RAM 佔用極微，官方基準（非 3060）約 **13–57 ms/題**（CUDA 12 題 0.16–0.69 s 換算；RTX 3060 未實測）可完成二元或枚舉分類，可作為零成本本地 JEV 決策器。 |
| **Tier A：本地 Coding / 工具呼叫甜區** | `qwen3-coder-30b` / `qwen36-35b` / `Flint-40B` | `19–23 GB` | `8–10 GB` / `18–20 GB` | **預估可執行（30–60+ tok/s，預估，未實測）**：RTX 3060 12GB VRAM 比官方基準機 C（RTX 3070 8GB，實測 30 tok/s）多出 4GB VRAM，開啟 `CUDA` + `Q36_DN_GPU=1` 可將稠密層、DeltaNet 與熱點專家放入 12GB VRAM，其餘專家放 32GB RAM。 |
| **Tier B：中型硬碟串流 MoE** | `deepseek-v4-flash-reap` (150B) / `deepseek-v4-flash` (284B) | `85 GB` / `167 GB` | `16 / 32 GB` | **勉強可跑但慢（~1 tok/s）**：167 GB 會吃掉 `C:\` 71% 剩餘空間，僅適合外接高速 NVMe 實驗。 |
| **Tier C：超巨型 MoE** | `glm-5.2` (744B) / `kimi-k3` (2.8T) | `429 GB` / `1.56 TB` | `16–64 GB` | **不適用**：`C:\` 可用空間（233.5 GB）放不下 429 GB 權重檔。 |

> 兩個前提（2026-11-16 依 GitHub issue #1405 補）：(1) 表中所有 CUDA 數字都假設 Windows 上拿得到 `coli_cuda.dll`；該 issue 顯示發行檔曾經不含這個 DLL、自行建置也有人失敗，啟用前先確認。(2) Tier B、Tier C 靠硬碟串流，同一則 issue 有人把模型放在 SATA SSD 上實測約 12 秒一個字，非 NVMe 不必考慮。
>
> 更新（2026-11-17）：以 GitHub API 查發行檔，v2.0.0 與 v2.1.0 都有獨立的 Windows CUDA 壓縮檔（`colibri-v2.1.0-windows-x86_64-cuda.zip`），前提 (1) 的缺口在發行面已補上；壓縮檔內是否就是 `coli_cuda.dll`、在本機能否載入，仍未實測。

### 評估結論（歸檔備查，不自動下載大檔或衍生新任務）

1. **遵循本機硬閘門**（見 `docs/AI_SETUP.md`，2026-11-14 以 `gh api repos/JustVugg/colibri/contents/docs/AI_SETUP.md` 確認存在）：`colibri` 最小聊天模型需下載 19–23 GB，且本機主力 Agent（Claude Opus 5.5、Codex、Antigravity、Hermes）皆已有穩定的雲端配額，目前無需耗費數十 GB 磁碟空間安裝本地 LLM。
2. **留存架構資產**：將 `JustVugg/colibri` 的三層 MoE 記憶體規劃、本機 RTX 3060 12GB 適配表、以及 `POST /v1/systemone`（本地零生成 Jev API 替代方案）與 `COLI_PARK`（Agent 跨輪 KV 暫存）完整記錄於本筆記備查（`status: archived`），日後若有離線推理或本地微秒級分類器需求，可直接按第 4 節 Tier S / Tier A 參數啟用。
