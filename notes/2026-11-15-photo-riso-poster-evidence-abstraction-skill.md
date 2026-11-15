---
id: "2026-11-15-photo-riso-poster-evidence-abstraction-skill"
title: "luckdvr/photo-riso-poster：證據導向抽象與 2–3 色 Riso 印刷風海報 Skill 查證評估"
source_url: "https://github.com/luckdvr/photo-riso-poster"
source_platform: "GitHub / Social"
author: "luckdvr"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: done
cluster: 2
cluster_role: "證據導向視覺Skill"
short_title: "PhotoRisoPoster海報Skill"
tags:
  - skill
  - risograph
  - visual-abstraction
  - prompt-engineering
  - image-generation
  - codex
---

# luckdvr/photo-riso-poster：證據導向抽象與 2–3 色 Riso 印刷風海報 Skill 查證評估

- **來源連結**：[luckdvr/photo-riso-poster](https://github.com/luckdvr/photo-riso-poster)
- **發布平台 / 作者**：`GitHub` / `luckdvr`（MIT License，60 Stars / 2 Forks，建立於 `2026-08-03`）
- **分析日期**：`2026-11-15`
- **當前狀態**：`🟢 已完成 (Done)`

> **安全審查與實查結果**：
> 已唯讀檢視 GitHub repo 檔案樹、[README.md](https://raw.githubusercontent.com/luckdvr/photo-riso-poster/main/README.md) 與 [SKILL.md](https://raw.githubusercontent.com/luckdvr/photo-riso-poster/main/SKILL.md)（共 73 行）。本專案為**純 Markdown 單檔規則（未附腳本、Hook 或 MCP）**。但 Markdown 會對宿主模型下指令，仍有提示詞注入、工具使用與資料傳送風險：[SKILL.md](https://github.com/luckdvr/photo-riso-poster/blob/main/SKILL.md) 要求自主呼叫生圖工具、允許重生成一次，並建議可用 EXIF 工具。本篇只做過人工閱讀，尚未跑 SkillSpector 與 agent-safety-checks 的安全檢查器，不算通過採納前的安全審查。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who（作者背景 / 執行機構）**：GitHub 開發者 `luckdvr`，靈感取自 `LiamGvchi/gc-minimal-zine-poster`（極簡 Zine 排版語法）與 `Evianis/travel-photo-abstraction`（證據優先的照片抽象方法），未夾帶兩者原始碼或圖檔。
- **What（核心產出 / 做了什麼）**：
  - 提供單一 `SKILL.md` 提示詞規格，將「照片」或「純文字主題」轉換為 2–3 色套印、帶紙張纖維與錯位油墨感（Misregistration）的 Risograph 孔版印刷檔案海報。
- **Why（為解決什麼問題 / 痛點）**：
  - 直接把照片交給生圖模型做「Riso 風格化（img2img）」，往往只是套上一層廉價數位濾鏡，保留過多雜亂背景、失去版畫節奏與留白呼吸感。
- **How（核心架構與關鍵機制）**：
  1. **Text-Only 嚴格隔離生圖（不附原圖）**：`SKILL.md` 強制規定**絕不把原照片或參考圖附給生圖工具**；必須先由主模型視覺讀取照片，記錄「主體／次要物件數量、正規化位置、比例、遮擋、方向、主軸、大面積色溫、2–3 個主色角色」與可選 EXIF 日期，再透過純文字 4 段式 Prompt（畫布紙色／油墨層與群聚／排印系統／氛圍與禁用清單）送交生圖工具。
  2. **三檔抽象度與自然語言局部微調**：支援 `faithful`（具象版畫細節）、`standard`（預設簡化剪影，人物與動物匿名化去五官）與 `minimal`（純幾何點／線／色塊，只保留數量與節奏），並允許用口語要求局部保留較多細節（如「狗要像本狗」）；但[原檔](https://github.com/luckdvr/photo-riso-poster/blob/main/SKILL.md)對人物／動物要求匿名或無五官剪影，`faithful` 只是抽象度選項，不保證認得出個體。
  3. **紙色冷暖跟隨與 65–85% 留白幾何**：冷色照片配青灰瓷白／冷雪白紙，暖色照片配淺米白紙；要求 `65–85%` 空紙留白、單一偏心視覺群聚佔 `10–25%`（禁止滿版風景與網格對齊）；這些是提示詞目標，不是量測過的樣張結果。
  4. **排印文字即證據**：禁止純裝飾文字，標記直接承載觀察結果（如數量 `x 007` / `x 024 TRUNKS`、固定詞彙 `ARCHIVE NNN` / `NO. NNN`、氣候／季節短行、2–4 個英文單字、可排成 2–4 行的短句）。「排印皆為觀測證據」只適用照片輸入；[原檔](https://github.com/luckdvr/photo-riso-poster/blob/main/SKILL.md) Input 段允許純文字主題虛構少量檔案式資訊。
- **When & Where（適用時機與場景）**：個人作品集、展覽／活動海報、攝影紀實視覺檔案，以及任何具備「讀圖＋生圖」能力的代理或對話介面（[README](https://github.com/luckdvr/photo-riso-poster/blob/main/README.md) 稱可移植到具看圖／生圖能力的平台；Antigravity `image-generator` 是否可用與如何計費未查證）。

---

## 2. 啟發與適用性評估

- **對應現有系統 / 專案**：
  - `SanHsien/agent-assets`（私有；跨平台共用 Skill 庫）、Antigravity 內建 `image-generator` subagent，以及 `C:\GitHub\ai-inbox` 視覺／設計類範本群組（Cluster 2）。
- **值得採納的核心設計方法（可跨 Skill 複用）**：
  - **「先視覺解構為結構化事實，再純文字重建」的兩階段管線**：刻意切斷 `img2img` 像素依賴，強迫模型把構圖不變量（數量、遮擋、不對稱間距、色溫角色）顯式寫進文字再生成，用意是避免 AI 視覺產出淪為「廉價濾鏡」。這是設計判斷，尚無成本或品質對照；文字轉述也會遺失細節。
  - **負向約束與自我複檢閉環**：明確列出 `Avoid` 清單（禁止滿版地面／天空、UI 純白、電影打光、3D、霓虹），並要求輸出後檢查「群聚是否過大、字詞是否拼錯、油墨是否過淡」，不達標則強化失敗規則重生成一次。
- **平台適配限制與注意事項**：
  - 原 repo 針對 Codex 內建生圖工具與 `$photo-riso-poster` 語法撰寫，且範例依賴多模態視覺讀圖與高品質文字渲染生圖模型；在 Antigravity 執行時需將「內建生圖工具」對應至 `image-generator` subagent（該 subagent 是否存在、是否免費或另耗配額，未查證），在無 EXIF 讀取工具（如純網頁端或未開 PIL/exiftool）時依規則自動略過日期行，不可偽造日期。
  - 若納入本機共用 Skill，僅取純文字 `SKILL.md`（無須下載 `examples/` 圖檔；約 17MB 為約數，未逐圖計量），且須先通過上述安全檢查。原專案為 MIT 授權，重用時仍要保留 LICENSE 與版權聲明。

---

## 3. 拆解待辦事項（Action Items）

- [x] **`T-20261115-14`**｜**[優先級：低]** 唯讀評估 photo-riso-poster 的構圖規則、授權與提示詞安全，提出是否值得納入共用 Skill 的決策
  - **目標範圍**：本 repo `docs/photo-riso-poster-readonly-assessment.md`；未來候選為 `SanHsien/agent-assets`（私有），本任務不修改該 repo 或 `~/.gemini`。
  - **具體做法**：以 GitHub contents 固定 SKILL.md、README、LICENSE 的來源與 blob SHA；審查自主工具呼叫、輸入照片／EXIF 資料流、虛構文字主題資訊及一次重生成規則。辨別照片證據與創作資訊，記錄授權保留方式；依可取得的本機官方指引確認候選安裝路徑與生圖介面，缺證據就列未查證。比較現有設計 Skill 是否已涵蓋該方法，不呼叫模型、不下載範例圖、不安裝或啟用原 skill。若日後採納外部 skill，必須先完成 SkillSpector 與 agent-safety-checks 安全檢查，不以本報告替代。
  - **驗收標準（DoD）**：上述報告存在，列來源／SHA／授權、具體風險與未查證欄位、採納或不採納的理由。若建議未來生圖，寫出兩個固定案例（純文字 standard、無 EXIF 的合成照片 minimal），每例最多初次加一次重生成；保存位置須在後續任務指明，列數量一致性、無虛構日期、短詞拼字與留白判讀方法。這只是未來驗收設計，不宣稱已有樣張或量測結果。報告與變更不得含私有內容或機密；後續實作時更新 ROADMAP、重建 README 並通過 verify_inbox。無原碼或授權證據時保持未完成，不能只靠 URL 結案。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/photo-riso-poster-readonly-assessment.md，固定 luckdvr/photo-riso-poster 7956422 與 SKILL.md、README、LICENSE 的 blob SHA，MIT 授權重用要保留聲明。十項提示詞安全風險：自主生圖、重生成、EXIF、文字分支虛構資訊、ARCHIVE 編號與自檢矛盾、README 與 SKILL.md 不一致等。比對現有設計 skill 都未涵蓋此方法；裁決不採納、不收錄，附兩個未來驗收案例。Fable 撰寫，Fable 獨立複審後修正用語；唯讀評估，未安裝、未生圖、未啟動模型。
