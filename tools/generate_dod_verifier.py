#!/usr/bin/env python3
"""
tools/generate_dod_verifier.py
從任務的 DoD（驗收標準）文字或 JSON 規格，產生一支獨立、可執行的驗收腳本 verify_delivery.py。

和既有功能的分工：
- build_index.missing_dod_artifacts / task_cli complete：只檢查「DoD 提到的檔案存在」，檢查在結案那一刻、由內部呼叫。
- 本工具：把 DoD 拆成「可機械檢查」與「必須人工判斷」兩份清單，產生一支可交給第三方（客戶、另一個 Agent）
  單獨執行的腳本；機械檢查除了檔案存在，還有環境變數、HTTP 狀態碼、HTML 元素、允許清單內的單元測試指令。
  無法機械檢查的條件（例如「內含架構原理」「實測數據」）不產生關鍵字檢查，一律列入「人工」清單，不假裝驗過。

安全設計：
- 本工具只「產生」腳本，不執行任何指令。
- 產生的腳本預設只做唯讀檢查；單元測試指令要加 --run-commands 才會執行，而且只執行
  `python -m unittest ...` 這一種、參數通過白名單驗證的指令，以 subprocess 清單式呼叫（不經 shell）。
- DoD 文字只會以 JSON 字串資料嵌進產生的腳本，不會被當成程式碼。

用法：
    python tools/generate_dod_verifier.py --task T-20261026-07 -o verify_delivery.py
    python tools/generate_dod_verifier.py --text "產出 `docs/a.md`，通過 `python -m unittest discover -s tests`" --plan
    python tools/generate_dod_verifier.py --spec spec.json -o verify_delivery.py
    python tools/generate_dod_verifier.py --open-summary
只使用 Python 標準函式庫。
"""

from __future__ import annotations

import argparse
import inspect
import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index as bi  # noqa: E402
import task_cli as tc  # noqa: E402

CHECK_TYPES = ("file_exists", "env", "http", "html_element", "command")
_TOKEN = re.compile(r"^[A-Za-z0-9_./*-]+$")
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_URL = re.compile(r"^https?://[^\s\"'<>]+$")
_FILLER = re.compile(r"產出|與|和|及|以|驗證存在|通過|並|且|，|,|、|\s")


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# 驗證函式：產生器與產生出的腳本共用同一份原始碼（用 inspect.getsource 嵌入），避免兩邊規則漂移
# --------------------------------------------------------------------------


def is_safe_relpath(p: str) -> bool:
    """相對路徑、無 .. 、無磁碟機代號、無絕對路徑。"""
    if not p or p.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", p):
        return False
    parts = re.split(r"[\\/]+", p)
    return ".." not in parts and "\x00" not in p


def validate_unittest_argv(argv: list) -> bool:
    """只接受 python -m unittest [discover] [-s DIR] [-t DIR] [-p PAT] [-v] [dotted.module ...]。"""
    import re as _re

    tok = _re.compile(r"^[A-Za-z0-9_./*-]+$")
    if len(argv) < 3 or argv[0] not in ("python", "python3") or argv[1:3] != ["-m", "unittest"]:
        return False
    rest, i = argv[3:], 0
    while i < len(rest):
        a = rest[i]
        if a in ("-s", "-t", "-p"):
            if i + 1 >= len(rest):
                return False
            v = rest[i + 1]
            if not tok.match(v) or ".." in v.split("/") or v.startswith("/") or _re.match(r"^[A-Za-z]:", v):
                return False
            i += 2
        elif a in ("discover", "-v", "-b", "-f"):
            i += 1
        elif tok.match(a) and not a.startswith("-") and ".." not in a.split("/") and not a.startswith("/"):
            i += 1
        else:
            return False
    return True


def parse_command(text: str) -> list[str] | None:
    """DoD 反引號裡的指令字串 -> 通過白名單的 argv；否則 None。"""
    try:
        argv = shlex.split(text, posix=True)
    except ValueError:
        return None
    return argv if validate_unittest_argv(argv) else None


