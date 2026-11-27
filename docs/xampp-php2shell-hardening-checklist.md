# Windows XAMPP 架站安全加固與 PHP2Shell 應變檢核表 (XAMPP & PHP2Shell Hardening Checklist)

> 來源筆記：`notes/2026-11-25-openai-php2shell-checker-xampp-hardening.md`（任務 `T-20261125-06`）  
> 適用環境：Windows 10／11／Server 上以 XAMPP（Apache + PHP + MariaDB）承載對外或內網服務的主機；預設安裝路徑 `C:\xampp`。  
> 使用方式：照第 0 節判斷急迫度，再依第 1 → 2 → 3 節走完 PHP2Shell 應變，最後逐項勾選第 4 節的生產加固。每一項都附「怎麼查」與「改成什麼」。

> [!IMPORTANT]
> 本檢核表的 CVE 編號、漏洞機制與安全修補版本門檻取自來源筆記（2026-11-25 整理，`source_review: partial`）。動手升級前，先到 PHP 官方安全公告與 `windows.php.net` 再確認一次最新修補版本；版本號以官方為準。

> [!WARNING]
> XAMPP 官方（Apache Friends）定位為本機開發套件，不建議直接用於生產環境。本檢核表是「既然已經在用，至少做到這些」的最低防線，不代表做完就適合長期對外營運。

---

## 0. 急迫度快速判斷

```text
這台 XAMPP 有對外（公網 / 跨網段）開放 80/443 嗎？
├─ 否（只在 localhost） ──→ 排程升級即可；仍建議做第 4 節加固
└─ 是
   ├─ PHP 版本 ≥ 修補版本（見 1.1）──→ 只做第 4 節加固
   └─ PHP 版本 < 修補版本 / 無法判斷
      └─→ 立即做第 2 節止血（當天），再做第 3 節根本修補（盡快）
```

---

## 1. 先診斷（不改任何設定）

### 1.1 確認 Apache 實際載入的 PHP 版本

- [ ] **CLI 版本**：

  ```powershell
  C:\xampp\php\php.exe -v
  ```

- [ ] **確認 Apache 用的是同一個 PHP 與 `php.ini`**：CLI 與 Apache 模組可能讀不同的 `php.ini`。檢查 `C:\xampp\apache\conf\extra\httpd-xampp.conf` 的 `PHPIniDir` 與 `LoadModule php_module` 指向的路徑：

  ```powershell
  Select-String -Path C:\xampp\apache\conf\extra\httpd-xampp.conf -Pattern 'PHPIniDir|LoadModule php'
  C:\xampp\php\php.exe --ini
  ```

- [ ] **對照修補門檻**（來源筆記，依 PHP 2026-10-21 安全公告）：

  | 分支 | 已修補版本 | 低於此版本 |
  | --- | --- | --- |
  | 8.2 | `8.2.35+` | 有風險 |
  | 8.3 | `8.3.36+` | 有風險 |
  | 8.4 | `8.4.27+` | 有風險 |
  | 8.5 | `8.5.12+` | 有風險 |
  | 5.4–8.1 | 已停止主線支援，無官方修補 | 必須升級分支 |

### 1.2 從外部看會暴露什麼

- [ ] **讀回應標頭**（只送 `HEAD`，不發送任何攻擊封包）：

  ```powershell
  curl.exe -sI http://localhost/
  ```

  看 `Server:` 是否帶出 Apache／OpenSSL／PHP 版本，`X-Powered-By:` 是否帶出 `PHP/8.x.y`。

- [ ] **（選用）OpenAI `php2shell-checker`**：`openai/php2shell-checker`（Apache-2.0）是純版本比對工具，提供 `phpcheck-url`（讀 `X-Powered-By`／`Server` 標頭、不跟隨轉址）與 `phpcheck-server`（本地版本檢查）。使用前先唯讀檢閱該 repo 的 README 與 `phpcheck.js`，依 README 指示執行；不要用 `curl | bash`／`iwr | iex` 類一行安裝。
- [ ] **三態判讀**：

  | 結果 | exit code | 意義 | 行動 |
  | --- | --- | --- | --- |
  | `OK` | 0 | 版本已達修補門檻 | 做第 4 節加固 |
  | `POTENTIALLY VULNERABLE` | 1 | 版本低於門檻 | 立即走第 2、3 節 |
  | `UNKNOWN` | 3 | 標頭被隱藏或無法判斷 | **不等於安全**；改用 1.1 的本機版本檢查為準 |

