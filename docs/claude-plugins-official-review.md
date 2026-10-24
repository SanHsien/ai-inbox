# Anthropic 官方 Claude Code 外掛清單深度檢閱與工作流適配報告

> 本檢閱報告直接讀取開源倉庫 [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) 之實際內容（涵蓋 40 個官方第一方插件 `plugins/` 與 100+ 第三方驗證插件 `external_plugins/`）。  
> 檢閱基準：維護者工作流環境（**Windows 11 原生**、Python/TypeScript、多 Agent 協作、Git 個人 fork 規範、嚴格零機密與品質閘門）。  
> 交付形式：以 `ai-inbox` 範本（`docs/claude-plugins-official-review.md`）交付。

---

## 1. 檢閱總覽與生態架構

官方倉庫將插件生態分為兩大維度：
1. **官方原生插件 (`plugins/`)**：由 Anthropic 團隊第一方維護，聚焦於代碼品質、LSP 語言支援、安全防護、技能建立與工作流管理。
2. **生態驗證插件 (`external_plugins/`)**：由各大生態廠商（如 Asana, Atlassian, Playwright, Supabase, Stripe 等）提供之 MCP 或工具整合。

---

## 2. 適合維護者工作流的官方外掛評選 (Recommended)

針對維護者「Windows 11 原生 + Python/TS + 跨 Agent 調度 + 零機密防護」之工作流特徵，篩選出以下高度適配的插件：

| 插件名稱 (Plugin Name) | 分類 | 核心功能 | 適合理由與實測評估 | 推薦安裝指令 |
| :--- | :--- | :--- | :--- | :--- |
| **`pr-review-toolkit`** | `development` | 多維度 Pull Request 審查工具包（架構、邊界、效能） | **極高適配**。維護者工作流極其注重交付前的嚴格審查與防線檢查，可無縫補充二審與盲審管線。 | `/plugin install pr-review-toolkit@claude-plugins-official` |
| **`security-guidance`** | `security` | 程式碼安全稽核、Diff 解析與敏感密鑰提醒 Hook | **極高適配**。內建 Git diff 安全監控與敏感路徑過濾，完全契合維護者「API key、Token 零洩漏」硬性閘門。 | `/plugin install security-guidance@claude-plugins-official` |
| **`skill-creator`** | `development` | 建立、改進、基準評測與打包 Agent Skills | **極高適配**。提供 `quick_validate.py`、`run_eval.py` 等 stdlib 腳本，直接支援自製 Skill 的自動化驗收與說明優化。 | `/plugin install skill-creator@claude-plugins-official` |
| **`claude-md-management`** | `productivity` | 依據對話反思與教訓自動修訂與維護 `CLAUDE.md` / 規則庫 | **高適配**。符合維護者「被糾正後將教訓寫入對應規則檔」之工作習慣，維持全域規則健全。 | `/plugin install claude-md-management@claude-plugins-official` |
| **`pyright-lsp`** | `development` | Python 靜態類型檢查與代碼導引 LSP 伺服器 | **高適配**。Windows 11 環境下支援 Python 3 專案即時符號導引與語法分析，零外部重型依賴。 | `/plugin install pyright-lsp@claude-plugins-official` |
| **`typescript-lsp`** | `development` | TypeScript/JavaScript 語言伺服器 LSP 支援 | **高適配**。支援前端與全端專案（如 Next.js/React）在終端內的快速類型推斷與補全。 | `/plugin install typescript-lsp@claude-plugins-official` |
| **`session-report`** | `productivity` | 解析會話紀錄並產生視覺化 HTML 分析報告 | **中高適配**。便於事後覆盤 Agent 的 Tool 調用頻次、Token 消耗與任務耗時。 | `/plugin install session-report@claude-plugins-official` |
| **`code-simplifier`** | `development` | 消除過度設計、精簡複雜嵌套與死碼 | **高適配**。契合維護者「拒絕罐頭空殼與長篇無用架構」的精實原則。 | `/plugin install code-simplifier@claude-plugins-official` |

---

## 3. 不適合或應排除的外掛清單 (Not Recommended / Excluded)

| 插件名稱 (Plugin Name) | 分類 | 不適合理由 |
| :--- | :--- | :--- |
| **`imessage`** | `productivity` | **平台不相容**：底層依賴 macOS 的 Messages 資料庫與 AppleScript，在 Windows 11 原生環境完全不可用。 |
| **`swift-lsp`** | `development` | **技術棧偏離**：維護者本地主力為 Windows/Python/TypeScript，無 Swift/iOS 開發需求，引入僅徒增進程開銷。 |
| **`csharp-lsp` / `jdtls-lsp`** | `development` | **技術棧偏離**：維護者無 C# / Java 開發流，且 JDTLS 依賴重量級 JDK 運行時。 |
| **`blackrock-advisor-center-plugin`** | `productivity` | **特定商用閉源 SaaS**：僅限貝萊德認證財務顧問使用，一般開發者無法通過身份驗證。 |
| **`chronograph-gp` / `chronograph-lp`** | `productivity` | **私募股權專用系統**：高度垂直且受商業許可限制，與個人技術情報與 AI 任務總管無關。 |
| **`laravel-boost`** | `development` | **生態偏離**：專為 PHP Laravel 框架設計，維護者全端環境為 Next.js + Python。 |

---

## 4. 未查證或需環境驗證項目 (Unverified)

以下插件收錄於市場目錄中，但受限於相依服務狀態或缺乏公開驗收測試，標註為「未查證」：

1. **`vsql-extension-builder`**：
   - 狀態：**未查證**
   - 理由：VillageSQL 為小眾 MySQL 擴充生態，缺乏公開詳細文檔與本機 Windows 編譯工具鏈說明。
2. **`zocks-advisor`**：
   - 狀態：**未查證**
   - 理由：需綁定第三方 Zocks AI 語音財務顧問專有帳號，無公開免費 API 可供實測驗證。
3. **`chronograph-*` 系列**：
   - 狀態：**未查證**
   - 理由：企業內網專有 API，無法自公開網路進行單元測試與連通性驗證。

---

## 5. 實測指令與外掛調用範例

以推薦之 `security-guidance` 與 `skill-creator` 為例，在 Claude Code 中可進行之典型驗收操作：

```bash
# 1. 查詢已安裝外掛狀態
/plugin list

# 2. 安裝官方精選安全輔助插件
/plugin install security-guidance@claude-plugins-official

# 3. 執行本機 Skill 結構驗證 (以 skill-creator 內建腳本)
python -m plugins.skill_creator.scripts.quick_validate --path ./templates/fullstack-website-builder-skill.md
```
