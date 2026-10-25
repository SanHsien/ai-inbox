---
id: 2026-10-24-felix-rieseberg-how-to-be-more-ambitious
title: "Felix Rieseberg〈How to be more ambitious〉解構：速度／高度／深度／廣度四維 AI 野心框架、深度四問與外部裁判原則，及對本地 Agent 工作流的落地"
source_url: "https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/"
source_platform: "Blog（社群轉貼：老軒筆記）"
author: "Felix Rieseberg (Anthropic)"
analyzed_at: 2026-10-24
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: 3
cluster_role: "Prompt 與工作流方法論"
short_title: "AI 野心四維框架與深度四問"
tags:
  - anthropic
  - prompt-engineering
  - ambition
  - verification
  - workflow
  - felix-rieseberg
---

# Felix Rieseberg〈How to be more ambitious〉解構：速度／高度／深度／廣度四維 AI 野心框架、深度四問與外部裁判原則，及對本地 Agent 工作流的落地

- **來源連結**：[原文：How to be more ambitious: A tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)（作者網站標示發布日 2026-10-13；本次由「老軒筆記」貼文轉述觸發分析，貼文未附原文連結，連結由我在作者網站首頁查得）
- **發布平台 / 作者**：作者個人網站 / `Felix Rieseberg`（Anthropic 工程經理，帶領 Claude.ai、Claude Code 桌面版團隊）
- **分析日期**：`2026-10-24`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md`](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md)（嚴格 TDD 與對抗式驗證）
  - [`notes/2026-10-23-claude-plugin-security-guidance.md`](./2026-10-23-claude-plugin-security-guidance.md)（外部機械閘門）

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：Felix Rieseberg；轉述者為「老軒筆記」。
- **What**：把「對 AI 的野心」拆成四個可練習的面向。

```text
 速度 Speed     同一件事做更快                  ← 多數人停在這
   │
 高度 Altitude  不交辦步驟，直接索要「結果」     ← 目標背後的目標
   │
 深度 Depth     用專家的「工具與原始材料」        ← 不是專家的口吻
   │
 廣度 Range     名詞換動詞，組「夢幻團隊」並行    ← 跨領域現在請得起
```

- **Why**：作者觀察到使用落差巨大；瓶頸往往不在模型能力，而在人敢不敢提出更大的要求。
- **How（可直接套用的技巧）**：
  - **高度**：例「修這個當機」→「讓我們的 App 保持不當機」。判斷訣竅：最後需要「開會討論」的事，就把高度拉高。
  - **深度**：不要叫 AI「扮演專家」（只換用語）；要求「使用專家實際的工具與方法」，並**找外部裁判**，不讓 AI 自己給自己打分。深度四問：①頂尖專家會多做什麼我沒要求的事；②從什麼最原始的材料開始；③用哪些具體方法與工具；④除了你我之外，什麼能客觀證明結果正確。
  - **廣度**：把任務名詞換成動詞，再問「各領域專家實際會『做』什麼」；同樣避免純角色扮演，要求做真正會做的動作（查證數字、找最脆弱假設）。
- **When & Where**：任何準備開會討論、或要交辦給 Agent 的中大型任務；開始下指令前先自問四個問題。

> [!NOTE]
> 貼文中的範例（QBR、客戶流失、載入 200 毫秒、外星人毀滅地球）出自轉述，我只查證了原文存在、日期與四個面向；逐字範例是否與原文一致，未逐段比對。

---

## 2. 技術規格與可執行細節

- 原文提供的深度元提示（meta-prompt）概念：先請模型回答深度四問，再讓它**重寫你的指令**，然後才執行。
- 驗證原則：外部裁判須是模型「能實際執行」的工具（測試、原始資料比對、獨立稽核程序），而非模型自評。
- 廣度提示範本（轉述）：「這個任務如果用動詞描述，是在『做』什麼？列出 5 個能帶來獨特視角的領域，說明每個領域的專家實際會做哪些分析，然後依序執行。」

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - 與全域硬閘門「回報完成前要真的執行過檢查並貼輸出」同一精神（外部裁判），本框架可補強「派工前如何寫出更高野心的任務」這一端。
  - 與 `verification-protocol`、`blind-review`、`ai-review` 互補：這些偏事後驗證，本框架偏事前指令設計。
  - 本 repo 的任務拆解也可套用：DoD 本身就是「外部裁判」。
- **落差與採納判斷**：
  - **值得採納**：把深度四問與動詞化做成可重用範本，並在一個真實任務上實測。
  - **需調整**：「設定不合理目標」這類做法在派工時要搭配 DoD 與停損，避免無限迭代。
  - **不採納**：不把「野心」寫成每次必跑的強制流程；小事（改錯字、查單一事實）不適用。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261024-01`**｜**[優先級：中]** 建立「AI 野心升級檢查表」範本（高度／深度四問／廣度動詞化），並用一個真實任務實測前後差異
  - **目標範圍**：`templates/ambition-prompt-checklist.md`
  - **具體做法**：
    1. 把四個面向整理成可勾選檢查表：目標背後的目標、深度四問、名詞換動詞與 5 領域提示、外部裁判。
    2. 從本 repo 的未做任務中挑一個，先寫原始指令，再套用檢查表改寫成高野心版本。
  - **驗收標準（DoD）**：產出 `templates/ambition-prompt-checklist.md`，含四個面向各至少 2 個勾選項與一段「改寫前／改寫後」對照（取自真實任務，註明任務編號）；以 `Select-String -Pattern '改寫前|改寫後'` 驗證兩者皆存在。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：已透過外部 Claude Session (agent-relay 20261024T155802447Z-1a658f) 建立 templates/ambition-prompt-checklist.md，涵蓋目標背後的目標、深度四問、廣度動詞化（含 5 領域視角）與外部裁判四大面向（共 19 個勾選項），並以 T-20261024-05 完成「改寫前／改寫後」對照實測。

