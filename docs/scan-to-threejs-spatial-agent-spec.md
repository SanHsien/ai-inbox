# 空間運算 Agent 規範：LiDAR 測量、Three.js 程式化建模與相機內參比對閉環

> 來源：[`wesbos/3d-model-anything`](https://github.com/wesbos/3d-model-anything)（MIT）的 `scan-to-threejs` 技能，筆記見 [`notes/2026-10-26-3d-model-anything-iphone-lidar-threejs.md`](../notes/2026-10-26-3d-model-anything-iphone-lidar-threejs.md)。
> 查證日期：2026-10-26。本規範配套工具：[`tools/verify_spatial_alignment.py`](../tools/verify_spatial_alignment.py)（幾何契約校驗）、[`assets/spatial-room-viewer/index.html`](../assets/spatial-room-viewer/index.html)（Three.js 檢視器）。
> 本 repo 不含 Swift／Xcode；只規範「拿到掃描資料之後」，由 Agent 用 Three.js 重建並驗證。

---

## 1. 輸入資料：RoomPlan 與 ARKit 提供什麼

| 資料 | 內容 | 出處 |
|------|------|------|
| `CapturedRoom` | `walls`、`doors`、`windows`、`openings`、`floors`（皆 `Surface`，2D 面）與 `objects`（`Object`，3D 範圍）；可 `export(to:exportOptions:)` 成 USDZ；可 Codable 序列化（所以才有 RoomPlan JSON） | [Apple：CapturedRoom](https://developer.apple.com/documentation/roomplan/capturedroom)（2026-10-26 以 Apple 文件 JSON 端點查證） |
| 每個元素 | `transform`（4x4）、`dimensions`（[寬, 高, 深]；牆、門、窗深度為 0）、類別、信心值 | 欄位細節見 wesbos 的 [`house-capture.md`](https://github.com/wesbos/3d-model-anything/blob/main/.agents/skills/scan-to-threejs/references/house-capture.md)；Apple 該頁**未**載明座標系與單位 |
| 定位照片 | 每張照片的相機位姿（4x4）、內參、影像尺寸；原始感測器像素 JPEG（橫向，未旋轉） | 同上（作者的匯出格式，非 Apple 規格；JSON 鍵名原文未列，需先 `jq 'keys'` 確認） |
| `ARCamera.intrinsics` | `simd_float3x3`，pinhole 模型；`fx`、`fy` 為像素焦距，`ox`、`oy` 為主點相對影像**左上角**的偏移；單位全是像素 | [Apple：ARCamera.intrinsics](https://developer.apple.com/documentation/arkit/arcamera/intrinsics) |
| `ARCamera.transform` | 相機在世界座標的位置與朝向（`simd_float4x4`） | [Apple：ARCamera](https://developer.apple.com/documentation/arkit/arcamera) |
| LiDAR 網格／深度 | `mesh/*.ply`、深度 Float16（公尺）、信心值 0~2 | 同 `house-capture.md`（作者宣稱格式） |

RoomPlan 的盒子是**邊界佔位**，不是家具成品（`SKILL.md` 原文意旨：boxes are bounds, not finished furniture）。

## 2. 坐標契約（Agent 一律照此，否則視為錯誤）

| 項目 | 契約 | 依據 |
|------|------|------|
| 長度單位 | 公尺 | `SKILL.md`：meters；`house-capture.md`：session 座標為公尺。Apple 的 RoomPlan／ARKit 座標頁**未明載**公尺，單位以作者格式文件為準（Apple 側未查證） |
| 上方向 | +Y | ARKit `.gravity` 對齊：Y 軸平行重力，(0,-1,0) 朝下（[Apple：gravity](https://developer.apple.com/documentation/arkit/arconfiguration/worldalignment-swift.enum/gravity)） |
| 手性 | 右手系 | ARKit 世界與相機座標為右手系（[Apple：Understanding World Tracking](https://developer.apple.com/documentation/arkit/understanding-world-tracking)）；Three.js 同為右手系、+Y 向上（Three.js 文件頁未逐字查到此句，以本規範工具的投影測試與檢視器實測為準） |
| 地面 | 地板頂面 = Y=0 | `SKILL.md`：floor zero |
| 變換 | 保留 `session-to-room`、`room-to-house`；幾何、照片位姿、光源、參考層套用**同一組**變換；不得靠房間名稱猜對齊 | `SKILL.md`；`house.json` 鏈：`sessionToHouse = zone.toHouse × session.alignment.toZone` |
| 矩陣記憶體順序 | column-major，平移在最後一欄（16 值 index 12~14） | `house-capture.md`；Three.js `Matrix4.elements` 亦為 column-major（[Matrix4 文件](https://threejs.org/docs/pages/Matrix4.html)） |
| 相機軸向 | 看向 **-Z**、+Y 向上、+X 向右 | ARKit：gravity 頁寫明 z 軸基向量 (0,0,-1) 為裝置相機面向；Three.js `Camera`：看向本地負 z 軸（[Camera 文件](https://threejs.org/docs/pages/Camera.html)）。所以 ARKit 相機位姿**不需轉軸**即可用於 Three.js 相機 |
| 像素座標 | 原點左上、u 向右、v **向下** | Apple intrinsics 頁：主點為相對左上角的偏移 |
| 垂直 FOV | `fov = 2·atan(H / (2·fy))`（度），主點置中時成立 | Three.js `PerspectiveCamera.fov` 為垂直視角（[PerspectiveCamera 文件](https://threejs.org/docs/pages/PerspectiveCamera.html)）；主點不在中心時用 `setViewOffset` |
| 影像方向 | 內參對應**未旋轉**的橫向感測器像素；顯示時才順時針轉 90°（EXIF 6） | `house-capture.md`（作者宣稱） |

投影公式（工具 `project_point` 的實作，ARKit／Three.js 約定）：

```text
相機座標 (Xc, Yc, Zc) = world_to_camera × 世界點        # world_to_camera = camera_to_world 的反矩陣
深度 d = -Zc                                           # d <= 0 代表在相機後方，不可見
u = cx + fx · Xc / d
v = cy - fy · Yc / d                                   # 世界往上 → Yc 增加 → v 減少（像素向下為正）
```

OpenCV 約定（看向 +Z、+Y 向下）則是 `d = Zc`、`v = cy + fy·Yc/d`。兩種約定搞混是「照片與模型上下顛倒」的常見原因，工具會自動試另一種約定並提示。

### 2.1 USDZ／Z-up 資料轉入 Three.js

- Z-up、右手系（多數 CAD）→ Y-up：`(x, y, z) → (x, z, -y)`（工具 `z_up_to_y_up`，測試 `test_z_up_to_y_up_keeps_right_handed` 驗證手性不變）。**不可**只交換 y、z，那會變成鏡像（左手系）。
- USD 檔以 `upAxis` 與 `metersPerUnit` 中繼資料宣告軸向與單位；RoomPlan 匯出的 USDZ 這兩個值**未查證**。載入前先量外框，確認房間高度落在 2~4.5 m 再使用。

## 3. 工作流時序圖

```text
 掃描資料        人/Agent                 Agent（Three.js）                  驗證
    │              │                          │                              │
    │ RoomPlan JSON│                          │                              │
    │ 照片+位姿+內參│                          │                              │
    ├─────────────▶│  ① 先量測：地板、牆面、    │                              │
    │              │    開口、天花板、物體尺寸   │                              │
    │              ├─────────────────────────▶│  ② 寫 room 模組（結構層）      │
    │              │                          │    單位 m、+Y 上、地板 Y=0     │
    │              │                          ├─────────────────────────────▶│ ③ verify_spatial_alignment.py
    │              │                          │◀─────────────────────────────┤    契約違反 → 回 ②
    │              │                          │  ④ 加物體體塊（RoomPlan 盒）   │
    │              │                          ├─────────────────────────────▶│ ③ 再驗
    │              │                          │  ⑤ Matched-Camera：用照片位姿 │
    │              │                          │    與內參渲染同視角、並排拼圖   │
    │              │                          │  ⑥ 人眼/視覺模型找「最大一處」差異│
    │              │                          │  ⑦ 修最大差異 → 回 ⑤，直到門檻   │
    │              │◀─────────────────────────┤  ⑧ 標註每個細節：測得/建模/估計  │
```

## 4. 先結構後細節：分層建模

| 層 | 內容 | 這層完成的條件 |
|----|------|----------------|
| L1 結構 | 地板、牆面、門窗開口、天花板（含高低差）、結構柱 | `verify_spatial_alignment.py` 通過；量測尺寸誤差在容許內 |
| L2 體塊 | RoomPlan `objects` 的盒子（位置、旋轉、尺寸） | 無穿牆、無懸空（家具 `support` 明確） |
| L3 細節 | 家具輪廓、材質比例、燈光 | 至少 3 張 matched-camera 比對圖，每張最大差異在門檻內 |

規則：L1 未過不做 L2；看不清楚的尺寸記為「不確定」而不是捏造數字；空白的掃描區域是證據，不要裁掉（`SKILL.md`）；個人掃描資料與比對圖不進 Git。

## 5. 相機比對腳本範例（可執行）

作用：用照片的位姿與內參，把模型地標投影到照片像素座標，與照片上標出的對應點比較，找出最大差異。腳本**只算數字，不判斷「像不像」**，判斷由人或視覺模型做（與作者的 `cmp_photo.sh` 同樣的分工：只擷取與拼接，不評分）。

存成 `cmp_camera.py`，在 repo 根目錄執行 `python cmp_camera.py`（只用標準庫）。示範資料裡 `door_head` 故意偏 40 px，模擬「模型門高錯了」：

```python
"""Matched-camera 比對：把模型地標用「照片的相機姿態與內參」投影，和照片上標出的像素比。
用法（repo 根目錄）：python cmp_camera.py
"""
import math
import sys

sys.path.insert(0, "tools")
import verify_spatial_alignment as v

sys.stdout.reconfigure(encoding="utf-8")  # Windows 管線預設 cp950，先改 UTF-8

# 1. 照片 metadata（實務上來自 photos.json：transform 16 值 column-major、intrinsics、sensor 像素尺寸）
K = {"fx": 1500.0, "fy": 1500.0, "cx": 960.0, "cy": 720.0, "width": 1920, "height": 1440}
# 相機在 (2.5, 1.5, 6.0)，朝 (2.5, 1.2, 2.0)；以下 16 值由 look-at 產生，等同 ARKit 的 camera.transform
eye, target = (2.5, 1.5, 6.0), (2.5, 1.2, 2.0)
z = [eye[i] - target[i] for i in range(3)]; n = math.sqrt(sum(a * a for a in z)); z = [a / n for a in z]
x = [z[2], 0.0, -z[0]]; n = math.sqrt(sum(a * a for a in x)); x = [a / n for a in x]
y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
c2w = x + [0.0] + y + [0.0] + z + [0.0] + list(eye) + [1.0]
M = v.mat_from_column_major(c2w)

# 2. 模型地標（世界座標，公尺）與人/視覺模型在「照片」上標出的像素
landmarks = {
    "wall_corner_A (0,0,0)": ((0, 0, 0), None),
    "wall_corner_B (5,0,0)": ((5, 0, 0), None),
    "ceiling_corner (5,2.6,0)": ((5, 2.6, 0), None),
    "door_head (2.5,2.0,0)": ((2.5, 2.0, 0), None),
}
# 示範用「照片標註」：以正確投影加上固定偏差，最後一個故意偏 40px 模擬模型門高錯誤
bias = [(1.5, -1.0), (-2.0, 1.5), (0.5, 2.0), (0.0, 40.0)]
obs = {}
for (name, (w, _)), (du, dv) in zip(landmarks.items(), bias):
    u, vv, _ = v.project_point(w, M, K, "arkit")
    obs[name] = (u + du, vv + dv)

# 3. 逐點誤差表
print(f"Three.js 相機參數：fov(垂直)={v.vertical_fov_deg(K['fy'], K['height']):.2f}° "
      f"aspect={K['width'] / K['height']:.4f} position={eye} lookAt={target}")
print(f"{'landmark':<26}{'projected(u,v)':<20}{'photo(u,v)':<20}{'err_px':>8}")
worst = (None, -1)
for name, (w, _) in landmarks.items():
    u, vv, d = v.project_point(w, M, K, "arkit")
    ou, ov = obs[name]
    e = math.hypot(u - ou, vv - ov)
    print(f"{name:<26}({u:7.1f},{vv:7.1f})   ({ou:7.1f},{ov:7.1f})   {e:8.2f}")
    if e > worst[1]:
        worst = (name, e)
print(f"最大差異：{worst[0]}，{worst[1]:.1f}px（門檻 8px） -> {'PASS' if worst[1] <= 8 else '先修這一處再重跑'}")
```

實際執行輸出（2026-10-26，Python 3.14.9，Windows 11）：

```text
Three.js 相機參數：fov(垂直)=51.28° aspect=1.3333 position=(2.5, 1.5, 6.0) lookAt=(2.5, 1.2, 2.0)
landmark                  projected(u,v)      photo(u,v)            err_px
wall_corner_A (0,0,0)     (  344.8,  977.7)   (  346.3,  976.7)       1.80
wall_corner_B (5,0,0)     ( 1575.2,  977.7)   ( 1573.2,  979.2)       2.50
ceiling_corner (5,2.6,0)  ( 1595.5,  327.1)   ( 1596.0,  329.1)       2.06
door_head (2.5,2.0,0)     (  960.0,  481.0)   (  960.0,  521.0)      40.00
最大差異：door_head (2.5,2.0,0)，40.0px（門檻 8px） -> 先修這一處再重跑
```

把輸出的 `fov`、`aspect`、`position`、`lookAt` 填進 Three.js `PerspectiveCamera` 就能渲染同視角畫面；渲染結果與照片並排後再用肉眼確認。

## 6. 驗證工具與驗收門檻

`tools/verify_spatial_alignment.py <scene.json> [--json]`：退出碼 0 通過、1 有違反、2 輸入無法解析。檢查項目都是幾何計算：

| 代碼 | 判定方式 |
|------|----------|
| `UNITS_NOT_METERS`／`UP_AXIS_NOT_PLUS_Y`／`NOT_RIGHT_HANDED` | 宣告的單位、上軸、手性 ≠ 契約 |
| `UNITS_SCALE_SUSPECT` | 房間高度不在 2.0~4.5 m；並試 ÷100、÷1000、÷39.37、÷3.28 看哪個單位能讓高度合理，給出提示 |
| `FLOOR_NOT_ZERO`／`Y_INVERTED` | `floor_y` 偏離 0 超過 2 cm；天花板低於地板；或全部物體都在地板下 |
| `OBJECT_OUTSIDE_ROOM` | 物體（含繞 Y 旋轉）4 個底角以射線法判斷是否在 XZ 圍牆多邊形內，貼牆（≤2 cm）算在內，支援 L 形等凹多邊形 |
| `OBJECT_FLOATING`／`OBJECT_NOT_ON_SUPPORT`／`OBJECT_BELOW_FLOOR`／`OBJECT_ABOVE_CEILING` | 底面與地板或支撐物頂面的垂直間距 |
| `MEASUREMENT_MISMATCH` | 量測值與模型值差 > 容許；比值接近 100／1000／25.4 時提示單位錯 |
| `REPROJECTION_ERROR`／`BAD_CAMERA_POSE`／`PRINCIPAL_POINT_OUTSIDE_IMAGE` | 位姿反矩陣後投影地標，RMS 像素誤差 > 門檻；位姿含縮放或鏡像（行列式為負）；主點落在影像外。誤差過大時自動試另一種相機約定與反向位姿，提示是軸向約定還是矩陣方向搞反 |

單檔實跑（2026-10-26；`good.json` 為合成的正常房間，`bad.json` 為同一房間加入沙發穿牆、桌子懸空、模型寬度差 100 倍、相機約定宣告錯誤）：

```text
$ python tools/verify_spatial_alignment.py good.json
[PASS] 空間契約通過                                          （退出碼 0）

$ python tools/verify_spatial_alignment.py bad.json
[ERROR] OBJECT_OUTSIDE_ROOM: sofa: 2/4 個角落在房間圍牆外（例 x=5.600, z=0.550）
[ERROR] OBJECT_FLOATING: tilted: support=floor 但底面離地 0.700 m（懸空）
[ERROR] MEASUREMENT_MISMATCH: width: 量測 5.020 m vs 模型 500.000 m，差 494.980 m > 容許 0.05 m；模型/量測比 99.6 ≈ 100 倍（公分↔公尺），疑似單位錯
[ERROR] REPROJECTION_ERROR: 有地標落在相機後方；改用 arkit 約定可擬合（RMS 1.80px）：相機軸向約定宣告錯誤
[FAIL] 4 項違反                                              （退出碼 1）
```

scene JSON 欄位見工具檔案開頭說明。單元測試 `tests/test_verify_spatial_alignment.py` 含穿牆、懸空、Y 倒置、單位錯、相機約定搞反、位姿取反、鏡像位姿等反例。

驗收門檻（預設值，可依專案改）：

| 項目 | 門檻 |
|------|------|
| 貼地／貼牆位置誤差 | ≤ 2 cm |
| 結構量測（牆長、房高、開口） | 與量測差 ≤ 5 cm（每項可在 `tolerance_m` 覆寫） |
| 地標重投影 RMS | ≤ 8 px（1920×1440 影像；`max_reproj_px` 可調） |
| matched-camera 比對 | 至少 3 張，每張最大差異已修到門檻內，且附圖 |
| 細節標註 | 每個細節標「測得／建模／估計」 |

## 7. 「編譯通過 ≠ 視覺正確」的防幻覺實踐

`SKILL.md` 明列：build 通過不能證明外觀正確。空間與圖形程式的錯誤多半是「語法合法、畫面錯」，所以：

1. 功能與外觀**分開驗**：build／型別檢查／瀏覽器 console 無錯是一關；matched-camera 比對圖是另一關，兩關都要過。
2. 契約先於美術：單位、軸向、地面零點用工具算，不靠肉眼。上下顛倒、左右鏡像、單位差 100 倍這類錯，工具比眼睛先抓到。
3. 比對腳本不評分：只出數字與並排圖；Agent 必須指出「最大的一處差異」，修完再比，不可宣稱「大致吻合」。
4. 不為了通過而裁圖或調門檻：不依非黑像素裁切；優化前後要拿完整品質圖比較。
5. 不確定就標不確定：沒有測到的尺寸寫「估計」，不編造；不依房間名稱猜變換。

## 8. 查證狀態

| 項目 | 狀態 |
|------|------|
| `SKILL.md`、`house-capture.md` 的契約與格式 | 已讀原文（2026-10-26）；格式為作者定義，**作者宣稱**；JSON 鍵名原文未列，使用前先確認 |
| Apple 的 `CapturedRoom` 結構、`intrinsics` 定義、`gravity` 座標說明、世界追蹤右手系 | 已查 Apple 文件 |
| Apple 側單位為公尺、RoomPlan `transform` 座標系 | 未查證（Apple 頁面未載明） |
| Three.js 看向 -Z、垂直 FOV、Matrix4 column-major | 已查 Three.js 文件頁與原始碼註解 |
| Three.js 右手系／+Y 上的官方明文 | 未逐字查到，以本 repo 測試與檢視器實測支持 |
| RoomPlan 匯出 USDZ 的 `upAxis`／`metersPerUnit` | 未查證，需對實際檔案檢查 |
| 真實 iPhone 掃描資料上的端到端比對 | 未實測（沒有掃描資料）；範例使用合成資料，只證明公式與工具行為 |
