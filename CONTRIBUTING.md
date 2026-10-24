# 貢獻指南 (Contributing Guide)

本專案為維護者**個人專用**之 AI 情報分析庫與任務看板，內容皆源自個人日常閱讀之技術文章與文獻。本倉庫公開旨在作為**開源參考範本**，讓社群開發者能借鏡跨 Agent（Claude Code / Codex / Antigravity / Hermes）協作、5W1H-CQR-KSU 論文拆解與任務追蹤之設計。

因為本庫與個人的工作流與專案緊密綁定，**目前僅限個人與個人的 Agent 寫入維護**；歡迎大家 Fork 打造屬於自己的 AI Inbox 或開 Issue 進行技術討論交流！

## 協作原則

1. **先讀規範**：在新增任何內容前，請務必先閱讀 [`AGENTS.md`](AGENTS.md) 與 [`SECURITY.md`](SECURITY.md)。
2. **單篇單檔**：每篇 AI 文章分析均獨立存放於 `notes/YYYY-MM-DD-<slug>.md`。
3. **任務編號唯一**：衍生任務均依 `T-YYYYMMDD-XX` 統一編碼，只寫在筆記中；`README.md` 總表由 `python tools/build_index.py` 產生。
4. **提交前驗證**：`python -m unittest discover -s tests` 與 `python tools/verify_inbox.py` 都要通過。
5. **驗收閉環**：待辦任務必須可驗證（DoD），完成後必須附上可檢驗之證據，不留空殼。
6. **語意化提交 (Conventional Commits)**：
   - `docs(inbox): add analysis for <slug>`
   - `chore(tasks): mark T-YYYYMMDD-XX as done`
   - `feat(template): update analysis schema`
