# Claude 提示檔與 API 相容性唯讀稽核

日期：2026-11-15（Asia/Taipei）；對應 T-20261115-18。執行者：Codex，路由 solo。

**結論：指定三個 checkout 的有界限靜態檢閱，未找到直接呼叫 Anthropic Messages API 的 consumer；不需要為了 Opus 5.5 虛構遷移工作。** relay 的 Claude CLI 委派、第三方 gateway 環境設定及文件範例必須分開看。提示檔有適用範圍與載入條件需要釐清，但本輪不修改規則、hooks、模型路由或 API 程式。

本公開文件撰寫時，DoD 另要求的私有 findings 報告尚未建立；2026-11-15 已於 `SanHsien/agent-assets`（私有）補交 `docs/prompt-api-audit-findings.md`。本公開版只記完成狀態與檢閱邊界，私有 findings 留在私有 repo。私有檢閱只在下文提供抽象摘要，不公開內部檔名清單、程式或規則內容。

## 1. 基準、方法與檢閱邊界

| 對象 | 本輪基準與範圍 | 證據限制 |
| --- | --- | --- |
| 交付 clone | `%USERPROFILE%/codex-work/inbox-t1821`；分支 `worker/t1821`；HEAD `9fe96637a5a187226ced59fab06b1fcb0e4f6543`；起始無檔案變更 | 不 pull、不 claim、不 complete、不 push；ROADMAP 未變更，沒有新增或結案工作 |
| `SanHsien/ai-inbox` 本機來源 | `C:/GitHub/ai-inbox`：根目錄 `AGENTS.md`、`templates/agent-reach/SKILL.md`、`docs/agent-dispatch.md`；32 個非測試程式檔搜尋，對命中處檢閱上下文 | Git HEAD／status 查詢均 exit 128，原因為 dubious ownership；未修改 safe.directory |
| `SanHsien/agent-relay` 本機來源 | `C:/GitHub/agent-relay`：根目錄 `AGENTS.md`、`SPEC.md` 的委派／隔離條款、`dispatch.py` 的 prompt／argv／環境設定、`gitsync.py` 與 `poller.py`；30 個非測試程式檔搜尋 | 同上；未啟動 relay、CLI 工人、同步或排程 |
| `SanHsien/agent-assets`（私有）本機來源 | repo 維護指引、共用規則入口、技能觸發／治理條款，以及發布、漂移檢查的契約與原始碼 | 只作靜態檢閱；不公開私有 findings 明細，不執行私有工具；Git 基準查詢同樣受阻 |

公開兩 repo 的提示檔盤點：ai-inbox 有上述 `AGENTS.md` 及一個技能範本；relay 有根目錄 `AGENTS.md`，另有程式組裝的 worker prompt。排除 Git metadata、歷史 worktree、快取、相依套件與私密原始匯出後，未找到既有 `CLAUDE.md` 或獨立 rules／commands／agents 提示檔；沒有建立新的 CLAUDE.md。私有技能只檢閱相關觸發與治理段落，不宣稱逐字審查全部參考資料。文章筆記、歷史報告及憑證內容不列入完整程式碼稽核。

來源快照以檔案內容補充，**不等於 commit 或遠端一致性證明**：

| 公開來源檔 | SHA-256 |
| --- | --- |
| ai-inbox `AGENTS.md` | `de19bb94df9f48af6902cf804ac459a88d1fd40e7968c53c681e1c8aa0bc787c` |
| ai-inbox `templates/agent-reach/SKILL.md` | `2e7a915ecf22dab4a7b6ef2e5b167e1f1ae55c457063fa22c5b2ea48947f9d68` |
| relay `pyproject.toml` | `d72ff5aff7336b67d5455ec01167d2a507f477d48a2a4fc72d14074e17a43c44` |

> 2026-11-17 註：`templates/agent-reach/SKILL.md` 在本稽核之後於第 28 行後加了一段「會複製 Chrome 登入狀態」的使用前警示，檔案雜湊因此與上表不同；上表是稽核當時的快照，第 2 節引用的第 4、8、28 行位置不變。

