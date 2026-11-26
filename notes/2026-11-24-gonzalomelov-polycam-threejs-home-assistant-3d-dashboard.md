---
id: "2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard"
title: "X 貼文評析：Gonzalo Melo 以 Polycam + 每房 4 張照片 + GPT-6 Astra 打造 Home Assistant 3D 數位孿生控制面板"
source_url: "https://x.com/gonzalomelov/status/2096610464545325097"
source_platform: "x"
author: "Gonzalo Melo (@gonzalomelov)"
analyzed_at: "2026-11-24"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9; codex/gpt-6.1-sol@01a2125a-4d1e-73b1-86ee-52ace903a7f4; codex/gpt-6.2-sol@01a21765-3f7c-7ed1-93a3-ae4311b8a38b"
revised_at: "2026-11-26"
source_review: full
source_images: 1
source_replies: 2
source_reviewed_at: "2026-11-26"
source_review_note: "依 2026-11-25 Chrome review 報告：影片 1 部（source_images 依報告計 1，靜態圖 0 張），登入後回覆計數 2、讀到 2，全部顯示，改為 full。兩則留言依報告，未自行核對；前次已直連 X 公開影片核對 00:01、00:04、00:26 畫面。 2026-11-26 Chrome 再審另查得 1 則引用，未計入回覆數。此次引用內容依再審報告。"
status: pending
cluster: 2
cluster_role: "3D智慧家庭儀表板"
short_title: "3D智慧家庭數位孿生"
tags:
  - threejs
  - home-assistant
  - polycam
  - gpt-6-astra
  - digital-twin
  - spatial-computing
  - generative-ui
---

# X 貼文評析：Gonzalo Melo 以 Polycam + 每房 4 張照片 + GPT-6 Astra 打造 Home Assistant 3D 數位孿生控制面板

