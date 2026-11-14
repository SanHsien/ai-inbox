---
id: 2026-11-14-gpt-6-1-terra-codex-work-quota-fast-mode-routing
title: "GPT-6.1 Terra 額度與 Fast 倍率核實：Plus 約 Sol 的 2 倍、Fast 2.5x，但整體額度並未增加"
source_url: "https://learn.chatgpt.com/docs/pricing"
source_platform: "OpenAI 官方文件（使用者提供線索，未附原始出處）"
author: "使用者提供 + 官方頁核實"
analyzed_at: 2026-11-14
analyzed_by: "Antigravity"
status: in-progress
cluster: "1"
cluster_role: "Terra額度路由"
short_title: "Terra額度與Fast倍率核實"
tags:
  - gpt-6-1-terra
  - codex
  - chatgpt-work
  - usage-limits
  - fast-mode
  - model-routing
  - cost-control
---

# GPT-6.1 Terra 額度與 Fast 倍率核實

## 1. Executive Summary

使用者提供一則沒有附出處的線索：

> GPT-6.1 Terra 程式額度增加：僅限 Codex 與 Work 介面，Plus 額度約為 Sol 的 2 倍；切勿開啟 Fast（消耗速度快 2.5 倍），建議日常任務切至 Terra，高難度編程再用 Sol。

2026-11-14 讀取官方頁 <https://learn.chatgpt.com/docs/pricing> 逐項核對。結論：**數字大致屬實，但「額度增加」的措辭不精確，「日常 Terra、高難度 Sol」是未驗證的建議。**

| 線索說法 | 判定 | 官方依據 |
|---------|------|---------|
| 僅限 Codex 與 Work | 相符 | Terra 在 Work 與 Codex 提供（Plus、Pro、Business、Enterprise、Edu），不在 Chat |
| Plus 約 Sol 的 2 倍 | 大致相符（粗估） | Plus 每 5 小時本機訊息：Terra 35–285、Sol 6.1 15–160；區間中點 160 比 87.5 約 1.83x |
| 額度「增加」 | **措辭不精確** | 官方：Overall Work and Codex plan limits are unchanged；是多一個每則耗額較低的模型 |
| Fast 快 2.5 倍 | 相符，但限訂閱內含額度 | Fast：訂閱內含 2.5x，購買 credits 與 Enterprise 隨用隨付 2x |
| 日常 Terra、高難度 Sol | **未驗證** | 官方用量頁沒有品質數據；Models 頁本次未讀 |

細節、完整表格與限制見 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 第 9 節。

## 2. 核實後的關鍵數字

```text
Plus 每 5 小時本機訊息（官方稱估計值，非固定上限）
  Luna 6        350–3,000   ████████████████████████  最高吞吐
  Terra 6.1      35–285     ████████                  約 Sol 的 1.8–2.3x
  Sol 6.1        15–160     ████
  Astra 6         5–45      █

Credits / 100 萬 tokens（輸入／快取輸入／輸出）
  Terra 6.1   25 / 1.25 / 125   → Sol 6.1 的 0.5x
  Sol 6.1     50 / 2.5  / 250

速度模式倍率（相對同模型 Standard）
  Fast                     訂閱內含 2.5x ｜ credits 2x
  Sol 6.1 / Astra Ultrafast 訂閱內含 8x   ｜ credits 6x
```

## 3. 與既有筆記的整合

