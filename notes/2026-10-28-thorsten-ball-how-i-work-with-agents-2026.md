---
id: 2026-10-28-thorsten-ball-how-i-work-with-agents-2026
title: "編譯器專家 Thorsten Ball 的 15 條 Agent 工作實戰哲學：無可辯駁證據、SDLC 端到端可視與爆破半徑審查解構"
source_url: "https://www.facebook.com/share/p/19Fvzd8btQ/"
source_platform: "Facebook (ChatGPT 生活運用) / X (@thorstenball)"
author: "Thorsten Ball (Amp /《Writing An Interpreter In Go》作者) / Maple Kuo (翻譯)"
analyzed_at: 2026-10-28
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "工程紀律與設計審查"
short_title: "Thorsten Ball 15 條 Agent 實戰哲學"
source_review: full
source_reviewed_at: 2026-11-18
source_images: 1
source_replies: 264
tags:
  - thorsten-ball
  - agent-philosophy
  - irrefutable-evidence
  - blast-radius
  - sdlc-observability
  - context-compaction
  - async-dispatch
---

# 編譯器專家 Thorsten Ball 的 15 條 Agent 工作實戰哲學：無可辯駁證據、SDLC 端到端可視與爆破半徑審查解構

- **來源連結**：[Facebook 社團分享 (ChatGPT 生活運用)](https://www.facebook.com/share/p/19Fvzd8btQ/) ｜ [X 原文 (@thorstenball)](https://x.com/thorstenball/status/2114386050638336082)
- **核心作者**：Thorsten Ball（知名開源技術書籍《Writing An Interpreter In Go》與《Writing A Compiler In Go》作者，現任 AI Coding Agent 團隊 **Amp** 核心工程師）
- **中文編譯**：Maple Kuo
- **分析主題**：2026 年 10 月前沿主線代碼完全由 Agent 接管後的思維範式轉變、無可辯駁證據（Irrefutable Evidence）、爆破半徑審查（Blast Radius Review）、讓整個 SDLC 對 Agent 透明可視、知識庫 A/B 盲測實驗
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md)（Karpathy 四大黃金原則工程加固）
  - [`notes/2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md`](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md)（SpaceX 首席工程師 pstack 方法論）
  - [`notes/2026-10-26-ai-shared-memory-template-team-collaboration.md`](./2026-10-26-ai-shared-memory-template-team-collaboration.md)（三跳索引與動詞寫入契約）
  - [`notes/2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md`](./2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md)（確定性交付與外部裁判）

---

## 0. 原始資料盤點

> 2026-11-16 重審：Facebook 社團貼文（文字、留言）與 X 原文（文章全文、封面圖）都看過。
>
> 2026-11-17 補讀：登入後讀 X 原文的回覆串，以預設排序捲到底並展開「疑似垃圾訊息」區，讀到 232 則（計數 275）。各串底下收合的子回覆沒有逐一展開，所以仍記為 `partial`。
>
> 2026-11-18 第二次補讀：X 回覆改用「相關」「最新」「按讚數」三種排序各捲到底，並把每一則帶回覆數的留言（62 則）逐一點進去看子回覆。**貼文計數 275 則，平台顯示 263 則已全部讀完（作者自己 20 則），差 12 則登入後也不顯示**；62 個子回覆頁沒有冒出任何主串沒顯示的回覆。加上 Facebook 的 1 則，合計 264 則。另外把作者第一則回覆給的「更長版本」連結追到底：是一支 34 分半的 YouTube 影片〈How Thorsten Ball Uses Amp, October 2026〉（Amp 官方頻道，2026-10-14），已抓英文字幕全文讀完。

