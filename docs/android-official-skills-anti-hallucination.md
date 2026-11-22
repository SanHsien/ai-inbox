# Google Android 官方 Skills 深度盤點與現代 Android 開發防幻覺手冊

> 本手冊收錄於 `docs/android-official-skills-anti-hallucination.md`，深度解構 Google Android 官方開源之 [`android/skills`](https://github.com/android/skills) 倉庫。
> **實測說明**：社群文章原稱「官方 30 個 Skills」；2026-10-23 首次盤點為 33 個，**2026-11-16 以 GitHub API 列出 `main` 分支所有 `SKILL.md`，共 37 個**。下表逐列對照過官方目錄：新增 5 個（`mlkit-agent-api`、`ink-app-builder`、`ink-custom-brush-builder`、`ios-to-android`、`glance-appwidget-updates-and-memory`），移除 1 個（`jetpack-compose/theming/styles`，首次盤點時列入，2026-11-16 已不在官方目錄）。新增 5 列的職責摘自各 `SKILL.md` 的 `description`；其餘 32 列只核對路徑存在，職責敘述沿用首次盤點、未逐一重讀。上游由機器人定期更新，數量會再變，使用前請重新列目錄。以 ai-inbox 範本形式交付。

> **2026-11-21 更正**：以 GitHub API 重列 `main` 分支，仍是 37 個、路徑與下表一致（約 1.07 萬顆星，Apache-2.0）。這次逐一讀了全部 37 個 `SKILL.md` 的 `description`，改掉 12 列與官方描述不符的職責敘述（`camerax`、`litert-runtime`、`ml-kit-genai-prompt-api`、`adaptive`、`jetpack-compose-performance`、`navigation-event`、`play-billing-library-version-upgrade`、`android-profiler`、`edge-to-edge`、`testing-setup`、`wear-widgets`、`projected-hardware`）：舊敘述寫了官方沒提的東西（JUnit5、Robolectric、NPU、Energy、Android 14+、Adaptive Navigation Suite 等）。依據：<https://github.com/android/skills>，查閱日 2026-11-21。

> **2026-11-22 補做（2026-11-21 稽核後重做）**：任務 DoD 要求的「觸發情境與輸入輸出契約」先前一直沒做。這次讀了全部 37 個 skill 主檔的正文，新增 1.1 節契約表；第 2 節改成先列官方 skill 實際涵蓋的 Compose 遷移清單（附檔案路徑），本 repo 自己的延伸移到 2.3 節並標明。

---

## 1. 官方 37 個 Skills 全景盤點（2026-11-16）

| # | 分類領域 | 官方相對路徑 (來源路徑) | Skill 名稱 | 核心職責與防幻覺重點 |
| :- | :--- | :--- | :--- | :--- |
| 1 | **Build System** | `build-system/agp/agp-9-upgrade/SKILL.md` | `agp-9-upgrade` | 升級至 Android Gradle Plugin 9.0，修正 Gradle API 廢棄語法與命名空間宣告。 |
| 2 | **Camera** | `camera/camerax/SKILL.md` | `camerax` | CameraX 相機開發指引：錄影的非同步生命週期、低階硬體互通、整合 ML Kit 或 Media3 特效。 |
| 3 | **Cars (車載)** | `cars/android-for-cars-parked-apps/SKILL.md` | `android-for-cars-parked-apps` | 適配車載 Android Auto / Automotive 停車模式下的影音與瀏覽器應用。 |
| 4 | **Device AI** | `device-ai/appfunctions/SKILL.md` | `appfunctions` | 識別並整合 Android 系統級 AppFunctions 語意工作流。 |
| 5 | **Device AI** | `device-ai/litert/litert-lm/SKILL.md` | `litert-lm` | 於裝置端利用 LiteRT-LM 執行開源大型語言模型 (On-Device LLM)。 |
| 6 | **Device AI** | `device-ai/litert/litert-runtime/SKILL.md` | `litert-runtime` | 以 CompiledModel API 設定並執行 `.tflite` 模型的裝置端推論（官方描述寫 CPU 與 GPU）。 |
| 7 | **Device AI** | `device-ai/ml-kit-genai-prompt-api/SKILL.md` | `ml-kit-genai-prompt-api` | 實作 ML Kit GenAI Prompt API：在裝置端向 Gemini Nano 送自然語言請求、結構化輸出、前綴快取。 |
| 8 | **Device AI** | `device-ai/mlkit-agent-api/SKILL.md` | `mlkit-agent-api` | 以 ML Kit GenAI Agent API（Gemini Nano、AICore）建立裝置端代理流程：多輪對話、透過 AppFunctions 呼叫工具。 |
| 9 | **DevTools** | `devtools/android-cli/SKILL.md` | `android-cli` | 指導安裝與操作 `android` 官方命令列工具（專案建置、模擬器操作）。 |
| 10 | **Identity** | `identity/restore-credentials/SKILL.md` | `restore-credentials` | 實現 Android 換機無縫登入與憑證自動還原 (Restore Credentials)。 |
| 11 | **Identity** | `identity/verified-email/SKILL.md` | `verified-email` | 安全取得經過驗證的使用者電子信箱工作流。 |
| 12 | **Compose** | `jetpack-compose/adaptive/SKILL.md` | `adaptive` | 讓 UI 適應手機、平板、折疊機、筆電、桌機、TV、車用與 XR 的視窗大小與輸入裝置（Compose MediaQuery API）。 |
| 13 | **Compose** | `jetpack-compose/ink/ink-app-builder/SKILL.md` | `ink-app-builder` | 以 Jetpack Ink（`androidx.ink`）與 Compose 加入手寫與觸控筆繪圖、擦除、復原與筆畫保存；不適用 XML View。 |
| 14 | **Compose** | `jetpack-compose/ink/ink-custom-brush-builder/SKILL.md` | `ink-custom-brush-builder` | 為 Jetpack Ink 定義自訂筆刷（`BrushFamily`、筆尖形狀、壓力與傾斜感應、材質）。 |
| 15 | **Compose** | `jetpack-compose/jetpack-compose-performance/SKILL.md` | `jetpack-compose-performance` | 診斷並最佳化 Compose UI 程式碼，減少重組負擔、避免掉幀。 |
| 16 | **Compose** | `jetpack-compose/migration/migrate-xml-views-to-jetpack-compose/SKILL.md` | `migrate-xml-views-to-jetpack-compose` | 結構化將傳統 XML Layout 遷移為現代 Jetpack Compose 函式。 |
| 17 | **Media** | `media/media3-cast-integration/SKILL.md` | `media3-cast-integration` | 整合 Jetpack Media3 與 Google Cast 投影串流。 |
| 18 | **Migration** | `migration/ios-to-android/SKILL.md` | `ios-to-android` | 把 iOS／Swift 的功能或整個 App 移植到 Android（Compose、Room、Coroutines 與 Flow）。 |
| 19 | **Navigation** | `navigation/navigation-3/SKILL.md` | `navigation-3` | 遷移至 Jetpack Navigation 3 現代型別安全 (Type-Safe) 導航架構。 |
| 20 | **Navigation** | `navigation/navigation-event/SKILL.md` | `navigation-event` | 用 NavigationEvent 函式庫（`androidx.navigationevent`）攔截返回手勢並執行預測性返回動畫；含 SDK 36 以上從舊 `BackHandler` 遷移。 |
| 21 | **Performance** | `performance/anr-audit-and-fix/SKILL.md` | `anr-audit-and-fix` | 審查主執行緒阻塞風險並解析 ANR 堆疊傾印 (Stack Dump)。 |
| 22 | **Performance** | `performance/r8-analyzer/SKILL.md` | `r8-analyzer` | 分析 R8 ProGuard 混淆規則，移除冗餘 Keep Rules 並縮小 APK 體積。 |
| 23 | **Play 生態** | `play/engage-sdk-integration/SKILL.md` | `engage-sdk-integration` | 整合 Google Play Engage SDK 提升個人化內容推薦曝光。 |
| 24 | **Play 生態** | `play/play-billing-library-version-upgrade/SKILL.md` | `play-billing-library-version-upgrade` | 把專案從任何舊版 Play Billing Library 升級到最新穩定版。 |
| 25 | **Play 生態** | `play/play-policy-insights/SKILL.md` | `play-policy-insights` | 自動化 Google Play 政策合規審查（權限宣告、資料安全 Data Safety）。 |
| 26 | **Profilers** | `profilers/android-profiler/SKILL.md` | `android-profiler` | 錄製並分析效能資料：系統追蹤、CPU 呼叫堆疊、GPU 記憶體、Java／原生堆積剖析。 |
| 27 | **Security** | `security/android-intent-security/SKILL.md` | `android-intent-security` | 審查 Intent 劫持、PendingIntent 偽造與非公開 Component 暴露。 |
| 28 | **Security** | `security/android-permissions-security/SKILL.md` | `android-permissions-security` | 審查 Android 權限最小化原則與 IPC 端點權限保護。 |
| 29 | **System** | `system/edge-to-edge/SKILL.md` | `edge-to-edge` | 把 Compose App 遷移成邊到邊顯示，修正被系統列遮住的元件、輸入法 insets 與系統列可讀性。 |
| 30 | **System** | `system/glance-appwidget-updates-and-memory/SKILL.md` | `glance-appwidget-updates-and-memory` | 處理 Glance 桌面小工具的狀態更新、背景同步與 RemoteViews 點陣圖記憶體上限。 |
| 31 | **System** | `system/glance-canonical-layouts/SKILL.md` | `glance-canonical-layouts` | 使用 Jetpack Glance 建立符合官方典範佈局之桌面 Widgets。 |
| 32 | **Testing** | `testing/testing-setup/SKILL.md` | `testing-setup` | 分析並建立測試策略：安裝測試函式庫，建立單元、UI、截圖與端對端測試的基礎設施。 |
| 33 | **TV** | `tv/leanback-to-compose-tv-migration/SKILL.md` | `leanback-to-compose-tv-migration` | 將過時的 Android TV Leanback 架構遷移至 Compose for TV。 |
| 34 | **Wear OS** | `wear/wear-compose-m3/SKILL.md` | `wear-compose-m3` | 穿戴裝置 Wear OS 專用 Material 3 Compose 佈局開發指引。 |
| 35 | **Wear OS** | `wear/wear-widgets/SKILL.md` | `wear-widgets` | 用 Glance Wear 與 Remote Compose 建立、遷移、更新與驗證 Wear OS 小工具。 |
| 36 | **XR (空間運算)** | `xr/display-glasses-with-jetpack-compose-glimmer/SKILL.md` | `display-glasses-with-jetpack-compose-glimmer` | 投影智慧眼鏡 (Display Glasses) 與 Glimmer 輕量 Compose 適配。 |
| 37 | **XR (空間運算)** | `xr/projected-hardware/SKILL.md` | `projected-hardware` | 存取與管理 Android XR 投影裝置（音訊眼鏡、顯示眼鏡）的硬體，如相機與麥克風。 |

---

## 1.1 觸發情境與輸入／輸出契約（2026-11-22 補做）

> **來源與做法**：2026-11-22 以 GitHub API 讀取 `android/skills` commit `c72942584fff970dac86ced78b367fce0c441e52`（2026-11-15，當時 `main` 的最新一筆）全部 37 個 skill 的主檔（frontmatter 與正文）。「觸發情境」摘自 frontmatter 的 `description`（含官方寫的「不要用於」）；「輸入／前置條件」摘自正文的 Prerequisites、Requirements、Codebase exploration 等段落；「輸出／完成判準」摘自 Verification、Checklist、Report、Post-implementation 等段落。
> **讀法**：官方沒有統一的「輸入／輸出」欄位，這張表是把各 skill 正文裡實際寫到的前置條件與完成判準整理出來，不是官方的正式介面定義。寫「無獨立驗證段落」表示該檔的標題裡沒有驗證、檢查清單或報告段落，不代表做完不用驗證。各 skill 的 `references/` 子檔沒有逐一讀。版本號（SDK、函式庫）是這個 commit 當下的寫法，上游會改，使用前請重讀。

| # | Skill | 觸發情境（官方 `description`） | 輸入／前置條件 | 輸出／完成判準 |
| :- | :--- | :--- | :--- | :--- |
| C1 | `agp-9-upgrade` | 把專案升級或遷移到 AGP 9；不用於 Kotlin Multiplatform 專案。 | 既有 Android 專案。先查目前的 AGP 版本，低於 9 就停下，請使用者先用 Android Studio 的 AGP Upgrade Assistant 升到最新穩定版（使用者可要求略過這一步）。 | 依 6 個步驟改完建置設定後驗證三項：Gradle IDE sync 成功、`./gradlew help` 成功、`./gradlew build --dry-run` 成功。 |
| C2 | `camerax` | 實作相機功能、處理錄影的非同步生命週期、用 CameraX 接低階硬體互通、整合 ML Kit 或 Media3 特效。 | 正文沒有前置條件段落。 | 程序性指引與標準寫法（核心流程、裝置差異、常見陷阱）；跨多檔的功能要照 `references/expert-blueprints.md` 分步實作。無獨立驗證段落。 |
| C3 | `android-for-cars-parked-apps` | 把既有的影片串流、遊戲、瀏覽器 App 遷移、建置或稽核成 Android Auto 與 Android Automotive OS 的停車時使用 App；不用於行車中使用的媒體音訊、導航範本、地點、IoT、天氣、通訊類 App。 | 既有的 adaptive App，且屬於上述三類之一。先在程式碼找 manifest、`automotive_app_desc.xml`、Gradle 檔與既有播放器；新增相依前先徵得使用者同意。 | 依 6 個步驟修改，以 `./gradlew assembleDebug` 建置並修掉錯誤；完成後告知使用者如何用 DHU 或 Automotive 模擬器測試，以及 beta 類別要先加入早期存取計畫。 |
| C4 | `appfunctions` | 在 App 裡發掘、實作、撰寫說明、測試或升級 AppFunctions（含舊版 `@AppFunction` 寫法）；不用於建立「呼叫 AppFunctions 的代理」或遠端 MCP server。 | `targetSdk` 36 以上、`compileSdk` 37 以上；用 `androidx.appfunctions:appfunctions` 與 KSP 編譯器 1.0.0-beta01 以上。 | 四步流程：發掘可開放的功能、產生 Kotlin 實作與設定、調整 KDoc 與 App 說明、用 ADB 指令測試。只做部分步驟時，要列出略過的步驟並詢問是否續做。 |
| C5 | `litert-lm` | 用 `.litertlm` 模型做裝置端的聊天、摘要或擷取功能（CPU 或 GPU）；不用於 `.tflite` 視覺、音訊、嵌入模型，也不含影像或音訊輸入、工具呼叫、NPU、模型轉換。 | Kotlin Android 專案、`minSdk` 24 以上、`litertlm-android` 相依；GPU 後端要在 manifest 加兩筆 `uses-native-library`；模型檔放在裝置的檔案系統。 | 7 個步驟（Gradle 與 manifest、選模型、放模型、初始化引擎、對話 ViewModel、Compose 畫面、引擎生命週期）。程式可編譯後，回報使用者還要自己做的步驟；附檢查清單。 |
| C6 | `litert-runtime` | 任何 Android LiteRT 或 `.tflite` 工作：Gradle 設定、推論輔助類別、GPU 失敗退回 CPU、從舊 `Interpreter` 遷移、延遲量測；不用於 `.litertlm` 生成式 LLM 或 Python 模型轉換。 | Kotlin 專案、`minSdk` 24 以上；執行環境二選一：Google Play services（預設）或隨 APK 內建。 | 5 個步驟；最後在實體裝置上先用 CPU、再用 GPU，拿同一筆固定輸入比對模型的參考輸出；附檢查清單。 |
| C7 | `ml-kit-genai-prompt-api` | 在裝置端向 Gemini Nano 送自然語言請求、使用結構化輸出、做前綴快取、最佳化既有提示詞。 | Android API level 26 以上（`minSdk` 不足就調到 26）；`com.google.mlkit:genai-prompt` 至少 1.0.0-beta4；用到 schema compiler 時 KSP 至少 2.3.6。 | 依四類規則實作或改寫（提示詞、前綴快取、生命週期、結構化輸出）；結構化輸出要先檢查裝置是否支援，並回傳 `@Generable` 型別而非字串。無獨立驗證段落。 |
| C8 | `mlkit-agent-api` | 實作對話代理、在 ViewModel 內做多輪 `AgentSession`、透過 AppFunctions 自動呼叫工具、單輪 `runSingleTurnAsync`、處理 `GenAiException`；不用於雲端 Gemini 或 Vertex AI、沒有代理迴圈的單輪文字生成、非 Android 平台。 | `com.google.mlkit:genai-agent` 與 `androidx.appfunctions` 相依；對象是 AICore Developer Preview。 | 六節的實作寫法（初始化、多輪對話與生命週期、工具呼叫、單輪執行、錯誤碼對照）。無獨立驗證段落。 |
| C9 | `android-cli` | 安裝與使用 `android` 命令列工具：建專案、安裝並執行 APK、操作裝置與模擬器、管理 SDK、檢視建置產物、算繪 Compose 預覽、查官方文件、安裝官方 skill。 | 正文沒有前置條件段落，從安裝工具開始。 | 各子指令的用法與 `android help` 的輸出內容；執行 journey 測試時，以 check、verify 開頭的動作只檢視目前畫面來判定是否符合預期。 |
| C10 | `restore-credentials` | 建立、用來登入、刪除 restore key，讓使用者換機還原後不必重新登入。 | 要有 WebAuthn relying party 伺服器（已支援 passkey 的話可沿用同一組端點）；使用 `androidx.credentials`。 | 用戶端建立、取得、清除 restore key 的實作。只做 Android 用戶端，不含伺服器端的密碼學驗證；完成後要提醒開發者後端注意事項。 |
| C11 | `verified-email` | 用 Credential Manager 把免 OTP 的已驗證電子郵件取得流程整合進 App。 | `minSdk` 28 以上、Google Play services 25.49.x 以上；先在程式碼搜尋註冊、帳號救援等畫面找整合點。 | 用戶端送出請求與解析回應的實作；完整回應字串必須送到伺服器做密碼學驗證，通過後才建立帳號或登入。 |
| C12 | `adaptive` | 讓 App 的 UI 適應手機、平板、折疊機、筆電、桌機、TV、車用與 XR：視窗大小、滑鼠與鍵盤輸入、設定變更時保留狀態、多窗格版面、桌面體驗。 | 所有畫面都用 Compose（還有 Fragment 或 View 就建議先用 XML 轉 Compose 的 skill）；使用 Navigation 3（否則建議先用 Navigation 3 的 skill）。 | 8 個步驟；先確認各種裝置尺寸都有截圖測試；最後建置並跑本機測試，截圖測試不要自動更新基準圖，請使用者看過差異後再決定。 |
| C13 | `ink-app-builder` | 做觸控筆或手指繪圖介面、筆跡算繪、內建筆刷、幾何擦除、復原與重做、用 Room 保存筆畫；不用於 XML View，自訂 `BrushFamily` 轉給 `ink-custom-brush-builder`。 | `minSdk` 26；所有 `androidx.ink` 模組版本要一致；修改建置檔前先徵得使用者同意。 | 可運作的 Compose 與 ViewModel 實作（依工作內容走 5 個步驟中對應的幾步）。無獨立驗證段落。 |
| C14 | `ink-custom-brush-builder` | 自訂 `BrushTip` 形狀、用 `BrushBehavior` 加入壓力、傾斜、速度或雜訊感應、多層筆刷、材質、輸入平滑、序列化筆刷；不用於 XML View、繪圖介面設定或內建筆刷的選擇。 | `androidx.ink` 1.1.0-alpha03 以上；修改建置檔前先徵得使用者同意。 | 完整的 Kotlin `BrushFamily`、`BrushCoat`、`BrushTip`、`BrushPaint`、`BrushBehavior` 實作。無獨立驗證段落。 |
| C15 | `jetpack-compose-performance` | 分析既有 Compose 程式碼的效能瓶頸，減少重組負擔、避免掉幀與卡頓。 | 既有的 Compose 程式碼；先確認三項基本條件：用 release 建置量測、開啟 R8、有 Baseline Profiles。 | 對 7 類規則做完整掃描（不是找到第一個問題就停）；回報問題或改程式之前，必須先讀對應的 `references/` 檔。無獨立驗證段落。 |
| C16 | `migrate-xml-views-to-jetpack-compose` | 要把一個 XML View 遷移成 Jetpack Compose；只遷移 UI。 | 一個 XML layout（使用者指定，沒指定就由 skill 挑候選）；能互動時請使用者提供畫面截圖，否則在模擬器建截圖測試取得基準圖。 | 新的 composable 並附 Compose Preview；與基準截圖比對到版面與樣式一致後，寫一個 Compose UI 測試；替換原本的用法，刪除不再被引用的 XML 與舊測試。 |
| C17 | `media3-cast-integration` | 為 App 加入 Cast 功能，或從舊版 Cast SDK 遷移到 Media3 Cast。 | Jetpack Media3 1.9.0 以上（更低版本沒有 Cast）。 | 5 個步驟：相依、manifest、播放器與 service、UI、清掉舊 Cast SDK 程式碼。無獨立驗證段落。 |
| C18 | `ios-to-android` | 任何從 iOS／Swift 程式碼移植或實作 Android 功能的工作，單一功能（藍牙、定位、計費、資料庫、單一畫面）也算；不用於純 Android 的工作。 | iOS 原始碼。分兩種模式：整個 App 的全新遷移、單一子功能遷移；子功能模式必須先查清目標程式碼的既有慣例。 | 10 個步驟；分層設編譯關卡（例如資料層完成後先跑 `./gradlew compileDebugKotlin`）；最後一步是建置驗證、移植測試、品質分級與產出 walkthrough。 |
| C19 | `navigation-3` | 安裝或遷移到 Jetpack Navigation 3，實作 deep link、多重返回堆疊、scene、條件式導覽、回傳結果、與 Hilt 和 ViewModel 整合。 | 遷移指南列的前提：先完成型別安全導覽（Navigation 2）的遷移。 | 主檔本身是遷移指南、開發文件與範例（recipes）的索引，沒有步驟，也無獨立驗證段落。 |
| C20 | `navigation-event` | 在 Compose Android 攔截返回手勢、執行預測性返回動畫；含 SDK 36 以上從舊 `BackHandler` 遷移。 | compile SDK 36 以上；使用 `ComponentActivity` 內建的 dispatcher owner，不要自己包一層。 | 5 個步驟：規劃、相依、設定 dispatcher 與輸入、處理返回與轉場、清理資源；附檢查清單。 |
| C21 | `anr-audit-and-fix` | 掃描程式碼的 ANR 風險，或分析 ANR 堆疊傾印；不用於非 ANR 的當機、掉幀、一般 CPU 剖析或 Perfetto 系統追蹤。 | 路徑 A 的輸入是原始碼；路徑 B 的輸入是 ANR trace 或堆疊傾印。 | 路徑 A：只回報通過「證明在哪個執行緒執行、證明呼叫會阻塞」的候選，被排除的另外列出並各附一行理由。路徑 B：照報告範本輸出，只對 `APP_DEFECT`、`APP_RESOURCE_OVERLOAD` 兩類提出修正。 |
| C22 | `r8-analyzer` | 想縮小 App 體積、移除多餘或過寬的 keep rule、排查 ProGuard 設定；不用於一般 Gradle 建置錯誤、Compose 效能或執行期 CPU 剖析。 | `build.gradle`、`build.gradle.kts` 與 `gradle.properties`；AGP 低於 9.3 時建議升級。 | 嚴格依 `references/REPORT_FORMAT.md` 格式的報告，指標直接取自工具產生的分析檔。 |
| C23 | `engage-sdk-integration` | 加入 Play Engage SDK 支援、產生發布程式碼、把資料類別對應到 entity、修正 SDK 相關錯誤。 | 先問開發者 App 屬於哪個 vertical、是 TV 還是行動裝置、要發布哪種 cluster；請開發者提供本地資料模型。 | 一個新目錄，內含固定的幾個類別：`Constants`、`ItemToEntityConverter`、`ClusterRequestFactory`、`EngageWorker`、`EngagePublisher`、`EngageBroadcastReceiver`。 |
| C24 | `play-billing-library-version-upgrade` | 把專案從任何舊版 Play Billing Library 升級或遷移到最新穩定版。 | 既有專案；先偵測目前使用的版本，再對照文件規劃升級路徑。 | 分段升級時每一段都跑 `./gradlew assembleDebug`；最後照版本檢查清單逐項核對，跑 `./gradlew test` 與完整的 clean build；最終報告要向開發者說明每項修改的原因。 |
| C25 | `play-policy-insights` | 對照 Google Play 政策稽核 App，涵蓋權限與 API、使用者帳號與身分、資料安全與隱私三個領域。 | App 的原始碼目錄。第一階段執行 skill 附的 `orchestrator.py init <app_dir>`；腳本失敗就必須停止，不可改用人工稽核代替。 | 由 `generate_report.py` 產生的 `compliance_report.md`，交給使用者後就停止。 |
| C26 | `android-profiler` | 錄製或分析效能資料（系統追蹤、CPU 呼叫堆疊、GPU 記憶體、Java 與原生堆積），診斷卡頓、ANR、啟動延遲、耗電、記憶體壓力等；使用者沒明說要 profiling 也適用。 | 先讀 `references/env_setup.md` 設定 `$SKILL_ROOT`；使用者的意圖不清楚時要先問，不可猜。 | 錄製走 recording orchestrator、分析走 analysis orchestrator 所定的執行計畫；主檔本身不規定產出格式。 |
| C27 | `android-intent-security` | 稽核 manifest 的元件設定，或稽核處理外來 Intent 的程式碼，防止 Intent Redirection 與未授權存取；不用於網路安全、TLS 設定或一般的執行期權限流程。 | 最低 API level 23；`androidx.core:core` 1.9.0 以上（才有 `IntentSanitizer`）。 | 套用安全強化後，必須產出結構化的「Security Hardening and Alignment Update」報告（寫進 session 的產出資料夾，或印在最終回覆）；附品質檢查清單。 |
| C28 | `android-permissions-security` | 審查 manifest、定義自訂權限、保護 Service、Receiver 與 Provider、用 Binder 驗證呼叫者的簽章與 UID、實作執行期權限流程。 | `androidx.core:core-ktx` 與 `androidx.activity:activity-ktx`（或 `fragment-ktx`）；`knownSigner` 需要 SDK 31 以上，廣播身分分享需要 SDK 34 以上。 | 9 節的稽核與修補寫法；附品質檢查清單。 |
| C29 | `edge-to-edge` | 把 Compose App 遷移成邊到邊顯示；修正被系統列遮住的元件、輸入法 insets、系統列的可讀性。 | 專案必須使用 Compose；target SDK 35 以上（不足就調到 35）。 | 3 個步驟：規劃、加入邊到邊支援、套用 insets；附檢查清單（例如每個 Activity 都呼叫 `enableEdgeToEdge()`）。 |
| C30 | `glance-appwidget-updates-and-memory` | 設定 Android 17（API 37）的 SDK 與 widget receiver、修正小工具畫面停住不更新、把圖片縮到記憶體上限內、用 FileProvider 分享 `content://` URI、修正 `ActionCallback` 與前景服務相關的當機；不用於 Glance 版面範本或 App 內的 Compose 畫面。 | Kotlin 專案、`minSdk` 26 以上、`compileSdk` 37；Jetpack Glance 1.2.0（最低 1.1.1）並啟用 Compose 編譯器外掛。 | 依詳細步驟與參考實作檔修改；附常見錯誤與修法對照。無獨立驗證段落。 |
| C31 | `glance-canonical-layouts` | 用 Android Platform Samples 的 Glance 典範版面建立主畫面小工具，或實作標準小工具版面（Check List、Image Grid、Snap Scrolling、Standard Toolbar）。 | 專案必須使用 Jetpack Glance；從參考檔清單找到要用的版面。 | 把該版面的參考檔一次複製進 App 模組；附檢查清單（manifest 有註冊、Widget Info XML 的尺寸值不改動等）。 |
| C32 | `testing-setup` | 分析並建立 App 的測試策略：安裝測試函式庫，建立單元、UI、截圖與端對端測試的基礎設施。 | 既有專案；先從 `libs.versions.toml` 或建置檔找出目前用的 DI、單元測試與 mock 框架。 | 14 個步驟；最後詢問使用者是否把分析結果與改動寫成文件（專案有 AGENTS.md 就更新它，沒有就建立 `docs/testing.md`）。 |
| C33 | `leanback-to-compose-tv-migration` | 把 Android TV App 從 Leanback、View 或 Support Fragment 遷移到 Compose for TV：瀏覽、設定、登入、影片播放等畫面，或取代 `BrowseSupportFragment` 等類別。 | 既有的 Leanback App；一律使用 `androidx.tv.material3`，不用行動版的 Material 3。 | 分五個階段遷移（基礎與設計系統、末端畫面、瀏覽與探索、詳情與播放、統一與清理），附類別對照表。無獨立驗證段落。 |
| C34 | `wear-compose-m3` | 建立、更新或遷移（從 Material 2.5 或 Horologist）Wear OS 的 Compose Material3 App。 | 直接讀 `gradle/libs.versions.toml` 或 `build.gradle.kts` 找目前版本（不要跑 `./gradlew dependencies`）；取得 Material3 最新穩定版號。 | 依官方遷移指南的元件對照改寫；重構前先做 Gradle sync 或 `./gradlew assembleDebug`；截圖測試預期會失敗，以 Material3 的預設值為準，不要硬調回舊畫面。 |
| C35 | `wear-widgets` | 實作 `GlanceWearWidget`、Remote Compose UI、widget provider XML、選擇器預覽圖，或把舊的 ProtoLayout Tile 遷移成 Wear OS 小工具；不用於手機主畫面小工具、錶面 complication 或全螢幕的 Wear OS activity。 | 先查出三個函式庫的最新版本（不要跑 `./gradlew dependencies`）；在模組內搜尋既有的 `TileService` 或 `GlanceWearWidget`。 | `./gradlew :app:assembleDebug` 編譯與連結無誤；專案有單元測試時跑 `./gradlew :app:testDebugUnitTest` 並全數通過。 |
| C36 | `display-glasses-with-jetpack-compose-glimmer` | 用 Jetpack Compose Glimmer 為顯示眼鏡開發投影式的 Android XR App；不用於沒有顯示器的音訊眼鏡、非眼鏡的 XR 頭戴裝置、手機與平板的 Material 3 UI。 | `compileSdk` 37 以上；`androidx.xr.glimmer:glimmer` 等相依（先看 `gradle/libs.versions.toml`，不可猜版本號）。 | 四節的做法：設定相依、精簡 UI 並對應輸入控制、用 Glimmer 建置、整合系統 UI。無獨立驗證段落。 |
| C37 | `projected-hardware` | 為智慧眼鏡開發時要存取相機、麥克風等硬體、處理眼鏡專屬的執行期權限，或用 projected context 管理連線生命週期。 | `compileSdk` 36 以上。 | 主檔指向必須先讀的參考文件（連線與生命週期、硬體權限、相機與音訊存取）。無獨立驗證段落。 |

---

## 2. 重點剖析一：XML View 遷移至 Jetpack Compose 現代防幻覺規範

> **2026-11-21 更正**：2.3 節的三點是本 repo 依一般 Compose 開發慣例整理的，**不是官方 skill 的原文規則**。以關鍵字搜尋該 skill 目錄下全部 Markdown（2026-11-21），找不到 `kotlinx.android.synthetic`、`rememberSaveable`、`derivedStateOf`、`StateFlow`；找得到的只有 `findViewById`、`ViewBinding`、`LazyColumn`。2026-11-22 補上 2.1、2.2 兩節，只列官方 skill 實際涵蓋的內容並附檔案路徑（路徑相對於 `android/skills` commit `c72942584fff970dac86ced78b367fce0c441e52` 的 repo 根目錄）。

### 2.1 官方遷移清單：`migrate-xml-views-to-jetpack-compose` 的 10 個步驟

主檔：`jetpack-compose/migration/migrate-xml-views-to-jetpack-compose/SKILL.md`。官方定的範圍是「一次遷移一個 XML layout、只遷移 UI」，目標是畫面與原本一致、功能不變。下表的「官方參考檔」路徑都在 `jetpack-compose/migration/migrate-xml-views-to-jetpack-compose/` 之下。

| 步驟 | 官方內容 | 官方參考檔 |
| :- | :--- | :--- |
| 1 | 找出最適合遷移的 XML 候選（使用者已指定就跳過）。 | `references/identify-optimal-xml-candidate.md` |
| 2 | 分析該 XML View 的結構、階層與周邊專案脈絡。 | `references/analysis-of-the-project-and-layout.md` |
| 3 | 依前兩步的結果產生遷移計畫；能互動時先給使用者核可。 | 主檔本身 |
| 4 | 取得 XML 畫面的基準截圖：請使用者提供，或在模擬器建截圖測試；兩者都做不到就略過。 | 主檔本身 |
| 5 | 檢查並補上 Compose 相依與編譯器設定，跑一次 sync 確認相依可解析。 | `references/android/develop/ui/compose/setup-compose-dependencies-and-compiler.md` |
| 6 | 設定 Compose 主題：只做這個 XML 候選需要的最少部分，不遷移整個主題，保留原本的 XML 主題以便互通。 | `references/android/develop/ui/compose/designsystems/migrate-xml-theme-to-compose.md` |
| 7 | 把 XML layout 轉成 Compose，並為新的 composable 加上 Compose Preview。 | `references/xml-layout-migration.md` |
| 8 | 把原本用到該 XML 的地方換成新的 composable（Compose 放進 View，或 View 放進 Compose）。 | `references/android/develop/ui/compose/migrate/interoperability-apis/compose-in-views.md`、`references/android/develop/ui/compose/migrate/interoperability-apis/views-in-compose.md` |
| 9 | 拿步驟 4 的基準截圖比對新 composable 的 Preview（不比文字內容，只看版面與樣式），調到一致後寫 Compose UI 測試。 | 主檔本身 |
| 10 | 刪除已遷移的 XML 檔與相關舊測試；只刪專案其他地方不再引用的。 | 主檔本身 |

步驟 8、9 的順序以主檔「Detailed steps」為準；同一份主檔的摘要清單把這兩步寫成相反順序（先驗證、再替換用法），這是官方文件自己的不一致。

### 2.2 其他官方 skill 裡與 Compose 遷移有關的部分

| 官方 skill | 涵蓋的遷移 | 檔案路徑 |
| :--- | :--- | :--- |
| `leanback-to-compose-tv-migration` | Android TV 的 Leanback、View、Support Fragment 遷移到 Compose for TV；五階段遷移策略與類別對照表。 | `tv/leanback-to-compose-tv-migration/SKILL.md` |
| `wear-compose-m3` | Wear OS 從 Material 2.5 或 Horologist 遷移到 Compose Material3。 | `wear/wear-compose-m3/SKILL.md`、`wear/wear-compose-m3/references/android/training/wearables/compose/migrate-to-material3.md` |
| `ios-to-android` | SwiftUI 畫面與版面移植成 Compose（整個 iOS 遷移流程的其中一部分）。 | `migration/ios-to-android/SKILL.md`、`migration/ios-to-android/references/ui-layout-swiftui-to-compose.md` |
| `navigation-event` | Compose 裡從舊的 `BackHandler` 遷移到 `NavigationBackHandler`（SDK 36 以上）。 | `navigation/navigation-event/SKILL.md` |
| `edge-to-edge` | 既有的 Compose App 遷移成邊到邊顯示。 | `system/edge-to-edge/SKILL.md` |
| `adaptive` | 本身不做 XML 遷移；前置條件要求所有畫面都已是 Compose，否則建議先用 XML 轉 Compose 的 skill。 | `jetpack-compose/adaptive/SKILL.md` |

### 2.3 本 repo 延伸（非官方內容）

AI 生成 Android 代碼時常見的錯誤，是混合傳統 View 體系與現代 Compose 語法。以下是本 repo 整理的遷移紀律【本 repo 延伸】，官方 skill 沒有這些條文：

1. **嚴禁 View 體系毒性殘留**：
   - 徹底廢除 `findViewById`、`ViewBinding` 與早已被 Kotlin 廢棄的 `kotlinx.android.synthetic`。
   - 嚴禁在 Composable 內部直接持有 `Context` 物件或儲存靜態 UI 狀態。
2. **狀態單向流 (UDF, Unidirectional Data Flow)**：
   - UI 狀態必須以 `StateFlow` 或 `State<T>` 由 ViewModel 向下傳遞，事件（點擊、輸入）透過 Lambda 回呼向上回傳。
   - 使用 `rememberSaveable` 確保螢幕旋轉與進程重啟時狀態不遺失。
3. **效能重組陷阱防範**：
   - 避免在 Composable 函式體中執行耗時計算，必須使用 `remember(key) { ... }` 或 `derivedStateOf { ... }` 進行快取。
   - 列表結構嚴格禁止使用 `Column` + `forEach` 載入大量動態資料，必須強制使用 `LazyColumn` / `LazyRow` 並指定穩定的 `key`。

---

## 3. 重點剖析二：Google Play Billing 與 Policy Insights 政策合規審查防線

> **2026-11-21 查證**：Billing 的 AIDL 淘汰、`ProductDetails`、Base Plan 與 3 天內確認購買，在 `play-billing-library-version-upgrade/references/` 找得到對應內容；「Data Safety」見於 `play-policy-insights`。第 2 點列的三個權限名稱是本 repo 舉的例子（官方資源檔只出現 `ACCESS_FINE_LOCATION`）。

Play 商店審查是 Android 開發者上架的最痛門檻。`play-billing-library-version-upgrade` 與 `play-policy-insights` 提供確定性靜態規則：

1. **Play Billing Library 強制升級合規**：
   - 淘汰所有舊版 AIDL 介面與舊版 BillingClient v4/v5 語法。
   - 訂閱制（Subscription）必須完整處理 `ProductDetails`、多重定價方案（Base Plans）與優惠方案（Offers）。
   - 交易確認閉環：購買完成後必須在 3 天內呼叫 `AcknowledgePurchaseParams`，否則 Google Play 將自動退款。
2. **Data Safety 與權限宣告一致性**：
   - `AndroidManifest.xml` 中宣告的敏感權限（如 `ACCESS_FINE_LOCATION`、`READ_MEDIA_IMAGES`、`POST_NOTIFICATIONS`），在靜態代碼中必須存在真實調用點與執行階段詢問邏輯。
   - 嚴格禁止存在宣告卻未在 Play Console 資料安全表單中說明的敏感資料收集行為。

---

## 4. 總結

Google 官方目前（2026-11-16）收錄 37 個 Agent Skills，證明了「領域專用規則檔（Domain Skills）」能有效終結 LLM 依賴過時訓練資料的盲區。本手冊盤點的清單為現代 Android 跨終端與政策合規提供了確定性的工程基準。
