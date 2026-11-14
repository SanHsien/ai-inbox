---
id: "2026-11-14-will-baoge-howtolivebetter-taiwan-edition-life-guide"
title: "Will 保哥改寫《高性價比人生指南》台灣版：772 條建議 + life-decision-guide skill（未逐條核完）"
source_url: "https://www.facebook.com/share/1BvwoVnL6f/"
source_platform: "facebook"
author: "Will 保哥（doggy8088）"
analyzed_at: "2026-11-14"
analyzed_by: "antigravity"
status: archived
cluster: 3
cluster_role: "人生指南Skill"
short_title: "台灣版人生指南"
tags:
  - howtolivebetter
  - doggy8088
  - life-guide
  - agent-skill
  - zh-tw
  - localization
  - opencc
  - cc-by-4-0
  - claude-code
  - codex
---

## Executive Summary

**Will 保哥的技術交流中心**（Facebook）宣布把網路廣傳、擁有 74.1K stars 的《高性價比人生指南》改寫為台灣版：把中國大陸的法規與生活習慣改成台灣資訊。貼文語氣是「請認真看，不要叫 AI 看」。

資料來源說明：Facebook 全文被截斷，只取得 og 摘要；以下內容以 GitHub 倉庫實讀為準。

核心事實：

- **原專案**：`eternity4719/HowToLiveBetter`，**75,646 stars、6,703 forks**（貼文時為 74.1K），CC-BY-4.0，2026-09-07 建立，2026-11-12 仍在更新，open issues 17。
- **台灣版**：`doggy8088/HowToLiveBetter`（fork，預設分支 `zh-tw`），116 stars、16 forks，2026-11-04 建立，線上版 `how-to-live-better.gh.miniasp.com`。
- **個人維護 Fork**：`SanHsien/HowToLiveBetter`（fork 自 `doggy8088/HowToLiveBetter`，root upstream 為 `eternity4719`），本地路徑 `C:\GitHub\HowToLiveBetter`。
- 內容：772 條建議，每條標「花掉什麼、換回什麼、證據等級 A/B/C」，來源只引期刊論文與官方文件；書分 30 多節（不要早死、不要浪費錢、法律紅線、緊急情況、租房與買房、看病、出國等）。
- **譯者自述「全書還沒逐條核完」**（`其他語言.md` 台灣列），內容可信度需打折。

---

## 技術架構深挖

### 倉庫結構（台灣版 `zh-tw` 分支）

```
doggy8088/HowToLiveBetter (zh-tw)
├── book/01..33+-*.md            # 正文，每節 20–180 KB
├── docs/*.md、docs/核實記錄/     # 長文與核實記錄
├── skills/life-decision-guide/   # AI skill 正本（Claude Code + Codex 共用）
├── .claude/skills/life-decision-guide/SKILL.md   # 薄殼，指向正本
├── AGENTS.md / CLAUDE.md (123 KB) # 改書規則（檔名 CLAUDE.md 只是歷史原因）
├── index.html                    # 線上檢索頁 + 性價比篩選 + 生活自查
├── .github/workflows/{book,links,zh-tw-locale}.yml
├── tools/check-zh-tw-locale.mjs  # 檢查急難電話與地域說明
└── LICENSE (CC BY 4.0) + LICENSE-CODE
```

下載格式：PDF、EPUB、離線單檔 HTML、Anki 牌組（`epub-latest` release）。

### 台灣化流程（由 commit 與 workflow 還原）

```
上游 main（簡體，大陸語境）
   │  同步（例：「zh-tw: 同步上游 36c7856 並重產繁體中文版」）
   ▼
重產管線：opencc tw2 繁簡與用語轉換 + PROTECT 檔名（避免 文件名↔檔名 震盪）
   ▼
人工校訂：SKILL.md「法律支持你」審限、急難電話、制度內容
   ▼
zh-tw-locale workflow：只檢查急難電話與地域說明（不建 EPUB、不發布、不用憑證）
```

重點：**自動化只驗證「電話與地域說明」**，法規、健保、勞保等實質內容的台灣化靠人工校訂，且譯者承認尚未逐條核完。

### 上游寫作規則（CLAUDE.md 節錄，值得借鏡）

- 每條必答兩題：花掉什麼、換回什麼；四種資源（壽命、時間精力、金錢、人身自由）**分開算，不互相折算**。
- 證據分級 A（薈萃分析/大型佇列/RCT，有具體數字）、B（有研究但難量化）、C（作者經驗或共識）；有爭議者必須標「爭議」並列反方證據。
- 只引原始文獻（DOI/PubMed、WHO/CDC/官方機構）；禁止知乎、公眾號等二手轉述；一手媒體報導僅在五個條件滿足時收錄，且不得用來撐收益量級或上調證據等級。
- 寫「法律支持你」必須同時寫過程成本（要不要打官司、多久、誰出律師費）。
- 涉及他人時依受益人四檔（自己、直系親屬、朋友同事、陌生人）分開算，寫陌生人時必須寫風險面。

