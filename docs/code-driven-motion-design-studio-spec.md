# 代碼驅動 Motion Design 工作室規範

此文件定義本 repo 的工程契約，供製作可任意 seek 的動效、檢查分鏡與交付影片。
數值門檻、Anti-Slop 與 8 分規則是本 repo 的取捨，不是產業標準或原作者的經驗數據。

## 1. Harness 架構與環境

```text
產品需求 + 品牌來源
        |
        v
HTML / DOM / Canvas / SVG  <-- Node 可選：打包或本機預覽
        |
        v
window.seek(t 毫秒) <-- Python + Playwright Chromium
        |
        +--> 正序 PNG --> 逆序 PNG --> 像素差 / 文字框 / 對比 / errors
        |                                  |
        |                                  v
        |                         Contact Sheet + Worst-3
        |                                  |
        |                           修正 <-- FAIL
        |                                  |
        v                                 PASS
每幀 seek --> frames/frame_%04d.png --> FFmpeg --> output.mp4
```

簡單單檔不需要 Node；需要時使用專案指定的 Node 版本。所有素材本機化，避免網路或字型改變影格。
Python 依賴安裝：`python -m pip install Pillow playwright`，再執行 `python -m playwright install chromium`。
工具以 Python Playwright 同步 API 載入本機 HTML。可用 `--channel msedge` 或 `--channel chrome` 明確選通道；不靜默切換。
`channel` 屬於 `chromium.launch`，不是 `page` API。

## 2. 時間函式與 seek 契約

`window.seek(tInMs): void | Promise<void>`；t 是非負毫秒。完成時畫面必須已繪製完畢。
任意順序呼叫同一 t，像素必須相同；位置、透明度等由絕對 t 算出，不能累加 `x += delta`。
停用 `setInterval`、持續的 `requestAnimationFrame`／`setTimeout` 迴圈、CSS 自動播放與未設種子的亂數；需要 CSS 動畫時讓它 `paused`，由 seek 設 `currentTime`。等待圖片解碼及字型就緒後才完成 Promise。
測試涵蓋抽樣時間，不證明所有時間或不同平台都逐像素相同。

### 2.1 彈簧與錯落時序

本 repo 偏好欠阻尼比 `zeta = c / (2 * sqrt(k*m))` 在 0.7..0.85，或臨界阻尼 1。
相鄰元素進場延遲 40..80ms。這些是設計偏好，工具不量測彈簧自然度、景深或美感。
下例 `k=16, c=6, m=1` 得 zeta=0.75；兩元素延遲差 60ms。
範例保留標題可見，避免 t=0 全空白；以較慢彈簧展示 3 秒內可量到的位移。
只有欠阻尼範圍可用此解析式，其他參數直接拒絕，沒有把過阻尼套成臨界阻尼。

```html
<!doctype html>
<html lang="zh-Hant">
<meta charset="utf-8">
<title>Motion fixture</title>
<style>
:root{--bg-primary:#112233;--text-primary:#ffffff;--accent-brand:#ffb703} /* 填空：換成品牌色票 */
body{margin:0;background:var(--bg-primary);color:var(--text-primary);font:32px sans-serif}
h1,p{position:absolute;margin:0;left:80px}
h1{top:80px;font-size:48px}p{top:230px}
#card{position:absolute;left:80px;top:380px;width:240px;height:120px;background:var(--accent-brand)}
</style>
<h1 id="title">Motion Studio</h1>
<p id="subtitle">Deterministic frames</p>
<div id="card"></div>
<script>
function spring(t,k=16,c=6,m=1){
  const z=c/(2*Math.sqrt(k*m));
  if(!(k>0 && m>0 && z>0 && z<1)) throw new Error('underdamped only');
  if(t<=0) return 0;
  const w=Math.sqrt(k/m), d=w*Math.sqrt(1-z*z);
  return 1-Math.exp(-z*w*t)*(Math.cos(d*t)+z*w/d*Math.sin(d*t));
}
window.seek=function(ms){
  const t=Math.max(0,ms)/1000;
  document.getElementById('title').style.transform=`translateX(${80*spring(t/3)}px)`;
  document.getElementById('subtitle').style.transform=`translateX(${80*spring((t-.06)/3)}px)`;
  document.getElementById('card').style.transform=`translateX(${80*spring((t-.12)/3)}px)`;
};
window.seek(0);
</script>
</html>
```

