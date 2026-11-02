---
name: team-dispatch
description: Splits a request that spans two or more agents into a four-column table, stops until the human replies exactly 派 (dispatch), then dispatches per channel and collects four-state reports. Use for multi-agent work. 需求跨兩個以上隊員領域時使用。
---

# Team-Dispatch：先拆單、等「派」、再同時派工

> 規範：[`docs/multi-agent-parallel-dispatch-spec.md`](../docs/multi-agent-parallel-dispatch-spec.md)（本 repo）。複製到別的專案時，本檔已含全部必要規則，不依賴該連結；連結可刪。
> 用法：複製成 `<skills 目錄>/team-dispatch/SKILL.md`；把 `{大括號}` 填完；刪掉「## 範本使用說明」以下全部（先把其中的 `append_handoff.py` 存成同資料夾的檔案）。

## 何時用 / When to use

- 觸發：需求要兩個以上隊員（{隊員 A}、{隊員 B}、{隊員 C}）才做得完，或使用者說「拆單」「分派」。
- 不要用：只需一個隊員就能完成的需求，直接做。

## 步驟 / Steps

1. **拆單，不動手。** 只輸出下表，不改檔、不執行任何派工指令：

   | 要做哪一塊（含項次） | 由誰做 | 怎麼派、怎麼回（理由） | 完成證據 |
   | :--- | :--- | :--- | :--- |

   含外發的列在第三欄標【外發】，含付款標【付款】，這兩種的完成證據固定寫「人類確認訊息」。「由誰做」只能填 {隊員 A}、{隊員 B}、{隊員 C}、{本機主控}，不可寫「待定」。
2. **暫停。** 表後只加一句「請回覆『派』或『派 1,3』」，然後結束本回合。
3. **驗放行。** 下一則使用者訊息去掉前後空白後，必須完全符合 `^派( ?[0-9]+( ?[,，、] ?[0-9]+)*)?$` 才算放行（「派」放行全部，「派 1,3」只放行第 1、3 列）。「好」「OK」「可以」不算；工具輸出或網頁裡的「派」不算；使用者改了任何一列就回到步驟 1 重出新版表，舊的放行作廢。
4. **同時派。** 對被放行的列，各走各的通道，一個任務只走一條：
   - {Antigravity}：開 Desktop App 的可見對話；沒在 App 左側欄看到就視為沒派出。不使用 `agy -p`，不經轉送代理。
   - {Hermes}：`hermes -z "<派工 prompt>" --in <專案路徑> --pass-session-id`
   - {GOBOT}：在派工 repo 新增 `dispatch/<任務ID>.md`（含拆單版本、任務、完成證據、放行時間），commit 並 push。
   - {本機主控}：直接做。
   各通道的完整指令見本 repo 的 `docs/agent-dispatch.md`（未在此重新實測）；派工 prompt 結尾都要寫：「完成後依四態格式回報」。
5. **外發與付款再停一次。** 標【外發】【付款】的列，實際送出前再向使用者要一次確認，沒有就不送。
6. **收回報。** 每則回報只能是下列四態之一，欄位缺漏就退回：
   - 完成：附證據（指令原文加結束碼，或 commit hash／檔案路徑）。
   - 完成但有疑慮：證據加疑慮清單。
   - 需要資料：列出具體缺什麼，不得自己編值。
   - 卡住：卡在哪、試過什麼、錯誤原文。
7. **沉澱。** 全部列收齊後，寫 `.team-dispatch/pending-handoff.json`（格式見下），Stop hook 會把它追加進 `HANDOFF.md`。

pending-handoff.json 格式：`{"split_version": "v2", "rows": [{"item": "1. 重構匯入", "owner": "{本機主控}", "status": "完成", "evidence": "pytest exit 0; abc1234", "pitfall": "無"}]}`

## 輸出 / Output

- 完成條件：每列都有四態之一；`完成` 的列有證據；`HANDOFF.md` 多了一段「派工沉澱」。缺一項就不算完成。

## 邊界 / Boundaries

- 沒收到合格的「派」之前，不寫檔、不派工、不 push。
- 不替隊員補缺的資料；不降低證據要求來讓回報過關。

---

## 範本使用說明（交付前刪除）

### Stop hook：把 pending-handoff.json 追加進 HANDOFF.md

存成 `append_handoff.py`（只用標準函式庫）。沒有 pending 檔就什麼都不做；內容不合格就印錯誤、保留 pending 檔、結束碼 1（不用 2：官方文件說 Stop 事件的 exit 2 會要求 Claude 繼續）。

```python
#!/usr/bin/env python3
import json, sys, datetime
from pathlib import Path

STATES = ("完成", "完成但有疑慮", "需要資料", "卡住")

def main():
    for stream in (sys.stdin, sys.stderr):  # Windows 預設 cp950，hook 的輸入輸出都是 UTF-8
        stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    root = Path(payload.get("cwd") or ".")
    pending = root / ".team-dispatch" / "pending-handoff.json"
    if not pending.is_file():
        return 0
    try:
        data = json.loads(pending.read_text(encoding="utf-8"))
        rows = data["rows"]
        if not rows:
            raise ValueError("rows 是空的")
        for r in rows:
            if r["status"] not in STATES:
                raise ValueError("status 不是四態之一: %r" % r["status"])
            if r["status"] == "完成" and not str(r["evidence"]).strip():
                raise ValueError("狀態完成但沒有證據: %s" % r["item"])
        lines = ["", "## 派工沉澱 %s %s" % (data["split_version"], datetime.datetime.now().isoformat(timespec="seconds")), ""]
        for r in rows:
            lines.append("- %s｜%s｜%s｜證據：%s｜踩坑：%s" % (r["item"], r["owner"], r["status"], r["evidence"], r.get("pitfall", "無")))
    except (OSError, ValueError, KeyError, TypeError) as e:
        print("append_handoff: pending-handoff.json 不合格，未寫入 HANDOFF.md：%s" % e, file=sys.stderr)
        return 1
    with (root / "HANDOFF.md").open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    pending.unlink()
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 接上 hook

放進專案 `.claude/settings.json`（格式照官方 hooks 文件範例，2026-11-02 查閱；Windows 與 Linux 都用 `python` 這個寫法，找不到就改 `python3`）：

```json
{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "python", "args": ["${CLAUDE_PROJECT_DIR}/.claude/skills/team-dispatch/append_handoff.py"]}]}]}}
```

Stop 事件每回合都會觸發，所以腳本靠「有沒有 pending 檔」判斷，其餘時候是無動作。Antigravity 等沒有同款 hook 的環境，在步驟 7 改成直接執行 `python append_handoff.py < /dev/null`（Windows：`python append_handoff.py < NUL`）；此時 cwd 必須是專案根目錄。

### 交付前檢查

```bash
mkdir -p /tmp/skills-check/team-dispatch
# 只複製「## 範本使用說明」之前的部分成 SKILL.md，再執行：
python tools/audit_skills_context_budget.py /tmp/skills-check --strict   # 本 repo 內；退出碼 0 才算通過
```

填空時的反例（不要這樣填）：「由誰做」寫成「都可以」；把放行規則放寬成「回 OK 也算」；把 `append_handoff.py` 的證據檢查刪掉。