- **作者圖片**：Facebook 貼文沒有圖。X 原文只有 1 張文章封面圖：淡綠漸層背景上一顆帶放射線的灰色金屬球，純裝飾，沒有資訊。
- **作者留言補充**：Maple Kuo 在留言區補上原文標題〈How I work with Agents〉與 X 連結，沒有其他補充或勘誤。
- **網友留言重點**：Facebook 貼文除譯者自己那則外沒有其他留言。X 回覆 2026-11-16 未登入讀不到；2026-11-17 登入後讀到 232 則，其中約三成是請機器人翻譯、摘要或收藏的指令與灌水留言，有內容的整理如下。
  - **作者自己在回覆裡的補充**（Thorsten Ball）：
    - 開頭自己留言說另有一個更長、更深入的版本並附連結。2026-11-18 查到是 [YouTube 影片〈How Thorsten Ball Uses Amp, October 2026〉](https://www.youtube.com/watch?v=Z7l1EHfCMU8)（34 分半），是他到一家大型銀行客戶現場講的同一份內容。讀完字幕後，比 X 短文多出的事實：
      - **背景條件**：Amp 是單一 TypeScript monorepo、超過 200 萬行、自稱 99% 由 AI 寫成；全員直接推 main、**沒有 PR**，靠自家人天天用、功能旗標與 Agent 看得到線上狀態來兜底；設計師也直接改程式碼、不再用 Figma；本機開發已全面改成每個對話一台用完即丟的雲端機器。短文的 15 條是建立在這些條件上的。
      - **「讓 Agent 看得懂整個流程」的實際規模**：repo 裡有 15 份 AGENTS.md，各自說明怎麼操作不同部位；另有開發伺服器、雲端監控、部署、資料倉儲等技能。他特別說不要只寫固定流程，要給工具並解釋工具怎麼用。
      - **線上資料專門留一份給 Agent**：把線上出過問題的最大幾個對話串去識別化後放進正式環境當金絲雀樣本，只給 Agent 驗證用。這就是他回覆裡「要用正式環境的金絲雀」的出處。
      - **不用便宜模型的理由是實測**：他拿另一個較便宜的模型試「啟動開發伺服器」，模型來回試了好幾輪才找對指令，最後花的 token 反而更多。但他也說，分類、路由這類工作量固定的用途，選「通過評測的最便宜模型」是對的。
      - **盲測 Agent 的做法**：改完 AGENTS.md 後叫 Agent 自己開 5 到 10 台全新機器、用不同問法測新規則有沒有被遵守，並自己加對照組；通過才出貨，測完把評測對話封存。
      - **審查時問自己的問題**：能不能動、我懂不懂它怎麼運作、做法對不對、有沒有 bug、一個月後我知不知道要怎麼請它改。越靠系統邊緣容錯越高，「CSS 錯誤和壞掉的資料庫遷移不是同一回事」。
      - **在正式環境測試**：小改動包在功能旗標後面直接上線、只對自己開啟，再讓 Agent 另開機器重現問題；旗標授權要人按同意。
      - **不讓 Agent 寫給人看的文字**的界線講得更清楚：事故報告、文件、教使用者設環境變數這類「對方不在乎是誰寫的」機械性文字可以交給 Agent。
    - 「把『這不算證據』寫進 AGENTS.md」的意思：要校準 Agent 什麼才算真的證據。他舉的例子是本機記憶體內的資料庫不能當成正式環境效能的證據，應該用正式環境的金絲雀流量；兩位網友問是不是只寫那一句話，他的回答是要寫明哪些東西不算。
    - 不手動整理 context：他說完全不想這件事，讓工具自己壓縮；被問到成本時說不在意，認為盯著 token 計數沒有幫助。
    - 排程與心跳類的對話串會淹沒在功能開發的對話串裡，他的做法是設成「有新回覆才叫醒」。
    - 新模型一出就試，因為這是他的工作；被問到「讀正式環境」與「動正式環境」是否該分開權限，他回答本來就不是同一個權限。
    - 需要手機模擬器的工作仍用自己的機器當執行端。
    - 2026-11-18 補讀到的作者回覆：(1) 對「記下 Agent 被要求做什麼、實際改了什麼，再挑可疑步驟審」的建議，他回「浪費時間」；被追問後說明：因為不信任而去追蹤它每一步再逐項核對才是浪費，前提是你用得起更好的模型。(2)「在單一 Storybook 裡測過」也不算整合後能動的證據。(3) 被問 context 累積到九十萬 token 怎麼辦，他說現在有自動壓縮、會在出問題前先壓，已經不再想這件事。(4) 被 rsms 質疑遠端開發機慢，他說啟動一台約 14 秒，開發環境在 Agent 開工的同時背景啟動，沒成為問題；並說 Apple 平台支援快好了。
  - **反對與保留意見**：
    - 成本：rsms 說用最新模型很快就貴到不合理，他上個月一次衝刺光 token 就花了四萬多美元，大公司可以、個人不行；另有多則留言說前提是錢夠。作者回覆承認有些人會因價格被排除在外。
    - 「別擔心累積爛程式碼」是被反駁最多的一條：LalitMaganti、nickchecan、simo73884 都說變數命名可以不管，但系統設計層面照單全收會出問題，功能正確不等於架構可維護。作者沒有回覆這幾則。
    - 壓縮：Drk8_、bidah、johnroodepic 認為自動壓縮仍會掉資訊，被排除的方案最容易在摘要時消失，而那正是事後無法重推的部分。
    - 「對話串就是公司記憶」：LambrosPetrou 刻意不在 commit 放對話連結，重要脈絡應寫進註解與 repo 文件；cristianducu 說決策要能在對話串之外存活，否則得永遠留著同一個工具。
    - 證據：rwzheng 提醒不能讓 Agent 自己決定什麼算證據；m0rtitech 說 Agent 會改測試讓 CI 變綠，測試要放在它碰不到的地方；samuelpiatanesi、aventarion 主張寫程式的模型不審自己的程式，換一個沒看過解釋的新 Agent 從原始錯誤回報驗證。
    - 影響範圍：elissasa 問不先看怎麼知道影響範圍小；datachad、super_puppet_ 認為會送錢、寄信、改權限與部署設定的變更即使不在核心檔案也該人審。
    - 模型版本：themuscleai 說要出貨的工作應固定模型版本，新模型先並排評測再換；Maverick4407 說再強的模型錯誤率也不只一成，系統本來就該能從錯誤恢復。
    - dkraks 指出「不要讓 Agent 寫給人看的東西」與「要它產出走查與示範影片當證據」之間有矛盾，作者沒有回覆。
  - **實作回報**：Macfeecn 的證據標準是「我自己能重跑的指令」而不是 Agent 貼的 log；asuka_omen 要 Agent 說清楚是哪一種完成（寫好附路徑、測過附指令與輸出、上線附網址）；Alex_Vainshtein 做遊戲時測試全過但畫面是錯的，改成在目標裝置錄實際畫面檢查；real_brahimg 的排程工作另加一個檢查其他工作有沒有跑的看門工作，因為漏跑不會出聲；stas_sorokin_ 量到同一個小 repo 單一 Agent 12.5 秒、開 4 個子 Agent 27 秒。
  - **2026-11-18 補讀到的網友留言**（多在「最新」排序才出現）：AvatarRadu 對正式環境的工作要三張收據：已提交的變更、正在跑的版本、使用者看得到的行為；varunmundra5 遇過備份還原回來是零筆資料卻仍回報成功，因為「還原有跑」被當成證據；arunimastwt 建議偶爾餵 Agent 惡意輸入（被下毒的 README、惡意的工具回傳）看它的真實邊界；memokris 建議盲測再加第三組：放一份與新規則衝突的舊規則，看 Agent 分不分得出哪個還有效；iam_mykelking 稱讚「一次要 20 個變體加一頁測試頁」的做法。其餘是附和「不知道哪一成是錯的」與要機器人翻譯、收藏的指令，沒有新的反駁。
- **對分析的影響**：對照 X 英文原文後改了三處轉述，都不影響已完成的三份產出檔（三份文件已各自標明哪些是原文、哪些是本 repo 延伸）：
  1. 第 9 條原文是「Agent 很擅長產出證據（端到端走查、示範影片、前後數字）」，是正面陳述；原筆記寫成「Agent 擅長產生看起來像修好的幻覺承諾」，方向寫反了，已改。四條「無效證據黑名單」是本 repo 的延伸，原文只有一句「把『這不算證據』寫進 AGENTS.md」，已標明。
  2. 第 15 條原文是「核心檔案不到 5 個（<5），那些我會審」，講的是作者自己的程式碼庫，不是通用門檻；原筆記寫成「核心 ≤ 5 檔案法」，已改。原文結尾是「四題都答是，才可能去看程式碼」（If yes, might review code），原筆記寫「直接放行」，已改成照原文並註明字面有歧義。
  3. 第 6 條原文只說「開五個盲測 Agent 分對照組與實驗組看看」，沒有「統計顯著」「果斷刪除」；那是本 repo 的延伸，已標明。
  4. 2026-11-17 讀 X 回覆後：(1) 作者對「這不算證據」的解釋（要寫明哪些東西不算、記憶體內資料庫不能代表正式環境）與本 repo 黑名單的方向一致，黑名單仍是本 repo 的延伸，但不再只有原文一句話當依據。(2) 第 9 條與第 15 條的轉述不需再改。(3) 留言對「別擔心累積爛程式碼」「自動壓縮」「對話串當記憶」三條有具體反對意見，原筆記只轉述作者主張，已在第 3 節補一條「採用時的保留」。(4) 三份已完成的產出檔抽查後不需更正：證據規範已把記憶體內假資料列為無效證據，審查指南已把金流、憑證、權限設定列為必須人審。不新增任務。
  5. 2026-11-18 讀完全部回覆與作者的長版影片後：(1) 原文 15 條的適用前提要寫清楚：作者的團隊沒有 PR、全員推 main、每個對話一台雲端機器、有功能旗標與線上監控給 Agent 看。**沒有這些條件就照抄「只審核心檔案」「別擔心爛程式碼」，風險不同**；已在第 3 節「採用時的保留」補一條。(2)「不用便宜模型」不是全稱：作者自己說工作量固定的分類與路由可以用通過評測的最便宜模型，與本 repo 的分層派工做法不衝突。(3) 留言的三張收據、零筆資料的還原、Storybook 不算整合證據，都是「這不算證據」的具體例子，與本 repo 的黑名單方向一致，三份已完成的產出檔不需更正。

---

## 1. 核心內容摘要：Thorsten Ball 的 15 條 Agent 實戰哲學（Key Insights）

作為頂級系統編譯器專家與 Amp 團隊一線實踐者，Thorsten Ball 在 2026 年 10 月全面復盤了他將日常主線開發與完整軟體開發生命週期（SDLC）交由 Agent 接管後的關鍵思維躍遷：

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   Thorsten Ball 15 條 Agent 實戰思維躍遷矩陣                           │
├───────────────────────────────┬────────────────────────────────────────────────────────┤
│ 核心維度                      │ 顛覆性實戰洞察 (Core Practice Shift)                   │
├───────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. 模型選型                   │ 永遠用最新、最強大的模型；別雇用便宜 50% 但隨機變笨的。│
│ 2. 代碼品質                   │ 別再擔心垃圾代碼（Slop），只要端到端架構能守住即可維護。│
│ 3. 提示詞哲學                 │ 聚焦在「做什麼 (What)」而非「怎麼做 (How)」，給極限目標│
│ 4. SDLC 可視性                │ 讓整個 SDLC 對 Agent 透明可視；它看不到就會瞎編。      │
│ 5. 工具配備                   │ 為它打造貫穿部署、日誌、Feature Flag 與客訴排查的工具。│
│ 6. 知識評估                   │ 用 A/B 盲測 5 個 Agent，驗證 AGENTS.md 與 Skills 是否真有用│
│ 7. 開發環境                   │ 本機開發很蹩腳（Clunky），遠端隔離沙盒讓多 Agent 平行跑│
│ 8. 試錯方法                   │ 不要跟著它一步步試錯，讓它自己打造 20 種變體的試錯工具 │
│ 9. 交付信任                   │ ★ 要求無可辯駁的證據！在 AGENTS.md 寫明「哪些不算證據」│
│ 10. 交互節奏                  │ 別等 Agent，讓它等你；全面擁抱非同步，交付龐大批次工單 │
│ 11. 長程維護                  │ 自動化／排程／定時喚醒／心跳檢測（Heartbeat）是殺手級。│
│ 12. 上下文哲學                │ 別手動算 token；Compaction 效果極佳；一對話串對應一任務│
│ 13. 公司記憶                  │ 對話串直接與 Git Commits 關聯，就是全公司累積的活記憶。│
│ 14. 寫作邊界                  │ 不要讓 Agent 寫給人看的文字；只讓它寫除錯、事故檢討文檔│
│ 15. 審查邊界                  │ ★ 只審查影響範圍（Blast Radius）大的代碼（核心 < 5 檔） │
└───────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. 深入技術拆解：三大最具衝擊力的實戰工程實踐（Deep Dive）

在 Thorsten Ball 的 15 條實戰哲學中，有三大實踐對當前多 Agent 協同體系具有決定性的指導價值：

### 2.1 實踐一：要求「無可辯駁的證據（Irrefutable Evidence）」與定義「無效證據黑名單」
- **洞察精華**：
  作者稱這是影響最大的改變。原文的說法是正面的：Agent **很擅長產出證據**——端到端走查、示範影片、前後數字——所以直接向它要；人這邊要做的是培養對證據的信任與直覺。
- **神級建議**：**「記得在你的 `AGENTS.md` 裡寫上：『這些不算有效證據』」**。
  - 目前多數專案只寫「請提供測試證據」，結果 Agent 丟出一句「單元測試已全部通過」或自己 mock 了一段假資料，就聲稱是證據。
  - 以下四條**無效證據黑名單**是本 repo 的延伸，原文只有「把『這不算證據』寫進 AGENTS.md」一句：
    1. 自行宣稱的口頭文字斷言（「已修復完畢」）；
    2. 註解掉報錯測試後的綠燈輸出；
    3. 沒有涵蓋本機外部進程、只在記憶體 mock 的假資料；
    4. 未貼出完整指令與真實 exit code 的片段輸出。

### 2.2 實踐二：只審查「影響範圍（Blast Radius）」大的代碼（作者的核心檔案不到 5 個）
- **洞察精華**：
  許多人類工程師對 AI 代碼的審查卡在微觀細節：閉包還是類別、型別寫得漂不漂亮、命名語意、甚至代碼重複。Thorsten 認為這完全是傳統時代的心理包袱。
- **審查標準重構**：
  - 作者只審查**爆破半徑（Blast Radius）**大的部分：他的程式碼庫裡核心檔案不到 5 個（原文 `<5`，是描述自己的專案，不是給別人用的門檻），加上資料庫遷移檔。「權限安全性核心」是本 repo 的延伸，原文沒提。
  - 其餘程式碼他問四題：**能正常跑嗎、架構箭頭層次看得懂嗎、Agent 有跑過端到端測試嗎、一個月後還能改嗎**。原文結尾是「If yes, might review code」，字面是「都答是才可能去看程式碼」；[`docs/blast-radius-code-review-guide.md`](../docs/blast-radius-code-review-guide.md) 把它解讀成「四項皆是就免逐行審查」並註明這是解讀。

### 2.3 實踐三：對照組與實驗組「A/B 盲測」評估 `AGENTS.md` 與 Skills 真實價值
- **洞察精華**：
  許多開發者熱衷於在專案中累積數十支 Skills、寫滿上千行 `AGENTS.md`，但從未驗證過這些知識到底是真的提升了成功率，還是只是在浪費 Context 並造成注意力稀釋？
- **實戰做法**：
  同時啟動 5 個盲測 Agent，分成「未掛載該 Skill（對照組）」與「掛載該 Skill（實驗組）」，執行同一批邊界任務。原文只講到「分對照組與實驗組看 Agent 到底有沒有用這些知識」；「沒有統計顯著提升就刪除該文件」是本 repo 的延伸。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`agent-assets` 與 `ai-inbox`）的對照**：
  - 我們全域規則中的「回報完成之前，要真的執行過檢查並貼出它的真實輸出」與 Thorsten 的理念完全一致。
  - 但我們尚未正式定義「無效證據黑名單」，也缺乏「爆破半徑自動計算器」與「知識 A/B 盲測機制」。

- **採納與落地行動**：
  1. **規格化「無可辯駁證據與無效證據黑名單」**：將口頭承諾、吞掉例外、假資料等明確列為不合格證據，收錄於 `docs/irrefutable-evidence-and-invalid-patterns-spec.md` 並更新全域指引。
  2. **制定「爆破半徑審查指南」**：定義核心 5 檔案原則與 Migration 審查標準，收錄於 `docs/blast-radius-code-review-guide.md`。
  3. **設計「知識庫 A/B 盲測實驗協議」**：為後續評估複雜 Skill 與長規則提供客觀盲測標準，收錄於 `docs/agents-knowledge-ab-test-protocol.md`。

- **採用時的保留（2026-11-17 依 X 回覆補）**：
  - 「一律用最新最強的模型」有成本前提，作者自己在回覆裡承認有人會被價格排除；要出貨的工作也有人主張固定模型版本、先並排評測再換。
  - 「別擔心累積爛程式碼」在系統設計層面被多位回覆者反駁，作者沒有回應；本 repo 不照單採用這一條。
  - 「不手動管 context、交給自動壓縮」：回覆指出摘要最容易丟掉被排除的方案；重要決策仍要寫進 repo 文件，不能只留在對話串。
  - 證據要是自己能重跑的指令，而且測試不能由被驗的 Agent 自己改；這與本 repo「驗證不自驗」的既有規則一致。
  - **適用前提（2026-11-18 依作者長版影片補）**：這 15 條出自一個沒有 PR、全員直接推 main、每個對話一台用完即丟的雲端機器、有功能旗標且讓 Agent 讀得到線上監控的團隊。「只審核心檔案」靠的是出錯能很快被看到、很快修掉；沒有這些條件的 repo 不能只抄結論。作者也說工作量固定的分類、路由可以用通過評測的最便宜模型，「一律用最強模型」指的是開放式的開發工作。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261028-04`**｜**[優先級：高]** 撰寫「無可辯駁證據（Irrefutable Evidence）與無效證據黑名單規範」收錄於 `docs/irrefutable-evidence-and-invalid-patterns-spec.md`
  - **目標範圍**：`docs/irrefutable-evidence-and-invalid-patterns-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 定義「無可辯駁證據」的三大支柱：端到端真實進程日誌、外部裁判 Exit Code 0、前後指標對比。
    2. 制定「無效證據黑名單（Invalid Evidence Blacklist）」，嚴格定義口頭承諾、吞例外、註解測試、假資料與截斷日誌等不可作為完成依據的反模式。
    3. 提供可在 `AGENTS.md` 一鍵引入的防衰減規則片段。
  - **驗收標準（DoD）**：產出 `docs/irrefutable-evidence-and-invalid-patterns-spec.md`，內含有效證據契約、黑名單列表與 AGENTS.md 整合範例；以 `Test-Path docs/irrefutable-evidence-and-invalid-patterns-spec.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：docs/irrefutable-evidence-and-invalid-patterns-spec.md：證據分級、14 條黑名單與可貼的 AGENTS.md 片段；對照 Thorsten Ball 原文，作者說的與本 repo 延伸分開，黑名單依據區分 REVIEW.md 有紀錄與常見模式整理。獨立審查核對引述與紀錄行號。

- [x] **`T-20261028-05`**｜**[優先級：中]** 撰寫「爆破半徑審查（Blast Radius Review）與核心 5 檔案門檻指南」收錄於 `docs/blast-radius-code-review-guide.md`
  - **目標範圍**：`docs/blast-radius-code-review-guide.md`
  - **具體做法**：
    1. 定義高風險爆破半徑模組（核心架構 <= 5 檔、資料庫遷移檔、授權憑證層）。
    2. 制定低風險業務代碼的「免微觀審查四條件」（正常運行、架構清晰、端到端測試通過、可維護性）。
    3. 結合 `git diff --stat` 提供自動劃分審查梯隊的評估手冊。
  - **驗收標準（DoD）**：產出 `docs/blast-radius-code-review-guide.md`，內含爆破半徑評估樹與審查檢查清單；以 `Test-Path docs/blast-radius-code-review-guide.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：docs/blast-radius-code-review-guide.md：T1／T2／T3 評估樹與 git diff 指令（bash、PowerShell 皆實跑），核心檔案統一判 T1；「核心 5 檔」標明是本 repo 取捨，不是原文主張。獨立審查 PASS。

- [x] **`T-20261028-06`**｜**[優先級：低]** 撰寫「AGENTS.md 與 Skills 知識有效性 A/B 盲測實驗協議」收錄於 `docs/agents-knowledge-ab-test-protocol.md`
  - **目標範圍**：`docs/agents-knowledge-ab-test-protocol.md`
  - **具體做法**：
    1. 設計多 Agent 對照組（無 Skill/規則）與實驗組（掛載 Skill/規則）的平行盲測流水線。
    2. 制定評估指標：任務成功率、Token 消耗比、修正回合數（Turns）與代碼純淨度。
    3. 建立淘汰冗餘規則與過期 Skills 的客觀標準，防止知識庫腐蝕。
  - **驗收標準（DoD）**：產出 `docs/agents-knowledge-ab-test-protocol.md`，涵蓋實驗流程圖、評估指標公式與盲測指令範本；以 `Test-Path docs/agents-knowledge-ab-test-protocol.md` 驗證存在。
  - **完成日期**：2026-11-02
  - **實作紀錄 / 證據**：docs/agents-knowledge-ab-test-protocol.md：10 任務 60 次的盲測設計、精確二項與 Fisher 檢定（審查獨立重算相符）、作廢條件與兩支 bash 範本。用假 Agent 實跑確認破盲已堵、路徑錯與空任務 exit 2、基礎設施失敗超標 exit 1。門檻標為設計估計，尚未用真實 Agent 跑過。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **規範工程與黃金原則**：
  - [Karpathy 版 CLAUDE.md 四大黃金原則工程加固](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md) ｜ 關聯任務：`T-20261028-01`、`T-20261028-02`
- **SpaceX 首席工程師工作流**：
  - [pstack 方法論：一週 2000 個 PR 的自動化驗收](./2026-10-18-pstack-spacex-engineer-ai-coding-workflow.md) ｜ 關聯任務：`T-20261018-17`、`T-20261018-18`
- **防腐蝕與知識管理**：
  - [AI 共用記憶系統全景分析](./2026-10-26-ai-shared-memory-template-team-collaboration.md) ｜ 關聯任務：`T-20261026-23`、`T-20261026-24`
- **確定性交付與自動化 DoD**：
  - [AI 接案的確定性交付工程](./2026-10-26-ai-freelance-certainty-pricing-and-dod-spec.md) ｜ 關聯任務：`T-20261026-32`、`T-20261026-34`
