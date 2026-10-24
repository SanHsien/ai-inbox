# WebToApp（網站轉 Android App）技術評估與本機環境驗證報告

> 本文件收錄於 `docs/web-to-app-evaluation.md`，為任務 `T-20261023-03` 針對開源專案 [`shiaho777/web-to-app`](https://github.com/shiaho777/web-to-app) 的版本規格、授權協議、AndroidManifest.xml 權限宣告、Keystore 簽名機制、建置架構以及 Windows 11 本機整合環境的技術評估報告。

---

## 1. 專案基本規格與授權審查

- **官方倉庫**：[`shiaho777/web-to-app`](https://github.com/shiaho777/web-to-app)
- **最新版本**：`v2.8.2`（發布於 2026-10-24 17:28:18 UTC）
- **發布產物**：`web-to-app-2.8.2.APK`（檔案大小約 26.3 MB，SHA-256: `422b21ca1126def7453b655eb61da569f210e3ea8168baa1fd442cfa8f23855f`）
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
1. **資源注入**：使用者指定線上 URL 或導入本地靜態網頁（HTML/CSS/JS/SPA 構建產物）與圖示資源。
2. **AXML/ARSC 二進位修補**：ApkBuilder 讀取預編譯好的 shell 模板，直接在二進位層級替換應用名稱、套件識別碼（package name）、版本號與啟動網址，無需在手機上跑完整 Gradle 編譯鏈。
3. **權限按需裁剪**：根據使用者勾選的功能開關（如相機掃碼、地理定位、藍牙、背景運行），動態向子 APK 的 `AndroidManifest.xml` 注入對應權限宣告。
4. **設備端簽名**：透過內建的 `apksig` 函式庫完成 V1、V2、V3 簽名；若選擇上架 Google Play，則由 `AabSigner` 生成包含標準 META-INF 簽章的 `.aab` 格式檔案。

---

## 3. AndroidManifest.xml 權限宣告清單

經源碼審查，WebToApp 採取了「宿主工作台與生成子包權限分離」的設計策略：

### 3.1 宿主工作台（Host App: `app/src/main/AndroidManifest.xml`）
宿主工作台負責提供 UI、掃碼導入、檔案選取、打包通知與一鍵安裝，宣告了較為廣泛的系統權限：
- **網路通訊**：
  - `android.permission.INTERNET`
  - `android.permission.ACCESS_NETWORK_STATE`
  - `android.permission.ACCESS_LOCAL_NETWORK`（Android 16/17 區域網路預覽相容）
- **儲存與多媒體**：
  - `android.permission.READ_EXTERNAL_STORAGE`（maxSdkVersion 32）
  - `android.permission.WRITE_EXTERNAL_STORAGE`（maxSdkVersion 29）
  - `android.permission.READ_MEDIA_IMAGES`
  - `android.permission.READ_MEDIA_VIDEO`
  - `android.permission.READ_MEDIA_AUDIO`
  - `android.permission.READ_MEDIA_VISUAL_USER_SELECTED`
- **APK 打包與安裝核心**：
  - `android.permission.REQUEST_INSTALL_PACKAGES`（核心權限：打包完成後直接喚起系統安裝器）
  - `com.android.launcher.permission.INSTALL_SHORTCUT`（桌面捷徑生成）
- **前台與背景排程**：
  - `android.permission.POST_NOTIFICATIONS`
  - `android.permission.FOREGROUND_SERVICE`
  - `android.permission.FOREGROUND_SERVICE_DATA_SYNC`
  - `android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK`
  - `android.permission.FOREGROUND_SERVICE_SPECIAL_USE`
  - `android.permission.WAKE_LOCK`
  - `android.permission.RECEIVE_BOOT_COMPLETED`
  - `android.permission.SCHEDULE_EXACT_ALARM`
  - `android.permission.USE_EXACT_ALARM`
- **設備硬體交互**：
  - `android.permission.CAMERA`（掃描 QR Code 導入網址）
  - `android.permission.RECORD_AUDIO` / `MODIFY_AUDIO_SETTINGS`
  - `android.permission.ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION`
  - `android.permission.ACCESS_WIFI_STATE` / `CHANGE_WIFI_STATE` / `CHANGE_NETWORK_STATE`
  - `android.permission.BLUETOOTH` / `BLUETOOTH_ADMIN` / `BLUETOOTH_SCAN` / `BLUETOOTH_CONNECT`
  - `android.permission.USE_BIOMETRIC`（工作台應用鎖）
  - `android.permission.SYSTEM_ALERT_WINDOW`（懸浮窗預覽模式）

### 3.2 生成子 App（Generated Shell: `shell/src/main/AndroidManifest.xml`）
生成之子 App 的權限具備動態注入特性：
- **基本預設**：若為單純的靜態網頁或企業官網，僅需 `INTERNET` 與 `ACCESS_NETWORK_STATE`；若為純離線 HTML 應用，甚至可將 `INTERNET` 完全移除，確保最高的隱私安全性。
- **動態擴充**：子包模板預先定義了相機、麥克風、背景定位（`ACCESS_BACKGROUND_LOCATION`）、藍牙廣播（`BLUETOOTH_ADVERTISE`）、NFC、健康傳感器（`BODY_SENSORS`）等權限槽位，在使用者開啟特定 API 橋接時才正式寫入二進位 Manifest。

---

## 4. Keystore 簽名架構與備份機制

簽名是網站轉 App 與後續維護的核心命脈。WebToApp 的簽名架構由 `JarSigner.kt`、`PerAppSigningIdentity.kt` 與 `AabSigner.kt` 共同構成：

### 4.1 獨立金鑰管理機制（Per-App Signing Identity）
- **演算法規格**：採用 **RSA-3072** 密鑰對，產生自簽名 X.509 憑證，主體格式為 `CN=<packageName>`，憑證有效期限為 **30 年**（262,800 小時）。
- **金鑰儲存路徑**：
  - 金鑰檔格式為 **PKCS#12**（`.p12`），存放於 Android 私有目錄：
    `context.filesDir/app_signing/sig_<sha256(packageName)[0..19]>.p12`
  - 隨機密鑰密碼存於：
    `context.filesDir/.app_signing_credential`（由 `SecureRandom` 動態生成 40 位元英數字元組成的強密碼）。
- **更新相容性**：以 package name 作為雜湊對應，同一專案後續多次構建會自動復用相同的金鑰檔，確保已安裝的使用者能夠順利覆蓋安裝更新。

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
> 2. 若使用手機自動生成之金鑰，必須在構建完成後立即將 `.p12` 檔及 `.app_signing_credential` 密碼檔透過安全通道備份至離線密碼庫或加密硬碟。

---

## 5. 本機 Windows 11 環境實測與工具鏈檢查

維護者針對當前 Windows 11 本機開發環境進行了深度檢測：

```powershell
# 檢測指令
Get-Command adb.exe, emulator.exe
adb devices
emulator.exe -list-avds
```

### 檢測結果輸出：
1. **Android Debug Bridge (ADB)**：
   - 存在於 `C:\Android\adb.exe`（版本 35.x，Android SDK Platform-tools）。
   - ADB 常駐服務可正常啟動（`* daemon started successfully on port 5037 *`）。
2. **Android SDK 本地環境**：
   - 存在於 `C:\Users\SanHsien\AppData\Local\Android\Sdk`。
   - 包含完整的 `build-tools`、`emulator`、`platforms`、`platform-tools` 與 `system-images`。
3. **裝置與模擬器實例狀態**：
   - `adb devices` 輸出：`List of devices attached`（目前無連接任何實體 Android 裝置）。
   - `emulator.exe -list-avds` 輸出為空（目前尚未配置現成之 AVD 虛擬機器映像檔）。

### 結論推導：
- Windows 11 本機具備完整的 ADB 與 Android SDK 基礎建設。
- 但因為 WebToApp 本體是一個 `.apk` 應用程式，且其打包引擎直接在 Android 核心與 Dalvik/ART 虛擬機上運行，Windows 11 作業系統本身無法直接在 x86_64 原生環境下裸跑 APK（除非透過啟動 Android Studio AVD 模擬器，或透過 USB 連接實體 Android 手機）。
- 因此，要完整驗證 WebToApp 的打包流程與產出 APK，必須啟動本機 AVD 模擬器或連接實機。

---

## 6. 已知限制與技術邊界

1. **實機/模擬器環境相依性**：WebToApp 無法直接以 Node.js 或 Python 命令列腳本在 Windows 終端純無頭（headless）執行，必須透過 Android OS 容器執行打包。
2. **Web 視圖與原生體驗落差**：
   - 預設基於系統 WebView，不同 Android 系統版本之 Chromium 核心版本不一，若目標網頁使用了過新的 CSS 特性（如某些 Container Queries 或新版 CSS nesting），在老舊手機上可能產生版面相容性問題。
   - 頁面內跳轉若缺乏 SPA 路由控制，容易在點擊實體 Back 鍵時直接退出應用，需在 WebToApp 中適配 `wta:back` 攔截器。
3. **Google Play 政策審查限制**：
   - 純網頁套殼若無提供獨特的使用者體驗、推播或離線功能，極易觸犯 Google Play 的「最低功能性政策（Minimum Functionality）」與「WebView 垃圾內容政策（Spam Policy）」。
4. **效能與檔案體積限制**：
   - 若開啟內嵌 Node.js、PHP、Python 等運行時，產出的 APK 體積將暴增 30MB ~ 120MB 不等，且後台長時間保活受限於各廠牌 Android ROM 的省電管理機制（電池最佳化限制）。

---

## 7. 總體結論

結論：可行（需搭配 Android 實機或模擬器執行打包與驗證）
