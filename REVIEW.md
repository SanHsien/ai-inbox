# REVIEW — 全庫覆核（latest-only）

- **覆核日期**：2026-10-25
- **範圍**：`tools/`、`tests/`、`docs/`、`templates/`、`assets/`、`notes/` 全部已提交內容（約 2.7 萬行），以及 75 項「已做」任務的證據
- **方式**：分 5 批獨立覆核（核心工具、外部裁判驗證器、功能型工具、文件範本成品、筆記證據），逐項造反例或實跑驗證；互動頁面以瀏覽器實際開啟檢查主控台
- **修復 commit**：`650f260`（2026-10-25，五批覆核修正）、`5593eb4`（2026-10-25，獨立審查回饋：標「覆核後補修」的項目）、`eee506d`（2026-10-25，依 DoD 退回 4 項任務）
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
- ⏸ [低] 程式碼圍欄內長得像任務行的文字會被當任務（目前由 ID 重複檢查間接擋住）
- ⏸ [低] `task_cli.py` 寫回時 CRLF 會轉 LF（現有筆記皆 LF，暫無影響）

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
- ⏸ [低] 三伏三冒間距：`docs/target-story-generative-ui-spec.md` 寫「太緊 <2、剛好 3-4、太鬆 >5」（2 與 5 未定義），程式為 2-4 剛好、≥5 太鬆
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
- ⏸ [中] `health_bank_parser.py` 欄數對不上的列只做文字遮罩，無標籤的純姓名遮不到（是否整列丟棄）
- ⏸ [低] 舊式外僑居留證（2 英文＋8 數字）與醫令碼格式衝突，未遮
- ⏸ [低] `write_outputs` 不清除上一輪舊輸出檔

## 4. 文件、範本、互動成品

- ✅ [高] `docs/zeabur-incident-credential-audit.md` 把私有 repo 列為「公開專案」，並用 3 個未登記別名 → 移除、改用已登記別名。**注意：該名稱仍在 git 歷史中**
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
- ✅ [中] 標準：DoD 逐字未達成就不算已做，證據裡的「限制」若落在 DoD 之內即退回。依此退回 4 項（勾選改回未做、移除完成日期、已完成部分保留、寫明剩下要做什麼）：
  - T-20261019-06：DoD 要的 `android skills list` 與建立測試專案的實際輸出未取得（安全閘門刻意未安裝）
  - T-20261023-03：DoD 要的 APK 安裝截圖或 log 未取得（無模擬器與實機）
  - T-20261017-32：DoD 要「實測基準報告」，但模型的延遲、正確率、1M 承載力都未實測
  - T-20261018-18：DoD 明列要復用 `agent-governance-toolkit`，未整合；`quality-loop` 技能也未改
- ✅ [低] T-20261023-04 的 DoD 已達成，保留已做；但它以 T-20261023-03「可行」為前提，已在 `docs/web-to-app-freelance-workflow.md` 開頭標明前提未實測
- ➖ 以缺口字眼補篩其餘已做任務：T-20261017-31、T-20261018-16、T-20261019-01、T-20261019-07、T-20261019-08 的「限制」都在 DoD 範圍外，維持已做
- ⏸ [低] T-20261019-02：DoD「跨 Agent／機器／手機端門鈴」中，跨機器以同機雙 clone 模擬（跨 Agent 與手機為真實），目前保留已做
- ✅ [低] T-20261018-03、T-20261018-14：DoD 要瀏覽器實跑，原證據無紀錄 → 已實跑並補上紀錄（過程中修掉上述 JSON 導出錯誤）
- ⏸ [低] T-20261018-13 證據寫「38 項測試」，現為 50 項（歷史數字，不影響結論）
