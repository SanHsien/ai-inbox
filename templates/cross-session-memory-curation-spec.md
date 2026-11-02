---
id: cross-session-memory-curation-spec
title: 高保真跨 Session 記憶寫入 Prompt 與漸進式清理手冊
version: 1
task: T-20261031-42
spec: docs/claude-code-cross-session-memory-evaluation-guide.md
checker: tools/audit_session_memory_compression.py
verified_on: 2026-11-02
language: zh-TW
---

# 高保真跨 Session 記憶寫入 Prompt 與漸進式清理手冊

> 規範依據：[`docs/claude-code-cross-session-memory-evaluation-guide.md`](../docs/claude-code-cross-session-memory-evaluation-guide.md)（第 2 節壓縮衰減、第 3 節預算與過濾）。對應任務 `T-20261031-42`。
> 用法：複製第 1 節 Prompt 與第 2 節條目格式到你的專案；把 `{大括號}` 換成實際內容。第 4 節的清單腳本與第 6 節的稽核指令都只用 Python 標準函式庫，可單獨複製。
> 本範本裡的「數字」（保留天數、行數、門檻）是**本 repo 的取捨**，沒有外部基準；第 7 節說明怎麼用你自己的紀錄校準。查證過的外部上限（例如 Claude Code 的 `MEMORY.md` 200 行／25KB）只在規範文件裡引用，這裡不重述。

## 0. 流程總覽

```text
 原始 transcript ─► [1 寫入 Prompt] ─► 記憶草稿 ─► [6 稽核 exit 0?] ─► 寫入記憶庫
                                                       │ 1/2 → 退回重寫
 記憶庫 ─► [4 每月清單：過期？] ─► [5 衝突覆蓋] ─► 人核准後才刪除或改狀態
```

---

## 1. 防壓縮失真的寫入 Prompt（四欄強制骨架）

把整段貼給負責寫記憶的模型。它要求「原樣抄寫」與「附出處」，是因為量測工具比對的就是這兩件事（路徑、錯誤代碼、測試結果行、原因句）。

```text
你要把一段工作紀錄寫成一則跨 Session 記憶，給「下一個沒看過這段對話的人」用。
輸入是原始紀錄（下方 <transcript> 區塊）。只准用裡面有的資訊，不准補充、不准推測。

輸出必須是一份 Markdown，開頭是 YAML frontmatter，接著剛好四個二級標題，順序固定：
## 背景事實 / ## 根因分析 / ## 踩坑結論 / ## 待辦事項

規則（逐條遵守）：
1. 路徑、錯誤代碼、指令、測試結果行（例如 "Ran 5 tests"、"FAILED (failures=1)"、"exit code 1"）
   一律「原樣」抄寫，放在背景事實或踩坑結論，不得改寫成概述（不要寫成「測試失敗」「設定檔」）。
2. 根因分析與踩坑結論裡，每個決定都要寫成「因為 {原因}，所以 {做法}」或「改用 {新做法}，因為 {原因}」，
   原因與做法放在同一句。只寫做法不寫原因，視為不合格。
3. 被放棄的方案也要寫：「放棄 {方案}，因為 {原因}」。
4. 每條事實後面用括號附出處：（出處：{transcript 位置、commit 或檔案行號}）。
   紀錄裡找不到出處的資訊，寫成「未驗證：{內容}」，不得當成事實。
5. 待辦事項寫成可勾選清單，每項含「做什麼、在哪個檔案、怎麼知道做完」。沒有就寫「無」。
6. 家目錄路徑一律寫成 ~ 或 %USERPROFILE%；任何金鑰、token、密碼、cookie 一律整句不寫。
7. 不要客套話、不要開場白與結語；一行一個事實。
8. 與先前記憶衝突時，不要自己覆蓋：在待辦事項列出「與 {舊記憶檔名} 衝突：{差異}」，交給第 5 節處理。

frontmatter 欄位照第 2 節格式填：name、description、type、status、created、last_verified、expires。

<transcript>
{貼上原始紀錄，或指定檔案路徑}
</transcript>
```

---

## 2. 記憶條目格式

一則記憶一個檔，檔名 `{type}_{主題}.md`。frontmatter 欄位除 `name`、`description`、`type` 外都是本範本的約定；Claude Code 的 auto memory 只自動補 `modified` 時間戳，不要求其他欄位。

