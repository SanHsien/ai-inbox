# 上游簡體開源專案之零漂移繁體中文 Fork 自動同步規範

> 修訂日期：2026-11-14。上游固定版本：`c9b003c76571b4df97407b743a057289f9b7e34c`。
> 標題沿用既有規範名稱；「零漂移」不是任意 Fork 的保證。本文只讀比對原始碼，未執行上游同步、安裝、建置或推送；不宣稱零衝突或完整 OpenCC 管線已在本機驗收。

## 1. 範圍與錯誤範例

上游採取從 `upstream/main` 重建 `zh-tw` 的方式，避免逐次合併已翻譯的分支；這是生成分支的同步策略，無法保證任意 Fork 的自訂改動都能保留。[sync.sh](https://github.com/doggy8088/answer-me-with-html/blob/c9b003c76571b4df97407b743a057289f9b7e34c/scripts/zh-tw/sync.sh#L1-L28)

上游詞庫列有以下修補對。這是該版本的規則與註解，OpenCC 在其他版本或任意文本上的轉換結果均未查證。[vocab.mjs](https://github.com/doggy8088/answer-me-with-html/blob/c9b003c76571b4df97407b743a057289f9b7e34c/scripts/zh-tw/vocab.mjs)

| 原文／誤轉範例 | 修正結果 | 規則語境 |
|---|---|---|
| `連線埠` | `連接埠` | 上游註解將前者列為二次退化結果 |
| `隻影響` | `只影響` | 副詞與量詞誤轉修補 |
| `選一個類別型` / `型別別` | `選一個類型` / `型別` | 疊字修補 |
| `字面量（Literal）（Literal）` | `字面量（Literal）` | 重複註記修補 |
| `瞭什麼` | `了什麼` | 助詞修補 |
| `其他寫程式的 WAV` | `其他編碼的 WAV` | 音訊 encoding，錯誤範例是「寫程式」 |
| `瀏覽器自己寫程式並下載` | `瀏覽器自己編碼並下載` | 音訊 encoding |
| `渲染時會打印帶稿件行號的警告` / `並打印路徑` | `渲染時會輸出帶稿件行號的警告` / `並輸出路徑` | stdout 輸出 |
| `參考檔案` | `參考文件` | Documentation 語境還原 |

本庫另有 `摁下` → `按下` 規則；禁用範例是前者，不能把正確「按下」列為錯誤。這條及本庫其他延伸規則不代表上游詞庫的完整複製。[本庫規則](../tools/verify_zhtw_vocab.py)

## 2. 上游 sync.sh 逐段對照

以下行號均指上述固定 SHA 的 [sync.sh](https://github.com/doggy8088/answer-me-with-html/blob/c9b003c76571b4df97407b743a057289f9b7e34c/scripts/zh-tw/sync.sh)，是行為說明，不是可直接執行的本庫操作指令。

```text
讀取遠端 SHA / 本地 zh-tw 的 .base-sha
  -> 相同：NOCHANGE，exit 0
  -> 不同：fetch -> 推 origin/main -> 重建 zh-tw
           -> 從 origin/zh-tw 還原腳本與圖片
           -> convert -> 寫 .base-sha -> build -> check -> 測試白名單
           -> commit -> force-with-lease 推 origin/zh-tw
```

| 原始碼行 | 實際行為 |
|---|---|
| 11–18 | `set -eu`，切至 repo 根目錄；用 `git ls-remote upstream main` 取 SHA，從本地 `zh-tw:scripts/zh-tw/.base-sha` 讀舊值；相同才印 `NOCHANGE` 並 exit 0。仍有遠端查詢成本。 |
| 20–23 | `git fetch upstream main`，先推送 `upstream/main:main` 至 origin，再 `git checkout -B zh-tw upstream/main` 重建本地分支。 |
| 24–28 | 從 `origin/zh-tw` checkout `scripts/zh-tw` 與六張圖片：`tcp.png`、`architecture-dark.png`、`video-zh.png`、`text-vs-page-zh.png`、`og-en.jpg`、`og-zh.jpg`。兩個 checkout 都有 `|| true`；失敗不會立即中止。並非將本地資產備份到 `$TMP`，也未在此判斷生成腳本是否改變。 |
| 29–31 | 將本地 node bin 加入 PATH；找不到 `opencc-cli` 才全域安裝 `@willh/opencc-cli@0.1.5`，接著執行 `convert.mjs`。本次未執行這些命令。 |
| 32–35 | 先寫 `.base-sha`，再 `npm ci --ignore-scripts`、`npm run build`、`check.mjs`。錨點寫入不是所有驗證通過後才發生。 |
| 36–44 | `npm test` 輸出寫 `/tmp/zh-tw-test.log`；暫時關閉 `set -e`，抽取 `✖` 測試名稱，排除摘要及 `known-test-failures.txt` 白名單；只有 EXTRA 非空才明確 exit 1。不能描述為保證所有測試 exit 0；非該輸出格式的異常也可能漏判。 |
| 46–51 | `git add -A`、建立生成 commit，然後 `git push --force-with-lease origin zh-tw`。 |
| 52 | 印出 `SYNCED upstream=...`。 |

來源：[sync.sh 固定版本全文](https://github.com/doggy8088/answer-me-with-html/blob/c9b003c76571b4df97407b743a057289f9b7e34c/scripts/zh-tw/sync.sh#L11-L52)。此腳本會安裝、重建分支與對外推送，本文不建議在未審閱的工作樹直接執行。

`convert.mjs` 對指定內容呼叫 OpenCC `-f cn -t tw2` 並套用詞庫；`check.mjs` Gate 4 再對 CONTENT 執行 OpenCC + applyVocab，與現有內容比對。此外還有 zh-CN 殘留、簡體字、詞彙、文件連結及 repo slug 閘門。這是指定語料上的檢查，不能推論任意輸入的冪等性。[convert.mjs](https://github.com/doggy8088/answer-me-with-html/blob/c9b003c76571b4df97407b743a057289f9b7e34c/scripts/zh-tw/convert.mjs)、[check.mjs](https://github.com/doggy8088/answer-me-with-html/blob/c9b003c76571b4df97407b743a057289f9b7e34c/scripts/zh-tw/check.mjs)

## 3. 本庫工具的實際契約

本庫 Python 工具只做內建詞庫替換，不執行 OpenCC。每輪依規則順序替換，反覆直到固定點；例如 `型別別別` 一次 API 呼叫即收斂為 `型別`。若規則循環則拒絕處理。`--verify-idempotent` 驗證內建規則與重疊樣本，並非 OpenCC 端到端測試或任意文本的形式證明。[實作](../tools/verify_zhtw_vocab.py)、[回歸測試](../tests/test_verify_zhtw_vocab.py)

`--check` / `--fix` 會略過 Markdown 圍欄與單行內長度相同的反引號 run；不同長度不能配對，未閉合 run 視為正文。這是本庫的有限 tokenizer，不宣稱完整 CommonMark（例如跨行 code span 未支援）。目錄遞迴收集 `.md`，明確指定檔案則直接處理；不存在路徑、零檔案、空白檔案、無法讀取或非 UTF-8 均失敗。先檢查全部輸入再修補，但多檔寫入沒有交易回滾保證。[實作](../tools/verify_zhtw_vocab.py)

```powershell
python tools/verify_zhtw_vocab.py --verify-idempotent
python tools/verify_zhtw_vocab.py --verify-idempotent --check notes docs templates README.md
python tools/verify_zhtw_vocab.py --fix path/to/file.md
```

結束碼：`0` = 請求的操作通過；`1` = 發現詞彙問題或冪等樣本失敗；`2` = 引數／輸入／讀寫錯誤（含無操作及零輸入）。`--fix` 只修補，不保證文件事實正確；錯誤反例應放在程式碼引用中保留，不能批次轉成正確詞後仍稱為錯誤範例。[CLI](../tools/verify_zhtw_vocab.py)
