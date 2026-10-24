# Claude Code 閒置壓縮（Idle Compaction）Windows 11 本地配置與實測指南

> 本文件收錄於 `docs/claude-idle-compaction-setup.md`，為任務 `T-20261017-27` 針對 Anthropic Claude Code 官方閒置壓縮機制（Idle Compaction）與環境參數 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` 在 Windows 11 原生環境下的最佳實踐配置指南、運作機制剖析與實機驗收紀錄。
> 關聯研究筆記：[`notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md`](../notes/2026-10-17-claude-code-idle-compaction-cc-session-reader.md)。

---

## 1. 機制背景與架構解析

### 1.1 Prompt Cache TTL 與閒置壓縮機制（Idle Compaction）
在長會話開發中，Anthropic 伺服器端的 Prompt Cache 有效時間（TTL）約為 5 分鐘至 1 小時。當開發者在長會話中暫時離開（如會議、用餐或跨日）超過 1 小時，服務端快取將徹底失效。若會話累積至 200k+ tokens，快取過期後的下一條 Prompt 必須重新支付全量 Cache Write 與計算成本，伴隨極高的初字延遲（TTFT）。

為減緩快取失效衝擊，Claude Code 引入了後台 **閒置壓縮（Idle Compaction）**：
- **觸發條件**：在會話閒置約 54 分鐘（快取過期前）且會話累積 Tokens 達到門檻時，後台自動執行 Compact。
- **預設問題**：預設觸發門檻為 `200k` tokens，採「有損壓縮（Lossy Compaction）」，將對話濃縮為抽象摘要，容易丟失中間探索決策、原始提問細節與除錯因果。

### 1.2 最佳實踐配置目標
透過配置 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS=350000`，將觸發門檻提高至 350k：
1. **防止大型連貫專案被過早抽象化**：在 200k~350k 區間內保持完整原始記憶。
2. **與分層記憶體系協同**：
   - 會話內長跑（In-Session）：由 `autocompact 400K` 與結構化記憶管理。
   - 跨會話 / 快取過期（Inter-Session）：若真正需要歷史重建，搭配 `SanHsien/cc-session-reader`（`cc-session inherit`）以靜態 Go 引擎無損抽取對話（過濾 85% 工具雜訊，保留 100% 對話），取代粗暴的有損摘要。

---

## 2. Windows 11 原生配置範例

### 2.1 設定檔路徑
Claude Code 本機設定檔位於使用者目錄：
```text
C:\Users\<Username>\.claude\settings.json
```

### 2.2 `settings.json` 配置方式
在 `~/.claude/settings.json` 中配置 `env` 物件注入環境變數：

```json
{
  "env": {
    "CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS": "350000"
  }
}
```

> **參數說明**：
> - `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`：數值型字串，門檻最低限制為 `100000`（100k），無上限。設為 `350000`（350k）可避免長會話在 200k 時過早進入有損壓縮。
> - 若欲完全停用閒置壓縮，可在 `settings.json` 最外層加上 `"idleCompaction": false`；但在搭配門檻提高至 350k 的策略下，保留預設開啟（`idleCompaction: true`）作為 350k 瀕臨崩潰時的最後防線更具彈性。

### 2.3 PowerShell 環境變數配置（全域 / 使用者層級）
若需在 Windows 11 系統或目前終端機直接生效，可使用下列 PowerShell 指令：

```powershell
# 1. 僅在目前 PowerShell Session 生效
$env:CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS = "350000"

# 2. 寫入 Windows 11 使用者環境變數（跨終端重開永久生效）
[System.Environment]::SetEnvironmentVariable('CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS', '350000', 'User')
```

---

## 3. 觸發條件與生命週期矩陣

| 參數 / 條件 | 官方預設值 | 最佳實踐建議值 | 說明 |
| :--- | :--- | :--- | :--- |
| **最低版本支援** | >= 2.1.299 | **2.1.309+** | 2.1.299 起正式支援 `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` 環境參數 |
| **觸發閒置時間** | ~54 分鐘 | ~54 分鐘 | Prompt Cache 瀕臨 1 小時過期臨界點 |
| **觸發 Token 門檻** | `200000` (200k) | **`350000` (350k)** | 最低可設 100k，設為 350k 延後有損壓縮觸發時機 |
| **退出開關 (`idleCompaction`)** | `true` | 保留預設或 `false` | 設為 `false` 可徹底關閉後台閒置壓縮 |

---

## 4. 本地實測驗證紀錄

本機已於 Windows 11 原生環境完成實測檢查，各項驗證輸出如下：

### 4.1 CLI 版本驗證
執行 `claude --version`：
```text
2.1.309 (Claude Code)
```
- **判定**：版本 `2.1.309` 高於官方要求門檻 `2.1.299`，完整支援 Idle Compaction 參數。

### 4.2 本地 `settings.json` 參數檢驗
安全讀取本機 `~/.claude/settings.json`（已過濾任何機敏憑證與 API Keys）：
```powershell
Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw |
  ConvertFrom-Json |
  Select-Object -Property idleCompaction, @{N='env_CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS';E={$_.env.CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS}}
```

**實機檢驗輸出**：
```text
idleCompaction                          : 
env_CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS : 350000
```
- **判定**：
  - `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` 已成功設定為 `350000`。
  - `idleCompaction` 未顯式設為 `false`，代表保留 Claude Code 預設開啟行為，在累積滿 350k tokens 且閒置逾 54 分鐘時方作為保底機制運作。

---

## 5. 總結與記憶維護流水線

```text
┌────────────────────────────────────────────────────────────────────────┐
│               Windows 11 Claude Code 會話全週期記憶架構                │
└────────────────────────────────────────────────────────────────────────┘

 [會話進行中 (In-Session)]
   │
   ├─► 0 ~ 350k Tokens：保留 100% 原始對話與完整推論上下文（不受預設 200k 閒置壓縮干擾）
   ├─► 超過 350k Tokens 且閒置 54 分鐘：觸發保底 Idle Compaction（摘要壓縮）
   └─► 搭配 claude-mem：由背景 Observer 記錄關鍵技術決策與專案針式記憶

 [會話過期或跨日接手 (Inter-Session)]
   │
   └─► 執行 `cc-session inherit <session-id>`
         └─► Go 引擎 context 外解析原生 transcript.jsonl
         └─► 過濾 85% Bash/Tool Dump 雜訊
         └─► 無損繼承純對話歷史（降至 30k~50k Tokens），徹底避開快取失效與摘要失憶
```
