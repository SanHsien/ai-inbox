---
id: 2026-10-28-multi-agent-team-dispatch-five-roads-going-li
title: "四 Agent 雲端與本機派工協定：Claude 拆單、Antigravity 審查、Hermes 通訊與 GOBOT 雲端值守架構解構"
source_url: "https://www.facebook.com/share/p/18BnwD3B6T/"
source_platform: "Facebook (Claude Taiwan)"
author: "Going Li (李國印)"
analyzed_at: 2026-10-28
analyzed_by: "Antigravity"
status: pending
cluster: 1
cluster_role: "開發流程"
short_title: "Going Li 四 Agent 派工與五路工具流"
tags:
  - multi-agent
  - team-dispatch
  - claudecode
  - antigravity
  - hermes-agent
  - grok-bot
  - output-oriented-pipeline
  - fallback-chains
---

# 四 Agent 雲端與本機派工協定：Claude 拆單、Antigravity 審查、Hermes 通訊與 GOBOT 雲端值守架構解構

- **來源連結**：[Facebook 社團分享 (Claude Taiwan)](https://www.facebook.com/share/p/18BnwD3B6T/)
- **核心作者**：李國印（Going Li，MUZI GOING'S AI LAB 負責人，專注於個人 AI 工作台多 Agent 協同架構與工具鏈整合）
- **分析主題**：從「串列接力」轉向「單一拆單 + 三棒同時派工」的多 Agent 協同拓撲、Mac 蓋上後由雲端 GOBOT（Grok Bot）接管 24 小時排程與爬蟲、Claude Code（拆單/編程）、Antigravity（架構審查/UI/UX）、Hermes（手機 Discord 入口/排程）四大隊員分工、人類「派」授權硬閘門、四態回報機制、以及按「我要做什麼產出」劃分的 20 個工具 5 條路徑與多層備援鏈架構
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md`](./2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md)（feedback-desk 跨 Agent 工單認領與交接協議）
  - [`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)（Thorsten Ball 15 條 Agent 實戰哲學：非同步排程喚醒與無可辯駁證據）
  - [`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md)（Karpathy 四大黃金原則工程加固：先定位再動手）
  - [`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](./2026-10-26-ai-shared-memory-template-team-collaboration.md)（AI 共用記憶系統三跳索引與動詞寫入契約）

---

## 1. 核心內容摘要：四 Agent 協同與派工拓撲全貌（Executive Summary）

在個人與獨立團隊推進 AI 工作流時，常面臨「單一 Agent 負擔過重」或「多 Agent 串列接力時溝通成本呈指數爆炸」的難題；同時，本機電腦（Mac/Windows）一旦休眠或闔上螢幕，所有排程與耗時爬蟲即刻中斷。

Going Li 提出了具備高度實戰價值的**「一棒接過，三棒同時派工」**架構，並納入雲端獨立隊員 GOBOT（Grok Bot），實現 24 小時不間斷運作：

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           Going Li 四 Agent 平行派工與沉澱架構拓撲                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  [ 人類負責人 (GOING) ] ──(輸入目標 / 要求)──┐                                                  │
│  - 定目標、提要求、貼 Token 與支付授權       │                                                  │
│  - 審核拆單清單，明確回覆「派」字才放行      │                                                  │
│                                              ▼                                                  │
│                                   [ 主控拆單：Claude Code ]                                     │
│                                   - 需求跨領域時先拆成幾塊                                      │
│                                   - 標明由誰做、一句理由                                        │
│                                   - 人類核可後「三棒同時派」                                    │
│                                              │                                                  │
│                     ┌────────────────────────┼────────────────────────┐                         │
│                     ▼                        ▼                        ▼                         │
│             [ 通道 A: 本機審查 ]      [ 通道 B: 行動通訊 ]      [ 通道 C: 雲端派工檔 ]          │
│               Antigravity                 Hermes                     GOBOT                      │
│             - 架構審查、UI/UX         - 手機 Discord 入口       - 跑在獨立雲端電腦              │
│             - 介面審核與安全架        - 定時排程通知推播         - GitHub 專用派工檔輪詢         │
│             - 寫入專用交接板          - 多層大腦容錯備援         - 24hr 爬蟲與名單整理          │
│             (下次開啟即可檢視)        (Gemini->GPT->Copilot)    (Mac 關機依然運行)              │
│                     │                        │                        │                         │
│                     └────────────────────────┼────────────────────────┘                         │
│                                              ▼                                                  │
│                                    [ 回報：四態 + 證據 ]                                        │
│                                    - 完成 / 完成但有疑慮                                        │
│                                    - 需要資料 / 卡住                                            │
│                                    - 事不出虛接、不盲寫                                         │
│                                              ▼                                                  │
│                               [ 沉澱：做完回回寫共用記憶庫 ]                                    │
│                               - HANDOFF.md + Obsidian 知識庫                                    │
│                               - Hook: sync-claude-experience.py                                 │
│                               - 下次任何隊員接手都不用重讀                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 深入技術拆解：三大核心實戰機制（Deep Dive）

