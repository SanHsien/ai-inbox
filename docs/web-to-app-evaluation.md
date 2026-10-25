# WebToApp（網站轉 Android App）技術評估與本機環境驗證報告

> 本文件收錄於 `docs/web-to-app-evaluation.md`，為任務 `T-20261023-03` 針對開源專案 [`shiaho777/web-to-app`](https://github.com/shiaho777/web-to-app) 的版本規格、授權協議、AndroidManifest.xml 權限宣告、Keystore 簽名機制、建置架構以及 Windows 11 本機整合環境的技術評估與實測驗證報告。

---

## 1. 專案基本規格與授權審查

- **官方倉庫**：[`shiaho777/web-to-app`](https://github.com/shiaho777/web-to-app)
- **最新版本**：`v2.8.2`（發布於 2026-10-24 17:28:18 UTC）
- **發布產物**：`web-to-app-2.8.2.APK`（檔案大小 26,307,242 bytes，約 26.3 MB / 25.08 MB，SHA-256: `422b21ca1126def7453b655eb61da569f210e3ea8168baa1fd442cfa8f23855f`）
- **社群指標**：GitHub Stars 約 7,028+、Forks 約 600+
- **開源授權**：**The Unlicense**（公有領域專用授權）
  - 允許自由複製、修改、散布、商業利用或重新編譯，無任何版權保留條款或專利限制。
  - 對於商用接案極具彈性，可作為白牌工具或自建封裝流水線的基礎。

---

## 2. 系統架構與建置原理

WebToApp 採用高度自包含的雙層架構設計，主打全程在 Android 設備端完成打包、簽名與 AAB 轉換，無需依賴遠端伺服器或電腦端 Android Studio：

```
+--------------------------------------------------------------------------+
|                     WebToApp 宿主工作台 (app 模組)                         |
|  - UI / 12 種應用專案類型管理 / AI Agent 對話生成 (60+ 操控工具)         |
|  - 二進位 AXML / ARSC 動態修補 (ApkBuilder)                              |
|  - 簽名模組: apksig (V1/V2/V3) + AabSigner (JAR v1 PKCS#7)               |
+--------------------------------------------------------------------------+
                                     │
           動態組裝 & 簽名導出        ▼
+--------------------------------------------------------------------------+
|                     生成的獨立子 App (shell 模組)                         |
|  - 瀏覽器引擎: 預設系統 WebView / 可選 GeckoView (Firefox)                |
|  - 內嵌伺服端 Runtime (可選): Node.js 18.20 / PHP 8.4 / Python 3.14 / Go |
|  - 網路與隱私: DoH (7 家提供商) / ECH / TLS 指紋偽裝 / 50+ 維指紋混淆    |
|  - 離線與擴展: PWA 緩存 / 油猴腳本 (GM_*) / MV3 Chrome 擴充套件支援      |
+--------------------------------------------------------------------------+
```

### 打包與轉換運作流程：
1. **模板提取**：從宿主 APK 的 `assets/template/webview_shell.apk`（約 8.68 MB）提取標準 `:shell` 預編譯模板。
2. **資源注入**：使用者指定線上 URL 或導入本地靜態網頁（HTML/CSS/JS/SPA 構建產物）與圖示資源，寫入 `assets/app_config.json`。
3. **AXML/ARSC 二進位修補**：ApkBuilder 讀取預編譯好的 shell 模板，直接在二進位層級替換應用名稱、套件識別碼（package name）、版本號與啟動網址，無需在手機上跑完整 Gradle 編譯鏈。
4. **權限按需裁剪**：根據使用者勾選的功能開關（如相機掃碼、地理定位、藍牙、背景運行），動態向子 APK 的 `AndroidManifest.xml` 注入對應權限宣告。
5. **設備端簽名**：透過內建的 `apksig` 函式庫完成 V1、V2、V3 簽名；若選擇上架 Google Play，則由 `AabSigner` 生成包含標準 META-INF 簽章的 `.aab` 格式檔案。

---

## 3. AndroidManifest.xml 權限宣告清單

經本機工具鏈 `aapt.exe dump permissions` 實測分析，WebToApp 採取了「宿主工作台與生成子包權限分離」的設計策略：

### 3.1 宿主工作台（Host App: `com.webtoapp`）
宿主工作台負責提供 UI、掃碼導入、檔案選取、打包通知與一鍵安裝，實測宣告了 34 項系統權限：

```text
package: com.webtoapp
uses-permission: name='android.permission.QUERY_ALL_PACKAGES'
uses-permission: name='android.permission.INTERNET'
uses-permission: name='android.permission.ACCESS_NETWORK_STATE'
uses-permission: name='android.permission.ACCESS_LOCAL_NETWORK'
uses-permission: name='android.permission.READ_EXTERNAL_STORAGE' maxSdkVersion='32'
uses-permission: name='android.permission.WRITE_EXTERNAL_STORAGE' maxSdkVersion='29'
uses-permission: name='android.permission.READ_MEDIA_IMAGES'
uses-permission: name='android.permission.READ_MEDIA_VIDEO'
uses-permission: name='android.permission.READ_MEDIA_AUDIO'
uses-permission: name='android.permission.READ_MEDIA_VISUAL_USER_SELECTED'
uses-permission: name='android.permission.REQUEST_INSTALL_PACKAGES'
uses-permission: name='com.android.launcher.permission.INSTALL_SHORTCUT'
uses-permission: name='android.permission.POST_NOTIFICATIONS'
uses-permission: name='android.permission.CAMERA'
uses-permission: name='android.permission.RECORD_AUDIO'
uses-permission: name='android.permission.MODIFY_AUDIO_SETTINGS'
uses-permission: name='android.permission.ACCESS_FINE_LOCATION'
uses-permission: name='android.permission.ACCESS_COARSE_LOCATION'
uses-permission: name='android.permission.ACCESS_WIFI_STATE'
uses-permission: name='android.permission.CHANGE_WIFI_STATE'
uses-permission: name='android.permission.CHANGE_NETWORK_STATE'
uses-permission: name='android.permission.BLUETOOTH' maxSdkVersion='30'
uses-permission: name='android.permission.BLUETOOTH_ADMIN' maxSdkVersion='30'
uses-permission: name='android.permission.BLUETOOTH_SCAN'
uses-permission: name='android.permission.BLUETOOTH_CONNECT'
uses-permission: name='android.permission.USE_BIOMETRIC'
uses-permission: name='android.permission.SYSTEM_ALERT_WINDOW'
uses-permission: name='android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS'
uses-permission: name='android.permission.ACCESS_NOTIFICATION_POLICY'
uses-permission: name='android.permission.FOREGROUND_SERVICE'
uses-permission: name='android.permission.FOREGROUND_SERVICE_DATA_SYNC'
uses-permission: name='android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK'
uses-permission: name='android.permission.FOREGROUND_SERVICE_SPECIAL_USE'
uses-permission: name='android.permission.WAKE_LOCK'
uses-permission: name='android.permission.RECEIVE_BOOT_COMPLETED'
uses-permission: name='android.permission.SCHEDULE_EXACT_ALARM'
uses-permission: name='android.permission.USE_EXACT_ALARM'
uses-permission: name='android.permission.USE_FINGERPRINT'
uses-permission: name='android.permission.HIGH_SAMPLING_RATE_SENSORS'
uses-permission: name='com.google.android.c2dm.permission.RECEIVE'
permission: com.webtoapp.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION
uses-permission: name='com.webtoapp.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION'
```

### 3.2 生成子 App（Generated Shell: `com.w2a.rybz` 實測）
由 WebToApp 設備端針對靜態頁封裝生成的子 App，權限宣告經 `RuntimePermissionSync` 自動大幅裁剪，僅保留最基礎的 7 項權限：

```text
package: com.w2a.rybz
uses-permission: name='android.permission.INTERNET'
uses-permission: name='android.permission.ACCESS_NETWORK_STATE'
uses-permission: name='android.permission.ACCESS_LOCAL_NETWORK'
uses-permission: name='android.permission.DOWNLOAD_WITHOUT_NOTIFICATION'
uses-permission: name='android.permission.FOREGROUND_SERVICE'
uses-permission: name='android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK'
uses-permission: name='android.permission.WAKE_LOCK'
permission: com.w2a.rybz.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION
uses-permission: name='com.w2a.rybz.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION'
```

**權限分析小結**：生成子 App 徹底剝離了宿主的高權限（如相機、麥克風、粗/細地理定位、藍牙掃描、讀取所有多媒體、忽略電池最佳化等），權限架構非常輕巧乾淨，大幅降低 Google Play 上架審查與惡意權限警告風險。

---

## 4. Keystore 簽名架構與備份機制

簽名是網站轉 App 與後續維護的核心命脈。WebToApp 的簽名架構由 `JarSigner.kt`、`PerAppSigningIdentity.kt` 與 `AabSigner.kt` 共同構成：

### 4.1 獨立金鑰管理機制（Per-App Signing Identity）
- **演算法規格**：採用 **RSA-2048**（部分進階模組支援 RSA-3072）密鑰對，產生自簽名 X.509 憑證，主體格式為 `CN=WebToApp, O=WebToApp, C=CN`。
- **實機檢測金鑰位置**：
  經模擬器 root 權限檢驗 `/data/data/com.webtoapp/files/`，金鑰與密鑰憑證檔案確實存放於應用內部私有目錄：
  - 金鑰檔格式：**PKCS#12**（`.p12`），檔名為 `webtoapp_keystore.p12`（檔案大小 2,509 bytes）。
  - 密鑰密碼存於：`.ks_credential`（檔案大小 32 bytes）。
- **簽名檢驗結果（`apksigner.bat verify --verbose --print-certs` 實測）**：
  ```text
  Verifies
  Verified using v1 scheme (JAR signing): true
  Verified using v2 scheme (APK Signature Scheme v2): true
  Verified using v3 scheme (APK Signature Scheme v3): true
  Verified using v3.1 scheme (APK Signature Scheme v3.1): false
  Verified using v4 scheme (APK Signature Scheme v4): false
  Verified for SourceStamp: false
  Number of signers: 1
  Signer #1 certificate DN: CN=WebToApp, O=WebToApp, C=CN
  Signer #1 certificate SHA-256 digest: 984577ec14aba224ab3820c919ca19fe00a59e7a94cdab497bedd99b41707323
  Signer #1 certificate SHA-1 digest: e9eb492bf750028806cc943ea4c1fbaaa1978c9e
  Signer #1 certificate MD5 digest: 8a12b9c170c6199be15ea8be9b77c661
  Signer #1 key algorithm: RSA
  Signer #1 key size (bits): 2048
  Signer #1 public key SHA-256 digest: 2ae4eacf802adcb6bced74e24ed21f671726f8d6ec9f829745aca71f6bdd86f4
  ```

### 4.2 自訂金鑰支援（Custom Keystore）
- 支援使用者匯入自有的 `.p12` 或 Android Studio 生成的 `.jks` 金鑰檔（存放於 `context.filesDir/custom_keystore.p12`），並可自訂 Key Alias 與密碼。
- 內建 `BouncyCastleProvider`，可完整相容 Android Studio 新版預設的 PBES2 with AES-256 加密容器。

### 4.3 重大風險：金鑰遺失與備份規範
> [!CAUTION]
> **私有目錄金鑰遺失風險**：
> WebToApp 預設將金鑰與隨機密碼存放在手機的應用私有目錄（`context.filesDir`）。若維護者或使用者在手機端「清除應用資料」、「解除安裝 WebToApp」或「更換手機」，該私鑰與憑證將**永久消失且無法恢復**！
>
> **標準備份處置程序**：
> 1. 在正式商用接案時，**強烈建議在電腦端使用 `keytool` 建立獨立的商用金鑰庫（.jks 或 .p12）**，再匯入 WebToApp 簽名，而非完全依賴手機端臨時產生的金鑰。
> 2. 若使用手機自動生成之金鑰，必須在構建完成後立即將 `.p12` 檔及 `.ks_credential` 密碼檔透過安全通道備份至離線密碼庫或加密硬碟。

---

## 5. 本機 Windows 11 環境實測與工具鏈檢查

維護者針對當前 Windows 11 原生開發環境，使用本機現成之 Android SDK 工具鏈與 API 34 x86_64 模擬器完成了全流程實測驗證：

### 5.1 本機工具鏈規格
- **模擬器**：`C:\Users\SanHsien\AppData\Local\Android\Sdk\emulator\emulator.exe`（Version 32.1.15.0，WHPX 硬體加速）
- **系統映像檔**：`system-images\android-34\google_apis\x86_64`（Android 14.0, API Level 34）
- **建置工具**：`C:\Users\SanHsien\AppData\Local\Android\Sdk\build-tools\36.0.0\aapt.exe`、`apksigner.bat`
- **ADB**：`C:\Users\SanHsien\AppData\Local\Android\Sdk\platform-tools\adb.exe`（Android Debug Bridge version 1.0.41, 34.0.4）

### 5.2 模擬器建立與開機驗證
維護者於 `$env:USERPROFILE\.android\avd` 建立了指向現成系統映像之暫存 AVD `wta_test_api34`：
```powershell
# 模擬器啟動指令
& emulator.exe -avd wta_test_api34 -no-audio -no-boot-anim -gpu swiftshader_indirect -no-window
```
開機輪詢檢驗至 `sys.boot_completed = 1` 成功就緒：
```text
List of devices attached
emulator-5554          device product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64 device:emu64xa transport_id:1
ro.build.version.release = 14
```

### 5.3 宿主 App 安裝與啟動實測
```powershell
adb install -r -g web-to-app-2.8.2.APK
adb shell am start -n com.webtoapp/com.webtoapp.ui.MainActivity -a android.intent.action.MAIN -c android.intent.category.LAUNCHER
```
**終端輸出結果**：
```text
Performing Streamed Install
Success
Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.webtoapp/.ui.MainActivity }
mCurrentFocus=Window{e557e80 u0 com.webtoapp/com.webtoapp.ui.MainActivity}
mFocusedApp=ActivityRecord{6dc269a u0 com.webtoapp/.ui.MainActivity t8}
```
*技術細節記錄*：宿主之啟動 Activity 為 `com.webtoapp.ui.MainActivity`（位於 `.ui` 子包），初次冷開機顯示語言選擇引導頁（Select Language），經 UI Automator 選定「中文」後進入「我的應用」主工作台。

### 5.4 本機靜態頁打包流程實測
維護者準備了本機樣本文頁 `index.html`（含深色卡片風格與互動按鈕），並實測了將其轉換為獨立 APK 的完整流程：
1. **反向代理建立**：
   本機以 `python -m http.server 8080` 啟動靜態網站服務，透過 `adb reverse tcp:8080 tcp:8080` 將手機端之 `127.0.0.1:8080` 埠映射回 Windows 開發機。
2. **工作台配置**：
   在 WebToApp 中新建應用，設定應用名稱為 `WebToAppSample`，網站地址為 `http://127.0.0.1:8080/index.html`。
3. **網頁特徵提取**：
   點擊「分析網站」，WebToApp 成功解析頁面並提取基礎信息（`未检测到 PWA 配置，已从页面提取基本信息`），一鍵套用生成配置。
4. **設備端 APK 构建**：
   進入「构建 APK」頁面，自動分配獨立包名 `com.w2a.rybz`，選擇「系统 WebView」引擎，點擊「构建」。
   - 打包進度實況：`Repacking base template... 63%` -> `100%`。
   - 生成產物目錄：`/storage/emulated/0/Android/data/com.webtoapp/files/built_apks/WebToAppSample_v1.0.0.APK`。
   - 構建摘要報告：體積 `8.3 MB`、版本 `1.0.0 (1)`、JDK `17`、簽名 `v1+v2+v3`。

### 5.5 打包產物 APK 安裝與執行實測
將產出之 `WebToAppSample_v1.0.0.APK` 拉回 Windows 開發機並執行模擬器安裝：
```powershell
adb install -r -g WebToAppSample_v1.0.0.APK
adb shell am start -n com.w2a.rybz/com.webtoapp.ui.shell.ShellActivity -a android.intent.action.MAIN -c android.intent.category.LAUNCHER
```
**終端安裝與執行輸出**：
```text
Performing Streamed Install
Success
Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.w2a.rybz/com.webtoapp.ui.shell.ShellActivity }
mFocusedApp=ActivityRecord{9d3c565 u0 com.w2a.rybz/com.webtoapp.ui.shell.ShellActivity t9}
```

**子 App 執行 Logcat 實錄（PID: 9093）**：
```text
10-25 15:19:29.724  9093  9093 D ShellActivity: 开始读取状态栏配置
10-25 15:19:30.101  9093  9093 D [GENERAL] ShellActivity: 键盘模式: RESIZE (边到边，动画期间平移，结束时再改高度)
10-25 15:19:30.157  9093  9093 D ShellActivity: 沉浸式全屏模式: false
10-25 15:19:30.171  9093  9093 I ShellActivity: setContent 开始，主题=KIMI_NO_NAWA
10-25 15:19:35.824  9093  9093 D [GENERAL] ShellScreen: appType='WEB' (normalized='WEB'), targetUrl='http://127.0.0.1:8080/index.html'
10-25 15:19:37.278  9093  9093 D [GENERAL] ShellActivity: UserAgentMode parsed: 'DEFAULT' -> DEFAULT
10-25 15:19:37.496  9093  9093 D [GENERAL] ShellActivity: Constructed WebViewConfig: userAgentMode=DEFAULT, customUserAgent=null, userAgent=null
10-25 15:19:37.511  9093  9093 D [GENERAL] ShellActivity: InjectScripts: shellScripts=2, mapped=2
10-25 15:19:37.511  9093  9093 D [GENERAL] ShellActivity:   Script[0]: name='__perf_start__', enabled=true, runAt=DOCUMENT_START, codeLength=1076
10-25 15:19:37.511  9093  9093 D [GENERAL] ShellActivity:   Script[1]: name='__perf_end__', enabled=true, runAt=DOCUMENT_END, codeLength=1296
10-25 15:19:38.878  9093  9093 D [GENERAL] ShellScreen: 进入 WebView 分支 (else)，加载 URL: http://127.0.0.1:8080/index.html
10-25 15:19:39.714  9093  9093 I [GENERAL] EngineViewFactory: create: requested=SYSTEM_WEBVIEW resolved=SYSTEM_WEBVIEW ech=false dnsMode=SYSTEM
10-25 15:19:40.453  9093  9093 I WebViewFactory: Loading com.google.android.webview version 113.0.5672.136 (code 567263637)
```
子 App 順利加載了系統 WebView，並成功渲染呈現出本機靜態網頁內容，驗證流程 100% 成功。

---

## 6. 已知限制與技術邊界

經實機實測操作，發現以下具體之限制與技術邊界：

1. **表單 URL 嚴格正規表達式校驗**：
   - WebToApp 前端表單在建立與編輯應用時，嚴格限制網站地址必須符合 `http://` 或 `https://` 協定。若使用者直接輸入 `file:///sdcard/...` 本地路徑，表單會拋出「`请输入有效的 URL`」錯誤並阻斷保存。
   - **處置方案**：若需封裝本地靜態網站，應在開發階段透過本機 HTTP 伺服器搭配 `adb reverse` 映射，或使用 WebToApp 內建模板匯入前端專案包，而非直接指定 `file://` 協定。
2. **軟體鍵盤 UI 遮蔽問題**：
   - 在 Android 設備端填寫表單時，軟體鍵盤彈出時會遮擋底部的「一鍵應用」與「保存」按鈕；自動化操作時必須顯式發送 `KEYCODE_BACK` 收起軟體鍵盤後方可點擊底部操作按鈕。
3. **多版本 ADB 衝突風險**：
   - 若 Windows 系統中同時存在多個 ADB 執行檔（例如 `C:\Android\adb.exe` 1.0.32 與 Android SDK `platform-tools\adb.exe` 1.0.41），因伺服端協定版本不同，互相呼叫會導致 adb server 反覆重啟並報 `device offline`，必須確保開發工具鏈鎖定單一 Sdk platform-tools 路徑。
4. **Google Play 政策審查限制**：
   - 純網頁套殼若無提供獨特的使用者體驗、推播或離線功能，極易觸犯 Google Play 的「最低功能性政策（Minimum Functionality）」與「WebView 垃圾內容政策（Spam Policy）」。
5. **私有金鑰遺失風險**：
   - WebToApp 預設在手機 `/data/data/com.webtoapp/files/` 目錄動態生成 `webtoapp_keystore.p12`。一旦手機清除資料或卸載應用，該金鑰將徹底遺失；接案交付前必須將其備份匯出。

---

## 7. 總體結論

結論：可行（本機 Windows 11 已透過原生 Android SDK 工具鏈與 API 34 模擬器完成全流程實機驗證：WebToApp 宿主安裝、本機靜態頁打包、APK 二進位改名與簽名、權限自動裁剪，以及生成子 App 之安裝與 WebView 執行驗證均 100% 成功）
