# AI Inbox 任務 DoD 外部裁判（External Judge）稽核報告

> 依據 Felix Rieseberg〈How to be more ambitious〉所提出之「深度（Depth）維度」與「外部裁判（External Judge）原則」，Agent 執行任務之驗收標準（DoD）必須具備自身以外的客觀檢查機制（如自動化測試、機械式腳本斷言、外部系統 API/CLI 實體驗證、Schema 檢驗等），而非僅依賴 Agent 自行產出之文件或自評。
> 本次稽核針對 `ai-inbox` 待辦佇列中抽查之 10 項未做任務（含進行中與未做），逐項檢視其現行驗收標準（DoD）之驗證方式，評估其是否具備外部裁判，並提出具體之工程化補強建議。

---

## 1. 抽查 10 項未做任務之 DoD 外部裁判檢驗矩陣

| 任務編號 | 驗證方式 | 是否外部裁判 | 建議 |
| :--- | :--- | :---: | :--- |
| T-20261017-27 | 產出設定範例與文字驗證記錄，依賴人工敘述確認參數生效且會話狀態受控 | 否 | 撰寫設定檔驗證腳本，以 JSON Schema 機械式校驗 settings.json，並透過 CLI 執行 dry-run 會話斷言參數已被直譯器載入生效。 |
| T-20261023-01 | 產出安裝與設定手冊，記錄終端 log，以肉眼或文件比對確認 ~/.claude/security/log.txt 是否記錄攔截輸出 | 否 | 建立自動化整合測試腳本，執行注入危險指令（如 `eval()`）的測試語句，直接由測試斷言 log.txt 是否產生結構化攔截記錄與非零退出碼。 |
| T-20261023-05 | 使用 Select-String -Pattern '結論' 檢查字樣，並輔以 secret 掃描工具確認無敏感金鑰 | 部分 | 保留 secret 掃描作為防護硬閘門；但 Select-String 僅確認關鍵字存在，應補充憑證撤銷記錄格式與歷史追蹤之自動化校驗腳本。 |
| T-20261023-02 | 產出範本與手冊，在範例專案刻意編寫越界檔案路徑與空殼函式，由人機互動觀察 Claude Code 是否阻止 | 否 | 建立自動化對抗測試 Harness，模擬違規路徑與空殼函式提交，以外部測試程式直接檢驗攔截器退出碼與錯誤日誌，而非仰賴 LLM 自發性審查。 |
| T-20261023-03 | 以 Test-Path 驗證 Markdown 評估文件存在，並檢查內文包含「結論：可行／不可行」字串 | 否 | 引入外部 SDK 工具（如 Android SDK 之 `aapt dump badging` 或 `apkanalyzer`）機械式驗證構建之 APK 是否合法，而非僅驗證文字報告存在。 |
| T-20261024-03 | 以 Select-String -Pattern '結論' 驗證文件存在該字樣，手動比對終端輸出與無 token 限制 | 否 | 編寫自動化探測腳本，實際執行 CLI --version，若串接 MCP 則發送標準 JSON-RPC `tools/list` 請求並驗證回應資料結構。 |
| T-20261024-05 | 以 Select-String -Pattern 'https://' 計數 URL 至少 4 個，並檢查全文包含判定文字 | 否 | 撰寫 HTTP 探測腳本（如 curl 或 Python 連線檢測）確保所附官方連結皆為有效 HTTP 200，並透過跨模型二審（ai-review）核實判定論據。 |
| T-20261023-04 | 檢查文件是否產出六步驟規格；若前置條件不成立則改標記為不做 | 否 | 將接案流程規格定義為可程式化解析之 YAML/JSON 規格檔或狀態機圖，撰寫 Schema 測試驗證步驟輸入輸出定義，而非僅檢查 Markdown 段落。 |
| T-20261024-04 | 以 Select-String -Pattern '^\| ' 計數 Markdown 表格列數是否大於等於 8 列 | 否 | 撰寫結構解析檢查器，自動驗證比對矩陣是否完整涵蓋協定、通訊格式與狀態遷移各面向鍵值，或引入 blind-review 子代理進行對抗式審查。 |
| T-20261024-06 | 以 Select-String -Pattern 'https://' 計數 URL 至少 3 個，並確認前置任務已完成 | 否 | 建立可執行的 Checklist 驗證器，自動解析 Markdown 核取方塊結構（- [ ]）之類別數量，並以腳本批量探測引證規範條款之 URL 連通性。 |

---

## 2. 稽核結論與數據分析

缺口統計：抽查 10 項未做任務中，完全具備外部裁判 0 項（0%）、部分具備外部裁判 1 項（10%）、完全缺乏外部裁判 9 項（90%）；現有 DoD 高度仰賴「文件存在（Test-Path）」與「正則字串計數（Select-String）」，缺乏客觀測試腳本、程式化斷言或獨立工具審查，外部裁判缺口率達 90% 以上。

---

## 3. 系統性補強方針

針對上述稽核發現之缺口，建議維護者與開發 Agent 於後續任務規劃中落實下列三項外部裁判工程化標準：

