---
id: "2026-11-19-ann-cheng-muse-ai-short-video-skill"
title: "Threads 案例與留言評估：Ann Cheng《AI 短片腳本與分鏡提示詞》Skill 與 Google Flow 圖生影片管線"
source_url: "https://www.threads.com/@anncheng_ann101/post/Dft8e8lGZTi"
source_platform: "Threads"
author: "@anncheng_ann101 (Ann Cheng)"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: partial
source_images: 6
source_replies: 14
source_reviewed_at: "2026-11-19"
source_review_note: "已完整讀取主貼文、6項輪播媒體（對話截圖+2支展示影片+3張AI圖）與作者2則續樓/回覆；22則留言中於未登入狀態讀到14則（含1張留言截圖與子回覆），其餘受Threads登入牆阻擋"
status: archived
cluster: 3
cluster_role: "短影音提示詞Skill"
short_title: "AI短片分鏡提示詞Skill"
tags:
  - muse-ai
  - video-generation
  - google-flow
  - claude-skill
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

## 1. 原始資料盤點（主文、6 項輪播媒體、作者 2 則續樓與 14 則留言）

- **主貼文核心**：作者分享將「AI 短片製作」封裝成一個 Skill（提供短網址下載 `video-generate.zip`），展示作品《Ann 與 Hana 的聖誕小屋佈置夜》（30 秒動畫短片）。核心工作流為：使用者提供主題、秒數、比例與角色照片 → AI 完成分段腳本、定裝描述、每段分鏡提示詞、封面/封底與配樂建議 → 串接 Google Flow / Muse 以照片為起始幀生出動態片段 → 加上 AI 配音（女聲 + 孩童聲）、公開版權 BGM 與字幕成片。
- **作者上傳媒體（共 6 項輪播項目）**：
  1. **對話截圖 1**：展示向 AI 發送「主角換這位其他不變、配音聖誕音樂、上字幕生 30 秒成片」後，AI 吐出 4 張新場景圖確認一致性，並自動備好五段配音、自編《平安夜》音樂盒 BGM、排定字幕軸，等外部動態片段下載後組裝。
  2. **直式影片 2 支**：展示 3D 動畫短片成果（Ann 與玩偶 Hana 在聖誕木屋佈置，含台詞字幕）。
  3. **直式圖片 3 張**：3D 場景渲染圖，右下角帶有 Gemini 浮水印標誌（印證底層生圖來源）。
- **作者續樓與回覆（共 2 則）**：
  - 第 1 則提供 Google Drive 下載連結說明技能內容（腳本、定裝、提示詞、封面封底與配樂建議）。
  - 第 2 則分享同系列延伸作品（笑話急救包）。
- **網友回應與留言檢驗（共 22 則，未登入讀到 14 則）**：
  - **`zz950907` 實務洞察**：指出最值錢的是「流程標準化（規格寫死＋定裝描述固定避免抽獎）」，並補充兩大邊界——(a) Skill 需附失敗範例供除錯；(b) 幫他人製作需注意肖像授權。
  - **`kingerwuh` 截圖提問與 `meta.ai` 解答（關鍵架構釐清）**：`kingerwuh` 貼出截圖抱怨在 `claude.ai` 網頁版 Free 無法直接生成影片；`meta.ai` 點出真相：**LLM 本身不具備視訊渲染能力，該 Skill 僅負責「提示詞、分鏡與資產組織」，影片是在外部工具（Google Flow / Runway 等）生成**，新手常誤以為 AI 對話框能「一鍵端到端渲染視頻」。
  - **`catliomoon` 工具限制回報**：指出若直接用 Muse 生成，單次最長限制為 10 秒影片。
- **原始資料對分析的影響**：若只看主文容易誤以為存在某個「直接在對話框跑完全程的端到端魔法」；納入留言串的用戶踩坑截圖後，證實本質仍是**「文字模型生腳本與提示詞＋外部圖生影模型（Flow/Runway/Kling）分段生成＋後製組裝」的傳統分段管線**。

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
  - **理由**：屬既有影音 SOP 的社群應用實例，技術結構未超出已收錄的影音生成範式；歸檔留存其「留言區揭露之 LLM 與外部影片工具分工本質」及社群回饋即可。
