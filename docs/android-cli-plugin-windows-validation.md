# Android CLI Plugin 在 Windows 11 之安裝安全評估與整合驗證報告

> 本文件收錄於 `docs/android-cli-plugin-windows-validation.md`，為任務 `T-20261019-06` 針對 Google 官方 `android-cli-plugin` 與 `android` CLI 在 Windows 11 原生環境下的安裝機制、安全風險與整合流水線的完整技術評估。依據安全規範與大量下載硬閘門要求，本階段交付評估文件。

---

## 1. 官方安裝腳本安全性審查（Security Audit）

Google 官方提供的 Windows 安裝腳本端點為：
`https://dl.google.com/android/cli/latest/windows_x86_64/install.cmd`

維護者將該腳本抓取至沙盒環境（`C:\GitHub\_sandbox\android-install.cmd`）進行靜態語法與行為審查，核心關鍵段落如下：

```cmd
:: Move to the installation directory
echo Installing to %INSTALL_DIR%...
move /y "!TMP_FILE!" "%INSTALL_DIR%\%BINARY_NAME%"

:: Add to Registry if not already present
set "USER_PATH="
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%b"
echo !USER_PATH! | findstr /i /c:"%INSTALL_DIR%" >nul
if %errorLevel% neq 0 (
    echo Adding %INSTALL_DIR% to user PATH...
    if "!USER_PATH!"=="" (
        set "NEW_PATH=%INSTALL_DIR%"
    ) else (
        set "NEW_PATH=!USER_PATH!;%INSTALL_DIR%"
    )
    reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
)

:: Force first download/initialization
echo Initializing CLI...
set "ANDROID_CLI_INSTALL_SOURCE=!SOURCE!"
set "ANDROID_CLI_FRESH_INSTALL=1"
"%INSTALL_DIR%\%BINARY_NAME%"
```

### 審查發現與安全違規點

1. **強制修改系統註冊表（Registry Violation）**：
   - 腳本第 47 行使用 `reg add "HKCU\Environment" /v Path ... /f` 強制覆寫當前使用者的全域環境變數 `Path`。
   - **違規判斷**：違反安全規則第 1 條「不得修改系統設定」及第 2 條「不做全域安裝、不改 PATH」。
2. **首次執行觸發大型二進位與 SDK 下載（Bandwidth & Storage Limit）**：
   - 腳本第 54 行在加入 Path 後立即呼叫 `android.exe` 執行初始化，此步驟會自動連線 Google 伺服器下載：
     - Android Command-line Tools（約 150 MB）
     - Android SDK Platform & Build-tools（約 400 MB ~ 800 MB）
     - OpenJDK 執行環境（約 200 MB ~ 300 MB）
     - 總下載量通常高達 1.5 GB ~ 3.5 GB。
   - **違規判斷**：違反安全規則第 3 條「需要下載超過 1 GB 就停在那一項，回報需要維護者決定，不要繞過」。

---

## 2. 本地現狀盤點與環境分析

| 檢查項目 | 檢測指令 / 路徑 | 本機現況 | 風險與相容性分析 |
| :--- | :--- | :--- | :--- |
| **`android` 執行檔** | `Get-Command android` | 未安裝 (None) | 系統中無殘留或過期版本。 |
| **全域外掛配置** | `~/.gemini/config/plugins/android-cli-plugin` | 已就緒 (Ready) | 具備完整的 495 行 `SKILL.md`，定義 `android create`, `android sdk`, `android skills` 等完整契約。 |
| **JDK 環境** | `Get-Command java` | 未配置 (None) | 需要 JDK 17+ 才能編譯 Android Gradle 專案。 |
| **Android SDK 目錄** | `$env:ANDROID_HOME` | 未設定 (None) | 需指定專用資料夾以防磁碟膨脹。 |

---

## 3. 綠色沙盒化安裝與自動化流水線建議架構

為解決官方 `install.cmd` 越權改動註冊表與大量下載問題，建議未來若維護者授權安裝，應採用如下**「無侵入式沙盒安裝架構」**：

```text
[使用者授權 >1GB 下載]
         │
         ▼
[隔離目錄 C:\GitHub\_sandbox\android-cli\]
   ├── bin\android.exe              <── 僅手動解包放置，不寫入系統 Registry
   └── sdk\                         <── 透過 ANDROID_HOME 指向此處
         │
         ▼
[環境隔離啟動腳本 run-android.ps1]
   ├── $env:PATH = "$PSScriptRoot\bin;" + $env:PATH
   ├── $env:ANDROID_HOME = "$PSScriptRoot\sdk"
   └── android skills list --all
         │
         ▼
[端到端測試]
   ├── android create empty-activity --name="SandboxApp" --output="./tmp-app"
   └── android describe ./tmp-app
```

### 命令規格與預期行為驗證

當沙盒化環境就緒後，以下指令應能在 Windows 11 原生 PowerShell 下安全執行：

1. **列出官方 Agent Skills**：
   ```powershell
   android skills list --all
   ```
   *預期輸出*：列出 33 個官方收錄的 Android 專家技能（如 Compose 遷移、Accessibility 審查、Play Billing 等）。
2. **安裝特定技能至本地工作區**：
   ```powershell
   android skills add compose-migration
   ```
3. **無介面建立空專案**：
   ```powershell
   android create empty-activity --name="SmokeTest" --output="./sandbox-app" --minSdk=26
   ```

---

## 4. 評估總結與結論

1. **硬閘門觸發停下**：因官方腳本企圖修改全域 Registry `Path`，且 Android SDK 依賴下載量超過 1 GB，本次評估遵循最高安全原則，不執行遠端安裝腳本，僅產出架構與安全評估報告。
2. **待決事項**：待維護者後續決定是否在獨立磁碟路徑授權下載完整 Android SDK / JDK 環境。
