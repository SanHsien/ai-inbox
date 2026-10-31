---
id: 2026-10-31-zeabur-oss-installer-self-hosted-paas
title: "Zeabur 商業關站全面轉向開源：Zeabur OSS Apache-2.0、Installer 一鍵安裝、K8s 無額外狀態架構與自建私有 PaaS 實戰"
source_url: "https://www.threads.com/share/BAjeqlHOXc/"
source_platform: "Threads (@_xox._.xox._.xox._.xox._.xox_) / Zeabur OSS (oss.zeabur.com)"
author: "‎ǼǾՖ唯一ی‎ (@_xox._.xox._.xox._.xox._.xox_) / 林沅霖 (Zeabur)"
analyzed_at: 2026-10-31
analyzed_by: "Antigravity"
status: pending
cluster: 3
cluster_role: "自架PaaS生態"
short_title: "Zeabur OSS開源與Installer自建"
tags:
  - zeabur
  - zeabur-oss
  - zeabur-installer
  - self-hosted-paas
  - kubernetes-native
  - no-extra-state
  - passkey-auth
  - k3s
  - cloud-migration
---

# Zeabur 商業關站全面轉向開源：Zeabur OSS Apache-2.0、Installer 一鍵安裝、K8s 無額外狀態架構與自建私有 PaaS 實戰

- **來源連結**：[Threads 原文分享 (@_xox._.xox._.xox._.xox._.xox_)](https://www.threads.com/share/BAjeqlHOXc/) ｜ [貼文永久網址](https://www.threads.com/@_xox._.xox._.xox._.xox._.xox_/post/DfD8l9vAX0L) ｜ [Zeabur OSS 官方文檔 (oss.zeabur.com)](https://oss.zeabur.com/) ｜ [Zeabur GitHub 倉庫](https://github.com/zeabur/zeabur) ｜ [Zeabur 官方公告：Next chapter of Zeabur](https://zeabur.com/blog/next-chapter-of-zeabur)
- **核心作者**：‎ǼǾՖ唯一ی‎（@_xox._.xox._.xox._.xox._.xox_）／ 林沅霖（Zeabur 創辦人）
- **分析主題**：解構知名雲端部署平台 Zeabur 在歷經資安風波後，官方正式宣佈商業雲端服務將於 2026 年底逐步結束營運，並將平台核心資產全面重構、以 **Apache-2.0 協議開源為「Zeabur OSS」**，同時推出 **Zeabur Installer** 一鍵安裝套件。深入探討其「No Extra State（無內部資料庫、無自定義 CRD、純 K8s 原生投影）」極簡架構、WebAuthn/Passkey 安全驗證、K3s 單機與 Helm 叢集三大部署模式，以及開發者如何藉此擺脫公有雲綁定、搭建 100% 數據自主的私有 Sovereign PaaS。
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-31-zeabur-open-source-paas-architecture-analysis.md`](./2026-10-31-zeabur-open-source-paas-architecture-analysis.md)（Zeabur 開源 PaaS 架構解構：zbpack 打包與多租戶資安反思）
  - [`notes/2026-10-23-zeabur-october-2026-security-incident.md`](./2026-10-23-zeabur-october-2026-security-incident.md)（Zeabur 遭黑客攻擊事件反思：本地 OAuth 憑證、專案隔離與微服務架構）
  - [`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)（Thorsten Ball 15 條實戰哲學：端到端 SDLC 可視與無可辯駁證據）

---

## 1. 核心內容摘要：問題背景與關站轉向全景（Executive Summary）

在經歷 2026 年 8 月與 10 月中旬兩起嚴重的資安攻擊後，雲端託管平台 Zeabur 創辦人林沅霖於 2026 年 10 月 17 日發布公開信，宣佈商業雲端服務將劃下句點：
- **關站時程表**：2026 年 12 月 1 日起停止新註冊並暫停共享叢集；**2026 年 12 月 31 日**前全面關閉所有專用伺服器與 Dashboard 託管服務，並提供資料備份遷移與退款方案。
- **鳳凰涅槃：全面開源（Zeabur OSS & Installer）**：官方不將技術隨平台埋葬，而是將商業版本的完整能力重構為 **Apache-2.0 開源協議**，發布 **Zeabur OSS**（`oss.zeabur.com`）與專屬安裝器 **Zeabur Installer**。