---

## 2. 暫時止血（升級前的過渡措施）

> [!CAUTION]
> 改設定前先備份三個檔案，改壞時直接還原：
>
> ```powershell
> $ts = Get-Date -Format yyyyMMdd-HHmmss
> Copy-Item C:\xampp\php\php.ini "C:\xampp\php\php.ini.bak-$ts"
> Copy-Item C:\xampp\apache\conf\httpd.conf "C:\xampp\apache\conf\httpd.conf.bak-$ts"
> Copy-Item C:\xampp\mysql\bin\my.ini "C:\xampp\mysql\bin\my.ini.bak-$ts"
> ```

### 2.1 `CVE-2026-109619`（`session.upload_progress` UAF）

- [ ] 在 **Apache 實際載入的主 `php.ini`**（1.1 查到的那一份）設定：

  ```ini
  ; C:\xampp\php\php.ini
  session.upload_progress.enabled = 0
  ```

- [ ] **不能**寫在 `.user.ini` 或用 `ini_set()`：漏洞在應用程式碼執行前就被觸發，這兩種方式來不及生效。若用虛擬主機層級設定，只能用 `php_admin_flag session.upload_progress.enabled off`。
- [ ] 副作用：依賴上傳進度條（`$_SESSION` upload progress）的功能會失效。

### 2.2 `CVE-2026-109618`（OOM `longjmp()` Heap Corruption）——高風險權衡

來源筆記提到的權宜做法是 `memory_limit = -1`（關掉 PHP 記憶體上限，避開內部 OOM 中斷路徑）。這會把記憶體耗盡轉嫁給作業系統，對外網站可能被打成整台主機 OOM／DoS。

- [ ] **預設不採用**。只有在「確認無法當天升級」且「能接受 DoS 風險」時才開，並且**必須同時**做下面三件事：

  ```ini
  ; C:\xampp\php\php.ini
  memory_limit = -1
  post_max_size = 8M
  upload_max_filesize = 8M      ; 不可大於 post_max_size
  ```

  ```apache
  # C:\xampp\apache\conf\httpd.conf（全域或 <VirtualHost> 內）
  LimitRequestBody 10485760     # 10 MB，依網站實際上傳需求調整
  ```

- [ ] 在變更紀錄寫下開啟時間，升級完成後**立即**把 `memory_limit` 改回有限值（例如 `256M`）。

### 2.3 套用並驗證

- [ ] 語法檢查後重啟 Apache：

  ```powershell
  C:\xampp\apache\bin\httpd.exe -t
  ```

  輸出 `Syntax OK` 才重啟（XAMPP Control Panel 或 `Restart-Service Apache2.4`，服務名以 `Get-Service *apache*` 為準）。
- [ ] 確認設定真的生效（以 Apache 載入的 `php.ini` 為準）：

  ```powershell
  C:\xampp\php\php.exe -c C:\xampp\php\php.ini -r "echo ini_get('session.upload_progress.enabled'), ' ', ini_get('memory_limit'), PHP_EOL;"
  ```

  預期第一個值為空字串或 `0`。

---

## 3. 根本修補

- [ ] **方案 A：升級 XAMPP**——新版 XAMPP 內建的 PHP 已達第 1.1 節門檻時才有意義；先看發行說明的 PHP 版本號。升級前備份 `htdocs`、資料庫（`mysqldump`）與三個設定檔。
- [ ] **方案 B：就地替換 PHP**（XAMPP 尚未跟進時）：
  1. 從 PHP Windows 官方下載與現有架構相同的 **Thread Safe (TS) x64 Zip**（XAMPP 的 Apache 模組需要 TS 版）。
  2. 停止 Apache，把 `C:\xampp\php` 改名備份（例如 `php.old`），解壓新版到 `C:\xampp\php`。
  3. 由新版的 `php.ini-production` 複製成 `php.ini`，再把舊 `php.ini` 中網站需要的 extension 與路徑設定逐項搬過來（不要整份覆蓋舊檔）。
  4. 確認 `httpd-xampp.conf` 的 `LoadModule php_module` 檔名與新版 DLL 一致。
  5. `httpd.exe -t` → 啟動 Apache → 重跑第 1 節的版本與標頭檢查。
