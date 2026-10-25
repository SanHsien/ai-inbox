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
