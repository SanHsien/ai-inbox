---
id: "2026-11-25-openai-php2shell-checker-xampp-hardening"
title: "PHP2Shell（CVE-2026-109618 / 109619）、OpenAI `php2shell-checker` 與 Windows XAMPP 架站安全加固評估"
source_url: "https://github.com/openai/php2shell-checker"
source_platform: "GitHub (openai/php2shell-checker) / 資安公告與 XAMPP 維運評估"
author: "OpenAI / Wiz / Calif（PHP2Shell 揭露）"
analyzed_at: "2026-11-25"
analyzed_by: "antigravity"
written_by: "antigravity/gemini-4-hydrogen@ac6a8875-15e0-4f9f-ad0a-058d7b01bba9"
source_review: partial
source_images: 0
source_replies: 0
source_reviewed_at: "2026-11-25"
source_review_note: "已透過 gh api 唯讀檢閱 openai/php2shell-checker（metadata、檔案樹、README.md 與 phpcheck.js），並以 search_web 查證 PHP2Shell（CVE-2026-109618 / CVE-2026-109619）、mrmad.com.tw 報導摘要與 Windows XAMPP 安全加固規範；未以瀏覽器開啟 mrmad.com.tw 與 socradar.io 原頁面，亦未執行本地掃描。"
status: pending
cluster: 2
cluster_role: "XAMPP架站安全"
short_title: "PHP2Shell與XAMPP加固"
tags:
  - php2shell
  - cve-2026-109618
  - cve-2026-109619
  - xampp
  - windows-server
  - security-hardening
  - openai
---

# PHP2Shell（CVE-2026-109618 / 109619）、OpenAI `php2shell-checker` 與 Windows XAMPP 架站安全加固評估

