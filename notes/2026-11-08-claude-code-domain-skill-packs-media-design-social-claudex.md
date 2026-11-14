---
id: 2026-11-08-claude-code-domain-skill-packs-media-design-social-claudex
title: "Claude Code 垂直領域 Skill 與 MCP 生態系全盤點：影音配音聽覺自審、YouTube/IG 確定性腳本、前端反 AI Slop 五件套與 Claudex 跨模型互審"
source_url: "https://www.instagram.com/reel/DfMpBTvh_Yj/"
source_platform: "Instagram Reels & Posts (8 則同主題工作流彙整) / GitHub"
author: "Kwon 永誠 (@kwons_en)、Airi (@airi_aimagic)、Hana (@its_hana_digital)、Chloe (@chloemakesdesign)、阿幸 (@hsing.daily)、Rena 姜瑞娜 (@renakeung)、Chiara (@lynexaai)"
analyzed_at: 2026-11-08
analyzed_by: "Antigravity"
status: pending
cluster: "2"
cluster_role: "提示詞工程與上下文"
short_title: "Claude垂直領域Skill與MCP生態盤點"
tags:
  - claude-code
  - agent-skills
  - earshot
  - mmaudio
  - youtube-agent-skill
  - instagram-agent-skill
  - impeccable
  - ui-ux-pro-max
  - claudex-loop
  - anti-slop
---

# Claude Code 垂直領域 Skill 與 MCP 生態系全盤點：影音配音聽覺自審、YouTube/IG 確定性腳本、前端反 AI Slop 五件套與 Claudex 跨模型互審

