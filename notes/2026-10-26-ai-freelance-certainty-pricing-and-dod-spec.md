---
id: 2026-10-26-ai-freelance-certainty-pricing-and-dod-spec
title: "AI 接案的確定性交付工程：需求解壓縮、價值報價法、外部裁判 DoD 與 Session 工具鏈降維打擊"
source_url: "https://youtu.be/6M0TBCIyzR4"
source_platform: "YouTube (Debug 土撥鼠)"
author: "Debug 土撥鼠"
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: done
cluster: 1
cluster_role: "接案與商業化"
short_title: "AI 接案確定性與價值報價工程"
tags:
  - ai-freelance
  - value-based-pricing
  - scope-management
  - dod-verification
  - requirement-decomposition
  - certainty-delivery
  - agents-md
---

# AI 接案的確定性交付工程：需求解壓縮、價值報價法、外部裁判 DoD 與 Session 工具鏈降維打擊

- **來源連結**：[YouTube 影片 (Debug 土撥鼠)](https://youtu.be/6M0TBCIyzR4)
- **影片標題**：〈AI 199 元做網站？新手接案最容易踩的四個坑：客戶付錢買的從來不是 Code〉
- **頻道作者**：Debug 土撥鼠
- **分析主題**：AI 接案市場低價內捲剖析、需求解壓縮（為什麼不能對名詞報價）、三大報價法（薪水法/請人成本法/價值報價法）、Scope 防失控與前提時程、結不了案的 Bug vs 新需求界線、軟體公司真正賣的「確定性（Certainty）」
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-24-feedback-desk-client-ticket-ai-handoff.md`](./2026-10-24-feedback-desk-client-ticket-ai-handoff.md)（客戶工單流轉與 AI 接案交接帳本）
  - [`notes/2026-10-23-web-to-app-android-packaging.md`](./2026-10-23-web-to-app-android-packaging.md)（Web-to-App 接案流程與毛利評估）
  - [`notes/2026-10-26-llm-burn-rate-cache-routing-benchmark.md`](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md)（LLM 燃燒率與 Cache 成本壓制）
  - [`notes/2026-10-18-multi-agent-factory-magpie-herdr-routing.md`](./2026-10-18-multi-agent-factory-magpie-herdr-routing.md)（AGENTS.md 邊界與多代理協同工廠）
  - [`notes/2026-10-26-block-buzz-nostr-agent-workspace.md`](./2026-10-26-block-buzz-nostr-agent-workspace.md)（Buzz 私有化常駐工作台）

---

## 1. 核心內容摘要：AI 時代軟體接案的六大殘酷現實（Key Insights）

Debug 土撥鼠在本作中直擊了當前 AI 爆發期軟體外包與接案市場的結構性劇變，提出資深工程師與軟體公司的核心生存法則：

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      AI 軟體接案生存矩陣：四大確定性與核心陷阱                          │
├───────────────────────────────┬─────────────────────────────────────────────────────────┤
│ 核心維度 (客戶真正買的價值)   │ 傳統新手踩坑陷阱               │ 工程化防線解法         │
├───────────────────────────────┼────────────────────────────────┼────────────────────────┤
│ 1. 需求確定性 (真知道要什麼嗎)│ 對空泛「名詞」報價 (壓縮檔陷阱)│ 三跳解壓縮 ＋ 原型工件 │
│ 2. 價格確定性 (價錢會失控嗎)  │ 工時換薪水 (AI 讓工時變短更窮) │ 請人成本法 ＋ 價值報價 │
│ 3. 時程確定性 (會不會準時交付)│ 承諾固定交期、「順便加一下」   │ 前提時程 ＋ 變更單(CR) │
│ 4. 驗收確定性 (專案能結案嗎)  │ 沒定義「完成」、Bug/需求扯皮   │ 外部裁判自動化 DoD 腳本│
└───────────────────────────────┴────────────────────────────────┴────────────────────────┘
```

### 1.1 六大核心觀點解構

1. **AI 接案市場現況：案子變多，錢卻變少（低價內捲）**：
   - AI 工具降低了編碼門檻，Fiverr/Upwork 與台灣接案平台充斥著 199 元起跳的套版與代碼搬運工。
   - 單純賣「Code 生產時間」的工程師在 AI 浪潮下價值急遽縮水。
2. **需求是一個壓縮檔：為什麼不能對名詞報價**：
   - 客戶提出的是空泛的名詞（如「我要一個電商系統」、「幫我做會員登入」）。
   - 名詞背後是未解壓的壓縮檔，包山包海（金流退款、發票統編、權限角色、異常處理）。對名詞直接喊價等於給自己挖坑。
3. **三種報價方法演進**：
   - **薪水法（時薪/人天）**：傳統估時方式。但在 AI 時代，AI 讓 10 小時的工作縮減成 1 小時，按工時收費只會越做越窮。
   - **請人成本法（機會成本）**：以客戶自行聘僱正職工程師的真實代價為基準（年薪 + 勞健保 + 設備 + 資遣風險 $\approx$ 年薪 1.3 倍），凸顯外包的相對划算。
   - **價值報價法（Value-Based Pricing）**：依據系統為客戶帶來的「增量營收」或「節省成本」定價，跳脫工時限制，分享商業價值。
4. **「這個順便加一下」：Scope 失控與時程要寫前提**：
   - 專案最常死在客戶無休止的「順便加一下小功能」。
   - 時程絕對不能寫死死線（Deadline），必須寫「前提條件（Prerequisites）」（例如：「在客戶提供金流金鑰與規格確認書後 14 個工作天內交付」）。
5. **結不了案的專案：驗收標準、Bug 和新需求怎麼分**：
   - 沒有定義「什麼叫完成（Definition of Done）」，專案永遠無法結案。
   - **分界線鐵律**：規格書有寫但跑不出來叫 Bug（免費修復）；規格書沒寫但客戶想要的叫新需求（走 Change Request 加收費用）。
6. **Code 越來越便宜，軟體公司到底還在賣什麼？**：
   - 代碼已成大宗商品（Commodity）。
   - 軟體公司真正賣的是**「確定性（Certainty）、架構風險承擔、業務落地能力與售後維護保障」**。

---

## 2. 運用 Session 實戰工具鏈之降維打擊（Session Mastery Mapping）

運用本對話 Session 中所沉澱的**五大資深實戰技巧、架構與軟體工具**，能將影片中的商業思維升級為**可機械化執行的工程防線**：

### 2.1 降維打擊一：以「Three.js / HTML 確定性工件」取代文字報價單，破解「名詞壓縮檔」
- **實戰痛點**：客戶只給空泛名詞，傳統訪談要耗費兩週來回寫需求書。
- **Session 解法**：
  - 運用 `answer-me-with-html` 與 `3d-model-anything` 技術：在第一次訪談後 24 小時內，直接用 AI 快速產出包含互動 UI、流程跳轉的 **單檔 HTML 確定性原型工件**。
  - 讓客戶直接「看到、點到、操作到」，在簽約前就把名詞解壓縮為具體欄位與畫面，徹底消滅認知落差。

### 2.2 降維打擊二：以「Sol 6.1 + Prompt Cache 燃燒率基準」將底層成本壓低 90%，在低價市場榨出暴利
- **實戰痛點**：接案單價被市場壓低，若 AI 消耗成本控不住，利潤空間極薄。
- **Session 解法**：
  - 嚴格執行我們實測的 **LLM 燃燒率與 Cache 路由基準**：
    - 嚴禁濫用高費率模型（如 Astra 6 4 小時燒乾 100 鎂）；
    - 規劃採用 **Sol 6.1 High（24H 跑五六個專案僅消耗 50% 額度）**，日常施工切換至 **Luna 6 Max**。
    - 搭配 **Prompt Caching 置頂**，重複讀取專案架構時 Token 費用驟降 80% 以上。
    - 競爭對手用人力或昂貴 API 成本做一單虧一單，我們以極低邊際成本達成百萬級專案高毛利。

### 2.3 降維打擊三：以專案 `AGENTS.md` 建立不可跨越的「Scope 鋼鐵防線」
- **實戰痛點**：客戶或工程師隨性「順便加一下」，導致專案 Scope 爆炸與代碼腐蝕。
- **Session 解法**：
  - 借鏡 **Grok/Herdr 統一進入點心法**：在專案根目錄由 `AGENTS.md` 嚴格定義：
    1. **已授權施工範圍（Whitelisted Scope）**
    2. **嚴禁變更禁區（Forbidden Zones / Non-Goals）**
    3. **變更門檻（Change Request Protocol）**
  - 當客戶提出額外要求時，不是人肉去爭執，而是讓 Agent 與合約附錄直接對齊 `AGENTS.md`，自動判定為 Scope 外項目並產出加價變更單。

### 2.4 降維打擊四：以「外部裁判自動化驗收腳本（Automated DoD Suite）」終結結案扯皮
- **實戰痛點**：結案時客戶無限上綱，把新需求硬拗成 Bug 扣留尾款。
- **Session 解法**：
  - 將本 repo 驗收體系（`verify_inbox.py` 與 `unittest`）移植至接案交付：
    - 簽約時將驗收標準寫成**客觀的自動化測試腳本（DoD Suite）**。
    - 驗收時在客戶伺服器或 CI 跑一次：**全綠 pass 即代表驗收完成、撥付尾款**；
    - 任何報錯對照測試案例，若案例未覆蓋者即為「新需求」，白紙黑字、無可辯駁。

### 2.5 降維打擊五：以「Buzz 私有化常駐工作台」將單次專案升級為「年費型維護生態」
- **實戰痛點**：專案做完一次性拿錢，沒有後續被動收入。
- **Session 解法**：
  - 運用 **Block Buzz Nostr 協同中樞**：幫客戶部署私有化 NAS / 地端常駐工作台，將交付的系統與專屬業務 Agent（客服、資料報表、運維）掛進類 Slack 聊天室。
  - 將原本一次性的軟體外包，升級為「系統交付 ＋ 私有 Agent 運維月費」的長青商業模式。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`ai-inbox` / `SanHsien/agent-assets`（私有））的契合點**：
  - 本 repo 本身即是「確定性交付」的終極範本（46 篇筆記、117 項任務全部由外部裁判與單元測試嚴格守護）。
  - 將這套「DoD 逐字達成、零空殼、自動化驗證」的方法論整理為通用接案標準，能直接賦能所有外包與技術交付。

- **採納與落地行動**：
  1. **制定「需求解壓縮與規格拆解範本（Decomposition Prompt）」**：建立能將客戶模糊名詞轉化為三層實施架構的引導提示詞。
  2. **產出「接案防失控合約條款指引」**：涵蓋前提時程（Prerequisites）、變更單（CR）與 Scope 禁區。
  3. **實作「客觀 DoD 自動化驗證產生器」**：讓 Agent 根據需求規格書自動產生驗收測試腳本。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261026-32`**｜**[優先級：高]** 撰寫「需求解壓縮與名詞規格化提示詞範本」收錄於 `templates/client-requirement-decomposition-prompt.md`
  - **目標範圍**：`templates/client-requirement-decomposition-prompt.md`（範本文件；不修改其他專案程式）
  - **具體做法**：
    1. 針對客戶常見的抽象名詞（會員、電商、AI 客服、後台管理），設計三層解壓縮結構。
    2. 自動產出：功能邊界、資料模型欄位、邊界異常處理與第一版 Single-file HTML 確定性原型代碼結構。
    3. 明列 Non-Goals（非本次範圍項目），徹底杜絕曖昧空間。
  - **驗收標準（DoD）**：產出 `templates/client-requirement-decomposition-prompt.md`，內含解壓縮框架、反例對照與電商/會員實戰案例；以 `Test-Path templates/client-requirement-decomposition-prompt.md` 驗證存在。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：templates/client-requirement-decomposition-prompt.md（158 行）：三層解壓縮框架、反例對照、電商與會員實戰案例。獨立驗收（fresh-context 審查員，2026-10-26）通過。

- [x] **`T-20261026-33`**｜**[優先級：中]** 撰寫「AI 接案防失控合約與時程前提規範指南」收錄於 `docs/freelance-contract-scope-and-prerequisites-spec.md`
  - **目標範圍**：`docs/freelance-contract-scope-and-prerequisites-spec.md`
  - **具體做法**：
    1. 制定時程前提條款（Prerequisites Clause）標準法言範本（將交付日與客戶前置依賴解耦）。
    2. 定義 Bug vs 新需求之判定判定表與 Change Request（CR）加價變更流程。
    3. 整合請人成本法與價值報價法（Value-based Pricing）之對話話術與談判手冊。
  - **驗收標準（DoD）**：產出 `docs/freelance-contract-scope-and-prerequisites-spec.md`，涵蓋合約條款範本、前提公式與報價話術；以 `Test-Path docs/freelance-contract-scope-and-prerequisites-spec.md` 驗證存在。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：docs/freelance-contract-scope-and-prerequisites-spec.md（182 行）：合約條款範本、前提公式、報價話術，附非法律意見聲明。獨立驗收（fresh-context 審查員，2026-10-26）通過。

- [x] **`T-20261026-34`**｜**[優先級：中]** 實作「客觀驗收標準（DoD）自動化驗證腳本產生器原型」於 `tools/generate_dod_verifier.py`
  - **目標範圍**：`tools/generate_dod_verifier.py` 與 `tests/test_generate_dod_verifier.py`
  - **具體做法**：
    1. 讀取專案需求 JSON/Markdown 規格，自動產生驗收 Python 測試腳本（HTTP API 檢查、DOM 元素斷言、環境變數檢驗）。
    2. 產生獨立的 `verify_delivery.py`，供客戶一鍵執行驗收並輸出法律級客觀交付報告。
    3. 撰寫單元測試驗證產生器之正確性。
  - **驗收標準（DoD）**：產出 `tools/generate_dod_verifier.py` 與單元測試，執行測試全綠通過。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：tools/generate_dod_verifier.py＋tests/test_generate_dod_verifier.py：22 tests OK；產生的 verify_delivery.py 對 T-20261026-07 實跑 3/3 PASS、exit 0。獨立驗收（fresh-context 審查員，2026-10-26）通過。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **客戶工單流轉與接案管理**：
  - [Feedback Desk 客戶工單與 AI 接手](./2026-10-24-feedback-desk-client-ticket-ai-handoff.md) ｜ 關聯任務：`T-20261024-03`
  - [Web-to-App 接案流程與毛利評估](./2026-10-23-web-to-app-android-packaging.md) ｜ 關聯任務：`T-20261023-03`
- **成本壓制與燃燒率優化**：
  - [LLM 燃燒率與 Cache 路由實測基準](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md) ｜ 關聯任務：`T-20261026-03`
- **確定性視覺工件與 Generative UI**：
  - [answer-me-with-html 視覺工件](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md) ｜ 關聯任務：`T-20261026-06`
- **長程私有化常駐工作台**：
  - [Block Buzz: Nostr 協同工作台](./2026-10-26-block-buzz-nostr-agent-workspace.md) ｜ 關聯任務：`T-20261026-08`、`T-20261026-27`