- **來源貼文**：[Gonzalo Melo on X](https://x.com/gonzalomelov/status/2096610464545325097)（回覆 OpenAI Developers 24 小時挑戰 [`@OpenAIDevs/status/2096259745501921758`](https://x.com/OpenAIDevs/status/2096259745501921758)）
- **發布平台 / 作者**：`x.com` / `Gonzalo Melo (@gonzalomelov)`（發布於 `2026-09-06 22:44` UTC+8 瀏覽器時區）
- **開源倉庫**：無（貼文未附程式碼連結；2026-11-24 查核 `github.com/gonzalomelov` 公開倉庫清單亦無此專案）
- **分析日期**：`2026-11-24`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-26-3d-model-anything-iphone-lidar-threejs.md`](./2026-10-26-3d-model-anything-iphone-lidar-threejs.md)（`wesbos/3d-model-anything`：LiDAR 空間掃描與 Three.js 重建閉環；作者 Wes Bos 當時於留言表示「下一步想接智慧家庭」）
  - [`docs/scan-to-threejs-spatial-agent-spec.md`](../docs/scan-to-threejs-spatial-agent-spec.md)（空間運算 Agent 坐標契約與視覺比對閉環）
  - [`assets/spatial-room-viewer/index.html`](../assets/spatial-room-viewer/index.html)（單檔 Three.js 空間漫遊展示範本）

---

## 0. 原始資料盤點（貼文正文、43 秒示範影片與留言區）

- **貼文脈絡與正文（逐字重點）**：
  - 該貼文為參與 `@OpenAIDevs`「What can you ship with GPT-6 Astra? (24 hours)」活動之展示，互動數據為 2 則回覆、2 則轉貼、38 個喜歡、29 個書籤、4,800 次瀏覽。
  - 核心作法：以 **Polycam**（`@Polycam3D`）室內掃描加上**每個房間 4 張照片**與一份**一頁規格書（one-page spec）**作為輸入，由 **GPT-6 Astra** 為每個房間生成**程序化 Three.js（procedural Three.js）**程式碼，整合進 **Home Assistant**（`@home_assistant`）成為即時 3D 儀表板；點擊 3D 渲染場景中的燈具即可控制實體燈光開關。
- **附帶媒體（靜態圖 0 張、示範影片 1 部 `00:43`，最高解析度 `1440×900`）**：
  - `00:00–00:04`：先顯示 Home Assistant 的 `Overview` 頁；`00:01` 可見歡迎文字與 Areas 卡片（Living Room、Kitchen、Bedroom、Study、Barbecue、Bathroom、Devices），約 `00:04` 切到 `Home` 頁後才呈現空白載入。本次直接核對公開影片；報告將 `Barbecue` 誤記為 `Balcony`，此處依畫面更正。
  - `00:09–00:20`：載入完成後呈深色背景**全屋等角視角（Isometric）3D 數位孿生模型**，右上角顯示即時天氣（`8.5 °C`、`cloudy · 54% humidity · wind 22 km/h`）。場景內各房間標註即時感測器與裝置狀態：`Sofa camera offline`、`DINING`、`Fridge 5°`、`HALLWAY`、`BEDROOM`、`Bedroom TV off`、`Floodlight off`，以及 `STUDY` 內的雙螢幕桌、`Gonzalo` 人員追蹤標籤、`Floor lamp off`、智慧燈泡（`100% · 2700 K` / `100% · 6500 K`）、智慧插座即時功耗（`0 W`）、電暖器等。示範者可拖曳旋轉並縮放拉近視角。
  - `00:26`：點擊 3D 書房場景中的燈具後，介面彈出 Home Assistant 原生裝置控制卡片：`Study > WiZ 824512`（副標題 `Wiz`；省略畫面中的區域網路 IP），顯示 `Off (1 minute ago)`、亮度滑桿、開關／模式切換、4 個色溫預設按鈕及底部 `Effect` 按鈕；裝置名稱已直接核對公開影片。
  - `00:30–00:41`：顯示書房燈光狀態變更為開啟（`100% · 2700 K`）並將鏡頭拉回全屋 3D 俯視角度。
- **留言區**：依 [Chrome review 報告](../reviews/reports/2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard/2026-11-25-01-review-claude.md)，登入後回覆計數 2、讀到 2，全部顯示；以下兩則依報告，未自行核對：
  - John Perrone（`@jjperrone`，9 月 25 日）：原以為需要會 3D 建模，看到掃描加每房 4 張照片後覺得可行，想當週末專案；無技術質疑或更正。
  - `@oprfwa`（9 月 28 日）：正面稱讚，無技術補充。
- **引用貼文**：依 [2026-11-26 Chrome 再審報告](../reviews/reports/2026-11-24-gonzalomelov-polycam-threejs-home-assistant-3d-dashboard/2026-11-26-02-review-claude.md)，Polycam 官方帳號 @Polycam3D 於 9 月 11 日引用貼文，稱這是 Polycam 掃描資料搭配 Astra 的創意用法。這則引用未提供技術驗證，另計於 2 則串內回覆之外。
- **前次修正影響與來源**：依登入後報告解除留言缺漏、改為 `full`；另從 [X 公開媒體資料](https://cdn.syndication.twimg.com/tweet-result?id=2096610464545325097&token=1) 取得[公開影片](https://video.twimg.com/amplify_video/2096609477940142080/vid/avc1/1440x900/6tJKyVMwPz4coyMz.mp4)，核對開場時序與燈具名稱。這些更正不增加原始碼或可重現性的證據。

---

## 1. 技術架構拆解與證據邊界

```text
[輸入素材]
  ├── Polycam 3D 室內掃描（提供整體空間拓撲與比例尺）
  ├── 每房間 4 張照片（提供家具外觀、材質與燈具位置證據）
  └── 一頁規格書（One-page spec：定義 Home Assistant Entity 對應與介面需求）
        │
        ▼ (交由 GPT-6 Astra 生成)
[程序化 Three.js 房間模組]
  ├── 幾何物件分層（牆面、地板、家具與可點擊裝置 Mesh）
  ├── 裝置狀態標籤疊加（Entity ID 綁定：溫度、功耗 W、人員追蹤、開關/色溫）
  └── Raycasting 點擊事件 ──► 觸發 Home Assistant 原生對話框 (`more-info` / WiZ 燈控卡)
```

### 證據分級與關鍵限制（不當作已驗證量產規格）

1. **已確認（影片與貼文直接可證）**：作者成功在 Home Assistant 介面中嵌入可拖曳縮放的 Three.js 全屋 3D 場景，並實作「3D 物件點擊（Raycasting）→ 開啟 Home Assistant 原生裝置控制卡（WiZ 燈具）→ 狀態即時更新（`100% · 2700 K`）」的完整互動閉環。
2. **未揭露／未查證（黑盒展示限制）**：
   - **無開源原始碼與 Prompt**：貼文未附 GitHub repo，亦未公開該「一頁規格書（one-page spec）」、Polycam 匯出格式（OBJ/glTF/點雲）或 Home Assistant Custom Card / Panel 實作代碼。
   - **無生成成本與修正次數數據**：雖係參加 24 小時挑戰的作品，但貼文未說明 Astra 是一次生成抑或歷經多次人工除錯與視覺校準才完成。

---

## 2. 與既有專案的比較及架構啟發

| 比較維度 | [`wesbos/3d-model-anything`](./2026-10-26-3d-model-anything-iphone-lidar-threejs.md)（2026-10-26） | `@gonzalomelov` 3D Home Assistant（2026-09-06） |
| :--- | :--- | :--- |
| **空間採集端** | 自寫 iOS App（LiDAR + RoomPlan + `frames.json` 相機內參） | 現成商業工具 **Polycam** 掃描 + 每房 4 張照片 |
| **生成模型與做法** | GPT-6 Astra + `scan-to-threejs` Skill（含 `cmp.sh` 同位姿比對閉環） | GPT-6 Astra 依一頁規格與照片撰寫程序化 Three.js |
| **核心目標** | 高擬真可漫遊 3D 空間模型（Dollhouse / Walking / Overlay） | **IoT 數位孿生監控與雙向控制**（綁定感測器數值與實體開關） |
| **開源與可重現性** | 完整 MIT 開源（含 Skill、腳本與 Viewer） | **無開源代碼**（僅 43 秒演示影片與概念驗證） |

- **對本專案空間資產的具體補強點**：
  - 本儲存庫既有 [`docs/scan-to-threejs-spatial-agent-spec.md`](../docs/scan-to-threejs-spatial-agent-spec.md) 已涵蓋「LiDAR / RoomPlan → Three.js 坐標契約與視覺比對閉環」，但尚未定義**「3D 場景網格節點（Mesh）如何與外部感測器／智慧家電 Entity 綁定（Metadata Binding & Raycasting）」**。
  - 若未來需要將 `assets/spatial-room-viewer/index.html` 從純靜態展示延伸為即時監控／數位孿生面板，只需為可互動裝置 Mesh 加上標準化的 `userData.entityId` 綁定契約與標籤投影（CSS2DRenderer / HUD Overlay）規格即可，無需重寫底層建模規範。

---

## 3. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261124-01`**｜**[優先級：低]** 在 `docs/scan-to-threejs-spatial-agent-spec.md` 增補「3D 數位孿生裝置節點（`entityId`）綁定、狀態 HUD 投影與點擊事件（Raycasting）回呼契約」章節
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\scan-to-threejs-spatial-agent-spec.md`（收錄於集群 2；僅擴充規格，不強制引入 Home Assistant 實機部署）
  - **執行步驟**：
    1. 參照 `@gonzalomelov` 示範之裝置標籤（開關狀態、色溫/亮度、功耗 `W`、離線警告與人員位置）與點擊控制卡互動模式，定義 Three.js 裝置 Mesh 的 `userData` 綁定欄位（`entityId`、`domain`、`deviceClass`、`labelAnchor`）。
    2. 規範「狀態只讀訂閱（State Sync）」與「點擊觸發控制回呼（Raycasting `onEntitySelect`）」的隔離邊界，明確標註本案原貼文無開源代碼、屬概念驗證參考。
  - **驗收標準（DoD）**：`docs/scan-to-threejs-spatial-agent-spec.md` 新增數位孿生裝置綁定與 Raycasting 互動契約章節，明註概念驗證邊界，且 `python tools/verify_inbox.py` 驗證通過。