### 2.1 機制一：派工單協定（Team-Dispatch Protocol）四步閉環
傳統多 Agent 協作常走「串列傳話筒」模式（A 傳給 B，B 傳給 C），極易產生上下文衰減與溝通內耗。Going Li 將其重構為四步驟原子派工流：

1. **STEP 01 拆單（先列表，不先動手）**：
   - 當需求跨越兩個以上隊員領域時，Claude Code 嚴禁直接實作。
   - 必須輸出結構化表格：`要做哪一塊` ｜ `由誰做` ｜ `怎麼派、怎麼回（理由）`。
   - **硬閘門（Hard Gate）**：人類輸入「派」字，指令才真正放行分發。
2. **STEP 02 三棒同時派（各走各的通道，絕無一棒傳四手）**：
   - `GOBOT`：寫入 GitHub 專用派工檔，雲端每小時自主拉取。
   - `Hermes`：命令列與 Discord 排程通道（`dispatch hermes --cron`）。
   - `Antigravity`：寫入專用交接板（`dispatch antigravity`），下次啟動自動承接。
   - `Claude Code`：保留給核心編程與本機工具鏈。
3. **STEP 03 回報（四態＋客觀證據）**：
   - 狀態標準化為四種：`完成`、`完成但有疑慮`、`需要資料`、`卡住`。
   - 恪守「事不出虛接、不盲寫」，必須附上執行結果證據；凡涉及對外推播或付款，一律暫停向人類確認。
4. **STEP 04 沉澱（做完回記憶庫，免重複探索）**：
   - 執行結果與踩坑教訓由 Hook（`sync-claude-experience.py`）自動同步至 `HANDOFF.md` 與 Obsidian。
   - 任何隊員後續接手時，先讀記憶庫即可接續工作，避免重蹈覆轍。

### 2.2 機制二：雲端 24 小時守護隊員（GOBOT）與最小權限架構
- **突破「闔蓋停擺」硬限制**：
  - 本地 Mac/Windows 筆電無法兼顧 24 小時排程與高耗時爬蟲。
  - 將 Grok Bot（GOBOT）部署於獨立雲端 VM，建構每小時定時巡檢 routine。
- **權限最小化（Least Privilege）安全設計**：
  - 雲端 Agent 不開放全域 GitHub 權限，只簽發單一限定 repo（專用派工檔）之 Token。
  - GOBOT 僅對該 repo 進行拉取任務、執行後回填「完成」狀態，其餘主專案代碼庫維持隔離。

