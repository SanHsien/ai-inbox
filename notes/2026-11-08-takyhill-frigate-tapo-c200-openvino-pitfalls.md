---
id: 2026-11-08-takyhill-frigate-tapo-c200-openvino-pitfalls
title: "Frigate 0.18.2 實測圖解與踩雷拆解：以測試影片驗證的 OpenVINO 模型張量契約、Tapo C200 接法（雙串流未實測）與 GHSA Root RCE 漏洞防護"
source_url: "https://www.threads.com/share/BAX-zHTFS8"
source_platform: "Threads (@takyhill) / 方格子 Vocus / GitHub (blakeblackshear/frigate)"
author: "許哲維 (@takyhill)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: archived
cluster: "3"
cluster_role: "螢幕感知與瀏覽器代理"
short_title: "Frigate實測踩雷與RCE漏洞防護"
source_review: partial
source_reviewed_at: 2026-11-17
source_review_note: "Threads 留言讀到 11 則／共 12 則；方格子留言讀到 4 則／頁面標示 6 則，其餘要登入或展開不了。"
source_images: 12
source_replies: 15
tags:
  - frigate
  - tapo-c200
  - rtsp
  - openvino
  - go2rtc
  - docker-shm
  - ghsa-rce
  - edge-ai
---

# Frigate 0.18.2 實測圖解與踩雷拆解：以測試影片驗證的 OpenVINO 模型張量契約、Tapo C200 接法（雙串流未實測）與 GHSA Root RCE 漏洞防護