- **來源連結（8 則同系列 Instagram 貼文合併分析）**：
  1. [IG Reel `DfMpBTvh_Yj` (@kwons_en：Openverse + MMAudio + Earshot 影音自動配音與聽覺自審)](https://www.instagram.com/reel/DfMpBTvh_Yj/)
  2. [IG Reel `DfRwxagKLG9` (@airi_aimagic：YouTube 11 個免費 Claude Skills 經營頻道)](https://www.instagram.com/reel/DfRwxagKLG9/)
  3. [IG Reel `DfKHNzYq_s7` (@airi_aimagic：Instagram 13 個 Claude Skills 寫 Reels 26 公式、回留言與草稿安全邊界)](https://www.instagram.com/reel/DfKHNzYq_s7/)
  4. [IG Post `DfPQ-yeEzYJ` (@its_hana_digital：以背景、結構與限制取代空泛 Hook/Caption 指令)](https://www.instagram.com/p/DfPQ-yeEzYJ/)
  5. [IG Reel `DebpuRpkfnw` (@chloemakesdesign：消除 AI 介面感的 5 大前端設計 Skill 與 MCP 工具鏈)](https://www.instagram.com/reel/DebpuRpkfnw/)
  6. [IG Reel `DfFHkoEOs-F` (@hsing.daily：Instagram-Agent-Skill 13 個 IG 經營專用 Skill 流程)](https://www.instagram.com/reel/DfFHkoEOs-F/)
  7. [IG Post `DfMnV6sGAUE` (@renakeung：Instagram 13 Skills + `voice.md` 口吻設定與草稿安全邊界)](https://www.instagram.com/p/DfMnV6sGAUE/)
  8. [IG Reel `DdX7C1YP5Kj` (@lynexaai：Claudex Loop 讓 Claude 與 ChatGPT/Codex 四階段互審與角色互換開發)](https://www.instagram.com/reel/DdX7C1YP5Kj/)
- **對應官方開源 GitHub 專案（主動深挖補齊）**：
  - [`Leonxlnx/earshot`](https://github.com/Leonxlnx/earshot)（4,156 Stars，MIT）& [`hkchengrex/MMAudio`](https://github.com/hkchengrex/MMAudio)（2,307 Stars，MIT，CVPR 2025）
  - [`Jakeschincariol/youtube-agent-skill`](https://github.com/Jakeschincariol/youtube-agent-skill)（4,992 Stars，MIT）
  - [`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill)（5,302 Stars，MIT）
  - [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)（146,485 Stars，MIT）、[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)（105,368 Stars，Apache-2.0）、[`21st-dev/magic-mcp`](https://github.com/21st-dev/magic-mcp)（6,414 Stars，ISC）
  - [`chaseai-yt/claudex-loop`](https://github.com/chaseai-yt/claudex-loop)（3,374 Stars，MIT）
- **當前狀態**：`🔴 未做 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-17-tasteskill-v2-anti-slop-frontend.md`](./2026-10-17-tasteskill-v2-anti-slop-frontend.md)（Taste-Skill v2 前端反 AI Slop 規則）
  - [`notes/2026-11-08-google-research-harness2-recursive-agent-harnessing.md`](./2026-11-08-google-research-harness2-recursive-agent-harnessing.md)（Google Research Harness² 8 大模組與沙盒防弊契約）

---

## 1. 核心內容摘要：5W1H 初篩與八篇貼文合併脈絡（Executive Summary）

這 8 則 Instagram 貼文在外觀上都是典型的「介紹一套 Claude Code 神級工具組合 → 留言關鍵字領取安裝連結」社群導流內容；將其背後隱藏的原始碼倉庫逐一挖出後，可歸納為 **Claude Code 垂直領域外部 Harness（Skill Packs + Deterministic CLI + MCP）的四大實戰範式**：

```
+-----------------------------------------------------------------------------------+
|               8 則 IG 貼文背後指向的 4 大 Claude Code 垂直工具鏈                  |
+-----------------------------------------+-----------------------------------------+
| 1. 影音音效合成與聽覺閉環 (DfMpBTvh_Yj) | 2. 自媒體頻道確定性經營 (5 則貼文合併)  |
|  - Openverse (500萬+ CC0 音效搜尋)      |  - youtube-agent-skill (11 Skills+6 CLI)|
|  - hkchengrex/MMAudio (畫面對齊生音效)  |  - instagram-agent-skill (13 Skills+5CLI)|
|  - Leonxlnx/earshot (AI 聽覺自審與評分) |  - voice.md 個人語氣錨點 + 結構化約束   |
+-----------------------------------------+-----------------------------------------+
| 3. 前端 UI 反 AI Slop 五件套 (DebpuRpkfnw)| 4. 跨模型四階段對抗互審 (DdX7C1YP5Kj) |
|  - UI UX Pro Max (192 規則 / 80 風格)   |  - chaseai-yt/claudex-loop              |
|  - pbakaus/impeccable (62 條決定性規則) |  - Claude 擬計畫 -> Codex 挑漏洞        |
|  - 21st MCP + Figma MCP + DevTools MCP  |  - 角色互換寫 Code + SHA256 審批指紋    |
+-----------------------------------------+-----------------------------------------+
```

---

## 2. 四大主題技術深挖與 CQR 實證剖析（Deep Dive）

### 2.1 主題一：影音剪輯自動配音與 AI 聽覺自審閉環（`DfMpBTvh_Yj`）

- **貼文主張**（`@kwons_en`）：剪片最累的是翻十幾個網站找音效、放上去還慢半拍；透過 **Openverse + MMAudio + Earshot** 三件套，讓 Claude 自己找、自己生、自己聽完修正。
- **底層開源架構查證**：
  1. **Openverse**：檢索超過 500 萬個 CC0 與開放授權音效素材。
  2. **[`hkchengrex/MMAudio`](https://github.com/hkchengrex/MMAudio)**（UIUC & Sony AI，CVPR 2025，論文 [arXiv:2412.15322](https://arxiv.org/abs/2412.15322)，2026-11-14 查證標題為 MMAudio: Taming Multimodal Joint Training for High-Quality Video-to-Audio Synthesis）：多模態聯合訓練的 Video-to-Audio 模型，內建幀級同步模組（Synchronization Module）使生成音效對齊畫面動作。
  3. **[`Leonxlnx/earshot`](https://github.com/Leonxlnx/earshot)**（`v0.4.0`，4,156 Stars，純 CPU 執行之 CLI / Python API / MCP Server）：
     - 解決 Coding Agent「會寫渲染影片的程式碼（如 Remotion），卻聽不到自己做出來的聲音是否破音或慢了 80ms」的盲區。
     - **核心指令**：`earshot describe`（輸出瞬態、衰減時間、AudioSet 標籤與峰值 dBFS）、`earshot timeline`（逐秒聽覺逐字稿，標記事件與畫面切點同步誤差）、`earshot sheet -o out.png`（輸出含頻譜、波形、響度與畫面幀的視覺化對照圖供多模態模型檢視）、`earshot critique`（對照 7 部專業產品發佈片計算 23 項評分指標與 LUFS 響度）、以及 `earshot forge` / `earshot fit`（以純程式碼合成 252 種無版權音效）。

### 2.2 主題二：YouTube 與 Instagram 確定性自媒體工作流（`DfRwxagKLG9`、`DfKHNzYq_s7`、`DfFHkoEOs-F`、`DfMnV6sGAUE`、`DfPQ-yeEzYJ`）

這 5 則貼文共同圍繞同一位作者 **Jake Schincariol** 開源的姊妹專案與結構化提示詞原則（其中 `@airi_aimagic` 分別以 `DfRwxagKLG9` 介紹 YouTube 11 Skills、以 `DfKHNzYq_s7` 介紹 Instagram 13 Skills 的 `/ig-reel` 26 種開頭公式打分、`/ig-comment`、`/ig-reply`、`/ig-profile`、`/ig-plan`、`/ig-viral` 與「只寫草稿、不給 IG 密碼」之安全邊界）：

| 專案名稱 | 規模與指令數 | 內建零依賴 Python 確定性工具 | 關鍵設計亮點與 CQR 實測限制 |
| :--- | :--- | :--- | :--- |
| **[`Jakeschincariol/youtube-agent-skill`](https://github.com/Jakeschincariol/youtube-agent-skill)** (4,992★) | 11 個 Skills（`/yt-script`, `/yt-package`, `/yt-edit`, `/yt-comment`, `/yt-plan`, `/yt-viral`, `/yt-retention`, `/yt-shorts`, `/yt-seo`, `/yt-chapters`, `/yt-audit`） | 6 支：`hookscore.py`、`title.py`、`deadair.py`、`chapters.py`、`retention.py`、`swipe.py` | - 將「標題＋縮圖」視為單一點擊面聯合檢查（`title.py` 抓重複與截斷）。<br>- `deadair.py` 直接把 `.srt` 逐字稿轉成標好秒數的剪輯決策清單（EDL）。<br>- `swipe.py` 不看絕對觀看數，而是計算**超越該頻道自身中位數的倍數（Outlier Multiple）**。 |
| **[`Jakeschincariol/instagram-agent-skill`](https://github.com/Jakeschincariol/instagram-agent-skill)** (5,302★) | 13 個 Skills（`/ig-reel`, `/ig-viral`, `/ig-caption`, `/ig-carousel`, `/ig-story`, `/ig-profile`, `/ig-plan`, `/ig-human`, `/ig-comment`, `/ig-reply`, `/ig-dm`, `/ig-repurpose`, `/ig-audit`） | 6 支：`hookscore.py`、`beats.py`、`caption.py`、`humanize.py`、`detect.py`、`swipe.py` | - `beats.py` 依 165 wpm 估算每句台詞秒數，抓出「超過 3 秒才進主軸」與「單一畫面停滯超過 4 秒」的流失點。<br>- `caption.py` 模擬 IG 動態牆**前 125 字元折疊視窗**，並強制執行 2025/12/18 生效的 **5 個 Hashtag 上限**。<br>- `humanize.py` 自動清除 18 類複製貼上隱藏字元、破折號與 154 個套話（`slop.json`）。 |

- **CQR 實證亮點（作者於 README 誠實公開的負面實驗結果）**：
  1. **`hookscore.py` 能抓出爛開頭（AUC `0.83`），但無法預測爆款（AUC `0.56`）**（出處：[instagram-agent-skill README](https://github.com/Jakeschincariol/instagram-agent-skill#readme) 第 225-242 行附近的實測段落；該段說明 74 筆語料是 YouTube Shorts 的前 3 秒自動字幕，非 Reels，且為作者自述、本筆記未重現；此數字僅屬 IG 庫，不套用於上方 YouTube 庫那一列）：在 74 支真實短影音上，五項評分維度中只有 `SPECIFICITY`（具體數字或專有名詞）能有效區分高低表現（中位數差 60 分），`STAKES` 與 `ADDRESS` 中位數完全相同。
  2. **草稿唯讀鐵律（Nothing gets posted until you say yes）**：兩個專案皆刻意不接自動發文爬蟲，避免違反平台條款遭封鎖，且未知數據一律輸出 `{{your number}}` 佔位符，絕不捏造案例數據。
  3. **`voice.md` 與具體約束（對應 `@its_hana_digital` `DfPQ-yeEzYJ`）**：必須先提供 3 支過往影片或填寫 `~/.claude/{youtube,instagram}/voice.md` 建立個人語氣、受眾與禁忌詞，才能消除千篇一律的 AI 腔調。

### 2.3 主題三：消除「一眼 AI 介面」的前端設計五件套（`DebpuRpkfnw`）

- **貼文主張**（`@chloemakesdesign`）：Claude 做出來的介面充滿紫色漸層與卡片套卡片，不是 Prompt 問題，而是少了「先定風格、最後再檢查」的 5 個工具：
  1. **[`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)**（146,485 Stars）：提供 192 條設計推理規則（2026-11-14 查證：README 寫 192 Reasoning Rules）與 80 種可搜尋 UI 風格（2026-11-14 查證：README 寫 80 searchable styles，其中 51 種為 active），開工前先鎖定配色與字體階層。
  2. **[`pbakaus/impeccable`](https://github.com/pbakaus/impeccable)**（Paul Bakaus 開源，105,368 Stars）：提供 24 個設計引導指令（如 `/impeccable bolder`、`quieter`、`critique`、`audit`、`harden`）與 **62 條零 LLM 決定性反 AI Slop 規則**（`npx impeccable detect`，直接攔截 Inter 濫用、藍紫漸層、巢狀卡片、低對比度）。
  3. **[`21st-dev/magic-mcp`](https://github.com/21st-dev/magic-mcp)**（現已升級為 **21st MCP**，2026-11-14 查證：repo 說明寫「Magic MCP is now the 21st MCP」，`npx @21st-dev/cli@latest init`，6,414 Stars）：直接在編輯器內搜尋 10,000+ 個高品質 React/Tailwind 元件。
  4. **Figma MCP**：選取設計稿畫框直接轉為結構化元件程式碼。
  5. **Chrome DevTools MCP**：讓 Agent 自動開啟真實瀏覽器檢查渲染結果與響應式破版並自行修正。
- **重要資安發現（`pbakaus/impeccable` Live Mode 無沙盒風險）**：
  - 查閱 `pbakaus/impeccable` 官方 README 第 72 行發現：當執行 `/impeccable live` 並在瀏覽器按 Apply 時，若聊天 session 超過 1 分鐘未輪詢，它會自動從 `PATH` 啟動 `codex` 或 `claude`，**並預設加上 `--dangerously-bypass-approvals-and-sandbox` 或 `--permission-mode bypassPermissions` 完全關閉沙盒與審批**，還會在陌生 repo 執行 `package.json` 的 `impeccable:manual-edit-validate`。
  - **防護做法**：必須在啟動環境設定 `IMPECCABLE_LIVE_COPY_AGENT=chat` 或 `off`，且在無人值守執行時留意 Claude Code 的 Command Hooks 會在模型審批之外自動執行。

### 2.4 主題四：Claudex Loop 跨模型四階段計畫硬化與角色互換（`DdX7C1YP5Kj`）

- **貼文主張**（`@lynexaai`）：透過開源專案 **Claudex Loop** 讓 Claude 與 ChatGPT/Codex 協同工作，先擬計畫再由另一方挑漏洞，寫程式時雙方互換角色。
- **底層開源架構查證（[`chaseai-yt/claudex-loop`](https://github.com/chaseai-yt/claudex-loop)，3,374 Stars，前身為 `grill-me-codex` / `crucible`）**：
  1. **核心鐵律：「Whoever built it never grades it（建造者絕不自己評分）」**。
  2. **四階段工作流**：
     - Phase 1 `Recon`（環境與程式碼盤點）→ Phase 2 `Interrogate`（需求追問對齊）→ Phase 3 `Adversarial Plan Review`（跨模型挑戰計畫，綁定計畫檔路徑與 `SHA256` 雜湊，任何後續修改即令核准失效）→ Phase 4 `Cross-Model Build & Inspection`（角色互換實作與獨立驗收，綁定 pre-build commit 與變更指紋）。
  3. **沙盒與權限隔離**：審查階段（Review）強制在唯讀沙盒運行，並關閉使用者自訂 Plugins、Apps 與外部 MCP Servers，防止審查者在唯讀 Shell 外產生副作用。
  4. **與本庫現有技能對映**：本庫環境已內建 `/grill-me`、`ai-review`（跨模型二審）與 `blind-review`（盲審子代理），可吸收 Claudex Loop 的「計畫 SHA256 指紋鎖定」與「Review 階段關閉非必要 MCP」機制。

---

## 3. 拆解待辦事項（Action Items）

- [ ] **`T-20261108-04`**｜**[優先級：高]** 撰寫《Claude Code 垂直領域 Skill 與 MCP 生態系盤點及安全採納規範》，並實作 `tools/verify_agent_skill_pack_safety.py` 靜態審計器
  - **目標範圍**：`docs/claude-code-domain-skill-packs-and-mcp-audit.md`、`tools/verify_agent_skill_pack_safety.py`、`tests/test_verify_agent_skill_pack_safety.py`
  - **具體實作步驟**：
    1. 撰寫 `docs/claude-code-domain-skill-packs-and-mcp-audit.md`，完整整理 8 則 IG 貼文對應之四大垂直領域開源專案（`earshot`/`MMAudio`、`youtube-agent-skill`/`instagram-agent-skill`、`ui-ux-pro-max`/`impeccable`/`21st-mcp`、`claudex-loop`）架構、CQR 實證數據（`hookscore.py` AUC `0.83` vs `0.56`）與安全邊界。
    2. 實作 `tools/verify_agent_skill_pack_safety.py`，以 `--pack` 對技能包實際檔案做靜態啟發式掃描（通過不代表安全，仍需人工審查），並保留四條自填宣告檢查項目（不能當作採納依據）：`SKILLPACK-001`（攔截 `--dangerously-bypass-approvals-and-sandbox` / `bypassPermissions` 與 Impeccable Live Mode 背景自動提權）、`SKILLPACK-002`（背景 Hook 審查與 `DO_NOT_TRACK=1` / `telemetry: false` 閘門）、`SKILLPACK-003`（社交平台 `human_publish_only` 草稿唯讀與 `{{your number}}` 零虛構數據佔位符）、`SKILLPACK-004`（確定性本地 Linter 支撐與反 `100% undetectable` 誇大宣稱）。
    3. 撰寫 `tests/test_verify_agent_skill_pack_safety.py` 涵蓋四條規則之正反例單元測試。
  - **驗收標準（DoD）**：
    - `python tools/verify_agent_skill_pack_safety.py` 回傳 `[PASS]`（exit 0）。
    - `python -m unittest tests/test_verify_agent_skill_pack_safety.py -v` 全數通過。
    - `python tools/build_index.py` 與 `python tools/verify_inbox.py` 契約及 100% 目錄覆蓋率驗證通過。
  - **實作紀錄 / 證據**：已完成 `docs/claude-code-domain-skill-packs-and-mcp-audit.md`、`tools/verify_agent_skill_pack_safety.py` 與 `tests/test_verify_agent_skill_pack_safety.py`；執行 `python tools/verify_agent_skill_pack_safety.py` 輸出 `[PASS] Agent Skill Pack 安全與決定性審計通過（共檢驗 5 組工具鏈）。`，單元測試 `Ran 6 tests — OK`。 **退回（2026-11-14，獨立審查）**：`tools/verify_agent_skill_pack_safety.py:198` 只做固定子字串比對，`--permission-mode=bypassPermissions`、雙空白、Tab 都繞得過；:219、:260 只檢查自填的 JSON，完全不掃第三方技能包的實際檔案，不能當全域規則第 15 條的採納關卡；刪掉旗標檢查沒有任何測試變紅。

- [ ] **`T-20261108-06`**｜**[優先級：中]** 新增 `tools/check_external_refs.py`：掃描 `notes/` 內的 GitHub repo 與 arXiv 連結，確認存在、是否改名或封存
  - **目標範圍**：`tools/check_external_refs.py`、`tests/test_check_external_refs.py`、`docs/evidence/external-refs-check-2026-11.md`
  - **具體做法**：
    1. 掃 `notes/*.md`（略過程式碼圍欄），抽出 `https://github.com/<owner>/<repo>` 與 `arxiv.org/(abs|pdf)/<id>`，去重；同一行含「（私有）」的 repo 跳過。
    2. 用 `gh api repos/<o>/<r>` 查（無 gh 時退用 urllib 加 `GITHUB_TOKEN`）：404 記錯誤、改名（301 或回傳的 full_name 不同）記警告、archived 記警告；arXiv 用 HEAD 請求，404 記錯誤。
    3. 查詢函式可注入，測試用假回應、不連網；支援 `--offline`（只列清單）與 `--cache <檔>`。
    4. 不接 CI（會連網、有 rate limit），只當人工巡檢與派工驗收用，在 `AGENTS.md` 寫作鐵律補一行用法。
  - **驗收標準（DoD）**：`python -m unittest tests/test_check_external_refs.py` 全綠，至少涵蓋 404 → exit 1、改名 → exit 0 且有警告、「（私有）」被略過、arXiv 404 → exit 1；實跑 `python tools/check_external_refs.py --notes notes` 的摘要存成 `docs/evidence/external-refs-check-2026-11.md`（總數與失敗清單，失敗要逐條處理）；`python tools/verify_inbox.py` 通過。
  - **完成日期**：
  - **實作紀錄 / 證據**：
