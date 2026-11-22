---
id: "2026-11-21-infoq-gemini4-neon-antigravity-swe-sweep-harness-eval"
title: "InfoQ 評析：Gemini 4 Neon 接入 Antigravity 後 SWE-sweep 子任務加權分數升至三倍與 Harness 聯合訓練"
source_url: "https://www.infoq.cn/article/tDxNggErsJNeb53ZkYeF"
source_platform: "infoq.cn"
author: "Tina"
analyzed_at: "2026-11-21"
analyzed_by: "antigravity"
written_by: "legacy/unknown@pre-review; claude/opus-5.5@e7344aab-d6b6-4fcb-961e-1304a5af6031"
revised_at: "2026-11-22"
source_review: full
source_images: 10
source_replies: 0
source_reviewed_at: "2026-11-21"
status: archived
cluster: 1
cluster_role: "Neon+AGY效應"
short_title: "Neon接入AGY三倍"
tags:
  - gemini-4-neon
  - antigravity
  - swe-sweep
  - harness-coupling
  - artificial-analysis
  - model-routing
  - quota-reset
---

# InfoQ 評析：Gemini 4 Neon 接入 Antigravity 後 SWE-sweep 子任務加權分數升至三倍與 Harness 聯合訓練

- **來源文章**：["美国大豆包"又发新模型，Neon 接入 Antigravity 后编程解题率升至三倍多（InfoQ）](https://www.infoq.cn/article/tDxNggErsJNeb53ZkYeF)
- **發布平台 / 作者**：`infoq.cn` / `Tina`（`2026-11-20`）
- **分析日期**：`2026-11-21`
- **當前狀態**：`📦 已歸檔 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`](./2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md)（Gemini 4 Neon 實測基準與 AGY 12 項配置）
  - [`notes/2026-11-18-gemini-4-carbon-argon-swarm-evals.md`](./2026-11-18-gemini-4-carbon-argon-swarm-evals.md)（Gemini 4 Carbon / Argon 與 `/swarm`）
  - [`notes/2026-11-20-gemini-decision-1-decisions-api-eval.md`](./2026-11-20-gemini-decision-1-decisions-api-eval.md)（Gemini Decision 1 路由模型）
  - [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md)（多模型選型速查表）

---

## 1. 原始資料盤點（正文、10 張圖片與評論區）

- **Neon 定位與速度優勢**：
  - 2026-11-18 發布，為 Google DeepMind 七週內的第四款 Gemini 4 模型（Argon → Carbon → Hydrogen → Neon）。
  - **high 檔 Artificial Analysis 智能指數 60 分**（與 Carbon high 並列），但單任務成本 **$3.74**（Carbon 標準價 $7.76，Neon 低 52%）；xhigh 檔升至 $6.44，仍比 Carbon 標準價低 17%。
  - 生成速度約 **110 tokens/s**（Carbon 約 57 tokens/s，接近兩倍；Artificial Analysis 原文未註明這組速度的推理檔位）。
  - **token 與耗時比較是 Neon xhigh 對 Carbon high**（不是上面的 high 對 high）：Neon xhigh 每題多用約 15% 輸出 token，但每題約 21 分鐘，比 Carbon high 的約 36 分鐘少約四成。
  - 註：Artificial Analysis 原文對 high 檔只寫「與 Carbon high 同分、每題成本不到 Carbon 標準價的一半」，沒有列出 `$3.74`；`$3.74`／低 52% 是 InfoQ 的數字，未在 Artificial Analysis 原文找到。
  - API 定價：輸入 $3 / 輸出 $15（每 1M tokens）；Carbon / Argon 首發優惠至 11/30 為 $2/$10，12/1 漲至 $4/$20。

