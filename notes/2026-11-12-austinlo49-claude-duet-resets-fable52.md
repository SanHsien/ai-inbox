---
id: "2026-11-12-austinlo49-claude-duet-resets-fable52"
title: "Claude Duet 研究預覽附贈 limit resets（Pro 3 次、Max／Ultra 1 次，12/15 到期）"
source_url: "https://www.threads.com/share/BBMpowrj3D"
source_platform: "threads"
author: "@austinlo49"
analyzed_at: "2026-11-12"
analyzed_by: "antigravity"
status: archived
cluster: 1
cluster_role: "Claude配額管理"
short_title: "Duet申請送Resets"
source_review: partial
source_reviewed_at: 2026-11-16
source_review_note: "未登入讀到 10 則／共 12 則回覆，其餘 2 則要登入；作者圖 1 張與留言附圖已看"
source_images: 1
source_replies: 10
tags:
  - claude
  - claude-duet
  - fable-5-2
  - anthropic
  - resets
  - usage-limit
  - claude-pro
  - claude-max
  - agent
---

# Claude Duet 研究預覽附贈 limit resets（Pro 3 次、Max／Ultra 1 次，12/15 到期）

- **來源連結**：[Threads 貼文：@austinlo49](https://www.threads.com/share/BBMpowrj3D)
- **發布平台 / 作者**：`threads` / `@austinlo49`
- **分析日期**：`2026-11-12`
- **當前狀態**：`⚪ 不做 (Archived)`

---

## 0. 原始資料盤點

> 2026-11-16 以未登入瀏覽器重看原貼文。貼文顯示 12 則回覆；未登入讀到 10 則（含作者 3 則），其餘 2 則要登入才看得到。

- **作者圖片**：1 張。圖 1 是 Anthropic 寄給作者的 Duet 通知信截圖，標題「3 limit resets for the research preview」。信中說明 Duet 與方案共用用量、背景檢查也算用量、做財務模型或簡報這類大任務用得更多；為了讓使用者在研究預覽期間有空間試用，已在帳號加上 3 次 limit resets，要在 12 月 15 日前從 claude.ai 的用量頁使用。
- **作者留言補充**：回覆網友說自己等了大約半個月才收到邀請；對「只拿到 1 次」的網友回「可能運氣不好」（這個說法不對，見下）。
- **網友留言重點**：
  - **hanbingjheng**：轉述信件內容，補上期限 12/15。
  - **boowenchen（附信件截圖）**：他的信標題是「Usage and your limit reset」，內文寫只加了 **1 次** limit reset，同樣 12 月 15 日到期。
  - **brt_1122**：貼出官方說明中心文章 [開始使用 Claude Duet](https://support.claude.com/zh-TW/articles/17631495)（連結預覽卡只有 Claude Support 標誌）。
  - **lifeather**：申請很久都沒下來。**clubababyotter**：有了 Duet 但換一台主機就不見（無人解答）。**arguskao**：問怎麼申請、道謝。
- **對分析的影響**：
  - **原稿的更正方向錯了，已改回。** 2026-11-14 的修訂把「送 3 次 resets」判為「貼文誤植，那是 Fable 5.2 上市促銷，與 Duet 無關」，理由是官方 Duet 產品頁沒提 resets。但作者上傳的信件截圖標題就寫著 research preview 的 3 次 limit resets，那次修訂沒看圖。
  - **以官方說明中心為準**（2026-11-16 實際開啟留言貼的文章）：研究預覽期間 Anthropic 會在帳號加上完整的 limit reset，每次使用會重新填滿 5 小時工作階段與每週限制；數量依方案——**Pro 3 次、Max 與 Ultra 1 次**；未使用的在 **2026-12-15** 過期。這同時解釋了留言者為什麼只拿到 1 次（方案不同，不是運氣）。
  - 貼文說「申請就送」也不精確：resets 是**獲准加入研究預覽後**才加到帳號，等候名單分批開放，作者自己等了約半個月。
  - 「Reset 有效期未公開」「3 次 reset 的換算量未公開」兩處原稿說法已不成立，已改。標題、5W1H、福利機制表、CQR、評估表一併更正。
  - Fable 5.2 公告裡另有一筆「依訂閱時間長短給 1～3 次 Fable resets」的促銷（原稿 2026-11-14 查證），與本篇的 Duet resets 是兩件事，兩者都存在。
  - 官方說明中心仍寫明僅限美國地區的 Pro／Max／Ultra 帳戶，Team／Enterprise 尚未開放；原稿這部分正確。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：Anthropic（Claude Duet）；貼文作者 `@austinlo49`。
- **What**：Claude Duet 研究預覽的 waitlist 申請；獲准加入後帳號會被加上 limit resets（Pro 3 次、Max／Ultra 1 次，官方說明中心 2026-11-16 查證）。
- **Why**：Duet 背景執行耗配額，社群視 resets 為緩衝。
- **How**：至 claude.com/duet 加入 waitlist（見下方技術架構）。
- **When & Where**：Pro／Max／Ultra 訂閱者，**僅限美國**（官方頁寫 in the US）；研究預覽期間。
- **Key Metrics / Numbers**：官方頁僅寫 6,000+ connectors；官方公告 https://www.anthropic.com/news/claude-fable-and-mythos-5-2 寫明「one to three Fable resets based on how long they've subscribed」（2026-11-14 實際取得該頁確認原文），這是 Fable 5.2 上市的另一筆促銷。Duet 研究預覽的 resets 則寫在官方說明中心：Pro 3 次、Max／Ultra 1 次，2026-12-15 到期（2026-11-16 查證；原稿曾誤判為貼文誤植，已更正）。

### 摘要原文

**@austinlo49** 提示 Claude Pro/Max 用戶：申請 **Claude Duet** 早期測試可獲得 **3 次 limit resets**（作者附的官方通知信截圖與官方說明中心都證實；3 次是 Pro 方案的數量，Max／Ultra 為 1 次），且通知郵件恰巧在 **Fable 5.2** 發布當天（2026-11-09）寄出，社群視為送炭時機。

**核心資訊**：
- Duet = Anthropic 自主 agent app，2026-10 推出研究預覽，Pro/Max 訂閱者 waitlist 申請
- 加入研究預覽的附帶福利：limit resets（Pro 3 次、Max／Ultra 1 次），2026-12-15 前要用掉
- 適用對象：已有 Claude Pro 或 Max 訂閱的用戶（**僅限美國**；官方頁另列 Ultra，Team／Enterprise 尚未納入）

---

## 技術架構深挖

### Claude Duet 是什麼

```
Claude Duet（Research Preview，2026-10）
  ├── 底層模型：Claude Opus 5.5
  ├── 執行方式：雲端 VM 自主執行（非等待 prompt）
  ├── 整合工具：Gmail / Slack / Calendar / QuickBooks / HubSpot（以下清單官方頁僅寫 6,000+ connectors，個別項目未逐一核對）
  ├── 自主行為：晨間摘要、背景任務監控、主動通知
  └── 安全閘門：
       ├── 傳送訊息 → 需人工批准
       ├── 付款行為 → 需人工批准
       ├── 刪除資料 → 需人工批准
       └── 簽署協議 → 需人工批准
```

**定價**：Pro/Max 訂閱者免費加入（無額外費用），但背景執行直接消耗現有方案的 token 配額。

### Reset 福利機制

| 項目 | 說明 |
|------|------|
| **Reset 數量** | Pro 3 次；Max／Ultra 1 次（官方說明中心） |
| **Reset 效果** | 每次使用會重新填滿 5 小時工作階段與每週限制；在網頁版或 Claude Desktop 的「設定 > 使用」手動選擇使用 |
| **到期日** | 未使用的在 2026-12-15 過期 |
| **適用層級** | Pro／Max／Ultra 訂閱者（美國地區帳戶） |
| **申請管道** | claude.com 的 Duet 申請頁面（waitlist） |
| **通知時間** | 2026-11-09（Fable 5.2 發布當日）開始寄出 |

### 配額消耗現況（Duet 的隱患）

```
Claude Duet 背景 Agent 執行鏈：
  每次背景掃描 → 消耗 token
  晨間摘要（每日）→ 消耗 token
  監控整合工具（持續輪詢）→ 消耗 token
           ↓
  比人工聊天快得多地吃掉月配額
  → 社群常見「reset 耗盡」問題
  → reset（Pro 3 次、Max／Ultra 1 次）是緩衝
```

### Fable 5.2 背景（同日發布，解釋「雪中送炭」）

| 項目 | 資訊 |
|------|------|
| **發布日** | 2026-11-09 |
| **定位** | Anthropic 旗艦模型，同步發布 Mythos 5.2（資安/生科） |
| **強項** | 程式碼生成、複雜邏輯推理、多步驟 Agentic Work |
| **社群焦點** | Vibe Coding 一鍵生成遊戲（網頁遊戲、3D 關卡） |
| **配額消耗** | 長時間 agentic 任務極耗配額，reset 需求更高 |

Fable 5.2 發布同日 Duet reset 通知到信箱，使用者實際測 Fable 5.2 的 token 消耗量遠高於一般對話，reset 相當於額外緩衝，社群評價「時機完美」。

---

## ASCII 情境圖

```
申請 Claude Duet waitlist
        │
        ▼
  Anthropic 寄出通知郵件
  （2026-11-09，Fable 5.2 發布同日）
        │
        ├──→ 解鎖 Duet 功能（背景自主 agent）
        │
        └──→ 帳號加上 limit resets（Pro 3／Max、Ultra 1，12/15 到期）
                    │
                    ▼
           Fable 5.2 測試 / 大量 token 消耗
                    │
                    ▼
              reset 緩衝發揮作用
              「雪中送炭」✓
```

---

## 2. CQR 深入論證檢驗（選填）

- **Claim**：加入 Duet 研究預覽可得 3 次 resets。
- **Evidence**：作者附的官方通知信截圖（3 次）、留言者的信件截圖（1 次）、官方說明中心「限制重設」段（Pro 3 次、Max／Ultra 1 次，2026-12-15 到期；2026-11-16 查證）。官方 Duet 產品頁寫明研究預覽、僅限美國、與方案共用用量。
- **Reasoning**：主張成立，但只對 Pro 方案是 3 次；「申請就送」應改為「獲准加入後才有」。地區限制使非美國帳戶無法申請。

---

## 3. 啟發與適用性評估

### 與本機使用情境對照

| 評估維度 | 結論 |
|---------|------|
| **適用性** | 有 Claude Pro/Max 訂閱則直接可申請，reset 是實質配額福利 |
| **Duet 安全性** | 有明確人工批准閘門（付款/刪除/發訊），設計合理 |
| **配額風險** | Duet 背景執行會持續消耗配額，需監控避免提前耗盡 |
| **Fable 5.2 整合** | 適合重度 agentic 任務（程式碼/遊戲生成），輕量任務用 Opus 5.5 更划算 |
| **Reset 有效期** | 2026-12-15 到期（官方說明中心） |

---

### 評估結論與處置

**評分：⭐⭐⭐（3/5）**

此貼為**使用技巧提示**，非開源工具分析。核心價值：提醒有訂閱的用戶去申請 Duet 以換取免費 resets。資訊簡短；申請窗口與資格（僅限美國）請以官方頁為準。

**扣分點**：Duet 背景執行的配額消耗模式不透明；waitlist 名額限制不明。

**處置**：僅歸檔備查；無可驗收的具體任務，不衍生待辦（原核取清單因無可驗收 DoD 已刪除）。

---

## 4. 拆解待辦事項（Action Items）

無（零任務判斷：維持歸檔）。

**參考連結**：
- Claude Duet 官方頁面：https://claude.com/duet（需登入）
- 官方說明中心（含限制重設數量與到期日）：https://support.claude.com/zh-TW/articles/17631495
- Fable 5.2 發布公告：https://www.anthropic.com/news/claude-fable-and-mythos-5-2
- 社群討論：reddit.com/r/ClaudeAI（搜尋 "duet resets"）
