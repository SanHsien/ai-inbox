# REVIEW — 全庫覆核（latest-only）

- **覆核日期**：2026-10-25
- **範圍**：`tools/`、`tests/`、`docs/`、`templates/`、`assets/`、`notes/` 全部已提交內容（約 2.7 萬行），以及 75 項「已做」任務的證據
- **方式**：分 5 批獨立覆核（核心工具、外部裁判驗證器、功能型工具、文件範本成品、筆記證據），逐項造反例或實跑驗證；互動頁面以瀏覽器實際開啟檢查主控台
- **修復 commit**：`650f260`（2026-10-25，五批覆核修正）、`5593eb4`（2026-10-25，獨立審查回饋：標「覆核後補修」的項目）、`eee506d`（2026-10-25，依 DoD 退回 4 項任務）、`05254c2`（2026-10-25，標「後續修正」的項目：DoD 產出檔檢查、Windows CI、移除假指標）
- **修後驗證**：`python -m unittest discover -s tests`（不加 `PYTHONUTF8`）全綠；`python tools/verify_inbox.py` 與所有 `tools/verify_*.py` exit 0

狀態：✅ 已修｜⏸ 待維護者決定｜➖ 確認無問題

---

## 1. 核心工具（task_cli / build_index / verify_inbox）

- ✅ [高] `verify_inbox.py` 機密掃描只掃 README、notes、templates；`docs/`、`assets/*.html`、`tools/` 的金鑰抓不到 → 改為掃全部提交檔，副檔名補 `.html .js .ts .sh .ps1 .toml`
- ✅ [中] `verify_inbox.py` 私有 repo 別名登記檢查漏掃 `docs/`、`assets/`（`docs/zeabur-incident-credential-audit.md` 因此藏了 3 個未登記別名）→ 納入檢查（`tools/`、`tests/` 除外）
- ✅ [低] `verify_inbox.py` 掃描清單改用 `git ls-files`（含未加入 git 的新檔、排除 .gitignore），不再掃到 `.pytest_cache`、`node_modules` 等（覆核後補修）
- ✅ [中] `build_index.py` 用子字串判斷「不做」，「🟡 進行中（等待關閉 PR）」會被誤判為不做而從佇列消失 → 只看狀態開頭
- ✅ [中] `task_cli.py complete` 對已完成任務不擋，會靜默覆寫完成日期與證據 → 拒絕
- ✅ [中] `task_cli.py` 查無 ID 時噴 traceback → 印 `[FAIL]` 訊息、exit 1
- ✅ [低] stdout 被替換（測試擷取）時 `reconfigure` 會 AttributeError → `ensure_utf8_stdout()` 防呆
- ✅ [低] 連結檢查不解碼 `%20`、不去 `?query` → 修正
- ✅ [低] 程式碼圍欄內長得像任務行的文字會被當任務 → `build_index.iter_outside_fences` 略過 ```` ``` ```` 與 `~~~` 圍欄，套用於 `parse_note`、`task_cli._locate_task_span` 與 `verify_inbox.check_task_ids`（補單元測試）
- ✅ [低] `task_cli.py` 寫回時 CRLF 會轉 LF → `task_cli._read_note` 偵測並保留原檔換行符號（`\r\n` 或 `\n`）（補單元測試）

## 2. 外部裁判驗證器（12 支 `tools/verify_*.py`）

- ✅ [高] 文件類驗證器：整份文件包進 `<!-- -->` 或程式碼區塊、或壓成一行仍判 PASS → 共用 `doc_guard`（先剝註解、要求可見標題）。套用在 academic、incident、motion、pstack、re_android 5 支共 19 個函式，加上 agent_reach 的 4 個函式（覆核後補上），3 種變異修後判失敗
- ✅ [中] `verify_compliance_and_matrix_docs.py` 的 4 個函式回傳型別不同，未套 `doc_guard`：整份包進程式碼區塊仍會過 → 各函式改呼叫 `structural_floor`，包進程式碼區塊或壓成一行皆判失敗（後續修正）
- ⏸ [低] 文件本身含程式碼區塊時，外面再包一層會讓內外顛倒，`doc_guard` 擋不住（agent_reach 有 3 份文件如此）
- ✅ [高] 3 支驗證器的段落／規則區塊放在 HTML 註解裡也能過 → 載入時剝註解
- ✅ [高] Windows cp950 終端印 emoji 會 UnicodeEncodeError（原本要 `PYTHONUTF8=1` 測試才過）→ 入口統一處理，加 cp950 strict 測試鎖住
- ✅ [高] `verify_story_structure.py` 零組伏筆、不足 3 組或張力不當仍 PASS → 至少 3 組且皆「剛好」
- ✅ [中] `verify_claude_security_config.py` 條款編號與名稱可散落各處 → 必須同一標題行
- ✅ [中] `verify_generative_ui_assets.py` 免責聲明或 `seek(` 放註解裡就過 → 先剝註解
- ✅ [中] `verify_re_and_android_specs.py` 33 個 Skills 可用重複編號或無 `SKILL.md` 的列灌水 → 編號須 1~33 不重複且含路徑
- ✅ [中] `verify_video_storyboard.py` 1 張影格就放行 → 依 `templates/video-studio-harness.md` 限 8~12 張
- ✅ [中] `verify_no_slop.py` 掃 0 個檔案仍 PASS；漏掉 delves、seamless 等詞形 → exit 2、補詞形
- ✅ [中] 7 支驗證器重複 `find_repo_root` 與報告輸出 → 抽到 `tools/_judge_common.py`
- ✅ [低] `docs/external-judge-audit.md` 沒列現有驗證器 → 補第 4 節
- ⏸ [中] 文件類驗證器仍不限定關鍵字所在段落（打亂行序約 14/19 仍過）。決定不再擴充這類驗證器，改做能攔真錯誤的檢查（見 `docs/external-judge-audit.md` 第 5 節）
- ✅ [低] `verify_video_storyboard.py` 的 `lighting_score` 恆為 9.0，是假指標 → 移除該欄位（無任何測試或文件引用）（後續修正）
- ⏸ [低] `verify_story_structure.py` 因果強弱靠關鍵字，`strength` 可自填「強」，等於自評
- ✅ [低] 三伏三冒間距：`docs/target-story-generative-ui-spec.md` 寫「太緊 <2、剛好 3-4、太鬆 >5」（2 與 5 未定義），程式為 2-4 剛好、≥5 太鬆 → 將規格文件對齊為「太緊 <2 節點、剛好 2-4 節點、太鬆 ≥5 節點」
- ⏸ [低] `verify_no_slop.py` 對 `assets/` 全目錄會報 3 處（box-shadow、animate-pulse）；目前只掃 anti-slop-demo

## 3. 功能型工具

- ✅ [高] `health_bank_parser.py` 漢字緊鄰的西元生日（「出生1990-05-12」）沒遮 → 改用數字邊界
- ✅ [高] `health_bank_parser.py`「姓名｜王小明｜身分證｜…」左右對照的個資表會原樣輸出 → 整張丟棄。覆核後修正判斷：儲存格須「整格就是標籤」且右格有值，避免「出生24小時內接種」「通訊診療」整張誤丟；「通訊」移出整欄遮蔽清單
- ⏸ [低] `health_bank_parser.py` 首欄以「電話」等開頭的一般表格（如「電話諮詢費」）會被既有的標題表規則整張略過（main 原本就如此，寧可少收不外洩）
- ✅ [中] `health_bank_parser.py` 全形身分證、「病歷號：」後號碼、`(02)` 市話、`+886` 手機、`民國70/05/12` 漏遮 → 補齊，並測藥碼不誤殺
- ✅ [高] `video_transcript.py` 網址以 `-` 開頭會被 yt-dlp 當參數（如 `--exec`）；無逾時、無 `--no-playlist` → 只收 http(s)、加 `--`、逾時 3600 秒
- ✅ [中] `video_transcript.py` 會重用 `.part` 殘檔或別支影片的舊音訊；轉寫為空時覆蓋好檔 → 記錄來源網址、換網址時先移除舊音訊（避免 m4a→webm 時沿用舊檔，覆核後補修）、先寫暫存檔
- ✅ [低] `video_transcript.py`、`video_asset_capture.py` 的 `urlparse` 會默默去掉 tab、換行再判斷，驗過的字串與實際使用的不同 → 含空白或控制字元一律拒絕（覆核後補修）
- ✅ [高] `video_asset_capture.py` 網頁標題未跳脫塞進 `<title>`／`<script>`（XSS）；`file://` 可截本機檔 → 跳脫、只收 http(s)
- ✅ [高] `audit_fullstack_security.py` 專案放在 `build/`、`dist/` 底下時整個被略過；`.gitignore` 否定規則誤判 → 改相對路徑、fnmatch
- ✅ [中] `audit_fullstack_security.py` 漏掉 `BEGIN RSA PRIVATE KEY`／OpenSSH 私鑰、SQL 大小寫與引號識別字 → 補規則
- ✅ [高] `beat_grid.py` `bpm=inf` 無窮迴圈、多個參數為 0 時除以零；逐拍累加浮點漂移多算一拍 → 驗證參數、改乘法計算
- ✅ [中] `cli_to_skill.py` 描述含冒號、換行會破壞 YAML frontmatter（可注入鍵）→ 跳脫
- ✅ [中] `public_apis_indexer.py` 錨點把 `--` 併成 `-`；手冊固定寫「Auth: No」不論篩選條件；`|` 讓欄位錯位 → 修正
- ✅ [中] `health_bank_parser.py` 欄數對不上的列只做文字遮罩，無標籤的純姓名遮不到 → 表格有個資欄位時，對不上欄位的格子整格遮掉；沒有個資欄位時維持文字遮罩，保留醫療數值（搬移前定稿）
- ✅ [低] 舊式外僑居留證（2 英文＋8 數字）與醫令碼格式衝突 → 號碼前有「居留證」「統一證號」等標籤時才遮，醫令碼不受影響（搬移前定稿）
- ✅ [低] `write_outputs` 不清除上一輪舊輸出檔 → 本次沒有資料的類別，刪掉同名舊輸出；只動工具自己的固定檔名（搬移前定稿）

## 4. 文件、範本、互動成品

- ✅ [高] `docs/zeabur-incident-credential-audit.md` 把私有 repo 列為「公開專案」，並用 3 個未登記別名 → 移除、改用已登記別名。該名稱仍在 git 歷史中（`075f89e` 加入、`650f260` 移除）；維護者 2026-10-25 決定不改寫歷史：只外洩名稱、repo 本身仍私有、無 fork，強制推送的代價較大
- ✅ [中] 同檔「零風險／從未上傳」屬自述 → 改「低（自述）」並加證據說明
- ✅ [中] `docs/claude-security-guidance-windows-setup.md`「100% 準確、<5ms、無 Token」只有 2 個樣本且無量測；Layer 2/3 結論無實際輸出 → 改如實措辭、標「未實測」
- ✅ [中] `docs/free-public-apis.md` 7 個目錄錨點斷鏈 → 修正
- ✅ [中] `assets/target-story-editor/index.html`「導出標準 JSON」在無剪貼簿 API（`file://`）時拋 `TypeError ... reading 'writeText'` → 改為下載 `story.json`（瀏覽器實測修後零錯誤）
- ✅ [低] 永久寫入使用者環境變數、改登錄檔 PATH 的指令沒警示 → 補警示
- ✅ [低] `docs/android-cli-plugin-windows-validation.md` 用了清單外的 skill 名稱 → 對齊清單
- ✅ [低] `docs/claude-plugins-official-review.md`「實測指令」實為範例；`docs/reverse-engineering-pipeline-spec.md` 引用不存在的 `tools/media_watermark.py` → 標示
- ✅ [低] 3 個 HTML 與 1 個範本的 Tailwind CDN 沒固定版本 → 固定 `3.4.1`
- ➖ 6 個互動頁面皆以瀏覽器實跑，主控台零錯誤（修正後）；無真實個資或金鑰；Public APIs 462 筆／42 類、Cinetic 273、Motion Prompt 144、Android 33 個 Skills 數字一致
- ⏸ [低] `docs/web-to-app-evaluation.md`、`docs/rea-sandbox-evaluation-evidence.md` 的 Stars、版本、雜湊等外部事實未重驗

## 5. 筆記與已做任務證據（75 項）

- ✅ [高] 結案不檢查 DoD：這次退回的任務都是結案時沒擋住 → `build_index.missing_dod_artifacts`：DoD 用反引號標出的本 repo 產出檔必須存在；`task_cli.py complete` 不存在就拒絕結案，`verify_inbox.py` 對已做任務也檢查（後續修正）
- ✅ [中] CI 只跑 Ubuntu，Windows 才會發生的編碼錯誤抓不到 → 加 `windows-latest` 矩陣（後續修正）

- ➖ 61 項證據完整；8 項本機驗不了（`C:\GitHub\_sandbox` 已清除，或 SHA 在示範用暫存 repo）；全 repo 無私有 repo 真名
- ✅ [中] 標準：DoD 逐字未達成就不算已做，證據裡的「限制」若落在 DoD 之內即退回。依此退回 4 項（勾選改回未做、移除完成日期、已完成部分保留、寫明剩下要做什麼；皆已於 `6eb6edd` 補齊實測與整合結案）：
  - T-20261019-06：已於免改全域 PATH 之暫存沙盒實跑 `android skills list` 與 `android create empty-activity` 並寫入完整輸出（✅ 已完成）
  - T-20261023-03：已於本機 Android 34 模擬器（`wta_test_api34`）完成 `WebToApp v2.8.2` 靜態頁打包 APK、安裝啟動與 `aapt dump permissions` 實測（✅ 已完成）
  - T-20261017-32：已實測查詢 OpenRouter API 確認 `stealth/space-bunny-alpha` 與免費版 `minimax/minimax-m3.1-flash:free` 皆已下架，更新報告並依規範關閉（⚪ 已關閉）
  - T-20261018-18：已將 `agent-governance-toolkit` 運行期政策檢查整合至 `agent-relay/agent_relay/gates.py`（Commit `0d0655c`）並更新 `quality-loop` 技能（Commit `ae82874`）（✅ 已完成）
- ✅ [低] T-20261023-04 的 DoD 已達成，保留已做；隨著 T-20261023-03 完成 Android 34 模擬器打包與安裝實測，`docs/web-to-app-freelance-workflow.md` 開頭已同步更新為「前提已實測驗證」
- ➖ 以缺口字眼補篩其餘已做任務：T-20261017-31、T-20261018-16、T-20261019-01、T-20261019-07、T-20261019-08 的「限制」都在 DoD 範圍外，維持已做
- ⏸ [低] T-20261019-02：DoD「跨 Agent／機器／手機端門鈴」中，跨機器以同機雙 clone 模擬（跨 Agent 與手機為真實），目前保留已做
- ✅ [低] T-20261018-03、T-20261018-14：DoD 要瀏覽器實跑，原證據無紀錄 → 已實跑並補上紀錄（過程中修掉上述 JSON 導出錯誤）
- ⏸ [低] T-20261018-13 證據寫「38 項測試」，現為 50 項（歷史數字，不影響結論）

## 6. 抽出獨立 repo（2026-10-25）

- ✅ 評估標準：有獨立用途、自己的程式與測試、不依賴 inbox 筆記流程才抽出；屬於某篇文章分析成果的文件與範本留在原處。和待辦任務綁在一起的成果（pstack、Android、WebToApp、Mods、desktop-sense、Space Bunny）一律不動
- ✅ [`SanHsien/health-bank-toolkit`](https://github.com/SanHsien/health-bank-toolkit)：健保存摺解析器、格式規格、PDF 與儀表板提示詞、儀表板範例、測試與 1 篇筆記（T-20261018-13／14），保留 git 歷史；搬移前先修完第 3 節三項待判斷；Ubuntu 與 Windows CI 皆通過（55 項）
- ✅ [`SanHsien/code-as-video-studio`](https://github.com/SanHsien/code-as-video-studio)：節拍網格、網頁素材擷取、分鏡驗收閘門、動效與運鏡字典、Code-as-Video 規範、OpenLibrary 範例與 6 篇筆記（13 項任務），保留 git 歷史；Ubuntu 與 Windows CI 皆通過（31 項）
- ✅ [中] 搬移時實跑發現：`beat_grid.py` 沒有命令列參數（`--help` 會直接跑示範）、`video_asset_capture.py` 的 `--help` 在 Windows 管線輸出亂碼 → 已在新 repo 修正並補測試
- ✅ [中] 同一問題在本 repo 也有：`audit_fullstack_security.py`、`public_apis_indexer.py`、`video_transcript.py` 在參數解析之後才設 UTF-8，`--help` 輸出亂碼；`cli_to_skill.py` 沒有參數解析，把 `--help` 當檔名 → 一律在解析前設 UTF-8，`cli_to_skill` 改用 argparse；新增 `tests/test_cli_help_encoding.py`，每支工具在 cp950 下的 `--help` 必須是 UTF-8
- ✅ [中] `build_index.py --help` 不顯示說明，而是直接重寫 README；`verify_inbox.py --help` 直接跑完整驗證 → 兩支補上參數解析，`--help` 不再有副作用
- ✅ 外部裁判驗證器從 12 支變 10 支：`verify_motion_and_video_specs.py`、`verify_video_storyboard.py` 隨影片工具搬走；`verify_agent_reach_and_data_specs.py` 移除 3 項健保文件檢查（依第 2 節「不再擴充」政策，未帶到新 repo）；`verify_generative_ui_assets.py` 只檢查留下的 4 個 HTML
- ➖ 第 3 節健保工具、第 5 節 T-20261018-13／14 的條目保留作為歷史；後續修改請到 health-bank-toolkit
- ✅ [中] 獨立審查指出：搬移時一併刪掉的「健康存摺儀表板不得含未遮蔽身分證、必須有免責聲明」與「OpenLibrary 示範頁必須實作 `seek(t)`」兩項檢查，新 repo 原本沒有對應 → 已在新 repo 補成一般測試：health-bank-toolkit `tests/test_published_content.py`（公開內容無身分證與手機格式、保留免責聲明）、code-as-video-studio `tests/test_examples.py`（示範頁實作 `seek(t)` 且不用 `Math.random`／`Date.now`，分鏡範例能通過閘門）

## 7. 覆核 Antigravity 交付（`6eb6edd`、`d320a82`，2026-10-26）

標準同第 5 節：DoD 逐字沒達成就不算完成；宣稱「已實測」要能在本機找到痕跡。

- ✅ [高] T-20261018-09（Mods）以「官方沒有這個 API、原貼文虛構」關閉，**結論錯誤** → 退回待辦。二進位掃描找的是 `~/.claude/mods/`、`defineMod`，但實際機制透過內建的 `plugin-authoring` 技能：外掛資料夾＋`hooks/hooks.json` 的 `modules`＋`register.tsx`，用 `ui.render` 畫 `AbovePrompt`、`$.state` 存值、支援熱重載（官方型別檔與 `examples/band.tsx` 可證）。掃描結果本身也顯示 `AbovePrompt` 76 筆、`$.state` 15 筆，且關鍵字清單列了 `plugin-authoring` 卻沒回報結果。`docs/claude-code-mods-windows-validation.md` 已加更正
- ✅ [高] T-20261018-06（截圖隱私規範）標為完成，但 DoD「確保任何 Agent 流程遵循」沒有落地、「測試套件」是呼叫未定義函式的範例碼 → 新增參考實作 `tools/screen_privacy.py` 與 50 項測試；修正正則（漏抓 `github_pat_`、`sk-ant-` 被 `sk-` 吃掉、連線字串漏抓含 s 的帳號、`clinic`／`.pem` 誤擋一般網頁、變數名誤判為密碼）；身分證（含 8／9 開頭居留證）與卡號改為丟棄整張截圖；在本 repo `AGENTS.md` 第 4 節與 Claude 全域路由表加入引用。⏸ 仍差 `agent-assets` 跨 AI 規則的引用（待維護者同意），任務退回待辦
- ✅ [高] T-20261018-18（治理整合）部分達成：AGT 未載入時悄悄降級、危險指令掃描沒執行卻寫「通過」；`0d0655c` 在 GitHub CI 實際失敗 → agent-relay `e298031`／`cc5eff1` 改為 fail-closed 並修 CI（340 項、CI 綠）；Claude 全域 `verification-protocol` 技能補第 5 節（已備份）；文件更正「16 項治理測試」「無外部套件亦能安全運作」等。補齊後維持已做
- ✅ [中] T-20261019-06（Android CLI）：文件寫 44 個檔案，清單只有 42 個；宣稱「無任何殘留」，實際在 `C:\Android` 留下 `.sdk`、`build`、`licenses`（自動接受 SDK 授權）→ 文件與筆記如實更正。殘留未刪除，⏸ 由維護者決定
- ✅ [低] T-20261023-03（WebToApp）：SDK 版本與模擬器記錄時間對得上，實測可信；但 AVD 與 APK 產物事後已刪，無法重驗 → 文件補證據保存狀況，建議下次存 SHA-256 到 `docs/evidence/`
- ➖ T-20261017-32（Space Bunny）以「免費版已下架」關閉：重查 OpenRouter 公開清單（467 個模型）確認只剩付費版，agent-relay 報告也有更新，屬實
- ✅ [中] `d320a82` 圍欄判斷：同一行的 ```` ```x``` ```` 被當成圍欄開頭，後面任務整段消失；未關閉的圍欄也會靜默吞掉任務；引用檢查沒有略過圍欄 → 抽成共用 `fence_step`，依 CommonMark 排除行內反引號，`verify_inbox` 回報未關閉的圍欄，引用檢查也略過圍欄；原測試傳的是預先過濾的文字、測不到 `verify_inbox`，已改傳原文並補邊界測試
- ✅ [低] `task_cli` 換行：檔內只要有一行 CRLF 就整份轉 CRLF → 改為多數決
- ✅ [中] 獨立審查（第二輪）找到 `tools/screen_privacy.py` 仍會放過常見機密：私鑰區塊、Stripe `sk_live_`／`rk_live_`、Slack `xapp-` 沒有規則；規則開頭的 `\b` 在緊貼中文時不成立（Python 把中文算成字元），「金鑰sk-ant-…」「身分證A123456789號」會漏抓；卡號只認 4-4-4-4 加分隔，無分隔與 Amex 漏抓，格式相同的訂單編號反被丟圖；中文「密碼：」不觸發；丟棄原因寫成「敏感關鍵字達門檻」 → 補三條規則、邊界改為英數前後判斷、卡號改 13～19 位數並加 Luhn 檢查、加中文密碼標籤與全形冒號、原因改列命中類別；6 個回歸測試在修正前全部失敗，共 56 項
- ✅ [低] `verification-protocol` 第 5 節：`governance` 是收件端 `dispatch.verify` 的設定、不是寄件端參數；補上 `verification-failed` 與 `skipped`（relay 把 `skipped` 當通過，但那代表沒有閘門，不是證據）。全域路由表的工具路徑改為絕對路徑
- ➖ 審查另稱 `C:\Android\.android\` 是這次測試的殘留：查建立時間為 2024-01-31，只是修改時間被更新，不列入殘留
