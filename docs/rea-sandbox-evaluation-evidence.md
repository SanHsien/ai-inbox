# REA（Reverse Engineer Anything）沙盒環境實測報告

> 本報告記錄在 Windows 11 沙盒環境（`C:\GitHub\_sandbox\rea\`）下，對 `SanHsien/rea`（來源 URL: `https://github.com/SanHsien/rea`，上游 URL: `https://github.com/morluto/rea`）及 REA 工具鏈（實測版本 v6.7.0，發布於 2026-10-18；2026-10-30 重驗，來源 URL: `https://www.npmjs.com/package/rea-agents` 與 `https://registry.npmjs.org/rea-agents`，最新版本已發布 v6.8.0 於 2026-10-25）進行之實測驗證。  
> 依據維護者安全邊界決策：  
> 1. 允許在沙盒目錄下載可攜版 JDK 21 與 Ghidra 官方發行版（不寫入系統登錄檔、不更動系統 PATH、僅於進程內透過環境變數傳入路徑）；  
> 2. 嚴格禁止執行改寫正式 Agent 配置的 `npx rea-agents setup`，改為在沙盒環境手動啟動 MCP Server 並透過協議驗證；  
> 3. 解包出的應用程式原始碼留存於隔離沙盒暫存區，嚴禁 commit 進入任何 Git 倉庫。

---

## 1. DoD 1：可攜式依賴下載與雜湊比對驗證

在下載前嚴格核對官方來源，並以 SHA-256 演算法逐字節比對官方公布之 Checksum：

### 1.1 Adoptium Eclipse Temurin JDK 21（可攜版）
- **官方下載來源**：`https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_windows_hotspot_21.0.12.1_1.zip`
- **檔案名稱**：`OpenJDK21U-jdk_x64_windows_hotspot_21.0.12.1_1.zip`（195.6 MB，精確大小 205,073,461 位元組；2026-10-30 重驗，來源 URL: `https://api.github.com/repos/adoptium/temurin21-binaries/releases/tags/jdk-21.0.12.1%2B1`）
- **官方公布 SHA-256**：`f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e`（2026-10-30 重驗，來源 URL: `https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_windows_hotspot_21.0.12.1_1.zip.sha256.txt` 與 [`Release jdk-21.0.12.1+1`](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1)）
- **本地下載計算 SHA-256**：`f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e`
- **雜湊比對結果**：`MATCH`（完全一致）
- **執行期驗證**：
  ```text
  C:\GitHub\_sandbox\rea\jdk-21\jdk-21.0.12.1+1\bin\java.exe -version
  openjdk version "21.0.12.1" 2026-08-18 LTS
  OpenJDK Runtime Environment Temurin-21.0.12.1+1 (build 21.0.12.1+1-LTS)
  OpenJDK 64-Bit Server VM Temurin-21.0.12.1+1 (build 21.0.12.1+1-LTS, mixed mode, sharing)
  ```

### 1.2 NSA Ghidra 12.2 Public Build
- **官方下載來源**：`https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.2_build/ghidra_12.2_PUBLIC_20261016.zip`
- **檔案名稱**：`ghidra_12.2_PUBLIC_20261016.zip`（543.3 MB，精確大小 569,712,708 位元組；2026-10-30 重驗，來源 URL: `https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/tags/Ghidra_12.2_build`）
- **官方公布 SHA-256**：`2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67`（2026-10-30 重驗，來源 URL: [`Release Ghidra_12.2_build`](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.2_build) 官方 Release 內文標註）
- **本地下載計算 SHA-256**：`2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67`
- **雜湊比對結果**：`MATCH`（完全一致）
- **解包驗證**：成功解壓至 `C:\GitHub\_sandbox\rea\ghidra\ghidra_12.2_PUBLIC`，核心無頭分析腳本 `support\analyzeHeadless.bat` 存在可用。

---

## 2. DoD 2：沙盒環境手動啟動 MCP Server 與工具調用

- **啟動方式**：透過隔離行程傳入沙盒環境變數：
  - `JAVA_HOME=C:\GitHub\_sandbox\rea\jdk-21\jdk-21.0.12.1+1`
  - `GHIDRA_HOME=C:\GitHub\_sandbox\rea\ghidra\ghidra_12.2_PUBLIC`
  - `PATH=C:\GitHub\_sandbox\rea\jdk-21\jdk-21.0.12.1+1\bin;...`
  - 執行指令：`node C:\GitHub\_sandbox\rea\node_modules\rea-agents\scripts\rea.mjs mcp`
- **協議握手（JSON-RPC 2.0 stdio）**：
  - `protocolVersion`: `2024-11-05`
  - `serverInfo`: `{ name: "rea", version: "6.7.0" }`
  - `capabilities`: 支援 tools、completions、prompts
