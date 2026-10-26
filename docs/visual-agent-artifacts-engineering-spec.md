# AI Agent 視覺化工件輸出規範與 Token 節流工程指引

> 對應任務：`T-20261026-06`（來源筆記：[answer-me-with-html 深度評估](../notes/2026-10-26-answer-me-with-html-visual-agent-artifacts.md)）。
> 參考實作：本 repo 的 [`tools/render_artifact_html.py`](../tools/render_artifact_html.py)（`T-20261026-07`）。
> 查證日期：2026-10-26。

## 0. 一頁結論

- 作法：Agent 只寫一份短的「語意草稿（Draft）」，版面、配色、連線、互動腳本由本機確定性渲染器產生。
- 實測（本文第 5 節，同一份內容、位元組與估算 token）：草稿比「手寫精簡 HTML」小約 3.4～3.9 倍，比「手寫帶完整樣式與互動的 HTML」小約 7.4～8.9 倍。**8 倍成立的前提是對照組要寫完整樣式**；對照組寫極簡樣式時只有約 3.5 倍。
- 上游專案自己宣稱 8 倍（9 頁平均 4,893 → 612 輸出 token），這是作者宣稱；本文沒有重跑它的 benchmark（第 5.4 節）。
- 只有「需要結構化視覺」的回答才用工件；一兩句話能答完的不要用。

## 1. 手寫 HTML/SVG 的三大痛點

| 痛點 | 機制 | 後果 | 本文可驗證的部分 |
|---|---|---|---|
| Token 暴增 | 模型要逐字輸出 CSS、標籤、屬性、腳本 | 同樣內容輸出量是草稿的數倍 | 第 5 節實測 |
| 生成延遲 | 輸出 token 是序列生成，量大就慢 | 等待時間隨輸出量線性增加 | 上游宣稱 31 s → 12 s（作者宣稱，未重跑）；本機渲染一次約 0.2 ms（第 5.3 節） |
| 座標空間幻覺 | 模型沒有排版引擎，`cx`、`cy`、`path` 靠「猜」 | 文字重疊、箭頭錯位、內容溢出 | 結構性原因：草稿不含座標，所以不會出現這類錯誤 |

補充：生成延遲的實測受模型與供應商影響大，本文只量測本機渲染端，不量模型端。

## 2. 架構原理：語意草稿與確定性渲染分離

```text
 使用者提問
     │
     ▼
 ┌───────────┐  只輸出語意（內容、結構、選項）
 │ AI Agent  │──────────────────────────┐
 └───────────┘                          ▼
                                 ┌───────────────┐
                                 │ Draft（.md）  │  可審查、可 diff、可重跑
                                 └───────┬───────┘
                                         ▼ python tools/render_artifact_html.py
                                 ┌───────────────────────────┐
                                 │ 確定性渲染器              │
                                 │ 解析 → 跳脫 → 套版 → 嵌入 │  同輸入 = 同位元組輸出
                                 └───────┬───────────────────┘
                                         ▼
                                 ┌─────────────────────────┐
                                 │ 單檔 HTML（無外部資源） │
                                 └───────┬─────────────────┘
                                         ▼ 使用者在瀏覽器勾選
                                 ┌─────────────────────────┐
                                 │ 「複製決策回饋」字串    │──▶ 貼回 Agent 對話
                                 └─────────────────────────┘
```

分工原則：

| 層 | 負責 | 不負責 |
|---|---|---|
| Agent | 內容是否正確、結構如何分段、要問使用者什麼 | 顏色、間距、座標、腳本 |
| 渲染器 | 版面、樣式、跳脫、互動腳本 | 判斷內容對不對 |
| 使用者 | 閱讀、勾選決策 | 修 HTML |

## 3. Draft 語法規格（v1，本 repo 實作）

> 這是本 repo 自訂的最小子集，**靈感來自**上游 `QingYunA/answer-me-with-html` 的「frontmatter + 帶標籤圍欄區塊」做法（上游 README 列出 `flow`、`tree`、`sequence`、`timeline`、`chart`、`callout`、`ask`、`kv` 等元件）。本 repo 只實作下表的元件，語法與上游**不保證相容**。

### 3.1 文件結構

