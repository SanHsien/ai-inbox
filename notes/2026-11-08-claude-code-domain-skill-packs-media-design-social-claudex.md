---
id: 2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex
title: "Claude Code 垂直領域 Skill 與 MCP 生態系全盤點：影音配音聽覺自審、YouTube/IG 確定性腳本、前端反 AI Slop 五件套與 Claudex 跨模型互審"
source_url: "https://www.instagram.com/reel/DfMpBTvh_Yj/"
source_platform: "Instagram Reels & Posts (8 則同主題工作流彙整) / GitHub"
author: "Kwon 永誠 (@kwons_en)、Airi (@airi_aimagic)、Hana (@its_hana_digital)、Chloe (@chloemakesdesign)、阿幸 (@hsing.daily)、Rena 姜瑞娜 (@renakeung)、Chiara (@lynexaai)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: done
cluster: "2"
cluster_role: "提示詞工程與上下文"
short_title: "Claude垂直領域Skill與MCP生態盤點"
source_review: full
source_reviewed_at: 2026-11-18
source_images: 51
source_replies: 4774
tags:
  - claude-code
  - agent-skills
  - earshot
  - mmaudio
  - youtube-agent-skill
  - instagram-agent-skill
  - impeccable
  - ui-ux-pro-max
  - claudex-loop
  - anti-slop
---

# Claude Code 垂直領域 Skill 與 MCP 生態系全盤點：影音配音聽覺自審、YouTube/IG 確定性腳本、前端反 AI Slop 五件套與 Claudex 跨模型互審