這標誌著雲原生開發典範的根本轉移：**從「依賴中心化 SaaS 託管」走向「自建數據主權 PaaS（Self-Hosted Sovereign PaaS）」**。開發者現在只需準備一台平價 Linux 伺服器（透過 K3s）或既有的 Kubernetes 叢集，即可一鍵自建專屬部署平台，兼具 PaaS 的極致開發體驗與自託管的絕對隱私安全。

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      Zeabur OSS: Kubernetes 原生無額外狀態架構全貌                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  [ 開發者終端 / Web 介面 / Passkey 認證 ]                                                        │
│  ├─ WebAuthn / Passkeys 叢集成員身份認證 (Zeabur Identity：免密碼防釣魚)                        │
│  └─ 自然語言錯誤診斷與安全配置 UI (Zeabur Platform 控制台)                                       │
│      │                                                                                          │
│      ▼ REST / WebSocket 原生映射                                                                │
│  [ Zeabur OSS 控制平面 (Control Plane: Zero Extra State) ]                                      │
│  ├─ ★ 核心哲學：No Internal Database（不安裝 Postgres/MySQL，完全依賴 K8s 狀態）               │
│  ├─ ★ 零 Vendor Lock-in：不定義任何自定義 CRD，若 Zeabur 卸載，底層工作負載 100% 正常運行        │
│  └─ 投影映射：Namespace ──► Project ｜ Deployment/Service ──► Service                           │
│      │                                                                                          │
│      ▼ 依賴 K8s API 驅動三大引擎                                                                │
│  ├─ 1. Zeabur Builder (BuildKit 原生)：監聽 Git Webhook，在 Pod 內自動拉取並構建 OCI 鏡像       │
│  ├─ 2. Zeabur Catalog (精選模板庫)：預先驗證的 Helm Charts / YAML (Postgres, Redis, n8n 等)     │
│  └─ 3. Ingress & TLS 控制：自動配置 Traefik / cert-manager 達成免費自動 HTTPS                   │
│      │                                                                                          │
│      ▼ 三大靈活落地場景 (Deployment Modes)                                                       │
│  ├─ 模式 A (單機伺服器)：Zeabur Installer Web UI 一鍵自動配置 Linux + K3s/RKE2 + Zeabur        │
│  ├─ 模式 B (既有 K8s 叢集)：透過官方 Helm Chart 快速注入至 EKS / GKE / Civo / 自建叢集           │
│  └─ 模式 C (本地開發機)：執行 `zeaburctl ui`，以本地 `~/.kube/config` 零安裝即刻啟動控制台      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 深入技術拆解：四大核心實戰規範（Deep Dive）

### 2.1 規範一：No Extra State（無額外狀態庫）的極致雲原生架構
- **摒棄內部資料庫與自定義 CRD**：
  - 傳統自建 PaaS（如早期 Rancher、Dokku、CapRover 等）通常需要外掛複雜的 MySQL/Postgres 存儲平台元數據，一旦數據庫損毀或升級失敗，整個 PaaS 癱瘓；或定義了大量專有 CRD，導致遷移時產生嚴重的平台鎖定。
  - Zeabur OSS 採用革命性的**「純投影架構（Pure Projection Architecture）」**：它**不安裝任何專有資料庫，也不引入非標準 CRD**，直接以 Kubernetes 的原生物件（Namespace、Deployment、Service、Ingress、ConfigMap、Secret）作為單一事實來源（SSOT）。
- **零鎖定與高彈性（Zero Lock-in Guarantee）**：
  - 即使 Zeabur Pod 崩潰重啟或被徹底刪除，你的應用程式依然完全不受影響地在 Kubernetes 節點上穩定運作，標準 `kubectl` 隨時可接手控制。

