---
id: "2026-11-27-tracy-ai-claude-blender-edimakor-mv-eval"
title: "Tracy AI小妹：Claude＋Blender＋Edimakor AI 電影與音樂 MV 工作流實測評估"
source_url: "https://www.youtube.com/watch?v=KEPovpoio9U"
source_platform: "YouTube (@Tracy_AI-Channel)"
author: "Tracy AI小妹"
analyzed_at: "2026-11-27"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_reviewed_at: "2026-11-27"
source_images: 11
source_replies: 2
tags:
  - ai-video
  - blender
  - bpy
  - edimakor
  - music-video
  - prompt-engineering
  - workflow
status: pending
cluster: 2
cluster_role: "Blender灰盒控片"
short_title: "Claude+Blender控片教學"
---

# Tracy AI小妹：Claude＋Blender＋Edimakor AI 電影與音樂 MV 工作流實測評估

- **來源連結**：[完全不會 Blender 也能做 AI 電影？Claude＋Blender＋Edimakor 完整教學，輸入歌曲和人物圖片，3分鐘打造專屬音樂MV](https://www.youtube.com/watch?v=KEPovpoio9U)
- **發布平台 / 作者**：`YouTube` / `Tracy AI小妹 (@Tracy_AI-Channel)`（訂閱 1.45 萬，2026-09-12 發布，片長 `09:17`，觀看 2,726 次，按讚 39）
- **分析日期**：`2026-11-27`
- **當前狀態**：`🔴 未做 (Pending)`

---

## 0. 原始資料盤點

> 透過 `tools/video_transcript.py`（`CUDA`、`small` 模型）完整轉寫 557 秒音訊逐字稿，並以無頭瀏覽器開啟原頁面讀取完整資訊欄、時間軸、2 則公開留言（0 則網友回覆），並檢視 11 個時間點畫面截圖。

- **影片關鍵畫面截圖（11 個時間點）**：
  - `0:57`、`1:21`：Claude 免費版網頁介面生成 Blender Python（`import bpy`、`import math`）腳本（Artifact `Parkour character PY` / `Parkour obstacle course`，含 `COURSE` 動作清單 `"run"`、`"vault"`、`"gap"`、`"wall"`），並附操作步驟（貼入 `Blender → Scripting → Run Script (Alt+P)` 並輸出 `FFmpeg / MPEG-4`）。
  - `1:53`：Edimakor 官網介紹頁（主打 `AI 數位人`、`圖片轉影片`、`自动字幕` 與 `Veo 3.1` 試用）。
  - `2:14`、`2:48`：HitPaw Edimakor 桌面端 `AI影片 → 影片參考` 介面，右上提示 `Wan 3.0 已上線!`，選用 `MiniMax H3 HOT`；`參考媒體（影片 1/3、圖片 1/9、音訊 0/3）` 同時上傳 4 秒灰模 Blender 跑酷片段與多視角粉髮角色資料卡，輸出 `768P` / `2K` 災難逃生風格影片。
  - `3:43`：文生影片示範畫面，對應資訊欄「中國水墨畫＋日系地下雜誌編輯風格」實驗性 2D MV 提示詞（含朱紅印章、書法直排條幅）。
  - `4:38`：AI 模仿音樂生成段（B-roll 示意畫面，並引導觀看頻道先前影片）。
  - `5:55`、`6:30`：`Edimakor.ai` 網頁版 `AI 音樂影片` 介面：可選 `敘事型影片` 或 `演唱型影片`、上傳 `10秒–180秒` 含人聲音訊（`MP3/AAC/M4A/WAV`，不支援純音樂）、最多 7 張角色圖、比例（`9:16`、`16:9`、`1:1`、`4:3`、`3:4`）與解析度（`540p`/`720p`/`1080p`）；並展示港風夜晚車內雨景敘事 MV 片段。
  - `8:22`：HitPaw Edimakor 桌面端 `AI影片 → AI 舞蹈`，選用 `Kling 3.0 Motion Control`，上傳單張全身人像照搭配舞蹈模板。
  - `9:00`：HitPaw Edimakor 個人版台幣定價表（Windows）：1 個月 `NT$580`（原價 `NT$890`，300 點/月）、1 年 `NT$1,580`（原價 `NT$1,880`，終身免費升級＋10,000 AI 點數/永久）、永久版 `NT$2,180`（原價 `NT$2,880`，終身免費升級＋10,000 AI 點數/永久，1 台電腦）。
- **作者資訊欄補充**：
  - 提供 Edimakor 導流短網址（`reurl.cc/zOQeNe`）、Blender 官方下載頁、相關評測影片連結（Genspark、Genki AI、Edimakor `GPT Image 2 + Seedance 2.0`、Focal AI、Freebeat AI），以及文末完整的「30 秒 16:9 中國水墨畫×日系地下雜誌風格實驗性音樂 MV」中文提示詞（含鼓點硬切、鈸響定格、高潮拼貼堆疊等節奏提示）。未附任何 GitHub repo。
- **留言區重點（共 2 則）**：
  - 置頂留言與第二則留言皆為頻道主 `@Tracy_AI-Channel` 本人發布，分別放 Edimakor 下載短網址與與資訊欄相同的 13 段章節時間軸；無其他網友實測回覆或勘誤。
- **對分析的影響**：
  - 確認本片屬 **HitPaw Edimakor 商業推廣／導流教學**（無開源專案或可審查程式碼）；但畫面證實「免費版 Claude 生成 `bpy` 灰盒跑酷片 → 作為 Video-to-Video 運鏡參考輸入」的具體接法可獨立於 Edimakor 存在。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who**：YouTube 創作者 `Tracy AI小妹`（`2026-09-12` 發布，含 HitPaw Edimakor 分潤導流連結）。
- **What**：示範一條結合「LLM 生成 Blender Python 腳本」與「商業 AI 剪輯軟體 HitPaw Edimakor（桌面端＋`Edimakor.ai` 網頁端）」的影片／音樂 MV 製作流程。
- **Why**：單純靠文字提示詞難以精準控制 AI 生成影片的運鏡與角色動態；作者主張先用 Blender 產出低門檻灰盒（graybox）動作與鏡頭參考片，再交由影片生成模型重繪風格與場景。
- **How**：
  ```text
  [免費版 Claude 網頁] ──生成 bpy 腳本──▶ [Blender Scripting (Alt+P)] ──算圖 MP4──┐
                                                                                 ├──▶ [Video-to-Video 模型 (MiniMax H3)] ──▶ 2K/4K 增強
  [GPT Image 角色資料卡 (多視角)] ───────────────────────────────────────────────┘

  [AI 參考音樂翻唱/改編] + [AI 歌詞] + [角色圖 1–7 張] ──▶ [Edimakor.ai 網頁版] ──▶ 敘事型 MV / 對嘴演唱型 MV
  ```
- **When & Where**：適合零 3D 基礎、想快速驗證「動態運鏡草圖 → AI 風格化重繪」或低門檻試作短影音／MV 雛形的個人創作者。
- **Key Metrics / Numbers**：
  - 影片生成長度：片中示範 `Wan 3.0` 最長可生成 30 秒單段影片；`Edimakor.ai` AI 音樂影片支援 `10–180 秒` 含人聲音訊、最多 7 張參考圖、最高 `1080p`，單次產生等待約 `3–5 分鐘`。
  - 授權與點數：桌面終身版 `NT$2,180`（1 台電腦、含 10,000 永久 AI 點數），換算表列「AI 文字/圖片轉影片約 63 次、AI 影片生成器約 667 次」。

---

## 2. CQR 深入論證檢驗（宣傳宣稱核對）

- **Claim（影片標題與敘事主張）**：「完全不會 Blender 也能做 AI 電影」「輸入歌曲和人物圖片，3 分鐘打造專屬音樂 MV」。
- **Evidence（片中實際呈現）**：
  - Blender 跑酷骨架確實由免費版 Claude 寫出 `bpy` 並成功在視口跑動，但作者在口白（`01:16`）自行承認目前做出來的效果「還比較粗糙」。
  - `06:10` 口白說明光是在 `Edimakor.ai` 按下產生後就要「等待 3 到 5 分鐘」，尚未計入 Blender 腳本除錯、音樂翻唱、歌詞與角色圖生成時間。
  - 模型效果僅以單一提示詞展示片段成片，無多組對照實驗或失敗率統計。
- **Reasoning（推論局限與商業偏誤）**：
  - 「3 分鐘打造 MV」屬標題行銷誇飾；實際全流程（跨 Blender 與多頁工具切換）遠高於 3 分鐘。
  - 片中將 `MiniMax H3`、`Wan 3.0`、`Kling 3.0 Motion Control`、`GPT Image` 包裝在 HitPaw Edimakor 單一訂閱／買斷殼下推廣；對已具備獨立模型／API 或本機工具鏈的開發者而言，商業整合軟體並非必要依賴，且「終身 10,000 點」受限於高消耗模型（例如轉影片僅約 63 次）仍屬消耗型點數。

---

## 3. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - [`docs/3d-gui-agent-control-bridge.md`](../docs/3d-gui-agent-control-bridge.md)（已涵蓋 `blender-mcp` / `CLI-Anything` 控制路徑）
  - [`notes/2026-11-15-higgsfield-mcp-opus55-video-review-report.md`](./2026-11-15-higgsfield-mcp-opus55-video-review-report.md)（已定義全身三視角色表作為一致性參考）
  - [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)（本庫獨立出去的程式化影片與分鏡工作室）
- **落差與採納判斷**：
  - **值得採納的部分**：
    1. **免 MCP / 零訂閱「`bpy` 灰盒運鏡參考片」工作模式**：即使不部署 `blender-mcp` 或 `CLI-Anything`，單純讓 LLM 輸出獨立 `bpy` 腳本在 Blender 執行算圖出 4 秒灰盒動態片，搭配「角色資料卡」作為雙輸入參考，即可把鏡頭運動與時間軸從純文字隨機性中抽離。
    2. **音樂 MV 提示詞的節奏錨點寫法**：資訊欄示範的「每記鼓聲觸發硬切／快速變焦、鈸響定格、高潮隨滾奏堆疊拼貼」可作為 `code-as-video-studio` 音畫同步分鏡提示詞的參考語彙。
  - **不適用 / 不採納的部分**：
    - **不採納 HitPaw Edimakor 軟體與其點數方案**：屬閉源商業包裝且具明顯分潤導流性質，功能可由現有獨立模型 API 或開源／本機工作流取代，不列入採購或部署待辦。

---

## 4. 拆解待辦事項（Action Items）

- [ ] **`T-20261127-01`**｜**[優先級：低]** 在 `docs/3d-gui-agent-control-bridge.md` 補充「免 MCP 之 `bpy` 灰盒運鏡參考片 → Video-to-Video 雙輸入控片」輕量替代路徑
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\3d-gui-agent-control-bridge.md`（收錄於集群 2）
  - **具體做法**：於文件既有 Blender 控制章節補充一節，說明何時不需架設 `blender-mcp` / `CLI-Anything`，直接由 LLM 產生一次性 `bpy` 腳本產出灰盒運鏡 MP4，並搭配多視角角色資料卡餵給 Video-to-Video 模型（對照自來影片 2026-11-27 實測模式，註明不綁定特定商業軟體 Edimakor）。
  - **驗收標準（DoD）**：`docs/3d-gui-agent-control-bridge.md` 完成增補，且執行 `python tools/verify_inbox.py` 驗證通過。
  - **完成日期**：
  - **實作紀錄 / 證據**：
