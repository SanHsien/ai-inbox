---
id: 2026-10-26-3d-model-anything-iphone-lidar-threejs
title: "3D Model Anything 深度解析：iPhone LiDAR 空間掃描、Three.js 程式化三維重建與 Agent 視覺比對閉環"
source_url: "https://github.com/wesbos/3d-model-anything"
source_platform: "GitHub (wesbos/3d-model-anything) / Threads"
author: "Wes Bos / 李昱翰 (@leeunhn)"
analyzed_at: 2026-10-26
analyzed_by: "Antigravity"
status: done
cluster: 2
cluster_role: "LiDAR空間重建"
short_title: "3D Model Anything"
tags:
  - threejs
  - lidar-scanning
  - spatial-computing
  - agent-skills
  - visual-verification
  - ios-roomplan
---

# 3D Model Anything 深度解析：iPhone LiDAR 空間掃描、Three.js 程式化三維重建與 Agent 視覺比對閉環

- **官方開源倉庫**：[`wesbos/3d-model-anything`](https://github.com/wesbos/3d-model-anything) ｜ MIT License
- **在線展示**：[Wes Bos Office 3D Viewer](https://wesbos.github.io/3d-model-anything/) ｜ [YouTube 介紹](https://www.youtube.com/watch?v=JGQCcCzuS88)
- **社群引介來源**：[Threads 貼文（李昱翰 @leeunhn）](https://www.threads.com/@leeunhn/post/De3ViwPkt0-) ｜ [分享短鏈](https://www.threads.com/share/BAPezaO6q6/)
- **分析主題**：空間運算（Spatial Computing）、iPhone LiDAR + RoomPlan 數據捕獲、Three.js 程式化可編輯建模、AI Coding Agent 專屬技能（`scan-to-threejs`）與相機內參視覺對齊閉環
- **分析日期**：`2026-10-26`
- **當前狀態**：`🟢 已完成 (Done)`
- **相關交叉參照**：
  - [`notes/2026-10-18-target-story-generative-ui-editor.md`](./2026-10-18-target-story-generative-ui-editor.md)（Generative UI 互動產品設計與狀態管理）
  - [`notes/2026-10-26-answer-me-with-html-visual-agent-artifacts.md`](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md)（工件輸出與確定性版面計算）

---

## 1. 核心內容摘要與專案背景（Key Insights）

社群作者李昱翰（`@leeunhn`）引介了知名全端工程大師、Syntax 播客主持人 **Wes Bos** 的重磅開源專案 **`3D Model Anything`（`wesbos/3d-model-anything`）**。

過去若想將實體房間或室內空間數位化為可編輯的 3D 模型，通常需要昂貴的工業級雷射掃描儀、複雜的攝影測量（Photogrammetry）軟體，或是手動在 Blender/3ds Max 中艱苦描線。

Wes Bos 提出了一種顛覆性的工作流：**「iPhone LiDAR 空間實體證據記錄 + AI Coding Agent 漸進式程式化重建 + 瀏覽器端 Three.js 零依賴漫遊」**。

### 1.1 核心工作流三位一體
1. **空間測量與影像取證（iOS App: `house-capture`）**：
   利用配備 LiDAR 的 iPhone/iPad，結合 Apple RoomPlan 與 ARKit，在空間中走動掃描。App 記錄下房間結構幾何、牆面門窗開口、物體邊界盒（Bounding Boxes）、相機內參（Camera Intrinsics）與一組精確定位的照片（Posed Photographs）。
2. **AI Coding Agent 專屬技能（`scan-to-threejs`）**：
   Wes Bos 不追求黑盒子式的「單鍵轉模型」，而是將房間建模定義為 **AI 代理人的反覆運算式工程任務（Iterative Reconstruction Workflow）**。Agent 讀取物理測量證據，以純 JavaScript/TypeScript 編寫語意明確、幾何分層的 Three.js 程式碼，重建房間、地板、天花板與家具。
3. **多視角網頁互動檢視器（Three.js Viewer）**：
   在瀏覽器中直接開啟，支援第一人稱漫遊（Walking / FPV）、娃娃屋（Dollhouse）、俯視圖（Overhead）、線框模式（Wireframe）、零件平鋪（Knolling）與實景相片疊合（Overlay），流暢運行於現代 Web 端。

---

## 2. 深入技術拆解與架構原理（Deep Dive）

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    3D Model Anything 系統工作流架構                     │
└─────────────────────────────────────────────────────────────────────────┘

  [ 物理空間實體 ]
        │
        ▼ 攜帶 iPhone/iPad LiDAR 掃描房間
 ┌──────────────────────────────────────────────────┐
 │ iOS App (apps/house-capture)                     │
 │ 1. RoomPlan JSON (牆體開口、物體 Bounding Boxes) │
 │ 2. 定位照片集 (Posed Photos + Camera Intrinsics)  │
 │ 3. 點雲與深度圖 (Optional Depth / Mesh)          │
 └──────┬───────────────────────────────────────────┘
        │ 匯出至 data/captures-in/<room>/
        ▼
 ┌──────────────────────────────────────────────────┐
 │ AI Coding Agent (.agents/skills/scan-to-threejs) │
 │ 1. 座標系統歸一化 (Meters, +Y Up, Floor Zero)    │
 │ 2. 幾何分層建模 (地板/牆壁/開口 優先於 家具裝飾) │
 │ 3. Matched-Camera 視角並排比對 (cmp_photo.sh)    │
 │ 4. 識別視覺偏差並精準修正 Three.js 程式碼        │
 └──────┬───────────────────────────────────────────┘
        │ 輸出結構化 Three.js 模組 (demos/<id>/room.ts)
        ▼
 ┌──────────────────────────────────────────────────┐
 │ 瀏覽器端檢視器 (Vite + Three.js Viewer)          │
 │ ・Dollhouse (娃娃屋模式)                         │
 │ ・Walking (第一人稱漫遊，WASD + 滑鼠視角)        │
 │ ・Overlay (模型與相片對齊疊合檢查)               │
 │ ・Knolling (家具組件拆解展示)                    │
 └──────────────────────────────────────────────────┘
```

### 2.1 坐標系契約與幾何分層準則（Spatial Coordinate Contract）
`scan-to-threejs` 定義了嚴格的坐標與物理量契約，杜絕 Agent 在空間建模時產生尺度混亂：
- **標準度量衡**：所有長度以**米（meters）**為唯一單位。
- **軸向約定**：**+Y 朝上（+Y up）**，**地面為 Y=0（floor zero）**。
- **變換保持**：嚴格保留 `session-to-room` 與 `room-to-house` 變換矩陣，所有幾何體、相機姿態與光源統一套用相同變換，嚴禁依據「名稱猜測」對齊。
- **幾何分層優先級**：
  1. 第一級：建立基準地板、牆面平面、門窗開口、天花板高度階梯與結構柱。
  2. 第二級：根據 RoomPlan Bounding Boxes 置入基礎體塊（強調：RoomPlan 的盒子僅為佔位邊界，非最終家具成品）。
  3. 第三級：比對相機照片，雕琢家具結構、輪廓剪影（Silhouettes）、材質比例（Material Scale）與燈光配置。

### 2.2 視覺驗證閉環：Matched-Camera 與「編譯通過不等於視覺正確」
本專案最核心的工程哲學與我們的規範完全一致：**「A build passing does not establish visual accuracy.（代碼編譯通過絕不代表視覺正確）」**。

為此，技能庫提供了專用的相機對齊驗證腳本：
```bash
# 產生俯視平面圖與掃描數據的疊合對比圖
CAP_URL=http://localhost:5188 "$S/cmp.sh" plan 'room=my-room&view=top&ppm=110'

# 使用 iPhone 拍攝時記錄的相機姿態，渲染相同視角的 3D 場景並與原照片並排拼接
CAP_URL=http://localhost:5188 "$S/cmp_photo.sh" my-room 0 13 26
```
Agent 透過 `agent-browser` 截取渲染畫面，調用 Python 腳本將虛擬相機視角與實體拍攝相片拼貼成對比圖（Stitched Comparison）。Agent 必須主動檢查對比圖、找出最大的一處具體差異、修改 Three.js 代碼，然後重複驗證，直到輪廓與特徵完全吻合。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **採納與落地行動**：
  1. **空間運算 Agent 技能範本提煉**：
     - Wes Bos 的 `scan-to-threejs` 是目前 AI Agent 在 3D 與空間運算領域結構最嚴謹、驗收規範最明確的 Skill 之一。
     - 其「物理證據 $\to$ 坐標契約 $\to$ 語意化程式化建模 $\to$ 視覺相機內參比對」的四步閉環，為我們的 `SanHsien/agent-assets`（私有） 與技能體系提供了頂級範本。
  2. **空間幾何契約校驗工具**：
     - 在本 repo 中提煉輕量空間契約檢驗工具（驗證單位為米、+Y 朝上、地面為零、Bounding Box 合法性），杜絕 Agent 生成錯亂的三維代碼。
  3. **Three.js 輕量展示範本整合**：
     - 結合既有 `assets/target-story-editor/` 等 Generative UI 資產，在 `assets/` 建立單檔純靜態 Three.js 空間漫遊展示，作為後續 3D 工件渲染的標準模板。

- **不採納／邊界考量**：
  - 本 repo 不需要引入完整的 Swift / Xcode iOS App 編譯環境；我們專注於接收標準的 RoomPlan / Capture JSON 數據，並由 Agent 在網頁端完成 Three.js 程式化建模與視覺驗證閉環。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261026-11`**｜**[優先級：高]** 撰寫「空間運算 Agent 規範：物理 LiDAR 測量、Three.js 程式化建模與相機內參比對閉環」收錄於 `docs/scan-to-threejs-spatial-agent-spec.md`
  - **目標範圍**：`docs/scan-to-threejs-spatial-agent-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳解 iOS RoomPlan 與 LiDAR 數據格式（空間幾何、門窗開口、定位照片與相機內參）。
    2. 定義空間建模的坐標契約（米制單位、+Y 朝上、地面零點、變換矩陣繼承）。
    3. 規範「先結構後細節」的漸進式建模分層與 Matched-Camera 視角並排比對流程。
    4. 闡述「編譯通過不等於視覺正確」在空間與圖形程式開發中的防幻覺實踐。
  - **驗收標準（DoD）**：產出 `docs/scan-to-threejs-spatial-agent-spec.md`，內含坐標契約、工作流時序圖、相機比對腳本範例與驗收門檻；以 `Test-Path docs/scan-to-threejs-spatial-agent-spec.md` 驗證存在。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：docs/scan-to-threejs-spatial-agent-spec.md（216 行）：座標契約、工作流時序圖、相機比對腳本範例與驗收門檻。獨立驗收（fresh-context 審查員，2026-10-26）通過：cmp_camera 範例重跑輸出逐字相符。

- [x] **`T-20261026-12`**｜**[優先級：中]** 實作 `tools/verify_spatial_alignment.py` 空間幾何契約校驗工具與單元測試
  - **目標範圍**：`tools/verify_spatial_alignment.py` 與 `tests/test_verify_spatial_alignment.py`
  - **具體做法**：
    1. 以純 Python 3.11+ 實作幾何契約檢查器，解析房間模型資料（JSON / Three.js 節點定義）。
    2. 校驗基本契約：單位是否為米、最低地板坐標是否貼齊 Y=0、物體是否完全位於房間圍牆邊界內。
    3. 撰寫單元測試覆蓋正常房間幾何與穿牆、懸空、坐標倒置等異常案例。
  - **驗收標準（DoD）**：產出 `tools/verify_spatial_alignment.py` 與 `tests/test_verify_spatial_alignment.py`，通過 `python -m unittest discover -s tests -p "test_verify_spatial_alignment.py"`。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：tools/verify_spatial_alignment.py＋tests/test_verify_spatial_alignment.py：34 tests OK，反例含穿牆、懸空、Y 軸倒置、鏡像位姿，皆為幾何斷言。獨立驗收（fresh-context 審查員，2026-10-26）通過。

- [x] **`T-20261026-13`**｜**[優先級：低]** 建立 `assets/spatial-room-viewer/index.html` 輕量 Three.js 空間漫遊與娃娃屋展示範本
  - **目標範圍**：`assets/spatial-room-viewer/index.html`（獨立 HTML 靜態展示）
  - **具體做法**：
    1. 採用純前端 CDN（Three.js + OrbitControls / PointerLockControls）實作單檔式 3D 空間展示。
    2. 支援按鈕原地切換 Dollhouse（娃娃屋軌道視角）與 Walking（第一人稱走動漫遊視角）。
    3. 實作基礎牆面、地板、窗戶與簡單家具立方體之參數化網格，零外部本地後端即可在瀏覽器開啟。
  - **驗收標準（DoD）**：產出 `assets/spatial-room-viewer/index.html`，以瀏覽器 `file://` 協定開啟無 JavaScript 錯誤，可正常進行視角切換與空間導覽。
  - **完成日期**：2026-10-26
  - **實作紀錄 / 證據**：assets/spatial-room-viewer/index.html（215 行，Three.js 0.160.0 固定版本、jsdelivr importmap）：審查員以 headless Chrome 用 file:// 開啟無 console 錯誤，dollhouse→walking→dollhouse 切換成功；主 session 另以本機 http 實測兩種視角皆可切換、無 JS 錯誤。

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **視覺化與 Generative UI 相關**：
  - [靶心人故事編輯器：Generative UI 互動產品設計](./2026-10-18-target-story-generative-ui-editor.md) ｜ 關聯任務：`T-20261018-03`、`T-20261018-04`
  - [answer-me-with-html 視覺工件](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md) ｜ 關聯任務：`T-20261026-06`、`T-20261026-07`
- **多 Agent 協同與工作區架構**：
  - [Block Buzz 協同工作區](./2026-10-26-block-buzz-nostr-agent-workspace.md) ｜ 關聯任務：`T-20261026-08`