- [x] **`T-20261024-02`**｜**[優先級：低]** 稽核現有任務與技能是否具備「外部裁判」，列出缺口
  - **目標範圍**：`docs/external-judge-audit.md`（只讀盤點 ai-inbox 內的 DoD，不修改任務）
  - **具體做法**：
    1. 抽查 ai-inbox 內 10 項未做任務的 DoD，標註其驗證是否來自自身以外的檢查（測試、腳本、外部工具）。
    2. 對只靠「文件存在」或自評的 DoD 列為缺口並建議補強方式。
  - **驗收標準（DoD）**：產出 `docs/external-judge-audit.md`，含 10 列表格（任務編號、驗證方式、是否外部裁判、建議）與缺口統計一行；表格列數以 `Select-String -Pattern '^\| T-'` 計數為 10。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：已建立 docs/external-judge-audit.md 盤點 10 項未做任務之 DoD 外部裁判狀態與補強建議，通過 Select-String 計數 10 列與 verify_inbox.py 驗證。

- [x] **`T-20261025-02`**｜**[優先級：高]** 依 `docs/external-judge-audit.md` 補強：實作合規清單、宣稱查證與對照矩陣之「外部裁判」結構驗證器
  - **目標範圍**：`tools/verify_compliance_and_matrix_docs.py` 與 `tests/test_verify_compliance_and_matrix_docs.py`
  - **具體做法**：
    1. 實作 `tools/verify_compliance_and_matrix_docs.py`（純 Python stdlib），取代單純的 `Select-String` 行數統計，機械化解析並驗證：(a) `docs/ai-persona-compliance-checklist.md` 五大類別各有 `>= 3` 個 `- [ ]` 勾選項，且所有 `https://` 官方連結語法有效、無重複；(b) `docs/ai-influencer-claims-check.md` 三項宣稱區塊皆明確標註法定結論（`官方證實` / `官方未提及` / `與官方矛盾`）並附官方來源連結；(c) `docs/feedback-desk-vs-agent-relay.md` 對照表至少 8 個維度列、每列欄位數一致且無空白格；(d) `templates/ambition-prompt-checklist.md` 四大面向勾選項與「改寫前／改寫後」實例完整。
    2. 撰寫 `tests/test_verify_compliance_and_matrix_docs.py`，涵蓋真實文件通過測試，以及缺漏分類、無效結論、空白表格單元格之反例攔截測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_compliance_and_matrix_docs.py` 回傳 exit 0，且 `python -m pytest tests/test_verify_compliance_and_matrix_docs.py -q` 全數通過（至少 6 項測試）。
  - **完成日期**：2026-10-25
  - **實作紀錄 / 證據**：已實作 `tools/verify_compliance_and_matrix_docs.py` 提供純 stdlib 結構驗證器，解析並驗證四大文件之五大分類、勾選項、URL 合法性、法定結論、對照矩陣完整性與改寫前後對照實例；建立 `tests/test_verify_compliance_and_matrix_docs.py` 共 9 項 pytest 測試（涵蓋真實文件檢驗與各類反例攔截），執行驗證器 exit 0 且 pytest 9 項測試全數綠燈通過。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **工程驗收與驗證**：
  - [SpaceX 前首席工程師 pstack 方法論與嚴格 TDD 驗證](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-17`、`T-20261018-18`
  - [Anthropic 官方 security-guidance 外掛解構](./2026-10-23-claude-plugin-security-guidance.md) ｜ 關聯任務：`T-20261023-01`、`T-20261023-02`
