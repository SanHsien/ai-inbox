# Claude Code 垂直領域 Skill 與 MCP 生態系盤點及安全採納規範

> **對應任務**：`T-20261108-04`
> **來源筆記**：[notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md](../notes/2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex.md)
> **驗證工具**：[`tools/verify_agent_skill_pack_safety.py`](../tools/verify_agent_skill_pack_safety.py) ｜ [`tests/test_verify_agent_skill_pack_safety.py`](../tests/test_verify_agent_skill_pack_safety.py)

---

## 1. 背景與核心洞察：從「空白 Prompt」走向「確定性 Linter + 閉環驗證」

綜合 2026 年 9 月至 11 月 Instagram 上 7 則高互動 AI 工作流貼文，社群分享表面上皆採用「留言關鍵字領取連結」的私訊導流包裝，但其底層指向的 GitHub 開源專案揭示了同一條架構演進定律：

```
[舊世代：單純 Prompt 填空]
  "幫我寫一個 X 的 Hook / 做一個好看的網頁 / 配個音效"
       │
       ▼ 缺乏量化探針與感官回饋
  [AI Slop：紫色漸層、破折號氾濫、音效慢半拍、單一模型盲目自信]

[新世代：Domain Skill Pack + Deterministic CLI + Multi-Modal/Cross-Model Critique]
  1. 前置基準鎖定 (voice.md / PRODUCT.md / DESIGN.md / 192 Palettes)
       │
       ▼
  2. 確定性本地探針 (hookscore.py / humanize.py / impeccable 62 rules / earshot LUFS & sync)
       │
       ▼
  3. 雙向對抗與人工閘門 (Claudex Loop 跨模型互審 + Human-Publish Gate 草稿唯讀)
```

---

## 2. 四大垂直領域開源工具鏈完整對照矩陣