範例色彩（`:root` 三個變數）是驗證用中性配色，不是任何品牌。正式使用先照範本的品牌來源欄位提取色票，再只改這三個變數。
文字使用 DOM，讓工具可實測行框；Canvas/SVG 繪製的文字須額外人工檢查，不可宣稱已通過文字度量。

## 3. Anti-Slop 檢查表

| 編號 | 本 repo 禁制 | 工具的啟發式候選規則 |
| --- | --- | --- |
| SLOP-M01 | 漸層背景加置中標題 | 原始碼同時有任意 linear/radial gradient 與置中宣告，不限藍紫色 |
| SLOP-M02 | 全體同時淡入 | opacity transition 或名稱含 fade 的 animation；保守標記，未解析全部時間軸 |
| SLOP-M03 | 浮誇陰影、呆板角落標籤 | shadow-2xl 或含 25px/50px 的 box-shadow；未全面辨識標籤 |
| SLOP-M04 | 生硬線性運動、無阻尼彈跳 | transition/animation 的 linear 或 alternate infinite |
| SLOP-M05 | 假數字跳動、隨機粒子噪音 | Math.random 呼叫；非所有粒子或假數字都可識別 |

HTML/CSS 註解及獨立 JS 行註解會剝除；Emoji 與 elevate 不是 M05。
這不是完整 JS/CSS 語法分析器：可能誤報字串、漏掉外部腳本或別名。命中候選均阻擋，需人查明並修正實際設計；不可只刪除檢查或降低門檻。
未命中也不代表設計好，人工審查仍要看資訊順序、品牌與節奏。

## 4. 分鏡量測、評分與硬閘門

```text
每個抽樣 t 正序 seek -> 截圖 -> 文字 Range 行框與背景取樣
每個抽樣 t 逆序 seek -> 截圖 -> 與正序逐像素比對
相鄰正序 PNG -> RGB channel 平均絕對差（保留像素位置）
```

- 空白：Pillow 灰階標準差 < 1，包括全黑、全白、灰色及深色純背景。
- 動態：相鄰影格逐像素平均絕對差等於 0 即靜止；即使均值、標準差相同，移動的方塊仍可辨識。
- 冪等：同一 t 的正序與逆序 RGB 差必須等於 0。
- 排版：可見 DOM 文字節點的 Range 行框，不同文字節點之間交集面積超過較小行框的 25% 即碰撞；超出 1280x720 視窗或被祖先 overflow 裁切即失敗。同一文字節點自己的換行不算碰撞；25% 是本 repo 的取捨，容許緊行距。不是所有圖形的碰撞。
- 對比：暫時隱藏文字，對各行框左/中/右的背景像素取樣；文字色由瀏覽器解析成 sRGB（rgb、oklch、color-mix 等語法都適用，解析不出來即失敗），與祖先 opacity 合成後算相對亮度比，採三點最差值，必須 >=4.5。
- 頁面：console.error、未捕捉 pageerror、seek 拋錯/拒絕、執行期缺少函式均失敗。
- 自走：載入前包住計時 API 計數。呼叫過 `setInterval`、seek 完成後閒置 300ms 內仍排程 >=3 次 `requestAnimationFrame`／`setTimeout`（3 次是本 repo 的取捨）、或仍有播放中的 CSS/Web 動畫，均失敗。只比兩次截圖會漏掉剛好同相位的自走動畫，所以直接計數。
- 壞 PNG、影格數不足或 Contact Sheet PNG 缺失均失敗；缺 Pillow 不代填數值。

限制：三點背景取樣不能代表整個字形；遮擋、混合模式、濾鏡、CSS 偽元素、SVG/Canvas 文字、旋轉後非矩形碰撞不在文字量測保證內。無 DOM 文字時 `text_boxes=[]` 表示沒有可測文字，不是文字檢查合格證明。工具不評構圖重心、文字語意、糊焦、物理自然度或美感。靜態停留、完全淡出也會被保守阻擋，應調整設計/抽樣覆蓋並人工覆核，不可用抽樣隱藏已知缺陷。

