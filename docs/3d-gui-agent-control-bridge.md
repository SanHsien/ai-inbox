# AI Agent 操控 3D 與本機 GUI 軟體之雙軌橋接方案規格

> 來源：`notes/2026-10-26-chatgpt-6-1-gpt-work-codex-skills-practitioner-guide.md`（任務 `T-20261026-30`），回應觀眾 `@payson1998` 在孔老師 AI 研習社影片留言區的提問（作者宣稱，原影片未附回覆內容，屬社群轉貼，不花時間查證留言者身分）。

---

## 1. 問題本質：為什麼大模型「無法直接操作」本機 3D GUI 軟體

大模型（含具備電腦使用能力的 Agent）本身**沒有**對任意桌面應用程式的通用操控介面。它能做的只有兩類輸入：

1. **文字 / 結構化資料**：對話、工具呼叫參數、檔案內容。
2. **視覺畫面點擊座標**（電腦使用 / Computer Use 類工具）：對螢幕截圖判斷座標後模擬滑鼠鍵盤。

3D GUI 軟體（Blender、Cinema 4D、SketchUp 等）的互動核心是：
- 即時渲染的 3D 視窗（滑鼠拖曳旋轉視角、滾輪縮放、物件選取框）；
- 大量疊層面板（Modifier、Properties、Outliner）且**版面因外掛與使用者自訂差異極大**；
- 操作語意（例如「把這個立方體 Bevel 0.02」）需要先在內部場景圖找到物件，再呼叫對應的建模運算，這一步**純視覺點擊無法可靠完成**——座標會因視窗大小、縮放層級、相機角度而整套失效。

所以觀眾提問「請他操作 3D 軟體他表示無法直接操作」的根本原因不是模型「不想做」，而是：**沒有裝任何橋接層時，Agent 只能看畫面、模擬點擊，而 3D 軟體的操作語意無法只靠像素座標穩定表達**。解法不是讓模型更聰明，而是加一層把「操作語意」轉成「程式可呼叫的動作」的橋接層——下面的方案 A、B 都是這種橋接層，差別在橋接層長在哪裡。

```text
┌─────────────────────────────────────────────────────────────────┐
│ 沒有橋接層時的唯一路徑（脆弱）                                      │
│ Agent ──螢幕截圖──▶ 判斷座標 ──模擬點擊/拖曳──▶ 3D 軟體視窗          │
│         （視窗大小/縮放/相機角度一變，座標全部失效；無場景語意）        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 方案 A：Three.js WebGL 互動 HTML 工件渲染

### 2.1 適用場景

- 需求是「讓使用者在瀏覽器裡看到、操作一個 3D 模型／場景」，**不需要**產出可在 Blender 等專業軟體中繼續編輯的檔案。
- 典型案例：產品展示、空間掃描重建檢視器（`wesbos/3d-model-anything`，見 `notes/2026-10-26-3d-model-anything-iphone-lidar-threejs.md`）、資料視覺化的 3D 呈現。
- 優點：Agent 直接**輸出程式碼**（HTML + JS），不需要操控任何外部應用程式視窗，無點擊座標問題。

### 2.2 資料交換契約

Agent 不是「操控」3D 軟體，而是**產出獨立運行的場景描述**，交給瀏覽器的 Three.js runtime 渲染：

```text
┌────────────────────┐   scene_spec.json   ┌──────────────────────────┐
│ 上游資料來源          │ ──────────────────▶ │ Agent（程式碼生成）        │
│ （LiDAR/RoomPlan 掃描 │                     │ 讀 scene_spec 寫 Three.js │
│  資料、或人工描述）    │                     │ 場景建構程式碼             │
└────────────────────┘                      └────────────┬─────────────┘
                                                          │ 產出單檔 HTML
                                                          ▼
                                             ┌──────────────────────────┐
                                             │ 瀏覽器 WebGL 渲染          │
                                             │ Three.js Scene/Camera/    │
                                             │ Renderer + OrbitControls  │
                                             └──────────────────────────┘