1. **升級正則計數為語法／Schema 斷言**：對於純文件或規格類任務，避免僅用 Select-String 計算列數或連結數，改以 Python/Pydantic/YAML Schema 解析實際結構與必填欄位。
2. **實體執行取代靜態日誌記錄**：對於工具配置與外掛整合任務（如 CLI、外掛設定），禁止僅要求貼上 terminal log，必須搭配可執行的微型測試腳本（Smoke Test）驗證真實環境反饋與 Exit Code。
3. **質化產出引入獨立審查代理人（Multi-Agent Review）**：針對調研、分析與架構比對等難以單靠單元測試斷言之任務，明確指定外部審查技能（如 `blind-review`、`ai-review`）作為驗收硬閘門，避免 Agent 自產自評。

---

## 4. 已落地的外部裁判驗證器（2026-10-25 現況）

上述補強方針已有 10 支驗證器實作於 `tools/`（原為 12 支；`verify_motion_and_video_specs.py` 與 `verify_video_storyboard.py` 已於 2026-10-25 隨影片工具移至 [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)）（皆純 Python stdlib），共用邏輯集中在 `tools/_judge_common.py`（UTF-8 輸出、repo 根推導、HTML 註解／程式碼區塊剝除、標題結構下限、統一 PASS/FAIL 報告）。每支都有對應的 `tests/test_verify_*.py`；`tests/test_verify_judge_common.py` 以「整份文件藏進註解／程式碼區塊／壓成一行必須失敗」的反例檢驗共用防線。

| 驗證器 | 檢查對象 | 指令 |
| :--- | :--- | :--- |
| `verify_claude_security_config.py` | `docs/claude-idle-compaction-setup.md`、`templates/claude-security-guidance.md`（含 `scan_code_snippet` 靜態掃描） | `python tools/verify_claude_security_config.py` |
| `verify_compliance_and_matrix_docs.py` | 合規清單、宣稱查證、對照矩陣、野心提示清單（4 份） | `python tools/verify_compliance_and_matrix_docs.py` |
| `verify_incident_and_workflow_specs.py` | 資安事件盤點、應變清單、WebToApp 評估與接案流程（4 份） | `python tools/verify_incident_and_workflow_specs.py` |
| `verify_generative_ui_assets.py` | `assets/` 內 4 個單檔 HTML（結構、HTTPS） | `python tools/verify_generative_ui_assets.py` |
| `verify_academic_and_latex_guard.py` | LaTeX 保護提示詞、學術閱讀提示詞、實測報告（3 份） | `python tools/verify_academic_and_latex_guard.py` |
| `verify_re_and_android_specs.py` | 逆向工程流水線、REA 沙盒、Android 33 Skills、Android CLI 評測（4 份） | `python tools/verify_re_and_android_specs.py` |
| `verify_agent_reach_and_data_specs.py` | Agent-Reach 路由、Public APIs（3 份；健康存摺文件已移至 health-bank-toolkit，這 3 項檢查未帶過去） | `python tools/verify_agent_reach_and_data_specs.py` |
| `verify_pstack_and_fullstack_specs.py` | pstack playbooks、外掛評測、全端建站技能、主體盤點提示詞（4 份） | `python tools/verify_pstack_and_fullstack_specs.py` |
| `verify_no_slop.py` | HTML／CSS 的 SLOP-01~05 罐頭特徵（預設掃描 `assets/` 全目錄，可傳指定路徑或目錄；掃不到任何檔案回傳 exit 2） | `python tools/verify_no_slop.py [路徑...]` |
| `verify_story_structure.py` | 靶心人故事 JSON：七節點／三箭頭字數契約、因果、三伏三冒（至少 3 組且張力皆「剛好」） | `python tools/verify_story_structure.py --input story.json` |

另有 `tools/verify_inbox.py`（筆記契約，CI 同款）不在本批次內。全套單元測試：`python -m unittest discover -s tests`（CI 即執行此指令）。

**已知限制（誠實揭露）**：文件類驗證器本質上仍是「在可見內容中找必備關鍵字／標題／表格列數」。它們能擋下整份藏進註解、塞進程式碼區塊或缺少標題結構的作弊，但不證明語意正確；關鍵字是否出現在「對的段落」多半未逐段限定。質化內容仍需第 3 節的獨立審查代理人（`blind-review`、`ai-review`）把關。

## 5. 擴充政策（2026-10-25 起）

- **不再新增「一份文件一支」的關鍵字型驗證器。** 現有 10 支保留，用途是防止既有文件的結構被改壞；它們只檢查關鍵字與段落是否存在，打亂行序後約 14／19 個函式仍會通過，擋不住內容錯誤。
- 要新增檢查時，優先做**能攔下真錯誤**的機械檢查，例如 `verify_inbox.py` 的「已做任務的 DoD 產出檔必須存在」、機密與私有別名掃描。
- 新文件不需要配一支驗證器；DoD 寫清楚產出檔路徑（用反引號標出 `docs/...`），結案時 `task_cli.py complete` 就會檢查它存在。
