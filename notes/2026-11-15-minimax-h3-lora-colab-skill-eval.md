---
id: "2026-11-15-minimax-h3-lora-colab-skill-eval"
title: "killkli/minimax-h3-lora-colab-skill：透過 Google Colab CLI 驅動遠端 A100 訓練 LoRA 之 Skill 架構評估"
source_url: "https://www.threads.com/@killkli/post/Dd0ic3HkuqQ"
source_platform: "Threads / GitHub"
author: "killkli"
github_repo: "https://github.com/killkli/minimax-h3-lora-colab-skill"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity"
status: archived
cluster: 2
cluster_role: "Colab驅動LoRA"
short_title: "Colab驅動LoRA訓練Skill"
source_review: full
source_reviewed_at: 2026-11-18
source_images: 0
source_replies: 2
tags:
  - skill
  - google-colab
  - lora-training
  - minimax-h3
  - remote-gpu
  - codex
---

# killkli/minimax-h3-lora-colab-skill：透過 Google Colab CLI 驅動遠端 A100 訓練 LoRA 之 Skill 架構評估

- **來源連結**：[killkli/minimax-h3-lora-colab-skill](https://github.com/killkli/minimax-h3-lora-colab-skill)（28 Stars / 3 Forks，最後更新 `2026-09-28`）
- **發布平台 / 作者**：`GitHub` / `killkli`
- **分析日期**：`2026-11-15`
- **當前狀態**：`⚪ 封存 (Archived)`

---

## 0. 原始資料盤點

> 2026-11-18 補讀：**找回原貼文**。從作者的 Threads 個人頁往回捲到 9 月底，找到作者本人（`@killkli`）2026-09-28 的貼文：<https://www.threads.com/@killkli/post/Dd0ic3HkuqQ>。`source_url` 已改成這則貼文；原值 `https://github.com/killkli/minimax-h3-lora-colab-skill` 移到 `github_repo`。
>
> - **貼文文字**：附上本 repo 連結，說 LoRA 訓練成功；接著說大家不必照抄他的技能，只要能順利用 Colab，目前三大廠的 agent 都能很順利寫出 LoRA 來跑；成果是個人用途、不分享。
> - **作者圖片**：0 張（只有 GitHub 連結預覽卡）。
> - **留言**：貼文計數 3 則，熱門與最新兩種排序都捲到底，平台顯示 2 則已全部讀完，差 1 則登入後也不顯示。兩則都是「進度太快還沒跟上」「還沒弄清楚什麼是 LoRA」，沒有實測、反駁或更正。
> - **脈絡**：同作者前一天（09-27）另有一則介紹 `minimax-h3-colab-skill`（生成影片用，不是訓練 LoRA）的貼文，提到 Google AI Pro 帳號每月有 Colab 運算單元、搭配剛開放的 Colab CLI 就能讓 agent 直接呼叫。那則是本 repo 的前身，不是本筆記的來源，留言未讀。
> - **對分析的影響**：第 2 節那句引述確認是**作者本人**說的，不是第三方轉述，已把「未查證轉述」改成「作者自述」。作者說自己訓練成功，但 README 仍寫發布本 repo 時沒有跑過雲端訓練驗證，兩者並存；沒有第三方實測，結論（封存、不導入）不變。

> 貼文文字、作者上傳的每張圖片（含輪播）、作者留言補充、網友留言（展開到底）都要看過，見 AGENTS.md 第 3 節。

- **作者圖片**：無。README 沒有任何圖片或影片（2026-11-16 查）。
- **作者留言補充**：無。筆記第 2 節引用的「貼文指出…」原本來自一則沒有留下連結的社群貼文（2026-11-18 已找回，是作者本人的 Threads 貼文，見上）；2026-11-16 當時找不回原文，貼文的圖與留言沒看到。
- **網友留言重點**：無。repo 的 issue 與 PR（含已關閉）都是 0 則，沒有開 Discussions；星數仍是 28。
- **對分析的影響**：結論不變。重讀 README 補三點：一、`test` 指令會真的開一個遠端 GPU 探測，只驗證探測、傳輸與 Drive 路徑，不代表訓練跑得完，而且同樣耗 Colab 運算單元；二、README 自己寫明沒有官方最低 VRAM 保證、上游範例設定標示未驗證、發布本 repo 時沒有跑過雲端訓練；三、H3 流程用 Qwen3-VL 處理影像，Qwen Image 的 LoRA 權重不能拿來當 H3 的。「三大廠 Agent 都能順利寫出 LoRA」那句因貼文找不回，改標為未查證轉述。

---

## 1. 核心內容摘要與原始碼實查

- **核心目標**：封裝成 Codex Skill，讓代理協助整理、標註配對圖片資料集，並透過 **Google Colab CLI（`colab --auth=oauth2`）** 啟動遠端 Colab A100 High-RAM 實例，執行 Ostris AI Toolkit 訓練 **MiniMax H3 Ref2VA LoRA**（`.safetensors`）並備份至 Google Drive。
- **關鍵工作流設計（`SKILL.md` + `scripts/runner.py`）**：
  1. **兩階段安全切分（本地預備 vs 遠端燒額度）**：
     - `prepare` 階段只複製圖片到暫存目錄、依 Agent 產出的 `dataset-plan.json` 寫入描述與參照圖配對、生成 `dataset_manifest.json` 供人工審閱，**絕不自動上傳或覆蓋原圖**。
     - `train` 階段明確要求「必須在使用者明確要求下才啟動遠端 GPU」，且**禁止失敗後自動重試**（避免燒光 Colab 計算單元），並將 checkpoints 同步保存至 `MyDrive/MiniMax_H3_LoRAs/`。
  2. **透明標註未驗證風險與硬體門檻**：明確指出上游 AI Toolkit Ref2VA 範例標為 `unverified`，且需 60 GiB 空間與建議 48 GiB+ VRAM（A100 High-RAM）。

---

## 2. 技術評估與 Windows 11 相容性檢查

- **值得借鏡的通用架構模式**：
  - **「Google Colab CLI 作為 Agent 的免自建遠端 GPU 後端」**：作者本人在 Threads 貼文（2026-09-28，作者自述、無第三方實測）稱「只要能用 Colab，三大廠 Agent 都能順利寫出 LoRA 來跑」，其關鍵在於把本機代理與遠端算力透過官方 CLI（`usage --json` 查餘額、`test` 探測 GPU／Drive 路徑、執行 `.ipynb` 並回傳產物；`test` 會真的開遠端 GPU，同樣耗運算單元，也不代表訓練跑得完）解耦。
  - **算力／費用安全閘門**：將「資料整理（免費可逆）」與「啟動付費雲端 GPU（不可逆扣額度、禁自動重試）」硬切分，是非常乾淨的 Agent Skill 設計範式。
- **Windows 11 原生執行相容性缺口（實查 `scripts/runner.py`）**：
  - 安裝腳本 `install.sh` 為 Bash，且 `scripts/runner.py` 第 73–107 行使用 `start_new_session=True` 與 POSIX 專屬的 `os.killpg(child.pid, signal.SIGTERM / SIGKILL)` 處理超時終止；**在 Windows 11 原生 Python 環境若觸發超時會因缺乏 `os.killpg` / `SIGKILL` 而拋錯**，且預設尋址 `~/.local/bin/colab`。若要在 Windows 11 使用此模式，須改用 `subprocess.CREATE_NEW_PROCESS_GROUP` 或 `taskkill /T /F`。

---

## 3. 評估結論與待辦事項決策

- **是否納入開發／工作流待辦**：**暫不建立工程任務**（維持 `status: archived`）。
  - **理由**：目前無訓練 MiniMax H3 Ref2VA LoRA 的專案需求；保留本篇對「Google Colab CLI 遠端 GPU 驅動模式」、「兩段式計費安全閘門」以及 `runner.py` Windows POSIX 相容性提醒作為日後需要雲端 GPU 實驗時的架構參考即可。