```

`scene_spec.json`（最小契約，供 Agent 讀取後生成對應 Three.js 物件）：

| 欄位 | 型別 | 說明 |
| :--- | :--- | :--- |
| `objects[]` | array | 每個物件：`type`（`box`／`mesh`／`imported_gltf`）、`position`[x,y,z]、`rotation`、`scale`、`material` |
| `camera` | object | 初始相機位置與視角模式（`walking`／`dollhouse`／`overhead`，命名沿用 `wesbos/3d-model-anything` 的檢視模式，作者宣稱） |
| `lights[]` | array | 光源型別與強度 |
| `source_evidence` | string | 若場景由掃描資料重建，記錄原始資料路徑，不內嵌機密 |

### 2.3 渲染管線

```text
[HTML 工件載入]
     │
     ▼
Three.js Scene 建立 ── 讀 scene_spec.objects[] 逐個 new Mesh(...)
     │
     ▼
Camera + OrbitControls（滑鼠旋轉/縮放/平移，瀏覽器原生事件，不需 Agent 介入）
     │
     ▼
Renderer.render() 迴圈（requestAnimationFrame）
     │
     ▼
使用者在瀏覽器內互動；若要「改場景」，是重新請 Agent 產出新的 scene_spec／新 HTML，
不是即時遠端控制一個正在跑的 Blender 行程
```

### 2.4 外部腳本與授權限制

建議做法（本文件的建議，不是 repo 既有規則）：外部腳本只從 cdnjs／jsdelivr／unpkg 這類公開 CDN 載入並**固定版本**，避免 CDN 上的新版默默改變行為，例如：

```html
<script src="https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js" type="module"></script>
```

用 `file://` 開啟整個場景不得有 JavaScript 錯誤（console 乾淨）；若使用 `OrbitControls` 等附加模組，一併固定版本並改用 ES module 匯入，不要用會動態拉取未鎖版本依賴的 CDN 捷徑。

---

## 3. 方案 B：Blender Python / CLI-Anything / MCP 外部指令轉發

### 3.1 適用場景

- 需求是**實際操控一個正在執行的 3D 軟體**（例如要它在 Blender 裡真的做出一個帶倒角的立方體、匯出 `.blend`、跑一次渲染），而不是在瀏覽器裡展示結果。
- 前提：Agent 的執行環境需要能連到該軟體開放的本機通道（Socket／stdio），且使用者已安裝並啟用對應的外掛／伺服端元件。

### 3.2 已查證的 MCP Server（2026-10-26 查證）

| 專案 | 角色 | 連結 | 授權 | 關鍵風險 |
| :--- | :--- | :--- | :--- | :--- |
| `ahujasid/blender-mcp`（現名 **MCP for Blender**） | Blender 端 addon（Socket Server）＋ MCP Server，讓具 MCP 能力的 Agent 透過 JSON-over-TCP 呼叫 Blender | <https://github.com/ahujasid/blender-mcp> | MIT | `execute_blender_code` 可執行任意 Python；Socket **無驗證/加密**，只能綁 localhost，可用 `BLENDER_MCP_SAFE_MODE=1` 擋高風險操作（檔案存取、執行外部程式、網路） |
| `HKUDS/CLI-Anything`（含 `cli-anything-blender` harness） | 把任意軟體（含 Blender，透過 `bpy`）包成 Agent-Native CLI；7 階段流水線分析→設計→實作→測試→文件→發布 | <https://github.com/HKUDS/CLI-Anything> | Apache-2.0 | 生成的 CLI 呼叫真實應用後端，等同該應用的操作權限；文件稱 208 項測試通過（作者宣稱，未在本機重現） |

MCP 傳輸層的官方規範（與本機連線安全直接相關）：**標準傳輸只有 stdio 與 Streamable HTTP 兩種**；本機跑的 Streamable HTTP server 規範要求「必須驗證 Origin header、本機應只綁 127.0.0.1、應實作身分驗證」，出處：[MCP 規格 Transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)（2026-10-26 查證）。這對應到 `blender-mcp` 的風險提示：Socket 沒做這些防護時，**任何能連到該 port 的程式都能跑 Python**，因此只能本機使用，不可對外開放。

### 3.3 架構實施指引