### 2.2 規範二：Zeabur Identity 基於 Passkeys（WebAuthn）的身分防禦
- **終結傳統帳密外洩風險**：
  - 歷次 PaaS 資安事件中，弱密碼、撞庫攻擊與未加密憑證是主要破口。
  - Zeabur OSS 的身份模組（`Zeabur Identity`）原生整合 WebAuthn 標準，全面採用 **Passkeys（生物識別 / 實體安全金鑰 FIDO2）** 登入，從架構層杜絕釣魚攻擊與憑證竊取。
- **叢集成員權限治理**：
  - 結合 Kubernetes RBAC，實現組織內部不同工程師對專案（Namespaces）的精細化授權，兼顧多人協同與最小權限原則。

### 2.3 規範三：Zeabur Installer 三大部署模式落地
1. **單台 Linux 伺服器一鍵自建（Single Node via Web Installer）**：
   - 官方提供瀏覽器端 Web Installer 工具，僅需在一台平價 VPS（如 Hetzner、DigitalOcean、自架伺服器，建議 4GB+ RAM）上執行安裝指令：
     ```bash
     curl -fsSL https://oss.zeabur.com/install.sh | bash
     ```
   - Installer 自動檢測作業系統環境，自動拉起 K3s 輕量 Kubernetes、Traefik Ingress、Zeabur Identity 與 Zeabur Platform，5 分鐘內完成整套 PaaS 架設。
2. **既有 Kubernetes 叢集導入（Helm Chart Deployment）**：
   - 適用於企業既有雲端叢集（AWS EKS、GCP GKE 或 Civo），透過 Helm Repo 一鍵部署：
     ```bash
     helm repo add zeabur https://charts.zeabur.com
     helm install zeabur zeabur/zeabur -n zeabur-system --create-namespace
     ```
3. **本地開發者模式（zeaburctl ui）**：
   - 本地機器執行 `zeaburctl ui`，直接讀取本地 `~/.kube/config`，在瀏覽器以圖形化介面直觀管理任意連線的 K8s 叢集。

