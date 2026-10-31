---
id: 2026-10-31-zero-breach-toolkit-mercenary-spyware-forensics
title: "Zero-Breach-Toolkit 開源傭兵間諜軟體鑑識工具解構：跨平台離線檢測、Pegasus/Predator IoC 比對、唯讀數位鑑識與端點防禦實戰"
source_url: "https://www.threads.com/share/BAa4BXlFwW/"
source_platform: "Threads (@leeunhn) / GitHub (interplains/Zero-Breach-Toolkit)"
author: "李昀翰 (@leeunhn) / interplains (Zero-Breach-Toolkit)"
analyzed_at: 2026-10-31
analyzed_by: "Antigravity"
status: pending
cluster: 3
cluster_role: "端點資安與間諜軟體鑑識"
short_title: "Zero-Breach-Toolkit間諜軟體鑑識"
tags:
  - zero-breach-toolkit
  - mercenary-spyware
  - digital-forensics
  - pegasus
  - predator
  - endpoint-security
  - offline-scanner
  - mvt
  - ioc-matching
  - yara-x
---

# Zero-Breach-Toolkit 開源傭兵間諜軟體鑑識工具解構：跨平台離線檢測、Pegasus/Predator IoC 比對、唯讀數位鑑識與端點防禦實戰

- **來源連結**：[Threads 原文分享 (@leeunhn)](https://www.threads.com/share/BAa4BXlFwW/) ｜ [貼文永久網址](https://www.threads.com/@leeunhn/post/DfFLV0EmppX) ｜ [Zero-Breach-Toolkit 官方 GitHub](https://github.com/interplains/Zero-Breach-Toolkit) ｜ [Amnesty MVT 開源鑑識工具 (mvt.re)](https://mvt.re/) ｜ [Citizen Lab 威脅情報研究](https://citizenlab.ca/)
- **核心作者**：李昀翰（@leeunhn，數位資安與科技探索者）／ interplains 開源團隊
- **分析主題**：解構在 GitHub 迅速收穫 3,200+ 顆星的熱門開源數位鑑識工具 **Zero-Breach-Toolkit（`interplains/Zero-Breach-Toolkit`）**。深入剖析其如何打破過往「檢測高階間諜軟體必須付費送專業資安實驗室」的高門檻，提供一套完全**「本地離線運行（Offline-First）」**、**「嚴格唯讀（Strictly Read-Only）」**且支援 **Windows、macOS、Linux、Android 設備與 iOS 備份檔**的鑑識掃描器。詳細探討針對國家級/商業傭兵間諜軟體（Mercenary Spyware，如 NSO Group Pegasus、Cytrox Predator、Candiru、Graphite）的侵害指標（IoC）比對機制、鑑識限制與端點安全縱深防禦實戰。
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-23-zeabur-october-2026-security-incident.md`](./2026-10-23-zeabur-october-2026-security-incident.md)（Zeabur 資安事件反思：憑證生命週期、多租戶隔離與滲透防護）
  - [`notes/2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md`](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md)（Karpathy 專案規範四大硬閘門：最小特權原則與環境隔離）
  - [`notes/2026-10-18-desktop-sense-local-screen-context.md`](./2026-10-18-desktop-sense-local-screen-context.md)（desktop-sense 本機螢幕上下文與端點環境感知）
  - [`notes/2026-10-31-github-apps-server-to-server-copilot-agent-workload-identity.md`](./2026-10-31-github-apps-server-to-server-copilot-agent-workload-identity.md)（GitHub Apps S2S 認證與憑證最小權限隔離防線）

---

## 1. 核心內容摘要：問題背景與商業間諜軟體威脅全景（Executive Summary）

隨著商業傭兵間諜軟體（Mercenary Spyware）在政治異議人士、調查記者、人權律師及企業高階主管設備上屢遭曝光，端點安全面臨前所未有的隱蔽威脅：

```text
【高階商業間諜軟體特徵 (Pegasus / Predator)】
  - 零點擊漏洞滲透 (Zero-Click Exploits，如 iMessage / WhatsApp 封包觸發)
  - 記憶體常駐推論 (In-Memory Only)，幾乎不寫入實體磁碟常駐行程
  - 自動日誌抹除 (Log Tampering)，活動結束後主動銷毀 trace
  - 高度規避傳統防毒軟體 (Antivirus / EDR 靜態特徵碼難以命中)
               │
               ▼ (過往痛點：依賴高昂外部鑑識機構)
  - 需交付全機鏡像給第三方機構，存在二次個人私隱與商業機密洩漏風險
               │
               ▼ (Zero-Breach-Toolkit 典範：本地開源離線鑑識)
+-------------------------------------------------------------------------+
|                  Zero-Breach-Toolkit 核心設計哲學                       |
|   1. 100% 離線隔離：掃描期間阻斷 Python Socket 網路傳輸，杜絕回傳與 C2 告警 |
|   2. 嚴格唯讀防護：嚴禁修改原始日誌、備份檔與系統設定，保障司法數位鑑識完整度 |
|   3. 跨全平台覆蓋：Windows, macOS, Linux, Android (ADB), iOS (iTunes 備份) |
|   4. 公開 IoC 比對：整合 Citizen Lab、Amnesty International、Google TAG 庫 |
+-------------------------------------------------------------------------+
```

---

## 2. 系統架構與數位鑑識技術機制（System Architecture & Forensics）

Zero-Breach-Toolkit 採用多層解耦的跨平台鑑識架構，核心聚焦於**歷史足跡（Historical Artifacts）**的深度提取與已知侵害指標（IoC）比對：

```text
+-------------------------------------------------------------------------+
|                        輸入層 (Input Sources)                           |
|  [Windows 端點]  [macOS 端點]  [Linux 端點]  [Android ADB]  [iOS 備份檔] |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    核心鑑識剖析器 (Forensic Parsers)                    |
|  - 瀏覽器資料庫剖析: Chrome / Safari / Edge (SQLite 歷史、下載、Cookie)   |
|  - 系統持久化掃描: Registry (Run/RunOnce)、LaunchDaemons、Cron、Systemd  |
|  - 行動端特定日誌: iOS SMS.db、CallHistory、Safari Favicon、sysdiagnose  |
|  - 網路連線足跡: DNS 解析快取、Hosts 檔案、歷史 Proxy 配置紀錄         |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                 威脅指標比對引擎 (IoC Matching Engine)                   |
|   - STIX2 / JSON 侵害指標庫 (Citizen Lab, Amnesty International)        |
|   - YARA-X (Rust 高效能特徵碼比對引擎，比對記憶體與二進位字串)          |
|   - 網域與 IP 黑名單比對 (Regex / Fast String Prefix Match)             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    輸出與報告層 (Report Generation)                     |
|     * Markdown 結構化檢驗報告     * JSON 機械判讀摘要                   |
|     * 命中風險分級 (Clean / Suspicious / Confirmed IoC)                 |
+-------------------------------------------------------------------------+
```

### 關鍵技術機制：
1. **無特權／低特權運作（Unprivileged Execution）**：
   在 Windows 上無須 Administrator 最高權限即可檢測用戶態持久化與瀏覽器暫存；在 macOS 上僅需使用者授權終端機「完整磁碟存取權（Full Disk Access）」以讀取沙盒化的 Safari 資料庫。
2. **行動端備份鑑識支援**：
   比照 Amnesty 的 Mobile Verification Toolkit（MVT），使用者可使用 iTunes / Finder 產生未加密備份，Toolkit 解析備份內的 `Manifest.db`、`SMS.db`（檢驗簡訊零點擊注入連結）與 Safari 資料庫，完全無須越獄（Jailbreak）或 Root 設備。
3. **「未檢出不等於安全（The Clean Scan Caveat）」資安防線**：
   工具官方文檔明確指出：現代國家級間諜軟體常僅常駐於 RAM 並具備定時自毀（Self-destruct）機制。**單次離線掃描呈陰性（Clean），僅代表「未發現已知歷史殘留痕跡」，絕不構成「設備絕對乾淨」的保證**。對於高風險目標，仍需搭配即時網路異常流量監控與資安救援機構介入。

---

## 3. 跨專案應用：AI-Inbox 開發環境端點防線

在多 Agent 與開源工具鏈頻繁執行的開發者主機上，Zero-Breach-Toolkit 提供了極佳的本機防護借鑑：

| 防護構面 | 核心威脅情境 | Zero-Breach 鑑識機制 | 專案防線整合策略 |
| :--- | :--- | :--- | :--- |
| **憑證與連線竊取** | 惡意套件讀取本機 SSH Key、`.gitconfig`、AWS/GCP 憑證 | 掃描異常進程存取歷史與背景未知服務 | [`2026-10-23-zeabur-incident`](./2026-10-23-zeabur-october-2026-security-incident.md) 憑證輪替與硬閘門 |
| **非授權常駐** | 偽裝成常駐 Daemon 或排程任務竊取鍵盤側錄 | 審查 LaunchDaemons、Windows Run、Cron | 定期本機自動化排程審查與 Diff 監控 |
| **行動端連動污染** | 開發者插上手機進行 Android/iOS 偵錯時遭遇側向移動 | 離線解析 ADB dump 與 iOS 備份資料庫 | 定期執行行動設備衛生自檢（Mobile Hygiene） |

---

## 4. 關聯任務與知識拓撲（Task & Knowledge Relations）

- **雲端資安事件與憑證審查**：
  - [Zeabur 遭黑客攻擊事件反思：本地 OAuth 憑證與專案隔離](./2026-10-23-zeabur-october-2026-security-incident.md) ｜ 關聯任務：`T-20261023-05`、`T-20261023-06`
- **架構硬化與專案規範**：
  - [Karpathy 專案規範四大硬閘門](./2026-10-28-karpathy-claude-md-four-rules-engineering-hardening.md) ｜ 關聯任務：`T-20261028-01`、`T-20261028-02`
- **環境感知與端點脈絡**：
  - [desktop-sense 本機螢幕上下文與環境感知](./2026-10-18-desktop-sense-local-screen-context.md) ｜ 關聯任務：`T-20261018-06`
- **工作負載身分認證與最小授權**：
  - [GitHub Apps S2S 代理人身分認證](./2026-10-31-github-apps-server-to-server-copilot-agent-workload-identity.md) ｜ 關聯任務：`T-20261031-25`、`T-20261031-26`

---

## 5. Action Items 任務拆解

本分析轉化為 3 項具體工程落地任務，納入集群 3 待辦隊列：

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261031-31`**｜**[優先級：高]** 撰寫「商業間諜軟體端點鑑識與離線掃描落地手冊：Pegasus / Predator 威脅模型、跨平台 IoC 匹配與備份分析規格」收錄於 `docs/mercenary-spyware-forensic-guide.md`
  - **目標範圍**：`docs/mercenary-spyware-forensic-guide.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 深入分析知名傭兵級間諜軟體（Pegasus、Predator、Candiru、Subzero）的攻擊鏈（零點擊漏洞 Zero-Click、記憶體常駐、Log 自動清除特徵）。
    2. 規範 Zero-Breach-Toolkit 與 Amnesty MVT 跨平台掃描標準（Windows 註冊表/排程任務、macOS LaunchDaemons/Safari DB、iOS iTunes 備份 Manifest/SMS.db、Android ADB dump）。
    3. 明確定義「離線唯讀防禦準則（Offline & Read-Only）」與「掃描無異常不等於 100% 安全（Clean Scan Caveat）」的資安極限與通報 SOP。
  - **驗收標準（DoD）**：產出 `docs/mercenary-spyware-forensic-guide.md`，具備標準 Markdown 結構與威脅鑑識對比表；以 `Test-Path docs/mercenary-spyware-forensic-guide.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-32`**｜**[優先級：中]** 實作「端點鑑識日誌與 IoC 威脅指標離線比對審查工具」於 `tools/audit_forensic_ioc.py` 與單元測試
  - **目標範圍**：`tools/audit_forensic_ioc.py` 與 `tests/test_audit_forensic_ioc.py`
  - **具體做法**：
    1. 實作離線 IoC 威脅比對 CLI 工具，支援讀取 STIX2 / JSON / YARA 格式之公開威脅指標。
    2. 掃描輸入的系統記錄（如 Hosts 檔、DNS 快取文字、歷史連線 IP/Domain、檔案雜湊 SHA256）。
    3. 產出結構化 Markdown / JSON 鑑識報告，包含風險等級判定（High / Medium / Clean）與 CLI exit code 規範。
  - **驗收標準（DoD）**：產出 `tools/audit_forensic_ioc.py` 與對應測試；執行 `python -m unittest tests/test_audit_forensic_ioc.py` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-33`**｜**[優先級：低]** 產出標準化「個人與工程團隊端點資安防護與定期鑑識排程範本」收錄於 `templates/endpoint-forensic-audit-checklist.md`
  - **目標範圍**：`templates/endpoint-forensic-audit-checklist.md`
  - **具體做法**：
    1. 產出供個人開發者、遠端工作者與團隊運營的端點設備安全自檢手冊（包含 iOS/Android 備份產生、離線工具執行、瀏覽器歷史審查）。
    2. 提供發現潛在 IoC 命中時的緊急處置與通報應變範本（斷網、保留原始 Evidence、聯繫資安機構救援）。
  - **驗收標準（DoD）**：產出 `templates/endpoint-forensic-audit-checklist.md`，具備標準 YAML frontmatter 與完整檢核清單結構；以 `Test-Path templates/endpoint-forensic-audit-checklist.md` 驗證存在。
