# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `20df187a8306` 查的快照，開工前先重查 GitHub。

## 現況

public、非 fork 的個人 AI 情報筆記與跨 Agent 任務總管（`docs/`、`tools/`、`tests/`、`assets/`），維護者持續直推 main 新增筆記與任務。健康：2026-10-30 查到 open issue 0、open PR 0、Dependabot 與 Code scanning 告警各 0，`CI Contract Verification`、`CodeQL` 在 `main` 最近一次皆 success（2026-10-30 `gh` 查詢）；沒有 release。沒有依賴宣告檔，freshness 以 `.github/dependabot.yml:3` 的 `fleet-waiver` 登記為刻意不適用。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
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

自有 repo，直推 `main`，無 release 節奏；改動前跑 `python -m unittest discover -s tests` 與 `python tools/verify_inbox.py`（與 CI 相同）。GitHub Actions 版本由 Dependabot 追蹤；新筆記照 `AGENTS.md` 流程進 `notes/`。
