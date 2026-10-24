# Agent-Native CLI 封裝與自動生成 Skill 標準協議 (CLI-Anything to Skill Protocol)

> 本協議文件收錄於 `docs/cli-anything-to-skill-protocol.md`，定義將 CLI-Anything 生成的 7-Stage CLI Harness 自動轉換為 Antigravity 與 Claude Code 相容之 `SKILL.md` 的標準規範與安全防護準則。以 ai-inbox 範本形式交付。

---

## 1. 背景與設計哲學

傳統 GUI-based Computer Use 面臨截圖延遲高、坐標偏移、解析度差異與不可確定性等多重痛點。香港大學（HKUDS）提出的 **CLI-Anything** 框架倡導「Agent-Native Computer Use」：透過靜態代碼分析、動態追蹤與 7-Stage 生成流水線，將任意既有軟體或函式庫封裝為具備嚴格 `--json` 輸出、清楚 Command Tree 與明確 Exit Code 的 CLI Harness。

本協議旨在串接 CLI-Anything 的輸出層與現代 Coding Agent（如 Antigravity、Claude Code）的擴充生態（Skills 體系），建立雙向對齊的自動化標準，使生成的 CLI 能被 Agent 零摩擦、高可靠地調用。

---

## 2. 映射架構 (CLI Schema to SKILL.md)

CLI-Anything 產出的 CLI 中繼描述檔（通常為 JSON Schema 或 CLI Command Tree）必須依以下規則映射至 `SKILL.md`：

### 2.1 Metadata 映射
| CLI Schema 欄位 | SKILL.md 映射位置 | 轉換規則 |
| :--- | :--- | :--- |
| `name` | YAML frontmatter: `name` | 保持 kebab-case，例如 `cli-video-editor` |
| `summary` / `description` | YAML frontmatter: `description` | 簡明扼要，強調該 CLI 能完成的目標 |
| `intent_keywords` | YAML frontmatter: `triggers` | 提取觸發自然語言關鍵字清單 |
| `version` | 內文 `## 1. 工具資訊` | 記錄版本號與依賴要求 |

### 2.2 命令樹與參數映射 (Command Tree & Flags)
1. **指令分組 (Subcommand Routing)**：
   - 一級指令（如 `cli-tool export`）映射為 Skill 的獨立操作步驟或工作流章節。
   - 二級指令若超過 5 個，需在 Skill 中建立「快速查表（Quick Reference Table）」，列出語法、關鍵參數與使用情境。
2. **參數規格化 (Arguments & Options)**：
   - 所有的非互動式調用必須包含 `--json` 參數，以便 Agent 透過 stdout 直接解析 JSON 回傳。
   - 布林 Flag 必須提供清楚的預設值（Default: `false` / `true`）。
   - 檔案輸入路徑必須聲明絕對路徑或工作目錄相對路徑規範。

### 2.3 結束碼與錯誤分類 (Exit Code Mapping)
Agent 必須依據回傳的 Exit Code 採取不同決策：
- `0`: **成功 (Success)**。stdout 保證為標準 JSON，包含 `status: "ok"` 與操作 payload。
- `1`: **使用者/參數錯誤 (Invalid Usage)**。Agent 需自我檢視指令列參數格式，重新生成正確語法，不得無效重試。
- `2`: **執行階段受阻 (Runtime Exception)**。資源鎖定、網路中斷或依賴遺失，需在 log 中提取原因。
- `126` / `127`: **命令不可執行或未安裝**。Agent 應提示維護者檢查本機 PATH 或先決環境。

---

## 3. 全域安全防線條款 (Blast Radius Guardrails)

自動將任意軟體封裝為 CLI 時，可能暴露高危操作（例如刪除檔案、清空資料表、強行終止進程）。在產生 `SKILL.md` 時，轉換器**必須強制注入安全防護區塊**：

1. **破壞性操作隔離（Destructive Operations Confirmation Gate）**：
   - 凡涉及 `delete`、`drop`、`purge`、`format`、`overwrite`、`kill`、`truncate` 等指令或 `--force`、`--all` 參數，在 Skill 中必須標註：
     ```markdown
     > [!CAUTION] 高危破壞性指令
     > 本操作具備破壞性（Blast Radius: High），Agent 嚴禁自主執行，必須先明確向使用者列出受影響路徑並取得確認。
     ```
2. **零機密原則（Zero Secrets in CLI Arguments）**：
   - 嚴禁在指令列參數中明文傳遞 Token、密碼或私鑰（例如 `--token <SECRET>`）。
   - 轉換器必須將認證參數改寫為環境變數讀取模式（例如讀取 `TOOL_API_KEY`），並在 Skill 中指明安全設定指引。
3. **路徑越界防禦（Path Traversal Prevention）**：
   - 檔案讀寫操作限定於專案工作區目錄內，禁止解析指向全域敏感路徑（如使用者家目錄金鑰、Windows System32）的操作。

---

## 4. 自動化轉換腳本規範 (`tools/cli_to_skill.py`)

為了讓轉換流程完全機械化與可測試，維護者於 `tools/cli_to_skill.py` 實作標準轉換器，其輸入輸出定義如下：

### 4.1 輸入 Schema 格式 (CLI Definition JSON)
```json
{
  "name": "media-processor",
  "version": "1.2.0",
  "description": "本地多媒體無損壓縮與格式轉換工具",
  "triggers": ["影片轉檔", "音訊壓縮", "media-processor"],
  "commands": [
    {
      "name": "compress",
      "description": "壓縮指定影片至目標位元率",
      "destructive": false,
      "args": [
        {"name": "--input", "required": true, "type": "string", "help": "輸入影片路徑"},
        {"name": "--output", "required": true, "type": "string", "help": "輸出影片路徑"},
        {"name": "--bitrate", "required": false, "type": "string", "default": "2500k", "help": "目標位元率"}
      ]
    },
    {
      "name": "purge-cache",
      "description": "清空轉檔暫存快取目錄",
      "destructive": true,
      "args": [
        {"name": "--all", "required": false, "type": "boolean", "default": false, "help": "強制清空所有快取"}
      ]
    }
  ]
}
```

### 4.2 轉換輸出產物
轉換腳本將自動生成符合 YAML frontmatter 與 Markdown 結構的標準 `SKILL.md`，並在具備破壞性之指令標題下方自動插入警戒提示。