| 元素 | 語法 | 渲染 |
|---|---|---|
| 前置資料 | 檔首 `---` 區塊，目前只用 `title: ...` | `<title>` 與頁面 `<h1>` |
| 標題 | `#`、`##`、`###` | `<h1>`～`<h3>`（沒寫 `title` 時，用第一個標題當頁籤標題） |
| 段落 | 連續文字行，空行分段 | `<p>` |
| 行內 | `` `程式` ``、`**粗體**` | `<code>`、`<strong>` |
| 清單 | `- ` 或 `* `；`1. ` | `<ul>`、`<ol>` |
| 程式碼 | 三個反引號 + 語言名 | `<pre><code>`，內容一律當純文字 |
| 表格 | 表頭列、`\|---\|---\|` 分隔列、資料列 | `<table>`；儲存格 `ok`／`no`／`warn` 轉成 ✓／✗／! 並上色 |

不支援且**刻意不做**：連結 `[x](url)`、圖片、原始 HTML。原因是這三者是注入面（`javascript:` URL、事件屬性）；需要連結時請把網址寫成純文字。

### 3.2 元件區塊（帶標籤的圍欄）

| 區塊 | 開頭 | 內文 | 渲染 |
|---|---|---|---|
| 流程 | `flow LR` 或 `flow TB` | 每行一條鏈：`A -> B -> C` | 方塊加箭頭；排版由 CSS flex 決定，沒有座標 |
| 提示 | `callout info`、`warn`、`ok` 或 `no` | 一段文字 | 左邊框著色的提示框；未知種類退回 `info` |
| 問題 | `ask <id>` | 第 1 行問題；之後每行 `- 選項`；問題結尾加 `(single)` 表示單選 | 核取方塊（預設複選）或單選鈕；頁面出現任何 `ask` 就會加上底部「複製決策回饋」列 |

以上開頭都接在三個反引號之後（見 3.4 的範例）。`ask` 的 `<id>` 只保留英數、底線、連字號；其餘字元會被濾掉。沒給 id 時依出現順序自動編號 `q1`、`q2`。

### 3.3 錯誤處理約定

| 情況 | 行為 |
|---|---|
| 圍欄沒有結尾 | 吃到檔尾，不丟錯 |
| 未知圍欄語言 | 當一般程式碼，語言名跳脫後顯示 |
| 表格某列欄位不足 | 補空儲存格 |
| CRLF 換行 | 先正規化成 LF，輸出與 LF 輸入相同 |
| frontmatter 沒有結尾 `---` | 視為沒有 frontmatter |

渲染器對任何輸入都不丟例外；寫不對的草稿會被當成一般文字顯示出來，容易在預覽時發現。

### 3.4 範例

下面這份就是第 5 節量測用的草稿（`draft.md`）：

````text
---
title: 快取策略選型
---
## 結論
選 **方案 B（Redis）**：延遲最低，營運成本可接受。

## 比較

| 方案 | 延遲 | 成本 | 維運 |
|---|---|---|---|
| A 行程內快取 | ok | ok | warn |
| B Redis | ok | warn | ok |
| C CDN 邊緣快取 | warn | no | ok |

## 資料流

```flow LR
請求 -> 應用程式 -> Redis -> 資料庫
```

```callout warn
Redis 掛掉時必須退回直連資料庫，否則整站不可用。
```

## 範例

```python
cache.set(key, value, ttl=300)
```

## 待你決定

```ask q1
要採用哪個方案？ (single)
- 方案 A
- 方案 B
- 方案 C
```

```ask q2
上線前要補哪些項目？
- 退回直連機制
- 監控告警
- 壓測
```
````

## 4. 受控語言：ASD-STE100 精神的撰寫規則

> ASD-STE100（Simplified Technical English）是航太與國防文件用的受控英文規格。**未查證**：官網 asd-ste100.org 在 2026-10-26 回應 HTTP 403，本節沒有核對現行版本號與規則編號。下列規則依該規格公認的精神，以及上游 README 對檢查項目的描述（過長句、冗詞、被動語態；上游預設只警告）整理，不是逐條引用規格。

規則的目的是讓「下一個讀的 Agent 或人」只有一種讀法。中文草稿套用如下：

| # | 規則 | 不好 | 好 |
|---|---|---|---|
| 1 | 一句一件事；句子長度上限約 25 字（操作步驟 20 字） | 「先備份再更新設定然後重啟服務並確認沒有錯誤」 | 「1. 備份設定。2. 更新設定。3. 重啟服務。4. 確認日誌沒有錯誤。」 |
| 2 | 同一概念永遠用同一個詞 | 「快取」「暫存」「cache」交替出現 | 全文只用「快取」 |
| 3 | 主動語態，主詞明確 | 「設定被更新」 | 「安裝腳本更新設定」 |
| 4 | 用具體數字與條件，不用「適度」「盡量」「可能」 | 「延遲偏高時請調整」 | 「p95 延遲超過 200 ms 時，把 TTL 改為 300 秒」 |
| 5 | 步驟用編號清單，每步一個動作 | 一整段敘述 | `1.` `2.` 清單 |
| 6 | 警告放在對應步驟之前，用 `callout warn` | 警告埋在段落最後 | 步驟前的 `callout warn` |
| 7 | 結論放最前面 | 先講背景再給答案 | 第一段就是結論 |
| 8 | 刪除沒有資訊量的詞（「基本上」「其實」「值得一提的是」） | 「基本上我們其實可以……」 | 「可以……」 |

