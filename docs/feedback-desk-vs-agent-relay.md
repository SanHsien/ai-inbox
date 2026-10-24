# feedback-desk 與 agent-relay 多 Agent 協作機制對照分析（T-20261024-04）

## 1. 評估背景與目標
依據任務 `T-20261024-04`，針對開源專案 `feedback-desk`（Cloudflare Workers 版工單系統）與本地多 Agent 通訊協定 `agent-relay`（基於 Git Mailbox 與 Worktree 的非同步派工規格）進行多維度架構對照。
本次比對旨在分析兩者在協作流程、狀態追蹤、權限隔離與人機邊界上的異同，列出本地協作體系可借鏡強化與明確不採納之項目，避免盲目導入外部雲端相依。

## 2. 核心機制多維度對照表

| 維度 | feedback-desk 機制 | agent-relay 現況 | 判斷 | 理由 |
| :--- | :--- | :--- | :--- | :--- |
| **狀態機** | 採工單生命週期三態：`open`（處理中）→ `review`（待審核）→ `closed`（已完成）。AI 完成修改後填寫調整說明並切換至 `review`，經客戶審核後結案。 | 採 Maildir 形式信箱目錄原子改名狀態機：`new → cur → done`。派工回信結構化記錄 `status`（`ok` / `failed` / `timeout` / `refused` / `error` / `interrupted`）與驗收閘門日誌 `gate.status`。 | 已有 | agent-relay 的 Maildir 狀態轉移具備檔案系統原子性與跨機器 Git 合併無衝突特性，派工回信狀態定義已充分涵蓋自動化排程與中斷補救，無需退化為簡化的工單三態。 |
| **認領** | 支援工單層級之 `claim` 與 `release` 指令。紀錄當前認領之開發者或 AI 工具，防止多個 AI 同時重複處理同次回報單。 | 採信箱單一擁有者原則（收件信箱專屬搬移）＋ SPEC 第 9 節檔案級簽出鎖（Check-out Lock，`claims/<repo key>/<claim id>.json`）。派工時要求宣告 `dispatch.paths`，重疊即阻擋。 | 已有 | agent-relay 不僅在信件層級實現單收件人認領，更進一步在程式碼層次提供嚴密的路徑碰撞檢查（保守重疊判斷），安全防禦粒度高於 feedback-desk 的工單層級標記。 |
| **交接紀錄** | 工單頂部提供專屬交接留言區塊（`handoff` 子命令），下一個接手的工程師或 AI 讀單時能優先載入前任留下的調整脈絡與指示。 | SPEC 第 8 節規範交接資料包（Hand-over bundle，`relay context`），自動彙整 `HANDOFF.md`、Obsidian 筆記、`.claude/handoffs/*.md` 門鈴交接卡、前一會話尾部摘要與 git 狀態，並在 dispatch 時注入工人 prompt。 | 已有 | agent-relay 已實現自動化交接包提取與門鈴卡機制，並包含字數上限截斷與嚴格的 Token 遮罩處理，比依賴手動寫入工單留言更具系統整合性與資安防護力。 |
| **動作署名（帳號＋AI 工具）** | 每筆留言、狀態切換與交接紀錄均強制記錄「帳號＋AI 工具」複合身分（例如「王小明（Codex）」、「李大華（Claude Code）」），由環境變數 `FEEDBACK_DESK_AGENT` 或 MCP 來源解析。 | 信封欄位記錄 `from`（信箱名，如 `commander`）、`host`（主機名）、`dispatch.runtime`（`claude`、`codex`、`agy`、`hermes`），並於回信附帶 `result.runtime` 與 Ed25519 簽章，但尚未對一般手動回信提供固定格式的「維護者＋AI 工具」署名標記。 | 缺少 | 在多終端、多模型交互對話場景下，明確在動作日誌或信件摘要註明「維護者帳號（特定 AI Runtime）」能大幅提升稽核歷史與除錯追蹤的清晰度，此命名慣例值得納入信封擴充參考。 |
| **人工確認閘門** | 人工驗收閉環：AI 僅能推進工單至「待審核（review）」，必須由外部客戶或專案負責人登入 Web 介面核可後方能變更為「已完成（closed）」。 | 實體隔離閘門：派工工人僅能在獨立 git worktree（`relay/<id>` 分支）修改檔案，預設剝離 shell 執行權限且不具備 push / commit 主分支能力；成果由維護者收信檢閱 `diff --stat` 與測試結果後，手動決定是否合併。 | 已有 | agent-relay 在作業系統與版本控制層實施物理隔離，維護者的合併審查權限構成最高等級的安全確認閘門，防禦強度顯著超越 Web 前端的按鈕狀態切換。 |
| **客戶可見範圍** | 多專案租戶隔離，提供專屬客戶開單與追蹤入口，隔離內部敏感討論，客戶僅能瀏覽與開立自身專案工單並上傳截圖。 | 專注於本地與內網各 Agent 間之點對點非同步通訊，儲存層為私人 Git 儲存庫的孤兒分支，無公開 Web UI，無客戶身分管理模組。 | 不需要 | 本地協作環境屬於個人與內部多 Agent 協同開發，目前無對外接案或開放客戶直接操作之業務需求；維持無對外暴露介面能完全杜絕外部攻擊面，不應引入多餘的客戶端系統。 |
| **通訊與儲存傳輸架構** | 依賴 Cloudflare Workers + D1 (SQLite) + R2 物件儲存，需公網域名、Cloudflare 帳號與 API 憑證，透過 HTTP REST / MCP 伺服器進行雲端通訊。 | 依賴本機檔案系統與 Git 孤兒分支（Mailbox 分支），無對外開放 Port、免公網 IP、免第三方雲端資料庫，透過標準 Git push/pull 與原生檔案鎖達成非同步同步。 | 不需要 | 本地以 Git 為底層之傳輸架構具備天然的版本控制、離線可用性與零第三方依賴，無需承擔雲端平台（如 Zeabur 或 Cloudflare）之連線中斷或外洩風險。 |
| **機密邊界與 Token 防護** | 透過 `mcp install` 簽發個別 Bearer Token 存於本地設定檔，CLI 提示要求 AI 不看密碼，但在雲端 Worker 端仍需維護帳號密碼與全域 `APP_SECRET`。 | SPEC 第 1 節與第 8 節明訂機密過濾規則，信件與交接包自動遮罩 Token 形狀（如 `sk-`、`ghp_` 等），採用 Ed25519 非對稱簽章驗證寄件者，任何 Token 與金鑰不進信件、不進 Git 歷史。 | 已有 | agent-relay 採零憑證進儲存庫與非對稱金鑰簽章機制，架構設計上嚴格落實防禦性機密邊界。 |

## 3. 採納建議與架構結論

1. **借鏡採納項**：
   - **動作署名標準化**：在 `agent-relay` 的信件通訊與各類 handoff 門鈴通知中，可參考 feedback-desk 的「`帳號（AI 工具）`」呈現模式（例如在通知 Toast 或交接卡標註 `maintainer (claude-code)`），讓維護者一眼識別本次操作由哪位模型或環境發起。
2. **暫不採納項**：
   - **客戶入口與外部 Web 託管**：無接案客戶場景下，不增加 Cloudflare Workers / D1 / R2 的外部雲端相依，恪守本地原生與私有儲存優先原則。
   - **簡化三態工單取代 Maildir**：Maildir 的目錄轉移與原子寫入為分散式防衝突基石，不因前端直觀性而退化底層通訊架構。