- **工具清單列舉（`tools/list`）**：
  - 註冊工具總數：**207 個 MCP 工具**（另含 6 個 MCP Prompts、153 個 CLI 子命令）
  - 涵蓋範圍：原生二進位分析（Ghidra/Hopper/IDA 橋接）、JavaScript 靜態分析與 ASAR 解包、CDP 瀏覽器觀測、Android APK JADX 反編譯、Evidence 證據導出等。
- **工具調用驗證（`tools/call`）**：
  - 調用工具：`binary_session`
  - 執行結果：成功回傳伺服器標識、SDK 版本（`2.3.1`）、目錄摘要 SHA-256（`96d8f6e6ea1b...`）與可用分析能力。

---

## 3. DoD 3：Electron 應用 ASAR 解包與 JS 靜態分析

選定本機已安裝之真實 Electron 應用程式組件進行端到端解包與語意重建分析：

- **目標目標檔案**：`%USERPROFILE%\AppData\Local\Programs\antigravity\resources\app.asar`
- **檔案規格**：4,502,673 位元組（約 4.5 MB）
- **SHA-256 雜湊**：`ad7fb1a177a11522490cba910c0970a117bec568cd9ad85233fa62873361ed05`

### 3.1 安全解包（`extract-artifact`）
- **證據代碼**：`ev_e8c652f24eefc20f879d1e994f07f2b0b073bfa54bd3fe979d2048b4f10a8046`
- **解包統計**：
  - 圖節點數（`node_count`）：**1,221**
  - 實例出現數（`occurrence_count`）：**1,251**
  - 關係邊數（`edge_count`）：**1,250**
  - 包含模組：`dist/main.js`、`dist/languageServer.js`、`package.json` 及完整 `node_modules` 依賴樹。
- **原始碼隔離政策**：解包檔案僅存放於沙盒暫存區（`%TEMP%\rea-extracted-*`），分析後自動清理，未寫入任何 Git 倉庫。

### 3.2 靜態 JavaScript 應用分析（`analyze-javascript-application`）
- **證據代碼**：`ev_10c1ef8f86e60435e68f690c26361265dc02eaa45faca351ffe2168950a7fc69`
- **分析範圍**：完成全部 **778 個 JavaScript 原始碼模組** 之 AST 解析與資料流追蹤。
- **生成圖譜**：
  - `JavaScriptApplicationGraph`：構建模組匯入匯出、Electron 主進程與渲染進程邊界關係。
  - `JavaScriptSemanticGraph`：靜態綁定語意閉包、Promise 異步流與物件屬性槽（Property Slots）。

---

## 4. DoD 4：CDP 觀測模式公開網站 API 攔截實測

- **觀測標的**：公開測試網站 `https://jsonplaceholder.typicode.com/`（完全免登入、無身分憑證）。
- **觀測架構**：啟動獨立無頭 Chrome 實例（`--remote-debugging-port=9222 --headless=new`），使用隨機全新臨時使用者目錄，透過 Chrome DevTools Protocol（CDP）WebSocket 連線啟用 `Network.enable` 與 `Page.enable`。
- **攔截結果**：成功捕捉 **6 個公開 API 請求**（滿足 $\ge 5$ 個之要求）：
  
  | 序號 | 主機（Host） | 路徑（Path） | HTTP 狀態碼 | 媒體類型（MIME Type） |
  | :--- | :--- | :--- | :--- | :--- |
  | 1 | `jsonplaceholder.typicode.com` | `/albums/1` | `200 OK` | `application/json` |
  | 2 | `jsonplaceholder.typicode.com` | `/comments/1` | `200 OK` | `application/json` |
  | 3 | `jsonplaceholder.typicode.com` | `/todos/1` | `200 OK` | `application/json` |
  | 4 | `jsonplaceholder.typicode.com` | `/photos/1` | `200 OK` | `application/json` |
  | 5 | `jsonplaceholder.typicode.com` | `/posts/1` | `200 OK` | `application/json` |
  | 6 | `jsonplaceholder.typicode.com` | `/posts/2` | `200 OK` | `application/json` |

- **安全合規防線**：
  - 嚴格遵守零憑證原則：日誌僅記錄請求路徑、狀態碼與 MIME 類型；
  - 嚴禁記錄 Cookie、Authorization 標頭、Token 或回應內容（Response Body）；
  - 測試結束後立即銷毀無頭 Chrome 行程與暫存目錄。

---

## 5. 沙盒空間與環境清潔度審查

- **沙盒目錄**：`C:\GitHub\_sandbox\rea\`
- **總佔用空間**：約 **2,192 MB**（包含 Adoptium JDK 21 可攜壓縮包與目錄、Ghidra 12.2 壓縮包與目錄、隔離之 node_modules）。
- **系統影響**：
  - 全域登錄檔：零變更。
  - 系統環境變數 PATH：零變更。
  - 正式 Agent 設定（Claude Code / Codex / Cursor / Antigravity）：完全未改寫（未執行 `npx rea-agents setup`）。