### `life-decision-guide` skill 設計（實讀）

| 設計 | 內容 |
|------|------|
| 觸發詞 | 該不該、值不值、要不要、划不划算、怎麼選、幫我決定、這樣犯法嗎、能領什麼、先做什麼、性價比 |
| 核心規則 | **沒查到就別答**：每個數字、法條、結論必須指回某節某條；指不回去就直說書裡沒寫，常識判斷需標明是常識；不得憑記憶補數字、DOI、法條款號 |
| 第 0 步 | 先判斷是否要馬上停下：急症、火場、溺水 → 先說 119；犯罪暴力 → 110；自殺念頭且人清醒 → 1925 安心專線；已發生危險 → 119（必要時加 110），不要只給 1925 |
| 在地化 | 明確寫「不要把 120、12356 當成台灣電話」；119/110/1925 附官方頁連結與查閱日（2026-11-07） |
| 取得正文 | 隨包 `references/book/`（離線）→ 本地倉庫 → 遠端 `git clone --depth 1`，或 `curl` 取 raw 檔 |
| 輸出 | 按成本、收益量級、證據等級排序，並標「出自第幾節第幾條」 |

---

## 風險與疑點

| 項目 | 評估 |
|------|------|
| **內容未逐條核完** | 譯者自述全書未逐條核對；醫療、法律、保險、緊急處置條目可能殘留大陸制度或轉換錯誤 |
| **高風險領域** | 內容涉及急救、用藥、法律責任、投資與保險，錯誤成本高；屬參考資料，不構成專業意見 |
| **自動轉換風險** | opencc 用語轉換有已知震盪（commit 已修一例），僅靠人工校訂補洞 |
| **遠端取得正文** | skill 在無本地副本時以 `git clone` 或 `curl` 抓遠端檔案作為回答依據；來源是作者個人倉庫的活分支（`zh-tw`），內容會變動，屬可變來源 |
| **規模** | `book/` 每節 20–180 KB、CLAUDE.md 123 KB；整包載入 context 成本高，skill 靠 `index.tsv` 與節定位來避免 |
| **授權** | 書 CC-BY-4.0（需署名）；程式 `LICENSE-CODE`；fork 屬合法再創作，需保留署名 |
| **上游敏感性** | 上游收錄境外一手媒體報導與敏感法律條目，內容立場需自行判斷 |
| **未驗證** | 條目的證據等級、DOI、台灣法規現行性均未逐條查核；僅確認倉庫結構、skill 規則與 fork 關係 |

---

## 與本機防線對照

- **來源明確**：作者 Will 保哥（doggy8088）長期經營台灣技術社群，倉庫與 Facebook 貼文互相對得上；上游身分為 `eternity4719`。
- **本地 Fork 與安全配置**：本機已完成個人維護 fork（`SanHsien/HowToLiveBetter`）並 clone 至標準路徑 `C:\GitHub\HowToLiveBetter`。遠端防線依全域規範嚴格配置：`origin` 鎖定 `SanHsien/HowToLiveBetter`，而 `upstream`（`doggy8088`）與 `upstream-root`（`eternity4719`）之 push URL 均設為 `DISABLE`，確保任何變更或 PR 絕不誤推上游。
- **零信任**：skill 為只讀指引，不含 hook 或安裝腳本；唯一的外部取得是 `git clone`/`curl` 抓 Markdown。若要採用，直接使用本地 `C:\GitHub\HowToLiveBetter` 離線副本，避免讓 agent 即時抓外部活分支。
- **可借用的設計**：「沒查到就別答、每條指回出處」與本機「回報前要實跑」的原則同源，可移植到本機知識庫型 skill。
- **不建議**：以此 skill 取代專業醫療或法律意見；任何涉及用藥、急救、訴訟的結論都要回到官方原文核對。

---

## 評估結論與處置

**評分：⭐⭐⭐（3/5）**

作為「引用導向」的知識庫與 skill 設計範例，品質高：證據分級、來源規範、在地化急難電話與「沒查到就別答」都做得扎實。扣分：內容由大陸語境轉換而來，**譯者自述未逐條核完**，高風險領域的可信度無法保證；貼文本身是推薦與宣傳，沒有新的技術細節。

**處置**：本機已 fork 並 clone 至 `C:\GitHub\HowToLiveBetter`，具備獨立維護與離線查閱環境。若要試用 skill，直接引用本地副本（`references/book/`），切勿讓 agent 聯網即時抓外部活分支；高風險條目（健保、勞保、租賃、急救電話）須先抽樣對照台灣法規官方原文再決定是否採納。

**參考連結**：
- 個人 Fork：https://github.com/SanHsien/HowToLiveBetter
- 台灣版：https://github.com/doggy8088/HowToLiveBetter
- 線上版：https://how-to-live-better.gh.miniasp.com/
- 上游：https://github.com/eternity4719/HowToLiveBetter
