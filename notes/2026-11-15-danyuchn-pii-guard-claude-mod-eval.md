---
id: "2026-11-15-danyuchn-pii-guard-claude-mod-eval"
title: "danyuchn/pii-guard：台灣個資可逆遮罩與 Claude Mod 唯讀評估"
source_url: "https://github.com/danyuchn/pii-guard"
source_platform: "GitHub"
author: "danyuchn"
analyzed_at: "2026-11-15"
analyzed_by: "antigravity / Codex"
status: done
cluster: 3
cluster_role: "台灣個資遮罩Mod"
short_title: "PII-Guard個資遮罩Mod"
source_reviewed_at: 2026-11-17
source_review: full
source_images: 2
source_replies: 2
tags:
  - pii-guard
  - claude-mods
  - privacy
  - taiwan-pii
  - fail-closed
  - hookd
---

# danyuchn/pii-guard：台灣個資可逆遮罩與 Claude Mod 唯讀評估

- **來源連結**：[danyuchn/pii-guard](https://github.com/danyuchn/pii-guard)，固定 `3d55636785868785e6452e5590052571dc459659`；MIT。撤除未查證的 Stars／Forks／最後更新日期。
- **發布平台 / 作者**：GitHub / danyuchn。
- **分析日期**：2026-11-15；本輪只讀原始碼，不安裝或執行第三方工具。
- **當前狀態**：`🟢 已完成 (Done)`
- **查核證據與裁決**：[唯讀評估報告](../docs/pii-guard-readonly-assessment.md)，含固定來源與 blob SHA。
- **交叉參照**：[Claude Mods](./2026-10-18-claude-code-mods-self-extending-runtime.md)、[同作者會話模式工具](./2026-11-08-dustin-gmat-danyuchn-claude-work-mode-session-modes.md)。

## 0. 原始資料盤點

> 2026-11-17 用瀏覽器重看 GitHub repo 的 `main`（最後更新 2026-11-15，比本篇固定的 `3d55636` 新，差多少未比對）。來源是 GitHub，沒有社群貼文。

- **作者圖片**：
  - 圖 1（`docs/annotate-ui.png`）：人工補標頁的靜態截圖。一份虛構判決書，紅色標籤是自動偵測（`ORG-1`、`PERSON-1`、`LOCATION-1` 等），藍色 `MANUAL-1`、`MANUAL-2` 是使用者補遮的證人與法官；頂端顯示「9 個遮蔽、已補遮 2、已放回 0」。
  - 圖 2（`docs/annotate-demo.gif`，約 21 秒、170 格；2026-11-17 抽 10 格看完整段）：同一頁的操作動畫，另一份虛構判決書，開頭 18 個遮蔽。開頭就看得到偵測層的毛病：法院名被切成 `LOCATION-2` 加 `ORG-4` 兩個代號、被告公司名切成 `ORG-3 精密工業 ORG-2`，中間漏了一段原文；README 文字也承認這點。接下來示範補救流程：點彩色標記會跳出小框顯示原文，有「放回原文／取消」；使用者把切碎的幾段放回（計數變成 16 個遮蔽、已放回 2），公司全名恢復成明文，再選取整個名稱補遮成單一的 `MANUAL-1`；捲到文末，頁尾提示該名稱已遮蔽共 1 處，最後按「完成並關閉」（頂端為 13 個遮蔽、已補遮 1、已放回 6）。
- **作者留言補充**：issue #3 由作者以 PR #4 關閉。
- **網友留言重點**（GitHub issue，共 1 則）：
  - #3（已關閉）：回報者在 Windows 11、Python 3.13 實測，`audit_manager.py` 與 `local_workflow.py` 在模組頂層 `import fcntl`，導致 quick 模式、本機網頁入口與 4 個測試模組在 Windows 直接壞掉；核心 anonymize／restore、偵測與 eval 能跑。回報者另開了修 eval 誤報的 PR #2。
- **對分析的影響**：
  - 圖 2 的開頭畫格直接顯示偵測層會把一個機構名切碎並漏字，補強第 2 節「漏偵測仍可能被模型看見」的判斷。
  - 看完整段 GIF 後補一點：作者示範的正是「偵測切碎→人工放回再整段補遮」的補救流程，等於承認自動偵測要靠人工複核才可靠；而複核全靠使用者自己看出哪裡切錯。這與第 2 節的判斷一致，裁決不變。
  - `main` 的 README 現在有「平台支援」段：Windows 以 `msvcrt` 鎖取代 `flock`、新建私有目錄會收緊 NTFS ACL 並讀回驗證、加強模式在 Windows 以 `LOCAL_MODEL_UNVERIFIED` 拒絕。這與第 3 節「Windows 前提」的描述一致。
  - issue #3 顯示 Windows 支援是外部回報後才補上的（PR #4）；本篇固定的 `3d55636` 在 PR #4 之前還是之後，未比對。第 3 節「本機未實測」的保留維持不變。
  - 暫不採納的裁決與 `T-20261115-17` 不變。

---

## 1. 核心內容摘要（5W1H 初篩）

- **Who / What**：繁中台灣個資去識別化工具，含 Python CLI、本機網頁、hookd 與 Claude Mod。核心基於 Presidio、CKIP NER、台灣辨識器，CKIP 不可用時有 spaCy 退回路徑，不能把引擎視為等效。[src/pii_guard/pipeline/engine.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/pipeline/engine.py)
- **Why**：讓模型使用佔位符，本機保留對照表並在寫檔時還原。原文「海外方案均不支援」與「繁中圈最成熟」沒有比較證據，撤除。[README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/README.md)
- **How**：Mod 將 prompt／工具事件／壓縮事件交本機 hookd。Read／Bash／Grep／MCP 結果遮罩，Write／Edit／MultiEdit／Bash 輸入還原；預設拒 WebFetch／WebSearch／MCP，Agent／Task／Workflow 只拒 remote 模式；allowed_tools 可放寬。[examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts)、[src/pii_guard/hookd/policy.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/hookd/policy.py)

```text
prompt / 工具結果 --> Mod --> 本機 hookd --> 佔位符 --> 模型
模型工具輸入 ------> Mod --> 政策判斷 --> 還原 --> 工具 / 磁碟
                                +----> 拒絕外送
```

- **When / Where**：另行通過安全審查、可接受本機保存真值與 mapping 的文件工作流，不是全機網路或截圖防線。[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)
- **安裝指引（僅記錄，未執行）**：官方 `uv sync`，文件格式另加 `--extra formats`；Mod 用 `uv run pii-guard-hookd install --mod`，再加 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` 與 `--plugin-dir` 載入。安裝會改 Claude 設定，本輪不做。[README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/README.md)、[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)
- **Key Metrics**：未獨立實測。上游 eval 與 Edit 成功紀錄屬作者報告，不當成本機驗收。

## 2. 宣稱與證據界線

- **Edit 缺口**：作者稱 Mod 在 Edit 比對前還原；前端確實改寫參數，但沒有 host 的獨立時序證據，不宣稱徹底修復。[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)、[examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts)
- **Fail-closed**：常見錯誤回 deny／drop／skip／扣留結果；但 session.start catch 回 undefined，成功 HTTP 卻缺欄位時有保留原值分支，通用扣留深度 >12 回原值。作者所述 host 十秒 timeout 與 catch 行為未獨立驗證，不能保證所有超時都安全。[examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts)
- **壓縮與名單**：Compact 只掃已知值，不重新跑完整偵測；pii-terms 禁讀名單是指引與工具約束，未證明不能繞過。[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)、[examples/claude-code-mod/commands/pii-terms.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/commands/pii-terms.md)
- **資料不離機**：所讀 Mod／hookd 走 loopback；但漏偵測與路徑人名仍可能被模型看見，原 prompt 可能先落本機 transcript，mapping 含真值。加強稽核只連本機 Ollama，不是任意遠端 URL；依賴與模型仍需下載。[examples/claude-code-mod/README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/README.md)、[src/pii_guard/enhanced_audit.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/enhanced_audit.py)、[README.md](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/README.md)

## 3. 適用性與採納裁決

- **暫不採納／不掛 hook**：原樣 --pack 掃描退出碼 1，1 FAIL／6 REVIEW／2 未掃描圖片；FAIL 是防外連正則誤報，但不可改報掃描通過。SkillSpector 啟動失敗，沒有成功審計結果。[逐項判讀](../docs/pii-guard-readonly-assessment.md)
- **Windows 前提**：Mod 路徑順序是 options.hookdHome、PII_GUARD_HOOKD_HOME、EVAL_PII_GUARD_HOOKD_HOME、HOME；只設變數不等於相容性通過。已有 NTFS ACL／鎖與 Windows CI 定義，但本機未實測，Ollama 加強模式在 Windows 明確拒絕。[examples/claude-code-mod/hooks/register.ts](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/examples/claude-code-mod/hooks/register.ts)、[src/pii_guard/_compat.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/_compat.py)、[.github/workflows/windows.yml](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/.github/workflows/windows.yml)、[src/pii_guard/enhanced_audit.py](https://github.com/danyuchn/pii-guard/blob/3d55636785868785e6452e5590052571dc459659/src/pii_guard/enhanced_audit.py)
- **既有防線**：screen_privacy 是視窗分類、OCR 文字機密檢查與丟圖決策，pii-guard 是可逆文字遮罩／工具政策，不能取代截圖前後關卡。[比較與固定版本](../docs/pii-guard-readonly-assessment.md)
- **採納條件**：完成雙重靜態審計後，另行授權只用假資料的隔離動態驗證，檢查 Windows ACL、離線／超時、Edit、路徑／transcript、既有 hooks 相容性。此為採納條件，不是本輪 DoD；未新增任務 ID，後續觸發條件統一記於 [ROADMAP](../ROADMAP.md)。

## 4. 拆解待辦事項（Action Items）

- [x] **`T-20261115-17`**｜**[優先級：中]** 唯讀查核 `danyuchn/pii-guard` 並評估 Windows 與現有隱私防線的採納條件
  - **目標範圍**：本筆記與 `docs/pii-guard-readonly-assessment.md`；第三方 repo 只下載與讀檔，不安裝、不執行測試或 hook。
  - **具體做法**：固定 commit／關鍵 blob SHA／授權；追蹤資料流、掛載、權限、落盤、網路、子程序；比較 screen_privacy；逐項判讀 --pack 結果，列已查／未查與採納裁決。
  - **驗收標準（DoD）**：產出 `docs/pii-guard-readonly-assessment.md`，含固定來源、ASCII 資料流、原樣掃描退出碼與每項 REVIEW 判讀、Windows 前提、採納條件與動態驗證停止條件；改正本筆記事實；`python tools/build_index.py`、`python tools/verify_zhtw_vocab.py --check notes docs`、`python tools/verify_inbox.py` 均退出碼 0。動態實測與 SkillSpector 成功審計屬採納條件，不是本輪 DoD。
  - **完成日期**：2026-11-15
  - **實作紀錄 / 證據**：完成（2026-11-15）：docs/pii-guard-readonly-assessment.md，固定 danyuchn/pii-guard 3d55636（MIT，0.2.0），20 個 blob SHA。資料流、hook 權限、寫檔、子程序都盤點過：外連只到 127.0.0.1；Ollama 只驗 loopback，win32 回 LOCAL_MODEL_UNVERIFIED；mapping 以明文寫入。agent-safety-checks --pack 結束碼 1，1 FAIL 經複審重跑確認是正則誤報，6 REVIEW 已逐項判讀。與 screen_privacy 做了比較。裁決暫不採納；動態實測依全域規則第 15 條改列 ROADMAP 採納條件。Codex 撰寫，Fable 獨立複審通過；未執行上游程式。