量不到的文字不會被默默當成合格：偵測到 SVG 文字（`svg text/tspan/textPath`）、Canvas 文字（`fillText`／`strokeText` 被呼叫，載入前包住計數）、或被其他元素蓋住的 DOM 文字（行框中心點最上層元素不是文字自己的元素）時，報告多一個 `unmeasured` 欄位（`kind`、`count`、`frames`），stderr 印 `[WARN] 未量測`，Contact Sheet 加「未量測」段落。這不改變 exit code 與 `passed`，因為工具無法判斷這些文字好不好；它代表這部分的對比與碰撞沒有被量過，須人工檢查，不可引為通過證據。Canvas 計數只涵蓋主執行緒的 `fillText`／`strokeText`，用 `drawImage` 貼上已含文字的點陣圖偵測不到。

已知誤報：
- 漸層文字（`background-clip:text` 加 `color:transparent`）：隱藏文字後取樣到的背景就是漸層本身，文字色又是透明，對比會算成 1.0 而失敗。請改用實色文字讓工具能量；若堅持漸層文字，須人工目視確認該標題對比並在交付紀錄註明，不可為此放寬門檻或關閉檢查。
- 文字從畫面外滑入（抽樣時文字框在視窗外，判為超出畫面）與動畫結尾的停格（相鄰影格完全相同，判為靜止）：兩者都是合法設計卻會被保守阻擋，應調整抽樣範圍（`--timestamps`）使其落在有動作且文字在畫面內的區間，並人工覆核被排除的時段。

| 維度 | 最高分 | 實際扣分 |
| --- | --- | --- |
| layout | 2.5 | 每筆行框碰撞/裁切扣 1，最低 0 |
| contrast | 2.5 | 有空白、壞圖或對比不合格即 0 |
| motion | 2.5 | 相鄰靜止或 seek 不一致即 0 |
| anti_slop | 2.5 | 每個 M01..M05 候選扣 1，最低 0 |

未量到亮度或逆序差，該影格總分為 0。排序輸出 Worst-3 與時間、問題。
**所有影格 >=8 分、沒有任何 issues/errors/Anti-Slop 候選、所有影格與總覽產生，才可 PASS。**
分數只是診斷摘要，不能用其他維度分數抵消失敗。

```bash
python tools/audit_motion_storyboard.py index.html --duration 3000 --frames 6 --output-dir artifacts/storyboard --json
```

範圍：`--frames` 2..120；`--duration` 有限且 0 < ms <=600000；`--min-score` 8..10。
`--timestamps` 可替代等分抽樣，必須有 2..120 個嚴格遞增、位於 0..duration 的有限值；例如 `0,600,1200,1800,2400,3000`。
結束碼：0 通過；1 品質、頁面或影格失敗；2 缺依賴/瀏覽器、參數/路徑錯誤；3 逾時 INCOMPLETE。
`AI_INBOX_MOTION_TIMEOUT_MS` 控制單一瀏覽器操作及非同步 seek，預設 15000ms。`AI_INBOX_MOTION_TOTAL_TIMEOUT_S` 是整體保險，預設 600 秒；`page.evaluate` 本身沒有逾時，seek 若是同步無窮迴圈，逾時後行程印 INCOMPLETE 並以 3 結束。

### 4.1 測試與停止條件

預設 `python -m unittest discover -s tests` 不跑瀏覽器（CI 只裝 Pillow 時，跑參數、依賴、評分、文字量測等單元測試；瀏覽器測試整組明確 skip）；沒有 Pillow 時依賴 Pillow 的單元測試也明確 skip，不會變紅。
設 `AI_INBOX_BROWSER_TESTS=1` 後跑 `python -m unittest discover -s tests -p test_audit_motion_storyboard.py`。
`AI_INBOX_MOTION_TEST_TIMEOUT_SECONDS` 預設 90 秒/子程序；`AI_INBOX_MOTION_TEST_WORKERS` 預設 1；`AI_INBOX_MOTION_TEST_CHANNEL` 可指定 msedge/chrome，未設時 Windows 用 msedge，其他平台用 Chromium。
逾時明列 INCOMPLETE skip，既不是通過也不是品質失敗；測試會終止自己建立的程序樹。驗收報告須揭露 skip，不能將 exit 0 當完整瀏覽器驗收。
修復最低分分鏡後只跑受影響測試；有完整通過證據即停止，不反覆開瀏覽器。

## 5. 導出與 effort 路由

先通過分鏡檢查，再用範本的 `render_frames.py` 逐幀 seek 輸出 `frames/frame_0000.png` 起的序列。`render_frames.py` 每幀有可設定的整體逾時（`--frame-timeout` 或環境變數 `MOTION_RENDER_FRAME_TIMEOUT_S`，預設 60 秒），逾時印 INCOMPLETE 並 exit 3，已輸出的 PNG 不可交付。
以下命令可在 PowerShell 與 bash 單行執行：