可機械檢查的子集（長度、被動語態關鍵詞、禁用模糊詞）可以放在渲染前的 lint 步驟，**預設只警告，不擋渲染**。本 repo 的渲染器目前沒有實作這個 lint。

## 5. Token 節流實測

### 5.1 方法與限制

- **對象**：同一份內容（第 3.4 節的草稿；一頁：結論、3x3 比較表、流程、提示、程式碼、兩個決策問題）。
- **對照組**：
  - A：Draft（`draft.md`，即第 3.4 節）。
  - B：手寫精簡 HTML（`handwritten.html`，我手寫的最小版本：極簡 CSS 加一小段互動腳本，無 CSP、無響應式細節；全文見附錄）。
  - C：手寫完整 HTML（`rendered.html`，即本渲染器的輸出：完整深色主題 CSS、四種提示框配色、流程元件樣式、CSP、可複製回饋腳本與底部列）。C 代表「要求模型自己寫出和渲染器同等品質的頁面」。
- **沒有官方 tokenizer**：本環境沒有 `tiktoken`（`import tiktoken` 回 `ModuleNotFoundError`），也沒有 Anthropic tokenizer，所以 token 數是**估算**，不是實測。估算公式寫在腳本裡：CJK 字元每字估 1 token，其餘位元組每 4 位元組估 1 token；另給悲觀情境（CJK 每字 1.5、其餘每 3 位元組）。字元數與位元組數是精確值。
- **限制**：單一樣本、一種內容、不是模型實際輸出的 token。B 是人（我）手寫的，不是模型輸出；模型實際輸出通常更囉嗦。

### 5.2 指令與輸出

產生 C：

```text
python tools/render_artifact_html.py draft.md -o rendered.html
```

計數腳本 `count.py`：

```python
import re,sys,json
def est(s, cjk=1.0, ratio=4):
    cj=len(re.findall(r'[　-〿㐀-鿿＀-￯]',s))
    rest=len(s.encode('utf-8'))-cj*3
    # 其餘位元組(含符號/少量非CJK Unicode)；ASCII 約 4 byte/token
    return round(cj*cjk + rest/ratio)
for f in ['draft.md','handwritten.html','rendered.html']:
    s=open(f,encoding='utf-8').read()
    print(f, 'chars',len(s),'bytes',len(s.encode()),'est_tok(cjk=1,asciiB/4)',est(s),'est_tok(cjk=1.5,asciiB/3)',est(s,1.5,3))
```

輸出（原樣，`python count.py`）：

```text
draft.md chars 461 bytes 703 est_tok(cjk=1,asciiB/4) 206 est_tok(cjk=1.5,asciiB/3) 295
handwritten.html chars 2370 bytes 2758 est_tok(cjk=1,asciiB/4) 736 est_tok(cjk=1.5,asciiB/3) 1012
rendered.html chars 5820 bytes 6258 est_tok(cjk=1,asciiB/4) 1617 est_tok(cjk=1.5,asciiB/3) 2191
```

倍率（對照組 ÷ Draft，四捨五入到小數 1 位）：

| 對照組 | 字元數 | UTF-8 位元組 | 估算 token（基本） | 估算 token（悲觀） |
|---|---|---|---|---|
| B 手寫精簡 HTML | 5.1x | 3.9x | 3.6x | 3.4x |
| C 手寫完整 HTML | 12.6x | 8.9x | 7.9x | 7.4x |

注意：`count.py` 的輸出 `est_tok(cjk=1,asciiB/4)` 為基本估算，`est_tok(cjk=1.5,asciiB/3)` 為悲觀估算。

### 5.3 本機渲染耗時與確定性

