# 上游簡體開源專案之零漂移繁體中文 Fork 自動同步規範

> **版本**：1.0.0  
> **建立日期**：2026-11-07  
> **來源依據**：萃取自 Will 保哥（[`doggy8088/answer-me-with-html@zh-tw`](https://github.com/doggy8088/answer-me-with-html/tree/zh-tw)，上游 [`QingYunA/answer-me-with-html`](https://github.com/QingYunA/answer-me-with-html)）之 `scripts/zh-tw/` 自動化繁體中文化管線，對應任務 `T-20261107-02`、`T-20261107-03`、`T-20261107-04`。

---

## 1. 核心痛點：為什麼傳統繁中 Fork 會迅速腐敗？

維護上游簡體中文（或英文夾雜簡體）開源專案的台灣繁體中文 Fork 時，傳統做法是「在分支上手動改檔案，上游更新時執行 `git merge upstream/main`」。這會導致三個工程災難：

1. **合併衝突（Merge Conflict）隨時間指數累積**：因為全文每一行漢字都被轉為繁體，只要上游改動任何一段文字，`git merge` 或 `git rebase` 就會產生大面積衝突。
2. **OpenCC 二次轉換退化（Second-Pass Degradation）**：當開發者對已經轉過一次繁體的檔案再跑一次 OpenCC（`cn -> tw2`），會發生二次轉換退化（例如：`連接埠` 被二次轉成 `連線埠`、`類型` 疊字變成 `類別型`、`型別` 變成 `型別別`）。
3. **語境多義詞誤傷（Context-Blind Substitution）**：OpenCC 的通用詞庫會把音訊格式的「编码」無腦轉為「寫程式」（變成 `` `其他編碼的 WAV` ``）、把終端機 stdout 的「打印路徑」轉為紙本「列印路徑」、把 Documentation 的「参考文件」轉為檔案系統的 `` `參考文件` ``。

---

## 2. 零漂移自動同步架構（Reset + Regenerate Pipeline）

保哥在 `doggy8088/answer-me-with-html`（`zh-tw` 分支）實作的解法是：**永遠不對上游做 `git merge`，每次同步都從 `upstream/main` 全新重建 `zh-tw` 分支，再透過確定性腳本重新產生繁體中文內容**。

```text
upstream/main (上游最新 Commit SHA)
   │
   ├─► Step 1. 讀取 scripts/zh-tw/.base-sha 比對上游 SHA
   │           └─ 若相同：印出 NOCHANGE 並直接結束（0 成本）
   │
   ├─► Step 2. 備份本地專屬資產至暫存區 ($TMP)
   │           ├─ scripts/zh-tw/ (轉換腳本、修補字典、.base-sha)
   │           └─ 已重產生的繁體中文示範圖檔 (若上游生成腳本未變則免重繪)
   │
   ├─► Step 3. 強制重置分支基底：git checkout -B zh-tw upstream/main
   │           └─ 徹底消除 merge commit 髒歷史與雙向衝突
   │
   ├─► Step 4. 還原 scripts/zh-tw/ 並執行兩階段繁中轉換
   │           ├─ Stage A：OpenCC (cn -> tw2) 基礎簡轉繁
   │           └─ Stage B：套用台灣技術詞庫與二次退化修補字典 (vocab)
   │
   ├─► Step 5. 雙重冪等與建置驗證閘門 (Gate Check)
   │           ├─ 執行建置腳本（如重編譯內嵌模板 bundle）
   │           ├─ 執行 check（驗證再跑一次轉換 diff 為 0，且無簡體殘留）
   │           └─ 執行專案單元測試
   │
   └─► Step 6. 寫入新 .base-sha、單一 Commit 提交、git push --force-with-lease origin zh-tw
```

---

## 3. 兩階段轉換與 OpenCC 二次退化修補規格

本 repo 已將此字典與檢查邏輯實作於 [`tools/verify_zhtw_vocab.py`](../tools/verify_zhtw_vocab.py)。核心規則分為兩層：

### 3.1 第一層：OpenCC 二次轉換退化修補（Second-Pass Guard）

| 退化詞（誤轉結果） | 修正結果（台灣正體） | 成因與防禦說明 |
| :--- | :--- | :--- |
| `連線埠` | `連接埠` | OpenCC `cn -> tw2` 將「端口」轉為「連接埠」後，若跑第二次會把「连接」轉「連線」而退化成 `` `連接埠` `` |
| `隻影響` | `只影響` | 副詞「只」（僅）在特定斷詞下被誤轉為量詞「隻」 |
| `選一個類別型` | `選一個類型` | 「類別」與「類型」規則重疊造成疊字退化 |
| `型別別` | `型別` | 「类型 -> 型別」二次套用造成字尾重複 |
| `字面量（Literal）（Literal）` | `字面量（Literal）` | 括號英文補充說明在多次執行時重複附加 |
| `瞭什麼` | `了什麼` | 語尾助詞「了」在「什麼」前被誤判為動詞「明瞭」的「瞭」 |

### 3.2 第二層：語境多義詞與兩岸慣用動詞修補

| 原始／誤轉詞彙 | 修正結果（台灣慣用） | 語境說明 |
| :--- | :--- | :--- |
| `其他寫程式的 WAV` / `自己寫程式並下載` | `其他編碼的 WAV` / `自己編碼並下載` | 簡體「编码」在音訊／資料格式語境指 Encoding（編碼），而非 Coding（寫程式） |
| `渲染時會打印` / `並打印路徑` | `渲染時會輸出` / `並輸出路徑` | CLI 終端機 stdout 輸出在簡體常寫「打印」，台灣技術語境應稱「輸出」（紙本才用「列印」） |
| `參考檔案` | `參考文件` | 全域將簡體「文件（file）」轉為「檔案」後，屬於 Documentation 的 `` `參考文件` `` 需精準還原為「參考文件」 |
| `摁下` | `按下` | 按鈕操作動詞統一使用台灣慣用「按下」，禁用大陸北方方言 `` `按下` `` |

---

## 4. 本機檢查與驗證指令

對任何 Markdown 文件或繁體中文化產物執行靜態檢查與冪等性驗證：

```powershell
# 1. 驗證詞庫與退化修補規則的嚴格冪等性（跑兩次結果完全一致）
python tools/verify_zhtw_vocab.py --verify-idempotent

# 2. 掃描目標目錄或檔案是否殘留 OpenCC 退化詞或禁用詞（自動略過程式碼區塊與行內反引號反例）
python tools/verify_zhtw_vocab.py --check notes docs templates README.md

# 3. 就地修補目標檔案中的退化詞
python tools/verify_zhtw_vocab.py --fix <path/to/file.md>
```