```bash
ffmpeg -y -framerate 60 -start_number 0 -i frames/frame_%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart output.mp4
```

CRF 18 是本 repo 的有損交付起點，18..22 是可自行比較畫質與體積的試用區間，**不是無損，也不保證視覺無失真**。yuv420p 亦有色度抽樣損失；保留 PNG 當逐像素基準。`+faststart` 將 moov metadata 前移，改善啟播條件，不保證網路秒開。實際播放器相容性需另驗。

Effort 路由：局部文案/色票用既有低成本設定；完整短片先定分鏡；多鏡頭先定時序及風險再決定是否獨立 review。模型與 effort 名稱依使用平台的已驗證政策，不預設任何產品都有 medium/xhigh/max，也不為形式多叫模型。

## 6. 來源與查證（2026-11-02）

下列每筆都在 2026-11-02 實際開過頁面或原始檔，只寫頁面上看得到的內容；本文的門檻（8 分、4.5:1 以外的數值、25%、3 次、300ms 等）是本 repo 的取捨，不是這些來源給的數字。

- [Playwright Python BrowserType](https://playwright.dev/python/docs/api/class-browsertype)：`launch` 的 `channel` 選項列有 `chrome`、`msedge` 等值，另可用 `"chromium"` 選新 headless 模式。`channel` 只出現在這一頁，不在 Page API。
- [Playwright Python Page](https://playwright.dev/python/docs/api/class-page)：有 `evaluate`、`screenshot`，以及 `pageerror`、`console` 事件，與工具的用法對應。
- [FFmpeg n7.1 `doc/muxers.texi`](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1/doc/muxers.texi)（tag `n7.1`；annotated tag 物件是 507a51f，指向的 commit 是 b08d796，以 `git ls-remote https://github.com/FFmpeg/FFmpeg refs/tags/n7.1 'refs/tags/n7.1^{}'` 於 2026-11-02 核對）：第 387-388 行說明可在 `-movflags` 加 `+faststart` 把資料搬到檔案開頭以利播放；第 500-504 行說明 `faststart` 是第二遍把 moov atom 移到檔頭，耗時，且在 fragmented output 等情況不適用。官方渲染頁 ffmpeg-formats.html 本輪連線逾時，未讀。
- [FFmpeg H.264 編碼指南（Internet Archive 快照）](https://web.archive.org/web/2024/https://trac.ffmpeg.org/wiki/Encode/H.264)：原站目前回應反機器人驗證頁，改讀快照（頁尾 Last modified Dec 12, 2024，之後可能已有更新）。內容：CRF 範圍 0–51、預設 23，主觀合理範圍 17–28；17 或 18「visually lossless or nearly so」但 "isn't technically lossless"；真正無損要用 `-qp 0`（或特定 profile 的 `-crf 0`）；QuickTime 等播放器需要 `yuv420p`。因此本文把 CRF 18 稱為有損交付起點。
- [Remotion `random()`](https://www.remotion.dev/docs/random)：以 seed 取得確定性的偽亂數；Remotion 以多執行緒渲染，`Math.random()` 在各執行緒結果不同。只佐證「亂數要有 seed」，不證明其他部分。
- [Motion Canvas Introduction](https://motioncanvas.io/docs/)：TypeScript generator 動畫函式庫加即時預覽編輯器，頁尾版權 2023。只當同類工具參考，不證明本文的 seek 契約。
- [0xalpha.ai 的 Threads 貼文](https://www.threads.net/@0xalpha.ai/post/DeMLz-KD1EE)：以無頭 Edge 未登入開啟，頁面日期 2026-10-7。貼文列出七步：裝 Node、ffmpeg、Playwright 並用 Claude Code 跑 Opus 5.5；用 CLAUDE.md 寫工作室規範；影片是時間的函式，用 `seek(t)` 畫任何一格；規範裡禁掉漸層背景加置中標題、全部淡入、角落小標；產品影片給網址並用真實截圖、logo、品牌色；正式渲染前出縮圖總覽自評 1–10 分，修最差 3 個，全部 8 分以上才輸出；整套包成 skill；effort 小修用 medium、新片 xhigh、發表會開場才開 max。本文第 2～5 節是據此整理的本 repo 規範，貼文沒有提供 Playwright 實作、像素比對或任何量測門檻。
