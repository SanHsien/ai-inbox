# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-11-15 依 `main` 查的快照（第三次），開工前先重查 GitHub。

## 現況

public、非 fork 的個人 AI 情報筆記與跨 Agent 任務總管（`notes/` 120 篇、`tools/` 31 支 CLI 工具、`docs/` 67 份、`templates/` 22 份、`assets/` 7 組、`tests/` 37 支測試檔；任務數與狀態以 README 任務總表為準），維護者持續直推 main 新增筆記與任務。健康：open issue 0、open PR 0、Dependabot 與 Code scanning 告警各 0，`CI Contract Verification`、`CodeQL` 皆 success；沒有 release。`README.md` 的任務總表、文章索引、四大知識圖譜與全庫產出物導覽皆由 `tools/build_index.py` 自動生成並由 `tools/verify_inbox.py` 執行契約與覆蓋率校驗。沒有依賴宣告檔，freshness 以 `.github/dependabot.yml:3` 的 `fleet-waiver` 登記為刻意不適用。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 剩餘 `partial` 筆記 | 找到原始貼文的新線索（作者帳號、轉貼、搜尋引擎收錄），或 K-harness 重新公開 | 2026-11-18 再查轉引與存檔後剩 7 篇 `partial`，原始社群貼文都已搜尋過找不到（試過的方式寫在各篇 `source_review_note`，含 Wayback、archive.ph、ecosyste.ms、X／Threads 站內搜尋），轉引與替代來源都已讀完；Reddit 在本環境查不了，要維護者手動搜；pi-hybrid-harness 的 K-harness 連結 404，只剩 ecosyste.ms 的中繼資料。有新線索時照 SOP 第 3 節讀完改 `full`；`verify_inbox.py` 通過 | Claude（Fable 子 agent） | [重審 SOP](docs/source-review-sop.md) 第 5 節 |
| Windows 常駐 Agent 人工設定與恢復驗收 | 維護者確定要部署，已確認既有排程 owner、登入前提與本機回復管道 | 依規格逐項人工驗收外網、鎖屏、登出、重啟及有界限觀察；分別記結果與限制，不以一次成功稱 24×7 穩定 | 維護者 | [維運規格](docs/windows-24x7-agent-ops-spec.md)、[唯讀證據](docs/evidence/windows-agent-ops-readonly-check.md)；本輪只有文件與工具 |
| 詞彙檢查器：未加引號的專名保護、`支持→支援` 技術受詞白名單 | 實際出現專名被誤改（例如產品名含 `數據庫`），或需要擋 `支持 UTF-8` 這類用詞 | 先寫出誤改實例的回歸測試再改 `tools/verify_zhtw_vocab.py`；`支持` 只在白名單受詞前替換，`支持開源社群` 等反例不變；`--verify-idempotent --check notes docs templates README.md` 通過 | Codex | [評估第 6 節](docs/speak-human-tw-assessment.md)；引號、URL 保護與五條候選規則已於 2026-11-15 完成 |
| pii-guard 隔離動態驗證（採納條件） | 固定版本雙重靜態審計完成、SkillSpector 入口恢復，且另獲隔離實測授權 | 依評估第 8 節，只用一組假資料驗證 Windows ACL、離線／超時、Edit 與載入／既有 hook 相容性；遇停止條件即停，不改全域設定 | 維護者另行指派 | [唯讀評估](docs/pii-guard-readonly-assessment.md)（T-20261115-17，未結案） |
| 重新確認 `av>=14,<17` 固定版本是否還需要 | `faster-whisper` 發布高於 1.2.1 的版本，或維護者在新機器重裝 `video_transcript` 環境 | 在乾淨 venv 以最新 `faster-whisper` 安裝並跑 `tools/video_transcript.py` 一次；依結果更新或刪除 `docs/video-transcript-howto.md:35` 與 `:53` 的 pin，兩處一致 | Claude Sonnet | `docs/video-transcript-howto.md:35`、`:53`；freshness 深掃報告（2026-10-28）「未處理／留意」 |
| 新增依賴宣告檔時改用 dependency-freshness workflow | repo 新增 requirements／pyproject，或 `assets/inbox-band-mod` 補上 package.json | 加上含 `check_dependency_freshness` 的 workflow，並在同一 commit 刪掉 `.github/dependabot.yml:3` 的 `fleet-waiver`；`python -m fleet_ops audit`（repo-fleet-ops）該 repo freshness 欄不再是 `w` | Claude Sonnet | `.github/dependabot.yml:3`；freshness 深掃報告（2026-10-28） |
| 編輯器匯出 JSON 轉驗證器輸入的轉換工具 | 維護者決定要讓 target-story 編輯器與驗證器串成一條流程 | 新工具把 `assets/target-story-editor` 的匯出餵進 `tools/verify_story_structure.py` 且 exit 0（至少一份編輯器匯出檔）、並有一個測試以固定匯出檔釘住輸出；`docs/target-story-generative-ui-spec.md` 第 3 節改寫並有測試對照 | 維護者 | 深掃報告（2026-10-26）缺陷 9 與「刻意不修」 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 把文件類 `verify_*` 擴充成段落限定的關鍵字驗證 | 關鍵字型裁判可被打亂行序繞過，已決定改做能攔真錯誤的檢查 | `docs/external-judge-audit.md` 第 5 節的前提改變 |
| 改工具的 emoji 輸出以相容 cp950 | 只影響本機非 UTF-8 終端，CI 為 UTF-8；本機以 `PYTHONUTF8=1` 即可 | 維護者要在非 UTF-8 終端日常執行這些工具 |
| 為了讓稽核欄位變綠而加沒有保護作用的 workflow | 沒有依賴宣告檔，freshness 以 waiver 登記才是誠實表達 | 出現依賴宣告檔（見中期） |
| 為 `verify_story_structure.py` 的非預期輸入型別加完整錯誤訊息 | 退出碼本來就是 1，只影響訊息 | 有人在自動化流程中依賴其錯誤訊息文字 |

## 維護方式

自有 repo，直推 `main`，無 release 節奏；改動前跑 `python -m unittest discover -s tests` 與 `python tools/verify_inbox.py`（與 CI 相同）。動到 `assets/shader-hero-demo/` 或 `templates/zero-build-hero-injector-skill.md` 時，另外設 `AI_INBOX_BROWSER_TESTS=1` 跑瀏覽器端到端測試（需 Playwright；CI 不跑這部分）。GitHub Actions 版本由 Dependabot 追蹤；新筆記照 `AGENTS.md` 流程進 `notes/`。