### 2.4 規範四：商業關站下的數據遷移與自託管運維策略
- **平滑遷移三部曲（Migration Playbook）**：
  1. **資料導出與快照備份**：在 2026 年 12 月 1 日前，透過 Zeabur Dashboard 或 CLI 全量備份託管的 PostgreSQL/MySQL 數據（`pg_dump` / `mysqldump`）與物件存儲數據。
  2. **憑證與 API Key 輪替**：由於平台即將退役，全面輪換在 Zeabur 環境變數中儲存的第三方服務金鑰（OpenAI, GitHub Token, Stripe 等），遵循硬閘門條款。
  3. **域名 DNS 權重割接**：在自建的 Zeabur OSS 或自託管伺服器上配置好應用後，修改 DNS A/CNAME 記錄切換流量，驗證 SSL 憑證即時生效。

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`ai-inbox` / `agent-assets`）的契合度**：
  1. **補齊「私有 Sovereign PaaS」終極落地拼圖**：
     - 本篇筆記與剛收錄的 `notes/2026-10-31-zeabur-open-source-paas-architecture-analysis.md` 構成完整閉環：前者解構了 PaaS 核心打包與資安架構，本篇則給出了**「官方停運背景下的開源重生（Zeabur OSS）與實際自建操作指南」**。
     - 解決了個人開發者與 AI Agent 在面對中心化託管服務關站時的應對策略，提供自主可控的基礎設施標準。
  2. **工程化沉澱為 K8s 資源檢驗工具與部署範本**：
     - 開發專屬的 Zeabur OSS 資源合規檢查工具（`tools/audit_zeabur_oss_k8s_spec.py`），驗證 K8s 資源配置是否符合無額外狀態標準與資安規範。
     - 產出標準化單機 K3s / Helm 一鍵部署腳本與 CLAUDE.md 運維範本（`templates/zeabur-oss-installer-setup.md`）。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261031-19`**｜**[優先級：高]** 撰寫「Zeabur OSS 與 Installer 自建私有 PaaS 落地手冊：K3s 單機安裝、K8s 無狀態架構與資料備份遷移」收錄於 `docs/zeabur-oss-self-hosted-paas-guide.md`
  - **目標範圍**：`docs/zeabur-oss-self-hosted-paas-guide.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳細整理 Zeabur 商業版關站時程（12/1 暫停、12/31 停運）與資料備份/金鑰輪替指南。
    2. 深度剖析 Zeabur OSS 的「No Extra State（無資料庫、無專有 CRD）」架構設計原則。
    3. 詳盡規範單台 Linux 伺服器使用 Zeabur Installer（K3s/RKE2）與既有 K8s 叢集 Helm 安裝步驟。
    4. 制定 Passkeys（WebAuthn）身份認證配置與 Traefik 自動 TLS 憑證流程。
  - **驗收標準（DoD）**：產出 `docs/zeabur-oss-self-hosted-paas-guide.md`，內含完整遷移時間軸、自建步驟、Helm 參數配置與安全加固指標；以 `Test-Path docs/zeabur-oss-self-hosted-paas-guide.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-20`**｜**[優先級：中]** 實作「Zeabur OSS Kubernetes 資源合規與無狀態架構驗證工具」於 `tools/audit_zeabur_oss_k8s_spec.py` 與單元測試
  - **目標範圍**：`tools/audit_zeabur_oss_k8s_spec.py` 與 `tests/test_audit_zeabur_oss_k8s_spec.py`
  - **具體做法**：
    1. 實作靜態檢查 CLI 工具，讀取 Kubernetes Manifests（YAML/JSON）檔案。
    2. 檢查是否符合純 K8s 原生物件映射規範（無非法 CRD 依賴、標籤規範、命名空間隔離、資源配額限制）。
    3. 產出結構化 JSON/Markdown 審查報告並給予 `[PASS]/[FAIL]` 判定。
    4. 撰寫單元測試覆蓋合法原生物件通過、非法 CRD 攔截、標籤缺失告警與語法異常防禦。
  - **驗收標準（DoD）**：產出 `tools/audit_zeabur_oss_k8s_spec.py` 與單元測試，執行 `python -m unittest discover -s tests` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-21`**｜**[優先級：低]** 產出標準化「Zeabur Installer 單機 K3s / Helm 一鍵部署腳本與 CLAUDE.md 運維範本」收錄於 `templates/zeabur-oss-installer-setup.md`
  - **目標範圍**：`templates/zeabur-oss-installer-setup.md`
  - **具體做法**：
    1. 產出可直接供個人 VPS 一鍵安裝 Zeabur OSS 的 Shell 腳本範本與 Helm values.yaml。
    2. 提供供 AI Coding Agent（Claude Code / Antigravity）直接執行的私有 PaaS 維運指令與自檢手冊。
  - **驗收標準（DoD）**：產出 `templates/zeabur-oss-installer-setup.md`，具備標準 YAML frontmatter 與完整配置代碼；以 `Test-Path templates/zeabur-oss-installer-setup.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **PaaS 架構解構與資安反思**：
  - [Zeabur 開源 PaaS 平台架構解構：zbpack 零配置打包與多租戶資安反思](./2026-10-31-zeabur-open-source-paas-architecture-analysis.md) ｜ 關聯任務：`T-20261031-13`、`T-20261031-14`
- **雲端資安事件與憑證審查**：
  - [Zeabur 遭黑客攻擊事件反思：本地 OAuth 憑證、專案隔離與微服務架構](./2026-10-23-zeabur-october-2026-security-incident.md) ｜ 關聯任務：`T-20261023-05`、`T-20261023-06`
- **確定性交付與 SDLC 審查**：
  - [Thorsten Ball 15 條 Agent 實戰哲學](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md) ｜ 關聯任務：`T-20261028-04`、`T-20261028-05`
