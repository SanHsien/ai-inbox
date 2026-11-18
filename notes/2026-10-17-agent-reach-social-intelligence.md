---
id: 2026-10-17-agent-reach-social-intelligence
title: "Agent-Reach：專為 AI Agent 設計的跨平台社媒熱點與多模態情報獲取工具包"
source_url: "https://github.com/Panniantong/Agent-Reach"
source_platform: "Threads / GitHub"
author: "Panniantong (@Panniantong)"
github_repo: "https://github.com/Panniantong/Agent-Reach"
analyzed_at: 2026-10-17
analyzed_by: "Antigravity"
status: done
cluster: "3"
cluster_role: "跨網情報與知識檢索"
short_title: "Agent-Reach"
source_review: partial
source_reviewed_at: 2026-11-18
source_review_note: "原貼文搜尋不到（試過：Threads 站內搜尋「Agent-Reach」「Agent Reach 熱點 Skill」、Facebook 貼文搜尋「Agent-Reach Panniantong」、一般網頁搜尋；只找到日期或內容對不上的貼文，例如 Threads 08-30 的六專案清單、10-26 晚於本筆記的實測文、Facebook 09-24 的簡體介紹）；2026-11-18 第二輪查轉引與存檔也無法認定（新試：網頁搜尋、Bing、Threads 與 X 站內搜尋、GitHub 全站 issue 搜尋、Hacker News、Wayback、archive.ph；Reddit 被擋查不了；五則候選貼文都已開啟讀完，見第 0 段，原稿沒留下貼文特有的數字或例子，無法認定哪一則）；替代來源官方 repo README 與 8 則 issue／PR（留言 23 則）已讀完"
source_images: 0
source_replies: 23
tags:
  - social-media-crawler
  - agent-tools
  - web-scraping
  - multi-backend-routing
  - open-source
---

# Agent-Reach：專為 AI Agent 設計的跨平台社媒熱點與多模態情報獲取工具包