# --------------------------------------------------------------------------
# DoD 文字 -> 檢查清單
# --------------------------------------------------------------------------

_TEST_PATH = re.compile(r"^Test-Path\s+(\S+)$")


def plan_from_dod(dod: str) -> dict:
    """回傳 {"checks": [...], "manual": [...]}。manual 是沒有任何機械檢查可覆蓋的條件原文。"""
    checks: list[dict] = []
    seen: set[tuple] = set()

    def add(c: dict) -> None:
        key = tuple(sorted((k, json.dumps(v)) for k, v in c.items()))
        if key not in seen:
            seen.add(key)
            checks.append(c)

    manual: list[str] = []
    for m in re.finditer(r"`([^`]+)`", dod):
        span = m.group(1).strip()
        tp = _TEST_PATH.match(span)
        if tp:
            path = tp.group(1)
            if is_safe_relpath(path):
                add({"type": "file_exists", "path": path.replace("\\", "/")})
            else:
                manual.append(f"路徑不安全，未產生檢查：{span}")
        elif span.startswith(("python ", "python3 ")):
            argv = parse_command(span)
            if argv:
                add({"type": "command", "argv": argv})
            else:
                manual.append(f"指令不在允許清單（只允許 python -m unittest ...），請人工執行：{span}")
    for path in bi.DOD_ARTIFACT.findall(dod):
        if is_safe_relpath(path):
            add({"type": "file_exists", "path": path})

    # 每個子句剝掉反引號與連接詞後還有內容，就代表有機械檢查覆蓋不到的條件
    for sentence in re.split(r"[；;。]", dod):
        for clause in re.split(r"[，,]", sentence):
            clause = clause.strip()
            if not clause:
                continue
            leftover = _FILLER.sub("", re.sub(r"`[^`]*`", "", clause))
            if leftover:
                manual.append(clause)
    return {"checks": checks, "manual": manual}


def validate_check(c: dict) -> dict:
    """驗證（並正規化）一個檢查項目，不合法就丟 ValueError。"""
    if not isinstance(c, dict) or c.get("type") not in CHECK_TYPES:
        raise ValueError(f"未知的檢查類型：{c.get('type') if isinstance(c, dict) else c!r}（可用：{', '.join(CHECK_TYPES)}）")
    t = c["type"]
    if t == "file_exists":
        if not is_safe_relpath(str(c.get("path", ""))):
            raise ValueError(f"file_exists 的 path 必須是安全的相對路徑：{c.get('path')!r}")
        return {"type": t, "path": str(c["path"]).replace("\\", "/")}
    if t == "env":
        if not _ENV_NAME.match(str(c.get("name", ""))):
            raise ValueError(f"env 的 name 不合法：{c.get('name')!r}")
        out = {"type": t, "name": c["name"]}
        if "equals" in c:
            out["equals"] = str(c["equals"])
        return out
    if t == "http":
        if not _URL.match(str(c.get("url", ""))):
            raise ValueError(f"http 的 url 必須是 http(s) 網址：{c.get('url')!r}")
        status = c.get("status", 200)
        if not isinstance(status, int) or not 100 <= status <= 599:
            raise ValueError(f"http 的 status 不合法：{status!r}")
        return {"type": t, "url": c["url"], "status": status}
    if t == "html_element":
        if not is_safe_relpath(str(c.get("file", ""))) or not re.match(r"^[A-Za-z][A-Za-z0-9-]*$", str(c.get("tag", ""))):
            raise ValueError("html_element 需要安全的 file 路徑與合法的 tag")
        out = {"type": t, "file": str(c["file"]).replace("\\", "/"), "tag": c["tag"].lower()}
        for k in ("id", "text_contains"):
            if k in c:
                out[k] = str(c[k])
        return out
    argv = c.get("argv")
    if isinstance(argv, str):
        argv = parse_command(argv)
    if not isinstance(argv, list) or not validate_unittest_argv(argv):
        raise ValueError(f"command 只允許 python -m unittest ...：{c.get('argv')!r}")
    return {"type": t, "argv": argv}