```markdown sample-memory
---
name: config-loader-missing-file
description: 載入設定檔失敗的根因與修法（缺檔時沒有預設值）
type: project
status: active
created: 2026-11-02
last_verified: 2026-11-02
expires: 2027-01-31
supersedes: none
---

## 背景事實
- 設定載入在 src/config/loader.py 失敗，測試檔 tests/test_loader.py，錯誤是 FileNotFoundError，errno 名 ENOENT（出處：transcript 第 3 筆）
- 修前 Ran 5 tests，FAILED (failures=1)；修後 Ran 6 tests，結果 OK（出處：transcript 第 3、5 筆）

## 根因分析
- 因為載入器假設 config/app.toml 一定存在，所以缺檔時直接拋例外而不是退回預設值。

## 踩坑結論
- 改用先檢查檔案是否存在再讀取，因為捕捉 FileNotFoundError 會連真正的權限問題一起吞掉。
- 放棄在測試裡建立假設定檔的做法，因為會讓測試依賴檔案系統狀態。

## 待辦事項
- [ ] 在 src/config/loader.py 補上缺檔時使用預設值的邏輯；完成時 tests/test_loader.py 新增缺檔案例並通過
```

欄位規則：

| 欄位 | 必填 | 說明 |
| :--- | :---: | :--- |
| `name` / `description` / `type` | 是 | `type` 的值是本範本的約定：`user`、`feedback`、`project`、`reference`（官方 auto memory 文件只用 `user_role.md`、`feedback_testing.md` 當主題檔命名範例，並沒有規定 type 清單，見規範第 1.1 節） |
| `status` | 是 | `active`、`unverified`、`superseded`、`expired`。只有 `active` 可以被自動注入 |
| `created` / `last_verified` | 是 | `YYYY-MM-DD`。`last_verified` 是最後一次對照當前程式碼或檔案確認的日子，不是最後編輯日 |
| `expires` | 是 | `YYYY-MM-DD`。依第 3 節預設天數從 `last_verified` 算起 |
| `supersedes` | 是 | 被它取代的檔名；沒有就寫 `none` |

---

## 3. TTL 預設（本 repo 取捨，請依第 7 節校準）

| 條目性質 | 預設有效天數（自 `last_verified`） | 到期處理 |
| :--- | ---: | :--- |
| 進行中的專案狀態、暫時繞過方式 | 30 | 重新驗證；不能驗證就改 `unverified` |
| 踩坑與根因（含環境、版本、路徑） | 90 | 重新驗證；環境已變就改 `superseded` |
| 已定案的架構決策、使用者偏好 | 180 | 重新確認；沒有變就更新 `last_verified` 與 `expires` |
| 外部資源指引（網址、帳號位置） | 90 | 打開確認仍有效 |

規則：到期不等於刪除。到期的條目先改 `status: expired` 並移出自動注入；實際刪除檔案需要人明確核准。

---

## 4. 漸進式清理：找出過期條目

下面這支腳本唯讀，不改也不刪任何檔案。複製存成 `list_expired_memory.py`。

```python list-expired
#!/usr/bin/env python3
"""列出記憶資料夾中已過期、狀態不明或欄位損壞的條目。唯讀。
用法：python list_expired_memory.py <記憶資料夾> [--today YYYY-MM-DD]
結束碼：0 沒有問題；1 有過期或損壞條目；2 資料夾不存在、沒有任何 .md 記憶檔、或參數錯誤。"""
import argparse
import datetime
import pathlib
import re
import sys

for _s in (sys.stdout, sys.stderr):  # Windows 中文主控台不是 UTF-8 時避免輸出崩潰
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

STATUSES = {"active", "unverified", "superseded", "expired"}


def parse_meta(text):
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and re.fullmatch(r"[A-Za-z_]\w*", k.strip()):
            meta[k.strip()] = v.strip()
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--today", default=None)
    args = ap.parse_args()
    try:
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    except ValueError:
        print("錯誤：--today 需為 YYYY-MM-DD", file=sys.stderr)
        return 2
    root = pathlib.Path(args.folder)
    files = sorted(p for p in root.glob("*.md") if p.name != "MEMORY.md") if root.is_dir() else []
    if not files:
        print("錯誤：資料夾不存在或沒有任何記憶檔，無從檢查（這不是通過）", file=sys.stderr)
        return 2
    bad = 0
    for p in files:
        try:
            meta = parse_meta(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            meta = None
        if meta is None:
            print(f"[損壞] {p.name}: 讀不到合法的 frontmatter")
            bad += 1
            continue
        status = meta.get("status", "")
        try:
            expires = datetime.date.fromisoformat(meta.get("expires", ""))
        except ValueError:
            print(f"[損壞] {p.name}: expires 缺少或不是 YYYY-MM-DD")
            bad += 1
            continue
        if status not in STATUSES:
            print(f"[損壞] {p.name}: status 需為 {'/'.join(sorted(STATUSES))}")
            bad += 1
        elif status == "active" and expires < today:
            print(f"[過期] {p.name}: expires {expires} 早於 {today}，狀態仍是 active")
            bad += 1
    print(f"檢查 {len(files)} 個檔，{bad} 個需處理")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
```