- [ ] 修補完成後：把第 2.2 節的 `memory_limit` 恢復有限值；`session.upload_progress.enabled` 可視需要恢復，但沒用到就維持 `0`。

---

## 4. Windows XAMPP 生產加固五項清單

### 4.1 MariaDB：帳號與監聽位址

- [ ] **`root` 設強密碼、刪匿名帳號、刪 `test` 庫**。用互動式登入（`-p` 不帶值，密碼不進指令列歷史）：

  ```powershell
  C:\xampp\mysql\bin\mysql.exe -u root -p
  ```

  ```sql
  SELECT User, Host FROM mysql.user;                 -- 先看現況
  ALTER USER 'root'@'localhost' IDENTIFIED BY '<在此互動輸入強密碼>';
  DROP USER IF EXISTS ''@'localhost';
  DROP USER IF EXISTS ''@'%';
  DROP DATABASE IF EXISTS test;
  FLUSH PRIVILEGES;
  ```

- [ ] **只監聽本機**：

  ```ini
  ; C:\xampp\mysql\bin\my.ini
  [mysqld]
  bind-address = 127.0.0.1
  ```

- [ ] **驗證**：重啟 MariaDB 後，`3306` 只應綁在 `127.0.0.1`：

  ```powershell
  netstat -ano | findstr :3306
  ```

  出現 `0.0.0.0:3306` 或 `[::]:3306` 表示仍對外監聽。
- [ ] 網站應用改用獨立的最小權限資料庫帳號，不用 `root`。

### 4.2 `phpMyAdmin`：移除或鎖本機

- [ ] **不需要就移除**：XAMPP 的 phpMyAdmin 位於 `C:\xampp\phpMyAdmin`，由 `httpd-xampp.conf` 的 `Alias /phpmyadmin` 掛出；刪除該 `Alias` 區塊與目錄即可。
- [ ] **需要就只允許本機或指定 IP**：

  ```apache
  # C:\xampp\apache\conf\extra\httpd-xampp.conf
  <Directory "C:/xampp/phpMyAdmin">
      Require local
      # 或指定管理端 IP：Require ip 192.168.1.10
  </Directory>
  ```

- [ ] **不要把密碼寫死在設定檔**：`C:\xampp\phpMyAdmin\config.inc.php` 中 `$cfg['Servers'][$i]['auth_type']` 應為 `'cookie'`，不是 `'config'`（`config` 模式會把 root 密碼明文存在檔案裡）。
- [ ] 一併移除 XAMPP 範例頁：`C:\xampp\htdocs\dashboard`、`C:\xampp\htdocs\xampp`、`C:\xampp\htdocs\index.php`（若是預設轉址頁），並確認 `httpd-xampp.conf` 中 `/xampp`、`/security`、`/server-status`、`/server-info` 都是 `Require local`。
- [ ] **驗證**：從另一台機器開 `http://<主機IP>/phpmyadmin/`，應得到 `403` 或 `404`。

### 4.3 Apache 與 PHP：關目錄列表、隱藏版本

- [ ] **關閉目錄列表**：

  ```apache
  # C:\xampp\apache\conf\httpd.conf，<Directory "C:/xampp/htdocs"> 區塊內
  Options -Indexes +FollowSymLinks
  ```

- [ ] **隱藏版本**（XAMPP 預設寫在 `conf/extra/httpd-default.conf`，先確認 `httpd.conf` 中 `Include conf/extra/httpd-default.conf` 沒有被註解）：

  ```apache
  ServerTokens Prod
  ServerSignature Off
  ```

- [ ] **PHP 不洩漏資訊**：

  ```ini
  ; C:\xampp\php\php.ini
  expose_php = Off
  display_errors = Off
  log_errors = On
  allow_url_include = Off
  ; allow_url_fopen：網站不需要遠端讀檔就設 Off
  ```

- [ ] **驗證**：`httpd.exe -t` 為 `Syntax OK`，重啟後 `curl.exe -sI http://localhost/` 的 `Server:` 只剩 `Apache`，且沒有 `X-Powered-By:`；開一個沒有 `index` 檔的子目錄應得到 `403`。

### 4.4 Windows：`C:\xampp` 權限與多餘服務

