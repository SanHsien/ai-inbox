---
id: 2026-10-21-strata-consumer-gpu-large-llm-inference
title: "Strata 架構解構：12GB 消費級顯卡流暢運行 125B MoE 大模型、VRAM-RAM-SSD 三層卸載黑科技與 Coding Agent 離線本地化部署實踐"
source_url: "https://github.com/Niko1221/Strata"
source_platform: "GitHub / 社群貼文"
author: "Niko1221 / 社群分享"
github_repo: "https://github.com/Niko1221/Strata"
analyzed_at: 2026-10-21
analyzed_by: "Antigravity"
status: archived # pending | in-progress | done | archived
cluster: "3"
cluster_role: "端點資安與雲端基建"
short_title: "Strata 12GB 顯卡運行 125B 大模型"
source_review: partial
source_reviewed_at: 2026-11-18
source_review_note: "原貼文無法認定（4 則同主題候選貼文的文字、作者圖片與留言都讀過：Threads 09-29、10-05、10-18 各一則與 Facebook 09-29 一則；其中三則寫 12GB 顯示卡要配 64GB 記憶體、一則寫 8GB 顯示卡即可，本筆記原稿寫的卻是 12GB 配 32GB，四則也都沒有原稿的圖書館比喻與 RTX 3080 Ti 範例，無法確定哪一則是來源）；替代來源 repo README 2 張圖與 4 則 issue 的 10 則留言已讀完"
source_images: 4
source_replies: 69
tags:
  - strata
  - local-llm
  - qwen-125b
  - consumer-gpu
  - tiered-offloading
  - speculative-decoding
  - agent-tools
---

# Strata 架構解構：12GB 消費級顯卡流暢運行 125B MoE 大模型、VRAM-RAM-SSD 三層卸載黑科技與 Coding Agent 離線本地化部署實踐

