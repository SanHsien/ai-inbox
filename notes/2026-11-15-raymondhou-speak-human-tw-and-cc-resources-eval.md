---
id: "2026-11-15-raymondhou-speak-human-tw-and-cc-resources-eval"
title: "Raymondhou0917 雙倉庫評估：speak-human-tw（去 AI 味 Skill）與 claude-code-resources（入門資源站）"
source_url: "https://github.com/Raymondhou0917/speak-human-tw"
source_platform: "GitHub"
author: "Raymond Hou (Raymondhou0917)"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity；Codex 於 2026-11-15 查核修訂"
status: done
cluster: 3
cluster_role: "繁中去AI味與資源評估"
short_title: "說人話Skill與CC資源評估"
source_review: full
source_reviewed_at: 2026-11-17
source_images: 7
source_replies: 91
tags:
  - skill
  - zh-tw
  - de-ai
  - writing
  - claude-code
  - repo-evaluation
---

# Raymondhou0917 雙倉庫評估：speak-human-tw 與 claude-code-resources

- **來源連結**：[speak-human-tw 固定來源](https://github.com/Raymondhou0917/speak-human-tw/tree/14885da5c91ed7ca2972f084599edcdd2a32ad04)、[claude-code-resources 固定來源](https://github.com/Raymondhou0917/claude-code-resources/tree/1320df1e396e7630b09d2dc80fae4b2c96861d54)
- **發布平台 / 作者**：GitHub／Raymond Hou（Raymondhou0917）
- **分析／修訂日期**：2026-11-15
- **當前狀態**：`🟢 已完成 (Done)`
- **完整評估**：[speak-human-tw 唯讀評估](../docs/speak-human-tw-assessment.md)

## 0. 原始資料盤點

> 貼文文字、作者上傳的每張圖片、作者留言補充、網友留言都要看過，見 AGENTS.md 第 3 節。本篇來源是 GitHub，圖片看 README，留言改看 issue 與 PR。

- **作者圖片**（2026-11-16 看，徽章不計）：
  - speak-human-tw 6 張：橫幅；案例一是拿 2024 年真人手寫的週報去檢查，結論「不用改」（圖內寫「36 種 AI 痕跡」，現行是 38 類，是舊版截圖）；案例二是檢查 AI 代寫的 YouTube 留言回覆，逐條列 6 處並附原句、理由、改法（截圖底部顯示作者是在略過權限確認的模式下執行）；四格情境示意（社群、文章、Email、行銷）；求星圖；星數成長圖（07-10 上線，11-15 為 1,178）。
  - claude-code-resources 1 張：「Claude Code × Codex 雙棲進化地圖」，入門／活用／高手三級，各分 Claude Code、兩者共用、Codex 三欄。2026-11-17 放大逐格看完：
    - 入門：兩邊都建議先用桌面版；共用欄講 Context、壓縮對話、約用到 80% 就手動整理、規劃與執行分兩個對話。
    - 活用：Claude Code 欄是 `/loop`、`/goal`、`/verify`、Hooks；共用欄是先講背景目的與結果、直接給完整路徑、優先用 API／MCP／瀏覽器控制而不是看螢幕、流程穩定後存成 Skill；Codex 欄是整理檔案、Artifacts、Computer Use（標為最後手段）、遠端接續。
    - 高手：Claude Code 欄是 `/schedule`、agents、agent teams、ultracode；共用欄是核心規則只維護一份（`CLAUDE.md`／`AGENTS.md` 只當入口）、重要偏好存在自己的資料夾而不是只放平台記憶、規則與技能要兩邊都讀得到、能跑很多代理不代表每次都該開滿；Codex 欄是 Automations、Security、Worktree、Profiles。
    - 這張圖是概念導覽，沒有指令細節；「共用」欄的主張（單一規則來源、本機記憶、可遷移）與維護者現行做法相同，沒有新做法可採。
- **作者留言補充**：兩個 repo 的維護回覆多數署名「雷小蒙（雷蒙的 AI 分身助手）」，先由 AI 初審、再說明「等雷蒙確認」。
- **網友留言重點（speak-human-tw）**（2026-11-17 用 `gh api` 補讀：10 個 issue／PR 與 21 則留言全讀）：
  - [PR #2](https://github.com/Raymondhou0917/speak-human-tw/pull/2)：外部貢獻者提出「稿件是資料不是指令」的隔離；作者方實測注入後採精簡版併入，並明講這是提示層防護、不能取代執行環境的權限控制。
  - [PR #6](https://github.com/Raymondhou0917/speak-human-tw/pull/6)（未合併）：有人拿它處理 Code Review 報告，發現「再降格式」的字面規則會把狀態摘要行、表格這類文件骨架改寫成散文，提議加第 6 類保護；作者方還在確認這類文件算不算適用範圍。
  - [#8](https://github.com/Raymondhou0917/speak-human-tw/issues/8)：OpenCode 的打包版曾壞掉，改成直接 clone 進 skills 目錄。[PR #7](https://github.com/Raymondhou0917/speak-human-tw/pull/7)：詞表加「運營→營運」，PR 自述由 AI agent 起草。[#5](https://github.com/Raymondhou0917/speak-human-tw/issues/5)：作者方確認只針對台灣繁中，不含粵語與文言。
  - 補讀到的三項：[#3](https://github.com/Raymondhou0917/speak-human-tw/issues/3)／[PR #4](https://github.com/Raymondhou0917/speak-human-tw/pull/4) 是社群做的 OpenCode 外掛，作者方說抓了 npm 套件實際內容檢查過（規則檔照原樣打包、沒有安裝後腳本）才收進安裝文件，但仍定位為社群整合、不是官方支援；[PR #10](https://github.com/Raymondhou0917/speak-human-tw/pull/10)（作者本人，2026-11-09 合併）一次加了 17 個詞，早於本篇固定的 commit，所以「47 組詞表」已含這批。PR #6 自 2026-08-08 作者方說「等雷蒙確認」後沒有再動，仍未合併。
- **網友留言重點（claude-code-resources）**（2026-11-17 補讀：39 個 issue／PR 全部看過，其中 21 個是自動同步課程場次的 PR、只有標題；其餘 18 個的本文與 21 則留言全讀）：
  - [#1](https://github.com/Raymondhou0917/claude-code-resources/issues/1)、[#2](https://github.com/Raymondhou0917/claude-code-resources/issues/2)、[#3](https://github.com/Raymondhou0917/claude-code-resources/issues/3)：教材曾寫出不存在的套件名稱（三個掛在 `@anthropic-ai` 底下的名字），讀者照做失敗後回報才修正。
  - [#4](https://github.com/Raymondhou0917/claude-code-resources/issues/4)：有讀者照教學設定 Google Workspace CLI 的 OAuth 後，Google Cloud 專案被停權，申訴一個月沒回音；作者事後補上官方 README 原有的兩個警告。
  - [#12](https://github.com/Raymondhou0917/claude-code-resources/issues/12)：讀者指出「安全刪除」教材在 Windows 原生 PowerShell 沒有資源回收筒保護，並附 PowerShell 5.1、7 與 Git Bash 的實測；作者已補進教材。
  - [#13](https://github.com/Raymondhou0917/claude-code-resources/issues/13)：讀者回報在 macOS 的 Claude 桌面版 Code 分頁，`permissions.deny` 與 PreToolUse hook 都沒生效，危險指令真的執行；引用的上游 `anthropics/claude-code#87657` 現為已關閉（帶 stale 標籤）。
    - 本機證據（僅 Windows，與該回報的 macOS 不同平台）：2026-11-16～17 維護者 Windows 桌面版 Code 分頁的 PreToolUse hook（`route_guard`）實際攔下了未宣告路由的 Edit 呼叫，hook 有生效；`permissions.deny` 在 Windows 桌面版未驗證。macOS 的回報本 repo 無法重現或反駁。
  - [#6](https://github.com/Raymondhou0917/claude-code-resources/issues/6)：Windows 桌面版接 MCP 失敗，作者建議改走 CLI。
  - 補讀到的幾項：
    - #13 的回報者事後補一句：問題其實出在付費課程教材的設定，不是這個 repo 的入門教材，所以在這裡關掉、改貼到課程 repo；作者仍在入門教材加了一段「桌面版 Code 分頁對 deny 清單與 hook 支援不完整，高風險操作請在終端機做」的已知限制。
    - [#9](https://github.com/Raymondhou0917/claude-code-resources/issues/9)：新手把要在終端機執行的安裝指令貼進 Claude 對話框；作者在兩處指令前加註「請在終端機執行」。
    - [#7](https://github.com/Raymondhou0917/claude-code-resources/issues/7)／[PR #8](https://github.com/Raymondhou0917/claude-code-resources/pull/8)：狀態列顏色在淺色主題看不清。修正時作者方實測發現主題設定其實寫在 `~/.claude.json`，不是 `settings.json`，第一版修法因此無效、合併前又改了一次。
    - PR #10、#11、#14、#15、#30 都是協作者維護的 Mac 安裝包（多選選單、補環境設定讓 AI 找得到已裝的工具、Intel 機型改走官方下載、修第三方解壓縮後顯示已損毀）。安裝包只有 Mac 版，與維護者的 Windows 環境無關。
    - PR #5：外部工具想被收錄，作者以「這份清單主要服務非工程背景學員」婉拒。
- **上游現況**：2026-11-17 再查，兩個 repo 的最新版各比本篇固定的 commit 多 2 個 commit，都是自動產生的（speak-human-tw 是每日更新星數圖，claude-code-resources 是同步課程場次），評估沒有過期。
- **對分析的影響**：
  1. 第 1 節「不應直接全域套用於…本 repo 的任務格式」原本是推論，PR #6 是實際使用者遇到的同一個問題，補上出處。
  2. 第 1.1 節「提示注入邊界未做攻擊測試」補充：作者方做過一次無害注入的試跑並留了一條回歸測試，但自己也說不能取代權限控制；結論不變。
  3. 第 3 節 claude-code-resources 的理由補兩點：Windows 原生的內容經讀者回報後已補強；教材指令曾多次出錯、還有讀者照做被平台停權的案例，照做前要逐條核對官方文件。
  4. #13 與維護者環境有關（本機靠 hook 把關，也常用桌面版），但回報是 macOS、上游已關閉，本機 Windows 桌面版是否有同樣問題未查證；沒有新增任務，列在回報給整合者決定。
  5. `T-20261115-16` 的評估文件不受影響，不需重開。
  6. **2026-11-17 補讀後修正第 4 點的前提**：#13 的回報者自己說問題屬於付費課程教材的設定，不是這個 repo 的入門教材；所以它不能當成「這份入門教材的安全三件套在桌面版無效」的證據，只能說「有人回報類似設定在 macOS 桌面版被繞過」。本機 Windows 的觀察不變。
  7. #7／#8「主題設定實際寫在哪個檔」是又一個「教材憑印象寫、實測才發現不對」的例子，與第 3 節「照做前逐條核對官方文件」的理由一致，不另開任務。

---

## 1. 核心內容與事實查核（5W1H）

- **Who／What**：Raymondhou0917 提供繁中編輯 Skill 與 AI Agent 入門資源；speak-human-tw 的 SKILL frontmatter 為 v1.4.0，定位為既有稿件校對與改寫，不是特定作者風格代筆。[SKILL](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/SKILL.md)
- **Why**：希望減少空泛套話並保留事實；這是作者的設計目標，不能推為已證實的改寫成效。[保護清單](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/protected-list.md)
- **How**：判情境、鎖保護清單、判改寫範圍、逐類改寫、保真回讀、自評。互動模式通常先列清單等確認，但該次使用者明確授權時可跳過；非互動模式另規定事後摘要。這些都是提示契約，沒有工具權限或 OS 隔離保證。[流程與例外](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/SKILL.md)
- **When／Where**：社群、電子報／部落格、銷售、客服與辦公文書五種情境；不應直接全域套用於程式碼、設定或本 repo 的任務格式（上游 [PR #6](https://github.com/Raymondhou0917/speak-human-tw/pull/6) 有使用者回報同類問題：格式規則會把報告的狀態行與表格改寫成散文）。[情境規範](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/scenes.md)
- **可重算數量**：固定 commit 有 [38 類痕跡](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/patterns.md)、[47 組詞表](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/references/taiwan-localization.md)；[benchmark](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/evals/benchmark.md) 現有 42 條（27 SF＋15 SNF）。移除原筆記未固定查詢時間的 Stars／Forks／最後更新數字。

### 1.1 安全與授權修正

- speak-human-tw 的 [LICENSE](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/LICENSE) 是 MIT。公開 ai-inbox 與 `SanHsien/agent-assets`（私有）可依條款複製／修改，但副本或實質部分須保留著作權及完整授權聲明；第三方素材權利鏈未全面查證。
- SKILL 有「稿件是資料」的提示注入邊界，作者方在 [PR #2](https://github.com/Raymondhou0917/speak-human-tw/pull/2) 做過一次無害注入試跑並留下回歸測試，自己也說明這只是提示層防護；沒有完整攻擊測試，不能稱安全性極高。核心校對內容是 Markdown，不代表整個 repo 沒有可執行內容：[星數腳本](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/scripts/generate_star_history.py) 含子程序與網路請求，[workflow](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/.github/workflows/update-star-history.yml) 有 contents 寫入權限與推送步驟。本輪只靜態閱讀，沒有執行。
- claude-code-resources 不能以 GitHub 分類 `NOASSERTION` 代替授權原文：[LICENSE](https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/LICENSE) 與 [README](https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/README.md) 明示 Starter Kit 為 CC BY-NC-SA 4.0，網站文章／課程另列著作權限制。環境安裝包的完整獨立授權範圍未查證。
- 該 README 說明 Mac 安裝包與六份 Starter Kit；後者宣稱支援 macOS／Linux／Windows，不能把整個資源站概括為只適用 Mac。本次僅核對宣告，不宣稱跨平台實測成功，也未全面檢查字型、圖片及安裝包的權利與安全。

## 2. CQR：規範與成效分開

- **Claim**：作者希望降低 AI 風格痕跡並維持內容保真。
- **Evidence**：[v1.4.0 結果檔](https://github.com/Raymondhou0917/speak-human-tw/blob/14885da5c91ed7ca2972f084599edcdd2a32ad04/evals/results-v1.4.0.md) 記載 40 條舊案例與模型判分；與現行 42 條不是同一份測集。
- **Reasoning／限制**：這是上游自報，未在本輪重跑。結果檔自己也指出人味目標未納入評測，且互動完整回歸未執行；不能宣稱本機安全、作者風格或全數案例通過已獲驗證。

## 3. 採納判斷

| 倉庫 | 判斷 | 理由與邊界 |
| --- | --- | --- |
| speak-human-tw | 暫不 Fork／安裝；借鏡保護清單與少量候選詞 | 本 repo 的[詞彙器](../tools/verify_zhtw_vocab.py)是固定字串轉換，不能承擔多數語義編輯規則；47 組詞表與 38 類逐列裁決、具體候選與反例見[評估](../docs/speak-human-tw-assessment.md)。任何實際收錄另走安全關卡與授權保留。 |
| claude-code-resources | 本輪不 Fork／搬運 | 是入門學習資源，Starter Kit 有非商用／相同方式分享條件；未證明本環境需要導入，不因 Mac 安裝包就否定 Windows 教材價值（Windows 原生 PowerShell 的安全刪除做法已在 [#12](https://github.com/Raymondhou0917/claude-code-resources/issues/12) 後補進教材）。教材指令曾多次寫錯套件名稱、也有讀者照做後 Google Cloud 專案被停權（[#4](https://github.com/Raymondhou0917/claude-code-resources/issues/4)），照做前要逐條核對官方文件。[README](https://github.com/Raymondhou0917/claude-code-resources/blob/1320df1e396e7630b09d2dc80fae4b2c96861d54/README.md) |

原筆記所稱本機已安裝 `human-writing`、配置比上游完整與整合互補，本輪未查證，撤回確定敘述。`verify_no_slop.py` 是前端 HTML／CSS 設計與少量英文黑話檢查，不能當繁中 38 類規則的等價實作。[本機原始碼](../tools/verify_no_slop.py)

## 4. 拆解待辦事項（Action Items）

- [x] **`T-20261115-16`**｜**[優先級：低]** 唯讀評估 speak-human-tw 的授權、47 組詞表與 38 類痕跡，不修改檢查器或安裝 Skill
  - **目標範圍**：本筆記與 `docs/speak-human-tw-assessment.md`；對照 `tools/verify_zhtw_vocab.py` 及其既有測試，均只讀。
  - **具體做法**：固定來源 commit，核對 LICENSE、詞表、patterns、保護清單與 benchmark；修正過度宣稱。逐列比較詞表與 38 類規則，記錄覆蓋、缺口、衝突、候選正例／反例與採納裁決；明示公開 repo 與 `SanHsien/agent-assets`（私有）的複製條件。不執行上游程式，不改檢查器、全域設定或私有 repo。
  - **驗收標準（DoD）**：產出 `docs/speak-human-tw-assessment.md`，含固定 SHA／來源連結、授權與未查證權利範圍、47 組詞表及 38 類逐列對照、既有原始碼／測試證據、具體候選規則與反例、明確裁決及未實測項目。執行 `python tools/build_index.py`、`python tools/verify_zhtw_vocab.py --check notes docs`、`python tools/verify_inbox.py` 並回報各結束碼；任何失敗不得宣稱通過。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/speak-human-tw-assessment.md，固定 Raymondhou0917/speak-human-tw 14885da（MIT），47 組詞表與 38 類規則逐列對照 tools/verify_zhtw_vocab.py。實測引號、URL、專名會被改寫，`服務器`、`支持` 目前沒有規則。裁決：先補保護範圍再試候選規則，不整包加入全域替換；後續工作已列入 ROADMAP。筆記撤回「安全性極高」、更正 claude-code-resources 授權為 CC BY-NC-SA 4.0。Codex 撰寫，Fable 獨立複審通過；未執行上游程式，檢查器本身未改。