- **來源連結**：[Threads 原文分享](https://www.threads.com/share/BAX-zHTFS8) ｜ [貼文永久網址 (@takyhill)](https://www.threads.com/@takyhill/post/DfSGTk8mmQe) ｜ [方格子完整圖解教學](https://vocus.cc/article/6ae9f056fd8978000135818e) ｜ [GitHub (blakeblackshear/frigate v0.18.2)](https://github.com/blakeblackshear/frigate/releases/tag/v0.18.2)
- **核心作者**：許哲維（`@takyhill`）
- **分析主題**：解構許哲維以「8 核純 CPU 舊電腦 + Docker `frigate:0.18.2` + 本機轉播的街景測試影片」完成之實測設定檔與踩雷清單，以及文中建議搭配的 NT\$699 TP-Link Tapo C200 插電攝影機接法（Tapo 本身未見實機畫面，見第 0 節）（OpenVINO `model` 區塊漏寫致 `buffer is too small` 崩潰、持續移動街景無法完成背景校準致零偵測、`/dev/shm` 512MB 共享記憶體配置、攝影機硬體相容邊界），並深挖 `v0.18.2` 修補之兩項 Critical 等級 Root RCE 資安漏洞（`GHSA-93xj-hg88-ffg7`、`GHSA-qjjw-3v66-279f`）。
- **當前狀態**：`⚪ 已封存 (Archived)`
- **相關交叉參照**：
  - [`notes/2026-11-08-frigate-nvr-rtsp-openvino-local-ai-camera.md`](./2026-11-08-frigate-nvr-rtsp-openvino-local-ai-camera.md)（`@roboa.ai` Frigate 三層能力架構、硬體門檻與 ClearCam 對照）
  - [`notes/2026-10-31-clearcam-open-source-ai-nvr-yolov9-qwen3-vl.md`](./2026-10-31-clearcam-open-source-ai-nvr-yolov9-qwen3-vl.md)（ClearCam 開源智慧 NVR 與 Qwen3 VL 事件摘要）
  - [`docs/agent-driven-onboarding-and-security-spec.md`](../docs/agent-driven-onboarding-and-security-spec.md)（Agent 引導非技術用戶部署開源專案之安全護欄）

---

## 0. 原始資料盤點

> 2026-11-16 以未登入的內建瀏覽器重看：Threads 貼文文字與 2 張附圖（在媒體檢視器放大看過）、Threads 留言 11 則（含作者 5 則；貼文標示 12 則回覆）；方格子文章的 10 張圖（逐張放大）、文末留言 4 則（含作者 2 則；頁面標示 6 則）與文內關於「實測／未實測」的說明。

- **作者圖片**（Threads 2 張＋方格子 10 張，其中 2 張重複出現在兩處）：
  - Threads 圖 1／方格子圖 1：Frigate 偵錯畫面，一條行人徒步街上滿是 `person` 偵測框與信心度，下半部有一個橘色框是自訂區域。
  - Threads 圖 2／方格子圖 6：Review 頁，顯示 Alerts 1、Detections 0，左下角 CPU 27%、系統狀態正常。
  - 方格子圖 2：網頁內建的設定編輯器，可讀到完整設定。**攝影機名稱是 `street`，輸入路徑是本機位址上的一路 RTSP 轉播（`rtsp://127.0.0.1:18554/street`），同一路同時擔任 `detect` 與 `record`**；偵測解析度 640x360、5 fps；另有 `lightning_threshold: 0.95`、追蹤 person／car／bicycle／dog、一個只看 person 的 `sidewalk` 區域。
  - 方格子圖 3：登入頁。圖 4、5：即時畫面（街景，無偵測框）。圖 7：事件回放時間軸。圖 8：Explore 頁，Person 類別 80 個追蹤物件。圖 9：Masks / Zones 設定頁，`sidewalk` 區域蓋住畫面下半。圖 10：System 頁，版本 `0.18.2-cfa08c5`，偵測器推論 2.56 ms、偵測器 CPU 81.8%、記憶體 1.7%。
  - **12 張圖沒有任何一張是 Tapo 攝影機的畫面**，全部是同一段街景測試影片。
- **作者留言補充**：
  - Threads 第一則回覆說明圖中測試影片出自 Wikimedia Commons 的格拉斯哥街景（CC BY-SA 3.0）；第二則貼方格子完整教學連結。
  - 回覆網友：測試用的是一般舊電腦，換低功耗小主機更省電但辨識需要一定效能；用 VPS 是另一條路，但本文重點是舊電腦再利用與影像不外傳；**目前沒有錄安裝影片**，是用截圖加設定檔帶步驟。
  - 方格子文內自己標明：設定檔與截圖都是實際跑過的，沒測過的會標「未實測」。標了未實測的有三處：**實測時 `detect` 與 `record` 接同一路串流，把 `stream1` 另設為錄影角色的雙串流寫法是依官方文件、未實測**；`required_zones`「只有人走進門口才通知」未實測；整個「進階」段（小米經 go2rtc 轉接、Intel 內顯加速等）未實測。文首另聲明含購物分潤連結。
- **網友留言重點**：
  - Threads：`zeonmodo` 建議裝在樹莓派比較省電；`silent.harbour.888` 說不如租便宜 VPS；`ice520_520` 問有沒有真實安裝與設定影片（作者答沒有）；`dada3c.tw` 的留言是推廣另一種在相機晶片上辨識的感測器，與本文無關。
  - 方格子：匠選科技說先講清楚不要開 5000 埠那段很有幫助；Loco Bryant 肯定用低畫質串流跑偵測與 zones 降誤報的寫法。沒有人回報照做後的實機結果。
- **對分析的影響**：
  1. **「Tapo C200 實測」要降級**：原筆記標題、分析主題與 5W1H 都寫成「以 Tapo C200 完成實測」。依設定檔截圖與作者留言，實測的輸入是一段本機轉播的街景測試影片；Tapo C200 是文章建議購買的機型，文中沒有任何 Tapo 實機畫面或連線證據。已改標題、分析主題、1 節的 What 與 How 兩列。
  2. **「雙串流策略」是未實測的建議**：原筆記把 `stream1` 錄影、`stream2` 偵測寫成實測策略。作者明講實測時兩個角色接同一路，雙串流寫法未實測。已改 How 那一列。
  3. **效能數字的適用範圍**：2.5～4 ms 與 80～118% 是在 640x360、5 fps、單一路測試影片、8 核純 CPU 下量到的（System 頁截圖為 2.56 ms、81.8%），不代表接上真實攝影機高畫質主串流後的負載。已在 What 列與 2.3 節表格下加註。
  4. 2.3 節最後一列建議「掛載 `/dev/dri` 改用內顯」屬於作者標明未實測的進階段，已加註。
  5. 2.2 節的設定檔與踩雷項目（漏寫 `model` 區塊、`shm_size`、不開 5000 埠）與截圖一致，不變；第 3 節的漏洞查核不受影響。
  6. 維持歸檔、不開任務。

---

## 1. 核心內容摘要：5W1H 初篩與實測架構（Executive Summary）

| 維度 | 核心內容 |
| :--- | :--- |
| **Who（主體）** | 科技作者許哲維（`@takyhill`），針對開源 NVR **Frigate `v0.18.2`** 進行安裝、設定檔驗證與踩坑紀錄（輸入來源為測試影片，非實體攝影機）。 |
| **What（核心實測）** | 在無獨顯之 8 核 CPU 舊電腦（Linux + Docker）上，以一路 640x360、5 fps 的街景測試影片（本機 RTSP 轉播）實測 OpenVINO CPU 推論（單次推論 2.5～4 ms，偵測器 CPU 使用率 80～118%）。文章建議的攝影機是約 NT\$699 的 **TP-Link Tapo C200（插電款）**，但截圖與設定檔都沒有 Tapo 實機畫面；上述數字不代表接上實體攝影機後的負載。 |
| **Why（補足痛點）** | 社群雖有許多 Frigate 概念介紹（如 `@roboa.ai` 短片），但新手照裝時常死在：**買錯不支援 RTSP 的電池款／小米攝影機**、**漏寫 OpenVINO `model` 張量規格導致程序崩潰**、**Docker `shm_size` 不足報 `Bus error`**，或**誤開無鑑權 `5000` 埠與舊版 RCE 漏洞**。 |
| **Where（部署環境）** | Debian / Ubuntu Linux + Docker（映像檔 `ghcr.io/blakeblackshear/frigate:0.18.2`），管理介面透過 `https://<IP>:8971`（自簽憑證 + `admin` 隨機初始密碼）存取。 |
| **When（關鍵邊界）** | 選購平價網路攝影機或撰寫 Frigate `docker-compose.yml` 與 `config/config.yml` 時。 |
| **How（串流配置）** | 作者實測時 `detect` 與 `record` 接的是同一路串流。「高畫質主串流（`stream1`）錄影、低畫質子串流（`stream2`，`640x360`、`5 fps`）偵測」的雙串流寫法是作者依官方文件給的建議，**文中標明未實測**。 |

---

## 2. 深入技術拆解：攝影機硬體邊界、OpenVINO 設定契約與 8 大實測踩雷

### 2.1 「有一款很紅的攝影機其實接不上」：RTSP 硬體相容性矩陣

貼文標題點出的硬體陷阱，實務上分為兩類常見誤買情境：

> 下列硬體相容矩陣為作者自述，未查證。

| 攝影機類型 / 代表型號 | 原生 RTSP 支援 | 原因與技術解法 |
| :--- | :---: | :--- |
| **TP-Link Tapo 插電款**（如 **Tapo C200**、C210、C220、C310） | ✅ 原生支援 | 於 Tapo App「進階設定 → 攝影機帳戶」建立獨立帳密（勿與雲端主帳號相同），即可透過 `rtsp://帳號:密碼@IP:554/stream1`（高畫質）與 `/stream2`（低畫質）拉流。 |
| **TP-Link Tapo 電池款**（如 **Tapo C410 / C420 / C425 / D230**） | ❌ 不支援 | 電池供電款為維持長續航，平時處於深睡眠狀態，無法維持 24 小時常駐 RTSP 推流，**無法直接接入 Frigate**。 |
| **小米／米家智慧攝影機**（台灣極普及之平價鏡頭） | ❌ 無原生 RTSP | 官方韌體封閉 RTSP 輸出；若要接入 Frigate，必須透過內建或外掛之 **`go2rtc`**（見 GitHub Discussion `#21421`）以小米私有協定轉接為 RTSP 流。 |

### 2.2 實測通過之 `docker-compose.yml` 與 `config/config.yml` 關鍵契約

1. **Docker 容器共享記憶體與連接埠隔離（`docker-compose.yml`）**：
   - `shm_size: "512mb"`：Docker 預設 `/dev/shm` 僅 64MB，FFmpeg 解碼高畫質視訊幀寫入共享記憶體時會直接觸發 `Bus error`，實測必須拉高至 `512mb`（多鏡頭需更高）。
   - `tmpfs: /tmp/cache`（約 1GB）：供錄影切片暫存於 RAM，避免頻繁寫入磨損 SSD。
   - **連接埠安全邊界**：僅映射 `8971:8971`（具登入鑑權與 TLS）與 `8554:8554`（RTSP restream）；**嚴禁對外暴露 `5000` 埠**（內部無鑑權 API 埠）。
2. **OpenVINO CPU 偵測器張量契約（`config/config.yml`）**：
   ```yaml
   mqtt:
     enabled: false
   detectors:
     ov:
       type: openvino
       device: CPU
   model:
     width: 300
     height: 300
     input_tensor: nhwc
     input_pixel_format: bgr
     path: /openvino-model/ssdlite_mobilenet_v2.xml
     labelmap_path: /openvino-model/coco_91cl_bkgr.txt
   ```
   - **實測必死陷阱**：當 `detectors` 指定 `type: openvino` 時，容器內建的 `/openvino-model/ssdlite_mobilenet_v2.xml` 要求輸入張量為 `300x300`、`nhwc`、`bgr`；若漏寫 `model:` 區塊，Frigate 會套用預設的 `320x320` 張量尺寸，導致攝影機推論程序直接報 `buffer is too small` 崩潰重啟。

### 2.3 實測踩雷與原理剖析（Background Calibration 死鎖）

| 踩雷現象 | 底層機制原因 | 排錯與規避方式 |
| :--- | :--- | :--- |
| **漏寫 `model` 區塊導致攝影機程序當掉** | OpenVINO 內建 `ssdlite_mobilenet_v2.xml` 輸入維度固定為 `300x300`，與預設值不合觸發 `buffer is too small`。 | 顯式宣告 `model` 的 `width: 300`、`height: 300`、`input_tensor: nhwc`、`input_pixel_format: bgr`。 |
| **餵入人潮不斷的街景測試片時，偵測數永遠為 `0`** | Frigate 的移動偵測（Motion Detection）啟動時需等待畫面出現**幾乎無動靜的靜態幀**以完成初始背景模型校準（Calibration）；若測試影片從頭到尾人車川流不息，永遠無法完成校準，因此不會觸發下游 AI 物件偵測。 | 測試時確保畫面有短暫靜止片段供背景收斂；一般家門口場景自然具備靜止時段。 |
| **8 核純 CPU 推論僅 2.5～4 ms，但 CPU 使用率達 80～118%** | SSDLite MobileNet v2 單次推論雖快，但加上 FFmpeg `stream2`（640x360 @ 5fps）軟體解碼、移動偵測與軌跡追蹤，仍會吃滿約 1 顆邏輯核心。 | 若有 Intel 6 代以上內顯，掛載 `/dev/dri` 並將 `device: CPU` 改為 `device: GPU`（OpenVINO iGPU 加速），並用 VLC 先行驗證 `stream2` 連通性。 |

> 適用範圍（2026-11-16 補）：上表的推論時間與 CPU 使用率是單一路 640x360、5 fps 測試影片下的數字。最後一列改用內顯加速的做法，屬於作者文中標明「未實測」的進階段。

---

## 3. CQR 論證檢驗與 `v0.18.2` Critical RCE 資安漏洞深挖

作者於踩雷清單第 5 點特別警告：「**請用 0.18.2 以上：之前版本有可遠端執行指令的安全漏洞。**」經直接查核 GitHub `blakeblackshear/frigate` Security Advisories，確認 `v0.18.2`（2026-10-15 發布）修補多項漏洞，下表列出其中 3 項（其中 2 項為 **Critical 等級 Root RCE**）：

| 漏洞編號 | 嚴重度 | 影響版本 | 攻擊向量與成因（Root Cause） | 防護與修補結論 |
| :--- | :---: | :---: | :--- | :--- |
| **`GHSA-93xj-hg88-ffg7`** | **Critical** | `< 0.18.2` | **Direct WebSocket Paths Root RCE**：低權限的 `viewer` 角色（或直接存取無鑑權 `5000` 埠的攻擊者；「無鑑權 5000 埠」未查證）可透過直連內部 WebSocket 路徑繞過權限控管，以容器內 `root` 身分執行任意系統指令。 | 必須升級至 **`v0.18.2+`**（PR `#24658`），且嚴禁將內部 `5000` 埠暴露於區網或公網。 |
| **`GHSA-qjjw-3v66-279f`** | **Critical** | `< 0.18.2` | **`go2rtc` Source Scheme 繞過 `exec:` 過濾器致 Root RCE（需 admin 認證；官方標題為 admin-authenticated RCE as root）**：Frigate 雖過濾了 `go2rtc` 設定中的 `exec:` 指令前綴，但攻擊者可利用複合 source scheme 繞過檢查，進而在 `go2rtc` 子程序中以 `root` 執行任意命令。 | 必須升級至 **`v0.18.2+`**，並以強密碼保護 `:8971` 管理員帳戶。 |
| **`GHSA-3cxh-fj2f-h497`**<br>（接續 `GHSA-935r-r3xx-6gmw`） | **Medium** | `< 0.18.2` | **Nginx `/auth` 路徑正規化差異繞過**：`/auth` 媒體與串流鑑權檢查的是原始請求路徑（raw request path），而非 Nginx 正規化後實際派發的路徑，導致可構造特殊路徑繞過媒體授權。 | 必須升級至 **`v0.18.2+`**（PR `#24662` 正規化媒體鑑權請求路徑）。 |

---

## 4. 評估結論與不新增待辦理由

- **評估結論**：本篇為許哲維針對 Frigate `v0.18.2` 的設定與排錯手冊（以測試影片驗證，Tapo C200 為建議機型、雙串流未實測），補齊了前篇 [`2026-11-08-frigate-nvr-rtsp-openvino-local-ai-camera.md`](./2026-11-08-frigate-nvr-rtsp-openvino-local-ai-camera.md) 未展開的 `docker-compose.yml` / `config.yml` OpenVINO 張量契約、攝影機電池款／小米相容性陷阱，以及 `v0.18.2` 修補的 `GHSA-93xj-hg88-ffg7` / `GHSA-qjjw-3v66-279f` Root RCE 漏洞細節。
- **不拆解新任務理由**：本 repo 定位為 AI Agent 情報與工具總管，不涉及實體家庭攝影機安裝，且 Threads 媒體萃取工具已於前篇 `T-20261108-01` 實作完畢；依 `AGENTS.md` 規範將本篇作為實戰參考知識歸檔（`status: archived`）。
