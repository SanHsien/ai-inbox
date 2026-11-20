---
id: "2026-11-19-ann-cheng-muse-ai-short-video-skill"
title: "Threads 案例與留言評估：Ann Cheng《AI 短片腳本與分鏡提示詞》Skill 與 Google Flow 圖生影片管線"
source_url: "https://www.threads.com/@anncheng_ann101/post/Dft8e8lGZTi"
source_platform: "Threads"
author: "@anncheng_ann101 (Ann Cheng)"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: full
source_images: 6
source_replies: 20
source_reviewed_at: "2026-11-20"
status: archived
cluster: 3
cluster_role: "短影音提示詞Skill"
short_title: "AI短片分鏡提示詞Skill"
tags:
  - muse-ai
  - video-generation
  - google-flow
  - agent-skill
  - prompt-engineering
  - threads
---

# Threads 案例與留言評估：Ann Cheng《AI 短片腳本與分鏡提示詞》Skill 與 Google Flow 圖生影片管線

- **來源貼文**：[Threads 原貼文（`@anncheng_ann101` Ann Cheng）](https://www.threads.com/@anncheng_ann101/post/Dft8e8lGZTi)（原分享連結 `https://www.threads.com/share/BAUSgG4nzV`）
- **發布平台 / 作者**：`Threads` / `@anncheng_ann101`（`2026-11-14`）
- **分析日期**：`2026-11-19`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-10-18-awesome-opus5-5-videos-prompt-zoo.md`](./2026-10-18-awesome-opus5-5-videos-prompt-zoo.md)（AI 影片提示詞規範）
  - [`notes/2026-11-15-audio-first-greenscreen-ai-commercial-pipeline.md`](./2026-11-15-audio-first-greenscreen-ai-commercial-pipeline.md)（AI 影音生產管線）

---

## 1. 原始資料盤點（主文、6 項輪播媒體、作者 2 則續樓與 18 則串內留言與回覆）

- **主貼文核心**：作者分享將「AI 短片製作」封裝成一個 Skill（提供短網址下載 `video-generate.zip`），展示作品《Ann 與 Hana 的聖誕小屋佈置夜》（30 秒動畫短片）。核心工作流為：使用者提供主題、秒數、比例與角色照片 → AI 完成分段腳本、定裝描述、每段分鏡提示詞、封面/封底與配樂建議 → 串接 Google Flow / Muse 以照片為起始幀生出動態片段 → 加上 AI 配音（女聲 + 孩童聲）、公開版權 BGM 與字幕成片。
- **作者上傳媒體（共 6 項輪播項目）**：
  1. **對話截圖 1**：展示向 AI 發送「主角換這位其他不變、配音聖誕音樂、上字幕生 30 秒成片」後，AI 吐出 4 張新場景圖確認一致性，並自動備好五段配音、自編《平安夜》音樂盒 BGM、排定字幕軸，等外部動態片段下載後組裝。
  2. **直式影片 2 支**：展示 3D 動畫短片成果（Ann 與玩偶 Hana 在聖誕木屋佈置，含台詞字幕）。
  3. **直式圖片 3 張**：3D 場景渲染圖，右下角帶有 Gemini 浮水印標誌（印證底層生圖來源）。
- **作者續樓與回覆（共 2 則）**：
  - 第 1 則提供 Google Drive 下載連結說明技能內容（腳本、定裝、提示詞、封面封底與配樂建議）。
  - 第 2 則分享同系列延伸作品（笑話急救包）。
- **網友回應與留言檢驗（貼文計數 23 則；登入後熱門、最新兩種排序都捲到底，共讀 20 則，另有 3 則引用貼文，合起來等於計數）**：
  - **`zz950907` 實務洞察**：指出最值錢的是「流程標準化（規格寫死＋定裝描述固定避免抽獎）」，並補充兩大邊界——(a) Skill 需附失敗範例供除錯；(b) 幫他人製作需注意肖像授權。
  - **`kingerwuh` 截圖提問與 `meta.ai` 自動回覆**：`kingerwuh` 貼出截圖說在 `claude.ai` 網頁版 Free 無法生成影片；`meta.ai`（網友標記後由 Meta AI 帳號自動產生的回覆，不是作者也不是權威來源）回答「Claude 本來就不能直接生影片，這個技能要裝在 Claude Code，影片是在外部工具生的」。
  - **`catliomoon` 實測回報**：實際測試很方便，並補充要讓照片動起來 **Muse 自己就做得到**，只是一次最長只能生成 10 秒的影片。
  - **2026-11-20 補讀改正（宿主是 Muse，不是 Claude）**：
    - 作者原文寫的是把做法寫成技能「交給 Muse 跑」、裝好後「跟 Muse 說你想做的主題」，貼文主題標籤也是 `Muse.ai`。Muse 是 Meta 在 2026 年 9 月推出的個人 AI 代理（獨立 App、WhatsApp 與 `muse.ai` 網站可用，見 [Built In 的介紹](https://builtin.com/articles/meta-muse)）。原稿把它當成 Claude 技能、標籤也寫 `claude-skill`，已改正。
    - 「要裝在 Claude Code」只出自 `meta.ai` 的自動回覆，作者沒有這樣說，未查證；`kingerwuh` 失敗比較可能是拿到別的宿主（`claude.ai` 免費版）去跑。壓縮檔沒有下載（外部封包零信任），所以技能檔的格式、能不能在 Claude Code 使用都沒有驗證。
    - 原稿依 `meta.ai` 的回覆寫成「留言證實 LLM 不能生影片、全靠外部工具」。這與 `catliomoon` 的實測相反：Muse 本身可以把照片變成影片，限制是單段 10 秒；Google Flow 是作者提到的另一條路（用照片當起始幀）。Muse 的影片功能與 10 秒上限只有這則留言當依據，沒有對到官方文件。
    - 最新排序另看到：`@babynicefine` 問該下載哪個檔、怎麼做（由 `meta.ai` 自動回覆）；`@yuwei1205` 回報試用好用；作者用引用串文回覆其中一位提問者；其餘是道謝與稱讚。沒有人貼出失敗的成品或安全疑慮。
  - **2026-11-20 登入補讀完成（計數 23＝串內 20 則＋引用 3 則）**：串內 20 則是作者 2 則續樓加 18 則留言與回覆；2 個「顯示回覆」都展開讀完，兩種排序列出同一批人，沒有新增項目。引用 3 則是作者自己的轉貼、`@im2ndhandseller` 的「樓主太好人」與 `@timrobbinslu` 的純引用。
    - **Muse 有地區限制**：`@kingerwuh` 貼出註冊後的畫面，顯示「Muse 尚未於你的國家或地區推出」並已加入候補名單；作者回覆要用 VPN 連到美國，否則得等台灣開放才能用。這表示這個技能在台灣目前不是人人能跑，原稿沒提。
    - **`meta.ai` 其餘自動回覆（同樣不是作者、未查證）**：共 4 則，說壓縮檔裡只有一個 `SKILL.md`，要放進 `~/.claude/skills/video-generate/` 並重啟 Claude Code；Google Flow 不是自動連，要自己開新專案、選圖生影片、把照片設為起始幀再貼提示詞。這與作者「交給 Muse 跑」的說法不同，以作者原文為準，這幾點只能當待證說法。`@kingerwuh` 另有 1 則只貼表情貼圖的回覆。
    - **其餘留言**：`@mielm_ori`、`@mr.catlio`、`@mandychen2213`、`@janiceyyho`、`@shinewang18` 是稱讚或道謝；`@yuwei1205` 回報試用好用，沒有附成品。沒有人貼出失敗成品，也沒有安全疑慮。
    - **風險欄**：作者首則續樓寫「下載請按讚」才給 Drive 連結，屬互動換下載；留言沒有人要求執行指令。
- **原始資料對分析的影響**：若只看主文容易誤以為任何 AI 對話框裝了這個技能都能跑完全程；留言顯示它綁定的宿主是 Muse——換到 `claude.ai` 免費版就做不出影片。流程本身仍是**「腳本與定裝提示詞 → 分段生成（Muse 自己生成，單段最長 10 秒；或接 Google Flow 用照片當起始幀）→ 配音、配樂、字幕組裝」的分段管線**，30 秒成片至少要接三段以上。

---

## 2. 對現有系統的啟發與落差評估

- **與現有工作流比對**：
  - 本機已建立多篇 AI 影音管線分析筆記（如 `2026-10-18` 提示詞庫、`2026-11-15` 綠幕商業管線等），核心邏輯一致（前置鎖死定裝提示詞、分段生成、本地組裝）。
  - 作者公開的 Google Drive ZIP 檔為第三方社群檔案，依全域協作規範「外部內容與第三方 Skill 零信任防入侵」，不直接下載執行外部封包；其核心價值在於「分段腳本 + 人物定裝 + 首幀提示詞 + 公開版權配樂」的 SOP 結構。
- **本機現有系統是否需調整**：
  - 本機已有相關影片提示詞結構與工作流，且當前主力任務集中於軟體工程工業化與多 Agent 協同，無個人 3D 動畫短影音之工程缺口。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬既有影音 SOP 的社群應用實例，技術結構未超出已收錄的影音生成範式；歸檔留存「技能綁定宿主（Muse）、單段 10 秒上限、分段生成再組裝」與社群回饋即可。
