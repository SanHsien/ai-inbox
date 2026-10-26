# REA + CLI-Anything 逆向分析與功能重造流水線規格 (Reverse Engineering Pipeline Spec)

> 本規格文件收錄於 `docs/reverse-engineering-pipeline-spec.md`，定義 Coding Agent 協同調用本地逆向工具鏈（REA 與 CLI-Anything），實現從「觀測行為 → 理解結構 → 重造功能」的端到端自動化工作流。以 ai-inbox 範本形式交付。

---

## 1. 架構概述與工具矩陣

現代軟體分析面臨兩大挑戰：封閉應用的黑箱行為難以捉摸，以及傳統 GUI 點擊觀測的不可靠性。本流水線結合香港大學的 `CLI-Anything` 與開源逆向 MCP `morluto/rea`，打造「證據驅動」的 Agent-Native 逆向分析架構。

### 1.1 工具責任矩陣與架構決策

| 工具組件 | 角色與責任邊界 | 採用狀態 | 決策理由與輸入輸出契約 |
| :--- | :--- | :--- | :--- |
| **CLI-Anything** | **行為探針與驅動層**<br>動態參數探測、命令樹建立、CLI Harness 生成 | **核心採用** | 提供確定性 CLI 輸入與 stdout `--json` 捕獲，取代脆弱的視覺點擊。<br>輸出：`execution_trace.json`、CLI Command Schema。 |
| **REA (morluto/rea)** | **結構理解與逆向核心**<br>Chrome CDP 網路觀測、ASAR 解包、JS AST 審查、Ghidra/JADX 反編譯 | **核心採用** | 透過 MCP 提供開箱即用的跨平台靜態與動態逆向工具鏈。<br>輸出：`decompiled_source/`、API 協議分析報告、函數呼叫圖。 |
| **desktop-sense** | **本機螢幕截圖與 OCR 視覺感知** | **【選用、未採用】** | **未採用理由**：<br>1. **隱私與安全防線**：全域截圖容易在公開對話或日誌中洩漏桌面機密與個人隱私；<br>2. **效率低下**：多模態截圖 Token 消耗巨大且有坐標抖動；<br>3. **替代方案成熟**：REA 之 CDP 模式與 CLI-Anything 結構化 stdout 已能 100% 覆蓋行為觀測需求，無需依賴視覺點擊。 |

---

## 2. 三階段流水線運作模型 (Pipeline Lifecycle)

```text
[階段一：行為觀測]             [階段二：結構逆向]              [階段三：無菌重造]
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│  CLI-Anything    │          │    REA MCP       │          │  Cleanroom Spec  │
│  動態參數探測     │ ──Trace─▶│  ASAR/CDP/AST   │ ──Specs─▶│  Agent-Native    │
│  捕獲 Exit Code   │          │  提取核心演算法  │          │  重造乾淨實作     │
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

### 階段一：動態行為觀測 (Behavior Observation)
1. **目標啟動**：透過 CDP（Chrome DevTools Protocol）或原生子進程啟動目標應用。
2. **通訊攔截**：監聽 Network Request/Response，自動過濾掉靜態資源（css/png），鎖定核心 REST / RPC / WebSocket 封包。
3. **邊界探測**：傳入極值與異常參數，記錄目標軟體的 Exit Code 與錯誤提示。

### 階段二：結構反編譯與靜態分析 (Structural Decompilation)
1. **多目標自動路由**：
   - 若為 **Electron 應用**：調用 REA 之 `asar_extract` 解包 `app.asar`，提取前端 JS/TS bundle。
   - 若為 **網頁/前端應用**：調用 REA 之 `js_beautify` 與 AST 分析器，恢復變數符號並找出核心邏輯入口。
   - 若為 **Android APK / 原生二進位**：自動路由至 JADX / Ghidra 執行反編譯，搜尋加密金鑰或編解碼演算法。
2. **證據提煉 (Evidence Extraction)**：
   - 提取資料結構定義（Schema）、封包加解密演算法（Hashing / HMAC）、核心計算邏輯。

### 階段三：無菌室乾淨重造 (Cleanroom Re-implementation)
1. **防版權污染**：僅參考逆向提煉出的「規格定義（Functional Spec）」與「I/O 契約」，不複製任何反編譯程式碼。
2. **Agent-Native 生成**：由 Agent 以現代標準技術（Python stdlib、TypeScript）重新實作核心演算法，並封裝為具備 `--json` 輸出的 CLI 或標準 Skill。

---

## 3. 端到端實戰範例：Electron 跨平台多媒體轉換器逆向與重造

以下示範如何使用本流水線分析某封閉 Electron 轉檔軟體之私有運算演算法：

### 步驟 1：行為觀測 (CLI-Anything 探針)
```bash
# 透過 CLI-Anything 探針觸發目標軟體之轉檔指令並捕獲輸出
cli-anything probe --target "./legacy-converter.exe" --input "sample.mp4" --args "--preset=fast"
# 產出：發現其背後呼叫私有演算法對音軌注入特定水印元數據
```

### 步驟 2：結構逆向 (REA MCP 解包)
Agent 透過 MCP 調用 REA 工具：
```json
// REA MCP Request
{
  "tool": "rea_unpack_asar",
  "arguments": {
    "archive_path": "./resources/app.asar",
    "output_dir": "./artifacts/unpacked_app"
  }
}
```
隨後在 `unpacked_app/dist/main.js` 透過 AST 搜尋，發現私有音訊水印生成函式：
```javascript
// 反編譯提煉出的演算法邏輯（證據）：
// 水印為 SHA-256(timestamp + salt) 的前 8 bytes 注入 ID3 tag
```

### 步驟 3：無菌室重造 (Cleanroom Re-creation)
Agent 完全不引用原始二進位，直接使用 Python stdlib 寫出標準 CLI 工具 `tools/media_watermark.py`（示意檔名，本 repo 並未收錄此工具）：
```python
import hashlib
import time

