# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-11-24 依 `main`（`2ce397d`）查的快照，開工前先重查 GitHub。

## 現況

public、非 fork 的個人 AI 情報筆記與跨 Agent 任務總管（2026-11-24 依 `main` `2ce397d` 快照：`notes/` 168 篇、`tools/` 31 支 CLI 工具、`docs/` 91 份、`templates/` 23 份、`assets/` 7 組、`tests/` 38 支測試檔；任務數與狀態以 README 任務總表為準，現行 265 項任務：未做 9／進行中 0／已做 177／不做 79），維護者持續直推 main 新增筆記與任務。健康：open issue 0、open PR 0、Dependabot 告警 0、Code scanning 告警 0（alert #9 `py/incomplete-url-substring-sanitization` 已於 2026-11-24 標為 fixed，2026-11-27 以 `gh api` 複查 open 數為 0），`CI Contract Verification`、`CodeQL` 皆 success；沒有 release。獨立審查管線（`queue --legacy 0`）目前 `fix` 道 0 件、待獨立審查／覆核 10 篇（11 項審查工作）。`README.md` 的任務總表、文章索引、四大知識圖譜與全庫產出物導覽皆由 `tools/build_index.py` 自動生成並由 `tools/verify_inbox.py` 執行契約與覆蓋率校驗。沒有依賴宣告檔，freshness 以 `.github/dependabot.yml:3` 的 `fleet-waiver` 登記為刻意不適用。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 舊筆記逐步補審 | 審查制度上線時既有筆記以內容雜湊凍結免審，但其中仍有沒被第二人看過的；Codex 額度常有剩 | 每天排程 `python tools/review_pipeline.py cron --lane codex --legacy 2` 補審最新的免審筆記；`python tools/review_pipeline.py queue --legacy 200` 不再列出 codex 道的 review 工作（若有退回由整合者改完再審） | Codex | [規劃](docs/review-pipeline-plan.md) 2.3 節 |
| 完成待審筆記之獨立審查與強模型覆核（Codex 道） | 2026-11-21 起新增與修正的筆記尚有未完成獨立審查或觸發強模型覆核者，逾期 7 天 `verify_inbox.py` 會失敗，且其任務無法認領／結案 | 執行 `python tools/review_pipeline.py run --lane codex --commit` 完成 `codex` 道所有非 legacy 的 `review` 與 `audit` 項目；`python tools/review_pipeline.py queue --lane codex --legacy 0` 為空 | Codex | [規劃](docs/review-pipeline-plan.md) 2.4～2.5 節、`tools/review_pipeline.py` |
| 完成待審筆記之來源補審與強模型覆核（Chrome 道） | 需登入或瀏覽器開啟原始來源的筆記（含社群貼文與觸發強模型 `audit` 的條目）無法由無頭環境完成，逾期 7 天 `verify_inbox.py` 會失敗 | 依 [AGENTS.md](AGENTS.md) 流程 C 第 2 步以 Chrome 工作階段完成 `chrome` 道非 legacy 的 `review` 與 `audit` 項目並入帳；`python tools/review_pipeline.py queue --lane chrome --legacy 0` 為空 | Claude Opus | [AGENTS.md](AGENTS.md) 流程 C 第 2 步、[規劃](docs/review-pipeline-plan.md) 2.4～2.5 節 |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 剩餘 `partial` 筆記 | 找到原始貼文的新線索（作者帳號、轉貼、搜尋引擎收錄）、K-harness 重新公開、文首題圖恢復截取，或補齊影片畫面截圖與需登入之社群回覆 | 現存 `source_review: partial` 筆記涵蓋來源查無／404、題圖未讀與媒體／留言待補等情形；補讀完整來源或取得新線索後依 SOP 第 3 節改為 `full` 並送審，`verify_inbox.py` 通過（現行清單以 `rg -n "source_review: partial" notes/` 為準）。2026-11-25 的 Polycam／Home Assistant 筆記已依登入後報告補齊 2 則留言、改為 `full`，不再列入補讀範圍；修正後再審仍由近期審查項目追蹤 | Claude Opus | [重審 SOP](docs/source-review-sop.md) 第 5 節、[本輪修正](REVIEW.md#18-三篇筆記-fix-道修正2026-11-25) |
| Windows 常駐 Agent 人工設定與恢復驗收 | 維護者確定要部署，已確認既有排程 owner、登入前提與本機回復管道 | 基準階段的唯讀摘要、睡眠原值與 unknown 項釐清已於 2026-11-19 做完（工具原本讀不到睡眠值的錯已修）。剩下都要維護者在場：基準的 owner 核對、保存工作、本機回復方式；外網、鎖屏、登出、重啟、有界限觀察另需第二台裝置。分別記結果與限制，不以一次成功稱 24×7 穩定 | 維護者 | [維運規格](docs/windows-24x7-agent-ops-spec.md)的人工驗收表、[唯讀證據](docs/evidence/windows-agent-ops-readonly-check.md) 2026-11-19 一節 |
| pii-guard 隔離動態驗證（採納條件） | 固定版本雙重靜態審計完成、SkillSpector 入口恢復，且另獲隔離實測授權 | 依評估第 8 節，只用一組假資料驗證 Windows ACL、離線／超時、Edit 與載入／既有 hook 相容性；遇停止條件即停，不改全域設定 | 維護者 | [唯讀評估](docs/pii-guard-readonly-assessment.md)（T-20261115-17，未結案） |
| 重新確認 `av>=14,<17` 固定版本是否還需要 | `faster-whisper` 發布高於 1.2.1 的版本（2026-11-27 PyPI 最新仍為 1.2.1） | 2026-11-27 已在乾淨 venv 以 `av` 19.0.2 實跑 `tools/video_transcript.py`：exit 0，執行期 patch 有效；未 patch 的 `decode_audio()` 仍報 `metadata_errors` 錯，故 pin 保留給直接使用 `faster-whisper` 的情境，說明已更新於 `docs/video-transcript-howto.md`。新版 `faster-whisper` 發布後，在乾淨 venv 不經 patch 直接呼叫 `decode_audio()`，通過就刪 pin 與 patch | Claude Sonnet | `2ce397d`、`docs/video-transcript-howto.md` 陷阱表；freshness 深掃報告（2026-10-28）「未處理／留意」 |
| 新增依賴宣告檔時改用 dependency-freshness workflow | repo 新增 requirements／pyproject，或 `assets/inbox-band-mod` 補上 package.json | 加上含 `check_dependency_freshness` 的 workflow，並在同一 commit 刪掉 `.github/dependabot.yml:3` 的 `fleet-waiver`；`python -m fleet_ops audit`（repo-fleet-ops）該 repo freshness 欄不再是 `w` | Claude Sonnet | `.github/dependabot.yml:3`；freshness 深掃報告（2026-10-28） |
| 編輯器匯出 JSON 轉驗證器輸入的轉換工具 | 維護者決定要讓 target-story 編輯器與驗證器串成一條流程 | 新工具把 `assets/target-story-editor` 的匯出餵進 `tools/verify_story_structure.py` 且 exit 0（至少一份編輯器匯出檔）、並有一個測試以固定匯出檔釘住輸出；`docs/target-story-generative-ui-spec.md` 第 3 節改寫並有測試對照 | 維護者 | 深掃報告（2026-10-26）缺陷 9 與「刻意不修」 |
| `main` 開分支保護（禁止 force-push） | 維護者決定要開（屬 GitHub 安全設定） | 目前 force-push 會讓 CI 的審查紀錄只追加檢查報錯而不是放行；開了之後這類竄改在推送時就被拒。`gh api repos/SanHsien/ai-inbox/branches/main/protection` 不再回 404 | 維護者 | [REVIEW.md](REVIEW.md) 第 17 節、[規劃](docs/review-pipeline-plan.md) 第 4 節 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 審查紀錄加簽章（SSH／GPG） | 能推 main 的 agent 都拿得到本機金鑰，簽章擋不了它們，只多一層維護；現行做法是報告檔、內容雜湊與 git 歷史留痕 | 審查改由本機以外、金鑰不共用的服務執行 |
| 把文件類 `verify_*` 擴充成段落限定的關鍵字驗證 | 關鍵字型裁判可被打亂行序繞過，已決定改做能攔真錯誤的檢查 | `docs/external-judge-audit.md` 第 5 節的前提改變 |
| 改工具的 emoji 輸出以相容 cp950 | 只影響本機非 UTF-8 終端，CI 為 UTF-8；本機以 `PYTHONUTF8=1` 即可 | 維護者要在非 UTF-8 終端日常執行這些工具 |
| 為了讓稽核欄位變綠而加沒有保護作用的 workflow | 沒有依賴宣告檔，freshness 以 waiver 登記才是誠實表達 | 出現依賴宣告檔（見中期） |
| 為 `verify_story_structure.py` 的非預期輸入型別加完整錯誤訊息 | 退出碼本來就是 1，只影響訊息 | 有人在自動化流程中依賴其錯誤訊息文字 |

## 維護方式

自有 repo，直推 `main`，無 release 節奏；改動前跑 `python -m unittest discover -s tests` 與 `python tools/verify_inbox.py`（與 CI 相同）。動到 `assets/shader-hero-demo/` 或 `templates/zero-build-hero-injector-skill.md` 時，另外設 `AI_INBOX_BROWSER_TESTS=1` 跑瀏覽器端到端測試（需 Playwright；CI 不跑這部分）。GitHub Actions 版本由 Dependabot 追蹤；新筆記照 `AGENTS.md` 流程進 `notes/`。
