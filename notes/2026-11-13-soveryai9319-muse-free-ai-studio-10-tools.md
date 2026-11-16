---
id: "2026-11-13-soveryai9319-muse-free-ai-studio-10-tools"
title: "Muse 指揮 10 個免費工具組 AI 工作室：Kaggle/Simular/OpenRouter 等零成本架構"
source_url: "https://www.threads.com/share/BAexxbxxvd"
source_platform: "threads"
author: "@soveryai9319"
analyzed_at: "2026-11-13"
analyzed_by: "antigravity"
status: archived
cluster: 3
cluster_role: "免費算力整合"
short_title: "Muse指揮10免費工具"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "未登入讀到 9 則／共 40 則回覆，其餘 31 則要登入；貼文無作者圖"
source_images: 0
source_replies: 9
tags:
  - muse
  - free-tier
  - kaggle
  - github-actions
  - simular-box
  - openrouter
  - cloudflare
  - supabase
  - google-colab
  - sakupa
  - zero-cost
  - ai-studio
---

# Muse 指揮 10 個免費工具組 AI 工作室：Kaggle/Simular/OpenRouter 等零成本架構

- **來源連結**：[Threads 貼文：@soveryai9319](https://www.threads.com/share/BAexxbxxvd)
- **發布平台 / 作者**：`threads` / `@soveryai9319`
- **分析日期**：`2026-11-13`
- **當前狀態**：`⚪ 不做 (Archived)`

---

## 0. 原始資料盤點

> 2026-11-16 以未登入瀏覽器重看原貼文（發文日 2026-11-09；83 讚、40 則回覆、232 次分享）。未登入讀到 9 則回覆，其餘 31 則要登入才看得到。

- **作者圖片**：無。貼文是純文字清單，沒有圖、沒有影片，也沒有任何成果截圖或架構圖。
- **作者留言補充**：無。讀到的 9 則回覆裡沒有作者本人的回覆，也沒有補連結或設定細節。
- **網友留言重點**：
  - 讀到的 9 則裡有 7 則是在貼**邀請碼**（其中同一個帳號重複貼了 3 次），話術是「互相兌換，雙方可得十億免費 token」。留言沒寫明是哪個服務的邀請碼；邀請碼本身不抄進筆記。
  - **reindeer.ainote**：OpenRouter 上好的模型都要付費。這與本筆記對 `:free` 模型每日 50 次上限的整理一致。
  - **nix.0910**：清單裡有兩個服務沒用過（接著也是貼碼）。
  - 沒有任何人回報照這套架構實際跑起來的結果。
- **對分析的影響**：
  - **這篇更像導流貼文，不是實作分享**：沒有圖、沒有作者補充、沒有實測回報，留言區大半是邀請碼互換。原稿「概念紮實、可複製的低成本架構」的評語缺乏依據——貼文只有工具清單與三步驟口號，沒有任何一步的設定方法。評估結論已補上這點，評分維持 2/5。
  - 各服務的免費額度數字（Kaggle 每週 30 小時、Workers 每日 10 萬次等）不是貼文寫的，是建檔時另外查的；原稿表頭寫「工具清單（貼文原文）」會讓人誤以為額度出自貼文，已改表頭說明。貼文原文對每個工具只有一句用途。
  - Cloady 仍查不到；留言也沒有人說明。
  - 結論與處置不變（歸檔、不採用 token 集中給第三方 Agent 的做法、不衍生任務）。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：貼文作者 @soveryai9319（凡森）；涉及 10 個第三方免費服務。
- **What**：讓 Muse Agent 統一指揮 10 個免費工具，組成零成本 AI 工作室。
- **Why**：以免費額度拼出算力、資料庫、部署與排程。
- **How**：Muse 規劃部署與排程，各服務帳號授權交給 Muse（見下方架構圖）。
- **When & Where**：個人實驗與低流量專案；各服務額度以官方定價頁為準。
- **Key Metrics / Numbers**：額度數字多為貼文自述；Simular 首頁僅寫 box 免費，credits 數字未查證。

### 摘要原文

**@soveryai9319（凡森）** 分享一套「讓 Muse Agent 統一指揮 10 個免費工具」的零成本 AI 工作室架構。
核心思路：先把每個免費服務的帳號與 token 收攏給 Muse（**與本庫「絕對零機密」原則衝突**：AGENTS.md 第 4 節第 2 條規範機密不得寫入 repo，本作法雖非寫入 repo，但把 10 個服務的 token 集中交給單一第三方 Agent，風險同源），再讓 Muse 自動規劃部署、排程任務、排錯，人只需要負責帳號授權確認。

工具清單（工具名稱與用途出自貼文；「免費額度重點」一欄是建檔時另查的，貼文沒有寫額度數字）：

| # | 工具 | 用途 | 免費額度重點 |
|---|------|------|------------|
| 1 | Kaggle | GPU 算力 | 雙 T4 GPU，每週 30 小時 |
| 2 | GitHub Actions | 自動任務排程 | 2,000 分鐘/月（公開 repo 無限） |
| 3 | Simular Box | AI 雲端電腦 | 首頁僅寫 box 免費；每日 1,000 credits（貼文自述，credits 數字未查證），4vCPU/8GB RAM |
| 4 | Cloady | 免費容器 | 資訊有限（見下方說明） |
| 5 | Supabase | 資料庫 | 500MB PostgreSQL，50MB 儲存 |
| 6 | OpenRouter | 模型 API | `:free` 模型 50 req/day（付 $10 升至 1,000） |
| 7 | Cloudflare Workers | 輕量服務部署 | 100,000 req/day，10ms CPU |
| 8 | Google Colab | GPU 算力 | T4 GPU 免費（有使用時間上限） |
| 9 | Cloudflare R2 | 物件儲存 | 10GB 免費，Class A 100萬次/月 |
| 10 | Sakupa | 靜態網站 | 30 天免費預覽，MCP Server 部署 |

---

## 技術架構深挖

### 整體架構圖

```
Muse Agent（統一指揮）
       │
       ├── 算力層
       │     ├── Kaggle（雙 T4 GPU，模型訓練/推論）
       │     ├── Google Colab（T4，快速實驗）
       │     └── Simular Box（雲端 VM，Agent 自主執行環境）
       │
       ├── 自動化層
       │     └── GitHub Actions（排程任務、CI/CD、webhook）
       │
       ├── 模型 API 層
       │     └── OpenRouter（:free 模型路由，零成本 LLM 調用）
       │
       ├── 後端服務層
       │     ├── Cloady（容器，細節不明）
       │     └── Cloudflare Workers（邊緣計算，輕量 API）
       │
       ├── 資料層
       │     ├── Supabase（PostgreSQL + 實時 DB）
       │     └── Cloudflare R2（物件儲存，S3 相容）
       │
       └── 前端/靜態層
             └── Sakupa（MCP Server，AI 聊天 → 一鍵部署靜態站）
```

### 各工具深挖

**Kaggle（雙 T4 GPU）**
- 免費條件：需手機號驗證，每週 30 小時 GPU 配額
- 適合：批次推論、Fine-tuning、Notebook 式任務
- 限制：單次 session 最長 12 小時，不支援持久後台服務

**GitHub Actions（自動任務）**
- 公開 repo：無限分鐘；私有 repo：2,000 分鐘/月
- 適合：Cron job、模型推論觸發、資料同步
- Muse 整合點：透過 workflow dispatch 或 schedule 觸發 Muse 任務

**Simular Box（AI 雲端電腦）**
- 官網：https://box.simular.ai
- 規格：4 vCPU / 8GB RAM / 40GB disk，Ubuntu + 瀏覽器 + terminal
- 免費：首頁僅寫 box 免費；每日 1,000 credits 為貼文自述，未查證（無需信用卡、workspace 持久化亦未查證）
- 兼容：Claude / ChatGPT / Cursor / Codex（MCP 相容）
- **Muse 整合重點**：Simular Box 是 Muse 的「身體」，Agent 在此自主執行任務

**Cloady（免費容器）**
- 公開資訊極少，無法找到官方 GitHub 或文件站
- 推測：可能為小眾/封測服務，或作者筆誤（近似 Koyeb/Render/Cloud Run）
- **建議替代**：Google Cloud Run（scale-to-zero，每月數百萬 req 免費）或 Render（750h/月）

**Supabase（資料庫）**
- 免費層：1 個專案，500MB PostgreSQL，50MB 檔案儲存，50,000 月活用戶
- 特色：Realtime 訂閱、Vector 擴展（pgvector，適合 RAG）
- Muse 整合點：Agent 寫入結構化資料與向量嵌入

**OpenRouter（免費模型 API）**
- 免費帳號：50 req/day（付 \$10 一次性升至 1,000 req/day）
- `:free` 模型清單：Gemma、Qwen、Nemotron 等，透過 `openrouter/free` 自動路由
- 注意：credit 低於 0 時，`:free` 模型也會被封鎖（402 錯誤）

**Cloudflare Workers（邊緣服務）**
- 免費：100,000 req/day，10ms CPU 時間/req，128MB 記憶體
- 適合：API proxy、webhook 接收、輕量 LLM routing

**Google Colab（GPU 算力）**
- T4 GPU 免費，使用時間有上限（非固定，依平台負載動態調整）
- 適合：快速實驗，不適合 24/7 後台服務

**Cloudflare R2（物件儲存）**
- 免費：10GB，Class A（PUT）100萬次/月，Class B（GET）1,000萬次/月
- 無 egress 費用（不收流出頻寬費），S3 API 相容
- Muse 整合點：模型快取、任務 artifact 儲存

**Sakupa（靜態網站 + MCP）**
- npm：`npx -y @sakupa/mcp@latest`
- 機制：AI 聊天 → Sakupa MCP → 本地 build → 部署靜態站
- 免費：30 天可更新預覽；付費長期保留（約 ¥200/網站/月）
- 特色：**無需帳號**，credentials 存本地 `~/.sakupa/credentials/`

### Muse 工作流（三步驟）

```
① 把 10 個工具的帳號 token 交給 Muse
       ↓
② Muse 自動規劃：先配雲端電腦 + GPU + 模型 API
   → Simular Box（VM）
   → Kaggle / Colab（GPU）
   → OpenRouter（:free 模型）
       ↓
③ Muse 接入資料與自動任務層
   → Supabase（DB）
   → Cloudflare R2（Storage）
   → GitHub Actions（排程）
   → Cloudflare Workers（邊緣 API）
   → Sakupa（前端發布）

人工介入點：帳號授權確認（僅此一項）
```

---

## 實際成本試算（月）

| 層級 | 工具 | 月費 |
|------|------|------|
| GPU | Kaggle + Colab | \$0 |
| VM | Simular Box（免費；credits 數字未查證） | \$0 |
| 自動化 | GitHub Actions（公開 repo） | \$0 |
| 模型 | OpenRouter :free | \$0（50 req/day）|
| DB | Supabase | \$0 |
| 儲存 | Cloudflare R2 | \$0（≤10GB）|
| 邊緣 | Cloudflare Workers | \$0（≤100k/day）|
| 前端 | Sakupa | \$0（30 天，更新可延）|
| **合計** | | **\$0** |

---

## 2. CQR 深入論證檢驗（選填）

- **Claim**：一個 Agent 指揮 10 個免費工具即可零成本運作 AI 工作室。
- **Evidence**：額度數字為貼文自述，僅部分對照官方定價頁；Simular credits、Cloady 皆未查證。
- **Reasoning**：免費額度會變動、Cloady 不可驗證；token 集中交給單一 Agent 與零機密原則衝突，風險大於貼文給的好處。

---

## 3. 啟發與適用性評估

### 與本機防線對照

| 評估維度 | 結論 |
|---------|------|
| **安全性** | 把多服務 token 集中給 Muse 是最大風險點；需確認 Muse 的 token 儲存是否加密 |
| **Cloady 可信度** | 無法驗證，建議替換為 Google Cloud Run 或 Render |
| **OpenRouter 陷阱** | 付費 credit 低於 0 時 :free 模型也停用，需監控餘額 |
| **Simular Box** | 每日 credits 有限，長時間 Agent 任務可能超出 |
| **Sakupa** | MCP 路線有趣，30 天需手動更新，長期需付費或替換 Cloudflare Pages |
| **整體評估** | 架構可行，但 Cloady 存疑、token 集中管理有安全風險 |

---

### 評估結論與處置

**評分：⭐⭐（2/5）**（原 4/5；因「把 10 個服務 token 交給 Muse」與零機密原則衝突，且不安裝，故調降使評分與歸檔結論一致）

「用 AI Agent 指揮一群免費服務」這個概念說得通，但貼文本身只有清單與口號，沒有設定方法、沒有成果畫面，留言區也沒有人回報實作結果（2026-11-16 重看原貼文與留言後補）；以下的可行性判斷來自對各服務的另行查證，不是貼文提供的。
Simular Box（VM） + OpenRouter（模型） + Supabase（DB） + Cloudflare（邊緣+儲存） + GitHub Actions（排程）這五件是核心骨幹，組合可行性高。
Sakupa 的 MCP 部署流程是亮點（AI 聊天直接發布靜態站）。

**扣分點**：Cloady 無可查資訊；token 集中管理安全風險未提及；Kaggle/Colab 不支援持久後台；貼文無任何實作證據，留言區大半是邀請碼互換。

**處置**：僅歸檔備查；不採用 token 集中給第三方 Agent 的作法，不衍生待辦（原核取清單因無可驗收 DoD 已刪除）。

---

## 4. 拆解待辦事項（Action Items）

無（零任務判斷：維持歸檔）。

**參考連結**：
- Simular Box：https://box.simular.ai
- OpenRouter 免費模型：https://openrouter.ai/models?order=newest&supported_parameters=free
- Sakupa MCP：https://www.npmjs.com/package/@sakupa/mcp
- Supabase 免費層：https://supabase.com/pricing
- Cloudflare R2：https://www.cloudflare.com/developer-platform/r2/
