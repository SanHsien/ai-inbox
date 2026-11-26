---
id: "2026-11-26-comfyui-seedance-ai-comic-drama-fact-check"
title: "YouTube「ComfyUI+Seedance2.5 全流程自動化製作 AI 漫劇（51 分鐘）」畫面查證與節點架構拆解"
source_url: "https://youtu.be/MIf8wDBlXog"
source_platform: "YouTube"
author: "AI漫剧制作教程 (@Justin-w7m2f / 畫面浮水印：上语AI SHANGYU AI)"
analyzed_at: "2026-11-26"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: full
source_images: 0
source_replies: 276
source_reviewed_at: "2026-11-26"
status: archived
cluster: 4
cluster_role: "ComfyUI漫劇拆解"
short_title: "ComfyUI漫劇工作流查證"
tags:
  - ai-video
  - ai-drama
  - comfyui
  - fact-check
  - monetization
  - youtube
---

# YouTube「ComfyUI+Seedance2.5 全流程自動化製作 AI 漫劇（51 分鐘）」畫面查證與節點架構拆解

- **來源影片**：[【2026九月最新ComfyUI漫劇工作流】AI漫劇變天了！ComfyUI+Seedance2.5，手把手教你從0到1全流程自動化製作AI漫劇！穩定出片！](https://www.youtube.com/watch?v=MIf8wDBlXog)（`2026-09-02` 發布，片長 `51:05`，56,915 次觀看、880 讚、276 則留言）
- **同頻道前案**：[YouTube「小說改編 AI 真人短劇全流程」導流話術查證](2026-11-15-ai-comic-drama-novel-adaptation-fact-check.md)

---

## 核心結論

這是同頻道（`AI漫剧制作教程`）的課程導流教學片：標題宣稱「ComfyUI+Seedance2.5 全流程自動化」，但影片說明欄**無任何 GitHub Repo、工作流 JSON 或工具連結**，僅附一組導向微信公眾號的純文字引流碼（`mp.weixin.qq.com/s/KDqODXQMFTh7bik0oztV7w`），且畫面浮水印為培訓機構 `上语AI / SHANGYU AI`。實測取樣畫面顯示，所謂流程實為**多工具人工分段串接**（RunningHub 雲端 ComfyUI 生圖 + 資產規劃表 + 即夢 AI 封面 + 剪映手動剪輯），並非一鍵全自動管線。歸檔作為引流話術辨識與 ComfyUI 節點組合參考，不另開實作任務。

---

## 一、畫面實測拆解：真實用到的節點與工具鏈

影片未提供字幕與逐字稿（`captionTracks` 為空），透過取樣關鍵影格（`0:12`、`10:13`、`20:27`、`33:11`、`44:56`）還原其實際工作流如下：

1. **雲端 ComfyUI 靜態資產生成（RunningHub，`10:13`）**：
   - 在 **RunningHub**（`高可用云端C...`）執行 ComfyUI，可見核心模型節點為：
     - UNET：`z_image_turbo_bf16.safetensors`
     - CLIP：`qwen_3_4b.safetensors`（類型 `qwen_image`）
     - VAE：`z_image_turbo-vae.safetensors`
     - 搭配多組 `LoRA加载器(仅模型)`、`K采样器`（10 steps、CFG 1.0、`euler`、`simple`）與 `空Latent`（`1080×1920` 豎屏）。
2. **資產分表設計（`20:27`）**：
   - 將漫劇素材拆為四大類先生成後組裝：**人物**（依狀態分檔，如 `带伤男主`、`干净男主`、`银发正装男主`、`混混配角`、`特战 NPC`）、**現代場景**（`老式出租屋`）、**古代場景**（`云雾峡谷`、`古城墙城门`、`古风集市`）、**關鍵道具**（`黄金御轿`、`古旧卷轴`）。
3. **後製剪輯與封面分離（`33:11`、`44:56`）**：
   - **剪映（JianyingPro）**：手動載入片段進時間軸進行配樂與音效疊加（`第6节-画面配乐与音效`）。
   - **即夢 AI（圖片 5.0 Lite，9:16 2K）**：單獨生成豎屏海報與標題文字（強調「圖片和文字分開生成的狀態」）。

---

## 二、留言區關鍵實務訊號

276 則留言多為「666」「求資料包」等互動（無置頂留言），唯一具備技術含金量的對話來自：
- `@color1580`：`我覺得ComfyUI最麻煩的點 就是每一次更新都有可能導致現有工作流崩壞`
- `@twowinydmnfex2`：`現在可以免費串上Claude讓他自己去搞~`

反映出實際落地時，ComfyUI 自訂節點與工作流 JSON 的**版本依賴脆性**遠高於商業 SaaS，且社群已開始轉向以 Coding Agent（如 Claude）協助排錯與維護環境。

---

## 三、評估與歸檔結論

- **可取之處**：`Z-Image-Turbo` + `Qwen-3-4B` 的低步數（10 steps / CFG 1.0）`1080×1920` 豎屏生圖參數，以及「角色依受傷／服裝狀態拆分資產」的製片思路，可用於一般分鏡一致性的資產準備參考。
- **不採信宣稱**：無開源工作流可驗證「Seedance 2.5 全流程自動化」，本質仍為多平台手動切換與微信私域引流課程，狀態設為 `archived`。