### 2.3 機制三：以「產出（What）」為核心的五路工具流與容錯備援鏈（Tool Fallback Matrix）
不以「工具名稱」分類，而是以「我要做什麼」劃分 5 條專屬產出管線，且每個主力工具旁必備容錯替代方案：

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        20 個工具，5 條產出路徑與主力/備援矩陣                          │
├───────────────┬──────────────────────────────────┬─────────────────────────────────────┤
│ 產出路徑      │ 主力流水線 (Primary Route)       │ 容錯備援方案 (Fallback Route)       │
├───────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ ROAD 01 做影片 │ /url-to-video -> 分鏡 -> Fish   │ HeyGen 簡短生成 / Gemma 部署生成 /  │
│               │ 配音(雅婷) -> Hedra 數字人對嘴   │ 2Duber / Suno v3.5 翻唱配片         │
├───────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ ROAD 02 做圖像 │ 節慶小卡 -> Gemini 生四張 ->     │ Canva 模版 / Figma 排版匯出 /       │
│               │ LINE 回數字挑選 -> GAS 自動發送   │ 3D 派 Higgsfield                    │
├───────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ ROAD 03 做程式 │ Claude Code 主力編程 +           │ Vercel 部署 / Next.js 出型版 /      │
│               │ Antigravity 審架構 + UI/UX 規範   │ 大工程走 prd-with-docs 部署         │
├───────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ ROAD 04 整理文 │ 逐字稿丟 Obsidian -> Claude 提煉 │ Whisper 本機跑 (敏感/長錄音) /      │
│               │ 產出 docx/pptx 轉 PDF 交付       │ Notion 頁面 / Gemma 降階整理        │
├───────────────┼──────────────────────────────────┼─────────────────────────────────────┤
│ ROAD 05 調度員 │ 手機 Discord -> Hermes (Gemini) │ 備援鏈：Gemini 斷線換 ChatGPT(GPT-6)│
│               │ Claude Code 拆單 -> 我說「派」   │ 再掛換 Copilot；Mac 關機給 GOBOT    │
└───────────────┴──────────────────────────────────┴─────────────────────────────────────┘
```

#### 踩坑經驗與教訓防禦（Lessons Learned）
1. **備援鍵配置錯誤導致靜默失效**：
   - Hermes 原先的備援模型鍵名設定錯誤，導致主模型掛掉時從未真正切換至備援，系統直接噴錯。**工具必須有自我檢驗（Healthcheck/Dry-run）機制**，而非等出事才發現。
2. **Gateway 白名單誤用 Username**：
   - 認證與白名單過濾必須綁定不可變之唯一 ID（User ID），若綁定使用者名稱（Username），容易因改名或格式變更導致 Gateway 全面失聯。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`agent-assets` / `ai-inbox` / Antigravity）的融合**：
  1. **落實「Team-Dispatch」拆單協議**：
     - 將「先拆單、不先動手、標明責任、人類說『派』才執行」的硬閘門寫入全域協同規範與提示詞模板。
  2. **完善工具鏈備援檢驗機制**：
     - 借鑑備援鍵設錯的教訓，撰寫驗證器檢查工具流設定檔與備援模型健全度。
  3. **四大 Agent 專屬通道規範加固**：
     - 現有全域規範已規定 Antigravity、Claude、Codex、Hermes 的頂層派工與回報通道，進一步結合 Going Li 的 GitHub 派工檔與交接板機制，形成完整的雲端＋本機多端閉環。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261028-10`**｜**[優先級：高]** 撰寫「四 Agent 平行派工協議與人類審核門檻規範」收錄於 `docs/multi-agent-parallel-dispatch-spec.md`
  - **目標範圍**：`docs/multi-agent-parallel-dispatch-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 定義 Claude Code（拆單主控）、Antigravity（審查/UI）、Hermes（通訊/排程）、GOBOT（雲端輪詢）職責劃分表。
    2. 制定「先列表、不先動手」的拆單四欄契約與人類回覆「派」之強制硬閘門。
    3. 規範四態回報（完成、有疑慮、缺資料、卡住）與客觀證據格式。
    4. 納入 GitHub 專用派工檔之最小權限安全設定指引。
  - **驗收標準（DoD）**：產出 `docs/multi-agent-parallel-dispatch-spec.md`，內含角色矩陣、拆單流程圖、回報狀態契約與最小權限規範；以 `Test-Path docs/multi-agent-parallel-dispatch-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261028-11`**｜**[優先級：中]** 實作「產出導向工具流矩陣與備援鏈設定驗證器」於 `tools/verify_tool_fallback_matrix.py`
  - **目標範圍**：`tools/verify_tool_fallback_matrix.py` 與 `tests/test_verify_tool_fallback_matrix.py`
  - **具體做法**：
    1. 實作設定檔檢驗工具，驗證五大產出路徑是否均具備主力與合格的備援工具定義。
    2. 檢查規則：防範備援鍵名設定錯誤（避免靜默失效）、禁止白名單使用非唯一 Username、確保外發與付款步驟具備人類確認旗標。
    3. 撰寫單元測試覆蓋有效與無效配置檢驗。
  - **驗收標準（DoD）**：產出 `tools/verify_tool_fallback_matrix.py` 與單元測試，執行 `python -m unittest discover -s tests` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261028-12`**｜**[優先級：低]** 產出標準化「多 Agent 拆單派工 Skill 範本（Team-Dispatch）」收錄於 `templates/team-dispatch-skill-template.md`
  - **目標範圍**：`templates/team-dispatch-skill-template.md`
  - **具體做法**：
    1. 產出可直接供 Claude Code 或 Antigravity 引入的 `SKILL.md` 範本。
    2. 包含跨隊員任務拆解 Prompt、等待「派」指令之暫停邏輯、通道分派指令範例。
    3. 整合執行完畢自動調用 Hook 同步至 `HANDOFF.md` 的範例代碼。
  - **驗收標準（DoD）**：產出 `templates/team-dispatch-skill-template.md`，包含標準 YAML frontmatter 與完整指令流程；以 `Test-Path templates/team-dispatch-skill-template.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 協調與交接機制**：
  - [feedback-desk 開源 Agent 工單系統](./2026-10-28-feedback-desk-ai-agent-client-ticketing-handoff.md) ｜ 關聯任務：`T-20261028-07`、`T-20261028-08`
  - [Thorsten Ball 15 條 Agent 實戰哲學](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md) ｜ 關聯任務：`T-20261028-04`、`T-20261028-05`
- **規範工程與黃金原則**：
  - [Karpathy 版 CLAUDE.md 四大黃金原則工程加固](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md) ｜ 關聯任務：`T-20261028-01`、`T-20261028-02`
- **共用記憶與跨端沉澱**：
  - [AI 共用記憶系統全景分析](./2026-10-26-ai-shared-memory-template-team-collaboration.md) ｜ 關聯任務：`T-20261026-23`、`T-20261026-24`
