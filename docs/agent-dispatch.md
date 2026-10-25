# 跨 Agent 派工與完工回報

> 從 `AGENTS.md` 流程 B 第 4 點搬出（2026-10-25）。內容是四套 Agent 桌面端開新對話、派工與回報的操作指令；`AGENTS.md` 只保留本 repo 的讀寫協定。

## 開啟新 Session 派工注意事項（四大 Agent Desktop 左側欄可視新對話＋自動回報）

- **一、Antigravity Desktop（頂層可視新對話＋`send_message` 回報）**：
  - **同機 Antigravity 內直接呼叫**：呼叫原生 `language_server.exe agentapi new-conversation`（勿透過 `agentapi.bat` 以免 `cmd.exe` 截斷換行），建立 `nestingDepth: 0` 的頂層新對話，立即顯示在 Antigravity Desktop 左側欄：
    ```powershell
    & "$env:LOCALAPPDATA\Programs\Antigravity\resources\bin\language_server.exe" agentapi new-conversation `
      --model=flash `
      --title="[派工] T-YYYYMMDD-XX 任務標題" `
      "<完整派工 Prompt，結尾要求完成後呼叫 send_message 工具（Recipient 填主對話 UUID）回報 Commit SHA 與驗證輸出>"
    ```
    執行後從回傳 JSON 取得 `newConversation.conversationId`，在回覆中提供可點擊連結 `[[派工] T-YYYYMMDD-XX](conversation://<conversationId>)`。
  - **模型梯隊選擇（`--model` 與 Gemini 3.8 Flash）**：
    - CLI 參數僅支援三大梯隊：`--model=<flash_lite|flash|pro>`。
    - 指定 `--model=flash` 時，底層自動調度為 **`gemini-3.8-flash-tiered`**（即 Gemini 3.8 Flash 梯隊）；`--model=flash_lite` 對應 `gemini-3.5-flash-lite`；`--model=pro` 對應 Pro 梯隊。
    - ⚠️ **切勿直接傳入具體思考強度後綴**（例如傳入 `--model=gemini-3.8-flash-high` 會報錯 `no available models found for tier`）；Thinking Level（High / Medium / Low）是 Antigravity Desktop 前端介面專屬配置，CLI 派工時一律使用 `--model=flash`。
  - **完工自動封存（無後續待辦時必做）**：派工新對話在呼叫 `send_message` 回報主對話後，若該新對話已無任何待辦事項，應執行 Connect-RPC `UpdateConversationAnnotations` 將自身標記為封存（務必帶 `mergeAnnotations = $true` 以保留既有標題）：
    ```powershell
    Invoke-RestMethod -Method Post -Uri "http://$env:ANTIGRAVITY_LS_ADDRESS/exa.language_server_pb.LanguageServerService/UpdateConversationAnnotations" -Headers @{ "Connect-Protocol-Version" = "1"; "x-codeium-csrf-token" = $env:ANTIGRAVITY_CSRF_TOKEN } -ContentType "application/json" -Body (@{ cascadeId = $env:ANTIGRAVITY_CONVERSATION_ID; cascadeIds = @($env:ANTIGRAVITY_CONVERSATION_ID); annotations = @{ archived = $true }; mergeAnnotations = $true } | ConvertTo-Json -Depth 5)
    ```
  - **從其他 Agent（Claude / Codex / Hermes）派給 Antigravity Desktop 開頂層新對話**：
    ```powershell
    python -m agent_relay send --to antigravity --kind task --project C:\GitHub\ai-inbox --ref antigravity-session:new --subject "T-YYYYMMDD-XX" --body-file task.md
    ```
    Antigravity sidecar 會自動呼叫 `agentapi new-conversation --title="[Relay] <信件ID>"` 開啟頂層新對話，完工後透過 `agent-relay send --kind result` 回報原寄件端。
- **二、Claude Desktop / Claude Code（`--bg -n` / `--desktop` 可視新會話＋自動回報）**：
  - **關鍵陷阱**：必須在**目標專案根目錄（`C:\GitHub\ai-inbox`）**啟動，不可在 `.relay-worktrees/<id>` 子目錄啟動，否則會話紀錄會歸入 `.relay-worktrees` 資料夾，導致在 Claude Desktop 的 `ai-inbox` 專案下看不到。
  - **啟動與開啟桌面視窗**：
    ```powershell
    Set-Location C:\GitHub\ai-inbox
    # 背景啟動具名會話（回傳 session <id>，寫入 ~/.claude/projects/C--GitHub-ai-inbox/）
    claude --bg -n "[派工] T-YYYYMMDD-XX 任務標題" --permission-mode acceptEdits "<派工 Prompt>"
    # 在 Claude Desktop 桌面視窗直接打開該會話觀看（或直接用 claude --desktop -n "[派工] ..." "<Prompt>" 啟動）
    claude --desktop --resume <id>
    ```
  - **完工自動回報**：在派工 Prompt 結尾要求完工時依發起端執行回報指令（回報 Antigravity：`language_server.exe agentapi send-message <主對話UUID> "<結果>"` 或 `agent-relay send --to antigravity`；回報 Codex：`codex queue --thread <主會話ID> --message "<結果>"`）。
- **三、Codex Desktop / Codex CLI（專案會話＋原生 `codex queue` 跨會話 `send_message`）**：
  - Codex Desktop 與 CLI 共用本機 `app-server` 與 `~/.codex/sessions`（可用 `codex agents` 列出全部活躍會話）。
  - **啟動新會話**：在目標專案根目錄執行 `codex -C C:\GitHub\ai-inbox "<派工 Prompt>"`（或 `codex app C:\GitHub\ai-inbox` 開啟桌面端）。
  - **完工自動回報（Codex 原生 `send_message` 等價指令）**：
    ```powershell
    codex queue -C C:\GitHub\ai-inbox --thread <主會話UUID或名稱> --message "<完工回報與 Commit SHA>"
    ```
- **四、Hermes Desktop / Web Dashboard（`state.db` 具名會話＋自動回報）**：
  - Hermes Desktop（`hermes desktop`）與 Web Dashboard（`hermes dashboard`，port 9119）共用 `%LOCALAPPDATA%\hermes\state.db`。
  - **啟動並命名左側欄會話**：
    ```powershell
    hermes -z "<派工 Prompt>" --in C:\GitHub\ai-inbox --pass-session-id
    hermes sessions rename <session_id> "[派工] T-YYYYMMDD-XX 任務標題"
    ```
  - **完工自動回報**：回報給 Hermes 主會話用 `hermes --resume <主會話ID> -z "<回報內容>" --in C:\GitHub\ai-inbox`（或 `hermes kanban` / `hermes send`）；回報給 Antigravity / Codex 則呼叫 `agentapi send-message` / `codex queue` / `agent-relay send`。
- **五、Antigravity 內部背景子代理（`invoke_subagent`）與 `agent-relay` 無頭 Worktree 工人**：
  - 若不需出現在左側頂層對話欄，可用 `invoke_subagent(TypeName="self")`（內建 `advisor-*-implementer` 僅唯讀）或 `agent-relay dispatch`（在 `.relay-worktrees/<id>` 執行無頭 CLI 並自動跑驗證閘門）。