- **來源連結（8 則同系列 Instagram 貼文合併分析）**：
  1. [IG Reel `DfMpBTvh_Yj` (@kwons_en：Openverse + MMAudio + Earshot 影音自動配音與聽覺自審)](https://www.instagram.com/reel/DfMpBTvh_Yj/)
  2. [IG Reel `DfRwxagKLG9` (@airi_aimagic：YouTube 11 個免費 Claude Skills 經營頻道)](https://www.instagram.com/reel/DfRwxagKLG9/)
  3. [IG Reel `DfKHNzYq_s7` (@airi_aimagic：Instagram 13 個 Claude Skills 寫 Reels 26 公式、回留言與草稿安全邊界)](https://www.instagram.com/reel/DfKHNzYq_s7/)
  4. [IG Post `DfPQ-yeEzYJ` (@its_hana_digital：以背景、結構與限制取代空泛 Hook/Caption 指令)](https://www.instagram.com/p/DfPQ-yeEzYJ/)
  5. [IG Reel `DebpuRpkfnw` (@chloemakesdesign：消除 AI 介面感的 5 大前端設計 Skill 與 MCP 工具鏈)](https://www.instagram.com/reel/DebpuRpkfnw/)
  6. [IG Reel `DfFHkoEOs-F` (@hsing.daily：Instagram-Agent-Skill 13 個 IG 經營專用 Skill 流程)](https://www.instagram.com/reel/DfFHkoEOs-F/)
  7. [IG Post `DfMnV6sGAUE` (@renakeung：Instagram 13 Skills + `voice.md` 口吻設定與草稿安全邊界)](https://www.instagram.com/p/DfMnV6sGAUE/)
  8. [IG Reel `DdX7C1YP5Kj` (@lynexaai：Claudex Loop 讓 Claude 與 ChatGPT/Codex 四階段互審與角色互換開發)](https://www.instagram.com/reel/DdX7C1YP5Kj/)
- **對應官方開源 GitHub 專案（主動深挖補齊）**：
  - [`Leonxlnx/earshot`](https://github.com/Leonxlnx/earshot)（4,156 Stars，MIT）& [`hkchengrex/MMAudio`](https://github.com/hkchengrex/MMAudio)（2,307 Stars，MIT，CVPR 2025）
  - [`Jakeschincariol/youtube-agent-skill`](https://github.com/Jakeschincariol/youtube-agent-skill)（4,992 Stars，MIT）
  - [`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill)（5,302 Stars，MIT）
  - [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)（146,485 Stars，MIT）、[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)（105,368 Stars，Apache-2.0）、[`21st-dev/magic-mcp`](https://github.com/21st-dev/magic-mcp)（6,414 Stars，ISC）
  - [`chaseai-yt/claudex-loop`](https://github.com/chaseai-yt/claudex-loop)（3,374 Stars，MIT）
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-17-tasteskill-v2-anti-slop-frontend.md`](./2026-10-17-tasteskill-v2-anti-slop-frontend.md)（Taste-Skill v2 前端反 AI Slop 規則）
  - [`notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md`](./2026-11-08-google-research-harness2-recursive-agent-harnessing.md)（Google Research Harness² 8 大模組與沙盒防弊契約）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看 8 則 IG 貼文：說明文字全文、影片抽格（每支 5～8 格，字幕燒在畫面上）、兩則輪播各 7 張、留言區可見部分。未登入時每則只顯示最新 12 則留言（`DfFHkoEOs-F` 只顯示 4 則），共讀 88 則；各則留言總數依序約 5,155／1,496／2.2 萬／1,592／1,950／4,730／538／6,908，其餘要登入才看得到。
> 2026-11-17 登入補讀：6 支 Reels 開留言面板往下捲（內建瀏覽器載入很慢，每則捲約兩分鐘），讀到的則數與頁面標示總數見 frontmatter；第 1 支捲到底並展開 26 串回覆，其餘各讀四百多則。2 則輪播貼文在窄版面點不開留言面板，沒有補到。另用 `tools/video_transcript.py` 取了 6 支影片的逐字稿（Whisper small，專有名詞有錯字，只當對照用）。
> 2026-11-18 再補：2 則輪播貼文改開 `https://www.instagram.com/p/<id>/` 直接頁，留言列在右欄、子回覆可展開，各讀到熱門排序第一頁約 18 則（`DfPQ-yeEzYJ` 全是關鍵字「Claude」加作者「已私訊」的固定回覆；`DfMnV6sGAUE` 全是表情符號與「我要裝」，作者回覆其中一句是「追蹤我才能收到訊息」）。沒有實測、提問或反駁。再往下的留言要捲動才載入，當時瀏覽器面板沒有顯示、頁面不出畫格，捲不動，所以這 2 則仍沒讀夠；本篇維持 `partial`。

- **作者圖片／影片畫面**（共 51 格／張）：
  - `DfMpBTvh_Yj`（@kwons_en，48 秒，8 格）：片頭大字「千萬不要再用 Claude 剪影片了」；Openverse 畫面顯示約 522 萬個音效；MMAudio 論文頁（CVPR 2025）；時間軸上音效對齊剪點的示意；Earshot 的 GitHub 頁與終端機 `earshot` 指令；「關門聲」搜尋結果清單；片尾要觀眾留言「音效」。畫面都是示意動畫，沒有實際跑指令的輸出。
  - `DfRwxagKLG9`（@airi_aimagic，57 秒，7 格）：依序是寫腳本（畫面字樣為 21 種開頭公式）、剪輯清單、排一週、爆款引擎（倍數排行示意）、三步安裝（Claude Code → 貼 GitHub 連結 → `/yt-script`）、留言「YOUTUBE」。
  - `DfKHNzYq_s7`（@airi_aimagic，88 秒，5 格）：`/ig-reel`、`/ig-plan` 週曆（每天互動 20 分鐘）、爆款排名長條圖、三步安裝（畫面上有 `instagram-agent-skill` 連結字樣）。
  - `DfPQ-yeEzYJ`（@its_hana_digital，輪播 7 張）：封面寫「我訓練 Claude 寫 IG 內容，90 天漲了 8,000 位粉絲」；第 2～5 張是四個填空式提示詞範本的節錄（爆紅內容產生器、Hook 製造機、Reel 腳本寫手、社會認同轉換器），各自規定角色、產出結構、字數與禁止事項；第 6 張說明有效的原因是交代了角色、考量與輸出架構；第 7 張要觀眾留言「Claude」領全文。**整組圖沒有提到任何 GitHub 專案、Skill 或 `voice.md`**。
  - `DebpuRpkfnw`（@chloemakesdesign，56 秒，7 格）：五個工具各一格，背景是對應的 GitHub／文件頁（`ui-ux-pro-max-skill`、`impeccable`、`21st-dev/magic-mcp`、Figma MCP 文件、`ChromeDevTools/chrome-devtools-mcp`），片尾是五項清單與留言「美感」。
  - `DfFHkoEOs-F`（@hsing.daily，42 秒，5 格）：26 種開頭公式選單、爆款改寫示意（原片 12.4 倍 → 改成自己的版本）、主頁評分 72/100、13 個 Skill 的指令方塊。
  - `DfMnV6sGAUE`（@renakeung，輪播 7 張，平台標示「AI 內容」）：第 2 張三件事（寫腳本、找爆款用「跟自己平均比的倍數」、排一週）；第 3 張三步安裝；第 4 張先跑的 5 個指令；**第 5 張「中文用之前先知道 3 件事」：26 種開頭公式的例句都是英文、打分工具量不到中文字所以分數只能參考、去 AI 味功能會把中文破折號改壞**；第 6 張 `voice.md` 做法（整理 3 支最滿意的 Reels 逐字稿，請 Claude 照著寫 `voice.md`，13 個技能動筆前都會先讀）；第 7 張留言「我要裝」。
  - `DdX7C1YP5Kj`（@lynexaai，53 秒，5 格）：Claude 與 GPT 圖示放進同一個流程、一份中文的實作計畫文件（含目標與可觀察的驗收條件）交給 GPT 審、兩個 AI 互換角色的示意。
- **影片逐字稿**（2026-11-17 補取，6 支）：口白內容與說明文字、抽格畫面一致，沒有多出畫面上看不到的資訊。值得記的只有兩點：`DfKHNzYq_s7` 的口白幾乎是 `@auraguy.ai` 英文原片說明文字的逐句中譯（見下方留言）；`DfMpBTvh_Yj`、`DebpuRpkfnw`、`DdX7C1YP5Kj` 的口白都只講功能，沒有任何實測數字。
- **作者留言補充**（2026-11-17 更正：上次寫「都沒有作者留言」是未登入看不到）：6 支 Reels 的作者幾乎每一則留言底下都有一則自動回覆，內容只有「已私訊，請查看陌生訊息／訊息請求」這類固定句（每位作者 1 到 3 種句型輪替），沒有連結、補充或勘誤。頁面標示的留言總數大約一半是這種自動回覆。安裝連結一律走私訊，貼文與留言區都沒有公開連結。
- **網友留言重點**（2026-11-17 補讀約 4,700 則後）：
  - 九成九以上仍是領取用的關鍵字與表情符號。
  - **`DfKHNzYq_s7` 被指抄襲**：`jing.mu`（63 個讚，該則最高）貼出 `@auraguy.ai` 2026-10-26 的英文原片 [`De7V3pbTWX6`](https://www.instagram.com/reel/De7V3pbTWX6/)，說這支是直接抄劇本；`felix_tsao` 附和並說至少要標原作者。已開原片核對：說明文字的段落順序、賣點與「留言 SKILL 領教學」的做法都相同，原片早 6 天、留言約 2 萬則。`@airi_aimagic` 沒有回應。
  - **私訊沒收到**：`DfMpBTvh_Yj` 有 13 則、`DfRwxagKLG9` 有 4 則、`DfKHNzYq_s7` 有 7 則回報留了關鍵字但沒收到私訊（其中一則說特地加了好友也沒有）。
  - `DebpuRpkfnw`：`syr710`（38 個讚）與 `sigrid.momo` 指出這支談「一看就是 AI 做的」的影片，口白本身就是 AI 合成聲音；另有兩則留言把口白的「美感」聽成別的詞。
  - 零星提問都沒有人回答：`cup0319` 問是不是只能 Claude 用、`walking_with_god_every_day` 問三個工具是否免費（`DfMpBTvh_Yj`）；`yoyo651207`、`amethyst_920` 問有沒有手機版、是不是一定要電腦（`DfFHkoEOs-F`）；`fix_norma` 問兩個模型意見不同時怎麼知道誰對（`DdX7C1YP5Kj`）。
  - `anting13579`（`DfRwxagKLG9`）：標題和封面要當成一組先想，腳本之前先確認觀眾為什麼點進來。這是唯一一則談方法的留言。
  - 讀到的範圍內沒有任何人回報實際裝了、用了之後的結果。
  - 上次（未登入、88 則）的摘要，當時還沒看到上面的抄襲指控：讀到的 88 則幾乎全是領取用的關鍵字（「音效」「YouTube」「Skill」「Claude」「美感」「Reel」「我要裝」「計畫」）與表情符號，沒有實測回報、反駁或出處更正。
- **留言抽樣判準（2026-11-18）**：8 則貼文留言合計約 4.4 萬則，讀了約 4,774 則（6 支 Reels 各超過熱門前 300 則，2 則輪播各讀第一頁約 18 則）。讀到的幾乎全是索取資源的關鍵字留言與作者的「已私訊」自動回覆，沒有任何實測、反駁或更正；依 SOP「留言極多時可抽樣」判斷其餘不重要，標 `full`。作者上傳的圖片 51 張已全部看過。
- **對分析的影響**：
  1. **修正 `DfPQ-yeEzYJ` 的歸類**：原筆記把它算進「圍繞 Jake Schincariol 姊妹專案的 5 則」，並說它對應 `voice.md`。看完 7 張圖，這篇是獨立的四個結構化提示詞範本，與那兩個 repo 無關；`voice.md` 的做法出自 `DfMnV6sGAUE` 第 6 張。已改 2.2 節開頭與第 3 點。
  2. **補上中文使用限制**：`DfMnV6sGAUE` 第 5 張指出這套 IG 技能對中文的三個限制，已補進 2.2 節。這與原筆記列的 `beats.py` 以 165 wpm 估秒數、`humanize.py` 清破折號是同一件事的兩面：這些確定性工具是照英文設計的，中文內容的分數與自動改寫不能直接採信。
  3. **貼文數字與 README 不一致之處**（正文維持 README 查證值）：`DebpuRpkfnw` 說明文字寫 UI UX Pro Max「192 套配色」（README 的 192 是推理規則數）、Impeccable「59 條規則」（2026-11-14 查 README 為 62 條）；`DfRwxagKLG9` 寫 YouTube 版 21 種開頭公式、IG 版 26 種；`DfFHkoEOs-F` 寫 3,000 多顆星、`DfMnV6sGAUE` 寫 4 千多顆星，都是發文當時的數字。
  4. `DfPQ-yeEzYJ` 封面的「90 天漲 8,000 粉」是作者自述，圖文沒有附任何後台數據，不當作成效證據。
  5. 2026-11-17 補讀後：
     - **來源性質更清楚**：8 則都是「留關鍵字換私訊」的導流貼文，其中 `DfKHNzYq_s7` 是翻譯別人的英文原片。這不影響正文，因為正文的技術內容本來就是直接查 GitHub repo 與 README 寫的，沒有採信貼文說法；但第 1 節若把這幾位發文者寫成工具的介紹者，要理解成轉述者，不是作者也不是實測者。已在 2.2 節開頭補一句。
     - 四千多則留言沒有一則實測回報，所以貼文裡「省下幾小時」「90 天漲 8,000 粉」這類效果宣稱仍然沒有任何佐證，維持不採信。
     - `fix_norma` 的提問（兩個模型意見不同聽誰的）是跨模型互審流程的真問題，貼文與留言都沒有回答；本機的做法是以可執行的驗收條件為準，不以任一模型的意見為準，正文不用改。
  6. 任務不變：已完成的兩個任務針對的是技能包安全檢查與外部連結巡檢，不受上述修正影響。

---

## 1. 核心內容摘要：5W1H 初篩與八篇貼文合併脈絡（Executive Summary）

這 8 則 Instagram 貼文在外觀上都是典型的「介紹一套 Claude Code 神級工具組合 → 留言關鍵字領取安裝連結」社群導流內容；將其背後隱藏的原始碼倉庫逐一挖出後，可歸納為 **Claude Code 垂直領域外部 Harness（Skill Packs + Deterministic CLI + MCP）的四大實戰範式**：

```
+-----------------------------------------------------------------------------------+
|               8 則 IG 貼文背後指向的 4 大 Claude Code 垂直工具鏈                  |
+-----------------------------------------+-----------------------------------------+
| 1. 影音音效合成與聽覺閉環 (DfMpBTvh_Yj) | 2. 自媒體頻道確定性經營 (5 則貼文合併)  |
|  - Openverse (500萬+ CC0 音效搜尋)      |  - youtube-agent-skill (11 Skills+6 CLI)|
|  - hkchengrex/MMAudio (畫面對齊生音效)  |  - instagram-agent-skill (13 Skills+5CLI)|
|  - Leonxlnx/earshot (AI 聽覺自審與評分) |  - voice.md 個人語氣錨點 + 結構化約束   |
+-----------------------------------------+-----------------------------------------+
| 3. 前端 UI 反 AI Slop 五件套 (DebpuRpkfnw)| 4. 跨模型四階段對抗互審 (DdX7C1YP5Kj) |
|  - UI UX Pro Max (192 規則 / 80 風格)   |  - chaseai-yt/claudex-loop              |
|  - pbakaus/impeccable (62 條決定性規則) |  - Claude 擬計畫 -> Codex 挑漏洞        |
|  - 21st MCP + Figma MCP + DevTools MCP  |  - 角色互換寫 Code + SHA256 審批指紋    |
+-----------------------------------------+-----------------------------------------+
```

---

## 2. 四大主題技術深挖與 CQR 實證剖析（Deep Dive）

### 2.1 主題一：影音剪輯自動配音與 AI 聽覺自審閉環（`DfMpBTvh_Yj`）

- **貼文主張**（`@kwons_en`）：剪片最累的是翻十幾個網站找音效、放上去還慢半拍；透過 **Openverse + MMAudio + Earshot** 三件套，讓 Claude 自己找、自己生、自己聽完修正。
- **底層開源架構查證**：
  1. **Openverse**：檢索超過 500 萬個 CC0 與開放授權音效素材。
  2. **[`hkchengrex/MMAudio`](https://github.com/hkchengrex/MMAudio)**（UIUC & Sony AI，CVPR 2025，論文 [arXiv:2412.15322](https://arxiv.org/abs/2412.15322)，2026-11-14 查證標題為 MMAudio: Taming Multimodal Joint Training for High-Quality Video-to-Audio Synthesis）：多模態聯合訓練的 Video-to-Audio 模型，內建幀級同步模組（Synchronization Module）使生成音效對齊畫面動作。
  3. **[`Leonxlnx/earshot`](https://github.com/Leonxlnx/earshot)**（`v0.4.0`，4,156 Stars，純 CPU 執行之 CLI / Python API / MCP Server）：
     - 解決 Coding Agent「會寫渲染影片的程式碼（如 Remotion），卻聽不到自己做出來的聲音是否破音或慢了 80ms」的盲區。
     - **核心指令**：`earshot describe`（輸出瞬態、衰減時間、AudioSet 標籤與峰值 dBFS）、`earshot timeline`（逐秒聽覺逐字稿，標記事件與畫面切點同步誤差）、`earshot sheet -o out.png`（輸出含頻譜、波形、響度與畫面幀的視覺化對照圖供多模態模型檢視）、`earshot critique`（對照 7 部專業產品發佈片計算 23 項評分指標與 LUFS 響度）、以及 `earshot forge` / `earshot fit`（以純程式碼合成 252 種無版權音效）。

### 2.2 主題二：YouTube 與 Instagram 確定性自媒體工作流（`DfRwxagKLG9`、`DfKHNzYq_s7`、`DfFHkoEOs-F`、`DfMnV6sGAUE`、`DfPQ-yeEzYJ`）

其中 4 則（`DfRwxagKLG9`、`DfKHNzYq_s7`、`DfFHkoEOs-F`、`DfMnV6sGAUE`）圍繞同一位作者 **Jake Schincariol** 開源的姊妹專案（這 4 位發文者都是轉述者，不是專案作者；`DfKHNzYq_s7` 的內容譯自 `@auraguy.ai` 的英文原片，見第 0 節）；`DfPQ-yeEzYJ` 是獨立的四個結構化提示詞範本，沒有提到這兩個 repo（2026-11-16 看完輪播 7 張後修正），因主題同為「用具體約束取代空泛指令」而併在本節（其中 `@airi_aimagic` 分別以 `DfRwxagKLG9` 介紹 YouTube 11 Skills、以 `DfKHNzYq_s7` 介紹 Instagram 13 Skills 的 `/ig-reel` 26 種開頭公式打分、`/ig-comment`、`/ig-reply`、`/ig-profile`、`/ig-plan`、`/ig-viral` 與「只寫草稿、不給 IG 密碼」之安全邊界）：

| 專案名稱 | 規模與指令數 | 內建零依賴 Python 確定性工具 | 關鍵設計亮點與 CQR 實測限制 |
| :--- | :--- | :--- | :--- |
| **[`Jakeschincariol/youtube-agent-skill`](https://github.com/Jakeschincariol/youtube-agent-skill)** (4,992★) | 11 個 Skills（`/yt-script`, `/yt-package`, `/yt-edit`, `/yt-comment`, `/yt-plan`, `/yt-viral`, `/yt-retention`, `/yt-shorts`, `/yt-seo`, `/yt-chapters`, `/yt-audit`） | 6 支：`hookscore.py`、`title.py`、`deadair.py`、`chapters.py`、`retention.py`、`swipe.py` | - 將「標題＋縮圖」視為單一點擊面聯合檢查（`title.py` 抓重複與截斷）。<br>- `deadair.py` 直接把 `.srt` 逐字稿轉成標好秒數的剪輯決策清單（EDL）。<br>- `swipe.py` 不看絕對觀看數，而是計算**超越該頻道自身中位數的倍數（Outlier Multiple）**。 |
| **[`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill)** (5,302★) | 13 個 Skills（`/ig-reel`, `/ig-viral`, `/ig-caption`, `/ig-carousel`, `/ig-story`, `/ig-profile`, `/ig-plan`, `/ig-human`, `/ig-comment`, `/ig-reply`, `/ig-dm`, `/ig-repurpose`, `/ig-audit`） | 6 支：`hookscore.py`、`beats.py`、`caption.py`、`humanize.py`、`detect.py`、`swipe.py` | - `beats.py` 依 165 wpm 估算每句台詞秒數，抓出「超過 3 秒才進主軸」與「單一畫面停滯超過 4 秒」的流失點。<br>- `caption.py` 模擬 IG 動態牆**前 125 字元折疊視窗**，並強制執行 2025/12/18 生效的 **5 個 Hashtag 上限**。<br>- `humanize.py` 自動清除 18 類複製貼上隱藏字元、破折號與 154 個套話（`slop.json`）。 |

- **CQR 實證亮點（作者於 README 誠實公開的負面實驗結果）**：
  1. **`hookscore.py` 能抓出爛開頭（AUC `0.83`），但無法預測爆款（AUC `0.56`）**（出處：[instagram-agent-skill README](https://github.com/Jakeschincariol/instagram-agent-skill#readme) 第 225-242 行附近的實測段落；該段說明 74 筆語料是 YouTube Shorts 的前 3 秒自動字幕，非 Reels，且為作者自述、本筆記未重現；此數字僅屬 IG 庫，不套用於上方 YouTube 庫那一列）：在 74 支真實短影音上，五項評分維度中只有 `SPECIFICITY`（具體數字或專有名詞）能有效區分高低表現（中位數差 60 分），`STAKES` 與 `ADDRESS` 中位數完全相同。
  2. **草稿唯讀鐵律（Nothing gets posted until you say yes）**：兩個專案皆刻意不接自動發文爬蟲，避免違反平台條款遭封鎖，且未知數據一律輸出 `{{your number}}` 佔位符，絕不捏造案例數據。
  3. **`voice.md`（對應 `@renakeung` `DfMnV6sGAUE` 第 6 張圖）**：先提供 3 支過往影片逐字稿或填寫 `~/.claude/{youtube,instagram}/voice.md` 建立個人語氣、受眾與禁忌詞，13 個技能動筆前都會先讀，用來消除千篇一律的 AI 腔調。
  4. **具體約束（對應 `@its_hana_digital` `DfPQ-yeEzYJ`）**：與上述 repo 無關的四個填空式提示詞範本，共同點是每個都寫明角色、產出結構、字數上限與禁止事項。
  5. **中文使用限制（`DfMnV6sGAUE` 第 5 張圖，轉述者自述、本筆記未重現）**：26 種開頭公式的例句都是英文；打分工具量不到中文字，分數只能參考；去 AI 味功能會把中文破折號改壞。用在中文內容時，`hookscore.py`、`beats.py`（165 wpm 是英文語速）與 `humanize.py` 的輸出都要人工複核。

### 2.3 主題三：消除「一眼 AI 介面」的前端設計五件套（`DebpuRpkfnw`）

- **貼文主張**（`@chloemakesdesign`）：Claude 做出來的介面充滿紫色漸層與卡片套卡片，不是 Prompt 問題，而是少了「先定風格、最後再檢查」的 5 個工具：
  1. **[`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)**（146,485 Stars）：提供 192 條設計推理規則（2026-11-14 查證：README 寫 192 Reasoning Rules）與 80 種可搜尋 UI 風格（2026-11-14 查證：README 寫 80 searchable styles，其中 51 種為 active），開工前先鎖定配色與字體階層。
  2. **[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)**（Paul Bakaus 開源，105,368 Stars）：提供 24 個設計引導指令（如 `/impeccable bolder`、`quieter`、`critique`、`audit`、`harden`）與 **62 條零 LLM 決定性反 AI Slop 規則**（`npx impeccable detect`，直接攔截 Inter 濫用、藍紫漸層、巢狀卡片、低對比度）。
  3. **[`21st-dev/magic-mcp`](https://github.com/21st-dev/magic-mcp)**（現已升級為 **21st MCP**，2026-11-14 查證：repo 說明寫「Magic MCP is now the 21st MCP」，`npx @21st-dev/cli@latest init`，6,414 Stars）：直接在編輯器內搜尋 10,000+ 個高品質 React/Tailwind 元件。
  4. **Figma MCP**：選取設計稿畫框直接轉為結構化元件程式碼。
  5. **Chrome DevTools MCP**：讓 Agent 自動開啟真實瀏覽器檢查渲染結果與響應式破版並自行修正。
- **重要資安發現（`pbakaus/impeccable` Live Mode 無沙盒風險）**：
  - 查閱 `pbakaus/impeccable` 官方 README 第 72 行發現：當執行 `/impeccable live` 並在瀏覽器按 Apply 時，若聊天 session 超過 1 分鐘未輪詢，它會自動從 `PATH` 啟動 `codex` 或 `claude`，**並預設加上 `--dangerously-bypass-approvals-and-sandbox` 或 `--permission-mode bypassPermissions` 完全關閉沙盒與審批**，還會在陌生 repo 執行 `package.json` 的 `impeccable:manual-edit-validate`。
  - **防護做法**：必須在啟動環境設定 `IMPECCABLE_LIVE_COPY_AGENT=chat` 或 `off`，且在無人值守執行時留意 Claude Code 的 Command Hooks 會在模型審批之外自動執行。

### 2.4 主題四：Claudex Loop 跨模型四階段計畫硬化與角色互換（`DdX7C1YP5Kj`）

- **貼文主張**（`@lynexaai`）：透過開源專案 **Claudex Loop** 讓 Claude 與 ChatGPT/Codex 協同工作，先擬計畫再由另一方挑漏洞，寫程式時雙方互換角色。
- **底層開源架構查證（[`chaseai-yt/claudex-loop`](https://github.com/chaseai-yt/claudex-loop)，3,374 Stars，前身為 `grill-me-codex` / `crucible`）**：
  1. **核心鐵律：「Whoever built it never grades it（建造者絕不自己評分）」**。
  2. **四階段工作流**：
     - Phase 1 `Recon`（環境與程式碼盤點）→ Phase 2 `Interrogate`（需求追問對齊）→ Phase 3 `Adversarial Plan Review`（跨模型挑戰計畫，綁定計畫檔路徑與 `SHA256` 雜湊，任何後續修改即令核准失效）→ Phase 4 `Cross-Model Build & Inspection`（角色互換實作與獨立驗收，綁定 pre-build commit 與變更指紋）。
  3. **沙盒與權限隔離**：審查階段（Review）強制在唯讀沙盒運行，並關閉使用者自訂 Plugins、Apps 與外部 MCP Servers，防止審查者在唯讀 Shell 外產生副作用。
  4. **與本庫現有技能對映**：本庫環境已內建 `/grill-me`、`ai-review`（跨模型二審）與 `blind-review`（盲審子代理），可吸收 Claudex Loop 的「計畫 SHA256 指紋鎖定」與「Review 階段關閉非必要 MCP」機制。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261108-04`**｜**[優先級：高]** 撰寫《Claude Code 垂直領域 Skill 與 MCP 生態系盤點及安全採納規範》，並實作 `tools/verify_agent_skill_pack_safety.py` 靜態審計器
  - **目標範圍**：`docs/claude-code-domain-skill-packs-and-mcp-audit.md`、`tools/verify_agent_skill_pack_safety.py`、`tests/test_verify_agent_skill_pack_safety.py`
  - **具體實作步驟**：
    1. 撰寫 `docs/claude-code-domain-skill-packs-and-mcp-audit.md`，完整整理 8 則 IG 貼文對應之四大垂直領域開源專案（`earshot`/`MMAudio`、`youtube-agent-skill`/`instagram-agent-skill`、`ui-ux-pro-max`/`impeccable`/`21st-mcp`、`claudex-loop`）架構、CQR 實證數據（`hookscore.py` AUC `0.83` vs `0.56`）與安全邊界。
    2. 實作 `tools/verify_agent_skill_pack_safety.py`，以 `--pack` 對技能包實際檔案做靜態啟發式掃描（通過不代表安全，仍需人工審查），並保留四條自填宣告檢查項目（不能當作採納依據）：`SKILLPACK-001`（攔截 `--dangerously-bypass-approvals-and-sandbox` / `bypassPermissions` 與 Impeccable Live Mode 背景自動提權）、`SKILLPACK-002`（背景 Hook 審查與 `DO_NOT_TRACK=1` / `telemetry: false` 閘門）、`SKILLPACK-003`（社交平台 `human_publish_only` 草稿唯讀與 `{{your number}}` 零虛構數據佔位符）、`SKILLPACK-004`（確定性本地 Linter 支撐與反 `100% undetectable` 誇大宣稱）。
    3. 撰寫 `tests/test_verify_agent_skill_pack_safety.py` 涵蓋四條規則之正反例單元測試。
  - **驗收標準（DoD）**：
    - python tools/verify_agent_skill_pack_safety.py --self-test 回 0；以 `--pack` 掃描含危險旗標的假技能包回 1、掃描不存在的目錄回 2（由 tests/test_verify_agent_skill_pack_safety.py 涵蓋）。（DoD 於 2026-11-14 隨退回修正改寫：原本的裸執行回 `[PASS]` 不能當採納檢查。）
    - python -m unittest tests/test_verify_agent_skill_pack_safety.py -v 全數通過。
    - `python tools/build_index.py` 與 `python tools/verify_inbox.py` 契約及 100% 目錄覆蓋率驗證通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：重寫（2026-11-14，Fable）：改為 --pack 實掃技能包目錄的靜態啟發式審計器，argv 等級解析（等號、空白、Tab、引號、大小寫、NFKC 全形、續行），類別 BYPASS／REMOTE-EXEC／OBFUSCATED／CRED-ACCESS／INSTALL-EXEC 判 FAIL，AUTO-HOOK／MCP-SERVER／DYNAMIC-EXEC 列 REVIEW；裸執行回 2，內建範例改由 --self-test。審查反例（=、雙空白、Tab）由 exit 0 變 1；Opus 以 25 個假技能包測試，抓不到的變數間接、$(…) 拼接已寫進文件第 4.7 節。專屬測試約 90 個，mutation 全被抓到。 **搬移註記（2026-11-14）**：工具與測試已移至 [`SanHsien/agent-safety-checks`](https://github.com/SanHsien/agent-safety-checks)（保留 git 歷史）。

- [x] **`T-20261108-06`**｜**[優先級：中]** 新增 `tools/check_external_refs.py`：掃描 `notes/` 內的 GitHub repo 與 arXiv 連結，確認存在、是否改名或封存
  - **目標範圍**：`tools/check_external_refs.py`、`tests/test_check_external_refs.py`、`docs/evidence/external-refs-check-2026-11.md`
  - **具體做法**：
    1. 掃 `notes/*.md`（略過程式碼圍欄），抽出 `https://github.com/<owner>/<repo>` 與 `arxiv.org/(abs|pdf)/<id>`，去重；同一行含「（私有）」的 repo 跳過。
    2. 用 `gh api repos/<o>/<r>` 查（無 gh 時退用 urllib 加 `GITHUB_TOKEN`）：404 記錯誤、改名（301 或回傳的 full_name 不同）記警告、archived 記警告；arXiv 用 HEAD 請求，404 記錯誤。
    3. 查詢函式可注入，測試用假回應、不連網；支援 `--offline`（只列清單）與 `--cache <檔>`。
    4. 不接 CI（會連網、有 rate limit），只當人工巡檢與派工驗收用，在 `AGENTS.md` 寫作鐵律補一行用法。
  - **驗收標準（DoD）**：`python -m unittest tests/test_check_external_refs.py` 全綠，至少涵蓋 404 → exit 1、改名 → exit 0 且有警告、「（私有）」被略過、arXiv 404 → exit 1；實跑 `python tools/check_external_refs.py --notes notes` 的摘要存成 `docs/evidence/external-refs-check-2026-11.md`（總數與失敗清單，失敗要逐條處理）；`python tools/verify_inbox.py` 通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：完成（2026-11-14）：tools/check_external_refs.py＋tests（404、改名、封存、私有略過、arXiv、壞快取、gh 輸出 UTF-8 解碼等）。實跑 94 個連結：92 OK，2 個 404 是筆記刻意記錄的「尚未 Fork」，1 改名、1 封存；證據 docs/evidence/external-refs-check-2026-11.md。整合者實跑時抓到 gh 輸出以 cp950 解碼而崩潰的 bug，已修並加回歸測試。
