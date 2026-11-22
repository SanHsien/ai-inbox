---
id: 2026-10-19-android-official-skills-google-coding-agent
title: "Google Android 團隊官方 30 個 Agent Skills 解構：終結過時 API 幻覺、Jetpack Compose 遷移、Play Billing 審查與跨終端（Wear/TV/Auto/XR）開發閉環"
source_url: "https://github.com/android/skills"
source_platform: "GitHub / 社群貼文"
author: "Google Android Team (@android)"
github_repo: "https://github.com/android/skills"
analyzed_at: 2026-10-19
analyzed_by: "Antigravity"
status: done # pending | in-progress | done | archived
cluster: "3"
cluster_role: "外掛生態與設定治理"
short_title: "Google Android 官方 Agent Skills"
source_review: partial
source_reviewed_at: 2026-11-18
source_review_note: "原貼文搜尋不到（試過：Threads 站內搜尋「android/skills」「Android 官方 Skills 30」、Facebook 貼文搜尋「android/skills Google Android 官方 Agent Skills」「github.com/android/skills」「Android 官方 30 個 Skills android skills add」；唯一主題相同的是 Facebook 工程師米奇 2026-04-21 的貼文，已點開讀完，內容與本筆記對不上，不是來源）；2026-11-18 第二輪查轉引與存檔仍沒有（新試：網頁搜尋、Bing、Threads 站內搜尋 4 組、X 站內搜尋、GitHub 全站 issue 搜尋、Hacker News、Wayback；Reddit 被擋查不了；X 上找到 10-16 到 10-19 四則中文介紹文，都已開啟讀完，各對上一部分但無法認定，見第 0 段；另用 GitHub API 查到 v1.0.15 於 2026-10-14 發布時正好 30 個技能、repo 於 10-16 上 GitHub Trending 且當時 8k 星，可推定原貼文發在 10-16 到 10-19 之間）；替代來源官方 repo 的 2 則 issue 內文與 8 則回覆已讀完，README 無圖"
source_images: 0
source_replies: 10
tags:
  - android-skills
  - jetpack-compose
  - google-play-billing
  - security-audit
  - agent-skills
  - android-cli
---

# Google Android 團隊官方 30 個 Agent Skills 解構：終結過時 API 幻覺、Jetpack Compose 遷移、Play Billing 審查與跨終端（Wear/TV/Auto/XR）開發閉環

