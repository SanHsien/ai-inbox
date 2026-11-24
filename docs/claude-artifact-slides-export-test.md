# Claude Artifact「Slides」簡報匯出實測

## 基本資料

- 測試日期：2026-11-24
- 帳號方案：Claude Pro，Slides 類型可用
- 任務：ai-inbox T-20261113-01，決定本機簡報走哪條路線
- 測試內容：5 頁測試簡報（cover、why、compare 表格、chart 長條圖、next），字型用 Google Fonts 連結的 Inter 加 Noto Sans TC

## 實際觸發的工具呼叫

1. `Artifact` quickstart，intent=slides
2. `Artifact` publish，帶 Slides 類型的 type_url
3. 兩次 publish，寫入 `project/deck.json`、`project/deck.css`、5 個 `project/slides/*.html`
4. 匯出：在 claude.ai 檢視頁用 Claude in Chrome 點選「分享 › 匯出」下載

## 匯出選單選項

| 選項 | 是否實測 |
|---|---|
| PDF（下載前跳出 Image quality：Good／Better／Best；本次選 Best，未勾 speaker notes） | 已測 |
| PowerPoint「目前字型」（說明：可編輯；使用簡報的字型） | 已測 |
| PowerPoint「基本字型」（說明：可編輯；使用每台電腦都有的字型） | 已測 |
| 投影片轉為圖片（每頁一張圖，文字不可編輯） | 未測 |
| PNG | 未測 |
| Google Slides | 未測 |

## 測試方法