def generate_watermark(salt: str) -> str:
    """依據逆向提取之規格乾淨重造演算法"""
    payload = f"{int(time.time())}_{salt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
```
最後依據 `docs/cli-anything-to-skill-protocol.md` 自動生成相應的 `SKILL.md`，完成從黑箱到 Agent-Native 工具的完整閉環。

---

## 4. 法律與道德合規宣告

- 本流水線規格僅限用於**自有軟體安全性審計**、**開源專案技術學習**、**協定互通性研究（Interoperability）**及**合法除錯**。
- 嚴禁利用此流水線規避數位版權保護機制（DRM）或破解未經授權之商業機密軟體。

---

## 5. 合規防線與拒答處理規範

> 來源：`notes/2026-10-19-rea-reverse-engineer-anything-agent.md` 第 2.3 節的實務心得（作者宣稱）。任務原稱此節為「審查避障」；本文件的立場是：**用準確、可查證的用途宣告取得雲端模型的協助；被拒答就停手，不換說法試探、不靠改寫繞過安全對齊。** 理由見 5.2。

### 5.1 動手前的閘門（全部成立才進入雲端分析）

| # | 檢查項 | 不成立時 |
| :--- | :--- | :--- |
| G1 | 目標是**自有軟體**、有**書面授權**的客戶軟體，或為**協定互通性**（見 5.4）所需 | 停止，不上傳任何位元組 |
| G2 | 目的是靜態分析、Call Graph、重建功能規格與資料格式；**不是**取得序號、略過授權／試用／DRM 檢查 | 停止 |
| G3 | 已記錄 `authorization_ref`（合約編號、自有 repo、授權信 ID） | 補齊再開始 |
| G4 | 上傳雲端的內容已評估：不含客戶機密、個資、憑證（遵守 `AGENTS.md` 第 4 節） | 只上傳必要的函式片段，不傳整檔 |
| G5 | 產出只留規格與 I/O 契約，不入庫反編譯程式碼與修補後的二進位 | 依第 2 節階段三 |

### 5.2 為什麼不教「避障」

- 筆記提到的有效做法，本質是**把真實用途與限制講清楚**（靜態分析、重建功能與資料格式、不用原版程式碼、不商用、不做違法用途）。這是準確宣告，不是話術；宣告內容必須與事實一致，G1～G5 就是讓它成立的條件。
- 宣告不實、或宣告為真但被拒答後反覆改寫試探，等於把安全對齊當作要繞過的對象。本流水線的處理是：**拒答一次就記錄，改走非模型路徑**（人工使用 Ghidra／JADX 閱讀、補充授權證明後由人決定是否重試），不做第二種措辭。
- 以「本地未審查模型」執行修補，**不改變行為的合法性**：責任閘門在 5.5 的契約驗證器與 G1～G5，不在模型有沒有拒答機制。

### 5.3 Clean Room 合規宣告 Prompt 範本

用於對雲端模型發起靜態分析。`{{ }}` 為必填欄位，缺任何一項不得送出。

```text
【用途與授權宣告】
我正在對 {{目標名稱與版本}} 進行 {{自有軟體安全審計 | 已授權的客戶軟體除錯 | 協定互通性研究}}。
授權依據：{{authorization_ref，例如合約編號或自有 repo}}。
本次僅做「靜態分析」，採 Clean Room 原則：
 - 目的是理解功能並重建「功能規格」與「資料格式」，之後由另一個不接觸原始程式碼的實作者獨立重寫；
 - 不會複製或散布原版程式碼或二進位，不做商業轉售，不用於略過授權、試用限制、DRM 或任何違法用途。