def plan_from_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or not isinstance(spec.get("checks"), list):
        raise ValueError('規格必須是 {"title": ..., "checks": [...], "manual": [...]} ')
    manual = [str(x) for x in spec.get("manual", [])]
    return {"title": str(spec.get("title", "")), "checks": [validate_check(c) for c in spec["checks"]], "manual": manual}


# --------------------------------------------------------------------------
# 產生腳本
# --------------------------------------------------------------------------

_TEMPLATE = '''#!/usr/bin/env python3
"""verify_delivery.py -- 由 tools/generate_dod_verifier.py 產生的驗收腳本。

標題：{title_doc}
預設只做唯讀檢查。單元測試指令要加 --run-commands 才會執行（只允許 python -m unittest ...）。
結束碼：0 = 自動檢查全部通過；1 = 有失敗；3 = 加 --strict 且仍有人工項目。
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

{validator_src}

TITLE = json.loads({title_json})
CHECKS = json.loads({checks_json})
MANUAL = json.loads({manual_json})


class _Find(HTMLParser):
    def __init__(self, tag, el_id, text):
        super().__init__()
        self.tag, self.el_id, self.text = tag, el_id, text
        self.depth = 0
        self.buf = []
        self.found = False

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif tag == self.tag and (self.el_id is None or dict(attrs).get("id") == self.el_id):
            self.depth = 1
            self.buf = []

    def handle_data(self, data):
        if self.depth:
            self.buf.append(data)

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            if self.depth == 0 and (self.text is None or self.text in "".join(self.buf)):
                self.found = True


def run_check(c, root, run_commands, network):
    t = c["type"]
    if t == "file_exists":
        p = root / c["path"]
        return ("PASS" if p.exists() else "FAIL"), c["path"]
    if t == "env":
        v = os.environ.get(c["name"])
        if v is None:
            return "FAIL", c["name"] + " 未設定"
        if "equals" in c and v != c["equals"]:
            return "FAIL", c["name"] + " 的值不符"
        return "PASS", c["name"]
    if t == "http":
        if not network:
            return "SKIP", "--no-network：" + c["url"]
        try:
            with urllib.request.urlopen(c["url"], timeout=10) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            return "FAIL", c["url"] + " 連線失敗：" + type(e).__name__
        return ("PASS" if code == c["status"] else "FAIL"), "%s 回應 %s（預期 %s）" % (c["url"], code, c["status"])
    if t == "html_element":
        p = root / c["file"]
        if not p.is_file():
            return "FAIL", c["file"] + " 不存在"
        f = _Find(c["tag"], c.get("id"), c.get("text_contains"))
        f.feed(p.read_text(encoding="utf-8", errors="replace"))
        label = "<%s%s> in %s" % (c["tag"], (" id=" + c["id"]) if "id" in c else "", c["file"])
        return ("PASS" if f.found else "FAIL"), label
    if t == "command":
        argv = list(c["argv"])
        shown = " ".join(argv)
        if not validate_unittest_argv(argv):
            return "FAIL", "指令不在允許清單：" + shown
        if not run_commands:
            return "SKIP", "未加 --run-commands，請手動執行：" + shown
        argv[0] = sys.executable
        proc = subprocess.run(argv, cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace")
        return ("PASS" if proc.returncode == 0 else "FAIL"), shown + " -> exit " + str(proc.returncode)
    return "FAIL", "未知類型 " + t


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="DoD 驗收腳本（自動產生）")
    ap.add_argument("--root", default=".", help="專案根目錄（相對路徑檢查的基準）")
    ap.add_argument("--run-commands", action="store_true", help="執行允許清單內的 python -m unittest 指令")
    ap.add_argument("--no-network", action="store_true", help="略過 HTTP 檢查")
    ap.add_argument("--strict", action="store_true", help="仍有人工項目時結束碼為 3")
    ap.add_argument("--json", action="store_true", help="以 JSON 輸出報告")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    results = []
    for c in CHECKS:
        status, detail = run_check(c, root, args.run_commands, not args.no_network)
        results.append({{"type": c["type"], "status": status, "detail": detail}})
    failed = sum(r["status"] == "FAIL" for r in results)
    skipped = sum(r["status"] == "SKIP" for r in results)
    passed = sum(r["status"] == "PASS" for r in results)
    if args.json:
        print(json.dumps({{"title": TITLE, "results": results, "manual": MANUAL}}, ensure_ascii=False, indent=2))
    else:
        print("== " + (TITLE or "DoD 驗收") + " ==")
        for r in results:
            print("[%s] %s  %s" % (r["status"], r["type"], r["detail"]))
        for m in MANUAL:
            print("[MANUAL] " + m)
        print("自動檢查：通過 %d／失敗 %d／略過 %d；人工項目 %d（腳本未驗證）" % (passed, failed, skipped, len(MANUAL)))
    if failed:
        return 1
    if args.strict and (MANUAL or skipped):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def generate_script(plan: dict, title: str = "") -> str:
    title = title or plan.get("title", "")
    return _TEMPLATE.format(
        title_doc=re.sub(r"[^\w\s一-鿿.,:()-]", "", title)[:80] or "(未命名)",
        validator_src="\n\n".join(inspect.getsource(f) for f in (is_safe_relpath, validate_unittest_argv)),
        title_json=repr(json.dumps(title, ensure_ascii=True)),
        checks_json=repr(json.dumps(plan["checks"], ensure_ascii=True)),
        manual_json=repr(json.dumps(plan["manual"], ensure_ascii=True)),
    )


def _task_plan(task_id: str) -> tuple[dict, str]:
    task = tc.find_task(bi.load_notes(), task_id)
    dod = task.fields.get("驗收標準（DoD）", "")
    if not bi.filled(dod):
        raise ValueError(f"{task_id} 沒有 DoD 文字")
    return plan_from_dod(dod), f"{task.id} {task.title}"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="從任務 DoD 文字或 JSON 規格產生可執行的驗收腳本（只產生，不執行）。")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--task", metavar="ID", help="讀 notes/ 內該任務的 DoD")
    src.add_argument("--text", help="直接給 DoD 文字")
    src.add_argument("--spec", metavar="FILE", help='JSON 規格：{"title","checks":[...],"manual":[...]}')
    src.add_argument("--open-summary", action="store_true", help="列出所有未完成任務各自可產生幾項自動檢查／人工項目")
    ap.add_argument("-o", "--output", help="產生的腳本輸出路徑；省略則印到 stdout")
    ap.add_argument("--plan", action="store_true", help="只印檢查計畫（JSON），不產生腳本")
    return ap


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    args = build_parser().parse_args(argv)
    try:
        if args.open_summary:
            for n in bi.load_notes():
                for t in n.tasks:
                    if t.done or t.archived:
                        continue
                    plan = plan_from_dod(t.fields.get("驗收標準（DoD）", ""))
                    kinds = sorted({c["type"] for c in plan["checks"]})
                    print(f"{t.id}\t自動 {len(plan['checks'])}\t人工 {len(plan['manual'])}\t{','.join(kinds) or '-'}")
            return 0
        if args.task:
            plan, title = _task_plan(args.task)
        elif args.text is not None:
            plan, title = plan_from_dod(args.text), ""
        else:
            plan = plan_from_spec(json.loads(Path(args.spec).read_text(encoding="utf-8")))
            title = plan["title"]
    except (ValueError, KeyError, OSError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 2
    if args.plan:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    script = generate_script(plan, title)
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(script)
        print(f"已產生 {args.output}：自動 {len(plan['checks'])} 項、人工 {len(plan['manual'])} 項")
    else:
        sys.stdout.write(script)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