- **來源連結**：[android/skills (GitHub)](https://github.com/android/skills) ｜ [Android Developer 官方文檔](https://developer.android.com)
- **發布平台 / 原作者**：`GitHub / 社群貼文` / `Google Android Team (@android)`
- **分析日期**：`2026-10-19`
- **當前狀態**：`🟢 已完成 (Done)`

---

## 0. 原始資料盤點

> 2026-11-18 第二輪（查轉引、存檔）：仍找不到原貼文，維持 `partial`；但查到一項可以佐證貼文說法的資料。
>
> - **各管道結果**：
>   - 有結果：X 站內搜尋（「Android Skills」加 30 或 Compose、限中文、2026-10-13 到 10-20，找到 4 則；只搜 `android/skills` 加日期的那一組回來的全是無關貼文）、GitHub 全站 issue 搜尋 repo 網址（10 月有 63 則，其中 GitHub Trending 每日摘要在 10-17、10-18 兩天收錄本 repo）、GitHub API 查各版本技能數、Wayback（只存了 `@Zen_with_AI` 那則）。
>   - 沒結果：網頁搜尋兩組、Bing 搜尋、Threads 站內搜尋 4 組（「Android Skills 30 Compose Play Billing」「Android 官方 Skills Wear XR」「Android 官方 skills Google agent 過時」「安卓 skills Google 官方 Compose」）、Hacker News、Wayback 對其餘候選。
>   - 查不了：Reddit（三種方式都被擋）。
> - **這個 repo 在 2026-10-16 衝上 GitHub Trending**，10-16 到 10-19 之間 X 上有一波中文介紹文。四則都已開啟讀完全文、圖與回覆，**各對上一部分，沒有一則能認定是來源**：
>   - `@ai_fengshou` 10-16，<https://x.com/ai_fengshou/status/2111106137336807599>：說 Google 承認有些 Android 工作 LLM 寫不好、所以自己寫了標準答案，當天上 Trending，專攻評測裡模型出錯的地方，Claude Code 一條指令裝上。1 張圖是 repo 分享卡，顯示 **8k 星**、8 位貢獻者、35 則 issue；3 則回覆，其中一則也說「8k 星的標準答案」。對得上「8K+ Stars」與「針對實測出的盲區」；對不上的點：寫的是「20 多個技能包」不是 30，沒有 Play Billing、Wear／TV／XR，也沒有 `android skills add --all`。
>   - `@Zen_with_AI` 10-19，<https://x.com/Zen_with_AI/status/2111921006613069944>：說 Android 官方下場給 AI agent 發外掛，涵蓋 Compose、CameraX、Navigation、R8、AGP 9 升級、Wear、TV、XR 眼鏡，附 Claude Code 外掛安裝指令。無圖，計數 4 則回覆、顯示 2 則（一則希望別再亂改 Gradle）。對得上「官方下場」的語氣與 Wear／TV／XR；對不上的點：沒有 30 個、星數、Play Billing，安裝指令也不同。
>   - `@Evan_Lin` 10-18，<https://x.com/Evan_Lin/status/2111791064181031035>：繁體的每週熱門專案摘要，說這個 repo 能杜絕 AI 產生過時或反模式的 Android 程式碼。無圖無回覆。對得上「終結過時 API」的說法；對不上的點：它把內容說成 UI／Domain／Data 分層、Hilt、StateFlow 的架構指南（官方目錄沒有這些技能），沒有 30 個、Play Billing、跨裝置。
>   - `@ygqz666` 10-17，<https://x.com/ygqz666/status/2111431033740566555>：只講 edge-to-edge 單一技能怎麼裝怎麼用，1 張圖沒有放大看，0 則回覆。與本筆記的全景式寫法對不上。
> - **推測**：本筆記的原貼文應該是同一波裡把上面幾種說法併在一起的另一則貼文（Threads 或 Facebook），這次沒找到。
> - **「30 個」有依據了**：用 GitHub API 列 `android/skills` 各版本標籤的檔案樹，**v1.0.15（2026-10-14 發布）正好是 30 個 `SKILL.md`**；前一版 v1.0.14（10-12）是 25 個，下一版 v1.0.16（10-21）起是 33 個（與 `T-20261019-05` 在 10-23 實查的 33 個吻合）。第三方轉包 repo `ya123-4/android-skills-dsh`（2026-10-18 建立）的說明也寫「android/skills 1.0.15 共 30 個技能」。
> - **對分析的影響**：
>   - 貼文的「30 個」在當時是正確數字，不是誇大或筆誤；1.1 節「貼文當時稱 30 個」的寫法不用改。
>   - 「8K+ Stars」也有旁證：10-16 的 repo 分享卡就是 8k 星。
>   - 可以推定原貼文發在 **2026-10-16 到 10-19 之間**（上 Trending 之後、本筆記分析日之前），日後再找可用這個區間。
>   - `@Evan_Lin` 那則把 repo 說成分層架構與 Hilt 指南，與官方目錄不符；本筆記原稿的「State Hoisting」「Scoped Storage」等不存在的技能，可能也是這一波轉述裡走樣的，2026-11-16 已改正，不用再動。
>   - 其餘內容沒有新資料，正文不改，任務未增減。

> 2026-11-18 補讀：原貼文仍搜尋不到，維持 `partial`（搜尋方式見 frontmatter 的 `source_review_note`）。唯一主題相同的候選已點開核對，**不是來源**：
>
> - **候選貼文**：Facebook「工程師米奇」粉絲專頁 2026-04-21，<https://www.facebook.com/geekMickey/posts/pfbid02rZ5deuvNY85SYRcjphn8wEGHEWWokdF7ERWjb7Kx7J3JhtjQmGmYGCfSLVNgeooQl>。內容是介紹 Android Skills 是給 LLM 用的 `SKILL.md` 資源庫，舉的任務有 XML 遷移到 Jetpack Compose、升級 AGP 9、Navigation 3 與 Edge-to-edge、Play Billing 升級與 R8 分析；用 Android CLI 安裝，預設裝到 Gemini／Antigravity 的技能目錄，可用 `--all` 或 `--skill` 指定；提醒官方聲明 AI 會出錯，專案暫不接受外部程式碼貢獻。留言 0 則。附 1 張圖沒有放大看。
> - **為何對不上**：本筆記的「30 個」、「8K+ Stars」、Wear／TV／Auto／XR 跨裝置、Play 審查與權限等說法，這則貼文都沒有；貼文日期也比本筆記早半年。
> - **可用的一點**：貼文轉述的「預設安裝到 Gemini／Antigravity 的技能目錄」與「暫不接受外部貢獻」，沒有與本筆記衝突的資訊，正文不改。

> 2026-11-16 重審：來源是 GitHub repo，重讀了官方 README 全文、列出全部 `SKILL.md` 路徑，並讀了兩則 issue 的內文（沒有逐則讀底下回覆）。frontmatter 的平台欄寫了「社群貼文」，但筆記沒有留下那則貼文的連結，所以貼文的圖片與留言無法回頭查看。
>
> 2026-11-17 補讀：用 `gh api` 把 #61、#143 底下的回覆全部讀完（3 則＋5 則）。社群貼文沒有連結，登入也補不了，維持 `partial`。

- **作者圖片**：無。官方 README 是純文字，沒有圖片。
- **作者留言補充**（官方 README 自己的說明，原稿沒寫到的部分）：
  - **只做模型表現差的地方**：README 明說技能開發聚焦在評測顯示模型表現不佳的用例，並點名「基礎的 Jetpack Compose 最佳實踐」這種模型已經會的領域**不優先做**。
  - **Claude Code 與 Codex 有官方外掛安裝方式**：Claude Code 用 `/plugin marketplace add android/skills` 再 `/plugin install android-skills@android-skills`；Codex 有對應的 `codex plugin` 指令。
  - `android skills add` 不加 `--all` 時只會裝 `android-cli` 這一個技能；沒有偵測到任何 agent 目錄時，預設裝到 Gemini／Antigravity 的技能目錄。
  - 不接受外部貢獻，只收 issue；並附免責聲明要使用者自行複查結果。
- **網友留言重點**（issue）：
  - #61（未關閉）：有人指出 **`android-cli` 這個技能會直接叫 agent 用 `curl … | bash` 把 Android CLI 裝到使用者機器上**（系統層級安裝），而不是告知使用者、讓使用者決定；建議改成「前置需求」寫法。這與本 repo 的規則（外部來源不直接執行安裝腳本）直接相關。
  - #143（未關閉）：用 Antigravity 的外掛安裝指令直接裝這個 repo 會失敗（偵測不到外掛結構），目前仍要走 Android CLI。
  - #61 的回覆（3 則）：官方協作者 `simona-anomis` 先請回報者改到 Android CLI 的問題追蹤系統另開一單；回報者追問「各技能是不是各管各的」後，她說明每個技能有自己的負責人、repo 層也會維持一致，並表示已把問題轉交（2026-07-06）。之後沒有更新，issue 仍未關閉。
  - #143 的回覆（5 則）：沒有官方回應；內容是重貼原文、貼連結，以及一段與本 repo 無關的貢獻流程文字，沒有新資訊。
- **對分析的影響**：
  - **技能數量**：標題與正文的「30 個」是貼文當時的說法；`T-20261019-05` 於 2026-10-23 實查為 33 個；2026-11-16 再列目錄是 **37 個**。數量持續增加，標題保留原貼文說法，正文已加註。
  - **星數**：原稿寫 8K+，2026-11-16 查 GitHub API 為約 1.06 萬。授權 Apache-2.0 無誤。
  - **1.1 架構圖與 1.2 第 3 點的技能內容有幾處與實際目錄不符，已在 1.2 末尾加一段「與實際目錄對照」**：
    - 沒有「Scoped Storage／Photo Picker」「執行期權限流水線」這樣的技能；安全類實際是 `android-intent-security` 與 `android-permissions-security` 兩個。
    - Compose 類實際是 XML 轉 Compose 遷移、Compose 效能、自適應版面、手寫筆跡（ink）；沒有教「State Hoisting 基礎」的技能，官方還明說基礎 Compose 不優先做。
    - 車用只有「停車時可用的 app」一個技能，不是完整的車載範本 API；TV 是 Leanback 轉 Compose for TV 的遷移；XR 是顯示型眼鏡與投影硬體兩個技能；Wear 是 Compose Material 3 與小工具。
    - 原稿沒提到的類別：裝置端 AI（AppFunctions、LiteRT、ML Kit GenAI）、AGP 9 升級、CameraX、身分驗證、Media3 Cast、iOS 轉 Android、ANR 稽核、R8 分析、Profiler、edge-to-edge、Glance 小工具、測試環境設定。
  - **新增一項風險提醒**：`android-cli` 技能會指示 agent 自動執行安裝腳本（issue #61）。已完成的 `T-20261019-06` 當時就是自行審查安裝腳本後改用暫存沙盒手動下載，做法與這則 issue 的顧慮一致，不需重開；日後若用官方外掛方式整包安裝，要留意這個技能。
  - **2026-11-17 補讀結果**：官方已知 #61 的自動安裝問題並轉交，但四個多月沒有修正；#143 仍無官方支援。上面的風險提醒與結論都不變，任務未增減。

---

## 1. 核心內容摘要

### 1.1 核心主張：官方跳下來帶路，解決 AI 開發 Android App 的「過時知識詛咒」

在軟體工程領域，Android 開發以其**高頻迭代、嚴格生命週期與快速棄用舊 API** 聞名。通用大語言模型（如 GPT-4o、Claude 3.7、Gemini 2.5）由於訓練資料中包含大量 2015~2022 年的歷史舊代碼，在生成 Android 程式碼時經常出現嚴重幻覺：
1. **死守廢棄 XML**：依舊熱衷生成 `findViewById`、舊版 XML 佈局與複雜的 `FragmentTransaction`，而非現代標準的 **Jetpack Compose** 宣告式 UI；
2. **踩雷 Google Play 審查**：使用已被官方強烈警告甚至禁止的 Play Billing 舊版 API，忽略了 Google Play Console 對隱私權限與資料安全聲明的嚴格要求，導致上架即被退件；
3. **權限處理漏洞**：忽略 Android 13/14/15 逐步收緊的 Scoped Storage、照片選擇器（Photo Picker）與細微化通知權限；
4. **跨設備生態盲區**：對 Wear OS（手錶）、Android TV（電視）、Android for Cars（車載系統）以及新興的 Android XR（延展實境眼鏡）缺乏架構規範認知。

為了徹底解決這些卡關痛點，**Google Android 官方團隊親自打造並開源了 `android/skills`**（分析當時 8K+ Stars，2026-11-16 約 1.06 萬；Apache-2.0 協議），針對團隊評測出模型表現不佳的用例釋出標準化 Agent Skills（貼文當時稱 **30 個**；2026-10-23 實查 33 個，2026-11-16 為 37 個），透過一條指令：
```bash
android skills add --all
```
即可讓本機的 AI Coding Agent（Claude Code, Cursor, Codex, Antigravity）直接載入官方最佳實踐。

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Google Android 官方 Agent Skills 體系全景              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 現代架構與 UI 現代化 (Modern UI & Architecture)                     │
│    └─ XML 遷移至 Jetpack Compose: 狀態提升、重組優化、自定義 Layout      │
│    └─ Navigation 3 / 現代單一 Activity 架構規範                         │
│                                                                        │
│ 2. 商業化與 Google Play 政策合規 (Billing & Play Policy Gate)           │
│    └─ Play Billing 升級: 訂閱、單次購買、購買憑證校驗與防沉迷政策對照    │
│    └─ Target SDK 政策即時校驗: 避免上架時被 Google Play 拒絕            │
│                                                                        │
│ 3. 系統權限與防禦性安全審查 (Permissions & Security Audits)             │
│    └─ Scoped Storage / 照片選擇器 (Photo Picker) 規範化接入             │
│    └─ 執行期權限請求流水線 (Runtime Permissions Pipeline)               │
│                                                                        │
│ 4. 跨終端與多形態設備適配 (Multi-Form-Factor Ecosystem)                 │
│    ├─ Wear OS: 圓形錶面自適應、Tiles (方塊) 與 Complications (複雜功能) │
│    ├─ Android TV: D-Pad 焦點導航與 Leanback 介面最佳實踐                │
│    ├─ Android Auto / Cars: 駕駛安全限制與車載範本 API                    │
│    └─ Android XR: 空間運算 (Spatial Panels) 與 3D 沉浸式互動           │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 核心技能矩陣與工作流解構

```
[Android 官方 Skills 驅動的 Agent 開發流]

  +-----------------------+
  |  使用者需求 / 現有專案 |
  +-----------+-----------+
              |
              v
  +-----------------------+
  | android skills 檢索   | ===> 匹配 30 個精準技能手冊 (SKILL.md)
  +-----------+-----------+
              |
      +-------+-------+---------------+---------------+
      |               |               |               |
      v               v               v               v
  [Compose 遷移]  [Play Billing]   [權限安全檢查]   [跨終端適配]
  ・消除 XML 佈局  ・替換舊 API     ・Scoped Storage ・Wear OS Tiles
  ・狀態提升設計  ・Play 政策檢查  ・Photo Picker   ・TV D-pad 焦點
  ・重組效能調優  ・收據合規校驗   ・最小權限原則   ・XR 空間面板
      |               |               |               |
      +-------+-------+---------------+---------------+
              |
              v
  +-----------------------+
  |  官方架構約束與驗證   | ===> 嚴禁過時代碼、自動附帶 Lint 規則
  +-----------+-----------+
              |
              v
  +-----------------------+
  | 快速編譯與真機/AVD測試| ===> 透過 android CLI 部署至模擬器驗證
  +-----------------------+
```

1. **模組化 SKILL.md 設計（Modular & Token-Efficient）**：
   - 每個 Skill 獨立封裝於標準的 `SKILL.md` 中，僅在 Agent 偵測到相關意圖（如「把這個 layout.xml 改成 Compose」或「實作訂閱扣款」）時才被按需載入（On-demand Context Injection），大幅節省 Context Window 與 Token 消耗。
2. **與 Android CLI 的無縫閉環**：
   - 不僅提供純靜態知識，還與官方 `android` 命令列深度綁定：
     - `android skills list`：列出環境中所有已安裝與可用的官方技能。
     - `android skills add <skill-id>`：精準拉取單一模組（例如 `r8-analyzer`、`compose-migration`）。
     - `android layout` / `android screen`：為 Agent 提供即時 UI Layout Tree 檢查與截圖座標識別能力。
3. **四大高頻卡關領域專題拆解**：
   - **Jetpack Compose 遷移**：直接注入官方 State Hoisting、Remember/DerivedStateOf 與 Compose Compiler 最佳化規則，避免生成無窮重組（Infinite Recomposition）的無效代碼。
   - **Play Billing 與政策合規**：對齊最新的 Play Billing Library，並在代碼層級提供政策檢查清單（Checklist），在開發期就攔截違規行為。
   - **安全與權限審查**：強制依循最小權限原則（Principle of Least Privilege），主動將高危權限替換為系統級 Picker 或無權限替代方案。
   - **多元硬體設備適配**：涵蓋智慧手錶（Wear OS）、智慧電視（Android TV）、車用系統（Android Auto）及空間計算（Android XR），消除跨平台開發障礙。
4. **與實際目錄對照（2026-11-16 補，以官方 repo 目錄為準）**：
   - 上面的分類是依貼文敘述整理的，部分項目在官方目錄裡沒有對應技能（例如 Scoped Storage、Photo Picker、執行期權限流水線、State Hoisting 基礎）。官方 README 明說只做模型表現差的用例，基礎 Compose 不優先。
   - 實際 37 個技能的類別：建置系統（AGP 9 升級）、相機（CameraX）、車用（停車時可用的 app）、裝置端 AI（AppFunctions、LiteRT、ML Kit GenAI）、開發工具（android-cli）、身分驗證、Compose（自適應、ink、效能、XML 遷移）、媒體（Media3 Cast）、iOS 轉 Android、導覽（Navigation 3、navigation-event）、效能（ANR 稽核、R8 分析）、Play（Engage SDK、Billing 升級、政策洞察）、Profiler、安全（intent、permissions）、系統（edge-to-edge、Glance）、測試、TV（Leanback 轉 Compose）、Wear（Compose M3、小工具）、XR（顯示型眼鏡、投影硬體）。
   - Claude Code 可用官方外掛方式安裝：`/plugin marketplace add android/skills`、`/plugin install android-skills@android-skills`。注意 `android-cli` 技能會指示 agent 直接執行安裝腳本（官方 issue #61），整包安裝前先看過。

---

## 2. 對現有工作流與專案之啟發

1. **直接增強本地 `android-cli-plugin` 實用價值**：
   - 本地環境已預裝 `android-cli-plugin`（位於 `~/.gemini/config/plugins/android-cli-plugin`），該外掛完整宣告了 `android skills`、`android sdk`、`android emulator` 等指令。
   - 將 `android/skills` 官方庫與本地工具鏈結合，可直接在本機搭建出企業級的 Android AI 開發流水線。
2. **借鑑「官方技能包（Domain Expert Skills）」組織模式**：
   - Android 官方的 30 個 Skills 模式為特定技術領域（如 iOS、Flutter、React Native 或後端特定框架）提供了一個完美的典範：**不是靠模型大海撈針，而是由官方/領域專家將常見卡關點抽象為 30 個高內聚、低耦合的 `SKILL.md` 規則庫**。

---

## 3. 具體評估待辦事項

以下任務已同步至主倉庫 `README.md` 待辦事項清單：

- [x] **`T-20261019-05`**｜**[優先級：高]** 深度盤點 `android/skills` 官方收錄之 30 個 Skills 清單與 `SKILL.md` 規範（重點涵蓋 XML 轉 Compose、Play Billing 政策合規、安全審查與 Wear/TV/XR），整理出現代 Android 開發防幻覺手冊
  - **目標範圍**：`android/skills`、`android-cli-plugin`
  - **驗收標準（DoD）**：產出 `docs/android-official-skills-anti-hallucination.md`，盤點官方收錄之 30 個 Skills 規格、觸發情境與輸入輸出契約，重點標注 Compose 遷移與 Play Billing 政策防護清單。
  - **完成日期**：2026-10-23
  - **實作紀錄 / 證據**：以 ai-inbox 範本形式交付。直連檢驗官方 `android/skills` 倉庫，如實釐清收錄清單實為 33 個 Skills（非原宣稱 30 個），產出完整盤點與防幻覺手冊 `docs/android-official-skills-anti-hallucination.md`，深度涵蓋 16 大領域、官方相對來源路徑、XML 轉 Compose 紀律與 Play Billing 政策防線。 **2026-11-21 稽核後重做（2026-11-22 完成）**：原交付缺 DoD 的「觸發情境與輸入輸出契約」。以 GitHub API 讀 `android/skills` commit `c72942584fff970dac86ced78b367fce0c441e52` 全部 37 個 skill 主檔，於文件新增 1.1 節契約表（37 列：觸發情境、輸入／前置條件、輸出／完成判準）；第 2 節改成只列官方 `migrate-xml-views-to-jetpack-compose` 的 10 步驟與參考檔路徑、其他官方 skill 的 Compose 遷移部分，本 repo 延伸另列 2.3 節。`tools/verify_re_and_android_specs.py` 新增契約表檢查（先寫 4 個會紅的測試），`python -m unittest tests.test_verify_re_and_android_specs` 17 項通過。各 skill 的 `references/` 子檔未逐一讀。
- [x] **`T-20261019-06`**｜**[優先級：中]** 評估本地 `android-cli-plugin` 與 `android skills add --all` 之 Windows 11 安裝與整合驗證，建立自動化 Android 專案建置與 AI 輔助開發測試流水線
  - **目標範圍**：`android-cli`、本地 Android 開發環境
  - **驗收標準（DoD）**：產出 `docs/android-cli-plugin-windows-validation.md`，記錄在 Windows 11 本地終端執行 `android skills list` 與建立測試專案之完整命令輸出日誌，驗證本地 CLI 外掛可用。
  - **完成日期**：2026-10-25
  - **狀態**：✅ 完成（2026-10-25，於免改全域 PATH 之暫存沙盒解壓實跑 android skills list 與建立測試專案，完整輸出已寫入 docs/android-cli-plugin-windows-validation.md）。
  - **實作紀錄 / 證據**：完成 Google 官方安裝腳本 `install.cmd` 之安全審查，精確定位修改全域 Registry `HKCU\Environment\Path` 之違規行為。依硬閘門規範改採綠色免污染之暫存沙盒（`$env:TEMP\android-cli-sandbox`）手動下載官方輕量二進位 `android.exe`（3.03 MB），並僅在當前 PowerShell 行程注入環境變數。實跑 `android --version`（版本 1.1.16717390）、`android skills list`（成功列出 33 個官方 Skills，下載 1.2 MB）與 `android create empty-activity` 成功建立 Jetpack Compose 最小測試專案（文件清單列 42 個檔案），完整終端命令日誌與結構已固化至 `docs/android-cli-plugin-windows-validation.md`，驗證完畢已清理暫存沙盒。**覆核註記（2026-10-26）**：沙盒外的 `C:\Android` 留有 `.sdk`、`build`、`licenses`（自動接受 SDK 授權），已在文件第 4 節揭露；檔案數更正為 42。
