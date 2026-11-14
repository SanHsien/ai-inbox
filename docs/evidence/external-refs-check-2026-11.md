# T-20261108-06：2026-11 外部連結巡檢證據

巡檢日期：2026-11-14。這是人工查詢快照；不代表後續狀態。

## 工具與範圍

一手實作來源：[工具原始碼](../../tools/check_external_refs.py)、[離線回歸測試](../../tests/test_check_external_refs.py)。
掃描 `notes/*.md`，略過反引號／波浪號圍欄；同列標「（私有）」的 GitHub repo 略過。
GitHub 只查 repo 層級，不驗證檔案、分支、Issue 或頁內錨點；arXiv PDF 正規化至摘要 URL。

```text
notes/*.md -> 去重 -> gh api / urllib HEAD 或 GET -> 狀態與警告
```

不安裝套件，不接 CI。預設使用已安裝的 `gh api repos/<owner>/<repo>`；沒有 gh 時使用 urllib，GitHub 可用 `GITHUB_TOKEN`。
`--transport urllib` 是安裝了 gh 但無法使用時的明確備援，不自動對失敗重試或切換查詢方式。
`--offline` 只列清單，輸出 NOT CHECKED；`--cache <檔>` 只儲存成功查詢的快照，無到期機制，重查前須刪除。
快取無採樣時間，故不能當作即時查證；錯誤 schema 不接受。網路逾時、403、429 等一律是無法查證。

| 結束碼 | 意義 |
| --- | --- |
| 0 | 線上無錯誤；改名／封存／重新導向僅警告。離線 0 僅表示列出清單成功。 |
| 1 | 404 或其他無法查證狀態、查詢失敗、回應 schema 無效。 |
| 2 | 不存在／非目錄 notes、沒有支援連結、壞快取、讀寫或命令列參數錯誤。 |

## 實跑結果

最終結果（2026-11-14，整合者在可用 gh 的環境重跑，取代先前 Codex 沙盒中 gh 無法使用、58 個連結回 403 的那一輪）：

`python tools/check_external_refs.py --notes notes --cache <暫存檔>` → exit 1；`SUMMARY total=93 errors=2 warnings=2 online`，91 個 OK（含 3 個 arXiv）。

重跑時抓到工具本身的 bug：`gh api` 的輸出以系統編碼（cp950）解碼，遇到含非 ASCII 的 repo 描述時 stdout 變成 None 而崩潰。已改為 `encoding='utf-8'`，並加回歸測試 `test_gh_output_decoded_as_utf8_not_locale`（拿掉修正時該測試變紅）。

逐條處理：

| 結果 | 連結 | 處理 |
| --- | --- | --- |
| ERROR 404 | https://github.com/sanhsien/glm-5（`notes/2026-10-21-0x-alpha-glm-5-3-flash-1m-context.md:80`） | 刻意引用：筆記原文寫明「HTTP 404，確認目前尚未 Fork」，404 正是筆記要記錄的事實，不改。 |
| ERROR 404 | https://github.com/sanhsien/strata（`notes/2026-10-21-strata-consumer-gpu-large-llm-inference.md:79`） | 同上，筆記寫明「回應 404，確認尚未 Fork」，不改。 |
| WARNING 改名 | https://github.com/all-hands-ai/openhands → OpenHands/OpenHands | GitHub 會自動轉址，連結仍可用；不改筆記原文。 |
| WARNING 封存 | https://github.com/opencut-app/opencut-classic | 上游已封存，屬事實狀態；不改。 |

結論：沒有發現捏造或失效的外部連結；兩個 404 是筆記刻意記錄的「尚未 Fork」狀態。
