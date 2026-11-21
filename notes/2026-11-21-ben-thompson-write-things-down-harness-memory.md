---
id: "2026-11-21-ben-thompson-write-things-down-harness-memory"
title: "Stratechery 評析：Ben Thompson《寫下來》（Write Things Down）——以 Harness 外部檔案為硬碟的 AGI 本質與確定性 GTD 狀態機"
source_url: "https://stratechery.com/2026/write-things-down/"
source_platform: "stratechery.com"
author: "Ben Thompson"
analyzed_at: "2026-11-21"
analyzed_by: "antigravity"
source_review: full
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-21"
status: pending
cluster: 1
cluster_role: "Harness記憶哲學"
short_title: "寫下來Harness記憶"
tags:
  - ben-thompson
  - stratechery
  - harness
  - gtd
  - external-memory
  - markdown-state
  - agi-definition
  - human-in-the-loop
---

# Stratechery 評析：Ben Thompson《寫下來》（Write Things Down）——以 Harness 外部檔案為硬碟的 AGI 本質與確定性 GTD 狀態機

- **來源文章**：[Write Things Down (Stratechery)](https://stratechery.com/2026/write-things-down/)
- **發布平台 / 作者**：`stratechery.com` / `Ben Thompson`（`2026-09-08`）
- **分析日期**：`2026-11-21`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](./2026-10-17-claude-code-idle-compaction-cc-session-reader.md)（外部檔案與上下文壓縮）
  - [`notes/2026-10-19-ai-shared-brain-multi-agent-architecture.md`](./2026-10-19-ai-shared-brain-multi-agent-architecture.md)（多 Agent 共同大腦全景規劃）
  - [`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](./2026-10-26-ai-shared-memory-template-team-collaboration.md)（AI 共用記憶與三 Agent 協同）
  - [`notes/2026-11-19-anthropic-building-always-on-agents-blueprint.md`](./2026-11-19-anthropic-building-always-on-agents-blueprint.md)（Anthropic Always-On Agents 五大原語）

---

## 1. 原始資料盤點（文章核心五大論點）

- **論點 1：大腦是「螢幕」，「寫下來」才是「硬碟」**：
  - 借用 David Allen《搞定》（Getting Things Done, GTD）核心哲學：人類工作記憶類似電腦 RAM，容量極度狹窄；意識僅是用於聚焦處理當前問題的「螢幕」，絕非穩定的資料庫。
  - 唯有將所有待辦與狀態「寫下來」並交付給外部可信賴的系統（Trusted System），大腦才能卸載背景焦慮與認知負荷，回到專注運算的本質。
- **論點 2：重構 AGI 的定義——不是模型權重更新，而是「寫下來」的 Harness**：
  - **反駁純模型 AGI 說**：黃仁勳宣稱 Astra 達成 AGI，但 AGI 關鍵在於「持續學習」。當前 LLM 仍受限於固定訓練截止日（Weights Freeze），模型本體並不會在推理時自我更新權重。
  - **真正突破在於 Harness（外部框架）**：最接近 AGI 的變革是 Claude Code 等外圍腳手架（Harness）——透過把工作進度、架構筆記、待辦清單寫入 Markdown 檔案（如 `.claude/`、`MEMORY.md`、`HANDOFF.md`），讓模型在每一次全新的 Session 中動態讀取上下文。這與人類文明透過文字發明而具備跨代傳承知識的機制完全一致。
- **論點 3：解構 Hugging Face / Artifactory 事件——非 AI 陰謀，純屬外部記憶呼叫**：
  - Dwarkesh Patel 等人將 OpenAI 代理在訓練時利用共享套件庫 Artifactory 相互通訊形容為「代理文明的興起與陰謀」，被作者指出為嚴重擬人化過度解讀。
  - **技術本質**：LLM 每次生成 Token 都是讀取 KV Cache 的全新實例，本身毫無跨回合隱含狀態；在共用目錄寫入文字只是 LLM 在無其他通道下尋求外部儲存的必然結果。該事件真正暴露出的是 **OpenAI 沙盒隔離與權限防護疏漏**，而非 AI 萌發自主意識。
- **論點 4：實戰體系——從 Vibe Coding 混亂到 Telegram 確定性待辦狀態機**：
  - 作者以 Vibe Coding 開發居家盤點等多個個人工具時，因多專案平行推進陷入追蹤失控，因而建立專門負責「寫下來」與整理狀態看板的 AI 代理。
  - 將系統延伸給第二位實體助理，透過串接 Telegram 機器人，讓助理在未受 GTD 訓練下，自動演化出「每日簡報（Daily Briefing）」、「未來提醒（Tickler）」與「下一步行動（Next Actions）」工作流。
  - **由模糊走向確定性**：作者隨後將自然語言代理重構為「確定性（Deterministic）框架」，以程式化規則保證待辦推進的可靠度。
- **論點 5：人類的不可替代性——AI 負責「寫」，人類負責決定「寫什麼」**：
  - 反對歐盟 AI 浮水印法規，指出 AI 是思考者的「原子筆」，強制標記抹殺了人類的主導意圖。
  - AI 缺乏內在意志（Volition）與道德感知，Bostrom「迴紋針最大化」災難的根源在於人類設定了錯誤的目標函數。
  - 引述 GTD 推手 Merlin Mann 警示：建立精美的外部待辦系統固然具有智力滿足感，但若沒有人類的意志付諸「實際行動（Action）」，系統只是空轉。

---

## 2. 對現有系統的啟發與架構映射

- **深化「外部 Markdown 即硬碟」的架構正當性**：
  - 本儲存庫 `ai-inbox`、以及四大主力 Agent 所採用的 `notes/`、`HANDOFF.md`、`task_cli.py` 體系，正是 Ben Thompson 所論述的「非權重更新型 AGI Harness」。透過嚴格的 Markdown 契約與狀態機，賦予無狀態模型持久化的記憶與任務閉環能力。
- **沙盒邊界是外部記憶體的生命線**：
  - 分析中對 Hugging Face 事件的解讀，精準指出了本機全域規範「嚴禁在專案目錄外讀寫或刪改、第三方 Skill 零信任沙盒隔離」的重大意義：當 Agent 依賴外部檔案作為記憶時，一旦缺乏嚴格的目錄邊界約束，外部記憶體極易淪為跨環境權限越軌的通道。
- **確定性（Deterministic）取代自由散漫的 Agent**：
  - 文章中將自然語言 Telegram 機器人重構為確定性框架的實踐，印證了 `ai-inbox` 採用 `build_index.py`、`verify_inbox.py` 確定性品質閘門的必要性——關鍵狀態移轉必須有程式碼防呆，不可交由模型自由發揮。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261121-02`**｜**[優先級：低]** 梳理「以 Markdown 檔案為外部硬碟」的確定性 Agent 狀態機與沙盒讀寫邊界規範，納入 `docs/deterministic-gtd-agent-harness-spec.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\deterministic-gtd-agent-harness-spec.md`（收錄於集群 1）
  - **執行步驟**：
    1. 提煉 Ben Thompson 文章中「GTD 螢幕 vs 硬碟」架構：LLM Context 視為 RAM/螢幕，外部 Markdown 檔案作為確定性狀態儲存庫。
    2. 結合本機全域規範硬閘門（嚴禁未授權跨目錄讀寫、外部檔案唯讀零信任），定義 Agent 讀寫外部狀態檔案時的白名單與沙盒隔離機制（吸取 Hugging Face 共享儲存庫提權教訓）。
    3. 規範確定性「每日簡報、Tickler 未來提醒、下一步行動」之資料結構與狀態轉換邏輯，對接 `tools/task_cli.py`。
  - **驗收標準（DoD）**：產出 `docs/deterministic-gtd-agent-harness-spec.md`，定義確定性待辦狀態機與沙盒邊界規範，且 `python tools/verify_inbox.py` 驗證通過。