同一份草稿在本機（Python 3.14.9，Windows 11）連續呼叫 `render()` 100 次，平均約 0.21 毫秒／次（行程啟動時間不含在內）。同一輸入連跑兩次 CLI，輸出的 MD5 相同（`f0781d51bcf3c660dc6ed9cb676ebd47`），符合確定性。這個值是用第 3.4 節的草稿原文（703 位元組、LF 換行）跑 `python tools/render_artifact_html.py draft.md -o r1.html` 兩次所得（2026-10-26 覆核重算；初版寫的 `193190fd…` 無法重現，已更正）。渲染器或草稿只要改一個字，這個值就會變，用來比對「同一版本是否確定」而不是固定答案。

### 5.4 結論與原文宣稱的對照

| 項目 | 數值 | 來源／狀態 |
|---|---|---|
| 上游 README：9 頁手寫平均 4,893 輸出 token；使用 skill 後平均 612，約 1/8；時間 31 s → 12 s | 8.0x | 作者宣稱。方法是 3 主題 x 3 次取中位數、Claude Sonnet 5.5、一般 Claude Code；token 數放在其 `bench/corpus/tokens.json`。本文**未重跑**。上游同時承認整體成本只降約 15%（每輪仍要讀系統提示與對話）。來源：[github.com/QingYunA/answer-me-with-html](https://github.com/QingYunA/answer-me-with-html)，查證日 2026-10-26 |
| 筆記引用的社群貼文：「4,000+ → 500 以內、省 87%」 | 約 8x | 貼文作者宣稱；87% 與 8x 在算術上一致（1 - 1/8 = 87.5%），未獨立驗證 |
| 本文實測：Draft 對手寫完整 HTML | 7.4～8.9x（位元組與估算 token） | 估算，單一樣本 |
| 本文實測：Draft 對手寫精簡 HTML | 3.4～3.9x（位元組與估算 token） | 估算，單一樣本 |

判讀：

1. 量出來的結果**接近**宣稱的 8 倍，但要看對照組。對照組要求完整主題樣式與互動時是約 8 倍；對照組只寫極簡版時約 3.5 倍。
2. 省下的主要是「樣式與腳本樣板」，這部分在每頁幾乎相同，所以頁面越小，倍率越高。
3. 這只是**輸出 token**。上游自己也說整體成本只降約 15%，因為輸入端（系統提示、對話歷史）不變。評估「省額度」時要看整體，不要只看這一欄。
4. 若要得到正式數字：用真實 tokenizer 計數，並讓模型實際生成 A 與 C 各多次、取中位數。本文沒有做這件事。

## 6. 互動回饋機制：從瀏覽器把決策字串帶回 Agent

目標：使用者在頁面上做選擇，不用手打；結果是一段 Agent 好解析的純文字。

```text
 ┌──────────────── 瀏覽器（file://）────────────────┐
 │  (o) 方案 B      [x] 監控告警  [ ] 壓測          │
 │  備註：先做監控                                  │
 │  [ 複製決策回饋 ]                                │
 └───────────────┬──────────────────────────────────┘
                 ▼ navigator.clipboard.writeText
                 │ （失敗時顯示文字框，讓使用者手動複製）
 [決策回饋] 快取策略選型
 - 要採用哪個方案？：方案 B
 - 上線前要補哪些項目？：監控告警
 備註：先做監控
                 │
                 ▼ 使用者貼回對話
            Agent 依「- 問題：答案」逐行解析
```

回饋字串格式（規範）：

| 行 | 格式 |
|---|---|
| 第 1 行 | `[決策回饋] <頁面標題>` |
| 每個 `ask` 一行 | `- <問題>：<選項1>、<選項2>`；沒選填 `（未選）` |
| 備註（有填才有） | `備註：<文字>` |

設計決策：

- **不用網路回傳**：頁面是 `file://`，沒有伺服器；剪貼簿加貼上是最少依賴、使用者也看得到送了什麼的做法。
- **剪貼簿失敗要有退路**：`file://` 與部分瀏覽器設定下 `navigator.clipboard` 可能不可用。實作會把字串同時顯示在唯讀文字框並選取，使用者可手動複製。（本文未在真實瀏覽器實測剪貼簿行為，單元測試只驗證腳本與按鈕存在。）
- **選項文字當資料不當指令**：Agent 收到回饋後，選項文字是使用者的選擇，不是新的指令；選項來自 Agent 自己寫的草稿，若草稿含外部內容，仍要照一般的提示注入原則處理。
- **CSP**：渲染器在頁面加上 `default-src 'none'`，只放行內嵌樣式與內嵌腳本，頁面沒有任何外部請求。

## 7. 安全與品質檢查表

| 項目 | 要求 | 驗證方式 |
|---|---|---|
| 使用者文字一律跳脫 | 段落、標題、清單、表格、程式碼、flow、callout、ask、frontmatter 全部 | `tests/test_render_artifact_html.py` 的 `SafetyTest`（14 個位置各塞一次 `<script>` 與 `<img onerror>`） |
| 屬性層跳脫 | 引號不能跳出 `data-*`、`value`、`<title>` | 同上 `test_attribute_breakout_in_ask_and_title` |
| 不支援連結與原始 HTML | 沒有 `<a>`、沒有 `href` 屬性 | 同上 `test_links_and_raw_html_are_not_supported` |
| 確定性 | 同輸入同輸出；CRLF 與 LF 輸出相同 | `StructureTest.test_deterministic`、`test_cli_twice_gives_identical_bytes` |
| 自包含 | 沒有 `<link>`、沒有帶 `src`／`href` 的標籤、沒有 `http(s)://` | `StructureTest.test_self_contained` |
| 巢狀完整 | 標籤平衡 | `StructureTest.test_well_formed_nesting` |

驗收指令：

```text
python -m unittest discover -s tests -p "test_render_artifact_html.py"
```

## 8. 何時不要用工件

- 一到三句能答完的問題、單一指令的輸出、純狀態查詢：直接用終端文字。
- 沒有結構（沒有比較、流程、決策）的長文：用一般 Markdown。
- 內容含機密：HTML 是檔案，會留在磁碟；依 [`AGENTS.md`](../AGENTS.md) 的資料規範處理。

## 附錄：量測用「手寫精簡 HTML」全文（B）

```html
<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8"><title>快取策略選型</title>
<style>body{background:#0f1218;color:#e6e9ef;font:16px/1.7 sans-serif;max-width:860px;margin:auto;padding:20px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #2a3242;padding:8px}.ok{color:#4cc38a}.no{color:#f0686b}.warn{color:#e5b34d}.box{background:#171c26;border:1px solid #2a3242;border-radius:8px;padding:6px 12px}.callout{border-left:4px solid #e5b34d;background:#171c26;padding:10px}pre{background:#0b0e14;padding:12px}fieldset{border:1px solid #2a3242;margin:1em 0}</style></head>
<body><h1>快取策略選型</h1>
<h2>結論</h2><p>選 <b>方案 B（Redis）</b>：延遲最低，營運成本可接受。</p>
<h2>比較</h2>
<table><thead><tr><th>方案</th><th>延遲</th><th>成本</th><th>維運</th></tr></thead><tbody>
<tr><td>A 行程內快取</td><td class="ok">✓</td><td class="ok">✓</td><td class="warn">!</td></tr>
<tr><td>B Redis</td><td class="ok">✓</td><td class="warn">!</td><td class="ok">✓</td></tr>
<tr><td>C CDN 邊緣快取</td><td class="warn">!</td><td class="no">✗</td><td class="ok">✓</td></tr>
</tbody></table>
<h2>資料流</h2>
<div style="display:flex;gap:8px;align-items:center"><span class="box">請求</span>→<span class="box">應用程式</span>→<span class="box">Redis</span>→<span class="box">資料庫</span></div>
<div class="callout">Redis 掛掉時必須退回直連資料庫，否則整站不可用。</div>
<h2>範例</h2><pre><code>cache.set(key, value, ttl=300)</code></pre>
<h2>待你決定</h2>
<fieldset data-q="要採用哪個方案？"><legend>要採用哪個方案？</legend>
<label><input type="radio" name="q1" value="方案 A"> 方案 A</label><br><label><input type="radio" name="q1" value="方案 B"> 方案 B</label><br><label><input type="radio" name="q1" value="方案 C"> 方案 C</label></fieldset>
<fieldset data-q="上線前要補哪些項目？"><legend>上線前要補哪些項目？</legend>
<label><input type="checkbox" name="q2" value="退回直連機制"> 退回直連機制</label><br><label><input type="checkbox" name="q2" value="監控告警"> 監控告警</label><br><label><input type="checkbox" name="q2" value="壓測"> 壓測</label></fieldset>
<button id="b">複製決策回饋</button><textarea id="o" readonly></textarea>
<script>document.getElementById('b').onclick=function(){var l=['[決策回饋] 快取策略選型'];document.querySelectorAll('fieldset').forEach(function(f){var p=[];f.querySelectorAll('input:checked').forEach(function(i){p.push(i.value)});l.push('- '+f.dataset.q+'：'+(p.join('、')||'（未選）'))});var t=l.join('\n');o.value=t;navigator.clipboard&&navigator.clipboard.writeText(t)}</script>
</body></html>
```
