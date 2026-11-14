---
id: 2026-11-07-threads-canva-chinese-fonts-share-evaluation
title: "Threads「Canva 中文字型分享」貼文評估：7 款字型清單整理、簡轉繁與日本漢字缺字風險，以及對工程流程之低關聯性"
source_url: "https://www.threads.com/@thank______u/post/DfR_g81iShY"
source_platform: "Threads (@thank______u)"
author: "蘇蘇 (@thank______u)"
analyzed_at: 2026-11-07
analyzed_by: "Antigravity"
status: archived
cluster: "2"
cluster_role: "審美防線與字型排版"
short_title: "Canva 中文字型貼文評估"
tags:
  - canva
  - typography
  - chinese-fonts
  - presentation-design
---

# Threads「Canva 中文字型分享」貼文評估：7 款字型清單整理、簡轉繁與日本漢字缺字風險，以及對工程流程之低關聯性

- **來源連結**：[Threads 貼文：@thank______u](https://www.threads.com/@thank______u/post/DfR_g81iShY) ｜ [分享短網址](https://www.threads.com/share/BBheDT0vhn)
- **抓取時間**：2026-11-07（貼文約 3 天前發布，183K views、8K 讚、67 留言、5.5K 轉發）
- **歸屬集群**：集群 2：Code-as-Video、視覺特效與 Generative UI（角色：`Canva 簡報與視覺字型速查`）
- **評估結論**：`🔴 工程價值無／僅留字型清單備查`：不衍生任何任務

---

## 1. 貼文內容與結構拆解

作者「蘇蘇（`@thank______u`）」發布「`\ Canva 中文字型來啦 ༘♡ /`」，封面寫「不藏私分享 21 款中文字型！（Part 1）」，實際於本篇輪播圖中列出 **7 款** Canva 內建漢字字型（每張配一句搞笑語錄吸引收藏），並在置頂留言放上個人商業空間／商品攝影作品集，招攬攝影委託與美編設計課程。

留言區絕大多數為「存」「留」「留己看」等書籤式互動，屬於典型的社群「工具書／懶人包引流」貼文。

---

## 2. 圖卡中的 7 款 Canva 字型清單與技術注意事項

為省去日後翻找圖片的時間，直接將 9 張圖卡中的 7 款字型名稱、費用標記與字集風險整理如下：

| # | Canva 搜尋名稱 | 方案需求 | 風格分類 | 字集來源與繁體中文使用風險 |
|---|---|---|---|---|
| 1 | `可畫長美黑-繁` | 免費 | 窄長美術黑體 | Canva 官方繁體化字型，適合主標題，繁中字集較完整 |
| 2 | `字由点字像素16 简体中文` | 👑 Pro | 16px 點陣像素體 | **簡體字集**：部分繁體字會缺字（Tofu 空白框）或退回預設字型 |
| 3 | `UD角ゴC70` | 👑 Pro | 日本通用設計黑體（粗） | **日文 JIS 漢字**（是否為 Morisawa BIZ/UD 系列：未查證）：繁體字可能缺字，未實測 |
| 4 | `可畫牛奶餅乾-繁` | 免費 | 圓潤可愛美術體 | Canva 官方繁體化字型，適合社群圖卡短標 |
| 5 | `可畫新哥德體-繁` | 免費 | 裝飾哥德風字體 | Canva 官方繁體化字型，筆畫末端帶尖角裝飾，僅適合大字標題 |
| 6 | `可画轻中宋-繁` | 免費 | 現代扁平宋體 | 搜尋名稱為簡體「可画轻中宋」，但掛 `-繁` 後綴支援繁體 |
| 7 | `UD明朝 (N仕様)` | 免費 | 日本通用設計明朝體 | **日文 JIS 漢字**：同第 3 款，適合簡報短標題，長文需留意台日漢字差異與缺字 |

---

## 3. 評估結論與待辦

```text
貼文性質：社群美編字型懶人包（Part 1，7 款）＋ 攝影課程工商引流
工程關聯：無（Canva 封閉端內建字型，無法直接用於本機 CSS / Remotion / Code-as-Video 渲染）
處置方式：將 7 款字型名稱轉為純文字表格留存備查，不衍生工程任務
```

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

本篇**不衍生任何待辦任務**。理由：純屬 Canva 介面內的字型名稱收藏，無涉及 AI Agent、API、自動化或可重用之工程架構。若日後在 Canva 製作簡報或社群圖卡，直接查閱本筆記第 2 節表格即可。
