---
id: 2026-11-07-willh-doggy8088-answer-me-with-html-zhtw-fork
title: "Will 保哥推薦 answer-me-with-html 繁中分支（doggy8088/answer-me-with-html@zh-tw）評估：OpenCC 自動同步轉換管線、OpenCC 二次誤轉修補字典，與既有自建視覺化工件對照"
source_url: "https://www.facebook.com/100064322940906/posts/1590827443071339/"
source_platform: "Facebook (Will 保哥的技術交流中心)"
author: "Will 保哥 (@will.fans / @doggy8088)"
analyzed_at: 2026-11-07
analyzed_by: "Antigravity"
status: done
cluster: "2"
cluster_role: "視覺工件與互動 UI"
short_title: "保哥 answer-me-with-html 繁中 Fork 評估"
source_review: full
source_reviewed_at: 2026-11-16
source_images: 5
source_replies: 10
tags:
  - answer-me-with-html
  - opencc
  - zh-tw-localization
  - upstream-sync
  - agent-skills
---

# Will 保哥推薦 answer-me-with-html 繁中分支（doggy8088/answer-me-with-html@zh-tw）評估：OpenCC 自動同步轉換管線、OpenCC 二次誤轉修補字典，與既有自建視覺化工件對照

- **來源連結**：[Facebook 貼文：Will 保哥的技術交流中心](https://www.facebook.com/100064322940906/posts/1590827443071339/) ｜ [分享短網址](https://www.facebook.com/share/19PyAfYJ4k/)
- **保哥繁中 Fork 倉庫**：[`doggy8088/answer-me-with-html`](https://github.com/doggy8088/answer-me-with-html/tree/zh-tw)（預設分支 `zh-tw`，110 Stars、11 Forks，快照日 2026-11-07；2026-11-16 重審時 194 Stars、24 Forks，未開放 Issues；上游為 [`QingYunA/answer-me-with-html`](https://github.com/QingYunA/answer-me-with-html)）
- **發布時間**：2026-11-07 08:34 (UTC+8)（2026-11-16 重審時：760 個心情、10 則留言、182 次分享）
- **歸屬集群**：集群 2：Code-as-Video、視覺特效與 Generative UI（角色：`上游追蹤與繁體中文化管線`）
- **評估結論**：`🟢 answer-me-with-html 渲染器已落地；保哥 zh-tw 分支的「零漂移自動同步 + OpenCC 二次退化修補詞庫」極具工程價值，已轉化為本機檢查工具與同步規範`
- **相關交叉參照**：
  - [`notes/2026-10-26-answer-me-with-html-visual-agent-artifacts.md`](./2026-10-26-answer-me-with-html-visual-agent-artifacts.md)（本機已於 2026-10-26 完成 `answer-me-with-html` 深度分析，並交付 `docs/visual-agent-artifacts-engineering-spec.md` 與 `tools/render_artifact_html.py`，任務 `T-20261026-06`、`T-20261026-07` 已結案）

---

## 0. 原始資料盤點

> 2026-11-16 重審：Facebook 未登入可讀貼文全文、連結預覽卡與全部 10 則留言；另開 `README.zh-TW.md` 看內文與圖片。

- **作者圖片**：貼文本身沒有上傳圖片，只有一張 GitHub 連結預覽卡（repo 名稱、繁中簡介、194 星、24 fork）。連到的 `README.zh-TW.md` 有 5 張內容圖，逐張放大看過：
  - 圖 1 `plain-vs-skill.png`：同一個 TCP 問題的兩種做法並排，直接要 HTML 是 9,351 個輸出 token、57 秒；用技能是 899 個、11 秒。圖內文字是英文，沒有重產成繁中。
  - 圖 2 `video-zh.png`：解釋影片的四個畫面（片頭、時序圖、流程圖、對比表），繁中。
  - 圖 3 `tcp.png`：TCP 三次握手與四次揮手的範例頁，六個面板（時序圖、為什麼是三次、狀態遷移、`關鍵數位`、四次揮手、標誌位對照表），繁中。
  - 圖 4 `ste100.png`：ASD-STE100 總覽頁，英文。
  - 圖 5 `architecture-dark.png`：暗色單欄樣板，說明技能本身的渲染流程與目錄結構，繁中。
- **作者留言補充**（2 則回覆）：
  - 回 `黃德友`（說類似 eli5）：「差很多」。
  - 回 `Hc Chang`（問能否整合某種分析法）：反問對方那種分析法是什麼呈現方式，沒有結論。
  - 作者沒有回答 `Jim Kang` 與 `Jack Jack` 的問題。
- **網友留言重點**（10 則全部讀到）：
  - `余小章`：用 `npx -y skills add doggy8088/answer-me-with-html -g -y -a` 加萬用字元一次裝到所有 Agent，更新用 `npx skills update`。
  - `Jim Kang`：問到底什麼時候用（產文件時，還是每次回覆），說自己還找不到好用途。沒有人回答。
  - `Jack Jack`：問和 fork 之前有什麼差別。沒有人回答；答案就是本筆記第 2 節（內容相同，只多了繁中轉換管線）。
  - `Chieh Hao Hsu`：等於幫你把部落格內容寫好。`Dollen Kuo Jerry`：實用，資料再利用方便。
- **對分析的影響**：
  - 發布時間原寫「00:34 (UTC+8)」，頁面顯示上午 8:34，原值其實是 UTC；互動數與星數一併更新。
  - 圖 1 的數字（9,351 對 899、57 秒對 11 秒）是單一題目的示範，和 README 內文的平均值（4,893 對 612、31 秒對 12 秒）不同；第 1 節原寫「8x 輸出 Token 節省」沿用的是平均值，已註明出處，避免和圖上的約 10 倍混用。
  - 重審時讀 `README.zh-TW.md` 內文，發現轉換管線仍留下幾個詞沒修：`粘貼給你的 Agent`（台灣慣用「貼上」）、`每次都得到同樣的數位`（原意是數字）、圖 3 面板標題 `關鍵數位` 也是同一個誤轉。本機 `tools/verify_zhtw_vocab.py` 目前也沒有這兩條規則，新增任務 `T-20261107-06` 補上。
  - `Jim Kang` 的疑問補進第 1 節：README 自己的答案是「關係複雜、多步流程、多維對比才出頁面」，另有預設關閉的高頻模式。

---

## 1. 貼文重點與本機現況對照

- **貼文內容**：Will 保哥分享自己使用 `answer-me-with-html` 一週的心得（「從一開始的沒什麼，用到現在怎樣也離不開」），並附上他自己維護的繁體中文分支 [`doggy8088/answer-me-with-html` (`zh-tw`)](https://github.com/doggy8088/answer-me-with-html/blob/zh-tw/README.zh-TW.md)。
- **留言區補充**：余小章分享 `npx -y skills add doggy8088/answer-me-with-html -g -y -a '*'` 與 `npx skills update` 一鍵安裝至所有 Agent 的指令。
- **留言區的疑問**：有人問「到底什麼時候用」且沒人回答。README 的說法是由 Agent 判斷，概念關係複雜、有多步流程或要做多維對比才出頁面；另有預設關閉的「高頻模式」，打開後每個結論都附一頁。
- **與本機對照**：`answer-me-with-html` 的核心概念（語意 Markdown 草稿 + 確定性渲染分離、8x 輸出 Token 節省（README 的 9 頁平均：4,893 對 612 個 token；README 首圖的單題示範是 9,351 對 899）、ASD-STE100 受控語言）我們已在 **2026-10-26** 完整評估並實作本機 Python 渲染器 `tools/render_artifact_html.py`（18 項測試全綠）。因此**不需要再重複為 `answer-me-with-html` 本身開任務**。

---

## 2. 真正值得深挖的亮點：保哥如何維護「零漂移」的繁體中文 Fork

透過 GitHub API 比對 `doggy8088/answer-me-with-html` 的 `main...zh-tw`（快照日 2026-11-07 筆記記為 `ahead_by=2, behind_by=0`；2026-11-14 複查為 1，該值隨推送變動），發現保哥沒有手動改檔，而是寫了一套 `scripts/zh-tw/` 自動化繁中再生管線，非常乾淨且具冪等性（Idempotent）：

```text
upstream/main (QingYunA)
   │
   ├─► 1. 比對 scripts/zh-tw/.base-sha，上游沒動就 NOCHANGE 退出
   ├─► 2. git checkout -B zh-tw upstream/main（每次都從上游全新重建，不留 merge 髒歷史）
   ├─► 3. 保留 scripts/zh-tw/ 與 4 張繁中重產生的示範圖 (regen-images.mjs)
   ├─► 4. convert.mjs：呼叫 @willh/opencc-cli (cn -> tw2) + 套用 vocab.mjs 修補字典
   ├─► 5. npm run build + check.mjs（驗證再跑一次轉換完全無 diff，確保冪等）+ npm test
   └─► 6. git push --force-with-lease origin zh-tw
```

### 保哥在 `scripts/zh-tw/vocab.mjs` 整理的 OpenCC 常見誤轉修補字典（可直接備查）

OpenCC 的 `cn -> tw2` 在技術文件與二次轉換（second-pass）時有幾個經典誤傷，保哥用兩層字典修掉：

| 類別 | OpenCC 轉換後（或原文） | 修正為台灣慣用詞 | 原因說明 |
|---|---|---|---|
| **OpenCC 二次退化 / 斷詞誤判** | `連線埠` | `連接埠` | OpenCC 對「連接埠」跑第二次會退化成 `` `連線埠` `` |
| | `隻影響` | `只影響` | 副詞「只」（僅）被誤轉成量詞「隻」 |
| | `選一個類別型` / `型別別` | `選一個類型` / `型別` | 「類型 / 型別」疊字退化 |
| | `字面量（Literal）（Literal）` | `字面量（Literal）` | 括號英文註記重複附加 |
| | `瞭什麼` | `了什麼` | 助詞「了」被誤轉為「瞭」 |
| **語境多義詞（一詞多譯）** | `其他寫程式的 WAV` / `自己寫程式並下載` | `其他編碼的 WAV` / `自己編碼並下載` | 簡體「编码」被 OpenCC 無腦轉成「寫程式」，音訊語境應為「編碼」 |
| | `渲染時會打印…` / `並打印路徑` | `渲染時會輸出…` / `並輸出路徑` | 終端機 stdout 的「打印」應為「輸出」；紙本列印才用「列印」 |
| | `文件` vs `參考檔案` | `檔案` vs `參考文件` | 檔案系統是「檔案」，但 Documentation 被轉成 `` `參考檔案` `` 需還原為「參考文件」 |

---

## 3. 關於留言區 `npx -y skills add ... -g -y -a '*'` 的提醒

留言提到的 `-a '*'` 會把 Skill 一口氣裝進系統上偵測到的所有 Agent 全域目錄。雖然方便，但會跳過個別 Agent 的描述空間與觸發評估。若真要安裝保哥的繁中版 `answer-me-with-html`，建議指定單一主力 Agent（例如 `-a claude-code`），不要無腦用 `-a '*'` 全灑。

---

## 4. 待辦

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [x] **`T-20261107-02`**｜**[優先級：高]** 借鑑保哥 `scripts/zh-tw/vocab.mjs` 實作「台灣繁體中文技術詞彙與 OpenCC 二次退化檢查／冪等修補工具」於 `tools/verify_zhtw_vocab.py` 與單元測試
  - **目標範圍**：`tools/verify_zhtw_vocab.py`、`tests/test_verify_zhtw_vocab.py`
  - **具體做法**：
    1. 實作 `apply_zhtw_vocab()`、`scan_degraded_vocab()` 與 `verify_idempotence()`，內建 OpenCC (`cn -> tw2`) 二次轉換退化修補（`連線埠→連接埠`、`隻影響→只影響`、`選一個類別型→選一個類型`、`型別別→型別`、`字面量（Literal）（Literal）→字面量（Literal）`、`瞭什麼→了什麼`）、語境多義詞還原（音訊 `寫程式→編碼`、終端機 `打印→輸出`、`參考檔案→參考文件`）及大陸動詞修補（`摁下→按下`）。
    2. 支援略過 Markdown 圍欄程式碼區塊與行內反引號反例（`skip_code=True`），並提供 `--check`、`--fix`、`--verify-idempotent` CLI。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_zhtw_vocab.py` 綠燈通過，且 `python tools/verify_zhtw_vocab.py --verify-idempotent --check notes docs templates README.md` 全數通過。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正（2026-11-14）：行內程式碼依反引號 run 長度配對；--check 遇不存在路徑、零輸入、空檔、非 UTF-8 回 2；修補反覆執行到固定點（`型別別別` → `型別`）。DoD 指令 `python tools/verify_zhtw_vocab.py --verify-idempotent --check notes docs templates README.md` 現為 exit 0。4 項回歸測試，mutation 皆被抓到。

- [x] **`T-20261107-03`**｜**[優先級：中]** 撰寫「上游簡體開源專案之零漂移繁體中文 Fork 自動同步規範（`reset from upstream + OpenCC + 冪等詞庫修補`）」收錄於 `docs/zhtw-fork-idempotent-sync-spec.md`
  - **目標範圍**：`docs/zhtw-fork-idempotent-sync-spec.md`
  - **具體做法**：
    1. 完整記錄保哥 `doggy8088/answer-me-with-html@zh-tw` 如何以 `.base-sha` 錨點、`git checkout -B zh-tw upstream/main` 強制重建、OpenCC + 兩層詞庫修補與雙重冪等檢驗閘門，徹底消除上游簡體專案 Fork 的合併衝突與二次轉換退化。
  - **驗收標準（DoD）**：產出 `docs/zhtw-fork-idempotent-sync-spec.md`；以 `Test-Path docs/zhtw-fork-idempotent-sync-spec.md` 驗證存在。
  - **完成日期**：2026-11-14
  - **實作紀錄 / 證據**：修正（2026-11-14）：恢復被批次轉換破壞的錯誤範例；備份流程逐行對照上游 sync.sh（固定 SHA c9b003c76571b4df97407b743a057289f9b7e34c）改寫，更正原文三處與實際不符的描述（沒有備份到 $TMP、先寫 .base-sha、測試只比對白名單）。

- [x] **`T-20261107-04`**｜**[優先級：中]** 升級 `tools/render_artifact_html.py` 支援 `--zhtw` 編譯前台灣繁體中文詞庫修補並保持預設輸出位元組確定性
  - **目標範圍**：`tools/render_artifact_html.py`、`tests/test_render_artifact_html.py`
  - **具體做法**：
    1. 於 `render(source, normalize_zhtw=False)` 與 CLI 新增 `--zhtw` 選項，啟用時自動呼叫 `verify_zhtw_vocab.apply_zhtw_vocab(source, skip_code=True)` 修補草稿中的 OpenCC 二次退化詞與大陸用語，且不更動程式碼區塊。
    2. 預設未加 `--zhtw` 時維持 100% 原始位元組輸出，確保既有 `T-20261026-06` 確定性雜湊不變。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_render_artifact_html.py` 綠燈通過。
  - **完成日期**：2026-11-07
  - **實作紀錄 / 證據**：已於 `tools/render_artifact_html.py` 新增 `normalize_zhtw` 與 `--zhtw` 參數，並於 `tests/test_render_artifact_html.py` 新增 `test_zhtw_normalization_repairs_degraded_vocab_outside_code`，19 項測試全數通過。

- [x] **`T-20261107-06`**｜**[優先級：低]** 為 `tools/verify_zhtw_vocab.py` 補 `粘貼→貼上` 與數字被誤轉成「數位」的語境規則與測試
  - **目標範圍**：`tools/verify_zhtw_vocab.py`、`tests/test_verify_zhtw_vocab.py`
  - **具體做法**：
    1. 來源：2026-11-16 重審時在 `doggy8088/answer-me-with-html` 的 `README.zh-TW.md` 讀到 `粘貼給你的 Agent`、`每次都得到同樣的數位`、`關鍵數位`，是該 repo 轉換管線與本機詞庫都沒涵蓋的殘留。
    2. 新增 `粘貼→貼上`（無歧義，直接替換）。
    3. 「數位」在台灣是 digital 的正確用詞，不能整詞替換；只加語境片語規則（`同樣的數位→同樣的數字`、`關鍵數位→關鍵數字`），並補一個反例測試確認「數位轉型」「數位簽章」不被改動。
    4. 兩條規則都要通過既有的冪等檢查，且不動程式碼區塊與行內反引號。
  - **驗收標準（DoD）**：執行 `python -m unittest tests/test_verify_zhtw_vocab.py` 綠燈通過（含新增的正例與「數位轉型」反例）；`python tools/verify_zhtw_vocab.py --verify-idempotent --check notes docs templates README.md` 維持 exit 0。
  - **完成日期**：2026-11-17
  - **實作紀錄 / 證據**：tools/verify_zhtw_vocab.py 新增 `粘貼→貼上` 與「數位」語境規則（含 digital 複合詞排除）、--fix 保留換行；tests/test_verify_zhtw_vocab.py 39 tests OK（含數位轉型反例）；--verify-idempotent --check notes docs templates README.md exit 0。