- PPTX 用本機 PowerPoint（COM）逐頁匯出 1600x900 PNG；PDF 用 PyMuPDF 以 120 dpi 轉 PNG。
- 結構檢查用 python-pptx、直接解 zip 看 XML，以及 PyMuPDF。
- 比對基準是原始網頁版（deck.css 與 slides/*.html）。
- 輸出圖在 `render/` 下四個資料夾：`pdf`、`artifact-current-fonts`、`artifact-basic-fonts`、`pptx-skill`，各 5 張。
- 渲染環境：本機沒有 Inter，PowerPoint 版的外觀是「這台電腦」的結果，換機器可能不同。
- 本機有 Microsoft JhengHei；是否有 Noto Sans TC 未查。

## 結構檢查結果

| 項目 | artifact-export.pdf | artifact-current-fonts.pptx | artifact-basic-fonts.pptx | pptx-skill.pptx |
|---|---|---|---|---|
| 檔案大小 | 662,212 B | 107,432 B | 39,950 B | 30,465 B |
| 文字 | 每頁一張 3840x2160 點陣圖鋪滿整頁，上面疊隱形文字層（字型 Glyphless）。能抽出字，但畫面是圖 | 可編輯文字框（42 個 run） | 可編輯文字框（42 個 run） | 可編輯文字框（60 個 run） |
| 字型名稱 | 無（畫面是圖） | 全部是 Inter（latin、ea、cs 都指 Inter） | 全部是 Arial（latin、ea、cs 都指 Arial） | Microsoft JhengHei（40 個 run）、Arial（20 個 run） |
| 內嵌字型 | 不適用 | 有，`ppt/fonts/` 兩個 .fntdata（各約 67 KB），embeddedFontLst 只列 Inter 的 regular 與 bold；沒有 Noto Sans TC | 無 | 無 |
| 表格 | 圖（內含可抽出的文字層） | 原生表格 5x3，欄寬 28／36／36%，儲存格有框線 | 同左 | 原生表格 5x3 |
| 圖表 | 圖 | 長條與軸線是一張 PNG 圖片，4 個數值與 4 個週標籤是分開的文字框；不是原生圖表 | 同左 | 原生 PowerPoint 圖表（clustered column，`ppt/charts/chart1.xml`） |
| 圖片數量 | 5 張整頁圖 | 1 張（圖表） | 1 張（圖表） | 0 |

兩個 Artifact PPTX 的圖表圖片是同一份（image-4-1.png，32,575 B）。

## 逐頁比對

### 第 1 頁 cover（深色底、橘色 eyebrow、兩行大標、副標）

| 項目 | PDF | PPTX 目前字型 | PPTX 基本字型 |
|---|---|---|---|
| 字型替換 | 無差異（畫面是 Inter 加中文黑體，是點陣圖） | 副標看起來變成有襯線字體；eyebrow 與大標仍是無襯線 | 英文變 Arial，中文是系統黑體；整體接近原樣 |
| 中文缺字或豆腐方塊 | 無 | 無 | 無 |
| 換行 | 無差異（副標兩行） | 副標斷在「對 / 照。」，與網頁版（「與 pptx skill / 對照。」）不同 | 副標斷點與 PDF 不同（「與 / pptx skill 對照。」），第一行多放了一個「與」 |
| 位置偏移 | 無差異 | 基線小幅偏移，肉眼看差距很小 | 同左 |
| 顏色 | 無差異 | 無差異（橘色 eyebrow、底色都對） | 無差異 |

### 第 2 頁 why（三張卡片）

| 項目 | PDF | PPTX 目前字型 | PPTX 基本字型 |
|---|---|---|---|
| 字型替換 | 無差異 | 卡片內文（含英文與中文）變有襯線字體；標題維持無襯線 | 內文變 Arial 加系統中文，無襯線，外觀相近 |
| 中文缺字或豆腐方塊 | 無 | 無 | 無 |
| 換行 | 無差異 | 內文換行與 PDF 不同（「，」前換行處不同） | 部分斷點不同（第一張卡「deck」後接「，不用…」換行） |
| 位置偏移 | 無差異 | 無明顯偏移 | 無明顯偏移 |
| 顏色與卡片 | 無差異（白卡片、陰影、淺米色底） | 無差異，陰影保留 | 無差異 |

### 第 3 頁 compare（表格）

| 項目 | PDF | PPTX 目前字型 | PPTX 基本字型 |
|---|---|---|---|
| 字型替換 | 無差異 | 表格內文（不含粗體表頭）變有襯線字體 | Arial，外觀相近 |
| 中文缺字或豆腐方塊 | 無 | 無 | 無 |
| 換行 | 無差異 | 無差異（每格單行） | 無差異 |
| 表格欄寬、框線 | 無差異 | 欄寬 28／36／36% 與原稿相同；框線灰色，表頭灰底，皆保留 | 同左 |
| 位置偏移 | 無差異 | 無明顯偏移 | 無明顯偏移 |
| 顏色 | 無差異 | 無差異 | 無差異 |

### 第 4 頁 chart（SVG 長條圖加文字標籤）

| 項目 | PDF | PPTX 目前字型 | PPTX 基本字型 |
|---|---|---|---|
| 字型替換 | 無差異 | 週標籤（Week 1–4）變有襯線字體；數值粗體維持 | Arial，無襯線 |
| 中文缺字或豆腐方塊 | 無 | 無（「28（最高）」正常） | 無 |
| 換行 | 無差異 | 無差異 | 無差異 |
| 位置偏移 | 無差異 | 長條、數值、標籤位置與 PDF 看起來一致 | 同左 |
| 圖表標籤位置 | 無差異 | 無差異，但圖是圖片、標籤是文字框，沒有綁定 | 同左 |
| 顏色 | 無差異（藍色加橘色最高值） | 無差異 | 無差異 |
| 可編輯性 | 不可編輯 | 數值要改只能改文字框，長條改不了 | 同左 |

### 第 5 頁 next（深色結尾頁）

| 項目 | PDF | PPTX 目前字型 | PPTX 基本字型 |
|---|---|---|---|
| 字型替換 | 無差異 | 副標（含檔名 docs/claude-artifact-slides-export-test.md）變有襯線字體 | Arial 加系統中文，外觀接近 |
| 中文缺字或豆腐方塊 | 無 | 無 | 無 |
| 換行 | 無差異（單行） | 無差異（單行） | 無差異（單行） |
| 位置偏移 | 無差異 | 無明顯偏移 | 無明顯偏移 |
| 顏色 | 無差異 | 無差異 | 無差異 |

### 整體小結

- PDF：5 頁畫面與網頁版一致，沒有發現跑版。代價是畫面是 3840x2160 點陣圖，文字不可編輯。
- PPTX 目前字型：版面位置、表格、顏色都保留；但在這台沒有 Inter 的電腦上，內文與表格文字的渲染變成有襯線字體，是最明顯的字型差異。內嵌的 Inter 只有 regular 與 bold，沒有內嵌 Noto Sans TC，中文是否也靠 Inter 的 ea 指定退回系統字型，本次沒有進一步驗證。
- PPTX 基本字型：全部 Arial，沒有襯線字體問題，版面與 PDF 最接近；代價是字型不是原設計的 Inter。
- 兩個 PPTX 的圖表都是圖片，不是原生圖表。

## 與 pptx skill 版的對照

pptx skill 版內容相同，但不是網頁版的複製，而是重新排版，逐頁差異如下：

| 頁面 | 差異 |
|---|---|
| 第 1 頁 | 兩行大標被合成一行「簡報匯出實測 / Slides Export Test」；eyebrow 不是橘色；副標變窄。其餘深色底保留 |
| 第 2 頁 | 背景是白色，不是米色；eyebrow「測試目的」整個消失；卡片是灰底、沒有陰影，標題與內文合成一段（「省時間：…」），多出三個橘色圓點；卡片較高、文字偏上，下方留白 |
| 第 3 頁 | eyebrow「比較表」消失；表頭變深藍底白字，第一欄變粗體，表格較高；背景白色 |
| 第 4 頁 | eyebrow「圖表」消失；圖表是原生圖表，第 1、2、4 週長條顏色變成灰藍色（原稿是 #2F6FB3 藍），多出 Y 軸（0–30）與格線；數值標籤不是粗體；「28（最高）」變成只有「28」 |
| 第 5 頁 | eyebrow 不是橘色；大標比原稿大；副標位置偏下 |

優點：原生圖表可直接改數據；字型用本機有的 Microsoft JhengHei 加 Arial，不會缺字；檔案最小（30,465 B）。
缺點：不會忠實還原網頁版設計，每頁都要另外校對；中文版型要自己描述。

## 路線建議

結論先講：這次樣本只有 5 頁、一台電腦，下面是根據這份實測的取向，不是一般性保證。

| 情境 | 建議 | 實測依據 |
|---|---|---|
| 只要看、要傳給別人、版面要完全不變 | Artifact PDF（Best） | 5 頁都與網頁版一致，沒有跑版；缺點是整頁是點陣圖，文字不能改，檔案 662 KB |
| 要帶走再改字、可接受英文字型改 Arial | Artifact PPTX「基本字型」 | 結構是原生文字框與原生表格，沒有襯線替換，版面最接近 PDF；圖表仍是圖片 |
| 要帶走再改字、且對方電腦有 Inter | Artifact PPTX「目前字型」 | 版面一樣，有內嵌 Inter regular 與 bold；但本機沒有 Inter 的環境渲染出襯線字體，對方沒有 Inter 時是否正常未測 |
| 圖表數據要能改、可以重新排版 | pptx skill | 唯一有原生圖表；但設計與網頁版不一致，需另外校對 |

未測的部分：「投影片轉為圖片」、PNG、Google Slides、speaker notes 匯出、Image quality 選 Good 或 Better 的差別、內嵌字型在另一台電腦的實際顯示、超過 5 頁的簡報。不在這些項目上下結論。