```text
┌────────────────────────┐
│ Agent（Claude Code 等） │
│ 具 MCP Client 能力       │
└───────────┬────────────┘
            │ MCP（stdio 或 Streamable HTTP，僅綁 127.0.0.1）
            ▼
┌────────────────────────────────────┐
│ MCP for Blender：MCP Server 進程      │
│ （server.py，轉發 JSON 指令）          │
└───────────┬────────────────────────┘
            │ Socket (TCP, JSON，無驗證——限本機)
            ▼
┌────────────────────────────────────┐
│ Blender 內的 addon.py               │
│ 接收指令、在 Blender Python 環境執行   │
│ （建模/材質/相機/渲染 API 呼叫）        │
└────────────────────────────────────┘
```

實施步驟（依 [blender-mcp README](https://github.com/ahujasid/blender-mcp) 的安裝方式，2026-10-26 查證；本機未安裝 Blender，未實測）：
1. `uvx mcp-for-blender install-addon`，在 Blender 偏好設定內啟用該 addon。
2. 在 Blender 的 MCP for Blender 側邊欄啟動 Socket Server（僅本機）。
3. Agent 端的 MCP client 設定（如 Claude Desktop／Claude Code 的 `mcpServers` 設定）指向 `uvx mcp-for-blender`。
4. 高風險操作前設定 `BLENDER_MCP_SAFE_MODE=1`；需要更高自由度再評估關閉，且先確認場景已存檔（官方 README 提示：「ALWAYS save your work before using it」，作者宣稱）。
5. 不需要通用程式碼執行、只需要固定幾類操作（例如「匯出截圖」「跑渲染」）時，優先改用 `CLI-Anything` 產生的 `cli-anything-blender` 固定指令集，縮小可執行動作的範圍，而不是開放 `execute_blender_code` 這種任意程式碼介面。

### 3.4 本機螢幕截圖與隱私規範的交集

方案 B 若需要**視覺確認**操作結果（例如截圖 Blender 視窗確認渲染是否正確），必須遵守本 repo [`docs/multimodal-screen-privacy-spec.md`](./multimodal-screen-privacy-spec.md)：
- 截圖前用 `python tools/screen_privacy.py --title "<視窗標題>" --app <程式名>` 判斷是否 `blocked`／`nocap`；3D 軟體視窗一般不在黑名單，但若視窗標題帶有使用者自訂的機密專案名稱仍需走正規化與清洗（該規範第 2 節）。
- 截圖後 OCR 掃描，依該規範第 5 節的機密與 PII 正則表處理；命中金鑰／身分證/卡號等一律整張丟棄（`drop_image`），不可送給視覺模型。
- 截圖保留依該規範「生命週期」章節：48 小時內清除，不作為長期證據留存於 repo。

---

## 4. 方案選擇指引

| 情境 | 建議方案 |
| :--- | :--- |
| 只要讓人在瀏覽器看/轉/縮放一個 3D 結果，不需要進專業軟體編輯 | **方案 A**（Three.js 工件） |
| 需要 Agent 實際改動一個正在跑的 Blender 場景、匯出 Blender 專屬格式、串接現有 Blender 外掛生態 | **方案 B**（MCP／CLI-Anything） |
| 不確定、或兩者都要（先用 Agent 直接建模，再把結果匯出成網頁可看的檔案） | 先走方案 B 產出場景，再把匯出的幾何資料轉成方案 A 的 `scene_spec.json` 做網頁端展示 |

---

## 5. 回應觀眾提問的結論

`@payson1998` 問「3D 的部份是要安裝外掛程式嗎？還是進工作模式跟他聊天就可以了？」的直接回答：**兩者都不是單靠聊天能完成**。
- 若目的只是「看 3D 結果」：不需要外掛，Agent 直接生成方案 A 的 Three.js HTML 工件即可，瀏覽器打開就能轉動模型。
- 若目的是「要它真的在 Blender 裡做事」：**需要**安裝橋接外掛（方案 B 的 `MCP for Blender` addon 或 `CLI-Anything` 的 Blender harness），單純對話視窗無法讓大模型取得 Blender 內部的場景圖與建模 API。

---

## 6. 未查證事項

- 「`cli-anything-blender` 208 項測試通過」為官方 README 的宣稱，本文件未在本機重跑驗證。
- Grok Build / GPT Work 等桌面端目前是否已原生整合上述任一橋接方案：未查證，截至查證日期官方文件未提及。