搜尋線索包括 provider 名稱、Messages 建立／串流、API endpoint、thinking／tool choice／工具版本；逐處區分執行程式、偵測字串、文件與範例。這不是完整資料流分析，也無法排除動態產生 endpoint、未納入檔案、外部 CLI 或 gateway 內部的 API 呼叫。以下 GitHub 連結是公開來源定位；行號以本機本輪內容為準，未確認遠端 main 相同。

## 2. 提示檔 findings 與分類

| 分類 | 位置／發現 | 建議與適用條件 |
| --- | --- | --- |
| 已確認的治理範圍衝突風險 | ai-inbox [`templates/agent-reach/SKILL.md:4`](https://github.com/SanHsien/ai-inbox/blob/main/templates/agent-reach/SKILL.md#L4)、`:8`、`:28` 對任何網路查詢／URL 宣告 MUST USE；`:39–43` 又擴張到多平台蒐集與版本檢查 | 與本輪只用必要一手來源、禁止啟動第三方工具的明確限制衝突時，以本輪授權為準。後續可把範本觸發條件限縮為明確採用該工具且通過審計的任務，移除無條件附帶檢查。範本存在不代表目前已安裝或啟用，這不是模型 API 錯誤 |
| 待確認：載入條件 | 三 repo 採用 AGENTS 指引，不能僅由檔案存在推導 Claude 已載入 | 官方目前支援 AGENTS，但受版本、Project instructions 設定、其他 CLAUDE 指令檔與 plugin 狀態影響；須由維護者日後在既有 session 查看載入證據。本輪未讀原生設定或執行 Claude，不要求補建 CLAUDE.md。[官方載入規則](https://code.claude.com/docs/en/memory#agents-md)（2026-11-21 複查：該段的錨點現為 `#agents-md`，原連結的錨點已失效，已改） |
| 範圍差異，非 API 衝突 | ai-inbox [`AGENTS.md:144`](https://github.com/SanHsien/ai-inbox/blob/main/AGENTS.md#L144) 附近採私有 repo 真名加私有標示；relay [`AGENTS.md:50`](https://github.com/SanHsien/agent-relay/blob/main/AGENTS.md#L50) 採別名 | 此報告遵循交付 repo 與派工要求，使用真名加「私有」。日後跨 repo 搬文件須按目的地去識別，不把一方的局部規則當成另一方的全域規則 |
| 合理的 worker 限制 | relay [`agent_relay/dispatch.py:578–592`](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/dispatch.py#L578) 區分唯讀與可寫工作，要求實際讀檔與證據，並把 handover 視為資料 | 保留。明確工具使用與證據要求有實際用途，不因 MUST／不要等強語氣而機械刪除；官方 changelog 也說應保留有文件根據的 thinking 關鍵字。[官方 changelog](https://code.claude.com/docs/en/changelog) |
| 私有摘要 | `SanHsien/agent-assets`（私有）已完成相關範圍的唯讀檢閱 | 只確認共用資產與原生治理應分開評估；具體 findings 不公開。私有 findings 只記在私有報告，本文不轉載，也不宣稱完整私有稽核以外的保證 |
| 過時／不精確的稽核說法 | 把兩種 prompt audit 當同一功能，或把全部 thinking 字詞判為應刪除 | `/claude-api prompt-audit` 處理 prompts／tool descriptions；`/doctor prompt-audit`（別名 `/checkup prompt-audit`）處理指令檔／skills／agents／commands。官方 changelog 現可確認後者在 **2.1.283** 加入；本輪沒有檢查本機 Claude 版本，也沒有執行任何一種稽核。[官方 changelog](https://code.claude.com/docs/en/changelog)（2026-11-21 複查 changelog 原文：`/doctor prompt-audit` 列在 2.1.283（2026-09-25）條目下，本列說法正確；來源筆記第 0 段 11-17 那則「2.1.283 只出現在 Remote Control 條件」的紀錄與 changelog 不符） |

## 3. API consumer 與相容性判定

```text
找到 Anthropic 關鍵字
        |
        +--> 偵測器／文件範例 --> 非直接 consumer
        +--> CLI argv／環境設定 --> CLI 或 gateway owner 負責
        +--> 自建 Messages request／response adapter
                    |
                    +--> 固定模型及平台 --> 才套用對應遷移規則
```

| 對象／呼叫點 | 模型、平台與實際責任 | 分類與建議 |
| --- | --- | --- |
| ai-inbox `tools/audit_fullstack_security.py:44`、`tools/verify_inbox.py:32` 等 provider 命中 | 機密偵測字串；沒有模型請求 | N/A；保留偵測，不誤當 API adapter |
| ai-inbox [`tools/verify_tool_fallback_matrix.py:257–264`](https://github.com/SanHsien/ai-inbox/blob/main/tools/verify_tool_fallback_matrix.py#L257) | EXAMPLE 資料中的 provider／CLI healthcheck 描述，非 Messages 請求 | N/A；本輪未執行 healthcheck |
| ai-inbox [`docs/agent-dispatch.md:29–39`](https://github.com/SanHsien/ai-inbox/blob/main/docs/agent-dispatch.md#L29) | Claude CLI 操作文件，未固定 Opus 5.5 API request | 文件範例；不能由此判定 API 遷移完成或需要修改 thinking JSON |
| relay [`dispatch.py:341–401`](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/dispatch.py#L341)、`:628` | 依 spec／config 選模型，組 CLI argv 並啟動子程序；可委由外部 launcher 組指令 | 執行中 CLI 委派能力，不是本 repo 自建 Messages adapter。實際 CLI 版本、所選模型、外部 launcher 與 JSON 解析相容性未實測，保留待確認 |
| relay [`dispatch.py:491–524`](https://github.com/SanHsien/agent-relay/blob/main/agent_relay/dispatch.py#L491)、`:404–420` | 第三方 gateway 設定傳給 CLI；程式限制該路線使用非 Anthropic 模型 | gateway 委派設定，不等於直接 Anthropic consumer。Opus 5.5 遷移 N/A；若日後改允許 Anthropic 模型，須重新確認 gateway／CLI owner 與協定。未呼叫設定讀取函式、未讀憑證檔 |
| `SanHsien/agent-assets`（私有） | 本輪程式搜尋範圍未找到直接 Messages consumer | N/A，僅限所檢閱來源；不公布內部呼叫點或程式碼 |

以下是**條件式檢查表，不是已發生的 API findings**。只有日後證實使用 Opus 5.5 的自建 adapter 才適用；依 [Anthropic 官方遷移指南](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)：

- 請求：移除 disabled／手動 thinking budget、sampling 參數及 assistant prefill；按平台選正確模型 ID。
- 工具：`auto`／`none` 與 strict schema 分別管選擇及結構，strict 不保證一定呼叫；computer use 版本須區分平台，Bedrock 有例外。
- 回應：按 block type 解析文字；thinking 顯示可省略，不能因此丟失最終 text；歷史 blocks／signature 原樣保留，並遵守 prefix 相容條件。

本輪沒有發現需要套用上表的具體自建 adapter，因此沒有「已修好」項目，也不把 CLI 的內部 HTTP 行為推定為已驗證。

## 4. 驗收與交付限制

本文件與[跨機同步評估](agent-assets-cross-machine-sync-assessment.md)共同交付。文件檢查命令與結果見該評估第 7 節；檢查只證明公開文件契約，不證明模型或部署行為。

| DoD | 本輪結果 |
| --- | --- |
| 三 repo 範圍、基準、來源、分類與公開建議 | 已記錄；來源 repo Git SHA／dirty 狀態 unknown，以內容指紋與明列邊界補充 |
| consumer／CLI／範例分流，模型及平台適用條件 | 已記錄；無直接 consumer 的有界限 N/A，未虛構遷移 |
| 指定公開報告 | 本文件 |
| 指定私有 findings 報告 | 已於 2026-11-15 補交至 `SanHsien/agent-assets`（私有）的 `docs/prompt-api-audit-findings.md`；內容不在本公開文件 |
| 隱私與操作邊界 | 私有內容不外流；未讀憑證、未呼叫 Claude／API／reviewer，未改原生規則或 hooks |

本報告不代表 Claude 官方 skill 實測、全量安全稽核、API 遷移或來源遠端最新版驗收。後續若要依 findings 修檔，另開任務處理。
