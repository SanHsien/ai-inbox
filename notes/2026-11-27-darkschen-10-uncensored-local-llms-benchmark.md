---
id: "2026-11-27-darkschen-10-uncensored-local-llms-benchmark"
title: "Facebook 社團實測：10 款無審查地端模型（24GB–128GB）Token 速度基準、Strata 避坑與雲地協作架構"
source_url: "https://www.facebook.com/groups/gaitech/posts/1852706389246901/"
source_platform: "Facebook (Generative AI 技術交流中心)"
author: "陳盟升 (@darkschen)"
analyzed_at: "2026-11-27"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 1
source_replies: 40
source_reviewed_at: "2026-11-27"
source_review_note: "貼文全文、1 張終端機基準測試圖與 13 串頂層留言皆已展開讀取；40 則總留言中實見 35 則（13 頂層＋22 回覆），其餘 5 則回覆於未登入狀態未渲染"
status: archived
cluster: 3
cluster_role: "地端無審查模型選型"
short_title: "10款無審查地端模型實測"
tags:
  - local-llm
  - uncensored
  - strata
  - qwen
  - nemotron
  - benchmark
  - facebook
---

# Facebook 社團實測：10 款無審查地端模型（24GB–128GB）Token 速度基準、Strata 避坑與雲地協作架構

- **來源貼文**：[陳盟升（`Generative AI 技術交流中心`）Facebook 貼文](https://www.facebook.com/groups/gaitech/posts/1852706389246901/)（原分享連結 `https://www.facebook.com/share/p/1Gm1YuxoQz/`，`2026-11-26` 發布，275 讚、40 則留言、76 次分享）
- **相關筆記**：[Strata 架構解構：12GB 消費級顯卡流暢運行 125B MoE 大模型](2026-10-21-strata-consumer-gpu-large-llm-inference.md)

---

## 核心結論

作者以兩台 128GB 測試機（NVIDIA GB10 與 MacBook M5 Max）搭配長上下文 AI Agent 負載（單次幾萬至十幾萬字上下文），實測 10 組跨 `24GB` 至 `128GB` 級距的無審查（abliterated / uncensored）地端模型。綜合性價比與速度首選為 **MoE 架構的 `Qwen3.8 Flash Next 125B`**（每次僅啟用約 6B 參數，Mac 4bit MLX 達 106–132 t/s，或透過 `Strata` 引擎在 `12GB 顯卡 + 64GB RAM` 上運行）。核心價值不在成人內容，而在**「拿掉政治與安全過度拒答，並讓雲端模型擔任指揮官、地端無審查模型負責執行雲端拒答任務」**。屬硬體選型與模型清單參考，歸檔備查，不另開實作任務。

---

## 一、10 款實測模型基準對照（取自貼文與終端機實測圖）

| 模型 | 量化 / 量級 | 約佔記憶體 | 生成速度 (t/s) | 讀入速度 (t/s) | 適用情境 / 備註 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Inkling 2 Mini 26B` | SQ-20（SQ-10 約 10.5GB） | 約 22GB | 17–35 | 770–1,300 | 美國開源，小顯存最通用首選 |
| `Qwen3.8 27B Heretic` | NVFP4 | 約 21GB | 25–43 | 約 2,000 | Dense 模型，適合 4090/5090 等高頻寬顯卡寫程式 |
| `Occamy 1.0 35B` | Q6_K（Qwen3.6 35B 改） | 約 29GB | 55–64 | 約 1,650 | MoE 每次僅用 ~3B，長上下文穩定主力 |
| `Nemotron 3.5 Bolt 74B` | 24GB 版 | 約 29GB | 57–75 | 600–1,000 | NVIDIA 出品，支援看圖與看影片（22 題過 16 題） |
| `★ Qwen3.8 Flash Next 125B` | Q3 (Swift 1.5 IQ3_S) | 約 58GB | 48–55 | 約 2,000 | GB10 主力（MoE 每次僅用 ~6B） |
| `★ Qwen3.8 Flash Next 125B` | 4bit MLX（Mac 專用） | 約 72GB | 106–132 | 1,700–2,100 | Mac 128GB 高速主力 |
| `★ Qwen3.8 Flash Next 125B` | Q4 (UD-IQ4_XS) | 約 78GB | 43–50 | 約 2,200 | 更接近原版品質 |
| `★ Qwen3.8 Flash Next 125B` | Q5 MLX (oQ5e，Mac 專用) | 94–110GB | 52–78 | 約 1,660 | 128GB Mac 最高品質（開了佔滿資源） |
| `Hy4-Flash 220B` | SQ-64 | 約 59GB | 35–74 | 750–830 | 騰訊新模型，官方宣稱 64GB RAM + 8GB GPU 可跑 |
| `Hy4-Flash 220B` | SQ-96 / SQ-128 | 100–112GB | 28–41 | 約 890 | SQ-128 四道程式題全過；須自接拒答修正檔 |

---

## 二、硬體分級建議與原貼文模型庫清單

- **硬體分級**：
  - `≤24GB` 顯卡：選 `Inkling 2 Mini 26B`、`Qwen3.8 27B` 或 `Occamy 1.0 35B`。
  - 影片理解：選 `Nemotron 3.5 Bolt 74B`（對應引擎須用 `llama.cpp`）。
  - `12GB GPU + 64GB RAM`（如 RTX 5070 / 4070 Ti Super）：用 **Strata** 引擎卸載運行 `Qwen3.8 Flash Next 125B`（留言 `RedSuns Chan` 建議 `IQ3_XXS`；`Longtime Chou` 回報公司 10 人團隊用 RTX 6000 跑 Strata 版極流暢）。
  - `64GB–128GB` 統一記憶體：直跑 `Qwen3.8 Flash Next`，高階觀望 `Hy4-Flash`。
- **模型 Repo ID（純文字整理自原貼文）**：
  - 通用：`SC117/Inkling-2-Mini-abliterated-Strata`、`SC117/occamy-1.0-abliterated-FIT-GGUF`、`BoldingBuilds/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-Abliterated-24GB-GGUF`、`SC117/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF`、`SC117/Qwen3.8-Flash-Next-abliterated-UD-GGUF`
  - Mac MLX：`ARC4NUM/Qwen3.8-Flash-Next-Uncensored-MLX-Serve-4bit`、`mlx-community/Qwen3.8-Flash-Next-Uncensored-oQ5e-mtp`
  - DGX-Spark / Hy4-Flash：`SmokeyPete/Qwen3.8-27B-Heretic-NVFP4-DGX-Spark`、`strata-engine/Hy4-Flash-Strata`、`alesha-pro/Hy4-flash-Uncensored-GGUF`

---

## 三、留言區關鍵避坑與工作流模式

1. **Strata 官方內建模型「都有審查」**：作者與留言 `Chen Nick` 明確提醒不要直接從 Strata 內建清單下載（浪費頻寬），應手動下載 `SC117` 等去審查模型後，在 Strata 指定本地路徑。
2. **多模態引擎差異**：`Garfield Huang` 實測 LM Studio（雖底層也是 `llama.cpp`）會回覆無法看影片；作者明確表示已不再手動折騰 LM Studio，而是**直接交給 `Claude Code` 幫忙裝引擎、改拒答修正檔（如 Hy4-Flash）與測速**。
3. **雲地協作定位**：保留訂閱制雲端模型（如 Claude）做高階規劃與指揮，把會觸發思想或內容審查的子任務派給地端無審查模型處理。