- **來源連結**：[Niko1221/Strata (GitHub)](https://github.com/Niko1221/Strata) ｜ [Qwen3.8-Flash-Next (HuggingFace)](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)
- **發布平台 / 原作者**：`GitHub / 社群貼文` / `Niko1221 / 社群分享`
- **分析日期**：`2026-10-21`
- **當前狀態**：`⚪ 已封存 (Archived)`

---

## 0. 原始資料盤點

> 2026-11-18 補讀：原貼文無法認定，維持 `partial`。找到 4 則同主題的候選貼文，**文字、作者自己的圖、留言都讀過**，當成相關來源記在下面；沒有任何一則能確定是本筆記的來源。
>
> - **候選 1**（Facebook，陳盟升，2026-09-29）：<https://www.facebook.com/darkschen/posts/pfbid0wFtVNQ9Z34KynK56NeoxZbnhzCAtgiHQsdaSf7NAgXPHHUv4ic6xMU6pYJT45MYql>。只有三行：12GB 顯示卡加 64GB 記憶體就能跑 125B 的 Qwen3.8-Flash-Next，預載速度破千、長上下文每秒 40 到 60 個 token。圖 1 張是 README 截圖（MIT 授權；官方在 RTX 5070 12GB、64GB 記憶體上量到的各量化版本速度表）。留言計數 29 則，顯示 19 則已讀完：有人說量化到這種程度已不堪用；有人反駁說自己用較高位元的量化加 128K 上下文是可用的，只是慢；有人問降智程度與正確率會掉多少，沒有人拿出數字。
> - **候選 2**（Threads，`@leeunhn`，2026-09-29）：<https://www.threads.com/@leeunhn/post/Dd37dDok7T9>。寫「8GB 以上的 NVIDIA 顯示卡就能跑」、一鍵安裝、相容 OpenAI 與 Anthropic 的 API、當時 1,423 顆星。圖只有 repo 預覽卡。留言計數 12 則，讀到 10 則：第一則就更正「記憶體最低要 64GB」；一位用 RTX 4070 Super 12GB 加 64GB 跑 IQ2_XS 約每秒 60 個 token；一位用 **RTX 3060 12GB、i7-10700K、DDR4 64GB** 跑 IQ3_XXS，聊天約每秒 30、寫程式約 25，顯示卡記憶體用 11GB、系統記憶體用 55GB，寫一個小遊戲約 20 分鐘；有人提醒量化到這個程度，agent 出錯機率會大增。
> - **候選 3**（Threads，`@jay.janitor_`，2026-10-05）：<https://www.threads.com/@jay.janitor_/post/DeFT7Fcky0F>。寫 12GB 顯示卡加 64GB 記憶體順跑 125B。圖只有 repo 預覽卡。留言計數 23 則，讀到 15 則：一位把 RTX 3060 直通給虛擬機、64GB、256K 上下文跑 IQ3_XXS，一開始每秒 25、上下文過 128K 後掉到 15，而且**只有一個處理槽、不能同時處理多個請求**；一位換到 32GB DDR4 的機器跑 IQ2，結果一直重複輸出文字，結論是要 64GB 才玩得起來；一位說專案更新太快，花了一個週末處理一直當掉的問題，建議調穩就不要亂更新；有人說慢的 DDR4 與 CPU 會變成瓶頸，只有每秒 30。
> - **候選 4**（Threads，`@atsuki_sammie`，2026-10-18）：<https://www.threads.com/@atsuki_sammie/post/Deoehg2ki7l>。作者用 RTX 3060 12GB 加 64GB 跑 Q3 量化，自稱約每秒 50 個 token，並做了繁體中文安裝助手；續串寫建議配置：RTX 20 系列以上、12GB 顯示卡記憶體、**64GB 記憶體，32GB 只能試部分精簡模型**。作者在留言貼 1 張實測圖：同一道邏輯題，RTX 3060 12GB 跑 IQ2_XS 每秒 62.7、IQ3_S 每秒 55.0，RTX 5080 16GB 跑 IQ3_S 每秒 97.7（測試機是 i9-14900KF 加 DDR5 64GB；圖上註明是單題單次結果）。留言計數 32 則，讀到 15 則，作者一再回覆「這款基本要 64GB，大部分都塞在記憶體」。
> - **讀取範圍**：Threads 三則各捲到頁尾，讀到的則數少於計數，差額是收合的子回覆與平台不顯示的回覆，沒有逐則點開；留言者自己貼的圖沒有看。
> - **哪一則最接近**：候選 4。日期在本筆記前三天，而且「RTX 20 系列以上、12GB」的寫法與原稿相同。但它寫的是 64GB，原稿寫 32GB；原稿的圖書館比喻、RTX 3080 Ti 範例、macOS 支援，四則裡都沒有，比較像是分析時從 README 另外讀來或自行延伸的。所以無法認定。
> - **對分析的影響**：
>   - **原稿「12GB 加 32GB 記憶體即可流暢執行」站不住**。三則貼文與多位留言者的實測一致指向 64GB；32GB 的實測是一直重複輸出。1.1 節已補註。
>   - RTX 3060 12GB 的實測速度落差很大：每秒 15 到 30（DDR4 或虛擬機）對上 55 到 63（DDR5 新平台）。記憶體與 CPU 的速度影響很大，不能只看顯示卡。
>   - 新增兩項使用上的限制：一次只能處理一個請求；專案更新頻繁、穩定性靠自己顧。低位元量化對 agent 任務正確率的影響，留言有人擔心，但沒有人提供數字。
>   - 結論（封存）不變。以下是 2026-11-16 看 repo 的紀錄。

> 2026-11-16 重審：本篇原始來源是 GitHub repo（frontmatter 寫「社群貼文」但沒有留下貼文連結，無從回看）。這次看了 README 全文、README 內 2 張截圖、`docs/MODELS.md` 的記憶體需求段，以及 4 則 issue 的留言共 10 則（#6072、#6074、#6090、#6082，其中 #6082 無留言）。

- **作者圖片**：共 2 張（README 內的產品截圖；商標與徽章不計）。
  - 圖 1（桌面 App）：左側對話、右側即時預覽 `index.html`；使用的模型是 Qwen3.8-Flash-Next 的 Gyro-S 量化版，介面有 Subagents、Skills、Monitor、Models 等入口，輸入框旁有「Bypass permissions」選項。
  - 圖 2（終端監控）：服務位址 `http://127.0.0.1:18500`、模型 Gyro-S、上下文 32K；RTX 5070，VRAM 10.4／12 GB，快取 3,099 個專家；系統 RAM 用到 47.7／63 GB；生成 45.1 tok/s；近期請求的 prompt 大多命中重用快取。
- **作者留言補充**：README 現況與本筆記寫作時有出入：安裝改成 `curl … | sh`／`irm … | iex` 一行指令與桌面安裝檔；模型清單列出 Qwen3.8-Flash-Next 與 Qwen3.6-35B-A3B 兩種。`docs/MODELS.md` 寫明：32 GB RAM 配 12～16 GB 顯卡只跑得動 coding 專用的 Coder 量化版；一般尺寸要 48 GB（Q2_0、IQ2_XS）到 64 GB RAM。
- **網友留言重點**：
  - #6072（為何無預警移除 DeepSeek）：留言者整理的說法是，維護者先前拒絕支援其他 MoE 架構，衍生出分支專案 Project Maya；Strata 之後把 Maya 的 DeepSeek 引擎移植回來，引發出處與治理爭議，現在已移除 DeepSeek 支援。這是留言者的推測，未經維護者證實。另有人貼出自行保留該引擎的分支。
  - #6074（效能回報）：兩位使用者用 16 GB 顯卡實測新版 prompt 讀取速度，一位在 20K 長度退步 13%、其他長度持平或小幅進步；另一位在 Windows 上 16K～32K 進步 20% 以上。兩人的機器都是 96 GB 等級的 RAM。
  - #6090 只有機器人的格式提醒。
- **對分析的影響**：
  - 原筆記 1.1 寫「12 GB 顯卡＋32 GB RAM 即可流暢運行 125B」。依 `docs/MODELS.md` 與圖 2（12 GB 顯卡那台實際用了近 48 GB RAM），這個組合只適用 coding 專用的最小量化版；已在 1.1 補上限制。
  - 原筆記寫 API「預設 8080 埠」，圖 2 顯示的是 18500；已在 1.1 註明以實際啟動畫面為準。
  - 安裝指令是遠端腳本直接管線執行，依全域規則不可照跑；加上 DeepSeek 支援被移除的治理爭議，兩點都支持本篇兩項任務維持「不做」、筆記維持封存。任務未增減。

---

## 1. 核心內容摘要

### 1.1 核心主張：打破硬體壁壘，消費級 12GB/16GB 顯卡流暢執行 125B 旗艦級 MoE 模型

過去要運行 100B+ 參數等級的頂級大語言模型（如 125B 的 Qwen3.8-Flash-Next），傳統做法通常需要高昂的資料中心級伺服器（數百 GB VRAM）或要價不菲的高配統一記憶體硬體（如 128GB/256GB Mac Studio）。

**Strata**（MIT 開源協議）透過極具創意的**三層動態卸載架構（Tiered Offloading）與投機解碼技術**，徹底打破了此一硬體天花板：
- **極低硬體門檻**：只需 **12GB 顯存的消費級顯卡（RTX 20/30/40/50 系列，如 RTX 3080 Ti 12GB）+ 32GB 系統 RAM**，即可在本地運行 125B 參數的 Qwen3.8-Flash-Next（2026-11-18 補：社群貼文與多位留言者的實測都指向要 64GB，32GB 的實測是一直重複輸出；這句以 64GB 為準）（2026-11-16 補：依官方 `docs/MODELS.md`，32 GB RAM 配 12～16 GB 顯卡只跑得動 coding 專用的 Coder 量化版；一般尺寸要 48～64 GB RAM）；
- **全平台覆蓋**：支援 Windows 10/11、Linux、macOS，涵蓋 NVIDIA (CUDA)、AMD (ROCm/HIP)、Intel Arc 與 Apple Silicon；
- **原生 Agent 與 API 相容**：直接提供標準 **OpenAI 與 Anthropic API 兼容端點**（原分析記為預設 8080 埠；README 現行截圖顯示的是 `127.0.0.1:18500`，以實際啟動畫面為準），Claude Code、Codex CLI、Antigravity、OpenCode 等 Coding Agent 可零改動直接串接。

### 1.2 技術架構與「圖書館分層」黑科技原理

Strata 將 125B MoE 模型的 24,576 個稀疏專家（Experts）比喻為圖書館的參考書籍，依硬體傳輸頻寬與延遲進行了精確的階層劃分：

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Strata 三層硬體卸載與推論加速架構                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 顯卡顯存 (GPU VRAM - 書桌 Desk，12~24GB)                           │
│    └─ 存放高頻活躍專家：常駐約 4,000 個最高頻使用的專家權重            │
│    └─ 特點：極速運算，每個 Token 的主力計算都在顯存內完成              │
│                                                                        │
│ 2. 系統記憶體 (System RAM - 閱覽室書架 Shelves，32~64GB)               │
│    └─ 存放完整專家池：容納全部 24,576 個專家權重                       │
│    └─ 運作方式：當預測出現未在桌上的專家時，CPU/PCIe 背景預加載，      │
│                 顯卡無須中斷等待                                       │
│                                                                        │
│ 3. 高速硬碟 (NVMe SSD - 檔案庫 Archive，80GB 空間)                     │
│    └─ 存放 29GB 靜態查詢表 (Lookup Table)：每個 Token 僅讀取極少數行， │
│       不浪費系統 RAM 空間                                              │
│                                                                        │
│ 4. 投機解碼流水線 (Speculative Guess-and-Check Pipeline)               │
│    └─ 小型輔助模型 (Draft Helper) 預先猜測後續數個 Token               │
│    └─ 125B 主模型一次批次校驗全部預測，生成速度提升 1.6x ~ 1.8x        │
│    └─ Prompt 處理支援批次高達 8,192 tokens，吞吐超過 1,000 tokens/s    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 對現有工作流與專案之啟發

### 2.1 與已有資產的對應與查證

1. **GitHub Fork 狀態查證**：
   - 經對真實網址發起 HTTP 狀態碼檢測（`https://github.com/SanHsien/Strata` 回應 404），確認目前個人帳號下**尚未 Fork** `Niko1221/Strata`。
   - 鑑於該工具能大幅降低本地私有化大模型推論的硬體門檻，具有極高的邊緣部署與備援調研價值。

2. **充實「AI 共同大腦」的本地 Worker 與離線降級池（Note 28 & 集群 1）**：
   - 在 Note 28（AI 共同大腦）與 Note 7（跨 CLI 外包編排）中，多代理系統的核心挑戰之一是**雲端 API 額度焦慮與限流（Rate Limit）**；
   - Strata 讓本機 12GB 顯存的開發機直接具備 125B 級別的私有化推理端點，且直接相容 OpenAI / Anthropic 協議；
   - 可在 `agent-advisor` 中配置為**本地高階備援節點（Offline Fallback Worker）**：當雲端 API 斷網、排隊逾時或額度耗盡時，自動轉向本地 `http://localhost:8080/v1` 繼續跑測試、重構或修 Bug。

3. **隱私敏感任務與合規代碼審計**：
   - 依據全域協作規範，涉及內部核心邏輯或敏感資料時不可隨意上傳至第三方公有雲；
   - 借助 Strata 的完全離線特性（No Telemetry、無帳號、無雲端依賴），敏感專案可在純本地閉環中由 125B 模型完成深度的架構分析與靜態審計。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [ ] **`T-20261021-01`**｜**[優先級：低]** 在 Windows 11 本地測試 `Niko1221/Strata` 的安裝與相容性（驗證 CUDA 驅動檢測、CLI/App 啟動與 OpenAI/Anthropic API 本地端點響應）
  - **目標範圍**：`Niko1221/Strata`（本地測試）、本地 Coding Agent API 配置
  - **狀態**：⚪ 不做（宣稱 12GB 顯卡跑 125B 未經查證，要下載數十 GB 且佔用顯卡；維護者已有 Claude／Codex／Gemini 訂閱，不需要本地離線後端）
  - **具體做法**：下載或安裝 Strata Windows 版本，依硬體規格（GPU VRAM + 系統 RAM）配置最小模型分片，啟動本機 API 服務，使用 `curl` 測試 `http://localhost:8080/v1/chat/completions` 是否能正常推論並返回流式回應
  - **驗收標準（DoD）**：Strata 本地端點成功啟動、以 curl 發送請求能在 30 秒內流式輸出回應、記憶體與顯存佔用符合三層分流預期
- [ ] **`T-20261021-02`**｜**[優先級：低]** 評估將 Strata 本地端點整合至 `agent-advisor` 路由矩陣與 Coding Agent 離線降級工作流（Local 125B Offline Fallback）
  - **目標範圍**：`SanHsien/agent-advisor` ＋ 全域 Agent 路由配置
  - **狀態**：⚪ 不做（同 T-20261021-01；agent-advisor 只做 Claude／Codex／Cursor／Antigravity 內建子代理路由，不接外部 Provider）
  - **具體做法**：在 `agent-advisor` 中新增本地 Strata Provider 配置，定義當遠端 API 限流或斷網時，自動路由轉發至 `http://localhost:8080`，並測試以 Claude Code / Codex 連接本機 125B 模型執行程式碼檢查
  - **驗收標準（DoD）**：產出 Provider 路由配置手冊，實測在斷開遠端網路連線時，Agent 能成功調用本地 Strata 完成單一檔案的 Bug 檢測與重構

---

## 4. 關聯筆記與相關任務（Related Notes & Sessions）

- **多 Agent 協同與模型路由調度**：
  - [AI 共同大腦工業級架構全景規劃](./2026-10-19-ai-shared-brain-multi-agent-architecture.md) ｜ 關聯任務：`T-20261019-07`、`T-20261019-08`
  - [雙軌模型分工：/model opusplan 與 /advisor](./2026-10-17-model-routing-opusplan-advisor.md) ｜ 關聯任務：`T-20261017-11`、`T-20261017-12`
  - [跨 CLI 子代理外包編排實踐](./2026-10-17-cross-cli-subagent-orchestration-space-bunny.md) ｜ 關聯任務：`T-20261017-31`、`T-20261017-32`
- **Agent 原生工具鏈與基礎設施**：
  - [GitHub 開源 AI 工具矩陣：Jev/OpenHands/LibreChat](./2026-10-17-github-open-source-ai-toolkit-matrix.md) ｜ 關聯任務：`T-20261017-33`、`T-20261017-34`
  - [CLI-Anything：軟體升級為 Agent-Native CLI](./2026-10-18-cli-anything-agent-native-computer-use.md) ｜ 關聯任務：`T-20261018-11`、`T-20261018-12`
  - [desktop-sense：本機螢幕即時視覺感知](./2026-10-18-desktop-sense-local-screen-context.md) ｜ 關聯任務：`T-20261018-05`、`T-20261018-06`