每月操作：

1. 跑上面的腳本；exit 1 時逐條處理列出的檔案。
2. 過期的條目：先對照當前程式碼或檔案重新驗證；仍成立就更新 `last_verified` 與 `expires`，不成立就走第 5 節。
3. 把「改狀態」和「刪檔」分成兩次動作，刪檔前向負責人列出清單並取得明確同意。
4. 每次清理後，用第 6 節的稽核指令檢查剛改過的條目，避免清理時又把事實改壞。

---

## 5. 衝突覆蓋（Reconciliation）

兩則記憶對同一件事說法不同時，不要憑直覺選一個。照順序做：

| 步驟 | 做法 | 結果 |
| :---: | :--- | :--- |
| 1 | 找出兩條各自的出處與 `last_verified` | 沒有出處的一方先標 `unverified` |
| 2 | 對照當前程式碼、檔案或實際跑指令，重新驗證 | 驗證結果就是裁決依據，不是「哪條比較新」 |
| 3 | 驗證成立的一方保持 `active`；另一方改 `status: superseded`，並在勝出條目的 `supersedes` 填被取代的檔名 | 舊條目保留，不刪 |
| 4 | 在勝出條目的「踩坑結論」補一句為什麼舊說法錯（因為 …） | 避免之後又有人寫回舊說法 |
| 5 | 兩邊都驗證不了：兩條都改 `unverified`，從自動注入移除，並在待辦事項寫明要驗證什麼 | 不確定的事不進自動注入 |

禁止的做法：只因為日期較新就覆蓋、直接把舊內容改寫成新內容而不留 `supersedes`、為了讓稽核通過而放寬門檻。

---

## 6. 寫入後稽核

量測工具位於 ai-inbox 的 `tools/audit_session_memory_compression.py`，只用標準函式庫；複製到你的專案後照下面指令執行。

```bash
python audit_session_memory_compression.py --transcript {原始紀錄.jsonl} --memory {新記憶.md}
```

| 結束碼 | 意義 | 該做什麼 |
| :---: | :--- | :--- |
| 0 | `[PASS]`：損失率沒超過 `--max-loss`，且沒有機密、真實家目錄路徑、客套話、查無出處的事實 | 可以寫入記憶庫 |
| 1 | `[FAIL]` | 看報告的「發現」與「未保留的事實」，回第 1 節 Prompt 重寫 |
| 2 | 輸入壞了或樣本不足，**量不出來** | 修好輸入再跑；這不是通過 |

transcript 需為 JSONL（每行一個 JSON，UTF-8）。工具的限制（字面比對、`decisions` 要人工抽查、transcript 結構是假設的 Claude Code 本機形狀）寫在它的檔頭與報告的「限制」一節。

下面是一組可以直接跑的自測資料，對應第 2 節的範例記憶，預期 exit 0。自測資料很短，記憶（含 frontmatter 與標題）反而比原文長，所以報告會多一則 `not-compressed` 警告（WARN，不影響結束碼），屬預期；真實紀錄不應該出現。

```jsonl sample-transcript
{"type":"user","message":{"role":"user","content":"載入設定檔時測試失敗，請查原因。"}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"因為載入器假設 config/app.toml 一定存在，所以缺檔時直接拋例外而不是退回預設值。"},{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"python -m unittest tests/test_loader.py"}}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":"FileNotFoundError: src/config/loader.py\nENOENT\nRan 5 tests in 0.2s\nFAILED (failures=1)"}]}}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"改用先檢查檔案是否存在再讀取，因為捕捉 FileNotFoundError 會連真正的權限問題一起吞掉。"},{"type":"text","text":"放棄在測試裡建立假設定檔的做法，因為會讓測試依賴檔案系統狀態。"}]}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":"Ran 6 tests in 0.3s\n\nOK\n"}]}}
```

---

## 7. 校準與誠實揭露

- 第 3 節的天數、第 1 節的規則數、稽核的 `--max-loss` 預設，都是起點。校準方式：挑 5 至 10 個你真實的 session，用同一份 Prompt 寫記憶，跑稽核，看哪一類事實常掉、哪些條目在多久之後變成錯的，再調天數與門檻。
- 稽核通過只代表「可抽取的事實有保留、沒有已知樣式的洩漏」，不代表記憶內容正確或有用；`decisions` 類別要人工抽查。
- 不要為了通過而放寬門檻或刪掉「未保留的事實」清單；要調門檻，先寫下調整理由與依據的樣本。