- **開源檢查工具**：[`openai/php2shell-checker`](https://github.com/openai/php2shell-checker)（`Apache-2.0`，`1,476` stars）
- **相關報導與線上檢測**：[瘋先生 `mrmad.com.tw/openai-php2shell-checker-tool`](https://mrmad.com.tw/openai-php2shell-checker-tool) ｜ [SOCRadar Free PHP2Shell Checker](https://socradar.io/free-tools/php2shell-checker)
- **分析日期**：`2026-11-25`
- **當前狀態**：`🔴 待辦 (Pending)`
- **相關交叉參照**：
  - [`docs/production-smoke-security-checklist.md`](../docs/production-smoke-security-checklist.md)（本庫全端網站上線前 QA 與資安稽核檢核表）
  - [`tools/audit_fullstack_security.py`](../tools/audit_fullstack_security.py)（本庫自動化安全稽核腳本）

---

## 0. 原始資料盤點（`openai/php2shell-checker` 與 PHP2Shell CVE 脈絡）

- **漏洞本質（PHP2Shell，CVSS 9.2）**：
  - 2026 年 10 月由 Wiz、OpenAI 與 Calif 聯合揭露的 **PHP 核心執行期記憶體安全漏洞（免驗證 RCE／記憶體洩漏）**，影響自 PHP 5.4 起的多個分支：
    - **`CVE-2026-109618`**：請求初始化階段觸發記憶體耗盡（OOM）時，C 層 `longjmp()` 緊急跳出中斷未初始化完成的資料結構，導致後續清理流程誤讀殘留指標造成 Heap Corruption。
    - **`CVE-2026-109619`**：與 PHP 內建 `session.upload_progress` 子系統相關的 Use-After-Free（UAF）；在任何應用層 PHP 程式碼執行之前，帶有 `PHP_SESSION_UPLOAD_PROGRESS` 的 `multipart/form-data` 請求就會提前寫入 `$_SESSION` 並觸發漏洞。
  - **官方安全修補版本**（低於以下版本皆具潛在風險，5.4–8.1 已過主線支援）：
    - PHP `8.2.35+`、`8.3.36+`、`8.4.27+`、`8.5.12+`（對應 PHP 2026-10-21 安全公告）。
- **OpenAI `php2shell-checker` 機制與邊界**：
  - 純版本比對預警工具（**不發送漏洞利用封包**），提供 `phpcheck-url`（以 `HEAD`／備援 `GET` 讀取 `X-Powered-By` 與 `Server` 標頭，不跟隨轉址）與 `phpcheck-server`（本地執行版本檢查）。
  - 回傳三態：`OK`（exit 0）、`POTENTIALLY VULNERABLE`（exit 1）、`UNKNOWN`（exit 3，例如隱藏標頭或 Linux 發行版 backport 修補無法從標頭判斷）。
- **使用者提及的「暫時性止血措施」技術核對**：
  1. **`session.upload_progress.enabled = 0`**：針對 `CVE-2026-109619` 有效，但**必須寫在伺服器主 `php.ini`（或 `php_admin_flag`）**；寫在 `.user.ini` 或執行期 `ini_set()` 無效（因為解析發生在應用碼執行之前）。
  2. **「移除 memory limit」（即 `memory_limit = -1`）**：針對 `CVE-2026-109618` 繞開 PHP 內部 OOM `longjmp()` 中斷路徑的權宜措施——**風險極高**：在對外網站關閉 `memory_limit` 會把記憶體耗盡轉嫁給作業系統導致主機 OOM / DoS，若暫時啟用必須同步調低 `post_max_size` 並在 Apache 層限制 `LimitRequestBody`，且僅能作升級前的短暫止血。

---

## 1. Windows XAMPP 架站常見風險與加固評估

XAMPP 專為本機開發便利設計，官方（Apache Friends）明確不建議直接用於生產環境。若目前仍以 XAMPP 承載對外或內網服務，除 PHP2Shell 外還須同步處理以下常見架站風險：

1. **套件綑綁導致修補滯後（針對 PHP2Shell）**：
   - 舊版 XAMPP 內建舊版 PHP；若新版 XAMPP 尚未跟進 `8.2.35+ / 8.3.36+ / 8.4.27+ / 8.5.12+`，需從 PHP Windows 官方下載對應的 **Thread Safe (TS) Zip** 就地替換 `C:\xampp\php` 並重設 `php.ini`、重啟 Apache（同時建議在 `php.ini` 先關閉 `session.upload_progress.enabled = 0` 與 `expose_php = Off`）。
2. **資料庫與 `phpMyAdmin` 預設門戶大開**：
   - MariaDB 預設 `root` 無密碼、存在匿名帳號與 `test` 庫，且未限制 `bind-address = 127.0.0.1`；`C:\xampp\htdocs\phpmyadmin` 若暴露於公網極易遭暴力猜測或已知漏洞掃描。
3. **Windows 權限與多餘常駐服務（LPE 放大風險）**：
   - 若 Apache 以高權限（如 `LocalSystem`）運行，且 `C:\xampp` 保留一般使用者寫入權限（ACL），一旦 PHP2Shell 或網站弱點遭突破，攻擊者可直接提權控制整台 Windows 主機；未使用的 FileZilla FTP／Mercury Mail 亦應停用。
4. **Apache / PHP 資訊洩漏與目錄暴露**：
   - `httpd.conf` 預設 `Options Indexes`（目錄列表）、`ServerSignature On` / `ServerTokens Full`，以及 `php.ini` 的 `display_errors = On`、`allow_url_fopen = On` 皆會洩漏版本與路徑細節。
5. **傳輸加密與前緣防護**：
   - 直接裸露 `:80` / `:3306` 而無 TLS（HTTPS）、無 Windows 防火牆白名單或反向代理／WAF（如 Cloudflare Tunnel / WAF、Caddy / Nginx 前置）會直接承受自動化掃描流量。

---

## 2. 拆解出的待辦任務 (Action Items)

- [ ] **`T-20261125-06`**｜**[優先級：高]** 建立 Windows XAMPP 架站安全加固與 PHP2Shell（`CVE-2026-109618` / `109619`）應變檢核表 `docs/xampp-php2shell-hardening-checklist.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\xampp-php2shell-hardening-checklist.md`（收錄於集群 2）
  - **執行步驟**：
    1. 整理「先診斷（`php -v` / `php2shell-checker`）→ 暫時止血（`php.ini` 設 `session.upload_progress.enabled = 0` 與 `memory_limit = -1` 之 DoS 權衡＋`post_max_size`/`LimitRequestBody` 限制）→ 根本修補（升級 XAMPP 或替換 Thread Safe PHP 8.2.35+ / 8.3.36+ / 8.4.27+ / 8.5.12+）」標準作業流程。
    2. 納入 Windows XAMPP 生產加固五項清單：MariaDB（`root` 強密碼、刪匿名與 `test`、`bind-address = 127.0.0.1`）、移除或 IP 鎖定 `phpMyAdmin`、Apache（關 `Indexes` 與 `ServerTokens Prod`）、Windows `C:\xampp` ACL 最小權限與停用 FileZilla/Mercury、防火牆封鎖 `3306` 與前置 HTTPS／WAF。
  - **驗收標準（DoD）**：產出 `docs/xampp-php2shell-hardening-checklist.md`，指令與 `php.ini` / `httpd.conf` / `my.ini` 區段清晰可直接對照檢查，且 `python tools/verify_inbox.py` 驗證通過。

- [ ] **`T-20261125-07`**｜**[優先級：中]** 評估將「運行期版本與標頭暴露檢查（參考 `openai/php2shell-checker`）」納入 `docs/production-smoke-security-checklist.md`
  - **目標範圍**：`C:\GitHub\ai-inbox\docs\production-smoke-security-checklist.md`（收錄於集群 2）
  - **執行步驟**：
    1. 參考 `openai/php2shell-checker` 的非侵入式雙模態檢查（URL 標頭 `X-Powered-By` / `Server` 與本地執行期版本比對），在 `docs/production-smoke-security-checklist.md` 補充「伺服器標頭隱藏（`expose_php = Off` / `ServerTokens Prod`）與執行期 CVE 基準版本門檻檢核」條目。
    2. 明確區分 `OK` / `POTENTIALLY VULNERABLE` / `UNKNOWN` 三態判讀，避免隱藏標頭時誤判為安全。
  - **驗收標準（DoD）**：`docs/production-smoke-security-checklist.md` 完成補充且 `python tools/verify_inbox.py` 驗證通過。