- 既有速查表只涵蓋 Sol 6.1／Astra 6／Luna 6，現已增補 Terra 與 Fast（第 9 節），其餘章節與查證日維持原樣。
- [`2026-10-26-llm-burn-rate-cache-routing-benchmark.md`](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md) 的實測不含 Terra，已在文首補上指向本筆記的註記，**沒有改動原實測數據**。
- [`2026-11-07-github-copilot-fusion-model-routing-cascade-critique.md`](./2026-11-07-github-copilot-fusion-model-routing-cascade-critique.md) 的留言提到 gpt-6.1-terra 在 Copilot 路由的角色；Copilot 計費與 Codex 額度是不同體系，不可互換。
- [`2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md`](./2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md) 說明 Work 與 Codex 共用額度，與官方頁首句「ChatGPT Work and Codex share usage」一致。
- 依 `T-20261026-02` 的先例（模型名、額度、價格不寫成永久偏好），Terra 數字不寫進共用偏好庫，改以附日期與出處的速查表收錄。

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261114-01`**｜**[優先級：高]** 將 GPT-6.1 Terra 額度、credits 單價與 Fast 倍率核實結果增補進模型速查表
  - **目標範圍**：`docs/model-burn-rate-routing-matrix.md`（只增補第 9 節與標題、來源標記；不改第 1～8 節的數據）
  - **具體做法**：
    1. 讀官方用量頁，逐項核對線索的五個說法並標註相符、粗估、措辭不精確、未驗證。
    2. 補 Terra 對 Sol 6.1 的 Plus 訊息數與 credits 對照，並標明推算方式與區間。
    3. 補 Fast 與 Ultrafast 倍率表，註明 2.5x 僅限訂閱內含額度。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 含「GPT-6.1 Terra 與 Fast 倍率」章節，內有逐項核對表、額度與 credits 對照、Fast 倍率表與未驗證清單；`python tools/verify_inbox.py` 通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：`docs/model-burn-rate-routing-matrix.md` 新增第 9 節（9.1–9.6，約 66 行）。數字取自 2026-11-14 讀取的官方頁：Terra 35–285 對 Sol 15–160、Terra credits 25/1.25/125 對 Sol 50/2.5/250、Fast 2.5x／2x。線索中「額度增加」依官方原文「Overall Work and Codex plan limits are unchanged」標為措辭不精確。

- [ ] **`T-20261114-02`**｜**[優先級：中]** 將「日常用 Terra、高難度用 Sol、不開 Fast」寫入 `SanHsien/agent-assets`（私有）共用偏好庫
  - **狀態**：⚪ 不做（不做：這是未附出處的使用者線索，且品質差異未驗證；模型名、額度、倍率屬會變動的資料，`T-20261026-02` 已確立不寫成永久偏好。數字改以附日期與出處的方式收錄在 T-20261114-01 的速查表第 9 節。）
  - **目標範圍**：`C:\GitHub\agent-assets\knowledge\user_preferences.md`（私有）
  - **具體做法**：
    1. 在模型調度段落補 Terra 與 Fast 的路由紀律。
  - **驗收標準（DoD）**：不執行。
  - **實作紀錄 / 證據**：*（不做，無實作）*

- [ ] **`T-20261114-03`**｜**[優先級：低]** 用本機用量儀表板實測 Terra 與 Sol 6.1 的實際耗額與任務品質，回填速查表第 9 節
  - **狀態**：🔴 未做（需要連續使用一段時間才有資料；不能靠讀文件完成）
  - **目標範圍**：`docs/model-burn-rate-routing-matrix.md`（只補第 9 節的實測欄位）
  - **具體做法**：
    1. 選 3 個同類型日常任務，分別用 Terra 與 Sol 6.1 的 Standard 模式完成，記錄開始與結束時儀表板的 5 小時額度百分比。
    2. 對輸出做同一份驗收（測試通過、人工審查），記錄品質差異。
    3. 同一任務各跑一次 Fast，確認 2.5x 是否與儀表板相符。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 第 9 節新增「本機實測」小節，含任務描述、各模式額度消耗與品質結論；沒有實測資料時不得填寫。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

## 5. 評估結論

**採用度高（數字可靠），可信度分層：**

- 官方可核實：可用介面、Plus 訊息數區間、credits 單價、Fast 倍率。
- 需修正措辭：整體方案額度沒有增加。
- 未驗證：Terra 日常夠用、Sol 才適合高難度的品質判斷；Terra 開 Fast 是否也是 2.5x（官方表為通則，未列例外，推算成立但未實測）。

操作層面，目前唯一有官方背書的省額做法是：能用 Terra 時別用 Sol（約省一半 credits、約多一倍訊息數）、非必要不開 Fast；是否因此犧牲品質，需靠 `T-20261114-03` 實測。
