---
id: 2026-11-14-gpt-6-1-terra-codex-work-quota-fast-mode-routing
title: "GPT-6.1 Terra 額度與 Fast 倍率核實：Plus 約 Sol 的 2 倍、Fast 2.5x，但整體額度並未增加"
source_url: "https://learn.chatgpt.com/docs/pricing"
source_platform: "OpenAI 官方文件（使用者提供線索，未附原始出處）"
author: "使用者提供 + 官方頁核實"
analyzed_at: 2026-11-14
analyzed_by: "Antigravity"
status: done
cluster: "1"
cluster_role: "Terra額度路由"
short_title: "Terra額度與Fast倍率核實"
source_review: partial
source_review_note: "原貼文搜尋不到（試過：Threads 站內搜尋「Terra Fast 2.5」、Facebook 貼文搜尋「GPT-6.1 Terra Fast 2.5x Plus 額度」「Terra 額度 Sol 2 倍 Fast 2.5 Codex」；沒有內容吻合的貼文）；替代來源官方文件頁全文已讀完（無圖、無留言區）。2026-11-18 第二輪：找到一篇四個說法都對得上的中文文章（MapleFeather〈GPT-6.1 Terra vs Sol 額度差多少〉，更新於 2026-11-04），全文讀完，沒有內文圖、沒有留言區；但線索寫「額度增加」，文章明寫整體額度沒有變多，用詞也不同，不能認定線索就是出自這篇，原貼文仍不明。另試過沒有吻合結果的管道：網頁搜尋（中英文）、Threads 站內搜尋四組關鍵字、X 站內搜尋、文章作者的 Threads 個人頁近期貼文、Hacker News。兩則相近的 Threads 貼文（10-27、11-01）已進貼文讀完文字與留言（1／1 則、16／19 則，兩種排序都捲到底），都對不上，其中一則的 3 分鐘影片沒看到。各候選貼文與文章網址另查了 Wayback（availability API）與 archive.ph，都沒有存檔；Reddit 查不了（內建瀏覽器擋 reddit.com、網頁搜尋工具不能限定該網域、直接請求被擋）；2026-11-18 改派 Codex 用網頁搜尋限定 Reddit 查 9 組關鍵字，找到 r/codex 6 則相關討論（見第 0 段），沒有一則四項說法都對得上，不是線索來源"
source_reviewed_at: 2026-11-18
source_images: 0
source_replies: 17
tags:
  - gpt-6-1-terra
  - codex
  - chatgpt-work
  - usage-limits
  - fast-mode
  - model-routing
  - cost-control
---

# GPT-6.1 Terra 額度與 Fast 倍率核實

## 0. 原始資料盤點

