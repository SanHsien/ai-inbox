# Google Android 官方 Skills 深度盤點與現代 Android 開發防幻覺手冊

> 本手冊收錄於 `docs/android-official-skills-anti-hallucination.md`，深度解構 Google Android 官方開源之 [`android/skills`](https://github.com/android/skills) 倉庫。
> **實測說明**：社群文章原稱「官方 30 個 Skills」，經維護者直接檢驗官方 GitHub 最新倉庫內容，目前已實質擴充至 **33 個 Skills**。本手冊完整收錄 33 個 Skills 之相對路徑、職責與防幻覺契約。以 ai-inbox 範本形式交付。

---

## 1. 官方 33 個 Skills 全景盤點

| # | 分類領域 | 官方相對路徑 (來源路徑) | Skill 名稱 | 核心職責與防幻覺重點 |
| :- | :--- | :--- | :--- | :--- |
| 1 | **Build System** | `build-system/agp/agp-9-upgrade/SKILL.md` | `agp-9-upgrade` | 升級至 Android Gradle Plugin 9.0，修正 Gradle API 廢棄語法與命名空間宣告。 |
| 2 | **Camera** | `camera/camerax/SKILL.md` | `camerax` | 指導 CameraX 生命週期綁定、預覽與影像分析，防止舊 Camera1 API 幻覺。 |
| 3 | **Cars (車載)** | `cars/android-for-cars-parked-apps/SKILL.md` | `android-for-cars-parked-apps` | 適配車載 Android Auto / Automotive 停車模式下的影音與瀏覽器應用。 |
| 4 | **Device AI** | `device-ai/appfunctions/SKILL.md` | `appfunctions` | 識別並整合 Android 系統級 AppFunctions 語意工作流。 |
| 5 | **Device AI** | `device-ai/litert/litert-lm/SKILL.md` | `litert-lm` | 於裝置端利用 LiteRT-LM 執行開源大型語言模型 (On-Device LLM)。 |
| 6 | **Device AI** | `device-ai/litert/litert-runtime/SKILL.md` | `litert-runtime` | 配置並執行 `.tflite` 模型之裝置端硬體加速推論 (NPU/GPU)。 |
| 7 | **Device AI** | `device-ai/ml-kit-genai-prompt-api/SKILL.md` | `ml-kit-genai-prompt-api` | 整合 ML Kit GenAI Prompt API，執行裝置端摘要與智慧問答。 |
| 8 | **DevTools** | `devtools/android-cli/SKILL.md` | `android-cli` | 指導安裝與操作 `android` 官方命令列工具（專案建置、模擬器操作）。 |
| 9 | **Identity** | `identity/restore-credentials/SKILL.md` | `restore-credentials` | 實現 Android 換機無縫登入與憑證自動還原 (Restore Credentials)。 |
| 10 | **Identity** | `identity/verified-email/SKILL.md` | `verified-email` | 安全取得經過驗證的使用者電子信箱工作流。 |
| 11 | **Compose** | `jetpack-compose/adaptive/SKILL.md` | `adaptive` | 利用 Adaptive Navigation Suite 適配折疊螢幕、平板與多視窗佈局。 |
| 12 | **Compose** | `jetpack-compose/jetpack-compose-performance/SKILL.md` | `jetpack-compose-performance` | 診斷與消除不必要的 Recomposition（重組），使用 Stability 標記。 |
| 13 | **Compose** | `jetpack-compose/migration/migrate-xml-views-to-jetpack-compose/SKILL.md` | `migrate-xml-views-to-jetpack-compose` | 結構化將傳統 XML Layout 遷移為現代 Jetpack Compose 函式。 |
| 14 | **Compose** | `jetpack-compose/theming/styles/SKILL.md` | `styles` | 整合 Jetpack Compose Styles API 與 Material Theme 3 樣式系統。 |
| 15 | **Media** | `media/media3-cast-integration/SKILL.md` | `media3-cast-integration` | 整合 Jetpack Media3 與 Google Cast 投影串流。 |
| 16 | **Navigation** | `navigation/navigation-3/SKILL.md` | `navigation-3` | 遷移至 Jetpack Navigation 3 現代型別安全 (Type-Safe) 導航架構。 |
| 17 | **Navigation** | `navigation/navigation-event/SKILL.md` | `navigation-event` | 攔截返回手勢並實現 Android 14+ 預測性返回 (Predictive Back) 動畫。 |
| 18 | **Performance** | `performance/anr-audit-and-fix/SKILL.md` | `anr-audit-and-fix` | 審查主執行緒阻塞風險並解析 ANR 堆疊傾印 (Stack Dump)。 |
| 19 | **Performance** | `performance/r8-analyzer/SKILL.md` | `r8-analyzer` | 分析 R8 ProGuard 混淆規則，移除冗餘 Keep Rules 並縮小 APK 體積。 |
| 20 | **Play 生態** | `play/engage-sdk-integration/SKILL.md` | `engage-sdk-integration` | 整合 Google Play Engage SDK 提升個人化內容推薦曝光。 |
| 21 | **Play 生態** | `play/play-billing-library-version-upgrade/SKILL.md` | `play-billing-library-version-upgrade` | 升級 Play Billing Library 至最新版，消除舊版週期性扣款過期寫法。 |
| 22 | **Play 生態** | `play/play-policy-insights/SKILL.md` | `play-policy-insights` | 自動化 Google Play 政策合規審查（權限宣告、資料安全 Data Safety）。 |
| 23 | **Profilers** | `profilers/android-profiler/SKILL.md` | `android-profiler` | 利用 Android Profiler 分析 CPU、Memory、Energy 瓶頸。 |
| 24 | **Security** | `security/android-intent-security/SKILL.md` | `android-intent-security` | 審查 Intent 劫持、PendingIntent 偽造與非公開 Component 暴露。 |
| 25 | **Security** | `security/android-permissions-security/SKILL.md` | `android-permissions-security` | 審查 Android 權限最小化原則與 IPC 端點權限保護。 |
| 26 | **System** | `system/edge-to-edge/SKILL.md` | `edge-to-edge` | 適配 Android 15 強制性邊到邊 (Edge-to-Edge) 與 Insets 避讓處理。 |
| 27 | **System** | `system/glance-canonical-layouts/SKILL.md` | `glance-canonical-layouts` | 使用 Jetpack Glance 建立符合官方典範佈局之桌面 Widgets。 |
| 28 | **Testing** | `testing/testing-setup/SKILL.md` | `testing-setup` | 配置 JUnit5、Robolectric 與 Compose Test 現代自動化測試環境。 |
| 29 | **TV** | `tv/leanback-to-compose-tv-migration/SKILL.md` | `leanback-to-compose-tv-migration` | 將過時的 Android TV Leanback 架構遷移至 Compose for TV。 |
| 30 | **Wear OS** | `wear/wear-compose-m3/SKILL.md` | `wear-compose-m3` | 穿戴裝置 Wear OS 專用 Material 3 Compose 佈局開發指引。 |
| 31 | **Wear OS** | `wear/wear-widgets/SKILL.md` | `wear-widgets` | 建立與更新 Wear OS 穿戴錶盤圖塊與 Glance Widgets。 |
| 32 | **XR (空間運算)** | `xr/display-glasses-with-jetpack-compose-glimmer/SKILL.md` | `display-glasses-with-jetpack-compose-glimmer` | 投影智慧眼鏡 (Display Glasses) 與 Glimmer 輕量 Compose 適配。 |
| 33 | **XR (空間運算)** | `xr/projected-hardware/SKILL.md` | `projected-hardware` | Android XR 空間硬體感知與感測器管理流程。 |

---

## 2. 重點剖析一：XML View 遷移至 Jetpack Compose 現代防幻覺規範

AI 生成 Android 代碼時最嚴重的幻覺，莫過於混合傳統 View 體系與現代 Compose 語法。官方 `migrate-xml-views-to-jetpack-compose` 確立了嚴格的遷移紀律：

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

Google 官方推出 33 個收錄完整的 Agent Skills，證明了「領域專用規則檔（Domain Skills）」能有效終結 LLM 依賴過時訓練資料的盲區。本手冊盤點的清單為現代 Android 跨終端與政策合規提供了確定性的工程基準。