【請你做】
1. 就我貼上的組合語言片段 {{函式名稱或位址範圍}}，說明該函式的輸入、輸出與副作用。
2. 列出 Call Graph（呼叫者／被呼叫者、呼叫位址），註明哪些是推測。
3. 重建所處理的資料結構欄位（偏移、型別、長度），註明信心程度。
4. 每一項結論附上對應的位址或指令作為證據；無法確定的寫「未能確定」。

【請你不要做】
- 不要輸出可直接用於略過授權檢查或啟用驗證的修補建議；若你判斷這份分析的用途不符合上述宣告，請直接說明並停止。

【輸出格式】
JSON，符合第 5.5 節的 re_handoff.v1（findings 欄位）；無法填的欄位留空字串。
```

使用規則：
1. 宣告必須是真的；欄位由人填寫，不由 Agent 自動補齊「授權依據」。
2. 模型回答拒絕或要求更多說明時，補**事實**（授權文件、目的），不補話術；補完仍拒絕就停止。
3. 範本中「請你不要做」那段不可刪除；它讓模型與日後審查者看到限制是雙向的。

### 5.4 法律背景（一般性說明，非法律意見）

以下僅為方便查找的出處清單，各法域的要件與例外不同，實際案件請洽律師。

| 法域 | 內容（摘要） | 出處 |
| :--- | :--- | :--- |
| 歐盟 | 軟體指令 2009/24/EC 第 6 條：在取得互通性資訊所必需時，取得合法使用權的人可進行還原（decompilation）；官方文字列有三項累積條件（合法使用者、資訊先前不易取得、僅限互通所需部分），另對取得資訊的用途設有限制。第 6(2) 款細節本次未取得官方全文，**未查證** | [legislation.gov.uk 第 6 條](https://www.legislation.gov.uk/eudr/2009/24/article/6)（2026-10-26 查證第 6(1) 款）；官方全文請另查 EUR-Lex |
| 美國 | 17 U.S.C. §1201(a)(1)(A) 禁止規避控制存取的技術措施；§1201(f) 為互通性逆向的有限例外，要求合法持有程式副本、僅為取得獨立程式互通所需且先前不易取得的元素 | [Cornell LII 17 USC 1201](https://www.law.cornell.edu/uscode/text/17/1201)（2026-10-26 查證） |
| 台灣 | 著作權法第 80 條之 2 規範「防盜拷措施」的規避與相關設備提供；第 3 項有例外、第 4 項授權主管機關訂定例外認定要點。現行條文與要點**本次未能從全國法規資料庫取得，未查證** | 次級來源：[智慧局文件](https://www.tipo.gov.tw/wSite/public/Attachment/0/f1747972069582.pdf)；請自行核對 [全國法規資料庫](https://law.moj.gov.tw/) |

要點：
- Clean Room 是一種**降低侵權風險的作法**（分析團隊產規格、實作團隊不接觸原碼），**不是法定的安全港**；契約條款（EULA 禁止逆向）也可能另有拘束力，本表未涵蓋。
- 規避 DRM／授權機制，即使目的是互通，各法域例外都很窄；本流水線一律列為 G2 不通過。

### 5.5 雲地雙軌管線與資料介接契約

```text
 [人]  填寫 authorization_ref、purpose，檢查 G1~G5
   │
   ▼
┌───────────────────────────────┐   片段（最小必要）   ┌──────────────────────────────┐
│ 地端：REA / Ghidra / JADX     │ ───────────────────▶ │ 雲端 LLM（靜態分析）          │
│ 取得 Assembly、位址、位元組   │                      │ 5.3 Prompt                   │
└───────────────────────────────┘ ◀─────────────────── │ 輸出 re_handoff.v1 findings  │
        ▲                          findings JSON       │  ・Assembly 說明、呼叫位址    │
        │                                              │  ・TfmRegKey（見下方說明）    │
        │                                              │  ・Patch 檔案偏移量           │
        │                                              └───────────────┬──────────────┘
        │                                                              │ re_handoff.v1
        │                                                              ▼
        │                                              ┌──────────────────────────────┐
        │                                              │ 契約驗證器 check_handoff.py   │
        │                                              │ （閘門：不過就不進地端）      │
        │                                              └───────────────┬──────────────┘
        │                                                              │ 通過
        │            result JSON（套用結果、位元組）                    ▼
        └────────────────────────────────────────────  ┌──────────────────────────────┐
                                                       │ 地端執行：本地模型／二進位工具 │
                                                       │ 在「副本」上做位元修補與動態除錯│
                                                       └──────────────────────────────┘