- **SWE-sweep Harness 配對比較（Google 自行計算）**：
  - Google 以 mini-swe-agent 與各家官方 Agent Harness 分別測試三款模型。依 [Google 評測方法](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_neon_model_evaluation.pdf)，數字是**子任務加權分數（subtask-weighted reward）**，不是「完整任務解決比例」；provider harness 分別是 Antigravity-CLI 1.5.9、Claude Code、Codex（Codex 與 Claude Code 版本未註明）。數字與 [Google 模型卡](https://deepmind.google/models/model-cards/gemini-4-neon/) 一致：

  ```text
  模型                mini-SWE   自家 Agent Harness   倍率   （子任務加權分數）
  ─────────────────────────────────────────────────────────
  Neon + AGY           12.8%  →  39.0%  (Antigravity)   3.0×
  Claude Opus 5.5 + CC  3.6%  →  10.1%  (Claude Code)   2.8×
  GPT-6.2 Sol + Codex  11.6%  →   8.3%  (Codex)         0.7×
  ```

  - **Antigravity Harness 與 Gemini 經過聯合訓練**（[Antigravity 官方文件](https://antigravity.google/docs/overview?tab=ide) 寫明 harness 與 Gemini 模型 co-trained，但沒有量化效果），Neon 針對長程程式 Session 優化了不必要的檔案讀取並改善上下文管理；AGY 並行調度多個 Hydrogen 子代理在各自 Git worktree 中工作並驗證合併。Google 評測方法也註明 Antigravity-CLI 預設有可分派子代理掃描整個程式庫的工具，特別適合 SWE-sweep 這類找 bug 任務——也就是這組比較同時改變了框架與工具能力。
  - **GPT-6.2 Sol 接入 Codex 反而下降**（11.6% → 8.3%），為三組中唯一負向的 Harness 耦合效果。

- **知識工作與視覺推理進步**：
  - **GDP.pdf**：Neon high 33.4%（Carbon high 28.4%，高出 5 個百分點，與該評測最高成績相當）。
  - **AA-Briefcase**：Neon xhigh 1700 Elo（Carbon 1611），仍低於 Claude Fable 5.2 (1785) 和 Sonnet 5.5 (1815)；演示文稿分項升至 1771（新紀錄，超越 Sonnet 5.5 的 1726）。
  - **MKA（多模態知識 Agent）**：Neon Climb WSR 56%（Carbon 54%，落後 Fable 5.2 的 57% 僅 1 個百分點）。

- **Antigravity 一週年與額度重置**（InfoQ 轉述，未取得一手來源，待查證）：
  - Varun Mohan 宣布重置所有用戶在全部模型（包含 Claude、GPT-OSS 等第三方）的使用額度。
  - 額度機制：免費版每週刷新，Pro/Ultra 每五小時刷新一次，受每週上限約束。
  - 文章補充 Antigravity 歷史背景：Mohan 與 Douglas Chen 共同創辦 Windsurf → 2025.07 被 Google 招入 DeepMind 並取得非獨家授權 → 四個月後推出 Antigravity。

- **圖片與評論區**：
  - 共 10 張圖片（含封面圖、Artificial Analysis 智能指數對比圖、SWE-sweep 配對實驗圖、GDP.pdf 對比圖、AA-Briefcase Elo 圖、速度 token 圖、定價表等）。
  - 評論區：`0` 則留言。

---

## 2. 對現有系統的啟發與架構映射

- **Harness 選擇是選型盲區**：這組配置顯示，框架選擇可能大幅影響成績。Sol 在 mini-SWE 為 11.6%，接入 Codex 反而是 8.3%——**「榜單上的裸分」和「接入工具鏈後的分數」可以反向**。但這只是 Google 自行計算的一組比較，不能據此斷定框架影響一般而言大於模型差距。這是本機路由決策的警示。
- **AGY 聯合訓練的貢獻尚未量化**：官方確認聯合訓練存在，但公開比較同時改變了框架與工具（含子代理工具），沒有拆分聯合訓練效果的消融實驗，所以 39% 有多少來自聯合訓練仍未知。文章也指出「各項優化分別貢獻了多少，以及換到其他代碼倉庫後能否複現，還有待驗證」。在本機評估中不可將此 39% 直接類推至非 AGY 環境。
- **與既有筆記交叉參照**：本篇（InfoQ 評析）轉述 Google 自行計算的評測與 Artificial Analysis 的評測；`2026-11-20-antigravity-gemini4-neon-12-prompts-eval.md`（Woshipm 饼干哥哥文章筆記）整理社群文章與實測轉述（CursorBench、JAZII）。Google 的比較是廠商自行計算，沒有隔離其他變因，不宜稱為控制實驗。兩份合併後構成較完整的 Neon 能力剖面。

---

## 3. 拆解出的待辦任務 (Action Items)

本篇新增數據（SWE-sweep 配對、GDP.pdf、AA-Briefcase Elo、定價時間表）可直接併入既有任務 `T-20261120-03`（將 Neon / Hydrogen / Sol 基準補入路由矩陣）處理，無需另開獨立任務。歸檔不另拆。