| 領域象限 | 來源 IG 貼文 | 核心開源專案 / 工具 | GitHub Stars / 授權 | 核心確定性工具與架構機制 |
| :--- | :--- | :--- | :--- | :--- |
| **A. 影音音效自動合成與聽覺自審** | [`DfMpBTvh_Yj`](https://www.instagram.com/reel/DfMpBTvh_Yj/) (`@kwons_en`) | 1. **Openverse API**<br>2. [`hkchengrex/MMAudio`](https://github.com/hkchengrex/MMAudio)<br>3. [`Leonxlnx/earshot`](https://github.com/Leonxlnx/earshot) | MMAudio: `2,307★` (MIT)<br>Earshot: `4,156★` (MIT) | - **Openverse**：檢索 500 萬+ CC0/開放授權音效。<br>- **MMAudio**（CVPR 2025）：依影片畫面幀同步合成音訊。<br>- **Earshot**：純 CPU 本地執行 CLI/MCP，提供 `describe`、`match`、`timeline`、`sheet` 與 `critique`（對照 7 部專業宣傳片計算 23 項指標、LUFS 響度與 80ms 轉場對齊誤差），以及 `earshot forge` / `fit` 程式碼合成音效。 |
| **B. 自媒體頻道經營與去 AI 味（YouTube / IG）** | [`DfRwxagKLG9`](https://www.instagram.com/reel/DfRwxagKLG9/) (`@airi_aimagic`)<br>[`DfFHkoEOs-F`](https://www.instagram.com/reel/DfFHkoEOs-F/) (`@hsing.daily`)<br>[`DfMnV6sGAUE`](https://www.instagram.com/p/DfMnV6sGAUE/) (`@renakeung`)<br>[`DfPQ-yeEzYJ`](https://www.instagram.com/p/DfPQ-yeEzYJ/) (`@its_hana_digital`) | 1. [`Jakeschincariol/youtube-agent-skill`](https://github.com/Jakeschincariol/youtube-agent-skill)<br>2. [`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill) | YouTube: `4,992★` (MIT)<br>Instagram: `5,302★` (MIT) | - **個人語氣錨點**：強制先填寫 `templates/voice.md`。<br>- **YouTube 11 Skills + 6 Python 工具**：`/yt-script`（21 公式 + `hookscore.py`）、`/yt-package`（`title.py` 標題封面聯合檢查）、`/yt-edit`（`deadair.py` SRT 轉剪輯清單）、`/yt-retention`（`retention.py` 觀眾流失點定位）、`/yt-viral`（`swipe.py` 自頻道中位數倍數排名）。<br>- **IG 13 Skills + 5 Python 工具**：`/ig-reel`（26 公式 + `beats.py` 165 wpm 秒數估算）、`/ig-caption`（`caption.py` 預覽前 125 字截斷與 2025/12 新規 5 個 Hashtag 上限）、`/ig-human`（`humanize.py` 清除 18 類零寬隱藏字元與 154 個套話詞彙 + `detect.py` 5 維度評分）。 |
| **C. 前端 UI/UX 反 AI Slop 設計工具鏈** | [`DebpuRpkfnw`](https://www.instagram.com/reel/DebpuRpkfnw/) (`@chloemakesdesign`) | 1. [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)<br>2. [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)<br>3. [`21st-dev/magic-mcp`](https://github.com/21st-dev/magic-mcp)<br>4. Figma MCP & Chrome DevTools MCP | UI UX Pro Max: `146,485★` (MIT)<br>Impeccable: `105,368★` (Apache-2.0)<br>21st MCP: `6,414★` (ISC) | - **先定風格**：`UI UX Pro Max`（192 條推理規則、80 種可搜尋 UI 風格）+ `Impeccable` `/impeccable init` 產出 `PRODUCT.md` 與 `DESIGN.md`。<br>- **元件與畫稿橋接**：`21st MCP`（原 Magic MCP，檢索 10,000+ React/Tailwind 元件）+ `Figma MCP`。<br>- **確定性收尾檢查**：`npx impeccable detect` 內建 **62 條決定性規則**（無須 LLM，直接抓出 Inter 濫用、藍紫漸層、卡片套卡片、對比度不足），搭配 `Chrome DevTools MCP` 實機渲染巡檢。 |
| **D. 跨模型四階段計畫硬化與互審** | [`DdX7C1YP5Kj`](https://www.instagram.com/reel/DdX7C1YP5Kj/) (`@lynexaai`) | [`chaseai-yt/claudex-loop`](https://github.com/chaseai-yt/claudex-loop) | `3,374★` (MIT) | - **四階段工作流**：Recon → Interrogate → Cross-Model Adversarial Plan Review → Role-Swapped Build & Inspection。<br>- **建造者不自審鐵律（Whoever built it never grades it）**：寫計畫的模型不審計畫，寫 Code 的模型不驗 Code。<br>- **雜湊鎖定與唯讀沙盒**：核准紀錄綁定計畫檔路徑與 `SHA256`（改動計畫即失效）；審查階段強制跑在唯讀沙盒並關閉外部 Plugin/MCP。 |

---

## 3. CQR 實證數據與作者誠實揭露之限制（Critical Audit）

在閱讀社群行銷貼文時，常看到「爆款引擎」「自動抓出流量密碼」等誇大宣傳；但檢視原專案作者（如 Jake Schincariol 與 Paul Bakaus）的原始碼與技術說明，有幾項極具價值的實證結論：

1. **Hook 評分器只能「淘汰爛開頭」，無法「預測爆款」**：
   - `instagram-agent-skill` 與 `youtube-agent-skill` 的 `hookscore.py` 在 5 個頻道共 74 支真實短影音（觀看數 931 至 550,000）上實測：
   - 區分「刻意寫爛的開頭 vs 真實開頭」的 **AUC 達 `0.83`**（能精準攔截以打招呼 `Hey guys` 或乞討注意力 `Stop scrolling` 開頭的廢片）。
   - 但區分「同一創作者的爆款 vs 平庸作」的 **AUC 僅 `0.56`（接近擲硬幣 `0.50`）**；五項指標中只有 `SPECIFICITY`（具體數字或名詞，中位數差距 60 分）有顯著區辨力。
2. **模板正則（Regex）與真實口語的落差**：
   - 作者最初用自己寫的模板正則去匹配真實爆款口語，命中率僅 **8%**；改用真實逐字稿重寫並補入 `Contrarian Flip`、`The Statistic`、`The Reveal`、`Someone Else's Result`、`The Superlative` 後才提升至 **49%**（其餘 51% 為無固定公式的 Podcast 切片，選擇誠實棄權）。
   - 此外，口語中的數字常拼寫為英文單字（如 `"zero dollars"`、`"three marketing books"`），只算阿拉伯數字會誤判為缺乏具體性。
3. **Humanizer 清除的是「統計套話與隱藏字元」，而非破解密碼學浮水印**：
   - `humanize.py` 移除 18 類複製貼上殘留的零寬與格式字元（Zero-width spaces/joiners、BOM、Unicode tag characters）、破折號（Em dash）與 154 個套話詞彙（`slop.json`），並拒絕捏造數據（未知數字強制輸出 `{{your number}}`）。

---

## 4. 第三方 Agent Skill 與 MCP 採納之四大安全防線（`SKILLPACK-001` ~ `004`）

深挖上述高星專案的 README 與實作，發現數個在企業或個人開發機直接安裝會踩到的資安與權限陷阱。本庫透過 [`tools/verify_agent_skill_pack_safety.py`](../tools/verify_agent_skill_pack_safety.py) 強制執行以下四條防線：

### `SKILLPACK-001`：禁止背景自動降級或繞過沙盒（No-Bypass-Sandbox-Escalation）
- **實戰案例（`pbakaus/impeccable` Live Mode 陷阱）**：
  - `pbakaus/impeccable` README 第 72 行明確記載：當使用 `/impeccable live` 並在瀏覽器點擊 Apply 時，若過去 1 分鐘內沒有活躍的聊天 session 輪詢，Live Server 會自動從 `PATH` 呼叫 `codex` 或 `claude`，並**強制帶上 `--dangerously-bypass-approvals-and-sandbox` 或 `--permission-mode bypassPermissions`**，且直接執行目標專案 `package.json` 內的 `impeccable:manual-edit-validate` 腳本。
- **機械防線**：
  1. 嚴禁在任何自動化指令中使用 `--dangerously-bypass-approvals-and-sandbox`、`--permission-mode bypassPermissions`、`--dangerously-skip-permissions`。
  2. 使用 Impeccable 時，環境變數必須固定設定 `IMPECCABLE_LIVE_COPY_AGENT=chat` 或 `off`，禁止退回無沙盒背景 CLI。

### `SKILLPACK-002`：背景 Hook 審查與遙測關閉閘門（Hook-And-Telemetry-Gate）
- **實戰案例**：
  - 在 Claude Code 中，已安裝的 Command Hooks **即使使用者拒絕了模型自身的指令也會照常執行**（`Hooks run outside model approval`），且 Impeccable 首次觸發時會自動下載二進位引擎至 `~/.impeccable/bin/` 並向 `impeccable.style` 發送方向選擇遙測。
- **機械防線**：
  1. 安裝任何帶 Hook 的 Skill 前必須先檢視其腳本內容（`hook_reviewed: true`），無人值守執行時支援以 `--settings '{"disableAllHooks": true}'` 關閉。
  2. 預設配置 `DO_NOT_TRACK=1` 與 `"telemetry": false`。

### `SKILLPACK-003`：草稿唯讀與零虛構數據閘門（Zero-Fabrication & Human-Publish Gate）
- **機械防線**：
  1. **Human-Publish Gate**：社交平台（YouTube / Instagram）Skill 一律只產出本地草稿與檢驗報告（`human_publish_only: true`），嚴禁使用第三方非官方爬蟲或無頭瀏覽器自動代發貼文、留言或私訊（避免違反平台服務條款導致封號或洩露帳號 Cookie）。
  2. **Zero-Fabrication**：遇到使用者未提供的案例數字或成效指標，強制保留 `{{your number}}` 佔位符並標記提醒，嚴禁模型自行編造數據。

### `SKILLPACK-004`：確定性本地工具支撐與反誇大宣稱（Deterministic-Linter-Backing）
- **機械防線**：
  1. 任何宣稱能改善程式碼、設計或文案品質的 Skill Pack，必須提供可離線執行的確定性檢驗腳本（如 `hookscore.py`、`detect.py`、`npx impeccable detect`、`earshot measure`）。
  2. 禁止在規範或提示詞中宣稱 `100% undetectable` 或 `guaranteed viral`。
