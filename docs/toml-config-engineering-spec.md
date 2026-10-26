# TOML v1.0 vs v1.1 規格差異與 AI Agent 設定檔工程指引

> 查證日期：2026-10-26。對應任務 `T-20261026-04`；配套工具見 `tools/toml_validator.py`（`T-20261026-05`）。
> 來源筆記：`notes/2026-10-26-toml-v11-specification-and-config-engineering.md`。
> 本文所有 Python 輸出都是 2026-10-26 在本機 `%TEMP%\tomlspec` 實際執行的結果（Python 3.14.9 與 3.11.15、PyYAML 6.0.3）。

## 1. 結論

- TOML 1.1.0 **已正式發布**：官方 `CHANGELOG.md` 標 `1.1.0 / 2025-12-18`，GitHub Release `1.1.0` 發布時間 `2025-12-24`（`gh api repos/toml-lang/toml/releases`）。
- Python 內建 `tomllib` **3.11 加入、只支援 TOML 1.0.0**；官方文件稱 **3.15 起支援 1.1.0**（[docs.python.org/3/library/tomllib.html](https://docs.python.org/3/library/tomllib.html)）。
  本機 3.11.15 與 3.14.9 實測都拒絕 1.1 語法（第 3 節）。本機沒有 3.15，**3.15 的行為未實測**。
- 要寫給「各種 Python 版本都能讀」的設定檔，**用 1.0 語法**。1.1 語法只在確定所有讀取端都支援時才用。

## 2. v1.0 與 v1.1 差異

來源：官方 [`CHANGELOG.md`](https://github.com/toml-lang/toml/blob/main/CHANGELOG.md) 的 1.1.0 段、[Release 1.1.0](https://github.com/toml-lang/toml/releases/tag/1.1.0)。

| 項目 | v1.0.0 | v1.1.0 | 官方 PR |
|------|--------|--------|---------|
| 內嵌表格 `{ }` | 必須單行、不可有尾隨逗號 | 可跨行、可有尾隨逗號 | #904 |
| 基本字串 `\xHH` | 無 | 新增，碼位 ≤ 255 | #796 |
| 基本字串 `\e` | 無 | 新增（ESC，0x1B） | #790 |
| 日期時間／時間的秒 | 必填 | 可省略（`14:15`） | #894 |

另有數項只是澄清文字（注釋不影響產出的表格、點號鍵定義表格的方式、次毫秒精度允許等），不改變語法。

### 筆記與官方不一致的地方（已更正）

來源筆記寫「v1.1 放寬無引號鍵可用 Unicode 非 ASCII 字符（`名稱 = "測試"`）」。
**官方 1.1.0 規格不是這樣**：tag `1.1.0` 的 `toml.md` 仍寫「Bare keys may only contain ASCII letters, ASCII digits, underscores, and dashes」，CHANGELOG 的 1.1.0 段也沒有這一項。
實測也一致：`名稱 = "測試"` 在本機 tomllib 報 `Invalid statement`，要寫成 `"名稱" = "測試"`。中文鍵一律加引號。
（筆記資料來源是第三方繁中譯本，是否譯者另有說明未查證。）

## 3. 實測：本機 `tomllib` 對 1.0／1.1 語法

測試腳本 `demo.py`（節錄，完整程式為每行呼叫 `tomllib.loads` 並印出結果或 `TOMLDecodeError`）：

```text
python 3.14.9
[OK ] v1.0 inline table single line: {'a': {'x': 1, 'y': 2}}
[ERR] v1.1 inline table multiline+trailing comma: Invalid initial character for a key part (at line 1, column 6)
[ERR] v1.1 \e escape: Unescaped '\' in a string (at line 1, column 8)
[ERR] v1.1 \x41 escape: Unescaped '\' in a string (at line 1, column 8)
[ERR] v1.1 time without seconds: Expected newline or end of document after a statement (at line 1, column 6)
[ERR] v1.1 datetime without seconds: Expected newline or end of document after a statement (at line 1, column 15)
[OK ] quoted CJK key (v1.0 ok): {'名稱': '測試'}
[ERR] bare CJK key: Invalid statement (at line 1, column 1)
[OK ] Windows path, literal string: {'p': 'C:\\GitHub\\ai-inbox'}
[ERR] Windows path, basic string (wrong): Unescaped '\' in a string (at line 1, column 10)
[OK ] string NO stays string: {'country': 'NO'}
[ERR] bare NO invalid: Invalid value (at line 1, column 11)
[ERR] duplicate key: Cannot overwrite a value (at end of document)
[OK ] multiline literal: {'prompt': 'line1\n  C:\\dir\n'}
```

3.11.15 對前 7 列的結果相同（四項 1.1 語法同樣失敗）。

## 4. YAML 陷阱 vs TOML

YAML 欄位為 PyYAML 6.0.3（YAML 1.1 解析器）`safe_load` 的實測；不同 YAML 函式庫（例如 YAML 1.2 實作）結果可能不同。

輸入 `t.yaml`：

```yaml
country: NO
answer: yes
ver: 3.10
zip: 0123
t: 12:30:00
```

實測輸出：

```text
PyYAML 6.0.3
{'country': False, 'answer': True, 'ver': 3.1, 'zip': 83, 't': 45000}
縮排錯誤: while parsing a block mapping
```

| 陷阱 | YAML（PyYAML 實測） | TOML（tomllib 實測） |
|------|--------------------|---------------------|
| Norway：`NO`、`yes` | 變成 `False`、`True` | `"NO"` 一定是字串；裸 `NO` 直接報 `Invalid value` |
| 版本號 `3.10` | 變成浮點 `3.1` | **同樣變成 `3.1`**（TOML 浮點也吃掉尾端 0），必須寫 `"3.10"` |
| 前導 0 `0123` | 當八進位變 `83` | TOML 不允許前導 0 的整數，直接報錯（規格規定；本文未另行實測） |
| 時間 `12:30:00` | 變成整數 `45000`（YAML 1.1 六十進位） | 這是 TOML 的 Local Time 型別，不會變整數 |
| 縮排錯誤 | 縮排不齊就 `ScannerError` | 縮排無語意；結構靠 `[表格]` 標頭 |
| 重複鍵 | PyYAML 預設後者覆蓋前者（本文未實測，不作斷言） | **報錯** `Cannot overwrite a value` |
| Windows 路徑 | 引號內會跳脫（未實測） | 字面字串 `'C:\GitHub\ai-inbox'` 免跳脫；寫成雙引號直接報錯 |
| 多行 Prompt | `\|`、`>`、`\|-` 等符號各有不同換行語意 | `'''...'''` 所見即所得 |

重點：**TOML 沒有解決版本號被當浮點的問題**，這是此文件與來源筆記最大的差別；`tools/toml_validator.py` 的 `float-version` 檢查就是為這個陷阱而設。

## 5. Python 實務範例（已實際執行）

### 5.1 `tomllib`（唯讀、標準庫）

`agent.toml`：

```toml
# Agent 設定
name = "reviewer"
timeout = 30
workdir = 'C:\GitHub\ai-inbox'   # 字面字串：反斜線不用跳脫
prompt = '''
你是審查員。
路徑 C:\temp\new 不需要轉義。
'''

[limits]
max_tokens = 8000
price = 0.10

[[tools]]
id = "grep"

[[tools]]
id = "read"
```

`ex.py`：

```python
import tomllib
from decimal import Decimal
from pathlib import Path

with open("agent.toml", "rb") as f:          # 必須用二進位模式
    cfg = tomllib.load(f)
print(cfg["workdir"])
print(repr(cfg["prompt"]))
print(cfg["limits"], [t["id"] for t in cfg["tools"]])

exact = tomllib.loads(Path("agent.toml").read_text(encoding="utf-8"), parse_float=Decimal)
print(repr(exact["limits"]["price"]))

try:
    with open("agent.toml", "r", encoding="utf-8") as f:
        tomllib.load(f)
except TypeError as e:
    print("文字模式:", e)
```

實測輸出（Python 3.14.9，`PYTHONUTF8=1 python ex.py`）：

```text
C:\GitHub\ai-inbox
'你是審查員。\n路徑 C:\\temp\\new 不需要轉義。\n'
{'max_tokens': 8000, 'price': 0.1} ['grep', 'read']
Decimal('0.10')
文字模式: File must be opened in binary mode, e.g. use `open('foo.toml', 'rb')`
```

要點：用 `"rb"` 開檔；金額等不能有浮點誤差的欄位用 `parse_float=Decimal`；`tomllib` **只能讀，不能寫**。

### 5.2 `tomlkit`（保留註解與排版的讀寫）

PyPI 最新版 0.15.2、需 Python ≥ 3.9（`pypi.org/pypi/tomlkit/json`，2026-10-26 查）。本機**未安裝**，以下範例**未實際執行**；寫入前請先在你的環境跑一次。
`tomlkit` 是否支援 TOML 1.1 語法：**未查證**。

```python
import tomlkit

doc = tomlkit.parse(open("agent.toml", encoding="utf-8").read())
doc["timeout"] = 60                      # 改值，保留其他行的註解與排版
open("agent.toml", "w", encoding="utf-8").write(tomlkit.dumps(doc))
```

選擇：只讀用 `tomllib`；程式要回寫使用者手寫的設定檔且不能弄丟註解，才用 `tomlkit`。

## 6. AI Agent 設定檔工程指引

1. **語法取 1.0 的交集**：多行內嵌表格改寫成 `[table]` 或單行；ESC 用 `"\u001b"`；時間不省略秒。
2. **Windows 路徑與多行 Prompt 用字面字串** `'...'`／`'''...'''`；內容含單引號 `'` 時才改用基本字串並跳脫。
3. **中文鍵加引號**：`"名稱" = ...`。
4. **版本號、郵遞區號等「長得像數字的字串」一律加引號**。
5. **讀入後立即驗證**：解析成功不代表欄位齊全。用 `tools/toml_validator.py` 檢查語法與必填鍵。
6. **Windows 編輯器存檔注意 BOM**：`tomllib` 拒絕 BOM，驗證器的 `bom` 檢查會直接指出。

## 7. 對應 `tools/toml_validator.py` 的檢查

| 本文陷阱 | 驗證器檢查碼 | 嚴重度 |
|---------|-------------|-------|
| 語法錯誤、重複鍵、重複表格、雙引號裡的 Windows 路徑、裸 `NO`、中文裸鍵 | `parse` | error |
| 本機是 1.0 解析器卻用了 1.1 語法 | `parse`（附提示） | warning |
| `3.10` 變 `3.1` | `float-version` | warning |
| BOM、非 UTF-8 | `bom`、`encoding` | error |
| `enabled = "false"` 型別錯 | `required`（`--require x.enabled:bool`） | error |
| `[project]` 缺 `name`／`version` | `pep621`（`--profile pep621`） | error |

```text
python tools/toml_validator.py . --profile pep621 --require project.name:str
```

## 8. 未查證項目

- Python 3.15 `tomllib` 的實際行為（本機無 3.15）。
- `tomlkit` 的 1.1 支援與第 5.2 節範例的執行結果。
- 第三方繁中譯本（`toml.gh.miniasp.com`）關於 Unicode 裸鍵的說法來源。