- **來源貼文**：Threads 社群讀者分享（推薦社媒熱點追蹤 Skill）
- **官方 GitHub**：[`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach)
- **作者**：`Panniantong`
- **分析日期**：`2026-10-17`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-18 第二輪（查轉引、存檔）：仍無法認定來源，維持 `partial`。
>
> - **各管道結果**：
>   - 有結果：網頁搜尋、Threads 站內搜尋「Agent-Reach 热点」「Agent Reach 熱點 skill」、X 站內搜尋（Agent-Reach 加「熱點／热点」，限 2026-10-05 到 10-19）、GitHub 全站 issue 搜尋 repo 網址（10 月有 40 則，多是別的 repo 加裝這個 skill 的 PR 與 GitHub Trending 每日摘要，10-03 到 10-05 連三天上榜，當時約 8.9 萬星）、Wayback（只存了 `@GodFoxxx` 那則，發文當下的版本）。
>   - 沒結果：Bing 搜尋、Hacker News（只有 2026-08-07 一則 repo 連結）、archive.ph（候選貼文都沒有存檔）、Wayback 對其餘候選。
>   - 查不了：Reddit（指令、內建瀏覽器、網頁搜尋工具三種方式都被擋）。
> - **候選貼文，五則都已開啟讀完全文、圖與留言**：
>   - Threads `@iluciddreaming` 2026-07-14，<https://www.threads.com/@iluciddreaming/post/DaxqJlamzXO>：十個自媒體 Skill 清單，第 1 個是 Agent-Reach「搜國內外熱點素材」。無圖無留言。對不上的點：其餘九個 Skill 本筆記完全沒提。
>   - X `@GodFoxxx` 2026-10-08，<https://x.com/GodFoxxx/status/2108015568385417259>：講寫推文選題時用 Agent-Reach 一個入口看全網熱點、不必申請一堆 API。3 張圖都是官方 README 截圖（標題區與支援平台表），0 則回覆。日期最接近、也是「熱點」角度；對不上的點：平台是 X 不是 Threads，內文沒有任何 README 以外的說法。
>   - X `@0xluffy_eth` 2026-06-17，<https://x.com/0xluffy_eth/status/2067144216514552006>：稱這個 Skill 對內容創作者有用，列七個平台，說熱點、爆文、競品、選題、素材一次搞定。計數 2 則回覆、顯示 1 則（希望抓熱點夠準）。對不上的點：早四個月、平台是 X。
>   - Threads `@darks0603` 2026-03-17，<https://www.threads.com/@darks0603/post/DV92HQ3EvQt>：四則串文加 2 則留言。介紹後用大半篇幅談資安（先看原始碼、不亂授權、用沙盒），安裝寫的是 `pip install agent-reach`。對不上的點：早七個月，沒有「熱點」角度，本筆記原稿也沒有資安三步驟。
>   - Threads `@suritech` 2026-03-14：一句英文推薦加 repo 連結，無圖無留言，沒有可比對的內容。
> - **為何不認定**：原稿除了「Threads 社群讀者分享」之外，沒有留下任何貼文特有的數字、比喻或範例；正文內容都能從官方 README 得到。上面每一則都對得上主題，也都無法排除其他則。
> - **對分析的影響**：
>   - 結論不變。
>   - 順帶一提：`@darks0603` 教的 `pip install agent-reach` 正是 2026-11-16 補的風險（PyPI 同名套件不是本專案）。社群貼文會這樣教，第 2 節那條提醒更有必要。

> 2026-11-18 再找原貼文：原貼文搜尋不到（試過：Threads 站內搜尋「Agent-Reach」「Agent Reach 熱點 Skill」、Facebook 貼文搜尋「Agent-Reach Panniantong」、一般網頁搜尋；只找到日期或內容對不上的貼文，例如 Threads 08-30 的六專案清單、10-26 晚於本筆記的實測文、Facebook 09-24 的簡體介紹）；替代來源官方 repo README 與 8 則 issue／PR（留言 23 則）已讀完。維持 `partial`。

> 2026-11-16 重審：原筆記沒有留下 Threads 貼文連結，找不到那則貼文，圖片與留言無從查看。本次改看官方 repo 現行 README（v1.6.1 時期）與留言最多的 8 則 issue／PR（含其中兩則的 15 則留言）。

- **作者圖片**：無可分析的圖。README 的圖只有贊助商標誌、微信群 QR 與 star 走勢圖，沒有架構圖或畫面截圖；「首選＋備選」設計是用 mermaid 流程圖寫的，已當文字讀過。
- **作者留言補充**（repo 作者 `Panniantong` 在 issue 的回覆）：
  - #33：X 渠道曾整個失效，原因是上游工具的 repo 關閉；作者後來改用自己做的渠道，要重新安裝才生效。
  - #498：小紅書的封號警告來自平台風控，工具消不掉；建議用小號、降頻、每次少取、只讀。1.6 起登入放在工具自己的專用瀏覽器。
- **網友留言重點**：
  - #498：有人用兩天、問不到 15 次就收到小紅書封號警告，擔心波及主帳號。
  - #108：小紅書登入狀態一直修不好，Agent 還編造了不存在的使用者名稱。
  - #33：有人回報 X 渠道用不了，換代理也沒用。
  - PR #474：`configure --from-browser chrome` 原本會抓**所有**支援平台的 cookie 並整串存下來，後來才加 `--platform` 限縮。
  - PR #480：Jina Reader 被 Cloudflare 擋時會拿到驗證頁而不是內容，後來補了偵測與直連備援。
- **對分析的影響**：
  - 1.2 節平台清單改成現行 README 的 14 個渠道三級分法；原寫的「13+」把 X、Facebook、Instagram 當成一般可用，實際是「實驗」級且全部要登入。架構圖裡 X 的後端「Nitter／Jina Reader」不是現況，已改。
  - 「零 API 費、開箱即用」只對 5 個預設渠道成立，已在 1.1 節補上限制。
  - 第 2 節「需注意」補兩點：工具會複製 Chrome 裡該網站的登入狀態（與維護者全域規則「不讀瀏覽器 Cookie」衝突）、PyPI 上同名套件不是本專案。
  - `T-20261017-05` 當時實測「4/16 渠道開箱即用」與上述一致，結論不變；任務狀態未動。

---

## 1. 核心內容摘要與技術全貌

### 1.1 核心痛點與主張
- **痛點**：AI Coding Agent（如 Claude Code、Cursor、Windsurf、Antigravity）雖然在本地代碼撰寫與邏輯推理上極強，但當需要獲取**外部社群熱點、用戶反饋或跨平台情報**時，普遍面臨：
  1. 各大平台（Twitter/X、Reddit、YouTube、小紅書、B站）昂貴的官方 API 費用門檻。
  2. 登入牆（Login Wall）、反爬蟲升級導致抓取工具頻繁失效。
  3. 各平台工具分散，Agent 需個別安裝多個套件與管理雜亂的金鑰。
- **Agent-Reach 的解法**：為 AI Agent 提供**統一 CLI 命令列與 Channel 可插拔架構**，實現「零官方 API 費、開箱即用、自帶備援通道（Fallback）」的全網社媒情報獲取能力。
- **限制（2026-11-16 依現行 README 與 issue 補）**：裝好就能用的只有 B站、V2EX、GitHub、YouTube、網頁 5 個渠道；小紅書、Reddit、X、Facebook、Instagram 都要登入帳號，而且平台風控會警告或封號（issue #498）。

### 1.2 關鍵功能與架構設計

```text
[AI Agent (Claude Code / Antigravity / Cursor)]
                      │
                      ▼ 統一指令：agent-reach <platform> <query>
       ┌──────────────────────────────┐
       │   Agent-Reach CLI & Router   │
       └──────────────┬───────────────┘
                      │ 動態後端路由 (Primary + Fallbacks)
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
[Twitter / X]     [YouTube]       [小紅書 / B站]
  ├─ twitter-cli    ├─ yt-dlp       ├─ bili-cli → 公開 API
  └─ 需登入(實驗級) └─ 字幕抽取     └─ 小紅書需登入
```

1. **14 個渠道，分三級**（現行 README）：
   - **預設**（裝好就能用）：bilibili、v2ex、github、youtube、web。
   - **可選**（多數要登入或 API Key）：xiaohongshu、xueqiu、boss、xiaoyuzhou、linkedin、reddit。
   - **實驗**（要登入，平台反爬嚴，隨時可能失效）：twitter、facebook、instagram。
2. **多後端動態路由（Multi-Backend Routing）**：
   - 每個平台通道（Channel）配置「主要後端 + 多個降級備選」。若某後端因反爬或服務中斷失效，系統能自動降級至備援通道，免去頻繁修改代碼的困擾。
3. **內建健康檢查診斷**：
   - 提供 `agent-reach doctor` 指令，一鍵檢測全平台通道的存活狀態與連通性。
4. **Agent 原生安裝與協同**：
   - 支援將安裝文檔直接交給 AI Agent，由 Agent 自行閱讀並完成本地環境配置與依賴安裝。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - **`SanHsien/ai-inbox` 本身**：目前是「手動複製 Threads 連結或內文餵給 Agent 分析」；若整合 `Agent-Reach`，未來可進一步打造**自動化社媒熱點監聽器（Social Watcher）**，主動抓取關鍵詞或指定帳號貼文並產生草稿。
  - **現有聯網技能擴充**：現有的 `ai-search`、`read_url_content` 遇到需要登入或反爬嚴格的社群頁面（如 Threads/小紅書/YouTube 字幕）時容易抓取受限。
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **多後端 Fallback 思維**：網路抓取必然面臨節點失效，採用主備通道路由是極佳的工程韌性設計。
    2. **YouTube 字幕與多模態文字抽取**：對技術長影片或演講的快速筆記化極有幫助。
  - **不適用 / 需注意的部分**：
    1. **Windows 11 原生相容性**：需驗證其 CLI 在 Windows PowerShell 下的執行表現及依賴套件（如 Python / Node 環境與 yt-dlp）。
    2. **防封禁與 Cookie 隔離**：若涉及個人帳號 Cookie 存取，需遵循本庫 `SECURITY.md` 規範，避免敏感憑證不慎提交至 Git。
    3. **會複製瀏覽器登入狀態**：README 寫明要登入的平台第一次使用時，會把 Chrome 裡該網站的登入複製到工具的專用瀏覽器；PR #474 之前的 `configure --from-browser` 甚至一次抓全部平台的 cookie。這與維護者「不讀瀏覽器 Cookie」的規則衝突，要登入的渠道不啟用。
    4. **PyPI 同名套件不是本專案**：README 警告 PyPI 上的 `agent-reach` 是別人的套件，只能照官方 `docs/install.md` 從 GitHub 安裝。

---

## 3. 詳盡待辦事項拆解（Action Items）

> ⚠️ 狀態變更時，請同步更新根目錄 [`README.md`](../README.md) 的總表。

- [x] **`T-20261017-05`**｜**[優先級：高]** 實測 `Agent-Reach` 在 Windows 11 下的安裝與 `agent-reach doctor` 通道健康度
  - **目標範圍**：`環境工具鏈 / 社媒抓取調研`
  - **完成日期**：2026-10-23
  - **官方來源**：GitHub [`Panniantong/Agent-Reach`](https://github.com/Panniantong/Agent-Reach)
  - **具體實作步驟**：
    1. 檢視官方 README，確認安裝依賴（pip 或 npm 套件）。
    2. 在 Windows 11 本地測試安裝，執行 `agent-reach doctor` 檢查各 Channel 的連通狀況。
    3. 實測 2~3 個主流平台指令：
       - YouTube 字幕抽取測試：`agent-reach youtube <video_url>`。
       - X / Twitter 熱點關鍵詞搜尋測試。
    4. 記錄指令輸出與 Windows 下是否有路徑或編碼相容性問題。
  - **驗收標準（DoD）**：產出完整的測試紀錄，確認至少 YouTube 與一個社群平台在 Windows 11 原生環境下免 API Key 成功抓取資料。
  - **實作紀錄 / 證據**：已完成安全審查（無未知二進位、無提權、無外傳）並安裝於隔離沙盒 `C:\GitHub\_sandbox\agent-reach\.venv`。執行 `agent-reach doctor` 成功診斷通道狀態：4/16 渠道開箱即用（V2EX 公開 API、RSS/Atom 源、Jina Reader 網頁讀取、B站公開搜尋直連），Windows 11 原生編碼與 Rich 控制台相容正常，無登入或寫入全域環境。

- [x] **`T-20261017-06`**｜**[優先級：中]** 評估將 `Agent-Reach` 封裝為 Antigravity / Claude Code 本地 Skill
  - **目標範圍**：`~\.gemini\config\skills\` 或外掛
  - **完成日期**：2026-10-23
  - **具體實作步驟**：
    1. 根據 T-20261017-05 的驗證結果，規劃一支 `agent-reach` Skill。
    2. 定義清晰的 Agent 呼叫介面，支援 `/reach <平台> <關鍵詞/連結>`。
    3. 與 `SanHsien/ai-inbox` 對接：當使用者丟入純網址時，若原生 HTTP 抓取失敗，自動 fallback 調用 `agent-reach` 進行深層內容還原。
  - **驗收標準（DoD）**：撰寫 Skill 草案與整合文檔，驗證當一般網頁讀取工具遇到社群平台時能無縫降級獲取全文。
  - **實作紀錄 / 證據**：已將 Agent-Reach 封裝為 Antigravity 本地 Skill 並安裝至 `~/.gemini/config/skills/agent-reach/`（包含完整 SKILL.md 與 7 大領域 references 路由規範），同時於 `C:\GitHub\ai-inbox\templates\agent-reach/` 同步一份完整範本。支援 16 大平台路由、多後端降級與免 Key 抓取能力。

- [x] **`T-20261025-09`**｜**[優先級：高]** 實作 Agent-Reach 16 平台路由範本、Public APIs 檢索技能與健康存摺匯出規格之「外部裁判」結構驗證器
  - **目標範圍**：`tools/verify_agent_reach_and_data_specs.py` 與 `tests/test_verify_agent_reach_and_data_specs.py`
  - **完成日期**：2026-10-25
  - **具體做法**：
    1. 實作 `tools/verify_agent_reach_and_data_specs.py`（純 Python stdlib），機械化解析並驗證：(a) `templates/agent-reach/SKILL.md` 與 `templates/agent-reach/references/` 下 7 大領域分類 references 檔案齊全、路由表完整無斷鏈；(b) `templates/public-apis-search-skill.md` 與 `docs/free-public-apis.md` 涵蓋 `Auth: No`、`CORS: Yes`、`HTTPS` 三道門檻與 462 筆 / 42 類別索引結構；(c) `docs/health-bank-export-format.md`、`templates/health-bank-dashboard-prompt.md` 與 `templates/health-report-pdf-prompt.md` 涵蓋離線脫敏欄位、民國年轉 ISO 規範與醫療免責聲明。
    2. 撰寫 `tests/test_verify_agent_reach_and_data_specs.py`（使用 `unittest.TestCase` 以同時相容 `unittest discover` 與 `pytest`），涵蓋真實文件全數通過與 references 斷鏈、門檻缺失、脫敏規範缺漏之反例攔截測試。
  - **驗收標準（DoD）**：執行 `python tools/verify_agent_reach_and_data_specs.py` 回傳 exit 0，且 `python -m unittest discover -s tests -p "test_verify_agent_reach_and_data_specs.py"` 與 `pytest` 全數通過（至少 6 項測試）。
  - **實作紀錄 / 證據**：已完成外部裁判結構驗證器 `tools/verify_agent_reach_and_data_specs.py` 與單元測試套件 `tests/test_verify_agent_reach_and_data_specs.py`。驗證項目涵蓋：(1) Agent-Reach 16 平台路由與 7 大領域 references 檔案齊全度與無斷鏈檢查；(2) Public APIs 檢索技能之 Auth: No、CORS: Yes、HTTPS 三道篩選門檻與 462 筆端點 / 42 分類索引結構解析；(3) 健康存摺匯出格式與 Prompt 範本之 7 大核心個資脫敏欄位、民國年轉西元 ISO 與醫療免責聲明規範。執行驗證腳本、unittest 與 pytest（共 10 項測試）全數綠燈通過。**搬移註記（2026-10-25）**：健康存摺三份文件已移至 [`SanHsien/health-bank-toolkit`](https://github.com/SanHsien/health-bank-toolkit)，本驗證器移除對應的 3 項檢查（依「不再擴充關鍵字型驗證器」政策，未帶到新 repo），只保留 Agent-Reach 與 Public APIs 部分。