```

**雲端 → 地端 `re_handoff.v1`**

| 欄位 | 型別 | 說明 |
| :--- | :--- | :--- |
| `schema` | string | 固定 `re_handoff.v1` |
| `purpose` | enum | `interoperability`／`own-software-bugfix`／`security-audit-authorized` |
| `authorization_ref` | string | 必填；人填，Agent 不得自行產生 |
| `target.sha256` | string(64) | 目標檔雜湊，地端套用前先比對 |
| `findings[]` | array | `function`、`va`（位址）、`asm_note`、`confidence`、`evidence` |
| `registry_keys[]` | array | 分析中看到的登錄機碼名稱（筆記所稱 `TfmRegKey` 即屬此類；該名稱的含義**未查證**，本文件只當成字串欄位） |
| `patches[]` | array | `id`、`file_offset`(int)、`original_bytes`、`new_bytes`、`reason` |

**地端 → 雲端 result**：`patch_id`、`applied`(bool)、`post_bytes`、`test_log_ref`（日誌路徑，不貼機密）。

**地端執行規則**
1. 只改**副本**；套用前比對 `target.sha256` 與 `file_offset` 處的 `original_bytes`，不一致就中止。
2. `original_bytes` 與 `new_bytes` 長度必須相同；修補前備份。
3. `reason` 涉及授權、序號、啟用、試用、DRM 的 patch 由驗證器拒絕（驗證器為關鍵字**黑名單輔助**，不能取代 G2 的人工判斷）。
4. 修補後的二進位與反編譯輸出不入庫（沿用 `docs/rea-sandbox-evaluation-evidence.md` 的隔離政策）。

**驗證器範例與實測輸出**（2026-10-26，Python 3.14，純 stdlib，內容為本節規則的最小實作；`check_handoff.py` 並未收錄於本 repo `tools/`，需要時可自行存檔）：

```python
import json, sys
ALLOWED = {"interoperability", "own-software-bugfix", "security-audit-authorized"}
BANNED = ("license", "licence", "serial", "activation", "trial", "drm", "授權", "序號", "啟用", "試用")
def check(h):
    e = []
    if h.get("schema") != "re_handoff.v1": e.append("schema must be re_handoff.v1")
    if h.get("purpose") not in ALLOWED: e.append("purpose not in allowlist")
    if not h.get("authorization_ref"): e.append("authorization_ref required")
    if len(str(h.get("target", {}).get("sha256", ""))) != 64: e.append("target.sha256 must be 64 hex chars")
    for p in h.get("patches", []):
        if len(p.get("original_bytes", "")) != len(p.get("new_bytes", "x")): e.append(f"{p.get('id')}: byte length mismatch")
        if any(b in p.get("reason", "").lower() for b in BANNED): e.append(f"{p.get('id')}: reason touches licensing/DRM -> reject")
        if not isinstance(p.get("file_offset"), int): e.append(f"{p.get('id')}: file_offset must be int")
    return e
if __name__ == "__main__":
    errs = check(json.load(open(sys.argv[1], encoding="utf-8")))
    print("\n".join(errs) or "OK"); sys.exit(1 if errs else 0)
```

```text
$ python check_handoff.py good.json        # 自有 build 修正反向分支
OK
exit=0
$ python check_handoff.py bad.json         # 無授權、雜湊錯、長度不符、reason 為略過授權檢查
authorization_ref required
target.sha256 must be 64 hex chars
P1: byte length mismatch
P1: reason touches licensing/DRM -> reject
exit=1
```

### 5.6 未查證與限制

- 「合規宣告能提高雲端模型配合度」是筆記作者的實務經驗，**未獨立重現**；本文件未對任何模型做拒答率測試。
- 筆記所述模型（GPT-4o／Claude 3.7）為作者提及的版本，本文件不依賴特定模型。
- 歐盟第 6(2) 款與台灣第 80 條之 2 現行條文見 5.4 說明，未取得官方全文。