- [ ] **檢查 Apache 服務身分**：

  ```powershell
  sc.exe qc Apache2.4
  ```

  `SERVICE_START_NAME` 若為 `LocalSystem`，改用專用低權限帳號（服務內容 → 登入），並只給該帳號 `C:\xampp` 讀取與執行、`htdocs` 中必要上傳／快取目錄的寫入權限。
- [ ] **檢查一般使用者寫入權限**：

  ```powershell
  icacls C:\xampp
  icacls C:\xampp\apache\conf
  icacls C:\xampp\php
  ```

  `Users`／`Authenticated Users` 對 `apache\conf`、`php`、`mysql\bin` 不應有 `(F)`、`(M)`、`(W)`。調整 ACL 前先 `icacls C:\xampp /save C:\acl-backup-xampp.txt /t` 備份。
- [ ] **停用不用的常駐服務**（FileZilla FTP、Mercury Mail、Tomcat）：

  ```powershell
  Get-Service | Where-Object { $_.Name -match 'filezilla|mercury|tomcat' -or $_.DisplayName -match 'FileZilla|Mercury|Tomcat' }
  ```

  確認不用後，用系統管理員權限 `Stop-Service <名稱>` 並 `Set-Service <名稱> -StartupType Disabled`。

### 4.5 防火牆與前緣防護

- [ ] **封鎖資料庫對外連入**（系統管理員 PowerShell）：

  ```powershell
  New-NetFirewallRule -DisplayName "Block MariaDB 3306 inbound" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Block
  Get-NetFirewallRule -DisplayName "Block MariaDB 3306 inbound" | Format-List DisplayName, Enabled, Action
  ```

  FTP（`21`）、SMTP／POP3（`25`／`110`）同理，未使用就封鎖。
- [ ] **只開需要的入站埠**：檢查是否有寬鬆規則（例如 XAMPP 安裝時允許的 `Apache HTTP Server` 對所有設定檔開放）：

  ```powershell
  Get-NetFirewallRule -Direction Inbound -Enabled True -Action Allow | Where-Object DisplayName -match 'Apache|mysql|maria|filezilla|mercury'
  ```

- [ ] **HTTPS 與前置防護**：不要把 `:80` 直接裸露在公網；改由反向代理或通道終結 TLS 並擋掉自動化掃描（例如 Cloudflare Tunnel／WAF，或 Caddy／Nginx 前置），Apache 只監聽本機或內網位址（`httpd.conf` 的 `Listen 127.0.0.1:80`）。
- [ ] **驗證**：從外部網路對主機掃描或連線 `3306` 應逾時或被拒；`443` 回應的憑證有效。

---

## 5. 完成後的回歸檢查

| 檢查 | 指令 | 通過條件 |
| --- | --- | --- |
| PHP 版本 | `C:\xampp\php\php.exe -v` | 達第 1.1 節門檻 |
| Apache 設定語法 | `C:\xampp\apache\bin\httpd.exe -t` | `Syntax OK` |
| 標頭暴露 | `curl.exe -sI http://localhost/` | 無 `X-Powered-By`，`Server: Apache` |
| DB 監聽 | `netstat -ano \| findstr :3306` | 只有 `127.0.0.1:3306` |
| 臨時止血是否已撤 | `php.exe -r "echo ini_get('memory_limit');"` | 不是 `-1` |
| 多餘服務 | `Get-Service` 篩 FileZilla／Mercury | `Stopped` 且 `Disabled` |
| 網站功能 | 人工走過登入、上傳、表單 | 功能正常 |

> [!NOTE]
> 本檢核表為書面規格，尚未在實機 XAMPP 環境逐條執行驗證。指令依 XAMPP 預設目錄結構撰寫；若安裝路徑或服務名稱不同，以實機 `Get-Service`、`httpd-xampp.conf` 內容為準。

## 6. 參考

- 來源筆記：`notes/2026-11-25-openai-php2shell-checker-xampp-hardening.md`
- 檢查工具：[`openai/php2shell-checker`](https://github.com/openai/php2shell-checker)
- 相關檢核表：[`docs/production-smoke-security-checklist.md`](./production-smoke-security-checklist.md)（後續由 `T-20261125-07` 補入標頭暴露與執行期版本門檻檢核）
