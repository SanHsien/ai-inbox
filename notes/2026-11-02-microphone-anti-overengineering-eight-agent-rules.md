---
id: 2026-11-02-microphone-anti-overengineering-eight-agent-rules
title: "「麥克風的市場求生手冊」給 Agent 的 8 條極簡治病規約：終結 Codex 過度設計、無休止審查與規則通膨"
source_url: "https://www.facebook.com/100044633940228/posts/1648280996669683/"
source_platform: "Facebook (麥克風的市場求生手冊)"
author: "麥克風的市場求生手冊 (@mktsurvivalkit)"
analyzed_at: 2026-11-02
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "工程紀律與設計審查"
short_title: "麥克風給Agent的8條防過度設計規約"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 0
source_replies: 7
tags:
  - agent-rules
  - anti-overengineering
  - codex
  - claude-code
  - software-engineering
  - prompt-engineering
  - human-in-the-loop
  - kiss-principle
---

# 「麥克風的市場求生手冊」給 Agent 的 8 條極簡治病規約：終結 Codex 過度設計、無休止審查與規則通膨

- **來源連結**：[Facebook 貼文：麥克風的市場求生手冊](https://www.facebook.com/100044633940228/posts/1648280996669683/) ｜ [分享短網址](https://www.facebook.com/share/1ExNpch5ia/)
- **核心作者**：麥克風（知名投資與工程觀察粉專「麥克風的市場求生手冊」）
- **發布時間**：2026-10-31
- **歸屬集群**：集群 1：Agent 開發方法論與工程實踐（角色：`Agent防過度設計與輕量工作規約`）
- **當前狀態**：`🟢 已結案 (Resolved)`
- **相關交叉參照**：
  - [`notes/2026-11-02-google-elephant-goldfish-model-software-design-review.md`](./2026-11-02-google-elephant-goldfish-model-software-design-review.md)（Google EGM 模型軟體架構審查與過度封裝反思）
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（多代理調度與網關路由治理）
  - [`notes/2026-11-01-claude-code-four-role-dispatch-runtime-rules.md`](./2026-11-01-claude-code-four-role-dispatch-runtime-rules.md)（Claude Code 四角色派工與執行時期規範）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（四 Agent 平行派工與五路工具流整合）

---

## 0. 原始資料盤點

> 2026-11-16 重審：未登入瀏覽器讀貼文全文與可見的 6 則留言（頁面顯示共 7 則，Facebook 註明「最相關」排序可能過濾掉部分留言，其餘要登入才看得到）。

> 2026-11-17 登入補讀：登入後把留言排序改成「所有留言」，7 則全部讀完（沒有回覆串可展開）。補到的是 `Edward Lee` 那一則。

- **作者圖片**：無。貼文是純文字。
- **作者留言補充**：作者只有一則置頂留言，內容與本文主題無關（個人爭議與粉專訂閱連結），沒有補充規則原文、Prompt 或勘誤。
- **網友留言重點**：
  - `AI Hot Shorts`：反對「拜託模型照規則做」，主張每個步驟、每個條件都用程式強制驗證，不合格就自動退回重做——只允許照要求做，而不是請它照要求做。
  - `林晉賢`：建議改用 hooks 落實，並貼了一段示意設定與一支擋高風險指令的 shell 腳本（對應規則 1、2、5、7、8）。那段設定的欄位是示意寫法，不是 Claude Code 實際的 hooks 格式，不能直接套用；但方向（規則 5 的高風險動作用 PreToolUse 擋、規則 7 用連續失敗次數偵測）是具體可做的。
  - `Edward Lee`（2026-11-17 補讀）：受夠了端對端測試的假驗證，認為直接跑、壞了就是壞了；自己最近改成多寫確定性的短腳本來約束模型，理由是「用法規管比用教學管有用」。另外猜測 OpenAI 的模型是刻意中斷迴圈來省運算資源，所以要人一直催才會繼續，並認為 Claude 比較穩；這段是個人猜測，沒有佐證。
  - `Shihyen Chen`：自己的分工是 Claude 寫程式比較乾淨，較強的模型才拿去和 Codex 討論開發計畫。`Chen John Lin`：直接用 Claude Code 比較省事。
- **對分析的影響**：
  - **原文主張的對象更正**：貼文原話是受不了 **Codex** 的過度設計，所以叫 **Claude** 寫了這 8 條。第 1 節原寫成作者對「Codex 及 Claude Code」都難以忍受，與原文不符，已改。
  - **8 條是白話轉述，不是規則原文**：貼文開頭就說「白話說就是」，Claude 實際寫出的規則全文沒有公開。第 2 節的「病灶」名稱（Mock Theatre、Rube Goldberg 等）、「貝佐斯決策模型」「Rule of Three」「調試成本暴增 10 倍」都是分析者的延伸，不是作者說的；已在第 2 節開頭加註。
  - **留言指出的缺口**：三則留言（`AI Hot Shorts`、`林晉賢`，加上 2026-11-17 補讀到的 `Edward Lee`）都說這類規則光寫在提示詞裡不夠，要用 hooks、腳本或程式強制。補讀沒有帶來新的做法，下面的判斷不變。本 repo 的落地（`T-20261102-11` 的靜態稽核腳本）只涵蓋規則 2 與規則 6 的行數檢查；規則 5（高風險動作）在維護者環境已有 PreToolUse hook 攔截，規則 3、7 目前仍只靠提示詞。已補進第 3 節。不另開任務：規則 7 的「同一原因卡兩次」難以用程式可靠判定，硬做會變成又一個關鍵字型檢查器。
  - 已完成任務的三個產出檔重審後沒有發現與原文衝突的事實錯誤。

---

## 1. 來源摘要與核心論述

台灣知名科技與投資觀察者「麥克風」在 2026 年 10 月底於 Facebook 發文指出：受不了 **Codex 的過度設計毛病**（2026-11-16 更正：原文只點名 Codex，Claude 是幫忙寫規則的一方；「官僚化傾向」是分析者的用詞）。

作者請 Claude 寫了給 agent 的 **8 條規則**，貼文公開的是這 8 條的白話轉述（規則原文沒有貼出）：

```text
+-----------------------------------------------------------------------------------------+
|                  「麥克風」給 AI Coding Agent 的 8 條極簡治病規約                      |
+-----------------------------------------------------------------------------------------+
| 1. 先真的跑通一次，假環境的測試不算數。                                                 |
| 2. 先做最簡單的版本，預計超過 300 行要先說明理由。                                      |
| 3. 審查最多兩輪，之後只擋「跑不完」或「會壞資料」的問題。                               |
| 4. 偶爾重複、偶爾要人補救都可以接受，不追求完美。                                       |
| 5. 改了能復原的事不用審批，只有刪資料、動錢、對外發布、改權限才要。                     |
| 6. 想加新規則或新關卡要你同意，還要說明能不能順便刪掉一條舊的。                         |
| 7. 同一個原因卡兩次就停下來，用三句白話問你，不要再加機制繞過去。                       |
| 8. 回報只講做了什麼、你怎麼親眼看到結果、下一步是什麼，不貼 hash 和術語。              |
+-----------------------------------------------------------------------------------------+
```

---

## 2. 深入解構：8 條規約對應的 AI 編程致命病灶

> **2026-11-16 重審註記**：本節的病灶名稱、類比（貝佐斯雙向門、Rule of Three）與「調試成本暴增 10 倍」等說法是分析者的延伸，原貼文只有上面那 8 句話。

這 8 條白話規約之所以具備極高實用價值，在於它們精確擊中了目前 AI Coding Agent 最常見的 8 大工程反模式：

```
+----------------------------------------------------------------------------------------+
|                                  AI 編程八大病灶 vs 八條規約                           |
+----------------------------------------------------------------------------------------+
|  常見病灶 (AI Anti-Pattern)               |  麥克風規約 (Lean Prescription)            |
+------------------------------------------+---------------------------------------------+
|  1. Mock 狂魔與假綠燈 (Mock Theatre)      |  -> 1. 必須在真實環境跑通，假環境測試不算   |
|  2. 抽象層爆炸 (Premature Abstraction)   |  -> 2. 預設 300 行上限，超過先說明理由     |
|  3. 審查無休止迴圈 (Review Doom Loop)     |  -> 3. 審查最多兩輪，之後只擋致命問題       |
|  4. 完美主義強迫症 (Paralysis by Analysis)|  -> 4. 容忍適度重複與人工作業，不追求完美   |
|  5. 芝麻綠豆事事請示 (Excessive Check-in) |  -> 5. 可逆變更自行推進，不可逆高危才審批   |
|  6. 規則不斷堆疊通膨 (Rule Inflation)     |  -> 6. 新增一條規則必須評估能否刪除舊規則   |
|  7. 幽靈繞路發明 Hack (The Rube Goldberg) |  -> 7. 卡兩次即停下，三句白話求助人類       |
|  8. 八股文公文腔報喜 (Bureaucratic Slop)  |  -> 8. 回報三要素：做什麼、如何驗、下一步   |
+----------------------------------------------------------------------------------------+
```

### 2.1 規則 1：破除假綠燈（Mock Theatre）
- **病灶**：AI 特別喜歡在單元測試中使用大量的 Mock、Fake、Monkey-patch，甚至自我催眠。表面上所有測試都是綠燈，但一上真實環境就因真實網路、權限、檔案路徑或二進位依賴而崩潰。
- **解法**：嚴禁「假環境過關就宣稱修好」；改完必須在真實目標平台（如 Windows 11 原生）上跑真實進程，以標準輸出與 exit code 為唯一真理。

### 2.2 規則 2：300 行預算制（Line Budget）
- **病灶**：要求一個小功能，Codex 往往自作主張設計 AbstractFactory、Dependency Injection Container、Strategy Provider、Observer 模式，寫出幾千行厚重代碼。
- **解法**：KISS（Keep It Simple, Stupid）原則具象化為「300 行紅線」。超過預算必須主動向人類解釋為何需要這等規模，抑制模型盲目的代碼膨脹。

### 2.3 規則 3：終結無休止審查迴圈（Review Cap）
- **病灶**：引入 Multi-agent review、ai-review 或子代理審查時，代理人之間容易陷入無限 nitpick（挑剔命名風骨、假設極端冷門邊界），導致 PR 停滯不前。
- **解法**：硬性限制最多 2 輪審查。第 3 輪起只擋「無法終止（死循環/掛起）」或「破壞資料/安全漏洞」，其餘品味問題一律放行。

### 2.4 規則 4：拒絕過早 DRY（Accepting Duplication）
- **病灶**：模型極度排斥任何微小重複，為了消除 3 行相似代碼，強行抽象出複雜的高階泛型或動態分發，結果讓調試成本暴增 10 倍。
- **解法**：接納適度重複（Rule of Three），承認初期手動補救比維護龐大脆弱的抽象更有工程彈性。

### 2.5 規則 5：貝佐斯決策模型（Two-Way Door Autonomy）
- **病灶**：Agent 在本地修改程式碼時，動輒中斷並輸出長篇大論向使用者詢問「請問我是否可以修改 X.py 第 12 行？」，嚴重破壞心流。
- **解法**：區分「可逆決策（雙向門）」與「不可逆決策（單向門）」。本地 Git 改動隨時能 `git checkout`，Agent 擁有完全自治權；唯有涉及刪除正式資料、扣款動錢、對外公開發布、修改系統權限等單向門時，才停下徵詢人類授權。

### 2.6 規則 6：規則淨零增長法（Rule Sunset / Zero-Growth）
- **病灶**：開發者每次踩坑就往 `CLAUDE.md`、`AGENTS.md` 或全域 Prompt 加一條規則。幾個月後規則庫膨脹至數千行，模型被互相矛盾的規則綁手綁腳，Token 成本爆表。
- **解法**：**「想加一條新規則，必須先嘗試刪掉一條舊規則」**。強制規則庫保持精簡，避免規約通膨窒息系統。

### 2.7 規則 7：兩次撞牆即停（Fail Fast, Talk Plain）
- **病灶**：當指令報錯或權限被拒，Agent 經常自行發明複雜的臨時腳本、Wrapper 或沙盒繞過，越陷越深，製造難以挽回的破壞。
- **解法**：同一個原因連續卡住 2 次，嚴禁自行疊加第三層機制，強制停下來以三句白話向人類求助。

### 2.8 規則 8：三段式清爽回報（Lean Reporting）
- **病灶**：結案時輸出充滿長篇 Git SHA、AST 符號、技術縮寫或虛假架構宣稱。
- **解法**：回報只回答三件事：
  1. **做了什麼**（What was done）
  2. **你如何親眼驗證**（How to verify visually / functionally）
  3. **下一步是什麼**（What's next）

---

## 3. 對現有系統的啟發與改造方案

| 現有系統實踐 | 麥克風 8 條規約之借鑑 | 改造落地動作 |
| :--- | :--- | :--- |
| **測試檢查門檻** | 與「非 mock 真實驗證」完全吻合 | 強化在 `RULE[user_global]` 與 `verify_inbox.py` 的真實驗證要求 |
| **代碼規模管控** | 缺乏對單次重構或任務的代碼行數紅線 | 引入「單次實作 300 行預算規範」，建立超額說明機制 |
| **多代理 Review 治理** | `blind-review` 與 `ai-review` 有時審查輪次過長 | 設定硬性「2 輪審查上限」，第 2 輪後只攔截安全與死鎖 |
| **Prompt 規則維護** | 規則檔案容易只增不減 | 實施「規則淨增長審查」，評估每次新增規則時是否可整併舊規則 |
| **收尾總結格式** | 有時仍包含過多內部雜訊 | 標準化為「做了什麼、如何親自驗證、下一步」三段式簡報 |
| **強制手段（留言補充）** | 留言 `AI Hot Shorts`、`林晉賢` 指出規則寫在提示詞裡不夠，要用 hooks 或程式強制 | 規則 2、6 已有靜態稽核腳本；規則 5 已由 PreToolUse hook 攔截；規則 3、7 仍只靠提示詞，暫不做（難以用程式可靠判定） |

---

## 4. 具體待辦任務與落地拆解（Action Items）

為將麥克風提煉的「給 Agent 的 8 條極簡治病規約」落實為知識庫與全系統工程防線，規劃以下 3 項任務：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261102-10`**｜**[優先級：高]** 撰寫「AI Coding Agent 防過度設計與防官僚化精實工程手冊（8 條白話規約與反模式清單）」收錄於 `docs/anti-overengineering-agent-rules-spec.md`
  - **目標範圍**：`docs/anti-overengineering-agent-rules-spec.md`（規範手冊；不修改現有業務程式碼）
  - **具體做法**：
    1. 系統性收錄麥克風 8 條白話規約，逐條對應傳統軟體工程反模式（Premature Optimization、Mock Theatre、Rule Bloat、Doom Loop）。
    2. 提供「300 行預算制」、「兩輪審查熔斷機制」與「單向門 vs 雙向門操作矩陣」之具體判定流程。
    3. 制定精實回報模板（做什麼、如何驗、下一步），規範跨 Agent 輸出風格。
  - **驗收標準（DoD）**：產出 `docs/anti-overengineering-agent-rules-spec.md`，具備完整繁體中文結構；以 `Test-Path docs/anti-overengineering-agent-rules-spec.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：已完成規格手冊撰寫，詳述 8 大反模式、300 行預算守衛、兩輪審查熔斷機制與單雙向門矩陣；以 `Test-Path` 驗證為 True。

- [x] **`T-20261102-11`**｜**[優先級：中]** 實作「Agent 單次改動規模與規則通膨靜態稽核腳本」於 `tools/verify_agent_lean_rules.py` 與單元測試
  - **目標範圍**：`tools/verify_agent_lean_rules.py`、`tests/test_verify_agent_lean_rules.py`
  - **具體做法**：
    1. 實作純 Python 稽核工具 `tools/verify_agent_lean_rules.py`，支援掃描 Git diff 或檔案變更行數，當單次變更超過 300 行且未包含宣告說明時發出提醒。
    2. 檢查規則檔案（如 `AGENTS.md`、`CLAUDE.md`）之行數與規則條目通膨率，落實規則精簡方針。
    3. 撰寫單元測試套件 `tests/test_verify_agent_lean_rules.py`，驗證行數門檻判斷、說明匹配邏輯與無違規放行機制。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_agent_lean_rules.py` 綠燈通過。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：已完成 `tools/verify_agent_lean_rules.py` 與單元測試 `tests/test_verify_agent_lean_rules.py`，測試覆蓋正常變更、300 行超額豁免宣告、未宣告攔截與規則檔案長度審查，單元測試全數綠燈通過。

- [x] **`T-20261102-12`**｜**[優先級：低]** 產出即插即用的「8 條輕量治病 Agent 系統提示詞模組（適用 CLAUDE.md / AGENTS.md / GEMINI.md）」收錄於 `templates/anti-overengineering-agent-prompt.md`
  - **目標範圍**：`templates/anti-overengineering-agent-prompt.md`
  - **具體做法**：
    1. 將 8 條規約改寫為可直接複製貼入任何專案根目錄 `CLAUDE.md`、`AGENTS.md` 或 `GEMINI.md` 的極簡 Prompt 片段（小於 500 字，節省 Token）。
    2. 包含白話中文版與標準英文對照版，適配多語言 Agent 環境。
    3. 附帶反模式微型問答，供 Agent 開工前自檢。
  - **驗收標準（DoD）**：產出 `templates/anti-overengineering-agent-prompt.md`；以 `Test-Path templates/anti-overengineering-agent-prompt.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：已產出雙語精實 Prompt 模板於 `templates/anti-overengineering-agent-prompt.md`，字數控制在極簡 Token 預算內，以 `Test-Path` 驗證為 True。