> 2026-11-18 第二輪（找轉引與存檔）：**找到一篇四個說法都對得上的文章，但不能認定線索出自它；原貼文仍不明，維持 `partial`。**
>
> - **最接近的來源**：MapleFeather（作者夜羽凌）〈[GPT-6.1 Terra vs Sol 額度差多少？約 2 倍、點數砍半](https://maplefeather.com/article/gpt-6-1-terra-usage-limits-2026)〉，頁面只標更新日期 2026-11-04。全文讀完；內文沒有圖（只有延伸閱讀的縮圖），沒有留言區。
> - **對得上的地方**：文章開頭的四點摘要與線索逐條對應：Plus 在 Work、Codex 約為 6.1 Sol 的 2 倍；別開 Fast，額度扣 2.5 倍；看圖、填表、寫提案換 Terra；難的程式留給 Sol。
> - **對不上的地方**：線索開頭寫「程式額度增加」，文章卻明寫 Work 與 Codex 的整體額度沒有跟著變多；線索說「日常任務切至 Terra」，文章分得更細（看圖與文書給 Terra、大量整理給 Luna、長時間寫程式留在 Sol、最難的留在 Astra）。線索比較像有人把這類文章再濃縮一次的結果，中間經過誰的手查不到。
> - **兩則相近的 Threads 貼文，進貼文讀完後都對不上**：
>   - `@cooljerrett`（2026-10-27）：<https://www.threads.com/@cooljerrett/post/De-qP71j8is>。對得上兩點：Terra 用量額度是 Sol 的兩倍、最難的程式官方仍建議交給 Sol。對不上：完全沒提 Fast 與 2.5 倍，也沒說只在 Codex 與 Work 提供；主題是速度（填表 53 秒對 3 分 21 秒）與操作 Blender。附 1 支約 3 分鐘的影片，截圖逾時沒看到內容。留言計數 1 則，就是作者續串貼的官方連結，兩種排序都確認沒有其他留言。
>   - `@idontwantthreehigh`（2026-11-01）：<https://www.threads.com/@idontwantthreehigh/post/DfMnlkmFBCG>。主題不同：講的是 12 月起 Codex 與 ChatGPT 聊天改吃同一桶額度，列五件該先做的事。對得上的只有「輕的給 Terra 或 Luna、Sol 留給卡關的」「不急就關 Fast」；對不上：Fast 寫的是「多燒一倍以上」不是 2.5 倍，沒有「Sol 的 2 倍」，也沒有「僅限 Codex 與 Work」。沒有圖。留言計數 19 則，熱門與最新兩種排序都捲到底，合計讀到 16 則（作者續串 1 則、作者回覆 5 則、網友 10 則），差 3 則平台不顯示。留言幾乎都在說要退訂改用別家，沒有人補充或更正額度數字。
>   - 這兩則「共用同一桶」「Pro 200 砍半已撤回」的說法與 MapleFeather 文章一致，但都是第三方說法，本篇未向官方查證。
> - **存檔與 Reddit**：MapleFeather 文章與上面兩則貼文都查了 Wayback（availability API；CDX 介面當天回空白、連一定有存檔的網址也查不到，不採計）與 archive.ph，都沒有存檔。Reddit 查不了：內建瀏覽器擋 reddit.com，網頁搜尋工具不能限定該網域，直接請求也被擋。
> - **這輪試過、沒有吻合結果的管道**：網頁搜尋（繁中兩組、英文一組）；Threads 站內搜尋「Terra Sol 2倍 Fast」「Terra 額度 Fast 2.5」「Terra 別開 Fast」「Terra Plus 額度 Sol 兩倍 Codex Work」；X 站內搜尋「Terra Sol 額度 Fast 2.5」；文章作者的 Threads 個人頁（往回捲到 11-09，沒有 Terra 貼文，更早的沒有再捲）；Hacker News。
> - **對分析的影響**：
>   - 本篇的判定都不用改。文章的數字（35–285、15–160、25／1.25／125、Fast 2.5 倍與點數 2 倍）與本篇從官方頁核對到的一致；文章也寫「整體額度沒有變多」，與本篇「措辭不精確」的判定相同。
>   - 文章補了一個本篇沒寫的算法，可用官方數字自己驗算：**只有 Terra 開 Fast 時，35–285 除以 2.5 是約 14–114 則，比不開 Fast 的 Sol（15–160 則）還少**。也就是線索「切勿開啟 Fast」的理由成立：開了 Fast，Terra 省額度的好處就整個還回去。
>   - 文章另提兩點，是第三方說法，本篇未向官方頁查證：`config.toml` 若已設成預設開 Fast，切到 Terra 也會照開；可能另有週上限，官方沒有公布數字。
>   - 「日常 Terra、高難度 Sol」仍是**未驗證**：文章轉述官方模型建議是 Terra 管日常寫作與看圖、6.1 Sol 管重複的長時間工作，但這是二手轉述，官方 Models 頁本篇仍未讀。
>   - 搜尋時看到多則 2026-11-17 的 Threads 貼文說 OpenAI 已推出 GPT-6.2 Astra 與 Sol（只讀了搜尋結果的首則文字，未向官方查證）。若屬實，本篇與 `docs/model-burn-rate-routing-matrix.md` 第 9 節的 Sol 6.1 對照數字可能已不是現行版本，使用前要重查官方頁。

> 2026-11-18 再找原貼文：原貼文搜尋不到（試過：Threads 站內搜尋「Terra Fast 2.5」、Facebook 貼文搜尋「GPT-6.1 Terra Fast 2.5x Plus 額度」「Terra 額度 Sol 2 倍 Fast 2.5 Codex」；沒有內容吻合的貼文）；替代來源官方文件頁全文已讀完（無圖、無留言區）。維持 `partial`。

> 本篇的來源有兩層：使用者轉貼的一段文字線索（沒有附原始貼文連結，所以沒有作者圖片與留言可看），以及用來核實的官方文件頁。2026-11-16 以瀏覽器重讀官方頁全文。

- **作者圖片**：無。線索是純文字，原始貼文不明；官方頁 <https://learn.chatgpt.com/docs/pricing> 正文沒有圖片，資料都在文字與表格裡（方案卡、每 5 小時訊息數表、速度模式倍率表、credits 單價表、功能可用性矩陣）。
- **作者留言補充**：無（官方文件頁沒有留言區）。
- **網友留言重點**：無。線索的原始貼文沒有提供，無法查看其留言。
- **對分析的影響**：
  - 2026-11-16 重讀官方頁，本篇引用的數字全部仍相符：Terra 35–285、Sol 6.1 15–160（Plus 與 Standard Business 相同）；Terra credits 25／1.25／125、Sol 6.1 50／2.5／250；Fast 訂閱內含 2.5x、credits 2x；Ultrafast 8x／6x；「Overall Work and Codex plan limits are unchanged」與「Terra 不在 Chat 提供」兩句原文都在。
  - 補兩個原稿沒寫的官方細節（不影響結論）：Terra 不支援 UAE 推論落地；Plus 方案卡的模型清單只列 Sol 6.1 與 Luna，Terra 只出現在頁尾的功能可用性段落與矩陣。
  - 沒有需要修正的內容，任務狀態不變。

---
> - **Reddit（2026-11-18，派 Codex 用網頁搜尋限定 reddit.com 查，Claude 的瀏覽器開不了 Reddit；留言以 Codex 取得的 JSON 快照為準，未逐則讀完）**：r/codex 有 6 則相關討論，沒有一則同時有四項說法，不是線索來源；但有幾則**實測反駁「約 2 倍」**：
>   - 〈Allowance table update for GPT & competitors and Terra opinion〉（2026-10-28）：<https://www.reddit.com/r/codex/comments/1xhhrxs/>。作者用 Plus 帳號量測，反駁「Terra 用量是 Sol 兩倍」，並認為 Terra 跑程式任務不可靠；留言提醒 API 半價不等於訂閱額度翻倍。
>   - 〈GPT-6.1 Terra (Medium) burns through usage limits much faster than Sol on the same tasks〉（2026-10-28）：<https://www.reddit.com/r/codex/comments/1xhhzme/>。同類任務 Terra 反而更耗額度；留言有人量到同一任務 Terra 約 60 萬 token、Sol 約 20 萬。
>   - 〈Limits decreased when using 6.1 Terra?〉（2026-10-26，快照 26 則）：<https://www.reddit.com/r/codex/comments/1xgcwoq/>。作者估算 Terra 5 小時額度換成 API 金額比 Sol 少；少數留言認為 Terra low 適合範圍明確的簡單工作。
>   - 〈Terra 6.1 is practically dead on arrival; Luna often beats it〉（2026-10-27，快照 79 則）：<https://www.reddit.com/r/codex/comments/1xgnfmm/>。作者認為 Luna 常更便宜也更快；留言有人支持 Terra 做電腦操作、視覺與 3D 工作。
>   - 〈Fast & Ultrafast are highly questionable.〉（2026-11-07）：<https://www.reddit.com/r/codex/comments/1xq8lm0/>。留言區分「速度倍率」與「額度倍率」，提到 Fast 耗額是標準的 2.5 倍，與官方表一致。
>   - **對分析的影響**：官方表的 Plus 估計區間仍是 Terra 35–285、Sol 15–160，但社群實測（10-26 到 10-28 上線初期）多數覺得 Terra **沒有比 Sol 省，甚至更耗**；本機 9.7 節實測因解析度不足也無法確認倍率。所以「Plus 額度約 Sol 2 倍」只能當官方估計，不能當實際體感；路由仍以「不開 Fast」最確定。

## 1. Executive Summary

使用者提供一則沒有附出處的線索：

> GPT-6.1 Terra 程式額度增加：僅限 Codex 與 Work 介面，Plus 額度約為 Sol 的 2 倍；切勿開啟 Fast（消耗速度快 2.5 倍），建議日常任務切至 Terra，高難度編程再用 Sol。

2026-11-14 讀取官方頁 <https://learn.chatgpt.com/docs/pricing> 逐項核對。結論：**數字大致屬實，但「額度增加」的措辭不精確，「日常 Terra、高難度 Sol」是未驗證的建議。**

| 線索說法 | 判定 | 官方依據 |
|---------|------|---------|
| 僅限 Codex 與 Work | 相符 | Terra 在 Work 與 Codex 提供（Plus、Pro、Business、Enterprise、Edu），不在 Chat |
| Plus 約 Sol 的 2 倍 | 大致相符（粗估） | Plus 每 5 小時本機訊息：Terra 35–285、Sol 6.1 15–160；區間中點 160 比 87.5 約 1.83x |
| 額度「增加」 | **措辭不精確** | 官方：Overall Work and Codex plan limits are unchanged；是多一個每則耗額較低的模型 |
| Fast 快 2.5 倍 | 相符，但限訂閱內含額度 | Fast：訂閱內含 2.5x，購買 credits 與 Enterprise 隨用隨付 2x |
| 日常 Terra、高難度 Sol | **未驗證** | 官方用量頁沒有品質數據；Models 頁本次未讀 |

細節、完整表格與限制見 [`docs/model-burn-rate-routing-matrix.md`](../docs/model-burn-rate-routing-matrix.md) 第 9 節。

## 2. 核實後的關鍵數字

```text
Plus 每 5 小時本機訊息（官方稱估計值，非固定上限）
  Luna 6        350–3,000   ████████████████████████  最高吞吐
  Terra 6.1      35–285     ████████                  約 Sol 的 1.8–2.3x
  Sol 6.1        15–160     ████
  Astra 6         5–45      █

Credits / 100 萬 tokens（輸入／快取輸入／輸出）
  Terra 6.1   25 / 1.25 / 125   → Sol 6.1 的 0.5x
  Sol 6.1     50 / 2.5  / 250

速度模式倍率（相對同模型 Standard）
  Fast                     訂閱內含 2.5x ｜ credits 2x
  Sol 6.1 / Astra Ultrafast 訂閱內含 8x   ｜ credits 6x
```

## 3. 與既有筆記的整合

- 既有速查表只涵蓋 Sol 6.1／Astra 6／Luna 6，現已增補 Terra 與 Fast（第 9 節），其餘章節與查證日維持原樣。
- [`2026-10-26-llm-burn-rate-cache-routing-benchmark.md`](./2026-10-26-llm-burn-rate-cache-routing-benchmark.md) 的實測不含 Terra，已在文首補上指向本筆記的註記，**沒有改動原實測數據**。
- [`2026-11-07-github-copilot-fusion-model-routing-cascade-critique.md`](./2026-11-07-github-copilot-fusion-model-routing-cascade-critique.md) 的留言提到 gpt-6.1-terra 在 Copilot 路由的角色；Copilot 計費與 Codex 額度是不同體系，不可互換。
- [`2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md`](./2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md) 說明 Work 與 Codex 共用額度，與官方頁首句「ChatGPT Work and Codex share usage」一致。
- 依 `T-20261026-02` 的先例（模型名、額度、價格不寫成永久偏好），Terra 數字不寫進共用偏好庫，改以附日期與出處的速查表收錄。

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261114-01`**｜**[優先級：高]** 將 GPT-6.1 Terra 額度、credits 單價與 Fast 倍率核實結果增補進模型速查表
  - **目標範圍**：`docs/model-burn-rate-routing-matrix.md`（只增補第 9 節與標題、來源標記；不改第 1～8 節的數據）
  - **具體做法**：
    1. 讀官方用量頁，逐項核對線索的五個說法並標註相符、粗估、措辭不精確、未驗證。
    2. 補 Terra 對 Sol 6.1 的 Plus 訊息數與 credits 對照，並標明推算方式與區間。
    3. 補 Fast 與 Ultrafast 倍率表，註明 2.5x 僅限訂閱內含額度。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 含「GPT-6.1 Terra 與 Fast 倍率」章節，內有逐項核對表、額度與 credits 對照、Fast 倍率表與未驗證清單；`python tools/verify_inbox.py` 通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：`docs/model-burn-rate-routing-matrix.md` 新增第 9 節（9.1–9.6，約 66 行）。數字取自 2026-11-14 讀取的官方頁：Terra 35–285 對 Sol 15–160、Terra credits 25/1.25/125 對 Sol 50/2.5/250、Fast 2.5x／2x。線索中「額度增加」依官方原文「Overall Work and Codex plan limits are unchanged」標為措辭不精確。

- [ ] **`T-20261114-02`**｜**[優先級：中]** 將「日常用 Terra、高難度用 Sol、不開 Fast」寫入 `SanHsien/agent-assets`（私有）共用偏好庫
  - **狀態**：⚪ 不做（不做：這是未附出處的使用者線索，且品質差異未驗證；模型名、額度、倍率屬會變動的資料，`T-20261026-02` 已確立不寫成永久偏好。數字改以附日期與出處的方式收錄在 T-20261114-01 的速查表第 9 節。）
  - **目標範圍**：`C:\GitHub\agent-assets\knowledge\user_preferences.md`（私有）
  - **具體做法**：
    1. 在模型調度段落補 Terra 與 Fast 的路由紀律。
  - **驗收標準（DoD）**：不執行。
  - **實作紀錄 / 證據**：*（不做，無實作）*

- [x] **`T-20261114-03`**｜**[優先級：低]** 用本機用量儀表板實測 Terra 與 Sol 6.1 的實際耗額與任務品質，回填速查表第 9 節
  - **目標範圍**：`docs/model-burn-rate-routing-matrix.md`（只補第 9 節的實測欄位）
  - **具體做法**：
    1. 選 3 個同類型日常任務，分別用 Terra 與 Sol 6.1 的 Standard 模式完成，記錄開始與結束時儀表板的 5 小時額度百分比。
    2. 對輸出做同一份驗收（測試通過、人工審查），記錄品質差異。
    3. 同一任務各跑一次 Fast，確認 2.5x 是否與儀表板相符。
  - **驗收標準（DoD）**：`docs/model-burn-rate-routing-matrix.md` 第 9 節新增「本機實測」小節，含任務描述、各模式額度消耗與品質結論；沒有實測資料時不得填寫。
  - **完成日期**：2026-11-16
  - **實作紀錄 / 證據**：完成（2026-11-16）：docs/model-burn-rate-routing-matrix.md 新增 9.7「本機實測」，第 0 節新增【本機實測】分級；原始資料、任務、隱藏驗收測試與腳本放在 docs/evidence/terra-sol-burn-2026-11-16/。3 個小任務 × Terra／Sol 6.1 Standard，加上任務 a 兩邊各跑一次 Fast，共 8 次（2 次撞上游 502 已重跑）。結果：品質全部通過隱藏驗收、看不出差異；Standard 每次多半只動 1 個百分點，解析度不足以驗證 Terra 約 2 倍；Sol Fast 一次 5 點、Standard 1 點，Terra Fast 2 點；Sol Fast 這次反而較慢。限制：每組只有 1 次樣本、額度為帳號共用。

## 5. 評估結論

**採用度高（數字可靠），可信度分層：**

- 官方可核實：可用介面、Plus 訊息數區間、credits 單價、Fast 倍率。
- 需修正措辭：整體方案額度沒有增加。
- 未驗證：Terra 日常夠用、Sol 才適合高難度的品質判斷；Terra 開 Fast 是否也是 2.5x（官方表為通則，未列例外，推算成立但未實測）。

操作層面，目前唯一有官方背書的省額做法是：能用 Terra 時別用 Sol（約省一半 credits、約多一倍訊息數）、非必要不開 Fast；是否因此犧牲品質，需靠 `T-20261114-03` 實測。
