---
id: "2026-11-19-shengan231202-guanyu-swiss-riso-poster-prompt"
title: "Threads 案例評估：學甲聖安殿關聖帝君「真圖+解構瑞士Riso風格抽象視覺標識」提示詞與神明海報實例"
source_url: "https://www.threads.com/@shengan231202/post/Df3-0yTn5O8"
source_platform: "Threads"
author: "@shengan231202 (學甲 - 聖安殿)"
analyzed_at: "2026-11-19"
analyzed_by: "antigravity"
source_review: partial
source_images: 2
source_replies: 3
source_reviewed_at: "2026-11-19"
source_review_note: "主貼文、2項媒體（1張海報圖+1段原像影片）與作者3則續樓（含完整兩段提示詞與轉載出處）完整讀取；73則網友留言受Threads登入牆阻擋"
status: archived
cluster: 2
cluster_role: "海報視覺解構Prompt"
short_title: "關聖帝君瑞士Riso海報"
tags:
  - image-generation
  - prompt-engineering
  - swiss-design
  - risograph
  - chatgpt
  - threads
---

# Threads 案例評估：學甲聖安殿關聖帝君「真圖+解構瑞士Riso風格抽象視覺標識」提示詞與神明海報實例

- **來源貼文**：[Threads 原貼文（`@shengan231202`）](https://www.threads.com/@shengan231202/post/Df3-0yTn5O8)（原分享連結 `https://www.threads.com/share/BAZnUVh7yg`）
- **發布平台 / 作者**：`Threads` / `@shengan231202`（學甲 - 聖安殿，引用自 `@zhengfamily0303` ChatGPT 生成範例）
- **分析日期**：`2026-11-19`
- **當前狀態**：`⚪ 封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-15-photo-riso-poster-evidence-abstraction-skill.md`](./2026-11-15-photo-riso-poster-evidence-abstraction-skill.md)（Photo-Riso-Poster 證據鏈提煉海報 Skill）

---

## 1. 原始資料盤點（主文、海報圖與實拍影片、作者 3 則續樓、留言狀態）

- **主貼文核心**：分享將宮廟神像實拍照轉製成「上實體攝影＋下幾何抽象符號」的高質感 3:4 直式海報提示詞，展示成品以「關聖帝君」神像實拍為基礎生成。
- **作者上傳媒體（共 2 項）**：
  1. **海報成品圖片（1 張）**：
     - **上半部（50%）**：真實攝影照片，保留紅面長鬚關聖帝君神像主體、繁複金飾神冠、黃綠紅刺繡神袍與神龕光影。
     - **下半部（50%）**：暖米白帶微顆粒質感的幾何抽象標識，中央以對稱幾何模組、線條與圓弧網格重構神冠、面容與神袍輪廓，配備色票（金黃/暗紅/深綠/黑）、文字排版（直排「關聖帝君」與英文「GUAN YU THE SAINT OF RIGHTEOUSNESS」）、標注節點與紅色篆書印章。
  2. **實拍原始影片（1 段）**：拍攝同一尊關聖帝君神像實景，證明上半部為真實照片延伸。
- **作者續樓與提示詞全文（共 3 則）**：
  - **續樓 1**：註明感謝原作者 `@zhengfamily0303`（於 2026-11-17 分享使用 ChatGPT 製作的範例）。
  - **續樓 2（提示詞第一段）**：
    - 設定 3:4 竪版海報，上下嚴格 1:1 分割（各 50%）。上半部為真實攝影，僅做輕量調色，自然延展背景，嚴禁拉伸扭曲主體；下半部提煉主體內核（輪廓、結構、姿態），不復刻完整物象，以幾何解構、模塊化、線條結構、負空間手法做成高端品牌視覺標識。風格指定：`post-digital graphic design`、`deconstructed Swiss design`、`generative symbol system`、`diagrammatic abstraction`。
  - **續樓 3（提示詞第二段）**：
    - 強調構圖克制與大面積留白，禁止堆砌多圖標或做成資訊圖表。文字僅作為檔案與實驗刊物式的極小索引標注；色彩從上圖提取標誌性色調搭配灰白/暖白底色；材質融合：`xerox texture`、`risograph grain`、`print registration error`、`scanner noise`、`subtle paper texture`，增加印刷錯位與噪點質感。
- **網友留言狀態（73 則受登入牆阻擋）**：主文顯示 73 則留言，未登入狀態下被 Threads 登入牆阻擋（「登入即可查看更多回覆」），僅完整讀到作者 3 則續樓。
- **原始資料對分析的影響**：作者完整提供了兩段提示詞原始碼與上游轉載出處，證實為社群流行之「瑞士解構主義 + Riso 印刷質感 + 上真下標識」提示詞流派。

---

## 2. 與既有系統之技術比對與評估

- **與既有筆記比對（`2026-11-15-photo-riso-poster-evidence-abstraction-skill`）**：
  - 在 `2026-11-15` 的筆記中，我們已深度評估過 GitHub 開源專案 `luckdvr/photo-riso-poster` 的 Skill 結構（同樣採用 2:1 或 1:1 分割、上攝影下 Riso 向量抽象解構、瑞士字體排版與印刷錯位）。
  - 本篇貼文是該風格在中文社群（特別是傳統民間信仰／宮廟文化題材）的直接實踐案例，印證了此類結構化提示詞（嚴格比例分割、禁止扭曲主體、幾何標識提煉、專用材質噪點詞彙）在 ChatGPT / DALL-E / Midjourney 等當前圖像模型上的可重現性與輸出穩定度。
- **對現有系統的意義**：
  - 提示詞語法完整、結構清晰（明確區隔了構圖邊界、風格流派、材質控制與文字角色），可作為生圖或多模態 Agent 生成設計海報時的高品質範本。
  - 核心架構已由 `photo-riso-poster` 覆蓋，無新增系統工具或工作流缺口。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：屬純提示詞（Prompt）與生圖案例分享，技術範式已在既有筆記 `2026-11-15-photo-riso-poster-evidence-abstraction-skill` 完整建檔並完成評估；歸檔留存其完整中文提示詞結構與文化題材應用案例即可。
